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
void err_fun(double *nom_x, double *delta_x, double *out_8904005694201781505) {
   out_8904005694201781505[0] = delta_x[0] + nom_x[0];
   out_8904005694201781505[1] = delta_x[1] + nom_x[1];
   out_8904005694201781505[2] = delta_x[2] + nom_x[2];
   out_8904005694201781505[3] = delta_x[3] + nom_x[3];
   out_8904005694201781505[4] = delta_x[4] + nom_x[4];
   out_8904005694201781505[5] = delta_x[5] + nom_x[5];
   out_8904005694201781505[6] = delta_x[6] + nom_x[6];
   out_8904005694201781505[7] = delta_x[7] + nom_x[7];
   out_8904005694201781505[8] = delta_x[8] + nom_x[8];
   out_8904005694201781505[9] = delta_x[9] + nom_x[9];
   out_8904005694201781505[10] = delta_x[10] + nom_x[10];
   out_8904005694201781505[11] = delta_x[11] + nom_x[11];
   out_8904005694201781505[12] = delta_x[12] + nom_x[12];
   out_8904005694201781505[13] = delta_x[13] + nom_x[13];
   out_8904005694201781505[14] = delta_x[14] + nom_x[14];
   out_8904005694201781505[15] = delta_x[15] + nom_x[15];
   out_8904005694201781505[16] = delta_x[16] + nom_x[16];
   out_8904005694201781505[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_319882326801197501) {
   out_319882326801197501[0] = -nom_x[0] + true_x[0];
   out_319882326801197501[1] = -nom_x[1] + true_x[1];
   out_319882326801197501[2] = -nom_x[2] + true_x[2];
   out_319882326801197501[3] = -nom_x[3] + true_x[3];
   out_319882326801197501[4] = -nom_x[4] + true_x[4];
   out_319882326801197501[5] = -nom_x[5] + true_x[5];
   out_319882326801197501[6] = -nom_x[6] + true_x[6];
   out_319882326801197501[7] = -nom_x[7] + true_x[7];
   out_319882326801197501[8] = -nom_x[8] + true_x[8];
   out_319882326801197501[9] = -nom_x[9] + true_x[9];
   out_319882326801197501[10] = -nom_x[10] + true_x[10];
   out_319882326801197501[11] = -nom_x[11] + true_x[11];
   out_319882326801197501[12] = -nom_x[12] + true_x[12];
   out_319882326801197501[13] = -nom_x[13] + true_x[13];
   out_319882326801197501[14] = -nom_x[14] + true_x[14];
   out_319882326801197501[15] = -nom_x[15] + true_x[15];
   out_319882326801197501[16] = -nom_x[16] + true_x[16];
   out_319882326801197501[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_2755842367827800629) {
   out_2755842367827800629[0] = 1.0;
   out_2755842367827800629[1] = 0.0;
   out_2755842367827800629[2] = 0.0;
   out_2755842367827800629[3] = 0.0;
   out_2755842367827800629[4] = 0.0;
   out_2755842367827800629[5] = 0.0;
   out_2755842367827800629[6] = 0.0;
   out_2755842367827800629[7] = 0.0;
   out_2755842367827800629[8] = 0.0;
   out_2755842367827800629[9] = 0.0;
   out_2755842367827800629[10] = 0.0;
   out_2755842367827800629[11] = 0.0;
   out_2755842367827800629[12] = 0.0;
   out_2755842367827800629[13] = 0.0;
   out_2755842367827800629[14] = 0.0;
   out_2755842367827800629[15] = 0.0;
   out_2755842367827800629[16] = 0.0;
   out_2755842367827800629[17] = 0.0;
   out_2755842367827800629[18] = 0.0;
   out_2755842367827800629[19] = 1.0;
   out_2755842367827800629[20] = 0.0;
   out_2755842367827800629[21] = 0.0;
   out_2755842367827800629[22] = 0.0;
   out_2755842367827800629[23] = 0.0;
   out_2755842367827800629[24] = 0.0;
   out_2755842367827800629[25] = 0.0;
   out_2755842367827800629[26] = 0.0;
   out_2755842367827800629[27] = 0.0;
   out_2755842367827800629[28] = 0.0;
   out_2755842367827800629[29] = 0.0;
   out_2755842367827800629[30] = 0.0;
   out_2755842367827800629[31] = 0.0;
   out_2755842367827800629[32] = 0.0;
   out_2755842367827800629[33] = 0.0;
   out_2755842367827800629[34] = 0.0;
   out_2755842367827800629[35] = 0.0;
   out_2755842367827800629[36] = 0.0;
   out_2755842367827800629[37] = 0.0;
   out_2755842367827800629[38] = 1.0;
   out_2755842367827800629[39] = 0.0;
   out_2755842367827800629[40] = 0.0;
   out_2755842367827800629[41] = 0.0;
   out_2755842367827800629[42] = 0.0;
   out_2755842367827800629[43] = 0.0;
   out_2755842367827800629[44] = 0.0;
   out_2755842367827800629[45] = 0.0;
   out_2755842367827800629[46] = 0.0;
   out_2755842367827800629[47] = 0.0;
   out_2755842367827800629[48] = 0.0;
   out_2755842367827800629[49] = 0.0;
   out_2755842367827800629[50] = 0.0;
   out_2755842367827800629[51] = 0.0;
   out_2755842367827800629[52] = 0.0;
   out_2755842367827800629[53] = 0.0;
   out_2755842367827800629[54] = 0.0;
   out_2755842367827800629[55] = 0.0;
   out_2755842367827800629[56] = 0.0;
   out_2755842367827800629[57] = 1.0;
   out_2755842367827800629[58] = 0.0;
   out_2755842367827800629[59] = 0.0;
   out_2755842367827800629[60] = 0.0;
   out_2755842367827800629[61] = 0.0;
   out_2755842367827800629[62] = 0.0;
   out_2755842367827800629[63] = 0.0;
   out_2755842367827800629[64] = 0.0;
   out_2755842367827800629[65] = 0.0;
   out_2755842367827800629[66] = 0.0;
   out_2755842367827800629[67] = 0.0;
   out_2755842367827800629[68] = 0.0;
   out_2755842367827800629[69] = 0.0;
   out_2755842367827800629[70] = 0.0;
   out_2755842367827800629[71] = 0.0;
   out_2755842367827800629[72] = 0.0;
   out_2755842367827800629[73] = 0.0;
   out_2755842367827800629[74] = 0.0;
   out_2755842367827800629[75] = 0.0;
   out_2755842367827800629[76] = 1.0;
   out_2755842367827800629[77] = 0.0;
   out_2755842367827800629[78] = 0.0;
   out_2755842367827800629[79] = 0.0;
   out_2755842367827800629[80] = 0.0;
   out_2755842367827800629[81] = 0.0;
   out_2755842367827800629[82] = 0.0;
   out_2755842367827800629[83] = 0.0;
   out_2755842367827800629[84] = 0.0;
   out_2755842367827800629[85] = 0.0;
   out_2755842367827800629[86] = 0.0;
   out_2755842367827800629[87] = 0.0;
   out_2755842367827800629[88] = 0.0;
   out_2755842367827800629[89] = 0.0;
   out_2755842367827800629[90] = 0.0;
   out_2755842367827800629[91] = 0.0;
   out_2755842367827800629[92] = 0.0;
   out_2755842367827800629[93] = 0.0;
   out_2755842367827800629[94] = 0.0;
   out_2755842367827800629[95] = 1.0;
   out_2755842367827800629[96] = 0.0;
   out_2755842367827800629[97] = 0.0;
   out_2755842367827800629[98] = 0.0;
   out_2755842367827800629[99] = 0.0;
   out_2755842367827800629[100] = 0.0;
   out_2755842367827800629[101] = 0.0;
   out_2755842367827800629[102] = 0.0;
   out_2755842367827800629[103] = 0.0;
   out_2755842367827800629[104] = 0.0;
   out_2755842367827800629[105] = 0.0;
   out_2755842367827800629[106] = 0.0;
   out_2755842367827800629[107] = 0.0;
   out_2755842367827800629[108] = 0.0;
   out_2755842367827800629[109] = 0.0;
   out_2755842367827800629[110] = 0.0;
   out_2755842367827800629[111] = 0.0;
   out_2755842367827800629[112] = 0.0;
   out_2755842367827800629[113] = 0.0;
   out_2755842367827800629[114] = 1.0;
   out_2755842367827800629[115] = 0.0;
   out_2755842367827800629[116] = 0.0;
   out_2755842367827800629[117] = 0.0;
   out_2755842367827800629[118] = 0.0;
   out_2755842367827800629[119] = 0.0;
   out_2755842367827800629[120] = 0.0;
   out_2755842367827800629[121] = 0.0;
   out_2755842367827800629[122] = 0.0;
   out_2755842367827800629[123] = 0.0;
   out_2755842367827800629[124] = 0.0;
   out_2755842367827800629[125] = 0.0;
   out_2755842367827800629[126] = 0.0;
   out_2755842367827800629[127] = 0.0;
   out_2755842367827800629[128] = 0.0;
   out_2755842367827800629[129] = 0.0;
   out_2755842367827800629[130] = 0.0;
   out_2755842367827800629[131] = 0.0;
   out_2755842367827800629[132] = 0.0;
   out_2755842367827800629[133] = 1.0;
   out_2755842367827800629[134] = 0.0;
   out_2755842367827800629[135] = 0.0;
   out_2755842367827800629[136] = 0.0;
   out_2755842367827800629[137] = 0.0;
   out_2755842367827800629[138] = 0.0;
   out_2755842367827800629[139] = 0.0;
   out_2755842367827800629[140] = 0.0;
   out_2755842367827800629[141] = 0.0;
   out_2755842367827800629[142] = 0.0;
   out_2755842367827800629[143] = 0.0;
   out_2755842367827800629[144] = 0.0;
   out_2755842367827800629[145] = 0.0;
   out_2755842367827800629[146] = 0.0;
   out_2755842367827800629[147] = 0.0;
   out_2755842367827800629[148] = 0.0;
   out_2755842367827800629[149] = 0.0;
   out_2755842367827800629[150] = 0.0;
   out_2755842367827800629[151] = 0.0;
   out_2755842367827800629[152] = 1.0;
   out_2755842367827800629[153] = 0.0;
   out_2755842367827800629[154] = 0.0;
   out_2755842367827800629[155] = 0.0;
   out_2755842367827800629[156] = 0.0;
   out_2755842367827800629[157] = 0.0;
   out_2755842367827800629[158] = 0.0;
   out_2755842367827800629[159] = 0.0;
   out_2755842367827800629[160] = 0.0;
   out_2755842367827800629[161] = 0.0;
   out_2755842367827800629[162] = 0.0;
   out_2755842367827800629[163] = 0.0;
   out_2755842367827800629[164] = 0.0;
   out_2755842367827800629[165] = 0.0;
   out_2755842367827800629[166] = 0.0;
   out_2755842367827800629[167] = 0.0;
   out_2755842367827800629[168] = 0.0;
   out_2755842367827800629[169] = 0.0;
   out_2755842367827800629[170] = 0.0;
   out_2755842367827800629[171] = 1.0;
   out_2755842367827800629[172] = 0.0;
   out_2755842367827800629[173] = 0.0;
   out_2755842367827800629[174] = 0.0;
   out_2755842367827800629[175] = 0.0;
   out_2755842367827800629[176] = 0.0;
   out_2755842367827800629[177] = 0.0;
   out_2755842367827800629[178] = 0.0;
   out_2755842367827800629[179] = 0.0;
   out_2755842367827800629[180] = 0.0;
   out_2755842367827800629[181] = 0.0;
   out_2755842367827800629[182] = 0.0;
   out_2755842367827800629[183] = 0.0;
   out_2755842367827800629[184] = 0.0;
   out_2755842367827800629[185] = 0.0;
   out_2755842367827800629[186] = 0.0;
   out_2755842367827800629[187] = 0.0;
   out_2755842367827800629[188] = 0.0;
   out_2755842367827800629[189] = 0.0;
   out_2755842367827800629[190] = 1.0;
   out_2755842367827800629[191] = 0.0;
   out_2755842367827800629[192] = 0.0;
   out_2755842367827800629[193] = 0.0;
   out_2755842367827800629[194] = 0.0;
   out_2755842367827800629[195] = 0.0;
   out_2755842367827800629[196] = 0.0;
   out_2755842367827800629[197] = 0.0;
   out_2755842367827800629[198] = 0.0;
   out_2755842367827800629[199] = 0.0;
   out_2755842367827800629[200] = 0.0;
   out_2755842367827800629[201] = 0.0;
   out_2755842367827800629[202] = 0.0;
   out_2755842367827800629[203] = 0.0;
   out_2755842367827800629[204] = 0.0;
   out_2755842367827800629[205] = 0.0;
   out_2755842367827800629[206] = 0.0;
   out_2755842367827800629[207] = 0.0;
   out_2755842367827800629[208] = 0.0;
   out_2755842367827800629[209] = 1.0;
   out_2755842367827800629[210] = 0.0;
   out_2755842367827800629[211] = 0.0;
   out_2755842367827800629[212] = 0.0;
   out_2755842367827800629[213] = 0.0;
   out_2755842367827800629[214] = 0.0;
   out_2755842367827800629[215] = 0.0;
   out_2755842367827800629[216] = 0.0;
   out_2755842367827800629[217] = 0.0;
   out_2755842367827800629[218] = 0.0;
   out_2755842367827800629[219] = 0.0;
   out_2755842367827800629[220] = 0.0;
   out_2755842367827800629[221] = 0.0;
   out_2755842367827800629[222] = 0.0;
   out_2755842367827800629[223] = 0.0;
   out_2755842367827800629[224] = 0.0;
   out_2755842367827800629[225] = 0.0;
   out_2755842367827800629[226] = 0.0;
   out_2755842367827800629[227] = 0.0;
   out_2755842367827800629[228] = 1.0;
   out_2755842367827800629[229] = 0.0;
   out_2755842367827800629[230] = 0.0;
   out_2755842367827800629[231] = 0.0;
   out_2755842367827800629[232] = 0.0;
   out_2755842367827800629[233] = 0.0;
   out_2755842367827800629[234] = 0.0;
   out_2755842367827800629[235] = 0.0;
   out_2755842367827800629[236] = 0.0;
   out_2755842367827800629[237] = 0.0;
   out_2755842367827800629[238] = 0.0;
   out_2755842367827800629[239] = 0.0;
   out_2755842367827800629[240] = 0.0;
   out_2755842367827800629[241] = 0.0;
   out_2755842367827800629[242] = 0.0;
   out_2755842367827800629[243] = 0.0;
   out_2755842367827800629[244] = 0.0;
   out_2755842367827800629[245] = 0.0;
   out_2755842367827800629[246] = 0.0;
   out_2755842367827800629[247] = 1.0;
   out_2755842367827800629[248] = 0.0;
   out_2755842367827800629[249] = 0.0;
   out_2755842367827800629[250] = 0.0;
   out_2755842367827800629[251] = 0.0;
   out_2755842367827800629[252] = 0.0;
   out_2755842367827800629[253] = 0.0;
   out_2755842367827800629[254] = 0.0;
   out_2755842367827800629[255] = 0.0;
   out_2755842367827800629[256] = 0.0;
   out_2755842367827800629[257] = 0.0;
   out_2755842367827800629[258] = 0.0;
   out_2755842367827800629[259] = 0.0;
   out_2755842367827800629[260] = 0.0;
   out_2755842367827800629[261] = 0.0;
   out_2755842367827800629[262] = 0.0;
   out_2755842367827800629[263] = 0.0;
   out_2755842367827800629[264] = 0.0;
   out_2755842367827800629[265] = 0.0;
   out_2755842367827800629[266] = 1.0;
   out_2755842367827800629[267] = 0.0;
   out_2755842367827800629[268] = 0.0;
   out_2755842367827800629[269] = 0.0;
   out_2755842367827800629[270] = 0.0;
   out_2755842367827800629[271] = 0.0;
   out_2755842367827800629[272] = 0.0;
   out_2755842367827800629[273] = 0.0;
   out_2755842367827800629[274] = 0.0;
   out_2755842367827800629[275] = 0.0;
   out_2755842367827800629[276] = 0.0;
   out_2755842367827800629[277] = 0.0;
   out_2755842367827800629[278] = 0.0;
   out_2755842367827800629[279] = 0.0;
   out_2755842367827800629[280] = 0.0;
   out_2755842367827800629[281] = 0.0;
   out_2755842367827800629[282] = 0.0;
   out_2755842367827800629[283] = 0.0;
   out_2755842367827800629[284] = 0.0;
   out_2755842367827800629[285] = 1.0;
   out_2755842367827800629[286] = 0.0;
   out_2755842367827800629[287] = 0.0;
   out_2755842367827800629[288] = 0.0;
   out_2755842367827800629[289] = 0.0;
   out_2755842367827800629[290] = 0.0;
   out_2755842367827800629[291] = 0.0;
   out_2755842367827800629[292] = 0.0;
   out_2755842367827800629[293] = 0.0;
   out_2755842367827800629[294] = 0.0;
   out_2755842367827800629[295] = 0.0;
   out_2755842367827800629[296] = 0.0;
   out_2755842367827800629[297] = 0.0;
   out_2755842367827800629[298] = 0.0;
   out_2755842367827800629[299] = 0.0;
   out_2755842367827800629[300] = 0.0;
   out_2755842367827800629[301] = 0.0;
   out_2755842367827800629[302] = 0.0;
   out_2755842367827800629[303] = 0.0;
   out_2755842367827800629[304] = 1.0;
   out_2755842367827800629[305] = 0.0;
   out_2755842367827800629[306] = 0.0;
   out_2755842367827800629[307] = 0.0;
   out_2755842367827800629[308] = 0.0;
   out_2755842367827800629[309] = 0.0;
   out_2755842367827800629[310] = 0.0;
   out_2755842367827800629[311] = 0.0;
   out_2755842367827800629[312] = 0.0;
   out_2755842367827800629[313] = 0.0;
   out_2755842367827800629[314] = 0.0;
   out_2755842367827800629[315] = 0.0;
   out_2755842367827800629[316] = 0.0;
   out_2755842367827800629[317] = 0.0;
   out_2755842367827800629[318] = 0.0;
   out_2755842367827800629[319] = 0.0;
   out_2755842367827800629[320] = 0.0;
   out_2755842367827800629[321] = 0.0;
   out_2755842367827800629[322] = 0.0;
   out_2755842367827800629[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_2465907068804727132) {
   out_2465907068804727132[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_2465907068804727132[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_2465907068804727132[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_2465907068804727132[3] = dt*state[12] + state[3];
   out_2465907068804727132[4] = dt*state[13] + state[4];
   out_2465907068804727132[5] = dt*state[14] + state[5];
   out_2465907068804727132[6] = state[6];
   out_2465907068804727132[7] = state[7];
   out_2465907068804727132[8] = state[8];
   out_2465907068804727132[9] = state[9];
   out_2465907068804727132[10] = state[10];
   out_2465907068804727132[11] = state[11];
   out_2465907068804727132[12] = state[12];
   out_2465907068804727132[13] = state[13];
   out_2465907068804727132[14] = state[14];
   out_2465907068804727132[15] = state[15];
   out_2465907068804727132[16] = state[16];
   out_2465907068804727132[17] = state[17];
}
void F_fun(double *state, double dt, double *out_8858355740763119346) {
   out_8858355740763119346[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_8858355740763119346[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_8858355740763119346[2] = 0;
   out_8858355740763119346[3] = 0;
   out_8858355740763119346[4] = 0;
   out_8858355740763119346[5] = 0;
   out_8858355740763119346[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_8858355740763119346[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_8858355740763119346[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_8858355740763119346[9] = 0;
   out_8858355740763119346[10] = 0;
   out_8858355740763119346[11] = 0;
   out_8858355740763119346[12] = 0;
   out_8858355740763119346[13] = 0;
   out_8858355740763119346[14] = 0;
   out_8858355740763119346[15] = 0;
   out_8858355740763119346[16] = 0;
   out_8858355740763119346[17] = 0;
   out_8858355740763119346[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_8858355740763119346[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_8858355740763119346[20] = 0;
   out_8858355740763119346[21] = 0;
   out_8858355740763119346[22] = 0;
   out_8858355740763119346[23] = 0;
   out_8858355740763119346[24] = 0;
   out_8858355740763119346[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_8858355740763119346[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_8858355740763119346[27] = 0;
   out_8858355740763119346[28] = 0;
   out_8858355740763119346[29] = 0;
   out_8858355740763119346[30] = 0;
   out_8858355740763119346[31] = 0;
   out_8858355740763119346[32] = 0;
   out_8858355740763119346[33] = 0;
   out_8858355740763119346[34] = 0;
   out_8858355740763119346[35] = 0;
   out_8858355740763119346[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_8858355740763119346[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_8858355740763119346[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_8858355740763119346[39] = 0;
   out_8858355740763119346[40] = 0;
   out_8858355740763119346[41] = 0;
   out_8858355740763119346[42] = 0;
   out_8858355740763119346[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_8858355740763119346[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_8858355740763119346[45] = 0;
   out_8858355740763119346[46] = 0;
   out_8858355740763119346[47] = 0;
   out_8858355740763119346[48] = 0;
   out_8858355740763119346[49] = 0;
   out_8858355740763119346[50] = 0;
   out_8858355740763119346[51] = 0;
   out_8858355740763119346[52] = 0;
   out_8858355740763119346[53] = 0;
   out_8858355740763119346[54] = 0;
   out_8858355740763119346[55] = 0;
   out_8858355740763119346[56] = 0;
   out_8858355740763119346[57] = 1;
   out_8858355740763119346[58] = 0;
   out_8858355740763119346[59] = 0;
   out_8858355740763119346[60] = 0;
   out_8858355740763119346[61] = 0;
   out_8858355740763119346[62] = 0;
   out_8858355740763119346[63] = 0;
   out_8858355740763119346[64] = 0;
   out_8858355740763119346[65] = 0;
   out_8858355740763119346[66] = dt;
   out_8858355740763119346[67] = 0;
   out_8858355740763119346[68] = 0;
   out_8858355740763119346[69] = 0;
   out_8858355740763119346[70] = 0;
   out_8858355740763119346[71] = 0;
   out_8858355740763119346[72] = 0;
   out_8858355740763119346[73] = 0;
   out_8858355740763119346[74] = 0;
   out_8858355740763119346[75] = 0;
   out_8858355740763119346[76] = 1;
   out_8858355740763119346[77] = 0;
   out_8858355740763119346[78] = 0;
   out_8858355740763119346[79] = 0;
   out_8858355740763119346[80] = 0;
   out_8858355740763119346[81] = 0;
   out_8858355740763119346[82] = 0;
   out_8858355740763119346[83] = 0;
   out_8858355740763119346[84] = 0;
   out_8858355740763119346[85] = dt;
   out_8858355740763119346[86] = 0;
   out_8858355740763119346[87] = 0;
   out_8858355740763119346[88] = 0;
   out_8858355740763119346[89] = 0;
   out_8858355740763119346[90] = 0;
   out_8858355740763119346[91] = 0;
   out_8858355740763119346[92] = 0;
   out_8858355740763119346[93] = 0;
   out_8858355740763119346[94] = 0;
   out_8858355740763119346[95] = 1;
   out_8858355740763119346[96] = 0;
   out_8858355740763119346[97] = 0;
   out_8858355740763119346[98] = 0;
   out_8858355740763119346[99] = 0;
   out_8858355740763119346[100] = 0;
   out_8858355740763119346[101] = 0;
   out_8858355740763119346[102] = 0;
   out_8858355740763119346[103] = 0;
   out_8858355740763119346[104] = dt;
   out_8858355740763119346[105] = 0;
   out_8858355740763119346[106] = 0;
   out_8858355740763119346[107] = 0;
   out_8858355740763119346[108] = 0;
   out_8858355740763119346[109] = 0;
   out_8858355740763119346[110] = 0;
   out_8858355740763119346[111] = 0;
   out_8858355740763119346[112] = 0;
   out_8858355740763119346[113] = 0;
   out_8858355740763119346[114] = 1;
   out_8858355740763119346[115] = 0;
   out_8858355740763119346[116] = 0;
   out_8858355740763119346[117] = 0;
   out_8858355740763119346[118] = 0;
   out_8858355740763119346[119] = 0;
   out_8858355740763119346[120] = 0;
   out_8858355740763119346[121] = 0;
   out_8858355740763119346[122] = 0;
   out_8858355740763119346[123] = 0;
   out_8858355740763119346[124] = 0;
   out_8858355740763119346[125] = 0;
   out_8858355740763119346[126] = 0;
   out_8858355740763119346[127] = 0;
   out_8858355740763119346[128] = 0;
   out_8858355740763119346[129] = 0;
   out_8858355740763119346[130] = 0;
   out_8858355740763119346[131] = 0;
   out_8858355740763119346[132] = 0;
   out_8858355740763119346[133] = 1;
   out_8858355740763119346[134] = 0;
   out_8858355740763119346[135] = 0;
   out_8858355740763119346[136] = 0;
   out_8858355740763119346[137] = 0;
   out_8858355740763119346[138] = 0;
   out_8858355740763119346[139] = 0;
   out_8858355740763119346[140] = 0;
   out_8858355740763119346[141] = 0;
   out_8858355740763119346[142] = 0;
   out_8858355740763119346[143] = 0;
   out_8858355740763119346[144] = 0;
   out_8858355740763119346[145] = 0;
   out_8858355740763119346[146] = 0;
   out_8858355740763119346[147] = 0;
   out_8858355740763119346[148] = 0;
   out_8858355740763119346[149] = 0;
   out_8858355740763119346[150] = 0;
   out_8858355740763119346[151] = 0;
   out_8858355740763119346[152] = 1;
   out_8858355740763119346[153] = 0;
   out_8858355740763119346[154] = 0;
   out_8858355740763119346[155] = 0;
   out_8858355740763119346[156] = 0;
   out_8858355740763119346[157] = 0;
   out_8858355740763119346[158] = 0;
   out_8858355740763119346[159] = 0;
   out_8858355740763119346[160] = 0;
   out_8858355740763119346[161] = 0;
   out_8858355740763119346[162] = 0;
   out_8858355740763119346[163] = 0;
   out_8858355740763119346[164] = 0;
   out_8858355740763119346[165] = 0;
   out_8858355740763119346[166] = 0;
   out_8858355740763119346[167] = 0;
   out_8858355740763119346[168] = 0;
   out_8858355740763119346[169] = 0;
   out_8858355740763119346[170] = 0;
   out_8858355740763119346[171] = 1;
   out_8858355740763119346[172] = 0;
   out_8858355740763119346[173] = 0;
   out_8858355740763119346[174] = 0;
   out_8858355740763119346[175] = 0;
   out_8858355740763119346[176] = 0;
   out_8858355740763119346[177] = 0;
   out_8858355740763119346[178] = 0;
   out_8858355740763119346[179] = 0;
   out_8858355740763119346[180] = 0;
   out_8858355740763119346[181] = 0;
   out_8858355740763119346[182] = 0;
   out_8858355740763119346[183] = 0;
   out_8858355740763119346[184] = 0;
   out_8858355740763119346[185] = 0;
   out_8858355740763119346[186] = 0;
   out_8858355740763119346[187] = 0;
   out_8858355740763119346[188] = 0;
   out_8858355740763119346[189] = 0;
   out_8858355740763119346[190] = 1;
   out_8858355740763119346[191] = 0;
   out_8858355740763119346[192] = 0;
   out_8858355740763119346[193] = 0;
   out_8858355740763119346[194] = 0;
   out_8858355740763119346[195] = 0;
   out_8858355740763119346[196] = 0;
   out_8858355740763119346[197] = 0;
   out_8858355740763119346[198] = 0;
   out_8858355740763119346[199] = 0;
   out_8858355740763119346[200] = 0;
   out_8858355740763119346[201] = 0;
   out_8858355740763119346[202] = 0;
   out_8858355740763119346[203] = 0;
   out_8858355740763119346[204] = 0;
   out_8858355740763119346[205] = 0;
   out_8858355740763119346[206] = 0;
   out_8858355740763119346[207] = 0;
   out_8858355740763119346[208] = 0;
   out_8858355740763119346[209] = 1;
   out_8858355740763119346[210] = 0;
   out_8858355740763119346[211] = 0;
   out_8858355740763119346[212] = 0;
   out_8858355740763119346[213] = 0;
   out_8858355740763119346[214] = 0;
   out_8858355740763119346[215] = 0;
   out_8858355740763119346[216] = 0;
   out_8858355740763119346[217] = 0;
   out_8858355740763119346[218] = 0;
   out_8858355740763119346[219] = 0;
   out_8858355740763119346[220] = 0;
   out_8858355740763119346[221] = 0;
   out_8858355740763119346[222] = 0;
   out_8858355740763119346[223] = 0;
   out_8858355740763119346[224] = 0;
   out_8858355740763119346[225] = 0;
   out_8858355740763119346[226] = 0;
   out_8858355740763119346[227] = 0;
   out_8858355740763119346[228] = 1;
   out_8858355740763119346[229] = 0;
   out_8858355740763119346[230] = 0;
   out_8858355740763119346[231] = 0;
   out_8858355740763119346[232] = 0;
   out_8858355740763119346[233] = 0;
   out_8858355740763119346[234] = 0;
   out_8858355740763119346[235] = 0;
   out_8858355740763119346[236] = 0;
   out_8858355740763119346[237] = 0;
   out_8858355740763119346[238] = 0;
   out_8858355740763119346[239] = 0;
   out_8858355740763119346[240] = 0;
   out_8858355740763119346[241] = 0;
   out_8858355740763119346[242] = 0;
   out_8858355740763119346[243] = 0;
   out_8858355740763119346[244] = 0;
   out_8858355740763119346[245] = 0;
   out_8858355740763119346[246] = 0;
   out_8858355740763119346[247] = 1;
   out_8858355740763119346[248] = 0;
   out_8858355740763119346[249] = 0;
   out_8858355740763119346[250] = 0;
   out_8858355740763119346[251] = 0;
   out_8858355740763119346[252] = 0;
   out_8858355740763119346[253] = 0;
   out_8858355740763119346[254] = 0;
   out_8858355740763119346[255] = 0;
   out_8858355740763119346[256] = 0;
   out_8858355740763119346[257] = 0;
   out_8858355740763119346[258] = 0;
   out_8858355740763119346[259] = 0;
   out_8858355740763119346[260] = 0;
   out_8858355740763119346[261] = 0;
   out_8858355740763119346[262] = 0;
   out_8858355740763119346[263] = 0;
   out_8858355740763119346[264] = 0;
   out_8858355740763119346[265] = 0;
   out_8858355740763119346[266] = 1;
   out_8858355740763119346[267] = 0;
   out_8858355740763119346[268] = 0;
   out_8858355740763119346[269] = 0;
   out_8858355740763119346[270] = 0;
   out_8858355740763119346[271] = 0;
   out_8858355740763119346[272] = 0;
   out_8858355740763119346[273] = 0;
   out_8858355740763119346[274] = 0;
   out_8858355740763119346[275] = 0;
   out_8858355740763119346[276] = 0;
   out_8858355740763119346[277] = 0;
   out_8858355740763119346[278] = 0;
   out_8858355740763119346[279] = 0;
   out_8858355740763119346[280] = 0;
   out_8858355740763119346[281] = 0;
   out_8858355740763119346[282] = 0;
   out_8858355740763119346[283] = 0;
   out_8858355740763119346[284] = 0;
   out_8858355740763119346[285] = 1;
   out_8858355740763119346[286] = 0;
   out_8858355740763119346[287] = 0;
   out_8858355740763119346[288] = 0;
   out_8858355740763119346[289] = 0;
   out_8858355740763119346[290] = 0;
   out_8858355740763119346[291] = 0;
   out_8858355740763119346[292] = 0;
   out_8858355740763119346[293] = 0;
   out_8858355740763119346[294] = 0;
   out_8858355740763119346[295] = 0;
   out_8858355740763119346[296] = 0;
   out_8858355740763119346[297] = 0;
   out_8858355740763119346[298] = 0;
   out_8858355740763119346[299] = 0;
   out_8858355740763119346[300] = 0;
   out_8858355740763119346[301] = 0;
   out_8858355740763119346[302] = 0;
   out_8858355740763119346[303] = 0;
   out_8858355740763119346[304] = 1;
   out_8858355740763119346[305] = 0;
   out_8858355740763119346[306] = 0;
   out_8858355740763119346[307] = 0;
   out_8858355740763119346[308] = 0;
   out_8858355740763119346[309] = 0;
   out_8858355740763119346[310] = 0;
   out_8858355740763119346[311] = 0;
   out_8858355740763119346[312] = 0;
   out_8858355740763119346[313] = 0;
   out_8858355740763119346[314] = 0;
   out_8858355740763119346[315] = 0;
   out_8858355740763119346[316] = 0;
   out_8858355740763119346[317] = 0;
   out_8858355740763119346[318] = 0;
   out_8858355740763119346[319] = 0;
   out_8858355740763119346[320] = 0;
   out_8858355740763119346[321] = 0;
   out_8858355740763119346[322] = 0;
   out_8858355740763119346[323] = 1;
}
void h_4(double *state, double *unused, double *out_5314299562689028081) {
   out_5314299562689028081[0] = state[6] + state[9];
   out_5314299562689028081[1] = state[7] + state[10];
   out_5314299562689028081[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_8603924174579759350) {
   out_8603924174579759350[0] = 0;
   out_8603924174579759350[1] = 0;
   out_8603924174579759350[2] = 0;
   out_8603924174579759350[3] = 0;
   out_8603924174579759350[4] = 0;
   out_8603924174579759350[5] = 0;
   out_8603924174579759350[6] = 1;
   out_8603924174579759350[7] = 0;
   out_8603924174579759350[8] = 0;
   out_8603924174579759350[9] = 1;
   out_8603924174579759350[10] = 0;
   out_8603924174579759350[11] = 0;
   out_8603924174579759350[12] = 0;
   out_8603924174579759350[13] = 0;
   out_8603924174579759350[14] = 0;
   out_8603924174579759350[15] = 0;
   out_8603924174579759350[16] = 0;
   out_8603924174579759350[17] = 0;
   out_8603924174579759350[18] = 0;
   out_8603924174579759350[19] = 0;
   out_8603924174579759350[20] = 0;
   out_8603924174579759350[21] = 0;
   out_8603924174579759350[22] = 0;
   out_8603924174579759350[23] = 0;
   out_8603924174579759350[24] = 0;
   out_8603924174579759350[25] = 1;
   out_8603924174579759350[26] = 0;
   out_8603924174579759350[27] = 0;
   out_8603924174579759350[28] = 1;
   out_8603924174579759350[29] = 0;
   out_8603924174579759350[30] = 0;
   out_8603924174579759350[31] = 0;
   out_8603924174579759350[32] = 0;
   out_8603924174579759350[33] = 0;
   out_8603924174579759350[34] = 0;
   out_8603924174579759350[35] = 0;
   out_8603924174579759350[36] = 0;
   out_8603924174579759350[37] = 0;
   out_8603924174579759350[38] = 0;
   out_8603924174579759350[39] = 0;
   out_8603924174579759350[40] = 0;
   out_8603924174579759350[41] = 0;
   out_8603924174579759350[42] = 0;
   out_8603924174579759350[43] = 0;
   out_8603924174579759350[44] = 1;
   out_8603924174579759350[45] = 0;
   out_8603924174579759350[46] = 0;
   out_8603924174579759350[47] = 1;
   out_8603924174579759350[48] = 0;
   out_8603924174579759350[49] = 0;
   out_8603924174579759350[50] = 0;
   out_8603924174579759350[51] = 0;
   out_8603924174579759350[52] = 0;
   out_8603924174579759350[53] = 0;
}
void h_10(double *state, double *unused, double *out_1117176031280540036) {
   out_1117176031280540036[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_1117176031280540036[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_1117176031280540036[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_8788488427206403946) {
   out_8788488427206403946[0] = 0;
   out_8788488427206403946[1] = 9.8100000000000005*cos(state[1]);
   out_8788488427206403946[2] = 0;
   out_8788488427206403946[3] = 0;
   out_8788488427206403946[4] = -state[8];
   out_8788488427206403946[5] = state[7];
   out_8788488427206403946[6] = 0;
   out_8788488427206403946[7] = state[5];
   out_8788488427206403946[8] = -state[4];
   out_8788488427206403946[9] = 0;
   out_8788488427206403946[10] = 0;
   out_8788488427206403946[11] = 0;
   out_8788488427206403946[12] = 1;
   out_8788488427206403946[13] = 0;
   out_8788488427206403946[14] = 0;
   out_8788488427206403946[15] = 1;
   out_8788488427206403946[16] = 0;
   out_8788488427206403946[17] = 0;
   out_8788488427206403946[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_8788488427206403946[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_8788488427206403946[20] = 0;
   out_8788488427206403946[21] = state[8];
   out_8788488427206403946[22] = 0;
   out_8788488427206403946[23] = -state[6];
   out_8788488427206403946[24] = -state[5];
   out_8788488427206403946[25] = 0;
   out_8788488427206403946[26] = state[3];
   out_8788488427206403946[27] = 0;
   out_8788488427206403946[28] = 0;
   out_8788488427206403946[29] = 0;
   out_8788488427206403946[30] = 0;
   out_8788488427206403946[31] = 1;
   out_8788488427206403946[32] = 0;
   out_8788488427206403946[33] = 0;
   out_8788488427206403946[34] = 1;
   out_8788488427206403946[35] = 0;
   out_8788488427206403946[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_8788488427206403946[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_8788488427206403946[38] = 0;
   out_8788488427206403946[39] = -state[7];
   out_8788488427206403946[40] = state[6];
   out_8788488427206403946[41] = 0;
   out_8788488427206403946[42] = state[4];
   out_8788488427206403946[43] = -state[3];
   out_8788488427206403946[44] = 0;
   out_8788488427206403946[45] = 0;
   out_8788488427206403946[46] = 0;
   out_8788488427206403946[47] = 0;
   out_8788488427206403946[48] = 0;
   out_8788488427206403946[49] = 0;
   out_8788488427206403946[50] = 1;
   out_8788488427206403946[51] = 0;
   out_8788488427206403946[52] = 0;
   out_8788488427206403946[53] = 1;
}
void h_13(double *state, double *unused, double *out_4742713455498518035) {
   out_4742713455498518035[0] = state[3];
   out_4742713455498518035[1] = state[4];
   out_4742713455498518035[2] = state[5];
}
void H_13(double *state, double *unused, double *out_5391650349247426549) {
   out_5391650349247426549[0] = 0;
   out_5391650349247426549[1] = 0;
   out_5391650349247426549[2] = 0;
   out_5391650349247426549[3] = 1;
   out_5391650349247426549[4] = 0;
   out_5391650349247426549[5] = 0;
   out_5391650349247426549[6] = 0;
   out_5391650349247426549[7] = 0;
   out_5391650349247426549[8] = 0;
   out_5391650349247426549[9] = 0;
   out_5391650349247426549[10] = 0;
   out_5391650349247426549[11] = 0;
   out_5391650349247426549[12] = 0;
   out_5391650349247426549[13] = 0;
   out_5391650349247426549[14] = 0;
   out_5391650349247426549[15] = 0;
   out_5391650349247426549[16] = 0;
   out_5391650349247426549[17] = 0;
   out_5391650349247426549[18] = 0;
   out_5391650349247426549[19] = 0;
   out_5391650349247426549[20] = 0;
   out_5391650349247426549[21] = 0;
   out_5391650349247426549[22] = 1;
   out_5391650349247426549[23] = 0;
   out_5391650349247426549[24] = 0;
   out_5391650349247426549[25] = 0;
   out_5391650349247426549[26] = 0;
   out_5391650349247426549[27] = 0;
   out_5391650349247426549[28] = 0;
   out_5391650349247426549[29] = 0;
   out_5391650349247426549[30] = 0;
   out_5391650349247426549[31] = 0;
   out_5391650349247426549[32] = 0;
   out_5391650349247426549[33] = 0;
   out_5391650349247426549[34] = 0;
   out_5391650349247426549[35] = 0;
   out_5391650349247426549[36] = 0;
   out_5391650349247426549[37] = 0;
   out_5391650349247426549[38] = 0;
   out_5391650349247426549[39] = 0;
   out_5391650349247426549[40] = 0;
   out_5391650349247426549[41] = 1;
   out_5391650349247426549[42] = 0;
   out_5391650349247426549[43] = 0;
   out_5391650349247426549[44] = 0;
   out_5391650349247426549[45] = 0;
   out_5391650349247426549[46] = 0;
   out_5391650349247426549[47] = 0;
   out_5391650349247426549[48] = 0;
   out_5391650349247426549[49] = 0;
   out_5391650349247426549[50] = 0;
   out_5391650349247426549[51] = 0;
   out_5391650349247426549[52] = 0;
   out_5391650349247426549[53] = 0;
}
void h_14(double *state, double *unused, double *out_9173159729852422823) {
   out_9173159729852422823[0] = state[6];
   out_9173159729852422823[1] = state[7];
   out_9173159729852422823[2] = state[8];
}
void H_14(double *state, double *unused, double *out_4640683318240274821) {
   out_4640683318240274821[0] = 0;
   out_4640683318240274821[1] = 0;
   out_4640683318240274821[2] = 0;
   out_4640683318240274821[3] = 0;
   out_4640683318240274821[4] = 0;
   out_4640683318240274821[5] = 0;
   out_4640683318240274821[6] = 1;
   out_4640683318240274821[7] = 0;
   out_4640683318240274821[8] = 0;
   out_4640683318240274821[9] = 0;
   out_4640683318240274821[10] = 0;
   out_4640683318240274821[11] = 0;
   out_4640683318240274821[12] = 0;
   out_4640683318240274821[13] = 0;
   out_4640683318240274821[14] = 0;
   out_4640683318240274821[15] = 0;
   out_4640683318240274821[16] = 0;
   out_4640683318240274821[17] = 0;
   out_4640683318240274821[18] = 0;
   out_4640683318240274821[19] = 0;
   out_4640683318240274821[20] = 0;
   out_4640683318240274821[21] = 0;
   out_4640683318240274821[22] = 0;
   out_4640683318240274821[23] = 0;
   out_4640683318240274821[24] = 0;
   out_4640683318240274821[25] = 1;
   out_4640683318240274821[26] = 0;
   out_4640683318240274821[27] = 0;
   out_4640683318240274821[28] = 0;
   out_4640683318240274821[29] = 0;
   out_4640683318240274821[30] = 0;
   out_4640683318240274821[31] = 0;
   out_4640683318240274821[32] = 0;
   out_4640683318240274821[33] = 0;
   out_4640683318240274821[34] = 0;
   out_4640683318240274821[35] = 0;
   out_4640683318240274821[36] = 0;
   out_4640683318240274821[37] = 0;
   out_4640683318240274821[38] = 0;
   out_4640683318240274821[39] = 0;
   out_4640683318240274821[40] = 0;
   out_4640683318240274821[41] = 0;
   out_4640683318240274821[42] = 0;
   out_4640683318240274821[43] = 0;
   out_4640683318240274821[44] = 1;
   out_4640683318240274821[45] = 0;
   out_4640683318240274821[46] = 0;
   out_4640683318240274821[47] = 0;
   out_4640683318240274821[48] = 0;
   out_4640683318240274821[49] = 0;
   out_4640683318240274821[50] = 0;
   out_4640683318240274821[51] = 0;
   out_4640683318240274821[52] = 0;
   out_4640683318240274821[53] = 0;
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
void pose_err_fun(double *nom_x, double *delta_x, double *out_8904005694201781505) {
  err_fun(nom_x, delta_x, out_8904005694201781505);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_319882326801197501) {
  inv_err_fun(nom_x, true_x, out_319882326801197501);
}
void pose_H_mod_fun(double *state, double *out_2755842367827800629) {
  H_mod_fun(state, out_2755842367827800629);
}
void pose_f_fun(double *state, double dt, double *out_2465907068804727132) {
  f_fun(state,  dt, out_2465907068804727132);
}
void pose_F_fun(double *state, double dt, double *out_8858355740763119346) {
  F_fun(state,  dt, out_8858355740763119346);
}
void pose_h_4(double *state, double *unused, double *out_5314299562689028081) {
  h_4(state, unused, out_5314299562689028081);
}
void pose_H_4(double *state, double *unused, double *out_8603924174579759350) {
  H_4(state, unused, out_8603924174579759350);
}
void pose_h_10(double *state, double *unused, double *out_1117176031280540036) {
  h_10(state, unused, out_1117176031280540036);
}
void pose_H_10(double *state, double *unused, double *out_8788488427206403946) {
  H_10(state, unused, out_8788488427206403946);
}
void pose_h_13(double *state, double *unused, double *out_4742713455498518035) {
  h_13(state, unused, out_4742713455498518035);
}
void pose_H_13(double *state, double *unused, double *out_5391650349247426549) {
  H_13(state, unused, out_5391650349247426549);
}
void pose_h_14(double *state, double *unused, double *out_9173159729852422823) {
  h_14(state, unused, out_9173159729852422823);
}
void pose_H_14(double *state, double *unused, double *out_4640683318240274821) {
  H_14(state, unused, out_4640683318240274821);
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
