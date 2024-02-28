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
void car_err_fun(double *nom_x, double *delta_x, double *out_6581031727810852793);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_9157278643797334052);
void car_H_mod_fun(double *state, double *out_493258648145988980);
void car_f_fun(double *state, double dt, double *out_7646812063593062567);
void car_F_fun(double *state, double dt, double *out_8742539171151325573);
void car_h_25(double *state, double *unused, double *out_8353939142913991519);
void car_H_25(double *state, double *unused, double *out_169381335348964671);
void car_h_24(double *state, double *unused, double *out_5452610352969860592);
void car_H_24(double *state, double *unused, double *out_639838817392303395);
void car_h_30(double *state, double *unused, double *out_3925690890824425794);
void car_H_30(double *state, double *unused, double *out_298720282492204741);
void car_h_26(double *state, double *unused, double *out_7264909465791674113);
void car_H_26(double *state, double *unused, double *out_3910884654223020895);
void car_h_27(double *state, double *unused, double *out_3352265875253145874);
void car_H_27(double *state, double *unused, double *out_2473483594292629652);
void car_h_29(double *state, double *unused, double *out_7201538703571882383);
void car_H_29(double *state, double *unused, double *out_4186846321162180685);
void car_h_28(double *state, double *unused, double *out_1649407392407699771);
void car_H_28(double *state, double *unused, double *out_9177498735477840357);
void car_h_31(double *state, double *unused, double *out_6455355402541537747);
void car_H_31(double *state, double *unused, double *out_138735373472004243);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}