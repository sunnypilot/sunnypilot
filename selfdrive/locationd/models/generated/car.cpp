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
void err_fun(double *nom_x, double *delta_x, double *out_218205740670826108) {
   out_218205740670826108[0] = delta_x[0] + nom_x[0];
   out_218205740670826108[1] = delta_x[1] + nom_x[1];
   out_218205740670826108[2] = delta_x[2] + nom_x[2];
   out_218205740670826108[3] = delta_x[3] + nom_x[3];
   out_218205740670826108[4] = delta_x[4] + nom_x[4];
   out_218205740670826108[5] = delta_x[5] + nom_x[5];
   out_218205740670826108[6] = delta_x[6] + nom_x[6];
   out_218205740670826108[7] = delta_x[7] + nom_x[7];
   out_218205740670826108[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_4568867566118868017) {
   out_4568867566118868017[0] = -nom_x[0] + true_x[0];
   out_4568867566118868017[1] = -nom_x[1] + true_x[1];
   out_4568867566118868017[2] = -nom_x[2] + true_x[2];
   out_4568867566118868017[3] = -nom_x[3] + true_x[3];
   out_4568867566118868017[4] = -nom_x[4] + true_x[4];
   out_4568867566118868017[5] = -nom_x[5] + true_x[5];
   out_4568867566118868017[6] = -nom_x[6] + true_x[6];
   out_4568867566118868017[7] = -nom_x[7] + true_x[7];
   out_4568867566118868017[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_5579606029964835433) {
   out_5579606029964835433[0] = 1.0;
   out_5579606029964835433[1] = 0;
   out_5579606029964835433[2] = 0;
   out_5579606029964835433[3] = 0;
   out_5579606029964835433[4] = 0;
   out_5579606029964835433[5] = 0;
   out_5579606029964835433[6] = 0;
   out_5579606029964835433[7] = 0;
   out_5579606029964835433[8] = 0;
   out_5579606029964835433[9] = 0;
   out_5579606029964835433[10] = 1.0;
   out_5579606029964835433[11] = 0;
   out_5579606029964835433[12] = 0;
   out_5579606029964835433[13] = 0;
   out_5579606029964835433[14] = 0;
   out_5579606029964835433[15] = 0;
   out_5579606029964835433[16] = 0;
   out_5579606029964835433[17] = 0;
   out_5579606029964835433[18] = 0;
   out_5579606029964835433[19] = 0;
   out_5579606029964835433[20] = 1.0;
   out_5579606029964835433[21] = 0;
   out_5579606029964835433[22] = 0;
   out_5579606029964835433[23] = 0;
   out_5579606029964835433[24] = 0;
   out_5579606029964835433[25] = 0;
   out_5579606029964835433[26] = 0;
   out_5579606029964835433[27] = 0;
   out_5579606029964835433[28] = 0;
   out_5579606029964835433[29] = 0;
   out_5579606029964835433[30] = 1.0;
   out_5579606029964835433[31] = 0;
   out_5579606029964835433[32] = 0;
   out_5579606029964835433[33] = 0;
   out_5579606029964835433[34] = 0;
   out_5579606029964835433[35] = 0;
   out_5579606029964835433[36] = 0;
   out_5579606029964835433[37] = 0;
   out_5579606029964835433[38] = 0;
   out_5579606029964835433[39] = 0;
   out_5579606029964835433[40] = 1.0;
   out_5579606029964835433[41] = 0;
   out_5579606029964835433[42] = 0;
   out_5579606029964835433[43] = 0;
   out_5579606029964835433[44] = 0;
   out_5579606029964835433[45] = 0;
   out_5579606029964835433[46] = 0;
   out_5579606029964835433[47] = 0;
   out_5579606029964835433[48] = 0;
   out_5579606029964835433[49] = 0;
   out_5579606029964835433[50] = 1.0;
   out_5579606029964835433[51] = 0;
   out_5579606029964835433[52] = 0;
   out_5579606029964835433[53] = 0;
   out_5579606029964835433[54] = 0;
   out_5579606029964835433[55] = 0;
   out_5579606029964835433[56] = 0;
   out_5579606029964835433[57] = 0;
   out_5579606029964835433[58] = 0;
   out_5579606029964835433[59] = 0;
   out_5579606029964835433[60] = 1.0;
   out_5579606029964835433[61] = 0;
   out_5579606029964835433[62] = 0;
   out_5579606029964835433[63] = 0;
   out_5579606029964835433[64] = 0;
   out_5579606029964835433[65] = 0;
   out_5579606029964835433[66] = 0;
   out_5579606029964835433[67] = 0;
   out_5579606029964835433[68] = 0;
   out_5579606029964835433[69] = 0;
   out_5579606029964835433[70] = 1.0;
   out_5579606029964835433[71] = 0;
   out_5579606029964835433[72] = 0;
   out_5579606029964835433[73] = 0;
   out_5579606029964835433[74] = 0;
   out_5579606029964835433[75] = 0;
   out_5579606029964835433[76] = 0;
   out_5579606029964835433[77] = 0;
   out_5579606029964835433[78] = 0;
   out_5579606029964835433[79] = 0;
   out_5579606029964835433[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_661179480090036700) {
   out_661179480090036700[0] = state[0];
   out_661179480090036700[1] = state[1];
   out_661179480090036700[2] = state[2];
   out_661179480090036700[3] = state[3];
   out_661179480090036700[4] = state[4];
   out_661179480090036700[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8000000000000007*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_661179480090036700[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_661179480090036700[7] = state[7];
   out_661179480090036700[8] = state[8];
}
void F_fun(double *state, double dt, double *out_3757571913489682424) {
   out_3757571913489682424[0] = 1;
   out_3757571913489682424[1] = 0;
   out_3757571913489682424[2] = 0;
   out_3757571913489682424[3] = 0;
   out_3757571913489682424[4] = 0;
   out_3757571913489682424[5] = 0;
   out_3757571913489682424[6] = 0;
   out_3757571913489682424[7] = 0;
   out_3757571913489682424[8] = 0;
   out_3757571913489682424[9] = 0;
   out_3757571913489682424[10] = 1;
   out_3757571913489682424[11] = 0;
   out_3757571913489682424[12] = 0;
   out_3757571913489682424[13] = 0;
   out_3757571913489682424[14] = 0;
   out_3757571913489682424[15] = 0;
   out_3757571913489682424[16] = 0;
   out_3757571913489682424[17] = 0;
   out_3757571913489682424[18] = 0;
   out_3757571913489682424[19] = 0;
   out_3757571913489682424[20] = 1;
   out_3757571913489682424[21] = 0;
   out_3757571913489682424[22] = 0;
   out_3757571913489682424[23] = 0;
   out_3757571913489682424[24] = 0;
   out_3757571913489682424[25] = 0;
   out_3757571913489682424[26] = 0;
   out_3757571913489682424[27] = 0;
   out_3757571913489682424[28] = 0;
   out_3757571913489682424[29] = 0;
   out_3757571913489682424[30] = 1;
   out_3757571913489682424[31] = 0;
   out_3757571913489682424[32] = 0;
   out_3757571913489682424[33] = 0;
   out_3757571913489682424[34] = 0;
   out_3757571913489682424[35] = 0;
   out_3757571913489682424[36] = 0;
   out_3757571913489682424[37] = 0;
   out_3757571913489682424[38] = 0;
   out_3757571913489682424[39] = 0;
   out_3757571913489682424[40] = 1;
   out_3757571913489682424[41] = 0;
   out_3757571913489682424[42] = 0;
   out_3757571913489682424[43] = 0;
   out_3757571913489682424[44] = 0;
   out_3757571913489682424[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_3757571913489682424[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_3757571913489682424[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_3757571913489682424[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_3757571913489682424[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_3757571913489682424[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_3757571913489682424[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_3757571913489682424[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_3757571913489682424[53] = -9.8000000000000007*dt;
   out_3757571913489682424[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_3757571913489682424[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_3757571913489682424[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_3757571913489682424[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_3757571913489682424[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_3757571913489682424[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_3757571913489682424[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_3757571913489682424[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_3757571913489682424[62] = 0;
   out_3757571913489682424[63] = 0;
   out_3757571913489682424[64] = 0;
   out_3757571913489682424[65] = 0;
   out_3757571913489682424[66] = 0;
   out_3757571913489682424[67] = 0;
   out_3757571913489682424[68] = 0;
   out_3757571913489682424[69] = 0;
   out_3757571913489682424[70] = 1;
   out_3757571913489682424[71] = 0;
   out_3757571913489682424[72] = 0;
   out_3757571913489682424[73] = 0;
   out_3757571913489682424[74] = 0;
   out_3757571913489682424[75] = 0;
   out_3757571913489682424[76] = 0;
   out_3757571913489682424[77] = 0;
   out_3757571913489682424[78] = 0;
   out_3757571913489682424[79] = 0;
   out_3757571913489682424[80] = 1;
}
void h_25(double *state, double *unused, double *out_6425695131840469157) {
   out_6425695131840469157[0] = state[6];
}
void H_25(double *state, double *unused, double *out_3708933076406995603) {
   out_3708933076406995603[0] = 0;
   out_3708933076406995603[1] = 0;
   out_3708933076406995603[2] = 0;
   out_3708933076406995603[3] = 0;
   out_3708933076406995603[4] = 0;
   out_3708933076406995603[5] = 0;
   out_3708933076406995603[6] = 1;
   out_3708933076406995603[7] = 0;
   out_3708933076406995603[8] = 0;
}
void h_24(double *state, double *unused, double *out_6311602043493232022) {
   out_6311602043493232022[0] = state[4];
   out_6311602043493232022[1] = state[5];
}
void H_24(double *state, double *unused, double *out_7594207551456324474) {
   out_7594207551456324474[0] = 0;
   out_7594207551456324474[1] = 0;
   out_7594207551456324474[2] = 0;
   out_7594207551456324474[3] = 0;
   out_7594207551456324474[4] = 1;
   out_7594207551456324474[5] = 0;
   out_7594207551456324474[6] = 0;
   out_7594207551456324474[7] = 0;
   out_7594207551456324474[8] = 0;
   out_7594207551456324474[9] = 0;
   out_7594207551456324474[10] = 0;
   out_7594207551456324474[11] = 0;
   out_7594207551456324474[12] = 0;
   out_7594207551456324474[13] = 0;
   out_7594207551456324474[14] = 1;
   out_7594207551456324474[15] = 0;
   out_7594207551456324474[16] = 0;
   out_7594207551456324474[17] = 0;
}
void h_30(double *state, double *unused, double *out_4257783685048410018) {
   out_4257783685048410018[0] = state[4];
}
void H_30(double *state, double *unused, double *out_818763253720612595) {
   out_818763253720612595[0] = 0;
   out_818763253720612595[1] = 0;
   out_818763253720612595[2] = 0;
   out_818763253720612595[3] = 0;
   out_818763253720612595[4] = 1;
   out_818763253720612595[5] = 0;
   out_818763253720612595[6] = 0;
   out_818763253720612595[7] = 0;
   out_818763253720612595[8] = 0;
}
void h_26(double *state, double *unused, double *out_4927687678159242457) {
   out_4927687678159242457[0] = state[7];
}
void H_26(double *state, double *unused, double *out_32570242467060621) {
   out_32570242467060621[0] = 0;
   out_32570242467060621[1] = 0;
   out_32570242467060621[2] = 0;
   out_32570242467060621[3] = 0;
   out_32570242467060621[4] = 0;
   out_32570242467060621[5] = 0;
   out_32570242467060621[6] = 0;
   out_32570242467060621[7] = 1;
   out_32570242467060621[8] = 0;
}
void h_27(double *state, double *unused, double *out_8840331268697770696) {
   out_8840331268697770696[0] = state[3];
}
void H_27(double *state, double *unused, double *out_1404830817463330622) {
   out_1404830817463330622[0] = 0;
   out_1404830817463330622[1] = 0;
   out_1404830817463330622[2] = 0;
   out_1404830817463330622[3] = 1;
   out_1404830817463330622[4] = 0;
   out_1404830817463330622[5] = 0;
   out_1404830817463330622[6] = 0;
   out_1404830817463330622[7] = 0;
   out_1404830817463330622[8] = 0;
}
void h_29(double *state, double *unused, double *out_3314273832146747583) {
   out_3314273832146747583[0] = state[1];
}
void H_29(double *state, double *unused, double *out_308531909406220411) {
   out_308531909406220411[0] = 0;
   out_308531909406220411[1] = 1;
   out_308531909406220411[2] = 0;
   out_308531909406220411[3] = 0;
   out_308531909406220411[4] = 0;
   out_308531909406220411[5] = 0;
   out_308531909406220411[6] = 0;
   out_308531909406220411[7] = 0;
   out_308531909406220411[8] = 0;
}
void h_28(double *state, double *unused, double *out_3359961747551607452) {
   out_3359961747551607452[0] = state[0];
}
void H_28(double *state, double *unused, double *out_5390930926475750985) {
   out_5390930926475750985[0] = 1;
   out_5390930926475750985[1] = 0;
   out_5390930926475750985[2] = 0;
   out_5390930926475750985[3] = 0;
   out_5390930926475750985[4] = 0;
   out_5390930926475750985[5] = 0;
   out_5390930926475750985[6] = 0;
   out_5390930926475750985[7] = 0;
   out_5390930926475750985[8] = 0;
}
void h_31(double *state, double *unused, double *out_6465333577647216793) {
   out_6465333577647216793[0] = state[8];
}
void H_31(double *state, double *unused, double *out_658778344700412097) {
   out_658778344700412097[0] = 0;
   out_658778344700412097[1] = 0;
   out_658778344700412097[2] = 0;
   out_658778344700412097[3] = 0;
   out_658778344700412097[4] = 0;
   out_658778344700412097[5] = 0;
   out_658778344700412097[6] = 0;
   out_658778344700412097[7] = 0;
   out_658778344700412097[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_218205740670826108) {
  err_fun(nom_x, delta_x, out_218205740670826108);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_4568867566118868017) {
  inv_err_fun(nom_x, true_x, out_4568867566118868017);
}
void car_H_mod_fun(double *state, double *out_5579606029964835433) {
  H_mod_fun(state, out_5579606029964835433);
}
void car_f_fun(double *state, double dt, double *out_661179480090036700) {
  f_fun(state,  dt, out_661179480090036700);
}
void car_F_fun(double *state, double dt, double *out_3757571913489682424) {
  F_fun(state,  dt, out_3757571913489682424);
}
void car_h_25(double *state, double *unused, double *out_6425695131840469157) {
  h_25(state, unused, out_6425695131840469157);
}
void car_H_25(double *state, double *unused, double *out_3708933076406995603) {
  H_25(state, unused, out_3708933076406995603);
}
void car_h_24(double *state, double *unused, double *out_6311602043493232022) {
  h_24(state, unused, out_6311602043493232022);
}
void car_H_24(double *state, double *unused, double *out_7594207551456324474) {
  H_24(state, unused, out_7594207551456324474);
}
void car_h_30(double *state, double *unused, double *out_4257783685048410018) {
  h_30(state, unused, out_4257783685048410018);
}
void car_H_30(double *state, double *unused, double *out_818763253720612595) {
  H_30(state, unused, out_818763253720612595);
}
void car_h_26(double *state, double *unused, double *out_4927687678159242457) {
  h_26(state, unused, out_4927687678159242457);
}
void car_H_26(double *state, double *unused, double *out_32570242467060621) {
  H_26(state, unused, out_32570242467060621);
}
void car_h_27(double *state, double *unused, double *out_8840331268697770696) {
  h_27(state, unused, out_8840331268697770696);
}
void car_H_27(double *state, double *unused, double *out_1404830817463330622) {
  H_27(state, unused, out_1404830817463330622);
}
void car_h_29(double *state, double *unused, double *out_3314273832146747583) {
  h_29(state, unused, out_3314273832146747583);
}
void car_H_29(double *state, double *unused, double *out_308531909406220411) {
  H_29(state, unused, out_308531909406220411);
}
void car_h_28(double *state, double *unused, double *out_3359961747551607452) {
  h_28(state, unused, out_3359961747551607452);
}
void car_H_28(double *state, double *unused, double *out_5390930926475750985) {
  H_28(state, unused, out_5390930926475750985);
}
void car_h_31(double *state, double *unused, double *out_6465333577647216793) {
  h_31(state, unused, out_6465333577647216793);
}
void car_H_31(double *state, double *unused, double *out_658778344700412097) {
  H_31(state, unused, out_658778344700412097);
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
