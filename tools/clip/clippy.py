import asyncio
import hashlib
import json
import logging
import os
import re
import shutil
import sys
import html
from collections import deque
from logging.handlers import RotatingFileHandler

import discord
from discord import app_commands
from discord.ext import commands

from openpilot.tools.lib.api import CommaApi, UnauthorizedError
from openpilot.tools.lib.route import Route

import threading
from flask import Flask, send_file, abort, make_response
from pathlib import Path

if not (CLIPPY_TOKEN := os.getenv("CLIPPY_TOKEN")):
  sys.exit("❌ CLIPPY_TOKEN is missing – set it in the environment")

ALLOWED_GUILD_IDS = {880416502577266699, 1368811404689276958}

CLIPPY_BASE_URL = "https://clippy.royjr.com"

WORKING_DIR = os.path.expanduser("~/github/sunnypilot/tools/clip")
CLIPS_DIR = os.path.join(WORKING_DIR, "clips")
STATS_PATH = os.path.join(WORKING_DIR, "clippy_stats.json")
LOG_PATH = os.path.join(WORKING_DIR, "clippy.log")
os.makedirs(CLIPS_DIR, exist_ok=True)

MAX_TOTAL_JOBS         = 20
MAX_CONCURRENT_CLIPS       = 3
MAX_CONCURRENT_CLIPS_PER_USER  = 3
MAX_CLIP_DURATION        = 60 * 5

CLIPPY_STATS_ALLOWED_ROLES    = ["sunnypilot-dev"]
CLIPPY_UNLIMITED_ALLOWED_ROLES  = ["sunnypilot-dev"]

TAIL_LINES = 25
tail_buffer = deque(maxlen=TAIL_LINES)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=lambda bot, msg: [], intents=intents)

clip_queue    = []
clip_semaphore  = asyncio.Semaphore(MAX_CONCURRENT_CLIPS)
user_cooldowns  = {}


async def queue_monitor():
  while True:
    print("\033c", end="")
    w = shutil.get_terminal_size().columns
    bar = "-" * w
    print(f"{bar}\nTotal: {stats['total']} | ✅ {stats['success']} | ❌ {stats['fail']}\n{bar}")
    print("\n".join(f"{i+1:02d}. {j['status']} {j['user']}: {j['route']}" for i, j in enumerate(clip_queue)) or "No jobs in queue.")
    print(f"{bar}\n" + "\n".join(line[:w] for line in tail_buffer) + f"\n{bar}")
    await asyncio.sleep(1)

def start_clip_server():
  clip_dir_resolved = Path(CLIPS_DIR).resolve()
  app = Flask("clippy")

  @app.route('/<path:filename>')
  def get_clip(filename):
    full_path = (clip_dir_resolved / filename).resolve()
    try:
      full_path.relative_to(clip_dir_resolved)
    except ValueError:
      abort(404)
    if not full_path.name.endswith(".mp4"):
      abort(404)
    try:
      if not full_path.is_file() or not full_path.samefile(full_path):
        abort(404)
    except Exception:
      abort(404)
    response = make_response(send_file(
      str(full_path),
      mimetype="video/mp4",
      as_attachment=False,
      conditional=True,
    ))
    response.headers.update({
      "Cache-Control": "no-store",
      "Accept-Ranges": "bytes",
      "Content-Disposition": f'inline; filename="{filename}"',
      "X-Content-Type-Options": "nosniff",
    })
    return response

  @app.errorhandler(404)
  def not_found(_):
    return "clip not found", 404

  app.run(host="127.0.0.1", port=5000)

def has_any_role(user, role_list):
  if isinstance(user, discord.Member):
    return any(role.name in role_list for role in user.roles)
  return False

def user_tag(user: discord.User) -> str:
  return f"{user.display_name} ({user.name})"

def load_stats():
  if os.path.exists(STATS_PATH):
    with open(STATS_PATH, "r") as f:
      return json.load(f)
  return {"total": 0, "success": 0, "fail": 0}

def save_stats():
  with open(STATS_PATH, "w") as f:
    json.dump(stats, f)

stats = load_stats()


class SanitizeFilter(logging.Filter):
  def filter(self, record: logging.LogRecord) -> bool:
    if isinstance(record.msg, str):
      record.msg = re.compile(r'[\x00-\x1f\x7f-\x9f]').sub('', record.msg)
    return True


class DequeHandler(logging.Handler):
  def __init__(self, buf):
    super().__init__()
    self.buf = buf
    self.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))

  def emit(self, record):
    try:
      self.buf.append(self.format(record))
    except Exception:
      self.handleError(record)

log_handler = RotatingFileHandler(LOG_PATH, maxBytes=5*1024*1024, backupCount=3)
log_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))

root = logging.getLogger()
root.setLevel(logging.INFO)
root.addHandler(log_handler)
root.addHandler(DequeHandler(tail_buffer))
root.addFilter(SanitizeFilter())


class DeletePublishedView(discord.ui.View):
  def __init__(self, message: discord.Message, author_id: int, video_path):
    super().__init__(timeout=300)
    self.message = message
    self.author_id = author_id
    self.video_path = video_path

  @discord.ui.button(label="Unpublish Clip", style=discord.ButtonStyle.primary)
  async def unpublish(self, interaction: discord.Interaction, _button: discord.ui.Button):
    if interaction.user.id != self.author_id:
      logging.error(f"🚫 {user_tag(interaction.user)} cant unpublish {self.message.id}")
      await interaction.response.send_message("🚫 You can't unpublish this clip.", ephemeral=True)
      return

    try:
      await self.message.delete()
      logging.info(f"🗑️ {user_tag(interaction.user)} unpublished {self.message.id}")
      await interaction.response.edit_message(content="🗑️ Unpublished clip.", view=None)
    except Exception as e:
      logging.error(f"❌ Failed to unpublish clip {self.message.id}: {e}")
      await interaction.response.send_message(f"❌ Failed to unpublish clip.", ephemeral=True)

  @discord.ui.button(label="Unpublish + Delete Clip", style=discord.ButtonStyle.danger)
  async def delete(self, interaction: discord.Interaction, _button: discord.ui.Button):
    if interaction.user.id != self.author_id:
      logging.error(f"🚫 {user_tag(interaction.user)} cant unpublish and delete {self.message.id}")
      await interaction.response.send_message("🚫 You can't unpublish and delete this clip.", ephemeral=True)
      return

    try:
      if not os.path.realpath(self.video_path).startswith(os.path.realpath(CLIPS_DIR) + os.sep):
        logging.error(f"❌ Unsafe delete attempt: {self.video_path}")
        await interaction.response.send_message("❌ Unsafe delete attempt.", ephemeral=True)
        return
      os.remove(self.video_path)
      await self.message.delete()
      logging.info(f"🗑️ {user_tag(interaction.user)} unpublished {self.message.id}")
      await interaction.response.edit_message(content="🗑️ Unpublished and deleted clip.", view=None)
    except Exception as e:
      logging.error(f"❌ Failed to unpublish clip {self.message.id}: {e}")
      await interaction.response.send_message(f"❌ Failed to unpublish and delete clip.", ephemeral=True)


class PublishView(discord.ui.View):
  def __init__(self, route_str, title, video_path, author_id, file_size, safe_name):
    super().__init__(timeout=300)
    self.route_str = route_str
    self.title = title
    self.video_path = video_path
    self.author_id = author_id
    self.file_size = file_size
    self.safe_name = safe_name

  @discord.ui.button(label="Publish Clip", style=discord.ButtonStyle.success)
  async def publish(self, interaction: discord.Interaction, _button: discord.ui.Button):
    if interaction.user.id != self.author_id:
      await interaction.response.send_message("🚫 You can't publish this clip.", ephemeral=True)
      return

    if not os.path.exists(self.video_path):
      logging.error(f"❌ {user_tag(interaction.user)} failed to publish {self.route_str} – file missing")
      await interaction.response.edit_message(
        content="❌ Clip could not be published. File missing.",
        attachments=[], view=None
      )
      self.stop()
      return

    logging.info(f"✅ {user_tag(interaction.user)} published {self.route_str}")

    if not (1 <= self.file_size <= 9):
      published_msg = await interaction.channel.send(
        f"{interaction.user.mention} shared a [clip]({CLIPPY_BASE_URL}/{self.safe_name}.mp4) from [{self.route_str}](https://connect.comma.ai/{self.route_str})\n{self.title}"
      )
    else:
      published_msg = await interaction.channel.send(
        f"{interaction.user.mention} shared a clip from [{self.route_str}](https://connect.comma.ai/{self.route_str})\n{self.title}",
        file=discord.File(self.video_path)
      )
    await interaction.response.edit_message(
      content="✅ Clip published to channel.", attachments=[], view=DeletePublishedView(published_msg, interaction.user.id, self.video_path),
    )
    self.stop()

  @discord.ui.button(label="Delete Clip", style=discord.ButtonStyle.danger)
  async def delete(self, interaction: discord.Interaction, _button: discord.ui.Button):
    if interaction.user.id != self.author_id:
      logging.error(f"🚫 {user_tag(interaction.user)} cant delete {self.video_path}")
      await interaction.response.send_message("🚫 You can't delete this clip.", ephemeral=True)
      return

    try:
      if not os.path.realpath(self.video_path).startswith(os.path.realpath(CLIPS_DIR) + os.sep):
        logging.error(f"❌ Unsafe delete attempt: {self.video_path}")
        await interaction.response.send_message("❌ Unsafe delete attempt.", ephemeral=True)
        return
      os.remove(self.video_path)
      logging.info(f"🗑️ {user_tag(interaction.user)} deleted {self.route_str}")
      await interaction.response.edit_message(content="🗑️ Clip deleted.", attachments=[], view=None)
      self.stop()
    except Exception as e:
      logging.error(f"❌ Failed to delete {self.route_str}")
      await interaction.response.edit_message(content=f"❌ Failed to delete clip.", view=None)


@bot.tree.command(name="clippy", description="Generate a driving clip - make sure you upload logs first!")
@app_commands.describe(
  input="connect link or dongle/route/starttime/endtime or dongle/route/startsegment-endsegment",
  title="Title (default: none)",
  quality="Video quality (default: high)",
  wide="Use wide view if uploaded (default: true)",
  speed="Playback speed (default: 1)",
  cache="Set to false to regenerate clip if its already cached (default: true)",
  private="If true, only you will see the preview (default: true)",
  bookmarks="Automatically clip bookmarks (default: false)",
  filesize="Max filesize (MB), set to 0 for unlimited (default: 9)",
  developer="Show the developer UI (default: Off)"
)
@app_commands.choices(
  quality=[
    app_commands.Choice(name="high", value="high"),
    app_commands.Choice(name="low",  value="low"),
  ],
  developer=[
    app_commands.Choice(name="Right",  value="1"),
    app_commands.Choice(name="Right & Bottom",  value="2"),
  ]
)
async def clippy(
  interaction: discord.Interaction,
  input: str,
  title: str = None,
  quality: app_commands.Choice[str] | None = None,
  wide: bool = True,
  speed: int = 1,
  cache: bool = True,
  private: bool = True,
  bookmarks: bool = False,
  filesize: int = 9,
  developer: app_commands.Choice[str] | None = None,
):

  if interaction.guild_id not in ALLOWED_GUILD_IDS:
    logging.error(f"❌ This bot is not available in this server {interaction.guild_id}")
    await interaction.response.send_message("❌ This bot is not available in this server.", ephemeral=True)
    return

  if len(clip_queue) >= MAX_TOTAL_JOBS:
    await interaction.response.send_message(
      "🚫 Server busy – too many jobs in queue. Please try again later.",
      ephemeral=True
    )
    return

  user_id = interaction.user.id
  if not has_any_role(interaction.user, CLIPPY_UNLIMITED_ALLOWED_ROLES):
    if user_cooldowns.get(user_id, 0) >= MAX_CONCURRENT_CLIPS_PER_USER:
      logging.error(f"🚫 {user_tag(interaction.user)} hit the cooldown limit")
      await interaction.response.send_message(
        "🚫 You already have a clip running. Wait for it to finish.",
        ephemeral=True
      )
      return

  user_cooldowns[user_id] = user_cooldowns.get(user_id, 0) + 1

  try:
    await interaction.response.defer(ephemeral=True)

    quality_value = quality.value if quality else "high"
    title_cmd = title[:80] if title else ""
    title = f"> ### **{html.unescape(title[:80])}**" if title else ""
    stats["total"] += 1

    # ── fast‑fail validation ────────────────────────────────────────────────────
    def fail(msg: str):
      stats["fail"] += 1
      save_stats()
      return interaction.followup.send(f"❌ {msg}", ephemeral=True)

    input = input.removeprefix("https://connect.comma.ai/")

    if bookmarks:
      match = re.match(r'^([a-z0-9]+)/([a-zA-Z0-9\-]+)$', input)
      if not match:
        logging.error(f"❌ {user_tag(interaction.user)} entered bad input {input}")
        await fail("Use connect link, `dongle/route/starttime/endtime` or `dongle/route/startsegment-endsegment` (endsegment optional).\n```\n--- CONNECT ---\nhttps://connect.comma.ai/a2a0ccea32023010/2023-07-27--13-01-19/5/10\n\n--- EXAMPLES ---\na2a0ccea32023010/2023-07-27--13-01-19/0     segment 0\na2a0ccea32023010/2023-07-27--13-01-19/0-1   segments 0 through 1\na2a0ccea32023010/2023-07-27--13-01-19/5/10  from 5 to 10 seconds\na2a0ccea32023010/2023-07-27--13-01-19       when using bookmark option\n```")
        return
      else:
        dongle, route = match.groups()
        start = 0
        end = 0
    else:

      match = re.match(r'^([a-z0-9]+)/([a-zA-Z0-9\-]+)/(\d+)/(\d+)$', input)
      if not match:
        match = re.match(r"^([a-z0-9]+)/([A-Za-z0-9\-]+)/(\d+)(?:-(\d+))?$", input)
        if not match:
          logging.error(f"❌ {user_tag(interaction.user)} entered bad input {input}")
          await fail("Use connect link, `dongle/route/starttime/endtime` or `dongle/route/startsegment-endsegment` (endsegment optional).\n```\n--- CONNECT ---\nhttps://connect.comma.ai/a2a0ccea32023010/2023-07-27--13-01-19/5/10\n\n--- EXAMPLES ---\na2a0ccea32023010/2023-07-27--13-01-19/0     segment 0\na2a0ccea32023010/2023-07-27--13-01-19/0-1   segments 0 through 1\na2a0ccea32023010/2023-07-27--13-01-19/5/10  from 5 to 10 seconds\na2a0ccea32023010/2023-07-27--13-01-19       when using bookmark option\n```")
          return
        else:
          dongle, route, seg_start, seg_end = match.groups()

          if int(seg_start) == 0:
            # in_start = 2  # fix for 2s
            in_start = 0
          else:
            in_start = int(seg_start) * 60

          if seg_end is None:
            in_end = 60 if int(seg_start) == 0 else in_start + 60
          else:
            in_end = 60 if int(seg_end) == 0 else (int(seg_end) + 1) * 60
      else:
        dongle, route, in_start, in_end = match.groups()

      start = int(in_start)
      end = int(in_end)

      # fix for 2s
      # if start < 2 or end <= start:
      #   await fail("Start must be at least 2 and end must be greater than start.")
      #   return

      if end <= start:
        logging.error(f"❌ {user_tag(interaction.user)} entered bad times {input}")
        await fail("End must be greater than start time.")
        return
      duration = end - start
      if duration > MAX_CLIP_DURATION:
        logging.error(f"❌ {user_tag(interaction.user)} hit the max duration limit {input}")
        await fail(f"Clips must be {int(MAX_CLIP_DURATION / 60)} minutes or less.")
        return

    status_msg = await interaction.followup.send(
      "🕐 Waiting in queue..", ephemeral=private
    )

    if speed == 0:
      speed = 1
    if speed > 1:
      end = start + int(duration / speed)
    elif speed < 1:
      end = start + int(duration / speed)
    if bookmarks:
      route_str  = f"{dongle}/{route}"
      connect_route_str  = f"{dongle}/{route}"
      base   = f"{dongle}_{route}_bookmarks_{quality_value}"
    else:
      route_str  = f"{dongle}/{route}/{start}/{end}"
      connect_start = 1 if start == 0 else start
      connect_route_str  = f"{dongle}/{route}/{connect_start}/{end}"
      base   = f"{dongle}_{route}_{start}_{end}_{quality_value}"
    if wide:
      base += "_wide"
    if speed:
      base += f"_{speed}"
    base += f"_s{filesize}"
    clean_base = re.sub(r'[^A-Za-z0-9_-]+', '_', base)
    if title_cmd:
      title_hash = hashlib.sha1(title_cmd.encode()).hexdigest()[:10]
      safe_name  = f"{clean_base}_{title_hash}"
    else:
      safe_name  = clean_base

    safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', safe_name)

    if any(job["route"] == safe_name for job in clip_queue):
      await status_msg.edit(content="❌ That clip is already in the queue or processing – wait for it to finish.")
      return

    try:
      logs = CommaApi().get(f"/v1/route/{dongle}|{route}/files").get("logs")

      segments = [
        re.search(r'/(\d+)/rlog\.(?:zst|bz2)', url).group(1)
        for url in logs
        if re.search(r'/(\d+)/rlog\.(?:zst|bz2)', url)
      ]

      startsegment = start // 60
      endsegment = (end - 1) // 60

      segment_set = set(int(s) for s in segments)
      if bookmarks:
        missing = False
      else:
        missing = [i for i in range(startsegment, endsegment + 1) if i not in segment_set]

      if missing:
        logging.error(f"❌ {user_tag(interaction.user)} segments missing {missing}")
        await status_msg.edit(content=f"❌ You need to upload the missing logs for segments `{missing}` using [connect.comma.ai](https://connect.comma.ai/{connect_route_str})")
        return
      else:
        if bookmarks:
          logging.info(f"🕐 {user_tag(interaction.user)} getting bookmarks {route_str}")
          await status_msg.edit(content=f"🕐 Getting bookmarks")
        else:
          logging.info(f"☑️ {user_tag(interaction.user)} segments present {route_str}")
          await status_msg.edit(content=f"☑️ All required segments are present.")

    except UnauthorizedError as e:
      logging.error(f"❌ {user_tag(interaction.user)} unauthorized: {e}")
      await status_msg.edit(content=f"❌ You need to make the route public using [connect.comma.ai](https://connect.comma.ai/{route_str}). `/clippy-auth` is no longer supported.")
      return

    except Exception as e:
      logging.error(f"❌ {user_tag(interaction.user)} unexpected error: {e}")
      await status_msg.edit(content=f"❌ Error: unexpected error")
      return

    if bookmarks:
      try:
        route = Route(route_str)
        user_flags_at_time = []

        for segment in route.segments:
          for event in segment.events:
            if event['type'] == 'user_flag':
              user_flags_at_time.append(round(event['route_offset_millis'] / 1000))

      except Exception as e:
        logging.error(f"❌ {user_tag(interaction.user)} unauthorized: {e}")
        await status_msg.edit(content=f"❌ You need to make the route public using [connect.comma.ai](https://connect.comma.ai/{route_str}). `/clippy-auth` is no longer supported.")
        return

      if len(user_flags_at_time) == 0:
        logging.error(f"❌ {user_tag(interaction.user)} no bookmarks found")
        await status_msg.edit(content=f"❌ No bookmarks found")
        return
      else:
        bookmarklinks = ''
        for user_flag_at_time in user_flags_at_time:
          bookmarklinks += f"```{connect_route_str}/{user_flag_at_time - 10}/{user_flag_at_time + 5}```"
        logging.info(f"✅ {user_tag(interaction.user)} {len(user_flags_at_time)} bookmarks found! - {user_flags_at_time}")
        await status_msg.edit(content=f"✅ {len(user_flags_at_time)} bookmarks found! - {user_flags_at_time}{bookmarklinks}")
        return

    full_path   = os.path.join(CLIPS_DIR, f"{safe_name}.mp4")

    clip_queue.append({"user": interaction.user.display_name,
               "route": safe_name,
               "duration": duration,
               "status": "🕐"})
    save_stats()
    if private:
      logging.info(f"🕐 {user_tag(interaction.user)} queued (PRIVATE) {route_str}")
    else:
      logging.info(f"🕐 {user_tag(interaction.user)} queued {route_str}")

    if os.path.exists(full_path) and cache:
      stats["success"] += 1
      save_stats()
      for j in clip_queue:
        if j["route"] == safe_name:
          j["status"] = "✅"

      if private:
        logging.info(f"📁 {user_tag(interaction.user)} used cache (PRIVATE) {route_str}")
        await status_msg.edit(content="📁 Used cached clip.")
        if not (1 <= filesize <= 9):
          await interaction.followup.send(
            content=f"Preview for [`{route_str}`]({CLIPPY_BASE_URL}/{safe_name}.mp4)\n{title}",
            view=PublishView(route_str, title, full_path, interaction.user.id, filesize, safe_name),
            ephemeral=True
          )
        else:
          await interaction.followup.send(
            content=f"Preview for `{route_str}`\n{title}",
            file=discord.File(full_path),
            view=PublishView(route_str, title, full_path, interaction.user.id, filesize, safe_name),
            ephemeral=True
          )
      else:
        logging.info(f"📁 {user_tag(interaction.user)} used cache {route_str}")

        if not (1 <= filesize <= 9):
          published_msg = await interaction.channel.send(
            f"{interaction.user.mention} shared a [clip]({CLIPPY_BASE_URL}/{safe_name}.mp4) from [{route_str}](https://connect.comma.ai/{route_str})\n{title}"
          )
        else:
          published_msg = await interaction.channel.send(
            f"{interaction.user.mention} shared a clip from [{route_str}](https://connect.comma.ai/{route_str})\n{title}",
            file=discord.File(full_path)
          )
        await status_msg.edit(
          content="📁 Used cached clip.", attachments=[], view=DeletePublishedView(published_msg, interaction.user.id, full_path),
        )

    else:
      async with clip_semaphore:
        for j in clip_queue:
          if j["route"] == safe_name:
            j["status"] = "🔄"
        logging.info(f"🔄 {user_tag(interaction.user)} processing {route_str}")
        await status_msg.edit(content=f"🔄 Processing {j['duration']}s clip..")

        cmd = ["python3", "run.py", route_str, "-q", quality_value, "-x", str(speed), "-o", full_path]
        if not (in_start and in_end):
          if in_start != 0: # fix for 2s
            cmd += ["-s", str(start), "-e", str(end)]

        if title_cmd:
          cmd += ["-t", str(title_cmd)]

        if wide:
          cmd += ["-w"]

        if filesize:
          cmd += ["-f", str(filesize)]

        if developer:
          dev_mode = int(developer.value)
        else:
          dev_mode = 0
        cmd += ["-z", str(dev_mode)]

        proc = await asyncio.create_subprocess_exec(
          *cmd, cwd=WORKING_DIR,
          stdout=asyncio.subprocess.PIPE,
          stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        clean_err = "\n".join(stderr.decode().splitlines()[3:]) if stderr else ""

        if proc.returncode != 0 or not os.path.exists(full_path):
          for j in clip_queue:
            if j["route"] == safe_name:
              j["status"] = "❌"
          stats["fail"] += 1
          save_stats()
          logging.error(f"❌ {user_tag(interaction.user)} failed {route_str}\n{clean_err}")

          if clean_err == "clip.py: error: failed to get route: Unauthorized. Authenticate with tools/lib/auth.py":
            await status_msg.edit(content=f"❌ You need to make the route public using [connect.comma.ai](https://connect.comma.ai/{route_str}). `/clippy-auth` is no longer supported.")
          elif clean_err == "clip.py: error: failed to get route: 404:The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again.":
            await status_msg.edit(content="❌ This route does not exist, please try another.")
          else:
            await status_msg.edit(content="❌ Clip failed to generate.")
        else:
          for j in clip_queue:
            if j["route"] == safe_name:
              j["status"] = "✅"
          stats["success"] += 1
          save_stats()

          if private:
            logging.info(f"✅ {user_tag(interaction.user)} success (PRIVATE) {route_str}")
            await status_msg.edit(content="✅ Clip ready.")

            if not (1 <= filesize <= 9):
              await interaction.followup.send(
                content=f"Preview for [`{route_str}`]({CLIPPY_BASE_URL}/{safe_name}.mp4)\n{title}",
                view=PublishView(route_str, title, full_path, interaction.user.id, filesize, safe_name),
                ephemeral=True
              )
            else:
              await interaction.followup.send(
                content=f"Preview for `{route_str}`\n{title}",
                file=discord.File(full_path),
                view=PublishView(route_str, title, full_path, interaction.user.id, filesize, safe_name),
                ephemeral=True
              )
          else:
            logging.info(f"✅ {user_tag(interaction.user)} success {route_str}")

            if not (1 <= filesize <= 9):
              published_msg = await interaction.channel.send(
                f"{interaction.user.mention} shared a [clip]({CLIPPY_BASE_URL}/{safe_name}.mp4) from [{route_str}](https://connect.comma.ai/{route_str})\n{title}"
              )
            else:
              published_msg = await interaction.channel.send(
                f"{interaction.user.mention} shared a clip from [{route_str}](https://connect.comma.ai/{route_str})\n{title}",
                file=discord.File(full_path)
              )
            await status_msg.edit(
              content="✅ Clip ready.", attachments=[], view=DeletePublishedView(published_msg, interaction.user.id, full_path),
            )

    await asyncio.sleep(1)
    clip_queue[:] = [j for j in clip_queue if j["route"] != safe_name]

  finally:
    if user_id in user_cooldowns:
      user_cooldowns[user_id] = max(0, user_cooldowns[user_id] - 1)
    clip_queue[:] = [j for j in clip_queue if j["route"] != safe_name]


@bot.tree.command(name="clippy-stats", description="View clippy stats")
async def clippy_stats(interaction: discord.Interaction):

  if interaction.guild_id not in ALLOWED_GUILD_IDS:
    logging.error(f"❌ This bot is not available in this server {interaction.guild_id}")
    await interaction.response.send_message("❌ This bot is not available in this server.", ephemeral=True)
    return

  if not has_any_role(interaction.user, CLIPPY_STATS_ALLOWED_ROLES):
    logging.error(f"🚫 {user_tag(interaction.user)} not allowed to use /clippy-stats")
    await interaction.response.send_message("🚫 You don't have permission.", ephemeral=True)
    return

  stat  = f"Total: {stats['total']} | ✅ {stats['success']} | ❌ {stats['fail']}"
  queue = "\n".join(f"{j['status']} {j['user']}: {j['route']}" for j in clip_queue) or "No active jobs."
  tail  = "\n".join(list(tail_buffer)[-5:][::-1]) or "[no log records yet]"

  content = f"```{stat}``````{queue}``````{tail}"
  await interaction.response.send_message(content[:1997] + "```", ephemeral=True)
  logging.info(f"✅ {user_tag(interaction.user)} used /clippy-stats")


@bot.event
async def on_ready():
  await bot.tree.sync()
  for guild in bot.guilds:
    logging.info(f"Connected to guild: {guild.name} ({guild.id})")
  await bot.change_presence(activity=discord.Game(name="your clips"))
  asyncio.create_task(queue_monitor())
  print(f"Logged in as {bot.user}")

threading.Thread(target=start_clip_server, daemon=True).start()
bot.run(CLIPPY_TOKEN)
