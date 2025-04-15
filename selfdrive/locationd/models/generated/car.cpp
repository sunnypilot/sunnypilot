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
 *                      Code generated with SymPy 1.13.2                      *
 *                                                                            *
 *              See http://www.sympy.org/ for more information.               *
 *                                                                            *
 *                         This file is part of 'ekf'                         *
 ******************************************************************************/
void err_fun(double *nom_x, double *delta_x, double *out_1648004092401022955) {
   out_1648004092401022955[0] = delta_x[0] + nom_x[0];
   out_1648004092401022955[1] = delta_x[1] + nom_x[1];
   out_1648004092401022955[2] = delta_x[2] + nom_x[2];
   out_1648004092401022955[3] = delta_x[3] + nom_x[3];
   out_1648004092401022955[4] = delta_x[4] + nom_x[4];
   out_1648004092401022955[5] = delta_x[5] + nom_x[5];
   out_1648004092401022955[6] = delta_x[6] + nom_x[6];
   out_1648004092401022955[7] = delta_x[7] + nom_x[7];
   out_1648004092401022955[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_8224224676727042815) {
   out_8224224676727042815[0] = -nom_x[0] + true_x[0];
   out_8224224676727042815[1] = -nom_x[1] + true_x[1];
   out_8224224676727042815[2] = -nom_x[2] + true_x[2];
   out_8224224676727042815[3] = -nom_x[3] + true_x[3];
   out_8224224676727042815[4] = -nom_x[4] + true_x[4];
   out_8224224676727042815[5] = -nom_x[5] + true_x[5];
   out_8224224676727042815[6] = -nom_x[6] + true_x[6];
   out_8224224676727042815[7] = -nom_x[7] + true_x[7];
   out_8224224676727042815[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_8414001810184439650) {
   out_8414001810184439650[0] = 1.0;
   out_8414001810184439650[1] = 0.0;
   out_8414001810184439650[2] = 0.0;
   out_8414001810184439650[3] = 0.0;
   out_8414001810184439650[4] = 0.0;
   out_8414001810184439650[5] = 0.0;
   out_8414001810184439650[6] = 0.0;
   out_8414001810184439650[7] = 0.0;
   out_8414001810184439650[8] = 0.0;
   out_8414001810184439650[9] = 0.0;
   out_8414001810184439650[10] = 1.0;
   out_8414001810184439650[11] = 0.0;
   out_8414001810184439650[12] = 0.0;
   out_8414001810184439650[13] = 0.0;
   out_8414001810184439650[14] = 0.0;
   out_8414001810184439650[15] = 0.0;
   out_8414001810184439650[16] = 0.0;
   out_8414001810184439650[17] = 0.0;
   out_8414001810184439650[18] = 0.0;
   out_8414001810184439650[19] = 0.0;
   out_8414001810184439650[20] = 1.0;
   out_8414001810184439650[21] = 0.0;
   out_8414001810184439650[22] = 0.0;
   out_8414001810184439650[23] = 0.0;
   out_8414001810184439650[24] = 0.0;
   out_8414001810184439650[25] = 0.0;
   out_8414001810184439650[26] = 0.0;
   out_8414001810184439650[27] = 0.0;
   out_8414001810184439650[28] = 0.0;
   out_8414001810184439650[29] = 0.0;
   out_8414001810184439650[30] = 1.0;
   out_8414001810184439650[31] = 0.0;
   out_8414001810184439650[32] = 0.0;
   out_8414001810184439650[33] = 0.0;
   out_8414001810184439650[34] = 0.0;
   out_8414001810184439650[35] = 0.0;
   out_8414001810184439650[36] = 0.0;
   out_8414001810184439650[37] = 0.0;
   out_8414001810184439650[38] = 0.0;
   out_8414001810184439650[39] = 0.0;
   out_8414001810184439650[40] = 1.0;
   out_8414001810184439650[41] = 0.0;
   out_8414001810184439650[42] = 0.0;
   out_8414001810184439650[43] = 0.0;
   out_8414001810184439650[44] = 0.0;
   out_8414001810184439650[45] = 0.0;
   out_8414001810184439650[46] = 0.0;
   out_8414001810184439650[47] = 0.0;
   out_8414001810184439650[48] = 0.0;
   out_8414001810184439650[49] = 0.0;
   out_8414001810184439650[50] = 1.0;
   out_8414001810184439650[51] = 0.0;
   out_8414001810184439650[52] = 0.0;
   out_8414001810184439650[53] = 0.0;
   out_8414001810184439650[54] = 0.0;
   out_8414001810184439650[55] = 0.0;
   out_8414001810184439650[56] = 0.0;
   out_8414001810184439650[57] = 0.0;
   out_8414001810184439650[58] = 0.0;
   out_8414001810184439650[59] = 0.0;
   out_8414001810184439650[60] = 1.0;
   out_8414001810184439650[61] = 0.0;
   out_8414001810184439650[62] = 0.0;
   out_8414001810184439650[63] = 0.0;
   out_8414001810184439650[64] = 0.0;
   out_8414001810184439650[65] = 0.0;
   out_8414001810184439650[66] = 0.0;
   out_8414001810184439650[67] = 0.0;
   out_8414001810184439650[68] = 0.0;
   out_8414001810184439650[69] = 0.0;
   out_8414001810184439650[70] = 1.0;
   out_8414001810184439650[71] = 0.0;
   out_8414001810184439650[72] = 0.0;
   out_8414001810184439650[73] = 0.0;
   out_8414001810184439650[74] = 0.0;
   out_8414001810184439650[75] = 0.0;
   out_8414001810184439650[76] = 0.0;
   out_8414001810184439650[77] = 0.0;
   out_8414001810184439650[78] = 0.0;
   out_8414001810184439650[79] = 0.0;
   out_8414001810184439650[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_3948327662823114415) {
   out_3948327662823114415[0] = state[0];
   out_3948327662823114415[1] = state[1];
   out_3948327662823114415[2] = state[2];
   out_3948327662823114415[3] = state[3];
   out_3948327662823114415[4] = state[4];
   out_3948327662823114415[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8000000000000007*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_3948327662823114415[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_3948327662823114415[7] = state[7];
   out_3948327662823114415[8] = state[8];
}
void F_fun(double *state, double dt, double *out_3295329725115080623) {
   out_3295329725115080623[0] = 1;
   out_3295329725115080623[1] = 0;
   out_3295329725115080623[2] = 0;
   out_3295329725115080623[3] = 0;
   out_3295329725115080623[4] = 0;
   out_3295329725115080623[5] = 0;
   out_3295329725115080623[6] = 0;
   out_3295329725115080623[7] = 0;
   out_3295329725115080623[8] = 0;
   out_3295329725115080623[9] = 0;
   out_3295329725115080623[10] = 1;
   out_3295329725115080623[11] = 0;
   out_3295329725115080623[12] = 0;
   out_3295329725115080623[13] = 0;
   out_3295329725115080623[14] = 0;
   out_3295329725115080623[15] = 0;
   out_3295329725115080623[16] = 0;
   out_3295329725115080623[17] = 0;
   out_3295329725115080623[18] = 0;
   out_3295329725115080623[19] = 0;
   out_3295329725115080623[20] = 1;
   out_3295329725115080623[21] = 0;
   out_3295329725115080623[22] = 0;
   out_3295329725115080623[23] = 0;
   out_3295329725115080623[24] = 0;
   out_3295329725115080623[25] = 0;
   out_3295329725115080623[26] = 0;
   out_3295329725115080623[27] = 0;
   out_3295329725115080623[28] = 0;
   out_3295329725115080623[29] = 0;
   out_3295329725115080623[30] = 1;
   out_3295329725115080623[31] = 0;
   out_3295329725115080623[32] = 0;
   out_3295329725115080623[33] = 0;
   out_3295329725115080623[34] = 0;
   out_3295329725115080623[35] = 0;
   out_3295329725115080623[36] = 0;
   out_3295329725115080623[37] = 0;
   out_3295329725115080623[38] = 0;
   out_3295329725115080623[39] = 0;
   out_3295329725115080623[40] = 1;
   out_3295329725115080623[41] = 0;
   out_3295329725115080623[42] = 0;
   out_3295329725115080623[43] = 0;
   out_3295329725115080623[44] = 0;
   out_3295329725115080623[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_3295329725115080623[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_3295329725115080623[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_3295329725115080623[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_3295329725115080623[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_3295329725115080623[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_3295329725115080623[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_3295329725115080623[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_3295329725115080623[53] = -9.8000000000000007*dt;
   out_3295329725115080623[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_3295329725115080623[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_3295329725115080623[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_3295329725115080623[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_3295329725115080623[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_3295329725115080623[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_3295329725115080623[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_3295329725115080623[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_3295329725115080623[62] = 0;
   out_3295329725115080623[63] = 0;
   out_3295329725115080623[64] = 0;
   out_3295329725115080623[65] = 0;
   out_3295329725115080623[66] = 0;
   out_3295329725115080623[67] = 0;
   out_3295329725115080623[68] = 0;
   out_3295329725115080623[69] = 0;
   out_3295329725115080623[70] = 1;
   out_3295329725115080623[71] = 0;
   out_3295329725115080623[72] = 0;
   out_3295329725115080623[73] = 0;
   out_3295329725115080623[74] = 0;
   out_3295329725115080623[75] = 0;
   out_3295329725115080623[76] = 0;
   out_3295329725115080623[77] = 0;
   out_3295329725115080623[78] = 0;
   out_3295329725115080623[79] = 0;
   out_3295329725115080623[80] = 1;
}
void h_25(double *state, double *unused, double *out_2198496317441769050) {
   out_2198496317441769050[0] = state[6];
}
void H_25(double *state, double *unused, double *out_3510309984999774810) {
   out_3510309984999774810[0] = 0;
   out_3510309984999774810[1] = 0;
   out_3510309984999774810[2] = 0;
   out_3510309984999774810[3] = 0;
   out_3510309984999774810[4] = 0;
   out_3510309984999774810[5] = 0;
   out_3510309984999774810[6] = 1;
   out_3510309984999774810[7] = 0;
   out_3510309984999774810[8] = 0;
}
void h_24(double *state, double *unused, double *out_5882476347173498120) {
   out_5882476347173498120[0] = state[4];
   out_5882476347173498120[1] = state[5];
}
void H_24(double *state, double *unused, double *out_3906955289353634305) {
   out_3906955289353634305[0] = 0;
   out_3906955289353634305[1] = 0;
   out_3906955289353634305[2] = 0;
   out_3906955289353634305[3] = 0;
   out_3906955289353634305[4] = 1;
   out_3906955289353634305[5] = 0;
   out_3906955289353634305[6] = 0;
   out_3906955289353634305[7] = 0;
   out_3906955289353634305[8] = 0;
   out_3906955289353634305[9] = 0;
   out_3906955289353634305[10] = 0;
   out_3906955289353634305[11] = 0;
   out_3906955289353634305[12] = 0;
   out_3906955289353634305[13] = 0;
   out_3906955289353634305[14] = 1;
   out_3906955289353634305[15] = 0;
   out_3906955289353634305[16] = 0;
   out_3906955289353634305[17] = 0;
}
void h_30(double *state, double *unused, double *out_926942978867358) {
   out_926942978867358[0] = state[4];
}
void H_30(double *state, double *unused, double *out_991977026492526183) {
   out_991977026492526183[0] = 0;
   out_991977026492526183[1] = 0;
   out_991977026492526183[2] = 0;
   out_991977026492526183[3] = 0;
   out_991977026492526183[4] = 1;
   out_991977026492526183[5] = 0;
   out_991977026492526183[6] = 0;
   out_991977026492526183[7] = 0;
   out_991977026492526183[8] = 0;
}
void h_26(double *state, double *unused, double *out_7436070377407568171) {
   out_7436070377407568171[0] = state[7];
}
void H_26(double *state, double *unused, double *out_205784015238974209) {
   out_205784015238974209[0] = 0;
   out_205784015238974209[1] = 0;
   out_205784015238974209[2] = 0;
   out_205784015238974209[3] = 0;
   out_205784015238974209[4] = 0;
   out_205784015238974209[5] = 0;
   out_205784015238974209[6] = 0;
   out_205784015238974209[7] = 1;
   out_205784015238974209[8] = 0;
}
void h_27(double *state, double *unused, double *out_4804266386351296729) {
   out_4804266386351296729[0] = state[3];
}
void H_27(double *state, double *unused, double *out_3166740338292951094) {
   out_3166740338292951094[0] = 0;
   out_3166740338292951094[1] = 0;
   out_3166740338292951094[2] = 0;
   out_3166740338292951094[3] = 1;
   out_3166740338292951094[4] = 0;
   out_3166740338292951094[5] = 0;
   out_3166740338292951094[6] = 0;
   out_3166740338292951094[7] = 0;
   out_3166740338292951094[8] = 0;
}
void h_29(double *state, double *unused, double *out_942582909922795077) {
   out_942582909922795077[0] = state[1];
}
void H_29(double *state, double *unused, double *out_481745682178133999) {
   out_481745682178133999[0] = 0;
   out_481745682178133999[1] = 1;
   out_481745682178133999[2] = 0;
   out_481745682178133999[3] = 0;
   out_481745682178133999[4] = 0;
   out_481745682178133999[5] = 0;
   out_481745682178133999[6] = 0;
   out_481745682178133999[7] = 0;
   out_481745682178133999[8] = 0;
}
void h_28(double *state, double *unused, double *out_7616818489621150112) {
   out_7616818489621150112[0] = state[0];
}
void H_28(double *state, double *unused, double *out_5564144699247664573) {
   out_5564144699247664573[0] = 1;
   out_5564144699247664573[1] = 0;
   out_5564144699247664573[2] = 0;
   out_5564144699247664573[3] = 0;
   out_5564144699247664573[4] = 0;
   out_5564144699247664573[5] = 0;
   out_5564144699247664573[6] = 0;
   out_5564144699247664573[7] = 0;
   out_5564144699247664573[8] = 0;
}
void h_31(double *state, double *unused, double *out_8365610357412903353) {
   out_8365610357412903353[0] = state[8];
}
void H_31(double *state, double *unused, double *out_831992117472325685) {
   out_831992117472325685[0] = 0;
   out_831992117472325685[1] = 0;
   out_831992117472325685[2] = 0;
   out_831992117472325685[3] = 0;
   out_831992117472325685[4] = 0;
   out_831992117472325685[5] = 0;
   out_831992117472325685[6] = 0;
   out_831992117472325685[7] = 0;
   out_831992117472325685[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_1648004092401022955) {
  err_fun(nom_x, delta_x, out_1648004092401022955);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_8224224676727042815) {
  inv_err_fun(nom_x, true_x, out_8224224676727042815);
}
void car_H_mod_fun(double *state, double *out_8414001810184439650) {
  H_mod_fun(state, out_8414001810184439650);
}
void car_f_fun(double *state, double dt, double *out_3948327662823114415) {
  f_fun(state,  dt, out_3948327662823114415);
}
void car_F_fun(double *state, double dt, double *out_3295329725115080623) {
  F_fun(state,  dt, out_3295329725115080623);
}
void car_h_25(double *state, double *unused, double *out_2198496317441769050) {
  h_25(state, unused, out_2198496317441769050);
}
void car_H_25(double *state, double *unused, double *out_3510309984999774810) {
  H_25(state, unused, out_3510309984999774810);
}
void car_h_24(double *state, double *unused, double *out_5882476347173498120) {
  h_24(state, unused, out_5882476347173498120);
}
void car_H_24(double *state, double *unused, double *out_3906955289353634305) {
  H_24(state, unused, out_3906955289353634305);
}
void car_h_30(double *state, double *unused, double *out_926942978867358) {
  h_30(state, unused, out_926942978867358);
}
void car_H_30(double *state, double *unused, double *out_991977026492526183) {
  H_30(state, unused, out_991977026492526183);
}
void car_h_26(double *state, double *unused, double *out_7436070377407568171) {
  h_26(state, unused, out_7436070377407568171);
}
void car_H_26(double *state, double *unused, double *out_205784015238974209) {
  H_26(state, unused, out_205784015238974209);
}
void car_h_27(double *state, double *unused, double *out_4804266386351296729) {
  h_27(state, unused, out_4804266386351296729);
}
void car_H_27(double *state, double *unused, double *out_3166740338292951094) {
  H_27(state, unused, out_3166740338292951094);
}
void car_h_29(double *state, double *unused, double *out_942582909922795077) {
  h_29(state, unused, out_942582909922795077);
}
void car_H_29(double *state, double *unused, double *out_481745682178133999) {
  H_29(state, unused, out_481745682178133999);
}
void car_h_28(double *state, double *unused, double *out_7616818489621150112) {
  h_28(state, unused, out_7616818489621150112);
}
void car_H_28(double *state, double *unused, double *out_5564144699247664573) {
  H_28(state, unused, out_5564144699247664573);
}
void car_h_31(double *state, double *unused, double *out_8365610357412903353) {
  h_31(state, unused, out_8365610357412903353);
}
void car_H_31(double *state, double *unused, double *out_831992117472325685) {
  H_31(state, unused, out_831992117472325685);
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
