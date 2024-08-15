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
void err_fun(double *nom_x, double *delta_x, double *out_7323774311990484810) {
   out_7323774311990484810[0] = delta_x[0] + nom_x[0];
   out_7323774311990484810[1] = delta_x[1] + nom_x[1];
   out_7323774311990484810[2] = delta_x[2] + nom_x[2];
   out_7323774311990484810[3] = delta_x[3] + nom_x[3];
   out_7323774311990484810[4] = delta_x[4] + nom_x[4];
   out_7323774311990484810[5] = delta_x[5] + nom_x[5];
   out_7323774311990484810[6] = delta_x[6] + nom_x[6];
   out_7323774311990484810[7] = delta_x[7] + nom_x[7];
   out_7323774311990484810[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_3361913979724621566) {
   out_3361913979724621566[0] = -nom_x[0] + true_x[0];
   out_3361913979724621566[1] = -nom_x[1] + true_x[1];
   out_3361913979724621566[2] = -nom_x[2] + true_x[2];
   out_3361913979724621566[3] = -nom_x[3] + true_x[3];
   out_3361913979724621566[4] = -nom_x[4] + true_x[4];
   out_3361913979724621566[5] = -nom_x[5] + true_x[5];
   out_3361913979724621566[6] = -nom_x[6] + true_x[6];
   out_3361913979724621566[7] = -nom_x[7] + true_x[7];
   out_3361913979724621566[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_7670763674896342596) {
   out_7670763674896342596[0] = 1.0;
   out_7670763674896342596[1] = 0;
   out_7670763674896342596[2] = 0;
   out_7670763674896342596[3] = 0;
   out_7670763674896342596[4] = 0;
   out_7670763674896342596[5] = 0;
   out_7670763674896342596[6] = 0;
   out_7670763674896342596[7] = 0;
   out_7670763674896342596[8] = 0;
   out_7670763674896342596[9] = 0;
   out_7670763674896342596[10] = 1.0;
   out_7670763674896342596[11] = 0;
   out_7670763674896342596[12] = 0;
   out_7670763674896342596[13] = 0;
   out_7670763674896342596[14] = 0;
   out_7670763674896342596[15] = 0;
   out_7670763674896342596[16] = 0;
   out_7670763674896342596[17] = 0;
   out_7670763674896342596[18] = 0;
   out_7670763674896342596[19] = 0;
   out_7670763674896342596[20] = 1.0;
   out_7670763674896342596[21] = 0;
   out_7670763674896342596[22] = 0;
   out_7670763674896342596[23] = 0;
   out_7670763674896342596[24] = 0;
   out_7670763674896342596[25] = 0;
   out_7670763674896342596[26] = 0;
   out_7670763674896342596[27] = 0;
   out_7670763674896342596[28] = 0;
   out_7670763674896342596[29] = 0;
   out_7670763674896342596[30] = 1.0;
   out_7670763674896342596[31] = 0;
   out_7670763674896342596[32] = 0;
   out_7670763674896342596[33] = 0;
   out_7670763674896342596[34] = 0;
   out_7670763674896342596[35] = 0;
   out_7670763674896342596[36] = 0;
   out_7670763674896342596[37] = 0;
   out_7670763674896342596[38] = 0;
   out_7670763674896342596[39] = 0;
   out_7670763674896342596[40] = 1.0;
   out_7670763674896342596[41] = 0;
   out_7670763674896342596[42] = 0;
   out_7670763674896342596[43] = 0;
   out_7670763674896342596[44] = 0;
   out_7670763674896342596[45] = 0;
   out_7670763674896342596[46] = 0;
   out_7670763674896342596[47] = 0;
   out_7670763674896342596[48] = 0;
   out_7670763674896342596[49] = 0;
   out_7670763674896342596[50] = 1.0;
   out_7670763674896342596[51] = 0;
   out_7670763674896342596[52] = 0;
   out_7670763674896342596[53] = 0;
   out_7670763674896342596[54] = 0;
   out_7670763674896342596[55] = 0;
   out_7670763674896342596[56] = 0;
   out_7670763674896342596[57] = 0;
   out_7670763674896342596[58] = 0;
   out_7670763674896342596[59] = 0;
   out_7670763674896342596[60] = 1.0;
   out_7670763674896342596[61] = 0;
   out_7670763674896342596[62] = 0;
   out_7670763674896342596[63] = 0;
   out_7670763674896342596[64] = 0;
   out_7670763674896342596[65] = 0;
   out_7670763674896342596[66] = 0;
   out_7670763674896342596[67] = 0;
   out_7670763674896342596[68] = 0;
   out_7670763674896342596[69] = 0;
   out_7670763674896342596[70] = 1.0;
   out_7670763674896342596[71] = 0;
   out_7670763674896342596[72] = 0;
   out_7670763674896342596[73] = 0;
   out_7670763674896342596[74] = 0;
   out_7670763674896342596[75] = 0;
   out_7670763674896342596[76] = 0;
   out_7670763674896342596[77] = 0;
   out_7670763674896342596[78] = 0;
   out_7670763674896342596[79] = 0;
   out_7670763674896342596[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_4442205562604345935) {
   out_4442205562604345935[0] = state[0];
   out_4442205562604345935[1] = state[1];
   out_4442205562604345935[2] = state[2];
   out_4442205562604345935[3] = state[3];
   out_4442205562604345935[4] = state[4];
   out_4442205562604345935[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8000000000000007*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_4442205562604345935[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_4442205562604345935[7] = state[7];
   out_4442205562604345935[8] = state[8];
}
void F_fun(double *state, double dt, double *out_3741498127708014361) {
   out_3741498127708014361[0] = 1;
   out_3741498127708014361[1] = 0;
   out_3741498127708014361[2] = 0;
   out_3741498127708014361[3] = 0;
   out_3741498127708014361[4] = 0;
   out_3741498127708014361[5] = 0;
   out_3741498127708014361[6] = 0;
   out_3741498127708014361[7] = 0;
   out_3741498127708014361[8] = 0;
   out_3741498127708014361[9] = 0;
   out_3741498127708014361[10] = 1;
   out_3741498127708014361[11] = 0;
   out_3741498127708014361[12] = 0;
   out_3741498127708014361[13] = 0;
   out_3741498127708014361[14] = 0;
   out_3741498127708014361[15] = 0;
   out_3741498127708014361[16] = 0;
   out_3741498127708014361[17] = 0;
   out_3741498127708014361[18] = 0;
   out_3741498127708014361[19] = 0;
   out_3741498127708014361[20] = 1;
   out_3741498127708014361[21] = 0;
   out_3741498127708014361[22] = 0;
   out_3741498127708014361[23] = 0;
   out_3741498127708014361[24] = 0;
   out_3741498127708014361[25] = 0;
   out_3741498127708014361[26] = 0;
   out_3741498127708014361[27] = 0;
   out_3741498127708014361[28] = 0;
   out_3741498127708014361[29] = 0;
   out_3741498127708014361[30] = 1;
   out_3741498127708014361[31] = 0;
   out_3741498127708014361[32] = 0;
   out_3741498127708014361[33] = 0;
   out_3741498127708014361[34] = 0;
   out_3741498127708014361[35] = 0;
   out_3741498127708014361[36] = 0;
   out_3741498127708014361[37] = 0;
   out_3741498127708014361[38] = 0;
   out_3741498127708014361[39] = 0;
   out_3741498127708014361[40] = 1;
   out_3741498127708014361[41] = 0;
   out_3741498127708014361[42] = 0;
   out_3741498127708014361[43] = 0;
   out_3741498127708014361[44] = 0;
   out_3741498127708014361[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_3741498127708014361[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_3741498127708014361[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_3741498127708014361[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_3741498127708014361[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_3741498127708014361[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_3741498127708014361[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_3741498127708014361[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_3741498127708014361[53] = -9.8000000000000007*dt;
   out_3741498127708014361[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_3741498127708014361[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_3741498127708014361[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_3741498127708014361[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_3741498127708014361[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_3741498127708014361[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_3741498127708014361[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_3741498127708014361[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_3741498127708014361[62] = 0;
   out_3741498127708014361[63] = 0;
   out_3741498127708014361[64] = 0;
   out_3741498127708014361[65] = 0;
   out_3741498127708014361[66] = 0;
   out_3741498127708014361[67] = 0;
   out_3741498127708014361[68] = 0;
   out_3741498127708014361[69] = 0;
   out_3741498127708014361[70] = 1;
   out_3741498127708014361[71] = 0;
   out_3741498127708014361[72] = 0;
   out_3741498127708014361[73] = 0;
   out_3741498127708014361[74] = 0;
   out_3741498127708014361[75] = 0;
   out_3741498127708014361[76] = 0;
   out_3741498127708014361[77] = 0;
   out_3741498127708014361[78] = 0;
   out_3741498127708014361[79] = 0;
   out_3741498127708014361[80] = 1;
}
void h_25(double *state, double *unused, double *out_8739001293148261377) {
   out_8739001293148261377[0] = state[6];
}
void H_25(double *state, double *unused, double *out_8219246077433628171) {
   out_8219246077433628171[0] = 0;
   out_8219246077433628171[1] = 0;
   out_8219246077433628171[2] = 0;
   out_8219246077433628171[3] = 0;
   out_8219246077433628171[4] = 0;
   out_8219246077433628171[5] = 0;
   out_8219246077433628171[6] = 1;
   out_8219246077433628171[7] = 0;
   out_8219246077433628171[8] = 0;
}
void h_24(double *state, double *unused, double *out_3866938681010227057) {
   out_3866938681010227057[0] = state[4];
   out_3866938681010227057[1] = state[5];
}
void H_24(double *state, double *unused, double *out_4661320478631305035) {
   out_4661320478631305035[0] = 0;
   out_4661320478631305035[1] = 0;
   out_4661320478631305035[2] = 0;
   out_4661320478631305035[3] = 0;
   out_4661320478631305035[4] = 1;
   out_4661320478631305035[5] = 0;
   out_4661320478631305035[6] = 0;
   out_4661320478631305035[7] = 0;
   out_4661320478631305035[8] = 0;
   out_4661320478631305035[9] = 0;
   out_4661320478631305035[10] = 0;
   out_4661320478631305035[11] = 0;
   out_4661320478631305035[12] = 0;
   out_4661320478631305035[13] = 0;
   out_4661320478631305035[14] = 1;
   out_4661320478631305035[15] = 0;
   out_4661320478631305035[16] = 0;
   out_4661320478631305035[17] = 0;
}
void h_30(double *state, double *unused, double *out_8463807230863755488) {
   out_8463807230863755488[0] = state[4];
}
void H_30(double *state, double *unused, double *out_1302555735942011416) {
   out_1302555735942011416[0] = 0;
   out_1302555735942011416[1] = 0;
   out_1302555735942011416[2] = 0;
   out_1302555735942011416[3] = 0;
   out_1302555735942011416[4] = 1;
   out_1302555735942011416[5] = 0;
   out_1302555735942011416[6] = 0;
   out_1302555735942011416[7] = 0;
   out_1302555735942011416[8] = 0;
}
void h_26(double *state, double *unused, double *out_4981263575184950483) {
   out_4981263575184950483[0] = state[7];
}
void H_26(double *state, double *unused, double *out_4914720107672827570) {
   out_4914720107672827570[0] = 0;
   out_4914720107672827570[1] = 0;
   out_4914720107672827570[2] = 0;
   out_4914720107672827570[3] = 0;
   out_4914720107672827570[4] = 0;
   out_4914720107672827570[5] = 0;
   out_4914720107672827570[6] = 0;
   out_4914720107672827570[7] = 1;
   out_4914720107672827570[8] = 0;
}
void h_27(double *state, double *unused, double *out_1946758319516529598) {
   out_1946758319516529598[0] = state[3];
}
void H_27(double *state, double *unused, double *out_3477319047742436327) {
   out_3477319047742436327[0] = 0;
   out_3477319047742436327[1] = 0;
   out_3477319047742436327[2] = 0;
   out_3477319047742436327[3] = 1;
   out_3477319047742436327[4] = 0;
   out_3477319047742436327[5] = 0;
   out_3477319047742436327[6] = 0;
   out_3477319047742436327[7] = 0;
   out_3477319047742436327[8] = 0;
}
void h_29(double *state, double *unused, double *out_9039426989944133693) {
   out_9039426989944133693[0] = state[1];
}
void H_29(double *state, double *unused, double *out_792324391627619232) {
   out_792324391627619232[0] = 0;
   out_792324391627619232[1] = 1;
   out_792324391627619232[2] = 0;
   out_792324391627619232[3] = 0;
   out_792324391627619232[4] = 0;
   out_792324391627619232[5] = 0;
   out_792324391627619232[6] = 0;
   out_792324391627619232[7] = 0;
   out_792324391627619232[8] = 0;
}
void h_28(double *state, double *unused, double *out_4551163640325227249) {
   out_4551163640325227249[0] = state[0];
}
void H_28(double *state, double *unused, double *out_5874723408697149806) {
   out_5874723408697149806[0] = 1;
   out_5874723408697149806[1] = 0;
   out_5874723408697149806[2] = 0;
   out_5874723408697149806[3] = 0;
   out_5874723408697149806[4] = 0;
   out_5874723408697149806[5] = 0;
   out_5874723408697149806[6] = 0;
   out_5874723408697149806[7] = 0;
   out_5874723408697149806[8] = 0;
}
void h_31(double *state, double *unused, double *out_7860862958278154023) {
   out_7860862958278154023[0] = state[8];
}
void H_31(double *state, double *unused, double *out_8188600115556667743) {
   out_8188600115556667743[0] = 0;
   out_8188600115556667743[1] = 0;
   out_8188600115556667743[2] = 0;
   out_8188600115556667743[3] = 0;
   out_8188600115556667743[4] = 0;
   out_8188600115556667743[5] = 0;
   out_8188600115556667743[6] = 0;
   out_8188600115556667743[7] = 0;
   out_8188600115556667743[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_7323774311990484810) {
  err_fun(nom_x, delta_x, out_7323774311990484810);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_3361913979724621566) {
  inv_err_fun(nom_x, true_x, out_3361913979724621566);
}
void car_H_mod_fun(double *state, double *out_7670763674896342596) {
  H_mod_fun(state, out_7670763674896342596);
}
void car_f_fun(double *state, double dt, double *out_4442205562604345935) {
  f_fun(state,  dt, out_4442205562604345935);
}
void car_F_fun(double *state, double dt, double *out_3741498127708014361) {
  F_fun(state,  dt, out_3741498127708014361);
}
void car_h_25(double *state, double *unused, double *out_8739001293148261377) {
  h_25(state, unused, out_8739001293148261377);
}
void car_H_25(double *state, double *unused, double *out_8219246077433628171) {
  H_25(state, unused, out_8219246077433628171);
}
void car_h_24(double *state, double *unused, double *out_3866938681010227057) {
  h_24(state, unused, out_3866938681010227057);
}
void car_H_24(double *state, double *unused, double *out_4661320478631305035) {
  H_24(state, unused, out_4661320478631305035);
}
void car_h_30(double *state, double *unused, double *out_8463807230863755488) {
  h_30(state, unused, out_8463807230863755488);
}
void car_H_30(double *state, double *unused, double *out_1302555735942011416) {
  H_30(state, unused, out_1302555735942011416);
}
void car_h_26(double *state, double *unused, double *out_4981263575184950483) {
  h_26(state, unused, out_4981263575184950483);
}
void car_H_26(double *state, double *unused, double *out_4914720107672827570) {
  H_26(state, unused, out_4914720107672827570);
}
void car_h_27(double *state, double *unused, double *out_1946758319516529598) {
  h_27(state, unused, out_1946758319516529598);
}
void car_H_27(double *state, double *unused, double *out_3477319047742436327) {
  H_27(state, unused, out_3477319047742436327);
}
void car_h_29(double *state, double *unused, double *out_9039426989944133693) {
  h_29(state, unused, out_9039426989944133693);
}
void car_H_29(double *state, double *unused, double *out_792324391627619232) {
  H_29(state, unused, out_792324391627619232);
}
void car_h_28(double *state, double *unused, double *out_4551163640325227249) {
  h_28(state, unused, out_4551163640325227249);
}
void car_H_28(double *state, double *unused, double *out_5874723408697149806) {
  H_28(state, unused, out_5874723408697149806);
}
void car_h_31(double *state, double *unused, double *out_7860862958278154023) {
  h_31(state, unused, out_7860862958278154023);
}
void car_H_31(double *state, double *unused, double *out_8188600115556667743) {
  H_31(state, unused, out_8188600115556667743);
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
