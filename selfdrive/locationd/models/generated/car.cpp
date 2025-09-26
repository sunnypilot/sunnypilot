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
void err_fun(double *nom_x, double *delta_x, double *out_853408928340835901) {
   out_853408928340835901[0] = delta_x[0] + nom_x[0];
   out_853408928340835901[1] = delta_x[1] + nom_x[1];
   out_853408928340835901[2] = delta_x[2] + nom_x[2];
   out_853408928340835901[3] = delta_x[3] + nom_x[3];
   out_853408928340835901[4] = delta_x[4] + nom_x[4];
   out_853408928340835901[5] = delta_x[5] + nom_x[5];
   out_853408928340835901[6] = delta_x[6] + nom_x[6];
   out_853408928340835901[7] = delta_x[7] + nom_x[7];
   out_853408928340835901[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_7742796402997516638) {
   out_7742796402997516638[0] = -nom_x[0] + true_x[0];
   out_7742796402997516638[1] = -nom_x[1] + true_x[1];
   out_7742796402997516638[2] = -nom_x[2] + true_x[2];
   out_7742796402997516638[3] = -nom_x[3] + true_x[3];
   out_7742796402997516638[4] = -nom_x[4] + true_x[4];
   out_7742796402997516638[5] = -nom_x[5] + true_x[5];
   out_7742796402997516638[6] = -nom_x[6] + true_x[6];
   out_7742796402997516638[7] = -nom_x[7] + true_x[7];
   out_7742796402997516638[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_6309495207021630516) {
   out_6309495207021630516[0] = 1.0;
   out_6309495207021630516[1] = 0.0;
   out_6309495207021630516[2] = 0.0;
   out_6309495207021630516[3] = 0.0;
   out_6309495207021630516[4] = 0.0;
   out_6309495207021630516[5] = 0.0;
   out_6309495207021630516[6] = 0.0;
   out_6309495207021630516[7] = 0.0;
   out_6309495207021630516[8] = 0.0;
   out_6309495207021630516[9] = 0.0;
   out_6309495207021630516[10] = 1.0;
   out_6309495207021630516[11] = 0.0;
   out_6309495207021630516[12] = 0.0;
   out_6309495207021630516[13] = 0.0;
   out_6309495207021630516[14] = 0.0;
   out_6309495207021630516[15] = 0.0;
   out_6309495207021630516[16] = 0.0;
   out_6309495207021630516[17] = 0.0;
   out_6309495207021630516[18] = 0.0;
   out_6309495207021630516[19] = 0.0;
   out_6309495207021630516[20] = 1.0;
   out_6309495207021630516[21] = 0.0;
   out_6309495207021630516[22] = 0.0;
   out_6309495207021630516[23] = 0.0;
   out_6309495207021630516[24] = 0.0;
   out_6309495207021630516[25] = 0.0;
   out_6309495207021630516[26] = 0.0;
   out_6309495207021630516[27] = 0.0;
   out_6309495207021630516[28] = 0.0;
   out_6309495207021630516[29] = 0.0;
   out_6309495207021630516[30] = 1.0;
   out_6309495207021630516[31] = 0.0;
   out_6309495207021630516[32] = 0.0;
   out_6309495207021630516[33] = 0.0;
   out_6309495207021630516[34] = 0.0;
   out_6309495207021630516[35] = 0.0;
   out_6309495207021630516[36] = 0.0;
   out_6309495207021630516[37] = 0.0;
   out_6309495207021630516[38] = 0.0;
   out_6309495207021630516[39] = 0.0;
   out_6309495207021630516[40] = 1.0;
   out_6309495207021630516[41] = 0.0;
   out_6309495207021630516[42] = 0.0;
   out_6309495207021630516[43] = 0.0;
   out_6309495207021630516[44] = 0.0;
   out_6309495207021630516[45] = 0.0;
   out_6309495207021630516[46] = 0.0;
   out_6309495207021630516[47] = 0.0;
   out_6309495207021630516[48] = 0.0;
   out_6309495207021630516[49] = 0.0;
   out_6309495207021630516[50] = 1.0;
   out_6309495207021630516[51] = 0.0;
   out_6309495207021630516[52] = 0.0;
   out_6309495207021630516[53] = 0.0;
   out_6309495207021630516[54] = 0.0;
   out_6309495207021630516[55] = 0.0;
   out_6309495207021630516[56] = 0.0;
   out_6309495207021630516[57] = 0.0;
   out_6309495207021630516[58] = 0.0;
   out_6309495207021630516[59] = 0.0;
   out_6309495207021630516[60] = 1.0;
   out_6309495207021630516[61] = 0.0;
   out_6309495207021630516[62] = 0.0;
   out_6309495207021630516[63] = 0.0;
   out_6309495207021630516[64] = 0.0;
   out_6309495207021630516[65] = 0.0;
   out_6309495207021630516[66] = 0.0;
   out_6309495207021630516[67] = 0.0;
   out_6309495207021630516[68] = 0.0;
   out_6309495207021630516[69] = 0.0;
   out_6309495207021630516[70] = 1.0;
   out_6309495207021630516[71] = 0.0;
   out_6309495207021630516[72] = 0.0;
   out_6309495207021630516[73] = 0.0;
   out_6309495207021630516[74] = 0.0;
   out_6309495207021630516[75] = 0.0;
   out_6309495207021630516[76] = 0.0;
   out_6309495207021630516[77] = 0.0;
   out_6309495207021630516[78] = 0.0;
   out_6309495207021630516[79] = 0.0;
   out_6309495207021630516[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_514567004980479814) {
   out_514567004980479814[0] = state[0];
   out_514567004980479814[1] = state[1];
   out_514567004980479814[2] = state[2];
   out_514567004980479814[3] = state[3];
   out_514567004980479814[4] = state[4];
   out_514567004980479814[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8100000000000005*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_514567004980479814[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_514567004980479814[7] = state[7];
   out_514567004980479814[8] = state[8];
}
void F_fun(double *state, double dt, double *out_5656357106442317914) {
   out_5656357106442317914[0] = 1;
   out_5656357106442317914[1] = 0;
   out_5656357106442317914[2] = 0;
   out_5656357106442317914[3] = 0;
   out_5656357106442317914[4] = 0;
   out_5656357106442317914[5] = 0;
   out_5656357106442317914[6] = 0;
   out_5656357106442317914[7] = 0;
   out_5656357106442317914[8] = 0;
   out_5656357106442317914[9] = 0;
   out_5656357106442317914[10] = 1;
   out_5656357106442317914[11] = 0;
   out_5656357106442317914[12] = 0;
   out_5656357106442317914[13] = 0;
   out_5656357106442317914[14] = 0;
   out_5656357106442317914[15] = 0;
   out_5656357106442317914[16] = 0;
   out_5656357106442317914[17] = 0;
   out_5656357106442317914[18] = 0;
   out_5656357106442317914[19] = 0;
   out_5656357106442317914[20] = 1;
   out_5656357106442317914[21] = 0;
   out_5656357106442317914[22] = 0;
   out_5656357106442317914[23] = 0;
   out_5656357106442317914[24] = 0;
   out_5656357106442317914[25] = 0;
   out_5656357106442317914[26] = 0;
   out_5656357106442317914[27] = 0;
   out_5656357106442317914[28] = 0;
   out_5656357106442317914[29] = 0;
   out_5656357106442317914[30] = 1;
   out_5656357106442317914[31] = 0;
   out_5656357106442317914[32] = 0;
   out_5656357106442317914[33] = 0;
   out_5656357106442317914[34] = 0;
   out_5656357106442317914[35] = 0;
   out_5656357106442317914[36] = 0;
   out_5656357106442317914[37] = 0;
   out_5656357106442317914[38] = 0;
   out_5656357106442317914[39] = 0;
   out_5656357106442317914[40] = 1;
   out_5656357106442317914[41] = 0;
   out_5656357106442317914[42] = 0;
   out_5656357106442317914[43] = 0;
   out_5656357106442317914[44] = 0;
   out_5656357106442317914[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_5656357106442317914[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_5656357106442317914[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_5656357106442317914[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_5656357106442317914[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_5656357106442317914[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_5656357106442317914[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_5656357106442317914[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_5656357106442317914[53] = -9.8100000000000005*dt;
   out_5656357106442317914[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_5656357106442317914[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_5656357106442317914[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_5656357106442317914[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_5656357106442317914[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_5656357106442317914[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_5656357106442317914[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_5656357106442317914[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_5656357106442317914[62] = 0;
   out_5656357106442317914[63] = 0;
   out_5656357106442317914[64] = 0;
   out_5656357106442317914[65] = 0;
   out_5656357106442317914[66] = 0;
   out_5656357106442317914[67] = 0;
   out_5656357106442317914[68] = 0;
   out_5656357106442317914[69] = 0;
   out_5656357106442317914[70] = 1;
   out_5656357106442317914[71] = 0;
   out_5656357106442317914[72] = 0;
   out_5656357106442317914[73] = 0;
   out_5656357106442317914[74] = 0;
   out_5656357106442317914[75] = 0;
   out_5656357106442317914[76] = 0;
   out_5656357106442317914[77] = 0;
   out_5656357106442317914[78] = 0;
   out_5656357106442317914[79] = 0;
   out_5656357106442317914[80] = 1;
}
void h_25(double *state, double *unused, double *out_5718536217680117524) {
   out_5718536217680117524[0] = state[6];
}
void H_25(double *state, double *unused, double *out_1405803381836965676) {
   out_1405803381836965676[0] = 0;
   out_1405803381836965676[1] = 0;
   out_1405803381836965676[2] = 0;
   out_1405803381836965676[3] = 0;
   out_1405803381836965676[4] = 0;
   out_1405803381836965676[5] = 0;
   out_1405803381836965676[6] = 1;
   out_1405803381836965676[7] = 0;
   out_1405803381836965676[8] = 0;
}
void h_24(double *state, double *unused, double *out_5378089274505107240) {
   out_5378089274505107240[0] = state[4];
   out_5378089274505107240[1] = state[5];
}
void H_24(double *state, double *unused, double *out_1876260863880304400) {
   out_1876260863880304400[0] = 0;
   out_1876260863880304400[1] = 0;
   out_1876260863880304400[2] = 0;
   out_1876260863880304400[3] = 0;
   out_1876260863880304400[4] = 1;
   out_1876260863880304400[5] = 0;
   out_1876260863880304400[6] = 0;
   out_1876260863880304400[7] = 0;
   out_1876260863880304400[8] = 0;
   out_1876260863880304400[9] = 0;
   out_1876260863880304400[10] = 0;
   out_1876260863880304400[11] = 0;
   out_1876260863880304400[12] = 0;
   out_1876260863880304400[13] = 0;
   out_1876260863880304400[14] = 1;
   out_1876260863880304400[15] = 0;
   out_1876260863880304400[16] = 0;
   out_1876260863880304400[17] = 0;
}
void h_30(double *state, double *unused, double *out_2044729039140554917) {
   out_2044729039140554917[0] = state[4];
}
void H_30(double *state, double *unused, double *out_1535142328980205746) {
   out_1535142328980205746[0] = 0;
   out_1535142328980205746[1] = 0;
   out_1535142328980205746[2] = 0;
   out_1535142328980205746[3] = 0;
   out_1535142328980205746[4] = 1;
   out_1535142328980205746[5] = 0;
   out_1535142328980205746[6] = 0;
   out_1535142328980205746[7] = 0;
   out_1535142328980205746[8] = 0;
}
void h_26(double *state, double *unused, double *out_992057012303777768) {
   out_992057012303777768[0] = state[7];
}
void H_26(double *state, double *unused, double *out_5147306700711021900) {
   out_5147306700711021900[0] = 0;
   out_5147306700711021900[1] = 0;
   out_5147306700711021900[2] = 0;
   out_5147306700711021900[3] = 0;
   out_5147306700711021900[4] = 0;
   out_5147306700711021900[5] = 0;
   out_5147306700711021900[6] = 0;
   out_5147306700711021900[7] = 1;
   out_5147306700711021900[8] = 0;
}
void h_27(double *state, double *unused, double *out_5935964882397702313) {
   out_5935964882397702313[0] = state[3];
}
void H_27(double *state, double *unused, double *out_3709905640780630657) {
   out_3709905640780630657[0] = 0;
   out_3709905640780630657[1] = 0;
   out_3709905640780630657[2] = 0;
   out_3709905640780630657[3] = 1;
   out_3709905640780630657[4] = 0;
   out_3709905640780630657[5] = 0;
   out_3709905640780630657[6] = 0;
   out_3709905640780630657[7] = 0;
   out_3709905640780630657[8] = 0;
}
void h_29(double *state, double *unused, double *out_3870901714593307419) {
   out_3870901714593307419[0] = state[1];
}
void H_29(double *state, double *unused, double *out_1024910984665813562) {
   out_1024910984665813562[0] = 0;
   out_1024910984665813562[1] = 1;
   out_1024910984665813562[2] = 0;
   out_1024910984665813562[3] = 0;
   out_1024910984665813562[4] = 0;
   out_1024910984665813562[5] = 0;
   out_1024910984665813562[6] = 0;
   out_1024910984665813562[7] = 0;
   out_1024910984665813562[8] = 0;
}
void h_28(double *state, double *unused, double *out_2660117069650245724) {
   out_2660117069650245724[0] = state[0];
}
void H_28(double *state, double *unused, double *out_3459638096084855439) {
   out_3459638096084855439[0] = 1;
   out_3459638096084855439[1] = 0;
   out_3459638096084855439[2] = 0;
   out_3459638096084855439[3] = 0;
   out_3459638096084855439[4] = 0;
   out_3459638096084855439[5] = 0;
   out_3459638096084855439[6] = 0;
   out_3459638096084855439[7] = 0;
   out_3459638096084855439[8] = 0;
}
void h_31(double *state, double *unused, double *out_8629904557750062228) {
   out_8629904557750062228[0] = state[8];
}
void H_31(double *state, double *unused, double *out_1375157419960005248) {
   out_1375157419960005248[0] = 0;
   out_1375157419960005248[1] = 0;
   out_1375157419960005248[2] = 0;
   out_1375157419960005248[3] = 0;
   out_1375157419960005248[4] = 0;
   out_1375157419960005248[5] = 0;
   out_1375157419960005248[6] = 0;
   out_1375157419960005248[7] = 0;
   out_1375157419960005248[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_853408928340835901) {
  err_fun(nom_x, delta_x, out_853408928340835901);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_7742796402997516638) {
  inv_err_fun(nom_x, true_x, out_7742796402997516638);
}
void car_H_mod_fun(double *state, double *out_6309495207021630516) {
  H_mod_fun(state, out_6309495207021630516);
}
void car_f_fun(double *state, double dt, double *out_514567004980479814) {
  f_fun(state,  dt, out_514567004980479814);
}
void car_F_fun(double *state, double dt, double *out_5656357106442317914) {
  F_fun(state,  dt, out_5656357106442317914);
}
void car_h_25(double *state, double *unused, double *out_5718536217680117524) {
  h_25(state, unused, out_5718536217680117524);
}
void car_H_25(double *state, double *unused, double *out_1405803381836965676) {
  H_25(state, unused, out_1405803381836965676);
}
void car_h_24(double *state, double *unused, double *out_5378089274505107240) {
  h_24(state, unused, out_5378089274505107240);
}
void car_H_24(double *state, double *unused, double *out_1876260863880304400) {
  H_24(state, unused, out_1876260863880304400);
}
void car_h_30(double *state, double *unused, double *out_2044729039140554917) {
  h_30(state, unused, out_2044729039140554917);
}
void car_H_30(double *state, double *unused, double *out_1535142328980205746) {
  H_30(state, unused, out_1535142328980205746);
}
void car_h_26(double *state, double *unused, double *out_992057012303777768) {
  h_26(state, unused, out_992057012303777768);
}
void car_H_26(double *state, double *unused, double *out_5147306700711021900) {
  H_26(state, unused, out_5147306700711021900);
}
void car_h_27(double *state, double *unused, double *out_5935964882397702313) {
  h_27(state, unused, out_5935964882397702313);
}
void car_H_27(double *state, double *unused, double *out_3709905640780630657) {
  H_27(state, unused, out_3709905640780630657);
}
void car_h_29(double *state, double *unused, double *out_3870901714593307419) {
  h_29(state, unused, out_3870901714593307419);
}
void car_H_29(double *state, double *unused, double *out_1024910984665813562) {
  H_29(state, unused, out_1024910984665813562);
}
void car_h_28(double *state, double *unused, double *out_2660117069650245724) {
  h_28(state, unused, out_2660117069650245724);
}
void car_H_28(double *state, double *unused, double *out_3459638096084855439) {
  H_28(state, unused, out_3459638096084855439);
}
void car_h_31(double *state, double *unused, double *out_8629904557750062228) {
  h_31(state, unused, out_8629904557750062228);
}
void car_H_31(double *state, double *unused, double *out_1375157419960005248) {
  H_31(state, unused, out_1375157419960005248);
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
