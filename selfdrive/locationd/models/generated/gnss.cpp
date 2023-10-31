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
void err_fun(double *nom_x, double *delta_x, double *out_1856399012621437567) {
   out_1856399012621437567[0] = delta_x[0] + nom_x[0];
   out_1856399012621437567[1] = delta_x[1] + nom_x[1];
   out_1856399012621437567[2] = delta_x[2] + nom_x[2];
   out_1856399012621437567[3] = delta_x[3] + nom_x[3];
   out_1856399012621437567[4] = delta_x[4] + nom_x[4];
   out_1856399012621437567[5] = delta_x[5] + nom_x[5];
   out_1856399012621437567[6] = delta_x[6] + nom_x[6];
   out_1856399012621437567[7] = delta_x[7] + nom_x[7];
   out_1856399012621437567[8] = delta_x[8] + nom_x[8];
   out_1856399012621437567[9] = delta_x[9] + nom_x[9];
   out_1856399012621437567[10] = delta_x[10] + nom_x[10];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_5659332400997797470) {
   out_5659332400997797470[0] = -nom_x[0] + true_x[0];
   out_5659332400997797470[1] = -nom_x[1] + true_x[1];
   out_5659332400997797470[2] = -nom_x[2] + true_x[2];
   out_5659332400997797470[3] = -nom_x[3] + true_x[3];
   out_5659332400997797470[4] = -nom_x[4] + true_x[4];
   out_5659332400997797470[5] = -nom_x[5] + true_x[5];
   out_5659332400997797470[6] = -nom_x[6] + true_x[6];
   out_5659332400997797470[7] = -nom_x[7] + true_x[7];
   out_5659332400997797470[8] = -nom_x[8] + true_x[8];
   out_5659332400997797470[9] = -nom_x[9] + true_x[9];
   out_5659332400997797470[10] = -nom_x[10] + true_x[10];
}
void H_mod_fun(double *state, double *out_6521121627186908832) {
   out_6521121627186908832[0] = 1.0;
   out_6521121627186908832[1] = 0;
   out_6521121627186908832[2] = 0;
   out_6521121627186908832[3] = 0;
   out_6521121627186908832[4] = 0;
   out_6521121627186908832[5] = 0;
   out_6521121627186908832[6] = 0;
   out_6521121627186908832[7] = 0;
   out_6521121627186908832[8] = 0;
   out_6521121627186908832[9] = 0;
   out_6521121627186908832[10] = 0;
   out_6521121627186908832[11] = 0;
   out_6521121627186908832[12] = 1.0;
   out_6521121627186908832[13] = 0;
   out_6521121627186908832[14] = 0;
   out_6521121627186908832[15] = 0;
   out_6521121627186908832[16] = 0;
   out_6521121627186908832[17] = 0;
   out_6521121627186908832[18] = 0;
   out_6521121627186908832[19] = 0;
   out_6521121627186908832[20] = 0;
   out_6521121627186908832[21] = 0;
   out_6521121627186908832[22] = 0;
   out_6521121627186908832[23] = 0;
   out_6521121627186908832[24] = 1.0;
   out_6521121627186908832[25] = 0;
   out_6521121627186908832[26] = 0;
   out_6521121627186908832[27] = 0;
   out_6521121627186908832[28] = 0;
   out_6521121627186908832[29] = 0;
   out_6521121627186908832[30] = 0;
   out_6521121627186908832[31] = 0;
   out_6521121627186908832[32] = 0;
   out_6521121627186908832[33] = 0;
   out_6521121627186908832[34] = 0;
   out_6521121627186908832[35] = 0;
   out_6521121627186908832[36] = 1.0;
   out_6521121627186908832[37] = 0;
   out_6521121627186908832[38] = 0;
   out_6521121627186908832[39] = 0;
   out_6521121627186908832[40] = 0;
   out_6521121627186908832[41] = 0;
   out_6521121627186908832[42] = 0;
   out_6521121627186908832[43] = 0;
   out_6521121627186908832[44] = 0;
   out_6521121627186908832[45] = 0;
   out_6521121627186908832[46] = 0;
   out_6521121627186908832[47] = 0;
   out_6521121627186908832[48] = 1.0;
   out_6521121627186908832[49] = 0;
   out_6521121627186908832[50] = 0;
   out_6521121627186908832[51] = 0;
   out_6521121627186908832[52] = 0;
   out_6521121627186908832[53] = 0;
   out_6521121627186908832[54] = 0;
   out_6521121627186908832[55] = 0;
   out_6521121627186908832[56] = 0;
   out_6521121627186908832[57] = 0;
   out_6521121627186908832[58] = 0;
   out_6521121627186908832[59] = 0;
   out_6521121627186908832[60] = 1.0;
   out_6521121627186908832[61] = 0;
   out_6521121627186908832[62] = 0;
   out_6521121627186908832[63] = 0;
   out_6521121627186908832[64] = 0;
   out_6521121627186908832[65] = 0;
   out_6521121627186908832[66] = 0;
   out_6521121627186908832[67] = 0;
   out_6521121627186908832[68] = 0;
   out_6521121627186908832[69] = 0;
   out_6521121627186908832[70] = 0;
   out_6521121627186908832[71] = 0;
   out_6521121627186908832[72] = 1.0;
   out_6521121627186908832[73] = 0;
   out_6521121627186908832[74] = 0;
   out_6521121627186908832[75] = 0;
   out_6521121627186908832[76] = 0;
   out_6521121627186908832[77] = 0;
   out_6521121627186908832[78] = 0;
   out_6521121627186908832[79] = 0;
   out_6521121627186908832[80] = 0;
   out_6521121627186908832[81] = 0;
   out_6521121627186908832[82] = 0;
   out_6521121627186908832[83] = 0;
   out_6521121627186908832[84] = 1.0;
   out_6521121627186908832[85] = 0;
   out_6521121627186908832[86] = 0;
   out_6521121627186908832[87] = 0;
   out_6521121627186908832[88] = 0;
   out_6521121627186908832[89] = 0;
   out_6521121627186908832[90] = 0;
   out_6521121627186908832[91] = 0;
   out_6521121627186908832[92] = 0;
   out_6521121627186908832[93] = 0;
   out_6521121627186908832[94] = 0;
   out_6521121627186908832[95] = 0;
   out_6521121627186908832[96] = 1.0;
   out_6521121627186908832[97] = 0;
   out_6521121627186908832[98] = 0;
   out_6521121627186908832[99] = 0;
   out_6521121627186908832[100] = 0;
   out_6521121627186908832[101] = 0;
   out_6521121627186908832[102] = 0;
   out_6521121627186908832[103] = 0;
   out_6521121627186908832[104] = 0;
   out_6521121627186908832[105] = 0;
   out_6521121627186908832[106] = 0;
   out_6521121627186908832[107] = 0;
   out_6521121627186908832[108] = 1.0;
   out_6521121627186908832[109] = 0;
   out_6521121627186908832[110] = 0;
   out_6521121627186908832[111] = 0;
   out_6521121627186908832[112] = 0;
   out_6521121627186908832[113] = 0;
   out_6521121627186908832[114] = 0;
   out_6521121627186908832[115] = 0;
   out_6521121627186908832[116] = 0;
   out_6521121627186908832[117] = 0;
   out_6521121627186908832[118] = 0;
   out_6521121627186908832[119] = 0;
   out_6521121627186908832[120] = 1.0;
}
void f_fun(double *state, double dt, double *out_8022750769580419123) {
   out_8022750769580419123[0] = dt*state[3] + state[0];
   out_8022750769580419123[1] = dt*state[4] + state[1];
   out_8022750769580419123[2] = dt*state[5] + state[2];
   out_8022750769580419123[3] = state[3];
   out_8022750769580419123[4] = state[4];
   out_8022750769580419123[5] = state[5];
   out_8022750769580419123[6] = dt*state[7] + state[6];
   out_8022750769580419123[7] = dt*state[8] + state[7];
   out_8022750769580419123[8] = state[8];
   out_8022750769580419123[9] = state[9];
   out_8022750769580419123[10] = state[10];
}
void F_fun(double *state, double dt, double *out_6336087931668650939) {
   out_6336087931668650939[0] = 1;
   out_6336087931668650939[1] = 0;
   out_6336087931668650939[2] = 0;
   out_6336087931668650939[3] = dt;
   out_6336087931668650939[4] = 0;
   out_6336087931668650939[5] = 0;
   out_6336087931668650939[6] = 0;
   out_6336087931668650939[7] = 0;
   out_6336087931668650939[8] = 0;
   out_6336087931668650939[9] = 0;
   out_6336087931668650939[10] = 0;
   out_6336087931668650939[11] = 0;
   out_6336087931668650939[12] = 1;
   out_6336087931668650939[13] = 0;
   out_6336087931668650939[14] = 0;
   out_6336087931668650939[15] = dt;
   out_6336087931668650939[16] = 0;
   out_6336087931668650939[17] = 0;
   out_6336087931668650939[18] = 0;
   out_6336087931668650939[19] = 0;
   out_6336087931668650939[20] = 0;
   out_6336087931668650939[21] = 0;
   out_6336087931668650939[22] = 0;
   out_6336087931668650939[23] = 0;
   out_6336087931668650939[24] = 1;
   out_6336087931668650939[25] = 0;
   out_6336087931668650939[26] = 0;
   out_6336087931668650939[27] = dt;
   out_6336087931668650939[28] = 0;
   out_6336087931668650939[29] = 0;
   out_6336087931668650939[30] = 0;
   out_6336087931668650939[31] = 0;
   out_6336087931668650939[32] = 0;
   out_6336087931668650939[33] = 0;
   out_6336087931668650939[34] = 0;
   out_6336087931668650939[35] = 0;
   out_6336087931668650939[36] = 1;
   out_6336087931668650939[37] = 0;
   out_6336087931668650939[38] = 0;
   out_6336087931668650939[39] = 0;
   out_6336087931668650939[40] = 0;
   out_6336087931668650939[41] = 0;
   out_6336087931668650939[42] = 0;
   out_6336087931668650939[43] = 0;
   out_6336087931668650939[44] = 0;
   out_6336087931668650939[45] = 0;
   out_6336087931668650939[46] = 0;
   out_6336087931668650939[47] = 0;
   out_6336087931668650939[48] = 1;
   out_6336087931668650939[49] = 0;
   out_6336087931668650939[50] = 0;
   out_6336087931668650939[51] = 0;
   out_6336087931668650939[52] = 0;
   out_6336087931668650939[53] = 0;
   out_6336087931668650939[54] = 0;
   out_6336087931668650939[55] = 0;
   out_6336087931668650939[56] = 0;
   out_6336087931668650939[57] = 0;
   out_6336087931668650939[58] = 0;
   out_6336087931668650939[59] = 0;
   out_6336087931668650939[60] = 1;
   out_6336087931668650939[61] = 0;
   out_6336087931668650939[62] = 0;
   out_6336087931668650939[63] = 0;
   out_6336087931668650939[64] = 0;
   out_6336087931668650939[65] = 0;
   out_6336087931668650939[66] = 0;
   out_6336087931668650939[67] = 0;
   out_6336087931668650939[68] = 0;
   out_6336087931668650939[69] = 0;
   out_6336087931668650939[70] = 0;
   out_6336087931668650939[71] = 0;
   out_6336087931668650939[72] = 1;
   out_6336087931668650939[73] = dt;
   out_6336087931668650939[74] = 0;
   out_6336087931668650939[75] = 0;
   out_6336087931668650939[76] = 0;
   out_6336087931668650939[77] = 0;
   out_6336087931668650939[78] = 0;
   out_6336087931668650939[79] = 0;
   out_6336087931668650939[80] = 0;
   out_6336087931668650939[81] = 0;
   out_6336087931668650939[82] = 0;
   out_6336087931668650939[83] = 0;
   out_6336087931668650939[84] = 1;
   out_6336087931668650939[85] = dt;
   out_6336087931668650939[86] = 0;
   out_6336087931668650939[87] = 0;
   out_6336087931668650939[88] = 0;
   out_6336087931668650939[89] = 0;
   out_6336087931668650939[90] = 0;
   out_6336087931668650939[91] = 0;
   out_6336087931668650939[92] = 0;
   out_6336087931668650939[93] = 0;
   out_6336087931668650939[94] = 0;
   out_6336087931668650939[95] = 0;
   out_6336087931668650939[96] = 1;
   out_6336087931668650939[97] = 0;
   out_6336087931668650939[98] = 0;
   out_6336087931668650939[99] = 0;
   out_6336087931668650939[100] = 0;
   out_6336087931668650939[101] = 0;
   out_6336087931668650939[102] = 0;
   out_6336087931668650939[103] = 0;
   out_6336087931668650939[104] = 0;
   out_6336087931668650939[105] = 0;
   out_6336087931668650939[106] = 0;
   out_6336087931668650939[107] = 0;
   out_6336087931668650939[108] = 1;
   out_6336087931668650939[109] = 0;
   out_6336087931668650939[110] = 0;
   out_6336087931668650939[111] = 0;
   out_6336087931668650939[112] = 0;
   out_6336087931668650939[113] = 0;
   out_6336087931668650939[114] = 0;
   out_6336087931668650939[115] = 0;
   out_6336087931668650939[116] = 0;
   out_6336087931668650939[117] = 0;
   out_6336087931668650939[118] = 0;
   out_6336087931668650939[119] = 0;
   out_6336087931668650939[120] = 1;
}
void h_6(double *state, double *sat_pos, double *out_6727337945144809708) {
   out_6727337945144809708[0] = sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2)) + state[6];
}
void H_6(double *state, double *sat_pos, double *out_1448263778646329223) {
   out_1448263778646329223[0] = (-sat_pos[0] + state[0])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_1448263778646329223[1] = (-sat_pos[1] + state[1])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_1448263778646329223[2] = (-sat_pos[2] + state[2])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_1448263778646329223[3] = 0;
   out_1448263778646329223[4] = 0;
   out_1448263778646329223[5] = 0;
   out_1448263778646329223[6] = 1;
   out_1448263778646329223[7] = 0;
   out_1448263778646329223[8] = 0;
   out_1448263778646329223[9] = 0;
   out_1448263778646329223[10] = 0;
}
void h_20(double *state, double *sat_pos, double *out_2137014843544135742) {
   out_2137014843544135742[0] = sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2)) + sat_pos[3]*state[10] + state[6] + state[9];
}
void H_20(double *state, double *sat_pos, double *out_1721365513193142610) {
   out_1721365513193142610[0] = (-sat_pos[0] + state[0])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_1721365513193142610[1] = (-sat_pos[1] + state[1])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_1721365513193142610[2] = (-sat_pos[2] + state[2])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_1721365513193142610[3] = 0;
   out_1721365513193142610[4] = 0;
   out_1721365513193142610[5] = 0;
   out_1721365513193142610[6] = 1;
   out_1721365513193142610[7] = 0;
   out_1721365513193142610[8] = 0;
   out_1721365513193142610[9] = 1;
   out_1721365513193142610[10] = sat_pos[3];
}
void h_7(double *state, double *sat_pos_vel, double *out_7819726430377713612) {
   out_7819726430377713612[0] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[3] - state[3])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[4] - state[4])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + (sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + state[7];
}
void H_7(double *state, double *sat_pos_vel, double *out_5800620054238539955) {
   out_5800620054238539955[0] = pow(sat_pos_vel[0] - state[0], 2)*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[0] - state[0])*(sat_pos_vel[1] - state[1])*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[0] - state[0])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[3] - state[3])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_5800620054238539955[1] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[1] - state[1])*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + pow(sat_pos_vel[1] - state[1], 2)*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[4] - state[4])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_5800620054238539955[2] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + pow(sat_pos_vel[2] - state[2], 2)*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[5] - state[5])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_5800620054238539955[3] = -(sat_pos_vel[0] - state[0])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_5800620054238539955[4] = -(sat_pos_vel[1] - state[1])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_5800620054238539955[5] = -(sat_pos_vel[2] - state[2])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_5800620054238539955[6] = 0;
   out_5800620054238539955[7] = 1;
   out_5800620054238539955[8] = 0;
   out_5800620054238539955[9] = 0;
   out_5800620054238539955[10] = 0;
}
void h_21(double *state, double *sat_pos_vel, double *out_7819726430377713612) {
   out_7819726430377713612[0] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[3] - state[3])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[4] - state[4])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + (sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + state[7];
}
void H_21(double *state, double *sat_pos_vel, double *out_5800620054238539955) {
   out_5800620054238539955[0] = pow(sat_pos_vel[0] - state[0], 2)*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[0] - state[0])*(sat_pos_vel[1] - state[1])*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[0] - state[0])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[3] - state[3])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_5800620054238539955[1] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[1] - state[1])*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + pow(sat_pos_vel[1] - state[1], 2)*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[4] - state[4])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_5800620054238539955[2] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + pow(sat_pos_vel[2] - state[2], 2)*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[5] - state[5])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_5800620054238539955[3] = -(sat_pos_vel[0] - state[0])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_5800620054238539955[4] = -(sat_pos_vel[1] - state[1])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_5800620054238539955[5] = -(sat_pos_vel[2] - state[2])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_5800620054238539955[6] = 0;
   out_5800620054238539955[7] = 1;
   out_5800620054238539955[8] = 0;
   out_5800620054238539955[9] = 0;
   out_5800620054238539955[10] = 0;
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
void gnss_err_fun(double *nom_x, double *delta_x, double *out_1856399012621437567) {
  err_fun(nom_x, delta_x, out_1856399012621437567);
}
void gnss_inv_err_fun(double *nom_x, double *true_x, double *out_5659332400997797470) {
  inv_err_fun(nom_x, true_x, out_5659332400997797470);
}
void gnss_H_mod_fun(double *state, double *out_6521121627186908832) {
  H_mod_fun(state, out_6521121627186908832);
}
void gnss_f_fun(double *state, double dt, double *out_8022750769580419123) {
  f_fun(state,  dt, out_8022750769580419123);
}
void gnss_F_fun(double *state, double dt, double *out_6336087931668650939) {
  F_fun(state,  dt, out_6336087931668650939);
}
void gnss_h_6(double *state, double *sat_pos, double *out_6727337945144809708) {
  h_6(state, sat_pos, out_6727337945144809708);
}
void gnss_H_6(double *state, double *sat_pos, double *out_1448263778646329223) {
  H_6(state, sat_pos, out_1448263778646329223);
}
void gnss_h_20(double *state, double *sat_pos, double *out_2137014843544135742) {
  h_20(state, sat_pos, out_2137014843544135742);
}
void gnss_H_20(double *state, double *sat_pos, double *out_1721365513193142610) {
  H_20(state, sat_pos, out_1721365513193142610);
}
void gnss_h_7(double *state, double *sat_pos_vel, double *out_7819726430377713612) {
  h_7(state, sat_pos_vel, out_7819726430377713612);
}
void gnss_H_7(double *state, double *sat_pos_vel, double *out_5800620054238539955) {
  H_7(state, sat_pos_vel, out_5800620054238539955);
}
void gnss_h_21(double *state, double *sat_pos_vel, double *out_7819726430377713612) {
  h_21(state, sat_pos_vel, out_7819726430377713612);
}
void gnss_H_21(double *state, double *sat_pos_vel, double *out_5800620054238539955) {
  H_21(state, sat_pos_vel, out_5800620054238539955);
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
