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
void err_fun(double *nom_x, double *delta_x, double *out_165846048707596909) {
   out_165846048707596909[0] = delta_x[0] + nom_x[0];
   out_165846048707596909[1] = delta_x[1] + nom_x[1];
   out_165846048707596909[2] = delta_x[2] + nom_x[2];
   out_165846048707596909[3] = delta_x[3] + nom_x[3];
   out_165846048707596909[4] = delta_x[4] + nom_x[4];
   out_165846048707596909[5] = delta_x[5] + nom_x[5];
   out_165846048707596909[6] = delta_x[6] + nom_x[6];
   out_165846048707596909[7] = delta_x[7] + nom_x[7];
   out_165846048707596909[8] = delta_x[8] + nom_x[8];
   out_165846048707596909[9] = delta_x[9] + nom_x[9];
   out_165846048707596909[10] = delta_x[10] + nom_x[10];
   out_165846048707596909[11] = delta_x[11] + nom_x[11];
   out_165846048707596909[12] = delta_x[12] + nom_x[12];
   out_165846048707596909[13] = delta_x[13] + nom_x[13];
   out_165846048707596909[14] = delta_x[14] + nom_x[14];
   out_165846048707596909[15] = delta_x[15] + nom_x[15];
   out_165846048707596909[16] = delta_x[16] + nom_x[16];
   out_165846048707596909[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_6648002265281282693) {
   out_6648002265281282693[0] = -nom_x[0] + true_x[0];
   out_6648002265281282693[1] = -nom_x[1] + true_x[1];
   out_6648002265281282693[2] = -nom_x[2] + true_x[2];
   out_6648002265281282693[3] = -nom_x[3] + true_x[3];
   out_6648002265281282693[4] = -nom_x[4] + true_x[4];
   out_6648002265281282693[5] = -nom_x[5] + true_x[5];
   out_6648002265281282693[6] = -nom_x[6] + true_x[6];
   out_6648002265281282693[7] = -nom_x[7] + true_x[7];
   out_6648002265281282693[8] = -nom_x[8] + true_x[8];
   out_6648002265281282693[9] = -nom_x[9] + true_x[9];
   out_6648002265281282693[10] = -nom_x[10] + true_x[10];
   out_6648002265281282693[11] = -nom_x[11] + true_x[11];
   out_6648002265281282693[12] = -nom_x[12] + true_x[12];
   out_6648002265281282693[13] = -nom_x[13] + true_x[13];
   out_6648002265281282693[14] = -nom_x[14] + true_x[14];
   out_6648002265281282693[15] = -nom_x[15] + true_x[15];
   out_6648002265281282693[16] = -nom_x[16] + true_x[16];
   out_6648002265281282693[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_3826583937831985339) {
   out_3826583937831985339[0] = 1.0;
   out_3826583937831985339[1] = 0.0;
   out_3826583937831985339[2] = 0.0;
   out_3826583937831985339[3] = 0.0;
   out_3826583937831985339[4] = 0.0;
   out_3826583937831985339[5] = 0.0;
   out_3826583937831985339[6] = 0.0;
   out_3826583937831985339[7] = 0.0;
   out_3826583937831985339[8] = 0.0;
   out_3826583937831985339[9] = 0.0;
   out_3826583937831985339[10] = 0.0;
   out_3826583937831985339[11] = 0.0;
   out_3826583937831985339[12] = 0.0;
   out_3826583937831985339[13] = 0.0;
   out_3826583937831985339[14] = 0.0;
   out_3826583937831985339[15] = 0.0;
   out_3826583937831985339[16] = 0.0;
   out_3826583937831985339[17] = 0.0;
   out_3826583937831985339[18] = 0.0;
   out_3826583937831985339[19] = 1.0;
   out_3826583937831985339[20] = 0.0;
   out_3826583937831985339[21] = 0.0;
   out_3826583937831985339[22] = 0.0;
   out_3826583937831985339[23] = 0.0;
   out_3826583937831985339[24] = 0.0;
   out_3826583937831985339[25] = 0.0;
   out_3826583937831985339[26] = 0.0;
   out_3826583937831985339[27] = 0.0;
   out_3826583937831985339[28] = 0.0;
   out_3826583937831985339[29] = 0.0;
   out_3826583937831985339[30] = 0.0;
   out_3826583937831985339[31] = 0.0;
   out_3826583937831985339[32] = 0.0;
   out_3826583937831985339[33] = 0.0;
   out_3826583937831985339[34] = 0.0;
   out_3826583937831985339[35] = 0.0;
   out_3826583937831985339[36] = 0.0;
   out_3826583937831985339[37] = 0.0;
   out_3826583937831985339[38] = 1.0;
   out_3826583937831985339[39] = 0.0;
   out_3826583937831985339[40] = 0.0;
   out_3826583937831985339[41] = 0.0;
   out_3826583937831985339[42] = 0.0;
   out_3826583937831985339[43] = 0.0;
   out_3826583937831985339[44] = 0.0;
   out_3826583937831985339[45] = 0.0;
   out_3826583937831985339[46] = 0.0;
   out_3826583937831985339[47] = 0.0;
   out_3826583937831985339[48] = 0.0;
   out_3826583937831985339[49] = 0.0;
   out_3826583937831985339[50] = 0.0;
   out_3826583937831985339[51] = 0.0;
   out_3826583937831985339[52] = 0.0;
   out_3826583937831985339[53] = 0.0;
   out_3826583937831985339[54] = 0.0;
   out_3826583937831985339[55] = 0.0;
   out_3826583937831985339[56] = 0.0;
   out_3826583937831985339[57] = 1.0;
   out_3826583937831985339[58] = 0.0;
   out_3826583937831985339[59] = 0.0;
   out_3826583937831985339[60] = 0.0;
   out_3826583937831985339[61] = 0.0;
   out_3826583937831985339[62] = 0.0;
   out_3826583937831985339[63] = 0.0;
   out_3826583937831985339[64] = 0.0;
   out_3826583937831985339[65] = 0.0;
   out_3826583937831985339[66] = 0.0;
   out_3826583937831985339[67] = 0.0;
   out_3826583937831985339[68] = 0.0;
   out_3826583937831985339[69] = 0.0;
   out_3826583937831985339[70] = 0.0;
   out_3826583937831985339[71] = 0.0;
   out_3826583937831985339[72] = 0.0;
   out_3826583937831985339[73] = 0.0;
   out_3826583937831985339[74] = 0.0;
   out_3826583937831985339[75] = 0.0;
   out_3826583937831985339[76] = 1.0;
   out_3826583937831985339[77] = 0.0;
   out_3826583937831985339[78] = 0.0;
   out_3826583937831985339[79] = 0.0;
   out_3826583937831985339[80] = 0.0;
   out_3826583937831985339[81] = 0.0;
   out_3826583937831985339[82] = 0.0;
   out_3826583937831985339[83] = 0.0;
   out_3826583937831985339[84] = 0.0;
   out_3826583937831985339[85] = 0.0;
   out_3826583937831985339[86] = 0.0;
   out_3826583937831985339[87] = 0.0;
   out_3826583937831985339[88] = 0.0;
   out_3826583937831985339[89] = 0.0;
   out_3826583937831985339[90] = 0.0;
   out_3826583937831985339[91] = 0.0;
   out_3826583937831985339[92] = 0.0;
   out_3826583937831985339[93] = 0.0;
   out_3826583937831985339[94] = 0.0;
   out_3826583937831985339[95] = 1.0;
   out_3826583937831985339[96] = 0.0;
   out_3826583937831985339[97] = 0.0;
   out_3826583937831985339[98] = 0.0;
   out_3826583937831985339[99] = 0.0;
   out_3826583937831985339[100] = 0.0;
   out_3826583937831985339[101] = 0.0;
   out_3826583937831985339[102] = 0.0;
   out_3826583937831985339[103] = 0.0;
   out_3826583937831985339[104] = 0.0;
   out_3826583937831985339[105] = 0.0;
   out_3826583937831985339[106] = 0.0;
   out_3826583937831985339[107] = 0.0;
   out_3826583937831985339[108] = 0.0;
   out_3826583937831985339[109] = 0.0;
   out_3826583937831985339[110] = 0.0;
   out_3826583937831985339[111] = 0.0;
   out_3826583937831985339[112] = 0.0;
   out_3826583937831985339[113] = 0.0;
   out_3826583937831985339[114] = 1.0;
   out_3826583937831985339[115] = 0.0;
   out_3826583937831985339[116] = 0.0;
   out_3826583937831985339[117] = 0.0;
   out_3826583937831985339[118] = 0.0;
   out_3826583937831985339[119] = 0.0;
   out_3826583937831985339[120] = 0.0;
   out_3826583937831985339[121] = 0.0;
   out_3826583937831985339[122] = 0.0;
   out_3826583937831985339[123] = 0.0;
   out_3826583937831985339[124] = 0.0;
   out_3826583937831985339[125] = 0.0;
   out_3826583937831985339[126] = 0.0;
   out_3826583937831985339[127] = 0.0;
   out_3826583937831985339[128] = 0.0;
   out_3826583937831985339[129] = 0.0;
   out_3826583937831985339[130] = 0.0;
   out_3826583937831985339[131] = 0.0;
   out_3826583937831985339[132] = 0.0;
   out_3826583937831985339[133] = 1.0;
   out_3826583937831985339[134] = 0.0;
   out_3826583937831985339[135] = 0.0;
   out_3826583937831985339[136] = 0.0;
   out_3826583937831985339[137] = 0.0;
   out_3826583937831985339[138] = 0.0;
   out_3826583937831985339[139] = 0.0;
   out_3826583937831985339[140] = 0.0;
   out_3826583937831985339[141] = 0.0;
   out_3826583937831985339[142] = 0.0;
   out_3826583937831985339[143] = 0.0;
   out_3826583937831985339[144] = 0.0;
   out_3826583937831985339[145] = 0.0;
   out_3826583937831985339[146] = 0.0;
   out_3826583937831985339[147] = 0.0;
   out_3826583937831985339[148] = 0.0;
   out_3826583937831985339[149] = 0.0;
   out_3826583937831985339[150] = 0.0;
   out_3826583937831985339[151] = 0.0;
   out_3826583937831985339[152] = 1.0;
   out_3826583937831985339[153] = 0.0;
   out_3826583937831985339[154] = 0.0;
   out_3826583937831985339[155] = 0.0;
   out_3826583937831985339[156] = 0.0;
   out_3826583937831985339[157] = 0.0;
   out_3826583937831985339[158] = 0.0;
   out_3826583937831985339[159] = 0.0;
   out_3826583937831985339[160] = 0.0;
   out_3826583937831985339[161] = 0.0;
   out_3826583937831985339[162] = 0.0;
   out_3826583937831985339[163] = 0.0;
   out_3826583937831985339[164] = 0.0;
   out_3826583937831985339[165] = 0.0;
   out_3826583937831985339[166] = 0.0;
   out_3826583937831985339[167] = 0.0;
   out_3826583937831985339[168] = 0.0;
   out_3826583937831985339[169] = 0.0;
   out_3826583937831985339[170] = 0.0;
   out_3826583937831985339[171] = 1.0;
   out_3826583937831985339[172] = 0.0;
   out_3826583937831985339[173] = 0.0;
   out_3826583937831985339[174] = 0.0;
   out_3826583937831985339[175] = 0.0;
   out_3826583937831985339[176] = 0.0;
   out_3826583937831985339[177] = 0.0;
   out_3826583937831985339[178] = 0.0;
   out_3826583937831985339[179] = 0.0;
   out_3826583937831985339[180] = 0.0;
   out_3826583937831985339[181] = 0.0;
   out_3826583937831985339[182] = 0.0;
   out_3826583937831985339[183] = 0.0;
   out_3826583937831985339[184] = 0.0;
   out_3826583937831985339[185] = 0.0;
   out_3826583937831985339[186] = 0.0;
   out_3826583937831985339[187] = 0.0;
   out_3826583937831985339[188] = 0.0;
   out_3826583937831985339[189] = 0.0;
   out_3826583937831985339[190] = 1.0;
   out_3826583937831985339[191] = 0.0;
   out_3826583937831985339[192] = 0.0;
   out_3826583937831985339[193] = 0.0;
   out_3826583937831985339[194] = 0.0;
   out_3826583937831985339[195] = 0.0;
   out_3826583937831985339[196] = 0.0;
   out_3826583937831985339[197] = 0.0;
   out_3826583937831985339[198] = 0.0;
   out_3826583937831985339[199] = 0.0;
   out_3826583937831985339[200] = 0.0;
   out_3826583937831985339[201] = 0.0;
   out_3826583937831985339[202] = 0.0;
   out_3826583937831985339[203] = 0.0;
   out_3826583937831985339[204] = 0.0;
   out_3826583937831985339[205] = 0.0;
   out_3826583937831985339[206] = 0.0;
   out_3826583937831985339[207] = 0.0;
   out_3826583937831985339[208] = 0.0;
   out_3826583937831985339[209] = 1.0;
   out_3826583937831985339[210] = 0.0;
   out_3826583937831985339[211] = 0.0;
   out_3826583937831985339[212] = 0.0;
   out_3826583937831985339[213] = 0.0;
   out_3826583937831985339[214] = 0.0;
   out_3826583937831985339[215] = 0.0;
   out_3826583937831985339[216] = 0.0;
   out_3826583937831985339[217] = 0.0;
   out_3826583937831985339[218] = 0.0;
   out_3826583937831985339[219] = 0.0;
   out_3826583937831985339[220] = 0.0;
   out_3826583937831985339[221] = 0.0;
   out_3826583937831985339[222] = 0.0;
   out_3826583937831985339[223] = 0.0;
   out_3826583937831985339[224] = 0.0;
   out_3826583937831985339[225] = 0.0;
   out_3826583937831985339[226] = 0.0;
   out_3826583937831985339[227] = 0.0;
   out_3826583937831985339[228] = 1.0;
   out_3826583937831985339[229] = 0.0;
   out_3826583937831985339[230] = 0.0;
   out_3826583937831985339[231] = 0.0;
   out_3826583937831985339[232] = 0.0;
   out_3826583937831985339[233] = 0.0;
   out_3826583937831985339[234] = 0.0;
   out_3826583937831985339[235] = 0.0;
   out_3826583937831985339[236] = 0.0;
   out_3826583937831985339[237] = 0.0;
   out_3826583937831985339[238] = 0.0;
   out_3826583937831985339[239] = 0.0;
   out_3826583937831985339[240] = 0.0;
   out_3826583937831985339[241] = 0.0;
   out_3826583937831985339[242] = 0.0;
   out_3826583937831985339[243] = 0.0;
   out_3826583937831985339[244] = 0.0;
   out_3826583937831985339[245] = 0.0;
   out_3826583937831985339[246] = 0.0;
   out_3826583937831985339[247] = 1.0;
   out_3826583937831985339[248] = 0.0;
   out_3826583937831985339[249] = 0.0;
   out_3826583937831985339[250] = 0.0;
   out_3826583937831985339[251] = 0.0;
   out_3826583937831985339[252] = 0.0;
   out_3826583937831985339[253] = 0.0;
   out_3826583937831985339[254] = 0.0;
   out_3826583937831985339[255] = 0.0;
   out_3826583937831985339[256] = 0.0;
   out_3826583937831985339[257] = 0.0;
   out_3826583937831985339[258] = 0.0;
   out_3826583937831985339[259] = 0.0;
   out_3826583937831985339[260] = 0.0;
   out_3826583937831985339[261] = 0.0;
   out_3826583937831985339[262] = 0.0;
   out_3826583937831985339[263] = 0.0;
   out_3826583937831985339[264] = 0.0;
   out_3826583937831985339[265] = 0.0;
   out_3826583937831985339[266] = 1.0;
   out_3826583937831985339[267] = 0.0;
   out_3826583937831985339[268] = 0.0;
   out_3826583937831985339[269] = 0.0;
   out_3826583937831985339[270] = 0.0;
   out_3826583937831985339[271] = 0.0;
   out_3826583937831985339[272] = 0.0;
   out_3826583937831985339[273] = 0.0;
   out_3826583937831985339[274] = 0.0;
   out_3826583937831985339[275] = 0.0;
   out_3826583937831985339[276] = 0.0;
   out_3826583937831985339[277] = 0.0;
   out_3826583937831985339[278] = 0.0;
   out_3826583937831985339[279] = 0.0;
   out_3826583937831985339[280] = 0.0;
   out_3826583937831985339[281] = 0.0;
   out_3826583937831985339[282] = 0.0;
   out_3826583937831985339[283] = 0.0;
   out_3826583937831985339[284] = 0.0;
   out_3826583937831985339[285] = 1.0;
   out_3826583937831985339[286] = 0.0;
   out_3826583937831985339[287] = 0.0;
   out_3826583937831985339[288] = 0.0;
   out_3826583937831985339[289] = 0.0;
   out_3826583937831985339[290] = 0.0;
   out_3826583937831985339[291] = 0.0;
   out_3826583937831985339[292] = 0.0;
   out_3826583937831985339[293] = 0.0;
   out_3826583937831985339[294] = 0.0;
   out_3826583937831985339[295] = 0.0;
   out_3826583937831985339[296] = 0.0;
   out_3826583937831985339[297] = 0.0;
   out_3826583937831985339[298] = 0.0;
   out_3826583937831985339[299] = 0.0;
   out_3826583937831985339[300] = 0.0;
   out_3826583937831985339[301] = 0.0;
   out_3826583937831985339[302] = 0.0;
   out_3826583937831985339[303] = 0.0;
   out_3826583937831985339[304] = 1.0;
   out_3826583937831985339[305] = 0.0;
   out_3826583937831985339[306] = 0.0;
   out_3826583937831985339[307] = 0.0;
   out_3826583937831985339[308] = 0.0;
   out_3826583937831985339[309] = 0.0;
   out_3826583937831985339[310] = 0.0;
   out_3826583937831985339[311] = 0.0;
   out_3826583937831985339[312] = 0.0;
   out_3826583937831985339[313] = 0.0;
   out_3826583937831985339[314] = 0.0;
   out_3826583937831985339[315] = 0.0;
   out_3826583937831985339[316] = 0.0;
   out_3826583937831985339[317] = 0.0;
   out_3826583937831985339[318] = 0.0;
   out_3826583937831985339[319] = 0.0;
   out_3826583937831985339[320] = 0.0;
   out_3826583937831985339[321] = 0.0;
   out_3826583937831985339[322] = 0.0;
   out_3826583937831985339[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_3932199691534334272) {
   out_3932199691534334272[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_3932199691534334272[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_3932199691534334272[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_3932199691534334272[3] = dt*state[12] + state[3];
   out_3932199691534334272[4] = dt*state[13] + state[4];
   out_3932199691534334272[5] = dt*state[14] + state[5];
   out_3932199691534334272[6] = state[6];
   out_3932199691534334272[7] = state[7];
   out_3932199691534334272[8] = state[8];
   out_3932199691534334272[9] = state[9];
   out_3932199691534334272[10] = state[10];
   out_3932199691534334272[11] = state[11];
   out_3932199691534334272[12] = state[12];
   out_3932199691534334272[13] = state[13];
   out_3932199691534334272[14] = state[14];
   out_3932199691534334272[15] = state[15];
   out_3932199691534334272[16] = state[16];
   out_3932199691534334272[17] = state[17];
}
void F_fun(double *state, double dt, double *out_9115777546130168700) {
   out_9115777546130168700[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_9115777546130168700[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_9115777546130168700[2] = 0;
   out_9115777546130168700[3] = 0;
   out_9115777546130168700[4] = 0;
   out_9115777546130168700[5] = 0;
   out_9115777546130168700[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_9115777546130168700[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_9115777546130168700[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_9115777546130168700[9] = 0;
   out_9115777546130168700[10] = 0;
   out_9115777546130168700[11] = 0;
   out_9115777546130168700[12] = 0;
   out_9115777546130168700[13] = 0;
   out_9115777546130168700[14] = 0;
   out_9115777546130168700[15] = 0;
   out_9115777546130168700[16] = 0;
   out_9115777546130168700[17] = 0;
   out_9115777546130168700[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_9115777546130168700[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_9115777546130168700[20] = 0;
   out_9115777546130168700[21] = 0;
   out_9115777546130168700[22] = 0;
   out_9115777546130168700[23] = 0;
   out_9115777546130168700[24] = 0;
   out_9115777546130168700[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_9115777546130168700[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_9115777546130168700[27] = 0;
   out_9115777546130168700[28] = 0;
   out_9115777546130168700[29] = 0;
   out_9115777546130168700[30] = 0;
   out_9115777546130168700[31] = 0;
   out_9115777546130168700[32] = 0;
   out_9115777546130168700[33] = 0;
   out_9115777546130168700[34] = 0;
   out_9115777546130168700[35] = 0;
   out_9115777546130168700[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_9115777546130168700[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_9115777546130168700[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_9115777546130168700[39] = 0;
   out_9115777546130168700[40] = 0;
   out_9115777546130168700[41] = 0;
   out_9115777546130168700[42] = 0;
   out_9115777546130168700[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_9115777546130168700[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_9115777546130168700[45] = 0;
   out_9115777546130168700[46] = 0;
   out_9115777546130168700[47] = 0;
   out_9115777546130168700[48] = 0;
   out_9115777546130168700[49] = 0;
   out_9115777546130168700[50] = 0;
   out_9115777546130168700[51] = 0;
   out_9115777546130168700[52] = 0;
   out_9115777546130168700[53] = 0;
   out_9115777546130168700[54] = 0;
   out_9115777546130168700[55] = 0;
   out_9115777546130168700[56] = 0;
   out_9115777546130168700[57] = 1;
   out_9115777546130168700[58] = 0;
   out_9115777546130168700[59] = 0;
   out_9115777546130168700[60] = 0;
   out_9115777546130168700[61] = 0;
   out_9115777546130168700[62] = 0;
   out_9115777546130168700[63] = 0;
   out_9115777546130168700[64] = 0;
   out_9115777546130168700[65] = 0;
   out_9115777546130168700[66] = dt;
   out_9115777546130168700[67] = 0;
   out_9115777546130168700[68] = 0;
   out_9115777546130168700[69] = 0;
   out_9115777546130168700[70] = 0;
   out_9115777546130168700[71] = 0;
   out_9115777546130168700[72] = 0;
   out_9115777546130168700[73] = 0;
   out_9115777546130168700[74] = 0;
   out_9115777546130168700[75] = 0;
   out_9115777546130168700[76] = 1;
   out_9115777546130168700[77] = 0;
   out_9115777546130168700[78] = 0;
   out_9115777546130168700[79] = 0;
   out_9115777546130168700[80] = 0;
   out_9115777546130168700[81] = 0;
   out_9115777546130168700[82] = 0;
   out_9115777546130168700[83] = 0;
   out_9115777546130168700[84] = 0;
   out_9115777546130168700[85] = dt;
   out_9115777546130168700[86] = 0;
   out_9115777546130168700[87] = 0;
   out_9115777546130168700[88] = 0;
   out_9115777546130168700[89] = 0;
   out_9115777546130168700[90] = 0;
   out_9115777546130168700[91] = 0;
   out_9115777546130168700[92] = 0;
   out_9115777546130168700[93] = 0;
   out_9115777546130168700[94] = 0;
   out_9115777546130168700[95] = 1;
   out_9115777546130168700[96] = 0;
   out_9115777546130168700[97] = 0;
   out_9115777546130168700[98] = 0;
   out_9115777546130168700[99] = 0;
   out_9115777546130168700[100] = 0;
   out_9115777546130168700[101] = 0;
   out_9115777546130168700[102] = 0;
   out_9115777546130168700[103] = 0;
   out_9115777546130168700[104] = dt;
   out_9115777546130168700[105] = 0;
   out_9115777546130168700[106] = 0;
   out_9115777546130168700[107] = 0;
   out_9115777546130168700[108] = 0;
   out_9115777546130168700[109] = 0;
   out_9115777546130168700[110] = 0;
   out_9115777546130168700[111] = 0;
   out_9115777546130168700[112] = 0;
   out_9115777546130168700[113] = 0;
   out_9115777546130168700[114] = 1;
   out_9115777546130168700[115] = 0;
   out_9115777546130168700[116] = 0;
   out_9115777546130168700[117] = 0;
   out_9115777546130168700[118] = 0;
   out_9115777546130168700[119] = 0;
   out_9115777546130168700[120] = 0;
   out_9115777546130168700[121] = 0;
   out_9115777546130168700[122] = 0;
   out_9115777546130168700[123] = 0;
   out_9115777546130168700[124] = 0;
   out_9115777546130168700[125] = 0;
   out_9115777546130168700[126] = 0;
   out_9115777546130168700[127] = 0;
   out_9115777546130168700[128] = 0;
   out_9115777546130168700[129] = 0;
   out_9115777546130168700[130] = 0;
   out_9115777546130168700[131] = 0;
   out_9115777546130168700[132] = 0;
   out_9115777546130168700[133] = 1;
   out_9115777546130168700[134] = 0;
   out_9115777546130168700[135] = 0;
   out_9115777546130168700[136] = 0;
   out_9115777546130168700[137] = 0;
   out_9115777546130168700[138] = 0;
   out_9115777546130168700[139] = 0;
   out_9115777546130168700[140] = 0;
   out_9115777546130168700[141] = 0;
   out_9115777546130168700[142] = 0;
   out_9115777546130168700[143] = 0;
   out_9115777546130168700[144] = 0;
   out_9115777546130168700[145] = 0;
   out_9115777546130168700[146] = 0;
   out_9115777546130168700[147] = 0;
   out_9115777546130168700[148] = 0;
   out_9115777546130168700[149] = 0;
   out_9115777546130168700[150] = 0;
   out_9115777546130168700[151] = 0;
   out_9115777546130168700[152] = 1;
   out_9115777546130168700[153] = 0;
   out_9115777546130168700[154] = 0;
   out_9115777546130168700[155] = 0;
   out_9115777546130168700[156] = 0;
   out_9115777546130168700[157] = 0;
   out_9115777546130168700[158] = 0;
   out_9115777546130168700[159] = 0;
   out_9115777546130168700[160] = 0;
   out_9115777546130168700[161] = 0;
   out_9115777546130168700[162] = 0;
   out_9115777546130168700[163] = 0;
   out_9115777546130168700[164] = 0;
   out_9115777546130168700[165] = 0;
   out_9115777546130168700[166] = 0;
   out_9115777546130168700[167] = 0;
   out_9115777546130168700[168] = 0;
   out_9115777546130168700[169] = 0;
   out_9115777546130168700[170] = 0;
   out_9115777546130168700[171] = 1;
   out_9115777546130168700[172] = 0;
   out_9115777546130168700[173] = 0;
   out_9115777546130168700[174] = 0;
   out_9115777546130168700[175] = 0;
   out_9115777546130168700[176] = 0;
   out_9115777546130168700[177] = 0;
   out_9115777546130168700[178] = 0;
   out_9115777546130168700[179] = 0;
   out_9115777546130168700[180] = 0;
   out_9115777546130168700[181] = 0;
   out_9115777546130168700[182] = 0;
   out_9115777546130168700[183] = 0;
   out_9115777546130168700[184] = 0;
   out_9115777546130168700[185] = 0;
   out_9115777546130168700[186] = 0;
   out_9115777546130168700[187] = 0;
   out_9115777546130168700[188] = 0;
   out_9115777546130168700[189] = 0;
   out_9115777546130168700[190] = 1;
   out_9115777546130168700[191] = 0;
   out_9115777546130168700[192] = 0;
   out_9115777546130168700[193] = 0;
   out_9115777546130168700[194] = 0;
   out_9115777546130168700[195] = 0;
   out_9115777546130168700[196] = 0;
   out_9115777546130168700[197] = 0;
   out_9115777546130168700[198] = 0;
   out_9115777546130168700[199] = 0;
   out_9115777546130168700[200] = 0;
   out_9115777546130168700[201] = 0;
   out_9115777546130168700[202] = 0;
   out_9115777546130168700[203] = 0;
   out_9115777546130168700[204] = 0;
   out_9115777546130168700[205] = 0;
   out_9115777546130168700[206] = 0;
   out_9115777546130168700[207] = 0;
   out_9115777546130168700[208] = 0;
   out_9115777546130168700[209] = 1;
   out_9115777546130168700[210] = 0;
   out_9115777546130168700[211] = 0;
   out_9115777546130168700[212] = 0;
   out_9115777546130168700[213] = 0;
   out_9115777546130168700[214] = 0;
   out_9115777546130168700[215] = 0;
   out_9115777546130168700[216] = 0;
   out_9115777546130168700[217] = 0;
   out_9115777546130168700[218] = 0;
   out_9115777546130168700[219] = 0;
   out_9115777546130168700[220] = 0;
   out_9115777546130168700[221] = 0;
   out_9115777546130168700[222] = 0;
   out_9115777546130168700[223] = 0;
   out_9115777546130168700[224] = 0;
   out_9115777546130168700[225] = 0;
   out_9115777546130168700[226] = 0;
   out_9115777546130168700[227] = 0;
   out_9115777546130168700[228] = 1;
   out_9115777546130168700[229] = 0;
   out_9115777546130168700[230] = 0;
   out_9115777546130168700[231] = 0;
   out_9115777546130168700[232] = 0;
   out_9115777546130168700[233] = 0;
   out_9115777546130168700[234] = 0;
   out_9115777546130168700[235] = 0;
   out_9115777546130168700[236] = 0;
   out_9115777546130168700[237] = 0;
   out_9115777546130168700[238] = 0;
   out_9115777546130168700[239] = 0;
   out_9115777546130168700[240] = 0;
   out_9115777546130168700[241] = 0;
   out_9115777546130168700[242] = 0;
   out_9115777546130168700[243] = 0;
   out_9115777546130168700[244] = 0;
   out_9115777546130168700[245] = 0;
   out_9115777546130168700[246] = 0;
   out_9115777546130168700[247] = 1;
   out_9115777546130168700[248] = 0;
   out_9115777546130168700[249] = 0;
   out_9115777546130168700[250] = 0;
   out_9115777546130168700[251] = 0;
   out_9115777546130168700[252] = 0;
   out_9115777546130168700[253] = 0;
   out_9115777546130168700[254] = 0;
   out_9115777546130168700[255] = 0;
   out_9115777546130168700[256] = 0;
   out_9115777546130168700[257] = 0;
   out_9115777546130168700[258] = 0;
   out_9115777546130168700[259] = 0;
   out_9115777546130168700[260] = 0;
   out_9115777546130168700[261] = 0;
   out_9115777546130168700[262] = 0;
   out_9115777546130168700[263] = 0;
   out_9115777546130168700[264] = 0;
   out_9115777546130168700[265] = 0;
   out_9115777546130168700[266] = 1;
   out_9115777546130168700[267] = 0;
   out_9115777546130168700[268] = 0;
   out_9115777546130168700[269] = 0;
   out_9115777546130168700[270] = 0;
   out_9115777546130168700[271] = 0;
   out_9115777546130168700[272] = 0;
   out_9115777546130168700[273] = 0;
   out_9115777546130168700[274] = 0;
   out_9115777546130168700[275] = 0;
   out_9115777546130168700[276] = 0;
   out_9115777546130168700[277] = 0;
   out_9115777546130168700[278] = 0;
   out_9115777546130168700[279] = 0;
   out_9115777546130168700[280] = 0;
   out_9115777546130168700[281] = 0;
   out_9115777546130168700[282] = 0;
   out_9115777546130168700[283] = 0;
   out_9115777546130168700[284] = 0;
   out_9115777546130168700[285] = 1;
   out_9115777546130168700[286] = 0;
   out_9115777546130168700[287] = 0;
   out_9115777546130168700[288] = 0;
   out_9115777546130168700[289] = 0;
   out_9115777546130168700[290] = 0;
   out_9115777546130168700[291] = 0;
   out_9115777546130168700[292] = 0;
   out_9115777546130168700[293] = 0;
   out_9115777546130168700[294] = 0;
   out_9115777546130168700[295] = 0;
   out_9115777546130168700[296] = 0;
   out_9115777546130168700[297] = 0;
   out_9115777546130168700[298] = 0;
   out_9115777546130168700[299] = 0;
   out_9115777546130168700[300] = 0;
   out_9115777546130168700[301] = 0;
   out_9115777546130168700[302] = 0;
   out_9115777546130168700[303] = 0;
   out_9115777546130168700[304] = 1;
   out_9115777546130168700[305] = 0;
   out_9115777546130168700[306] = 0;
   out_9115777546130168700[307] = 0;
   out_9115777546130168700[308] = 0;
   out_9115777546130168700[309] = 0;
   out_9115777546130168700[310] = 0;
   out_9115777546130168700[311] = 0;
   out_9115777546130168700[312] = 0;
   out_9115777546130168700[313] = 0;
   out_9115777546130168700[314] = 0;
   out_9115777546130168700[315] = 0;
   out_9115777546130168700[316] = 0;
   out_9115777546130168700[317] = 0;
   out_9115777546130168700[318] = 0;
   out_9115777546130168700[319] = 0;
   out_9115777546130168700[320] = 0;
   out_9115777546130168700[321] = 0;
   out_9115777546130168700[322] = 0;
   out_9115777546130168700[323] = 1;
}
void h_4(double *state, double *unused, double *out_3213295537891936167) {
   out_3213295537891936167[0] = state[6] + state[9];
   out_3213295537891936167[1] = state[7] + state[10];
   out_3213295537891936167[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_3101938741858735467) {
   out_3101938741858735467[0] = 0;
   out_3101938741858735467[1] = 0;
   out_3101938741858735467[2] = 0;
   out_3101938741858735467[3] = 0;
   out_3101938741858735467[4] = 0;
   out_3101938741858735467[5] = 0;
   out_3101938741858735467[6] = 1;
   out_3101938741858735467[7] = 0;
   out_3101938741858735467[8] = 0;
   out_3101938741858735467[9] = 1;
   out_3101938741858735467[10] = 0;
   out_3101938741858735467[11] = 0;
   out_3101938741858735467[12] = 0;
   out_3101938741858735467[13] = 0;
   out_3101938741858735467[14] = 0;
   out_3101938741858735467[15] = 0;
   out_3101938741858735467[16] = 0;
   out_3101938741858735467[17] = 0;
   out_3101938741858735467[18] = 0;
   out_3101938741858735467[19] = 0;
   out_3101938741858735467[20] = 0;
   out_3101938741858735467[21] = 0;
   out_3101938741858735467[22] = 0;
   out_3101938741858735467[23] = 0;
   out_3101938741858735467[24] = 0;
   out_3101938741858735467[25] = 1;
   out_3101938741858735467[26] = 0;
   out_3101938741858735467[27] = 0;
   out_3101938741858735467[28] = 1;
   out_3101938741858735467[29] = 0;
   out_3101938741858735467[30] = 0;
   out_3101938741858735467[31] = 0;
   out_3101938741858735467[32] = 0;
   out_3101938741858735467[33] = 0;
   out_3101938741858735467[34] = 0;
   out_3101938741858735467[35] = 0;
   out_3101938741858735467[36] = 0;
   out_3101938741858735467[37] = 0;
   out_3101938741858735467[38] = 0;
   out_3101938741858735467[39] = 0;
   out_3101938741858735467[40] = 0;
   out_3101938741858735467[41] = 0;
   out_3101938741858735467[42] = 0;
   out_3101938741858735467[43] = 0;
   out_3101938741858735467[44] = 1;
   out_3101938741858735467[45] = 0;
   out_3101938741858735467[46] = 0;
   out_3101938741858735467[47] = 1;
   out_3101938741858735467[48] = 0;
   out_3101938741858735467[49] = 0;
   out_3101938741858735467[50] = 0;
   out_3101938741858735467[51] = 0;
   out_3101938741858735467[52] = 0;
   out_3101938741858735467[53] = 0;
}
void h_10(double *state, double *unused, double *out_5489470472982430598) {
   out_5489470472982430598[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_5489470472982430598[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_5489470472982430598[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_8922665824980314411) {
   out_8922665824980314411[0] = 0;
   out_8922665824980314411[1] = 9.8100000000000005*cos(state[1]);
   out_8922665824980314411[2] = 0;
   out_8922665824980314411[3] = 0;
   out_8922665824980314411[4] = -state[8];
   out_8922665824980314411[5] = state[7];
   out_8922665824980314411[6] = 0;
   out_8922665824980314411[7] = state[5];
   out_8922665824980314411[8] = -state[4];
   out_8922665824980314411[9] = 0;
   out_8922665824980314411[10] = 0;
   out_8922665824980314411[11] = 0;
   out_8922665824980314411[12] = 1;
   out_8922665824980314411[13] = 0;
   out_8922665824980314411[14] = 0;
   out_8922665824980314411[15] = 1;
   out_8922665824980314411[16] = 0;
   out_8922665824980314411[17] = 0;
   out_8922665824980314411[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_8922665824980314411[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_8922665824980314411[20] = 0;
   out_8922665824980314411[21] = state[8];
   out_8922665824980314411[22] = 0;
   out_8922665824980314411[23] = -state[6];
   out_8922665824980314411[24] = -state[5];
   out_8922665824980314411[25] = 0;
   out_8922665824980314411[26] = state[3];
   out_8922665824980314411[27] = 0;
   out_8922665824980314411[28] = 0;
   out_8922665824980314411[29] = 0;
   out_8922665824980314411[30] = 0;
   out_8922665824980314411[31] = 1;
   out_8922665824980314411[32] = 0;
   out_8922665824980314411[33] = 0;
   out_8922665824980314411[34] = 1;
   out_8922665824980314411[35] = 0;
   out_8922665824980314411[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_8922665824980314411[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_8922665824980314411[38] = 0;
   out_8922665824980314411[39] = -state[7];
   out_8922665824980314411[40] = state[6];
   out_8922665824980314411[41] = 0;
   out_8922665824980314411[42] = state[4];
   out_8922665824980314411[43] = -state[3];
   out_8922665824980314411[44] = 0;
   out_8922665824980314411[45] = 0;
   out_8922665824980314411[46] = 0;
   out_8922665824980314411[47] = 0;
   out_8922665824980314411[48] = 0;
   out_8922665824980314411[49] = 0;
   out_8922665824980314411[50] = 1;
   out_8922665824980314411[51] = 0;
   out_8922665824980314411[52] = 0;
   out_8922665824980314411[53] = 1;
}
void h_13(double *state, double *unused, double *out_8982009317064219914) {
   out_8982009317064219914[0] = state[3];
   out_8982009317064219914[1] = state[4];
   out_8982009317064219914[2] = state[5];
}
void H_13(double *state, double *unused, double *out_6314212567191068268) {
   out_6314212567191068268[0] = 0;
   out_6314212567191068268[1] = 0;
   out_6314212567191068268[2] = 0;
   out_6314212567191068268[3] = 1;
   out_6314212567191068268[4] = 0;
   out_6314212567191068268[5] = 0;
   out_6314212567191068268[6] = 0;
   out_6314212567191068268[7] = 0;
   out_6314212567191068268[8] = 0;
   out_6314212567191068268[9] = 0;
   out_6314212567191068268[10] = 0;
   out_6314212567191068268[11] = 0;
   out_6314212567191068268[12] = 0;
   out_6314212567191068268[13] = 0;
   out_6314212567191068268[14] = 0;
   out_6314212567191068268[15] = 0;
   out_6314212567191068268[16] = 0;
   out_6314212567191068268[17] = 0;
   out_6314212567191068268[18] = 0;
   out_6314212567191068268[19] = 0;
   out_6314212567191068268[20] = 0;
   out_6314212567191068268[21] = 0;
   out_6314212567191068268[22] = 1;
   out_6314212567191068268[23] = 0;
   out_6314212567191068268[24] = 0;
   out_6314212567191068268[25] = 0;
   out_6314212567191068268[26] = 0;
   out_6314212567191068268[27] = 0;
   out_6314212567191068268[28] = 0;
   out_6314212567191068268[29] = 0;
   out_6314212567191068268[30] = 0;
   out_6314212567191068268[31] = 0;
   out_6314212567191068268[32] = 0;
   out_6314212567191068268[33] = 0;
   out_6314212567191068268[34] = 0;
   out_6314212567191068268[35] = 0;
   out_6314212567191068268[36] = 0;
   out_6314212567191068268[37] = 0;
   out_6314212567191068268[38] = 0;
   out_6314212567191068268[39] = 0;
   out_6314212567191068268[40] = 0;
   out_6314212567191068268[41] = 1;
   out_6314212567191068268[42] = 0;
   out_6314212567191068268[43] = 0;
   out_6314212567191068268[44] = 0;
   out_6314212567191068268[45] = 0;
   out_6314212567191068268[46] = 0;
   out_6314212567191068268[47] = 0;
   out_6314212567191068268[48] = 0;
   out_6314212567191068268[49] = 0;
   out_6314212567191068268[50] = 0;
   out_6314212567191068268[51] = 0;
   out_6314212567191068268[52] = 0;
   out_6314212567191068268[53] = 0;
}
void h_14(double *state, double *unused, double *out_8976270627455297792) {
   out_8976270627455297792[0] = state[6];
   out_8976270627455297792[1] = state[7];
   out_8976270627455297792[2] = state[8];
}
void H_14(double *state, double *unused, double *out_7065179598198219996) {
   out_7065179598198219996[0] = 0;
   out_7065179598198219996[1] = 0;
   out_7065179598198219996[2] = 0;
   out_7065179598198219996[3] = 0;
   out_7065179598198219996[4] = 0;
   out_7065179598198219996[5] = 0;
   out_7065179598198219996[6] = 1;
   out_7065179598198219996[7] = 0;
   out_7065179598198219996[8] = 0;
   out_7065179598198219996[9] = 0;
   out_7065179598198219996[10] = 0;
   out_7065179598198219996[11] = 0;
   out_7065179598198219996[12] = 0;
   out_7065179598198219996[13] = 0;
   out_7065179598198219996[14] = 0;
   out_7065179598198219996[15] = 0;
   out_7065179598198219996[16] = 0;
   out_7065179598198219996[17] = 0;
   out_7065179598198219996[18] = 0;
   out_7065179598198219996[19] = 0;
   out_7065179598198219996[20] = 0;
   out_7065179598198219996[21] = 0;
   out_7065179598198219996[22] = 0;
   out_7065179598198219996[23] = 0;
   out_7065179598198219996[24] = 0;
   out_7065179598198219996[25] = 1;
   out_7065179598198219996[26] = 0;
   out_7065179598198219996[27] = 0;
   out_7065179598198219996[28] = 0;
   out_7065179598198219996[29] = 0;
   out_7065179598198219996[30] = 0;
   out_7065179598198219996[31] = 0;
   out_7065179598198219996[32] = 0;
   out_7065179598198219996[33] = 0;
   out_7065179598198219996[34] = 0;
   out_7065179598198219996[35] = 0;
   out_7065179598198219996[36] = 0;
   out_7065179598198219996[37] = 0;
   out_7065179598198219996[38] = 0;
   out_7065179598198219996[39] = 0;
   out_7065179598198219996[40] = 0;
   out_7065179598198219996[41] = 0;
   out_7065179598198219996[42] = 0;
   out_7065179598198219996[43] = 0;
   out_7065179598198219996[44] = 1;
   out_7065179598198219996[45] = 0;
   out_7065179598198219996[46] = 0;
   out_7065179598198219996[47] = 0;
   out_7065179598198219996[48] = 0;
   out_7065179598198219996[49] = 0;
   out_7065179598198219996[50] = 0;
   out_7065179598198219996[51] = 0;
   out_7065179598198219996[52] = 0;
   out_7065179598198219996[53] = 0;
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
void pose_err_fun(double *nom_x, double *delta_x, double *out_165846048707596909) {
  err_fun(nom_x, delta_x, out_165846048707596909);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_6648002265281282693) {
  inv_err_fun(nom_x, true_x, out_6648002265281282693);
}
void pose_H_mod_fun(double *state, double *out_3826583937831985339) {
  H_mod_fun(state, out_3826583937831985339);
}
void pose_f_fun(double *state, double dt, double *out_3932199691534334272) {
  f_fun(state,  dt, out_3932199691534334272);
}
void pose_F_fun(double *state, double dt, double *out_9115777546130168700) {
  F_fun(state,  dt, out_9115777546130168700);
}
void pose_h_4(double *state, double *unused, double *out_3213295537891936167) {
  h_4(state, unused, out_3213295537891936167);
}
void pose_H_4(double *state, double *unused, double *out_3101938741858735467) {
  H_4(state, unused, out_3101938741858735467);
}
void pose_h_10(double *state, double *unused, double *out_5489470472982430598) {
  h_10(state, unused, out_5489470472982430598);
}
void pose_H_10(double *state, double *unused, double *out_8922665824980314411) {
  H_10(state, unused, out_8922665824980314411);
}
void pose_h_13(double *state, double *unused, double *out_8982009317064219914) {
  h_13(state, unused, out_8982009317064219914);
}
void pose_H_13(double *state, double *unused, double *out_6314212567191068268) {
  H_13(state, unused, out_6314212567191068268);
}
void pose_h_14(double *state, double *unused, double *out_8976270627455297792) {
  h_14(state, unused, out_8976270627455297792);
}
void pose_H_14(double *state, double *unused, double *out_7065179598198219996) {
  H_14(state, unused, out_7065179598198219996);
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
