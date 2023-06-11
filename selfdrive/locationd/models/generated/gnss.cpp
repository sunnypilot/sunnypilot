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
void err_fun(double *nom_x, double *delta_x, double *out_4588913850449385760) {
   out_4588913850449385760[0] = delta_x[0] + nom_x[0];
   out_4588913850449385760[1] = delta_x[1] + nom_x[1];
   out_4588913850449385760[2] = delta_x[2] + nom_x[2];
   out_4588913850449385760[3] = delta_x[3] + nom_x[3];
   out_4588913850449385760[4] = delta_x[4] + nom_x[4];
   out_4588913850449385760[5] = delta_x[5] + nom_x[5];
   out_4588913850449385760[6] = delta_x[6] + nom_x[6];
   out_4588913850449385760[7] = delta_x[7] + nom_x[7];
   out_4588913850449385760[8] = delta_x[8] + nom_x[8];
   out_4588913850449385760[9] = delta_x[9] + nom_x[9];
   out_4588913850449385760[10] = delta_x[10] + nom_x[10];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_361280867974834565) {
   out_361280867974834565[0] = -nom_x[0] + true_x[0];
   out_361280867974834565[1] = -nom_x[1] + true_x[1];
   out_361280867974834565[2] = -nom_x[2] + true_x[2];
   out_361280867974834565[3] = -nom_x[3] + true_x[3];
   out_361280867974834565[4] = -nom_x[4] + true_x[4];
   out_361280867974834565[5] = -nom_x[5] + true_x[5];
   out_361280867974834565[6] = -nom_x[6] + true_x[6];
   out_361280867974834565[7] = -nom_x[7] + true_x[7];
   out_361280867974834565[8] = -nom_x[8] + true_x[8];
   out_361280867974834565[9] = -nom_x[9] + true_x[9];
   out_361280867974834565[10] = -nom_x[10] + true_x[10];
}
void H_mod_fun(double *state, double *out_3692418476170695800) {
   out_3692418476170695800[0] = 1.0;
   out_3692418476170695800[1] = 0;
   out_3692418476170695800[2] = 0;
   out_3692418476170695800[3] = 0;
   out_3692418476170695800[4] = 0;
   out_3692418476170695800[5] = 0;
   out_3692418476170695800[6] = 0;
   out_3692418476170695800[7] = 0;
   out_3692418476170695800[8] = 0;
   out_3692418476170695800[9] = 0;
   out_3692418476170695800[10] = 0;
   out_3692418476170695800[11] = 0;
   out_3692418476170695800[12] = 1.0;
   out_3692418476170695800[13] = 0;
   out_3692418476170695800[14] = 0;
   out_3692418476170695800[15] = 0;
   out_3692418476170695800[16] = 0;
   out_3692418476170695800[17] = 0;
   out_3692418476170695800[18] = 0;
   out_3692418476170695800[19] = 0;
   out_3692418476170695800[20] = 0;
   out_3692418476170695800[21] = 0;
   out_3692418476170695800[22] = 0;
   out_3692418476170695800[23] = 0;
   out_3692418476170695800[24] = 1.0;
   out_3692418476170695800[25] = 0;
   out_3692418476170695800[26] = 0;
   out_3692418476170695800[27] = 0;
   out_3692418476170695800[28] = 0;
   out_3692418476170695800[29] = 0;
   out_3692418476170695800[30] = 0;
   out_3692418476170695800[31] = 0;
   out_3692418476170695800[32] = 0;
   out_3692418476170695800[33] = 0;
   out_3692418476170695800[34] = 0;
   out_3692418476170695800[35] = 0;
   out_3692418476170695800[36] = 1.0;
   out_3692418476170695800[37] = 0;
   out_3692418476170695800[38] = 0;
   out_3692418476170695800[39] = 0;
   out_3692418476170695800[40] = 0;
   out_3692418476170695800[41] = 0;
   out_3692418476170695800[42] = 0;
   out_3692418476170695800[43] = 0;
   out_3692418476170695800[44] = 0;
   out_3692418476170695800[45] = 0;
   out_3692418476170695800[46] = 0;
   out_3692418476170695800[47] = 0;
   out_3692418476170695800[48] = 1.0;
   out_3692418476170695800[49] = 0;
   out_3692418476170695800[50] = 0;
   out_3692418476170695800[51] = 0;
   out_3692418476170695800[52] = 0;
   out_3692418476170695800[53] = 0;
   out_3692418476170695800[54] = 0;
   out_3692418476170695800[55] = 0;
   out_3692418476170695800[56] = 0;
   out_3692418476170695800[57] = 0;
   out_3692418476170695800[58] = 0;
   out_3692418476170695800[59] = 0;
   out_3692418476170695800[60] = 1.0;
   out_3692418476170695800[61] = 0;
   out_3692418476170695800[62] = 0;
   out_3692418476170695800[63] = 0;
   out_3692418476170695800[64] = 0;
   out_3692418476170695800[65] = 0;
   out_3692418476170695800[66] = 0;
   out_3692418476170695800[67] = 0;
   out_3692418476170695800[68] = 0;
   out_3692418476170695800[69] = 0;
   out_3692418476170695800[70] = 0;
   out_3692418476170695800[71] = 0;
   out_3692418476170695800[72] = 1.0;
   out_3692418476170695800[73] = 0;
   out_3692418476170695800[74] = 0;
   out_3692418476170695800[75] = 0;
   out_3692418476170695800[76] = 0;
   out_3692418476170695800[77] = 0;
   out_3692418476170695800[78] = 0;
   out_3692418476170695800[79] = 0;
   out_3692418476170695800[80] = 0;
   out_3692418476170695800[81] = 0;
   out_3692418476170695800[82] = 0;
   out_3692418476170695800[83] = 0;
   out_3692418476170695800[84] = 1.0;
   out_3692418476170695800[85] = 0;
   out_3692418476170695800[86] = 0;
   out_3692418476170695800[87] = 0;
   out_3692418476170695800[88] = 0;
   out_3692418476170695800[89] = 0;
   out_3692418476170695800[90] = 0;
   out_3692418476170695800[91] = 0;
   out_3692418476170695800[92] = 0;
   out_3692418476170695800[93] = 0;
   out_3692418476170695800[94] = 0;
   out_3692418476170695800[95] = 0;
   out_3692418476170695800[96] = 1.0;
   out_3692418476170695800[97] = 0;
   out_3692418476170695800[98] = 0;
   out_3692418476170695800[99] = 0;
   out_3692418476170695800[100] = 0;
   out_3692418476170695800[101] = 0;
   out_3692418476170695800[102] = 0;
   out_3692418476170695800[103] = 0;
   out_3692418476170695800[104] = 0;
   out_3692418476170695800[105] = 0;
   out_3692418476170695800[106] = 0;
   out_3692418476170695800[107] = 0;
   out_3692418476170695800[108] = 1.0;
   out_3692418476170695800[109] = 0;
   out_3692418476170695800[110] = 0;
   out_3692418476170695800[111] = 0;
   out_3692418476170695800[112] = 0;
   out_3692418476170695800[113] = 0;
   out_3692418476170695800[114] = 0;
   out_3692418476170695800[115] = 0;
   out_3692418476170695800[116] = 0;
   out_3692418476170695800[117] = 0;
   out_3692418476170695800[118] = 0;
   out_3692418476170695800[119] = 0;
   out_3692418476170695800[120] = 1.0;
}
void f_fun(double *state, double dt, double *out_3599858202863344339) {
   out_3599858202863344339[0] = dt*state[3] + state[0];
   out_3599858202863344339[1] = dt*state[4] + state[1];
   out_3599858202863344339[2] = dt*state[5] + state[2];
   out_3599858202863344339[3] = state[3];
   out_3599858202863344339[4] = state[4];
   out_3599858202863344339[5] = state[5];
   out_3599858202863344339[6] = dt*state[7] + state[6];
   out_3599858202863344339[7] = dt*state[8] + state[7];
   out_3599858202863344339[8] = state[8];
   out_3599858202863344339[9] = state[9];
   out_3599858202863344339[10] = state[10];
}
void F_fun(double *state, double dt, double *out_6614403358289748728) {
   out_6614403358289748728[0] = 1;
   out_6614403358289748728[1] = 0;
   out_6614403358289748728[2] = 0;
   out_6614403358289748728[3] = dt;
   out_6614403358289748728[4] = 0;
   out_6614403358289748728[5] = 0;
   out_6614403358289748728[6] = 0;
   out_6614403358289748728[7] = 0;
   out_6614403358289748728[8] = 0;
   out_6614403358289748728[9] = 0;
   out_6614403358289748728[10] = 0;
   out_6614403358289748728[11] = 0;
   out_6614403358289748728[12] = 1;
   out_6614403358289748728[13] = 0;
   out_6614403358289748728[14] = 0;
   out_6614403358289748728[15] = dt;
   out_6614403358289748728[16] = 0;
   out_6614403358289748728[17] = 0;
   out_6614403358289748728[18] = 0;
   out_6614403358289748728[19] = 0;
   out_6614403358289748728[20] = 0;
   out_6614403358289748728[21] = 0;
   out_6614403358289748728[22] = 0;
   out_6614403358289748728[23] = 0;
   out_6614403358289748728[24] = 1;
   out_6614403358289748728[25] = 0;
   out_6614403358289748728[26] = 0;
   out_6614403358289748728[27] = dt;
   out_6614403358289748728[28] = 0;
   out_6614403358289748728[29] = 0;
   out_6614403358289748728[30] = 0;
   out_6614403358289748728[31] = 0;
   out_6614403358289748728[32] = 0;
   out_6614403358289748728[33] = 0;
   out_6614403358289748728[34] = 0;
   out_6614403358289748728[35] = 0;
   out_6614403358289748728[36] = 1;
   out_6614403358289748728[37] = 0;
   out_6614403358289748728[38] = 0;
   out_6614403358289748728[39] = 0;
   out_6614403358289748728[40] = 0;
   out_6614403358289748728[41] = 0;
   out_6614403358289748728[42] = 0;
   out_6614403358289748728[43] = 0;
   out_6614403358289748728[44] = 0;
   out_6614403358289748728[45] = 0;
   out_6614403358289748728[46] = 0;
   out_6614403358289748728[47] = 0;
   out_6614403358289748728[48] = 1;
   out_6614403358289748728[49] = 0;
   out_6614403358289748728[50] = 0;
   out_6614403358289748728[51] = 0;
   out_6614403358289748728[52] = 0;
   out_6614403358289748728[53] = 0;
   out_6614403358289748728[54] = 0;
   out_6614403358289748728[55] = 0;
   out_6614403358289748728[56] = 0;
   out_6614403358289748728[57] = 0;
   out_6614403358289748728[58] = 0;
   out_6614403358289748728[59] = 0;
   out_6614403358289748728[60] = 1;
   out_6614403358289748728[61] = 0;
   out_6614403358289748728[62] = 0;
   out_6614403358289748728[63] = 0;
   out_6614403358289748728[64] = 0;
   out_6614403358289748728[65] = 0;
   out_6614403358289748728[66] = 0;
   out_6614403358289748728[67] = 0;
   out_6614403358289748728[68] = 0;
   out_6614403358289748728[69] = 0;
   out_6614403358289748728[70] = 0;
   out_6614403358289748728[71] = 0;
   out_6614403358289748728[72] = 1;
   out_6614403358289748728[73] = dt;
   out_6614403358289748728[74] = 0;
   out_6614403358289748728[75] = 0;
   out_6614403358289748728[76] = 0;
   out_6614403358289748728[77] = 0;
   out_6614403358289748728[78] = 0;
   out_6614403358289748728[79] = 0;
   out_6614403358289748728[80] = 0;
   out_6614403358289748728[81] = 0;
   out_6614403358289748728[82] = 0;
   out_6614403358289748728[83] = 0;
   out_6614403358289748728[84] = 1;
   out_6614403358289748728[85] = dt;
   out_6614403358289748728[86] = 0;
   out_6614403358289748728[87] = 0;
   out_6614403358289748728[88] = 0;
   out_6614403358289748728[89] = 0;
   out_6614403358289748728[90] = 0;
   out_6614403358289748728[91] = 0;
   out_6614403358289748728[92] = 0;
   out_6614403358289748728[93] = 0;
   out_6614403358289748728[94] = 0;
   out_6614403358289748728[95] = 0;
   out_6614403358289748728[96] = 1;
   out_6614403358289748728[97] = 0;
   out_6614403358289748728[98] = 0;
   out_6614403358289748728[99] = 0;
   out_6614403358289748728[100] = 0;
   out_6614403358289748728[101] = 0;
   out_6614403358289748728[102] = 0;
   out_6614403358289748728[103] = 0;
   out_6614403358289748728[104] = 0;
   out_6614403358289748728[105] = 0;
   out_6614403358289748728[106] = 0;
   out_6614403358289748728[107] = 0;
   out_6614403358289748728[108] = 1;
   out_6614403358289748728[109] = 0;
   out_6614403358289748728[110] = 0;
   out_6614403358289748728[111] = 0;
   out_6614403358289748728[112] = 0;
   out_6614403358289748728[113] = 0;
   out_6614403358289748728[114] = 0;
   out_6614403358289748728[115] = 0;
   out_6614403358289748728[116] = 0;
   out_6614403358289748728[117] = 0;
   out_6614403358289748728[118] = 0;
   out_6614403358289748728[119] = 0;
   out_6614403358289748728[120] = 1;
}
void h_6(double *state, double *sat_pos, double *out_3965377368938519904) {
   out_3965377368938519904[0] = sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2)) + state[6];
}
void H_6(double *state, double *sat_pos, double *out_4010469744061131744) {
   out_4010469744061131744[0] = (-sat_pos[0] + state[0])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_4010469744061131744[1] = (-sat_pos[1] + state[1])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_4010469744061131744[2] = (-sat_pos[2] + state[2])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_4010469744061131744[3] = 0;
   out_4010469744061131744[4] = 0;
   out_4010469744061131744[5] = 0;
   out_4010469744061131744[6] = 1;
   out_4010469744061131744[7] = 0;
   out_4010469744061131744[8] = 0;
   out_4010469744061131744[9] = 0;
   out_4010469744061131744[10] = 0;
}
void h_20(double *state, double *sat_pos, double *out_4397465078196892446) {
   out_4397465078196892446[0] = sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2)) + sat_pos[3]*state[10] + state[6] + state[9];
}
void H_20(double *state, double *sat_pos, double *out_7230021967014098202) {
   out_7230021967014098202[0] = (-sat_pos[0] + state[0])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_7230021967014098202[1] = (-sat_pos[1] + state[1])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_7230021967014098202[2] = (-sat_pos[2] + state[2])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_7230021967014098202[3] = 0;
   out_7230021967014098202[4] = 0;
   out_7230021967014098202[5] = 0;
   out_7230021967014098202[6] = 1;
   out_7230021967014098202[7] = 0;
   out_7230021967014098202[8] = 0;
   out_7230021967014098202[9] = 1;
   out_7230021967014098202[10] = sat_pos[3];
}
void h_7(double *state, double *sat_pos_vel, double *out_8859539764878579118) {
   out_8859539764878579118[0] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[3] - state[3])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[4] - state[4])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + (sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + state[7];
}
void H_7(double *state, double *sat_pos_vel, double *out_6351382189608033375) {
   out_6351382189608033375[0] = pow(sat_pos_vel[0] - state[0], 2)*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[0] - state[0])*(sat_pos_vel[1] - state[1])*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[0] - state[0])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[3] - state[3])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_6351382189608033375[1] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[1] - state[1])*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + pow(sat_pos_vel[1] - state[1], 2)*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[4] - state[4])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_6351382189608033375[2] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + pow(sat_pos_vel[2] - state[2], 2)*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[5] - state[5])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_6351382189608033375[3] = -(sat_pos_vel[0] - state[0])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_6351382189608033375[4] = -(sat_pos_vel[1] - state[1])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_6351382189608033375[5] = -(sat_pos_vel[2] - state[2])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_6351382189608033375[6] = 0;
   out_6351382189608033375[7] = 1;
   out_6351382189608033375[8] = 0;
   out_6351382189608033375[9] = 0;
   out_6351382189608033375[10] = 0;
}
void h_21(double *state, double *sat_pos_vel, double *out_8859539764878579118) {
   out_8859539764878579118[0] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[3] - state[3])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[4] - state[4])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + (sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + state[7];
}
void H_21(double *state, double *sat_pos_vel, double *out_6351382189608033375) {
   out_6351382189608033375[0] = pow(sat_pos_vel[0] - state[0], 2)*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[0] - state[0])*(sat_pos_vel[1] - state[1])*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[0] - state[0])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[3] - state[3])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_6351382189608033375[1] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[1] - state[1])*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + pow(sat_pos_vel[1] - state[1], 2)*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[4] - state[4])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_6351382189608033375[2] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + pow(sat_pos_vel[2] - state[2], 2)*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[5] - state[5])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_6351382189608033375[3] = -(sat_pos_vel[0] - state[0])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_6351382189608033375[4] = -(sat_pos_vel[1] - state[1])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_6351382189608033375[5] = -(sat_pos_vel[2] - state[2])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_6351382189608033375[6] = 0;
   out_6351382189608033375[7] = 1;
   out_6351382189608033375[8] = 0;
   out_6351382189608033375[9] = 0;
   out_6351382189608033375[10] = 0;
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
void gnss_err_fun(double *nom_x, double *delta_x, double *out_4588913850449385760) {
  err_fun(nom_x, delta_x, out_4588913850449385760);
}
void gnss_inv_err_fun(double *nom_x, double *true_x, double *out_361280867974834565) {
  inv_err_fun(nom_x, true_x, out_361280867974834565);
}
void gnss_H_mod_fun(double *state, double *out_3692418476170695800) {
  H_mod_fun(state, out_3692418476170695800);
}
void gnss_f_fun(double *state, double dt, double *out_3599858202863344339) {
  f_fun(state,  dt, out_3599858202863344339);
}
void gnss_F_fun(double *state, double dt, double *out_6614403358289748728) {
  F_fun(state,  dt, out_6614403358289748728);
}
void gnss_h_6(double *state, double *sat_pos, double *out_3965377368938519904) {
  h_6(state, sat_pos, out_3965377368938519904);
}
void gnss_H_6(double *state, double *sat_pos, double *out_4010469744061131744) {
  H_6(state, sat_pos, out_4010469744061131744);
}
void gnss_h_20(double *state, double *sat_pos, double *out_4397465078196892446) {
  h_20(state, sat_pos, out_4397465078196892446);
}
void gnss_H_20(double *state, double *sat_pos, double *out_7230021967014098202) {
  H_20(state, sat_pos, out_7230021967014098202);
}
void gnss_h_7(double *state, double *sat_pos_vel, double *out_8859539764878579118) {
  h_7(state, sat_pos_vel, out_8859539764878579118);
}
void gnss_H_7(double *state, double *sat_pos_vel, double *out_6351382189608033375) {
  H_7(state, sat_pos_vel, out_6351382189608033375);
}
void gnss_h_21(double *state, double *sat_pos_vel, double *out_8859539764878579118) {
  h_21(state, sat_pos_vel, out_8859539764878579118);
}
void gnss_H_21(double *state, double *sat_pos_vel, double *out_6351382189608033375) {
  H_21(state, sat_pos_vel, out_6351382189608033375);
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
