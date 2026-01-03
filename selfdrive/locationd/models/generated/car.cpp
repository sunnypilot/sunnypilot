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
void err_fun(double *nom_x, double *delta_x, double *out_1708276238722752291) {
   out_1708276238722752291[0] = delta_x[0] + nom_x[0];
   out_1708276238722752291[1] = delta_x[1] + nom_x[1];
   out_1708276238722752291[2] = delta_x[2] + nom_x[2];
   out_1708276238722752291[3] = delta_x[3] + nom_x[3];
   out_1708276238722752291[4] = delta_x[4] + nom_x[4];
   out_1708276238722752291[5] = delta_x[5] + nom_x[5];
   out_1708276238722752291[6] = delta_x[6] + nom_x[6];
   out_1708276238722752291[7] = delta_x[7] + nom_x[7];
   out_1708276238722752291[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_1274280650614196092) {
   out_1274280650614196092[0] = -nom_x[0] + true_x[0];
   out_1274280650614196092[1] = -nom_x[1] + true_x[1];
   out_1274280650614196092[2] = -nom_x[2] + true_x[2];
   out_1274280650614196092[3] = -nom_x[3] + true_x[3];
   out_1274280650614196092[4] = -nom_x[4] + true_x[4];
   out_1274280650614196092[5] = -nom_x[5] + true_x[5];
   out_1274280650614196092[6] = -nom_x[6] + true_x[6];
   out_1274280650614196092[7] = -nom_x[7] + true_x[7];
   out_1274280650614196092[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_4854109873621591679) {
   out_4854109873621591679[0] = 1.0;
   out_4854109873621591679[1] = 0.0;
   out_4854109873621591679[2] = 0.0;
   out_4854109873621591679[3] = 0.0;
   out_4854109873621591679[4] = 0.0;
   out_4854109873621591679[5] = 0.0;
   out_4854109873621591679[6] = 0.0;
   out_4854109873621591679[7] = 0.0;
   out_4854109873621591679[8] = 0.0;
   out_4854109873621591679[9] = 0.0;
   out_4854109873621591679[10] = 1.0;
   out_4854109873621591679[11] = 0.0;
   out_4854109873621591679[12] = 0.0;
   out_4854109873621591679[13] = 0.0;
   out_4854109873621591679[14] = 0.0;
   out_4854109873621591679[15] = 0.0;
   out_4854109873621591679[16] = 0.0;
   out_4854109873621591679[17] = 0.0;
   out_4854109873621591679[18] = 0.0;
   out_4854109873621591679[19] = 0.0;
   out_4854109873621591679[20] = 1.0;
   out_4854109873621591679[21] = 0.0;
   out_4854109873621591679[22] = 0.0;
   out_4854109873621591679[23] = 0.0;
   out_4854109873621591679[24] = 0.0;
   out_4854109873621591679[25] = 0.0;
   out_4854109873621591679[26] = 0.0;
   out_4854109873621591679[27] = 0.0;
   out_4854109873621591679[28] = 0.0;
   out_4854109873621591679[29] = 0.0;
   out_4854109873621591679[30] = 1.0;
   out_4854109873621591679[31] = 0.0;
   out_4854109873621591679[32] = 0.0;
   out_4854109873621591679[33] = 0.0;
   out_4854109873621591679[34] = 0.0;
   out_4854109873621591679[35] = 0.0;
   out_4854109873621591679[36] = 0.0;
   out_4854109873621591679[37] = 0.0;
   out_4854109873621591679[38] = 0.0;
   out_4854109873621591679[39] = 0.0;
   out_4854109873621591679[40] = 1.0;
   out_4854109873621591679[41] = 0.0;
   out_4854109873621591679[42] = 0.0;
   out_4854109873621591679[43] = 0.0;
   out_4854109873621591679[44] = 0.0;
   out_4854109873621591679[45] = 0.0;
   out_4854109873621591679[46] = 0.0;
   out_4854109873621591679[47] = 0.0;
   out_4854109873621591679[48] = 0.0;
   out_4854109873621591679[49] = 0.0;
   out_4854109873621591679[50] = 1.0;
   out_4854109873621591679[51] = 0.0;
   out_4854109873621591679[52] = 0.0;
   out_4854109873621591679[53] = 0.0;
   out_4854109873621591679[54] = 0.0;
   out_4854109873621591679[55] = 0.0;
   out_4854109873621591679[56] = 0.0;
   out_4854109873621591679[57] = 0.0;
   out_4854109873621591679[58] = 0.0;
   out_4854109873621591679[59] = 0.0;
   out_4854109873621591679[60] = 1.0;
   out_4854109873621591679[61] = 0.0;
   out_4854109873621591679[62] = 0.0;
   out_4854109873621591679[63] = 0.0;
   out_4854109873621591679[64] = 0.0;
   out_4854109873621591679[65] = 0.0;
   out_4854109873621591679[66] = 0.0;
   out_4854109873621591679[67] = 0.0;
   out_4854109873621591679[68] = 0.0;
   out_4854109873621591679[69] = 0.0;
   out_4854109873621591679[70] = 1.0;
   out_4854109873621591679[71] = 0.0;
   out_4854109873621591679[72] = 0.0;
   out_4854109873621591679[73] = 0.0;
   out_4854109873621591679[74] = 0.0;
   out_4854109873621591679[75] = 0.0;
   out_4854109873621591679[76] = 0.0;
   out_4854109873621591679[77] = 0.0;
   out_4854109873621591679[78] = 0.0;
   out_4854109873621591679[79] = 0.0;
   out_4854109873621591679[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_7164062772176981129) {
   out_7164062772176981129[0] = state[0];
   out_7164062772176981129[1] = state[1];
   out_7164062772176981129[2] = state[2];
   out_7164062772176981129[3] = state[3];
   out_7164062772176981129[4] = state[4];
   out_7164062772176981129[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8100000000000005*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_7164062772176981129[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_7164062772176981129[7] = state[7];
   out_7164062772176981129[8] = state[8];
}
void F_fun(double *state, double dt, double *out_3676584348292578380) {
   out_3676584348292578380[0] = 1;
   out_3676584348292578380[1] = 0;
   out_3676584348292578380[2] = 0;
   out_3676584348292578380[3] = 0;
   out_3676584348292578380[4] = 0;
   out_3676584348292578380[5] = 0;
   out_3676584348292578380[6] = 0;
   out_3676584348292578380[7] = 0;
   out_3676584348292578380[8] = 0;
   out_3676584348292578380[9] = 0;
   out_3676584348292578380[10] = 1;
   out_3676584348292578380[11] = 0;
   out_3676584348292578380[12] = 0;
   out_3676584348292578380[13] = 0;
   out_3676584348292578380[14] = 0;
   out_3676584348292578380[15] = 0;
   out_3676584348292578380[16] = 0;
   out_3676584348292578380[17] = 0;
   out_3676584348292578380[18] = 0;
   out_3676584348292578380[19] = 0;
   out_3676584348292578380[20] = 1;
   out_3676584348292578380[21] = 0;
   out_3676584348292578380[22] = 0;
   out_3676584348292578380[23] = 0;
   out_3676584348292578380[24] = 0;
   out_3676584348292578380[25] = 0;
   out_3676584348292578380[26] = 0;
   out_3676584348292578380[27] = 0;
   out_3676584348292578380[28] = 0;
   out_3676584348292578380[29] = 0;
   out_3676584348292578380[30] = 1;
   out_3676584348292578380[31] = 0;
   out_3676584348292578380[32] = 0;
   out_3676584348292578380[33] = 0;
   out_3676584348292578380[34] = 0;
   out_3676584348292578380[35] = 0;
   out_3676584348292578380[36] = 0;
   out_3676584348292578380[37] = 0;
   out_3676584348292578380[38] = 0;
   out_3676584348292578380[39] = 0;
   out_3676584348292578380[40] = 1;
   out_3676584348292578380[41] = 0;
   out_3676584348292578380[42] = 0;
   out_3676584348292578380[43] = 0;
   out_3676584348292578380[44] = 0;
   out_3676584348292578380[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_3676584348292578380[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_3676584348292578380[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_3676584348292578380[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_3676584348292578380[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_3676584348292578380[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_3676584348292578380[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_3676584348292578380[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_3676584348292578380[53] = -9.8100000000000005*dt;
   out_3676584348292578380[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_3676584348292578380[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_3676584348292578380[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_3676584348292578380[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_3676584348292578380[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_3676584348292578380[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_3676584348292578380[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_3676584348292578380[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_3676584348292578380[62] = 0;
   out_3676584348292578380[63] = 0;
   out_3676584348292578380[64] = 0;
   out_3676584348292578380[65] = 0;
   out_3676584348292578380[66] = 0;
   out_3676584348292578380[67] = 0;
   out_3676584348292578380[68] = 0;
   out_3676584348292578380[69] = 0;
   out_3676584348292578380[70] = 1;
   out_3676584348292578380[71] = 0;
   out_3676584348292578380[72] = 0;
   out_3676584348292578380[73] = 0;
   out_3676584348292578380[74] = 0;
   out_3676584348292578380[75] = 0;
   out_3676584348292578380[76] = 0;
   out_3676584348292578380[77] = 0;
   out_3676584348292578380[78] = 0;
   out_3676584348292578380[79] = 0;
   out_3676584348292578380[80] = 1;
}
void h_25(double *state, double *unused, double *out_5158107795025371723) {
   out_5158107795025371723[0] = state[6];
}
void H_25(double *state, double *unused, double *out_4339078352290645558) {
   out_4339078352290645558[0] = 0;
   out_4339078352290645558[1] = 0;
   out_4339078352290645558[2] = 0;
   out_4339078352290645558[3] = 0;
   out_4339078352290645558[4] = 0;
   out_4339078352290645558[5] = 0;
   out_4339078352290645558[6] = 1;
   out_4339078352290645558[7] = 0;
   out_4339078352290645558[8] = 0;
}
void h_24(double *state, double *unused, double *out_981736047762438888) {
   out_981736047762438888[0] = state[4];
   out_981736047762438888[1] = state[5];
}
void H_24(double *state, double *unused, double *out_4888986833778549667) {
   out_4888986833778549667[0] = 0;
   out_4888986833778549667[1] = 0;
   out_4888986833778549667[2] = 0;
   out_4888986833778549667[3] = 0;
   out_4888986833778549667[4] = 1;
   out_4888986833778549667[5] = 0;
   out_4888986833778549667[6] = 0;
   out_4888986833778549667[7] = 0;
   out_4888986833778549667[8] = 0;
   out_4888986833778549667[9] = 0;
   out_4888986833778549667[10] = 0;
   out_4888986833778549667[11] = 0;
   out_4888986833778549667[12] = 0;
   out_4888986833778549667[13] = 0;
   out_4888986833778549667[14] = 1;
   out_4888986833778549667[15] = 0;
   out_4888986833778549667[16] = 0;
   out_4888986833778549667[17] = 0;
}
void h_30(double *state, double *unused, double *out_2302450969223516602) {
   out_2302450969223516602[0] = state[4];
}
void H_30(double *state, double *unused, double *out_8866774682418253756) {
   out_8866774682418253756[0] = 0;
   out_8866774682418253756[1] = 0;
   out_8866774682418253756[2] = 0;
   out_8866774682418253756[3] = 0;
   out_8866774682418253756[4] = 1;
   out_8866774682418253756[5] = 0;
   out_8866774682418253756[6] = 0;
   out_8866774682418253756[7] = 0;
   out_8866774682418253756[8] = 0;
}
void h_26(double *state, double *unused, double *out_7528358185058841549) {
   out_7528358185058841549[0] = state[7];
}
void H_26(double *state, double *unused, double *out_8080581671164701782) {
   out_8080581671164701782[0] = 0;
   out_8080581671164701782[1] = 0;
   out_8080581671164701782[2] = 0;
   out_8080581671164701782[3] = 0;
   out_8080581671164701782[4] = 0;
   out_8080581671164701782[5] = 0;
   out_8080581671164701782[6] = 0;
   out_8080581671164701782[7] = 1;
   out_8080581671164701782[8] = 0;
}
void h_27(double *state, double *unused, double *out_2553702474216674072) {
   out_2553702474216674072[0] = state[3];
}
void H_27(double *state, double *unused, double *out_6643180611234310539) {
   out_6643180611234310539[0] = 0;
   out_6643180611234310539[1] = 0;
   out_6643180611234310539[2] = 0;
   out_6643180611234310539[3] = 1;
   out_6643180611234310539[4] = 0;
   out_6643180611234310539[5] = 0;
   out_6643180611234310539[6] = 0;
   out_6643180611234310539[7] = 0;
   out_6643180611234310539[8] = 0;
}
void h_29(double *state, double *unused, double *out_5339237020667849287) {
   out_5339237020667849287[0] = state[1];
}
void H_29(double *state, double *unused, double *out_8356543338103861572) {
   out_8356543338103861572[0] = 0;
   out_8356543338103861572[1] = 1;
   out_8356543338103861572[2] = 0;
   out_8356543338103861572[3] = 0;
   out_8356543338103861572[4] = 0;
   out_8356543338103861572[5] = 0;
   out_8356543338103861572[6] = 0;
   out_8356543338103861572[7] = 0;
   out_8356543338103861572[8] = 0;
}
void h_28(double *state, double *unused, double *out_3903956340727170114) {
   out_3903956340727170114[0] = state[0];
}
void H_28(double *state, double *unused, double *out_6392913066538535321) {
   out_6392913066538535321[0] = 1;
   out_6392913066538535321[1] = 0;
   out_6392913066538535321[2] = 0;
   out_6392913066538535321[3] = 0;
   out_6392913066538535321[4] = 0;
   out_6392913066538535321[5] = 0;
   out_6392913066538535321[6] = 0;
   out_6392913066538535321[7] = 0;
   out_6392913066538535321[8] = 0;
}
void h_31(double *state, double *unused, double *out_5315294463376500868) {
   out_5315294463376500868[0] = state[8];
}
void H_31(double *state, double *unused, double *out_4308432390413685130) {
   out_4308432390413685130[0] = 0;
   out_4308432390413685130[1] = 0;
   out_4308432390413685130[2] = 0;
   out_4308432390413685130[3] = 0;
   out_4308432390413685130[4] = 0;
   out_4308432390413685130[5] = 0;
   out_4308432390413685130[6] = 0;
   out_4308432390413685130[7] = 0;
   out_4308432390413685130[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_1708276238722752291) {
  err_fun(nom_x, delta_x, out_1708276238722752291);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_1274280650614196092) {
  inv_err_fun(nom_x, true_x, out_1274280650614196092);
}
void car_H_mod_fun(double *state, double *out_4854109873621591679) {
  H_mod_fun(state, out_4854109873621591679);
}
void car_f_fun(double *state, double dt, double *out_7164062772176981129) {
  f_fun(state,  dt, out_7164062772176981129);
}
void car_F_fun(double *state, double dt, double *out_3676584348292578380) {
  F_fun(state,  dt, out_3676584348292578380);
}
void car_h_25(double *state, double *unused, double *out_5158107795025371723) {
  h_25(state, unused, out_5158107795025371723);
}
void car_H_25(double *state, double *unused, double *out_4339078352290645558) {
  H_25(state, unused, out_4339078352290645558);
}
void car_h_24(double *state, double *unused, double *out_981736047762438888) {
  h_24(state, unused, out_981736047762438888);
}
void car_H_24(double *state, double *unused, double *out_4888986833778549667) {
  H_24(state, unused, out_4888986833778549667);
}
void car_h_30(double *state, double *unused, double *out_2302450969223516602) {
  h_30(state, unused, out_2302450969223516602);
}
void car_H_30(double *state, double *unused, double *out_8866774682418253756) {
  H_30(state, unused, out_8866774682418253756);
}
void car_h_26(double *state, double *unused, double *out_7528358185058841549) {
  h_26(state, unused, out_7528358185058841549);
}
void car_H_26(double *state, double *unused, double *out_8080581671164701782) {
  H_26(state, unused, out_8080581671164701782);
}
void car_h_27(double *state, double *unused, double *out_2553702474216674072) {
  h_27(state, unused, out_2553702474216674072);
}
void car_H_27(double *state, double *unused, double *out_6643180611234310539) {
  H_27(state, unused, out_6643180611234310539);
}
void car_h_29(double *state, double *unused, double *out_5339237020667849287) {
  h_29(state, unused, out_5339237020667849287);
}
void car_H_29(double *state, double *unused, double *out_8356543338103861572) {
  H_29(state, unused, out_8356543338103861572);
}
void car_h_28(double *state, double *unused, double *out_3903956340727170114) {
  h_28(state, unused, out_3903956340727170114);
}
void car_H_28(double *state, double *unused, double *out_6392913066538535321) {
  H_28(state, unused, out_6392913066538535321);
}
void car_h_31(double *state, double *unused, double *out_5315294463376500868) {
  h_31(state, unused, out_5315294463376500868);
}
void car_H_31(double *state, double *unused, double *out_4308432390413685130) {
  H_31(state, unused, out_4308432390413685130);
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
