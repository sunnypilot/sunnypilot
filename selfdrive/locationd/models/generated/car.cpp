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
void err_fun(double *nom_x, double *delta_x, double *out_4404972482043756320) {
   out_4404972482043756320[0] = delta_x[0] + nom_x[0];
   out_4404972482043756320[1] = delta_x[1] + nom_x[1];
   out_4404972482043756320[2] = delta_x[2] + nom_x[2];
   out_4404972482043756320[3] = delta_x[3] + nom_x[3];
   out_4404972482043756320[4] = delta_x[4] + nom_x[4];
   out_4404972482043756320[5] = delta_x[5] + nom_x[5];
   out_4404972482043756320[6] = delta_x[6] + nom_x[6];
   out_4404972482043756320[7] = delta_x[7] + nom_x[7];
   out_4404972482043756320[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_1878142591409797047) {
   out_1878142591409797047[0] = -nom_x[0] + true_x[0];
   out_1878142591409797047[1] = -nom_x[1] + true_x[1];
   out_1878142591409797047[2] = -nom_x[2] + true_x[2];
   out_1878142591409797047[3] = -nom_x[3] + true_x[3];
   out_1878142591409797047[4] = -nom_x[4] + true_x[4];
   out_1878142591409797047[5] = -nom_x[5] + true_x[5];
   out_1878142591409797047[6] = -nom_x[6] + true_x[6];
   out_1878142591409797047[7] = -nom_x[7] + true_x[7];
   out_1878142591409797047[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_8303006938306786866) {
   out_8303006938306786866[0] = 1.0;
   out_8303006938306786866[1] = 0;
   out_8303006938306786866[2] = 0;
   out_8303006938306786866[3] = 0;
   out_8303006938306786866[4] = 0;
   out_8303006938306786866[5] = 0;
   out_8303006938306786866[6] = 0;
   out_8303006938306786866[7] = 0;
   out_8303006938306786866[8] = 0;
   out_8303006938306786866[9] = 0;
   out_8303006938306786866[10] = 1.0;
   out_8303006938306786866[11] = 0;
   out_8303006938306786866[12] = 0;
   out_8303006938306786866[13] = 0;
   out_8303006938306786866[14] = 0;
   out_8303006938306786866[15] = 0;
   out_8303006938306786866[16] = 0;
   out_8303006938306786866[17] = 0;
   out_8303006938306786866[18] = 0;
   out_8303006938306786866[19] = 0;
   out_8303006938306786866[20] = 1.0;
   out_8303006938306786866[21] = 0;
   out_8303006938306786866[22] = 0;
   out_8303006938306786866[23] = 0;
   out_8303006938306786866[24] = 0;
   out_8303006938306786866[25] = 0;
   out_8303006938306786866[26] = 0;
   out_8303006938306786866[27] = 0;
   out_8303006938306786866[28] = 0;
   out_8303006938306786866[29] = 0;
   out_8303006938306786866[30] = 1.0;
   out_8303006938306786866[31] = 0;
   out_8303006938306786866[32] = 0;
   out_8303006938306786866[33] = 0;
   out_8303006938306786866[34] = 0;
   out_8303006938306786866[35] = 0;
   out_8303006938306786866[36] = 0;
   out_8303006938306786866[37] = 0;
   out_8303006938306786866[38] = 0;
   out_8303006938306786866[39] = 0;
   out_8303006938306786866[40] = 1.0;
   out_8303006938306786866[41] = 0;
   out_8303006938306786866[42] = 0;
   out_8303006938306786866[43] = 0;
   out_8303006938306786866[44] = 0;
   out_8303006938306786866[45] = 0;
   out_8303006938306786866[46] = 0;
   out_8303006938306786866[47] = 0;
   out_8303006938306786866[48] = 0;
   out_8303006938306786866[49] = 0;
   out_8303006938306786866[50] = 1.0;
   out_8303006938306786866[51] = 0;
   out_8303006938306786866[52] = 0;
   out_8303006938306786866[53] = 0;
   out_8303006938306786866[54] = 0;
   out_8303006938306786866[55] = 0;
   out_8303006938306786866[56] = 0;
   out_8303006938306786866[57] = 0;
   out_8303006938306786866[58] = 0;
   out_8303006938306786866[59] = 0;
   out_8303006938306786866[60] = 1.0;
   out_8303006938306786866[61] = 0;
   out_8303006938306786866[62] = 0;
   out_8303006938306786866[63] = 0;
   out_8303006938306786866[64] = 0;
   out_8303006938306786866[65] = 0;
   out_8303006938306786866[66] = 0;
   out_8303006938306786866[67] = 0;
   out_8303006938306786866[68] = 0;
   out_8303006938306786866[69] = 0;
   out_8303006938306786866[70] = 1.0;
   out_8303006938306786866[71] = 0;
   out_8303006938306786866[72] = 0;
   out_8303006938306786866[73] = 0;
   out_8303006938306786866[74] = 0;
   out_8303006938306786866[75] = 0;
   out_8303006938306786866[76] = 0;
   out_8303006938306786866[77] = 0;
   out_8303006938306786866[78] = 0;
   out_8303006938306786866[79] = 0;
   out_8303006938306786866[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_4068599896429511203) {
   out_4068599896429511203[0] = state[0];
   out_4068599896429511203[1] = state[1];
   out_4068599896429511203[2] = state[2];
   out_4068599896429511203[3] = state[3];
   out_4068599896429511203[4] = state[4];
   out_4068599896429511203[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8000000000000007*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_4068599896429511203[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_4068599896429511203[7] = state[7];
   out_4068599896429511203[8] = state[8];
}
void F_fun(double *state, double dt, double *out_6707421618485807550) {
   out_6707421618485807550[0] = 1;
   out_6707421618485807550[1] = 0;
   out_6707421618485807550[2] = 0;
   out_6707421618485807550[3] = 0;
   out_6707421618485807550[4] = 0;
   out_6707421618485807550[5] = 0;
   out_6707421618485807550[6] = 0;
   out_6707421618485807550[7] = 0;
   out_6707421618485807550[8] = 0;
   out_6707421618485807550[9] = 0;
   out_6707421618485807550[10] = 1;
   out_6707421618485807550[11] = 0;
   out_6707421618485807550[12] = 0;
   out_6707421618485807550[13] = 0;
   out_6707421618485807550[14] = 0;
   out_6707421618485807550[15] = 0;
   out_6707421618485807550[16] = 0;
   out_6707421618485807550[17] = 0;
   out_6707421618485807550[18] = 0;
   out_6707421618485807550[19] = 0;
   out_6707421618485807550[20] = 1;
   out_6707421618485807550[21] = 0;
   out_6707421618485807550[22] = 0;
   out_6707421618485807550[23] = 0;
   out_6707421618485807550[24] = 0;
   out_6707421618485807550[25] = 0;
   out_6707421618485807550[26] = 0;
   out_6707421618485807550[27] = 0;
   out_6707421618485807550[28] = 0;
   out_6707421618485807550[29] = 0;
   out_6707421618485807550[30] = 1;
   out_6707421618485807550[31] = 0;
   out_6707421618485807550[32] = 0;
   out_6707421618485807550[33] = 0;
   out_6707421618485807550[34] = 0;
   out_6707421618485807550[35] = 0;
   out_6707421618485807550[36] = 0;
   out_6707421618485807550[37] = 0;
   out_6707421618485807550[38] = 0;
   out_6707421618485807550[39] = 0;
   out_6707421618485807550[40] = 1;
   out_6707421618485807550[41] = 0;
   out_6707421618485807550[42] = 0;
   out_6707421618485807550[43] = 0;
   out_6707421618485807550[44] = 0;
   out_6707421618485807550[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_6707421618485807550[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_6707421618485807550[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_6707421618485807550[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_6707421618485807550[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_6707421618485807550[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_6707421618485807550[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_6707421618485807550[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_6707421618485807550[53] = -9.8000000000000007*dt;
   out_6707421618485807550[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_6707421618485807550[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_6707421618485807550[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_6707421618485807550[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_6707421618485807550[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_6707421618485807550[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_6707421618485807550[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_6707421618485807550[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_6707421618485807550[62] = 0;
   out_6707421618485807550[63] = 0;
   out_6707421618485807550[64] = 0;
   out_6707421618485807550[65] = 0;
   out_6707421618485807550[66] = 0;
   out_6707421618485807550[67] = 0;
   out_6707421618485807550[68] = 0;
   out_6707421618485807550[69] = 0;
   out_6707421618485807550[70] = 1;
   out_6707421618485807550[71] = 0;
   out_6707421618485807550[72] = 0;
   out_6707421618485807550[73] = 0;
   out_6707421618485807550[74] = 0;
   out_6707421618485807550[75] = 0;
   out_6707421618485807550[76] = 0;
   out_6707421618485807550[77] = 0;
   out_6707421618485807550[78] = 0;
   out_6707421618485807550[79] = 0;
   out_6707421618485807550[80] = 1;
}
void h_25(double *state, double *unused, double *out_6170927995150476655) {
   out_6170927995150476655[0] = state[6];
}
void H_25(double *state, double *unused, double *out_1911527141633227669) {
   out_1911527141633227669[0] = 0;
   out_1911527141633227669[1] = 0;
   out_1911527141633227669[2] = 0;
   out_1911527141633227669[3] = 0;
   out_1911527141633227669[4] = 0;
   out_1911527141633227669[5] = 0;
   out_1911527141633227669[6] = 1;
   out_1911527141633227669[7] = 0;
   out_1911527141633227669[8] = 0;
}
void h_24(double *state, double *unused, double *out_5813330457683306165) {
   out_5813330457683306165[0] = state[4];
   out_5813330457683306165[1] = state[5];
}
void H_24(double *state, double *unused, double *out_498498893594818832) {
   out_498498893594818832[0] = 0;
   out_498498893594818832[1] = 0;
   out_498498893594818832[2] = 0;
   out_498498893594818832[3] = 0;
   out_498498893594818832[4] = 1;
   out_498498893594818832[5] = 0;
   out_498498893594818832[6] = 0;
   out_498498893594818832[7] = 0;
   out_498498893594818832[8] = 0;
   out_498498893594818832[9] = 0;
   out_498498893594818832[10] = 0;
   out_498498893594818832[11] = 0;
   out_498498893594818832[12] = 0;
   out_498498893594818832[13] = 0;
   out_498498893594818832[14] = 1;
   out_498498893594818832[15] = 0;
   out_498498893594818832[16] = 0;
   out_498498893594818832[17] = 0;
}
void h_30(double *state, double *unused, double *out_5895733932865970766) {
   out_5895733932865970766[0] = state[4];
}
void H_30(double *state, double *unused, double *out_606805816874020958) {
   out_606805816874020958[0] = 0;
   out_606805816874020958[1] = 0;
   out_606805816874020958[2] = 0;
   out_606805816874020958[3] = 0;
   out_606805816874020958[4] = 1;
   out_606805816874020958[5] = 0;
   out_606805816874020958[6] = 0;
   out_606805816874020958[7] = 0;
   out_606805816874020958[8] = 0;
}
void h_26(double *state, double *unused, double *out_4205286098130289806) {
   out_4205286098130289806[0] = state[7];
}
void H_26(double *state, double *unused, double *out_5653030460507283893) {
   out_5653030460507283893[0] = 0;
   out_5653030460507283893[1] = 0;
   out_5653030460507283893[2] = 0;
   out_5653030460507283893[3] = 0;
   out_5653030460507283893[4] = 0;
   out_5653030460507283893[5] = 0;
   out_5653030460507283893[6] = 0;
   out_5653030460507283893[7] = 1;
   out_5653030460507283893[8] = 0;
}
void h_27(double *state, double *unused, double *out_1169254727489631010) {
   out_1169254727489631010[0] = state[3];
}
void H_27(double *state, double *unused, double *out_1567957494926403953) {
   out_1567957494926403953[0] = 0;
   out_1567957494926403953[1] = 0;
   out_1567957494926403953[2] = 0;
   out_1567957494926403953[3] = 1;
   out_1567957494926403953[4] = 0;
   out_1567957494926403953[5] = 0;
   out_1567957494926403953[6] = 0;
   out_1567957494926403953[7] = 0;
   out_1567957494926403953[8] = 0;
}
void h_29(double *state, double *unused, double *out_894060665205125121) {
   out_894060665205125121[0] = state[1];
}
void H_29(double *state, double *unused, double *out_1117037161188413142) {
   out_1117037161188413142[0] = 0;
   out_1117037161188413142[1] = 1;
   out_1117037161188413142[2] = 0;
   out_1117037161188413142[3] = 0;
   out_1117037161188413142[4] = 0;
   out_1117037161188413142[5] = 0;
   out_1117037161188413142[6] = 0;
   out_1117037161188413142[7] = 0;
   out_1117037161188413142[8] = 0;
}
void h_28(double *state, double *unused, double *out_2112764580391293445) {
   out_2112764580391293445[0] = state[0];
}
void H_28(double *state, double *unused, double *out_3965361855881117432) {
   out_3965361855881117432[0] = 1;
   out_3965361855881117432[1] = 0;
   out_3965361855881117432[2] = 0;
   out_3965361855881117432[3] = 0;
   out_3965361855881117432[4] = 0;
   out_3965361855881117432[5] = 0;
   out_3965361855881117432[6] = 0;
   out_3965361855881117432[7] = 0;
   out_3965361855881117432[8] = 0;
}
void h_31(double *state, double *unused, double *out_6013741326799347510) {
   out_6013741326799347510[0] = state[8];
}
void H_31(double *state, double *unused, double *out_6279238562740635369) {
   out_6279238562740635369[0] = 0;
   out_6279238562740635369[1] = 0;
   out_6279238562740635369[2] = 0;
   out_6279238562740635369[3] = 0;
   out_6279238562740635369[4] = 0;
   out_6279238562740635369[5] = 0;
   out_6279238562740635369[6] = 0;
   out_6279238562740635369[7] = 0;
   out_6279238562740635369[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_4404972482043756320) {
  err_fun(nom_x, delta_x, out_4404972482043756320);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_1878142591409797047) {
  inv_err_fun(nom_x, true_x, out_1878142591409797047);
}
void car_H_mod_fun(double *state, double *out_8303006938306786866) {
  H_mod_fun(state, out_8303006938306786866);
}
void car_f_fun(double *state, double dt, double *out_4068599896429511203) {
  f_fun(state,  dt, out_4068599896429511203);
}
void car_F_fun(double *state, double dt, double *out_6707421618485807550) {
  F_fun(state,  dt, out_6707421618485807550);
}
void car_h_25(double *state, double *unused, double *out_6170927995150476655) {
  h_25(state, unused, out_6170927995150476655);
}
void car_H_25(double *state, double *unused, double *out_1911527141633227669) {
  H_25(state, unused, out_1911527141633227669);
}
void car_h_24(double *state, double *unused, double *out_5813330457683306165) {
  h_24(state, unused, out_5813330457683306165);
}
void car_H_24(double *state, double *unused, double *out_498498893594818832) {
  H_24(state, unused, out_498498893594818832);
}
void car_h_30(double *state, double *unused, double *out_5895733932865970766) {
  h_30(state, unused, out_5895733932865970766);
}
void car_H_30(double *state, double *unused, double *out_606805816874020958) {
  H_30(state, unused, out_606805816874020958);
}
void car_h_26(double *state, double *unused, double *out_4205286098130289806) {
  h_26(state, unused, out_4205286098130289806);
}
void car_H_26(double *state, double *unused, double *out_5653030460507283893) {
  H_26(state, unused, out_5653030460507283893);
}
void car_h_27(double *state, double *unused, double *out_1169254727489631010) {
  h_27(state, unused, out_1169254727489631010);
}
void car_H_27(double *state, double *unused, double *out_1567957494926403953) {
  H_27(state, unused, out_1567957494926403953);
}
void car_h_29(double *state, double *unused, double *out_894060665205125121) {
  h_29(state, unused, out_894060665205125121);
}
void car_H_29(double *state, double *unused, double *out_1117037161188413142) {
  H_29(state, unused, out_1117037161188413142);
}
void car_h_28(double *state, double *unused, double *out_2112764580391293445) {
  h_28(state, unused, out_2112764580391293445);
}
void car_H_28(double *state, double *unused, double *out_3965361855881117432) {
  H_28(state, unused, out_3965361855881117432);
}
void car_h_31(double *state, double *unused, double *out_6013741326799347510) {
  h_31(state, unused, out_6013741326799347510);
}
void car_H_31(double *state, double *unused, double *out_6279238562740635369) {
  H_31(state, unused, out_6279238562740635369);
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
