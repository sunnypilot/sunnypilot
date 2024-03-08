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
void err_fun(double *nom_x, double *delta_x, double *out_9097705428546364050) {
   out_9097705428546364050[0] = delta_x[0] + nom_x[0];
   out_9097705428546364050[1] = delta_x[1] + nom_x[1];
   out_9097705428546364050[2] = delta_x[2] + nom_x[2];
   out_9097705428546364050[3] = delta_x[3] + nom_x[3];
   out_9097705428546364050[4] = delta_x[4] + nom_x[4];
   out_9097705428546364050[5] = delta_x[5] + nom_x[5];
   out_9097705428546364050[6] = delta_x[6] + nom_x[6];
   out_9097705428546364050[7] = delta_x[7] + nom_x[7];
   out_9097705428546364050[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_5952769540740002055) {
   out_5952769540740002055[0] = -nom_x[0] + true_x[0];
   out_5952769540740002055[1] = -nom_x[1] + true_x[1];
   out_5952769540740002055[2] = -nom_x[2] + true_x[2];
   out_5952769540740002055[3] = -nom_x[3] + true_x[3];
   out_5952769540740002055[4] = -nom_x[4] + true_x[4];
   out_5952769540740002055[5] = -nom_x[5] + true_x[5];
   out_5952769540740002055[6] = -nom_x[6] + true_x[6];
   out_5952769540740002055[7] = -nom_x[7] + true_x[7];
   out_5952769540740002055[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_1702034534077900134) {
   out_1702034534077900134[0] = 1.0;
   out_1702034534077900134[1] = 0;
   out_1702034534077900134[2] = 0;
   out_1702034534077900134[3] = 0;
   out_1702034534077900134[4] = 0;
   out_1702034534077900134[5] = 0;
   out_1702034534077900134[6] = 0;
   out_1702034534077900134[7] = 0;
   out_1702034534077900134[8] = 0;
   out_1702034534077900134[9] = 0;
   out_1702034534077900134[10] = 1.0;
   out_1702034534077900134[11] = 0;
   out_1702034534077900134[12] = 0;
   out_1702034534077900134[13] = 0;
   out_1702034534077900134[14] = 0;
   out_1702034534077900134[15] = 0;
   out_1702034534077900134[16] = 0;
   out_1702034534077900134[17] = 0;
   out_1702034534077900134[18] = 0;
   out_1702034534077900134[19] = 0;
   out_1702034534077900134[20] = 1.0;
   out_1702034534077900134[21] = 0;
   out_1702034534077900134[22] = 0;
   out_1702034534077900134[23] = 0;
   out_1702034534077900134[24] = 0;
   out_1702034534077900134[25] = 0;
   out_1702034534077900134[26] = 0;
   out_1702034534077900134[27] = 0;
   out_1702034534077900134[28] = 0;
   out_1702034534077900134[29] = 0;
   out_1702034534077900134[30] = 1.0;
   out_1702034534077900134[31] = 0;
   out_1702034534077900134[32] = 0;
   out_1702034534077900134[33] = 0;
   out_1702034534077900134[34] = 0;
   out_1702034534077900134[35] = 0;
   out_1702034534077900134[36] = 0;
   out_1702034534077900134[37] = 0;
   out_1702034534077900134[38] = 0;
   out_1702034534077900134[39] = 0;
   out_1702034534077900134[40] = 1.0;
   out_1702034534077900134[41] = 0;
   out_1702034534077900134[42] = 0;
   out_1702034534077900134[43] = 0;
   out_1702034534077900134[44] = 0;
   out_1702034534077900134[45] = 0;
   out_1702034534077900134[46] = 0;
   out_1702034534077900134[47] = 0;
   out_1702034534077900134[48] = 0;
   out_1702034534077900134[49] = 0;
   out_1702034534077900134[50] = 1.0;
   out_1702034534077900134[51] = 0;
   out_1702034534077900134[52] = 0;
   out_1702034534077900134[53] = 0;
   out_1702034534077900134[54] = 0;
   out_1702034534077900134[55] = 0;
   out_1702034534077900134[56] = 0;
   out_1702034534077900134[57] = 0;
   out_1702034534077900134[58] = 0;
   out_1702034534077900134[59] = 0;
   out_1702034534077900134[60] = 1.0;
   out_1702034534077900134[61] = 0;
   out_1702034534077900134[62] = 0;
   out_1702034534077900134[63] = 0;
   out_1702034534077900134[64] = 0;
   out_1702034534077900134[65] = 0;
   out_1702034534077900134[66] = 0;
   out_1702034534077900134[67] = 0;
   out_1702034534077900134[68] = 0;
   out_1702034534077900134[69] = 0;
   out_1702034534077900134[70] = 1.0;
   out_1702034534077900134[71] = 0;
   out_1702034534077900134[72] = 0;
   out_1702034534077900134[73] = 0;
   out_1702034534077900134[74] = 0;
   out_1702034534077900134[75] = 0;
   out_1702034534077900134[76] = 0;
   out_1702034534077900134[77] = 0;
   out_1702034534077900134[78] = 0;
   out_1702034534077900134[79] = 0;
   out_1702034534077900134[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_3539324188133064767) {
   out_3539324188133064767[0] = state[0];
   out_3539324188133064767[1] = state[1];
   out_3539324188133064767[2] = state[2];
   out_3539324188133064767[3] = state[3];
   out_3539324188133064767[4] = state[4];
   out_3539324188133064767[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8000000000000007*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_3539324188133064767[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_3539324188133064767[7] = state[7];
   out_3539324188133064767[8] = state[8];
}
void F_fun(double *state, double dt, double *out_7450011976583637852) {
   out_7450011976583637852[0] = 1;
   out_7450011976583637852[1] = 0;
   out_7450011976583637852[2] = 0;
   out_7450011976583637852[3] = 0;
   out_7450011976583637852[4] = 0;
   out_7450011976583637852[5] = 0;
   out_7450011976583637852[6] = 0;
   out_7450011976583637852[7] = 0;
   out_7450011976583637852[8] = 0;
   out_7450011976583637852[9] = 0;
   out_7450011976583637852[10] = 1;
   out_7450011976583637852[11] = 0;
   out_7450011976583637852[12] = 0;
   out_7450011976583637852[13] = 0;
   out_7450011976583637852[14] = 0;
   out_7450011976583637852[15] = 0;
   out_7450011976583637852[16] = 0;
   out_7450011976583637852[17] = 0;
   out_7450011976583637852[18] = 0;
   out_7450011976583637852[19] = 0;
   out_7450011976583637852[20] = 1;
   out_7450011976583637852[21] = 0;
   out_7450011976583637852[22] = 0;
   out_7450011976583637852[23] = 0;
   out_7450011976583637852[24] = 0;
   out_7450011976583637852[25] = 0;
   out_7450011976583637852[26] = 0;
   out_7450011976583637852[27] = 0;
   out_7450011976583637852[28] = 0;
   out_7450011976583637852[29] = 0;
   out_7450011976583637852[30] = 1;
   out_7450011976583637852[31] = 0;
   out_7450011976583637852[32] = 0;
   out_7450011976583637852[33] = 0;
   out_7450011976583637852[34] = 0;
   out_7450011976583637852[35] = 0;
   out_7450011976583637852[36] = 0;
   out_7450011976583637852[37] = 0;
   out_7450011976583637852[38] = 0;
   out_7450011976583637852[39] = 0;
   out_7450011976583637852[40] = 1;
   out_7450011976583637852[41] = 0;
   out_7450011976583637852[42] = 0;
   out_7450011976583637852[43] = 0;
   out_7450011976583637852[44] = 0;
   out_7450011976583637852[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_7450011976583637852[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_7450011976583637852[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_7450011976583637852[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_7450011976583637852[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_7450011976583637852[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_7450011976583637852[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_7450011976583637852[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_7450011976583637852[53] = -9.8000000000000007*dt;
   out_7450011976583637852[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_7450011976583637852[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_7450011976583637852[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_7450011976583637852[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_7450011976583637852[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_7450011976583637852[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_7450011976583637852[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_7450011976583637852[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_7450011976583637852[62] = 0;
   out_7450011976583637852[63] = 0;
   out_7450011976583637852[64] = 0;
   out_7450011976583637852[65] = 0;
   out_7450011976583637852[66] = 0;
   out_7450011976583637852[67] = 0;
   out_7450011976583637852[68] = 0;
   out_7450011976583637852[69] = 0;
   out_7450011976583637852[70] = 1;
   out_7450011976583637852[71] = 0;
   out_7450011976583637852[72] = 0;
   out_7450011976583637852[73] = 0;
   out_7450011976583637852[74] = 0;
   out_7450011976583637852[75] = 0;
   out_7450011976583637852[76] = 0;
   out_7450011976583637852[77] = 0;
   out_7450011976583637852[78] = 0;
   out_7450011976583637852[79] = 0;
   out_7450011976583637852[80] = 1;
}
void h_25(double *state, double *unused, double *out_1236988245966960864) {
   out_1236988245966960864[0] = state[6];
}
void H_25(double *state, double *unused, double *out_2734993885933809184) {
   out_2734993885933809184[0] = 0;
   out_2734993885933809184[1] = 0;
   out_2734993885933809184[2] = 0;
   out_2734993885933809184[3] = 0;
   out_2734993885933809184[4] = 0;
   out_2734993885933809184[5] = 0;
   out_2734993885933809184[6] = 1;
   out_2734993885933809184[7] = 0;
   out_2734993885933809184[8] = 0;
}
void h_24(double *state, double *unused, double *out_5670170784642370660) {
   out_5670170784642370660[0] = state[4];
   out_5670170784642370660[1] = state[5];
}
void H_24(double *state, double *unused, double *out_2011515441032699850) {
   out_2011515441032699850[0] = 0;
   out_2011515441032699850[1] = 0;
   out_2011515441032699850[2] = 0;
   out_2011515441032699850[3] = 0;
   out_2011515441032699850[4] = 1;
   out_2011515441032699850[5] = 0;
   out_2011515441032699850[6] = 0;
   out_2011515441032699850[7] = 0;
   out_2011515441032699850[8] = 0;
   out_2011515441032699850[9] = 0;
   out_2011515441032699850[10] = 0;
   out_2011515441032699850[11] = 0;
   out_2011515441032699850[12] = 0;
   out_2011515441032699850[13] = 0;
   out_2011515441032699850[14] = 1;
   out_2011515441032699850[15] = 0;
   out_2011515441032699850[16] = 0;
   out_2011515441032699850[17] = 0;
}
void h_30(double *state, double *unused, double *out_1135489597399021944) {
   out_1135489597399021944[0] = state[4];
}
void H_30(double *state, double *unused, double *out_5253326844441057811) {
   out_5253326844441057811[0] = 0;
   out_5253326844441057811[1] = 0;
   out_5253326844441057811[2] = 0;
   out_5253326844441057811[3] = 0;
   out_5253326844441057811[4] = 1;
   out_5253326844441057811[5] = 0;
   out_5253326844441057811[6] = 0;
   out_5253326844441057811[7] = 0;
   out_5253326844441057811[8] = 0;
}
void h_26(double *state, double *unused, double *out_6137162865059867589) {
   out_6137162865059867589[0] = state[7];
}
void H_26(double *state, double *unused, double *out_1006509432940247040) {
   out_1006509432940247040[0] = 0;
   out_1006509432940247040[1] = 0;
   out_1006509432940247040[2] = 0;
   out_1006509432940247040[3] = 0;
   out_1006509432940247040[4] = 0;
   out_1006509432940247040[5] = 0;
   out_1006509432940247040[6] = 0;
   out_1006509432940247040[7] = 1;
   out_1006509432940247040[8] = 0;
}
void h_27(double *state, double *unused, double *out_6238661513627806509) {
   out_6238661513627806509[0] = state[3];
}
void H_27(double *state, double *unused, double *out_7476920915625001028) {
   out_7476920915625001028[0] = 0;
   out_7476920915625001028[1] = 0;
   out_7476920915625001028[2] = 0;
   out_7476920915625001028[3] = 1;
   out_7476920915625001028[4] = 0;
   out_7476920915625001028[5] = 0;
   out_7476920915625001028[6] = 0;
   out_7476920915625001028[7] = 0;
   out_7476920915625001028[8] = 0;
}
void h_29(double *state, double *unused, double *out_8570633031827722757) {
   out_8570633031827722757[0] = state[1];
}
void H_29(double *state, double *unused, double *out_5763558188755449995) {
   out_5763558188755449995[0] = 0;
   out_5763558188755449995[1] = 1;
   out_5763558188755449995[2] = 0;
   out_5763558188755449995[3] = 0;
   out_5763558188755449995[4] = 0;
   out_5763558188755449995[5] = 0;
   out_5763558188755449995[6] = 0;
   out_5763558188755449995[7] = 0;
   out_5763558188755449995[8] = 0;
}
void h_28(double *state, double *unused, double *out_5295151660726144074) {
   out_5295151660726144074[0] = state[0];
}
void H_28(double *state, double *unused, double *out_681159171685919421) {
   out_681159171685919421[0] = 1;
   out_681159171685919421[1] = 0;
   out_681159171685919421[2] = 0;
   out_681159171685919421[3] = 0;
   out_681159171685919421[4] = 0;
   out_681159171685919421[5] = 0;
   out_681159171685919421[6] = 0;
   out_681159171685919421[7] = 0;
   out_681159171685919421[8] = 0;
}
void h_31(double *state, double *unused, double *out_4918458949873699265) {
   out_4918458949873699265[0] = state[8];
}
void H_31(double *state, double *unused, double *out_2765639847810769612) {
   out_2765639847810769612[0] = 0;
   out_2765639847810769612[1] = 0;
   out_2765639847810769612[2] = 0;
   out_2765639847810769612[3] = 0;
   out_2765639847810769612[4] = 0;
   out_2765639847810769612[5] = 0;
   out_2765639847810769612[6] = 0;
   out_2765639847810769612[7] = 0;
   out_2765639847810769612[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_9097705428546364050) {
  err_fun(nom_x, delta_x, out_9097705428546364050);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_5952769540740002055) {
  inv_err_fun(nom_x, true_x, out_5952769540740002055);
}
void car_H_mod_fun(double *state, double *out_1702034534077900134) {
  H_mod_fun(state, out_1702034534077900134);
}
void car_f_fun(double *state, double dt, double *out_3539324188133064767) {
  f_fun(state,  dt, out_3539324188133064767);
}
void car_F_fun(double *state, double dt, double *out_7450011976583637852) {
  F_fun(state,  dt, out_7450011976583637852);
}
void car_h_25(double *state, double *unused, double *out_1236988245966960864) {
  h_25(state, unused, out_1236988245966960864);
}
void car_H_25(double *state, double *unused, double *out_2734993885933809184) {
  H_25(state, unused, out_2734993885933809184);
}
void car_h_24(double *state, double *unused, double *out_5670170784642370660) {
  h_24(state, unused, out_5670170784642370660);
}
void car_H_24(double *state, double *unused, double *out_2011515441032699850) {
  H_24(state, unused, out_2011515441032699850);
}
void car_h_30(double *state, double *unused, double *out_1135489597399021944) {
  h_30(state, unused, out_1135489597399021944);
}
void car_H_30(double *state, double *unused, double *out_5253326844441057811) {
  H_30(state, unused, out_5253326844441057811);
}
void car_h_26(double *state, double *unused, double *out_6137162865059867589) {
  h_26(state, unused, out_6137162865059867589);
}
void car_H_26(double *state, double *unused, double *out_1006509432940247040) {
  H_26(state, unused, out_1006509432940247040);
}
void car_h_27(double *state, double *unused, double *out_6238661513627806509) {
  h_27(state, unused, out_6238661513627806509);
}
void car_H_27(double *state, double *unused, double *out_7476920915625001028) {
  H_27(state, unused, out_7476920915625001028);
}
void car_h_29(double *state, double *unused, double *out_8570633031827722757) {
  h_29(state, unused, out_8570633031827722757);
}
void car_H_29(double *state, double *unused, double *out_5763558188755449995) {
  H_29(state, unused, out_5763558188755449995);
}
void car_h_28(double *state, double *unused, double *out_5295151660726144074) {
  h_28(state, unused, out_5295151660726144074);
}
void car_H_28(double *state, double *unused, double *out_681159171685919421) {
  H_28(state, unused, out_681159171685919421);
}
void car_h_31(double *state, double *unused, double *out_4918458949873699265) {
  h_31(state, unused, out_4918458949873699265);
}
void car_H_31(double *state, double *unused, double *out_2765639847810769612) {
  H_31(state, unused, out_2765639847810769612);
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
