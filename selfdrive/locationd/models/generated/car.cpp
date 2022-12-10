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
void err_fun(double *nom_x, double *delta_x, double *out_6009369833100329869) {
   out_6009369833100329869[0] = delta_x[0] + nom_x[0];
   out_6009369833100329869[1] = delta_x[1] + nom_x[1];
   out_6009369833100329869[2] = delta_x[2] + nom_x[2];
   out_6009369833100329869[3] = delta_x[3] + nom_x[3];
   out_6009369833100329869[4] = delta_x[4] + nom_x[4];
   out_6009369833100329869[5] = delta_x[5] + nom_x[5];
   out_6009369833100329869[6] = delta_x[6] + nom_x[6];
   out_6009369833100329869[7] = delta_x[7] + nom_x[7];
   out_6009369833100329869[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_4988631012282075045) {
   out_4988631012282075045[0] = -nom_x[0] + true_x[0];
   out_4988631012282075045[1] = -nom_x[1] + true_x[1];
   out_4988631012282075045[2] = -nom_x[2] + true_x[2];
   out_4988631012282075045[3] = -nom_x[3] + true_x[3];
   out_4988631012282075045[4] = -nom_x[4] + true_x[4];
   out_4988631012282075045[5] = -nom_x[5] + true_x[5];
   out_4988631012282075045[6] = -nom_x[6] + true_x[6];
   out_4988631012282075045[7] = -nom_x[7] + true_x[7];
   out_4988631012282075045[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_8291842742918771528) {
   out_8291842742918771528[0] = 1.0;
   out_8291842742918771528[1] = 0;
   out_8291842742918771528[2] = 0;
   out_8291842742918771528[3] = 0;
   out_8291842742918771528[4] = 0;
   out_8291842742918771528[5] = 0;
   out_8291842742918771528[6] = 0;
   out_8291842742918771528[7] = 0;
   out_8291842742918771528[8] = 0;
   out_8291842742918771528[9] = 0;
   out_8291842742918771528[10] = 1.0;
   out_8291842742918771528[11] = 0;
   out_8291842742918771528[12] = 0;
   out_8291842742918771528[13] = 0;
   out_8291842742918771528[14] = 0;
   out_8291842742918771528[15] = 0;
   out_8291842742918771528[16] = 0;
   out_8291842742918771528[17] = 0;
   out_8291842742918771528[18] = 0;
   out_8291842742918771528[19] = 0;
   out_8291842742918771528[20] = 1.0;
   out_8291842742918771528[21] = 0;
   out_8291842742918771528[22] = 0;
   out_8291842742918771528[23] = 0;
   out_8291842742918771528[24] = 0;
   out_8291842742918771528[25] = 0;
   out_8291842742918771528[26] = 0;
   out_8291842742918771528[27] = 0;
   out_8291842742918771528[28] = 0;
   out_8291842742918771528[29] = 0;
   out_8291842742918771528[30] = 1.0;
   out_8291842742918771528[31] = 0;
   out_8291842742918771528[32] = 0;
   out_8291842742918771528[33] = 0;
   out_8291842742918771528[34] = 0;
   out_8291842742918771528[35] = 0;
   out_8291842742918771528[36] = 0;
   out_8291842742918771528[37] = 0;
   out_8291842742918771528[38] = 0;
   out_8291842742918771528[39] = 0;
   out_8291842742918771528[40] = 1.0;
   out_8291842742918771528[41] = 0;
   out_8291842742918771528[42] = 0;
   out_8291842742918771528[43] = 0;
   out_8291842742918771528[44] = 0;
   out_8291842742918771528[45] = 0;
   out_8291842742918771528[46] = 0;
   out_8291842742918771528[47] = 0;
   out_8291842742918771528[48] = 0;
   out_8291842742918771528[49] = 0;
   out_8291842742918771528[50] = 1.0;
   out_8291842742918771528[51] = 0;
   out_8291842742918771528[52] = 0;
   out_8291842742918771528[53] = 0;
   out_8291842742918771528[54] = 0;
   out_8291842742918771528[55] = 0;
   out_8291842742918771528[56] = 0;
   out_8291842742918771528[57] = 0;
   out_8291842742918771528[58] = 0;
   out_8291842742918771528[59] = 0;
   out_8291842742918771528[60] = 1.0;
   out_8291842742918771528[61] = 0;
   out_8291842742918771528[62] = 0;
   out_8291842742918771528[63] = 0;
   out_8291842742918771528[64] = 0;
   out_8291842742918771528[65] = 0;
   out_8291842742918771528[66] = 0;
   out_8291842742918771528[67] = 0;
   out_8291842742918771528[68] = 0;
   out_8291842742918771528[69] = 0;
   out_8291842742918771528[70] = 1.0;
   out_8291842742918771528[71] = 0;
   out_8291842742918771528[72] = 0;
   out_8291842742918771528[73] = 0;
   out_8291842742918771528[74] = 0;
   out_8291842742918771528[75] = 0;
   out_8291842742918771528[76] = 0;
   out_8291842742918771528[77] = 0;
   out_8291842742918771528[78] = 0;
   out_8291842742918771528[79] = 0;
   out_8291842742918771528[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_2540038828347396790) {
   out_2540038828347396790[0] = state[0];
   out_2540038828347396790[1] = state[1];
   out_2540038828347396790[2] = state[2];
   out_2540038828347396790[3] = state[3];
   out_2540038828347396790[4] = state[4];
   out_2540038828347396790[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8000000000000007*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_2540038828347396790[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_2540038828347396790[7] = state[7];
   out_2540038828347396790[8] = state[8];
}
void F_fun(double *state, double dt, double *out_582319150166730703) {
   out_582319150166730703[0] = 1;
   out_582319150166730703[1] = 0;
   out_582319150166730703[2] = 0;
   out_582319150166730703[3] = 0;
   out_582319150166730703[4] = 0;
   out_582319150166730703[5] = 0;
   out_582319150166730703[6] = 0;
   out_582319150166730703[7] = 0;
   out_582319150166730703[8] = 0;
   out_582319150166730703[9] = 0;
   out_582319150166730703[10] = 1;
   out_582319150166730703[11] = 0;
   out_582319150166730703[12] = 0;
   out_582319150166730703[13] = 0;
   out_582319150166730703[14] = 0;
   out_582319150166730703[15] = 0;
   out_582319150166730703[16] = 0;
   out_582319150166730703[17] = 0;
   out_582319150166730703[18] = 0;
   out_582319150166730703[19] = 0;
   out_582319150166730703[20] = 1;
   out_582319150166730703[21] = 0;
   out_582319150166730703[22] = 0;
   out_582319150166730703[23] = 0;
   out_582319150166730703[24] = 0;
   out_582319150166730703[25] = 0;
   out_582319150166730703[26] = 0;
   out_582319150166730703[27] = 0;
   out_582319150166730703[28] = 0;
   out_582319150166730703[29] = 0;
   out_582319150166730703[30] = 1;
   out_582319150166730703[31] = 0;
   out_582319150166730703[32] = 0;
   out_582319150166730703[33] = 0;
   out_582319150166730703[34] = 0;
   out_582319150166730703[35] = 0;
   out_582319150166730703[36] = 0;
   out_582319150166730703[37] = 0;
   out_582319150166730703[38] = 0;
   out_582319150166730703[39] = 0;
   out_582319150166730703[40] = 1;
   out_582319150166730703[41] = 0;
   out_582319150166730703[42] = 0;
   out_582319150166730703[43] = 0;
   out_582319150166730703[44] = 0;
   out_582319150166730703[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_582319150166730703[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_582319150166730703[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_582319150166730703[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_582319150166730703[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_582319150166730703[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_582319150166730703[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_582319150166730703[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_582319150166730703[53] = -9.8000000000000007*dt;
   out_582319150166730703[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_582319150166730703[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_582319150166730703[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_582319150166730703[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_582319150166730703[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_582319150166730703[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_582319150166730703[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_582319150166730703[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_582319150166730703[62] = 0;
   out_582319150166730703[63] = 0;
   out_582319150166730703[64] = 0;
   out_582319150166730703[65] = 0;
   out_582319150166730703[66] = 0;
   out_582319150166730703[67] = 0;
   out_582319150166730703[68] = 0;
   out_582319150166730703[69] = 0;
   out_582319150166730703[70] = 1;
   out_582319150166730703[71] = 0;
   out_582319150166730703[72] = 0;
   out_582319150166730703[73] = 0;
   out_582319150166730703[74] = 0;
   out_582319150166730703[75] = 0;
   out_582319150166730703[76] = 0;
   out_582319150166730703[77] = 0;
   out_582319150166730703[78] = 0;
   out_582319150166730703[79] = 0;
   out_582319150166730703[80] = 1;
}
void h_25(double *state, double *unused, double *out_846705907394000494) {
   out_846705907394000494[0] = state[6];
}
void H_25(double *state, double *unused, double *out_6804065410528503604) {
   out_6804065410528503604[0] = 0;
   out_6804065410528503604[1] = 0;
   out_6804065410528503604[2] = 0;
   out_6804065410528503604[3] = 0;
   out_6804065410528503604[4] = 0;
   out_6804065410528503604[5] = 0;
   out_6804065410528503604[6] = 1;
   out_6804065410528503604[7] = 0;
   out_6804065410528503604[8] = 0;
}
void h_24(double *state, double *unused, double *out_5408900164323158659) {
   out_5408900164323158659[0] = state[4];
   out_5408900164323158659[1] = state[5];
}
void H_24(double *state, double *unused, double *out_5067106856589529911) {
   out_5067106856589529911[0] = 0;
   out_5067106856589529911[1] = 0;
   out_5067106856589529911[2] = 0;
   out_5067106856589529911[3] = 0;
   out_5067106856589529911[4] = 1;
   out_5067106856589529911[5] = 0;
   out_5067106856589529911[6] = 0;
   out_5067106856589529911[7] = 0;
   out_5067106856589529911[8] = 0;
   out_5067106856589529911[9] = 0;
   out_5067106856589529911[10] = 0;
   out_5067106856589529911[11] = 0;
   out_5067106856589529911[12] = 0;
   out_5067106856589529911[13] = 0;
   out_5067106856589529911[14] = 1;
   out_5067106856589529911[15] = 0;
   out_5067106856589529911[16] = 0;
   out_5067106856589529911[17] = 0;
}
void h_30(double *state, double *unused, double *out_2664788043652164855) {
   out_2664788043652164855[0] = state[4];
}
void H_30(double *state, double *unused, double *out_9124345704673799385) {
   out_9124345704673799385[0] = 0;
   out_9124345704673799385[1] = 0;
   out_9124345704673799385[2] = 0;
   out_9124345704673799385[3] = 0;
   out_9124345704673799385[4] = 1;
   out_9124345704673799385[5] = 0;
   out_9124345704673799385[6] = 0;
   out_9124345704673799385[7] = 0;
   out_9124345704673799385[8] = 0;
}
void h_26(double *state, double *unused, double *out_3734253473761684291) {
   out_3734253473761684291[0] = state[7];
}
void H_26(double *state, double *unused, double *out_3062562091654447380) {
   out_3062562091654447380[0] = 0;
   out_3062562091654447380[1] = 0;
   out_3062562091654447380[2] = 0;
   out_3062562091654447380[3] = 0;
   out_3062562091654447380[4] = 0;
   out_3062562091654447380[5] = 0;
   out_3062562091654447380[6] = 0;
   out_3062562091654447380[7] = 1;
   out_3062562091654447380[8] = 0;
}
void h_27(double *state, double *unused, double *out_3883491958838333179) {
   out_3883491958838333179[0] = state[3];
}
void H_27(double *state, double *unused, double *out_4499963151584838623) {
   out_4499963151584838623[0] = 0;
   out_4499963151584838623[1] = 0;
   out_4499963151584838623[2] = 0;
   out_4499963151584838623[3] = 1;
   out_4499963151584838623[4] = 0;
   out_4499963151584838623[5] = 0;
   out_4499963151584838623[6] = 0;
   out_4499963151584838623[7] = 0;
   out_4499963151584838623[8] = 0;
}
void h_29(double *state, double *unused, double *out_3608297896553827290) {
   out_3608297896553827290[0] = state[1];
}
void H_29(double *state, double *unused, double *out_2786600424715287590) {
   out_2786600424715287590[0] = 0;
   out_2786600424715287590[1] = 1;
   out_2786600424715287590[2] = 0;
   out_2786600424715287590[3] = 0;
   out_2786600424715287590[4] = 0;
   out_2786600424715287590[5] = 0;
   out_2786600424715287590[6] = 0;
   out_2786600424715287590[7] = 0;
   out_2786600424715287590[8] = 0;
}
void h_28(double *state, double *unused, double *out_6487897279647030830) {
   out_6487897279647030830[0] = state[0];
}
void H_28(double *state, double *unused, double *out_4750230696280613841) {
   out_4750230696280613841[0] = 1;
   out_4750230696280613841[1] = 0;
   out_4750230696280613841[2] = 0;
   out_4750230696280613841[3] = 0;
   out_4750230696280613841[4] = 0;
   out_4750230696280613841[5] = 0;
   out_4750230696280613841[6] = 0;
   out_4750230696280613841[7] = 0;
   out_4750230696280613841[8] = 0;
}
void h_31(double *state, double *unused, double *out_5924129318956350442) {
   out_5924129318956350442[0] = state[8];
}
void H_31(double *state, double *unused, double *out_6834711372405464032) {
   out_6834711372405464032[0] = 0;
   out_6834711372405464032[1] = 0;
   out_6834711372405464032[2] = 0;
   out_6834711372405464032[3] = 0;
   out_6834711372405464032[4] = 0;
   out_6834711372405464032[5] = 0;
   out_6834711372405464032[6] = 0;
   out_6834711372405464032[7] = 0;
   out_6834711372405464032[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_6009369833100329869) {
  err_fun(nom_x, delta_x, out_6009369833100329869);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_4988631012282075045) {
  inv_err_fun(nom_x, true_x, out_4988631012282075045);
}
void car_H_mod_fun(double *state, double *out_8291842742918771528) {
  H_mod_fun(state, out_8291842742918771528);
}
void car_f_fun(double *state, double dt, double *out_2540038828347396790) {
  f_fun(state,  dt, out_2540038828347396790);
}
void car_F_fun(double *state, double dt, double *out_582319150166730703) {
  F_fun(state,  dt, out_582319150166730703);
}
void car_h_25(double *state, double *unused, double *out_846705907394000494) {
  h_25(state, unused, out_846705907394000494);
}
void car_H_25(double *state, double *unused, double *out_6804065410528503604) {
  H_25(state, unused, out_6804065410528503604);
}
void car_h_24(double *state, double *unused, double *out_5408900164323158659) {
  h_24(state, unused, out_5408900164323158659);
}
void car_H_24(double *state, double *unused, double *out_5067106856589529911) {
  H_24(state, unused, out_5067106856589529911);
}
void car_h_30(double *state, double *unused, double *out_2664788043652164855) {
  h_30(state, unused, out_2664788043652164855);
}
void car_H_30(double *state, double *unused, double *out_9124345704673799385) {
  H_30(state, unused, out_9124345704673799385);
}
void car_h_26(double *state, double *unused, double *out_3734253473761684291) {
  h_26(state, unused, out_3734253473761684291);
}
void car_H_26(double *state, double *unused, double *out_3062562091654447380) {
  H_26(state, unused, out_3062562091654447380);
}
void car_h_27(double *state, double *unused, double *out_3883491958838333179) {
  h_27(state, unused, out_3883491958838333179);
}
void car_H_27(double *state, double *unused, double *out_4499963151584838623) {
  H_27(state, unused, out_4499963151584838623);
}
void car_h_29(double *state, double *unused, double *out_3608297896553827290) {
  h_29(state, unused, out_3608297896553827290);
}
void car_H_29(double *state, double *unused, double *out_2786600424715287590) {
  H_29(state, unused, out_2786600424715287590);
}
void car_h_28(double *state, double *unused, double *out_6487897279647030830) {
  h_28(state, unused, out_6487897279647030830);
}
void car_H_28(double *state, double *unused, double *out_4750230696280613841) {
  H_28(state, unused, out_4750230696280613841);
}
void car_h_31(double *state, double *unused, double *out_5924129318956350442) {
  h_31(state, unused, out_5924129318956350442);
}
void car_H_31(double *state, double *unused, double *out_6834711372405464032) {
  H_31(state, unused, out_6834711372405464032);
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
