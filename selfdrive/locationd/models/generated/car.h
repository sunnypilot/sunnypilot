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
void car_err_fun(double *nom_x, double *delta_x, double *out_1452165264433778352);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_9135951192458516155);
void car_H_mod_fun(double *state, double *out_3307709395632443617);
void car_f_fun(double *state, double dt, double *out_901337125042991402);
void car_F_fun(double *state, double dt, double *out_6056477044377128709);
void car_h_25(double *state, double *unused, double *out_4706993825862034863);
void car_H_25(double *state, double *unused, double *out_4613628637341416188);
void car_h_24(double *state, double *unused, double *out_4084205169702521809);
void car_H_24(double *state, double *unused, double *out_8171554236143739324);
void car_h_30(double *state, double *unused, double *out_4746632271668782499);
void car_H_30(double *state, double *unused, double *out_7131961595848664815);
void car_h_26(double *state, double *unused, double *out_896097599412174336);
void car_H_26(double *state, double *unused, double *out_872125318467359964);
void car_h_27(double *state, double *unused, double *out_8513843032012191806);
void car_H_27(double *state, double *unused, double *out_2088831004586616921);
void car_h_29(double *state, double *unused, double *out_2150249053710375945);
void car_H_29(double *state, double *unused, double *out_596163651528200174);
void car_h_28(double *state, double *unused, double *out_4115890950730562794);
void car_H_28(double *state, double *unused, double *out_2559793923093526425);
void car_h_31(double *state, double *unused, double *out_5976484991026844312);
void car_H_31(double *state, double *unused, double *out_245917216234008488);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}