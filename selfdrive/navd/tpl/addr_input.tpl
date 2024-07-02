<form name="searchForm" method="post">
    <fieldset class="uk-fieldset">
        <div class="uk-margin">
            <select class="uk-select" name="fav_val">
                <option value="favorites">Select Saved Destinations</option>
                <option value="home">Home</option>
                <option value="work">Work</option>
                <option value="fav1">Favorite 1</option>
                <option value="fav2">Favorite 2</option>
                <option value="fav3">Favorite 3</option>
            <div style="padding: 5px; color: red; font-weight: bold;" align="center">{{msg}}</div>
            <input class="uk-input" type="text" name="addr_val" placeholder="Search a place">
            <input class="uk-button uk-button-primary uk-width-1-1 uk-margin-small-bottom" type="submit" value="Search">
        </div>
    </fieldset>
</form>
