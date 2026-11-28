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
void err_fun(double *nom_x, double *delta_x, double *out_8852971544794429466) {
   out_8852971544794429466[0] = delta_x[0] + nom_x[0];
   out_8852971544794429466[1] = delta_x[1] + nom_x[1];
   out_8852971544794429466[2] = delta_x[2] + nom_x[2];
   out_8852971544794429466[3] = delta_x[3] + nom_x[3];
   out_8852971544794429466[4] = delta_x[4] + nom_x[4];
   out_8852971544794429466[5] = delta_x[5] + nom_x[5];
   out_8852971544794429466[6] = delta_x[6] + nom_x[6];
   out_8852971544794429466[7] = delta_x[7] + nom_x[7];
   out_8852971544794429466[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_5565710821617854915) {
   out_5565710821617854915[0] = -nom_x[0] + true_x[0];
   out_5565710821617854915[1] = -nom_x[1] + true_x[1];
   out_5565710821617854915[2] = -nom_x[2] + true_x[2];
   out_5565710821617854915[3] = -nom_x[3] + true_x[3];
   out_5565710821617854915[4] = -nom_x[4] + true_x[4];
   out_5565710821617854915[5] = -nom_x[5] + true_x[5];
   out_5565710821617854915[6] = -nom_x[6] + true_x[6];
   out_5565710821617854915[7] = -nom_x[7] + true_x[7];
   out_5565710821617854915[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_3163685400089475165) {
   out_3163685400089475165[0] = 1.0;
   out_3163685400089475165[1] = 0.0;
   out_3163685400089475165[2] = 0.0;
   out_3163685400089475165[3] = 0.0;
   out_3163685400089475165[4] = 0.0;
   out_3163685400089475165[5] = 0.0;
   out_3163685400089475165[6] = 0.0;
   out_3163685400089475165[7] = 0.0;
   out_3163685400089475165[8] = 0.0;
   out_3163685400089475165[9] = 0.0;
   out_3163685400089475165[10] = 1.0;
   out_3163685400089475165[11] = 0.0;
   out_3163685400089475165[12] = 0.0;
   out_3163685400089475165[13] = 0.0;
   out_3163685400089475165[14] = 0.0;
   out_3163685400089475165[15] = 0.0;
   out_3163685400089475165[16] = 0.0;
   out_3163685400089475165[17] = 0.0;
   out_3163685400089475165[18] = 0.0;
   out_3163685400089475165[19] = 0.0;
   out_3163685400089475165[20] = 1.0;
   out_3163685400089475165[21] = 0.0;
   out_3163685400089475165[22] = 0.0;
   out_3163685400089475165[23] = 0.0;
   out_3163685400089475165[24] = 0.0;
   out_3163685400089475165[25] = 0.0;
   out_3163685400089475165[26] = 0.0;
   out_3163685400089475165[27] = 0.0;
   out_3163685400089475165[28] = 0.0;
   out_3163685400089475165[29] = 0.0;
   out_3163685400089475165[30] = 1.0;
   out_3163685400089475165[31] = 0.0;
   out_3163685400089475165[32] = 0.0;
   out_3163685400089475165[33] = 0.0;
   out_3163685400089475165[34] = 0.0;
   out_3163685400089475165[35] = 0.0;
   out_3163685400089475165[36] = 0.0;
   out_3163685400089475165[37] = 0.0;
   out_3163685400089475165[38] = 0.0;
   out_3163685400089475165[39] = 0.0;
   out_3163685400089475165[40] = 1.0;
   out_3163685400089475165[41] = 0.0;
   out_3163685400089475165[42] = 0.0;
   out_3163685400089475165[43] = 0.0;
   out_3163685400089475165[44] = 0.0;
   out_3163685400089475165[45] = 0.0;
   out_3163685400089475165[46] = 0.0;
   out_3163685400089475165[47] = 0.0;
   out_3163685400089475165[48] = 0.0;
   out_3163685400089475165[49] = 0.0;
   out_3163685400089475165[50] = 1.0;
   out_3163685400089475165[51] = 0.0;
   out_3163685400089475165[52] = 0.0;
   out_3163685400089475165[53] = 0.0;
   out_3163685400089475165[54] = 0.0;
   out_3163685400089475165[55] = 0.0;
   out_3163685400089475165[56] = 0.0;
   out_3163685400089475165[57] = 0.0;
   out_3163685400089475165[58] = 0.0;
   out_3163685400089475165[59] = 0.0;
   out_3163685400089475165[60] = 1.0;
   out_3163685400089475165[61] = 0.0;
   out_3163685400089475165[62] = 0.0;
   out_3163685400089475165[63] = 0.0;
   out_3163685400089475165[64] = 0.0;
   out_3163685400089475165[65] = 0.0;
   out_3163685400089475165[66] = 0.0;
   out_3163685400089475165[67] = 0.0;
   out_3163685400089475165[68] = 0.0;
   out_3163685400089475165[69] = 0.0;
   out_3163685400089475165[70] = 1.0;
   out_3163685400089475165[71] = 0.0;
   out_3163685400089475165[72] = 0.0;
   out_3163685400089475165[73] = 0.0;
   out_3163685400089475165[74] = 0.0;
   out_3163685400089475165[75] = 0.0;
   out_3163685400089475165[76] = 0.0;
   out_3163685400089475165[77] = 0.0;
   out_3163685400089475165[78] = 0.0;
   out_3163685400089475165[79] = 0.0;
   out_3163685400089475165[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_1059011955327416614) {
   out_1059011955327416614[0] = state[0];
   out_1059011955327416614[1] = state[1];
   out_1059011955327416614[2] = state[2];
   out_1059011955327416614[3] = state[3];
   out_1059011955327416614[4] = state[4];
   out_1059011955327416614[5] = dt*(stiffness_front*(-state[2] - state[3] + state[7])*state[0]/state[1] + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/state[4] + ((-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/state[4] - state[4])*state[6] - 9.8100000000000005*state[8]) + state[5];
   out_1059011955327416614[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_1059011955327416614[7] = state[7];
   out_1059011955327416614[8] = state[8];
}
void F_fun(double *state, double dt, double *out_3203946852622260196) {
   out_3203946852622260196[0] = 1;
   out_3203946852622260196[1] = 0;
   out_3203946852622260196[2] = 0;
   out_3203946852622260196[3] = 0;
   out_3203946852622260196[4] = 0;
   out_3203946852622260196[5] = 0;
   out_3203946852622260196[6] = 0;
   out_3203946852622260196[7] = 0;
   out_3203946852622260196[8] = 0;
   out_3203946852622260196[9] = 0;
   out_3203946852622260196[10] = 1;
   out_3203946852622260196[11] = 0;
   out_3203946852622260196[12] = 0;
   out_3203946852622260196[13] = 0;
   out_3203946852622260196[14] = 0;
   out_3203946852622260196[15] = 0;
   out_3203946852622260196[16] = 0;
   out_3203946852622260196[17] = 0;
   out_3203946852622260196[18] = 0;
   out_3203946852622260196[19] = 0;
   out_3203946852622260196[20] = 1;
   out_3203946852622260196[21] = 0;
   out_3203946852622260196[22] = 0;
   out_3203946852622260196[23] = 0;
   out_3203946852622260196[24] = 0;
   out_3203946852622260196[25] = 0;
   out_3203946852622260196[26] = 0;
   out_3203946852622260196[27] = 0;
   out_3203946852622260196[28] = 0;
   out_3203946852622260196[29] = 0;
   out_3203946852622260196[30] = 1;
   out_3203946852622260196[31] = 0;
   out_3203946852622260196[32] = 0;
   out_3203946852622260196[33] = 0;
   out_3203946852622260196[34] = 0;
   out_3203946852622260196[35] = 0;
   out_3203946852622260196[36] = 0;
   out_3203946852622260196[37] = 0;
   out_3203946852622260196[38] = 0;
   out_3203946852622260196[39] = 0;
   out_3203946852622260196[40] = 1;
   out_3203946852622260196[41] = 0;
   out_3203946852622260196[42] = 0;
   out_3203946852622260196[43] = 0;
   out_3203946852622260196[44] = 0;
   out_3203946852622260196[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/state[1] + (-stiffness_front - stiffness_rear)*state[5]/state[4] + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/state[4]);
   out_3203946852622260196[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/pow(state[1], 2);
   out_3203946852622260196[47] = -dt*stiffness_front*state[0]/state[1];
   out_3203946852622260196[48] = -dt*stiffness_front*state[0]/state[1];
   out_3203946852622260196[49] = dt*(-(-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/pow(state[4], 2) + (-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/pow(state[4], 2) - 1)*state[6]);
   out_3203946852622260196[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/state[4] + 1;
   out_3203946852622260196[51] = dt*((-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/state[4] - state[4]);
   out_3203946852622260196[52] = dt*stiffness_front*state[0]/state[1];
   out_3203946852622260196[53] = -9.8100000000000005*dt;
   out_3203946852622260196[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_3203946852622260196[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_3203946852622260196[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_3203946852622260196[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_3203946852622260196[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_3203946852622260196[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_3203946852622260196[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_3203946852622260196[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_3203946852622260196[62] = 0;
   out_3203946852622260196[63] = 0;
   out_3203946852622260196[64] = 0;
   out_3203946852622260196[65] = 0;
   out_3203946852622260196[66] = 0;
   out_3203946852622260196[67] = 0;
   out_3203946852622260196[68] = 0;
   out_3203946852622260196[69] = 0;
   out_3203946852622260196[70] = 1;
   out_3203946852622260196[71] = 0;
   out_3203946852622260196[72] = 0;
   out_3203946852622260196[73] = 0;
   out_3203946852622260196[74] = 0;
   out_3203946852622260196[75] = 0;
   out_3203946852622260196[76] = 0;
   out_3203946852622260196[77] = 0;
   out_3203946852622260196[78] = 0;
   out_3203946852622260196[79] = 0;
   out_3203946852622260196[80] = 1;
}
void h_25(double *state, double *unused, double *out_5888820655433728672) {
   out_5888820655433728672[0] = state[6];
}
void H_25(double *state, double *unused, double *out_1740006425095189675) {
   out_1740006425095189675[0] = 0;
   out_1740006425095189675[1] = 0;
   out_1740006425095189675[2] = 0;
   out_1740006425095189675[3] = 0;
   out_1740006425095189675[4] = 0;
   out_1740006425095189675[5] = 0;
   out_1740006425095189675[6] = 1;
   out_1740006425095189675[7] = 0;
   out_1740006425095189675[8] = 0;
}
void h_24(double *state, double *unused, double *out_7698655859731977364) {
   out_7698655859731977364[0] = state[4];
   out_7698655859731977364[1] = state[5];
}
void H_24(double *state, double *unused, double *out_1343361120741330180) {
   out_1343361120741330180[0] = 0;
   out_1343361120741330180[1] = 0;
   out_1343361120741330180[2] = 0;
   out_1343361120741330180[3] = 0;
   out_1343361120741330180[4] = 1;
   out_1343361120741330180[5] = 0;
   out_1343361120741330180[6] = 0;
   out_1343361120741330180[7] = 0;
   out_1343361120741330180[8] = 0;
   out_1343361120741330180[9] = 0;
   out_1343361120741330180[10] = 0;
   out_1343361120741330180[11] = 0;
   out_1343361120741330180[12] = 0;
   out_1343361120741330180[13] = 0;
   out_1343361120741330180[14] = 1;
   out_1343361120741330180[15] = 0;
   out_1343361120741330180[16] = 0;
   out_1343361120741330180[17] = 0;
}
void h_30(double *state, double *unused, double *out_8836546645789213633) {
   out_8836546645789213633[0] = state[4];
}
void H_30(double *state, double *unused, double *out_4258339383602438302) {
   out_4258339383602438302[0] = 0;
   out_4258339383602438302[1] = 0;
   out_4258339383602438302[2] = 0;
   out_4258339383602438302[3] = 0;
   out_4258339383602438302[4] = 1;
   out_4258339383602438302[5] = 0;
   out_4258339383602438302[6] = 0;
   out_4258339383602438302[7] = 0;
   out_4258339383602438302[8] = 0;
}
void h_26(double *state, double *unused, double *out_7752730088945658857) {
   out_7752730088945658857[0] = state[7];
}
void H_26(double *state, double *unused, double *out_2001496893778866549) {
   out_2001496893778866549[0] = 0;
   out_2001496893778866549[1] = 0;
   out_2001496893778866549[2] = 0;
   out_2001496893778866549[3] = 0;
   out_2001496893778866549[4] = 0;
   out_2001496893778866549[5] = 0;
   out_2001496893778866549[6] = 0;
   out_2001496893778866549[7] = 1;
   out_2001496893778866549[8] = 0;
}
void h_27(double *state, double *unused, double *out_4529810036305668007) {
   out_4529810036305668007[0] = state[3];
}
void H_27(double *state, double *unused, double *out_6481933454786381519) {
   out_6481933454786381519[0] = 0;
   out_6481933454786381519[1] = 0;
   out_6481933454786381519[2] = 0;
   out_6481933454786381519[3] = 1;
   out_6481933454786381519[4] = 0;
   out_6481933454786381519[5] = 0;
   out_6481933454786381519[6] = 0;
   out_6481933454786381519[7] = 0;
   out_6481933454786381519[8] = 0;
}
void h_29(double *state, double *unused, double *out_7146098811053532673) {
   out_7146098811053532673[0] = state[1];
}
void H_29(double *state, double *unused, double *out_4768570727916830486) {
   out_4768570727916830486[0] = 0;
   out_4768570727916830486[1] = 1;
   out_4768570727916830486[2] = 0;
   out_4768570727916830486[3] = 0;
   out_4768570727916830486[4] = 0;
   out_4768570727916830486[5] = 0;
   out_4768570727916830486[6] = 0;
   out_4768570727916830486[7] = 0;
   out_4768570727916830486[8] = 0;
}
void h_28(double *state, double *unused, double *out_471863231355177638) {
   out_471863231355177638[0] = state[0];
}
void H_28(double *state, double *unused, double *out_313828289152700088) {
   out_313828289152700088[0] = 1;
   out_313828289152700088[1] = 0;
   out_313828289152700088[2] = 0;
   out_313828289152700088[3] = 0;
   out_313828289152700088[4] = 0;
   out_313828289152700088[5] = 0;
   out_313828289152700088[6] = 0;
   out_313828289152700088[7] = 0;
   out_313828289152700088[8] = 0;
}
void h_31(double *state, double *unused, double *out_1992451995320320513) {
   out_1992451995320320513[0] = state[8];
}
void H_31(double *state, double *unused, double *out_2627704996012218025) {
   out_2627704996012218025[0] = 0;
   out_2627704996012218025[1] = 0;
   out_2627704996012218025[2] = 0;
   out_2627704996012218025[3] = 0;
   out_2627704996012218025[4] = 0;
   out_2627704996012218025[5] = 0;
   out_2627704996012218025[6] = 0;
   out_2627704996012218025[7] = 0;
   out_2627704996012218025[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_8852971544794429466) {
  err_fun(nom_x, delta_x, out_8852971544794429466);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_5565710821617854915) {
  inv_err_fun(nom_x, true_x, out_5565710821617854915);
}
void car_H_mod_fun(double *state, double *out_3163685400089475165) {
  H_mod_fun(state, out_3163685400089475165);
}
void car_f_fun(double *state, double dt, double *out_1059011955327416614) {
  f_fun(state,  dt, out_1059011955327416614);
}
void car_F_fun(double *state, double dt, double *out_3203946852622260196) {
  F_fun(state,  dt, out_3203946852622260196);
}
void car_h_25(double *state, double *unused, double *out_5888820655433728672) {
  h_25(state, unused, out_5888820655433728672);
}
void car_H_25(double *state, double *unused, double *out_1740006425095189675) {
  H_25(state, unused, out_1740006425095189675);
}
void car_h_24(double *state, double *unused, double *out_7698655859731977364) {
  h_24(state, unused, out_7698655859731977364);
}
void car_H_24(double *state, double *unused, double *out_1343361120741330180) {
  H_24(state, unused, out_1343361120741330180);
}
void car_h_30(double *state, double *unused, double *out_8836546645789213633) {
  h_30(state, unused, out_8836546645789213633);
}
void car_H_30(double *state, double *unused, double *out_4258339383602438302) {
  H_30(state, unused, out_4258339383602438302);
}
void car_h_26(double *state, double *unused, double *out_7752730088945658857) {
  h_26(state, unused, out_7752730088945658857);
}
void car_H_26(double *state, double *unused, double *out_2001496893778866549) {
  H_26(state, unused, out_2001496893778866549);
}
void car_h_27(double *state, double *unused, double *out_4529810036305668007) {
  h_27(state, unused, out_4529810036305668007);
}
void car_H_27(double *state, double *unused, double *out_6481933454786381519) {
  H_27(state, unused, out_6481933454786381519);
}
void car_h_29(double *state, double *unused, double *out_7146098811053532673) {
  h_29(state, unused, out_7146098811053532673);
}
void car_H_29(double *state, double *unused, double *out_4768570727916830486) {
  H_29(state, unused, out_4768570727916830486);
}
void car_h_28(double *state, double *unused, double *out_471863231355177638) {
  h_28(state, unused, out_471863231355177638);
}
void car_H_28(double *state, double *unused, double *out_313828289152700088) {
  H_28(state, unused, out_313828289152700088);
}
void car_h_31(double *state, double *unused, double *out_1992451995320320513) {
  h_31(state, unused, out_1992451995320320513);
}
void car_H_31(double *state, double *unused, double *out_2627704996012218025) {
  H_31(state, unused, out_2627704996012218025);
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
