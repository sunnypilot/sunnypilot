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
void car_err_fun(double *nom_x, double *delta_x, double *out_616676496519843540);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_9159640380644645045);
void car_H_mod_fun(double *state, double *out_3329662807632018400);
void car_f_fun(double *state, double dt, double *out_3004432371693856628);
void car_F_fun(double *state, double dt, double *out_4674607950146575611);
void car_h_25(double *state, double *unused, double *out_7961708134929802500);
void car_H_25(double *state, double *unused, double *out_7390534805731274448);
void car_h_24(double *state, double *unused, double *out_6293551899498467220);
void car_H_24(double *state, double *unused, double *out_3637817634301350275);
void car_h_30(double *state, double *unused, double *out_6847586410525726766);
void car_H_30(double *state, double *unused, double *out_2862838475603666250);
void car_h_26(double *state, double *unused, double *out_6597484395522979205);
void car_H_26(double *state, double *unused, double *out_3649031486857218224);
void car_h_27(double *state, double *unused, double *out_1767199018911056790);
void car_H_27(double *state, double *unused, double *out_5086432546787609467);
void car_h_29(double *state, double *unused, double *out_1845913142864881121);
void car_H_29(double *state, double *unused, double *out_3373069819918058434);
void car_h_28(double *state, double *unused, double *out_416945152400560748);
void car_H_28(double *state, double *unused, double *out_5336700091483384685);
void car_h_31(double *state, double *unused, double *out_770159022074290704);
void car_H_31(double *state, double *unused, double *out_3022823384623866748);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}