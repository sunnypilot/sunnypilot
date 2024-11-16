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
void err_fun(double *nom_x, double *delta_x, double *out_8249429775729676839) {
   out_8249429775729676839[0] = delta_x[0] + nom_x[0];
   out_8249429775729676839[1] = delta_x[1] + nom_x[1];
   out_8249429775729676839[2] = delta_x[2] + nom_x[2];
   out_8249429775729676839[3] = delta_x[3] + nom_x[3];
   out_8249429775729676839[4] = delta_x[4] + nom_x[4];
   out_8249429775729676839[5] = delta_x[5] + nom_x[5];
   out_8249429775729676839[6] = delta_x[6] + nom_x[6];
   out_8249429775729676839[7] = delta_x[7] + nom_x[7];
   out_8249429775729676839[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_830104287538898022) {
   out_830104287538898022[0] = -nom_x[0] + true_x[0];
   out_830104287538898022[1] = -nom_x[1] + true_x[1];
   out_830104287538898022[2] = -nom_x[2] + true_x[2];
   out_830104287538898022[3] = -nom_x[3] + true_x[3];
   out_830104287538898022[4] = -nom_x[4] + true_x[4];
   out_830104287538898022[5] = -nom_x[5] + true_x[5];
   out_830104287538898022[6] = -nom_x[6] + true_x[6];
   out_830104287538898022[7] = -nom_x[7] + true_x[7];
   out_830104287538898022[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_4361542019279921949) {
   out_4361542019279921949[0] = 1.0;
   out_4361542019279921949[1] = 0;
   out_4361542019279921949[2] = 0;
   out_4361542019279921949[3] = 0;
   out_4361542019279921949[4] = 0;
   out_4361542019279921949[5] = 0;
   out_4361542019279921949[6] = 0;
   out_4361542019279921949[7] = 0;
   out_4361542019279921949[8] = 0;
   out_4361542019279921949[9] = 0;
   out_4361542019279921949[10] = 1.0;
   out_4361542019279921949[11] = 0;
   out_4361542019279921949[12] = 0;
   out_4361542019279921949[13] = 0;
   out_4361542019279921949[14] = 0;
   out_4361542019279921949[15] = 0;
   out_4361542019279921949[16] = 0;
   out_4361542019279921949[17] = 0;
   out_4361542019279921949[18] = 0;
   out_4361542019279921949[19] = 0;
   out_4361542019279921949[20] = 1.0;
   out_4361542019279921949[21] = 0;
   out_4361542019279921949[22] = 0;
   out_4361542019279921949[23] = 0;
   out_4361542019279921949[24] = 0;
   out_4361542019279921949[25] = 0;
   out_4361542019279921949[26] = 0;
   out_4361542019279921949[27] = 0;
   out_4361542019279921949[28] = 0;
   out_4361542019279921949[29] = 0;
   out_4361542019279921949[30] = 1.0;
   out_4361542019279921949[31] = 0;
   out_4361542019279921949[32] = 0;
   out_4361542019279921949[33] = 0;
   out_4361542019279921949[34] = 0;
   out_4361542019279921949[35] = 0;
   out_4361542019279921949[36] = 0;
   out_4361542019279921949[37] = 0;
   out_4361542019279921949[38] = 0;
   out_4361542019279921949[39] = 0;
   out_4361542019279921949[40] = 1.0;
   out_4361542019279921949[41] = 0;
   out_4361542019279921949[42] = 0;
   out_4361542019279921949[43] = 0;
   out_4361542019279921949[44] = 0;
   out_4361542019279921949[45] = 0;
   out_4361542019279921949[46] = 0;
   out_4361542019279921949[47] = 0;
   out_4361542019279921949[48] = 0;
   out_4361542019279921949[49] = 0;
   out_4361542019279921949[50] = 1.0;
   out_4361542019279921949[51] = 0;
   out_4361542019279921949[52] = 0;
   out_4361542019279921949[53] = 0;
   out_4361542019279921949[54] = 0;
   out_4361542019279921949[55] = 0;
   out_4361542019279921949[56] = 0;
   out_4361542019279921949[57] = 0;
   out_4361542019279921949[58] = 0;
   out_4361542019279921949[59] = 0;
   out_4361542019279921949[60] = 1.0;
   out_4361542019279921949[61] = 0;
   out_4361542019279921949[62] = 0;
   out_4361542019279921949[63] = 0;
   out_4361542019279921949[64] = 0;
   out_4361542019279921949[65] = 0;
   out_4361542019279921949[66] = 0;
   out_4361542019279921949[67] = 0;
   out_4361542019279921949[68] = 0;
   out_4361542019279921949[69] = 0;
   out_4361542019279921949[70] = 1.0;
   out_4361542019279921949[71] = 0;
   out_4361542019279921949[72] = 0;
   out_4361542019279921949[73] = 0;
   out_4361542019279921949[74] = 0;
   out_4361542019279921949[75] = 0;
   out_4361542019279921949[76] = 0;
   out_4361542019279921949[77] = 0;
   out_4361542019279921949[78] = 0;
   out_4361542019279921949[79] = 0;
   out_4361542019279921949[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_2834190715000315846) {
   out_2834190715000315846[0] = state[0];
   out_2834190715000315846[1] = state[1];
   out_2834190715000315846[2] = state[2];
   out_2834190715000315846[3] = state[3];
   out_2834190715000315846[4] = state[4];
   out_2834190715000315846[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8000000000000007*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_2834190715000315846[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_2834190715000315846[7] = state[7];
   out_2834190715000315846[8] = state[8];
}
void F_fun(double *state, double dt, double *out_8944307819367133251) {
   out_8944307819367133251[0] = 1;
   out_8944307819367133251[1] = 0;
   out_8944307819367133251[2] = 0;
   out_8944307819367133251[3] = 0;
   out_8944307819367133251[4] = 0;
   out_8944307819367133251[5] = 0;
   out_8944307819367133251[6] = 0;
   out_8944307819367133251[7] = 0;
   out_8944307819367133251[8] = 0;
   out_8944307819367133251[9] = 0;
   out_8944307819367133251[10] = 1;
   out_8944307819367133251[11] = 0;
   out_8944307819367133251[12] = 0;
   out_8944307819367133251[13] = 0;
   out_8944307819367133251[14] = 0;
   out_8944307819367133251[15] = 0;
   out_8944307819367133251[16] = 0;
   out_8944307819367133251[17] = 0;
   out_8944307819367133251[18] = 0;
   out_8944307819367133251[19] = 0;
   out_8944307819367133251[20] = 1;
   out_8944307819367133251[21] = 0;
   out_8944307819367133251[22] = 0;
   out_8944307819367133251[23] = 0;
   out_8944307819367133251[24] = 0;
   out_8944307819367133251[25] = 0;
   out_8944307819367133251[26] = 0;
   out_8944307819367133251[27] = 0;
   out_8944307819367133251[28] = 0;
   out_8944307819367133251[29] = 0;
   out_8944307819367133251[30] = 1;
   out_8944307819367133251[31] = 0;
   out_8944307819367133251[32] = 0;
   out_8944307819367133251[33] = 0;
   out_8944307819367133251[34] = 0;
   out_8944307819367133251[35] = 0;
   out_8944307819367133251[36] = 0;
   out_8944307819367133251[37] = 0;
   out_8944307819367133251[38] = 0;
   out_8944307819367133251[39] = 0;
   out_8944307819367133251[40] = 1;
   out_8944307819367133251[41] = 0;
   out_8944307819367133251[42] = 0;
   out_8944307819367133251[43] = 0;
   out_8944307819367133251[44] = 0;
   out_8944307819367133251[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_8944307819367133251[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_8944307819367133251[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_8944307819367133251[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_8944307819367133251[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_8944307819367133251[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_8944307819367133251[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_8944307819367133251[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_8944307819367133251[53] = -9.8000000000000007*dt;
   out_8944307819367133251[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_8944307819367133251[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_8944307819367133251[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_8944307819367133251[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_8944307819367133251[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_8944307819367133251[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_8944307819367133251[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_8944307819367133251[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_8944307819367133251[62] = 0;
   out_8944307819367133251[63] = 0;
   out_8944307819367133251[64] = 0;
   out_8944307819367133251[65] = 0;
   out_8944307819367133251[66] = 0;
   out_8944307819367133251[67] = 0;
   out_8944307819367133251[68] = 0;
   out_8944307819367133251[69] = 0;
   out_8944307819367133251[70] = 1;
   out_8944307819367133251[71] = 0;
   out_8944307819367133251[72] = 0;
   out_8944307819367133251[73] = 0;
   out_8944307819367133251[74] = 0;
   out_8944307819367133251[75] = 0;
   out_8944307819367133251[76] = 0;
   out_8944307819367133251[77] = 0;
   out_8944307819367133251[78] = 0;
   out_8944307819367133251[79] = 0;
   out_8944307819367133251[80] = 1;
}
void h_25(double *state, double *unused, double *out_4307604535579416709) {
   out_4307604535579416709[0] = state[6];
}
void H_25(double *state, double *unused, double *out_7813441128818867203) {
   out_7813441128818867203[0] = 0;
   out_7813441128818867203[1] = 0;
   out_7813441128818867203[2] = 0;
   out_7813441128818867203[3] = 0;
   out_7813441128818867203[4] = 0;
   out_7813441128818867203[5] = 0;
   out_7813441128818867203[6] = 1;
   out_7813441128818867203[7] = 0;
   out_7813441128818867203[8] = 0;
}
void h_24(double *state, double *unused, double *out_6273662611818280039) {
   out_6273662611818280039[0] = state[4];
   out_6273662611818280039[1] = state[5];
}
void H_24(double *state, double *unused, double *out_5886793617924175379) {
   out_5886793617924175379[0] = 0;
   out_5886793617924175379[1] = 0;
   out_5886793617924175379[2] = 0;
   out_5886793617924175379[3] = 0;
   out_5886793617924175379[4] = 1;
   out_5886793617924175379[5] = 0;
   out_5886793617924175379[6] = 0;
   out_5886793617924175379[7] = 0;
   out_5886793617924175379[8] = 0;
   out_5886793617924175379[9] = 0;
   out_5886793617924175379[10] = 0;
   out_5886793617924175379[11] = 0;
   out_5886793617924175379[12] = 0;
   out_5886793617924175379[13] = 0;
   out_5886793617924175379[14] = 1;
   out_5886793617924175379[15] = 0;
   out_5886793617924175379[16] = 0;
   out_5886793617924175379[17] = 0;
}
void h_30(double *state, double *unused, double *out_5931642792047228057) {
   out_5931642792047228057[0] = state[4];
}
void H_30(double *state, double *unused, double *out_896750787327250448) {
   out_896750787327250448[0] = 0;
   out_896750787327250448[1] = 0;
   out_896750787327250448[2] = 0;
   out_896750787327250448[3] = 0;
   out_896750787327250448[4] = 1;
   out_896750787327250448[5] = 0;
   out_896750787327250448[6] = 0;
   out_896750787327250448[7] = 0;
   out_896750787327250448[8] = 0;
}
void h_26(double *state, double *unused, double *out_6116059764248474413) {
   out_6116059764248474413[0] = state[7];
}
void H_26(double *state, double *unused, double *out_6891799626016628189) {
   out_6891799626016628189[0] = 0;
   out_6891799626016628189[1] = 0;
   out_6891799626016628189[2] = 0;
   out_6891799626016628189[3] = 0;
   out_6891799626016628189[4] = 0;
   out_6891799626016628189[5] = 0;
   out_6891799626016628189[6] = 0;
   out_6891799626016628189[7] = 1;
   out_6891799626016628189[8] = 0;
}
void h_27(double *state, double *unused, double *out_4488704928686580431) {
   out_4488704928686580431[0] = state[3];
}
void H_27(double *state, double *unused, double *out_8329200685947019432) {
   out_8329200685947019432[0] = 0;
   out_8329200685947019432[1] = 0;
   out_8329200685947019432[2] = 0;
   out_8329200685947019432[3] = 1;
   out_8329200685947019432[4] = 0;
   out_8329200685947019432[5] = 0;
   out_8329200685947019432[6] = 0;
   out_8329200685947019432[7] = 0;
   out_8329200685947019432[8] = 0;
}
void h_29(double *state, double *unused, double *out_8350388405115082083) {
   out_8350388405115082083[0] = state[1];
}
void H_29(double *state, double *unused, double *out_7432548731647715089) {
   out_7432548731647715089[0] = 0;
   out_7432548731647715089[1] = 1;
   out_7432548731647715089[2] = 0;
   out_7432548731647715089[3] = 0;
   out_7432548731647715089[4] = 0;
   out_7432548731647715089[5] = 0;
   out_7432548731647715089[6] = 0;
   out_7432548731647715089[7] = 0;
   out_7432548731647715089[8] = 0;
}
void h_28(double *state, double *unused, double *out_2722204557567641080) {
   out_2722204557567641080[0] = state[0];
}
void H_28(double *state, double *unused, double *out_8579468230642794650) {
   out_8579468230642794650[0] = 1;
   out_8579468230642794650[1] = 0;
   out_8579468230642794650[2] = 0;
   out_8579468230642794650[3] = 0;
   out_8579468230642794650[4] = 0;
   out_8579468230642794650[5] = 0;
   out_8579468230642794650[6] = 0;
   out_8579468230642794650[7] = 0;
   out_8579468230642794650[8] = 0;
}
void h_31(double *state, double *unused, double *out_4150417867228287564) {
   out_4150417867228287564[0] = state[8];
}
void H_31(double *state, double *unused, double *out_7782795166941906775) {
   out_7782795166941906775[0] = 0;
   out_7782795166941906775[1] = 0;
   out_7782795166941906775[2] = 0;
   out_7782795166941906775[3] = 0;
   out_7782795166941906775[4] = 0;
   out_7782795166941906775[5] = 0;
   out_7782795166941906775[6] = 0;
   out_7782795166941906775[7] = 0;
   out_7782795166941906775[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_8249429775729676839) {
  err_fun(nom_x, delta_x, out_8249429775729676839);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_830104287538898022) {
  inv_err_fun(nom_x, true_x, out_830104287538898022);
}
void car_H_mod_fun(double *state, double *out_4361542019279921949) {
  H_mod_fun(state, out_4361542019279921949);
}
void car_f_fun(double *state, double dt, double *out_2834190715000315846) {
  f_fun(state,  dt, out_2834190715000315846);
}
void car_F_fun(double *state, double dt, double *out_8944307819367133251) {
  F_fun(state,  dt, out_8944307819367133251);
}
void car_h_25(double *state, double *unused, double *out_4307604535579416709) {
  h_25(state, unused, out_4307604535579416709);
}
void car_H_25(double *state, double *unused, double *out_7813441128818867203) {
  H_25(state, unused, out_7813441128818867203);
}
void car_h_24(double *state, double *unused, double *out_6273662611818280039) {
  h_24(state, unused, out_6273662611818280039);
}
void car_H_24(double *state, double *unused, double *out_5886793617924175379) {
  H_24(state, unused, out_5886793617924175379);
}
void car_h_30(double *state, double *unused, double *out_5931642792047228057) {
  h_30(state, unused, out_5931642792047228057);
}
void car_H_30(double *state, double *unused, double *out_896750787327250448) {
  H_30(state, unused, out_896750787327250448);
}
void car_h_26(double *state, double *unused, double *out_6116059764248474413) {
  h_26(state, unused, out_6116059764248474413);
}
void car_H_26(double *state, double *unused, double *out_6891799626016628189) {
  H_26(state, unused, out_6891799626016628189);
}
void car_h_27(double *state, double *unused, double *out_4488704928686580431) {
  h_27(state, unused, out_4488704928686580431);
}
void car_H_27(double *state, double *unused, double *out_8329200685947019432) {
  H_27(state, unused, out_8329200685947019432);
}
void car_h_29(double *state, double *unused, double *out_8350388405115082083) {
  h_29(state, unused, out_8350388405115082083);
}
void car_H_29(double *state, double *unused, double *out_7432548731647715089) {
  H_29(state, unused, out_7432548731647715089);
}
void car_h_28(double *state, double *unused, double *out_2722204557567641080) {
  h_28(state, unused, out_2722204557567641080);
}
void car_H_28(double *state, double *unused, double *out_8579468230642794650) {
  H_28(state, unused, out_8579468230642794650);
}
void car_h_31(double *state, double *unused, double *out_4150417867228287564) {
  h_31(state, unused, out_4150417867228287564);
}
void car_H_31(double *state, double *unused, double *out_7782795166941906775) {
  H_31(state, unused, out_7782795166941906775);
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
