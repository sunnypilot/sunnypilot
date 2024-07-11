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
void err_fun(double *nom_x, double *delta_x, double *out_5515282840857201190) {
   out_5515282840857201190[0] = delta_x[0] + nom_x[0];
   out_5515282840857201190[1] = delta_x[1] + nom_x[1];
   out_5515282840857201190[2] = delta_x[2] + nom_x[2];
   out_5515282840857201190[3] = delta_x[3] + nom_x[3];
   out_5515282840857201190[4] = delta_x[4] + nom_x[4];
   out_5515282840857201190[5] = delta_x[5] + nom_x[5];
   out_5515282840857201190[6] = delta_x[6] + nom_x[6];
   out_5515282840857201190[7] = delta_x[7] + nom_x[7];
   out_5515282840857201190[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_7649367513361168321) {
   out_7649367513361168321[0] = -nom_x[0] + true_x[0];
   out_7649367513361168321[1] = -nom_x[1] + true_x[1];
   out_7649367513361168321[2] = -nom_x[2] + true_x[2];
   out_7649367513361168321[3] = -nom_x[3] + true_x[3];
   out_7649367513361168321[4] = -nom_x[4] + true_x[4];
   out_7649367513361168321[5] = -nom_x[5] + true_x[5];
   out_7649367513361168321[6] = -nom_x[6] + true_x[6];
   out_7649367513361168321[7] = -nom_x[7] + true_x[7];
   out_7649367513361168321[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_9120682032769952111) {
   out_9120682032769952111[0] = 1.0;
   out_9120682032769952111[1] = 0;
   out_9120682032769952111[2] = 0;
   out_9120682032769952111[3] = 0;
   out_9120682032769952111[4] = 0;
   out_9120682032769952111[5] = 0;
   out_9120682032769952111[6] = 0;
   out_9120682032769952111[7] = 0;
   out_9120682032769952111[8] = 0;
   out_9120682032769952111[9] = 0;
   out_9120682032769952111[10] = 1.0;
   out_9120682032769952111[11] = 0;
   out_9120682032769952111[12] = 0;
   out_9120682032769952111[13] = 0;
   out_9120682032769952111[14] = 0;
   out_9120682032769952111[15] = 0;
   out_9120682032769952111[16] = 0;
   out_9120682032769952111[17] = 0;
   out_9120682032769952111[18] = 0;
   out_9120682032769952111[19] = 0;
   out_9120682032769952111[20] = 1.0;
   out_9120682032769952111[21] = 0;
   out_9120682032769952111[22] = 0;
   out_9120682032769952111[23] = 0;
   out_9120682032769952111[24] = 0;
   out_9120682032769952111[25] = 0;
   out_9120682032769952111[26] = 0;
   out_9120682032769952111[27] = 0;
   out_9120682032769952111[28] = 0;
   out_9120682032769952111[29] = 0;
   out_9120682032769952111[30] = 1.0;
   out_9120682032769952111[31] = 0;
   out_9120682032769952111[32] = 0;
   out_9120682032769952111[33] = 0;
   out_9120682032769952111[34] = 0;
   out_9120682032769952111[35] = 0;
   out_9120682032769952111[36] = 0;
   out_9120682032769952111[37] = 0;
   out_9120682032769952111[38] = 0;
   out_9120682032769952111[39] = 0;
   out_9120682032769952111[40] = 1.0;
   out_9120682032769952111[41] = 0;
   out_9120682032769952111[42] = 0;
   out_9120682032769952111[43] = 0;
   out_9120682032769952111[44] = 0;
   out_9120682032769952111[45] = 0;
   out_9120682032769952111[46] = 0;
   out_9120682032769952111[47] = 0;
   out_9120682032769952111[48] = 0;
   out_9120682032769952111[49] = 0;
   out_9120682032769952111[50] = 1.0;
   out_9120682032769952111[51] = 0;
   out_9120682032769952111[52] = 0;
   out_9120682032769952111[53] = 0;
   out_9120682032769952111[54] = 0;
   out_9120682032769952111[55] = 0;
   out_9120682032769952111[56] = 0;
   out_9120682032769952111[57] = 0;
   out_9120682032769952111[58] = 0;
   out_9120682032769952111[59] = 0;
   out_9120682032769952111[60] = 1.0;
   out_9120682032769952111[61] = 0;
   out_9120682032769952111[62] = 0;
   out_9120682032769952111[63] = 0;
   out_9120682032769952111[64] = 0;
   out_9120682032769952111[65] = 0;
   out_9120682032769952111[66] = 0;
   out_9120682032769952111[67] = 0;
   out_9120682032769952111[68] = 0;
   out_9120682032769952111[69] = 0;
   out_9120682032769952111[70] = 1.0;
   out_9120682032769952111[71] = 0;
   out_9120682032769952111[72] = 0;
   out_9120682032769952111[73] = 0;
   out_9120682032769952111[74] = 0;
   out_9120682032769952111[75] = 0;
   out_9120682032769952111[76] = 0;
   out_9120682032769952111[77] = 0;
   out_9120682032769952111[78] = 0;
   out_9120682032769952111[79] = 0;
   out_9120682032769952111[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_6653043797221081730) {
   out_6653043797221081730[0] = state[0];
   out_6653043797221081730[1] = state[1];
   out_6653043797221081730[2] = state[2];
   out_6653043797221081730[3] = state[3];
   out_6653043797221081730[4] = state[4];
   out_6653043797221081730[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8000000000000007*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_6653043797221081730[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_6653043797221081730[7] = state[7];
   out_6653043797221081730[8] = state[8];
}
void F_fun(double *state, double dt, double *out_2733155322343162446) {
   out_2733155322343162446[0] = 1;
   out_2733155322343162446[1] = 0;
   out_2733155322343162446[2] = 0;
   out_2733155322343162446[3] = 0;
   out_2733155322343162446[4] = 0;
   out_2733155322343162446[5] = 0;
   out_2733155322343162446[6] = 0;
   out_2733155322343162446[7] = 0;
   out_2733155322343162446[8] = 0;
   out_2733155322343162446[9] = 0;
   out_2733155322343162446[10] = 1;
   out_2733155322343162446[11] = 0;
   out_2733155322343162446[12] = 0;
   out_2733155322343162446[13] = 0;
   out_2733155322343162446[14] = 0;
   out_2733155322343162446[15] = 0;
   out_2733155322343162446[16] = 0;
   out_2733155322343162446[17] = 0;
   out_2733155322343162446[18] = 0;
   out_2733155322343162446[19] = 0;
   out_2733155322343162446[20] = 1;
   out_2733155322343162446[21] = 0;
   out_2733155322343162446[22] = 0;
   out_2733155322343162446[23] = 0;
   out_2733155322343162446[24] = 0;
   out_2733155322343162446[25] = 0;
   out_2733155322343162446[26] = 0;
   out_2733155322343162446[27] = 0;
   out_2733155322343162446[28] = 0;
   out_2733155322343162446[29] = 0;
   out_2733155322343162446[30] = 1;
   out_2733155322343162446[31] = 0;
   out_2733155322343162446[32] = 0;
   out_2733155322343162446[33] = 0;
   out_2733155322343162446[34] = 0;
   out_2733155322343162446[35] = 0;
   out_2733155322343162446[36] = 0;
   out_2733155322343162446[37] = 0;
   out_2733155322343162446[38] = 0;
   out_2733155322343162446[39] = 0;
   out_2733155322343162446[40] = 1;
   out_2733155322343162446[41] = 0;
   out_2733155322343162446[42] = 0;
   out_2733155322343162446[43] = 0;
   out_2733155322343162446[44] = 0;
   out_2733155322343162446[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_2733155322343162446[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_2733155322343162446[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_2733155322343162446[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_2733155322343162446[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_2733155322343162446[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_2733155322343162446[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_2733155322343162446[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_2733155322343162446[53] = -9.8000000000000007*dt;
   out_2733155322343162446[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_2733155322343162446[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_2733155322343162446[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_2733155322343162446[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_2733155322343162446[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_2733155322343162446[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_2733155322343162446[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_2733155322343162446[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_2733155322343162446[62] = 0;
   out_2733155322343162446[63] = 0;
   out_2733155322343162446[64] = 0;
   out_2733155322343162446[65] = 0;
   out_2733155322343162446[66] = 0;
   out_2733155322343162446[67] = 0;
   out_2733155322343162446[68] = 0;
   out_2733155322343162446[69] = 0;
   out_2733155322343162446[70] = 1;
   out_2733155322343162446[71] = 0;
   out_2733155322343162446[72] = 0;
   out_2733155322343162446[73] = 0;
   out_2733155322343162446[74] = 0;
   out_2733155322343162446[75] = 0;
   out_2733155322343162446[76] = 0;
   out_2733155322343162446[77] = 0;
   out_2733155322343162446[78] = 0;
   out_2733155322343162446[79] = 0;
   out_2733155322343162446[80] = 1;
}
void h_25(double *state, double *unused, double *out_4036115050903680798) {
   out_4036115050903680798[0] = state[6];
}
void H_25(double *state, double *unused, double *out_7980036622989360732) {
   out_7980036622989360732[0] = 0;
   out_7980036622989360732[1] = 0;
   out_7980036622989360732[2] = 0;
   out_7980036622989360732[3] = 0;
   out_7980036622989360732[4] = 0;
   out_7980036622989360732[5] = 0;
   out_7980036622989360732[6] = 1;
   out_7980036622989360732[7] = 0;
   out_7980036622989360732[8] = 0;
}
void h_24(double *state, double *unused, double *out_4949789322380165994) {
   out_4949789322380165994[0] = state[4];
   out_4949789322380165994[1] = state[5];
}
void H_24(double *state, double *unused, double *out_5720198123753681850) {
   out_5720198123753681850[0] = 0;
   out_5720198123753681850[1] = 0;
   out_5720198123753681850[2] = 0;
   out_5720198123753681850[3] = 0;
   out_5720198123753681850[4] = 1;
   out_5720198123753681850[5] = 0;
   out_5720198123753681850[6] = 0;
   out_5720198123753681850[7] = 0;
   out_5720198123753681850[8] = 0;
   out_5720198123753681850[9] = 0;
   out_5720198123753681850[10] = 0;
   out_5720198123753681850[11] = 0;
   out_5720198123753681850[12] = 0;
   out_5720198123753681850[13] = 0;
   out_5720198123753681850[14] = 1;
   out_5720198123753681850[15] = 0;
   out_5720198123753681850[16] = 0;
   out_5720198123753681850[17] = 0;
}
void h_30(double *state, double *unused, double *out_7223676118347812489) {
   out_7223676118347812489[0] = state[4];
}
void H_30(double *state, double *unused, double *out_5461703664482112105) {
   out_5461703664482112105[0] = 0;
   out_5461703664482112105[1] = 0;
   out_5461703664482112105[2] = 0;
   out_5461703664482112105[3] = 0;
   out_5461703664482112105[4] = 1;
   out_5461703664482112105[5] = 0;
   out_5461703664482112105[6] = 0;
   out_5461703664482112105[7] = 0;
   out_5461703664482112105[8] = 0;
}
void h_26(double *state, double *unused, double *out_2222002850686966844) {
   out_2222002850686966844[0] = state[7];
}
void H_26(double *state, double *unused, double *out_6725204131846134660) {
   out_6725204131846134660[0] = 0;
   out_6725204131846134660[1] = 0;
   out_6725204131846134660[2] = 0;
   out_6725204131846134660[3] = 0;
   out_6725204131846134660[4] = 0;
   out_6725204131846134660[5] = 0;
   out_6725204131846134660[6] = 0;
   out_6725204131846134660[7] = 1;
   out_6725204131846134660[8] = 0;
}
void h_27(double *state, double *unused, double *out_4706019044014513237) {
   out_4706019044014513237[0] = state[3];
}
void H_27(double *state, double *unused, double *out_7636466976282537016) {
   out_7636466976282537016[0] = 0;
   out_7636466976282537016[1] = 0;
   out_7636466976282537016[2] = 0;
   out_7636466976282537016[3] = 1;
   out_7636466976282537016[4] = 0;
   out_7636466976282537016[5] = 0;
   out_7636466976282537016[6] = 0;
   out_7636466976282537016[7] = 0;
   out_7636466976282537016[8] = 0;
}
void h_29(double *state, double *unused, double *out_6797707040063507594) {
   out_6797707040063507594[0] = state[1];
}
void H_29(double *state, double *unused, double *out_4951472320167719921) {
   out_4951472320167719921[0] = 0;
   out_4951472320167719921[1] = 1;
   out_4951472320167719921[2] = 0;
   out_4951472320167719921[3] = 0;
   out_4951472320167719921[4] = 0;
   out_4951472320167719921[5] = 0;
   out_4951472320167719921[6] = 0;
   out_4951472320167719921[7] = 0;
   out_4951472320167719921[8] = 0;
}
void h_28(double *state, double *unused, double *out_7341683512281189233) {
   out_7341683512281189233[0] = state[0];
}
void H_28(double *state, double *unused, double *out_8412872736472301121) {
   out_8412872736472301121[0] = 1;
   out_8412872736472301121[1] = 0;
   out_8412872736472301121[2] = 0;
   out_8412872736472301121[3] = 0;
   out_8412872736472301121[4] = 0;
   out_8412872736472301121[5] = 0;
   out_8412872736472301121[6] = 0;
   out_8412872736472301121[7] = 0;
   out_8412872736472301121[8] = 0;
}
void h_31(double *state, double *unused, double *out_8946784456945013104) {
   out_8946784456945013104[0] = state[8];
}
void H_31(double *state, double *unused, double *out_6098996029612783184) {
   out_6098996029612783184[0] = 0;
   out_6098996029612783184[1] = 0;
   out_6098996029612783184[2] = 0;
   out_6098996029612783184[3] = 0;
   out_6098996029612783184[4] = 0;
   out_6098996029612783184[5] = 0;
   out_6098996029612783184[6] = 0;
   out_6098996029612783184[7] = 0;
   out_6098996029612783184[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_5515282840857201190) {
  err_fun(nom_x, delta_x, out_5515282840857201190);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_7649367513361168321) {
  inv_err_fun(nom_x, true_x, out_7649367513361168321);
}
void car_H_mod_fun(double *state, double *out_9120682032769952111) {
  H_mod_fun(state, out_9120682032769952111);
}
void car_f_fun(double *state, double dt, double *out_6653043797221081730) {
  f_fun(state,  dt, out_6653043797221081730);
}
void car_F_fun(double *state, double dt, double *out_2733155322343162446) {
  F_fun(state,  dt, out_2733155322343162446);
}
void car_h_25(double *state, double *unused, double *out_4036115050903680798) {
  h_25(state, unused, out_4036115050903680798);
}
void car_H_25(double *state, double *unused, double *out_7980036622989360732) {
  H_25(state, unused, out_7980036622989360732);
}
void car_h_24(double *state, double *unused, double *out_4949789322380165994) {
  h_24(state, unused, out_4949789322380165994);
}
void car_H_24(double *state, double *unused, double *out_5720198123753681850) {
  H_24(state, unused, out_5720198123753681850);
}
void car_h_30(double *state, double *unused, double *out_7223676118347812489) {
  h_30(state, unused, out_7223676118347812489);
}
void car_H_30(double *state, double *unused, double *out_5461703664482112105) {
  H_30(state, unused, out_5461703664482112105);
}
void car_h_26(double *state, double *unused, double *out_2222002850686966844) {
  h_26(state, unused, out_2222002850686966844);
}
void car_H_26(double *state, double *unused, double *out_6725204131846134660) {
  H_26(state, unused, out_6725204131846134660);
}
void car_h_27(double *state, double *unused, double *out_4706019044014513237) {
  h_27(state, unused, out_4706019044014513237);
}
void car_H_27(double *state, double *unused, double *out_7636466976282537016) {
  H_27(state, unused, out_7636466976282537016);
}
void car_h_29(double *state, double *unused, double *out_6797707040063507594) {
  h_29(state, unused, out_6797707040063507594);
}
void car_H_29(double *state, double *unused, double *out_4951472320167719921) {
  H_29(state, unused, out_4951472320167719921);
}
void car_h_28(double *state, double *unused, double *out_7341683512281189233) {
  h_28(state, unused, out_7341683512281189233);
}
void car_H_28(double *state, double *unused, double *out_8412872736472301121) {
  H_28(state, unused, out_8412872736472301121);
}
void car_h_31(double *state, double *unused, double *out_8946784456945013104) {
  h_31(state, unused, out_8946784456945013104);
}
void car_H_31(double *state, double *unused, double *out_6098996029612783184) {
  H_31(state, unused, out_6098996029612783184);
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
