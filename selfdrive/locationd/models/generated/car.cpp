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
void err_fun(double *nom_x, double *delta_x, double *out_6670847255313813537) {
   out_6670847255313813537[0] = delta_x[0] + nom_x[0];
   out_6670847255313813537[1] = delta_x[1] + nom_x[1];
   out_6670847255313813537[2] = delta_x[2] + nom_x[2];
   out_6670847255313813537[3] = delta_x[3] + nom_x[3];
   out_6670847255313813537[4] = delta_x[4] + nom_x[4];
   out_6670847255313813537[5] = delta_x[5] + nom_x[5];
   out_6670847255313813537[6] = delta_x[6] + nom_x[6];
   out_6670847255313813537[7] = delta_x[7] + nom_x[7];
   out_6670847255313813537[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_3529315537186539635) {
   out_3529315537186539635[0] = -nom_x[0] + true_x[0];
   out_3529315537186539635[1] = -nom_x[1] + true_x[1];
   out_3529315537186539635[2] = -nom_x[2] + true_x[2];
   out_3529315537186539635[3] = -nom_x[3] + true_x[3];
   out_3529315537186539635[4] = -nom_x[4] + true_x[4];
   out_3529315537186539635[5] = -nom_x[5] + true_x[5];
   out_3529315537186539635[6] = -nom_x[6] + true_x[6];
   out_3529315537186539635[7] = -nom_x[7] + true_x[7];
   out_3529315537186539635[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_338496889012731866) {
   out_338496889012731866[0] = 1.0;
   out_338496889012731866[1] = 0.0;
   out_338496889012731866[2] = 0.0;
   out_338496889012731866[3] = 0.0;
   out_338496889012731866[4] = 0.0;
   out_338496889012731866[5] = 0.0;
   out_338496889012731866[6] = 0.0;
   out_338496889012731866[7] = 0.0;
   out_338496889012731866[8] = 0.0;
   out_338496889012731866[9] = 0.0;
   out_338496889012731866[10] = 1.0;
   out_338496889012731866[11] = 0.0;
   out_338496889012731866[12] = 0.0;
   out_338496889012731866[13] = 0.0;
   out_338496889012731866[14] = 0.0;
   out_338496889012731866[15] = 0.0;
   out_338496889012731866[16] = 0.0;
   out_338496889012731866[17] = 0.0;
   out_338496889012731866[18] = 0.0;
   out_338496889012731866[19] = 0.0;
   out_338496889012731866[20] = 1.0;
   out_338496889012731866[21] = 0.0;
   out_338496889012731866[22] = 0.0;
   out_338496889012731866[23] = 0.0;
   out_338496889012731866[24] = 0.0;
   out_338496889012731866[25] = 0.0;
   out_338496889012731866[26] = 0.0;
   out_338496889012731866[27] = 0.0;
   out_338496889012731866[28] = 0.0;
   out_338496889012731866[29] = 0.0;
   out_338496889012731866[30] = 1.0;
   out_338496889012731866[31] = 0.0;
   out_338496889012731866[32] = 0.0;
   out_338496889012731866[33] = 0.0;
   out_338496889012731866[34] = 0.0;
   out_338496889012731866[35] = 0.0;
   out_338496889012731866[36] = 0.0;
   out_338496889012731866[37] = 0.0;
   out_338496889012731866[38] = 0.0;
   out_338496889012731866[39] = 0.0;
   out_338496889012731866[40] = 1.0;
   out_338496889012731866[41] = 0.0;
   out_338496889012731866[42] = 0.0;
   out_338496889012731866[43] = 0.0;
   out_338496889012731866[44] = 0.0;
   out_338496889012731866[45] = 0.0;
   out_338496889012731866[46] = 0.0;
   out_338496889012731866[47] = 0.0;
   out_338496889012731866[48] = 0.0;
   out_338496889012731866[49] = 0.0;
   out_338496889012731866[50] = 1.0;
   out_338496889012731866[51] = 0.0;
   out_338496889012731866[52] = 0.0;
   out_338496889012731866[53] = 0.0;
   out_338496889012731866[54] = 0.0;
   out_338496889012731866[55] = 0.0;
   out_338496889012731866[56] = 0.0;
   out_338496889012731866[57] = 0.0;
   out_338496889012731866[58] = 0.0;
   out_338496889012731866[59] = 0.0;
   out_338496889012731866[60] = 1.0;
   out_338496889012731866[61] = 0.0;
   out_338496889012731866[62] = 0.0;
   out_338496889012731866[63] = 0.0;
   out_338496889012731866[64] = 0.0;
   out_338496889012731866[65] = 0.0;
   out_338496889012731866[66] = 0.0;
   out_338496889012731866[67] = 0.0;
   out_338496889012731866[68] = 0.0;
   out_338496889012731866[69] = 0.0;
   out_338496889012731866[70] = 1.0;
   out_338496889012731866[71] = 0.0;
   out_338496889012731866[72] = 0.0;
   out_338496889012731866[73] = 0.0;
   out_338496889012731866[74] = 0.0;
   out_338496889012731866[75] = 0.0;
   out_338496889012731866[76] = 0.0;
   out_338496889012731866[77] = 0.0;
   out_338496889012731866[78] = 0.0;
   out_338496889012731866[79] = 0.0;
   out_338496889012731866[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_3923934035523038452) {
   out_3923934035523038452[0] = state[0];
   out_3923934035523038452[1] = state[1];
   out_3923934035523038452[2] = state[2];
   out_3923934035523038452[3] = state[3];
   out_3923934035523038452[4] = state[4];
   out_3923934035523038452[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8100000000000005*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_3923934035523038452[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_3923934035523038452[7] = state[7];
   out_3923934035523038452[8] = state[8];
}
void F_fun(double *state, double dt, double *out_4825516617134300251) {
   out_4825516617134300251[0] = 1;
   out_4825516617134300251[1] = 0;
   out_4825516617134300251[2] = 0;
   out_4825516617134300251[3] = 0;
   out_4825516617134300251[4] = 0;
   out_4825516617134300251[5] = 0;
   out_4825516617134300251[6] = 0;
   out_4825516617134300251[7] = 0;
   out_4825516617134300251[8] = 0;
   out_4825516617134300251[9] = 0;
   out_4825516617134300251[10] = 1;
   out_4825516617134300251[11] = 0;
   out_4825516617134300251[12] = 0;
   out_4825516617134300251[13] = 0;
   out_4825516617134300251[14] = 0;
   out_4825516617134300251[15] = 0;
   out_4825516617134300251[16] = 0;
   out_4825516617134300251[17] = 0;
   out_4825516617134300251[18] = 0;
   out_4825516617134300251[19] = 0;
   out_4825516617134300251[20] = 1;
   out_4825516617134300251[21] = 0;
   out_4825516617134300251[22] = 0;
   out_4825516617134300251[23] = 0;
   out_4825516617134300251[24] = 0;
   out_4825516617134300251[25] = 0;
   out_4825516617134300251[26] = 0;
   out_4825516617134300251[27] = 0;
   out_4825516617134300251[28] = 0;
   out_4825516617134300251[29] = 0;
   out_4825516617134300251[30] = 1;
   out_4825516617134300251[31] = 0;
   out_4825516617134300251[32] = 0;
   out_4825516617134300251[33] = 0;
   out_4825516617134300251[34] = 0;
   out_4825516617134300251[35] = 0;
   out_4825516617134300251[36] = 0;
   out_4825516617134300251[37] = 0;
   out_4825516617134300251[38] = 0;
   out_4825516617134300251[39] = 0;
   out_4825516617134300251[40] = 1;
   out_4825516617134300251[41] = 0;
   out_4825516617134300251[42] = 0;
   out_4825516617134300251[43] = 0;
   out_4825516617134300251[44] = 0;
   out_4825516617134300251[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_4825516617134300251[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_4825516617134300251[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_4825516617134300251[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_4825516617134300251[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_4825516617134300251[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_4825516617134300251[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_4825516617134300251[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_4825516617134300251[53] = -9.8100000000000005*dt;
   out_4825516617134300251[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_4825516617134300251[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_4825516617134300251[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_4825516617134300251[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_4825516617134300251[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_4825516617134300251[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_4825516617134300251[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_4825516617134300251[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_4825516617134300251[62] = 0;
   out_4825516617134300251[63] = 0;
   out_4825516617134300251[64] = 0;
   out_4825516617134300251[65] = 0;
   out_4825516617134300251[66] = 0;
   out_4825516617134300251[67] = 0;
   out_4825516617134300251[68] = 0;
   out_4825516617134300251[69] = 0;
   out_4825516617134300251[70] = 1;
   out_4825516617134300251[71] = 0;
   out_4825516617134300251[72] = 0;
   out_4825516617134300251[73] = 0;
   out_4825516617134300251[74] = 0;
   out_4825516617134300251[75] = 0;
   out_4825516617134300251[76] = 0;
   out_4825516617134300251[77] = 0;
   out_4825516617134300251[78] = 0;
   out_4825516617134300251[79] = 0;
   out_4825516617134300251[80] = 1;
}
void h_25(double *state, double *unused, double *out_2301414804881314403) {
   out_2301414804881314403[0] = state[6];
}
void H_25(double *state, double *unused, double *out_8854691336899505371) {
   out_8854691336899505371[0] = 0;
   out_8854691336899505371[1] = 0;
   out_8854691336899505371[2] = 0;
   out_8854691336899505371[3] = 0;
   out_8854691336899505371[4] = 0;
   out_8854691336899505371[5] = 0;
   out_8854691336899505371[6] = 1;
   out_8854691336899505371[7] = 0;
   out_8854691336899505371[8] = 0;
}
void h_24(double *state, double *unused, double *out_620520591641681701) {
   out_620520591641681701[0] = state[4];
   out_620520591641681701[1] = state[5];
}
void H_24(double *state, double *unused, double *out_4845543409843537211) {
   out_4845543409843537211[0] = 0;
   out_4845543409843537211[1] = 0;
   out_4845543409843537211[2] = 0;
   out_4845543409843537211[3] = 0;
   out_4845543409843537211[4] = 1;
   out_4845543409843537211[5] = 0;
   out_4845543409843537211[6] = 0;
   out_4845543409843537211[7] = 0;
   out_4845543409843537211[8] = 0;
   out_4845543409843537211[9] = 0;
   out_4845543409843537211[10] = 0;
   out_4845543409843537211[11] = 0;
   out_4845543409843537211[12] = 0;
   out_4845543409843537211[13] = 0;
   out_4845543409843537211[14] = 1;
   out_4845543409843537211[15] = 0;
   out_4845543409843537211[16] = 0;
   out_4845543409843537211[17] = 0;
}
void h_30(double *state, double *unused, double *out_8684770504579348888) {
   out_8684770504579348888[0] = state[4];
}
void H_30(double *state, double *unused, double *out_6336358378392256744) {
   out_6336358378392256744[0] = 0;
   out_6336358378392256744[1] = 0;
   out_6336358378392256744[2] = 0;
   out_6336358378392256744[3] = 0;
   out_6336358378392256744[4] = 1;
   out_6336358378392256744[5] = 0;
   out_6336358378392256744[6] = 0;
   out_6336358378392256744[7] = 0;
   out_6336358378392256744[8] = 0;
}
void h_26(double *state, double *unused, double *out_8818463716228540293) {
   out_8818463716228540293[0] = state[7];
}
void H_26(double *state, double *unused, double *out_5850549417935990021) {
   out_5850549417935990021[0] = 0;
   out_5850549417935990021[1] = 0;
   out_5850549417935990021[2] = 0;
   out_5850549417935990021[3] = 0;
   out_5850549417935990021[4] = 0;
   out_5850549417935990021[5] = 0;
   out_5850549417935990021[6] = 0;
   out_5850549417935990021[7] = 1;
   out_5850549417935990021[8] = 0;
}
void h_27(double *state, double *unused, double *out_2700258462779531242) {
   out_2700258462779531242[0] = state[3];
}
void H_27(double *state, double *unused, double *out_4112764307208313527) {
   out_4112764307208313527[0] = 0;
   out_4112764307208313527[1] = 0;
   out_4112764307208313527[2] = 0;
   out_4112764307208313527[3] = 1;
   out_4112764307208313527[4] = 0;
   out_4112764307208313527[5] = 0;
   out_4112764307208313527[6] = 0;
   out_4112764307208313527[7] = 0;
   out_4112764307208313527[8] = 0;
}
void h_29(double *state, double *unused, double *out_1249627070150648075) {
   out_1249627070150648075[0] = state[1];
}
void H_29(double *state, double *unused, double *out_5826127034077864560) {
   out_5826127034077864560[0] = 0;
   out_5826127034077864560[1] = 1;
   out_5826127034077864560[2] = 0;
   out_5826127034077864560[3] = 0;
   out_5826127034077864560[4] = 0;
   out_5826127034077864560[5] = 0;
   out_5826127034077864560[6] = 0;
   out_5826127034077864560[7] = 0;
   out_5826127034077864560[8] = 0;
}
void h_28(double *state, double *unused, double *out_5424608509547706960) {
   out_5424608509547706960[0] = state[0];
}
void H_28(double *state, double *unused, double *out_7538218022562156482) {
   out_7538218022562156482[0] = 1;
   out_7538218022562156482[1] = 0;
   out_7538218022562156482[2] = 0;
   out_7538218022562156482[3] = 0;
   out_7538218022562156482[4] = 0;
   out_7538218022562156482[5] = 0;
   out_7538218022562156482[6] = 0;
   out_7538218022562156482[7] = 0;
   out_7538218022562156482[8] = 0;
}
void h_31(double *state, double *unused, double *out_5938864333135336753) {
   out_5938864333135336753[0] = state[8];
}
void H_31(double *state, double *unused, double *out_8824045375022544943) {
   out_8824045375022544943[0] = 0;
   out_8824045375022544943[1] = 0;
   out_8824045375022544943[2] = 0;
   out_8824045375022544943[3] = 0;
   out_8824045375022544943[4] = 0;
   out_8824045375022544943[5] = 0;
   out_8824045375022544943[6] = 0;
   out_8824045375022544943[7] = 0;
   out_8824045375022544943[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_6670847255313813537) {
  err_fun(nom_x, delta_x, out_6670847255313813537);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_3529315537186539635) {
  inv_err_fun(nom_x, true_x, out_3529315537186539635);
}
void car_H_mod_fun(double *state, double *out_338496889012731866) {
  H_mod_fun(state, out_338496889012731866);
}
void car_f_fun(double *state, double dt, double *out_3923934035523038452) {
  f_fun(state,  dt, out_3923934035523038452);
}
void car_F_fun(double *state, double dt, double *out_4825516617134300251) {
  F_fun(state,  dt, out_4825516617134300251);
}
void car_h_25(double *state, double *unused, double *out_2301414804881314403) {
  h_25(state, unused, out_2301414804881314403);
}
void car_H_25(double *state, double *unused, double *out_8854691336899505371) {
  H_25(state, unused, out_8854691336899505371);
}
void car_h_24(double *state, double *unused, double *out_620520591641681701) {
  h_24(state, unused, out_620520591641681701);
}
void car_H_24(double *state, double *unused, double *out_4845543409843537211) {
  H_24(state, unused, out_4845543409843537211);
}
void car_h_30(double *state, double *unused, double *out_8684770504579348888) {
  h_30(state, unused, out_8684770504579348888);
}
void car_H_30(double *state, double *unused, double *out_6336358378392256744) {
  H_30(state, unused, out_6336358378392256744);
}
void car_h_26(double *state, double *unused, double *out_8818463716228540293) {
  h_26(state, unused, out_8818463716228540293);
}
void car_H_26(double *state, double *unused, double *out_5850549417935990021) {
  H_26(state, unused, out_5850549417935990021);
}
void car_h_27(double *state, double *unused, double *out_2700258462779531242) {
  h_27(state, unused, out_2700258462779531242);
}
void car_H_27(double *state, double *unused, double *out_4112764307208313527) {
  H_27(state, unused, out_4112764307208313527);
}
void car_h_29(double *state, double *unused, double *out_1249627070150648075) {
  h_29(state, unused, out_1249627070150648075);
}
void car_H_29(double *state, double *unused, double *out_5826127034077864560) {
  H_29(state, unused, out_5826127034077864560);
}
void car_h_28(double *state, double *unused, double *out_5424608509547706960) {
  h_28(state, unused, out_5424608509547706960);
}
void car_H_28(double *state, double *unused, double *out_7538218022562156482) {
  H_28(state, unused, out_7538218022562156482);
}
void car_h_31(double *state, double *unused, double *out_5938864333135336753) {
  h_31(state, unused, out_5938864333135336753);
}
void car_H_31(double *state, double *unused, double *out_8824045375022544943) {
  H_31(state, unused, out_8824045375022544943);
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
