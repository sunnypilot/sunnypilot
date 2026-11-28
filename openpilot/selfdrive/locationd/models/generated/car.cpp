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
void err_fun(double *nom_x, double *delta_x, double *out_6263818396156197794) {
   out_6263818396156197794[0] = delta_x[0] + nom_x[0];
   out_6263818396156197794[1] = delta_x[1] + nom_x[1];
   out_6263818396156197794[2] = delta_x[2] + nom_x[2];
   out_6263818396156197794[3] = delta_x[3] + nom_x[3];
   out_6263818396156197794[4] = delta_x[4] + nom_x[4];
   out_6263818396156197794[5] = delta_x[5] + nom_x[5];
   out_6263818396156197794[6] = delta_x[6] + nom_x[6];
   out_6263818396156197794[7] = delta_x[7] + nom_x[7];
   out_6263818396156197794[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_8403854160198660494) {
   out_8403854160198660494[0] = -nom_x[0] + true_x[0];
   out_8403854160198660494[1] = -nom_x[1] + true_x[1];
   out_8403854160198660494[2] = -nom_x[2] + true_x[2];
   out_8403854160198660494[3] = -nom_x[3] + true_x[3];
   out_8403854160198660494[4] = -nom_x[4] + true_x[4];
   out_8403854160198660494[5] = -nom_x[5] + true_x[5];
   out_8403854160198660494[6] = -nom_x[6] + true_x[6];
   out_8403854160198660494[7] = -nom_x[7] + true_x[7];
   out_8403854160198660494[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_2773070206469320626) {
   out_2773070206469320626[0] = 1.0;
   out_2773070206469320626[1] = 0.0;
   out_2773070206469320626[2] = 0.0;
   out_2773070206469320626[3] = 0.0;
   out_2773070206469320626[4] = 0.0;
   out_2773070206469320626[5] = 0.0;
   out_2773070206469320626[6] = 0.0;
   out_2773070206469320626[7] = 0.0;
   out_2773070206469320626[8] = 0.0;
   out_2773070206469320626[9] = 0.0;
   out_2773070206469320626[10] = 1.0;
   out_2773070206469320626[11] = 0.0;
   out_2773070206469320626[12] = 0.0;
   out_2773070206469320626[13] = 0.0;
   out_2773070206469320626[14] = 0.0;
   out_2773070206469320626[15] = 0.0;
   out_2773070206469320626[16] = 0.0;
   out_2773070206469320626[17] = 0.0;
   out_2773070206469320626[18] = 0.0;
   out_2773070206469320626[19] = 0.0;
   out_2773070206469320626[20] = 1.0;
   out_2773070206469320626[21] = 0.0;
   out_2773070206469320626[22] = 0.0;
   out_2773070206469320626[23] = 0.0;
   out_2773070206469320626[24] = 0.0;
   out_2773070206469320626[25] = 0.0;
   out_2773070206469320626[26] = 0.0;
   out_2773070206469320626[27] = 0.0;
   out_2773070206469320626[28] = 0.0;
   out_2773070206469320626[29] = 0.0;
   out_2773070206469320626[30] = 1.0;
   out_2773070206469320626[31] = 0.0;
   out_2773070206469320626[32] = 0.0;
   out_2773070206469320626[33] = 0.0;
   out_2773070206469320626[34] = 0.0;
   out_2773070206469320626[35] = 0.0;
   out_2773070206469320626[36] = 0.0;
   out_2773070206469320626[37] = 0.0;
   out_2773070206469320626[38] = 0.0;
   out_2773070206469320626[39] = 0.0;
   out_2773070206469320626[40] = 1.0;
   out_2773070206469320626[41] = 0.0;
   out_2773070206469320626[42] = 0.0;
   out_2773070206469320626[43] = 0.0;
   out_2773070206469320626[44] = 0.0;
   out_2773070206469320626[45] = 0.0;
   out_2773070206469320626[46] = 0.0;
   out_2773070206469320626[47] = 0.0;
   out_2773070206469320626[48] = 0.0;
   out_2773070206469320626[49] = 0.0;
   out_2773070206469320626[50] = 1.0;
   out_2773070206469320626[51] = 0.0;
   out_2773070206469320626[52] = 0.0;
   out_2773070206469320626[53] = 0.0;
   out_2773070206469320626[54] = 0.0;
   out_2773070206469320626[55] = 0.0;
   out_2773070206469320626[56] = 0.0;
   out_2773070206469320626[57] = 0.0;
   out_2773070206469320626[58] = 0.0;
   out_2773070206469320626[59] = 0.0;
   out_2773070206469320626[60] = 1.0;
   out_2773070206469320626[61] = 0.0;
   out_2773070206469320626[62] = 0.0;
   out_2773070206469320626[63] = 0.0;
   out_2773070206469320626[64] = 0.0;
   out_2773070206469320626[65] = 0.0;
   out_2773070206469320626[66] = 0.0;
   out_2773070206469320626[67] = 0.0;
   out_2773070206469320626[68] = 0.0;
   out_2773070206469320626[69] = 0.0;
   out_2773070206469320626[70] = 1.0;
   out_2773070206469320626[71] = 0.0;
   out_2773070206469320626[72] = 0.0;
   out_2773070206469320626[73] = 0.0;
   out_2773070206469320626[74] = 0.0;
   out_2773070206469320626[75] = 0.0;
   out_2773070206469320626[76] = 0.0;
   out_2773070206469320626[77] = 0.0;
   out_2773070206469320626[78] = 0.0;
   out_2773070206469320626[79] = 0.0;
   out_2773070206469320626[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_3353722608774504922) {
   out_3353722608774504922[0] = state[0];
   out_3353722608774504922[1] = state[1];
   out_3353722608774504922[2] = state[2];
   out_3353722608774504922[3] = state[3];
   out_3353722608774504922[4] = state[4];
   out_3353722608774504922[5] = dt*(stiffness_front*(-state[2] - state[3] + state[7])*state[0]/state[1] + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/state[4] + ((-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/state[4] - state[4])*state[6] - 9.8100000000000005*state[8]) + state[5];
   out_3353722608774504922[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_3353722608774504922[7] = state[7];
   out_3353722608774504922[8] = state[8];
}
void F_fun(double *state, double dt, double *out_5992377215234180239) {
   out_5992377215234180239[0] = 1;
   out_5992377215234180239[1] = 0;
   out_5992377215234180239[2] = 0;
   out_5992377215234180239[3] = 0;
   out_5992377215234180239[4] = 0;
   out_5992377215234180239[5] = 0;
   out_5992377215234180239[6] = 0;
   out_5992377215234180239[7] = 0;
   out_5992377215234180239[8] = 0;
   out_5992377215234180239[9] = 0;
   out_5992377215234180239[10] = 1;
   out_5992377215234180239[11] = 0;
   out_5992377215234180239[12] = 0;
   out_5992377215234180239[13] = 0;
   out_5992377215234180239[14] = 0;
   out_5992377215234180239[15] = 0;
   out_5992377215234180239[16] = 0;
   out_5992377215234180239[17] = 0;
   out_5992377215234180239[18] = 0;
   out_5992377215234180239[19] = 0;
   out_5992377215234180239[20] = 1;
   out_5992377215234180239[21] = 0;
   out_5992377215234180239[22] = 0;
   out_5992377215234180239[23] = 0;
   out_5992377215234180239[24] = 0;
   out_5992377215234180239[25] = 0;
   out_5992377215234180239[26] = 0;
   out_5992377215234180239[27] = 0;
   out_5992377215234180239[28] = 0;
   out_5992377215234180239[29] = 0;
   out_5992377215234180239[30] = 1;
   out_5992377215234180239[31] = 0;
   out_5992377215234180239[32] = 0;
   out_5992377215234180239[33] = 0;
   out_5992377215234180239[34] = 0;
   out_5992377215234180239[35] = 0;
   out_5992377215234180239[36] = 0;
   out_5992377215234180239[37] = 0;
   out_5992377215234180239[38] = 0;
   out_5992377215234180239[39] = 0;
   out_5992377215234180239[40] = 1;
   out_5992377215234180239[41] = 0;
   out_5992377215234180239[42] = 0;
   out_5992377215234180239[43] = 0;
   out_5992377215234180239[44] = 0;
   out_5992377215234180239[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/state[1] + (-stiffness_front - stiffness_rear)*state[5]/state[4] + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/state[4]);
   out_5992377215234180239[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/pow(state[1], 2);
   out_5992377215234180239[47] = -dt*stiffness_front*state[0]/state[1];
   out_5992377215234180239[48] = -dt*stiffness_front*state[0]/state[1];
   out_5992377215234180239[49] = dt*(-(-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/pow(state[4], 2) + (-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/pow(state[4], 2) - 1)*state[6]);
   out_5992377215234180239[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/state[4] + 1;
   out_5992377215234180239[51] = dt*((-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/state[4] - state[4]);
   out_5992377215234180239[52] = dt*stiffness_front*state[0]/state[1];
   out_5992377215234180239[53] = -9.8100000000000005*dt;
   out_5992377215234180239[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_5992377215234180239[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_5992377215234180239[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_5992377215234180239[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_5992377215234180239[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_5992377215234180239[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_5992377215234180239[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_5992377215234180239[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_5992377215234180239[62] = 0;
   out_5992377215234180239[63] = 0;
   out_5992377215234180239[64] = 0;
   out_5992377215234180239[65] = 0;
   out_5992377215234180239[66] = 0;
   out_5992377215234180239[67] = 0;
   out_5992377215234180239[68] = 0;
   out_5992377215234180239[69] = 0;
   out_5992377215234180239[70] = 1;
   out_5992377215234180239[71] = 0;
   out_5992377215234180239[72] = 0;
   out_5992377215234180239[73] = 0;
   out_5992377215234180239[74] = 0;
   out_5992377215234180239[75] = 0;
   out_5992377215234180239[76] = 0;
   out_5992377215234180239[77] = 0;
   out_5992377215234180239[78] = 0;
   out_5992377215234180239[79] = 0;
   out_5992377215234180239[80] = 1;
}
void h_25(double *state, double *unused, double *out_9059731259054464923) {
   out_9059731259054464923[0] = state[6];
}
void H_25(double *state, double *unused, double *out_6296050856458812303) {
   out_6296050856458812303[0] = 0;
   out_6296050856458812303[1] = 0;
   out_6296050856458812303[2] = 0;
   out_6296050856458812303[3] = 0;
   out_6296050856458812303[4] = 0;
   out_6296050856458812303[5] = 0;
   out_6296050856458812303[6] = 1;
   out_6296050856458812303[7] = 0;
   out_6296050856458812303[8] = 0;
}
void h_24(double *state, double *unused, double *out_3366975732395860410) {
   out_3366975732395860410[0] = state[4];
   out_3366975732395860410[1] = state[5];
}
void H_24(double *state, double *unused, double *out_8592767618448416177) {
   out_8592767618448416177[0] = 0;
   out_8592767618448416177[1] = 0;
   out_8592767618448416177[2] = 0;
   out_8592767618448416177[3] = 0;
   out_8592767618448416177[4] = 1;
   out_8592767618448416177[5] = 0;
   out_8592767618448416177[6] = 0;
   out_8592767618448416177[7] = 0;
   out_8592767618448416177[8] = 0;
   out_8592767618448416177[9] = 0;
   out_8592767618448416177[10] = 0;
   out_8592767618448416177[11] = 0;
   out_8592767618448416177[12] = 0;
   out_8592767618448416177[13] = 0;
   out_8592767618448416177[14] = 1;
   out_8592767618448416177[15] = 0;
   out_8592767618448416177[16] = 0;
   out_8592767618448416177[17] = 0;
}
void h_30(double *state, double *unused, double *out_4202737548822924391) {
   out_4202737548822924391[0] = state[4];
}
void H_30(double *state, double *unused, double *out_6166711909315572233) {
   out_6166711909315572233[0] = 0;
   out_6166711909315572233[1] = 0;
   out_6166711909315572233[2] = 0;
   out_6166711909315572233[3] = 0;
   out_6166711909315572233[4] = 1;
   out_6166711909315572233[5] = 0;
   out_6166711909315572233[6] = 0;
   out_6166711909315572233[7] = 0;
   out_6166711909315572233[8] = 0;
}
void h_26(double *state, double *unused, double *out_8168308899468918369) {
   out_8168308899468918369[0] = state[7];
}
void H_26(double *state, double *unused, double *out_2554547537584756079) {
   out_2554547537584756079[0] = 0;
   out_2554547537584756079[1] = 0;
   out_2554547537584756079[2] = 0;
   out_2554547537584756079[3] = 0;
   out_2554547537584756079[4] = 0;
   out_2554547537584756079[5] = 0;
   out_2554547537584756079[6] = 0;
   out_2554547537584756079[7] = 1;
   out_2554547537584756079[8] = 0;
}
void h_27(double *state, double *unused, double *out_2056968555261399144) {
   out_2056968555261399144[0] = state[3];
}
void H_27(double *state, double *unused, double *out_3991948597515147322) {
   out_3991948597515147322[0] = 0;
   out_3991948597515147322[1] = 0;
   out_3991948597515147322[2] = 0;
   out_3991948597515147322[3] = 1;
   out_3991948597515147322[4] = 0;
   out_3991948597515147322[5] = 0;
   out_3991948597515147322[6] = 0;
   out_3991948597515147322[7] = 0;
   out_3991948597515147322[8] = 0;
}
void h_29(double *state, double *unused, double *out_1899781886910269999) {
   out_1899781886910269999[0] = state[1];
}
void H_29(double *state, double *unused, double *out_2278585870645596289) {
   out_2278585870645596289[0] = 0;
   out_2278585870645596289[1] = 1;
   out_2278585870645596289[2] = 0;
   out_2278585870645596289[3] = 0;
   out_2278585870645596289[4] = 0;
   out_2278585870645596289[5] = 0;
   out_2278585870645596289[6] = 0;
   out_2278585870645596289[7] = 0;
   out_2278585870645596289[8] = 0;
}
void h_28(double *state, double *unused, double *out_979817496182933541) {
   out_979817496182933541[0] = state[0];
}
void H_28(double *state, double *unused, double *out_2803813146423934285) {
   out_2803813146423934285[0] = 1;
   out_2803813146423934285[1] = 0;
   out_2803813146423934285[2] = 0;
   out_2803813146423934285[3] = 0;
   out_2803813146423934285[4] = 0;
   out_2803813146423934285[5] = 0;
   out_2803813146423934285[6] = 0;
   out_2803813146423934285[7] = 0;
   out_2803813146423934285[8] = 0;
}
void h_31(double *state, double *unused, double *out_3219898774683952390) {
   out_3219898774683952390[0] = state[8];
}
void H_31(double *state, double *unused, double *out_6326696818335772731) {
   out_6326696818335772731[0] = 0;
   out_6326696818335772731[1] = 0;
   out_6326696818335772731[2] = 0;
   out_6326696818335772731[3] = 0;
   out_6326696818335772731[4] = 0;
   out_6326696818335772731[5] = 0;
   out_6326696818335772731[6] = 0;
   out_6326696818335772731[7] = 0;
   out_6326696818335772731[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_6263818396156197794) {
  err_fun(nom_x, delta_x, out_6263818396156197794);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_8403854160198660494) {
  inv_err_fun(nom_x, true_x, out_8403854160198660494);
}
void car_H_mod_fun(double *state, double *out_2773070206469320626) {
  H_mod_fun(state, out_2773070206469320626);
}
void car_f_fun(double *state, double dt, double *out_3353722608774504922) {
  f_fun(state,  dt, out_3353722608774504922);
}
void car_F_fun(double *state, double dt, double *out_5992377215234180239) {
  F_fun(state,  dt, out_5992377215234180239);
}
void car_h_25(double *state, double *unused, double *out_9059731259054464923) {
  h_25(state, unused, out_9059731259054464923);
}
void car_H_25(double *state, double *unused, double *out_6296050856458812303) {
  H_25(state, unused, out_6296050856458812303);
}
void car_h_24(double *state, double *unused, double *out_3366975732395860410) {
  h_24(state, unused, out_3366975732395860410);
}
void car_H_24(double *state, double *unused, double *out_8592767618448416177) {
  H_24(state, unused, out_8592767618448416177);
}
void car_h_30(double *state, double *unused, double *out_4202737548822924391) {
  h_30(state, unused, out_4202737548822924391);
}
void car_H_30(double *state, double *unused, double *out_6166711909315572233) {
  H_30(state, unused, out_6166711909315572233);
}
void car_h_26(double *state, double *unused, double *out_8168308899468918369) {
  h_26(state, unused, out_8168308899468918369);
}
void car_H_26(double *state, double *unused, double *out_2554547537584756079) {
  H_26(state, unused, out_2554547537584756079);
}
void car_h_27(double *state, double *unused, double *out_2056968555261399144) {
  h_27(state, unused, out_2056968555261399144);
}
void car_H_27(double *state, double *unused, double *out_3991948597515147322) {
  H_27(state, unused, out_3991948597515147322);
}
void car_h_29(double *state, double *unused, double *out_1899781886910269999) {
  h_29(state, unused, out_1899781886910269999);
}
void car_H_29(double *state, double *unused, double *out_2278585870645596289) {
  H_29(state, unused, out_2278585870645596289);
}
void car_h_28(double *state, double *unused, double *out_979817496182933541) {
  h_28(state, unused, out_979817496182933541);
}
void car_H_28(double *state, double *unused, double *out_2803813146423934285) {
  H_28(state, unused, out_2803813146423934285);
}
void car_h_31(double *state, double *unused, double *out_3219898774683952390) {
  h_31(state, unused, out_3219898774683952390);
}
void car_H_31(double *state, double *unused, double *out_6326696818335772731) {
  H_31(state, unused, out_6326696818335772731);
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
