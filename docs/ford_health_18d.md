# Route 18d: memory growth and health-message stalls

Route: `84865544361f55cb/0000018d--edff60065e`, running clean
`07affcf9340623d759f31915477b5176d21c0b14`. Examined 37 uploaded qlogs.

## Observed faults

- `card` RSS rose from 68.7 MiB to 871.2 MiB over about 40 minutes.
  PSS also grew substantially, identifying retained process memory rather than
  just shared mappings. `controlsd` remained comparatively stable.
- Communication-error diagnostics identified `deviceState` as below frequency.
  A 4.005-second `gpu1-usr` temperature read coincided with a 4.436-second gap
  between health messages. A separate SOM power read took 1.577 seconds.

## Memory fix

The NumPy `ndpointer` argument conversion reaches `ctypes.cast`, which creates
cyclic pointer references. `card` disables cyclic garbage collection through
`config_realtime_process`. Consequently, every native encoder call retained
small allocations indefinitely.

Keep NumPy's dtype/contiguity validation, but construct an acyclic pointer that
owns the input array until the synchronous native call finishes. No forced GC,
controller equations, gains, candidate search, bounds, or packet changes.

The regression test reproduced 3,000 retained pointers in 500 ordinary encoder
updates and 5,500 with preview. Both now retain zero. Before the fix, an
encoder-only run grew by 51.0 MB in 12,000 updates. The fixed full controller
stayed near 72.3 MB for 300,000 updates with GC disabled (50 minutes of updates
at 100 Hz, executed faster than real time).

## Communication fault: separate work

The temperature and power reads above are in shared upstream `hardwared`, not
in the Ford controller. A tested background-reader candidate is preserved on
local branch `codex/ford-health-18d-sensor-candidate`. It is deliberately
excluded from this controller fix because it changes shared sensor sampling,
freshness handling and thermal behavior and needs its own review.

This fix does not claim to eliminate the observed health-message stalls.
Reducing memory pressure may help general resource pressure, but is not proof
that the blocking sensor I/O will stop.

## Validation

- 156 focused Ford tests passed, including native argument lifetime, preview,
  turn-entry assistance and the controller/transmit path.
- Nine frozen routes, 556,776 input samples: before/after C0/C1 and observer
  results match exactly, with entry assist both enabled and disabled.
- Ruff and whitespace checks passed.

Frozen replays establish unchanged commands, not a new claim about vehicle
tracking. The memory reproduction was local; on-device memory still needs
confirmation after updating. Other logged processes also used memory, so this
identifies and fixes the dominant confirmed leak rather than proving the whole
system cannot grow.
