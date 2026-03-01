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
void err_fun(double *nom_x, double *delta_x, double *out_4033566628567507317) {
   out_4033566628567507317[0] = delta_x[0] + nom_x[0];
   out_4033566628567507317[1] = delta_x[1] + nom_x[1];
   out_4033566628567507317[2] = delta_x[2] + nom_x[2];
   out_4033566628567507317[3] = delta_x[3] + nom_x[3];
   out_4033566628567507317[4] = delta_x[4] + nom_x[4];
   out_4033566628567507317[5] = delta_x[5] + nom_x[5];
   out_4033566628567507317[6] = delta_x[6] + nom_x[6];
   out_4033566628567507317[7] = delta_x[7] + nom_x[7];
   out_4033566628567507317[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_5990136425401933100) {
   out_5990136425401933100[0] = -nom_x[0] + true_x[0];
   out_5990136425401933100[1] = -nom_x[1] + true_x[1];
   out_5990136425401933100[2] = -nom_x[2] + true_x[2];
   out_5990136425401933100[3] = -nom_x[3] + true_x[3];
   out_5990136425401933100[4] = -nom_x[4] + true_x[4];
   out_5990136425401933100[5] = -nom_x[5] + true_x[5];
   out_5990136425401933100[6] = -nom_x[6] + true_x[6];
   out_5990136425401933100[7] = -nom_x[7] + true_x[7];
   out_5990136425401933100[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_9104365257016194246) {
   out_9104365257016194246[0] = 1.0;
   out_9104365257016194246[1] = 0.0;
   out_9104365257016194246[2] = 0.0;
   out_9104365257016194246[3] = 0.0;
   out_9104365257016194246[4] = 0.0;
   out_9104365257016194246[5] = 0.0;
   out_9104365257016194246[6] = 0.0;
   out_9104365257016194246[7] = 0.0;
   out_9104365257016194246[8] = 0.0;
   out_9104365257016194246[9] = 0.0;
   out_9104365257016194246[10] = 1.0;
   out_9104365257016194246[11] = 0.0;
   out_9104365257016194246[12] = 0.0;
   out_9104365257016194246[13] = 0.0;
   out_9104365257016194246[14] = 0.0;
   out_9104365257016194246[15] = 0.0;
   out_9104365257016194246[16] = 0.0;
   out_9104365257016194246[17] = 0.0;
   out_9104365257016194246[18] = 0.0;
   out_9104365257016194246[19] = 0.0;
   out_9104365257016194246[20] = 1.0;
   out_9104365257016194246[21] = 0.0;
   out_9104365257016194246[22] = 0.0;
   out_9104365257016194246[23] = 0.0;
   out_9104365257016194246[24] = 0.0;
   out_9104365257016194246[25] = 0.0;
   out_9104365257016194246[26] = 0.0;
   out_9104365257016194246[27] = 0.0;
   out_9104365257016194246[28] = 0.0;
   out_9104365257016194246[29] = 0.0;
   out_9104365257016194246[30] = 1.0;
   out_9104365257016194246[31] = 0.0;
   out_9104365257016194246[32] = 0.0;
   out_9104365257016194246[33] = 0.0;
   out_9104365257016194246[34] = 0.0;
   out_9104365257016194246[35] = 0.0;
   out_9104365257016194246[36] = 0.0;
   out_9104365257016194246[37] = 0.0;
   out_9104365257016194246[38] = 0.0;
   out_9104365257016194246[39] = 0.0;
   out_9104365257016194246[40] = 1.0;
   out_9104365257016194246[41] = 0.0;
   out_9104365257016194246[42] = 0.0;
   out_9104365257016194246[43] = 0.0;
   out_9104365257016194246[44] = 0.0;
   out_9104365257016194246[45] = 0.0;
   out_9104365257016194246[46] = 0.0;
   out_9104365257016194246[47] = 0.0;
   out_9104365257016194246[48] = 0.0;
   out_9104365257016194246[49] = 0.0;
   out_9104365257016194246[50] = 1.0;
   out_9104365257016194246[51] = 0.0;
   out_9104365257016194246[52] = 0.0;
   out_9104365257016194246[53] = 0.0;
   out_9104365257016194246[54] = 0.0;
   out_9104365257016194246[55] = 0.0;
   out_9104365257016194246[56] = 0.0;
   out_9104365257016194246[57] = 0.0;
   out_9104365257016194246[58] = 0.0;
   out_9104365257016194246[59] = 0.0;
   out_9104365257016194246[60] = 1.0;
   out_9104365257016194246[61] = 0.0;
   out_9104365257016194246[62] = 0.0;
   out_9104365257016194246[63] = 0.0;
   out_9104365257016194246[64] = 0.0;
   out_9104365257016194246[65] = 0.0;
   out_9104365257016194246[66] = 0.0;
   out_9104365257016194246[67] = 0.0;
   out_9104365257016194246[68] = 0.0;
   out_9104365257016194246[69] = 0.0;
   out_9104365257016194246[70] = 1.0;
   out_9104365257016194246[71] = 0.0;
   out_9104365257016194246[72] = 0.0;
   out_9104365257016194246[73] = 0.0;
   out_9104365257016194246[74] = 0.0;
   out_9104365257016194246[75] = 0.0;
   out_9104365257016194246[76] = 0.0;
   out_9104365257016194246[77] = 0.0;
   out_9104365257016194246[78] = 0.0;
   out_9104365257016194246[79] = 0.0;
   out_9104365257016194246[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_6902401556560306947) {
   out_6902401556560306947[0] = state[0];
   out_6902401556560306947[1] = state[1];
   out_6902401556560306947[2] = state[2];
   out_6902401556560306947[3] = state[3];
   out_6902401556560306947[4] = state[4];
   out_6902401556560306947[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8100000000000005*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_6902401556560306947[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_6902401556560306947[7] = state[7];
   out_6902401556560306947[8] = state[8];
}
void F_fun(double *state, double dt, double *out_5718491602786937955) {
   out_5718491602786937955[0] = 1;
   out_5718491602786937955[1] = 0;
   out_5718491602786937955[2] = 0;
   out_5718491602786937955[3] = 0;
   out_5718491602786937955[4] = 0;
   out_5718491602786937955[5] = 0;
   out_5718491602786937955[6] = 0;
   out_5718491602786937955[7] = 0;
   out_5718491602786937955[8] = 0;
   out_5718491602786937955[9] = 0;
   out_5718491602786937955[10] = 1;
   out_5718491602786937955[11] = 0;
   out_5718491602786937955[12] = 0;
   out_5718491602786937955[13] = 0;
   out_5718491602786937955[14] = 0;
   out_5718491602786937955[15] = 0;
   out_5718491602786937955[16] = 0;
   out_5718491602786937955[17] = 0;
   out_5718491602786937955[18] = 0;
   out_5718491602786937955[19] = 0;
   out_5718491602786937955[20] = 1;
   out_5718491602786937955[21] = 0;
   out_5718491602786937955[22] = 0;
   out_5718491602786937955[23] = 0;
   out_5718491602786937955[24] = 0;
   out_5718491602786937955[25] = 0;
   out_5718491602786937955[26] = 0;
   out_5718491602786937955[27] = 0;
   out_5718491602786937955[28] = 0;
   out_5718491602786937955[29] = 0;
   out_5718491602786937955[30] = 1;
   out_5718491602786937955[31] = 0;
   out_5718491602786937955[32] = 0;
   out_5718491602786937955[33] = 0;
   out_5718491602786937955[34] = 0;
   out_5718491602786937955[35] = 0;
   out_5718491602786937955[36] = 0;
   out_5718491602786937955[37] = 0;
   out_5718491602786937955[38] = 0;
   out_5718491602786937955[39] = 0;
   out_5718491602786937955[40] = 1;
   out_5718491602786937955[41] = 0;
   out_5718491602786937955[42] = 0;
   out_5718491602786937955[43] = 0;
   out_5718491602786937955[44] = 0;
   out_5718491602786937955[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_5718491602786937955[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_5718491602786937955[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_5718491602786937955[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_5718491602786937955[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_5718491602786937955[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_5718491602786937955[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_5718491602786937955[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_5718491602786937955[53] = -9.8100000000000005*dt;
   out_5718491602786937955[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_5718491602786937955[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_5718491602786937955[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_5718491602786937955[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_5718491602786937955[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_5718491602786937955[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_5718491602786937955[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_5718491602786937955[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_5718491602786937955[62] = 0;
   out_5718491602786937955[63] = 0;
   out_5718491602786937955[64] = 0;
   out_5718491602786937955[65] = 0;
   out_5718491602786937955[66] = 0;
   out_5718491602786937955[67] = 0;
   out_5718491602786937955[68] = 0;
   out_5718491602786937955[69] = 0;
   out_5718491602786937955[70] = 1;
   out_5718491602786937955[71] = 0;
   out_5718491602786937955[72] = 0;
   out_5718491602786937955[73] = 0;
   out_5718491602786937955[74] = 0;
   out_5718491602786937955[75] = 0;
   out_5718491602786937955[76] = 0;
   out_5718491602786937955[77] = 0;
   out_5718491602786937955[78] = 0;
   out_5718491602786937955[79] = 0;
   out_5718491602786937955[80] = 1;
}
void h_25(double *state, double *unused, double *out_789803669906526962) {
   out_789803669906526962[0] = state[6];
}
void H_25(double *state, double *unused, double *out_1183027224042334441) {
   out_1183027224042334441[0] = 0;
   out_1183027224042334441[1] = 0;
   out_1183027224042334441[2] = 0;
   out_1183027224042334441[3] = 0;
   out_1183027224042334441[4] = 0;
   out_1183027224042334441[5] = 0;
   out_1183027224042334441[6] = 1;
   out_1183027224042334441[7] = 0;
   out_1183027224042334441[8] = 0;
}
void h_24(double *state, double *unused, double *out_2222181505745557291) {
   out_2222181505745557291[0] = state[4];
   out_2222181505745557291[1] = state[5];
}
void H_24(double *state, double *unused, double *out_5471178234065851316) {
   out_5471178234065851316[0] = 0;
   out_5471178234065851316[1] = 0;
   out_5471178234065851316[2] = 0;
   out_5471178234065851316[3] = 0;
   out_5471178234065851316[4] = 1;
   out_5471178234065851316[5] = 0;
   out_5471178234065851316[6] = 0;
   out_5471178234065851316[7] = 0;
   out_5471178234065851316[8] = 0;
   out_5471178234065851316[9] = 0;
   out_5471178234065851316[10] = 0;
   out_5471178234065851316[11] = 0;
   out_5471178234065851316[12] = 0;
   out_5471178234065851316[13] = 0;
   out_5471178234065851316[14] = 1;
   out_5471178234065851316[15] = 0;
   out_5471178234065851316[16] = 0;
   out_5471178234065851316[17] = 0;
}
void h_30(double *state, double *unused, double *out_8671076320660576147) {
   out_8671076320660576147[0] = state[4];
}
void H_30(double *state, double *unused, double *out_5710723554169942639) {
   out_5710723554169942639[0] = 0;
   out_5710723554169942639[1] = 0;
   out_5710723554169942639[2] = 0;
   out_5710723554169942639[3] = 0;
   out_5710723554169942639[4] = 1;
   out_5710723554169942639[5] = 0;
   out_5710723554169942639[6] = 0;
   out_5710723554169942639[7] = 0;
   out_5710723554169942639[8] = 0;
}
void h_26(double *state, double *unused, double *out_4813287755367682237) {
   out_4813287755367682237[0] = state[7];
}
void H_26(double *state, double *unused, double *out_4924530542916390665) {
   out_4924530542916390665[0] = 0;
   out_4924530542916390665[1] = 0;
   out_4924530542916390665[2] = 0;
   out_4924530542916390665[3] = 0;
   out_4924530542916390665[4] = 0;
   out_4924530542916390665[5] = 0;
   out_4924530542916390665[6] = 0;
   out_4924530542916390665[7] = 1;
   out_4924530542916390665[8] = 0;
}
void h_27(double *state, double *unused, double *out_5791476937567372607) {
   out_5791476937567372607[0] = state[3];
}
void H_27(double *state, double *unused, double *out_7885486865970367550) {
   out_7885486865970367550[0] = 0;
   out_7885486865970367550[1] = 0;
   out_7885486865970367550[2] = 0;
   out_7885486865970367550[3] = 1;
   out_7885486865970367550[4] = 0;
   out_7885486865970367550[5] = 0;
   out_7885486865970367550[6] = 0;
   out_7885486865970367550[7] = 0;
   out_7885486865970367550[8] = 0;
}
void h_29(double *state, double *unused, double *out_8793583659713677357) {
   out_8793583659713677357[0] = state[1];
}
void H_29(double *state, double *unused, double *out_5200492209855550455) {
   out_5200492209855550455[0] = 0;
   out_5200492209855550455[1] = 1;
   out_5200492209855550455[2] = 0;
   out_5200492209855550455[3] = 0;
   out_5200492209855550455[4] = 0;
   out_5200492209855550455[5] = 0;
   out_5200492209855550455[6] = 0;
   out_5200492209855550455[7] = 0;
   out_5200492209855550455[8] = 0;
}
void h_28(double *state, double *unused, double *out_4067104454337337601) {
   out_4067104454337337601[0] = state[0];
}
void H_28(double *state, double *unused, double *out_8163852846784470587) {
   out_8163852846784470587[0] = 1;
   out_8163852846784470587[1] = 0;
   out_8163852846784470587[2] = 0;
   out_8163852846784470587[3] = 0;
   out_8163852846784470587[4] = 0;
   out_8163852846784470587[5] = 0;
   out_8163852846784470587[6] = 0;
   out_8163852846784470587[7] = 0;
   out_8163852846784470587[8] = 0;
}
void h_31(double *state, double *unused, double *out_8553068926727199403) {
   out_8553068926727199403[0] = state[8];
}
void H_31(double *state, double *unused, double *out_5550738645149742141) {
   out_5550738645149742141[0] = 0;
   out_5550738645149742141[1] = 0;
   out_5550738645149742141[2] = 0;
   out_5550738645149742141[3] = 0;
   out_5550738645149742141[4] = 0;
   out_5550738645149742141[5] = 0;
   out_5550738645149742141[6] = 0;
   out_5550738645149742141[7] = 0;
   out_5550738645149742141[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_4033566628567507317) {
  err_fun(nom_x, delta_x, out_4033566628567507317);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_5990136425401933100) {
  inv_err_fun(nom_x, true_x, out_5990136425401933100);
}
void car_H_mod_fun(double *state, double *out_9104365257016194246) {
  H_mod_fun(state, out_9104365257016194246);
}
void car_f_fun(double *state, double dt, double *out_6902401556560306947) {
  f_fun(state,  dt, out_6902401556560306947);
}
void car_F_fun(double *state, double dt, double *out_5718491602786937955) {
  F_fun(state,  dt, out_5718491602786937955);
}
void car_h_25(double *state, double *unused, double *out_789803669906526962) {
  h_25(state, unused, out_789803669906526962);
}
void car_H_25(double *state, double *unused, double *out_1183027224042334441) {
  H_25(state, unused, out_1183027224042334441);
}
void car_h_24(double *state, double *unused, double *out_2222181505745557291) {
  h_24(state, unused, out_2222181505745557291);
}
void car_H_24(double *state, double *unused, double *out_5471178234065851316) {
  H_24(state, unused, out_5471178234065851316);
}
void car_h_30(double *state, double *unused, double *out_8671076320660576147) {
  h_30(state, unused, out_8671076320660576147);
}
void car_H_30(double *state, double *unused, double *out_5710723554169942639) {
  H_30(state, unused, out_5710723554169942639);
}
void car_h_26(double *state, double *unused, double *out_4813287755367682237) {
  h_26(state, unused, out_4813287755367682237);
}
void car_H_26(double *state, double *unused, double *out_4924530542916390665) {
  H_26(state, unused, out_4924530542916390665);
}
void car_h_27(double *state, double *unused, double *out_5791476937567372607) {
  h_27(state, unused, out_5791476937567372607);
}
void car_H_27(double *state, double *unused, double *out_7885486865970367550) {
  H_27(state, unused, out_7885486865970367550);
}
void car_h_29(double *state, double *unused, double *out_8793583659713677357) {
  h_29(state, unused, out_8793583659713677357);
}
void car_H_29(double *state, double *unused, double *out_5200492209855550455) {
  H_29(state, unused, out_5200492209855550455);
}
void car_h_28(double *state, double *unused, double *out_4067104454337337601) {
  h_28(state, unused, out_4067104454337337601);
}
void car_H_28(double *state, double *unused, double *out_8163852846784470587) {
  H_28(state, unused, out_8163852846784470587);
}
void car_h_31(double *state, double *unused, double *out_8553068926727199403) {
  h_31(state, unused, out_8553068926727199403);
}
void car_H_31(double *state, double *unused, double *out_5550738645149742141) {
  H_31(state, unused, out_5550738645149742141);
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
