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
void err_fun(double *nom_x, double *delta_x, double *out_5059320499403781563) {
   out_5059320499403781563[0] = delta_x[0] + nom_x[0];
   out_5059320499403781563[1] = delta_x[1] + nom_x[1];
   out_5059320499403781563[2] = delta_x[2] + nom_x[2];
   out_5059320499403781563[3] = delta_x[3] + nom_x[3];
   out_5059320499403781563[4] = delta_x[4] + nom_x[4];
   out_5059320499403781563[5] = delta_x[5] + nom_x[5];
   out_5059320499403781563[6] = delta_x[6] + nom_x[6];
   out_5059320499403781563[7] = delta_x[7] + nom_x[7];
   out_5059320499403781563[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_8028694691748550712) {
   out_8028694691748550712[0] = -nom_x[0] + true_x[0];
   out_8028694691748550712[1] = -nom_x[1] + true_x[1];
   out_8028694691748550712[2] = -nom_x[2] + true_x[2];
   out_8028694691748550712[3] = -nom_x[3] + true_x[3];
   out_8028694691748550712[4] = -nom_x[4] + true_x[4];
   out_8028694691748550712[5] = -nom_x[5] + true_x[5];
   out_8028694691748550712[6] = -nom_x[6] + true_x[6];
   out_8028694691748550712[7] = -nom_x[7] + true_x[7];
   out_8028694691748550712[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_1011613483250515043) {
   out_1011613483250515043[0] = 1.0;
   out_1011613483250515043[1] = 0.0;
   out_1011613483250515043[2] = 0.0;
   out_1011613483250515043[3] = 0.0;
   out_1011613483250515043[4] = 0.0;
   out_1011613483250515043[5] = 0.0;
   out_1011613483250515043[6] = 0.0;
   out_1011613483250515043[7] = 0.0;
   out_1011613483250515043[8] = 0.0;
   out_1011613483250515043[9] = 0.0;
   out_1011613483250515043[10] = 1.0;
   out_1011613483250515043[11] = 0.0;
   out_1011613483250515043[12] = 0.0;
   out_1011613483250515043[13] = 0.0;
   out_1011613483250515043[14] = 0.0;
   out_1011613483250515043[15] = 0.0;
   out_1011613483250515043[16] = 0.0;
   out_1011613483250515043[17] = 0.0;
   out_1011613483250515043[18] = 0.0;
   out_1011613483250515043[19] = 0.0;
   out_1011613483250515043[20] = 1.0;
   out_1011613483250515043[21] = 0.0;
   out_1011613483250515043[22] = 0.0;
   out_1011613483250515043[23] = 0.0;
   out_1011613483250515043[24] = 0.0;
   out_1011613483250515043[25] = 0.0;
   out_1011613483250515043[26] = 0.0;
   out_1011613483250515043[27] = 0.0;
   out_1011613483250515043[28] = 0.0;
   out_1011613483250515043[29] = 0.0;
   out_1011613483250515043[30] = 1.0;
   out_1011613483250515043[31] = 0.0;
   out_1011613483250515043[32] = 0.0;
   out_1011613483250515043[33] = 0.0;
   out_1011613483250515043[34] = 0.0;
   out_1011613483250515043[35] = 0.0;
   out_1011613483250515043[36] = 0.0;
   out_1011613483250515043[37] = 0.0;
   out_1011613483250515043[38] = 0.0;
   out_1011613483250515043[39] = 0.0;
   out_1011613483250515043[40] = 1.0;
   out_1011613483250515043[41] = 0.0;
   out_1011613483250515043[42] = 0.0;
   out_1011613483250515043[43] = 0.0;
   out_1011613483250515043[44] = 0.0;
   out_1011613483250515043[45] = 0.0;
   out_1011613483250515043[46] = 0.0;
   out_1011613483250515043[47] = 0.0;
   out_1011613483250515043[48] = 0.0;
   out_1011613483250515043[49] = 0.0;
   out_1011613483250515043[50] = 1.0;
   out_1011613483250515043[51] = 0.0;
   out_1011613483250515043[52] = 0.0;
   out_1011613483250515043[53] = 0.0;
   out_1011613483250515043[54] = 0.0;
   out_1011613483250515043[55] = 0.0;
   out_1011613483250515043[56] = 0.0;
   out_1011613483250515043[57] = 0.0;
   out_1011613483250515043[58] = 0.0;
   out_1011613483250515043[59] = 0.0;
   out_1011613483250515043[60] = 1.0;
   out_1011613483250515043[61] = 0.0;
   out_1011613483250515043[62] = 0.0;
   out_1011613483250515043[63] = 0.0;
   out_1011613483250515043[64] = 0.0;
   out_1011613483250515043[65] = 0.0;
   out_1011613483250515043[66] = 0.0;
   out_1011613483250515043[67] = 0.0;
   out_1011613483250515043[68] = 0.0;
   out_1011613483250515043[69] = 0.0;
   out_1011613483250515043[70] = 1.0;
   out_1011613483250515043[71] = 0.0;
   out_1011613483250515043[72] = 0.0;
   out_1011613483250515043[73] = 0.0;
   out_1011613483250515043[74] = 0.0;
   out_1011613483250515043[75] = 0.0;
   out_1011613483250515043[76] = 0.0;
   out_1011613483250515043[77] = 0.0;
   out_1011613483250515043[78] = 0.0;
   out_1011613483250515043[79] = 0.0;
   out_1011613483250515043[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_2197439487468085332) {
   out_2197439487468085332[0] = state[0];
   out_2197439487468085332[1] = state[1];
   out_2197439487468085332[2] = state[2];
   out_2197439487468085332[3] = state[3];
   out_2197439487468085332[4] = state[4];
   out_2197439487468085332[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8100000000000005*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_2197439487468085332[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_2197439487468085332[7] = state[7];
   out_2197439487468085332[8] = state[8];
}
void F_fun(double *state, double dt, double *out_7087540084366041403) {
   out_7087540084366041403[0] = 1;
   out_7087540084366041403[1] = 0;
   out_7087540084366041403[2] = 0;
   out_7087540084366041403[3] = 0;
   out_7087540084366041403[4] = 0;
   out_7087540084366041403[5] = 0;
   out_7087540084366041403[6] = 0;
   out_7087540084366041403[7] = 0;
   out_7087540084366041403[8] = 0;
   out_7087540084366041403[9] = 0;
   out_7087540084366041403[10] = 1;
   out_7087540084366041403[11] = 0;
   out_7087540084366041403[12] = 0;
   out_7087540084366041403[13] = 0;
   out_7087540084366041403[14] = 0;
   out_7087540084366041403[15] = 0;
   out_7087540084366041403[16] = 0;
   out_7087540084366041403[17] = 0;
   out_7087540084366041403[18] = 0;
   out_7087540084366041403[19] = 0;
   out_7087540084366041403[20] = 1;
   out_7087540084366041403[21] = 0;
   out_7087540084366041403[22] = 0;
   out_7087540084366041403[23] = 0;
   out_7087540084366041403[24] = 0;
   out_7087540084366041403[25] = 0;
   out_7087540084366041403[26] = 0;
   out_7087540084366041403[27] = 0;
   out_7087540084366041403[28] = 0;
   out_7087540084366041403[29] = 0;
   out_7087540084366041403[30] = 1;
   out_7087540084366041403[31] = 0;
   out_7087540084366041403[32] = 0;
   out_7087540084366041403[33] = 0;
   out_7087540084366041403[34] = 0;
   out_7087540084366041403[35] = 0;
   out_7087540084366041403[36] = 0;
   out_7087540084366041403[37] = 0;
   out_7087540084366041403[38] = 0;
   out_7087540084366041403[39] = 0;
   out_7087540084366041403[40] = 1;
   out_7087540084366041403[41] = 0;
   out_7087540084366041403[42] = 0;
   out_7087540084366041403[43] = 0;
   out_7087540084366041403[44] = 0;
   out_7087540084366041403[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_7087540084366041403[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_7087540084366041403[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_7087540084366041403[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_7087540084366041403[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_7087540084366041403[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_7087540084366041403[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_7087540084366041403[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_7087540084366041403[53] = -9.8100000000000005*dt;
   out_7087540084366041403[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_7087540084366041403[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_7087540084366041403[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_7087540084366041403[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_7087540084366041403[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_7087540084366041403[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_7087540084366041403[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_7087540084366041403[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_7087540084366041403[62] = 0;
   out_7087540084366041403[63] = 0;
   out_7087540084366041403[64] = 0;
   out_7087540084366041403[65] = 0;
   out_7087540084366041403[66] = 0;
   out_7087540084366041403[67] = 0;
   out_7087540084366041403[68] = 0;
   out_7087540084366041403[69] = 0;
   out_7087540084366041403[70] = 1;
   out_7087540084366041403[71] = 0;
   out_7087540084366041403[72] = 0;
   out_7087540084366041403[73] = 0;
   out_7087540084366041403[74] = 0;
   out_7087540084366041403[75] = 0;
   out_7087540084366041403[76] = 0;
   out_7087540084366041403[77] = 0;
   out_7087540084366041403[78] = 0;
   out_7087540084366041403[79] = 0;
   out_7087540084366041403[80] = 1;
}
void h_25(double *state, double *unused, double *out_7407988264137374316) {
   out_7407988264137374316[0] = state[6];
}
void H_25(double *state, double *unused, double *out_3892078341934149797) {
   out_3892078341934149797[0] = 0;
   out_3892078341934149797[1] = 0;
   out_3892078341934149797[2] = 0;
   out_3892078341934149797[3] = 0;
   out_3892078341934149797[4] = 0;
   out_3892078341934149797[5] = 0;
   out_3892078341934149797[6] = 1;
   out_3892078341934149797[7] = 0;
   out_3892078341934149797[8] = 0;
}
void h_24(double *state, double *unused, double *out_8835218896431103117) {
   out_8835218896431103117[0] = state[4];
   out_8835218896431103117[1] = state[5];
}
void H_24(double *state, double *unused, double *out_2235142160227532400) {
   out_2235142160227532400[0] = 0;
   out_2235142160227532400[1] = 0;
   out_2235142160227532400[2] = 0;
   out_2235142160227532400[3] = 0;
   out_2235142160227532400[4] = 1;
   out_2235142160227532400[5] = 0;
   out_2235142160227532400[6] = 0;
   out_2235142160227532400[7] = 0;
   out_2235142160227532400[8] = 0;
   out_2235142160227532400[9] = 0;
   out_2235142160227532400[10] = 0;
   out_2235142160227532400[11] = 0;
   out_2235142160227532400[12] = 0;
   out_2235142160227532400[13] = 0;
   out_2235142160227532400[14] = 1;
   out_2235142160227532400[15] = 0;
   out_2235142160227532400[16] = 0;
   out_2235142160227532400[17] = 0;
}
void h_30(double *state, double *unused, double *out_7565174932488503461) {
   out_7565174932488503461[0] = state[4];
}
void H_30(double *state, double *unused, double *out_6410411300441398424) {
   out_6410411300441398424[0] = 0;
   out_6410411300441398424[1] = 0;
   out_6410411300441398424[2] = 0;
   out_6410411300441398424[3] = 0;
   out_6410411300441398424[4] = 1;
   out_6410411300441398424[5] = 0;
   out_6410411300441398424[6] = 0;
   out_6410411300441398424[7] = 0;
   out_6410411300441398424[8] = 0;
}
void h_26(double *state, double *unused, double *out_1416794239518337304) {
   out_1416794239518337304[0] = state[7];
}
void H_26(double *state, double *unused, double *out_7196604311694950398) {
   out_7196604311694950398[0] = 0;
   out_7196604311694950398[1] = 0;
   out_7196604311694950398[2] = 0;
   out_7196604311694950398[3] = 0;
   out_7196604311694950398[4] = 0;
   out_7196604311694950398[5] = 0;
   out_7196604311694950398[6] = 0;
   out_7196604311694950398[7] = 1;
   out_7196604311694950398[8] = 0;
}
void h_27(double *state, double *unused, double *out_2406314996476528671) {
   out_2406314996476528671[0] = state[3];
}
void H_27(double *state, double *unused, double *out_8634005371625341641) {
   out_8634005371625341641[0] = 0;
   out_8634005371625341641[1] = 0;
   out_8634005371625341641[2] = 0;
   out_8634005371625341641[3] = 1;
   out_8634005371625341641[4] = 0;
   out_8634005371625341641[5] = 0;
   out_8634005371625341641[6] = 0;
   out_8634005371625341641[7] = 0;
   out_8634005371625341641[8] = 0;
}
void h_29(double *state, double *unused, double *out_8277163820412350504) {
   out_8277163820412350504[0] = state[1];
}
void H_29(double *state, double *unused, double *out_6920642644755790608) {
   out_6920642644755790608[0] = 0;
   out_6920642644755790608[1] = 1;
   out_6920642644755790608[2] = 0;
   out_6920642644755790608[3] = 0;
   out_6920642644755790608[4] = 0;
   out_6920642644755790608[5] = 0;
   out_6920642644755790608[6] = 0;
   out_6920642644755790608[7] = 0;
   out_6920642644755790608[8] = 0;
}
void h_28(double *state, double *unused, double *out_5218867099746382054) {
   out_5218867099746382054[0] = state[0];
}
void H_28(double *state, double *unused, double *out_1838243627686260034) {
   out_1838243627686260034[0] = 1;
   out_1838243627686260034[1] = 0;
   out_1838243627686260034[2] = 0;
   out_1838243627686260034[3] = 0;
   out_1838243627686260034[4] = 0;
   out_1838243627686260034[5] = 0;
   out_1838243627686260034[6] = 0;
   out_1838243627686260034[7] = 0;
   out_1838243627686260034[8] = 0;
}
void h_31(double *state, double *unused, double *out_7683182326421880205) {
   out_7683182326421880205[0] = state[8];
}
void H_31(double *state, double *unused, double *out_7477990481263584566) {
   out_7477990481263584566[0] = 0;
   out_7477990481263584566[1] = 0;
   out_7477990481263584566[2] = 0;
   out_7477990481263584566[3] = 0;
   out_7477990481263584566[4] = 0;
   out_7477990481263584566[5] = 0;
   out_7477990481263584566[6] = 0;
   out_7477990481263584566[7] = 0;
   out_7477990481263584566[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_5059320499403781563) {
  err_fun(nom_x, delta_x, out_5059320499403781563);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_8028694691748550712) {
  inv_err_fun(nom_x, true_x, out_8028694691748550712);
}
void car_H_mod_fun(double *state, double *out_1011613483250515043) {
  H_mod_fun(state, out_1011613483250515043);
}
void car_f_fun(double *state, double dt, double *out_2197439487468085332) {
  f_fun(state,  dt, out_2197439487468085332);
}
void car_F_fun(double *state, double dt, double *out_7087540084366041403) {
  F_fun(state,  dt, out_7087540084366041403);
}
void car_h_25(double *state, double *unused, double *out_7407988264137374316) {
  h_25(state, unused, out_7407988264137374316);
}
void car_H_25(double *state, double *unused, double *out_3892078341934149797) {
  H_25(state, unused, out_3892078341934149797);
}
void car_h_24(double *state, double *unused, double *out_8835218896431103117) {
  h_24(state, unused, out_8835218896431103117);
}
void car_H_24(double *state, double *unused, double *out_2235142160227532400) {
  H_24(state, unused, out_2235142160227532400);
}
void car_h_30(double *state, double *unused, double *out_7565174932488503461) {
  h_30(state, unused, out_7565174932488503461);
}
void car_H_30(double *state, double *unused, double *out_6410411300441398424) {
  H_30(state, unused, out_6410411300441398424);
}
void car_h_26(double *state, double *unused, double *out_1416794239518337304) {
  h_26(state, unused, out_1416794239518337304);
}
void car_H_26(double *state, double *unused, double *out_7196604311694950398) {
  H_26(state, unused, out_7196604311694950398);
}
void car_h_27(double *state, double *unused, double *out_2406314996476528671) {
  h_27(state, unused, out_2406314996476528671);
}
void car_H_27(double *state, double *unused, double *out_8634005371625341641) {
  H_27(state, unused, out_8634005371625341641);
}
void car_h_29(double *state, double *unused, double *out_8277163820412350504) {
  h_29(state, unused, out_8277163820412350504);
}
void car_H_29(double *state, double *unused, double *out_6920642644755790608) {
  H_29(state, unused, out_6920642644755790608);
}
void car_h_28(double *state, double *unused, double *out_5218867099746382054) {
  h_28(state, unused, out_5218867099746382054);
}
void car_H_28(double *state, double *unused, double *out_1838243627686260034) {
  H_28(state, unused, out_1838243627686260034);
}
void car_h_31(double *state, double *unused, double *out_7683182326421880205) {
  h_31(state, unused, out_7683182326421880205);
}
void car_H_31(double *state, double *unused, double *out_7477990481263584566) {
  H_31(state, unused, out_7477990481263584566);
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
