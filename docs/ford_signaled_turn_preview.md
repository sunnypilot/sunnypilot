# Signaled-turn preview trial

The installed option now also includes the independently tested geometry entry
candidate. See [stop continuity and geometry entry](ford_stop_geometry_entry.md)
for current behavior. The original action-only trial and evidence follow below.

The coordinated Ford controller can start a large intersection turn late even
when the model geometry already shows the turn. This opt-in trial uses geometry
as a timing cue for the existing action request. It does not replace the action
with path heading or lateral position.

## Selection

In sunnylink Ford settings, enable **Signaled-Turn Preview (Experimental)** with
**Selected-Action Path Tracking** and **Coordinated C0/C1 Steering** on, and
**Model Geometry Reference** off. Keep **Large-Turn Entry Assist** on to match the
offline candidate. Apply settings while offroad, then start a new onroad session.
The new parameter, `FordPscmTurnPreview`, defaults off. The existing turn-entry
assist remains a separate option. Turning the master selected-action option off
still selects upstream Ford control.

## Command change

`controlsd` samples heading change at 7 and 14 metres of cumulative model-path
distance, once per model message. The cue fades in above 5 degrees at 7 metres
and 20 degrees at 14 metres; both headings must have the same sign. Full weight
requires at least 10 and 30 degrees respectively. This uses path distance even
when forward X folds back during a turn.

The cue and original model timestamp travel in `carControlSP.fordTurnPreview`.
`card` adds at most 0.20 seconds of the existing filtered action-angle rate,
capped at 30 wheel degrees, to the trimmed inverse target. It requires exactly
one matching driver turn signal and both raw model action and filtered angle
request growing toward the turn. The original action, rate estimate, and trim
error remain unchanged. The existing inverse acceleration allowance, encoder,
CAN bounds, transmit observer, and optional post-encoder assist still apply.
C2 and C3 remain zero.

Missing, invalid, future or older-than-150-ms geometry removes this addition.
Lane changes, maneuver injection, driver steering input, or a fresh PSCM limit
of 2 or greater suppress it too. These cue failures do not invalidate the base
controller. New model array work stays out of the CAN loop. There are no new
subscriptions, logging frequencies, shared process changes, or correction
integrators.

## Offline evidence and limits

The frozen candidate's latest-route left entry first changed commands about
0.60 seconds earlier, but the reconstructed reference reached 90 degrees only
21 ms earlier. Another good left entry reached that reference 239 ms earlier.
The latest-route right entry retained identical packets. Those are estimates
from the older-firmware reconstruction, not measured wheel improvements.

Nine of ten bookmarked wobble windows retained identical packets. The remaining
window differed by at most 0.02 m C0 and 0.001 rad C1. Two camera-verified ordinary
lane-following sections retained identical packets with the matching-signal
gate. This does not establish unchanged behavior on all ordinary roads.

Retained command history can affect output after the signal/cue clears. In one
good unwind the reconstructed 30-degree crossing was 0.103 seconds later, with
the 5-degree crossing unchanged. Offline replay holds the measured wheel fixed;
it cannot establish stability, physical smoothness, or successful turn completion.

The installation checks exercise actual model messages, additive Cap'n Proto
transport, both process startup selectors, card's reader contract, and the real
Ford CAN packer. They compare full command histories with the retained candidate
when enabled and the prior controller when disabled. Route gaps reset only the
offline predictor; production timing-gap behavior is unchanged.

All 11 retained routes (18f, 190, 183, 185, 17c, 166, 16a, 172, 177, 175, 17a)
matched exactly in both configurations: 1,208,782 controller updates and 116,886
model messages. The installed helper's heading samples and action-trend signs
also matched the original offline extractor. The relevant controller,
integration, startup, and sunnylink suites passed 410 tests; lint and generated
settings consistency checks passed.

On the development Mac, the new cue helper's median/p99 update cost was
20.5/37.5 microseconds per new model message; cached calls were 0.125/0.25
microseconds. A 10,000-message Python allocation check retained 32 additional
bytes after warmup. These are local checks, not device realtime or whole-process
memory validation.
