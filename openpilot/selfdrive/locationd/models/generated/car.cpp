#include "car.h"

namespace {
#define DIM 9
#define EDIM 9
#define MEDIM 9
typedef void (*Hfun)(double *, double *, double *);

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
void err_fun(double *nom_x, double *delta_x, double *out_7360625163823445495) {
   out_7360625163823445495[0] = delta_x[0] + nom_x[0];
   out_7360625163823445495[1] = delta_x[1] + nom_x[1];
   out_7360625163823445495[2] = delta_x[2] + nom_x[2];
   out_7360625163823445495[3] = delta_x[3] + nom_x[3];
   out_7360625163823445495[4] = delta_x[4] + nom_x[4];
   out_7360625163823445495[5] = delta_x[5] + nom_x[5];
   out_7360625163823445495[6] = delta_x[6] + nom_x[6];
   out_7360625163823445495[7] = delta_x[7] + nom_x[7];
   out_7360625163823445495[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_8413491231423970122) {
   out_8413491231423970122[0] = -nom_x[0] + true_x[0];
   out_8413491231423970122[1] = -nom_x[1] + true_x[1];
   out_8413491231423970122[2] = -nom_x[2] + true_x[2];
   out_8413491231423970122[3] = -nom_x[3] + true_x[3];
   out_8413491231423970122[4] = -nom_x[4] + true_x[4];
   out_8413491231423970122[5] = -nom_x[5] + true_x[5];
   out_8413491231423970122[6] = -nom_x[6] + true_x[6];
   out_8413491231423970122[7] = -nom_x[7] + true_x[7];
   out_8413491231423970122[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_2632326835772732722) {
   out_2632326835772732722[0] = 1.0;
   out_2632326835772732722[1] = 0.0;
   out_2632326835772732722[2] = 0.0;
   out_2632326835772732722[3] = 0.0;
   out_2632326835772732722[4] = 0.0;
   out_2632326835772732722[5] = 0.0;
   out_2632326835772732722[6] = 0.0;
   out_2632326835772732722[7] = 0.0;
   out_2632326835772732722[8] = 0.0;
   out_2632326835772732722[9] = 0.0;
   out_2632326835772732722[10] = 1.0;
   out_2632326835772732722[11] = 0.0;
   out_2632326835772732722[12] = 0.0;
   out_2632326835772732722[13] = 0.0;
   out_2632326835772732722[14] = 0.0;
   out_2632326835772732722[15] = 0.0;
   out_2632326835772732722[16] = 0.0;
   out_2632326835772732722[17] = 0.0;
   out_2632326835772732722[18] = 0.0;
   out_2632326835772732722[19] = 0.0;
   out_2632326835772732722[20] = 1.0;
   out_2632326835772732722[21] = 0.0;
   out_2632326835772732722[22] = 0.0;
   out_2632326835772732722[23] = 0.0;
   out_2632326835772732722[24] = 0.0;
   out_2632326835772732722[25] = 0.0;
   out_2632326835772732722[26] = 0.0;
   out_2632326835772732722[27] = 0.0;
   out_2632326835772732722[28] = 0.0;
   out_2632326835772732722[29] = 0.0;
   out_2632326835772732722[30] = 1.0;
   out_2632326835772732722[31] = 0.0;
   out_2632326835772732722[32] = 0.0;
   out_2632326835772732722[33] = 0.0;
   out_2632326835772732722[34] = 0.0;
   out_2632326835772732722[35] = 0.0;
   out_2632326835772732722[36] = 0.0;
   out_2632326835772732722[37] = 0.0;
   out_2632326835772732722[38] = 0.0;
   out_2632326835772732722[39] = 0.0;
   out_2632326835772732722[40] = 1.0;
   out_2632326835772732722[41] = 0.0;
   out_2632326835772732722[42] = 0.0;
   out_2632326835772732722[43] = 0.0;
   out_2632326835772732722[44] = 0.0;
   out_2632326835772732722[45] = 0.0;
   out_2632326835772732722[46] = 0.0;
   out_2632326835772732722[47] = 0.0;
   out_2632326835772732722[48] = 0.0;
   out_2632326835772732722[49] = 0.0;
   out_2632326835772732722[50] = 1.0;
   out_2632326835772732722[51] = 0.0;
   out_2632326835772732722[52] = 0.0;
   out_2632326835772732722[53] = 0.0;
   out_2632326835772732722[54] = 0.0;
   out_2632326835772732722[55] = 0.0;
   out_2632326835772732722[56] = 0.0;
   out_2632326835772732722[57] = 0.0;
   out_2632326835772732722[58] = 0.0;
   out_2632326835772732722[59] = 0.0;
   out_2632326835772732722[60] = 1.0;
   out_2632326835772732722[61] = 0.0;
   out_2632326835772732722[62] = 0.0;
   out_2632326835772732722[63] = 0.0;
   out_2632326835772732722[64] = 0.0;
   out_2632326835772732722[65] = 0.0;
   out_2632326835772732722[66] = 0.0;
   out_2632326835772732722[67] = 0.0;
   out_2632326835772732722[68] = 0.0;
   out_2632326835772732722[69] = 0.0;
   out_2632326835772732722[70] = 1.0;
   out_2632326835772732722[71] = 0.0;
   out_2632326835772732722[72] = 0.0;
   out_2632326835772732722[73] = 0.0;
   out_2632326835772732722[74] = 0.0;
   out_2632326835772732722[75] = 0.0;
   out_2632326835772732722[76] = 0.0;
   out_2632326835772732722[77] = 0.0;
   out_2632326835772732722[78] = 0.0;
   out_2632326835772732722[79] = 0.0;
   out_2632326835772732722[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_8532698894052839577) {
   out_8532698894052839577[0] = state[0];
   out_8532698894052839577[1] = state[1];
   out_8532698894052839577[2] = state[2];
   out_8532698894052839577[3] = state[3];
   out_8532698894052839577[4] = state[4];
   out_8532698894052839577[5] = dt*(stiffness_front*(-state[2] - state[3] + state[7])*state[0]/state[1] + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/state[4] + ((-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/state[4] - state[4])*state[6] - 9.8100000000000005*state[8]) + state[5];
   out_8532698894052839577[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_8532698894052839577[7] = state[7];
   out_8532698894052839577[8] = state[8];
}
void F_fun(double *state, double dt, double *out_5046006616921834778) {
   out_5046006616921834778[0] = 1;
   out_5046006616921834778[1] = 0;
   out_5046006616921834778[2] = 0;
   out_5046006616921834778[3] = 0;
   out_5046006616921834778[4] = 0;
   out_5046006616921834778[5] = 0;
   out_5046006616921834778[6] = 0;
   out_5046006616921834778[7] = 0;
   out_5046006616921834778[8] = 0;
   out_5046006616921834778[9] = 0;
   out_5046006616921834778[10] = 1;
   out_5046006616921834778[11] = 0;
   out_5046006616921834778[12] = 0;
   out_5046006616921834778[13] = 0;
   out_5046006616921834778[14] = 0;
   out_5046006616921834778[15] = 0;
   out_5046006616921834778[16] = 0;
   out_5046006616921834778[17] = 0;
   out_5046006616921834778[18] = 0;
   out_5046006616921834778[19] = 0;
   out_5046006616921834778[20] = 1;
   out_5046006616921834778[21] = 0;
   out_5046006616921834778[22] = 0;
   out_5046006616921834778[23] = 0;
   out_5046006616921834778[24] = 0;
   out_5046006616921834778[25] = 0;
   out_5046006616921834778[26] = 0;
   out_5046006616921834778[27] = 0;
   out_5046006616921834778[28] = 0;
   out_5046006616921834778[29] = 0;
   out_5046006616921834778[30] = 1;
   out_5046006616921834778[31] = 0;
   out_5046006616921834778[32] = 0;
   out_5046006616921834778[33] = 0;
   out_5046006616921834778[34] = 0;
   out_5046006616921834778[35] = 0;
   out_5046006616921834778[36] = 0;
   out_5046006616921834778[37] = 0;
   out_5046006616921834778[38] = 0;
   out_5046006616921834778[39] = 0;
   out_5046006616921834778[40] = 1;
   out_5046006616921834778[41] = 0;
   out_5046006616921834778[42] = 0;
   out_5046006616921834778[43] = 0;
   out_5046006616921834778[44] = 0;
   out_5046006616921834778[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/state[1] + (-stiffness_front - stiffness_rear)*state[5]/state[4] + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/state[4]);
   out_5046006616921834778[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/pow(state[1], 2);
   out_5046006616921834778[47] = -dt*stiffness_front*state[0]/state[1];
   out_5046006616921834778[48] = -dt*stiffness_front*state[0]/state[1];
   out_5046006616921834778[49] = dt*(-(-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/pow(state[4], 2) + (-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/pow(state[4], 2) - 1)*state[6]);
   out_5046006616921834778[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/state[4] + 1;
   out_5046006616921834778[51] = dt*((-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/state[4] - state[4]);
   out_5046006616921834778[52] = dt*stiffness_front*state[0]/state[1];
   out_5046006616921834778[53] = -9.8100000000000005*dt;
   out_5046006616921834778[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_5046006616921834778[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_5046006616921834778[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_5046006616921834778[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_5046006616921834778[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_5046006616921834778[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_5046006616921834778[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_5046006616921834778[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_5046006616921834778[62] = 0;
   out_5046006616921834778[63] = 0;
   out_5046006616921834778[64] = 0;
   out_5046006616921834778[65] = 0;
   out_5046006616921834778[66] = 0;
   out_5046006616921834778[67] = 0;
   out_5046006616921834778[68] = 0;
   out_5046006616921834778[69] = 0;
   out_5046006616921834778[70] = 1;
   out_5046006616921834778[71] = 0;
   out_5046006616921834778[72] = 0;
   out_5046006616921834778[73] = 0;
   out_5046006616921834778[74] = 0;
   out_5046006616921834778[75] = 0;
   out_5046006616921834778[76] = 0;
   out_5046006616921834778[77] = 0;
   out_5046006616921834778[78] = 0;
   out_5046006616921834778[79] = 0;
   out_5046006616921834778[80] = 1;
}
void h_25(double *state, double *unused, double *out_5546638875155758793) {
   out_5546638875155758793[0] = state[6];
}
void H_25(double *state, double *unused, double *out_890653814216758955) {
   out_890653814216758955[0] = 0;
   out_890653814216758955[1] = 0;
   out_890653814216758955[2] = 0;
   out_890653814216758955[3] = 0;
   out_890653814216758955[4] = 0;
   out_890653814216758955[5] = 0;
   out_890653814216758955[6] = 1;
   out_890653814216758955[7] = 0;
   out_890653814216758955[8] = 0;
}
void h_24(double *state, double *unused, double *out_4367318711229477977) {
   out_4367318711229477977[0] = state[4];
   out_4367318711229477977[1] = state[5];
}
void H_24(double *state, double *unused, double *out_4448579413019082091) {
   out_4448579413019082091[0] = 0;
   out_4448579413019082091[1] = 0;
   out_4448579413019082091[2] = 0;
   out_4448579413019082091[3] = 0;
   out_4448579413019082091[4] = 1;
   out_4448579413019082091[5] = 0;
   out_4448579413019082091[6] = 0;
   out_4448579413019082091[7] = 0;
   out_4448579413019082091[8] = 0;
   out_4448579413019082091[9] = 0;
   out_4448579413019082091[10] = 0;
   out_4448579413019082091[11] = 0;
   out_4448579413019082091[12] = 0;
   out_4448579413019082091[13] = 0;
   out_4448579413019082091[14] = 1;
   out_4448579413019082091[15] = 0;
   out_4448579413019082091[16] = 0;
   out_4448579413019082091[17] = 0;
}
void h_30(double *state, double *unused, double *out_1909189346901736443) {
   out_1909189346901736443[0] = state[4];
}
void H_30(double *state, double *unused, double *out_7807344155708375710) {
   out_7807344155708375710[0] = 0;
   out_7807344155708375710[1] = 0;
   out_7807344155708375710[2] = 0;
   out_7807344155708375710[3] = 0;
   out_7807344155708375710[4] = 1;
   out_7807344155708375710[5] = 0;
   out_7807344155708375710[6] = 0;
   out_7807344155708375710[7] = 0;
   out_7807344155708375710[8] = 0;
}
void h_26(double *state, double *unused, double *out_6910862614562582088) {
   out_6910862614562582088[0] = state[7];
}
void H_26(double *state, double *unused, double *out_2850849504657297269) {
   out_2850849504657297269[0] = 0;
   out_2850849504657297269[1] = 0;
   out_2850849504657297269[2] = 0;
   out_2850849504657297269[3] = 0;
   out_2850849504657297269[4] = 0;
   out_2850849504657297269[5] = 0;
   out_2850849504657297269[6] = 0;
   out_2850849504657297269[7] = 1;
   out_2850849504657297269[8] = 0;
}
void h_27(double *state, double *unused, double *out_3918136026546952058) {
   out_3918136026546952058[0] = state[3];
}
void H_27(double *state, double *unused, double *out_5632580843907950799) {
   out_5632580843907950799[0] = 0;
   out_5632580843907950799[1] = 0;
   out_5632580843907950799[2] = 0;
   out_5632580843907950799[3] = 1;
   out_5632580843907950799[4] = 0;
   out_5632580843907950799[5] = 0;
   out_5632580843907950799[6] = 0;
   out_5632580843907950799[7] = 0;
   out_5632580843907950799[8] = 0;
}
void h_29(double *state, double *unused, double *out_3092483920759109202) {
   out_3092483920759109202[0] = state[1];
}
void H_29(double *state, double *unused, double *out_8317575500022767894) {
   out_8317575500022767894[0] = 0;
   out_8317575500022767894[1] = 1;
   out_8317575500022767894[2] = 0;
   out_8317575500022767894[3] = 0;
   out_8317575500022767894[4] = 0;
   out_8317575500022767894[5] = 0;
   out_8317575500022767894[6] = 0;
   out_8317575500022767894[7] = 0;
   out_8317575500022767894[8] = 0;
}
void h_28(double *state, double *unused, double *out_4521451911223429575) {
   out_4521451911223429575[0] = state[0];
}
void H_28(double *state, double *unused, double *out_1163180900031130808) {
   out_1163180900031130808[0] = 1;
   out_1163180900031130808[1] = 0;
   out_1163180900031130808[2] = 0;
   out_1163180900031130808[3] = 0;
   out_1163180900031130808[4] = 0;
   out_1163180900031130808[5] = 0;
   out_1163180900031130808[6] = 0;
   out_1163180900031130808[7] = 0;
   out_1163180900031130808[8] = 0;
}
void h_31(double *state, double *unused, double *out_5821832937440264682) {
   out_5821832937440264682[0] = state[8];
}
void H_31(double *state, double *unused, double *out_921299776093719383) {
   out_921299776093719383[0] = 0;
   out_921299776093719383[1] = 0;
   out_921299776093719383[2] = 0;
   out_921299776093719383[3] = 0;
   out_921299776093719383[4] = 0;
   out_921299776093719383[5] = 0;
   out_921299776093719383[6] = 0;
   out_921299776093719383[7] = 0;
   out_921299776093719383[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_7360625163823445495) {
  err_fun(nom_x, delta_x, out_7360625163823445495);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_8413491231423970122) {
  inv_err_fun(nom_x, true_x, out_8413491231423970122);
}
void car_H_mod_fun(double *state, double *out_2632326835772732722) {
  H_mod_fun(state, out_2632326835772732722);
}
void car_f_fun(double *state, double dt, double *out_8532698894052839577) {
  f_fun(state,  dt, out_8532698894052839577);
}
void car_F_fun(double *state, double dt, double *out_5046006616921834778) {
  F_fun(state,  dt, out_5046006616921834778);
}
void car_h_25(double *state, double *unused, double *out_5546638875155758793) {
  h_25(state, unused, out_5546638875155758793);
}
void car_H_25(double *state, double *unused, double *out_890653814216758955) {
  H_25(state, unused, out_890653814216758955);
}
void car_h_24(double *state, double *unused, double *out_4367318711229477977) {
  h_24(state, unused, out_4367318711229477977);
}
void car_H_24(double *state, double *unused, double *out_4448579413019082091) {
  H_24(state, unused, out_4448579413019082091);
}
void car_h_30(double *state, double *unused, double *out_1909189346901736443) {
  h_30(state, unused, out_1909189346901736443);
}
void car_H_30(double *state, double *unused, double *out_7807344155708375710) {
  H_30(state, unused, out_7807344155708375710);
}
void car_h_26(double *state, double *unused, double *out_6910862614562582088) {
  h_26(state, unused, out_6910862614562582088);
}
void car_H_26(double *state, double *unused, double *out_2850849504657297269) {
  H_26(state, unused, out_2850849504657297269);
}
void car_h_27(double *state, double *unused, double *out_3918136026546952058) {
  h_27(state, unused, out_3918136026546952058);
}
void car_H_27(double *state, double *unused, double *out_5632580843907950799) {
  H_27(state, unused, out_5632580843907950799);
}
void car_h_29(double *state, double *unused, double *out_3092483920759109202) {
  h_29(state, unused, out_3092483920759109202);
}
void car_H_29(double *state, double *unused, double *out_8317575500022767894) {
  H_29(state, unused, out_8317575500022767894);
}
void car_h_28(double *state, double *unused, double *out_4521451911223429575) {
  h_28(state, unused, out_4521451911223429575);
}
void car_H_28(double *state, double *unused, double *out_1163180900031130808) {
  H_28(state, unused, out_1163180900031130808);
}
void car_h_31(double *state, double *unused, double *out_5821832937440264682) {
  h_31(state, unused, out_5821832937440264682);
}
void car_H_31(double *state, double *unused, double *out_921299776093719383) {
  H_31(state, unused, out_921299776093719383);
}
void car_predict(double *in_x, double *in_P, double *in_Q, double dt) {
  predict(in_x, in_P, in_Q, dt);
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
