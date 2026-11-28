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
void err_fun(double *nom_x, double *delta_x, double *out_8585539421584719708) {
   out_8585539421584719708[0] = delta_x[0] + nom_x[0];
   out_8585539421584719708[1] = delta_x[1] + nom_x[1];
   out_8585539421584719708[2] = delta_x[2] + nom_x[2];
   out_8585539421584719708[3] = delta_x[3] + nom_x[3];
   out_8585539421584719708[4] = delta_x[4] + nom_x[4];
   out_8585539421584719708[5] = delta_x[5] + nom_x[5];
   out_8585539421584719708[6] = delta_x[6] + nom_x[6];
   out_8585539421584719708[7] = delta_x[7] + nom_x[7];
   out_8585539421584719708[8] = delta_x[8] + nom_x[8];
   out_8585539421584719708[9] = delta_x[9] + nom_x[9];
   out_8585539421584719708[10] = delta_x[10] + nom_x[10];
   out_8585539421584719708[11] = delta_x[11] + nom_x[11];
   out_8585539421584719708[12] = delta_x[12] + nom_x[12];
   out_8585539421584719708[13] = delta_x[13] + nom_x[13];
   out_8585539421584719708[14] = delta_x[14] + nom_x[14];
   out_8585539421584719708[15] = delta_x[15] + nom_x[15];
   out_8585539421584719708[16] = delta_x[16] + nom_x[16];
   out_8585539421584719708[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_6468830226543666520) {
   out_6468830226543666520[0] = -nom_x[0] + true_x[0];
   out_6468830226543666520[1] = -nom_x[1] + true_x[1];
   out_6468830226543666520[2] = -nom_x[2] + true_x[2];
   out_6468830226543666520[3] = -nom_x[3] + true_x[3];
   out_6468830226543666520[4] = -nom_x[4] + true_x[4];
   out_6468830226543666520[5] = -nom_x[5] + true_x[5];
   out_6468830226543666520[6] = -nom_x[6] + true_x[6];
   out_6468830226543666520[7] = -nom_x[7] + true_x[7];
   out_6468830226543666520[8] = -nom_x[8] + true_x[8];
   out_6468830226543666520[9] = -nom_x[9] + true_x[9];
   out_6468830226543666520[10] = -nom_x[10] + true_x[10];
   out_6468830226543666520[11] = -nom_x[11] + true_x[11];
   out_6468830226543666520[12] = -nom_x[12] + true_x[12];
   out_6468830226543666520[13] = -nom_x[13] + true_x[13];
   out_6468830226543666520[14] = -nom_x[14] + true_x[14];
   out_6468830226543666520[15] = -nom_x[15] + true_x[15];
   out_6468830226543666520[16] = -nom_x[16] + true_x[16];
   out_6468830226543666520[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_2349771934270070487) {
   out_2349771934270070487[0] = 1.0;
   out_2349771934270070487[1] = 0.0;
   out_2349771934270070487[2] = 0.0;
   out_2349771934270070487[3] = 0.0;
   out_2349771934270070487[4] = 0.0;
   out_2349771934270070487[5] = 0.0;
   out_2349771934270070487[6] = 0.0;
   out_2349771934270070487[7] = 0.0;
   out_2349771934270070487[8] = 0.0;
   out_2349771934270070487[9] = 0.0;
   out_2349771934270070487[10] = 0.0;
   out_2349771934270070487[11] = 0.0;
   out_2349771934270070487[12] = 0.0;
   out_2349771934270070487[13] = 0.0;
   out_2349771934270070487[14] = 0.0;
   out_2349771934270070487[15] = 0.0;
   out_2349771934270070487[16] = 0.0;
   out_2349771934270070487[17] = 0.0;
   out_2349771934270070487[18] = 0.0;
   out_2349771934270070487[19] = 1.0;
   out_2349771934270070487[20] = 0.0;
   out_2349771934270070487[21] = 0.0;
   out_2349771934270070487[22] = 0.0;
   out_2349771934270070487[23] = 0.0;
   out_2349771934270070487[24] = 0.0;
   out_2349771934270070487[25] = 0.0;
   out_2349771934270070487[26] = 0.0;
   out_2349771934270070487[27] = 0.0;
   out_2349771934270070487[28] = 0.0;
   out_2349771934270070487[29] = 0.0;
   out_2349771934270070487[30] = 0.0;
   out_2349771934270070487[31] = 0.0;
   out_2349771934270070487[32] = 0.0;
   out_2349771934270070487[33] = 0.0;
   out_2349771934270070487[34] = 0.0;
   out_2349771934270070487[35] = 0.0;
   out_2349771934270070487[36] = 0.0;
   out_2349771934270070487[37] = 0.0;
   out_2349771934270070487[38] = 1.0;
   out_2349771934270070487[39] = 0.0;
   out_2349771934270070487[40] = 0.0;
   out_2349771934270070487[41] = 0.0;
   out_2349771934270070487[42] = 0.0;
   out_2349771934270070487[43] = 0.0;
   out_2349771934270070487[44] = 0.0;
   out_2349771934270070487[45] = 0.0;
   out_2349771934270070487[46] = 0.0;
   out_2349771934270070487[47] = 0.0;
   out_2349771934270070487[48] = 0.0;
   out_2349771934270070487[49] = 0.0;
   out_2349771934270070487[50] = 0.0;
   out_2349771934270070487[51] = 0.0;
   out_2349771934270070487[52] = 0.0;
   out_2349771934270070487[53] = 0.0;
   out_2349771934270070487[54] = 0.0;
   out_2349771934270070487[55] = 0.0;
   out_2349771934270070487[56] = 0.0;
   out_2349771934270070487[57] = 1.0;
   out_2349771934270070487[58] = 0.0;
   out_2349771934270070487[59] = 0.0;
   out_2349771934270070487[60] = 0.0;
   out_2349771934270070487[61] = 0.0;
   out_2349771934270070487[62] = 0.0;
   out_2349771934270070487[63] = 0.0;
   out_2349771934270070487[64] = 0.0;
   out_2349771934270070487[65] = 0.0;
   out_2349771934270070487[66] = 0.0;
   out_2349771934270070487[67] = 0.0;
   out_2349771934270070487[68] = 0.0;
   out_2349771934270070487[69] = 0.0;
   out_2349771934270070487[70] = 0.0;
   out_2349771934270070487[71] = 0.0;
   out_2349771934270070487[72] = 0.0;
   out_2349771934270070487[73] = 0.0;
   out_2349771934270070487[74] = 0.0;
   out_2349771934270070487[75] = 0.0;
   out_2349771934270070487[76] = 1.0;
   out_2349771934270070487[77] = 0.0;
   out_2349771934270070487[78] = 0.0;
   out_2349771934270070487[79] = 0.0;
   out_2349771934270070487[80] = 0.0;
   out_2349771934270070487[81] = 0.0;
   out_2349771934270070487[82] = 0.0;
   out_2349771934270070487[83] = 0.0;
   out_2349771934270070487[84] = 0.0;
   out_2349771934270070487[85] = 0.0;
   out_2349771934270070487[86] = 0.0;
   out_2349771934270070487[87] = 0.0;
   out_2349771934270070487[88] = 0.0;
   out_2349771934270070487[89] = 0.0;
   out_2349771934270070487[90] = 0.0;
   out_2349771934270070487[91] = 0.0;
   out_2349771934270070487[92] = 0.0;
   out_2349771934270070487[93] = 0.0;
   out_2349771934270070487[94] = 0.0;
   out_2349771934270070487[95] = 1.0;
   out_2349771934270070487[96] = 0.0;
   out_2349771934270070487[97] = 0.0;
   out_2349771934270070487[98] = 0.0;
   out_2349771934270070487[99] = 0.0;
   out_2349771934270070487[100] = 0.0;
   out_2349771934270070487[101] = 0.0;
   out_2349771934270070487[102] = 0.0;
   out_2349771934270070487[103] = 0.0;
   out_2349771934270070487[104] = 0.0;
   out_2349771934270070487[105] = 0.0;
   out_2349771934270070487[106] = 0.0;
   out_2349771934270070487[107] = 0.0;
   out_2349771934270070487[108] = 0.0;
   out_2349771934270070487[109] = 0.0;
   out_2349771934270070487[110] = 0.0;
   out_2349771934270070487[111] = 0.0;
   out_2349771934270070487[112] = 0.0;
   out_2349771934270070487[113] = 0.0;
   out_2349771934270070487[114] = 1.0;
   out_2349771934270070487[115] = 0.0;
   out_2349771934270070487[116] = 0.0;
   out_2349771934270070487[117] = 0.0;
   out_2349771934270070487[118] = 0.0;
   out_2349771934270070487[119] = 0.0;
   out_2349771934270070487[120] = 0.0;
   out_2349771934270070487[121] = 0.0;
   out_2349771934270070487[122] = 0.0;
   out_2349771934270070487[123] = 0.0;
   out_2349771934270070487[124] = 0.0;
   out_2349771934270070487[125] = 0.0;
   out_2349771934270070487[126] = 0.0;
   out_2349771934270070487[127] = 0.0;
   out_2349771934270070487[128] = 0.0;
   out_2349771934270070487[129] = 0.0;
   out_2349771934270070487[130] = 0.0;
   out_2349771934270070487[131] = 0.0;
   out_2349771934270070487[132] = 0.0;
   out_2349771934270070487[133] = 1.0;
   out_2349771934270070487[134] = 0.0;
   out_2349771934270070487[135] = 0.0;
   out_2349771934270070487[136] = 0.0;
   out_2349771934270070487[137] = 0.0;
   out_2349771934270070487[138] = 0.0;
   out_2349771934270070487[139] = 0.0;
   out_2349771934270070487[140] = 0.0;
   out_2349771934270070487[141] = 0.0;
   out_2349771934270070487[142] = 0.0;
   out_2349771934270070487[143] = 0.0;
   out_2349771934270070487[144] = 0.0;
   out_2349771934270070487[145] = 0.0;
   out_2349771934270070487[146] = 0.0;
   out_2349771934270070487[147] = 0.0;
   out_2349771934270070487[148] = 0.0;
   out_2349771934270070487[149] = 0.0;
   out_2349771934270070487[150] = 0.0;
   out_2349771934270070487[151] = 0.0;
   out_2349771934270070487[152] = 1.0;
   out_2349771934270070487[153] = 0.0;
   out_2349771934270070487[154] = 0.0;
   out_2349771934270070487[155] = 0.0;
   out_2349771934270070487[156] = 0.0;
   out_2349771934270070487[157] = 0.0;
   out_2349771934270070487[158] = 0.0;
   out_2349771934270070487[159] = 0.0;
   out_2349771934270070487[160] = 0.0;
   out_2349771934270070487[161] = 0.0;
   out_2349771934270070487[162] = 0.0;
   out_2349771934270070487[163] = 0.0;
   out_2349771934270070487[164] = 0.0;
   out_2349771934270070487[165] = 0.0;
   out_2349771934270070487[166] = 0.0;
   out_2349771934270070487[167] = 0.0;
   out_2349771934270070487[168] = 0.0;
   out_2349771934270070487[169] = 0.0;
   out_2349771934270070487[170] = 0.0;
   out_2349771934270070487[171] = 1.0;
   out_2349771934270070487[172] = 0.0;
   out_2349771934270070487[173] = 0.0;
   out_2349771934270070487[174] = 0.0;
   out_2349771934270070487[175] = 0.0;
   out_2349771934270070487[176] = 0.0;
   out_2349771934270070487[177] = 0.0;
   out_2349771934270070487[178] = 0.0;
   out_2349771934270070487[179] = 0.0;
   out_2349771934270070487[180] = 0.0;
   out_2349771934270070487[181] = 0.0;
   out_2349771934270070487[182] = 0.0;
   out_2349771934270070487[183] = 0.0;
   out_2349771934270070487[184] = 0.0;
   out_2349771934270070487[185] = 0.0;
   out_2349771934270070487[186] = 0.0;
   out_2349771934270070487[187] = 0.0;
   out_2349771934270070487[188] = 0.0;
   out_2349771934270070487[189] = 0.0;
   out_2349771934270070487[190] = 1.0;
   out_2349771934270070487[191] = 0.0;
   out_2349771934270070487[192] = 0.0;
   out_2349771934270070487[193] = 0.0;
   out_2349771934270070487[194] = 0.0;
   out_2349771934270070487[195] = 0.0;
   out_2349771934270070487[196] = 0.0;
   out_2349771934270070487[197] = 0.0;
   out_2349771934270070487[198] = 0.0;
   out_2349771934270070487[199] = 0.0;
   out_2349771934270070487[200] = 0.0;
   out_2349771934270070487[201] = 0.0;
   out_2349771934270070487[202] = 0.0;
   out_2349771934270070487[203] = 0.0;
   out_2349771934270070487[204] = 0.0;
   out_2349771934270070487[205] = 0.0;
   out_2349771934270070487[206] = 0.0;
   out_2349771934270070487[207] = 0.0;
   out_2349771934270070487[208] = 0.0;
   out_2349771934270070487[209] = 1.0;
   out_2349771934270070487[210] = 0.0;
   out_2349771934270070487[211] = 0.0;
   out_2349771934270070487[212] = 0.0;
   out_2349771934270070487[213] = 0.0;
   out_2349771934270070487[214] = 0.0;
   out_2349771934270070487[215] = 0.0;
   out_2349771934270070487[216] = 0.0;
   out_2349771934270070487[217] = 0.0;
   out_2349771934270070487[218] = 0.0;
   out_2349771934270070487[219] = 0.0;
   out_2349771934270070487[220] = 0.0;
   out_2349771934270070487[221] = 0.0;
   out_2349771934270070487[222] = 0.0;
   out_2349771934270070487[223] = 0.0;
   out_2349771934270070487[224] = 0.0;
   out_2349771934270070487[225] = 0.0;
   out_2349771934270070487[226] = 0.0;
   out_2349771934270070487[227] = 0.0;
   out_2349771934270070487[228] = 1.0;
   out_2349771934270070487[229] = 0.0;
   out_2349771934270070487[230] = 0.0;
   out_2349771934270070487[231] = 0.0;
   out_2349771934270070487[232] = 0.0;
   out_2349771934270070487[233] = 0.0;
   out_2349771934270070487[234] = 0.0;
   out_2349771934270070487[235] = 0.0;
   out_2349771934270070487[236] = 0.0;
   out_2349771934270070487[237] = 0.0;
   out_2349771934270070487[238] = 0.0;
   out_2349771934270070487[239] = 0.0;
   out_2349771934270070487[240] = 0.0;
   out_2349771934270070487[241] = 0.0;
   out_2349771934270070487[242] = 0.0;
   out_2349771934270070487[243] = 0.0;
   out_2349771934270070487[244] = 0.0;
   out_2349771934270070487[245] = 0.0;
   out_2349771934270070487[246] = 0.0;
   out_2349771934270070487[247] = 1.0;
   out_2349771934270070487[248] = 0.0;
   out_2349771934270070487[249] = 0.0;
   out_2349771934270070487[250] = 0.0;
   out_2349771934270070487[251] = 0.0;
   out_2349771934270070487[252] = 0.0;
   out_2349771934270070487[253] = 0.0;
   out_2349771934270070487[254] = 0.0;
   out_2349771934270070487[255] = 0.0;
   out_2349771934270070487[256] = 0.0;
   out_2349771934270070487[257] = 0.0;
   out_2349771934270070487[258] = 0.0;
   out_2349771934270070487[259] = 0.0;
   out_2349771934270070487[260] = 0.0;
   out_2349771934270070487[261] = 0.0;
   out_2349771934270070487[262] = 0.0;
   out_2349771934270070487[263] = 0.0;
   out_2349771934270070487[264] = 0.0;
   out_2349771934270070487[265] = 0.0;
   out_2349771934270070487[266] = 1.0;
   out_2349771934270070487[267] = 0.0;
   out_2349771934270070487[268] = 0.0;
   out_2349771934270070487[269] = 0.0;
   out_2349771934270070487[270] = 0.0;
   out_2349771934270070487[271] = 0.0;
   out_2349771934270070487[272] = 0.0;
   out_2349771934270070487[273] = 0.0;
   out_2349771934270070487[274] = 0.0;
   out_2349771934270070487[275] = 0.0;
   out_2349771934270070487[276] = 0.0;
   out_2349771934270070487[277] = 0.0;
   out_2349771934270070487[278] = 0.0;
   out_2349771934270070487[279] = 0.0;
   out_2349771934270070487[280] = 0.0;
   out_2349771934270070487[281] = 0.0;
   out_2349771934270070487[282] = 0.0;
   out_2349771934270070487[283] = 0.0;
   out_2349771934270070487[284] = 0.0;
   out_2349771934270070487[285] = 1.0;
   out_2349771934270070487[286] = 0.0;
   out_2349771934270070487[287] = 0.0;
   out_2349771934270070487[288] = 0.0;
   out_2349771934270070487[289] = 0.0;
   out_2349771934270070487[290] = 0.0;
   out_2349771934270070487[291] = 0.0;
   out_2349771934270070487[292] = 0.0;
   out_2349771934270070487[293] = 0.0;
   out_2349771934270070487[294] = 0.0;
   out_2349771934270070487[295] = 0.0;
   out_2349771934270070487[296] = 0.0;
   out_2349771934270070487[297] = 0.0;
   out_2349771934270070487[298] = 0.0;
   out_2349771934270070487[299] = 0.0;
   out_2349771934270070487[300] = 0.0;
   out_2349771934270070487[301] = 0.0;
   out_2349771934270070487[302] = 0.0;
   out_2349771934270070487[303] = 0.0;
   out_2349771934270070487[304] = 1.0;
   out_2349771934270070487[305] = 0.0;
   out_2349771934270070487[306] = 0.0;
   out_2349771934270070487[307] = 0.0;
   out_2349771934270070487[308] = 0.0;
   out_2349771934270070487[309] = 0.0;
   out_2349771934270070487[310] = 0.0;
   out_2349771934270070487[311] = 0.0;
   out_2349771934270070487[312] = 0.0;
   out_2349771934270070487[313] = 0.0;
   out_2349771934270070487[314] = 0.0;
   out_2349771934270070487[315] = 0.0;
   out_2349771934270070487[316] = 0.0;
   out_2349771934270070487[317] = 0.0;
   out_2349771934270070487[318] = 0.0;
   out_2349771934270070487[319] = 0.0;
   out_2349771934270070487[320] = 0.0;
   out_2349771934270070487[321] = 0.0;
   out_2349771934270070487[322] = 0.0;
   out_2349771934270070487[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_872855095581035755) {
   out_872855095581035755[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_872855095581035755[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_872855095581035755[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_872855095581035755[3] = dt*state[12] + state[3];
   out_872855095581035755[4] = dt*state[13] + state[4];
   out_872855095581035755[5] = dt*state[14] + state[5];
   out_872855095581035755[6] = state[6];
   out_872855095581035755[7] = state[7];
   out_872855095581035755[8] = state[8];
   out_872855095581035755[9] = state[9];
   out_872855095581035755[10] = state[10];
   out_872855095581035755[11] = state[11];
   out_872855095581035755[12] = state[12];
   out_872855095581035755[13] = state[13];
   out_872855095581035755[14] = state[14];
   out_872855095581035755[15] = state[15];
   out_872855095581035755[16] = state[16];
   out_872855095581035755[17] = state[17];
}
void F_fun(double *state, double dt, double *out_3872170684396481521) {
   out_3872170684396481521[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_3872170684396481521[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_3872170684396481521[2] = 0;
   out_3872170684396481521[3] = 0;
   out_3872170684396481521[4] = 0;
   out_3872170684396481521[5] = 0;
   out_3872170684396481521[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_3872170684396481521[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_3872170684396481521[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_3872170684396481521[9] = 0;
   out_3872170684396481521[10] = 0;
   out_3872170684396481521[11] = 0;
   out_3872170684396481521[12] = 0;
   out_3872170684396481521[13] = 0;
   out_3872170684396481521[14] = 0;
   out_3872170684396481521[15] = 0;
   out_3872170684396481521[16] = 0;
   out_3872170684396481521[17] = 0;
   out_3872170684396481521[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_3872170684396481521[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_3872170684396481521[20] = 0;
   out_3872170684396481521[21] = 0;
   out_3872170684396481521[22] = 0;
   out_3872170684396481521[23] = 0;
   out_3872170684396481521[24] = 0;
   out_3872170684396481521[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_3872170684396481521[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_3872170684396481521[27] = 0;
   out_3872170684396481521[28] = 0;
   out_3872170684396481521[29] = 0;
   out_3872170684396481521[30] = 0;
   out_3872170684396481521[31] = 0;
   out_3872170684396481521[32] = 0;
   out_3872170684396481521[33] = 0;
   out_3872170684396481521[34] = 0;
   out_3872170684396481521[35] = 0;
   out_3872170684396481521[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_3872170684396481521[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_3872170684396481521[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_3872170684396481521[39] = 0;
   out_3872170684396481521[40] = 0;
   out_3872170684396481521[41] = 0;
   out_3872170684396481521[42] = 0;
   out_3872170684396481521[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_3872170684396481521[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_3872170684396481521[45] = 0;
   out_3872170684396481521[46] = 0;
   out_3872170684396481521[47] = 0;
   out_3872170684396481521[48] = 0;
   out_3872170684396481521[49] = 0;
   out_3872170684396481521[50] = 0;
   out_3872170684396481521[51] = 0;
   out_3872170684396481521[52] = 0;
   out_3872170684396481521[53] = 0;
   out_3872170684396481521[54] = 0;
   out_3872170684396481521[55] = 0;
   out_3872170684396481521[56] = 0;
   out_3872170684396481521[57] = 1;
   out_3872170684396481521[58] = 0;
   out_3872170684396481521[59] = 0;
   out_3872170684396481521[60] = 0;
   out_3872170684396481521[61] = 0;
   out_3872170684396481521[62] = 0;
   out_3872170684396481521[63] = 0;
   out_3872170684396481521[64] = 0;
   out_3872170684396481521[65] = 0;
   out_3872170684396481521[66] = dt;
   out_3872170684396481521[67] = 0;
   out_3872170684396481521[68] = 0;
   out_3872170684396481521[69] = 0;
   out_3872170684396481521[70] = 0;
   out_3872170684396481521[71] = 0;
   out_3872170684396481521[72] = 0;
   out_3872170684396481521[73] = 0;
   out_3872170684396481521[74] = 0;
   out_3872170684396481521[75] = 0;
   out_3872170684396481521[76] = 1;
   out_3872170684396481521[77] = 0;
   out_3872170684396481521[78] = 0;
   out_3872170684396481521[79] = 0;
   out_3872170684396481521[80] = 0;
   out_3872170684396481521[81] = 0;
   out_3872170684396481521[82] = 0;
   out_3872170684396481521[83] = 0;
   out_3872170684396481521[84] = 0;
   out_3872170684396481521[85] = dt;
   out_3872170684396481521[86] = 0;
   out_3872170684396481521[87] = 0;
   out_3872170684396481521[88] = 0;
   out_3872170684396481521[89] = 0;
   out_3872170684396481521[90] = 0;
   out_3872170684396481521[91] = 0;
   out_3872170684396481521[92] = 0;
   out_3872170684396481521[93] = 0;
   out_3872170684396481521[94] = 0;
   out_3872170684396481521[95] = 1;
   out_3872170684396481521[96] = 0;
   out_3872170684396481521[97] = 0;
   out_3872170684396481521[98] = 0;
   out_3872170684396481521[99] = 0;
   out_3872170684396481521[100] = 0;
   out_3872170684396481521[101] = 0;
   out_3872170684396481521[102] = 0;
   out_3872170684396481521[103] = 0;
   out_3872170684396481521[104] = dt;
   out_3872170684396481521[105] = 0;
   out_3872170684396481521[106] = 0;
   out_3872170684396481521[107] = 0;
   out_3872170684396481521[108] = 0;
   out_3872170684396481521[109] = 0;
   out_3872170684396481521[110] = 0;
   out_3872170684396481521[111] = 0;
   out_3872170684396481521[112] = 0;
   out_3872170684396481521[113] = 0;
   out_3872170684396481521[114] = 1;
   out_3872170684396481521[115] = 0;
   out_3872170684396481521[116] = 0;
   out_3872170684396481521[117] = 0;
   out_3872170684396481521[118] = 0;
   out_3872170684396481521[119] = 0;
   out_3872170684396481521[120] = 0;
   out_3872170684396481521[121] = 0;
   out_3872170684396481521[122] = 0;
   out_3872170684396481521[123] = 0;
   out_3872170684396481521[124] = 0;
   out_3872170684396481521[125] = 0;
   out_3872170684396481521[126] = 0;
   out_3872170684396481521[127] = 0;
   out_3872170684396481521[128] = 0;
   out_3872170684396481521[129] = 0;
   out_3872170684396481521[130] = 0;
   out_3872170684396481521[131] = 0;
   out_3872170684396481521[132] = 0;
   out_3872170684396481521[133] = 1;
   out_3872170684396481521[134] = 0;
   out_3872170684396481521[135] = 0;
   out_3872170684396481521[136] = 0;
   out_3872170684396481521[137] = 0;
   out_3872170684396481521[138] = 0;
   out_3872170684396481521[139] = 0;
   out_3872170684396481521[140] = 0;
   out_3872170684396481521[141] = 0;
   out_3872170684396481521[142] = 0;
   out_3872170684396481521[143] = 0;
   out_3872170684396481521[144] = 0;
   out_3872170684396481521[145] = 0;
   out_3872170684396481521[146] = 0;
   out_3872170684396481521[147] = 0;
   out_3872170684396481521[148] = 0;
   out_3872170684396481521[149] = 0;
   out_3872170684396481521[150] = 0;
   out_3872170684396481521[151] = 0;
   out_3872170684396481521[152] = 1;
   out_3872170684396481521[153] = 0;
   out_3872170684396481521[154] = 0;
   out_3872170684396481521[155] = 0;
   out_3872170684396481521[156] = 0;
   out_3872170684396481521[157] = 0;
   out_3872170684396481521[158] = 0;
   out_3872170684396481521[159] = 0;
   out_3872170684396481521[160] = 0;
   out_3872170684396481521[161] = 0;
   out_3872170684396481521[162] = 0;
   out_3872170684396481521[163] = 0;
   out_3872170684396481521[164] = 0;
   out_3872170684396481521[165] = 0;
   out_3872170684396481521[166] = 0;
   out_3872170684396481521[167] = 0;
   out_3872170684396481521[168] = 0;
   out_3872170684396481521[169] = 0;
   out_3872170684396481521[170] = 0;
   out_3872170684396481521[171] = 1;
   out_3872170684396481521[172] = 0;
   out_3872170684396481521[173] = 0;
   out_3872170684396481521[174] = 0;
   out_3872170684396481521[175] = 0;
   out_3872170684396481521[176] = 0;
   out_3872170684396481521[177] = 0;
   out_3872170684396481521[178] = 0;
   out_3872170684396481521[179] = 0;
   out_3872170684396481521[180] = 0;
   out_3872170684396481521[181] = 0;
   out_3872170684396481521[182] = 0;
   out_3872170684396481521[183] = 0;
   out_3872170684396481521[184] = 0;
   out_3872170684396481521[185] = 0;
   out_3872170684396481521[186] = 0;
   out_3872170684396481521[187] = 0;
   out_3872170684396481521[188] = 0;
   out_3872170684396481521[189] = 0;
   out_3872170684396481521[190] = 1;
   out_3872170684396481521[191] = 0;
   out_3872170684396481521[192] = 0;
   out_3872170684396481521[193] = 0;
   out_3872170684396481521[194] = 0;
   out_3872170684396481521[195] = 0;
   out_3872170684396481521[196] = 0;
   out_3872170684396481521[197] = 0;
   out_3872170684396481521[198] = 0;
   out_3872170684396481521[199] = 0;
   out_3872170684396481521[200] = 0;
   out_3872170684396481521[201] = 0;
   out_3872170684396481521[202] = 0;
   out_3872170684396481521[203] = 0;
   out_3872170684396481521[204] = 0;
   out_3872170684396481521[205] = 0;
   out_3872170684396481521[206] = 0;
   out_3872170684396481521[207] = 0;
   out_3872170684396481521[208] = 0;
   out_3872170684396481521[209] = 1;
   out_3872170684396481521[210] = 0;
   out_3872170684396481521[211] = 0;
   out_3872170684396481521[212] = 0;
   out_3872170684396481521[213] = 0;
   out_3872170684396481521[214] = 0;
   out_3872170684396481521[215] = 0;
   out_3872170684396481521[216] = 0;
   out_3872170684396481521[217] = 0;
   out_3872170684396481521[218] = 0;
   out_3872170684396481521[219] = 0;
   out_3872170684396481521[220] = 0;
   out_3872170684396481521[221] = 0;
   out_3872170684396481521[222] = 0;
   out_3872170684396481521[223] = 0;
   out_3872170684396481521[224] = 0;
   out_3872170684396481521[225] = 0;
   out_3872170684396481521[226] = 0;
   out_3872170684396481521[227] = 0;
   out_3872170684396481521[228] = 1;
   out_3872170684396481521[229] = 0;
   out_3872170684396481521[230] = 0;
   out_3872170684396481521[231] = 0;
   out_3872170684396481521[232] = 0;
   out_3872170684396481521[233] = 0;
   out_3872170684396481521[234] = 0;
   out_3872170684396481521[235] = 0;
   out_3872170684396481521[236] = 0;
   out_3872170684396481521[237] = 0;
   out_3872170684396481521[238] = 0;
   out_3872170684396481521[239] = 0;
   out_3872170684396481521[240] = 0;
   out_3872170684396481521[241] = 0;
   out_3872170684396481521[242] = 0;
   out_3872170684396481521[243] = 0;
   out_3872170684396481521[244] = 0;
   out_3872170684396481521[245] = 0;
   out_3872170684396481521[246] = 0;
   out_3872170684396481521[247] = 1;
   out_3872170684396481521[248] = 0;
   out_3872170684396481521[249] = 0;
   out_3872170684396481521[250] = 0;
   out_3872170684396481521[251] = 0;
   out_3872170684396481521[252] = 0;
   out_3872170684396481521[253] = 0;
   out_3872170684396481521[254] = 0;
   out_3872170684396481521[255] = 0;
   out_3872170684396481521[256] = 0;
   out_3872170684396481521[257] = 0;
   out_3872170684396481521[258] = 0;
   out_3872170684396481521[259] = 0;
   out_3872170684396481521[260] = 0;
   out_3872170684396481521[261] = 0;
   out_3872170684396481521[262] = 0;
   out_3872170684396481521[263] = 0;
   out_3872170684396481521[264] = 0;
   out_3872170684396481521[265] = 0;
   out_3872170684396481521[266] = 1;
   out_3872170684396481521[267] = 0;
   out_3872170684396481521[268] = 0;
   out_3872170684396481521[269] = 0;
   out_3872170684396481521[270] = 0;
   out_3872170684396481521[271] = 0;
   out_3872170684396481521[272] = 0;
   out_3872170684396481521[273] = 0;
   out_3872170684396481521[274] = 0;
   out_3872170684396481521[275] = 0;
   out_3872170684396481521[276] = 0;
   out_3872170684396481521[277] = 0;
   out_3872170684396481521[278] = 0;
   out_3872170684396481521[279] = 0;
   out_3872170684396481521[280] = 0;
   out_3872170684396481521[281] = 0;
   out_3872170684396481521[282] = 0;
   out_3872170684396481521[283] = 0;
   out_3872170684396481521[284] = 0;
   out_3872170684396481521[285] = 1;
   out_3872170684396481521[286] = 0;
   out_3872170684396481521[287] = 0;
   out_3872170684396481521[288] = 0;
   out_3872170684396481521[289] = 0;
   out_3872170684396481521[290] = 0;
   out_3872170684396481521[291] = 0;
   out_3872170684396481521[292] = 0;
   out_3872170684396481521[293] = 0;
   out_3872170684396481521[294] = 0;
   out_3872170684396481521[295] = 0;
   out_3872170684396481521[296] = 0;
   out_3872170684396481521[297] = 0;
   out_3872170684396481521[298] = 0;
   out_3872170684396481521[299] = 0;
   out_3872170684396481521[300] = 0;
   out_3872170684396481521[301] = 0;
   out_3872170684396481521[302] = 0;
   out_3872170684396481521[303] = 0;
   out_3872170684396481521[304] = 1;
   out_3872170684396481521[305] = 0;
   out_3872170684396481521[306] = 0;
   out_3872170684396481521[307] = 0;
   out_3872170684396481521[308] = 0;
   out_3872170684396481521[309] = 0;
   out_3872170684396481521[310] = 0;
   out_3872170684396481521[311] = 0;
   out_3872170684396481521[312] = 0;
   out_3872170684396481521[313] = 0;
   out_3872170684396481521[314] = 0;
   out_3872170684396481521[315] = 0;
   out_3872170684396481521[316] = 0;
   out_3872170684396481521[317] = 0;
   out_3872170684396481521[318] = 0;
   out_3872170684396481521[319] = 0;
   out_3872170684396481521[320] = 0;
   out_3872170684396481521[321] = 0;
   out_3872170684396481521[322] = 0;
   out_3872170684396481521[323] = 1;
}
void h_4(double *state, double *unused, double *out_8985748621613840114) {
   out_8985748621613840114[0] = state[6] + state[9];
   out_8985748621613840114[1] = state[7] + state[10];
   out_8985748621613840114[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_8197853741022029208) {
   out_8197853741022029208[0] = 0;
   out_8197853741022029208[1] = 0;
   out_8197853741022029208[2] = 0;
   out_8197853741022029208[3] = 0;
   out_8197853741022029208[4] = 0;
   out_8197853741022029208[5] = 0;
   out_8197853741022029208[6] = 1;
   out_8197853741022029208[7] = 0;
   out_8197853741022029208[8] = 0;
   out_8197853741022029208[9] = 1;
   out_8197853741022029208[10] = 0;
   out_8197853741022029208[11] = 0;
   out_8197853741022029208[12] = 0;
   out_8197853741022029208[13] = 0;
   out_8197853741022029208[14] = 0;
   out_8197853741022029208[15] = 0;
   out_8197853741022029208[16] = 0;
   out_8197853741022029208[17] = 0;
   out_8197853741022029208[18] = 0;
   out_8197853741022029208[19] = 0;
   out_8197853741022029208[20] = 0;
   out_8197853741022029208[21] = 0;
   out_8197853741022029208[22] = 0;
   out_8197853741022029208[23] = 0;
   out_8197853741022029208[24] = 0;
   out_8197853741022029208[25] = 1;
   out_8197853741022029208[26] = 0;
   out_8197853741022029208[27] = 0;
   out_8197853741022029208[28] = 1;
   out_8197853741022029208[29] = 0;
   out_8197853741022029208[30] = 0;
   out_8197853741022029208[31] = 0;
   out_8197853741022029208[32] = 0;
   out_8197853741022029208[33] = 0;
   out_8197853741022029208[34] = 0;
   out_8197853741022029208[35] = 0;
   out_8197853741022029208[36] = 0;
   out_8197853741022029208[37] = 0;
   out_8197853741022029208[38] = 0;
   out_8197853741022029208[39] = 0;
   out_8197853741022029208[40] = 0;
   out_8197853741022029208[41] = 0;
   out_8197853741022029208[42] = 0;
   out_8197853741022029208[43] = 0;
   out_8197853741022029208[44] = 1;
   out_8197853741022029208[45] = 0;
   out_8197853741022029208[46] = 0;
   out_8197853741022029208[47] = 1;
   out_8197853741022029208[48] = 0;
   out_8197853741022029208[49] = 0;
   out_8197853741022029208[50] = 0;
   out_8197853741022029208[51] = 0;
   out_8197853741022029208[52] = 0;
   out_8197853741022029208[53] = 0;
}
void h_10(double *state, double *unused, double *out_4789509988246305805) {
   out_4789509988246305805[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_4789509988246305805[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_4789509988246305805[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_4835060174289664588) {
   out_4835060174289664588[0] = 0;
   out_4835060174289664588[1] = 9.8100000000000005*cos(state[1]);
   out_4835060174289664588[2] = 0;
   out_4835060174289664588[3] = 0;
   out_4835060174289664588[4] = -state[8];
   out_4835060174289664588[5] = state[7];
   out_4835060174289664588[6] = 0;
   out_4835060174289664588[7] = state[5];
   out_4835060174289664588[8] = -state[4];
   out_4835060174289664588[9] = 0;
   out_4835060174289664588[10] = 0;
   out_4835060174289664588[11] = 0;
   out_4835060174289664588[12] = 1;
   out_4835060174289664588[13] = 0;
   out_4835060174289664588[14] = 0;
   out_4835060174289664588[15] = 1;
   out_4835060174289664588[16] = 0;
   out_4835060174289664588[17] = 0;
   out_4835060174289664588[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_4835060174289664588[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_4835060174289664588[20] = 0;
   out_4835060174289664588[21] = state[8];
   out_4835060174289664588[22] = 0;
   out_4835060174289664588[23] = -state[6];
   out_4835060174289664588[24] = -state[5];
   out_4835060174289664588[25] = 0;
   out_4835060174289664588[26] = state[3];
   out_4835060174289664588[27] = 0;
   out_4835060174289664588[28] = 0;
   out_4835060174289664588[29] = 0;
   out_4835060174289664588[30] = 0;
   out_4835060174289664588[31] = 1;
   out_4835060174289664588[32] = 0;
   out_4835060174289664588[33] = 0;
   out_4835060174289664588[34] = 1;
   out_4835060174289664588[35] = 0;
   out_4835060174289664588[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_4835060174289664588[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_4835060174289664588[38] = 0;
   out_4835060174289664588[39] = -state[7];
   out_4835060174289664588[40] = state[6];
   out_4835060174289664588[41] = 0;
   out_4835060174289664588[42] = state[4];
   out_4835060174289664588[43] = -state[3];
   out_4835060174289664588[44] = 0;
   out_4835060174289664588[45] = 0;
   out_4835060174289664588[46] = 0;
   out_4835060174289664588[47] = 0;
   out_4835060174289664588[48] = 0;
   out_4835060174289664588[49] = 0;
   out_4835060174289664588[50] = 1;
   out_4835060174289664588[51] = 0;
   out_4835060174289664588[52] = 0;
   out_4835060174289664588[53] = 1;
}
void h_13(double *state, double *unused, double *out_8593399093047740463) {
   out_8593399093047740463[0] = state[3];
   out_8593399093047740463[1] = state[4];
   out_8593399093047740463[2] = state[5];
}
void H_13(double *state, double *unused, double *out_4985579915689696407) {
   out_4985579915689696407[0] = 0;
   out_4985579915689696407[1] = 0;
   out_4985579915689696407[2] = 0;
   out_4985579915689696407[3] = 1;
   out_4985579915689696407[4] = 0;
   out_4985579915689696407[5] = 0;
   out_4985579915689696407[6] = 0;
   out_4985579915689696407[7] = 0;
   out_4985579915689696407[8] = 0;
   out_4985579915689696407[9] = 0;
   out_4985579915689696407[10] = 0;
   out_4985579915689696407[11] = 0;
   out_4985579915689696407[12] = 0;
   out_4985579915689696407[13] = 0;
   out_4985579915689696407[14] = 0;
   out_4985579915689696407[15] = 0;
   out_4985579915689696407[16] = 0;
   out_4985579915689696407[17] = 0;
   out_4985579915689696407[18] = 0;
   out_4985579915689696407[19] = 0;
   out_4985579915689696407[20] = 0;
   out_4985579915689696407[21] = 0;
   out_4985579915689696407[22] = 1;
   out_4985579915689696407[23] = 0;
   out_4985579915689696407[24] = 0;
   out_4985579915689696407[25] = 0;
   out_4985579915689696407[26] = 0;
   out_4985579915689696407[27] = 0;
   out_4985579915689696407[28] = 0;
   out_4985579915689696407[29] = 0;
   out_4985579915689696407[30] = 0;
   out_4985579915689696407[31] = 0;
   out_4985579915689696407[32] = 0;
   out_4985579915689696407[33] = 0;
   out_4985579915689696407[34] = 0;
   out_4985579915689696407[35] = 0;
   out_4985579915689696407[36] = 0;
   out_4985579915689696407[37] = 0;
   out_4985579915689696407[38] = 0;
   out_4985579915689696407[39] = 0;
   out_4985579915689696407[40] = 0;
   out_4985579915689696407[41] = 1;
   out_4985579915689696407[42] = 0;
   out_4985579915689696407[43] = 0;
   out_4985579915689696407[44] = 0;
   out_4985579915689696407[45] = 0;
   out_4985579915689696407[46] = 0;
   out_4985579915689696407[47] = 0;
   out_4985579915689696407[48] = 0;
   out_4985579915689696407[49] = 0;
   out_4985579915689696407[50] = 0;
   out_4985579915689696407[51] = 0;
   out_4985579915689696407[52] = 0;
   out_4985579915689696407[53] = 0;
}
void h_14(double *state, double *unused, double *out_4024064767553809233) {
   out_4024064767553809233[0] = state[6];
   out_4024064767553809233[1] = state[7];
   out_4024064767553809233[2] = state[8];
}
void H_14(double *state, double *unused, double *out_4234612884682544679) {
   out_4234612884682544679[0] = 0;
   out_4234612884682544679[1] = 0;
   out_4234612884682544679[2] = 0;
   out_4234612884682544679[3] = 0;
   out_4234612884682544679[4] = 0;
   out_4234612884682544679[5] = 0;
   out_4234612884682544679[6] = 1;
   out_4234612884682544679[7] = 0;
   out_4234612884682544679[8] = 0;
   out_4234612884682544679[9] = 0;
   out_4234612884682544679[10] = 0;
   out_4234612884682544679[11] = 0;
   out_4234612884682544679[12] = 0;
   out_4234612884682544679[13] = 0;
   out_4234612884682544679[14] = 0;
   out_4234612884682544679[15] = 0;
   out_4234612884682544679[16] = 0;
   out_4234612884682544679[17] = 0;
   out_4234612884682544679[18] = 0;
   out_4234612884682544679[19] = 0;
   out_4234612884682544679[20] = 0;
   out_4234612884682544679[21] = 0;
   out_4234612884682544679[22] = 0;
   out_4234612884682544679[23] = 0;
   out_4234612884682544679[24] = 0;
   out_4234612884682544679[25] = 1;
   out_4234612884682544679[26] = 0;
   out_4234612884682544679[27] = 0;
   out_4234612884682544679[28] = 0;
   out_4234612884682544679[29] = 0;
   out_4234612884682544679[30] = 0;
   out_4234612884682544679[31] = 0;
   out_4234612884682544679[32] = 0;
   out_4234612884682544679[33] = 0;
   out_4234612884682544679[34] = 0;
   out_4234612884682544679[35] = 0;
   out_4234612884682544679[36] = 0;
   out_4234612884682544679[37] = 0;
   out_4234612884682544679[38] = 0;
   out_4234612884682544679[39] = 0;
   out_4234612884682544679[40] = 0;
   out_4234612884682544679[41] = 0;
   out_4234612884682544679[42] = 0;
   out_4234612884682544679[43] = 0;
   out_4234612884682544679[44] = 1;
   out_4234612884682544679[45] = 0;
   out_4234612884682544679[46] = 0;
   out_4234612884682544679[47] = 0;
   out_4234612884682544679[48] = 0;
   out_4234612884682544679[49] = 0;
   out_4234612884682544679[50] = 0;
   out_4234612884682544679[51] = 0;
   out_4234612884682544679[52] = 0;
   out_4234612884682544679[53] = 0;
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
void pose_err_fun(double *nom_x, double *delta_x, double *out_8585539421584719708) {
  err_fun(nom_x, delta_x, out_8585539421584719708);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_6468830226543666520) {
  inv_err_fun(nom_x, true_x, out_6468830226543666520);
}
void pose_H_mod_fun(double *state, double *out_2349771934270070487) {
  H_mod_fun(state, out_2349771934270070487);
}
void pose_f_fun(double *state, double dt, double *out_872855095581035755) {
  f_fun(state,  dt, out_872855095581035755);
}
void pose_F_fun(double *state, double dt, double *out_3872170684396481521) {
  F_fun(state,  dt, out_3872170684396481521);
}
void pose_h_4(double *state, double *unused, double *out_8985748621613840114) {
  h_4(state, unused, out_8985748621613840114);
}
void pose_H_4(double *state, double *unused, double *out_8197853741022029208) {
  H_4(state, unused, out_8197853741022029208);
}
void pose_h_10(double *state, double *unused, double *out_4789509988246305805) {
  h_10(state, unused, out_4789509988246305805);
}
void pose_H_10(double *state, double *unused, double *out_4835060174289664588) {
  H_10(state, unused, out_4835060174289664588);
}
void pose_h_13(double *state, double *unused, double *out_8593399093047740463) {
  h_13(state, unused, out_8593399093047740463);
}
void pose_H_13(double *state, double *unused, double *out_4985579915689696407) {
  H_13(state, unused, out_4985579915689696407);
}
void pose_h_14(double *state, double *unused, double *out_4024064767553809233) {
  h_14(state, unused, out_4024064767553809233);
}
void pose_H_14(double *state, double *unused, double *out_4234612884682544679) {
  H_14(state, unused, out_4234612884682544679);
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
