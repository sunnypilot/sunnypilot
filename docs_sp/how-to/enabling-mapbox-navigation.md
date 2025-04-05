# :map: Enabling Mapbox navigation

Enabling Mapbox Navigation on sunnypilot enhances your driving experience by providing accurate maps and directions.

Following the instructions below, you will set up a free Mapbox account, generating your own access token, and 
configuring on your comma 3/3X. Next:

## 1. Create a free Mapbox account

Sign up for a free Mapbox account. Although a credit card is required for verification, you will not be charged for the
free tier.

## 2. Generate access token

!!! warning
    You won't be able to access the secret key after this window.

On the Dashboard, find the **Access Tokens** section and click `Create a Token`. Name it as you like and set 
the scopes to allow everything for both Public and Secret. Copy both keys.

## 3. Connect comma 3/3X to a network

Once rebooted, connect your comma 3/3X to a network with internet access and note the comma 3/3X’s IP address.

## 4. Configure keys

In a browser, navigate to `C3_IP:8082` (e.g., 192.168.1.69:8082). You should see the comma logo and an input field. 
Paste your Public token (pk.xx), press enter, paste your Secret key (sk.xx), and press enter again. This page lets 
you search for destinations.

## 5. Set Home and Work addresses

To set Home and Work addresses, search for a place, select Home/Work from the dropdown, and click Navigate. For 
other destinations, select Recent Places.

!!! warning
    Your comma 3/3X requires an active internet connection to download map data, generate directions, and update
    ETA. Once data is downloaded, offline use is possible, but updates (like new directions after a missed turn)
    won't occur.

!!! info
    At this time, it is not possible to search directly on the comma 3/3X.

!!! info
    Mapbox does not support alphanumeric addresses (e.g., W123N1234 Main St). There is currently no known
    workaround for this.

!!! tip
    If your comma 3/3X shows a "Map Loading" screen, a reboot via the UI should fix it.
    Connect the comma 3/3X to a network (i.e. your phone's hotspot) and use your phone browser to search for places.

    In the Navigation panel on the comma 3/3X, select Home, Work, and Recent Places without needing a browser 
    (assuming internet connection).
