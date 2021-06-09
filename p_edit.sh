#!/usr/bin/bash

export LD_LIBRARY_PATH=/data/data/com.termux/files/usr/lib
export HOME=/data/data/com.termux/files/home
export PATH=/usr/local/bin:/data/data/com.termux/files/usr/bin:/data/data/com.termux/files/usr/sbin:/data/data/com.termux/files/usr/bin/applets:/bin:/sbin:/vendor/bin:/system/sbin:/system/bin:/system/xbin:/data/data/com.termux/files/usr/bin/python
export PYTHONPATH=/data/openpilot

cd /data/openpilot
MAX_STEER=`cat /data/params/d/MaxSteer`
MAX_RT_DELTA=`cat /data/params/d/MaxRTDelta`
MAX_RATE_UP=`cat /data/params/d/MaxRateUp`
MAX_RATE_DOWN=`cat /data/params/d/MaxRateDown`
sed -i "1s/.*/const int HYUNDAI_MAX_STEER \= ${MAX_STEER}\;             \/\/ like stock/g" /data/openpilot/panda/board/safety/safety_hyundai.h
sed -i "2s/.*/const int HYUNDAI_MAX_RT_DELTA \= ${MAX_RT_DELTA}\;          \/\/ max delta torque allowed for real time checks/g" /data/openpilot/panda/board/safety/safety_hyundai.h
sed -i "4s/.*/const int HYUNDAI_MAX_RATE_UP \= ${MAX_RATE_UP}\;/g" /data/openpilot/panda/board/safety/safety_hyundai.h
sed -i "5s/.*/const int HYUNDAI_MAX_RATE_DOWN \= ${MAX_RATE_DOWN}\;/g" /data/openpilot/panda/board/safety/safety_hyundai.h
reboot