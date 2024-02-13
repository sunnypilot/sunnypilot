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
void err_fun(double *nom_x, double *delta_x, double *out_5824625824693245396) {
   out_5824625824693245396[0] = delta_x[0] + nom_x[0];
   out_5824625824693245396[1] = delta_x[1] + nom_x[1];
   out_5824625824693245396[2] = delta_x[2] + nom_x[2];
   out_5824625824693245396[3] = delta_x[3] + nom_x[3];
   out_5824625824693245396[4] = delta_x[4] + nom_x[4];
   out_5824625824693245396[5] = delta_x[5] + nom_x[5];
   out_5824625824693245396[6] = delta_x[6] + nom_x[6];
   out_5824625824693245396[7] = delta_x[7] + nom_x[7];
   out_5824625824693245396[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_827571073640092976) {
   out_827571073640092976[0] = -nom_x[0] + true_x[0];
   out_827571073640092976[1] = -nom_x[1] + true_x[1];
   out_827571073640092976[2] = -nom_x[2] + true_x[2];
   out_827571073640092976[3] = -nom_x[3] + true_x[3];
   out_827571073640092976[4] = -nom_x[4] + true_x[4];
   out_827571073640092976[5] = -nom_x[5] + true_x[5];
   out_827571073640092976[6] = -nom_x[6] + true_x[6];
   out_827571073640092976[7] = -nom_x[7] + true_x[7];
   out_827571073640092976[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_5176602298372304418) {
   out_5176602298372304418[0] = 1.0;
   out_5176602298372304418[1] = 0;
   out_5176602298372304418[2] = 0;
   out_5176602298372304418[3] = 0;
   out_5176602298372304418[4] = 0;
   out_5176602298372304418[5] = 0;
   out_5176602298372304418[6] = 0;
   out_5176602298372304418[7] = 0;
   out_5176602298372304418[8] = 0;
   out_5176602298372304418[9] = 0;
   out_5176602298372304418[10] = 1.0;
   out_5176602298372304418[11] = 0;
   out_5176602298372304418[12] = 0;
   out_5176602298372304418[13] = 0;
   out_5176602298372304418[14] = 0;
   out_5176602298372304418[15] = 0;
   out_5176602298372304418[16] = 0;
   out_5176602298372304418[17] = 0;
   out_5176602298372304418[18] = 0;
   out_5176602298372304418[19] = 0;
   out_5176602298372304418[20] = 1.0;
   out_5176602298372304418[21] = 0;
   out_5176602298372304418[22] = 0;
   out_5176602298372304418[23] = 0;
   out_5176602298372304418[24] = 0;
   out_5176602298372304418[25] = 0;
   out_5176602298372304418[26] = 0;
   out_5176602298372304418[27] = 0;
   out_5176602298372304418[28] = 0;
   out_5176602298372304418[29] = 0;
   out_5176602298372304418[30] = 1.0;
   out_5176602298372304418[31] = 0;
   out_5176602298372304418[32] = 0;
   out_5176602298372304418[33] = 0;
   out_5176602298372304418[34] = 0;
   out_5176602298372304418[35] = 0;
   out_5176602298372304418[36] = 0;
   out_5176602298372304418[37] = 0;
   out_5176602298372304418[38] = 0;
   out_5176602298372304418[39] = 0;
   out_5176602298372304418[40] = 1.0;
   out_5176602298372304418[41] = 0;
   out_5176602298372304418[42] = 0;
   out_5176602298372304418[43] = 0;
   out_5176602298372304418[44] = 0;
   out_5176602298372304418[45] = 0;
   out_5176602298372304418[46] = 0;
   out_5176602298372304418[47] = 0;
   out_5176602298372304418[48] = 0;
   out_5176602298372304418[49] = 0;
   out_5176602298372304418[50] = 1.0;
   out_5176602298372304418[51] = 0;
   out_5176602298372304418[52] = 0;
   out_5176602298372304418[53] = 0;
   out_5176602298372304418[54] = 0;
   out_5176602298372304418[55] = 0;
   out_5176602298372304418[56] = 0;
   out_5176602298372304418[57] = 0;
   out_5176602298372304418[58] = 0;
   out_5176602298372304418[59] = 0;
   out_5176602298372304418[60] = 1.0;
   out_5176602298372304418[61] = 0;
   out_5176602298372304418[62] = 0;
   out_5176602298372304418[63] = 0;
   out_5176602298372304418[64] = 0;
   out_5176602298372304418[65] = 0;
   out_5176602298372304418[66] = 0;
   out_5176602298372304418[67] = 0;
   out_5176602298372304418[68] = 0;
   out_5176602298372304418[69] = 0;
   out_5176602298372304418[70] = 1.0;
   out_5176602298372304418[71] = 0;
   out_5176602298372304418[72] = 0;
   out_5176602298372304418[73] = 0;
   out_5176602298372304418[74] = 0;
   out_5176602298372304418[75] = 0;
   out_5176602298372304418[76] = 0;
   out_5176602298372304418[77] = 0;
   out_5176602298372304418[78] = 0;
   out_5176602298372304418[79] = 0;
   out_5176602298372304418[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_3449864392992608841) {
   out_3449864392992608841[0] = state[0];
   out_3449864392992608841[1] = state[1];
   out_3449864392992608841[2] = state[2];
   out_3449864392992608841[3] = state[3];
   out_3449864392992608841[4] = state[4];
   out_3449864392992608841[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8000000000000007*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_3449864392992608841[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_3449864392992608841[7] = state[7];
   out_3449864392992608841[8] = state[8];
}
void F_fun(double *state, double dt, double *out_5579800985270018693) {
   out_5579800985270018693[0] = 1;
   out_5579800985270018693[1] = 0;
   out_5579800985270018693[2] = 0;
   out_5579800985270018693[3] = 0;
   out_5579800985270018693[4] = 0;
   out_5579800985270018693[5] = 0;
   out_5579800985270018693[6] = 0;
   out_5579800985270018693[7] = 0;
   out_5579800985270018693[8] = 0;
   out_5579800985270018693[9] = 0;
   out_5579800985270018693[10] = 1;
   out_5579800985270018693[11] = 0;
   out_5579800985270018693[12] = 0;
   out_5579800985270018693[13] = 0;
   out_5579800985270018693[14] = 0;
   out_5579800985270018693[15] = 0;
   out_5579800985270018693[16] = 0;
   out_5579800985270018693[17] = 0;
   out_5579800985270018693[18] = 0;
   out_5579800985270018693[19] = 0;
   out_5579800985270018693[20] = 1;
   out_5579800985270018693[21] = 0;
   out_5579800985270018693[22] = 0;
   out_5579800985270018693[23] = 0;
   out_5579800985270018693[24] = 0;
   out_5579800985270018693[25] = 0;
   out_5579800985270018693[26] = 0;
   out_5579800985270018693[27] = 0;
   out_5579800985270018693[28] = 0;
   out_5579800985270018693[29] = 0;
   out_5579800985270018693[30] = 1;
   out_5579800985270018693[31] = 0;
   out_5579800985270018693[32] = 0;
   out_5579800985270018693[33] = 0;
   out_5579800985270018693[34] = 0;
   out_5579800985270018693[35] = 0;
   out_5579800985270018693[36] = 0;
   out_5579800985270018693[37] = 0;
   out_5579800985270018693[38] = 0;
   out_5579800985270018693[39] = 0;
   out_5579800985270018693[40] = 1;
   out_5579800985270018693[41] = 0;
   out_5579800985270018693[42] = 0;
   out_5579800985270018693[43] = 0;
   out_5579800985270018693[44] = 0;
   out_5579800985270018693[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_5579800985270018693[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_5579800985270018693[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_5579800985270018693[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_5579800985270018693[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_5579800985270018693[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_5579800985270018693[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_5579800985270018693[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_5579800985270018693[53] = -9.8000000000000007*dt;
   out_5579800985270018693[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_5579800985270018693[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_5579800985270018693[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_5579800985270018693[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_5579800985270018693[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_5579800985270018693[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_5579800985270018693[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_5579800985270018693[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_5579800985270018693[62] = 0;
   out_5579800985270018693[63] = 0;
   out_5579800985270018693[64] = 0;
   out_5579800985270018693[65] = 0;
   out_5579800985270018693[66] = 0;
   out_5579800985270018693[67] = 0;
   out_5579800985270018693[68] = 0;
   out_5579800985270018693[69] = 0;
   out_5579800985270018693[70] = 1;
   out_5579800985270018693[71] = 0;
   out_5579800985270018693[72] = 0;
   out_5579800985270018693[73] = 0;
   out_5579800985270018693[74] = 0;
   out_5579800985270018693[75] = 0;
   out_5579800985270018693[76] = 0;
   out_5579800985270018693[77] = 0;
   out_5579800985270018693[78] = 0;
   out_5579800985270018693[79] = 0;
   out_5579800985270018693[80] = 1;
}
void h_25(double *state, double *unused, double *out_7875926850580227468) {
   out_7875926850580227468[0] = state[6];
}
void H_25(double *state, double *unused, double *out_4018744907348973114) {
   out_4018744907348973114[0] = 0;
   out_4018744907348973114[1] = 0;
   out_4018744907348973114[2] = 0;
   out_4018744907348973114[3] = 0;
   out_4018744907348973114[4] = 0;
   out_4018744907348973114[5] = 0;
   out_4018744907348973114[6] = 1;
   out_4018744907348973114[7] = 0;
   out_4018744907348973114[8] = 0;
}
void h_24(double *state, double *unused, double *out_5156118782180595319) {
   out_5156118782180595319[0] = state[4];
   out_5156118782180595319[1] = state[5];
}
void H_24(double *state, double *unused, double *out_2289881788171659045) {
   out_2289881788171659045[0] = 0;
   out_2289881788171659045[1] = 0;
   out_2289881788171659045[2] = 0;
   out_2289881788171659045[3] = 0;
   out_2289881788171659045[4] = 1;
   out_2289881788171659045[5] = 0;
   out_2289881788171659045[6] = 0;
   out_2289881788171659045[7] = 0;
   out_2289881788171659045[8] = 0;
   out_2289881788171659045[9] = 0;
   out_2289881788171659045[10] = 0;
   out_2289881788171659045[11] = 0;
   out_2289881788171659045[12] = 0;
   out_2289881788171659045[13] = 0;
   out_2289881788171659045[14] = 1;
   out_2289881788171659045[15] = 0;
   out_2289881788171659045[16] = 0;
   out_2289881788171659045[17] = 0;
}
void h_30(double *state, double *unused, double *out_1105091624229876532) {
   out_1105091624229876532[0] = state[4];
}
void H_30(double *state, double *unused, double *out_7511308824868961747) {
   out_7511308824868961747[0] = 0;
   out_7511308824868961747[1] = 0;
   out_7511308824868961747[2] = 0;
   out_7511308824868961747[3] = 0;
   out_7511308824868961747[4] = 1;
   out_7511308824868961747[5] = 0;
   out_7511308824868961747[6] = 0;
   out_7511308824868961747[7] = 0;
   out_7511308824868961747[8] = 0;
}
void h_26(double *state, double *unused, double *out_3896581643430969113) {
   out_3896581643430969113[0] = state[7];
}
void H_26(double *state, double *unused, double *out_277241588474916890) {
   out_277241588474916890[0] = 0;
   out_277241588474916890[1] = 0;
   out_277241588474916890[2] = 0;
   out_277241588474916890[3] = 0;
   out_277241588474916890[4] = 0;
   out_277241588474916890[5] = 0;
   out_277241588474916890[6] = 0;
   out_277241588474916890[7] = 1;
   out_277241588474916890[8] = 0;
}
void h_27(double *state, double *unused, double *out_5569143955468478503) {
   out_5569143955468478503[0] = state[3];
}
void H_27(double *state, double *unused, double *out_8760671937040164958) {
   out_8760671937040164958[0] = 0;
   out_8760671937040164958[1] = 0;
   out_8760671937040164958[2] = 0;
   out_8760671937040164958[3] = 1;
   out_8760671937040164958[4] = 0;
   out_8760671937040164958[5] = 0;
   out_8760671937040164958[6] = 0;
   out_8760671937040164958[7] = 0;
   out_8760671937040164958[8] = 0;
}
void h_29(double *state, double *unused, double *out_6106764891890722177) {
   out_6106764891890722177[0] = state[1];
}
void H_29(double *state, double *unused, double *out_7001077480554569563) {
   out_7001077480554569563[0] = 0;
   out_7001077480554569563[1] = 1;
   out_7001077480554569563[2] = 0;
   out_7001077480554569563[3] = 0;
   out_7001077480554569563[4] = 0;
   out_7001077480554569563[5] = 0;
   out_7001077480554569563[6] = 0;
   out_7001077480554569563[7] = 0;
   out_7001077480554569563[8] = 0;
}
void h_28(double *state, double *unused, double *out_6512653808370140938) {
   out_6512653808370140938[0] = state[0];
}
void H_28(double *state, double *unused, double *out_6363267576085451479) {
   out_6363267576085451479[0] = 1;
   out_6363267576085451479[1] = 0;
   out_6363267576085451479[2] = 0;
   out_6363267576085451479[3] = 0;
   out_6363267576085451479[4] = 0;
   out_6363267576085451479[5] = 0;
   out_6363267576085451479[6] = 0;
   out_6363267576085451479[7] = 0;
   out_6363267576085451479[8] = 0;
}
void h_31(double *state, double *unused, double *out_2807551966308651707) {
   out_2807551966308651707[0] = state[8];
}
void H_31(double *state, double *unused, double *out_4049390869225933542) {
   out_4049390869225933542[0] = 0;
   out_4049390869225933542[1] = 0;
   out_4049390869225933542[2] = 0;
   out_4049390869225933542[3] = 0;
   out_4049390869225933542[4] = 0;
   out_4049390869225933542[5] = 0;
   out_4049390869225933542[6] = 0;
   out_4049390869225933542[7] = 0;
   out_4049390869225933542[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_5824625824693245396) {
  err_fun(nom_x, delta_x, out_5824625824693245396);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_827571073640092976) {
  inv_err_fun(nom_x, true_x, out_827571073640092976);
}
void car_H_mod_fun(double *state, double *out_5176602298372304418) {
  H_mod_fun(state, out_5176602298372304418);
}
void car_f_fun(double *state, double dt, double *out_3449864392992608841) {
  f_fun(state,  dt, out_3449864392992608841);
}
void car_F_fun(double *state, double dt, double *out_5579800985270018693) {
  F_fun(state,  dt, out_5579800985270018693);
}
void car_h_25(double *state, double *unused, double *out_7875926850580227468) {
  h_25(state, unused, out_7875926850580227468);
}
void car_H_25(double *state, double *unused, double *out_4018744907348973114) {
  H_25(state, unused, out_4018744907348973114);
}
void car_h_24(double *state, double *unused, double *out_5156118782180595319) {
  h_24(state, unused, out_5156118782180595319);
}
void car_H_24(double *state, double *unused, double *out_2289881788171659045) {
  H_24(state, unused, out_2289881788171659045);
}
void car_h_30(double *state, double *unused, double *out_1105091624229876532) {
  h_30(state, unused, out_1105091624229876532);
}
void car_H_30(double *state, double *unused, double *out_7511308824868961747) {
  H_30(state, unused, out_7511308824868961747);
}
void car_h_26(double *state, double *unused, double *out_3896581643430969113) {
  h_26(state, unused, out_3896581643430969113);
}
void car_H_26(double *state, double *unused, double *out_277241588474916890) {
  H_26(state, unused, out_277241588474916890);
}
void car_h_27(double *state, double *unused, double *out_5569143955468478503) {
  h_27(state, unused, out_5569143955468478503);
}
void car_H_27(double *state, double *unused, double *out_8760671937040164958) {
  H_27(state, unused, out_8760671937040164958);
}
void car_h_29(double *state, double *unused, double *out_6106764891890722177) {
  h_29(state, unused, out_6106764891890722177);
}
void car_H_29(double *state, double *unused, double *out_7001077480554569563) {
  H_29(state, unused, out_7001077480554569563);
}
void car_h_28(double *state, double *unused, double *out_6512653808370140938) {
  h_28(state, unused, out_6512653808370140938);
}
void car_H_28(double *state, double *unused, double *out_6363267576085451479) {
  H_28(state, unused, out_6363267576085451479);
}
void car_h_31(double *state, double *unused, double *out_2807551966308651707) {
  h_31(state, unused, out_2807551966308651707);
}
void car_H_31(double *state, double *unused, double *out_4049390869225933542) {
  H_31(state, unused, out_4049390869225933542);
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
