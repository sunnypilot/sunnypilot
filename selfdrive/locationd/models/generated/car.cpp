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
void err_fun(double *nom_x, double *delta_x, double *out_3273042440096814304) {
   out_3273042440096814304[0] = delta_x[0] + nom_x[0];
   out_3273042440096814304[1] = delta_x[1] + nom_x[1];
   out_3273042440096814304[2] = delta_x[2] + nom_x[2];
   out_3273042440096814304[3] = delta_x[3] + nom_x[3];
   out_3273042440096814304[4] = delta_x[4] + nom_x[4];
   out_3273042440096814304[5] = delta_x[5] + nom_x[5];
   out_3273042440096814304[6] = delta_x[6] + nom_x[6];
   out_3273042440096814304[7] = delta_x[7] + nom_x[7];
   out_3273042440096814304[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_5732845985013317398) {
   out_5732845985013317398[0] = -nom_x[0] + true_x[0];
   out_5732845985013317398[1] = -nom_x[1] + true_x[1];
   out_5732845985013317398[2] = -nom_x[2] + true_x[2];
   out_5732845985013317398[3] = -nom_x[3] + true_x[3];
   out_5732845985013317398[4] = -nom_x[4] + true_x[4];
   out_5732845985013317398[5] = -nom_x[5] + true_x[5];
   out_5732845985013317398[6] = -nom_x[6] + true_x[6];
   out_5732845985013317398[7] = -nom_x[7] + true_x[7];
   out_5732845985013317398[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_421472006259524810) {
   out_421472006259524810[0] = 1.0;
   out_421472006259524810[1] = 0;
   out_421472006259524810[2] = 0;
   out_421472006259524810[3] = 0;
   out_421472006259524810[4] = 0;
   out_421472006259524810[5] = 0;
   out_421472006259524810[6] = 0;
   out_421472006259524810[7] = 0;
   out_421472006259524810[8] = 0;
   out_421472006259524810[9] = 0;
   out_421472006259524810[10] = 1.0;
   out_421472006259524810[11] = 0;
   out_421472006259524810[12] = 0;
   out_421472006259524810[13] = 0;
   out_421472006259524810[14] = 0;
   out_421472006259524810[15] = 0;
   out_421472006259524810[16] = 0;
   out_421472006259524810[17] = 0;
   out_421472006259524810[18] = 0;
   out_421472006259524810[19] = 0;
   out_421472006259524810[20] = 1.0;
   out_421472006259524810[21] = 0;
   out_421472006259524810[22] = 0;
   out_421472006259524810[23] = 0;
   out_421472006259524810[24] = 0;
   out_421472006259524810[25] = 0;
   out_421472006259524810[26] = 0;
   out_421472006259524810[27] = 0;
   out_421472006259524810[28] = 0;
   out_421472006259524810[29] = 0;
   out_421472006259524810[30] = 1.0;
   out_421472006259524810[31] = 0;
   out_421472006259524810[32] = 0;
   out_421472006259524810[33] = 0;
   out_421472006259524810[34] = 0;
   out_421472006259524810[35] = 0;
   out_421472006259524810[36] = 0;
   out_421472006259524810[37] = 0;
   out_421472006259524810[38] = 0;
   out_421472006259524810[39] = 0;
   out_421472006259524810[40] = 1.0;
   out_421472006259524810[41] = 0;
   out_421472006259524810[42] = 0;
   out_421472006259524810[43] = 0;
   out_421472006259524810[44] = 0;
   out_421472006259524810[45] = 0;
   out_421472006259524810[46] = 0;
   out_421472006259524810[47] = 0;
   out_421472006259524810[48] = 0;
   out_421472006259524810[49] = 0;
   out_421472006259524810[50] = 1.0;
   out_421472006259524810[51] = 0;
   out_421472006259524810[52] = 0;
   out_421472006259524810[53] = 0;
   out_421472006259524810[54] = 0;
   out_421472006259524810[55] = 0;
   out_421472006259524810[56] = 0;
   out_421472006259524810[57] = 0;
   out_421472006259524810[58] = 0;
   out_421472006259524810[59] = 0;
   out_421472006259524810[60] = 1.0;
   out_421472006259524810[61] = 0;
   out_421472006259524810[62] = 0;
   out_421472006259524810[63] = 0;
   out_421472006259524810[64] = 0;
   out_421472006259524810[65] = 0;
   out_421472006259524810[66] = 0;
   out_421472006259524810[67] = 0;
   out_421472006259524810[68] = 0;
   out_421472006259524810[69] = 0;
   out_421472006259524810[70] = 1.0;
   out_421472006259524810[71] = 0;
   out_421472006259524810[72] = 0;
   out_421472006259524810[73] = 0;
   out_421472006259524810[74] = 0;
   out_421472006259524810[75] = 0;
   out_421472006259524810[76] = 0;
   out_421472006259524810[77] = 0;
   out_421472006259524810[78] = 0;
   out_421472006259524810[79] = 0;
   out_421472006259524810[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_3776724096449913501) {
   out_3776724096449913501[0] = state[0];
   out_3776724096449913501[1] = state[1];
   out_3776724096449913501[2] = state[2];
   out_3776724096449913501[3] = state[3];
   out_3776724096449913501[4] = state[4];
   out_3776724096449913501[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8000000000000007*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_3776724096449913501[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_3776724096449913501[7] = state[7];
   out_3776724096449913501[8] = state[8];
}
void F_fun(double *state, double dt, double *out_1353218831850316658) {
   out_1353218831850316658[0] = 1;
   out_1353218831850316658[1] = 0;
   out_1353218831850316658[2] = 0;
   out_1353218831850316658[3] = 0;
   out_1353218831850316658[4] = 0;
   out_1353218831850316658[5] = 0;
   out_1353218831850316658[6] = 0;
   out_1353218831850316658[7] = 0;
   out_1353218831850316658[8] = 0;
   out_1353218831850316658[9] = 0;
   out_1353218831850316658[10] = 1;
   out_1353218831850316658[11] = 0;
   out_1353218831850316658[12] = 0;
   out_1353218831850316658[13] = 0;
   out_1353218831850316658[14] = 0;
   out_1353218831850316658[15] = 0;
   out_1353218831850316658[16] = 0;
   out_1353218831850316658[17] = 0;
   out_1353218831850316658[18] = 0;
   out_1353218831850316658[19] = 0;
   out_1353218831850316658[20] = 1;
   out_1353218831850316658[21] = 0;
   out_1353218831850316658[22] = 0;
   out_1353218831850316658[23] = 0;
   out_1353218831850316658[24] = 0;
   out_1353218831850316658[25] = 0;
   out_1353218831850316658[26] = 0;
   out_1353218831850316658[27] = 0;
   out_1353218831850316658[28] = 0;
   out_1353218831850316658[29] = 0;
   out_1353218831850316658[30] = 1;
   out_1353218831850316658[31] = 0;
   out_1353218831850316658[32] = 0;
   out_1353218831850316658[33] = 0;
   out_1353218831850316658[34] = 0;
   out_1353218831850316658[35] = 0;
   out_1353218831850316658[36] = 0;
   out_1353218831850316658[37] = 0;
   out_1353218831850316658[38] = 0;
   out_1353218831850316658[39] = 0;
   out_1353218831850316658[40] = 1;
   out_1353218831850316658[41] = 0;
   out_1353218831850316658[42] = 0;
   out_1353218831850316658[43] = 0;
   out_1353218831850316658[44] = 0;
   out_1353218831850316658[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_1353218831850316658[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_1353218831850316658[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_1353218831850316658[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_1353218831850316658[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_1353218831850316658[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_1353218831850316658[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_1353218831850316658[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_1353218831850316658[53] = -9.8000000000000007*dt;
   out_1353218831850316658[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_1353218831850316658[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_1353218831850316658[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_1353218831850316658[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_1353218831850316658[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_1353218831850316658[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_1353218831850316658[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_1353218831850316658[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_1353218831850316658[62] = 0;
   out_1353218831850316658[63] = 0;
   out_1353218831850316658[64] = 0;
   out_1353218831850316658[65] = 0;
   out_1353218831850316658[66] = 0;
   out_1353218831850316658[67] = 0;
   out_1353218831850316658[68] = 0;
   out_1353218831850316658[69] = 0;
   out_1353218831850316658[70] = 1;
   out_1353218831850316658[71] = 0;
   out_1353218831850316658[72] = 0;
   out_1353218831850316658[73] = 0;
   out_1353218831850316658[74] = 0;
   out_1353218831850316658[75] = 0;
   out_1353218831850316658[76] = 0;
   out_1353218831850316658[77] = 0;
   out_1353218831850316658[78] = 0;
   out_1353218831850316658[79] = 0;
   out_1353218831850316658[80] = 1;
}
void h_25(double *state, double *unused, double *out_1344834859822615607) {
   out_1344834859822615607[0] = state[6];
}
void H_25(double *state, double *unused, double *out_6507594322557232788) {
   out_6507594322557232788[0] = 0;
   out_6507594322557232788[1] = 0;
   out_6507594322557232788[2] = 0;
   out_6507594322557232788[3] = 0;
   out_6507594322557232788[4] = 0;
   out_6507594322557232788[5] = 0;
   out_6507594322557232788[6] = 1;
   out_6507594322557232788[7] = 0;
   out_6507594322557232788[8] = 0;
}
void h_24(double *state, double *unused, double *out_5433380832945564861) {
   out_5433380832945564861[0] = state[4];
   out_5433380832945564861[1] = state[5];
}
void H_24(double *state, double *unused, double *out_8680243921562732354) {
   out_8680243921562732354[0] = 0;
   out_8680243921562732354[1] = 0;
   out_8680243921562732354[2] = 0;
   out_8680243921562732354[3] = 0;
   out_8680243921562732354[4] = 1;
   out_8680243921562732354[5] = 0;
   out_8680243921562732354[6] = 0;
   out_8680243921562732354[7] = 0;
   out_8680243921562732354[8] = 0;
   out_8680243921562732354[9] = 0;
   out_8680243921562732354[10] = 0;
   out_8680243921562732354[11] = 0;
   out_8680243921562732354[12] = 0;
   out_8680243921562732354[13] = 0;
   out_8680243921562732354[14] = 1;
   out_8680243921562732354[15] = 0;
   out_8680243921562732354[16] = 0;
   out_8680243921562732354[17] = 0;
}
void h_30(double *state, double *unused, double *out_7964191929203084827) {
   out_7964191929203084827[0] = state[4];
}
void H_30(double *state, double *unused, double *out_6636933269700472858) {
   out_6636933269700472858[0] = 0;
   out_6636933269700472858[1] = 0;
   out_6636933269700472858[2] = 0;
   out_6636933269700472858[3] = 0;
   out_6636933269700472858[4] = 1;
   out_6636933269700472858[5] = 0;
   out_6636933269700472858[6] = 0;
   out_6636933269700472858[7] = 0;
   out_6636933269700472858[8] = 0;
}
void h_26(double *state, double *unused, double *out_7445766093062134104) {
   out_7445766093062134104[0] = state[7];
}
void H_26(double *state, double *unused, double *out_8197646432278262604) {
   out_8197646432278262604[0] = 0;
   out_8197646432278262604[1] = 0;
   out_8197646432278262604[2] = 0;
   out_8197646432278262604[3] = 0;
   out_8197646432278262604[4] = 0;
   out_8197646432278262604[5] = 0;
   out_8197646432278262604[6] = 0;
   out_8197646432278262604[7] = 1;
   out_8197646432278262604[8] = 0;
}
void h_27(double *state, double *unused, double *out_7327758699128757360) {
   out_7327758699128757360[0] = state[3];
}
void H_27(double *state, double *unused, double *out_8811696581500897769) {
   out_8811696581500897769[0] = 0;
   out_8811696581500897769[1] = 0;
   out_8811696581500897769[2] = 0;
   out_8811696581500897769[3] = 1;
   out_8811696581500897769[4] = 0;
   out_8811696581500897769[5] = 0;
   out_8811696581500897769[6] = 0;
   out_8811696581500897769[7] = 0;
   out_8811696581500897769[8] = 0;
}
void h_29(double *state, double *unused, double *out_7020682076301422392) {
   out_7020682076301422392[0] = state[1];
}
void H_29(double *state, double *unused, double *out_7921684765339102814) {
   out_7921684765339102814[0] = 0;
   out_7921684765339102814[1] = 1;
   out_7921684765339102814[2] = 0;
   out_7921684765339102814[3] = 0;
   out_7921684765339102814[4] = 0;
   out_7921684765339102814[5] = 0;
   out_7921684765339102814[6] = 0;
   out_7921684765339102814[7] = 0;
   out_7921684765339102814[8] = 0;
}
void h_28(double *state, double *unused, double *out_4051910886381300771) {
   out_4051910886381300771[0] = state[0];
}
void H_28(double *state, double *unused, double *out_8561429036805122551) {
   out_8561429036805122551[0] = 1;
   out_8561429036805122551[1] = 0;
   out_8561429036805122551[2] = 0;
   out_8561429036805122551[3] = 0;
   out_8561429036805122551[4] = 0;
   out_8561429036805122551[5] = 0;
   out_8561429036805122551[6] = 0;
   out_8561429036805122551[7] = 0;
   out_8561429036805122551[8] = 0;
}
void h_31(double *state, double *unused, double *out_5842118044635442722) {
   out_5842118044635442722[0] = state[8];
}
void H_31(double *state, double *unused, double *out_6476948360680272360) {
   out_6476948360680272360[0] = 0;
   out_6476948360680272360[1] = 0;
   out_6476948360680272360[2] = 0;
   out_6476948360680272360[3] = 0;
   out_6476948360680272360[4] = 0;
   out_6476948360680272360[5] = 0;
   out_6476948360680272360[6] = 0;
   out_6476948360680272360[7] = 0;
   out_6476948360680272360[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_3273042440096814304) {
  err_fun(nom_x, delta_x, out_3273042440096814304);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_5732845985013317398) {
  inv_err_fun(nom_x, true_x, out_5732845985013317398);
}
void car_H_mod_fun(double *state, double *out_421472006259524810) {
  H_mod_fun(state, out_421472006259524810);
}
void car_f_fun(double *state, double dt, double *out_3776724096449913501) {
  f_fun(state,  dt, out_3776724096449913501);
}
void car_F_fun(double *state, double dt, double *out_1353218831850316658) {
  F_fun(state,  dt, out_1353218831850316658);
}
void car_h_25(double *state, double *unused, double *out_1344834859822615607) {
  h_25(state, unused, out_1344834859822615607);
}
void car_H_25(double *state, double *unused, double *out_6507594322557232788) {
  H_25(state, unused, out_6507594322557232788);
}
void car_h_24(double *state, double *unused, double *out_5433380832945564861) {
  h_24(state, unused, out_5433380832945564861);
}
void car_H_24(double *state, double *unused, double *out_8680243921562732354) {
  H_24(state, unused, out_8680243921562732354);
}
void car_h_30(double *state, double *unused, double *out_7964191929203084827) {
  h_30(state, unused, out_7964191929203084827);
}
void car_H_30(double *state, double *unused, double *out_6636933269700472858) {
  H_30(state, unused, out_6636933269700472858);
}
void car_h_26(double *state, double *unused, double *out_7445766093062134104) {
  h_26(state, unused, out_7445766093062134104);
}
void car_H_26(double *state, double *unused, double *out_8197646432278262604) {
  H_26(state, unused, out_8197646432278262604);
}
void car_h_27(double *state, double *unused, double *out_7327758699128757360) {
  h_27(state, unused, out_7327758699128757360);
}
void car_H_27(double *state, double *unused, double *out_8811696581500897769) {
  H_27(state, unused, out_8811696581500897769);
}
void car_h_29(double *state, double *unused, double *out_7020682076301422392) {
  h_29(state, unused, out_7020682076301422392);
}
void car_H_29(double *state, double *unused, double *out_7921684765339102814) {
  H_29(state, unused, out_7921684765339102814);
}
void car_h_28(double *state, double *unused, double *out_4051910886381300771) {
  h_28(state, unused, out_4051910886381300771);
}
void car_H_28(double *state, double *unused, double *out_8561429036805122551) {
  H_28(state, unused, out_8561429036805122551);
}
void car_h_31(double *state, double *unused, double *out_5842118044635442722) {
  h_31(state, unused, out_5842118044635442722);
}
void car_H_31(double *state, double *unused, double *out_6476948360680272360) {
  H_31(state, unused, out_6476948360680272360);
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
