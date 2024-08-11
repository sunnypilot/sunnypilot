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
void err_fun(double *nom_x, double *delta_x, double *out_4680039436617746285) {
   out_4680039436617746285[0] = delta_x[0] + nom_x[0];
   out_4680039436617746285[1] = delta_x[1] + nom_x[1];
   out_4680039436617746285[2] = delta_x[2] + nom_x[2];
   out_4680039436617746285[3] = delta_x[3] + nom_x[3];
   out_4680039436617746285[4] = delta_x[4] + nom_x[4];
   out_4680039436617746285[5] = delta_x[5] + nom_x[5];
   out_4680039436617746285[6] = delta_x[6] + nom_x[6];
   out_4680039436617746285[7] = delta_x[7] + nom_x[7];
   out_4680039436617746285[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_6464047771063674000) {
   out_6464047771063674000[0] = -nom_x[0] + true_x[0];
   out_6464047771063674000[1] = -nom_x[1] + true_x[1];
   out_6464047771063674000[2] = -nom_x[2] + true_x[2];
   out_6464047771063674000[3] = -nom_x[3] + true_x[3];
   out_6464047771063674000[4] = -nom_x[4] + true_x[4];
   out_6464047771063674000[5] = -nom_x[5] + true_x[5];
   out_6464047771063674000[6] = -nom_x[6] + true_x[6];
   out_6464047771063674000[7] = -nom_x[7] + true_x[7];
   out_6464047771063674000[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_915927946953392880) {
   out_915927946953392880[0] = 1.0;
   out_915927946953392880[1] = 0;
   out_915927946953392880[2] = 0;
   out_915927946953392880[3] = 0;
   out_915927946953392880[4] = 0;
   out_915927946953392880[5] = 0;
   out_915927946953392880[6] = 0;
   out_915927946953392880[7] = 0;
   out_915927946953392880[8] = 0;
   out_915927946953392880[9] = 0;
   out_915927946953392880[10] = 1.0;
   out_915927946953392880[11] = 0;
   out_915927946953392880[12] = 0;
   out_915927946953392880[13] = 0;
   out_915927946953392880[14] = 0;
   out_915927946953392880[15] = 0;
   out_915927946953392880[16] = 0;
   out_915927946953392880[17] = 0;
   out_915927946953392880[18] = 0;
   out_915927946953392880[19] = 0;
   out_915927946953392880[20] = 1.0;
   out_915927946953392880[21] = 0;
   out_915927946953392880[22] = 0;
   out_915927946953392880[23] = 0;
   out_915927946953392880[24] = 0;
   out_915927946953392880[25] = 0;
   out_915927946953392880[26] = 0;
   out_915927946953392880[27] = 0;
   out_915927946953392880[28] = 0;
   out_915927946953392880[29] = 0;
   out_915927946953392880[30] = 1.0;
   out_915927946953392880[31] = 0;
   out_915927946953392880[32] = 0;
   out_915927946953392880[33] = 0;
   out_915927946953392880[34] = 0;
   out_915927946953392880[35] = 0;
   out_915927946953392880[36] = 0;
   out_915927946953392880[37] = 0;
   out_915927946953392880[38] = 0;
   out_915927946953392880[39] = 0;
   out_915927946953392880[40] = 1.0;
   out_915927946953392880[41] = 0;
   out_915927946953392880[42] = 0;
   out_915927946953392880[43] = 0;
   out_915927946953392880[44] = 0;
   out_915927946953392880[45] = 0;
   out_915927946953392880[46] = 0;
   out_915927946953392880[47] = 0;
   out_915927946953392880[48] = 0;
   out_915927946953392880[49] = 0;
   out_915927946953392880[50] = 1.0;
   out_915927946953392880[51] = 0;
   out_915927946953392880[52] = 0;
   out_915927946953392880[53] = 0;
   out_915927946953392880[54] = 0;
   out_915927946953392880[55] = 0;
   out_915927946953392880[56] = 0;
   out_915927946953392880[57] = 0;
   out_915927946953392880[58] = 0;
   out_915927946953392880[59] = 0;
   out_915927946953392880[60] = 1.0;
   out_915927946953392880[61] = 0;
   out_915927946953392880[62] = 0;
   out_915927946953392880[63] = 0;
   out_915927946953392880[64] = 0;
   out_915927946953392880[65] = 0;
   out_915927946953392880[66] = 0;
   out_915927946953392880[67] = 0;
   out_915927946953392880[68] = 0;
   out_915927946953392880[69] = 0;
   out_915927946953392880[70] = 1.0;
   out_915927946953392880[71] = 0;
   out_915927946953392880[72] = 0;
   out_915927946953392880[73] = 0;
   out_915927946953392880[74] = 0;
   out_915927946953392880[75] = 0;
   out_915927946953392880[76] = 0;
   out_915927946953392880[77] = 0;
   out_915927946953392880[78] = 0;
   out_915927946953392880[79] = 0;
   out_915927946953392880[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_5875377148384648318) {
   out_5875377148384648318[0] = state[0];
   out_5875377148384648318[1] = state[1];
   out_5875377148384648318[2] = state[2];
   out_5875377148384648318[3] = state[3];
   out_5875377148384648318[4] = state[4];
   out_5875377148384648318[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8000000000000007*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_5875377148384648318[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_5875377148384648318[7] = state[7];
   out_5875377148384648318[8] = state[8];
}
void F_fun(double *state, double dt, double *out_3741941609747229027) {
   out_3741941609747229027[0] = 1;
   out_3741941609747229027[1] = 0;
   out_3741941609747229027[2] = 0;
   out_3741941609747229027[3] = 0;
   out_3741941609747229027[4] = 0;
   out_3741941609747229027[5] = 0;
   out_3741941609747229027[6] = 0;
   out_3741941609747229027[7] = 0;
   out_3741941609747229027[8] = 0;
   out_3741941609747229027[9] = 0;
   out_3741941609747229027[10] = 1;
   out_3741941609747229027[11] = 0;
   out_3741941609747229027[12] = 0;
   out_3741941609747229027[13] = 0;
   out_3741941609747229027[14] = 0;
   out_3741941609747229027[15] = 0;
   out_3741941609747229027[16] = 0;
   out_3741941609747229027[17] = 0;
   out_3741941609747229027[18] = 0;
   out_3741941609747229027[19] = 0;
   out_3741941609747229027[20] = 1;
   out_3741941609747229027[21] = 0;
   out_3741941609747229027[22] = 0;
   out_3741941609747229027[23] = 0;
   out_3741941609747229027[24] = 0;
   out_3741941609747229027[25] = 0;
   out_3741941609747229027[26] = 0;
   out_3741941609747229027[27] = 0;
   out_3741941609747229027[28] = 0;
   out_3741941609747229027[29] = 0;
   out_3741941609747229027[30] = 1;
   out_3741941609747229027[31] = 0;
   out_3741941609747229027[32] = 0;
   out_3741941609747229027[33] = 0;
   out_3741941609747229027[34] = 0;
   out_3741941609747229027[35] = 0;
   out_3741941609747229027[36] = 0;
   out_3741941609747229027[37] = 0;
   out_3741941609747229027[38] = 0;
   out_3741941609747229027[39] = 0;
   out_3741941609747229027[40] = 1;
   out_3741941609747229027[41] = 0;
   out_3741941609747229027[42] = 0;
   out_3741941609747229027[43] = 0;
   out_3741941609747229027[44] = 0;
   out_3741941609747229027[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_3741941609747229027[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_3741941609747229027[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_3741941609747229027[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_3741941609747229027[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_3741941609747229027[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_3741941609747229027[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_3741941609747229027[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_3741941609747229027[53] = -9.8000000000000007*dt;
   out_3741941609747229027[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_3741941609747229027[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_3741941609747229027[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_3741941609747229027[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_3741941609747229027[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_3741941609747229027[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_3741941609747229027[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_3741941609747229027[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_3741941609747229027[62] = 0;
   out_3741941609747229027[63] = 0;
   out_3741941609747229027[64] = 0;
   out_3741941609747229027[65] = 0;
   out_3741941609747229027[66] = 0;
   out_3741941609747229027[67] = 0;
   out_3741941609747229027[68] = 0;
   out_3741941609747229027[69] = 0;
   out_3741941609747229027[70] = 1;
   out_3741941609747229027[71] = 0;
   out_3741941609747229027[72] = 0;
   out_3741941609747229027[73] = 0;
   out_3741941609747229027[74] = 0;
   out_3741941609747229027[75] = 0;
   out_3741941609747229027[76] = 0;
   out_3741941609747229027[77] = 0;
   out_3741941609747229027[78] = 0;
   out_3741941609747229027[79] = 0;
   out_3741941609747229027[80] = 1;
}
void h_25(double *state, double *unused, double *out_5013938002243898062) {
   out_5013938002243898062[0] = state[6];
}
void H_25(double *state, double *unused, double *out_4811433704179120774) {
   out_4811433704179120774[0] = 0;
   out_4811433704179120774[1] = 0;
   out_4811433704179120774[2] = 0;
   out_4811433704179120774[3] = 0;
   out_4811433704179120774[4] = 0;
   out_4811433704179120774[5] = 0;
   out_4811433704179120774[6] = 1;
   out_4811433704179120774[7] = 0;
   out_4811433704179120774[8] = 0;
}
void h_24(double *state, double *unused, double *out_7703538372309607031) {
   out_7703538372309607031[0] = state[4];
   out_7703538372309607031[1] = state[5];
}
void H_24(double *state, double *unused, double *out_2638784105173621208) {
   out_2638784105173621208[0] = 0;
   out_2638784105173621208[1] = 0;
   out_2638784105173621208[2] = 0;
   out_2638784105173621208[3] = 0;
   out_2638784105173621208[4] = 1;
   out_2638784105173621208[5] = 0;
   out_2638784105173621208[6] = 0;
   out_2638784105173621208[7] = 0;
   out_2638784105173621208[8] = 0;
   out_2638784105173621208[9] = 0;
   out_2638784105173621208[10] = 0;
   out_2638784105173621208[11] = 0;
   out_2638784105173621208[12] = 0;
   out_2638784105173621208[13] = 0;
   out_2638784105173621208[14] = 1;
   out_2638784105173621208[15] = 0;
   out_2638784105173621208[16] = 0;
   out_2638784105173621208[17] = 0;
}
void h_30(double *state, double *unused, double *out_1376488473989875712) {
   out_1376488473989875712[0] = state[4];
}
void H_30(double *state, double *unused, double *out_7329766662686369401) {
   out_7329766662686369401[0] = 0;
   out_7329766662686369401[1] = 0;
   out_7329766662686369401[2] = 0;
   out_7329766662686369401[3] = 0;
   out_7329766662686369401[4] = 1;
   out_7329766662686369401[5] = 0;
   out_7329766662686369401[6] = 0;
   out_7329766662686369401[7] = 0;
   out_7329766662686369401[8] = 0;
}
void h_26(double *state, double *unused, double *out_7605480698016965053) {
   out_7605480698016965053[0] = state[7];
}
void H_26(double *state, double *unused, double *out_1069930385305064550) {
   out_1069930385305064550[0] = 0;
   out_1069930385305064550[1] = 0;
   out_1069930385305064550[2] = 0;
   out_1069930385305064550[3] = 0;
   out_1069930385305064550[4] = 0;
   out_1069930385305064550[5] = 0;
   out_1069930385305064550[6] = 0;
   out_1069930385305064550[7] = 1;
   out_1069930385305064550[8] = 0;
}
void h_27(double *state, double *unused, double *out_12264734583052417) {
   out_12264734583052417[0] = state[3];
}
void H_27(double *state, double *unused, double *out_8893383339839238998) {
   out_8893383339839238998[0] = 0;
   out_8893383339839238998[1] = 0;
   out_8893383339839238998[2] = 0;
   out_8893383339839238998[3] = 1;
   out_8893383339839238998[4] = 0;
   out_8893383339839238998[5] = 0;
   out_8893383339839238998[6] = 0;
   out_8893383339839238998[7] = 0;
   out_8893383339839238998[8] = 0;
}
void h_29(double *state, double *unused, double *out_3625184793670969933) {
   out_3625184793670969933[0] = state[1];
}
void H_29(double *state, double *unused, double *out_7839998007000761585) {
   out_7839998007000761585[0] = 0;
   out_7839998007000761585[1] = 1;
   out_7839998007000761585[2] = 0;
   out_7839998007000761585[3] = 0;
   out_7839998007000761585[4] = 0;
   out_7839998007000761585[5] = 0;
   out_7839998007000761585[6] = 0;
   out_7839998007000761585[7] = 0;
   out_7839998007000761585[8] = 0;
}
void h_28(double *state, double *unused, double *out_3393257316228255090) {
   out_3393257316228255090[0] = state[0];
}
void H_28(double *state, double *unused, double *out_2757598989931231011) {
   out_2757598989931231011[0] = 1;
   out_2757598989931231011[1] = 0;
   out_2757598989931231011[2] = 0;
   out_2757598989931231011[3] = 0;
   out_2757598989931231011[4] = 0;
   out_2757598989931231011[5] = 0;
   out_2757598989931231011[6] = 0;
   out_2757598989931231011[7] = 0;
   out_2757598989931231011[8] = 0;
}
void h_31(double *state, double *unused, double *out_2446620762004990263) {
   out_2446620762004990263[0] = state[8];
}
void H_31(double *state, double *unused, double *out_443722283071713074) {
   out_443722283071713074[0] = 0;
   out_443722283071713074[1] = 0;
   out_443722283071713074[2] = 0;
   out_443722283071713074[3] = 0;
   out_443722283071713074[4] = 0;
   out_443722283071713074[5] = 0;
   out_443722283071713074[6] = 0;
   out_443722283071713074[7] = 0;
   out_443722283071713074[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_4680039436617746285) {
  err_fun(nom_x, delta_x, out_4680039436617746285);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_6464047771063674000) {
  inv_err_fun(nom_x, true_x, out_6464047771063674000);
}
void car_H_mod_fun(double *state, double *out_915927946953392880) {
  H_mod_fun(state, out_915927946953392880);
}
void car_f_fun(double *state, double dt, double *out_5875377148384648318) {
  f_fun(state,  dt, out_5875377148384648318);
}
void car_F_fun(double *state, double dt, double *out_3741941609747229027) {
  F_fun(state,  dt, out_3741941609747229027);
}
void car_h_25(double *state, double *unused, double *out_5013938002243898062) {
  h_25(state, unused, out_5013938002243898062);
}
void car_H_25(double *state, double *unused, double *out_4811433704179120774) {
  H_25(state, unused, out_4811433704179120774);
}
void car_h_24(double *state, double *unused, double *out_7703538372309607031) {
  h_24(state, unused, out_7703538372309607031);
}
void car_H_24(double *state, double *unused, double *out_2638784105173621208) {
  H_24(state, unused, out_2638784105173621208);
}
void car_h_30(double *state, double *unused, double *out_1376488473989875712) {
  h_30(state, unused, out_1376488473989875712);
}
void car_H_30(double *state, double *unused, double *out_7329766662686369401) {
  H_30(state, unused, out_7329766662686369401);
}
void car_h_26(double *state, double *unused, double *out_7605480698016965053) {
  h_26(state, unused, out_7605480698016965053);
}
void car_H_26(double *state, double *unused, double *out_1069930385305064550) {
  H_26(state, unused, out_1069930385305064550);
}
void car_h_27(double *state, double *unused, double *out_12264734583052417) {
  h_27(state, unused, out_12264734583052417);
}
void car_H_27(double *state, double *unused, double *out_8893383339839238998) {
  H_27(state, unused, out_8893383339839238998);
}
void car_h_29(double *state, double *unused, double *out_3625184793670969933) {
  h_29(state, unused, out_3625184793670969933);
}
void car_H_29(double *state, double *unused, double *out_7839998007000761585) {
  H_29(state, unused, out_7839998007000761585);
}
void car_h_28(double *state, double *unused, double *out_3393257316228255090) {
  h_28(state, unused, out_3393257316228255090);
}
void car_H_28(double *state, double *unused, double *out_2757598989931231011) {
  H_28(state, unused, out_2757598989931231011);
}
void car_h_31(double *state, double *unused, double *out_2446620762004990263) {
  h_31(state, unused, out_2446620762004990263);
}
void car_H_31(double *state, double *unused, double *out_443722283071713074) {
  H_31(state, unused, out_443722283071713074);
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
