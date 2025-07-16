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
void err_fun(double *nom_x, double *delta_x, double *out_2720831518809093631) {
   out_2720831518809093631[0] = delta_x[0] + nom_x[0];
   out_2720831518809093631[1] = delta_x[1] + nom_x[1];
   out_2720831518809093631[2] = delta_x[2] + nom_x[2];
   out_2720831518809093631[3] = delta_x[3] + nom_x[3];
   out_2720831518809093631[4] = delta_x[4] + nom_x[4];
   out_2720831518809093631[5] = delta_x[5] + nom_x[5];
   out_2720831518809093631[6] = delta_x[6] + nom_x[6];
   out_2720831518809093631[7] = delta_x[7] + nom_x[7];
   out_2720831518809093631[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_5669322879472346789) {
   out_5669322879472346789[0] = -nom_x[0] + true_x[0];
   out_5669322879472346789[1] = -nom_x[1] + true_x[1];
   out_5669322879472346789[2] = -nom_x[2] + true_x[2];
   out_5669322879472346789[3] = -nom_x[3] + true_x[3];
   out_5669322879472346789[4] = -nom_x[4] + true_x[4];
   out_5669322879472346789[5] = -nom_x[5] + true_x[5];
   out_5669322879472346789[6] = -nom_x[6] + true_x[6];
   out_5669322879472346789[7] = -nom_x[7] + true_x[7];
   out_5669322879472346789[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_3032044944192446983) {
   out_3032044944192446983[0] = 1.0;
   out_3032044944192446983[1] = 0.0;
   out_3032044944192446983[2] = 0.0;
   out_3032044944192446983[3] = 0.0;
   out_3032044944192446983[4] = 0.0;
   out_3032044944192446983[5] = 0.0;
   out_3032044944192446983[6] = 0.0;
   out_3032044944192446983[7] = 0.0;
   out_3032044944192446983[8] = 0.0;
   out_3032044944192446983[9] = 0.0;
   out_3032044944192446983[10] = 1.0;
   out_3032044944192446983[11] = 0.0;
   out_3032044944192446983[12] = 0.0;
   out_3032044944192446983[13] = 0.0;
   out_3032044944192446983[14] = 0.0;
   out_3032044944192446983[15] = 0.0;
   out_3032044944192446983[16] = 0.0;
   out_3032044944192446983[17] = 0.0;
   out_3032044944192446983[18] = 0.0;
   out_3032044944192446983[19] = 0.0;
   out_3032044944192446983[20] = 1.0;
   out_3032044944192446983[21] = 0.0;
   out_3032044944192446983[22] = 0.0;
   out_3032044944192446983[23] = 0.0;
   out_3032044944192446983[24] = 0.0;
   out_3032044944192446983[25] = 0.0;
   out_3032044944192446983[26] = 0.0;
   out_3032044944192446983[27] = 0.0;
   out_3032044944192446983[28] = 0.0;
   out_3032044944192446983[29] = 0.0;
   out_3032044944192446983[30] = 1.0;
   out_3032044944192446983[31] = 0.0;
   out_3032044944192446983[32] = 0.0;
   out_3032044944192446983[33] = 0.0;
   out_3032044944192446983[34] = 0.0;
   out_3032044944192446983[35] = 0.0;
   out_3032044944192446983[36] = 0.0;
   out_3032044944192446983[37] = 0.0;
   out_3032044944192446983[38] = 0.0;
   out_3032044944192446983[39] = 0.0;
   out_3032044944192446983[40] = 1.0;
   out_3032044944192446983[41] = 0.0;
   out_3032044944192446983[42] = 0.0;
   out_3032044944192446983[43] = 0.0;
   out_3032044944192446983[44] = 0.0;
   out_3032044944192446983[45] = 0.0;
   out_3032044944192446983[46] = 0.0;
   out_3032044944192446983[47] = 0.0;
   out_3032044944192446983[48] = 0.0;
   out_3032044944192446983[49] = 0.0;
   out_3032044944192446983[50] = 1.0;
   out_3032044944192446983[51] = 0.0;
   out_3032044944192446983[52] = 0.0;
   out_3032044944192446983[53] = 0.0;
   out_3032044944192446983[54] = 0.0;
   out_3032044944192446983[55] = 0.0;
   out_3032044944192446983[56] = 0.0;
   out_3032044944192446983[57] = 0.0;
   out_3032044944192446983[58] = 0.0;
   out_3032044944192446983[59] = 0.0;
   out_3032044944192446983[60] = 1.0;
   out_3032044944192446983[61] = 0.0;
   out_3032044944192446983[62] = 0.0;
   out_3032044944192446983[63] = 0.0;
   out_3032044944192446983[64] = 0.0;
   out_3032044944192446983[65] = 0.0;
   out_3032044944192446983[66] = 0.0;
   out_3032044944192446983[67] = 0.0;
   out_3032044944192446983[68] = 0.0;
   out_3032044944192446983[69] = 0.0;
   out_3032044944192446983[70] = 1.0;
   out_3032044944192446983[71] = 0.0;
   out_3032044944192446983[72] = 0.0;
   out_3032044944192446983[73] = 0.0;
   out_3032044944192446983[74] = 0.0;
   out_3032044944192446983[75] = 0.0;
   out_3032044944192446983[76] = 0.0;
   out_3032044944192446983[77] = 0.0;
   out_3032044944192446983[78] = 0.0;
   out_3032044944192446983[79] = 0.0;
   out_3032044944192446983[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_22366909949606488) {
   out_22366909949606488[0] = state[0];
   out_22366909949606488[1] = state[1];
   out_22366909949606488[2] = state[2];
   out_22366909949606488[3] = state[3];
   out_22366909949606488[4] = state[4];
   out_22366909949606488[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8000000000000007*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_22366909949606488[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_22366909949606488[7] = state[7];
   out_22366909949606488[8] = state[8];
}
void F_fun(double *state, double dt, double *out_5191748143905924473) {
   out_5191748143905924473[0] = 1;
   out_5191748143905924473[1] = 0;
   out_5191748143905924473[2] = 0;
   out_5191748143905924473[3] = 0;
   out_5191748143905924473[4] = 0;
   out_5191748143905924473[5] = 0;
   out_5191748143905924473[6] = 0;
   out_5191748143905924473[7] = 0;
   out_5191748143905924473[8] = 0;
   out_5191748143905924473[9] = 0;
   out_5191748143905924473[10] = 1;
   out_5191748143905924473[11] = 0;
   out_5191748143905924473[12] = 0;
   out_5191748143905924473[13] = 0;
   out_5191748143905924473[14] = 0;
   out_5191748143905924473[15] = 0;
   out_5191748143905924473[16] = 0;
   out_5191748143905924473[17] = 0;
   out_5191748143905924473[18] = 0;
   out_5191748143905924473[19] = 0;
   out_5191748143905924473[20] = 1;
   out_5191748143905924473[21] = 0;
   out_5191748143905924473[22] = 0;
   out_5191748143905924473[23] = 0;
   out_5191748143905924473[24] = 0;
   out_5191748143905924473[25] = 0;
   out_5191748143905924473[26] = 0;
   out_5191748143905924473[27] = 0;
   out_5191748143905924473[28] = 0;
   out_5191748143905924473[29] = 0;
   out_5191748143905924473[30] = 1;
   out_5191748143905924473[31] = 0;
   out_5191748143905924473[32] = 0;
   out_5191748143905924473[33] = 0;
   out_5191748143905924473[34] = 0;
   out_5191748143905924473[35] = 0;
   out_5191748143905924473[36] = 0;
   out_5191748143905924473[37] = 0;
   out_5191748143905924473[38] = 0;
   out_5191748143905924473[39] = 0;
   out_5191748143905924473[40] = 1;
   out_5191748143905924473[41] = 0;
   out_5191748143905924473[42] = 0;
   out_5191748143905924473[43] = 0;
   out_5191748143905924473[44] = 0;
   out_5191748143905924473[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_5191748143905924473[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_5191748143905924473[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_5191748143905924473[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_5191748143905924473[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_5191748143905924473[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_5191748143905924473[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_5191748143905924473[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_5191748143905924473[53] = -9.8000000000000007*dt;
   out_5191748143905924473[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_5191748143905924473[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_5191748143905924473[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_5191748143905924473[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_5191748143905924473[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_5191748143905924473[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_5191748143905924473[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_5191748143905924473[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_5191748143905924473[62] = 0;
   out_5191748143905924473[63] = 0;
   out_5191748143905924473[64] = 0;
   out_5191748143905924473[65] = 0;
   out_5191748143905924473[66] = 0;
   out_5191748143905924473[67] = 0;
   out_5191748143905924473[68] = 0;
   out_5191748143905924473[69] = 0;
   out_5191748143905924473[70] = 1;
   out_5191748143905924473[71] = 0;
   out_5191748143905924473[72] = 0;
   out_5191748143905924473[73] = 0;
   out_5191748143905924473[74] = 0;
   out_5191748143905924473[75] = 0;
   out_5191748143905924473[76] = 0;
   out_5191748143905924473[77] = 0;
   out_5191748143905924473[78] = 0;
   out_5191748143905924473[79] = 0;
   out_5191748143905924473[80] = 1;
}
void h_25(double *state, double *unused, double *out_6689287487861708910) {
   out_6689287487861708910[0] = state[6];
}
void H_25(double *state, double *unused, double *out_7935736769377111823) {
   out_7935736769377111823[0] = 0;
   out_7935736769377111823[1] = 0;
   out_7935736769377111823[2] = 0;
   out_7935736769377111823[3] = 0;
   out_7935736769377111823[4] = 0;
   out_7935736769377111823[5] = 0;
   out_7935736769377111823[6] = 1;
   out_7935736769377111823[7] = 0;
   out_7935736769377111823[8] = 0;
}
void h_24(double *state, double *unused, double *out_5847146628445868711) {
   out_5847146628445868711[0] = state[4];
   out_5847146628445868711[1] = state[5];
}
void H_24(double *state, double *unused, double *out_493062176388395503) {
   out_493062176388395503[0] = 0;
   out_493062176388395503[1] = 0;
   out_493062176388395503[2] = 0;
   out_493062176388395503[3] = 0;
   out_493062176388395503[4] = 1;
   out_493062176388395503[5] = 0;
   out_493062176388395503[6] = 0;
   out_493062176388395503[7] = 0;
   out_493062176388395503[8] = 0;
   out_493062176388395503[9] = 0;
   out_493062176388395503[10] = 0;
   out_493062176388395503[11] = 0;
   out_493062176388395503[12] = 0;
   out_493062176388395503[13] = 0;
   out_493062176388395503[14] = 1;
   out_493062176388395503[15] = 0;
   out_493062176388395503[16] = 0;
   out_493062176388395503[17] = 0;
}
void h_30(double *state, double *unused, double *out_2448429796822142272) {
   out_2448429796822142272[0] = state[4];
}
void H_30(double *state, double *unused, double *out_3408040439249503625) {
   out_3408040439249503625[0] = 0;
   out_3408040439249503625[1] = 0;
   out_3408040439249503625[2] = 0;
   out_3408040439249503625[3] = 0;
   out_3408040439249503625[4] = 1;
   out_3408040439249503625[5] = 0;
   out_3408040439249503625[6] = 0;
   out_3408040439249503625[7] = 0;
   out_3408040439249503625[8] = 0;
}
void h_26(double *state, double *unused, double *out_6873790712120373805) {
   out_6873790712120373805[0] = state[7];
}
void H_26(double *state, double *unused, double *out_4194233450503055599) {
   out_4194233450503055599[0] = 0;
   out_4194233450503055599[1] = 0;
   out_4194233450503055599[2] = 0;
   out_4194233450503055599[3] = 0;
   out_4194233450503055599[4] = 0;
   out_4194233450503055599[5] = 0;
   out_4194233450503055599[6] = 0;
   out_4194233450503055599[7] = 1;
   out_4194233450503055599[8] = 0;
}
void h_27(double *state, double *unused, double *out_6755783318186997061) {
   out_6755783318186997061[0] = state[3];
}
void H_27(double *state, double *unused, double *out_1233277127449078714) {
   out_1233277127449078714[0] = 0;
   out_1233277127449078714[1] = 0;
   out_1233277127449078714[2] = 0;
   out_1233277127449078714[3] = 1;
   out_1233277127449078714[4] = 0;
   out_1233277127449078714[5] = 0;
   out_1233277127449078714[6] = 0;
   out_1233277127449078714[7] = 0;
   out_1233277127449078714[8] = 0;
}
void h_29(double *state, double *unused, double *out_7592657457243182691) {
   out_7592657457243182691[0] = state[1];
}
void H_29(double *state, double *unused, double *out_3918271783563895809) {
   out_3918271783563895809[0] = 0;
   out_3918271783563895809[1] = 1;
   out_3918271783563895809[2] = 0;
   out_3918271783563895809[3] = 0;
   out_3918271783563895809[4] = 0;
   out_3918271783563895809[5] = 0;
   out_3918271783563895809[6] = 0;
   out_3918271783563895809[7] = 0;
   out_3918271783563895809[8] = 0;
}
void h_28(double *state, double *unused, double *out_8654174704078221870) {
   out_8654174704078221870[0] = state[0];
}
void H_28(double *state, double *unused, double *out_5881902055129222060) {
   out_5881902055129222060[0] = 1;
   out_5881902055129222060[1] = 0;
   out_5881902055129222060[2] = 0;
   out_5881902055129222060[3] = 0;
   out_5881902055129222060[4] = 0;
   out_5881902055129222060[5] = 0;
   out_5881902055129222060[6] = 0;
   out_5881902055129222060[7] = 0;
   out_5881902055129222060[8] = 0;
}
void h_31(double *state, double *unused, double *out_6414093425577203021) {
   out_6414093425577203021[0] = state[8];
}
void H_31(double *state, double *unused, double *out_3568025348269704123) {
   out_3568025348269704123[0] = 0;
   out_3568025348269704123[1] = 0;
   out_3568025348269704123[2] = 0;
   out_3568025348269704123[3] = 0;
   out_3568025348269704123[4] = 0;
   out_3568025348269704123[5] = 0;
   out_3568025348269704123[6] = 0;
   out_3568025348269704123[7] = 0;
   out_3568025348269704123[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_2720831518809093631) {
  err_fun(nom_x, delta_x, out_2720831518809093631);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_5669322879472346789) {
  inv_err_fun(nom_x, true_x, out_5669322879472346789);
}
void car_H_mod_fun(double *state, double *out_3032044944192446983) {
  H_mod_fun(state, out_3032044944192446983);
}
void car_f_fun(double *state, double dt, double *out_22366909949606488) {
  f_fun(state,  dt, out_22366909949606488);
}
void car_F_fun(double *state, double dt, double *out_5191748143905924473) {
  F_fun(state,  dt, out_5191748143905924473);
}
void car_h_25(double *state, double *unused, double *out_6689287487861708910) {
  h_25(state, unused, out_6689287487861708910);
}
void car_H_25(double *state, double *unused, double *out_7935736769377111823) {
  H_25(state, unused, out_7935736769377111823);
}
void car_h_24(double *state, double *unused, double *out_5847146628445868711) {
  h_24(state, unused, out_5847146628445868711);
}
void car_H_24(double *state, double *unused, double *out_493062176388395503) {
  H_24(state, unused, out_493062176388395503);
}
void car_h_30(double *state, double *unused, double *out_2448429796822142272) {
  h_30(state, unused, out_2448429796822142272);
}
void car_H_30(double *state, double *unused, double *out_3408040439249503625) {
  H_30(state, unused, out_3408040439249503625);
}
void car_h_26(double *state, double *unused, double *out_6873790712120373805) {
  h_26(state, unused, out_6873790712120373805);
}
void car_H_26(double *state, double *unused, double *out_4194233450503055599) {
  H_26(state, unused, out_4194233450503055599);
}
void car_h_27(double *state, double *unused, double *out_6755783318186997061) {
  h_27(state, unused, out_6755783318186997061);
}
void car_H_27(double *state, double *unused, double *out_1233277127449078714) {
  H_27(state, unused, out_1233277127449078714);
}
void car_h_29(double *state, double *unused, double *out_7592657457243182691) {
  h_29(state, unused, out_7592657457243182691);
}
void car_H_29(double *state, double *unused, double *out_3918271783563895809) {
  H_29(state, unused, out_3918271783563895809);
}
void car_h_28(double *state, double *unused, double *out_8654174704078221870) {
  h_28(state, unused, out_8654174704078221870);
}
void car_H_28(double *state, double *unused, double *out_5881902055129222060) {
  H_28(state, unused, out_5881902055129222060);
}
void car_h_31(double *state, double *unused, double *out_6414093425577203021) {
  h_31(state, unused, out_6414093425577203021);
}
void car_H_31(double *state, double *unused, double *out_3568025348269704123) {
  H_31(state, unused, out_3568025348269704123);
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
