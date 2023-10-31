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
void live_H(double *in_vec, double *out_2038889705009881429);
void live_err_fun(double *nom_x, double *delta_x, double *out_1909062281342758361);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_9085916003939023559);
void live_H_mod_fun(double *state, double *out_2004617956117849814);
void live_f_fun(double *state, double dt, double *out_6569003873343181674);
void live_F_fun(double *state, double dt, double *out_9204401918535706304);
void live_h_4(double *state, double *unused, double *out_1152664288045785834);
void live_H_4(double *state, double *unused, double *out_490968432834082475);
void live_h_9(double *state, double *unused, double *out_7142367124321499696);
void live_H_9(double *state, double *unused, double *out_7778187368098529945);
void live_h_10(double *state, double *unused, double *out_3415287187935510862);
void live_H_10(double *state, double *unused, double *out_871707072305034635);
void live_h_12(double *state, double *unused, double *out_7219912438526087750);
void live_H_12(double *state, double *unused, double *out_5890289944208650521);
void live_h_35(double *state, double *unused, double *out_713142883830897031);
void live_H_35(double *state, double *unused, double *out_3144726911883636812);
void live_h_32(double *state, double *unused, double *out_7939864099077747077);
void live_H_32(double *state, double *unused, double *out_7485731687616743700);
void live_h_13(double *state, double *unused, double *out_6387757370702057616);
void live_H_13(double *state, double *unused, double *out_7799441889219766245);
void live_h_14(double *state, double *unused, double *out_7142367124321499696);
void live_H_14(double *state, double *unused, double *out_7778187368098529945);
void live_h_33(double *state, double *unused, double *out_3692354153322585856);
void live_H_33(double *state, double *unused, double *out_5830092755220792);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}