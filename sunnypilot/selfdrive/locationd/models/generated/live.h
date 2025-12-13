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
void live_H(double *in_vec, double *out_6773248180377028269);
void live_err_fun(double *nom_x, double *delta_x, double *out_3078908707285172450);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_3001687793636694690);
void live_H_mod_fun(double *state, double *out_7744172158108410202);
void live_f_fun(double *state, double dt, double *out_108246524572319324);
void live_F_fun(double *state, double dt, double *out_2806339196993722952);
void live_h_4(double *state, double *unused, double *out_8920660424317903088);
void live_H_4(double *state, double *unused, double *out_9062124490991154876);
void live_h_9(double *state, double *unused, double *out_2456085839319519733);
void live_H_9(double *state, double *unused, double *out_1774905555726707406);
void live_h_10(double *state, double *unused, double *out_4221670832727056511);
void live_H_10(double *state, double *unused, double *out_5715913554767402096);
void live_h_12(double *state, double *unused, double *out_8323206387338638220);
void live_H_12(double *state, double *unused, double *out_3003361205675663744);
void live_h_35(double *state, double *unused, double *out_1158746533604642232);
void live_H_35(double *state, double *unused, double *out_5695462433618547500);
void live_h_32(double *state, double *unused, double *out_9200596853550511094);
void live_H_32(double *state, double *unused, double *out_8532582402419095046);
void live_h_13(double *state, double *unused, double *out_890288028977404358);
void live_H_13(double *state, double *unused, double *out_2132609685842605794);
void live_h_14(double *state, double *unused, double *out_2456085839319519733);
void live_H_14(double *state, double *unused, double *out_1774905555726707406);
void live_h_33(double *state, double *unused, double *out_4535332388479281243);
void live_H_33(double *state, double *unused, double *out_2544905428979689896);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}