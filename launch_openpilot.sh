#!/usr/bin/env bash
python sunnypilot_dev_msync/seat_control_service.py --frequency 10 &
exec ./launch_chffrplus.sh
