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
void err_fun(double *nom_x, double *delta_x, double *out_205475353292099530) {
   out_205475353292099530[0] = delta_x[0] + nom_x[0];
   out_205475353292099530[1] = delta_x[1] + nom_x[1];
   out_205475353292099530[2] = delta_x[2] + nom_x[2];
   out_205475353292099530[3] = delta_x[3] + nom_x[3];
   out_205475353292099530[4] = delta_x[4] + nom_x[4];
   out_205475353292099530[5] = delta_x[5] + nom_x[5];
   out_205475353292099530[6] = delta_x[6] + nom_x[6];
   out_205475353292099530[7] = delta_x[7] + nom_x[7];
   out_205475353292099530[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_6859088956493527341) {
   out_6859088956493527341[0] = -nom_x[0] + true_x[0];
   out_6859088956493527341[1] = -nom_x[1] + true_x[1];
   out_6859088956493527341[2] = -nom_x[2] + true_x[2];
   out_6859088956493527341[3] = -nom_x[3] + true_x[3];
   out_6859088956493527341[4] = -nom_x[4] + true_x[4];
   out_6859088956493527341[5] = -nom_x[5] + true_x[5];
   out_6859088956493527341[6] = -nom_x[6] + true_x[6];
   out_6859088956493527341[7] = -nom_x[7] + true_x[7];
   out_6859088956493527341[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_8201686483145055601) {
   out_8201686483145055601[0] = 1.0;
   out_8201686483145055601[1] = 0.0;
   out_8201686483145055601[2] = 0.0;
   out_8201686483145055601[3] = 0.0;
   out_8201686483145055601[4] = 0.0;
   out_8201686483145055601[5] = 0.0;
   out_8201686483145055601[6] = 0.0;
   out_8201686483145055601[7] = 0.0;
   out_8201686483145055601[8] = 0.0;
   out_8201686483145055601[9] = 0.0;
   out_8201686483145055601[10] = 1.0;
   out_8201686483145055601[11] = 0.0;
   out_8201686483145055601[12] = 0.0;
   out_8201686483145055601[13] = 0.0;
   out_8201686483145055601[14] = 0.0;
   out_8201686483145055601[15] = 0.0;
   out_8201686483145055601[16] = 0.0;
   out_8201686483145055601[17] = 0.0;
   out_8201686483145055601[18] = 0.0;
   out_8201686483145055601[19] = 0.0;
   out_8201686483145055601[20] = 1.0;
   out_8201686483145055601[21] = 0.0;
   out_8201686483145055601[22] = 0.0;
   out_8201686483145055601[23] = 0.0;
   out_8201686483145055601[24] = 0.0;
   out_8201686483145055601[25] = 0.0;
   out_8201686483145055601[26] = 0.0;
   out_8201686483145055601[27] = 0.0;
   out_8201686483145055601[28] = 0.0;
   out_8201686483145055601[29] = 0.0;
   out_8201686483145055601[30] = 1.0;
   out_8201686483145055601[31] = 0.0;
   out_8201686483145055601[32] = 0.0;
   out_8201686483145055601[33] = 0.0;
   out_8201686483145055601[34] = 0.0;
   out_8201686483145055601[35] = 0.0;
   out_8201686483145055601[36] = 0.0;
   out_8201686483145055601[37] = 0.0;
   out_8201686483145055601[38] = 0.0;
   out_8201686483145055601[39] = 0.0;
   out_8201686483145055601[40] = 1.0;
   out_8201686483145055601[41] = 0.0;
   out_8201686483145055601[42] = 0.0;
   out_8201686483145055601[43] = 0.0;
   out_8201686483145055601[44] = 0.0;
   out_8201686483145055601[45] = 0.0;
   out_8201686483145055601[46] = 0.0;
   out_8201686483145055601[47] = 0.0;
   out_8201686483145055601[48] = 0.0;
   out_8201686483145055601[49] = 0.0;
   out_8201686483145055601[50] = 1.0;
   out_8201686483145055601[51] = 0.0;
   out_8201686483145055601[52] = 0.0;
   out_8201686483145055601[53] = 0.0;
   out_8201686483145055601[54] = 0.0;
   out_8201686483145055601[55] = 0.0;
   out_8201686483145055601[56] = 0.0;
   out_8201686483145055601[57] = 0.0;
   out_8201686483145055601[58] = 0.0;
   out_8201686483145055601[59] = 0.0;
   out_8201686483145055601[60] = 1.0;
   out_8201686483145055601[61] = 0.0;
   out_8201686483145055601[62] = 0.0;
   out_8201686483145055601[63] = 0.0;
   out_8201686483145055601[64] = 0.0;
   out_8201686483145055601[65] = 0.0;
   out_8201686483145055601[66] = 0.0;
   out_8201686483145055601[67] = 0.0;
   out_8201686483145055601[68] = 0.0;
   out_8201686483145055601[69] = 0.0;
   out_8201686483145055601[70] = 1.0;
   out_8201686483145055601[71] = 0.0;
   out_8201686483145055601[72] = 0.0;
   out_8201686483145055601[73] = 0.0;
   out_8201686483145055601[74] = 0.0;
   out_8201686483145055601[75] = 0.0;
   out_8201686483145055601[76] = 0.0;
   out_8201686483145055601[77] = 0.0;
   out_8201686483145055601[78] = 0.0;
   out_8201686483145055601[79] = 0.0;
   out_8201686483145055601[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_2204957494938772746) {
   out_2204957494938772746[0] = state[0];
   out_2204957494938772746[1] = state[1];
   out_2204957494938772746[2] = state[2];
   out_2204957494938772746[3] = state[3];
   out_2204957494938772746[4] = state[4];
   out_2204957494938772746[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8100000000000005*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_2204957494938772746[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_2204957494938772746[7] = state[7];
   out_2204957494938772746[8] = state[8];
}
void F_fun(double *state, double dt, double *out_2327939745960551937) {
   out_2327939745960551937[0] = 1;
   out_2327939745960551937[1] = 0;
   out_2327939745960551937[2] = 0;
   out_2327939745960551937[3] = 0;
   out_2327939745960551937[4] = 0;
   out_2327939745960551937[5] = 0;
   out_2327939745960551937[6] = 0;
   out_2327939745960551937[7] = 0;
   out_2327939745960551937[8] = 0;
   out_2327939745960551937[9] = 0;
   out_2327939745960551937[10] = 1;
   out_2327939745960551937[11] = 0;
   out_2327939745960551937[12] = 0;
   out_2327939745960551937[13] = 0;
   out_2327939745960551937[14] = 0;
   out_2327939745960551937[15] = 0;
   out_2327939745960551937[16] = 0;
   out_2327939745960551937[17] = 0;
   out_2327939745960551937[18] = 0;
   out_2327939745960551937[19] = 0;
   out_2327939745960551937[20] = 1;
   out_2327939745960551937[21] = 0;
   out_2327939745960551937[22] = 0;
   out_2327939745960551937[23] = 0;
   out_2327939745960551937[24] = 0;
   out_2327939745960551937[25] = 0;
   out_2327939745960551937[26] = 0;
   out_2327939745960551937[27] = 0;
   out_2327939745960551937[28] = 0;
   out_2327939745960551937[29] = 0;
   out_2327939745960551937[30] = 1;
   out_2327939745960551937[31] = 0;
   out_2327939745960551937[32] = 0;
   out_2327939745960551937[33] = 0;
   out_2327939745960551937[34] = 0;
   out_2327939745960551937[35] = 0;
   out_2327939745960551937[36] = 0;
   out_2327939745960551937[37] = 0;
   out_2327939745960551937[38] = 0;
   out_2327939745960551937[39] = 0;
   out_2327939745960551937[40] = 1;
   out_2327939745960551937[41] = 0;
   out_2327939745960551937[42] = 0;
   out_2327939745960551937[43] = 0;
   out_2327939745960551937[44] = 0;
   out_2327939745960551937[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_2327939745960551937[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_2327939745960551937[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_2327939745960551937[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_2327939745960551937[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_2327939745960551937[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_2327939745960551937[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_2327939745960551937[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_2327939745960551937[53] = -9.8100000000000005*dt;
   out_2327939745960551937[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_2327939745960551937[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_2327939745960551937[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_2327939745960551937[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_2327939745960551937[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_2327939745960551937[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_2327939745960551937[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_2327939745960551937[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_2327939745960551937[62] = 0;
   out_2327939745960551937[63] = 0;
   out_2327939745960551937[64] = 0;
   out_2327939745960551937[65] = 0;
   out_2327939745960551937[66] = 0;
   out_2327939745960551937[67] = 0;
   out_2327939745960551937[68] = 0;
   out_2327939745960551937[69] = 0;
   out_2327939745960551937[70] = 1;
   out_2327939745960551937[71] = 0;
   out_2327939745960551937[72] = 0;
   out_2327939745960551937[73] = 0;
   out_2327939745960551937[74] = 0;
   out_2327939745960551937[75] = 0;
   out_2327939745960551937[76] = 0;
   out_2327939745960551937[77] = 0;
   out_2327939745960551937[78] = 0;
   out_2327939745960551937[79] = 0;
   out_2327939745960551937[80] = 1;
}
void h_25(double *state, double *unused, double *out_8734450240234959528) {
   out_8734450240234959528[0] = state[6];
}
void H_25(double *state, double *unused, double *out_6133161197384342845) {
   out_6133161197384342845[0] = 0;
   out_6133161197384342845[1] = 0;
   out_6133161197384342845[2] = 0;
   out_6133161197384342845[3] = 0;
   out_6133161197384342845[4] = 0;
   out_6133161197384342845[5] = 0;
   out_6133161197384342845[6] = 1;
   out_6133161197384342845[7] = 0;
   out_6133161197384342845[8] = 0;
}
void h_24(double *state, double *unused, double *out_8806581475742121932) {
   out_8806581475742121932[0] = state[4];
   out_8806581475742121932[1] = state[5];
}
void H_24(double *state, double *unused, double *out_5738011069733690670) {
   out_5738011069733690670[0] = 0;
   out_5738011069733690670[1] = 0;
   out_5738011069733690670[2] = 0;
   out_5738011069733690670[3] = 0;
   out_5738011069733690670[4] = 1;
   out_5738011069733690670[5] = 0;
   out_5738011069733690670[6] = 0;
   out_5738011069733690670[7] = 0;
   out_5738011069733690670[8] = 0;
   out_5738011069733690670[9] = 0;
   out_5738011069733690670[10] = 0;
   out_5738011069733690670[11] = 0;
   out_5738011069733690670[12] = 0;
   out_5738011069733690670[13] = 0;
   out_5738011069733690670[14] = 1;
   out_5738011069733690670[15] = 0;
   out_5738011069733690670[16] = 0;
   out_5738011069733690670[17] = 0;
}
void h_30(double *state, double *unused, double *out_971184983414287087) {
   out_971184983414287087[0] = state[4];
}
void H_30(double *state, double *unused, double *out_5396892534833592016) {
   out_5396892534833592016[0] = 0;
   out_5396892534833592016[1] = 0;
   out_5396892534833592016[2] = 0;
   out_5396892534833592016[3] = 0;
   out_5396892534833592016[4] = 1;
   out_5396892534833592016[5] = 0;
   out_5396892534833592016[6] = 0;
   out_5396892534833592016[7] = 0;
   out_5396892534833592016[8] = 0;
}
void h_26(double *state, double *unused, double *out_1416855028350640224) {
   out_1416855028350640224[0] = state[7];
}
void H_26(double *state, double *unused, double *out_2391657878510286621) {
   out_2391657878510286621[0] = 0;
   out_2391657878510286621[1] = 0;
   out_2391657878510286621[2] = 0;
   out_2391657878510286621[3] = 0;
   out_2391657878510286621[4] = 0;
   out_2391657878510286621[5] = 0;
   out_2391657878510286621[6] = 0;
   out_2391657878510286621[7] = 1;
   out_2391657878510286621[8] = 0;
}
void h_27(double *state, double *unused, double *out_5511166866350839857) {
   out_5511166866350839857[0] = state[3];
}
void H_27(double *state, double *unused, double *out_7571655846634016927) {
   out_7571655846634016927[0] = 0;
   out_7571655846634016927[1] = 0;
   out_7571655846634016927[2] = 0;
   out_7571655846634016927[3] = 1;
   out_7571655846634016927[4] = 0;
   out_7571655846634016927[5] = 0;
   out_7571655846634016927[6] = 0;
   out_7571655846634016927[7] = 0;
   out_7571655846634016927[8] = 0;
}
void h_29(double *state, double *unused, double *out_5235972804066333968) {
   out_5235972804066333968[0] = state[1];
}
void H_29(double *state, double *unused, double *out_9161725500205983656) {
   out_9161725500205983656[0] = 0;
   out_9161725500205983656[1] = 1;
   out_9161725500205983656[2] = 0;
   out_9161725500205983656[3] = 0;
   out_9161725500205983656[4] = 0;
   out_9161725500205983656[5] = 0;
   out_9161725500205983656[6] = 0;
   out_9161725500205983656[7] = 0;
   out_9161725500205983656[8] = 0;
}
void h_28(double *state, double *unused, double *out_7891338238985058206) {
   out_7891338238985058206[0] = state[0];
}
void H_28(double *state, double *unused, double *out_4079326483136453082) {
   out_4079326483136453082[0] = 1;
   out_4079326483136453082[1] = 0;
   out_4079326483136453082[2] = 0;
   out_4079326483136453082[3] = 0;
   out_4079326483136453082[4] = 0;
   out_4079326483136453082[5] = 0;
   out_4079326483136453082[6] = 0;
   out_4079326483136453082[7] = 0;
   out_4079326483136453082[8] = 0;
}
void h_31(double *state, double *unused, double *out_8694811794428211892) {
   out_8694811794428211892[0] = state[8];
}
void H_31(double *state, double *unused, double *out_6163807159261303273) {
   out_6163807159261303273[0] = 0;
   out_6163807159261303273[1] = 0;
   out_6163807159261303273[2] = 0;
   out_6163807159261303273[3] = 0;
   out_6163807159261303273[4] = 0;
   out_6163807159261303273[5] = 0;
   out_6163807159261303273[6] = 0;
   out_6163807159261303273[7] = 0;
   out_6163807159261303273[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_205475353292099530) {
  err_fun(nom_x, delta_x, out_205475353292099530);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_6859088956493527341) {
  inv_err_fun(nom_x, true_x, out_6859088956493527341);
}
void car_H_mod_fun(double *state, double *out_8201686483145055601) {
  H_mod_fun(state, out_8201686483145055601);
}
void car_f_fun(double *state, double dt, double *out_2204957494938772746) {
  f_fun(state,  dt, out_2204957494938772746);
}
void car_F_fun(double *state, double dt, double *out_2327939745960551937) {
  F_fun(state,  dt, out_2327939745960551937);
}
void car_h_25(double *state, double *unused, double *out_8734450240234959528) {
  h_25(state, unused, out_8734450240234959528);
}
void car_H_25(double *state, double *unused, double *out_6133161197384342845) {
  H_25(state, unused, out_6133161197384342845);
}
void car_h_24(double *state, double *unused, double *out_8806581475742121932) {
  h_24(state, unused, out_8806581475742121932);
}
void car_H_24(double *state, double *unused, double *out_5738011069733690670) {
  H_24(state, unused, out_5738011069733690670);
}
void car_h_30(double *state, double *unused, double *out_971184983414287087) {
  h_30(state, unused, out_971184983414287087);
}
void car_H_30(double *state, double *unused, double *out_5396892534833592016) {
  H_30(state, unused, out_5396892534833592016);
}
void car_h_26(double *state, double *unused, double *out_1416855028350640224) {
  h_26(state, unused, out_1416855028350640224);
}
void car_H_26(double *state, double *unused, double *out_2391657878510286621) {
  H_26(state, unused, out_2391657878510286621);
}
void car_h_27(double *state, double *unused, double *out_5511166866350839857) {
  h_27(state, unused, out_5511166866350839857);
}
void car_H_27(double *state, double *unused, double *out_7571655846634016927) {
  H_27(state, unused, out_7571655846634016927);
}
void car_h_29(double *state, double *unused, double *out_5235972804066333968) {
  h_29(state, unused, out_5235972804066333968);
}
void car_H_29(double *state, double *unused, double *out_9161725500205983656) {
  H_29(state, unused, out_9161725500205983656);
}
void car_h_28(double *state, double *unused, double *out_7891338238985058206) {
  h_28(state, unused, out_7891338238985058206);
}
void car_H_28(double *state, double *unused, double *out_4079326483136453082) {
  H_28(state, unused, out_4079326483136453082);
}
void car_h_31(double *state, double *unused, double *out_8694811794428211892) {
  h_31(state, unused, out_8694811794428211892);
}
void car_H_31(double *state, double *unused, double *out_6163807159261303273) {
  H_31(state, unused, out_6163807159261303273);
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
