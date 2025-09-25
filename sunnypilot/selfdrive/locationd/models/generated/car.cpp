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
void err_fun(double *nom_x, double *delta_x, double *out_3178351787780867479) {
   out_3178351787780867479[0] = delta_x[0] + nom_x[0];
   out_3178351787780867479[1] = delta_x[1] + nom_x[1];
   out_3178351787780867479[2] = delta_x[2] + nom_x[2];
   out_3178351787780867479[3] = delta_x[3] + nom_x[3];
   out_3178351787780867479[4] = delta_x[4] + nom_x[4];
   out_3178351787780867479[5] = delta_x[5] + nom_x[5];
   out_3178351787780867479[6] = delta_x[6] + nom_x[6];
   out_3178351787780867479[7] = delta_x[7] + nom_x[7];
   out_3178351787780867479[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_6240253129487023512) {
   out_6240253129487023512[0] = -nom_x[0] + true_x[0];
   out_6240253129487023512[1] = -nom_x[1] + true_x[1];
   out_6240253129487023512[2] = -nom_x[2] + true_x[2];
   out_6240253129487023512[3] = -nom_x[3] + true_x[3];
   out_6240253129487023512[4] = -nom_x[4] + true_x[4];
   out_6240253129487023512[5] = -nom_x[5] + true_x[5];
   out_6240253129487023512[6] = -nom_x[6] + true_x[6];
   out_6240253129487023512[7] = -nom_x[7] + true_x[7];
   out_6240253129487023512[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_7483116987311173272) {
   out_7483116987311173272[0] = 1.0;
   out_7483116987311173272[1] = 0.0;
   out_7483116987311173272[2] = 0.0;
   out_7483116987311173272[3] = 0.0;
   out_7483116987311173272[4] = 0.0;
   out_7483116987311173272[5] = 0.0;
   out_7483116987311173272[6] = 0.0;
   out_7483116987311173272[7] = 0.0;
   out_7483116987311173272[8] = 0.0;
   out_7483116987311173272[9] = 0.0;
   out_7483116987311173272[10] = 1.0;
   out_7483116987311173272[11] = 0.0;
   out_7483116987311173272[12] = 0.0;
   out_7483116987311173272[13] = 0.0;
   out_7483116987311173272[14] = 0.0;
   out_7483116987311173272[15] = 0.0;
   out_7483116987311173272[16] = 0.0;
   out_7483116987311173272[17] = 0.0;
   out_7483116987311173272[18] = 0.0;
   out_7483116987311173272[19] = 0.0;
   out_7483116987311173272[20] = 1.0;
   out_7483116987311173272[21] = 0.0;
   out_7483116987311173272[22] = 0.0;
   out_7483116987311173272[23] = 0.0;
   out_7483116987311173272[24] = 0.0;
   out_7483116987311173272[25] = 0.0;
   out_7483116987311173272[26] = 0.0;
   out_7483116987311173272[27] = 0.0;
   out_7483116987311173272[28] = 0.0;
   out_7483116987311173272[29] = 0.0;
   out_7483116987311173272[30] = 1.0;
   out_7483116987311173272[31] = 0.0;
   out_7483116987311173272[32] = 0.0;
   out_7483116987311173272[33] = 0.0;
   out_7483116987311173272[34] = 0.0;
   out_7483116987311173272[35] = 0.0;
   out_7483116987311173272[36] = 0.0;
   out_7483116987311173272[37] = 0.0;
   out_7483116987311173272[38] = 0.0;
   out_7483116987311173272[39] = 0.0;
   out_7483116987311173272[40] = 1.0;
   out_7483116987311173272[41] = 0.0;
   out_7483116987311173272[42] = 0.0;
   out_7483116987311173272[43] = 0.0;
   out_7483116987311173272[44] = 0.0;
   out_7483116987311173272[45] = 0.0;
   out_7483116987311173272[46] = 0.0;
   out_7483116987311173272[47] = 0.0;
   out_7483116987311173272[48] = 0.0;
   out_7483116987311173272[49] = 0.0;
   out_7483116987311173272[50] = 1.0;
   out_7483116987311173272[51] = 0.0;
   out_7483116987311173272[52] = 0.0;
   out_7483116987311173272[53] = 0.0;
   out_7483116987311173272[54] = 0.0;
   out_7483116987311173272[55] = 0.0;
   out_7483116987311173272[56] = 0.0;
   out_7483116987311173272[57] = 0.0;
   out_7483116987311173272[58] = 0.0;
   out_7483116987311173272[59] = 0.0;
   out_7483116987311173272[60] = 1.0;
   out_7483116987311173272[61] = 0.0;
   out_7483116987311173272[62] = 0.0;
   out_7483116987311173272[63] = 0.0;
   out_7483116987311173272[64] = 0.0;
   out_7483116987311173272[65] = 0.0;
   out_7483116987311173272[66] = 0.0;
   out_7483116987311173272[67] = 0.0;
   out_7483116987311173272[68] = 0.0;
   out_7483116987311173272[69] = 0.0;
   out_7483116987311173272[70] = 1.0;
   out_7483116987311173272[71] = 0.0;
   out_7483116987311173272[72] = 0.0;
   out_7483116987311173272[73] = 0.0;
   out_7483116987311173272[74] = 0.0;
   out_7483116987311173272[75] = 0.0;
   out_7483116987311173272[76] = 0.0;
   out_7483116987311173272[77] = 0.0;
   out_7483116987311173272[78] = 0.0;
   out_7483116987311173272[79] = 0.0;
   out_7483116987311173272[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_5651695903721239210) {
   out_5651695903721239210[0] = state[0];
   out_5651695903721239210[1] = state[1];
   out_5651695903721239210[2] = state[2];
   out_5651695903721239210[3] = state[3];
   out_5651695903721239210[4] = state[4];
   out_5651695903721239210[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8100000000000005*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_5651695903721239210[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_5651695903721239210[7] = state[7];
   out_5651695903721239210[8] = state[8];
}
void F_fun(double *state, double dt, double *out_13263414419101982) {
   out_13263414419101982[0] = 1;
   out_13263414419101982[1] = 0;
   out_13263414419101982[2] = 0;
   out_13263414419101982[3] = 0;
   out_13263414419101982[4] = 0;
   out_13263414419101982[5] = 0;
   out_13263414419101982[6] = 0;
   out_13263414419101982[7] = 0;
   out_13263414419101982[8] = 0;
   out_13263414419101982[9] = 0;
   out_13263414419101982[10] = 1;
   out_13263414419101982[11] = 0;
   out_13263414419101982[12] = 0;
   out_13263414419101982[13] = 0;
   out_13263414419101982[14] = 0;
   out_13263414419101982[15] = 0;
   out_13263414419101982[16] = 0;
   out_13263414419101982[17] = 0;
   out_13263414419101982[18] = 0;
   out_13263414419101982[19] = 0;
   out_13263414419101982[20] = 1;
   out_13263414419101982[21] = 0;
   out_13263414419101982[22] = 0;
   out_13263414419101982[23] = 0;
   out_13263414419101982[24] = 0;
   out_13263414419101982[25] = 0;
   out_13263414419101982[26] = 0;
   out_13263414419101982[27] = 0;
   out_13263414419101982[28] = 0;
   out_13263414419101982[29] = 0;
   out_13263414419101982[30] = 1;
   out_13263414419101982[31] = 0;
   out_13263414419101982[32] = 0;
   out_13263414419101982[33] = 0;
   out_13263414419101982[34] = 0;
   out_13263414419101982[35] = 0;
   out_13263414419101982[36] = 0;
   out_13263414419101982[37] = 0;
   out_13263414419101982[38] = 0;
   out_13263414419101982[39] = 0;
   out_13263414419101982[40] = 1;
   out_13263414419101982[41] = 0;
   out_13263414419101982[42] = 0;
   out_13263414419101982[43] = 0;
   out_13263414419101982[44] = 0;
   out_13263414419101982[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_13263414419101982[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_13263414419101982[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_13263414419101982[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_13263414419101982[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_13263414419101982[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_13263414419101982[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_13263414419101982[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_13263414419101982[53] = -9.8100000000000005*dt;
   out_13263414419101982[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_13263414419101982[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_13263414419101982[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_13263414419101982[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_13263414419101982[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_13263414419101982[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_13263414419101982[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_13263414419101982[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_13263414419101982[62] = 0;
   out_13263414419101982[63] = 0;
   out_13263414419101982[64] = 0;
   out_13263414419101982[65] = 0;
   out_13263414419101982[66] = 0;
   out_13263414419101982[67] = 0;
   out_13263414419101982[68] = 0;
   out_13263414419101982[69] = 0;
   out_13263414419101982[70] = 1;
   out_13263414419101982[71] = 0;
   out_13263414419101982[72] = 0;
   out_13263414419101982[73] = 0;
   out_13263414419101982[74] = 0;
   out_13263414419101982[75] = 0;
   out_13263414419101982[76] = 0;
   out_13263414419101982[77] = 0;
   out_13263414419101982[78] = 0;
   out_13263414419101982[79] = 0;
   out_13263414419101982[80] = 1;
}
void h_25(double *state, double *unused, double *out_4287938734280851291) {
   out_4287938734280851291[0] = state[6];
}
void H_25(double *state, double *unused, double *out_7820602372196285352) {
   out_7820602372196285352[0] = 0;
   out_7820602372196285352[1] = 0;
   out_7820602372196285352[2] = 0;
   out_7820602372196285352[3] = 0;
   out_7820602372196285352[4] = 0;
   out_7820602372196285352[5] = 0;
   out_7820602372196285352[6] = 1;
   out_7820602372196285352[7] = 0;
   out_7820602372196285352[8] = 0;
}
void h_24(double *state, double *unused, double *out_967862149043042631) {
   out_967862149043042631[0] = state[4];
   out_967862149043042631[1] = state[5];
}
void H_24(double *state, double *unused, double *out_402210738519358459) {
   out_402210738519358459[0] = 0;
   out_402210738519358459[1] = 0;
   out_402210738519358459[2] = 0;
   out_402210738519358459[3] = 0;
   out_402210738519358459[4] = 1;
   out_402210738519358459[5] = 0;
   out_402210738519358459[6] = 0;
   out_402210738519358459[7] = 0;
   out_402210738519358459[8] = 0;
   out_402210738519358459[9] = 0;
   out_402210738519358459[10] = 0;
   out_402210738519358459[11] = 0;
   out_402210738519358459[12] = 0;
   out_402210738519358459[13] = 0;
   out_402210738519358459[14] = 1;
   out_402210738519358459[15] = 0;
   out_402210738519358459[16] = 0;
   out_402210738519358459[17] = 0;
}
void h_30(double *state, double *unused, double *out_4012744671996345402) {
   out_4012744671996345402[0] = state[4];
}
void H_30(double *state, double *unused, double *out_7949941319339525422) {
   out_7949941319339525422[0] = 0;
   out_7949941319339525422[1] = 0;
   out_7949941319339525422[2] = 0;
   out_7949941319339525422[3] = 0;
   out_7949941319339525422[4] = 1;
   out_7949941319339525422[5] = 0;
   out_7949941319339525422[6] = 0;
   out_7949941319339525422[7] = 0;
   out_7949941319339525422[8] = 0;
}
void h_26(double *state, double *unused, double *out_3069234819094682967) {
   out_3069234819094682967[0] = state[7];
}
void H_26(double *state, double *unused, double *out_6884638382639210040) {
   out_6884638382639210040[0] = 0;
   out_6884638382639210040[1] = 0;
   out_6884638382639210040[2] = 0;
   out_6884638382639210040[3] = 0;
   out_6884638382639210040[4] = 0;
   out_6884638382639210040[5] = 0;
   out_6884638382639210040[6] = 0;
   out_6884638382639210040[7] = 1;
   out_6884638382639210040[8] = 0;
}
void h_27(double *state, double *unused, double *out_7156042635635634546) {
   out_7156042635635634546[0] = state[3];
}
void H_27(double *state, double *unused, double *out_8322039442569601283) {
   out_8322039442569601283[0] = 0;
   out_8322039442569601283[1] = 0;
   out_8322039442569601283[2] = 0;
   out_8322039442569601283[3] = 1;
   out_8322039442569601283[4] = 0;
   out_8322039442569601283[5] = 0;
   out_8322039442569601283[6] = 0;
   out_8322039442569601283[7] = 0;
   out_8322039442569601283[8] = 0;
}
void h_29(double *state, double *unused, double *out_3409428787319867885) {
   out_3409428787319867885[0] = state[1];
}
void H_29(double *state, double *unused, double *out_6608676715700050250) {
   out_6608676715700050250[0] = 0;
   out_6608676715700050250[1] = 1;
   out_6608676715700050250[2] = 0;
   out_6608676715700050250[3] = 0;
   out_6608676715700050250[4] = 0;
   out_6608676715700050250[5] = 0;
   out_6608676715700050250[6] = 0;
   out_6608676715700050250[7] = 0;
   out_6608676715700050250[8] = 0;
}
void h_28(double *state, double *unused, double *out_976713301355686606) {
   out_976713301355686606[0] = state[0];
}
void H_28(double *state, double *unused, double *out_1526277698630519676) {
   out_1526277698630519676[0] = 1;
   out_1526277698630519676[1] = 0;
   out_1526277698630519676[2] = 0;
   out_1526277698630519676[3] = 0;
   out_1526277698630519676[4] = 0;
   out_1526277698630519676[5] = 0;
   out_1526277698630519676[6] = 0;
   out_1526277698630519676[7] = 0;
   out_1526277698630519676[8] = 0;
}
void h_31(double *state, double *unused, double *out_3605000760603672068) {
   out_3605000760603672068[0] = state[8];
}
void H_31(double *state, double *unused, double *out_7789956410319324924) {
   out_7789956410319324924[0] = 0;
   out_7789956410319324924[1] = 0;
   out_7789956410319324924[2] = 0;
   out_7789956410319324924[3] = 0;
   out_7789956410319324924[4] = 0;
   out_7789956410319324924[5] = 0;
   out_7789956410319324924[6] = 0;
   out_7789956410319324924[7] = 0;
   out_7789956410319324924[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_3178351787780867479) {
  err_fun(nom_x, delta_x, out_3178351787780867479);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_6240253129487023512) {
  inv_err_fun(nom_x, true_x, out_6240253129487023512);
}
void car_H_mod_fun(double *state, double *out_7483116987311173272) {
  H_mod_fun(state, out_7483116987311173272);
}
void car_f_fun(double *state, double dt, double *out_5651695903721239210) {
  f_fun(state,  dt, out_5651695903721239210);
}
void car_F_fun(double *state, double dt, double *out_13263414419101982) {
  F_fun(state,  dt, out_13263414419101982);
}
void car_h_25(double *state, double *unused, double *out_4287938734280851291) {
  h_25(state, unused, out_4287938734280851291);
}
void car_H_25(double *state, double *unused, double *out_7820602372196285352) {
  H_25(state, unused, out_7820602372196285352);
}
void car_h_24(double *state, double *unused, double *out_967862149043042631) {
  h_24(state, unused, out_967862149043042631);
}
void car_H_24(double *state, double *unused, double *out_402210738519358459) {
  H_24(state, unused, out_402210738519358459);
}
void car_h_30(double *state, double *unused, double *out_4012744671996345402) {
  h_30(state, unused, out_4012744671996345402);
}
void car_H_30(double *state, double *unused, double *out_7949941319339525422) {
  H_30(state, unused, out_7949941319339525422);
}
void car_h_26(double *state, double *unused, double *out_3069234819094682967) {
  h_26(state, unused, out_3069234819094682967);
}
void car_H_26(double *state, double *unused, double *out_6884638382639210040) {
  H_26(state, unused, out_6884638382639210040);
}
void car_h_27(double *state, double *unused, double *out_7156042635635634546) {
  h_27(state, unused, out_7156042635635634546);
}
void car_H_27(double *state, double *unused, double *out_8322039442569601283) {
  H_27(state, unused, out_8322039442569601283);
}
void car_h_29(double *state, double *unused, double *out_3409428787319867885) {
  h_29(state, unused, out_3409428787319867885);
}
void car_H_29(double *state, double *unused, double *out_6608676715700050250) {
  H_29(state, unused, out_6608676715700050250);
}
void car_h_28(double *state, double *unused, double *out_976713301355686606) {
  h_28(state, unused, out_976713301355686606);
}
void car_H_28(double *state, double *unused, double *out_1526277698630519676) {
  H_28(state, unused, out_1526277698630519676);
}
void car_h_31(double *state, double *unused, double *out_3605000760603672068) {
  h_31(state, unused, out_3605000760603672068);
}
void car_H_31(double *state, double *unused, double *out_7789956410319324924) {
  H_31(state, unused, out_7789956410319324924);
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
