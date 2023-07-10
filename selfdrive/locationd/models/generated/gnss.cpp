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
 *                      Code generated with SymPy 1.11.1                      *
 *                                                                            *
 *              See http://www.sympy.org/ for more information.               *
 *                                                                            *
 *                         This file is part of 'ekf'                         *
 ******************************************************************************/
void err_fun(double *nom_x, double *delta_x, double *out_966236154794564673) {
   out_966236154794564673[0] = delta_x[0] + nom_x[0];
   out_966236154794564673[1] = delta_x[1] + nom_x[1];
   out_966236154794564673[2] = delta_x[2] + nom_x[2];
   out_966236154794564673[3] = delta_x[3] + nom_x[3];
   out_966236154794564673[4] = delta_x[4] + nom_x[4];
   out_966236154794564673[5] = delta_x[5] + nom_x[5];
   out_966236154794564673[6] = delta_x[6] + nom_x[6];
   out_966236154794564673[7] = delta_x[7] + nom_x[7];
   out_966236154794564673[8] = delta_x[8] + nom_x[8];
   out_966236154794564673[9] = delta_x[9] + nom_x[9];
   out_966236154794564673[10] = delta_x[10] + nom_x[10];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_1570495147257342659) {
   out_1570495147257342659[0] = -nom_x[0] + true_x[0];
   out_1570495147257342659[1] = -nom_x[1] + true_x[1];
   out_1570495147257342659[2] = -nom_x[2] + true_x[2];
   out_1570495147257342659[3] = -nom_x[3] + true_x[3];
   out_1570495147257342659[4] = -nom_x[4] + true_x[4];
   out_1570495147257342659[5] = -nom_x[5] + true_x[5];
   out_1570495147257342659[6] = -nom_x[6] + true_x[6];
   out_1570495147257342659[7] = -nom_x[7] + true_x[7];
   out_1570495147257342659[8] = -nom_x[8] + true_x[8];
   out_1570495147257342659[9] = -nom_x[9] + true_x[9];
   out_1570495147257342659[10] = -nom_x[10] + true_x[10];
}
void H_mod_fun(double *state, double *out_1116987290868003958) {
   out_1116987290868003958[0] = 1.0;
   out_1116987290868003958[1] = 0;
   out_1116987290868003958[2] = 0;
   out_1116987290868003958[3] = 0;
   out_1116987290868003958[4] = 0;
   out_1116987290868003958[5] = 0;
   out_1116987290868003958[6] = 0;
   out_1116987290868003958[7] = 0;
   out_1116987290868003958[8] = 0;
   out_1116987290868003958[9] = 0;
   out_1116987290868003958[10] = 0;
   out_1116987290868003958[11] = 0;
   out_1116987290868003958[12] = 1.0;
   out_1116987290868003958[13] = 0;
   out_1116987290868003958[14] = 0;
   out_1116987290868003958[15] = 0;
   out_1116987290868003958[16] = 0;
   out_1116987290868003958[17] = 0;
   out_1116987290868003958[18] = 0;
   out_1116987290868003958[19] = 0;
   out_1116987290868003958[20] = 0;
   out_1116987290868003958[21] = 0;
   out_1116987290868003958[22] = 0;
   out_1116987290868003958[23] = 0;
   out_1116987290868003958[24] = 1.0;
   out_1116987290868003958[25] = 0;
   out_1116987290868003958[26] = 0;
   out_1116987290868003958[27] = 0;
   out_1116987290868003958[28] = 0;
   out_1116987290868003958[29] = 0;
   out_1116987290868003958[30] = 0;
   out_1116987290868003958[31] = 0;
   out_1116987290868003958[32] = 0;
   out_1116987290868003958[33] = 0;
   out_1116987290868003958[34] = 0;
   out_1116987290868003958[35] = 0;
   out_1116987290868003958[36] = 1.0;
   out_1116987290868003958[37] = 0;
   out_1116987290868003958[38] = 0;
   out_1116987290868003958[39] = 0;
   out_1116987290868003958[40] = 0;
   out_1116987290868003958[41] = 0;
   out_1116987290868003958[42] = 0;
   out_1116987290868003958[43] = 0;
   out_1116987290868003958[44] = 0;
   out_1116987290868003958[45] = 0;
   out_1116987290868003958[46] = 0;
   out_1116987290868003958[47] = 0;
   out_1116987290868003958[48] = 1.0;
   out_1116987290868003958[49] = 0;
   out_1116987290868003958[50] = 0;
   out_1116987290868003958[51] = 0;
   out_1116987290868003958[52] = 0;
   out_1116987290868003958[53] = 0;
   out_1116987290868003958[54] = 0;
   out_1116987290868003958[55] = 0;
   out_1116987290868003958[56] = 0;
   out_1116987290868003958[57] = 0;
   out_1116987290868003958[58] = 0;
   out_1116987290868003958[59] = 0;
   out_1116987290868003958[60] = 1.0;
   out_1116987290868003958[61] = 0;
   out_1116987290868003958[62] = 0;
   out_1116987290868003958[63] = 0;
   out_1116987290868003958[64] = 0;
   out_1116987290868003958[65] = 0;
   out_1116987290868003958[66] = 0;
   out_1116987290868003958[67] = 0;
   out_1116987290868003958[68] = 0;
   out_1116987290868003958[69] = 0;
   out_1116987290868003958[70] = 0;
   out_1116987290868003958[71] = 0;
   out_1116987290868003958[72] = 1.0;
   out_1116987290868003958[73] = 0;
   out_1116987290868003958[74] = 0;
   out_1116987290868003958[75] = 0;
   out_1116987290868003958[76] = 0;
   out_1116987290868003958[77] = 0;
   out_1116987290868003958[78] = 0;
   out_1116987290868003958[79] = 0;
   out_1116987290868003958[80] = 0;
   out_1116987290868003958[81] = 0;
   out_1116987290868003958[82] = 0;
   out_1116987290868003958[83] = 0;
   out_1116987290868003958[84] = 1.0;
   out_1116987290868003958[85] = 0;
   out_1116987290868003958[86] = 0;
   out_1116987290868003958[87] = 0;
   out_1116987290868003958[88] = 0;
   out_1116987290868003958[89] = 0;
   out_1116987290868003958[90] = 0;
   out_1116987290868003958[91] = 0;
   out_1116987290868003958[92] = 0;
   out_1116987290868003958[93] = 0;
   out_1116987290868003958[94] = 0;
   out_1116987290868003958[95] = 0;
   out_1116987290868003958[96] = 1.0;
   out_1116987290868003958[97] = 0;
   out_1116987290868003958[98] = 0;
   out_1116987290868003958[99] = 0;
   out_1116987290868003958[100] = 0;
   out_1116987290868003958[101] = 0;
   out_1116987290868003958[102] = 0;
   out_1116987290868003958[103] = 0;
   out_1116987290868003958[104] = 0;
   out_1116987290868003958[105] = 0;
   out_1116987290868003958[106] = 0;
   out_1116987290868003958[107] = 0;
   out_1116987290868003958[108] = 1.0;
   out_1116987290868003958[109] = 0;
   out_1116987290868003958[110] = 0;
   out_1116987290868003958[111] = 0;
   out_1116987290868003958[112] = 0;
   out_1116987290868003958[113] = 0;
   out_1116987290868003958[114] = 0;
   out_1116987290868003958[115] = 0;
   out_1116987290868003958[116] = 0;
   out_1116987290868003958[117] = 0;
   out_1116987290868003958[118] = 0;
   out_1116987290868003958[119] = 0;
   out_1116987290868003958[120] = 1.0;
}
void f_fun(double *state, double dt, double *out_7944759911088803830) {
   out_7944759911088803830[0] = dt*state[3] + state[0];
   out_7944759911088803830[1] = dt*state[4] + state[1];
   out_7944759911088803830[2] = dt*state[5] + state[2];
   out_7944759911088803830[3] = state[3];
   out_7944759911088803830[4] = state[4];
   out_7944759911088803830[5] = state[5];
   out_7944759911088803830[6] = dt*state[7] + state[6];
   out_7944759911088803830[7] = dt*state[8] + state[7];
   out_7944759911088803830[8] = state[8];
   out_7944759911088803830[9] = state[9];
   out_7944759911088803830[10] = state[10];
}
void F_fun(double *state, double dt, double *out_6000912361546807532) {
   out_6000912361546807532[0] = 1;
   out_6000912361546807532[1] = 0;
   out_6000912361546807532[2] = 0;
   out_6000912361546807532[3] = dt;
   out_6000912361546807532[4] = 0;
   out_6000912361546807532[5] = 0;
   out_6000912361546807532[6] = 0;
   out_6000912361546807532[7] = 0;
   out_6000912361546807532[8] = 0;
   out_6000912361546807532[9] = 0;
   out_6000912361546807532[10] = 0;
   out_6000912361546807532[11] = 0;
   out_6000912361546807532[12] = 1;
   out_6000912361546807532[13] = 0;
   out_6000912361546807532[14] = 0;
   out_6000912361546807532[15] = dt;
   out_6000912361546807532[16] = 0;
   out_6000912361546807532[17] = 0;
   out_6000912361546807532[18] = 0;
   out_6000912361546807532[19] = 0;
   out_6000912361546807532[20] = 0;
   out_6000912361546807532[21] = 0;
   out_6000912361546807532[22] = 0;
   out_6000912361546807532[23] = 0;
   out_6000912361546807532[24] = 1;
   out_6000912361546807532[25] = 0;
   out_6000912361546807532[26] = 0;
   out_6000912361546807532[27] = dt;
   out_6000912361546807532[28] = 0;
   out_6000912361546807532[29] = 0;
   out_6000912361546807532[30] = 0;
   out_6000912361546807532[31] = 0;
   out_6000912361546807532[32] = 0;
   out_6000912361546807532[33] = 0;
   out_6000912361546807532[34] = 0;
   out_6000912361546807532[35] = 0;
   out_6000912361546807532[36] = 1;
   out_6000912361546807532[37] = 0;
   out_6000912361546807532[38] = 0;
   out_6000912361546807532[39] = 0;
   out_6000912361546807532[40] = 0;
   out_6000912361546807532[41] = 0;
   out_6000912361546807532[42] = 0;
   out_6000912361546807532[43] = 0;
   out_6000912361546807532[44] = 0;
   out_6000912361546807532[45] = 0;
   out_6000912361546807532[46] = 0;
   out_6000912361546807532[47] = 0;
   out_6000912361546807532[48] = 1;
   out_6000912361546807532[49] = 0;
   out_6000912361546807532[50] = 0;
   out_6000912361546807532[51] = 0;
   out_6000912361546807532[52] = 0;
   out_6000912361546807532[53] = 0;
   out_6000912361546807532[54] = 0;
   out_6000912361546807532[55] = 0;
   out_6000912361546807532[56] = 0;
   out_6000912361546807532[57] = 0;
   out_6000912361546807532[58] = 0;
   out_6000912361546807532[59] = 0;
   out_6000912361546807532[60] = 1;
   out_6000912361546807532[61] = 0;
   out_6000912361546807532[62] = 0;
   out_6000912361546807532[63] = 0;
   out_6000912361546807532[64] = 0;
   out_6000912361546807532[65] = 0;
   out_6000912361546807532[66] = 0;
   out_6000912361546807532[67] = 0;
   out_6000912361546807532[68] = 0;
   out_6000912361546807532[69] = 0;
   out_6000912361546807532[70] = 0;
   out_6000912361546807532[71] = 0;
   out_6000912361546807532[72] = 1;
   out_6000912361546807532[73] = dt;
   out_6000912361546807532[74] = 0;
   out_6000912361546807532[75] = 0;
   out_6000912361546807532[76] = 0;
   out_6000912361546807532[77] = 0;
   out_6000912361546807532[78] = 0;
   out_6000912361546807532[79] = 0;
   out_6000912361546807532[80] = 0;
   out_6000912361546807532[81] = 0;
   out_6000912361546807532[82] = 0;
   out_6000912361546807532[83] = 0;
   out_6000912361546807532[84] = 1;
   out_6000912361546807532[85] = dt;
   out_6000912361546807532[86] = 0;
   out_6000912361546807532[87] = 0;
   out_6000912361546807532[88] = 0;
   out_6000912361546807532[89] = 0;
   out_6000912361546807532[90] = 0;
   out_6000912361546807532[91] = 0;
   out_6000912361546807532[92] = 0;
   out_6000912361546807532[93] = 0;
   out_6000912361546807532[94] = 0;
   out_6000912361546807532[95] = 0;
   out_6000912361546807532[96] = 1;
   out_6000912361546807532[97] = 0;
   out_6000912361546807532[98] = 0;
   out_6000912361546807532[99] = 0;
   out_6000912361546807532[100] = 0;
   out_6000912361546807532[101] = 0;
   out_6000912361546807532[102] = 0;
   out_6000912361546807532[103] = 0;
   out_6000912361546807532[104] = 0;
   out_6000912361546807532[105] = 0;
   out_6000912361546807532[106] = 0;
   out_6000912361546807532[107] = 0;
   out_6000912361546807532[108] = 1;
   out_6000912361546807532[109] = 0;
   out_6000912361546807532[110] = 0;
   out_6000912361546807532[111] = 0;
   out_6000912361546807532[112] = 0;
   out_6000912361546807532[113] = 0;
   out_6000912361546807532[114] = 0;
   out_6000912361546807532[115] = 0;
   out_6000912361546807532[116] = 0;
   out_6000912361546807532[117] = 0;
   out_6000912361546807532[118] = 0;
   out_6000912361546807532[119] = 0;
   out_6000912361546807532[120] = 1;
}
void h_6(double *state, double *sat_pos, double *out_5247022646599428476) {
   out_5247022646599428476[0] = sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2)) + state[6];
}
void H_6(double *state, double *sat_pos, double *out_6280952107920151244) {
   out_6280952107920151244[0] = (-sat_pos[0] + state[0])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_6280952107920151244[1] = (-sat_pos[1] + state[1])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_6280952107920151244[2] = (-sat_pos[2] + state[2])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_6280952107920151244[3] = 0;
   out_6280952107920151244[4] = 0;
   out_6280952107920151244[5] = 0;
   out_6280952107920151244[6] = 1;
   out_6280952107920151244[7] = 0;
   out_6280952107920151244[8] = 0;
   out_6280952107920151244[9] = 0;
   out_6280952107920151244[10] = 0;
}
void h_20(double *state, double *sat_pos, double *out_3690994761720456636) {
   out_3690994761720456636[0] = sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2)) + sat_pos[3]*state[10] + state[6] + state[9];
}
void H_20(double *state, double *sat_pos, double *out_9122906747733130927) {
   out_9122906747733130927[0] = (-sat_pos[0] + state[0])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_9122906747733130927[1] = (-sat_pos[1] + state[1])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_9122906747733130927[2] = (-sat_pos[2] + state[2])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_9122906747733130927[3] = 0;
   out_9122906747733130927[4] = 0;
   out_9122906747733130927[5] = 0;
   out_9122906747733130927[6] = 1;
   out_9122906747733130927[7] = 0;
   out_9122906747733130927[8] = 0;
   out_9122906747733130927[9] = 1;
   out_9122906747733130927[10] = sat_pos[3];
}
void h_7(double *state, double *sat_pos_vel, double *out_266928008761275148) {
   out_266928008761275148[0] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[3] - state[3])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[4] - state[4])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + (sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + state[7];
}
void H_7(double *state, double *sat_pos_vel, double *out_7588446133012577443) {
   out_7588446133012577443[0] = pow(sat_pos_vel[0] - state[0], 2)*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[0] - state[0])*(sat_pos_vel[1] - state[1])*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[0] - state[0])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[3] - state[3])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_7588446133012577443[1] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[1] - state[1])*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + pow(sat_pos_vel[1] - state[1], 2)*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[4] - state[4])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_7588446133012577443[2] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + pow(sat_pos_vel[2] - state[2], 2)*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[5] - state[5])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_7588446133012577443[3] = -(sat_pos_vel[0] - state[0])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_7588446133012577443[4] = -(sat_pos_vel[1] - state[1])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_7588446133012577443[5] = -(sat_pos_vel[2] - state[2])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_7588446133012577443[6] = 0;
   out_7588446133012577443[7] = 1;
   out_7588446133012577443[8] = 0;
   out_7588446133012577443[9] = 0;
   out_7588446133012577443[10] = 0;
}
void h_21(double *state, double *sat_pos_vel, double *out_266928008761275148) {
   out_266928008761275148[0] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[3] - state[3])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[4] - state[4])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + (sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + state[7];
}
void H_21(double *state, double *sat_pos_vel, double *out_7588446133012577443) {
   out_7588446133012577443[0] = pow(sat_pos_vel[0] - state[0], 2)*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[0] - state[0])*(sat_pos_vel[1] - state[1])*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[0] - state[0])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[3] - state[3])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_7588446133012577443[1] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[1] - state[1])*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + pow(sat_pos_vel[1] - state[1], 2)*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[4] - state[4])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_7588446133012577443[2] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + pow(sat_pos_vel[2] - state[2], 2)*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[5] - state[5])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_7588446133012577443[3] = -(sat_pos_vel[0] - state[0])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_7588446133012577443[4] = -(sat_pos_vel[1] - state[1])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_7588446133012577443[5] = -(sat_pos_vel[2] - state[2])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_7588446133012577443[6] = 0;
   out_7588446133012577443[7] = 1;
   out_7588446133012577443[8] = 0;
   out_7588446133012577443[9] = 0;
   out_7588446133012577443[10] = 0;
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
void gnss_err_fun(double *nom_x, double *delta_x, double *out_966236154794564673) {
  err_fun(nom_x, delta_x, out_966236154794564673);
}
void gnss_inv_err_fun(double *nom_x, double *true_x, double *out_1570495147257342659) {
  inv_err_fun(nom_x, true_x, out_1570495147257342659);
}
void gnss_H_mod_fun(double *state, double *out_1116987290868003958) {
  H_mod_fun(state, out_1116987290868003958);
}
void gnss_f_fun(double *state, double dt, double *out_7944759911088803830) {
  f_fun(state,  dt, out_7944759911088803830);
}
void gnss_F_fun(double *state, double dt, double *out_6000912361546807532) {
  F_fun(state,  dt, out_6000912361546807532);
}
void gnss_h_6(double *state, double *sat_pos, double *out_5247022646599428476) {
  h_6(state, sat_pos, out_5247022646599428476);
}
void gnss_H_6(double *state, double *sat_pos, double *out_6280952107920151244) {
  H_6(state, sat_pos, out_6280952107920151244);
}
void gnss_h_20(double *state, double *sat_pos, double *out_3690994761720456636) {
  h_20(state, sat_pos, out_3690994761720456636);
}
void gnss_H_20(double *state, double *sat_pos, double *out_9122906747733130927) {
  H_20(state, sat_pos, out_9122906747733130927);
}
void gnss_h_7(double *state, double *sat_pos_vel, double *out_266928008761275148) {
  h_7(state, sat_pos_vel, out_266928008761275148);
}
void gnss_H_7(double *state, double *sat_pos_vel, double *out_7588446133012577443) {
  H_7(state, sat_pos_vel, out_7588446133012577443);
}
void gnss_h_21(double *state, double *sat_pos_vel, double *out_266928008761275148) {
  h_21(state, sat_pos_vel, out_266928008761275148);
}
void gnss_H_21(double *state, double *sat_pos_vel, double *out_7588446133012577443) {
  H_21(state, sat_pos_vel, out_7588446133012577443);
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
