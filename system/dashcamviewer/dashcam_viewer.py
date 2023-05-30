#!/usr/bin/env python3
from flask import Flask, render_template, Response, request
from system.dashcamviewer.helpers import *

app = Flask(__name__)


@app.route("/")
def index_page():
  return render_template("index.html")


@app.route("/footage/full/<cameratype>/<route>")
def full(cameratype, route):
  chunk_size = 1024 * 512  # 5KiB
  file_name = cameratype + (".ts" if cameratype == "qcamera" else ".hevc")
  vidlist = "|".join(ROOT + "/" + segment + "/" + file_name for segment in segments_in_route(route))

  def generate_buffered_stream():
    with ffmpeg_mp4_concat_wrap_process_builder(vidlist, cameratype, chunk_size) as process:
      for chunk in iter(lambda: process.stdout.read(chunk_size), b""):
        yield bytes(chunk)
  return Response(generate_buffered_stream(), status=200, mimetype='video/mp4')


@app.route("/footage/<cameratype>/<segment>")
def fcamera(cameratype, segment):
  if not is_valid_segment(segment):
    return "invalid segment"
  file_name = ROOT + "/" + segment + "/" + cameratype + (".ts" if cameratype == "qcamera" else ".hevc")
  return Response(ffmpeg_mp4_wrap_process_builder(file_name).stdout.read(), status=200, mimetype='video/mp4')


@app.route("/footage/<route>")
def route(route):
  if len(route) != 20:
    return "route not found"

  if str(request.query_string) == "b''":
    query_segment = str("0")
    query_type = "qcamera"
  else:
    query_segment = (str(request.query_string).split(","))[0][2:]
    query_type = (str(request.query_string).split(","))[1][:-1]

  links = ""
  segments = ""
  for segment in segments_in_route(route):
    links += "<a href='"+route+"?"+segment.split("--")[2]+","+query_type+"'>"+segment+"</a><br>"
    segments += "'"+segment+"',"
  return render_template("route.html",route=route, query_type=query_type, links=links, segments=segments, query_segment=query_segment)
  

@app.route("/footage")
def footage():
  return render_template("footage.html", rows=all_routes())


@app.route("/screenrecords")
def screenrecords():
  return render_template("screenrecords.html", rows=all_screenrecords())


def main():
  app.run(host="0.0.0.0")


if __name__ == '__main__':
  main()
