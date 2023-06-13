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
void err_fun(double *nom_x, double *delta_x, double *out_6610478330683822785) {
   out_6610478330683822785[0] = delta_x[0] + nom_x[0];
   out_6610478330683822785[1] = delta_x[1] + nom_x[1];
   out_6610478330683822785[2] = delta_x[2] + nom_x[2];
   out_6610478330683822785[3] = delta_x[3] + nom_x[3];
   out_6610478330683822785[4] = delta_x[4] + nom_x[4];
   out_6610478330683822785[5] = delta_x[5] + nom_x[5];
   out_6610478330683822785[6] = delta_x[6] + nom_x[6];
   out_6610478330683822785[7] = delta_x[7] + nom_x[7];
   out_6610478330683822785[8] = delta_x[8] + nom_x[8];
   out_6610478330683822785[9] = delta_x[9] + nom_x[9];
   out_6610478330683822785[10] = delta_x[10] + nom_x[10];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_3052097266079563493) {
   out_3052097266079563493[0] = -nom_x[0] + true_x[0];
   out_3052097266079563493[1] = -nom_x[1] + true_x[1];
   out_3052097266079563493[2] = -nom_x[2] + true_x[2];
   out_3052097266079563493[3] = -nom_x[3] + true_x[3];
   out_3052097266079563493[4] = -nom_x[4] + true_x[4];
   out_3052097266079563493[5] = -nom_x[5] + true_x[5];
   out_3052097266079563493[6] = -nom_x[6] + true_x[6];
   out_3052097266079563493[7] = -nom_x[7] + true_x[7];
   out_3052097266079563493[8] = -nom_x[8] + true_x[8];
   out_3052097266079563493[9] = -nom_x[9] + true_x[9];
   out_3052097266079563493[10] = -nom_x[10] + true_x[10];
}
void H_mod_fun(double *state, double *out_7863374150261741197) {
   out_7863374150261741197[0] = 1.0;
   out_7863374150261741197[1] = 0;
   out_7863374150261741197[2] = 0;
   out_7863374150261741197[3] = 0;
   out_7863374150261741197[4] = 0;
   out_7863374150261741197[5] = 0;
   out_7863374150261741197[6] = 0;
   out_7863374150261741197[7] = 0;
   out_7863374150261741197[8] = 0;
   out_7863374150261741197[9] = 0;
   out_7863374150261741197[10] = 0;
   out_7863374150261741197[11] = 0;
   out_7863374150261741197[12] = 1.0;
   out_7863374150261741197[13] = 0;
   out_7863374150261741197[14] = 0;
   out_7863374150261741197[15] = 0;
   out_7863374150261741197[16] = 0;
   out_7863374150261741197[17] = 0;
   out_7863374150261741197[18] = 0;
   out_7863374150261741197[19] = 0;
   out_7863374150261741197[20] = 0;
   out_7863374150261741197[21] = 0;
   out_7863374150261741197[22] = 0;
   out_7863374150261741197[23] = 0;
   out_7863374150261741197[24] = 1.0;
   out_7863374150261741197[25] = 0;
   out_7863374150261741197[26] = 0;
   out_7863374150261741197[27] = 0;
   out_7863374150261741197[28] = 0;
   out_7863374150261741197[29] = 0;
   out_7863374150261741197[30] = 0;
   out_7863374150261741197[31] = 0;
   out_7863374150261741197[32] = 0;
   out_7863374150261741197[33] = 0;
   out_7863374150261741197[34] = 0;
   out_7863374150261741197[35] = 0;
   out_7863374150261741197[36] = 1.0;
   out_7863374150261741197[37] = 0;
   out_7863374150261741197[38] = 0;
   out_7863374150261741197[39] = 0;
   out_7863374150261741197[40] = 0;
   out_7863374150261741197[41] = 0;
   out_7863374150261741197[42] = 0;
   out_7863374150261741197[43] = 0;
   out_7863374150261741197[44] = 0;
   out_7863374150261741197[45] = 0;
   out_7863374150261741197[46] = 0;
   out_7863374150261741197[47] = 0;
   out_7863374150261741197[48] = 1.0;
   out_7863374150261741197[49] = 0;
   out_7863374150261741197[50] = 0;
   out_7863374150261741197[51] = 0;
   out_7863374150261741197[52] = 0;
   out_7863374150261741197[53] = 0;
   out_7863374150261741197[54] = 0;
   out_7863374150261741197[55] = 0;
   out_7863374150261741197[56] = 0;
   out_7863374150261741197[57] = 0;
   out_7863374150261741197[58] = 0;
   out_7863374150261741197[59] = 0;
   out_7863374150261741197[60] = 1.0;
   out_7863374150261741197[61] = 0;
   out_7863374150261741197[62] = 0;
   out_7863374150261741197[63] = 0;
   out_7863374150261741197[64] = 0;
   out_7863374150261741197[65] = 0;
   out_7863374150261741197[66] = 0;
   out_7863374150261741197[67] = 0;
   out_7863374150261741197[68] = 0;
   out_7863374150261741197[69] = 0;
   out_7863374150261741197[70] = 0;
   out_7863374150261741197[71] = 0;
   out_7863374150261741197[72] = 1.0;
   out_7863374150261741197[73] = 0;
   out_7863374150261741197[74] = 0;
   out_7863374150261741197[75] = 0;
   out_7863374150261741197[76] = 0;
   out_7863374150261741197[77] = 0;
   out_7863374150261741197[78] = 0;
   out_7863374150261741197[79] = 0;
   out_7863374150261741197[80] = 0;
   out_7863374150261741197[81] = 0;
   out_7863374150261741197[82] = 0;
   out_7863374150261741197[83] = 0;
   out_7863374150261741197[84] = 1.0;
   out_7863374150261741197[85] = 0;
   out_7863374150261741197[86] = 0;
   out_7863374150261741197[87] = 0;
   out_7863374150261741197[88] = 0;
   out_7863374150261741197[89] = 0;
   out_7863374150261741197[90] = 0;
   out_7863374150261741197[91] = 0;
   out_7863374150261741197[92] = 0;
   out_7863374150261741197[93] = 0;
   out_7863374150261741197[94] = 0;
   out_7863374150261741197[95] = 0;
   out_7863374150261741197[96] = 1.0;
   out_7863374150261741197[97] = 0;
   out_7863374150261741197[98] = 0;
   out_7863374150261741197[99] = 0;
   out_7863374150261741197[100] = 0;
   out_7863374150261741197[101] = 0;
   out_7863374150261741197[102] = 0;
   out_7863374150261741197[103] = 0;
   out_7863374150261741197[104] = 0;
   out_7863374150261741197[105] = 0;
   out_7863374150261741197[106] = 0;
   out_7863374150261741197[107] = 0;
   out_7863374150261741197[108] = 1.0;
   out_7863374150261741197[109] = 0;
   out_7863374150261741197[110] = 0;
   out_7863374150261741197[111] = 0;
   out_7863374150261741197[112] = 0;
   out_7863374150261741197[113] = 0;
   out_7863374150261741197[114] = 0;
   out_7863374150261741197[115] = 0;
   out_7863374150261741197[116] = 0;
   out_7863374150261741197[117] = 0;
   out_7863374150261741197[118] = 0;
   out_7863374150261741197[119] = 0;
   out_7863374150261741197[120] = 1.0;
}
void f_fun(double *state, double dt, double *out_1355891940419784179) {
   out_1355891940419784179[0] = dt*state[3] + state[0];
   out_1355891940419784179[1] = dt*state[4] + state[1];
   out_1355891940419784179[2] = dt*state[5] + state[2];
   out_1355891940419784179[3] = state[3];
   out_1355891940419784179[4] = state[4];
   out_1355891940419784179[5] = state[5];
   out_1355891940419784179[6] = dt*state[7] + state[6];
   out_1355891940419784179[7] = dt*state[8] + state[7];
   out_1355891940419784179[8] = state[8];
   out_1355891940419784179[9] = state[9];
   out_1355891940419784179[10] = state[10];
}
void F_fun(double *state, double dt, double *out_6103640977023954324) {
   out_6103640977023954324[0] = 1;
   out_6103640977023954324[1] = 0;
   out_6103640977023954324[2] = 0;
   out_6103640977023954324[3] = dt;
   out_6103640977023954324[4] = 0;
   out_6103640977023954324[5] = 0;
   out_6103640977023954324[6] = 0;
   out_6103640977023954324[7] = 0;
   out_6103640977023954324[8] = 0;
   out_6103640977023954324[9] = 0;
   out_6103640977023954324[10] = 0;
   out_6103640977023954324[11] = 0;
   out_6103640977023954324[12] = 1;
   out_6103640977023954324[13] = 0;
   out_6103640977023954324[14] = 0;
   out_6103640977023954324[15] = dt;
   out_6103640977023954324[16] = 0;
   out_6103640977023954324[17] = 0;
   out_6103640977023954324[18] = 0;
   out_6103640977023954324[19] = 0;
   out_6103640977023954324[20] = 0;
   out_6103640977023954324[21] = 0;
   out_6103640977023954324[22] = 0;
   out_6103640977023954324[23] = 0;
   out_6103640977023954324[24] = 1;
   out_6103640977023954324[25] = 0;
   out_6103640977023954324[26] = 0;
   out_6103640977023954324[27] = dt;
   out_6103640977023954324[28] = 0;
   out_6103640977023954324[29] = 0;
   out_6103640977023954324[30] = 0;
   out_6103640977023954324[31] = 0;
   out_6103640977023954324[32] = 0;
   out_6103640977023954324[33] = 0;
   out_6103640977023954324[34] = 0;
   out_6103640977023954324[35] = 0;
   out_6103640977023954324[36] = 1;
   out_6103640977023954324[37] = 0;
   out_6103640977023954324[38] = 0;
   out_6103640977023954324[39] = 0;
   out_6103640977023954324[40] = 0;
   out_6103640977023954324[41] = 0;
   out_6103640977023954324[42] = 0;
   out_6103640977023954324[43] = 0;
   out_6103640977023954324[44] = 0;
   out_6103640977023954324[45] = 0;
   out_6103640977023954324[46] = 0;
   out_6103640977023954324[47] = 0;
   out_6103640977023954324[48] = 1;
   out_6103640977023954324[49] = 0;
   out_6103640977023954324[50] = 0;
   out_6103640977023954324[51] = 0;
   out_6103640977023954324[52] = 0;
   out_6103640977023954324[53] = 0;
   out_6103640977023954324[54] = 0;
   out_6103640977023954324[55] = 0;
   out_6103640977023954324[56] = 0;
   out_6103640977023954324[57] = 0;
   out_6103640977023954324[58] = 0;
   out_6103640977023954324[59] = 0;
   out_6103640977023954324[60] = 1;
   out_6103640977023954324[61] = 0;
   out_6103640977023954324[62] = 0;
   out_6103640977023954324[63] = 0;
   out_6103640977023954324[64] = 0;
   out_6103640977023954324[65] = 0;
   out_6103640977023954324[66] = 0;
   out_6103640977023954324[67] = 0;
   out_6103640977023954324[68] = 0;
   out_6103640977023954324[69] = 0;
   out_6103640977023954324[70] = 0;
   out_6103640977023954324[71] = 0;
   out_6103640977023954324[72] = 1;
   out_6103640977023954324[73] = dt;
   out_6103640977023954324[74] = 0;
   out_6103640977023954324[75] = 0;
   out_6103640977023954324[76] = 0;
   out_6103640977023954324[77] = 0;
   out_6103640977023954324[78] = 0;
   out_6103640977023954324[79] = 0;
   out_6103640977023954324[80] = 0;
   out_6103640977023954324[81] = 0;
   out_6103640977023954324[82] = 0;
   out_6103640977023954324[83] = 0;
   out_6103640977023954324[84] = 1;
   out_6103640977023954324[85] = dt;
   out_6103640977023954324[86] = 0;
   out_6103640977023954324[87] = 0;
   out_6103640977023954324[88] = 0;
   out_6103640977023954324[89] = 0;
   out_6103640977023954324[90] = 0;
   out_6103640977023954324[91] = 0;
   out_6103640977023954324[92] = 0;
   out_6103640977023954324[93] = 0;
   out_6103640977023954324[94] = 0;
   out_6103640977023954324[95] = 0;
   out_6103640977023954324[96] = 1;
   out_6103640977023954324[97] = 0;
   out_6103640977023954324[98] = 0;
   out_6103640977023954324[99] = 0;
   out_6103640977023954324[100] = 0;
   out_6103640977023954324[101] = 0;
   out_6103640977023954324[102] = 0;
   out_6103640977023954324[103] = 0;
   out_6103640977023954324[104] = 0;
   out_6103640977023954324[105] = 0;
   out_6103640977023954324[106] = 0;
   out_6103640977023954324[107] = 0;
   out_6103640977023954324[108] = 1;
   out_6103640977023954324[109] = 0;
   out_6103640977023954324[110] = 0;
   out_6103640977023954324[111] = 0;
   out_6103640977023954324[112] = 0;
   out_6103640977023954324[113] = 0;
   out_6103640977023954324[114] = 0;
   out_6103640977023954324[115] = 0;
   out_6103640977023954324[116] = 0;
   out_6103640977023954324[117] = 0;
   out_6103640977023954324[118] = 0;
   out_6103640977023954324[119] = 0;
   out_6103640977023954324[120] = 1;
}
void h_6(double *state, double *sat_pos, double *out_8639638469545015026) {
   out_8639638469545015026[0] = sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2)) + state[6];
}
void H_6(double *state, double *sat_pos, double *out_3815070702462107900) {
   out_3815070702462107900[0] = (-sat_pos[0] + state[0])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_3815070702462107900[1] = (-sat_pos[1] + state[1])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_3815070702462107900[2] = (-sat_pos[2] + state[2])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_3815070702462107900[3] = 0;
   out_3815070702462107900[4] = 0;
   out_3815070702462107900[5] = 0;
   out_3815070702462107900[6] = 1;
   out_3815070702462107900[7] = 0;
   out_3815070702462107900[8] = 0;
   out_3815070702462107900[9] = 0;
   out_3815070702462107900[10] = 0;
}
void h_20(double *state, double *sat_pos, double *out_371384230938458631) {
   out_371384230938458631[0] = sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2)) + sat_pos[3]*state[10] + state[6] + state[9];
}
void H_20(double *state, double *sat_pos, double *out_5682384660731021071) {
   out_5682384660731021071[0] = (-sat_pos[0] + state[0])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_5682384660731021071[1] = (-sat_pos[1] + state[1])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_5682384660731021071[2] = (-sat_pos[2] + state[2])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_5682384660731021071[3] = 0;
   out_5682384660731021071[4] = 0;
   out_5682384660731021071[5] = 0;
   out_5682384660731021071[6] = 1;
   out_5682384660731021071[7] = 0;
   out_5682384660731021071[8] = 0;
   out_5682384660731021071[9] = 1;
   out_5682384660731021071[10] = sat_pos[3];
}
void h_7(double *state, double *sat_pos_vel, double *out_4876434118703082912) {
   out_4876434118703082912[0] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[3] - state[3])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[4] - state[4])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + (sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + state[7];
}
void H_7(double *state, double *sat_pos_vel, double *out_5591453878569163415) {
   out_5591453878569163415[0] = pow(sat_pos_vel[0] - state[0], 2)*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[0] - state[0])*(sat_pos_vel[1] - state[1])*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[0] - state[0])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[3] - state[3])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_5591453878569163415[1] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[1] - state[1])*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + pow(sat_pos_vel[1] - state[1], 2)*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[4] - state[4])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_5591453878569163415[2] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + pow(sat_pos_vel[2] - state[2], 2)*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[5] - state[5])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_5591453878569163415[3] = -(sat_pos_vel[0] - state[0])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_5591453878569163415[4] = -(sat_pos_vel[1] - state[1])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_5591453878569163415[5] = -(sat_pos_vel[2] - state[2])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_5591453878569163415[6] = 0;
   out_5591453878569163415[7] = 1;
   out_5591453878569163415[8] = 0;
   out_5591453878569163415[9] = 0;
   out_5591453878569163415[10] = 0;
}
void h_21(double *state, double *sat_pos_vel, double *out_4876434118703082912) {
   out_4876434118703082912[0] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[3] - state[3])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[4] - state[4])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + (sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + state[7];
}
void H_21(double *state, double *sat_pos_vel, double *out_5591453878569163415) {
   out_5591453878569163415[0] = pow(sat_pos_vel[0] - state[0], 2)*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[0] - state[0])*(sat_pos_vel[1] - state[1])*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[0] - state[0])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[3] - state[3])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_5591453878569163415[1] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[1] - state[1])*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + pow(sat_pos_vel[1] - state[1], 2)*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[4] - state[4])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_5591453878569163415[2] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + pow(sat_pos_vel[2] - state[2], 2)*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[5] - state[5])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_5591453878569163415[3] = -(sat_pos_vel[0] - state[0])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_5591453878569163415[4] = -(sat_pos_vel[1] - state[1])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_5591453878569163415[5] = -(sat_pos_vel[2] - state[2])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_5591453878569163415[6] = 0;
   out_5591453878569163415[7] = 1;
   out_5591453878569163415[8] = 0;
   out_5591453878569163415[9] = 0;
   out_5591453878569163415[10] = 0;
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
void gnss_err_fun(double *nom_x, double *delta_x, double *out_6610478330683822785) {
  err_fun(nom_x, delta_x, out_6610478330683822785);
}
void gnss_inv_err_fun(double *nom_x, double *true_x, double *out_3052097266079563493) {
  inv_err_fun(nom_x, true_x, out_3052097266079563493);
}
void gnss_H_mod_fun(double *state, double *out_7863374150261741197) {
  H_mod_fun(state, out_7863374150261741197);
}
void gnss_f_fun(double *state, double dt, double *out_1355891940419784179) {
  f_fun(state,  dt, out_1355891940419784179);
}
void gnss_F_fun(double *state, double dt, double *out_6103640977023954324) {
  F_fun(state,  dt, out_6103640977023954324);
}
void gnss_h_6(double *state, double *sat_pos, double *out_8639638469545015026) {
  h_6(state, sat_pos, out_8639638469545015026);
}
void gnss_H_6(double *state, double *sat_pos, double *out_3815070702462107900) {
  H_6(state, sat_pos, out_3815070702462107900);
}
void gnss_h_20(double *state, double *sat_pos, double *out_371384230938458631) {
  h_20(state, sat_pos, out_371384230938458631);
}
void gnss_H_20(double *state, double *sat_pos, double *out_5682384660731021071) {
  H_20(state, sat_pos, out_5682384660731021071);
}
void gnss_h_7(double *state, double *sat_pos_vel, double *out_4876434118703082912) {
  h_7(state, sat_pos_vel, out_4876434118703082912);
}
void gnss_H_7(double *state, double *sat_pos_vel, double *out_5591453878569163415) {
  H_7(state, sat_pos_vel, out_5591453878569163415);
}
void gnss_h_21(double *state, double *sat_pos_vel, double *out_4876434118703082912) {
  h_21(state, sat_pos_vel, out_4876434118703082912);
}
void gnss_H_21(double *state, double *sat_pos_vel, double *out_5591453878569163415) {
  H_21(state, sat_pos_vel, out_5591453878569163415);
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
