<!doctype html>
<html>
<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="initial-scale=1.0, user-scalable=no, width=device-width">
    <title>输入提示后查询</title>
    <!-- UIkit CSS -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/uikit@3.9.2/dist/css/uikit.min.css" />

    <!-- UIkit JS -->
    <script src="https://cdn.jsdelivr.net/npm/uikit@3.9.2/dist/js/uikit.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/uikit@3.9.2/dist/js/uikit-icons.min.js"></script>
    <link rel="stylesheet" href="./style.css"/>
    <script type="text/javascript">
            window._AMapSecurityConfig = {
                securityJsCode:'{{amap_key_2}}',
            }
    </script>
    <script type="text/javascript"
            src="https://webapi.amap.com/maps?v=1.4.2&key={{amap_key}}"></script>
    <style type="text/css">
        body {
            font-size: 12px;
        }
    </style>
</head>
<body>
  <div style="place-items: center; padding: 5px; font-weight: bold;" align="center"><a href="?reset=1"><img style="width: 100px; height: 100px; background-color: black;" src="logo.png"></a></div>
  <div class="uk-grid-match uk-grid-small uk-text-center" uk-grid>
    <div class="uk-width-1-3@m">
      <select id="save_type" class="uk-select">
        <option value="recent">最近</option>
        <option value="home">住家</option>
        <option value="work">工作</option>
      </select>
    </div>
    <div class="uk-width-expand@m">
      <input class="uk-input" type="text" id="keyword" name="keyword" placeholder="请输入关键字：(选定后搜索)" onfocus='this.value=""'/>
    </div>
  </div>
  <input type="hidden" id="longitude" />
  <input type="hidden" id="latitude" />
  <div style="height: 80%" id="container"></div>
  <script src="./index.js"></script>
</body>
</html>