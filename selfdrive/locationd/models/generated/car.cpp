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
void err_fun(double *nom_x, double *delta_x, double *out_4158925373118689754) {
   out_4158925373118689754[0] = delta_x[0] + nom_x[0];
   out_4158925373118689754[1] = delta_x[1] + nom_x[1];
   out_4158925373118689754[2] = delta_x[2] + nom_x[2];
   out_4158925373118689754[3] = delta_x[3] + nom_x[3];
   out_4158925373118689754[4] = delta_x[4] + nom_x[4];
   out_4158925373118689754[5] = delta_x[5] + nom_x[5];
   out_4158925373118689754[6] = delta_x[6] + nom_x[6];
   out_4158925373118689754[7] = delta_x[7] + nom_x[7];
   out_4158925373118689754[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_4984125863451852969) {
   out_4984125863451852969[0] = -nom_x[0] + true_x[0];
   out_4984125863451852969[1] = -nom_x[1] + true_x[1];
   out_4984125863451852969[2] = -nom_x[2] + true_x[2];
   out_4984125863451852969[3] = -nom_x[3] + true_x[3];
   out_4984125863451852969[4] = -nom_x[4] + true_x[4];
   out_4984125863451852969[5] = -nom_x[5] + true_x[5];
   out_4984125863451852969[6] = -nom_x[6] + true_x[6];
   out_4984125863451852969[7] = -nom_x[7] + true_x[7];
   out_4984125863451852969[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_7144135399215499310) {
   out_7144135399215499310[0] = 1.0;
   out_7144135399215499310[1] = 0.0;
   out_7144135399215499310[2] = 0.0;
   out_7144135399215499310[3] = 0.0;
   out_7144135399215499310[4] = 0.0;
   out_7144135399215499310[5] = 0.0;
   out_7144135399215499310[6] = 0.0;
   out_7144135399215499310[7] = 0.0;
   out_7144135399215499310[8] = 0.0;
   out_7144135399215499310[9] = 0.0;
   out_7144135399215499310[10] = 1.0;
   out_7144135399215499310[11] = 0.0;
   out_7144135399215499310[12] = 0.0;
   out_7144135399215499310[13] = 0.0;
   out_7144135399215499310[14] = 0.0;
   out_7144135399215499310[15] = 0.0;
   out_7144135399215499310[16] = 0.0;
   out_7144135399215499310[17] = 0.0;
   out_7144135399215499310[18] = 0.0;
   out_7144135399215499310[19] = 0.0;
   out_7144135399215499310[20] = 1.0;
   out_7144135399215499310[21] = 0.0;
   out_7144135399215499310[22] = 0.0;
   out_7144135399215499310[23] = 0.0;
   out_7144135399215499310[24] = 0.0;
   out_7144135399215499310[25] = 0.0;
   out_7144135399215499310[26] = 0.0;
   out_7144135399215499310[27] = 0.0;
   out_7144135399215499310[28] = 0.0;
   out_7144135399215499310[29] = 0.0;
   out_7144135399215499310[30] = 1.0;
   out_7144135399215499310[31] = 0.0;
   out_7144135399215499310[32] = 0.0;
   out_7144135399215499310[33] = 0.0;
   out_7144135399215499310[34] = 0.0;
   out_7144135399215499310[35] = 0.0;
   out_7144135399215499310[36] = 0.0;
   out_7144135399215499310[37] = 0.0;
   out_7144135399215499310[38] = 0.0;
   out_7144135399215499310[39] = 0.0;
   out_7144135399215499310[40] = 1.0;
   out_7144135399215499310[41] = 0.0;
   out_7144135399215499310[42] = 0.0;
   out_7144135399215499310[43] = 0.0;
   out_7144135399215499310[44] = 0.0;
   out_7144135399215499310[45] = 0.0;
   out_7144135399215499310[46] = 0.0;
   out_7144135399215499310[47] = 0.0;
   out_7144135399215499310[48] = 0.0;
   out_7144135399215499310[49] = 0.0;
   out_7144135399215499310[50] = 1.0;
   out_7144135399215499310[51] = 0.0;
   out_7144135399215499310[52] = 0.0;
   out_7144135399215499310[53] = 0.0;
   out_7144135399215499310[54] = 0.0;
   out_7144135399215499310[55] = 0.0;
   out_7144135399215499310[56] = 0.0;
   out_7144135399215499310[57] = 0.0;
   out_7144135399215499310[58] = 0.0;
   out_7144135399215499310[59] = 0.0;
   out_7144135399215499310[60] = 1.0;
   out_7144135399215499310[61] = 0.0;
   out_7144135399215499310[62] = 0.0;
   out_7144135399215499310[63] = 0.0;
   out_7144135399215499310[64] = 0.0;
   out_7144135399215499310[65] = 0.0;
   out_7144135399215499310[66] = 0.0;
   out_7144135399215499310[67] = 0.0;
   out_7144135399215499310[68] = 0.0;
   out_7144135399215499310[69] = 0.0;
   out_7144135399215499310[70] = 1.0;
   out_7144135399215499310[71] = 0.0;
   out_7144135399215499310[72] = 0.0;
   out_7144135399215499310[73] = 0.0;
   out_7144135399215499310[74] = 0.0;
   out_7144135399215499310[75] = 0.0;
   out_7144135399215499310[76] = 0.0;
   out_7144135399215499310[77] = 0.0;
   out_7144135399215499310[78] = 0.0;
   out_7144135399215499310[79] = 0.0;
   out_7144135399215499310[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_4290930710925439296) {
   out_4290930710925439296[0] = state[0];
   out_4290930710925439296[1] = state[1];
   out_4290930710925439296[2] = state[2];
   out_4290930710925439296[3] = state[3];
   out_4290930710925439296[4] = state[4];
   out_4290930710925439296[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8000000000000007*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_4290930710925439296[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_4290930710925439296[7] = state[7];
   out_4290930710925439296[8] = state[8];
}
void F_fun(double *state, double dt, double *out_6422410295062662532) {
   out_6422410295062662532[0] = 1;
   out_6422410295062662532[1] = 0;
   out_6422410295062662532[2] = 0;
   out_6422410295062662532[3] = 0;
   out_6422410295062662532[4] = 0;
   out_6422410295062662532[5] = 0;
   out_6422410295062662532[6] = 0;
   out_6422410295062662532[7] = 0;
   out_6422410295062662532[8] = 0;
   out_6422410295062662532[9] = 0;
   out_6422410295062662532[10] = 1;
   out_6422410295062662532[11] = 0;
   out_6422410295062662532[12] = 0;
   out_6422410295062662532[13] = 0;
   out_6422410295062662532[14] = 0;
   out_6422410295062662532[15] = 0;
   out_6422410295062662532[16] = 0;
   out_6422410295062662532[17] = 0;
   out_6422410295062662532[18] = 0;
   out_6422410295062662532[19] = 0;
   out_6422410295062662532[20] = 1;
   out_6422410295062662532[21] = 0;
   out_6422410295062662532[22] = 0;
   out_6422410295062662532[23] = 0;
   out_6422410295062662532[24] = 0;
   out_6422410295062662532[25] = 0;
   out_6422410295062662532[26] = 0;
   out_6422410295062662532[27] = 0;
   out_6422410295062662532[28] = 0;
   out_6422410295062662532[29] = 0;
   out_6422410295062662532[30] = 1;
   out_6422410295062662532[31] = 0;
   out_6422410295062662532[32] = 0;
   out_6422410295062662532[33] = 0;
   out_6422410295062662532[34] = 0;
   out_6422410295062662532[35] = 0;
   out_6422410295062662532[36] = 0;
   out_6422410295062662532[37] = 0;
   out_6422410295062662532[38] = 0;
   out_6422410295062662532[39] = 0;
   out_6422410295062662532[40] = 1;
   out_6422410295062662532[41] = 0;
   out_6422410295062662532[42] = 0;
   out_6422410295062662532[43] = 0;
   out_6422410295062662532[44] = 0;
   out_6422410295062662532[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_6422410295062662532[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_6422410295062662532[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_6422410295062662532[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_6422410295062662532[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_6422410295062662532[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_6422410295062662532[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_6422410295062662532[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_6422410295062662532[53] = -9.8000000000000007*dt;
   out_6422410295062662532[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_6422410295062662532[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_6422410295062662532[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_6422410295062662532[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_6422410295062662532[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_6422410295062662532[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_6422410295062662532[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_6422410295062662532[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_6422410295062662532[62] = 0;
   out_6422410295062662532[63] = 0;
   out_6422410295062662532[64] = 0;
   out_6422410295062662532[65] = 0;
   out_6422410295062662532[66] = 0;
   out_6422410295062662532[67] = 0;
   out_6422410295062662532[68] = 0;
   out_6422410295062662532[69] = 0;
   out_6422410295062662532[70] = 1;
   out_6422410295062662532[71] = 0;
   out_6422410295062662532[72] = 0;
   out_6422410295062662532[73] = 0;
   out_6422410295062662532[74] = 0;
   out_6422410295062662532[75] = 0;
   out_6422410295062662532[76] = 0;
   out_6422410295062662532[77] = 0;
   out_6422410295062662532[78] = 0;
   out_6422410295062662532[79] = 0;
   out_6422410295062662532[80] = 1;
}
void h_25(double *state, double *unused, double *out_278399437397340579) {
   out_278399437397340579[0] = state[6];
}
void H_25(double *state, double *unused, double *out_1620022460843769287) {
   out_1620022460843769287[0] = 0;
   out_1620022460843769287[1] = 0;
   out_1620022460843769287[2] = 0;
   out_1620022460843769287[3] = 0;
   out_1620022460843769287[4] = 0;
   out_1620022460843769287[5] = 0;
   out_1620022460843769287[6] = 1;
   out_1620022460843769287[7] = 0;
   out_1620022460843769287[8] = 0;
}
void h_24(double *state, double *unused, double *out_2140840430466241598) {
   out_2140840430466241598[0] = state[4];
   out_2140840430466241598[1] = state[5];
}
void H_24(double *state, double *unused, double *out_552627138161730279) {
   out_552627138161730279[0] = 0;
   out_552627138161730279[1] = 0;
   out_552627138161730279[2] = 0;
   out_552627138161730279[3] = 0;
   out_552627138161730279[4] = 1;
   out_552627138161730279[5] = 0;
   out_552627138161730279[6] = 0;
   out_552627138161730279[7] = 0;
   out_552627138161730279[8] = 0;
   out_552627138161730279[9] = 0;
   out_552627138161730279[10] = 0;
   out_552627138161730279[11] = 0;
   out_552627138161730279[12] = 0;
   out_552627138161730279[13] = 0;
   out_552627138161730279[14] = 1;
   out_552627138161730279[15] = 0;
   out_552627138161730279[16] = 0;
   out_552627138161730279[17] = 0;
}
void h_30(double *state, double *unused, double *out_7182159326851547746) {
   out_7182159326851547746[0] = state[4];
}
void H_30(double *state, double *unused, double *out_4138355419351017914) {
   out_4138355419351017914[0] = 0;
   out_4138355419351017914[1] = 0;
   out_4138355419351017914[2] = 0;
   out_4138355419351017914[3] = 0;
   out_4138355419351017914[4] = 1;
   out_4138355419351017914[5] = 0;
   out_4138355419351017914[6] = 0;
   out_4138355419351017914[7] = 0;
   out_4138355419351017914[8] = 0;
}
void h_26(double *state, double *unused, double *out_6038677531022678923) {
   out_6038677531022678923[0] = state[7];
}
void H_26(double *state, double *unused, double *out_2121480858030286937) {
   out_2121480858030286937[0] = 0;
   out_2121480858030286937[1] = 0;
   out_2121480858030286937[2] = 0;
   out_2121480858030286937[3] = 0;
   out_2121480858030286937[4] = 0;
   out_2121480858030286937[5] = 0;
   out_2121480858030286937[6] = 0;
   out_2121480858030286937[7] = 1;
   out_2121480858030286937[8] = 0;
}
void h_27(double *state, double *unused, double *out_5423289500512988116) {
   out_5423289500512988116[0] = state[3];
}
void H_27(double *state, double *unused, double *out_1963592107550593003) {
   out_1963592107550593003[0] = 0;
   out_1963592107550593003[1] = 0;
   out_1963592107550593003[2] = 0;
   out_1963592107550593003[3] = 1;
   out_1963592107550593003[4] = 0;
   out_1963592107550593003[5] = 0;
   out_1963592107550593003[6] = 0;
   out_1963592107550593003[7] = 0;
   out_1963592107550593003[8] = 0;
}
void h_29(double *state, double *unused, double *out_6578843442175070229) {
   out_6578843442175070229[0] = state[1];
}
void H_29(double *state, double *unused, double *out_4648586763665410098) {
   out_4648586763665410098[0] = 0;
   out_4648586763665410098[1] = 1;
   out_4648586763665410098[2] = 0;
   out_4648586763665410098[3] = 0;
   out_4648586763665410098[4] = 0;
   out_4648586763665410098[5] = 0;
   out_4648586763665410098[6] = 0;
   out_4648586763665410098[7] = 0;
   out_4648586763665410098[8] = 0;
}
void h_28(double *state, double *unused, double *out_8131199048761675284) {
   out_8131199048761675284[0] = state[0];
}
void H_28(double *state, double *unused, double *out_433812253404120476) {
   out_433812253404120476[0] = 1;
   out_433812253404120476[1] = 0;
   out_433812253404120476[2] = 0;
   out_433812253404120476[3] = 0;
   out_433812253404120476[4] = 0;
   out_433812253404120476[5] = 0;
   out_433812253404120476[6] = 0;
   out_433812253404120476[7] = 0;
   out_433812253404120476[8] = 0;
}
void h_31(double *state, double *unused, double *out_435586105748469724) {
   out_435586105748469724[0] = state[8];
}
void H_31(double *state, double *unused, double *out_2747688960263638413) {
   out_2747688960263638413[0] = 0;
   out_2747688960263638413[1] = 0;
   out_2747688960263638413[2] = 0;
   out_2747688960263638413[3] = 0;
   out_2747688960263638413[4] = 0;
   out_2747688960263638413[5] = 0;
   out_2747688960263638413[6] = 0;
   out_2747688960263638413[7] = 0;
   out_2747688960263638413[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_4158925373118689754) {
  err_fun(nom_x, delta_x, out_4158925373118689754);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_4984125863451852969) {
  inv_err_fun(nom_x, true_x, out_4984125863451852969);
}
void car_H_mod_fun(double *state, double *out_7144135399215499310) {
  H_mod_fun(state, out_7144135399215499310);
}
void car_f_fun(double *state, double dt, double *out_4290930710925439296) {
  f_fun(state,  dt, out_4290930710925439296);
}
void car_F_fun(double *state, double dt, double *out_6422410295062662532) {
  F_fun(state,  dt, out_6422410295062662532);
}
void car_h_25(double *state, double *unused, double *out_278399437397340579) {
  h_25(state, unused, out_278399437397340579);
}
void car_H_25(double *state, double *unused, double *out_1620022460843769287) {
  H_25(state, unused, out_1620022460843769287);
}
void car_h_24(double *state, double *unused, double *out_2140840430466241598) {
  h_24(state, unused, out_2140840430466241598);
}
void car_H_24(double *state, double *unused, double *out_552627138161730279) {
  H_24(state, unused, out_552627138161730279);
}
void car_h_30(double *state, double *unused, double *out_7182159326851547746) {
  h_30(state, unused, out_7182159326851547746);
}
void car_H_30(double *state, double *unused, double *out_4138355419351017914) {
  H_30(state, unused, out_4138355419351017914);
}
void car_h_26(double *state, double *unused, double *out_6038677531022678923) {
  h_26(state, unused, out_6038677531022678923);
}
void car_H_26(double *state, double *unused, double *out_2121480858030286937) {
  H_26(state, unused, out_2121480858030286937);
}
void car_h_27(double *state, double *unused, double *out_5423289500512988116) {
  h_27(state, unused, out_5423289500512988116);
}
void car_H_27(double *state, double *unused, double *out_1963592107550593003) {
  H_27(state, unused, out_1963592107550593003);
}
void car_h_29(double *state, double *unused, double *out_6578843442175070229) {
  h_29(state, unused, out_6578843442175070229);
}
void car_H_29(double *state, double *unused, double *out_4648586763665410098) {
  H_29(state, unused, out_4648586763665410098);
}
void car_h_28(double *state, double *unused, double *out_8131199048761675284) {
  h_28(state, unused, out_8131199048761675284);
}
void car_H_28(double *state, double *unused, double *out_433812253404120476) {
  H_28(state, unused, out_433812253404120476);
}
void car_h_31(double *state, double *unused, double *out_435586105748469724) {
  h_31(state, unused, out_435586105748469724);
}
void car_H_31(double *state, double *unused, double *out_2747688960263638413) {
  H_31(state, unused, out_2747688960263638413);
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
