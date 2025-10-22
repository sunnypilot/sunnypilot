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
void live_H(double *in_vec, double *out_5575510021741180691);
void live_err_fun(double *nom_x, double *delta_x, double *out_4893154029986387901);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_5675355979356323921);
void live_H_mod_fun(double *state, double *out_9128713921715953632);
void live_f_fun(double *state, double dt, double *out_3274333114073176547);
void live_F_fun(double *state, double dt, double *out_7324676647981046755);
void live_h_4(double *state, double *unused, double *out_8911989884858215772);
void live_H_4(double *state, double *unused, double *out_1545045470011699408);
void live_h_9(double *state, double *unused, double *out_4393084026744099620);
void live_H_9(double *state, double *unused, double *out_8832264405276146878);
void live_h_10(double *state, double *unused, double *out_5432116630879962303);
void live_H_10(double *state, double *unused, double *out_2487950163448138648);
void live_h_12(double *state, double *unused, double *out_2956097051640129536);
void live_H_12(double *state, double *unused, double *out_6564501878043661203);
void live_h_35(double *state, double *unused, double *out_6691267644104565729);
void live_H_35(double *state, double *unused, double *out_9136679163340876704);
void live_h_32(double *state, double *unused, double *out_935793821218724225);
void live_H_32(double *state, double *unused, double *out_693008289712397714);
void live_h_13(double *state, double *unused, double *out_7244581276277651797);
void live_H_13(double *state, double *unused, double *out_3532118805189496743);
void live_h_14(double *state, double *unused, double *out_4393084026744099620);
void live_H_14(double *state, double *unused, double *out_8832264405276146878);
void live_h_33(double *state, double *unused, double *out_6248970935171980790);
void live_H_33(double *state, double *unused, double *out_5986122158702019100);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}