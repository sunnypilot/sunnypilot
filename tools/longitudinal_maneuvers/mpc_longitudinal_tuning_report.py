import io
import sys
import markdown
import numpy as np
import matplotlib.pyplot as plt
from openpilot.common.realtime import DT_MDL
from openpilot.selfdrive.controls.tests.test_following_distance import desired_follow_distance
from openpilot.tools.longitudinal_maneuvers.maneuver_helpers import Axis, axis_labels
from openpilot.selfdrive.test.longitudinal_maneuvers.maneuver import Maneuver


def get_html_from_results(results, labels, AXIS):
  fig, ax = plt.subplots(figsize=(16, 8))
  for idx, key in enumerate(results.keys()):
    ax.plot(results[key][:, Axis.TIME], results[key][:, AXIS], label=labels[idx])

  ax.set_xlabel(axis_labels[Axis.TIME])
  ax.set_ylabel(axis_labels[AXIS])
  ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0)
  ax.grid(True, linestyle='--', alpha=0.7)
  ax.text(-0.075, 0.5, '.', transform=ax.transAxes, color='none')

  fig_buffer = io.StringIO()
  fig.savefig(fig_buffer, format='svg', bbox_inches='tight')
  plt.close(fig)
  return fig_buffer.getvalue() + '<br/>'

def generate_mpc_tuning_report():
  htmls = []

  results = {}
  name = 'Resuming behind lead'
  labels = []
  for lead_accel in np.linspace(1.0, 4.0, 4):
    man = Maneuver(
      '',
      duration=11,
      initial_speed=0.0,
      lead_relevancy=True,
      initial_distance_lead=desired_follow_distance(0.0, 0.0),
      speed_lead_values=[0.0, 10 * lead_accel],
      cruise_values=[100, 100],
      prob_lead_values=[1.0, 1.0],
      breakpoints=[1., 11],
    )
    valid, results[lead_accel] = man.evaluate()
    labels.append(f'{lead_accel} m/s^2 lead acceleration')

  htmls.append(markdown.markdown('# ' + name))
  htmls.append(get_html_from_results(results, labels, Axis.EGO_V))
  htmls.append(get_html_from_results(results, labels, Axis.EGO_A))


  results = {}
  name = 'Approaching stopped car from 140m'
  labels = []
  for speed in np.arange(0,45,5):
    man = Maneuver(
      name,
      duration=30.,
      initial_speed=float(speed),
      lead_relevancy=True,
      initial_distance_lead=140.,
      speed_lead_values=[0.0, 0.],
      breakpoints=[0., 30.],
    )
    valid, results[speed] = man.evaluate()
    labels.append(f'{speed} m/s approach speed')

  htmls.append(markdown.markdown('# ' + name))
  htmls.append(get_html_from_results(results, labels, Axis.EGO_A))
  htmls.append(get_html_from_results(results, labels, Axis.D_REL))


  results = {}
  name = 'Following 5s (triangular) oscillating lead'
  labels = []
  speed = np.int64(10)
  for oscil in np.arange(0, 10, 1):
    man = Maneuver(
      '',
      duration=30.,
      initial_speed=float(speed),
      lead_relevancy=True,
      initial_distance_lead=desired_follow_distance(speed, speed),
      speed_lead_values=[speed, speed, speed - oscil, speed + oscil, speed - oscil, speed + oscil, speed - oscil],
      breakpoints=[0.,2., 5, 8, 15, 18, 25.],
    )
    valid, results[oscil] = man.evaluate()
    labels.append(f'{oscil} m/s oscillation size')

  htmls.append(markdown.markdown('# ' + name))
  htmls.append(get_html_from_results(results, labels, Axis.D_REL))
  htmls.append(get_html_from_results(results, labels, Axis.EGO_V))
  htmls.append(get_html_from_results(results, labels, Axis.EGO_A))


  results = {}
  name = 'Following 5s (sinusoidal) oscillating lead'
  labels = []
  speed = np.int64(10)
  duration = float(30)
  f_osc = 1. / 5
  for oscil in np.arange(0, 10, 1):
    bps = DT_MDL * np.arange(int(duration / DT_MDL))
    lead_speeds = speed + oscil * np.sin(2 * np.pi * f_osc * bps)
    man = Maneuver(
      '',
      duration=duration,
      initial_speed=float(speed),
      lead_relevancy=True,
      initial_distance_lead=desired_follow_distance(speed, speed),
      speed_lead_values=lead_speeds,
      breakpoints=bps,
    )
    valid, results[oscil] = man.evaluate()
    labels.append(f'{oscil} m/s oscillation size')

  htmls.append(markdown.markdown('# ' + name))
  htmls.append(get_html_from_results(results, labels, Axis.D_REL))
  htmls.append(get_html_from_results(results, labels, Axis.EGO_V))
  htmls.append(get_html_from_results(results, labels, Axis.EGO_A))


  results = {}
  name = 'Speed profile when converging to steady state lead at 30m/s'
  labels = []
  for distance in np.arange(20, 140, 10):
    man = Maneuver(
      '',
      duration=50,
      initial_speed=30.0,
      lead_relevancy=True,
      initial_distance_lead=distance,
      speed_lead_values=[30.0],
      breakpoints=[0.],
    )
    valid, results[distance] = man.evaluate()
    labels.append(f'{distance} m initial distance')

  htmls.append(markdown.markdown('# ' + name))
  htmls.append(get_html_from_results(results, labels, Axis.EGO_V))
  htmls.append(get_html_from_results(results, labels, Axis.D_REL))


  results = {}
  name = 'Speed profile when converging to steady state lead at 20m/s'
  labels = []
  for distance in np.arange(20, 140, 10):
    man = Maneuver(
      '',
      duration=50,
      initial_speed=20.0,
      lead_relevancy=True,
      initial_distance_lead=distance,
      speed_lead_values=[20.0],
      breakpoints=[0.],
    )
    valid, results[distance] = man.evaluate()
    labels.append(f'{distance} m initial distance')

  htmls.append(markdown.markdown('# ' + name))
  htmls.append(get_html_from_results(results, labels, Axis.EGO_V))
  htmls.append(get_html_from_results(results, labels, Axis.D_REL))


  results = {}
  name = 'Following car at 30m/s that comes to a stop'
  labels = []
  for stop_time in np.arange(4, 14, 1):
    man = Maneuver(
      '',
      duration=30,
      initial_speed=30.0,
      cruise_values=[30.0, 30.0, 30.0],
      lead_relevancy=True,
      initial_distance_lead=60.0,
      speed_lead_values=[30.0, 30.0, 0.0],
      breakpoints=[0., 5., 5 + stop_time],
    )
    valid, results[stop_time] = man.evaluate()
    labels.append(f'{stop_time} seconds stop time')

  htmls.append(markdown.markdown('# ' + name))
  htmls.append(get_html_from_results(results, labels, Axis.EGO_A))
  htmls.append(get_html_from_results(results, labels, Axis.D_REL))


  results = {}
  name = 'Response to cut-in at half follow distance'
  labels = []
  for speed in np.arange(0, 40, 5):
    man = Maneuver(
      '',
      duration=20,
      initial_speed=float(speed),
      cruise_values=[speed, speed, speed],
      lead_relevancy=True,
      initial_distance_lead=desired_follow_distance(speed, speed)/2,
      speed_lead_values=[speed, speed, speed],
      prob_lead_values=[0.0, 0.0, 1.0],
      breakpoints=[0., 5.0, 5.01],
    )
    valid, results[speed] = man.evaluate()
    labels.append(f'{speed} m/s speed')

  htmls.append(markdown.markdown('# ' + name))
  htmls.append(get_html_from_results(results, labels, Axis.EGO_A))
  htmls.append(get_html_from_results(results, labels, Axis.D_REL))


  results = {}
  name = 'Follow a lead that accelerates at 2m/s^2 until steady state speed'
  labels = []
  for speed in np.arange(0, 40, 5):
    man = Maneuver(
      '',
      duration=60,
      initial_speed=0.0,
      lead_relevancy=True,
      initial_distance_lead=desired_follow_distance(0.0, 0.0),
      speed_lead_values=[0.0, 0.0, speed],
      prob_lead_values=[1.0, 1.0, 1.0],
      breakpoints=[0., 1.0, speed/2],
    )
    valid, results[speed] = man.evaluate()
    labels.append(f'{speed} m/s speed')

  htmls.append(markdown.markdown('# ' + name))
  htmls.append(get_html_from_results(results, labels, Axis.EGO_V))
  htmls.append(get_html_from_results(results, labels, Axis.EGO_A))


  results = {}
  name = 'From stop to cruise'
  labels = []
  for speed in np.arange(0, 40, 5):
    man = Maneuver(
      '',
      duration=50,
      initial_speed=0.0,
      lead_relevancy=True,
      initial_distance_lead=desired_follow_distance(0.0, 0.0),
      speed_lead_values=[0.0, 0.0],
      cruise_values=[0.0, speed],
      prob_lead_values=[0.0, 0.0],
      breakpoints=[1., 1.01],
    )
    valid, results[speed] = man.evaluate()
    labels.append(f'{speed} m/s speed')

  htmls.append(markdown.markdown('# ' + name))
  htmls.append(get_html_from_results(results, labels, Axis.EGO_V))
  htmls.append(get_html_from_results(results, labels, Axis.EGO_A))


  results = {}
  name = 'From cruise to min'
  labels = []
  for speed in np.arange(10, 40, 5):
    man = Maneuver(
      '',
      duration=50,
      initial_speed=float(speed),
      lead_relevancy=True,
      initial_distance_lead=desired_follow_distance(0.0, 0.0),
      speed_lead_values=[0.0, 0.0],
      cruise_values=[speed, 10.0],
      prob_lead_values=[0.0, 0.0],
      breakpoints=[1., 1.01],
    )
    valid, results[speed] = man.evaluate()
    labels.append(f'{speed} m/s speed')

  htmls.append(markdown.markdown('# ' + name))
  htmls.append(get_html_from_results(results, labels, Axis.EGO_V))
  htmls.append(get_html_from_results(results, labels, Axis.EGO_A))

  return htmls

def run_single_config(config):
  accel_name, accel_key, dyn_name, dyn_key = config
  import os
  import uuid
  import markdown
  
  # Crucial: Isolate each parallel python process with a unique ZMQ/Params Shared Memory prefix!
  prefix = "tuning_" + str(uuid.uuid4())[:8]
  os.environ["OPENPILOT_PREFIX"] = prefix
  
  # Ensure the IPC directory exists so cereal/msgq doesn't crash when opening sockets
  os.makedirs(f"/dev/shm/msgq_{prefix}", exist_ok=True)
  os.makedirs(f"/dev/shm/{prefix}", exist_ok=True)
  
  from openpilot.common.params import Params
  from openpilot.selfdrive.test.longitudinal_maneuvers.maneuver import Maneuver
  
  original_init = Maneuver.__init__
  def new_init(self, title, duration, **kwargs):
      kwargs['personality'] = getattr(self, '__global_personality', 1)
      original_init(self, title, duration, **kwargs)
  Maneuver.__init__ = new_init

  params = Params()
  if accel_name == "Stock":
      params.put_bool("AccelPersonalityEnabled", False)
      params.put_bool("DynamicFollow", False)
      params.put("LongitudinalPersonality", 1)
      params.put("AccelPersonality", 1)
      Maneuver.__global_personality = 1
      title = "Stock (Openpilot) Baseline"
  else:
      params.put_bool("AccelPersonalityEnabled", True)
      params.put("AccelPersonality", accel_key)
      params.put_bool("DynamicFollow", True)
      params.put("LongitudinalPersonality", dyn_key)
      Maneuver.__global_personality = dyn_key
      title = f"{accel_name} Accel, {dyn_name} Dynamic"

  print(f"Starting simulation: {title}")
  htmls = generate_mpc_tuning_report()
  print(f"Finished simulation: {title}")
  
  header = markdown.markdown(f'<br><hr><h1>Tuning Report: {title}</h1>')
  return header + "".join(htmls)

if __name__ == '__main__':
  import multiprocessing as mp

  configs = [("Stock", -1, "Stock", -1)]
  accel_profiles = {0: "Sport", 1: "Normal", 2: "Eco"}
  dynamic_profiles = {0: "Aggressive", 1: "Standard", 2: "Relaxed"}

  for accel_key, accel_name in accel_profiles.items():
    for dyn_key, dyn_name in dynamic_profiles.items():
      configs.append((accel_name, accel_key, dyn_name, dyn_key))

  print(f"Booting {len(configs)} parallel simulations...")
  ctx = mp.get_context('spawn')
  with ctx.Pool(processes=min(len(configs), mp.cpu_count())) as pool:
      htmls_chunks = pool.map(run_single_config, configs)

  if len(sys.argv) < 2:
    file_name = 'long_mpc_tune_report.html'
  else:
    file_name = sys.argv[1]

  with open(file_name, 'w') as f:
    f.write(markdown.markdown('# MPC longitudinal tuning report (All Profiles)'))
    for chunk in htmls_chunks:
      f.write(chunk)
  print(f"Done! Report aggregated concurrently and saved to {file_name}")
