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
void err_fun(double *nom_x, double *delta_x, double *out_6747998805596484752) {
   out_6747998805596484752[0] = delta_x[0] + nom_x[0];
   out_6747998805596484752[1] = delta_x[1] + nom_x[1];
   out_6747998805596484752[2] = delta_x[2] + nom_x[2];
   out_6747998805596484752[3] = delta_x[3] + nom_x[3];
   out_6747998805596484752[4] = delta_x[4] + nom_x[4];
   out_6747998805596484752[5] = delta_x[5] + nom_x[5];
   out_6747998805596484752[6] = delta_x[6] + nom_x[6];
   out_6747998805596484752[7] = delta_x[7] + nom_x[7];
   out_6747998805596484752[8] = delta_x[8] + nom_x[8];
   out_6747998805596484752[9] = delta_x[9] + nom_x[9];
   out_6747998805596484752[10] = delta_x[10] + nom_x[10];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_6535890535670437130) {
   out_6535890535670437130[0] = -nom_x[0] + true_x[0];
   out_6535890535670437130[1] = -nom_x[1] + true_x[1];
   out_6535890535670437130[2] = -nom_x[2] + true_x[2];
   out_6535890535670437130[3] = -nom_x[3] + true_x[3];
   out_6535890535670437130[4] = -nom_x[4] + true_x[4];
   out_6535890535670437130[5] = -nom_x[5] + true_x[5];
   out_6535890535670437130[6] = -nom_x[6] + true_x[6];
   out_6535890535670437130[7] = -nom_x[7] + true_x[7];
   out_6535890535670437130[8] = -nom_x[8] + true_x[8];
   out_6535890535670437130[9] = -nom_x[9] + true_x[9];
   out_6535890535670437130[10] = -nom_x[10] + true_x[10];
}
void H_mod_fun(double *state, double *out_4448015362564357721) {
   out_4448015362564357721[0] = 1.0;
   out_4448015362564357721[1] = 0;
   out_4448015362564357721[2] = 0;
   out_4448015362564357721[3] = 0;
   out_4448015362564357721[4] = 0;
   out_4448015362564357721[5] = 0;
   out_4448015362564357721[6] = 0;
   out_4448015362564357721[7] = 0;
   out_4448015362564357721[8] = 0;
   out_4448015362564357721[9] = 0;
   out_4448015362564357721[10] = 0;
   out_4448015362564357721[11] = 0;
   out_4448015362564357721[12] = 1.0;
   out_4448015362564357721[13] = 0;
   out_4448015362564357721[14] = 0;
   out_4448015362564357721[15] = 0;
   out_4448015362564357721[16] = 0;
   out_4448015362564357721[17] = 0;
   out_4448015362564357721[18] = 0;
   out_4448015362564357721[19] = 0;
   out_4448015362564357721[20] = 0;
   out_4448015362564357721[21] = 0;
   out_4448015362564357721[22] = 0;
   out_4448015362564357721[23] = 0;
   out_4448015362564357721[24] = 1.0;
   out_4448015362564357721[25] = 0;
   out_4448015362564357721[26] = 0;
   out_4448015362564357721[27] = 0;
   out_4448015362564357721[28] = 0;
   out_4448015362564357721[29] = 0;
   out_4448015362564357721[30] = 0;
   out_4448015362564357721[31] = 0;
   out_4448015362564357721[32] = 0;
   out_4448015362564357721[33] = 0;
   out_4448015362564357721[34] = 0;
   out_4448015362564357721[35] = 0;
   out_4448015362564357721[36] = 1.0;
   out_4448015362564357721[37] = 0;
   out_4448015362564357721[38] = 0;
   out_4448015362564357721[39] = 0;
   out_4448015362564357721[40] = 0;
   out_4448015362564357721[41] = 0;
   out_4448015362564357721[42] = 0;
   out_4448015362564357721[43] = 0;
   out_4448015362564357721[44] = 0;
   out_4448015362564357721[45] = 0;
   out_4448015362564357721[46] = 0;
   out_4448015362564357721[47] = 0;
   out_4448015362564357721[48] = 1.0;
   out_4448015362564357721[49] = 0;
   out_4448015362564357721[50] = 0;
   out_4448015362564357721[51] = 0;
   out_4448015362564357721[52] = 0;
   out_4448015362564357721[53] = 0;
   out_4448015362564357721[54] = 0;
   out_4448015362564357721[55] = 0;
   out_4448015362564357721[56] = 0;
   out_4448015362564357721[57] = 0;
   out_4448015362564357721[58] = 0;
   out_4448015362564357721[59] = 0;
   out_4448015362564357721[60] = 1.0;
   out_4448015362564357721[61] = 0;
   out_4448015362564357721[62] = 0;
   out_4448015362564357721[63] = 0;
   out_4448015362564357721[64] = 0;
   out_4448015362564357721[65] = 0;
   out_4448015362564357721[66] = 0;
   out_4448015362564357721[67] = 0;
   out_4448015362564357721[68] = 0;
   out_4448015362564357721[69] = 0;
   out_4448015362564357721[70] = 0;
   out_4448015362564357721[71] = 0;
   out_4448015362564357721[72] = 1.0;
   out_4448015362564357721[73] = 0;
   out_4448015362564357721[74] = 0;
   out_4448015362564357721[75] = 0;
   out_4448015362564357721[76] = 0;
   out_4448015362564357721[77] = 0;
   out_4448015362564357721[78] = 0;
   out_4448015362564357721[79] = 0;
   out_4448015362564357721[80] = 0;
   out_4448015362564357721[81] = 0;
   out_4448015362564357721[82] = 0;
   out_4448015362564357721[83] = 0;
   out_4448015362564357721[84] = 1.0;
   out_4448015362564357721[85] = 0;
   out_4448015362564357721[86] = 0;
   out_4448015362564357721[87] = 0;
   out_4448015362564357721[88] = 0;
   out_4448015362564357721[89] = 0;
   out_4448015362564357721[90] = 0;
   out_4448015362564357721[91] = 0;
   out_4448015362564357721[92] = 0;
   out_4448015362564357721[93] = 0;
   out_4448015362564357721[94] = 0;
   out_4448015362564357721[95] = 0;
   out_4448015362564357721[96] = 1.0;
   out_4448015362564357721[97] = 0;
   out_4448015362564357721[98] = 0;
   out_4448015362564357721[99] = 0;
   out_4448015362564357721[100] = 0;
   out_4448015362564357721[101] = 0;
   out_4448015362564357721[102] = 0;
   out_4448015362564357721[103] = 0;
   out_4448015362564357721[104] = 0;
   out_4448015362564357721[105] = 0;
   out_4448015362564357721[106] = 0;
   out_4448015362564357721[107] = 0;
   out_4448015362564357721[108] = 1.0;
   out_4448015362564357721[109] = 0;
   out_4448015362564357721[110] = 0;
   out_4448015362564357721[111] = 0;
   out_4448015362564357721[112] = 0;
   out_4448015362564357721[113] = 0;
   out_4448015362564357721[114] = 0;
   out_4448015362564357721[115] = 0;
   out_4448015362564357721[116] = 0;
   out_4448015362564357721[117] = 0;
   out_4448015362564357721[118] = 0;
   out_4448015362564357721[119] = 0;
   out_4448015362564357721[120] = 1.0;
}
void f_fun(double *state, double dt, double *out_9118525254568713176) {
   out_9118525254568713176[0] = dt*state[3] + state[0];
   out_9118525254568713176[1] = dt*state[4] + state[1];
   out_9118525254568713176[2] = dt*state[5] + state[2];
   out_9118525254568713176[3] = state[3];
   out_9118525254568713176[4] = state[4];
   out_9118525254568713176[5] = state[5];
   out_9118525254568713176[6] = dt*state[7] + state[6];
   out_9118525254568713176[7] = dt*state[8] + state[7];
   out_9118525254568713176[8] = state[8];
   out_9118525254568713176[9] = state[9];
   out_9118525254568713176[10] = state[10];
}
void F_fun(double *state, double dt, double *out_6402003280863482888) {
   out_6402003280863482888[0] = 1;
   out_6402003280863482888[1] = 0;
   out_6402003280863482888[2] = 0;
   out_6402003280863482888[3] = dt;
   out_6402003280863482888[4] = 0;
   out_6402003280863482888[5] = 0;
   out_6402003280863482888[6] = 0;
   out_6402003280863482888[7] = 0;
   out_6402003280863482888[8] = 0;
   out_6402003280863482888[9] = 0;
   out_6402003280863482888[10] = 0;
   out_6402003280863482888[11] = 0;
   out_6402003280863482888[12] = 1;
   out_6402003280863482888[13] = 0;
   out_6402003280863482888[14] = 0;
   out_6402003280863482888[15] = dt;
   out_6402003280863482888[16] = 0;
   out_6402003280863482888[17] = 0;
   out_6402003280863482888[18] = 0;
   out_6402003280863482888[19] = 0;
   out_6402003280863482888[20] = 0;
   out_6402003280863482888[21] = 0;
   out_6402003280863482888[22] = 0;
   out_6402003280863482888[23] = 0;
   out_6402003280863482888[24] = 1;
   out_6402003280863482888[25] = 0;
   out_6402003280863482888[26] = 0;
   out_6402003280863482888[27] = dt;
   out_6402003280863482888[28] = 0;
   out_6402003280863482888[29] = 0;
   out_6402003280863482888[30] = 0;
   out_6402003280863482888[31] = 0;
   out_6402003280863482888[32] = 0;
   out_6402003280863482888[33] = 0;
   out_6402003280863482888[34] = 0;
   out_6402003280863482888[35] = 0;
   out_6402003280863482888[36] = 1;
   out_6402003280863482888[37] = 0;
   out_6402003280863482888[38] = 0;
   out_6402003280863482888[39] = 0;
   out_6402003280863482888[40] = 0;
   out_6402003280863482888[41] = 0;
   out_6402003280863482888[42] = 0;
   out_6402003280863482888[43] = 0;
   out_6402003280863482888[44] = 0;
   out_6402003280863482888[45] = 0;
   out_6402003280863482888[46] = 0;
   out_6402003280863482888[47] = 0;
   out_6402003280863482888[48] = 1;
   out_6402003280863482888[49] = 0;
   out_6402003280863482888[50] = 0;
   out_6402003280863482888[51] = 0;
   out_6402003280863482888[52] = 0;
   out_6402003280863482888[53] = 0;
   out_6402003280863482888[54] = 0;
   out_6402003280863482888[55] = 0;
   out_6402003280863482888[56] = 0;
   out_6402003280863482888[57] = 0;
   out_6402003280863482888[58] = 0;
   out_6402003280863482888[59] = 0;
   out_6402003280863482888[60] = 1;
   out_6402003280863482888[61] = 0;
   out_6402003280863482888[62] = 0;
   out_6402003280863482888[63] = 0;
   out_6402003280863482888[64] = 0;
   out_6402003280863482888[65] = 0;
   out_6402003280863482888[66] = 0;
   out_6402003280863482888[67] = 0;
   out_6402003280863482888[68] = 0;
   out_6402003280863482888[69] = 0;
   out_6402003280863482888[70] = 0;
   out_6402003280863482888[71] = 0;
   out_6402003280863482888[72] = 1;
   out_6402003280863482888[73] = dt;
   out_6402003280863482888[74] = 0;
   out_6402003280863482888[75] = 0;
   out_6402003280863482888[76] = 0;
   out_6402003280863482888[77] = 0;
   out_6402003280863482888[78] = 0;
   out_6402003280863482888[79] = 0;
   out_6402003280863482888[80] = 0;
   out_6402003280863482888[81] = 0;
   out_6402003280863482888[82] = 0;
   out_6402003280863482888[83] = 0;
   out_6402003280863482888[84] = 1;
   out_6402003280863482888[85] = dt;
   out_6402003280863482888[86] = 0;
   out_6402003280863482888[87] = 0;
   out_6402003280863482888[88] = 0;
   out_6402003280863482888[89] = 0;
   out_6402003280863482888[90] = 0;
   out_6402003280863482888[91] = 0;
   out_6402003280863482888[92] = 0;
   out_6402003280863482888[93] = 0;
   out_6402003280863482888[94] = 0;
   out_6402003280863482888[95] = 0;
   out_6402003280863482888[96] = 1;
   out_6402003280863482888[97] = 0;
   out_6402003280863482888[98] = 0;
   out_6402003280863482888[99] = 0;
   out_6402003280863482888[100] = 0;
   out_6402003280863482888[101] = 0;
   out_6402003280863482888[102] = 0;
   out_6402003280863482888[103] = 0;
   out_6402003280863482888[104] = 0;
   out_6402003280863482888[105] = 0;
   out_6402003280863482888[106] = 0;
   out_6402003280863482888[107] = 0;
   out_6402003280863482888[108] = 1;
   out_6402003280863482888[109] = 0;
   out_6402003280863482888[110] = 0;
   out_6402003280863482888[111] = 0;
   out_6402003280863482888[112] = 0;
   out_6402003280863482888[113] = 0;
   out_6402003280863482888[114] = 0;
   out_6402003280863482888[115] = 0;
   out_6402003280863482888[116] = 0;
   out_6402003280863482888[117] = 0;
   out_6402003280863482888[118] = 0;
   out_6402003280863482888[119] = 0;
   out_6402003280863482888[120] = 1;
}
void h_6(double *state, double *sat_pos, double *out_5846375561327839295) {
   out_5846375561327839295[0] = sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2)) + state[6];
}
void H_6(double *state, double *sat_pos, double *out_2124454474474073235) {
   out_2124454474474073235[0] = (-sat_pos[0] + state[0])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_2124454474474073235[1] = (-sat_pos[1] + state[1])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_2124454474474073235[2] = (-sat_pos[2] + state[2])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_2124454474474073235[3] = 0;
   out_2124454474474073235[4] = 0;
   out_2124454474474073235[5] = 0;
   out_2124454474474073235[6] = 1;
   out_2124454474474073235[7] = 0;
   out_2124454474474073235[8] = 0;
   out_2124454474474073235[9] = 0;
   out_2124454474474073235[10] = 0;
}
void h_20(double *state, double *sat_pos, double *out_963325950330645553) {
   out_963325950330645553[0] = sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2)) + sat_pos[3]*state[10] + state[6] + state[9];
}
void H_20(double *state, double *sat_pos, double *out_963608637703027460) {
   out_963608637703027460[0] = (-sat_pos[0] + state[0])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_963608637703027460[1] = (-sat_pos[1] + state[1])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_963608637703027460[2] = (-sat_pos[2] + state[2])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_963608637703027460[3] = 0;
   out_963608637703027460[4] = 0;
   out_963608637703027460[5] = 0;
   out_963608637703027460[6] = 1;
   out_963608637703027460[7] = 0;
   out_963608637703027460[8] = 0;
   out_963608637703027460[9] = 1;
   out_963608637703027460[10] = sat_pos[3];
}
void h_7(double *state, double *sat_pos_vel, double *out_9158958912499879745) {
   out_9158958912499879745[0] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[3] - state[3])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[4] - state[4])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + (sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + state[7];
}
void H_7(double *state, double *sat_pos_vel, double *out_1177645737388839302) {
   out_1177645737388839302[0] = pow(sat_pos_vel[0] - state[0], 2)*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[0] - state[0])*(sat_pos_vel[1] - state[1])*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[0] - state[0])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[3] - state[3])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_1177645737388839302[1] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[1] - state[1])*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + pow(sat_pos_vel[1] - state[1], 2)*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[4] - state[4])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_1177645737388839302[2] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + pow(sat_pos_vel[2] - state[2], 2)*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[5] - state[5])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_1177645737388839302[3] = -(sat_pos_vel[0] - state[0])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_1177645737388839302[4] = -(sat_pos_vel[1] - state[1])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_1177645737388839302[5] = -(sat_pos_vel[2] - state[2])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_1177645737388839302[6] = 0;
   out_1177645737388839302[7] = 1;
   out_1177645737388839302[8] = 0;
   out_1177645737388839302[9] = 0;
   out_1177645737388839302[10] = 0;
}
void h_21(double *state, double *sat_pos_vel, double *out_9158958912499879745) {
   out_9158958912499879745[0] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[3] - state[3])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[4] - state[4])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + (sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + state[7];
}
void H_21(double *state, double *sat_pos_vel, double *out_1177645737388839302) {
   out_1177645737388839302[0] = pow(sat_pos_vel[0] - state[0], 2)*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[0] - state[0])*(sat_pos_vel[1] - state[1])*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[0] - state[0])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[3] - state[3])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_1177645737388839302[1] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[1] - state[1])*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + pow(sat_pos_vel[1] - state[1], 2)*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[4] - state[4])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_1177645737388839302[2] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + pow(sat_pos_vel[2] - state[2], 2)*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[5] - state[5])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_1177645737388839302[3] = -(sat_pos_vel[0] - state[0])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_1177645737388839302[4] = -(sat_pos_vel[1] - state[1])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_1177645737388839302[5] = -(sat_pos_vel[2] - state[2])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_1177645737388839302[6] = 0;
   out_1177645737388839302[7] = 1;
   out_1177645737388839302[8] = 0;
   out_1177645737388839302[9] = 0;
   out_1177645737388839302[10] = 0;
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
void gnss_err_fun(double *nom_x, double *delta_x, double *out_6747998805596484752) {
  err_fun(nom_x, delta_x, out_6747998805596484752);
}
void gnss_inv_err_fun(double *nom_x, double *true_x, double *out_6535890535670437130) {
  inv_err_fun(nom_x, true_x, out_6535890535670437130);
}
void gnss_H_mod_fun(double *state, double *out_4448015362564357721) {
  H_mod_fun(state, out_4448015362564357721);
}
void gnss_f_fun(double *state, double dt, double *out_9118525254568713176) {
  f_fun(state,  dt, out_9118525254568713176);
}
void gnss_F_fun(double *state, double dt, double *out_6402003280863482888) {
  F_fun(state,  dt, out_6402003280863482888);
}
void gnss_h_6(double *state, double *sat_pos, double *out_5846375561327839295) {
  h_6(state, sat_pos, out_5846375561327839295);
}
void gnss_H_6(double *state, double *sat_pos, double *out_2124454474474073235) {
  H_6(state, sat_pos, out_2124454474474073235);
}
void gnss_h_20(double *state, double *sat_pos, double *out_963325950330645553) {
  h_20(state, sat_pos, out_963325950330645553);
}
void gnss_H_20(double *state, double *sat_pos, double *out_963608637703027460) {
  H_20(state, sat_pos, out_963608637703027460);
}
void gnss_h_7(double *state, double *sat_pos_vel, double *out_9158958912499879745) {
  h_7(state, sat_pos_vel, out_9158958912499879745);
}
void gnss_H_7(double *state, double *sat_pos_vel, double *out_1177645737388839302) {
  H_7(state, sat_pos_vel, out_1177645737388839302);
}
void gnss_h_21(double *state, double *sat_pos_vel, double *out_9158958912499879745) {
  h_21(state, sat_pos_vel, out_9158958912499879745);
}
void gnss_H_21(double *state, double *sat_pos_vel, double *out_1177645737388839302) {
  H_21(state, sat_pos_vel, out_1177645737388839302);
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
