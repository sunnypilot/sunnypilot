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
void err_fun(double *nom_x, double *delta_x, double *out_8152243261381841861) {
   out_8152243261381841861[0] = delta_x[0] + nom_x[0];
   out_8152243261381841861[1] = delta_x[1] + nom_x[1];
   out_8152243261381841861[2] = delta_x[2] + nom_x[2];
   out_8152243261381841861[3] = delta_x[3] + nom_x[3];
   out_8152243261381841861[4] = delta_x[4] + nom_x[4];
   out_8152243261381841861[5] = delta_x[5] + nom_x[5];
   out_8152243261381841861[6] = delta_x[6] + nom_x[6];
   out_8152243261381841861[7] = delta_x[7] + nom_x[7];
   out_8152243261381841861[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_1302168845595593824) {
   out_1302168845595593824[0] = -nom_x[0] + true_x[0];
   out_1302168845595593824[1] = -nom_x[1] + true_x[1];
   out_1302168845595593824[2] = -nom_x[2] + true_x[2];
   out_1302168845595593824[3] = -nom_x[3] + true_x[3];
   out_1302168845595593824[4] = -nom_x[4] + true_x[4];
   out_1302168845595593824[5] = -nom_x[5] + true_x[5];
   out_1302168845595593824[6] = -nom_x[6] + true_x[6];
   out_1302168845595593824[7] = -nom_x[7] + true_x[7];
   out_1302168845595593824[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_720082183471150414) {
   out_720082183471150414[0] = 1.0;
   out_720082183471150414[1] = 0;
   out_720082183471150414[2] = 0;
   out_720082183471150414[3] = 0;
   out_720082183471150414[4] = 0;
   out_720082183471150414[5] = 0;
   out_720082183471150414[6] = 0;
   out_720082183471150414[7] = 0;
   out_720082183471150414[8] = 0;
   out_720082183471150414[9] = 0;
   out_720082183471150414[10] = 1.0;
   out_720082183471150414[11] = 0;
   out_720082183471150414[12] = 0;
   out_720082183471150414[13] = 0;
   out_720082183471150414[14] = 0;
   out_720082183471150414[15] = 0;
   out_720082183471150414[16] = 0;
   out_720082183471150414[17] = 0;
   out_720082183471150414[18] = 0;
   out_720082183471150414[19] = 0;
   out_720082183471150414[20] = 1.0;
   out_720082183471150414[21] = 0;
   out_720082183471150414[22] = 0;
   out_720082183471150414[23] = 0;
   out_720082183471150414[24] = 0;
   out_720082183471150414[25] = 0;
   out_720082183471150414[26] = 0;
   out_720082183471150414[27] = 0;
   out_720082183471150414[28] = 0;
   out_720082183471150414[29] = 0;
   out_720082183471150414[30] = 1.0;
   out_720082183471150414[31] = 0;
   out_720082183471150414[32] = 0;
   out_720082183471150414[33] = 0;
   out_720082183471150414[34] = 0;
   out_720082183471150414[35] = 0;
   out_720082183471150414[36] = 0;
   out_720082183471150414[37] = 0;
   out_720082183471150414[38] = 0;
   out_720082183471150414[39] = 0;
   out_720082183471150414[40] = 1.0;
   out_720082183471150414[41] = 0;
   out_720082183471150414[42] = 0;
   out_720082183471150414[43] = 0;
   out_720082183471150414[44] = 0;
   out_720082183471150414[45] = 0;
   out_720082183471150414[46] = 0;
   out_720082183471150414[47] = 0;
   out_720082183471150414[48] = 0;
   out_720082183471150414[49] = 0;
   out_720082183471150414[50] = 1.0;
   out_720082183471150414[51] = 0;
   out_720082183471150414[52] = 0;
   out_720082183471150414[53] = 0;
   out_720082183471150414[54] = 0;
   out_720082183471150414[55] = 0;
   out_720082183471150414[56] = 0;
   out_720082183471150414[57] = 0;
   out_720082183471150414[58] = 0;
   out_720082183471150414[59] = 0;
   out_720082183471150414[60] = 1.0;
   out_720082183471150414[61] = 0;
   out_720082183471150414[62] = 0;
   out_720082183471150414[63] = 0;
   out_720082183471150414[64] = 0;
   out_720082183471150414[65] = 0;
   out_720082183471150414[66] = 0;
   out_720082183471150414[67] = 0;
   out_720082183471150414[68] = 0;
   out_720082183471150414[69] = 0;
   out_720082183471150414[70] = 1.0;
   out_720082183471150414[71] = 0;
   out_720082183471150414[72] = 0;
   out_720082183471150414[73] = 0;
   out_720082183471150414[74] = 0;
   out_720082183471150414[75] = 0;
   out_720082183471150414[76] = 0;
   out_720082183471150414[77] = 0;
   out_720082183471150414[78] = 0;
   out_720082183471150414[79] = 0;
   out_720082183471150414[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_1005905684588084232) {
   out_1005905684588084232[0] = state[0];
   out_1005905684588084232[1] = state[1];
   out_1005905684588084232[2] = state[2];
   out_1005905684588084232[3] = state[3];
   out_1005905684588084232[4] = state[4];
   out_1005905684588084232[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8000000000000007*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_1005905684588084232[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_1005905684588084232[7] = state[7];
   out_1005905684588084232[8] = state[8];
}
void F_fun(double *state, double dt, double *out_8578060064959244144) {
   out_8578060064959244144[0] = 1;
   out_8578060064959244144[1] = 0;
   out_8578060064959244144[2] = 0;
   out_8578060064959244144[3] = 0;
   out_8578060064959244144[4] = 0;
   out_8578060064959244144[5] = 0;
   out_8578060064959244144[6] = 0;
   out_8578060064959244144[7] = 0;
   out_8578060064959244144[8] = 0;
   out_8578060064959244144[9] = 0;
   out_8578060064959244144[10] = 1;
   out_8578060064959244144[11] = 0;
   out_8578060064959244144[12] = 0;
   out_8578060064959244144[13] = 0;
   out_8578060064959244144[14] = 0;
   out_8578060064959244144[15] = 0;
   out_8578060064959244144[16] = 0;
   out_8578060064959244144[17] = 0;
   out_8578060064959244144[18] = 0;
   out_8578060064959244144[19] = 0;
   out_8578060064959244144[20] = 1;
   out_8578060064959244144[21] = 0;
   out_8578060064959244144[22] = 0;
   out_8578060064959244144[23] = 0;
   out_8578060064959244144[24] = 0;
   out_8578060064959244144[25] = 0;
   out_8578060064959244144[26] = 0;
   out_8578060064959244144[27] = 0;
   out_8578060064959244144[28] = 0;
   out_8578060064959244144[29] = 0;
   out_8578060064959244144[30] = 1;
   out_8578060064959244144[31] = 0;
   out_8578060064959244144[32] = 0;
   out_8578060064959244144[33] = 0;
   out_8578060064959244144[34] = 0;
   out_8578060064959244144[35] = 0;
   out_8578060064959244144[36] = 0;
   out_8578060064959244144[37] = 0;
   out_8578060064959244144[38] = 0;
   out_8578060064959244144[39] = 0;
   out_8578060064959244144[40] = 1;
   out_8578060064959244144[41] = 0;
   out_8578060064959244144[42] = 0;
   out_8578060064959244144[43] = 0;
   out_8578060064959244144[44] = 0;
   out_8578060064959244144[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_8578060064959244144[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_8578060064959244144[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_8578060064959244144[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_8578060064959244144[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_8578060064959244144[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_8578060064959244144[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_8578060064959244144[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_8578060064959244144[53] = -9.8000000000000007*dt;
   out_8578060064959244144[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_8578060064959244144[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_8578060064959244144[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_8578060064959244144[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_8578060064959244144[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_8578060064959244144[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_8578060064959244144[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_8578060064959244144[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_8578060064959244144[62] = 0;
   out_8578060064959244144[63] = 0;
   out_8578060064959244144[64] = 0;
   out_8578060064959244144[65] = 0;
   out_8578060064959244144[66] = 0;
   out_8578060064959244144[67] = 0;
   out_8578060064959244144[68] = 0;
   out_8578060064959244144[69] = 0;
   out_8578060064959244144[70] = 1;
   out_8578060064959244144[71] = 0;
   out_8578060064959244144[72] = 0;
   out_8578060064959244144[73] = 0;
   out_8578060064959244144[74] = 0;
   out_8578060064959244144[75] = 0;
   out_8578060064959244144[76] = 0;
   out_8578060064959244144[77] = 0;
   out_8578060064959244144[78] = 0;
   out_8578060064959244144[79] = 0;
   out_8578060064959244144[80] = 1;
}
void h_25(double *state, double *unused, double *out_5524927027376144470) {
   out_5524927027376144470[0] = state[6];
}
void H_25(double *state, double *unused, double *out_3613918526609956662) {
   out_3613918526609956662[0] = 0;
   out_3613918526609956662[1] = 0;
   out_3613918526609956662[2] = 0;
   out_3613918526609956662[3] = 0;
   out_3613918526609956662[4] = 0;
   out_3613918526609956662[5] = 0;
   out_3613918526609956662[6] = 1;
   out_3613918526609956662[7] = 0;
   out_3613918526609956662[8] = 0;
}
void h_24(double *state, double *unused, double *out_2463198998502258202) {
   out_2463198998502258202[0] = state[4];
   out_2463198998502258202[1] = state[5];
}
void H_24(double *state, double *unused, double *out_8257253740508076853) {
   out_8257253740508076853[0] = 0;
   out_8257253740508076853[1] = 0;
   out_8257253740508076853[2] = 0;
   out_8257253740508076853[3] = 0;
   out_8257253740508076853[4] = 1;
   out_8257253740508076853[5] = 0;
   out_8257253740508076853[6] = 0;
   out_8257253740508076853[7] = 0;
   out_8257253740508076853[8] = 0;
   out_8257253740508076853[9] = 0;
   out_8257253740508076853[10] = 0;
   out_8257253740508076853[11] = 0;
   out_8257253740508076853[12] = 0;
   out_8257253740508076853[13] = 0;
   out_8257253740508076853[14] = 1;
   out_8257253740508076853[15] = 0;
   out_8257253740508076853[16] = 0;
   out_8257253740508076853[17] = 0;
}
void h_30(double *state, double *unused, double *out_2577201037020659509) {
   out_2577201037020659509[0] = state[4];
}
void H_30(double *state, double *unused, double *out_6132251485117205289) {
   out_6132251485117205289[0] = 0;
   out_6132251485117205289[1] = 0;
   out_6132251485117205289[2] = 0;
   out_6132251485117205289[3] = 0;
   out_6132251485117205289[4] = 1;
   out_6132251485117205289[5] = 0;
   out_6132251485117205289[6] = 0;
   out_6132251485117205289[7] = 0;
   out_6132251485117205289[8] = 0;
}
void h_26(double *state, double *unused, double *out_6404768134986181256) {
   out_6404768134986181256[0] = state[7];
}
void H_26(double *state, double *unused, double *out_127584792264099562) {
   out_127584792264099562[0] = 0;
   out_127584792264099562[1] = 0;
   out_127584792264099562[2] = 0;
   out_127584792264099562[3] = 0;
   out_127584792264099562[4] = 0;
   out_127584792264099562[5] = 0;
   out_127584792264099562[6] = 0;
   out_127584792264099562[7] = 1;
   out_127584792264099562[8] = 0;
}
void h_27(double *state, double *unused, double *out_1212977297613836214) {
   out_1212977297613836214[0] = state[3];
}
void H_27(double *state, double *unused, double *out_8355845556301148506) {
   out_8355845556301148506[0] = 0;
   out_8355845556301148506[1] = 0;
   out_8355845556301148506[2] = 0;
   out_8355845556301148506[3] = 1;
   out_8355845556301148506[4] = 0;
   out_8355845556301148506[5] = 0;
   out_8355845556301148506[6] = 0;
   out_8355845556301148506[7] = 0;
   out_8355845556301148506[8] = 0;
}
void h_29(double *state, double *unused, double *out_2424472230640186136) {
   out_2424472230640186136[0] = state[1];
}
void H_29(double *state, double *unused, double *out_6642482829431597473) {
   out_6642482829431597473[0] = 0;
   out_6642482829431597473[1] = 1;
   out_6642482829431597473[2] = 0;
   out_6642482829431597473[3] = 0;
   out_6642482829431597473[4] = 0;
   out_6642482829431597473[5] = 0;
   out_6642482829431597473[6] = 0;
   out_6642482829431597473[7] = 0;
   out_6642482829431597473[8] = 0;
}
void h_28(double *state, double *unused, double *out_2752594053032157764) {
   out_2752594053032157764[0] = state[0];
}
void H_28(double *state, double *unused, double *out_1560083812362066899) {
   out_1560083812362066899[0] = 1;
   out_1560083812362066899[1] = 0;
   out_1560083812362066899[2] = 0;
   out_1560083812362066899[3] = 0;
   out_1560083812362066899[4] = 0;
   out_1560083812362066899[5] = 0;
   out_1560083812362066899[6] = 0;
   out_1560083812362066899[7] = 0;
   out_1560083812362066899[8] = 0;
}
void h_31(double *state, double *unused, double *out_1245908198974206466) {
   out_1245908198974206466[0] = state[8];
}
void H_31(double *state, double *unused, double *out_3644564488486917090) {
   out_3644564488486917090[0] = 0;
   out_3644564488486917090[1] = 0;
   out_3644564488486917090[2] = 0;
   out_3644564488486917090[3] = 0;
   out_3644564488486917090[4] = 0;
   out_3644564488486917090[5] = 0;
   out_3644564488486917090[6] = 0;
   out_3644564488486917090[7] = 0;
   out_3644564488486917090[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_8152243261381841861) {
  err_fun(nom_x, delta_x, out_8152243261381841861);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_1302168845595593824) {
  inv_err_fun(nom_x, true_x, out_1302168845595593824);
}
void car_H_mod_fun(double *state, double *out_720082183471150414) {
  H_mod_fun(state, out_720082183471150414);
}
void car_f_fun(double *state, double dt, double *out_1005905684588084232) {
  f_fun(state,  dt, out_1005905684588084232);
}
void car_F_fun(double *state, double dt, double *out_8578060064959244144) {
  F_fun(state,  dt, out_8578060064959244144);
}
void car_h_25(double *state, double *unused, double *out_5524927027376144470) {
  h_25(state, unused, out_5524927027376144470);
}
void car_H_25(double *state, double *unused, double *out_3613918526609956662) {
  H_25(state, unused, out_3613918526609956662);
}
void car_h_24(double *state, double *unused, double *out_2463198998502258202) {
  h_24(state, unused, out_2463198998502258202);
}
void car_H_24(double *state, double *unused, double *out_8257253740508076853) {
  H_24(state, unused, out_8257253740508076853);
}
void car_h_30(double *state, double *unused, double *out_2577201037020659509) {
  h_30(state, unused, out_2577201037020659509);
}
void car_H_30(double *state, double *unused, double *out_6132251485117205289) {
  H_30(state, unused, out_6132251485117205289);
}
void car_h_26(double *state, double *unused, double *out_6404768134986181256) {
  h_26(state, unused, out_6404768134986181256);
}
void car_H_26(double *state, double *unused, double *out_127584792264099562) {
  H_26(state, unused, out_127584792264099562);
}
void car_h_27(double *state, double *unused, double *out_1212977297613836214) {
  h_27(state, unused, out_1212977297613836214);
}
void car_H_27(double *state, double *unused, double *out_8355845556301148506) {
  H_27(state, unused, out_8355845556301148506);
}
void car_h_29(double *state, double *unused, double *out_2424472230640186136) {
  h_29(state, unused, out_2424472230640186136);
}
void car_H_29(double *state, double *unused, double *out_6642482829431597473) {
  H_29(state, unused, out_6642482829431597473);
}
void car_h_28(double *state, double *unused, double *out_2752594053032157764) {
  h_28(state, unused, out_2752594053032157764);
}
void car_H_28(double *state, double *unused, double *out_1560083812362066899) {
  H_28(state, unused, out_1560083812362066899);
}
void car_h_31(double *state, double *unused, double *out_1245908198974206466) {
  h_31(state, unused, out_1245908198974206466);
}
void car_H_31(double *state, double *unused, double *out_3644564488486917090) {
  H_31(state, unused, out_3644564488486917090);
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
