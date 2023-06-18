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
void err_fun(double *nom_x, double *delta_x, double *out_6208051589904680687) {
   out_6208051589904680687[0] = delta_x[0] + nom_x[0];
   out_6208051589904680687[1] = delta_x[1] + nom_x[1];
   out_6208051589904680687[2] = delta_x[2] + nom_x[2];
   out_6208051589904680687[3] = delta_x[3] + nom_x[3];
   out_6208051589904680687[4] = delta_x[4] + nom_x[4];
   out_6208051589904680687[5] = delta_x[5] + nom_x[5];
   out_6208051589904680687[6] = delta_x[6] + nom_x[6];
   out_6208051589904680687[7] = delta_x[7] + nom_x[7];
   out_6208051589904680687[8] = delta_x[8] + nom_x[8];
   out_6208051589904680687[9] = delta_x[9] + nom_x[9];
   out_6208051589904680687[10] = delta_x[10] + nom_x[10];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_980651649795713821) {
   out_980651649795713821[0] = -nom_x[0] + true_x[0];
   out_980651649795713821[1] = -nom_x[1] + true_x[1];
   out_980651649795713821[2] = -nom_x[2] + true_x[2];
   out_980651649795713821[3] = -nom_x[3] + true_x[3];
   out_980651649795713821[4] = -nom_x[4] + true_x[4];
   out_980651649795713821[5] = -nom_x[5] + true_x[5];
   out_980651649795713821[6] = -nom_x[6] + true_x[6];
   out_980651649795713821[7] = -nom_x[7] + true_x[7];
   out_980651649795713821[8] = -nom_x[8] + true_x[8];
   out_980651649795713821[9] = -nom_x[9] + true_x[9];
   out_980651649795713821[10] = -nom_x[10] + true_x[10];
}
void H_mod_fun(double *state, double *out_8761108313881456199) {
   out_8761108313881456199[0] = 1.0;
   out_8761108313881456199[1] = 0;
   out_8761108313881456199[2] = 0;
   out_8761108313881456199[3] = 0;
   out_8761108313881456199[4] = 0;
   out_8761108313881456199[5] = 0;
   out_8761108313881456199[6] = 0;
   out_8761108313881456199[7] = 0;
   out_8761108313881456199[8] = 0;
   out_8761108313881456199[9] = 0;
   out_8761108313881456199[10] = 0;
   out_8761108313881456199[11] = 0;
   out_8761108313881456199[12] = 1.0;
   out_8761108313881456199[13] = 0;
   out_8761108313881456199[14] = 0;
   out_8761108313881456199[15] = 0;
   out_8761108313881456199[16] = 0;
   out_8761108313881456199[17] = 0;
   out_8761108313881456199[18] = 0;
   out_8761108313881456199[19] = 0;
   out_8761108313881456199[20] = 0;
   out_8761108313881456199[21] = 0;
   out_8761108313881456199[22] = 0;
   out_8761108313881456199[23] = 0;
   out_8761108313881456199[24] = 1.0;
   out_8761108313881456199[25] = 0;
   out_8761108313881456199[26] = 0;
   out_8761108313881456199[27] = 0;
   out_8761108313881456199[28] = 0;
   out_8761108313881456199[29] = 0;
   out_8761108313881456199[30] = 0;
   out_8761108313881456199[31] = 0;
   out_8761108313881456199[32] = 0;
   out_8761108313881456199[33] = 0;
   out_8761108313881456199[34] = 0;
   out_8761108313881456199[35] = 0;
   out_8761108313881456199[36] = 1.0;
   out_8761108313881456199[37] = 0;
   out_8761108313881456199[38] = 0;
   out_8761108313881456199[39] = 0;
   out_8761108313881456199[40] = 0;
   out_8761108313881456199[41] = 0;
   out_8761108313881456199[42] = 0;
   out_8761108313881456199[43] = 0;
   out_8761108313881456199[44] = 0;
   out_8761108313881456199[45] = 0;
   out_8761108313881456199[46] = 0;
   out_8761108313881456199[47] = 0;
   out_8761108313881456199[48] = 1.0;
   out_8761108313881456199[49] = 0;
   out_8761108313881456199[50] = 0;
   out_8761108313881456199[51] = 0;
   out_8761108313881456199[52] = 0;
   out_8761108313881456199[53] = 0;
   out_8761108313881456199[54] = 0;
   out_8761108313881456199[55] = 0;
   out_8761108313881456199[56] = 0;
   out_8761108313881456199[57] = 0;
   out_8761108313881456199[58] = 0;
   out_8761108313881456199[59] = 0;
   out_8761108313881456199[60] = 1.0;
   out_8761108313881456199[61] = 0;
   out_8761108313881456199[62] = 0;
   out_8761108313881456199[63] = 0;
   out_8761108313881456199[64] = 0;
   out_8761108313881456199[65] = 0;
   out_8761108313881456199[66] = 0;
   out_8761108313881456199[67] = 0;
   out_8761108313881456199[68] = 0;
   out_8761108313881456199[69] = 0;
   out_8761108313881456199[70] = 0;
   out_8761108313881456199[71] = 0;
   out_8761108313881456199[72] = 1.0;
   out_8761108313881456199[73] = 0;
   out_8761108313881456199[74] = 0;
   out_8761108313881456199[75] = 0;
   out_8761108313881456199[76] = 0;
   out_8761108313881456199[77] = 0;
   out_8761108313881456199[78] = 0;
   out_8761108313881456199[79] = 0;
   out_8761108313881456199[80] = 0;
   out_8761108313881456199[81] = 0;
   out_8761108313881456199[82] = 0;
   out_8761108313881456199[83] = 0;
   out_8761108313881456199[84] = 1.0;
   out_8761108313881456199[85] = 0;
   out_8761108313881456199[86] = 0;
   out_8761108313881456199[87] = 0;
   out_8761108313881456199[88] = 0;
   out_8761108313881456199[89] = 0;
   out_8761108313881456199[90] = 0;
   out_8761108313881456199[91] = 0;
   out_8761108313881456199[92] = 0;
   out_8761108313881456199[93] = 0;
   out_8761108313881456199[94] = 0;
   out_8761108313881456199[95] = 0;
   out_8761108313881456199[96] = 1.0;
   out_8761108313881456199[97] = 0;
   out_8761108313881456199[98] = 0;
   out_8761108313881456199[99] = 0;
   out_8761108313881456199[100] = 0;
   out_8761108313881456199[101] = 0;
   out_8761108313881456199[102] = 0;
   out_8761108313881456199[103] = 0;
   out_8761108313881456199[104] = 0;
   out_8761108313881456199[105] = 0;
   out_8761108313881456199[106] = 0;
   out_8761108313881456199[107] = 0;
   out_8761108313881456199[108] = 1.0;
   out_8761108313881456199[109] = 0;
   out_8761108313881456199[110] = 0;
   out_8761108313881456199[111] = 0;
   out_8761108313881456199[112] = 0;
   out_8761108313881456199[113] = 0;
   out_8761108313881456199[114] = 0;
   out_8761108313881456199[115] = 0;
   out_8761108313881456199[116] = 0;
   out_8761108313881456199[117] = 0;
   out_8761108313881456199[118] = 0;
   out_8761108313881456199[119] = 0;
   out_8761108313881456199[120] = 1.0;
}
void f_fun(double *state, double dt, double *out_6985979927194349446) {
   out_6985979927194349446[0] = dt*state[3] + state[0];
   out_6985979927194349446[1] = dt*state[4] + state[1];
   out_6985979927194349446[2] = dt*state[5] + state[2];
   out_6985979927194349446[3] = state[3];
   out_6985979927194349446[4] = state[4];
   out_6985979927194349446[5] = state[5];
   out_6985979927194349446[6] = dt*state[7] + state[6];
   out_6985979927194349446[7] = dt*state[8] + state[7];
   out_6985979927194349446[8] = state[8];
   out_6985979927194349446[9] = state[9];
   out_6985979927194349446[10] = state[10];
}
void F_fun(double *state, double dt, double *out_5398596809828011208) {
   out_5398596809828011208[0] = 1;
   out_5398596809828011208[1] = 0;
   out_5398596809828011208[2] = 0;
   out_5398596809828011208[3] = dt;
   out_5398596809828011208[4] = 0;
   out_5398596809828011208[5] = 0;
   out_5398596809828011208[6] = 0;
   out_5398596809828011208[7] = 0;
   out_5398596809828011208[8] = 0;
   out_5398596809828011208[9] = 0;
   out_5398596809828011208[10] = 0;
   out_5398596809828011208[11] = 0;
   out_5398596809828011208[12] = 1;
   out_5398596809828011208[13] = 0;
   out_5398596809828011208[14] = 0;
   out_5398596809828011208[15] = dt;
   out_5398596809828011208[16] = 0;
   out_5398596809828011208[17] = 0;
   out_5398596809828011208[18] = 0;
   out_5398596809828011208[19] = 0;
   out_5398596809828011208[20] = 0;
   out_5398596809828011208[21] = 0;
   out_5398596809828011208[22] = 0;
   out_5398596809828011208[23] = 0;
   out_5398596809828011208[24] = 1;
   out_5398596809828011208[25] = 0;
   out_5398596809828011208[26] = 0;
   out_5398596809828011208[27] = dt;
   out_5398596809828011208[28] = 0;
   out_5398596809828011208[29] = 0;
   out_5398596809828011208[30] = 0;
   out_5398596809828011208[31] = 0;
   out_5398596809828011208[32] = 0;
   out_5398596809828011208[33] = 0;
   out_5398596809828011208[34] = 0;
   out_5398596809828011208[35] = 0;
   out_5398596809828011208[36] = 1;
   out_5398596809828011208[37] = 0;
   out_5398596809828011208[38] = 0;
   out_5398596809828011208[39] = 0;
   out_5398596809828011208[40] = 0;
   out_5398596809828011208[41] = 0;
   out_5398596809828011208[42] = 0;
   out_5398596809828011208[43] = 0;
   out_5398596809828011208[44] = 0;
   out_5398596809828011208[45] = 0;
   out_5398596809828011208[46] = 0;
   out_5398596809828011208[47] = 0;
   out_5398596809828011208[48] = 1;
   out_5398596809828011208[49] = 0;
   out_5398596809828011208[50] = 0;
   out_5398596809828011208[51] = 0;
   out_5398596809828011208[52] = 0;
   out_5398596809828011208[53] = 0;
   out_5398596809828011208[54] = 0;
   out_5398596809828011208[55] = 0;
   out_5398596809828011208[56] = 0;
   out_5398596809828011208[57] = 0;
   out_5398596809828011208[58] = 0;
   out_5398596809828011208[59] = 0;
   out_5398596809828011208[60] = 1;
   out_5398596809828011208[61] = 0;
   out_5398596809828011208[62] = 0;
   out_5398596809828011208[63] = 0;
   out_5398596809828011208[64] = 0;
   out_5398596809828011208[65] = 0;
   out_5398596809828011208[66] = 0;
   out_5398596809828011208[67] = 0;
   out_5398596809828011208[68] = 0;
   out_5398596809828011208[69] = 0;
   out_5398596809828011208[70] = 0;
   out_5398596809828011208[71] = 0;
   out_5398596809828011208[72] = 1;
   out_5398596809828011208[73] = dt;
   out_5398596809828011208[74] = 0;
   out_5398596809828011208[75] = 0;
   out_5398596809828011208[76] = 0;
   out_5398596809828011208[77] = 0;
   out_5398596809828011208[78] = 0;
   out_5398596809828011208[79] = 0;
   out_5398596809828011208[80] = 0;
   out_5398596809828011208[81] = 0;
   out_5398596809828011208[82] = 0;
   out_5398596809828011208[83] = 0;
   out_5398596809828011208[84] = 1;
   out_5398596809828011208[85] = dt;
   out_5398596809828011208[86] = 0;
   out_5398596809828011208[87] = 0;
   out_5398596809828011208[88] = 0;
   out_5398596809828011208[89] = 0;
   out_5398596809828011208[90] = 0;
   out_5398596809828011208[91] = 0;
   out_5398596809828011208[92] = 0;
   out_5398596809828011208[93] = 0;
   out_5398596809828011208[94] = 0;
   out_5398596809828011208[95] = 0;
   out_5398596809828011208[96] = 1;
   out_5398596809828011208[97] = 0;
   out_5398596809828011208[98] = 0;
   out_5398596809828011208[99] = 0;
   out_5398596809828011208[100] = 0;
   out_5398596809828011208[101] = 0;
   out_5398596809828011208[102] = 0;
   out_5398596809828011208[103] = 0;
   out_5398596809828011208[104] = 0;
   out_5398596809828011208[105] = 0;
   out_5398596809828011208[106] = 0;
   out_5398596809828011208[107] = 0;
   out_5398596809828011208[108] = 1;
   out_5398596809828011208[109] = 0;
   out_5398596809828011208[110] = 0;
   out_5398596809828011208[111] = 0;
   out_5398596809828011208[112] = 0;
   out_5398596809828011208[113] = 0;
   out_5398596809828011208[114] = 0;
   out_5398596809828011208[115] = 0;
   out_5398596809828011208[116] = 0;
   out_5398596809828011208[117] = 0;
   out_5398596809828011208[118] = 0;
   out_5398596809828011208[119] = 0;
   out_5398596809828011208[120] = 1;
}
void h_6(double *state, double *sat_pos, double *out_854109254235318073) {
   out_854109254235318073[0] = sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2)) + state[6];
}
void H_6(double *state, double *sat_pos, double *out_4878360041893525515) {
   out_4878360041893525515[0] = (-sat_pos[0] + state[0])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_4878360041893525515[1] = (-sat_pos[1] + state[1])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_4878360041893525515[2] = (-sat_pos[2] + state[2])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_4878360041893525515[3] = 0;
   out_4878360041893525515[4] = 0;
   out_4878360041893525515[5] = 0;
   out_4878360041893525515[6] = 1;
   out_4878360041893525515[7] = 0;
   out_4878360041893525515[8] = 0;
   out_4878360041893525515[9] = 0;
   out_4878360041893525515[10] = 0;
}
void h_20(double *state, double *sat_pos, double *out_3910060068815622044) {
   out_3910060068815622044[0] = sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2)) + sat_pos[3]*state[10] + state[6] + state[9];
}
void H_20(double *state, double *sat_pos, double *out_7601181949165199926) {
   out_7601181949165199926[0] = (-sat_pos[0] + state[0])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_7601181949165199926[1] = (-sat_pos[1] + state[1])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_7601181949165199926[2] = (-sat_pos[2] + state[2])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_7601181949165199926[3] = 0;
   out_7601181949165199926[4] = 0;
   out_7601181949165199926[5] = 0;
   out_7601181949165199926[6] = 1;
   out_7601181949165199926[7] = 0;
   out_7601181949165199926[8] = 0;
   out_7601181949165199926[9] = 1;
   out_7601181949165199926[10] = sat_pos[3];
}
void h_7(double *state, double *sat_pos_vel, double *out_7752585033610334316) {
   out_7752585033610334316[0] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[3] - state[3])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[4] - state[4])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + (sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + state[7];
}
void H_7(double *state, double *sat_pos_vel, double *out_8389742934130346329) {
   out_8389742934130346329[0] = pow(sat_pos_vel[0] - state[0], 2)*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[0] - state[0])*(sat_pos_vel[1] - state[1])*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[0] - state[0])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[3] - state[3])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_8389742934130346329[1] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[1] - state[1])*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + pow(sat_pos_vel[1] - state[1], 2)*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[4] - state[4])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_8389742934130346329[2] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + pow(sat_pos_vel[2] - state[2], 2)*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[5] - state[5])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_8389742934130346329[3] = -(sat_pos_vel[0] - state[0])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_8389742934130346329[4] = -(sat_pos_vel[1] - state[1])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_8389742934130346329[5] = -(sat_pos_vel[2] - state[2])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_8389742934130346329[6] = 0;
   out_8389742934130346329[7] = 1;
   out_8389742934130346329[8] = 0;
   out_8389742934130346329[9] = 0;
   out_8389742934130346329[10] = 0;
}
void h_21(double *state, double *sat_pos_vel, double *out_7752585033610334316) {
   out_7752585033610334316[0] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[3] - state[3])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[4] - state[4])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + (sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + state[7];
}
void H_21(double *state, double *sat_pos_vel, double *out_8389742934130346329) {
   out_8389742934130346329[0] = pow(sat_pos_vel[0] - state[0], 2)*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[0] - state[0])*(sat_pos_vel[1] - state[1])*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[0] - state[0])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[3] - state[3])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_8389742934130346329[1] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[1] - state[1])*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + pow(sat_pos_vel[1] - state[1], 2)*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[4] - state[4])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_8389742934130346329[2] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + pow(sat_pos_vel[2] - state[2], 2)*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[5] - state[5])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_8389742934130346329[3] = -(sat_pos_vel[0] - state[0])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_8389742934130346329[4] = -(sat_pos_vel[1] - state[1])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_8389742934130346329[5] = -(sat_pos_vel[2] - state[2])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_8389742934130346329[6] = 0;
   out_8389742934130346329[7] = 1;
   out_8389742934130346329[8] = 0;
   out_8389742934130346329[9] = 0;
   out_8389742934130346329[10] = 0;
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
void gnss_err_fun(double *nom_x, double *delta_x, double *out_6208051589904680687) {
  err_fun(nom_x, delta_x, out_6208051589904680687);
}
void gnss_inv_err_fun(double *nom_x, double *true_x, double *out_980651649795713821) {
  inv_err_fun(nom_x, true_x, out_980651649795713821);
}
void gnss_H_mod_fun(double *state, double *out_8761108313881456199) {
  H_mod_fun(state, out_8761108313881456199);
}
void gnss_f_fun(double *state, double dt, double *out_6985979927194349446) {
  f_fun(state,  dt, out_6985979927194349446);
}
void gnss_F_fun(double *state, double dt, double *out_5398596809828011208) {
  F_fun(state,  dt, out_5398596809828011208);
}
void gnss_h_6(double *state, double *sat_pos, double *out_854109254235318073) {
  h_6(state, sat_pos, out_854109254235318073);
}
void gnss_H_6(double *state, double *sat_pos, double *out_4878360041893525515) {
  H_6(state, sat_pos, out_4878360041893525515);
}
void gnss_h_20(double *state, double *sat_pos, double *out_3910060068815622044) {
  h_20(state, sat_pos, out_3910060068815622044);
}
void gnss_H_20(double *state, double *sat_pos, double *out_7601181949165199926) {
  H_20(state, sat_pos, out_7601181949165199926);
}
void gnss_h_7(double *state, double *sat_pos_vel, double *out_7752585033610334316) {
  h_7(state, sat_pos_vel, out_7752585033610334316);
}
void gnss_H_7(double *state, double *sat_pos_vel, double *out_8389742934130346329) {
  H_7(state, sat_pos_vel, out_8389742934130346329);
}
void gnss_h_21(double *state, double *sat_pos_vel, double *out_7752585033610334316) {
  h_21(state, sat_pos_vel, out_7752585033610334316);
}
void gnss_H_21(double *state, double *sat_pos_vel, double *out_8389742934130346329) {
  H_21(state, sat_pos_vel, out_8389742934130346329);
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
