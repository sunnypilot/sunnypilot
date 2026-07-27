"""Infer MHP (mixture-density-hypothesis) parameter values from output slice sizes.

The legacy supercombo encoded its outputs using fixed values for
``PLAN_MHP_N``, ``PLAN_MHP_SELECTION``, ``LEAD_MHP_N``, and ``LEAD_MHP_SELECTION``.
Newer supercombo architectures emit differently-sized slices for the same heads,
yet the parser downstream still expects to be told the layout.

This module figures those numbers out at runtime from the model's output slice,
so the existing ``parse_mdn`` path can handle any supercombo flavor without code
changes for each variant. ``infer_mhp`` always tries the legacy values first so
existing compiled pkls behave identically (full backwards compatibility).

Schema reminder (``parse_mdn`` packs hypotheses contiguously in the order
``in_N × (mu | std | weights)`` along the channel axis):

    slice_size == in_N × (2·n_values + out_N)

where ``n_values`` is the per-hypothesis value width (``IDX_N × PLAN_WIDTH``
for plan, ``LEAD_TRAJ_LEN × LEAD_WIDTH`` for lead, etc.).
"""

def infer_mhp(
  slice_size: int,
  n_values: int,
  legacy_in_n: int,
  legacy_out_n: int,
  max_in_n: int = 16,
) -> tuple[int, int]:
  """Infer ``(in_N, out_N)`` for an MDN-encoded output slice.

  Tries values in this order, returning on the first match:

  1. ``(legacy_in_n, legacy_out_n)`` exactly — preserves exact backwards
     compatibility for existing supercombo pkls.
  2. ``out_N ∈ (0, 1, 3)`` (no weights, single weight, three-way selection) at
     increasing in_N — covers the common architectural patterns.
  3. Brute-force any valid ``out_N`` that divides ``slice_size``.

  Args:
    slice_size: Number of floats in the output slice (typically
      ``slices[name].stop - slices[name].start``).
    n_values: Per-hypothesis mu/std width (e.g. ``IDX_N × PLAN_WIDTH`` for plan).
    legacy_in_n: The legacy in_N value (highest priority for backwards compat).
    legacy_out_n: The legacy out_N value.
    max_in_n: Upper bound on accepted hypothesis counts (filters silly parses).

  Returns:
    ``(in_N, out_N)``. If nothing fits the formulas, returns ``(1, 0)`` —
    single hypothesis with no weights — which is the gentlest fallback.
  """
  if slice_size <= 0 or n_values <= 0:
    return 1, 0

  # Priority 1: exact legacy match (BC-preserving).
  per_hyp_legacy = 2 * n_values + legacy_out_n
  if per_hyp_legacy > 0 and legacy_in_n * per_hyp_legacy == slice_size:
    return legacy_in_n, legacy_out_n

  # Priority 2: common weight layouts across supercombo variants.
  for out_n in (0, 1, 3):
    per_hyp = 2 * n_values + out_n
    if per_hyp <= 0:
      continue
    if slice_size % per_hyp == 0:
      in_n = slice_size // per_hyp
      if 1 <= in_n <= max_in_n:
        return in_n, out_n

  # Priority 3: brute-force any divisor that yields a sensible in_N.
  # Bound out_n by max_in_n to keep the search tiny (3 hypotheses
  # of weights is already a lot).
  for out_n in range(0, max_in_n + 1):
    per_hyp = 2 * n_values + out_n
    if per_hyp <= 0:
      continue
    if slice_size % per_hyp == 0:
      in_n = slice_size // per_hyp
      if 1 <= in_n <= max_in_n:
        return in_n, out_n

  # Last resort: best-effort single hypothesis with no weights.
  return 1, 0


def slice_size(sl) -> int:
  """Return the float-width of a ``slice``/``None`` from ``output_slices``.

  ``None`` and ``slice(None, None, None)`` are treated as 0 (output absent).
  Negative-end slices (ONNX-style "from end") aren't supported by this helper
  because parser expects single-tensor packed outputs.
  """
  if sl is None:
    return 0
  start = 0 if sl.start is None else sl.start
  stop = sl.stop
  if stop is None or stop < 0:
    return 0
  return max(0, stop - start)


def infer_mhp_for_outputs(
  output_slices: dict,
  constants,
  max_in_n: int = 16,
) -> dict:
  """Build a dict of MHP values keyed by head name from a model's output_slices.

  Reads ``output_slices['plan']`` and ``output_slices['lead']`` (if present)
  and infers their ``in_N``/``out_N``. Other heads aren't MDN-encoded the same
  way and remain driven by the ``constants`` module.
  """
  config: dict[str, int] = {}

  plan_size = slice_size(output_slices.get('plan'))
  if plan_size > 0:
    n = constants.IDX_N * constants.PLAN_WIDTH
    in_n, out_n = infer_mhp(plan_size, n, constants.PLAN_MHP_N, constants.PLAN_MHP_SELECTION, max_in_n)
    config['plan_mhp_n'] = in_n
    config['plan_mhp_selection'] = out_n

  lead_size = slice_size(output_slices.get('lead'))
  if lead_size > 0:
    n = constants.LEAD_TRAJ_LEN * constants.LEAD_WIDTH
    in_n, out_n = infer_mhp(lead_size, n, constants.LEAD_MHP_N, constants.LEAD_MHP_SELECTION, max_in_n)
    config['lead_mhp_n'] = in_n
    config['lead_mhp_selection'] = out_n

  return config
