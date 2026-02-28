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
void err_fun(double *nom_x, double *delta_x, double *out_4509339408202490749) {
   out_4509339408202490749[0] = delta_x[0] + nom_x[0];
   out_4509339408202490749[1] = delta_x[1] + nom_x[1];
   out_4509339408202490749[2] = delta_x[2] + nom_x[2];
   out_4509339408202490749[3] = delta_x[3] + nom_x[3];
   out_4509339408202490749[4] = delta_x[4] + nom_x[4];
   out_4509339408202490749[5] = delta_x[5] + nom_x[5];
   out_4509339408202490749[6] = delta_x[6] + nom_x[6];
   out_4509339408202490749[7] = delta_x[7] + nom_x[7];
   out_4509339408202490749[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_5279638846554635965) {
   out_5279638846554635965[0] = -nom_x[0] + true_x[0];
   out_5279638846554635965[1] = -nom_x[1] + true_x[1];
   out_5279638846554635965[2] = -nom_x[2] + true_x[2];
   out_5279638846554635965[3] = -nom_x[3] + true_x[3];
   out_5279638846554635965[4] = -nom_x[4] + true_x[4];
   out_5279638846554635965[5] = -nom_x[5] + true_x[5];
   out_5279638846554635965[6] = -nom_x[6] + true_x[6];
   out_5279638846554635965[7] = -nom_x[7] + true_x[7];
   out_5279638846554635965[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_5281375903857501390) {
   out_5281375903857501390[0] = 1.0;
   out_5281375903857501390[1] = 0.0;
   out_5281375903857501390[2] = 0.0;
   out_5281375903857501390[3] = 0.0;
   out_5281375903857501390[4] = 0.0;
   out_5281375903857501390[5] = 0.0;
   out_5281375903857501390[6] = 0.0;
   out_5281375903857501390[7] = 0.0;
   out_5281375903857501390[8] = 0.0;
   out_5281375903857501390[9] = 0.0;
   out_5281375903857501390[10] = 1.0;
   out_5281375903857501390[11] = 0.0;
   out_5281375903857501390[12] = 0.0;
   out_5281375903857501390[13] = 0.0;
   out_5281375903857501390[14] = 0.0;
   out_5281375903857501390[15] = 0.0;
   out_5281375903857501390[16] = 0.0;
   out_5281375903857501390[17] = 0.0;
   out_5281375903857501390[18] = 0.0;
   out_5281375903857501390[19] = 0.0;
   out_5281375903857501390[20] = 1.0;
   out_5281375903857501390[21] = 0.0;
   out_5281375903857501390[22] = 0.0;
   out_5281375903857501390[23] = 0.0;
   out_5281375903857501390[24] = 0.0;
   out_5281375903857501390[25] = 0.0;
   out_5281375903857501390[26] = 0.0;
   out_5281375903857501390[27] = 0.0;
   out_5281375903857501390[28] = 0.0;
   out_5281375903857501390[29] = 0.0;
   out_5281375903857501390[30] = 1.0;
   out_5281375903857501390[31] = 0.0;
   out_5281375903857501390[32] = 0.0;
   out_5281375903857501390[33] = 0.0;
   out_5281375903857501390[34] = 0.0;
   out_5281375903857501390[35] = 0.0;
   out_5281375903857501390[36] = 0.0;
   out_5281375903857501390[37] = 0.0;
   out_5281375903857501390[38] = 0.0;
   out_5281375903857501390[39] = 0.0;
   out_5281375903857501390[40] = 1.0;
   out_5281375903857501390[41] = 0.0;
   out_5281375903857501390[42] = 0.0;
   out_5281375903857501390[43] = 0.0;
   out_5281375903857501390[44] = 0.0;
   out_5281375903857501390[45] = 0.0;
   out_5281375903857501390[46] = 0.0;
   out_5281375903857501390[47] = 0.0;
   out_5281375903857501390[48] = 0.0;
   out_5281375903857501390[49] = 0.0;
   out_5281375903857501390[50] = 1.0;
   out_5281375903857501390[51] = 0.0;
   out_5281375903857501390[52] = 0.0;
   out_5281375903857501390[53] = 0.0;
   out_5281375903857501390[54] = 0.0;
   out_5281375903857501390[55] = 0.0;
   out_5281375903857501390[56] = 0.0;
   out_5281375903857501390[57] = 0.0;
   out_5281375903857501390[58] = 0.0;
   out_5281375903857501390[59] = 0.0;
   out_5281375903857501390[60] = 1.0;
   out_5281375903857501390[61] = 0.0;
   out_5281375903857501390[62] = 0.0;
   out_5281375903857501390[63] = 0.0;
   out_5281375903857501390[64] = 0.0;
   out_5281375903857501390[65] = 0.0;
   out_5281375903857501390[66] = 0.0;
   out_5281375903857501390[67] = 0.0;
   out_5281375903857501390[68] = 0.0;
   out_5281375903857501390[69] = 0.0;
   out_5281375903857501390[70] = 1.0;
   out_5281375903857501390[71] = 0.0;
   out_5281375903857501390[72] = 0.0;
   out_5281375903857501390[73] = 0.0;
   out_5281375903857501390[74] = 0.0;
   out_5281375903857501390[75] = 0.0;
   out_5281375903857501390[76] = 0.0;
   out_5281375903857501390[77] = 0.0;
   out_5281375903857501390[78] = 0.0;
   out_5281375903857501390[79] = 0.0;
   out_5281375903857501390[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_7805851541589707250) {
   out_7805851541589707250[0] = state[0];
   out_7805851541589707250[1] = state[1];
   out_7805851541589707250[2] = state[2];
   out_7805851541589707250[3] = state[3];
   out_7805851541589707250[4] = state[4];
   out_7805851541589707250[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8100000000000005*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_7805851541589707250[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_7805851541589707250[7] = state[7];
   out_7805851541589707250[8] = state[8];
}
void F_fun(double *state, double dt, double *out_8399297218245309857) {
   out_8399297218245309857[0] = 1;
   out_8399297218245309857[1] = 0;
   out_8399297218245309857[2] = 0;
   out_8399297218245309857[3] = 0;
   out_8399297218245309857[4] = 0;
   out_8399297218245309857[5] = 0;
   out_8399297218245309857[6] = 0;
   out_8399297218245309857[7] = 0;
   out_8399297218245309857[8] = 0;
   out_8399297218245309857[9] = 0;
   out_8399297218245309857[10] = 1;
   out_8399297218245309857[11] = 0;
   out_8399297218245309857[12] = 0;
   out_8399297218245309857[13] = 0;
   out_8399297218245309857[14] = 0;
   out_8399297218245309857[15] = 0;
   out_8399297218245309857[16] = 0;
   out_8399297218245309857[17] = 0;
   out_8399297218245309857[18] = 0;
   out_8399297218245309857[19] = 0;
   out_8399297218245309857[20] = 1;
   out_8399297218245309857[21] = 0;
   out_8399297218245309857[22] = 0;
   out_8399297218245309857[23] = 0;
   out_8399297218245309857[24] = 0;
   out_8399297218245309857[25] = 0;
   out_8399297218245309857[26] = 0;
   out_8399297218245309857[27] = 0;
   out_8399297218245309857[28] = 0;
   out_8399297218245309857[29] = 0;
   out_8399297218245309857[30] = 1;
   out_8399297218245309857[31] = 0;
   out_8399297218245309857[32] = 0;
   out_8399297218245309857[33] = 0;
   out_8399297218245309857[34] = 0;
   out_8399297218245309857[35] = 0;
   out_8399297218245309857[36] = 0;
   out_8399297218245309857[37] = 0;
   out_8399297218245309857[38] = 0;
   out_8399297218245309857[39] = 0;
   out_8399297218245309857[40] = 1;
   out_8399297218245309857[41] = 0;
   out_8399297218245309857[42] = 0;
   out_8399297218245309857[43] = 0;
   out_8399297218245309857[44] = 0;
   out_8399297218245309857[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_8399297218245309857[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_8399297218245309857[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_8399297218245309857[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_8399297218245309857[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_8399297218245309857[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_8399297218245309857[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_8399297218245309857[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_8399297218245309857[53] = -9.8100000000000005*dt;
   out_8399297218245309857[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_8399297218245309857[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_8399297218245309857[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_8399297218245309857[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_8399297218245309857[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_8399297218245309857[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_8399297218245309857[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_8399297218245309857[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_8399297218245309857[62] = 0;
   out_8399297218245309857[63] = 0;
   out_8399297218245309857[64] = 0;
   out_8399297218245309857[65] = 0;
   out_8399297218245309857[66] = 0;
   out_8399297218245309857[67] = 0;
   out_8399297218245309857[68] = 0;
   out_8399297218245309857[69] = 0;
   out_8399297218245309857[70] = 1;
   out_8399297218245309857[71] = 0;
   out_8399297218245309857[72] = 0;
   out_8399297218245309857[73] = 0;
   out_8399297218245309857[74] = 0;
   out_8399297218245309857[75] = 0;
   out_8399297218245309857[76] = 0;
   out_8399297218245309857[77] = 0;
   out_8399297218245309857[78] = 0;
   out_8399297218245309857[79] = 0;
   out_8399297218245309857[80] = 1;
}
void h_25(double *state, double *unused, double *out_2366189864445090968) {
   out_2366189864445090968[0] = state[6];
}
void H_25(double *state, double *unused, double *out_3911812322054735847) {
   out_3911812322054735847[0] = 0;
   out_3911812322054735847[1] = 0;
   out_3911812322054735847[2] = 0;
   out_3911812322054735847[3] = 0;
   out_3911812322054735847[4] = 0;
   out_3911812322054735847[5] = 0;
   out_3911812322054735847[6] = 1;
   out_3911812322054735847[7] = 0;
   out_3911812322054735847[8] = 0;
}
void h_24(double *state, double *unused, double *out_6229388731742918084) {
   out_6229388731742918084[0] = state[4];
   out_6229388731742918084[1] = state[5];
}
void H_24(double *state, double *unused, double *out_5760039343842644875) {
   out_5760039343842644875[0] = 0;
   out_5760039343842644875[1] = 0;
   out_5760039343842644875[2] = 0;
   out_5760039343842644875[3] = 0;
   out_5760039343842644875[4] = 1;
   out_5760039343842644875[5] = 0;
   out_5760039343842644875[6] = 0;
   out_5760039343842644875[7] = 0;
   out_5760039343842644875[8] = 0;
   out_5760039343842644875[9] = 0;
   out_5760039343842644875[10] = 0;
   out_5760039343842644875[11] = 0;
   out_5760039343842644875[12] = 0;
   out_5760039343842644875[13] = 0;
   out_5760039343842644875[14] = 1;
   out_5760039343842644875[15] = 0;
   out_5760039343842644875[16] = 0;
   out_5760039343842644875[17] = 0;
}
void h_30(double *state, double *unused, double *out_8317288952443788207) {
   out_8317288952443788207[0] = state[4];
}
void H_30(double *state, double *unused, double *out_3004878019436880908) {
   out_3004878019436880908[0] = 0;
   out_3004878019436880908[1] = 0;
   out_3004878019436880908[2] = 0;
   out_3004878019436880908[3] = 0;
   out_3004878019436880908[4] = 1;
   out_3004878019436880908[5] = 0;
   out_3004878019436880908[6] = 0;
   out_3004878019436880908[7] = 0;
   out_3004878019436880908[8] = 0;
}
void h_26(double *state, double *unused, double *out_1147485949258922644) {
   out_1147485949258922644[0] = state[7];
}
void H_26(double *state, double *unused, double *out_7653315640928792071) {
   out_7653315640928792071[0] = 0;
   out_7653315640928792071[1] = 0;
   out_7653315640928792071[2] = 0;
   out_7653315640928792071[3] = 0;
   out_7653315640928792071[4] = 0;
   out_7653315640928792071[5] = 0;
   out_7653315640928792071[6] = 0;
   out_7653315640928792071[7] = 1;
   out_7653315640928792071[8] = 0;
}
void h_27(double *state, double *unused, double *out_4970595185253788619) {
   out_4970595185253788619[0] = state[3];
}
void H_27(double *state, double *unused, double *out_830114707636455997) {
   out_830114707636455997[0] = 0;
   out_830114707636455997[1] = 0;
   out_830114707636455997[2] = 0;
   out_830114707636455997[3] = 1;
   out_830114707636455997[4] = 0;
   out_830114707636455997[5] = 0;
   out_830114707636455997[6] = 0;
   out_830114707636455997[7] = 0;
   out_830114707636455997[8] = 0;
}
void h_29(double *state, double *unused, double *out_5127781853604917764) {
   out_5127781853604917764[0] = state[1];
}
void H_29(double *state, double *unused, double *out_3515109363751273092) {
   out_3515109363751273092[0] = 0;
   out_3515109363751273092[1] = 1;
   out_3515109363751273092[2] = 0;
   out_3515109363751273092[3] = 0;
   out_3515109363751273092[4] = 0;
   out_3515109363751273092[5] = 0;
   out_3515109363751273092[6] = 0;
   out_3515109363751273092[7] = 0;
   out_3515109363751273092[8] = 0;
}
void h_28(double *state, double *unused, double *out_6265239402201541486) {
   out_6265239402201541486[0] = state[0];
}
void H_28(double *state, double *unused, double *out_1567289653318257482) {
   out_1567289653318257482[0] = 1;
   out_1567289653318257482[1] = 0;
   out_1567289653318257482[2] = 0;
   out_1567289653318257482[3] = 0;
   out_1567289653318257482[4] = 0;
   out_1567289653318257482[5] = 0;
   out_1567289653318257482[6] = 0;
   out_1567289653318257482[7] = 0;
   out_1567289653318257482[8] = 0;
}
void h_31(double *state, double *unused, double *out_8199281558510411463) {
   out_8199281558510411463[0] = state[8];
}
void H_31(double *state, double *unused, double *out_3881166360177775419) {
   out_3881166360177775419[0] = 0;
   out_3881166360177775419[1] = 0;
   out_3881166360177775419[2] = 0;
   out_3881166360177775419[3] = 0;
   out_3881166360177775419[4] = 0;
   out_3881166360177775419[5] = 0;
   out_3881166360177775419[6] = 0;
   out_3881166360177775419[7] = 0;
   out_3881166360177775419[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_4509339408202490749) {
  err_fun(nom_x, delta_x, out_4509339408202490749);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_5279638846554635965) {
  inv_err_fun(nom_x, true_x, out_5279638846554635965);
}
void car_H_mod_fun(double *state, double *out_5281375903857501390) {
  H_mod_fun(state, out_5281375903857501390);
}
void car_f_fun(double *state, double dt, double *out_7805851541589707250) {
  f_fun(state,  dt, out_7805851541589707250);
}
void car_F_fun(double *state, double dt, double *out_8399297218245309857) {
  F_fun(state,  dt, out_8399297218245309857);
}
void car_h_25(double *state, double *unused, double *out_2366189864445090968) {
  h_25(state, unused, out_2366189864445090968);
}
void car_H_25(double *state, double *unused, double *out_3911812322054735847) {
  H_25(state, unused, out_3911812322054735847);
}
void car_h_24(double *state, double *unused, double *out_6229388731742918084) {
  h_24(state, unused, out_6229388731742918084);
}
void car_H_24(double *state, double *unused, double *out_5760039343842644875) {
  H_24(state, unused, out_5760039343842644875);
}
void car_h_30(double *state, double *unused, double *out_8317288952443788207) {
  h_30(state, unused, out_8317288952443788207);
}
void car_H_30(double *state, double *unused, double *out_3004878019436880908) {
  H_30(state, unused, out_3004878019436880908);
}
void car_h_26(double *state, double *unused, double *out_1147485949258922644) {
  h_26(state, unused, out_1147485949258922644);
}
void car_H_26(double *state, double *unused, double *out_7653315640928792071) {
  H_26(state, unused, out_7653315640928792071);
}
void car_h_27(double *state, double *unused, double *out_4970595185253788619) {
  h_27(state, unused, out_4970595185253788619);
}
void car_H_27(double *state, double *unused, double *out_830114707636455997) {
  H_27(state, unused, out_830114707636455997);
}
void car_h_29(double *state, double *unused, double *out_5127781853604917764) {
  h_29(state, unused, out_5127781853604917764);
}
void car_H_29(double *state, double *unused, double *out_3515109363751273092) {
  H_29(state, unused, out_3515109363751273092);
}
void car_h_28(double *state, double *unused, double *out_6265239402201541486) {
  h_28(state, unused, out_6265239402201541486);
}
void car_H_28(double *state, double *unused, double *out_1567289653318257482) {
  H_28(state, unused, out_1567289653318257482);
}
void car_h_31(double *state, double *unused, double *out_8199281558510411463) {
  h_31(state, unused, out_8199281558510411463);
}
void car_H_31(double *state, double *unused, double *out_3881166360177775419) {
  H_31(state, unused, out_3881166360177775419);
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
