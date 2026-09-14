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
void car_err_fun(double *nom_x, double *delta_x, double *out_2496243277963511837);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_8723072931307095264);
void car_H_mod_fun(double *state, double *out_2432465619939465173);
void car_f_fun(double *state, double dt, double *out_433459712136092591);
void car_F_fun(double *state, double dt, double *out_2989085374181927005);
void car_h_25(double *state, double *unused, double *out_7779026555707581006);
void car_H_25(double *state, double *unused, double *out_7597270765006040550);
void car_h_24(double *state, double *unused, double *out_1363944844356195076);
void car_H_24(double *state, double *unused, double *out_4648440628852349640);
void car_h_30(double *state, double *unused, double *out_7936213224058710151);
void car_H_30(double *state, double *unused, double *out_7726609712149280620);
void car_h_26(double *state, double *unused, double *out_1537171706644861005);
void car_H_26(double *state, double *unused, double *out_6940416700895728646);
void car_h_27(double *state, double *unused, double *out_3232574083573269797);
void car_H_27(double *state, double *unused, double *out_8545371049759846085);
void car_h_29(double *state, double *unused, double *out_3538261142777081139);
void car_H_29(double *state, double *unused, double *out_7216378367834888436);
void car_h_28(double *state, double *unused, double *out_2289064230671607362);
void car_H_28(double *state, double *unused, double *out_5252748096269562185);
void car_h_31(double *state, double *unused, double *out_8054220617992086895);
void car_H_31(double *state, double *unused, double *out_7566624803129080122);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}