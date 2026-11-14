#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void live_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_9(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_12(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_35(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_32(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_33(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_H(double *in_vec, double *out_8536236811475430067);
void live_err_fun(double *nom_x, double *delta_x, double *out_4614868058485758139);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_8573554928028298681);
void live_H_mod_fun(double *state, double *out_6128852447133223565);
void live_f_fun(double *state, double dt, double *out_7195534889995166041);
void live_F_fun(double *state, double dt, double *out_9012508306389018670);
void live_h_4(double *state, double *unused, double *out_2657657745771735915);
void live_H_4(double *state, double *unused, double *out_1457735078816209632);
void live_h_9(double *state, double *unused, double *out_181525824636861445);
void live_H_9(double *state, double *unused, double *out_8744954014080657102);
void live_h_10(double *state, double *unused, double *out_2940864223365932608);
void live_H_10(double *state, double *unused, double *out_6591157835936482265);
void live_h_12(double *state, double *unused, double *out_830811219903448800);
void live_H_12(double *state, double *unused, double *out_4923523298226523364);
void live_h_35(double *state, double *unused, double *out_1177115113523305926);
void live_H_35(double *state, double *unused, double *out_2177960265901509655);
void live_h_32(double *state, double *unused, double *out_8970203849717307468);
void live_H_32(double *state, double *unused, double *out_5493453269239321848);
void live_h_13(double *state, double *unused, double *out_1337448462981849436);
void live_H_13(double *state, double *unused, double *out_2400089242629978824);
void live_h_14(double *state, double *unused, double *out_181525824636861445);
void live_H_14(double *state, double *unused, double *out_8744954014080657102);
void live_h_33(double *state, double *unused, double *out_3078698583527751553);
void live_H_33(double *state, double *unused, double *out_972596738737347949);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}