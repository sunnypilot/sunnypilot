from cereal import custom, messaging
MpcSource = custom.MpcSource

def get_mpc_mode(sm, dynamic_experimental_controller, mpc, CP):
  """
  Determines the appropriate MPC mode based on the experimental state and system 
  configurations. It either returns a default mode or updates the dynamic 
  experimental controller and retrieves the updated mode.

  :param is_experimental: A flag indicating whether to use the experimental mode. 
                          If False, defaults to 'acc' mode.
  :type is_experimental: bool

  :return: The calculated or retrieved MPC mode.
  :rtype: str
  """
  is_experimental = sm['selfdriveState'].experimentalMode
  if not dynamic_experimental_controller.is_enabled() or not is_experimental:
    return 'blended' if is_experimental else 'acc'

  dynamic_experimental_controller.set_mpc_fcw_crash_cnt(mpc.crash_cnt)
  dynamic_experimental_controller.update(CP.radarUnavailable, sm['carState'], sm['radarState'].leadOne, sm['modelV2'], sm['controlsState'])
  #, sm['navInstruction'].maneuverDistance)
  return dynamic_experimental_controller.get_mpc_mode()


def publish_longitudinal_plan_sp(sm, pm, mpc, dynamic_experimental_controller):
  plan_sp_send = messaging.new_message('longitudinalPlanSP')

  plan_sp_send.valid = sm.all_checks(service_list=['carState', 'controlsState'])

  longitudinalPlanSP = plan_sp_send.longitudinalPlanSP

  # DEC
  longitudinalPlanSP.mpcSource = MpcSource.blended if mpc.mode == 'blended' else MpcSource.acc
  print(f"mpcSource: {longitudinalPlanSP.mpcSource}")

  longitudinalPlanSP.dynamicExperimentalControl = dynamic_experimental_controller.is_enabled()
  print(f"dynamicExperimentalControl: {longitudinalPlanSP.dynamicExperimentalControl}")


  pm.send('longitudinalPlanSP', plan_sp_send)
