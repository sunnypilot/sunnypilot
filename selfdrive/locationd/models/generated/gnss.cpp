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
void err_fun(double *nom_x, double *delta_x, double *out_5196781054003887891) {
   out_5196781054003887891[0] = delta_x[0] + nom_x[0];
   out_5196781054003887891[1] = delta_x[1] + nom_x[1];
   out_5196781054003887891[2] = delta_x[2] + nom_x[2];
   out_5196781054003887891[3] = delta_x[3] + nom_x[3];
   out_5196781054003887891[4] = delta_x[4] + nom_x[4];
   out_5196781054003887891[5] = delta_x[5] + nom_x[5];
   out_5196781054003887891[6] = delta_x[6] + nom_x[6];
   out_5196781054003887891[7] = delta_x[7] + nom_x[7];
   out_5196781054003887891[8] = delta_x[8] + nom_x[8];
   out_5196781054003887891[9] = delta_x[9] + nom_x[9];
   out_5196781054003887891[10] = delta_x[10] + nom_x[10];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_817175628468433117) {
   out_817175628468433117[0] = -nom_x[0] + true_x[0];
   out_817175628468433117[1] = -nom_x[1] + true_x[1];
   out_817175628468433117[2] = -nom_x[2] + true_x[2];
   out_817175628468433117[3] = -nom_x[3] + true_x[3];
   out_817175628468433117[4] = -nom_x[4] + true_x[4];
   out_817175628468433117[5] = -nom_x[5] + true_x[5];
   out_817175628468433117[6] = -nom_x[6] + true_x[6];
   out_817175628468433117[7] = -nom_x[7] + true_x[7];
   out_817175628468433117[8] = -nom_x[8] + true_x[8];
   out_817175628468433117[9] = -nom_x[9] + true_x[9];
   out_817175628468433117[10] = -nom_x[10] + true_x[10];
}
void H_mod_fun(double *state, double *out_6506367600169501482) {
   out_6506367600169501482[0] = 1.0;
   out_6506367600169501482[1] = 0;
   out_6506367600169501482[2] = 0;
   out_6506367600169501482[3] = 0;
   out_6506367600169501482[4] = 0;
   out_6506367600169501482[5] = 0;
   out_6506367600169501482[6] = 0;
   out_6506367600169501482[7] = 0;
   out_6506367600169501482[8] = 0;
   out_6506367600169501482[9] = 0;
   out_6506367600169501482[10] = 0;
   out_6506367600169501482[11] = 0;
   out_6506367600169501482[12] = 1.0;
   out_6506367600169501482[13] = 0;
   out_6506367600169501482[14] = 0;
   out_6506367600169501482[15] = 0;
   out_6506367600169501482[16] = 0;
   out_6506367600169501482[17] = 0;
   out_6506367600169501482[18] = 0;
   out_6506367600169501482[19] = 0;
   out_6506367600169501482[20] = 0;
   out_6506367600169501482[21] = 0;
   out_6506367600169501482[22] = 0;
   out_6506367600169501482[23] = 0;
   out_6506367600169501482[24] = 1.0;
   out_6506367600169501482[25] = 0;
   out_6506367600169501482[26] = 0;
   out_6506367600169501482[27] = 0;
   out_6506367600169501482[28] = 0;
   out_6506367600169501482[29] = 0;
   out_6506367600169501482[30] = 0;
   out_6506367600169501482[31] = 0;
   out_6506367600169501482[32] = 0;
   out_6506367600169501482[33] = 0;
   out_6506367600169501482[34] = 0;
   out_6506367600169501482[35] = 0;
   out_6506367600169501482[36] = 1.0;
   out_6506367600169501482[37] = 0;
   out_6506367600169501482[38] = 0;
   out_6506367600169501482[39] = 0;
   out_6506367600169501482[40] = 0;
   out_6506367600169501482[41] = 0;
   out_6506367600169501482[42] = 0;
   out_6506367600169501482[43] = 0;
   out_6506367600169501482[44] = 0;
   out_6506367600169501482[45] = 0;
   out_6506367600169501482[46] = 0;
   out_6506367600169501482[47] = 0;
   out_6506367600169501482[48] = 1.0;
   out_6506367600169501482[49] = 0;
   out_6506367600169501482[50] = 0;
   out_6506367600169501482[51] = 0;
   out_6506367600169501482[52] = 0;
   out_6506367600169501482[53] = 0;
   out_6506367600169501482[54] = 0;
   out_6506367600169501482[55] = 0;
   out_6506367600169501482[56] = 0;
   out_6506367600169501482[57] = 0;
   out_6506367600169501482[58] = 0;
   out_6506367600169501482[59] = 0;
   out_6506367600169501482[60] = 1.0;
   out_6506367600169501482[61] = 0;
   out_6506367600169501482[62] = 0;
   out_6506367600169501482[63] = 0;
   out_6506367600169501482[64] = 0;
   out_6506367600169501482[65] = 0;
   out_6506367600169501482[66] = 0;
   out_6506367600169501482[67] = 0;
   out_6506367600169501482[68] = 0;
   out_6506367600169501482[69] = 0;
   out_6506367600169501482[70] = 0;
   out_6506367600169501482[71] = 0;
   out_6506367600169501482[72] = 1.0;
   out_6506367600169501482[73] = 0;
   out_6506367600169501482[74] = 0;
   out_6506367600169501482[75] = 0;
   out_6506367600169501482[76] = 0;
   out_6506367600169501482[77] = 0;
   out_6506367600169501482[78] = 0;
   out_6506367600169501482[79] = 0;
   out_6506367600169501482[80] = 0;
   out_6506367600169501482[81] = 0;
   out_6506367600169501482[82] = 0;
   out_6506367600169501482[83] = 0;
   out_6506367600169501482[84] = 1.0;
   out_6506367600169501482[85] = 0;
   out_6506367600169501482[86] = 0;
   out_6506367600169501482[87] = 0;
   out_6506367600169501482[88] = 0;
   out_6506367600169501482[89] = 0;
   out_6506367600169501482[90] = 0;
   out_6506367600169501482[91] = 0;
   out_6506367600169501482[92] = 0;
   out_6506367600169501482[93] = 0;
   out_6506367600169501482[94] = 0;
   out_6506367600169501482[95] = 0;
   out_6506367600169501482[96] = 1.0;
   out_6506367600169501482[97] = 0;
   out_6506367600169501482[98] = 0;
   out_6506367600169501482[99] = 0;
   out_6506367600169501482[100] = 0;
   out_6506367600169501482[101] = 0;
   out_6506367600169501482[102] = 0;
   out_6506367600169501482[103] = 0;
   out_6506367600169501482[104] = 0;
   out_6506367600169501482[105] = 0;
   out_6506367600169501482[106] = 0;
   out_6506367600169501482[107] = 0;
   out_6506367600169501482[108] = 1.0;
   out_6506367600169501482[109] = 0;
   out_6506367600169501482[110] = 0;
   out_6506367600169501482[111] = 0;
   out_6506367600169501482[112] = 0;
   out_6506367600169501482[113] = 0;
   out_6506367600169501482[114] = 0;
   out_6506367600169501482[115] = 0;
   out_6506367600169501482[116] = 0;
   out_6506367600169501482[117] = 0;
   out_6506367600169501482[118] = 0;
   out_6506367600169501482[119] = 0;
   out_6506367600169501482[120] = 1.0;
}
void f_fun(double *state, double dt, double *out_4633542785125246216) {
   out_4633542785125246216[0] = dt*state[3] + state[0];
   out_4633542785125246216[1] = dt*state[4] + state[1];
   out_4633542785125246216[2] = dt*state[5] + state[2];
   out_4633542785125246216[3] = state[3];
   out_4633542785125246216[4] = state[4];
   out_4633542785125246216[5] = state[5];
   out_4633542785125246216[6] = dt*state[7] + state[6];
   out_4633542785125246216[7] = dt*state[8] + state[7];
   out_4633542785125246216[8] = state[8];
   out_4633542785125246216[9] = state[9];
   out_4633542785125246216[10] = state[10];
}
void F_fun(double *state, double dt, double *out_3078776459737750197) {
   out_3078776459737750197[0] = 1;
   out_3078776459737750197[1] = 0;
   out_3078776459737750197[2] = 0;
   out_3078776459737750197[3] = dt;
   out_3078776459737750197[4] = 0;
   out_3078776459737750197[5] = 0;
   out_3078776459737750197[6] = 0;
   out_3078776459737750197[7] = 0;
   out_3078776459737750197[8] = 0;
   out_3078776459737750197[9] = 0;
   out_3078776459737750197[10] = 0;
   out_3078776459737750197[11] = 0;
   out_3078776459737750197[12] = 1;
   out_3078776459737750197[13] = 0;
   out_3078776459737750197[14] = 0;
   out_3078776459737750197[15] = dt;
   out_3078776459737750197[16] = 0;
   out_3078776459737750197[17] = 0;
   out_3078776459737750197[18] = 0;
   out_3078776459737750197[19] = 0;
   out_3078776459737750197[20] = 0;
   out_3078776459737750197[21] = 0;
   out_3078776459737750197[22] = 0;
   out_3078776459737750197[23] = 0;
   out_3078776459737750197[24] = 1;
   out_3078776459737750197[25] = 0;
   out_3078776459737750197[26] = 0;
   out_3078776459737750197[27] = dt;
   out_3078776459737750197[28] = 0;
   out_3078776459737750197[29] = 0;
   out_3078776459737750197[30] = 0;
   out_3078776459737750197[31] = 0;
   out_3078776459737750197[32] = 0;
   out_3078776459737750197[33] = 0;
   out_3078776459737750197[34] = 0;
   out_3078776459737750197[35] = 0;
   out_3078776459737750197[36] = 1;
   out_3078776459737750197[37] = 0;
   out_3078776459737750197[38] = 0;
   out_3078776459737750197[39] = 0;
   out_3078776459737750197[40] = 0;
   out_3078776459737750197[41] = 0;
   out_3078776459737750197[42] = 0;
   out_3078776459737750197[43] = 0;
   out_3078776459737750197[44] = 0;
   out_3078776459737750197[45] = 0;
   out_3078776459737750197[46] = 0;
   out_3078776459737750197[47] = 0;
   out_3078776459737750197[48] = 1;
   out_3078776459737750197[49] = 0;
   out_3078776459737750197[50] = 0;
   out_3078776459737750197[51] = 0;
   out_3078776459737750197[52] = 0;
   out_3078776459737750197[53] = 0;
   out_3078776459737750197[54] = 0;
   out_3078776459737750197[55] = 0;
   out_3078776459737750197[56] = 0;
   out_3078776459737750197[57] = 0;
   out_3078776459737750197[58] = 0;
   out_3078776459737750197[59] = 0;
   out_3078776459737750197[60] = 1;
   out_3078776459737750197[61] = 0;
   out_3078776459737750197[62] = 0;
   out_3078776459737750197[63] = 0;
   out_3078776459737750197[64] = 0;
   out_3078776459737750197[65] = 0;
   out_3078776459737750197[66] = 0;
   out_3078776459737750197[67] = 0;
   out_3078776459737750197[68] = 0;
   out_3078776459737750197[69] = 0;
   out_3078776459737750197[70] = 0;
   out_3078776459737750197[71] = 0;
   out_3078776459737750197[72] = 1;
   out_3078776459737750197[73] = dt;
   out_3078776459737750197[74] = 0;
   out_3078776459737750197[75] = 0;
   out_3078776459737750197[76] = 0;
   out_3078776459737750197[77] = 0;
   out_3078776459737750197[78] = 0;
   out_3078776459737750197[79] = 0;
   out_3078776459737750197[80] = 0;
   out_3078776459737750197[81] = 0;
   out_3078776459737750197[82] = 0;
   out_3078776459737750197[83] = 0;
   out_3078776459737750197[84] = 1;
   out_3078776459737750197[85] = dt;
   out_3078776459737750197[86] = 0;
   out_3078776459737750197[87] = 0;
   out_3078776459737750197[88] = 0;
   out_3078776459737750197[89] = 0;
   out_3078776459737750197[90] = 0;
   out_3078776459737750197[91] = 0;
   out_3078776459737750197[92] = 0;
   out_3078776459737750197[93] = 0;
   out_3078776459737750197[94] = 0;
   out_3078776459737750197[95] = 0;
   out_3078776459737750197[96] = 1;
   out_3078776459737750197[97] = 0;
   out_3078776459737750197[98] = 0;
   out_3078776459737750197[99] = 0;
   out_3078776459737750197[100] = 0;
   out_3078776459737750197[101] = 0;
   out_3078776459737750197[102] = 0;
   out_3078776459737750197[103] = 0;
   out_3078776459737750197[104] = 0;
   out_3078776459737750197[105] = 0;
   out_3078776459737750197[106] = 0;
   out_3078776459737750197[107] = 0;
   out_3078776459737750197[108] = 1;
   out_3078776459737750197[109] = 0;
   out_3078776459737750197[110] = 0;
   out_3078776459737750197[111] = 0;
   out_3078776459737750197[112] = 0;
   out_3078776459737750197[113] = 0;
   out_3078776459737750197[114] = 0;
   out_3078776459737750197[115] = 0;
   out_3078776459737750197[116] = 0;
   out_3078776459737750197[117] = 0;
   out_3078776459737750197[118] = 0;
   out_3078776459737750197[119] = 0;
   out_3078776459737750197[120] = 1;
}
void h_6(double *state, double *sat_pos, double *out_901069036076917951) {
   out_901069036076917951[0] = sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2)) + state[6];
}
void H_6(double *state, double *sat_pos, double *out_3809735544314870023) {
   out_3809735544314870023[0] = (-sat_pos[0] + state[0])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_3809735544314870023[1] = (-sat_pos[1] + state[1])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_3809735544314870023[2] = (-sat_pos[2] + state[2])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_3809735544314870023[3] = 0;
   out_3809735544314870023[4] = 0;
   out_3809735544314870023[5] = 0;
   out_3809735544314870023[6] = 1;
   out_3809735544314870023[7] = 0;
   out_3809735544314870023[8] = 0;
   out_3809735544314870023[9] = 0;
   out_3809735544314870023[10] = 0;
}
void h_20(double *state, double *sat_pos, double *out_6206347775842541559) {
   out_6206347775842541559[0] = sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2)) + sat_pos[3]*state[10] + state[6] + state[9];
}
void H_20(double *state, double *sat_pos, double *out_762568504147176596) {
   out_762568504147176596[0] = (-sat_pos[0] + state[0])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_762568504147176596[1] = (-sat_pos[1] + state[1])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_762568504147176596[2] = (-sat_pos[2] + state[2])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_762568504147176596[3] = 0;
   out_762568504147176596[4] = 0;
   out_762568504147176596[5] = 0;
   out_762568504147176596[6] = 1;
   out_762568504147176596[7] = 0;
   out_762568504147176596[8] = 0;
   out_762568504147176596[9] = 1;
   out_762568504147176596[10] = sat_pos[3];
}
void h_7(double *state, double *sat_pos_vel, double *out_26779780329986471) {
   out_26779780329986471[0] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[3] - state[3])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[4] - state[4])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + (sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + state[7];
}
void H_7(double *state, double *sat_pos_vel, double *out_4581830375766098908) {
   out_4581830375766098908[0] = pow(sat_pos_vel[0] - state[0], 2)*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[0] - state[0])*(sat_pos_vel[1] - state[1])*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[0] - state[0])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[3] - state[3])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_4581830375766098908[1] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[1] - state[1])*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + pow(sat_pos_vel[1] - state[1], 2)*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[4] - state[4])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_4581830375766098908[2] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + pow(sat_pos_vel[2] - state[2], 2)*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[5] - state[5])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_4581830375766098908[3] = -(sat_pos_vel[0] - state[0])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_4581830375766098908[4] = -(sat_pos_vel[1] - state[1])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_4581830375766098908[5] = -(sat_pos_vel[2] - state[2])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_4581830375766098908[6] = 0;
   out_4581830375766098908[7] = 1;
   out_4581830375766098908[8] = 0;
   out_4581830375766098908[9] = 0;
   out_4581830375766098908[10] = 0;
}
void h_21(double *state, double *sat_pos_vel, double *out_26779780329986471) {
   out_26779780329986471[0] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[3] - state[3])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[4] - state[4])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + (sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + state[7];
}
void H_21(double *state, double *sat_pos_vel, double *out_4581830375766098908) {
   out_4581830375766098908[0] = pow(sat_pos_vel[0] - state[0], 2)*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[0] - state[0])*(sat_pos_vel[1] - state[1])*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[0] - state[0])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[3] - state[3])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_4581830375766098908[1] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[1] - state[1])*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + pow(sat_pos_vel[1] - state[1], 2)*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[4] - state[4])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_4581830375766098908[2] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + pow(sat_pos_vel[2] - state[2], 2)*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[5] - state[5])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_4581830375766098908[3] = -(sat_pos_vel[0] - state[0])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_4581830375766098908[4] = -(sat_pos_vel[1] - state[1])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_4581830375766098908[5] = -(sat_pos_vel[2] - state[2])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_4581830375766098908[6] = 0;
   out_4581830375766098908[7] = 1;
   out_4581830375766098908[8] = 0;
   out_4581830375766098908[9] = 0;
   out_4581830375766098908[10] = 0;
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
void gnss_err_fun(double *nom_x, double *delta_x, double *out_5196781054003887891) {
  err_fun(nom_x, delta_x, out_5196781054003887891);
}
void gnss_inv_err_fun(double *nom_x, double *true_x, double *out_817175628468433117) {
  inv_err_fun(nom_x, true_x, out_817175628468433117);
}
void gnss_H_mod_fun(double *state, double *out_6506367600169501482) {
  H_mod_fun(state, out_6506367600169501482);
}
void gnss_f_fun(double *state, double dt, double *out_4633542785125246216) {
  f_fun(state,  dt, out_4633542785125246216);
}
void gnss_F_fun(double *state, double dt, double *out_3078776459737750197) {
  F_fun(state,  dt, out_3078776459737750197);
}
void gnss_h_6(double *state, double *sat_pos, double *out_901069036076917951) {
  h_6(state, sat_pos, out_901069036076917951);
}
void gnss_H_6(double *state, double *sat_pos, double *out_3809735544314870023) {
  H_6(state, sat_pos, out_3809735544314870023);
}
void gnss_h_20(double *state, double *sat_pos, double *out_6206347775842541559) {
  h_20(state, sat_pos, out_6206347775842541559);
}
void gnss_H_20(double *state, double *sat_pos, double *out_762568504147176596) {
  H_20(state, sat_pos, out_762568504147176596);
}
void gnss_h_7(double *state, double *sat_pos_vel, double *out_26779780329986471) {
  h_7(state, sat_pos_vel, out_26779780329986471);
}
void gnss_H_7(double *state, double *sat_pos_vel, double *out_4581830375766098908) {
  H_7(state, sat_pos_vel, out_4581830375766098908);
}
void gnss_h_21(double *state, double *sat_pos_vel, double *out_26779780329986471) {
  h_21(state, sat_pos_vel, out_26779780329986471);
}
void gnss_H_21(double *state, double *sat_pos_vel, double *out_4581830375766098908) {
  H_21(state, sat_pos_vel, out_4581830375766098908);
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
