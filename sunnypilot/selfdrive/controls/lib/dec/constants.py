class WMACConstants:
  # Lead detection parameters
  LEAD_WINDOW_SIZE = 6  # Stable detection window
  LEAD_PROB = 0.4  # Balanced threshold for lead detection

  # Slow down detection parameters
  SLOW_DOWN_WINDOW_SIZE = 5  # Responsive but stable
  SLOW_DOWN_PROB = 0.3  # Balanced threshold for slow down scenarios

  # Optimized slow down distance curve - smooth and progressive
  SLOW_DOWN_BP = [0., 10., 20., 30., 40., 50., 55., 60.]
  SLOW_DOWN_DIST = [32., 46., 64., 86., 108., 130., 145., 165.]

  # Slowness detection parameters
  SLOWNESS_WINDOW_SIZE = 15  # Stable slowness detection
  SLOWNESS_PROB = 0.65  # Clear threshold for slowness
  SLOWNESS_CRUISE_OFFSET = 1.025  # Conservative cruise speed offset
  SLOWNESS_DEFICIT_THRESHOLD = 0.25  # 25% below cruise speed to trigger
  SLOWNESS_MIN_SPEED = 30.0  # Minimum speed to consider slowness (km/h)

  # Lead detection parameters
  SLOW_LEAD_PROB = 0.6  # Probability for slow lead detection
  SLOW_LEAD_VREL_THRESHOLD = -1.785  # Relative velocity threshold
  SLOW_LEAD_SPEED_RATIO = 0.8  # Lead speed ratio compared to ours (80% of our speed)
  SLOW_LEAD_STOPPED_THRESHOLD = 1.0  # Speed threshold for stopped lead
  SLOW_LEAD_DISTANCE_THRESHOLD = 75.0  # Distance threshold for filtered detection
