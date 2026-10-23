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
void car_err_fun(double *nom_x, double *delta_x, double *out_3585265450871354510);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_4534440969468340130);
void car_H_mod_fun(double *state, double *out_7815971298073658297);
void car_f_fun(double *state, double dt, double *out_3011916394083426809);
void car_F_fun(double *state, double dt, double *out_4768916904116545459);
void car_h_25(double *state, double *unused, double *out_8627167620031889565);
void car_H_25(double *state, double *unused, double *out_1719062931467283681);
void car_h_24(double *state, double *unused, double *out_5179238137807796494);
void car_H_24(double *state, double *unused, double *out_453586667538215885);
void car_h_30(double *state, double *unused, double *out_4528864321752517701);
void car_H_30(double *state, double *unused, double *out_4237395889974532308);
void car_h_26(double *state, double *unused, double *out_5472374174654180136);
void car_H_26(double *state, double *unused, double *out_2022440387406772543);
void car_h_27(double *state, double *unused, double *out_2749092444325053967);
void car_H_27(double *state, double *unused, double *out_6460989961158475525);
void car_h_29(double *state, double *unused, double *out_5132180206428995218);
void car_H_29(double *state, double *unused, double *out_4747627234288924492);
void car_h_28(double *state, double *unused, double *out_9148133961738903113);
void car_H_28(double *state, double *unused, double *out_334771782780606082);
void car_h_31(double *state, double *unused, double *out_745894969277840380);
void car_H_31(double *state, double *unused, double *out_2648648489640124019);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}