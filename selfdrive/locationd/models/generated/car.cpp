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
void err_fun(double *nom_x, double *delta_x, double *out_3560803852879544025) {
   out_3560803852879544025[0] = delta_x[0] + nom_x[0];
   out_3560803852879544025[1] = delta_x[1] + nom_x[1];
   out_3560803852879544025[2] = delta_x[2] + nom_x[2];
   out_3560803852879544025[3] = delta_x[3] + nom_x[3];
   out_3560803852879544025[4] = delta_x[4] + nom_x[4];
   out_3560803852879544025[5] = delta_x[5] + nom_x[5];
   out_3560803852879544025[6] = delta_x[6] + nom_x[6];
   out_3560803852879544025[7] = delta_x[7] + nom_x[7];
   out_3560803852879544025[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_7615336851490548874) {
   out_7615336851490548874[0] = -nom_x[0] + true_x[0];
   out_7615336851490548874[1] = -nom_x[1] + true_x[1];
   out_7615336851490548874[2] = -nom_x[2] + true_x[2];
   out_7615336851490548874[3] = -nom_x[3] + true_x[3];
   out_7615336851490548874[4] = -nom_x[4] + true_x[4];
   out_7615336851490548874[5] = -nom_x[5] + true_x[5];
   out_7615336851490548874[6] = -nom_x[6] + true_x[6];
   out_7615336851490548874[7] = -nom_x[7] + true_x[7];
   out_7615336851490548874[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_8478329586395114374) {
   out_8478329586395114374[0] = 1.0;
   out_8478329586395114374[1] = 0.0;
   out_8478329586395114374[2] = 0.0;
   out_8478329586395114374[3] = 0.0;
   out_8478329586395114374[4] = 0.0;
   out_8478329586395114374[5] = 0.0;
   out_8478329586395114374[6] = 0.0;
   out_8478329586395114374[7] = 0.0;
   out_8478329586395114374[8] = 0.0;
   out_8478329586395114374[9] = 0.0;
   out_8478329586395114374[10] = 1.0;
   out_8478329586395114374[11] = 0.0;
   out_8478329586395114374[12] = 0.0;
   out_8478329586395114374[13] = 0.0;
   out_8478329586395114374[14] = 0.0;
   out_8478329586395114374[15] = 0.0;
   out_8478329586395114374[16] = 0.0;
   out_8478329586395114374[17] = 0.0;
   out_8478329586395114374[18] = 0.0;
   out_8478329586395114374[19] = 0.0;
   out_8478329586395114374[20] = 1.0;
   out_8478329586395114374[21] = 0.0;
   out_8478329586395114374[22] = 0.0;
   out_8478329586395114374[23] = 0.0;
   out_8478329586395114374[24] = 0.0;
   out_8478329586395114374[25] = 0.0;
   out_8478329586395114374[26] = 0.0;
   out_8478329586395114374[27] = 0.0;
   out_8478329586395114374[28] = 0.0;
   out_8478329586395114374[29] = 0.0;
   out_8478329586395114374[30] = 1.0;
   out_8478329586395114374[31] = 0.0;
   out_8478329586395114374[32] = 0.0;
   out_8478329586395114374[33] = 0.0;
   out_8478329586395114374[34] = 0.0;
   out_8478329586395114374[35] = 0.0;
   out_8478329586395114374[36] = 0.0;
   out_8478329586395114374[37] = 0.0;
   out_8478329586395114374[38] = 0.0;
   out_8478329586395114374[39] = 0.0;
   out_8478329586395114374[40] = 1.0;
   out_8478329586395114374[41] = 0.0;
   out_8478329586395114374[42] = 0.0;
   out_8478329586395114374[43] = 0.0;
   out_8478329586395114374[44] = 0.0;
   out_8478329586395114374[45] = 0.0;
   out_8478329586395114374[46] = 0.0;
   out_8478329586395114374[47] = 0.0;
   out_8478329586395114374[48] = 0.0;
   out_8478329586395114374[49] = 0.0;
   out_8478329586395114374[50] = 1.0;
   out_8478329586395114374[51] = 0.0;
   out_8478329586395114374[52] = 0.0;
   out_8478329586395114374[53] = 0.0;
   out_8478329586395114374[54] = 0.0;
   out_8478329586395114374[55] = 0.0;
   out_8478329586395114374[56] = 0.0;
   out_8478329586395114374[57] = 0.0;
   out_8478329586395114374[58] = 0.0;
   out_8478329586395114374[59] = 0.0;
   out_8478329586395114374[60] = 1.0;
   out_8478329586395114374[61] = 0.0;
   out_8478329586395114374[62] = 0.0;
   out_8478329586395114374[63] = 0.0;
   out_8478329586395114374[64] = 0.0;
   out_8478329586395114374[65] = 0.0;
   out_8478329586395114374[66] = 0.0;
   out_8478329586395114374[67] = 0.0;
   out_8478329586395114374[68] = 0.0;
   out_8478329586395114374[69] = 0.0;
   out_8478329586395114374[70] = 1.0;
   out_8478329586395114374[71] = 0.0;
   out_8478329586395114374[72] = 0.0;
   out_8478329586395114374[73] = 0.0;
   out_8478329586395114374[74] = 0.0;
   out_8478329586395114374[75] = 0.0;
   out_8478329586395114374[76] = 0.0;
   out_8478329586395114374[77] = 0.0;
   out_8478329586395114374[78] = 0.0;
   out_8478329586395114374[79] = 0.0;
   out_8478329586395114374[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_3623878700035833994) {
   out_3623878700035833994[0] = state[0];
   out_3623878700035833994[1] = state[1];
   out_3623878700035833994[2] = state[2];
   out_3623878700035833994[3] = state[3];
   out_3623878700035833994[4] = state[4];
   out_3623878700035833994[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8100000000000005*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_3623878700035833994[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_3623878700035833994[7] = state[7];
   out_3623878700035833994[8] = state[8];
}
void F_fun(double *state, double dt, double *out_5787759682681306104) {
   out_5787759682681306104[0] = 1;
   out_5787759682681306104[1] = 0;
   out_5787759682681306104[2] = 0;
   out_5787759682681306104[3] = 0;
   out_5787759682681306104[4] = 0;
   out_5787759682681306104[5] = 0;
   out_5787759682681306104[6] = 0;
   out_5787759682681306104[7] = 0;
   out_5787759682681306104[8] = 0;
   out_5787759682681306104[9] = 0;
   out_5787759682681306104[10] = 1;
   out_5787759682681306104[11] = 0;
   out_5787759682681306104[12] = 0;
   out_5787759682681306104[13] = 0;
   out_5787759682681306104[14] = 0;
   out_5787759682681306104[15] = 0;
   out_5787759682681306104[16] = 0;
   out_5787759682681306104[17] = 0;
   out_5787759682681306104[18] = 0;
   out_5787759682681306104[19] = 0;
   out_5787759682681306104[20] = 1;
   out_5787759682681306104[21] = 0;
   out_5787759682681306104[22] = 0;
   out_5787759682681306104[23] = 0;
   out_5787759682681306104[24] = 0;
   out_5787759682681306104[25] = 0;
   out_5787759682681306104[26] = 0;
   out_5787759682681306104[27] = 0;
   out_5787759682681306104[28] = 0;
   out_5787759682681306104[29] = 0;
   out_5787759682681306104[30] = 1;
   out_5787759682681306104[31] = 0;
   out_5787759682681306104[32] = 0;
   out_5787759682681306104[33] = 0;
   out_5787759682681306104[34] = 0;
   out_5787759682681306104[35] = 0;
   out_5787759682681306104[36] = 0;
   out_5787759682681306104[37] = 0;
   out_5787759682681306104[38] = 0;
   out_5787759682681306104[39] = 0;
   out_5787759682681306104[40] = 1;
   out_5787759682681306104[41] = 0;
   out_5787759682681306104[42] = 0;
   out_5787759682681306104[43] = 0;
   out_5787759682681306104[44] = 0;
   out_5787759682681306104[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_5787759682681306104[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_5787759682681306104[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_5787759682681306104[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_5787759682681306104[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_5787759682681306104[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_5787759682681306104[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_5787759682681306104[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_5787759682681306104[53] = -9.8100000000000005*dt;
   out_5787759682681306104[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_5787759682681306104[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_5787759682681306104[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_5787759682681306104[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_5787759682681306104[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_5787759682681306104[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_5787759682681306104[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_5787759682681306104[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_5787759682681306104[62] = 0;
   out_5787759682681306104[63] = 0;
   out_5787759682681306104[64] = 0;
   out_5787759682681306104[65] = 0;
   out_5787759682681306104[66] = 0;
   out_5787759682681306104[67] = 0;
   out_5787759682681306104[68] = 0;
   out_5787759682681306104[69] = 0;
   out_5787759682681306104[70] = 1;
   out_5787759682681306104[71] = 0;
   out_5787759682681306104[72] = 0;
   out_5787759682681306104[73] = 0;
   out_5787759682681306104[74] = 0;
   out_5787759682681306104[75] = 0;
   out_5787759682681306104[76] = 0;
   out_5787759682681306104[77] = 0;
   out_5787759682681306104[78] = 0;
   out_5787759682681306104[79] = 0;
   out_5787759682681306104[80] = 1;
}
void h_25(double *state, double *unused, double *out_5963614328607929912) {
   out_5963614328607929912[0] = state[6];
}
void H_25(double *state, double *unused, double *out_6445433837324945565) {
   out_6445433837324945565[0] = 0;
   out_6445433837324945565[1] = 0;
   out_6445433837324945565[2] = 0;
   out_6445433837324945565[3] = 0;
   out_6445433837324945565[4] = 0;
   out_6445433837324945565[5] = 0;
   out_6445433837324945565[6] = 1;
   out_6445433837324945565[7] = 0;
   out_6445433837324945565[8] = 0;
}
void h_24(double *state, double *unused, double *out_5741338745664737274) {
   out_5741338745664737274[0] = state[4];
   out_5741338745664737274[1] = state[5];
}
void H_24(double *state, double *unused, double *out_2887508238522622429) {
   out_2887508238522622429[0] = 0;
   out_2887508238522622429[1] = 0;
   out_2887508238522622429[2] = 0;
   out_2887508238522622429[3] = 0;
   out_2887508238522622429[4] = 1;
   out_2887508238522622429[5] = 0;
   out_2887508238522622429[6] = 0;
   out_2887508238522622429[7] = 0;
   out_2887508238522622429[8] = 0;
   out_2887508238522622429[9] = 0;
   out_2887508238522622429[10] = 0;
   out_2887508238522622429[11] = 0;
   out_2887508238522622429[12] = 0;
   out_2887508238522622429[13] = 0;
   out_2887508238522622429[14] = 1;
   out_2887508238522622429[15] = 0;
   out_2887508238522622429[16] = 0;
   out_2887508238522622429[17] = 0;
}
void h_30(double *state, double *unused, double *out_4275632999018714854) {
   out_4275632999018714854[0] = state[4];
}
void H_30(double *state, double *unused, double *out_3927100878817696938) {
   out_3927100878817696938[0] = 0;
   out_3927100878817696938[1] = 0;
   out_3927100878817696938[2] = 0;
   out_3927100878817696938[3] = 0;
   out_3927100878817696938[4] = 1;
   out_3927100878817696938[5] = 0;
   out_3927100878817696938[6] = 0;
   out_3927100878817696938[7] = 0;
   out_3927100878817696938[8] = 0;
}
void h_26(double *state, double *unused, double *out_6880038319827412505) {
   out_6880038319827412505[0] = state[7];
}
void H_26(double *state, double *unused, double *out_8259806917510549827) {
   out_8259806917510549827[0] = 0;
   out_8259806917510549827[1] = 0;
   out_8259806917510549827[2] = 0;
   out_8259806917510549827[3] = 0;
   out_8259806917510549827[4] = 0;
   out_8259806917510549827[5] = 0;
   out_8259806917510549827[6] = 0;
   out_8259806917510549827[7] = 1;
   out_8259806917510549827[8] = 0;
}
void h_27(double *state, double *unused, double *out_5480367041308555925) {
   out_5480367041308555925[0] = state[3];
}
void H_27(double *state, double *unused, double *out_1703506807633753721) {
   out_1703506807633753721[0] = 0;
   out_1703506807633753721[1] = 0;
   out_1703506807633753721[2] = 0;
   out_1703506807633753721[3] = 1;
   out_1703506807633753721[4] = 0;
   out_1703506807633753721[5] = 0;
   out_1703506807633753721[6] = 0;
   out_1703506807633753721[7] = 0;
   out_1703506807633753721[8] = 0;
}
void h_29(double *state, double *unused, double *out_9104693555972494039) {
   out_9104693555972494039[0] = state[1];
}
void H_29(double *state, double *unused, double *out_3416869534503304754) {
   out_3416869534503304754[0] = 0;
   out_3416869534503304754[1] = 1;
   out_3416869534503304754[2] = 0;
   out_3416869534503304754[3] = 0;
   out_3416869534503304754[4] = 0;
   out_3416869534503304754[5] = 0;
   out_3416869534503304754[6] = 0;
   out_3416869534503304754[7] = 0;
   out_3416869534503304754[8] = 0;
}
void h_28(double *state, double *unused, double *out_2667814938038702542) {
   out_2667814938038702542[0] = state[0];
}
void H_28(double *state, double *unused, double *out_8499268551572835328) {
   out_8499268551572835328[0] = 1;
   out_8499268551572835328[1] = 0;
   out_8499268551572835328[2] = 0;
   out_8499268551572835328[3] = 0;
   out_8499268551572835328[4] = 0;
   out_8499268551572835328[5] = 0;
   out_8499268551572835328[6] = 0;
   out_8499268551572835328[7] = 0;
   out_8499268551572835328[8] = 0;
}
void h_31(double *state, double *unused, double *out_5806427660256800767) {
   out_5806427660256800767[0] = state[8];
}
void H_31(double *state, double *unused, double *out_6414787875447985137) {
   out_6414787875447985137[0] = 0;
   out_6414787875447985137[1] = 0;
   out_6414787875447985137[2] = 0;
   out_6414787875447985137[3] = 0;
   out_6414787875447985137[4] = 0;
   out_6414787875447985137[5] = 0;
   out_6414787875447985137[6] = 0;
   out_6414787875447985137[7] = 0;
   out_6414787875447985137[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_3560803852879544025) {
  err_fun(nom_x, delta_x, out_3560803852879544025);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_7615336851490548874) {
  inv_err_fun(nom_x, true_x, out_7615336851490548874);
}
void car_H_mod_fun(double *state, double *out_8478329586395114374) {
  H_mod_fun(state, out_8478329586395114374);
}
void car_f_fun(double *state, double dt, double *out_3623878700035833994) {
  f_fun(state,  dt, out_3623878700035833994);
}
void car_F_fun(double *state, double dt, double *out_5787759682681306104) {
  F_fun(state,  dt, out_5787759682681306104);
}
void car_h_25(double *state, double *unused, double *out_5963614328607929912) {
  h_25(state, unused, out_5963614328607929912);
}
void car_H_25(double *state, double *unused, double *out_6445433837324945565) {
  H_25(state, unused, out_6445433837324945565);
}
void car_h_24(double *state, double *unused, double *out_5741338745664737274) {
  h_24(state, unused, out_5741338745664737274);
}
void car_H_24(double *state, double *unused, double *out_2887508238522622429) {
  H_24(state, unused, out_2887508238522622429);
}
void car_h_30(double *state, double *unused, double *out_4275632999018714854) {
  h_30(state, unused, out_4275632999018714854);
}
void car_H_30(double *state, double *unused, double *out_3927100878817696938) {
  H_30(state, unused, out_3927100878817696938);
}
void car_h_26(double *state, double *unused, double *out_6880038319827412505) {
  h_26(state, unused, out_6880038319827412505);
}
void car_H_26(double *state, double *unused, double *out_8259806917510549827) {
  H_26(state, unused, out_8259806917510549827);
}
void car_h_27(double *state, double *unused, double *out_5480367041308555925) {
  h_27(state, unused, out_5480367041308555925);
}
void car_H_27(double *state, double *unused, double *out_1703506807633753721) {
  H_27(state, unused, out_1703506807633753721);
}
void car_h_29(double *state, double *unused, double *out_9104693555972494039) {
  h_29(state, unused, out_9104693555972494039);
}
void car_H_29(double *state, double *unused, double *out_3416869534503304754) {
  H_29(state, unused, out_3416869534503304754);
}
void car_h_28(double *state, double *unused, double *out_2667814938038702542) {
  h_28(state, unused, out_2667814938038702542);
}
void car_H_28(double *state, double *unused, double *out_8499268551572835328) {
  H_28(state, unused, out_8499268551572835328);
}
void car_h_31(double *state, double *unused, double *out_5806427660256800767) {
  h_31(state, unused, out_5806427660256800767);
}
void car_H_31(double *state, double *unused, double *out_6414787875447985137) {
  H_31(state, unused, out_6414787875447985137);
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
