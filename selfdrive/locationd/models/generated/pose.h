#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_err_fun(double *nom_x, double *delta_x, double *out_1055807072610005846);
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_983516364171912274);
void pose_H_mod_fun(double *state, double *out_5307849917674294752);
void pose_f_fun(double *state, double dt, double *out_3929566488353935407);
void pose_F_fun(double *state, double dt, double *out_7175672084270467645);
void pose_h_4(double *state, double *unused, double *out_762986349532875001);
void pose_H_4(double *state, double *unused, double *out_4125909736121572372);
void pose_h_10(double *state, double *unused, double *out_895627576329681885);
void pose_H_10(double *state, double *unused, double *out_7661760800865717506);
void pose_h_13(double *state, double *unused, double *out_4233008290515268972);
void pose_H_13(double *state, double *unused, double *out_913635910789239571);
void pose_h_14(double *state, double *unused, double *out_5980176444970125081);
void pose_H_14(double *state, double *unused, double *out_162668879782087843);
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt);
}