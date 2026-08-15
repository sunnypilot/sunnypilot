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
void err_fun(double *nom_x, double *delta_x, double *out_3066078453041735876) {
   out_3066078453041735876[0] = delta_x[0] + nom_x[0];
   out_3066078453041735876[1] = delta_x[1] + nom_x[1];
   out_3066078453041735876[2] = delta_x[2] + nom_x[2];
   out_3066078453041735876[3] = delta_x[3] + nom_x[3];
   out_3066078453041735876[4] = delta_x[4] + nom_x[4];
   out_3066078453041735876[5] = delta_x[5] + nom_x[5];
   out_3066078453041735876[6] = delta_x[6] + nom_x[6];
   out_3066078453041735876[7] = delta_x[7] + nom_x[7];
   out_3066078453041735876[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_7998306431651746749) {
   out_7998306431651746749[0] = -nom_x[0] + true_x[0];
   out_7998306431651746749[1] = -nom_x[1] + true_x[1];
   out_7998306431651746749[2] = -nom_x[2] + true_x[2];
   out_7998306431651746749[3] = -nom_x[3] + true_x[3];
   out_7998306431651746749[4] = -nom_x[4] + true_x[4];
   out_7998306431651746749[5] = -nom_x[5] + true_x[5];
   out_7998306431651746749[6] = -nom_x[6] + true_x[6];
   out_7998306431651746749[7] = -nom_x[7] + true_x[7];
   out_7998306431651746749[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_8410823161376016702) {
   out_8410823161376016702[0] = 1.0;
   out_8410823161376016702[1] = 0.0;
   out_8410823161376016702[2] = 0.0;
   out_8410823161376016702[3] = 0.0;
   out_8410823161376016702[4] = 0.0;
   out_8410823161376016702[5] = 0.0;
   out_8410823161376016702[6] = 0.0;
   out_8410823161376016702[7] = 0.0;
   out_8410823161376016702[8] = 0.0;
   out_8410823161376016702[9] = 0.0;
   out_8410823161376016702[10] = 1.0;
   out_8410823161376016702[11] = 0.0;
   out_8410823161376016702[12] = 0.0;
   out_8410823161376016702[13] = 0.0;
   out_8410823161376016702[14] = 0.0;
   out_8410823161376016702[15] = 0.0;
   out_8410823161376016702[16] = 0.0;
   out_8410823161376016702[17] = 0.0;
   out_8410823161376016702[18] = 0.0;
   out_8410823161376016702[19] = 0.0;
   out_8410823161376016702[20] = 1.0;
   out_8410823161376016702[21] = 0.0;
   out_8410823161376016702[22] = 0.0;
   out_8410823161376016702[23] = 0.0;
   out_8410823161376016702[24] = 0.0;
   out_8410823161376016702[25] = 0.0;
   out_8410823161376016702[26] = 0.0;
   out_8410823161376016702[27] = 0.0;
   out_8410823161376016702[28] = 0.0;
   out_8410823161376016702[29] = 0.0;
   out_8410823161376016702[30] = 1.0;
   out_8410823161376016702[31] = 0.0;
   out_8410823161376016702[32] = 0.0;
   out_8410823161376016702[33] = 0.0;
   out_8410823161376016702[34] = 0.0;
   out_8410823161376016702[35] = 0.0;
   out_8410823161376016702[36] = 0.0;
   out_8410823161376016702[37] = 0.0;
   out_8410823161376016702[38] = 0.0;
   out_8410823161376016702[39] = 0.0;
   out_8410823161376016702[40] = 1.0;
   out_8410823161376016702[41] = 0.0;
   out_8410823161376016702[42] = 0.0;
   out_8410823161376016702[43] = 0.0;
   out_8410823161376016702[44] = 0.0;
   out_8410823161376016702[45] = 0.0;
   out_8410823161376016702[46] = 0.0;
   out_8410823161376016702[47] = 0.0;
   out_8410823161376016702[48] = 0.0;
   out_8410823161376016702[49] = 0.0;
   out_8410823161376016702[50] = 1.0;
   out_8410823161376016702[51] = 0.0;
   out_8410823161376016702[52] = 0.0;
   out_8410823161376016702[53] = 0.0;
   out_8410823161376016702[54] = 0.0;
   out_8410823161376016702[55] = 0.0;
   out_8410823161376016702[56] = 0.0;
   out_8410823161376016702[57] = 0.0;
   out_8410823161376016702[58] = 0.0;
   out_8410823161376016702[59] = 0.0;
   out_8410823161376016702[60] = 1.0;
   out_8410823161376016702[61] = 0.0;
   out_8410823161376016702[62] = 0.0;
   out_8410823161376016702[63] = 0.0;
   out_8410823161376016702[64] = 0.0;
   out_8410823161376016702[65] = 0.0;
   out_8410823161376016702[66] = 0.0;
   out_8410823161376016702[67] = 0.0;
   out_8410823161376016702[68] = 0.0;
   out_8410823161376016702[69] = 0.0;
   out_8410823161376016702[70] = 1.0;
   out_8410823161376016702[71] = 0.0;
   out_8410823161376016702[72] = 0.0;
   out_8410823161376016702[73] = 0.0;
   out_8410823161376016702[74] = 0.0;
   out_8410823161376016702[75] = 0.0;
   out_8410823161376016702[76] = 0.0;
   out_8410823161376016702[77] = 0.0;
   out_8410823161376016702[78] = 0.0;
   out_8410823161376016702[79] = 0.0;
   out_8410823161376016702[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_8406538155675584278) {
   out_8406538155675584278[0] = state[0];
   out_8406538155675584278[1] = state[1];
   out_8406538155675584278[2] = state[2];
   out_8406538155675584278[3] = state[3];
   out_8406538155675584278[4] = state[4];
   out_8406538155675584278[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8100000000000005*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_8406538155675584278[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_8406538155675584278[7] = state[7];
   out_8406538155675584278[8] = state[8];
}
void F_fun(double *state, double dt, double *out_9168420830296677739) {
   out_9168420830296677739[0] = 1;
   out_9168420830296677739[1] = 0;
   out_9168420830296677739[2] = 0;
   out_9168420830296677739[3] = 0;
   out_9168420830296677739[4] = 0;
   out_9168420830296677739[5] = 0;
   out_9168420830296677739[6] = 0;
   out_9168420830296677739[7] = 0;
   out_9168420830296677739[8] = 0;
   out_9168420830296677739[9] = 0;
   out_9168420830296677739[10] = 1;
   out_9168420830296677739[11] = 0;
   out_9168420830296677739[12] = 0;
   out_9168420830296677739[13] = 0;
   out_9168420830296677739[14] = 0;
   out_9168420830296677739[15] = 0;
   out_9168420830296677739[16] = 0;
   out_9168420830296677739[17] = 0;
   out_9168420830296677739[18] = 0;
   out_9168420830296677739[19] = 0;
   out_9168420830296677739[20] = 1;
   out_9168420830296677739[21] = 0;
   out_9168420830296677739[22] = 0;
   out_9168420830296677739[23] = 0;
   out_9168420830296677739[24] = 0;
   out_9168420830296677739[25] = 0;
   out_9168420830296677739[26] = 0;
   out_9168420830296677739[27] = 0;
   out_9168420830296677739[28] = 0;
   out_9168420830296677739[29] = 0;
   out_9168420830296677739[30] = 1;
   out_9168420830296677739[31] = 0;
   out_9168420830296677739[32] = 0;
   out_9168420830296677739[33] = 0;
   out_9168420830296677739[34] = 0;
   out_9168420830296677739[35] = 0;
   out_9168420830296677739[36] = 0;
   out_9168420830296677739[37] = 0;
   out_9168420830296677739[38] = 0;
   out_9168420830296677739[39] = 0;
   out_9168420830296677739[40] = 1;
   out_9168420830296677739[41] = 0;
   out_9168420830296677739[42] = 0;
   out_9168420830296677739[43] = 0;
   out_9168420830296677739[44] = 0;
   out_9168420830296677739[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_9168420830296677739[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_9168420830296677739[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_9168420830296677739[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_9168420830296677739[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_9168420830296677739[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_9168420830296677739[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_9168420830296677739[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_9168420830296677739[53] = -9.8100000000000005*dt;
   out_9168420830296677739[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_9168420830296677739[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_9168420830296677739[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_9168420830296677739[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_9168420830296677739[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_9168420830296677739[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_9168420830296677739[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_9168420830296677739[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_9168420830296677739[62] = 0;
   out_9168420830296677739[63] = 0;
   out_9168420830296677739[64] = 0;
   out_9168420830296677739[65] = 0;
   out_9168420830296677739[66] = 0;
   out_9168420830296677739[67] = 0;
   out_9168420830296677739[68] = 0;
   out_9168420830296677739[69] = 0;
   out_9168420830296677739[70] = 1;
   out_9168420830296677739[71] = 0;
   out_9168420830296677739[72] = 0;
   out_9168420830296677739[73] = 0;
   out_9168420830296677739[74] = 0;
   out_9168420830296677739[75] = 0;
   out_9168420830296677739[76] = 0;
   out_9168420830296677739[77] = 0;
   out_9168420830296677739[78] = 0;
   out_9168420830296677739[79] = 0;
   out_9168420830296677739[80] = 1;
}
void h_25(double *state, double *unused, double *out_6925664705835598268) {
   out_6925664705835598268[0] = state[6];
}
void H_25(double *state, double *unused, double *out_842732686421297677) {
   out_842732686421297677[0] = 0;
   out_842732686421297677[1] = 0;
   out_842732686421297677[2] = 0;
   out_842732686421297677[3] = 0;
   out_842732686421297677[4] = 0;
   out_842732686421297677[5] = 0;
   out_842732686421297677[6] = 1;
   out_842732686421297677[7] = 0;
   out_842732686421297677[8] = 0;
}
void h_24(double *state, double *unused, double *out_611774507479316058) {
   out_611774507479316058[0] = state[4];
   out_611774507479316058[1] = state[5];
}
void H_24(double *state, double *unused, double *out_7496938144529483434) {
   out_7496938144529483434[0] = 0;
   out_7496938144529483434[1] = 0;
   out_7496938144529483434[2] = 0;
   out_7496938144529483434[3] = 0;
   out_7496938144529483434[4] = 1;
   out_7496938144529483434[5] = 0;
   out_7496938144529483434[6] = 0;
   out_7496938144529483434[7] = 0;
   out_7496938144529483434[8] = 0;
   out_7496938144529483434[9] = 0;
   out_7496938144529483434[10] = 0;
   out_7496938144529483434[11] = 0;
   out_7496938144529483434[12] = 0;
   out_7496938144529483434[13] = 0;
   out_7496938144529483434[14] = 1;
   out_7496938144529483434[15] = 0;
   out_7496938144529483434[16] = 0;
   out_7496938144529483434[17] = 0;
}
void h_30(double *state, double *unused, double *out_7082851374186727413) {
   out_7082851374186727413[0] = state[4];
}
void H_30(double *state, double *unused, double *out_3684963643706310521) {
   out_3684963643706310521[0] = 0;
   out_3684963643706310521[1] = 0;
   out_3684963643706310521[2] = 0;
   out_3684963643706310521[3] = 0;
   out_3684963643706310521[4] = 1;
   out_3684963643706310521[5] = 0;
   out_3684963643706310521[6] = 0;
   out_3684963643706310521[7] = 0;
   out_3684963643706310521[8] = 0;
}
void h_26(double *state, double *unused, double *out_6139341521285064978) {
   out_6139341521285064978[0] = state[7];
}
void H_26(double *state, double *unused, double *out_2898770632452758547) {
   out_2898770632452758547[0] = 0;
   out_2898770632452758547[1] = 0;
   out_2898770632452758547[2] = 0;
   out_2898770632452758547[3] = 0;
   out_2898770632452758547[4] = 0;
   out_2898770632452758547[5] = 0;
   out_2898770632452758547[6] = 0;
   out_2898770632452758547[7] = 1;
   out_2898770632452758547[8] = 0;
}
void h_27(double *state, double *unused, double *out_8484293316429620663) {
   out_8484293316429620663[0] = state[3];
}
void H_27(double *state, double *unused, double *out_5859726955506735432) {
   out_5859726955506735432[0] = 0;
   out_5859726955506735432[1] = 0;
   out_5859726955506735432[2] = 0;
   out_5859726955506735432[3] = 1;
   out_5859726955506735432[4] = 0;
   out_5859726955506735432[5] = 0;
   out_5859726955506735432[6] = 0;
   out_5859726955506735432[7] = 0;
   out_5859726955506735432[8] = 0;
}
void h_29(double *state, double *unused, double *out_2081178106525881768) {
   out_2081178106525881768[0] = state[1];
}
void H_29(double *state, double *unused, double *out_3174732299391918337) {
   out_3174732299391918337[0] = 0;
   out_3174732299391918337[1] = 1;
   out_3174732299391918337[2] = 0;
   out_3174732299391918337[3] = 0;
   out_3174732299391918337[4] = 0;
   out_3174732299391918337[5] = 0;
   out_3174732299391918337[6] = 0;
   out_3174732299391918337[7] = 0;
   out_3174732299391918337[8] = 0;
}
void h_28(double *state, double *unused, double *out_9087609201106098180) {
   out_9087609201106098180[0] = state[0];
}
void H_28(double *state, double *unused, double *out_8257131316461448911) {
   out_8257131316461448911[0] = 1;
   out_8257131316461448911[1] = 0;
   out_8257131316461448911[2] = 0;
   out_8257131316461448911[3] = 0;
   out_8257131316461448911[4] = 0;
   out_8257131316461448911[5] = 0;
   out_8257131316461448911[6] = 0;
   out_8257131316461448911[7] = 0;
   out_8257131316461448911[8] = 0;
}
void h_31(double *state, double *unused, double *out_7580923347048146882) {
   out_7580923347048146882[0] = state[8];
}
void H_31(double *state, double *unused, double *out_3524978734686110023) {
   out_3524978734686110023[0] = 0;
   out_3524978734686110023[1] = 0;
   out_3524978734686110023[2] = 0;
   out_3524978734686110023[3] = 0;
   out_3524978734686110023[4] = 0;
   out_3524978734686110023[5] = 0;
   out_3524978734686110023[6] = 0;
   out_3524978734686110023[7] = 0;
   out_3524978734686110023[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_3066078453041735876) {
  err_fun(nom_x, delta_x, out_3066078453041735876);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_7998306431651746749) {
  inv_err_fun(nom_x, true_x, out_7998306431651746749);
}
void car_H_mod_fun(double *state, double *out_8410823161376016702) {
  H_mod_fun(state, out_8410823161376016702);
}
void car_f_fun(double *state, double dt, double *out_8406538155675584278) {
  f_fun(state,  dt, out_8406538155675584278);
}
void car_F_fun(double *state, double dt, double *out_9168420830296677739) {
  F_fun(state,  dt, out_9168420830296677739);
}
void car_h_25(double *state, double *unused, double *out_6925664705835598268) {
  h_25(state, unused, out_6925664705835598268);
}
void car_H_25(double *state, double *unused, double *out_842732686421297677) {
  H_25(state, unused, out_842732686421297677);
}
void car_h_24(double *state, double *unused, double *out_611774507479316058) {
  h_24(state, unused, out_611774507479316058);
}
void car_H_24(double *state, double *unused, double *out_7496938144529483434) {
  H_24(state, unused, out_7496938144529483434);
}
void car_h_30(double *state, double *unused, double *out_7082851374186727413) {
  h_30(state, unused, out_7082851374186727413);
}
void car_H_30(double *state, double *unused, double *out_3684963643706310521) {
  H_30(state, unused, out_3684963643706310521);
}
void car_h_26(double *state, double *unused, double *out_6139341521285064978) {
  h_26(state, unused, out_6139341521285064978);
}
void car_H_26(double *state, double *unused, double *out_2898770632452758547) {
  H_26(state, unused, out_2898770632452758547);
}
void car_h_27(double *state, double *unused, double *out_8484293316429620663) {
  h_27(state, unused, out_8484293316429620663);
}
void car_H_27(double *state, double *unused, double *out_5859726955506735432) {
  H_27(state, unused, out_5859726955506735432);
}
void car_h_29(double *state, double *unused, double *out_2081178106525881768) {
  h_29(state, unused, out_2081178106525881768);
}
void car_H_29(double *state, double *unused, double *out_3174732299391918337) {
  H_29(state, unused, out_3174732299391918337);
}
void car_h_28(double *state, double *unused, double *out_9087609201106098180) {
  h_28(state, unused, out_9087609201106098180);
}
void car_H_28(double *state, double *unused, double *out_8257131316461448911) {
  H_28(state, unused, out_8257131316461448911);
}
void car_h_31(double *state, double *unused, double *out_7580923347048146882) {
  h_31(state, unused, out_7580923347048146882);
}
void car_H_31(double *state, double *unused, double *out_3524978734686110023) {
  H_31(state, unused, out_3524978734686110023);
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
