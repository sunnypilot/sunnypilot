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
 *                       Code generated with SymPy 1.12                       *
 *                                                                            *
 *              See http://www.sympy.org/ for more information.               *
 *                                                                            *
 *                         This file is part of 'ekf'                         *
 ******************************************************************************/
void err_fun(double *nom_x, double *delta_x, double *out_3451169381060055315) {
   out_3451169381060055315[0] = delta_x[0] + nom_x[0];
   out_3451169381060055315[1] = delta_x[1] + nom_x[1];
   out_3451169381060055315[2] = delta_x[2] + nom_x[2];
   out_3451169381060055315[3] = delta_x[3] + nom_x[3];
   out_3451169381060055315[4] = delta_x[4] + nom_x[4];
   out_3451169381060055315[5] = delta_x[5] + nom_x[5];
   out_3451169381060055315[6] = delta_x[6] + nom_x[6];
   out_3451169381060055315[7] = delta_x[7] + nom_x[7];
   out_3451169381060055315[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_7186137212168118329) {
   out_7186137212168118329[0] = -nom_x[0] + true_x[0];
   out_7186137212168118329[1] = -nom_x[1] + true_x[1];
   out_7186137212168118329[2] = -nom_x[2] + true_x[2];
   out_7186137212168118329[3] = -nom_x[3] + true_x[3];
   out_7186137212168118329[4] = -nom_x[4] + true_x[4];
   out_7186137212168118329[5] = -nom_x[5] + true_x[5];
   out_7186137212168118329[6] = -nom_x[6] + true_x[6];
   out_7186137212168118329[7] = -nom_x[7] + true_x[7];
   out_7186137212168118329[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_7616985092703441005) {
   out_7616985092703441005[0] = 1.0;
   out_7616985092703441005[1] = 0;
   out_7616985092703441005[2] = 0;
   out_7616985092703441005[3] = 0;
   out_7616985092703441005[4] = 0;
   out_7616985092703441005[5] = 0;
   out_7616985092703441005[6] = 0;
   out_7616985092703441005[7] = 0;
   out_7616985092703441005[8] = 0;
   out_7616985092703441005[9] = 0;
   out_7616985092703441005[10] = 1.0;
   out_7616985092703441005[11] = 0;
   out_7616985092703441005[12] = 0;
   out_7616985092703441005[13] = 0;
   out_7616985092703441005[14] = 0;
   out_7616985092703441005[15] = 0;
   out_7616985092703441005[16] = 0;
   out_7616985092703441005[17] = 0;
   out_7616985092703441005[18] = 0;
   out_7616985092703441005[19] = 0;
   out_7616985092703441005[20] = 1.0;
   out_7616985092703441005[21] = 0;
   out_7616985092703441005[22] = 0;
   out_7616985092703441005[23] = 0;
   out_7616985092703441005[24] = 0;
   out_7616985092703441005[25] = 0;
   out_7616985092703441005[26] = 0;
   out_7616985092703441005[27] = 0;
   out_7616985092703441005[28] = 0;
   out_7616985092703441005[29] = 0;
   out_7616985092703441005[30] = 1.0;
   out_7616985092703441005[31] = 0;
   out_7616985092703441005[32] = 0;
   out_7616985092703441005[33] = 0;
   out_7616985092703441005[34] = 0;
   out_7616985092703441005[35] = 0;
   out_7616985092703441005[36] = 0;
   out_7616985092703441005[37] = 0;
   out_7616985092703441005[38] = 0;
   out_7616985092703441005[39] = 0;
   out_7616985092703441005[40] = 1.0;
   out_7616985092703441005[41] = 0;
   out_7616985092703441005[42] = 0;
   out_7616985092703441005[43] = 0;
   out_7616985092703441005[44] = 0;
   out_7616985092703441005[45] = 0;
   out_7616985092703441005[46] = 0;
   out_7616985092703441005[47] = 0;
   out_7616985092703441005[48] = 0;
   out_7616985092703441005[49] = 0;
   out_7616985092703441005[50] = 1.0;
   out_7616985092703441005[51] = 0;
   out_7616985092703441005[52] = 0;
   out_7616985092703441005[53] = 0;
   out_7616985092703441005[54] = 0;
   out_7616985092703441005[55] = 0;
   out_7616985092703441005[56] = 0;
   out_7616985092703441005[57] = 0;
   out_7616985092703441005[58] = 0;
   out_7616985092703441005[59] = 0;
   out_7616985092703441005[60] = 1.0;
   out_7616985092703441005[61] = 0;
   out_7616985092703441005[62] = 0;
   out_7616985092703441005[63] = 0;
   out_7616985092703441005[64] = 0;
   out_7616985092703441005[65] = 0;
   out_7616985092703441005[66] = 0;
   out_7616985092703441005[67] = 0;
   out_7616985092703441005[68] = 0;
   out_7616985092703441005[69] = 0;
   out_7616985092703441005[70] = 1.0;
   out_7616985092703441005[71] = 0;
   out_7616985092703441005[72] = 0;
   out_7616985092703441005[73] = 0;
   out_7616985092703441005[74] = 0;
   out_7616985092703441005[75] = 0;
   out_7616985092703441005[76] = 0;
   out_7616985092703441005[77] = 0;
   out_7616985092703441005[78] = 0;
   out_7616985092703441005[79] = 0;
   out_7616985092703441005[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_5673807216349312269) {
   out_5673807216349312269[0] = state[0];
   out_5673807216349312269[1] = state[1];
   out_5673807216349312269[2] = state[2];
   out_5673807216349312269[3] = state[3];
   out_5673807216349312269[4] = state[4];
   out_5673807216349312269[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8000000000000007*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_5673807216349312269[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_5673807216349312269[7] = state[7];
   out_5673807216349312269[8] = state[8];
}
void F_fun(double *state, double dt, double *out_6905028213774737392) {
   out_6905028213774737392[0] = 1;
   out_6905028213774737392[1] = 0;
   out_6905028213774737392[2] = 0;
   out_6905028213774737392[3] = 0;
   out_6905028213774737392[4] = 0;
   out_6905028213774737392[5] = 0;
   out_6905028213774737392[6] = 0;
   out_6905028213774737392[7] = 0;
   out_6905028213774737392[8] = 0;
   out_6905028213774737392[9] = 0;
   out_6905028213774737392[10] = 1;
   out_6905028213774737392[11] = 0;
   out_6905028213774737392[12] = 0;
   out_6905028213774737392[13] = 0;
   out_6905028213774737392[14] = 0;
   out_6905028213774737392[15] = 0;
   out_6905028213774737392[16] = 0;
   out_6905028213774737392[17] = 0;
   out_6905028213774737392[18] = 0;
   out_6905028213774737392[19] = 0;
   out_6905028213774737392[20] = 1;
   out_6905028213774737392[21] = 0;
   out_6905028213774737392[22] = 0;
   out_6905028213774737392[23] = 0;
   out_6905028213774737392[24] = 0;
   out_6905028213774737392[25] = 0;
   out_6905028213774737392[26] = 0;
   out_6905028213774737392[27] = 0;
   out_6905028213774737392[28] = 0;
   out_6905028213774737392[29] = 0;
   out_6905028213774737392[30] = 1;
   out_6905028213774737392[31] = 0;
   out_6905028213774737392[32] = 0;
   out_6905028213774737392[33] = 0;
   out_6905028213774737392[34] = 0;
   out_6905028213774737392[35] = 0;
   out_6905028213774737392[36] = 0;
   out_6905028213774737392[37] = 0;
   out_6905028213774737392[38] = 0;
   out_6905028213774737392[39] = 0;
   out_6905028213774737392[40] = 1;
   out_6905028213774737392[41] = 0;
   out_6905028213774737392[42] = 0;
   out_6905028213774737392[43] = 0;
   out_6905028213774737392[44] = 0;
   out_6905028213774737392[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_6905028213774737392[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_6905028213774737392[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_6905028213774737392[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_6905028213774737392[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_6905028213774737392[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_6905028213774737392[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_6905028213774737392[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_6905028213774737392[53] = -9.8000000000000007*dt;
   out_6905028213774737392[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_6905028213774737392[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_6905028213774737392[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_6905028213774737392[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_6905028213774737392[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_6905028213774737392[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_6905028213774737392[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_6905028213774737392[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_6905028213774737392[62] = 0;
   out_6905028213774737392[63] = 0;
   out_6905028213774737392[64] = 0;
   out_6905028213774737392[65] = 0;
   out_6905028213774737392[66] = 0;
   out_6905028213774737392[67] = 0;
   out_6905028213774737392[68] = 0;
   out_6905028213774737392[69] = 0;
   out_6905028213774737392[70] = 1;
   out_6905028213774737392[71] = 0;
   out_6905028213774737392[72] = 0;
   out_6905028213774737392[73] = 0;
   out_6905028213774737392[74] = 0;
   out_6905028213774737392[75] = 0;
   out_6905028213774737392[76] = 0;
   out_6905028213774737392[77] = 0;
   out_6905028213774737392[78] = 0;
   out_6905028213774737392[79] = 0;
   out_6905028213774737392[80] = 1;
}
void h_25(double *state, double *unused, double *out_8121427082764877011) {
   out_8121427082764877011[0] = state[6];
}
void H_25(double *state, double *unused, double *out_3812417976563737166) {
   out_3812417976563737166[0] = 0;
   out_3812417976563737166[1] = 0;
   out_3812417976563737166[2] = 0;
   out_3812417976563737166[3] = 0;
   out_3812417976563737166[4] = 0;
   out_3812417976563737166[5] = 0;
   out_3812417976563737166[6] = 1;
   out_3812417976563737166[7] = 0;
   out_3812417976563737166[8] = 0;
}
void h_24(double *state, double *unused, double *out_3997942509789646952) {
   out_3997942509789646952[0] = state[4];
   out_3997942509789646952[1] = state[5];
}
void H_24(double *state, double *unused, double *out_8681232841591444018) {
   out_8681232841591444018[0] = 0;
   out_8681232841591444018[1] = 0;
   out_8681232841591444018[2] = 0;
   out_8681232841591444018[3] = 0;
   out_8681232841591444018[4] = 1;
   out_8681232841591444018[5] = 0;
   out_8681232841591444018[6] = 0;
   out_8681232841591444018[7] = 0;
   out_8681232841591444018[8] = 0;
   out_8681232841591444018[9] = 0;
   out_8681232841591444018[10] = 0;
   out_8681232841591444018[11] = 0;
   out_8681232841591444018[12] = 0;
   out_8681232841591444018[13] = 0;
   out_8681232841591444018[14] = 1;
   out_8681232841591444018[15] = 0;
   out_8681232841591444018[16] = 0;
   out_8681232841591444018[17] = 0;
}
void h_30(double *state, double *unused, double *out_1350591856414526075) {
   out_1350591856414526075[0] = state[4];
}
void H_30(double *state, double *unused, double *out_8340114306691345364) {
   out_8340114306691345364[0] = 0;
   out_8340114306691345364[1] = 0;
   out_8340114306691345364[2] = 0;
   out_8340114306691345364[3] = 0;
   out_8340114306691345364[4] = 1;
   out_8340114306691345364[5] = 0;
   out_8340114306691345364[6] = 0;
   out_8340114306691345364[7] = 0;
   out_8340114306691345364[8] = 0;
}
void h_26(double *state, double *unused, double *out_3651081411246319570) {
   out_3651081411246319570[0] = state[7];
}
void H_26(double *state, double *unused, double *out_7553921295437793390) {
   out_7553921295437793390[0] = 0;
   out_7553921295437793390[1] = 0;
   out_7553921295437793390[2] = 0;
   out_7553921295437793390[3] = 0;
   out_7553921295437793390[4] = 0;
   out_7553921295437793390[5] = 0;
   out_7553921295437793390[6] = 0;
   out_7553921295437793390[7] = 1;
   out_7553921295437793390[8] = 0;
}
void h_27(double *state, double *unused, double *out_3533074017312942826) {
   out_3533074017312942826[0] = state[3];
}
void H_27(double *state, double *unused, double *out_7931866455217781341) {
   out_7931866455217781341[0] = 0;
   out_7931866455217781341[1] = 0;
   out_7931866455217781341[2] = 0;
   out_7931866455217781341[3] = 1;
   out_7931866455217781341[4] = 0;
   out_7931866455217781341[5] = 0;
   out_7931866455217781341[6] = 0;
   out_7931866455217781341[7] = 0;
   out_7931866455217781341[8] = 0;
}
void h_29(double *state, double *unused, double *out_7631377315592314690) {
   out_7631377315592314690[0] = state[1];
}
void H_29(double *state, double *unused, double *out_7829882962376953180) {
   out_7829882962376953180[0] = 0;
   out_7829882962376953180[1] = 1;
   out_7829882962376953180[2] = 0;
   out_7829882962376953180[3] = 0;
   out_7829882962376953180[4] = 0;
   out_7829882962376953180[5] = 0;
   out_7829882962376953180[6] = 0;
   out_7829882962376953180[7] = 0;
   out_7829882962376953180[8] = 0;
}
void h_28(double *state, double *unused, double *out_4141131178418881891) {
   out_4141131178418881891[0] = state[0];
}
void H_28(double *state, double *unused, double *out_5534462094263067862) {
   out_5534462094263067862[0] = 1;
   out_5534462094263067862[1] = 0;
   out_5534462094263067862[2] = 0;
   out_5534462094263067862[3] = 0;
   out_5534462094263067862[4] = 0;
   out_5534462094263067862[5] = 0;
   out_5534462094263067862[6] = 0;
   out_5534462094263067862[7] = 0;
   out_5534462094263067862[8] = 0;
}
void h_31(double *state, double *unused, double *out_1685439514226132721) {
   out_1685439514226132721[0] = state[8];
}
void H_31(double *state, double *unused, double *out_8180129397671144866) {
   out_8180129397671144866[0] = 0;
   out_8180129397671144866[1] = 0;
   out_8180129397671144866[2] = 0;
   out_8180129397671144866[3] = 0;
   out_8180129397671144866[4] = 0;
   out_8180129397671144866[5] = 0;
   out_8180129397671144866[6] = 0;
   out_8180129397671144866[7] = 0;
   out_8180129397671144866[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_3451169381060055315) {
  err_fun(nom_x, delta_x, out_3451169381060055315);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_7186137212168118329) {
  inv_err_fun(nom_x, true_x, out_7186137212168118329);
}
void car_H_mod_fun(double *state, double *out_7616985092703441005) {
  H_mod_fun(state, out_7616985092703441005);
}
void car_f_fun(double *state, double dt, double *out_5673807216349312269) {
  f_fun(state,  dt, out_5673807216349312269);
}
void car_F_fun(double *state, double dt, double *out_6905028213774737392) {
  F_fun(state,  dt, out_6905028213774737392);
}
void car_h_25(double *state, double *unused, double *out_8121427082764877011) {
  h_25(state, unused, out_8121427082764877011);
}
void car_H_25(double *state, double *unused, double *out_3812417976563737166) {
  H_25(state, unused, out_3812417976563737166);
}
void car_h_24(double *state, double *unused, double *out_3997942509789646952) {
  h_24(state, unused, out_3997942509789646952);
}
void car_H_24(double *state, double *unused, double *out_8681232841591444018) {
  H_24(state, unused, out_8681232841591444018);
}
void car_h_30(double *state, double *unused, double *out_1350591856414526075) {
  h_30(state, unused, out_1350591856414526075);
}
void car_H_30(double *state, double *unused, double *out_8340114306691345364) {
  H_30(state, unused, out_8340114306691345364);
}
void car_h_26(double *state, double *unused, double *out_3651081411246319570) {
  h_26(state, unused, out_3651081411246319570);
}
void car_H_26(double *state, double *unused, double *out_7553921295437793390) {
  H_26(state, unused, out_7553921295437793390);
}
void car_h_27(double *state, double *unused, double *out_3533074017312942826) {
  h_27(state, unused, out_3533074017312942826);
}
void car_H_27(double *state, double *unused, double *out_7931866455217781341) {
  H_27(state, unused, out_7931866455217781341);
}
void car_h_29(double *state, double *unused, double *out_7631377315592314690) {
  h_29(state, unused, out_7631377315592314690);
}
void car_H_29(double *state, double *unused, double *out_7829882962376953180) {
  H_29(state, unused, out_7829882962376953180);
}
void car_h_28(double *state, double *unused, double *out_4141131178418881891) {
  h_28(state, unused, out_4141131178418881891);
}
void car_H_28(double *state, double *unused, double *out_5534462094263067862) {
  H_28(state, unused, out_5534462094263067862);
}
void car_h_31(double *state, double *unused, double *out_1685439514226132721) {
  h_31(state, unused, out_1685439514226132721);
}
void car_H_31(double *state, double *unused, double *out_8180129397671144866) {
  H_31(state, unused, out_8180129397671144866);
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

ekf_init(car);
