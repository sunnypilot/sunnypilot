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
void car_err_fun(double *nom_x, double *delta_x, double *out_5123805303118663312);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_6837749996360934905);
void car_H_mod_fun(double *state, double *out_1004474096501644305);
void car_f_fun(double *state, double dt, double *out_4352460870670239441);
void car_F_fun(double *state, double dt, double *out_4167083004924647729);
void car_h_25(double *state, double *unused, double *out_7195362026210797347);
void car_H_25(double *state, double *unused, double *out_517600271157786473);
void car_h_24(double *state, double *unused, double *out_1170089474205098434);
void car_H_24(double *state, double *unused, double *out_6057971535433731628);
void car_h_30(double *state, double *unused, double *out_8645993418839680514);
void car_H_30(double *state, double *unused, double *out_2000732687349462154);
void car_h_26(double *state, double *unused, double *out_4315762643117593807);
void car_H_26(double *state, double *unused, double *out_4259103590031842697);
void car_h_27(double *state, double *unused, double *out_6592046141534319830);
void car_H_27(double *state, double *unused, double *out_4224326758533405371);
void car_h_29(double *state, double *unused, double *out_3644320151178834869);
void car_H_29(double *state, double *unused, double *out_2510964031663854338);
void car_h_28(double *state, double *unused, double *out_2872728760168391021);
void car_H_28(double *state, double *unused, double *out_2571434985405676236);
void car_h_31(double *state, double *unused, double *out_424526799860446411);
void car_H_31(double *state, double *unused, double *out_486954309280826045);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}