#pragma once
#include "rednose/helpers/common_ekf.h"
extern "C" {
void car_update_25(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_24(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_30(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_26(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_27(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_29(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_28(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_31(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_err_fun(double *nom_x, double *delta_x, double *out_7470397526871273149);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_6628002157851279603);
void car_H_mod_fun(double *state, double *out_338615810674868519);
void car_f_fun(double *state, double dt, double *out_3565074677649486182);
void car_F_fun(double *state, double dt, double *out_1768894250710066862);
void car_h_25(double *state, double *unused, double *out_5309084791442776367);
void car_H_25(double *state, double *unused, double *out_2366865651751345480);
void car_h_24(double *state, double *unused, double *out_4964929704142686901);
void car_H_24(double *state, double *unused, double *out_6861199534317849745);
void car_h_30(double *state, double *unused, double *out_6759716184071659534);
void car_H_30(double *state, double *unused, double *out_6894561981878953678);
void car_h_26(double *state, double *unused, double *out_6461120673802567135);
void car_H_26(double *state, double *unused, double *out_6108368970625401704);
void car_h_27(double *state, double *unused, double *out_1903562740631468860);
void car_H_27(double *state, double *unused, double *out_4670967910695010461);
void car_h_29(double *state, double *unused, double *out_1758042916410813889);
void car_H_29(double *state, double *unused, double *out_6384330637564561494);
void car_h_28(double *state, double *unused, double *out_2847072593533131295);
void car_H_28(double *state, double *unused, double *out_6980014419075459548);
void car_h_31(double *state, double *unused, double *out_858029248528357936);
void car_H_31(double *state, double *unused, double *out_6734577072858753180);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}