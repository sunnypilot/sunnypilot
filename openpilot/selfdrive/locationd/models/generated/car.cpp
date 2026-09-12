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
void err_fun(double *nom_x, double *delta_x, double *out_2496243277963511837) {
   out_2496243277963511837[0] = delta_x[0] + nom_x[0];
   out_2496243277963511837[1] = delta_x[1] + nom_x[1];
   out_2496243277963511837[2] = delta_x[2] + nom_x[2];
   out_2496243277963511837[3] = delta_x[3] + nom_x[3];
   out_2496243277963511837[4] = delta_x[4] + nom_x[4];
   out_2496243277963511837[5] = delta_x[5] + nom_x[5];
   out_2496243277963511837[6] = delta_x[6] + nom_x[6];
   out_2496243277963511837[7] = delta_x[7] + nom_x[7];
   out_2496243277963511837[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_8723072931307095264) {
   out_8723072931307095264[0] = -nom_x[0] + true_x[0];
   out_8723072931307095264[1] = -nom_x[1] + true_x[1];
   out_8723072931307095264[2] = -nom_x[2] + true_x[2];
   out_8723072931307095264[3] = -nom_x[3] + true_x[3];
   out_8723072931307095264[4] = -nom_x[4] + true_x[4];
   out_8723072931307095264[5] = -nom_x[5] + true_x[5];
   out_8723072931307095264[6] = -nom_x[6] + true_x[6];
   out_8723072931307095264[7] = -nom_x[7] + true_x[7];
   out_8723072931307095264[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_2432465619939465173) {
   out_2432465619939465173[0] = 1.0;
   out_2432465619939465173[1] = 0.0;
   out_2432465619939465173[2] = 0.0;
   out_2432465619939465173[3] = 0.0;
   out_2432465619939465173[4] = 0.0;
   out_2432465619939465173[5] = 0.0;
   out_2432465619939465173[6] = 0.0;
   out_2432465619939465173[7] = 0.0;
   out_2432465619939465173[8] = 0.0;
   out_2432465619939465173[9] = 0.0;
   out_2432465619939465173[10] = 1.0;
   out_2432465619939465173[11] = 0.0;
   out_2432465619939465173[12] = 0.0;
   out_2432465619939465173[13] = 0.0;
   out_2432465619939465173[14] = 0.0;
   out_2432465619939465173[15] = 0.0;
   out_2432465619939465173[16] = 0.0;
   out_2432465619939465173[17] = 0.0;
   out_2432465619939465173[18] = 0.0;
   out_2432465619939465173[19] = 0.0;
   out_2432465619939465173[20] = 1.0;
   out_2432465619939465173[21] = 0.0;
   out_2432465619939465173[22] = 0.0;
   out_2432465619939465173[23] = 0.0;
   out_2432465619939465173[24] = 0.0;
   out_2432465619939465173[25] = 0.0;
   out_2432465619939465173[26] = 0.0;
   out_2432465619939465173[27] = 0.0;
   out_2432465619939465173[28] = 0.0;
   out_2432465619939465173[29] = 0.0;
   out_2432465619939465173[30] = 1.0;
   out_2432465619939465173[31] = 0.0;
   out_2432465619939465173[32] = 0.0;
   out_2432465619939465173[33] = 0.0;
   out_2432465619939465173[34] = 0.0;
   out_2432465619939465173[35] = 0.0;
   out_2432465619939465173[36] = 0.0;
   out_2432465619939465173[37] = 0.0;
   out_2432465619939465173[38] = 0.0;
   out_2432465619939465173[39] = 0.0;
   out_2432465619939465173[40] = 1.0;
   out_2432465619939465173[41] = 0.0;
   out_2432465619939465173[42] = 0.0;
   out_2432465619939465173[43] = 0.0;
   out_2432465619939465173[44] = 0.0;
   out_2432465619939465173[45] = 0.0;
   out_2432465619939465173[46] = 0.0;
   out_2432465619939465173[47] = 0.0;
   out_2432465619939465173[48] = 0.0;
   out_2432465619939465173[49] = 0.0;
   out_2432465619939465173[50] = 1.0;
   out_2432465619939465173[51] = 0.0;
   out_2432465619939465173[52] = 0.0;
   out_2432465619939465173[53] = 0.0;
   out_2432465619939465173[54] = 0.0;
   out_2432465619939465173[55] = 0.0;
   out_2432465619939465173[56] = 0.0;
   out_2432465619939465173[57] = 0.0;
   out_2432465619939465173[58] = 0.0;
   out_2432465619939465173[59] = 0.0;
   out_2432465619939465173[60] = 1.0;
   out_2432465619939465173[61] = 0.0;
   out_2432465619939465173[62] = 0.0;
   out_2432465619939465173[63] = 0.0;
   out_2432465619939465173[64] = 0.0;
   out_2432465619939465173[65] = 0.0;
   out_2432465619939465173[66] = 0.0;
   out_2432465619939465173[67] = 0.0;
   out_2432465619939465173[68] = 0.0;
   out_2432465619939465173[69] = 0.0;
   out_2432465619939465173[70] = 1.0;
   out_2432465619939465173[71] = 0.0;
   out_2432465619939465173[72] = 0.0;
   out_2432465619939465173[73] = 0.0;
   out_2432465619939465173[74] = 0.0;
   out_2432465619939465173[75] = 0.0;
   out_2432465619939465173[76] = 0.0;
   out_2432465619939465173[77] = 0.0;
   out_2432465619939465173[78] = 0.0;
   out_2432465619939465173[79] = 0.0;
   out_2432465619939465173[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_433459712136092591) {
   out_433459712136092591[0] = state[0];
   out_433459712136092591[1] = state[1];
   out_433459712136092591[2] = state[2];
   out_433459712136092591[3] = state[3];
   out_433459712136092591[4] = state[4];
   out_433459712136092591[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8100000000000005*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_433459712136092591[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_433459712136092591[7] = state[7];
   out_433459712136092591[8] = state[8];
}
void F_fun(double *state, double dt, double *out_2989085374181927005) {
   out_2989085374181927005[0] = 1;
   out_2989085374181927005[1] = 0;
   out_2989085374181927005[2] = 0;
   out_2989085374181927005[3] = 0;
   out_2989085374181927005[4] = 0;
   out_2989085374181927005[5] = 0;
   out_2989085374181927005[6] = 0;
   out_2989085374181927005[7] = 0;
   out_2989085374181927005[8] = 0;
   out_2989085374181927005[9] = 0;
   out_2989085374181927005[10] = 1;
   out_2989085374181927005[11] = 0;
   out_2989085374181927005[12] = 0;
   out_2989085374181927005[13] = 0;
   out_2989085374181927005[14] = 0;
   out_2989085374181927005[15] = 0;
   out_2989085374181927005[16] = 0;
   out_2989085374181927005[17] = 0;
   out_2989085374181927005[18] = 0;
   out_2989085374181927005[19] = 0;
   out_2989085374181927005[20] = 1;
   out_2989085374181927005[21] = 0;
   out_2989085374181927005[22] = 0;
   out_2989085374181927005[23] = 0;
   out_2989085374181927005[24] = 0;
   out_2989085374181927005[25] = 0;
   out_2989085374181927005[26] = 0;
   out_2989085374181927005[27] = 0;
   out_2989085374181927005[28] = 0;
   out_2989085374181927005[29] = 0;
   out_2989085374181927005[30] = 1;
   out_2989085374181927005[31] = 0;
   out_2989085374181927005[32] = 0;
   out_2989085374181927005[33] = 0;
   out_2989085374181927005[34] = 0;
   out_2989085374181927005[35] = 0;
   out_2989085374181927005[36] = 0;
   out_2989085374181927005[37] = 0;
   out_2989085374181927005[38] = 0;
   out_2989085374181927005[39] = 0;
   out_2989085374181927005[40] = 1;
   out_2989085374181927005[41] = 0;
   out_2989085374181927005[42] = 0;
   out_2989085374181927005[43] = 0;
   out_2989085374181927005[44] = 0;
   out_2989085374181927005[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_2989085374181927005[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_2989085374181927005[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_2989085374181927005[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_2989085374181927005[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_2989085374181927005[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_2989085374181927005[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_2989085374181927005[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_2989085374181927005[53] = -9.8100000000000005*dt;
   out_2989085374181927005[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_2989085374181927005[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_2989085374181927005[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_2989085374181927005[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_2989085374181927005[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_2989085374181927005[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_2989085374181927005[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_2989085374181927005[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_2989085374181927005[62] = 0;
   out_2989085374181927005[63] = 0;
   out_2989085374181927005[64] = 0;
   out_2989085374181927005[65] = 0;
   out_2989085374181927005[66] = 0;
   out_2989085374181927005[67] = 0;
   out_2989085374181927005[68] = 0;
   out_2989085374181927005[69] = 0;
   out_2989085374181927005[70] = 1;
   out_2989085374181927005[71] = 0;
   out_2989085374181927005[72] = 0;
   out_2989085374181927005[73] = 0;
   out_2989085374181927005[74] = 0;
   out_2989085374181927005[75] = 0;
   out_2989085374181927005[76] = 0;
   out_2989085374181927005[77] = 0;
   out_2989085374181927005[78] = 0;
   out_2989085374181927005[79] = 0;
   out_2989085374181927005[80] = 1;
}
void h_25(double *state, double *unused, double *out_7779026555707581006) {
   out_7779026555707581006[0] = state[6];
}
void H_25(double *state, double *unused, double *out_7597270765006040550) {
   out_7597270765006040550[0] = 0;
   out_7597270765006040550[1] = 0;
   out_7597270765006040550[2] = 0;
   out_7597270765006040550[3] = 0;
   out_7597270765006040550[4] = 0;
   out_7597270765006040550[5] = 0;
   out_7597270765006040550[6] = 1;
   out_7597270765006040550[7] = 0;
   out_7597270765006040550[8] = 0;
}
void h_24(double *state, double *unused, double *out_1363944844356195076) {
   out_1363944844356195076[0] = state[4];
   out_1363944844356195076[1] = state[5];
}
void H_24(double *state, double *unused, double *out_4648440628852349640) {
   out_4648440628852349640[0] = 0;
   out_4648440628852349640[1] = 0;
   out_4648440628852349640[2] = 0;
   out_4648440628852349640[3] = 0;
   out_4648440628852349640[4] = 1;
   out_4648440628852349640[5] = 0;
   out_4648440628852349640[6] = 0;
   out_4648440628852349640[7] = 0;
   out_4648440628852349640[8] = 0;
   out_4648440628852349640[9] = 0;
   out_4648440628852349640[10] = 0;
   out_4648440628852349640[11] = 0;
   out_4648440628852349640[12] = 0;
   out_4648440628852349640[13] = 0;
   out_4648440628852349640[14] = 1;
   out_4648440628852349640[15] = 0;
   out_4648440628852349640[16] = 0;
   out_4648440628852349640[17] = 0;
}
void h_30(double *state, double *unused, double *out_7936213224058710151) {
   out_7936213224058710151[0] = state[4];
}
void H_30(double *state, double *unused, double *out_7726609712149280620) {
   out_7726609712149280620[0] = 0;
   out_7726609712149280620[1] = 0;
   out_7726609712149280620[2] = 0;
   out_7726609712149280620[3] = 0;
   out_7726609712149280620[4] = 1;
   out_7726609712149280620[5] = 0;
   out_7726609712149280620[6] = 0;
   out_7726609712149280620[7] = 0;
   out_7726609712149280620[8] = 0;
}
void h_26(double *state, double *unused, double *out_1537171706644861005) {
   out_1537171706644861005[0] = state[7];
}
void H_26(double *state, double *unused, double *out_6940416700895728646) {
   out_6940416700895728646[0] = 0;
   out_6940416700895728646[1] = 0;
   out_6940416700895728646[2] = 0;
   out_6940416700895728646[3] = 0;
   out_6940416700895728646[4] = 0;
   out_6940416700895728646[5] = 0;
   out_6940416700895728646[6] = 0;
   out_6940416700895728646[7] = 1;
   out_6940416700895728646[8] = 0;
}
void h_27(double *state, double *unused, double *out_3232574083573269797) {
   out_3232574083573269797[0] = state[3];
}
void H_27(double *state, double *unused, double *out_8545371049759846085) {
   out_8545371049759846085[0] = 0;
   out_8545371049759846085[1] = 0;
   out_8545371049759846085[2] = 0;
   out_8545371049759846085[3] = 1;
   out_8545371049759846085[4] = 0;
   out_8545371049759846085[5] = 0;
   out_8545371049759846085[6] = 0;
   out_8545371049759846085[7] = 0;
   out_8545371049759846085[8] = 0;
}
void h_29(double *state, double *unused, double *out_3538261142777081139) {
   out_3538261142777081139[0] = state[1];
}
void H_29(double *state, double *unused, double *out_7216378367834888436) {
   out_7216378367834888436[0] = 0;
   out_7216378367834888436[1] = 1;
   out_7216378367834888436[2] = 0;
   out_7216378367834888436[3] = 0;
   out_7216378367834888436[4] = 0;
   out_7216378367834888436[5] = 0;
   out_7216378367834888436[6] = 0;
   out_7216378367834888436[7] = 0;
   out_7216378367834888436[8] = 0;
}
void h_28(double *state, double *unused, double *out_2289064230671607362) {
   out_2289064230671607362[0] = state[0];
}
void H_28(double *state, double *unused, double *out_5252748096269562185) {
   out_5252748096269562185[0] = 1;
   out_5252748096269562185[1] = 0;
   out_5252748096269562185[2] = 0;
   out_5252748096269562185[3] = 0;
   out_5252748096269562185[4] = 0;
   out_5252748096269562185[5] = 0;
   out_5252748096269562185[6] = 0;
   out_5252748096269562185[7] = 0;
   out_5252748096269562185[8] = 0;
}
void h_31(double *state, double *unused, double *out_8054220617992086895) {
   out_8054220617992086895[0] = state[8];
}
void H_31(double *state, double *unused, double *out_7566624803129080122) {
   out_7566624803129080122[0] = 0;
   out_7566624803129080122[1] = 0;
   out_7566624803129080122[2] = 0;
   out_7566624803129080122[3] = 0;
   out_7566624803129080122[4] = 0;
   out_7566624803129080122[5] = 0;
   out_7566624803129080122[6] = 0;
   out_7566624803129080122[7] = 0;
   out_7566624803129080122[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_2496243277963511837) {
  err_fun(nom_x, delta_x, out_2496243277963511837);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_8723072931307095264) {
  inv_err_fun(nom_x, true_x, out_8723072931307095264);
}
void car_H_mod_fun(double *state, double *out_2432465619939465173) {
  H_mod_fun(state, out_2432465619939465173);
}
void car_f_fun(double *state, double dt, double *out_433459712136092591) {
  f_fun(state,  dt, out_433459712136092591);
}
void car_F_fun(double *state, double dt, double *out_2989085374181927005) {
  F_fun(state,  dt, out_2989085374181927005);
}
void car_h_25(double *state, double *unused, double *out_7779026555707581006) {
  h_25(state, unused, out_7779026555707581006);
}
void car_H_25(double *state, double *unused, double *out_7597270765006040550) {
  H_25(state, unused, out_7597270765006040550);
}
void car_h_24(double *state, double *unused, double *out_1363944844356195076) {
  h_24(state, unused, out_1363944844356195076);
}
void car_H_24(double *state, double *unused, double *out_4648440628852349640) {
  H_24(state, unused, out_4648440628852349640);
}
void car_h_30(double *state, double *unused, double *out_7936213224058710151) {
  h_30(state, unused, out_7936213224058710151);
}
void car_H_30(double *state, double *unused, double *out_7726609712149280620) {
  H_30(state, unused, out_7726609712149280620);
}
void car_h_26(double *state, double *unused, double *out_1537171706644861005) {
  h_26(state, unused, out_1537171706644861005);
}
void car_H_26(double *state, double *unused, double *out_6940416700895728646) {
  H_26(state, unused, out_6940416700895728646);
}
void car_h_27(double *state, double *unused, double *out_3232574083573269797) {
  h_27(state, unused, out_3232574083573269797);
}
void car_H_27(double *state, double *unused, double *out_8545371049759846085) {
  H_27(state, unused, out_8545371049759846085);
}
void car_h_29(double *state, double *unused, double *out_3538261142777081139) {
  h_29(state, unused, out_3538261142777081139);
}
void car_H_29(double *state, double *unused, double *out_7216378367834888436) {
  H_29(state, unused, out_7216378367834888436);
}
void car_h_28(double *state, double *unused, double *out_2289064230671607362) {
  h_28(state, unused, out_2289064230671607362);
}
void car_H_28(double *state, double *unused, double *out_5252748096269562185) {
  H_28(state, unused, out_5252748096269562185);
}
void car_h_31(double *state, double *unused, double *out_8054220617992086895) {
  h_31(state, unused, out_8054220617992086895);
}
void car_H_31(double *state, double *unused, double *out_7566624803129080122) {
  H_31(state, unused, out_7566624803129080122);
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
