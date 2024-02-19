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
void car_err_fun(double *nom_x, double *delta_x, double *out_7179596139758080413);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_2615111515505904601);
void car_H_mod_fun(double *state, double *out_8585370806554949128);
void car_f_fun(double *state, double dt, double *out_206262983803821674);
void car_F_fun(double *state, double dt, double *out_2052198398990982001);
void car_h_25(double *state, double *unused, double *out_8428502641983275766);
void car_H_25(double *state, double *unused, double *out_6836289276866676448);
void car_h_24(double *state, double *unused, double *out_557687457453017340);
void car_H_24(double *state, double *unused, double *out_6439643972512816953);
void car_h_30(double *state, double *unused, double *out_1609000481154498631);
void car_H_30(double *state, double *unused, double *out_9092121838335626541);
void car_h_26(double *state, double *unused, double *out_7864825203113545885);
void car_H_26(double *state, double *unused, double *out_3094785957992620224);
void car_h_27(double *state, double *unused, double *out_4151277612470839713);
void car_H_27(double *state, double *unused, double *out_7179858923573500164);
void car_h_29(double *state, double *unused, double *out_6610673748815344276);
void car_H_29(double *state, double *unused, double *out_8581890494021234357);
void car_h_28(double *state, double *unused, double *out_4645031851795157427);
void car_H_28(double *state, double *unused, double *out_4782454562618786685);
void car_h_31(double *state, double *unused, double *out_1613919571485492219);
void car_H_31(double *state, double *unused, double *out_2468577855759268748);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}