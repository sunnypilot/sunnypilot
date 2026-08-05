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
void err_fun(double *nom_x, double *delta_x, double *out_1308307769420293042) {
   out_1308307769420293042[0] = delta_x[0] + nom_x[0];
   out_1308307769420293042[1] = delta_x[1] + nom_x[1];
   out_1308307769420293042[2] = delta_x[2] + nom_x[2];
   out_1308307769420293042[3] = delta_x[3] + nom_x[3];
   out_1308307769420293042[4] = delta_x[4] + nom_x[4];
   out_1308307769420293042[5] = delta_x[5] + nom_x[5];
   out_1308307769420293042[6] = delta_x[6] + nom_x[6];
   out_1308307769420293042[7] = delta_x[7] + nom_x[7];
   out_1308307769420293042[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_2556976084631402) {
   out_2556976084631402[0] = -nom_x[0] + true_x[0];
   out_2556976084631402[1] = -nom_x[1] + true_x[1];
   out_2556976084631402[2] = -nom_x[2] + true_x[2];
   out_2556976084631402[3] = -nom_x[3] + true_x[3];
   out_2556976084631402[4] = -nom_x[4] + true_x[4];
   out_2556976084631402[5] = -nom_x[5] + true_x[5];
   out_2556976084631402[6] = -nom_x[6] + true_x[6];
   out_2556976084631402[7] = -nom_x[7] + true_x[7];
   out_2556976084631402[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_6527467579721338563) {
   out_6527467579721338563[0] = 1.0;
   out_6527467579721338563[1] = 0.0;
   out_6527467579721338563[2] = 0.0;
   out_6527467579721338563[3] = 0.0;
   out_6527467579721338563[4] = 0.0;
   out_6527467579721338563[5] = 0.0;
   out_6527467579721338563[6] = 0.0;
   out_6527467579721338563[7] = 0.0;
   out_6527467579721338563[8] = 0.0;
   out_6527467579721338563[9] = 0.0;
   out_6527467579721338563[10] = 1.0;
   out_6527467579721338563[11] = 0.0;
   out_6527467579721338563[12] = 0.0;
   out_6527467579721338563[13] = 0.0;
   out_6527467579721338563[14] = 0.0;
   out_6527467579721338563[15] = 0.0;
   out_6527467579721338563[16] = 0.0;
   out_6527467579721338563[17] = 0.0;
   out_6527467579721338563[18] = 0.0;
   out_6527467579721338563[19] = 0.0;
   out_6527467579721338563[20] = 1.0;
   out_6527467579721338563[21] = 0.0;
   out_6527467579721338563[22] = 0.0;
   out_6527467579721338563[23] = 0.0;
   out_6527467579721338563[24] = 0.0;
   out_6527467579721338563[25] = 0.0;
   out_6527467579721338563[26] = 0.0;
   out_6527467579721338563[27] = 0.0;
   out_6527467579721338563[28] = 0.0;
   out_6527467579721338563[29] = 0.0;
   out_6527467579721338563[30] = 1.0;
   out_6527467579721338563[31] = 0.0;
   out_6527467579721338563[32] = 0.0;
   out_6527467579721338563[33] = 0.0;
   out_6527467579721338563[34] = 0.0;
   out_6527467579721338563[35] = 0.0;
   out_6527467579721338563[36] = 0.0;
   out_6527467579721338563[37] = 0.0;
   out_6527467579721338563[38] = 0.0;
   out_6527467579721338563[39] = 0.0;
   out_6527467579721338563[40] = 1.0;
   out_6527467579721338563[41] = 0.0;
   out_6527467579721338563[42] = 0.0;
   out_6527467579721338563[43] = 0.0;
   out_6527467579721338563[44] = 0.0;
   out_6527467579721338563[45] = 0.0;
   out_6527467579721338563[46] = 0.0;
   out_6527467579721338563[47] = 0.0;
   out_6527467579721338563[48] = 0.0;
   out_6527467579721338563[49] = 0.0;
   out_6527467579721338563[50] = 1.0;
   out_6527467579721338563[51] = 0.0;
   out_6527467579721338563[52] = 0.0;
   out_6527467579721338563[53] = 0.0;
   out_6527467579721338563[54] = 0.0;
   out_6527467579721338563[55] = 0.0;
   out_6527467579721338563[56] = 0.0;
   out_6527467579721338563[57] = 0.0;
   out_6527467579721338563[58] = 0.0;
   out_6527467579721338563[59] = 0.0;
   out_6527467579721338563[60] = 1.0;
   out_6527467579721338563[61] = 0.0;
   out_6527467579721338563[62] = 0.0;
   out_6527467579721338563[63] = 0.0;
   out_6527467579721338563[64] = 0.0;
   out_6527467579721338563[65] = 0.0;
   out_6527467579721338563[66] = 0.0;
   out_6527467579721338563[67] = 0.0;
   out_6527467579721338563[68] = 0.0;
   out_6527467579721338563[69] = 0.0;
   out_6527467579721338563[70] = 1.0;
   out_6527467579721338563[71] = 0.0;
   out_6527467579721338563[72] = 0.0;
   out_6527467579721338563[73] = 0.0;
   out_6527467579721338563[74] = 0.0;
   out_6527467579721338563[75] = 0.0;
   out_6527467579721338563[76] = 0.0;
   out_6527467579721338563[77] = 0.0;
   out_6527467579721338563[78] = 0.0;
   out_6527467579721338563[79] = 0.0;
   out_6527467579721338563[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_46405867141907835) {
   out_46405867141907835[0] = state[0];
   out_46405867141907835[1] = state[1];
   out_46405867141907835[2] = state[2];
   out_46405867141907835[3] = state[3];
   out_46405867141907835[4] = state[4];
   out_46405867141907835[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8100000000000005*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_46405867141907835[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_46405867141907835[7] = state[7];
   out_46405867141907835[8] = state[8];
}
void F_fun(double *state, double dt, double *out_3458223914096858551) {
   out_3458223914096858551[0] = 1;
   out_3458223914096858551[1] = 0;
   out_3458223914096858551[2] = 0;
   out_3458223914096858551[3] = 0;
   out_3458223914096858551[4] = 0;
   out_3458223914096858551[5] = 0;
   out_3458223914096858551[6] = 0;
   out_3458223914096858551[7] = 0;
   out_3458223914096858551[8] = 0;
   out_3458223914096858551[9] = 0;
   out_3458223914096858551[10] = 1;
   out_3458223914096858551[11] = 0;
   out_3458223914096858551[12] = 0;
   out_3458223914096858551[13] = 0;
   out_3458223914096858551[14] = 0;
   out_3458223914096858551[15] = 0;
   out_3458223914096858551[16] = 0;
   out_3458223914096858551[17] = 0;
   out_3458223914096858551[18] = 0;
   out_3458223914096858551[19] = 0;
   out_3458223914096858551[20] = 1;
   out_3458223914096858551[21] = 0;
   out_3458223914096858551[22] = 0;
   out_3458223914096858551[23] = 0;
   out_3458223914096858551[24] = 0;
   out_3458223914096858551[25] = 0;
   out_3458223914096858551[26] = 0;
   out_3458223914096858551[27] = 0;
   out_3458223914096858551[28] = 0;
   out_3458223914096858551[29] = 0;
   out_3458223914096858551[30] = 1;
   out_3458223914096858551[31] = 0;
   out_3458223914096858551[32] = 0;
   out_3458223914096858551[33] = 0;
   out_3458223914096858551[34] = 0;
   out_3458223914096858551[35] = 0;
   out_3458223914096858551[36] = 0;
   out_3458223914096858551[37] = 0;
   out_3458223914096858551[38] = 0;
   out_3458223914096858551[39] = 0;
   out_3458223914096858551[40] = 1;
   out_3458223914096858551[41] = 0;
   out_3458223914096858551[42] = 0;
   out_3458223914096858551[43] = 0;
   out_3458223914096858551[44] = 0;
   out_3458223914096858551[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_3458223914096858551[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_3458223914096858551[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_3458223914096858551[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_3458223914096858551[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_3458223914096858551[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_3458223914096858551[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_3458223914096858551[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_3458223914096858551[53] = -9.8100000000000005*dt;
   out_3458223914096858551[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_3458223914096858551[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_3458223914096858551[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_3458223914096858551[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_3458223914096858551[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_3458223914096858551[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_3458223914096858551[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_3458223914096858551[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_3458223914096858551[62] = 0;
   out_3458223914096858551[63] = 0;
   out_3458223914096858551[64] = 0;
   out_3458223914096858551[65] = 0;
   out_3458223914096858551[66] = 0;
   out_3458223914096858551[67] = 0;
   out_3458223914096858551[68] = 0;
   out_3458223914096858551[69] = 0;
   out_3458223914096858551[70] = 1;
   out_3458223914096858551[71] = 0;
   out_3458223914096858551[72] = 0;
   out_3458223914096858551[73] = 0;
   out_3458223914096858551[74] = 0;
   out_3458223914096858551[75] = 0;
   out_3458223914096858551[76] = 0;
   out_3458223914096858551[77] = 0;
   out_3458223914096858551[78] = 0;
   out_3458223914096858551[79] = 0;
   out_3458223914096858551[80] = 1;
}
void h_25(double *state, double *unused, double *out_5649626404835719527) {
   out_5649626404835719527[0] = state[6];
}
void H_25(double *state, double *unused, double *out_1393870453252521242) {
   out_1393870453252521242[0] = 0;
   out_1393870453252521242[1] = 0;
   out_1393870453252521242[2] = 0;
   out_1393870453252521242[3] = 0;
   out_1393870453252521242[4] = 0;
   out_1393870453252521242[5] = 0;
   out_1393870453252521242[6] = 1;
   out_1393870453252521242[7] = 0;
   out_1393870453252521242[8] = 0;
}
void h_24(double *state, double *unused, double *out_775491211629833659) {
   out_775491211629833659[0] = state[4];
   out_775491211629833659[1] = state[5];
}
void H_24(double *state, double *unused, double *out_778779145752978324) {
   out_778779145752978324[0] = 0;
   out_778779145752978324[1] = 0;
   out_778779145752978324[2] = 0;
   out_778779145752978324[3] = 0;
   out_778779145752978324[4] = 1;
   out_778779145752978324[5] = 0;
   out_778779145752978324[6] = 0;
   out_778779145752978324[7] = 0;
   out_778779145752978324[8] = 0;
   out_778779145752978324[9] = 0;
   out_778779145752978324[10] = 0;
   out_778779145752978324[11] = 0;
   out_778779145752978324[12] = 0;
   out_778779145752978324[13] = 0;
   out_778779145752978324[14] = 1;
   out_778779145752978324[15] = 0;
   out_778779145752978324[16] = 0;
   out_778779145752978324[17] = 0;
}
void h_30(double *state, double *unused, double *out_6641670473033171960) {
   out_6641670473033171960[0] = state[4];
}
void H_30(double *state, double *unused, double *out_3912203411759769869) {
   out_3912203411759769869[0] = 0;
   out_3912203411759769869[1] = 0;
   out_3912203411759769869[2] = 0;
   out_3912203411759769869[3] = 0;
   out_3912203411759769869[4] = 1;
   out_3912203411759769869[5] = 0;
   out_3912203411759769869[6] = 0;
   out_3912203411759769869[7] = 0;
   out_3912203411759769869[8] = 0;
}
void h_26(double *state, double *unused, double *out_7244986357709649477) {
   out_7244986357709649477[0] = state[7];
}
void H_26(double *state, double *unused, double *out_2347632865621534982) {
   out_2347632865621534982[0] = 0;
   out_2347632865621534982[1] = 0;
   out_2347632865621534982[2] = 0;
   out_2347632865621534982[3] = 0;
   out_2347632865621534982[4] = 0;
   out_2347632865621534982[5] = 0;
   out_2347632865621534982[6] = 0;
   out_2347632865621534982[7] = 1;
   out_2347632865621534982[8] = 0;
}
void h_27(double *state, double *unused, double *out_1785517029592981286) {
   out_1785517029592981286[0] = state[3];
}
void H_27(double *state, double *unused, double *out_1737440099959344958) {
   out_1737440099959344958[0] = 0;
   out_1737440099959344958[1] = 0;
   out_1737440099959344958[2] = 0;
   out_1737440099959344958[3] = 1;
   out_1737440099959344958[4] = 0;
   out_1737440099959344958[5] = 0;
   out_1737440099959344958[6] = 0;
   out_1737440099959344958[7] = 0;
   out_1737440099959344958[8] = 0;
}
void h_29(double *state, double *unused, double *out_9200668279867682005) {
   out_9200668279867682005[0] = state[1];
}
void H_29(double *state, double *unused, double *out_4422434756074162053) {
   out_4422434756074162053[0] = 0;
   out_4422434756074162053[1] = 1;
   out_4422434756074162053[2] = 0;
   out_4422434756074162053[3] = 0;
   out_4422434756074162053[4] = 0;
   out_4422434756074162053[5] = 0;
   out_4422434756074162053[6] = 0;
   out_4422434756074162053[7] = 0;
   out_4422434756074162053[8] = 0;
}
void h_28(double *state, double *unused, double *out_2729026882494643721) {
   out_2729026882494643721[0] = state[0];
}
void H_28(double *state, double *unused, double *out_659964260995368521) {
   out_659964260995368521[0] = 1;
   out_659964260995368521[1] = 0;
   out_659964260995368521[2] = 0;
   out_659964260995368521[3] = 0;
   out_659964260995368521[4] = 0;
   out_659964260995368521[5] = 0;
   out_659964260995368521[6] = 0;
   out_659964260995368521[7] = 0;
   out_659964260995368521[8] = 0;
}
void h_31(double *state, double *unused, double *out_6026282442523481153) {
   out_6026282442523481153[0] = state[8];
}
void H_31(double *state, double *unused, double *out_2973840967854886458) {
   out_2973840967854886458[0] = 0;
   out_2973840967854886458[1] = 0;
   out_2973840967854886458[2] = 0;
   out_2973840967854886458[3] = 0;
   out_2973840967854886458[4] = 0;
   out_2973840967854886458[5] = 0;
   out_2973840967854886458[6] = 0;
   out_2973840967854886458[7] = 0;
   out_2973840967854886458[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_1308307769420293042) {
  err_fun(nom_x, delta_x, out_1308307769420293042);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_2556976084631402) {
  inv_err_fun(nom_x, true_x, out_2556976084631402);
}
void car_H_mod_fun(double *state, double *out_6527467579721338563) {
  H_mod_fun(state, out_6527467579721338563);
}
void car_f_fun(double *state, double dt, double *out_46405867141907835) {
  f_fun(state,  dt, out_46405867141907835);
}
void car_F_fun(double *state, double dt, double *out_3458223914096858551) {
  F_fun(state,  dt, out_3458223914096858551);
}
void car_h_25(double *state, double *unused, double *out_5649626404835719527) {
  h_25(state, unused, out_5649626404835719527);
}
void car_H_25(double *state, double *unused, double *out_1393870453252521242) {
  H_25(state, unused, out_1393870453252521242);
}
void car_h_24(double *state, double *unused, double *out_775491211629833659) {
  h_24(state, unused, out_775491211629833659);
}
void car_H_24(double *state, double *unused, double *out_778779145752978324) {
  H_24(state, unused, out_778779145752978324);
}
void car_h_30(double *state, double *unused, double *out_6641670473033171960) {
  h_30(state, unused, out_6641670473033171960);
}
void car_H_30(double *state, double *unused, double *out_3912203411759769869) {
  H_30(state, unused, out_3912203411759769869);
}
void car_h_26(double *state, double *unused, double *out_7244986357709649477) {
  h_26(state, unused, out_7244986357709649477);
}
void car_H_26(double *state, double *unused, double *out_2347632865621534982) {
  H_26(state, unused, out_2347632865621534982);
}
void car_h_27(double *state, double *unused, double *out_1785517029592981286) {
  h_27(state, unused, out_1785517029592981286);
}
void car_H_27(double *state, double *unused, double *out_1737440099959344958) {
  H_27(state, unused, out_1737440099959344958);
}
void car_h_29(double *state, double *unused, double *out_9200668279867682005) {
  h_29(state, unused, out_9200668279867682005);
}
void car_H_29(double *state, double *unused, double *out_4422434756074162053) {
  H_29(state, unused, out_4422434756074162053);
}
void car_h_28(double *state, double *unused, double *out_2729026882494643721) {
  h_28(state, unused, out_2729026882494643721);
}
void car_H_28(double *state, double *unused, double *out_659964260995368521) {
  H_28(state, unused, out_659964260995368521);
}
void car_h_31(double *state, double *unused, double *out_6026282442523481153) {
  h_31(state, unused, out_6026282442523481153);
}
void car_H_31(double *state, double *unused, double *out_2973840967854886458) {
  H_31(state, unused, out_2973840967854886458);
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
