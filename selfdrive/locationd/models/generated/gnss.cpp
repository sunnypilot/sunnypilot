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
void err_fun(double *nom_x, double *delta_x, double *out_3708978687379214111) {
   out_3708978687379214111[0] = delta_x[0] + nom_x[0];
   out_3708978687379214111[1] = delta_x[1] + nom_x[1];
   out_3708978687379214111[2] = delta_x[2] + nom_x[2];
   out_3708978687379214111[3] = delta_x[3] + nom_x[3];
   out_3708978687379214111[4] = delta_x[4] + nom_x[4];
   out_3708978687379214111[5] = delta_x[5] + nom_x[5];
   out_3708978687379214111[6] = delta_x[6] + nom_x[6];
   out_3708978687379214111[7] = delta_x[7] + nom_x[7];
   out_3708978687379214111[8] = delta_x[8] + nom_x[8];
   out_3708978687379214111[9] = delta_x[9] + nom_x[9];
   out_3708978687379214111[10] = delta_x[10] + nom_x[10];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_2153812957683424211) {
   out_2153812957683424211[0] = -nom_x[0] + true_x[0];
   out_2153812957683424211[1] = -nom_x[1] + true_x[1];
   out_2153812957683424211[2] = -nom_x[2] + true_x[2];
   out_2153812957683424211[3] = -nom_x[3] + true_x[3];
   out_2153812957683424211[4] = -nom_x[4] + true_x[4];
   out_2153812957683424211[5] = -nom_x[5] + true_x[5];
   out_2153812957683424211[6] = -nom_x[6] + true_x[6];
   out_2153812957683424211[7] = -nom_x[7] + true_x[7];
   out_2153812957683424211[8] = -nom_x[8] + true_x[8];
   out_2153812957683424211[9] = -nom_x[9] + true_x[9];
   out_2153812957683424211[10] = -nom_x[10] + true_x[10];
}
void H_mod_fun(double *state, double *out_4628416537597784978) {
   out_4628416537597784978[0] = 1.0;
   out_4628416537597784978[1] = 0;
   out_4628416537597784978[2] = 0;
   out_4628416537597784978[3] = 0;
   out_4628416537597784978[4] = 0;
   out_4628416537597784978[5] = 0;
   out_4628416537597784978[6] = 0;
   out_4628416537597784978[7] = 0;
   out_4628416537597784978[8] = 0;
   out_4628416537597784978[9] = 0;
   out_4628416537597784978[10] = 0;
   out_4628416537597784978[11] = 0;
   out_4628416537597784978[12] = 1.0;
   out_4628416537597784978[13] = 0;
   out_4628416537597784978[14] = 0;
   out_4628416537597784978[15] = 0;
   out_4628416537597784978[16] = 0;
   out_4628416537597784978[17] = 0;
   out_4628416537597784978[18] = 0;
   out_4628416537597784978[19] = 0;
   out_4628416537597784978[20] = 0;
   out_4628416537597784978[21] = 0;
   out_4628416537597784978[22] = 0;
   out_4628416537597784978[23] = 0;
   out_4628416537597784978[24] = 1.0;
   out_4628416537597784978[25] = 0;
   out_4628416537597784978[26] = 0;
   out_4628416537597784978[27] = 0;
   out_4628416537597784978[28] = 0;
   out_4628416537597784978[29] = 0;
   out_4628416537597784978[30] = 0;
   out_4628416537597784978[31] = 0;
   out_4628416537597784978[32] = 0;
   out_4628416537597784978[33] = 0;
   out_4628416537597784978[34] = 0;
   out_4628416537597784978[35] = 0;
   out_4628416537597784978[36] = 1.0;
   out_4628416537597784978[37] = 0;
   out_4628416537597784978[38] = 0;
   out_4628416537597784978[39] = 0;
   out_4628416537597784978[40] = 0;
   out_4628416537597784978[41] = 0;
   out_4628416537597784978[42] = 0;
   out_4628416537597784978[43] = 0;
   out_4628416537597784978[44] = 0;
   out_4628416537597784978[45] = 0;
   out_4628416537597784978[46] = 0;
   out_4628416537597784978[47] = 0;
   out_4628416537597784978[48] = 1.0;
   out_4628416537597784978[49] = 0;
   out_4628416537597784978[50] = 0;
   out_4628416537597784978[51] = 0;
   out_4628416537597784978[52] = 0;
   out_4628416537597784978[53] = 0;
   out_4628416537597784978[54] = 0;
   out_4628416537597784978[55] = 0;
   out_4628416537597784978[56] = 0;
   out_4628416537597784978[57] = 0;
   out_4628416537597784978[58] = 0;
   out_4628416537597784978[59] = 0;
   out_4628416537597784978[60] = 1.0;
   out_4628416537597784978[61] = 0;
   out_4628416537597784978[62] = 0;
   out_4628416537597784978[63] = 0;
   out_4628416537597784978[64] = 0;
   out_4628416537597784978[65] = 0;
   out_4628416537597784978[66] = 0;
   out_4628416537597784978[67] = 0;
   out_4628416537597784978[68] = 0;
   out_4628416537597784978[69] = 0;
   out_4628416537597784978[70] = 0;
   out_4628416537597784978[71] = 0;
   out_4628416537597784978[72] = 1.0;
   out_4628416537597784978[73] = 0;
   out_4628416537597784978[74] = 0;
   out_4628416537597784978[75] = 0;
   out_4628416537597784978[76] = 0;
   out_4628416537597784978[77] = 0;
   out_4628416537597784978[78] = 0;
   out_4628416537597784978[79] = 0;
   out_4628416537597784978[80] = 0;
   out_4628416537597784978[81] = 0;
   out_4628416537597784978[82] = 0;
   out_4628416537597784978[83] = 0;
   out_4628416537597784978[84] = 1.0;
   out_4628416537597784978[85] = 0;
   out_4628416537597784978[86] = 0;
   out_4628416537597784978[87] = 0;
   out_4628416537597784978[88] = 0;
   out_4628416537597784978[89] = 0;
   out_4628416537597784978[90] = 0;
   out_4628416537597784978[91] = 0;
   out_4628416537597784978[92] = 0;
   out_4628416537597784978[93] = 0;
   out_4628416537597784978[94] = 0;
   out_4628416537597784978[95] = 0;
   out_4628416537597784978[96] = 1.0;
   out_4628416537597784978[97] = 0;
   out_4628416537597784978[98] = 0;
   out_4628416537597784978[99] = 0;
   out_4628416537597784978[100] = 0;
   out_4628416537597784978[101] = 0;
   out_4628416537597784978[102] = 0;
   out_4628416537597784978[103] = 0;
   out_4628416537597784978[104] = 0;
   out_4628416537597784978[105] = 0;
   out_4628416537597784978[106] = 0;
   out_4628416537597784978[107] = 0;
   out_4628416537597784978[108] = 1.0;
   out_4628416537597784978[109] = 0;
   out_4628416537597784978[110] = 0;
   out_4628416537597784978[111] = 0;
   out_4628416537597784978[112] = 0;
   out_4628416537597784978[113] = 0;
   out_4628416537597784978[114] = 0;
   out_4628416537597784978[115] = 0;
   out_4628416537597784978[116] = 0;
   out_4628416537597784978[117] = 0;
   out_4628416537597784978[118] = 0;
   out_4628416537597784978[119] = 0;
   out_4628416537597784978[120] = 1.0;
}
void f_fun(double *state, double dt, double *out_7298165946464525334) {
   out_7298165946464525334[0] = dt*state[3] + state[0];
   out_7298165946464525334[1] = dt*state[4] + state[1];
   out_7298165946464525334[2] = dt*state[5] + state[2];
   out_7298165946464525334[3] = state[3];
   out_7298165946464525334[4] = state[4];
   out_7298165946464525334[5] = state[5];
   out_7298165946464525334[6] = dt*state[7] + state[6];
   out_7298165946464525334[7] = dt*state[8] + state[7];
   out_7298165946464525334[8] = state[8];
   out_7298165946464525334[9] = state[9];
   out_7298165946464525334[10] = state[10];
}
void F_fun(double *state, double dt, double *out_7533698438399796741) {
   out_7533698438399796741[0] = 1;
   out_7533698438399796741[1] = 0;
   out_7533698438399796741[2] = 0;
   out_7533698438399796741[3] = dt;
   out_7533698438399796741[4] = 0;
   out_7533698438399796741[5] = 0;
   out_7533698438399796741[6] = 0;
   out_7533698438399796741[7] = 0;
   out_7533698438399796741[8] = 0;
   out_7533698438399796741[9] = 0;
   out_7533698438399796741[10] = 0;
   out_7533698438399796741[11] = 0;
   out_7533698438399796741[12] = 1;
   out_7533698438399796741[13] = 0;
   out_7533698438399796741[14] = 0;
   out_7533698438399796741[15] = dt;
   out_7533698438399796741[16] = 0;
   out_7533698438399796741[17] = 0;
   out_7533698438399796741[18] = 0;
   out_7533698438399796741[19] = 0;
   out_7533698438399796741[20] = 0;
   out_7533698438399796741[21] = 0;
   out_7533698438399796741[22] = 0;
   out_7533698438399796741[23] = 0;
   out_7533698438399796741[24] = 1;
   out_7533698438399796741[25] = 0;
   out_7533698438399796741[26] = 0;
   out_7533698438399796741[27] = dt;
   out_7533698438399796741[28] = 0;
   out_7533698438399796741[29] = 0;
   out_7533698438399796741[30] = 0;
   out_7533698438399796741[31] = 0;
   out_7533698438399796741[32] = 0;
   out_7533698438399796741[33] = 0;
   out_7533698438399796741[34] = 0;
   out_7533698438399796741[35] = 0;
   out_7533698438399796741[36] = 1;
   out_7533698438399796741[37] = 0;
   out_7533698438399796741[38] = 0;
   out_7533698438399796741[39] = 0;
   out_7533698438399796741[40] = 0;
   out_7533698438399796741[41] = 0;
   out_7533698438399796741[42] = 0;
   out_7533698438399796741[43] = 0;
   out_7533698438399796741[44] = 0;
   out_7533698438399796741[45] = 0;
   out_7533698438399796741[46] = 0;
   out_7533698438399796741[47] = 0;
   out_7533698438399796741[48] = 1;
   out_7533698438399796741[49] = 0;
   out_7533698438399796741[50] = 0;
   out_7533698438399796741[51] = 0;
   out_7533698438399796741[52] = 0;
   out_7533698438399796741[53] = 0;
   out_7533698438399796741[54] = 0;
   out_7533698438399796741[55] = 0;
   out_7533698438399796741[56] = 0;
   out_7533698438399796741[57] = 0;
   out_7533698438399796741[58] = 0;
   out_7533698438399796741[59] = 0;
   out_7533698438399796741[60] = 1;
   out_7533698438399796741[61] = 0;
   out_7533698438399796741[62] = 0;
   out_7533698438399796741[63] = 0;
   out_7533698438399796741[64] = 0;
   out_7533698438399796741[65] = 0;
   out_7533698438399796741[66] = 0;
   out_7533698438399796741[67] = 0;
   out_7533698438399796741[68] = 0;
   out_7533698438399796741[69] = 0;
   out_7533698438399796741[70] = 0;
   out_7533698438399796741[71] = 0;
   out_7533698438399796741[72] = 1;
   out_7533698438399796741[73] = dt;
   out_7533698438399796741[74] = 0;
   out_7533698438399796741[75] = 0;
   out_7533698438399796741[76] = 0;
   out_7533698438399796741[77] = 0;
   out_7533698438399796741[78] = 0;
   out_7533698438399796741[79] = 0;
   out_7533698438399796741[80] = 0;
   out_7533698438399796741[81] = 0;
   out_7533698438399796741[82] = 0;
   out_7533698438399796741[83] = 0;
   out_7533698438399796741[84] = 1;
   out_7533698438399796741[85] = dt;
   out_7533698438399796741[86] = 0;
   out_7533698438399796741[87] = 0;
   out_7533698438399796741[88] = 0;
   out_7533698438399796741[89] = 0;
   out_7533698438399796741[90] = 0;
   out_7533698438399796741[91] = 0;
   out_7533698438399796741[92] = 0;
   out_7533698438399796741[93] = 0;
   out_7533698438399796741[94] = 0;
   out_7533698438399796741[95] = 0;
   out_7533698438399796741[96] = 1;
   out_7533698438399796741[97] = 0;
   out_7533698438399796741[98] = 0;
   out_7533698438399796741[99] = 0;
   out_7533698438399796741[100] = 0;
   out_7533698438399796741[101] = 0;
   out_7533698438399796741[102] = 0;
   out_7533698438399796741[103] = 0;
   out_7533698438399796741[104] = 0;
   out_7533698438399796741[105] = 0;
   out_7533698438399796741[106] = 0;
   out_7533698438399796741[107] = 0;
   out_7533698438399796741[108] = 1;
   out_7533698438399796741[109] = 0;
   out_7533698438399796741[110] = 0;
   out_7533698438399796741[111] = 0;
   out_7533698438399796741[112] = 0;
   out_7533698438399796741[113] = 0;
   out_7533698438399796741[114] = 0;
   out_7533698438399796741[115] = 0;
   out_7533698438399796741[116] = 0;
   out_7533698438399796741[117] = 0;
   out_7533698438399796741[118] = 0;
   out_7533698438399796741[119] = 0;
   out_7533698438399796741[120] = 1;
}
void h_6(double *state, double *sat_pos, double *out_7098435553514511068) {
   out_7098435553514511068[0] = sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2)) + state[6];
}
void H_6(double *state, double *sat_pos, double *out_279244630454215938) {
   out_279244630454215938[0] = (-sat_pos[0] + state[0])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_279244630454215938[1] = (-sat_pos[1] + state[1])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_279244630454215938[2] = (-sat_pos[2] + state[2])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_279244630454215938[3] = 0;
   out_279244630454215938[4] = 0;
   out_279244630454215938[5] = 0;
   out_279244630454215938[6] = 1;
   out_279244630454215938[7] = 0;
   out_279244630454215938[8] = 0;
   out_279244630454215938[9] = 0;
   out_279244630454215938[10] = 0;
}
void h_20(double *state, double *sat_pos, double *out_4723154202215786973) {
   out_4723154202215786973[0] = sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2)) + sat_pos[3]*state[10] + state[6] + state[9];
}
void H_20(double *state, double *sat_pos, double *out_7530708677883952507) {
   out_7530708677883952507[0] = (-sat_pos[0] + state[0])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_7530708677883952507[1] = (-sat_pos[1] + state[1])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_7530708677883952507[2] = (-sat_pos[2] + state[2])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_7530708677883952507[3] = 0;
   out_7530708677883952507[4] = 0;
   out_7530708677883952507[5] = 0;
   out_7530708677883952507[6] = 1;
   out_7530708677883952507[7] = 0;
   out_7530708677883952507[8] = 0;
   out_7530708677883952507[9] = 1;
   out_7530708677883952507[10] = sat_pos[3];
}
void h_7(double *state, double *sat_pos_vel, double *out_7180798933054063665) {
   out_7180798933054063665[0] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[3] - state[3])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[4] - state[4])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + (sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + state[7];
}
void H_7(double *state, double *sat_pos_vel, double *out_6334088002612665567) {
   out_6334088002612665567[0] = pow(sat_pos_vel[0] - state[0], 2)*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[0] - state[0])*(sat_pos_vel[1] - state[1])*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[0] - state[0])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[3] - state[3])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_6334088002612665567[1] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[1] - state[1])*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + pow(sat_pos_vel[1] - state[1], 2)*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[4] - state[4])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_6334088002612665567[2] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + pow(sat_pos_vel[2] - state[2], 2)*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[5] - state[5])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_6334088002612665567[3] = -(sat_pos_vel[0] - state[0])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_6334088002612665567[4] = -(sat_pos_vel[1] - state[1])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_6334088002612665567[5] = -(sat_pos_vel[2] - state[2])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_6334088002612665567[6] = 0;
   out_6334088002612665567[7] = 1;
   out_6334088002612665567[8] = 0;
   out_6334088002612665567[9] = 0;
   out_6334088002612665567[10] = 0;
}
void h_21(double *state, double *sat_pos_vel, double *out_7180798933054063665) {
   out_7180798933054063665[0] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[3] - state[3])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[4] - state[4])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + (sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + state[7];
}
void H_21(double *state, double *sat_pos_vel, double *out_6334088002612665567) {
   out_6334088002612665567[0] = pow(sat_pos_vel[0] - state[0], 2)*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[0] - state[0])*(sat_pos_vel[1] - state[1])*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[0] - state[0])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[3] - state[3])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_6334088002612665567[1] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[1] - state[1])*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + pow(sat_pos_vel[1] - state[1], 2)*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[4] - state[4])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_6334088002612665567[2] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + pow(sat_pos_vel[2] - state[2], 2)*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[5] - state[5])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_6334088002612665567[3] = -(sat_pos_vel[0] - state[0])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_6334088002612665567[4] = -(sat_pos_vel[1] - state[1])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_6334088002612665567[5] = -(sat_pos_vel[2] - state[2])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_6334088002612665567[6] = 0;
   out_6334088002612665567[7] = 1;
   out_6334088002612665567[8] = 0;
   out_6334088002612665567[9] = 0;
   out_6334088002612665567[10] = 0;
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
void gnss_err_fun(double *nom_x, double *delta_x, double *out_3708978687379214111) {
  err_fun(nom_x, delta_x, out_3708978687379214111);
}
void gnss_inv_err_fun(double *nom_x, double *true_x, double *out_2153812957683424211) {
  inv_err_fun(nom_x, true_x, out_2153812957683424211);
}
void gnss_H_mod_fun(double *state, double *out_4628416537597784978) {
  H_mod_fun(state, out_4628416537597784978);
}
void gnss_f_fun(double *state, double dt, double *out_7298165946464525334) {
  f_fun(state,  dt, out_7298165946464525334);
}
void gnss_F_fun(double *state, double dt, double *out_7533698438399796741) {
  F_fun(state,  dt, out_7533698438399796741);
}
void gnss_h_6(double *state, double *sat_pos, double *out_7098435553514511068) {
  h_6(state, sat_pos, out_7098435553514511068);
}
void gnss_H_6(double *state, double *sat_pos, double *out_279244630454215938) {
  H_6(state, sat_pos, out_279244630454215938);
}
void gnss_h_20(double *state, double *sat_pos, double *out_4723154202215786973) {
  h_20(state, sat_pos, out_4723154202215786973);
}
void gnss_H_20(double *state, double *sat_pos, double *out_7530708677883952507) {
  H_20(state, sat_pos, out_7530708677883952507);
}
void gnss_h_7(double *state, double *sat_pos_vel, double *out_7180798933054063665) {
  h_7(state, sat_pos_vel, out_7180798933054063665);
}
void gnss_H_7(double *state, double *sat_pos_vel, double *out_6334088002612665567) {
  H_7(state, sat_pos_vel, out_6334088002612665567);
}
void gnss_h_21(double *state, double *sat_pos_vel, double *out_7180798933054063665) {
  h_21(state, sat_pos_vel, out_7180798933054063665);
}
void gnss_H_21(double *state, double *sat_pos_vel, double *out_6334088002612665567) {
  H_21(state, sat_pos_vel, out_6334088002612665567);
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
