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
void err_fun(double *nom_x, double *delta_x, double *out_5888416049405480502) {
   out_5888416049405480502[0] = delta_x[0] + nom_x[0];
   out_5888416049405480502[1] = delta_x[1] + nom_x[1];
   out_5888416049405480502[2] = delta_x[2] + nom_x[2];
   out_5888416049405480502[3] = delta_x[3] + nom_x[3];
   out_5888416049405480502[4] = delta_x[4] + nom_x[4];
   out_5888416049405480502[5] = delta_x[5] + nom_x[5];
   out_5888416049405480502[6] = delta_x[6] + nom_x[6];
   out_5888416049405480502[7] = delta_x[7] + nom_x[7];
   out_5888416049405480502[8] = delta_x[8] + nom_x[8];
   out_5888416049405480502[9] = delta_x[9] + nom_x[9];
   out_5888416049405480502[10] = delta_x[10] + nom_x[10];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_772137700245917424) {
   out_772137700245917424[0] = -nom_x[0] + true_x[0];
   out_772137700245917424[1] = -nom_x[1] + true_x[1];
   out_772137700245917424[2] = -nom_x[2] + true_x[2];
   out_772137700245917424[3] = -nom_x[3] + true_x[3];
   out_772137700245917424[4] = -nom_x[4] + true_x[4];
   out_772137700245917424[5] = -nom_x[5] + true_x[5];
   out_772137700245917424[6] = -nom_x[6] + true_x[6];
   out_772137700245917424[7] = -nom_x[7] + true_x[7];
   out_772137700245917424[8] = -nom_x[8] + true_x[8];
   out_772137700245917424[9] = -nom_x[9] + true_x[9];
   out_772137700245917424[10] = -nom_x[10] + true_x[10];
}
void H_mod_fun(double *state, double *out_6081254025442487169) {
   out_6081254025442487169[0] = 1.0;
   out_6081254025442487169[1] = 0;
   out_6081254025442487169[2] = 0;
   out_6081254025442487169[3] = 0;
   out_6081254025442487169[4] = 0;
   out_6081254025442487169[5] = 0;
   out_6081254025442487169[6] = 0;
   out_6081254025442487169[7] = 0;
   out_6081254025442487169[8] = 0;
   out_6081254025442487169[9] = 0;
   out_6081254025442487169[10] = 0;
   out_6081254025442487169[11] = 0;
   out_6081254025442487169[12] = 1.0;
   out_6081254025442487169[13] = 0;
   out_6081254025442487169[14] = 0;
   out_6081254025442487169[15] = 0;
   out_6081254025442487169[16] = 0;
   out_6081254025442487169[17] = 0;
   out_6081254025442487169[18] = 0;
   out_6081254025442487169[19] = 0;
   out_6081254025442487169[20] = 0;
   out_6081254025442487169[21] = 0;
   out_6081254025442487169[22] = 0;
   out_6081254025442487169[23] = 0;
   out_6081254025442487169[24] = 1.0;
   out_6081254025442487169[25] = 0;
   out_6081254025442487169[26] = 0;
   out_6081254025442487169[27] = 0;
   out_6081254025442487169[28] = 0;
   out_6081254025442487169[29] = 0;
   out_6081254025442487169[30] = 0;
   out_6081254025442487169[31] = 0;
   out_6081254025442487169[32] = 0;
   out_6081254025442487169[33] = 0;
   out_6081254025442487169[34] = 0;
   out_6081254025442487169[35] = 0;
   out_6081254025442487169[36] = 1.0;
   out_6081254025442487169[37] = 0;
   out_6081254025442487169[38] = 0;
   out_6081254025442487169[39] = 0;
   out_6081254025442487169[40] = 0;
   out_6081254025442487169[41] = 0;
   out_6081254025442487169[42] = 0;
   out_6081254025442487169[43] = 0;
   out_6081254025442487169[44] = 0;
   out_6081254025442487169[45] = 0;
   out_6081254025442487169[46] = 0;
   out_6081254025442487169[47] = 0;
   out_6081254025442487169[48] = 1.0;
   out_6081254025442487169[49] = 0;
   out_6081254025442487169[50] = 0;
   out_6081254025442487169[51] = 0;
   out_6081254025442487169[52] = 0;
   out_6081254025442487169[53] = 0;
   out_6081254025442487169[54] = 0;
   out_6081254025442487169[55] = 0;
   out_6081254025442487169[56] = 0;
   out_6081254025442487169[57] = 0;
   out_6081254025442487169[58] = 0;
   out_6081254025442487169[59] = 0;
   out_6081254025442487169[60] = 1.0;
   out_6081254025442487169[61] = 0;
   out_6081254025442487169[62] = 0;
   out_6081254025442487169[63] = 0;
   out_6081254025442487169[64] = 0;
   out_6081254025442487169[65] = 0;
   out_6081254025442487169[66] = 0;
   out_6081254025442487169[67] = 0;
   out_6081254025442487169[68] = 0;
   out_6081254025442487169[69] = 0;
   out_6081254025442487169[70] = 0;
   out_6081254025442487169[71] = 0;
   out_6081254025442487169[72] = 1.0;
   out_6081254025442487169[73] = 0;
   out_6081254025442487169[74] = 0;
   out_6081254025442487169[75] = 0;
   out_6081254025442487169[76] = 0;
   out_6081254025442487169[77] = 0;
   out_6081254025442487169[78] = 0;
   out_6081254025442487169[79] = 0;
   out_6081254025442487169[80] = 0;
   out_6081254025442487169[81] = 0;
   out_6081254025442487169[82] = 0;
   out_6081254025442487169[83] = 0;
   out_6081254025442487169[84] = 1.0;
   out_6081254025442487169[85] = 0;
   out_6081254025442487169[86] = 0;
   out_6081254025442487169[87] = 0;
   out_6081254025442487169[88] = 0;
   out_6081254025442487169[89] = 0;
   out_6081254025442487169[90] = 0;
   out_6081254025442487169[91] = 0;
   out_6081254025442487169[92] = 0;
   out_6081254025442487169[93] = 0;
   out_6081254025442487169[94] = 0;
   out_6081254025442487169[95] = 0;
   out_6081254025442487169[96] = 1.0;
   out_6081254025442487169[97] = 0;
   out_6081254025442487169[98] = 0;
   out_6081254025442487169[99] = 0;
   out_6081254025442487169[100] = 0;
   out_6081254025442487169[101] = 0;
   out_6081254025442487169[102] = 0;
   out_6081254025442487169[103] = 0;
   out_6081254025442487169[104] = 0;
   out_6081254025442487169[105] = 0;
   out_6081254025442487169[106] = 0;
   out_6081254025442487169[107] = 0;
   out_6081254025442487169[108] = 1.0;
   out_6081254025442487169[109] = 0;
   out_6081254025442487169[110] = 0;
   out_6081254025442487169[111] = 0;
   out_6081254025442487169[112] = 0;
   out_6081254025442487169[113] = 0;
   out_6081254025442487169[114] = 0;
   out_6081254025442487169[115] = 0;
   out_6081254025442487169[116] = 0;
   out_6081254025442487169[117] = 0;
   out_6081254025442487169[118] = 0;
   out_6081254025442487169[119] = 0;
   out_6081254025442487169[120] = 1.0;
}
void f_fun(double *state, double dt, double *out_7103374999999395041) {
   out_7103374999999395041[0] = dt*state[3] + state[0];
   out_7103374999999395041[1] = dt*state[4] + state[1];
   out_7103374999999395041[2] = dt*state[5] + state[2];
   out_7103374999999395041[3] = state[3];
   out_7103374999999395041[4] = state[4];
   out_7103374999999395041[5] = state[5];
   out_7103374999999395041[6] = dt*state[7] + state[6];
   out_7103374999999395041[7] = dt*state[8] + state[7];
   out_7103374999999395041[8] = state[8];
   out_7103374999999395041[9] = state[9];
   out_7103374999999395041[10] = state[10];
}
void F_fun(double *state, double dt, double *out_3225715469495907391) {
   out_3225715469495907391[0] = 1;
   out_3225715469495907391[1] = 0;
   out_3225715469495907391[2] = 0;
   out_3225715469495907391[3] = dt;
   out_3225715469495907391[4] = 0;
   out_3225715469495907391[5] = 0;
   out_3225715469495907391[6] = 0;
   out_3225715469495907391[7] = 0;
   out_3225715469495907391[8] = 0;
   out_3225715469495907391[9] = 0;
   out_3225715469495907391[10] = 0;
   out_3225715469495907391[11] = 0;
   out_3225715469495907391[12] = 1;
   out_3225715469495907391[13] = 0;
   out_3225715469495907391[14] = 0;
   out_3225715469495907391[15] = dt;
   out_3225715469495907391[16] = 0;
   out_3225715469495907391[17] = 0;
   out_3225715469495907391[18] = 0;
   out_3225715469495907391[19] = 0;
   out_3225715469495907391[20] = 0;
   out_3225715469495907391[21] = 0;
   out_3225715469495907391[22] = 0;
   out_3225715469495907391[23] = 0;
   out_3225715469495907391[24] = 1;
   out_3225715469495907391[25] = 0;
   out_3225715469495907391[26] = 0;
   out_3225715469495907391[27] = dt;
   out_3225715469495907391[28] = 0;
   out_3225715469495907391[29] = 0;
   out_3225715469495907391[30] = 0;
   out_3225715469495907391[31] = 0;
   out_3225715469495907391[32] = 0;
   out_3225715469495907391[33] = 0;
   out_3225715469495907391[34] = 0;
   out_3225715469495907391[35] = 0;
   out_3225715469495907391[36] = 1;
   out_3225715469495907391[37] = 0;
   out_3225715469495907391[38] = 0;
   out_3225715469495907391[39] = 0;
   out_3225715469495907391[40] = 0;
   out_3225715469495907391[41] = 0;
   out_3225715469495907391[42] = 0;
   out_3225715469495907391[43] = 0;
   out_3225715469495907391[44] = 0;
   out_3225715469495907391[45] = 0;
   out_3225715469495907391[46] = 0;
   out_3225715469495907391[47] = 0;
   out_3225715469495907391[48] = 1;
   out_3225715469495907391[49] = 0;
   out_3225715469495907391[50] = 0;
   out_3225715469495907391[51] = 0;
   out_3225715469495907391[52] = 0;
   out_3225715469495907391[53] = 0;
   out_3225715469495907391[54] = 0;
   out_3225715469495907391[55] = 0;
   out_3225715469495907391[56] = 0;
   out_3225715469495907391[57] = 0;
   out_3225715469495907391[58] = 0;
   out_3225715469495907391[59] = 0;
   out_3225715469495907391[60] = 1;
   out_3225715469495907391[61] = 0;
   out_3225715469495907391[62] = 0;
   out_3225715469495907391[63] = 0;
   out_3225715469495907391[64] = 0;
   out_3225715469495907391[65] = 0;
   out_3225715469495907391[66] = 0;
   out_3225715469495907391[67] = 0;
   out_3225715469495907391[68] = 0;
   out_3225715469495907391[69] = 0;
   out_3225715469495907391[70] = 0;
   out_3225715469495907391[71] = 0;
   out_3225715469495907391[72] = 1;
   out_3225715469495907391[73] = dt;
   out_3225715469495907391[74] = 0;
   out_3225715469495907391[75] = 0;
   out_3225715469495907391[76] = 0;
   out_3225715469495907391[77] = 0;
   out_3225715469495907391[78] = 0;
   out_3225715469495907391[79] = 0;
   out_3225715469495907391[80] = 0;
   out_3225715469495907391[81] = 0;
   out_3225715469495907391[82] = 0;
   out_3225715469495907391[83] = 0;
   out_3225715469495907391[84] = 1;
   out_3225715469495907391[85] = dt;
   out_3225715469495907391[86] = 0;
   out_3225715469495907391[87] = 0;
   out_3225715469495907391[88] = 0;
   out_3225715469495907391[89] = 0;
   out_3225715469495907391[90] = 0;
   out_3225715469495907391[91] = 0;
   out_3225715469495907391[92] = 0;
   out_3225715469495907391[93] = 0;
   out_3225715469495907391[94] = 0;
   out_3225715469495907391[95] = 0;
   out_3225715469495907391[96] = 1;
   out_3225715469495907391[97] = 0;
   out_3225715469495907391[98] = 0;
   out_3225715469495907391[99] = 0;
   out_3225715469495907391[100] = 0;
   out_3225715469495907391[101] = 0;
   out_3225715469495907391[102] = 0;
   out_3225715469495907391[103] = 0;
   out_3225715469495907391[104] = 0;
   out_3225715469495907391[105] = 0;
   out_3225715469495907391[106] = 0;
   out_3225715469495907391[107] = 0;
   out_3225715469495907391[108] = 1;
   out_3225715469495907391[109] = 0;
   out_3225715469495907391[110] = 0;
   out_3225715469495907391[111] = 0;
   out_3225715469495907391[112] = 0;
   out_3225715469495907391[113] = 0;
   out_3225715469495907391[114] = 0;
   out_3225715469495907391[115] = 0;
   out_3225715469495907391[116] = 0;
   out_3225715469495907391[117] = 0;
   out_3225715469495907391[118] = 0;
   out_3225715469495907391[119] = 0;
   out_3225715469495907391[120] = 1;
}
void h_6(double *state, double *sat_pos, double *out_4135186210083771617) {
   out_4135186210083771617[0] = sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2)) + state[6];
}
void H_6(double *state, double *sat_pos, double *out_2035153063914442509) {
   out_2035153063914442509[0] = (-sat_pos[0] + state[0])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_2035153063914442509[1] = (-sat_pos[1] + state[1])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_2035153063914442509[2] = (-sat_pos[2] + state[2])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_2035153063914442509[3] = 0;
   out_2035153063914442509[4] = 0;
   out_2035153063914442509[5] = 0;
   out_2035153063914442509[6] = 1;
   out_2035153063914442509[7] = 0;
   out_2035153063914442509[8] = 0;
   out_2035153063914442509[9] = 0;
   out_2035153063914442509[10] = 0;
}
void h_20(double *state, double *sat_pos, double *out_2483402616262014693) {
   out_2483402616262014693[0] = sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2)) + sat_pos[3]*state[10] + state[6] + state[9];
}
void H_20(double *state, double *sat_pos, double *out_8177039925481845738) {
   out_8177039925481845738[0] = (-sat_pos[0] + state[0])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_8177039925481845738[1] = (-sat_pos[1] + state[1])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_8177039925481845738[2] = (-sat_pos[2] + state[2])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_8177039925481845738[3] = 0;
   out_8177039925481845738[4] = 0;
   out_8177039925481845738[5] = 0;
   out_8177039925481845738[6] = 1;
   out_8177039925481845738[7] = 0;
   out_8177039925481845738[8] = 0;
   out_8177039925481845738[9] = 1;
   out_8177039925481845738[10] = sat_pos[3];
}
void h_7(double *state, double *sat_pos_vel, double *out_1668019775180221260) {
   out_1668019775180221260[0] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[3] - state[3])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[4] - state[4])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + (sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + state[7];
}
void H_7(double *state, double *sat_pos_vel, double *out_887204893166495018) {
   out_887204893166495018[0] = pow(sat_pos_vel[0] - state[0], 2)*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[0] - state[0])*(sat_pos_vel[1] - state[1])*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[0] - state[0])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[3] - state[3])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_887204893166495018[1] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[1] - state[1])*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + pow(sat_pos_vel[1] - state[1], 2)*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[4] - state[4])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_887204893166495018[2] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + pow(sat_pos_vel[2] - state[2], 2)*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[5] - state[5])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_887204893166495018[3] = -(sat_pos_vel[0] - state[0])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_887204893166495018[4] = -(sat_pos_vel[1] - state[1])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_887204893166495018[5] = -(sat_pos_vel[2] - state[2])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_887204893166495018[6] = 0;
   out_887204893166495018[7] = 1;
   out_887204893166495018[8] = 0;
   out_887204893166495018[9] = 0;
   out_887204893166495018[10] = 0;
}
void h_21(double *state, double *sat_pos_vel, double *out_1668019775180221260) {
   out_1668019775180221260[0] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[3] - state[3])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[4] - state[4])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + (sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + state[7];
}
void H_21(double *state, double *sat_pos_vel, double *out_887204893166495018) {
   out_887204893166495018[0] = pow(sat_pos_vel[0] - state[0], 2)*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[0] - state[0])*(sat_pos_vel[1] - state[1])*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[0] - state[0])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[3] - state[3])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_887204893166495018[1] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[1] - state[1])*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + pow(sat_pos_vel[1] - state[1], 2)*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[4] - state[4])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_887204893166495018[2] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + pow(sat_pos_vel[2] - state[2], 2)*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[5] - state[5])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_887204893166495018[3] = -(sat_pos_vel[0] - state[0])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_887204893166495018[4] = -(sat_pos_vel[1] - state[1])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_887204893166495018[5] = -(sat_pos_vel[2] - state[2])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_887204893166495018[6] = 0;
   out_887204893166495018[7] = 1;
   out_887204893166495018[8] = 0;
   out_887204893166495018[9] = 0;
   out_887204893166495018[10] = 0;
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
void gnss_err_fun(double *nom_x, double *delta_x, double *out_5888416049405480502) {
  err_fun(nom_x, delta_x, out_5888416049405480502);
}
void gnss_inv_err_fun(double *nom_x, double *true_x, double *out_772137700245917424) {
  inv_err_fun(nom_x, true_x, out_772137700245917424);
}
void gnss_H_mod_fun(double *state, double *out_6081254025442487169) {
  H_mod_fun(state, out_6081254025442487169);
}
void gnss_f_fun(double *state, double dt, double *out_7103374999999395041) {
  f_fun(state,  dt, out_7103374999999395041);
}
void gnss_F_fun(double *state, double dt, double *out_3225715469495907391) {
  F_fun(state,  dt, out_3225715469495907391);
}
void gnss_h_6(double *state, double *sat_pos, double *out_4135186210083771617) {
  h_6(state, sat_pos, out_4135186210083771617);
}
void gnss_H_6(double *state, double *sat_pos, double *out_2035153063914442509) {
  H_6(state, sat_pos, out_2035153063914442509);
}
void gnss_h_20(double *state, double *sat_pos, double *out_2483402616262014693) {
  h_20(state, sat_pos, out_2483402616262014693);
}
void gnss_H_20(double *state, double *sat_pos, double *out_8177039925481845738) {
  H_20(state, sat_pos, out_8177039925481845738);
}
void gnss_h_7(double *state, double *sat_pos_vel, double *out_1668019775180221260) {
  h_7(state, sat_pos_vel, out_1668019775180221260);
}
void gnss_H_7(double *state, double *sat_pos_vel, double *out_887204893166495018) {
  H_7(state, sat_pos_vel, out_887204893166495018);
}
void gnss_h_21(double *state, double *sat_pos_vel, double *out_1668019775180221260) {
  h_21(state, sat_pos_vel, out_1668019775180221260);
}
void gnss_H_21(double *state, double *sat_pos_vel, double *out_887204893166495018) {
  H_21(state, sat_pos_vel, out_887204893166495018);
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
