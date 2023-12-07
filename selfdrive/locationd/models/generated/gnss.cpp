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
void err_fun(double *nom_x, double *delta_x, double *out_2891005972447064978) {
   out_2891005972447064978[0] = delta_x[0] + nom_x[0];
   out_2891005972447064978[1] = delta_x[1] + nom_x[1];
   out_2891005972447064978[2] = delta_x[2] + nom_x[2];
   out_2891005972447064978[3] = delta_x[3] + nom_x[3];
   out_2891005972447064978[4] = delta_x[4] + nom_x[4];
   out_2891005972447064978[5] = delta_x[5] + nom_x[5];
   out_2891005972447064978[6] = delta_x[6] + nom_x[6];
   out_2891005972447064978[7] = delta_x[7] + nom_x[7];
   out_2891005972447064978[8] = delta_x[8] + nom_x[8];
   out_2891005972447064978[9] = delta_x[9] + nom_x[9];
   out_2891005972447064978[10] = delta_x[10] + nom_x[10];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_3707348186065527957) {
   out_3707348186065527957[0] = -nom_x[0] + true_x[0];
   out_3707348186065527957[1] = -nom_x[1] + true_x[1];
   out_3707348186065527957[2] = -nom_x[2] + true_x[2];
   out_3707348186065527957[3] = -nom_x[3] + true_x[3];
   out_3707348186065527957[4] = -nom_x[4] + true_x[4];
   out_3707348186065527957[5] = -nom_x[5] + true_x[5];
   out_3707348186065527957[6] = -nom_x[6] + true_x[6];
   out_3707348186065527957[7] = -nom_x[7] + true_x[7];
   out_3707348186065527957[8] = -nom_x[8] + true_x[8];
   out_3707348186065527957[9] = -nom_x[9] + true_x[9];
   out_3707348186065527957[10] = -nom_x[10] + true_x[10];
}
void H_mod_fun(double *state, double *out_3968679355288269749) {
   out_3968679355288269749[0] = 1.0;
   out_3968679355288269749[1] = 0;
   out_3968679355288269749[2] = 0;
   out_3968679355288269749[3] = 0;
   out_3968679355288269749[4] = 0;
   out_3968679355288269749[5] = 0;
   out_3968679355288269749[6] = 0;
   out_3968679355288269749[7] = 0;
   out_3968679355288269749[8] = 0;
   out_3968679355288269749[9] = 0;
   out_3968679355288269749[10] = 0;
   out_3968679355288269749[11] = 0;
   out_3968679355288269749[12] = 1.0;
   out_3968679355288269749[13] = 0;
   out_3968679355288269749[14] = 0;
   out_3968679355288269749[15] = 0;
   out_3968679355288269749[16] = 0;
   out_3968679355288269749[17] = 0;
   out_3968679355288269749[18] = 0;
   out_3968679355288269749[19] = 0;
   out_3968679355288269749[20] = 0;
   out_3968679355288269749[21] = 0;
   out_3968679355288269749[22] = 0;
   out_3968679355288269749[23] = 0;
   out_3968679355288269749[24] = 1.0;
   out_3968679355288269749[25] = 0;
   out_3968679355288269749[26] = 0;
   out_3968679355288269749[27] = 0;
   out_3968679355288269749[28] = 0;
   out_3968679355288269749[29] = 0;
   out_3968679355288269749[30] = 0;
   out_3968679355288269749[31] = 0;
   out_3968679355288269749[32] = 0;
   out_3968679355288269749[33] = 0;
   out_3968679355288269749[34] = 0;
   out_3968679355288269749[35] = 0;
   out_3968679355288269749[36] = 1.0;
   out_3968679355288269749[37] = 0;
   out_3968679355288269749[38] = 0;
   out_3968679355288269749[39] = 0;
   out_3968679355288269749[40] = 0;
   out_3968679355288269749[41] = 0;
   out_3968679355288269749[42] = 0;
   out_3968679355288269749[43] = 0;
   out_3968679355288269749[44] = 0;
   out_3968679355288269749[45] = 0;
   out_3968679355288269749[46] = 0;
   out_3968679355288269749[47] = 0;
   out_3968679355288269749[48] = 1.0;
   out_3968679355288269749[49] = 0;
   out_3968679355288269749[50] = 0;
   out_3968679355288269749[51] = 0;
   out_3968679355288269749[52] = 0;
   out_3968679355288269749[53] = 0;
   out_3968679355288269749[54] = 0;
   out_3968679355288269749[55] = 0;
   out_3968679355288269749[56] = 0;
   out_3968679355288269749[57] = 0;
   out_3968679355288269749[58] = 0;
   out_3968679355288269749[59] = 0;
   out_3968679355288269749[60] = 1.0;
   out_3968679355288269749[61] = 0;
   out_3968679355288269749[62] = 0;
   out_3968679355288269749[63] = 0;
   out_3968679355288269749[64] = 0;
   out_3968679355288269749[65] = 0;
   out_3968679355288269749[66] = 0;
   out_3968679355288269749[67] = 0;
   out_3968679355288269749[68] = 0;
   out_3968679355288269749[69] = 0;
   out_3968679355288269749[70] = 0;
   out_3968679355288269749[71] = 0;
   out_3968679355288269749[72] = 1.0;
   out_3968679355288269749[73] = 0;
   out_3968679355288269749[74] = 0;
   out_3968679355288269749[75] = 0;
   out_3968679355288269749[76] = 0;
   out_3968679355288269749[77] = 0;
   out_3968679355288269749[78] = 0;
   out_3968679355288269749[79] = 0;
   out_3968679355288269749[80] = 0;
   out_3968679355288269749[81] = 0;
   out_3968679355288269749[82] = 0;
   out_3968679355288269749[83] = 0;
   out_3968679355288269749[84] = 1.0;
   out_3968679355288269749[85] = 0;
   out_3968679355288269749[86] = 0;
   out_3968679355288269749[87] = 0;
   out_3968679355288269749[88] = 0;
   out_3968679355288269749[89] = 0;
   out_3968679355288269749[90] = 0;
   out_3968679355288269749[91] = 0;
   out_3968679355288269749[92] = 0;
   out_3968679355288269749[93] = 0;
   out_3968679355288269749[94] = 0;
   out_3968679355288269749[95] = 0;
   out_3968679355288269749[96] = 1.0;
   out_3968679355288269749[97] = 0;
   out_3968679355288269749[98] = 0;
   out_3968679355288269749[99] = 0;
   out_3968679355288269749[100] = 0;
   out_3968679355288269749[101] = 0;
   out_3968679355288269749[102] = 0;
   out_3968679355288269749[103] = 0;
   out_3968679355288269749[104] = 0;
   out_3968679355288269749[105] = 0;
   out_3968679355288269749[106] = 0;
   out_3968679355288269749[107] = 0;
   out_3968679355288269749[108] = 1.0;
   out_3968679355288269749[109] = 0;
   out_3968679355288269749[110] = 0;
   out_3968679355288269749[111] = 0;
   out_3968679355288269749[112] = 0;
   out_3968679355288269749[113] = 0;
   out_3968679355288269749[114] = 0;
   out_3968679355288269749[115] = 0;
   out_3968679355288269749[116] = 0;
   out_3968679355288269749[117] = 0;
   out_3968679355288269749[118] = 0;
   out_3968679355288269749[119] = 0;
   out_3968679355288269749[120] = 1.0;
}
void f_fun(double *state, double dt, double *out_399920222174142974) {
   out_399920222174142974[0] = dt*state[3] + state[0];
   out_399920222174142974[1] = dt*state[4] + state[1];
   out_399920222174142974[2] = dt*state[5] + state[2];
   out_399920222174142974[3] = state[3];
   out_399920222174142974[4] = state[4];
   out_399920222174142974[5] = state[5];
   out_399920222174142974[6] = dt*state[7] + state[6];
   out_399920222174142974[7] = dt*state[8] + state[7];
   out_399920222174142974[8] = state[8];
   out_399920222174142974[9] = state[9];
   out_399920222174142974[10] = state[10];
}
void F_fun(double *state, double dt, double *out_4032596610344199094) {
   out_4032596610344199094[0] = 1;
   out_4032596610344199094[1] = 0;
   out_4032596610344199094[2] = 0;
   out_4032596610344199094[3] = dt;
   out_4032596610344199094[4] = 0;
   out_4032596610344199094[5] = 0;
   out_4032596610344199094[6] = 0;
   out_4032596610344199094[7] = 0;
   out_4032596610344199094[8] = 0;
   out_4032596610344199094[9] = 0;
   out_4032596610344199094[10] = 0;
   out_4032596610344199094[11] = 0;
   out_4032596610344199094[12] = 1;
   out_4032596610344199094[13] = 0;
   out_4032596610344199094[14] = 0;
   out_4032596610344199094[15] = dt;
   out_4032596610344199094[16] = 0;
   out_4032596610344199094[17] = 0;
   out_4032596610344199094[18] = 0;
   out_4032596610344199094[19] = 0;
   out_4032596610344199094[20] = 0;
   out_4032596610344199094[21] = 0;
   out_4032596610344199094[22] = 0;
   out_4032596610344199094[23] = 0;
   out_4032596610344199094[24] = 1;
   out_4032596610344199094[25] = 0;
   out_4032596610344199094[26] = 0;
   out_4032596610344199094[27] = dt;
   out_4032596610344199094[28] = 0;
   out_4032596610344199094[29] = 0;
   out_4032596610344199094[30] = 0;
   out_4032596610344199094[31] = 0;
   out_4032596610344199094[32] = 0;
   out_4032596610344199094[33] = 0;
   out_4032596610344199094[34] = 0;
   out_4032596610344199094[35] = 0;
   out_4032596610344199094[36] = 1;
   out_4032596610344199094[37] = 0;
   out_4032596610344199094[38] = 0;
   out_4032596610344199094[39] = 0;
   out_4032596610344199094[40] = 0;
   out_4032596610344199094[41] = 0;
   out_4032596610344199094[42] = 0;
   out_4032596610344199094[43] = 0;
   out_4032596610344199094[44] = 0;
   out_4032596610344199094[45] = 0;
   out_4032596610344199094[46] = 0;
   out_4032596610344199094[47] = 0;
   out_4032596610344199094[48] = 1;
   out_4032596610344199094[49] = 0;
   out_4032596610344199094[50] = 0;
   out_4032596610344199094[51] = 0;
   out_4032596610344199094[52] = 0;
   out_4032596610344199094[53] = 0;
   out_4032596610344199094[54] = 0;
   out_4032596610344199094[55] = 0;
   out_4032596610344199094[56] = 0;
   out_4032596610344199094[57] = 0;
   out_4032596610344199094[58] = 0;
   out_4032596610344199094[59] = 0;
   out_4032596610344199094[60] = 1;
   out_4032596610344199094[61] = 0;
   out_4032596610344199094[62] = 0;
   out_4032596610344199094[63] = 0;
   out_4032596610344199094[64] = 0;
   out_4032596610344199094[65] = 0;
   out_4032596610344199094[66] = 0;
   out_4032596610344199094[67] = 0;
   out_4032596610344199094[68] = 0;
   out_4032596610344199094[69] = 0;
   out_4032596610344199094[70] = 0;
   out_4032596610344199094[71] = 0;
   out_4032596610344199094[72] = 1;
   out_4032596610344199094[73] = dt;
   out_4032596610344199094[74] = 0;
   out_4032596610344199094[75] = 0;
   out_4032596610344199094[76] = 0;
   out_4032596610344199094[77] = 0;
   out_4032596610344199094[78] = 0;
   out_4032596610344199094[79] = 0;
   out_4032596610344199094[80] = 0;
   out_4032596610344199094[81] = 0;
   out_4032596610344199094[82] = 0;
   out_4032596610344199094[83] = 0;
   out_4032596610344199094[84] = 1;
   out_4032596610344199094[85] = dt;
   out_4032596610344199094[86] = 0;
   out_4032596610344199094[87] = 0;
   out_4032596610344199094[88] = 0;
   out_4032596610344199094[89] = 0;
   out_4032596610344199094[90] = 0;
   out_4032596610344199094[91] = 0;
   out_4032596610344199094[92] = 0;
   out_4032596610344199094[93] = 0;
   out_4032596610344199094[94] = 0;
   out_4032596610344199094[95] = 0;
   out_4032596610344199094[96] = 1;
   out_4032596610344199094[97] = 0;
   out_4032596610344199094[98] = 0;
   out_4032596610344199094[99] = 0;
   out_4032596610344199094[100] = 0;
   out_4032596610344199094[101] = 0;
   out_4032596610344199094[102] = 0;
   out_4032596610344199094[103] = 0;
   out_4032596610344199094[104] = 0;
   out_4032596610344199094[105] = 0;
   out_4032596610344199094[106] = 0;
   out_4032596610344199094[107] = 0;
   out_4032596610344199094[108] = 1;
   out_4032596610344199094[109] = 0;
   out_4032596610344199094[110] = 0;
   out_4032596610344199094[111] = 0;
   out_4032596610344199094[112] = 0;
   out_4032596610344199094[113] = 0;
   out_4032596610344199094[114] = 0;
   out_4032596610344199094[115] = 0;
   out_4032596610344199094[116] = 0;
   out_4032596610344199094[117] = 0;
   out_4032596610344199094[118] = 0;
   out_4032596610344199094[119] = 0;
   out_4032596610344199094[120] = 1;
}
void h_6(double *state, double *sat_pos, double *out_7663281162910400321) {
   out_7663281162910400321[0] = sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2)) + state[6];
}
void H_6(double *state, double *sat_pos, double *out_6735513936967990127) {
   out_6735513936967990127[0] = (-sat_pos[0] + state[0])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_6735513936967990127[1] = (-sat_pos[1] + state[1])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_6735513936967990127[2] = (-sat_pos[2] + state[2])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_6735513936967990127[3] = 0;
   out_6735513936967990127[4] = 0;
   out_6735513936967990127[5] = 0;
   out_6735513936967990127[6] = 1;
   out_6735513936967990127[7] = 0;
   out_6735513936967990127[8] = 0;
   out_6735513936967990127[9] = 0;
   out_6735513936967990127[10] = 0;
}
void h_20(double *state, double *sat_pos, double *out_113008328182865177) {
   out_113008328182865177[0] = sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2)) + sat_pos[3]*state[10] + state[6] + state[9];
}
void H_20(double *state, double *sat_pos, double *out_8868019487569726413) {
   out_8868019487569726413[0] = (-sat_pos[0] + state[0])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_8868019487569726413[1] = (-sat_pos[1] + state[1])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_8868019487569726413[2] = (-sat_pos[2] + state[2])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_8868019487569726413[3] = 0;
   out_8868019487569726413[4] = 0;
   out_8868019487569726413[5] = 0;
   out_8868019487569726413[6] = 1;
   out_8868019487569726413[7] = 0;
   out_8868019487569726413[8] = 0;
   out_8868019487569726413[9] = 1;
   out_8868019487569726413[10] = sat_pos[3];
}
void h_7(double *state, double *sat_pos_vel, double *out_4555536823234833923) {
   out_4555536823234833923[0] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[3] - state[3])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[4] - state[4])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + (sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + state[7];
}
void H_7(double *state, double *sat_pos_vel, double *out_4061718503456001340) {
   out_4061718503456001340[0] = pow(sat_pos_vel[0] - state[0], 2)*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[0] - state[0])*(sat_pos_vel[1] - state[1])*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[0] - state[0])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[3] - state[3])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_4061718503456001340[1] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[1] - state[1])*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + pow(sat_pos_vel[1] - state[1], 2)*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[4] - state[4])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_4061718503456001340[2] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + pow(sat_pos_vel[2] - state[2], 2)*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[5] - state[5])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_4061718503456001340[3] = -(sat_pos_vel[0] - state[0])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_4061718503456001340[4] = -(sat_pos_vel[1] - state[1])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_4061718503456001340[5] = -(sat_pos_vel[2] - state[2])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_4061718503456001340[6] = 0;
   out_4061718503456001340[7] = 1;
   out_4061718503456001340[8] = 0;
   out_4061718503456001340[9] = 0;
   out_4061718503456001340[10] = 0;
}
void h_21(double *state, double *sat_pos_vel, double *out_4555536823234833923) {
   out_4555536823234833923[0] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[3] - state[3])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[4] - state[4])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + (sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + state[7];
}
void H_21(double *state, double *sat_pos_vel, double *out_4061718503456001340) {
   out_4061718503456001340[0] = pow(sat_pos_vel[0] - state[0], 2)*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[0] - state[0])*(sat_pos_vel[1] - state[1])*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[0] - state[0])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[3] - state[3])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_4061718503456001340[1] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[1] - state[1])*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + pow(sat_pos_vel[1] - state[1], 2)*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[4] - state[4])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_4061718503456001340[2] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + pow(sat_pos_vel[2] - state[2], 2)*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[5] - state[5])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_4061718503456001340[3] = -(sat_pos_vel[0] - state[0])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_4061718503456001340[4] = -(sat_pos_vel[1] - state[1])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_4061718503456001340[5] = -(sat_pos_vel[2] - state[2])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_4061718503456001340[6] = 0;
   out_4061718503456001340[7] = 1;
   out_4061718503456001340[8] = 0;
   out_4061718503456001340[9] = 0;
   out_4061718503456001340[10] = 0;
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
void gnss_err_fun(double *nom_x, double *delta_x, double *out_2891005972447064978) {
  err_fun(nom_x, delta_x, out_2891005972447064978);
}
void gnss_inv_err_fun(double *nom_x, double *true_x, double *out_3707348186065527957) {
  inv_err_fun(nom_x, true_x, out_3707348186065527957);
}
void gnss_H_mod_fun(double *state, double *out_3968679355288269749) {
  H_mod_fun(state, out_3968679355288269749);
}
void gnss_f_fun(double *state, double dt, double *out_399920222174142974) {
  f_fun(state,  dt, out_399920222174142974);
}
void gnss_F_fun(double *state, double dt, double *out_4032596610344199094) {
  F_fun(state,  dt, out_4032596610344199094);
}
void gnss_h_6(double *state, double *sat_pos, double *out_7663281162910400321) {
  h_6(state, sat_pos, out_7663281162910400321);
}
void gnss_H_6(double *state, double *sat_pos, double *out_6735513936967990127) {
  H_6(state, sat_pos, out_6735513936967990127);
}
void gnss_h_20(double *state, double *sat_pos, double *out_113008328182865177) {
  h_20(state, sat_pos, out_113008328182865177);
}
void gnss_H_20(double *state, double *sat_pos, double *out_8868019487569726413) {
  H_20(state, sat_pos, out_8868019487569726413);
}
void gnss_h_7(double *state, double *sat_pos_vel, double *out_4555536823234833923) {
  h_7(state, sat_pos_vel, out_4555536823234833923);
}
void gnss_H_7(double *state, double *sat_pos_vel, double *out_4061718503456001340) {
  H_7(state, sat_pos_vel, out_4061718503456001340);
}
void gnss_h_21(double *state, double *sat_pos_vel, double *out_4555536823234833923) {
  h_21(state, sat_pos_vel, out_4555536823234833923);
}
void gnss_H_21(double *state, double *sat_pos_vel, double *out_4061718503456001340) {
  H_21(state, sat_pos_vel, out_4061718503456001340);
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
