#!/usr/bin/env python3.8
# The MIT License
#
# Copyright (c) 2019-, Rick Lan, dragonpilot community, and a number of other of contributors.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from http.server import BaseHTTPRequestHandler, HTTPServer
from cgi import parse_header, parse_multipart
from urllib.parse import parse_qs, unquote
import json
import requests
import math
from common.basedir import BASEDIR
from common.params import Params
from common.realtime import set_core_affinity
from system.swaglog import cloudlog
params = Params()

hostName = ""
serverPort = 8082

pi = 3.1415926535897932384626
x_pi = 3.14159265358979324 * 3000.0 / 180.0
a = 6378245.0
ee = 0.00669342162296594323


class OtisServ(BaseHTTPRequestHandler):
  def do_GET(self):
    use_amap = params.get_bool("EnableAmap")
    use_gmap = not use_amap and params.get_bool("EnableGmap")

    if self.path == '/logo.png':
      self.get_logo()
      return
    if self.path == '/?reset=1':
      params.put("NavDestination", "")
    if use_amap:
      if self.path == '/style.css':
        self.send_response(200)
        self.send_header("Content-type", "text/css")
        self.end_headers()
        self.get_amap_css()
        return
      elif self.path == '/index.js':
        self.send_response(200)
        self.send_header("Content-type", "text/javascript")
        self.end_headers()
        self.get_amap_js()
        return
      else:
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        if self.get_amap_key() is None or self.get_amap_key_2() is None:
          self.display_page_amap_key()
          return
        if self.get_app_token() is None:
          self.display_page_app_token()
          return
        self.display_page_amap()
    elif use_gmap:
      if self.path == '/style.css':
        self.send_response(200)
        self.send_header("Content-type", "text/css")
        self.end_headers()
        self.get_gmap_css()
        return
      elif self.path == '/index.js':
        self.send_response(200)
        self.send_header("Content-type", "text/javascript")
        self.end_headers()
        self.get_gmap_js()
        return
      else:
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        if self.get_gmap_key() is None:
          self.display_page_gmap_key()
          return
        if self.get_app_token() is None:
          self.display_page_app_token()
          return
        self.display_page_gmap()
    else:
      self.send_response(200)
      self.send_header("Content-type", "text/html")
      self.end_headers()
      if self.get_public_token() is None:
        self.display_page_public_token()
        return
      if self.get_app_token() is None:
        self.display_page_app_token()
        return
      self.display_page_addr_input()

  def do_POST(self):
    use_amap = params.get_bool("EnableAmap")
    use_gmap = not use_amap and params.get_bool("EnableGmap")

    postvars = self.parse_POST()
    self.send_response(200)
    self.send_header("Content-type", "text/html")
    self.end_headers()

    if use_amap:
      # amap token
      if self.get_amap_key() is None or self.get_amap_key_2() is None:
        if postvars is None or \
                ("amap_key_val" not in postvars or postvars.get("amap_key_val")[0] == "") or \
                ("amap_key_val_2" not in postvars or postvars.get("amap_key_val_2")[0] == ""):
          self.display_page_amap_key()
          return
        params.put("AmapKey1", postvars.get("amap_key_val")[0])
        params.put("AmapKey2", postvars.get("amap_key_val_2")[0])

    elif use_gmap:
      # gmap token
      if self.get_gmap_key() is None:
        if postvars is None or "gmap_key_val" not in postvars or postvars.get("gmap_key_val")[0] == "":
          self.display_page_gmap_key()
          return
        params.put("GmapKey", postvars.get("gmap_key_val")[0])

    else:
      # mapbox public key
      if self.get_public_token() is None:
        if postvars is None or "pk_token_val" not in postvars or postvars.get("pk_token_val")[0] == "":
          self.display_page_public_token()
          return
        token = postvars.get("pk_token_val")[0]
        if "pk." not in token:
          self.display_page_public_token("Your token was incorrect!")
          return
        params.put('CustomMapboxTokenPk', token)

    # app key
    if self.get_app_token() is None:
      if postvars is None or "sk_token_val" not in postvars or postvars.get("sk_token_val")[0] == "":
        self.display_page_app_token()
        return
      token = postvars.get("sk_token_val")[0]
      if "sk." not in token:
        self.display_page_app_token("Your token was incorrect!")
        return
      params.put('CustomMapboxTokenSk', token)

    # nav confirmed
    if postvars is not None:
      if "lat" in postvars and postvars.get("lat")[0] != "" and "lon" in postvars and postvars.get("lon")[0] != "":
        lat = float(postvars.get("lat")[0])
        lng = float(postvars.get("lon")[0])
        save_type = postvars.get("save_type")[0]
        name = postvars.get("name")[0] if postvars.get("name") is not None else ""
        if use_amap:
          lng, lat = self.gcj02towgs84(lng, lat)
        params.put('NavDestination', "{\"latitude\": %f, \"longitude\": %f, \"place_name\": \"%s\"}" % (lat, lng, name))
        self.to_json(lat, lng, save_type, name)
      # favorites
      if not use_gmap and "fav_val" in postvars:
        addr = postvars.get("fav_val")[0]
        real_addr = None
        lon = None
        lat = None
        if addr != "favorites":
          val = params.get("ApiCache_NavDestinations", encoding='utf8')
          if val is not None:
            val = val.rstrip('\x00')
            dests = json.loads(val)
            for item in dests:
              if "label" in item and item["label"] == addr:
                lat = item["latitude"]
                lon = item["longitude"]
                real_addr = item["place_name"]
                break
            else:
              real_addr = None
          if real_addr is not None:
            self.display_page_nav_confirmation(real_addr, lon, lat)
            return
          else:
            self.display_page_addr_input("Place Not Found")
            return
      # search
      if not use_gmap and "addr_val" in postvars:
        addr = postvars.get("addr_val")[0]
        if addr != "":
          real_addr, lat, lon = self.query_addr(addr)
          if real_addr is not None:
            self.display_page_nav_confirmation(real_addr, lon, lat)
            return
          else:
            self.display_page_addr_input("Place Not Found")
            return
    if use_amap:
      self.display_page_amap()
    elif use_gmap:
      self.display_page_gmap()
    else:
      self.display_page_addr_input()

  def get_logo(self):
    self.send_response(200)
    self.send_header('Content-type','image/png')
    self.end_headers()
    f = open("%s/selfdrive/assets/img_spinner_comma.png" % BASEDIR, "rb")
    self.wfile.write(f.read())
    f.close()

  def get_gmap_css(self):
    self.wfile.write(bytes(self.get_parsed_template("gmap/style.css"), "utf-8"))

  def get_gmap_js(self):
    lon, lat = self.get_last_lon_lat()
    self.wfile.write(bytes(self.get_parsed_template("gmap/index.js", {"{{lat}}": lat, "{{lon}}": lon}), "utf-8"))

  def get_gmap_key(self):
    token = params.get("GmapKey", encoding='utf8')
    if token is not None and token != "":
      return token.rstrip('\x00')
    return None

  def get_amap_css(self):
    self.wfile.write(bytes(self.get_parsed_template("amap/style.css"), "utf-8"))

  def get_amap_js(self):
    lon, lat = self.get_last_lon_lat()
    self.wfile.write(bytes(self.get_parsed_template("amap/index.js", {"{{lat}}": lat, "{{lon}}": lon}), "utf-8"))

  def get_amap_key(self):
    token = params.get("AmapKey1", encoding='utf8')
    if token is not None and token != "":
      return token.rstrip('\x00')
    return None

  def get_amap_key_2(self):
    token = params.get("AmapKey2", encoding='utf8')
    if token is not None and token != "":
      return token.rstrip('\x00')
    return None

  def get_public_token(self):
    token = params.get("CustomMapboxTokenPk", encoding='utf8')
    if token is not None and token != "":
      return token.rstrip('\x00')
    return None

  def get_app_token(self):
    token = params.get("CustomMapboxTokenSk", encoding='utf8')
    if token is not None and token != "":
      return token.rstrip('\x00')
    return None

  def get_last_lon_lat(self):
    last_pos = Params().get("LastGPSPosition")
    if last_pos is not None and last_pos != "":
      l = json.loads(last_pos)
      return l["longitude"], l["latitude"]
    return "", ""

  def display_page_gmap_key(self):
    self.wfile.write(bytes(self.get_parsed_template("body", {"{{content}}": self.get_parsed_template("gmap/key_input")}), "utf-8"))

  def display_page_amap_key(self):
    self.wfile.write(bytes(self.get_parsed_template("body", {"{{content}}": self.get_parsed_template("amap/key_input")}), "utf-8"))

  def display_page_public_token(self, msg = ""):
    self.wfile.write(bytes(self.get_parsed_template("body", {"{{content}}": self.get_parsed_template("public_token_input", {"{{msg}}": msg})}), "utf-8"))

  def display_page_app_token(self, msg = ""):
    self.wfile.write(bytes(self.get_parsed_template("body", {"{{content}}": self.get_parsed_template("app_token_input", {"{{msg}}": msg})}), "utf-8"))

  def display_page_addr_input(self, msg = ""):
    self.wfile.write(bytes(self.get_parsed_template("body", {"{{content}}": self.get_parsed_template("addr_input", {"{{msg}}": msg})}), "utf-8"))

  def display_page_nav_confirmation(self, addr, lon, lat):
    content = self.get_parsed_template("addr_input", {"{{msg}}": ""}) + self.get_parsed_template("nav_confirmation", {"{{token}}": self.get_public_token(), "{{lon}}": lon, "{{lat}}": lat, "{{addr}}": addr})
    self.wfile.write(bytes(self.get_parsed_template("body", {"{{content}}": content }), "utf-8"))

  def display_page_gmap(self):
    self.wfile.write(bytes(self.get_parsed_template("gmap/index.html", {"{{gmap_key}}": self.get_gmap_key()}), "utf-8"))

  def display_page_amap(self):
    self.wfile.write(bytes(self.get_parsed_template("amap/index.html", {"{{amap_key}}": self.get_amap_key(), "{{amap_key_2}}": self.get_amap_key_2()}), "utf-8"))

  def get_parsed_template(self, name, replace = {}):
    f = open('%s/selfdrive/navd/tpl/%s.tpl' % (BASEDIR, name), mode='r', encoding='utf-8')
    content = f.read()
    for key in replace:
      content = content.replace(key, str(replace[key]))
    f.close()
    return content

  def query_addr(self, addr):
    if addr == "":
      return None, None, None
    query = "https://api.mapbox.com/geocoding/v5/mapbox.places/" + unquote(addr) + ".json?access_token=" + self.get_public_token() + "&limit=1"
    # focus on place around last gps position
    last_pos = Params().get("LastGPSPosition")
    if last_pos is not None and last_pos != "":
      l = json.loads(last_pos)
      query += "&proximity=%s,%s" % (l["longitude"], l["latitude"])

    r = requests.get(query)
    if r.status_code != 200:
      return None, None, None

    j = json.loads(r.text)
    if not j["features"]:
      return None, None, None

    feature = j["features"][0]
    return feature["place_name"], feature["center"][1], feature["center"][0]

  def parse_POST(self):
    ctype, pdict = parse_header(self.headers['content-type'])
    if ctype == 'application/x-www-form-urlencoded':
      length = int(self.headers['content-length'])
      postvars = parse_qs(
        self.rfile.read(length).decode('utf-8'),
        keep_blank_values=1)
    else:
      postvars = {}
    return postvars

  def gcj02towgs84(self, lng, lat):
    dlat = self.transform_lat(lng - 105.0, lat - 35.0)
    dlng = self.transform_lng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * pi
    magic = math.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)
    dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * pi)
    mglat = lat + dlat
    mglng = lng + dlng
    return [lng * 2 - mglng, lat * 2 - mglat]

  def transform_lat(self, lng, lat):
    ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + 0.1 * lng * lat + 0.2 * math.sqrt(abs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 * math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lat * pi) + 40.0 * math.sin(lat / 3.0 * pi)) * 2.0 / 3.0
    ret += (160.0 * math.sin(lat / 12.0 * pi) + 320 * math.sin(lat * pi / 30.0)) * 2.0 / 3.0
    return ret

  def transform_lng(self, lng, lat):
    ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + 0.1 * lng * lat + 0.1 * math.sqrt(abs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 * math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lng * pi) + 40.0 * math.sin(lng / 3.0 * pi)) * 2.0 / 3.0
    ret += (150.0 * math.sin(lng / 12.0 * pi) + 300.0 * math.sin(lng / 30.0 * pi)) * 2.0 / 3.0
    return ret

  def to_json(self, lat, lng, type = "recent", name = ""):
    if name == "":
      name =  str(lat) + "," + str(lng)
    new_dest = {"latitude": float(lat), "longitude": float(lng), "place_name": name}

    if type == "recent":
      new_dest["save_type"] = "recent"
    else:
      new_dest["save_type"] = "favorite"
      new_dest["label"] = type

    val = params.get("ApiCache_NavDestinations", encoding='utf8')
    if val is not None:
      val = val.rstrip('\x00')
    dests = [] if val is None else json.loads(val)

    # type idx
    type_label_ids = {"home": None, "work": None, "fav1": None, "fav2": None, "fav3": None, "recent": []}
    idx = 0
    for d in dests:
      if d["save_type"] == "favorite":
        type_label_ids[d["label"]] = idx
      else:
        type_label_ids["recent"].append(idx)
      idx += 1

    if type == "recent":
      id = None
      if len(type_label_ids["recent"]) > 10:
        dests.pop(type_label_ids["recent"][-1])
    else:
      id = type_label_ids[type]

    if id is None:
      dests.insert(0, new_dest)
    else:
      dests[id] = new_dest

    params.put("ApiCache_NavDestinations", json.dumps(dests).rstrip("\n\r"))

def main():
  try:
    set_core_affinity([0, 1, 2, 3])
  except Exception:
    cloudlog.exception("otisserv: failed to set core affinity")
  webServer = HTTPServer((hostName, serverPort), OtisServ)

  try:
    webServer.serve_forever()
  except KeyboardInterrupt:
    pass

  webServer.server_close()

if __name__ == "__main__":
  main()
