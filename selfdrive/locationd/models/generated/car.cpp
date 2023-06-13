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
void err_fun(double *nom_x, double *delta_x, double *out_7671677794621234283) {
   out_7671677794621234283[0] = delta_x[0] + nom_x[0];
   out_7671677794621234283[1] = delta_x[1] + nom_x[1];
   out_7671677794621234283[2] = delta_x[2] + nom_x[2];
   out_7671677794621234283[3] = delta_x[3] + nom_x[3];
   out_7671677794621234283[4] = delta_x[4] + nom_x[4];
   out_7671677794621234283[5] = delta_x[5] + nom_x[5];
   out_7671677794621234283[6] = delta_x[6] + nom_x[6];
   out_7671677794621234283[7] = delta_x[7] + nom_x[7];
   out_7671677794621234283[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_3956625128940863804) {
   out_3956625128940863804[0] = -nom_x[0] + true_x[0];
   out_3956625128940863804[1] = -nom_x[1] + true_x[1];
   out_3956625128940863804[2] = -nom_x[2] + true_x[2];
   out_3956625128940863804[3] = -nom_x[3] + true_x[3];
   out_3956625128940863804[4] = -nom_x[4] + true_x[4];
   out_3956625128940863804[5] = -nom_x[5] + true_x[5];
   out_3956625128940863804[6] = -nom_x[6] + true_x[6];
   out_3956625128940863804[7] = -nom_x[7] + true_x[7];
   out_3956625128940863804[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_1750402193623347166) {
   out_1750402193623347166[0] = 1.0;
   out_1750402193623347166[1] = 0;
   out_1750402193623347166[2] = 0;
   out_1750402193623347166[3] = 0;
   out_1750402193623347166[4] = 0;
   out_1750402193623347166[5] = 0;
   out_1750402193623347166[6] = 0;
   out_1750402193623347166[7] = 0;
   out_1750402193623347166[8] = 0;
   out_1750402193623347166[9] = 0;
   out_1750402193623347166[10] = 1.0;
   out_1750402193623347166[11] = 0;
   out_1750402193623347166[12] = 0;
   out_1750402193623347166[13] = 0;
   out_1750402193623347166[14] = 0;
   out_1750402193623347166[15] = 0;
   out_1750402193623347166[16] = 0;
   out_1750402193623347166[17] = 0;
   out_1750402193623347166[18] = 0;
   out_1750402193623347166[19] = 0;
   out_1750402193623347166[20] = 1.0;
   out_1750402193623347166[21] = 0;
   out_1750402193623347166[22] = 0;
   out_1750402193623347166[23] = 0;
   out_1750402193623347166[24] = 0;
   out_1750402193623347166[25] = 0;
   out_1750402193623347166[26] = 0;
   out_1750402193623347166[27] = 0;
   out_1750402193623347166[28] = 0;
   out_1750402193623347166[29] = 0;
   out_1750402193623347166[30] = 1.0;
   out_1750402193623347166[31] = 0;
   out_1750402193623347166[32] = 0;
   out_1750402193623347166[33] = 0;
   out_1750402193623347166[34] = 0;
   out_1750402193623347166[35] = 0;
   out_1750402193623347166[36] = 0;
   out_1750402193623347166[37] = 0;
   out_1750402193623347166[38] = 0;
   out_1750402193623347166[39] = 0;
   out_1750402193623347166[40] = 1.0;
   out_1750402193623347166[41] = 0;
   out_1750402193623347166[42] = 0;
   out_1750402193623347166[43] = 0;
   out_1750402193623347166[44] = 0;
   out_1750402193623347166[45] = 0;
   out_1750402193623347166[46] = 0;
   out_1750402193623347166[47] = 0;
   out_1750402193623347166[48] = 0;
   out_1750402193623347166[49] = 0;
   out_1750402193623347166[50] = 1.0;
   out_1750402193623347166[51] = 0;
   out_1750402193623347166[52] = 0;
   out_1750402193623347166[53] = 0;
   out_1750402193623347166[54] = 0;
   out_1750402193623347166[55] = 0;
   out_1750402193623347166[56] = 0;
   out_1750402193623347166[57] = 0;
   out_1750402193623347166[58] = 0;
   out_1750402193623347166[59] = 0;
   out_1750402193623347166[60] = 1.0;
   out_1750402193623347166[61] = 0;
   out_1750402193623347166[62] = 0;
   out_1750402193623347166[63] = 0;
   out_1750402193623347166[64] = 0;
   out_1750402193623347166[65] = 0;
   out_1750402193623347166[66] = 0;
   out_1750402193623347166[67] = 0;
   out_1750402193623347166[68] = 0;
   out_1750402193623347166[69] = 0;
   out_1750402193623347166[70] = 1.0;
   out_1750402193623347166[71] = 0;
   out_1750402193623347166[72] = 0;
   out_1750402193623347166[73] = 0;
   out_1750402193623347166[74] = 0;
   out_1750402193623347166[75] = 0;
   out_1750402193623347166[76] = 0;
   out_1750402193623347166[77] = 0;
   out_1750402193623347166[78] = 0;
   out_1750402193623347166[79] = 0;
   out_1750402193623347166[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_7591795441338291553) {
   out_7591795441338291553[0] = state[0];
   out_7591795441338291553[1] = state[1];
   out_7591795441338291553[2] = state[2];
   out_7591795441338291553[3] = state[3];
   out_7591795441338291553[4] = state[4];
   out_7591795441338291553[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8000000000000007*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_7591795441338291553[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_7591795441338291553[7] = state[7];
   out_7591795441338291553[8] = state[8];
}
void F_fun(double *state, double dt, double *out_1094147876976225567) {
   out_1094147876976225567[0] = 1;
   out_1094147876976225567[1] = 0;
   out_1094147876976225567[2] = 0;
   out_1094147876976225567[3] = 0;
   out_1094147876976225567[4] = 0;
   out_1094147876976225567[5] = 0;
   out_1094147876976225567[6] = 0;
   out_1094147876976225567[7] = 0;
   out_1094147876976225567[8] = 0;
   out_1094147876976225567[9] = 0;
   out_1094147876976225567[10] = 1;
   out_1094147876976225567[11] = 0;
   out_1094147876976225567[12] = 0;
   out_1094147876976225567[13] = 0;
   out_1094147876976225567[14] = 0;
   out_1094147876976225567[15] = 0;
   out_1094147876976225567[16] = 0;
   out_1094147876976225567[17] = 0;
   out_1094147876976225567[18] = 0;
   out_1094147876976225567[19] = 0;
   out_1094147876976225567[20] = 1;
   out_1094147876976225567[21] = 0;
   out_1094147876976225567[22] = 0;
   out_1094147876976225567[23] = 0;
   out_1094147876976225567[24] = 0;
   out_1094147876976225567[25] = 0;
   out_1094147876976225567[26] = 0;
   out_1094147876976225567[27] = 0;
   out_1094147876976225567[28] = 0;
   out_1094147876976225567[29] = 0;
   out_1094147876976225567[30] = 1;
   out_1094147876976225567[31] = 0;
   out_1094147876976225567[32] = 0;
   out_1094147876976225567[33] = 0;
   out_1094147876976225567[34] = 0;
   out_1094147876976225567[35] = 0;
   out_1094147876976225567[36] = 0;
   out_1094147876976225567[37] = 0;
   out_1094147876976225567[38] = 0;
   out_1094147876976225567[39] = 0;
   out_1094147876976225567[40] = 1;
   out_1094147876976225567[41] = 0;
   out_1094147876976225567[42] = 0;
   out_1094147876976225567[43] = 0;
   out_1094147876976225567[44] = 0;
   out_1094147876976225567[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_1094147876976225567[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_1094147876976225567[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_1094147876976225567[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_1094147876976225567[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_1094147876976225567[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_1094147876976225567[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_1094147876976225567[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_1094147876976225567[53] = -9.8000000000000007*dt;
   out_1094147876976225567[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_1094147876976225567[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_1094147876976225567[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_1094147876976225567[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_1094147876976225567[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_1094147876976225567[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_1094147876976225567[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_1094147876976225567[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_1094147876976225567[62] = 0;
   out_1094147876976225567[63] = 0;
   out_1094147876976225567[64] = 0;
   out_1094147876976225567[65] = 0;
   out_1094147876976225567[66] = 0;
   out_1094147876976225567[67] = 0;
   out_1094147876976225567[68] = 0;
   out_1094147876976225567[69] = 0;
   out_1094147876976225567[70] = 1;
   out_1094147876976225567[71] = 0;
   out_1094147876976225567[72] = 0;
   out_1094147876976225567[73] = 0;
   out_1094147876976225567[74] = 0;
   out_1094147876976225567[75] = 0;
   out_1094147876976225567[76] = 0;
   out_1094147876976225567[77] = 0;
   out_1094147876976225567[78] = 0;
   out_1094147876976225567[79] = 0;
   out_1094147876976225567[80] = 1;
}
void h_25(double *state, double *unused, double *out_3240176429712773857) {
   out_3240176429712773857[0] = state[6];
}
void H_25(double *state, double *unused, double *out_4178007864366031569) {
   out_4178007864366031569[0] = 0;
   out_4178007864366031569[1] = 0;
   out_4178007864366031569[2] = 0;
   out_4178007864366031569[3] = 0;
   out_4178007864366031569[4] = 0;
   out_4178007864366031569[5] = 0;
   out_4178007864366031569[6] = 1;
   out_4178007864366031569[7] = 0;
   out_4178007864366031569[8] = 0;
}
void h_24(double *state, double *unused, double *out_795643072989297307) {
   out_795643072989297307[0] = state[4];
   out_795643072989297307[1] = state[5];
}
void H_24(double *state, double *unused, double *out_8067703529492358621) {
   out_8067703529492358621[0] = 0;
   out_8067703529492358621[1] = 0;
   out_8067703529492358621[2] = 0;
   out_8067703529492358621[3] = 0;
   out_8067703529492358621[4] = 1;
   out_8067703529492358621[5] = 0;
   out_8067703529492358621[6] = 0;
   out_8067703529492358621[7] = 0;
   out_8067703529492358621[8] = 0;
   out_8067703529492358621[9] = 0;
   out_8067703529492358621[10] = 0;
   out_8067703529492358621[11] = 0;
   out_8067703529492358621[12] = 0;
   out_8067703529492358621[13] = 0;
   out_8067703529492358621[14] = 1;
   out_8067703529492358621[15] = 0;
   out_8067703529492358621[16] = 0;
   out_8067703529492358621[17] = 0;
}
void h_30(double *state, double *unused, double *out_5256484251550966135) {
   out_5256484251550966135[0] = state[4];
}
void H_30(double *state, double *unused, double *out_2738682477125585186) {
   out_2738682477125585186[0] = 0;
   out_2738682477125585186[1] = 0;
   out_2738682477125585186[2] = 0;
   out_2738682477125585186[3] = 0;
   out_2738682477125585186[4] = 1;
   out_2738682477125585186[5] = 0;
   out_2738682477125585186[6] = 0;
   out_2738682477125585186[7] = 0;
   out_2738682477125585186[8] = 0;
}
void h_26(double *state, double *unused, double *out_4602097140353744073) {
   out_4602097140353744073[0] = state[7];
}
void H_26(double *state, double *unused, double *out_7919511183240087793) {
   out_7919511183240087793[0] = 0;
   out_7919511183240087793[1] = 0;
   out_7919511183240087793[2] = 0;
   out_7919511183240087793[3] = 0;
   out_7919511183240087793[4] = 0;
   out_7919511183240087793[5] = 0;
   out_7919511183240087793[6] = 0;
   out_7919511183240087793[7] = 1;
   out_7919511183240087793[8] = 0;
}
void h_27(double *state, double *unused, double *out_7638128510994402869) {
   out_7638128510994402869[0] = state[3];
}
void H_27(double *state, double *unused, double *out_563919165325160275) {
   out_563919165325160275[0] = 0;
   out_563919165325160275[1] = 0;
   out_563919165325160275[2] = 0;
   out_563919165325160275[3] = 1;
   out_563919165325160275[4] = 0;
   out_563919165325160275[5] = 0;
   out_563919165325160275[6] = 0;
   out_563919165325160275[7] = 0;
   out_563919165325160275[8] = 0;
}
void h_29(double *state, double *unused, double *out_254810983890120490) {
   out_254810983890120490[0] = state[1];
}
void H_29(double *state, double *unused, double *out_3248913821439977370) {
   out_3248913821439977370[0] = 0;
   out_3248913821439977370[1] = 1;
   out_3248913821439977370[2] = 0;
   out_3248913821439977370[3] = 0;
   out_3248913821439977370[4] = 0;
   out_3248913821439977370[5] = 0;
   out_3248913821439977370[6] = 0;
   out_3248913821439977370[7] = 0;
   out_3248913821439977370[8] = 0;
}
void h_28(double *state, double *unused, double *out_5138476857617589391) {
   out_5138476857617589391[0] = state[0];
}
void H_28(double *state, double *unused, double *out_6231842578613921332) {
   out_6231842578613921332[0] = 1;
   out_6231842578613921332[1] = 0;
   out_6231842578613921332[2] = 0;
   out_6231842578613921332[3] = 0;
   out_6231842578613921332[4] = 0;
   out_6231842578613921332[5] = 0;
   out_6231842578613921332[6] = 0;
   out_6231842578613921332[7] = 0;
   out_6231842578613921332[8] = 0;
}
void h_31(double *state, double *unused, double *out_9039453604025643456) {
   out_9039453604025643456[0] = state[8];
}
void H_31(double *state, double *unused, double *out_4147361902489071141) {
   out_4147361902489071141[0] = 0;
   out_4147361902489071141[1] = 0;
   out_4147361902489071141[2] = 0;
   out_4147361902489071141[3] = 0;
   out_4147361902489071141[4] = 0;
   out_4147361902489071141[5] = 0;
   out_4147361902489071141[6] = 0;
   out_4147361902489071141[7] = 0;
   out_4147361902489071141[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_7671677794621234283) {
  err_fun(nom_x, delta_x, out_7671677794621234283);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_3956625128940863804) {
  inv_err_fun(nom_x, true_x, out_3956625128940863804);
}
void car_H_mod_fun(double *state, double *out_1750402193623347166) {
  H_mod_fun(state, out_1750402193623347166);
}
void car_f_fun(double *state, double dt, double *out_7591795441338291553) {
  f_fun(state,  dt, out_7591795441338291553);
}
void car_F_fun(double *state, double dt, double *out_1094147876976225567) {
  F_fun(state,  dt, out_1094147876976225567);
}
void car_h_25(double *state, double *unused, double *out_3240176429712773857) {
  h_25(state, unused, out_3240176429712773857);
}
void car_H_25(double *state, double *unused, double *out_4178007864366031569) {
  H_25(state, unused, out_4178007864366031569);
}
void car_h_24(double *state, double *unused, double *out_795643072989297307) {
  h_24(state, unused, out_795643072989297307);
}
void car_H_24(double *state, double *unused, double *out_8067703529492358621) {
  H_24(state, unused, out_8067703529492358621);
}
void car_h_30(double *state, double *unused, double *out_5256484251550966135) {
  h_30(state, unused, out_5256484251550966135);
}
void car_H_30(double *state, double *unused, double *out_2738682477125585186) {
  H_30(state, unused, out_2738682477125585186);
}
void car_h_26(double *state, double *unused, double *out_4602097140353744073) {
  h_26(state, unused, out_4602097140353744073);
}
void car_H_26(double *state, double *unused, double *out_7919511183240087793) {
  H_26(state, unused, out_7919511183240087793);
}
void car_h_27(double *state, double *unused, double *out_7638128510994402869) {
  h_27(state, unused, out_7638128510994402869);
}
void car_H_27(double *state, double *unused, double *out_563919165325160275) {
  H_27(state, unused, out_563919165325160275);
}
void car_h_29(double *state, double *unused, double *out_254810983890120490) {
  h_29(state, unused, out_254810983890120490);
}
void car_H_29(double *state, double *unused, double *out_3248913821439977370) {
  H_29(state, unused, out_3248913821439977370);
}
void car_h_28(double *state, double *unused, double *out_5138476857617589391) {
  h_28(state, unused, out_5138476857617589391);
}
void car_H_28(double *state, double *unused, double *out_6231842578613921332) {
  H_28(state, unused, out_6231842578613921332);
}
void car_h_31(double *state, double *unused, double *out_9039453604025643456) {
  h_31(state, unused, out_9039453604025643456);
}
void car_H_31(double *state, double *unused, double *out_4147361902489071141) {
  H_31(state, unused, out_4147361902489071141);
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
