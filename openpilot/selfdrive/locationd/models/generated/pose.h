#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_err_fun(double *nom_x, double *delta_x, double *out_7491504487925958906);
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_8173082431785614969);
void pose_H_mod_fun(double *state, double *out_3955896825213980969);
void pose_f_fun(double *state, double dt, double *out_6226431844178190638);
void pose_F_fun(double *state, double dt, double *out_5590858509180719260);
void pose_h_4(double *state, double *unused, double *out_8311116516369893334);
void pose_H_4(double *state, double *unused, double *out_1196621559825099766);
void pose_h_10(double *state, double *unused, double *out_8024633733467632830);
void pose_H_10(double *state, double *unused, double *out_9211636060607930666);
void pose_h_13(double *state, double *unused, double *out_5246243153983473200);
void pose_H_13(double *state, double *unused, double *out_4408895385157432567);
void pose_h_14(double *state, double *unused, double *out_2666716766060469740);
void pose_H_14(double *state, double *unused, double *out_5159862416164584295);
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt);
}