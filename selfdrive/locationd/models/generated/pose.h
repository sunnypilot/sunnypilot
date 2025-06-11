#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_err_fun(double *nom_x, double *delta_x, double *out_1350382518294072040);
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_4816619957066290687);
void pose_H_mod_fun(double *state, double *out_6137993433719180276);
void pose_f_fun(double *state, double dt, double *out_8563298307309017918);
void pose_F_fun(double *state, double dt, double *out_6651613570104814248);
void pose_h_4(double *state, double *unused, double *out_3971641468391678980);
void pose_H_4(double *state, double *unused, double *out_8716652090797251543);
void pose_h_10(double *state, double *unused, double *out_9093229976132518865);
void pose_H_10(double *state, double *unused, double *out_943400041793457972);
void pose_h_13(double *state, double *unused, double *out_3008735883514341503);
void pose_H_13(double *state, double *unused, double *out_6517818157579967272);
void pose_h_14(double *state, double *unused, double *out_879287342420246227);
void pose_H_14(double *state, double *unused, double *out_5766851126572815544);
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt);
}