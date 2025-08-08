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
void err_fun(double *nom_x, double *delta_x, double *out_7216862993207776403) {
   out_7216862993207776403[0] = delta_x[0] + nom_x[0];
   out_7216862993207776403[1] = delta_x[1] + nom_x[1];
   out_7216862993207776403[2] = delta_x[2] + nom_x[2];
   out_7216862993207776403[3] = delta_x[3] + nom_x[3];
   out_7216862993207776403[4] = delta_x[4] + nom_x[4];
   out_7216862993207776403[5] = delta_x[5] + nom_x[5];
   out_7216862993207776403[6] = delta_x[6] + nom_x[6];
   out_7216862993207776403[7] = delta_x[7] + nom_x[7];
   out_7216862993207776403[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_6378237758255440014) {
   out_6378237758255440014[0] = -nom_x[0] + true_x[0];
   out_6378237758255440014[1] = -nom_x[1] + true_x[1];
   out_6378237758255440014[2] = -nom_x[2] + true_x[2];
   out_6378237758255440014[3] = -nom_x[3] + true_x[3];
   out_6378237758255440014[4] = -nom_x[4] + true_x[4];
   out_6378237758255440014[5] = -nom_x[5] + true_x[5];
   out_6378237758255440014[6] = -nom_x[6] + true_x[6];
   out_6378237758255440014[7] = -nom_x[7] + true_x[7];
   out_6378237758255440014[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_4368013663920627707) {
   out_4368013663920627707[0] = 1.0;
   out_4368013663920627707[1] = 0.0;
   out_4368013663920627707[2] = 0.0;
   out_4368013663920627707[3] = 0.0;
   out_4368013663920627707[4] = 0.0;
   out_4368013663920627707[5] = 0.0;
   out_4368013663920627707[6] = 0.0;
   out_4368013663920627707[7] = 0.0;
   out_4368013663920627707[8] = 0.0;
   out_4368013663920627707[9] = 0.0;
   out_4368013663920627707[10] = 1.0;
   out_4368013663920627707[11] = 0.0;
   out_4368013663920627707[12] = 0.0;
   out_4368013663920627707[13] = 0.0;
   out_4368013663920627707[14] = 0.0;
   out_4368013663920627707[15] = 0.0;
   out_4368013663920627707[16] = 0.0;
   out_4368013663920627707[17] = 0.0;
   out_4368013663920627707[18] = 0.0;
   out_4368013663920627707[19] = 0.0;
   out_4368013663920627707[20] = 1.0;
   out_4368013663920627707[21] = 0.0;
   out_4368013663920627707[22] = 0.0;
   out_4368013663920627707[23] = 0.0;
   out_4368013663920627707[24] = 0.0;
   out_4368013663920627707[25] = 0.0;
   out_4368013663920627707[26] = 0.0;
   out_4368013663920627707[27] = 0.0;
   out_4368013663920627707[28] = 0.0;
   out_4368013663920627707[29] = 0.0;
   out_4368013663920627707[30] = 1.0;
   out_4368013663920627707[31] = 0.0;
   out_4368013663920627707[32] = 0.0;
   out_4368013663920627707[33] = 0.0;
   out_4368013663920627707[34] = 0.0;
   out_4368013663920627707[35] = 0.0;
   out_4368013663920627707[36] = 0.0;
   out_4368013663920627707[37] = 0.0;
   out_4368013663920627707[38] = 0.0;
   out_4368013663920627707[39] = 0.0;
   out_4368013663920627707[40] = 1.0;
   out_4368013663920627707[41] = 0.0;
   out_4368013663920627707[42] = 0.0;
   out_4368013663920627707[43] = 0.0;
   out_4368013663920627707[44] = 0.0;
   out_4368013663920627707[45] = 0.0;
   out_4368013663920627707[46] = 0.0;
   out_4368013663920627707[47] = 0.0;
   out_4368013663920627707[48] = 0.0;
   out_4368013663920627707[49] = 0.0;
   out_4368013663920627707[50] = 1.0;
   out_4368013663920627707[51] = 0.0;
   out_4368013663920627707[52] = 0.0;
   out_4368013663920627707[53] = 0.0;
   out_4368013663920627707[54] = 0.0;
   out_4368013663920627707[55] = 0.0;
   out_4368013663920627707[56] = 0.0;
   out_4368013663920627707[57] = 0.0;
   out_4368013663920627707[58] = 0.0;
   out_4368013663920627707[59] = 0.0;
   out_4368013663920627707[60] = 1.0;
   out_4368013663920627707[61] = 0.0;
   out_4368013663920627707[62] = 0.0;
   out_4368013663920627707[63] = 0.0;
   out_4368013663920627707[64] = 0.0;
   out_4368013663920627707[65] = 0.0;
   out_4368013663920627707[66] = 0.0;
   out_4368013663920627707[67] = 0.0;
   out_4368013663920627707[68] = 0.0;
   out_4368013663920627707[69] = 0.0;
   out_4368013663920627707[70] = 1.0;
   out_4368013663920627707[71] = 0.0;
   out_4368013663920627707[72] = 0.0;
   out_4368013663920627707[73] = 0.0;
   out_4368013663920627707[74] = 0.0;
   out_4368013663920627707[75] = 0.0;
   out_4368013663920627707[76] = 0.0;
   out_4368013663920627707[77] = 0.0;
   out_4368013663920627707[78] = 0.0;
   out_4368013663920627707[79] = 0.0;
   out_4368013663920627707[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_640655310412688382) {
   out_640655310412688382[0] = state[0];
   out_640655310412688382[1] = state[1];
   out_640655310412688382[2] = state[2];
   out_640655310412688382[3] = state[3];
   out_640655310412688382[4] = state[4];
   out_640655310412688382[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8000000000000007*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_640655310412688382[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_640655310412688382[7] = state[7];
   out_640655310412688382[8] = state[8];
}
void F_fun(double *state, double dt, double *out_9164188615644588775) {
   out_9164188615644588775[0] = 1;
   out_9164188615644588775[1] = 0;
   out_9164188615644588775[2] = 0;
   out_9164188615644588775[3] = 0;
   out_9164188615644588775[4] = 0;
   out_9164188615644588775[5] = 0;
   out_9164188615644588775[6] = 0;
   out_9164188615644588775[7] = 0;
   out_9164188615644588775[8] = 0;
   out_9164188615644588775[9] = 0;
   out_9164188615644588775[10] = 1;
   out_9164188615644588775[11] = 0;
   out_9164188615644588775[12] = 0;
   out_9164188615644588775[13] = 0;
   out_9164188615644588775[14] = 0;
   out_9164188615644588775[15] = 0;
   out_9164188615644588775[16] = 0;
   out_9164188615644588775[17] = 0;
   out_9164188615644588775[18] = 0;
   out_9164188615644588775[19] = 0;
   out_9164188615644588775[20] = 1;
   out_9164188615644588775[21] = 0;
   out_9164188615644588775[22] = 0;
   out_9164188615644588775[23] = 0;
   out_9164188615644588775[24] = 0;
   out_9164188615644588775[25] = 0;
   out_9164188615644588775[26] = 0;
   out_9164188615644588775[27] = 0;
   out_9164188615644588775[28] = 0;
   out_9164188615644588775[29] = 0;
   out_9164188615644588775[30] = 1;
   out_9164188615644588775[31] = 0;
   out_9164188615644588775[32] = 0;
   out_9164188615644588775[33] = 0;
   out_9164188615644588775[34] = 0;
   out_9164188615644588775[35] = 0;
   out_9164188615644588775[36] = 0;
   out_9164188615644588775[37] = 0;
   out_9164188615644588775[38] = 0;
   out_9164188615644588775[39] = 0;
   out_9164188615644588775[40] = 1;
   out_9164188615644588775[41] = 0;
   out_9164188615644588775[42] = 0;
   out_9164188615644588775[43] = 0;
   out_9164188615644588775[44] = 0;
   out_9164188615644588775[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_9164188615644588775[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_9164188615644588775[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_9164188615644588775[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_9164188615644588775[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_9164188615644588775[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_9164188615644588775[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_9164188615644588775[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_9164188615644588775[53] = -9.8000000000000007*dt;
   out_9164188615644588775[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_9164188615644588775[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_9164188615644588775[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_9164188615644588775[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_9164188615644588775[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_9164188615644588775[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_9164188615644588775[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_9164188615644588775[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_9164188615644588775[62] = 0;
   out_9164188615644588775[63] = 0;
   out_9164188615644588775[64] = 0;
   out_9164188615644588775[65] = 0;
   out_9164188615644588775[66] = 0;
   out_9164188615644588775[67] = 0;
   out_9164188615644588775[68] = 0;
   out_9164188615644588775[69] = 0;
   out_9164188615644588775[70] = 1;
   out_9164188615644588775[71] = 0;
   out_9164188615644588775[72] = 0;
   out_9164188615644588775[73] = 0;
   out_9164188615644588775[74] = 0;
   out_9164188615644588775[75] = 0;
   out_9164188615644588775[76] = 0;
   out_9164188615644588775[77] = 0;
   out_9164188615644588775[78] = 0;
   out_9164188615644588775[79] = 0;
   out_9164188615644588775[80] = 1;
}
void h_25(double *state, double *unused, double *out_1790118014898518564) {
   out_1790118014898518564[0] = state[6];
}
void H_25(double *state, double *unused, double *out_7891062302565992855) {
   out_7891062302565992855[0] = 0;
   out_7891062302565992855[1] = 0;
   out_7891062302565992855[2] = 0;
   out_7891062302565992855[3] = 0;
   out_7891062302565992855[4] = 0;
   out_7891062302565992855[5] = 0;
   out_7891062302565992855[6] = 1;
   out_7891062302565992855[7] = 0;
   out_7891062302565992855[8] = 0;
}
void h_24(double *state, double *unused, double *out_4114360205345828396) {
   out_4114360205345828396[0] = state[4];
   out_4114360205345828396[1] = state[5];
}
void H_24(double *state, double *unused, double *out_5809172444177049727) {
   out_5809172444177049727[0] = 0;
   out_5809172444177049727[1] = 0;
   out_5809172444177049727[2] = 0;
   out_5809172444177049727[3] = 0;
   out_5809172444177049727[4] = 1;
   out_5809172444177049727[5] = 0;
   out_5809172444177049727[6] = 0;
   out_5809172444177049727[7] = 0;
   out_5809172444177049727[8] = 0;
   out_5809172444177049727[9] = 0;
   out_5809172444177049727[10] = 0;
   out_5809172444177049727[11] = 0;
   out_5809172444177049727[12] = 0;
   out_5809172444177049727[13] = 0;
   out_5809172444177049727[14] = 1;
   out_5809172444177049727[15] = 0;
   out_5809172444177049727[16] = 0;
   out_5809172444177049727[17] = 0;
}
void h_30(double *state, double *unused, double *out_5888421313177890428) {
   out_5888421313177890428[0] = state[4];
}
void H_30(double *state, double *unused, double *out_5372729344058744228) {
   out_5372729344058744228[0] = 0;
   out_5372729344058744228[1] = 0;
   out_5372729344058744228[2] = 0;
   out_5372729344058744228[3] = 0;
   out_5372729344058744228[4] = 1;
   out_5372729344058744228[5] = 0;
   out_5372729344058744228[6] = 0;
   out_5372729344058744228[7] = 0;
   out_5372729344058744228[8] = 0;
}
void h_26(double *state, double *unused, double *out_2851635261733557743) {
   out_2851635261733557743[0] = state[7];
}
void H_26(double *state, double *unused, double *out_4586536332805192254) {
   out_4586536332805192254[0] = 0;
   out_4586536332805192254[1] = 0;
   out_4586536332805192254[2] = 0;
   out_4586536332805192254[3] = 0;
   out_4586536332805192254[4] = 0;
   out_4586536332805192254[5] = 0;
   out_4586536332805192254[6] = 0;
   out_4586536332805192254[7] = 1;
   out_4586536332805192254[8] = 0;
}
void h_27(double *state, double *unused, double *out_2733627867800180999) {
   out_2733627867800180999[0] = state[3];
}
void H_27(double *state, double *unused, double *out_3149135272874801011) {
   out_3149135272874801011[0] = 0;
   out_3149135272874801011[1] = 0;
   out_3149135272874801011[2] = 0;
   out_3149135272874801011[3] = 1;
   out_3149135272874801011[4] = 0;
   out_3149135272874801011[5] = 0;
   out_3149135272874801011[6] = 0;
   out_3149135272874801011[7] = 0;
   out_3149135272874801011[8] = 0;
}
void h_29(double *state, double *unused, double *out_6159281243117812042) {
   out_6159281243117812042[0] = state[1];
}
void H_29(double *state, double *unused, double *out_4862497999744352044) {
   out_4862497999744352044[0] = 0;
   out_4862497999744352044[1] = 1;
   out_4862497999744352044[2] = 0;
   out_4862497999744352044[3] = 0;
   out_4862497999744352044[4] = 0;
   out_4862497999744352044[5] = 0;
   out_4862497999744352044[6] = 0;
   out_4862497999744352044[7] = 0;
   out_4862497999744352044[8] = 0;
}
void h_28(double *state, double *unused, double *out_542219944947275590) {
   out_542219944947275590[0] = state[0];
}
void H_28(double *state, double *unused, double *out_8501847056895668998) {
   out_8501847056895668998[0] = 1;
   out_8501847056895668998[1] = 0;
   out_8501847056895668998[2] = 0;
   out_8501847056895668998[3] = 0;
   out_8501847056895668998[4] = 0;
   out_8501847056895668998[5] = 0;
   out_8501847056895668998[6] = 0;
   out_8501847056895668998[7] = 0;
   out_8501847056895668998[8] = 0;
}
void h_31(double *state, double *unused, double *out_8775353408056983867) {
   out_8775353408056983867[0] = state[8];
}
void H_31(double *state, double *unused, double *out_814387052054175602) {
   out_814387052054175602[0] = 0;
   out_814387052054175602[1] = 0;
   out_814387052054175602[2] = 0;
   out_814387052054175602[3] = 0;
   out_814387052054175602[4] = 0;
   out_814387052054175602[5] = 0;
   out_814387052054175602[6] = 0;
   out_814387052054175602[7] = 0;
   out_814387052054175602[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_7216862993207776403) {
  err_fun(nom_x, delta_x, out_7216862993207776403);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_6378237758255440014) {
  inv_err_fun(nom_x, true_x, out_6378237758255440014);
}
void car_H_mod_fun(double *state, double *out_4368013663920627707) {
  H_mod_fun(state, out_4368013663920627707);
}
void car_f_fun(double *state, double dt, double *out_640655310412688382) {
  f_fun(state,  dt, out_640655310412688382);
}
void car_F_fun(double *state, double dt, double *out_9164188615644588775) {
  F_fun(state,  dt, out_9164188615644588775);
}
void car_h_25(double *state, double *unused, double *out_1790118014898518564) {
  h_25(state, unused, out_1790118014898518564);
}
void car_H_25(double *state, double *unused, double *out_7891062302565992855) {
  H_25(state, unused, out_7891062302565992855);
}
void car_h_24(double *state, double *unused, double *out_4114360205345828396) {
  h_24(state, unused, out_4114360205345828396);
}
void car_H_24(double *state, double *unused, double *out_5809172444177049727) {
  H_24(state, unused, out_5809172444177049727);
}
void car_h_30(double *state, double *unused, double *out_5888421313177890428) {
  h_30(state, unused, out_5888421313177890428);
}
void car_H_30(double *state, double *unused, double *out_5372729344058744228) {
  H_30(state, unused, out_5372729344058744228);
}
void car_h_26(double *state, double *unused, double *out_2851635261733557743) {
  h_26(state, unused, out_2851635261733557743);
}
void car_H_26(double *state, double *unused, double *out_4586536332805192254) {
  H_26(state, unused, out_4586536332805192254);
}
void car_h_27(double *state, double *unused, double *out_2733627867800180999) {
  h_27(state, unused, out_2733627867800180999);
}
void car_H_27(double *state, double *unused, double *out_3149135272874801011) {
  H_27(state, unused, out_3149135272874801011);
}
void car_h_29(double *state, double *unused, double *out_6159281243117812042) {
  h_29(state, unused, out_6159281243117812042);
}
void car_H_29(double *state, double *unused, double *out_4862497999744352044) {
  H_29(state, unused, out_4862497999744352044);
}
void car_h_28(double *state, double *unused, double *out_542219944947275590) {
  h_28(state, unused, out_542219944947275590);
}
void car_H_28(double *state, double *unused, double *out_8501847056895668998) {
  H_28(state, unused, out_8501847056895668998);
}
void car_h_31(double *state, double *unused, double *out_8775353408056983867) {
  h_31(state, unused, out_8775353408056983867);
}
void car_H_31(double *state, double *unused, double *out_814387052054175602) {
  H_31(state, unused, out_814387052054175602);
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
