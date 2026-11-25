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
void car_err_fun(double *nom_x, double *delta_x, double *out_7776651228618240194);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_5273421026182551058);
void car_H_mod_fun(double *state, double *out_2181953899905443363);
void car_f_fun(double *state, double dt, double *out_2503069281528488208);
void car_F_fun(double *state, double dt, double *out_1406798686887127281);
void car_h_25(double *state, double *unused, double *out_3759466007672649026);
void car_H_25(double *state, double *unused, double *out_8343452140830248448);
void car_h_24(double *state, double *unused, double *out_3758799493215832204);
void car_H_24(double *state, double *unused, double *out_4785526542027925312);
void car_h_30(double *state, double *unused, double *out_3207849157008383468);
void car_H_30(double *state, double *unused, double *out_5575595602751694970);
void car_h_26(double *state, double *unused, double *out_9031737129220547093);
void car_H_26(double *state, double *unused, double *out_6361788614005246944);
void car_h_27(double *state, double *unused, double *out_2486985049787524442);
void car_H_27(double *state, double *unused, double *out_3400832290951270059);
void car_h_29(double *state, double *unused, double *out_2762179112072030331);
void car_H_29(double *state, double *unused, double *out_6085826947066087154);
void car_h_28(double *state, double *unused, double *out_4515777654005541337);
void car_H_28(double *state, double *unused, double *out_1003427929996556580);
void car_h_31(double *state, double *unused, double *out_6376371694301822855);
void car_H_31(double *state, double *unused, double *out_5735580511771895468);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}