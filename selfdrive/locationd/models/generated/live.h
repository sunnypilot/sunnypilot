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
void live_H(double *in_vec, double *out_3774328600697724702);
void live_err_fun(double *nom_x, double *delta_x, double *out_7836871875743155711);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_6630162193384917047);
void live_H_mod_fun(double *state, double *out_8048759451165961396);
void live_f_fun(double *state, double dt, double *out_7921013289385952844);
void live_F_fun(double *state, double dt, double *out_4662442160671292604);
void live_h_4(double *state, double *unused, double *out_7870695401363690378);
void live_H_4(double *state, double *unused, double *out_4792338244417275633);
void live_h_9(double *state, double *unused, double *out_8777781742605020016);
void live_H_9(double *state, double *unused, double *out_5033527891046866278);
void live_h_10(double *state, double *unused, double *out_4373838033093977729);
void live_H_10(double *state, double *unused, double *out_8635137508413484634);
void live_h_12(double *state, double *unused, double *out_2464697288469995839);
void live_H_12(double *state, double *unused, double *out_8634949421260314188);
void live_h_35(double *state, double *unused, double *out_991013079297920428);
void live_H_35(double *state, double *unused, double *out_5889386388935300479);
void live_h_32(double *state, double *unused, double *out_1645124735898739364);
void live_H_32(double *state, double *unused, double *out_4486439399712056049);
void live_h_13(double *state, double *unused, double *out_2926276888320798032);
void live_H_13(double *state, double *unused, double *out_517852867070353434);
void live_h_14(double *state, double *unused, double *out_8777781742605020016);
void live_H_14(double *state, double *unused, double *out_5033527891046866278);
void live_h_33(double *state, double *unused, double *out_1599134906378397443);
void live_H_33(double *state, double *unused, double *out_7137186767280811003);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}