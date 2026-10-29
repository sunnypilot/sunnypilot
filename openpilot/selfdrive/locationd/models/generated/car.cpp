#include "car.h"

namespace {
#define DIM 9
#define EDIM 9
#define MEDIM 9
typedef void (*Hfun)(double *, double *, double *);

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
void err_fun(double *nom_x, double *delta_x, double *out_3585265450871354510) {
   out_3585265450871354510[0] = delta_x[0] + nom_x[0];
   out_3585265450871354510[1] = delta_x[1] + nom_x[1];
   out_3585265450871354510[2] = delta_x[2] + nom_x[2];
   out_3585265450871354510[3] = delta_x[3] + nom_x[3];
   out_3585265450871354510[4] = delta_x[4] + nom_x[4];
   out_3585265450871354510[5] = delta_x[5] + nom_x[5];
   out_3585265450871354510[6] = delta_x[6] + nom_x[6];
   out_3585265450871354510[7] = delta_x[7] + nom_x[7];
   out_3585265450871354510[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_4534440969468340130) {
   out_4534440969468340130[0] = -nom_x[0] + true_x[0];
   out_4534440969468340130[1] = -nom_x[1] + true_x[1];
   out_4534440969468340130[2] = -nom_x[2] + true_x[2];
   out_4534440969468340130[3] = -nom_x[3] + true_x[3];
   out_4534440969468340130[4] = -nom_x[4] + true_x[4];
   out_4534440969468340130[5] = -nom_x[5] + true_x[5];
   out_4534440969468340130[6] = -nom_x[6] + true_x[6];
   out_4534440969468340130[7] = -nom_x[7] + true_x[7];
   out_4534440969468340130[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_7815971298073658297) {
   out_7815971298073658297[0] = 1.0;
   out_7815971298073658297[1] = 0.0;
   out_7815971298073658297[2] = 0.0;
   out_7815971298073658297[3] = 0.0;
   out_7815971298073658297[4] = 0.0;
   out_7815971298073658297[5] = 0.0;
   out_7815971298073658297[6] = 0.0;
   out_7815971298073658297[7] = 0.0;
   out_7815971298073658297[8] = 0.0;
   out_7815971298073658297[9] = 0.0;
   out_7815971298073658297[10] = 1.0;
   out_7815971298073658297[11] = 0.0;
   out_7815971298073658297[12] = 0.0;
   out_7815971298073658297[13] = 0.0;
   out_7815971298073658297[14] = 0.0;
   out_7815971298073658297[15] = 0.0;
   out_7815971298073658297[16] = 0.0;
   out_7815971298073658297[17] = 0.0;
   out_7815971298073658297[18] = 0.0;
   out_7815971298073658297[19] = 0.0;
   out_7815971298073658297[20] = 1.0;
   out_7815971298073658297[21] = 0.0;
   out_7815971298073658297[22] = 0.0;
   out_7815971298073658297[23] = 0.0;
   out_7815971298073658297[24] = 0.0;
   out_7815971298073658297[25] = 0.0;
   out_7815971298073658297[26] = 0.0;
   out_7815971298073658297[27] = 0.0;
   out_7815971298073658297[28] = 0.0;
   out_7815971298073658297[29] = 0.0;
   out_7815971298073658297[30] = 1.0;
   out_7815971298073658297[31] = 0.0;
   out_7815971298073658297[32] = 0.0;
   out_7815971298073658297[33] = 0.0;
   out_7815971298073658297[34] = 0.0;
   out_7815971298073658297[35] = 0.0;
   out_7815971298073658297[36] = 0.0;
   out_7815971298073658297[37] = 0.0;
   out_7815971298073658297[38] = 0.0;
   out_7815971298073658297[39] = 0.0;
   out_7815971298073658297[40] = 1.0;
   out_7815971298073658297[41] = 0.0;
   out_7815971298073658297[42] = 0.0;
   out_7815971298073658297[43] = 0.0;
   out_7815971298073658297[44] = 0.0;
   out_7815971298073658297[45] = 0.0;
   out_7815971298073658297[46] = 0.0;
   out_7815971298073658297[47] = 0.0;
   out_7815971298073658297[48] = 0.0;
   out_7815971298073658297[49] = 0.0;
   out_7815971298073658297[50] = 1.0;
   out_7815971298073658297[51] = 0.0;
   out_7815971298073658297[52] = 0.0;
   out_7815971298073658297[53] = 0.0;
   out_7815971298073658297[54] = 0.0;
   out_7815971298073658297[55] = 0.0;
   out_7815971298073658297[56] = 0.0;
   out_7815971298073658297[57] = 0.0;
   out_7815971298073658297[58] = 0.0;
   out_7815971298073658297[59] = 0.0;
   out_7815971298073658297[60] = 1.0;
   out_7815971298073658297[61] = 0.0;
   out_7815971298073658297[62] = 0.0;
   out_7815971298073658297[63] = 0.0;
   out_7815971298073658297[64] = 0.0;
   out_7815971298073658297[65] = 0.0;
   out_7815971298073658297[66] = 0.0;
   out_7815971298073658297[67] = 0.0;
   out_7815971298073658297[68] = 0.0;
   out_7815971298073658297[69] = 0.0;
   out_7815971298073658297[70] = 1.0;
   out_7815971298073658297[71] = 0.0;
   out_7815971298073658297[72] = 0.0;
   out_7815971298073658297[73] = 0.0;
   out_7815971298073658297[74] = 0.0;
   out_7815971298073658297[75] = 0.0;
   out_7815971298073658297[76] = 0.0;
   out_7815971298073658297[77] = 0.0;
   out_7815971298073658297[78] = 0.0;
   out_7815971298073658297[79] = 0.0;
   out_7815971298073658297[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_3011916394083426809) {
   out_3011916394083426809[0] = state[0];
   out_3011916394083426809[1] = state[1];
   out_3011916394083426809[2] = state[2];
   out_3011916394083426809[3] = state[3];
   out_3011916394083426809[4] = state[4];
   out_3011916394083426809[5] = dt*(stiffness_front*(-state[2] - state[3] + state[7])*state[0]/state[1] + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/state[4] + ((-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/state[4] - state[4])*state[6] - 9.8100000000000005*state[8]) + state[5];
   out_3011916394083426809[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_3011916394083426809[7] = state[7];
   out_3011916394083426809[8] = state[8];
}
void F_fun(double *state, double dt, double *out_4768916904116545459) {
   out_4768916904116545459[0] = 1;
   out_4768916904116545459[1] = 0;
   out_4768916904116545459[2] = 0;
   out_4768916904116545459[3] = 0;
   out_4768916904116545459[4] = 0;
   out_4768916904116545459[5] = 0;
   out_4768916904116545459[6] = 0;
   out_4768916904116545459[7] = 0;
   out_4768916904116545459[8] = 0;
   out_4768916904116545459[9] = 0;
   out_4768916904116545459[10] = 1;
   out_4768916904116545459[11] = 0;
   out_4768916904116545459[12] = 0;
   out_4768916904116545459[13] = 0;
   out_4768916904116545459[14] = 0;
   out_4768916904116545459[15] = 0;
   out_4768916904116545459[16] = 0;
   out_4768916904116545459[17] = 0;
   out_4768916904116545459[18] = 0;
   out_4768916904116545459[19] = 0;
   out_4768916904116545459[20] = 1;
   out_4768916904116545459[21] = 0;
   out_4768916904116545459[22] = 0;
   out_4768916904116545459[23] = 0;
   out_4768916904116545459[24] = 0;
   out_4768916904116545459[25] = 0;
   out_4768916904116545459[26] = 0;
   out_4768916904116545459[27] = 0;
   out_4768916904116545459[28] = 0;
   out_4768916904116545459[29] = 0;
   out_4768916904116545459[30] = 1;
   out_4768916904116545459[31] = 0;
   out_4768916904116545459[32] = 0;
   out_4768916904116545459[33] = 0;
   out_4768916904116545459[34] = 0;
   out_4768916904116545459[35] = 0;
   out_4768916904116545459[36] = 0;
   out_4768916904116545459[37] = 0;
   out_4768916904116545459[38] = 0;
   out_4768916904116545459[39] = 0;
   out_4768916904116545459[40] = 1;
   out_4768916904116545459[41] = 0;
   out_4768916904116545459[42] = 0;
   out_4768916904116545459[43] = 0;
   out_4768916904116545459[44] = 0;
   out_4768916904116545459[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/state[1] + (-stiffness_front - stiffness_rear)*state[5]/state[4] + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/state[4]);
   out_4768916904116545459[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/pow(state[1], 2);
   out_4768916904116545459[47] = -dt*stiffness_front*state[0]/state[1];
   out_4768916904116545459[48] = -dt*stiffness_front*state[0]/state[1];
   out_4768916904116545459[49] = dt*(-(-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/pow(state[4], 2) + (-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/pow(state[4], 2) - 1)*state[6]);
   out_4768916904116545459[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/state[4] + 1;
   out_4768916904116545459[51] = dt*((-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/state[4] - state[4]);
   out_4768916904116545459[52] = dt*stiffness_front*state[0]/state[1];
   out_4768916904116545459[53] = -9.8100000000000005*dt;
   out_4768916904116545459[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_4768916904116545459[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_4768916904116545459[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_4768916904116545459[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_4768916904116545459[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_4768916904116545459[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_4768916904116545459[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_4768916904116545459[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_4768916904116545459[62] = 0;
   out_4768916904116545459[63] = 0;
   out_4768916904116545459[64] = 0;
   out_4768916904116545459[65] = 0;
   out_4768916904116545459[66] = 0;
   out_4768916904116545459[67] = 0;
   out_4768916904116545459[68] = 0;
   out_4768916904116545459[69] = 0;
   out_4768916904116545459[70] = 1;
   out_4768916904116545459[71] = 0;
   out_4768916904116545459[72] = 0;
   out_4768916904116545459[73] = 0;
   out_4768916904116545459[74] = 0;
   out_4768916904116545459[75] = 0;
   out_4768916904116545459[76] = 0;
   out_4768916904116545459[77] = 0;
   out_4768916904116545459[78] = 0;
   out_4768916904116545459[79] = 0;
   out_4768916904116545459[80] = 1;
}
void h_25(double *state, double *unused, double *out_8627167620031889565) {
   out_8627167620031889565[0] = state[6];
}
void H_25(double *state, double *unused, double *out_1719062931467283681) {
   out_1719062931467283681[0] = 0;
   out_1719062931467283681[1] = 0;
   out_1719062931467283681[2] = 0;
   out_1719062931467283681[3] = 0;
   out_1719062931467283681[4] = 0;
   out_1719062931467283681[5] = 0;
   out_1719062931467283681[6] = 1;
   out_1719062931467283681[7] = 0;
   out_1719062931467283681[8] = 0;
}
void h_24(double *state, double *unused, double *out_5179238137807796494) {
   out_5179238137807796494[0] = state[4];
   out_5179238137807796494[1] = state[5];
}
void H_24(double *state, double *unused, double *out_453586667538215885) {
   out_453586667538215885[0] = 0;
   out_453586667538215885[1] = 0;
   out_453586667538215885[2] = 0;
   out_453586667538215885[3] = 0;
   out_453586667538215885[4] = 1;
   out_453586667538215885[5] = 0;
   out_453586667538215885[6] = 0;
   out_453586667538215885[7] = 0;
   out_453586667538215885[8] = 0;
   out_453586667538215885[9] = 0;
   out_453586667538215885[10] = 0;
   out_453586667538215885[11] = 0;
   out_453586667538215885[12] = 0;
   out_453586667538215885[13] = 0;
   out_453586667538215885[14] = 1;
   out_453586667538215885[15] = 0;
   out_453586667538215885[16] = 0;
   out_453586667538215885[17] = 0;
}
void h_30(double *state, double *unused, double *out_4528864321752517701) {
   out_4528864321752517701[0] = state[4];
}
void H_30(double *state, double *unused, double *out_4237395889974532308) {
   out_4237395889974532308[0] = 0;
   out_4237395889974532308[1] = 0;
   out_4237395889974532308[2] = 0;
   out_4237395889974532308[3] = 0;
   out_4237395889974532308[4] = 1;
   out_4237395889974532308[5] = 0;
   out_4237395889974532308[6] = 0;
   out_4237395889974532308[7] = 0;
   out_4237395889974532308[8] = 0;
}
void h_26(double *state, double *unused, double *out_5472374174654180136) {
   out_5472374174654180136[0] = state[7];
}
void H_26(double *state, double *unused, double *out_2022440387406772543) {
   out_2022440387406772543[0] = 0;
   out_2022440387406772543[1] = 0;
   out_2022440387406772543[2] = 0;
   out_2022440387406772543[3] = 0;
   out_2022440387406772543[4] = 0;
   out_2022440387406772543[5] = 0;
   out_2022440387406772543[6] = 0;
   out_2022440387406772543[7] = 1;
   out_2022440387406772543[8] = 0;
}
void h_27(double *state, double *unused, double *out_2749092444325053967) {
   out_2749092444325053967[0] = state[3];
}
void H_27(double *state, double *unused, double *out_6460989961158475525) {
   out_6460989961158475525[0] = 0;
   out_6460989961158475525[1] = 0;
   out_6460989961158475525[2] = 0;
   out_6460989961158475525[3] = 1;
   out_6460989961158475525[4] = 0;
   out_6460989961158475525[5] = 0;
   out_6460989961158475525[6] = 0;
   out_6460989961158475525[7] = 0;
   out_6460989961158475525[8] = 0;
}
void h_29(double *state, double *unused, double *out_5132180206428995218) {
   out_5132180206428995218[0] = state[1];
}
void H_29(double *state, double *unused, double *out_4747627234288924492) {
   out_4747627234288924492[0] = 0;
   out_4747627234288924492[1] = 1;
   out_4747627234288924492[2] = 0;
   out_4747627234288924492[3] = 0;
   out_4747627234288924492[4] = 0;
   out_4747627234288924492[5] = 0;
   out_4747627234288924492[6] = 0;
   out_4747627234288924492[7] = 0;
   out_4747627234288924492[8] = 0;
}
void h_28(double *state, double *unused, double *out_9148133961738903113) {
   out_9148133961738903113[0] = state[0];
}
void H_28(double *state, double *unused, double *out_334771782780606082) {
   out_334771782780606082[0] = 1;
   out_334771782780606082[1] = 0;
   out_334771782780606082[2] = 0;
   out_334771782780606082[3] = 0;
   out_334771782780606082[4] = 0;
   out_334771782780606082[5] = 0;
   out_334771782780606082[6] = 0;
   out_334771782780606082[7] = 0;
   out_334771782780606082[8] = 0;
}
void h_31(double *state, double *unused, double *out_745894969277840380) {
   out_745894969277840380[0] = state[8];
}
void H_31(double *state, double *unused, double *out_2648648489640124019) {
   out_2648648489640124019[0] = 0;
   out_2648648489640124019[1] = 0;
   out_2648648489640124019[2] = 0;
   out_2648648489640124019[3] = 0;
   out_2648648489640124019[4] = 0;
   out_2648648489640124019[5] = 0;
   out_2648648489640124019[6] = 0;
   out_2648648489640124019[7] = 0;
   out_2648648489640124019[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_3585265450871354510) {
  err_fun(nom_x, delta_x, out_3585265450871354510);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_4534440969468340130) {
  inv_err_fun(nom_x, true_x, out_4534440969468340130);
}
void car_H_mod_fun(double *state, double *out_7815971298073658297) {
  H_mod_fun(state, out_7815971298073658297);
}
void car_f_fun(double *state, double dt, double *out_3011916394083426809) {
  f_fun(state,  dt, out_3011916394083426809);
}
void car_F_fun(double *state, double dt, double *out_4768916904116545459) {
  F_fun(state,  dt, out_4768916904116545459);
}
void car_h_25(double *state, double *unused, double *out_8627167620031889565) {
  h_25(state, unused, out_8627167620031889565);
}
void car_H_25(double *state, double *unused, double *out_1719062931467283681) {
  H_25(state, unused, out_1719062931467283681);
}
void car_h_24(double *state, double *unused, double *out_5179238137807796494) {
  h_24(state, unused, out_5179238137807796494);
}
void car_H_24(double *state, double *unused, double *out_453586667538215885) {
  H_24(state, unused, out_453586667538215885);
}
void car_h_30(double *state, double *unused, double *out_4528864321752517701) {
  h_30(state, unused, out_4528864321752517701);
}
void car_H_30(double *state, double *unused, double *out_4237395889974532308) {
  H_30(state, unused, out_4237395889974532308);
}
void car_h_26(double *state, double *unused, double *out_5472374174654180136) {
  h_26(state, unused, out_5472374174654180136);
}
void car_H_26(double *state, double *unused, double *out_2022440387406772543) {
  H_26(state, unused, out_2022440387406772543);
}
void car_h_27(double *state, double *unused, double *out_2749092444325053967) {
  h_27(state, unused, out_2749092444325053967);
}
void car_H_27(double *state, double *unused, double *out_6460989961158475525) {
  H_27(state, unused, out_6460989961158475525);
}
void car_h_29(double *state, double *unused, double *out_5132180206428995218) {
  h_29(state, unused, out_5132180206428995218);
}
void car_H_29(double *state, double *unused, double *out_4747627234288924492) {
  H_29(state, unused, out_4747627234288924492);
}
void car_h_28(double *state, double *unused, double *out_9148133961738903113) {
  h_28(state, unused, out_9148133961738903113);
}
void car_H_28(double *state, double *unused, double *out_334771782780606082) {
  H_28(state, unused, out_334771782780606082);
}
void car_h_31(double *state, double *unused, double *out_745894969277840380) {
  h_31(state, unused, out_745894969277840380);
}
void car_H_31(double *state, double *unused, double *out_2648648489640124019) {
  H_31(state, unused, out_2648648489640124019);
}
void car_predict(double *in_x, double *in_P, double *in_Q, double dt) {
  predict(in_x, in_P, in_Q, dt);
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
