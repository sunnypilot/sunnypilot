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
void live_H(double *in_vec, double *out_4177709683089171457);
void live_err_fun(double *nom_x, double *delta_x, double *out_5407889575643092892);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_4882586415534734470);
void live_H_mod_fun(double *state, double *out_8956971761540353190);
void live_f_fun(double *state, double dt, double *out_887329842068110705);
void live_F_fun(double *state, double dt, double *out_5605343981307858209);
void live_h_4(double *state, double *unused, double *out_426777422164272670);
void live_H_4(double *state, double *unused, double *out_918598418246462164);
void live_h_9(double *state, double *unused, double *out_7323485185758897526);
void live_H_9(double *state, double *unused, double *out_677408771616871519);
void live_h_10(double *state, double *unused, double *out_513882067179901221);
void live_H_10(double *state, double *unused, double *out_6556574736836933006);
void live_h_12(double *state, double *unused, double *out_926958483110485324);
void live_H_12(double *state, double *unused, double *out_4100857989785499631);
void live_h_35(double *state, double *unused, double *out_4057350054272984831);
void live_H_35(double *state, double *unused, double *out_2448063639126145212);
void live_h_32(double *state, double *unused, double *out_4477022913046825892);
void live_H_32(double *state, double *unused, double *out_6533799327223068312);
void live_h_13(double *state, double *unused, double *out_1121824037711693177);
void live_H_13(double *state, double *unused, double *out_4358476608526819101);
void live_h_14(double *state, double *unused, double *out_7323485185758897526);
void live_H_14(double *state, double *unused, double *out_677408771616871519);
void live_h_33(double *state, double *unused, double *out_2849170436071411464);
void live_H_33(double *state, double *unused, double *out_5598620643765002816);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}