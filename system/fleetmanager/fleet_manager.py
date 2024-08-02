#!/usr/bin/env python3
import os
import random
import secrets
import threading
import time
from flask import Flask, render_template, Response, request, send_from_directory, session, redirect, url_for
from openpilot.common.realtime import set_core_affinity
import openpilot.system.fleetmanager.helpers as fleet
from openpilot.system.hardware.hw import Paths
from openpilot.common.swaglog import cloudlog

app = Flask(__name__)


@app.route("/")
@app.route("/index")
def home_page():
  return render_template("index.html")


@app.route("/login", methods=["POST"])
def login():
  inputted_pin = request.form.get("pin")
  with open(fleet.PIN_PATH + "otp.conf", "r") as file:
    correct_pin = file.read().strip()

  if inputted_pin == correct_pin:
    session["logged_in"] = True
    if "previous_page" in session:
      previous_page = session["previous_page"]
      session.pop("previous_page", None)
      return redirect(previous_page)
    else:
      return redirect(url_for("home_page"))
  else:
    error_message = "Incorrect PIN. Please try again."
    return render_template("login.html", error=error_message)


@app.route("/footage/full/<cameratype>/<route>")
@fleet.login_required
def full(cameratype, route):
  chunk_size = 1024 * 512  # 5KiB
  file_name = cameratype + (".ts" if cameratype == "qcamera" else ".hevc")
  vidlist = "|".join(Paths.log_root() + "/" + segment + "/" + file_name for segment in fleet.segments_in_route(route))

  def generate_buffered_stream():
    with fleet.ffmpeg_mp4_concat_wrap_process_builder(vidlist, cameratype, chunk_size) as process:
      for chunk in iter(lambda: process.stdout.read(chunk_size), b""):
        yield bytes(chunk)
  return Response(generate_buffered_stream(), status=200, mimetype='video/mp4')


@app.route("/footage/<cameratype>/<segment>")
@fleet.login_required
def fcamera(cameratype, segment):
  if not fleet.is_valid_segment(segment):
    return render_template("error.html", error="invalid segment")
  file_name = Paths.log_root() + "/" + segment + "/" + cameratype + (".ts" if cameratype == "qcamera" else ".hevc")
  return Response(fleet.ffmpeg_mp4_wrap_process_builder(file_name).stdout.read(), status=200, mimetype='video/mp4')


@app.route("/footage/<route>")
@fleet.login_required
def route(route):
  if len(route) != 20:
    return render_template("error.html", error="route not found")

  if str(request.query_string) == "b''":
    query_segment = str("0")
    query_type = "qcamera"
  else:
    query_segment = (str(request.query_string).split(","))[0][2:]
    query_type = (str(request.query_string).split(","))[1][:-1]

  links = ""
  segments = ""
  for segment in fleet.segments_in_route(route):
    links += "<a href='"+route+"?"+segment.split("--")[2]+","+query_type+"'>"+segment+"</a><br>"
    segments += "'"+segment+"',"
  return render_template("route.html", route=route, query_type=query_type, links=links, segments=segments, query_segment=query_segment)


@app.route("/footage/")
@app.route("/footage")
@fleet.login_required
def footage():
  return render_template("footage.html", rows=fleet.all_routes())


@app.route("/screenrecords/")
@app.route("/screenrecords")
@fleet.login_required
def screenrecords():
  rows = fleet.list_files(fleet.SCREENRECORD_PATH, True)
  if not rows:
    return render_template("error.html", error="no screenrecords found at:<br><br>" + fleet.SCREENRECORD_PATH)
  return render_template("screenrecords.html", rows=rows, clip=rows[0])


@app.route("/screenrecords/<clip>")
@fleet.login_required
def screenrecord(clip):
  return render_template("screenrecords.html", rows=fleet.list_files(fleet.SCREENRECORD_PATH), clip=clip)


@app.route("/screenrecords/play/pipe/<file>")
@fleet.login_required
def videoscreenrecord(file):
  file_name = fleet.SCREENRECORD_PATH + file
  return Response(fleet.ffplay_mp4_wrap_process_builder(file_name).stdout.read(), status=200, mimetype='video/mp4')


@app.route("/screenrecords/download/<clip>")
@fleet.login_required
def download_file(clip):
  return send_from_directory(fleet.SCREENRECORD_PATH, clip, as_attachment=True)


@app.route("/about")
def about():
  return render_template("about.html")


@app.route("/error_logs")
def error_logs():
  return render_template("error_logs.html", rows=fleet.list_files(fleet.ERROR_LOGS_PATH))


@app.route("/error_logs/<file_name>")
def open_error_log(file_name):
  f = open(fleet.ERROR_LOGS_PATH + file_name)
  error = f.read()
  return render_template("error_log.html", file_name=file_name, file_content=error)


def generate_pin():
  if not os.path.exists(fleet.PIN_PATH):
    os.makedirs(fleet.PIN_PATH)
  pin = str(random.randint(100000, 999999))
  with open(fleet.PIN_PATH + "otp.conf", "w") as file:
    file.write(pin)


def schedule_pin_generate():
  pin_thread = threading.Thread(target=update_pin)
  pin_thread.start()


def update_pin():
  while True:
    generate_pin()
    time.sleep(30)


def main():
  try:
    set_core_affinity([0, 1, 2, 3])
  except Exception:
    cloudlog.exception("fleet_manager: failed to set core affinity")
  app.secret_key = secrets.token_hex(32)
  schedule_pin_generate()
  app.run(host="0.0.0.0", port=5050)


if __name__ == '__main__':
  main()
