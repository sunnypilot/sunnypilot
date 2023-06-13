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
void car_err_fun(double *nom_x, double *delta_x, double *out_7671677794621234283);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_3956625128940863804);
void car_H_mod_fun(double *state, double *out_1750402193623347166);
void car_f_fun(double *state, double dt, double *out_7591795441338291553);
void car_F_fun(double *state, double dt, double *out_1094147876976225567);
void car_h_25(double *state, double *unused, double *out_3240176429712773857);
void car_H_25(double *state, double *unused, double *out_4178007864366031569);
void car_h_24(double *state, double *unused, double *out_795643072989297307);
void car_H_24(double *state, double *unused, double *out_8067703529492358621);
void car_h_30(double *state, double *unused, double *out_5256484251550966135);
void car_H_30(double *state, double *unused, double *out_2738682477125585186);
void car_h_26(double *state, double *unused, double *out_4602097140353744073);
void car_H_26(double *state, double *unused, double *out_7919511183240087793);
void car_h_27(double *state, double *unused, double *out_7638128510994402869);
void car_H_27(double *state, double *unused, double *out_563919165325160275);
void car_h_29(double *state, double *unused, double *out_254810983890120490);
void car_H_29(double *state, double *unused, double *out_3248913821439977370);
void car_h_28(double *state, double *unused, double *out_5138476857617589391);
void car_H_28(double *state, double *unused, double *out_6231842578613921332);
void car_h_31(double *state, double *unused, double *out_9039453604025643456);
void car_H_31(double *state, double *unused, double *out_4147361902489071141);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}