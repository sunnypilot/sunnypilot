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
void err_fun(double *nom_x, double *delta_x, double *out_7619292515865737175) {
   out_7619292515865737175[0] = delta_x[0] + nom_x[0];
   out_7619292515865737175[1] = delta_x[1] + nom_x[1];
   out_7619292515865737175[2] = delta_x[2] + nom_x[2];
   out_7619292515865737175[3] = delta_x[3] + nom_x[3];
   out_7619292515865737175[4] = delta_x[4] + nom_x[4];
   out_7619292515865737175[5] = delta_x[5] + nom_x[5];
   out_7619292515865737175[6] = delta_x[6] + nom_x[6];
   out_7619292515865737175[7] = delta_x[7] + nom_x[7];
   out_7619292515865737175[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_5452062773601768243) {
   out_5452062773601768243[0] = -nom_x[0] + true_x[0];
   out_5452062773601768243[1] = -nom_x[1] + true_x[1];
   out_5452062773601768243[2] = -nom_x[2] + true_x[2];
   out_5452062773601768243[3] = -nom_x[3] + true_x[3];
   out_5452062773601768243[4] = -nom_x[4] + true_x[4];
   out_5452062773601768243[5] = -nom_x[5] + true_x[5];
   out_5452062773601768243[6] = -nom_x[6] + true_x[6];
   out_5452062773601768243[7] = -nom_x[7] + true_x[7];
   out_5452062773601768243[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_7725418025905253046) {
   out_7725418025905253046[0] = 1.0;
   out_7725418025905253046[1] = 0;
   out_7725418025905253046[2] = 0;
   out_7725418025905253046[3] = 0;
   out_7725418025905253046[4] = 0;
   out_7725418025905253046[5] = 0;
   out_7725418025905253046[6] = 0;
   out_7725418025905253046[7] = 0;
   out_7725418025905253046[8] = 0;
   out_7725418025905253046[9] = 0;
   out_7725418025905253046[10] = 1.0;
   out_7725418025905253046[11] = 0;
   out_7725418025905253046[12] = 0;
   out_7725418025905253046[13] = 0;
   out_7725418025905253046[14] = 0;
   out_7725418025905253046[15] = 0;
   out_7725418025905253046[16] = 0;
   out_7725418025905253046[17] = 0;
   out_7725418025905253046[18] = 0;
   out_7725418025905253046[19] = 0;
   out_7725418025905253046[20] = 1.0;
   out_7725418025905253046[21] = 0;
   out_7725418025905253046[22] = 0;
   out_7725418025905253046[23] = 0;
   out_7725418025905253046[24] = 0;
   out_7725418025905253046[25] = 0;
   out_7725418025905253046[26] = 0;
   out_7725418025905253046[27] = 0;
   out_7725418025905253046[28] = 0;
   out_7725418025905253046[29] = 0;
   out_7725418025905253046[30] = 1.0;
   out_7725418025905253046[31] = 0;
   out_7725418025905253046[32] = 0;
   out_7725418025905253046[33] = 0;
   out_7725418025905253046[34] = 0;
   out_7725418025905253046[35] = 0;
   out_7725418025905253046[36] = 0;
   out_7725418025905253046[37] = 0;
   out_7725418025905253046[38] = 0;
   out_7725418025905253046[39] = 0;
   out_7725418025905253046[40] = 1.0;
   out_7725418025905253046[41] = 0;
   out_7725418025905253046[42] = 0;
   out_7725418025905253046[43] = 0;
   out_7725418025905253046[44] = 0;
   out_7725418025905253046[45] = 0;
   out_7725418025905253046[46] = 0;
   out_7725418025905253046[47] = 0;
   out_7725418025905253046[48] = 0;
   out_7725418025905253046[49] = 0;
   out_7725418025905253046[50] = 1.0;
   out_7725418025905253046[51] = 0;
   out_7725418025905253046[52] = 0;
   out_7725418025905253046[53] = 0;
   out_7725418025905253046[54] = 0;
   out_7725418025905253046[55] = 0;
   out_7725418025905253046[56] = 0;
   out_7725418025905253046[57] = 0;
   out_7725418025905253046[58] = 0;
   out_7725418025905253046[59] = 0;
   out_7725418025905253046[60] = 1.0;
   out_7725418025905253046[61] = 0;
   out_7725418025905253046[62] = 0;
   out_7725418025905253046[63] = 0;
   out_7725418025905253046[64] = 0;
   out_7725418025905253046[65] = 0;
   out_7725418025905253046[66] = 0;
   out_7725418025905253046[67] = 0;
   out_7725418025905253046[68] = 0;
   out_7725418025905253046[69] = 0;
   out_7725418025905253046[70] = 1.0;
   out_7725418025905253046[71] = 0;
   out_7725418025905253046[72] = 0;
   out_7725418025905253046[73] = 0;
   out_7725418025905253046[74] = 0;
   out_7725418025905253046[75] = 0;
   out_7725418025905253046[76] = 0;
   out_7725418025905253046[77] = 0;
   out_7725418025905253046[78] = 0;
   out_7725418025905253046[79] = 0;
   out_7725418025905253046[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_1475289048643592209) {
   out_1475289048643592209[0] = state[0];
   out_1475289048643592209[1] = state[1];
   out_1475289048643592209[2] = state[2];
   out_1475289048643592209[3] = state[3];
   out_1475289048643592209[4] = state[4];
   out_1475289048643592209[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8000000000000007*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_1475289048643592209[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_1475289048643592209[7] = state[7];
   out_1475289048643592209[8] = state[8];
}
void F_fun(double *state, double dt, double *out_1545992405806302656) {
   out_1545992405806302656[0] = 1;
   out_1545992405806302656[1] = 0;
   out_1545992405806302656[2] = 0;
   out_1545992405806302656[3] = 0;
   out_1545992405806302656[4] = 0;
   out_1545992405806302656[5] = 0;
   out_1545992405806302656[6] = 0;
   out_1545992405806302656[7] = 0;
   out_1545992405806302656[8] = 0;
   out_1545992405806302656[9] = 0;
   out_1545992405806302656[10] = 1;
   out_1545992405806302656[11] = 0;
   out_1545992405806302656[12] = 0;
   out_1545992405806302656[13] = 0;
   out_1545992405806302656[14] = 0;
   out_1545992405806302656[15] = 0;
   out_1545992405806302656[16] = 0;
   out_1545992405806302656[17] = 0;
   out_1545992405806302656[18] = 0;
   out_1545992405806302656[19] = 0;
   out_1545992405806302656[20] = 1;
   out_1545992405806302656[21] = 0;
   out_1545992405806302656[22] = 0;
   out_1545992405806302656[23] = 0;
   out_1545992405806302656[24] = 0;
   out_1545992405806302656[25] = 0;
   out_1545992405806302656[26] = 0;
   out_1545992405806302656[27] = 0;
   out_1545992405806302656[28] = 0;
   out_1545992405806302656[29] = 0;
   out_1545992405806302656[30] = 1;
   out_1545992405806302656[31] = 0;
   out_1545992405806302656[32] = 0;
   out_1545992405806302656[33] = 0;
   out_1545992405806302656[34] = 0;
   out_1545992405806302656[35] = 0;
   out_1545992405806302656[36] = 0;
   out_1545992405806302656[37] = 0;
   out_1545992405806302656[38] = 0;
   out_1545992405806302656[39] = 0;
   out_1545992405806302656[40] = 1;
   out_1545992405806302656[41] = 0;
   out_1545992405806302656[42] = 0;
   out_1545992405806302656[43] = 0;
   out_1545992405806302656[44] = 0;
   out_1545992405806302656[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_1545992405806302656[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_1545992405806302656[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_1545992405806302656[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_1545992405806302656[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_1545992405806302656[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_1545992405806302656[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_1545992405806302656[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_1545992405806302656[53] = -9.8000000000000007*dt;
   out_1545992405806302656[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_1545992405806302656[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_1545992405806302656[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_1545992405806302656[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_1545992405806302656[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_1545992405806302656[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_1545992405806302656[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_1545992405806302656[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_1545992405806302656[62] = 0;
   out_1545992405806302656[63] = 0;
   out_1545992405806302656[64] = 0;
   out_1545992405806302656[65] = 0;
   out_1545992405806302656[66] = 0;
   out_1545992405806302656[67] = 0;
   out_1545992405806302656[68] = 0;
   out_1545992405806302656[69] = 0;
   out_1545992405806302656[70] = 1;
   out_1545992405806302656[71] = 0;
   out_1545992405806302656[72] = 0;
   out_1545992405806302656[73] = 0;
   out_1545992405806302656[74] = 0;
   out_1545992405806302656[75] = 0;
   out_1545992405806302656[76] = 0;
   out_1545992405806302656[77] = 0;
   out_1545992405806302656[78] = 0;
   out_1545992405806302656[79] = 0;
   out_1545992405806302656[80] = 1;
}
void h_25(double *state, double *unused, double *out_7361177615809799200) {
   out_7361177615809799200[0] = state[6];
}
void H_25(double *state, double *unused, double *out_8815050834348377649) {
   out_8815050834348377649[0] = 0;
   out_8815050834348377649[1] = 0;
   out_8815050834348377649[2] = 0;
   out_8815050834348377649[3] = 0;
   out_8815050834348377649[4] = 0;
   out_8815050834348377649[5] = 0;
   out_8815050834348377649[6] = 1;
   out_8815050834348377649[7] = 0;
   out_8815050834348377649[8] = 0;
}
void h_24(double *state, double *unused, double *out_5817420711568356655) {
   out_5817420711568356655[0] = state[4];
   out_5817420711568356655[1] = state[5];
}
void H_24(double *state, double *unused, double *out_7402022586309968812) {
   out_7402022586309968812[0] = 0;
   out_7402022586309968812[1] = 0;
   out_7402022586309968812[2] = 0;
   out_7402022586309968812[3] = 0;
   out_7402022586309968812[4] = 1;
   out_7402022586309968812[5] = 0;
   out_7402022586309968812[6] = 0;
   out_7402022586309968812[7] = 0;
   out_7402022586309968812[8] = 0;
   out_7402022586309968812[9] = 0;
   out_7402022586309968812[10] = 0;
   out_7402022586309968812[11] = 0;
   out_7402022586309968812[12] = 0;
   out_7402022586309968812[13] = 0;
   out_7402022586309968812[14] = 1;
   out_7402022586309968812[15] = 0;
   out_7402022586309968812[16] = 0;
   out_7402022586309968812[17] = 0;
}
void h_30(double *state, double *unused, double *out_590342389459448264) {
   out_590342389459448264[0] = state[4];
}
void H_30(double *state, double *unused, double *out_6296717875841129022) {
   out_6296717875841129022[0] = 0;
   out_6296717875841129022[1] = 0;
   out_6296717875841129022[2] = 0;
   out_6296717875841129022[3] = 0;
   out_6296717875841129022[4] = 1;
   out_6296717875841129022[5] = 0;
   out_6296717875841129022[6] = 0;
   out_6296717875841129022[7] = 0;
   out_6296717875841129022[8] = 0;
}
void h_26(double *state, double *unused, double *out_4411330878201397381) {
   out_4411330878201397381[0] = state[7];
}
void H_26(double *state, double *unused, double *out_5890189920487117743) {
   out_5890189920487117743[0] = 0;
   out_5890189920487117743[1] = 0;
   out_5890189920487117743[2] = 0;
   out_5890189920487117743[3] = 0;
   out_5890189920487117743[4] = 0;
   out_5890189920487117743[5] = 0;
   out_5890189920487117743[6] = 0;
   out_5890189920487117743[7] = 1;
   out_5890189920487117743[8] = 0;
}
void h_27(double *state, double *unused, double *out_6417667762908136765) {
   out_6417667762908136765[0] = state[3];
}
void H_27(double *state, double *unused, double *out_7327590980417508986) {
   out_7327590980417508986[0] = 0;
   out_7327590980417508986[1] = 0;
   out_7327590980417508986[2] = 0;
   out_7327590980417508986[3] = 1;
   out_7327590980417508986[4] = 0;
   out_7327590980417508986[5] = 0;
   out_7327590980417508986[6] = 0;
   out_7327590980417508986[7] = 0;
   out_7327590980417508986[8] = 0;
}
void h_29(double *state, double *unused, double *out_5592015657120293909) {
   out_5592015657120293909[0] = state[1];
}
void H_29(double *state, double *unused, double *out_5786486531526736838) {
   out_5786486531526736838[0] = 0;
   out_5786486531526736838[1] = 1;
   out_5786486531526736838[2] = 0;
   out_5786486531526736838[3] = 0;
   out_5786486531526736838[4] = 0;
   out_5786486531526736838[5] = 0;
   out_5786486531526736838[6] = 0;
   out_5786486531526736838[7] = 0;
   out_5786486531526736838[8] = 0;
}
void h_28(double *state, double *unused, double *out_7631124229519785839) {
   out_7631124229519785839[0] = state[0];
}
void H_28(double *state, double *unused, double *out_7577858525113284204) {
   out_7577858525113284204[0] = 1;
   out_7577858525113284204[1] = 0;
   out_7577858525113284204[2] = 0;
   out_7577858525113284204[3] = 0;
   out_7577858525113284204[4] = 0;
   out_7577858525113284204[5] = 0;
   out_7577858525113284204[6] = 0;
   out_7577858525113284204[7] = 0;
   out_7577858525113284204[8] = 0;
}
void h_31(double *state, double *unused, double *out_7518364284160928345) {
   out_7518364284160928345[0] = state[8];
}
void H_31(double *state, double *unused, double *out_5263981818253766267) {
   out_5263981818253766267[0] = 0;
   out_5263981818253766267[1] = 0;
   out_5263981818253766267[2] = 0;
   out_5263981818253766267[3] = 0;
   out_5263981818253766267[4] = 0;
   out_5263981818253766267[5] = 0;
   out_5263981818253766267[6] = 0;
   out_5263981818253766267[7] = 0;
   out_5263981818253766267[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_7619292515865737175) {
  err_fun(nom_x, delta_x, out_7619292515865737175);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_5452062773601768243) {
  inv_err_fun(nom_x, true_x, out_5452062773601768243);
}
void car_H_mod_fun(double *state, double *out_7725418025905253046) {
  H_mod_fun(state, out_7725418025905253046);
}
void car_f_fun(double *state, double dt, double *out_1475289048643592209) {
  f_fun(state,  dt, out_1475289048643592209);
}
void car_F_fun(double *state, double dt, double *out_1545992405806302656) {
  F_fun(state,  dt, out_1545992405806302656);
}
void car_h_25(double *state, double *unused, double *out_7361177615809799200) {
  h_25(state, unused, out_7361177615809799200);
}
void car_H_25(double *state, double *unused, double *out_8815050834348377649) {
  H_25(state, unused, out_8815050834348377649);
}
void car_h_24(double *state, double *unused, double *out_5817420711568356655) {
  h_24(state, unused, out_5817420711568356655);
}
void car_H_24(double *state, double *unused, double *out_7402022586309968812) {
  H_24(state, unused, out_7402022586309968812);
}
void car_h_30(double *state, double *unused, double *out_590342389459448264) {
  h_30(state, unused, out_590342389459448264);
}
void car_H_30(double *state, double *unused, double *out_6296717875841129022) {
  H_30(state, unused, out_6296717875841129022);
}
void car_h_26(double *state, double *unused, double *out_4411330878201397381) {
  h_26(state, unused, out_4411330878201397381);
}
void car_H_26(double *state, double *unused, double *out_5890189920487117743) {
  H_26(state, unused, out_5890189920487117743);
}
void car_h_27(double *state, double *unused, double *out_6417667762908136765) {
  h_27(state, unused, out_6417667762908136765);
}
void car_H_27(double *state, double *unused, double *out_7327590980417508986) {
  H_27(state, unused, out_7327590980417508986);
}
void car_h_29(double *state, double *unused, double *out_5592015657120293909) {
  h_29(state, unused, out_5592015657120293909);
}
void car_H_29(double *state, double *unused, double *out_5786486531526736838) {
  H_29(state, unused, out_5786486531526736838);
}
void car_h_28(double *state, double *unused, double *out_7631124229519785839) {
  h_28(state, unused, out_7631124229519785839);
}
void car_H_28(double *state, double *unused, double *out_7577858525113284204) {
  H_28(state, unused, out_7577858525113284204);
}
void car_h_31(double *state, double *unused, double *out_7518364284160928345) {
  h_31(state, unused, out_7518364284160928345);
}
void car_H_31(double *state, double *unused, double *out_5263981818253766267) {
  H_31(state, unused, out_5263981818253766267);
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
