from cereal import messaging, custom


if __name__ == "__main__":
  sm = messaging.SubMaster(["modelManagerSP"])
  while True:
    sm.update(500)
    if sm.updated:
      msg = sm["modelManagerSP"]
      for model in msg.selectedBundle.models:
        if model.downloadProgress.status == custom.ModelManagerSP.DownloadStatus.downloading:
          print("")
          print(f"{model.fileName}: {model.downloadProgress}")
          print("")
