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
void live_H(double *in_vec, double *out_3746421578053593084);
void live_err_fun(double *nom_x, double *delta_x, double *out_105236110951022335);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_2568821321730323506);
void live_H_mod_fun(double *state, double *out_4178029040380659435);
void live_f_fun(double *state, double dt, double *out_2854293671312532649);
void live_F_fun(double *state, double dt, double *out_2734333177670994956);
void live_h_4(double *state, double *unused, double *out_6903605953758365865);
void live_H_4(double *state, double *unused, double *out_1185945476069595036);
void live_h_9(double *state, double *unused, double *out_843879415323879201);
void live_H_9(double *state, double *unused, double *out_8473164411334042506);
void live_h_10(double *state, double *unused, double *out_1414980015961280100);
void live_H_10(double *state, double *unused, double *out_428453928759913306);
void live_h_12(double *state, double *unused, double *out_8263943828113241647);
void live_H_12(double *state, double *unused, double *out_5195312900973137960);
void live_h_35(double *state, double *unused, double *out_8651411254774222807);
void live_H_35(double *state, double *unused, double *out_6848107251632492379);
void live_h_32(double *state, double *unused, double *out_3384300439832651195);
void live_H_32(double *state, double *unused, double *out_1046802879424879821);
void live_h_13(double *state, double *unused, double *out_5825044127856092602);
void live_H_13(double *state, double *unused, double *out_1730508795022754155);
void live_h_14(double *state, double *unused, double *out_843879415323879201);
void live_H_14(double *state, double *unused, double *out_8473164411334042506);
void live_h_33(double *state, double *unused, double *out_7000952243169395244);
void live_H_33(double *state, double *unused, double *out_3697550246993634775);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}