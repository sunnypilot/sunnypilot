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
void live_H(double *in_vec, double *out_2013739140175643273);
void live_err_fun(double *nom_x, double *delta_x, double *out_1876438827900857303);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_3087809867876308847);
void live_H_mod_fun(double *state, double *out_3909243575089689648);
void live_f_fun(double *state, double dt, double *out_5601172785335869134);
void live_F_fun(double *state, double dt, double *out_1276442692334032077);
void live_h_4(double *state, double *unused, double *out_5526042232346777828);
void live_H_4(double *state, double *unused, double *out_5524503644776366178);
void live_h_9(double *state, double *unused, double *out_6361605780069524325);
void live_H_9(double *state, double *unused, double *out_2635642092496286836);
void live_h_10(double *state, double *unused, double *out_7655262323704911590);
void live_H_10(double *state, double *unused, double *out_5035020155542049060);
void live_h_12(double *state, double *unused, double *out_207745976639939943);
void live_H_12(double *state, double *unused, double *out_4903404619728772511);
void live_h_35(double *state, double *unused, double *out_3761009240575150130);
void live_H_35(double *state, double *unused, double *out_2157841587403758802);
void live_h_32(double *state, double *unused, double *out_8490477202422695563);
void live_H_32(double *state, double *unused, double *out_547182925497991135);
void live_h_13(double *state, double *unused, double *out_4828476018981696148);
void live_H_13(double *state, double *unused, double *out_5157033160448038839);
void live_h_14(double *state, double *unused, double *out_6361605780069524325);
void live_H_14(double *state, double *unused, double *out_2635642092496286836);
void live_h_33(double *state, double *unused, double *out_6019711942166543762);
void live_H_33(double *state, double *unused, double *out_992715417235098802);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}