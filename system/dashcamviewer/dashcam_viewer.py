#!/usr/bin/env python3
import os
import random
import secrets
import system.dashcamviewer.helpers as dashcam
from flask import Flask, render_template, Response, request, send_from_directory, session, redirect, url_for
from functools import wraps
from system.loggerd.config import ROOT as REALDATA

app = Flask(__name__)


def login_required(f):
  @wraps(f)
  def decorated_route(*args, **kwargs):
    if not session.get("logged_in"):
      return redirect(url_for("index_page"))
    return f(*args, **kwargs)
  return decorated_route


@app.route("/")
def index_page():
  if session.get("logged_in"):
    return redirect(url_for("home_page"))
  return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():
  inputted_pin = request.form.get("pin")
  with open(dashcam.PIN_PATH + "otp.conf", "r") as file:
    correct_pin = file.read().strip()

  if inputted_pin == correct_pin:
    session["logged_in"] = True
    return redirect(url_for("home_page"))
  else:
    error_message = "Incorrect PIN. Please try again."
    return render_template("login.html", error=error_message)


@app.route("/index")
@login_required
def home_page():
  return render_template("index.html")


@app.route("/footage/full/<cameratype>/<route>")
@login_required
def full(cameratype, route):
  chunk_size = 1024 * 512  # 5KiB
  file_name = cameratype + (".ts" if cameratype == "qcamera" else ".hevc")
  vidlist = "|".join(REALDATA + "/" + segment + "/" + file_name for segment in dashcam.segments_in_route(route))

  def generate_buffered_stream():
    with dashcam.ffmpeg_mp4_concat_wrap_process_builder(vidlist, cameratype, chunk_size) as process:
      for chunk in iter(lambda: process.stdout.read(chunk_size), b""):
        yield bytes(chunk)
  return Response(generate_buffered_stream(), status=200, mimetype='video/mp4')


@app.route("/footage/<cameratype>/<segment>")
@login_required
def fcamera(cameratype, segment):
  if not dashcam.is_valid_segment(segment):
    return render_template("error.html", error="invalid segment")
  file_name = REALDATA + "/" + segment + "/" + cameratype + (".ts" if cameratype == "qcamera" else ".hevc")
  return Response(dashcam.ffmpeg_mp4_wrap_process_builder(file_name).stdout.read(), status=200, mimetype='video/mp4')


@app.route("/footage/<route>")
@login_required
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
  for segment in dashcam.segments_in_route(route):
    links += "<a href='"+route+"?"+segment.split("--")[2]+","+query_type+"'>"+segment+"</a><br>"
    segments += "'"+segment+"',"
  return render_template("route.html", route=route, query_type=query_type, links=links, segments=segments, query_segment=query_segment)


@app.route("/footage")
@login_required
def footage():
  return render_template("footage.html", rows=dashcam.all_routes())


@app.route("/screenrecords")
@login_required
def screenrecords():
  rows = dashcam.all_screenrecords()
  if not rows:
    return render_template("error.html", error="no screenrecords found at:<br><br>" + dashcam.SCREENRECORD_PATH)
  return render_template("screenrecords.html", rows=rows, clip=rows[0])


@app.route("/screenrecords/<clip>")
@login_required
def screenrecord(clip):
  return render_template("screenrecords.html", rows=dashcam.all_screenrecords(), clip=clip)


@app.route("/screenrecords/play/pipe/<file>")
@login_required
def videoscreenrecord(file):
  file_name = dashcam.SCREENRECORD_PATH + file
  return Response(dashcam.ffplay_mp4_wrap_process_builder(file_name).stdout.read(), status=200, mimetype='video/mp4')


@app.route("/screenrecords/download/<clip>")
@login_required
def download_file(clip):
  return send_from_directory(dashcam.SCREENRECORD_PATH, clip, as_attachment=True)


@app.route("/about")
@login_required
def about():
  return render_template("about.html")


def main():
  if not os.path.exists(dashcam.PIN_PATH):
    os.makedirs(dashcam.PIN_PATH)
  pin = str(random.randint(100000, 999999))
  with open(dashcam.PIN_PATH + "otp.conf", "w") as file:
    file.write(pin)

  app.secret_key = secrets.token_hex(32)
  app.run(host="0.0.0.0", port=5050)


if __name__ == '__main__':
  main()
