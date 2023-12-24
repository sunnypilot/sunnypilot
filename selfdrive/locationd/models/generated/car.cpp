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
void err_fun(double *nom_x, double *delta_x, double *out_1027636603068461502) {
   out_1027636603068461502[0] = delta_x[0] + nom_x[0];
   out_1027636603068461502[1] = delta_x[1] + nom_x[1];
   out_1027636603068461502[2] = delta_x[2] + nom_x[2];
   out_1027636603068461502[3] = delta_x[3] + nom_x[3];
   out_1027636603068461502[4] = delta_x[4] + nom_x[4];
   out_1027636603068461502[5] = delta_x[5] + nom_x[5];
   out_1027636603068461502[6] = delta_x[6] + nom_x[6];
   out_1027636603068461502[7] = delta_x[7] + nom_x[7];
   out_1027636603068461502[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_2498107869525935257) {
   out_2498107869525935257[0] = -nom_x[0] + true_x[0];
   out_2498107869525935257[1] = -nom_x[1] + true_x[1];
   out_2498107869525935257[2] = -nom_x[2] + true_x[2];
   out_2498107869525935257[3] = -nom_x[3] + true_x[3];
   out_2498107869525935257[4] = -nom_x[4] + true_x[4];
   out_2498107869525935257[5] = -nom_x[5] + true_x[5];
   out_2498107869525935257[6] = -nom_x[6] + true_x[6];
   out_2498107869525935257[7] = -nom_x[7] + true_x[7];
   out_2498107869525935257[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_2880487860269583385) {
   out_2880487860269583385[0] = 1.0;
   out_2880487860269583385[1] = 0;
   out_2880487860269583385[2] = 0;
   out_2880487860269583385[3] = 0;
   out_2880487860269583385[4] = 0;
   out_2880487860269583385[5] = 0;
   out_2880487860269583385[6] = 0;
   out_2880487860269583385[7] = 0;
   out_2880487860269583385[8] = 0;
   out_2880487860269583385[9] = 0;
   out_2880487860269583385[10] = 1.0;
   out_2880487860269583385[11] = 0;
   out_2880487860269583385[12] = 0;
   out_2880487860269583385[13] = 0;
   out_2880487860269583385[14] = 0;
   out_2880487860269583385[15] = 0;
   out_2880487860269583385[16] = 0;
   out_2880487860269583385[17] = 0;
   out_2880487860269583385[18] = 0;
   out_2880487860269583385[19] = 0;
   out_2880487860269583385[20] = 1.0;
   out_2880487860269583385[21] = 0;
   out_2880487860269583385[22] = 0;
   out_2880487860269583385[23] = 0;
   out_2880487860269583385[24] = 0;
   out_2880487860269583385[25] = 0;
   out_2880487860269583385[26] = 0;
   out_2880487860269583385[27] = 0;
   out_2880487860269583385[28] = 0;
   out_2880487860269583385[29] = 0;
   out_2880487860269583385[30] = 1.0;
   out_2880487860269583385[31] = 0;
   out_2880487860269583385[32] = 0;
   out_2880487860269583385[33] = 0;
   out_2880487860269583385[34] = 0;
   out_2880487860269583385[35] = 0;
   out_2880487860269583385[36] = 0;
   out_2880487860269583385[37] = 0;
   out_2880487860269583385[38] = 0;
   out_2880487860269583385[39] = 0;
   out_2880487860269583385[40] = 1.0;
   out_2880487860269583385[41] = 0;
   out_2880487860269583385[42] = 0;
   out_2880487860269583385[43] = 0;
   out_2880487860269583385[44] = 0;
   out_2880487860269583385[45] = 0;
   out_2880487860269583385[46] = 0;
   out_2880487860269583385[47] = 0;
   out_2880487860269583385[48] = 0;
   out_2880487860269583385[49] = 0;
   out_2880487860269583385[50] = 1.0;
   out_2880487860269583385[51] = 0;
   out_2880487860269583385[52] = 0;
   out_2880487860269583385[53] = 0;
   out_2880487860269583385[54] = 0;
   out_2880487860269583385[55] = 0;
   out_2880487860269583385[56] = 0;
   out_2880487860269583385[57] = 0;
   out_2880487860269583385[58] = 0;
   out_2880487860269583385[59] = 0;
   out_2880487860269583385[60] = 1.0;
   out_2880487860269583385[61] = 0;
   out_2880487860269583385[62] = 0;
   out_2880487860269583385[63] = 0;
   out_2880487860269583385[64] = 0;
   out_2880487860269583385[65] = 0;
   out_2880487860269583385[66] = 0;
   out_2880487860269583385[67] = 0;
   out_2880487860269583385[68] = 0;
   out_2880487860269583385[69] = 0;
   out_2880487860269583385[70] = 1.0;
   out_2880487860269583385[71] = 0;
   out_2880487860269583385[72] = 0;
   out_2880487860269583385[73] = 0;
   out_2880487860269583385[74] = 0;
   out_2880487860269583385[75] = 0;
   out_2880487860269583385[76] = 0;
   out_2880487860269583385[77] = 0;
   out_2880487860269583385[78] = 0;
   out_2880487860269583385[79] = 0;
   out_2880487860269583385[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_8985245024092687483) {
   out_8985245024092687483[0] = state[0];
   out_8985245024092687483[1] = state[1];
   out_8985245024092687483[2] = state[2];
   out_8985245024092687483[3] = state[3];
   out_8985245024092687483[4] = state[4];
   out_8985245024092687483[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8000000000000007*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_8985245024092687483[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_8985245024092687483[7] = state[7];
   out_8985245024092687483[8] = state[8];
}
void F_fun(double *state, double dt, double *out_135664326016666632) {
   out_135664326016666632[0] = 1;
   out_135664326016666632[1] = 0;
   out_135664326016666632[2] = 0;
   out_135664326016666632[3] = 0;
   out_135664326016666632[4] = 0;
   out_135664326016666632[5] = 0;
   out_135664326016666632[6] = 0;
   out_135664326016666632[7] = 0;
   out_135664326016666632[8] = 0;
   out_135664326016666632[9] = 0;
   out_135664326016666632[10] = 1;
   out_135664326016666632[11] = 0;
   out_135664326016666632[12] = 0;
   out_135664326016666632[13] = 0;
   out_135664326016666632[14] = 0;
   out_135664326016666632[15] = 0;
   out_135664326016666632[16] = 0;
   out_135664326016666632[17] = 0;
   out_135664326016666632[18] = 0;
   out_135664326016666632[19] = 0;
   out_135664326016666632[20] = 1;
   out_135664326016666632[21] = 0;
   out_135664326016666632[22] = 0;
   out_135664326016666632[23] = 0;
   out_135664326016666632[24] = 0;
   out_135664326016666632[25] = 0;
   out_135664326016666632[26] = 0;
   out_135664326016666632[27] = 0;
   out_135664326016666632[28] = 0;
   out_135664326016666632[29] = 0;
   out_135664326016666632[30] = 1;
   out_135664326016666632[31] = 0;
   out_135664326016666632[32] = 0;
   out_135664326016666632[33] = 0;
   out_135664326016666632[34] = 0;
   out_135664326016666632[35] = 0;
   out_135664326016666632[36] = 0;
   out_135664326016666632[37] = 0;
   out_135664326016666632[38] = 0;
   out_135664326016666632[39] = 0;
   out_135664326016666632[40] = 1;
   out_135664326016666632[41] = 0;
   out_135664326016666632[42] = 0;
   out_135664326016666632[43] = 0;
   out_135664326016666632[44] = 0;
   out_135664326016666632[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_135664326016666632[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_135664326016666632[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_135664326016666632[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_135664326016666632[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_135664326016666632[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_135664326016666632[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_135664326016666632[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_135664326016666632[53] = -9.8000000000000007*dt;
   out_135664326016666632[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_135664326016666632[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_135664326016666632[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_135664326016666632[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_135664326016666632[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_135664326016666632[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_135664326016666632[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_135664326016666632[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_135664326016666632[62] = 0;
   out_135664326016666632[63] = 0;
   out_135664326016666632[64] = 0;
   out_135664326016666632[65] = 0;
   out_135664326016666632[66] = 0;
   out_135664326016666632[67] = 0;
   out_135664326016666632[68] = 0;
   out_135664326016666632[69] = 0;
   out_135664326016666632[70] = 1;
   out_135664326016666632[71] = 0;
   out_135664326016666632[72] = 0;
   out_135664326016666632[73] = 0;
   out_135664326016666632[74] = 0;
   out_135664326016666632[75] = 0;
   out_135664326016666632[76] = 0;
   out_135664326016666632[77] = 0;
   out_135664326016666632[78] = 0;
   out_135664326016666632[79] = 0;
   out_135664326016666632[80] = 1;
}
void h_25(double *state, double *unused, double *out_1339936627130384923) {
   out_1339936627130384923[0] = state[6];
}
void H_25(double *state, double *unused, double *out_8541205388556229655) {
   out_8541205388556229655[0] = 0;
   out_8541205388556229655[1] = 0;
   out_8541205388556229655[2] = 0;
   out_8541205388556229655[3] = 0;
   out_8541205388556229655[4] = 0;
   out_8541205388556229655[5] = 0;
   out_8541205388556229655[6] = 1;
   out_8541205388556229655[7] = 0;
   out_8541205388556229655[8] = 0;
}
void h_24(double *state, double *unused, double *out_7843416543337357224) {
   out_7843416543337357224[0] = state[4];
   out_7843416543337357224[1] = state[5];
}
void H_24(double *state, double *unused, double *out_4983279789753906519) {
   out_4983279789753906519[0] = 0;
   out_4983279789753906519[1] = 0;
   out_4983279789753906519[2] = 0;
   out_4983279789753906519[3] = 0;
   out_4983279789753906519[4] = 1;
   out_4983279789753906519[5] = 0;
   out_4983279789753906519[6] = 0;
   out_4983279789753906519[7] = 0;
   out_4983279789753906519[8] = 0;
   out_4983279789753906519[9] = 0;
   out_4983279789753906519[10] = 0;
   out_4983279789753906519[11] = 0;
   out_4983279789753906519[12] = 0;
   out_4983279789753906519[13] = 0;
   out_4983279789753906519[14] = 1;
   out_4983279789753906519[15] = 0;
   out_4983279789753906519[16] = 0;
   out_4983279789753906519[17] = 0;
}
void h_30(double *state, double *unused, double *out_7253669653801133296) {
   out_7253669653801133296[0] = state[4];
}
void H_30(double *state, double *unused, double *out_6022872430048981028) {
   out_6022872430048981028[0] = 0;
   out_6022872430048981028[1] = 0;
   out_6022872430048981028[2] = 0;
   out_6022872430048981028[3] = 0;
   out_6022872430048981028[4] = 1;
   out_6022872430048981028[5] = 0;
   out_6022872430048981028[6] = 0;
   out_6022872430048981028[7] = 0;
   out_6022872430048981028[8] = 0;
}
void h_26(double *state, double *unused, double *out_7856985538477610813) {
   out_7856985538477610813[0] = state[7];
}
void H_26(double *state, double *unused, double *out_5236679418795429054) {
   out_5236679418795429054[0] = 0;
   out_5236679418795429054[1] = 0;
   out_5236679418795429054[2] = 0;
   out_5236679418795429054[3] = 0;
   out_5236679418795429054[4] = 0;
   out_5236679418795429054[5] = 0;
   out_5236679418795429054[6] = 0;
   out_5236679418795429054[7] = 1;
   out_5236679418795429054[8] = 0;
}
void h_27(double *state, double *unused, double *out_3661736640530460722) {
   out_3661736640530460722[0] = state[3];
}
void H_27(double *state, double *unused, double *out_3799278358865037811) {
   out_3799278358865037811[0] = 0;
   out_3799278358865037811[1] = 0;
   out_3799278358865037811[2] = 0;
   out_3799278358865037811[3] = 1;
   out_3799278358865037811[4] = 0;
   out_3799278358865037811[5] = 0;
   out_3799278358865037811[6] = 0;
   out_3799278358865037811[7] = 0;
   out_3799278358865037811[8] = 0;
}
void h_29(double *state, double *unused, double *out_2211105247901577555) {
   out_2211105247901577555[0] = state[1];
}
void H_29(double *state, double *unused, double *out_5512641085734588844) {
   out_5512641085734588844[0] = 0;
   out_5512641085734588844[1] = 1;
   out_5512641085734588844[2] = 0;
   out_5512641085734588844[3] = 0;
   out_5512641085734588844[4] = 0;
   out_5512641085734588844[5] = 0;
   out_5512641085734588844[6] = 0;
   out_5512641085734588844[7] = 0;
   out_5512641085734588844[8] = 0;
}
void h_28(double *state, double *unused, double *out_8663409908191306367) {
   out_8663409908191306367[0] = state[0];
}
void H_28(double *state, double *unused, double *out_7851703970905432198) {
   out_7851703970905432198[0] = 1;
   out_7851703970905432198[1] = 0;
   out_7851703970905432198[2] = 0;
   out_7851703970905432198[3] = 0;
   out_7851703970905432198[4] = 0;
   out_7851703970905432198[5] = 0;
   out_7851703970905432198[6] = 0;
   out_7851703970905432198[7] = 0;
   out_7851703970905432198[8] = 0;
}
void h_31(double *state, double *unused, double *out_5201620103558886575) {
   out_5201620103558886575[0] = state[8];
}
void H_31(double *state, double *unused, double *out_1464530138044412402) {
   out_1464530138044412402[0] = 0;
   out_1464530138044412402[1] = 0;
   out_1464530138044412402[2] = 0;
   out_1464530138044412402[3] = 0;
   out_1464530138044412402[4] = 0;
   out_1464530138044412402[5] = 0;
   out_1464530138044412402[6] = 0;
   out_1464530138044412402[7] = 0;
   out_1464530138044412402[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_1027636603068461502) {
  err_fun(nom_x, delta_x, out_1027636603068461502);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_2498107869525935257) {
  inv_err_fun(nom_x, true_x, out_2498107869525935257);
}
void car_H_mod_fun(double *state, double *out_2880487860269583385) {
  H_mod_fun(state, out_2880487860269583385);
}
void car_f_fun(double *state, double dt, double *out_8985245024092687483) {
  f_fun(state,  dt, out_8985245024092687483);
}
void car_F_fun(double *state, double dt, double *out_135664326016666632) {
  F_fun(state,  dt, out_135664326016666632);
}
void car_h_25(double *state, double *unused, double *out_1339936627130384923) {
  h_25(state, unused, out_1339936627130384923);
}
void car_H_25(double *state, double *unused, double *out_8541205388556229655) {
  H_25(state, unused, out_8541205388556229655);
}
void car_h_24(double *state, double *unused, double *out_7843416543337357224) {
  h_24(state, unused, out_7843416543337357224);
}
void car_H_24(double *state, double *unused, double *out_4983279789753906519) {
  H_24(state, unused, out_4983279789753906519);
}
void car_h_30(double *state, double *unused, double *out_7253669653801133296) {
  h_30(state, unused, out_7253669653801133296);
}
void car_H_30(double *state, double *unused, double *out_6022872430048981028) {
  H_30(state, unused, out_6022872430048981028);
}
void car_h_26(double *state, double *unused, double *out_7856985538477610813) {
  h_26(state, unused, out_7856985538477610813);
}
void car_H_26(double *state, double *unused, double *out_5236679418795429054) {
  H_26(state, unused, out_5236679418795429054);
}
void car_h_27(double *state, double *unused, double *out_3661736640530460722) {
  h_27(state, unused, out_3661736640530460722);
}
void car_H_27(double *state, double *unused, double *out_3799278358865037811) {
  H_27(state, unused, out_3799278358865037811);
}
void car_h_29(double *state, double *unused, double *out_2211105247901577555) {
  h_29(state, unused, out_2211105247901577555);
}
void car_H_29(double *state, double *unused, double *out_5512641085734588844) {
  H_29(state, unused, out_5512641085734588844);
}
void car_h_28(double *state, double *unused, double *out_8663409908191306367) {
  h_28(state, unused, out_8663409908191306367);
}
void car_H_28(double *state, double *unused, double *out_7851703970905432198) {
  H_28(state, unused, out_7851703970905432198);
}
void car_h_31(double *state, double *unused, double *out_5201620103558886575) {
  h_31(state, unused, out_5201620103558886575);
}
void car_H_31(double *state, double *unused, double *out_1464530138044412402) {
  H_31(state, unused, out_1464530138044412402);
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

ekf_init(car);
