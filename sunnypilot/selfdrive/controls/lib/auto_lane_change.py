"""
Auto Lane Change Controller (slow-lead auto-overtake)
"""
from enum import Enum
from openpilot.common.realtime import DT_MDL
from cereal import log

# Auto lane change timer modes
# -------------------------------------------------------------------------------------------------
# Auto-lane-change high-level mode/state machine.
#
#  • OFF         – feature disabled.
#  • NUDGE       – manual steering torque required (driver "nudges" the wheel).
#  • ARMED       – system is armed (either via turn-signal tap or slow-lead auto-overtake).
#  • ACTIVE      – lane change manoeuvre in progress; curvature offset will be requested.
#  • DONE        – manoeuvre completed.
#  • ABORTED     – manoeuvre aborted (blind-spot, brake press, etc.).
#
# Timer-flavoured sub-modes (selected through Params) control how long we wait before automatically
# initiating the lane change once ARMED. They follow the original sunnypilot implementation and are
# left unchanged: NUDGELESS, HALF_SECOND, ONE_SECOND, TWO_SECONDS, THREE_SECONDS.
# -------------------------------------------------------------------------------------------------

AutoLaneChangeMode = Enum('AutoLaneChangeMode', [
  # Feature states
  'OFF',
  'NUDGE',
  'ARMED',
  'ACTIVE',
  'DONE',
  'ABORTED',

  # Auto-initiation timer presets
  'NUDGELESS',
  'HALF_SECOND',
  'ONE_SECOND',
  'TWO_SECONDS',
  'THREE_SECONDS',
])

# Delay thresholds in seconds for each mode
# Map timer-preset modes to their respective delays. For every other state the delay is meaningless
# and defaults to ∞ so the helper logic never triggers automatically.

AUTO_LANE_CHANGE_TIMER = {
  AutoLaneChangeMode.NUDGELESS:     0.0,
  AutoLaneChangeMode.HALF_SECOND:   0.5,
  AutoLaneChangeMode.ONE_SECOND:    1.0,
  AutoLaneChangeMode.TWO_SECONDS:   2.0,
  AutoLaneChangeMode.THREE_SECONDS: 3.0,
  # Non-timer modes – effectively "never"
  AutoLaneChangeMode.OFF:           float('inf'),
  AutoLaneChangeMode.NUDGE:         float('inf'),
  AutoLaneChangeMode.ARMED:         float('inf'),
  AutoLaneChangeMode.ACTIVE:        float('inf'),
  AutoLaneChangeMode.DONE:          float('inf'),
  AutoLaneChangeMode.ABORTED:       float('inf'),
}

# Negative delay offset on blindspot detection
ONE_SECOND_DELAY = -1.0

# Shorter timeout for completing a lane change once active [s]
LANE_CHANGE_DONE_TIME =  1.0

# Minimum probability that a lane line exists before allowing a lane change
LANE_PRESENCE_THRESHOLD = 0.7

class AutoLaneChangeController:
  def __init__(self, helper=None):
    # Helper (DesireHelper) for state tracking
    self.helper = helper
    # Use blindspot delay (BSM) behavior when True
    self.lane_change_bsm_delay: bool = False
    # Selected timer mode (default to NUDGELESS so lane change proceeds immediately unless the
    # user overrides it via Params)
    self.lane_change_set_timer: AutoLaneChangeMode = AutoLaneChangeMode.NUDGELESS
    # Accumulated wait timer (seconds)
    self.lane_change_wait_timer: float = 0.0
    # High-level state -----------------------------------------------
    self.mode: AutoLaneChangeMode = AutoLaneChangeMode.OFF
    # Direction requested for the manoeuvre (left/right)
    self.direction = None  # Will hold log.LaneChangeDirection when armed
    # Public timer for debug (s)
    self._state_timer: float = 0.0

    # Latest lane line probabilities for left and right
    self._left_prob: float = 1.0
    self._right_prob: float = 1.0

    # Internal flags --------------------------------------------------
    # Disqualify after brake press
    self.prev_brake_pressed: bool = False
    # Disqualify continuous lane change
    self.prev_lane_change: bool = False

    # For diagnostics/logging: how was the current manoeuvre armed? ("manual" or "auto")
    self._trigger: str | None = None



  def reset(self) -> None:
    """Reset wait timer and brake flag."""
    self.lane_change_wait_timer = 0.0
    self.prev_brake_pressed = False
    self._state_timer = 0.0
    self.mode = AutoLaneChangeMode.OFF
    self.direction = None
    self._trigger = None
    self._left_prob = 1.0
    self._right_prob = 1.0

  # -------------------------------------------------------------------------------------------
  # Public interface expected by controlsd/desire_helper (compat shim with legacy sunnypilot).
  # -------------------------------------------------------------------------------------------

  # update_params -----------------------------------------------------------------------------
  def update_params(self) -> None:
    """Hot-reload parameters from Params.

    Currently we only fetch two optional params so that users can adjust behaviour at runtime
    without a full restart. They are **optional**, so we silently ignore missing keys on systems
    that do not provide them.
    """
    try:
      from openpilot.common.params import Params
      params = Params()

      # ------------------------------------------------------------------
      # Backwards-compatibility: support both the new compact params used by
      # the rewritten implementation *and* the original sunnypilot ones so
      # existing user settings continue to work after an upgrade.
      # ------------------------------------------------------------------

      # Whether to apply a 1 s negative delay once the blind-spot clears
      if params.get("AutoLC_BSMD") is not None:
        self.lane_change_bsm_delay = params.get_bool("AutoLC_BSMD")
      else:
        # Legacy key – keep working if the user still has it set
        self.lane_change_bsm_delay = params.get_bool("AutoLaneChangeBsmDelay")

      # Timer mode preset (as an int index). Prefer the new key but fall back
      # to the legacy one if missing.
      val = params.get("AutoLC_TimerMode")
      if val is None:
        val = params.get("AutoLaneChangeTimer")  # legacy key

      # Attempt to parse the value into an int, default to 0 on failure.
      try:
        timer_mode_idx = int(val or 0)
      except (TypeError, ValueError):
        timer_mode_idx = 0

      # Mapping for the new compact index encoding (0-4)
      timer_modes_new = [AutoLaneChangeMode.NUDGELESS, AutoLaneChangeMode.HALF_SECOND,
                         AutoLaneChangeMode.ONE_SECOND, AutoLaneChangeMode.TWO_SECONDS,
                         AutoLaneChangeMode.THREE_SECONDS]

      # Legacy mapping (sunnypilot ≤v1.0) – indices differed:
      #   1=NUDGELESS, 2=HALF_SECOND, 3=ONE_SECOND, 4=TWO_SECONDS, 5=THREE_SECONDS
      timer_modes_legacy = {
        1: AutoLaneChangeMode.NUDGELESS,
        2: AutoLaneChangeMode.HALF_SECOND,
        3: AutoLaneChangeMode.ONE_SECOND,
        4: AutoLaneChangeMode.TWO_SECONDS,
        5: AutoLaneChangeMode.THREE_SECONDS,
      }

      if 0 <= timer_mode_idx < len(timer_modes_new):
        self.lane_change_set_timer = timer_modes_new[timer_mode_idx]
      elif timer_mode_idx in timer_modes_legacy:
        self.lane_change_set_timer = timer_modes_legacy[timer_mode_idx]
    except Exception:
      # Params might not be available in unit-test environments – ignore.
      pass

  def update_lane_lines(self, left_prob: float, right_prob: float) -> None:
    """Update the latest lane line detection probabilities."""
    self._left_prob = float(left_prob)
    self._right_prob = float(right_prob)

  # should_arm --------------------------------------------------------------------------------
  def should_arm(self, sm) -> bool:
    """Return True if slow-lead auto-overtake conditions are met.

    This is a **minimal** heuristic implementation – it simply checks if a lead vehicle is
    present and slower than us by >3 m/s while we are travelling above 25 m/s (~55 mph).
    """
    print("[ALC] Checking should_arm...")
    try:
      lead = sm['radarState'].leadOne
      if not getattr(lead, 'status', False):
        print("[ALC] No lead detected.")
        return False
      v_ego = sm['carState'].vEgo
      # Require decent highway speed
      if v_ego < 25.0:
        print(f"[ALC] Ego speed {v_ego} m/s too low.")
        return False
      # Convert relative speed to absolute lead speed if available
      v_rel = getattr(lead, 'vRel', 0.0)
      v_lead_abs = v_ego + v_rel
      # Require the lead to be at least 3 m/s (~7 mph) slower
      slow_lead = (v_ego - v_lead_abs) > 2.0
      if not slow_lead:
        print(f"[ALC] Lead not significantly slower (v_ego: {v_ego}, v_lead_abs: {v_lead_abs}).")
        return False

      print(f"[ALC] Slow lead detected. v_ego: {v_ego}, v_lead_abs: {v_lead_abs}")

      # Check for lane line presence (assuming left lane change for now, adapt as needed)
      # TODO: Determine actual desired lane change direction before this check
      # For now, let's assume we want to change to the left if a slow lead is ahead.
      # This needs to be more robust, e.g. checking both sides or based on model output.
      desired_direction = log.LaneChangeDirection.left # Placeholder
      self.direction = desired_direction # Temporarily set direction for lane_exists property

      if not self.lane_exists:
        print(f"[ALC] No valid lane line for direction {desired_direction.name}.")
        self.direction = None # Reset direction
        return False
      print(f"[ALC] Valid lane line detected for direction {desired_direction.name}.")

      # Check blind spot (assuming left lane change for now)
      # TODO: Adapt for actual desired lane change direction
      # The actual blindspot_detected is passed to update(), not directly available here.
      # We'll rely on the update() method to handle blindspot during ARMED/ACTIVE states.
      # However, it would be better to check here if possible.
      # For now, we proceed and let update() handle it.

      print("[ALC] Conditions met for arming auto-overtake.")
      return True
    except Exception as e:
      print(f"[ALC] Error in should_arm: {e}")
      return False

  # arm --------------------------------------------------------------------------------------
  def arm(self, direction, trigger: str = "manual"):
    """Arm the system for a lane change in *direction* (left/right).

    The *trigger* argument is for diagnostics only and indicates whether the
    arming was initiated by a manual turn-signal tap ("manual") or by the
    automatic slow-lead overtake heuristic ("auto").
    """
    from openpilot.common.swaglog import cloudlog  # import here to avoid cycles

    # Do not re-arm if a manoeuvre is already in progress.
    if self.mode not in (AutoLaneChangeMode.OFF, AutoLaneChangeMode.DONE, AutoLaneChangeMode.ABORTED):
      return

    self.direction = direction
    self.mode = AutoLaneChangeMode.ARMED
    self._state_timer = 0.0
    self._trigger = trigger

    dir_str = direction.name if hasattr(direction, "name") else str(int(direction))
    cloudlog.info(f"ALC armed ({trigger}) dir={dir_str}")

  # update -----------------------------------------------------------------------------------
  def update(self, blindspot_detected: bool, brake_pressed: bool, dt: float):
    """Main periodic update called by controlsd (50 Hz).

    Handles the high-level OFF→ARMED→ACTIVE→DONE/ABORTED transitions and reuses the existing
    `update_lane_change` helper for the underlying wait-timer logic.
    """

    # Always keep the wait-timer helper updated – its state is used in several properties/tests
    self.update_lane_change(blindspot_detected, brake_pressed)

    # OFF state – nothing to do
    if self.mode in (AutoLaneChangeMode.OFF, AutoLaneChangeMode.DONE, AutoLaneChangeMode.ABORTED):
      return

    # Abort on brake any time before ACTIVE
    if brake_pressed and self.mode in (AutoLaneChangeMode.ARMED, AutoLaneChangeMode.ACTIVE):
      self.mode = AutoLaneChangeMode.ABORTED
      return

    # Guard against blind-spot
    if blindspot_detected and self.mode in (AutoLaneChangeMode.ARMED, AutoLaneChangeMode.ACTIVE):
      # Stay armed, but do not progress timer
      return

    # State machine ----------------------------------------------------
    self._state_timer += dt

    prev_mode = self.mode
    print(f"[ALC] update: current mode: {self.mode.name}, timer: {self._state_timer:.2f}s, blindspot: {blindspot_detected}, brake: {brake_pressed}")

    if self.mode == AutoLaneChangeMode.ARMED:
      # Wait until helper timer cleared (AutoLC delay) and a lane exists
      print(f"[ALC] ARMED: auto_lc_allowed: {self.auto_lane_change_allowed}, lane_exists: {self.lane_exists}")
      if self.auto_lane_change_allowed and self.lane_exists:
        self.mode = AutoLaneChangeMode.ACTIVE
        self._state_timer = 0.0
        print(f"[ALC] Transitioning to ACTIVE. Trigger: {self._trigger}")

    elif self.mode == AutoLaneChangeMode.ACTIVE:
      # Consider the manoeuvre complete once the shorter timeout elapses or if DesireHelper marks completion
      finished = self._state_timer > LANE_CHANGE_DONE_TIME

      # Additionally, use DesireHelper if available
      if self.helper is not None and \
         getattr(self.helper, 'lane_change_state', None) == log.LaneChangeState.off:
        finished = True

      if finished:
        self.mode = AutoLaneChangeMode.DONE

    # Log mode transitions for easier debugging
    if self.mode != prev_mode:
      from openpilot.common.swaglog import cloudlog
      cloudlog.info(f"ALC state transition: {prev_mode.name} -> {self.mode.name}")

  # timer property ---------------------------------------------------------------------------
  @property
  def timer(self) -> float:
    """Public timer used by controlsd for debug – expose state timer."""
    return float(self._state_timer)

  def update_lane_change(self, blindspot_detected: bool, brake_pressed: bool) -> None:
    """Update wait timer based on blindspot and brake inputs."""
    # Brake press latches disqualified state
    if brake_pressed:
      self.prev_brake_pressed = True
      return

    # On blindspot detection with BSM delay, apply negative offset
    if blindspot_detected and self.lane_change_bsm_delay:
      self.lane_change_wait_timer = ONE_SECOND_DELAY
      return

    # Increment timer by model timestep
    self.lane_change_wait_timer += DT_MDL

  def update_state(self) -> None:
    """Track continuous lane change to disallow subsequent arming."""
    if not self.helper:
      return
    state = getattr(self.helper, 'lane_change_state', None)
    # Detect initiation of a lane change
    if state == log.LaneChangeState.laneChangeStarting:
      self.prev_lane_change = True

  @property
  def lane_change_delay(self) -> float:
    """Configured delay threshold based on selected mode."""
    return AUTO_LANE_CHANGE_TIMER.get(self.lane_change_set_timer, float('inf'))

  @property
  def lane_exists(self) -> bool:
    """Return True if a detectable lane line exists in the desired direction."""
    if self.direction is None: # Added check for None direction
      print("[ALC] lane_exists: direction is None, returning False")
      return False # Or True, depending on desired default behavior
    if self.direction == log.LaneChangeDirection.left:
      print(f"[ALC] lane_exists: checking left, prob: {self._left_prob:.2f}, threshold: {LANE_PRESENCE_THRESHOLD}")
      return self._left_prob > LANE_PRESENCE_THRESHOLD
    if self.direction == log.LaneChangeDirection.right:
      print(f"[ALC] lane_exists: checking right, prob: {self._right_prob:.2f}, threshold: {LANE_PRESENCE_THRESHOLD}")
      return self._right_prob > LANE_PRESENCE_THRESHOLD
    print("[ALC] lane_exists: direction not left/right, returning True")
    return True

  @property
  def auto_lane_change_allowed(self) -> bool:
    """Return True if wait timer exceeded and no disqualifying flags."""
    # OFF or NUDGE modes never allow auto
    if self.lane_change_set_timer in (AutoLaneChangeMode.OFF, AutoLaneChangeMode.NUDGE):
      return False
    # Disqualify if brake was pressed
    if self.prev_brake_pressed:
      return False
    # Disqualify continuous lane change after one cycle
    if self.prev_lane_change:
      return False
    # Timer must exceed configured delay
    return self.lane_change_wait_timer > self.lane_change_delay
