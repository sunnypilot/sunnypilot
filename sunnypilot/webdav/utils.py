from openpilot.common.params import Params


def get_webdav_config(params=None) -> tuple[bool, str | None, str | None, str | None, str | None]:
  """Get the WebDAV configuration.

  Returns a tuple of (is_enabled, endpoint, folder, username, password).
  """
  params = params or Params()
  is_enabled = params.get_bool("WebDAVEnabled")
  endpoint = params.get("WebDAVEndpoint")
  folder = params.get("WebDAVFolder")
  username = params.get("WebDAVUsername")
  password = params.get("WebDAVPassword")
  return is_enabled, endpoint, folder, username, password


def webdav_ready(params=None) -> bool:
  """Check if WebDAV uploading is ready.

  WebDAV is ready when it's enabled and has a valid endpoint configured.
  """
  params = params or Params()
  is_enabled, endpoint, _, _, _ = get_webdav_config(params)
  return is_enabled and endpoint is not None and len(endpoint) > 0


def use_webdav_uploader(params=None) -> bool:
  """Check if the device should use the WebDAV uploader.

  Returns True if WebDAV is ready and not on a metered connection.

  Note: This function is used by the process manager to determine whether to
  start the uploader process. The metered connection check here prevents the
  uploader from starting on metered connections. The uploader's main loop also
  respects metered status for ongoing uploads. This mirrors the behavior of the
  sunnylink uploader (see sunnylink/utils.py:use_sunnylink_uploader).
  """
  params = params or Params()
  return not params.get_bool("NetworkMetered") and webdav_ready(params)
