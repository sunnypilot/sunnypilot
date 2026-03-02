"""
BluePilot UI Constants and Layout Dimensions
Matches the Qt SidebarBP layout specifications
"""


class BPConstants:
  """BluePilot layout constants matching Qt implementation"""

  # Sidebar dimensions (wider than stock 300px)
  SIDEBAR_WIDTH = 460  # Cards: 280px + spacing + buttons

  # Card dimensions
  CARD_WIDTH = 280
  CARD_MARGIN = 30
  CARD_SPACING = 20
  CARD_RADIUS = 12

  # Network card
  NETWORK_CARD_HEIGHT = 140
  NETWORK_CARD_Y = 20

  # Metric card heights
  METRIC_CARD_COMPACT_HEIGHT = 130  # CPU, GPU, Memory cards
  METRIC_CARD_STANDARD_HEIGHT = 120  # Vehicle, Connect, SunnyLink

  # Signal bars
  SIGNAL_BAR_COUNT = 5
  SIGNAL_BAR_WIDTH = 10
  SIGNAL_BAR_SPACING = 5
  SIGNAL_BAR_MAX_HEIGHT = 35

  # Button dimensions
  BUTTON_SIZE = 100
  BUTTON_SPACING = 20
  BUTTON_MARGIN = 25
  BUTTON_RADIUS = 20

  # Fan icon (from Qt FAN_SIZE = 90)
  FAN_SIZE = 90

  # Font sizes
  FONT_SIZE_SMALL = 24
  FONT_SIZE_MEDIUM = 28
  FONT_SIZE_LARGE = 32
  FONT_SIZE_XLARGE = 36
  FONT_SIZE_HEADER = 40

  # Badge dimensions
  BADGE_HEIGHT = 58
  BADGE_MIN_WIDTH = 100
  BADGE_RADIUS = 12
  BADGE_ACCENT_WIDTH = 6

  # Header
  HEADER_HEIGHT = 80
  CONTENT_MARGIN = 40
  SPACING = 25
  RIGHT_COLUMN_WIDTH = 750

  # Offroad home
  REFRESH_INTERVAL = 10.0

  # Animation
  HOVER_ANIMATION_DURATION = 300  # ms
  FAN_ANIMATION_DURATION = 3000  # ms

  # Metrics refresh interval (frames)
  METRICS_REFRESH_INTERVAL = 10


# Carrier name mapping (for cellular network display)
CARRIER_MAP = {
  # US Carriers
  "310410": "AT&T", "310150": "AT&T", "310070": "AT&T",
  "310560": "AT&T", "310680": "AT&T", "310380": "AT&T", "311180": "AT&T",
  "310260": "T-Mobile", "310200": "T-Mobile", "310210": "T-Mobile",
  "310220": "T-Mobile", "310230": "T-Mobile", "310240": "T-Mobile",
  "310250": "T-Mobile", "310270": "T-Mobile", "310660": "T-Mobile",
  "310800": "T-Mobile", "311660": "T-Mobile", "311882": "T-Mobile", "312530": "T-Mobile",
  "311480": "Verizon", "311481": "Verizon", "311482": "Verizon",
  "311483": "Verizon", "311484": "Verizon", "311485": "Verizon",
  "311486": "Verizon", "311487": "Verizon", "311488": "Verizon", "311489": "Verizon",
  "310004": "Verizon", "310005": "Verizon", "310006": "Verizon",
  "310010": "Verizon", "310012": "Verizon", "310013": "Verizon",
  "310590": "Verizon", "310890": "Verizon", "310910": "Verizon",
  "311110": "Verizon", "311270": "Verizon",
  "310120": "Sprint", "312190": "Sprint", "311490": "Sprint",
  "311870": "Sprint", "311880": "Sprint",
  "312420": "US Cellular", "311580": "US Cellular",

  # Canadian Carriers
  "302220": "Telus", "302221": "Telus", "302860": "Telus",
  "302610": "Bell", "302640": "Bell", "302651": "Bell",
  "302720": "Rogers", "302721": "Rogers",

  # UK Carriers
  "23415": "Vodafone UK", "23410": "O2 UK",
  "23433": "EE", "23434": "EE", "23430": "EE", "23431": "EE", "23432": "EE",
  "23420": "Three UK",

  # European Carriers
  "26201": "Deutsche Telekom", "26202": "Vodafone DE", "26203": "O2 DE",
  "20801": "Orange FR", "20810": "SFR", "20820": "Bouygues", "20815": "Free Mobile",
  "22201": "TIM", "22210": "Vodafone IT", "22288": "Wind Tre",
  "21401": "Vodafone ES", "21403": "Orange ES", "21407": "Movistar",

  # Australian Carriers
  "50501": "Telstra", "50502": "Optus", "50503": "Vodafone AU",

  # Asian Carriers
  "44010": "NTT DoCoMo", "44020": "SoftBank", "44050": "KDDI",
  "46000": "China Mobile", "46001": "China Unicom", "46003": "China Telecom",
  "46697": "Taiwan Mobile", "46692": "Chunghwa", "46601": "Far EasTone",
  "45005": "SK Telecom", "45008": "KT", "45006": "LG U+",
  "52501": "Singtel", "52502": "Singtel", "52503": "StarHub",
  "52505": "StarHub", "52504": "M1",
  "51010": "Telkomsel", "51011": "XL Axiata", "51089": "Smartfren",
  "40401": "Vodafone India", "40402": "Airtel", "40403": "Airtel",
  "40410": "Airtel", "40411": "Vodafone India", "40420": "Airtel",
  "405840": "Jio", "405854": "Jio", "405855": "Jio", "405856": "Jio",
}


def get_carrier_name(operator_code: str) -> str:
  """Map carrier codes to human-readable names"""
  if not operator_code or not operator_code.strip():
    return "Cellular"
  return CARRIER_MAP.get(operator_code.strip(), "Cellular")
