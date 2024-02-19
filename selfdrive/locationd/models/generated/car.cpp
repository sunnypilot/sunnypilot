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
void err_fun(double *nom_x, double *delta_x, double *out_7179596139758080413) {
   out_7179596139758080413[0] = delta_x[0] + nom_x[0];
   out_7179596139758080413[1] = delta_x[1] + nom_x[1];
   out_7179596139758080413[2] = delta_x[2] + nom_x[2];
   out_7179596139758080413[3] = delta_x[3] + nom_x[3];
   out_7179596139758080413[4] = delta_x[4] + nom_x[4];
   out_7179596139758080413[5] = delta_x[5] + nom_x[5];
   out_7179596139758080413[6] = delta_x[6] + nom_x[6];
   out_7179596139758080413[7] = delta_x[7] + nom_x[7];
   out_7179596139758080413[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_2615111515505904601) {
   out_2615111515505904601[0] = -nom_x[0] + true_x[0];
   out_2615111515505904601[1] = -nom_x[1] + true_x[1];
   out_2615111515505904601[2] = -nom_x[2] + true_x[2];
   out_2615111515505904601[3] = -nom_x[3] + true_x[3];
   out_2615111515505904601[4] = -nom_x[4] + true_x[4];
   out_2615111515505904601[5] = -nom_x[5] + true_x[5];
   out_2615111515505904601[6] = -nom_x[6] + true_x[6];
   out_2615111515505904601[7] = -nom_x[7] + true_x[7];
   out_2615111515505904601[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_8585370806554949128) {
   out_8585370806554949128[0] = 1.0;
   out_8585370806554949128[1] = 0;
   out_8585370806554949128[2] = 0;
   out_8585370806554949128[3] = 0;
   out_8585370806554949128[4] = 0;
   out_8585370806554949128[5] = 0;
   out_8585370806554949128[6] = 0;
   out_8585370806554949128[7] = 0;
   out_8585370806554949128[8] = 0;
   out_8585370806554949128[9] = 0;
   out_8585370806554949128[10] = 1.0;
   out_8585370806554949128[11] = 0;
   out_8585370806554949128[12] = 0;
   out_8585370806554949128[13] = 0;
   out_8585370806554949128[14] = 0;
   out_8585370806554949128[15] = 0;
   out_8585370806554949128[16] = 0;
   out_8585370806554949128[17] = 0;
   out_8585370806554949128[18] = 0;
   out_8585370806554949128[19] = 0;
   out_8585370806554949128[20] = 1.0;
   out_8585370806554949128[21] = 0;
   out_8585370806554949128[22] = 0;
   out_8585370806554949128[23] = 0;
   out_8585370806554949128[24] = 0;
   out_8585370806554949128[25] = 0;
   out_8585370806554949128[26] = 0;
   out_8585370806554949128[27] = 0;
   out_8585370806554949128[28] = 0;
   out_8585370806554949128[29] = 0;
   out_8585370806554949128[30] = 1.0;
   out_8585370806554949128[31] = 0;
   out_8585370806554949128[32] = 0;
   out_8585370806554949128[33] = 0;
   out_8585370806554949128[34] = 0;
   out_8585370806554949128[35] = 0;
   out_8585370806554949128[36] = 0;
   out_8585370806554949128[37] = 0;
   out_8585370806554949128[38] = 0;
   out_8585370806554949128[39] = 0;
   out_8585370806554949128[40] = 1.0;
   out_8585370806554949128[41] = 0;
   out_8585370806554949128[42] = 0;
   out_8585370806554949128[43] = 0;
   out_8585370806554949128[44] = 0;
   out_8585370806554949128[45] = 0;
   out_8585370806554949128[46] = 0;
   out_8585370806554949128[47] = 0;
   out_8585370806554949128[48] = 0;
   out_8585370806554949128[49] = 0;
   out_8585370806554949128[50] = 1.0;
   out_8585370806554949128[51] = 0;
   out_8585370806554949128[52] = 0;
   out_8585370806554949128[53] = 0;
   out_8585370806554949128[54] = 0;
   out_8585370806554949128[55] = 0;
   out_8585370806554949128[56] = 0;
   out_8585370806554949128[57] = 0;
   out_8585370806554949128[58] = 0;
   out_8585370806554949128[59] = 0;
   out_8585370806554949128[60] = 1.0;
   out_8585370806554949128[61] = 0;
   out_8585370806554949128[62] = 0;
   out_8585370806554949128[63] = 0;
   out_8585370806554949128[64] = 0;
   out_8585370806554949128[65] = 0;
   out_8585370806554949128[66] = 0;
   out_8585370806554949128[67] = 0;
   out_8585370806554949128[68] = 0;
   out_8585370806554949128[69] = 0;
   out_8585370806554949128[70] = 1.0;
   out_8585370806554949128[71] = 0;
   out_8585370806554949128[72] = 0;
   out_8585370806554949128[73] = 0;
   out_8585370806554949128[74] = 0;
   out_8585370806554949128[75] = 0;
   out_8585370806554949128[76] = 0;
   out_8585370806554949128[77] = 0;
   out_8585370806554949128[78] = 0;
   out_8585370806554949128[79] = 0;
   out_8585370806554949128[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_206262983803821674) {
   out_206262983803821674[0] = state[0];
   out_206262983803821674[1] = state[1];
   out_206262983803821674[2] = state[2];
   out_206262983803821674[3] = state[3];
   out_206262983803821674[4] = state[4];
   out_206262983803821674[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8000000000000007*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_206262983803821674[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_206262983803821674[7] = state[7];
   out_206262983803821674[8] = state[8];
}
void F_fun(double *state, double dt, double *out_2052198398990982001) {
   out_2052198398990982001[0] = 1;
   out_2052198398990982001[1] = 0;
   out_2052198398990982001[2] = 0;
   out_2052198398990982001[3] = 0;
   out_2052198398990982001[4] = 0;
   out_2052198398990982001[5] = 0;
   out_2052198398990982001[6] = 0;
   out_2052198398990982001[7] = 0;
   out_2052198398990982001[8] = 0;
   out_2052198398990982001[9] = 0;
   out_2052198398990982001[10] = 1;
   out_2052198398990982001[11] = 0;
   out_2052198398990982001[12] = 0;
   out_2052198398990982001[13] = 0;
   out_2052198398990982001[14] = 0;
   out_2052198398990982001[15] = 0;
   out_2052198398990982001[16] = 0;
   out_2052198398990982001[17] = 0;
   out_2052198398990982001[18] = 0;
   out_2052198398990982001[19] = 0;
   out_2052198398990982001[20] = 1;
   out_2052198398990982001[21] = 0;
   out_2052198398990982001[22] = 0;
   out_2052198398990982001[23] = 0;
   out_2052198398990982001[24] = 0;
   out_2052198398990982001[25] = 0;
   out_2052198398990982001[26] = 0;
   out_2052198398990982001[27] = 0;
   out_2052198398990982001[28] = 0;
   out_2052198398990982001[29] = 0;
   out_2052198398990982001[30] = 1;
   out_2052198398990982001[31] = 0;
   out_2052198398990982001[32] = 0;
   out_2052198398990982001[33] = 0;
   out_2052198398990982001[34] = 0;
   out_2052198398990982001[35] = 0;
   out_2052198398990982001[36] = 0;
   out_2052198398990982001[37] = 0;
   out_2052198398990982001[38] = 0;
   out_2052198398990982001[39] = 0;
   out_2052198398990982001[40] = 1;
   out_2052198398990982001[41] = 0;
   out_2052198398990982001[42] = 0;
   out_2052198398990982001[43] = 0;
   out_2052198398990982001[44] = 0;
   out_2052198398990982001[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_2052198398990982001[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_2052198398990982001[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_2052198398990982001[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_2052198398990982001[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_2052198398990982001[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_2052198398990982001[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_2052198398990982001[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_2052198398990982001[53] = -9.8000000000000007*dt;
   out_2052198398990982001[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_2052198398990982001[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_2052198398990982001[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_2052198398990982001[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_2052198398990982001[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_2052198398990982001[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_2052198398990982001[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_2052198398990982001[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_2052198398990982001[62] = 0;
   out_2052198398990982001[63] = 0;
   out_2052198398990982001[64] = 0;
   out_2052198398990982001[65] = 0;
   out_2052198398990982001[66] = 0;
   out_2052198398990982001[67] = 0;
   out_2052198398990982001[68] = 0;
   out_2052198398990982001[69] = 0;
   out_2052198398990982001[70] = 1;
   out_2052198398990982001[71] = 0;
   out_2052198398990982001[72] = 0;
   out_2052198398990982001[73] = 0;
   out_2052198398990982001[74] = 0;
   out_2052198398990982001[75] = 0;
   out_2052198398990982001[76] = 0;
   out_2052198398990982001[77] = 0;
   out_2052198398990982001[78] = 0;
   out_2052198398990982001[79] = 0;
   out_2052198398990982001[80] = 1;
}
void h_25(double *state, double *unused, double *out_8428502641983275766) {
   out_8428502641983275766[0] = state[6];
}
void H_25(double *state, double *unused, double *out_6836289276866676448) {
   out_6836289276866676448[0] = 0;
   out_6836289276866676448[1] = 0;
   out_6836289276866676448[2] = 0;
   out_6836289276866676448[3] = 0;
   out_6836289276866676448[4] = 0;
   out_6836289276866676448[5] = 0;
   out_6836289276866676448[6] = 1;
   out_6836289276866676448[7] = 0;
   out_6836289276866676448[8] = 0;
}
void h_24(double *state, double *unused, double *out_557687457453017340) {
   out_557687457453017340[0] = state[4];
   out_557687457453017340[1] = state[5];
}
void H_24(double *state, double *unused, double *out_6439643972512816953) {
   out_6439643972512816953[0] = 0;
   out_6439643972512816953[1] = 0;
   out_6439643972512816953[2] = 0;
   out_6439643972512816953[3] = 0;
   out_6439643972512816953[4] = 1;
   out_6439643972512816953[5] = 0;
   out_6439643972512816953[6] = 0;
   out_6439643972512816953[7] = 0;
   out_6439643972512816953[8] = 0;
   out_6439643972512816953[9] = 0;
   out_6439643972512816953[10] = 0;
   out_6439643972512816953[11] = 0;
   out_6439643972512816953[12] = 0;
   out_6439643972512816953[13] = 0;
   out_6439643972512816953[14] = 1;
   out_6439643972512816953[15] = 0;
   out_6439643972512816953[16] = 0;
   out_6439643972512816953[17] = 0;
}
void h_30(double *state, double *unused, double *out_1609000481154498631) {
   out_1609000481154498631[0] = state[4];
}
void H_30(double *state, double *unused, double *out_9092121838335626541) {
   out_9092121838335626541[0] = 0;
   out_9092121838335626541[1] = 0;
   out_9092121838335626541[2] = 0;
   out_9092121838335626541[3] = 0;
   out_9092121838335626541[4] = 1;
   out_9092121838335626541[5] = 0;
   out_9092121838335626541[6] = 0;
   out_9092121838335626541[7] = 0;
   out_9092121838335626541[8] = 0;
}
void h_26(double *state, double *unused, double *out_7864825203113545885) {
   out_7864825203113545885[0] = state[7];
}
void H_26(double *state, double *unused, double *out_3094785957992620224) {
   out_3094785957992620224[0] = 0;
   out_3094785957992620224[1] = 0;
   out_3094785957992620224[2] = 0;
   out_3094785957992620224[3] = 0;
   out_3094785957992620224[4] = 0;
   out_3094785957992620224[5] = 0;
   out_3094785957992620224[6] = 0;
   out_3094785957992620224[7] = 1;
   out_3094785957992620224[8] = 0;
}
void h_27(double *state, double *unused, double *out_4151277612470839713) {
   out_4151277612470839713[0] = state[3];
}
void H_27(double *state, double *unused, double *out_7179858923573500164) {
   out_7179858923573500164[0] = 0;
   out_7179858923573500164[1] = 0;
   out_7179858923573500164[2] = 0;
   out_7179858923573500164[3] = 1;
   out_7179858923573500164[4] = 0;
   out_7179858923573500164[5] = 0;
   out_7179858923573500164[6] = 0;
   out_7179858923573500164[7] = 0;
   out_7179858923573500164[8] = 0;
}
void h_29(double *state, double *unused, double *out_6610673748815344276) {
   out_6610673748815344276[0] = state[1];
}
void H_29(double *state, double *unused, double *out_8581890494021234357) {
   out_8581890494021234357[0] = 0;
   out_8581890494021234357[1] = 1;
   out_8581890494021234357[2] = 0;
   out_8581890494021234357[3] = 0;
   out_8581890494021234357[4] = 0;
   out_8581890494021234357[5] = 0;
   out_8581890494021234357[6] = 0;
   out_8581890494021234357[7] = 0;
   out_8581890494021234357[8] = 0;
}
void h_28(double *state, double *unused, double *out_4645031851795157427) {
   out_4645031851795157427[0] = state[0];
}
void H_28(double *state, double *unused, double *out_4782454562618786685) {
   out_4782454562618786685[0] = 1;
   out_4782454562618786685[1] = 0;
   out_4782454562618786685[2] = 0;
   out_4782454562618786685[3] = 0;
   out_4782454562618786685[4] = 0;
   out_4782454562618786685[5] = 0;
   out_4782454562618786685[6] = 0;
   out_4782454562618786685[7] = 0;
   out_4782454562618786685[8] = 0;
}
void h_31(double *state, double *unused, double *out_1613919571485492219) {
   out_1613919571485492219[0] = state[8];
}
void H_31(double *state, double *unused, double *out_2468577855759268748) {
   out_2468577855759268748[0] = 0;
   out_2468577855759268748[1] = 0;
   out_2468577855759268748[2] = 0;
   out_2468577855759268748[3] = 0;
   out_2468577855759268748[4] = 0;
   out_2468577855759268748[5] = 0;
   out_2468577855759268748[6] = 0;
   out_2468577855759268748[7] = 0;
   out_2468577855759268748[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_7179596139758080413) {
  err_fun(nom_x, delta_x, out_7179596139758080413);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_2615111515505904601) {
  inv_err_fun(nom_x, true_x, out_2615111515505904601);
}
void car_H_mod_fun(double *state, double *out_8585370806554949128) {
  H_mod_fun(state, out_8585370806554949128);
}
void car_f_fun(double *state, double dt, double *out_206262983803821674) {
  f_fun(state,  dt, out_206262983803821674);
}
void car_F_fun(double *state, double dt, double *out_2052198398990982001) {
  F_fun(state,  dt, out_2052198398990982001);
}
void car_h_25(double *state, double *unused, double *out_8428502641983275766) {
  h_25(state, unused, out_8428502641983275766);
}
void car_H_25(double *state, double *unused, double *out_6836289276866676448) {
  H_25(state, unused, out_6836289276866676448);
}
void car_h_24(double *state, double *unused, double *out_557687457453017340) {
  h_24(state, unused, out_557687457453017340);
}
void car_H_24(double *state, double *unused, double *out_6439643972512816953) {
  H_24(state, unused, out_6439643972512816953);
}
void car_h_30(double *state, double *unused, double *out_1609000481154498631) {
  h_30(state, unused, out_1609000481154498631);
}
void car_H_30(double *state, double *unused, double *out_9092121838335626541) {
  H_30(state, unused, out_9092121838335626541);
}
void car_h_26(double *state, double *unused, double *out_7864825203113545885) {
  h_26(state, unused, out_7864825203113545885);
}
void car_H_26(double *state, double *unused, double *out_3094785957992620224) {
  H_26(state, unused, out_3094785957992620224);
}
void car_h_27(double *state, double *unused, double *out_4151277612470839713) {
  h_27(state, unused, out_4151277612470839713);
}
void car_H_27(double *state, double *unused, double *out_7179858923573500164) {
  H_27(state, unused, out_7179858923573500164);
}
void car_h_29(double *state, double *unused, double *out_6610673748815344276) {
  h_29(state, unused, out_6610673748815344276);
}
void car_H_29(double *state, double *unused, double *out_8581890494021234357) {
  H_29(state, unused, out_8581890494021234357);
}
void car_h_28(double *state, double *unused, double *out_4645031851795157427) {
  h_28(state, unused, out_4645031851795157427);
}
void car_H_28(double *state, double *unused, double *out_4782454562618786685) {
  H_28(state, unused, out_4782454562618786685);
}
void car_h_31(double *state, double *unused, double *out_1613919571485492219) {
  h_31(state, unused, out_1613919571485492219);
}
void car_H_31(double *state, double *unused, double *out_2468577855759268748) {
  H_31(state, unused, out_2468577855759268748);
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
