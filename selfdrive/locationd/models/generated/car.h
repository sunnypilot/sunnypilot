#pragma once
#include "rednose/helpers/common_ekf.h"
extern "C" {
void car_update_25(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_24(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_30(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_26(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_27(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_29(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_28(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_31(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_err_fun(double *nom_x, double *delta_x, double *out_8630036957783610817);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_7303735420975857079);
void car_H_mod_fun(double *state, double *out_912091471879250615);
void car_f_fun(double *state, double dt, double *out_6387851905084876196);
void car_F_fun(double *state, double dt, double *out_7370170245979772652);
void car_h_25(double *state, double *unused, double *out_157466368787385471);
void car_H_25(double *state, double *unused, double *out_3683197520838206278);
void car_h_24(double *state, double *unused, double *out_8915772749604783063);
void car_H_24(double *state, double *unused, double *out_1510547921832706712);
void car_h_30(double *state, double *unused, double *out_443951788825978083);
void car_H_30(double *state, double *unused, double *out_6201530479345454905);
void car_h_26(double *state, double *unused, double *out_1047267673502455600);
void car_H_26(double *state, double *unused, double *out_58305798035849946);
void car_h_27(double *state, double *unused, double *out_5159139636448231116);
void car_H_27(double *state, double *unused, double *out_4026767167545029994);
void car_h_29(double *state, double *unused, double *out_9020823112876732768);
void car_H_29(double *state, double *unused, double *out_6711761823659847089);
void car_h_28(double *state, double *unused, double *out_3468691801712550156);
void car_H_28(double *state, double *unused, double *out_1629362806590316515);
void car_h_31(double *state, double *unused, double *out_8654127050051125463);
void car_H_31(double *state, double *unused, double *out_684513900269201422);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}