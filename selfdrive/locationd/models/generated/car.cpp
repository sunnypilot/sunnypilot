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
void err_fun(double *nom_x, double *delta_x, double *out_7675945724591624261) {
   out_7675945724591624261[0] = delta_x[0] + nom_x[0];
   out_7675945724591624261[1] = delta_x[1] + nom_x[1];
   out_7675945724591624261[2] = delta_x[2] + nom_x[2];
   out_7675945724591624261[3] = delta_x[3] + nom_x[3];
   out_7675945724591624261[4] = delta_x[4] + nom_x[4];
   out_7675945724591624261[5] = delta_x[5] + nom_x[5];
   out_7675945724591624261[6] = delta_x[6] + nom_x[6];
   out_7675945724591624261[7] = delta_x[7] + nom_x[7];
   out_7675945724591624261[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_9175739039507983624) {
   out_9175739039507983624[0] = -nom_x[0] + true_x[0];
   out_9175739039507983624[1] = -nom_x[1] + true_x[1];
   out_9175739039507983624[2] = -nom_x[2] + true_x[2];
   out_9175739039507983624[3] = -nom_x[3] + true_x[3];
   out_9175739039507983624[4] = -nom_x[4] + true_x[4];
   out_9175739039507983624[5] = -nom_x[5] + true_x[5];
   out_9175739039507983624[6] = -nom_x[6] + true_x[6];
   out_9175739039507983624[7] = -nom_x[7] + true_x[7];
   out_9175739039507983624[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_4679052084973721620) {
   out_4679052084973721620[0] = 1.0;
   out_4679052084973721620[1] = 0;
   out_4679052084973721620[2] = 0;
   out_4679052084973721620[3] = 0;
   out_4679052084973721620[4] = 0;
   out_4679052084973721620[5] = 0;
   out_4679052084973721620[6] = 0;
   out_4679052084973721620[7] = 0;
   out_4679052084973721620[8] = 0;
   out_4679052084973721620[9] = 0;
   out_4679052084973721620[10] = 1.0;
   out_4679052084973721620[11] = 0;
   out_4679052084973721620[12] = 0;
   out_4679052084973721620[13] = 0;
   out_4679052084973721620[14] = 0;
   out_4679052084973721620[15] = 0;
   out_4679052084973721620[16] = 0;
   out_4679052084973721620[17] = 0;
   out_4679052084973721620[18] = 0;
   out_4679052084973721620[19] = 0;
   out_4679052084973721620[20] = 1.0;
   out_4679052084973721620[21] = 0;
   out_4679052084973721620[22] = 0;
   out_4679052084973721620[23] = 0;
   out_4679052084973721620[24] = 0;
   out_4679052084973721620[25] = 0;
   out_4679052084973721620[26] = 0;
   out_4679052084973721620[27] = 0;
   out_4679052084973721620[28] = 0;
   out_4679052084973721620[29] = 0;
   out_4679052084973721620[30] = 1.0;
   out_4679052084973721620[31] = 0;
   out_4679052084973721620[32] = 0;
   out_4679052084973721620[33] = 0;
   out_4679052084973721620[34] = 0;
   out_4679052084973721620[35] = 0;
   out_4679052084973721620[36] = 0;
   out_4679052084973721620[37] = 0;
   out_4679052084973721620[38] = 0;
   out_4679052084973721620[39] = 0;
   out_4679052084973721620[40] = 1.0;
   out_4679052084973721620[41] = 0;
   out_4679052084973721620[42] = 0;
   out_4679052084973721620[43] = 0;
   out_4679052084973721620[44] = 0;
   out_4679052084973721620[45] = 0;
   out_4679052084973721620[46] = 0;
   out_4679052084973721620[47] = 0;
   out_4679052084973721620[48] = 0;
   out_4679052084973721620[49] = 0;
   out_4679052084973721620[50] = 1.0;
   out_4679052084973721620[51] = 0;
   out_4679052084973721620[52] = 0;
   out_4679052084973721620[53] = 0;
   out_4679052084973721620[54] = 0;
   out_4679052084973721620[55] = 0;
   out_4679052084973721620[56] = 0;
   out_4679052084973721620[57] = 0;
   out_4679052084973721620[58] = 0;
   out_4679052084973721620[59] = 0;
   out_4679052084973721620[60] = 1.0;
   out_4679052084973721620[61] = 0;
   out_4679052084973721620[62] = 0;
   out_4679052084973721620[63] = 0;
   out_4679052084973721620[64] = 0;
   out_4679052084973721620[65] = 0;
   out_4679052084973721620[66] = 0;
   out_4679052084973721620[67] = 0;
   out_4679052084973721620[68] = 0;
   out_4679052084973721620[69] = 0;
   out_4679052084973721620[70] = 1.0;
   out_4679052084973721620[71] = 0;
   out_4679052084973721620[72] = 0;
   out_4679052084973721620[73] = 0;
   out_4679052084973721620[74] = 0;
   out_4679052084973721620[75] = 0;
   out_4679052084973721620[76] = 0;
   out_4679052084973721620[77] = 0;
   out_4679052084973721620[78] = 0;
   out_4679052084973721620[79] = 0;
   out_4679052084973721620[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_2673333106136537243) {
   out_2673333106136537243[0] = state[0];
   out_2673333106136537243[1] = state[1];
   out_2673333106136537243[2] = state[2];
   out_2673333106136537243[3] = state[3];
   out_2673333106136537243[4] = state[4];
   out_2673333106136537243[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8000000000000007*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_2673333106136537243[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_2673333106136537243[7] = state[7];
   out_2673333106136537243[8] = state[8];
}
void F_fun(double *state, double dt, double *out_5868321442563579311) {
   out_5868321442563579311[0] = 1;
   out_5868321442563579311[1] = 0;
   out_5868321442563579311[2] = 0;
   out_5868321442563579311[3] = 0;
   out_5868321442563579311[4] = 0;
   out_5868321442563579311[5] = 0;
   out_5868321442563579311[6] = 0;
   out_5868321442563579311[7] = 0;
   out_5868321442563579311[8] = 0;
   out_5868321442563579311[9] = 0;
   out_5868321442563579311[10] = 1;
   out_5868321442563579311[11] = 0;
   out_5868321442563579311[12] = 0;
   out_5868321442563579311[13] = 0;
   out_5868321442563579311[14] = 0;
   out_5868321442563579311[15] = 0;
   out_5868321442563579311[16] = 0;
   out_5868321442563579311[17] = 0;
   out_5868321442563579311[18] = 0;
   out_5868321442563579311[19] = 0;
   out_5868321442563579311[20] = 1;
   out_5868321442563579311[21] = 0;
   out_5868321442563579311[22] = 0;
   out_5868321442563579311[23] = 0;
   out_5868321442563579311[24] = 0;
   out_5868321442563579311[25] = 0;
   out_5868321442563579311[26] = 0;
   out_5868321442563579311[27] = 0;
   out_5868321442563579311[28] = 0;
   out_5868321442563579311[29] = 0;
   out_5868321442563579311[30] = 1;
   out_5868321442563579311[31] = 0;
   out_5868321442563579311[32] = 0;
   out_5868321442563579311[33] = 0;
   out_5868321442563579311[34] = 0;
   out_5868321442563579311[35] = 0;
   out_5868321442563579311[36] = 0;
   out_5868321442563579311[37] = 0;
   out_5868321442563579311[38] = 0;
   out_5868321442563579311[39] = 0;
   out_5868321442563579311[40] = 1;
   out_5868321442563579311[41] = 0;
   out_5868321442563579311[42] = 0;
   out_5868321442563579311[43] = 0;
   out_5868321442563579311[44] = 0;
   out_5868321442563579311[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_5868321442563579311[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_5868321442563579311[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_5868321442563579311[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_5868321442563579311[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_5868321442563579311[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_5868321442563579311[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_5868321442563579311[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_5868321442563579311[53] = -9.8000000000000007*dt;
   out_5868321442563579311[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_5868321442563579311[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_5868321442563579311[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_5868321442563579311[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_5868321442563579311[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_5868321442563579311[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_5868321442563579311[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_5868321442563579311[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_5868321442563579311[62] = 0;
   out_5868321442563579311[63] = 0;
   out_5868321442563579311[64] = 0;
   out_5868321442563579311[65] = 0;
   out_5868321442563579311[66] = 0;
   out_5868321442563579311[67] = 0;
   out_5868321442563579311[68] = 0;
   out_5868321442563579311[69] = 0;
   out_5868321442563579311[70] = 1;
   out_5868321442563579311[71] = 0;
   out_5868321442563579311[72] = 0;
   out_5868321442563579311[73] = 0;
   out_5868321442563579311[74] = 0;
   out_5868321442563579311[75] = 0;
   out_5868321442563579311[76] = 0;
   out_5868321442563579311[77] = 0;
   out_5868321442563579311[78] = 0;
   out_5868321442563579311[79] = 0;
   out_5868321442563579311[80] = 1;
}
void h_25(double *state, double *unused, double *out_417479862903067851) {
   out_417479862903067851[0] = state[6];
}
void H_25(double *state, double *unused, double *out_2343775444601259513) {
   out_2343775444601259513[0] = 0;
   out_2343775444601259513[1] = 0;
   out_2343775444601259513[2] = 0;
   out_2343775444601259513[3] = 0;
   out_2343775444601259513[4] = 0;
   out_2343775444601259513[5] = 0;
   out_2343775444601259513[6] = 1;
   out_2343775444601259513[7] = 0;
   out_2343775444601259513[8] = 0;
}
void h_24(double *state, double *unused, double *out_2649485575402304942) {
   out_2649485575402304942[0] = state[4];
   out_2649485575402304942[1] = state[5];
}
void H_24(double *state, double *unused, double *out_4516425043606759079) {
   out_4516425043606759079[0] = 0;
   out_4516425043606759079[1] = 0;
   out_4516425043606759079[2] = 0;
   out_4516425043606759079[3] = 0;
   out_4516425043606759079[4] = 1;
   out_4516425043606759079[5] = 0;
   out_4516425043606759079[6] = 0;
   out_4516425043606759079[7] = 0;
   out_4516425043606759079[8] = 0;
   out_4516425043606759079[9] = 0;
   out_4516425043606759079[10] = 0;
   out_4516425043606759079[11] = 0;
   out_4516425043606759079[12] = 0;
   out_4516425043606759079[13] = 0;
   out_4516425043606759079[14] = 1;
   out_4516425043606759079[15] = 0;
   out_4516425043606759079[16] = 0;
   out_4516425043606759079[17] = 0;
}
void h_30(double *state, double *unused, double *out_9057357339621609735) {
   out_9057357339621609735[0] = state[4];
}
void H_30(double *state, double *unused, double *out_6871471774728867711) {
   out_6871471774728867711[0] = 0;
   out_6871471774728867711[1] = 0;
   out_6871471774728867711[2] = 0;
   out_6871471774728867711[3] = 0;
   out_6871471774728867711[4] = 1;
   out_6871471774728867711[5] = 0;
   out_6871471774728867711[6] = 0;
   out_6871471774728867711[7] = 0;
   out_6871471774728867711[8] = 0;
}
void h_26(double *state, double *unused, double *out_6244805236351756352) {
   out_6244805236351756352[0] = state[7];
}
void H_26(double *state, double *unused, double *out_6085278763475315737) {
   out_6085278763475315737[0] = 0;
   out_6085278763475315737[1] = 0;
   out_6085278763475315737[2] = 0;
   out_6085278763475315737[3] = 0;
   out_6085278763475315737[4] = 0;
   out_6085278763475315737[5] = 0;
   out_6085278763475315737[6] = 0;
   out_6085278763475315737[7] = 1;
   out_6085278763475315737[8] = 0;
}
void h_27(double *state, double *unused, double *out_3454265914347400536) {
   out_3454265914347400536[0] = state[3];
}
void H_27(double *state, double *unused, double *out_4647877703544924494) {
   out_4647877703544924494[0] = 0;
   out_4647877703544924494[1] = 0;
   out_4647877703544924494[2] = 0;
   out_4647877703544924494[3] = 1;
   out_4647877703544924494[4] = 0;
   out_4647877703544924494[5] = 0;
   out_4647877703544924494[6] = 0;
   out_4647877703544924494[7] = 0;
   out_4647877703544924494[8] = 0;
}
void h_29(double *state, double *unused, double *out_8221642933011800144) {
   out_8221642933011800144[0] = state[1];
}
void H_29(double *state, double *unused, double *out_6361240430414475527) {
   out_6361240430414475527[0] = 0;
   out_6361240430414475527[1] = 1;
   out_6361240430414475527[2] = 0;
   out_6361240430414475527[3] = 0;
   out_6361240430414475527[4] = 0;
   out_6361240430414475527[5] = 0;
   out_6361240430414475527[6] = 0;
   out_6361240430414475527[7] = 0;
   out_6361240430414475527[8] = 0;
}
void h_28(double *state, double *unused, double *out_1167920115108707778) {
   out_1167920115108707778[0] = state[0];
}
void H_28(double *state, double *unused, double *out_4397610158849149276) {
   out_4397610158849149276[0] = 1;
   out_4397610158849149276[1] = 0;
   out_4397610158849149276[2] = 0;
   out_4397610158849149276[3] = 0;
   out_4397610158849149276[4] = 0;
   out_4397610158849149276[5] = 0;
   out_4397610158849149276[6] = 0;
   out_4397610158849149276[7] = 0;
   out_4397610158849149276[8] = 0;
}
void h_31(double *state, double *unused, double *out_692673925187573740) {
   out_692673925187573740[0] = state[8];
}
void H_31(double *state, double *unused, double *out_2313129482724299085) {
   out_2313129482724299085[0] = 0;
   out_2313129482724299085[1] = 0;
   out_2313129482724299085[2] = 0;
   out_2313129482724299085[3] = 0;
   out_2313129482724299085[4] = 0;
   out_2313129482724299085[5] = 0;
   out_2313129482724299085[6] = 0;
   out_2313129482724299085[7] = 0;
   out_2313129482724299085[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_7675945724591624261) {
  err_fun(nom_x, delta_x, out_7675945724591624261);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_9175739039507983624) {
  inv_err_fun(nom_x, true_x, out_9175739039507983624);
}
void car_H_mod_fun(double *state, double *out_4679052084973721620) {
  H_mod_fun(state, out_4679052084973721620);
}
void car_f_fun(double *state, double dt, double *out_2673333106136537243) {
  f_fun(state,  dt, out_2673333106136537243);
}
void car_F_fun(double *state, double dt, double *out_5868321442563579311) {
  F_fun(state,  dt, out_5868321442563579311);
}
void car_h_25(double *state, double *unused, double *out_417479862903067851) {
  h_25(state, unused, out_417479862903067851);
}
void car_H_25(double *state, double *unused, double *out_2343775444601259513) {
  H_25(state, unused, out_2343775444601259513);
}
void car_h_24(double *state, double *unused, double *out_2649485575402304942) {
  h_24(state, unused, out_2649485575402304942);
}
void car_H_24(double *state, double *unused, double *out_4516425043606759079) {
  H_24(state, unused, out_4516425043606759079);
}
void car_h_30(double *state, double *unused, double *out_9057357339621609735) {
  h_30(state, unused, out_9057357339621609735);
}
void car_H_30(double *state, double *unused, double *out_6871471774728867711) {
  H_30(state, unused, out_6871471774728867711);
}
void car_h_26(double *state, double *unused, double *out_6244805236351756352) {
  h_26(state, unused, out_6244805236351756352);
}
void car_H_26(double *state, double *unused, double *out_6085278763475315737) {
  H_26(state, unused, out_6085278763475315737);
}
void car_h_27(double *state, double *unused, double *out_3454265914347400536) {
  h_27(state, unused, out_3454265914347400536);
}
void car_H_27(double *state, double *unused, double *out_4647877703544924494) {
  H_27(state, unused, out_4647877703544924494);
}
void car_h_29(double *state, double *unused, double *out_8221642933011800144) {
  h_29(state, unused, out_8221642933011800144);
}
void car_H_29(double *state, double *unused, double *out_6361240430414475527) {
  H_29(state, unused, out_6361240430414475527);
}
void car_h_28(double *state, double *unused, double *out_1167920115108707778) {
  h_28(state, unused, out_1167920115108707778);
}
void car_H_28(double *state, double *unused, double *out_4397610158849149276) {
  H_28(state, unused, out_4397610158849149276);
}
void car_h_31(double *state, double *unused, double *out_692673925187573740) {
  h_31(state, unused, out_692673925187573740);
}
void car_H_31(double *state, double *unused, double *out_2313129482724299085) {
  H_31(state, unused, out_2313129482724299085);
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
