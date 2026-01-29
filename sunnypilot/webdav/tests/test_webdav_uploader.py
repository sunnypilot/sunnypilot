"""
Tests for the WebDAV uploader functionality.
"""
from openpilot.common.params import Params
from openpilot.sunnypilot.webdav.utils import get_webdav_config, webdav_ready, use_webdav_uploader


class TestWebDAVUtils:
  """Test the WebDAV utility functions."""

  def setup_method(self):
    self.params = Params()
    # Clear all WebDAV params before each test
    self.params.remove("WebDAVEnabled")
    self.params.remove("WebDAVEndpoint")
    self.params.remove("WebDAVFolder")
    self.params.remove("WebDAVUsername")
    self.params.remove("WebDAVPassword")
    self.params.remove("NetworkMetered")

  def test_get_webdav_config_disabled(self):
    """Test that config returns disabled when WebDAVEnabled is not set."""
    self.params.put_bool("WebDAVEnabled", False)
    is_enabled, endpoint, folder, username, password = get_webdav_config(self.params)
    assert is_enabled is False
    assert endpoint is None
    assert folder is None
    assert username is None
    assert password is None

  def test_get_webdav_config_enabled_with_endpoint(self):
    """Test that config returns all fields when set."""
    self.params.put_bool("WebDAVEnabled", True)
    self.params.put("WebDAVEndpoint", "https://webdav.example.com/dav/")
    self.params.put("WebDAVFolder", "sunnypilot/drives")
    self.params.put("WebDAVUsername", "testuser")
    self.params.put("WebDAVPassword", "testpass")

    is_enabled, endpoint, folder, username, password = get_webdav_config(self.params)
    assert is_enabled is True
    assert endpoint == "https://webdav.example.com/dav/"
    assert folder == "sunnypilot/drives"
    assert username == "testuser"
    assert password == "testpass"

  def test_webdav_ready_returns_false_when_disabled(self):
    """Test that webdav_ready returns False when not enabled."""
    self.params.put_bool("WebDAVEnabled", False)
    self.params.put("WebDAVEndpoint", "https://webdav.example.com/dav/")
    assert webdav_ready(self.params) is False

  def test_webdav_ready_returns_false_when_no_endpoint(self):
    """Test that webdav_ready returns False when endpoint is not set."""
    self.params.put_bool("WebDAVEnabled", True)
    assert webdav_ready(self.params) is False

  def test_webdav_ready_returns_false_when_endpoint_empty(self):
    """Test that webdav_ready returns False when endpoint is empty."""
    self.params.put_bool("WebDAVEnabled", True)
    self.params.put("WebDAVEndpoint", "")
    assert webdav_ready(self.params) is False

  def test_webdav_ready_returns_true_when_properly_configured(self):
    """Test that webdav_ready returns True when properly configured."""
    self.params.put_bool("WebDAVEnabled", True)
    self.params.put("WebDAVEndpoint", "https://webdav.example.com/dav/")
    assert webdav_ready(self.params) is True

  def test_use_webdav_uploader_returns_false_on_metered(self):
    """Test that use_webdav_uploader returns False on metered connection."""
    self.params.put_bool("WebDAVEnabled", True)
    self.params.put("WebDAVEndpoint", "https://webdav.example.com/dav/")
    self.params.put_bool("NetworkMetered", True)
    assert use_webdav_uploader(self.params) is False

  def test_use_webdav_uploader_returns_false_when_not_ready(self):
    """Test that use_webdav_uploader returns False when not ready."""
    self.params.put_bool("WebDAVEnabled", False)
    self.params.put_bool("NetworkMetered", False)
    assert use_webdav_uploader(self.params) is False

  def test_use_webdav_uploader_returns_true_when_ready_and_unmetered(self):
    """Test that use_webdav_uploader returns True when ready and on unmetered connection."""
    self.params.put_bool("WebDAVEnabled", True)
    self.params.put("WebDAVEndpoint", "https://webdav.example.com/dav/")
    self.params.put_bool("NetworkMetered", False)
    assert use_webdav_uploader(self.params) is True


class TestWebDAVUploaderUnit:
  """Unit tests for WebDAVUploader class."""

  def setup_method(self):
    self.params = Params()
    self.params.put("DongleId", "test_dongle_id")
    self.params.put_bool("WebDAVEnabled", True)
    self.params.put("WebDAVEndpoint", "https://webdav.example.com/dav/")
    self.params.put("WebDAVFolder", "sunnypilot/drives")
    self.params.put("WebDAVUsername", "testuser")
    self.params.put("WebDAVPassword", "testpass")
    self.params.put_bool("NetworkMetered", False)

  def teardown_method(self):
    # Clear folder param so it doesn't affect other tests
    self.params.remove("WebDAVFolder")

  def test_uploader_init(self):
    """Test that the WebDAVUploader initializes correctly."""
    from openpilot.sunnypilot.webdav.uploader import WebDAVUploader

    uploader = WebDAVUploader("test_dongle_id", "/tmp/test_root")
    assert uploader.dongle_id == "test_dongle_id"
    assert uploader.root == "/tmp/test_root"

  def test_upload_path_with_folder(self, mocker):
    """Test that upload path includes folder when set."""
    from openpilot.sunnypilot.webdav.uploader import WebDAVUploader
    from openpilot.sunnypilot.webdav import uploader as uploader_module

    # Set the folder
    self.params.put("WebDAVFolder", "sunnypilot/drives")

    mock_response = mocker.MagicMock()
    mock_response.status_code = 201
    mock_response.request = mocker.MagicMock()
    mock_response.request.headers = {"Content-Length": "100"}

    mock_put = mocker.patch('openpilot.sunnypilot.webdav.uploader.requests.put', return_value=mock_response)
    mocker.patch('openpilot.sunnypilot.webdav.uploader.requests.request', return_value=mock_response)
    mocker.patch.object(uploader_module, 'get_upload_stream', return_value=(mocker.MagicMock(), 100))

    uploader = WebDAVUploader("test_dongle_id", "/tmp/test_root")
    uploader.do_upload("segment/qlog.zst", "/tmp/test_root/segment/qlog")

    # Check that the URL contains the folder path
    call_args = mock_put.call_args
    url = call_args[0][0]
    assert "sunnypilot/drives/test_dongle_id/segment/qlog.zst" in url

  def test_upload_path_without_folder(self, mocker):
    """Test that upload path works correctly when folder is not set."""
    from openpilot.sunnypilot.webdav.uploader import WebDAVUploader
    from openpilot.sunnypilot.webdav import uploader as uploader_module

    # Remove the folder
    self.params.remove("WebDAVFolder")

    mock_response = mocker.MagicMock()
    mock_response.status_code = 201
    mock_response.request = mocker.MagicMock()
    mock_response.request.headers = {"Content-Length": "100"}

    mock_put = mocker.patch('openpilot.sunnypilot.webdav.uploader.requests.put', return_value=mock_response)
    mocker.patch('openpilot.sunnypilot.webdav.uploader.requests.request', return_value=mock_response)
    mocker.patch.object(uploader_module, 'get_upload_stream', return_value=(mocker.MagicMock(), 100))

    uploader = WebDAVUploader("test_dongle_id", "/tmp/test_root")
    uploader.do_upload("segment/qlog.zst", "/tmp/test_root/segment/qlog")

    # Check that the URL doesn't have folder prefix, just dongle_id
    call_args = mock_put.call_args
    url = call_args[0][0]
    assert "test_dongle_id/segment/qlog.zst" in url
    assert "sunnypilot/drives" not in url

  def test_upload_path_with_empty_folder(self, mocker):
    """Test that upload path works correctly when folder is just slashes."""
    from openpilot.sunnypilot.webdav.uploader import WebDAVUploader
    from openpilot.sunnypilot.webdav import uploader as uploader_module

    # Set folder to just slashes (edge case)
    self.params.put("WebDAVFolder", "///")

    mock_response = mocker.MagicMock()
    mock_response.status_code = 201
    mock_response.request = mocker.MagicMock()
    mock_response.request.headers = {"Content-Length": "100"}

    mock_put = mocker.patch('openpilot.sunnypilot.webdav.uploader.requests.put', return_value=mock_response)
    mocker.patch('openpilot.sunnypilot.webdav.uploader.requests.request', return_value=mock_response)
    mocker.patch.object(uploader_module, 'get_upload_stream', return_value=(mocker.MagicMock(), 100))

    uploader = WebDAVUploader("test_dongle_id", "/tmp/test_root")
    uploader.do_upload("segment/qlog.zst", "/tmp/test_root/segment/qlog")

    # Check that the URL doesn't have leading slashes, just dongle_id
    call_args = mock_put.call_args
    url = call_args[0][0]
    assert "test_dongle_id/segment/qlog.zst" in url
    # Shouldn't start with // after the domain
    assert "dav//test_dongle_id" not in url

  def test_ensure_remote_directory(self, mocker):
    """Test that _ensure_remote_directory creates parent directories."""
    from openpilot.sunnypilot.webdav.uploader import WebDAVUploader

    mock_response = mocker.MagicMock()
    mock_response.status_code = 201
    mocker.patch('openpilot.sunnypilot.webdav.uploader.requests.request', return_value=mock_response)

    uploader = WebDAVUploader("test_dongle_id", "/tmp/test_root")
    result = uploader._ensure_remote_directory(
      "https://webdav.example.com/dav/",
      "sunnypilot/drives/dongle_id/segment_dir/file.log",
      ("user", "pass")
    )

    assert result is True
