#!/usr/bin/env python3

import os
import time
import signal
import subprocess
import psutil


from openpilot.common.params import Params
from openpilot.common.swaglog import cloudlog

DASHCAM_MGR_PID_PARAM = "DashcamServerPid"


def main():
  manage_dashcam_serverd(DASHCAM_MGR_PID_PARAM, 'dashcam_serverd', 'system.dashcam_server.dashcam_server')


def is_dashcam_server_enabled(params):
  """检测 dashcam server 是否被用户启用"""
  return int(params.get("DashcamServerEnabled"))


def get_dashcam_server_port(params):
  """获取 dashcam server 端口"""
  return params.get("DashcamServerPort", encoding='utf-8')

def is_dashcam_server_running(params, pid_param):
  """检测 dashcam server 是否正在运行"""
  pid = params.get(pid_param, encoding='utf-8')
  if pid is None:
    return False

  try:
    # 检查进程是否存在
    p = psutil.Process(int(pid))
    cmdline = ' '.join(p.cmdline())
    return 'dashcam_server' in cmdline or 'system.dashcam_server.dashcam_server' in cmdline
  except (psutil.NoSuchProcess, psutil.AccessDenied, ValueError):
    return False


def start_dashcam_server(params, pid_param, process_name, target):
  """启动 dashcam server"""
  port = get_dashcam_server_port(params)
  cloudlog.info(f"启动 {process_name}，端口: {port}")

  proc = subprocess.Popen(['python', '-m', target],
                         stdin=open('/dev/null'),
                         stdout=open('/dev/null', 'w'),
                         stderr=open('/dev/null', 'w'),
                         preexec_fn=os.setpgrp)
  params.put(pid_param, str(proc.pid))

def stop_dashcam_server(params, pid_param, process_name):
  """停止 dashcam server"""
  pid = params.get(pid_param, encoding='utf-8')
  if pid is None:
    return

  try:
    cloudlog.info(f"停止 {process_name}，PID: {pid}")
    # 先发送 SIGTERM
    os.kill(int(pid), signal.SIGTERM)
    time.sleep(2)

    # 检查进程是否还在运行
    try:
      os.kill(int(pid), 0)
      # 如果还在运行，发送 SIGKILL
      cloudlog.info(f"强制停止 {process_name}，PID: {pid}")
      os.kill(int(pid), signal.SIGKILL)
    except OSError:
      pass  # 进程已经停止

  except (OSError, ValueError):
    pass  # 进程不存在或无效 PID
  finally:
    params.remove(pid_param)
    cloudlog.info(f"{process_name} 已停止")


def manage_dashcam_serverd(pid_param, process_name, target):
  params = Params()
  try:
    while True:
      # print("检测按钮是否开启")
      service_enabled = is_dashcam_server_enabled(params) == 1
      server_running = is_dashcam_server_running(params, pid_param)

      # 检测按钮是否开启，但是服务没开启则开启服务
      if service_enabled and not server_running:
        start_dashcam_server(params, pid_param, process_name, target)

      # 如果按钮关闭，并且服务开启则关闭服务
      elif not service_enabled and server_running:
        stop_dashcam_server(params, pid_param, process_name)

      # 每5秒检查一次
      time.sleep(3)

  except KeyboardInterrupt:
    cloudlog.info("收到停止信号，正在关闭...")
    if is_dashcam_server_running(params, pid_param):
      stop_dashcam_server(params, pid_param, process_name)
  except Exception as e:
    cloudlog.exception(f"manage_{process_name} 异常: {e}")


if __name__ == '__main__':
  main()
