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
void err_fun(double *nom_x, double *delta_x, double *out_2237090466909891562) {
   out_2237090466909891562[0] = delta_x[0] + nom_x[0];
   out_2237090466909891562[1] = delta_x[1] + nom_x[1];
   out_2237090466909891562[2] = delta_x[2] + nom_x[2];
   out_2237090466909891562[3] = delta_x[3] + nom_x[3];
   out_2237090466909891562[4] = delta_x[4] + nom_x[4];
   out_2237090466909891562[5] = delta_x[5] + nom_x[5];
   out_2237090466909891562[6] = delta_x[6] + nom_x[6];
   out_2237090466909891562[7] = delta_x[7] + nom_x[7];
   out_2237090466909891562[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_7921264511585388702) {
   out_7921264511585388702[0] = -nom_x[0] + true_x[0];
   out_7921264511585388702[1] = -nom_x[1] + true_x[1];
   out_7921264511585388702[2] = -nom_x[2] + true_x[2];
   out_7921264511585388702[3] = -nom_x[3] + true_x[3];
   out_7921264511585388702[4] = -nom_x[4] + true_x[4];
   out_7921264511585388702[5] = -nom_x[5] + true_x[5];
   out_7921264511585388702[6] = -nom_x[6] + true_x[6];
   out_7921264511585388702[7] = -nom_x[7] + true_x[7];
   out_7921264511585388702[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_4309360915425036189) {
   out_4309360915425036189[0] = 1.0;
   out_4309360915425036189[1] = 0.0;
   out_4309360915425036189[2] = 0.0;
   out_4309360915425036189[3] = 0.0;
   out_4309360915425036189[4] = 0.0;
   out_4309360915425036189[5] = 0.0;
   out_4309360915425036189[6] = 0.0;
   out_4309360915425036189[7] = 0.0;
   out_4309360915425036189[8] = 0.0;
   out_4309360915425036189[9] = 0.0;
   out_4309360915425036189[10] = 1.0;
   out_4309360915425036189[11] = 0.0;
   out_4309360915425036189[12] = 0.0;
   out_4309360915425036189[13] = 0.0;
   out_4309360915425036189[14] = 0.0;
   out_4309360915425036189[15] = 0.0;
   out_4309360915425036189[16] = 0.0;
   out_4309360915425036189[17] = 0.0;
   out_4309360915425036189[18] = 0.0;
   out_4309360915425036189[19] = 0.0;
   out_4309360915425036189[20] = 1.0;
   out_4309360915425036189[21] = 0.0;
   out_4309360915425036189[22] = 0.0;
   out_4309360915425036189[23] = 0.0;
   out_4309360915425036189[24] = 0.0;
   out_4309360915425036189[25] = 0.0;
   out_4309360915425036189[26] = 0.0;
   out_4309360915425036189[27] = 0.0;
   out_4309360915425036189[28] = 0.0;
   out_4309360915425036189[29] = 0.0;
   out_4309360915425036189[30] = 1.0;
   out_4309360915425036189[31] = 0.0;
   out_4309360915425036189[32] = 0.0;
   out_4309360915425036189[33] = 0.0;
   out_4309360915425036189[34] = 0.0;
   out_4309360915425036189[35] = 0.0;
   out_4309360915425036189[36] = 0.0;
   out_4309360915425036189[37] = 0.0;
   out_4309360915425036189[38] = 0.0;
   out_4309360915425036189[39] = 0.0;
   out_4309360915425036189[40] = 1.0;
   out_4309360915425036189[41] = 0.0;
   out_4309360915425036189[42] = 0.0;
   out_4309360915425036189[43] = 0.0;
   out_4309360915425036189[44] = 0.0;
   out_4309360915425036189[45] = 0.0;
   out_4309360915425036189[46] = 0.0;
   out_4309360915425036189[47] = 0.0;
   out_4309360915425036189[48] = 0.0;
   out_4309360915425036189[49] = 0.0;
   out_4309360915425036189[50] = 1.0;
   out_4309360915425036189[51] = 0.0;
   out_4309360915425036189[52] = 0.0;
   out_4309360915425036189[53] = 0.0;
   out_4309360915425036189[54] = 0.0;
   out_4309360915425036189[55] = 0.0;
   out_4309360915425036189[56] = 0.0;
   out_4309360915425036189[57] = 0.0;
   out_4309360915425036189[58] = 0.0;
   out_4309360915425036189[59] = 0.0;
   out_4309360915425036189[60] = 1.0;
   out_4309360915425036189[61] = 0.0;
   out_4309360915425036189[62] = 0.0;
   out_4309360915425036189[63] = 0.0;
   out_4309360915425036189[64] = 0.0;
   out_4309360915425036189[65] = 0.0;
   out_4309360915425036189[66] = 0.0;
   out_4309360915425036189[67] = 0.0;
   out_4309360915425036189[68] = 0.0;
   out_4309360915425036189[69] = 0.0;
   out_4309360915425036189[70] = 1.0;
   out_4309360915425036189[71] = 0.0;
   out_4309360915425036189[72] = 0.0;
   out_4309360915425036189[73] = 0.0;
   out_4309360915425036189[74] = 0.0;
   out_4309360915425036189[75] = 0.0;
   out_4309360915425036189[76] = 0.0;
   out_4309360915425036189[77] = 0.0;
   out_4309360915425036189[78] = 0.0;
   out_4309360915425036189[79] = 0.0;
   out_4309360915425036189[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_6525599712203705111) {
   out_6525599712203705111[0] = state[0];
   out_6525599712203705111[1] = state[1];
   out_6525599712203705111[2] = state[2];
   out_6525599712203705111[3] = state[3];
   out_6525599712203705111[4] = state[4];
   out_6525599712203705111[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8100000000000005*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_6525599712203705111[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_6525599712203705111[7] = state[7];
   out_6525599712203705111[8] = state[8];
}
void F_fun(double *state, double dt, double *out_8055578706737644462) {
   out_8055578706737644462[0] = 1;
   out_8055578706737644462[1] = 0;
   out_8055578706737644462[2] = 0;
   out_8055578706737644462[3] = 0;
   out_8055578706737644462[4] = 0;
   out_8055578706737644462[5] = 0;
   out_8055578706737644462[6] = 0;
   out_8055578706737644462[7] = 0;
   out_8055578706737644462[8] = 0;
   out_8055578706737644462[9] = 0;
   out_8055578706737644462[10] = 1;
   out_8055578706737644462[11] = 0;
   out_8055578706737644462[12] = 0;
   out_8055578706737644462[13] = 0;
   out_8055578706737644462[14] = 0;
   out_8055578706737644462[15] = 0;
   out_8055578706737644462[16] = 0;
   out_8055578706737644462[17] = 0;
   out_8055578706737644462[18] = 0;
   out_8055578706737644462[19] = 0;
   out_8055578706737644462[20] = 1;
   out_8055578706737644462[21] = 0;
   out_8055578706737644462[22] = 0;
   out_8055578706737644462[23] = 0;
   out_8055578706737644462[24] = 0;
   out_8055578706737644462[25] = 0;
   out_8055578706737644462[26] = 0;
   out_8055578706737644462[27] = 0;
   out_8055578706737644462[28] = 0;
   out_8055578706737644462[29] = 0;
   out_8055578706737644462[30] = 1;
   out_8055578706737644462[31] = 0;
   out_8055578706737644462[32] = 0;
   out_8055578706737644462[33] = 0;
   out_8055578706737644462[34] = 0;
   out_8055578706737644462[35] = 0;
   out_8055578706737644462[36] = 0;
   out_8055578706737644462[37] = 0;
   out_8055578706737644462[38] = 0;
   out_8055578706737644462[39] = 0;
   out_8055578706737644462[40] = 1;
   out_8055578706737644462[41] = 0;
   out_8055578706737644462[42] = 0;
   out_8055578706737644462[43] = 0;
   out_8055578706737644462[44] = 0;
   out_8055578706737644462[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_8055578706737644462[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_8055578706737644462[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_8055578706737644462[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_8055578706737644462[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_8055578706737644462[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_8055578706737644462[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_8055578706737644462[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_8055578706737644462[53] = -9.8100000000000005*dt;
   out_8055578706737644462[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_8055578706737644462[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_8055578706737644462[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_8055578706737644462[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_8055578706737644462[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_8055578706737644462[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_8055578706737644462[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_8055578706737644462[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_8055578706737644462[62] = 0;
   out_8055578706737644462[63] = 0;
   out_8055578706737644462[64] = 0;
   out_8055578706737644462[65] = 0;
   out_8055578706737644462[66] = 0;
   out_8055578706737644462[67] = 0;
   out_8055578706737644462[68] = 0;
   out_8055578706737644462[69] = 0;
   out_8055578706737644462[70] = 1;
   out_8055578706737644462[71] = 0;
   out_8055578706737644462[72] = 0;
   out_8055578706737644462[73] = 0;
   out_8055578706737644462[74] = 0;
   out_8055578706737644462[75] = 0;
   out_8055578706737644462[76] = 0;
   out_8055578706737644462[77] = 0;
   out_8055578706737644462[78] = 0;
   out_8055578706737644462[79] = 0;
   out_8055578706737644462[80] = 1;
}
void h_25(double *state, double *unused, double *out_6597204507449544518) {
   out_6597204507449544518[0] = state[6];
}
void H_25(double *state, double *unused, double *out_9213052740609701029) {
   out_9213052740609701029[0] = 0;
   out_9213052740609701029[1] = 0;
   out_9213052740609701029[2] = 0;
   out_9213052740609701029[3] = 0;
   out_9213052740609701029[4] = 0;
   out_9213052740609701029[5] = 0;
   out_9213052740609701029[6] = 1;
   out_9213052740609701029[7] = 0;
   out_9213052740609701029[8] = 0;
}
void h_24(double *state, double *unused, double *out_6958676434988343269) {
   out_6958676434988343269[0] = state[4];
   out_6958676434988343269[1] = state[5];
}
void H_24(double *state, double *unused, double *out_3085832238448018832) {
   out_3085832238448018832[0] = 0;
   out_3085832238448018832[1] = 0;
   out_3085832238448018832[2] = 0;
   out_3085832238448018832[3] = 0;
   out_3085832238448018832[4] = 1;
   out_3085832238448018832[5] = 0;
   out_3085832238448018832[6] = 0;
   out_3085832238448018832[7] = 0;
   out_3085832238448018832[8] = 0;
   out_3085832238448018832[9] = 0;
   out_3085832238448018832[10] = 0;
   out_3085832238448018832[11] = 0;
   out_3085832238448018832[12] = 0;
   out_3085832238448018832[13] = 0;
   out_3085832238448018832[14] = 1;
   out_3085832238448018832[15] = 0;
   out_3085832238448018832[16] = 0;
   out_3085832238448018832[17] = 0;
}
void h_30(double *state, double *unused, double *out_5078704339909656162) {
   out_5078704339909656162[0] = state[4];
}
void H_30(double *state, double *unused, double *out_6715358374592601960) {
   out_6715358374592601960[0] = 0;
   out_6715358374592601960[1] = 0;
   out_6715358374592601960[2] = 0;
   out_6715358374592601960[3] = 0;
   out_6715358374592601960[4] = 1;
   out_6715358374592601960[5] = 0;
   out_6715358374592601960[6] = 0;
   out_6715358374592601960[7] = 0;
   out_6715358374592601960[8] = 0;
}
void h_26(double *state, double *unused, double *out_3941839072530820280) {
   out_3941839072530820280[0] = state[7];
}
void H_26(double *state, double *unused, double *out_5929165363339049986) {
   out_5929165363339049986[0] = 0;
   out_5929165363339049986[1] = 0;
   out_5929165363339049986[2] = 0;
   out_5929165363339049986[3] = 0;
   out_5929165363339049986[4] = 0;
   out_5929165363339049986[5] = 0;
   out_5929165363339049986[6] = 0;
   out_5929165363339049986[7] = 1;
   out_5929165363339049986[8] = 0;
}
void h_27(double *state, double *unused, double *out_7764948308525686255) {
   out_7764948308525686255[0] = state[3];
}
void H_27(double *state, double *unused, double *out_8890121686393026871) {
   out_8890121686393026871[0] = 0;
   out_8890121686393026871[1] = 0;
   out_8890121686393026871[2] = 0;
   out_8890121686393026871[3] = 1;
   out_8890121686393026871[4] = 0;
   out_8890121686393026871[5] = 0;
   out_8890121686393026871[6] = 0;
   out_8890121686393026871[7] = 0;
   out_8890121686393026871[8] = 0;
}
void h_29(double *state, double *unused, double *out_1479826874621175208) {
   out_1479826874621175208[0] = state[1];
}
void H_29(double *state, double *unused, double *out_6205127030278209776) {
   out_6205127030278209776[0] = 0;
   out_6205127030278209776[1] = 1;
   out_6205127030278209776[2] = 0;
   out_6205127030278209776[3] = 0;
   out_6205127030278209776[4] = 0;
   out_6205127030278209776[5] = 0;
   out_6205127030278209776[6] = 0;
   out_6205127030278209776[7] = 0;
   out_6205127030278209776[8] = 0;
}
void h_28(double *state, double *unused, double *out_6937398475674729436) {
   out_6937398475674729436[0] = state[0];
}
void H_28(double *state, double *unused, double *out_7159218026361811266) {
   out_7159218026361811266[0] = 1;
   out_7159218026361811266[1] = 0;
   out_7159218026361811266[2] = 0;
   out_7159218026361811266[3] = 0;
   out_7159218026361811266[4] = 0;
   out_7159218026361811266[5] = 0;
   out_7159218026361811266[6] = 0;
   out_7159218026361811266[7] = 0;
   out_7159218026361811266[8] = 0;
}
void h_31(double *state, double *unused, double *out_2042672969268997366) {
   out_2042672969268997366[0] = state[8];
}
void H_31(double *state, double *unused, double *out_6555373465572401462) {
   out_6555373465572401462[0] = 0;
   out_6555373465572401462[1] = 0;
   out_6555373465572401462[2] = 0;
   out_6555373465572401462[3] = 0;
   out_6555373465572401462[4] = 0;
   out_6555373465572401462[5] = 0;
   out_6555373465572401462[6] = 0;
   out_6555373465572401462[7] = 0;
   out_6555373465572401462[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_2237090466909891562) {
  err_fun(nom_x, delta_x, out_2237090466909891562);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_7921264511585388702) {
  inv_err_fun(nom_x, true_x, out_7921264511585388702);
}
void car_H_mod_fun(double *state, double *out_4309360915425036189) {
  H_mod_fun(state, out_4309360915425036189);
}
void car_f_fun(double *state, double dt, double *out_6525599712203705111) {
  f_fun(state,  dt, out_6525599712203705111);
}
void car_F_fun(double *state, double dt, double *out_8055578706737644462) {
  F_fun(state,  dt, out_8055578706737644462);
}
void car_h_25(double *state, double *unused, double *out_6597204507449544518) {
  h_25(state, unused, out_6597204507449544518);
}
void car_H_25(double *state, double *unused, double *out_9213052740609701029) {
  H_25(state, unused, out_9213052740609701029);
}
void car_h_24(double *state, double *unused, double *out_6958676434988343269) {
  h_24(state, unused, out_6958676434988343269);
}
void car_H_24(double *state, double *unused, double *out_3085832238448018832) {
  H_24(state, unused, out_3085832238448018832);
}
void car_h_30(double *state, double *unused, double *out_5078704339909656162) {
  h_30(state, unused, out_5078704339909656162);
}
void car_H_30(double *state, double *unused, double *out_6715358374592601960) {
  H_30(state, unused, out_6715358374592601960);
}
void car_h_26(double *state, double *unused, double *out_3941839072530820280) {
  h_26(state, unused, out_3941839072530820280);
}
void car_H_26(double *state, double *unused, double *out_5929165363339049986) {
  H_26(state, unused, out_5929165363339049986);
}
void car_h_27(double *state, double *unused, double *out_7764948308525686255) {
  h_27(state, unused, out_7764948308525686255);
}
void car_H_27(double *state, double *unused, double *out_8890121686393026871) {
  H_27(state, unused, out_8890121686393026871);
}
void car_h_29(double *state, double *unused, double *out_1479826874621175208) {
  h_29(state, unused, out_1479826874621175208);
}
void car_H_29(double *state, double *unused, double *out_6205127030278209776) {
  H_29(state, unused, out_6205127030278209776);
}
void car_h_28(double *state, double *unused, double *out_6937398475674729436) {
  h_28(state, unused, out_6937398475674729436);
}
void car_H_28(double *state, double *unused, double *out_7159218026361811266) {
  H_28(state, unused, out_7159218026361811266);
}
void car_h_31(double *state, double *unused, double *out_2042672969268997366) {
  h_31(state, unused, out_2042672969268997366);
}
void car_H_31(double *state, double *unused, double *out_6555373465572401462) {
  H_31(state, unused, out_6555373465572401462);
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
