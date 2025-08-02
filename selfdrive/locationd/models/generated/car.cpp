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
void err_fun(double *nom_x, double *delta_x, double *out_4601697762902887404) {
   out_4601697762902887404[0] = delta_x[0] + nom_x[0];
   out_4601697762902887404[1] = delta_x[1] + nom_x[1];
   out_4601697762902887404[2] = delta_x[2] + nom_x[2];
   out_4601697762902887404[3] = delta_x[3] + nom_x[3];
   out_4601697762902887404[4] = delta_x[4] + nom_x[4];
   out_4601697762902887404[5] = delta_x[5] + nom_x[5];
   out_4601697762902887404[6] = delta_x[6] + nom_x[6];
   out_4601697762902887404[7] = delta_x[7] + nom_x[7];
   out_4601697762902887404[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_3959595646079752203) {
   out_3959595646079752203[0] = -nom_x[0] + true_x[0];
   out_3959595646079752203[1] = -nom_x[1] + true_x[1];
   out_3959595646079752203[2] = -nom_x[2] + true_x[2];
   out_3959595646079752203[3] = -nom_x[3] + true_x[3];
   out_3959595646079752203[4] = -nom_x[4] + true_x[4];
   out_3959595646079752203[5] = -nom_x[5] + true_x[5];
   out_3959595646079752203[6] = -nom_x[6] + true_x[6];
   out_3959595646079752203[7] = -nom_x[7] + true_x[7];
   out_3959595646079752203[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_653001050605998855) {
   out_653001050605998855[0] = 1.0;
   out_653001050605998855[1] = 0.0;
   out_653001050605998855[2] = 0.0;
   out_653001050605998855[3] = 0.0;
   out_653001050605998855[4] = 0.0;
   out_653001050605998855[5] = 0.0;
   out_653001050605998855[6] = 0.0;
   out_653001050605998855[7] = 0.0;
   out_653001050605998855[8] = 0.0;
   out_653001050605998855[9] = 0.0;
   out_653001050605998855[10] = 1.0;
   out_653001050605998855[11] = 0.0;
   out_653001050605998855[12] = 0.0;
   out_653001050605998855[13] = 0.0;
   out_653001050605998855[14] = 0.0;
   out_653001050605998855[15] = 0.0;
   out_653001050605998855[16] = 0.0;
   out_653001050605998855[17] = 0.0;
   out_653001050605998855[18] = 0.0;
   out_653001050605998855[19] = 0.0;
   out_653001050605998855[20] = 1.0;
   out_653001050605998855[21] = 0.0;
   out_653001050605998855[22] = 0.0;
   out_653001050605998855[23] = 0.0;
   out_653001050605998855[24] = 0.0;
   out_653001050605998855[25] = 0.0;
   out_653001050605998855[26] = 0.0;
   out_653001050605998855[27] = 0.0;
   out_653001050605998855[28] = 0.0;
   out_653001050605998855[29] = 0.0;
   out_653001050605998855[30] = 1.0;
   out_653001050605998855[31] = 0.0;
   out_653001050605998855[32] = 0.0;
   out_653001050605998855[33] = 0.0;
   out_653001050605998855[34] = 0.0;
   out_653001050605998855[35] = 0.0;
   out_653001050605998855[36] = 0.0;
   out_653001050605998855[37] = 0.0;
   out_653001050605998855[38] = 0.0;
   out_653001050605998855[39] = 0.0;
   out_653001050605998855[40] = 1.0;
   out_653001050605998855[41] = 0.0;
   out_653001050605998855[42] = 0.0;
   out_653001050605998855[43] = 0.0;
   out_653001050605998855[44] = 0.0;
   out_653001050605998855[45] = 0.0;
   out_653001050605998855[46] = 0.0;
   out_653001050605998855[47] = 0.0;
   out_653001050605998855[48] = 0.0;
   out_653001050605998855[49] = 0.0;
   out_653001050605998855[50] = 1.0;
   out_653001050605998855[51] = 0.0;
   out_653001050605998855[52] = 0.0;
   out_653001050605998855[53] = 0.0;
   out_653001050605998855[54] = 0.0;
   out_653001050605998855[55] = 0.0;
   out_653001050605998855[56] = 0.0;
   out_653001050605998855[57] = 0.0;
   out_653001050605998855[58] = 0.0;
   out_653001050605998855[59] = 0.0;
   out_653001050605998855[60] = 1.0;
   out_653001050605998855[61] = 0.0;
   out_653001050605998855[62] = 0.0;
   out_653001050605998855[63] = 0.0;
   out_653001050605998855[64] = 0.0;
   out_653001050605998855[65] = 0.0;
   out_653001050605998855[66] = 0.0;
   out_653001050605998855[67] = 0.0;
   out_653001050605998855[68] = 0.0;
   out_653001050605998855[69] = 0.0;
   out_653001050605998855[70] = 1.0;
   out_653001050605998855[71] = 0.0;
   out_653001050605998855[72] = 0.0;
   out_653001050605998855[73] = 0.0;
   out_653001050605998855[74] = 0.0;
   out_653001050605998855[75] = 0.0;
   out_653001050605998855[76] = 0.0;
   out_653001050605998855[77] = 0.0;
   out_653001050605998855[78] = 0.0;
   out_653001050605998855[79] = 0.0;
   out_653001050605998855[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_1462235041247810438) {
   out_1462235041247810438[0] = state[0];
   out_1462235041247810438[1] = state[1];
   out_1462235041247810438[2] = state[2];
   out_1462235041247810438[3] = state[3];
   out_1462235041247810438[4] = state[4];
   out_1462235041247810438[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8000000000000007*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_1462235041247810438[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_1462235041247810438[7] = state[7];
   out_1462235041247810438[8] = state[8];
}
void F_fun(double *state, double dt, double *out_5625707751492774003) {
   out_5625707751492774003[0] = 1;
   out_5625707751492774003[1] = 0;
   out_5625707751492774003[2] = 0;
   out_5625707751492774003[3] = 0;
   out_5625707751492774003[4] = 0;
   out_5625707751492774003[5] = 0;
   out_5625707751492774003[6] = 0;
   out_5625707751492774003[7] = 0;
   out_5625707751492774003[8] = 0;
   out_5625707751492774003[9] = 0;
   out_5625707751492774003[10] = 1;
   out_5625707751492774003[11] = 0;
   out_5625707751492774003[12] = 0;
   out_5625707751492774003[13] = 0;
   out_5625707751492774003[14] = 0;
   out_5625707751492774003[15] = 0;
   out_5625707751492774003[16] = 0;
   out_5625707751492774003[17] = 0;
   out_5625707751492774003[18] = 0;
   out_5625707751492774003[19] = 0;
   out_5625707751492774003[20] = 1;
   out_5625707751492774003[21] = 0;
   out_5625707751492774003[22] = 0;
   out_5625707751492774003[23] = 0;
   out_5625707751492774003[24] = 0;
   out_5625707751492774003[25] = 0;
   out_5625707751492774003[26] = 0;
   out_5625707751492774003[27] = 0;
   out_5625707751492774003[28] = 0;
   out_5625707751492774003[29] = 0;
   out_5625707751492774003[30] = 1;
   out_5625707751492774003[31] = 0;
   out_5625707751492774003[32] = 0;
   out_5625707751492774003[33] = 0;
   out_5625707751492774003[34] = 0;
   out_5625707751492774003[35] = 0;
   out_5625707751492774003[36] = 0;
   out_5625707751492774003[37] = 0;
   out_5625707751492774003[38] = 0;
   out_5625707751492774003[39] = 0;
   out_5625707751492774003[40] = 1;
   out_5625707751492774003[41] = 0;
   out_5625707751492774003[42] = 0;
   out_5625707751492774003[43] = 0;
   out_5625707751492774003[44] = 0;
   out_5625707751492774003[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_5625707751492774003[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_5625707751492774003[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_5625707751492774003[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_5625707751492774003[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_5625707751492774003[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_5625707751492774003[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_5625707751492774003[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_5625707751492774003[53] = -9.8000000000000007*dt;
   out_5625707751492774003[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_5625707751492774003[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_5625707751492774003[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_5625707751492774003[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_5625707751492774003[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_5625707751492774003[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_5625707751492774003[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_5625707751492774003[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_5625707751492774003[62] = 0;
   out_5625707751492774003[63] = 0;
   out_5625707751492774003[64] = 0;
   out_5625707751492774003[65] = 0;
   out_5625707751492774003[66] = 0;
   out_5625707751492774003[67] = 0;
   out_5625707751492774003[68] = 0;
   out_5625707751492774003[69] = 0;
   out_5625707751492774003[70] = 1;
   out_5625707751492774003[71] = 0;
   out_5625707751492774003[72] = 0;
   out_5625707751492774003[73] = 0;
   out_5625707751492774003[74] = 0;
   out_5625707751492774003[75] = 0;
   out_5625707751492774003[76] = 0;
   out_5625707751492774003[77] = 0;
   out_5625707751492774003[78] = 0;
   out_5625707751492774003[79] = 0;
   out_5625707751492774003[80] = 1;
}
void h_25(double *state, double *unused, double *out_8183390139860994988) {
   out_8183390139860994988[0] = state[6];
}
void H_25(double *state, double *unused, double *out_4175981700595490532) {
   out_4175981700595490532[0] = 0;
   out_4175981700595490532[1] = 0;
   out_4175981700595490532[2] = 0;
   out_4175981700595490532[3] = 0;
   out_4175981700595490532[4] = 0;
   out_4175981700595490532[5] = 0;
   out_4175981700595490532[6] = 1;
   out_4175981700595490532[7] = 0;
   out_4175981700595490532[8] = 0;
}
void h_24(double *state, double *unused, double *out_736265725996846818) {
   out_736265725996846818[0] = state[4];
   out_736265725996846818[1] = state[5];
}
void H_24(double *state, double *unused, double *out_570527626371018502) {
   out_570527626371018502[0] = 0;
   out_570527626371018502[1] = 0;
   out_570527626371018502[2] = 0;
   out_570527626371018502[3] = 0;
   out_570527626371018502[4] = 1;
   out_570527626371018502[5] = 0;
   out_570527626371018502[6] = 0;
   out_570527626371018502[7] = 0;
   out_570527626371018502[8] = 0;
   out_570527626371018502[9] = 0;
   out_570527626371018502[10] = 0;
   out_570527626371018502[11] = 0;
   out_570527626371018502[12] = 0;
   out_570527626371018502[13] = 0;
   out_570527626371018502[14] = 1;
   out_570527626371018502[15] = 0;
   out_570527626371018502[16] = 0;
   out_570527626371018502[17] = 0;
}
void h_30(double *state, double *unused, double *out_4321706663432493336) {
   out_4321706663432493336[0] = state[4];
}
void H_30(double *state, double *unused, double *out_7354072031622444329) {
   out_7354072031622444329[0] = 0;
   out_7354072031622444329[1] = 0;
   out_7354072031622444329[2] = 0;
   out_7354072031622444329[3] = 0;
   out_7354072031622444329[4] = 1;
   out_7354072031622444329[5] = 0;
   out_7354072031622444329[6] = 0;
   out_7354072031622444329[7] = 0;
   out_7354072031622444329[8] = 0;
}
void h_26(double *state, double *unused, double *out_1020160572453537227) {
   out_1020160572453537227[0] = state[7];
}
void H_26(double *state, double *unused, double *out_434478381721434308) {
   out_434478381721434308[0] = 0;
   out_434478381721434308[1] = 0;
   out_434478381721434308[2] = 0;
   out_434478381721434308[3] = 0;
   out_434478381721434308[4] = 0;
   out_434478381721434308[5] = 0;
   out_434478381721434308[6] = 0;
   out_434478381721434308[7] = 1;
   out_434478381721434308[8] = 0;
}
void h_27(double *state, double *unused, double *out_5907861322247942854) {
   out_5907861322247942854[0] = state[3];
}
void H_27(double *state, double *unused, double *out_1871879441651825551) {
   out_1871879441651825551[0] = 0;
   out_1871879441651825551[1] = 0;
   out_1871879441651825551[2] = 0;
   out_1871879441651825551[3] = 1;
   out_1871879441651825551[4] = 0;
   out_1871879441651825551[5] = 0;
   out_1871879441651825551[6] = 0;
   out_1871879441651825551[7] = 0;
   out_1871879441651825551[8] = 0;
}
void h_29(double *state, double *unused, double *out_679966604228352309) {
   out_679966604228352309[0] = state[1];
}
void H_29(double *state, double *unused, double *out_158516714782274518) {
   out_158516714782274518[0] = 0;
   out_158516714782274518[1] = 1;
   out_158516714782274518[2] = 0;
   out_158516714782274518[3] = 0;
   out_158516714782274518[4] = 0;
   out_158516714782274518[5] = 0;
   out_158516714782274518[6] = 0;
   out_158516714782274518[7] = 0;
   out_158516714782274518[8] = 0;
}
void h_28(double *state, double *unused, double *out_5536120047668542983) {
   out_5536120047668542983[0] = state[0];
}
void H_28(double *state, double *unused, double *out_2122146986347600769) {
   out_2122146986347600769[0] = 1;
   out_2122146986347600769[1] = 0;
   out_2122146986347600769[2] = 0;
   out_2122146986347600769[3] = 0;
   out_2122146986347600769[4] = 0;
   out_2122146986347600769[5] = 0;
   out_2122146986347600769[6] = 0;
   out_2122146986347600769[7] = 0;
   out_2122146986347600769[8] = 0;
}
void h_31(double *state, double *unused, double *out_3146269333088116058) {
   out_3146269333088116058[0] = state[8];
}
void H_31(double *state, double *unused, double *out_4206627662472450960) {
   out_4206627662472450960[0] = 0;
   out_4206627662472450960[1] = 0;
   out_4206627662472450960[2] = 0;
   out_4206627662472450960[3] = 0;
   out_4206627662472450960[4] = 0;
   out_4206627662472450960[5] = 0;
   out_4206627662472450960[6] = 0;
   out_4206627662472450960[7] = 0;
   out_4206627662472450960[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_4601697762902887404) {
  err_fun(nom_x, delta_x, out_4601697762902887404);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_3959595646079752203) {
  inv_err_fun(nom_x, true_x, out_3959595646079752203);
}
void car_H_mod_fun(double *state, double *out_653001050605998855) {
  H_mod_fun(state, out_653001050605998855);
}
void car_f_fun(double *state, double dt, double *out_1462235041247810438) {
  f_fun(state,  dt, out_1462235041247810438);
}
void car_F_fun(double *state, double dt, double *out_5625707751492774003) {
  F_fun(state,  dt, out_5625707751492774003);
}
void car_h_25(double *state, double *unused, double *out_8183390139860994988) {
  h_25(state, unused, out_8183390139860994988);
}
void car_H_25(double *state, double *unused, double *out_4175981700595490532) {
  H_25(state, unused, out_4175981700595490532);
}
void car_h_24(double *state, double *unused, double *out_736265725996846818) {
  h_24(state, unused, out_736265725996846818);
}
void car_H_24(double *state, double *unused, double *out_570527626371018502) {
  H_24(state, unused, out_570527626371018502);
}
void car_h_30(double *state, double *unused, double *out_4321706663432493336) {
  h_30(state, unused, out_4321706663432493336);
}
void car_H_30(double *state, double *unused, double *out_7354072031622444329) {
  H_30(state, unused, out_7354072031622444329);
}
void car_h_26(double *state, double *unused, double *out_1020160572453537227) {
  h_26(state, unused, out_1020160572453537227);
}
void car_H_26(double *state, double *unused, double *out_434478381721434308) {
  H_26(state, unused, out_434478381721434308);
}
void car_h_27(double *state, double *unused, double *out_5907861322247942854) {
  h_27(state, unused, out_5907861322247942854);
}
void car_H_27(double *state, double *unused, double *out_1871879441651825551) {
  H_27(state, unused, out_1871879441651825551);
}
void car_h_29(double *state, double *unused, double *out_679966604228352309) {
  h_29(state, unused, out_679966604228352309);
}
void car_H_29(double *state, double *unused, double *out_158516714782274518) {
  H_29(state, unused, out_158516714782274518);
}
void car_h_28(double *state, double *unused, double *out_5536120047668542983) {
  h_28(state, unused, out_5536120047668542983);
}
void car_H_28(double *state, double *unused, double *out_2122146986347600769) {
  H_28(state, unused, out_2122146986347600769);
}
void car_h_31(double *state, double *unused, double *out_3146269333088116058) {
  h_31(state, unused, out_3146269333088116058);
}
void car_H_31(double *state, double *unused, double *out_4206627662472450960) {
  H_31(state, unused, out_4206627662472450960);
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
