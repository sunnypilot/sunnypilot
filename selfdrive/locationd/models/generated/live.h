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
void live_H(double *in_vec, double *out_757562583052757246);
void live_err_fun(double *nom_x, double *delta_x, double *out_3871806392276481772);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_7967854238640231459);
void live_H_mod_fun(double *state, double *out_8261281829583298016);
void live_f_fun(double *state, double dt, double *out_4896127263541326294);
void live_F_fun(double *state, double dt, double *out_4168231684540016827);
void live_h_4(double *state, double *unused, double *out_4991721715502618263);
void live_H_4(double *state, double *unused, double *out_1060307404855628995);
void live_h_9(double *state, double *unused, double *out_5955690056654132601);
void live_H_9(double *state, double *unused, double *out_819117758226038350);
void live_h_10(double *state, double *unused, double *out_6748260789248896796);
void live_H_10(double *state, double *unused, double *out_6747811974431363251);
void live_h_12(double *state, double *unused, double *out_6103274577744846967);
void live_H_12(double *state, double *unused, double *out_3959149003176332800);
void live_h_35(double *state, double *unused, double *out_312039740995566217);
void live_H_35(double *state, double *unused, double *out_6704712035501346509);
void live_h_32(double *state, double *unused, double *out_7214231673700524842);
void live_H_32(double *state, double *unused, double *out_5940727666000592549);
void live_h_13(double *state, double *unused, double *out_1768116978492445216);
void live_H_13(double *state, double *unused, double *out_2823756408362652077);
void live_h_14(double *state, double *unused, double *out_5955690056654132601);
void live_H_14(double *state, double *unused, double *out_819117758226038350);
void live_h_33(double *state, double *unused, double *out_6006118663079489692);
void live_H_33(double *state, double *unused, double *out_8591475033569347503);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}