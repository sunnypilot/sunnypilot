#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void car_update_25(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_24(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_30(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_26(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_27(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_29(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_28(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_31(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_err_fun(double *nom_x, double *delta_x, double *out_7216862993207776403);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_6378237758255440014);
void car_H_mod_fun(double *state, double *out_4368013663920627707);
void car_f_fun(double *state, double dt, double *out_640655310412688382);
void car_F_fun(double *state, double dt, double *out_9164188615644588775);
void car_h_25(double *state, double *unused, double *out_1790118014898518564);
void car_H_25(double *state, double *unused, double *out_7891062302565992855);
void car_h_24(double *state, double *unused, double *out_4114360205345828396);
void car_H_24(double *state, double *unused, double *out_5809172444177049727);
void car_h_30(double *state, double *unused, double *out_5888421313177890428);
void car_H_30(double *state, double *unused, double *out_5372729344058744228);
void car_h_26(double *state, double *unused, double *out_2851635261733557743);
void car_H_26(double *state, double *unused, double *out_4586536332805192254);
void car_h_27(double *state, double *unused, double *out_2733627867800180999);
void car_H_27(double *state, double *unused, double *out_3149135272874801011);
void car_h_29(double *state, double *unused, double *out_6159281243117812042);
void car_H_29(double *state, double *unused, double *out_4862497999744352044);
void car_h_28(double *state, double *unused, double *out_542219944947275590);
void car_H_28(double *state, double *unused, double *out_8501847056895668998);
void car_h_31(double *state, double *unused, double *out_8775353408056983867);
void car_H_31(double *state, double *unused, double *out_814387052054175602);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}