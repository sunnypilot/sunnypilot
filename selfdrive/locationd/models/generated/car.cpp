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
void err_fun(double *nom_x, double *delta_x, double *out_810329987946403557) {
   out_810329987946403557[0] = delta_x[0] + nom_x[0];
   out_810329987946403557[1] = delta_x[1] + nom_x[1];
   out_810329987946403557[2] = delta_x[2] + nom_x[2];
   out_810329987946403557[3] = delta_x[3] + nom_x[3];
   out_810329987946403557[4] = delta_x[4] + nom_x[4];
   out_810329987946403557[5] = delta_x[5] + nom_x[5];
   out_810329987946403557[6] = delta_x[6] + nom_x[6];
   out_810329987946403557[7] = delta_x[7] + nom_x[7];
   out_810329987946403557[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_5716896811801670801) {
   out_5716896811801670801[0] = -nom_x[0] + true_x[0];
   out_5716896811801670801[1] = -nom_x[1] + true_x[1];
   out_5716896811801670801[2] = -nom_x[2] + true_x[2];
   out_5716896811801670801[3] = -nom_x[3] + true_x[3];
   out_5716896811801670801[4] = -nom_x[4] + true_x[4];
   out_5716896811801670801[5] = -nom_x[5] + true_x[5];
   out_5716896811801670801[6] = -nom_x[6] + true_x[6];
   out_5716896811801670801[7] = -nom_x[7] + true_x[7];
   out_5716896811801670801[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_4260664193875322727) {
   out_4260664193875322727[0] = 1.0;
   out_4260664193875322727[1] = 0;
   out_4260664193875322727[2] = 0;
   out_4260664193875322727[3] = 0;
   out_4260664193875322727[4] = 0;
   out_4260664193875322727[5] = 0;
   out_4260664193875322727[6] = 0;
   out_4260664193875322727[7] = 0;
   out_4260664193875322727[8] = 0;
   out_4260664193875322727[9] = 0;
   out_4260664193875322727[10] = 1.0;
   out_4260664193875322727[11] = 0;
   out_4260664193875322727[12] = 0;
   out_4260664193875322727[13] = 0;
   out_4260664193875322727[14] = 0;
   out_4260664193875322727[15] = 0;
   out_4260664193875322727[16] = 0;
   out_4260664193875322727[17] = 0;
   out_4260664193875322727[18] = 0;
   out_4260664193875322727[19] = 0;
   out_4260664193875322727[20] = 1.0;
   out_4260664193875322727[21] = 0;
   out_4260664193875322727[22] = 0;
   out_4260664193875322727[23] = 0;
   out_4260664193875322727[24] = 0;
   out_4260664193875322727[25] = 0;
   out_4260664193875322727[26] = 0;
   out_4260664193875322727[27] = 0;
   out_4260664193875322727[28] = 0;
   out_4260664193875322727[29] = 0;
   out_4260664193875322727[30] = 1.0;
   out_4260664193875322727[31] = 0;
   out_4260664193875322727[32] = 0;
   out_4260664193875322727[33] = 0;
   out_4260664193875322727[34] = 0;
   out_4260664193875322727[35] = 0;
   out_4260664193875322727[36] = 0;
   out_4260664193875322727[37] = 0;
   out_4260664193875322727[38] = 0;
   out_4260664193875322727[39] = 0;
   out_4260664193875322727[40] = 1.0;
   out_4260664193875322727[41] = 0;
   out_4260664193875322727[42] = 0;
   out_4260664193875322727[43] = 0;
   out_4260664193875322727[44] = 0;
   out_4260664193875322727[45] = 0;
   out_4260664193875322727[46] = 0;
   out_4260664193875322727[47] = 0;
   out_4260664193875322727[48] = 0;
   out_4260664193875322727[49] = 0;
   out_4260664193875322727[50] = 1.0;
   out_4260664193875322727[51] = 0;
   out_4260664193875322727[52] = 0;
   out_4260664193875322727[53] = 0;
   out_4260664193875322727[54] = 0;
   out_4260664193875322727[55] = 0;
   out_4260664193875322727[56] = 0;
   out_4260664193875322727[57] = 0;
   out_4260664193875322727[58] = 0;
   out_4260664193875322727[59] = 0;
   out_4260664193875322727[60] = 1.0;
   out_4260664193875322727[61] = 0;
   out_4260664193875322727[62] = 0;
   out_4260664193875322727[63] = 0;
   out_4260664193875322727[64] = 0;
   out_4260664193875322727[65] = 0;
   out_4260664193875322727[66] = 0;
   out_4260664193875322727[67] = 0;
   out_4260664193875322727[68] = 0;
   out_4260664193875322727[69] = 0;
   out_4260664193875322727[70] = 1.0;
   out_4260664193875322727[71] = 0;
   out_4260664193875322727[72] = 0;
   out_4260664193875322727[73] = 0;
   out_4260664193875322727[74] = 0;
   out_4260664193875322727[75] = 0;
   out_4260664193875322727[76] = 0;
   out_4260664193875322727[77] = 0;
   out_4260664193875322727[78] = 0;
   out_4260664193875322727[79] = 0;
   out_4260664193875322727[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_1338751046029408378) {
   out_1338751046029408378[0] = state[0];
   out_1338751046029408378[1] = state[1];
   out_1338751046029408378[2] = state[2];
   out_1338751046029408378[3] = state[3];
   out_1338751046029408378[4] = state[4];
   out_1338751046029408378[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8000000000000007*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_1338751046029408378[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_1338751046029408378[7] = state[7];
   out_1338751046029408378[8] = state[8];
}
void F_fun(double *state, double dt, double *out_5413251715551156627) {
   out_5413251715551156627[0] = 1;
   out_5413251715551156627[1] = 0;
   out_5413251715551156627[2] = 0;
   out_5413251715551156627[3] = 0;
   out_5413251715551156627[4] = 0;
   out_5413251715551156627[5] = 0;
   out_5413251715551156627[6] = 0;
   out_5413251715551156627[7] = 0;
   out_5413251715551156627[8] = 0;
   out_5413251715551156627[9] = 0;
   out_5413251715551156627[10] = 1;
   out_5413251715551156627[11] = 0;
   out_5413251715551156627[12] = 0;
   out_5413251715551156627[13] = 0;
   out_5413251715551156627[14] = 0;
   out_5413251715551156627[15] = 0;
   out_5413251715551156627[16] = 0;
   out_5413251715551156627[17] = 0;
   out_5413251715551156627[18] = 0;
   out_5413251715551156627[19] = 0;
   out_5413251715551156627[20] = 1;
   out_5413251715551156627[21] = 0;
   out_5413251715551156627[22] = 0;
   out_5413251715551156627[23] = 0;
   out_5413251715551156627[24] = 0;
   out_5413251715551156627[25] = 0;
   out_5413251715551156627[26] = 0;
   out_5413251715551156627[27] = 0;
   out_5413251715551156627[28] = 0;
   out_5413251715551156627[29] = 0;
   out_5413251715551156627[30] = 1;
   out_5413251715551156627[31] = 0;
   out_5413251715551156627[32] = 0;
   out_5413251715551156627[33] = 0;
   out_5413251715551156627[34] = 0;
   out_5413251715551156627[35] = 0;
   out_5413251715551156627[36] = 0;
   out_5413251715551156627[37] = 0;
   out_5413251715551156627[38] = 0;
   out_5413251715551156627[39] = 0;
   out_5413251715551156627[40] = 1;
   out_5413251715551156627[41] = 0;
   out_5413251715551156627[42] = 0;
   out_5413251715551156627[43] = 0;
   out_5413251715551156627[44] = 0;
   out_5413251715551156627[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_5413251715551156627[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_5413251715551156627[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_5413251715551156627[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_5413251715551156627[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_5413251715551156627[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_5413251715551156627[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_5413251715551156627[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_5413251715551156627[53] = -9.8000000000000007*dt;
   out_5413251715551156627[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_5413251715551156627[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_5413251715551156627[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_5413251715551156627[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_5413251715551156627[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_5413251715551156627[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_5413251715551156627[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_5413251715551156627[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_5413251715551156627[62] = 0;
   out_5413251715551156627[63] = 0;
   out_5413251715551156627[64] = 0;
   out_5413251715551156627[65] = 0;
   out_5413251715551156627[66] = 0;
   out_5413251715551156627[67] = 0;
   out_5413251715551156627[68] = 0;
   out_5413251715551156627[69] = 0;
   out_5413251715551156627[70] = 1;
   out_5413251715551156627[71] = 0;
   out_5413251715551156627[72] = 0;
   out_5413251715551156627[73] = 0;
   out_5413251715551156627[74] = 0;
   out_5413251715551156627[75] = 0;
   out_5413251715551156627[76] = 0;
   out_5413251715551156627[77] = 0;
   out_5413251715551156627[78] = 0;
   out_5413251715551156627[79] = 0;
   out_5413251715551156627[80] = 1;
}
void h_25(double *state, double *unused, double *out_124630543568800147) {
   out_124630543568800147[0] = state[6];
}
void H_25(double *state, double *unused, double *out_4993281568702638206) {
   out_4993281568702638206[0] = 0;
   out_4993281568702638206[1] = 0;
   out_4993281568702638206[2] = 0;
   out_4993281568702638206[3] = 0;
   out_4993281568702638206[4] = 0;
   out_4993281568702638206[5] = 0;
   out_4993281568702638206[6] = 1;
   out_4993281568702638206[7] = 0;
   out_4993281568702638206[8] = 0;
}
void h_24(double *state, double *unused, double *out_8120860186226682358) {
   out_8120860186226682358[0] = state[4];
   out_8120860186226682358[1] = state[5];
}
void H_24(double *state, double *unused, double *out_2820631969697138640) {
   out_2820631969697138640[0] = 0;
   out_2820631969697138640[1] = 0;
   out_2820631969697138640[2] = 0;
   out_2820631969697138640[3] = 0;
   out_2820631969697138640[4] = 1;
   out_2820631969697138640[5] = 0;
   out_2820631969697138640[6] = 0;
   out_2820631969697138640[7] = 0;
   out_2820631969697138640[8] = 0;
   out_2820631969697138640[9] = 0;
   out_2820631969697138640[10] = 0;
   out_2820631969697138640[11] = 0;
   out_2820631969697138640[12] = 0;
   out_2820631969697138640[13] = 0;
   out_2820631969697138640[14] = 1;
   out_2820631969697138640[15] = 0;
   out_2820631969697138640[16] = 0;
   out_2820631969697138640[17] = 0;
}
void h_30(double *state, double *unused, double *out_3072356533924285108) {
   out_3072356533924285108[0] = state[4];
}
void H_30(double *state, double *unused, double *out_7511614527209886833) {
   out_7511614527209886833[0] = 0;
   out_7511614527209886833[1] = 0;
   out_7511614527209886833[2] = 0;
   out_7511614527209886833[3] = 0;
   out_7511614527209886833[4] = 1;
   out_7511614527209886833[5] = 0;
   out_7511614527209886833[6] = 0;
   out_7511614527209886833[7] = 0;
   out_7511614527209886833[8] = 0;
}
void h_26(double *state, double *unused, double *out_2090272440588986996) {
   out_2090272440588986996[0] = state[7];
}
void H_26(double *state, double *unused, double *out_1251778249828581982) {
   out_1251778249828581982[0] = 0;
   out_1251778249828581982[1] = 0;
   out_1251778249828581982[2] = 0;
   out_1251778249828581982[3] = 0;
   out_1251778249828581982[4] = 0;
   out_1251778249828581982[5] = 0;
   out_1251778249828581982[6] = 0;
   out_1251778249828581982[7] = 1;
   out_1251778249828581982[8] = 0;
}
void h_27(double *state, double *unused, double *out_5126303811229645792) {
   out_5126303811229645792[0] = state[3];
}
void H_27(double *state, double *unused, double *out_5336851215409461922) {
   out_5336851215409461922[0] = 0;
   out_5336851215409461922[1] = 0;
   out_5336851215409461922[2] = 0;
   out_5336851215409461922[3] = 1;
   out_5336851215409461922[4] = 0;
   out_5336851215409461922[5] = 0;
   out_5336851215409461922[6] = 0;
   out_5336851215409461922[7] = 0;
   out_5336851215409461922[8] = 0;
}
void h_29(double *state, double *unused, double *out_3675672418600762625) {
   out_3675672418600762625[0] = state[1];
}
void H_29(double *state, double *unused, double *out_8021845871524279017) {
   out_8021845871524279017[0] = 0;
   out_8021845871524279017[1] = 1;
   out_8021845871524279017[2] = 0;
   out_8021845871524279017[3] = 0;
   out_8021845871524279017[4] = 0;
   out_8021845871524279017[5] = 0;
   out_8021845871524279017[6] = 0;
   out_8021845871524279017[7] = 0;
   out_8021845871524279017[8] = 0;
}
void h_28(double *state, double *unused, double *out_8258220002250123303) {
   out_8258220002250123303[0] = state[0];
}
void H_28(double *state, double *unused, double *out_2939446854454748443) {
   out_2939446854454748443[0] = 1;
   out_2939446854454748443[1] = 0;
   out_2939446854454748443[2] = 0;
   out_2939446854454748443[3] = 0;
   out_2939446854454748443[4] = 0;
   out_2939446854454748443[5] = 0;
   out_2939446854454748443[6] = 0;
   out_2939446854454748443[7] = 0;
   out_2939446854454748443[8] = 0;
}
void h_31(double *state, double *unused, double *out_7756642107185249038) {
   out_7756642107185249038[0] = state[8];
}
void H_31(double *state, double *unused, double *out_625570147595230506) {
   out_625570147595230506[0] = 0;
   out_625570147595230506[1] = 0;
   out_625570147595230506[2] = 0;
   out_625570147595230506[3] = 0;
   out_625570147595230506[4] = 0;
   out_625570147595230506[5] = 0;
   out_625570147595230506[6] = 0;
   out_625570147595230506[7] = 0;
   out_625570147595230506[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_810329987946403557) {
  err_fun(nom_x, delta_x, out_810329987946403557);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_5716896811801670801) {
  inv_err_fun(nom_x, true_x, out_5716896811801670801);
}
void car_H_mod_fun(double *state, double *out_4260664193875322727) {
  H_mod_fun(state, out_4260664193875322727);
}
void car_f_fun(double *state, double dt, double *out_1338751046029408378) {
  f_fun(state,  dt, out_1338751046029408378);
}
void car_F_fun(double *state, double dt, double *out_5413251715551156627) {
  F_fun(state,  dt, out_5413251715551156627);
}
void car_h_25(double *state, double *unused, double *out_124630543568800147) {
  h_25(state, unused, out_124630543568800147);
}
void car_H_25(double *state, double *unused, double *out_4993281568702638206) {
  H_25(state, unused, out_4993281568702638206);
}
void car_h_24(double *state, double *unused, double *out_8120860186226682358) {
  h_24(state, unused, out_8120860186226682358);
}
void car_H_24(double *state, double *unused, double *out_2820631969697138640) {
  H_24(state, unused, out_2820631969697138640);
}
void car_h_30(double *state, double *unused, double *out_3072356533924285108) {
  h_30(state, unused, out_3072356533924285108);
}
void car_H_30(double *state, double *unused, double *out_7511614527209886833) {
  H_30(state, unused, out_7511614527209886833);
}
void car_h_26(double *state, double *unused, double *out_2090272440588986996) {
  h_26(state, unused, out_2090272440588986996);
}
void car_H_26(double *state, double *unused, double *out_1251778249828581982) {
  H_26(state, unused, out_1251778249828581982);
}
void car_h_27(double *state, double *unused, double *out_5126303811229645792) {
  h_27(state, unused, out_5126303811229645792);
}
void car_H_27(double *state, double *unused, double *out_5336851215409461922) {
  H_27(state, unused, out_5336851215409461922);
}
void car_h_29(double *state, double *unused, double *out_3675672418600762625) {
  h_29(state, unused, out_3675672418600762625);
}
void car_H_29(double *state, double *unused, double *out_8021845871524279017) {
  H_29(state, unused, out_8021845871524279017);
}
void car_h_28(double *state, double *unused, double *out_8258220002250123303) {
  h_28(state, unused, out_8258220002250123303);
}
void car_H_28(double *state, double *unused, double *out_2939446854454748443) {
  H_28(state, unused, out_2939446854454748443);
}
void car_h_31(double *state, double *unused, double *out_7756642107185249038) {
  h_31(state, unused, out_7756642107185249038);
}
void car_H_31(double *state, double *unused, double *out_625570147595230506) {
  H_31(state, unused, out_625570147595230506);
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
