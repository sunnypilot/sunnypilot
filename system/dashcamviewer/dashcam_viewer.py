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
  return """<html>
  <head>
    <meta name="viewport" content="initial-scale=1, width=device-width"/>
    <link href="/static/favicon.ico" rel="icon">
    <title>Dashcam Footage</title>
  </head>
  <body>
  <center>
    <video id="video" width="320" height="240" controls autoplay="autoplay" style="background:black">
    </video>
    <br><br>
    current segment: <span id="currentsegment"></span>
    <br>
    current view: <span id="currentview"></span>
    <br>
    <a download=\""""+route+"-"+ query_type + ".mp4" + """\" href=\"/footage/full/"""+query_type+"""/"""+route+"""\">download full route """ + query_type + """</a>
    <br><br>
    <a href="/footage">back to routes</a>
    <br><br>
    <a href=\""""+route+"""?0,qcamera\">qcamera</a> -
    <a href=\""""+route+"""?0,fcamera\">fcamera</a> -
    <a href=\""""+route+"""?0,dcamera\">dcamera</a> -
    <a href=\""""+route+"""?0,ecamera\">ecamera</a>
    <br><br>
    """+links+"""
  </center>
  </body>
    <script>
    var video = document.getElementById('video');
    var tracks = {
      list: ["""+segments+"""],
      index: """+query_segment+""",
      next: function() {
        if (this.index == this.list.length - 1) this.index = 0;
        else {
            this.index += 1;
        }
      },
      play: function() {
        return ( \""""+query_type+"""/" + this.list[this.index] );
      }
    }
    video.addEventListener('ended', function(e) {
      tracks.next();
      video.src = tracks.play();
      document.getElementById("currentsegment").textContent=video.src.split("/")[5];
      document.getElementById("currentview").textContent=video.src.split("/")[4];
      video.load();
      video.play();
    });
    video.src = tracks.play();
    document.getElementById("currentsegment").textContent=video.src.split("/")[5];
    document.getElementById("currentview").textContent=video.src.split("/")[4];
    </script>
</html>
"""


@app.route("/footage")
def index():
  result = """
  <html>
    <head>
      <meta name="viewport" content="initial-scale=1, width=device-width"/>
      <link href="/static/favicon.ico" rel="icon">
      <title>Dashcam Footage</title>
    </head>
    <body><center><br><a href='\\'>Back to landing page</a><br>"""
  for route in all_routes():
    result += "<a href='footage/"+route+"'>"+route+"</a><br>"
  result += """</center></body></html>"""
  return result


def main():
  app.run(host="0.0.0.0")


if __name__ == '__main__':
  main()
