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
void live_H(double *in_vec, double *out_5547513360766488616);
void live_err_fun(double *nom_x, double *delta_x, double *out_8152021498605537933);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_3488683882407452892);
void live_H_mod_fun(double *state, double *out_5050869278678087392);
void live_f_fun(double *state, double dt, double *out_4582041944931785985);
void live_F_fun(double *state, double dt, double *out_470910177407983085);
void live_h_4(double *state, double *unused, double *out_4162695987564959166);
void live_H_4(double *state, double *unused, double *out_7166535479927763264);
void live_h_9(double *state, double *unused, double *out_1325124770210002279);
void live_H_9(double *state, double *unused, double *out_7407725126557353909);
void live_h_10(double *state, double *unused, double *out_6692785092354307680);
void live_H_10(double *state, double *unused, double *out_5121103522105378464);
void live_h_12(double *state, double *unused, double *out_4404100439764009988);
void live_H_12(double *state, double *unused, double *out_6260752185749826557);
void live_h_35(double *state, double *unused, double *out_3190577133274387988);
void live_H_35(double *state, double *unused, double *out_7913546536409180976);
void live_h_32(double *state, double *unused, double *out_4047494869817944848);
void live_H_32(double *state, double *unused, double *out_2112242164201568418);
void live_h_13(double *state, double *unused, double *out_8986692755940651560);
void live_H_13(double *state, double *unused, double *out_8772512993598512035);
void live_h_14(double *state, double *unused, double *out_1325124770210002279);
void live_H_14(double *state, double *unused, double *out_7407725126557353909);
void live_h_33(double *state, double *unused, double *out_7455934698752997074);
void live_H_33(double *state, double *unused, double *out_4762989531770323372);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}