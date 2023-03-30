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
void live_H(double *in_vec, double *out_1411274581290681856);
void live_err_fun(double *nom_x, double *delta_x, double *out_6771207196260069590);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_7704558692502514782);
void live_H_mod_fun(double *state, double *out_3132617661005846243);
void live_f_fun(double *state, double dt, double *out_3015935617370769610);
void live_F_fun(double *state, double dt, double *out_766393386454938038);
void live_h_4(double *state, double *unused, double *out_4410721155773680452);
void live_H_4(double *state, double *unused, double *out_7628001169045861891);
void live_h_9(double *state, double *unused, double *out_2031945012273343769);
void live_H_9(double *state, double *unused, double *out_340782233781414421);
void live_h_10(double *state, double *unused, double *out_1659405342571751664);
void live_H_10(double *state, double *unused, double *out_1619354407599027015);
void live_h_12(double *state, double *unused, double *out_3463172096804218820);
void live_H_12(double *state, double *unused, double *out_4437484527620956729);
void live_h_35(double *state, double *unused, double *out_430618380064533265);
void live_H_35(double *state, double *unused, double *out_4261339111673254515);
void live_h_32(double *state, double *unused, double *out_2573549883782041958);
void live_H_32(double *state, double *unused, double *out_4130174326732514046);
void live_h_13(double *state, double *unused, double *out_9169220267387108964);
void live_H_13(double *state, double *unused, double *out_7697282693947683554);
void live_h_14(double *state, double *unused, double *out_2031945012273343769);
void live_H_14(double *state, double *unused, double *out_340782233781414421);
void live_h_33(double *state, double *unused, double *out_3119208726560059184);
void live_H_33(double *state, double *unused, double *out_5935247181600459914);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}