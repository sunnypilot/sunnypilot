#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_err_fun(double *nom_x, double *delta_x, double *out_8901306953069029009);
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_5676752390099238868);
void pose_H_mod_fun(double *state, double *out_906252113673065885);
void pose_f_fun(double *state, double dt, double *out_5850564288516734669);
void pose_F_fun(double *state, double dt, double *out_7498091432372823234);
void pose_h_4(double *state, double *unused, double *out_3808668925773133272);
void pose_H_4(double *state, double *unused, double *out_6754333920425024606);
void pose_h_10(double *state, double *unused, double *out_810924982525442876);
void pose_H_10(double *state, double *unused, double *out_653044011191738521);
void pose_h_13(double *state, double *unused, double *out_2288129125178979412);
void pose_H_13(double *state, double *unused, double *out_3542060095092691805);
void pose_h_14(double *state, double *unused, double *out_732552053741622262);
void pose_H_14(double *state, double *unused, double *out_2791093064085540077);
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt);
}