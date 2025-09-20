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
void err_fun(double *nom_x, double *delta_x, double *out_5951427109496666900) {
   out_5951427109496666900[0] = delta_x[0] + nom_x[0];
   out_5951427109496666900[1] = delta_x[1] + nom_x[1];
   out_5951427109496666900[2] = delta_x[2] + nom_x[2];
   out_5951427109496666900[3] = delta_x[3] + nom_x[3];
   out_5951427109496666900[4] = delta_x[4] + nom_x[4];
   out_5951427109496666900[5] = delta_x[5] + nom_x[5];
   out_5951427109496666900[6] = delta_x[6] + nom_x[6];
   out_5951427109496666900[7] = delta_x[7] + nom_x[7];
   out_5951427109496666900[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_3753933029986705763) {
   out_3753933029986705763[0] = -nom_x[0] + true_x[0];
   out_3753933029986705763[1] = -nom_x[1] + true_x[1];
   out_3753933029986705763[2] = -nom_x[2] + true_x[2];
   out_3753933029986705763[3] = -nom_x[3] + true_x[3];
   out_3753933029986705763[4] = -nom_x[4] + true_x[4];
   out_3753933029986705763[5] = -nom_x[5] + true_x[5];
   out_3753933029986705763[6] = -nom_x[6] + true_x[6];
   out_3753933029986705763[7] = -nom_x[7] + true_x[7];
   out_3753933029986705763[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_1598157310801926240) {
   out_1598157310801926240[0] = 1.0;
   out_1598157310801926240[1] = 0.0;
   out_1598157310801926240[2] = 0.0;
   out_1598157310801926240[3] = 0.0;
   out_1598157310801926240[4] = 0.0;
   out_1598157310801926240[5] = 0.0;
   out_1598157310801926240[6] = 0.0;
   out_1598157310801926240[7] = 0.0;
   out_1598157310801926240[8] = 0.0;
   out_1598157310801926240[9] = 0.0;
   out_1598157310801926240[10] = 1.0;
   out_1598157310801926240[11] = 0.0;
   out_1598157310801926240[12] = 0.0;
   out_1598157310801926240[13] = 0.0;
   out_1598157310801926240[14] = 0.0;
   out_1598157310801926240[15] = 0.0;
   out_1598157310801926240[16] = 0.0;
   out_1598157310801926240[17] = 0.0;
   out_1598157310801926240[18] = 0.0;
   out_1598157310801926240[19] = 0.0;
   out_1598157310801926240[20] = 1.0;
   out_1598157310801926240[21] = 0.0;
   out_1598157310801926240[22] = 0.0;
   out_1598157310801926240[23] = 0.0;
   out_1598157310801926240[24] = 0.0;
   out_1598157310801926240[25] = 0.0;
   out_1598157310801926240[26] = 0.0;
   out_1598157310801926240[27] = 0.0;
   out_1598157310801926240[28] = 0.0;
   out_1598157310801926240[29] = 0.0;
   out_1598157310801926240[30] = 1.0;
   out_1598157310801926240[31] = 0.0;
   out_1598157310801926240[32] = 0.0;
   out_1598157310801926240[33] = 0.0;
   out_1598157310801926240[34] = 0.0;
   out_1598157310801926240[35] = 0.0;
   out_1598157310801926240[36] = 0.0;
   out_1598157310801926240[37] = 0.0;
   out_1598157310801926240[38] = 0.0;
   out_1598157310801926240[39] = 0.0;
   out_1598157310801926240[40] = 1.0;
   out_1598157310801926240[41] = 0.0;
   out_1598157310801926240[42] = 0.0;
   out_1598157310801926240[43] = 0.0;
   out_1598157310801926240[44] = 0.0;
   out_1598157310801926240[45] = 0.0;
   out_1598157310801926240[46] = 0.0;
   out_1598157310801926240[47] = 0.0;
   out_1598157310801926240[48] = 0.0;
   out_1598157310801926240[49] = 0.0;
   out_1598157310801926240[50] = 1.0;
   out_1598157310801926240[51] = 0.0;
   out_1598157310801926240[52] = 0.0;
   out_1598157310801926240[53] = 0.0;
   out_1598157310801926240[54] = 0.0;
   out_1598157310801926240[55] = 0.0;
   out_1598157310801926240[56] = 0.0;
   out_1598157310801926240[57] = 0.0;
   out_1598157310801926240[58] = 0.0;
   out_1598157310801926240[59] = 0.0;
   out_1598157310801926240[60] = 1.0;
   out_1598157310801926240[61] = 0.0;
   out_1598157310801926240[62] = 0.0;
   out_1598157310801926240[63] = 0.0;
   out_1598157310801926240[64] = 0.0;
   out_1598157310801926240[65] = 0.0;
   out_1598157310801926240[66] = 0.0;
   out_1598157310801926240[67] = 0.0;
   out_1598157310801926240[68] = 0.0;
   out_1598157310801926240[69] = 0.0;
   out_1598157310801926240[70] = 1.0;
   out_1598157310801926240[71] = 0.0;
   out_1598157310801926240[72] = 0.0;
   out_1598157310801926240[73] = 0.0;
   out_1598157310801926240[74] = 0.0;
   out_1598157310801926240[75] = 0.0;
   out_1598157310801926240[76] = 0.0;
   out_1598157310801926240[77] = 0.0;
   out_1598157310801926240[78] = 0.0;
   out_1598157310801926240[79] = 0.0;
   out_1598157310801926240[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_5645298880168262869) {
   out_5645298880168262869[0] = state[0];
   out_5645298880168262869[1] = state[1];
   out_5645298880168262869[2] = state[2];
   out_5645298880168262869[3] = state[3];
   out_5645298880168262869[4] = state[4];
   out_5645298880168262869[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8100000000000005*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_5645298880168262869[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_5645298880168262869[7] = state[7];
   out_5645298880168262869[8] = state[8];
}
void F_fun(double *state, double dt, double *out_716541319675324393) {
   out_716541319675324393[0] = 1;
   out_716541319675324393[1] = 0;
   out_716541319675324393[2] = 0;
   out_716541319675324393[3] = 0;
   out_716541319675324393[4] = 0;
   out_716541319675324393[5] = 0;
   out_716541319675324393[6] = 0;
   out_716541319675324393[7] = 0;
   out_716541319675324393[8] = 0;
   out_716541319675324393[9] = 0;
   out_716541319675324393[10] = 1;
   out_716541319675324393[11] = 0;
   out_716541319675324393[12] = 0;
   out_716541319675324393[13] = 0;
   out_716541319675324393[14] = 0;
   out_716541319675324393[15] = 0;
   out_716541319675324393[16] = 0;
   out_716541319675324393[17] = 0;
   out_716541319675324393[18] = 0;
   out_716541319675324393[19] = 0;
   out_716541319675324393[20] = 1;
   out_716541319675324393[21] = 0;
   out_716541319675324393[22] = 0;
   out_716541319675324393[23] = 0;
   out_716541319675324393[24] = 0;
   out_716541319675324393[25] = 0;
   out_716541319675324393[26] = 0;
   out_716541319675324393[27] = 0;
   out_716541319675324393[28] = 0;
   out_716541319675324393[29] = 0;
   out_716541319675324393[30] = 1;
   out_716541319675324393[31] = 0;
   out_716541319675324393[32] = 0;
   out_716541319675324393[33] = 0;
   out_716541319675324393[34] = 0;
   out_716541319675324393[35] = 0;
   out_716541319675324393[36] = 0;
   out_716541319675324393[37] = 0;
   out_716541319675324393[38] = 0;
   out_716541319675324393[39] = 0;
   out_716541319675324393[40] = 1;
   out_716541319675324393[41] = 0;
   out_716541319675324393[42] = 0;
   out_716541319675324393[43] = 0;
   out_716541319675324393[44] = 0;
   out_716541319675324393[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_716541319675324393[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_716541319675324393[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_716541319675324393[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_716541319675324393[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_716541319675324393[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_716541319675324393[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_716541319675324393[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_716541319675324393[53] = -9.8100000000000005*dt;
   out_716541319675324393[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_716541319675324393[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_716541319675324393[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_716541319675324393[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_716541319675324393[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_716541319675324393[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_716541319675324393[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_716541319675324393[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_716541319675324393[62] = 0;
   out_716541319675324393[63] = 0;
   out_716541319675324393[64] = 0;
   out_716541319675324393[65] = 0;
   out_716541319675324393[66] = 0;
   out_716541319675324393[67] = 0;
   out_716541319675324393[68] = 0;
   out_716541319675324393[69] = 0;
   out_716541319675324393[70] = 1;
   out_716541319675324393[71] = 0;
   out_716541319675324393[72] = 0;
   out_716541319675324393[73] = 0;
   out_716541319675324393[74] = 0;
   out_716541319675324393[75] = 0;
   out_716541319675324393[76] = 0;
   out_716541319675324393[77] = 0;
   out_716541319675324393[78] = 0;
   out_716541319675324393[79] = 0;
   out_716541319675324393[80] = 1;
}
void h_25(double *state, double *unused, double *out_2904930533355629161) {
   out_2904930533355629161[0] = state[6];
}
void H_25(double *state, double *unused, double *out_1924823339187565437) {
   out_1924823339187565437[0] = 0;
   out_1924823339187565437[1] = 0;
   out_1924823339187565437[2] = 0;
   out_1924823339187565437[3] = 0;
   out_1924823339187565437[4] = 0;
   out_1924823339187565437[5] = 0;
   out_1924823339187565437[6] = 1;
   out_1924823339187565437[7] = 0;
   out_1924823339187565437[8] = 0;
}
void h_24(double *state, double *unused, double *out_8473448618580967526) {
   out_8473448618580967526[0] = state[4];
   out_8473448618580967526[1] = state[5];
}
void H_24(double *state, double *unused, double *out_2821685987778943597) {
   out_2821685987778943597[0] = 0;
   out_2821685987778943597[1] = 0;
   out_2821685987778943597[2] = 0;
   out_2821685987778943597[3] = 0;
   out_2821685987778943597[4] = 1;
   out_2821685987778943597[5] = 0;
   out_2821685987778943597[6] = 0;
   out_2821685987778943597[7] = 0;
   out_2821685987778943597[8] = 0;
   out_2821685987778943597[9] = 0;
   out_2821685987778943597[10] = 0;
   out_2821685987778943597[11] = 0;
   out_2821685987778943597[12] = 0;
   out_2821685987778943597[13] = 0;
   out_2821685987778943597[14] = 1;
   out_2821685987778943597[15] = 0;
   out_2821685987778943597[16] = 0;
   out_2821685987778943597[17] = 0;
}
void h_30(double *state, double *unused, double *out_5318829265255205330) {
   out_5318829265255205330[0] = state[4];
}
void H_30(double *state, double *unused, double *out_4443156297694814064) {
   out_4443156297694814064[0] = 0;
   out_4443156297694814064[1] = 0;
   out_4443156297694814064[2] = 0;
   out_4443156297694814064[3] = 0;
   out_4443156297694814064[4] = 1;
   out_4443156297694814064[5] = 0;
   out_4443156297694814064[6] = 0;
   out_4443156297694814064[7] = 0;
   out_4443156297694814064[8] = 0;
}
void h_26(double *state, double *unused, double *out_8867577960655567420) {
   out_8867577960655567420[0] = state[7];
}
void H_26(double *state, double *unused, double *out_1816679979686490787) {
   out_1816679979686490787[0] = 0;
   out_1816679979686490787[1] = 0;
   out_1816679979686490787[2] = 0;
   out_1816679979686490787[3] = 0;
   out_1816679979686490787[4] = 0;
   out_1816679979686490787[5] = 0;
   out_1816679979686490787[6] = 0;
   out_1816679979686490787[7] = 1;
   out_1816679979686490787[8] = 0;
}
void h_27(double *state, double *unused, double *out_1961420680453966726) {
   out_1961420680453966726[0] = state[3];
}
void H_27(double *state, double *unused, double *out_6666750368878757281) {
   out_6666750368878757281[0] = 0;
   out_6666750368878757281[1] = 0;
   out_6666750368878757281[2] = 0;
   out_6666750368878757281[3] = 1;
   out_6666750368878757281[4] = 0;
   out_6666750368878757281[5] = 0;
   out_6666750368878757281[6] = 0;
   out_6666750368878757281[7] = 0;
   out_6666750368878757281[8] = 0;
}
void h_29(double *state, double *unused, double *out_6678456796264575158) {
   out_6678456796264575158[0] = state[1];
}
void H_29(double *state, double *unused, double *out_4953387642009206248) {
   out_4953387642009206248[0] = 0;
   out_4953387642009206248[1] = 1;
   out_4953387642009206248[2] = 0;
   out_4953387642009206248[3] = 0;
   out_4953387642009206248[4] = 0;
   out_4953387642009206248[5] = 0;
   out_4953387642009206248[6] = 0;
   out_4953387642009206248[7] = 0;
   out_4953387642009206248[8] = 0;
}
void h_28(double *state, double *unused, double *out_2320143160789693782) {
   out_2320143160789693782[0] = state[0];
}
void H_28(double *state, double *unused, double *out_129011375060324326) {
   out_129011375060324326[0] = 1;
   out_129011375060324326[1] = 0;
   out_129011375060324326[2] = 0;
   out_129011375060324326[3] = 0;
   out_129011375060324326[4] = 0;
   out_129011375060324326[5] = 0;
   out_129011375060324326[6] = 0;
   out_129011375060324326[7] = 0;
   out_129011375060324326[8] = 0;
}
void h_31(double *state, double *unused, double *out_8354860635895864126) {
   out_8354860635895864126[0] = state[8];
}
void H_31(double *state, double *unused, double *out_1955469301064525865) {
   out_1955469301064525865[0] = 0;
   out_1955469301064525865[1] = 0;
   out_1955469301064525865[2] = 0;
   out_1955469301064525865[3] = 0;
   out_1955469301064525865[4] = 0;
   out_1955469301064525865[5] = 0;
   out_1955469301064525865[6] = 0;
   out_1955469301064525865[7] = 0;
   out_1955469301064525865[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_5951427109496666900) {
  err_fun(nom_x, delta_x, out_5951427109496666900);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_3753933029986705763) {
  inv_err_fun(nom_x, true_x, out_3753933029986705763);
}
void car_H_mod_fun(double *state, double *out_1598157310801926240) {
  H_mod_fun(state, out_1598157310801926240);
}
void car_f_fun(double *state, double dt, double *out_5645298880168262869) {
  f_fun(state,  dt, out_5645298880168262869);
}
void car_F_fun(double *state, double dt, double *out_716541319675324393) {
  F_fun(state,  dt, out_716541319675324393);
}
void car_h_25(double *state, double *unused, double *out_2904930533355629161) {
  h_25(state, unused, out_2904930533355629161);
}
void car_H_25(double *state, double *unused, double *out_1924823339187565437) {
  H_25(state, unused, out_1924823339187565437);
}
void car_h_24(double *state, double *unused, double *out_8473448618580967526) {
  h_24(state, unused, out_8473448618580967526);
}
void car_H_24(double *state, double *unused, double *out_2821685987778943597) {
  H_24(state, unused, out_2821685987778943597);
}
void car_h_30(double *state, double *unused, double *out_5318829265255205330) {
  h_30(state, unused, out_5318829265255205330);
}
void car_H_30(double *state, double *unused, double *out_4443156297694814064) {
  H_30(state, unused, out_4443156297694814064);
}
void car_h_26(double *state, double *unused, double *out_8867577960655567420) {
  h_26(state, unused, out_8867577960655567420);
}
void car_H_26(double *state, double *unused, double *out_1816679979686490787) {
  H_26(state, unused, out_1816679979686490787);
}
void car_h_27(double *state, double *unused, double *out_1961420680453966726) {
  h_27(state, unused, out_1961420680453966726);
}
void car_H_27(double *state, double *unused, double *out_6666750368878757281) {
  H_27(state, unused, out_6666750368878757281);
}
void car_h_29(double *state, double *unused, double *out_6678456796264575158) {
  h_29(state, unused, out_6678456796264575158);
}
void car_H_29(double *state, double *unused, double *out_4953387642009206248) {
  H_29(state, unused, out_4953387642009206248);
}
void car_h_28(double *state, double *unused, double *out_2320143160789693782) {
  h_28(state, unused, out_2320143160789693782);
}
void car_H_28(double *state, double *unused, double *out_129011375060324326) {
  H_28(state, unused, out_129011375060324326);
}
void car_h_31(double *state, double *unused, double *out_8354860635895864126) {
  h_31(state, unused, out_8354860635895864126);
}
void car_H_31(double *state, double *unused, double *out_1955469301064525865) {
  H_31(state, unused, out_1955469301064525865);
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
