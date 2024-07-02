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
void err_fun(double *nom_x, double *delta_x, double *out_5388524865571385571) {
   out_5388524865571385571[0] = delta_x[0] + nom_x[0];
   out_5388524865571385571[1] = delta_x[1] + nom_x[1];
   out_5388524865571385571[2] = delta_x[2] + nom_x[2];
   out_5388524865571385571[3] = delta_x[3] + nom_x[3];
   out_5388524865571385571[4] = delta_x[4] + nom_x[4];
   out_5388524865571385571[5] = delta_x[5] + nom_x[5];
   out_5388524865571385571[6] = delta_x[6] + nom_x[6];
   out_5388524865571385571[7] = delta_x[7] + nom_x[7];
   out_5388524865571385571[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_7040447560413333839) {
   out_7040447560413333839[0] = -nom_x[0] + true_x[0];
   out_7040447560413333839[1] = -nom_x[1] + true_x[1];
   out_7040447560413333839[2] = -nom_x[2] + true_x[2];
   out_7040447560413333839[3] = -nom_x[3] + true_x[3];
   out_7040447560413333839[4] = -nom_x[4] + true_x[4];
   out_7040447560413333839[5] = -nom_x[5] + true_x[5];
   out_7040447560413333839[6] = -nom_x[6] + true_x[6];
   out_7040447560413333839[7] = -nom_x[7] + true_x[7];
   out_7040447560413333839[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_2980610617701040674) {
   out_2980610617701040674[0] = 1.0;
   out_2980610617701040674[1] = 0;
   out_2980610617701040674[2] = 0;
   out_2980610617701040674[3] = 0;
   out_2980610617701040674[4] = 0;
   out_2980610617701040674[5] = 0;
   out_2980610617701040674[6] = 0;
   out_2980610617701040674[7] = 0;
   out_2980610617701040674[8] = 0;
   out_2980610617701040674[9] = 0;
   out_2980610617701040674[10] = 1.0;
   out_2980610617701040674[11] = 0;
   out_2980610617701040674[12] = 0;
   out_2980610617701040674[13] = 0;
   out_2980610617701040674[14] = 0;
   out_2980610617701040674[15] = 0;
   out_2980610617701040674[16] = 0;
   out_2980610617701040674[17] = 0;
   out_2980610617701040674[18] = 0;
   out_2980610617701040674[19] = 0;
   out_2980610617701040674[20] = 1.0;
   out_2980610617701040674[21] = 0;
   out_2980610617701040674[22] = 0;
   out_2980610617701040674[23] = 0;
   out_2980610617701040674[24] = 0;
   out_2980610617701040674[25] = 0;
   out_2980610617701040674[26] = 0;
   out_2980610617701040674[27] = 0;
   out_2980610617701040674[28] = 0;
   out_2980610617701040674[29] = 0;
   out_2980610617701040674[30] = 1.0;
   out_2980610617701040674[31] = 0;
   out_2980610617701040674[32] = 0;
   out_2980610617701040674[33] = 0;
   out_2980610617701040674[34] = 0;
   out_2980610617701040674[35] = 0;
   out_2980610617701040674[36] = 0;
   out_2980610617701040674[37] = 0;
   out_2980610617701040674[38] = 0;
   out_2980610617701040674[39] = 0;
   out_2980610617701040674[40] = 1.0;
   out_2980610617701040674[41] = 0;
   out_2980610617701040674[42] = 0;
   out_2980610617701040674[43] = 0;
   out_2980610617701040674[44] = 0;
   out_2980610617701040674[45] = 0;
   out_2980610617701040674[46] = 0;
   out_2980610617701040674[47] = 0;
   out_2980610617701040674[48] = 0;
   out_2980610617701040674[49] = 0;
   out_2980610617701040674[50] = 1.0;
   out_2980610617701040674[51] = 0;
   out_2980610617701040674[52] = 0;
   out_2980610617701040674[53] = 0;
   out_2980610617701040674[54] = 0;
   out_2980610617701040674[55] = 0;
   out_2980610617701040674[56] = 0;
   out_2980610617701040674[57] = 0;
   out_2980610617701040674[58] = 0;
   out_2980610617701040674[59] = 0;
   out_2980610617701040674[60] = 1.0;
   out_2980610617701040674[61] = 0;
   out_2980610617701040674[62] = 0;
   out_2980610617701040674[63] = 0;
   out_2980610617701040674[64] = 0;
   out_2980610617701040674[65] = 0;
   out_2980610617701040674[66] = 0;
   out_2980610617701040674[67] = 0;
   out_2980610617701040674[68] = 0;
   out_2980610617701040674[69] = 0;
   out_2980610617701040674[70] = 1.0;
   out_2980610617701040674[71] = 0;
   out_2980610617701040674[72] = 0;
   out_2980610617701040674[73] = 0;
   out_2980610617701040674[74] = 0;
   out_2980610617701040674[75] = 0;
   out_2980610617701040674[76] = 0;
   out_2980610617701040674[77] = 0;
   out_2980610617701040674[78] = 0;
   out_2980610617701040674[79] = 0;
   out_2980610617701040674[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_2068294276185711975) {
   out_2068294276185711975[0] = state[0];
   out_2068294276185711975[1] = state[1];
   out_2068294276185711975[2] = state[2];
   out_2068294276185711975[3] = state[3];
   out_2068294276185711975[4] = state[4];
   out_2068294276185711975[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8000000000000007*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_2068294276185711975[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_2068294276185711975[7] = state[7];
   out_2068294276185711975[8] = state[8];
}
void F_fun(double *state, double dt, double *out_2484699426223934627) {
   out_2484699426223934627[0] = 1;
   out_2484699426223934627[1] = 0;
   out_2484699426223934627[2] = 0;
   out_2484699426223934627[3] = 0;
   out_2484699426223934627[4] = 0;
   out_2484699426223934627[5] = 0;
   out_2484699426223934627[6] = 0;
   out_2484699426223934627[7] = 0;
   out_2484699426223934627[8] = 0;
   out_2484699426223934627[9] = 0;
   out_2484699426223934627[10] = 1;
   out_2484699426223934627[11] = 0;
   out_2484699426223934627[12] = 0;
   out_2484699426223934627[13] = 0;
   out_2484699426223934627[14] = 0;
   out_2484699426223934627[15] = 0;
   out_2484699426223934627[16] = 0;
   out_2484699426223934627[17] = 0;
   out_2484699426223934627[18] = 0;
   out_2484699426223934627[19] = 0;
   out_2484699426223934627[20] = 1;
   out_2484699426223934627[21] = 0;
   out_2484699426223934627[22] = 0;
   out_2484699426223934627[23] = 0;
   out_2484699426223934627[24] = 0;
   out_2484699426223934627[25] = 0;
   out_2484699426223934627[26] = 0;
   out_2484699426223934627[27] = 0;
   out_2484699426223934627[28] = 0;
   out_2484699426223934627[29] = 0;
   out_2484699426223934627[30] = 1;
   out_2484699426223934627[31] = 0;
   out_2484699426223934627[32] = 0;
   out_2484699426223934627[33] = 0;
   out_2484699426223934627[34] = 0;
   out_2484699426223934627[35] = 0;
   out_2484699426223934627[36] = 0;
   out_2484699426223934627[37] = 0;
   out_2484699426223934627[38] = 0;
   out_2484699426223934627[39] = 0;
   out_2484699426223934627[40] = 1;
   out_2484699426223934627[41] = 0;
   out_2484699426223934627[42] = 0;
   out_2484699426223934627[43] = 0;
   out_2484699426223934627[44] = 0;
   out_2484699426223934627[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_2484699426223934627[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_2484699426223934627[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_2484699426223934627[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_2484699426223934627[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_2484699426223934627[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_2484699426223934627[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_2484699426223934627[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_2484699426223934627[53] = -9.8000000000000007*dt;
   out_2484699426223934627[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_2484699426223934627[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_2484699426223934627[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_2484699426223934627[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_2484699426223934627[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_2484699426223934627[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_2484699426223934627[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_2484699426223934627[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_2484699426223934627[62] = 0;
   out_2484699426223934627[63] = 0;
   out_2484699426223934627[64] = 0;
   out_2484699426223934627[65] = 0;
   out_2484699426223934627[66] = 0;
   out_2484699426223934627[67] = 0;
   out_2484699426223934627[68] = 0;
   out_2484699426223934627[69] = 0;
   out_2484699426223934627[70] = 1;
   out_2484699426223934627[71] = 0;
   out_2484699426223934627[72] = 0;
   out_2484699426223934627[73] = 0;
   out_2484699426223934627[74] = 0;
   out_2484699426223934627[75] = 0;
   out_2484699426223934627[76] = 0;
   out_2484699426223934627[77] = 0;
   out_2484699426223934627[78] = 0;
   out_2484699426223934627[79] = 0;
   out_2484699426223934627[80] = 1;
}
void h_25(double *state, double *unused, double *out_9047703257817053185) {
   out_9047703257817053185[0] = state[6];
}
void H_25(double *state, double *unused, double *out_9459682309458463) {
   out_9459682309458463[0] = 0;
   out_9459682309458463[1] = 0;
   out_9459682309458463[2] = 0;
   out_9459682309458463[3] = 0;
   out_9459682309458463[4] = 0;
   out_9459682309458463[5] = 0;
   out_9459682309458463[6] = 1;
   out_9459682309458463[7] = 0;
   out_9459682309458463[8] = 0;
}
void h_24(double *state, double *unused, double *out_3785372931671791340) {
   out_3785372931671791340[0] = state[4];
   out_3785372931671791340[1] = state[5];
}
void H_24(double *state, double *unused, double *out_3543901091891214266) {
   out_3543901091891214266[0] = 0;
   out_3543901091891214266[1] = 0;
   out_3543901091891214266[2] = 0;
   out_3543901091891214266[3] = 0;
   out_3543901091891214266[4] = 1;
   out_3543901091891214266[5] = 0;
   out_3543901091891214266[6] = 0;
   out_3543901091891214266[7] = 0;
   out_3543901091891214266[8] = 0;
   out_3543901091891214266[9] = 0;
   out_3543901091891214266[10] = 0;
   out_3543901091891214266[11] = 0;
   out_3543901091891214266[12] = 0;
   out_3543901091891214266[13] = 0;
   out_3543901091891214266[14] = 1;
   out_3543901091891214266[15] = 0;
   out_3543901091891214266[16] = 0;
   out_3543901091891214266[17] = 0;
}
void h_30(double *state, double *unused, double *out_407825781098511301) {
   out_407825781098511301[0] = state[4];
}
void H_30(double *state, double *unused, double *out_2527792640816707090) {
   out_2527792640816707090[0] = 0;
   out_2527792640816707090[1] = 0;
   out_2527792640816707090[2] = 0;
   out_2527792640816707090[3] = 0;
   out_2527792640816707090[4] = 1;
   out_2527792640816707090[5] = 0;
   out_2527792640816707090[6] = 0;
   out_2527792640816707090[7] = 0;
   out_2527792640816707090[8] = 0;
}
void h_26(double *state, double *unused, double *out_3220377884368364684) {
   out_3220377884368364684[0] = state[7];
}
void H_26(double *state, double *unused, double *out_3732043636564597761) {
   out_3732043636564597761[0] = 0;
   out_3732043636564597761[1] = 0;
   out_3732043636564597761[2] = 0;
   out_3732043636564597761[3] = 0;
   out_3732043636564597761[4] = 0;
   out_3732043636564597761[5] = 0;
   out_3732043636564597761[6] = 0;
   out_3732043636564597761[7] = 1;
   out_3732043636564597761[8] = 0;
}
void h_27(double *state, double *unused, double *out_4397367548231652786) {
   out_4397367548231652786[0] = state[3];
}
void H_27(double *state, double *unused, double *out_353029329016282179) {
   out_353029329016282179[0] = 0;
   out_353029329016282179[1] = 0;
   out_353029329016282179[2] = 0;
   out_353029329016282179[3] = 1;
   out_353029329016282179[4] = 0;
   out_353029329016282179[5] = 0;
   out_353029329016282179[6] = 0;
   out_353029329016282179[7] = 0;
   out_353029329016282179[8] = 0;
}
void h_29(double *state, double *unused, double *out_6286111268657226389) {
   out_6286111268657226389[0] = state[1];
}
void H_29(double *state, double *unused, double *out_3038023985131099274) {
   out_3038023985131099274[0] = 0;
   out_3038023985131099274[1] = 1;
   out_3038023985131099274[2] = 0;
   out_3038023985131099274[3] = 0;
   out_3038023985131099274[4] = 0;
   out_3038023985131099274[5] = 0;
   out_3038023985131099274[6] = 0;
   out_3038023985131099274[7] = 0;
   out_3038023985131099274[8] = 0;
}
void h_28(double *state, double *unused, double *out_7434153599675985471) {
   out_7434153599675985471[0] = state[0];
}
void H_28(double *state, double *unused, double *out_2044375031938431300) {
   out_2044375031938431300[0] = 1;
   out_2044375031938431300[1] = 0;
   out_2044375031938431300[2] = 0;
   out_2044375031938431300[3] = 0;
   out_2044375031938431300[4] = 0;
   out_2044375031938431300[5] = 0;
   out_2044375031938431300[6] = 0;
   out_2044375031938431300[7] = 0;
   out_2044375031938431300[8] = 0;
}
void h_31(double *state, double *unused, double *out_2459875331340758022) {
   out_2459875331340758022[0] = state[8];
}
void H_31(double *state, double *unused, double *out_4358251738797949237) {
   out_4358251738797949237[0] = 0;
   out_4358251738797949237[1] = 0;
   out_4358251738797949237[2] = 0;
   out_4358251738797949237[3] = 0;
   out_4358251738797949237[4] = 0;
   out_4358251738797949237[5] = 0;
   out_4358251738797949237[6] = 0;
   out_4358251738797949237[7] = 0;
   out_4358251738797949237[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_5388524865571385571) {
  err_fun(nom_x, delta_x, out_5388524865571385571);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_7040447560413333839) {
  inv_err_fun(nom_x, true_x, out_7040447560413333839);
}
void car_H_mod_fun(double *state, double *out_2980610617701040674) {
  H_mod_fun(state, out_2980610617701040674);
}
void car_f_fun(double *state, double dt, double *out_2068294276185711975) {
  f_fun(state,  dt, out_2068294276185711975);
}
void car_F_fun(double *state, double dt, double *out_2484699426223934627) {
  F_fun(state,  dt, out_2484699426223934627);
}
void car_h_25(double *state, double *unused, double *out_9047703257817053185) {
  h_25(state, unused, out_9047703257817053185);
}
void car_H_25(double *state, double *unused, double *out_9459682309458463) {
  H_25(state, unused, out_9459682309458463);
}
void car_h_24(double *state, double *unused, double *out_3785372931671791340) {
  h_24(state, unused, out_3785372931671791340);
}
void car_H_24(double *state, double *unused, double *out_3543901091891214266) {
  H_24(state, unused, out_3543901091891214266);
}
void car_h_30(double *state, double *unused, double *out_407825781098511301) {
  h_30(state, unused, out_407825781098511301);
}
void car_H_30(double *state, double *unused, double *out_2527792640816707090) {
  H_30(state, unused, out_2527792640816707090);
}
void car_h_26(double *state, double *unused, double *out_3220377884368364684) {
  h_26(state, unused, out_3220377884368364684);
}
void car_H_26(double *state, double *unused, double *out_3732043636564597761) {
  H_26(state, unused, out_3732043636564597761);
}
void car_h_27(double *state, double *unused, double *out_4397367548231652786) {
  h_27(state, unused, out_4397367548231652786);
}
void car_H_27(double *state, double *unused, double *out_353029329016282179) {
  H_27(state, unused, out_353029329016282179);
}
void car_h_29(double *state, double *unused, double *out_6286111268657226389) {
  h_29(state, unused, out_6286111268657226389);
}
void car_H_29(double *state, double *unused, double *out_3038023985131099274) {
  H_29(state, unused, out_3038023985131099274);
}
void car_h_28(double *state, double *unused, double *out_7434153599675985471) {
  h_28(state, unused, out_7434153599675985471);
}
void car_H_28(double *state, double *unused, double *out_2044375031938431300) {
  H_28(state, unused, out_2044375031938431300);
}
void car_h_31(double *state, double *unused, double *out_2459875331340758022) {
  h_31(state, unused, out_2459875331340758022);
}
void car_H_31(double *state, double *unused, double *out_4358251738797949237) {
  H_31(state, unused, out_4358251738797949237);
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
