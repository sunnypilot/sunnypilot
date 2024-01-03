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
void live_H(double *in_vec, double *out_4803752866237518805);
void live_err_fun(double *nom_x, double *delta_x, double *out_3139786301780846039);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_5873938798188305086);
void live_H_mod_fun(double *state, double *out_7676734681660604098);
void live_f_fun(double *state, double dt, double *out_8180926755761486799);
void live_F_fun(double *state, double dt, double *out_1938659733493136892);
void live_h_4(double *state, double *unused, double *out_8681534188933206153);
void live_H_4(double *state, double *unused, double *out_4360580272650345355);
void live_h_9(double *state, double *unused, double *out_926990079681796669);
void live_H_9(double *state, double *unused, double *out_4119390626020754710);
void live_h_10(double *state, double *unused, double *out_2996523681036057994);
void live_H_10(double *state, double *unused, double *out_4414860148651295847);
void live_h_12(double *state, double *unused, double *out_7130410618713103849);
void live_H_12(double *state, double *unused, double *out_658876135381616440);
void live_h_35(double *state, double *unused, double *out_6517342850202050802);
void live_H_35(double *state, double *unused, double *out_3404439167706630149);
void live_h_32(double *state, double *unused, double *out_4403188540589911972);
void live_H_32(double *state, double *unused, double *out_6677495319863093524);
void live_h_13(double *state, double *unused, double *out_626880725603460292);
void live_H_13(double *state, double *unused, double *out_4495004969689374435);
void live_h_14(double *state, double *unused, double *out_926990079681796669);
void live_H_14(double *state, double *unused, double *out_4119390626020754710);
void live_h_33(double *state, double *unused, double *out_2722382023231819963);
void live_H_33(double *state, double *unused, double *out_6554996172345487753);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}