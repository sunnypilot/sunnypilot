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
void err_fun(double *nom_x, double *delta_x, double *out_7386474349186888019) {
   out_7386474349186888019[0] = delta_x[0] + nom_x[0];
   out_7386474349186888019[1] = delta_x[1] + nom_x[1];
   out_7386474349186888019[2] = delta_x[2] + nom_x[2];
   out_7386474349186888019[3] = delta_x[3] + nom_x[3];
   out_7386474349186888019[4] = delta_x[4] + nom_x[4];
   out_7386474349186888019[5] = delta_x[5] + nom_x[5];
   out_7386474349186888019[6] = delta_x[6] + nom_x[6];
   out_7386474349186888019[7] = delta_x[7] + nom_x[7];
   out_7386474349186888019[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_1643524624122634889) {
   out_1643524624122634889[0] = -nom_x[0] + true_x[0];
   out_1643524624122634889[1] = -nom_x[1] + true_x[1];
   out_1643524624122634889[2] = -nom_x[2] + true_x[2];
   out_1643524624122634889[3] = -nom_x[3] + true_x[3];
   out_1643524624122634889[4] = -nom_x[4] + true_x[4];
   out_1643524624122634889[5] = -nom_x[5] + true_x[5];
   out_1643524624122634889[6] = -nom_x[6] + true_x[6];
   out_1643524624122634889[7] = -nom_x[7] + true_x[7];
   out_1643524624122634889[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_3924863114412422386) {
   out_3924863114412422386[0] = 1.0;
   out_3924863114412422386[1] = 0.0;
   out_3924863114412422386[2] = 0.0;
   out_3924863114412422386[3] = 0.0;
   out_3924863114412422386[4] = 0.0;
   out_3924863114412422386[5] = 0.0;
   out_3924863114412422386[6] = 0.0;
   out_3924863114412422386[7] = 0.0;
   out_3924863114412422386[8] = 0.0;
   out_3924863114412422386[9] = 0.0;
   out_3924863114412422386[10] = 1.0;
   out_3924863114412422386[11] = 0.0;
   out_3924863114412422386[12] = 0.0;
   out_3924863114412422386[13] = 0.0;
   out_3924863114412422386[14] = 0.0;
   out_3924863114412422386[15] = 0.0;
   out_3924863114412422386[16] = 0.0;
   out_3924863114412422386[17] = 0.0;
   out_3924863114412422386[18] = 0.0;
   out_3924863114412422386[19] = 0.0;
   out_3924863114412422386[20] = 1.0;
   out_3924863114412422386[21] = 0.0;
   out_3924863114412422386[22] = 0.0;
   out_3924863114412422386[23] = 0.0;
   out_3924863114412422386[24] = 0.0;
   out_3924863114412422386[25] = 0.0;
   out_3924863114412422386[26] = 0.0;
   out_3924863114412422386[27] = 0.0;
   out_3924863114412422386[28] = 0.0;
   out_3924863114412422386[29] = 0.0;
   out_3924863114412422386[30] = 1.0;
   out_3924863114412422386[31] = 0.0;
   out_3924863114412422386[32] = 0.0;
   out_3924863114412422386[33] = 0.0;
   out_3924863114412422386[34] = 0.0;
   out_3924863114412422386[35] = 0.0;
   out_3924863114412422386[36] = 0.0;
   out_3924863114412422386[37] = 0.0;
   out_3924863114412422386[38] = 0.0;
   out_3924863114412422386[39] = 0.0;
   out_3924863114412422386[40] = 1.0;
   out_3924863114412422386[41] = 0.0;
   out_3924863114412422386[42] = 0.0;
   out_3924863114412422386[43] = 0.0;
   out_3924863114412422386[44] = 0.0;
   out_3924863114412422386[45] = 0.0;
   out_3924863114412422386[46] = 0.0;
   out_3924863114412422386[47] = 0.0;
   out_3924863114412422386[48] = 0.0;
   out_3924863114412422386[49] = 0.0;
   out_3924863114412422386[50] = 1.0;
   out_3924863114412422386[51] = 0.0;
   out_3924863114412422386[52] = 0.0;
   out_3924863114412422386[53] = 0.0;
   out_3924863114412422386[54] = 0.0;
   out_3924863114412422386[55] = 0.0;
   out_3924863114412422386[56] = 0.0;
   out_3924863114412422386[57] = 0.0;
   out_3924863114412422386[58] = 0.0;
   out_3924863114412422386[59] = 0.0;
   out_3924863114412422386[60] = 1.0;
   out_3924863114412422386[61] = 0.0;
   out_3924863114412422386[62] = 0.0;
   out_3924863114412422386[63] = 0.0;
   out_3924863114412422386[64] = 0.0;
   out_3924863114412422386[65] = 0.0;
   out_3924863114412422386[66] = 0.0;
   out_3924863114412422386[67] = 0.0;
   out_3924863114412422386[68] = 0.0;
   out_3924863114412422386[69] = 0.0;
   out_3924863114412422386[70] = 1.0;
   out_3924863114412422386[71] = 0.0;
   out_3924863114412422386[72] = 0.0;
   out_3924863114412422386[73] = 0.0;
   out_3924863114412422386[74] = 0.0;
   out_3924863114412422386[75] = 0.0;
   out_3924863114412422386[76] = 0.0;
   out_3924863114412422386[77] = 0.0;
   out_3924863114412422386[78] = 0.0;
   out_3924863114412422386[79] = 0.0;
   out_3924863114412422386[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_3335581872075103078) {
   out_3335581872075103078[0] = state[0];
   out_3335581872075103078[1] = state[1];
   out_3335581872075103078[2] = state[2];
   out_3335581872075103078[3] = state[3];
   out_3335581872075103078[4] = state[4];
   out_3335581872075103078[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8100000000000005*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_3335581872075103078[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_3335581872075103078[7] = state[7];
   out_3335581872075103078[8] = state[8];
}
void F_fun(double *state, double dt, double *out_4298495675166004229) {
   out_4298495675166004229[0] = 1;
   out_4298495675166004229[1] = 0;
   out_4298495675166004229[2] = 0;
   out_4298495675166004229[3] = 0;
   out_4298495675166004229[4] = 0;
   out_4298495675166004229[5] = 0;
   out_4298495675166004229[6] = 0;
   out_4298495675166004229[7] = 0;
   out_4298495675166004229[8] = 0;
   out_4298495675166004229[9] = 0;
   out_4298495675166004229[10] = 1;
   out_4298495675166004229[11] = 0;
   out_4298495675166004229[12] = 0;
   out_4298495675166004229[13] = 0;
   out_4298495675166004229[14] = 0;
   out_4298495675166004229[15] = 0;
   out_4298495675166004229[16] = 0;
   out_4298495675166004229[17] = 0;
   out_4298495675166004229[18] = 0;
   out_4298495675166004229[19] = 0;
   out_4298495675166004229[20] = 1;
   out_4298495675166004229[21] = 0;
   out_4298495675166004229[22] = 0;
   out_4298495675166004229[23] = 0;
   out_4298495675166004229[24] = 0;
   out_4298495675166004229[25] = 0;
   out_4298495675166004229[26] = 0;
   out_4298495675166004229[27] = 0;
   out_4298495675166004229[28] = 0;
   out_4298495675166004229[29] = 0;
   out_4298495675166004229[30] = 1;
   out_4298495675166004229[31] = 0;
   out_4298495675166004229[32] = 0;
   out_4298495675166004229[33] = 0;
   out_4298495675166004229[34] = 0;
   out_4298495675166004229[35] = 0;
   out_4298495675166004229[36] = 0;
   out_4298495675166004229[37] = 0;
   out_4298495675166004229[38] = 0;
   out_4298495675166004229[39] = 0;
   out_4298495675166004229[40] = 1;
   out_4298495675166004229[41] = 0;
   out_4298495675166004229[42] = 0;
   out_4298495675166004229[43] = 0;
   out_4298495675166004229[44] = 0;
   out_4298495675166004229[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_4298495675166004229[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_4298495675166004229[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_4298495675166004229[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_4298495675166004229[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_4298495675166004229[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_4298495675166004229[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_4298495675166004229[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_4298495675166004229[53] = -9.8100000000000005*dt;
   out_4298495675166004229[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_4298495675166004229[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_4298495675166004229[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_4298495675166004229[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_4298495675166004229[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_4298495675166004229[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_4298495675166004229[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_4298495675166004229[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_4298495675166004229[62] = 0;
   out_4298495675166004229[63] = 0;
   out_4298495675166004229[64] = 0;
   out_4298495675166004229[65] = 0;
   out_4298495675166004229[66] = 0;
   out_4298495675166004229[67] = 0;
   out_4298495675166004229[68] = 0;
   out_4298495675166004229[69] = 0;
   out_4298495675166004229[70] = 1;
   out_4298495675166004229[71] = 0;
   out_4298495675166004229[72] = 0;
   out_4298495675166004229[73] = 0;
   out_4298495675166004229[74] = 0;
   out_4298495675166004229[75] = 0;
   out_4298495675166004229[76] = 0;
   out_4298495675166004229[77] = 0;
   out_4298495675166004229[78] = 0;
   out_4298495675166004229[79] = 0;
   out_4298495675166004229[80] = 1;
}
void h_25(double *state, double *unused, double *out_4842735039427911863) {
   out_4842735039427911863[0] = state[6];
}
void H_25(double *state, double *unused, double *out_4839294745646846211) {
   out_4839294745646846211[0] = 0;
   out_4839294745646846211[1] = 0;
   out_4839294745646846211[2] = 0;
   out_4839294745646846211[3] = 0;
   out_4839294745646846211[4] = 0;
   out_4839294745646846211[5] = 0;
   out_4839294745646846211[6] = 1;
   out_4839294745646846211[7] = 0;
   out_4839294745646846211[8] = 0;
}
void h_24(double *state, double *unused, double *out_6391236564095056534) {
   out_6391236564095056534[0] = state[4];
   out_6391236564095056534[1] = state[5];
}
void H_24(double *state, double *unused, double *out_3156043134379392427) {
   out_3156043134379392427[0] = 0;
   out_3156043134379392427[1] = 0;
   out_3156043134379392427[2] = 0;
   out_3156043134379392427[3] = 0;
   out_3156043134379392427[4] = 1;
   out_3156043134379392427[5] = 0;
   out_3156043134379392427[6] = 0;
   out_3156043134379392427[7] = 0;
   out_3156043134379392427[8] = 0;
   out_3156043134379392427[9] = 0;
   out_3156043134379392427[10] = 0;
   out_3156043134379392427[11] = 0;
   out_3156043134379392427[12] = 0;
   out_3156043134379392427[13] = 0;
   out_3156043134379392427[14] = 1;
   out_3156043134379392427[15] = 0;
   out_3156043134379392427[16] = 0;
   out_3156043134379392427[17] = 0;
}
void h_30(double *state, double *unused, double *out_8704418515856413515) {
   out_8704418515856413515[0] = state[4];
}
void H_30(double *state, double *unused, double *out_7357627704154094838) {
   out_7357627704154094838[0] = 0;
   out_7357627704154094838[1] = 0;
   out_7357627704154094838[2] = 0;
   out_7357627704154094838[3] = 0;
   out_7357627704154094838[4] = 1;
   out_7357627704154094838[5] = 0;
   out_7357627704154094838[6] = 0;
   out_7357627704154094838[7] = 0;
   out_7357627704154094838[8] = 0;
}
void h_26(double *state, double *unused, double *out_2531416071598916590) {
   out_2531416071598916590[0] = state[7];
}
void H_26(double *state, double *unused, double *out_1097791426772789987) {
   out_1097791426772789987[0] = 0;
   out_1097791426772789987[1] = 0;
   out_1097791426772789987[2] = 0;
   out_1097791426772789987[3] = 0;
   out_1097791426772789987[4] = 0;
   out_1097791426772789987[5] = 0;
   out_1097791426772789987[6] = 0;
   out_1097791426772789987[7] = 1;
   out_1097791426772789987[8] = 0;
}
void h_27(double *state, double *unused, double *out_3338687832041835488) {
   out_3338687832041835488[0] = state[3];
}
void H_27(double *state, double *unused, double *out_5182864392353669927) {
   out_5182864392353669927[0] = 0;
   out_5182864392353669927[1] = 0;
   out_5182864392353669927[2] = 0;
   out_5182864392353669927[3] = 1;
   out_5182864392353669927[4] = 0;
   out_5182864392353669927[5] = 0;
   out_5182864392353669927[6] = 0;
   out_5182864392353669927[7] = 0;
   out_5182864392353669927[8] = 0;
}
void h_29(double *state, double *unused, double *out_4740652290192292456) {
   out_4740652290192292456[0] = state[1];
}
void H_29(double *state, double *unused, double *out_7867859048468487022) {
   out_7867859048468487022[0] = 0;
   out_7867859048468487022[1] = 1;
   out_7867859048468487022[2] = 0;
   out_7867859048468487022[3] = 0;
   out_7867859048468487022[4] = 0;
   out_7867859048468487022[5] = 0;
   out_7867859048468487022[6] = 0;
   out_7867859048468487022[7] = 0;
   out_7867859048468487022[8] = 0;
}
void h_28(double *state, double *unused, double *out_4881309279861547540) {
   out_4881309279861547540[0] = state[0];
}
void H_28(double *state, double *unused, double *out_2785460031398956448) {
   out_2785460031398956448[0] = 1;
   out_2785460031398956448[1] = 0;
   out_2785460031398956448[2] = 0;
   out_2785460031398956448[3] = 0;
   out_2785460031398956448[4] = 0;
   out_2785460031398956448[5] = 0;
   out_2785460031398956448[6] = 0;
   out_2785460031398956448[7] = 0;
   out_2785460031398956448[8] = 0;
}
void h_31(double *state, double *unused, double *out_2273777257731247497) {
   out_2273777257731247497[0] = state[8];
}
void H_31(double *state, double *unused, double *out_471583324539438511) {
   out_471583324539438511[0] = 0;
   out_471583324539438511[1] = 0;
   out_471583324539438511[2] = 0;
   out_471583324539438511[3] = 0;
   out_471583324539438511[4] = 0;
   out_471583324539438511[5] = 0;
   out_471583324539438511[6] = 0;
   out_471583324539438511[7] = 0;
   out_471583324539438511[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_7386474349186888019) {
  err_fun(nom_x, delta_x, out_7386474349186888019);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_1643524624122634889) {
  inv_err_fun(nom_x, true_x, out_1643524624122634889);
}
void car_H_mod_fun(double *state, double *out_3924863114412422386) {
  H_mod_fun(state, out_3924863114412422386);
}
void car_f_fun(double *state, double dt, double *out_3335581872075103078) {
  f_fun(state,  dt, out_3335581872075103078);
}
void car_F_fun(double *state, double dt, double *out_4298495675166004229) {
  F_fun(state,  dt, out_4298495675166004229);
}
void car_h_25(double *state, double *unused, double *out_4842735039427911863) {
  h_25(state, unused, out_4842735039427911863);
}
void car_H_25(double *state, double *unused, double *out_4839294745646846211) {
  H_25(state, unused, out_4839294745646846211);
}
void car_h_24(double *state, double *unused, double *out_6391236564095056534) {
  h_24(state, unused, out_6391236564095056534);
}
void car_H_24(double *state, double *unused, double *out_3156043134379392427) {
  H_24(state, unused, out_3156043134379392427);
}
void car_h_30(double *state, double *unused, double *out_8704418515856413515) {
  h_30(state, unused, out_8704418515856413515);
}
void car_H_30(double *state, double *unused, double *out_7357627704154094838) {
  H_30(state, unused, out_7357627704154094838);
}
void car_h_26(double *state, double *unused, double *out_2531416071598916590) {
  h_26(state, unused, out_2531416071598916590);
}
void car_H_26(double *state, double *unused, double *out_1097791426772789987) {
  H_26(state, unused, out_1097791426772789987);
}
void car_h_27(double *state, double *unused, double *out_3338687832041835488) {
  h_27(state, unused, out_3338687832041835488);
}
void car_H_27(double *state, double *unused, double *out_5182864392353669927) {
  H_27(state, unused, out_5182864392353669927);
}
void car_h_29(double *state, double *unused, double *out_4740652290192292456) {
  h_29(state, unused, out_4740652290192292456);
}
void car_H_29(double *state, double *unused, double *out_7867859048468487022) {
  H_29(state, unused, out_7867859048468487022);
}
void car_h_28(double *state, double *unused, double *out_4881309279861547540) {
  h_28(state, unused, out_4881309279861547540);
}
void car_H_28(double *state, double *unused, double *out_2785460031398956448) {
  H_28(state, unused, out_2785460031398956448);
}
void car_h_31(double *state, double *unused, double *out_2273777257731247497) {
  h_31(state, unused, out_2273777257731247497);
}
void car_H_31(double *state, double *unused, double *out_471583324539438511) {
  H_31(state, unused, out_471583324539438511);
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
