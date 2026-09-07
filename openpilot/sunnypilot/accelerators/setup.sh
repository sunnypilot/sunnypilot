#!/usr/bin/env bash
# Boot-time hardware init for the accelerator backends, run from the launcher
# before manager starts. A backend that needs root uses sudo -n itself.
# Never fails the launch: a backend that cannot come up reports through
# unavailable_reason(), which becomes an offroad alert.
cd "$(dirname "$0")" || exit 0
for setup in */setup.sh; do
  [ -f "$setup" ] || continue
  bash "$setup" || echo "accelerators: ${setup%/setup.sh} setup failed" >&2
done
exit 0
