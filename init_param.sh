#!/usr/bin/bash

export LD_LIBRARY_PATH=/data/data/com.termux/files/usr/lib
export HOME=/data/data/com.termux/files/home
export PATH=/usr/local/bin:/data/data/com.termux/files/usr/bin:/data/data/com.termux/files/usr/sbin:/data/data/com.termux/files/usr/bin/applets:/bin:/sbin:/vendor/bin:/system/sbin:/system/bin:/system/xbin:/data/data/com.termux/files/usr/bin/python
export PYTHONPATH=/data/openpilot

cd /data/openpilot

/data/data/com.termux/files/usr/bin/cat /data/openpilot/param_init_value | while read line
do
ParamName=$(/data/data/com.termux/files/usr/bin/echo $line | /data/data/com.termux/files/usr/bin/applets/awk -F ':' '{print $1}')
ParamValue=$(/data/data/com.termux/files/usr/bin/echo $line | /data/data/com.termux/files/usr/bin/applets/awk -F ':' '{print $2}')
/data/data/com.termux/files/usr/bin/echo $ParamValue > /data/params/d/${ParamName}
done