#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void live_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_9(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_12(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_35(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_32(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_33(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_H(double *in_vec, double *out_6746369553526897517);
void live_err_fun(double *nom_x, double *delta_x, double *out_2356689388845686605);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_7416532235122030660);
void live_H_mod_fun(double *state, double *out_7744797074742978621);
void live_f_fun(double *state, double dt, double *out_8063025216892748525);
void live_F_fun(double *state, double dt, double *out_1924980074135776075);
void live_h_4(double *state, double *unused, double *out_7366302340587907635);
void live_H_4(double *state, double *unused, double *out_8678952100085115055);
void live_h_9(double *state, double *unused, double *out_1116014595619586497);
void live_H_9(double *state, double *unused, double *out_2480573038359989091);
void live_h_10(double *state, double *unused, double *out_15153629602772458);
void live_H_10(double *state, double *unused, double *out_4583653000591918572);
void live_h_12(double *state, double *unused, double *out_9071809923999704409);
void live_H_12(double *state, double *unused, double *out_4748335565592474766);
void live_h_35(double *state, double *unused, double *out_7011637724721731008);
void live_H_35(double *state, double *unused, double *out_2002772533267461057);
void live_h_32(double *state, double *unused, double *out_8005805873262674095);
void live_H_32(double *state, double *unused, double *out_6269965131311088716);
void live_h_13(double *state, double *unused, double *out_7868428076142185420);
void live_H_13(double *state, double *unused, double *out_4177806446556115282);
void live_h_14(double *state, double *unused, double *out_1116014595619586497);
void live_H_14(double *state, double *unused, double *out_2480573038359989091);
void live_h_33(double *state, double *unused, double *out_5108012817780654932);
void live_H_33(double *state, double *unused, double *out_1147784471371396547);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}