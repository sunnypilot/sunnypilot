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
 *                      Code generated with SymPy 1.11.1                      *
 *                                                                            *
 *              See http://www.sympy.org/ for more information.               *
 *                                                                            *
 *                         This file is part of 'ekf'                         *
 ******************************************************************************/
void err_fun(double *nom_x, double *delta_x, double *out_2634337573502312531) {
   out_2634337573502312531[0] = delta_x[0] + nom_x[0];
   out_2634337573502312531[1] = delta_x[1] + nom_x[1];
   out_2634337573502312531[2] = delta_x[2] + nom_x[2];
   out_2634337573502312531[3] = delta_x[3] + nom_x[3];
   out_2634337573502312531[4] = delta_x[4] + nom_x[4];
   out_2634337573502312531[5] = delta_x[5] + nom_x[5];
   out_2634337573502312531[6] = delta_x[6] + nom_x[6];
   out_2634337573502312531[7] = delta_x[7] + nom_x[7];
   out_2634337573502312531[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_364624501276122878) {
   out_364624501276122878[0] = -nom_x[0] + true_x[0];
   out_364624501276122878[1] = -nom_x[1] + true_x[1];
   out_364624501276122878[2] = -nom_x[2] + true_x[2];
   out_364624501276122878[3] = -nom_x[3] + true_x[3];
   out_364624501276122878[4] = -nom_x[4] + true_x[4];
   out_364624501276122878[5] = -nom_x[5] + true_x[5];
   out_364624501276122878[6] = -nom_x[6] + true_x[6];
   out_364624501276122878[7] = -nom_x[7] + true_x[7];
   out_364624501276122878[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_8283385258124076174) {
   out_8283385258124076174[0] = 1.0;
   out_8283385258124076174[1] = 0;
   out_8283385258124076174[2] = 0;
   out_8283385258124076174[3] = 0;
   out_8283385258124076174[4] = 0;
   out_8283385258124076174[5] = 0;
   out_8283385258124076174[6] = 0;
   out_8283385258124076174[7] = 0;
   out_8283385258124076174[8] = 0;
   out_8283385258124076174[9] = 0;
   out_8283385258124076174[10] = 1.0;
   out_8283385258124076174[11] = 0;
   out_8283385258124076174[12] = 0;
   out_8283385258124076174[13] = 0;
   out_8283385258124076174[14] = 0;
   out_8283385258124076174[15] = 0;
   out_8283385258124076174[16] = 0;
   out_8283385258124076174[17] = 0;
   out_8283385258124076174[18] = 0;
   out_8283385258124076174[19] = 0;
   out_8283385258124076174[20] = 1.0;
   out_8283385258124076174[21] = 0;
   out_8283385258124076174[22] = 0;
   out_8283385258124076174[23] = 0;
   out_8283385258124076174[24] = 0;
   out_8283385258124076174[25] = 0;
   out_8283385258124076174[26] = 0;
   out_8283385258124076174[27] = 0;
   out_8283385258124076174[28] = 0;
   out_8283385258124076174[29] = 0;
   out_8283385258124076174[30] = 1.0;
   out_8283385258124076174[31] = 0;
   out_8283385258124076174[32] = 0;
   out_8283385258124076174[33] = 0;
   out_8283385258124076174[34] = 0;
   out_8283385258124076174[35] = 0;
   out_8283385258124076174[36] = 0;
   out_8283385258124076174[37] = 0;
   out_8283385258124076174[38] = 0;
   out_8283385258124076174[39] = 0;
   out_8283385258124076174[40] = 1.0;
   out_8283385258124076174[41] = 0;
   out_8283385258124076174[42] = 0;
   out_8283385258124076174[43] = 0;
   out_8283385258124076174[44] = 0;
   out_8283385258124076174[45] = 0;
   out_8283385258124076174[46] = 0;
   out_8283385258124076174[47] = 0;
   out_8283385258124076174[48] = 0;
   out_8283385258124076174[49] = 0;
   out_8283385258124076174[50] = 1.0;
   out_8283385258124076174[51] = 0;
   out_8283385258124076174[52] = 0;
   out_8283385258124076174[53] = 0;
   out_8283385258124076174[54] = 0;
   out_8283385258124076174[55] = 0;
   out_8283385258124076174[56] = 0;
   out_8283385258124076174[57] = 0;
   out_8283385258124076174[58] = 0;
   out_8283385258124076174[59] = 0;
   out_8283385258124076174[60] = 1.0;
   out_8283385258124076174[61] = 0;
   out_8283385258124076174[62] = 0;
   out_8283385258124076174[63] = 0;
   out_8283385258124076174[64] = 0;
   out_8283385258124076174[65] = 0;
   out_8283385258124076174[66] = 0;
   out_8283385258124076174[67] = 0;
   out_8283385258124076174[68] = 0;
   out_8283385258124076174[69] = 0;
   out_8283385258124076174[70] = 1.0;
   out_8283385258124076174[71] = 0;
   out_8283385258124076174[72] = 0;
   out_8283385258124076174[73] = 0;
   out_8283385258124076174[74] = 0;
   out_8283385258124076174[75] = 0;
   out_8283385258124076174[76] = 0;
   out_8283385258124076174[77] = 0;
   out_8283385258124076174[78] = 0;
   out_8283385258124076174[79] = 0;
   out_8283385258124076174[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_1842212169269794394) {
   out_1842212169269794394[0] = state[0];
   out_1842212169269794394[1] = state[1];
   out_1842212169269794394[2] = state[2];
   out_1842212169269794394[3] = state[3];
   out_1842212169269794394[4] = state[4];
   out_1842212169269794394[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8000000000000007*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_1842212169269794394[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_1842212169269794394[7] = state[7];
   out_1842212169269794394[8] = state[8];
}
void F_fun(double *state, double dt, double *out_844160246145237490) {
   out_844160246145237490[0] = 1;
   out_844160246145237490[1] = 0;
   out_844160246145237490[2] = 0;
   out_844160246145237490[3] = 0;
   out_844160246145237490[4] = 0;
   out_844160246145237490[5] = 0;
   out_844160246145237490[6] = 0;
   out_844160246145237490[7] = 0;
   out_844160246145237490[8] = 0;
   out_844160246145237490[9] = 0;
   out_844160246145237490[10] = 1;
   out_844160246145237490[11] = 0;
   out_844160246145237490[12] = 0;
   out_844160246145237490[13] = 0;
   out_844160246145237490[14] = 0;
   out_844160246145237490[15] = 0;
   out_844160246145237490[16] = 0;
   out_844160246145237490[17] = 0;
   out_844160246145237490[18] = 0;
   out_844160246145237490[19] = 0;
   out_844160246145237490[20] = 1;
   out_844160246145237490[21] = 0;
   out_844160246145237490[22] = 0;
   out_844160246145237490[23] = 0;
   out_844160246145237490[24] = 0;
   out_844160246145237490[25] = 0;
   out_844160246145237490[26] = 0;
   out_844160246145237490[27] = 0;
   out_844160246145237490[28] = 0;
   out_844160246145237490[29] = 0;
   out_844160246145237490[30] = 1;
   out_844160246145237490[31] = 0;
   out_844160246145237490[32] = 0;
   out_844160246145237490[33] = 0;
   out_844160246145237490[34] = 0;
   out_844160246145237490[35] = 0;
   out_844160246145237490[36] = 0;
   out_844160246145237490[37] = 0;
   out_844160246145237490[38] = 0;
   out_844160246145237490[39] = 0;
   out_844160246145237490[40] = 1;
   out_844160246145237490[41] = 0;
   out_844160246145237490[42] = 0;
   out_844160246145237490[43] = 0;
   out_844160246145237490[44] = 0;
   out_844160246145237490[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_844160246145237490[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_844160246145237490[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_844160246145237490[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_844160246145237490[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_844160246145237490[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_844160246145237490[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_844160246145237490[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_844160246145237490[53] = -9.8000000000000007*dt;
   out_844160246145237490[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_844160246145237490[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_844160246145237490[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_844160246145237490[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_844160246145237490[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_844160246145237490[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_844160246145237490[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_844160246145237490[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_844160246145237490[62] = 0;
   out_844160246145237490[63] = 0;
   out_844160246145237490[64] = 0;
   out_844160246145237490[65] = 0;
   out_844160246145237490[66] = 0;
   out_844160246145237490[67] = 0;
   out_844160246145237490[68] = 0;
   out_844160246145237490[69] = 0;
   out_844160246145237490[70] = 1;
   out_844160246145237490[71] = 0;
   out_844160246145237490[72] = 0;
   out_844160246145237490[73] = 0;
   out_844160246145237490[74] = 0;
   out_844160246145237490[75] = 0;
   out_844160246145237490[76] = 0;
   out_844160246145237490[77] = 0;
   out_844160246145237490[78] = 0;
   out_844160246145237490[79] = 0;
   out_844160246145237490[80] = 1;
}
void h_25(double *state, double *unused, double *out_1303483449461821305) {
   out_1303483449461821305[0] = state[6];
}
void H_25(double *state, double *unused, double *out_8922345036839792704) {
   out_8922345036839792704[0] = 0;
   out_8922345036839792704[1] = 0;
   out_8922345036839792704[2] = 0;
   out_8922345036839792704[3] = 0;
   out_8922345036839792704[4] = 0;
   out_8922345036839792704[5] = 0;
   out_8922345036839792704[6] = 1;
   out_8922345036839792704[7] = 0;
   out_8922345036839792704[8] = 0;
}
void h_24(double *state, double *unused, double *out_1550963005683787860) {
   out_1550963005683787860[0] = state[4];
   out_1550963005683787860[1] = state[5];
}
void H_24(double *state, double *unused, double *out_6745130613232642731) {
   out_6745130613232642731[0] = 0;
   out_6745130613232642731[1] = 0;
   out_6745130613232642731[2] = 0;
   out_6745130613232642731[3] = 0;
   out_6745130613232642731[4] = 1;
   out_6745130613232642731[5] = 0;
   out_6745130613232642731[6] = 0;
   out_6745130613232642731[7] = 0;
   out_6745130613232642731[8] = 0;
   out_6745130613232642731[9] = 0;
   out_6745130613232642731[10] = 0;
   out_6745130613232642731[11] = 0;
   out_6745130613232642731[12] = 0;
   out_6745130613232642731[13] = 0;
   out_6745130613232642731[14] = 1;
   out_6745130613232642731[15] = 0;
   out_6745130613232642731[16] = 0;
   out_6745130613232642731[17] = 0;
}
void h_30(double *state, double *unused, double *out_7891311375938116468) {
   out_7891311375938116468[0] = state[4];
}
void H_30(double *state, double *unused, double *out_6404012078332544077) {
   out_6404012078332544077[0] = 0;
   out_6404012078332544077[1] = 0;
   out_6404012078332544077[2] = 0;
   out_6404012078332544077[3] = 0;
   out_6404012078332544077[4] = 1;
   out_6404012078332544077[5] = 0;
   out_6404012078332544077[6] = 0;
   out_6404012078332544077[7] = 0;
   out_6404012078332544077[8] = 0;
}
void h_26(double *state, double *unused, double *out_8834821228839778903) {
   out_8834821228839778903[0] = state[7];
}
void H_26(double *state, double *unused, double *out_5782895717995702688) {
   out_5782895717995702688[0] = 0;
   out_5782895717995702688[1] = 0;
   out_5782895717995702688[2] = 0;
   out_5782895717995702688[3] = 0;
   out_5782895717995702688[4] = 0;
   out_5782895717995702688[5] = 0;
   out_5782895717995702688[6] = 0;
   out_5782895717995702688[7] = 1;
   out_5782895717995702688[8] = 0;
}
void h_27(double *state, double *unused, double *out_5701435530743450317) {
   out_5701435530743450317[0] = state[3];
}
void H_27(double *state, double *unused, double *out_8578775390132968988) {
   out_8578775390132968988[0] = 0;
   out_8578775390132968988[1] = 0;
   out_8578775390132968988[2] = 0;
   out_8578775390132968988[3] = 1;
   out_8578775390132968988[4] = 0;
   out_8578775390132968988[5] = 0;
   out_8578775390132968988[6] = 0;
   out_8578775390132968988[7] = 0;
   out_8578775390132968988[8] = 0;
}
void h_29(double *state, double *unused, double *out_4854525324493783783) {
   out_4854525324493783783[0] = state[1];
}
void H_29(double *state, double *unused, double *out_5893780734018151893) {
   out_5893780734018151893[0] = 0;
   out_5893780734018151893[1] = 1;
   out_5893780734018151893[2] = 0;
   out_5893780734018151893[3] = 0;
   out_5893780734018151893[4] = 0;
   out_5893780734018151893[5] = 0;
   out_5893780734018151893[6] = 0;
   out_5893780734018151893[7] = 0;
   out_5893780734018151893[8] = 0;
}
void h_28(double *state, double *unused, double *out_697605986670398829) {
   out_697605986670398829[0] = state[0];
}
void H_28(double *state, double *unused, double *out_7470564322621869149) {
   out_7470564322621869149[0] = 1;
   out_7470564322621869149[1] = 0;
   out_7470564322621869149[2] = 0;
   out_7470564322621869149[3] = 0;
   out_7470564322621869149[4] = 0;
   out_7470564322621869149[5] = 0;
   out_7470564322621869149[6] = 0;
   out_7470564322621869149[7] = 0;
   out_7470564322621869149[8] = 0;
}
void h_31(double *state, double *unused, double *out_1460670117812950450) {
   out_1460670117812950450[0] = state[8];
}
void H_31(double *state, double *unused, double *out_5156687615762351212) {
   out_5156687615762351212[0] = 0;
   out_5156687615762351212[1] = 0;
   out_5156687615762351212[2] = 0;
   out_5156687615762351212[3] = 0;
   out_5156687615762351212[4] = 0;
   out_5156687615762351212[5] = 0;
   out_5156687615762351212[6] = 0;
   out_5156687615762351212[7] = 0;
   out_5156687615762351212[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_2634337573502312531) {
  err_fun(nom_x, delta_x, out_2634337573502312531);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_364624501276122878) {
  inv_err_fun(nom_x, true_x, out_364624501276122878);
}
void car_H_mod_fun(double *state, double *out_8283385258124076174) {
  H_mod_fun(state, out_8283385258124076174);
}
void car_f_fun(double *state, double dt, double *out_1842212169269794394) {
  f_fun(state,  dt, out_1842212169269794394);
}
void car_F_fun(double *state, double dt, double *out_844160246145237490) {
  F_fun(state,  dt, out_844160246145237490);
}
void car_h_25(double *state, double *unused, double *out_1303483449461821305) {
  h_25(state, unused, out_1303483449461821305);
}
void car_H_25(double *state, double *unused, double *out_8922345036839792704) {
  H_25(state, unused, out_8922345036839792704);
}
void car_h_24(double *state, double *unused, double *out_1550963005683787860) {
  h_24(state, unused, out_1550963005683787860);
}
void car_H_24(double *state, double *unused, double *out_6745130613232642731) {
  H_24(state, unused, out_6745130613232642731);
}
void car_h_30(double *state, double *unused, double *out_7891311375938116468) {
  h_30(state, unused, out_7891311375938116468);
}
void car_H_30(double *state, double *unused, double *out_6404012078332544077) {
  H_30(state, unused, out_6404012078332544077);
}
void car_h_26(double *state, double *unused, double *out_8834821228839778903) {
  h_26(state, unused, out_8834821228839778903);
}
void car_H_26(double *state, double *unused, double *out_5782895717995702688) {
  H_26(state, unused, out_5782895717995702688);
}
void car_h_27(double *state, double *unused, double *out_5701435530743450317) {
  h_27(state, unused, out_5701435530743450317);
}
void car_H_27(double *state, double *unused, double *out_8578775390132968988) {
  H_27(state, unused, out_8578775390132968988);
}
void car_h_29(double *state, double *unused, double *out_4854525324493783783) {
  h_29(state, unused, out_4854525324493783783);
}
void car_H_29(double *state, double *unused, double *out_5893780734018151893) {
  H_29(state, unused, out_5893780734018151893);
}
void car_h_28(double *state, double *unused, double *out_697605986670398829) {
  h_28(state, unused, out_697605986670398829);
}
void car_H_28(double *state, double *unused, double *out_7470564322621869149) {
  H_28(state, unused, out_7470564322621869149);
}
void car_h_31(double *state, double *unused, double *out_1460670117812950450) {
  h_31(state, unused, out_1460670117812950450);
}
void car_H_31(double *state, double *unused, double *out_5156687615762351212) {
  H_31(state, unused, out_5156687615762351212);
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
