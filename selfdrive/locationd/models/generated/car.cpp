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
void err_fun(double *nom_x, double *delta_x, double *out_9168682336158195836) {
   out_9168682336158195836[0] = delta_x[0] + nom_x[0];
   out_9168682336158195836[1] = delta_x[1] + nom_x[1];
   out_9168682336158195836[2] = delta_x[2] + nom_x[2];
   out_9168682336158195836[3] = delta_x[3] + nom_x[3];
   out_9168682336158195836[4] = delta_x[4] + nom_x[4];
   out_9168682336158195836[5] = delta_x[5] + nom_x[5];
   out_9168682336158195836[6] = delta_x[6] + nom_x[6];
   out_9168682336158195836[7] = delta_x[7] + nom_x[7];
   out_9168682336158195836[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_5209405894281129857) {
   out_5209405894281129857[0] = -nom_x[0] + true_x[0];
   out_5209405894281129857[1] = -nom_x[1] + true_x[1];
   out_5209405894281129857[2] = -nom_x[2] + true_x[2];
   out_5209405894281129857[3] = -nom_x[3] + true_x[3];
   out_5209405894281129857[4] = -nom_x[4] + true_x[4];
   out_5209405894281129857[5] = -nom_x[5] + true_x[5];
   out_5209405894281129857[6] = -nom_x[6] + true_x[6];
   out_5209405894281129857[7] = -nom_x[7] + true_x[7];
   out_5209405894281129857[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_8788279686404140347) {
   out_8788279686404140347[0] = 1.0;
   out_8788279686404140347[1] = 0;
   out_8788279686404140347[2] = 0;
   out_8788279686404140347[3] = 0;
   out_8788279686404140347[4] = 0;
   out_8788279686404140347[5] = 0;
   out_8788279686404140347[6] = 0;
   out_8788279686404140347[7] = 0;
   out_8788279686404140347[8] = 0;
   out_8788279686404140347[9] = 0;
   out_8788279686404140347[10] = 1.0;
   out_8788279686404140347[11] = 0;
   out_8788279686404140347[12] = 0;
   out_8788279686404140347[13] = 0;
   out_8788279686404140347[14] = 0;
   out_8788279686404140347[15] = 0;
   out_8788279686404140347[16] = 0;
   out_8788279686404140347[17] = 0;
   out_8788279686404140347[18] = 0;
   out_8788279686404140347[19] = 0;
   out_8788279686404140347[20] = 1.0;
   out_8788279686404140347[21] = 0;
   out_8788279686404140347[22] = 0;
   out_8788279686404140347[23] = 0;
   out_8788279686404140347[24] = 0;
   out_8788279686404140347[25] = 0;
   out_8788279686404140347[26] = 0;
   out_8788279686404140347[27] = 0;
   out_8788279686404140347[28] = 0;
   out_8788279686404140347[29] = 0;
   out_8788279686404140347[30] = 1.0;
   out_8788279686404140347[31] = 0;
   out_8788279686404140347[32] = 0;
   out_8788279686404140347[33] = 0;
   out_8788279686404140347[34] = 0;
   out_8788279686404140347[35] = 0;
   out_8788279686404140347[36] = 0;
   out_8788279686404140347[37] = 0;
   out_8788279686404140347[38] = 0;
   out_8788279686404140347[39] = 0;
   out_8788279686404140347[40] = 1.0;
   out_8788279686404140347[41] = 0;
   out_8788279686404140347[42] = 0;
   out_8788279686404140347[43] = 0;
   out_8788279686404140347[44] = 0;
   out_8788279686404140347[45] = 0;
   out_8788279686404140347[46] = 0;
   out_8788279686404140347[47] = 0;
   out_8788279686404140347[48] = 0;
   out_8788279686404140347[49] = 0;
   out_8788279686404140347[50] = 1.0;
   out_8788279686404140347[51] = 0;
   out_8788279686404140347[52] = 0;
   out_8788279686404140347[53] = 0;
   out_8788279686404140347[54] = 0;
   out_8788279686404140347[55] = 0;
   out_8788279686404140347[56] = 0;
   out_8788279686404140347[57] = 0;
   out_8788279686404140347[58] = 0;
   out_8788279686404140347[59] = 0;
   out_8788279686404140347[60] = 1.0;
   out_8788279686404140347[61] = 0;
   out_8788279686404140347[62] = 0;
   out_8788279686404140347[63] = 0;
   out_8788279686404140347[64] = 0;
   out_8788279686404140347[65] = 0;
   out_8788279686404140347[66] = 0;
   out_8788279686404140347[67] = 0;
   out_8788279686404140347[68] = 0;
   out_8788279686404140347[69] = 0;
   out_8788279686404140347[70] = 1.0;
   out_8788279686404140347[71] = 0;
   out_8788279686404140347[72] = 0;
   out_8788279686404140347[73] = 0;
   out_8788279686404140347[74] = 0;
   out_8788279686404140347[75] = 0;
   out_8788279686404140347[76] = 0;
   out_8788279686404140347[77] = 0;
   out_8788279686404140347[78] = 0;
   out_8788279686404140347[79] = 0;
   out_8788279686404140347[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_3220267060095610864) {
   out_3220267060095610864[0] = state[0];
   out_3220267060095610864[1] = state[1];
   out_3220267060095610864[2] = state[2];
   out_3220267060095610864[3] = state[3];
   out_3220267060095610864[4] = state[4];
   out_3220267060095610864[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8000000000000007*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_3220267060095610864[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_3220267060095610864[7] = state[7];
   out_3220267060095610864[8] = state[8];
}
void F_fun(double *state, double dt, double *out_5498270358931541556) {
   out_5498270358931541556[0] = 1;
   out_5498270358931541556[1] = 0;
   out_5498270358931541556[2] = 0;
   out_5498270358931541556[3] = 0;
   out_5498270358931541556[4] = 0;
   out_5498270358931541556[5] = 0;
   out_5498270358931541556[6] = 0;
   out_5498270358931541556[7] = 0;
   out_5498270358931541556[8] = 0;
   out_5498270358931541556[9] = 0;
   out_5498270358931541556[10] = 1;
   out_5498270358931541556[11] = 0;
   out_5498270358931541556[12] = 0;
   out_5498270358931541556[13] = 0;
   out_5498270358931541556[14] = 0;
   out_5498270358931541556[15] = 0;
   out_5498270358931541556[16] = 0;
   out_5498270358931541556[17] = 0;
   out_5498270358931541556[18] = 0;
   out_5498270358931541556[19] = 0;
   out_5498270358931541556[20] = 1;
   out_5498270358931541556[21] = 0;
   out_5498270358931541556[22] = 0;
   out_5498270358931541556[23] = 0;
   out_5498270358931541556[24] = 0;
   out_5498270358931541556[25] = 0;
   out_5498270358931541556[26] = 0;
   out_5498270358931541556[27] = 0;
   out_5498270358931541556[28] = 0;
   out_5498270358931541556[29] = 0;
   out_5498270358931541556[30] = 1;
   out_5498270358931541556[31] = 0;
   out_5498270358931541556[32] = 0;
   out_5498270358931541556[33] = 0;
   out_5498270358931541556[34] = 0;
   out_5498270358931541556[35] = 0;
   out_5498270358931541556[36] = 0;
   out_5498270358931541556[37] = 0;
   out_5498270358931541556[38] = 0;
   out_5498270358931541556[39] = 0;
   out_5498270358931541556[40] = 1;
   out_5498270358931541556[41] = 0;
   out_5498270358931541556[42] = 0;
   out_5498270358931541556[43] = 0;
   out_5498270358931541556[44] = 0;
   out_5498270358931541556[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_5498270358931541556[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_5498270358931541556[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_5498270358931541556[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_5498270358931541556[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_5498270358931541556[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_5498270358931541556[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_5498270358931541556[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_5498270358931541556[53] = -9.8000000000000007*dt;
   out_5498270358931541556[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_5498270358931541556[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_5498270358931541556[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_5498270358931541556[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_5498270358931541556[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_5498270358931541556[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_5498270358931541556[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_5498270358931541556[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_5498270358931541556[62] = 0;
   out_5498270358931541556[63] = 0;
   out_5498270358931541556[64] = 0;
   out_5498270358931541556[65] = 0;
   out_5498270358931541556[66] = 0;
   out_5498270358931541556[67] = 0;
   out_5498270358931541556[68] = 0;
   out_5498270358931541556[69] = 0;
   out_5498270358931541556[70] = 1;
   out_5498270358931541556[71] = 0;
   out_5498270358931541556[72] = 0;
   out_5498270358931541556[73] = 0;
   out_5498270358931541556[74] = 0;
   out_5498270358931541556[75] = 0;
   out_5498270358931541556[76] = 0;
   out_5498270358931541556[77] = 0;
   out_5498270358931541556[78] = 0;
   out_5498270358931541556[79] = 0;
   out_5498270358931541556[80] = 1;
}
void h_25(double *state, double *unused, double *out_5568378315864805240) {
   out_5568378315864805240[0] = state[6];
}
void H_25(double *state, double *unused, double *out_2053125876532739177) {
   out_2053125876532739177[0] = 0;
   out_2053125876532739177[1] = 0;
   out_2053125876532739177[2] = 0;
   out_2053125876532739177[3] = 0;
   out_2053125876532739177[4] = 0;
   out_2053125876532739177[5] = 0;
   out_2053125876532739177[6] = 1;
   out_2053125876532739177[7] = 0;
   out_2053125876532739177[8] = 0;
}
void h_24(double *state, double *unused, double *out_8626736192149469552) {
   out_8626736192149469552[0] = state[4];
   out_8626736192149469552[1] = state[5];
}
void H_24(double *state, double *unused, double *out_119523722472760389) {
   out_119523722472760389[0] = 0;
   out_119523722472760389[1] = 0;
   out_119523722472760389[2] = 0;
   out_119523722472760389[3] = 0;
   out_119523722472760389[4] = 1;
   out_119523722472760389[5] = 0;
   out_119523722472760389[6] = 0;
   out_119523722472760389[7] = 0;
   out_119523722472760389[8] = 0;
   out_119523722472760389[9] = 0;
   out_119523722472760389[10] = 0;
   out_119523722472760389[11] = 0;
   out_119523722472760389[12] = 0;
   out_119523722472760389[13] = 0;
   out_119523722472760389[14] = 1;
   out_119523722472760389[15] = 0;
   out_119523722472760389[16] = 0;
   out_119523722472760389[17] = 0;
}
void h_30(double *state, double *unused, double *out_4997093107090697191) {
   out_4997093107090697191[0] = state[4];
}
void H_30(double *state, double *unused, double *out_8969816218024355932) {
   out_8969816218024355932[0] = 0;
   out_8969816218024355932[1] = 0;
   out_8969816218024355932[2] = 0;
   out_8969816218024355932[3] = 0;
   out_8969816218024355932[4] = 1;
   out_8969816218024355932[5] = 0;
   out_8969816218024355932[6] = 0;
   out_8969816218024355932[7] = 0;
   out_8969816218024355932[8] = 0;
}
void h_26(double *state, double *unused, double *out_34713109409403959) {
   out_34713109409403959[0] = state[7];
}
void H_26(double *state, double *unused, double *out_5357651846293539778) {
   out_5357651846293539778[0] = 0;
   out_5357651846293539778[1] = 0;
   out_5357651846293539778[2] = 0;
   out_5357651846293539778[3] = 0;
   out_5357651846293539778[4] = 0;
   out_5357651846293539778[5] = 0;
   out_5357651846293539778[6] = 0;
   out_5357651846293539778[7] = 1;
   out_5357651846293539778[8] = 0;
}
void h_27(double *state, double *unused, double *out_6395928148715762059) {
   out_6395928148715762059[0] = state[3];
}
void H_27(double *state, double *unused, double *out_6795052906223931021) {
   out_6795052906223931021[0] = 0;
   out_6795052906223931021[1] = 0;
   out_6795052906223931021[2] = 0;
   out_6795052906223931021[3] = 1;
   out_6795052906223931021[4] = 0;
   out_6795052906223931021[5] = 0;
   out_6795052906223931021[6] = 0;
   out_6795052906223931021[7] = 0;
   out_6795052906223931021[8] = 0;
}
void h_29(double *state, double *unused, double *out_8413366396739767207) {
   out_8413366396739767207[0] = state[1];
}
void H_29(double *state, double *unused, double *out_5081690179354379988) {
   out_5081690179354379988[0] = 0;
   out_5081690179354379988[1] = 1;
   out_5081690179354379988[2] = 0;
   out_5081690179354379988[3] = 0;
   out_5081690179354379988[4] = 0;
   out_5081690179354379988[5] = 0;
   out_5081690179354379988[6] = 0;
   out_5081690179354379988[7] = 0;
   out_5081690179354379988[8] = 0;
}
void h_28(double *state, double *unused, double *out_7049142657332943912) {
   out_7049142657332943912[0] = state[0];
}
void H_28(double *state, double *unused, double *out_708837715150586) {
   out_708837715150586[0] = 1;
   out_708837715150586[1] = 0;
   out_708837715150586[2] = 0;
   out_708837715150586[3] = 0;
   out_708837715150586[4] = 0;
   out_708837715150586[5] = 0;
   out_708837715150586[6] = 0;
   out_708837715150586[7] = 0;
   out_708837715150586[8] = 0;
}
void h_31(double *state, double *unused, double *out_1930928787610782890) {
   out_1930928787610782890[0] = state[8];
}
void H_31(double *state, double *unused, double *out_2083771838409699605) {
   out_2083771838409699605[0] = 0;
   out_2083771838409699605[1] = 0;
   out_2083771838409699605[2] = 0;
   out_2083771838409699605[3] = 0;
   out_2083771838409699605[4] = 0;
   out_2083771838409699605[5] = 0;
   out_2083771838409699605[6] = 0;
   out_2083771838409699605[7] = 0;
   out_2083771838409699605[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_9168682336158195836) {
  err_fun(nom_x, delta_x, out_9168682336158195836);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_5209405894281129857) {
  inv_err_fun(nom_x, true_x, out_5209405894281129857);
}
void car_H_mod_fun(double *state, double *out_8788279686404140347) {
  H_mod_fun(state, out_8788279686404140347);
}
void car_f_fun(double *state, double dt, double *out_3220267060095610864) {
  f_fun(state,  dt, out_3220267060095610864);
}
void car_F_fun(double *state, double dt, double *out_5498270358931541556) {
  F_fun(state,  dt, out_5498270358931541556);
}
void car_h_25(double *state, double *unused, double *out_5568378315864805240) {
  h_25(state, unused, out_5568378315864805240);
}
void car_H_25(double *state, double *unused, double *out_2053125876532739177) {
  H_25(state, unused, out_2053125876532739177);
}
void car_h_24(double *state, double *unused, double *out_8626736192149469552) {
  h_24(state, unused, out_8626736192149469552);
}
void car_H_24(double *state, double *unused, double *out_119523722472760389) {
  H_24(state, unused, out_119523722472760389);
}
void car_h_30(double *state, double *unused, double *out_4997093107090697191) {
  h_30(state, unused, out_4997093107090697191);
}
void car_H_30(double *state, double *unused, double *out_8969816218024355932) {
  H_30(state, unused, out_8969816218024355932);
}
void car_h_26(double *state, double *unused, double *out_34713109409403959) {
  h_26(state, unused, out_34713109409403959);
}
void car_H_26(double *state, double *unused, double *out_5357651846293539778) {
  H_26(state, unused, out_5357651846293539778);
}
void car_h_27(double *state, double *unused, double *out_6395928148715762059) {
  h_27(state, unused, out_6395928148715762059);
}
void car_H_27(double *state, double *unused, double *out_6795052906223931021) {
  H_27(state, unused, out_6795052906223931021);
}
void car_h_29(double *state, double *unused, double *out_8413366396739767207) {
  h_29(state, unused, out_8413366396739767207);
}
void car_H_29(double *state, double *unused, double *out_5081690179354379988) {
  H_29(state, unused, out_5081690179354379988);
}
void car_h_28(double *state, double *unused, double *out_7049142657332943912) {
  h_28(state, unused, out_7049142657332943912);
}
void car_H_28(double *state, double *unused, double *out_708837715150586) {
  H_28(state, unused, out_708837715150586);
}
void car_h_31(double *state, double *unused, double *out_1930928787610782890) {
  h_31(state, unused, out_1930928787610782890);
}
void car_H_31(double *state, double *unused, double *out_2083771838409699605) {
  H_31(state, unused, out_2083771838409699605);
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
