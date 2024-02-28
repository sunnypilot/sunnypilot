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
void err_fun(double *nom_x, double *delta_x, double *out_9217969317605642867) {
   out_9217969317605642867[0] = delta_x[0] + nom_x[0];
   out_9217969317605642867[1] = delta_x[1] + nom_x[1];
   out_9217969317605642867[2] = delta_x[2] + nom_x[2];
   out_9217969317605642867[3] = delta_x[3] + nom_x[3];
   out_9217969317605642867[4] = delta_x[4] + nom_x[4];
   out_9217969317605642867[5] = delta_x[5] + nom_x[5];
   out_9217969317605642867[6] = delta_x[6] + nom_x[6];
   out_9217969317605642867[7] = delta_x[7] + nom_x[7];
   out_9217969317605642867[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_6393584235681603618) {
   out_6393584235681603618[0] = -nom_x[0] + true_x[0];
   out_6393584235681603618[1] = -nom_x[1] + true_x[1];
   out_6393584235681603618[2] = -nom_x[2] + true_x[2];
   out_6393584235681603618[3] = -nom_x[3] + true_x[3];
   out_6393584235681603618[4] = -nom_x[4] + true_x[4];
   out_6393584235681603618[5] = -nom_x[5] + true_x[5];
   out_6393584235681603618[6] = -nom_x[6] + true_x[6];
   out_6393584235681603618[7] = -nom_x[7] + true_x[7];
   out_6393584235681603618[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_8159470262941037049) {
   out_8159470262941037049[0] = 1.0;
   out_8159470262941037049[1] = 0;
   out_8159470262941037049[2] = 0;
   out_8159470262941037049[3] = 0;
   out_8159470262941037049[4] = 0;
   out_8159470262941037049[5] = 0;
   out_8159470262941037049[6] = 0;
   out_8159470262941037049[7] = 0;
   out_8159470262941037049[8] = 0;
   out_8159470262941037049[9] = 0;
   out_8159470262941037049[10] = 1.0;
   out_8159470262941037049[11] = 0;
   out_8159470262941037049[12] = 0;
   out_8159470262941037049[13] = 0;
   out_8159470262941037049[14] = 0;
   out_8159470262941037049[15] = 0;
   out_8159470262941037049[16] = 0;
   out_8159470262941037049[17] = 0;
   out_8159470262941037049[18] = 0;
   out_8159470262941037049[19] = 0;
   out_8159470262941037049[20] = 1.0;
   out_8159470262941037049[21] = 0;
   out_8159470262941037049[22] = 0;
   out_8159470262941037049[23] = 0;
   out_8159470262941037049[24] = 0;
   out_8159470262941037049[25] = 0;
   out_8159470262941037049[26] = 0;
   out_8159470262941037049[27] = 0;
   out_8159470262941037049[28] = 0;
   out_8159470262941037049[29] = 0;
   out_8159470262941037049[30] = 1.0;
   out_8159470262941037049[31] = 0;
   out_8159470262941037049[32] = 0;
   out_8159470262941037049[33] = 0;
   out_8159470262941037049[34] = 0;
   out_8159470262941037049[35] = 0;
   out_8159470262941037049[36] = 0;
   out_8159470262941037049[37] = 0;
   out_8159470262941037049[38] = 0;
   out_8159470262941037049[39] = 0;
   out_8159470262941037049[40] = 1.0;
   out_8159470262941037049[41] = 0;
   out_8159470262941037049[42] = 0;
   out_8159470262941037049[43] = 0;
   out_8159470262941037049[44] = 0;
   out_8159470262941037049[45] = 0;
   out_8159470262941037049[46] = 0;
   out_8159470262941037049[47] = 0;
   out_8159470262941037049[48] = 0;
   out_8159470262941037049[49] = 0;
   out_8159470262941037049[50] = 1.0;
   out_8159470262941037049[51] = 0;
   out_8159470262941037049[52] = 0;
   out_8159470262941037049[53] = 0;
   out_8159470262941037049[54] = 0;
   out_8159470262941037049[55] = 0;
   out_8159470262941037049[56] = 0;
   out_8159470262941037049[57] = 0;
   out_8159470262941037049[58] = 0;
   out_8159470262941037049[59] = 0;
   out_8159470262941037049[60] = 1.0;
   out_8159470262941037049[61] = 0;
   out_8159470262941037049[62] = 0;
   out_8159470262941037049[63] = 0;
   out_8159470262941037049[64] = 0;
   out_8159470262941037049[65] = 0;
   out_8159470262941037049[66] = 0;
   out_8159470262941037049[67] = 0;
   out_8159470262941037049[68] = 0;
   out_8159470262941037049[69] = 0;
   out_8159470262941037049[70] = 1.0;
   out_8159470262941037049[71] = 0;
   out_8159470262941037049[72] = 0;
   out_8159470262941037049[73] = 0;
   out_8159470262941037049[74] = 0;
   out_8159470262941037049[75] = 0;
   out_8159470262941037049[76] = 0;
   out_8159470262941037049[77] = 0;
   out_8159470262941037049[78] = 0;
   out_8159470262941037049[79] = 0;
   out_8159470262941037049[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_5395246748545447116) {
   out_5395246748545447116[0] = state[0];
   out_5395246748545447116[1] = state[1];
   out_5395246748545447116[2] = state[2];
   out_5395246748545447116[3] = state[3];
   out_5395246748545447116[4] = state[4];
   out_5395246748545447116[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8000000000000007*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_5395246748545447116[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_5395246748545447116[7] = state[7];
   out_5395246748545447116[8] = state[8];
}
void F_fun(double *state, double dt, double *out_7501393170954007307) {
   out_7501393170954007307[0] = 1;
   out_7501393170954007307[1] = 0;
   out_7501393170954007307[2] = 0;
   out_7501393170954007307[3] = 0;
   out_7501393170954007307[4] = 0;
   out_7501393170954007307[5] = 0;
   out_7501393170954007307[6] = 0;
   out_7501393170954007307[7] = 0;
   out_7501393170954007307[8] = 0;
   out_7501393170954007307[9] = 0;
   out_7501393170954007307[10] = 1;
   out_7501393170954007307[11] = 0;
   out_7501393170954007307[12] = 0;
   out_7501393170954007307[13] = 0;
   out_7501393170954007307[14] = 0;
   out_7501393170954007307[15] = 0;
   out_7501393170954007307[16] = 0;
   out_7501393170954007307[17] = 0;
   out_7501393170954007307[18] = 0;
   out_7501393170954007307[19] = 0;
   out_7501393170954007307[20] = 1;
   out_7501393170954007307[21] = 0;
   out_7501393170954007307[22] = 0;
   out_7501393170954007307[23] = 0;
   out_7501393170954007307[24] = 0;
   out_7501393170954007307[25] = 0;
   out_7501393170954007307[26] = 0;
   out_7501393170954007307[27] = 0;
   out_7501393170954007307[28] = 0;
   out_7501393170954007307[29] = 0;
   out_7501393170954007307[30] = 1;
   out_7501393170954007307[31] = 0;
   out_7501393170954007307[32] = 0;
   out_7501393170954007307[33] = 0;
   out_7501393170954007307[34] = 0;
   out_7501393170954007307[35] = 0;
   out_7501393170954007307[36] = 0;
   out_7501393170954007307[37] = 0;
   out_7501393170954007307[38] = 0;
   out_7501393170954007307[39] = 0;
   out_7501393170954007307[40] = 1;
   out_7501393170954007307[41] = 0;
   out_7501393170954007307[42] = 0;
   out_7501393170954007307[43] = 0;
   out_7501393170954007307[44] = 0;
   out_7501393170954007307[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_7501393170954007307[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_7501393170954007307[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_7501393170954007307[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_7501393170954007307[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_7501393170954007307[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_7501393170954007307[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_7501393170954007307[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_7501393170954007307[53] = -9.8000000000000007*dt;
   out_7501393170954007307[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_7501393170954007307[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_7501393170954007307[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_7501393170954007307[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_7501393170954007307[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_7501393170954007307[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_7501393170954007307[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_7501393170954007307[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_7501393170954007307[62] = 0;
   out_7501393170954007307[63] = 0;
   out_7501393170954007307[64] = 0;
   out_7501393170954007307[65] = 0;
   out_7501393170954007307[66] = 0;
   out_7501393170954007307[67] = 0;
   out_7501393170954007307[68] = 0;
   out_7501393170954007307[69] = 0;
   out_7501393170954007307[70] = 1;
   out_7501393170954007307[71] = 0;
   out_7501393170954007307[72] = 0;
   out_7501393170954007307[73] = 0;
   out_7501393170954007307[74] = 0;
   out_7501393170954007307[75] = 0;
   out_7501393170954007307[76] = 0;
   out_7501393170954007307[77] = 0;
   out_7501393170954007307[78] = 0;
   out_7501393170954007307[79] = 0;
   out_7501393170954007307[80] = 1;
}
void h_25(double *state, double *unused, double *out_3212620688693559532) {
   out_3212620688693559532[0] = state[6];
}
void H_25(double *state, double *unused, double *out_3368569190577985703) {
   out_3368569190577985703[0] = 0;
   out_3368569190577985703[1] = 0;
   out_3368569190577985703[2] = 0;
   out_3368569190577985703[3] = 0;
   out_3368569190577985703[4] = 0;
   out_3368569190577985703[5] = 0;
   out_3368569190577985703[6] = 1;
   out_3368569190577985703[7] = 0;
   out_3368569190577985703[8] = 0;
}
void h_24(double *state, double *unused, double *out_8983580996630113210) {
   out_8983580996630113210[0] = state[4];
   out_8983580996630113210[1] = state[5];
}
void H_24(double *state, double *unused, double *out_1195919591572486137) {
   out_1195919591572486137[0] = 0;
   out_1195919591572486137[1] = 0;
   out_1195919591572486137[2] = 0;
   out_1195919591572486137[3] = 0;
   out_1195919591572486137[4] = 1;
   out_1195919591572486137[5] = 0;
   out_1195919591572486137[6] = 0;
   out_1195919591572486137[7] = 0;
   out_1195919591572486137[8] = 0;
   out_1195919591572486137[9] = 0;
   out_1195919591572486137[10] = 0;
   out_1195919591572486137[11] = 0;
   out_1195919591572486137[12] = 0;
   out_1195919591572486137[13] = 0;
   out_1195919591572486137[14] = 1;
   out_1195919591572486137[15] = 0;
   out_1195919591572486137[16] = 0;
   out_1195919591572486137[17] = 0;
}
void h_30(double *state, double *unused, double *out_5781578470390223898) {
   out_5781578470390223898[0] = state[4];
}
void H_30(double *state, double *unused, double *out_5886902149085234330) {
   out_5886902149085234330[0] = 0;
   out_5886902149085234330[1] = 0;
   out_5886902149085234330[2] = 0;
   out_5886902149085234330[3] = 0;
   out_5886902149085234330[4] = 1;
   out_5886902149085234330[5] = 0;
   out_5886902149085234330[6] = 0;
   out_5886902149085234330[7] = 0;
   out_5886902149085234330[8] = 0;
}
void h_26(double *state, double *unused, double *out_5676102393679055679) {
   out_5676102393679055679[0] = state[7];
}
void H_26(double *state, double *unused, double *out_372934128296070521) {
   out_372934128296070521[0] = 0;
   out_372934128296070521[1] = 0;
   out_372934128296070521[2] = 0;
   out_372934128296070521[3] = 0;
   out_372934128296070521[4] = 0;
   out_372934128296070521[5] = 0;
   out_372934128296070521[6] = 0;
   out_372934128296070521[7] = 1;
   out_372934128296070521[8] = 0;
}
void h_27(double *state, double *unused, double *out_5060714363169364872) {
   out_5060714363169364872[0] = state[3];
}
void H_27(double *state, double *unused, double *out_3712138837284809419) {
   out_3712138837284809419[0] = 0;
   out_3712138837284809419[1] = 0;
   out_3712138837284809419[2] = 0;
   out_3712138837284809419[3] = 1;
   out_3712138837284809419[4] = 0;
   out_3712138837284809419[5] = 0;
   out_3712138837284809419[6] = 0;
   out_3712138837284809419[7] = 0;
   out_3712138837284809419[8] = 0;
}
void h_29(double *state, double *unused, double *out_3947328683450635392) {
   out_3947328683450635392[0] = state[1];
}
void H_29(double *state, double *unused, double *out_6397133493399626514) {
   out_6397133493399626514[0] = 0;
   out_6397133493399626514[1] = 1;
   out_6397133493399626514[2] = 0;
   out_6397133493399626514[3] = 0;
   out_6397133493399626514[4] = 0;
   out_6397133493399626514[5] = 0;
   out_6397133493399626514[6] = 0;
   out_6397133493399626514[7] = 0;
   out_6397133493399626514[8] = 0;
}
void h_28(double *state, double *unused, double *out_779150521925704364) {
   out_779150521925704364[0] = state[0];
}
void H_28(double *state, double *unused, double *out_1314734476330095940) {
   out_1314734476330095940[0] = 1;
   out_1314734476330095940[1] = 0;
   out_1314734476330095940[2] = 0;
   out_1314734476330095940[3] = 0;
   out_1314734476330095940[4] = 0;
   out_1314734476330095940[5] = 0;
   out_1314734476330095940[6] = 0;
   out_1314734476330095940[7] = 0;
   out_1314734476330095940[8] = 0;
}
void h_31(double *state, double *unused, double *out_3802642380919982425) {
   out_3802642380919982425[0] = state[8];
}
void H_31(double *state, double *unused, double *out_999142230529421997) {
   out_999142230529421997[0] = 0;
   out_999142230529421997[1] = 0;
   out_999142230529421997[2] = 0;
   out_999142230529421997[3] = 0;
   out_999142230529421997[4] = 0;
   out_999142230529421997[5] = 0;
   out_999142230529421997[6] = 0;
   out_999142230529421997[7] = 0;
   out_999142230529421997[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_9217969317605642867) {
  err_fun(nom_x, delta_x, out_9217969317605642867);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_6393584235681603618) {
  inv_err_fun(nom_x, true_x, out_6393584235681603618);
}
void car_H_mod_fun(double *state, double *out_8159470262941037049) {
  H_mod_fun(state, out_8159470262941037049);
}
void car_f_fun(double *state, double dt, double *out_5395246748545447116) {
  f_fun(state,  dt, out_5395246748545447116);
}
void car_F_fun(double *state, double dt, double *out_7501393170954007307) {
  F_fun(state,  dt, out_7501393170954007307);
}
void car_h_25(double *state, double *unused, double *out_3212620688693559532) {
  h_25(state, unused, out_3212620688693559532);
}
void car_H_25(double *state, double *unused, double *out_3368569190577985703) {
  H_25(state, unused, out_3368569190577985703);
}
void car_h_24(double *state, double *unused, double *out_8983580996630113210) {
  h_24(state, unused, out_8983580996630113210);
}
void car_H_24(double *state, double *unused, double *out_1195919591572486137) {
  H_24(state, unused, out_1195919591572486137);
}
void car_h_30(double *state, double *unused, double *out_5781578470390223898) {
  h_30(state, unused, out_5781578470390223898);
}
void car_H_30(double *state, double *unused, double *out_5886902149085234330) {
  H_30(state, unused, out_5886902149085234330);
}
void car_h_26(double *state, double *unused, double *out_5676102393679055679) {
  h_26(state, unused, out_5676102393679055679);
}
void car_H_26(double *state, double *unused, double *out_372934128296070521) {
  H_26(state, unused, out_372934128296070521);
}
void car_h_27(double *state, double *unused, double *out_5060714363169364872) {
  h_27(state, unused, out_5060714363169364872);
}
void car_H_27(double *state, double *unused, double *out_3712138837284809419) {
  H_27(state, unused, out_3712138837284809419);
}
void car_h_29(double *state, double *unused, double *out_3947328683450635392) {
  h_29(state, unused, out_3947328683450635392);
}
void car_H_29(double *state, double *unused, double *out_6397133493399626514) {
  H_29(state, unused, out_6397133493399626514);
}
void car_h_28(double *state, double *unused, double *out_779150521925704364) {
  h_28(state, unused, out_779150521925704364);
}
void car_H_28(double *state, double *unused, double *out_1314734476330095940) {
  H_28(state, unused, out_1314734476330095940);
}
void car_h_31(double *state, double *unused, double *out_3802642380919982425) {
  h_31(state, unused, out_3802642380919982425);
}
void car_H_31(double *state, double *unused, double *out_999142230529421997) {
  H_31(state, unused, out_999142230529421997);
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
