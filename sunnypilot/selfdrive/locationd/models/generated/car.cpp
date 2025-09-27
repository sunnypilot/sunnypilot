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
void err_fun(double *nom_x, double *delta_x, double *out_8815656279812630393) {
   out_8815656279812630393[0] = delta_x[0] + nom_x[0];
   out_8815656279812630393[1] = delta_x[1] + nom_x[1];
   out_8815656279812630393[2] = delta_x[2] + nom_x[2];
   out_8815656279812630393[3] = delta_x[3] + nom_x[3];
   out_8815656279812630393[4] = delta_x[4] + nom_x[4];
   out_8815656279812630393[5] = delta_x[5] + nom_x[5];
   out_8815656279812630393[6] = delta_x[6] + nom_x[6];
   out_8815656279812630393[7] = delta_x[7] + nom_x[7];
   out_8815656279812630393[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_2634005456400563428) {
   out_2634005456400563428[0] = -nom_x[0] + true_x[0];
   out_2634005456400563428[1] = -nom_x[1] + true_x[1];
   out_2634005456400563428[2] = -nom_x[2] + true_x[2];
   out_2634005456400563428[3] = -nom_x[3] + true_x[3];
   out_2634005456400563428[4] = -nom_x[4] + true_x[4];
   out_2634005456400563428[5] = -nom_x[5] + true_x[5];
   out_2634005456400563428[6] = -nom_x[6] + true_x[6];
   out_2634005456400563428[7] = -nom_x[7] + true_x[7];
   out_2634005456400563428[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_5776307114296964175) {
   out_5776307114296964175[0] = 1.0;
   out_5776307114296964175[1] = 0.0;
   out_5776307114296964175[2] = 0.0;
   out_5776307114296964175[3] = 0.0;
   out_5776307114296964175[4] = 0.0;
   out_5776307114296964175[5] = 0.0;
   out_5776307114296964175[6] = 0.0;
   out_5776307114296964175[7] = 0.0;
   out_5776307114296964175[8] = 0.0;
   out_5776307114296964175[9] = 0.0;
   out_5776307114296964175[10] = 1.0;
   out_5776307114296964175[11] = 0.0;
   out_5776307114296964175[12] = 0.0;
   out_5776307114296964175[13] = 0.0;
   out_5776307114296964175[14] = 0.0;
   out_5776307114296964175[15] = 0.0;
   out_5776307114296964175[16] = 0.0;
   out_5776307114296964175[17] = 0.0;
   out_5776307114296964175[18] = 0.0;
   out_5776307114296964175[19] = 0.0;
   out_5776307114296964175[20] = 1.0;
   out_5776307114296964175[21] = 0.0;
   out_5776307114296964175[22] = 0.0;
   out_5776307114296964175[23] = 0.0;
   out_5776307114296964175[24] = 0.0;
   out_5776307114296964175[25] = 0.0;
   out_5776307114296964175[26] = 0.0;
   out_5776307114296964175[27] = 0.0;
   out_5776307114296964175[28] = 0.0;
   out_5776307114296964175[29] = 0.0;
   out_5776307114296964175[30] = 1.0;
   out_5776307114296964175[31] = 0.0;
   out_5776307114296964175[32] = 0.0;
   out_5776307114296964175[33] = 0.0;
   out_5776307114296964175[34] = 0.0;
   out_5776307114296964175[35] = 0.0;
   out_5776307114296964175[36] = 0.0;
   out_5776307114296964175[37] = 0.0;
   out_5776307114296964175[38] = 0.0;
   out_5776307114296964175[39] = 0.0;
   out_5776307114296964175[40] = 1.0;
   out_5776307114296964175[41] = 0.0;
   out_5776307114296964175[42] = 0.0;
   out_5776307114296964175[43] = 0.0;
   out_5776307114296964175[44] = 0.0;
   out_5776307114296964175[45] = 0.0;
   out_5776307114296964175[46] = 0.0;
   out_5776307114296964175[47] = 0.0;
   out_5776307114296964175[48] = 0.0;
   out_5776307114296964175[49] = 0.0;
   out_5776307114296964175[50] = 1.0;
   out_5776307114296964175[51] = 0.0;
   out_5776307114296964175[52] = 0.0;
   out_5776307114296964175[53] = 0.0;
   out_5776307114296964175[54] = 0.0;
   out_5776307114296964175[55] = 0.0;
   out_5776307114296964175[56] = 0.0;
   out_5776307114296964175[57] = 0.0;
   out_5776307114296964175[58] = 0.0;
   out_5776307114296964175[59] = 0.0;
   out_5776307114296964175[60] = 1.0;
   out_5776307114296964175[61] = 0.0;
   out_5776307114296964175[62] = 0.0;
   out_5776307114296964175[63] = 0.0;
   out_5776307114296964175[64] = 0.0;
   out_5776307114296964175[65] = 0.0;
   out_5776307114296964175[66] = 0.0;
   out_5776307114296964175[67] = 0.0;
   out_5776307114296964175[68] = 0.0;
   out_5776307114296964175[69] = 0.0;
   out_5776307114296964175[70] = 1.0;
   out_5776307114296964175[71] = 0.0;
   out_5776307114296964175[72] = 0.0;
   out_5776307114296964175[73] = 0.0;
   out_5776307114296964175[74] = 0.0;
   out_5776307114296964175[75] = 0.0;
   out_5776307114296964175[76] = 0.0;
   out_5776307114296964175[77] = 0.0;
   out_5776307114296964175[78] = 0.0;
   out_5776307114296964175[79] = 0.0;
   out_5776307114296964175[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_3329281261028883663) {
   out_3329281261028883663[0] = state[0];
   out_3329281261028883663[1] = state[1];
   out_3329281261028883663[2] = state[2];
   out_3329281261028883663[3] = state[3];
   out_3329281261028883663[4] = state[4];
   out_3329281261028883663[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8100000000000005*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_3329281261028883663[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_3329281261028883663[7] = state[7];
   out_3329281261028883663[8] = state[8];
}
void F_fun(double *state, double dt, double *out_1569093053633695445) {
   out_1569093053633695445[0] = 1;
   out_1569093053633695445[1] = 0;
   out_1569093053633695445[2] = 0;
   out_1569093053633695445[3] = 0;
   out_1569093053633695445[4] = 0;
   out_1569093053633695445[5] = 0;
   out_1569093053633695445[6] = 0;
   out_1569093053633695445[7] = 0;
   out_1569093053633695445[8] = 0;
   out_1569093053633695445[9] = 0;
   out_1569093053633695445[10] = 1;
   out_1569093053633695445[11] = 0;
   out_1569093053633695445[12] = 0;
   out_1569093053633695445[13] = 0;
   out_1569093053633695445[14] = 0;
   out_1569093053633695445[15] = 0;
   out_1569093053633695445[16] = 0;
   out_1569093053633695445[17] = 0;
   out_1569093053633695445[18] = 0;
   out_1569093053633695445[19] = 0;
   out_1569093053633695445[20] = 1;
   out_1569093053633695445[21] = 0;
   out_1569093053633695445[22] = 0;
   out_1569093053633695445[23] = 0;
   out_1569093053633695445[24] = 0;
   out_1569093053633695445[25] = 0;
   out_1569093053633695445[26] = 0;
   out_1569093053633695445[27] = 0;
   out_1569093053633695445[28] = 0;
   out_1569093053633695445[29] = 0;
   out_1569093053633695445[30] = 1;
   out_1569093053633695445[31] = 0;
   out_1569093053633695445[32] = 0;
   out_1569093053633695445[33] = 0;
   out_1569093053633695445[34] = 0;
   out_1569093053633695445[35] = 0;
   out_1569093053633695445[36] = 0;
   out_1569093053633695445[37] = 0;
   out_1569093053633695445[38] = 0;
   out_1569093053633695445[39] = 0;
   out_1569093053633695445[40] = 1;
   out_1569093053633695445[41] = 0;
   out_1569093053633695445[42] = 0;
   out_1569093053633695445[43] = 0;
   out_1569093053633695445[44] = 0;
   out_1569093053633695445[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_1569093053633695445[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_1569093053633695445[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_1569093053633695445[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_1569093053633695445[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_1569093053633695445[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_1569093053633695445[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_1569093053633695445[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_1569093053633695445[53] = -9.8100000000000005*dt;
   out_1569093053633695445[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_1569093053633695445[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_1569093053633695445[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_1569093053633695445[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_1569093053633695445[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_1569093053633695445[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_1569093053633695445[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_1569093053633695445[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_1569093053633695445[62] = 0;
   out_1569093053633695445[63] = 0;
   out_1569093053633695445[64] = 0;
   out_1569093053633695445[65] = 0;
   out_1569093053633695445[66] = 0;
   out_1569093053633695445[67] = 0;
   out_1569093053633695445[68] = 0;
   out_1569093053633695445[69] = 0;
   out_1569093053633695445[70] = 1;
   out_1569093053633695445[71] = 0;
   out_1569093053633695445[72] = 0;
   out_1569093053633695445[73] = 0;
   out_1569093053633695445[74] = 0;
   out_1569093053633695445[75] = 0;
   out_1569093053633695445[76] = 0;
   out_1569093053633695445[77] = 0;
   out_1569093053633695445[78] = 0;
   out_1569093053633695445[79] = 0;
   out_1569093053633695445[80] = 1;
}
void h_25(double *state, double *unused, double *out_7560488039046634277) {
   out_7560488039046634277[0] = state[6];
}
void H_25(double *state, double *unused, double *out_8687652227143085723) {
   out_8687652227143085723[0] = 0;
   out_8687652227143085723[1] = 0;
   out_8687652227143085723[2] = 0;
   out_8687652227143085723[3] = 0;
   out_8687652227143085723[4] = 0;
   out_8687652227143085723[5] = 0;
   out_8687652227143085723[6] = 1;
   out_8687652227143085723[7] = 0;
   out_8687652227143085723[8] = 0;
}
void h_24(double *state, double *unused, double *out_221107266672237923) {
   out_221107266672237923[0] = state[4];
   out_221107266672237923[1] = state[5];
}
void H_24(double *state, double *unused, double *out_6999835791273981532) {
   out_6999835791273981532[0] = 0;
   out_6999835791273981532[1] = 0;
   out_6999835791273981532[2] = 0;
   out_6999835791273981532[3] = 0;
   out_6999835791273981532[4] = 1;
   out_6999835791273981532[5] = 0;
   out_6999835791273981532[6] = 0;
   out_6999835791273981532[7] = 0;
   out_6999835791273981532[8] = 0;
   out_6999835791273981532[9] = 0;
   out_6999835791273981532[10] = 0;
   out_6999835791273981532[11] = 0;
   out_6999835791273981532[12] = 0;
   out_6999835791273981532[13] = 0;
   out_6999835791273981532[14] = 1;
   out_6999835791273981532[15] = 0;
   out_6999835791273981532[16] = 0;
   out_6999835791273981532[17] = 0;
}
void h_30(double *state, double *unused, double *out_4719141994691783036) {
   out_4719141994691783036[0] = state[4];
}
void H_30(double *state, double *unused, double *out_8816991174286325793) {
   out_8816991174286325793[0] = 0;
   out_8816991174286325793[1] = 0;
   out_8816991174286325793[2] = 0;
   out_8816991174286325793[3] = 0;
   out_8816991174286325793[4] = 1;
   out_8816991174286325793[5] = 0;
   out_8816991174286325793[6] = 0;
   out_8816991174286325793[7] = 0;
   out_8816991174286325793[8] = 0;
}
void h_26(double *state, double *unused, double *out_6539264067491314914) {
   out_6539264067491314914[0] = state[7];
}
void H_26(double *state, double *unused, double *out_6017588527692409669) {
   out_6017588527692409669[0] = 0;
   out_6017588527692409669[1] = 0;
   out_6017588527692409669[2] = 0;
   out_6017588527692409669[3] = 0;
   out_6017588527692409669[4] = 0;
   out_6017588527692409669[5] = 0;
   out_6017588527692409669[6] = 0;
   out_6017588527692409669[7] = 1;
   out_6017588527692409669[8] = 0;
}
void h_27(double *state, double *unused, double *out_5923876036981624107) {
   out_5923876036981624107[0] = state[3];
}
void H_27(double *state, double *unused, double *out_7454989587622800912) {
   out_7454989587622800912[0] = 0;
   out_7454989587622800912[1] = 0;
   out_7454989587622800912[2] = 0;
   out_7454989587622800912[3] = 1;
   out_7454989587622800912[4] = 0;
   out_7454989587622800912[5] = 0;
   out_7454989587622800912[6] = 0;
   out_7454989587622800912[7] = 0;
   out_7454989587622800912[8] = 0;
}
void h_29(double *state, double *unused, double *out_6078256905706434238) {
   out_6078256905706434238[0] = state[1];
}
void H_29(double *state, double *unused, double *out_5741626860753249879) {
   out_5741626860753249879[0] = 0;
   out_5741626860753249879[1] = 1;
   out_5741626860753249879[2] = 0;
   out_5741626860753249879[3] = 0;
   out_5741626860753249879[4] = 0;
   out_5741626860753249879[5] = 0;
   out_5741626860753249879[6] = 0;
   out_5741626860753249879[7] = 0;
   out_5741626860753249879[8] = 0;
}
void h_28(double *state, double *unused, double *out_3543704664347405758) {
   out_3543704664347405758[0] = state[0];
}
void H_28(double *state, double *unused, double *out_659227843683719305) {
   out_659227843683719305[0] = 1;
   out_659227843683719305[1] = 0;
   out_659227843683719305[2] = 0;
   out_659227843683719305[3] = 0;
   out_659227843683719305[4] = 0;
   out_659227843683719305[5] = 0;
   out_659227843683719305[6] = 0;
   out_659227843683719305[7] = 0;
   out_659227843683719305[8] = 0;
}
void h_31(double *state, double *unused, double *out_1683110624051124240) {
   out_1683110624051124240[0] = state[8];
}
void H_31(double *state, double *unused, double *out_8657006265266125295) {
   out_8657006265266125295[0] = 0;
   out_8657006265266125295[1] = 0;
   out_8657006265266125295[2] = 0;
   out_8657006265266125295[3] = 0;
   out_8657006265266125295[4] = 0;
   out_8657006265266125295[5] = 0;
   out_8657006265266125295[6] = 0;
   out_8657006265266125295[7] = 0;
   out_8657006265266125295[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_8815656279812630393) {
  err_fun(nom_x, delta_x, out_8815656279812630393);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_2634005456400563428) {
  inv_err_fun(nom_x, true_x, out_2634005456400563428);
}
void car_H_mod_fun(double *state, double *out_5776307114296964175) {
  H_mod_fun(state, out_5776307114296964175);
}
void car_f_fun(double *state, double dt, double *out_3329281261028883663) {
  f_fun(state,  dt, out_3329281261028883663);
}
void car_F_fun(double *state, double dt, double *out_1569093053633695445) {
  F_fun(state,  dt, out_1569093053633695445);
}
void car_h_25(double *state, double *unused, double *out_7560488039046634277) {
  h_25(state, unused, out_7560488039046634277);
}
void car_H_25(double *state, double *unused, double *out_8687652227143085723) {
  H_25(state, unused, out_8687652227143085723);
}
void car_h_24(double *state, double *unused, double *out_221107266672237923) {
  h_24(state, unused, out_221107266672237923);
}
void car_H_24(double *state, double *unused, double *out_6999835791273981532) {
  H_24(state, unused, out_6999835791273981532);
}
void car_h_30(double *state, double *unused, double *out_4719141994691783036) {
  h_30(state, unused, out_4719141994691783036);
}
void car_H_30(double *state, double *unused, double *out_8816991174286325793) {
  H_30(state, unused, out_8816991174286325793);
}
void car_h_26(double *state, double *unused, double *out_6539264067491314914) {
  h_26(state, unused, out_6539264067491314914);
}
void car_H_26(double *state, double *unused, double *out_6017588527692409669) {
  H_26(state, unused, out_6017588527692409669);
}
void car_h_27(double *state, double *unused, double *out_5923876036981624107) {
  h_27(state, unused, out_5923876036981624107);
}
void car_H_27(double *state, double *unused, double *out_7454989587622800912) {
  H_27(state, unused, out_7454989587622800912);
}
void car_h_29(double *state, double *unused, double *out_6078256905706434238) {
  h_29(state, unused, out_6078256905706434238);
}
void car_H_29(double *state, double *unused, double *out_5741626860753249879) {
  H_29(state, unused, out_5741626860753249879);
}
void car_h_28(double *state, double *unused, double *out_3543704664347405758) {
  h_28(state, unused, out_3543704664347405758);
}
void car_H_28(double *state, double *unused, double *out_659227843683719305) {
  H_28(state, unused, out_659227843683719305);
}
void car_h_31(double *state, double *unused, double *out_1683110624051124240) {
  h_31(state, unused, out_1683110624051124240);
}
void car_H_31(double *state, double *unused, double *out_8657006265266125295) {
  H_31(state, unused, out_8657006265266125295);
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
