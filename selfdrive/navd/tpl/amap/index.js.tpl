var windowsArr = [];
var markers = [];
var map = new AMap.Map("container", {
  resizeEnable: true,
  center: [{{lon}}, {{lat}}], //地图中心点
  zoom: 13, //地图显示的缩放级别
  keyboardEnable: false,
});

var infoWindow;
function openInfo(name, addr, lng, lat) {
  //构建信息窗体中显示的内容
  var info = [];
  info.push('<div class="uk-card uk-card-default uk-card-body">');
  info.push('<a class="uk-card-badge uk-label" onClick="javascript:infoWindow.close()" uk-close></a>');
  info.push("<h3 style=\"padding-top: 10px;\" class=\"uk-card-title\">" + name + "</h3>");
  info.push("<p>" + addr + "</p>");
  info.push('<div class="uk-card-footer">');
  info.push('<form name="navForm" method="post">');
  info.push('  <input type="hidden" name="lat" value="' + lat + '">');
  info.push('  <input type="hidden" name="lon" value="' + lng + '">');
  info.push('  <input type="hidden" name="save_type" value="' + document.getElementById("save_type").value + '">');
  info.push('  <input type="hidden" name="name" value="' + name + '">');
  info.push('  <input class="uk-button uk-button-primary" type="submit" value="导航" >');
  info.push('</form>');
  info.push('</div>');
  info.push("</div>");

  var pos = new AMap.LngLat(lng, lat)
  infoWindow = new AMap.InfoWindow({
    position: pos,
    isCustom: true,
    offset: new AMap.Pixel(0, -30),
    content: info.join(""), //使用默认信息窗体框样式，显示信息内容
  });

  infoWindow.open(map, pos);
}
AMap.plugin(["AMap.Autocomplete", "AMap.PlaceSearch"], function () {
  var autoOptions = {
    city: "全国", //城市，默认全国
    input: "keyword", //使用联想输入的input的id
  };
  autocomplete = new AMap.Autocomplete(autoOptions);
  var placeSearch = new AMap.PlaceSearch({
    map: "",
  });
  AMap.event.addListener(autocomplete, "select", function (e) {
    //TODO 针对选中的poi实现自己的功能
    //重寫搜尋點及其提示資訊begin=====
    placeSearch.setCity(e.poi.adcode);
    if (e.poi && e.poi.location) {
      map.setZoom(17);
      map.setCenter(e.poi.location);
    }
    placeSearch.search(e.poi.name, check_dest); //關鍵字查詢查詢

    function check_dest(status, result) {
      if (status === "complete" && result.info === "OK") {
        for (var h = 0; h < result.poiList.pois.length; h++) {
          //返回搜尋列表迴圈繫結marker
          var jy = result.poiList.pois[h]["location"]; //經緯度
          var name = result.poiList.pois[h]["name"]; //地址
          marker = new AMap.Marker({
            //加點
            map: map,
            position: jy,
          });
          marker.extData = {
            getLng: jy["lng"],
            getLat: jy["lat"],
            name: name,
            address: result.poiList.pois[h]["address"],
          }; //自定義想傳入的引數

          marker.on("click", function (e) {
            var hs = e.target.extData;
            var content = openInfo(
              hs["name"],
              hs["address"],
              hs["getLng"],
              hs["getLat"]
            );
          });
          markers.push(marker);
        }
      }
    }
    //重寫搜尋點及其提示資訊end=====
  });
});
var clickEventListener = map.on('click', function(e)  {
  map.remove(markers);
  document.getElementById('longitude').value = e.lnglat.getLng();
  document.getElementById('latitude').value = e.lnglat.getLat();
  lnglatXY = [e.lnglat.getLng(), e.lnglat.getLat()];
  var marker = new AMap.Marker({
    //加點
    map: map,
    position: lnglatXY,
  });
  marker.extData = {
    getLng: e.lnglat.getLng(),
    getLat: e.lnglat.getLat(),
  }; //自定義想傳入的引數

  marker.on("click", function (e) {
    var hs = e.target.extData;
    var content = openInfo(
      "",
      "(" + hs["getLat"] + ", " + hs["getLng"] + ")",
      hs["getLng"],
      hs["getLat"]
    );
  });
  markers.push(marker);
  if (typeof(infoWindow) != "undefined") {
    infoWindow.close();
  }
});