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
void car_err_fun(double *nom_x, double *delta_x, double *out_974266586704450606);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_5405916937632846827);
void car_H_mod_fun(double *state, double *out_1988421079300520544);
void car_f_fun(double *state, double dt, double *out_3725388884411746145);
void car_F_fun(double *state, double dt, double *out_2674620274016128632);
void car_h_25(double *state, double *unused, double *out_5158729862070967329);
void car_H_25(double *state, double *unused, double *out_1534559570688971133);
void car_h_24(double *state, double *unused, double *out_3236043973782204970);
void car_H_24(double *state, double *unused, double *out_5092485169491294269);
void car_h_30(double *state, double *unused, double *out_1218573841245160863);
void car_H_30(double *state, double *unused, double *out_2993136759438637065);
void car_h_26(double *state, double *unused, double *out_8431860768198393613);
void car_H_26(double *state, double *unused, double *out_2206943748185085091);
void car_h_27(double *state, double *unused, double *out_6102239714972629764);
void car_H_27(double *state, double *unused, double *out_769542688254693848);
void car_h_29(double *state, double *unused, double *out_7617615358659010009);
void car_H_29(double *state, double *unused, double *out_2482905415124244881);
void car_h_28(double *state, double *unused, double *out_1100566447311784119);
void car_H_28(double *state, double *unused, double *out_519275143558918630);
void car_h_31(double *state, double *unused, double *out_2604535394749705112);
void car_H_31(double *state, double *unused, double *out_1565205532565931561);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}