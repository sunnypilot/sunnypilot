#include "gnss.h"

namespace {
#define DIM 11
#define EDIM 11
#define MEDIM 11
typedef void (*Hfun)(double *, double *, double *);
const static double MAHA_THRESH_6 = 3.8414588206941227;
const static double MAHA_THRESH_20 = 3.8414588206941227;
const static double MAHA_THRESH_7 = 3.8414588206941227;
const static double MAHA_THRESH_21 = 3.8414588206941227;

/******************************************************************************
 *                       Code generated with SymPy 1.12                       *
 *                                                                            *
 *              See http://www.sympy.org/ for more information.               *
 *                                                                            *
 *                         This file is part of 'ekf'                         *
 ******************************************************************************/
void err_fun(double *nom_x, double *delta_x, double *out_7759149317582249240) {
   out_7759149317582249240[0] = delta_x[0] + nom_x[0];
   out_7759149317582249240[1] = delta_x[1] + nom_x[1];
   out_7759149317582249240[2] = delta_x[2] + nom_x[2];
   out_7759149317582249240[3] = delta_x[3] + nom_x[3];
   out_7759149317582249240[4] = delta_x[4] + nom_x[4];
   out_7759149317582249240[5] = delta_x[5] + nom_x[5];
   out_7759149317582249240[6] = delta_x[6] + nom_x[6];
   out_7759149317582249240[7] = delta_x[7] + nom_x[7];
   out_7759149317582249240[8] = delta_x[8] + nom_x[8];
   out_7759149317582249240[9] = delta_x[9] + nom_x[9];
   out_7759149317582249240[10] = delta_x[10] + nom_x[10];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_9118422902961757933) {
   out_9118422902961757933[0] = -nom_x[0] + true_x[0];
   out_9118422902961757933[1] = -nom_x[1] + true_x[1];
   out_9118422902961757933[2] = -nom_x[2] + true_x[2];
   out_9118422902961757933[3] = -nom_x[3] + true_x[3];
   out_9118422902961757933[4] = -nom_x[4] + true_x[4];
   out_9118422902961757933[5] = -nom_x[5] + true_x[5];
   out_9118422902961757933[6] = -nom_x[6] + true_x[6];
   out_9118422902961757933[7] = -nom_x[7] + true_x[7];
   out_9118422902961757933[8] = -nom_x[8] + true_x[8];
   out_9118422902961757933[9] = -nom_x[9] + true_x[9];
   out_9118422902961757933[10] = -nom_x[10] + true_x[10];
}
void H_mod_fun(double *state, double *out_1633358768098501879) {
   out_1633358768098501879[0] = 1.0;
   out_1633358768098501879[1] = 0;
   out_1633358768098501879[2] = 0;
   out_1633358768098501879[3] = 0;
   out_1633358768098501879[4] = 0;
   out_1633358768098501879[5] = 0;
   out_1633358768098501879[6] = 0;
   out_1633358768098501879[7] = 0;
   out_1633358768098501879[8] = 0;
   out_1633358768098501879[9] = 0;
   out_1633358768098501879[10] = 0;
   out_1633358768098501879[11] = 0;
   out_1633358768098501879[12] = 1.0;
   out_1633358768098501879[13] = 0;
   out_1633358768098501879[14] = 0;
   out_1633358768098501879[15] = 0;
   out_1633358768098501879[16] = 0;
   out_1633358768098501879[17] = 0;
   out_1633358768098501879[18] = 0;
   out_1633358768098501879[19] = 0;
   out_1633358768098501879[20] = 0;
   out_1633358768098501879[21] = 0;
   out_1633358768098501879[22] = 0;
   out_1633358768098501879[23] = 0;
   out_1633358768098501879[24] = 1.0;
   out_1633358768098501879[25] = 0;
   out_1633358768098501879[26] = 0;
   out_1633358768098501879[27] = 0;
   out_1633358768098501879[28] = 0;
   out_1633358768098501879[29] = 0;
   out_1633358768098501879[30] = 0;
   out_1633358768098501879[31] = 0;
   out_1633358768098501879[32] = 0;
   out_1633358768098501879[33] = 0;
   out_1633358768098501879[34] = 0;
   out_1633358768098501879[35] = 0;
   out_1633358768098501879[36] = 1.0;
   out_1633358768098501879[37] = 0;
   out_1633358768098501879[38] = 0;
   out_1633358768098501879[39] = 0;
   out_1633358768098501879[40] = 0;
   out_1633358768098501879[41] = 0;
   out_1633358768098501879[42] = 0;
   out_1633358768098501879[43] = 0;
   out_1633358768098501879[44] = 0;
   out_1633358768098501879[45] = 0;
   out_1633358768098501879[46] = 0;
   out_1633358768098501879[47] = 0;
   out_1633358768098501879[48] = 1.0;
   out_1633358768098501879[49] = 0;
   out_1633358768098501879[50] = 0;
   out_1633358768098501879[51] = 0;
   out_1633358768098501879[52] = 0;
   out_1633358768098501879[53] = 0;
   out_1633358768098501879[54] = 0;
   out_1633358768098501879[55] = 0;
   out_1633358768098501879[56] = 0;
   out_1633358768098501879[57] = 0;
   out_1633358768098501879[58] = 0;
   out_1633358768098501879[59] = 0;
   out_1633358768098501879[60] = 1.0;
   out_1633358768098501879[61] = 0;
   out_1633358768098501879[62] = 0;
   out_1633358768098501879[63] = 0;
   out_1633358768098501879[64] = 0;
   out_1633358768098501879[65] = 0;
   out_1633358768098501879[66] = 0;
   out_1633358768098501879[67] = 0;
   out_1633358768098501879[68] = 0;
   out_1633358768098501879[69] = 0;
   out_1633358768098501879[70] = 0;
   out_1633358768098501879[71] = 0;
   out_1633358768098501879[72] = 1.0;
   out_1633358768098501879[73] = 0;
   out_1633358768098501879[74] = 0;
   out_1633358768098501879[75] = 0;
   out_1633358768098501879[76] = 0;
   out_1633358768098501879[77] = 0;
   out_1633358768098501879[78] = 0;
   out_1633358768098501879[79] = 0;
   out_1633358768098501879[80] = 0;
   out_1633358768098501879[81] = 0;
   out_1633358768098501879[82] = 0;
   out_1633358768098501879[83] = 0;
   out_1633358768098501879[84] = 1.0;
   out_1633358768098501879[85] = 0;
   out_1633358768098501879[86] = 0;
   out_1633358768098501879[87] = 0;
   out_1633358768098501879[88] = 0;
   out_1633358768098501879[89] = 0;
   out_1633358768098501879[90] = 0;
   out_1633358768098501879[91] = 0;
   out_1633358768098501879[92] = 0;
   out_1633358768098501879[93] = 0;
   out_1633358768098501879[94] = 0;
   out_1633358768098501879[95] = 0;
   out_1633358768098501879[96] = 1.0;
   out_1633358768098501879[97] = 0;
   out_1633358768098501879[98] = 0;
   out_1633358768098501879[99] = 0;
   out_1633358768098501879[100] = 0;
   out_1633358768098501879[101] = 0;
   out_1633358768098501879[102] = 0;
   out_1633358768098501879[103] = 0;
   out_1633358768098501879[104] = 0;
   out_1633358768098501879[105] = 0;
   out_1633358768098501879[106] = 0;
   out_1633358768098501879[107] = 0;
   out_1633358768098501879[108] = 1.0;
   out_1633358768098501879[109] = 0;
   out_1633358768098501879[110] = 0;
   out_1633358768098501879[111] = 0;
   out_1633358768098501879[112] = 0;
   out_1633358768098501879[113] = 0;
   out_1633358768098501879[114] = 0;
   out_1633358768098501879[115] = 0;
   out_1633358768098501879[116] = 0;
   out_1633358768098501879[117] = 0;
   out_1633358768098501879[118] = 0;
   out_1633358768098501879[119] = 0;
   out_1633358768098501879[120] = 1.0;
}
void f_fun(double *state, double dt, double *out_436651591053660649) {
   out_436651591053660649[0] = dt*state[3] + state[0];
   out_436651591053660649[1] = dt*state[4] + state[1];
   out_436651591053660649[2] = dt*state[5] + state[2];
   out_436651591053660649[3] = state[3];
   out_436651591053660649[4] = state[4];
   out_436651591053660649[5] = state[5];
   out_436651591053660649[6] = dt*state[7] + state[6];
   out_436651591053660649[7] = dt*state[8] + state[7];
   out_436651591053660649[8] = state[8];
   out_436651591053660649[9] = state[9];
   out_436651591053660649[10] = state[10];
}
void F_fun(double *state, double dt, double *out_7304280096771648861) {
   out_7304280096771648861[0] = 1;
   out_7304280096771648861[1] = 0;
   out_7304280096771648861[2] = 0;
   out_7304280096771648861[3] = dt;
   out_7304280096771648861[4] = 0;
   out_7304280096771648861[5] = 0;
   out_7304280096771648861[6] = 0;
   out_7304280096771648861[7] = 0;
   out_7304280096771648861[8] = 0;
   out_7304280096771648861[9] = 0;
   out_7304280096771648861[10] = 0;
   out_7304280096771648861[11] = 0;
   out_7304280096771648861[12] = 1;
   out_7304280096771648861[13] = 0;
   out_7304280096771648861[14] = 0;
   out_7304280096771648861[15] = dt;
   out_7304280096771648861[16] = 0;
   out_7304280096771648861[17] = 0;
   out_7304280096771648861[18] = 0;
   out_7304280096771648861[19] = 0;
   out_7304280096771648861[20] = 0;
   out_7304280096771648861[21] = 0;
   out_7304280096771648861[22] = 0;
   out_7304280096771648861[23] = 0;
   out_7304280096771648861[24] = 1;
   out_7304280096771648861[25] = 0;
   out_7304280096771648861[26] = 0;
   out_7304280096771648861[27] = dt;
   out_7304280096771648861[28] = 0;
   out_7304280096771648861[29] = 0;
   out_7304280096771648861[30] = 0;
   out_7304280096771648861[31] = 0;
   out_7304280096771648861[32] = 0;
   out_7304280096771648861[33] = 0;
   out_7304280096771648861[34] = 0;
   out_7304280096771648861[35] = 0;
   out_7304280096771648861[36] = 1;
   out_7304280096771648861[37] = 0;
   out_7304280096771648861[38] = 0;
   out_7304280096771648861[39] = 0;
   out_7304280096771648861[40] = 0;
   out_7304280096771648861[41] = 0;
   out_7304280096771648861[42] = 0;
   out_7304280096771648861[43] = 0;
   out_7304280096771648861[44] = 0;
   out_7304280096771648861[45] = 0;
   out_7304280096771648861[46] = 0;
   out_7304280096771648861[47] = 0;
   out_7304280096771648861[48] = 1;
   out_7304280096771648861[49] = 0;
   out_7304280096771648861[50] = 0;
   out_7304280096771648861[51] = 0;
   out_7304280096771648861[52] = 0;
   out_7304280096771648861[53] = 0;
   out_7304280096771648861[54] = 0;
   out_7304280096771648861[55] = 0;
   out_7304280096771648861[56] = 0;
   out_7304280096771648861[57] = 0;
   out_7304280096771648861[58] = 0;
   out_7304280096771648861[59] = 0;
   out_7304280096771648861[60] = 1;
   out_7304280096771648861[61] = 0;
   out_7304280096771648861[62] = 0;
   out_7304280096771648861[63] = 0;
   out_7304280096771648861[64] = 0;
   out_7304280096771648861[65] = 0;
   out_7304280096771648861[66] = 0;
   out_7304280096771648861[67] = 0;
   out_7304280096771648861[68] = 0;
   out_7304280096771648861[69] = 0;
   out_7304280096771648861[70] = 0;
   out_7304280096771648861[71] = 0;
   out_7304280096771648861[72] = 1;
   out_7304280096771648861[73] = dt;
   out_7304280096771648861[74] = 0;
   out_7304280096771648861[75] = 0;
   out_7304280096771648861[76] = 0;
   out_7304280096771648861[77] = 0;
   out_7304280096771648861[78] = 0;
   out_7304280096771648861[79] = 0;
   out_7304280096771648861[80] = 0;
   out_7304280096771648861[81] = 0;
   out_7304280096771648861[82] = 0;
   out_7304280096771648861[83] = 0;
   out_7304280096771648861[84] = 1;
   out_7304280096771648861[85] = dt;
   out_7304280096771648861[86] = 0;
   out_7304280096771648861[87] = 0;
   out_7304280096771648861[88] = 0;
   out_7304280096771648861[89] = 0;
   out_7304280096771648861[90] = 0;
   out_7304280096771648861[91] = 0;
   out_7304280096771648861[92] = 0;
   out_7304280096771648861[93] = 0;
   out_7304280096771648861[94] = 0;
   out_7304280096771648861[95] = 0;
   out_7304280096771648861[96] = 1;
   out_7304280096771648861[97] = 0;
   out_7304280096771648861[98] = 0;
   out_7304280096771648861[99] = 0;
   out_7304280096771648861[100] = 0;
   out_7304280096771648861[101] = 0;
   out_7304280096771648861[102] = 0;
   out_7304280096771648861[103] = 0;
   out_7304280096771648861[104] = 0;
   out_7304280096771648861[105] = 0;
   out_7304280096771648861[106] = 0;
   out_7304280096771648861[107] = 0;
   out_7304280096771648861[108] = 1;
   out_7304280096771648861[109] = 0;
   out_7304280096771648861[110] = 0;
   out_7304280096771648861[111] = 0;
   out_7304280096771648861[112] = 0;
   out_7304280096771648861[113] = 0;
   out_7304280096771648861[114] = 0;
   out_7304280096771648861[115] = 0;
   out_7304280096771648861[116] = 0;
   out_7304280096771648861[117] = 0;
   out_7304280096771648861[118] = 0;
   out_7304280096771648861[119] = 0;
   out_7304280096771648861[120] = 1;
}
void h_6(double *state, double *sat_pos, double *out_4764504202269866901) {
   out_4764504202269866901[0] = sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2)) + state[6];
}
void H_6(double *state, double *sat_pos, double *out_4085363850207817832) {
   out_4085363850207817832[0] = (-sat_pos[0] + state[0])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_4085363850207817832[1] = (-sat_pos[1] + state[1])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_4085363850207817832[2] = (-sat_pos[2] + state[2])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_4085363850207817832[3] = 0;
   out_4085363850207817832[4] = 0;
   out_4085363850207817832[5] = 0;
   out_4085363850207817832[6] = 1;
   out_4085363850207817832[7] = 0;
   out_4085363850207817832[8] = 0;
   out_4085363850207817832[9] = 0;
   out_4085363850207817832[10] = 0;
}
void h_20(double *state, double *sat_pos, double *out_6801986365944636663) {
   out_6801986365944636663[0] = sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2)) + sat_pos[3]*state[10] + state[6] + state[9];
}
void H_20(double *state, double *sat_pos, double *out_7866410108663176377) {
   out_7866410108663176377[0] = (-sat_pos[0] + state[0])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_7866410108663176377[1] = (-sat_pos[1] + state[1])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_7866410108663176377[2] = (-sat_pos[2] + state[2])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_7866410108663176377[3] = 0;
   out_7866410108663176377[4] = 0;
   out_7866410108663176377[5] = 0;
   out_7866410108663176377[6] = 1;
   out_7866410108663176377[7] = 0;
   out_7866410108663176377[8] = 0;
   out_7866410108663176377[9] = 1;
   out_7866410108663176377[10] = sat_pos[3];
}
void h_7(double *state, double *sat_pos_vel, double *out_4005211607259102508) {
   out_4005211607259102508[0] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[3] - state[3])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[4] - state[4])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + (sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + state[7];
}
void H_7(double *state, double *sat_pos_vel, double *out_2701243593729319356) {
   out_2701243593729319356[0] = pow(sat_pos_vel[0] - state[0], 2)*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[0] - state[0])*(sat_pos_vel[1] - state[1])*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[0] - state[0])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[3] - state[3])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_2701243593729319356[1] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[1] - state[1])*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + pow(sat_pos_vel[1] - state[1], 2)*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[4] - state[4])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_2701243593729319356[2] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + pow(sat_pos_vel[2] - state[2], 2)*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[5] - state[5])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_2701243593729319356[3] = -(sat_pos_vel[0] - state[0])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_2701243593729319356[4] = -(sat_pos_vel[1] - state[1])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_2701243593729319356[5] = -(sat_pos_vel[2] - state[2])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_2701243593729319356[6] = 0;
   out_2701243593729319356[7] = 1;
   out_2701243593729319356[8] = 0;
   out_2701243593729319356[9] = 0;
   out_2701243593729319356[10] = 0;
}
void h_21(double *state, double *sat_pos_vel, double *out_4005211607259102508) {
   out_4005211607259102508[0] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[3] - state[3])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[4] - state[4])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + (sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + state[7];
}
void H_21(double *state, double *sat_pos_vel, double *out_2701243593729319356) {
   out_2701243593729319356[0] = pow(sat_pos_vel[0] - state[0], 2)*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[0] - state[0])*(sat_pos_vel[1] - state[1])*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[0] - state[0])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[3] - state[3])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_2701243593729319356[1] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[1] - state[1])*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + pow(sat_pos_vel[1] - state[1], 2)*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[4] - state[4])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_2701243593729319356[2] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + pow(sat_pos_vel[2] - state[2], 2)*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[5] - state[5])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_2701243593729319356[3] = -(sat_pos_vel[0] - state[0])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_2701243593729319356[4] = -(sat_pos_vel[1] - state[1])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_2701243593729319356[5] = -(sat_pos_vel[2] - state[2])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_2701243593729319356[6] = 0;
   out_2701243593729319356[7] = 1;
   out_2701243593729319356[8] = 0;
   out_2701243593729319356[9] = 0;
   out_2701243593729319356[10] = 0;
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

void gnss_update_6(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<1, 3, 0>(in_x, in_P, h_6, H_6, NULL, in_z, in_R, in_ea, MAHA_THRESH_6);
}
void gnss_update_20(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<1, 3, 0>(in_x, in_P, h_20, H_20, NULL, in_z, in_R, in_ea, MAHA_THRESH_20);
}
void gnss_update_7(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<1, 3, 0>(in_x, in_P, h_7, H_7, NULL, in_z, in_R, in_ea, MAHA_THRESH_7);
}
void gnss_update_21(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<1, 3, 0>(in_x, in_P, h_21, H_21, NULL, in_z, in_R, in_ea, MAHA_THRESH_21);
}
void gnss_err_fun(double *nom_x, double *delta_x, double *out_7759149317582249240) {
  err_fun(nom_x, delta_x, out_7759149317582249240);
}
void gnss_inv_err_fun(double *nom_x, double *true_x, double *out_9118422902961757933) {
  inv_err_fun(nom_x, true_x, out_9118422902961757933);
}
void gnss_H_mod_fun(double *state, double *out_1633358768098501879) {
  H_mod_fun(state, out_1633358768098501879);
}
void gnss_f_fun(double *state, double dt, double *out_436651591053660649) {
  f_fun(state,  dt, out_436651591053660649);
}
void gnss_F_fun(double *state, double dt, double *out_7304280096771648861) {
  F_fun(state,  dt, out_7304280096771648861);
}
void gnss_h_6(double *state, double *sat_pos, double *out_4764504202269866901) {
  h_6(state, sat_pos, out_4764504202269866901);
}
void gnss_H_6(double *state, double *sat_pos, double *out_4085363850207817832) {
  H_6(state, sat_pos, out_4085363850207817832);
}
void gnss_h_20(double *state, double *sat_pos, double *out_6801986365944636663) {
  h_20(state, sat_pos, out_6801986365944636663);
}
void gnss_H_20(double *state, double *sat_pos, double *out_7866410108663176377) {
  H_20(state, sat_pos, out_7866410108663176377);
}
void gnss_h_7(double *state, double *sat_pos_vel, double *out_4005211607259102508) {
  h_7(state, sat_pos_vel, out_4005211607259102508);
}
void gnss_H_7(double *state, double *sat_pos_vel, double *out_2701243593729319356) {
  H_7(state, sat_pos_vel, out_2701243593729319356);
}
void gnss_h_21(double *state, double *sat_pos_vel, double *out_4005211607259102508) {
  h_21(state, sat_pos_vel, out_4005211607259102508);
}
void gnss_H_21(double *state, double *sat_pos_vel, double *out_2701243593729319356) {
  H_21(state, sat_pos_vel, out_2701243593729319356);
}
void gnss_predict(double *in_x, double *in_P, double *in_Q, double dt) {
  predict(in_x, in_P, in_Q, dt);
}
}

const EKF gnss = {
  .name = "gnss",
  .kinds = { 6, 20, 7, 21 },
  .feature_kinds = {  },
  .f_fun = gnss_f_fun,
  .F_fun = gnss_F_fun,
  .err_fun = gnss_err_fun,
  .inv_err_fun = gnss_inv_err_fun,
  .H_mod_fun = gnss_H_mod_fun,
  .predict = gnss_predict,
  .hs = {
    { 6, gnss_h_6 },
    { 20, gnss_h_20 },
    { 7, gnss_h_7 },
    { 21, gnss_h_21 },
  },
  .Hs = {
    { 6, gnss_H_6 },
    { 20, gnss_H_20 },
    { 7, gnss_H_7 },
    { 21, gnss_H_21 },
  },
  .updates = {
    { 6, gnss_update_6 },
    { 20, gnss_update_20 },
    { 7, gnss_update_7 },
    { 21, gnss_update_21 },
  },
  .Hes = {
  },
  .sets = {
  },
  .extra_routines = {
  },
};

ekf_init(gnss);
