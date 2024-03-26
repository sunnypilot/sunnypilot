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
void err_fun(double *nom_x, double *delta_x, double *out_9210742210888155066) {
   out_9210742210888155066[0] = delta_x[0] + nom_x[0];
   out_9210742210888155066[1] = delta_x[1] + nom_x[1];
   out_9210742210888155066[2] = delta_x[2] + nom_x[2];
   out_9210742210888155066[3] = delta_x[3] + nom_x[3];
   out_9210742210888155066[4] = delta_x[4] + nom_x[4];
   out_9210742210888155066[5] = delta_x[5] + nom_x[5];
   out_9210742210888155066[6] = delta_x[6] + nom_x[6];
   out_9210742210888155066[7] = delta_x[7] + nom_x[7];
   out_9210742210888155066[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_3383382481161837801) {
   out_3383382481161837801[0] = -nom_x[0] + true_x[0];
   out_3383382481161837801[1] = -nom_x[1] + true_x[1];
   out_3383382481161837801[2] = -nom_x[2] + true_x[2];
   out_3383382481161837801[3] = -nom_x[3] + true_x[3];
   out_3383382481161837801[4] = -nom_x[4] + true_x[4];
   out_3383382481161837801[5] = -nom_x[5] + true_x[5];
   out_3383382481161837801[6] = -nom_x[6] + true_x[6];
   out_3383382481161837801[7] = -nom_x[7] + true_x[7];
   out_3383382481161837801[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_8527379894240690997) {
   out_8527379894240690997[0] = 1.0;
   out_8527379894240690997[1] = 0;
   out_8527379894240690997[2] = 0;
   out_8527379894240690997[3] = 0;
   out_8527379894240690997[4] = 0;
   out_8527379894240690997[5] = 0;
   out_8527379894240690997[6] = 0;
   out_8527379894240690997[7] = 0;
   out_8527379894240690997[8] = 0;
   out_8527379894240690997[9] = 0;
   out_8527379894240690997[10] = 1.0;
   out_8527379894240690997[11] = 0;
   out_8527379894240690997[12] = 0;
   out_8527379894240690997[13] = 0;
   out_8527379894240690997[14] = 0;
   out_8527379894240690997[15] = 0;
   out_8527379894240690997[16] = 0;
   out_8527379894240690997[17] = 0;
   out_8527379894240690997[18] = 0;
   out_8527379894240690997[19] = 0;
   out_8527379894240690997[20] = 1.0;
   out_8527379894240690997[21] = 0;
   out_8527379894240690997[22] = 0;
   out_8527379894240690997[23] = 0;
   out_8527379894240690997[24] = 0;
   out_8527379894240690997[25] = 0;
   out_8527379894240690997[26] = 0;
   out_8527379894240690997[27] = 0;
   out_8527379894240690997[28] = 0;
   out_8527379894240690997[29] = 0;
   out_8527379894240690997[30] = 1.0;
   out_8527379894240690997[31] = 0;
   out_8527379894240690997[32] = 0;
   out_8527379894240690997[33] = 0;
   out_8527379894240690997[34] = 0;
   out_8527379894240690997[35] = 0;
   out_8527379894240690997[36] = 0;
   out_8527379894240690997[37] = 0;
   out_8527379894240690997[38] = 0;
   out_8527379894240690997[39] = 0;
   out_8527379894240690997[40] = 1.0;
   out_8527379894240690997[41] = 0;
   out_8527379894240690997[42] = 0;
   out_8527379894240690997[43] = 0;
   out_8527379894240690997[44] = 0;
   out_8527379894240690997[45] = 0;
   out_8527379894240690997[46] = 0;
   out_8527379894240690997[47] = 0;
   out_8527379894240690997[48] = 0;
   out_8527379894240690997[49] = 0;
   out_8527379894240690997[50] = 1.0;
   out_8527379894240690997[51] = 0;
   out_8527379894240690997[52] = 0;
   out_8527379894240690997[53] = 0;
   out_8527379894240690997[54] = 0;
   out_8527379894240690997[55] = 0;
   out_8527379894240690997[56] = 0;
   out_8527379894240690997[57] = 0;
   out_8527379894240690997[58] = 0;
   out_8527379894240690997[59] = 0;
   out_8527379894240690997[60] = 1.0;
   out_8527379894240690997[61] = 0;
   out_8527379894240690997[62] = 0;
   out_8527379894240690997[63] = 0;
   out_8527379894240690997[64] = 0;
   out_8527379894240690997[65] = 0;
   out_8527379894240690997[66] = 0;
   out_8527379894240690997[67] = 0;
   out_8527379894240690997[68] = 0;
   out_8527379894240690997[69] = 0;
   out_8527379894240690997[70] = 1.0;
   out_8527379894240690997[71] = 0;
   out_8527379894240690997[72] = 0;
   out_8527379894240690997[73] = 0;
   out_8527379894240690997[74] = 0;
   out_8527379894240690997[75] = 0;
   out_8527379894240690997[76] = 0;
   out_8527379894240690997[77] = 0;
   out_8527379894240690997[78] = 0;
   out_8527379894240690997[79] = 0;
   out_8527379894240690997[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_161039606333012886) {
   out_161039606333012886[0] = state[0];
   out_161039606333012886[1] = state[1];
   out_161039606333012886[2] = state[2];
   out_161039606333012886[3] = state[3];
   out_161039606333012886[4] = state[4];
   out_161039606333012886[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8000000000000007*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_161039606333012886[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_161039606333012886[7] = state[7];
   out_161039606333012886[8] = state[8];
}
void F_fun(double *state, double dt, double *out_4115038986771892062) {
   out_4115038986771892062[0] = 1;
   out_4115038986771892062[1] = 0;
   out_4115038986771892062[2] = 0;
   out_4115038986771892062[3] = 0;
   out_4115038986771892062[4] = 0;
   out_4115038986771892062[5] = 0;
   out_4115038986771892062[6] = 0;
   out_4115038986771892062[7] = 0;
   out_4115038986771892062[8] = 0;
   out_4115038986771892062[9] = 0;
   out_4115038986771892062[10] = 1;
   out_4115038986771892062[11] = 0;
   out_4115038986771892062[12] = 0;
   out_4115038986771892062[13] = 0;
   out_4115038986771892062[14] = 0;
   out_4115038986771892062[15] = 0;
   out_4115038986771892062[16] = 0;
   out_4115038986771892062[17] = 0;
   out_4115038986771892062[18] = 0;
   out_4115038986771892062[19] = 0;
   out_4115038986771892062[20] = 1;
   out_4115038986771892062[21] = 0;
   out_4115038986771892062[22] = 0;
   out_4115038986771892062[23] = 0;
   out_4115038986771892062[24] = 0;
   out_4115038986771892062[25] = 0;
   out_4115038986771892062[26] = 0;
   out_4115038986771892062[27] = 0;
   out_4115038986771892062[28] = 0;
   out_4115038986771892062[29] = 0;
   out_4115038986771892062[30] = 1;
   out_4115038986771892062[31] = 0;
   out_4115038986771892062[32] = 0;
   out_4115038986771892062[33] = 0;
   out_4115038986771892062[34] = 0;
   out_4115038986771892062[35] = 0;
   out_4115038986771892062[36] = 0;
   out_4115038986771892062[37] = 0;
   out_4115038986771892062[38] = 0;
   out_4115038986771892062[39] = 0;
   out_4115038986771892062[40] = 1;
   out_4115038986771892062[41] = 0;
   out_4115038986771892062[42] = 0;
   out_4115038986771892062[43] = 0;
   out_4115038986771892062[44] = 0;
   out_4115038986771892062[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_4115038986771892062[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_4115038986771892062[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_4115038986771892062[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_4115038986771892062[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_4115038986771892062[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_4115038986771892062[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_4115038986771892062[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_4115038986771892062[53] = -9.8000000000000007*dt;
   out_4115038986771892062[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_4115038986771892062[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_4115038986771892062[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_4115038986771892062[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_4115038986771892062[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_4115038986771892062[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_4115038986771892062[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_4115038986771892062[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_4115038986771892062[62] = 0;
   out_4115038986771892062[63] = 0;
   out_4115038986771892062[64] = 0;
   out_4115038986771892062[65] = 0;
   out_4115038986771892062[66] = 0;
   out_4115038986771892062[67] = 0;
   out_4115038986771892062[68] = 0;
   out_4115038986771892062[69] = 0;
   out_4115038986771892062[70] = 1;
   out_4115038986771892062[71] = 0;
   out_4115038986771892062[72] = 0;
   out_4115038986771892062[73] = 0;
   out_4115038986771892062[74] = 0;
   out_4115038986771892062[75] = 0;
   out_4115038986771892062[76] = 0;
   out_4115038986771892062[77] = 0;
   out_4115038986771892062[78] = 0;
   out_4115038986771892062[79] = 0;
   out_4115038986771892062[80] = 1;
}
void h_25(double *state, double *unused, double *out_7382986880899433707) {
   out_7382986880899433707[0] = state[6];
}
void H_25(double *state, double *unused, double *out_2957978884612669829) {
   out_2957978884612669829[0] = 0;
   out_2957978884612669829[1] = 0;
   out_2957978884612669829[2] = 0;
   out_2957978884612669829[3] = 0;
   out_2957978884612669829[4] = 0;
   out_2957978884612669829[5] = 0;
   out_2957978884612669829[6] = 1;
   out_2957978884612669829[7] = 0;
   out_2957978884612669829[8] = 0;
}
void h_24(double *state, double *unused, double *out_8859429626558099191) {
   out_8859429626558099191[0] = state[4];
   out_8859429626558099191[1] = state[5];
}
void H_24(double *state, double *unused, double *out_599946714189653307) {
   out_599946714189653307[0] = 0;
   out_599946714189653307[1] = 0;
   out_599946714189653307[2] = 0;
   out_599946714189653307[3] = 0;
   out_599946714189653307[4] = 1;
   out_599946714189653307[5] = 0;
   out_599946714189653307[6] = 0;
   out_599946714189653307[7] = 0;
   out_599946714189653307[8] = 0;
   out_599946714189653307[9] = 0;
   out_599946714189653307[10] = 0;
   out_599946714189653307[11] = 0;
   out_599946714189653307[12] = 0;
   out_599946714189653307[13] = 0;
   out_599946714189653307[14] = 1;
   out_599946714189653307[15] = 0;
   out_599946714189653307[16] = 0;
   out_599946714189653307[17] = 0;
}
void h_30(double *state, double *unused, double *out_2423879716091576025) {
   out_2423879716091576025[0] = state[4];
}
void H_30(double *state, double *unused, double *out_439645926105421202) {
   out_439645926105421202[0] = 0;
   out_439645926105421202[1] = 0;
   out_439645926105421202[2] = 0;
   out_439645926105421202[3] = 0;
   out_439645926105421202[4] = 1;
   out_439645926105421202[5] = 0;
   out_439645926105421202[6] = 0;
   out_439645926105421202[7] = 0;
   out_439645926105421202[8] = 0;
}
void h_26(double *state, double *unused, double *out_2577793551569269620) {
   out_2577793551569269620[0] = state[7];
}
void H_26(double *state, double *unused, double *out_6699482203486726053) {
   out_6699482203486726053[0] = 0;
   out_6699482203486726053[1] = 0;
   out_6699482203486726053[2] = 0;
   out_6699482203486726053[3] = 0;
   out_6699482203486726053[4] = 0;
   out_6699482203486726053[5] = 0;
   out_6699482203486726053[6] = 0;
   out_6699482203486726053[7] = 1;
   out_6699482203486726053[8] = 0;
}
void h_27(double *state, double *unused, double *out_6400902787564135595) {
   out_6400902787564135595[0] = state[3];
}
void H_27(double *state, double *unused, double *out_1783948145078522015) {
   out_1783948145078522015[0] = 0;
   out_1783948145078522015[1] = 0;
   out_1783948145078522015[2] = 0;
   out_1783948145078522015[3] = 1;
   out_1783948145078522015[4] = 0;
   out_1783948145078522015[5] = 0;
   out_1783948145078522015[6] = 0;
   out_1783948145078522015[7] = 0;
   out_1783948145078522015[8] = 0;
}
void h_29(double *state, double *unused, double *out_1480369863189913590) {
   out_1480369863189913590[0] = state[1];
}
void H_29(double *state, double *unused, double *out_70585418208970982) {
   out_70585418208970982[0] = 0;
   out_70585418208970982[1] = 1;
   out_70585418208970982[2] = 0;
   out_70585418208970982[3] = 0;
   out_70585418208970982[4] = 0;
   out_70585418208970982[5] = 0;
   out_70585418208970982[6] = 0;
   out_70585418208970982[7] = 0;
   out_70585418208970982[8] = 0;
}
void h_28(double *state, double *unused, double *out_1399229519903289950) {
   out_1399229519903289950[0] = state[0];
}
void H_28(double *state, double *unused, double *out_5011813598860559592) {
   out_5011813598860559592[0] = 1;
   out_5011813598860559592[1] = 0;
   out_5011813598860559592[2] = 0;
   out_5011813598860559592[3] = 0;
   out_5011813598860559592[4] = 0;
   out_5011813598860559592[5] = 0;
   out_5011813598860559592[6] = 0;
   out_5011813598860559592[7] = 0;
   out_5011813598860559592[8] = 0;
}
void h_31(double *state, double *unused, double *out_7658180943183939596) {
   out_7658180943183939596[0] = state[8];
}
void H_31(double *state, double *unused, double *out_2927332922735709401) {
   out_2927332922735709401[0] = 0;
   out_2927332922735709401[1] = 0;
   out_2927332922735709401[2] = 0;
   out_2927332922735709401[3] = 0;
   out_2927332922735709401[4] = 0;
   out_2927332922735709401[5] = 0;
   out_2927332922735709401[6] = 0;
   out_2927332922735709401[7] = 0;
   out_2927332922735709401[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_9210742210888155066) {
  err_fun(nom_x, delta_x, out_9210742210888155066);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_3383382481161837801) {
  inv_err_fun(nom_x, true_x, out_3383382481161837801);
}
void car_H_mod_fun(double *state, double *out_8527379894240690997) {
  H_mod_fun(state, out_8527379894240690997);
}
void car_f_fun(double *state, double dt, double *out_161039606333012886) {
  f_fun(state,  dt, out_161039606333012886);
}
void car_F_fun(double *state, double dt, double *out_4115038986771892062) {
  F_fun(state,  dt, out_4115038986771892062);
}
void car_h_25(double *state, double *unused, double *out_7382986880899433707) {
  h_25(state, unused, out_7382986880899433707);
}
void car_H_25(double *state, double *unused, double *out_2957978884612669829) {
  H_25(state, unused, out_2957978884612669829);
}
void car_h_24(double *state, double *unused, double *out_8859429626558099191) {
  h_24(state, unused, out_8859429626558099191);
}
void car_H_24(double *state, double *unused, double *out_599946714189653307) {
  H_24(state, unused, out_599946714189653307);
}
void car_h_30(double *state, double *unused, double *out_2423879716091576025) {
  h_30(state, unused, out_2423879716091576025);
}
void car_H_30(double *state, double *unused, double *out_439645926105421202) {
  H_30(state, unused, out_439645926105421202);
}
void car_h_26(double *state, double *unused, double *out_2577793551569269620) {
  h_26(state, unused, out_2577793551569269620);
}
void car_H_26(double *state, double *unused, double *out_6699482203486726053) {
  H_26(state, unused, out_6699482203486726053);
}
void car_h_27(double *state, double *unused, double *out_6400902787564135595) {
  h_27(state, unused, out_6400902787564135595);
}
void car_H_27(double *state, double *unused, double *out_1783948145078522015) {
  H_27(state, unused, out_1783948145078522015);
}
void car_h_29(double *state, double *unused, double *out_1480369863189913590) {
  h_29(state, unused, out_1480369863189913590);
}
void car_H_29(double *state, double *unused, double *out_70585418208970982) {
  H_29(state, unused, out_70585418208970982);
}
void car_h_28(double *state, double *unused, double *out_1399229519903289950) {
  h_28(state, unused, out_1399229519903289950);
}
void car_H_28(double *state, double *unused, double *out_5011813598860559592) {
  H_28(state, unused, out_5011813598860559592);
}
void car_h_31(double *state, double *unused, double *out_7658180943183939596) {
  h_31(state, unused, out_7658180943183939596);
}
void car_H_31(double *state, double *unused, double *out_2927332922735709401) {
  H_31(state, unused, out_2927332922735709401);
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
