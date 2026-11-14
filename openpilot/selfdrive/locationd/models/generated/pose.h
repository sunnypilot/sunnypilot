#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_err_fun(double *nom_x, double *delta_x, double *out_5308991872147398563);
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_5440750294658648606);
void pose_H_mod_fun(double *state, double *out_7655853576405724458);
void pose_f_fun(double *state, double dt, double *out_4136808220434975141);
void pose_F_fun(double *state, double dt, double *out_2537852680944861179);
void pose_h_4(double *state, double *unused, double *out_7730454059225088569);
void pose_H_4(double *state, double *unused, double *out_7019083287459919586);
void pose_h_10(double *state, double *unused, double *out_1910166407148471034);
void pose_H_10(double *state, double *unused, double *out_3315929574475692252);
void pose_h_13(double *state, double *unused, double *out_2907941445058093810);
void pose_H_13(double *state, double *unused, double *out_7593905322947108006);
void pose_h_14(double *state, double *unused, double *out_5410884076226838020);
void pose_H_14(double *state, double *unused, double *out_8344872353954259734);
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt);
}