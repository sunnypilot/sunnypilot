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
 *                      Code generated with SymPy 1.13.2                      *
 *                                                                            *
 *              See http://www.sympy.org/ for more information.               *
 *                                                                            *
 *                         This file is part of 'ekf'                         *
 ******************************************************************************/
void err_fun(double *nom_x, double *delta_x, double *out_2733505511915312304) {
   out_2733505511915312304[0] = delta_x[0] + nom_x[0];
   out_2733505511915312304[1] = delta_x[1] + nom_x[1];
   out_2733505511915312304[2] = delta_x[2] + nom_x[2];
   out_2733505511915312304[3] = delta_x[3] + nom_x[3];
   out_2733505511915312304[4] = delta_x[4] + nom_x[4];
   out_2733505511915312304[5] = delta_x[5] + nom_x[5];
   out_2733505511915312304[6] = delta_x[6] + nom_x[6];
   out_2733505511915312304[7] = delta_x[7] + nom_x[7];
   out_2733505511915312304[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_2042722913738173368) {
   out_2042722913738173368[0] = -nom_x[0] + true_x[0];
   out_2042722913738173368[1] = -nom_x[1] + true_x[1];
   out_2042722913738173368[2] = -nom_x[2] + true_x[2];
   out_2042722913738173368[3] = -nom_x[3] + true_x[3];
   out_2042722913738173368[4] = -nom_x[4] + true_x[4];
   out_2042722913738173368[5] = -nom_x[5] + true_x[5];
   out_2042722913738173368[6] = -nom_x[6] + true_x[6];
   out_2042722913738173368[7] = -nom_x[7] + true_x[7];
   out_2042722913738173368[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_8648682746173350729) {
   out_8648682746173350729[0] = 1.0;
   out_8648682746173350729[1] = 0.0;
   out_8648682746173350729[2] = 0.0;
   out_8648682746173350729[3] = 0.0;
   out_8648682746173350729[4] = 0.0;
   out_8648682746173350729[5] = 0.0;
   out_8648682746173350729[6] = 0.0;
   out_8648682746173350729[7] = 0.0;
   out_8648682746173350729[8] = 0.0;
   out_8648682746173350729[9] = 0.0;
   out_8648682746173350729[10] = 1.0;
   out_8648682746173350729[11] = 0.0;
   out_8648682746173350729[12] = 0.0;
   out_8648682746173350729[13] = 0.0;
   out_8648682746173350729[14] = 0.0;
   out_8648682746173350729[15] = 0.0;
   out_8648682746173350729[16] = 0.0;
   out_8648682746173350729[17] = 0.0;
   out_8648682746173350729[18] = 0.0;
   out_8648682746173350729[19] = 0.0;
   out_8648682746173350729[20] = 1.0;
   out_8648682746173350729[21] = 0.0;
   out_8648682746173350729[22] = 0.0;
   out_8648682746173350729[23] = 0.0;
   out_8648682746173350729[24] = 0.0;
   out_8648682746173350729[25] = 0.0;
   out_8648682746173350729[26] = 0.0;
   out_8648682746173350729[27] = 0.0;
   out_8648682746173350729[28] = 0.0;
   out_8648682746173350729[29] = 0.0;
   out_8648682746173350729[30] = 1.0;
   out_8648682746173350729[31] = 0.0;
   out_8648682746173350729[32] = 0.0;
   out_8648682746173350729[33] = 0.0;
   out_8648682746173350729[34] = 0.0;
   out_8648682746173350729[35] = 0.0;
   out_8648682746173350729[36] = 0.0;
   out_8648682746173350729[37] = 0.0;
   out_8648682746173350729[38] = 0.0;
   out_8648682746173350729[39] = 0.0;
   out_8648682746173350729[40] = 1.0;
   out_8648682746173350729[41] = 0.0;
   out_8648682746173350729[42] = 0.0;
   out_8648682746173350729[43] = 0.0;
   out_8648682746173350729[44] = 0.0;
   out_8648682746173350729[45] = 0.0;
   out_8648682746173350729[46] = 0.0;
   out_8648682746173350729[47] = 0.0;
   out_8648682746173350729[48] = 0.0;
   out_8648682746173350729[49] = 0.0;
   out_8648682746173350729[50] = 1.0;
   out_8648682746173350729[51] = 0.0;
   out_8648682746173350729[52] = 0.0;
   out_8648682746173350729[53] = 0.0;
   out_8648682746173350729[54] = 0.0;
   out_8648682746173350729[55] = 0.0;
   out_8648682746173350729[56] = 0.0;
   out_8648682746173350729[57] = 0.0;
   out_8648682746173350729[58] = 0.0;
   out_8648682746173350729[59] = 0.0;
   out_8648682746173350729[60] = 1.0;
   out_8648682746173350729[61] = 0.0;
   out_8648682746173350729[62] = 0.0;
   out_8648682746173350729[63] = 0.0;
   out_8648682746173350729[64] = 0.0;
   out_8648682746173350729[65] = 0.0;
   out_8648682746173350729[66] = 0.0;
   out_8648682746173350729[67] = 0.0;
   out_8648682746173350729[68] = 0.0;
   out_8648682746173350729[69] = 0.0;
   out_8648682746173350729[70] = 1.0;
   out_8648682746173350729[71] = 0.0;
   out_8648682746173350729[72] = 0.0;
   out_8648682746173350729[73] = 0.0;
   out_8648682746173350729[74] = 0.0;
   out_8648682746173350729[75] = 0.0;
   out_8648682746173350729[76] = 0.0;
   out_8648682746173350729[77] = 0.0;
   out_8648682746173350729[78] = 0.0;
   out_8648682746173350729[79] = 0.0;
   out_8648682746173350729[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_4433059162913028335) {
   out_4433059162913028335[0] = state[0];
   out_4433059162913028335[1] = state[1];
   out_4433059162913028335[2] = state[2];
   out_4433059162913028335[3] = state[3];
   out_4433059162913028335[4] = state[4];
   out_4433059162913028335[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8000000000000007*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_4433059162913028335[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_4433059162913028335[7] = state[7];
   out_4433059162913028335[8] = state[8];
}
void F_fun(double *state, double dt, double *out_7479330613641780172) {
   out_7479330613641780172[0] = 1;
   out_7479330613641780172[1] = 0;
   out_7479330613641780172[2] = 0;
   out_7479330613641780172[3] = 0;
   out_7479330613641780172[4] = 0;
   out_7479330613641780172[5] = 0;
   out_7479330613641780172[6] = 0;
   out_7479330613641780172[7] = 0;
   out_7479330613641780172[8] = 0;
   out_7479330613641780172[9] = 0;
   out_7479330613641780172[10] = 1;
   out_7479330613641780172[11] = 0;
   out_7479330613641780172[12] = 0;
   out_7479330613641780172[13] = 0;
   out_7479330613641780172[14] = 0;
   out_7479330613641780172[15] = 0;
   out_7479330613641780172[16] = 0;
   out_7479330613641780172[17] = 0;
   out_7479330613641780172[18] = 0;
   out_7479330613641780172[19] = 0;
   out_7479330613641780172[20] = 1;
   out_7479330613641780172[21] = 0;
   out_7479330613641780172[22] = 0;
   out_7479330613641780172[23] = 0;
   out_7479330613641780172[24] = 0;
   out_7479330613641780172[25] = 0;
   out_7479330613641780172[26] = 0;
   out_7479330613641780172[27] = 0;
   out_7479330613641780172[28] = 0;
   out_7479330613641780172[29] = 0;
   out_7479330613641780172[30] = 1;
   out_7479330613641780172[31] = 0;
   out_7479330613641780172[32] = 0;
   out_7479330613641780172[33] = 0;
   out_7479330613641780172[34] = 0;
   out_7479330613641780172[35] = 0;
   out_7479330613641780172[36] = 0;
   out_7479330613641780172[37] = 0;
   out_7479330613641780172[38] = 0;
   out_7479330613641780172[39] = 0;
   out_7479330613641780172[40] = 1;
   out_7479330613641780172[41] = 0;
   out_7479330613641780172[42] = 0;
   out_7479330613641780172[43] = 0;
   out_7479330613641780172[44] = 0;
   out_7479330613641780172[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_7479330613641780172[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_7479330613641780172[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_7479330613641780172[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_7479330613641780172[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_7479330613641780172[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_7479330613641780172[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_7479330613641780172[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_7479330613641780172[53] = -9.8000000000000007*dt;
   out_7479330613641780172[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_7479330613641780172[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_7479330613641780172[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_7479330613641780172[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_7479330613641780172[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_7479330613641780172[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_7479330613641780172[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_7479330613641780172[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_7479330613641780172[62] = 0;
   out_7479330613641780172[63] = 0;
   out_7479330613641780172[64] = 0;
   out_7479330613641780172[65] = 0;
   out_7479330613641780172[66] = 0;
   out_7479330613641780172[67] = 0;
   out_7479330613641780172[68] = 0;
   out_7479330613641780172[69] = 0;
   out_7479330613641780172[70] = 1;
   out_7479330613641780172[71] = 0;
   out_7479330613641780172[72] = 0;
   out_7479330613641780172[73] = 0;
   out_7479330613641780172[74] = 0;
   out_7479330613641780172[75] = 0;
   out_7479330613641780172[76] = 0;
   out_7479330613641780172[77] = 0;
   out_7479330613641780172[78] = 0;
   out_7479330613641780172[79] = 0;
   out_7479330613641780172[80] = 1;
}
void h_25(double *state, double *unused, double *out_9005739562334179017) {
   out_9005739562334179017[0] = state[6];
}
void H_25(double *state, double *unused, double *out_604873101623963650) {
   out_604873101623963650[0] = 0;
   out_604873101623963650[1] = 0;
   out_604873101623963650[2] = 0;
   out_604873101623963650[3] = 0;
   out_604873101623963650[4] = 0;
   out_604873101623963650[5] = 0;
   out_604873101623963650[6] = 1;
   out_604873101623963650[7] = 0;
   out_604873101623963650[8] = 0;
}
void h_24(double *state, double *unused, double *out_1699962084933975115) {
   out_1699962084933975115[0] = state[4];
   out_1699962084933975115[1] = state[5];
}
void H_24(double *state, double *unused, double *out_8613805786016392741) {
   out_8613805786016392741[0] = 0;
   out_8613805786016392741[1] = 0;
   out_8613805786016392741[2] = 0;
   out_8613805786016392741[3] = 0;
   out_8613805786016392741[4] = 1;
   out_8613805786016392741[5] = 0;
   out_8613805786016392741[6] = 0;
   out_8613805786016392741[7] = 0;
   out_8613805786016392741[8] = 0;
   out_8613805786016392741[9] = 0;
   out_8613805786016392741[10] = 0;
   out_8613805786016392741[11] = 0;
   out_8613805786016392741[12] = 0;
   out_8613805786016392741[13] = 0;
   out_8613805786016392741[14] = 1;
   out_8613805786016392741[15] = 0;
   out_8613805786016392741[16] = 0;
   out_8613805786016392741[17] = 0;
}
void h_30(double *state, double *unused, double *out_1559731860621323414) {
   out_1559731860621323414[0] = state[4];
}
void H_30(double *state, double *unused, double *out_3922823228503644548) {
   out_3922823228503644548[0] = 0;
   out_3922823228503644548[1] = 0;
   out_3922823228503644548[2] = 0;
   out_3922823228503644548[3] = 0;
   out_3922823228503644548[4] = 1;
   out_3922823228503644548[5] = 0;
   out_3922823228503644548[6] = 0;
   out_3922823228503644548[7] = 0;
   out_3922823228503644548[8] = 0;
}
void h_26(double *state, double *unused, double *out_6561405128282169059) {
   out_6561405128282169059[0] = state[7];
}
void H_26(double *state, double *unused, double *out_3136630217250092574) {
   out_3136630217250092574[0] = 0;
   out_3136630217250092574[1] = 0;
   out_3136630217250092574[2] = 0;
   out_3136630217250092574[3] = 0;
   out_3136630217250092574[4] = 0;
   out_3136630217250092574[5] = 0;
   out_3136630217250092574[6] = 0;
   out_3136630217250092574[7] = 1;
   out_3136630217250092574[8] = 0;
}
void h_27(double *state, double *unused, double *out_4267593512827365087) {
   out_4267593512827365087[0] = state[3];
}
void H_27(double *state, double *unused, double *out_6097586540304069459) {
   out_6097586540304069459[0] = 0;
   out_6097586540304069459[1] = 0;
   out_6097586540304069459[2] = 0;
   out_6097586540304069459[3] = 1;
   out_6097586540304069459[4] = 0;
   out_6097586540304069459[5] = 0;
   out_6097586540304069459[6] = 0;
   out_6097586540304069459[7] = 0;
   out_6097586540304069459[8] = 0;
}
void h_29(double *state, double *unused, double *out_4542787575111870976) {
   out_4542787575111870976[0] = state[1];
}
void H_29(double *state, double *unused, double *out_3412591884189252364) {
   out_3412591884189252364[0] = 0;
   out_3412591884189252364[1] = 1;
   out_3412591884189252364[2] = 0;
   out_3412591884189252364[3] = 0;
   out_3412591884189252364[4] = 0;
   out_3412591884189252364[5] = 0;
   out_3412591884189252364[6] = 0;
   out_3412591884189252364[7] = 0;
   out_3412591884189252364[8] = 0;
}
void h_28(double *state, double *unused, double *out_1663188192018667436) {
   out_1663188192018667436[0] = state[0];
}
void H_28(double *state, double *unused, double *out_1448961612623926113) {
   out_1448961612623926113[0] = 1;
   out_1448961612623926113[1] = 0;
   out_1448961612623926113[2] = 0;
   out_1448961612623926113[3] = 0;
   out_1448961612623926113[4] = 0;
   out_1448961612623926113[5] = 0;
   out_1448961612623926113[6] = 0;
   out_1448961612623926113[7] = 0;
   out_1448961612623926113[8] = 0;
}
void h_31(double *state, double *unused, double *out_4595763231261982210) {
   out_4595763231261982210[0] = state[8];
}
void H_31(double *state, double *unused, double *out_3762838319483444050) {
   out_3762838319483444050[0] = 0;
   out_3762838319483444050[1] = 0;
   out_3762838319483444050[2] = 0;
   out_3762838319483444050[3] = 0;
   out_3762838319483444050[4] = 0;
   out_3762838319483444050[5] = 0;
   out_3762838319483444050[6] = 0;
   out_3762838319483444050[7] = 0;
   out_3762838319483444050[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_2733505511915312304) {
  err_fun(nom_x, delta_x, out_2733505511915312304);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_2042722913738173368) {
  inv_err_fun(nom_x, true_x, out_2042722913738173368);
}
void car_H_mod_fun(double *state, double *out_8648682746173350729) {
  H_mod_fun(state, out_8648682746173350729);
}
void car_f_fun(double *state, double dt, double *out_4433059162913028335) {
  f_fun(state,  dt, out_4433059162913028335);
}
void car_F_fun(double *state, double dt, double *out_7479330613641780172) {
  F_fun(state,  dt, out_7479330613641780172);
}
void car_h_25(double *state, double *unused, double *out_9005739562334179017) {
  h_25(state, unused, out_9005739562334179017);
}
void car_H_25(double *state, double *unused, double *out_604873101623963650) {
  H_25(state, unused, out_604873101623963650);
}
void car_h_24(double *state, double *unused, double *out_1699962084933975115) {
  h_24(state, unused, out_1699962084933975115);
}
void car_H_24(double *state, double *unused, double *out_8613805786016392741) {
  H_24(state, unused, out_8613805786016392741);
}
void car_h_30(double *state, double *unused, double *out_1559731860621323414) {
  h_30(state, unused, out_1559731860621323414);
}
void car_H_30(double *state, double *unused, double *out_3922823228503644548) {
  H_30(state, unused, out_3922823228503644548);
}
void car_h_26(double *state, double *unused, double *out_6561405128282169059) {
  h_26(state, unused, out_6561405128282169059);
}
void car_H_26(double *state, double *unused, double *out_3136630217250092574) {
  H_26(state, unused, out_3136630217250092574);
}
void car_h_27(double *state, double *unused, double *out_4267593512827365087) {
  h_27(state, unused, out_4267593512827365087);
}
void car_H_27(double *state, double *unused, double *out_6097586540304069459) {
  H_27(state, unused, out_6097586540304069459);
}
void car_h_29(double *state, double *unused, double *out_4542787575111870976) {
  h_29(state, unused, out_4542787575111870976);
}
void car_H_29(double *state, double *unused, double *out_3412591884189252364) {
  H_29(state, unused, out_3412591884189252364);
}
void car_h_28(double *state, double *unused, double *out_1663188192018667436) {
  h_28(state, unused, out_1663188192018667436);
}
void car_H_28(double *state, double *unused, double *out_1448961612623926113) {
  H_28(state, unused, out_1448961612623926113);
}
void car_h_31(double *state, double *unused, double *out_4595763231261982210) {
  h_31(state, unused, out_4595763231261982210);
}
void car_H_31(double *state, double *unused, double *out_3762838319483444050) {
  H_31(state, unused, out_3762838319483444050);
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
