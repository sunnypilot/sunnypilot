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
void err_fun(double *nom_x, double *delta_x, double *out_6775506088001038527) {
   out_6775506088001038527[0] = delta_x[0] + nom_x[0];
   out_6775506088001038527[1] = delta_x[1] + nom_x[1];
   out_6775506088001038527[2] = delta_x[2] + nom_x[2];
   out_6775506088001038527[3] = delta_x[3] + nom_x[3];
   out_6775506088001038527[4] = delta_x[4] + nom_x[4];
   out_6775506088001038527[5] = delta_x[5] + nom_x[5];
   out_6775506088001038527[6] = delta_x[6] + nom_x[6];
   out_6775506088001038527[7] = delta_x[7] + nom_x[7];
   out_6775506088001038527[8] = delta_x[8] + nom_x[8];
   out_6775506088001038527[9] = delta_x[9] + nom_x[9];
   out_6775506088001038527[10] = delta_x[10] + nom_x[10];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_1965239601308615964) {
   out_1965239601308615964[0] = -nom_x[0] + true_x[0];
   out_1965239601308615964[1] = -nom_x[1] + true_x[1];
   out_1965239601308615964[2] = -nom_x[2] + true_x[2];
   out_1965239601308615964[3] = -nom_x[3] + true_x[3];
   out_1965239601308615964[4] = -nom_x[4] + true_x[4];
   out_1965239601308615964[5] = -nom_x[5] + true_x[5];
   out_1965239601308615964[6] = -nom_x[6] + true_x[6];
   out_1965239601308615964[7] = -nom_x[7] + true_x[7];
   out_1965239601308615964[8] = -nom_x[8] + true_x[8];
   out_1965239601308615964[9] = -nom_x[9] + true_x[9];
   out_1965239601308615964[10] = -nom_x[10] + true_x[10];
}
void H_mod_fun(double *state, double *out_7340239268303197879) {
   out_7340239268303197879[0] = 1.0;
   out_7340239268303197879[1] = 0;
   out_7340239268303197879[2] = 0;
   out_7340239268303197879[3] = 0;
   out_7340239268303197879[4] = 0;
   out_7340239268303197879[5] = 0;
   out_7340239268303197879[6] = 0;
   out_7340239268303197879[7] = 0;
   out_7340239268303197879[8] = 0;
   out_7340239268303197879[9] = 0;
   out_7340239268303197879[10] = 0;
   out_7340239268303197879[11] = 0;
   out_7340239268303197879[12] = 1.0;
   out_7340239268303197879[13] = 0;
   out_7340239268303197879[14] = 0;
   out_7340239268303197879[15] = 0;
   out_7340239268303197879[16] = 0;
   out_7340239268303197879[17] = 0;
   out_7340239268303197879[18] = 0;
   out_7340239268303197879[19] = 0;
   out_7340239268303197879[20] = 0;
   out_7340239268303197879[21] = 0;
   out_7340239268303197879[22] = 0;
   out_7340239268303197879[23] = 0;
   out_7340239268303197879[24] = 1.0;
   out_7340239268303197879[25] = 0;
   out_7340239268303197879[26] = 0;
   out_7340239268303197879[27] = 0;
   out_7340239268303197879[28] = 0;
   out_7340239268303197879[29] = 0;
   out_7340239268303197879[30] = 0;
   out_7340239268303197879[31] = 0;
   out_7340239268303197879[32] = 0;
   out_7340239268303197879[33] = 0;
   out_7340239268303197879[34] = 0;
   out_7340239268303197879[35] = 0;
   out_7340239268303197879[36] = 1.0;
   out_7340239268303197879[37] = 0;
   out_7340239268303197879[38] = 0;
   out_7340239268303197879[39] = 0;
   out_7340239268303197879[40] = 0;
   out_7340239268303197879[41] = 0;
   out_7340239268303197879[42] = 0;
   out_7340239268303197879[43] = 0;
   out_7340239268303197879[44] = 0;
   out_7340239268303197879[45] = 0;
   out_7340239268303197879[46] = 0;
   out_7340239268303197879[47] = 0;
   out_7340239268303197879[48] = 1.0;
   out_7340239268303197879[49] = 0;
   out_7340239268303197879[50] = 0;
   out_7340239268303197879[51] = 0;
   out_7340239268303197879[52] = 0;
   out_7340239268303197879[53] = 0;
   out_7340239268303197879[54] = 0;
   out_7340239268303197879[55] = 0;
   out_7340239268303197879[56] = 0;
   out_7340239268303197879[57] = 0;
   out_7340239268303197879[58] = 0;
   out_7340239268303197879[59] = 0;
   out_7340239268303197879[60] = 1.0;
   out_7340239268303197879[61] = 0;
   out_7340239268303197879[62] = 0;
   out_7340239268303197879[63] = 0;
   out_7340239268303197879[64] = 0;
   out_7340239268303197879[65] = 0;
   out_7340239268303197879[66] = 0;
   out_7340239268303197879[67] = 0;
   out_7340239268303197879[68] = 0;
   out_7340239268303197879[69] = 0;
   out_7340239268303197879[70] = 0;
   out_7340239268303197879[71] = 0;
   out_7340239268303197879[72] = 1.0;
   out_7340239268303197879[73] = 0;
   out_7340239268303197879[74] = 0;
   out_7340239268303197879[75] = 0;
   out_7340239268303197879[76] = 0;
   out_7340239268303197879[77] = 0;
   out_7340239268303197879[78] = 0;
   out_7340239268303197879[79] = 0;
   out_7340239268303197879[80] = 0;
   out_7340239268303197879[81] = 0;
   out_7340239268303197879[82] = 0;
   out_7340239268303197879[83] = 0;
   out_7340239268303197879[84] = 1.0;
   out_7340239268303197879[85] = 0;
   out_7340239268303197879[86] = 0;
   out_7340239268303197879[87] = 0;
   out_7340239268303197879[88] = 0;
   out_7340239268303197879[89] = 0;
   out_7340239268303197879[90] = 0;
   out_7340239268303197879[91] = 0;
   out_7340239268303197879[92] = 0;
   out_7340239268303197879[93] = 0;
   out_7340239268303197879[94] = 0;
   out_7340239268303197879[95] = 0;
   out_7340239268303197879[96] = 1.0;
   out_7340239268303197879[97] = 0;
   out_7340239268303197879[98] = 0;
   out_7340239268303197879[99] = 0;
   out_7340239268303197879[100] = 0;
   out_7340239268303197879[101] = 0;
   out_7340239268303197879[102] = 0;
   out_7340239268303197879[103] = 0;
   out_7340239268303197879[104] = 0;
   out_7340239268303197879[105] = 0;
   out_7340239268303197879[106] = 0;
   out_7340239268303197879[107] = 0;
   out_7340239268303197879[108] = 1.0;
   out_7340239268303197879[109] = 0;
   out_7340239268303197879[110] = 0;
   out_7340239268303197879[111] = 0;
   out_7340239268303197879[112] = 0;
   out_7340239268303197879[113] = 0;
   out_7340239268303197879[114] = 0;
   out_7340239268303197879[115] = 0;
   out_7340239268303197879[116] = 0;
   out_7340239268303197879[117] = 0;
   out_7340239268303197879[118] = 0;
   out_7340239268303197879[119] = 0;
   out_7340239268303197879[120] = 1.0;
}
void f_fun(double *state, double dt, double *out_4979886782540772425) {
   out_4979886782540772425[0] = dt*state[3] + state[0];
   out_4979886782540772425[1] = dt*state[4] + state[1];
   out_4979886782540772425[2] = dt*state[5] + state[2];
   out_4979886782540772425[3] = state[3];
   out_4979886782540772425[4] = state[4];
   out_4979886782540772425[5] = state[5];
   out_4979886782540772425[6] = dt*state[7] + state[6];
   out_4979886782540772425[7] = dt*state[8] + state[7];
   out_4979886782540772425[8] = state[8];
   out_4979886782540772425[9] = state[9];
   out_4979886782540772425[10] = state[10];
}
void F_fun(double *state, double dt, double *out_4307622071330831920) {
   out_4307622071330831920[0] = 1;
   out_4307622071330831920[1] = 0;
   out_4307622071330831920[2] = 0;
   out_4307622071330831920[3] = dt;
   out_4307622071330831920[4] = 0;
   out_4307622071330831920[5] = 0;
   out_4307622071330831920[6] = 0;
   out_4307622071330831920[7] = 0;
   out_4307622071330831920[8] = 0;
   out_4307622071330831920[9] = 0;
   out_4307622071330831920[10] = 0;
   out_4307622071330831920[11] = 0;
   out_4307622071330831920[12] = 1;
   out_4307622071330831920[13] = 0;
   out_4307622071330831920[14] = 0;
   out_4307622071330831920[15] = dt;
   out_4307622071330831920[16] = 0;
   out_4307622071330831920[17] = 0;
   out_4307622071330831920[18] = 0;
   out_4307622071330831920[19] = 0;
   out_4307622071330831920[20] = 0;
   out_4307622071330831920[21] = 0;
   out_4307622071330831920[22] = 0;
   out_4307622071330831920[23] = 0;
   out_4307622071330831920[24] = 1;
   out_4307622071330831920[25] = 0;
   out_4307622071330831920[26] = 0;
   out_4307622071330831920[27] = dt;
   out_4307622071330831920[28] = 0;
   out_4307622071330831920[29] = 0;
   out_4307622071330831920[30] = 0;
   out_4307622071330831920[31] = 0;
   out_4307622071330831920[32] = 0;
   out_4307622071330831920[33] = 0;
   out_4307622071330831920[34] = 0;
   out_4307622071330831920[35] = 0;
   out_4307622071330831920[36] = 1;
   out_4307622071330831920[37] = 0;
   out_4307622071330831920[38] = 0;
   out_4307622071330831920[39] = 0;
   out_4307622071330831920[40] = 0;
   out_4307622071330831920[41] = 0;
   out_4307622071330831920[42] = 0;
   out_4307622071330831920[43] = 0;
   out_4307622071330831920[44] = 0;
   out_4307622071330831920[45] = 0;
   out_4307622071330831920[46] = 0;
   out_4307622071330831920[47] = 0;
   out_4307622071330831920[48] = 1;
   out_4307622071330831920[49] = 0;
   out_4307622071330831920[50] = 0;
   out_4307622071330831920[51] = 0;
   out_4307622071330831920[52] = 0;
   out_4307622071330831920[53] = 0;
   out_4307622071330831920[54] = 0;
   out_4307622071330831920[55] = 0;
   out_4307622071330831920[56] = 0;
   out_4307622071330831920[57] = 0;
   out_4307622071330831920[58] = 0;
   out_4307622071330831920[59] = 0;
   out_4307622071330831920[60] = 1;
   out_4307622071330831920[61] = 0;
   out_4307622071330831920[62] = 0;
   out_4307622071330831920[63] = 0;
   out_4307622071330831920[64] = 0;
   out_4307622071330831920[65] = 0;
   out_4307622071330831920[66] = 0;
   out_4307622071330831920[67] = 0;
   out_4307622071330831920[68] = 0;
   out_4307622071330831920[69] = 0;
   out_4307622071330831920[70] = 0;
   out_4307622071330831920[71] = 0;
   out_4307622071330831920[72] = 1;
   out_4307622071330831920[73] = dt;
   out_4307622071330831920[74] = 0;
   out_4307622071330831920[75] = 0;
   out_4307622071330831920[76] = 0;
   out_4307622071330831920[77] = 0;
   out_4307622071330831920[78] = 0;
   out_4307622071330831920[79] = 0;
   out_4307622071330831920[80] = 0;
   out_4307622071330831920[81] = 0;
   out_4307622071330831920[82] = 0;
   out_4307622071330831920[83] = 0;
   out_4307622071330831920[84] = 1;
   out_4307622071330831920[85] = dt;
   out_4307622071330831920[86] = 0;
   out_4307622071330831920[87] = 0;
   out_4307622071330831920[88] = 0;
   out_4307622071330831920[89] = 0;
   out_4307622071330831920[90] = 0;
   out_4307622071330831920[91] = 0;
   out_4307622071330831920[92] = 0;
   out_4307622071330831920[93] = 0;
   out_4307622071330831920[94] = 0;
   out_4307622071330831920[95] = 0;
   out_4307622071330831920[96] = 1;
   out_4307622071330831920[97] = 0;
   out_4307622071330831920[98] = 0;
   out_4307622071330831920[99] = 0;
   out_4307622071330831920[100] = 0;
   out_4307622071330831920[101] = 0;
   out_4307622071330831920[102] = 0;
   out_4307622071330831920[103] = 0;
   out_4307622071330831920[104] = 0;
   out_4307622071330831920[105] = 0;
   out_4307622071330831920[106] = 0;
   out_4307622071330831920[107] = 0;
   out_4307622071330831920[108] = 1;
   out_4307622071330831920[109] = 0;
   out_4307622071330831920[110] = 0;
   out_4307622071330831920[111] = 0;
   out_4307622071330831920[112] = 0;
   out_4307622071330831920[113] = 0;
   out_4307622071330831920[114] = 0;
   out_4307622071330831920[115] = 0;
   out_4307622071330831920[116] = 0;
   out_4307622071330831920[117] = 0;
   out_4307622071330831920[118] = 0;
   out_4307622071330831920[119] = 0;
   out_4307622071330831920[120] = 1;
}
void h_6(double *state, double *sat_pos, double *out_1019340167124243088) {
   out_1019340167124243088[0] = sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2)) + state[6];
}
void H_6(double *state, double *sat_pos, double *out_3723167288690265933) {
   out_3723167288690265933[0] = (-sat_pos[0] + state[0])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_3723167288690265933[1] = (-sat_pos[1] + state[1])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_3723167288690265933[2] = (-sat_pos[2] + state[2])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_3723167288690265933[3] = 0;
   out_3723167288690265933[4] = 0;
   out_3723167288690265933[5] = 0;
   out_3723167288690265933[6] = 1;
   out_3723167288690265933[7] = 0;
   out_3723167288690265933[8] = 0;
   out_3723167288690265933[9] = 0;
   out_3723167288690265933[10] = 0;
}
void h_20(double *state, double *sat_pos, double *out_5850517768349837563) {
   out_5850517768349837563[0] = sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2)) + sat_pos[3]*state[10] + state[6] + state[9];
}
void H_20(double *state, double *sat_pos, double *out_199690115275631714) {
   out_199690115275631714[0] = (-sat_pos[0] + state[0])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_199690115275631714[1] = (-sat_pos[1] + state[1])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_199690115275631714[2] = (-sat_pos[2] + state[2])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_199690115275631714[3] = 0;
   out_199690115275631714[4] = 0;
   out_199690115275631714[5] = 0;
   out_199690115275631714[6] = 1;
   out_199690115275631714[7] = 0;
   out_199690115275631714[8] = 0;
   out_199690115275631714[9] = 1;
   out_199690115275631714[10] = sat_pos[3];
}
void h_7(double *state, double *sat_pos_vel, double *out_3492188585488856412) {
   out_3492188585488856412[0] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[3] - state[3])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[4] - state[4])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + (sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + state[7];
}
void H_7(double *state, double *sat_pos_vel, double *out_1604423232564836340) {
   out_1604423232564836340[0] = pow(sat_pos_vel[0] - state[0], 2)*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[0] - state[0])*(sat_pos_vel[1] - state[1])*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[0] - state[0])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[3] - state[3])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_1604423232564836340[1] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[1] - state[1])*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + pow(sat_pos_vel[1] - state[1], 2)*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[4] - state[4])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_1604423232564836340[2] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + pow(sat_pos_vel[2] - state[2], 2)*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[5] - state[5])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_1604423232564836340[3] = -(sat_pos_vel[0] - state[0])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_1604423232564836340[4] = -(sat_pos_vel[1] - state[1])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_1604423232564836340[5] = -(sat_pos_vel[2] - state[2])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_1604423232564836340[6] = 0;
   out_1604423232564836340[7] = 1;
   out_1604423232564836340[8] = 0;
   out_1604423232564836340[9] = 0;
   out_1604423232564836340[10] = 0;
}
void h_21(double *state, double *sat_pos_vel, double *out_3492188585488856412) {
   out_3492188585488856412[0] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[3] - state[3])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[4] - state[4])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + (sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + state[7];
}
void H_21(double *state, double *sat_pos_vel, double *out_1604423232564836340) {
   out_1604423232564836340[0] = pow(sat_pos_vel[0] - state[0], 2)*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[0] - state[0])*(sat_pos_vel[1] - state[1])*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[0] - state[0])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[3] - state[3])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_1604423232564836340[1] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[1] - state[1])*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + pow(sat_pos_vel[1] - state[1], 2)*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[4] - state[4])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_1604423232564836340[2] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + pow(sat_pos_vel[2] - state[2], 2)*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[5] - state[5])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_1604423232564836340[3] = -(sat_pos_vel[0] - state[0])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_1604423232564836340[4] = -(sat_pos_vel[1] - state[1])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_1604423232564836340[5] = -(sat_pos_vel[2] - state[2])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_1604423232564836340[6] = 0;
   out_1604423232564836340[7] = 1;
   out_1604423232564836340[8] = 0;
   out_1604423232564836340[9] = 0;
   out_1604423232564836340[10] = 0;
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
void gnss_err_fun(double *nom_x, double *delta_x, double *out_6775506088001038527) {
  err_fun(nom_x, delta_x, out_6775506088001038527);
}
void gnss_inv_err_fun(double *nom_x, double *true_x, double *out_1965239601308615964) {
  inv_err_fun(nom_x, true_x, out_1965239601308615964);
}
void gnss_H_mod_fun(double *state, double *out_7340239268303197879) {
  H_mod_fun(state, out_7340239268303197879);
}
void gnss_f_fun(double *state, double dt, double *out_4979886782540772425) {
  f_fun(state,  dt, out_4979886782540772425);
}
void gnss_F_fun(double *state, double dt, double *out_4307622071330831920) {
  F_fun(state,  dt, out_4307622071330831920);
}
void gnss_h_6(double *state, double *sat_pos, double *out_1019340167124243088) {
  h_6(state, sat_pos, out_1019340167124243088);
}
void gnss_H_6(double *state, double *sat_pos, double *out_3723167288690265933) {
  H_6(state, sat_pos, out_3723167288690265933);
}
void gnss_h_20(double *state, double *sat_pos, double *out_5850517768349837563) {
  h_20(state, sat_pos, out_5850517768349837563);
}
void gnss_H_20(double *state, double *sat_pos, double *out_199690115275631714) {
  H_20(state, sat_pos, out_199690115275631714);
}
void gnss_h_7(double *state, double *sat_pos_vel, double *out_3492188585488856412) {
  h_7(state, sat_pos_vel, out_3492188585488856412);
}
void gnss_H_7(double *state, double *sat_pos_vel, double *out_1604423232564836340) {
  H_7(state, sat_pos_vel, out_1604423232564836340);
}
void gnss_h_21(double *state, double *sat_pos_vel, double *out_3492188585488856412) {
  h_21(state, sat_pos_vel, out_3492188585488856412);
}
void gnss_H_21(double *state, double *sat_pos_vel, double *out_1604423232564836340) {
  H_21(state, sat_pos_vel, out_1604423232564836340);
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
