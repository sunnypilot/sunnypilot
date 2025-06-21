class WMACConstants:
  # Lead detection parameters
  LEAD_WINDOW_SIZE = 7  # Stable detection window
  LEAD_PROB = 0.45  # Balanced threshold for lead detection

  # Slow down detection parameters
  SLOW_DOWN_WINDOW_SIZE = 5  # Responsive but stable
  SLOW_DOWN_PROB = 0.3  # Balanced threshold for slow down scenarios

  # Optimized slow down distance curve - smooth and progressive
  SLOW_DOWN_BP = [0., 10., 20., 30., 40., 50., 55., 60.]
  SLOW_DOWN_DIST = [32., 46., 64., 86., 108., 130., 145., 165.]
  #SLOW_DOWN_DIST = [28., 42., 58., 78., 98., 118., 133., 153.]
  #SLOW_DOWN_DIST = [25., 38., 55., 75., 95., 115., 130., 150.]
  #SLOW_DOWN_DIST = [30., 45., 60., 80., 100., 120., 135., 150.]
  #SLOW_DOWN_DIST = [35., 50., 65., 85., 105., 125., 140., 155.]
  #SLOW_DOWN_BP = [0., 10., 20., 30., 40., 50., 60., 70., 80.]
  #SLOW_DOWN_DIST = [28., 40., 56., 74., 94., 116., 140., 166., 194.]

  # Slowness detection parameters
  SLOWNESS_WINDOW_SIZE = 10  # Stable slowness detection
  SLOWNESS_PROB = 0.55  # Clear threshold for slowness
  SLOWNESS_CRUISE_OFFSET = 1.025  # Conservative cruise speed offset
