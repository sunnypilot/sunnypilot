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
void car_err_fun(double *nom_x, double *delta_x, double *out_6790105966704928287);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_8463553373470470506);
void car_H_mod_fun(double *state, double *out_728568532777367661);
void car_f_fun(double *state, double dt, double *out_8812121642862183985);
void car_F_fun(double *state, double dt, double *out_7320440814273975929);
void car_h_25(double *state, double *unused, double *out_7128581355117573680);
void car_H_25(double *state, double *unused, double *out_1907988392238058533);
void car_h_24(double *state, double *unused, double *out_1897761414026851607);
void car_H_24(double *state, double *unused, double *out_6238911909156001014);
void car_h_30(double *state, double *unused, double *out_6853387292833067791);
void car_H_30(double *state, double *unused, double *out_2037327339381298603);
void car_h_26(double *state, double *unused, double *out_6591683513215638180);
void car_H_26(double *state, double *unused, double *out_5649491711112114757);
void car_h_27(double *state, double *unused, double *out_4919121201178128790);
void car_H_27(double *state, double *unused, double *out_4212090651181723514);
void car_h_29(double *state, double *unused, double *out_8556570729432151140);
void car_H_29(double *state, double *unused, double *out_5925453378051274547);
void car_h_28(double *state, double *unused, double *out_3975611348276466355);
void car_H_28(double *state, double *unused, double *out_3961823106485948296);
void car_h_31(double *state, double *unused, double *out_5162715522751317807);
void car_H_31(double *state, double *unused, double *out_1877342430361098105);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}