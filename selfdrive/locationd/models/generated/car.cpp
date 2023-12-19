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
void err_fun(double *nom_x, double *delta_x, double *out_5539204589909662238) {
   out_5539204589909662238[0] = delta_x[0] + nom_x[0];
   out_5539204589909662238[1] = delta_x[1] + nom_x[1];
   out_5539204589909662238[2] = delta_x[2] + nom_x[2];
   out_5539204589909662238[3] = delta_x[3] + nom_x[3];
   out_5539204589909662238[4] = delta_x[4] + nom_x[4];
   out_5539204589909662238[5] = delta_x[5] + nom_x[5];
   out_5539204589909662238[6] = delta_x[6] + nom_x[6];
   out_5539204589909662238[7] = delta_x[7] + nom_x[7];
   out_5539204589909662238[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_6836761615042086214) {
   out_6836761615042086214[0] = -nom_x[0] + true_x[0];
   out_6836761615042086214[1] = -nom_x[1] + true_x[1];
   out_6836761615042086214[2] = -nom_x[2] + true_x[2];
   out_6836761615042086214[3] = -nom_x[3] + true_x[3];
   out_6836761615042086214[4] = -nom_x[4] + true_x[4];
   out_6836761615042086214[5] = -nom_x[5] + true_x[5];
   out_6836761615042086214[6] = -nom_x[6] + true_x[6];
   out_6836761615042086214[7] = -nom_x[7] + true_x[7];
   out_6836761615042086214[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_5300350899020605715) {
   out_5300350899020605715[0] = 1.0;
   out_5300350899020605715[1] = 0;
   out_5300350899020605715[2] = 0;
   out_5300350899020605715[3] = 0;
   out_5300350899020605715[4] = 0;
   out_5300350899020605715[5] = 0;
   out_5300350899020605715[6] = 0;
   out_5300350899020605715[7] = 0;
   out_5300350899020605715[8] = 0;
   out_5300350899020605715[9] = 0;
   out_5300350899020605715[10] = 1.0;
   out_5300350899020605715[11] = 0;
   out_5300350899020605715[12] = 0;
   out_5300350899020605715[13] = 0;
   out_5300350899020605715[14] = 0;
   out_5300350899020605715[15] = 0;
   out_5300350899020605715[16] = 0;
   out_5300350899020605715[17] = 0;
   out_5300350899020605715[18] = 0;
   out_5300350899020605715[19] = 0;
   out_5300350899020605715[20] = 1.0;
   out_5300350899020605715[21] = 0;
   out_5300350899020605715[22] = 0;
   out_5300350899020605715[23] = 0;
   out_5300350899020605715[24] = 0;
   out_5300350899020605715[25] = 0;
   out_5300350899020605715[26] = 0;
   out_5300350899020605715[27] = 0;
   out_5300350899020605715[28] = 0;
   out_5300350899020605715[29] = 0;
   out_5300350899020605715[30] = 1.0;
   out_5300350899020605715[31] = 0;
   out_5300350899020605715[32] = 0;
   out_5300350899020605715[33] = 0;
   out_5300350899020605715[34] = 0;
   out_5300350899020605715[35] = 0;
   out_5300350899020605715[36] = 0;
   out_5300350899020605715[37] = 0;
   out_5300350899020605715[38] = 0;
   out_5300350899020605715[39] = 0;
   out_5300350899020605715[40] = 1.0;
   out_5300350899020605715[41] = 0;
   out_5300350899020605715[42] = 0;
   out_5300350899020605715[43] = 0;
   out_5300350899020605715[44] = 0;
   out_5300350899020605715[45] = 0;
   out_5300350899020605715[46] = 0;
   out_5300350899020605715[47] = 0;
   out_5300350899020605715[48] = 0;
   out_5300350899020605715[49] = 0;
   out_5300350899020605715[50] = 1.0;
   out_5300350899020605715[51] = 0;
   out_5300350899020605715[52] = 0;
   out_5300350899020605715[53] = 0;
   out_5300350899020605715[54] = 0;
   out_5300350899020605715[55] = 0;
   out_5300350899020605715[56] = 0;
   out_5300350899020605715[57] = 0;
   out_5300350899020605715[58] = 0;
   out_5300350899020605715[59] = 0;
   out_5300350899020605715[60] = 1.0;
   out_5300350899020605715[61] = 0;
   out_5300350899020605715[62] = 0;
   out_5300350899020605715[63] = 0;
   out_5300350899020605715[64] = 0;
   out_5300350899020605715[65] = 0;
   out_5300350899020605715[66] = 0;
   out_5300350899020605715[67] = 0;
   out_5300350899020605715[68] = 0;
   out_5300350899020605715[69] = 0;
   out_5300350899020605715[70] = 1.0;
   out_5300350899020605715[71] = 0;
   out_5300350899020605715[72] = 0;
   out_5300350899020605715[73] = 0;
   out_5300350899020605715[74] = 0;
   out_5300350899020605715[75] = 0;
   out_5300350899020605715[76] = 0;
   out_5300350899020605715[77] = 0;
   out_5300350899020605715[78] = 0;
   out_5300350899020605715[79] = 0;
   out_5300350899020605715[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_7290139574394395979) {
   out_7290139574394395979[0] = state[0];
   out_7290139574394395979[1] = state[1];
   out_7290139574394395979[2] = state[2];
   out_7290139574394395979[3] = state[3];
   out_7290139574394395979[4] = state[4];
   out_7290139574394395979[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8000000000000007*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_7290139574394395979[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_7290139574394395979[7] = state[7];
   out_7290139574394395979[8] = state[8];
}
void F_fun(double *state, double dt, double *out_3369922846592360961) {
   out_3369922846592360961[0] = 1;
   out_3369922846592360961[1] = 0;
   out_3369922846592360961[2] = 0;
   out_3369922846592360961[3] = 0;
   out_3369922846592360961[4] = 0;
   out_3369922846592360961[5] = 0;
   out_3369922846592360961[6] = 0;
   out_3369922846592360961[7] = 0;
   out_3369922846592360961[8] = 0;
   out_3369922846592360961[9] = 0;
   out_3369922846592360961[10] = 1;
   out_3369922846592360961[11] = 0;
   out_3369922846592360961[12] = 0;
   out_3369922846592360961[13] = 0;
   out_3369922846592360961[14] = 0;
   out_3369922846592360961[15] = 0;
   out_3369922846592360961[16] = 0;
   out_3369922846592360961[17] = 0;
   out_3369922846592360961[18] = 0;
   out_3369922846592360961[19] = 0;
   out_3369922846592360961[20] = 1;
   out_3369922846592360961[21] = 0;
   out_3369922846592360961[22] = 0;
   out_3369922846592360961[23] = 0;
   out_3369922846592360961[24] = 0;
   out_3369922846592360961[25] = 0;
   out_3369922846592360961[26] = 0;
   out_3369922846592360961[27] = 0;
   out_3369922846592360961[28] = 0;
   out_3369922846592360961[29] = 0;
   out_3369922846592360961[30] = 1;
   out_3369922846592360961[31] = 0;
   out_3369922846592360961[32] = 0;
   out_3369922846592360961[33] = 0;
   out_3369922846592360961[34] = 0;
   out_3369922846592360961[35] = 0;
   out_3369922846592360961[36] = 0;
   out_3369922846592360961[37] = 0;
   out_3369922846592360961[38] = 0;
   out_3369922846592360961[39] = 0;
   out_3369922846592360961[40] = 1;
   out_3369922846592360961[41] = 0;
   out_3369922846592360961[42] = 0;
   out_3369922846592360961[43] = 0;
   out_3369922846592360961[44] = 0;
   out_3369922846592360961[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_3369922846592360961[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_3369922846592360961[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_3369922846592360961[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_3369922846592360961[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_3369922846592360961[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_3369922846592360961[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_3369922846592360961[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_3369922846592360961[53] = -9.8000000000000007*dt;
   out_3369922846592360961[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_3369922846592360961[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_3369922846592360961[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_3369922846592360961[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_3369922846592360961[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_3369922846592360961[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_3369922846592360961[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_3369922846592360961[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_3369922846592360961[62] = 0;
   out_3369922846592360961[63] = 0;
   out_3369922846592360961[64] = 0;
   out_3369922846592360961[65] = 0;
   out_3369922846592360961[66] = 0;
   out_3369922846592360961[67] = 0;
   out_3369922846592360961[68] = 0;
   out_3369922846592360961[69] = 0;
   out_3369922846592360961[70] = 1;
   out_3369922846592360961[71] = 0;
   out_3369922846592360961[72] = 0;
   out_3369922846592360961[73] = 0;
   out_3369922846592360961[74] = 0;
   out_3369922846592360961[75] = 0;
   out_3369922846592360961[76] = 0;
   out_3369922846592360961[77] = 0;
   out_3369922846592360961[78] = 0;
   out_3369922846592360961[79] = 0;
   out_3369922846592360961[80] = 1;
}
void h_25(double *state, double *unused, double *out_213866987500689272) {
   out_213866987500689272[0] = state[6];
}
void H_25(double *state, double *unused, double *out_8338833395014389035) {
   out_8338833395014389035[0] = 0;
   out_8338833395014389035[1] = 0;
   out_8338833395014389035[2] = 0;
   out_8338833395014389035[3] = 0;
   out_8338833395014389035[4] = 0;
   out_8338833395014389035[5] = 0;
   out_8338833395014389035[6] = 1;
   out_8338833395014389035[7] = 0;
   out_8338833395014389035[8] = 0;
}
void h_24(double *state, double *unused, double *out_6813311767306827479) {
   out_6813311767306827479[0] = state[4];
   out_6813311767306827479[1] = state[5];
}
void H_24(double *state, double *unused, double *out_3470018529986682183) {
   out_3470018529986682183[0] = 0;
   out_3470018529986682183[1] = 0;
   out_3470018529986682183[2] = 0;
   out_3470018529986682183[3] = 0;
   out_3470018529986682183[4] = 1;
   out_3470018529986682183[5] = 0;
   out_3470018529986682183[6] = 0;
   out_3470018529986682183[7] = 0;
   out_3470018529986682183[8] = 0;
   out_3470018529986682183[9] = 0;
   out_3470018529986682183[10] = 0;
   out_3470018529986682183[11] = 0;
   out_3470018529986682183[12] = 0;
   out_3470018529986682183[13] = 0;
   out_3470018529986682183[14] = 1;
   out_3470018529986682183[15] = 0;
   out_3470018529986682183[16] = 0;
   out_3470018529986682183[17] = 0;
}
void h_30(double *state, double *unused, double *out_3161592977856174233) {
   out_3161592977856174233[0] = state[4];
}
void H_30(double *state, double *unused, double *out_3811137064886780837) {
   out_3811137064886780837[0] = 0;
   out_3811137064886780837[1] = 0;
   out_3811137064886780837[2] = 0;
   out_3811137064886780837[3] = 0;
   out_3811137064886780837[4] = 1;
   out_3811137064886780837[5] = 0;
   out_3811137064886780837[6] = 0;
   out_3811137064886780837[7] = 0;
   out_3811137064886780837[8] = 0;
}
void h_26(double *state, double *unused, double *out_4105102830757836668) {
   out_4105102830757836668[0] = state[7];
}
void H_26(double *state, double *unused, double *out_4597330076140332811) {
   out_4597330076140332811[0] = 0;
   out_4597330076140332811[1] = 0;
   out_4597330076140332811[2] = 0;
   out_4597330076140332811[3] = 0;
   out_4597330076140332811[4] = 0;
   out_4597330076140332811[5] = 0;
   out_4597330076140332811[6] = 0;
   out_4597330076140332811[7] = 1;
   out_4597330076140332811[8] = 0;
}
void h_27(double *state, double *unused, double *out_8017746421296364907) {
   out_8017746421296364907[0] = state[3];
}
void H_27(double *state, double *unused, double *out_1636373753086355926) {
   out_1636373753086355926[0] = 0;
   out_1636373753086355926[1] = 0;
   out_1636373753086355926[2] = 0;
   out_1636373753086355926[3] = 1;
   out_1636373753086355926[4] = 0;
   out_1636373753086355926[5] = 0;
   out_1636373753086355926[6] = 0;
   out_1636373753086355926[7] = 0;
   out_1636373753086355926[8] = 0;
}
void h_29(double *state, double *unused, double *out_3764908862532651750) {
   out_3764908862532651750[0] = state[1];
}
void H_29(double *state, double *unused, double *out_4321368409201173021) {
   out_4321368409201173021[0] = 0;
   out_4321368409201173021[1] = 1;
   out_4321368409201173021[2] = 0;
   out_4321368409201173021[3] = 0;
   out_4321368409201173021[4] = 0;
   out_4321368409201173021[5] = 0;
   out_4321368409201173021[6] = 0;
   out_4321368409201173021[7] = 0;
   out_4321368409201173021[8] = 0;
}
void h_28(double *state, double *unused, double *out_8845296254147321726) {
   out_8845296254147321726[0] = state[0];
}
void H_28(double *state, double *unused, double *out_6284998680766499272) {
   out_6284998680766499272[0] = 1;
   out_6284998680766499272[1] = 0;
   out_6284998680766499272[2] = 0;
   out_6284998680766499272[3] = 0;
   out_6284998680766499272[4] = 0;
   out_6284998680766499272[5] = 0;
   out_6284998680766499272[6] = 0;
   out_6284998680766499272[7] = 0;
   out_6284998680766499272[8] = 0;
}
void h_31(double *state, double *unused, double *out_7667405663253359913) {
   out_7667405663253359913[0] = state[8];
}
void H_31(double *state, double *unused, double *out_3971121973906981335) {
   out_3971121973906981335[0] = 0;
   out_3971121973906981335[1] = 0;
   out_3971121973906981335[2] = 0;
   out_3971121973906981335[3] = 0;
   out_3971121973906981335[4] = 0;
   out_3971121973906981335[5] = 0;
   out_3971121973906981335[6] = 0;
   out_3971121973906981335[7] = 0;
   out_3971121973906981335[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_5539204589909662238) {
  err_fun(nom_x, delta_x, out_5539204589909662238);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_6836761615042086214) {
  inv_err_fun(nom_x, true_x, out_6836761615042086214);
}
void car_H_mod_fun(double *state, double *out_5300350899020605715) {
  H_mod_fun(state, out_5300350899020605715);
}
void car_f_fun(double *state, double dt, double *out_7290139574394395979) {
  f_fun(state,  dt, out_7290139574394395979);
}
void car_F_fun(double *state, double dt, double *out_3369922846592360961) {
  F_fun(state,  dt, out_3369922846592360961);
}
void car_h_25(double *state, double *unused, double *out_213866987500689272) {
  h_25(state, unused, out_213866987500689272);
}
void car_H_25(double *state, double *unused, double *out_8338833395014389035) {
  H_25(state, unused, out_8338833395014389035);
}
void car_h_24(double *state, double *unused, double *out_6813311767306827479) {
  h_24(state, unused, out_6813311767306827479);
}
void car_H_24(double *state, double *unused, double *out_3470018529986682183) {
  H_24(state, unused, out_3470018529986682183);
}
void car_h_30(double *state, double *unused, double *out_3161592977856174233) {
  h_30(state, unused, out_3161592977856174233);
}
void car_H_30(double *state, double *unused, double *out_3811137064886780837) {
  H_30(state, unused, out_3811137064886780837);
}
void car_h_26(double *state, double *unused, double *out_4105102830757836668) {
  h_26(state, unused, out_4105102830757836668);
}
void car_H_26(double *state, double *unused, double *out_4597330076140332811) {
  H_26(state, unused, out_4597330076140332811);
}
void car_h_27(double *state, double *unused, double *out_8017746421296364907) {
  h_27(state, unused, out_8017746421296364907);
}
void car_H_27(double *state, double *unused, double *out_1636373753086355926) {
  H_27(state, unused, out_1636373753086355926);
}
void car_h_29(double *state, double *unused, double *out_3764908862532651750) {
  h_29(state, unused, out_3764908862532651750);
}
void car_H_29(double *state, double *unused, double *out_4321368409201173021) {
  H_29(state, unused, out_4321368409201173021);
}
void car_h_28(double *state, double *unused, double *out_8845296254147321726) {
  h_28(state, unused, out_8845296254147321726);
}
void car_H_28(double *state, double *unused, double *out_6284998680766499272) {
  H_28(state, unused, out_6284998680766499272);
}
void car_h_31(double *state, double *unused, double *out_7667405663253359913) {
  h_31(state, unused, out_7667405663253359913);
}
void car_H_31(double *state, double *unused, double *out_3971121973906981335) {
  H_31(state, unused, out_3971121973906981335);
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
