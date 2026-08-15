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
void err_fun(double *nom_x, double *delta_x, double *out_5688174754372622748) {
   out_5688174754372622748[0] = delta_x[0] + nom_x[0];
   out_5688174754372622748[1] = delta_x[1] + nom_x[1];
   out_5688174754372622748[2] = delta_x[2] + nom_x[2];
   out_5688174754372622748[3] = delta_x[3] + nom_x[3];
   out_5688174754372622748[4] = delta_x[4] + nom_x[4];
   out_5688174754372622748[5] = delta_x[5] + nom_x[5];
   out_5688174754372622748[6] = delta_x[6] + nom_x[6];
   out_5688174754372622748[7] = delta_x[7] + nom_x[7];
   out_5688174754372622748[8] = delta_x[8] + nom_x[8];
   out_5688174754372622748[9] = delta_x[9] + nom_x[9];
   out_5688174754372622748[10] = delta_x[10] + nom_x[10];
   out_5688174754372622748[11] = delta_x[11] + nom_x[11];
   out_5688174754372622748[12] = delta_x[12] + nom_x[12];
   out_5688174754372622748[13] = delta_x[13] + nom_x[13];
   out_5688174754372622748[14] = delta_x[14] + nom_x[14];
   out_5688174754372622748[15] = delta_x[15] + nom_x[15];
   out_5688174754372622748[16] = delta_x[16] + nom_x[16];
   out_5688174754372622748[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_598026621986152539) {
   out_598026621986152539[0] = -nom_x[0] + true_x[0];
   out_598026621986152539[1] = -nom_x[1] + true_x[1];
   out_598026621986152539[2] = -nom_x[2] + true_x[2];
   out_598026621986152539[3] = -nom_x[3] + true_x[3];
   out_598026621986152539[4] = -nom_x[4] + true_x[4];
   out_598026621986152539[5] = -nom_x[5] + true_x[5];
   out_598026621986152539[6] = -nom_x[6] + true_x[6];
   out_598026621986152539[7] = -nom_x[7] + true_x[7];
   out_598026621986152539[8] = -nom_x[8] + true_x[8];
   out_598026621986152539[9] = -nom_x[9] + true_x[9];
   out_598026621986152539[10] = -nom_x[10] + true_x[10];
   out_598026621986152539[11] = -nom_x[11] + true_x[11];
   out_598026621986152539[12] = -nom_x[12] + true_x[12];
   out_598026621986152539[13] = -nom_x[13] + true_x[13];
   out_598026621986152539[14] = -nom_x[14] + true_x[14];
   out_598026621986152539[15] = -nom_x[15] + true_x[15];
   out_598026621986152539[16] = -nom_x[16] + true_x[16];
   out_598026621986152539[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_2381892679141553073) {
   out_2381892679141553073[0] = 1.0;
   out_2381892679141553073[1] = 0.0;
   out_2381892679141553073[2] = 0.0;
   out_2381892679141553073[3] = 0.0;
   out_2381892679141553073[4] = 0.0;
   out_2381892679141553073[5] = 0.0;
   out_2381892679141553073[6] = 0.0;
   out_2381892679141553073[7] = 0.0;
   out_2381892679141553073[8] = 0.0;
   out_2381892679141553073[9] = 0.0;
   out_2381892679141553073[10] = 0.0;
   out_2381892679141553073[11] = 0.0;
   out_2381892679141553073[12] = 0.0;
   out_2381892679141553073[13] = 0.0;
   out_2381892679141553073[14] = 0.0;
   out_2381892679141553073[15] = 0.0;
   out_2381892679141553073[16] = 0.0;
   out_2381892679141553073[17] = 0.0;
   out_2381892679141553073[18] = 0.0;
   out_2381892679141553073[19] = 1.0;
   out_2381892679141553073[20] = 0.0;
   out_2381892679141553073[21] = 0.0;
   out_2381892679141553073[22] = 0.0;
   out_2381892679141553073[23] = 0.0;
   out_2381892679141553073[24] = 0.0;
   out_2381892679141553073[25] = 0.0;
   out_2381892679141553073[26] = 0.0;
   out_2381892679141553073[27] = 0.0;
   out_2381892679141553073[28] = 0.0;
   out_2381892679141553073[29] = 0.0;
   out_2381892679141553073[30] = 0.0;
   out_2381892679141553073[31] = 0.0;
   out_2381892679141553073[32] = 0.0;
   out_2381892679141553073[33] = 0.0;
   out_2381892679141553073[34] = 0.0;
   out_2381892679141553073[35] = 0.0;
   out_2381892679141553073[36] = 0.0;
   out_2381892679141553073[37] = 0.0;
   out_2381892679141553073[38] = 1.0;
   out_2381892679141553073[39] = 0.0;
   out_2381892679141553073[40] = 0.0;
   out_2381892679141553073[41] = 0.0;
   out_2381892679141553073[42] = 0.0;
   out_2381892679141553073[43] = 0.0;
   out_2381892679141553073[44] = 0.0;
   out_2381892679141553073[45] = 0.0;
   out_2381892679141553073[46] = 0.0;
   out_2381892679141553073[47] = 0.0;
   out_2381892679141553073[48] = 0.0;
   out_2381892679141553073[49] = 0.0;
   out_2381892679141553073[50] = 0.0;
   out_2381892679141553073[51] = 0.0;
   out_2381892679141553073[52] = 0.0;
   out_2381892679141553073[53] = 0.0;
   out_2381892679141553073[54] = 0.0;
   out_2381892679141553073[55] = 0.0;
   out_2381892679141553073[56] = 0.0;
   out_2381892679141553073[57] = 1.0;
   out_2381892679141553073[58] = 0.0;
   out_2381892679141553073[59] = 0.0;
   out_2381892679141553073[60] = 0.0;
   out_2381892679141553073[61] = 0.0;
   out_2381892679141553073[62] = 0.0;
   out_2381892679141553073[63] = 0.0;
   out_2381892679141553073[64] = 0.0;
   out_2381892679141553073[65] = 0.0;
   out_2381892679141553073[66] = 0.0;
   out_2381892679141553073[67] = 0.0;
   out_2381892679141553073[68] = 0.0;
   out_2381892679141553073[69] = 0.0;
   out_2381892679141553073[70] = 0.0;
   out_2381892679141553073[71] = 0.0;
   out_2381892679141553073[72] = 0.0;
   out_2381892679141553073[73] = 0.0;
   out_2381892679141553073[74] = 0.0;
   out_2381892679141553073[75] = 0.0;
   out_2381892679141553073[76] = 1.0;
   out_2381892679141553073[77] = 0.0;
   out_2381892679141553073[78] = 0.0;
   out_2381892679141553073[79] = 0.0;
   out_2381892679141553073[80] = 0.0;
   out_2381892679141553073[81] = 0.0;
   out_2381892679141553073[82] = 0.0;
   out_2381892679141553073[83] = 0.0;
   out_2381892679141553073[84] = 0.0;
   out_2381892679141553073[85] = 0.0;
   out_2381892679141553073[86] = 0.0;
   out_2381892679141553073[87] = 0.0;
   out_2381892679141553073[88] = 0.0;
   out_2381892679141553073[89] = 0.0;
   out_2381892679141553073[90] = 0.0;
   out_2381892679141553073[91] = 0.0;
   out_2381892679141553073[92] = 0.0;
   out_2381892679141553073[93] = 0.0;
   out_2381892679141553073[94] = 0.0;
   out_2381892679141553073[95] = 1.0;
   out_2381892679141553073[96] = 0.0;
   out_2381892679141553073[97] = 0.0;
   out_2381892679141553073[98] = 0.0;
   out_2381892679141553073[99] = 0.0;
   out_2381892679141553073[100] = 0.0;
   out_2381892679141553073[101] = 0.0;
   out_2381892679141553073[102] = 0.0;
   out_2381892679141553073[103] = 0.0;
   out_2381892679141553073[104] = 0.0;
   out_2381892679141553073[105] = 0.0;
   out_2381892679141553073[106] = 0.0;
   out_2381892679141553073[107] = 0.0;
   out_2381892679141553073[108] = 0.0;
   out_2381892679141553073[109] = 0.0;
   out_2381892679141553073[110] = 0.0;
   out_2381892679141553073[111] = 0.0;
   out_2381892679141553073[112] = 0.0;
   out_2381892679141553073[113] = 0.0;
   out_2381892679141553073[114] = 1.0;
   out_2381892679141553073[115] = 0.0;
   out_2381892679141553073[116] = 0.0;
   out_2381892679141553073[117] = 0.0;
   out_2381892679141553073[118] = 0.0;
   out_2381892679141553073[119] = 0.0;
   out_2381892679141553073[120] = 0.0;
   out_2381892679141553073[121] = 0.0;
   out_2381892679141553073[122] = 0.0;
   out_2381892679141553073[123] = 0.0;
   out_2381892679141553073[124] = 0.0;
   out_2381892679141553073[125] = 0.0;
   out_2381892679141553073[126] = 0.0;
   out_2381892679141553073[127] = 0.0;
   out_2381892679141553073[128] = 0.0;
   out_2381892679141553073[129] = 0.0;
   out_2381892679141553073[130] = 0.0;
   out_2381892679141553073[131] = 0.0;
   out_2381892679141553073[132] = 0.0;
   out_2381892679141553073[133] = 1.0;
   out_2381892679141553073[134] = 0.0;
   out_2381892679141553073[135] = 0.0;
   out_2381892679141553073[136] = 0.0;
   out_2381892679141553073[137] = 0.0;
   out_2381892679141553073[138] = 0.0;
   out_2381892679141553073[139] = 0.0;
   out_2381892679141553073[140] = 0.0;
   out_2381892679141553073[141] = 0.0;
   out_2381892679141553073[142] = 0.0;
   out_2381892679141553073[143] = 0.0;
   out_2381892679141553073[144] = 0.0;
   out_2381892679141553073[145] = 0.0;
   out_2381892679141553073[146] = 0.0;
   out_2381892679141553073[147] = 0.0;
   out_2381892679141553073[148] = 0.0;
   out_2381892679141553073[149] = 0.0;
   out_2381892679141553073[150] = 0.0;
   out_2381892679141553073[151] = 0.0;
   out_2381892679141553073[152] = 1.0;
   out_2381892679141553073[153] = 0.0;
   out_2381892679141553073[154] = 0.0;
   out_2381892679141553073[155] = 0.0;
   out_2381892679141553073[156] = 0.0;
   out_2381892679141553073[157] = 0.0;
   out_2381892679141553073[158] = 0.0;
   out_2381892679141553073[159] = 0.0;
   out_2381892679141553073[160] = 0.0;
   out_2381892679141553073[161] = 0.0;
   out_2381892679141553073[162] = 0.0;
   out_2381892679141553073[163] = 0.0;
   out_2381892679141553073[164] = 0.0;
   out_2381892679141553073[165] = 0.0;
   out_2381892679141553073[166] = 0.0;
   out_2381892679141553073[167] = 0.0;
   out_2381892679141553073[168] = 0.0;
   out_2381892679141553073[169] = 0.0;
   out_2381892679141553073[170] = 0.0;
   out_2381892679141553073[171] = 1.0;
   out_2381892679141553073[172] = 0.0;
   out_2381892679141553073[173] = 0.0;
   out_2381892679141553073[174] = 0.0;
   out_2381892679141553073[175] = 0.0;
   out_2381892679141553073[176] = 0.0;
   out_2381892679141553073[177] = 0.0;
   out_2381892679141553073[178] = 0.0;
   out_2381892679141553073[179] = 0.0;
   out_2381892679141553073[180] = 0.0;
   out_2381892679141553073[181] = 0.0;
   out_2381892679141553073[182] = 0.0;
   out_2381892679141553073[183] = 0.0;
   out_2381892679141553073[184] = 0.0;
   out_2381892679141553073[185] = 0.0;
   out_2381892679141553073[186] = 0.0;
   out_2381892679141553073[187] = 0.0;
   out_2381892679141553073[188] = 0.0;
   out_2381892679141553073[189] = 0.0;
   out_2381892679141553073[190] = 1.0;
   out_2381892679141553073[191] = 0.0;
   out_2381892679141553073[192] = 0.0;
   out_2381892679141553073[193] = 0.0;
   out_2381892679141553073[194] = 0.0;
   out_2381892679141553073[195] = 0.0;
   out_2381892679141553073[196] = 0.0;
   out_2381892679141553073[197] = 0.0;
   out_2381892679141553073[198] = 0.0;
   out_2381892679141553073[199] = 0.0;
   out_2381892679141553073[200] = 0.0;
   out_2381892679141553073[201] = 0.0;
   out_2381892679141553073[202] = 0.0;
   out_2381892679141553073[203] = 0.0;
   out_2381892679141553073[204] = 0.0;
   out_2381892679141553073[205] = 0.0;
   out_2381892679141553073[206] = 0.0;
   out_2381892679141553073[207] = 0.0;
   out_2381892679141553073[208] = 0.0;
   out_2381892679141553073[209] = 1.0;
   out_2381892679141553073[210] = 0.0;
   out_2381892679141553073[211] = 0.0;
   out_2381892679141553073[212] = 0.0;
   out_2381892679141553073[213] = 0.0;
   out_2381892679141553073[214] = 0.0;
   out_2381892679141553073[215] = 0.0;
   out_2381892679141553073[216] = 0.0;
   out_2381892679141553073[217] = 0.0;
   out_2381892679141553073[218] = 0.0;
   out_2381892679141553073[219] = 0.0;
   out_2381892679141553073[220] = 0.0;
   out_2381892679141553073[221] = 0.0;
   out_2381892679141553073[222] = 0.0;
   out_2381892679141553073[223] = 0.0;
   out_2381892679141553073[224] = 0.0;
   out_2381892679141553073[225] = 0.0;
   out_2381892679141553073[226] = 0.0;
   out_2381892679141553073[227] = 0.0;
   out_2381892679141553073[228] = 1.0;
   out_2381892679141553073[229] = 0.0;
   out_2381892679141553073[230] = 0.0;
   out_2381892679141553073[231] = 0.0;
   out_2381892679141553073[232] = 0.0;
   out_2381892679141553073[233] = 0.0;
   out_2381892679141553073[234] = 0.0;
   out_2381892679141553073[235] = 0.0;
   out_2381892679141553073[236] = 0.0;
   out_2381892679141553073[237] = 0.0;
   out_2381892679141553073[238] = 0.0;
   out_2381892679141553073[239] = 0.0;
   out_2381892679141553073[240] = 0.0;
   out_2381892679141553073[241] = 0.0;
   out_2381892679141553073[242] = 0.0;
   out_2381892679141553073[243] = 0.0;
   out_2381892679141553073[244] = 0.0;
   out_2381892679141553073[245] = 0.0;
   out_2381892679141553073[246] = 0.0;
   out_2381892679141553073[247] = 1.0;
   out_2381892679141553073[248] = 0.0;
   out_2381892679141553073[249] = 0.0;
   out_2381892679141553073[250] = 0.0;
   out_2381892679141553073[251] = 0.0;
   out_2381892679141553073[252] = 0.0;
   out_2381892679141553073[253] = 0.0;
   out_2381892679141553073[254] = 0.0;
   out_2381892679141553073[255] = 0.0;
   out_2381892679141553073[256] = 0.0;
   out_2381892679141553073[257] = 0.0;
   out_2381892679141553073[258] = 0.0;
   out_2381892679141553073[259] = 0.0;
   out_2381892679141553073[260] = 0.0;
   out_2381892679141553073[261] = 0.0;
   out_2381892679141553073[262] = 0.0;
   out_2381892679141553073[263] = 0.0;
   out_2381892679141553073[264] = 0.0;
   out_2381892679141553073[265] = 0.0;
   out_2381892679141553073[266] = 1.0;
   out_2381892679141553073[267] = 0.0;
   out_2381892679141553073[268] = 0.0;
   out_2381892679141553073[269] = 0.0;
   out_2381892679141553073[270] = 0.0;
   out_2381892679141553073[271] = 0.0;
   out_2381892679141553073[272] = 0.0;
   out_2381892679141553073[273] = 0.0;
   out_2381892679141553073[274] = 0.0;
   out_2381892679141553073[275] = 0.0;
   out_2381892679141553073[276] = 0.0;
   out_2381892679141553073[277] = 0.0;
   out_2381892679141553073[278] = 0.0;
   out_2381892679141553073[279] = 0.0;
   out_2381892679141553073[280] = 0.0;
   out_2381892679141553073[281] = 0.0;
   out_2381892679141553073[282] = 0.0;
   out_2381892679141553073[283] = 0.0;
   out_2381892679141553073[284] = 0.0;
   out_2381892679141553073[285] = 1.0;
   out_2381892679141553073[286] = 0.0;
   out_2381892679141553073[287] = 0.0;
   out_2381892679141553073[288] = 0.0;
   out_2381892679141553073[289] = 0.0;
   out_2381892679141553073[290] = 0.0;
   out_2381892679141553073[291] = 0.0;
   out_2381892679141553073[292] = 0.0;
   out_2381892679141553073[293] = 0.0;
   out_2381892679141553073[294] = 0.0;
   out_2381892679141553073[295] = 0.0;
   out_2381892679141553073[296] = 0.0;
   out_2381892679141553073[297] = 0.0;
   out_2381892679141553073[298] = 0.0;
   out_2381892679141553073[299] = 0.0;
   out_2381892679141553073[300] = 0.0;
   out_2381892679141553073[301] = 0.0;
   out_2381892679141553073[302] = 0.0;
   out_2381892679141553073[303] = 0.0;
   out_2381892679141553073[304] = 1.0;
   out_2381892679141553073[305] = 0.0;
   out_2381892679141553073[306] = 0.0;
   out_2381892679141553073[307] = 0.0;
   out_2381892679141553073[308] = 0.0;
   out_2381892679141553073[309] = 0.0;
   out_2381892679141553073[310] = 0.0;
   out_2381892679141553073[311] = 0.0;
   out_2381892679141553073[312] = 0.0;
   out_2381892679141553073[313] = 0.0;
   out_2381892679141553073[314] = 0.0;
   out_2381892679141553073[315] = 0.0;
   out_2381892679141553073[316] = 0.0;
   out_2381892679141553073[317] = 0.0;
   out_2381892679141553073[318] = 0.0;
   out_2381892679141553073[319] = 0.0;
   out_2381892679141553073[320] = 0.0;
   out_2381892679141553073[321] = 0.0;
   out_2381892679141553073[322] = 0.0;
   out_2381892679141553073[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_1702484166209795754) {
   out_1702484166209795754[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_1702484166209795754[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_1702484166209795754[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_1702484166209795754[3] = dt*state[12] + state[3];
   out_1702484166209795754[4] = dt*state[13] + state[4];
   out_1702484166209795754[5] = dt*state[14] + state[5];
   out_1702484166209795754[6] = state[6];
   out_1702484166209795754[7] = state[7];
   out_1702484166209795754[8] = state[8];
   out_1702484166209795754[9] = state[9];
   out_1702484166209795754[10] = state[10];
   out_1702484166209795754[11] = state[11];
   out_1702484166209795754[12] = state[12];
   out_1702484166209795754[13] = state[13];
   out_1702484166209795754[14] = state[14];
   out_1702484166209795754[15] = state[15];
   out_1702484166209795754[16] = state[16];
   out_1702484166209795754[17] = state[17];
}
void F_fun(double *state, double dt, double *out_2610723520316632485) {
   out_2610723520316632485[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_2610723520316632485[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_2610723520316632485[2] = 0;
   out_2610723520316632485[3] = 0;
   out_2610723520316632485[4] = 0;
   out_2610723520316632485[5] = 0;
   out_2610723520316632485[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_2610723520316632485[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_2610723520316632485[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_2610723520316632485[9] = 0;
   out_2610723520316632485[10] = 0;
   out_2610723520316632485[11] = 0;
   out_2610723520316632485[12] = 0;
   out_2610723520316632485[13] = 0;
   out_2610723520316632485[14] = 0;
   out_2610723520316632485[15] = 0;
   out_2610723520316632485[16] = 0;
   out_2610723520316632485[17] = 0;
   out_2610723520316632485[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_2610723520316632485[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_2610723520316632485[20] = 0;
   out_2610723520316632485[21] = 0;
   out_2610723520316632485[22] = 0;
   out_2610723520316632485[23] = 0;
   out_2610723520316632485[24] = 0;
   out_2610723520316632485[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_2610723520316632485[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_2610723520316632485[27] = 0;
   out_2610723520316632485[28] = 0;
   out_2610723520316632485[29] = 0;
   out_2610723520316632485[30] = 0;
   out_2610723520316632485[31] = 0;
   out_2610723520316632485[32] = 0;
   out_2610723520316632485[33] = 0;
   out_2610723520316632485[34] = 0;
   out_2610723520316632485[35] = 0;
   out_2610723520316632485[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_2610723520316632485[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_2610723520316632485[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_2610723520316632485[39] = 0;
   out_2610723520316632485[40] = 0;
   out_2610723520316632485[41] = 0;
   out_2610723520316632485[42] = 0;
   out_2610723520316632485[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_2610723520316632485[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_2610723520316632485[45] = 0;
   out_2610723520316632485[46] = 0;
   out_2610723520316632485[47] = 0;
   out_2610723520316632485[48] = 0;
   out_2610723520316632485[49] = 0;
   out_2610723520316632485[50] = 0;
   out_2610723520316632485[51] = 0;
   out_2610723520316632485[52] = 0;
   out_2610723520316632485[53] = 0;
   out_2610723520316632485[54] = 0;
   out_2610723520316632485[55] = 0;
   out_2610723520316632485[56] = 0;
   out_2610723520316632485[57] = 1;
   out_2610723520316632485[58] = 0;
   out_2610723520316632485[59] = 0;
   out_2610723520316632485[60] = 0;
   out_2610723520316632485[61] = 0;
   out_2610723520316632485[62] = 0;
   out_2610723520316632485[63] = 0;
   out_2610723520316632485[64] = 0;
   out_2610723520316632485[65] = 0;
   out_2610723520316632485[66] = dt;
   out_2610723520316632485[67] = 0;
   out_2610723520316632485[68] = 0;
   out_2610723520316632485[69] = 0;
   out_2610723520316632485[70] = 0;
   out_2610723520316632485[71] = 0;
   out_2610723520316632485[72] = 0;
   out_2610723520316632485[73] = 0;
   out_2610723520316632485[74] = 0;
   out_2610723520316632485[75] = 0;
   out_2610723520316632485[76] = 1;
   out_2610723520316632485[77] = 0;
   out_2610723520316632485[78] = 0;
   out_2610723520316632485[79] = 0;
   out_2610723520316632485[80] = 0;
   out_2610723520316632485[81] = 0;
   out_2610723520316632485[82] = 0;
   out_2610723520316632485[83] = 0;
   out_2610723520316632485[84] = 0;
   out_2610723520316632485[85] = dt;
   out_2610723520316632485[86] = 0;
   out_2610723520316632485[87] = 0;
   out_2610723520316632485[88] = 0;
   out_2610723520316632485[89] = 0;
   out_2610723520316632485[90] = 0;
   out_2610723520316632485[91] = 0;
   out_2610723520316632485[92] = 0;
   out_2610723520316632485[93] = 0;
   out_2610723520316632485[94] = 0;
   out_2610723520316632485[95] = 1;
   out_2610723520316632485[96] = 0;
   out_2610723520316632485[97] = 0;
   out_2610723520316632485[98] = 0;
   out_2610723520316632485[99] = 0;
   out_2610723520316632485[100] = 0;
   out_2610723520316632485[101] = 0;
   out_2610723520316632485[102] = 0;
   out_2610723520316632485[103] = 0;
   out_2610723520316632485[104] = dt;
   out_2610723520316632485[105] = 0;
   out_2610723520316632485[106] = 0;
   out_2610723520316632485[107] = 0;
   out_2610723520316632485[108] = 0;
   out_2610723520316632485[109] = 0;
   out_2610723520316632485[110] = 0;
   out_2610723520316632485[111] = 0;
   out_2610723520316632485[112] = 0;
   out_2610723520316632485[113] = 0;
   out_2610723520316632485[114] = 1;
   out_2610723520316632485[115] = 0;
   out_2610723520316632485[116] = 0;
   out_2610723520316632485[117] = 0;
   out_2610723520316632485[118] = 0;
   out_2610723520316632485[119] = 0;
   out_2610723520316632485[120] = 0;
   out_2610723520316632485[121] = 0;
   out_2610723520316632485[122] = 0;
   out_2610723520316632485[123] = 0;
   out_2610723520316632485[124] = 0;
   out_2610723520316632485[125] = 0;
   out_2610723520316632485[126] = 0;
   out_2610723520316632485[127] = 0;
   out_2610723520316632485[128] = 0;
   out_2610723520316632485[129] = 0;
   out_2610723520316632485[130] = 0;
   out_2610723520316632485[131] = 0;
   out_2610723520316632485[132] = 0;
   out_2610723520316632485[133] = 1;
   out_2610723520316632485[134] = 0;
   out_2610723520316632485[135] = 0;
   out_2610723520316632485[136] = 0;
   out_2610723520316632485[137] = 0;
   out_2610723520316632485[138] = 0;
   out_2610723520316632485[139] = 0;
   out_2610723520316632485[140] = 0;
   out_2610723520316632485[141] = 0;
   out_2610723520316632485[142] = 0;
   out_2610723520316632485[143] = 0;
   out_2610723520316632485[144] = 0;
   out_2610723520316632485[145] = 0;
   out_2610723520316632485[146] = 0;
   out_2610723520316632485[147] = 0;
   out_2610723520316632485[148] = 0;
   out_2610723520316632485[149] = 0;
   out_2610723520316632485[150] = 0;
   out_2610723520316632485[151] = 0;
   out_2610723520316632485[152] = 1;
   out_2610723520316632485[153] = 0;
   out_2610723520316632485[154] = 0;
   out_2610723520316632485[155] = 0;
   out_2610723520316632485[156] = 0;
   out_2610723520316632485[157] = 0;
   out_2610723520316632485[158] = 0;
   out_2610723520316632485[159] = 0;
   out_2610723520316632485[160] = 0;
   out_2610723520316632485[161] = 0;
   out_2610723520316632485[162] = 0;
   out_2610723520316632485[163] = 0;
   out_2610723520316632485[164] = 0;
   out_2610723520316632485[165] = 0;
   out_2610723520316632485[166] = 0;
   out_2610723520316632485[167] = 0;
   out_2610723520316632485[168] = 0;
   out_2610723520316632485[169] = 0;
   out_2610723520316632485[170] = 0;
   out_2610723520316632485[171] = 1;
   out_2610723520316632485[172] = 0;
   out_2610723520316632485[173] = 0;
   out_2610723520316632485[174] = 0;
   out_2610723520316632485[175] = 0;
   out_2610723520316632485[176] = 0;
   out_2610723520316632485[177] = 0;
   out_2610723520316632485[178] = 0;
   out_2610723520316632485[179] = 0;
   out_2610723520316632485[180] = 0;
   out_2610723520316632485[181] = 0;
   out_2610723520316632485[182] = 0;
   out_2610723520316632485[183] = 0;
   out_2610723520316632485[184] = 0;
   out_2610723520316632485[185] = 0;
   out_2610723520316632485[186] = 0;
   out_2610723520316632485[187] = 0;
   out_2610723520316632485[188] = 0;
   out_2610723520316632485[189] = 0;
   out_2610723520316632485[190] = 1;
   out_2610723520316632485[191] = 0;
   out_2610723520316632485[192] = 0;
   out_2610723520316632485[193] = 0;
   out_2610723520316632485[194] = 0;
   out_2610723520316632485[195] = 0;
   out_2610723520316632485[196] = 0;
   out_2610723520316632485[197] = 0;
   out_2610723520316632485[198] = 0;
   out_2610723520316632485[199] = 0;
   out_2610723520316632485[200] = 0;
   out_2610723520316632485[201] = 0;
   out_2610723520316632485[202] = 0;
   out_2610723520316632485[203] = 0;
   out_2610723520316632485[204] = 0;
   out_2610723520316632485[205] = 0;
   out_2610723520316632485[206] = 0;
   out_2610723520316632485[207] = 0;
   out_2610723520316632485[208] = 0;
   out_2610723520316632485[209] = 1;
   out_2610723520316632485[210] = 0;
   out_2610723520316632485[211] = 0;
   out_2610723520316632485[212] = 0;
   out_2610723520316632485[213] = 0;
   out_2610723520316632485[214] = 0;
   out_2610723520316632485[215] = 0;
   out_2610723520316632485[216] = 0;
   out_2610723520316632485[217] = 0;
   out_2610723520316632485[218] = 0;
   out_2610723520316632485[219] = 0;
   out_2610723520316632485[220] = 0;
   out_2610723520316632485[221] = 0;
   out_2610723520316632485[222] = 0;
   out_2610723520316632485[223] = 0;
   out_2610723520316632485[224] = 0;
   out_2610723520316632485[225] = 0;
   out_2610723520316632485[226] = 0;
   out_2610723520316632485[227] = 0;
   out_2610723520316632485[228] = 1;
   out_2610723520316632485[229] = 0;
   out_2610723520316632485[230] = 0;
   out_2610723520316632485[231] = 0;
   out_2610723520316632485[232] = 0;
   out_2610723520316632485[233] = 0;
   out_2610723520316632485[234] = 0;
   out_2610723520316632485[235] = 0;
   out_2610723520316632485[236] = 0;
   out_2610723520316632485[237] = 0;
   out_2610723520316632485[238] = 0;
   out_2610723520316632485[239] = 0;
   out_2610723520316632485[240] = 0;
   out_2610723520316632485[241] = 0;
   out_2610723520316632485[242] = 0;
   out_2610723520316632485[243] = 0;
   out_2610723520316632485[244] = 0;
   out_2610723520316632485[245] = 0;
   out_2610723520316632485[246] = 0;
   out_2610723520316632485[247] = 1;
   out_2610723520316632485[248] = 0;
   out_2610723520316632485[249] = 0;
   out_2610723520316632485[250] = 0;
   out_2610723520316632485[251] = 0;
   out_2610723520316632485[252] = 0;
   out_2610723520316632485[253] = 0;
   out_2610723520316632485[254] = 0;
   out_2610723520316632485[255] = 0;
   out_2610723520316632485[256] = 0;
   out_2610723520316632485[257] = 0;
   out_2610723520316632485[258] = 0;
   out_2610723520316632485[259] = 0;
   out_2610723520316632485[260] = 0;
   out_2610723520316632485[261] = 0;
   out_2610723520316632485[262] = 0;
   out_2610723520316632485[263] = 0;
   out_2610723520316632485[264] = 0;
   out_2610723520316632485[265] = 0;
   out_2610723520316632485[266] = 1;
   out_2610723520316632485[267] = 0;
   out_2610723520316632485[268] = 0;
   out_2610723520316632485[269] = 0;
   out_2610723520316632485[270] = 0;
   out_2610723520316632485[271] = 0;
   out_2610723520316632485[272] = 0;
   out_2610723520316632485[273] = 0;
   out_2610723520316632485[274] = 0;
   out_2610723520316632485[275] = 0;
   out_2610723520316632485[276] = 0;
   out_2610723520316632485[277] = 0;
   out_2610723520316632485[278] = 0;
   out_2610723520316632485[279] = 0;
   out_2610723520316632485[280] = 0;
   out_2610723520316632485[281] = 0;
   out_2610723520316632485[282] = 0;
   out_2610723520316632485[283] = 0;
   out_2610723520316632485[284] = 0;
   out_2610723520316632485[285] = 1;
   out_2610723520316632485[286] = 0;
   out_2610723520316632485[287] = 0;
   out_2610723520316632485[288] = 0;
   out_2610723520316632485[289] = 0;
   out_2610723520316632485[290] = 0;
   out_2610723520316632485[291] = 0;
   out_2610723520316632485[292] = 0;
   out_2610723520316632485[293] = 0;
   out_2610723520316632485[294] = 0;
   out_2610723520316632485[295] = 0;
   out_2610723520316632485[296] = 0;
   out_2610723520316632485[297] = 0;
   out_2610723520316632485[298] = 0;
   out_2610723520316632485[299] = 0;
   out_2610723520316632485[300] = 0;
   out_2610723520316632485[301] = 0;
   out_2610723520316632485[302] = 0;
   out_2610723520316632485[303] = 0;
   out_2610723520316632485[304] = 1;
   out_2610723520316632485[305] = 0;
   out_2610723520316632485[306] = 0;
   out_2610723520316632485[307] = 0;
   out_2610723520316632485[308] = 0;
   out_2610723520316632485[309] = 0;
   out_2610723520316632485[310] = 0;
   out_2610723520316632485[311] = 0;
   out_2610723520316632485[312] = 0;
   out_2610723520316632485[313] = 0;
   out_2610723520316632485[314] = 0;
   out_2610723520316632485[315] = 0;
   out_2610723520316632485[316] = 0;
   out_2610723520316632485[317] = 0;
   out_2610723520316632485[318] = 0;
   out_2610723520316632485[319] = 0;
   out_2610723520316632485[320] = 0;
   out_2610723520316632485[321] = 0;
   out_2610723520316632485[322] = 0;
   out_2610723520316632485[323] = 1;
}
void h_4(double *state, double *unused, double *out_1625499965422042150) {
   out_1625499965422042150[0] = state[6] + state[9];
   out_1625499965422042150[1] = state[7] + state[10];
   out_1625499965422042150[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_5582302580243023097) {
   out_5582302580243023097[0] = 0;
   out_5582302580243023097[1] = 0;
   out_5582302580243023097[2] = 0;
   out_5582302580243023097[3] = 0;
   out_5582302580243023097[4] = 0;
   out_5582302580243023097[5] = 0;
   out_5582302580243023097[6] = 1;
   out_5582302580243023097[7] = 0;
   out_5582302580243023097[8] = 0;
   out_5582302580243023097[9] = 1;
   out_5582302580243023097[10] = 0;
   out_5582302580243023097[11] = 0;
   out_5582302580243023097[12] = 0;
   out_5582302580243023097[13] = 0;
   out_5582302580243023097[14] = 0;
   out_5582302580243023097[15] = 0;
   out_5582302580243023097[16] = 0;
   out_5582302580243023097[17] = 0;
   out_5582302580243023097[18] = 0;
   out_5582302580243023097[19] = 0;
   out_5582302580243023097[20] = 0;
   out_5582302580243023097[21] = 0;
   out_5582302580243023097[22] = 0;
   out_5582302580243023097[23] = 0;
   out_5582302580243023097[24] = 0;
   out_5582302580243023097[25] = 1;
   out_5582302580243023097[26] = 0;
   out_5582302580243023097[27] = 0;
   out_5582302580243023097[28] = 1;
   out_5582302580243023097[29] = 0;
   out_5582302580243023097[30] = 0;
   out_5582302580243023097[31] = 0;
   out_5582302580243023097[32] = 0;
   out_5582302580243023097[33] = 0;
   out_5582302580243023097[34] = 0;
   out_5582302580243023097[35] = 0;
   out_5582302580243023097[36] = 0;
   out_5582302580243023097[37] = 0;
   out_5582302580243023097[38] = 0;
   out_5582302580243023097[39] = 0;
   out_5582302580243023097[40] = 0;
   out_5582302580243023097[41] = 0;
   out_5582302580243023097[42] = 0;
   out_5582302580243023097[43] = 0;
   out_5582302580243023097[44] = 1;
   out_5582302580243023097[45] = 0;
   out_5582302580243023097[46] = 0;
   out_5582302580243023097[47] = 1;
   out_5582302580243023097[48] = 0;
   out_5582302580243023097[49] = 0;
   out_5582302580243023097[50] = 0;
   out_5582302580243023097[51] = 0;
   out_5582302580243023097[52] = 0;
   out_5582302580243023097[53] = 0;
}
void h_10(double *state, double *unused, double *out_2139046532052679128) {
   out_2139046532052679128[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_2139046532052679128[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_2139046532052679128[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_280379430924529525) {
   out_280379430924529525[0] = 0;
   out_280379430924529525[1] = 9.8100000000000005*cos(state[1]);
   out_280379430924529525[2] = 0;
   out_280379430924529525[3] = 0;
   out_280379430924529525[4] = -state[8];
   out_280379430924529525[5] = state[7];
   out_280379430924529525[6] = 0;
   out_280379430924529525[7] = state[5];
   out_280379430924529525[8] = -state[4];
   out_280379430924529525[9] = 0;
   out_280379430924529525[10] = 0;
   out_280379430924529525[11] = 0;
   out_280379430924529525[12] = 1;
   out_280379430924529525[13] = 0;
   out_280379430924529525[14] = 0;
   out_280379430924529525[15] = 1;
   out_280379430924529525[16] = 0;
   out_280379430924529525[17] = 0;
   out_280379430924529525[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_280379430924529525[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_280379430924529525[20] = 0;
   out_280379430924529525[21] = state[8];
   out_280379430924529525[22] = 0;
   out_280379430924529525[23] = -state[6];
   out_280379430924529525[24] = -state[5];
   out_280379430924529525[25] = 0;
   out_280379430924529525[26] = state[3];
   out_280379430924529525[27] = 0;
   out_280379430924529525[28] = 0;
   out_280379430924529525[29] = 0;
   out_280379430924529525[30] = 0;
   out_280379430924529525[31] = 1;
   out_280379430924529525[32] = 0;
   out_280379430924529525[33] = 0;
   out_280379430924529525[34] = 1;
   out_280379430924529525[35] = 0;
   out_280379430924529525[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_280379430924529525[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_280379430924529525[38] = 0;
   out_280379430924529525[39] = -state[7];
   out_280379430924529525[40] = state[6];
   out_280379430924529525[41] = 0;
   out_280379430924529525[42] = state[4];
   out_280379430924529525[43] = -state[3];
   out_280379430924529525[44] = 0;
   out_280379430924529525[45] = 0;
   out_280379430924529525[46] = 0;
   out_280379430924529525[47] = 0;
   out_280379430924529525[48] = 0;
   out_280379430924529525[49] = 0;
   out_280379430924529525[50] = 1;
   out_280379430924529525[51] = 0;
   out_280379430924529525[52] = 0;
   out_280379430924529525[53] = 1;
}
void h_13(double *state, double *unused, double *out_4130601663238522497) {
   out_4130601663238522497[0] = state[3];
   out_4130601663238522497[1] = state[4];
   out_4130601663238522497[2] = state[5];
}
void H_13(double *state, double *unused, double *out_2028328628073677832) {
   out_2028328628073677832[0] = 0;
   out_2028328628073677832[1] = 0;
   out_2028328628073677832[2] = 0;
   out_2028328628073677832[3] = 1;
   out_2028328628073677832[4] = 0;
   out_2028328628073677832[5] = 0;
   out_2028328628073677832[6] = 0;
   out_2028328628073677832[7] = 0;
   out_2028328628073677832[8] = 0;
   out_2028328628073677832[9] = 0;
   out_2028328628073677832[10] = 0;
   out_2028328628073677832[11] = 0;
   out_2028328628073677832[12] = 0;
   out_2028328628073677832[13] = 0;
   out_2028328628073677832[14] = 0;
   out_2028328628073677832[15] = 0;
   out_2028328628073677832[16] = 0;
   out_2028328628073677832[17] = 0;
   out_2028328628073677832[18] = 0;
   out_2028328628073677832[19] = 0;
   out_2028328628073677832[20] = 0;
   out_2028328628073677832[21] = 0;
   out_2028328628073677832[22] = 1;
   out_2028328628073677832[23] = 0;
   out_2028328628073677832[24] = 0;
   out_2028328628073677832[25] = 0;
   out_2028328628073677832[26] = 0;
   out_2028328628073677832[27] = 0;
   out_2028328628073677832[28] = 0;
   out_2028328628073677832[29] = 0;
   out_2028328628073677832[30] = 0;
   out_2028328628073677832[31] = 0;
   out_2028328628073677832[32] = 0;
   out_2028328628073677832[33] = 0;
   out_2028328628073677832[34] = 0;
   out_2028328628073677832[35] = 0;
   out_2028328628073677832[36] = 0;
   out_2028328628073677832[37] = 0;
   out_2028328628073677832[38] = 0;
   out_2028328628073677832[39] = 0;
   out_2028328628073677832[40] = 0;
   out_2028328628073677832[41] = 1;
   out_2028328628073677832[42] = 0;
   out_2028328628073677832[43] = 0;
   out_2028328628073677832[44] = 0;
   out_2028328628073677832[45] = 0;
   out_2028328628073677832[46] = 0;
   out_2028328628073677832[47] = 0;
   out_2028328628073677832[48] = 0;
   out_2028328628073677832[49] = 0;
   out_2028328628073677832[50] = 0;
   out_2028328628073677832[51] = 0;
   out_2028328628073677832[52] = 0;
   out_2028328628073677832[53] = 0;
}
void h_14(double *state, double *unused, double *out_5394061988893492228) {
   out_5394061988893492228[0] = state[6];
   out_5394061988893492228[1] = state[7];
   out_5394061988893492228[2] = state[8];
}
void H_14(double *state, double *unused, double *out_8665091012538395393) {
   out_8665091012538395393[0] = 0;
   out_8665091012538395393[1] = 0;
   out_8665091012538395393[2] = 0;
   out_8665091012538395393[3] = 0;
   out_8665091012538395393[4] = 0;
   out_8665091012538395393[5] = 0;
   out_8665091012538395393[6] = 1;
   out_8665091012538395393[7] = 0;
   out_8665091012538395393[8] = 0;
   out_8665091012538395393[9] = 0;
   out_8665091012538395393[10] = 0;
   out_8665091012538395393[11] = 0;
   out_8665091012538395393[12] = 0;
   out_8665091012538395393[13] = 0;
   out_8665091012538395393[14] = 0;
   out_8665091012538395393[15] = 0;
   out_8665091012538395393[16] = 0;
   out_8665091012538395393[17] = 0;
   out_8665091012538395393[18] = 0;
   out_8665091012538395393[19] = 0;
   out_8665091012538395393[20] = 0;
   out_8665091012538395393[21] = 0;
   out_8665091012538395393[22] = 0;
   out_8665091012538395393[23] = 0;
   out_8665091012538395393[24] = 0;
   out_8665091012538395393[25] = 1;
   out_8665091012538395393[26] = 0;
   out_8665091012538395393[27] = 0;
   out_8665091012538395393[28] = 0;
   out_8665091012538395393[29] = 0;
   out_8665091012538395393[30] = 0;
   out_8665091012538395393[31] = 0;
   out_8665091012538395393[32] = 0;
   out_8665091012538395393[33] = 0;
   out_8665091012538395393[34] = 0;
   out_8665091012538395393[35] = 0;
   out_8665091012538395393[36] = 0;
   out_8665091012538395393[37] = 0;
   out_8665091012538395393[38] = 0;
   out_8665091012538395393[39] = 0;
   out_8665091012538395393[40] = 0;
   out_8665091012538395393[41] = 0;
   out_8665091012538395393[42] = 0;
   out_8665091012538395393[43] = 0;
   out_8665091012538395393[44] = 1;
   out_8665091012538395393[45] = 0;
   out_8665091012538395393[46] = 0;
   out_8665091012538395393[47] = 0;
   out_8665091012538395393[48] = 0;
   out_8665091012538395393[49] = 0;
   out_8665091012538395393[50] = 0;
   out_8665091012538395393[51] = 0;
   out_8665091012538395393[52] = 0;
   out_8665091012538395393[53] = 0;
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
void pose_err_fun(double *nom_x, double *delta_x, double *out_5688174754372622748) {
  err_fun(nom_x, delta_x, out_5688174754372622748);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_598026621986152539) {
  inv_err_fun(nom_x, true_x, out_598026621986152539);
}
void pose_H_mod_fun(double *state, double *out_2381892679141553073) {
  H_mod_fun(state, out_2381892679141553073);
}
void pose_f_fun(double *state, double dt, double *out_1702484166209795754) {
  f_fun(state,  dt, out_1702484166209795754);
}
void pose_F_fun(double *state, double dt, double *out_2610723520316632485) {
  F_fun(state,  dt, out_2610723520316632485);
}
void pose_h_4(double *state, double *unused, double *out_1625499965422042150) {
  h_4(state, unused, out_1625499965422042150);
}
void pose_H_4(double *state, double *unused, double *out_5582302580243023097) {
  H_4(state, unused, out_5582302580243023097);
}
void pose_h_10(double *state, double *unused, double *out_2139046532052679128) {
  h_10(state, unused, out_2139046532052679128);
}
void pose_H_10(double *state, double *unused, double *out_280379430924529525) {
  H_10(state, unused, out_280379430924529525);
}
void pose_h_13(double *state, double *unused, double *out_4130601663238522497) {
  h_13(state, unused, out_4130601663238522497);
}
void pose_H_13(double *state, double *unused, double *out_2028328628073677832) {
  H_13(state, unused, out_2028328628073677832);
}
void pose_h_14(double *state, double *unused, double *out_5394061988893492228) {
  h_14(state, unused, out_5394061988893492228);
}
void pose_H_14(double *state, double *unused, double *out_8665091012538395393) {
  H_14(state, unused, out_8665091012538395393);
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
