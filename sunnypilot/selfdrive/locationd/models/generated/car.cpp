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
void err_fun(double *nom_x, double *delta_x, double *out_5809845421690136483) {
   out_5809845421690136483[0] = delta_x[0] + nom_x[0];
   out_5809845421690136483[1] = delta_x[1] + nom_x[1];
   out_5809845421690136483[2] = delta_x[2] + nom_x[2];
   out_5809845421690136483[3] = delta_x[3] + nom_x[3];
   out_5809845421690136483[4] = delta_x[4] + nom_x[4];
   out_5809845421690136483[5] = delta_x[5] + nom_x[5];
   out_5809845421690136483[6] = delta_x[6] + nom_x[6];
   out_5809845421690136483[7] = delta_x[7] + nom_x[7];
   out_5809845421690136483[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_5502881521170119146) {
   out_5502881521170119146[0] = -nom_x[0] + true_x[0];
   out_5502881521170119146[1] = -nom_x[1] + true_x[1];
   out_5502881521170119146[2] = -nom_x[2] + true_x[2];
   out_5502881521170119146[3] = -nom_x[3] + true_x[3];
   out_5502881521170119146[4] = -nom_x[4] + true_x[4];
   out_5502881521170119146[5] = -nom_x[5] + true_x[5];
   out_5502881521170119146[6] = -nom_x[6] + true_x[6];
   out_5502881521170119146[7] = -nom_x[7] + true_x[7];
   out_5502881521170119146[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_7849538553703122327) {
   out_7849538553703122327[0] = 1.0;
   out_7849538553703122327[1] = 0.0;
   out_7849538553703122327[2] = 0.0;
   out_7849538553703122327[3] = 0.0;
   out_7849538553703122327[4] = 0.0;
   out_7849538553703122327[5] = 0.0;
   out_7849538553703122327[6] = 0.0;
   out_7849538553703122327[7] = 0.0;
   out_7849538553703122327[8] = 0.0;
   out_7849538553703122327[9] = 0.0;
   out_7849538553703122327[10] = 1.0;
   out_7849538553703122327[11] = 0.0;
   out_7849538553703122327[12] = 0.0;
   out_7849538553703122327[13] = 0.0;
   out_7849538553703122327[14] = 0.0;
   out_7849538553703122327[15] = 0.0;
   out_7849538553703122327[16] = 0.0;
   out_7849538553703122327[17] = 0.0;
   out_7849538553703122327[18] = 0.0;
   out_7849538553703122327[19] = 0.0;
   out_7849538553703122327[20] = 1.0;
   out_7849538553703122327[21] = 0.0;
   out_7849538553703122327[22] = 0.0;
   out_7849538553703122327[23] = 0.0;
   out_7849538553703122327[24] = 0.0;
   out_7849538553703122327[25] = 0.0;
   out_7849538553703122327[26] = 0.0;
   out_7849538553703122327[27] = 0.0;
   out_7849538553703122327[28] = 0.0;
   out_7849538553703122327[29] = 0.0;
   out_7849538553703122327[30] = 1.0;
   out_7849538553703122327[31] = 0.0;
   out_7849538553703122327[32] = 0.0;
   out_7849538553703122327[33] = 0.0;
   out_7849538553703122327[34] = 0.0;
   out_7849538553703122327[35] = 0.0;
   out_7849538553703122327[36] = 0.0;
   out_7849538553703122327[37] = 0.0;
   out_7849538553703122327[38] = 0.0;
   out_7849538553703122327[39] = 0.0;
   out_7849538553703122327[40] = 1.0;
   out_7849538553703122327[41] = 0.0;
   out_7849538553703122327[42] = 0.0;
   out_7849538553703122327[43] = 0.0;
   out_7849538553703122327[44] = 0.0;
   out_7849538553703122327[45] = 0.0;
   out_7849538553703122327[46] = 0.0;
   out_7849538553703122327[47] = 0.0;
   out_7849538553703122327[48] = 0.0;
   out_7849538553703122327[49] = 0.0;
   out_7849538553703122327[50] = 1.0;
   out_7849538553703122327[51] = 0.0;
   out_7849538553703122327[52] = 0.0;
   out_7849538553703122327[53] = 0.0;
   out_7849538553703122327[54] = 0.0;
   out_7849538553703122327[55] = 0.0;
   out_7849538553703122327[56] = 0.0;
   out_7849538553703122327[57] = 0.0;
   out_7849538553703122327[58] = 0.0;
   out_7849538553703122327[59] = 0.0;
   out_7849538553703122327[60] = 1.0;
   out_7849538553703122327[61] = 0.0;
   out_7849538553703122327[62] = 0.0;
   out_7849538553703122327[63] = 0.0;
   out_7849538553703122327[64] = 0.0;
   out_7849538553703122327[65] = 0.0;
   out_7849538553703122327[66] = 0.0;
   out_7849538553703122327[67] = 0.0;
   out_7849538553703122327[68] = 0.0;
   out_7849538553703122327[69] = 0.0;
   out_7849538553703122327[70] = 1.0;
   out_7849538553703122327[71] = 0.0;
   out_7849538553703122327[72] = 0.0;
   out_7849538553703122327[73] = 0.0;
   out_7849538553703122327[74] = 0.0;
   out_7849538553703122327[75] = 0.0;
   out_7849538553703122327[76] = 0.0;
   out_7849538553703122327[77] = 0.0;
   out_7849538553703122327[78] = 0.0;
   out_7849538553703122327[79] = 0.0;
   out_7849538553703122327[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_2803371198255290252) {
   out_2803371198255290252[0] = state[0];
   out_2803371198255290252[1] = state[1];
   out_2803371198255290252[2] = state[2];
   out_2803371198255290252[3] = state[3];
   out_2803371198255290252[4] = state[4];
   out_2803371198255290252[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8100000000000005*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_2803371198255290252[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_2803371198255290252[7] = state[7];
   out_2803371198255290252[8] = state[8];
}
void F_fun(double *state, double dt, double *out_3087564586255421604) {
   out_3087564586255421604[0] = 1;
   out_3087564586255421604[1] = 0;
   out_3087564586255421604[2] = 0;
   out_3087564586255421604[3] = 0;
   out_3087564586255421604[4] = 0;
   out_3087564586255421604[5] = 0;
   out_3087564586255421604[6] = 0;
   out_3087564586255421604[7] = 0;
   out_3087564586255421604[8] = 0;
   out_3087564586255421604[9] = 0;
   out_3087564586255421604[10] = 1;
   out_3087564586255421604[11] = 0;
   out_3087564586255421604[12] = 0;
   out_3087564586255421604[13] = 0;
   out_3087564586255421604[14] = 0;
   out_3087564586255421604[15] = 0;
   out_3087564586255421604[16] = 0;
   out_3087564586255421604[17] = 0;
   out_3087564586255421604[18] = 0;
   out_3087564586255421604[19] = 0;
   out_3087564586255421604[20] = 1;
   out_3087564586255421604[21] = 0;
   out_3087564586255421604[22] = 0;
   out_3087564586255421604[23] = 0;
   out_3087564586255421604[24] = 0;
   out_3087564586255421604[25] = 0;
   out_3087564586255421604[26] = 0;
   out_3087564586255421604[27] = 0;
   out_3087564586255421604[28] = 0;
   out_3087564586255421604[29] = 0;
   out_3087564586255421604[30] = 1;
   out_3087564586255421604[31] = 0;
   out_3087564586255421604[32] = 0;
   out_3087564586255421604[33] = 0;
   out_3087564586255421604[34] = 0;
   out_3087564586255421604[35] = 0;
   out_3087564586255421604[36] = 0;
   out_3087564586255421604[37] = 0;
   out_3087564586255421604[38] = 0;
   out_3087564586255421604[39] = 0;
   out_3087564586255421604[40] = 1;
   out_3087564586255421604[41] = 0;
   out_3087564586255421604[42] = 0;
   out_3087564586255421604[43] = 0;
   out_3087564586255421604[44] = 0;
   out_3087564586255421604[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_3087564586255421604[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_3087564586255421604[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_3087564586255421604[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_3087564586255421604[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_3087564586255421604[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_3087564586255421604[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_3087564586255421604[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_3087564586255421604[53] = -9.8100000000000005*dt;
   out_3087564586255421604[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_3087564586255421604[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_3087564586255421604[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_3087564586255421604[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_3087564586255421604[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_3087564586255421604[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_3087564586255421604[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_3087564586255421604[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_3087564586255421604[62] = 0;
   out_3087564586255421604[63] = 0;
   out_3087564586255421604[64] = 0;
   out_3087564586255421604[65] = 0;
   out_3087564586255421604[66] = 0;
   out_3087564586255421604[67] = 0;
   out_3087564586255421604[68] = 0;
   out_3087564586255421604[69] = 0;
   out_3087564586255421604[70] = 1;
   out_3087564586255421604[71] = 0;
   out_3087564586255421604[72] = 0;
   out_3087564586255421604[73] = 0;
   out_3087564586255421604[74] = 0;
   out_3087564586255421604[75] = 0;
   out_3087564586255421604[76] = 0;
   out_3087564586255421604[77] = 0;
   out_3087564586255421604[78] = 0;
   out_3087564586255421604[79] = 0;
   out_3087564586255421604[80] = 1;
}
void h_25(double *state, double *unused, double *out_3664987702156534339) {
   out_3664987702156534339[0] = state[6];
}
void H_25(double *state, double *unused, double *out_1404017294094192052) {
   out_1404017294094192052[0] = 0;
   out_1404017294094192052[1] = 0;
   out_1404017294094192052[2] = 0;
   out_1404017294094192052[3] = 0;
   out_1404017294094192052[4] = 0;
   out_1404017294094192052[5] = 0;
   out_1404017294094192052[6] = 1;
   out_1404017294094192052[7] = 0;
   out_1404017294094192052[8] = 0;
}
void h_24(double *state, double *unused, double *out_8112067670215266046) {
   out_8112067670215266046[0] = state[4];
   out_8112067670215266046[1] = state[5];
}
void H_24(double *state, double *unused, double *out_768632304911307514) {
   out_768632304911307514[0] = 0;
   out_768632304911307514[1] = 0;
   out_768632304911307514[2] = 0;
   out_768632304911307514[3] = 0;
   out_768632304911307514[4] = 1;
   out_768632304911307514[5] = 0;
   out_768632304911307514[6] = 0;
   out_768632304911307514[7] = 0;
   out_768632304911307514[8] = 0;
   out_768632304911307514[9] = 0;
   out_768632304911307514[10] = 0;
   out_768632304911307514[11] = 0;
   out_768632304911307514[12] = 0;
   out_768632304911307514[13] = 0;
   out_768632304911307514[14] = 1;
   out_768632304911307514[15] = 0;
   out_768632304911307514[16] = 0;
   out_768632304911307514[17] = 0;
}
void h_30(double *state, double *unused, double *out_3940181764441040228) {
   out_3940181764441040228[0] = state[4];
}
void H_30(double *state, double *unused, double *out_3922350252601440679) {
   out_3922350252601440679[0] = 0;
   out_3922350252601440679[1] = 0;
   out_3922350252601440679[2] = 0;
   out_3922350252601440679[3] = 0;
   out_3922350252601440679[4] = 1;
   out_3922350252601440679[5] = 0;
   out_3922350252601440679[6] = 0;
   out_3922350252601440679[7] = 0;
   out_3922350252601440679[8] = 0;
}
void h_26(double *state, double *unused, double *out_8748577395274773432) {
   out_8748577395274773432[0] = state[7];
}
void H_26(double *state, double *unused, double *out_2337486024779864172) {
   out_2337486024779864172[0] = 0;
   out_2337486024779864172[1] = 0;
   out_2337486024779864172[2] = 0;
   out_2337486024779864172[3] = 0;
   out_2337486024779864172[4] = 0;
   out_2337486024779864172[5] = 0;
   out_2337486024779864172[6] = 0;
   out_2337486024779864172[7] = 1;
   out_2337486024779864172[8] = 0;
}
void h_27(double *state, double *unused, double *out_8666660969817379984) {
   out_8666660969817379984[0] = state[3];
}
void H_27(double *state, double *unused, double *out_6145944323785383896) {
   out_6145944323785383896[0] = 0;
   out_6145944323785383896[1] = 0;
   out_6145944323785383896[2] = 0;
   out_6145944323785383896[3] = 1;
   out_6145944323785383896[4] = 0;
   out_6145944323785383896[5] = 0;
   out_6145944323785383896[6] = 0;
   out_6145944323785383896[7] = 0;
   out_6145944323785383896[8] = 0;
}
void h_29(double *state, double *unused, double *out_903395712996707543) {
   out_903395712996707543[0] = state[1];
}
void H_29(double *state, double *unused, double *out_4432581596915832863) {
   out_4432581596915832863[0] = 0;
   out_4432581596915832863[1] = 1;
   out_4432581596915832863[2] = 0;
   out_4432581596915832863[3] = 0;
   out_4432581596915832863[4] = 0;
   out_4432581596915832863[5] = 0;
   out_4432581596915832863[6] = 0;
   out_4432581596915832863[7] = 0;
   out_4432581596915832863[8] = 0;
}
void h_28(double *state, double *unused, double *out_2987840130260439853) {
   out_2987840130260439853[0] = state[0];
}
void H_28(double *state, double *unused, double *out_649817420153697711) {
   out_649817420153697711[0] = 1;
   out_649817420153697711[1] = 0;
   out_649817420153697711[2] = 0;
   out_649817420153697711[3] = 0;
   out_649817420153697711[4] = 0;
   out_649817420153697711[5] = 0;
   out_649817420153697711[6] = 0;
   out_649817420153697711[7] = 0;
   out_649817420153697711[8] = 0;
}
void h_31(double *state, double *unused, double *out_7763291000435906203) {
   out_7763291000435906203[0] = state[8];
}
void H_31(double *state, double *unused, double *out_2963694127013215648) {
   out_2963694127013215648[0] = 0;
   out_2963694127013215648[1] = 0;
   out_2963694127013215648[2] = 0;
   out_2963694127013215648[3] = 0;
   out_2963694127013215648[4] = 0;
   out_2963694127013215648[5] = 0;
   out_2963694127013215648[6] = 0;
   out_2963694127013215648[7] = 0;
   out_2963694127013215648[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_5809845421690136483) {
  err_fun(nom_x, delta_x, out_5809845421690136483);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_5502881521170119146) {
  inv_err_fun(nom_x, true_x, out_5502881521170119146);
}
void car_H_mod_fun(double *state, double *out_7849538553703122327) {
  H_mod_fun(state, out_7849538553703122327);
}
void car_f_fun(double *state, double dt, double *out_2803371198255290252) {
  f_fun(state,  dt, out_2803371198255290252);
}
void car_F_fun(double *state, double dt, double *out_3087564586255421604) {
  F_fun(state,  dt, out_3087564586255421604);
}
void car_h_25(double *state, double *unused, double *out_3664987702156534339) {
  h_25(state, unused, out_3664987702156534339);
}
void car_H_25(double *state, double *unused, double *out_1404017294094192052) {
  H_25(state, unused, out_1404017294094192052);
}
void car_h_24(double *state, double *unused, double *out_8112067670215266046) {
  h_24(state, unused, out_8112067670215266046);
}
void car_H_24(double *state, double *unused, double *out_768632304911307514) {
  H_24(state, unused, out_768632304911307514);
}
void car_h_30(double *state, double *unused, double *out_3940181764441040228) {
  h_30(state, unused, out_3940181764441040228);
}
void car_H_30(double *state, double *unused, double *out_3922350252601440679) {
  H_30(state, unused, out_3922350252601440679);
}
void car_h_26(double *state, double *unused, double *out_8748577395274773432) {
  h_26(state, unused, out_8748577395274773432);
}
void car_H_26(double *state, double *unused, double *out_2337486024779864172) {
  H_26(state, unused, out_2337486024779864172);
}
void car_h_27(double *state, double *unused, double *out_8666660969817379984) {
  h_27(state, unused, out_8666660969817379984);
}
void car_H_27(double *state, double *unused, double *out_6145944323785383896) {
  H_27(state, unused, out_6145944323785383896);
}
void car_h_29(double *state, double *unused, double *out_903395712996707543) {
  h_29(state, unused, out_903395712996707543);
}
void car_H_29(double *state, double *unused, double *out_4432581596915832863) {
  H_29(state, unused, out_4432581596915832863);
}
void car_h_28(double *state, double *unused, double *out_2987840130260439853) {
  h_28(state, unused, out_2987840130260439853);
}
void car_H_28(double *state, double *unused, double *out_649817420153697711) {
  H_28(state, unused, out_649817420153697711);
}
void car_h_31(double *state, double *unused, double *out_7763291000435906203) {
  h_31(state, unused, out_7763291000435906203);
}
void car_H_31(double *state, double *unused, double *out_2963694127013215648) {
  H_31(state, unused, out_2963694127013215648);
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
