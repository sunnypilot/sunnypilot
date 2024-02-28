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
void car_err_fun(double *nom_x, double *delta_x, double *out_7619292515865737175);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_5452062773601768243);
void car_H_mod_fun(double *state, double *out_7725418025905253046);
void car_f_fun(double *state, double dt, double *out_1475289048643592209);
void car_F_fun(double *state, double dt, double *out_1545992405806302656);
void car_h_25(double *state, double *unused, double *out_7361177615809799200);
void car_H_25(double *state, double *unused, double *out_8815050834348377649);
void car_h_24(double *state, double *unused, double *out_5817420711568356655);
void car_H_24(double *state, double *unused, double *out_7402022586309968812);
void car_h_30(double *state, double *unused, double *out_590342389459448264);
void car_H_30(double *state, double *unused, double *out_6296717875841129022);
void car_h_26(double *state, double *unused, double *out_4411330878201397381);
void car_H_26(double *state, double *unused, double *out_5890189920487117743);
void car_h_27(double *state, double *unused, double *out_6417667762908136765);
void car_H_27(double *state, double *unused, double *out_7327590980417508986);
void car_h_29(double *state, double *unused, double *out_5592015657120293909);
void car_H_29(double *state, double *unused, double *out_5786486531526736838);
void car_h_28(double *state, double *unused, double *out_7631124229519785839);
void car_H_28(double *state, double *unused, double *out_7577858525113284204);
void car_h_31(double *state, double *unused, double *out_7518364284160928345);
void car_H_31(double *state, double *unused, double *out_5263981818253766267);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}