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
void err_fun(double *nom_x, double *delta_x, double *out_4489976497373888968) {
   out_4489976497373888968[0] = delta_x[0] + nom_x[0];
   out_4489976497373888968[1] = delta_x[1] + nom_x[1];
   out_4489976497373888968[2] = delta_x[2] + nom_x[2];
   out_4489976497373888968[3] = delta_x[3] + nom_x[3];
   out_4489976497373888968[4] = delta_x[4] + nom_x[4];
   out_4489976497373888968[5] = delta_x[5] + nom_x[5];
   out_4489976497373888968[6] = delta_x[6] + nom_x[6];
   out_4489976497373888968[7] = delta_x[7] + nom_x[7];
   out_4489976497373888968[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_7372567849217778160) {
   out_7372567849217778160[0] = -nom_x[0] + true_x[0];
   out_7372567849217778160[1] = -nom_x[1] + true_x[1];
   out_7372567849217778160[2] = -nom_x[2] + true_x[2];
   out_7372567849217778160[3] = -nom_x[3] + true_x[3];
   out_7372567849217778160[4] = -nom_x[4] + true_x[4];
   out_7372567849217778160[5] = -nom_x[5] + true_x[5];
   out_7372567849217778160[6] = -nom_x[6] + true_x[6];
   out_7372567849217778160[7] = -nom_x[7] + true_x[7];
   out_7372567849217778160[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_6447089845340017966) {
   out_6447089845340017966[0] = 1.0;
   out_6447089845340017966[1] = 0.0;
   out_6447089845340017966[2] = 0.0;
   out_6447089845340017966[3] = 0.0;
   out_6447089845340017966[4] = 0.0;
   out_6447089845340017966[5] = 0.0;
   out_6447089845340017966[6] = 0.0;
   out_6447089845340017966[7] = 0.0;
   out_6447089845340017966[8] = 0.0;
   out_6447089845340017966[9] = 0.0;
   out_6447089845340017966[10] = 1.0;
   out_6447089845340017966[11] = 0.0;
   out_6447089845340017966[12] = 0.0;
   out_6447089845340017966[13] = 0.0;
   out_6447089845340017966[14] = 0.0;
   out_6447089845340017966[15] = 0.0;
   out_6447089845340017966[16] = 0.0;
   out_6447089845340017966[17] = 0.0;
   out_6447089845340017966[18] = 0.0;
   out_6447089845340017966[19] = 0.0;
   out_6447089845340017966[20] = 1.0;
   out_6447089845340017966[21] = 0.0;
   out_6447089845340017966[22] = 0.0;
   out_6447089845340017966[23] = 0.0;
   out_6447089845340017966[24] = 0.0;
   out_6447089845340017966[25] = 0.0;
   out_6447089845340017966[26] = 0.0;
   out_6447089845340017966[27] = 0.0;
   out_6447089845340017966[28] = 0.0;
   out_6447089845340017966[29] = 0.0;
   out_6447089845340017966[30] = 1.0;
   out_6447089845340017966[31] = 0.0;
   out_6447089845340017966[32] = 0.0;
   out_6447089845340017966[33] = 0.0;
   out_6447089845340017966[34] = 0.0;
   out_6447089845340017966[35] = 0.0;
   out_6447089845340017966[36] = 0.0;
   out_6447089845340017966[37] = 0.0;
   out_6447089845340017966[38] = 0.0;
   out_6447089845340017966[39] = 0.0;
   out_6447089845340017966[40] = 1.0;
   out_6447089845340017966[41] = 0.0;
   out_6447089845340017966[42] = 0.0;
   out_6447089845340017966[43] = 0.0;
   out_6447089845340017966[44] = 0.0;
   out_6447089845340017966[45] = 0.0;
   out_6447089845340017966[46] = 0.0;
   out_6447089845340017966[47] = 0.0;
   out_6447089845340017966[48] = 0.0;
   out_6447089845340017966[49] = 0.0;
   out_6447089845340017966[50] = 1.0;
   out_6447089845340017966[51] = 0.0;
   out_6447089845340017966[52] = 0.0;
   out_6447089845340017966[53] = 0.0;
   out_6447089845340017966[54] = 0.0;
   out_6447089845340017966[55] = 0.0;
   out_6447089845340017966[56] = 0.0;
   out_6447089845340017966[57] = 0.0;
   out_6447089845340017966[58] = 0.0;
   out_6447089845340017966[59] = 0.0;
   out_6447089845340017966[60] = 1.0;
   out_6447089845340017966[61] = 0.0;
   out_6447089845340017966[62] = 0.0;
   out_6447089845340017966[63] = 0.0;
   out_6447089845340017966[64] = 0.0;
   out_6447089845340017966[65] = 0.0;
   out_6447089845340017966[66] = 0.0;
   out_6447089845340017966[67] = 0.0;
   out_6447089845340017966[68] = 0.0;
   out_6447089845340017966[69] = 0.0;
   out_6447089845340017966[70] = 1.0;
   out_6447089845340017966[71] = 0.0;
   out_6447089845340017966[72] = 0.0;
   out_6447089845340017966[73] = 0.0;
   out_6447089845340017966[74] = 0.0;
   out_6447089845340017966[75] = 0.0;
   out_6447089845340017966[76] = 0.0;
   out_6447089845340017966[77] = 0.0;
   out_6447089845340017966[78] = 0.0;
   out_6447089845340017966[79] = 0.0;
   out_6447089845340017966[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_2240279400731128408) {
   out_2240279400731128408[0] = state[0];
   out_2240279400731128408[1] = state[1];
   out_2240279400731128408[2] = state[2];
   out_2240279400731128408[3] = state[3];
   out_2240279400731128408[4] = state[4];
   out_2240279400731128408[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8000000000000007*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_2240279400731128408[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_2240279400731128408[7] = state[7];
   out_2240279400731128408[8] = state[8];
}
void F_fun(double *state, double dt, double *out_1078793132522145231) {
   out_1078793132522145231[0] = 1;
   out_1078793132522145231[1] = 0;
   out_1078793132522145231[2] = 0;
   out_1078793132522145231[3] = 0;
   out_1078793132522145231[4] = 0;
   out_1078793132522145231[5] = 0;
   out_1078793132522145231[6] = 0;
   out_1078793132522145231[7] = 0;
   out_1078793132522145231[8] = 0;
   out_1078793132522145231[9] = 0;
   out_1078793132522145231[10] = 1;
   out_1078793132522145231[11] = 0;
   out_1078793132522145231[12] = 0;
   out_1078793132522145231[13] = 0;
   out_1078793132522145231[14] = 0;
   out_1078793132522145231[15] = 0;
   out_1078793132522145231[16] = 0;
   out_1078793132522145231[17] = 0;
   out_1078793132522145231[18] = 0;
   out_1078793132522145231[19] = 0;
   out_1078793132522145231[20] = 1;
   out_1078793132522145231[21] = 0;
   out_1078793132522145231[22] = 0;
   out_1078793132522145231[23] = 0;
   out_1078793132522145231[24] = 0;
   out_1078793132522145231[25] = 0;
   out_1078793132522145231[26] = 0;
   out_1078793132522145231[27] = 0;
   out_1078793132522145231[28] = 0;
   out_1078793132522145231[29] = 0;
   out_1078793132522145231[30] = 1;
   out_1078793132522145231[31] = 0;
   out_1078793132522145231[32] = 0;
   out_1078793132522145231[33] = 0;
   out_1078793132522145231[34] = 0;
   out_1078793132522145231[35] = 0;
   out_1078793132522145231[36] = 0;
   out_1078793132522145231[37] = 0;
   out_1078793132522145231[38] = 0;
   out_1078793132522145231[39] = 0;
   out_1078793132522145231[40] = 1;
   out_1078793132522145231[41] = 0;
   out_1078793132522145231[42] = 0;
   out_1078793132522145231[43] = 0;
   out_1078793132522145231[44] = 0;
   out_1078793132522145231[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_1078793132522145231[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_1078793132522145231[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_1078793132522145231[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_1078793132522145231[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_1078793132522145231[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_1078793132522145231[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_1078793132522145231[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_1078793132522145231[53] = -9.8000000000000007*dt;
   out_1078793132522145231[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_1078793132522145231[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_1078793132522145231[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_1078793132522145231[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_1078793132522145231[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_1078793132522145231[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_1078793132522145231[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_1078793132522145231[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_1078793132522145231[62] = 0;
   out_1078793132522145231[63] = 0;
   out_1078793132522145231[64] = 0;
   out_1078793132522145231[65] = 0;
   out_1078793132522145231[66] = 0;
   out_1078793132522145231[67] = 0;
   out_1078793132522145231[68] = 0;
   out_1078793132522145231[69] = 0;
   out_1078793132522145231[70] = 1;
   out_1078793132522145231[71] = 0;
   out_1078793132522145231[72] = 0;
   out_1078793132522145231[73] = 0;
   out_1078793132522145231[74] = 0;
   out_1078793132522145231[75] = 0;
   out_1078793132522145231[76] = 0;
   out_1078793132522145231[77] = 0;
   out_1078793132522145231[78] = 0;
   out_1078793132522145231[79] = 0;
   out_1078793132522145231[80] = 1;
}
void h_25(double *state, double *unused, double *out_1533821598204291139) {
   out_1533821598204291139[0] = state[6];
}
void H_25(double *state, double *unused, double *out_1543398020155353126) {
   out_1543398020155353126[0] = 0;
   out_1543398020155353126[1] = 0;
   out_1543398020155353126[2] = 0;
   out_1543398020155353126[3] = 0;
   out_1543398020155353126[4] = 0;
   out_1543398020155353126[5] = 0;
   out_1543398020155353126[6] = 1;
   out_1543398020155353126[7] = 0;
   out_1543398020155353126[8] = 0;
}
void h_24(double *state, double *unused, double *out_715741241444623657) {
   out_715741241444623657[0] = state[4];
   out_715741241444623657[1] = state[5];
}
void H_24(double *state, double *unused, double *out_5525721171553121024) {
   out_5525721171553121024[0] = 0;
   out_5525721171553121024[1] = 0;
   out_5525721171553121024[2] = 0;
   out_5525721171553121024[3] = 0;
   out_5525721171553121024[4] = 1;
   out_5525721171553121024[5] = 0;
   out_5525721171553121024[6] = 0;
   out_5525721171553121024[7] = 0;
   out_5525721171553121024[8] = 0;
   out_5525721171553121024[9] = 0;
   out_5525721171553121024[10] = 0;
   out_5525721171553121024[11] = 0;
   out_5525721171553121024[12] = 0;
   out_5525721171553121024[13] = 0;
   out_5525721171553121024[14] = 1;
   out_5525721171553121024[15] = 0;
   out_5525721171553121024[16] = 0;
   out_5525721171553121024[17] = 0;
}
void h_30(double *state, double *unused, double *out_5632124896483663003) {
   out_5632124896483663003[0] = state[4];
}
void H_30(double *state, double *unused, double *out_974934938351895501) {
   out_974934938351895501[0] = 0;
   out_974934938351895501[1] = 0;
   out_974934938351895501[2] = 0;
   out_974934938351895501[3] = 0;
   out_974934938351895501[4] = 1;
   out_974934938351895501[5] = 0;
   out_974934938351895501[6] = 0;
   out_974934938351895501[7] = 0;
   out_974934938351895501[8] = 0;
}
void h_26(double *state, double *unused, double *out_7812945909565042968) {
   out_7812945909565042968[0] = state[7];
}
void H_26(double *state, double *unused, double *out_1761127949605447475) {
   out_1761127949605447475[0] = 0;
   out_1761127949605447475[1] = 0;
   out_1761127949605447475[2] = 0;
   out_1761127949605447475[3] = 0;
   out_1761127949605447475[4] = 0;
   out_1761127949605447475[5] = 0;
   out_1761127949605447475[6] = 0;
   out_1761127949605447475[7] = 1;
   out_1761127949605447475[8] = 0;
}
void h_27(double *state, double *unused, double *out_7930953303498419712) {
   out_7930953303498419712[0] = state[3];
}
void H_27(double *state, double *unused, double *out_3198529009535838718) {
   out_3198529009535838718[0] = 0;
   out_3198529009535838718[1] = 0;
   out_3198529009535838718[2] = 0;
   out_3198529009535838718[3] = 1;
   out_3198529009535838718[4] = 0;
   out_3198529009535838718[5] = 0;
   out_3198529009535838718[6] = 0;
   out_3198529009535838718[7] = 0;
   out_3198529009535838718[8] = 0;
}
void h_29(double *state, double *unused, double *out_1160118077148068776) {
   out_1160118077148068776[0] = state[1];
}
void H_29(double *state, double *unused, double *out_1485166282666287685) {
   out_1485166282666287685[0] = 0;
   out_1485166282666287685[1] = 1;
   out_1485166282666287685[2] = 0;
   out_1485166282666287685[3] = 0;
   out_1485166282666287685[4] = 0;
   out_1485166282666287685[5] = 0;
   out_1485166282666287685[6] = 0;
   out_1485166282666287685[7] = 0;
   out_1485166282666287685[8] = 0;
}
void h_28(double *state, double *unused, double *out_5514117502550286259) {
   out_5514117502550286259[0] = state[0];
}
void H_28(double *state, double *unused, double *out_3597232734403242889) {
   out_3597232734403242889[0] = 1;
   out_3597232734403242889[1] = 0;
   out_3597232734403242889[2] = 0;
   out_3597232734403242889[3] = 0;
   out_3597232734403242889[4] = 0;
   out_3597232734403242889[5] = 0;
   out_3597232734403242889[6] = 0;
   out_3597232734403242889[7] = 0;
   out_3597232734403242889[8] = 0;
}
void h_31(double *state, double *unused, double *out_932403440590927585) {
   out_932403440590927585[0] = state[8];
}
void H_31(double *state, double *unused, double *out_1134919847372095999) {
   out_1134919847372095999[0] = 0;
   out_1134919847372095999[1] = 0;
   out_1134919847372095999[2] = 0;
   out_1134919847372095999[3] = 0;
   out_1134919847372095999[4] = 0;
   out_1134919847372095999[5] = 0;
   out_1134919847372095999[6] = 0;
   out_1134919847372095999[7] = 0;
   out_1134919847372095999[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_4489976497373888968) {
  err_fun(nom_x, delta_x, out_4489976497373888968);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_7372567849217778160) {
  inv_err_fun(nom_x, true_x, out_7372567849217778160);
}
void car_H_mod_fun(double *state, double *out_6447089845340017966) {
  H_mod_fun(state, out_6447089845340017966);
}
void car_f_fun(double *state, double dt, double *out_2240279400731128408) {
  f_fun(state,  dt, out_2240279400731128408);
}
void car_F_fun(double *state, double dt, double *out_1078793132522145231) {
  F_fun(state,  dt, out_1078793132522145231);
}
void car_h_25(double *state, double *unused, double *out_1533821598204291139) {
  h_25(state, unused, out_1533821598204291139);
}
void car_H_25(double *state, double *unused, double *out_1543398020155353126) {
  H_25(state, unused, out_1543398020155353126);
}
void car_h_24(double *state, double *unused, double *out_715741241444623657) {
  h_24(state, unused, out_715741241444623657);
}
void car_H_24(double *state, double *unused, double *out_5525721171553121024) {
  H_24(state, unused, out_5525721171553121024);
}
void car_h_30(double *state, double *unused, double *out_5632124896483663003) {
  h_30(state, unused, out_5632124896483663003);
}
void car_H_30(double *state, double *unused, double *out_974934938351895501) {
  H_30(state, unused, out_974934938351895501);
}
void car_h_26(double *state, double *unused, double *out_7812945909565042968) {
  h_26(state, unused, out_7812945909565042968);
}
void car_H_26(double *state, double *unused, double *out_1761127949605447475) {
  H_26(state, unused, out_1761127949605447475);
}
void car_h_27(double *state, double *unused, double *out_7930953303498419712) {
  h_27(state, unused, out_7930953303498419712);
}
void car_H_27(double *state, double *unused, double *out_3198529009535838718) {
  H_27(state, unused, out_3198529009535838718);
}
void car_h_29(double *state, double *unused, double *out_1160118077148068776) {
  h_29(state, unused, out_1160118077148068776);
}
void car_H_29(double *state, double *unused, double *out_1485166282666287685) {
  H_29(state, unused, out_1485166282666287685);
}
void car_h_28(double *state, double *unused, double *out_5514117502550286259) {
  h_28(state, unused, out_5514117502550286259);
}
void car_H_28(double *state, double *unused, double *out_3597232734403242889) {
  H_28(state, unused, out_3597232734403242889);
}
void car_h_31(double *state, double *unused, double *out_932403440590927585) {
  h_31(state, unused, out_932403440590927585);
}
void car_H_31(double *state, double *unused, double *out_1134919847372095999) {
  H_31(state, unused, out_1134919847372095999);
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
