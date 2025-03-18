#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_err_fun(double *nom_x, double *delta_x, double *out_3059021723261949722);
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_6771718338208051804);
void pose_H_mod_fun(double *state, double *out_1014308954846494831);
void pose_f_fun(double *state, double dt, double *out_6438442720881406331);
void pose_F_fun(double *state, double dt, double *out_6531472760490035339);
void pose_h_4(double *state, double *unused, double *out_2496877672334565060);
void pose_H_4(double *state, double *unused, double *out_7942831634537215637);
void pose_h_10(double *state, double *unused, double *out_6821224095196569661);
void pose_H_10(double *state, double *unused, double *out_2541800970645913241);
void pose_h_13(double *state, double *unused, double *out_8366060029539452607);
void pose_H_13(double *state, double *unused, double *out_7291638613840003178);
void pose_h_14(double *state, double *unused, double *out_1084678045620217578);
void pose_H_14(double *state, double *unused, double *out_461685819257475213);
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt);
}