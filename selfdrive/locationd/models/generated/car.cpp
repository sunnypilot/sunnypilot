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
 *                      Code generated with SymPy 1.11.1                      *
 *                                                                            *
 *              See http://www.sympy.org/ for more information.               *
 *                                                                            *
 *                         This file is part of 'ekf'                         *
 ******************************************************************************/
void err_fun(double *nom_x, double *delta_x, double *out_3474583283146901891) {
   out_3474583283146901891[0] = delta_x[0] + nom_x[0];
   out_3474583283146901891[1] = delta_x[1] + nom_x[1];
   out_3474583283146901891[2] = delta_x[2] + nom_x[2];
   out_3474583283146901891[3] = delta_x[3] + nom_x[3];
   out_3474583283146901891[4] = delta_x[4] + nom_x[4];
   out_3474583283146901891[5] = delta_x[5] + nom_x[5];
   out_3474583283146901891[6] = delta_x[6] + nom_x[6];
   out_3474583283146901891[7] = delta_x[7] + nom_x[7];
   out_3474583283146901891[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_3780042915982957382) {
   out_3780042915982957382[0] = -nom_x[0] + true_x[0];
   out_3780042915982957382[1] = -nom_x[1] + true_x[1];
   out_3780042915982957382[2] = -nom_x[2] + true_x[2];
   out_3780042915982957382[3] = -nom_x[3] + true_x[3];
   out_3780042915982957382[4] = -nom_x[4] + true_x[4];
   out_3780042915982957382[5] = -nom_x[5] + true_x[5];
   out_3780042915982957382[6] = -nom_x[6] + true_x[6];
   out_3780042915982957382[7] = -nom_x[7] + true_x[7];
   out_3780042915982957382[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_6387042007052378269) {
   out_6387042007052378269[0] = 1.0;
   out_6387042007052378269[1] = 0;
   out_6387042007052378269[2] = 0;
   out_6387042007052378269[3] = 0;
   out_6387042007052378269[4] = 0;
   out_6387042007052378269[5] = 0;
   out_6387042007052378269[6] = 0;
   out_6387042007052378269[7] = 0;
   out_6387042007052378269[8] = 0;
   out_6387042007052378269[9] = 0;
   out_6387042007052378269[10] = 1.0;
   out_6387042007052378269[11] = 0;
   out_6387042007052378269[12] = 0;
   out_6387042007052378269[13] = 0;
   out_6387042007052378269[14] = 0;
   out_6387042007052378269[15] = 0;
   out_6387042007052378269[16] = 0;
   out_6387042007052378269[17] = 0;
   out_6387042007052378269[18] = 0;
   out_6387042007052378269[19] = 0;
   out_6387042007052378269[20] = 1.0;
   out_6387042007052378269[21] = 0;
   out_6387042007052378269[22] = 0;
   out_6387042007052378269[23] = 0;
   out_6387042007052378269[24] = 0;
   out_6387042007052378269[25] = 0;
   out_6387042007052378269[26] = 0;
   out_6387042007052378269[27] = 0;
   out_6387042007052378269[28] = 0;
   out_6387042007052378269[29] = 0;
   out_6387042007052378269[30] = 1.0;
   out_6387042007052378269[31] = 0;
   out_6387042007052378269[32] = 0;
   out_6387042007052378269[33] = 0;
   out_6387042007052378269[34] = 0;
   out_6387042007052378269[35] = 0;
   out_6387042007052378269[36] = 0;
   out_6387042007052378269[37] = 0;
   out_6387042007052378269[38] = 0;
   out_6387042007052378269[39] = 0;
   out_6387042007052378269[40] = 1.0;
   out_6387042007052378269[41] = 0;
   out_6387042007052378269[42] = 0;
   out_6387042007052378269[43] = 0;
   out_6387042007052378269[44] = 0;
   out_6387042007052378269[45] = 0;
   out_6387042007052378269[46] = 0;
   out_6387042007052378269[47] = 0;
   out_6387042007052378269[48] = 0;
   out_6387042007052378269[49] = 0;
   out_6387042007052378269[50] = 1.0;
   out_6387042007052378269[51] = 0;
   out_6387042007052378269[52] = 0;
   out_6387042007052378269[53] = 0;
   out_6387042007052378269[54] = 0;
   out_6387042007052378269[55] = 0;
   out_6387042007052378269[56] = 0;
   out_6387042007052378269[57] = 0;
   out_6387042007052378269[58] = 0;
   out_6387042007052378269[59] = 0;
   out_6387042007052378269[60] = 1.0;
   out_6387042007052378269[61] = 0;
   out_6387042007052378269[62] = 0;
   out_6387042007052378269[63] = 0;
   out_6387042007052378269[64] = 0;
   out_6387042007052378269[65] = 0;
   out_6387042007052378269[66] = 0;
   out_6387042007052378269[67] = 0;
   out_6387042007052378269[68] = 0;
   out_6387042007052378269[69] = 0;
   out_6387042007052378269[70] = 1.0;
   out_6387042007052378269[71] = 0;
   out_6387042007052378269[72] = 0;
   out_6387042007052378269[73] = 0;
   out_6387042007052378269[74] = 0;
   out_6387042007052378269[75] = 0;
   out_6387042007052378269[76] = 0;
   out_6387042007052378269[77] = 0;
   out_6387042007052378269[78] = 0;
   out_6387042007052378269[79] = 0;
   out_6387042007052378269[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_5471630993470310399) {
   out_5471630993470310399[0] = state[0];
   out_5471630993470310399[1] = state[1];
   out_5471630993470310399[2] = state[2];
   out_5471630993470310399[3] = state[3];
   out_5471630993470310399[4] = state[4];
   out_5471630993470310399[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8000000000000007*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_5471630993470310399[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_5471630993470310399[7] = state[7];
   out_5471630993470310399[8] = state[8];
}
void F_fun(double *state, double dt, double *out_8523483091456656155) {
   out_8523483091456656155[0] = 1;
   out_8523483091456656155[1] = 0;
   out_8523483091456656155[2] = 0;
   out_8523483091456656155[3] = 0;
   out_8523483091456656155[4] = 0;
   out_8523483091456656155[5] = 0;
   out_8523483091456656155[6] = 0;
   out_8523483091456656155[7] = 0;
   out_8523483091456656155[8] = 0;
   out_8523483091456656155[9] = 0;
   out_8523483091456656155[10] = 1;
   out_8523483091456656155[11] = 0;
   out_8523483091456656155[12] = 0;
   out_8523483091456656155[13] = 0;
   out_8523483091456656155[14] = 0;
   out_8523483091456656155[15] = 0;
   out_8523483091456656155[16] = 0;
   out_8523483091456656155[17] = 0;
   out_8523483091456656155[18] = 0;
   out_8523483091456656155[19] = 0;
   out_8523483091456656155[20] = 1;
   out_8523483091456656155[21] = 0;
   out_8523483091456656155[22] = 0;
   out_8523483091456656155[23] = 0;
   out_8523483091456656155[24] = 0;
   out_8523483091456656155[25] = 0;
   out_8523483091456656155[26] = 0;
   out_8523483091456656155[27] = 0;
   out_8523483091456656155[28] = 0;
   out_8523483091456656155[29] = 0;
   out_8523483091456656155[30] = 1;
   out_8523483091456656155[31] = 0;
   out_8523483091456656155[32] = 0;
   out_8523483091456656155[33] = 0;
   out_8523483091456656155[34] = 0;
   out_8523483091456656155[35] = 0;
   out_8523483091456656155[36] = 0;
   out_8523483091456656155[37] = 0;
   out_8523483091456656155[38] = 0;
   out_8523483091456656155[39] = 0;
   out_8523483091456656155[40] = 1;
   out_8523483091456656155[41] = 0;
   out_8523483091456656155[42] = 0;
   out_8523483091456656155[43] = 0;
   out_8523483091456656155[44] = 0;
   out_8523483091456656155[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_8523483091456656155[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_8523483091456656155[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_8523483091456656155[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_8523483091456656155[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_8523483091456656155[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_8523483091456656155[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_8523483091456656155[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_8523483091456656155[53] = -9.8000000000000007*dt;
   out_8523483091456656155[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_8523483091456656155[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_8523483091456656155[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_8523483091456656155[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_8523483091456656155[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_8523483091456656155[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_8523483091456656155[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_8523483091456656155[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_8523483091456656155[62] = 0;
   out_8523483091456656155[63] = 0;
   out_8523483091456656155[64] = 0;
   out_8523483091456656155[65] = 0;
   out_8523483091456656155[66] = 0;
   out_8523483091456656155[67] = 0;
   out_8523483091456656155[68] = 0;
   out_8523483091456656155[69] = 0;
   out_8523483091456656155[70] = 1;
   out_8523483091456656155[71] = 0;
   out_8523483091456656155[72] = 0;
   out_8523483091456656155[73] = 0;
   out_8523483091456656155[74] = 0;
   out_8523483091456656155[75] = 0;
   out_8523483091456656155[76] = 0;
   out_8523483091456656155[77] = 0;
   out_8523483091456656155[78] = 0;
   out_8523483091456656155[79] = 0;
   out_8523483091456656155[80] = 1;
}
void h_25(double *state, double *unused, double *out_6525986448049520314) {
   out_6525986448049520314[0] = state[6];
}
void H_25(double *state, double *unused, double *out_793230131916196905) {
   out_793230131916196905[0] = 0;
   out_793230131916196905[1] = 0;
   out_793230131916196905[2] = 0;
   out_793230131916196905[3] = 0;
   out_793230131916196905[4] = 0;
   out_793230131916196905[5] = 0;
   out_793230131916196905[6] = 1;
   out_793230131916196905[7] = 0;
   out_793230131916196905[8] = 0;
}
void h_24(double *state, double *unused, double *out_1498456185202745162) {
   out_1498456185202745162[0] = state[4];
   out_1498456185202745162[1] = state[5];
}
void H_24(double *state, double *unused, double *out_2965879730921696471) {
   out_2965879730921696471[0] = 0;
   out_2965879730921696471[1] = 0;
   out_2965879730921696471[2] = 0;
   out_2965879730921696471[3] = 0;
   out_2965879730921696471[4] = 1;
   out_2965879730921696471[5] = 0;
   out_2965879730921696471[6] = 0;
   out_2965879730921696471[7] = 0;
   out_2965879730921696471[8] = 0;
   out_2965879730921696471[9] = 0;
   out_2965879730921696471[10] = 0;
   out_2965879730921696471[11] = 0;
   out_2965879730921696471[12] = 0;
   out_2965879730921696471[13] = 0;
   out_2965879730921696471[14] = 1;
   out_2965879730921696471[15] = 0;
   out_2965879730921696471[16] = 0;
   out_2965879730921696471[17] = 0;
}
void h_30(double *state, double *unused, double *out_6671506272270175285) {
   out_6671506272270175285[0] = state[4];
}
void H_30(double *state, double *unused, double *out_1725102826591051722) {
   out_1725102826591051722[0] = 0;
   out_1725102826591051722[1] = 0;
   out_1725102826591051722[2] = 0;
   out_1725102826591051722[3] = 0;
   out_1725102826591051722[4] = 1;
   out_1725102826591051722[5] = 0;
   out_1725102826591051722[6] = 0;
   out_1725102826591051722[7] = 0;
   out_1725102826591051722[8] = 0;
}
void h_26(double *state, double *unused, double *out_1445599056434850338) {
   out_1445599056434850338[0] = state[7];
}
void H_26(double *state, double *unused, double *out_4534733450790253129) {
   out_4534733450790253129[0] = 0;
   out_4534733450790253129[1] = 0;
   out_4534733450790253129[2] = 0;
   out_4534733450790253129[3] = 0;
   out_4534733450790253129[4] = 0;
   out_4534733450790253129[5] = 0;
   out_4534733450790253129[6] = 0;
   out_4534733450790253129[7] = 1;
   out_4534733450790253129[8] = 0;
}
void h_27(double *state, double *unused, double *out_6172146376165167132) {
   out_6172146376165167132[0] = state[3];
}
void H_27(double *state, double *unused, double *out_3948696897774994939) {
   out_3948696897774994939[0] = 0;
   out_3948696897774994939[1] = 0;
   out_3948696897774994939[2] = 0;
   out_3948696897774994939[3] = 1;
   out_3948696897774994939[4] = 0;
   out_3948696897774994939[5] = 0;
   out_3948696897774994939[6] = 0;
   out_3948696897774994939[7] = 0;
   out_3948696897774994939[8] = 0;
}
void h_29(double *state, double *unused, double *out_3634720220825842600) {
   out_3634720220825842600[0] = state[1];
}
void H_29(double *state, double *unused, double *out_2235334170905443906) {
   out_2235334170905443906[0] = 0;
   out_2235334170905443906[1] = 1;
   out_2235334170905443906[2] = 0;
   out_2235334170905443906[3] = 0;
   out_2235334170905443906[4] = 0;
   out_2235334170905443906[5] = 0;
   out_2235334170905443906[6] = 0;
   out_2235334170905443906[7] = 0;
   out_2235334170905443906[8] = 0;
}
void h_28(double *state, double *unused, double *out_1170473108504321487) {
   out_1170473108504321487[0] = state[0];
}
void H_28(double *state, double *unused, double *out_2847064846164086668) {
   out_2847064846164086668[0] = 1;
   out_2847064846164086668[1] = 0;
   out_2847064846164086668[2] = 0;
   out_2847064846164086668[3] = 0;
   out_2847064846164086668[4] = 0;
   out_2847064846164086668[5] = 0;
   out_2847064846164086668[6] = 0;
   out_2847064846164086668[7] = 0;
   out_2847064846164086668[8] = 0;
}
void h_31(double *state, double *unused, double *out_4157492368839358861) {
   out_4157492368839358861[0] = state[8];
}
void H_31(double *state, double *unused, double *out_5160941553023604605) {
   out_5160941553023604605[0] = 0;
   out_5160941553023604605[1] = 0;
   out_5160941553023604605[2] = 0;
   out_5160941553023604605[3] = 0;
   out_5160941553023604605[4] = 0;
   out_5160941553023604605[5] = 0;
   out_5160941553023604605[6] = 0;
   out_5160941553023604605[7] = 0;
   out_5160941553023604605[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_3474583283146901891) {
  err_fun(nom_x, delta_x, out_3474583283146901891);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_3780042915982957382) {
  inv_err_fun(nom_x, true_x, out_3780042915982957382);
}
void car_H_mod_fun(double *state, double *out_6387042007052378269) {
  H_mod_fun(state, out_6387042007052378269);
}
void car_f_fun(double *state, double dt, double *out_5471630993470310399) {
  f_fun(state,  dt, out_5471630993470310399);
}
void car_F_fun(double *state, double dt, double *out_8523483091456656155) {
  F_fun(state,  dt, out_8523483091456656155);
}
void car_h_25(double *state, double *unused, double *out_6525986448049520314) {
  h_25(state, unused, out_6525986448049520314);
}
void car_H_25(double *state, double *unused, double *out_793230131916196905) {
  H_25(state, unused, out_793230131916196905);
}
void car_h_24(double *state, double *unused, double *out_1498456185202745162) {
  h_24(state, unused, out_1498456185202745162);
}
void car_H_24(double *state, double *unused, double *out_2965879730921696471) {
  H_24(state, unused, out_2965879730921696471);
}
void car_h_30(double *state, double *unused, double *out_6671506272270175285) {
  h_30(state, unused, out_6671506272270175285);
}
void car_H_30(double *state, double *unused, double *out_1725102826591051722) {
  H_30(state, unused, out_1725102826591051722);
}
void car_h_26(double *state, double *unused, double *out_1445599056434850338) {
  h_26(state, unused, out_1445599056434850338);
}
void car_H_26(double *state, double *unused, double *out_4534733450790253129) {
  H_26(state, unused, out_4534733450790253129);
}
void car_h_27(double *state, double *unused, double *out_6172146376165167132) {
  h_27(state, unused, out_6172146376165167132);
}
void car_H_27(double *state, double *unused, double *out_3948696897774994939) {
  H_27(state, unused, out_3948696897774994939);
}
void car_h_29(double *state, double *unused, double *out_3634720220825842600) {
  h_29(state, unused, out_3634720220825842600);
}
void car_H_29(double *state, double *unused, double *out_2235334170905443906) {
  H_29(state, unused, out_2235334170905443906);
}
void car_h_28(double *state, double *unused, double *out_1170473108504321487) {
  h_28(state, unused, out_1170473108504321487);
}
void car_H_28(double *state, double *unused, double *out_2847064846164086668) {
  H_28(state, unused, out_2847064846164086668);
}
void car_h_31(double *state, double *unused, double *out_4157492368839358861) {
  h_31(state, unused, out_4157492368839358861);
}
void car_H_31(double *state, double *unused, double *out_5160941553023604605) {
  H_31(state, unused, out_5160941553023604605);
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

ekf_init(car);
