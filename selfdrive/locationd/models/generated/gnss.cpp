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
void err_fun(double *nom_x, double *delta_x, double *out_1087418696294830103) {
   out_1087418696294830103[0] = delta_x[0] + nom_x[0];
   out_1087418696294830103[1] = delta_x[1] + nom_x[1];
   out_1087418696294830103[2] = delta_x[2] + nom_x[2];
   out_1087418696294830103[3] = delta_x[3] + nom_x[3];
   out_1087418696294830103[4] = delta_x[4] + nom_x[4];
   out_1087418696294830103[5] = delta_x[5] + nom_x[5];
   out_1087418696294830103[6] = delta_x[6] + nom_x[6];
   out_1087418696294830103[7] = delta_x[7] + nom_x[7];
   out_1087418696294830103[8] = delta_x[8] + nom_x[8];
   out_1087418696294830103[9] = delta_x[9] + nom_x[9];
   out_1087418696294830103[10] = delta_x[10] + nom_x[10];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_746412675603881976) {
   out_746412675603881976[0] = -nom_x[0] + true_x[0];
   out_746412675603881976[1] = -nom_x[1] + true_x[1];
   out_746412675603881976[2] = -nom_x[2] + true_x[2];
   out_746412675603881976[3] = -nom_x[3] + true_x[3];
   out_746412675603881976[4] = -nom_x[4] + true_x[4];
   out_746412675603881976[5] = -nom_x[5] + true_x[5];
   out_746412675603881976[6] = -nom_x[6] + true_x[6];
   out_746412675603881976[7] = -nom_x[7] + true_x[7];
   out_746412675603881976[8] = -nom_x[8] + true_x[8];
   out_746412675603881976[9] = -nom_x[9] + true_x[9];
   out_746412675603881976[10] = -nom_x[10] + true_x[10];
}
void H_mod_fun(double *state, double *out_6902851921478182689) {
   out_6902851921478182689[0] = 1.0;
   out_6902851921478182689[1] = 0;
   out_6902851921478182689[2] = 0;
   out_6902851921478182689[3] = 0;
   out_6902851921478182689[4] = 0;
   out_6902851921478182689[5] = 0;
   out_6902851921478182689[6] = 0;
   out_6902851921478182689[7] = 0;
   out_6902851921478182689[8] = 0;
   out_6902851921478182689[9] = 0;
   out_6902851921478182689[10] = 0;
   out_6902851921478182689[11] = 0;
   out_6902851921478182689[12] = 1.0;
   out_6902851921478182689[13] = 0;
   out_6902851921478182689[14] = 0;
   out_6902851921478182689[15] = 0;
   out_6902851921478182689[16] = 0;
   out_6902851921478182689[17] = 0;
   out_6902851921478182689[18] = 0;
   out_6902851921478182689[19] = 0;
   out_6902851921478182689[20] = 0;
   out_6902851921478182689[21] = 0;
   out_6902851921478182689[22] = 0;
   out_6902851921478182689[23] = 0;
   out_6902851921478182689[24] = 1.0;
   out_6902851921478182689[25] = 0;
   out_6902851921478182689[26] = 0;
   out_6902851921478182689[27] = 0;
   out_6902851921478182689[28] = 0;
   out_6902851921478182689[29] = 0;
   out_6902851921478182689[30] = 0;
   out_6902851921478182689[31] = 0;
   out_6902851921478182689[32] = 0;
   out_6902851921478182689[33] = 0;
   out_6902851921478182689[34] = 0;
   out_6902851921478182689[35] = 0;
   out_6902851921478182689[36] = 1.0;
   out_6902851921478182689[37] = 0;
   out_6902851921478182689[38] = 0;
   out_6902851921478182689[39] = 0;
   out_6902851921478182689[40] = 0;
   out_6902851921478182689[41] = 0;
   out_6902851921478182689[42] = 0;
   out_6902851921478182689[43] = 0;
   out_6902851921478182689[44] = 0;
   out_6902851921478182689[45] = 0;
   out_6902851921478182689[46] = 0;
   out_6902851921478182689[47] = 0;
   out_6902851921478182689[48] = 1.0;
   out_6902851921478182689[49] = 0;
   out_6902851921478182689[50] = 0;
   out_6902851921478182689[51] = 0;
   out_6902851921478182689[52] = 0;
   out_6902851921478182689[53] = 0;
   out_6902851921478182689[54] = 0;
   out_6902851921478182689[55] = 0;
   out_6902851921478182689[56] = 0;
   out_6902851921478182689[57] = 0;
   out_6902851921478182689[58] = 0;
   out_6902851921478182689[59] = 0;
   out_6902851921478182689[60] = 1.0;
   out_6902851921478182689[61] = 0;
   out_6902851921478182689[62] = 0;
   out_6902851921478182689[63] = 0;
   out_6902851921478182689[64] = 0;
   out_6902851921478182689[65] = 0;
   out_6902851921478182689[66] = 0;
   out_6902851921478182689[67] = 0;
   out_6902851921478182689[68] = 0;
   out_6902851921478182689[69] = 0;
   out_6902851921478182689[70] = 0;
   out_6902851921478182689[71] = 0;
   out_6902851921478182689[72] = 1.0;
   out_6902851921478182689[73] = 0;
   out_6902851921478182689[74] = 0;
   out_6902851921478182689[75] = 0;
   out_6902851921478182689[76] = 0;
   out_6902851921478182689[77] = 0;
   out_6902851921478182689[78] = 0;
   out_6902851921478182689[79] = 0;
   out_6902851921478182689[80] = 0;
   out_6902851921478182689[81] = 0;
   out_6902851921478182689[82] = 0;
   out_6902851921478182689[83] = 0;
   out_6902851921478182689[84] = 1.0;
   out_6902851921478182689[85] = 0;
   out_6902851921478182689[86] = 0;
   out_6902851921478182689[87] = 0;
   out_6902851921478182689[88] = 0;
   out_6902851921478182689[89] = 0;
   out_6902851921478182689[90] = 0;
   out_6902851921478182689[91] = 0;
   out_6902851921478182689[92] = 0;
   out_6902851921478182689[93] = 0;
   out_6902851921478182689[94] = 0;
   out_6902851921478182689[95] = 0;
   out_6902851921478182689[96] = 1.0;
   out_6902851921478182689[97] = 0;
   out_6902851921478182689[98] = 0;
   out_6902851921478182689[99] = 0;
   out_6902851921478182689[100] = 0;
   out_6902851921478182689[101] = 0;
   out_6902851921478182689[102] = 0;
   out_6902851921478182689[103] = 0;
   out_6902851921478182689[104] = 0;
   out_6902851921478182689[105] = 0;
   out_6902851921478182689[106] = 0;
   out_6902851921478182689[107] = 0;
   out_6902851921478182689[108] = 1.0;
   out_6902851921478182689[109] = 0;
   out_6902851921478182689[110] = 0;
   out_6902851921478182689[111] = 0;
   out_6902851921478182689[112] = 0;
   out_6902851921478182689[113] = 0;
   out_6902851921478182689[114] = 0;
   out_6902851921478182689[115] = 0;
   out_6902851921478182689[116] = 0;
   out_6902851921478182689[117] = 0;
   out_6902851921478182689[118] = 0;
   out_6902851921478182689[119] = 0;
   out_6902851921478182689[120] = 1.0;
}
void f_fun(double *state, double dt, double *out_5347949339748000854) {
   out_5347949339748000854[0] = dt*state[3] + state[0];
   out_5347949339748000854[1] = dt*state[4] + state[1];
   out_5347949339748000854[2] = dt*state[5] + state[2];
   out_5347949339748000854[3] = state[3];
   out_5347949339748000854[4] = state[4];
   out_5347949339748000854[5] = state[5];
   out_5347949339748000854[6] = dt*state[7] + state[6];
   out_5347949339748000854[7] = dt*state[8] + state[7];
   out_5347949339748000854[8] = state[8];
   out_5347949339748000854[9] = state[9];
   out_5347949339748000854[10] = state[10];
}
void F_fun(double *state, double dt, double *out_3634795260627257152) {
   out_3634795260627257152[0] = 1;
   out_3634795260627257152[1] = 0;
   out_3634795260627257152[2] = 0;
   out_3634795260627257152[3] = dt;
   out_3634795260627257152[4] = 0;
   out_3634795260627257152[5] = 0;
   out_3634795260627257152[6] = 0;
   out_3634795260627257152[7] = 0;
   out_3634795260627257152[8] = 0;
   out_3634795260627257152[9] = 0;
   out_3634795260627257152[10] = 0;
   out_3634795260627257152[11] = 0;
   out_3634795260627257152[12] = 1;
   out_3634795260627257152[13] = 0;
   out_3634795260627257152[14] = 0;
   out_3634795260627257152[15] = dt;
   out_3634795260627257152[16] = 0;
   out_3634795260627257152[17] = 0;
   out_3634795260627257152[18] = 0;
   out_3634795260627257152[19] = 0;
   out_3634795260627257152[20] = 0;
   out_3634795260627257152[21] = 0;
   out_3634795260627257152[22] = 0;
   out_3634795260627257152[23] = 0;
   out_3634795260627257152[24] = 1;
   out_3634795260627257152[25] = 0;
   out_3634795260627257152[26] = 0;
   out_3634795260627257152[27] = dt;
   out_3634795260627257152[28] = 0;
   out_3634795260627257152[29] = 0;
   out_3634795260627257152[30] = 0;
   out_3634795260627257152[31] = 0;
   out_3634795260627257152[32] = 0;
   out_3634795260627257152[33] = 0;
   out_3634795260627257152[34] = 0;
   out_3634795260627257152[35] = 0;
   out_3634795260627257152[36] = 1;
   out_3634795260627257152[37] = 0;
   out_3634795260627257152[38] = 0;
   out_3634795260627257152[39] = 0;
   out_3634795260627257152[40] = 0;
   out_3634795260627257152[41] = 0;
   out_3634795260627257152[42] = 0;
   out_3634795260627257152[43] = 0;
   out_3634795260627257152[44] = 0;
   out_3634795260627257152[45] = 0;
   out_3634795260627257152[46] = 0;
   out_3634795260627257152[47] = 0;
   out_3634795260627257152[48] = 1;
   out_3634795260627257152[49] = 0;
   out_3634795260627257152[50] = 0;
   out_3634795260627257152[51] = 0;
   out_3634795260627257152[52] = 0;
   out_3634795260627257152[53] = 0;
   out_3634795260627257152[54] = 0;
   out_3634795260627257152[55] = 0;
   out_3634795260627257152[56] = 0;
   out_3634795260627257152[57] = 0;
   out_3634795260627257152[58] = 0;
   out_3634795260627257152[59] = 0;
   out_3634795260627257152[60] = 1;
   out_3634795260627257152[61] = 0;
   out_3634795260627257152[62] = 0;
   out_3634795260627257152[63] = 0;
   out_3634795260627257152[64] = 0;
   out_3634795260627257152[65] = 0;
   out_3634795260627257152[66] = 0;
   out_3634795260627257152[67] = 0;
   out_3634795260627257152[68] = 0;
   out_3634795260627257152[69] = 0;
   out_3634795260627257152[70] = 0;
   out_3634795260627257152[71] = 0;
   out_3634795260627257152[72] = 1;
   out_3634795260627257152[73] = dt;
   out_3634795260627257152[74] = 0;
   out_3634795260627257152[75] = 0;
   out_3634795260627257152[76] = 0;
   out_3634795260627257152[77] = 0;
   out_3634795260627257152[78] = 0;
   out_3634795260627257152[79] = 0;
   out_3634795260627257152[80] = 0;
   out_3634795260627257152[81] = 0;
   out_3634795260627257152[82] = 0;
   out_3634795260627257152[83] = 0;
   out_3634795260627257152[84] = 1;
   out_3634795260627257152[85] = dt;
   out_3634795260627257152[86] = 0;
   out_3634795260627257152[87] = 0;
   out_3634795260627257152[88] = 0;
   out_3634795260627257152[89] = 0;
   out_3634795260627257152[90] = 0;
   out_3634795260627257152[91] = 0;
   out_3634795260627257152[92] = 0;
   out_3634795260627257152[93] = 0;
   out_3634795260627257152[94] = 0;
   out_3634795260627257152[95] = 0;
   out_3634795260627257152[96] = 1;
   out_3634795260627257152[97] = 0;
   out_3634795260627257152[98] = 0;
   out_3634795260627257152[99] = 0;
   out_3634795260627257152[100] = 0;
   out_3634795260627257152[101] = 0;
   out_3634795260627257152[102] = 0;
   out_3634795260627257152[103] = 0;
   out_3634795260627257152[104] = 0;
   out_3634795260627257152[105] = 0;
   out_3634795260627257152[106] = 0;
   out_3634795260627257152[107] = 0;
   out_3634795260627257152[108] = 1;
   out_3634795260627257152[109] = 0;
   out_3634795260627257152[110] = 0;
   out_3634795260627257152[111] = 0;
   out_3634795260627257152[112] = 0;
   out_3634795260627257152[113] = 0;
   out_3634795260627257152[114] = 0;
   out_3634795260627257152[115] = 0;
   out_3634795260627257152[116] = 0;
   out_3634795260627257152[117] = 0;
   out_3634795260627257152[118] = 0;
   out_3634795260627257152[119] = 0;
   out_3634795260627257152[120] = 1;
}
void h_6(double *state, double *sat_pos, double *out_4914217899585156638) {
   out_4914217899585156638[0] = sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2)) + state[6];
}
void H_6(double *state, double *sat_pos, double *out_9069722082748577789) {
   out_9069722082748577789[0] = (-sat_pos[0] + state[0])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_9069722082748577789[1] = (-sat_pos[1] + state[1])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_9069722082748577789[2] = (-sat_pos[2] + state[2])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_9069722082748577789[3] = 0;
   out_9069722082748577789[4] = 0;
   out_9069722082748577789[5] = 0;
   out_9069722082748577789[6] = 1;
   out_9069722082748577789[7] = 0;
   out_9069722082748577789[8] = 0;
   out_9069722082748577789[9] = 0;
   out_9069722082748577789[10] = 0;
}
void h_20(double *state, double *sat_pos, double *out_4990935818312259304) {
   out_4990935818312259304[0] = sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2)) + sat_pos[3]*state[10] + state[6] + state[9];
}
void H_20(double *state, double *sat_pos, double *out_3839852145693933779) {
   out_3839852145693933779[0] = (-sat_pos[0] + state[0])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_3839852145693933779[1] = (-sat_pos[1] + state[1])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_3839852145693933779[2] = (-sat_pos[2] + state[2])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_3839852145693933779[3] = 0;
   out_3839852145693933779[4] = 0;
   out_3839852145693933779[5] = 0;
   out_3839852145693933779[6] = 1;
   out_3839852145693933779[7] = 0;
   out_3839852145693933779[8] = 0;
   out_3839852145693933779[9] = 1;
   out_3839852145693933779[10] = sat_pos[3];
}
void h_7(double *state, double *sat_pos_vel, double *out_5214992409236640740) {
   out_5214992409236640740[0] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[3] - state[3])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[4] - state[4])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + (sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + state[7];
}
void H_7(double *state, double *sat_pos_vel, double *out_1614394445830539317) {
   out_1614394445830539317[0] = pow(sat_pos_vel[0] - state[0], 2)*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[0] - state[0])*(sat_pos_vel[1] - state[1])*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[0] - state[0])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[3] - state[3])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_1614394445830539317[1] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[1] - state[1])*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + pow(sat_pos_vel[1] - state[1], 2)*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[4] - state[4])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_1614394445830539317[2] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + pow(sat_pos_vel[2] - state[2], 2)*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[5] - state[5])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_1614394445830539317[3] = -(sat_pos_vel[0] - state[0])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_1614394445830539317[4] = -(sat_pos_vel[1] - state[1])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_1614394445830539317[5] = -(sat_pos_vel[2] - state[2])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_1614394445830539317[6] = 0;
   out_1614394445830539317[7] = 1;
   out_1614394445830539317[8] = 0;
   out_1614394445830539317[9] = 0;
   out_1614394445830539317[10] = 0;
}
void h_21(double *state, double *sat_pos_vel, double *out_5214992409236640740) {
   out_5214992409236640740[0] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[3] - state[3])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[4] - state[4])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + (sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + state[7];
}
void H_21(double *state, double *sat_pos_vel, double *out_1614394445830539317) {
   out_1614394445830539317[0] = pow(sat_pos_vel[0] - state[0], 2)*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[0] - state[0])*(sat_pos_vel[1] - state[1])*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[0] - state[0])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[3] - state[3])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_1614394445830539317[1] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[1] - state[1])*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + pow(sat_pos_vel[1] - state[1], 2)*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[4] - state[4])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_1614394445830539317[2] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + pow(sat_pos_vel[2] - state[2], 2)*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[5] - state[5])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_1614394445830539317[3] = -(sat_pos_vel[0] - state[0])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_1614394445830539317[4] = -(sat_pos_vel[1] - state[1])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_1614394445830539317[5] = -(sat_pos_vel[2] - state[2])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_1614394445830539317[6] = 0;
   out_1614394445830539317[7] = 1;
   out_1614394445830539317[8] = 0;
   out_1614394445830539317[9] = 0;
   out_1614394445830539317[10] = 0;
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
void gnss_err_fun(double *nom_x, double *delta_x, double *out_1087418696294830103) {
  err_fun(nom_x, delta_x, out_1087418696294830103);
}
void gnss_inv_err_fun(double *nom_x, double *true_x, double *out_746412675603881976) {
  inv_err_fun(nom_x, true_x, out_746412675603881976);
}
void gnss_H_mod_fun(double *state, double *out_6902851921478182689) {
  H_mod_fun(state, out_6902851921478182689);
}
void gnss_f_fun(double *state, double dt, double *out_5347949339748000854) {
  f_fun(state,  dt, out_5347949339748000854);
}
void gnss_F_fun(double *state, double dt, double *out_3634795260627257152) {
  F_fun(state,  dt, out_3634795260627257152);
}
void gnss_h_6(double *state, double *sat_pos, double *out_4914217899585156638) {
  h_6(state, sat_pos, out_4914217899585156638);
}
void gnss_H_6(double *state, double *sat_pos, double *out_9069722082748577789) {
  H_6(state, sat_pos, out_9069722082748577789);
}
void gnss_h_20(double *state, double *sat_pos, double *out_4990935818312259304) {
  h_20(state, sat_pos, out_4990935818312259304);
}
void gnss_H_20(double *state, double *sat_pos, double *out_3839852145693933779) {
  H_20(state, sat_pos, out_3839852145693933779);
}
void gnss_h_7(double *state, double *sat_pos_vel, double *out_5214992409236640740) {
  h_7(state, sat_pos_vel, out_5214992409236640740);
}
void gnss_H_7(double *state, double *sat_pos_vel, double *out_1614394445830539317) {
  H_7(state, sat_pos_vel, out_1614394445830539317);
}
void gnss_h_21(double *state, double *sat_pos_vel, double *out_5214992409236640740) {
  h_21(state, sat_pos_vel, out_5214992409236640740);
}
void gnss_H_21(double *state, double *sat_pos_vel, double *out_1614394445830539317) {
  H_21(state, sat_pos_vel, out_1614394445830539317);
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
