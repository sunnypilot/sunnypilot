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
            <option value="home">Set Home</option>
            <option value="work">Set Work</option>
            <option value="fav1">Set Favorite 1</option>
            <option value="fav2">Set Favorite 2</option>
            <option value="fav3">Set Favorite 3</option>
          </select>
          <input class="uk-button uk-button-primary uk-width-1-1 uk-margin-small-bottom" type="submit" value="Start Navigation">
        </div>
    </fieldset>
</form>
