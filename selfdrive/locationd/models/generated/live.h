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
void live_H(double *in_vec, double *out_4936451531631853074);
void live_err_fun(double *nom_x, double *delta_x, double *out_1355019412731270491);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_3724306521271248657);
void live_H_mod_fun(double *state, double *out_4479928638218003069);
void live_f_fun(double *state, double dt, double *out_262283035690484694);
void live_F_fun(double *state, double dt, double *out_1325286187468660998);
void live_h_4(double *state, double *unused, double *out_7413195925170192470);
void live_H_4(double *state, double *unused, double *out_5482573754117837714);
void live_h_9(double *state, double *unused, double *out_3358148432970012198);
void live_H_9(double *state, double *unused, double *out_1804645181146609756);
void live_h_10(double *state, double *unused, double *out_8120918261206966651);
void live_H_10(double *state, double *unused, double *out_5268034709010358343);
void live_h_12(double *state, double *unused, double *out_3031181799664214664);
void live_H_12(double *state, double *unused, double *out_6582911942548980906);
void live_h_35(double *state, double *unused, double *out_8689434747193440267);
void live_H_35(double *state, double *unused, double *out_2115911696745230338);
void live_h_32(double *state, double *unused, double *out_4425036595514927008);
void live_H_32(double *state, double *unused, double *out_3760751206456129940);
void live_h_13(double *state, double *unused, double *out_6572175830757283971);
void live_H_13(double *state, double *unused, double *out_3762712114619565501);
void live_h_14(double *state, double *unused, double *out_3358148432970012198);
void live_H_14(double *state, double *unused, double *out_1804645181146609756);
void live_h_33(double *state, double *unused, double *out_30279681972433378);
void live_H_33(double *state, double *unused, double *out_8080674596528484091);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}