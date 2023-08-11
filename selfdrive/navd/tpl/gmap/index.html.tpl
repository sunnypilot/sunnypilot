<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <title>sunnypilot</title>
    <script src="https://polyfill.io/v3/polyfill.min.js?features=default"></script>
    <link rel="stylesheet" type="text/css" href="./style.css" />
    <!-- UIkit CSS -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/uikit@3.9.2/dist/css/uikit.min.css" />

    <!-- UIkit JS -->
    <script src="https://cdn.jsdelivr.net/npm/uikit@3.9.2/dist/js/uikit.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/uikit@3.9.2/dist/js/uikit-icons.min.js"></script>

    <script src="./index.js"></script>
    <meta name="viewport" content="width=device-width">
  </head>
  <body>
    <div style="place-items: center; padding: 5px; font-weight: bold;" align="center"><a href="?reset=1"><img style="width: 100px; height: 100px; background-color: black;" src="logo.png"></a></div>
    <div class="uk-grid-match uk-grid-small uk-text-center" uk-grid>
      <div class="uk-width-1-3@m">
        <select id="save_type" class="uk-select" name="type">
          <option value="recent">Recent</option>
          <option value="home">Home</option>
          <option value="work">Work</option>
        </select>
      </div>
      <div class="uk-width-expand@m">
        <input class="uk-input" type="text" id="pac-input" name="keyword" placeholder="Search a place" onfocus='this.value=""'/>
      </div>
    </div>
    <div id="map"></div>
    <!-- Async script executes immediately and must be after any DOM elements used in callback. -->
    <script
      src="https://maps.googleapis.com/maps/api/js?key={{gmap_key}}&callback=initAutocomplete&libraries=places&v=weekly"
      async
    ></script>
  </body>
</html>