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
void err_fun(double *nom_x, double *delta_x, double *out_1452165264433778352) {
   out_1452165264433778352[0] = delta_x[0] + nom_x[0];
   out_1452165264433778352[1] = delta_x[1] + nom_x[1];
   out_1452165264433778352[2] = delta_x[2] + nom_x[2];
   out_1452165264433778352[3] = delta_x[3] + nom_x[3];
   out_1452165264433778352[4] = delta_x[4] + nom_x[4];
   out_1452165264433778352[5] = delta_x[5] + nom_x[5];
   out_1452165264433778352[6] = delta_x[6] + nom_x[6];
   out_1452165264433778352[7] = delta_x[7] + nom_x[7];
   out_1452165264433778352[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_9135951192458516155) {
   out_9135951192458516155[0] = -nom_x[0] + true_x[0];
   out_9135951192458516155[1] = -nom_x[1] + true_x[1];
   out_9135951192458516155[2] = -nom_x[2] + true_x[2];
   out_9135951192458516155[3] = -nom_x[3] + true_x[3];
   out_9135951192458516155[4] = -nom_x[4] + true_x[4];
   out_9135951192458516155[5] = -nom_x[5] + true_x[5];
   out_9135951192458516155[6] = -nom_x[6] + true_x[6];
   out_9135951192458516155[7] = -nom_x[7] + true_x[7];
   out_9135951192458516155[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_3307709395632443617) {
   out_3307709395632443617[0] = 1.0;
   out_3307709395632443617[1] = 0.0;
   out_3307709395632443617[2] = 0.0;
   out_3307709395632443617[3] = 0.0;
   out_3307709395632443617[4] = 0.0;
   out_3307709395632443617[5] = 0.0;
   out_3307709395632443617[6] = 0.0;
   out_3307709395632443617[7] = 0.0;
   out_3307709395632443617[8] = 0.0;
   out_3307709395632443617[9] = 0.0;
   out_3307709395632443617[10] = 1.0;
   out_3307709395632443617[11] = 0.0;
   out_3307709395632443617[12] = 0.0;
   out_3307709395632443617[13] = 0.0;
   out_3307709395632443617[14] = 0.0;
   out_3307709395632443617[15] = 0.0;
   out_3307709395632443617[16] = 0.0;
   out_3307709395632443617[17] = 0.0;
   out_3307709395632443617[18] = 0.0;
   out_3307709395632443617[19] = 0.0;
   out_3307709395632443617[20] = 1.0;
   out_3307709395632443617[21] = 0.0;
   out_3307709395632443617[22] = 0.0;
   out_3307709395632443617[23] = 0.0;
   out_3307709395632443617[24] = 0.0;
   out_3307709395632443617[25] = 0.0;
   out_3307709395632443617[26] = 0.0;
   out_3307709395632443617[27] = 0.0;
   out_3307709395632443617[28] = 0.0;
   out_3307709395632443617[29] = 0.0;
   out_3307709395632443617[30] = 1.0;
   out_3307709395632443617[31] = 0.0;
   out_3307709395632443617[32] = 0.0;
   out_3307709395632443617[33] = 0.0;
   out_3307709395632443617[34] = 0.0;
   out_3307709395632443617[35] = 0.0;
   out_3307709395632443617[36] = 0.0;
   out_3307709395632443617[37] = 0.0;
   out_3307709395632443617[38] = 0.0;
   out_3307709395632443617[39] = 0.0;
   out_3307709395632443617[40] = 1.0;
   out_3307709395632443617[41] = 0.0;
   out_3307709395632443617[42] = 0.0;
   out_3307709395632443617[43] = 0.0;
   out_3307709395632443617[44] = 0.0;
   out_3307709395632443617[45] = 0.0;
   out_3307709395632443617[46] = 0.0;
   out_3307709395632443617[47] = 0.0;
   out_3307709395632443617[48] = 0.0;
   out_3307709395632443617[49] = 0.0;
   out_3307709395632443617[50] = 1.0;
   out_3307709395632443617[51] = 0.0;
   out_3307709395632443617[52] = 0.0;
   out_3307709395632443617[53] = 0.0;
   out_3307709395632443617[54] = 0.0;
   out_3307709395632443617[55] = 0.0;
   out_3307709395632443617[56] = 0.0;
   out_3307709395632443617[57] = 0.0;
   out_3307709395632443617[58] = 0.0;
   out_3307709395632443617[59] = 0.0;
   out_3307709395632443617[60] = 1.0;
   out_3307709395632443617[61] = 0.0;
   out_3307709395632443617[62] = 0.0;
   out_3307709395632443617[63] = 0.0;
   out_3307709395632443617[64] = 0.0;
   out_3307709395632443617[65] = 0.0;
   out_3307709395632443617[66] = 0.0;
   out_3307709395632443617[67] = 0.0;
   out_3307709395632443617[68] = 0.0;
   out_3307709395632443617[69] = 0.0;
   out_3307709395632443617[70] = 1.0;
   out_3307709395632443617[71] = 0.0;
   out_3307709395632443617[72] = 0.0;
   out_3307709395632443617[73] = 0.0;
   out_3307709395632443617[74] = 0.0;
   out_3307709395632443617[75] = 0.0;
   out_3307709395632443617[76] = 0.0;
   out_3307709395632443617[77] = 0.0;
   out_3307709395632443617[78] = 0.0;
   out_3307709395632443617[79] = 0.0;
   out_3307709395632443617[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_901337125042991402) {
   out_901337125042991402[0] = state[0];
   out_901337125042991402[1] = state[1];
   out_901337125042991402[2] = state[2];
   out_901337125042991402[3] = state[3];
   out_901337125042991402[4] = state[4];
   out_901337125042991402[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8100000000000005*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_901337125042991402[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_901337125042991402[7] = state[7];
   out_901337125042991402[8] = state[8];
}
void F_fun(double *state, double dt, double *out_6056477044377128709) {
   out_6056477044377128709[0] = 1;
   out_6056477044377128709[1] = 0;
   out_6056477044377128709[2] = 0;
   out_6056477044377128709[3] = 0;
   out_6056477044377128709[4] = 0;
   out_6056477044377128709[5] = 0;
   out_6056477044377128709[6] = 0;
   out_6056477044377128709[7] = 0;
   out_6056477044377128709[8] = 0;
   out_6056477044377128709[9] = 0;
   out_6056477044377128709[10] = 1;
   out_6056477044377128709[11] = 0;
   out_6056477044377128709[12] = 0;
   out_6056477044377128709[13] = 0;
   out_6056477044377128709[14] = 0;
   out_6056477044377128709[15] = 0;
   out_6056477044377128709[16] = 0;
   out_6056477044377128709[17] = 0;
   out_6056477044377128709[18] = 0;
   out_6056477044377128709[19] = 0;
   out_6056477044377128709[20] = 1;
   out_6056477044377128709[21] = 0;
   out_6056477044377128709[22] = 0;
   out_6056477044377128709[23] = 0;
   out_6056477044377128709[24] = 0;
   out_6056477044377128709[25] = 0;
   out_6056477044377128709[26] = 0;
   out_6056477044377128709[27] = 0;
   out_6056477044377128709[28] = 0;
   out_6056477044377128709[29] = 0;
   out_6056477044377128709[30] = 1;
   out_6056477044377128709[31] = 0;
   out_6056477044377128709[32] = 0;
   out_6056477044377128709[33] = 0;
   out_6056477044377128709[34] = 0;
   out_6056477044377128709[35] = 0;
   out_6056477044377128709[36] = 0;
   out_6056477044377128709[37] = 0;
   out_6056477044377128709[38] = 0;
   out_6056477044377128709[39] = 0;
   out_6056477044377128709[40] = 1;
   out_6056477044377128709[41] = 0;
   out_6056477044377128709[42] = 0;
   out_6056477044377128709[43] = 0;
   out_6056477044377128709[44] = 0;
   out_6056477044377128709[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_6056477044377128709[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_6056477044377128709[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_6056477044377128709[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_6056477044377128709[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_6056477044377128709[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_6056477044377128709[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_6056477044377128709[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_6056477044377128709[53] = -9.8100000000000005*dt;
   out_6056477044377128709[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_6056477044377128709[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_6056477044377128709[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_6056477044377128709[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_6056477044377128709[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_6056477044377128709[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_6056477044377128709[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_6056477044377128709[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_6056477044377128709[62] = 0;
   out_6056477044377128709[63] = 0;
   out_6056477044377128709[64] = 0;
   out_6056477044377128709[65] = 0;
   out_6056477044377128709[66] = 0;
   out_6056477044377128709[67] = 0;
   out_6056477044377128709[68] = 0;
   out_6056477044377128709[69] = 0;
   out_6056477044377128709[70] = 1;
   out_6056477044377128709[71] = 0;
   out_6056477044377128709[72] = 0;
   out_6056477044377128709[73] = 0;
   out_6056477044377128709[74] = 0;
   out_6056477044377128709[75] = 0;
   out_6056477044377128709[76] = 0;
   out_6056477044377128709[77] = 0;
   out_6056477044377128709[78] = 0;
   out_6056477044377128709[79] = 0;
   out_6056477044377128709[80] = 1;
}
void h_25(double *state, double *unused, double *out_4706993825862034863) {
   out_4706993825862034863[0] = state[6];
}
void H_25(double *state, double *unused, double *out_4613628637341416188) {
   out_4613628637341416188[0] = 0;
   out_4613628637341416188[1] = 0;
   out_4613628637341416188[2] = 0;
   out_4613628637341416188[3] = 0;
   out_4613628637341416188[4] = 0;
   out_4613628637341416188[5] = 0;
   out_4613628637341416188[6] = 1;
   out_4613628637341416188[7] = 0;
   out_4613628637341416188[8] = 0;
}
void h_24(double *state, double *unused, double *out_4084205169702521809) {
   out_4084205169702521809[0] = state[4];
   out_4084205169702521809[1] = state[5];
}
void H_24(double *state, double *unused, double *out_8171554236143739324) {
   out_8171554236143739324[0] = 0;
   out_8171554236143739324[1] = 0;
   out_8171554236143739324[2] = 0;
   out_8171554236143739324[3] = 0;
   out_8171554236143739324[4] = 1;
   out_8171554236143739324[5] = 0;
   out_8171554236143739324[6] = 0;
   out_8171554236143739324[7] = 0;
   out_8171554236143739324[8] = 0;
   out_8171554236143739324[9] = 0;
   out_8171554236143739324[10] = 0;
   out_8171554236143739324[11] = 0;
   out_8171554236143739324[12] = 0;
   out_8171554236143739324[13] = 0;
   out_8171554236143739324[14] = 1;
   out_8171554236143739324[15] = 0;
   out_8171554236143739324[16] = 0;
   out_8171554236143739324[17] = 0;
}
void h_30(double *state, double *unused, double *out_4746632271668782499) {
   out_4746632271668782499[0] = state[4];
}
void H_30(double *state, double *unused, double *out_7131961595848664815) {
   out_7131961595848664815[0] = 0;
   out_7131961595848664815[1] = 0;
   out_7131961595848664815[2] = 0;
   out_7131961595848664815[3] = 0;
   out_7131961595848664815[4] = 1;
   out_7131961595848664815[5] = 0;
   out_7131961595848664815[6] = 0;
   out_7131961595848664815[7] = 0;
   out_7131961595848664815[8] = 0;
}
void h_26(double *state, double *unused, double *out_896097599412174336) {
   out_896097599412174336[0] = state[7];
}
void H_26(double *state, double *unused, double *out_872125318467359964) {
   out_872125318467359964[0] = 0;
   out_872125318467359964[1] = 0;
   out_872125318467359964[2] = 0;
   out_872125318467359964[3] = 0;
   out_872125318467359964[4] = 0;
   out_872125318467359964[5] = 0;
   out_872125318467359964[6] = 0;
   out_872125318467359964[7] = 1;
   out_872125318467359964[8] = 0;
}
void h_27(double *state, double *unused, double *out_8513843032012191806) {
   out_8513843032012191806[0] = state[3];
}
void H_27(double *state, double *unused, double *out_2088831004586616921) {
   out_2088831004586616921[0] = 0;
   out_2088831004586616921[1] = 0;
   out_2088831004586616921[2] = 0;
   out_2088831004586616921[3] = 1;
   out_2088831004586616921[4] = 0;
   out_2088831004586616921[5] = 0;
   out_2088831004586616921[6] = 0;
   out_2088831004586616921[7] = 0;
   out_2088831004586616921[8] = 0;
}
void h_29(double *state, double *unused, double *out_2150249053710375945) {
   out_2150249053710375945[0] = state[1];
}
void H_29(double *state, double *unused, double *out_596163651528200174) {
   out_596163651528200174[0] = 0;
   out_596163651528200174[1] = 1;
   out_596163651528200174[2] = 0;
   out_596163651528200174[3] = 0;
   out_596163651528200174[4] = 0;
   out_596163651528200174[5] = 0;
   out_596163651528200174[6] = 0;
   out_596163651528200174[7] = 0;
   out_596163651528200174[8] = 0;
}
void h_28(double *state, double *unused, double *out_4115890950730562794) {
   out_4115890950730562794[0] = state[0];
}
void H_28(double *state, double *unused, double *out_2559793923093526425) {
   out_2559793923093526425[0] = 1;
   out_2559793923093526425[1] = 0;
   out_2559793923093526425[2] = 0;
   out_2559793923093526425[3] = 0;
   out_2559793923093526425[4] = 0;
   out_2559793923093526425[5] = 0;
   out_2559793923093526425[6] = 0;
   out_2559793923093526425[7] = 0;
   out_2559793923093526425[8] = 0;
}
void h_31(double *state, double *unused, double *out_5976484991026844312) {
   out_5976484991026844312[0] = state[8];
}
void H_31(double *state, double *unused, double *out_245917216234008488) {
   out_245917216234008488[0] = 0;
   out_245917216234008488[1] = 0;
   out_245917216234008488[2] = 0;
   out_245917216234008488[3] = 0;
   out_245917216234008488[4] = 0;
   out_245917216234008488[5] = 0;
   out_245917216234008488[6] = 0;
   out_245917216234008488[7] = 0;
   out_245917216234008488[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_1452165264433778352) {
  err_fun(nom_x, delta_x, out_1452165264433778352);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_9135951192458516155) {
  inv_err_fun(nom_x, true_x, out_9135951192458516155);
}
void car_H_mod_fun(double *state, double *out_3307709395632443617) {
  H_mod_fun(state, out_3307709395632443617);
}
void car_f_fun(double *state, double dt, double *out_901337125042991402) {
  f_fun(state,  dt, out_901337125042991402);
}
void car_F_fun(double *state, double dt, double *out_6056477044377128709) {
  F_fun(state,  dt, out_6056477044377128709);
}
void car_h_25(double *state, double *unused, double *out_4706993825862034863) {
  h_25(state, unused, out_4706993825862034863);
}
void car_H_25(double *state, double *unused, double *out_4613628637341416188) {
  H_25(state, unused, out_4613628637341416188);
}
void car_h_24(double *state, double *unused, double *out_4084205169702521809) {
  h_24(state, unused, out_4084205169702521809);
}
void car_H_24(double *state, double *unused, double *out_8171554236143739324) {
  H_24(state, unused, out_8171554236143739324);
}
void car_h_30(double *state, double *unused, double *out_4746632271668782499) {
  h_30(state, unused, out_4746632271668782499);
}
void car_H_30(double *state, double *unused, double *out_7131961595848664815) {
  H_30(state, unused, out_7131961595848664815);
}
void car_h_26(double *state, double *unused, double *out_896097599412174336) {
  h_26(state, unused, out_896097599412174336);
}
void car_H_26(double *state, double *unused, double *out_872125318467359964) {
  H_26(state, unused, out_872125318467359964);
}
void car_h_27(double *state, double *unused, double *out_8513843032012191806) {
  h_27(state, unused, out_8513843032012191806);
}
void car_H_27(double *state, double *unused, double *out_2088831004586616921) {
  H_27(state, unused, out_2088831004586616921);
}
void car_h_29(double *state, double *unused, double *out_2150249053710375945) {
  h_29(state, unused, out_2150249053710375945);
}
void car_H_29(double *state, double *unused, double *out_596163651528200174) {
  H_29(state, unused, out_596163651528200174);
}
void car_h_28(double *state, double *unused, double *out_4115890950730562794) {
  h_28(state, unused, out_4115890950730562794);
}
void car_H_28(double *state, double *unused, double *out_2559793923093526425) {
  H_28(state, unused, out_2559793923093526425);
}
void car_h_31(double *state, double *unused, double *out_5976484991026844312) {
  h_31(state, unused, out_5976484991026844312);
}
void car_H_31(double *state, double *unused, double *out_245917216234008488) {
  H_31(state, unused, out_245917216234008488);
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
