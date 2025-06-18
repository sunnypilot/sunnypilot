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
void err_fun(double *nom_x, double *delta_x, double *out_6475690049946676788) {
   out_6475690049946676788[0] = delta_x[0] + nom_x[0];
   out_6475690049946676788[1] = delta_x[1] + nom_x[1];
   out_6475690049946676788[2] = delta_x[2] + nom_x[2];
   out_6475690049946676788[3] = delta_x[3] + nom_x[3];
   out_6475690049946676788[4] = delta_x[4] + nom_x[4];
   out_6475690049946676788[5] = delta_x[5] + nom_x[5];
   out_6475690049946676788[6] = delta_x[6] + nom_x[6];
   out_6475690049946676788[7] = delta_x[7] + nom_x[7];
   out_6475690049946676788[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_2648638800343186983) {
   out_2648638800343186983[0] = -nom_x[0] + true_x[0];
   out_2648638800343186983[1] = -nom_x[1] + true_x[1];
   out_2648638800343186983[2] = -nom_x[2] + true_x[2];
   out_2648638800343186983[3] = -nom_x[3] + true_x[3];
   out_2648638800343186983[4] = -nom_x[4] + true_x[4];
   out_2648638800343186983[5] = -nom_x[5] + true_x[5];
   out_2648638800343186983[6] = -nom_x[6] + true_x[6];
   out_2648638800343186983[7] = -nom_x[7] + true_x[7];
   out_2648638800343186983[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_3737699923818243103) {
   out_3737699923818243103[0] = 1.0;
   out_3737699923818243103[1] = 0.0;
   out_3737699923818243103[2] = 0.0;
   out_3737699923818243103[3] = 0.0;
   out_3737699923818243103[4] = 0.0;
   out_3737699923818243103[5] = 0.0;
   out_3737699923818243103[6] = 0.0;
   out_3737699923818243103[7] = 0.0;
   out_3737699923818243103[8] = 0.0;
   out_3737699923818243103[9] = 0.0;
   out_3737699923818243103[10] = 1.0;
   out_3737699923818243103[11] = 0.0;
   out_3737699923818243103[12] = 0.0;
   out_3737699923818243103[13] = 0.0;
   out_3737699923818243103[14] = 0.0;
   out_3737699923818243103[15] = 0.0;
   out_3737699923818243103[16] = 0.0;
   out_3737699923818243103[17] = 0.0;
   out_3737699923818243103[18] = 0.0;
   out_3737699923818243103[19] = 0.0;
   out_3737699923818243103[20] = 1.0;
   out_3737699923818243103[21] = 0.0;
   out_3737699923818243103[22] = 0.0;
   out_3737699923818243103[23] = 0.0;
   out_3737699923818243103[24] = 0.0;
   out_3737699923818243103[25] = 0.0;
   out_3737699923818243103[26] = 0.0;
   out_3737699923818243103[27] = 0.0;
   out_3737699923818243103[28] = 0.0;
   out_3737699923818243103[29] = 0.0;
   out_3737699923818243103[30] = 1.0;
   out_3737699923818243103[31] = 0.0;
   out_3737699923818243103[32] = 0.0;
   out_3737699923818243103[33] = 0.0;
   out_3737699923818243103[34] = 0.0;
   out_3737699923818243103[35] = 0.0;
   out_3737699923818243103[36] = 0.0;
   out_3737699923818243103[37] = 0.0;
   out_3737699923818243103[38] = 0.0;
   out_3737699923818243103[39] = 0.0;
   out_3737699923818243103[40] = 1.0;
   out_3737699923818243103[41] = 0.0;
   out_3737699923818243103[42] = 0.0;
   out_3737699923818243103[43] = 0.0;
   out_3737699923818243103[44] = 0.0;
   out_3737699923818243103[45] = 0.0;
   out_3737699923818243103[46] = 0.0;
   out_3737699923818243103[47] = 0.0;
   out_3737699923818243103[48] = 0.0;
   out_3737699923818243103[49] = 0.0;
   out_3737699923818243103[50] = 1.0;
   out_3737699923818243103[51] = 0.0;
   out_3737699923818243103[52] = 0.0;
   out_3737699923818243103[53] = 0.0;
   out_3737699923818243103[54] = 0.0;
   out_3737699923818243103[55] = 0.0;
   out_3737699923818243103[56] = 0.0;
   out_3737699923818243103[57] = 0.0;
   out_3737699923818243103[58] = 0.0;
   out_3737699923818243103[59] = 0.0;
   out_3737699923818243103[60] = 1.0;
   out_3737699923818243103[61] = 0.0;
   out_3737699923818243103[62] = 0.0;
   out_3737699923818243103[63] = 0.0;
   out_3737699923818243103[64] = 0.0;
   out_3737699923818243103[65] = 0.0;
   out_3737699923818243103[66] = 0.0;
   out_3737699923818243103[67] = 0.0;
   out_3737699923818243103[68] = 0.0;
   out_3737699923818243103[69] = 0.0;
   out_3737699923818243103[70] = 1.0;
   out_3737699923818243103[71] = 0.0;
   out_3737699923818243103[72] = 0.0;
   out_3737699923818243103[73] = 0.0;
   out_3737699923818243103[74] = 0.0;
   out_3737699923818243103[75] = 0.0;
   out_3737699923818243103[76] = 0.0;
   out_3737699923818243103[77] = 0.0;
   out_3737699923818243103[78] = 0.0;
   out_3737699923818243103[79] = 0.0;
   out_3737699923818243103[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_6948342231464486417) {
   out_6948342231464486417[0] = state[0];
   out_6948342231464486417[1] = state[1];
   out_6948342231464486417[2] = state[2];
   out_6948342231464486417[3] = state[3];
   out_6948342231464486417[4] = state[4];
   out_6948342231464486417[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8000000000000007*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_6948342231464486417[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_6948342231464486417[7] = state[7];
   out_6948342231464486417[8] = state[8];
}
void F_fun(double *state, double dt, double *out_2362643557470783203) {
   out_2362643557470783203[0] = 1;
   out_2362643557470783203[1] = 0;
   out_2362643557470783203[2] = 0;
   out_2362643557470783203[3] = 0;
   out_2362643557470783203[4] = 0;
   out_2362643557470783203[5] = 0;
   out_2362643557470783203[6] = 0;
   out_2362643557470783203[7] = 0;
   out_2362643557470783203[8] = 0;
   out_2362643557470783203[9] = 0;
   out_2362643557470783203[10] = 1;
   out_2362643557470783203[11] = 0;
   out_2362643557470783203[12] = 0;
   out_2362643557470783203[13] = 0;
   out_2362643557470783203[14] = 0;
   out_2362643557470783203[15] = 0;
   out_2362643557470783203[16] = 0;
   out_2362643557470783203[17] = 0;
   out_2362643557470783203[18] = 0;
   out_2362643557470783203[19] = 0;
   out_2362643557470783203[20] = 1;
   out_2362643557470783203[21] = 0;
   out_2362643557470783203[22] = 0;
   out_2362643557470783203[23] = 0;
   out_2362643557470783203[24] = 0;
   out_2362643557470783203[25] = 0;
   out_2362643557470783203[26] = 0;
   out_2362643557470783203[27] = 0;
   out_2362643557470783203[28] = 0;
   out_2362643557470783203[29] = 0;
   out_2362643557470783203[30] = 1;
   out_2362643557470783203[31] = 0;
   out_2362643557470783203[32] = 0;
   out_2362643557470783203[33] = 0;
   out_2362643557470783203[34] = 0;
   out_2362643557470783203[35] = 0;
   out_2362643557470783203[36] = 0;
   out_2362643557470783203[37] = 0;
   out_2362643557470783203[38] = 0;
   out_2362643557470783203[39] = 0;
   out_2362643557470783203[40] = 1;
   out_2362643557470783203[41] = 0;
   out_2362643557470783203[42] = 0;
   out_2362643557470783203[43] = 0;
   out_2362643557470783203[44] = 0;
   out_2362643557470783203[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_2362643557470783203[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_2362643557470783203[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_2362643557470783203[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_2362643557470783203[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_2362643557470783203[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_2362643557470783203[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_2362643557470783203[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_2362643557470783203[53] = -9.8000000000000007*dt;
   out_2362643557470783203[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_2362643557470783203[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_2362643557470783203[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_2362643557470783203[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_2362643557470783203[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_2362643557470783203[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_2362643557470783203[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_2362643557470783203[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_2362643557470783203[62] = 0;
   out_2362643557470783203[63] = 0;
   out_2362643557470783203[64] = 0;
   out_2362643557470783203[65] = 0;
   out_2362643557470783203[66] = 0;
   out_2362643557470783203[67] = 0;
   out_2362643557470783203[68] = 0;
   out_2362643557470783203[69] = 0;
   out_2362643557470783203[70] = 1;
   out_2362643557470783203[71] = 0;
   out_2362643557470783203[72] = 0;
   out_2362643557470783203[73] = 0;
   out_2362643557470783203[74] = 0;
   out_2362643557470783203[75] = 0;
   out_2362643557470783203[76] = 0;
   out_2362643557470783203[77] = 0;
   out_2362643557470783203[78] = 0;
   out_2362643557470783203[79] = 0;
   out_2362643557470783203[80] = 1;
}
void h_25(double *state, double *unused, double *out_7765488061907301122) {
   out_7765488061907301122[0] = state[6];
}
void H_25(double *state, double *unused, double *out_2788579001789760894) {
   out_2788579001789760894[0] = 0;
   out_2788579001789760894[1] = 0;
   out_2788579001789760894[2] = 0;
   out_2788579001789760894[3] = 0;
   out_2788579001789760894[4] = 0;
   out_2788579001789760894[5] = 0;
   out_2788579001789760894[6] = 1;
   out_2788579001789760894[7] = 0;
   out_2788579001789760894[8] = 0;
}
void h_24(double *state, double *unused, double *out_6031389446812726956) {
   out_6031389446812726956[0] = state[4];
   out_6031389446812726956[1] = state[5];
}
void H_24(double *state, double *unused, double *out_769346597012562242) {
   out_769346597012562242[0] = 0;
   out_769346597012562242[1] = 0;
   out_769346597012562242[2] = 0;
   out_769346597012562242[3] = 0;
   out_769346597012562242[4] = 1;
   out_769346597012562242[5] = 0;
   out_769346597012562242[6] = 0;
   out_769346597012562242[7] = 0;
   out_769346597012562242[8] = 0;
   out_769346597012562242[9] = 0;
   out_769346597012562242[10] = 0;
   out_769346597012562242[11] = 0;
   out_769346597012562242[12] = 0;
   out_769346597012562242[13] = 0;
   out_769346597012562242[14] = 1;
   out_769346597012562242[15] = 0;
   out_769346597012562242[16] = 0;
   out_769346597012562242[17] = 0;
}
void h_30(double *state, double *unused, double *out_2239430625356278009) {
   out_2239430625356278009[0] = state[4];
}
void H_30(double *state, double *unused, double *out_4128111339701855861) {
   out_4128111339701855861[0] = 0;
   out_4128111339701855861[1] = 0;
   out_4128111339701855861[2] = 0;
   out_4128111339701855861[3] = 0;
   out_4128111339701855861[4] = 1;
   out_4128111339701855861[5] = 0;
   out_4128111339701855861[6] = 0;
   out_4128111339701855861[7] = 0;
   out_4128111339701855861[8] = 0;
}
void h_26(double *state, double *unused, double *out_4007020432103895459) {
   out_4007020432103895459[0] = state[7];
}
void H_26(double *state, double *unused, double *out_6530082320663817118) {
   out_6530082320663817118[0] = 0;
   out_6530082320663817118[1] = 0;
   out_6530082320663817118[2] = 0;
   out_6530082320663817118[3] = 0;
   out_6530082320663817118[4] = 0;
   out_6530082320663817118[5] = 0;
   out_6530082320663817118[6] = 0;
   out_6530082320663817118[7] = 1;
   out_6530082320663817118[8] = 0;
}
void h_27(double *state, double *unused, double *out_5038526140721293659) {
   out_5038526140721293659[0] = state[3];
}
void H_27(double *state, double *unused, double *out_5092681260733425875) {
   out_5092681260733425875[0] = 0;
   out_5092681260733425875[1] = 0;
   out_5092681260733425875[2] = 0;
   out_5092681260733425875[3] = 1;
   out_5092681260733425875[4] = 0;
   out_5092681260733425875[5] = 0;
   out_5092681260733425875[6] = 0;
   out_5092681260733425875[7] = 0;
   out_5092681260733425875[8] = 0;
}
void h_29(double *state, double *unused, double *out_4763332078436787770) {
   out_4763332078436787770[0] = state[1];
}
void H_29(double *state, double *unused, double *out_2407686604618608780) {
   out_2407686604618608780[0] = 0;
   out_2407686604618608780[1] = 1;
   out_2407686604618608780[2] = 0;
   out_2407686604618608780[3] = 0;
   out_2407686604618608780[4] = 0;
   out_2407686604618608780[5] = 0;
   out_2407686604618608780[6] = 0;
   out_2407686604618608780[7] = 0;
   out_2407686604618608780[8] = 0;
}
void h_28(double *state, double *unused, double *out_7425294093682116204) {
   out_7425294093682116204[0] = state[0];
}
void H_28(double *state, double *unused, double *out_444056333053282529) {
   out_444056333053282529[0] = 1;
   out_444056333053282529[1] = 0;
   out_444056333053282529[2] = 0;
   out_444056333053282529[3] = 0;
   out_444056333053282529[4] = 0;
   out_444056333053282529[5] = 0;
   out_444056333053282529[6] = 0;
   out_444056333053282529[7] = 0;
   out_444056333053282529[8] = 0;
}
void h_31(double *state, double *unused, double *out_4769095137073389962) {
   out_4769095137073389962[0] = state[8];
}
void H_31(double *state, double *unused, double *out_2757933039912800466) {
   out_2757933039912800466[0] = 0;
   out_2757933039912800466[1] = 0;
   out_2757933039912800466[2] = 0;
   out_2757933039912800466[3] = 0;
   out_2757933039912800466[4] = 0;
   out_2757933039912800466[5] = 0;
   out_2757933039912800466[6] = 0;
   out_2757933039912800466[7] = 0;
   out_2757933039912800466[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_6475690049946676788) {
  err_fun(nom_x, delta_x, out_6475690049946676788);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_2648638800343186983) {
  inv_err_fun(nom_x, true_x, out_2648638800343186983);
}
void car_H_mod_fun(double *state, double *out_3737699923818243103) {
  H_mod_fun(state, out_3737699923818243103);
}
void car_f_fun(double *state, double dt, double *out_6948342231464486417) {
  f_fun(state,  dt, out_6948342231464486417);
}
void car_F_fun(double *state, double dt, double *out_2362643557470783203) {
  F_fun(state,  dt, out_2362643557470783203);
}
void car_h_25(double *state, double *unused, double *out_7765488061907301122) {
  h_25(state, unused, out_7765488061907301122);
}
void car_H_25(double *state, double *unused, double *out_2788579001789760894) {
  H_25(state, unused, out_2788579001789760894);
}
void car_h_24(double *state, double *unused, double *out_6031389446812726956) {
  h_24(state, unused, out_6031389446812726956);
}
void car_H_24(double *state, double *unused, double *out_769346597012562242) {
  H_24(state, unused, out_769346597012562242);
}
void car_h_30(double *state, double *unused, double *out_2239430625356278009) {
  h_30(state, unused, out_2239430625356278009);
}
void car_H_30(double *state, double *unused, double *out_4128111339701855861) {
  H_30(state, unused, out_4128111339701855861);
}
void car_h_26(double *state, double *unused, double *out_4007020432103895459) {
  h_26(state, unused, out_4007020432103895459);
}
void car_H_26(double *state, double *unused, double *out_6530082320663817118) {
  H_26(state, unused, out_6530082320663817118);
}
void car_h_27(double *state, double *unused, double *out_5038526140721293659) {
  h_27(state, unused, out_5038526140721293659);
}
void car_H_27(double *state, double *unused, double *out_5092681260733425875) {
  H_27(state, unused, out_5092681260733425875);
}
void car_h_29(double *state, double *unused, double *out_4763332078436787770) {
  h_29(state, unused, out_4763332078436787770);
}
void car_H_29(double *state, double *unused, double *out_2407686604618608780) {
  H_29(state, unused, out_2407686604618608780);
}
void car_h_28(double *state, double *unused, double *out_7425294093682116204) {
  h_28(state, unused, out_7425294093682116204);
}
void car_H_28(double *state, double *unused, double *out_444056333053282529) {
  H_28(state, unused, out_444056333053282529);
}
void car_h_31(double *state, double *unused, double *out_4769095137073389962) {
  h_31(state, unused, out_4769095137073389962);
}
void car_H_31(double *state, double *unused, double *out_2757933039912800466) {
  H_31(state, unused, out_2757933039912800466);
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
