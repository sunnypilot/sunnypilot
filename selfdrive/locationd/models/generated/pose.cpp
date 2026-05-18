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
void err_fun(double *nom_x, double *delta_x, double *out_3240425447174633819) {
   out_3240425447174633819[0] = delta_x[0] + nom_x[0];
   out_3240425447174633819[1] = delta_x[1] + nom_x[1];
   out_3240425447174633819[2] = delta_x[2] + nom_x[2];
   out_3240425447174633819[3] = delta_x[3] + nom_x[3];
   out_3240425447174633819[4] = delta_x[4] + nom_x[4];
   out_3240425447174633819[5] = delta_x[5] + nom_x[5];
   out_3240425447174633819[6] = delta_x[6] + nom_x[6];
   out_3240425447174633819[7] = delta_x[7] + nom_x[7];
   out_3240425447174633819[8] = delta_x[8] + nom_x[8];
   out_3240425447174633819[9] = delta_x[9] + nom_x[9];
   out_3240425447174633819[10] = delta_x[10] + nom_x[10];
   out_3240425447174633819[11] = delta_x[11] + nom_x[11];
   out_3240425447174633819[12] = delta_x[12] + nom_x[12];
   out_3240425447174633819[13] = delta_x[13] + nom_x[13];
   out_3240425447174633819[14] = delta_x[14] + nom_x[14];
   out_3240425447174633819[15] = delta_x[15] + nom_x[15];
   out_3240425447174633819[16] = delta_x[16] + nom_x[16];
   out_3240425447174633819[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_5810796157656117665) {
   out_5810796157656117665[0] = -nom_x[0] + true_x[0];
   out_5810796157656117665[1] = -nom_x[1] + true_x[1];
   out_5810796157656117665[2] = -nom_x[2] + true_x[2];
   out_5810796157656117665[3] = -nom_x[3] + true_x[3];
   out_5810796157656117665[4] = -nom_x[4] + true_x[4];
   out_5810796157656117665[5] = -nom_x[5] + true_x[5];
   out_5810796157656117665[6] = -nom_x[6] + true_x[6];
   out_5810796157656117665[7] = -nom_x[7] + true_x[7];
   out_5810796157656117665[8] = -nom_x[8] + true_x[8];
   out_5810796157656117665[9] = -nom_x[9] + true_x[9];
   out_5810796157656117665[10] = -nom_x[10] + true_x[10];
   out_5810796157656117665[11] = -nom_x[11] + true_x[11];
   out_5810796157656117665[12] = -nom_x[12] + true_x[12];
   out_5810796157656117665[13] = -nom_x[13] + true_x[13];
   out_5810796157656117665[14] = -nom_x[14] + true_x[14];
   out_5810796157656117665[15] = -nom_x[15] + true_x[15];
   out_5810796157656117665[16] = -nom_x[16] + true_x[16];
   out_5810796157656117665[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_1221928615010225756) {
   out_1221928615010225756[0] = 1.0;
   out_1221928615010225756[1] = 0.0;
   out_1221928615010225756[2] = 0.0;
   out_1221928615010225756[3] = 0.0;
   out_1221928615010225756[4] = 0.0;
   out_1221928615010225756[5] = 0.0;
   out_1221928615010225756[6] = 0.0;
   out_1221928615010225756[7] = 0.0;
   out_1221928615010225756[8] = 0.0;
   out_1221928615010225756[9] = 0.0;
   out_1221928615010225756[10] = 0.0;
   out_1221928615010225756[11] = 0.0;
   out_1221928615010225756[12] = 0.0;
   out_1221928615010225756[13] = 0.0;
   out_1221928615010225756[14] = 0.0;
   out_1221928615010225756[15] = 0.0;
   out_1221928615010225756[16] = 0.0;
   out_1221928615010225756[17] = 0.0;
   out_1221928615010225756[18] = 0.0;
   out_1221928615010225756[19] = 1.0;
   out_1221928615010225756[20] = 0.0;
   out_1221928615010225756[21] = 0.0;
   out_1221928615010225756[22] = 0.0;
   out_1221928615010225756[23] = 0.0;
   out_1221928615010225756[24] = 0.0;
   out_1221928615010225756[25] = 0.0;
   out_1221928615010225756[26] = 0.0;
   out_1221928615010225756[27] = 0.0;
   out_1221928615010225756[28] = 0.0;
   out_1221928615010225756[29] = 0.0;
   out_1221928615010225756[30] = 0.0;
   out_1221928615010225756[31] = 0.0;
   out_1221928615010225756[32] = 0.0;
   out_1221928615010225756[33] = 0.0;
   out_1221928615010225756[34] = 0.0;
   out_1221928615010225756[35] = 0.0;
   out_1221928615010225756[36] = 0.0;
   out_1221928615010225756[37] = 0.0;
   out_1221928615010225756[38] = 1.0;
   out_1221928615010225756[39] = 0.0;
   out_1221928615010225756[40] = 0.0;
   out_1221928615010225756[41] = 0.0;
   out_1221928615010225756[42] = 0.0;
   out_1221928615010225756[43] = 0.0;
   out_1221928615010225756[44] = 0.0;
   out_1221928615010225756[45] = 0.0;
   out_1221928615010225756[46] = 0.0;
   out_1221928615010225756[47] = 0.0;
   out_1221928615010225756[48] = 0.0;
   out_1221928615010225756[49] = 0.0;
   out_1221928615010225756[50] = 0.0;
   out_1221928615010225756[51] = 0.0;
   out_1221928615010225756[52] = 0.0;
   out_1221928615010225756[53] = 0.0;
   out_1221928615010225756[54] = 0.0;
   out_1221928615010225756[55] = 0.0;
   out_1221928615010225756[56] = 0.0;
   out_1221928615010225756[57] = 1.0;
   out_1221928615010225756[58] = 0.0;
   out_1221928615010225756[59] = 0.0;
   out_1221928615010225756[60] = 0.0;
   out_1221928615010225756[61] = 0.0;
   out_1221928615010225756[62] = 0.0;
   out_1221928615010225756[63] = 0.0;
   out_1221928615010225756[64] = 0.0;
   out_1221928615010225756[65] = 0.0;
   out_1221928615010225756[66] = 0.0;
   out_1221928615010225756[67] = 0.0;
   out_1221928615010225756[68] = 0.0;
   out_1221928615010225756[69] = 0.0;
   out_1221928615010225756[70] = 0.0;
   out_1221928615010225756[71] = 0.0;
   out_1221928615010225756[72] = 0.0;
   out_1221928615010225756[73] = 0.0;
   out_1221928615010225756[74] = 0.0;
   out_1221928615010225756[75] = 0.0;
   out_1221928615010225756[76] = 1.0;
   out_1221928615010225756[77] = 0.0;
   out_1221928615010225756[78] = 0.0;
   out_1221928615010225756[79] = 0.0;
   out_1221928615010225756[80] = 0.0;
   out_1221928615010225756[81] = 0.0;
   out_1221928615010225756[82] = 0.0;
   out_1221928615010225756[83] = 0.0;
   out_1221928615010225756[84] = 0.0;
   out_1221928615010225756[85] = 0.0;
   out_1221928615010225756[86] = 0.0;
   out_1221928615010225756[87] = 0.0;
   out_1221928615010225756[88] = 0.0;
   out_1221928615010225756[89] = 0.0;
   out_1221928615010225756[90] = 0.0;
   out_1221928615010225756[91] = 0.0;
   out_1221928615010225756[92] = 0.0;
   out_1221928615010225756[93] = 0.0;
   out_1221928615010225756[94] = 0.0;
   out_1221928615010225756[95] = 1.0;
   out_1221928615010225756[96] = 0.0;
   out_1221928615010225756[97] = 0.0;
   out_1221928615010225756[98] = 0.0;
   out_1221928615010225756[99] = 0.0;
   out_1221928615010225756[100] = 0.0;
   out_1221928615010225756[101] = 0.0;
   out_1221928615010225756[102] = 0.0;
   out_1221928615010225756[103] = 0.0;
   out_1221928615010225756[104] = 0.0;
   out_1221928615010225756[105] = 0.0;
   out_1221928615010225756[106] = 0.0;
   out_1221928615010225756[107] = 0.0;
   out_1221928615010225756[108] = 0.0;
   out_1221928615010225756[109] = 0.0;
   out_1221928615010225756[110] = 0.0;
   out_1221928615010225756[111] = 0.0;
   out_1221928615010225756[112] = 0.0;
   out_1221928615010225756[113] = 0.0;
   out_1221928615010225756[114] = 1.0;
   out_1221928615010225756[115] = 0.0;
   out_1221928615010225756[116] = 0.0;
   out_1221928615010225756[117] = 0.0;
   out_1221928615010225756[118] = 0.0;
   out_1221928615010225756[119] = 0.0;
   out_1221928615010225756[120] = 0.0;
   out_1221928615010225756[121] = 0.0;
   out_1221928615010225756[122] = 0.0;
   out_1221928615010225756[123] = 0.0;
   out_1221928615010225756[124] = 0.0;
   out_1221928615010225756[125] = 0.0;
   out_1221928615010225756[126] = 0.0;
   out_1221928615010225756[127] = 0.0;
   out_1221928615010225756[128] = 0.0;
   out_1221928615010225756[129] = 0.0;
   out_1221928615010225756[130] = 0.0;
   out_1221928615010225756[131] = 0.0;
   out_1221928615010225756[132] = 0.0;
   out_1221928615010225756[133] = 1.0;
   out_1221928615010225756[134] = 0.0;
   out_1221928615010225756[135] = 0.0;
   out_1221928615010225756[136] = 0.0;
   out_1221928615010225756[137] = 0.0;
   out_1221928615010225756[138] = 0.0;
   out_1221928615010225756[139] = 0.0;
   out_1221928615010225756[140] = 0.0;
   out_1221928615010225756[141] = 0.0;
   out_1221928615010225756[142] = 0.0;
   out_1221928615010225756[143] = 0.0;
   out_1221928615010225756[144] = 0.0;
   out_1221928615010225756[145] = 0.0;
   out_1221928615010225756[146] = 0.0;
   out_1221928615010225756[147] = 0.0;
   out_1221928615010225756[148] = 0.0;
   out_1221928615010225756[149] = 0.0;
   out_1221928615010225756[150] = 0.0;
   out_1221928615010225756[151] = 0.0;
   out_1221928615010225756[152] = 1.0;
   out_1221928615010225756[153] = 0.0;
   out_1221928615010225756[154] = 0.0;
   out_1221928615010225756[155] = 0.0;
   out_1221928615010225756[156] = 0.0;
   out_1221928615010225756[157] = 0.0;
   out_1221928615010225756[158] = 0.0;
   out_1221928615010225756[159] = 0.0;
   out_1221928615010225756[160] = 0.0;
   out_1221928615010225756[161] = 0.0;
   out_1221928615010225756[162] = 0.0;
   out_1221928615010225756[163] = 0.0;
   out_1221928615010225756[164] = 0.0;
   out_1221928615010225756[165] = 0.0;
   out_1221928615010225756[166] = 0.0;
   out_1221928615010225756[167] = 0.0;
   out_1221928615010225756[168] = 0.0;
   out_1221928615010225756[169] = 0.0;
   out_1221928615010225756[170] = 0.0;
   out_1221928615010225756[171] = 1.0;
   out_1221928615010225756[172] = 0.0;
   out_1221928615010225756[173] = 0.0;
   out_1221928615010225756[174] = 0.0;
   out_1221928615010225756[175] = 0.0;
   out_1221928615010225756[176] = 0.0;
   out_1221928615010225756[177] = 0.0;
   out_1221928615010225756[178] = 0.0;
   out_1221928615010225756[179] = 0.0;
   out_1221928615010225756[180] = 0.0;
   out_1221928615010225756[181] = 0.0;
   out_1221928615010225756[182] = 0.0;
   out_1221928615010225756[183] = 0.0;
   out_1221928615010225756[184] = 0.0;
   out_1221928615010225756[185] = 0.0;
   out_1221928615010225756[186] = 0.0;
   out_1221928615010225756[187] = 0.0;
   out_1221928615010225756[188] = 0.0;
   out_1221928615010225756[189] = 0.0;
   out_1221928615010225756[190] = 1.0;
   out_1221928615010225756[191] = 0.0;
   out_1221928615010225756[192] = 0.0;
   out_1221928615010225756[193] = 0.0;
   out_1221928615010225756[194] = 0.0;
   out_1221928615010225756[195] = 0.0;
   out_1221928615010225756[196] = 0.0;
   out_1221928615010225756[197] = 0.0;
   out_1221928615010225756[198] = 0.0;
   out_1221928615010225756[199] = 0.0;
   out_1221928615010225756[200] = 0.0;
   out_1221928615010225756[201] = 0.0;
   out_1221928615010225756[202] = 0.0;
   out_1221928615010225756[203] = 0.0;
   out_1221928615010225756[204] = 0.0;
   out_1221928615010225756[205] = 0.0;
   out_1221928615010225756[206] = 0.0;
   out_1221928615010225756[207] = 0.0;
   out_1221928615010225756[208] = 0.0;
   out_1221928615010225756[209] = 1.0;
   out_1221928615010225756[210] = 0.0;
   out_1221928615010225756[211] = 0.0;
   out_1221928615010225756[212] = 0.0;
   out_1221928615010225756[213] = 0.0;
   out_1221928615010225756[214] = 0.0;
   out_1221928615010225756[215] = 0.0;
   out_1221928615010225756[216] = 0.0;
   out_1221928615010225756[217] = 0.0;
   out_1221928615010225756[218] = 0.0;
   out_1221928615010225756[219] = 0.0;
   out_1221928615010225756[220] = 0.0;
   out_1221928615010225756[221] = 0.0;
   out_1221928615010225756[222] = 0.0;
   out_1221928615010225756[223] = 0.0;
   out_1221928615010225756[224] = 0.0;
   out_1221928615010225756[225] = 0.0;
   out_1221928615010225756[226] = 0.0;
   out_1221928615010225756[227] = 0.0;
   out_1221928615010225756[228] = 1.0;
   out_1221928615010225756[229] = 0.0;
   out_1221928615010225756[230] = 0.0;
   out_1221928615010225756[231] = 0.0;
   out_1221928615010225756[232] = 0.0;
   out_1221928615010225756[233] = 0.0;
   out_1221928615010225756[234] = 0.0;
   out_1221928615010225756[235] = 0.0;
   out_1221928615010225756[236] = 0.0;
   out_1221928615010225756[237] = 0.0;
   out_1221928615010225756[238] = 0.0;
   out_1221928615010225756[239] = 0.0;
   out_1221928615010225756[240] = 0.0;
   out_1221928615010225756[241] = 0.0;
   out_1221928615010225756[242] = 0.0;
   out_1221928615010225756[243] = 0.0;
   out_1221928615010225756[244] = 0.0;
   out_1221928615010225756[245] = 0.0;
   out_1221928615010225756[246] = 0.0;
   out_1221928615010225756[247] = 1.0;
   out_1221928615010225756[248] = 0.0;
   out_1221928615010225756[249] = 0.0;
   out_1221928615010225756[250] = 0.0;
   out_1221928615010225756[251] = 0.0;
   out_1221928615010225756[252] = 0.0;
   out_1221928615010225756[253] = 0.0;
   out_1221928615010225756[254] = 0.0;
   out_1221928615010225756[255] = 0.0;
   out_1221928615010225756[256] = 0.0;
   out_1221928615010225756[257] = 0.0;
   out_1221928615010225756[258] = 0.0;
   out_1221928615010225756[259] = 0.0;
   out_1221928615010225756[260] = 0.0;
   out_1221928615010225756[261] = 0.0;
   out_1221928615010225756[262] = 0.0;
   out_1221928615010225756[263] = 0.0;
   out_1221928615010225756[264] = 0.0;
   out_1221928615010225756[265] = 0.0;
   out_1221928615010225756[266] = 1.0;
   out_1221928615010225756[267] = 0.0;
   out_1221928615010225756[268] = 0.0;
   out_1221928615010225756[269] = 0.0;
   out_1221928615010225756[270] = 0.0;
   out_1221928615010225756[271] = 0.0;
   out_1221928615010225756[272] = 0.0;
   out_1221928615010225756[273] = 0.0;
   out_1221928615010225756[274] = 0.0;
   out_1221928615010225756[275] = 0.0;
   out_1221928615010225756[276] = 0.0;
   out_1221928615010225756[277] = 0.0;
   out_1221928615010225756[278] = 0.0;
   out_1221928615010225756[279] = 0.0;
   out_1221928615010225756[280] = 0.0;
   out_1221928615010225756[281] = 0.0;
   out_1221928615010225756[282] = 0.0;
   out_1221928615010225756[283] = 0.0;
   out_1221928615010225756[284] = 0.0;
   out_1221928615010225756[285] = 1.0;
   out_1221928615010225756[286] = 0.0;
   out_1221928615010225756[287] = 0.0;
   out_1221928615010225756[288] = 0.0;
   out_1221928615010225756[289] = 0.0;
   out_1221928615010225756[290] = 0.0;
   out_1221928615010225756[291] = 0.0;
   out_1221928615010225756[292] = 0.0;
   out_1221928615010225756[293] = 0.0;
   out_1221928615010225756[294] = 0.0;
   out_1221928615010225756[295] = 0.0;
   out_1221928615010225756[296] = 0.0;
   out_1221928615010225756[297] = 0.0;
   out_1221928615010225756[298] = 0.0;
   out_1221928615010225756[299] = 0.0;
   out_1221928615010225756[300] = 0.0;
   out_1221928615010225756[301] = 0.0;
   out_1221928615010225756[302] = 0.0;
   out_1221928615010225756[303] = 0.0;
   out_1221928615010225756[304] = 1.0;
   out_1221928615010225756[305] = 0.0;
   out_1221928615010225756[306] = 0.0;
   out_1221928615010225756[307] = 0.0;
   out_1221928615010225756[308] = 0.0;
   out_1221928615010225756[309] = 0.0;
   out_1221928615010225756[310] = 0.0;
   out_1221928615010225756[311] = 0.0;
   out_1221928615010225756[312] = 0.0;
   out_1221928615010225756[313] = 0.0;
   out_1221928615010225756[314] = 0.0;
   out_1221928615010225756[315] = 0.0;
   out_1221928615010225756[316] = 0.0;
   out_1221928615010225756[317] = 0.0;
   out_1221928615010225756[318] = 0.0;
   out_1221928615010225756[319] = 0.0;
   out_1221928615010225756[320] = 0.0;
   out_1221928615010225756[321] = 0.0;
   out_1221928615010225756[322] = 0.0;
   out_1221928615010225756[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_6673196704848212167) {
   out_6673196704848212167[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_6673196704848212167[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_6673196704848212167[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_6673196704848212167[3] = dt*state[12] + state[3];
   out_6673196704848212167[4] = dt*state[13] + state[4];
   out_6673196704848212167[5] = dt*state[14] + state[5];
   out_6673196704848212167[6] = state[6];
   out_6673196704848212167[7] = state[7];
   out_6673196704848212167[8] = state[8];
   out_6673196704848212167[9] = state[9];
   out_6673196704848212167[10] = state[10];
   out_6673196704848212167[11] = state[11];
   out_6673196704848212167[12] = state[12];
   out_6673196704848212167[13] = state[13];
   out_6673196704848212167[14] = state[14];
   out_6673196704848212167[15] = state[15];
   out_6673196704848212167[16] = state[16];
   out_6673196704848212167[17] = state[17];
}
void F_fun(double *state, double dt, double *out_9126575036203471234) {
   out_9126575036203471234[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_9126575036203471234[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_9126575036203471234[2] = 0;
   out_9126575036203471234[3] = 0;
   out_9126575036203471234[4] = 0;
   out_9126575036203471234[5] = 0;
   out_9126575036203471234[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_9126575036203471234[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_9126575036203471234[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_9126575036203471234[9] = 0;
   out_9126575036203471234[10] = 0;
   out_9126575036203471234[11] = 0;
   out_9126575036203471234[12] = 0;
   out_9126575036203471234[13] = 0;
   out_9126575036203471234[14] = 0;
   out_9126575036203471234[15] = 0;
   out_9126575036203471234[16] = 0;
   out_9126575036203471234[17] = 0;
   out_9126575036203471234[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_9126575036203471234[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_9126575036203471234[20] = 0;
   out_9126575036203471234[21] = 0;
   out_9126575036203471234[22] = 0;
   out_9126575036203471234[23] = 0;
   out_9126575036203471234[24] = 0;
   out_9126575036203471234[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_9126575036203471234[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_9126575036203471234[27] = 0;
   out_9126575036203471234[28] = 0;
   out_9126575036203471234[29] = 0;
   out_9126575036203471234[30] = 0;
   out_9126575036203471234[31] = 0;
   out_9126575036203471234[32] = 0;
   out_9126575036203471234[33] = 0;
   out_9126575036203471234[34] = 0;
   out_9126575036203471234[35] = 0;
   out_9126575036203471234[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_9126575036203471234[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_9126575036203471234[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_9126575036203471234[39] = 0;
   out_9126575036203471234[40] = 0;
   out_9126575036203471234[41] = 0;
   out_9126575036203471234[42] = 0;
   out_9126575036203471234[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_9126575036203471234[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_9126575036203471234[45] = 0;
   out_9126575036203471234[46] = 0;
   out_9126575036203471234[47] = 0;
   out_9126575036203471234[48] = 0;
   out_9126575036203471234[49] = 0;
   out_9126575036203471234[50] = 0;
   out_9126575036203471234[51] = 0;
   out_9126575036203471234[52] = 0;
   out_9126575036203471234[53] = 0;
   out_9126575036203471234[54] = 0;
   out_9126575036203471234[55] = 0;
   out_9126575036203471234[56] = 0;
   out_9126575036203471234[57] = 1;
   out_9126575036203471234[58] = 0;
   out_9126575036203471234[59] = 0;
   out_9126575036203471234[60] = 0;
   out_9126575036203471234[61] = 0;
   out_9126575036203471234[62] = 0;
   out_9126575036203471234[63] = 0;
   out_9126575036203471234[64] = 0;
   out_9126575036203471234[65] = 0;
   out_9126575036203471234[66] = dt;
   out_9126575036203471234[67] = 0;
   out_9126575036203471234[68] = 0;
   out_9126575036203471234[69] = 0;
   out_9126575036203471234[70] = 0;
   out_9126575036203471234[71] = 0;
   out_9126575036203471234[72] = 0;
   out_9126575036203471234[73] = 0;
   out_9126575036203471234[74] = 0;
   out_9126575036203471234[75] = 0;
   out_9126575036203471234[76] = 1;
   out_9126575036203471234[77] = 0;
   out_9126575036203471234[78] = 0;
   out_9126575036203471234[79] = 0;
   out_9126575036203471234[80] = 0;
   out_9126575036203471234[81] = 0;
   out_9126575036203471234[82] = 0;
   out_9126575036203471234[83] = 0;
   out_9126575036203471234[84] = 0;
   out_9126575036203471234[85] = dt;
   out_9126575036203471234[86] = 0;
   out_9126575036203471234[87] = 0;
   out_9126575036203471234[88] = 0;
   out_9126575036203471234[89] = 0;
   out_9126575036203471234[90] = 0;
   out_9126575036203471234[91] = 0;
   out_9126575036203471234[92] = 0;
   out_9126575036203471234[93] = 0;
   out_9126575036203471234[94] = 0;
   out_9126575036203471234[95] = 1;
   out_9126575036203471234[96] = 0;
   out_9126575036203471234[97] = 0;
   out_9126575036203471234[98] = 0;
   out_9126575036203471234[99] = 0;
   out_9126575036203471234[100] = 0;
   out_9126575036203471234[101] = 0;
   out_9126575036203471234[102] = 0;
   out_9126575036203471234[103] = 0;
   out_9126575036203471234[104] = dt;
   out_9126575036203471234[105] = 0;
   out_9126575036203471234[106] = 0;
   out_9126575036203471234[107] = 0;
   out_9126575036203471234[108] = 0;
   out_9126575036203471234[109] = 0;
   out_9126575036203471234[110] = 0;
   out_9126575036203471234[111] = 0;
   out_9126575036203471234[112] = 0;
   out_9126575036203471234[113] = 0;
   out_9126575036203471234[114] = 1;
   out_9126575036203471234[115] = 0;
   out_9126575036203471234[116] = 0;
   out_9126575036203471234[117] = 0;
   out_9126575036203471234[118] = 0;
   out_9126575036203471234[119] = 0;
   out_9126575036203471234[120] = 0;
   out_9126575036203471234[121] = 0;
   out_9126575036203471234[122] = 0;
   out_9126575036203471234[123] = 0;
   out_9126575036203471234[124] = 0;
   out_9126575036203471234[125] = 0;
   out_9126575036203471234[126] = 0;
   out_9126575036203471234[127] = 0;
   out_9126575036203471234[128] = 0;
   out_9126575036203471234[129] = 0;
   out_9126575036203471234[130] = 0;
   out_9126575036203471234[131] = 0;
   out_9126575036203471234[132] = 0;
   out_9126575036203471234[133] = 1;
   out_9126575036203471234[134] = 0;
   out_9126575036203471234[135] = 0;
   out_9126575036203471234[136] = 0;
   out_9126575036203471234[137] = 0;
   out_9126575036203471234[138] = 0;
   out_9126575036203471234[139] = 0;
   out_9126575036203471234[140] = 0;
   out_9126575036203471234[141] = 0;
   out_9126575036203471234[142] = 0;
   out_9126575036203471234[143] = 0;
   out_9126575036203471234[144] = 0;
   out_9126575036203471234[145] = 0;
   out_9126575036203471234[146] = 0;
   out_9126575036203471234[147] = 0;
   out_9126575036203471234[148] = 0;
   out_9126575036203471234[149] = 0;
   out_9126575036203471234[150] = 0;
   out_9126575036203471234[151] = 0;
   out_9126575036203471234[152] = 1;
   out_9126575036203471234[153] = 0;
   out_9126575036203471234[154] = 0;
   out_9126575036203471234[155] = 0;
   out_9126575036203471234[156] = 0;
   out_9126575036203471234[157] = 0;
   out_9126575036203471234[158] = 0;
   out_9126575036203471234[159] = 0;
   out_9126575036203471234[160] = 0;
   out_9126575036203471234[161] = 0;
   out_9126575036203471234[162] = 0;
   out_9126575036203471234[163] = 0;
   out_9126575036203471234[164] = 0;
   out_9126575036203471234[165] = 0;
   out_9126575036203471234[166] = 0;
   out_9126575036203471234[167] = 0;
   out_9126575036203471234[168] = 0;
   out_9126575036203471234[169] = 0;
   out_9126575036203471234[170] = 0;
   out_9126575036203471234[171] = 1;
   out_9126575036203471234[172] = 0;
   out_9126575036203471234[173] = 0;
   out_9126575036203471234[174] = 0;
   out_9126575036203471234[175] = 0;
   out_9126575036203471234[176] = 0;
   out_9126575036203471234[177] = 0;
   out_9126575036203471234[178] = 0;
   out_9126575036203471234[179] = 0;
   out_9126575036203471234[180] = 0;
   out_9126575036203471234[181] = 0;
   out_9126575036203471234[182] = 0;
   out_9126575036203471234[183] = 0;
   out_9126575036203471234[184] = 0;
   out_9126575036203471234[185] = 0;
   out_9126575036203471234[186] = 0;
   out_9126575036203471234[187] = 0;
   out_9126575036203471234[188] = 0;
   out_9126575036203471234[189] = 0;
   out_9126575036203471234[190] = 1;
   out_9126575036203471234[191] = 0;
   out_9126575036203471234[192] = 0;
   out_9126575036203471234[193] = 0;
   out_9126575036203471234[194] = 0;
   out_9126575036203471234[195] = 0;
   out_9126575036203471234[196] = 0;
   out_9126575036203471234[197] = 0;
   out_9126575036203471234[198] = 0;
   out_9126575036203471234[199] = 0;
   out_9126575036203471234[200] = 0;
   out_9126575036203471234[201] = 0;
   out_9126575036203471234[202] = 0;
   out_9126575036203471234[203] = 0;
   out_9126575036203471234[204] = 0;
   out_9126575036203471234[205] = 0;
   out_9126575036203471234[206] = 0;
   out_9126575036203471234[207] = 0;
   out_9126575036203471234[208] = 0;
   out_9126575036203471234[209] = 1;
   out_9126575036203471234[210] = 0;
   out_9126575036203471234[211] = 0;
   out_9126575036203471234[212] = 0;
   out_9126575036203471234[213] = 0;
   out_9126575036203471234[214] = 0;
   out_9126575036203471234[215] = 0;
   out_9126575036203471234[216] = 0;
   out_9126575036203471234[217] = 0;
   out_9126575036203471234[218] = 0;
   out_9126575036203471234[219] = 0;
   out_9126575036203471234[220] = 0;
   out_9126575036203471234[221] = 0;
   out_9126575036203471234[222] = 0;
   out_9126575036203471234[223] = 0;
   out_9126575036203471234[224] = 0;
   out_9126575036203471234[225] = 0;
   out_9126575036203471234[226] = 0;
   out_9126575036203471234[227] = 0;
   out_9126575036203471234[228] = 1;
   out_9126575036203471234[229] = 0;
   out_9126575036203471234[230] = 0;
   out_9126575036203471234[231] = 0;
   out_9126575036203471234[232] = 0;
   out_9126575036203471234[233] = 0;
   out_9126575036203471234[234] = 0;
   out_9126575036203471234[235] = 0;
   out_9126575036203471234[236] = 0;
   out_9126575036203471234[237] = 0;
   out_9126575036203471234[238] = 0;
   out_9126575036203471234[239] = 0;
   out_9126575036203471234[240] = 0;
   out_9126575036203471234[241] = 0;
   out_9126575036203471234[242] = 0;
   out_9126575036203471234[243] = 0;
   out_9126575036203471234[244] = 0;
   out_9126575036203471234[245] = 0;
   out_9126575036203471234[246] = 0;
   out_9126575036203471234[247] = 1;
   out_9126575036203471234[248] = 0;
   out_9126575036203471234[249] = 0;
   out_9126575036203471234[250] = 0;
   out_9126575036203471234[251] = 0;
   out_9126575036203471234[252] = 0;
   out_9126575036203471234[253] = 0;
   out_9126575036203471234[254] = 0;
   out_9126575036203471234[255] = 0;
   out_9126575036203471234[256] = 0;
   out_9126575036203471234[257] = 0;
   out_9126575036203471234[258] = 0;
   out_9126575036203471234[259] = 0;
   out_9126575036203471234[260] = 0;
   out_9126575036203471234[261] = 0;
   out_9126575036203471234[262] = 0;
   out_9126575036203471234[263] = 0;
   out_9126575036203471234[264] = 0;
   out_9126575036203471234[265] = 0;
   out_9126575036203471234[266] = 1;
   out_9126575036203471234[267] = 0;
   out_9126575036203471234[268] = 0;
   out_9126575036203471234[269] = 0;
   out_9126575036203471234[270] = 0;
   out_9126575036203471234[271] = 0;
   out_9126575036203471234[272] = 0;
   out_9126575036203471234[273] = 0;
   out_9126575036203471234[274] = 0;
   out_9126575036203471234[275] = 0;
   out_9126575036203471234[276] = 0;
   out_9126575036203471234[277] = 0;
   out_9126575036203471234[278] = 0;
   out_9126575036203471234[279] = 0;
   out_9126575036203471234[280] = 0;
   out_9126575036203471234[281] = 0;
   out_9126575036203471234[282] = 0;
   out_9126575036203471234[283] = 0;
   out_9126575036203471234[284] = 0;
   out_9126575036203471234[285] = 1;
   out_9126575036203471234[286] = 0;
   out_9126575036203471234[287] = 0;
   out_9126575036203471234[288] = 0;
   out_9126575036203471234[289] = 0;
   out_9126575036203471234[290] = 0;
   out_9126575036203471234[291] = 0;
   out_9126575036203471234[292] = 0;
   out_9126575036203471234[293] = 0;
   out_9126575036203471234[294] = 0;
   out_9126575036203471234[295] = 0;
   out_9126575036203471234[296] = 0;
   out_9126575036203471234[297] = 0;
   out_9126575036203471234[298] = 0;
   out_9126575036203471234[299] = 0;
   out_9126575036203471234[300] = 0;
   out_9126575036203471234[301] = 0;
   out_9126575036203471234[302] = 0;
   out_9126575036203471234[303] = 0;
   out_9126575036203471234[304] = 1;
   out_9126575036203471234[305] = 0;
   out_9126575036203471234[306] = 0;
   out_9126575036203471234[307] = 0;
   out_9126575036203471234[308] = 0;
   out_9126575036203471234[309] = 0;
   out_9126575036203471234[310] = 0;
   out_9126575036203471234[311] = 0;
   out_9126575036203471234[312] = 0;
   out_9126575036203471234[313] = 0;
   out_9126575036203471234[314] = 0;
   out_9126575036203471234[315] = 0;
   out_9126575036203471234[316] = 0;
   out_9126575036203471234[317] = 0;
   out_9126575036203471234[318] = 0;
   out_9126575036203471234[319] = 0;
   out_9126575036203471234[320] = 0;
   out_9126575036203471234[321] = 0;
   out_9126575036203471234[322] = 0;
   out_9126575036203471234[323] = 1;
}
void h_4(double *state, double *unused, double *out_4184048412485075607) {
   out_4184048412485075607[0] = state[6] + state[9];
   out_4184048412485075607[1] = state[7] + state[10];
   out_4184048412485075607[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_1978481286091244268) {
   out_1978481286091244268[0] = 0;
   out_1978481286091244268[1] = 0;
   out_1978481286091244268[2] = 0;
   out_1978481286091244268[3] = 0;
   out_1978481286091244268[4] = 0;
   out_1978481286091244268[5] = 0;
   out_1978481286091244268[6] = 1;
   out_1978481286091244268[7] = 0;
   out_1978481286091244268[8] = 0;
   out_1978481286091244268[9] = 1;
   out_1978481286091244268[10] = 0;
   out_1978481286091244268[11] = 0;
   out_1978481286091244268[12] = 0;
   out_1978481286091244268[13] = 0;
   out_1978481286091244268[14] = 0;
   out_1978481286091244268[15] = 0;
   out_1978481286091244268[16] = 0;
   out_1978481286091244268[17] = 0;
   out_1978481286091244268[18] = 0;
   out_1978481286091244268[19] = 0;
   out_1978481286091244268[20] = 0;
   out_1978481286091244268[21] = 0;
   out_1978481286091244268[22] = 0;
   out_1978481286091244268[23] = 0;
   out_1978481286091244268[24] = 0;
   out_1978481286091244268[25] = 1;
   out_1978481286091244268[26] = 0;
   out_1978481286091244268[27] = 0;
   out_1978481286091244268[28] = 1;
   out_1978481286091244268[29] = 0;
   out_1978481286091244268[30] = 0;
   out_1978481286091244268[31] = 0;
   out_1978481286091244268[32] = 0;
   out_1978481286091244268[33] = 0;
   out_1978481286091244268[34] = 0;
   out_1978481286091244268[35] = 0;
   out_1978481286091244268[36] = 0;
   out_1978481286091244268[37] = 0;
   out_1978481286091244268[38] = 0;
   out_1978481286091244268[39] = 0;
   out_1978481286091244268[40] = 0;
   out_1978481286091244268[41] = 0;
   out_1978481286091244268[42] = 0;
   out_1978481286091244268[43] = 0;
   out_1978481286091244268[44] = 1;
   out_1978481286091244268[45] = 0;
   out_1978481286091244268[46] = 0;
   out_1978481286091244268[47] = 1;
   out_1978481286091244268[48] = 0;
   out_1978481286091244268[49] = 0;
   out_1978481286091244268[50] = 0;
   out_1978481286091244268[51] = 0;
   out_1978481286091244268[52] = 0;
   out_1978481286091244268[53] = 0;
}
void h_10(double *state, double *unused, double *out_747511093795381270) {
   out_747511093795381270[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_747511093795381270[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_747511093795381270[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_3506143025433361193) {
   out_3506143025433361193[0] = 0;
   out_3506143025433361193[1] = 9.8100000000000005*cos(state[1]);
   out_3506143025433361193[2] = 0;
   out_3506143025433361193[3] = 0;
   out_3506143025433361193[4] = -state[8];
   out_3506143025433361193[5] = state[7];
   out_3506143025433361193[6] = 0;
   out_3506143025433361193[7] = state[5];
   out_3506143025433361193[8] = -state[4];
   out_3506143025433361193[9] = 0;
   out_3506143025433361193[10] = 0;
   out_3506143025433361193[11] = 0;
   out_3506143025433361193[12] = 1;
   out_3506143025433361193[13] = 0;
   out_3506143025433361193[14] = 0;
   out_3506143025433361193[15] = 1;
   out_3506143025433361193[16] = 0;
   out_3506143025433361193[17] = 0;
   out_3506143025433361193[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_3506143025433361193[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_3506143025433361193[20] = 0;
   out_3506143025433361193[21] = state[8];
   out_3506143025433361193[22] = 0;
   out_3506143025433361193[23] = -state[6];
   out_3506143025433361193[24] = -state[5];
   out_3506143025433361193[25] = 0;
   out_3506143025433361193[26] = state[3];
   out_3506143025433361193[27] = 0;
   out_3506143025433361193[28] = 0;
   out_3506143025433361193[29] = 0;
   out_3506143025433361193[30] = 0;
   out_3506143025433361193[31] = 1;
   out_3506143025433361193[32] = 0;
   out_3506143025433361193[33] = 0;
   out_3506143025433361193[34] = 1;
   out_3506143025433361193[35] = 0;
   out_3506143025433361193[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_3506143025433361193[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_3506143025433361193[38] = 0;
   out_3506143025433361193[39] = -state[7];
   out_3506143025433361193[40] = state[6];
   out_3506143025433361193[41] = 0;
   out_3506143025433361193[42] = state[4];
   out_3506143025433361193[43] = -state[3];
   out_3506143025433361193[44] = 0;
   out_3506143025433361193[45] = 0;
   out_3506143025433361193[46] = 0;
   out_3506143025433361193[47] = 0;
   out_3506143025433361193[48] = 0;
   out_3506143025433361193[49] = 0;
   out_3506143025433361193[50] = 1;
   out_3506143025433361193[51] = 0;
   out_3506143025433361193[52] = 0;
   out_3506143025433361193[53] = 1;
}
void h_13(double *state, double *unused, double *out_8398284471669141404) {
   out_8398284471669141404[0] = state[3];
   out_8398284471669141404[1] = state[4];
   out_8398284471669141404[2] = state[5];
}
void H_13(double *state, double *unused, double *out_5632149922225456661) {
   out_5632149922225456661[0] = 0;
   out_5632149922225456661[1] = 0;
   out_5632149922225456661[2] = 0;
   out_5632149922225456661[3] = 1;
   out_5632149922225456661[4] = 0;
   out_5632149922225456661[5] = 0;
   out_5632149922225456661[6] = 0;
   out_5632149922225456661[7] = 0;
   out_5632149922225456661[8] = 0;
   out_5632149922225456661[9] = 0;
   out_5632149922225456661[10] = 0;
   out_5632149922225456661[11] = 0;
   out_5632149922225456661[12] = 0;
   out_5632149922225456661[13] = 0;
   out_5632149922225456661[14] = 0;
   out_5632149922225456661[15] = 0;
   out_5632149922225456661[16] = 0;
   out_5632149922225456661[17] = 0;
   out_5632149922225456661[18] = 0;
   out_5632149922225456661[19] = 0;
   out_5632149922225456661[20] = 0;
   out_5632149922225456661[21] = 0;
   out_5632149922225456661[22] = 1;
   out_5632149922225456661[23] = 0;
   out_5632149922225456661[24] = 0;
   out_5632149922225456661[25] = 0;
   out_5632149922225456661[26] = 0;
   out_5632149922225456661[27] = 0;
   out_5632149922225456661[28] = 0;
   out_5632149922225456661[29] = 0;
   out_5632149922225456661[30] = 0;
   out_5632149922225456661[31] = 0;
   out_5632149922225456661[32] = 0;
   out_5632149922225456661[33] = 0;
   out_5632149922225456661[34] = 0;
   out_5632149922225456661[35] = 0;
   out_5632149922225456661[36] = 0;
   out_5632149922225456661[37] = 0;
   out_5632149922225456661[38] = 0;
   out_5632149922225456661[39] = 0;
   out_5632149922225456661[40] = 0;
   out_5632149922225456661[41] = 1;
   out_5632149922225456661[42] = 0;
   out_5632149922225456661[43] = 0;
   out_5632149922225456661[44] = 0;
   out_5632149922225456661[45] = 0;
   out_5632149922225456661[46] = 0;
   out_5632149922225456661[47] = 0;
   out_5632149922225456661[48] = 0;
   out_5632149922225456661[49] = 0;
   out_5632149922225456661[50] = 0;
   out_5632149922225456661[51] = 0;
   out_5632149922225456661[52] = 0;
   out_5632149922225456661[53] = 0;
}
void h_14(double *state, double *unused, double *out_7822783238651142803) {
   out_7822783238651142803[0] = state[6];
   out_7822783238651142803[1] = state[7];
   out_7822783238651142803[2] = state[8];
}
void H_14(double *state, double *unused, double *out_1984759570248240261) {
   out_1984759570248240261[0] = 0;
   out_1984759570248240261[1] = 0;
   out_1984759570248240261[2] = 0;
   out_1984759570248240261[3] = 0;
   out_1984759570248240261[4] = 0;
   out_1984759570248240261[5] = 0;
   out_1984759570248240261[6] = 1;
   out_1984759570248240261[7] = 0;
   out_1984759570248240261[8] = 0;
   out_1984759570248240261[9] = 0;
   out_1984759570248240261[10] = 0;
   out_1984759570248240261[11] = 0;
   out_1984759570248240261[12] = 0;
   out_1984759570248240261[13] = 0;
   out_1984759570248240261[14] = 0;
   out_1984759570248240261[15] = 0;
   out_1984759570248240261[16] = 0;
   out_1984759570248240261[17] = 0;
   out_1984759570248240261[18] = 0;
   out_1984759570248240261[19] = 0;
   out_1984759570248240261[20] = 0;
   out_1984759570248240261[21] = 0;
   out_1984759570248240261[22] = 0;
   out_1984759570248240261[23] = 0;
   out_1984759570248240261[24] = 0;
   out_1984759570248240261[25] = 1;
   out_1984759570248240261[26] = 0;
   out_1984759570248240261[27] = 0;
   out_1984759570248240261[28] = 0;
   out_1984759570248240261[29] = 0;
   out_1984759570248240261[30] = 0;
   out_1984759570248240261[31] = 0;
   out_1984759570248240261[32] = 0;
   out_1984759570248240261[33] = 0;
   out_1984759570248240261[34] = 0;
   out_1984759570248240261[35] = 0;
   out_1984759570248240261[36] = 0;
   out_1984759570248240261[37] = 0;
   out_1984759570248240261[38] = 0;
   out_1984759570248240261[39] = 0;
   out_1984759570248240261[40] = 0;
   out_1984759570248240261[41] = 0;
   out_1984759570248240261[42] = 0;
   out_1984759570248240261[43] = 0;
   out_1984759570248240261[44] = 1;
   out_1984759570248240261[45] = 0;
   out_1984759570248240261[46] = 0;
   out_1984759570248240261[47] = 0;
   out_1984759570248240261[48] = 0;
   out_1984759570248240261[49] = 0;
   out_1984759570248240261[50] = 0;
   out_1984759570248240261[51] = 0;
   out_1984759570248240261[52] = 0;
   out_1984759570248240261[53] = 0;
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
void pose_err_fun(double *nom_x, double *delta_x, double *out_3240425447174633819) {
  err_fun(nom_x, delta_x, out_3240425447174633819);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_5810796157656117665) {
  inv_err_fun(nom_x, true_x, out_5810796157656117665);
}
void pose_H_mod_fun(double *state, double *out_1221928615010225756) {
  H_mod_fun(state, out_1221928615010225756);
}
void pose_f_fun(double *state, double dt, double *out_6673196704848212167) {
  f_fun(state,  dt, out_6673196704848212167);
}
void pose_F_fun(double *state, double dt, double *out_9126575036203471234) {
  F_fun(state,  dt, out_9126575036203471234);
}
void pose_h_4(double *state, double *unused, double *out_4184048412485075607) {
  h_4(state, unused, out_4184048412485075607);
}
void pose_H_4(double *state, double *unused, double *out_1978481286091244268) {
  H_4(state, unused, out_1978481286091244268);
}
void pose_h_10(double *state, double *unused, double *out_747511093795381270) {
  h_10(state, unused, out_747511093795381270);
}
void pose_H_10(double *state, double *unused, double *out_3506143025433361193) {
  H_10(state, unused, out_3506143025433361193);
}
void pose_h_13(double *state, double *unused, double *out_8398284471669141404) {
  h_13(state, unused, out_8398284471669141404);
}
void pose_H_13(double *state, double *unused, double *out_5632149922225456661) {
  H_13(state, unused, out_5632149922225456661);
}
void pose_h_14(double *state, double *unused, double *out_7822783238651142803) {
  h_14(state, unused, out_7822783238651142803);
}
void pose_H_14(double *state, double *unused, double *out_1984759570248240261) {
  H_14(state, unused, out_1984759570248240261);
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
