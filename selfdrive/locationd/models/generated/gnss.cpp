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
void err_fun(double *nom_x, double *delta_x, double *out_8052698219636447439) {
   out_8052698219636447439[0] = delta_x[0] + nom_x[0];
   out_8052698219636447439[1] = delta_x[1] + nom_x[1];
   out_8052698219636447439[2] = delta_x[2] + nom_x[2];
   out_8052698219636447439[3] = delta_x[3] + nom_x[3];
   out_8052698219636447439[4] = delta_x[4] + nom_x[4];
   out_8052698219636447439[5] = delta_x[5] + nom_x[5];
   out_8052698219636447439[6] = delta_x[6] + nom_x[6];
   out_8052698219636447439[7] = delta_x[7] + nom_x[7];
   out_8052698219636447439[8] = delta_x[8] + nom_x[8];
   out_8052698219636447439[9] = delta_x[9] + nom_x[9];
   out_8052698219636447439[10] = delta_x[10] + nom_x[10];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_414007979716982857) {
   out_414007979716982857[0] = -nom_x[0] + true_x[0];
   out_414007979716982857[1] = -nom_x[1] + true_x[1];
   out_414007979716982857[2] = -nom_x[2] + true_x[2];
   out_414007979716982857[3] = -nom_x[3] + true_x[3];
   out_414007979716982857[4] = -nom_x[4] + true_x[4];
   out_414007979716982857[5] = -nom_x[5] + true_x[5];
   out_414007979716982857[6] = -nom_x[6] + true_x[6];
   out_414007979716982857[7] = -nom_x[7] + true_x[7];
   out_414007979716982857[8] = -nom_x[8] + true_x[8];
   out_414007979716982857[9] = -nom_x[9] + true_x[9];
   out_414007979716982857[10] = -nom_x[10] + true_x[10];
}
void H_mod_fun(double *state, double *out_1658508881837957111) {
   out_1658508881837957111[0] = 1.0;
   out_1658508881837957111[1] = 0;
   out_1658508881837957111[2] = 0;
   out_1658508881837957111[3] = 0;
   out_1658508881837957111[4] = 0;
   out_1658508881837957111[5] = 0;
   out_1658508881837957111[6] = 0;
   out_1658508881837957111[7] = 0;
   out_1658508881837957111[8] = 0;
   out_1658508881837957111[9] = 0;
   out_1658508881837957111[10] = 0;
   out_1658508881837957111[11] = 0;
   out_1658508881837957111[12] = 1.0;
   out_1658508881837957111[13] = 0;
   out_1658508881837957111[14] = 0;
   out_1658508881837957111[15] = 0;
   out_1658508881837957111[16] = 0;
   out_1658508881837957111[17] = 0;
   out_1658508881837957111[18] = 0;
   out_1658508881837957111[19] = 0;
   out_1658508881837957111[20] = 0;
   out_1658508881837957111[21] = 0;
   out_1658508881837957111[22] = 0;
   out_1658508881837957111[23] = 0;
   out_1658508881837957111[24] = 1.0;
   out_1658508881837957111[25] = 0;
   out_1658508881837957111[26] = 0;
   out_1658508881837957111[27] = 0;
   out_1658508881837957111[28] = 0;
   out_1658508881837957111[29] = 0;
   out_1658508881837957111[30] = 0;
   out_1658508881837957111[31] = 0;
   out_1658508881837957111[32] = 0;
   out_1658508881837957111[33] = 0;
   out_1658508881837957111[34] = 0;
   out_1658508881837957111[35] = 0;
   out_1658508881837957111[36] = 1.0;
   out_1658508881837957111[37] = 0;
   out_1658508881837957111[38] = 0;
   out_1658508881837957111[39] = 0;
   out_1658508881837957111[40] = 0;
   out_1658508881837957111[41] = 0;
   out_1658508881837957111[42] = 0;
   out_1658508881837957111[43] = 0;
   out_1658508881837957111[44] = 0;
   out_1658508881837957111[45] = 0;
   out_1658508881837957111[46] = 0;
   out_1658508881837957111[47] = 0;
   out_1658508881837957111[48] = 1.0;
   out_1658508881837957111[49] = 0;
   out_1658508881837957111[50] = 0;
   out_1658508881837957111[51] = 0;
   out_1658508881837957111[52] = 0;
   out_1658508881837957111[53] = 0;
   out_1658508881837957111[54] = 0;
   out_1658508881837957111[55] = 0;
   out_1658508881837957111[56] = 0;
   out_1658508881837957111[57] = 0;
   out_1658508881837957111[58] = 0;
   out_1658508881837957111[59] = 0;
   out_1658508881837957111[60] = 1.0;
   out_1658508881837957111[61] = 0;
   out_1658508881837957111[62] = 0;
   out_1658508881837957111[63] = 0;
   out_1658508881837957111[64] = 0;
   out_1658508881837957111[65] = 0;
   out_1658508881837957111[66] = 0;
   out_1658508881837957111[67] = 0;
   out_1658508881837957111[68] = 0;
   out_1658508881837957111[69] = 0;
   out_1658508881837957111[70] = 0;
   out_1658508881837957111[71] = 0;
   out_1658508881837957111[72] = 1.0;
   out_1658508881837957111[73] = 0;
   out_1658508881837957111[74] = 0;
   out_1658508881837957111[75] = 0;
   out_1658508881837957111[76] = 0;
   out_1658508881837957111[77] = 0;
   out_1658508881837957111[78] = 0;
   out_1658508881837957111[79] = 0;
   out_1658508881837957111[80] = 0;
   out_1658508881837957111[81] = 0;
   out_1658508881837957111[82] = 0;
   out_1658508881837957111[83] = 0;
   out_1658508881837957111[84] = 1.0;
   out_1658508881837957111[85] = 0;
   out_1658508881837957111[86] = 0;
   out_1658508881837957111[87] = 0;
   out_1658508881837957111[88] = 0;
   out_1658508881837957111[89] = 0;
   out_1658508881837957111[90] = 0;
   out_1658508881837957111[91] = 0;
   out_1658508881837957111[92] = 0;
   out_1658508881837957111[93] = 0;
   out_1658508881837957111[94] = 0;
   out_1658508881837957111[95] = 0;
   out_1658508881837957111[96] = 1.0;
   out_1658508881837957111[97] = 0;
   out_1658508881837957111[98] = 0;
   out_1658508881837957111[99] = 0;
   out_1658508881837957111[100] = 0;
   out_1658508881837957111[101] = 0;
   out_1658508881837957111[102] = 0;
   out_1658508881837957111[103] = 0;
   out_1658508881837957111[104] = 0;
   out_1658508881837957111[105] = 0;
   out_1658508881837957111[106] = 0;
   out_1658508881837957111[107] = 0;
   out_1658508881837957111[108] = 1.0;
   out_1658508881837957111[109] = 0;
   out_1658508881837957111[110] = 0;
   out_1658508881837957111[111] = 0;
   out_1658508881837957111[112] = 0;
   out_1658508881837957111[113] = 0;
   out_1658508881837957111[114] = 0;
   out_1658508881837957111[115] = 0;
   out_1658508881837957111[116] = 0;
   out_1658508881837957111[117] = 0;
   out_1658508881837957111[118] = 0;
   out_1658508881837957111[119] = 0;
   out_1658508881837957111[120] = 1.0;
}
void f_fun(double *state, double dt, double *out_2765158645351032639) {
   out_2765158645351032639[0] = dt*state[3] + state[0];
   out_2765158645351032639[1] = dt*state[4] + state[1];
   out_2765158645351032639[2] = dt*state[5] + state[2];
   out_2765158645351032639[3] = state[3];
   out_2765158645351032639[4] = state[4];
   out_2765158645351032639[5] = state[5];
   out_2765158645351032639[6] = dt*state[7] + state[6];
   out_2765158645351032639[7] = dt*state[8] + state[7];
   out_2765158645351032639[8] = state[8];
   out_2765158645351032639[9] = state[9];
   out_2765158645351032639[10] = state[10];
}
void F_fun(double *state, double dt, double *out_3889898511770947762) {
   out_3889898511770947762[0] = 1;
   out_3889898511770947762[1] = 0;
   out_3889898511770947762[2] = 0;
   out_3889898511770947762[3] = dt;
   out_3889898511770947762[4] = 0;
   out_3889898511770947762[5] = 0;
   out_3889898511770947762[6] = 0;
   out_3889898511770947762[7] = 0;
   out_3889898511770947762[8] = 0;
   out_3889898511770947762[9] = 0;
   out_3889898511770947762[10] = 0;
   out_3889898511770947762[11] = 0;
   out_3889898511770947762[12] = 1;
   out_3889898511770947762[13] = 0;
   out_3889898511770947762[14] = 0;
   out_3889898511770947762[15] = dt;
   out_3889898511770947762[16] = 0;
   out_3889898511770947762[17] = 0;
   out_3889898511770947762[18] = 0;
   out_3889898511770947762[19] = 0;
   out_3889898511770947762[20] = 0;
   out_3889898511770947762[21] = 0;
   out_3889898511770947762[22] = 0;
   out_3889898511770947762[23] = 0;
   out_3889898511770947762[24] = 1;
   out_3889898511770947762[25] = 0;
   out_3889898511770947762[26] = 0;
   out_3889898511770947762[27] = dt;
   out_3889898511770947762[28] = 0;
   out_3889898511770947762[29] = 0;
   out_3889898511770947762[30] = 0;
   out_3889898511770947762[31] = 0;
   out_3889898511770947762[32] = 0;
   out_3889898511770947762[33] = 0;
   out_3889898511770947762[34] = 0;
   out_3889898511770947762[35] = 0;
   out_3889898511770947762[36] = 1;
   out_3889898511770947762[37] = 0;
   out_3889898511770947762[38] = 0;
   out_3889898511770947762[39] = 0;
   out_3889898511770947762[40] = 0;
   out_3889898511770947762[41] = 0;
   out_3889898511770947762[42] = 0;
   out_3889898511770947762[43] = 0;
   out_3889898511770947762[44] = 0;
   out_3889898511770947762[45] = 0;
   out_3889898511770947762[46] = 0;
   out_3889898511770947762[47] = 0;
   out_3889898511770947762[48] = 1;
   out_3889898511770947762[49] = 0;
   out_3889898511770947762[50] = 0;
   out_3889898511770947762[51] = 0;
   out_3889898511770947762[52] = 0;
   out_3889898511770947762[53] = 0;
   out_3889898511770947762[54] = 0;
   out_3889898511770947762[55] = 0;
   out_3889898511770947762[56] = 0;
   out_3889898511770947762[57] = 0;
   out_3889898511770947762[58] = 0;
   out_3889898511770947762[59] = 0;
   out_3889898511770947762[60] = 1;
   out_3889898511770947762[61] = 0;
   out_3889898511770947762[62] = 0;
   out_3889898511770947762[63] = 0;
   out_3889898511770947762[64] = 0;
   out_3889898511770947762[65] = 0;
   out_3889898511770947762[66] = 0;
   out_3889898511770947762[67] = 0;
   out_3889898511770947762[68] = 0;
   out_3889898511770947762[69] = 0;
   out_3889898511770947762[70] = 0;
   out_3889898511770947762[71] = 0;
   out_3889898511770947762[72] = 1;
   out_3889898511770947762[73] = dt;
   out_3889898511770947762[74] = 0;
   out_3889898511770947762[75] = 0;
   out_3889898511770947762[76] = 0;
   out_3889898511770947762[77] = 0;
   out_3889898511770947762[78] = 0;
   out_3889898511770947762[79] = 0;
   out_3889898511770947762[80] = 0;
   out_3889898511770947762[81] = 0;
   out_3889898511770947762[82] = 0;
   out_3889898511770947762[83] = 0;
   out_3889898511770947762[84] = 1;
   out_3889898511770947762[85] = dt;
   out_3889898511770947762[86] = 0;
   out_3889898511770947762[87] = 0;
   out_3889898511770947762[88] = 0;
   out_3889898511770947762[89] = 0;
   out_3889898511770947762[90] = 0;
   out_3889898511770947762[91] = 0;
   out_3889898511770947762[92] = 0;
   out_3889898511770947762[93] = 0;
   out_3889898511770947762[94] = 0;
   out_3889898511770947762[95] = 0;
   out_3889898511770947762[96] = 1;
   out_3889898511770947762[97] = 0;
   out_3889898511770947762[98] = 0;
   out_3889898511770947762[99] = 0;
   out_3889898511770947762[100] = 0;
   out_3889898511770947762[101] = 0;
   out_3889898511770947762[102] = 0;
   out_3889898511770947762[103] = 0;
   out_3889898511770947762[104] = 0;
   out_3889898511770947762[105] = 0;
   out_3889898511770947762[106] = 0;
   out_3889898511770947762[107] = 0;
   out_3889898511770947762[108] = 1;
   out_3889898511770947762[109] = 0;
   out_3889898511770947762[110] = 0;
   out_3889898511770947762[111] = 0;
   out_3889898511770947762[112] = 0;
   out_3889898511770947762[113] = 0;
   out_3889898511770947762[114] = 0;
   out_3889898511770947762[115] = 0;
   out_3889898511770947762[116] = 0;
   out_3889898511770947762[117] = 0;
   out_3889898511770947762[118] = 0;
   out_3889898511770947762[119] = 0;
   out_3889898511770947762[120] = 1;
}
void h_6(double *state, double *sat_pos, double *out_3151616376493060002) {
   out_3151616376493060002[0] = sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2)) + state[6];
}
void H_6(double *state, double *sat_pos, double *out_8521601814755962792) {
   out_8521601814755962792[0] = (-sat_pos[0] + state[0])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_8521601814755962792[1] = (-sat_pos[1] + state[1])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_8521601814755962792[2] = (-sat_pos[2] + state[2])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_8521601814755962792[3] = 0;
   out_8521601814755962792[4] = 0;
   out_8521601814755962792[5] = 0;
   out_8521601814755962792[6] = 1;
   out_8521601814755962792[7] = 0;
   out_8521601814755962792[8] = 0;
   out_8521601814755962792[9] = 0;
   out_8521601814755962792[10] = 0;
}
void h_20(double *state, double *sat_pos, double *out_1001695644916733854) {
   out_1001695644916733854[0] = sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2)) + sat_pos[3]*state[10] + state[6] + state[9];
}
void H_20(double *state, double *sat_pos, double *out_3587922318809976588) {
   out_3587922318809976588[0] = (-sat_pos[0] + state[0])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_3587922318809976588[1] = (-sat_pos[1] + state[1])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_3587922318809976588[2] = (-sat_pos[2] + state[2])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_3587922318809976588[3] = 0;
   out_3587922318809976588[4] = 0;
   out_3587922318809976588[5] = 0;
   out_3587922318809976588[6] = 1;
   out_3587922318809976588[7] = 0;
   out_3587922318809976588[8] = 0;
   out_3587922318809976588[9] = 1;
   out_3587922318809976588[10] = sat_pos[3];
}
void h_7(double *state, double *sat_pos_vel, double *out_1581577151931372281) {
   out_1581577151931372281[0] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[3] - state[3])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[4] - state[4])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + (sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + state[7];
}
void H_7(double *state, double *sat_pos_vel, double *out_8392593010464093728) {
   out_8392593010464093728[0] = pow(sat_pos_vel[0] - state[0], 2)*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[0] - state[0])*(sat_pos_vel[1] - state[1])*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[0] - state[0])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[3] - state[3])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_8392593010464093728[1] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[1] - state[1])*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + pow(sat_pos_vel[1] - state[1], 2)*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[4] - state[4])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_8392593010464093728[2] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + pow(sat_pos_vel[2] - state[2], 2)*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[5] - state[5])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_8392593010464093728[3] = -(sat_pos_vel[0] - state[0])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_8392593010464093728[4] = -(sat_pos_vel[1] - state[1])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_8392593010464093728[5] = -(sat_pos_vel[2] - state[2])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_8392593010464093728[6] = 0;
   out_8392593010464093728[7] = 1;
   out_8392593010464093728[8] = 0;
   out_8392593010464093728[9] = 0;
   out_8392593010464093728[10] = 0;
}
void h_21(double *state, double *sat_pos_vel, double *out_1581577151931372281) {
   out_1581577151931372281[0] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[3] - state[3])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[4] - state[4])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + (sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + state[7];
}
void H_21(double *state, double *sat_pos_vel, double *out_8392593010464093728) {
   out_8392593010464093728[0] = pow(sat_pos_vel[0] - state[0], 2)*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[0] - state[0])*(sat_pos_vel[1] - state[1])*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[0] - state[0])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[3] - state[3])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_8392593010464093728[1] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[1] - state[1])*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + pow(sat_pos_vel[1] - state[1], 2)*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[4] - state[4])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_8392593010464093728[2] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + pow(sat_pos_vel[2] - state[2], 2)*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[5] - state[5])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_8392593010464093728[3] = -(sat_pos_vel[0] - state[0])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_8392593010464093728[4] = -(sat_pos_vel[1] - state[1])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_8392593010464093728[5] = -(sat_pos_vel[2] - state[2])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_8392593010464093728[6] = 0;
   out_8392593010464093728[7] = 1;
   out_8392593010464093728[8] = 0;
   out_8392593010464093728[9] = 0;
   out_8392593010464093728[10] = 0;
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
void gnss_err_fun(double *nom_x, double *delta_x, double *out_8052698219636447439) {
  err_fun(nom_x, delta_x, out_8052698219636447439);
}
void gnss_inv_err_fun(double *nom_x, double *true_x, double *out_414007979716982857) {
  inv_err_fun(nom_x, true_x, out_414007979716982857);
}
void gnss_H_mod_fun(double *state, double *out_1658508881837957111) {
  H_mod_fun(state, out_1658508881837957111);
}
void gnss_f_fun(double *state, double dt, double *out_2765158645351032639) {
  f_fun(state,  dt, out_2765158645351032639);
}
void gnss_F_fun(double *state, double dt, double *out_3889898511770947762) {
  F_fun(state,  dt, out_3889898511770947762);
}
void gnss_h_6(double *state, double *sat_pos, double *out_3151616376493060002) {
  h_6(state, sat_pos, out_3151616376493060002);
}
void gnss_H_6(double *state, double *sat_pos, double *out_8521601814755962792) {
  H_6(state, sat_pos, out_8521601814755962792);
}
void gnss_h_20(double *state, double *sat_pos, double *out_1001695644916733854) {
  h_20(state, sat_pos, out_1001695644916733854);
}
void gnss_H_20(double *state, double *sat_pos, double *out_3587922318809976588) {
  H_20(state, sat_pos, out_3587922318809976588);
}
void gnss_h_7(double *state, double *sat_pos_vel, double *out_1581577151931372281) {
  h_7(state, sat_pos_vel, out_1581577151931372281);
}
void gnss_H_7(double *state, double *sat_pos_vel, double *out_8392593010464093728) {
  H_7(state, sat_pos_vel, out_8392593010464093728);
}
void gnss_h_21(double *state, double *sat_pos_vel, double *out_1581577151931372281) {
  h_21(state, sat_pos_vel, out_1581577151931372281);
}
void gnss_H_21(double *state, double *sat_pos_vel, double *out_8392593010464093728) {
  H_21(state, sat_pos_vel, out_8392593010464093728);
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
