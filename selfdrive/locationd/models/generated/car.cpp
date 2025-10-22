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
void err_fun(double *nom_x, double *delta_x, double *out_8269169211827911365) {
   out_8269169211827911365[0] = delta_x[0] + nom_x[0];
   out_8269169211827911365[1] = delta_x[1] + nom_x[1];
   out_8269169211827911365[2] = delta_x[2] + nom_x[2];
   out_8269169211827911365[3] = delta_x[3] + nom_x[3];
   out_8269169211827911365[4] = delta_x[4] + nom_x[4];
   out_8269169211827911365[5] = delta_x[5] + nom_x[5];
   out_8269169211827911365[6] = delta_x[6] + nom_x[6];
   out_8269169211827911365[7] = delta_x[7] + nom_x[7];
   out_8269169211827911365[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_1061083252181456560) {
   out_1061083252181456560[0] = -nom_x[0] + true_x[0];
   out_1061083252181456560[1] = -nom_x[1] + true_x[1];
   out_1061083252181456560[2] = -nom_x[2] + true_x[2];
   out_1061083252181456560[3] = -nom_x[3] + true_x[3];
   out_1061083252181456560[4] = -nom_x[4] + true_x[4];
   out_1061083252181456560[5] = -nom_x[5] + true_x[5];
   out_1061083252181456560[6] = -nom_x[6] + true_x[6];
   out_1061083252181456560[7] = -nom_x[7] + true_x[7];
   out_1061083252181456560[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_6549540021929294116) {
   out_6549540021929294116[0] = 1.0;
   out_6549540021929294116[1] = 0.0;
   out_6549540021929294116[2] = 0.0;
   out_6549540021929294116[3] = 0.0;
   out_6549540021929294116[4] = 0.0;
   out_6549540021929294116[5] = 0.0;
   out_6549540021929294116[6] = 0.0;
   out_6549540021929294116[7] = 0.0;
   out_6549540021929294116[8] = 0.0;
   out_6549540021929294116[9] = 0.0;
   out_6549540021929294116[10] = 1.0;
   out_6549540021929294116[11] = 0.0;
   out_6549540021929294116[12] = 0.0;
   out_6549540021929294116[13] = 0.0;
   out_6549540021929294116[14] = 0.0;
   out_6549540021929294116[15] = 0.0;
   out_6549540021929294116[16] = 0.0;
   out_6549540021929294116[17] = 0.0;
   out_6549540021929294116[18] = 0.0;
   out_6549540021929294116[19] = 0.0;
   out_6549540021929294116[20] = 1.0;
   out_6549540021929294116[21] = 0.0;
   out_6549540021929294116[22] = 0.0;
   out_6549540021929294116[23] = 0.0;
   out_6549540021929294116[24] = 0.0;
   out_6549540021929294116[25] = 0.0;
   out_6549540021929294116[26] = 0.0;
   out_6549540021929294116[27] = 0.0;
   out_6549540021929294116[28] = 0.0;
   out_6549540021929294116[29] = 0.0;
   out_6549540021929294116[30] = 1.0;
   out_6549540021929294116[31] = 0.0;
   out_6549540021929294116[32] = 0.0;
   out_6549540021929294116[33] = 0.0;
   out_6549540021929294116[34] = 0.0;
   out_6549540021929294116[35] = 0.0;
   out_6549540021929294116[36] = 0.0;
   out_6549540021929294116[37] = 0.0;
   out_6549540021929294116[38] = 0.0;
   out_6549540021929294116[39] = 0.0;
   out_6549540021929294116[40] = 1.0;
   out_6549540021929294116[41] = 0.0;
   out_6549540021929294116[42] = 0.0;
   out_6549540021929294116[43] = 0.0;
   out_6549540021929294116[44] = 0.0;
   out_6549540021929294116[45] = 0.0;
   out_6549540021929294116[46] = 0.0;
   out_6549540021929294116[47] = 0.0;
   out_6549540021929294116[48] = 0.0;
   out_6549540021929294116[49] = 0.0;
   out_6549540021929294116[50] = 1.0;
   out_6549540021929294116[51] = 0.0;
   out_6549540021929294116[52] = 0.0;
   out_6549540021929294116[53] = 0.0;
   out_6549540021929294116[54] = 0.0;
   out_6549540021929294116[55] = 0.0;
   out_6549540021929294116[56] = 0.0;
   out_6549540021929294116[57] = 0.0;
   out_6549540021929294116[58] = 0.0;
   out_6549540021929294116[59] = 0.0;
   out_6549540021929294116[60] = 1.0;
   out_6549540021929294116[61] = 0.0;
   out_6549540021929294116[62] = 0.0;
   out_6549540021929294116[63] = 0.0;
   out_6549540021929294116[64] = 0.0;
   out_6549540021929294116[65] = 0.0;
   out_6549540021929294116[66] = 0.0;
   out_6549540021929294116[67] = 0.0;
   out_6549540021929294116[68] = 0.0;
   out_6549540021929294116[69] = 0.0;
   out_6549540021929294116[70] = 1.0;
   out_6549540021929294116[71] = 0.0;
   out_6549540021929294116[72] = 0.0;
   out_6549540021929294116[73] = 0.0;
   out_6549540021929294116[74] = 0.0;
   out_6549540021929294116[75] = 0.0;
   out_6549540021929294116[76] = 0.0;
   out_6549540021929294116[77] = 0.0;
   out_6549540021929294116[78] = 0.0;
   out_6549540021929294116[79] = 0.0;
   out_6549540021929294116[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_5904193651585035956) {
   out_5904193651585035956[0] = state[0];
   out_5904193651585035956[1] = state[1];
   out_5904193651585035956[2] = state[2];
   out_5904193651585035956[3] = state[3];
   out_5904193651585035956[4] = state[4];
   out_5904193651585035956[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8100000000000005*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_5904193651585035956[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_5904193651585035956[7] = state[7];
   out_5904193651585035956[8] = state[8];
}
void F_fun(double *state, double dt, double *out_8258638883296957904) {
   out_8258638883296957904[0] = 1;
   out_8258638883296957904[1] = 0;
   out_8258638883296957904[2] = 0;
   out_8258638883296957904[3] = 0;
   out_8258638883296957904[4] = 0;
   out_8258638883296957904[5] = 0;
   out_8258638883296957904[6] = 0;
   out_8258638883296957904[7] = 0;
   out_8258638883296957904[8] = 0;
   out_8258638883296957904[9] = 0;
   out_8258638883296957904[10] = 1;
   out_8258638883296957904[11] = 0;
   out_8258638883296957904[12] = 0;
   out_8258638883296957904[13] = 0;
   out_8258638883296957904[14] = 0;
   out_8258638883296957904[15] = 0;
   out_8258638883296957904[16] = 0;
   out_8258638883296957904[17] = 0;
   out_8258638883296957904[18] = 0;
   out_8258638883296957904[19] = 0;
   out_8258638883296957904[20] = 1;
   out_8258638883296957904[21] = 0;
   out_8258638883296957904[22] = 0;
   out_8258638883296957904[23] = 0;
   out_8258638883296957904[24] = 0;
   out_8258638883296957904[25] = 0;
   out_8258638883296957904[26] = 0;
   out_8258638883296957904[27] = 0;
   out_8258638883296957904[28] = 0;
   out_8258638883296957904[29] = 0;
   out_8258638883296957904[30] = 1;
   out_8258638883296957904[31] = 0;
   out_8258638883296957904[32] = 0;
   out_8258638883296957904[33] = 0;
   out_8258638883296957904[34] = 0;
   out_8258638883296957904[35] = 0;
   out_8258638883296957904[36] = 0;
   out_8258638883296957904[37] = 0;
   out_8258638883296957904[38] = 0;
   out_8258638883296957904[39] = 0;
   out_8258638883296957904[40] = 1;
   out_8258638883296957904[41] = 0;
   out_8258638883296957904[42] = 0;
   out_8258638883296957904[43] = 0;
   out_8258638883296957904[44] = 0;
   out_8258638883296957904[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_8258638883296957904[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_8258638883296957904[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_8258638883296957904[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_8258638883296957904[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_8258638883296957904[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_8258638883296957904[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_8258638883296957904[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_8258638883296957904[53] = -9.8100000000000005*dt;
   out_8258638883296957904[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_8258638883296957904[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_8258638883296957904[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_8258638883296957904[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_8258638883296957904[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_8258638883296957904[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_8258638883296957904[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_8258638883296957904[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_8258638883296957904[62] = 0;
   out_8258638883296957904[63] = 0;
   out_8258638883296957904[64] = 0;
   out_8258638883296957904[65] = 0;
   out_8258638883296957904[66] = 0;
   out_8258638883296957904[67] = 0;
   out_8258638883296957904[68] = 0;
   out_8258638883296957904[69] = 0;
   out_8258638883296957904[70] = 1;
   out_8258638883296957904[71] = 0;
   out_8258638883296957904[72] = 0;
   out_8258638883296957904[73] = 0;
   out_8258638883296957904[74] = 0;
   out_8258638883296957904[75] = 0;
   out_8258638883296957904[76] = 0;
   out_8258638883296957904[77] = 0;
   out_8258638883296957904[78] = 0;
   out_8258638883296957904[79] = 0;
   out_8258638883296957904[80] = 1;
}
void h_25(double *state, double *unused, double *out_7047596049686412249) {
   out_7047596049686412249[0] = state[6];
}
void H_25(double *state, double *unused, double *out_6993512226595592660) {
   out_6993512226595592660[0] = 0;
   out_6993512226595592660[1] = 0;
   out_6993512226595592660[2] = 0;
   out_6993512226595592660[3] = 0;
   out_6993512226595592660[4] = 0;
   out_6993512226595592660[5] = 0;
   out_6993512226595592660[6] = 1;
   out_6993512226595592660[7] = 0;
   out_6993512226595592660[8] = 0;
}
void h_24(double *state, double *unused, double *out_8355860068355601473) {
   out_8355860068355601473[0] = state[4];
   out_8355860068355601473[1] = state[5];
}
void H_24(double *state, double *unused, double *out_853841784278429402) {
   out_853841784278429402[0] = 0;
   out_853841784278429402[1] = 0;
   out_853841784278429402[2] = 0;
   out_853841784278429402[3] = 0;
   out_853841784278429402[4] = 1;
   out_853841784278429402[5] = 0;
   out_853841784278429402[6] = 0;
   out_853841784278429402[7] = 0;
   out_853841784278429402[8] = 0;
   out_853841784278429402[9] = 0;
   out_853841784278429402[10] = 0;
   out_853841784278429402[11] = 0;
   out_853841784278429402[12] = 0;
   out_853841784278429402[13] = 0;
   out_853841784278429402[14] = 1;
   out_853841784278429402[15] = 0;
   out_853841784278429402[16] = 0;
   out_853841784278429402[17] = 0;
}
void h_30(double *state, double *unused, double *out_276760823336061313) {
   out_276760823336061313[0] = state[4];
}
void H_30(double *state, double *unused, double *out_6925535516986350758) {
   out_6925535516986350758[0] = 0;
   out_6925535516986350758[1] = 0;
   out_6925535516986350758[2] = 0;
   out_6925535516986350758[3] = 0;
   out_6925535516986350758[4] = 1;
   out_6925535516986350758[5] = 0;
   out_6925535516986350758[6] = 0;
   out_6925535516986350758[7] = 0;
   out_6925535516986350758[8] = 0;
}
void h_26(double *state, double *unused, double *out_5239140821017354545) {
   out_5239140821017354545[0] = state[7];
}
void H_26(double *state, double *unused, double *out_7711728528239902732) {
   out_7711728528239902732[0] = 0;
   out_7711728528239902732[1] = 0;
   out_7711728528239902732[2] = 0;
   out_7711728528239902732[3] = 0;
   out_7711728528239902732[4] = 0;
   out_7711728528239902732[5] = 0;
   out_7711728528239902732[6] = 0;
   out_7711728528239902732[7] = 1;
   out_7711728528239902732[8] = 0;
}
void h_27(double *state, double *unused, double *out_7001195942741510355) {
   out_7001195942741510355[0] = state[3];
}
void H_27(double *state, double *unused, double *out_4750772205185925847) {
   out_4750772205185925847[0] = 0;
   out_4750772205185925847[1] = 0;
   out_4750772205185925847[2] = 0;
   out_4750772205185925847[3] = 1;
   out_4750772205185925847[4] = 0;
   out_4750772205185925847[5] = 0;
   out_4750772205185925847[6] = 0;
   out_4750772205185925847[7] = 0;
   out_4750772205185925847[8] = 0;
}
void h_29(double *state, double *unused, double *out_3906516822321848122) {
   out_3906516822321848122[0] = state[1];
}
void H_29(double *state, double *unused, double *out_7435766861300742942) {
   out_7435766861300742942[0] = 0;
   out_7435766861300742942[1] = 1;
   out_7435766861300742942[2] = 0;
   out_7435766861300742942[3] = 0;
   out_7435766861300742942[4] = 0;
   out_7435766861300742942[5] = 0;
   out_7435766861300742942[6] = 0;
   out_7435766861300742942[7] = 0;
   out_7435766861300742942[8] = 0;
}
void h_28(double *state, double *unused, double *out_8632996027698187878) {
   out_8632996027698187878[0] = state[0];
}
void H_28(double *state, double *unused, double *out_9047346940843482423) {
   out_9047346940843482423[0] = 1;
   out_9047346940843482423[1] = 0;
   out_9047346940843482423[2] = 0;
   out_9047346940843482423[3] = 0;
   out_9047346940843482423[4] = 0;
   out_9047346940843482423[5] = 0;
   out_9047346940843482423[6] = 0;
   out_9047346940843482423[7] = 0;
   out_9047346940843482423[8] = 0;
}
void h_31(double *state, double *unused, double *out_7204782718037541394) {
   out_7204782718037541394[0] = state[8];
}
void H_31(double *state, double *unused, double *out_7085520426006551256) {
   out_7085520426006551256[0] = 0;
   out_7085520426006551256[1] = 0;
   out_7085520426006551256[2] = 0;
   out_7085520426006551256[3] = 0;
   out_7085520426006551256[4] = 0;
   out_7085520426006551256[5] = 0;
   out_7085520426006551256[6] = 0;
   out_7085520426006551256[7] = 0;
   out_7085520426006551256[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_8269169211827911365) {
  err_fun(nom_x, delta_x, out_8269169211827911365);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_1061083252181456560) {
  inv_err_fun(nom_x, true_x, out_1061083252181456560);
}
void car_H_mod_fun(double *state, double *out_6549540021929294116) {
  H_mod_fun(state, out_6549540021929294116);
}
void car_f_fun(double *state, double dt, double *out_5904193651585035956) {
  f_fun(state,  dt, out_5904193651585035956);
}
void car_F_fun(double *state, double dt, double *out_8258638883296957904) {
  F_fun(state,  dt, out_8258638883296957904);
}
void car_h_25(double *state, double *unused, double *out_7047596049686412249) {
  h_25(state, unused, out_7047596049686412249);
}
void car_H_25(double *state, double *unused, double *out_6993512226595592660) {
  H_25(state, unused, out_6993512226595592660);
}
void car_h_24(double *state, double *unused, double *out_8355860068355601473) {
  h_24(state, unused, out_8355860068355601473);
}
void car_H_24(double *state, double *unused, double *out_853841784278429402) {
  H_24(state, unused, out_853841784278429402);
}
void car_h_30(double *state, double *unused, double *out_276760823336061313) {
  h_30(state, unused, out_276760823336061313);
}
void car_H_30(double *state, double *unused, double *out_6925535516986350758) {
  H_30(state, unused, out_6925535516986350758);
}
void car_h_26(double *state, double *unused, double *out_5239140821017354545) {
  h_26(state, unused, out_5239140821017354545);
}
void car_H_26(double *state, double *unused, double *out_7711728528239902732) {
  H_26(state, unused, out_7711728528239902732);
}
void car_h_27(double *state, double *unused, double *out_7001195942741510355) {
  h_27(state, unused, out_7001195942741510355);
}
void car_H_27(double *state, double *unused, double *out_4750772205185925847) {
  H_27(state, unused, out_4750772205185925847);
}
void car_h_29(double *state, double *unused, double *out_3906516822321848122) {
  h_29(state, unused, out_3906516822321848122);
}
void car_H_29(double *state, double *unused, double *out_7435766861300742942) {
  H_29(state, unused, out_7435766861300742942);
}
void car_h_28(double *state, double *unused, double *out_8632996027698187878) {
  h_28(state, unused, out_8632996027698187878);
}
void car_H_28(double *state, double *unused, double *out_9047346940843482423) {
  H_28(state, unused, out_9047346940843482423);
}
void car_h_31(double *state, double *unused, double *out_7204782718037541394) {
  h_31(state, unused, out_7204782718037541394);
}
void car_H_31(double *state, double *unused, double *out_7085520426006551256) {
  H_31(state, unused, out_7085520426006551256);
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
