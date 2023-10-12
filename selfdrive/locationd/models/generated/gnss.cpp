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
void err_fun(double *nom_x, double *delta_x, double *out_2893903750678761352) {
   out_2893903750678761352[0] = delta_x[0] + nom_x[0];
   out_2893903750678761352[1] = delta_x[1] + nom_x[1];
   out_2893903750678761352[2] = delta_x[2] + nom_x[2];
   out_2893903750678761352[3] = delta_x[3] + nom_x[3];
   out_2893903750678761352[4] = delta_x[4] + nom_x[4];
   out_2893903750678761352[5] = delta_x[5] + nom_x[5];
   out_2893903750678761352[6] = delta_x[6] + nom_x[6];
   out_2893903750678761352[7] = delta_x[7] + nom_x[7];
   out_2893903750678761352[8] = delta_x[8] + nom_x[8];
   out_2893903750678761352[9] = delta_x[9] + nom_x[9];
   out_2893903750678761352[10] = delta_x[10] + nom_x[10];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_1573976658111465050) {
   out_1573976658111465050[0] = -nom_x[0] + true_x[0];
   out_1573976658111465050[1] = -nom_x[1] + true_x[1];
   out_1573976658111465050[2] = -nom_x[2] + true_x[2];
   out_1573976658111465050[3] = -nom_x[3] + true_x[3];
   out_1573976658111465050[4] = -nom_x[4] + true_x[4];
   out_1573976658111465050[5] = -nom_x[5] + true_x[5];
   out_1573976658111465050[6] = -nom_x[6] + true_x[6];
   out_1573976658111465050[7] = -nom_x[7] + true_x[7];
   out_1573976658111465050[8] = -nom_x[8] + true_x[8];
   out_1573976658111465050[9] = -nom_x[9] + true_x[9];
   out_1573976658111465050[10] = -nom_x[10] + true_x[10];
}
void H_mod_fun(double *state, double *out_6669274116786942791) {
   out_6669274116786942791[0] = 1.0;
   out_6669274116786942791[1] = 0;
   out_6669274116786942791[2] = 0;
   out_6669274116786942791[3] = 0;
   out_6669274116786942791[4] = 0;
   out_6669274116786942791[5] = 0;
   out_6669274116786942791[6] = 0;
   out_6669274116786942791[7] = 0;
   out_6669274116786942791[8] = 0;
   out_6669274116786942791[9] = 0;
   out_6669274116786942791[10] = 0;
   out_6669274116786942791[11] = 0;
   out_6669274116786942791[12] = 1.0;
   out_6669274116786942791[13] = 0;
   out_6669274116786942791[14] = 0;
   out_6669274116786942791[15] = 0;
   out_6669274116786942791[16] = 0;
   out_6669274116786942791[17] = 0;
   out_6669274116786942791[18] = 0;
   out_6669274116786942791[19] = 0;
   out_6669274116786942791[20] = 0;
   out_6669274116786942791[21] = 0;
   out_6669274116786942791[22] = 0;
   out_6669274116786942791[23] = 0;
   out_6669274116786942791[24] = 1.0;
   out_6669274116786942791[25] = 0;
   out_6669274116786942791[26] = 0;
   out_6669274116786942791[27] = 0;
   out_6669274116786942791[28] = 0;
   out_6669274116786942791[29] = 0;
   out_6669274116786942791[30] = 0;
   out_6669274116786942791[31] = 0;
   out_6669274116786942791[32] = 0;
   out_6669274116786942791[33] = 0;
   out_6669274116786942791[34] = 0;
   out_6669274116786942791[35] = 0;
   out_6669274116786942791[36] = 1.0;
   out_6669274116786942791[37] = 0;
   out_6669274116786942791[38] = 0;
   out_6669274116786942791[39] = 0;
   out_6669274116786942791[40] = 0;
   out_6669274116786942791[41] = 0;
   out_6669274116786942791[42] = 0;
   out_6669274116786942791[43] = 0;
   out_6669274116786942791[44] = 0;
   out_6669274116786942791[45] = 0;
   out_6669274116786942791[46] = 0;
   out_6669274116786942791[47] = 0;
   out_6669274116786942791[48] = 1.0;
   out_6669274116786942791[49] = 0;
   out_6669274116786942791[50] = 0;
   out_6669274116786942791[51] = 0;
   out_6669274116786942791[52] = 0;
   out_6669274116786942791[53] = 0;
   out_6669274116786942791[54] = 0;
   out_6669274116786942791[55] = 0;
   out_6669274116786942791[56] = 0;
   out_6669274116786942791[57] = 0;
   out_6669274116786942791[58] = 0;
   out_6669274116786942791[59] = 0;
   out_6669274116786942791[60] = 1.0;
   out_6669274116786942791[61] = 0;
   out_6669274116786942791[62] = 0;
   out_6669274116786942791[63] = 0;
   out_6669274116786942791[64] = 0;
   out_6669274116786942791[65] = 0;
   out_6669274116786942791[66] = 0;
   out_6669274116786942791[67] = 0;
   out_6669274116786942791[68] = 0;
   out_6669274116786942791[69] = 0;
   out_6669274116786942791[70] = 0;
   out_6669274116786942791[71] = 0;
   out_6669274116786942791[72] = 1.0;
   out_6669274116786942791[73] = 0;
   out_6669274116786942791[74] = 0;
   out_6669274116786942791[75] = 0;
   out_6669274116786942791[76] = 0;
   out_6669274116786942791[77] = 0;
   out_6669274116786942791[78] = 0;
   out_6669274116786942791[79] = 0;
   out_6669274116786942791[80] = 0;
   out_6669274116786942791[81] = 0;
   out_6669274116786942791[82] = 0;
   out_6669274116786942791[83] = 0;
   out_6669274116786942791[84] = 1.0;
   out_6669274116786942791[85] = 0;
   out_6669274116786942791[86] = 0;
   out_6669274116786942791[87] = 0;
   out_6669274116786942791[88] = 0;
   out_6669274116786942791[89] = 0;
   out_6669274116786942791[90] = 0;
   out_6669274116786942791[91] = 0;
   out_6669274116786942791[92] = 0;
   out_6669274116786942791[93] = 0;
   out_6669274116786942791[94] = 0;
   out_6669274116786942791[95] = 0;
   out_6669274116786942791[96] = 1.0;
   out_6669274116786942791[97] = 0;
   out_6669274116786942791[98] = 0;
   out_6669274116786942791[99] = 0;
   out_6669274116786942791[100] = 0;
   out_6669274116786942791[101] = 0;
   out_6669274116786942791[102] = 0;
   out_6669274116786942791[103] = 0;
   out_6669274116786942791[104] = 0;
   out_6669274116786942791[105] = 0;
   out_6669274116786942791[106] = 0;
   out_6669274116786942791[107] = 0;
   out_6669274116786942791[108] = 1.0;
   out_6669274116786942791[109] = 0;
   out_6669274116786942791[110] = 0;
   out_6669274116786942791[111] = 0;
   out_6669274116786942791[112] = 0;
   out_6669274116786942791[113] = 0;
   out_6669274116786942791[114] = 0;
   out_6669274116786942791[115] = 0;
   out_6669274116786942791[116] = 0;
   out_6669274116786942791[117] = 0;
   out_6669274116786942791[118] = 0;
   out_6669274116786942791[119] = 0;
   out_6669274116786942791[120] = 1.0;
}
void f_fun(double *state, double dt, double *out_434701726961688353) {
   out_434701726961688353[0] = dt*state[3] + state[0];
   out_434701726961688353[1] = dt*state[4] + state[1];
   out_434701726961688353[2] = dt*state[5] + state[2];
   out_434701726961688353[3] = state[3];
   out_434701726961688353[4] = state[4];
   out_434701726961688353[5] = state[5];
   out_434701726961688353[6] = dt*state[7] + state[6];
   out_434701726961688353[7] = dt*state[8] + state[7];
   out_434701726961688353[8] = state[8];
   out_434701726961688353[9] = state[9];
   out_434701726961688353[10] = state[10];
}
void F_fun(double *state, double dt, double *out_4283718208164219015) {
   out_4283718208164219015[0] = 1;
   out_4283718208164219015[1] = 0;
   out_4283718208164219015[2] = 0;
   out_4283718208164219015[3] = dt;
   out_4283718208164219015[4] = 0;
   out_4283718208164219015[5] = 0;
   out_4283718208164219015[6] = 0;
   out_4283718208164219015[7] = 0;
   out_4283718208164219015[8] = 0;
   out_4283718208164219015[9] = 0;
   out_4283718208164219015[10] = 0;
   out_4283718208164219015[11] = 0;
   out_4283718208164219015[12] = 1;
   out_4283718208164219015[13] = 0;
   out_4283718208164219015[14] = 0;
   out_4283718208164219015[15] = dt;
   out_4283718208164219015[16] = 0;
   out_4283718208164219015[17] = 0;
   out_4283718208164219015[18] = 0;
   out_4283718208164219015[19] = 0;
   out_4283718208164219015[20] = 0;
   out_4283718208164219015[21] = 0;
   out_4283718208164219015[22] = 0;
   out_4283718208164219015[23] = 0;
   out_4283718208164219015[24] = 1;
   out_4283718208164219015[25] = 0;
   out_4283718208164219015[26] = 0;
   out_4283718208164219015[27] = dt;
   out_4283718208164219015[28] = 0;
   out_4283718208164219015[29] = 0;
   out_4283718208164219015[30] = 0;
   out_4283718208164219015[31] = 0;
   out_4283718208164219015[32] = 0;
   out_4283718208164219015[33] = 0;
   out_4283718208164219015[34] = 0;
   out_4283718208164219015[35] = 0;
   out_4283718208164219015[36] = 1;
   out_4283718208164219015[37] = 0;
   out_4283718208164219015[38] = 0;
   out_4283718208164219015[39] = 0;
   out_4283718208164219015[40] = 0;
   out_4283718208164219015[41] = 0;
   out_4283718208164219015[42] = 0;
   out_4283718208164219015[43] = 0;
   out_4283718208164219015[44] = 0;
   out_4283718208164219015[45] = 0;
   out_4283718208164219015[46] = 0;
   out_4283718208164219015[47] = 0;
   out_4283718208164219015[48] = 1;
   out_4283718208164219015[49] = 0;
   out_4283718208164219015[50] = 0;
   out_4283718208164219015[51] = 0;
   out_4283718208164219015[52] = 0;
   out_4283718208164219015[53] = 0;
   out_4283718208164219015[54] = 0;
   out_4283718208164219015[55] = 0;
   out_4283718208164219015[56] = 0;
   out_4283718208164219015[57] = 0;
   out_4283718208164219015[58] = 0;
   out_4283718208164219015[59] = 0;
   out_4283718208164219015[60] = 1;
   out_4283718208164219015[61] = 0;
   out_4283718208164219015[62] = 0;
   out_4283718208164219015[63] = 0;
   out_4283718208164219015[64] = 0;
   out_4283718208164219015[65] = 0;
   out_4283718208164219015[66] = 0;
   out_4283718208164219015[67] = 0;
   out_4283718208164219015[68] = 0;
   out_4283718208164219015[69] = 0;
   out_4283718208164219015[70] = 0;
   out_4283718208164219015[71] = 0;
   out_4283718208164219015[72] = 1;
   out_4283718208164219015[73] = dt;
   out_4283718208164219015[74] = 0;
   out_4283718208164219015[75] = 0;
   out_4283718208164219015[76] = 0;
   out_4283718208164219015[77] = 0;
   out_4283718208164219015[78] = 0;
   out_4283718208164219015[79] = 0;
   out_4283718208164219015[80] = 0;
   out_4283718208164219015[81] = 0;
   out_4283718208164219015[82] = 0;
   out_4283718208164219015[83] = 0;
   out_4283718208164219015[84] = 1;
   out_4283718208164219015[85] = dt;
   out_4283718208164219015[86] = 0;
   out_4283718208164219015[87] = 0;
   out_4283718208164219015[88] = 0;
   out_4283718208164219015[89] = 0;
   out_4283718208164219015[90] = 0;
   out_4283718208164219015[91] = 0;
   out_4283718208164219015[92] = 0;
   out_4283718208164219015[93] = 0;
   out_4283718208164219015[94] = 0;
   out_4283718208164219015[95] = 0;
   out_4283718208164219015[96] = 1;
   out_4283718208164219015[97] = 0;
   out_4283718208164219015[98] = 0;
   out_4283718208164219015[99] = 0;
   out_4283718208164219015[100] = 0;
   out_4283718208164219015[101] = 0;
   out_4283718208164219015[102] = 0;
   out_4283718208164219015[103] = 0;
   out_4283718208164219015[104] = 0;
   out_4283718208164219015[105] = 0;
   out_4283718208164219015[106] = 0;
   out_4283718208164219015[107] = 0;
   out_4283718208164219015[108] = 1;
   out_4283718208164219015[109] = 0;
   out_4283718208164219015[110] = 0;
   out_4283718208164219015[111] = 0;
   out_4283718208164219015[112] = 0;
   out_4283718208164219015[113] = 0;
   out_4283718208164219015[114] = 0;
   out_4283718208164219015[115] = 0;
   out_4283718208164219015[116] = 0;
   out_4283718208164219015[117] = 0;
   out_4283718208164219015[118] = 0;
   out_4283718208164219015[119] = 0;
   out_4283718208164219015[120] = 1;
}
void h_6(double *state, double *sat_pos, double *out_5902373520985669561) {
   out_5902373520985669561[0] = sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2)) + state[6];
}
void H_6(double *state, double *sat_pos, double *out_3487743119837133558) {
   out_3487743119837133558[0] = (-sat_pos[0] + state[0])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_3487743119837133558[1] = (-sat_pos[1] + state[1])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_3487743119837133558[2] = (-sat_pos[2] + state[2])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_3487743119837133558[3] = 0;
   out_3487743119837133558[4] = 0;
   out_3487743119837133558[5] = 0;
   out_3487743119837133558[6] = 1;
   out_3487743119837133558[7] = 0;
   out_3487743119837133558[8] = 0;
   out_3487743119837133558[9] = 0;
   out_3487743119837133558[10] = 0;
}
void h_20(double *state, double *sat_pos, double *out_1800868856491256789) {
   out_1800868856491256789[0] = sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2)) + sat_pos[3]*state[10] + state[6] + state[9];
}
void H_20(double *state, double *sat_pos, double *out_6403079063733113762) {
   out_6403079063733113762[0] = (-sat_pos[0] + state[0])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_6403079063733113762[1] = (-sat_pos[1] + state[1])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_6403079063733113762[2] = (-sat_pos[2] + state[2])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_6403079063733113762[3] = 0;
   out_6403079063733113762[4] = 0;
   out_6403079063733113762[5] = 0;
   out_6403079063733113762[6] = 1;
   out_6403079063733113762[7] = 0;
   out_6403079063733113762[8] = 0;
   out_6403079063733113762[9] = 1;
   out_6403079063733113762[10] = sat_pos[3];
}
void h_7(double *state, double *sat_pos_vel, double *out_8749859653706695012) {
   out_8749859653706695012[0] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[3] - state[3])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[4] - state[4])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + (sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + state[7];
}
void H_7(double *state, double *sat_pos_vel, double *out_2251765923777389959) {
   out_2251765923777389959[0] = pow(sat_pos_vel[0] - state[0], 2)*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[0] - state[0])*(sat_pos_vel[1] - state[1])*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[0] - state[0])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[3] - state[3])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_2251765923777389959[1] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[1] - state[1])*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + pow(sat_pos_vel[1] - state[1], 2)*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[4] - state[4])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_2251765923777389959[2] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + pow(sat_pos_vel[2] - state[2], 2)*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[5] - state[5])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_2251765923777389959[3] = -(sat_pos_vel[0] - state[0])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_2251765923777389959[4] = -(sat_pos_vel[1] - state[1])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_2251765923777389959[5] = -(sat_pos_vel[2] - state[2])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_2251765923777389959[6] = 0;
   out_2251765923777389959[7] = 1;
   out_2251765923777389959[8] = 0;
   out_2251765923777389959[9] = 0;
   out_2251765923777389959[10] = 0;
}
void h_21(double *state, double *sat_pos_vel, double *out_8749859653706695012) {
   out_8749859653706695012[0] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[3] - state[3])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[4] - state[4])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + (sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + state[7];
}
void H_21(double *state, double *sat_pos_vel, double *out_2251765923777389959) {
   out_2251765923777389959[0] = pow(sat_pos_vel[0] - state[0], 2)*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[0] - state[0])*(sat_pos_vel[1] - state[1])*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[0] - state[0])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[3] - state[3])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_2251765923777389959[1] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[1] - state[1])*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + pow(sat_pos_vel[1] - state[1], 2)*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[4] - state[4])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_2251765923777389959[2] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + pow(sat_pos_vel[2] - state[2], 2)*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[5] - state[5])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_2251765923777389959[3] = -(sat_pos_vel[0] - state[0])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_2251765923777389959[4] = -(sat_pos_vel[1] - state[1])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_2251765923777389959[5] = -(sat_pos_vel[2] - state[2])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_2251765923777389959[6] = 0;
   out_2251765923777389959[7] = 1;
   out_2251765923777389959[8] = 0;
   out_2251765923777389959[9] = 0;
   out_2251765923777389959[10] = 0;
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
void gnss_err_fun(double *nom_x, double *delta_x, double *out_2893903750678761352) {
  err_fun(nom_x, delta_x, out_2893903750678761352);
}
void gnss_inv_err_fun(double *nom_x, double *true_x, double *out_1573976658111465050) {
  inv_err_fun(nom_x, true_x, out_1573976658111465050);
}
void gnss_H_mod_fun(double *state, double *out_6669274116786942791) {
  H_mod_fun(state, out_6669274116786942791);
}
void gnss_f_fun(double *state, double dt, double *out_434701726961688353) {
  f_fun(state,  dt, out_434701726961688353);
}
void gnss_F_fun(double *state, double dt, double *out_4283718208164219015) {
  F_fun(state,  dt, out_4283718208164219015);
}
void gnss_h_6(double *state, double *sat_pos, double *out_5902373520985669561) {
  h_6(state, sat_pos, out_5902373520985669561);
}
void gnss_H_6(double *state, double *sat_pos, double *out_3487743119837133558) {
  H_6(state, sat_pos, out_3487743119837133558);
}
void gnss_h_20(double *state, double *sat_pos, double *out_1800868856491256789) {
  h_20(state, sat_pos, out_1800868856491256789);
}
void gnss_H_20(double *state, double *sat_pos, double *out_6403079063733113762) {
  H_20(state, sat_pos, out_6403079063733113762);
}
void gnss_h_7(double *state, double *sat_pos_vel, double *out_8749859653706695012) {
  h_7(state, sat_pos_vel, out_8749859653706695012);
}
void gnss_H_7(double *state, double *sat_pos_vel, double *out_2251765923777389959) {
  H_7(state, sat_pos_vel, out_2251765923777389959);
}
void gnss_h_21(double *state, double *sat_pos_vel, double *out_8749859653706695012) {
  h_21(state, sat_pos_vel, out_8749859653706695012);
}
void gnss_H_21(double *state, double *sat_pos_vel, double *out_2251765923777389959) {
  H_21(state, sat_pos_vel, out_2251765923777389959);
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
