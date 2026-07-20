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
void car_err_fun(double *nom_x, double *delta_x, double *out_4503132331689013745);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_5519222819843562437);
void car_H_mod_fun(double *state, double *out_99880963271144866);
void car_f_fun(double *state, double dt, double *out_4490574509847198287);
void car_F_fun(double *state, double dt, double *out_5588273031121660281);
void car_h_25(double *state, double *unused, double *out_4633670035125740311);
void car_H_25(double *state, double *unused, double *out_9153674884526169513);
void car_h_24(double *state, double *unused, double *out_4147879785077922233);
void car_H_24(double *state, double *unused, double *out_7067361405204513541);
void car_h_30(double *state, double *unused, double *out_8271119563379762661);
void car_H_30(double *state, double *unused, double *out_2376378847691765348);
void car_h_26(double *state, double *unused, double *out_749423849060713781);
void car_H_26(double *state, double *unused, double *out_5412171565652113289);
void car_h_27(double *state, double *unused, double *out_2801473399302960502);
void car_H_27(double *state, double *unused, double *out_6849572625582504532);
void car_h_29(double *state, double *unused, double *out_5173951242668943310);
void car_H_29(double *state, double *unused, double *out_8912176792012229989);
void car_h_28(double *state, double *unused, double *out_5994836064963036638);
void car_H_28(double *state, double *unused, double *out_6948546520446903738);
void car_h_31(double *state, double *unused, double *out_6352515274334922980);
void car_H_31(double *state, double *unused, double *out_9184320846403129941);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}