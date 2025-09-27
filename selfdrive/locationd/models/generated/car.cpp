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
void err_fun(double *nom_x, double *delta_x, double *out_616676496519843540) {
   out_616676496519843540[0] = delta_x[0] + nom_x[0];
   out_616676496519843540[1] = delta_x[1] + nom_x[1];
   out_616676496519843540[2] = delta_x[2] + nom_x[2];
   out_616676496519843540[3] = delta_x[3] + nom_x[3];
   out_616676496519843540[4] = delta_x[4] + nom_x[4];
   out_616676496519843540[5] = delta_x[5] + nom_x[5];
   out_616676496519843540[6] = delta_x[6] + nom_x[6];
   out_616676496519843540[7] = delta_x[7] + nom_x[7];
   out_616676496519843540[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_9159640380644645045) {
   out_9159640380644645045[0] = -nom_x[0] + true_x[0];
   out_9159640380644645045[1] = -nom_x[1] + true_x[1];
   out_9159640380644645045[2] = -nom_x[2] + true_x[2];
   out_9159640380644645045[3] = -nom_x[3] + true_x[3];
   out_9159640380644645045[4] = -nom_x[4] + true_x[4];
   out_9159640380644645045[5] = -nom_x[5] + true_x[5];
   out_9159640380644645045[6] = -nom_x[6] + true_x[6];
   out_9159640380644645045[7] = -nom_x[7] + true_x[7];
   out_9159640380644645045[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_3329662807632018400) {
   out_3329662807632018400[0] = 1.0;
   out_3329662807632018400[1] = 0.0;
   out_3329662807632018400[2] = 0.0;
   out_3329662807632018400[3] = 0.0;
   out_3329662807632018400[4] = 0.0;
   out_3329662807632018400[5] = 0.0;
   out_3329662807632018400[6] = 0.0;
   out_3329662807632018400[7] = 0.0;
   out_3329662807632018400[8] = 0.0;
   out_3329662807632018400[9] = 0.0;
   out_3329662807632018400[10] = 1.0;
   out_3329662807632018400[11] = 0.0;
   out_3329662807632018400[12] = 0.0;
   out_3329662807632018400[13] = 0.0;
   out_3329662807632018400[14] = 0.0;
   out_3329662807632018400[15] = 0.0;
   out_3329662807632018400[16] = 0.0;
   out_3329662807632018400[17] = 0.0;
   out_3329662807632018400[18] = 0.0;
   out_3329662807632018400[19] = 0.0;
   out_3329662807632018400[20] = 1.0;
   out_3329662807632018400[21] = 0.0;
   out_3329662807632018400[22] = 0.0;
   out_3329662807632018400[23] = 0.0;
   out_3329662807632018400[24] = 0.0;
   out_3329662807632018400[25] = 0.0;
   out_3329662807632018400[26] = 0.0;
   out_3329662807632018400[27] = 0.0;
   out_3329662807632018400[28] = 0.0;
   out_3329662807632018400[29] = 0.0;
   out_3329662807632018400[30] = 1.0;
   out_3329662807632018400[31] = 0.0;
   out_3329662807632018400[32] = 0.0;
   out_3329662807632018400[33] = 0.0;
   out_3329662807632018400[34] = 0.0;
   out_3329662807632018400[35] = 0.0;
   out_3329662807632018400[36] = 0.0;
   out_3329662807632018400[37] = 0.0;
   out_3329662807632018400[38] = 0.0;
   out_3329662807632018400[39] = 0.0;
   out_3329662807632018400[40] = 1.0;
   out_3329662807632018400[41] = 0.0;
   out_3329662807632018400[42] = 0.0;
   out_3329662807632018400[43] = 0.0;
   out_3329662807632018400[44] = 0.0;
   out_3329662807632018400[45] = 0.0;
   out_3329662807632018400[46] = 0.0;
   out_3329662807632018400[47] = 0.0;
   out_3329662807632018400[48] = 0.0;
   out_3329662807632018400[49] = 0.0;
   out_3329662807632018400[50] = 1.0;
   out_3329662807632018400[51] = 0.0;
   out_3329662807632018400[52] = 0.0;
   out_3329662807632018400[53] = 0.0;
   out_3329662807632018400[54] = 0.0;
   out_3329662807632018400[55] = 0.0;
   out_3329662807632018400[56] = 0.0;
   out_3329662807632018400[57] = 0.0;
   out_3329662807632018400[58] = 0.0;
   out_3329662807632018400[59] = 0.0;
   out_3329662807632018400[60] = 1.0;
   out_3329662807632018400[61] = 0.0;
   out_3329662807632018400[62] = 0.0;
   out_3329662807632018400[63] = 0.0;
   out_3329662807632018400[64] = 0.0;
   out_3329662807632018400[65] = 0.0;
   out_3329662807632018400[66] = 0.0;
   out_3329662807632018400[67] = 0.0;
   out_3329662807632018400[68] = 0.0;
   out_3329662807632018400[69] = 0.0;
   out_3329662807632018400[70] = 1.0;
   out_3329662807632018400[71] = 0.0;
   out_3329662807632018400[72] = 0.0;
   out_3329662807632018400[73] = 0.0;
   out_3329662807632018400[74] = 0.0;
   out_3329662807632018400[75] = 0.0;
   out_3329662807632018400[76] = 0.0;
   out_3329662807632018400[77] = 0.0;
   out_3329662807632018400[78] = 0.0;
   out_3329662807632018400[79] = 0.0;
   out_3329662807632018400[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_3004432371693856628) {
   out_3004432371693856628[0] = state[0];
   out_3004432371693856628[1] = state[1];
   out_3004432371693856628[2] = state[2];
   out_3004432371693856628[3] = state[3];
   out_3004432371693856628[4] = state[4];
   out_3004432371693856628[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8100000000000005*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_3004432371693856628[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_3004432371693856628[7] = state[7];
   out_3004432371693856628[8] = state[8];
}
void F_fun(double *state, double dt, double *out_4674607950146575611) {
   out_4674607950146575611[0] = 1;
   out_4674607950146575611[1] = 0;
   out_4674607950146575611[2] = 0;
   out_4674607950146575611[3] = 0;
   out_4674607950146575611[4] = 0;
   out_4674607950146575611[5] = 0;
   out_4674607950146575611[6] = 0;
   out_4674607950146575611[7] = 0;
   out_4674607950146575611[8] = 0;
   out_4674607950146575611[9] = 0;
   out_4674607950146575611[10] = 1;
   out_4674607950146575611[11] = 0;
   out_4674607950146575611[12] = 0;
   out_4674607950146575611[13] = 0;
   out_4674607950146575611[14] = 0;
   out_4674607950146575611[15] = 0;
   out_4674607950146575611[16] = 0;
   out_4674607950146575611[17] = 0;
   out_4674607950146575611[18] = 0;
   out_4674607950146575611[19] = 0;
   out_4674607950146575611[20] = 1;
   out_4674607950146575611[21] = 0;
   out_4674607950146575611[22] = 0;
   out_4674607950146575611[23] = 0;
   out_4674607950146575611[24] = 0;
   out_4674607950146575611[25] = 0;
   out_4674607950146575611[26] = 0;
   out_4674607950146575611[27] = 0;
   out_4674607950146575611[28] = 0;
   out_4674607950146575611[29] = 0;
   out_4674607950146575611[30] = 1;
   out_4674607950146575611[31] = 0;
   out_4674607950146575611[32] = 0;
   out_4674607950146575611[33] = 0;
   out_4674607950146575611[34] = 0;
   out_4674607950146575611[35] = 0;
   out_4674607950146575611[36] = 0;
   out_4674607950146575611[37] = 0;
   out_4674607950146575611[38] = 0;
   out_4674607950146575611[39] = 0;
   out_4674607950146575611[40] = 1;
   out_4674607950146575611[41] = 0;
   out_4674607950146575611[42] = 0;
   out_4674607950146575611[43] = 0;
   out_4674607950146575611[44] = 0;
   out_4674607950146575611[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_4674607950146575611[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_4674607950146575611[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_4674607950146575611[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_4674607950146575611[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_4674607950146575611[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_4674607950146575611[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_4674607950146575611[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_4674607950146575611[53] = -9.8100000000000005*dt;
   out_4674607950146575611[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_4674607950146575611[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_4674607950146575611[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_4674607950146575611[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_4674607950146575611[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_4674607950146575611[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_4674607950146575611[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_4674607950146575611[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_4674607950146575611[62] = 0;
   out_4674607950146575611[63] = 0;
   out_4674607950146575611[64] = 0;
   out_4674607950146575611[65] = 0;
   out_4674607950146575611[66] = 0;
   out_4674607950146575611[67] = 0;
   out_4674607950146575611[68] = 0;
   out_4674607950146575611[69] = 0;
   out_4674607950146575611[70] = 1;
   out_4674607950146575611[71] = 0;
   out_4674607950146575611[72] = 0;
   out_4674607950146575611[73] = 0;
   out_4674607950146575611[74] = 0;
   out_4674607950146575611[75] = 0;
   out_4674607950146575611[76] = 0;
   out_4674607950146575611[77] = 0;
   out_4674607950146575611[78] = 0;
   out_4674607950146575611[79] = 0;
   out_4674607950146575611[80] = 1;
}
void h_25(double *state, double *unused, double *out_7961708134929802500) {
   out_7961708134929802500[0] = state[6];
}
void H_25(double *state, double *unused, double *out_7390534805731274448) {
   out_7390534805731274448[0] = 0;
   out_7390534805731274448[1] = 0;
   out_7390534805731274448[2] = 0;
   out_7390534805731274448[3] = 0;
   out_7390534805731274448[4] = 0;
   out_7390534805731274448[5] = 0;
   out_7390534805731274448[6] = 1;
   out_7390534805731274448[7] = 0;
   out_7390534805731274448[8] = 0;
}
void h_24(double *state, double *unused, double *out_6293551899498467220) {
   out_6293551899498467220[0] = state[4];
   out_6293551899498467220[1] = state[5];
}
void H_24(double *state, double *unused, double *out_3637817634301350275) {
   out_3637817634301350275[0] = 0;
   out_3637817634301350275[1] = 0;
   out_3637817634301350275[2] = 0;
   out_3637817634301350275[3] = 0;
   out_3637817634301350275[4] = 1;
   out_3637817634301350275[5] = 0;
   out_3637817634301350275[6] = 0;
   out_3637817634301350275[7] = 0;
   out_3637817634301350275[8] = 0;
   out_3637817634301350275[9] = 0;
   out_3637817634301350275[10] = 0;
   out_3637817634301350275[11] = 0;
   out_3637817634301350275[12] = 0;
   out_3637817634301350275[13] = 0;
   out_3637817634301350275[14] = 1;
   out_3637817634301350275[15] = 0;
   out_3637817634301350275[16] = 0;
   out_3637817634301350275[17] = 0;
}
void h_30(double *state, double *unused, double *out_6847586410525726766) {
   out_6847586410525726766[0] = state[4];
}
void H_30(double *state, double *unused, double *out_2862838475603666250) {
   out_2862838475603666250[0] = 0;
   out_2862838475603666250[1] = 0;
   out_2862838475603666250[2] = 0;
   out_2862838475603666250[3] = 0;
   out_2862838475603666250[4] = 1;
   out_2862838475603666250[5] = 0;
   out_2862838475603666250[6] = 0;
   out_2862838475603666250[7] = 0;
   out_2862838475603666250[8] = 0;
}
void h_26(double *state, double *unused, double *out_6597484395522979205) {
   out_6597484395522979205[0] = state[7];
}
void H_26(double *state, double *unused, double *out_3649031486857218224) {
   out_3649031486857218224[0] = 0;
   out_3649031486857218224[1] = 0;
   out_3649031486857218224[2] = 0;
   out_3649031486857218224[3] = 0;
   out_3649031486857218224[4] = 0;
   out_3649031486857218224[5] = 0;
   out_3649031486857218224[6] = 0;
   out_3649031486857218224[7] = 1;
   out_3649031486857218224[8] = 0;
}
void h_27(double *state, double *unused, double *out_1767199018911056790) {
   out_1767199018911056790[0] = state[3];
}
void H_27(double *state, double *unused, double *out_5086432546787609467) {
   out_5086432546787609467[0] = 0;
   out_5086432546787609467[1] = 0;
   out_5086432546787609467[2] = 0;
   out_5086432546787609467[3] = 1;
   out_5086432546787609467[4] = 0;
   out_5086432546787609467[5] = 0;
   out_5086432546787609467[6] = 0;
   out_5086432546787609467[7] = 0;
   out_5086432546787609467[8] = 0;
}
void h_29(double *state, double *unused, double *out_1845913142864881121) {
   out_1845913142864881121[0] = state[1];
}
void H_29(double *state, double *unused, double *out_3373069819918058434) {
   out_3373069819918058434[0] = 0;
   out_3373069819918058434[1] = 1;
   out_3373069819918058434[2] = 0;
   out_3373069819918058434[3] = 0;
   out_3373069819918058434[4] = 0;
   out_3373069819918058434[5] = 0;
   out_3373069819918058434[6] = 0;
   out_3373069819918058434[7] = 0;
   out_3373069819918058434[8] = 0;
}
void h_28(double *state, double *unused, double *out_416945152400560748) {
   out_416945152400560748[0] = state[0];
}
void H_28(double *state, double *unused, double *out_5336700091483384685) {
   out_5336700091483384685[0] = 1;
   out_5336700091483384685[1] = 0;
   out_5336700091483384685[2] = 0;
   out_5336700091483384685[3] = 0;
   out_5336700091483384685[4] = 0;
   out_5336700091483384685[5] = 0;
   out_5336700091483384685[6] = 0;
   out_5336700091483384685[7] = 0;
   out_5336700091483384685[8] = 0;
}
void h_31(double *state, double *unused, double *out_770159022074290704) {
   out_770159022074290704[0] = state[8];
}
void H_31(double *state, double *unused, double *out_3022823384623866748) {
   out_3022823384623866748[0] = 0;
   out_3022823384623866748[1] = 0;
   out_3022823384623866748[2] = 0;
   out_3022823384623866748[3] = 0;
   out_3022823384623866748[4] = 0;
   out_3022823384623866748[5] = 0;
   out_3022823384623866748[6] = 0;
   out_3022823384623866748[7] = 0;
   out_3022823384623866748[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_616676496519843540) {
  err_fun(nom_x, delta_x, out_616676496519843540);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_9159640380644645045) {
  inv_err_fun(nom_x, true_x, out_9159640380644645045);
}
void car_H_mod_fun(double *state, double *out_3329662807632018400) {
  H_mod_fun(state, out_3329662807632018400);
}
void car_f_fun(double *state, double dt, double *out_3004432371693856628) {
  f_fun(state,  dt, out_3004432371693856628);
}
void car_F_fun(double *state, double dt, double *out_4674607950146575611) {
  F_fun(state,  dt, out_4674607950146575611);
}
void car_h_25(double *state, double *unused, double *out_7961708134929802500) {
  h_25(state, unused, out_7961708134929802500);
}
void car_H_25(double *state, double *unused, double *out_7390534805731274448) {
  H_25(state, unused, out_7390534805731274448);
}
void car_h_24(double *state, double *unused, double *out_6293551899498467220) {
  h_24(state, unused, out_6293551899498467220);
}
void car_H_24(double *state, double *unused, double *out_3637817634301350275) {
  H_24(state, unused, out_3637817634301350275);
}
void car_h_30(double *state, double *unused, double *out_6847586410525726766) {
  h_30(state, unused, out_6847586410525726766);
}
void car_H_30(double *state, double *unused, double *out_2862838475603666250) {
  H_30(state, unused, out_2862838475603666250);
}
void car_h_26(double *state, double *unused, double *out_6597484395522979205) {
  h_26(state, unused, out_6597484395522979205);
}
void car_H_26(double *state, double *unused, double *out_3649031486857218224) {
  H_26(state, unused, out_3649031486857218224);
}
void car_h_27(double *state, double *unused, double *out_1767199018911056790) {
  h_27(state, unused, out_1767199018911056790);
}
void car_H_27(double *state, double *unused, double *out_5086432546787609467) {
  H_27(state, unused, out_5086432546787609467);
}
void car_h_29(double *state, double *unused, double *out_1845913142864881121) {
  h_29(state, unused, out_1845913142864881121);
}
void car_H_29(double *state, double *unused, double *out_3373069819918058434) {
  H_29(state, unused, out_3373069819918058434);
}
void car_h_28(double *state, double *unused, double *out_416945152400560748) {
  h_28(state, unused, out_416945152400560748);
}
void car_H_28(double *state, double *unused, double *out_5336700091483384685) {
  H_28(state, unused, out_5336700091483384685);
}
void car_h_31(double *state, double *unused, double *out_770159022074290704) {
  h_31(state, unused, out_770159022074290704);
}
void car_H_31(double *state, double *unused, double *out_3022823384623866748) {
  H_31(state, unused, out_3022823384623866748);
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
