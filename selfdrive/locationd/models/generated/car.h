#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void car_update_25(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_24(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_30(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_26(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_27(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_29(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_28(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_31(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_err_fun(double *nom_x, double *delta_x, double *out_7323774311990484810);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_3361913979724621566);
void car_H_mod_fun(double *state, double *out_7670763674896342596);
void car_f_fun(double *state, double dt, double *out_4442205562604345935);
void car_F_fun(double *state, double dt, double *out_3741498127708014361);
void car_h_25(double *state, double *unused, double *out_8739001293148261377);
void car_H_25(double *state, double *unused, double *out_8219246077433628171);
void car_h_24(double *state, double *unused, double *out_3866938681010227057);
void car_H_24(double *state, double *unused, double *out_4661320478631305035);
void car_h_30(double *state, double *unused, double *out_8463807230863755488);
void car_H_30(double *state, double *unused, double *out_1302555735942011416);
void car_h_26(double *state, double *unused, double *out_4981263575184950483);
void car_H_26(double *state, double *unused, double *out_4914720107672827570);
void car_h_27(double *state, double *unused, double *out_1946758319516529598);
void car_H_27(double *state, double *unused, double *out_3477319047742436327);
void car_h_29(double *state, double *unused, double *out_9039426989944133693);
void car_H_29(double *state, double *unused, double *out_792324391627619232);
void car_h_28(double *state, double *unused, double *out_4551163640325227249);
void car_H_28(double *state, double *unused, double *out_5874723408697149806);
void car_h_31(double *state, double *unused, double *out_7860862958278154023);
void car_H_31(double *state, double *unused, double *out_8188600115556667743);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}