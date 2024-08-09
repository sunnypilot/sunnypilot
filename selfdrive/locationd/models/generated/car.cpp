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
 *                       Code generated with SymPy 1.12                       *
 *                                                                            *
 *              See http://www.sympy.org/ for more information.               *
 *                                                                            *
 *                         This file is part of 'ekf'                         *
 ******************************************************************************/
void err_fun(double *nom_x, double *delta_x, double *out_651882661893372929) {
   out_651882661893372929[0] = delta_x[0] + nom_x[0];
   out_651882661893372929[1] = delta_x[1] + nom_x[1];
   out_651882661893372929[2] = delta_x[2] + nom_x[2];
   out_651882661893372929[3] = delta_x[3] + nom_x[3];
   out_651882661893372929[4] = delta_x[4] + nom_x[4];
   out_651882661893372929[5] = delta_x[5] + nom_x[5];
   out_651882661893372929[6] = delta_x[6] + nom_x[6];
   out_651882661893372929[7] = delta_x[7] + nom_x[7];
   out_651882661893372929[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_727172026312988685) {
   out_727172026312988685[0] = -nom_x[0] + true_x[0];
   out_727172026312988685[1] = -nom_x[1] + true_x[1];
   out_727172026312988685[2] = -nom_x[2] + true_x[2];
   out_727172026312988685[3] = -nom_x[3] + true_x[3];
   out_727172026312988685[4] = -nom_x[4] + true_x[4];
   out_727172026312988685[5] = -nom_x[5] + true_x[5];
   out_727172026312988685[6] = -nom_x[6] + true_x[6];
   out_727172026312988685[7] = -nom_x[7] + true_x[7];
   out_727172026312988685[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_5475808663598843623) {
   out_5475808663598843623[0] = 1.0;
   out_5475808663598843623[1] = 0;
   out_5475808663598843623[2] = 0;
   out_5475808663598843623[3] = 0;
   out_5475808663598843623[4] = 0;
   out_5475808663598843623[5] = 0;
   out_5475808663598843623[6] = 0;
   out_5475808663598843623[7] = 0;
   out_5475808663598843623[8] = 0;
   out_5475808663598843623[9] = 0;
   out_5475808663598843623[10] = 1.0;
   out_5475808663598843623[11] = 0;
   out_5475808663598843623[12] = 0;
   out_5475808663598843623[13] = 0;
   out_5475808663598843623[14] = 0;
   out_5475808663598843623[15] = 0;
   out_5475808663598843623[16] = 0;
   out_5475808663598843623[17] = 0;
   out_5475808663598843623[18] = 0;
   out_5475808663598843623[19] = 0;
   out_5475808663598843623[20] = 1.0;
   out_5475808663598843623[21] = 0;
   out_5475808663598843623[22] = 0;
   out_5475808663598843623[23] = 0;
   out_5475808663598843623[24] = 0;
   out_5475808663598843623[25] = 0;
   out_5475808663598843623[26] = 0;
   out_5475808663598843623[27] = 0;
   out_5475808663598843623[28] = 0;
   out_5475808663598843623[29] = 0;
   out_5475808663598843623[30] = 1.0;
   out_5475808663598843623[31] = 0;
   out_5475808663598843623[32] = 0;
   out_5475808663598843623[33] = 0;
   out_5475808663598843623[34] = 0;
   out_5475808663598843623[35] = 0;
   out_5475808663598843623[36] = 0;
   out_5475808663598843623[37] = 0;
   out_5475808663598843623[38] = 0;
   out_5475808663598843623[39] = 0;
   out_5475808663598843623[40] = 1.0;
   out_5475808663598843623[41] = 0;
   out_5475808663598843623[42] = 0;
   out_5475808663598843623[43] = 0;
   out_5475808663598843623[44] = 0;
   out_5475808663598843623[45] = 0;
   out_5475808663598843623[46] = 0;
   out_5475808663598843623[47] = 0;
   out_5475808663598843623[48] = 0;
   out_5475808663598843623[49] = 0;
   out_5475808663598843623[50] = 1.0;
   out_5475808663598843623[51] = 0;
   out_5475808663598843623[52] = 0;
   out_5475808663598843623[53] = 0;
   out_5475808663598843623[54] = 0;
   out_5475808663598843623[55] = 0;
   out_5475808663598843623[56] = 0;
   out_5475808663598843623[57] = 0;
   out_5475808663598843623[58] = 0;
   out_5475808663598843623[59] = 0;
   out_5475808663598843623[60] = 1.0;
   out_5475808663598843623[61] = 0;
   out_5475808663598843623[62] = 0;
   out_5475808663598843623[63] = 0;
   out_5475808663598843623[64] = 0;
   out_5475808663598843623[65] = 0;
   out_5475808663598843623[66] = 0;
   out_5475808663598843623[67] = 0;
   out_5475808663598843623[68] = 0;
   out_5475808663598843623[69] = 0;
   out_5475808663598843623[70] = 1.0;
   out_5475808663598843623[71] = 0;
   out_5475808663598843623[72] = 0;
   out_5475808663598843623[73] = 0;
   out_5475808663598843623[74] = 0;
   out_5475808663598843623[75] = 0;
   out_5475808663598843623[76] = 0;
   out_5475808663598843623[77] = 0;
   out_5475808663598843623[78] = 0;
   out_5475808663598843623[79] = 0;
   out_5475808663598843623[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_4635679633596871047) {
   out_4635679633596871047[0] = state[0];
   out_4635679633596871047[1] = state[1];
   out_4635679633596871047[2] = state[2];
   out_4635679633596871047[3] = state[3];
   out_4635679633596871047[4] = state[4];
   out_4635679633596871047[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8000000000000007*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_4635679633596871047[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_4635679633596871047[7] = state[7];
   out_4635679633596871047[8] = state[8];
}
void F_fun(double *state, double dt, double *out_6816757899860436014) {
   out_6816757899860436014[0] = 1;
   out_6816757899860436014[1] = 0;
   out_6816757899860436014[2] = 0;
   out_6816757899860436014[3] = 0;
   out_6816757899860436014[4] = 0;
   out_6816757899860436014[5] = 0;
   out_6816757899860436014[6] = 0;
   out_6816757899860436014[7] = 0;
   out_6816757899860436014[8] = 0;
   out_6816757899860436014[9] = 0;
   out_6816757899860436014[10] = 1;
   out_6816757899860436014[11] = 0;
   out_6816757899860436014[12] = 0;
   out_6816757899860436014[13] = 0;
   out_6816757899860436014[14] = 0;
   out_6816757899860436014[15] = 0;
   out_6816757899860436014[16] = 0;
   out_6816757899860436014[17] = 0;
   out_6816757899860436014[18] = 0;
   out_6816757899860436014[19] = 0;
   out_6816757899860436014[20] = 1;
   out_6816757899860436014[21] = 0;
   out_6816757899860436014[22] = 0;
   out_6816757899860436014[23] = 0;
   out_6816757899860436014[24] = 0;
   out_6816757899860436014[25] = 0;
   out_6816757899860436014[26] = 0;
   out_6816757899860436014[27] = 0;
   out_6816757899860436014[28] = 0;
   out_6816757899860436014[29] = 0;
   out_6816757899860436014[30] = 1;
   out_6816757899860436014[31] = 0;
   out_6816757899860436014[32] = 0;
   out_6816757899860436014[33] = 0;
   out_6816757899860436014[34] = 0;
   out_6816757899860436014[35] = 0;
   out_6816757899860436014[36] = 0;
   out_6816757899860436014[37] = 0;
   out_6816757899860436014[38] = 0;
   out_6816757899860436014[39] = 0;
   out_6816757899860436014[40] = 1;
   out_6816757899860436014[41] = 0;
   out_6816757899860436014[42] = 0;
   out_6816757899860436014[43] = 0;
   out_6816757899860436014[44] = 0;
   out_6816757899860436014[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_6816757899860436014[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_6816757899860436014[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_6816757899860436014[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_6816757899860436014[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_6816757899860436014[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_6816757899860436014[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_6816757899860436014[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_6816757899860436014[53] = -9.8000000000000007*dt;
   out_6816757899860436014[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_6816757899860436014[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_6816757899860436014[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_6816757899860436014[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_6816757899860436014[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_6816757899860436014[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_6816757899860436014[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_6816757899860436014[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_6816757899860436014[62] = 0;
   out_6816757899860436014[63] = 0;
   out_6816757899860436014[64] = 0;
   out_6816757899860436014[65] = 0;
   out_6816757899860436014[66] = 0;
   out_6816757899860436014[67] = 0;
   out_6816757899860436014[68] = 0;
   out_6816757899860436014[69] = 0;
   out_6816757899860436014[70] = 1;
   out_6816757899860436014[71] = 0;
   out_6816757899860436014[72] = 0;
   out_6816757899860436014[73] = 0;
   out_6816757899860436014[74] = 0;
   out_6816757899860436014[75] = 0;
   out_6816757899860436014[76] = 0;
   out_6816757899860436014[77] = 0;
   out_6816757899860436014[78] = 0;
   out_6816757899860436014[79] = 0;
   out_6816757899860436014[80] = 1;
}
void h_25(double *state, double *unused, double *out_7319455008445036725) {
   out_7319455008445036725[0] = state[6];
}
void H_25(double *state, double *unused, double *out_654806835171789637) {
   out_654806835171789637[0] = 0;
   out_654806835171789637[1] = 0;
   out_654806835171789637[2] = 0;
   out_654806835171789637[3] = 0;
   out_654806835171789637[4] = 0;
   out_654806835171789637[5] = 0;
   out_654806835171789637[6] = 1;
   out_654806835171789637[7] = 0;
   out_654806835171789637[8] = 0;
}
void h_24(double *state, double *unused, double *out_5541470801123603669) {
   out_5541470801123603669[0] = state[4];
   out_5541470801123603669[1] = state[5];
}
void H_24(double *state, double *unused, double *out_1517842763833709929) {
   out_1517842763833709929[0] = 0;
   out_1517842763833709929[1] = 0;
   out_1517842763833709929[2] = 0;
   out_1517842763833709929[3] = 0;
   out_1517842763833709929[4] = 1;
   out_1517842763833709929[5] = 0;
   out_1517842763833709929[6] = 0;
   out_1517842763833709929[7] = 0;
   out_1517842763833709929[8] = 0;
   out_1517842763833709929[9] = 0;
   out_1517842763833709929[10] = 0;
   out_1517842763833709929[11] = 0;
   out_1517842763833709929[12] = 0;
   out_1517842763833709929[13] = 0;
   out_1517842763833709929[14] = 1;
   out_1517842763833709929[15] = 0;
   out_1517842763833709929[16] = 0;
   out_1517842763833709929[17] = 0;
}
void h_30(double *state, double *unused, double *out_8770086401073919892) {
   out_8770086401073919892[0] = state[4];
}
void H_30(double *state, double *unused, double *out_3173139793679038264) {
   out_3173139793679038264[0] = 0;
   out_3173139793679038264[1] = 0;
   out_3173139793679038264[2] = 0;
   out_3173139793679038264[3] = 0;
   out_3173139793679038264[4] = 1;
   out_3173139793679038264[5] = 0;
   out_3173139793679038264[6] = 0;
   out_3173139793679038264[7] = 0;
   out_3173139793679038264[8] = 0;
}
void h_26(double *state, double *unused, double *out_4033927801554674889) {
   out_4033927801554674889[0] = state[7];
}
void H_26(double *state, double *unused, double *out_3086696483702266587) {
   out_3086696483702266587[0] = 0;
   out_3086696483702266587[1] = 0;
   out_3086696483702266587[2] = 0;
   out_3086696483702266587[3] = 0;
   out_3086696483702266587[4] = 0;
   out_3086696483702266587[5] = 0;
   out_3086696483702266587[6] = 0;
   out_3086696483702266587[7] = 1;
   out_3086696483702266587[8] = 0;
}
void h_27(double *state, double *unused, double *out_3916379579010293380) {
   out_3916379579010293380[0] = state[3];
}
void H_27(double *state, double *unused, double *out_1649295423771875344) {
   out_1649295423771875344[0] = 0;
   out_1649295423771875344[1] = 0;
   out_1649295423771875344[2] = 0;
   out_1649295423771875344[3] = 1;
   out_1649295423771875344[4] = 0;
   out_1649295423771875344[5] = 0;
   out_1649295423771875344[6] = 0;
   out_1649295423771875344[7] = 0;
   out_1649295423771875344[8] = 0;
}
void h_29(double *state, double *unused, double *out_3768413133413074247) {
   out_3768413133413074247[0] = state[1];
}
void H_29(double *state, double *unused, double *out_3362658150641426377) {
   out_3362658150641426377[0] = 0;
   out_3362658150641426377[1] = 1;
   out_3362658150641426377[2] = 0;
   out_3362658150641426377[3] = 0;
   out_3362658150641426377[4] = 0;
   out_3362658150641426377[5] = 0;
   out_3362658150641426377[6] = 0;
   out_3362658150641426377[7] = 0;
   out_3362658150641426377[8] = 0;
}
void h_28(double *state, double *unused, double *out_8652079007140543148) {
   out_8652079007140543148[0] = state[0];
}
void H_28(double *state, double *unused, double *out_1399027879076100126) {
   out_1399027879076100126[0] = 1;
   out_1399027879076100126[1] = 0;
   out_1399027879076100126[2] = 0;
   out_1399027879076100126[3] = 0;
   out_1399027879076100126[4] = 0;
   out_1399027879076100126[5] = 0;
   out_1399027879076100126[6] = 0;
   out_1399027879076100126[7] = 0;
   out_1399027879076100126[8] = 0;
}
void h_31(double *state, double *unused, double *out_548619782094685789) {
   out_548619782094685789[0] = state[8];
}
void H_31(double *state, double *unused, double *out_685452797048750065) {
   out_685452797048750065[0] = 0;
   out_685452797048750065[1] = 0;
   out_685452797048750065[2] = 0;
   out_685452797048750065[3] = 0;
   out_685452797048750065[4] = 0;
   out_685452797048750065[5] = 0;
   out_685452797048750065[6] = 0;
   out_685452797048750065[7] = 0;
   out_685452797048750065[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_651882661893372929) {
  err_fun(nom_x, delta_x, out_651882661893372929);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_727172026312988685) {
  inv_err_fun(nom_x, true_x, out_727172026312988685);
}
void car_H_mod_fun(double *state, double *out_5475808663598843623) {
  H_mod_fun(state, out_5475808663598843623);
}
void car_f_fun(double *state, double dt, double *out_4635679633596871047) {
  f_fun(state,  dt, out_4635679633596871047);
}
void car_F_fun(double *state, double dt, double *out_6816757899860436014) {
  F_fun(state,  dt, out_6816757899860436014);
}
void car_h_25(double *state, double *unused, double *out_7319455008445036725) {
  h_25(state, unused, out_7319455008445036725);
}
void car_H_25(double *state, double *unused, double *out_654806835171789637) {
  H_25(state, unused, out_654806835171789637);
}
void car_h_24(double *state, double *unused, double *out_5541470801123603669) {
  h_24(state, unused, out_5541470801123603669);
}
void car_H_24(double *state, double *unused, double *out_1517842763833709929) {
  H_24(state, unused, out_1517842763833709929);
}
void car_h_30(double *state, double *unused, double *out_8770086401073919892) {
  h_30(state, unused, out_8770086401073919892);
}
void car_H_30(double *state, double *unused, double *out_3173139793679038264) {
  H_30(state, unused, out_3173139793679038264);
}
void car_h_26(double *state, double *unused, double *out_4033927801554674889) {
  h_26(state, unused, out_4033927801554674889);
}
void car_H_26(double *state, double *unused, double *out_3086696483702266587) {
  H_26(state, unused, out_3086696483702266587);
}
void car_h_27(double *state, double *unused, double *out_3916379579010293380) {
  h_27(state, unused, out_3916379579010293380);
}
void car_H_27(double *state, double *unused, double *out_1649295423771875344) {
  H_27(state, unused, out_1649295423771875344);
}
void car_h_29(double *state, double *unused, double *out_3768413133413074247) {
  h_29(state, unused, out_3768413133413074247);
}
void car_H_29(double *state, double *unused, double *out_3362658150641426377) {
  H_29(state, unused, out_3362658150641426377);
}
void car_h_28(double *state, double *unused, double *out_8652079007140543148) {
  h_28(state, unused, out_8652079007140543148);
}
void car_H_28(double *state, double *unused, double *out_1399027879076100126) {
  H_28(state, unused, out_1399027879076100126);
}
void car_h_31(double *state, double *unused, double *out_548619782094685789) {
  h_31(state, unused, out_548619782094685789);
}
void car_H_31(double *state, double *unused, double *out_685452797048750065) {
  H_31(state, unused, out_685452797048750065);
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
