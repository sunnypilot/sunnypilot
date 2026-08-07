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
void err_fun(double *nom_x, double *delta_x, double *out_2367152293466283987) {
   out_2367152293466283987[0] = delta_x[0] + nom_x[0];
   out_2367152293466283987[1] = delta_x[1] + nom_x[1];
   out_2367152293466283987[2] = delta_x[2] + nom_x[2];
   out_2367152293466283987[3] = delta_x[3] + nom_x[3];
   out_2367152293466283987[4] = delta_x[4] + nom_x[4];
   out_2367152293466283987[5] = delta_x[5] + nom_x[5];
   out_2367152293466283987[6] = delta_x[6] + nom_x[6];
   out_2367152293466283987[7] = delta_x[7] + nom_x[7];
   out_2367152293466283987[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_5829526074669369656) {
   out_5829526074669369656[0] = -nom_x[0] + true_x[0];
   out_5829526074669369656[1] = -nom_x[1] + true_x[1];
   out_5829526074669369656[2] = -nom_x[2] + true_x[2];
   out_5829526074669369656[3] = -nom_x[3] + true_x[3];
   out_5829526074669369656[4] = -nom_x[4] + true_x[4];
   out_5829526074669369656[5] = -nom_x[5] + true_x[5];
   out_5829526074669369656[6] = -nom_x[6] + true_x[6];
   out_5829526074669369656[7] = -nom_x[7] + true_x[7];
   out_5829526074669369656[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_1755007343641557895) {
   out_1755007343641557895[0] = 1.0;
   out_1755007343641557895[1] = 0.0;
   out_1755007343641557895[2] = 0.0;
   out_1755007343641557895[3] = 0.0;
   out_1755007343641557895[4] = 0.0;
   out_1755007343641557895[5] = 0.0;
   out_1755007343641557895[6] = 0.0;
   out_1755007343641557895[7] = 0.0;
   out_1755007343641557895[8] = 0.0;
   out_1755007343641557895[9] = 0.0;
   out_1755007343641557895[10] = 1.0;
   out_1755007343641557895[11] = 0.0;
   out_1755007343641557895[12] = 0.0;
   out_1755007343641557895[13] = 0.0;
   out_1755007343641557895[14] = 0.0;
   out_1755007343641557895[15] = 0.0;
   out_1755007343641557895[16] = 0.0;
   out_1755007343641557895[17] = 0.0;
   out_1755007343641557895[18] = 0.0;
   out_1755007343641557895[19] = 0.0;
   out_1755007343641557895[20] = 1.0;
   out_1755007343641557895[21] = 0.0;
   out_1755007343641557895[22] = 0.0;
   out_1755007343641557895[23] = 0.0;
   out_1755007343641557895[24] = 0.0;
   out_1755007343641557895[25] = 0.0;
   out_1755007343641557895[26] = 0.0;
   out_1755007343641557895[27] = 0.0;
   out_1755007343641557895[28] = 0.0;
   out_1755007343641557895[29] = 0.0;
   out_1755007343641557895[30] = 1.0;
   out_1755007343641557895[31] = 0.0;
   out_1755007343641557895[32] = 0.0;
   out_1755007343641557895[33] = 0.0;
   out_1755007343641557895[34] = 0.0;
   out_1755007343641557895[35] = 0.0;
   out_1755007343641557895[36] = 0.0;
   out_1755007343641557895[37] = 0.0;
   out_1755007343641557895[38] = 0.0;
   out_1755007343641557895[39] = 0.0;
   out_1755007343641557895[40] = 1.0;
   out_1755007343641557895[41] = 0.0;
   out_1755007343641557895[42] = 0.0;
   out_1755007343641557895[43] = 0.0;
   out_1755007343641557895[44] = 0.0;
   out_1755007343641557895[45] = 0.0;
   out_1755007343641557895[46] = 0.0;
   out_1755007343641557895[47] = 0.0;
   out_1755007343641557895[48] = 0.0;
   out_1755007343641557895[49] = 0.0;
   out_1755007343641557895[50] = 1.0;
   out_1755007343641557895[51] = 0.0;
   out_1755007343641557895[52] = 0.0;
   out_1755007343641557895[53] = 0.0;
   out_1755007343641557895[54] = 0.0;
   out_1755007343641557895[55] = 0.0;
   out_1755007343641557895[56] = 0.0;
   out_1755007343641557895[57] = 0.0;
   out_1755007343641557895[58] = 0.0;
   out_1755007343641557895[59] = 0.0;
   out_1755007343641557895[60] = 1.0;
   out_1755007343641557895[61] = 0.0;
   out_1755007343641557895[62] = 0.0;
   out_1755007343641557895[63] = 0.0;
   out_1755007343641557895[64] = 0.0;
   out_1755007343641557895[65] = 0.0;
   out_1755007343641557895[66] = 0.0;
   out_1755007343641557895[67] = 0.0;
   out_1755007343641557895[68] = 0.0;
   out_1755007343641557895[69] = 0.0;
   out_1755007343641557895[70] = 1.0;
   out_1755007343641557895[71] = 0.0;
   out_1755007343641557895[72] = 0.0;
   out_1755007343641557895[73] = 0.0;
   out_1755007343641557895[74] = 0.0;
   out_1755007343641557895[75] = 0.0;
   out_1755007343641557895[76] = 0.0;
   out_1755007343641557895[77] = 0.0;
   out_1755007343641557895[78] = 0.0;
   out_1755007343641557895[79] = 0.0;
   out_1755007343641557895[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_8527162516255122736) {
   out_8527162516255122736[0] = state[0];
   out_8527162516255122736[1] = state[1];
   out_8527162516255122736[2] = state[2];
   out_8527162516255122736[3] = state[3];
   out_8527162516255122736[4] = state[4];
   out_8527162516255122736[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8100000000000005*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_8527162516255122736[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_8527162516255122736[7] = state[7];
   out_8527162516255122736[8] = state[8];
}
void F_fun(double *state, double dt, double *out_7094558340758265304) {
   out_7094558340758265304[0] = 1;
   out_7094558340758265304[1] = 0;
   out_7094558340758265304[2] = 0;
   out_7094558340758265304[3] = 0;
   out_7094558340758265304[4] = 0;
   out_7094558340758265304[5] = 0;
   out_7094558340758265304[6] = 0;
   out_7094558340758265304[7] = 0;
   out_7094558340758265304[8] = 0;
   out_7094558340758265304[9] = 0;
   out_7094558340758265304[10] = 1;
   out_7094558340758265304[11] = 0;
   out_7094558340758265304[12] = 0;
   out_7094558340758265304[13] = 0;
   out_7094558340758265304[14] = 0;
   out_7094558340758265304[15] = 0;
   out_7094558340758265304[16] = 0;
   out_7094558340758265304[17] = 0;
   out_7094558340758265304[18] = 0;
   out_7094558340758265304[19] = 0;
   out_7094558340758265304[20] = 1;
   out_7094558340758265304[21] = 0;
   out_7094558340758265304[22] = 0;
   out_7094558340758265304[23] = 0;
   out_7094558340758265304[24] = 0;
   out_7094558340758265304[25] = 0;
   out_7094558340758265304[26] = 0;
   out_7094558340758265304[27] = 0;
   out_7094558340758265304[28] = 0;
   out_7094558340758265304[29] = 0;
   out_7094558340758265304[30] = 1;
   out_7094558340758265304[31] = 0;
   out_7094558340758265304[32] = 0;
   out_7094558340758265304[33] = 0;
   out_7094558340758265304[34] = 0;
   out_7094558340758265304[35] = 0;
   out_7094558340758265304[36] = 0;
   out_7094558340758265304[37] = 0;
   out_7094558340758265304[38] = 0;
   out_7094558340758265304[39] = 0;
   out_7094558340758265304[40] = 1;
   out_7094558340758265304[41] = 0;
   out_7094558340758265304[42] = 0;
   out_7094558340758265304[43] = 0;
   out_7094558340758265304[44] = 0;
   out_7094558340758265304[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_7094558340758265304[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_7094558340758265304[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_7094558340758265304[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_7094558340758265304[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_7094558340758265304[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_7094558340758265304[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_7094558340758265304[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_7094558340758265304[53] = -9.8100000000000005*dt;
   out_7094558340758265304[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_7094558340758265304[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_7094558340758265304[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_7094558340758265304[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_7094558340758265304[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_7094558340758265304[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_7094558340758265304[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_7094558340758265304[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_7094558340758265304[62] = 0;
   out_7094558340758265304[63] = 0;
   out_7094558340758265304[64] = 0;
   out_7094558340758265304[65] = 0;
   out_7094558340758265304[66] = 0;
   out_7094558340758265304[67] = 0;
   out_7094558340758265304[68] = 0;
   out_7094558340758265304[69] = 0;
   out_7094558340758265304[70] = 1;
   out_7094558340758265304[71] = 0;
   out_7094558340758265304[72] = 0;
   out_7094558340758265304[73] = 0;
   out_7094558340758265304[74] = 0;
   out_7094558340758265304[75] = 0;
   out_7094558340758265304[76] = 0;
   out_7094558340758265304[77] = 0;
   out_7094558340758265304[78] = 0;
   out_7094558340758265304[79] = 0;
   out_7094558340758265304[80] = 1;
}
void h_25(double *state, double *unused, double *out_6286236977752489740) {
   out_6286236977752489740[0] = state[6];
}
void H_25(double *state, double *unused, double *out_4084839440865213267) {
   out_4084839440865213267[0] = 0;
   out_4084839440865213267[1] = 0;
   out_4084839440865213267[2] = 0;
   out_4084839440865213267[3] = 0;
   out_4084839440865213267[4] = 0;
   out_4084839440865213267[5] = 0;
   out_4084839440865213267[6] = 1;
   out_4084839440865213267[7] = 0;
   out_4084839440865213267[8] = 0;
}
void h_24(double *state, double *unused, double *out_6918439556027581256) {
   out_6918439556027581256[0] = state[4];
   out_6918439556027581256[1] = state[5];
}
void H_24(double *state, double *unused, double *out_4929836049648908666) {
   out_4929836049648908666[0] = 0;
   out_4929836049648908666[1] = 0;
   out_4929836049648908666[2] = 0;
   out_4929836049648908666[3] = 0;
   out_4929836049648908666[4] = 1;
   out_4929836049648908666[5] = 0;
   out_4929836049648908666[6] = 0;
   out_4929836049648908666[7] = 0;
   out_4929836049648908666[8] = 0;
   out_4929836049648908666[9] = 0;
   out_4929836049648908666[10] = 0;
   out_4929836049648908666[11] = 0;
   out_4929836049648908666[12] = 0;
   out_4929836049648908666[13] = 0;
   out_4929836049648908666[14] = 1;
   out_4929836049648908666[15] = 0;
   out_4929836049648908666[16] = 0;
   out_4929836049648908666[17] = 0;
}
void h_30(double *state, double *unused, double *out_6443423646103618885) {
   out_6443423646103618885[0] = state[4];
}
void H_30(double *state, double *unused, double *out_6603172399372461894) {
   out_6603172399372461894[0] = 0;
   out_6603172399372461894[1] = 0;
   out_6603172399372461894[2] = 0;
   out_6603172399372461894[3] = 0;
   out_6603172399372461894[4] = 1;
   out_6603172399372461894[5] = 0;
   out_6603172399372461894[6] = 0;
   out_6603172399372461894[7] = 0;
   out_6603172399372461894[8] = 0;
}
void h_26(double *state, double *unused, double *out_7270973478954575704) {
   out_7270973478954575704[0] = state[7];
}
void H_26(double *state, double *unused, double *out_343336121991157043) {
   out_343336121991157043[0] = 0;
   out_343336121991157043[1] = 0;
   out_343336121991157043[2] = 0;
   out_343336121991157043[3] = 0;
   out_343336121991157043[4] = 0;
   out_343336121991157043[5] = 0;
   out_343336121991157043[6] = 0;
   out_343336121991157043[7] = 1;
   out_343336121991157043[8] = 0;
}
void h_27(double *state, double *unused, double *out_9123721044512729191) {
   out_9123721044512729191[0] = state[3];
}
void H_27(double *state, double *unused, double *out_8826766470556405111) {
   out_8826766470556405111[0] = 0;
   out_8826766470556405111[1] = 0;
   out_8826766470556405111[2] = 0;
   out_8826766470556405111[3] = 1;
   out_8826766470556405111[4] = 0;
   out_8826766470556405111[5] = 0;
   out_8826766470556405111[6] = 0;
   out_8826766470556405111[7] = 0;
   out_8826766470556405111[8] = 0;
}
void h_29(double *state, double *unused, double *out_2352885818162378255) {
   out_2352885818162378255[0] = state[1];
}
void H_29(double *state, double *unused, double *out_7113403743686854078) {
   out_7113403743686854078[0] = 0;
   out_7113403743686854078[1] = 1;
   out_7113403743686854078[2] = 0;
   out_7113403743686854078[3] = 0;
   out_7113403743686854078[4] = 0;
   out_7113403743686854078[5] = 0;
   out_7113403743686854078[6] = 0;
   out_7113403743686854078[7] = 0;
   out_7113403743686854078[8] = 0;
}
void h_28(double *state, double *unused, double *out_8180211191611066756) {
   out_8180211191611066756[0] = state[0];
}
void H_28(double *state, double *unused, double *out_2031004726617323504) {
   out_2031004726617323504[0] = 1;
   out_2031004726617323504[1] = 0;
   out_2031004726617323504[2] = 0;
   out_2031004726617323504[3] = 0;
   out_2031004726617323504[4] = 0;
   out_2031004726617323504[5] = 0;
   out_2031004726617323504[6] = 0;
   out_2031004726617323504[7] = 0;
   out_2031004726617323504[8] = 0;
}
void h_31(double *state, double *unused, double *out_5572679169480766713) {
   out_5572679169480766713[0] = state[8];
}
void H_31(double *state, double *unused, double *out_282871980242194433) {
   out_282871980242194433[0] = 0;
   out_282871980242194433[1] = 0;
   out_282871980242194433[2] = 0;
   out_282871980242194433[3] = 0;
   out_282871980242194433[4] = 0;
   out_282871980242194433[5] = 0;
   out_282871980242194433[6] = 0;
   out_282871980242194433[7] = 0;
   out_282871980242194433[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_2367152293466283987) {
  err_fun(nom_x, delta_x, out_2367152293466283987);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_5829526074669369656) {
  inv_err_fun(nom_x, true_x, out_5829526074669369656);
}
void car_H_mod_fun(double *state, double *out_1755007343641557895) {
  H_mod_fun(state, out_1755007343641557895);
}
void car_f_fun(double *state, double dt, double *out_8527162516255122736) {
  f_fun(state,  dt, out_8527162516255122736);
}
void car_F_fun(double *state, double dt, double *out_7094558340758265304) {
  F_fun(state,  dt, out_7094558340758265304);
}
void car_h_25(double *state, double *unused, double *out_6286236977752489740) {
  h_25(state, unused, out_6286236977752489740);
}
void car_H_25(double *state, double *unused, double *out_4084839440865213267) {
  H_25(state, unused, out_4084839440865213267);
}
void car_h_24(double *state, double *unused, double *out_6918439556027581256) {
  h_24(state, unused, out_6918439556027581256);
}
void car_H_24(double *state, double *unused, double *out_4929836049648908666) {
  H_24(state, unused, out_4929836049648908666);
}
void car_h_30(double *state, double *unused, double *out_6443423646103618885) {
  h_30(state, unused, out_6443423646103618885);
}
void car_H_30(double *state, double *unused, double *out_6603172399372461894) {
  H_30(state, unused, out_6603172399372461894);
}
void car_h_26(double *state, double *unused, double *out_7270973478954575704) {
  h_26(state, unused, out_7270973478954575704);
}
void car_H_26(double *state, double *unused, double *out_343336121991157043) {
  H_26(state, unused, out_343336121991157043);
}
void car_h_27(double *state, double *unused, double *out_9123721044512729191) {
  h_27(state, unused, out_9123721044512729191);
}
void car_H_27(double *state, double *unused, double *out_8826766470556405111) {
  H_27(state, unused, out_8826766470556405111);
}
void car_h_29(double *state, double *unused, double *out_2352885818162378255) {
  h_29(state, unused, out_2352885818162378255);
}
void car_H_29(double *state, double *unused, double *out_7113403743686854078) {
  H_29(state, unused, out_7113403743686854078);
}
void car_h_28(double *state, double *unused, double *out_8180211191611066756) {
  h_28(state, unused, out_8180211191611066756);
}
void car_H_28(double *state, double *unused, double *out_2031004726617323504) {
  H_28(state, unused, out_2031004726617323504);
}
void car_h_31(double *state, double *unused, double *out_5572679169480766713) {
  h_31(state, unused, out_5572679169480766713);
}
void car_H_31(double *state, double *unused, double *out_282871980242194433) {
  H_31(state, unused, out_282871980242194433);
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
