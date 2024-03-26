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
void live_H(double *in_vec, double *out_5741538366148904217);
void live_err_fun(double *nom_x, double *delta_x, double *out_5395525281395102729);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_5662798387785861106);
void live_H_mod_fun(double *state, double *out_5468661714541527342);
void live_f_fun(double *state, double dt, double *out_190662760170240953);
void live_F_fun(double *state, double dt, double *out_4181959506564051689);
void live_h_4(double *state, double *unused, double *out_7332599807256392162);
void live_H_4(double *state, double *unused, double *out_738139759425007688);
void live_h_9(double *state, double *unused, double *out_4687024559125295446);
void live_H_9(double *state, double *unused, double *out_8025358694689455158);
void live_h_10(double *state, double *unused, double *out_5394612558262562034);
void live_H_10(double *state, double *unused, double *out_8732149241878267315);
void live_h_12(double *state, double *unused, double *out_3575326993580998459);
void live_H_12(double *state, double *unused, double *out_5757596167456969483);
void live_h_35(double *state, double *unused, double *out_4545132011588375210);
void live_H_35(double *state, double *unused, double *out_8503159199781983192);
void live_h_32(double *state, double *unused, double *out_5981145703195314132);
void live_H_32(double *state, double *unused, double *out_8002746536594559623);
void live_h_13(double *state, double *unused, double *out_6924330541432908653);
void live_H_13(double *state, double *unused, double *out_5987826932430976617);
void live_h_14(double *state, double *unused, double *out_4687024559125295446);
void live_H_14(double *state, double *unused, double *out_8025358694689455158);
void live_h_33(double *state, double *unused, double *out_1890533787516451050);
void live_H_33(double *state, double *unused, double *out_7255358821436472668);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}