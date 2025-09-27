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
void car_err_fun(double *nom_x, double *delta_x, double *out_3560803852879544025);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_7615336851490548874);
void car_H_mod_fun(double *state, double *out_8478329586395114374);
void car_f_fun(double *state, double dt, double *out_3623878700035833994);
void car_F_fun(double *state, double dt, double *out_5787759682681306104);
void car_h_25(double *state, double *unused, double *out_5963614328607929912);
void car_H_25(double *state, double *unused, double *out_6445433837324945565);
void car_h_24(double *state, double *unused, double *out_5741338745664737274);
void car_H_24(double *state, double *unused, double *out_2887508238522622429);
void car_h_30(double *state, double *unused, double *out_4275632999018714854);
void car_H_30(double *state, double *unused, double *out_3927100878817696938);
void car_h_26(double *state, double *unused, double *out_6880038319827412505);
void car_H_26(double *state, double *unused, double *out_8259806917510549827);
void car_h_27(double *state, double *unused, double *out_5480367041308555925);
void car_H_27(double *state, double *unused, double *out_1703506807633753721);
void car_h_29(double *state, double *unused, double *out_9104693555972494039);
void car_H_29(double *state, double *unused, double *out_3416869534503304754);
void car_h_28(double *state, double *unused, double *out_2667814938038702542);
void car_H_28(double *state, double *unused, double *out_8499268551572835328);
void car_h_31(double *state, double *unused, double *out_5806427660256800767);
void car_H_31(double *state, double *unused, double *out_6414787875447985137);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}