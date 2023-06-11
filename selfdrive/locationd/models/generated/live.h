#pragma once
#include "rednose/helpers/common_ekf.h"
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
void live_H(double *in_vec, double *out_6409019039917668284);
void live_err_fun(double *nom_x, double *delta_x, double *out_4061617048242378524);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_1032655403399547817);
void live_H_mod_fun(double *state, double *out_1457537824329529482);
void live_f_fun(double *state, double dt, double *out_7387809313477893541);
void live_F_fun(double *state, double dt, double *out_9180543782983665576);
void live_h_4(double *state, double *unused, double *out_4492390463949384143);
void live_H_4(double *state, double *unused, double *out_6840823934948797475);
void live_h_9(double *state, double *unused, double *out_7683409762000862661);
void live_H_9(double *state, double *unused, double *out_6599634288319206830);
void live_h_10(double *state, double *unused, double *out_9216865912583274047);
void live_H_10(double *state, double *unused, double *out_773562674632846954);
void live_h_12(double *state, double *unused, double *out_7476619097990127394);
void live_H_12(double *state, double *unused, double *out_1821367526916835680);
void live_h_35(double *state, double *unused, double *out_162724865929704519);
void live_H_35(double *state, double *unused, double *out_924195505408178029);
void live_h_32(double *state, double *unused, double *out_4377549943098853278);
void live_H_32(double *state, double *unused, double *out_3416809270324928859);
void live_h_13(double *state, double *unused, double *out_1977043243384356195);
void live_H_13(double *state, double *unused, double *out_7445239302620530630);
void live_h_14(double *state, double *unused, double *out_7683409762000862661);
void live_H_14(double *state, double *unused, double *out_6599634288319206830);
void live_h_33(double *state, double *unused, double *out_605021574862289458);
void live_H_33(double *state, double *unused, double *out_323604872937332495);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}