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
void car_err_fun(double *nom_x, double *delta_x, double *out_1803508141925397670);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_5333939896853221127);
void car_H_mod_fun(double *state, double *out_2557259414991129935);
void car_f_fun(double *state, double dt, double *out_3703379460047437807);
void car_F_fun(double *state, double dt, double *out_2019960334582999654);
void car_h_25(double *state, double *unused, double *out_8936958561179864516);
void car_H_25(double *state, double *unused, double *out_410100477713749523);
void car_h_24(double *state, double *unused, double *out_3389245233051640465);
void car_H_24(double *state, double *unused, double *out_8808578409926606868);
void car_h_30(double *state, double *unused, double *out_1055685910425815331);
void car_H_30(double *state, double *unused, double *out_4117595852413858675);
void car_h_26(double *state, double *unused, double *out_7718254645993696192);
void car_H_26(double *state, double *unused, double *out_3331402841160306701);
void car_h_27(double *state, double *unused, double *out_8333642676503386999);
void car_H_27(double *state, double *unused, double *out_6292359164214283586);
void car_h_29(double *state, double *unused, double *out_8058448614218881110);
void car_H_29(double *state, double *unused, double *out_3607364508099466491);
void car_h_28(double *state, double *unused, double *out_3714059879792315471);
void car_H_28(double *state, double *unused, double *out_8689763525168997065);
void car_h_31(double *state, double *unused, double *out_4838655262900492652);
void car_H_31(double *state, double *unused, double *out_3957610943393658177);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}