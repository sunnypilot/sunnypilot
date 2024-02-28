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
void err_fun(double *nom_x, double *delta_x, double *out_6581031727810852793) {
   out_6581031727810852793[0] = delta_x[0] + nom_x[0];
   out_6581031727810852793[1] = delta_x[1] + nom_x[1];
   out_6581031727810852793[2] = delta_x[2] + nom_x[2];
   out_6581031727810852793[3] = delta_x[3] + nom_x[3];
   out_6581031727810852793[4] = delta_x[4] + nom_x[4];
   out_6581031727810852793[5] = delta_x[5] + nom_x[5];
   out_6581031727810852793[6] = delta_x[6] + nom_x[6];
   out_6581031727810852793[7] = delta_x[7] + nom_x[7];
   out_6581031727810852793[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_9157278643797334052) {
   out_9157278643797334052[0] = -nom_x[0] + true_x[0];
   out_9157278643797334052[1] = -nom_x[1] + true_x[1];
   out_9157278643797334052[2] = -nom_x[2] + true_x[2];
   out_9157278643797334052[3] = -nom_x[3] + true_x[3];
   out_9157278643797334052[4] = -nom_x[4] + true_x[4];
   out_9157278643797334052[5] = -nom_x[5] + true_x[5];
   out_9157278643797334052[6] = -nom_x[6] + true_x[6];
   out_9157278643797334052[7] = -nom_x[7] + true_x[7];
   out_9157278643797334052[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_493258648145988980) {
   out_493258648145988980[0] = 1.0;
   out_493258648145988980[1] = 0;
   out_493258648145988980[2] = 0;
   out_493258648145988980[3] = 0;
   out_493258648145988980[4] = 0;
   out_493258648145988980[5] = 0;
   out_493258648145988980[6] = 0;
   out_493258648145988980[7] = 0;
   out_493258648145988980[8] = 0;
   out_493258648145988980[9] = 0;
   out_493258648145988980[10] = 1.0;
   out_493258648145988980[11] = 0;
   out_493258648145988980[12] = 0;
   out_493258648145988980[13] = 0;
   out_493258648145988980[14] = 0;
   out_493258648145988980[15] = 0;
   out_493258648145988980[16] = 0;
   out_493258648145988980[17] = 0;
   out_493258648145988980[18] = 0;
   out_493258648145988980[19] = 0;
   out_493258648145988980[20] = 1.0;
   out_493258648145988980[21] = 0;
   out_493258648145988980[22] = 0;
   out_493258648145988980[23] = 0;
   out_493258648145988980[24] = 0;
   out_493258648145988980[25] = 0;
   out_493258648145988980[26] = 0;
   out_493258648145988980[27] = 0;
   out_493258648145988980[28] = 0;
   out_493258648145988980[29] = 0;
   out_493258648145988980[30] = 1.0;
   out_493258648145988980[31] = 0;
   out_493258648145988980[32] = 0;
   out_493258648145988980[33] = 0;
   out_493258648145988980[34] = 0;
   out_493258648145988980[35] = 0;
   out_493258648145988980[36] = 0;
   out_493258648145988980[37] = 0;
   out_493258648145988980[38] = 0;
   out_493258648145988980[39] = 0;
   out_493258648145988980[40] = 1.0;
   out_493258648145988980[41] = 0;
   out_493258648145988980[42] = 0;
   out_493258648145988980[43] = 0;
   out_493258648145988980[44] = 0;
   out_493258648145988980[45] = 0;
   out_493258648145988980[46] = 0;
   out_493258648145988980[47] = 0;
   out_493258648145988980[48] = 0;
   out_493258648145988980[49] = 0;
   out_493258648145988980[50] = 1.0;
   out_493258648145988980[51] = 0;
   out_493258648145988980[52] = 0;
   out_493258648145988980[53] = 0;
   out_493258648145988980[54] = 0;
   out_493258648145988980[55] = 0;
   out_493258648145988980[56] = 0;
   out_493258648145988980[57] = 0;
   out_493258648145988980[58] = 0;
   out_493258648145988980[59] = 0;
   out_493258648145988980[60] = 1.0;
   out_493258648145988980[61] = 0;
   out_493258648145988980[62] = 0;
   out_493258648145988980[63] = 0;
   out_493258648145988980[64] = 0;
   out_493258648145988980[65] = 0;
   out_493258648145988980[66] = 0;
   out_493258648145988980[67] = 0;
   out_493258648145988980[68] = 0;
   out_493258648145988980[69] = 0;
   out_493258648145988980[70] = 1.0;
   out_493258648145988980[71] = 0;
   out_493258648145988980[72] = 0;
   out_493258648145988980[73] = 0;
   out_493258648145988980[74] = 0;
   out_493258648145988980[75] = 0;
   out_493258648145988980[76] = 0;
   out_493258648145988980[77] = 0;
   out_493258648145988980[78] = 0;
   out_493258648145988980[79] = 0;
   out_493258648145988980[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_7646812063593062567) {
   out_7646812063593062567[0] = state[0];
   out_7646812063593062567[1] = state[1];
   out_7646812063593062567[2] = state[2];
   out_7646812063593062567[3] = state[3];
   out_7646812063593062567[4] = state[4];
   out_7646812063593062567[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8000000000000007*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_7646812063593062567[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_7646812063593062567[7] = state[7];
   out_7646812063593062567[8] = state[8];
}
void F_fun(double *state, double dt, double *out_8742539171151325573) {
   out_8742539171151325573[0] = 1;
   out_8742539171151325573[1] = 0;
   out_8742539171151325573[2] = 0;
   out_8742539171151325573[3] = 0;
   out_8742539171151325573[4] = 0;
   out_8742539171151325573[5] = 0;
   out_8742539171151325573[6] = 0;
   out_8742539171151325573[7] = 0;
   out_8742539171151325573[8] = 0;
   out_8742539171151325573[9] = 0;
   out_8742539171151325573[10] = 1;
   out_8742539171151325573[11] = 0;
   out_8742539171151325573[12] = 0;
   out_8742539171151325573[13] = 0;
   out_8742539171151325573[14] = 0;
   out_8742539171151325573[15] = 0;
   out_8742539171151325573[16] = 0;
   out_8742539171151325573[17] = 0;
   out_8742539171151325573[18] = 0;
   out_8742539171151325573[19] = 0;
   out_8742539171151325573[20] = 1;
   out_8742539171151325573[21] = 0;
   out_8742539171151325573[22] = 0;
   out_8742539171151325573[23] = 0;
   out_8742539171151325573[24] = 0;
   out_8742539171151325573[25] = 0;
   out_8742539171151325573[26] = 0;
   out_8742539171151325573[27] = 0;
   out_8742539171151325573[28] = 0;
   out_8742539171151325573[29] = 0;
   out_8742539171151325573[30] = 1;
   out_8742539171151325573[31] = 0;
   out_8742539171151325573[32] = 0;
   out_8742539171151325573[33] = 0;
   out_8742539171151325573[34] = 0;
   out_8742539171151325573[35] = 0;
   out_8742539171151325573[36] = 0;
   out_8742539171151325573[37] = 0;
   out_8742539171151325573[38] = 0;
   out_8742539171151325573[39] = 0;
   out_8742539171151325573[40] = 1;
   out_8742539171151325573[41] = 0;
   out_8742539171151325573[42] = 0;
   out_8742539171151325573[43] = 0;
   out_8742539171151325573[44] = 0;
   out_8742539171151325573[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_8742539171151325573[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_8742539171151325573[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_8742539171151325573[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_8742539171151325573[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_8742539171151325573[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_8742539171151325573[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_8742539171151325573[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_8742539171151325573[53] = -9.8000000000000007*dt;
   out_8742539171151325573[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_8742539171151325573[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_8742539171151325573[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_8742539171151325573[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_8742539171151325573[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_8742539171151325573[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_8742539171151325573[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_8742539171151325573[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_8742539171151325573[62] = 0;
   out_8742539171151325573[63] = 0;
   out_8742539171151325573[64] = 0;
   out_8742539171151325573[65] = 0;
   out_8742539171151325573[66] = 0;
   out_8742539171151325573[67] = 0;
   out_8742539171151325573[68] = 0;
   out_8742539171151325573[69] = 0;
   out_8742539171151325573[70] = 1;
   out_8742539171151325573[71] = 0;
   out_8742539171151325573[72] = 0;
   out_8742539171151325573[73] = 0;
   out_8742539171151325573[74] = 0;
   out_8742539171151325573[75] = 0;
   out_8742539171151325573[76] = 0;
   out_8742539171151325573[77] = 0;
   out_8742539171151325573[78] = 0;
   out_8742539171151325573[79] = 0;
   out_8742539171151325573[80] = 1;
}
void h_25(double *state, double *unused, double *out_8353939142913991519) {
   out_8353939142913991519[0] = state[6];
}
void H_25(double *state, double *unused, double *out_169381335348964671) {
   out_169381335348964671[0] = 0;
   out_169381335348964671[1] = 0;
   out_169381335348964671[2] = 0;
   out_169381335348964671[3] = 0;
   out_169381335348964671[4] = 0;
   out_169381335348964671[5] = 0;
   out_169381335348964671[6] = 1;
   out_169381335348964671[7] = 0;
   out_169381335348964671[8] = 0;
}
void h_24(double *state, double *unused, double *out_5452610352969860592) {
   out_5452610352969860592[0] = state[4];
   out_5452610352969860592[1] = state[5];
}
void H_24(double *state, double *unused, double *out_639838817392303395) {
   out_639838817392303395[0] = 0;
   out_639838817392303395[1] = 0;
   out_639838817392303395[2] = 0;
   out_639838817392303395[3] = 0;
   out_639838817392303395[4] = 1;
   out_639838817392303395[5] = 0;
   out_639838817392303395[6] = 0;
   out_639838817392303395[7] = 0;
   out_639838817392303395[8] = 0;
   out_639838817392303395[9] = 0;
   out_639838817392303395[10] = 0;
   out_639838817392303395[11] = 0;
   out_639838817392303395[12] = 0;
   out_639838817392303395[13] = 0;
   out_639838817392303395[14] = 1;
   out_639838817392303395[15] = 0;
   out_639838817392303395[16] = 0;
   out_639838817392303395[17] = 0;
}
void h_30(double *state, double *unused, double *out_3925690890824425794) {
   out_3925690890824425794[0] = state[4];
}
void H_30(double *state, double *unused, double *out_298720282492204741) {
   out_298720282492204741[0] = 0;
   out_298720282492204741[1] = 0;
   out_298720282492204741[2] = 0;
   out_298720282492204741[3] = 0;
   out_298720282492204741[4] = 1;
   out_298720282492204741[5] = 0;
   out_298720282492204741[6] = 0;
   out_298720282492204741[7] = 0;
   out_298720282492204741[8] = 0;
}
void h_26(double *state, double *unused, double *out_7264909465791674113) {
   out_7264909465791674113[0] = state[7];
}
void H_26(double *state, double *unused, double *out_3910884654223020895) {
   out_3910884654223020895[0] = 0;
   out_3910884654223020895[1] = 0;
   out_3910884654223020895[2] = 0;
   out_3910884654223020895[3] = 0;
   out_3910884654223020895[4] = 0;
   out_3910884654223020895[5] = 0;
   out_3910884654223020895[6] = 0;
   out_3910884654223020895[7] = 1;
   out_3910884654223020895[8] = 0;
}
void h_27(double *state, double *unused, double *out_3352265875253145874) {
   out_3352265875253145874[0] = state[3];
}
void H_27(double *state, double *unused, double *out_2473483594292629652) {
   out_2473483594292629652[0] = 0;
   out_2473483594292629652[1] = 0;
   out_2473483594292629652[2] = 0;
   out_2473483594292629652[3] = 1;
   out_2473483594292629652[4] = 0;
   out_2473483594292629652[5] = 0;
   out_2473483594292629652[6] = 0;
   out_2473483594292629652[7] = 0;
   out_2473483594292629652[8] = 0;
}
void h_29(double *state, double *unused, double *out_7201538703571882383) {
   out_7201538703571882383[0] = state[1];
}
void H_29(double *state, double *unused, double *out_4186846321162180685) {
   out_4186846321162180685[0] = 0;
   out_4186846321162180685[1] = 1;
   out_4186846321162180685[2] = 0;
   out_4186846321162180685[3] = 0;
   out_4186846321162180685[4] = 0;
   out_4186846321162180685[5] = 0;
   out_4186846321162180685[6] = 0;
   out_4186846321162180685[7] = 0;
   out_4186846321162180685[8] = 0;
}
void h_28(double *state, double *unused, double *out_1649407392407699771) {
   out_1649407392407699771[0] = state[0];
}
void H_28(double *state, double *unused, double *out_9177498735477840357) {
   out_9177498735477840357[0] = 1;
   out_9177498735477840357[1] = 0;
   out_9177498735477840357[2] = 0;
   out_9177498735477840357[3] = 0;
   out_9177498735477840357[4] = 0;
   out_9177498735477840357[5] = 0;
   out_9177498735477840357[6] = 0;
   out_9177498735477840357[7] = 0;
   out_9177498735477840357[8] = 0;
}
void h_31(double *state, double *unused, double *out_6455355402541537747) {
   out_6455355402541537747[0] = state[8];
}
void H_31(double *state, double *unused, double *out_138735373472004243) {
   out_138735373472004243[0] = 0;
   out_138735373472004243[1] = 0;
   out_138735373472004243[2] = 0;
   out_138735373472004243[3] = 0;
   out_138735373472004243[4] = 0;
   out_138735373472004243[5] = 0;
   out_138735373472004243[6] = 0;
   out_138735373472004243[7] = 0;
   out_138735373472004243[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_6581031727810852793) {
  err_fun(nom_x, delta_x, out_6581031727810852793);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_9157278643797334052) {
  inv_err_fun(nom_x, true_x, out_9157278643797334052);
}
void car_H_mod_fun(double *state, double *out_493258648145988980) {
  H_mod_fun(state, out_493258648145988980);
}
void car_f_fun(double *state, double dt, double *out_7646812063593062567) {
  f_fun(state,  dt, out_7646812063593062567);
}
void car_F_fun(double *state, double dt, double *out_8742539171151325573) {
  F_fun(state,  dt, out_8742539171151325573);
}
void car_h_25(double *state, double *unused, double *out_8353939142913991519) {
  h_25(state, unused, out_8353939142913991519);
}
void car_H_25(double *state, double *unused, double *out_169381335348964671) {
  H_25(state, unused, out_169381335348964671);
}
void car_h_24(double *state, double *unused, double *out_5452610352969860592) {
  h_24(state, unused, out_5452610352969860592);
}
void car_H_24(double *state, double *unused, double *out_639838817392303395) {
  H_24(state, unused, out_639838817392303395);
}
void car_h_30(double *state, double *unused, double *out_3925690890824425794) {
  h_30(state, unused, out_3925690890824425794);
}
void car_H_30(double *state, double *unused, double *out_298720282492204741) {
  H_30(state, unused, out_298720282492204741);
}
void car_h_26(double *state, double *unused, double *out_7264909465791674113) {
  h_26(state, unused, out_7264909465791674113);
}
void car_H_26(double *state, double *unused, double *out_3910884654223020895) {
  H_26(state, unused, out_3910884654223020895);
}
void car_h_27(double *state, double *unused, double *out_3352265875253145874) {
  h_27(state, unused, out_3352265875253145874);
}
void car_H_27(double *state, double *unused, double *out_2473483594292629652) {
  H_27(state, unused, out_2473483594292629652);
}
void car_h_29(double *state, double *unused, double *out_7201538703571882383) {
  h_29(state, unused, out_7201538703571882383);
}
void car_H_29(double *state, double *unused, double *out_4186846321162180685) {
  H_29(state, unused, out_4186846321162180685);
}
void car_h_28(double *state, double *unused, double *out_1649407392407699771) {
  h_28(state, unused, out_1649407392407699771);
}
void car_H_28(double *state, double *unused, double *out_9177498735477840357) {
  H_28(state, unused, out_9177498735477840357);
}
void car_h_31(double *state, double *unused, double *out_6455355402541537747) {
  h_31(state, unused, out_6455355402541537747);
}
void car_H_31(double *state, double *unused, double *out_138735373472004243) {
  H_31(state, unused, out_138735373472004243);
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
