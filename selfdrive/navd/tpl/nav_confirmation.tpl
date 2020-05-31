<div><img src="https://api.mapbox.com/styles/v1/mapbox/streets-v11/static/pin-s-l+000({{lon}},{{lat}})/{{lon}},{{lat}},14/300x300?access_token={{token}}" /></div>
<div style="padding: 5px; font-size: 10px;">{{addr}}</div>
<form name="navForm" method="post">
    <fieldset class="uk-fieldset">
        <div class="uk-margin">
          <input type="hidden" name="name" value="{{addr}}">
          <input type="hidden" name="lat" value="{{lat}}">
          <input type="hidden" name="lon" value="{{lon}}">
          <select id="save_type" name="save_type" class="uk-select">
            <option value="recent">Recent</option>
            <option value="home">Home</option>
            <option value="work">Work</option>
          </select>
          <input class="uk-button uk-button-primary uk-width-1-1 uk-margin-small-bottom" type="submit" value="Start Navigation">
        </div>
    </fieldset>
</form>