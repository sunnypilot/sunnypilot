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
void err_fun(double *nom_x, double *delta_x, double *out_5717304809118492246) {
   out_5717304809118492246[0] = delta_x[0] + nom_x[0];
   out_5717304809118492246[1] = delta_x[1] + nom_x[1];
   out_5717304809118492246[2] = delta_x[2] + nom_x[2];
   out_5717304809118492246[3] = delta_x[3] + nom_x[3];
   out_5717304809118492246[4] = delta_x[4] + nom_x[4];
   out_5717304809118492246[5] = delta_x[5] + nom_x[5];
   out_5717304809118492246[6] = delta_x[6] + nom_x[6];
   out_5717304809118492246[7] = delta_x[7] + nom_x[7];
   out_5717304809118492246[8] = delta_x[8] + nom_x[8];
   out_5717304809118492246[9] = delta_x[9] + nom_x[9];
   out_5717304809118492246[10] = delta_x[10] + nom_x[10];
   out_5717304809118492246[11] = delta_x[11] + nom_x[11];
   out_5717304809118492246[12] = delta_x[12] + nom_x[12];
   out_5717304809118492246[13] = delta_x[13] + nom_x[13];
   out_5717304809118492246[14] = delta_x[14] + nom_x[14];
   out_5717304809118492246[15] = delta_x[15] + nom_x[15];
   out_5717304809118492246[16] = delta_x[16] + nom_x[16];
   out_5717304809118492246[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_1297679808783662883) {
   out_1297679808783662883[0] = -nom_x[0] + true_x[0];
   out_1297679808783662883[1] = -nom_x[1] + true_x[1];
   out_1297679808783662883[2] = -nom_x[2] + true_x[2];
   out_1297679808783662883[3] = -nom_x[3] + true_x[3];
   out_1297679808783662883[4] = -nom_x[4] + true_x[4];
   out_1297679808783662883[5] = -nom_x[5] + true_x[5];
   out_1297679808783662883[6] = -nom_x[6] + true_x[6];
   out_1297679808783662883[7] = -nom_x[7] + true_x[7];
   out_1297679808783662883[8] = -nom_x[8] + true_x[8];
   out_1297679808783662883[9] = -nom_x[9] + true_x[9];
   out_1297679808783662883[10] = -nom_x[10] + true_x[10];
   out_1297679808783662883[11] = -nom_x[11] + true_x[11];
   out_1297679808783662883[12] = -nom_x[12] + true_x[12];
   out_1297679808783662883[13] = -nom_x[13] + true_x[13];
   out_1297679808783662883[14] = -nom_x[14] + true_x[14];
   out_1297679808783662883[15] = -nom_x[15] + true_x[15];
   out_1297679808783662883[16] = -nom_x[16] + true_x[16];
   out_1297679808783662883[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_173021604743855246) {
   out_173021604743855246[0] = 1.0;
   out_173021604743855246[1] = 0.0;
   out_173021604743855246[2] = 0.0;
   out_173021604743855246[3] = 0.0;
   out_173021604743855246[4] = 0.0;
   out_173021604743855246[5] = 0.0;
   out_173021604743855246[6] = 0.0;
   out_173021604743855246[7] = 0.0;
   out_173021604743855246[8] = 0.0;
   out_173021604743855246[9] = 0.0;
   out_173021604743855246[10] = 0.0;
   out_173021604743855246[11] = 0.0;
   out_173021604743855246[12] = 0.0;
   out_173021604743855246[13] = 0.0;
   out_173021604743855246[14] = 0.0;
   out_173021604743855246[15] = 0.0;
   out_173021604743855246[16] = 0.0;
   out_173021604743855246[17] = 0.0;
   out_173021604743855246[18] = 0.0;
   out_173021604743855246[19] = 1.0;
   out_173021604743855246[20] = 0.0;
   out_173021604743855246[21] = 0.0;
   out_173021604743855246[22] = 0.0;
   out_173021604743855246[23] = 0.0;
   out_173021604743855246[24] = 0.0;
   out_173021604743855246[25] = 0.0;
   out_173021604743855246[26] = 0.0;
   out_173021604743855246[27] = 0.0;
   out_173021604743855246[28] = 0.0;
   out_173021604743855246[29] = 0.0;
   out_173021604743855246[30] = 0.0;
   out_173021604743855246[31] = 0.0;
   out_173021604743855246[32] = 0.0;
   out_173021604743855246[33] = 0.0;
   out_173021604743855246[34] = 0.0;
   out_173021604743855246[35] = 0.0;
   out_173021604743855246[36] = 0.0;
   out_173021604743855246[37] = 0.0;
   out_173021604743855246[38] = 1.0;
   out_173021604743855246[39] = 0.0;
   out_173021604743855246[40] = 0.0;
   out_173021604743855246[41] = 0.0;
   out_173021604743855246[42] = 0.0;
   out_173021604743855246[43] = 0.0;
   out_173021604743855246[44] = 0.0;
   out_173021604743855246[45] = 0.0;
   out_173021604743855246[46] = 0.0;
   out_173021604743855246[47] = 0.0;
   out_173021604743855246[48] = 0.0;
   out_173021604743855246[49] = 0.0;
   out_173021604743855246[50] = 0.0;
   out_173021604743855246[51] = 0.0;
   out_173021604743855246[52] = 0.0;
   out_173021604743855246[53] = 0.0;
   out_173021604743855246[54] = 0.0;
   out_173021604743855246[55] = 0.0;
   out_173021604743855246[56] = 0.0;
   out_173021604743855246[57] = 1.0;
   out_173021604743855246[58] = 0.0;
   out_173021604743855246[59] = 0.0;
   out_173021604743855246[60] = 0.0;
   out_173021604743855246[61] = 0.0;
   out_173021604743855246[62] = 0.0;
   out_173021604743855246[63] = 0.0;
   out_173021604743855246[64] = 0.0;
   out_173021604743855246[65] = 0.0;
   out_173021604743855246[66] = 0.0;
   out_173021604743855246[67] = 0.0;
   out_173021604743855246[68] = 0.0;
   out_173021604743855246[69] = 0.0;
   out_173021604743855246[70] = 0.0;
   out_173021604743855246[71] = 0.0;
   out_173021604743855246[72] = 0.0;
   out_173021604743855246[73] = 0.0;
   out_173021604743855246[74] = 0.0;
   out_173021604743855246[75] = 0.0;
   out_173021604743855246[76] = 1.0;
   out_173021604743855246[77] = 0.0;
   out_173021604743855246[78] = 0.0;
   out_173021604743855246[79] = 0.0;
   out_173021604743855246[80] = 0.0;
   out_173021604743855246[81] = 0.0;
   out_173021604743855246[82] = 0.0;
   out_173021604743855246[83] = 0.0;
   out_173021604743855246[84] = 0.0;
   out_173021604743855246[85] = 0.0;
   out_173021604743855246[86] = 0.0;
   out_173021604743855246[87] = 0.0;
   out_173021604743855246[88] = 0.0;
   out_173021604743855246[89] = 0.0;
   out_173021604743855246[90] = 0.0;
   out_173021604743855246[91] = 0.0;
   out_173021604743855246[92] = 0.0;
   out_173021604743855246[93] = 0.0;
   out_173021604743855246[94] = 0.0;
   out_173021604743855246[95] = 1.0;
   out_173021604743855246[96] = 0.0;
   out_173021604743855246[97] = 0.0;
   out_173021604743855246[98] = 0.0;
   out_173021604743855246[99] = 0.0;
   out_173021604743855246[100] = 0.0;
   out_173021604743855246[101] = 0.0;
   out_173021604743855246[102] = 0.0;
   out_173021604743855246[103] = 0.0;
   out_173021604743855246[104] = 0.0;
   out_173021604743855246[105] = 0.0;
   out_173021604743855246[106] = 0.0;
   out_173021604743855246[107] = 0.0;
   out_173021604743855246[108] = 0.0;
   out_173021604743855246[109] = 0.0;
   out_173021604743855246[110] = 0.0;
   out_173021604743855246[111] = 0.0;
   out_173021604743855246[112] = 0.0;
   out_173021604743855246[113] = 0.0;
   out_173021604743855246[114] = 1.0;
   out_173021604743855246[115] = 0.0;
   out_173021604743855246[116] = 0.0;
   out_173021604743855246[117] = 0.0;
   out_173021604743855246[118] = 0.0;
   out_173021604743855246[119] = 0.0;
   out_173021604743855246[120] = 0.0;
   out_173021604743855246[121] = 0.0;
   out_173021604743855246[122] = 0.0;
   out_173021604743855246[123] = 0.0;
   out_173021604743855246[124] = 0.0;
   out_173021604743855246[125] = 0.0;
   out_173021604743855246[126] = 0.0;
   out_173021604743855246[127] = 0.0;
   out_173021604743855246[128] = 0.0;
   out_173021604743855246[129] = 0.0;
   out_173021604743855246[130] = 0.0;
   out_173021604743855246[131] = 0.0;
   out_173021604743855246[132] = 0.0;
   out_173021604743855246[133] = 1.0;
   out_173021604743855246[134] = 0.0;
   out_173021604743855246[135] = 0.0;
   out_173021604743855246[136] = 0.0;
   out_173021604743855246[137] = 0.0;
   out_173021604743855246[138] = 0.0;
   out_173021604743855246[139] = 0.0;
   out_173021604743855246[140] = 0.0;
   out_173021604743855246[141] = 0.0;
   out_173021604743855246[142] = 0.0;
   out_173021604743855246[143] = 0.0;
   out_173021604743855246[144] = 0.0;
   out_173021604743855246[145] = 0.0;
   out_173021604743855246[146] = 0.0;
   out_173021604743855246[147] = 0.0;
   out_173021604743855246[148] = 0.0;
   out_173021604743855246[149] = 0.0;
   out_173021604743855246[150] = 0.0;
   out_173021604743855246[151] = 0.0;
   out_173021604743855246[152] = 1.0;
   out_173021604743855246[153] = 0.0;
   out_173021604743855246[154] = 0.0;
   out_173021604743855246[155] = 0.0;
   out_173021604743855246[156] = 0.0;
   out_173021604743855246[157] = 0.0;
   out_173021604743855246[158] = 0.0;
   out_173021604743855246[159] = 0.0;
   out_173021604743855246[160] = 0.0;
   out_173021604743855246[161] = 0.0;
   out_173021604743855246[162] = 0.0;
   out_173021604743855246[163] = 0.0;
   out_173021604743855246[164] = 0.0;
   out_173021604743855246[165] = 0.0;
   out_173021604743855246[166] = 0.0;
   out_173021604743855246[167] = 0.0;
   out_173021604743855246[168] = 0.0;
   out_173021604743855246[169] = 0.0;
   out_173021604743855246[170] = 0.0;
   out_173021604743855246[171] = 1.0;
   out_173021604743855246[172] = 0.0;
   out_173021604743855246[173] = 0.0;
   out_173021604743855246[174] = 0.0;
   out_173021604743855246[175] = 0.0;
   out_173021604743855246[176] = 0.0;
   out_173021604743855246[177] = 0.0;
   out_173021604743855246[178] = 0.0;
   out_173021604743855246[179] = 0.0;
   out_173021604743855246[180] = 0.0;
   out_173021604743855246[181] = 0.0;
   out_173021604743855246[182] = 0.0;
   out_173021604743855246[183] = 0.0;
   out_173021604743855246[184] = 0.0;
   out_173021604743855246[185] = 0.0;
   out_173021604743855246[186] = 0.0;
   out_173021604743855246[187] = 0.0;
   out_173021604743855246[188] = 0.0;
   out_173021604743855246[189] = 0.0;
   out_173021604743855246[190] = 1.0;
   out_173021604743855246[191] = 0.0;
   out_173021604743855246[192] = 0.0;
   out_173021604743855246[193] = 0.0;
   out_173021604743855246[194] = 0.0;
   out_173021604743855246[195] = 0.0;
   out_173021604743855246[196] = 0.0;
   out_173021604743855246[197] = 0.0;
   out_173021604743855246[198] = 0.0;
   out_173021604743855246[199] = 0.0;
   out_173021604743855246[200] = 0.0;
   out_173021604743855246[201] = 0.0;
   out_173021604743855246[202] = 0.0;
   out_173021604743855246[203] = 0.0;
   out_173021604743855246[204] = 0.0;
   out_173021604743855246[205] = 0.0;
   out_173021604743855246[206] = 0.0;
   out_173021604743855246[207] = 0.0;
   out_173021604743855246[208] = 0.0;
   out_173021604743855246[209] = 1.0;
   out_173021604743855246[210] = 0.0;
   out_173021604743855246[211] = 0.0;
   out_173021604743855246[212] = 0.0;
   out_173021604743855246[213] = 0.0;
   out_173021604743855246[214] = 0.0;
   out_173021604743855246[215] = 0.0;
   out_173021604743855246[216] = 0.0;
   out_173021604743855246[217] = 0.0;
   out_173021604743855246[218] = 0.0;
   out_173021604743855246[219] = 0.0;
   out_173021604743855246[220] = 0.0;
   out_173021604743855246[221] = 0.0;
   out_173021604743855246[222] = 0.0;
   out_173021604743855246[223] = 0.0;
   out_173021604743855246[224] = 0.0;
   out_173021604743855246[225] = 0.0;
   out_173021604743855246[226] = 0.0;
   out_173021604743855246[227] = 0.0;
   out_173021604743855246[228] = 1.0;
   out_173021604743855246[229] = 0.0;
   out_173021604743855246[230] = 0.0;
   out_173021604743855246[231] = 0.0;
   out_173021604743855246[232] = 0.0;
   out_173021604743855246[233] = 0.0;
   out_173021604743855246[234] = 0.0;
   out_173021604743855246[235] = 0.0;
   out_173021604743855246[236] = 0.0;
   out_173021604743855246[237] = 0.0;
   out_173021604743855246[238] = 0.0;
   out_173021604743855246[239] = 0.0;
   out_173021604743855246[240] = 0.0;
   out_173021604743855246[241] = 0.0;
   out_173021604743855246[242] = 0.0;
   out_173021604743855246[243] = 0.0;
   out_173021604743855246[244] = 0.0;
   out_173021604743855246[245] = 0.0;
   out_173021604743855246[246] = 0.0;
   out_173021604743855246[247] = 1.0;
   out_173021604743855246[248] = 0.0;
   out_173021604743855246[249] = 0.0;
   out_173021604743855246[250] = 0.0;
   out_173021604743855246[251] = 0.0;
   out_173021604743855246[252] = 0.0;
   out_173021604743855246[253] = 0.0;
   out_173021604743855246[254] = 0.0;
   out_173021604743855246[255] = 0.0;
   out_173021604743855246[256] = 0.0;
   out_173021604743855246[257] = 0.0;
   out_173021604743855246[258] = 0.0;
   out_173021604743855246[259] = 0.0;
   out_173021604743855246[260] = 0.0;
   out_173021604743855246[261] = 0.0;
   out_173021604743855246[262] = 0.0;
   out_173021604743855246[263] = 0.0;
   out_173021604743855246[264] = 0.0;
   out_173021604743855246[265] = 0.0;
   out_173021604743855246[266] = 1.0;
   out_173021604743855246[267] = 0.0;
   out_173021604743855246[268] = 0.0;
   out_173021604743855246[269] = 0.0;
   out_173021604743855246[270] = 0.0;
   out_173021604743855246[271] = 0.0;
   out_173021604743855246[272] = 0.0;
   out_173021604743855246[273] = 0.0;
   out_173021604743855246[274] = 0.0;
   out_173021604743855246[275] = 0.0;
   out_173021604743855246[276] = 0.0;
   out_173021604743855246[277] = 0.0;
   out_173021604743855246[278] = 0.0;
   out_173021604743855246[279] = 0.0;
   out_173021604743855246[280] = 0.0;
   out_173021604743855246[281] = 0.0;
   out_173021604743855246[282] = 0.0;
   out_173021604743855246[283] = 0.0;
   out_173021604743855246[284] = 0.0;
   out_173021604743855246[285] = 1.0;
   out_173021604743855246[286] = 0.0;
   out_173021604743855246[287] = 0.0;
   out_173021604743855246[288] = 0.0;
   out_173021604743855246[289] = 0.0;
   out_173021604743855246[290] = 0.0;
   out_173021604743855246[291] = 0.0;
   out_173021604743855246[292] = 0.0;
   out_173021604743855246[293] = 0.0;
   out_173021604743855246[294] = 0.0;
   out_173021604743855246[295] = 0.0;
   out_173021604743855246[296] = 0.0;
   out_173021604743855246[297] = 0.0;
   out_173021604743855246[298] = 0.0;
   out_173021604743855246[299] = 0.0;
   out_173021604743855246[300] = 0.0;
   out_173021604743855246[301] = 0.0;
   out_173021604743855246[302] = 0.0;
   out_173021604743855246[303] = 0.0;
   out_173021604743855246[304] = 1.0;
   out_173021604743855246[305] = 0.0;
   out_173021604743855246[306] = 0.0;
   out_173021604743855246[307] = 0.0;
   out_173021604743855246[308] = 0.0;
   out_173021604743855246[309] = 0.0;
   out_173021604743855246[310] = 0.0;
   out_173021604743855246[311] = 0.0;
   out_173021604743855246[312] = 0.0;
   out_173021604743855246[313] = 0.0;
   out_173021604743855246[314] = 0.0;
   out_173021604743855246[315] = 0.0;
   out_173021604743855246[316] = 0.0;
   out_173021604743855246[317] = 0.0;
   out_173021604743855246[318] = 0.0;
   out_173021604743855246[319] = 0.0;
   out_173021604743855246[320] = 0.0;
   out_173021604743855246[321] = 0.0;
   out_173021604743855246[322] = 0.0;
   out_173021604743855246[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_2557189771328893554) {
   out_2557189771328893554[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_2557189771328893554[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_2557189771328893554[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_2557189771328893554[3] = dt*state[12] + state[3];
   out_2557189771328893554[4] = dt*state[13] + state[4];
   out_2557189771328893554[5] = dt*state[14] + state[5];
   out_2557189771328893554[6] = state[6];
   out_2557189771328893554[7] = state[7];
   out_2557189771328893554[8] = state[8];
   out_2557189771328893554[9] = state[9];
   out_2557189771328893554[10] = state[10];
   out_2557189771328893554[11] = state[11];
   out_2557189771328893554[12] = state[12];
   out_2557189771328893554[13] = state[13];
   out_2557189771328893554[14] = state[14];
   out_2557189771328893554[15] = state[15];
   out_2557189771328893554[16] = state[16];
   out_2557189771328893554[17] = state[17];
}
void F_fun(double *state, double dt, double *out_6231166407570578534) {
   out_6231166407570578534[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_6231166407570578534[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_6231166407570578534[2] = 0;
   out_6231166407570578534[3] = 0;
   out_6231166407570578534[4] = 0;
   out_6231166407570578534[5] = 0;
   out_6231166407570578534[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_6231166407570578534[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_6231166407570578534[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_6231166407570578534[9] = 0;
   out_6231166407570578534[10] = 0;
   out_6231166407570578534[11] = 0;
   out_6231166407570578534[12] = 0;
   out_6231166407570578534[13] = 0;
   out_6231166407570578534[14] = 0;
   out_6231166407570578534[15] = 0;
   out_6231166407570578534[16] = 0;
   out_6231166407570578534[17] = 0;
   out_6231166407570578534[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_6231166407570578534[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_6231166407570578534[20] = 0;
   out_6231166407570578534[21] = 0;
   out_6231166407570578534[22] = 0;
   out_6231166407570578534[23] = 0;
   out_6231166407570578534[24] = 0;
   out_6231166407570578534[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_6231166407570578534[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_6231166407570578534[27] = 0;
   out_6231166407570578534[28] = 0;
   out_6231166407570578534[29] = 0;
   out_6231166407570578534[30] = 0;
   out_6231166407570578534[31] = 0;
   out_6231166407570578534[32] = 0;
   out_6231166407570578534[33] = 0;
   out_6231166407570578534[34] = 0;
   out_6231166407570578534[35] = 0;
   out_6231166407570578534[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_6231166407570578534[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_6231166407570578534[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_6231166407570578534[39] = 0;
   out_6231166407570578534[40] = 0;
   out_6231166407570578534[41] = 0;
   out_6231166407570578534[42] = 0;
   out_6231166407570578534[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_6231166407570578534[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_6231166407570578534[45] = 0;
   out_6231166407570578534[46] = 0;
   out_6231166407570578534[47] = 0;
   out_6231166407570578534[48] = 0;
   out_6231166407570578534[49] = 0;
   out_6231166407570578534[50] = 0;
   out_6231166407570578534[51] = 0;
   out_6231166407570578534[52] = 0;
   out_6231166407570578534[53] = 0;
   out_6231166407570578534[54] = 0;
   out_6231166407570578534[55] = 0;
   out_6231166407570578534[56] = 0;
   out_6231166407570578534[57] = 1;
   out_6231166407570578534[58] = 0;
   out_6231166407570578534[59] = 0;
   out_6231166407570578534[60] = 0;
   out_6231166407570578534[61] = 0;
   out_6231166407570578534[62] = 0;
   out_6231166407570578534[63] = 0;
   out_6231166407570578534[64] = 0;
   out_6231166407570578534[65] = 0;
   out_6231166407570578534[66] = dt;
   out_6231166407570578534[67] = 0;
   out_6231166407570578534[68] = 0;
   out_6231166407570578534[69] = 0;
   out_6231166407570578534[70] = 0;
   out_6231166407570578534[71] = 0;
   out_6231166407570578534[72] = 0;
   out_6231166407570578534[73] = 0;
   out_6231166407570578534[74] = 0;
   out_6231166407570578534[75] = 0;
   out_6231166407570578534[76] = 1;
   out_6231166407570578534[77] = 0;
   out_6231166407570578534[78] = 0;
   out_6231166407570578534[79] = 0;
   out_6231166407570578534[80] = 0;
   out_6231166407570578534[81] = 0;
   out_6231166407570578534[82] = 0;
   out_6231166407570578534[83] = 0;
   out_6231166407570578534[84] = 0;
   out_6231166407570578534[85] = dt;
   out_6231166407570578534[86] = 0;
   out_6231166407570578534[87] = 0;
   out_6231166407570578534[88] = 0;
   out_6231166407570578534[89] = 0;
   out_6231166407570578534[90] = 0;
   out_6231166407570578534[91] = 0;
   out_6231166407570578534[92] = 0;
   out_6231166407570578534[93] = 0;
   out_6231166407570578534[94] = 0;
   out_6231166407570578534[95] = 1;
   out_6231166407570578534[96] = 0;
   out_6231166407570578534[97] = 0;
   out_6231166407570578534[98] = 0;
   out_6231166407570578534[99] = 0;
   out_6231166407570578534[100] = 0;
   out_6231166407570578534[101] = 0;
   out_6231166407570578534[102] = 0;
   out_6231166407570578534[103] = 0;
   out_6231166407570578534[104] = dt;
   out_6231166407570578534[105] = 0;
   out_6231166407570578534[106] = 0;
   out_6231166407570578534[107] = 0;
   out_6231166407570578534[108] = 0;
   out_6231166407570578534[109] = 0;
   out_6231166407570578534[110] = 0;
   out_6231166407570578534[111] = 0;
   out_6231166407570578534[112] = 0;
   out_6231166407570578534[113] = 0;
   out_6231166407570578534[114] = 1;
   out_6231166407570578534[115] = 0;
   out_6231166407570578534[116] = 0;
   out_6231166407570578534[117] = 0;
   out_6231166407570578534[118] = 0;
   out_6231166407570578534[119] = 0;
   out_6231166407570578534[120] = 0;
   out_6231166407570578534[121] = 0;
   out_6231166407570578534[122] = 0;
   out_6231166407570578534[123] = 0;
   out_6231166407570578534[124] = 0;
   out_6231166407570578534[125] = 0;
   out_6231166407570578534[126] = 0;
   out_6231166407570578534[127] = 0;
   out_6231166407570578534[128] = 0;
   out_6231166407570578534[129] = 0;
   out_6231166407570578534[130] = 0;
   out_6231166407570578534[131] = 0;
   out_6231166407570578534[132] = 0;
   out_6231166407570578534[133] = 1;
   out_6231166407570578534[134] = 0;
   out_6231166407570578534[135] = 0;
   out_6231166407570578534[136] = 0;
   out_6231166407570578534[137] = 0;
   out_6231166407570578534[138] = 0;
   out_6231166407570578534[139] = 0;
   out_6231166407570578534[140] = 0;
   out_6231166407570578534[141] = 0;
   out_6231166407570578534[142] = 0;
   out_6231166407570578534[143] = 0;
   out_6231166407570578534[144] = 0;
   out_6231166407570578534[145] = 0;
   out_6231166407570578534[146] = 0;
   out_6231166407570578534[147] = 0;
   out_6231166407570578534[148] = 0;
   out_6231166407570578534[149] = 0;
   out_6231166407570578534[150] = 0;
   out_6231166407570578534[151] = 0;
   out_6231166407570578534[152] = 1;
   out_6231166407570578534[153] = 0;
   out_6231166407570578534[154] = 0;
   out_6231166407570578534[155] = 0;
   out_6231166407570578534[156] = 0;
   out_6231166407570578534[157] = 0;
   out_6231166407570578534[158] = 0;
   out_6231166407570578534[159] = 0;
   out_6231166407570578534[160] = 0;
   out_6231166407570578534[161] = 0;
   out_6231166407570578534[162] = 0;
   out_6231166407570578534[163] = 0;
   out_6231166407570578534[164] = 0;
   out_6231166407570578534[165] = 0;
   out_6231166407570578534[166] = 0;
   out_6231166407570578534[167] = 0;
   out_6231166407570578534[168] = 0;
   out_6231166407570578534[169] = 0;
   out_6231166407570578534[170] = 0;
   out_6231166407570578534[171] = 1;
   out_6231166407570578534[172] = 0;
   out_6231166407570578534[173] = 0;
   out_6231166407570578534[174] = 0;
   out_6231166407570578534[175] = 0;
   out_6231166407570578534[176] = 0;
   out_6231166407570578534[177] = 0;
   out_6231166407570578534[178] = 0;
   out_6231166407570578534[179] = 0;
   out_6231166407570578534[180] = 0;
   out_6231166407570578534[181] = 0;
   out_6231166407570578534[182] = 0;
   out_6231166407570578534[183] = 0;
   out_6231166407570578534[184] = 0;
   out_6231166407570578534[185] = 0;
   out_6231166407570578534[186] = 0;
   out_6231166407570578534[187] = 0;
   out_6231166407570578534[188] = 0;
   out_6231166407570578534[189] = 0;
   out_6231166407570578534[190] = 1;
   out_6231166407570578534[191] = 0;
   out_6231166407570578534[192] = 0;
   out_6231166407570578534[193] = 0;
   out_6231166407570578534[194] = 0;
   out_6231166407570578534[195] = 0;
   out_6231166407570578534[196] = 0;
   out_6231166407570578534[197] = 0;
   out_6231166407570578534[198] = 0;
   out_6231166407570578534[199] = 0;
   out_6231166407570578534[200] = 0;
   out_6231166407570578534[201] = 0;
   out_6231166407570578534[202] = 0;
   out_6231166407570578534[203] = 0;
   out_6231166407570578534[204] = 0;
   out_6231166407570578534[205] = 0;
   out_6231166407570578534[206] = 0;
   out_6231166407570578534[207] = 0;
   out_6231166407570578534[208] = 0;
   out_6231166407570578534[209] = 1;
   out_6231166407570578534[210] = 0;
   out_6231166407570578534[211] = 0;
   out_6231166407570578534[212] = 0;
   out_6231166407570578534[213] = 0;
   out_6231166407570578534[214] = 0;
   out_6231166407570578534[215] = 0;
   out_6231166407570578534[216] = 0;
   out_6231166407570578534[217] = 0;
   out_6231166407570578534[218] = 0;
   out_6231166407570578534[219] = 0;
   out_6231166407570578534[220] = 0;
   out_6231166407570578534[221] = 0;
   out_6231166407570578534[222] = 0;
   out_6231166407570578534[223] = 0;
   out_6231166407570578534[224] = 0;
   out_6231166407570578534[225] = 0;
   out_6231166407570578534[226] = 0;
   out_6231166407570578534[227] = 0;
   out_6231166407570578534[228] = 1;
   out_6231166407570578534[229] = 0;
   out_6231166407570578534[230] = 0;
   out_6231166407570578534[231] = 0;
   out_6231166407570578534[232] = 0;
   out_6231166407570578534[233] = 0;
   out_6231166407570578534[234] = 0;
   out_6231166407570578534[235] = 0;
   out_6231166407570578534[236] = 0;
   out_6231166407570578534[237] = 0;
   out_6231166407570578534[238] = 0;
   out_6231166407570578534[239] = 0;
   out_6231166407570578534[240] = 0;
   out_6231166407570578534[241] = 0;
   out_6231166407570578534[242] = 0;
   out_6231166407570578534[243] = 0;
   out_6231166407570578534[244] = 0;
   out_6231166407570578534[245] = 0;
   out_6231166407570578534[246] = 0;
   out_6231166407570578534[247] = 1;
   out_6231166407570578534[248] = 0;
   out_6231166407570578534[249] = 0;
   out_6231166407570578534[250] = 0;
   out_6231166407570578534[251] = 0;
   out_6231166407570578534[252] = 0;
   out_6231166407570578534[253] = 0;
   out_6231166407570578534[254] = 0;
   out_6231166407570578534[255] = 0;
   out_6231166407570578534[256] = 0;
   out_6231166407570578534[257] = 0;
   out_6231166407570578534[258] = 0;
   out_6231166407570578534[259] = 0;
   out_6231166407570578534[260] = 0;
   out_6231166407570578534[261] = 0;
   out_6231166407570578534[262] = 0;
   out_6231166407570578534[263] = 0;
   out_6231166407570578534[264] = 0;
   out_6231166407570578534[265] = 0;
   out_6231166407570578534[266] = 1;
   out_6231166407570578534[267] = 0;
   out_6231166407570578534[268] = 0;
   out_6231166407570578534[269] = 0;
   out_6231166407570578534[270] = 0;
   out_6231166407570578534[271] = 0;
   out_6231166407570578534[272] = 0;
   out_6231166407570578534[273] = 0;
   out_6231166407570578534[274] = 0;
   out_6231166407570578534[275] = 0;
   out_6231166407570578534[276] = 0;
   out_6231166407570578534[277] = 0;
   out_6231166407570578534[278] = 0;
   out_6231166407570578534[279] = 0;
   out_6231166407570578534[280] = 0;
   out_6231166407570578534[281] = 0;
   out_6231166407570578534[282] = 0;
   out_6231166407570578534[283] = 0;
   out_6231166407570578534[284] = 0;
   out_6231166407570578534[285] = 1;
   out_6231166407570578534[286] = 0;
   out_6231166407570578534[287] = 0;
   out_6231166407570578534[288] = 0;
   out_6231166407570578534[289] = 0;
   out_6231166407570578534[290] = 0;
   out_6231166407570578534[291] = 0;
   out_6231166407570578534[292] = 0;
   out_6231166407570578534[293] = 0;
   out_6231166407570578534[294] = 0;
   out_6231166407570578534[295] = 0;
   out_6231166407570578534[296] = 0;
   out_6231166407570578534[297] = 0;
   out_6231166407570578534[298] = 0;
   out_6231166407570578534[299] = 0;
   out_6231166407570578534[300] = 0;
   out_6231166407570578534[301] = 0;
   out_6231166407570578534[302] = 0;
   out_6231166407570578534[303] = 0;
   out_6231166407570578534[304] = 1;
   out_6231166407570578534[305] = 0;
   out_6231166407570578534[306] = 0;
   out_6231166407570578534[307] = 0;
   out_6231166407570578534[308] = 0;
   out_6231166407570578534[309] = 0;
   out_6231166407570578534[310] = 0;
   out_6231166407570578534[311] = 0;
   out_6231166407570578534[312] = 0;
   out_6231166407570578534[313] = 0;
   out_6231166407570578534[314] = 0;
   out_6231166407570578534[315] = 0;
   out_6231166407570578534[316] = 0;
   out_6231166407570578534[317] = 0;
   out_6231166407570578534[318] = 0;
   out_6231166407570578534[319] = 0;
   out_6231166407570578534[320] = 0;
   out_6231166407570578534[321] = 0;
   out_6231166407570578534[322] = 0;
   out_6231166407570578534[323] = 1;
}
void h_4(double *state, double *unused, double *out_2859924915835927259) {
   out_2859924915835927259[0] = state[6] + state[9];
   out_2859924915835927259[1] = state[7] + state[10];
   out_2859924915835927259[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_8565174627339133892) {
   out_8565174627339133892[0] = 0;
   out_8565174627339133892[1] = 0;
   out_8565174627339133892[2] = 0;
   out_8565174627339133892[3] = 0;
   out_8565174627339133892[4] = 0;
   out_8565174627339133892[5] = 0;
   out_8565174627339133892[6] = 1;
   out_8565174627339133892[7] = 0;
   out_8565174627339133892[8] = 0;
   out_8565174627339133892[9] = 1;
   out_8565174627339133892[10] = 0;
   out_8565174627339133892[11] = 0;
   out_8565174627339133892[12] = 0;
   out_8565174627339133892[13] = 0;
   out_8565174627339133892[14] = 0;
   out_8565174627339133892[15] = 0;
   out_8565174627339133892[16] = 0;
   out_8565174627339133892[17] = 0;
   out_8565174627339133892[18] = 0;
   out_8565174627339133892[19] = 0;
   out_8565174627339133892[20] = 0;
   out_8565174627339133892[21] = 0;
   out_8565174627339133892[22] = 0;
   out_8565174627339133892[23] = 0;
   out_8565174627339133892[24] = 0;
   out_8565174627339133892[25] = 1;
   out_8565174627339133892[26] = 0;
   out_8565174627339133892[27] = 0;
   out_8565174627339133892[28] = 1;
   out_8565174627339133892[29] = 0;
   out_8565174627339133892[30] = 0;
   out_8565174627339133892[31] = 0;
   out_8565174627339133892[32] = 0;
   out_8565174627339133892[33] = 0;
   out_8565174627339133892[34] = 0;
   out_8565174627339133892[35] = 0;
   out_8565174627339133892[36] = 0;
   out_8565174627339133892[37] = 0;
   out_8565174627339133892[38] = 0;
   out_8565174627339133892[39] = 0;
   out_8565174627339133892[40] = 0;
   out_8565174627339133892[41] = 0;
   out_8565174627339133892[42] = 0;
   out_8565174627339133892[43] = 0;
   out_8565174627339133892[44] = 1;
   out_8565174627339133892[45] = 0;
   out_8565174627339133892[46] = 0;
   out_8565174627339133892[47] = 1;
   out_8565174627339133892[48] = 0;
   out_8565174627339133892[49] = 0;
   out_8565174627339133892[50] = 0;
   out_8565174627339133892[51] = 0;
   out_8565174627339133892[52] = 0;
   out_8565174627339133892[53] = 0;
}
void h_10(double *state, double *unused, double *out_2013770797981180213) {
   out_2013770797981180213[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_2013770797981180213[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_2013770797981180213[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_2161437616861568278) {
   out_2161437616861568278[0] = 0;
   out_2161437616861568278[1] = 9.8100000000000005*cos(state[1]);
   out_2161437616861568278[2] = 0;
   out_2161437616861568278[3] = 0;
   out_2161437616861568278[4] = -state[8];
   out_2161437616861568278[5] = state[7];
   out_2161437616861568278[6] = 0;
   out_2161437616861568278[7] = state[5];
   out_2161437616861568278[8] = -state[4];
   out_2161437616861568278[9] = 0;
   out_2161437616861568278[10] = 0;
   out_2161437616861568278[11] = 0;
   out_2161437616861568278[12] = 1;
   out_2161437616861568278[13] = 0;
   out_2161437616861568278[14] = 0;
   out_2161437616861568278[15] = 1;
   out_2161437616861568278[16] = 0;
   out_2161437616861568278[17] = 0;
   out_2161437616861568278[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_2161437616861568278[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_2161437616861568278[20] = 0;
   out_2161437616861568278[21] = state[8];
   out_2161437616861568278[22] = 0;
   out_2161437616861568278[23] = -state[6];
   out_2161437616861568278[24] = -state[5];
   out_2161437616861568278[25] = 0;
   out_2161437616861568278[26] = state[3];
   out_2161437616861568278[27] = 0;
   out_2161437616861568278[28] = 0;
   out_2161437616861568278[29] = 0;
   out_2161437616861568278[30] = 0;
   out_2161437616861568278[31] = 1;
   out_2161437616861568278[32] = 0;
   out_2161437616861568278[33] = 0;
   out_2161437616861568278[34] = 1;
   out_2161437616861568278[35] = 0;
   out_2161437616861568278[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_2161437616861568278[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_2161437616861568278[38] = 0;
   out_2161437616861568278[39] = -state[7];
   out_2161437616861568278[40] = state[6];
   out_2161437616861568278[41] = 0;
   out_2161437616861568278[42] = state[4];
   out_2161437616861568278[43] = -state[3];
   out_2161437616861568278[44] = 0;
   out_2161437616861568278[45] = 0;
   out_2161437616861568278[46] = 0;
   out_2161437616861568278[47] = 0;
   out_2161437616861568278[48] = 0;
   out_2161437616861568278[49] = 0;
   out_2161437616861568278[50] = 1;
   out_2161437616861568278[51] = 0;
   out_2161437616861568278[52] = 0;
   out_2161437616861568278[53] = 1;
}
void h_13(double *state, double *unused, double *out_7197851880815921934) {
   out_7197851880815921934[0] = state[3];
   out_7197851880815921934[1] = state[4];
   out_7197851880815921934[2] = state[5];
}
void H_13(double *state, double *unused, double *out_6669295621038084923) {
   out_6669295621038084923[0] = 0;
   out_6669295621038084923[1] = 0;
   out_6669295621038084923[2] = 0;
   out_6669295621038084923[3] = 1;
   out_6669295621038084923[4] = 0;
   out_6669295621038084923[5] = 0;
   out_6669295621038084923[6] = 0;
   out_6669295621038084923[7] = 0;
   out_6669295621038084923[8] = 0;
   out_6669295621038084923[9] = 0;
   out_6669295621038084923[10] = 0;
   out_6669295621038084923[11] = 0;
   out_6669295621038084923[12] = 0;
   out_6669295621038084923[13] = 0;
   out_6669295621038084923[14] = 0;
   out_6669295621038084923[15] = 0;
   out_6669295621038084923[16] = 0;
   out_6669295621038084923[17] = 0;
   out_6669295621038084923[18] = 0;
   out_6669295621038084923[19] = 0;
   out_6669295621038084923[20] = 0;
   out_6669295621038084923[21] = 0;
   out_6669295621038084923[22] = 1;
   out_6669295621038084923[23] = 0;
   out_6669295621038084923[24] = 0;
   out_6669295621038084923[25] = 0;
   out_6669295621038084923[26] = 0;
   out_6669295621038084923[27] = 0;
   out_6669295621038084923[28] = 0;
   out_6669295621038084923[29] = 0;
   out_6669295621038084923[30] = 0;
   out_6669295621038084923[31] = 0;
   out_6669295621038084923[32] = 0;
   out_6669295621038084923[33] = 0;
   out_6669295621038084923[34] = 0;
   out_6669295621038084923[35] = 0;
   out_6669295621038084923[36] = 0;
   out_6669295621038084923[37] = 0;
   out_6669295621038084923[38] = 0;
   out_6669295621038084923[39] = 0;
   out_6669295621038084923[40] = 0;
   out_6669295621038084923[41] = 1;
   out_6669295621038084923[42] = 0;
   out_6669295621038084923[43] = 0;
   out_6669295621038084923[44] = 0;
   out_6669295621038084923[45] = 0;
   out_6669295621038084923[46] = 0;
   out_6669295621038084923[47] = 0;
   out_6669295621038084923[48] = 0;
   out_6669295621038084923[49] = 0;
   out_6669295621038084923[50] = 0;
   out_6669295621038084923[51] = 0;
   out_6669295621038084923[52] = 0;
   out_6669295621038084923[53] = 0;
}
void h_14(double *state, double *unused, double *out_1386181666946440377) {
   out_1386181666946440377[0] = state[6];
   out_1386181666946440377[1] = state[7];
   out_1386181666946440377[2] = state[8];
}
void H_14(double *state, double *unused, double *out_8130058100694250293) {
   out_8130058100694250293[0] = 0;
   out_8130058100694250293[1] = 0;
   out_8130058100694250293[2] = 0;
   out_8130058100694250293[3] = 0;
   out_8130058100694250293[4] = 0;
   out_8130058100694250293[5] = 0;
   out_8130058100694250293[6] = 1;
   out_8130058100694250293[7] = 0;
   out_8130058100694250293[8] = 0;
   out_8130058100694250293[9] = 0;
   out_8130058100694250293[10] = 0;
   out_8130058100694250293[11] = 0;
   out_8130058100694250293[12] = 0;
   out_8130058100694250293[13] = 0;
   out_8130058100694250293[14] = 0;
   out_8130058100694250293[15] = 0;
   out_8130058100694250293[16] = 0;
   out_8130058100694250293[17] = 0;
   out_8130058100694250293[18] = 0;
   out_8130058100694250293[19] = 0;
   out_8130058100694250293[20] = 0;
   out_8130058100694250293[21] = 0;
   out_8130058100694250293[22] = 0;
   out_8130058100694250293[23] = 0;
   out_8130058100694250293[24] = 0;
   out_8130058100694250293[25] = 1;
   out_8130058100694250293[26] = 0;
   out_8130058100694250293[27] = 0;
   out_8130058100694250293[28] = 0;
   out_8130058100694250293[29] = 0;
   out_8130058100694250293[30] = 0;
   out_8130058100694250293[31] = 0;
   out_8130058100694250293[32] = 0;
   out_8130058100694250293[33] = 0;
   out_8130058100694250293[34] = 0;
   out_8130058100694250293[35] = 0;
   out_8130058100694250293[36] = 0;
   out_8130058100694250293[37] = 0;
   out_8130058100694250293[38] = 0;
   out_8130058100694250293[39] = 0;
   out_8130058100694250293[40] = 0;
   out_8130058100694250293[41] = 0;
   out_8130058100694250293[42] = 0;
   out_8130058100694250293[43] = 0;
   out_8130058100694250293[44] = 1;
   out_8130058100694250293[45] = 0;
   out_8130058100694250293[46] = 0;
   out_8130058100694250293[47] = 0;
   out_8130058100694250293[48] = 0;
   out_8130058100694250293[49] = 0;
   out_8130058100694250293[50] = 0;
   out_8130058100694250293[51] = 0;
   out_8130058100694250293[52] = 0;
   out_8130058100694250293[53] = 0;
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
void pose_err_fun(double *nom_x, double *delta_x, double *out_5717304809118492246) {
  err_fun(nom_x, delta_x, out_5717304809118492246);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_1297679808783662883) {
  inv_err_fun(nom_x, true_x, out_1297679808783662883);
}
void pose_H_mod_fun(double *state, double *out_173021604743855246) {
  H_mod_fun(state, out_173021604743855246);
}
void pose_f_fun(double *state, double dt, double *out_2557189771328893554) {
  f_fun(state,  dt, out_2557189771328893554);
}
void pose_F_fun(double *state, double dt, double *out_6231166407570578534) {
  F_fun(state,  dt, out_6231166407570578534);
}
void pose_h_4(double *state, double *unused, double *out_2859924915835927259) {
  h_4(state, unused, out_2859924915835927259);
}
void pose_H_4(double *state, double *unused, double *out_8565174627339133892) {
  H_4(state, unused, out_8565174627339133892);
}
void pose_h_10(double *state, double *unused, double *out_2013770797981180213) {
  h_10(state, unused, out_2013770797981180213);
}
void pose_H_10(double *state, double *unused, double *out_2161437616861568278) {
  H_10(state, unused, out_2161437616861568278);
}
void pose_h_13(double *state, double *unused, double *out_7197851880815921934) {
  h_13(state, unused, out_7197851880815921934);
}
void pose_H_13(double *state, double *unused, double *out_6669295621038084923) {
  H_13(state, unused, out_6669295621038084923);
}
void pose_h_14(double *state, double *unused, double *out_1386181666946440377) {
  h_14(state, unused, out_1386181666946440377);
}
void pose_H_14(double *state, double *unused, double *out_8130058100694250293) {
  H_14(state, unused, out_8130058100694250293);
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
