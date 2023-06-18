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
void live_H(double *in_vec, double *out_5173492457777781966);
void live_err_fun(double *nom_x, double *delta_x, double *out_5922210577939604492);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_6180260714953073839);
void live_H_mod_fun(double *state, double *out_4517018211893934989);
void live_f_fun(double *state, double dt, double *out_8888895791769188636);
void live_F_fun(double *state, double dt, double *out_466548289212658788);
void live_h_4(double *state, double *unused, double *out_7903893439571717825);
void live_H_4(double *state, double *unused, double *out_8120204986329223125);
void live_h_9(double *state, double *unused, double *out_1448285436355291799);
void live_H_9(double *state, double *unused, double *out_7879015339699632480);
void live_h_10(double *state, double *unused, double *out_7833176734581826377);
void live_H_10(double *state, double *unused, double *out_2945925451724885313);
void live_h_12(double *state, double *unused, double *out_7236527996738028961);
void live_H_12(double *state, double *unused, double *out_3100748578297261330);
void live_h_35(double *state, double *unused, double *out_6306229462798517433);
void live_H_35(double *state, double *unused, double *out_355185545972247621);
void live_h_32(double *state, double *unused, double *out_8578926984007907638);
void live_H_32(double *state, double *unused, double *out_5446118826235364937);
void live_h_13(double *state, double *unused, double *out_8977427483885865133);
void live_H_13(double *state, double *unused, double *out_7231128031793255484);
void live_h_14(double *state, double *unused, double *out_1448285436355291799);
void live_H_14(double *state, double *unused, double *out_7879015339699632480);
void live_h_33(double *state, double *unused, double *out_3309457895536849751);
void live_H_33(double *state, double *unused, double *out_2795371458666609983);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}