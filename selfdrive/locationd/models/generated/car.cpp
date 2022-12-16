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
 *                      Code generated with SymPy 1.11.1                      *
 *                                                                            *
 *              See http://www.sympy.org/ for more information.               *
 *                                                                            *
 *                         This file is part of 'ekf'                         *
 ******************************************************************************/
void err_fun(double *nom_x, double *delta_x, double *out_6879141421579502993) {
   out_6879141421579502993[0] = delta_x[0] + nom_x[0];
   out_6879141421579502993[1] = delta_x[1] + nom_x[1];
   out_6879141421579502993[2] = delta_x[2] + nom_x[2];
   out_6879141421579502993[3] = delta_x[3] + nom_x[3];
   out_6879141421579502993[4] = delta_x[4] + nom_x[4];
   out_6879141421579502993[5] = delta_x[5] + nom_x[5];
   out_6879141421579502993[6] = delta_x[6] + nom_x[6];
   out_6879141421579502993[7] = delta_x[7] + nom_x[7];
   out_6879141421579502993[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_5117966674436304926) {
   out_5117966674436304926[0] = -nom_x[0] + true_x[0];
   out_5117966674436304926[1] = -nom_x[1] + true_x[1];
   out_5117966674436304926[2] = -nom_x[2] + true_x[2];
   out_5117966674436304926[3] = -nom_x[3] + true_x[3];
   out_5117966674436304926[4] = -nom_x[4] + true_x[4];
   out_5117966674436304926[5] = -nom_x[5] + true_x[5];
   out_5117966674436304926[6] = -nom_x[6] + true_x[6];
   out_5117966674436304926[7] = -nom_x[7] + true_x[7];
   out_5117966674436304926[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_474615079286262384) {
   out_474615079286262384[0] = 1.0;
   out_474615079286262384[1] = 0;
   out_474615079286262384[2] = 0;
   out_474615079286262384[3] = 0;
   out_474615079286262384[4] = 0;
   out_474615079286262384[5] = 0;
   out_474615079286262384[6] = 0;
   out_474615079286262384[7] = 0;
   out_474615079286262384[8] = 0;
   out_474615079286262384[9] = 0;
   out_474615079286262384[10] = 1.0;
   out_474615079286262384[11] = 0;
   out_474615079286262384[12] = 0;
   out_474615079286262384[13] = 0;
   out_474615079286262384[14] = 0;
   out_474615079286262384[15] = 0;
   out_474615079286262384[16] = 0;
   out_474615079286262384[17] = 0;
   out_474615079286262384[18] = 0;
   out_474615079286262384[19] = 0;
   out_474615079286262384[20] = 1.0;
   out_474615079286262384[21] = 0;
   out_474615079286262384[22] = 0;
   out_474615079286262384[23] = 0;
   out_474615079286262384[24] = 0;
   out_474615079286262384[25] = 0;
   out_474615079286262384[26] = 0;
   out_474615079286262384[27] = 0;
   out_474615079286262384[28] = 0;
   out_474615079286262384[29] = 0;
   out_474615079286262384[30] = 1.0;
   out_474615079286262384[31] = 0;
   out_474615079286262384[32] = 0;
   out_474615079286262384[33] = 0;
   out_474615079286262384[34] = 0;
   out_474615079286262384[35] = 0;
   out_474615079286262384[36] = 0;
   out_474615079286262384[37] = 0;
   out_474615079286262384[38] = 0;
   out_474615079286262384[39] = 0;
   out_474615079286262384[40] = 1.0;
   out_474615079286262384[41] = 0;
   out_474615079286262384[42] = 0;
   out_474615079286262384[43] = 0;
   out_474615079286262384[44] = 0;
   out_474615079286262384[45] = 0;
   out_474615079286262384[46] = 0;
   out_474615079286262384[47] = 0;
   out_474615079286262384[48] = 0;
   out_474615079286262384[49] = 0;
   out_474615079286262384[50] = 1.0;
   out_474615079286262384[51] = 0;
   out_474615079286262384[52] = 0;
   out_474615079286262384[53] = 0;
   out_474615079286262384[54] = 0;
   out_474615079286262384[55] = 0;
   out_474615079286262384[56] = 0;
   out_474615079286262384[57] = 0;
   out_474615079286262384[58] = 0;
   out_474615079286262384[59] = 0;
   out_474615079286262384[60] = 1.0;
   out_474615079286262384[61] = 0;
   out_474615079286262384[62] = 0;
   out_474615079286262384[63] = 0;
   out_474615079286262384[64] = 0;
   out_474615079286262384[65] = 0;
   out_474615079286262384[66] = 0;
   out_474615079286262384[67] = 0;
   out_474615079286262384[68] = 0;
   out_474615079286262384[69] = 0;
   out_474615079286262384[70] = 1.0;
   out_474615079286262384[71] = 0;
   out_474615079286262384[72] = 0;
   out_474615079286262384[73] = 0;
   out_474615079286262384[74] = 0;
   out_474615079286262384[75] = 0;
   out_474615079286262384[76] = 0;
   out_474615079286262384[77] = 0;
   out_474615079286262384[78] = 0;
   out_474615079286262384[79] = 0;
   out_474615079286262384[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_7000723790512890111) {
   out_7000723790512890111[0] = state[0];
   out_7000723790512890111[1] = state[1];
   out_7000723790512890111[2] = state[2];
   out_7000723790512890111[3] = state[3];
   out_7000723790512890111[4] = state[4];
   out_7000723790512890111[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8000000000000007*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_7000723790512890111[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_7000723790512890111[7] = state[7];
   out_7000723790512890111[8] = state[8];
}
void F_fun(double *state, double dt, double *out_2040835191970999270) {
   out_2040835191970999270[0] = 1;
   out_2040835191970999270[1] = 0;
   out_2040835191970999270[2] = 0;
   out_2040835191970999270[3] = 0;
   out_2040835191970999270[4] = 0;
   out_2040835191970999270[5] = 0;
   out_2040835191970999270[6] = 0;
   out_2040835191970999270[7] = 0;
   out_2040835191970999270[8] = 0;
   out_2040835191970999270[9] = 0;
   out_2040835191970999270[10] = 1;
   out_2040835191970999270[11] = 0;
   out_2040835191970999270[12] = 0;
   out_2040835191970999270[13] = 0;
   out_2040835191970999270[14] = 0;
   out_2040835191970999270[15] = 0;
   out_2040835191970999270[16] = 0;
   out_2040835191970999270[17] = 0;
   out_2040835191970999270[18] = 0;
   out_2040835191970999270[19] = 0;
   out_2040835191970999270[20] = 1;
   out_2040835191970999270[21] = 0;
   out_2040835191970999270[22] = 0;
   out_2040835191970999270[23] = 0;
   out_2040835191970999270[24] = 0;
   out_2040835191970999270[25] = 0;
   out_2040835191970999270[26] = 0;
   out_2040835191970999270[27] = 0;
   out_2040835191970999270[28] = 0;
   out_2040835191970999270[29] = 0;
   out_2040835191970999270[30] = 1;
   out_2040835191970999270[31] = 0;
   out_2040835191970999270[32] = 0;
   out_2040835191970999270[33] = 0;
   out_2040835191970999270[34] = 0;
   out_2040835191970999270[35] = 0;
   out_2040835191970999270[36] = 0;
   out_2040835191970999270[37] = 0;
   out_2040835191970999270[38] = 0;
   out_2040835191970999270[39] = 0;
   out_2040835191970999270[40] = 1;
   out_2040835191970999270[41] = 0;
   out_2040835191970999270[42] = 0;
   out_2040835191970999270[43] = 0;
   out_2040835191970999270[44] = 0;
   out_2040835191970999270[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_2040835191970999270[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_2040835191970999270[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_2040835191970999270[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_2040835191970999270[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_2040835191970999270[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_2040835191970999270[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_2040835191970999270[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_2040835191970999270[53] = -9.8000000000000007*dt;
   out_2040835191970999270[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_2040835191970999270[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_2040835191970999270[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_2040835191970999270[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_2040835191970999270[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_2040835191970999270[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_2040835191970999270[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_2040835191970999270[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_2040835191970999270[62] = 0;
   out_2040835191970999270[63] = 0;
   out_2040835191970999270[64] = 0;
   out_2040835191970999270[65] = 0;
   out_2040835191970999270[66] = 0;
   out_2040835191970999270[67] = 0;
   out_2040835191970999270[68] = 0;
   out_2040835191970999270[69] = 0;
   out_2040835191970999270[70] = 1;
   out_2040835191970999270[71] = 0;
   out_2040835191970999270[72] = 0;
   out_2040835191970999270[73] = 0;
   out_2040835191970999270[74] = 0;
   out_2040835191970999270[75] = 0;
   out_2040835191970999270[76] = 0;
   out_2040835191970999270[77] = 0;
   out_2040835191970999270[78] = 0;
   out_2040835191970999270[79] = 0;
   out_2040835191970999270[80] = 1;
}
void h_25(double *state, double *unused, double *out_2447891744252367846) {
   out_2447891744252367846[0] = state[6];
}
void H_25(double *state, double *unused, double *out_7470380649254261837) {
   out_7470380649254261837[0] = 0;
   out_7470380649254261837[1] = 0;
   out_7470380649254261837[2] = 0;
   out_7470380649254261837[3] = 0;
   out_7470380649254261837[4] = 0;
   out_7470380649254261837[5] = 0;
   out_7470380649254261837[6] = 1;
   out_7470380649254261837[7] = 0;
   out_7470380649254261837[8] = 0;
}
void h_24(double *state, double *unused, double *out_1536598539730519785) {
   out_1536598539730519785[0] = state[4];
   out_1536598539730519785[1] = state[5];
}
void H_24(double *state, double *unused, double *out_4322157966347104022) {
   out_4322157966347104022[0] = 0;
   out_4322157966347104022[1] = 0;
   out_4322157966347104022[2] = 0;
   out_4322157966347104022[3] = 0;
   out_4322157966347104022[4] = 1;
   out_4322157966347104022[5] = 0;
   out_4322157966347104022[6] = 0;
   out_4322157966347104022[7] = 0;
   out_4322157966347104022[8] = 0;
   out_4322157966347104022[9] = 0;
   out_4322157966347104022[10] = 0;
   out_4322157966347104022[11] = 0;
   out_4322157966347104022[12] = 0;
   out_4322157966347104022[13] = 0;
   out_4322157966347104022[14] = 1;
   out_4322157966347104022[15] = 0;
   out_4322157966347104022[16] = 0;
   out_4322157966347104022[17] = 0;
}
void h_30(double *state, double *unused, double *out_9218726970602718782) {
   out_9218726970602718782[0] = state[4];
}
void H_30(double *state, double *unused, double *out_7341041702111021767) {
   out_7341041702111021767[0] = 0;
   out_7341041702111021767[1] = 0;
   out_7341041702111021767[2] = 0;
   out_7341041702111021767[3] = 0;
   out_7341041702111021767[4] = 1;
   out_7341041702111021767[5] = 0;
   out_7341041702111021767[6] = 0;
   out_7341041702111021767[7] = 0;
   out_7341041702111021767[8] = 0;
}
void h_26(double *state, double *unused, double *out_8275217117701056347) {
   out_8275217117701056347[0] = state[7];
}
void H_26(double *state, double *unused, double *out_8127234713364573741) {
   out_8127234713364573741[0] = 0;
   out_8127234713364573741[1] = 0;
   out_8127234713364573741[2] = 0;
   out_8127234713364573741[3] = 0;
   out_8127234713364573741[4] = 0;
   out_8127234713364573741[5] = 0;
   out_8127234713364573741[6] = 0;
   out_8127234713364573741[7] = 1;
   out_8127234713364573741[8] = 0;
}
void h_27(double *state, double *unused, double *out_1950060337029261166) {
   out_1950060337029261166[0] = state[3];
}
void H_27(double *state, double *unused, double *out_5166278390310596856) {
   out_5166278390310596856[0] = 0;
   out_5166278390310596856[1] = 0;
   out_5166278390310596856[2] = 0;
   out_5166278390310596856[3] = 1;
   out_5166278390310596856[4] = 0;
   out_5166278390310596856[5] = 0;
   out_5166278390310596856[6] = 0;
   out_5166278390310596856[7] = 0;
   out_5166278390310596856[8] = 0;
}
void h_29(double *state, double *unused, double *out_8615411085926241265) {
   out_8615411085926241265[0] = state[1];
}
void H_29(double *state, double *unused, double *out_7851273046425413951) {
   out_7851273046425413951[0] = 0;
   out_7851273046425413951[1] = 1;
   out_7851273046425413951[2] = 0;
   out_7851273046425413951[3] = 0;
   out_7851273046425413951[4] = 0;
   out_7851273046425413951[5] = 0;
   out_7851273046425413951[6] = 0;
   out_7851273046425413951[7] = 0;
   out_7851273046425413951[8] = 0;
}
void h_28(double *state, double *unused, double *out_6951733604690106811) {
   out_6951733604690106811[0] = state[0];
}
void H_28(double *state, double *unused, double *out_8631840755718811414) {
   out_8631840755718811414[0] = 1;
   out_8631840755718811414[1] = 0;
   out_8631840755718811414[2] = 0;
   out_8631840755718811414[3] = 0;
   out_8631840755718811414[4] = 0;
   out_8631840755718811414[5] = 0;
   out_8631840755718811414[6] = 0;
   out_8631840755718811414[7] = 0;
   out_8631840755718811414[8] = 0;
}
void h_31(double *state, double *unused, double *out_1600981538002701312) {
   out_1600981538002701312[0] = state[8];
}
void H_31(double *state, double *unused, double *out_7501026611131222265) {
   out_7501026611131222265[0] = 0;
   out_7501026611131222265[1] = 0;
   out_7501026611131222265[2] = 0;
   out_7501026611131222265[3] = 0;
   out_7501026611131222265[4] = 0;
   out_7501026611131222265[5] = 0;
   out_7501026611131222265[6] = 0;
   out_7501026611131222265[7] = 0;
   out_7501026611131222265[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_6879141421579502993) {
  err_fun(nom_x, delta_x, out_6879141421579502993);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_5117966674436304926) {
  inv_err_fun(nom_x, true_x, out_5117966674436304926);
}
void car_H_mod_fun(double *state, double *out_474615079286262384) {
  H_mod_fun(state, out_474615079286262384);
}
void car_f_fun(double *state, double dt, double *out_7000723790512890111) {
  f_fun(state,  dt, out_7000723790512890111);
}
void car_F_fun(double *state, double dt, double *out_2040835191970999270) {
  F_fun(state,  dt, out_2040835191970999270);
}
void car_h_25(double *state, double *unused, double *out_2447891744252367846) {
  h_25(state, unused, out_2447891744252367846);
}
void car_H_25(double *state, double *unused, double *out_7470380649254261837) {
  H_25(state, unused, out_7470380649254261837);
}
void car_h_24(double *state, double *unused, double *out_1536598539730519785) {
  h_24(state, unused, out_1536598539730519785);
}
void car_H_24(double *state, double *unused, double *out_4322157966347104022) {
  H_24(state, unused, out_4322157966347104022);
}
void car_h_30(double *state, double *unused, double *out_9218726970602718782) {
  h_30(state, unused, out_9218726970602718782);
}
void car_H_30(double *state, double *unused, double *out_7341041702111021767) {
  H_30(state, unused, out_7341041702111021767);
}
void car_h_26(double *state, double *unused, double *out_8275217117701056347) {
  h_26(state, unused, out_8275217117701056347);
}
void car_H_26(double *state, double *unused, double *out_8127234713364573741) {
  H_26(state, unused, out_8127234713364573741);
}
void car_h_27(double *state, double *unused, double *out_1950060337029261166) {
  h_27(state, unused, out_1950060337029261166);
}
void car_H_27(double *state, double *unused, double *out_5166278390310596856) {
  H_27(state, unused, out_5166278390310596856);
}
void car_h_29(double *state, double *unused, double *out_8615411085926241265) {
  h_29(state, unused, out_8615411085926241265);
}
void car_H_29(double *state, double *unused, double *out_7851273046425413951) {
  H_29(state, unused, out_7851273046425413951);
}
void car_h_28(double *state, double *unused, double *out_6951733604690106811) {
  h_28(state, unused, out_6951733604690106811);
}
void car_H_28(double *state, double *unused, double *out_8631840755718811414) {
  H_28(state, unused, out_8631840755718811414);
}
void car_h_31(double *state, double *unused, double *out_1600981538002701312) {
  h_31(state, unused, out_1600981538002701312);
}
void car_H_31(double *state, double *unused, double *out_7501026611131222265) {
  H_31(state, unused, out_7501026611131222265);
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
