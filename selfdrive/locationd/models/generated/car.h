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
void car_err_fun(double *nom_x, double *delta_x, double *out_218205740670826108);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_4568867566118868017);
void car_H_mod_fun(double *state, double *out_5579606029964835433);
void car_f_fun(double *state, double dt, double *out_661179480090036700);
void car_F_fun(double *state, double dt, double *out_3757571913489682424);
void car_h_25(double *state, double *unused, double *out_6425695131840469157);
void car_H_25(double *state, double *unused, double *out_3708933076406995603);
void car_h_24(double *state, double *unused, double *out_6311602043493232022);
void car_H_24(double *state, double *unused, double *out_7594207551456324474);
void car_h_30(double *state, double *unused, double *out_4257783685048410018);
void car_H_30(double *state, double *unused, double *out_818763253720612595);
void car_h_26(double *state, double *unused, double *out_4927687678159242457);
void car_H_26(double *state, double *unused, double *out_32570242467060621);
void car_h_27(double *state, double *unused, double *out_8840331268697770696);
void car_H_27(double *state, double *unused, double *out_1404830817463330622);
void car_h_29(double *state, double *unused, double *out_3314273832146747583);
void car_H_29(double *state, double *unused, double *out_308531909406220411);
void car_h_28(double *state, double *unused, double *out_3359961747551607452);
void car_H_28(double *state, double *unused, double *out_5390930926475750985);
void car_h_31(double *state, double *unused, double *out_6465333577647216793);
void car_H_31(double *state, double *unused, double *out_658778344700412097);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}