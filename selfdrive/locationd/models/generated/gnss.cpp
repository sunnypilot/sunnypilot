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
void err_fun(double *nom_x, double *delta_x, double *out_2474256111087528474) {
   out_2474256111087528474[0] = delta_x[0] + nom_x[0];
   out_2474256111087528474[1] = delta_x[1] + nom_x[1];
   out_2474256111087528474[2] = delta_x[2] + nom_x[2];
   out_2474256111087528474[3] = delta_x[3] + nom_x[3];
   out_2474256111087528474[4] = delta_x[4] + nom_x[4];
   out_2474256111087528474[5] = delta_x[5] + nom_x[5];
   out_2474256111087528474[6] = delta_x[6] + nom_x[6];
   out_2474256111087528474[7] = delta_x[7] + nom_x[7];
   out_2474256111087528474[8] = delta_x[8] + nom_x[8];
   out_2474256111087528474[9] = delta_x[9] + nom_x[9];
   out_2474256111087528474[10] = delta_x[10] + nom_x[10];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_7051622024455451737) {
   out_7051622024455451737[0] = -nom_x[0] + true_x[0];
   out_7051622024455451737[1] = -nom_x[1] + true_x[1];
   out_7051622024455451737[2] = -nom_x[2] + true_x[2];
   out_7051622024455451737[3] = -nom_x[3] + true_x[3];
   out_7051622024455451737[4] = -nom_x[4] + true_x[4];
   out_7051622024455451737[5] = -nom_x[5] + true_x[5];
   out_7051622024455451737[6] = -nom_x[6] + true_x[6];
   out_7051622024455451737[7] = -nom_x[7] + true_x[7];
   out_7051622024455451737[8] = -nom_x[8] + true_x[8];
   out_7051622024455451737[9] = -nom_x[9] + true_x[9];
   out_7051622024455451737[10] = -nom_x[10] + true_x[10];
}
void H_mod_fun(double *state, double *out_7896233018555451228) {
   out_7896233018555451228[0] = 1.0;
   out_7896233018555451228[1] = 0;
   out_7896233018555451228[2] = 0;
   out_7896233018555451228[3] = 0;
   out_7896233018555451228[4] = 0;
   out_7896233018555451228[5] = 0;
   out_7896233018555451228[6] = 0;
   out_7896233018555451228[7] = 0;
   out_7896233018555451228[8] = 0;
   out_7896233018555451228[9] = 0;
   out_7896233018555451228[10] = 0;
   out_7896233018555451228[11] = 0;
   out_7896233018555451228[12] = 1.0;
   out_7896233018555451228[13] = 0;
   out_7896233018555451228[14] = 0;
   out_7896233018555451228[15] = 0;
   out_7896233018555451228[16] = 0;
   out_7896233018555451228[17] = 0;
   out_7896233018555451228[18] = 0;
   out_7896233018555451228[19] = 0;
   out_7896233018555451228[20] = 0;
   out_7896233018555451228[21] = 0;
   out_7896233018555451228[22] = 0;
   out_7896233018555451228[23] = 0;
   out_7896233018555451228[24] = 1.0;
   out_7896233018555451228[25] = 0;
   out_7896233018555451228[26] = 0;
   out_7896233018555451228[27] = 0;
   out_7896233018555451228[28] = 0;
   out_7896233018555451228[29] = 0;
   out_7896233018555451228[30] = 0;
   out_7896233018555451228[31] = 0;
   out_7896233018555451228[32] = 0;
   out_7896233018555451228[33] = 0;
   out_7896233018555451228[34] = 0;
   out_7896233018555451228[35] = 0;
   out_7896233018555451228[36] = 1.0;
   out_7896233018555451228[37] = 0;
   out_7896233018555451228[38] = 0;
   out_7896233018555451228[39] = 0;
   out_7896233018555451228[40] = 0;
   out_7896233018555451228[41] = 0;
   out_7896233018555451228[42] = 0;
   out_7896233018555451228[43] = 0;
   out_7896233018555451228[44] = 0;
   out_7896233018555451228[45] = 0;
   out_7896233018555451228[46] = 0;
   out_7896233018555451228[47] = 0;
   out_7896233018555451228[48] = 1.0;
   out_7896233018555451228[49] = 0;
   out_7896233018555451228[50] = 0;
   out_7896233018555451228[51] = 0;
   out_7896233018555451228[52] = 0;
   out_7896233018555451228[53] = 0;
   out_7896233018555451228[54] = 0;
   out_7896233018555451228[55] = 0;
   out_7896233018555451228[56] = 0;
   out_7896233018555451228[57] = 0;
   out_7896233018555451228[58] = 0;
   out_7896233018555451228[59] = 0;
   out_7896233018555451228[60] = 1.0;
   out_7896233018555451228[61] = 0;
   out_7896233018555451228[62] = 0;
   out_7896233018555451228[63] = 0;
   out_7896233018555451228[64] = 0;
   out_7896233018555451228[65] = 0;
   out_7896233018555451228[66] = 0;
   out_7896233018555451228[67] = 0;
   out_7896233018555451228[68] = 0;
   out_7896233018555451228[69] = 0;
   out_7896233018555451228[70] = 0;
   out_7896233018555451228[71] = 0;
   out_7896233018555451228[72] = 1.0;
   out_7896233018555451228[73] = 0;
   out_7896233018555451228[74] = 0;
   out_7896233018555451228[75] = 0;
   out_7896233018555451228[76] = 0;
   out_7896233018555451228[77] = 0;
   out_7896233018555451228[78] = 0;
   out_7896233018555451228[79] = 0;
   out_7896233018555451228[80] = 0;
   out_7896233018555451228[81] = 0;
   out_7896233018555451228[82] = 0;
   out_7896233018555451228[83] = 0;
   out_7896233018555451228[84] = 1.0;
   out_7896233018555451228[85] = 0;
   out_7896233018555451228[86] = 0;
   out_7896233018555451228[87] = 0;
   out_7896233018555451228[88] = 0;
   out_7896233018555451228[89] = 0;
   out_7896233018555451228[90] = 0;
   out_7896233018555451228[91] = 0;
   out_7896233018555451228[92] = 0;
   out_7896233018555451228[93] = 0;
   out_7896233018555451228[94] = 0;
   out_7896233018555451228[95] = 0;
   out_7896233018555451228[96] = 1.0;
   out_7896233018555451228[97] = 0;
   out_7896233018555451228[98] = 0;
   out_7896233018555451228[99] = 0;
   out_7896233018555451228[100] = 0;
   out_7896233018555451228[101] = 0;
   out_7896233018555451228[102] = 0;
   out_7896233018555451228[103] = 0;
   out_7896233018555451228[104] = 0;
   out_7896233018555451228[105] = 0;
   out_7896233018555451228[106] = 0;
   out_7896233018555451228[107] = 0;
   out_7896233018555451228[108] = 1.0;
   out_7896233018555451228[109] = 0;
   out_7896233018555451228[110] = 0;
   out_7896233018555451228[111] = 0;
   out_7896233018555451228[112] = 0;
   out_7896233018555451228[113] = 0;
   out_7896233018555451228[114] = 0;
   out_7896233018555451228[115] = 0;
   out_7896233018555451228[116] = 0;
   out_7896233018555451228[117] = 0;
   out_7896233018555451228[118] = 0;
   out_7896233018555451228[119] = 0;
   out_7896233018555451228[120] = 1.0;
}
void f_fun(double *state, double dt, double *out_4333426533206936818) {
   out_4333426533206936818[0] = dt*state[3] + state[0];
   out_4333426533206936818[1] = dt*state[4] + state[1];
   out_4333426533206936818[2] = dt*state[5] + state[2];
   out_4333426533206936818[3] = state[3];
   out_4333426533206936818[4] = state[4];
   out_4333426533206936818[5] = state[5];
   out_4333426533206936818[6] = dt*state[7] + state[6];
   out_4333426533206936818[7] = dt*state[8] + state[7];
   out_4333426533206936818[8] = state[8];
   out_4333426533206936818[9] = state[9];
   out_4333426533206936818[10] = state[10];
}
void F_fun(double *state, double dt, double *out_2869766722226837856) {
   out_2869766722226837856[0] = 1;
   out_2869766722226837856[1] = 0;
   out_2869766722226837856[2] = 0;
   out_2869766722226837856[3] = dt;
   out_2869766722226837856[4] = 0;
   out_2869766722226837856[5] = 0;
   out_2869766722226837856[6] = 0;
   out_2869766722226837856[7] = 0;
   out_2869766722226837856[8] = 0;
   out_2869766722226837856[9] = 0;
   out_2869766722226837856[10] = 0;
   out_2869766722226837856[11] = 0;
   out_2869766722226837856[12] = 1;
   out_2869766722226837856[13] = 0;
   out_2869766722226837856[14] = 0;
   out_2869766722226837856[15] = dt;
   out_2869766722226837856[16] = 0;
   out_2869766722226837856[17] = 0;
   out_2869766722226837856[18] = 0;
   out_2869766722226837856[19] = 0;
   out_2869766722226837856[20] = 0;
   out_2869766722226837856[21] = 0;
   out_2869766722226837856[22] = 0;
   out_2869766722226837856[23] = 0;
   out_2869766722226837856[24] = 1;
   out_2869766722226837856[25] = 0;
   out_2869766722226837856[26] = 0;
   out_2869766722226837856[27] = dt;
   out_2869766722226837856[28] = 0;
   out_2869766722226837856[29] = 0;
   out_2869766722226837856[30] = 0;
   out_2869766722226837856[31] = 0;
   out_2869766722226837856[32] = 0;
   out_2869766722226837856[33] = 0;
   out_2869766722226837856[34] = 0;
   out_2869766722226837856[35] = 0;
   out_2869766722226837856[36] = 1;
   out_2869766722226837856[37] = 0;
   out_2869766722226837856[38] = 0;
   out_2869766722226837856[39] = 0;
   out_2869766722226837856[40] = 0;
   out_2869766722226837856[41] = 0;
   out_2869766722226837856[42] = 0;
   out_2869766722226837856[43] = 0;
   out_2869766722226837856[44] = 0;
   out_2869766722226837856[45] = 0;
   out_2869766722226837856[46] = 0;
   out_2869766722226837856[47] = 0;
   out_2869766722226837856[48] = 1;
   out_2869766722226837856[49] = 0;
   out_2869766722226837856[50] = 0;
   out_2869766722226837856[51] = 0;
   out_2869766722226837856[52] = 0;
   out_2869766722226837856[53] = 0;
   out_2869766722226837856[54] = 0;
   out_2869766722226837856[55] = 0;
   out_2869766722226837856[56] = 0;
   out_2869766722226837856[57] = 0;
   out_2869766722226837856[58] = 0;
   out_2869766722226837856[59] = 0;
   out_2869766722226837856[60] = 1;
   out_2869766722226837856[61] = 0;
   out_2869766722226837856[62] = 0;
   out_2869766722226837856[63] = 0;
   out_2869766722226837856[64] = 0;
   out_2869766722226837856[65] = 0;
   out_2869766722226837856[66] = 0;
   out_2869766722226837856[67] = 0;
   out_2869766722226837856[68] = 0;
   out_2869766722226837856[69] = 0;
   out_2869766722226837856[70] = 0;
   out_2869766722226837856[71] = 0;
   out_2869766722226837856[72] = 1;
   out_2869766722226837856[73] = dt;
   out_2869766722226837856[74] = 0;
   out_2869766722226837856[75] = 0;
   out_2869766722226837856[76] = 0;
   out_2869766722226837856[77] = 0;
   out_2869766722226837856[78] = 0;
   out_2869766722226837856[79] = 0;
   out_2869766722226837856[80] = 0;
   out_2869766722226837856[81] = 0;
   out_2869766722226837856[82] = 0;
   out_2869766722226837856[83] = 0;
   out_2869766722226837856[84] = 1;
   out_2869766722226837856[85] = dt;
   out_2869766722226837856[86] = 0;
   out_2869766722226837856[87] = 0;
   out_2869766722226837856[88] = 0;
   out_2869766722226837856[89] = 0;
   out_2869766722226837856[90] = 0;
   out_2869766722226837856[91] = 0;
   out_2869766722226837856[92] = 0;
   out_2869766722226837856[93] = 0;
   out_2869766722226837856[94] = 0;
   out_2869766722226837856[95] = 0;
   out_2869766722226837856[96] = 1;
   out_2869766722226837856[97] = 0;
   out_2869766722226837856[98] = 0;
   out_2869766722226837856[99] = 0;
   out_2869766722226837856[100] = 0;
   out_2869766722226837856[101] = 0;
   out_2869766722226837856[102] = 0;
   out_2869766722226837856[103] = 0;
   out_2869766722226837856[104] = 0;
   out_2869766722226837856[105] = 0;
   out_2869766722226837856[106] = 0;
   out_2869766722226837856[107] = 0;
   out_2869766722226837856[108] = 1;
   out_2869766722226837856[109] = 0;
   out_2869766722226837856[110] = 0;
   out_2869766722226837856[111] = 0;
   out_2869766722226837856[112] = 0;
   out_2869766722226837856[113] = 0;
   out_2869766722226837856[114] = 0;
   out_2869766722226837856[115] = 0;
   out_2869766722226837856[116] = 0;
   out_2869766722226837856[117] = 0;
   out_2869766722226837856[118] = 0;
   out_2869766722226837856[119] = 0;
   out_2869766722226837856[120] = 1;
}
void h_6(double *state, double *sat_pos, double *out_1024352917879833673) {
   out_1024352917879833673[0] = sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2)) + state[6];
}
void H_6(double *state, double *sat_pos, double *out_6472797684402021181) {
   out_6472797684402021181[0] = (-sat_pos[0] + state[0])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_6472797684402021181[1] = (-sat_pos[1] + state[1])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_6472797684402021181[2] = (-sat_pos[2] + state[2])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_6472797684402021181[3] = 0;
   out_6472797684402021181[4] = 0;
   out_6472797684402021181[5] = 0;
   out_6472797684402021181[6] = 1;
   out_6472797684402021181[7] = 0;
   out_6472797684402021181[8] = 0;
   out_6472797684402021181[9] = 0;
   out_6472797684402021181[10] = 0;
}
void h_20(double *state, double *sat_pos, double *out_501984527921721025) {
   out_501984527921721025[0] = sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2)) + sat_pos[3]*state[10] + state[6] + state[9];
}
void H_20(double *state, double *sat_pos, double *out_1676448818287402981) {
   out_1676448818287402981[0] = (-sat_pos[0] + state[0])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_1676448818287402981[1] = (-sat_pos[1] + state[1])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_1676448818287402981[2] = (-sat_pos[2] + state[2])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_1676448818287402981[3] = 0;
   out_1676448818287402981[4] = 0;
   out_1676448818287402981[5] = 0;
   out_1676448818287402981[6] = 1;
   out_1676448818287402981[7] = 0;
   out_1676448818287402981[8] = 0;
   out_1676448818287402981[9] = 1;
   out_1676448818287402981[10] = sat_pos[3];
}
void h_7(double *state, double *sat_pos_vel, double *out_517986936952942546) {
   out_517986936952942546[0] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[3] - state[3])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[4] - state[4])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + (sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + state[7];
}
void H_7(double *state, double *sat_pos_vel, double *out_579701802137747330) {
   out_579701802137747330[0] = pow(sat_pos_vel[0] - state[0], 2)*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[0] - state[0])*(sat_pos_vel[1] - state[1])*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[0] - state[0])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[3] - state[3])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_579701802137747330[1] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[1] - state[1])*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + pow(sat_pos_vel[1] - state[1], 2)*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[4] - state[4])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_579701802137747330[2] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + pow(sat_pos_vel[2] - state[2], 2)*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[5] - state[5])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_579701802137747330[3] = -(sat_pos_vel[0] - state[0])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_579701802137747330[4] = -(sat_pos_vel[1] - state[1])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_579701802137747330[5] = -(sat_pos_vel[2] - state[2])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_579701802137747330[6] = 0;
   out_579701802137747330[7] = 1;
   out_579701802137747330[8] = 0;
   out_579701802137747330[9] = 0;
   out_579701802137747330[10] = 0;
}
void h_21(double *state, double *sat_pos_vel, double *out_517986936952942546) {
   out_517986936952942546[0] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[3] - state[3])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[4] - state[4])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + (sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + state[7];
}
void H_21(double *state, double *sat_pos_vel, double *out_579701802137747330) {
   out_579701802137747330[0] = pow(sat_pos_vel[0] - state[0], 2)*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[0] - state[0])*(sat_pos_vel[1] - state[1])*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[0] - state[0])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[3] - state[3])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_579701802137747330[1] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[1] - state[1])*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + pow(sat_pos_vel[1] - state[1], 2)*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[4] - state[4])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_579701802137747330[2] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + pow(sat_pos_vel[2] - state[2], 2)*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[5] - state[5])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_579701802137747330[3] = -(sat_pos_vel[0] - state[0])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_579701802137747330[4] = -(sat_pos_vel[1] - state[1])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_579701802137747330[5] = -(sat_pos_vel[2] - state[2])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_579701802137747330[6] = 0;
   out_579701802137747330[7] = 1;
   out_579701802137747330[8] = 0;
   out_579701802137747330[9] = 0;
   out_579701802137747330[10] = 0;
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
void gnss_err_fun(double *nom_x, double *delta_x, double *out_2474256111087528474) {
  err_fun(nom_x, delta_x, out_2474256111087528474);
}
void gnss_inv_err_fun(double *nom_x, double *true_x, double *out_7051622024455451737) {
  inv_err_fun(nom_x, true_x, out_7051622024455451737);
}
void gnss_H_mod_fun(double *state, double *out_7896233018555451228) {
  H_mod_fun(state, out_7896233018555451228);
}
void gnss_f_fun(double *state, double dt, double *out_4333426533206936818) {
  f_fun(state,  dt, out_4333426533206936818);
}
void gnss_F_fun(double *state, double dt, double *out_2869766722226837856) {
  F_fun(state,  dt, out_2869766722226837856);
}
void gnss_h_6(double *state, double *sat_pos, double *out_1024352917879833673) {
  h_6(state, sat_pos, out_1024352917879833673);
}
void gnss_H_6(double *state, double *sat_pos, double *out_6472797684402021181) {
  H_6(state, sat_pos, out_6472797684402021181);
}
void gnss_h_20(double *state, double *sat_pos, double *out_501984527921721025) {
  h_20(state, sat_pos, out_501984527921721025);
}
void gnss_H_20(double *state, double *sat_pos, double *out_1676448818287402981) {
  H_20(state, sat_pos, out_1676448818287402981);
}
void gnss_h_7(double *state, double *sat_pos_vel, double *out_517986936952942546) {
  h_7(state, sat_pos_vel, out_517986936952942546);
}
void gnss_H_7(double *state, double *sat_pos_vel, double *out_579701802137747330) {
  H_7(state, sat_pos_vel, out_579701802137747330);
}
void gnss_h_21(double *state, double *sat_pos_vel, double *out_517986936952942546) {
  h_21(state, sat_pos_vel, out_517986936952942546);
}
void gnss_H_21(double *state, double *sat_pos_vel, double *out_579701802137747330) {
  H_21(state, sat_pos_vel, out_579701802137747330);
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
