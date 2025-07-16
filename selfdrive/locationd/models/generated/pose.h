#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_err_fun(double *nom_x, double *delta_x, double *out_5717304809118492246);
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_1297679808783662883);
void pose_H_mod_fun(double *state, double *out_173021604743855246);
void pose_f_fun(double *state, double dt, double *out_2557189771328893554);
void pose_F_fun(double *state, double dt, double *out_6231166407570578534);
void pose_h_4(double *state, double *unused, double *out_2859924915835927259);
void pose_H_4(double *state, double *unused, double *out_8565174627339133892);
void pose_h_10(double *state, double *unused, double *out_2013770797981180213);
void pose_H_10(double *state, double *unused, double *out_2161437616861568278);
void pose_h_13(double *state, double *unused, double *out_7197851880815921934);
void pose_H_13(double *state, double *unused, double *out_6669295621038084923);
void pose_h_14(double *state, double *unused, double *out_1386181666946440377);
void pose_H_14(double *state, double *unused, double *out_8130058100694250293);
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt);
}