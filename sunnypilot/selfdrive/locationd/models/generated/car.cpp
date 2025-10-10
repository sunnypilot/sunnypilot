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
void err_fun(double *nom_x, double *delta_x, double *out_2055827145629245641) {
   out_2055827145629245641[0] = delta_x[0] + nom_x[0];
   out_2055827145629245641[1] = delta_x[1] + nom_x[1];
   out_2055827145629245641[2] = delta_x[2] + nom_x[2];
   out_2055827145629245641[3] = delta_x[3] + nom_x[3];
   out_2055827145629245641[4] = delta_x[4] + nom_x[4];
   out_2055827145629245641[5] = delta_x[5] + nom_x[5];
   out_2055827145629245641[6] = delta_x[6] + nom_x[6];
   out_2055827145629245641[7] = delta_x[7] + nom_x[7];
   out_2055827145629245641[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_5357743043563844621) {
   out_5357743043563844621[0] = -nom_x[0] + true_x[0];
   out_5357743043563844621[1] = -nom_x[1] + true_x[1];
   out_5357743043563844621[2] = -nom_x[2] + true_x[2];
   out_5357743043563844621[3] = -nom_x[3] + true_x[3];
   out_5357743043563844621[4] = -nom_x[4] + true_x[4];
   out_5357743043563844621[5] = -nom_x[5] + true_x[5];
   out_5357743043563844621[6] = -nom_x[6] + true_x[6];
   out_5357743043563844621[7] = -nom_x[7] + true_x[7];
   out_5357743043563844621[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_3260931406444101209) {
   out_3260931406444101209[0] = 1.0;
   out_3260931406444101209[1] = 0.0;
   out_3260931406444101209[2] = 0.0;
   out_3260931406444101209[3] = 0.0;
   out_3260931406444101209[4] = 0.0;
   out_3260931406444101209[5] = 0.0;
   out_3260931406444101209[6] = 0.0;
   out_3260931406444101209[7] = 0.0;
   out_3260931406444101209[8] = 0.0;
   out_3260931406444101209[9] = 0.0;
   out_3260931406444101209[10] = 1.0;
   out_3260931406444101209[11] = 0.0;
   out_3260931406444101209[12] = 0.0;
   out_3260931406444101209[13] = 0.0;
   out_3260931406444101209[14] = 0.0;
   out_3260931406444101209[15] = 0.0;
   out_3260931406444101209[16] = 0.0;
   out_3260931406444101209[17] = 0.0;
   out_3260931406444101209[18] = 0.0;
   out_3260931406444101209[19] = 0.0;
   out_3260931406444101209[20] = 1.0;
   out_3260931406444101209[21] = 0.0;
   out_3260931406444101209[22] = 0.0;
   out_3260931406444101209[23] = 0.0;
   out_3260931406444101209[24] = 0.0;
   out_3260931406444101209[25] = 0.0;
   out_3260931406444101209[26] = 0.0;
   out_3260931406444101209[27] = 0.0;
   out_3260931406444101209[28] = 0.0;
   out_3260931406444101209[29] = 0.0;
   out_3260931406444101209[30] = 1.0;
   out_3260931406444101209[31] = 0.0;
   out_3260931406444101209[32] = 0.0;
   out_3260931406444101209[33] = 0.0;
   out_3260931406444101209[34] = 0.0;
   out_3260931406444101209[35] = 0.0;
   out_3260931406444101209[36] = 0.0;
   out_3260931406444101209[37] = 0.0;
   out_3260931406444101209[38] = 0.0;
   out_3260931406444101209[39] = 0.0;
   out_3260931406444101209[40] = 1.0;
   out_3260931406444101209[41] = 0.0;
   out_3260931406444101209[42] = 0.0;
   out_3260931406444101209[43] = 0.0;
   out_3260931406444101209[44] = 0.0;
   out_3260931406444101209[45] = 0.0;
   out_3260931406444101209[46] = 0.0;
   out_3260931406444101209[47] = 0.0;
   out_3260931406444101209[48] = 0.0;
   out_3260931406444101209[49] = 0.0;
   out_3260931406444101209[50] = 1.0;
   out_3260931406444101209[51] = 0.0;
   out_3260931406444101209[52] = 0.0;
   out_3260931406444101209[53] = 0.0;
   out_3260931406444101209[54] = 0.0;
   out_3260931406444101209[55] = 0.0;
   out_3260931406444101209[56] = 0.0;
   out_3260931406444101209[57] = 0.0;
   out_3260931406444101209[58] = 0.0;
   out_3260931406444101209[59] = 0.0;
   out_3260931406444101209[60] = 1.0;
   out_3260931406444101209[61] = 0.0;
   out_3260931406444101209[62] = 0.0;
   out_3260931406444101209[63] = 0.0;
   out_3260931406444101209[64] = 0.0;
   out_3260931406444101209[65] = 0.0;
   out_3260931406444101209[66] = 0.0;
   out_3260931406444101209[67] = 0.0;
   out_3260931406444101209[68] = 0.0;
   out_3260931406444101209[69] = 0.0;
   out_3260931406444101209[70] = 1.0;
   out_3260931406444101209[71] = 0.0;
   out_3260931406444101209[72] = 0.0;
   out_3260931406444101209[73] = 0.0;
   out_3260931406444101209[74] = 0.0;
   out_3260931406444101209[75] = 0.0;
   out_3260931406444101209[76] = 0.0;
   out_3260931406444101209[77] = 0.0;
   out_3260931406444101209[78] = 0.0;
   out_3260931406444101209[79] = 0.0;
   out_3260931406444101209[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_7842303097555582420) {
   out_7842303097555582420[0] = state[0];
   out_7842303097555582420[1] = state[1];
   out_7842303097555582420[2] = state[2];
   out_7842303097555582420[3] = state[3];
   out_7842303097555582420[4] = state[4];
   out_7842303097555582420[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8100000000000005*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_7842303097555582420[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_7842303097555582420[7] = state[7];
   out_7842303097555582420[8] = state[8];
}
void F_fun(double *state, double dt, double *out_4745107738599081994) {
   out_4745107738599081994[0] = 1;
   out_4745107738599081994[1] = 0;
   out_4745107738599081994[2] = 0;
   out_4745107738599081994[3] = 0;
   out_4745107738599081994[4] = 0;
   out_4745107738599081994[5] = 0;
   out_4745107738599081994[6] = 0;
   out_4745107738599081994[7] = 0;
   out_4745107738599081994[8] = 0;
   out_4745107738599081994[9] = 0;
   out_4745107738599081994[10] = 1;
   out_4745107738599081994[11] = 0;
   out_4745107738599081994[12] = 0;
   out_4745107738599081994[13] = 0;
   out_4745107738599081994[14] = 0;
   out_4745107738599081994[15] = 0;
   out_4745107738599081994[16] = 0;
   out_4745107738599081994[17] = 0;
   out_4745107738599081994[18] = 0;
   out_4745107738599081994[19] = 0;
   out_4745107738599081994[20] = 1;
   out_4745107738599081994[21] = 0;
   out_4745107738599081994[22] = 0;
   out_4745107738599081994[23] = 0;
   out_4745107738599081994[24] = 0;
   out_4745107738599081994[25] = 0;
   out_4745107738599081994[26] = 0;
   out_4745107738599081994[27] = 0;
   out_4745107738599081994[28] = 0;
   out_4745107738599081994[29] = 0;
   out_4745107738599081994[30] = 1;
   out_4745107738599081994[31] = 0;
   out_4745107738599081994[32] = 0;
   out_4745107738599081994[33] = 0;
   out_4745107738599081994[34] = 0;
   out_4745107738599081994[35] = 0;
   out_4745107738599081994[36] = 0;
   out_4745107738599081994[37] = 0;
   out_4745107738599081994[38] = 0;
   out_4745107738599081994[39] = 0;
   out_4745107738599081994[40] = 1;
   out_4745107738599081994[41] = 0;
   out_4745107738599081994[42] = 0;
   out_4745107738599081994[43] = 0;
   out_4745107738599081994[44] = 0;
   out_4745107738599081994[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_4745107738599081994[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_4745107738599081994[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_4745107738599081994[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_4745107738599081994[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_4745107738599081994[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_4745107738599081994[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_4745107738599081994[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_4745107738599081994[53] = -9.8100000000000005*dt;
   out_4745107738599081994[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_4745107738599081994[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_4745107738599081994[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_4745107738599081994[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_4745107738599081994[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_4745107738599081994[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_4745107738599081994[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_4745107738599081994[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_4745107738599081994[62] = 0;
   out_4745107738599081994[63] = 0;
   out_4745107738599081994[64] = 0;
   out_4745107738599081994[65] = 0;
   out_4745107738599081994[66] = 0;
   out_4745107738599081994[67] = 0;
   out_4745107738599081994[68] = 0;
   out_4745107738599081994[69] = 0;
   out_4745107738599081994[70] = 1;
   out_4745107738599081994[71] = 0;
   out_4745107738599081994[72] = 0;
   out_4745107738599081994[73] = 0;
   out_4745107738599081994[74] = 0;
   out_4745107738599081994[75] = 0;
   out_4745107738599081994[76] = 0;
   out_4745107738599081994[77] = 0;
   out_4745107738599081994[78] = 0;
   out_4745107738599081994[79] = 0;
   out_4745107738599081994[80] = 1;
}
void h_25(double *state, double *unused, double *out_6483180039600536938) {
   out_6483180039600536938[0] = state[6];
}
void H_25(double *state, double *unused, double *out_262049243545390468) {
   out_262049243545390468[0] = 0;
   out_262049243545390468[1] = 0;
   out_262049243545390468[2] = 0;
   out_262049243545390468[3] = 0;
   out_262049243545390468[4] = 0;
   out_262049243545390468[5] = 0;
   out_262049243545390468[6] = 1;
   out_262049243545390468[7] = 0;
   out_262049243545390468[8] = 0;
}
void h_24(double *state, double *unused, double *out_7077662757578670640) {
   out_7077662757578670640[0] = state[4];
   out_7077662757578670640[1] = state[5];
}
void H_24(double *state, double *unused, double *out_2439263667152540441) {
   out_2439263667152540441[0] = 0;
   out_2439263667152540441[1] = 0;
   out_2439263667152540441[2] = 0;
   out_2439263667152540441[3] = 0;
   out_2439263667152540441[4] = 1;
   out_2439263667152540441[5] = 0;
   out_2439263667152540441[6] = 0;
   out_2439263667152540441[7] = 0;
   out_2439263667152540441[8] = 0;
   out_2439263667152540441[9] = 0;
   out_2439263667152540441[10] = 0;
   out_2439263667152540441[11] = 0;
   out_2439263667152540441[12] = 0;
   out_2439263667152540441[13] = 0;
   out_2439263667152540441[14] = 1;
   out_2439263667152540441[15] = 0;
   out_2439263667152540441[16] = 0;
   out_2439263667152540441[17] = 0;
}
void h_30(double *state, double *unused, double *out_5032548646971653771) {
   out_5032548646971653771[0] = state[4];
}
void H_30(double *state, double *unused, double *out_2780382202052639095) {
   out_2780382202052639095[0] = 0;
   out_2780382202052639095[1] = 0;
   out_2780382202052639095[2] = 0;
   out_2780382202052639095[3] = 0;
   out_2780382202052639095[4] = 1;
   out_2780382202052639095[5] = 0;
   out_2780382202052639095[6] = 0;
   out_2780382202052639095[7] = 0;
   out_2780382202052639095[8] = 0;
}
void h_26(double *state, double *unused, double *out_8072328190851867282) {
   out_8072328190851867282[0] = state[7];
}
void H_26(double *state, double *unused, double *out_3479454075328665756) {
   out_3479454075328665756[0] = 0;
   out_3479454075328665756[1] = 0;
   out_3479454075328665756[2] = 0;
   out_3479454075328665756[3] = 0;
   out_3479454075328665756[4] = 0;
   out_3479454075328665756[5] = 0;
   out_3479454075328665756[6] = 0;
   out_3479454075328665756[7] = 1;
   out_3479454075328665756[8] = 0;
}
void h_27(double *state, double *unused, double *out_2152949263878450231) {
   out_2152949263878450231[0] = state[3];
}
void H_27(double *state, double *unused, double *out_5003976273236582312) {
   out_5003976273236582312[0] = 0;
   out_5003976273236582312[1] = 0;
   out_5003976273236582312[2] = 0;
   out_5003976273236582312[3] = 1;
   out_5003976273236582312[4] = 0;
   out_5003976273236582312[5] = 0;
   out_5003976273236582312[6] = 0;
   out_5003976273236582312[7] = 0;
   out_5003976273236582312[8] = 0;
}
void h_29(double *state, double *unused, double *out_8412522159077052200) {
   out_8412522159077052200[0] = state[1];
}
void H_29(double *state, double *unused, double *out_3290613546367031279) {
   out_3290613546367031279[0] = 0;
   out_3290613546367031279[1] = 1;
   out_3290613546367031279[2] = 0;
   out_3290613546367031279[3] = 0;
   out_3290613546367031279[4] = 0;
   out_3290613546367031279[5] = 0;
   out_3290613546367031279[6] = 0;
   out_3290613546367031279[7] = 0;
   out_3290613546367031279[8] = 0;
}
void h_28(double *state, double *unused, double *out_7154622531539295876) {
   out_7154622531539295876[0] = state[0];
}
void H_28(double *state, double *unused, double *out_1791785470702499295) {
   out_1791785470702499295[0] = 1;
   out_1791785470702499295[1] = 0;
   out_1791785470702499295[2] = 0;
   out_1791785470702499295[3] = 0;
   out_1791785470702499295[4] = 0;
   out_1791785470702499295[5] = 0;
   out_1791785470702499295[6] = 0;
   out_1791785470702499295[7] = 0;
   out_1791785470702499295[8] = 0;
}
void h_31(double *state, double *unused, double *out_1398092611153512247) {
   out_1398092611153512247[0] = state[8];
}
void H_31(double *state, double *unused, double *out_4105662177562017232) {
   out_4105662177562017232[0] = 0;
   out_4105662177562017232[1] = 0;
   out_4105662177562017232[2] = 0;
   out_4105662177562017232[3] = 0;
   out_4105662177562017232[4] = 0;
   out_4105662177562017232[5] = 0;
   out_4105662177562017232[6] = 0;
   out_4105662177562017232[7] = 0;
   out_4105662177562017232[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_2055827145629245641) {
  err_fun(nom_x, delta_x, out_2055827145629245641);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_5357743043563844621) {
  inv_err_fun(nom_x, true_x, out_5357743043563844621);
}
void car_H_mod_fun(double *state, double *out_3260931406444101209) {
  H_mod_fun(state, out_3260931406444101209);
}
void car_f_fun(double *state, double dt, double *out_7842303097555582420) {
  f_fun(state,  dt, out_7842303097555582420);
}
void car_F_fun(double *state, double dt, double *out_4745107738599081994) {
  F_fun(state,  dt, out_4745107738599081994);
}
void car_h_25(double *state, double *unused, double *out_6483180039600536938) {
  h_25(state, unused, out_6483180039600536938);
}
void car_H_25(double *state, double *unused, double *out_262049243545390468) {
  H_25(state, unused, out_262049243545390468);
}
void car_h_24(double *state, double *unused, double *out_7077662757578670640) {
  h_24(state, unused, out_7077662757578670640);
}
void car_H_24(double *state, double *unused, double *out_2439263667152540441) {
  H_24(state, unused, out_2439263667152540441);
}
void car_h_30(double *state, double *unused, double *out_5032548646971653771) {
  h_30(state, unused, out_5032548646971653771);
}
void car_H_30(double *state, double *unused, double *out_2780382202052639095) {
  H_30(state, unused, out_2780382202052639095);
}
void car_h_26(double *state, double *unused, double *out_8072328190851867282) {
  h_26(state, unused, out_8072328190851867282);
}
void car_H_26(double *state, double *unused, double *out_3479454075328665756) {
  H_26(state, unused, out_3479454075328665756);
}
void car_h_27(double *state, double *unused, double *out_2152949263878450231) {
  h_27(state, unused, out_2152949263878450231);
}
void car_H_27(double *state, double *unused, double *out_5003976273236582312) {
  H_27(state, unused, out_5003976273236582312);
}
void car_h_29(double *state, double *unused, double *out_8412522159077052200) {
  h_29(state, unused, out_8412522159077052200);
}
void car_H_29(double *state, double *unused, double *out_3290613546367031279) {
  H_29(state, unused, out_3290613546367031279);
}
void car_h_28(double *state, double *unused, double *out_7154622531539295876) {
  h_28(state, unused, out_7154622531539295876);
}
void car_H_28(double *state, double *unused, double *out_1791785470702499295) {
  H_28(state, unused, out_1791785470702499295);
}
void car_h_31(double *state, double *unused, double *out_1398092611153512247) {
  h_31(state, unused, out_1398092611153512247);
}
void car_H_31(double *state, double *unused, double *out_4105662177562017232) {
  H_31(state, unused, out_4105662177562017232);
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
