import matplotlib.pyplot as plt
import os
import sys
import argparse
import numpy as np
import base64
import io

from openpilot.tools.lib.logreader import LogReader, ReadMode

def extract_mem_cpu_data(lr):
  times, mems, cpus = [], [], []
  start_time = None

  for msg in lr:
    if msg.which() == 'procLog':
      if start_time is None:
        start_time = msg.logMonoTime
      mem = msg.procLog.mem
      mem_usage = (mem.total - mem.available) / mem.total * 100
      cpu_usages = [(total - cpu.idle) / total * 100 for cpu in msg.procLog.cpuTimes
                    if (total := cpu.idle + cpu.user + cpu.system + cpu.nice + cpu.iowait + cpu.irq + cpu.softirq) > 0]
      avg_cpu = sum(cpu_usages) / len(cpu_usages) if cpu_usages else 0
      times.append((msg.logMonoTime - start_time) / 1e9)
      mems.append(mem_usage)
      cpus.append(avg_cpu)
  return times, mems, cpus

def process_segment(lr):
  return [extract_mem_cpu_data(lr)]

def calculate_r_squared(y_true, y_pred):
  ss_res = np.sum((y_true - y_pred) ** 2)
  ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
  return 1 - (ss_res / ss_tot) if ss_tot != 0 else 0

def plot_results(segments, segment_data, route_name):
  valid_data = [d for d in segment_data if d and d[0]]
  if not valid_data:
    print("No valid data to plot")
    return

  avg_mems = [np.mean(d[1]) for d in valid_data]
  avg_cpus = [np.mean(d[2]) for d in valid_data]
  valid_segments = [segments[i] for i, d in enumerate(segment_data) if d and d[0]]

  height = max(10, 5 + len(valid_segments) * 0.4)
  fig1, ax1 = plt.subplots(1, 1, figsize=(12, height), dpi=150)

  y_pos = range(len(valid_segments))
  ax1.barh([y - 0.2 for y in y_pos], avg_mems, height=0.4, color="dodgerblue", alpha=0.8, label="Avg Mem %")
  ax1.barh([y + 0.2 for y in y_pos], avg_cpus, height=0.4, color="green", alpha=0.8, label="Avg CPU %")

  for i, (mem, cpu) in enumerate(zip(avg_mems, avg_cpus, strict=True)):
    ax1.text(mem, i - 0.2, f"{mem:.1f}%", va="center", fontsize=8, color="#005a9e", fontweight="bold")
    ax1.text(cpu, i + 0.2, f"{cpu:.1f}%", va="center", fontsize=8, color="#005a9e", fontweight="bold")

  ax1.set_yticks(y_pos)
  ax1.set_yticklabels([f"Seg {s}" for s in valid_segments])
  ax1.set_xlabel("Usage (%)")
  ax1.set_title("Average Memory and CPU Usage by Segment")
  ax1.legend()
  ax1.grid(axis="x", linestyle="--", alpha=0.5)
  ax1.invert_yaxis()

  fig2, ax2 = plt.subplots(1, 1, figsize=(12, 8), dpi=150)
  combined_times, combined_mems, combined_cpus = [], [], []
  time_offset = 0.0
  for times, mems, cpus in valid_data:
    if times:
      combined_times.extend([t + time_offset for t in times])
      combined_mems.extend(mems)
      combined_cpus.extend(cpus)
      time_offset += max(times)

  ax2.plot(combined_times, combined_mems, color="red", label="Memory Usage", alpha=0.6)
  ax2.plot(combined_times, combined_cpus, color="blue", label="CPU Usage", alpha=0.6)

  warmup_sec = 60
  if len(combined_times) > 1 and combined_times[-1] > warmup_sec:
      mask = np.array(combined_times) > warmup_sec
      x_reg = np.array(combined_times)[mask]

      y_mem_reg = np.array(combined_mems)[mask]
      slope_mem, intercept_mem = np.polyfit(x_reg, y_mem_reg, 1)
      trend_mem = slope_mem * x_reg + intercept_mem
      r2_mem = calculate_r_squared(y_mem_reg, trend_mem)
      ax2.plot(x_reg, trend_mem, color="darkred", linestyle="--", linewidth=2.5,
               label=f"Mem Trend (Slope: {slope_mem:.4f} %/s, R²: {r2_mem:.2f})")

      y_cpu_reg = np.array(combined_cpus)[mask]
      slope_cpu, intercept_cpu = np.polyfit(x_reg, y_cpu_reg, 1)
      trend_cpu = slope_cpu * x_reg + intercept_cpu
      r2_cpu = calculate_r_squared(y_cpu_reg, trend_cpu)
      ax2.plot(x_reg, trend_cpu, color="navy", linestyle="--", linewidth=2.5,
               label=f"CPU Trend (Slope: {slope_cpu:.4f} %/s, R²: {r2_cpu:.2f})")

  ax2.set_xlabel("Time (s)")
  ax2.set_ylabel("Usage (%)")
  ax2.set_title("Memory and CPU Usage Over Time")
  ax2.legend(loc='lower left', fontsize='small', framealpha=0.9)
  ax2.grid(True, linestyle="--", alpha=0.5)

  buffer1 = io.BytesIO()
  fig1.savefig(buffer1, format='webp', bbox_inches='tight', pad_inches=1.0)
  buffer1.seek(0)
  img1 = base64.b64encode(buffer1.getvalue()).decode()

  buffer2 = io.BytesIO()
  fig2.savefig(buffer2, format='webp', bbox_inches='tight', pad_inches=1.0)
  buffer2.seek(0)
  img2 = base64.b64encode(buffer2.getvalue()).decode()

  filename = f"memory_usage_{route_name}.html"
  save_path = os.path.join(os.path.dirname(__file__), "plots", filename)
  os.makedirs(os.path.dirname(save_path), exist_ok=True)

  html_template = (
    "<style>body{font-family:Arial,sans-serif;margin:20px}" +
    "h1,h2,h3{text-align:center;margin:5px 0}h2{margin-bottom:10px}" +
    "img{width:100%;max-width:800px;height:auto;display:block;margin:0 auto}</style>" +
    f"<h1>Memory Profile Report</h1><h3>Route: {route_name.replace('_', '/')}</h3>" +
    f"<img src='data:image/webp;base64,{img1}'>" +
    f"<img src='data:image/webp;base64,{img2}'>"
  )

  plt.close(fig1)
  plt.close(fig2)

  with open(save_path, "w") as f:
    f.write(html_template)

  print(f"Report saved to {save_path}")

def main():
  parser = argparse.ArgumentParser(description='Extract memory usage from route logs.')
  parser.add_argument('route_or_segment_name', help='Route or segment name from comma connect')
  args = parser.parse_args()

  try:
    print(f"Fetching logs for {args.route_or_segment_name}")
    lr = LogReader(args.route_or_segment_name, default_mode=ReadMode.QLOG)
    segment_data = lr.run_across_segments(24, process_segment)
    segments = list(range(len(segment_data)))
    route_name = args.route_or_segment_name.replace('/', '_')
    plot_results(segments, segment_data, route_name)
  except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)

if __name__ == "__main__":
  main()
