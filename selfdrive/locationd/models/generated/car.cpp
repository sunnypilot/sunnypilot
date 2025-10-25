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
void err_fun(double *nom_x, double *delta_x, double *out_6316955287570611368) {
   out_6316955287570611368[0] = delta_x[0] + nom_x[0];
   out_6316955287570611368[1] = delta_x[1] + nom_x[1];
   out_6316955287570611368[2] = delta_x[2] + nom_x[2];
   out_6316955287570611368[3] = delta_x[3] + nom_x[3];
   out_6316955287570611368[4] = delta_x[4] + nom_x[4];
   out_6316955287570611368[5] = delta_x[5] + nom_x[5];
   out_6316955287570611368[6] = delta_x[6] + nom_x[6];
   out_6316955287570611368[7] = delta_x[7] + nom_x[7];
   out_6316955287570611368[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_5871234739833284335) {
   out_5871234739833284335[0] = -nom_x[0] + true_x[0];
   out_5871234739833284335[1] = -nom_x[1] + true_x[1];
   out_5871234739833284335[2] = -nom_x[2] + true_x[2];
   out_5871234739833284335[3] = -nom_x[3] + true_x[3];
   out_5871234739833284335[4] = -nom_x[4] + true_x[4];
   out_5871234739833284335[5] = -nom_x[5] + true_x[5];
   out_5871234739833284335[6] = -nom_x[6] + true_x[6];
   out_5871234739833284335[7] = -nom_x[7] + true_x[7];
   out_5871234739833284335[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_2946259916610688922) {
   out_2946259916610688922[0] = 1.0;
   out_2946259916610688922[1] = 0.0;
   out_2946259916610688922[2] = 0.0;
   out_2946259916610688922[3] = 0.0;
   out_2946259916610688922[4] = 0.0;
   out_2946259916610688922[5] = 0.0;
   out_2946259916610688922[6] = 0.0;
   out_2946259916610688922[7] = 0.0;
   out_2946259916610688922[8] = 0.0;
   out_2946259916610688922[9] = 0.0;
   out_2946259916610688922[10] = 1.0;
   out_2946259916610688922[11] = 0.0;
   out_2946259916610688922[12] = 0.0;
   out_2946259916610688922[13] = 0.0;
   out_2946259916610688922[14] = 0.0;
   out_2946259916610688922[15] = 0.0;
   out_2946259916610688922[16] = 0.0;
   out_2946259916610688922[17] = 0.0;
   out_2946259916610688922[18] = 0.0;
   out_2946259916610688922[19] = 0.0;
   out_2946259916610688922[20] = 1.0;
   out_2946259916610688922[21] = 0.0;
   out_2946259916610688922[22] = 0.0;
   out_2946259916610688922[23] = 0.0;
   out_2946259916610688922[24] = 0.0;
   out_2946259916610688922[25] = 0.0;
   out_2946259916610688922[26] = 0.0;
   out_2946259916610688922[27] = 0.0;
   out_2946259916610688922[28] = 0.0;
   out_2946259916610688922[29] = 0.0;
   out_2946259916610688922[30] = 1.0;
   out_2946259916610688922[31] = 0.0;
   out_2946259916610688922[32] = 0.0;
   out_2946259916610688922[33] = 0.0;
   out_2946259916610688922[34] = 0.0;
   out_2946259916610688922[35] = 0.0;
   out_2946259916610688922[36] = 0.0;
   out_2946259916610688922[37] = 0.0;
   out_2946259916610688922[38] = 0.0;
   out_2946259916610688922[39] = 0.0;
   out_2946259916610688922[40] = 1.0;
   out_2946259916610688922[41] = 0.0;
   out_2946259916610688922[42] = 0.0;
   out_2946259916610688922[43] = 0.0;
   out_2946259916610688922[44] = 0.0;
   out_2946259916610688922[45] = 0.0;
   out_2946259916610688922[46] = 0.0;
   out_2946259916610688922[47] = 0.0;
   out_2946259916610688922[48] = 0.0;
   out_2946259916610688922[49] = 0.0;
   out_2946259916610688922[50] = 1.0;
   out_2946259916610688922[51] = 0.0;
   out_2946259916610688922[52] = 0.0;
   out_2946259916610688922[53] = 0.0;
   out_2946259916610688922[54] = 0.0;
   out_2946259916610688922[55] = 0.0;
   out_2946259916610688922[56] = 0.0;
   out_2946259916610688922[57] = 0.0;
   out_2946259916610688922[58] = 0.0;
   out_2946259916610688922[59] = 0.0;
   out_2946259916610688922[60] = 1.0;
   out_2946259916610688922[61] = 0.0;
   out_2946259916610688922[62] = 0.0;
   out_2946259916610688922[63] = 0.0;
   out_2946259916610688922[64] = 0.0;
   out_2946259916610688922[65] = 0.0;
   out_2946259916610688922[66] = 0.0;
   out_2946259916610688922[67] = 0.0;
   out_2946259916610688922[68] = 0.0;
   out_2946259916610688922[69] = 0.0;
   out_2946259916610688922[70] = 1.0;
   out_2946259916610688922[71] = 0.0;
   out_2946259916610688922[72] = 0.0;
   out_2946259916610688922[73] = 0.0;
   out_2946259916610688922[74] = 0.0;
   out_2946259916610688922[75] = 0.0;
   out_2946259916610688922[76] = 0.0;
   out_2946259916610688922[77] = 0.0;
   out_2946259916610688922[78] = 0.0;
   out_2946259916610688922[79] = 0.0;
   out_2946259916610688922[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_928310023590060116) {
   out_928310023590060116[0] = state[0];
   out_928310023590060116[1] = state[1];
   out_928310023590060116[2] = state[2];
   out_928310023590060116[3] = state[3];
   out_928310023590060116[4] = state[4];
   out_928310023590060116[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8100000000000005*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_928310023590060116[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_928310023590060116[7] = state[7];
   out_928310023590060116[8] = state[8];
}
void F_fun(double *state, double dt, double *out_849753637263936557) {
   out_849753637263936557[0] = 1;
   out_849753637263936557[1] = 0;
   out_849753637263936557[2] = 0;
   out_849753637263936557[3] = 0;
   out_849753637263936557[4] = 0;
   out_849753637263936557[5] = 0;
   out_849753637263936557[6] = 0;
   out_849753637263936557[7] = 0;
   out_849753637263936557[8] = 0;
   out_849753637263936557[9] = 0;
   out_849753637263936557[10] = 1;
   out_849753637263936557[11] = 0;
   out_849753637263936557[12] = 0;
   out_849753637263936557[13] = 0;
   out_849753637263936557[14] = 0;
   out_849753637263936557[15] = 0;
   out_849753637263936557[16] = 0;
   out_849753637263936557[17] = 0;
   out_849753637263936557[18] = 0;
   out_849753637263936557[19] = 0;
   out_849753637263936557[20] = 1;
   out_849753637263936557[21] = 0;
   out_849753637263936557[22] = 0;
   out_849753637263936557[23] = 0;
   out_849753637263936557[24] = 0;
   out_849753637263936557[25] = 0;
   out_849753637263936557[26] = 0;
   out_849753637263936557[27] = 0;
   out_849753637263936557[28] = 0;
   out_849753637263936557[29] = 0;
   out_849753637263936557[30] = 1;
   out_849753637263936557[31] = 0;
   out_849753637263936557[32] = 0;
   out_849753637263936557[33] = 0;
   out_849753637263936557[34] = 0;
   out_849753637263936557[35] = 0;
   out_849753637263936557[36] = 0;
   out_849753637263936557[37] = 0;
   out_849753637263936557[38] = 0;
   out_849753637263936557[39] = 0;
   out_849753637263936557[40] = 1;
   out_849753637263936557[41] = 0;
   out_849753637263936557[42] = 0;
   out_849753637263936557[43] = 0;
   out_849753637263936557[44] = 0;
   out_849753637263936557[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_849753637263936557[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_849753637263936557[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_849753637263936557[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_849753637263936557[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_849753637263936557[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_849753637263936557[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_849753637263936557[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_849753637263936557[53] = -9.8100000000000005*dt;
   out_849753637263936557[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_849753637263936557[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_849753637263936557[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_849753637263936557[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_849753637263936557[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_849753637263936557[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_849753637263936557[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_849753637263936557[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_849753637263936557[62] = 0;
   out_849753637263936557[63] = 0;
   out_849753637263936557[64] = 0;
   out_849753637263936557[65] = 0;
   out_849753637263936557[66] = 0;
   out_849753637263936557[67] = 0;
   out_849753637263936557[68] = 0;
   out_849753637263936557[69] = 0;
   out_849753637263936557[70] = 1;
   out_849753637263936557[71] = 0;
   out_849753637263936557[72] = 0;
   out_849753637263936557[73] = 0;
   out_849753637263936557[74] = 0;
   out_849753637263936557[75] = 0;
   out_849753637263936557[76] = 0;
   out_849753637263936557[77] = 0;
   out_849753637263936557[78] = 0;
   out_849753637263936557[79] = 0;
   out_849753637263936557[80] = 1;
}
void h_25(double *state, double *unused, double *out_2337915436122240747) {
   out_2337915436122240747[0] = state[6];
}
void H_25(double *state, double *unused, double *out_3550763043279341029) {
   out_3550763043279341029[0] = 0;
   out_3550763043279341029[1] = 0;
   out_3550763043279341029[2] = 0;
   out_3550763043279341029[3] = 0;
   out_3550763043279341029[4] = 0;
   out_3550763043279341029[5] = 0;
   out_3550763043279341029[6] = 1;
   out_3550763043279341029[7] = 0;
   out_3550763043279341029[8] = 0;
}
void h_24(double *state, double *unused, double *out_7341814559737059360) {
   out_7341814559737059360[0] = state[4];
   out_7341814559737059360[1] = state[5];
}
void H_24(double *state, double *unused, double *out_7453306437441494267) {
   out_7453306437441494267[0] = 0;
   out_7453306437441494267[1] = 0;
   out_7453306437441494267[2] = 0;
   out_7453306437441494267[3] = 0;
   out_7453306437441494267[4] = 1;
   out_7453306437441494267[5] = 0;
   out_7453306437441494267[6] = 0;
   out_7453306437441494267[7] = 0;
   out_7453306437441494267[8] = 0;
   out_7453306437441494267[9] = 0;
   out_7453306437441494267[10] = 0;
   out_7453306437441494267[11] = 0;
   out_7453306437441494267[12] = 0;
   out_7453306437441494267[13] = 0;
   out_7453306437441494267[14] = 1;
   out_7453306437441494267[15] = 0;
   out_7453306437441494267[16] = 0;
   out_7453306437441494267[17] = 0;
}
void h_30(double *state, double *unused, double *out_5543357214631808438) {
   out_5543357214631808438[0] = state[4];
}
void H_30(double *state, double *unused, double *out_8078459373406949227) {
   out_8078459373406949227[0] = 0;
   out_8078459373406949227[1] = 0;
   out_8078459373406949227[2] = 0;
   out_8078459373406949227[3] = 0;
   out_8078459373406949227[4] = 1;
   out_8078459373406949227[5] = 0;
   out_8078459373406949227[6] = 0;
   out_8078459373406949227[7] = 0;
   out_8078459373406949227[8] = 0;
}
void h_26(double *state, double *unused, double *out_7561519623191712615) {
   out_7561519623191712615[0] = state[7];
}
void H_26(double *state, double *unused, double *out_7292266362153397253) {
   out_7292266362153397253[0] = 0;
   out_7292266362153397253[1] = 0;
   out_7292266362153397253[2] = 0;
   out_7292266362153397253[3] = 0;
   out_7292266362153397253[4] = 0;
   out_7292266362153397253[5] = 0;
   out_7292266362153397253[6] = 0;
   out_7292266362153397253[7] = 1;
   out_7292266362153397253[8] = 0;
}
void h_27(double *state, double *unused, double *out_2663757831538604898) {
   out_2663757831538604898[0] = state[3];
}
void H_27(double *state, double *unused, double *out_5854865302223006010) {
   out_5854865302223006010[0] = 0;
   out_5854865302223006010[1] = 0;
   out_5854865302223006010[2] = 0;
   out_5854865302223006010[3] = 1;
   out_5854865302223006010[4] = 0;
   out_5854865302223006010[5] = 0;
   out_5854865302223006010[6] = 0;
   out_5854865302223006010[7] = 0;
   out_5854865302223006010[8] = 0;
}
void h_29(double *state, double *unused, double *out_2938951893823110787) {
   out_2938951893823110787[0] = state[1];
}
void H_29(double *state, double *unused, double *out_7568228029092557043) {
   out_7568228029092557043[0] = 0;
   out_7568228029092557043[1] = 1;
   out_7568228029092557043[2] = 0;
   out_7568228029092557043[3] = 0;
   out_7568228029092557043[4] = 0;
   out_7568228029092557043[5] = 0;
   out_7568228029092557043[6] = 0;
   out_7568228029092557043[7] = 0;
   out_7568228029092557043[8] = 0;
}
void h_28(double *state, double *unused, double *out_7665431099199450543) {
   out_7665431099199450543[0] = state[0];
}
void H_28(double *state, double *unused, double *out_5796117027547463999) {
   out_5796117027547463999[0] = 1;
   out_5796117027547463999[1] = 0;
   out_5796117027547463999[2] = 0;
   out_5796117027547463999[3] = 0;
   out_5796117027547463999[4] = 0;
   out_5796117027547463999[5] = 0;
   out_5796117027547463999[6] = 0;
   out_5796117027547463999[7] = 0;
   out_5796117027547463999[8] = 0;
}
void h_31(double *state, double *unused, double *out_5975364964376263097) {
   out_5975364964376263097[0] = state[8];
}
void H_31(double *state, double *unused, double *out_3520117081402380601) {
   out_3520117081402380601[0] = 0;
   out_3520117081402380601[1] = 0;
   out_3520117081402380601[2] = 0;
   out_3520117081402380601[3] = 0;
   out_3520117081402380601[4] = 0;
   out_3520117081402380601[5] = 0;
   out_3520117081402380601[6] = 0;
   out_3520117081402380601[7] = 0;
   out_3520117081402380601[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_6316955287570611368) {
  err_fun(nom_x, delta_x, out_6316955287570611368);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_5871234739833284335) {
  inv_err_fun(nom_x, true_x, out_5871234739833284335);
}
void car_H_mod_fun(double *state, double *out_2946259916610688922) {
  H_mod_fun(state, out_2946259916610688922);
}
void car_f_fun(double *state, double dt, double *out_928310023590060116) {
  f_fun(state,  dt, out_928310023590060116);
}
void car_F_fun(double *state, double dt, double *out_849753637263936557) {
  F_fun(state,  dt, out_849753637263936557);
}
void car_h_25(double *state, double *unused, double *out_2337915436122240747) {
  h_25(state, unused, out_2337915436122240747);
}
void car_H_25(double *state, double *unused, double *out_3550763043279341029) {
  H_25(state, unused, out_3550763043279341029);
}
void car_h_24(double *state, double *unused, double *out_7341814559737059360) {
  h_24(state, unused, out_7341814559737059360);
}
void car_H_24(double *state, double *unused, double *out_7453306437441494267) {
  H_24(state, unused, out_7453306437441494267);
}
void car_h_30(double *state, double *unused, double *out_5543357214631808438) {
  h_30(state, unused, out_5543357214631808438);
}
void car_H_30(double *state, double *unused, double *out_8078459373406949227) {
  H_30(state, unused, out_8078459373406949227);
}
void car_h_26(double *state, double *unused, double *out_7561519623191712615) {
  h_26(state, unused, out_7561519623191712615);
}
void car_H_26(double *state, double *unused, double *out_7292266362153397253) {
  H_26(state, unused, out_7292266362153397253);
}
void car_h_27(double *state, double *unused, double *out_2663757831538604898) {
  h_27(state, unused, out_2663757831538604898);
}
void car_H_27(double *state, double *unused, double *out_5854865302223006010) {
  H_27(state, unused, out_5854865302223006010);
}
void car_h_29(double *state, double *unused, double *out_2938951893823110787) {
  h_29(state, unused, out_2938951893823110787);
}
void car_H_29(double *state, double *unused, double *out_7568228029092557043) {
  H_29(state, unused, out_7568228029092557043);
}
void car_h_28(double *state, double *unused, double *out_7665431099199450543) {
  h_28(state, unused, out_7665431099199450543);
}
void car_H_28(double *state, double *unused, double *out_5796117027547463999) {
  H_28(state, unused, out_5796117027547463999);
}
void car_h_31(double *state, double *unused, double *out_5975364964376263097) {
  h_31(state, unused, out_5975364964376263097);
}
void car_H_31(double *state, double *unused, double *out_3520117081402380601) {
  H_31(state, unused, out_3520117081402380601);
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
