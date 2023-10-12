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
void err_fun(double *nom_x, double *delta_x, double *out_4478115031684730111) {
   out_4478115031684730111[0] = delta_x[0] + nom_x[0];
   out_4478115031684730111[1] = delta_x[1] + nom_x[1];
   out_4478115031684730111[2] = delta_x[2] + nom_x[2];
   out_4478115031684730111[3] = delta_x[3] + nom_x[3];
   out_4478115031684730111[4] = delta_x[4] + nom_x[4];
   out_4478115031684730111[5] = delta_x[5] + nom_x[5];
   out_4478115031684730111[6] = delta_x[6] + nom_x[6];
   out_4478115031684730111[7] = delta_x[7] + nom_x[7];
   out_4478115031684730111[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_977820433766164866) {
   out_977820433766164866[0] = -nom_x[0] + true_x[0];
   out_977820433766164866[1] = -nom_x[1] + true_x[1];
   out_977820433766164866[2] = -nom_x[2] + true_x[2];
   out_977820433766164866[3] = -nom_x[3] + true_x[3];
   out_977820433766164866[4] = -nom_x[4] + true_x[4];
   out_977820433766164866[5] = -nom_x[5] + true_x[5];
   out_977820433766164866[6] = -nom_x[6] + true_x[6];
   out_977820433766164866[7] = -nom_x[7] + true_x[7];
   out_977820433766164866[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_3399376930338853021) {
   out_3399376930338853021[0] = 1.0;
   out_3399376930338853021[1] = 0;
   out_3399376930338853021[2] = 0;
   out_3399376930338853021[3] = 0;
   out_3399376930338853021[4] = 0;
   out_3399376930338853021[5] = 0;
   out_3399376930338853021[6] = 0;
   out_3399376930338853021[7] = 0;
   out_3399376930338853021[8] = 0;
   out_3399376930338853021[9] = 0;
   out_3399376930338853021[10] = 1.0;
   out_3399376930338853021[11] = 0;
   out_3399376930338853021[12] = 0;
   out_3399376930338853021[13] = 0;
   out_3399376930338853021[14] = 0;
   out_3399376930338853021[15] = 0;
   out_3399376930338853021[16] = 0;
   out_3399376930338853021[17] = 0;
   out_3399376930338853021[18] = 0;
   out_3399376930338853021[19] = 0;
   out_3399376930338853021[20] = 1.0;
   out_3399376930338853021[21] = 0;
   out_3399376930338853021[22] = 0;
   out_3399376930338853021[23] = 0;
   out_3399376930338853021[24] = 0;
   out_3399376930338853021[25] = 0;
   out_3399376930338853021[26] = 0;
   out_3399376930338853021[27] = 0;
   out_3399376930338853021[28] = 0;
   out_3399376930338853021[29] = 0;
   out_3399376930338853021[30] = 1.0;
   out_3399376930338853021[31] = 0;
   out_3399376930338853021[32] = 0;
   out_3399376930338853021[33] = 0;
   out_3399376930338853021[34] = 0;
   out_3399376930338853021[35] = 0;
   out_3399376930338853021[36] = 0;
   out_3399376930338853021[37] = 0;
   out_3399376930338853021[38] = 0;
   out_3399376930338853021[39] = 0;
   out_3399376930338853021[40] = 1.0;
   out_3399376930338853021[41] = 0;
   out_3399376930338853021[42] = 0;
   out_3399376930338853021[43] = 0;
   out_3399376930338853021[44] = 0;
   out_3399376930338853021[45] = 0;
   out_3399376930338853021[46] = 0;
   out_3399376930338853021[47] = 0;
   out_3399376930338853021[48] = 0;
   out_3399376930338853021[49] = 0;
   out_3399376930338853021[50] = 1.0;
   out_3399376930338853021[51] = 0;
   out_3399376930338853021[52] = 0;
   out_3399376930338853021[53] = 0;
   out_3399376930338853021[54] = 0;
   out_3399376930338853021[55] = 0;
   out_3399376930338853021[56] = 0;
   out_3399376930338853021[57] = 0;
   out_3399376930338853021[58] = 0;
   out_3399376930338853021[59] = 0;
   out_3399376930338853021[60] = 1.0;
   out_3399376930338853021[61] = 0;
   out_3399376930338853021[62] = 0;
   out_3399376930338853021[63] = 0;
   out_3399376930338853021[64] = 0;
   out_3399376930338853021[65] = 0;
   out_3399376930338853021[66] = 0;
   out_3399376930338853021[67] = 0;
   out_3399376930338853021[68] = 0;
   out_3399376930338853021[69] = 0;
   out_3399376930338853021[70] = 1.0;
   out_3399376930338853021[71] = 0;
   out_3399376930338853021[72] = 0;
   out_3399376930338853021[73] = 0;
   out_3399376930338853021[74] = 0;
   out_3399376930338853021[75] = 0;
   out_3399376930338853021[76] = 0;
   out_3399376930338853021[77] = 0;
   out_3399376930338853021[78] = 0;
   out_3399376930338853021[79] = 0;
   out_3399376930338853021[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_4607110025418154468) {
   out_4607110025418154468[0] = state[0];
   out_4607110025418154468[1] = state[1];
   out_4607110025418154468[2] = state[2];
   out_4607110025418154468[3] = state[3];
   out_4607110025418154468[4] = state[4];
   out_4607110025418154468[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8000000000000007*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_4607110025418154468[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_4607110025418154468[7] = state[7];
   out_4607110025418154468[8] = state[8];
}
void F_fun(double *state, double dt, double *out_3068422806702534156) {
   out_3068422806702534156[0] = 1;
   out_3068422806702534156[1] = 0;
   out_3068422806702534156[2] = 0;
   out_3068422806702534156[3] = 0;
   out_3068422806702534156[4] = 0;
   out_3068422806702534156[5] = 0;
   out_3068422806702534156[6] = 0;
   out_3068422806702534156[7] = 0;
   out_3068422806702534156[8] = 0;
   out_3068422806702534156[9] = 0;
   out_3068422806702534156[10] = 1;
   out_3068422806702534156[11] = 0;
   out_3068422806702534156[12] = 0;
   out_3068422806702534156[13] = 0;
   out_3068422806702534156[14] = 0;
   out_3068422806702534156[15] = 0;
   out_3068422806702534156[16] = 0;
   out_3068422806702534156[17] = 0;
   out_3068422806702534156[18] = 0;
   out_3068422806702534156[19] = 0;
   out_3068422806702534156[20] = 1;
   out_3068422806702534156[21] = 0;
   out_3068422806702534156[22] = 0;
   out_3068422806702534156[23] = 0;
   out_3068422806702534156[24] = 0;
   out_3068422806702534156[25] = 0;
   out_3068422806702534156[26] = 0;
   out_3068422806702534156[27] = 0;
   out_3068422806702534156[28] = 0;
   out_3068422806702534156[29] = 0;
   out_3068422806702534156[30] = 1;
   out_3068422806702534156[31] = 0;
   out_3068422806702534156[32] = 0;
   out_3068422806702534156[33] = 0;
   out_3068422806702534156[34] = 0;
   out_3068422806702534156[35] = 0;
   out_3068422806702534156[36] = 0;
   out_3068422806702534156[37] = 0;
   out_3068422806702534156[38] = 0;
   out_3068422806702534156[39] = 0;
   out_3068422806702534156[40] = 1;
   out_3068422806702534156[41] = 0;
   out_3068422806702534156[42] = 0;
   out_3068422806702534156[43] = 0;
   out_3068422806702534156[44] = 0;
   out_3068422806702534156[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_3068422806702534156[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_3068422806702534156[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_3068422806702534156[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_3068422806702534156[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_3068422806702534156[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_3068422806702534156[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_3068422806702534156[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_3068422806702534156[53] = -9.8000000000000007*dt;
   out_3068422806702534156[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_3068422806702534156[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_3068422806702534156[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_3068422806702534156[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_3068422806702534156[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_3068422806702534156[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_3068422806702534156[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_3068422806702534156[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_3068422806702534156[62] = 0;
   out_3068422806702534156[63] = 0;
   out_3068422806702534156[64] = 0;
   out_3068422806702534156[65] = 0;
   out_3068422806702534156[66] = 0;
   out_3068422806702534156[67] = 0;
   out_3068422806702534156[68] = 0;
   out_3068422806702534156[69] = 0;
   out_3068422806702534156[70] = 1;
   out_3068422806702534156[71] = 0;
   out_3068422806702534156[72] = 0;
   out_3068422806702534156[73] = 0;
   out_3068422806702534156[74] = 0;
   out_3068422806702534156[75] = 0;
   out_3068422806702534156[76] = 0;
   out_3068422806702534156[77] = 0;
   out_3068422806702534156[78] = 0;
   out_3068422806702534156[79] = 0;
   out_3068422806702534156[80] = 1;
}
void h_25(double *state, double *unused, double *out_8030843570930631638) {
   out_8030843570930631638[0] = state[6];
}
void H_25(double *state, double *unused, double *out_4054472870645857943) {
   out_4054472870645857943[0] = 0;
   out_4054472870645857943[1] = 0;
   out_4054472870645857943[2] = 0;
   out_4054472870645857943[3] = 0;
   out_4054472870645857943[4] = 0;
   out_4054472870645857943[5] = 0;
   out_4054472870645857943[6] = 1;
   out_4054472870645857943[7] = 0;
   out_4054472870645857943[8] = 0;
}
void h_24(double *state, double *unused, double *out_5199469125424995696) {
   out_5199469125424995696[0] = state[4];
   out_5199469125424995696[1] = state[5];
}
void H_24(double *state, double *unused, double *out_5164206016994498448) {
   out_5164206016994498448[0] = 0;
   out_5164206016994498448[1] = 0;
   out_5164206016994498448[2] = 0;
   out_5164206016994498448[3] = 0;
   out_5164206016994498448[4] = 1;
   out_5164206016994498448[5] = 0;
   out_5164206016994498448[6] = 0;
   out_5164206016994498448[7] = 0;
   out_5164206016994498448[8] = 0;
   out_5164206016994498448[9] = 0;
   out_5164206016994498448[10] = 0;
   out_5164206016994498448[11] = 0;
   out_5164206016994498448[12] = 0;
   out_5164206016994498448[13] = 0;
   out_5164206016994498448[14] = 1;
   out_5164206016994498448[15] = 0;
   out_5164206016994498448[16] = 0;
   out_5164206016994498448[17] = 0;
}
void h_30(double *state, double *unused, double *out_1260008344580280702) {
   out_1260008344580280702[0] = state[4];
}
void H_30(double *state, double *unused, double *out_473223459481750255) {
   out_473223459481750255[0] = 0;
   out_473223459481750255[1] = 0;
   out_473223459481750255[2] = 0;
   out_473223459481750255[3] = 0;
   out_473223459481750255[4] = 1;
   out_473223459481750255[5] = 0;
   out_473223459481750255[6] = 0;
   out_473223459481750255[7] = 0;
   out_473223459481750255[8] = 0;
}
void h_26(double *state, double *unused, double *out_3741664923080564943) {
   out_3741664923080564943[0] = state[7];
}
void H_26(double *state, double *unused, double *out_312969551771801719) {
   out_312969551771801719[0] = 0;
   out_312969551771801719[1] = 0;
   out_312969551771801719[2] = 0;
   out_312969551771801719[3] = 0;
   out_312969551771801719[4] = 0;
   out_312969551771801719[5] = 0;
   out_312969551771801719[6] = 0;
   out_312969551771801719[7] = 1;
   out_312969551771801719[8] = 0;
}
void h_27(double *state, double *unused, double *out_6340395736194950678) {
   out_6340395736194950678[0] = state[3];
}
void H_27(double *state, double *unused, double *out_2647986771282175166) {
   out_2647986771282175166[0] = 0;
   out_2647986771282175166[1] = 0;
   out_2647986771282175166[2] = 0;
   out_2647986771282175166[3] = 1;
   out_2647986771282175166[4] = 0;
   out_2647986771282175166[5] = 0;
   out_2647986771282175166[6] = 0;
   out_2647986771282175166[7] = 0;
   out_2647986771282175166[8] = 0;
}
void h_29(double *state, double *unused, double *out_5950901141673940809) {
   out_5950901141673940809[0] = state[1];
}
void H_29(double *state, double *unused, double *out_37007884832641929) {
   out_37007884832641929[0] = 0;
   out_37007884832641929[1] = 1;
   out_37007884832641929[2] = 0;
   out_37007884832641929[3] = 0;
   out_37007884832641929[4] = 0;
   out_37007884832641929[5] = 0;
   out_37007884832641929[6] = 0;
   out_37007884832641929[7] = 0;
   out_37007884832641929[8] = 0;
}
void h_28(double *state, double *unused, double *out_7690649602705446720) {
   out_7690649602705446720[0] = state[0];
}
void H_28(double *state, double *unused, double *out_5045391132236888645) {
   out_5045391132236888645[0] = 1;
   out_5045391132236888645[1] = 0;
   out_5045391132236888645[2] = 0;
   out_5045391132236888645[3] = 0;
   out_5045391132236888645[4] = 0;
   out_5045391132236888645[5] = 0;
   out_5045391132236888645[6] = 0;
   out_5045391132236888645[7] = 0;
   out_5045391132236888645[8] = 0;
}
void h_31(double *state, double *unused, double *out_2522961007894396619) {
   out_2522961007894396619[0] = state[8];
}
void H_31(double *state, double *unused, double *out_313238550461549757) {
   out_313238550461549757[0] = 0;
   out_313238550461549757[1] = 0;
   out_313238550461549757[2] = 0;
   out_313238550461549757[3] = 0;
   out_313238550461549757[4] = 0;
   out_313238550461549757[5] = 0;
   out_313238550461549757[6] = 0;
   out_313238550461549757[7] = 0;
   out_313238550461549757[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_4478115031684730111) {
  err_fun(nom_x, delta_x, out_4478115031684730111);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_977820433766164866) {
  inv_err_fun(nom_x, true_x, out_977820433766164866);
}
void car_H_mod_fun(double *state, double *out_3399376930338853021) {
  H_mod_fun(state, out_3399376930338853021);
}
void car_f_fun(double *state, double dt, double *out_4607110025418154468) {
  f_fun(state,  dt, out_4607110025418154468);
}
void car_F_fun(double *state, double dt, double *out_3068422806702534156) {
  F_fun(state,  dt, out_3068422806702534156);
}
void car_h_25(double *state, double *unused, double *out_8030843570930631638) {
  h_25(state, unused, out_8030843570930631638);
}
void car_H_25(double *state, double *unused, double *out_4054472870645857943) {
  H_25(state, unused, out_4054472870645857943);
}
void car_h_24(double *state, double *unused, double *out_5199469125424995696) {
  h_24(state, unused, out_5199469125424995696);
}
void car_H_24(double *state, double *unused, double *out_5164206016994498448) {
  H_24(state, unused, out_5164206016994498448);
}
void car_h_30(double *state, double *unused, double *out_1260008344580280702) {
  h_30(state, unused, out_1260008344580280702);
}
void car_H_30(double *state, double *unused, double *out_473223459481750255) {
  H_30(state, unused, out_473223459481750255);
}
void car_h_26(double *state, double *unused, double *out_3741664923080564943) {
  h_26(state, unused, out_3741664923080564943);
}
void car_H_26(double *state, double *unused, double *out_312969551771801719) {
  H_26(state, unused, out_312969551771801719);
}
void car_h_27(double *state, double *unused, double *out_6340395736194950678) {
  h_27(state, unused, out_6340395736194950678);
}
void car_H_27(double *state, double *unused, double *out_2647986771282175166) {
  H_27(state, unused, out_2647986771282175166);
}
void car_h_29(double *state, double *unused, double *out_5950901141673940809) {
  h_29(state, unused, out_5950901141673940809);
}
void car_H_29(double *state, double *unused, double *out_37007884832641929) {
  H_29(state, unused, out_37007884832641929);
}
void car_h_28(double *state, double *unused, double *out_7690649602705446720) {
  h_28(state, unused, out_7690649602705446720);
}
void car_H_28(double *state, double *unused, double *out_5045391132236888645) {
  H_28(state, unused, out_5045391132236888645);
}
void car_h_31(double *state, double *unused, double *out_2522961007894396619) {
  h_31(state, unused, out_2522961007894396619);
}
void car_H_31(double *state, double *unused, double *out_313238550461549757) {
  H_31(state, unused, out_313238550461549757);
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

ekf_init(car);
