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
void err_fun(double *nom_x, double *delta_x, double *out_5123805303118663312) {
   out_5123805303118663312[0] = delta_x[0] + nom_x[0];
   out_5123805303118663312[1] = delta_x[1] + nom_x[1];
   out_5123805303118663312[2] = delta_x[2] + nom_x[2];
   out_5123805303118663312[3] = delta_x[3] + nom_x[3];
   out_5123805303118663312[4] = delta_x[4] + nom_x[4];
   out_5123805303118663312[5] = delta_x[5] + nom_x[5];
   out_5123805303118663312[6] = delta_x[6] + nom_x[6];
   out_5123805303118663312[7] = delta_x[7] + nom_x[7];
   out_5123805303118663312[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_6837749996360934905) {
   out_6837749996360934905[0] = -nom_x[0] + true_x[0];
   out_6837749996360934905[1] = -nom_x[1] + true_x[1];
   out_6837749996360934905[2] = -nom_x[2] + true_x[2];
   out_6837749996360934905[3] = -nom_x[3] + true_x[3];
   out_6837749996360934905[4] = -nom_x[4] + true_x[4];
   out_6837749996360934905[5] = -nom_x[5] + true_x[5];
   out_6837749996360934905[6] = -nom_x[6] + true_x[6];
   out_6837749996360934905[7] = -nom_x[7] + true_x[7];
   out_6837749996360934905[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_1004474096501644305) {
   out_1004474096501644305[0] = 1.0;
   out_1004474096501644305[1] = 0;
   out_1004474096501644305[2] = 0;
   out_1004474096501644305[3] = 0;
   out_1004474096501644305[4] = 0;
   out_1004474096501644305[5] = 0;
   out_1004474096501644305[6] = 0;
   out_1004474096501644305[7] = 0;
   out_1004474096501644305[8] = 0;
   out_1004474096501644305[9] = 0;
   out_1004474096501644305[10] = 1.0;
   out_1004474096501644305[11] = 0;
   out_1004474096501644305[12] = 0;
   out_1004474096501644305[13] = 0;
   out_1004474096501644305[14] = 0;
   out_1004474096501644305[15] = 0;
   out_1004474096501644305[16] = 0;
   out_1004474096501644305[17] = 0;
   out_1004474096501644305[18] = 0;
   out_1004474096501644305[19] = 0;
   out_1004474096501644305[20] = 1.0;
   out_1004474096501644305[21] = 0;
   out_1004474096501644305[22] = 0;
   out_1004474096501644305[23] = 0;
   out_1004474096501644305[24] = 0;
   out_1004474096501644305[25] = 0;
   out_1004474096501644305[26] = 0;
   out_1004474096501644305[27] = 0;
   out_1004474096501644305[28] = 0;
   out_1004474096501644305[29] = 0;
   out_1004474096501644305[30] = 1.0;
   out_1004474096501644305[31] = 0;
   out_1004474096501644305[32] = 0;
   out_1004474096501644305[33] = 0;
   out_1004474096501644305[34] = 0;
   out_1004474096501644305[35] = 0;
   out_1004474096501644305[36] = 0;
   out_1004474096501644305[37] = 0;
   out_1004474096501644305[38] = 0;
   out_1004474096501644305[39] = 0;
   out_1004474096501644305[40] = 1.0;
   out_1004474096501644305[41] = 0;
   out_1004474096501644305[42] = 0;
   out_1004474096501644305[43] = 0;
   out_1004474096501644305[44] = 0;
   out_1004474096501644305[45] = 0;
   out_1004474096501644305[46] = 0;
   out_1004474096501644305[47] = 0;
   out_1004474096501644305[48] = 0;
   out_1004474096501644305[49] = 0;
   out_1004474096501644305[50] = 1.0;
   out_1004474096501644305[51] = 0;
   out_1004474096501644305[52] = 0;
   out_1004474096501644305[53] = 0;
   out_1004474096501644305[54] = 0;
   out_1004474096501644305[55] = 0;
   out_1004474096501644305[56] = 0;
   out_1004474096501644305[57] = 0;
   out_1004474096501644305[58] = 0;
   out_1004474096501644305[59] = 0;
   out_1004474096501644305[60] = 1.0;
   out_1004474096501644305[61] = 0;
   out_1004474096501644305[62] = 0;
   out_1004474096501644305[63] = 0;
   out_1004474096501644305[64] = 0;
   out_1004474096501644305[65] = 0;
   out_1004474096501644305[66] = 0;
   out_1004474096501644305[67] = 0;
   out_1004474096501644305[68] = 0;
   out_1004474096501644305[69] = 0;
   out_1004474096501644305[70] = 1.0;
   out_1004474096501644305[71] = 0;
   out_1004474096501644305[72] = 0;
   out_1004474096501644305[73] = 0;
   out_1004474096501644305[74] = 0;
   out_1004474096501644305[75] = 0;
   out_1004474096501644305[76] = 0;
   out_1004474096501644305[77] = 0;
   out_1004474096501644305[78] = 0;
   out_1004474096501644305[79] = 0;
   out_1004474096501644305[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_4352460870670239441) {
   out_4352460870670239441[0] = state[0];
   out_4352460870670239441[1] = state[1];
   out_4352460870670239441[2] = state[2];
   out_4352460870670239441[3] = state[3];
   out_4352460870670239441[4] = state[4];
   out_4352460870670239441[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8000000000000007*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_4352460870670239441[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_4352460870670239441[7] = state[7];
   out_4352460870670239441[8] = state[8];
}
void F_fun(double *state, double dt, double *out_4167083004924647729) {
   out_4167083004924647729[0] = 1;
   out_4167083004924647729[1] = 0;
   out_4167083004924647729[2] = 0;
   out_4167083004924647729[3] = 0;
   out_4167083004924647729[4] = 0;
   out_4167083004924647729[5] = 0;
   out_4167083004924647729[6] = 0;
   out_4167083004924647729[7] = 0;
   out_4167083004924647729[8] = 0;
   out_4167083004924647729[9] = 0;
   out_4167083004924647729[10] = 1;
   out_4167083004924647729[11] = 0;
   out_4167083004924647729[12] = 0;
   out_4167083004924647729[13] = 0;
   out_4167083004924647729[14] = 0;
   out_4167083004924647729[15] = 0;
   out_4167083004924647729[16] = 0;
   out_4167083004924647729[17] = 0;
   out_4167083004924647729[18] = 0;
   out_4167083004924647729[19] = 0;
   out_4167083004924647729[20] = 1;
   out_4167083004924647729[21] = 0;
   out_4167083004924647729[22] = 0;
   out_4167083004924647729[23] = 0;
   out_4167083004924647729[24] = 0;
   out_4167083004924647729[25] = 0;
   out_4167083004924647729[26] = 0;
   out_4167083004924647729[27] = 0;
   out_4167083004924647729[28] = 0;
   out_4167083004924647729[29] = 0;
   out_4167083004924647729[30] = 1;
   out_4167083004924647729[31] = 0;
   out_4167083004924647729[32] = 0;
   out_4167083004924647729[33] = 0;
   out_4167083004924647729[34] = 0;
   out_4167083004924647729[35] = 0;
   out_4167083004924647729[36] = 0;
   out_4167083004924647729[37] = 0;
   out_4167083004924647729[38] = 0;
   out_4167083004924647729[39] = 0;
   out_4167083004924647729[40] = 1;
   out_4167083004924647729[41] = 0;
   out_4167083004924647729[42] = 0;
   out_4167083004924647729[43] = 0;
   out_4167083004924647729[44] = 0;
   out_4167083004924647729[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_4167083004924647729[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_4167083004924647729[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_4167083004924647729[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_4167083004924647729[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_4167083004924647729[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_4167083004924647729[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_4167083004924647729[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_4167083004924647729[53] = -9.8000000000000007*dt;
   out_4167083004924647729[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_4167083004924647729[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_4167083004924647729[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_4167083004924647729[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_4167083004924647729[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_4167083004924647729[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_4167083004924647729[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_4167083004924647729[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_4167083004924647729[62] = 0;
   out_4167083004924647729[63] = 0;
   out_4167083004924647729[64] = 0;
   out_4167083004924647729[65] = 0;
   out_4167083004924647729[66] = 0;
   out_4167083004924647729[67] = 0;
   out_4167083004924647729[68] = 0;
   out_4167083004924647729[69] = 0;
   out_4167083004924647729[70] = 1;
   out_4167083004924647729[71] = 0;
   out_4167083004924647729[72] = 0;
   out_4167083004924647729[73] = 0;
   out_4167083004924647729[74] = 0;
   out_4167083004924647729[75] = 0;
   out_4167083004924647729[76] = 0;
   out_4167083004924647729[77] = 0;
   out_4167083004924647729[78] = 0;
   out_4167083004924647729[79] = 0;
   out_4167083004924647729[80] = 1;
}
void h_25(double *state, double *unused, double *out_7195362026210797347) {
   out_7195362026210797347[0] = state[6];
}
void H_25(double *state, double *unused, double *out_517600271157786473) {
   out_517600271157786473[0] = 0;
   out_517600271157786473[1] = 0;
   out_517600271157786473[2] = 0;
   out_517600271157786473[3] = 0;
   out_517600271157786473[4] = 0;
   out_517600271157786473[5] = 0;
   out_517600271157786473[6] = 1;
   out_517600271157786473[7] = 0;
   out_517600271157786473[8] = 0;
}
void h_24(double *state, double *unused, double *out_1170089474205098434) {
   out_1170089474205098434[0] = state[4];
   out_1170089474205098434[1] = state[5];
}
void H_24(double *state, double *unused, double *out_6057971535433731628) {
   out_6057971535433731628[0] = 0;
   out_6057971535433731628[1] = 0;
   out_6057971535433731628[2] = 0;
   out_6057971535433731628[3] = 0;
   out_6057971535433731628[4] = 1;
   out_6057971535433731628[5] = 0;
   out_6057971535433731628[6] = 0;
   out_6057971535433731628[7] = 0;
   out_6057971535433731628[8] = 0;
   out_6057971535433731628[9] = 0;
   out_6057971535433731628[10] = 0;
   out_6057971535433731628[11] = 0;
   out_6057971535433731628[12] = 0;
   out_6057971535433731628[13] = 0;
   out_6057971535433731628[14] = 1;
   out_6057971535433731628[15] = 0;
   out_6057971535433731628[16] = 0;
   out_6057971535433731628[17] = 0;
}
void h_30(double *state, double *unused, double *out_8645993418839680514) {
   out_8645993418839680514[0] = state[4];
}
void H_30(double *state, double *unused, double *out_2000732687349462154) {
   out_2000732687349462154[0] = 0;
   out_2000732687349462154[1] = 0;
   out_2000732687349462154[2] = 0;
   out_2000732687349462154[3] = 0;
   out_2000732687349462154[4] = 1;
   out_2000732687349462154[5] = 0;
   out_2000732687349462154[6] = 0;
   out_2000732687349462154[7] = 0;
   out_2000732687349462154[8] = 0;
}
void h_26(double *state, double *unused, double *out_4315762643117593807) {
   out_4315762643117593807[0] = state[7];
}
void H_26(double *state, double *unused, double *out_4259103590031842697) {
   out_4259103590031842697[0] = 0;
   out_4259103590031842697[1] = 0;
   out_4259103590031842697[2] = 0;
   out_4259103590031842697[3] = 0;
   out_4259103590031842697[4] = 0;
   out_4259103590031842697[5] = 0;
   out_4259103590031842697[6] = 0;
   out_4259103590031842697[7] = 1;
   out_4259103590031842697[8] = 0;
}
void h_27(double *state, double *unused, double *out_6592046141534319830) {
   out_6592046141534319830[0] = state[3];
}
void H_27(double *state, double *unused, double *out_4224326758533405371) {
   out_4224326758533405371[0] = 0;
   out_4224326758533405371[1] = 0;
   out_4224326758533405371[2] = 0;
   out_4224326758533405371[3] = 1;
   out_4224326758533405371[4] = 0;
   out_4224326758533405371[5] = 0;
   out_4224326758533405371[6] = 0;
   out_4224326758533405371[7] = 0;
   out_4224326758533405371[8] = 0;
}
void h_29(double *state, double *unused, double *out_3644320151178834869) {
   out_3644320151178834869[0] = state[1];
}
void H_29(double *state, double *unused, double *out_2510964031663854338) {
   out_2510964031663854338[0] = 0;
   out_2510964031663854338[1] = 1;
   out_2510964031663854338[2] = 0;
   out_2510964031663854338[3] = 0;
   out_2510964031663854338[4] = 0;
   out_2510964031663854338[5] = 0;
   out_2510964031663854338[6] = 0;
   out_2510964031663854338[7] = 0;
   out_2510964031663854338[8] = 0;
}
void h_28(double *state, double *unused, double *out_2872728760168391021) {
   out_2872728760168391021[0] = state[0];
}
void H_28(double *state, double *unused, double *out_2571434985405676236) {
   out_2571434985405676236[0] = 1;
   out_2571434985405676236[1] = 0;
   out_2571434985405676236[2] = 0;
   out_2571434985405676236[3] = 0;
   out_2571434985405676236[4] = 0;
   out_2571434985405676236[5] = 0;
   out_2571434985405676236[6] = 0;
   out_2571434985405676236[7] = 0;
   out_2571434985405676236[8] = 0;
}
void h_31(double *state, double *unused, double *out_424526799860446411) {
   out_424526799860446411[0] = state[8];
}
void H_31(double *state, double *unused, double *out_486954309280826045) {
   out_486954309280826045[0] = 0;
   out_486954309280826045[1] = 0;
   out_486954309280826045[2] = 0;
   out_486954309280826045[3] = 0;
   out_486954309280826045[4] = 0;
   out_486954309280826045[5] = 0;
   out_486954309280826045[6] = 0;
   out_486954309280826045[7] = 0;
   out_486954309280826045[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_5123805303118663312) {
  err_fun(nom_x, delta_x, out_5123805303118663312);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_6837749996360934905) {
  inv_err_fun(nom_x, true_x, out_6837749996360934905);
}
void car_H_mod_fun(double *state, double *out_1004474096501644305) {
  H_mod_fun(state, out_1004474096501644305);
}
void car_f_fun(double *state, double dt, double *out_4352460870670239441) {
  f_fun(state,  dt, out_4352460870670239441);
}
void car_F_fun(double *state, double dt, double *out_4167083004924647729) {
  F_fun(state,  dt, out_4167083004924647729);
}
void car_h_25(double *state, double *unused, double *out_7195362026210797347) {
  h_25(state, unused, out_7195362026210797347);
}
void car_H_25(double *state, double *unused, double *out_517600271157786473) {
  H_25(state, unused, out_517600271157786473);
}
void car_h_24(double *state, double *unused, double *out_1170089474205098434) {
  h_24(state, unused, out_1170089474205098434);
}
void car_H_24(double *state, double *unused, double *out_6057971535433731628) {
  H_24(state, unused, out_6057971535433731628);
}
void car_h_30(double *state, double *unused, double *out_8645993418839680514) {
  h_30(state, unused, out_8645993418839680514);
}
void car_H_30(double *state, double *unused, double *out_2000732687349462154) {
  H_30(state, unused, out_2000732687349462154);
}
void car_h_26(double *state, double *unused, double *out_4315762643117593807) {
  h_26(state, unused, out_4315762643117593807);
}
void car_H_26(double *state, double *unused, double *out_4259103590031842697) {
  H_26(state, unused, out_4259103590031842697);
}
void car_h_27(double *state, double *unused, double *out_6592046141534319830) {
  h_27(state, unused, out_6592046141534319830);
}
void car_H_27(double *state, double *unused, double *out_4224326758533405371) {
  H_27(state, unused, out_4224326758533405371);
}
void car_h_29(double *state, double *unused, double *out_3644320151178834869) {
  h_29(state, unused, out_3644320151178834869);
}
void car_H_29(double *state, double *unused, double *out_2510964031663854338) {
  H_29(state, unused, out_2510964031663854338);
}
void car_h_28(double *state, double *unused, double *out_2872728760168391021) {
  h_28(state, unused, out_2872728760168391021);
}
void car_H_28(double *state, double *unused, double *out_2571434985405676236) {
  H_28(state, unused, out_2571434985405676236);
}
void car_h_31(double *state, double *unused, double *out_424526799860446411) {
  h_31(state, unused, out_424526799860446411);
}
void car_H_31(double *state, double *unused, double *out_486954309280826045) {
  H_31(state, unused, out_486954309280826045);
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
