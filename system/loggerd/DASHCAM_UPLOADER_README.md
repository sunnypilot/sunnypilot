# Openpilot Dashcam Uploader

This directory contains background daemon scripts (`gdrive_uploader.py` and `rsync_uploader.py`) that run automatically in the background of openpilot. They sweep for new dashcam video files and diagnostic logs, seamlessly backing them up to either Google Drive or an Rsync/Unraid server whenever your device enters an off-road state and connects to Wi-Fi.

## How It Works

* **Zero-Interference:** The background sync managers tie directly into openpilot's native process manager. Depending on your configuration, they are fully completely suppressed while you are actively driving to ensure 100% of the device's CPU overhead is directed purely to the driving models.
* **Auto-Resumption:** The scripts parse the `.ts` and `.hevc` files iteratively. If a connection drops, it will quietly pick back up right where it was paused during its next 10-second sweep cycle. 
* **State Caching:** Uploaded files have a native Unix Extended Attribute applied (`user.gd_upload` or `user.rsync_upload`). You'll never redundantly upload the same clip twice.

---

## Google Drive Setup Guide

Since openpilot doesn't have a web browser on the Comma device natively, you need to acquire a Google Drive **Refresh Token**. This acts as a permanent offline passport that allows the daemon to back up its own files silently.

### 1. Generate Application Keys
1. Go to your [Google Cloud Console](https://console.cloud.google.com/) and create a new project.
2. In the Search bar, search for **Google Drive API** and enable it.
3. On the left sidebar, click **Credentials**. 
4. Click **Create Credentials** -> **OAuth client ID**. 
5. Select **Web application** as the "Application type".
6. Under **Authorized redirect URIs**, paste exactly: `https://developers.google.com/oauthplayground`
7. Click Create. You now have a `Client ID` and `Client secret`.

### 2. Generate Your Refresh Token
1. Go to [Google's OAuth 2.0 Playground](https://developers.google.com/oauthplayground/).
2. Click the **Gear icon** in the top right.
3. Check the box for **"Use your own OAuth credentials"** and drop your Client ID and Secret in.
4. On the left side list, scroll down to **Drive API v3**, open it, and select `https://www.googleapis.com/auth/drive.file`.
5. Click **Authorize APIs** and log into your account.
6. Click **Exchange authorization code for tokens**.
7. Copy the brand new **Refresh token**.

### 3. Setup the Comma
Open your UI networking settings or SSH into the device and update the `DashcamUploaderGDAuth` params block to visually match this exact JSON architecture:

```json
{
  "client_id": "YOUR_CLIENT_ID",
  "client_secret": "YOUR_CLIENT_SECRET",
  "refresh_token": "YOUR_REFRESH_TOKEN"
}
```

### 4. Customizing the Base Folder Configuration
If you enter a short, friendly name (like `Comma` or `Openpilot/Drives`) into the **Google Drive Folder ID** UI prompt, the daemon will automatically build that exact folder structure at the root of your Google Drive. 

*(If you prefer not to use friendly names, you can still paste a raw, 33-character Google Drive API Folder ID like `1ABC123xyz_456LMNOP` exactly as it appears in your browser's URL bar. The daemon will automatically detect the formatting and bypass the name resolver to use the exact directory you specified).* 

Regardless, the script will systematically sort 100% of your drives natively using your filesystem date/time structure inside of it!

### 5. Managing the Queue / Resetting Uploads
Because the daemon caches its progress, it will never upload the same video twice. If you accidentally delete a file on your Google Drive and need the Comma to push it back up, simply navigate to your Comma's screen, go to the Uploader settings, and press **Reset Upload Queue**. This instantly strips the hidden tags off your files unconditionally and places them right back at the front of the line!

### 6. Troubleshooting & Manual Execution
If nothing seems to be uploading and you suspect an authentication error, you can bypass the background process manager entirely and run the synchronizers directly in your terminal. This will immediately spit out any underlying server or token errors into your console for easy debugging:

**Test Google Drive Uploader:**
```bash
cd /data/openpilot && python3 system/loggerd/gdrive_uploader.py
```

**Test Rsync Uploader:**
```bash
cd /data/openpilot && python3 system/loggerd/rsync_uploader.py
```

---

## Bonus: Google Apps Auto-Delete CRON Script

Google Drive doesn't auto-purge old data natively. To keep your Google Drive from fully overflowing with daily Commutes, add this native script to Google Apps Script (`script.google.com`) and add an alarm clock "Trigger" to run it exactly once a day.

```javascript
function autoDeleteOldFolders() {
  // Put the ID of your main "comma" drive folder right here:
  var parentFolderId = 'YOUR_BASE_FOLDER_ID'; 
  
  // How many days of archives should be retained?
  var maxDaysOld = 14; 
  
  var cutoff = new Date();
  cutoff.setDate(cutoff.getDate() - maxDaysOld);
  
  // Search for old directories using Google's native SQL-esque query param 
  var query = "'" + parentFolderId + "' in parents and mimeType = 'application/vnd.google-apps.folder' and modifiedDate < '" + cutoff.toISOString() + "'";
  var oldFolders = DriveApp.searchFolders(query);
  
  var count = 0;
  while (oldFolders.hasNext()) {
    var folder = oldFolders.next();
    folder.setTrashed(true);
    count++;
  }
  
  console.log("Successfully trashed " + count + " old folders.");
}
```

---

## Rsync / Unraid Setup Guide

If you prefer pure local NAS storage overhead over Google Drive, select **Rsync** as the target provider.

The UI expects an Rsync target in the string format of `user@192.168.1.100:/mnt/user/Openpilot/`.
It also requires the raw text of a Private SSH Key pasted into the GUI window.

**Unraid Persistence Note:** 
Because Unraid wipes its OS files upon every reboot, you must manually inject the Comma's Public SSH Key block into Unraid's boot persistence layer so the Comma is permanently trusted.
Place the public key directly inside `/boot/config/ssh/root/authorized_keys` on your Unraid flash drive.
