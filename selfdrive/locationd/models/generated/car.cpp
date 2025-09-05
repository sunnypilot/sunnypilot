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
void err_fun(double *nom_x, double *delta_x, double *out_311236628735257153) {
   out_311236628735257153[0] = delta_x[0] + nom_x[0];
   out_311236628735257153[1] = delta_x[1] + nom_x[1];
   out_311236628735257153[2] = delta_x[2] + nom_x[2];
   out_311236628735257153[3] = delta_x[3] + nom_x[3];
   out_311236628735257153[4] = delta_x[4] + nom_x[4];
   out_311236628735257153[5] = delta_x[5] + nom_x[5];
   out_311236628735257153[6] = delta_x[6] + nom_x[6];
   out_311236628735257153[7] = delta_x[7] + nom_x[7];
   out_311236628735257153[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_7313915667919824068) {
   out_7313915667919824068[0] = -nom_x[0] + true_x[0];
   out_7313915667919824068[1] = -nom_x[1] + true_x[1];
   out_7313915667919824068[2] = -nom_x[2] + true_x[2];
   out_7313915667919824068[3] = -nom_x[3] + true_x[3];
   out_7313915667919824068[4] = -nom_x[4] + true_x[4];
   out_7313915667919824068[5] = -nom_x[5] + true_x[5];
   out_7313915667919824068[6] = -nom_x[6] + true_x[6];
   out_7313915667919824068[7] = -nom_x[7] + true_x[7];
   out_7313915667919824068[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_9020713222352451970) {
   out_9020713222352451970[0] = 1.0;
   out_9020713222352451970[1] = 0.0;
   out_9020713222352451970[2] = 0.0;
   out_9020713222352451970[3] = 0.0;
   out_9020713222352451970[4] = 0.0;
   out_9020713222352451970[5] = 0.0;
   out_9020713222352451970[6] = 0.0;
   out_9020713222352451970[7] = 0.0;
   out_9020713222352451970[8] = 0.0;
   out_9020713222352451970[9] = 0.0;
   out_9020713222352451970[10] = 1.0;
   out_9020713222352451970[11] = 0.0;
   out_9020713222352451970[12] = 0.0;
   out_9020713222352451970[13] = 0.0;
   out_9020713222352451970[14] = 0.0;
   out_9020713222352451970[15] = 0.0;
   out_9020713222352451970[16] = 0.0;
   out_9020713222352451970[17] = 0.0;
   out_9020713222352451970[18] = 0.0;
   out_9020713222352451970[19] = 0.0;
   out_9020713222352451970[20] = 1.0;
   out_9020713222352451970[21] = 0.0;
   out_9020713222352451970[22] = 0.0;
   out_9020713222352451970[23] = 0.0;
   out_9020713222352451970[24] = 0.0;
   out_9020713222352451970[25] = 0.0;
   out_9020713222352451970[26] = 0.0;
   out_9020713222352451970[27] = 0.0;
   out_9020713222352451970[28] = 0.0;
   out_9020713222352451970[29] = 0.0;
   out_9020713222352451970[30] = 1.0;
   out_9020713222352451970[31] = 0.0;
   out_9020713222352451970[32] = 0.0;
   out_9020713222352451970[33] = 0.0;
   out_9020713222352451970[34] = 0.0;
   out_9020713222352451970[35] = 0.0;
   out_9020713222352451970[36] = 0.0;
   out_9020713222352451970[37] = 0.0;
   out_9020713222352451970[38] = 0.0;
   out_9020713222352451970[39] = 0.0;
   out_9020713222352451970[40] = 1.0;
   out_9020713222352451970[41] = 0.0;
   out_9020713222352451970[42] = 0.0;
   out_9020713222352451970[43] = 0.0;
   out_9020713222352451970[44] = 0.0;
   out_9020713222352451970[45] = 0.0;
   out_9020713222352451970[46] = 0.0;
   out_9020713222352451970[47] = 0.0;
   out_9020713222352451970[48] = 0.0;
   out_9020713222352451970[49] = 0.0;
   out_9020713222352451970[50] = 1.0;
   out_9020713222352451970[51] = 0.0;
   out_9020713222352451970[52] = 0.0;
   out_9020713222352451970[53] = 0.0;
   out_9020713222352451970[54] = 0.0;
   out_9020713222352451970[55] = 0.0;
   out_9020713222352451970[56] = 0.0;
   out_9020713222352451970[57] = 0.0;
   out_9020713222352451970[58] = 0.0;
   out_9020713222352451970[59] = 0.0;
   out_9020713222352451970[60] = 1.0;
   out_9020713222352451970[61] = 0.0;
   out_9020713222352451970[62] = 0.0;
   out_9020713222352451970[63] = 0.0;
   out_9020713222352451970[64] = 0.0;
   out_9020713222352451970[65] = 0.0;
   out_9020713222352451970[66] = 0.0;
   out_9020713222352451970[67] = 0.0;
   out_9020713222352451970[68] = 0.0;
   out_9020713222352451970[69] = 0.0;
   out_9020713222352451970[70] = 1.0;
   out_9020713222352451970[71] = 0.0;
   out_9020713222352451970[72] = 0.0;
   out_9020713222352451970[73] = 0.0;
   out_9020713222352451970[74] = 0.0;
   out_9020713222352451970[75] = 0.0;
   out_9020713222352451970[76] = 0.0;
   out_9020713222352451970[77] = 0.0;
   out_9020713222352451970[78] = 0.0;
   out_9020713222352451970[79] = 0.0;
   out_9020713222352451970[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_1159356000309350310) {
   out_1159356000309350310[0] = state[0];
   out_1159356000309350310[1] = state[1];
   out_1159356000309350310[2] = state[2];
   out_1159356000309350310[3] = state[3];
   out_1159356000309350310[4] = state[4];
   out_1159356000309350310[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8100000000000005*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_1159356000309350310[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_1159356000309350310[7] = state[7];
   out_1159356000309350310[8] = state[8];
}
void F_fun(double *state, double dt, double *out_8529210458665284284) {
   out_8529210458665284284[0] = 1;
   out_8529210458665284284[1] = 0;
   out_8529210458665284284[2] = 0;
   out_8529210458665284284[3] = 0;
   out_8529210458665284284[4] = 0;
   out_8529210458665284284[5] = 0;
   out_8529210458665284284[6] = 0;
   out_8529210458665284284[7] = 0;
   out_8529210458665284284[8] = 0;
   out_8529210458665284284[9] = 0;
   out_8529210458665284284[10] = 1;
   out_8529210458665284284[11] = 0;
   out_8529210458665284284[12] = 0;
   out_8529210458665284284[13] = 0;
   out_8529210458665284284[14] = 0;
   out_8529210458665284284[15] = 0;
   out_8529210458665284284[16] = 0;
   out_8529210458665284284[17] = 0;
   out_8529210458665284284[18] = 0;
   out_8529210458665284284[19] = 0;
   out_8529210458665284284[20] = 1;
   out_8529210458665284284[21] = 0;
   out_8529210458665284284[22] = 0;
   out_8529210458665284284[23] = 0;
   out_8529210458665284284[24] = 0;
   out_8529210458665284284[25] = 0;
   out_8529210458665284284[26] = 0;
   out_8529210458665284284[27] = 0;
   out_8529210458665284284[28] = 0;
   out_8529210458665284284[29] = 0;
   out_8529210458665284284[30] = 1;
   out_8529210458665284284[31] = 0;
   out_8529210458665284284[32] = 0;
   out_8529210458665284284[33] = 0;
   out_8529210458665284284[34] = 0;
   out_8529210458665284284[35] = 0;
   out_8529210458665284284[36] = 0;
   out_8529210458665284284[37] = 0;
   out_8529210458665284284[38] = 0;
   out_8529210458665284284[39] = 0;
   out_8529210458665284284[40] = 1;
   out_8529210458665284284[41] = 0;
   out_8529210458665284284[42] = 0;
   out_8529210458665284284[43] = 0;
   out_8529210458665284284[44] = 0;
   out_8529210458665284284[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_8529210458665284284[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_8529210458665284284[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_8529210458665284284[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_8529210458665284284[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_8529210458665284284[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_8529210458665284284[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_8529210458665284284[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_8529210458665284284[53] = -9.8100000000000005*dt;
   out_8529210458665284284[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_8529210458665284284[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_8529210458665284284[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_8529210458665284284[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_8529210458665284284[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_8529210458665284284[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_8529210458665284284[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_8529210458665284284[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_8529210458665284284[62] = 0;
   out_8529210458665284284[63] = 0;
   out_8529210458665284284[64] = 0;
   out_8529210458665284284[65] = 0;
   out_8529210458665284284[66] = 0;
   out_8529210458665284284[67] = 0;
   out_8529210458665284284[68] = 0;
   out_8529210458665284284[69] = 0;
   out_8529210458665284284[70] = 1;
   out_8529210458665284284[71] = 0;
   out_8529210458665284284[72] = 0;
   out_8529210458665284284[73] = 0;
   out_8529210458665284284[74] = 0;
   out_8529210458665284284[75] = 0;
   out_8529210458665284284[76] = 0;
   out_8529210458665284284[77] = 0;
   out_8529210458665284284[78] = 0;
   out_8529210458665284284[79] = 0;
   out_8529210458665284284[80] = 1;
}
void h_25(double *state, double *unused, double *out_4254560804621753910) {
   out_4254560804621753910[0] = state[6];
}
void H_25(double *state, double *unused, double *out_7096198754133444274) {
   out_7096198754133444274[0] = 0;
   out_7096198754133444274[1] = 0;
   out_7096198754133444274[2] = 0;
   out_7096198754133444274[3] = 0;
   out_7096198754133444274[4] = 0;
   out_7096198754133444274[5] = 0;
   out_7096198754133444274[6] = 1;
   out_7096198754133444274[7] = 0;
   out_7096198754133444274[8] = 0;
}
void h_24(double *state, double *unused, double *out_5260315530328507674) {
   out_5260315530328507674[0] = state[4];
   out_5260315530328507674[1] = state[5];
}
void H_24(double *state, double *unused, double *out_4918984330526294301) {
   out_4918984330526294301[0] = 0;
   out_4918984330526294301[1] = 0;
   out_4918984330526294301[2] = 0;
   out_4918984330526294301[3] = 0;
   out_4918984330526294301[4] = 1;
   out_4918984330526294301[5] = 0;
   out_4918984330526294301[6] = 0;
   out_4918984330526294301[7] = 0;
   out_4918984330526294301[8] = 0;
   out_4918984330526294301[9] = 0;
   out_4918984330526294301[10] = 0;
   out_4918984330526294301[11] = 0;
   out_4918984330526294301[12] = 0;
   out_4918984330526294301[13] = 0;
   out_4918984330526294301[14] = 1;
   out_4918984330526294301[15] = 0;
   out_4918984330526294301[16] = 0;
   out_4918984330526294301[17] = 0;
}
void h_30(double *state, double *unused, double *out_7892010332875776260) {
   out_7892010332875776260[0] = state[4];
}
void H_30(double *state, double *unused, double *out_4577865795626195647) {
   out_4577865795626195647[0] = 0;
   out_4577865795626195647[1] = 0;
   out_4577865795626195647[2] = 0;
   out_4577865795626195647[3] = 0;
   out_4577865795626195647[4] = 1;
   out_4577865795626195647[5] = 0;
   out_4577865795626195647[6] = 0;
   out_4577865795626195647[7] = 0;
   out_4577865795626195647[8] = 0;
}
void h_26(double *state, double *unused, double *out_3494058251594147248) {
   out_3494058251594147248[0] = state[7];
}
void H_26(double *state, double *unused, double *out_3791672784372643673) {
   out_3791672784372643673[0] = 0;
   out_3791672784372643673[1] = 0;
   out_3791672784372643673[2] = 0;
   out_3791672784372643673[3] = 0;
   out_3791672784372643673[4] = 0;
   out_3791672784372643673[5] = 0;
   out_3791672784372643673[6] = 0;
   out_3791672784372643673[7] = 1;
   out_3791672784372643673[8] = 0;
}
void h_27(double *state, double *unused, double *out_4727408367385086855) {
   out_4727408367385086855[0] = state[3];
}
void H_27(double *state, double *unused, double *out_6752629107426620558) {
   out_6752629107426620558[0] = 0;
   out_6752629107426620558[1] = 0;
   out_6752629107426620558[2] = 0;
   out_6752629107426620558[3] = 1;
   out_6752629107426620558[4] = 0;
   out_6752629107426620558[5] = 0;
   out_6752629107426620558[6] = 0;
   out_6752629107426620558[7] = 0;
   out_6752629107426620558[8] = 0;
}
void h_29(double *state, double *unused, double *out_5328826524998450409) {
   out_5328826524998450409[0] = state[1];
}
void H_29(double *state, double *unused, double *out_4067634451311803463) {
   out_4067634451311803463[0] = 0;
   out_4067634451311803463[1] = 1;
   out_4067634451311803463[2] = 0;
   out_4067634451311803463[3] = 0;
   out_4067634451311803463[4] = 0;
   out_4067634451311803463[5] = 0;
   out_4067634451311803463[6] = 0;
   out_4067634451311803463[7] = 0;
   out_4067634451311803463[8] = 0;
}
void h_28(double *state, double *unused, double *out_274264900275758790) {
   out_274264900275758790[0] = state[0];
}
void H_28(double *state, double *unused, double *out_9150033468381334037) {
   out_9150033468381334037[0] = 1;
   out_9150033468381334037[1] = 0;
   out_9150033468381334037[2] = 0;
   out_9150033468381334037[3] = 0;
   out_9150033468381334037[4] = 0;
   out_9150033468381334037[5] = 0;
   out_9150033468381334037[6] = 0;
   out_9150033468381334037[7] = 0;
   out_9150033468381334037[8] = 0;
}
void h_31(double *state, double *unused, double *out_2109033173680061951) {
   out_2109033173680061951[0] = state[8];
}
void H_31(double *state, double *unused, double *out_4417880886605995149) {
   out_4417880886605995149[0] = 0;
   out_4417880886605995149[1] = 0;
   out_4417880886605995149[2] = 0;
   out_4417880886605995149[3] = 0;
   out_4417880886605995149[4] = 0;
   out_4417880886605995149[5] = 0;
   out_4417880886605995149[6] = 0;
   out_4417880886605995149[7] = 0;
   out_4417880886605995149[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_311236628735257153) {
  err_fun(nom_x, delta_x, out_311236628735257153);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_7313915667919824068) {
  inv_err_fun(nom_x, true_x, out_7313915667919824068);
}
void car_H_mod_fun(double *state, double *out_9020713222352451970) {
  H_mod_fun(state, out_9020713222352451970);
}
void car_f_fun(double *state, double dt, double *out_1159356000309350310) {
  f_fun(state,  dt, out_1159356000309350310);
}
void car_F_fun(double *state, double dt, double *out_8529210458665284284) {
  F_fun(state,  dt, out_8529210458665284284);
}
void car_h_25(double *state, double *unused, double *out_4254560804621753910) {
  h_25(state, unused, out_4254560804621753910);
}
void car_H_25(double *state, double *unused, double *out_7096198754133444274) {
  H_25(state, unused, out_7096198754133444274);
}
void car_h_24(double *state, double *unused, double *out_5260315530328507674) {
  h_24(state, unused, out_5260315530328507674);
}
void car_H_24(double *state, double *unused, double *out_4918984330526294301) {
  H_24(state, unused, out_4918984330526294301);
}
void car_h_30(double *state, double *unused, double *out_7892010332875776260) {
  h_30(state, unused, out_7892010332875776260);
}
void car_H_30(double *state, double *unused, double *out_4577865795626195647) {
  H_30(state, unused, out_4577865795626195647);
}
void car_h_26(double *state, double *unused, double *out_3494058251594147248) {
  h_26(state, unused, out_3494058251594147248);
}
void car_H_26(double *state, double *unused, double *out_3791672784372643673) {
  H_26(state, unused, out_3791672784372643673);
}
void car_h_27(double *state, double *unused, double *out_4727408367385086855) {
  h_27(state, unused, out_4727408367385086855);
}
void car_H_27(double *state, double *unused, double *out_6752629107426620558) {
  H_27(state, unused, out_6752629107426620558);
}
void car_h_29(double *state, double *unused, double *out_5328826524998450409) {
  h_29(state, unused, out_5328826524998450409);
}
void car_H_29(double *state, double *unused, double *out_4067634451311803463) {
  H_29(state, unused, out_4067634451311803463);
}
void car_h_28(double *state, double *unused, double *out_274264900275758790) {
  h_28(state, unused, out_274264900275758790);
}
void car_H_28(double *state, double *unused, double *out_9150033468381334037) {
  H_28(state, unused, out_9150033468381334037);
}
void car_h_31(double *state, double *unused, double *out_2109033173680061951) {
  h_31(state, unused, out_2109033173680061951);
}
void car_H_31(double *state, double *unused, double *out_4417880886605995149) {
  H_31(state, unused, out_4417880886605995149);
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
