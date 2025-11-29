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
void err_fun(double *nom_x, double *delta_x, double *out_2505009923289236322) {
   out_2505009923289236322[0] = delta_x[0] + nom_x[0];
   out_2505009923289236322[1] = delta_x[1] + nom_x[1];
   out_2505009923289236322[2] = delta_x[2] + nom_x[2];
   out_2505009923289236322[3] = delta_x[3] + nom_x[3];
   out_2505009923289236322[4] = delta_x[4] + nom_x[4];
   out_2505009923289236322[5] = delta_x[5] + nom_x[5];
   out_2505009923289236322[6] = delta_x[6] + nom_x[6];
   out_2505009923289236322[7] = delta_x[7] + nom_x[7];
   out_2505009923289236322[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_693928023623824221) {
   out_693928023623824221[0] = -nom_x[0] + true_x[0];
   out_693928023623824221[1] = -nom_x[1] + true_x[1];
   out_693928023623824221[2] = -nom_x[2] + true_x[2];
   out_693928023623824221[3] = -nom_x[3] + true_x[3];
   out_693928023623824221[4] = -nom_x[4] + true_x[4];
   out_693928023623824221[5] = -nom_x[5] + true_x[5];
   out_693928023623824221[6] = -nom_x[6] + true_x[6];
   out_693928023623824221[7] = -nom_x[7] + true_x[7];
   out_693928023623824221[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_4242968391530992008) {
   out_4242968391530992008[0] = 1.0;
   out_4242968391530992008[1] = 0.0;
   out_4242968391530992008[2] = 0.0;
   out_4242968391530992008[3] = 0.0;
   out_4242968391530992008[4] = 0.0;
   out_4242968391530992008[5] = 0.0;
   out_4242968391530992008[6] = 0.0;
   out_4242968391530992008[7] = 0.0;
   out_4242968391530992008[8] = 0.0;
   out_4242968391530992008[9] = 0.0;
   out_4242968391530992008[10] = 1.0;
   out_4242968391530992008[11] = 0.0;
   out_4242968391530992008[12] = 0.0;
   out_4242968391530992008[13] = 0.0;
   out_4242968391530992008[14] = 0.0;
   out_4242968391530992008[15] = 0.0;
   out_4242968391530992008[16] = 0.0;
   out_4242968391530992008[17] = 0.0;
   out_4242968391530992008[18] = 0.0;
   out_4242968391530992008[19] = 0.0;
   out_4242968391530992008[20] = 1.0;
   out_4242968391530992008[21] = 0.0;
   out_4242968391530992008[22] = 0.0;
   out_4242968391530992008[23] = 0.0;
   out_4242968391530992008[24] = 0.0;
   out_4242968391530992008[25] = 0.0;
   out_4242968391530992008[26] = 0.0;
   out_4242968391530992008[27] = 0.0;
   out_4242968391530992008[28] = 0.0;
   out_4242968391530992008[29] = 0.0;
   out_4242968391530992008[30] = 1.0;
   out_4242968391530992008[31] = 0.0;
   out_4242968391530992008[32] = 0.0;
   out_4242968391530992008[33] = 0.0;
   out_4242968391530992008[34] = 0.0;
   out_4242968391530992008[35] = 0.0;
   out_4242968391530992008[36] = 0.0;
   out_4242968391530992008[37] = 0.0;
   out_4242968391530992008[38] = 0.0;
   out_4242968391530992008[39] = 0.0;
   out_4242968391530992008[40] = 1.0;
   out_4242968391530992008[41] = 0.0;
   out_4242968391530992008[42] = 0.0;
   out_4242968391530992008[43] = 0.0;
   out_4242968391530992008[44] = 0.0;
   out_4242968391530992008[45] = 0.0;
   out_4242968391530992008[46] = 0.0;
   out_4242968391530992008[47] = 0.0;
   out_4242968391530992008[48] = 0.0;
   out_4242968391530992008[49] = 0.0;
   out_4242968391530992008[50] = 1.0;
   out_4242968391530992008[51] = 0.0;
   out_4242968391530992008[52] = 0.0;
   out_4242968391530992008[53] = 0.0;
   out_4242968391530992008[54] = 0.0;
   out_4242968391530992008[55] = 0.0;
   out_4242968391530992008[56] = 0.0;
   out_4242968391530992008[57] = 0.0;
   out_4242968391530992008[58] = 0.0;
   out_4242968391530992008[59] = 0.0;
   out_4242968391530992008[60] = 1.0;
   out_4242968391530992008[61] = 0.0;
   out_4242968391530992008[62] = 0.0;
   out_4242968391530992008[63] = 0.0;
   out_4242968391530992008[64] = 0.0;
   out_4242968391530992008[65] = 0.0;
   out_4242968391530992008[66] = 0.0;
   out_4242968391530992008[67] = 0.0;
   out_4242968391530992008[68] = 0.0;
   out_4242968391530992008[69] = 0.0;
   out_4242968391530992008[70] = 1.0;
   out_4242968391530992008[71] = 0.0;
   out_4242968391530992008[72] = 0.0;
   out_4242968391530992008[73] = 0.0;
   out_4242968391530992008[74] = 0.0;
   out_4242968391530992008[75] = 0.0;
   out_4242968391530992008[76] = 0.0;
   out_4242968391530992008[77] = 0.0;
   out_4242968391530992008[78] = 0.0;
   out_4242968391530992008[79] = 0.0;
   out_4242968391530992008[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_1159864094741656085) {
   out_1159864094741656085[0] = state[0];
   out_1159864094741656085[1] = state[1];
   out_1159864094741656085[2] = state[2];
   out_1159864094741656085[3] = state[3];
   out_1159864094741656085[4] = state[4];
   out_1159864094741656085[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8100000000000005*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_1159864094741656085[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_1159864094741656085[7] = state[7];
   out_1159864094741656085[8] = state[8];
}
void F_fun(double *state, double dt, double *out_8150880409629162514) {
   out_8150880409629162514[0] = 1;
   out_8150880409629162514[1] = 0;
   out_8150880409629162514[2] = 0;
   out_8150880409629162514[3] = 0;
   out_8150880409629162514[4] = 0;
   out_8150880409629162514[5] = 0;
   out_8150880409629162514[6] = 0;
   out_8150880409629162514[7] = 0;
   out_8150880409629162514[8] = 0;
   out_8150880409629162514[9] = 0;
   out_8150880409629162514[10] = 1;
   out_8150880409629162514[11] = 0;
   out_8150880409629162514[12] = 0;
   out_8150880409629162514[13] = 0;
   out_8150880409629162514[14] = 0;
   out_8150880409629162514[15] = 0;
   out_8150880409629162514[16] = 0;
   out_8150880409629162514[17] = 0;
   out_8150880409629162514[18] = 0;
   out_8150880409629162514[19] = 0;
   out_8150880409629162514[20] = 1;
   out_8150880409629162514[21] = 0;
   out_8150880409629162514[22] = 0;
   out_8150880409629162514[23] = 0;
   out_8150880409629162514[24] = 0;
   out_8150880409629162514[25] = 0;
   out_8150880409629162514[26] = 0;
   out_8150880409629162514[27] = 0;
   out_8150880409629162514[28] = 0;
   out_8150880409629162514[29] = 0;
   out_8150880409629162514[30] = 1;
   out_8150880409629162514[31] = 0;
   out_8150880409629162514[32] = 0;
   out_8150880409629162514[33] = 0;
   out_8150880409629162514[34] = 0;
   out_8150880409629162514[35] = 0;
   out_8150880409629162514[36] = 0;
   out_8150880409629162514[37] = 0;
   out_8150880409629162514[38] = 0;
   out_8150880409629162514[39] = 0;
   out_8150880409629162514[40] = 1;
   out_8150880409629162514[41] = 0;
   out_8150880409629162514[42] = 0;
   out_8150880409629162514[43] = 0;
   out_8150880409629162514[44] = 0;
   out_8150880409629162514[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_8150880409629162514[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_8150880409629162514[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_8150880409629162514[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_8150880409629162514[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_8150880409629162514[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_8150880409629162514[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_8150880409629162514[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_8150880409629162514[53] = -9.8100000000000005*dt;
   out_8150880409629162514[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_8150880409629162514[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_8150880409629162514[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_8150880409629162514[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_8150880409629162514[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_8150880409629162514[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_8150880409629162514[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_8150880409629162514[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_8150880409629162514[62] = 0;
   out_8150880409629162514[63] = 0;
   out_8150880409629162514[64] = 0;
   out_8150880409629162514[65] = 0;
   out_8150880409629162514[66] = 0;
   out_8150880409629162514[67] = 0;
   out_8150880409629162514[68] = 0;
   out_8150880409629162514[69] = 0;
   out_8150880409629162514[70] = 1;
   out_8150880409629162514[71] = 0;
   out_8150880409629162514[72] = 0;
   out_8150880409629162514[73] = 0;
   out_8150880409629162514[74] = 0;
   out_8150880409629162514[75] = 0;
   out_8150880409629162514[76] = 0;
   out_8150880409629162514[77] = 0;
   out_8150880409629162514[78] = 0;
   out_8150880409629162514[79] = 0;
   out_8150880409629162514[80] = 1;
}
void h_25(double *state, double *unused, double *out_1560242497889987579) {
   out_1560242497889987579[0] = state[6];
}
void H_25(double *state, double *unused, double *out_7765949041520483685) {
   out_7765949041520483685[0] = 0;
   out_7765949041520483685[1] = 0;
   out_7765949041520483685[2] = 0;
   out_7765949041520483685[3] = 0;
   out_7765949041520483685[4] = 0;
   out_7765949041520483685[5] = 0;
   out_7765949041520483685[6] = 1;
   out_7765949041520483685[7] = 0;
   out_7765949041520483685[8] = 0;
}
void h_24(double *state, double *unused, double *out_440354277390915404) {
   out_440354277390915404[0] = state[4];
   out_440354277390915404[1] = state[5];
}
void H_24(double *state, double *unused, double *out_7122869433386744795) {
   out_7122869433386744795[0] = 0;
   out_7122869433386744795[1] = 0;
   out_7122869433386744795[2] = 0;
   out_7122869433386744795[3] = 0;
   out_7122869433386744795[4] = 1;
   out_7122869433386744795[5] = 0;
   out_7122869433386744795[6] = 0;
   out_7122869433386744795[7] = 0;
   out_7122869433386744795[8] = 0;
   out_7122869433386744795[9] = 0;
   out_7122869433386744795[10] = 0;
   out_7122869433386744795[11] = 0;
   out_7122869433386744795[12] = 0;
   out_7122869433386744795[13] = 0;
   out_7122869433386744795[14] = 1;
   out_7122869433386744795[15] = 0;
   out_7122869433386744795[16] = 0;
   out_7122869433386744795[17] = 0;
}
void h_30(double *state, double *unused, double *out_8148070424366282742) {
   out_8148070424366282742[0] = state[4];
}
void H_30(double *state, double *unused, double *out_3238252711392875487) {
   out_3238252711392875487[0] = 0;
   out_3238252711392875487[1] = 0;
   out_3238252711392875487[2] = 0;
   out_3238252711392875487[3] = 0;
   out_3238252711392875487[4] = 1;
   out_3238252711392875487[5] = 0;
   out_3238252711392875487[6] = 0;
   out_3238252711392875487[7] = 0;
   out_3238252711392875487[8] = 0;
}
void h_26(double *state, double *unused, double *out_4540688735349530918) {
   out_4540688735349530918[0] = state[7];
}
void H_26(double *state, double *unused, double *out_4024445722646427461) {
   out_4024445722646427461[0] = 0;
   out_4024445722646427461[1] = 0;
   out_4024445722646427461[2] = 0;
   out_4024445722646427461[3] = 0;
   out_4024445722646427461[4] = 0;
   out_4024445722646427461[5] = 0;
   out_4024445722646427461[6] = 0;
   out_4024445722646427461[7] = 1;
   out_4024445722646427461[8] = 0;
}
void h_27(double *state, double *unused, double *out_628045144811002679) {
   out_628045144811002679[0] = state[3];
}
void H_27(double *state, double *unused, double *out_5461846782576818704) {
   out_5461846782576818704[0] = 0;
   out_5461846782576818704[1] = 0;
   out_5461846782576818704[2] = 0;
   out_5461846782576818704[3] = 1;
   out_5461846782576818704[4] = 0;
   out_5461846782576818704[5] = 0;
   out_5461846782576818704[6] = 0;
   out_5461846782576818704[7] = 0;
   out_5461846782576818704[8] = 0;
}
void h_29(double *state, double *unused, double *out_5297000381682423229) {
   out_5297000381682423229[0] = state[1];
}
void H_29(double *state, double *unused, double *out_3748484055707267671) {
   out_3748484055707267671[0] = 0;
   out_3748484055707267671[1] = 1;
   out_3748484055707267671[2] = 0;
   out_3748484055707267671[3] = 0;
   out_3748484055707267671[4] = 0;
   out_3748484055707267671[5] = 0;
   out_3748484055707267671[6] = 0;
   out_3748484055707267671[7] = 0;
   out_3748484055707267671[8] = 0;
}
void h_28(double *state, double *unused, double *out_6386030058804740635) {
   out_6386030058804740635[0] = state[0];
}
void H_28(double *state, double *unused, double *out_1333914961362262903) {
   out_1333914961362262903[0] = 1;
   out_1333914961362262903[1] = 0;
   out_1333914961362262903[2] = 0;
   out_1333914961362262903[3] = 0;
   out_1333914961362262903[4] = 0;
   out_1333914961362262903[5] = 0;
   out_1333914961362262903[6] = 0;
   out_1333914961362262903[7] = 0;
   out_1333914961362262903[8] = 0;
}
void h_31(double *state, double *unused, double *out_2680928216743251404) {
   out_2680928216743251404[0] = state[8];
}
void H_31(double *state, double *unused, double *out_7796595003397444113) {
   out_7796595003397444113[0] = 0;
   out_7796595003397444113[1] = 0;
   out_7796595003397444113[2] = 0;
   out_7796595003397444113[3] = 0;
   out_7796595003397444113[4] = 0;
   out_7796595003397444113[5] = 0;
   out_7796595003397444113[6] = 0;
   out_7796595003397444113[7] = 0;
   out_7796595003397444113[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_2505009923289236322) {
  err_fun(nom_x, delta_x, out_2505009923289236322);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_693928023623824221) {
  inv_err_fun(nom_x, true_x, out_693928023623824221);
}
void car_H_mod_fun(double *state, double *out_4242968391530992008) {
  H_mod_fun(state, out_4242968391530992008);
}
void car_f_fun(double *state, double dt, double *out_1159864094741656085) {
  f_fun(state,  dt, out_1159864094741656085);
}
void car_F_fun(double *state, double dt, double *out_8150880409629162514) {
  F_fun(state,  dt, out_8150880409629162514);
}
void car_h_25(double *state, double *unused, double *out_1560242497889987579) {
  h_25(state, unused, out_1560242497889987579);
}
void car_H_25(double *state, double *unused, double *out_7765949041520483685) {
  H_25(state, unused, out_7765949041520483685);
}
void car_h_24(double *state, double *unused, double *out_440354277390915404) {
  h_24(state, unused, out_440354277390915404);
}
void car_H_24(double *state, double *unused, double *out_7122869433386744795) {
  H_24(state, unused, out_7122869433386744795);
}
void car_h_30(double *state, double *unused, double *out_8148070424366282742) {
  h_30(state, unused, out_8148070424366282742);
}
void car_H_30(double *state, double *unused, double *out_3238252711392875487) {
  H_30(state, unused, out_3238252711392875487);
}
void car_h_26(double *state, double *unused, double *out_4540688735349530918) {
  h_26(state, unused, out_4540688735349530918);
}
void car_H_26(double *state, double *unused, double *out_4024445722646427461) {
  H_26(state, unused, out_4024445722646427461);
}
void car_h_27(double *state, double *unused, double *out_628045144811002679) {
  h_27(state, unused, out_628045144811002679);
}
void car_H_27(double *state, double *unused, double *out_5461846782576818704) {
  H_27(state, unused, out_5461846782576818704);
}
void car_h_29(double *state, double *unused, double *out_5297000381682423229) {
  h_29(state, unused, out_5297000381682423229);
}
void car_H_29(double *state, double *unused, double *out_3748484055707267671) {
  H_29(state, unused, out_3748484055707267671);
}
void car_h_28(double *state, double *unused, double *out_6386030058804740635) {
  h_28(state, unused, out_6386030058804740635);
}
void car_H_28(double *state, double *unused, double *out_1333914961362262903) {
  H_28(state, unused, out_1333914961362262903);
}
void car_h_31(double *state, double *unused, double *out_2680928216743251404) {
  h_31(state, unused, out_2680928216743251404);
}
void car_H_31(double *state, double *unused, double *out_7796595003397444113) {
  H_31(state, unused, out_7796595003397444113);
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
