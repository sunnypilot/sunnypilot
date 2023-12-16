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
void err_fun(double *nom_x, double *delta_x, double *out_5150571341583167615) {
   out_5150571341583167615[0] = delta_x[0] + nom_x[0];
   out_5150571341583167615[1] = delta_x[1] + nom_x[1];
   out_5150571341583167615[2] = delta_x[2] + nom_x[2];
   out_5150571341583167615[3] = delta_x[3] + nom_x[3];
   out_5150571341583167615[4] = delta_x[4] + nom_x[4];
   out_5150571341583167615[5] = delta_x[5] + nom_x[5];
   out_5150571341583167615[6] = delta_x[6] + nom_x[6];
   out_5150571341583167615[7] = delta_x[7] + nom_x[7];
   out_5150571341583167615[8] = delta_x[8] + nom_x[8];
   out_5150571341583167615[9] = delta_x[9] + nom_x[9];
   out_5150571341583167615[10] = delta_x[10] + nom_x[10];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_4922120609791221850) {
   out_4922120609791221850[0] = -nom_x[0] + true_x[0];
   out_4922120609791221850[1] = -nom_x[1] + true_x[1];
   out_4922120609791221850[2] = -nom_x[2] + true_x[2];
   out_4922120609791221850[3] = -nom_x[3] + true_x[3];
   out_4922120609791221850[4] = -nom_x[4] + true_x[4];
   out_4922120609791221850[5] = -nom_x[5] + true_x[5];
   out_4922120609791221850[6] = -nom_x[6] + true_x[6];
   out_4922120609791221850[7] = -nom_x[7] + true_x[7];
   out_4922120609791221850[8] = -nom_x[8] + true_x[8];
   out_4922120609791221850[9] = -nom_x[9] + true_x[9];
   out_4922120609791221850[10] = -nom_x[10] + true_x[10];
}
void H_mod_fun(double *state, double *out_6843723691525215114) {
   out_6843723691525215114[0] = 1.0;
   out_6843723691525215114[1] = 0;
   out_6843723691525215114[2] = 0;
   out_6843723691525215114[3] = 0;
   out_6843723691525215114[4] = 0;
   out_6843723691525215114[5] = 0;
   out_6843723691525215114[6] = 0;
   out_6843723691525215114[7] = 0;
   out_6843723691525215114[8] = 0;
   out_6843723691525215114[9] = 0;
   out_6843723691525215114[10] = 0;
   out_6843723691525215114[11] = 0;
   out_6843723691525215114[12] = 1.0;
   out_6843723691525215114[13] = 0;
   out_6843723691525215114[14] = 0;
   out_6843723691525215114[15] = 0;
   out_6843723691525215114[16] = 0;
   out_6843723691525215114[17] = 0;
   out_6843723691525215114[18] = 0;
   out_6843723691525215114[19] = 0;
   out_6843723691525215114[20] = 0;
   out_6843723691525215114[21] = 0;
   out_6843723691525215114[22] = 0;
   out_6843723691525215114[23] = 0;
   out_6843723691525215114[24] = 1.0;
   out_6843723691525215114[25] = 0;
   out_6843723691525215114[26] = 0;
   out_6843723691525215114[27] = 0;
   out_6843723691525215114[28] = 0;
   out_6843723691525215114[29] = 0;
   out_6843723691525215114[30] = 0;
   out_6843723691525215114[31] = 0;
   out_6843723691525215114[32] = 0;
   out_6843723691525215114[33] = 0;
   out_6843723691525215114[34] = 0;
   out_6843723691525215114[35] = 0;
   out_6843723691525215114[36] = 1.0;
   out_6843723691525215114[37] = 0;
   out_6843723691525215114[38] = 0;
   out_6843723691525215114[39] = 0;
   out_6843723691525215114[40] = 0;
   out_6843723691525215114[41] = 0;
   out_6843723691525215114[42] = 0;
   out_6843723691525215114[43] = 0;
   out_6843723691525215114[44] = 0;
   out_6843723691525215114[45] = 0;
   out_6843723691525215114[46] = 0;
   out_6843723691525215114[47] = 0;
   out_6843723691525215114[48] = 1.0;
   out_6843723691525215114[49] = 0;
   out_6843723691525215114[50] = 0;
   out_6843723691525215114[51] = 0;
   out_6843723691525215114[52] = 0;
   out_6843723691525215114[53] = 0;
   out_6843723691525215114[54] = 0;
   out_6843723691525215114[55] = 0;
   out_6843723691525215114[56] = 0;
   out_6843723691525215114[57] = 0;
   out_6843723691525215114[58] = 0;
   out_6843723691525215114[59] = 0;
   out_6843723691525215114[60] = 1.0;
   out_6843723691525215114[61] = 0;
   out_6843723691525215114[62] = 0;
   out_6843723691525215114[63] = 0;
   out_6843723691525215114[64] = 0;
   out_6843723691525215114[65] = 0;
   out_6843723691525215114[66] = 0;
   out_6843723691525215114[67] = 0;
   out_6843723691525215114[68] = 0;
   out_6843723691525215114[69] = 0;
   out_6843723691525215114[70] = 0;
   out_6843723691525215114[71] = 0;
   out_6843723691525215114[72] = 1.0;
   out_6843723691525215114[73] = 0;
   out_6843723691525215114[74] = 0;
   out_6843723691525215114[75] = 0;
   out_6843723691525215114[76] = 0;
   out_6843723691525215114[77] = 0;
   out_6843723691525215114[78] = 0;
   out_6843723691525215114[79] = 0;
   out_6843723691525215114[80] = 0;
   out_6843723691525215114[81] = 0;
   out_6843723691525215114[82] = 0;
   out_6843723691525215114[83] = 0;
   out_6843723691525215114[84] = 1.0;
   out_6843723691525215114[85] = 0;
   out_6843723691525215114[86] = 0;
   out_6843723691525215114[87] = 0;
   out_6843723691525215114[88] = 0;
   out_6843723691525215114[89] = 0;
   out_6843723691525215114[90] = 0;
   out_6843723691525215114[91] = 0;
   out_6843723691525215114[92] = 0;
   out_6843723691525215114[93] = 0;
   out_6843723691525215114[94] = 0;
   out_6843723691525215114[95] = 0;
   out_6843723691525215114[96] = 1.0;
   out_6843723691525215114[97] = 0;
   out_6843723691525215114[98] = 0;
   out_6843723691525215114[99] = 0;
   out_6843723691525215114[100] = 0;
   out_6843723691525215114[101] = 0;
   out_6843723691525215114[102] = 0;
   out_6843723691525215114[103] = 0;
   out_6843723691525215114[104] = 0;
   out_6843723691525215114[105] = 0;
   out_6843723691525215114[106] = 0;
   out_6843723691525215114[107] = 0;
   out_6843723691525215114[108] = 1.0;
   out_6843723691525215114[109] = 0;
   out_6843723691525215114[110] = 0;
   out_6843723691525215114[111] = 0;
   out_6843723691525215114[112] = 0;
   out_6843723691525215114[113] = 0;
   out_6843723691525215114[114] = 0;
   out_6843723691525215114[115] = 0;
   out_6843723691525215114[116] = 0;
   out_6843723691525215114[117] = 0;
   out_6843723691525215114[118] = 0;
   out_6843723691525215114[119] = 0;
   out_6843723691525215114[120] = 1.0;
}
void f_fun(double *state, double dt, double *out_17408948005989977) {
   out_17408948005989977[0] = dt*state[3] + state[0];
   out_17408948005989977[1] = dt*state[4] + state[1];
   out_17408948005989977[2] = dt*state[5] + state[2];
   out_17408948005989977[3] = state[3];
   out_17408948005989977[4] = state[4];
   out_17408948005989977[5] = state[5];
   out_17408948005989977[6] = dt*state[7] + state[6];
   out_17408948005989977[7] = dt*state[8] + state[7];
   out_17408948005989977[8] = state[8];
   out_17408948005989977[9] = state[9];
   out_17408948005989977[10] = state[10];
}
void F_fun(double *state, double dt, double *out_2909713697722566302) {
   out_2909713697722566302[0] = 1;
   out_2909713697722566302[1] = 0;
   out_2909713697722566302[2] = 0;
   out_2909713697722566302[3] = dt;
   out_2909713697722566302[4] = 0;
   out_2909713697722566302[5] = 0;
   out_2909713697722566302[6] = 0;
   out_2909713697722566302[7] = 0;
   out_2909713697722566302[8] = 0;
   out_2909713697722566302[9] = 0;
   out_2909713697722566302[10] = 0;
   out_2909713697722566302[11] = 0;
   out_2909713697722566302[12] = 1;
   out_2909713697722566302[13] = 0;
   out_2909713697722566302[14] = 0;
   out_2909713697722566302[15] = dt;
   out_2909713697722566302[16] = 0;
   out_2909713697722566302[17] = 0;
   out_2909713697722566302[18] = 0;
   out_2909713697722566302[19] = 0;
   out_2909713697722566302[20] = 0;
   out_2909713697722566302[21] = 0;
   out_2909713697722566302[22] = 0;
   out_2909713697722566302[23] = 0;
   out_2909713697722566302[24] = 1;
   out_2909713697722566302[25] = 0;
   out_2909713697722566302[26] = 0;
   out_2909713697722566302[27] = dt;
   out_2909713697722566302[28] = 0;
   out_2909713697722566302[29] = 0;
   out_2909713697722566302[30] = 0;
   out_2909713697722566302[31] = 0;
   out_2909713697722566302[32] = 0;
   out_2909713697722566302[33] = 0;
   out_2909713697722566302[34] = 0;
   out_2909713697722566302[35] = 0;
   out_2909713697722566302[36] = 1;
   out_2909713697722566302[37] = 0;
   out_2909713697722566302[38] = 0;
   out_2909713697722566302[39] = 0;
   out_2909713697722566302[40] = 0;
   out_2909713697722566302[41] = 0;
   out_2909713697722566302[42] = 0;
   out_2909713697722566302[43] = 0;
   out_2909713697722566302[44] = 0;
   out_2909713697722566302[45] = 0;
   out_2909713697722566302[46] = 0;
   out_2909713697722566302[47] = 0;
   out_2909713697722566302[48] = 1;
   out_2909713697722566302[49] = 0;
   out_2909713697722566302[50] = 0;
   out_2909713697722566302[51] = 0;
   out_2909713697722566302[52] = 0;
   out_2909713697722566302[53] = 0;
   out_2909713697722566302[54] = 0;
   out_2909713697722566302[55] = 0;
   out_2909713697722566302[56] = 0;
   out_2909713697722566302[57] = 0;
   out_2909713697722566302[58] = 0;
   out_2909713697722566302[59] = 0;
   out_2909713697722566302[60] = 1;
   out_2909713697722566302[61] = 0;
   out_2909713697722566302[62] = 0;
   out_2909713697722566302[63] = 0;
   out_2909713697722566302[64] = 0;
   out_2909713697722566302[65] = 0;
   out_2909713697722566302[66] = 0;
   out_2909713697722566302[67] = 0;
   out_2909713697722566302[68] = 0;
   out_2909713697722566302[69] = 0;
   out_2909713697722566302[70] = 0;
   out_2909713697722566302[71] = 0;
   out_2909713697722566302[72] = 1;
   out_2909713697722566302[73] = dt;
   out_2909713697722566302[74] = 0;
   out_2909713697722566302[75] = 0;
   out_2909713697722566302[76] = 0;
   out_2909713697722566302[77] = 0;
   out_2909713697722566302[78] = 0;
   out_2909713697722566302[79] = 0;
   out_2909713697722566302[80] = 0;
   out_2909713697722566302[81] = 0;
   out_2909713697722566302[82] = 0;
   out_2909713697722566302[83] = 0;
   out_2909713697722566302[84] = 1;
   out_2909713697722566302[85] = dt;
   out_2909713697722566302[86] = 0;
   out_2909713697722566302[87] = 0;
   out_2909713697722566302[88] = 0;
   out_2909713697722566302[89] = 0;
   out_2909713697722566302[90] = 0;
   out_2909713697722566302[91] = 0;
   out_2909713697722566302[92] = 0;
   out_2909713697722566302[93] = 0;
   out_2909713697722566302[94] = 0;
   out_2909713697722566302[95] = 0;
   out_2909713697722566302[96] = 1;
   out_2909713697722566302[97] = 0;
   out_2909713697722566302[98] = 0;
   out_2909713697722566302[99] = 0;
   out_2909713697722566302[100] = 0;
   out_2909713697722566302[101] = 0;
   out_2909713697722566302[102] = 0;
   out_2909713697722566302[103] = 0;
   out_2909713697722566302[104] = 0;
   out_2909713697722566302[105] = 0;
   out_2909713697722566302[106] = 0;
   out_2909713697722566302[107] = 0;
   out_2909713697722566302[108] = 1;
   out_2909713697722566302[109] = 0;
   out_2909713697722566302[110] = 0;
   out_2909713697722566302[111] = 0;
   out_2909713697722566302[112] = 0;
   out_2909713697722566302[113] = 0;
   out_2909713697722566302[114] = 0;
   out_2909713697722566302[115] = 0;
   out_2909713697722566302[116] = 0;
   out_2909713697722566302[117] = 0;
   out_2909713697722566302[118] = 0;
   out_2909713697722566302[119] = 0;
   out_2909713697722566302[120] = 1;
}
void h_6(double *state, double *sat_pos, double *out_7716397383098239831) {
   out_7716397383098239831[0] = sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2)) + state[6];
}
void H_6(double *state, double *sat_pos, double *out_8734299093550610133) {
   out_8734299093550610133[0] = (-sat_pos[0] + state[0])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_8734299093550610133[1] = (-sat_pos[1] + state[1])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_8734299093550610133[2] = (-sat_pos[2] + state[2])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_8734299093550610133[3] = 0;
   out_8734299093550610133[4] = 0;
   out_8734299093550610133[5] = 0;
   out_8734299093550610133[6] = 1;
   out_8734299093550610133[7] = 0;
   out_8734299093550610133[8] = 0;
   out_8734299093550610133[9] = 0;
   out_8734299093550610133[10] = 0;
}
void h_20(double *state, double *sat_pos, double *out_3187395134236655731) {
   out_3187395134236655731[0] = sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2)) + sat_pos[3]*state[10] + state[6] + state[9];
}
void H_20(double *state, double *sat_pos, double *out_778578650651897423) {
   out_778578650651897423[0] = (-sat_pos[0] + state[0])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_778578650651897423[1] = (-sat_pos[1] + state[1])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_778578650651897423[2] = (-sat_pos[2] + state[2])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_778578650651897423[3] = 0;
   out_778578650651897423[4] = 0;
   out_778578650651897423[5] = 0;
   out_778578650651897423[6] = 1;
   out_778578650651897423[7] = 0;
   out_778578650651897423[8] = 0;
   out_778578650651897423[9] = 1;
   out_778578650651897423[10] = sat_pos[3];
}
void h_7(double *state, double *sat_pos_vel, double *out_7558782949651559266) {
   out_7558782949651559266[0] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[3] - state[3])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[4] - state[4])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + (sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + state[7];
}
void H_7(double *state, double *sat_pos_vel, double *out_1226120805724173486) {
   out_1226120805724173486[0] = pow(sat_pos_vel[0] - state[0], 2)*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[0] - state[0])*(sat_pos_vel[1] - state[1])*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[0] - state[0])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[3] - state[3])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_1226120805724173486[1] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[1] - state[1])*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + pow(sat_pos_vel[1] - state[1], 2)*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[4] - state[4])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_1226120805724173486[2] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + pow(sat_pos_vel[2] - state[2], 2)*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[5] - state[5])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_1226120805724173486[3] = -(sat_pos_vel[0] - state[0])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_1226120805724173486[4] = -(sat_pos_vel[1] - state[1])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_1226120805724173486[5] = -(sat_pos_vel[2] - state[2])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_1226120805724173486[6] = 0;
   out_1226120805724173486[7] = 1;
   out_1226120805724173486[8] = 0;
   out_1226120805724173486[9] = 0;
   out_1226120805724173486[10] = 0;
}
void h_21(double *state, double *sat_pos_vel, double *out_7558782949651559266) {
   out_7558782949651559266[0] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[3] - state[3])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[4] - state[4])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + (sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + state[7];
}
void H_21(double *state, double *sat_pos_vel, double *out_1226120805724173486) {
   out_1226120805724173486[0] = pow(sat_pos_vel[0] - state[0], 2)*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[0] - state[0])*(sat_pos_vel[1] - state[1])*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[0] - state[0])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[3] - state[3])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_1226120805724173486[1] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[1] - state[1])*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + pow(sat_pos_vel[1] - state[1], 2)*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[4] - state[4])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_1226120805724173486[2] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + pow(sat_pos_vel[2] - state[2], 2)*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[5] - state[5])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_1226120805724173486[3] = -(sat_pos_vel[0] - state[0])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_1226120805724173486[4] = -(sat_pos_vel[1] - state[1])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_1226120805724173486[5] = -(sat_pos_vel[2] - state[2])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_1226120805724173486[6] = 0;
   out_1226120805724173486[7] = 1;
   out_1226120805724173486[8] = 0;
   out_1226120805724173486[9] = 0;
   out_1226120805724173486[10] = 0;
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
void gnss_err_fun(double *nom_x, double *delta_x, double *out_5150571341583167615) {
  err_fun(nom_x, delta_x, out_5150571341583167615);
}
void gnss_inv_err_fun(double *nom_x, double *true_x, double *out_4922120609791221850) {
  inv_err_fun(nom_x, true_x, out_4922120609791221850);
}
void gnss_H_mod_fun(double *state, double *out_6843723691525215114) {
  H_mod_fun(state, out_6843723691525215114);
}
void gnss_f_fun(double *state, double dt, double *out_17408948005989977) {
  f_fun(state,  dt, out_17408948005989977);
}
void gnss_F_fun(double *state, double dt, double *out_2909713697722566302) {
  F_fun(state,  dt, out_2909713697722566302);
}
void gnss_h_6(double *state, double *sat_pos, double *out_7716397383098239831) {
  h_6(state, sat_pos, out_7716397383098239831);
}
void gnss_H_6(double *state, double *sat_pos, double *out_8734299093550610133) {
  H_6(state, sat_pos, out_8734299093550610133);
}
void gnss_h_20(double *state, double *sat_pos, double *out_3187395134236655731) {
  h_20(state, sat_pos, out_3187395134236655731);
}
void gnss_H_20(double *state, double *sat_pos, double *out_778578650651897423) {
  H_20(state, sat_pos, out_778578650651897423);
}
void gnss_h_7(double *state, double *sat_pos_vel, double *out_7558782949651559266) {
  h_7(state, sat_pos_vel, out_7558782949651559266);
}
void gnss_H_7(double *state, double *sat_pos_vel, double *out_1226120805724173486) {
  H_7(state, sat_pos_vel, out_1226120805724173486);
}
void gnss_h_21(double *state, double *sat_pos_vel, double *out_7558782949651559266) {
  h_21(state, sat_pos_vel, out_7558782949651559266);
}
void gnss_H_21(double *state, double *sat_pos_vel, double *out_1226120805724173486) {
  H_21(state, sat_pos_vel, out_1226120805724173486);
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
