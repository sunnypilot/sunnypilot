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
void err_fun(double *nom_x, double *delta_x, double *out_4244742674272470413) {
   out_4244742674272470413[0] = delta_x[0] + nom_x[0];
   out_4244742674272470413[1] = delta_x[1] + nom_x[1];
   out_4244742674272470413[2] = delta_x[2] + nom_x[2];
   out_4244742674272470413[3] = delta_x[3] + nom_x[3];
   out_4244742674272470413[4] = delta_x[4] + nom_x[4];
   out_4244742674272470413[5] = delta_x[5] + nom_x[5];
   out_4244742674272470413[6] = delta_x[6] + nom_x[6];
   out_4244742674272470413[7] = delta_x[7] + nom_x[7];
   out_4244742674272470413[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_4391628682247720481) {
   out_4391628682247720481[0] = -nom_x[0] + true_x[0];
   out_4391628682247720481[1] = -nom_x[1] + true_x[1];
   out_4391628682247720481[2] = -nom_x[2] + true_x[2];
   out_4391628682247720481[3] = -nom_x[3] + true_x[3];
   out_4391628682247720481[4] = -nom_x[4] + true_x[4];
   out_4391628682247720481[5] = -nom_x[5] + true_x[5];
   out_4391628682247720481[6] = -nom_x[6] + true_x[6];
   out_4391628682247720481[7] = -nom_x[7] + true_x[7];
   out_4391628682247720481[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_7497762910874470534) {
   out_7497762910874470534[0] = 1.0;
   out_7497762910874470534[1] = 0;
   out_7497762910874470534[2] = 0;
   out_7497762910874470534[3] = 0;
   out_7497762910874470534[4] = 0;
   out_7497762910874470534[5] = 0;
   out_7497762910874470534[6] = 0;
   out_7497762910874470534[7] = 0;
   out_7497762910874470534[8] = 0;
   out_7497762910874470534[9] = 0;
   out_7497762910874470534[10] = 1.0;
   out_7497762910874470534[11] = 0;
   out_7497762910874470534[12] = 0;
   out_7497762910874470534[13] = 0;
   out_7497762910874470534[14] = 0;
   out_7497762910874470534[15] = 0;
   out_7497762910874470534[16] = 0;
   out_7497762910874470534[17] = 0;
   out_7497762910874470534[18] = 0;
   out_7497762910874470534[19] = 0;
   out_7497762910874470534[20] = 1.0;
   out_7497762910874470534[21] = 0;
   out_7497762910874470534[22] = 0;
   out_7497762910874470534[23] = 0;
   out_7497762910874470534[24] = 0;
   out_7497762910874470534[25] = 0;
   out_7497762910874470534[26] = 0;
   out_7497762910874470534[27] = 0;
   out_7497762910874470534[28] = 0;
   out_7497762910874470534[29] = 0;
   out_7497762910874470534[30] = 1.0;
   out_7497762910874470534[31] = 0;
   out_7497762910874470534[32] = 0;
   out_7497762910874470534[33] = 0;
   out_7497762910874470534[34] = 0;
   out_7497762910874470534[35] = 0;
   out_7497762910874470534[36] = 0;
   out_7497762910874470534[37] = 0;
   out_7497762910874470534[38] = 0;
   out_7497762910874470534[39] = 0;
   out_7497762910874470534[40] = 1.0;
   out_7497762910874470534[41] = 0;
   out_7497762910874470534[42] = 0;
   out_7497762910874470534[43] = 0;
   out_7497762910874470534[44] = 0;
   out_7497762910874470534[45] = 0;
   out_7497762910874470534[46] = 0;
   out_7497762910874470534[47] = 0;
   out_7497762910874470534[48] = 0;
   out_7497762910874470534[49] = 0;
   out_7497762910874470534[50] = 1.0;
   out_7497762910874470534[51] = 0;
   out_7497762910874470534[52] = 0;
   out_7497762910874470534[53] = 0;
   out_7497762910874470534[54] = 0;
   out_7497762910874470534[55] = 0;
   out_7497762910874470534[56] = 0;
   out_7497762910874470534[57] = 0;
   out_7497762910874470534[58] = 0;
   out_7497762910874470534[59] = 0;
   out_7497762910874470534[60] = 1.0;
   out_7497762910874470534[61] = 0;
   out_7497762910874470534[62] = 0;
   out_7497762910874470534[63] = 0;
   out_7497762910874470534[64] = 0;
   out_7497762910874470534[65] = 0;
   out_7497762910874470534[66] = 0;
   out_7497762910874470534[67] = 0;
   out_7497762910874470534[68] = 0;
   out_7497762910874470534[69] = 0;
   out_7497762910874470534[70] = 1.0;
   out_7497762910874470534[71] = 0;
   out_7497762910874470534[72] = 0;
   out_7497762910874470534[73] = 0;
   out_7497762910874470534[74] = 0;
   out_7497762910874470534[75] = 0;
   out_7497762910874470534[76] = 0;
   out_7497762910874470534[77] = 0;
   out_7497762910874470534[78] = 0;
   out_7497762910874470534[79] = 0;
   out_7497762910874470534[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_2804212187320407990) {
   out_2804212187320407990[0] = state[0];
   out_2804212187320407990[1] = state[1];
   out_2804212187320407990[2] = state[2];
   out_2804212187320407990[3] = state[3];
   out_2804212187320407990[4] = state[4];
   out_2804212187320407990[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8000000000000007*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_2804212187320407990[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_2804212187320407990[7] = state[7];
   out_2804212187320407990[8] = state[8];
}
void F_fun(double *state, double dt, double *out_2566469647269033741) {
   out_2566469647269033741[0] = 1;
   out_2566469647269033741[1] = 0;
   out_2566469647269033741[2] = 0;
   out_2566469647269033741[3] = 0;
   out_2566469647269033741[4] = 0;
   out_2566469647269033741[5] = 0;
   out_2566469647269033741[6] = 0;
   out_2566469647269033741[7] = 0;
   out_2566469647269033741[8] = 0;
   out_2566469647269033741[9] = 0;
   out_2566469647269033741[10] = 1;
   out_2566469647269033741[11] = 0;
   out_2566469647269033741[12] = 0;
   out_2566469647269033741[13] = 0;
   out_2566469647269033741[14] = 0;
   out_2566469647269033741[15] = 0;
   out_2566469647269033741[16] = 0;
   out_2566469647269033741[17] = 0;
   out_2566469647269033741[18] = 0;
   out_2566469647269033741[19] = 0;
   out_2566469647269033741[20] = 1;
   out_2566469647269033741[21] = 0;
   out_2566469647269033741[22] = 0;
   out_2566469647269033741[23] = 0;
   out_2566469647269033741[24] = 0;
   out_2566469647269033741[25] = 0;
   out_2566469647269033741[26] = 0;
   out_2566469647269033741[27] = 0;
   out_2566469647269033741[28] = 0;
   out_2566469647269033741[29] = 0;
   out_2566469647269033741[30] = 1;
   out_2566469647269033741[31] = 0;
   out_2566469647269033741[32] = 0;
   out_2566469647269033741[33] = 0;
   out_2566469647269033741[34] = 0;
   out_2566469647269033741[35] = 0;
   out_2566469647269033741[36] = 0;
   out_2566469647269033741[37] = 0;
   out_2566469647269033741[38] = 0;
   out_2566469647269033741[39] = 0;
   out_2566469647269033741[40] = 1;
   out_2566469647269033741[41] = 0;
   out_2566469647269033741[42] = 0;
   out_2566469647269033741[43] = 0;
   out_2566469647269033741[44] = 0;
   out_2566469647269033741[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_2566469647269033741[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_2566469647269033741[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_2566469647269033741[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_2566469647269033741[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_2566469647269033741[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_2566469647269033741[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_2566469647269033741[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_2566469647269033741[53] = -9.8000000000000007*dt;
   out_2566469647269033741[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_2566469647269033741[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_2566469647269033741[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_2566469647269033741[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_2566469647269033741[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_2566469647269033741[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_2566469647269033741[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_2566469647269033741[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_2566469647269033741[62] = 0;
   out_2566469647269033741[63] = 0;
   out_2566469647269033741[64] = 0;
   out_2566469647269033741[65] = 0;
   out_2566469647269033741[66] = 0;
   out_2566469647269033741[67] = 0;
   out_2566469647269033741[68] = 0;
   out_2566469647269033741[69] = 0;
   out_2566469647269033741[70] = 1;
   out_2566469647269033741[71] = 0;
   out_2566469647269033741[72] = 0;
   out_2566469647269033741[73] = 0;
   out_2566469647269033741[74] = 0;
   out_2566469647269033741[75] = 0;
   out_2566469647269033741[76] = 0;
   out_2566469647269033741[77] = 0;
   out_2566469647269033741[78] = 0;
   out_2566469647269033741[79] = 0;
   out_2566469647269033741[80] = 1;
}
void h_25(double *state, double *unused, double *out_3243311392062354747) {
   out_3243311392062354747[0] = state[6];
}
void H_25(double *state, double *unused, double *out_2633319286481143646) {
   out_2633319286481143646[0] = 0;
   out_2633319286481143646[1] = 0;
   out_2633319286481143646[2] = 0;
   out_2633319286481143646[3] = 0;
   out_2633319286481143646[4] = 0;
   out_2633319286481143646[5] = 0;
   out_2633319286481143646[6] = 1;
   out_2633319286481143646[7] = 0;
   out_2633319286481143646[8] = 0;
}
void h_24(double *state, double *unused, double *out_317586459190038727) {
   out_317586459190038727[0] = state[4];
   out_317586459190038727[1] = state[5];
}
void H_24(double *state, double *unused, double *out_3942252520110374455) {
   out_3942252520110374455[0] = 0;
   out_3942252520110374455[1] = 0;
   out_3942252520110374455[2] = 0;
   out_3942252520110374455[3] = 0;
   out_3942252520110374455[4] = 1;
   out_3942252520110374455[5] = 0;
   out_3942252520110374455[6] = 0;
   out_3942252520110374455[7] = 0;
   out_3942252520110374455[8] = 0;
   out_3942252520110374455[9] = 0;
   out_3942252520110374455[10] = 0;
   out_3942252520110374455[11] = 0;
   out_3942252520110374455[12] = 0;
   out_3942252520110374455[13] = 0;
   out_3942252520110374455[14] = 1;
   out_3942252520110374455[15] = 0;
   out_3942252520110374455[16] = 0;
   out_3942252520110374455[17] = 0;
}
void h_30(double *state, double *unused, double *out_3097791567841699776) {
   out_3097791567841699776[0] = state[4];
}
void H_30(double *state, double *unused, double *out_7161015616608751844) {
   out_7161015616608751844[0] = 0;
   out_7161015616608751844[1] = 0;
   out_7161015616608751844[2] = 0;
   out_7161015616608751844[3] = 0;
   out_7161015616608751844[4] = 1;
   out_7161015616608751844[5] = 0;
   out_7161015616608751844[6] = 0;
   out_7161015616608751844[7] = 0;
   out_7161015616608751844[8] = 0;
}
void h_26(double *state, double *unused, double *out_8099464835502545421) {
   out_8099464835502545421[0] = state[7];
}
void H_26(double *state, double *unused, double *out_6374822605355199870) {
   out_6374822605355199870[0] = 0;
   out_6374822605355199870[1] = 0;
   out_6374822605355199870[2] = 0;
   out_6374822605355199870[3] = 0;
   out_6374822605355199870[4] = 0;
   out_6374822605355199870[5] = 0;
   out_6374822605355199870[6] = 0;
   out_6374822605355199870[7] = 1;
   out_6374822605355199870[8] = 0;
}
void h_27(double *state, double *unused, double *out_1758361875598490898) {
   out_1758361875598490898[0] = state[3];
}
void H_27(double *state, double *unused, double *out_4937421545424808627) {
   out_4937421545424808627[0] = 0;
   out_4937421545424808627[1] = 0;
   out_4937421545424808627[2] = 0;
   out_4937421545424808627[3] = 1;
   out_4937421545424808627[4] = 0;
   out_4937421545424808627[5] = 0;
   out_4937421545424808627[6] = 0;
   out_4937421545424808627[7] = 0;
   out_4937421545424808627[8] = 0;
}
void h_29(double *state, double *unused, double *out_5620045352026992550) {
   out_5620045352026992550[0] = state[1];
}
void H_29(double *state, double *unused, double *out_6650784272294359660) {
   out_6650784272294359660[0] = 0;
   out_6650784272294359660[1] = 1;
   out_6650784272294359660[2] = 0;
   out_6650784272294359660[3] = 0;
   out_6650784272294359660[4] = 0;
   out_6650784272294359660[5] = 0;
   out_6650784272294359660[6] = 0;
   out_6650784272294359660[7] = 0;
   out_6650784272294359660[8] = 0;
}
void h_28(double *state, double *unused, double *out_814852022696828463) {
   out_814852022696828463[0] = state[0];
}
void H_28(double *state, double *unused, double *out_4687154000729033409) {
   out_4687154000729033409[0] = 1;
   out_4687154000729033409[1] = 0;
   out_4687154000729033409[2] = 0;
   out_4687154000729033409[3] = 0;
   out_4687154000729033409[4] = 0;
   out_4687154000729033409[5] = 0;
   out_4687154000729033409[6] = 0;
   out_4687154000729033409[7] = 0;
   out_4687154000729033409[8] = 0;
}
void h_31(double *state, double *unused, double *out_4519953864758317694) {
   out_4519953864758317694[0] = state[8];
}
void H_31(double *state, double *unused, double *out_2602673324604183218) {
   out_2602673324604183218[0] = 0;
   out_2602673324604183218[1] = 0;
   out_2602673324604183218[2] = 0;
   out_2602673324604183218[3] = 0;
   out_2602673324604183218[4] = 0;
   out_2602673324604183218[5] = 0;
   out_2602673324604183218[6] = 0;
   out_2602673324604183218[7] = 0;
   out_2602673324604183218[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_4244742674272470413) {
  err_fun(nom_x, delta_x, out_4244742674272470413);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_4391628682247720481) {
  inv_err_fun(nom_x, true_x, out_4391628682247720481);
}
void car_H_mod_fun(double *state, double *out_7497762910874470534) {
  H_mod_fun(state, out_7497762910874470534);
}
void car_f_fun(double *state, double dt, double *out_2804212187320407990) {
  f_fun(state,  dt, out_2804212187320407990);
}
void car_F_fun(double *state, double dt, double *out_2566469647269033741) {
  F_fun(state,  dt, out_2566469647269033741);
}
void car_h_25(double *state, double *unused, double *out_3243311392062354747) {
  h_25(state, unused, out_3243311392062354747);
}
void car_H_25(double *state, double *unused, double *out_2633319286481143646) {
  H_25(state, unused, out_2633319286481143646);
}
void car_h_24(double *state, double *unused, double *out_317586459190038727) {
  h_24(state, unused, out_317586459190038727);
}
void car_H_24(double *state, double *unused, double *out_3942252520110374455) {
  H_24(state, unused, out_3942252520110374455);
}
void car_h_30(double *state, double *unused, double *out_3097791567841699776) {
  h_30(state, unused, out_3097791567841699776);
}
void car_H_30(double *state, double *unused, double *out_7161015616608751844) {
  H_30(state, unused, out_7161015616608751844);
}
void car_h_26(double *state, double *unused, double *out_8099464835502545421) {
  h_26(state, unused, out_8099464835502545421);
}
void car_H_26(double *state, double *unused, double *out_6374822605355199870) {
  H_26(state, unused, out_6374822605355199870);
}
void car_h_27(double *state, double *unused, double *out_1758361875598490898) {
  h_27(state, unused, out_1758361875598490898);
}
void car_H_27(double *state, double *unused, double *out_4937421545424808627) {
  H_27(state, unused, out_4937421545424808627);
}
void car_h_29(double *state, double *unused, double *out_5620045352026992550) {
  h_29(state, unused, out_5620045352026992550);
}
void car_H_29(double *state, double *unused, double *out_6650784272294359660) {
  H_29(state, unused, out_6650784272294359660);
}
void car_h_28(double *state, double *unused, double *out_814852022696828463) {
  h_28(state, unused, out_814852022696828463);
}
void car_H_28(double *state, double *unused, double *out_4687154000729033409) {
  H_28(state, unused, out_4687154000729033409);
}
void car_h_31(double *state, double *unused, double *out_4519953864758317694) {
  h_31(state, unused, out_4519953864758317694);
}
void car_H_31(double *state, double *unused, double *out_2602673324604183218) {
  H_31(state, unused, out_2602673324604183218);
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
