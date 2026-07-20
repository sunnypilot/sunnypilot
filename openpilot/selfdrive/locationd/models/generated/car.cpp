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
void err_fun(double *nom_x, double *delta_x, double *out_4503132331689013745) {
   out_4503132331689013745[0] = delta_x[0] + nom_x[0];
   out_4503132331689013745[1] = delta_x[1] + nom_x[1];
   out_4503132331689013745[2] = delta_x[2] + nom_x[2];
   out_4503132331689013745[3] = delta_x[3] + nom_x[3];
   out_4503132331689013745[4] = delta_x[4] + nom_x[4];
   out_4503132331689013745[5] = delta_x[5] + nom_x[5];
   out_4503132331689013745[6] = delta_x[6] + nom_x[6];
   out_4503132331689013745[7] = delta_x[7] + nom_x[7];
   out_4503132331689013745[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_5519222819843562437) {
   out_5519222819843562437[0] = -nom_x[0] + true_x[0];
   out_5519222819843562437[1] = -nom_x[1] + true_x[1];
   out_5519222819843562437[2] = -nom_x[2] + true_x[2];
   out_5519222819843562437[3] = -nom_x[3] + true_x[3];
   out_5519222819843562437[4] = -nom_x[4] + true_x[4];
   out_5519222819843562437[5] = -nom_x[5] + true_x[5];
   out_5519222819843562437[6] = -nom_x[6] + true_x[6];
   out_5519222819843562437[7] = -nom_x[7] + true_x[7];
   out_5519222819843562437[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_99880963271144866) {
   out_99880963271144866[0] = 1.0;
   out_99880963271144866[1] = 0.0;
   out_99880963271144866[2] = 0.0;
   out_99880963271144866[3] = 0.0;
   out_99880963271144866[4] = 0.0;
   out_99880963271144866[5] = 0.0;
   out_99880963271144866[6] = 0.0;
   out_99880963271144866[7] = 0.0;
   out_99880963271144866[8] = 0.0;
   out_99880963271144866[9] = 0.0;
   out_99880963271144866[10] = 1.0;
   out_99880963271144866[11] = 0.0;
   out_99880963271144866[12] = 0.0;
   out_99880963271144866[13] = 0.0;
   out_99880963271144866[14] = 0.0;
   out_99880963271144866[15] = 0.0;
   out_99880963271144866[16] = 0.0;
   out_99880963271144866[17] = 0.0;
   out_99880963271144866[18] = 0.0;
   out_99880963271144866[19] = 0.0;
   out_99880963271144866[20] = 1.0;
   out_99880963271144866[21] = 0.0;
   out_99880963271144866[22] = 0.0;
   out_99880963271144866[23] = 0.0;
   out_99880963271144866[24] = 0.0;
   out_99880963271144866[25] = 0.0;
   out_99880963271144866[26] = 0.0;
   out_99880963271144866[27] = 0.0;
   out_99880963271144866[28] = 0.0;
   out_99880963271144866[29] = 0.0;
   out_99880963271144866[30] = 1.0;
   out_99880963271144866[31] = 0.0;
   out_99880963271144866[32] = 0.0;
   out_99880963271144866[33] = 0.0;
   out_99880963271144866[34] = 0.0;
   out_99880963271144866[35] = 0.0;
   out_99880963271144866[36] = 0.0;
   out_99880963271144866[37] = 0.0;
   out_99880963271144866[38] = 0.0;
   out_99880963271144866[39] = 0.0;
   out_99880963271144866[40] = 1.0;
   out_99880963271144866[41] = 0.0;
   out_99880963271144866[42] = 0.0;
   out_99880963271144866[43] = 0.0;
   out_99880963271144866[44] = 0.0;
   out_99880963271144866[45] = 0.0;
   out_99880963271144866[46] = 0.0;
   out_99880963271144866[47] = 0.0;
   out_99880963271144866[48] = 0.0;
   out_99880963271144866[49] = 0.0;
   out_99880963271144866[50] = 1.0;
   out_99880963271144866[51] = 0.0;
   out_99880963271144866[52] = 0.0;
   out_99880963271144866[53] = 0.0;
   out_99880963271144866[54] = 0.0;
   out_99880963271144866[55] = 0.0;
   out_99880963271144866[56] = 0.0;
   out_99880963271144866[57] = 0.0;
   out_99880963271144866[58] = 0.0;
   out_99880963271144866[59] = 0.0;
   out_99880963271144866[60] = 1.0;
   out_99880963271144866[61] = 0.0;
   out_99880963271144866[62] = 0.0;
   out_99880963271144866[63] = 0.0;
   out_99880963271144866[64] = 0.0;
   out_99880963271144866[65] = 0.0;
   out_99880963271144866[66] = 0.0;
   out_99880963271144866[67] = 0.0;
   out_99880963271144866[68] = 0.0;
   out_99880963271144866[69] = 0.0;
   out_99880963271144866[70] = 1.0;
   out_99880963271144866[71] = 0.0;
   out_99880963271144866[72] = 0.0;
   out_99880963271144866[73] = 0.0;
   out_99880963271144866[74] = 0.0;
   out_99880963271144866[75] = 0.0;
   out_99880963271144866[76] = 0.0;
   out_99880963271144866[77] = 0.0;
   out_99880963271144866[78] = 0.0;
   out_99880963271144866[79] = 0.0;
   out_99880963271144866[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_4490574509847198287) {
   out_4490574509847198287[0] = state[0];
   out_4490574509847198287[1] = state[1];
   out_4490574509847198287[2] = state[2];
   out_4490574509847198287[3] = state[3];
   out_4490574509847198287[4] = state[4];
   out_4490574509847198287[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8100000000000005*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_4490574509847198287[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_4490574509847198287[7] = state[7];
   out_4490574509847198287[8] = state[8];
}
void F_fun(double *state, double dt, double *out_5588273031121660281) {
   out_5588273031121660281[0] = 1;
   out_5588273031121660281[1] = 0;
   out_5588273031121660281[2] = 0;
   out_5588273031121660281[3] = 0;
   out_5588273031121660281[4] = 0;
   out_5588273031121660281[5] = 0;
   out_5588273031121660281[6] = 0;
   out_5588273031121660281[7] = 0;
   out_5588273031121660281[8] = 0;
   out_5588273031121660281[9] = 0;
   out_5588273031121660281[10] = 1;
   out_5588273031121660281[11] = 0;
   out_5588273031121660281[12] = 0;
   out_5588273031121660281[13] = 0;
   out_5588273031121660281[14] = 0;
   out_5588273031121660281[15] = 0;
   out_5588273031121660281[16] = 0;
   out_5588273031121660281[17] = 0;
   out_5588273031121660281[18] = 0;
   out_5588273031121660281[19] = 0;
   out_5588273031121660281[20] = 1;
   out_5588273031121660281[21] = 0;
   out_5588273031121660281[22] = 0;
   out_5588273031121660281[23] = 0;
   out_5588273031121660281[24] = 0;
   out_5588273031121660281[25] = 0;
   out_5588273031121660281[26] = 0;
   out_5588273031121660281[27] = 0;
   out_5588273031121660281[28] = 0;
   out_5588273031121660281[29] = 0;
   out_5588273031121660281[30] = 1;
   out_5588273031121660281[31] = 0;
   out_5588273031121660281[32] = 0;
   out_5588273031121660281[33] = 0;
   out_5588273031121660281[34] = 0;
   out_5588273031121660281[35] = 0;
   out_5588273031121660281[36] = 0;
   out_5588273031121660281[37] = 0;
   out_5588273031121660281[38] = 0;
   out_5588273031121660281[39] = 0;
   out_5588273031121660281[40] = 1;
   out_5588273031121660281[41] = 0;
   out_5588273031121660281[42] = 0;
   out_5588273031121660281[43] = 0;
   out_5588273031121660281[44] = 0;
   out_5588273031121660281[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_5588273031121660281[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_5588273031121660281[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_5588273031121660281[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_5588273031121660281[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_5588273031121660281[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_5588273031121660281[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_5588273031121660281[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_5588273031121660281[53] = -9.8100000000000005*dt;
   out_5588273031121660281[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_5588273031121660281[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_5588273031121660281[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_5588273031121660281[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_5588273031121660281[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_5588273031121660281[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_5588273031121660281[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_5588273031121660281[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_5588273031121660281[62] = 0;
   out_5588273031121660281[63] = 0;
   out_5588273031121660281[64] = 0;
   out_5588273031121660281[65] = 0;
   out_5588273031121660281[66] = 0;
   out_5588273031121660281[67] = 0;
   out_5588273031121660281[68] = 0;
   out_5588273031121660281[69] = 0;
   out_5588273031121660281[70] = 1;
   out_5588273031121660281[71] = 0;
   out_5588273031121660281[72] = 0;
   out_5588273031121660281[73] = 0;
   out_5588273031121660281[74] = 0;
   out_5588273031121660281[75] = 0;
   out_5588273031121660281[76] = 0;
   out_5588273031121660281[77] = 0;
   out_5588273031121660281[78] = 0;
   out_5588273031121660281[79] = 0;
   out_5588273031121660281[80] = 1;
}
void h_25(double *state, double *unused, double *out_4633670035125740311) {
   out_4633670035125740311[0] = state[6];
}
void H_25(double *state, double *unused, double *out_9153674884526169513) {
   out_9153674884526169513[0] = 0;
   out_9153674884526169513[1] = 0;
   out_9153674884526169513[2] = 0;
   out_9153674884526169513[3] = 0;
   out_9153674884526169513[4] = 0;
   out_9153674884526169513[5] = 0;
   out_9153674884526169513[6] = 1;
   out_9153674884526169513[7] = 0;
   out_9153674884526169513[8] = 0;
}
void h_24(double *state, double *unused, double *out_4147879785077922233) {
   out_4147879785077922233[0] = state[4];
   out_4147879785077922233[1] = state[5];
}
void H_24(double *state, double *unused, double *out_7067361405204513541) {
   out_7067361405204513541[0] = 0;
   out_7067361405204513541[1] = 0;
   out_7067361405204513541[2] = 0;
   out_7067361405204513541[3] = 0;
   out_7067361405204513541[4] = 1;
   out_7067361405204513541[5] = 0;
   out_7067361405204513541[6] = 0;
   out_7067361405204513541[7] = 0;
   out_7067361405204513541[8] = 0;
   out_7067361405204513541[9] = 0;
   out_7067361405204513541[10] = 0;
   out_7067361405204513541[11] = 0;
   out_7067361405204513541[12] = 0;
   out_7067361405204513541[13] = 0;
   out_7067361405204513541[14] = 1;
   out_7067361405204513541[15] = 0;
   out_7067361405204513541[16] = 0;
   out_7067361405204513541[17] = 0;
}
void h_30(double *state, double *unused, double *out_8271119563379762661) {
   out_8271119563379762661[0] = state[4];
}
void H_30(double *state, double *unused, double *out_2376378847691765348) {
   out_2376378847691765348[0] = 0;
   out_2376378847691765348[1] = 0;
   out_2376378847691765348[2] = 0;
   out_2376378847691765348[3] = 0;
   out_2376378847691765348[4] = 1;
   out_2376378847691765348[5] = 0;
   out_2376378847691765348[6] = 0;
   out_2376378847691765348[7] = 0;
   out_2376378847691765348[8] = 0;
}
void h_26(double *state, double *unused, double *out_749423849060713781) {
   out_749423849060713781[0] = state[7];
}
void H_26(double *state, double *unused, double *out_5412171565652113289) {
   out_5412171565652113289[0] = 0;
   out_5412171565652113289[1] = 0;
   out_5412171565652113289[2] = 0;
   out_5412171565652113289[3] = 0;
   out_5412171565652113289[4] = 0;
   out_5412171565652113289[5] = 0;
   out_5412171565652113289[6] = 0;
   out_5412171565652113289[7] = 1;
   out_5412171565652113289[8] = 0;
}
void h_27(double *state, double *unused, double *out_2801473399302960502) {
   out_2801473399302960502[0] = state[3];
}
void H_27(double *state, double *unused, double *out_6849572625582504532) {
   out_6849572625582504532[0] = 0;
   out_6849572625582504532[1] = 0;
   out_6849572625582504532[2] = 0;
   out_6849572625582504532[3] = 1;
   out_6849572625582504532[4] = 0;
   out_6849572625582504532[5] = 0;
   out_6849572625582504532[6] = 0;
   out_6849572625582504532[7] = 0;
   out_6849572625582504532[8] = 0;
}
void h_29(double *state, double *unused, double *out_5173951242668943310) {
   out_5173951242668943310[0] = state[1];
}
void H_29(double *state, double *unused, double *out_8912176792012229989) {
   out_8912176792012229989[0] = 0;
   out_8912176792012229989[1] = 1;
   out_8912176792012229989[2] = 0;
   out_8912176792012229989[3] = 0;
   out_8912176792012229989[4] = 0;
   out_8912176792012229989[5] = 0;
   out_8912176792012229989[6] = 0;
   out_8912176792012229989[7] = 0;
   out_8912176792012229989[8] = 0;
}
void h_28(double *state, double *unused, double *out_5994836064963036638) {
   out_5994836064963036638[0] = state[0];
}
void H_28(double *state, double *unused, double *out_6948546520446903738) {
   out_6948546520446903738[0] = 1;
   out_6948546520446903738[1] = 0;
   out_6948546520446903738[2] = 0;
   out_6948546520446903738[3] = 0;
   out_6948546520446903738[4] = 0;
   out_6948546520446903738[5] = 0;
   out_6948546520446903738[6] = 0;
   out_6948546520446903738[7] = 0;
   out_6948546520446903738[8] = 0;
}
void h_31(double *state, double *unused, double *out_6352515274334922980) {
   out_6352515274334922980[0] = state[8];
}
void H_31(double *state, double *unused, double *out_9184320846403129941) {
   out_9184320846403129941[0] = 0;
   out_9184320846403129941[1] = 0;
   out_9184320846403129941[2] = 0;
   out_9184320846403129941[3] = 0;
   out_9184320846403129941[4] = 0;
   out_9184320846403129941[5] = 0;
   out_9184320846403129941[6] = 0;
   out_9184320846403129941[7] = 0;
   out_9184320846403129941[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_4503132331689013745) {
  err_fun(nom_x, delta_x, out_4503132331689013745);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_5519222819843562437) {
  inv_err_fun(nom_x, true_x, out_5519222819843562437);
}
void car_H_mod_fun(double *state, double *out_99880963271144866) {
  H_mod_fun(state, out_99880963271144866);
}
void car_f_fun(double *state, double dt, double *out_4490574509847198287) {
  f_fun(state,  dt, out_4490574509847198287);
}
void car_F_fun(double *state, double dt, double *out_5588273031121660281) {
  F_fun(state,  dt, out_5588273031121660281);
}
void car_h_25(double *state, double *unused, double *out_4633670035125740311) {
  h_25(state, unused, out_4633670035125740311);
}
void car_H_25(double *state, double *unused, double *out_9153674884526169513) {
  H_25(state, unused, out_9153674884526169513);
}
void car_h_24(double *state, double *unused, double *out_4147879785077922233) {
  h_24(state, unused, out_4147879785077922233);
}
void car_H_24(double *state, double *unused, double *out_7067361405204513541) {
  H_24(state, unused, out_7067361405204513541);
}
void car_h_30(double *state, double *unused, double *out_8271119563379762661) {
  h_30(state, unused, out_8271119563379762661);
}
void car_H_30(double *state, double *unused, double *out_2376378847691765348) {
  H_30(state, unused, out_2376378847691765348);
}
void car_h_26(double *state, double *unused, double *out_749423849060713781) {
  h_26(state, unused, out_749423849060713781);
}
void car_H_26(double *state, double *unused, double *out_5412171565652113289) {
  H_26(state, unused, out_5412171565652113289);
}
void car_h_27(double *state, double *unused, double *out_2801473399302960502) {
  h_27(state, unused, out_2801473399302960502);
}
void car_H_27(double *state, double *unused, double *out_6849572625582504532) {
  H_27(state, unused, out_6849572625582504532);
}
void car_h_29(double *state, double *unused, double *out_5173951242668943310) {
  h_29(state, unused, out_5173951242668943310);
}
void car_H_29(double *state, double *unused, double *out_8912176792012229989) {
  H_29(state, unused, out_8912176792012229989);
}
void car_h_28(double *state, double *unused, double *out_5994836064963036638) {
  h_28(state, unused, out_5994836064963036638);
}
void car_H_28(double *state, double *unused, double *out_6948546520446903738) {
  H_28(state, unused, out_6948546520446903738);
}
void car_h_31(double *state, double *unused, double *out_6352515274334922980) {
  h_31(state, unused, out_6352515274334922980);
}
void car_H_31(double *state, double *unused, double *out_9184320846403129941) {
  H_31(state, unused, out_9184320846403129941);
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
