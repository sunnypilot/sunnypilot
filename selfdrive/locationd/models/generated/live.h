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
void live_H(double *in_vec, double *out_1414364393616267060);
void live_err_fun(double *nom_x, double *delta_x, double *out_8526993589485217283);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_5446140761574181847);
void live_H_mod_fun(double *state, double *out_5432513086891330118);
void live_f_fun(double *state, double dt, double *out_3124841438364502345);
void live_F_fun(double *state, double dt, double *out_1516188799163097895);
void live_h_4(double *state, double *unused, double *out_5146405128764971715);
void live_H_4(double *state, double *unused, double *out_8280514637229318136);
void live_h_9(double *state, double *unused, double *out_6521535856256346272);
void live_H_9(double *state, double *unused, double *out_2879010501215786010);
void live_h_10(double *state, double *unused, double *out_7650523423264487676);
void live_H_10(double *state, double *unused, double *out_8349484776071401233);
void live_h_12(double *state, double *unused, double *out_1249483860836207293);
void live_H_12(double *state, double *unused, double *out_1899256260186585140);
void live_h_35(double *state, double *unused, double *out_9194488278142985817);
void live_H_35(double *state, double *unused, double *out_246461909527230721);
void live_h_32(double *state, double *unused, double *out_703087583863910197);
void live_H_32(double *state, double *unused, double *out_7428477456930016442);
void live_h_13(double *state, double *unused, double *out_1177272293085447184);
void live_H_13(double *state, double *unused, double *out_8170091630093444732);
void live_h_14(double *state, double *unused, double *out_6521535856256346272);
void live_H_14(double *state, double *unused, double *out_2879010501215786010);
void live_h_33(double *state, double *unused, double *out_3292218118027320547);
void live_H_33(double *state, double *unused, double *out_3397018914166088325);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}