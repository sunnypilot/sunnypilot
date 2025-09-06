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
void err_fun(double *nom_x, double *delta_x, double *out_605231361500348121) {
   out_605231361500348121[0] = delta_x[0] + nom_x[0];
   out_605231361500348121[1] = delta_x[1] + nom_x[1];
   out_605231361500348121[2] = delta_x[2] + nom_x[2];
   out_605231361500348121[3] = delta_x[3] + nom_x[3];
   out_605231361500348121[4] = delta_x[4] + nom_x[4];
   out_605231361500348121[5] = delta_x[5] + nom_x[5];
   out_605231361500348121[6] = delta_x[6] + nom_x[6];
   out_605231361500348121[7] = delta_x[7] + nom_x[7];
   out_605231361500348121[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_1750721289063579832) {
   out_1750721289063579832[0] = -nom_x[0] + true_x[0];
   out_1750721289063579832[1] = -nom_x[1] + true_x[1];
   out_1750721289063579832[2] = -nom_x[2] + true_x[2];
   out_1750721289063579832[3] = -nom_x[3] + true_x[3];
   out_1750721289063579832[4] = -nom_x[4] + true_x[4];
   out_1750721289063579832[5] = -nom_x[5] + true_x[5];
   out_1750721289063579832[6] = -nom_x[6] + true_x[6];
   out_1750721289063579832[7] = -nom_x[7] + true_x[7];
   out_1750721289063579832[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_4455056590274498868) {
   out_4455056590274498868[0] = 1.0;
   out_4455056590274498868[1] = 0.0;
   out_4455056590274498868[2] = 0.0;
   out_4455056590274498868[3] = 0.0;
   out_4455056590274498868[4] = 0.0;
   out_4455056590274498868[5] = 0.0;
   out_4455056590274498868[6] = 0.0;
   out_4455056590274498868[7] = 0.0;
   out_4455056590274498868[8] = 0.0;
   out_4455056590274498868[9] = 0.0;
   out_4455056590274498868[10] = 1.0;
   out_4455056590274498868[11] = 0.0;
   out_4455056590274498868[12] = 0.0;
   out_4455056590274498868[13] = 0.0;
   out_4455056590274498868[14] = 0.0;
   out_4455056590274498868[15] = 0.0;
   out_4455056590274498868[16] = 0.0;
   out_4455056590274498868[17] = 0.0;
   out_4455056590274498868[18] = 0.0;
   out_4455056590274498868[19] = 0.0;
   out_4455056590274498868[20] = 1.0;
   out_4455056590274498868[21] = 0.0;
   out_4455056590274498868[22] = 0.0;
   out_4455056590274498868[23] = 0.0;
   out_4455056590274498868[24] = 0.0;
   out_4455056590274498868[25] = 0.0;
   out_4455056590274498868[26] = 0.0;
   out_4455056590274498868[27] = 0.0;
   out_4455056590274498868[28] = 0.0;
   out_4455056590274498868[29] = 0.0;
   out_4455056590274498868[30] = 1.0;
   out_4455056590274498868[31] = 0.0;
   out_4455056590274498868[32] = 0.0;
   out_4455056590274498868[33] = 0.0;
   out_4455056590274498868[34] = 0.0;
   out_4455056590274498868[35] = 0.0;
   out_4455056590274498868[36] = 0.0;
   out_4455056590274498868[37] = 0.0;
   out_4455056590274498868[38] = 0.0;
   out_4455056590274498868[39] = 0.0;
   out_4455056590274498868[40] = 1.0;
   out_4455056590274498868[41] = 0.0;
   out_4455056590274498868[42] = 0.0;
   out_4455056590274498868[43] = 0.0;
   out_4455056590274498868[44] = 0.0;
   out_4455056590274498868[45] = 0.0;
   out_4455056590274498868[46] = 0.0;
   out_4455056590274498868[47] = 0.0;
   out_4455056590274498868[48] = 0.0;
   out_4455056590274498868[49] = 0.0;
   out_4455056590274498868[50] = 1.0;
   out_4455056590274498868[51] = 0.0;
   out_4455056590274498868[52] = 0.0;
   out_4455056590274498868[53] = 0.0;
   out_4455056590274498868[54] = 0.0;
   out_4455056590274498868[55] = 0.0;
   out_4455056590274498868[56] = 0.0;
   out_4455056590274498868[57] = 0.0;
   out_4455056590274498868[58] = 0.0;
   out_4455056590274498868[59] = 0.0;
   out_4455056590274498868[60] = 1.0;
   out_4455056590274498868[61] = 0.0;
   out_4455056590274498868[62] = 0.0;
   out_4455056590274498868[63] = 0.0;
   out_4455056590274498868[64] = 0.0;
   out_4455056590274498868[65] = 0.0;
   out_4455056590274498868[66] = 0.0;
   out_4455056590274498868[67] = 0.0;
   out_4455056590274498868[68] = 0.0;
   out_4455056590274498868[69] = 0.0;
   out_4455056590274498868[70] = 1.0;
   out_4455056590274498868[71] = 0.0;
   out_4455056590274498868[72] = 0.0;
   out_4455056590274498868[73] = 0.0;
   out_4455056590274498868[74] = 0.0;
   out_4455056590274498868[75] = 0.0;
   out_4455056590274498868[76] = 0.0;
   out_4455056590274498868[77] = 0.0;
   out_4455056590274498868[78] = 0.0;
   out_4455056590274498868[79] = 0.0;
   out_4455056590274498868[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_6628753160686287132) {
   out_6628753160686287132[0] = state[0];
   out_6628753160686287132[1] = state[1];
   out_6628753160686287132[2] = state[2];
   out_6628753160686287132[3] = state[3];
   out_6628753160686287132[4] = state[4];
   out_6628753160686287132[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8100000000000005*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_6628753160686287132[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_6628753160686287132[7] = state[7];
   out_6628753160686287132[8] = state[8];
}
void F_fun(double *state, double dt, double *out_2264722656215431531) {
   out_2264722656215431531[0] = 1;
   out_2264722656215431531[1] = 0;
   out_2264722656215431531[2] = 0;
   out_2264722656215431531[3] = 0;
   out_2264722656215431531[4] = 0;
   out_2264722656215431531[5] = 0;
   out_2264722656215431531[6] = 0;
   out_2264722656215431531[7] = 0;
   out_2264722656215431531[8] = 0;
   out_2264722656215431531[9] = 0;
   out_2264722656215431531[10] = 1;
   out_2264722656215431531[11] = 0;
   out_2264722656215431531[12] = 0;
   out_2264722656215431531[13] = 0;
   out_2264722656215431531[14] = 0;
   out_2264722656215431531[15] = 0;
   out_2264722656215431531[16] = 0;
   out_2264722656215431531[17] = 0;
   out_2264722656215431531[18] = 0;
   out_2264722656215431531[19] = 0;
   out_2264722656215431531[20] = 1;
   out_2264722656215431531[21] = 0;
   out_2264722656215431531[22] = 0;
   out_2264722656215431531[23] = 0;
   out_2264722656215431531[24] = 0;
   out_2264722656215431531[25] = 0;
   out_2264722656215431531[26] = 0;
   out_2264722656215431531[27] = 0;
   out_2264722656215431531[28] = 0;
   out_2264722656215431531[29] = 0;
   out_2264722656215431531[30] = 1;
   out_2264722656215431531[31] = 0;
   out_2264722656215431531[32] = 0;
   out_2264722656215431531[33] = 0;
   out_2264722656215431531[34] = 0;
   out_2264722656215431531[35] = 0;
   out_2264722656215431531[36] = 0;
   out_2264722656215431531[37] = 0;
   out_2264722656215431531[38] = 0;
   out_2264722656215431531[39] = 0;
   out_2264722656215431531[40] = 1;
   out_2264722656215431531[41] = 0;
   out_2264722656215431531[42] = 0;
   out_2264722656215431531[43] = 0;
   out_2264722656215431531[44] = 0;
   out_2264722656215431531[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_2264722656215431531[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_2264722656215431531[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_2264722656215431531[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_2264722656215431531[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_2264722656215431531[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_2264722656215431531[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_2264722656215431531[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_2264722656215431531[53] = -9.8100000000000005*dt;
   out_2264722656215431531[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_2264722656215431531[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_2264722656215431531[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_2264722656215431531[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_2264722656215431531[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_2264722656215431531[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_2264722656215431531[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_2264722656215431531[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_2264722656215431531[62] = 0;
   out_2264722656215431531[63] = 0;
   out_2264722656215431531[64] = 0;
   out_2264722656215431531[65] = 0;
   out_2264722656215431531[66] = 0;
   out_2264722656215431531[67] = 0;
   out_2264722656215431531[68] = 0;
   out_2264722656215431531[69] = 0;
   out_2264722656215431531[70] = 1;
   out_2264722656215431531[71] = 0;
   out_2264722656215431531[72] = 0;
   out_2264722656215431531[73] = 0;
   out_2264722656215431531[74] = 0;
   out_2264722656215431531[75] = 0;
   out_2264722656215431531[76] = 0;
   out_2264722656215431531[77] = 0;
   out_2264722656215431531[78] = 0;
   out_2264722656215431531[79] = 0;
   out_2264722656215431531[80] = 1;
}
void h_25(double *state, double *unused, double *out_7426226088437493508) {
   out_7426226088437493508[0] = state[6];
}
void H_25(double *state, double *unused, double *out_2224639529561806043) {
   out_2224639529561806043[0] = 0;
   out_2224639529561806043[1] = 0;
   out_2224639529561806043[2] = 0;
   out_2224639529561806043[3] = 0;
   out_2224639529561806043[4] = 0;
   out_2224639529561806043[5] = 0;
   out_2224639529561806043[6] = 1;
   out_2224639529561806043[7] = 0;
   out_2224639529561806043[8] = 0;
}
void h_24(double *state, double *unused, double *out_3037239344096390205) {
   out_3037239344096390205[0] = state[4];
   out_3037239344096390205[1] = state[5];
}
void H_24(double *state, double *unused, double *out_51989930556306477) {
   out_51989930556306477[0] = 0;
   out_51989930556306477[1] = 0;
   out_51989930556306477[2] = 0;
   out_51989930556306477[3] = 0;
   out_51989930556306477[4] = 1;
   out_51989930556306477[5] = 0;
   out_51989930556306477[6] = 0;
   out_51989930556306477[7] = 0;
   out_51989930556306477[8] = 0;
   out_51989930556306477[9] = 0;
   out_51989930556306477[10] = 0;
   out_51989930556306477[11] = 0;
   out_51989930556306477[12] = 0;
   out_51989930556306477[13] = 0;
   out_51989930556306477[14] = 1;
   out_51989930556306477[15] = 0;
   out_51989930556306477[16] = 0;
   out_51989930556306477[17] = 0;
}
void h_30(double *state, double *unused, double *out_4205599215429103046) {
   out_4205599215429103046[0] = state[4];
}
void H_30(double *state, double *unused, double *out_2303056800565802155) {
   out_2303056800565802155[0] = 0;
   out_2303056800565802155[1] = 0;
   out_2303056800565802155[2] = 0;
   out_2303056800565802155[3] = 0;
   out_2303056800565802155[4] = 1;
   out_2303056800565802155[5] = 0;
   out_2303056800565802155[6] = 0;
   out_2303056800565802155[7] = 0;
   out_2303056800565802155[8] = 0;
}
void h_26(double *state, double *unused, double *out_5652982176475607162) {
   out_5652982176475607162[0] = state[7];
}
void H_26(double *state, double *unused, double *out_1516863789312250181) {
   out_1516863789312250181[0] = 0;
   out_1516863789312250181[1] = 0;
   out_1516863789312250181[2] = 0;
   out_1516863789312250181[3] = 0;
   out_1516863789312250181[4] = 0;
   out_1516863789312250181[5] = 0;
   out_1516863789312250181[6] = 0;
   out_1516863789312250181[7] = 1;
   out_1516863789312250181[8] = 0;
}
void h_27(double *state, double *unused, double *out_2200318872602168561) {
   out_2200318872602168561[0] = state[3];
}
void H_27(double *state, double *unused, double *out_4477820112366227066) {
   out_4477820112366227066[0] = 0;
   out_4477820112366227066[1] = 0;
   out_4477820112366227066[2] = 0;
   out_4477820112366227066[3] = 1;
   out_4477820112366227066[4] = 0;
   out_4477820112366227066[5] = 0;
   out_4477820112366227066[6] = 0;
   out_4477820112366227066[7] = 0;
   out_4477820112366227066[8] = 0;
}
void h_29(double *state, double *unused, double *out_8483159944286710614) {
   out_8483159944286710614[0] = state[1];
}
void H_29(double *state, double *unused, double *out_1792825456251409971) {
   out_1792825456251409971[0] = 0;
   out_1792825456251409971[1] = 1;
   out_1792825456251409971[2] = 0;
   out_1792825456251409971[3] = 0;
   out_1792825456251409971[4] = 0;
   out_1792825456251409971[5] = 0;
   out_1792825456251409971[6] = 0;
   out_1792825456251409971[7] = 0;
   out_1792825456251409971[8] = 0;
}
void h_28(double *state, double *unused, double *out_2225042042696062972) {
   out_2225042042696062972[0] = state[0];
}
void H_28(double *state, double *unused, double *out_170804815313916280) {
   out_170804815313916280[0] = 1;
   out_170804815313916280[1] = 0;
   out_170804815313916280[2] = 0;
   out_170804815313916280[3] = 0;
   out_170804815313916280[4] = 0;
   out_170804815313916280[5] = 0;
   out_170804815313916280[6] = 0;
   out_170804815313916280[7] = 0;
   out_170804815313916280[8] = 0;
}
void h_31(double *state, double *unused, double *out_7988568567903780367) {
   out_7988568567903780367[0] = state[8];
}
void H_31(double *state, double *unused, double *out_2143071891545601657) {
   out_2143071891545601657[0] = 0;
   out_2143071891545601657[1] = 0;
   out_2143071891545601657[2] = 0;
   out_2143071891545601657[3] = 0;
   out_2143071891545601657[4] = 0;
   out_2143071891545601657[5] = 0;
   out_2143071891545601657[6] = 0;
   out_2143071891545601657[7] = 0;
   out_2143071891545601657[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_605231361500348121) {
  err_fun(nom_x, delta_x, out_605231361500348121);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_1750721289063579832) {
  inv_err_fun(nom_x, true_x, out_1750721289063579832);
}
void car_H_mod_fun(double *state, double *out_4455056590274498868) {
  H_mod_fun(state, out_4455056590274498868);
}
void car_f_fun(double *state, double dt, double *out_6628753160686287132) {
  f_fun(state,  dt, out_6628753160686287132);
}
void car_F_fun(double *state, double dt, double *out_2264722656215431531) {
  F_fun(state,  dt, out_2264722656215431531);
}
void car_h_25(double *state, double *unused, double *out_7426226088437493508) {
  h_25(state, unused, out_7426226088437493508);
}
void car_H_25(double *state, double *unused, double *out_2224639529561806043) {
  H_25(state, unused, out_2224639529561806043);
}
void car_h_24(double *state, double *unused, double *out_3037239344096390205) {
  h_24(state, unused, out_3037239344096390205);
}
void car_H_24(double *state, double *unused, double *out_51989930556306477) {
  H_24(state, unused, out_51989930556306477);
}
void car_h_30(double *state, double *unused, double *out_4205599215429103046) {
  h_30(state, unused, out_4205599215429103046);
}
void car_H_30(double *state, double *unused, double *out_2303056800565802155) {
  H_30(state, unused, out_2303056800565802155);
}
void car_h_26(double *state, double *unused, double *out_5652982176475607162) {
  h_26(state, unused, out_5652982176475607162);
}
void car_H_26(double *state, double *unused, double *out_1516863789312250181) {
  H_26(state, unused, out_1516863789312250181);
}
void car_h_27(double *state, double *unused, double *out_2200318872602168561) {
  h_27(state, unused, out_2200318872602168561);
}
void car_H_27(double *state, double *unused, double *out_4477820112366227066) {
  H_27(state, unused, out_4477820112366227066);
}
void car_h_29(double *state, double *unused, double *out_8483159944286710614) {
  h_29(state, unused, out_8483159944286710614);
}
void car_H_29(double *state, double *unused, double *out_1792825456251409971) {
  H_29(state, unused, out_1792825456251409971);
}
void car_h_28(double *state, double *unused, double *out_2225042042696062972) {
  h_28(state, unused, out_2225042042696062972);
}
void car_H_28(double *state, double *unused, double *out_170804815313916280) {
  H_28(state, unused, out_170804815313916280);
}
void car_h_31(double *state, double *unused, double *out_7988568567903780367) {
  h_31(state, unused, out_7988568567903780367);
}
void car_H_31(double *state, double *unused, double *out_2143071891545601657) {
  H_31(state, unused, out_2143071891545601657);
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
