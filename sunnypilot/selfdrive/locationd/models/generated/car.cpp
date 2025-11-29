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
void err_fun(double *nom_x, double *delta_x, double *out_6017625978963375894) {
   out_6017625978963375894[0] = delta_x[0] + nom_x[0];
   out_6017625978963375894[1] = delta_x[1] + nom_x[1];
   out_6017625978963375894[2] = delta_x[2] + nom_x[2];
   out_6017625978963375894[3] = delta_x[3] + nom_x[3];
   out_6017625978963375894[4] = delta_x[4] + nom_x[4];
   out_6017625978963375894[5] = delta_x[5] + nom_x[5];
   out_6017625978963375894[6] = delta_x[6] + nom_x[6];
   out_6017625978963375894[7] = delta_x[7] + nom_x[7];
   out_6017625978963375894[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_6841210236025661412) {
   out_6841210236025661412[0] = -nom_x[0] + true_x[0];
   out_6841210236025661412[1] = -nom_x[1] + true_x[1];
   out_6841210236025661412[2] = -nom_x[2] + true_x[2];
   out_6841210236025661412[3] = -nom_x[3] + true_x[3];
   out_6841210236025661412[4] = -nom_x[4] + true_x[4];
   out_6841210236025661412[5] = -nom_x[5] + true_x[5];
   out_6841210236025661412[6] = -nom_x[6] + true_x[6];
   out_6841210236025661412[7] = -nom_x[7] + true_x[7];
   out_6841210236025661412[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_1041246729861882300) {
   out_1041246729861882300[0] = 1.0;
   out_1041246729861882300[1] = 0.0;
   out_1041246729861882300[2] = 0.0;
   out_1041246729861882300[3] = 0.0;
   out_1041246729861882300[4] = 0.0;
   out_1041246729861882300[5] = 0.0;
   out_1041246729861882300[6] = 0.0;
   out_1041246729861882300[7] = 0.0;
   out_1041246729861882300[8] = 0.0;
   out_1041246729861882300[9] = 0.0;
   out_1041246729861882300[10] = 1.0;
   out_1041246729861882300[11] = 0.0;
   out_1041246729861882300[12] = 0.0;
   out_1041246729861882300[13] = 0.0;
   out_1041246729861882300[14] = 0.0;
   out_1041246729861882300[15] = 0.0;
   out_1041246729861882300[16] = 0.0;
   out_1041246729861882300[17] = 0.0;
   out_1041246729861882300[18] = 0.0;
   out_1041246729861882300[19] = 0.0;
   out_1041246729861882300[20] = 1.0;
   out_1041246729861882300[21] = 0.0;
   out_1041246729861882300[22] = 0.0;
   out_1041246729861882300[23] = 0.0;
   out_1041246729861882300[24] = 0.0;
   out_1041246729861882300[25] = 0.0;
   out_1041246729861882300[26] = 0.0;
   out_1041246729861882300[27] = 0.0;
   out_1041246729861882300[28] = 0.0;
   out_1041246729861882300[29] = 0.0;
   out_1041246729861882300[30] = 1.0;
   out_1041246729861882300[31] = 0.0;
   out_1041246729861882300[32] = 0.0;
   out_1041246729861882300[33] = 0.0;
   out_1041246729861882300[34] = 0.0;
   out_1041246729861882300[35] = 0.0;
   out_1041246729861882300[36] = 0.0;
   out_1041246729861882300[37] = 0.0;
   out_1041246729861882300[38] = 0.0;
   out_1041246729861882300[39] = 0.0;
   out_1041246729861882300[40] = 1.0;
   out_1041246729861882300[41] = 0.0;
   out_1041246729861882300[42] = 0.0;
   out_1041246729861882300[43] = 0.0;
   out_1041246729861882300[44] = 0.0;
   out_1041246729861882300[45] = 0.0;
   out_1041246729861882300[46] = 0.0;
   out_1041246729861882300[47] = 0.0;
   out_1041246729861882300[48] = 0.0;
   out_1041246729861882300[49] = 0.0;
   out_1041246729861882300[50] = 1.0;
   out_1041246729861882300[51] = 0.0;
   out_1041246729861882300[52] = 0.0;
   out_1041246729861882300[53] = 0.0;
   out_1041246729861882300[54] = 0.0;
   out_1041246729861882300[55] = 0.0;
   out_1041246729861882300[56] = 0.0;
   out_1041246729861882300[57] = 0.0;
   out_1041246729861882300[58] = 0.0;
   out_1041246729861882300[59] = 0.0;
   out_1041246729861882300[60] = 1.0;
   out_1041246729861882300[61] = 0.0;
   out_1041246729861882300[62] = 0.0;
   out_1041246729861882300[63] = 0.0;
   out_1041246729861882300[64] = 0.0;
   out_1041246729861882300[65] = 0.0;
   out_1041246729861882300[66] = 0.0;
   out_1041246729861882300[67] = 0.0;
   out_1041246729861882300[68] = 0.0;
   out_1041246729861882300[69] = 0.0;
   out_1041246729861882300[70] = 1.0;
   out_1041246729861882300[71] = 0.0;
   out_1041246729861882300[72] = 0.0;
   out_1041246729861882300[73] = 0.0;
   out_1041246729861882300[74] = 0.0;
   out_1041246729861882300[75] = 0.0;
   out_1041246729861882300[76] = 0.0;
   out_1041246729861882300[77] = 0.0;
   out_1041246729861882300[78] = 0.0;
   out_1041246729861882300[79] = 0.0;
   out_1041246729861882300[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_4989810676465268701) {
   out_4989810676465268701[0] = state[0];
   out_4989810676465268701[1] = state[1];
   out_4989810676465268701[2] = state[2];
   out_4989810676465268701[3] = state[3];
   out_4989810676465268701[4] = state[4];
   out_4989810676465268701[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8100000000000005*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_4989810676465268701[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_4989810676465268701[7] = state[7];
   out_4989810676465268701[8] = state[8];
}
void F_fun(double *state, double dt, double *out_5356911169490671165) {
   out_5356911169490671165[0] = 1;
   out_5356911169490671165[1] = 0;
   out_5356911169490671165[2] = 0;
   out_5356911169490671165[3] = 0;
   out_5356911169490671165[4] = 0;
   out_5356911169490671165[5] = 0;
   out_5356911169490671165[6] = 0;
   out_5356911169490671165[7] = 0;
   out_5356911169490671165[8] = 0;
   out_5356911169490671165[9] = 0;
   out_5356911169490671165[10] = 1;
   out_5356911169490671165[11] = 0;
   out_5356911169490671165[12] = 0;
   out_5356911169490671165[13] = 0;
   out_5356911169490671165[14] = 0;
   out_5356911169490671165[15] = 0;
   out_5356911169490671165[16] = 0;
   out_5356911169490671165[17] = 0;
   out_5356911169490671165[18] = 0;
   out_5356911169490671165[19] = 0;
   out_5356911169490671165[20] = 1;
   out_5356911169490671165[21] = 0;
   out_5356911169490671165[22] = 0;
   out_5356911169490671165[23] = 0;
   out_5356911169490671165[24] = 0;
   out_5356911169490671165[25] = 0;
   out_5356911169490671165[26] = 0;
   out_5356911169490671165[27] = 0;
   out_5356911169490671165[28] = 0;
   out_5356911169490671165[29] = 0;
   out_5356911169490671165[30] = 1;
   out_5356911169490671165[31] = 0;
   out_5356911169490671165[32] = 0;
   out_5356911169490671165[33] = 0;
   out_5356911169490671165[34] = 0;
   out_5356911169490671165[35] = 0;
   out_5356911169490671165[36] = 0;
   out_5356911169490671165[37] = 0;
   out_5356911169490671165[38] = 0;
   out_5356911169490671165[39] = 0;
   out_5356911169490671165[40] = 1;
   out_5356911169490671165[41] = 0;
   out_5356911169490671165[42] = 0;
   out_5356911169490671165[43] = 0;
   out_5356911169490671165[44] = 0;
   out_5356911169490671165[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_5356911169490671165[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_5356911169490671165[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_5356911169490671165[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_5356911169490671165[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_5356911169490671165[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_5356911169490671165[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_5356911169490671165[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_5356911169490671165[53] = -9.8100000000000005*dt;
   out_5356911169490671165[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_5356911169490671165[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_5356911169490671165[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_5356911169490671165[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_5356911169490671165[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_5356911169490671165[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_5356911169490671165[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_5356911169490671165[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_5356911169490671165[62] = 0;
   out_5356911169490671165[63] = 0;
   out_5356911169490671165[64] = 0;
   out_5356911169490671165[65] = 0;
   out_5356911169490671165[66] = 0;
   out_5356911169490671165[67] = 0;
   out_5356911169490671165[68] = 0;
   out_5356911169490671165[69] = 0;
   out_5356911169490671165[70] = 1;
   out_5356911169490671165[71] = 0;
   out_5356911169490671165[72] = 0;
   out_5356911169490671165[73] = 0;
   out_5356911169490671165[74] = 0;
   out_5356911169490671165[75] = 0;
   out_5356911169490671165[76] = 0;
   out_5356911169490671165[77] = 0;
   out_5356911169490671165[78] = 0;
   out_5356911169490671165[79] = 0;
   out_5356911169490671165[80] = 1;
}
void h_25(double *state, double *unused, double *out_5800435846139545547) {
   out_5800435846139545547[0] = state[6];
}
void H_25(double *state, double *unused, double *out_5944938555046547140) {
   out_5944938555046547140[0] = 0;
   out_5944938555046547140[1] = 0;
   out_5944938555046547140[2] = 0;
   out_5944938555046547140[3] = 0;
   out_5944938555046547140[4] = 0;
   out_5944938555046547140[5] = 0;
   out_5944938555046547140[6] = 1;
   out_5944938555046547140[7] = 0;
   out_5944938555046547140[8] = 0;
}
void h_24(double *state, double *unused, double *out_5732265362808196766) {
   out_5732265362808196766[0] = state[4];
   out_5732265362808196766[1] = state[5];
}
void H_24(double *state, double *unused, double *out_5474481073003208416) {
   out_5474481073003208416[0] = 0;
   out_5474481073003208416[1] = 0;
   out_5474481073003208416[2] = 0;
   out_5474481073003208416[3] = 0;
   out_5474481073003208416[4] = 1;
   out_5474481073003208416[5] = 0;
   out_5474481073003208416[6] = 0;
   out_5474481073003208416[7] = 0;
   out_5474481073003208416[8] = 0;
   out_5474481073003208416[9] = 0;
   out_5474481073003208416[10] = 0;
   out_5474481073003208416[11] = 0;
   out_5474481073003208416[12] = 0;
   out_5474481073003208416[13] = 0;
   out_5474481073003208416[14] = 1;
   out_5474481073003208416[15] = 0;
   out_5474481073003208416[16] = 0;
   out_5474481073003208416[17] = 0;
}
void h_30(double *state, double *unused, double *out_156371015655145690) {
   out_156371015655145690[0] = state[4];
}
void H_30(double *state, double *unused, double *out_1417242224918938942) {
   out_1417242224918938942[0] = 0;
   out_1417242224918938942[1] = 0;
   out_1417242224918938942[2] = 0;
   out_1417242224918938942[3] = 0;
   out_1417242224918938942[4] = 1;
   out_1417242224918938942[5] = 0;
   out_1417242224918938942[6] = 0;
   out_1417242224918938942[7] = 0;
   out_1417242224918938942[8] = 0;
}
void h_26(double *state, double *unused, double *out_6034656503213860778) {
   out_6034656503213860778[0] = state[7];
}
void H_26(double *state, double *unused, double *out_2203435236172490916) {
   out_2203435236172490916[0] = 0;
   out_2203435236172490916[1] = 0;
   out_2203435236172490916[2] = 0;
   out_2203435236172490916[3] = 0;
   out_2203435236172490916[4] = 0;
   out_2203435236172490916[5] = 0;
   out_2203435236172490916[6] = 0;
   out_2203435236172490916[7] = 1;
   out_2203435236172490916[8] = 0;
}
void h_27(double *state, double *unused, double *out_2122012912675332539) {
   out_2122012912675332539[0] = state[3];
}
void H_27(double *state, double *unused, double *out_3640836296102882159) {
   out_3640836296102882159[0] = 0;
   out_3640836296102882159[1] = 0;
   out_3640836296102882159[2] = 0;
   out_3640836296102882159[3] = 1;
   out_3640836296102882159[4] = 0;
   out_3640836296102882159[5] = 0;
   out_3640836296102882159[6] = 0;
   out_3640836296102882159[7] = 0;
   out_3640836296102882159[8] = 0;
}
void h_29(double *state, double *unused, double *out_8562027835299372343) {
   out_8562027835299372343[0] = state[1];
}
void H_29(double *state, double *unused, double *out_1927473569233331126) {
   out_1927473569233331126[0] = 0;
   out_1927473569233331126[1] = 1;
   out_1927473569233331126[2] = 0;
   out_1927473569233331126[3] = 0;
   out_1927473569233331126[4] = 0;
   out_1927473569233331126[5] = 0;
   out_1927473569233331126[6] = 0;
   out_1927473569233331126[7] = 0;
   out_1927473569233331126[8] = 0;
}
void h_28(double *state, double *unused, double *out_4124438144784840929) {
   out_4124438144784840929[0] = state[0];
}
void H_28(double *state, double *unused, double *out_3891103840798657377) {
   out_3891103840798657377[0] = 1;
   out_3891103840798657377[1] = 0;
   out_3891103840798657377[2] = 0;
   out_3891103840798657377[3] = 0;
   out_3891103840798657377[4] = 0;
   out_3891103840798657377[5] = 0;
   out_3891103840798657377[6] = 0;
   out_3891103840798657377[7] = 0;
   out_3891103840798657377[8] = 0;
}
void h_31(double *state, double *unused, double *out_1019066314689231588) {
   out_1019066314689231588[0] = state[8];
}
void H_31(double *state, double *unused, double *out_5975584516923507568) {
   out_5975584516923507568[0] = 0;
   out_5975584516923507568[1] = 0;
   out_5975584516923507568[2] = 0;
   out_5975584516923507568[3] = 0;
   out_5975584516923507568[4] = 0;
   out_5975584516923507568[5] = 0;
   out_5975584516923507568[6] = 0;
   out_5975584516923507568[7] = 0;
   out_5975584516923507568[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_6017625978963375894) {
  err_fun(nom_x, delta_x, out_6017625978963375894);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_6841210236025661412) {
  inv_err_fun(nom_x, true_x, out_6841210236025661412);
}
void car_H_mod_fun(double *state, double *out_1041246729861882300) {
  H_mod_fun(state, out_1041246729861882300);
}
void car_f_fun(double *state, double dt, double *out_4989810676465268701) {
  f_fun(state,  dt, out_4989810676465268701);
}
void car_F_fun(double *state, double dt, double *out_5356911169490671165) {
  F_fun(state,  dt, out_5356911169490671165);
}
void car_h_25(double *state, double *unused, double *out_5800435846139545547) {
  h_25(state, unused, out_5800435846139545547);
}
void car_H_25(double *state, double *unused, double *out_5944938555046547140) {
  H_25(state, unused, out_5944938555046547140);
}
void car_h_24(double *state, double *unused, double *out_5732265362808196766) {
  h_24(state, unused, out_5732265362808196766);
}
void car_H_24(double *state, double *unused, double *out_5474481073003208416) {
  H_24(state, unused, out_5474481073003208416);
}
void car_h_30(double *state, double *unused, double *out_156371015655145690) {
  h_30(state, unused, out_156371015655145690);
}
void car_H_30(double *state, double *unused, double *out_1417242224918938942) {
  H_30(state, unused, out_1417242224918938942);
}
void car_h_26(double *state, double *unused, double *out_6034656503213860778) {
  h_26(state, unused, out_6034656503213860778);
}
void car_H_26(double *state, double *unused, double *out_2203435236172490916) {
  H_26(state, unused, out_2203435236172490916);
}
void car_h_27(double *state, double *unused, double *out_2122012912675332539) {
  h_27(state, unused, out_2122012912675332539);
}
void car_H_27(double *state, double *unused, double *out_3640836296102882159) {
  H_27(state, unused, out_3640836296102882159);
}
void car_h_29(double *state, double *unused, double *out_8562027835299372343) {
  h_29(state, unused, out_8562027835299372343);
}
void car_H_29(double *state, double *unused, double *out_1927473569233331126) {
  H_29(state, unused, out_1927473569233331126);
}
void car_h_28(double *state, double *unused, double *out_4124438144784840929) {
  h_28(state, unused, out_4124438144784840929);
}
void car_H_28(double *state, double *unused, double *out_3891103840798657377) {
  H_28(state, unused, out_3891103840798657377);
}
void car_h_31(double *state, double *unused, double *out_1019066314689231588) {
  h_31(state, unused, out_1019066314689231588);
}
void car_H_31(double *state, double *unused, double *out_5975584516923507568) {
  H_31(state, unused, out_5975584516923507568);
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
