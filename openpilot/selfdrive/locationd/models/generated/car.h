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
void car_err_fun(double *nom_x, double *delta_x, double *out_7360625163823445495);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_8413491231423970122);
void car_H_mod_fun(double *state, double *out_2632326835772732722);
void car_f_fun(double *state, double dt, double *out_8532698894052839577);
void car_F_fun(double *state, double dt, double *out_5046006616921834778);
void car_h_25(double *state, double *unused, double *out_5546638875155758793);
void car_H_25(double *state, double *unused, double *out_890653814216758955);
void car_h_24(double *state, double *unused, double *out_4367318711229477977);
void car_H_24(double *state, double *unused, double *out_4448579413019082091);
void car_h_30(double *state, double *unused, double *out_1909189346901736443);
void car_H_30(double *state, double *unused, double *out_7807344155708375710);
void car_h_26(double *state, double *unused, double *out_6910862614562582088);
void car_H_26(double *state, double *unused, double *out_2850849504657297269);
void car_h_27(double *state, double *unused, double *out_3918136026546952058);
void car_H_27(double *state, double *unused, double *out_5632580843907950799);
void car_h_29(double *state, double *unused, double *out_3092483920759109202);
void car_H_29(double *state, double *unused, double *out_8317575500022767894);
void car_h_28(double *state, double *unused, double *out_4521451911223429575);
void car_H_28(double *state, double *unused, double *out_1163180900031130808);
void car_h_31(double *state, double *unused, double *out_5821832937440264682);
void car_H_31(double *state, double *unused, double *out_921299776093719383);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}