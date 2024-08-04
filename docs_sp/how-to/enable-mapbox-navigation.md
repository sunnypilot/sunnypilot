---
title: 🗺 Enable Mapbox Navigation
---

Enabling Mapbox Navigation on your sunnypilot 🚗 enhances your driving experience by providing accurate maps and directions. Follow the steps below to set up and enjoy this feature:

### **🛠 Setup Steps**
1. **Create a Free Mapbox Account**:  
   Sign up for a free Mapbox account. Although a credit card is required for verification, you will not be charged for the free tier.

2. **Generate Access Tokens**:  
   On the Dashboard, find the **Access Tokens** section and click `Create a Token`. Name it as you like and set the scopes to allow everything for both Public and Secret. Copy both keys. ⚠️ **Remember**: You won't be able to access the secret key after this window.

3. **Enable Mapbox Navigation on C3**:  
   Go to `SP - Visuals` on your C3 and toggle `Enable Mapbox Navigation*`. Accept the reboot prompt.

4. **Connect C3 to Network**:  
   Once rebooted, connect your C3 to a network with internet access and note the C3’s IP address.

5. **Configure Keys**:  
   In a browser, navigate to `C3_IP:8082` (e.g., 192.168.1.69:8082). You should see the Comma logo and an input field. Paste your Public token (pk.xx), press enter, paste your Secret key (sk.xx), and press enter again. This page lets you search for destinations.

6. **Set Home and Work Addresses**:  
   To set Home and Work addresses, search for a place, select Home/Work from the dropdown, and click Navigate. For other destinations, select Recent Places.

7. **Search on C3**:  
   At this time, it is not possible to search directly on the C3.

:::tip **TIPS:**
- If your C3 shows a "Map Loading" screen, a reboot via the UI should fix it.
- Connect the C3 to your phone's hotspot and use your phone browser to search for places.
- In the Navigation panel on the C3, select Home, Work, and Recent Places without needing a browser (assuming internet connection).
  :::

:::warning **IMPORTANT NOTE:**
Your C3 requires an active internet connection to download map data, generate directions, and update ETA. Once data is downloaded, offline use is possible, but updates (like new directions after a missed turn) won't occur.
:::

:::info **NAVIGATION NOTE:**
Mapbox does not support alphanumeric addresses (e.g., W123N1234 Main St). There is currently no known workaround for this.
:::
