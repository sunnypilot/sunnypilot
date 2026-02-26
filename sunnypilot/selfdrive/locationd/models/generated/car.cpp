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
void err_fun(double *nom_x, double *delta_x, double *out_2451474689670239473) {
   out_2451474689670239473[0] = delta_x[0] + nom_x[0];
   out_2451474689670239473[1] = delta_x[1] + nom_x[1];
   out_2451474689670239473[2] = delta_x[2] + nom_x[2];
   out_2451474689670239473[3] = delta_x[3] + nom_x[3];
   out_2451474689670239473[4] = delta_x[4] + nom_x[4];
   out_2451474689670239473[5] = delta_x[5] + nom_x[5];
   out_2451474689670239473[6] = delta_x[6] + nom_x[6];
   out_2451474689670239473[7] = delta_x[7] + nom_x[7];
   out_2451474689670239473[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_604343562526300868) {
   out_604343562526300868[0] = -nom_x[0] + true_x[0];
   out_604343562526300868[1] = -nom_x[1] + true_x[1];
   out_604343562526300868[2] = -nom_x[2] + true_x[2];
   out_604343562526300868[3] = -nom_x[3] + true_x[3];
   out_604343562526300868[4] = -nom_x[4] + true_x[4];
   out_604343562526300868[5] = -nom_x[5] + true_x[5];
   out_604343562526300868[6] = -nom_x[6] + true_x[6];
   out_604343562526300868[7] = -nom_x[7] + true_x[7];
   out_604343562526300868[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_7527290391511332925) {
   out_7527290391511332925[0] = 1.0;
   out_7527290391511332925[1] = 0.0;
   out_7527290391511332925[2] = 0.0;
   out_7527290391511332925[3] = 0.0;
   out_7527290391511332925[4] = 0.0;
   out_7527290391511332925[5] = 0.0;
   out_7527290391511332925[6] = 0.0;
   out_7527290391511332925[7] = 0.0;
   out_7527290391511332925[8] = 0.0;
   out_7527290391511332925[9] = 0.0;
   out_7527290391511332925[10] = 1.0;
   out_7527290391511332925[11] = 0.0;
   out_7527290391511332925[12] = 0.0;
   out_7527290391511332925[13] = 0.0;
   out_7527290391511332925[14] = 0.0;
   out_7527290391511332925[15] = 0.0;
   out_7527290391511332925[16] = 0.0;
   out_7527290391511332925[17] = 0.0;
   out_7527290391511332925[18] = 0.0;
   out_7527290391511332925[19] = 0.0;
   out_7527290391511332925[20] = 1.0;
   out_7527290391511332925[21] = 0.0;
   out_7527290391511332925[22] = 0.0;
   out_7527290391511332925[23] = 0.0;
   out_7527290391511332925[24] = 0.0;
   out_7527290391511332925[25] = 0.0;
   out_7527290391511332925[26] = 0.0;
   out_7527290391511332925[27] = 0.0;
   out_7527290391511332925[28] = 0.0;
   out_7527290391511332925[29] = 0.0;
   out_7527290391511332925[30] = 1.0;
   out_7527290391511332925[31] = 0.0;
   out_7527290391511332925[32] = 0.0;
   out_7527290391511332925[33] = 0.0;
   out_7527290391511332925[34] = 0.0;
   out_7527290391511332925[35] = 0.0;
   out_7527290391511332925[36] = 0.0;
   out_7527290391511332925[37] = 0.0;
   out_7527290391511332925[38] = 0.0;
   out_7527290391511332925[39] = 0.0;
   out_7527290391511332925[40] = 1.0;
   out_7527290391511332925[41] = 0.0;
   out_7527290391511332925[42] = 0.0;
   out_7527290391511332925[43] = 0.0;
   out_7527290391511332925[44] = 0.0;
   out_7527290391511332925[45] = 0.0;
   out_7527290391511332925[46] = 0.0;
   out_7527290391511332925[47] = 0.0;
   out_7527290391511332925[48] = 0.0;
   out_7527290391511332925[49] = 0.0;
   out_7527290391511332925[50] = 1.0;
   out_7527290391511332925[51] = 0.0;
   out_7527290391511332925[52] = 0.0;
   out_7527290391511332925[53] = 0.0;
   out_7527290391511332925[54] = 0.0;
   out_7527290391511332925[55] = 0.0;
   out_7527290391511332925[56] = 0.0;
   out_7527290391511332925[57] = 0.0;
   out_7527290391511332925[58] = 0.0;
   out_7527290391511332925[59] = 0.0;
   out_7527290391511332925[60] = 1.0;
   out_7527290391511332925[61] = 0.0;
   out_7527290391511332925[62] = 0.0;
   out_7527290391511332925[63] = 0.0;
   out_7527290391511332925[64] = 0.0;
   out_7527290391511332925[65] = 0.0;
   out_7527290391511332925[66] = 0.0;
   out_7527290391511332925[67] = 0.0;
   out_7527290391511332925[68] = 0.0;
   out_7527290391511332925[69] = 0.0;
   out_7527290391511332925[70] = 1.0;
   out_7527290391511332925[71] = 0.0;
   out_7527290391511332925[72] = 0.0;
   out_7527290391511332925[73] = 0.0;
   out_7527290391511332925[74] = 0.0;
   out_7527290391511332925[75] = 0.0;
   out_7527290391511332925[76] = 0.0;
   out_7527290391511332925[77] = 0.0;
   out_7527290391511332925[78] = 0.0;
   out_7527290391511332925[79] = 0.0;
   out_7527290391511332925[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_5082395293757901048) {
   out_5082395293757901048[0] = state[0];
   out_5082395293757901048[1] = state[1];
   out_5082395293757901048[2] = state[2];
   out_5082395293757901048[3] = state[3];
   out_5082395293757901048[4] = state[4];
   out_5082395293757901048[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8100000000000005*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_5082395293757901048[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_5082395293757901048[7] = state[7];
   out_5082395293757901048[8] = state[8];
}
void F_fun(double *state, double dt, double *out_8822652265481800230) {
   out_8822652265481800230[0] = 1;
   out_8822652265481800230[1] = 0;
   out_8822652265481800230[2] = 0;
   out_8822652265481800230[3] = 0;
   out_8822652265481800230[4] = 0;
   out_8822652265481800230[5] = 0;
   out_8822652265481800230[6] = 0;
   out_8822652265481800230[7] = 0;
   out_8822652265481800230[8] = 0;
   out_8822652265481800230[9] = 0;
   out_8822652265481800230[10] = 1;
   out_8822652265481800230[11] = 0;
   out_8822652265481800230[12] = 0;
   out_8822652265481800230[13] = 0;
   out_8822652265481800230[14] = 0;
   out_8822652265481800230[15] = 0;
   out_8822652265481800230[16] = 0;
   out_8822652265481800230[17] = 0;
   out_8822652265481800230[18] = 0;
   out_8822652265481800230[19] = 0;
   out_8822652265481800230[20] = 1;
   out_8822652265481800230[21] = 0;
   out_8822652265481800230[22] = 0;
   out_8822652265481800230[23] = 0;
   out_8822652265481800230[24] = 0;
   out_8822652265481800230[25] = 0;
   out_8822652265481800230[26] = 0;
   out_8822652265481800230[27] = 0;
   out_8822652265481800230[28] = 0;
   out_8822652265481800230[29] = 0;
   out_8822652265481800230[30] = 1;
   out_8822652265481800230[31] = 0;
   out_8822652265481800230[32] = 0;
   out_8822652265481800230[33] = 0;
   out_8822652265481800230[34] = 0;
   out_8822652265481800230[35] = 0;
   out_8822652265481800230[36] = 0;
   out_8822652265481800230[37] = 0;
   out_8822652265481800230[38] = 0;
   out_8822652265481800230[39] = 0;
   out_8822652265481800230[40] = 1;
   out_8822652265481800230[41] = 0;
   out_8822652265481800230[42] = 0;
   out_8822652265481800230[43] = 0;
   out_8822652265481800230[44] = 0;
   out_8822652265481800230[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_8822652265481800230[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_8822652265481800230[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_8822652265481800230[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_8822652265481800230[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_8822652265481800230[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_8822652265481800230[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_8822652265481800230[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_8822652265481800230[53] = -9.8100000000000005*dt;
   out_8822652265481800230[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_8822652265481800230[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_8822652265481800230[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_8822652265481800230[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_8822652265481800230[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_8822652265481800230[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_8822652265481800230[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_8822652265481800230[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_8822652265481800230[62] = 0;
   out_8822652265481800230[63] = 0;
   out_8822652265481800230[64] = 0;
   out_8822652265481800230[65] = 0;
   out_8822652265481800230[66] = 0;
   out_8822652265481800230[67] = 0;
   out_8822652265481800230[68] = 0;
   out_8822652265481800230[69] = 0;
   out_8822652265481800230[70] = 1;
   out_8822652265481800230[71] = 0;
   out_8822652265481800230[72] = 0;
   out_8822652265481800230[73] = 0;
   out_8822652265481800230[74] = 0;
   out_8822652265481800230[75] = 0;
   out_8822652265481800230[76] = 0;
   out_8822652265481800230[77] = 0;
   out_8822652265481800230[78] = 0;
   out_8822652265481800230[79] = 0;
   out_8822652265481800230[80] = 1;
}
void h_25(double *state, double *unused, double *out_345105324244458672) {
   out_345105324244458672[0] = state[6];
}
void H_25(double *state, double *unused, double *out_4004241752865967777) {
   out_4004241752865967777[0] = 0;
   out_4004241752865967777[1] = 0;
   out_4004241752865967777[2] = 0;
   out_4004241752865967777[3] = 0;
   out_4004241752865967777[4] = 0;
   out_4004241752865967777[5] = 0;
   out_4004241752865967777[6] = 1;
   out_4004241752865967777[7] = 0;
   out_4004241752865967777[8] = 0;
}
void h_24(double *state, double *unused, double *out_3988546653363688877) {
   out_3988546653363688877[0] = state[4];
   out_3988546653363688877[1] = state[5];
}
void H_24(double *state, double *unused, double *out_7562167351668290913) {
   out_7562167351668290913[0] = 0;
   out_7562167351668290913[1] = 0;
   out_7562167351668290913[2] = 0;
   out_7562167351668290913[3] = 0;
   out_7562167351668290913[4] = 1;
   out_7562167351668290913[5] = 0;
   out_7562167351668290913[6] = 0;
   out_7562167351668290913[7] = 0;
   out_7562167351668290913[8] = 0;
   out_7562167351668290913[9] = 0;
   out_7562167351668290913[10] = 0;
   out_7562167351668290913[11] = 0;
   out_7562167351668290913[12] = 0;
   out_7562167351668290913[13] = 0;
   out_7562167351668290913[14] = 1;
   out_7562167351668290913[15] = 0;
   out_7562167351668290913[16] = 0;
   out_7562167351668290913[17] = 0;
}
void h_30(double *state, double *unused, double *out_9209216749137479858) {
   out_9209216749137479858[0] = state[4];
}
void H_30(double *state, double *unused, double *out_7525811979351967084) {
   out_7525811979351967084[0] = 0;
   out_7525811979351967084[1] = 0;
   out_7525811979351967084[2] = 0;
   out_7525811979351967084[3] = 0;
   out_7525811979351967084[4] = 1;
   out_7525811979351967084[5] = 0;
   out_7525811979351967084[6] = 0;
   out_7525811979351967084[7] = 0;
   out_7525811979351967084[8] = 0;
}
void h_26(double *state, double *unused, double *out_4235854056911226113) {
   out_4235854056911226113[0] = state[7];
}
void H_26(double *state, double *unused, double *out_262738433991911553) {
   out_262738433991911553[0] = 0;
   out_262738433991911553[1] = 0;
   out_262738433991911553[2] = 0;
   out_262738433991911553[3] = 0;
   out_262738433991911553[4] = 0;
   out_262738433991911553[5] = 0;
   out_262738433991911553[6] = 0;
   out_262738433991911553[7] = 1;
   out_262738433991911553[8] = 0;
}
void h_27(double *state, double *unused, double *out_3381891375688791357) {
   out_3381891375688791357[0] = state[3];
}
void H_27(double *state, double *unused, double *out_8746168782557159621) {
   out_8746168782557159621[0] = 0;
   out_8746168782557159621[1] = 0;
   out_8746168782557159621[2] = 0;
   out_8746168782557159621[3] = 1;
   out_8746168782557159621[4] = 0;
   out_8746168782557159621[5] = 0;
   out_8746168782557159621[6] = 0;
   out_8746168782557159621[7] = 0;
   out_8746168782557159621[8] = 0;
}
void h_29(double *state, double *unused, double *out_8294017471670409323) {
   out_8294017471670409323[0] = state[1];
}
void H_29(double *state, double *unused, double *out_7015580635037574900) {
   out_7015580635037574900[0] = 0;
   out_7015580635037574900[1] = 1;
   out_7015580635037574900[2] = 0;
   out_7015580635037574900[3] = 0;
   out_7015580635037574900[4] = 0;
   out_7015580635037574900[5] = 0;
   out_7015580635037574900[6] = 0;
   out_7015580635037574900[7] = 0;
   out_7015580635037574900[8] = 0;
}
void h_28(double *state, double *unused, double *out_1016060705592837655) {
   out_1016060705592837655[0] = state[0];
}
void H_28(double *state, double *unused, double *out_6348764421602446142) {
   out_6348764421602446142[0] = 1;
   out_6348764421602446142[1] = 0;
   out_6348764421602446142[2] = 0;
   out_6348764421602446142[3] = 0;
   out_6348764421602446142[4] = 0;
   out_6348764421602446142[5] = 0;
   out_6348764421602446142[6] = 0;
   out_6348764421602446142[7] = 0;
   out_6348764421602446142[8] = 0;
}
void h_31(double *state, double *unused, double *out_7115453440004429653) {
   out_7115453440004429653[0] = state[8];
}
void H_31(double *state, double *unused, double *out_4034887714742928205) {
   out_4034887714742928205[0] = 0;
   out_4034887714742928205[1] = 0;
   out_4034887714742928205[2] = 0;
   out_4034887714742928205[3] = 0;
   out_4034887714742928205[4] = 0;
   out_4034887714742928205[5] = 0;
   out_4034887714742928205[6] = 0;
   out_4034887714742928205[7] = 0;
   out_4034887714742928205[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_2451474689670239473) {
  err_fun(nom_x, delta_x, out_2451474689670239473);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_604343562526300868) {
  inv_err_fun(nom_x, true_x, out_604343562526300868);
}
void car_H_mod_fun(double *state, double *out_7527290391511332925) {
  H_mod_fun(state, out_7527290391511332925);
}
void car_f_fun(double *state, double dt, double *out_5082395293757901048) {
  f_fun(state,  dt, out_5082395293757901048);
}
void car_F_fun(double *state, double dt, double *out_8822652265481800230) {
  F_fun(state,  dt, out_8822652265481800230);
}
void car_h_25(double *state, double *unused, double *out_345105324244458672) {
  h_25(state, unused, out_345105324244458672);
}
void car_H_25(double *state, double *unused, double *out_4004241752865967777) {
  H_25(state, unused, out_4004241752865967777);
}
void car_h_24(double *state, double *unused, double *out_3988546653363688877) {
  h_24(state, unused, out_3988546653363688877);
}
void car_H_24(double *state, double *unused, double *out_7562167351668290913) {
  H_24(state, unused, out_7562167351668290913);
}
void car_h_30(double *state, double *unused, double *out_9209216749137479858) {
  h_30(state, unused, out_9209216749137479858);
}
void car_H_30(double *state, double *unused, double *out_7525811979351967084) {
  H_30(state, unused, out_7525811979351967084);
}
void car_h_26(double *state, double *unused, double *out_4235854056911226113) {
  h_26(state, unused, out_4235854056911226113);
}
void car_H_26(double *state, double *unused, double *out_262738433991911553) {
  H_26(state, unused, out_262738433991911553);
}
void car_h_27(double *state, double *unused, double *out_3381891375688791357) {
  h_27(state, unused, out_3381891375688791357);
}
void car_H_27(double *state, double *unused, double *out_8746168782557159621) {
  H_27(state, unused, out_8746168782557159621);
}
void car_h_29(double *state, double *unused, double *out_8294017471670409323) {
  h_29(state, unused, out_8294017471670409323);
}
void car_H_29(double *state, double *unused, double *out_7015580635037574900) {
  H_29(state, unused, out_7015580635037574900);
}
void car_h_28(double *state, double *unused, double *out_1016060705592837655) {
  h_28(state, unused, out_1016060705592837655);
}
void car_H_28(double *state, double *unused, double *out_6348764421602446142) {
  H_28(state, unused, out_6348764421602446142);
}
void car_h_31(double *state, double *unused, double *out_7115453440004429653) {
  h_31(state, unused, out_7115453440004429653);
}
void car_H_31(double *state, double *unused, double *out_4034887714742928205) {
  H_31(state, unused, out_4034887714742928205);
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
