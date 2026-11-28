#include "pose.h"

namespace {
#define DIM 18
#define EDIM 18
#define MEDIM 18
typedef void (*Hfun)(double *, double *, double *);
const static double MAHA_THRESH_4 = 7.814727903251177;
const static double MAHA_THRESH_10 = 7.814727903251177;
const static double MAHA_THRESH_13 = 7.814727903251177;
const static double MAHA_THRESH_14 = 7.814727903251177;

/******************************************************************************
 *                      Code generated with SymPy 1.14.0                      *
 *                                                                            *
 *              See http://www.sympy.org/ for more information.               *
 *                                                                            *
 *                         This file is part of 'ekf'                         *
 ******************************************************************************/
void err_fun(double *nom_x, double *delta_x, double *out_2613652145363001248) {
   out_2613652145363001248[0] = delta_x[0] + nom_x[0];
   out_2613652145363001248[1] = delta_x[1] + nom_x[1];
   out_2613652145363001248[2] = delta_x[2] + nom_x[2];
   out_2613652145363001248[3] = delta_x[3] + nom_x[3];
   out_2613652145363001248[4] = delta_x[4] + nom_x[4];
   out_2613652145363001248[5] = delta_x[5] + nom_x[5];
   out_2613652145363001248[6] = delta_x[6] + nom_x[6];
   out_2613652145363001248[7] = delta_x[7] + nom_x[7];
   out_2613652145363001248[8] = delta_x[8] + nom_x[8];
   out_2613652145363001248[9] = delta_x[9] + nom_x[9];
   out_2613652145363001248[10] = delta_x[10] + nom_x[10];
   out_2613652145363001248[11] = delta_x[11] + nom_x[11];
   out_2613652145363001248[12] = delta_x[12] + nom_x[12];
   out_2613652145363001248[13] = delta_x[13] + nom_x[13];
   out_2613652145363001248[14] = delta_x[14] + nom_x[14];
   out_2613652145363001248[15] = delta_x[15] + nom_x[15];
   out_2613652145363001248[16] = delta_x[16] + nom_x[16];
   out_2613652145363001248[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_1002934702699052391) {
   out_1002934702699052391[0] = -nom_x[0] + true_x[0];
   out_1002934702699052391[1] = -nom_x[1] + true_x[1];
   out_1002934702699052391[2] = -nom_x[2] + true_x[2];
   out_1002934702699052391[3] = -nom_x[3] + true_x[3];
   out_1002934702699052391[4] = -nom_x[4] + true_x[4];
   out_1002934702699052391[5] = -nom_x[5] + true_x[5];
   out_1002934702699052391[6] = -nom_x[6] + true_x[6];
   out_1002934702699052391[7] = -nom_x[7] + true_x[7];
   out_1002934702699052391[8] = -nom_x[8] + true_x[8];
   out_1002934702699052391[9] = -nom_x[9] + true_x[9];
   out_1002934702699052391[10] = -nom_x[10] + true_x[10];
   out_1002934702699052391[11] = -nom_x[11] + true_x[11];
   out_1002934702699052391[12] = -nom_x[12] + true_x[12];
   out_1002934702699052391[13] = -nom_x[13] + true_x[13];
   out_1002934702699052391[14] = -nom_x[14] + true_x[14];
   out_1002934702699052391[15] = -nom_x[15] + true_x[15];
   out_1002934702699052391[16] = -nom_x[16] + true_x[16];
   out_1002934702699052391[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_3573439106494925480) {
   out_3573439106494925480[0] = 1.0;
   out_3573439106494925480[1] = 0.0;
   out_3573439106494925480[2] = 0.0;
   out_3573439106494925480[3] = 0.0;
   out_3573439106494925480[4] = 0.0;
   out_3573439106494925480[5] = 0.0;
   out_3573439106494925480[6] = 0.0;
   out_3573439106494925480[7] = 0.0;
   out_3573439106494925480[8] = 0.0;
   out_3573439106494925480[9] = 0.0;
   out_3573439106494925480[10] = 0.0;
   out_3573439106494925480[11] = 0.0;
   out_3573439106494925480[12] = 0.0;
   out_3573439106494925480[13] = 0.0;
   out_3573439106494925480[14] = 0.0;
   out_3573439106494925480[15] = 0.0;
   out_3573439106494925480[16] = 0.0;
   out_3573439106494925480[17] = 0.0;
   out_3573439106494925480[18] = 0.0;
   out_3573439106494925480[19] = 1.0;
   out_3573439106494925480[20] = 0.0;
   out_3573439106494925480[21] = 0.0;
   out_3573439106494925480[22] = 0.0;
   out_3573439106494925480[23] = 0.0;
   out_3573439106494925480[24] = 0.0;
   out_3573439106494925480[25] = 0.0;
   out_3573439106494925480[26] = 0.0;
   out_3573439106494925480[27] = 0.0;
   out_3573439106494925480[28] = 0.0;
   out_3573439106494925480[29] = 0.0;
   out_3573439106494925480[30] = 0.0;
   out_3573439106494925480[31] = 0.0;
   out_3573439106494925480[32] = 0.0;
   out_3573439106494925480[33] = 0.0;
   out_3573439106494925480[34] = 0.0;
   out_3573439106494925480[35] = 0.0;
   out_3573439106494925480[36] = 0.0;
   out_3573439106494925480[37] = 0.0;
   out_3573439106494925480[38] = 1.0;
   out_3573439106494925480[39] = 0.0;
   out_3573439106494925480[40] = 0.0;
   out_3573439106494925480[41] = 0.0;
   out_3573439106494925480[42] = 0.0;
   out_3573439106494925480[43] = 0.0;
   out_3573439106494925480[44] = 0.0;
   out_3573439106494925480[45] = 0.0;
   out_3573439106494925480[46] = 0.0;
   out_3573439106494925480[47] = 0.0;
   out_3573439106494925480[48] = 0.0;
   out_3573439106494925480[49] = 0.0;
   out_3573439106494925480[50] = 0.0;
   out_3573439106494925480[51] = 0.0;
   out_3573439106494925480[52] = 0.0;
   out_3573439106494925480[53] = 0.0;
   out_3573439106494925480[54] = 0.0;
   out_3573439106494925480[55] = 0.0;
   out_3573439106494925480[56] = 0.0;
   out_3573439106494925480[57] = 1.0;
   out_3573439106494925480[58] = 0.0;
   out_3573439106494925480[59] = 0.0;
   out_3573439106494925480[60] = 0.0;
   out_3573439106494925480[61] = 0.0;
   out_3573439106494925480[62] = 0.0;
   out_3573439106494925480[63] = 0.0;
   out_3573439106494925480[64] = 0.0;
   out_3573439106494925480[65] = 0.0;
   out_3573439106494925480[66] = 0.0;
   out_3573439106494925480[67] = 0.0;
   out_3573439106494925480[68] = 0.0;
   out_3573439106494925480[69] = 0.0;
   out_3573439106494925480[70] = 0.0;
   out_3573439106494925480[71] = 0.0;
   out_3573439106494925480[72] = 0.0;
   out_3573439106494925480[73] = 0.0;
   out_3573439106494925480[74] = 0.0;
   out_3573439106494925480[75] = 0.0;
   out_3573439106494925480[76] = 1.0;
   out_3573439106494925480[77] = 0.0;
   out_3573439106494925480[78] = 0.0;
   out_3573439106494925480[79] = 0.0;
   out_3573439106494925480[80] = 0.0;
   out_3573439106494925480[81] = 0.0;
   out_3573439106494925480[82] = 0.0;
   out_3573439106494925480[83] = 0.0;
   out_3573439106494925480[84] = 0.0;
   out_3573439106494925480[85] = 0.0;
   out_3573439106494925480[86] = 0.0;
   out_3573439106494925480[87] = 0.0;
   out_3573439106494925480[88] = 0.0;
   out_3573439106494925480[89] = 0.0;
   out_3573439106494925480[90] = 0.0;
   out_3573439106494925480[91] = 0.0;
   out_3573439106494925480[92] = 0.0;
   out_3573439106494925480[93] = 0.0;
   out_3573439106494925480[94] = 0.0;
   out_3573439106494925480[95] = 1.0;
   out_3573439106494925480[96] = 0.0;
   out_3573439106494925480[97] = 0.0;
   out_3573439106494925480[98] = 0.0;
   out_3573439106494925480[99] = 0.0;
   out_3573439106494925480[100] = 0.0;
   out_3573439106494925480[101] = 0.0;
   out_3573439106494925480[102] = 0.0;
   out_3573439106494925480[103] = 0.0;
   out_3573439106494925480[104] = 0.0;
   out_3573439106494925480[105] = 0.0;
   out_3573439106494925480[106] = 0.0;
   out_3573439106494925480[107] = 0.0;
   out_3573439106494925480[108] = 0.0;
   out_3573439106494925480[109] = 0.0;
   out_3573439106494925480[110] = 0.0;
   out_3573439106494925480[111] = 0.0;
   out_3573439106494925480[112] = 0.0;
   out_3573439106494925480[113] = 0.0;
   out_3573439106494925480[114] = 1.0;
   out_3573439106494925480[115] = 0.0;
   out_3573439106494925480[116] = 0.0;
   out_3573439106494925480[117] = 0.0;
   out_3573439106494925480[118] = 0.0;
   out_3573439106494925480[119] = 0.0;
   out_3573439106494925480[120] = 0.0;
   out_3573439106494925480[121] = 0.0;
   out_3573439106494925480[122] = 0.0;
   out_3573439106494925480[123] = 0.0;
   out_3573439106494925480[124] = 0.0;
   out_3573439106494925480[125] = 0.0;
   out_3573439106494925480[126] = 0.0;
   out_3573439106494925480[127] = 0.0;
   out_3573439106494925480[128] = 0.0;
   out_3573439106494925480[129] = 0.0;
   out_3573439106494925480[130] = 0.0;
   out_3573439106494925480[131] = 0.0;
   out_3573439106494925480[132] = 0.0;
   out_3573439106494925480[133] = 1.0;
   out_3573439106494925480[134] = 0.0;
   out_3573439106494925480[135] = 0.0;
   out_3573439106494925480[136] = 0.0;
   out_3573439106494925480[137] = 0.0;
   out_3573439106494925480[138] = 0.0;
   out_3573439106494925480[139] = 0.0;
   out_3573439106494925480[140] = 0.0;
   out_3573439106494925480[141] = 0.0;
   out_3573439106494925480[142] = 0.0;
   out_3573439106494925480[143] = 0.0;
   out_3573439106494925480[144] = 0.0;
   out_3573439106494925480[145] = 0.0;
   out_3573439106494925480[146] = 0.0;
   out_3573439106494925480[147] = 0.0;
   out_3573439106494925480[148] = 0.0;
   out_3573439106494925480[149] = 0.0;
   out_3573439106494925480[150] = 0.0;
   out_3573439106494925480[151] = 0.0;
   out_3573439106494925480[152] = 1.0;
   out_3573439106494925480[153] = 0.0;
   out_3573439106494925480[154] = 0.0;
   out_3573439106494925480[155] = 0.0;
   out_3573439106494925480[156] = 0.0;
   out_3573439106494925480[157] = 0.0;
   out_3573439106494925480[158] = 0.0;
   out_3573439106494925480[159] = 0.0;
   out_3573439106494925480[160] = 0.0;
   out_3573439106494925480[161] = 0.0;
   out_3573439106494925480[162] = 0.0;
   out_3573439106494925480[163] = 0.0;
   out_3573439106494925480[164] = 0.0;
   out_3573439106494925480[165] = 0.0;
   out_3573439106494925480[166] = 0.0;
   out_3573439106494925480[167] = 0.0;
   out_3573439106494925480[168] = 0.0;
   out_3573439106494925480[169] = 0.0;
   out_3573439106494925480[170] = 0.0;
   out_3573439106494925480[171] = 1.0;
   out_3573439106494925480[172] = 0.0;
   out_3573439106494925480[173] = 0.0;
   out_3573439106494925480[174] = 0.0;
   out_3573439106494925480[175] = 0.0;
   out_3573439106494925480[176] = 0.0;
   out_3573439106494925480[177] = 0.0;
   out_3573439106494925480[178] = 0.0;
   out_3573439106494925480[179] = 0.0;
   out_3573439106494925480[180] = 0.0;
   out_3573439106494925480[181] = 0.0;
   out_3573439106494925480[182] = 0.0;
   out_3573439106494925480[183] = 0.0;
   out_3573439106494925480[184] = 0.0;
   out_3573439106494925480[185] = 0.0;
   out_3573439106494925480[186] = 0.0;
   out_3573439106494925480[187] = 0.0;
   out_3573439106494925480[188] = 0.0;
   out_3573439106494925480[189] = 0.0;
   out_3573439106494925480[190] = 1.0;
   out_3573439106494925480[191] = 0.0;
   out_3573439106494925480[192] = 0.0;
   out_3573439106494925480[193] = 0.0;
   out_3573439106494925480[194] = 0.0;
   out_3573439106494925480[195] = 0.0;
   out_3573439106494925480[196] = 0.0;
   out_3573439106494925480[197] = 0.0;
   out_3573439106494925480[198] = 0.0;
   out_3573439106494925480[199] = 0.0;
   out_3573439106494925480[200] = 0.0;
   out_3573439106494925480[201] = 0.0;
   out_3573439106494925480[202] = 0.0;
   out_3573439106494925480[203] = 0.0;
   out_3573439106494925480[204] = 0.0;
   out_3573439106494925480[205] = 0.0;
   out_3573439106494925480[206] = 0.0;
   out_3573439106494925480[207] = 0.0;
   out_3573439106494925480[208] = 0.0;
   out_3573439106494925480[209] = 1.0;
   out_3573439106494925480[210] = 0.0;
   out_3573439106494925480[211] = 0.0;
   out_3573439106494925480[212] = 0.0;
   out_3573439106494925480[213] = 0.0;
   out_3573439106494925480[214] = 0.0;
   out_3573439106494925480[215] = 0.0;
   out_3573439106494925480[216] = 0.0;
   out_3573439106494925480[217] = 0.0;
   out_3573439106494925480[218] = 0.0;
   out_3573439106494925480[219] = 0.0;
   out_3573439106494925480[220] = 0.0;
   out_3573439106494925480[221] = 0.0;
   out_3573439106494925480[222] = 0.0;
   out_3573439106494925480[223] = 0.0;
   out_3573439106494925480[224] = 0.0;
   out_3573439106494925480[225] = 0.0;
   out_3573439106494925480[226] = 0.0;
   out_3573439106494925480[227] = 0.0;
   out_3573439106494925480[228] = 1.0;
   out_3573439106494925480[229] = 0.0;
   out_3573439106494925480[230] = 0.0;
   out_3573439106494925480[231] = 0.0;
   out_3573439106494925480[232] = 0.0;
   out_3573439106494925480[233] = 0.0;
   out_3573439106494925480[234] = 0.0;
   out_3573439106494925480[235] = 0.0;
   out_3573439106494925480[236] = 0.0;
   out_3573439106494925480[237] = 0.0;
   out_3573439106494925480[238] = 0.0;
   out_3573439106494925480[239] = 0.0;
   out_3573439106494925480[240] = 0.0;
   out_3573439106494925480[241] = 0.0;
   out_3573439106494925480[242] = 0.0;
   out_3573439106494925480[243] = 0.0;
   out_3573439106494925480[244] = 0.0;
   out_3573439106494925480[245] = 0.0;
   out_3573439106494925480[246] = 0.0;
   out_3573439106494925480[247] = 1.0;
   out_3573439106494925480[248] = 0.0;
   out_3573439106494925480[249] = 0.0;
   out_3573439106494925480[250] = 0.0;
   out_3573439106494925480[251] = 0.0;
   out_3573439106494925480[252] = 0.0;
   out_3573439106494925480[253] = 0.0;
   out_3573439106494925480[254] = 0.0;
   out_3573439106494925480[255] = 0.0;
   out_3573439106494925480[256] = 0.0;
   out_3573439106494925480[257] = 0.0;
   out_3573439106494925480[258] = 0.0;
   out_3573439106494925480[259] = 0.0;
   out_3573439106494925480[260] = 0.0;
   out_3573439106494925480[261] = 0.0;
   out_3573439106494925480[262] = 0.0;
   out_3573439106494925480[263] = 0.0;
   out_3573439106494925480[264] = 0.0;
   out_3573439106494925480[265] = 0.0;
   out_3573439106494925480[266] = 1.0;
   out_3573439106494925480[267] = 0.0;
   out_3573439106494925480[268] = 0.0;
   out_3573439106494925480[269] = 0.0;
   out_3573439106494925480[270] = 0.0;
   out_3573439106494925480[271] = 0.0;
   out_3573439106494925480[272] = 0.0;
   out_3573439106494925480[273] = 0.0;
   out_3573439106494925480[274] = 0.0;
   out_3573439106494925480[275] = 0.0;
   out_3573439106494925480[276] = 0.0;
   out_3573439106494925480[277] = 0.0;
   out_3573439106494925480[278] = 0.0;
   out_3573439106494925480[279] = 0.0;
   out_3573439106494925480[280] = 0.0;
   out_3573439106494925480[281] = 0.0;
   out_3573439106494925480[282] = 0.0;
   out_3573439106494925480[283] = 0.0;
   out_3573439106494925480[284] = 0.0;
   out_3573439106494925480[285] = 1.0;
   out_3573439106494925480[286] = 0.0;
   out_3573439106494925480[287] = 0.0;
   out_3573439106494925480[288] = 0.0;
   out_3573439106494925480[289] = 0.0;
   out_3573439106494925480[290] = 0.0;
   out_3573439106494925480[291] = 0.0;
   out_3573439106494925480[292] = 0.0;
   out_3573439106494925480[293] = 0.0;
   out_3573439106494925480[294] = 0.0;
   out_3573439106494925480[295] = 0.0;
   out_3573439106494925480[296] = 0.0;
   out_3573439106494925480[297] = 0.0;
   out_3573439106494925480[298] = 0.0;
   out_3573439106494925480[299] = 0.0;
   out_3573439106494925480[300] = 0.0;
   out_3573439106494925480[301] = 0.0;
   out_3573439106494925480[302] = 0.0;
   out_3573439106494925480[303] = 0.0;
   out_3573439106494925480[304] = 1.0;
   out_3573439106494925480[305] = 0.0;
   out_3573439106494925480[306] = 0.0;
   out_3573439106494925480[307] = 0.0;
   out_3573439106494925480[308] = 0.0;
   out_3573439106494925480[309] = 0.0;
   out_3573439106494925480[310] = 0.0;
   out_3573439106494925480[311] = 0.0;
   out_3573439106494925480[312] = 0.0;
   out_3573439106494925480[313] = 0.0;
   out_3573439106494925480[314] = 0.0;
   out_3573439106494925480[315] = 0.0;
   out_3573439106494925480[316] = 0.0;
   out_3573439106494925480[317] = 0.0;
   out_3573439106494925480[318] = 0.0;
   out_3573439106494925480[319] = 0.0;
   out_3573439106494925480[320] = 0.0;
   out_3573439106494925480[321] = 0.0;
   out_3573439106494925480[322] = 0.0;
   out_3573439106494925480[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_1448694129028724109) {
   out_1448694129028724109[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_1448694129028724109[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_1448694129028724109[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_1448694129028724109[3] = dt*state[12] + state[3];
   out_1448694129028724109[4] = dt*state[13] + state[4];
   out_1448694129028724109[5] = dt*state[14] + state[5];
   out_1448694129028724109[6] = state[6];
   out_1448694129028724109[7] = state[7];
   out_1448694129028724109[8] = state[8];
   out_1448694129028724109[9] = state[9];
   out_1448694129028724109[10] = state[10];
   out_1448694129028724109[11] = state[11];
   out_1448694129028724109[12] = state[12];
   out_1448694129028724109[13] = state[13];
   out_1448694129028724109[14] = state[14];
   out_1448694129028724109[15] = state[15];
   out_1448694129028724109[16] = state[16];
   out_1448694129028724109[17] = state[17];
}
void F_fun(double *state, double dt, double *out_5191980698119314658) {
   out_5191980698119314658[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_5191980698119314658[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_5191980698119314658[2] = 0;
   out_5191980698119314658[3] = 0;
   out_5191980698119314658[4] = 0;
   out_5191980698119314658[5] = 0;
   out_5191980698119314658[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_5191980698119314658[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_5191980698119314658[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_5191980698119314658[9] = 0;
   out_5191980698119314658[10] = 0;
   out_5191980698119314658[11] = 0;
   out_5191980698119314658[12] = 0;
   out_5191980698119314658[13] = 0;
   out_5191980698119314658[14] = 0;
   out_5191980698119314658[15] = 0;
   out_5191980698119314658[16] = 0;
   out_5191980698119314658[17] = 0;
   out_5191980698119314658[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_5191980698119314658[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_5191980698119314658[20] = 0;
   out_5191980698119314658[21] = 0;
   out_5191980698119314658[22] = 0;
   out_5191980698119314658[23] = 0;
   out_5191980698119314658[24] = 0;
   out_5191980698119314658[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_5191980698119314658[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_5191980698119314658[27] = 0;
   out_5191980698119314658[28] = 0;
   out_5191980698119314658[29] = 0;
   out_5191980698119314658[30] = 0;
   out_5191980698119314658[31] = 0;
   out_5191980698119314658[32] = 0;
   out_5191980698119314658[33] = 0;
   out_5191980698119314658[34] = 0;
   out_5191980698119314658[35] = 0;
   out_5191980698119314658[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_5191980698119314658[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_5191980698119314658[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_5191980698119314658[39] = 0;
   out_5191980698119314658[40] = 0;
   out_5191980698119314658[41] = 0;
   out_5191980698119314658[42] = 0;
   out_5191980698119314658[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_5191980698119314658[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_5191980698119314658[45] = 0;
   out_5191980698119314658[46] = 0;
   out_5191980698119314658[47] = 0;
   out_5191980698119314658[48] = 0;
   out_5191980698119314658[49] = 0;
   out_5191980698119314658[50] = 0;
   out_5191980698119314658[51] = 0;
   out_5191980698119314658[52] = 0;
   out_5191980698119314658[53] = 0;
   out_5191980698119314658[54] = 0;
   out_5191980698119314658[55] = 0;
   out_5191980698119314658[56] = 0;
   out_5191980698119314658[57] = 1;
   out_5191980698119314658[58] = 0;
   out_5191980698119314658[59] = 0;
   out_5191980698119314658[60] = 0;
   out_5191980698119314658[61] = 0;
   out_5191980698119314658[62] = 0;
   out_5191980698119314658[63] = 0;
   out_5191980698119314658[64] = 0;
   out_5191980698119314658[65] = 0;
   out_5191980698119314658[66] = dt;
   out_5191980698119314658[67] = 0;
   out_5191980698119314658[68] = 0;
   out_5191980698119314658[69] = 0;
   out_5191980698119314658[70] = 0;
   out_5191980698119314658[71] = 0;
   out_5191980698119314658[72] = 0;
   out_5191980698119314658[73] = 0;
   out_5191980698119314658[74] = 0;
   out_5191980698119314658[75] = 0;
   out_5191980698119314658[76] = 1;
   out_5191980698119314658[77] = 0;
   out_5191980698119314658[78] = 0;
   out_5191980698119314658[79] = 0;
   out_5191980698119314658[80] = 0;
   out_5191980698119314658[81] = 0;
   out_5191980698119314658[82] = 0;
   out_5191980698119314658[83] = 0;
   out_5191980698119314658[84] = 0;
   out_5191980698119314658[85] = dt;
   out_5191980698119314658[86] = 0;
   out_5191980698119314658[87] = 0;
   out_5191980698119314658[88] = 0;
   out_5191980698119314658[89] = 0;
   out_5191980698119314658[90] = 0;
   out_5191980698119314658[91] = 0;
   out_5191980698119314658[92] = 0;
   out_5191980698119314658[93] = 0;
   out_5191980698119314658[94] = 0;
   out_5191980698119314658[95] = 1;
   out_5191980698119314658[96] = 0;
   out_5191980698119314658[97] = 0;
   out_5191980698119314658[98] = 0;
   out_5191980698119314658[99] = 0;
   out_5191980698119314658[100] = 0;
   out_5191980698119314658[101] = 0;
   out_5191980698119314658[102] = 0;
   out_5191980698119314658[103] = 0;
   out_5191980698119314658[104] = dt;
   out_5191980698119314658[105] = 0;
   out_5191980698119314658[106] = 0;
   out_5191980698119314658[107] = 0;
   out_5191980698119314658[108] = 0;
   out_5191980698119314658[109] = 0;
   out_5191980698119314658[110] = 0;
   out_5191980698119314658[111] = 0;
   out_5191980698119314658[112] = 0;
   out_5191980698119314658[113] = 0;
   out_5191980698119314658[114] = 1;
   out_5191980698119314658[115] = 0;
   out_5191980698119314658[116] = 0;
   out_5191980698119314658[117] = 0;
   out_5191980698119314658[118] = 0;
   out_5191980698119314658[119] = 0;
   out_5191980698119314658[120] = 0;
   out_5191980698119314658[121] = 0;
   out_5191980698119314658[122] = 0;
   out_5191980698119314658[123] = 0;
   out_5191980698119314658[124] = 0;
   out_5191980698119314658[125] = 0;
   out_5191980698119314658[126] = 0;
   out_5191980698119314658[127] = 0;
   out_5191980698119314658[128] = 0;
   out_5191980698119314658[129] = 0;
   out_5191980698119314658[130] = 0;
   out_5191980698119314658[131] = 0;
   out_5191980698119314658[132] = 0;
   out_5191980698119314658[133] = 1;
   out_5191980698119314658[134] = 0;
   out_5191980698119314658[135] = 0;
   out_5191980698119314658[136] = 0;
   out_5191980698119314658[137] = 0;
   out_5191980698119314658[138] = 0;
   out_5191980698119314658[139] = 0;
   out_5191980698119314658[140] = 0;
   out_5191980698119314658[141] = 0;
   out_5191980698119314658[142] = 0;
   out_5191980698119314658[143] = 0;
   out_5191980698119314658[144] = 0;
   out_5191980698119314658[145] = 0;
   out_5191980698119314658[146] = 0;
   out_5191980698119314658[147] = 0;
   out_5191980698119314658[148] = 0;
   out_5191980698119314658[149] = 0;
   out_5191980698119314658[150] = 0;
   out_5191980698119314658[151] = 0;
   out_5191980698119314658[152] = 1;
   out_5191980698119314658[153] = 0;
   out_5191980698119314658[154] = 0;
   out_5191980698119314658[155] = 0;
   out_5191980698119314658[156] = 0;
   out_5191980698119314658[157] = 0;
   out_5191980698119314658[158] = 0;
   out_5191980698119314658[159] = 0;
   out_5191980698119314658[160] = 0;
   out_5191980698119314658[161] = 0;
   out_5191980698119314658[162] = 0;
   out_5191980698119314658[163] = 0;
   out_5191980698119314658[164] = 0;
   out_5191980698119314658[165] = 0;
   out_5191980698119314658[166] = 0;
   out_5191980698119314658[167] = 0;
   out_5191980698119314658[168] = 0;
   out_5191980698119314658[169] = 0;
   out_5191980698119314658[170] = 0;
   out_5191980698119314658[171] = 1;
   out_5191980698119314658[172] = 0;
   out_5191980698119314658[173] = 0;
   out_5191980698119314658[174] = 0;
   out_5191980698119314658[175] = 0;
   out_5191980698119314658[176] = 0;
   out_5191980698119314658[177] = 0;
   out_5191980698119314658[178] = 0;
   out_5191980698119314658[179] = 0;
   out_5191980698119314658[180] = 0;
   out_5191980698119314658[181] = 0;
   out_5191980698119314658[182] = 0;
   out_5191980698119314658[183] = 0;
   out_5191980698119314658[184] = 0;
   out_5191980698119314658[185] = 0;
   out_5191980698119314658[186] = 0;
   out_5191980698119314658[187] = 0;
   out_5191980698119314658[188] = 0;
   out_5191980698119314658[189] = 0;
   out_5191980698119314658[190] = 1;
   out_5191980698119314658[191] = 0;
   out_5191980698119314658[192] = 0;
   out_5191980698119314658[193] = 0;
   out_5191980698119314658[194] = 0;
   out_5191980698119314658[195] = 0;
   out_5191980698119314658[196] = 0;
   out_5191980698119314658[197] = 0;
   out_5191980698119314658[198] = 0;
   out_5191980698119314658[199] = 0;
   out_5191980698119314658[200] = 0;
   out_5191980698119314658[201] = 0;
   out_5191980698119314658[202] = 0;
   out_5191980698119314658[203] = 0;
   out_5191980698119314658[204] = 0;
   out_5191980698119314658[205] = 0;
   out_5191980698119314658[206] = 0;
   out_5191980698119314658[207] = 0;
   out_5191980698119314658[208] = 0;
   out_5191980698119314658[209] = 1;
   out_5191980698119314658[210] = 0;
   out_5191980698119314658[211] = 0;
   out_5191980698119314658[212] = 0;
   out_5191980698119314658[213] = 0;
   out_5191980698119314658[214] = 0;
   out_5191980698119314658[215] = 0;
   out_5191980698119314658[216] = 0;
   out_5191980698119314658[217] = 0;
   out_5191980698119314658[218] = 0;
   out_5191980698119314658[219] = 0;
   out_5191980698119314658[220] = 0;
   out_5191980698119314658[221] = 0;
   out_5191980698119314658[222] = 0;
   out_5191980698119314658[223] = 0;
   out_5191980698119314658[224] = 0;
   out_5191980698119314658[225] = 0;
   out_5191980698119314658[226] = 0;
   out_5191980698119314658[227] = 0;
   out_5191980698119314658[228] = 1;
   out_5191980698119314658[229] = 0;
   out_5191980698119314658[230] = 0;
   out_5191980698119314658[231] = 0;
   out_5191980698119314658[232] = 0;
   out_5191980698119314658[233] = 0;
   out_5191980698119314658[234] = 0;
   out_5191980698119314658[235] = 0;
   out_5191980698119314658[236] = 0;
   out_5191980698119314658[237] = 0;
   out_5191980698119314658[238] = 0;
   out_5191980698119314658[239] = 0;
   out_5191980698119314658[240] = 0;
   out_5191980698119314658[241] = 0;
   out_5191980698119314658[242] = 0;
   out_5191980698119314658[243] = 0;
   out_5191980698119314658[244] = 0;
   out_5191980698119314658[245] = 0;
   out_5191980698119314658[246] = 0;
   out_5191980698119314658[247] = 1;
   out_5191980698119314658[248] = 0;
   out_5191980698119314658[249] = 0;
   out_5191980698119314658[250] = 0;
   out_5191980698119314658[251] = 0;
   out_5191980698119314658[252] = 0;
   out_5191980698119314658[253] = 0;
   out_5191980698119314658[254] = 0;
   out_5191980698119314658[255] = 0;
   out_5191980698119314658[256] = 0;
   out_5191980698119314658[257] = 0;
   out_5191980698119314658[258] = 0;
   out_5191980698119314658[259] = 0;
   out_5191980698119314658[260] = 0;
   out_5191980698119314658[261] = 0;
   out_5191980698119314658[262] = 0;
   out_5191980698119314658[263] = 0;
   out_5191980698119314658[264] = 0;
   out_5191980698119314658[265] = 0;
   out_5191980698119314658[266] = 1;
   out_5191980698119314658[267] = 0;
   out_5191980698119314658[268] = 0;
   out_5191980698119314658[269] = 0;
   out_5191980698119314658[270] = 0;
   out_5191980698119314658[271] = 0;
   out_5191980698119314658[272] = 0;
   out_5191980698119314658[273] = 0;
   out_5191980698119314658[274] = 0;
   out_5191980698119314658[275] = 0;
   out_5191980698119314658[276] = 0;
   out_5191980698119314658[277] = 0;
   out_5191980698119314658[278] = 0;
   out_5191980698119314658[279] = 0;
   out_5191980698119314658[280] = 0;
   out_5191980698119314658[281] = 0;
   out_5191980698119314658[282] = 0;
   out_5191980698119314658[283] = 0;
   out_5191980698119314658[284] = 0;
   out_5191980698119314658[285] = 1;
   out_5191980698119314658[286] = 0;
   out_5191980698119314658[287] = 0;
   out_5191980698119314658[288] = 0;
   out_5191980698119314658[289] = 0;
   out_5191980698119314658[290] = 0;
   out_5191980698119314658[291] = 0;
   out_5191980698119314658[292] = 0;
   out_5191980698119314658[293] = 0;
   out_5191980698119314658[294] = 0;
   out_5191980698119314658[295] = 0;
   out_5191980698119314658[296] = 0;
   out_5191980698119314658[297] = 0;
   out_5191980698119314658[298] = 0;
   out_5191980698119314658[299] = 0;
   out_5191980698119314658[300] = 0;
   out_5191980698119314658[301] = 0;
   out_5191980698119314658[302] = 0;
   out_5191980698119314658[303] = 0;
   out_5191980698119314658[304] = 1;
   out_5191980698119314658[305] = 0;
   out_5191980698119314658[306] = 0;
   out_5191980698119314658[307] = 0;
   out_5191980698119314658[308] = 0;
   out_5191980698119314658[309] = 0;
   out_5191980698119314658[310] = 0;
   out_5191980698119314658[311] = 0;
   out_5191980698119314658[312] = 0;
   out_5191980698119314658[313] = 0;
   out_5191980698119314658[314] = 0;
   out_5191980698119314658[315] = 0;
   out_5191980698119314658[316] = 0;
   out_5191980698119314658[317] = 0;
   out_5191980698119314658[318] = 0;
   out_5191980698119314658[319] = 0;
   out_5191980698119314658[320] = 0;
   out_5191980698119314658[321] = 0;
   out_5191980698119314658[322] = 0;
   out_5191980698119314658[323] = 1;
}
void h_4(double *state, double *unused, double *out_5235289640549259173) {
   out_5235289640549259173[0] = state[6] + state[9];
   out_5235289640549259173[1] = state[7] + state[10];
   out_5235289640549259173[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_2274642700257033241) {
   out_2274642700257033241[0] = 0;
   out_2274642700257033241[1] = 0;
   out_2274642700257033241[2] = 0;
   out_2274642700257033241[3] = 0;
   out_2274642700257033241[4] = 0;
   out_2274642700257033241[5] = 0;
   out_2274642700257033241[6] = 1;
   out_2274642700257033241[7] = 0;
   out_2274642700257033241[8] = 0;
   out_2274642700257033241[9] = 1;
   out_2274642700257033241[10] = 0;
   out_2274642700257033241[11] = 0;
   out_2274642700257033241[12] = 0;
   out_2274642700257033241[13] = 0;
   out_2274642700257033241[14] = 0;
   out_2274642700257033241[15] = 0;
   out_2274642700257033241[16] = 0;
   out_2274642700257033241[17] = 0;
   out_2274642700257033241[18] = 0;
   out_2274642700257033241[19] = 0;
   out_2274642700257033241[20] = 0;
   out_2274642700257033241[21] = 0;
   out_2274642700257033241[22] = 0;
   out_2274642700257033241[23] = 0;
   out_2274642700257033241[24] = 0;
   out_2274642700257033241[25] = 1;
   out_2274642700257033241[26] = 0;
   out_2274642700257033241[27] = 0;
   out_2274642700257033241[28] = 1;
   out_2274642700257033241[29] = 0;
   out_2274642700257033241[30] = 0;
   out_2274642700257033241[31] = 0;
   out_2274642700257033241[32] = 0;
   out_2274642700257033241[33] = 0;
   out_2274642700257033241[34] = 0;
   out_2274642700257033241[35] = 0;
   out_2274642700257033241[36] = 0;
   out_2274642700257033241[37] = 0;
   out_2274642700257033241[38] = 0;
   out_2274642700257033241[39] = 0;
   out_2274642700257033241[40] = 0;
   out_2274642700257033241[41] = 0;
   out_2274642700257033241[42] = 0;
   out_2274642700257033241[43] = 0;
   out_2274642700257033241[44] = 1;
   out_2274642700257033241[45] = 0;
   out_2274642700257033241[46] = 0;
   out_2274642700257033241[47] = 1;
   out_2274642700257033241[48] = 0;
   out_2274642700257033241[49] = 0;
   out_2274642700257033241[50] = 0;
   out_2274642700257033241[51] = 0;
   out_2274642700257033241[52] = 0;
   out_2274642700257033241[53] = 0;
}
void h_10(double *state, double *unused, double *out_5091836047882356691) {
   out_5091836047882356691[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_5091836047882356691[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_5091836047882356691[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_4490205013045843640) {
   out_4490205013045843640[0] = 0;
   out_4490205013045843640[1] = 9.8100000000000005*cos(state[1]);
   out_4490205013045843640[2] = 0;
   out_4490205013045843640[3] = 0;
   out_4490205013045843640[4] = -state[8];
   out_4490205013045843640[5] = state[7];
   out_4490205013045843640[6] = 0;
   out_4490205013045843640[7] = state[5];
   out_4490205013045843640[8] = -state[4];
   out_4490205013045843640[9] = 0;
   out_4490205013045843640[10] = 0;
   out_4490205013045843640[11] = 0;
   out_4490205013045843640[12] = 1;
   out_4490205013045843640[13] = 0;
   out_4490205013045843640[14] = 0;
   out_4490205013045843640[15] = 1;
   out_4490205013045843640[16] = 0;
   out_4490205013045843640[17] = 0;
   out_4490205013045843640[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_4490205013045843640[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_4490205013045843640[20] = 0;
   out_4490205013045843640[21] = state[8];
   out_4490205013045843640[22] = 0;
   out_4490205013045843640[23] = -state[6];
   out_4490205013045843640[24] = -state[5];
   out_4490205013045843640[25] = 0;
   out_4490205013045843640[26] = state[3];
   out_4490205013045843640[27] = 0;
   out_4490205013045843640[28] = 0;
   out_4490205013045843640[29] = 0;
   out_4490205013045843640[30] = 0;
   out_4490205013045843640[31] = 1;
   out_4490205013045843640[32] = 0;
   out_4490205013045843640[33] = 0;
   out_4490205013045843640[34] = 1;
   out_4490205013045843640[35] = 0;
   out_4490205013045843640[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_4490205013045843640[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_4490205013045843640[38] = 0;
   out_4490205013045843640[39] = -state[7];
   out_4490205013045843640[40] = state[6];
   out_4490205013045843640[41] = 0;
   out_4490205013045843640[42] = state[4];
   out_4490205013045843640[43] = -state[3];
   out_4490205013045843640[44] = 0;
   out_4490205013045843640[45] = 0;
   out_4490205013045843640[46] = 0;
   out_4490205013045843640[47] = 0;
   out_4490205013045843640[48] = 0;
   out_4490205013045843640[49] = 0;
   out_4490205013045843640[50] = 1;
   out_4490205013045843640[51] = 0;
   out_4490205013045843640[52] = 0;
   out_4490205013045843640[53] = 1;
}
void h_13(double *state, double *unused, double *out_5979871826325457693) {
   out_5979871826325457693[0] = state[3];
   out_5979871826325457693[1] = state[4];
   out_5979871826325457693[2] = state[5];
}
void H_13(double *state, double *unused, double *out_937631125075299560) {
   out_937631125075299560[0] = 0;
   out_937631125075299560[1] = 0;
   out_937631125075299560[2] = 0;
   out_937631125075299560[3] = 1;
   out_937631125075299560[4] = 0;
   out_937631125075299560[5] = 0;
   out_937631125075299560[6] = 0;
   out_937631125075299560[7] = 0;
   out_937631125075299560[8] = 0;
   out_937631125075299560[9] = 0;
   out_937631125075299560[10] = 0;
   out_937631125075299560[11] = 0;
   out_937631125075299560[12] = 0;
   out_937631125075299560[13] = 0;
   out_937631125075299560[14] = 0;
   out_937631125075299560[15] = 0;
   out_937631125075299560[16] = 0;
   out_937631125075299560[17] = 0;
   out_937631125075299560[18] = 0;
   out_937631125075299560[19] = 0;
   out_937631125075299560[20] = 0;
   out_937631125075299560[21] = 0;
   out_937631125075299560[22] = 1;
   out_937631125075299560[23] = 0;
   out_937631125075299560[24] = 0;
   out_937631125075299560[25] = 0;
   out_937631125075299560[26] = 0;
   out_937631125075299560[27] = 0;
   out_937631125075299560[28] = 0;
   out_937631125075299560[29] = 0;
   out_937631125075299560[30] = 0;
   out_937631125075299560[31] = 0;
   out_937631125075299560[32] = 0;
   out_937631125075299560[33] = 0;
   out_937631125075299560[34] = 0;
   out_937631125075299560[35] = 0;
   out_937631125075299560[36] = 0;
   out_937631125075299560[37] = 0;
   out_937631125075299560[38] = 0;
   out_937631125075299560[39] = 0;
   out_937631125075299560[40] = 0;
   out_937631125075299560[41] = 1;
   out_937631125075299560[42] = 0;
   out_937631125075299560[43] = 0;
   out_937631125075299560[44] = 0;
   out_937631125075299560[45] = 0;
   out_937631125075299560[46] = 0;
   out_937631125075299560[47] = 0;
   out_937631125075299560[48] = 0;
   out_937631125075299560[49] = 0;
   out_937631125075299560[50] = 0;
   out_937631125075299560[51] = 0;
   out_937631125075299560[52] = 0;
   out_937631125075299560[53] = 0;
}
void h_14(double *state, double *unused, double *out_1085876952354499248) {
   out_1085876952354499248[0] = state[6];
   out_1085876952354499248[1] = state[7];
   out_1085876952354499248[2] = state[8];
}
void H_14(double *state, double *unused, double *out_2709759226901916840) {
   out_2709759226901916840[0] = 0;
   out_2709759226901916840[1] = 0;
   out_2709759226901916840[2] = 0;
   out_2709759226901916840[3] = 0;
   out_2709759226901916840[4] = 0;
   out_2709759226901916840[5] = 0;
   out_2709759226901916840[6] = 1;
   out_2709759226901916840[7] = 0;
   out_2709759226901916840[8] = 0;
   out_2709759226901916840[9] = 0;
   out_2709759226901916840[10] = 0;
   out_2709759226901916840[11] = 0;
   out_2709759226901916840[12] = 0;
   out_2709759226901916840[13] = 0;
   out_2709759226901916840[14] = 0;
   out_2709759226901916840[15] = 0;
   out_2709759226901916840[16] = 0;
   out_2709759226901916840[17] = 0;
   out_2709759226901916840[18] = 0;
   out_2709759226901916840[19] = 0;
   out_2709759226901916840[20] = 0;
   out_2709759226901916840[21] = 0;
   out_2709759226901916840[22] = 0;
   out_2709759226901916840[23] = 0;
   out_2709759226901916840[24] = 0;
   out_2709759226901916840[25] = 1;
   out_2709759226901916840[26] = 0;
   out_2709759226901916840[27] = 0;
   out_2709759226901916840[28] = 0;
   out_2709759226901916840[29] = 0;
   out_2709759226901916840[30] = 0;
   out_2709759226901916840[31] = 0;
   out_2709759226901916840[32] = 0;
   out_2709759226901916840[33] = 0;
   out_2709759226901916840[34] = 0;
   out_2709759226901916840[35] = 0;
   out_2709759226901916840[36] = 0;
   out_2709759226901916840[37] = 0;
   out_2709759226901916840[38] = 0;
   out_2709759226901916840[39] = 0;
   out_2709759226901916840[40] = 0;
   out_2709759226901916840[41] = 0;
   out_2709759226901916840[42] = 0;
   out_2709759226901916840[43] = 0;
   out_2709759226901916840[44] = 1;
   out_2709759226901916840[45] = 0;
   out_2709759226901916840[46] = 0;
   out_2709759226901916840[47] = 0;
   out_2709759226901916840[48] = 0;
   out_2709759226901916840[49] = 0;
   out_2709759226901916840[50] = 0;
   out_2709759226901916840[51] = 0;
   out_2709759226901916840[52] = 0;
   out_2709759226901916840[53] = 0;
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

void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<3, 3, 0>(in_x, in_P, h_4, H_4, NULL, in_z, in_R, in_ea, MAHA_THRESH_4);
}
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<3, 3, 0>(in_x, in_P, h_10, H_10, NULL, in_z, in_R, in_ea, MAHA_THRESH_10);
}
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<3, 3, 0>(in_x, in_P, h_13, H_13, NULL, in_z, in_R, in_ea, MAHA_THRESH_13);
}
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<3, 3, 0>(in_x, in_P, h_14, H_14, NULL, in_z, in_R, in_ea, MAHA_THRESH_14);
}
void pose_err_fun(double *nom_x, double *delta_x, double *out_2613652145363001248) {
  err_fun(nom_x, delta_x, out_2613652145363001248);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_1002934702699052391) {
  inv_err_fun(nom_x, true_x, out_1002934702699052391);
}
void pose_H_mod_fun(double *state, double *out_3573439106494925480) {
  H_mod_fun(state, out_3573439106494925480);
}
void pose_f_fun(double *state, double dt, double *out_1448694129028724109) {
  f_fun(state,  dt, out_1448694129028724109);
}
void pose_F_fun(double *state, double dt, double *out_5191980698119314658) {
  F_fun(state,  dt, out_5191980698119314658);
}
void pose_h_4(double *state, double *unused, double *out_5235289640549259173) {
  h_4(state, unused, out_5235289640549259173);
}
void pose_H_4(double *state, double *unused, double *out_2274642700257033241) {
  H_4(state, unused, out_2274642700257033241);
}
void pose_h_10(double *state, double *unused, double *out_5091836047882356691) {
  h_10(state, unused, out_5091836047882356691);
}
void pose_H_10(double *state, double *unused, double *out_4490205013045843640) {
  H_10(state, unused, out_4490205013045843640);
}
void pose_h_13(double *state, double *unused, double *out_5979871826325457693) {
  h_13(state, unused, out_5979871826325457693);
}
void pose_H_13(double *state, double *unused, double *out_937631125075299560) {
  H_13(state, unused, out_937631125075299560);
}
void pose_h_14(double *state, double *unused, double *out_1085876952354499248) {
  h_14(state, unused, out_1085876952354499248);
}
void pose_H_14(double *state, double *unused, double *out_2709759226901916840) {
  H_14(state, unused, out_2709759226901916840);
}
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt) {
  predict(in_x, in_P, in_Q, dt);
}
}

const EKF pose = {
  .name = "pose",
  .kinds = { 4, 10, 13, 14 },
  .feature_kinds = {  },
  .f_fun = pose_f_fun,
  .F_fun = pose_F_fun,
  .err_fun = pose_err_fun,
  .inv_err_fun = pose_inv_err_fun,
  .H_mod_fun = pose_H_mod_fun,
  .predict = pose_predict,
  .hs = {
    { 4, pose_h_4 },
    { 10, pose_h_10 },
    { 13, pose_h_13 },
    { 14, pose_h_14 },
  },
  .Hs = {
    { 4, pose_H_4 },
    { 10, pose_H_10 },
    { 13, pose_H_13 },
    { 14, pose_H_14 },
  },
  .updates = {
    { 4, pose_update_4 },
    { 10, pose_update_10 },
    { 13, pose_update_13 },
    { 14, pose_update_14 },
  },
  .Hes = {
  },
  .sets = {
  },
  .extra_routines = {
  },
};

ekf_lib_init(pose)
