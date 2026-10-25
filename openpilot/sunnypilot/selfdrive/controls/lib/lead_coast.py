import math


LEAD_COAST_RELEASE_RATIO = 0.9
LEAD_COAST_MIN_DISTANCE = 6.


def lead_allows_coasting(present: bool, distance: float, relative_speed: float, acceleration: float,
                         min_distance: float) -> bool:
  return not present or (distance >= min_distance and relative_speed >= -0.2 and acceleration >= -0.2)


class LeadCoastGap:
  """Keep each lead's entry headway fixed throughout an accepted idle request."""
  def __init__(self):
    self.time_gaps: tuple[float | None, ...] | None = None
    self.blocked = False

  @staticmethod
  def valid_saved_time_gaps(gaps) -> bool:
    return len(gaps) == 2 and all(math.isfinite(gap) and gap >= 0. for gap in gaps)

  @property
  def saved_time_gaps(self) -> list[float]:
    return [] if self.time_gaps is None else [gap if gap is not None else 0. for gap in self.time_gaps]

  def allows(self, leads, v_ego: float, min_distance: float) -> bool:
    if self.blocked or len(leads) != 2 or not math.isfinite(v_ego) or v_ego <= 0.:
      return False
    if self.time_gaps is None:
      return all(not present or (all(math.isfinite(value) for value in (distance, relative_speed, acceleration)) and
                                 lead_allows_coasting(present, distance, relative_speed, acceleration, min_distance))
                 for present, distance, relative_speed, acceleration in leads)
    return all(not present or (
      gap is not None and math.isfinite(distance) and math.isfinite(relative_speed) and math.isfinite(acceleration) and
      distance >= LEAD_COAST_MIN_DISTANCE and distance / v_ego > LEAD_COAST_RELEASE_RATIO * gap
    ) for (present, distance, relative_speed, acceleration), gap in zip(leads, self.time_gaps, strict=True))

  def update(self, requested: bool, leads, v_ego: float, min_distance: float,
             saved_time_gaps: list[float] | None = None) -> bool:
    if not requested:
      self.time_gaps = None
      self.blocked = False
      return False
    if saved_time_gaps is not None:
      if not self.valid_saved_time_gaps(saved_time_gaps):
        self.blocked = True
        return False
      self.time_gaps = tuple(gap if gap > 0. else None for gap in saved_time_gaps)
    if not self.allows(leads, v_ego, min_distance):
      self.blocked = True
      return False
    if self.time_gaps is None:
      self.time_gaps = tuple(distance / v_ego if present else None for present, distance, _, _ in leads)
    return True
