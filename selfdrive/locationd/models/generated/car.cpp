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
void err_fun(double *nom_x, double *delta_x, double *out_5118140892357841772) {
   out_5118140892357841772[0] = delta_x[0] + nom_x[0];
   out_5118140892357841772[1] = delta_x[1] + nom_x[1];
   out_5118140892357841772[2] = delta_x[2] + nom_x[2];
   out_5118140892357841772[3] = delta_x[3] + nom_x[3];
   out_5118140892357841772[4] = delta_x[4] + nom_x[4];
   out_5118140892357841772[5] = delta_x[5] + nom_x[5];
   out_5118140892357841772[6] = delta_x[6] + nom_x[6];
   out_5118140892357841772[7] = delta_x[7] + nom_x[7];
   out_5118140892357841772[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_4745321206345718051) {
   out_4745321206345718051[0] = -nom_x[0] + true_x[0];
   out_4745321206345718051[1] = -nom_x[1] + true_x[1];
   out_4745321206345718051[2] = -nom_x[2] + true_x[2];
   out_4745321206345718051[3] = -nom_x[3] + true_x[3];
   out_4745321206345718051[4] = -nom_x[4] + true_x[4];
   out_4745321206345718051[5] = -nom_x[5] + true_x[5];
   out_4745321206345718051[6] = -nom_x[6] + true_x[6];
   out_4745321206345718051[7] = -nom_x[7] + true_x[7];
   out_4745321206345718051[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_2596711998114896803) {
   out_2596711998114896803[0] = 1.0;
   out_2596711998114896803[1] = 0.0;
   out_2596711998114896803[2] = 0.0;
   out_2596711998114896803[3] = 0.0;
   out_2596711998114896803[4] = 0.0;
   out_2596711998114896803[5] = 0.0;
   out_2596711998114896803[6] = 0.0;
   out_2596711998114896803[7] = 0.0;
   out_2596711998114896803[8] = 0.0;
   out_2596711998114896803[9] = 0.0;
   out_2596711998114896803[10] = 1.0;
   out_2596711998114896803[11] = 0.0;
   out_2596711998114896803[12] = 0.0;
   out_2596711998114896803[13] = 0.0;
   out_2596711998114896803[14] = 0.0;
   out_2596711998114896803[15] = 0.0;
   out_2596711998114896803[16] = 0.0;
   out_2596711998114896803[17] = 0.0;
   out_2596711998114896803[18] = 0.0;
   out_2596711998114896803[19] = 0.0;
   out_2596711998114896803[20] = 1.0;
   out_2596711998114896803[21] = 0.0;
   out_2596711998114896803[22] = 0.0;
   out_2596711998114896803[23] = 0.0;
   out_2596711998114896803[24] = 0.0;
   out_2596711998114896803[25] = 0.0;
   out_2596711998114896803[26] = 0.0;
   out_2596711998114896803[27] = 0.0;
   out_2596711998114896803[28] = 0.0;
   out_2596711998114896803[29] = 0.0;
   out_2596711998114896803[30] = 1.0;
   out_2596711998114896803[31] = 0.0;
   out_2596711998114896803[32] = 0.0;
   out_2596711998114896803[33] = 0.0;
   out_2596711998114896803[34] = 0.0;
   out_2596711998114896803[35] = 0.0;
   out_2596711998114896803[36] = 0.0;
   out_2596711998114896803[37] = 0.0;
   out_2596711998114896803[38] = 0.0;
   out_2596711998114896803[39] = 0.0;
   out_2596711998114896803[40] = 1.0;
   out_2596711998114896803[41] = 0.0;
   out_2596711998114896803[42] = 0.0;
   out_2596711998114896803[43] = 0.0;
   out_2596711998114896803[44] = 0.0;
   out_2596711998114896803[45] = 0.0;
   out_2596711998114896803[46] = 0.0;
   out_2596711998114896803[47] = 0.0;
   out_2596711998114896803[48] = 0.0;
   out_2596711998114896803[49] = 0.0;
   out_2596711998114896803[50] = 1.0;
   out_2596711998114896803[51] = 0.0;
   out_2596711998114896803[52] = 0.0;
   out_2596711998114896803[53] = 0.0;
   out_2596711998114896803[54] = 0.0;
   out_2596711998114896803[55] = 0.0;
   out_2596711998114896803[56] = 0.0;
   out_2596711998114896803[57] = 0.0;
   out_2596711998114896803[58] = 0.0;
   out_2596711998114896803[59] = 0.0;
   out_2596711998114896803[60] = 1.0;
   out_2596711998114896803[61] = 0.0;
   out_2596711998114896803[62] = 0.0;
   out_2596711998114896803[63] = 0.0;
   out_2596711998114896803[64] = 0.0;
   out_2596711998114896803[65] = 0.0;
   out_2596711998114896803[66] = 0.0;
   out_2596711998114896803[67] = 0.0;
   out_2596711998114896803[68] = 0.0;
   out_2596711998114896803[69] = 0.0;
   out_2596711998114896803[70] = 1.0;
   out_2596711998114896803[71] = 0.0;
   out_2596711998114896803[72] = 0.0;
   out_2596711998114896803[73] = 0.0;
   out_2596711998114896803[74] = 0.0;
   out_2596711998114896803[75] = 0.0;
   out_2596711998114896803[76] = 0.0;
   out_2596711998114896803[77] = 0.0;
   out_2596711998114896803[78] = 0.0;
   out_2596711998114896803[79] = 0.0;
   out_2596711998114896803[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_6942410117250554106) {
   out_6942410117250554106[0] = state[0];
   out_6942410117250554106[1] = state[1];
   out_6942410117250554106[2] = state[2];
   out_6942410117250554106[3] = state[3];
   out_6942410117250554106[4] = state[4];
   out_6942410117250554106[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8100000000000005*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_6942410117250554106[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_6942410117250554106[7] = state[7];
   out_6942410117250554106[8] = state[8];
}
void F_fun(double *state, double dt, double *out_8478175790585558502) {
   out_8478175790585558502[0] = 1;
   out_8478175790585558502[1] = 0;
   out_8478175790585558502[2] = 0;
   out_8478175790585558502[3] = 0;
   out_8478175790585558502[4] = 0;
   out_8478175790585558502[5] = 0;
   out_8478175790585558502[6] = 0;
   out_8478175790585558502[7] = 0;
   out_8478175790585558502[8] = 0;
   out_8478175790585558502[9] = 0;
   out_8478175790585558502[10] = 1;
   out_8478175790585558502[11] = 0;
   out_8478175790585558502[12] = 0;
   out_8478175790585558502[13] = 0;
   out_8478175790585558502[14] = 0;
   out_8478175790585558502[15] = 0;
   out_8478175790585558502[16] = 0;
   out_8478175790585558502[17] = 0;
   out_8478175790585558502[18] = 0;
   out_8478175790585558502[19] = 0;
   out_8478175790585558502[20] = 1;
   out_8478175790585558502[21] = 0;
   out_8478175790585558502[22] = 0;
   out_8478175790585558502[23] = 0;
   out_8478175790585558502[24] = 0;
   out_8478175790585558502[25] = 0;
   out_8478175790585558502[26] = 0;
   out_8478175790585558502[27] = 0;
   out_8478175790585558502[28] = 0;
   out_8478175790585558502[29] = 0;
   out_8478175790585558502[30] = 1;
   out_8478175790585558502[31] = 0;
   out_8478175790585558502[32] = 0;
   out_8478175790585558502[33] = 0;
   out_8478175790585558502[34] = 0;
   out_8478175790585558502[35] = 0;
   out_8478175790585558502[36] = 0;
   out_8478175790585558502[37] = 0;
   out_8478175790585558502[38] = 0;
   out_8478175790585558502[39] = 0;
   out_8478175790585558502[40] = 1;
   out_8478175790585558502[41] = 0;
   out_8478175790585558502[42] = 0;
   out_8478175790585558502[43] = 0;
   out_8478175790585558502[44] = 0;
   out_8478175790585558502[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_8478175790585558502[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_8478175790585558502[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_8478175790585558502[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_8478175790585558502[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_8478175790585558502[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_8478175790585558502[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_8478175790585558502[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_8478175790585558502[53] = -9.8100000000000005*dt;
   out_8478175790585558502[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_8478175790585558502[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_8478175790585558502[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_8478175790585558502[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_8478175790585558502[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_8478175790585558502[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_8478175790585558502[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_8478175790585558502[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_8478175790585558502[62] = 0;
   out_8478175790585558502[63] = 0;
   out_8478175790585558502[64] = 0;
   out_8478175790585558502[65] = 0;
   out_8478175790585558502[66] = 0;
   out_8478175790585558502[67] = 0;
   out_8478175790585558502[68] = 0;
   out_8478175790585558502[69] = 0;
   out_8478175790585558502[70] = 1;
   out_8478175790585558502[71] = 0;
   out_8478175790585558502[72] = 0;
   out_8478175790585558502[73] = 0;
   out_8478175790585558502[74] = 0;
   out_8478175790585558502[75] = 0;
   out_8478175790585558502[76] = 0;
   out_8478175790585558502[77] = 0;
   out_8478175790585558502[78] = 0;
   out_8478175790585558502[79] = 0;
   out_8478175790585558502[80] = 1;
}
void h_25(double *state, double *unused, double *out_5217460560532285521) {
   out_5217460560532285521[0] = state[6];
}
void H_25(double *state, double *unused, double *out_926268651874594874) {
   out_926268651874594874[0] = 0;
   out_926268651874594874[1] = 0;
   out_926268651874594874[2] = 0;
   out_926268651874594874[3] = 0;
   out_926268651874594874[4] = 0;
   out_926268651874594874[5] = 0;
   out_926268651874594874[6] = 1;
   out_926268651874594874[7] = 0;
   out_926268651874594874[8] = 0;
}
void h_24(double *state, double *unused, double *out_5731469901121999514) {
   out_5731469901121999514[0] = state[4];
   out_5731469901121999514[1] = state[5];
}
void H_24(double *state, double *unused, double *out_7501840458466112975) {
   out_7501840458466112975[0] = 0;
   out_7501840458466112975[1] = 0;
   out_7501840458466112975[2] = 0;
   out_7501840458466112975[3] = 0;
   out_7501840458466112975[4] = 1;
   out_7501840458466112975[5] = 0;
   out_7501840458466112975[6] = 0;
   out_7501840458466112975[7] = 0;
   out_7501840458466112975[8] = 0;
   out_7501840458466112975[9] = 0;
   out_7501840458466112975[10] = 0;
   out_7501840458466112975[11] = 0;
   out_7501840458466112975[12] = 0;
   out_7501840458466112975[13] = 0;
   out_7501840458466112975[14] = 1;
   out_7501840458466112975[15] = 0;
   out_7501840458466112975[16] = 0;
   out_7501840458466112975[17] = 0;
}
void h_30(double *state, double *unused, double *out_1580011032278263171) {
   out_1580011032278263171[0] = state[4];
}
void H_30(double *state, double *unused, double *out_7842958993366211629) {
   out_7842958993366211629[0] = 0;
   out_7842958993366211629[1] = 0;
   out_7842958993366211629[2] = 0;
   out_7842958993366211629[3] = 0;
   out_7842958993366211629[4] = 1;
   out_7842958993366211629[5] = 0;
   out_7842958993366211629[6] = 0;
   out_7842958993366211629[7] = 0;
   out_7842958993366211629[8] = 0;
}
void h_26(double *state, double *unused, double *out_7458296519836978259) {
   out_7458296519836978259[0] = state[7];
}
void H_26(double *state, double *unused, double *out_1583122715984906778) {
   out_1583122715984906778[0] = 0;
   out_1583122715984906778[1] = 0;
   out_1583122715984906778[2] = 0;
   out_1583122715984906778[3] = 0;
   out_1583122715984906778[4] = 0;
   out_1583122715984906778[5] = 0;
   out_1583122715984906778[6] = 0;
   out_1583122715984906778[7] = 1;
   out_1583122715984906778[8] = 0;
}
void h_27(double *state, double *unused, double *out_3545652929298450020) {
   out_3545652929298450020[0] = state[3];
}
void H_27(double *state, double *unused, double *out_5668195681565786718) {
   out_5668195681565786718[0] = 0;
   out_5668195681565786718[1] = 0;
   out_5668195681565786718[2] = 0;
   out_5668195681565786718[3] = 1;
   out_5668195681565786718[4] = 0;
   out_5668195681565786718[5] = 0;
   out_5668195681565786718[6] = 0;
   out_5668195681565786718[7] = 0;
   out_5668195681565786718[8] = 0;
}
void h_29(double *state, double *unused, double *out_7065095063619095626) {
   out_7065095063619095626[0] = state[1];
}
void H_29(double *state, double *unused, double *out_8353190337680603813) {
   out_8353190337680603813[0] = 0;
   out_8353190337680603813[1] = 1;
   out_8353190337680603813[2] = 0;
   out_8353190337680603813[3] = 0;
   out_8353190337680603813[4] = 0;
   out_8353190337680603813[5] = 0;
   out_8353190337680603813[6] = 0;
   out_8353190337680603813[7] = 0;
   out_8353190337680603813[8] = 0;
}
void h_28(double *state, double *unused, double *out_8502049626997252450) {
   out_8502049626997252450[0] = state[0];
}
void H_28(double *state, double *unused, double *out_3270791320611073239) {
   out_3270791320611073239[0] = 1;
   out_3270791320611073239[1] = 0;
   out_3270791320611073239[2] = 0;
   out_3270791320611073239[3] = 0;
   out_3270791320611073239[4] = 0;
   out_3270791320611073239[5] = 0;
   out_3270791320611073239[6] = 0;
   out_3270791320611073239[7] = 0;
   out_3270791320611073239[8] = 0;
}
void h_31(double *state, double *unused, double *out_6261968348496233601) {
   out_6261968348496233601[0] = state[8];
}
void H_31(double *state, double *unused, double *out_956914613751555302) {
   out_956914613751555302[0] = 0;
   out_956914613751555302[1] = 0;
   out_956914613751555302[2] = 0;
   out_956914613751555302[3] = 0;
   out_956914613751555302[4] = 0;
   out_956914613751555302[5] = 0;
   out_956914613751555302[6] = 0;
   out_956914613751555302[7] = 0;
   out_956914613751555302[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_5118140892357841772) {
  err_fun(nom_x, delta_x, out_5118140892357841772);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_4745321206345718051) {
  inv_err_fun(nom_x, true_x, out_4745321206345718051);
}
void car_H_mod_fun(double *state, double *out_2596711998114896803) {
  H_mod_fun(state, out_2596711998114896803);
}
void car_f_fun(double *state, double dt, double *out_6942410117250554106) {
  f_fun(state,  dt, out_6942410117250554106);
}
void car_F_fun(double *state, double dt, double *out_8478175790585558502) {
  F_fun(state,  dt, out_8478175790585558502);
}
void car_h_25(double *state, double *unused, double *out_5217460560532285521) {
  h_25(state, unused, out_5217460560532285521);
}
void car_H_25(double *state, double *unused, double *out_926268651874594874) {
  H_25(state, unused, out_926268651874594874);
}
void car_h_24(double *state, double *unused, double *out_5731469901121999514) {
  h_24(state, unused, out_5731469901121999514);
}
void car_H_24(double *state, double *unused, double *out_7501840458466112975) {
  H_24(state, unused, out_7501840458466112975);
}
void car_h_30(double *state, double *unused, double *out_1580011032278263171) {
  h_30(state, unused, out_1580011032278263171);
}
void car_H_30(double *state, double *unused, double *out_7842958993366211629) {
  H_30(state, unused, out_7842958993366211629);
}
void car_h_26(double *state, double *unused, double *out_7458296519836978259) {
  h_26(state, unused, out_7458296519836978259);
}
void car_H_26(double *state, double *unused, double *out_1583122715984906778) {
  H_26(state, unused, out_1583122715984906778);
}
void car_h_27(double *state, double *unused, double *out_3545652929298450020) {
  h_27(state, unused, out_3545652929298450020);
}
void car_H_27(double *state, double *unused, double *out_5668195681565786718) {
  H_27(state, unused, out_5668195681565786718);
}
void car_h_29(double *state, double *unused, double *out_7065095063619095626) {
  h_29(state, unused, out_7065095063619095626);
}
void car_H_29(double *state, double *unused, double *out_8353190337680603813) {
  H_29(state, unused, out_8353190337680603813);
}
void car_h_28(double *state, double *unused, double *out_8502049626997252450) {
  h_28(state, unused, out_8502049626997252450);
}
void car_H_28(double *state, double *unused, double *out_3270791320611073239) {
  H_28(state, unused, out_3270791320611073239);
}
void car_h_31(double *state, double *unused, double *out_6261968348496233601) {
  h_31(state, unused, out_6261968348496233601);
}
void car_H_31(double *state, double *unused, double *out_956914613751555302) {
  H_31(state, unused, out_956914613751555302);
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
