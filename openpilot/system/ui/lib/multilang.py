from importlib.resources import files
import json
import os
import re
from openpilot.common.basedir import BASEDIR
from openpilot.common.swaglog import cloudlog

try:
  from openpilot.common.params import Params
except ImportError:
  Params = None

SYSTEM_UI_DIR = os.path.join(BASEDIR, "openpilot/system", "ui")
UI_DIR = files("openpilot.selfdrive.ui")
TRANSLATIONS_DIR = UI_DIR.joinpath("translations")
LANGUAGES_FILE = TRANSLATIONS_DIR.joinpath("languages.json")

UNIFONT_LANGUAGES = [
  "th",
  "zh-CHT",
  "zh-CHS",
  "ko",
  "ja",
]

C4_ZH_CHT_TRANSLATIONS = {
  "Advanced Settings": "進階設定",
  "VW: Blind Spot Driving Side": "VW：盲點系統駕駛側",
  "Left-Hand Drive": "左駕",
  "Right-Hand Drive": "右駕",
  "Speed Limit Display & Warning": "速限顯示與警告",
  "Off": "關閉",
  "driving personality": "駕駛風格",
  "aggressive": "積極",
  "standard": "標準",
  "relaxed": "舒適",
  "experimental mode": "實驗模式",
  "use metric units": "使用公制單位",
  "lane departure warnings": "車道偏離警示",
  "always-on driver monitor": "持續駕駛監控",
  "record & upload driver camera": "錄製並上傳\n駕駛監控影像",
  "record & upload mic audio": "錄製並上傳\n麥克風音訊",
  "enable sunnypilot": "啟用 sunnypilot",
  "VW: Lateral Correction (Recommended)": "VW：\n橫向修正（建議）",
  "Dark Mode": "深色模式",
  "Enable Accel Bar": "顯示加速度條",
  "SSH keys": "SSH 金鑰",
  "joystick debug mode": "搖桿控制測試模式",
  "longitudinal maneuver mode": "縱向操控測試模式",
  "lateral maneuver mode": "橫向操控測試模式",
  "alpha longitudinal": "Alpha 縱向控制",
  "ui debug mode": "UI 除錯模式",
  "Loading...": "載入中...",
  "Not set": "尚未設定",
  "Please connect to Wi-Fi to fetch your key.": "請連接 Wi-Fi 以取得金鑰。",
  "device ID": "裝置 ID",
  "serial": "序號",
  "target branch": "目標分支",
  "update sunnypilot": "更新 sunnypilot",
  "force download": "強制下載",
  "regulatory info": "法規資訊",
  "driver\ncamera preview": "駕駛監控鏡頭\n預覽",
  "review\ntraining guide": "檢視\n使用教學",
  "terms &\nconditions": "條款與\n細則",
  "subscribed": "已訂閱",
  "upgrade to prime": "升級至 Prime",
  "update now": "立即更新",
  "updater failed\nto respond": "更新程式\n沒有回應",
  "failed to update": "更新失敗",
  "download update": "下載更新",
  "up to date": "已是最新版本",
  "wi-fi": "Wi-Fi",
  "not connected": "未連線",
  "enable tethering": "啟用網路共享",
  "enable roaming": "允許數據漫遊",
  "tethering password": "網路共享密碼",
  "network usage": "網路用量設定",
  "apn settings": "APN 設定",
  "cellular metered": "行動網路計量付費",
  "edit": "編輯",
  "slide to forget": "滑動以移除此網路",
  "searching for networks": "正在搜尋網路",
  "forgetting...": "正在移除…",
  "not in range": "不在範圍內",
  "unsupported": "不支援",
  "start the car to\nuse sunnypilot": "發動車輛以\n使用 sunnypilot",
  "system booting": "系統啟動中",
  "openpilot can't start\ncheck alerts": "openpilot 無法啟動\n請查看警示",
  "pair with comma connect": "與 comma connect 配對",
  "cache size": "快取大小",
  "Vehicle in Left Blind Spot": "左側盲點有車輛",
  "Vehicle in Right Blind Spot": "右側盲點有車輛",
  "Vehicle in Blind Spot": "盲點有車輛",
}

# Plural form selectors for supported languages
PLURAL_SELECTORS = {
  'en': lambda n: 0 if n == 1 else 1,
  'de': lambda n: 0 if n == 1 else 1,
  'fr': lambda n: 0 if n <= 1 else 1,
  'pt-BR': lambda n: 0 if n == 1 else 1,
  'es': lambda n: 0 if n == 1 else 1,
  'tr': lambda n: 0 if n == 1 else 1,
  'uk': lambda n: 0 if n % 10 == 1 and n % 100 != 11 else (1 if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14 else 2),
  'th': lambda n: 0,
  'zh-CHT': lambda n: 0,
  'zh-CHS': lambda n: 0,
  'ko': lambda n: 0,
  'ja': lambda n: 0,
}


def _parse_quoted(s: str) -> str:
  """Parse a PO-format quoted string."""
  s = s.strip()
  if not (s.startswith('"') and s.endswith('"')):
    raise ValueError(f"Expected quoted string: {s!r}")
  s = s[1:-1]
  result: list[str] = []
  i = 0
  while i < len(s):
    if s[i] == '\\' and i + 1 < len(s):
      c = s[i + 1]
      if c == 'n':
        result.append('\n')
      elif c == 't':
        result.append('\t')
      elif c == '"':
        result.append('"')
      elif c == '\\':
        result.append('\\')
      else:
        result.append(s[i:i + 2])
      i += 2
    else:
      result.append(s[i])
      i += 1
  return ''.join(result)


def load_translations(path) -> tuple[dict[str, str], dict[str, list[str]]]:
  """Parse a .po file and return (translations, plurals) dicts.

  translations: msgid -> msgstr
  plurals: msgid -> [msgstr[0], msgstr[1], ...]
  """
  with path.open(encoding='utf-8') as f:
    lines = f.readlines()

  translations: dict[str, str] = {}
  plurals: dict[str, list[str]] = {}

  # Parser state
  msgid = msgid_plural = msgstr = ""
  msgstr_plurals: dict[int, str] = {}
  field: str | None = None
  plural_idx = 0

  def finish():
    nonlocal msgid, msgid_plural, msgstr, msgstr_plurals, field
    if msgid:  # skip header (empty msgid)
      if msgid_plural:
        max_idx = max(msgstr_plurals.keys()) if msgstr_plurals else 0
        plurals[msgid] = [msgstr_plurals.get(i, '') for i in range(max_idx + 1)]
      else:
        if msgstr:
          translations[msgid] = msgstr
    msgid = msgid_plural = msgstr = ""
    msgstr_plurals = {}
    field = None

  for raw in lines:
    line = raw.strip()

    if not line:
      finish()
      continue

    if line.startswith('#'):
      continue

    if line.startswith('msgid_plural '):
      msgid_plural = _parse_quoted(line[len('msgid_plural '):])
      field = 'msgid_plural'
      continue

    if line.startswith('msgid '):
      msgid = _parse_quoted(line[len('msgid '):])
      field = 'msgid'
      continue

    m = re.match(r'msgstr\[(\d+)]\s+(.*)', line)
    if m:
      plural_idx = int(m.group(1))
      msgstr_plurals[plural_idx] = _parse_quoted(m.group(2))
      field = 'msgstr_plural'
      continue

    if line.startswith('msgstr '):
      msgstr = _parse_quoted(line[len('msgstr '):])
      field = 'msgstr'
      continue

    if line.startswith('"'):
      val = _parse_quoted(line)
      if field == 'msgid':
        msgid += val
      elif field == 'msgid_plural':
        msgid_plural += val
      elif field == 'msgstr':
        msgstr += val
      elif field == 'msgstr_plural':
        msgstr_plurals[plural_idx] += val

  finish()
  return translations, plurals


class Multilang:
  def __init__(self):
    self._params = Params() if Params is not None else None
    self._language: str = "zh-CHT"
    self.languages: dict[str, str] = {}
    self.codes: dict[str, str] = {}
    self._translations: dict[str, str] = {}
    self._plurals: dict[str, list[str]] = {}
    self._plural_selector = PLURAL_SELECTORS.get('en', lambda n: 0)
    self._load_languages()

  @property
  def language(self) -> str:
    return self._language

  def requires_unifont(self) -> bool:
    """Certain languages require unifont to render their glyphs."""
    return self._language in UNIFONT_LANGUAGES

  def setup(self):
    try:
      po_path = TRANSLATIONS_DIR.joinpath(f'app_{self._language}.po')
      self._translations, self._plurals = load_translations(po_path)
      if self._language == "zh-CHT":
        self._translations.update(C4_ZH_CHT_TRANSLATIONS)
      self._plural_selector = PLURAL_SELECTORS.get(self._language, lambda n: 0)
      cloudlog.debug(f"Loaded translations for language: {self._language}")
    except FileNotFoundError:
      cloudlog.error(f"No translation file found for language: {self._language}, using default.")
      self._translations = {}
      self._plurals = {}

  def change_language(self, language_code: str) -> None:
    self._params.put("LanguageSetting", language_code, block=True)
    self._language = language_code
    self.setup()

  def tr(self, text: str) -> str:
    return self._translations.get(text, text) or text

  def trn(self, singular: str, plural: str, n: int) -> str:
    if singular in self._plurals:
      idx = self._plural_selector(n)
      forms = self._plurals[singular]
      if idx < len(forms) and forms[idx]:
        return forms[idx]
    return singular if n == 1 else plural

  def _load_languages(self):
    with LANGUAGES_FILE.open(encoding='utf-8') as f:
      self.languages = json.load(f)
    self.codes = {v: k for k, v in self.languages.items()}

    if self._params is not None:
      lang = str(self._params.get("LanguageSetting")).removeprefix("main_")
      if lang in self.codes:
        self._language = lang


multilang = Multilang()
multilang.setup()

tr, trn = multilang.tr, multilang.trn


# no-op marker for static strings translated later
def tr_noop(s: str) -> str:
  return s
