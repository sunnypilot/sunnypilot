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
void err_fun(double *nom_x, double *delta_x, double *out_3532684675618107860) {
   out_3532684675618107860[0] = delta_x[0] + nom_x[0];
   out_3532684675618107860[1] = delta_x[1] + nom_x[1];
   out_3532684675618107860[2] = delta_x[2] + nom_x[2];
   out_3532684675618107860[3] = delta_x[3] + nom_x[3];
   out_3532684675618107860[4] = delta_x[4] + nom_x[4];
   out_3532684675618107860[5] = delta_x[5] + nom_x[5];
   out_3532684675618107860[6] = delta_x[6] + nom_x[6];
   out_3532684675618107860[7] = delta_x[7] + nom_x[7];
   out_3532684675618107860[8] = delta_x[8] + nom_x[8];
   out_3532684675618107860[9] = delta_x[9] + nom_x[9];
   out_3532684675618107860[10] = delta_x[10] + nom_x[10];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_4040997643746645524) {
   out_4040997643746645524[0] = -nom_x[0] + true_x[0];
   out_4040997643746645524[1] = -nom_x[1] + true_x[1];
   out_4040997643746645524[2] = -nom_x[2] + true_x[2];
   out_4040997643746645524[3] = -nom_x[3] + true_x[3];
   out_4040997643746645524[4] = -nom_x[4] + true_x[4];
   out_4040997643746645524[5] = -nom_x[5] + true_x[5];
   out_4040997643746645524[6] = -nom_x[6] + true_x[6];
   out_4040997643746645524[7] = -nom_x[7] + true_x[7];
   out_4040997643746645524[8] = -nom_x[8] + true_x[8];
   out_4040997643746645524[9] = -nom_x[9] + true_x[9];
   out_4040997643746645524[10] = -nom_x[10] + true_x[10];
}
void H_mod_fun(double *state, double *out_5907768448464933327) {
   out_5907768448464933327[0] = 1.0;
   out_5907768448464933327[1] = 0;
   out_5907768448464933327[2] = 0;
   out_5907768448464933327[3] = 0;
   out_5907768448464933327[4] = 0;
   out_5907768448464933327[5] = 0;
   out_5907768448464933327[6] = 0;
   out_5907768448464933327[7] = 0;
   out_5907768448464933327[8] = 0;
   out_5907768448464933327[9] = 0;
   out_5907768448464933327[10] = 0;
   out_5907768448464933327[11] = 0;
   out_5907768448464933327[12] = 1.0;
   out_5907768448464933327[13] = 0;
   out_5907768448464933327[14] = 0;
   out_5907768448464933327[15] = 0;
   out_5907768448464933327[16] = 0;
   out_5907768448464933327[17] = 0;
   out_5907768448464933327[18] = 0;
   out_5907768448464933327[19] = 0;
   out_5907768448464933327[20] = 0;
   out_5907768448464933327[21] = 0;
   out_5907768448464933327[22] = 0;
   out_5907768448464933327[23] = 0;
   out_5907768448464933327[24] = 1.0;
   out_5907768448464933327[25] = 0;
   out_5907768448464933327[26] = 0;
   out_5907768448464933327[27] = 0;
   out_5907768448464933327[28] = 0;
   out_5907768448464933327[29] = 0;
   out_5907768448464933327[30] = 0;
   out_5907768448464933327[31] = 0;
   out_5907768448464933327[32] = 0;
   out_5907768448464933327[33] = 0;
   out_5907768448464933327[34] = 0;
   out_5907768448464933327[35] = 0;
   out_5907768448464933327[36] = 1.0;
   out_5907768448464933327[37] = 0;
   out_5907768448464933327[38] = 0;
   out_5907768448464933327[39] = 0;
   out_5907768448464933327[40] = 0;
   out_5907768448464933327[41] = 0;
   out_5907768448464933327[42] = 0;
   out_5907768448464933327[43] = 0;
   out_5907768448464933327[44] = 0;
   out_5907768448464933327[45] = 0;
   out_5907768448464933327[46] = 0;
   out_5907768448464933327[47] = 0;
   out_5907768448464933327[48] = 1.0;
   out_5907768448464933327[49] = 0;
   out_5907768448464933327[50] = 0;
   out_5907768448464933327[51] = 0;
   out_5907768448464933327[52] = 0;
   out_5907768448464933327[53] = 0;
   out_5907768448464933327[54] = 0;
   out_5907768448464933327[55] = 0;
   out_5907768448464933327[56] = 0;
   out_5907768448464933327[57] = 0;
   out_5907768448464933327[58] = 0;
   out_5907768448464933327[59] = 0;
   out_5907768448464933327[60] = 1.0;
   out_5907768448464933327[61] = 0;
   out_5907768448464933327[62] = 0;
   out_5907768448464933327[63] = 0;
   out_5907768448464933327[64] = 0;
   out_5907768448464933327[65] = 0;
   out_5907768448464933327[66] = 0;
   out_5907768448464933327[67] = 0;
   out_5907768448464933327[68] = 0;
   out_5907768448464933327[69] = 0;
   out_5907768448464933327[70] = 0;
   out_5907768448464933327[71] = 0;
   out_5907768448464933327[72] = 1.0;
   out_5907768448464933327[73] = 0;
   out_5907768448464933327[74] = 0;
   out_5907768448464933327[75] = 0;
   out_5907768448464933327[76] = 0;
   out_5907768448464933327[77] = 0;
   out_5907768448464933327[78] = 0;
   out_5907768448464933327[79] = 0;
   out_5907768448464933327[80] = 0;
   out_5907768448464933327[81] = 0;
   out_5907768448464933327[82] = 0;
   out_5907768448464933327[83] = 0;
   out_5907768448464933327[84] = 1.0;
   out_5907768448464933327[85] = 0;
   out_5907768448464933327[86] = 0;
   out_5907768448464933327[87] = 0;
   out_5907768448464933327[88] = 0;
   out_5907768448464933327[89] = 0;
   out_5907768448464933327[90] = 0;
   out_5907768448464933327[91] = 0;
   out_5907768448464933327[92] = 0;
   out_5907768448464933327[93] = 0;
   out_5907768448464933327[94] = 0;
   out_5907768448464933327[95] = 0;
   out_5907768448464933327[96] = 1.0;
   out_5907768448464933327[97] = 0;
   out_5907768448464933327[98] = 0;
   out_5907768448464933327[99] = 0;
   out_5907768448464933327[100] = 0;
   out_5907768448464933327[101] = 0;
   out_5907768448464933327[102] = 0;
   out_5907768448464933327[103] = 0;
   out_5907768448464933327[104] = 0;
   out_5907768448464933327[105] = 0;
   out_5907768448464933327[106] = 0;
   out_5907768448464933327[107] = 0;
   out_5907768448464933327[108] = 1.0;
   out_5907768448464933327[109] = 0;
   out_5907768448464933327[110] = 0;
   out_5907768448464933327[111] = 0;
   out_5907768448464933327[112] = 0;
   out_5907768448464933327[113] = 0;
   out_5907768448464933327[114] = 0;
   out_5907768448464933327[115] = 0;
   out_5907768448464933327[116] = 0;
   out_5907768448464933327[117] = 0;
   out_5907768448464933327[118] = 0;
   out_5907768448464933327[119] = 0;
   out_5907768448464933327[120] = 1.0;
}
void f_fun(double *state, double dt, double *out_8719739038902116923) {
   out_8719739038902116923[0] = dt*state[3] + state[0];
   out_8719739038902116923[1] = dt*state[4] + state[1];
   out_8719739038902116923[2] = dt*state[5] + state[2];
   out_8719739038902116923[3] = state[3];
   out_8719739038902116923[4] = state[4];
   out_8719739038902116923[5] = state[5];
   out_8719739038902116923[6] = dt*state[7] + state[6];
   out_8719739038902116923[7] = dt*state[8] + state[7];
   out_8719739038902116923[8] = state[8];
   out_8719739038902116923[9] = state[9];
   out_8719739038902116923[10] = state[10];
}
void F_fun(double *state, double dt, double *out_6368958041110140577) {
   out_6368958041110140577[0] = 1;
   out_6368958041110140577[1] = 0;
   out_6368958041110140577[2] = 0;
   out_6368958041110140577[3] = dt;
   out_6368958041110140577[4] = 0;
   out_6368958041110140577[5] = 0;
   out_6368958041110140577[6] = 0;
   out_6368958041110140577[7] = 0;
   out_6368958041110140577[8] = 0;
   out_6368958041110140577[9] = 0;
   out_6368958041110140577[10] = 0;
   out_6368958041110140577[11] = 0;
   out_6368958041110140577[12] = 1;
   out_6368958041110140577[13] = 0;
   out_6368958041110140577[14] = 0;
   out_6368958041110140577[15] = dt;
   out_6368958041110140577[16] = 0;
   out_6368958041110140577[17] = 0;
   out_6368958041110140577[18] = 0;
   out_6368958041110140577[19] = 0;
   out_6368958041110140577[20] = 0;
   out_6368958041110140577[21] = 0;
   out_6368958041110140577[22] = 0;
   out_6368958041110140577[23] = 0;
   out_6368958041110140577[24] = 1;
   out_6368958041110140577[25] = 0;
   out_6368958041110140577[26] = 0;
   out_6368958041110140577[27] = dt;
   out_6368958041110140577[28] = 0;
   out_6368958041110140577[29] = 0;
   out_6368958041110140577[30] = 0;
   out_6368958041110140577[31] = 0;
   out_6368958041110140577[32] = 0;
   out_6368958041110140577[33] = 0;
   out_6368958041110140577[34] = 0;
   out_6368958041110140577[35] = 0;
   out_6368958041110140577[36] = 1;
   out_6368958041110140577[37] = 0;
   out_6368958041110140577[38] = 0;
   out_6368958041110140577[39] = 0;
   out_6368958041110140577[40] = 0;
   out_6368958041110140577[41] = 0;
   out_6368958041110140577[42] = 0;
   out_6368958041110140577[43] = 0;
   out_6368958041110140577[44] = 0;
   out_6368958041110140577[45] = 0;
   out_6368958041110140577[46] = 0;
   out_6368958041110140577[47] = 0;
   out_6368958041110140577[48] = 1;
   out_6368958041110140577[49] = 0;
   out_6368958041110140577[50] = 0;
   out_6368958041110140577[51] = 0;
   out_6368958041110140577[52] = 0;
   out_6368958041110140577[53] = 0;
   out_6368958041110140577[54] = 0;
   out_6368958041110140577[55] = 0;
   out_6368958041110140577[56] = 0;
   out_6368958041110140577[57] = 0;
   out_6368958041110140577[58] = 0;
   out_6368958041110140577[59] = 0;
   out_6368958041110140577[60] = 1;
   out_6368958041110140577[61] = 0;
   out_6368958041110140577[62] = 0;
   out_6368958041110140577[63] = 0;
   out_6368958041110140577[64] = 0;
   out_6368958041110140577[65] = 0;
   out_6368958041110140577[66] = 0;
   out_6368958041110140577[67] = 0;
   out_6368958041110140577[68] = 0;
   out_6368958041110140577[69] = 0;
   out_6368958041110140577[70] = 0;
   out_6368958041110140577[71] = 0;
   out_6368958041110140577[72] = 1;
   out_6368958041110140577[73] = dt;
   out_6368958041110140577[74] = 0;
   out_6368958041110140577[75] = 0;
   out_6368958041110140577[76] = 0;
   out_6368958041110140577[77] = 0;
   out_6368958041110140577[78] = 0;
   out_6368958041110140577[79] = 0;
   out_6368958041110140577[80] = 0;
   out_6368958041110140577[81] = 0;
   out_6368958041110140577[82] = 0;
   out_6368958041110140577[83] = 0;
   out_6368958041110140577[84] = 1;
   out_6368958041110140577[85] = dt;
   out_6368958041110140577[86] = 0;
   out_6368958041110140577[87] = 0;
   out_6368958041110140577[88] = 0;
   out_6368958041110140577[89] = 0;
   out_6368958041110140577[90] = 0;
   out_6368958041110140577[91] = 0;
   out_6368958041110140577[92] = 0;
   out_6368958041110140577[93] = 0;
   out_6368958041110140577[94] = 0;
   out_6368958041110140577[95] = 0;
   out_6368958041110140577[96] = 1;
   out_6368958041110140577[97] = 0;
   out_6368958041110140577[98] = 0;
   out_6368958041110140577[99] = 0;
   out_6368958041110140577[100] = 0;
   out_6368958041110140577[101] = 0;
   out_6368958041110140577[102] = 0;
   out_6368958041110140577[103] = 0;
   out_6368958041110140577[104] = 0;
   out_6368958041110140577[105] = 0;
   out_6368958041110140577[106] = 0;
   out_6368958041110140577[107] = 0;
   out_6368958041110140577[108] = 1;
   out_6368958041110140577[109] = 0;
   out_6368958041110140577[110] = 0;
   out_6368958041110140577[111] = 0;
   out_6368958041110140577[112] = 0;
   out_6368958041110140577[113] = 0;
   out_6368958041110140577[114] = 0;
   out_6368958041110140577[115] = 0;
   out_6368958041110140577[116] = 0;
   out_6368958041110140577[117] = 0;
   out_6368958041110140577[118] = 0;
   out_6368958041110140577[119] = 0;
   out_6368958041110140577[120] = 1;
}
void h_6(double *state, double *sat_pos, double *out_2271110864362118697) {
   out_2271110864362118697[0] = sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2)) + state[6];
}
void H_6(double *state, double *sat_pos, double *out_1862672885827164935) {
   out_1862672885827164935[0] = (-sat_pos[0] + state[0])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_1862672885827164935[1] = (-sat_pos[1] + state[1])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_1862672885827164935[2] = (-sat_pos[2] + state[2])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_1862672885827164935[3] = 0;
   out_1862672885827164935[4] = 0;
   out_1862672885827164935[5] = 0;
   out_1862672885827164935[6] = 1;
   out_1862672885827164935[7] = 0;
   out_1862672885827164935[8] = 0;
   out_1862672885827164935[9] = 0;
   out_1862672885827164935[10] = 0;
}
void h_20(double *state, double *sat_pos, double *out_4324669159508799845) {
   out_4324669159508799845[0] = sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2)) + sat_pos[3]*state[10] + state[6] + state[9];
}
void H_20(double *state, double *sat_pos, double *out_2084788552121881515) {
   out_2084788552121881515[0] = (-sat_pos[0] + state[0])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_2084788552121881515[1] = (-sat_pos[1] + state[1])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_2084788552121881515[2] = (-sat_pos[2] + state[2])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_2084788552121881515[3] = 0;
   out_2084788552121881515[4] = 0;
   out_2084788552121881515[5] = 0;
   out_2084788552121881515[6] = 1;
   out_2084788552121881515[7] = 0;
   out_2084788552121881515[8] = 0;
   out_2084788552121881515[9] = 1;
   out_2084788552121881515[10] = sat_pos[3];
}
void h_7(double *state, double *sat_pos_vel, double *out_5010606036331411486) {
   out_5010606036331411486[0] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[3] - state[3])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[4] - state[4])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + (sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + state[7];
}
void H_7(double *state, double *sat_pos_vel, double *out_3676152182946046175) {
   out_3676152182946046175[0] = pow(sat_pos_vel[0] - state[0], 2)*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[0] - state[0])*(sat_pos_vel[1] - state[1])*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[0] - state[0])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[3] - state[3])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_3676152182946046175[1] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[1] - state[1])*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + pow(sat_pos_vel[1] - state[1], 2)*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[4] - state[4])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_3676152182946046175[2] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + pow(sat_pos_vel[2] - state[2], 2)*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[5] - state[5])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_3676152182946046175[3] = -(sat_pos_vel[0] - state[0])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_3676152182946046175[4] = -(sat_pos_vel[1] - state[1])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_3676152182946046175[5] = -(sat_pos_vel[2] - state[2])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_3676152182946046175[6] = 0;
   out_3676152182946046175[7] = 1;
   out_3676152182946046175[8] = 0;
   out_3676152182946046175[9] = 0;
   out_3676152182946046175[10] = 0;
}
void h_21(double *state, double *sat_pos_vel, double *out_5010606036331411486) {
   out_5010606036331411486[0] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[3] - state[3])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[4] - state[4])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + (sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + state[7];
}
void H_21(double *state, double *sat_pos_vel, double *out_3676152182946046175) {
   out_3676152182946046175[0] = pow(sat_pos_vel[0] - state[0], 2)*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[0] - state[0])*(sat_pos_vel[1] - state[1])*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[0] - state[0])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[3] - state[3])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_3676152182946046175[1] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[1] - state[1])*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + pow(sat_pos_vel[1] - state[1], 2)*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[4] - state[4])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_3676152182946046175[2] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + pow(sat_pos_vel[2] - state[2], 2)*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[5] - state[5])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_3676152182946046175[3] = -(sat_pos_vel[0] - state[0])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_3676152182946046175[4] = -(sat_pos_vel[1] - state[1])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_3676152182946046175[5] = -(sat_pos_vel[2] - state[2])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_3676152182946046175[6] = 0;
   out_3676152182946046175[7] = 1;
   out_3676152182946046175[8] = 0;
   out_3676152182946046175[9] = 0;
   out_3676152182946046175[10] = 0;
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
void gnss_err_fun(double *nom_x, double *delta_x, double *out_3532684675618107860) {
  err_fun(nom_x, delta_x, out_3532684675618107860);
}
void gnss_inv_err_fun(double *nom_x, double *true_x, double *out_4040997643746645524) {
  inv_err_fun(nom_x, true_x, out_4040997643746645524);
}
void gnss_H_mod_fun(double *state, double *out_5907768448464933327) {
  H_mod_fun(state, out_5907768448464933327);
}
void gnss_f_fun(double *state, double dt, double *out_8719739038902116923) {
  f_fun(state,  dt, out_8719739038902116923);
}
void gnss_F_fun(double *state, double dt, double *out_6368958041110140577) {
  F_fun(state,  dt, out_6368958041110140577);
}
void gnss_h_6(double *state, double *sat_pos, double *out_2271110864362118697) {
  h_6(state, sat_pos, out_2271110864362118697);
}
void gnss_H_6(double *state, double *sat_pos, double *out_1862672885827164935) {
  H_6(state, sat_pos, out_1862672885827164935);
}
void gnss_h_20(double *state, double *sat_pos, double *out_4324669159508799845) {
  h_20(state, sat_pos, out_4324669159508799845);
}
void gnss_H_20(double *state, double *sat_pos, double *out_2084788552121881515) {
  H_20(state, sat_pos, out_2084788552121881515);
}
void gnss_h_7(double *state, double *sat_pos_vel, double *out_5010606036331411486) {
  h_7(state, sat_pos_vel, out_5010606036331411486);
}
void gnss_H_7(double *state, double *sat_pos_vel, double *out_3676152182946046175) {
  H_7(state, sat_pos_vel, out_3676152182946046175);
}
void gnss_h_21(double *state, double *sat_pos_vel, double *out_5010606036331411486) {
  h_21(state, sat_pos_vel, out_5010606036331411486);
}
void gnss_H_21(double *state, double *sat_pos_vel, double *out_3676152182946046175) {
  H_21(state, sat_pos_vel, out_3676152182946046175);
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
