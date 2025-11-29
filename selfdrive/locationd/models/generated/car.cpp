#include "car.h"

namespace {
#define DIM 9
#define EDIM 9
#define MEDIM 9
typedef void (*Hfun)(double *, double *, double *);

double mass;

void set_mass(double x){ mass = x;}

double rotational_inertia;

void set_rotational_inertia(double x){ rotational_inertia = x;}

double center_to_front;

void set_center_to_front(double x){ center_to_front = x;}

double center_to_rear;

void set_center_to_rear(double x){ center_to_rear = x;}

double stiffness_front;

void set_stiffness_front(double x){ stiffness_front = x;}

double stiffness_rear;

void set_stiffness_rear(double x){ stiffness_rear = x;}
const static double MAHA_THRESH_25 = 3.8414588206941227;
const static double MAHA_THRESH_24 = 5.991464547107981;
const static double MAHA_THRESH_30 = 3.8414588206941227;
const static double MAHA_THRESH_26 = 3.8414588206941227;
const static double MAHA_THRESH_27 = 3.8414588206941227;
const static double MAHA_THRESH_29 = 3.8414588206941227;
const static double MAHA_THRESH_28 = 3.8414588206941227;
const static double MAHA_THRESH_31 = 3.8414588206941227;

/******************************************************************************
 *                      Code generated with SymPy 1.14.0                      *
 *                                                                            *
 *              See http://www.sympy.org/ for more information.               *
 *                                                                            *
 *                         This file is part of 'ekf'                         *
 ******************************************************************************/
void err_fun(double *nom_x, double *delta_x, double *out_8556571550800620063) {
   out_8556571550800620063[0] = delta_x[0] + nom_x[0];
   out_8556571550800620063[1] = delta_x[1] + nom_x[1];
   out_8556571550800620063[2] = delta_x[2] + nom_x[2];
   out_8556571550800620063[3] = delta_x[3] + nom_x[3];
   out_8556571550800620063[4] = delta_x[4] + nom_x[4];
   out_8556571550800620063[5] = delta_x[5] + nom_x[5];
   out_8556571550800620063[6] = delta_x[6] + nom_x[6];
   out_8556571550800620063[7] = delta_x[7] + nom_x[7];
   out_8556571550800620063[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_9079666833948885683) {
   out_9079666833948885683[0] = -nom_x[0] + true_x[0];
   out_9079666833948885683[1] = -nom_x[1] + true_x[1];
   out_9079666833948885683[2] = -nom_x[2] + true_x[2];
   out_9079666833948885683[3] = -nom_x[3] + true_x[3];
   out_9079666833948885683[4] = -nom_x[4] + true_x[4];
   out_9079666833948885683[5] = -nom_x[5] + true_x[5];
   out_9079666833948885683[6] = -nom_x[6] + true_x[6];
   out_9079666833948885683[7] = -nom_x[7] + true_x[7];
   out_9079666833948885683[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_7049774927416388908) {
   out_7049774927416388908[0] = 1.0;
   out_7049774927416388908[1] = 0.0;
   out_7049774927416388908[2] = 0.0;
   out_7049774927416388908[3] = 0.0;
   out_7049774927416388908[4] = 0.0;
   out_7049774927416388908[5] = 0.0;
   out_7049774927416388908[6] = 0.0;
   out_7049774927416388908[7] = 0.0;
   out_7049774927416388908[8] = 0.0;
   out_7049774927416388908[9] = 0.0;
   out_7049774927416388908[10] = 1.0;
   out_7049774927416388908[11] = 0.0;
   out_7049774927416388908[12] = 0.0;
   out_7049774927416388908[13] = 0.0;
   out_7049774927416388908[14] = 0.0;
   out_7049774927416388908[15] = 0.0;
   out_7049774927416388908[16] = 0.0;
   out_7049774927416388908[17] = 0.0;
   out_7049774927416388908[18] = 0.0;
   out_7049774927416388908[19] = 0.0;
   out_7049774927416388908[20] = 1.0;
   out_7049774927416388908[21] = 0.0;
   out_7049774927416388908[22] = 0.0;
   out_7049774927416388908[23] = 0.0;
   out_7049774927416388908[24] = 0.0;
   out_7049774927416388908[25] = 0.0;
   out_7049774927416388908[26] = 0.0;
   out_7049774927416388908[27] = 0.0;
   out_7049774927416388908[28] = 0.0;
   out_7049774927416388908[29] = 0.0;
   out_7049774927416388908[30] = 1.0;
   out_7049774927416388908[31] = 0.0;
   out_7049774927416388908[32] = 0.0;
   out_7049774927416388908[33] = 0.0;
   out_7049774927416388908[34] = 0.0;
   out_7049774927416388908[35] = 0.0;
   out_7049774927416388908[36] = 0.0;
   out_7049774927416388908[37] = 0.0;
   out_7049774927416388908[38] = 0.0;
   out_7049774927416388908[39] = 0.0;
   out_7049774927416388908[40] = 1.0;
   out_7049774927416388908[41] = 0.0;
   out_7049774927416388908[42] = 0.0;
   out_7049774927416388908[43] = 0.0;
   out_7049774927416388908[44] = 0.0;
   out_7049774927416388908[45] = 0.0;
   out_7049774927416388908[46] = 0.0;
   out_7049774927416388908[47] = 0.0;
   out_7049774927416388908[48] = 0.0;
   out_7049774927416388908[49] = 0.0;
   out_7049774927416388908[50] = 1.0;
   out_7049774927416388908[51] = 0.0;
   out_7049774927416388908[52] = 0.0;
   out_7049774927416388908[53] = 0.0;
   out_7049774927416388908[54] = 0.0;
   out_7049774927416388908[55] = 0.0;
   out_7049774927416388908[56] = 0.0;
   out_7049774927416388908[57] = 0.0;
   out_7049774927416388908[58] = 0.0;
   out_7049774927416388908[59] = 0.0;
   out_7049774927416388908[60] = 1.0;
   out_7049774927416388908[61] = 0.0;
   out_7049774927416388908[62] = 0.0;
   out_7049774927416388908[63] = 0.0;
   out_7049774927416388908[64] = 0.0;
   out_7049774927416388908[65] = 0.0;
   out_7049774927416388908[66] = 0.0;
   out_7049774927416388908[67] = 0.0;
   out_7049774927416388908[68] = 0.0;
   out_7049774927416388908[69] = 0.0;
   out_7049774927416388908[70] = 1.0;
   out_7049774927416388908[71] = 0.0;
   out_7049774927416388908[72] = 0.0;
   out_7049774927416388908[73] = 0.0;
   out_7049774927416388908[74] = 0.0;
   out_7049774927416388908[75] = 0.0;
   out_7049774927416388908[76] = 0.0;
   out_7049774927416388908[77] = 0.0;
   out_7049774927416388908[78] = 0.0;
   out_7049774927416388908[79] = 0.0;
   out_7049774927416388908[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_3420217845127717081) {
   out_3420217845127717081[0] = state[0];
   out_3420217845127717081[1] = state[1];
   out_3420217845127717081[2] = state[2];
   out_3420217845127717081[3] = state[3];
   out_3420217845127717081[4] = state[4];
   out_3420217845127717081[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8100000000000005*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_3420217845127717081[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_3420217845127717081[7] = state[7];
   out_3420217845127717081[8] = state[8];
}
void F_fun(double *state, double dt, double *out_9037712059141071569) {
   out_9037712059141071569[0] = 1;
   out_9037712059141071569[1] = 0;
   out_9037712059141071569[2] = 0;
   out_9037712059141071569[3] = 0;
   out_9037712059141071569[4] = 0;
   out_9037712059141071569[5] = 0;
   out_9037712059141071569[6] = 0;
   out_9037712059141071569[7] = 0;
   out_9037712059141071569[8] = 0;
   out_9037712059141071569[9] = 0;
   out_9037712059141071569[10] = 1;
   out_9037712059141071569[11] = 0;
   out_9037712059141071569[12] = 0;
   out_9037712059141071569[13] = 0;
   out_9037712059141071569[14] = 0;
   out_9037712059141071569[15] = 0;
   out_9037712059141071569[16] = 0;
   out_9037712059141071569[17] = 0;
   out_9037712059141071569[18] = 0;
   out_9037712059141071569[19] = 0;
   out_9037712059141071569[20] = 1;
   out_9037712059141071569[21] = 0;
   out_9037712059141071569[22] = 0;
   out_9037712059141071569[23] = 0;
   out_9037712059141071569[24] = 0;
   out_9037712059141071569[25] = 0;
   out_9037712059141071569[26] = 0;
   out_9037712059141071569[27] = 0;
   out_9037712059141071569[28] = 0;
   out_9037712059141071569[29] = 0;
   out_9037712059141071569[30] = 1;
   out_9037712059141071569[31] = 0;
   out_9037712059141071569[32] = 0;
   out_9037712059141071569[33] = 0;
   out_9037712059141071569[34] = 0;
   out_9037712059141071569[35] = 0;
   out_9037712059141071569[36] = 0;
   out_9037712059141071569[37] = 0;
   out_9037712059141071569[38] = 0;
   out_9037712059141071569[39] = 0;
   out_9037712059141071569[40] = 1;
   out_9037712059141071569[41] = 0;
   out_9037712059141071569[42] = 0;
   out_9037712059141071569[43] = 0;
   out_9037712059141071569[44] = 0;
   out_9037712059141071569[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_9037712059141071569[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_9037712059141071569[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_9037712059141071569[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_9037712059141071569[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_9037712059141071569[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_9037712059141071569[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_9037712059141071569[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_9037712059141071569[53] = -9.8100000000000005*dt;
   out_9037712059141071569[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_9037712059141071569[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_9037712059141071569[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_9037712059141071569[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_9037712059141071569[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_9037712059141071569[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_9037712059141071569[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_9037712059141071569[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_9037712059141071569[62] = 0;
   out_9037712059141071569[63] = 0;
   out_9037712059141071569[64] = 0;
   out_9037712059141071569[65] = 0;
   out_9037712059141071569[66] = 0;
   out_9037712059141071569[67] = 0;
   out_9037712059141071569[68] = 0;
   out_9037712059141071569[69] = 0;
   out_9037712059141071569[70] = 1;
   out_9037712059141071569[71] = 0;
   out_9037712059141071569[72] = 0;
   out_9037712059141071569[73] = 0;
   out_9037712059141071569[74] = 0;
   out_9037712059141071569[75] = 0;
   out_9037712059141071569[76] = 0;
   out_9037712059141071569[77] = 0;
   out_9037712059141071569[78] = 0;
   out_9037712059141071569[79] = 0;
   out_9037712059141071569[80] = 1;
}
void h_25(double *state, double *unused, double *out_720820836113428015) {
   out_720820836113428015[0] = state[6];
}
void H_25(double *state, double *unused, double *out_4899946186403132757) {
   out_4899946186403132757[0] = 0;
   out_4899946186403132757[1] = 0;
   out_4899946186403132757[2] = 0;
   out_4899946186403132757[3] = 0;
   out_4899946186403132757[4] = 0;
   out_4899946186403132757[5] = 0;
   out_4899946186403132757[6] = 1;
   out_4899946186403132757[7] = 0;
   out_4899946186403132757[8] = 0;
}
void h_24(double *state, double *unused, double *out_4072372206966036697) {
   out_4072372206966036697[0] = state[4];
   out_4072372206966036697[1] = state[5];
}
void H_24(double *state, double *unused, double *out_31131321375425905) {
   out_31131321375425905[0] = 0;
   out_31131321375425905[1] = 0;
   out_31131321375425905[2] = 0;
   out_31131321375425905[3] = 0;
   out_31131321375425905[4] = 1;
   out_31131321375425905[5] = 0;
   out_31131321375425905[6] = 0;
   out_31131321375425905[7] = 0;
   out_31131321375425905[8] = 0;
   out_31131321375425905[9] = 0;
   out_31131321375425905[10] = 0;
   out_31131321375425905[11] = 0;
   out_31131321375425905[12] = 0;
   out_31131321375425905[13] = 0;
   out_31131321375425905[14] = 1;
   out_31131321375425905[15] = 0;
   out_31131321375425905[16] = 0;
   out_31131321375425905[17] = 0;
}
void h_30(double *state, double *unused, double *out_2171452228742311182) {
   out_2171452228742311182[0] = state[4];
}
void H_30(double *state, double *unused, double *out_372249856275524559) {
   out_372249856275524559[0] = 0;
   out_372249856275524559[1] = 0;
   out_372249856275524559[2] = 0;
   out_372249856275524559[3] = 0;
   out_372249856275524559[4] = 1;
   out_372249856275524559[5] = 0;
   out_372249856275524559[6] = 0;
   out_372249856275524559[7] = 0;
   out_372249856275524559[8] = 0;
}
void h_26(double *state, double *unused, double *out_4084372493216736072) {
   out_4084372493216736072[0] = state[7];
}
void H_26(double *state, double *unused, double *out_1158442867529076533) {
   out_1158442867529076533[0] = 0;
   out_1158442867529076533[1] = 0;
   out_1158442867529076533[2] = 0;
   out_1158442867529076533[3] = 0;
   out_1158442867529076533[4] = 0;
   out_1158442867529076533[5] = 0;
   out_1158442867529076533[6] = 0;
   out_1158442867529076533[7] = 1;
   out_1158442867529076533[8] = 0;
}
void h_27(double *state, double *unused, double *out_2684701214697879492) {
   out_2684701214697879492[0] = state[3];
}
void H_27(double *state, double *unused, double *out_2595843927459467776) {
   out_2595843927459467776[0] = 0;
   out_2595843927459467776[1] = 0;
   out_2595843927459467776[2] = 0;
   out_2595843927459467776[3] = 1;
   out_2595843927459467776[4] = 0;
   out_2595843927459467776[5] = 0;
   out_2595843927459467776[6] = 0;
   out_2595843927459467776[7] = 0;
   out_2595843927459467776[8] = 0;
}
void h_29(double *state, double *unused, double *out_2830221038918534463) {
   out_2830221038918534463[0] = state[1];
}
void H_29(double *state, double *unused, double *out_882481200589916743) {
   out_882481200589916743[0] = 0;
   out_882481200589916743[1] = 1;
   out_882481200589916743[2] = 0;
   out_882481200589916743[3] = 0;
   out_882481200589916743[4] = 0;
   out_882481200589916743[5] = 0;
   out_882481200589916743[6] = 0;
   out_882481200589916743[7] = 0;
   out_882481200589916743[8] = 0;
}
void h_28(double *state, double *unused, double *out_7910608430533204439) {
   out_7910608430533204439[0] = state[0];
}
void H_28(double *state, double *unused, double *out_4199917816479613831) {
   out_4199917816479613831[0] = 1;
   out_4199917816479613831[1] = 0;
   out_4199917816479613831[2] = 0;
   out_4199917816479613831[3] = 0;
   out_4199917816479613831[4] = 0;
   out_4199917816479613831[5] = 0;
   out_4199917816479613831[6] = 0;
   out_4199917816479613831[7] = 0;
   out_4199917816479613831[8] = 0;
}
void h_31(double *state, double *unused, double *out_8602093486867477200) {
   out_8602093486867477200[0] = state[8];
}
void H_31(double *state, double *unused, double *out_532234765295725057) {
   out_532234765295725057[0] = 0;
   out_532234765295725057[1] = 0;
   out_532234765295725057[2] = 0;
   out_532234765295725057[3] = 0;
   out_532234765295725057[4] = 0;
   out_532234765295725057[5] = 0;
   out_532234765295725057[6] = 0;
   out_532234765295725057[7] = 0;
   out_532234765295725057[8] = 1;
}
#include <eigen3/Eigen/Dense>
#include <iostream>

typedef Eigen::Matrix<double, DIM, DIM, Eigen::RowMajor> DDM;
typedef Eigen::Matrix<double, EDIM, EDIM, Eigen::RowMajor> EEM;
typedef Eigen::Matrix<double, DIM, EDIM, Eigen::RowMajor> DEM;

void predict(double *in_x, double *in_P, double *in_Q, double dt) {
  typedef Eigen::Matrix<double, MEDIM, MEDIM, Eigen::RowMajor> RRM;

  double nx[DIM] = {0};
  double in_F[EDIM*EDIM] = {0};

  // functions from sympy
  f_fun(in_x, dt, nx);
  F_fun(in_x, dt, in_F);


  EEM F(in_F);
  EEM P(in_P);
  EEM Q(in_Q);

  RRM F_main = F.topLeftCorner(MEDIM, MEDIM);
  P.topLeftCorner(MEDIM, MEDIM) = (F_main * P.topLeftCorner(MEDIM, MEDIM)) * F_main.transpose();
  P.topRightCorner(MEDIM, EDIM - MEDIM) = F_main * P.topRightCorner(MEDIM, EDIM - MEDIM);
  P.bottomLeftCorner(EDIM - MEDIM, MEDIM) = P.bottomLeftCorner(EDIM - MEDIM, MEDIM) * F_main.transpose();

  P = P + dt*Q;

  // copy out state
  memcpy(in_x, nx, DIM * sizeof(double));
  memcpy(in_P, P.data(), EDIM * EDIM * sizeof(double));
}

// note: extra_args dim only correct when null space projecting
// otherwise 1
template <int ZDIM, int EADIM, bool MAHA_TEST>
void update(double *in_x, double *in_P, Hfun h_fun, Hfun H_fun, Hfun Hea_fun, double *in_z, double *in_R, double *in_ea, double MAHA_THRESHOLD) {
  typedef Eigen::Matrix<double, ZDIM, ZDIM, Eigen::RowMajor> ZZM;
  typedef Eigen::Matrix<double, ZDIM, DIM, Eigen::RowMajor> ZDM;
  typedef Eigen::Matrix<double, Eigen::Dynamic, EDIM, Eigen::RowMajor> XEM;
  //typedef Eigen::Matrix<double, EDIM, ZDIM, Eigen::RowMajor> EZM;
  typedef Eigen::Matrix<double, Eigen::Dynamic, 1> X1M;
  typedef Eigen::Matrix<double, Eigen::Dynamic, Eigen::Dynamic, Eigen::RowMajor> XXM;

  double in_hx[ZDIM] = {0};
  double in_H[ZDIM * DIM] = {0};
  double in_H_mod[EDIM * DIM] = {0};
  double delta_x[EDIM] = {0};
  double x_new[DIM] = {0};


  // state x, P
  Eigen::Matrix<double, ZDIM, 1> z(in_z);
  EEM P(in_P);
  ZZM pre_R(in_R);

  // functions from sympy
  h_fun(in_x, in_ea, in_hx);
  H_fun(in_x, in_ea, in_H);
  ZDM pre_H(in_H);

  // get y (y = z - hx)
  Eigen::Matrix<double, ZDIM, 1> pre_y(in_hx); pre_y = z - pre_y;
  X1M y; XXM H; XXM R;
  if (Hea_fun){
    typedef Eigen::Matrix<double, ZDIM, EADIM, Eigen::RowMajor> ZAM;
    double in_Hea[ZDIM * EADIM] = {0};
    Hea_fun(in_x, in_ea, in_Hea);
    ZAM Hea(in_Hea);
    XXM A = Hea.transpose().fullPivLu().kernel();


    y = A.transpose() * pre_y;
    H = A.transpose() * pre_H;
    R = A.transpose() * pre_R * A;
  } else {
    y = pre_y;
    H = pre_H;
    R = pre_R;
  }
  // get modified H
  H_mod_fun(in_x, in_H_mod);
  DEM H_mod(in_H_mod);
  XEM H_err = H * H_mod;

  // Do mahalobis distance test
  if (MAHA_TEST){
    XXM a = (H_err * P * H_err.transpose() + R).inverse();
    double maha_dist = y.transpose() * a * y;
    if (maha_dist > MAHA_THRESHOLD){
      R = 1.0e16 * R;
    }
  }

  // Outlier resilient weighting
  double weight = 1;//(1.5)/(1 + y.squaredNorm()/R.sum());

  // kalman gains and I_KH
  XXM S = ((H_err * P) * H_err.transpose()) + R/weight;
  XEM KT = S.fullPivLu().solve(H_err * P.transpose());
  //EZM K = KT.transpose(); TODO: WHY DOES THIS NOT COMPILE?
  //EZM K = S.fullPivLu().solve(H_err * P.transpose()).transpose();
  //std::cout << "Here is the matrix rot:\n" << K << std::endl;
  EEM I_KH = Eigen::Matrix<double, EDIM, EDIM>::Identity() - (KT.transpose() * H_err);

  // update state by injecting dx
  Eigen::Matrix<double, EDIM, 1> dx(delta_x);
  dx  = (KT.transpose() * y);
  memcpy(delta_x, dx.data(), EDIM * sizeof(double));
  err_fun(in_x, delta_x, x_new);
  Eigen::Matrix<double, DIM, 1> x(x_new);

  // update cov
  P = ((I_KH * P) * I_KH.transpose()) + ((KT.transpose() * R) * KT);

  // copy out state
  memcpy(in_x, x.data(), DIM * sizeof(double));
  memcpy(in_P, P.data(), EDIM * EDIM * sizeof(double));
  memcpy(in_z, y.data(), y.rows() * sizeof(double));
}




}
extern "C" {

void car_update_25(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<1, 3, 0>(in_x, in_P, h_25, H_25, NULL, in_z, in_R, in_ea, MAHA_THRESH_25);
}
void car_update_24(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<2, 3, 0>(in_x, in_P, h_24, H_24, NULL, in_z, in_R, in_ea, MAHA_THRESH_24);
}
void car_update_30(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<1, 3, 0>(in_x, in_P, h_30, H_30, NULL, in_z, in_R, in_ea, MAHA_THRESH_30);
}
void car_update_26(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<1, 3, 0>(in_x, in_P, h_26, H_26, NULL, in_z, in_R, in_ea, MAHA_THRESH_26);
}
void car_update_27(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<1, 3, 0>(in_x, in_P, h_27, H_27, NULL, in_z, in_R, in_ea, MAHA_THRESH_27);
}
void car_update_29(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<1, 3, 0>(in_x, in_P, h_29, H_29, NULL, in_z, in_R, in_ea, MAHA_THRESH_29);
}
void car_update_28(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<1, 3, 0>(in_x, in_P, h_28, H_28, NULL, in_z, in_R, in_ea, MAHA_THRESH_28);
}
void car_update_31(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<1, 3, 0>(in_x, in_P, h_31, H_31, NULL, in_z, in_R, in_ea, MAHA_THRESH_31);
}
void car_err_fun(double *nom_x, double *delta_x, double *out_8556571550800620063) {
  err_fun(nom_x, delta_x, out_8556571550800620063);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_9079666833948885683) {
  inv_err_fun(nom_x, true_x, out_9079666833948885683);
}
void car_H_mod_fun(double *state, double *out_7049774927416388908) {
  H_mod_fun(state, out_7049774927416388908);
}
void car_f_fun(double *state, double dt, double *out_3420217845127717081) {
  f_fun(state,  dt, out_3420217845127717081);
}
void car_F_fun(double *state, double dt, double *out_9037712059141071569) {
  F_fun(state,  dt, out_9037712059141071569);
}
void car_h_25(double *state, double *unused, double *out_720820836113428015) {
  h_25(state, unused, out_720820836113428015);
}
void car_H_25(double *state, double *unused, double *out_4899946186403132757) {
  H_25(state, unused, out_4899946186403132757);
}
void car_h_24(double *state, double *unused, double *out_4072372206966036697) {
  h_24(state, unused, out_4072372206966036697);
}
void car_H_24(double *state, double *unused, double *out_31131321375425905) {
  H_24(state, unused, out_31131321375425905);
}
void car_h_30(double *state, double *unused, double *out_2171452228742311182) {
  h_30(state, unused, out_2171452228742311182);
}
void car_H_30(double *state, double *unused, double *out_372249856275524559) {
  H_30(state, unused, out_372249856275524559);
}
void car_h_26(double *state, double *unused, double *out_4084372493216736072) {
  h_26(state, unused, out_4084372493216736072);
}
void car_H_26(double *state, double *unused, double *out_1158442867529076533) {
  H_26(state, unused, out_1158442867529076533);
}
void car_h_27(double *state, double *unused, double *out_2684701214697879492) {
  h_27(state, unused, out_2684701214697879492);
}
void car_H_27(double *state, double *unused, double *out_2595843927459467776) {
  H_27(state, unused, out_2595843927459467776);
}
void car_h_29(double *state, double *unused, double *out_2830221038918534463) {
  h_29(state, unused, out_2830221038918534463);
}
void car_H_29(double *state, double *unused, double *out_882481200589916743) {
  H_29(state, unused, out_882481200589916743);
}
void car_h_28(double *state, double *unused, double *out_7910608430533204439) {
  h_28(state, unused, out_7910608430533204439);
}
void car_H_28(double *state, double *unused, double *out_4199917816479613831) {
  H_28(state, unused, out_4199917816479613831);
}
void car_h_31(double *state, double *unused, double *out_8602093486867477200) {
  h_31(state, unused, out_8602093486867477200);
}
void car_H_31(double *state, double *unused, double *out_532234765295725057) {
  H_31(state, unused, out_532234765295725057);
}
void car_predict(double *in_x, double *in_P, double *in_Q, double dt) {
  predict(in_x, in_P, in_Q, dt);
}
void car_set_mass(double x) {
  set_mass(x);
}
void car_set_rotational_inertia(double x) {
  set_rotational_inertia(x);
}
void car_set_center_to_front(double x) {
  set_center_to_front(x);
}
void car_set_center_to_rear(double x) {
  set_center_to_rear(x);
}
void car_set_stiffness_front(double x) {
  set_stiffness_front(x);
}
void car_set_stiffness_rear(double x) {
  set_stiffness_rear(x);
}
}

const EKF car = {
  .name = "car",
  .kinds = { 25, 24, 30, 26, 27, 29, 28, 31 },
  .feature_kinds = {  },
  .f_fun = car_f_fun,
  .F_fun = car_F_fun,
  .err_fun = car_err_fun,
  .inv_err_fun = car_inv_err_fun,
  .H_mod_fun = car_H_mod_fun,
  .predict = car_predict,
  .hs = {
    { 25, car_h_25 },
    { 24, car_h_24 },
    { 30, car_h_30 },
    { 26, car_h_26 },
    { 27, car_h_27 },
    { 29, car_h_29 },
    { 28, car_h_28 },
    { 31, car_h_31 },
  },
  .Hs = {
    { 25, car_H_25 },
    { 24, car_H_24 },
    { 30, car_H_30 },
    { 26, car_H_26 },
    { 27, car_H_27 },
    { 29, car_H_29 },
    { 28, car_H_28 },
    { 31, car_H_31 },
  },
  .updates = {
    { 25, car_update_25 },
    { 24, car_update_24 },
    { 30, car_update_30 },
    { 26, car_update_26 },
    { 27, car_update_27 },
    { 29, car_update_29 },
    { 28, car_update_28 },
    { 31, car_update_31 },
  },
  .Hes = {
  },
  .sets = {
    { "mass", car_set_mass },
    { "rotational_inertia", car_set_rotational_inertia },
    { "center_to_front", car_set_center_to_front },
    { "center_to_rear", car_set_center_to_rear },
    { "stiffness_front", car_set_stiffness_front },
    { "stiffness_rear", car_set_stiffness_rear },
  },
  .extra_routines = {
  },
};

ekf_lib_init(car)
