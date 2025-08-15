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
void err_fun(double *nom_x, double *delta_x, double *out_974266586704450606) {
   out_974266586704450606[0] = delta_x[0] + nom_x[0];
   out_974266586704450606[1] = delta_x[1] + nom_x[1];
   out_974266586704450606[2] = delta_x[2] + nom_x[2];
   out_974266586704450606[3] = delta_x[3] + nom_x[3];
   out_974266586704450606[4] = delta_x[4] + nom_x[4];
   out_974266586704450606[5] = delta_x[5] + nom_x[5];
   out_974266586704450606[6] = delta_x[6] + nom_x[6];
   out_974266586704450606[7] = delta_x[7] + nom_x[7];
   out_974266586704450606[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_5405916937632846827) {
   out_5405916937632846827[0] = -nom_x[0] + true_x[0];
   out_5405916937632846827[1] = -nom_x[1] + true_x[1];
   out_5405916937632846827[2] = -nom_x[2] + true_x[2];
   out_5405916937632846827[3] = -nom_x[3] + true_x[3];
   out_5405916937632846827[4] = -nom_x[4] + true_x[4];
   out_5405916937632846827[5] = -nom_x[5] + true_x[5];
   out_5405916937632846827[6] = -nom_x[6] + true_x[6];
   out_5405916937632846827[7] = -nom_x[7] + true_x[7];
   out_5405916937632846827[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_1988421079300520544) {
   out_1988421079300520544[0] = 1.0;
   out_1988421079300520544[1] = 0.0;
   out_1988421079300520544[2] = 0.0;
   out_1988421079300520544[3] = 0.0;
   out_1988421079300520544[4] = 0.0;
   out_1988421079300520544[5] = 0.0;
   out_1988421079300520544[6] = 0.0;
   out_1988421079300520544[7] = 0.0;
   out_1988421079300520544[8] = 0.0;
   out_1988421079300520544[9] = 0.0;
   out_1988421079300520544[10] = 1.0;
   out_1988421079300520544[11] = 0.0;
   out_1988421079300520544[12] = 0.0;
   out_1988421079300520544[13] = 0.0;
   out_1988421079300520544[14] = 0.0;
   out_1988421079300520544[15] = 0.0;
   out_1988421079300520544[16] = 0.0;
   out_1988421079300520544[17] = 0.0;
   out_1988421079300520544[18] = 0.0;
   out_1988421079300520544[19] = 0.0;
   out_1988421079300520544[20] = 1.0;
   out_1988421079300520544[21] = 0.0;
   out_1988421079300520544[22] = 0.0;
   out_1988421079300520544[23] = 0.0;
   out_1988421079300520544[24] = 0.0;
   out_1988421079300520544[25] = 0.0;
   out_1988421079300520544[26] = 0.0;
   out_1988421079300520544[27] = 0.0;
   out_1988421079300520544[28] = 0.0;
   out_1988421079300520544[29] = 0.0;
   out_1988421079300520544[30] = 1.0;
   out_1988421079300520544[31] = 0.0;
   out_1988421079300520544[32] = 0.0;
   out_1988421079300520544[33] = 0.0;
   out_1988421079300520544[34] = 0.0;
   out_1988421079300520544[35] = 0.0;
   out_1988421079300520544[36] = 0.0;
   out_1988421079300520544[37] = 0.0;
   out_1988421079300520544[38] = 0.0;
   out_1988421079300520544[39] = 0.0;
   out_1988421079300520544[40] = 1.0;
   out_1988421079300520544[41] = 0.0;
   out_1988421079300520544[42] = 0.0;
   out_1988421079300520544[43] = 0.0;
   out_1988421079300520544[44] = 0.0;
   out_1988421079300520544[45] = 0.0;
   out_1988421079300520544[46] = 0.0;
   out_1988421079300520544[47] = 0.0;
   out_1988421079300520544[48] = 0.0;
   out_1988421079300520544[49] = 0.0;
   out_1988421079300520544[50] = 1.0;
   out_1988421079300520544[51] = 0.0;
   out_1988421079300520544[52] = 0.0;
   out_1988421079300520544[53] = 0.0;
   out_1988421079300520544[54] = 0.0;
   out_1988421079300520544[55] = 0.0;
   out_1988421079300520544[56] = 0.0;
   out_1988421079300520544[57] = 0.0;
   out_1988421079300520544[58] = 0.0;
   out_1988421079300520544[59] = 0.0;
   out_1988421079300520544[60] = 1.0;
   out_1988421079300520544[61] = 0.0;
   out_1988421079300520544[62] = 0.0;
   out_1988421079300520544[63] = 0.0;
   out_1988421079300520544[64] = 0.0;
   out_1988421079300520544[65] = 0.0;
   out_1988421079300520544[66] = 0.0;
   out_1988421079300520544[67] = 0.0;
   out_1988421079300520544[68] = 0.0;
   out_1988421079300520544[69] = 0.0;
   out_1988421079300520544[70] = 1.0;
   out_1988421079300520544[71] = 0.0;
   out_1988421079300520544[72] = 0.0;
   out_1988421079300520544[73] = 0.0;
   out_1988421079300520544[74] = 0.0;
   out_1988421079300520544[75] = 0.0;
   out_1988421079300520544[76] = 0.0;
   out_1988421079300520544[77] = 0.0;
   out_1988421079300520544[78] = 0.0;
   out_1988421079300520544[79] = 0.0;
   out_1988421079300520544[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_3725388884411746145) {
   out_3725388884411746145[0] = state[0];
   out_3725388884411746145[1] = state[1];
   out_3725388884411746145[2] = state[2];
   out_3725388884411746145[3] = state[3];
   out_3725388884411746145[4] = state[4];
   out_3725388884411746145[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8100000000000005*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_3725388884411746145[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_3725388884411746145[7] = state[7];
   out_3725388884411746145[8] = state[8];
}
void F_fun(double *state, double dt, double *out_2674620274016128632) {
   out_2674620274016128632[0] = 1;
   out_2674620274016128632[1] = 0;
   out_2674620274016128632[2] = 0;
   out_2674620274016128632[3] = 0;
   out_2674620274016128632[4] = 0;
   out_2674620274016128632[5] = 0;
   out_2674620274016128632[6] = 0;
   out_2674620274016128632[7] = 0;
   out_2674620274016128632[8] = 0;
   out_2674620274016128632[9] = 0;
   out_2674620274016128632[10] = 1;
   out_2674620274016128632[11] = 0;
   out_2674620274016128632[12] = 0;
   out_2674620274016128632[13] = 0;
   out_2674620274016128632[14] = 0;
   out_2674620274016128632[15] = 0;
   out_2674620274016128632[16] = 0;
   out_2674620274016128632[17] = 0;
   out_2674620274016128632[18] = 0;
   out_2674620274016128632[19] = 0;
   out_2674620274016128632[20] = 1;
   out_2674620274016128632[21] = 0;
   out_2674620274016128632[22] = 0;
   out_2674620274016128632[23] = 0;
   out_2674620274016128632[24] = 0;
   out_2674620274016128632[25] = 0;
   out_2674620274016128632[26] = 0;
   out_2674620274016128632[27] = 0;
   out_2674620274016128632[28] = 0;
   out_2674620274016128632[29] = 0;
   out_2674620274016128632[30] = 1;
   out_2674620274016128632[31] = 0;
   out_2674620274016128632[32] = 0;
   out_2674620274016128632[33] = 0;
   out_2674620274016128632[34] = 0;
   out_2674620274016128632[35] = 0;
   out_2674620274016128632[36] = 0;
   out_2674620274016128632[37] = 0;
   out_2674620274016128632[38] = 0;
   out_2674620274016128632[39] = 0;
   out_2674620274016128632[40] = 1;
   out_2674620274016128632[41] = 0;
   out_2674620274016128632[42] = 0;
   out_2674620274016128632[43] = 0;
   out_2674620274016128632[44] = 0;
   out_2674620274016128632[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_2674620274016128632[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_2674620274016128632[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_2674620274016128632[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_2674620274016128632[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_2674620274016128632[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_2674620274016128632[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_2674620274016128632[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_2674620274016128632[53] = -9.8100000000000005*dt;
   out_2674620274016128632[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_2674620274016128632[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_2674620274016128632[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_2674620274016128632[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_2674620274016128632[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_2674620274016128632[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_2674620274016128632[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_2674620274016128632[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_2674620274016128632[62] = 0;
   out_2674620274016128632[63] = 0;
   out_2674620274016128632[64] = 0;
   out_2674620274016128632[65] = 0;
   out_2674620274016128632[66] = 0;
   out_2674620274016128632[67] = 0;
   out_2674620274016128632[68] = 0;
   out_2674620274016128632[69] = 0;
   out_2674620274016128632[70] = 1;
   out_2674620274016128632[71] = 0;
   out_2674620274016128632[72] = 0;
   out_2674620274016128632[73] = 0;
   out_2674620274016128632[74] = 0;
   out_2674620274016128632[75] = 0;
   out_2674620274016128632[76] = 0;
   out_2674620274016128632[77] = 0;
   out_2674620274016128632[78] = 0;
   out_2674620274016128632[79] = 0;
   out_2674620274016128632[80] = 1;
}
void h_25(double *state, double *unused, double *out_5158729862070967329) {
   out_5158729862070967329[0] = state[6];
}
void H_25(double *state, double *unused, double *out_1534559570688971133) {
   out_1534559570688971133[0] = 0;
   out_1534559570688971133[1] = 0;
   out_1534559570688971133[2] = 0;
   out_1534559570688971133[3] = 0;
   out_1534559570688971133[4] = 0;
   out_1534559570688971133[5] = 0;
   out_1534559570688971133[6] = 1;
   out_1534559570688971133[7] = 0;
   out_1534559570688971133[8] = 0;
}
void h_24(double *state, double *unused, double *out_3236043973782204970) {
   out_3236043973782204970[0] = state[4];
   out_3236043973782204970[1] = state[5];
}
void H_24(double *state, double *unused, double *out_5092485169491294269) {
   out_5092485169491294269[0] = 0;
   out_5092485169491294269[1] = 0;
   out_5092485169491294269[2] = 0;
   out_5092485169491294269[3] = 0;
   out_5092485169491294269[4] = 1;
   out_5092485169491294269[5] = 0;
   out_5092485169491294269[6] = 0;
   out_5092485169491294269[7] = 0;
   out_5092485169491294269[8] = 0;
   out_5092485169491294269[9] = 0;
   out_5092485169491294269[10] = 0;
   out_5092485169491294269[11] = 0;
   out_5092485169491294269[12] = 0;
   out_5092485169491294269[13] = 0;
   out_5092485169491294269[14] = 1;
   out_5092485169491294269[15] = 0;
   out_5092485169491294269[16] = 0;
   out_5092485169491294269[17] = 0;
}
void h_30(double *state, double *unused, double *out_1218573841245160863) {
   out_1218573841245160863[0] = state[4];
}
void H_30(double *state, double *unused, double *out_2993136759438637065) {
   out_2993136759438637065[0] = 0;
   out_2993136759438637065[1] = 0;
   out_2993136759438637065[2] = 0;
   out_2993136759438637065[3] = 0;
   out_2993136759438637065[4] = 1;
   out_2993136759438637065[5] = 0;
   out_2993136759438637065[6] = 0;
   out_2993136759438637065[7] = 0;
   out_2993136759438637065[8] = 0;
}
void h_26(double *state, double *unused, double *out_8431860768198393613) {
   out_8431860768198393613[0] = state[7];
}
void H_26(double *state, double *unused, double *out_2206943748185085091) {
   out_2206943748185085091[0] = 0;
   out_2206943748185085091[1] = 0;
   out_2206943748185085091[2] = 0;
   out_2206943748185085091[3] = 0;
   out_2206943748185085091[4] = 0;
   out_2206943748185085091[5] = 0;
   out_2206943748185085091[6] = 0;
   out_2206943748185085091[7] = 1;
   out_2206943748185085091[8] = 0;
}
void h_27(double *state, double *unused, double *out_6102239714972629764) {
   out_6102239714972629764[0] = state[3];
}
void H_27(double *state, double *unused, double *out_769542688254693848) {
   out_769542688254693848[0] = 0;
   out_769542688254693848[1] = 0;
   out_769542688254693848[2] = 0;
   out_769542688254693848[3] = 1;
   out_769542688254693848[4] = 0;
   out_769542688254693848[5] = 0;
   out_769542688254693848[6] = 0;
   out_769542688254693848[7] = 0;
   out_769542688254693848[8] = 0;
}
void h_29(double *state, double *unused, double *out_7617615358659010009) {
   out_7617615358659010009[0] = state[1];
}
void H_29(double *state, double *unused, double *out_2482905415124244881) {
   out_2482905415124244881[0] = 0;
   out_2482905415124244881[1] = 1;
   out_2482905415124244881[2] = 0;
   out_2482905415124244881[3] = 0;
   out_2482905415124244881[4] = 0;
   out_2482905415124244881[5] = 0;
   out_2482905415124244881[6] = 0;
   out_2482905415124244881[7] = 0;
   out_2482905415124244881[8] = 0;
}
void h_28(double *state, double *unused, double *out_1100566447311784119) {
   out_1100566447311784119[0] = state[0];
}
void H_28(double *state, double *unused, double *out_519275143558918630) {
   out_519275143558918630[0] = 1;
   out_519275143558918630[1] = 0;
   out_519275143558918630[2] = 0;
   out_519275143558918630[3] = 0;
   out_519275143558918630[4] = 0;
   out_519275143558918630[5] = 0;
   out_519275143558918630[6] = 0;
   out_519275143558918630[7] = 0;
   out_519275143558918630[8] = 0;
}
void h_31(double *state, double *unused, double *out_2604535394749705112) {
   out_2604535394749705112[0] = state[8];
}
void H_31(double *state, double *unused, double *out_1565205532565931561) {
   out_1565205532565931561[0] = 0;
   out_1565205532565931561[1] = 0;
   out_1565205532565931561[2] = 0;
   out_1565205532565931561[3] = 0;
   out_1565205532565931561[4] = 0;
   out_1565205532565931561[5] = 0;
   out_1565205532565931561[6] = 0;
   out_1565205532565931561[7] = 0;
   out_1565205532565931561[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_974266586704450606) {
  err_fun(nom_x, delta_x, out_974266586704450606);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_5405916937632846827) {
  inv_err_fun(nom_x, true_x, out_5405916937632846827);
}
void car_H_mod_fun(double *state, double *out_1988421079300520544) {
  H_mod_fun(state, out_1988421079300520544);
}
void car_f_fun(double *state, double dt, double *out_3725388884411746145) {
  f_fun(state,  dt, out_3725388884411746145);
}
void car_F_fun(double *state, double dt, double *out_2674620274016128632) {
  F_fun(state,  dt, out_2674620274016128632);
}
void car_h_25(double *state, double *unused, double *out_5158729862070967329) {
  h_25(state, unused, out_5158729862070967329);
}
void car_H_25(double *state, double *unused, double *out_1534559570688971133) {
  H_25(state, unused, out_1534559570688971133);
}
void car_h_24(double *state, double *unused, double *out_3236043973782204970) {
  h_24(state, unused, out_3236043973782204970);
}
void car_H_24(double *state, double *unused, double *out_5092485169491294269) {
  H_24(state, unused, out_5092485169491294269);
}
void car_h_30(double *state, double *unused, double *out_1218573841245160863) {
  h_30(state, unused, out_1218573841245160863);
}
void car_H_30(double *state, double *unused, double *out_2993136759438637065) {
  H_30(state, unused, out_2993136759438637065);
}
void car_h_26(double *state, double *unused, double *out_8431860768198393613) {
  h_26(state, unused, out_8431860768198393613);
}
void car_H_26(double *state, double *unused, double *out_2206943748185085091) {
  H_26(state, unused, out_2206943748185085091);
}
void car_h_27(double *state, double *unused, double *out_6102239714972629764) {
  h_27(state, unused, out_6102239714972629764);
}
void car_H_27(double *state, double *unused, double *out_769542688254693848) {
  H_27(state, unused, out_769542688254693848);
}
void car_h_29(double *state, double *unused, double *out_7617615358659010009) {
  h_29(state, unused, out_7617615358659010009);
}
void car_H_29(double *state, double *unused, double *out_2482905415124244881) {
  H_29(state, unused, out_2482905415124244881);
}
void car_h_28(double *state, double *unused, double *out_1100566447311784119) {
  h_28(state, unused, out_1100566447311784119);
}
void car_H_28(double *state, double *unused, double *out_519275143558918630) {
  H_28(state, unused, out_519275143558918630);
}
void car_h_31(double *state, double *unused, double *out_2604535394749705112) {
  h_31(state, unused, out_2604535394749705112);
}
void car_H_31(double *state, double *unused, double *out_1565205532565931561) {
  H_31(state, unused, out_1565205532565931561);
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
