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
void err_fun(double *nom_x, double *delta_x, double *out_5070392900769873758) {
   out_5070392900769873758[0] = delta_x[0] + nom_x[0];
   out_5070392900769873758[1] = delta_x[1] + nom_x[1];
   out_5070392900769873758[2] = delta_x[2] + nom_x[2];
   out_5070392900769873758[3] = delta_x[3] + nom_x[3];
   out_5070392900769873758[4] = delta_x[4] + nom_x[4];
   out_5070392900769873758[5] = delta_x[5] + nom_x[5];
   out_5070392900769873758[6] = delta_x[6] + nom_x[6];
   out_5070392900769873758[7] = delta_x[7] + nom_x[7];
   out_5070392900769873758[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_3742760733154016051) {
   out_3742760733154016051[0] = -nom_x[0] + true_x[0];
   out_3742760733154016051[1] = -nom_x[1] + true_x[1];
   out_3742760733154016051[2] = -nom_x[2] + true_x[2];
   out_3742760733154016051[3] = -nom_x[3] + true_x[3];
   out_3742760733154016051[4] = -nom_x[4] + true_x[4];
   out_3742760733154016051[5] = -nom_x[5] + true_x[5];
   out_3742760733154016051[6] = -nom_x[6] + true_x[6];
   out_3742760733154016051[7] = -nom_x[7] + true_x[7];
   out_3742760733154016051[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_5758456641177717920) {
   out_5758456641177717920[0] = 1.0;
   out_5758456641177717920[1] = 0.0;
   out_5758456641177717920[2] = 0.0;
   out_5758456641177717920[3] = 0.0;
   out_5758456641177717920[4] = 0.0;
   out_5758456641177717920[5] = 0.0;
   out_5758456641177717920[6] = 0.0;
   out_5758456641177717920[7] = 0.0;
   out_5758456641177717920[8] = 0.0;
   out_5758456641177717920[9] = 0.0;
   out_5758456641177717920[10] = 1.0;
   out_5758456641177717920[11] = 0.0;
   out_5758456641177717920[12] = 0.0;
   out_5758456641177717920[13] = 0.0;
   out_5758456641177717920[14] = 0.0;
   out_5758456641177717920[15] = 0.0;
   out_5758456641177717920[16] = 0.0;
   out_5758456641177717920[17] = 0.0;
   out_5758456641177717920[18] = 0.0;
   out_5758456641177717920[19] = 0.0;
   out_5758456641177717920[20] = 1.0;
   out_5758456641177717920[21] = 0.0;
   out_5758456641177717920[22] = 0.0;
   out_5758456641177717920[23] = 0.0;
   out_5758456641177717920[24] = 0.0;
   out_5758456641177717920[25] = 0.0;
   out_5758456641177717920[26] = 0.0;
   out_5758456641177717920[27] = 0.0;
   out_5758456641177717920[28] = 0.0;
   out_5758456641177717920[29] = 0.0;
   out_5758456641177717920[30] = 1.0;
   out_5758456641177717920[31] = 0.0;
   out_5758456641177717920[32] = 0.0;
   out_5758456641177717920[33] = 0.0;
   out_5758456641177717920[34] = 0.0;
   out_5758456641177717920[35] = 0.0;
   out_5758456641177717920[36] = 0.0;
   out_5758456641177717920[37] = 0.0;
   out_5758456641177717920[38] = 0.0;
   out_5758456641177717920[39] = 0.0;
   out_5758456641177717920[40] = 1.0;
   out_5758456641177717920[41] = 0.0;
   out_5758456641177717920[42] = 0.0;
   out_5758456641177717920[43] = 0.0;
   out_5758456641177717920[44] = 0.0;
   out_5758456641177717920[45] = 0.0;
   out_5758456641177717920[46] = 0.0;
   out_5758456641177717920[47] = 0.0;
   out_5758456641177717920[48] = 0.0;
   out_5758456641177717920[49] = 0.0;
   out_5758456641177717920[50] = 1.0;
   out_5758456641177717920[51] = 0.0;
   out_5758456641177717920[52] = 0.0;
   out_5758456641177717920[53] = 0.0;
   out_5758456641177717920[54] = 0.0;
   out_5758456641177717920[55] = 0.0;
   out_5758456641177717920[56] = 0.0;
   out_5758456641177717920[57] = 0.0;
   out_5758456641177717920[58] = 0.0;
   out_5758456641177717920[59] = 0.0;
   out_5758456641177717920[60] = 1.0;
   out_5758456641177717920[61] = 0.0;
   out_5758456641177717920[62] = 0.0;
   out_5758456641177717920[63] = 0.0;
   out_5758456641177717920[64] = 0.0;
   out_5758456641177717920[65] = 0.0;
   out_5758456641177717920[66] = 0.0;
   out_5758456641177717920[67] = 0.0;
   out_5758456641177717920[68] = 0.0;
   out_5758456641177717920[69] = 0.0;
   out_5758456641177717920[70] = 1.0;
   out_5758456641177717920[71] = 0.0;
   out_5758456641177717920[72] = 0.0;
   out_5758456641177717920[73] = 0.0;
   out_5758456641177717920[74] = 0.0;
   out_5758456641177717920[75] = 0.0;
   out_5758456641177717920[76] = 0.0;
   out_5758456641177717920[77] = 0.0;
   out_5758456641177717920[78] = 0.0;
   out_5758456641177717920[79] = 0.0;
   out_5758456641177717920[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_730595102125265078) {
   out_730595102125265078[0] = state[0];
   out_730595102125265078[1] = state[1];
   out_730595102125265078[2] = state[2];
   out_730595102125265078[3] = state[3];
   out_730595102125265078[4] = state[4];
   out_730595102125265078[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8100000000000005*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_730595102125265078[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_730595102125265078[7] = state[7];
   out_730595102125265078[8] = state[8];
}
void F_fun(double *state, double dt, double *out_7198115545780111359) {
   out_7198115545780111359[0] = 1;
   out_7198115545780111359[1] = 0;
   out_7198115545780111359[2] = 0;
   out_7198115545780111359[3] = 0;
   out_7198115545780111359[4] = 0;
   out_7198115545780111359[5] = 0;
   out_7198115545780111359[6] = 0;
   out_7198115545780111359[7] = 0;
   out_7198115545780111359[8] = 0;
   out_7198115545780111359[9] = 0;
   out_7198115545780111359[10] = 1;
   out_7198115545780111359[11] = 0;
   out_7198115545780111359[12] = 0;
   out_7198115545780111359[13] = 0;
   out_7198115545780111359[14] = 0;
   out_7198115545780111359[15] = 0;
   out_7198115545780111359[16] = 0;
   out_7198115545780111359[17] = 0;
   out_7198115545780111359[18] = 0;
   out_7198115545780111359[19] = 0;
   out_7198115545780111359[20] = 1;
   out_7198115545780111359[21] = 0;
   out_7198115545780111359[22] = 0;
   out_7198115545780111359[23] = 0;
   out_7198115545780111359[24] = 0;
   out_7198115545780111359[25] = 0;
   out_7198115545780111359[26] = 0;
   out_7198115545780111359[27] = 0;
   out_7198115545780111359[28] = 0;
   out_7198115545780111359[29] = 0;
   out_7198115545780111359[30] = 1;
   out_7198115545780111359[31] = 0;
   out_7198115545780111359[32] = 0;
   out_7198115545780111359[33] = 0;
   out_7198115545780111359[34] = 0;
   out_7198115545780111359[35] = 0;
   out_7198115545780111359[36] = 0;
   out_7198115545780111359[37] = 0;
   out_7198115545780111359[38] = 0;
   out_7198115545780111359[39] = 0;
   out_7198115545780111359[40] = 1;
   out_7198115545780111359[41] = 0;
   out_7198115545780111359[42] = 0;
   out_7198115545780111359[43] = 0;
   out_7198115545780111359[44] = 0;
   out_7198115545780111359[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_7198115545780111359[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_7198115545780111359[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_7198115545780111359[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_7198115545780111359[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_7198115545780111359[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_7198115545780111359[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_7198115545780111359[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_7198115545780111359[53] = -9.8100000000000005*dt;
   out_7198115545780111359[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_7198115545780111359[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_7198115545780111359[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_7198115545780111359[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_7198115545780111359[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_7198115545780111359[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_7198115545780111359[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_7198115545780111359[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_7198115545780111359[62] = 0;
   out_7198115545780111359[63] = 0;
   out_7198115545780111359[64] = 0;
   out_7198115545780111359[65] = 0;
   out_7198115545780111359[66] = 0;
   out_7198115545780111359[67] = 0;
   out_7198115545780111359[68] = 0;
   out_7198115545780111359[69] = 0;
   out_7198115545780111359[70] = 1;
   out_7198115545780111359[71] = 0;
   out_7198115545780111359[72] = 0;
   out_7198115545780111359[73] = 0;
   out_7198115545780111359[74] = 0;
   out_7198115545780111359[75] = 0;
   out_7198115545780111359[76] = 0;
   out_7198115545780111359[77] = 0;
   out_7198115545780111359[78] = 0;
   out_7198115545780111359[79] = 0;
   out_7198115545780111359[80] = 1;
}
void h_25(double *state, double *unused, double *out_5441109048213736058) {
   out_5441109048213736058[0] = state[6];
}
void H_25(double *state, double *unused, double *out_4766949399557973891) {
   out_4766949399557973891[0] = 0;
   out_4766949399557973891[1] = 0;
   out_4766949399557973891[2] = 0;
   out_4766949399557973891[3] = 0;
   out_4766949399557973891[4] = 0;
   out_4766949399557973891[5] = 0;
   out_4766949399557973891[6] = 1;
   out_4766949399557973891[7] = 0;
   out_4766949399557973891[8] = 0;
}
void h_24(double *state, double *unused, double *out_2797667639827089179) {
   out_2797667639827089179[0] = state[4];
   out_2797667639827089179[1] = state[5];
}
void H_24(double *state, double *unused, double *out_4461115786511221334) {
   out_4461115786511221334[0] = 0;
   out_4461115786511221334[1] = 0;
   out_4461115786511221334[2] = 0;
   out_4461115786511221334[3] = 0;
   out_4461115786511221334[4] = 1;
   out_4461115786511221334[5] = 0;
   out_4461115786511221334[6] = 0;
   out_4461115786511221334[7] = 0;
   out_4461115786511221334[8] = 0;
   out_4461115786511221334[9] = 0;
   out_4461115786511221334[10] = 0;
   out_4461115786511221334[11] = 0;
   out_4461115786511221334[12] = 0;
   out_4461115786511221334[13] = 0;
   out_4461115786511221334[14] = 1;
   out_4461115786511221334[15] = 0;
   out_4461115786511221334[16] = 0;
   out_4461115786511221334[17] = 0;
}
void h_30(double *state, double *unused, double *out_1188271489450022901) {
   out_1188271489450022901[0] = state[4];
}
void H_30(double *state, double *unused, double *out_9152098344023969527) {
   out_9152098344023969527[0] = 0;
   out_9152098344023969527[1] = 0;
   out_9152098344023969527[2] = 0;
   out_9152098344023969527[3] = 0;
   out_9152098344023969527[4] = 1;
   out_9152098344023969527[5] = 0;
   out_9152098344023969527[6] = 0;
   out_9152098344023969527[7] = 0;
   out_9152098344023969527[8] = 0;
}
void h_26(double *state, double *unused, double *out_6530138725336053464) {
   out_6530138725336053464[0] = state[7];
}
void H_26(double *state, double *unused, double *out_8508452718432030115) {
   out_8508452718432030115[0] = 0;
   out_8508452718432030115[1] = 0;
   out_8508452718432030115[2] = 0;
   out_8508452718432030115[3] = 0;
   out_8508452718432030115[4] = 0;
   out_8508452718432030115[5] = 0;
   out_8508452718432030115[6] = 0;
   out_8508452718432030115[7] = 1;
   out_8508452718432030115[8] = 0;
}
void h_27(double *state, double *unused, double *out_8003961757834969913) {
   out_8003961757834969913[0] = state[3];
}
void H_27(double *state, double *unused, double *out_6977335032223544616) {
   out_6977335032223544616[0] = 0;
   out_6977335032223544616[1] = 0;
   out_6977335032223544616[2] = 0;
   out_6977335032223544616[3] = 1;
   out_6977335032223544616[4] = 0;
   out_6977335032223544616[5] = 0;
   out_6977335032223544616[6] = 0;
   out_6977335032223544616[7] = 0;
   out_6977335032223544616[8] = 0;
}
void h_29(double *state, double *unused, double *out_1416133831358674750) {
   out_1416133831358674750[0] = state[1];
}
void H_29(double *state, double *unused, double *out_8784414385371189905) {
   out_8784414385371189905[0] = 0;
   out_8784414385371189905[1] = 1;
   out_8784414385371189905[2] = 0;
   out_8784414385371189905[3] = 0;
   out_8784414385371189905[4] = 0;
   out_8784414385371189905[5] = 0;
   out_8784414385371189905[6] = 0;
   out_8784414385371189905[7] = 0;
   out_8784414385371189905[8] = 0;
}
void h_28(double *state, double *unused, double *out_7400645873158492396) {
   out_7400645873158492396[0] = state[0];
}
void H_28(double *state, double *unused, double *out_6820784113805863654) {
   out_6820784113805863654[0] = 1;
   out_6820784113805863654[1] = 0;
   out_6820784113805863654[2] = 0;
   out_6820784113805863654[3] = 0;
   out_6820784113805863654[4] = 0;
   out_6820784113805863654[5] = 0;
   out_6820784113805863654[6] = 0;
   out_6820784113805863654[7] = 0;
   out_6820784113805863654[8] = 0;
}
void h_31(double *state, double *unused, double *out_1803659519959713708) {
   out_1803659519959713708[0] = state[8];
}
void H_31(double *state, double *unused, double *out_9134660820665381591) {
   out_9134660820665381591[0] = 0;
   out_9134660820665381591[1] = 0;
   out_9134660820665381591[2] = 0;
   out_9134660820665381591[3] = 0;
   out_9134660820665381591[4] = 0;
   out_9134660820665381591[5] = 0;
   out_9134660820665381591[6] = 0;
   out_9134660820665381591[7] = 0;
   out_9134660820665381591[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_5070392900769873758) {
  err_fun(nom_x, delta_x, out_5070392900769873758);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_3742760733154016051) {
  inv_err_fun(nom_x, true_x, out_3742760733154016051);
}
void car_H_mod_fun(double *state, double *out_5758456641177717920) {
  H_mod_fun(state, out_5758456641177717920);
}
void car_f_fun(double *state, double dt, double *out_730595102125265078) {
  f_fun(state,  dt, out_730595102125265078);
}
void car_F_fun(double *state, double dt, double *out_7198115545780111359) {
  F_fun(state,  dt, out_7198115545780111359);
}
void car_h_25(double *state, double *unused, double *out_5441109048213736058) {
  h_25(state, unused, out_5441109048213736058);
}
void car_H_25(double *state, double *unused, double *out_4766949399557973891) {
  H_25(state, unused, out_4766949399557973891);
}
void car_h_24(double *state, double *unused, double *out_2797667639827089179) {
  h_24(state, unused, out_2797667639827089179);
}
void car_H_24(double *state, double *unused, double *out_4461115786511221334) {
  H_24(state, unused, out_4461115786511221334);
}
void car_h_30(double *state, double *unused, double *out_1188271489450022901) {
  h_30(state, unused, out_1188271489450022901);
}
void car_H_30(double *state, double *unused, double *out_9152098344023969527) {
  H_30(state, unused, out_9152098344023969527);
}
void car_h_26(double *state, double *unused, double *out_6530138725336053464) {
  h_26(state, unused, out_6530138725336053464);
}
void car_H_26(double *state, double *unused, double *out_8508452718432030115) {
  H_26(state, unused, out_8508452718432030115);
}
void car_h_27(double *state, double *unused, double *out_8003961757834969913) {
  h_27(state, unused, out_8003961757834969913);
}
void car_H_27(double *state, double *unused, double *out_6977335032223544616) {
  H_27(state, unused, out_6977335032223544616);
}
void car_h_29(double *state, double *unused, double *out_1416133831358674750) {
  h_29(state, unused, out_1416133831358674750);
}
void car_H_29(double *state, double *unused, double *out_8784414385371189905) {
  H_29(state, unused, out_8784414385371189905);
}
void car_h_28(double *state, double *unused, double *out_7400645873158492396) {
  h_28(state, unused, out_7400645873158492396);
}
void car_H_28(double *state, double *unused, double *out_6820784113805863654) {
  H_28(state, unused, out_6820784113805863654);
}
void car_h_31(double *state, double *unused, double *out_1803659519959713708) {
  h_31(state, unused, out_1803659519959713708);
}
void car_H_31(double *state, double *unused, double *out_9134660820665381591) {
  H_31(state, unused, out_9134660820665381591);
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
