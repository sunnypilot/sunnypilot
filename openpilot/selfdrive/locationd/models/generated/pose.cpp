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
void err_fun(double *nom_x, double *delta_x, double *out_8299703332077589328) {
   out_8299703332077589328[0] = delta_x[0] + nom_x[0];
   out_8299703332077589328[1] = delta_x[1] + nom_x[1];
   out_8299703332077589328[2] = delta_x[2] + nom_x[2];
   out_8299703332077589328[3] = delta_x[3] + nom_x[3];
   out_8299703332077589328[4] = delta_x[4] + nom_x[4];
   out_8299703332077589328[5] = delta_x[5] + nom_x[5];
   out_8299703332077589328[6] = delta_x[6] + nom_x[6];
   out_8299703332077589328[7] = delta_x[7] + nom_x[7];
   out_8299703332077589328[8] = delta_x[8] + nom_x[8];
   out_8299703332077589328[9] = delta_x[9] + nom_x[9];
   out_8299703332077589328[10] = delta_x[10] + nom_x[10];
   out_8299703332077589328[11] = delta_x[11] + nom_x[11];
   out_8299703332077589328[12] = delta_x[12] + nom_x[12];
   out_8299703332077589328[13] = delta_x[13] + nom_x[13];
   out_8299703332077589328[14] = delta_x[14] + nom_x[14];
   out_8299703332077589328[15] = delta_x[15] + nom_x[15];
   out_8299703332077589328[16] = delta_x[16] + nom_x[16];
   out_8299703332077589328[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_4608058237383429265) {
   out_4608058237383429265[0] = -nom_x[0] + true_x[0];
   out_4608058237383429265[1] = -nom_x[1] + true_x[1];
   out_4608058237383429265[2] = -nom_x[2] + true_x[2];
   out_4608058237383429265[3] = -nom_x[3] + true_x[3];
   out_4608058237383429265[4] = -nom_x[4] + true_x[4];
   out_4608058237383429265[5] = -nom_x[5] + true_x[5];
   out_4608058237383429265[6] = -nom_x[6] + true_x[6];
   out_4608058237383429265[7] = -nom_x[7] + true_x[7];
   out_4608058237383429265[8] = -nom_x[8] + true_x[8];
   out_4608058237383429265[9] = -nom_x[9] + true_x[9];
   out_4608058237383429265[10] = -nom_x[10] + true_x[10];
   out_4608058237383429265[11] = -nom_x[11] + true_x[11];
   out_4608058237383429265[12] = -nom_x[12] + true_x[12];
   out_4608058237383429265[13] = -nom_x[13] + true_x[13];
   out_4608058237383429265[14] = -nom_x[14] + true_x[14];
   out_4608058237383429265[15] = -nom_x[15] + true_x[15];
   out_4608058237383429265[16] = -nom_x[16] + true_x[16];
   out_4608058237383429265[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_7885453398379249088) {
   out_7885453398379249088[0] = 1.0;
   out_7885453398379249088[1] = 0.0;
   out_7885453398379249088[2] = 0.0;
   out_7885453398379249088[3] = 0.0;
   out_7885453398379249088[4] = 0.0;
   out_7885453398379249088[5] = 0.0;
   out_7885453398379249088[6] = 0.0;
   out_7885453398379249088[7] = 0.0;
   out_7885453398379249088[8] = 0.0;
   out_7885453398379249088[9] = 0.0;
   out_7885453398379249088[10] = 0.0;
   out_7885453398379249088[11] = 0.0;
   out_7885453398379249088[12] = 0.0;
   out_7885453398379249088[13] = 0.0;
   out_7885453398379249088[14] = 0.0;
   out_7885453398379249088[15] = 0.0;
   out_7885453398379249088[16] = 0.0;
   out_7885453398379249088[17] = 0.0;
   out_7885453398379249088[18] = 0.0;
   out_7885453398379249088[19] = 1.0;
   out_7885453398379249088[20] = 0.0;
   out_7885453398379249088[21] = 0.0;
   out_7885453398379249088[22] = 0.0;
   out_7885453398379249088[23] = 0.0;
   out_7885453398379249088[24] = 0.0;
   out_7885453398379249088[25] = 0.0;
   out_7885453398379249088[26] = 0.0;
   out_7885453398379249088[27] = 0.0;
   out_7885453398379249088[28] = 0.0;
   out_7885453398379249088[29] = 0.0;
   out_7885453398379249088[30] = 0.0;
   out_7885453398379249088[31] = 0.0;
   out_7885453398379249088[32] = 0.0;
   out_7885453398379249088[33] = 0.0;
   out_7885453398379249088[34] = 0.0;
   out_7885453398379249088[35] = 0.0;
   out_7885453398379249088[36] = 0.0;
   out_7885453398379249088[37] = 0.0;
   out_7885453398379249088[38] = 1.0;
   out_7885453398379249088[39] = 0.0;
   out_7885453398379249088[40] = 0.0;
   out_7885453398379249088[41] = 0.0;
   out_7885453398379249088[42] = 0.0;
   out_7885453398379249088[43] = 0.0;
   out_7885453398379249088[44] = 0.0;
   out_7885453398379249088[45] = 0.0;
   out_7885453398379249088[46] = 0.0;
   out_7885453398379249088[47] = 0.0;
   out_7885453398379249088[48] = 0.0;
   out_7885453398379249088[49] = 0.0;
   out_7885453398379249088[50] = 0.0;
   out_7885453398379249088[51] = 0.0;
   out_7885453398379249088[52] = 0.0;
   out_7885453398379249088[53] = 0.0;
   out_7885453398379249088[54] = 0.0;
   out_7885453398379249088[55] = 0.0;
   out_7885453398379249088[56] = 0.0;
   out_7885453398379249088[57] = 1.0;
   out_7885453398379249088[58] = 0.0;
   out_7885453398379249088[59] = 0.0;
   out_7885453398379249088[60] = 0.0;
   out_7885453398379249088[61] = 0.0;
   out_7885453398379249088[62] = 0.0;
   out_7885453398379249088[63] = 0.0;
   out_7885453398379249088[64] = 0.0;
   out_7885453398379249088[65] = 0.0;
   out_7885453398379249088[66] = 0.0;
   out_7885453398379249088[67] = 0.0;
   out_7885453398379249088[68] = 0.0;
   out_7885453398379249088[69] = 0.0;
   out_7885453398379249088[70] = 0.0;
   out_7885453398379249088[71] = 0.0;
   out_7885453398379249088[72] = 0.0;
   out_7885453398379249088[73] = 0.0;
   out_7885453398379249088[74] = 0.0;
   out_7885453398379249088[75] = 0.0;
   out_7885453398379249088[76] = 1.0;
   out_7885453398379249088[77] = 0.0;
   out_7885453398379249088[78] = 0.0;
   out_7885453398379249088[79] = 0.0;
   out_7885453398379249088[80] = 0.0;
   out_7885453398379249088[81] = 0.0;
   out_7885453398379249088[82] = 0.0;
   out_7885453398379249088[83] = 0.0;
   out_7885453398379249088[84] = 0.0;
   out_7885453398379249088[85] = 0.0;
   out_7885453398379249088[86] = 0.0;
   out_7885453398379249088[87] = 0.0;
   out_7885453398379249088[88] = 0.0;
   out_7885453398379249088[89] = 0.0;
   out_7885453398379249088[90] = 0.0;
   out_7885453398379249088[91] = 0.0;
   out_7885453398379249088[92] = 0.0;
   out_7885453398379249088[93] = 0.0;
   out_7885453398379249088[94] = 0.0;
   out_7885453398379249088[95] = 1.0;
   out_7885453398379249088[96] = 0.0;
   out_7885453398379249088[97] = 0.0;
   out_7885453398379249088[98] = 0.0;
   out_7885453398379249088[99] = 0.0;
   out_7885453398379249088[100] = 0.0;
   out_7885453398379249088[101] = 0.0;
   out_7885453398379249088[102] = 0.0;
   out_7885453398379249088[103] = 0.0;
   out_7885453398379249088[104] = 0.0;
   out_7885453398379249088[105] = 0.0;
   out_7885453398379249088[106] = 0.0;
   out_7885453398379249088[107] = 0.0;
   out_7885453398379249088[108] = 0.0;
   out_7885453398379249088[109] = 0.0;
   out_7885453398379249088[110] = 0.0;
   out_7885453398379249088[111] = 0.0;
   out_7885453398379249088[112] = 0.0;
   out_7885453398379249088[113] = 0.0;
   out_7885453398379249088[114] = 1.0;
   out_7885453398379249088[115] = 0.0;
   out_7885453398379249088[116] = 0.0;
   out_7885453398379249088[117] = 0.0;
   out_7885453398379249088[118] = 0.0;
   out_7885453398379249088[119] = 0.0;
   out_7885453398379249088[120] = 0.0;
   out_7885453398379249088[121] = 0.0;
   out_7885453398379249088[122] = 0.0;
   out_7885453398379249088[123] = 0.0;
   out_7885453398379249088[124] = 0.0;
   out_7885453398379249088[125] = 0.0;
   out_7885453398379249088[126] = 0.0;
   out_7885453398379249088[127] = 0.0;
   out_7885453398379249088[128] = 0.0;
   out_7885453398379249088[129] = 0.0;
   out_7885453398379249088[130] = 0.0;
   out_7885453398379249088[131] = 0.0;
   out_7885453398379249088[132] = 0.0;
   out_7885453398379249088[133] = 1.0;
   out_7885453398379249088[134] = 0.0;
   out_7885453398379249088[135] = 0.0;
   out_7885453398379249088[136] = 0.0;
   out_7885453398379249088[137] = 0.0;
   out_7885453398379249088[138] = 0.0;
   out_7885453398379249088[139] = 0.0;
   out_7885453398379249088[140] = 0.0;
   out_7885453398379249088[141] = 0.0;
   out_7885453398379249088[142] = 0.0;
   out_7885453398379249088[143] = 0.0;
   out_7885453398379249088[144] = 0.0;
   out_7885453398379249088[145] = 0.0;
   out_7885453398379249088[146] = 0.0;
   out_7885453398379249088[147] = 0.0;
   out_7885453398379249088[148] = 0.0;
   out_7885453398379249088[149] = 0.0;
   out_7885453398379249088[150] = 0.0;
   out_7885453398379249088[151] = 0.0;
   out_7885453398379249088[152] = 1.0;
   out_7885453398379249088[153] = 0.0;
   out_7885453398379249088[154] = 0.0;
   out_7885453398379249088[155] = 0.0;
   out_7885453398379249088[156] = 0.0;
   out_7885453398379249088[157] = 0.0;
   out_7885453398379249088[158] = 0.0;
   out_7885453398379249088[159] = 0.0;
   out_7885453398379249088[160] = 0.0;
   out_7885453398379249088[161] = 0.0;
   out_7885453398379249088[162] = 0.0;
   out_7885453398379249088[163] = 0.0;
   out_7885453398379249088[164] = 0.0;
   out_7885453398379249088[165] = 0.0;
   out_7885453398379249088[166] = 0.0;
   out_7885453398379249088[167] = 0.0;
   out_7885453398379249088[168] = 0.0;
   out_7885453398379249088[169] = 0.0;
   out_7885453398379249088[170] = 0.0;
   out_7885453398379249088[171] = 1.0;
   out_7885453398379249088[172] = 0.0;
   out_7885453398379249088[173] = 0.0;
   out_7885453398379249088[174] = 0.0;
   out_7885453398379249088[175] = 0.0;
   out_7885453398379249088[176] = 0.0;
   out_7885453398379249088[177] = 0.0;
   out_7885453398379249088[178] = 0.0;
   out_7885453398379249088[179] = 0.0;
   out_7885453398379249088[180] = 0.0;
   out_7885453398379249088[181] = 0.0;
   out_7885453398379249088[182] = 0.0;
   out_7885453398379249088[183] = 0.0;
   out_7885453398379249088[184] = 0.0;
   out_7885453398379249088[185] = 0.0;
   out_7885453398379249088[186] = 0.0;
   out_7885453398379249088[187] = 0.0;
   out_7885453398379249088[188] = 0.0;
   out_7885453398379249088[189] = 0.0;
   out_7885453398379249088[190] = 1.0;
   out_7885453398379249088[191] = 0.0;
   out_7885453398379249088[192] = 0.0;
   out_7885453398379249088[193] = 0.0;
   out_7885453398379249088[194] = 0.0;
   out_7885453398379249088[195] = 0.0;
   out_7885453398379249088[196] = 0.0;
   out_7885453398379249088[197] = 0.0;
   out_7885453398379249088[198] = 0.0;
   out_7885453398379249088[199] = 0.0;
   out_7885453398379249088[200] = 0.0;
   out_7885453398379249088[201] = 0.0;
   out_7885453398379249088[202] = 0.0;
   out_7885453398379249088[203] = 0.0;
   out_7885453398379249088[204] = 0.0;
   out_7885453398379249088[205] = 0.0;
   out_7885453398379249088[206] = 0.0;
   out_7885453398379249088[207] = 0.0;
   out_7885453398379249088[208] = 0.0;
   out_7885453398379249088[209] = 1.0;
   out_7885453398379249088[210] = 0.0;
   out_7885453398379249088[211] = 0.0;
   out_7885453398379249088[212] = 0.0;
   out_7885453398379249088[213] = 0.0;
   out_7885453398379249088[214] = 0.0;
   out_7885453398379249088[215] = 0.0;
   out_7885453398379249088[216] = 0.0;
   out_7885453398379249088[217] = 0.0;
   out_7885453398379249088[218] = 0.0;
   out_7885453398379249088[219] = 0.0;
   out_7885453398379249088[220] = 0.0;
   out_7885453398379249088[221] = 0.0;
   out_7885453398379249088[222] = 0.0;
   out_7885453398379249088[223] = 0.0;
   out_7885453398379249088[224] = 0.0;
   out_7885453398379249088[225] = 0.0;
   out_7885453398379249088[226] = 0.0;
   out_7885453398379249088[227] = 0.0;
   out_7885453398379249088[228] = 1.0;
   out_7885453398379249088[229] = 0.0;
   out_7885453398379249088[230] = 0.0;
   out_7885453398379249088[231] = 0.0;
   out_7885453398379249088[232] = 0.0;
   out_7885453398379249088[233] = 0.0;
   out_7885453398379249088[234] = 0.0;
   out_7885453398379249088[235] = 0.0;
   out_7885453398379249088[236] = 0.0;
   out_7885453398379249088[237] = 0.0;
   out_7885453398379249088[238] = 0.0;
   out_7885453398379249088[239] = 0.0;
   out_7885453398379249088[240] = 0.0;
   out_7885453398379249088[241] = 0.0;
   out_7885453398379249088[242] = 0.0;
   out_7885453398379249088[243] = 0.0;
   out_7885453398379249088[244] = 0.0;
   out_7885453398379249088[245] = 0.0;
   out_7885453398379249088[246] = 0.0;
   out_7885453398379249088[247] = 1.0;
   out_7885453398379249088[248] = 0.0;
   out_7885453398379249088[249] = 0.0;
   out_7885453398379249088[250] = 0.0;
   out_7885453398379249088[251] = 0.0;
   out_7885453398379249088[252] = 0.0;
   out_7885453398379249088[253] = 0.0;
   out_7885453398379249088[254] = 0.0;
   out_7885453398379249088[255] = 0.0;
   out_7885453398379249088[256] = 0.0;
   out_7885453398379249088[257] = 0.0;
   out_7885453398379249088[258] = 0.0;
   out_7885453398379249088[259] = 0.0;
   out_7885453398379249088[260] = 0.0;
   out_7885453398379249088[261] = 0.0;
   out_7885453398379249088[262] = 0.0;
   out_7885453398379249088[263] = 0.0;
   out_7885453398379249088[264] = 0.0;
   out_7885453398379249088[265] = 0.0;
   out_7885453398379249088[266] = 1.0;
   out_7885453398379249088[267] = 0.0;
   out_7885453398379249088[268] = 0.0;
   out_7885453398379249088[269] = 0.0;
   out_7885453398379249088[270] = 0.0;
   out_7885453398379249088[271] = 0.0;
   out_7885453398379249088[272] = 0.0;
   out_7885453398379249088[273] = 0.0;
   out_7885453398379249088[274] = 0.0;
   out_7885453398379249088[275] = 0.0;
   out_7885453398379249088[276] = 0.0;
   out_7885453398379249088[277] = 0.0;
   out_7885453398379249088[278] = 0.0;
   out_7885453398379249088[279] = 0.0;
   out_7885453398379249088[280] = 0.0;
   out_7885453398379249088[281] = 0.0;
   out_7885453398379249088[282] = 0.0;
   out_7885453398379249088[283] = 0.0;
   out_7885453398379249088[284] = 0.0;
   out_7885453398379249088[285] = 1.0;
   out_7885453398379249088[286] = 0.0;
   out_7885453398379249088[287] = 0.0;
   out_7885453398379249088[288] = 0.0;
   out_7885453398379249088[289] = 0.0;
   out_7885453398379249088[290] = 0.0;
   out_7885453398379249088[291] = 0.0;
   out_7885453398379249088[292] = 0.0;
   out_7885453398379249088[293] = 0.0;
   out_7885453398379249088[294] = 0.0;
   out_7885453398379249088[295] = 0.0;
   out_7885453398379249088[296] = 0.0;
   out_7885453398379249088[297] = 0.0;
   out_7885453398379249088[298] = 0.0;
   out_7885453398379249088[299] = 0.0;
   out_7885453398379249088[300] = 0.0;
   out_7885453398379249088[301] = 0.0;
   out_7885453398379249088[302] = 0.0;
   out_7885453398379249088[303] = 0.0;
   out_7885453398379249088[304] = 1.0;
   out_7885453398379249088[305] = 0.0;
   out_7885453398379249088[306] = 0.0;
   out_7885453398379249088[307] = 0.0;
   out_7885453398379249088[308] = 0.0;
   out_7885453398379249088[309] = 0.0;
   out_7885453398379249088[310] = 0.0;
   out_7885453398379249088[311] = 0.0;
   out_7885453398379249088[312] = 0.0;
   out_7885453398379249088[313] = 0.0;
   out_7885453398379249088[314] = 0.0;
   out_7885453398379249088[315] = 0.0;
   out_7885453398379249088[316] = 0.0;
   out_7885453398379249088[317] = 0.0;
   out_7885453398379249088[318] = 0.0;
   out_7885453398379249088[319] = 0.0;
   out_7885453398379249088[320] = 0.0;
   out_7885453398379249088[321] = 0.0;
   out_7885453398379249088[322] = 0.0;
   out_7885453398379249088[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_1688144950946873165) {
   out_1688144950946873165[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_1688144950946873165[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_1688144950946873165[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_1688144950946873165[3] = dt*state[12] + state[3];
   out_1688144950946873165[4] = dt*state[13] + state[4];
   out_1688144950946873165[5] = dt*state[14] + state[5];
   out_1688144950946873165[6] = state[6];
   out_1688144950946873165[7] = state[7];
   out_1688144950946873165[8] = state[8];
   out_1688144950946873165[9] = state[9];
   out_1688144950946873165[10] = state[10];
   out_1688144950946873165[11] = state[11];
   out_1688144950946873165[12] = state[12];
   out_1688144950946873165[13] = state[13];
   out_1688144950946873165[14] = state[14];
   out_1688144950946873165[15] = state[15];
   out_1688144950946873165[16] = state[16];
   out_1688144950946873165[17] = state[17];
}
void F_fun(double *state, double dt, double *out_4851283621730691038) {
   out_4851283621730691038[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_4851283621730691038[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_4851283621730691038[2] = 0;
   out_4851283621730691038[3] = 0;
   out_4851283621730691038[4] = 0;
   out_4851283621730691038[5] = 0;
   out_4851283621730691038[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_4851283621730691038[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_4851283621730691038[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_4851283621730691038[9] = 0;
   out_4851283621730691038[10] = 0;
   out_4851283621730691038[11] = 0;
   out_4851283621730691038[12] = 0;
   out_4851283621730691038[13] = 0;
   out_4851283621730691038[14] = 0;
   out_4851283621730691038[15] = 0;
   out_4851283621730691038[16] = 0;
   out_4851283621730691038[17] = 0;
   out_4851283621730691038[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_4851283621730691038[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_4851283621730691038[20] = 0;
   out_4851283621730691038[21] = 0;
   out_4851283621730691038[22] = 0;
   out_4851283621730691038[23] = 0;
   out_4851283621730691038[24] = 0;
   out_4851283621730691038[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_4851283621730691038[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_4851283621730691038[27] = 0;
   out_4851283621730691038[28] = 0;
   out_4851283621730691038[29] = 0;
   out_4851283621730691038[30] = 0;
   out_4851283621730691038[31] = 0;
   out_4851283621730691038[32] = 0;
   out_4851283621730691038[33] = 0;
   out_4851283621730691038[34] = 0;
   out_4851283621730691038[35] = 0;
   out_4851283621730691038[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_4851283621730691038[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_4851283621730691038[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_4851283621730691038[39] = 0;
   out_4851283621730691038[40] = 0;
   out_4851283621730691038[41] = 0;
   out_4851283621730691038[42] = 0;
   out_4851283621730691038[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_4851283621730691038[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_4851283621730691038[45] = 0;
   out_4851283621730691038[46] = 0;
   out_4851283621730691038[47] = 0;
   out_4851283621730691038[48] = 0;
   out_4851283621730691038[49] = 0;
   out_4851283621730691038[50] = 0;
   out_4851283621730691038[51] = 0;
   out_4851283621730691038[52] = 0;
   out_4851283621730691038[53] = 0;
   out_4851283621730691038[54] = 0;
   out_4851283621730691038[55] = 0;
   out_4851283621730691038[56] = 0;
   out_4851283621730691038[57] = 1;
   out_4851283621730691038[58] = 0;
   out_4851283621730691038[59] = 0;
   out_4851283621730691038[60] = 0;
   out_4851283621730691038[61] = 0;
   out_4851283621730691038[62] = 0;
   out_4851283621730691038[63] = 0;
   out_4851283621730691038[64] = 0;
   out_4851283621730691038[65] = 0;
   out_4851283621730691038[66] = dt;
   out_4851283621730691038[67] = 0;
   out_4851283621730691038[68] = 0;
   out_4851283621730691038[69] = 0;
   out_4851283621730691038[70] = 0;
   out_4851283621730691038[71] = 0;
   out_4851283621730691038[72] = 0;
   out_4851283621730691038[73] = 0;
   out_4851283621730691038[74] = 0;
   out_4851283621730691038[75] = 0;
   out_4851283621730691038[76] = 1;
   out_4851283621730691038[77] = 0;
   out_4851283621730691038[78] = 0;
   out_4851283621730691038[79] = 0;
   out_4851283621730691038[80] = 0;
   out_4851283621730691038[81] = 0;
   out_4851283621730691038[82] = 0;
   out_4851283621730691038[83] = 0;
   out_4851283621730691038[84] = 0;
   out_4851283621730691038[85] = dt;
   out_4851283621730691038[86] = 0;
   out_4851283621730691038[87] = 0;
   out_4851283621730691038[88] = 0;
   out_4851283621730691038[89] = 0;
   out_4851283621730691038[90] = 0;
   out_4851283621730691038[91] = 0;
   out_4851283621730691038[92] = 0;
   out_4851283621730691038[93] = 0;
   out_4851283621730691038[94] = 0;
   out_4851283621730691038[95] = 1;
   out_4851283621730691038[96] = 0;
   out_4851283621730691038[97] = 0;
   out_4851283621730691038[98] = 0;
   out_4851283621730691038[99] = 0;
   out_4851283621730691038[100] = 0;
   out_4851283621730691038[101] = 0;
   out_4851283621730691038[102] = 0;
   out_4851283621730691038[103] = 0;
   out_4851283621730691038[104] = dt;
   out_4851283621730691038[105] = 0;
   out_4851283621730691038[106] = 0;
   out_4851283621730691038[107] = 0;
   out_4851283621730691038[108] = 0;
   out_4851283621730691038[109] = 0;
   out_4851283621730691038[110] = 0;
   out_4851283621730691038[111] = 0;
   out_4851283621730691038[112] = 0;
   out_4851283621730691038[113] = 0;
   out_4851283621730691038[114] = 1;
   out_4851283621730691038[115] = 0;
   out_4851283621730691038[116] = 0;
   out_4851283621730691038[117] = 0;
   out_4851283621730691038[118] = 0;
   out_4851283621730691038[119] = 0;
   out_4851283621730691038[120] = 0;
   out_4851283621730691038[121] = 0;
   out_4851283621730691038[122] = 0;
   out_4851283621730691038[123] = 0;
   out_4851283621730691038[124] = 0;
   out_4851283621730691038[125] = 0;
   out_4851283621730691038[126] = 0;
   out_4851283621730691038[127] = 0;
   out_4851283621730691038[128] = 0;
   out_4851283621730691038[129] = 0;
   out_4851283621730691038[130] = 0;
   out_4851283621730691038[131] = 0;
   out_4851283621730691038[132] = 0;
   out_4851283621730691038[133] = 1;
   out_4851283621730691038[134] = 0;
   out_4851283621730691038[135] = 0;
   out_4851283621730691038[136] = 0;
   out_4851283621730691038[137] = 0;
   out_4851283621730691038[138] = 0;
   out_4851283621730691038[139] = 0;
   out_4851283621730691038[140] = 0;
   out_4851283621730691038[141] = 0;
   out_4851283621730691038[142] = 0;
   out_4851283621730691038[143] = 0;
   out_4851283621730691038[144] = 0;
   out_4851283621730691038[145] = 0;
   out_4851283621730691038[146] = 0;
   out_4851283621730691038[147] = 0;
   out_4851283621730691038[148] = 0;
   out_4851283621730691038[149] = 0;
   out_4851283621730691038[150] = 0;
   out_4851283621730691038[151] = 0;
   out_4851283621730691038[152] = 1;
   out_4851283621730691038[153] = 0;
   out_4851283621730691038[154] = 0;
   out_4851283621730691038[155] = 0;
   out_4851283621730691038[156] = 0;
   out_4851283621730691038[157] = 0;
   out_4851283621730691038[158] = 0;
   out_4851283621730691038[159] = 0;
   out_4851283621730691038[160] = 0;
   out_4851283621730691038[161] = 0;
   out_4851283621730691038[162] = 0;
   out_4851283621730691038[163] = 0;
   out_4851283621730691038[164] = 0;
   out_4851283621730691038[165] = 0;
   out_4851283621730691038[166] = 0;
   out_4851283621730691038[167] = 0;
   out_4851283621730691038[168] = 0;
   out_4851283621730691038[169] = 0;
   out_4851283621730691038[170] = 0;
   out_4851283621730691038[171] = 1;
   out_4851283621730691038[172] = 0;
   out_4851283621730691038[173] = 0;
   out_4851283621730691038[174] = 0;
   out_4851283621730691038[175] = 0;
   out_4851283621730691038[176] = 0;
   out_4851283621730691038[177] = 0;
   out_4851283621730691038[178] = 0;
   out_4851283621730691038[179] = 0;
   out_4851283621730691038[180] = 0;
   out_4851283621730691038[181] = 0;
   out_4851283621730691038[182] = 0;
   out_4851283621730691038[183] = 0;
   out_4851283621730691038[184] = 0;
   out_4851283621730691038[185] = 0;
   out_4851283621730691038[186] = 0;
   out_4851283621730691038[187] = 0;
   out_4851283621730691038[188] = 0;
   out_4851283621730691038[189] = 0;
   out_4851283621730691038[190] = 1;
   out_4851283621730691038[191] = 0;
   out_4851283621730691038[192] = 0;
   out_4851283621730691038[193] = 0;
   out_4851283621730691038[194] = 0;
   out_4851283621730691038[195] = 0;
   out_4851283621730691038[196] = 0;
   out_4851283621730691038[197] = 0;
   out_4851283621730691038[198] = 0;
   out_4851283621730691038[199] = 0;
   out_4851283621730691038[200] = 0;
   out_4851283621730691038[201] = 0;
   out_4851283621730691038[202] = 0;
   out_4851283621730691038[203] = 0;
   out_4851283621730691038[204] = 0;
   out_4851283621730691038[205] = 0;
   out_4851283621730691038[206] = 0;
   out_4851283621730691038[207] = 0;
   out_4851283621730691038[208] = 0;
   out_4851283621730691038[209] = 1;
   out_4851283621730691038[210] = 0;
   out_4851283621730691038[211] = 0;
   out_4851283621730691038[212] = 0;
   out_4851283621730691038[213] = 0;
   out_4851283621730691038[214] = 0;
   out_4851283621730691038[215] = 0;
   out_4851283621730691038[216] = 0;
   out_4851283621730691038[217] = 0;
   out_4851283621730691038[218] = 0;
   out_4851283621730691038[219] = 0;
   out_4851283621730691038[220] = 0;
   out_4851283621730691038[221] = 0;
   out_4851283621730691038[222] = 0;
   out_4851283621730691038[223] = 0;
   out_4851283621730691038[224] = 0;
   out_4851283621730691038[225] = 0;
   out_4851283621730691038[226] = 0;
   out_4851283621730691038[227] = 0;
   out_4851283621730691038[228] = 1;
   out_4851283621730691038[229] = 0;
   out_4851283621730691038[230] = 0;
   out_4851283621730691038[231] = 0;
   out_4851283621730691038[232] = 0;
   out_4851283621730691038[233] = 0;
   out_4851283621730691038[234] = 0;
   out_4851283621730691038[235] = 0;
   out_4851283621730691038[236] = 0;
   out_4851283621730691038[237] = 0;
   out_4851283621730691038[238] = 0;
   out_4851283621730691038[239] = 0;
   out_4851283621730691038[240] = 0;
   out_4851283621730691038[241] = 0;
   out_4851283621730691038[242] = 0;
   out_4851283621730691038[243] = 0;
   out_4851283621730691038[244] = 0;
   out_4851283621730691038[245] = 0;
   out_4851283621730691038[246] = 0;
   out_4851283621730691038[247] = 1;
   out_4851283621730691038[248] = 0;
   out_4851283621730691038[249] = 0;
   out_4851283621730691038[250] = 0;
   out_4851283621730691038[251] = 0;
   out_4851283621730691038[252] = 0;
   out_4851283621730691038[253] = 0;
   out_4851283621730691038[254] = 0;
   out_4851283621730691038[255] = 0;
   out_4851283621730691038[256] = 0;
   out_4851283621730691038[257] = 0;
   out_4851283621730691038[258] = 0;
   out_4851283621730691038[259] = 0;
   out_4851283621730691038[260] = 0;
   out_4851283621730691038[261] = 0;
   out_4851283621730691038[262] = 0;
   out_4851283621730691038[263] = 0;
   out_4851283621730691038[264] = 0;
   out_4851283621730691038[265] = 0;
   out_4851283621730691038[266] = 1;
   out_4851283621730691038[267] = 0;
   out_4851283621730691038[268] = 0;
   out_4851283621730691038[269] = 0;
   out_4851283621730691038[270] = 0;
   out_4851283621730691038[271] = 0;
   out_4851283621730691038[272] = 0;
   out_4851283621730691038[273] = 0;
   out_4851283621730691038[274] = 0;
   out_4851283621730691038[275] = 0;
   out_4851283621730691038[276] = 0;
   out_4851283621730691038[277] = 0;
   out_4851283621730691038[278] = 0;
   out_4851283621730691038[279] = 0;
   out_4851283621730691038[280] = 0;
   out_4851283621730691038[281] = 0;
   out_4851283621730691038[282] = 0;
   out_4851283621730691038[283] = 0;
   out_4851283621730691038[284] = 0;
   out_4851283621730691038[285] = 1;
   out_4851283621730691038[286] = 0;
   out_4851283621730691038[287] = 0;
   out_4851283621730691038[288] = 0;
   out_4851283621730691038[289] = 0;
   out_4851283621730691038[290] = 0;
   out_4851283621730691038[291] = 0;
   out_4851283621730691038[292] = 0;
   out_4851283621730691038[293] = 0;
   out_4851283621730691038[294] = 0;
   out_4851283621730691038[295] = 0;
   out_4851283621730691038[296] = 0;
   out_4851283621730691038[297] = 0;
   out_4851283621730691038[298] = 0;
   out_4851283621730691038[299] = 0;
   out_4851283621730691038[300] = 0;
   out_4851283621730691038[301] = 0;
   out_4851283621730691038[302] = 0;
   out_4851283621730691038[303] = 0;
   out_4851283621730691038[304] = 1;
   out_4851283621730691038[305] = 0;
   out_4851283621730691038[306] = 0;
   out_4851283621730691038[307] = 0;
   out_4851283621730691038[308] = 0;
   out_4851283621730691038[309] = 0;
   out_4851283621730691038[310] = 0;
   out_4851283621730691038[311] = 0;
   out_4851283621730691038[312] = 0;
   out_4851283621730691038[313] = 0;
   out_4851283621730691038[314] = 0;
   out_4851283621730691038[315] = 0;
   out_4851283621730691038[316] = 0;
   out_4851283621730691038[317] = 0;
   out_4851283621730691038[318] = 0;
   out_4851283621730691038[319] = 0;
   out_4851283621730691038[320] = 0;
   out_4851283621730691038[321] = 0;
   out_4851283621730691038[322] = 0;
   out_4851283621730691038[323] = 1;
}
void h_4(double *state, double *unused, double *out_2329133011647763937) {
   out_2329133011647763937[0] = state[6] + state[9];
   out_2329133011647763937[1] = state[7] + state[10];
   out_2329133011647763937[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_8639614400433961695) {
   out_8639614400433961695[0] = 0;
   out_8639614400433961695[1] = 0;
   out_8639614400433961695[2] = 0;
   out_8639614400433961695[3] = 0;
   out_8639614400433961695[4] = 0;
   out_8639614400433961695[5] = 0;
   out_8639614400433961695[6] = 1;
   out_8639614400433961695[7] = 0;
   out_8639614400433961695[8] = 0;
   out_8639614400433961695[9] = 1;
   out_8639614400433961695[10] = 0;
   out_8639614400433961695[11] = 0;
   out_8639614400433961695[12] = 0;
   out_8639614400433961695[13] = 0;
   out_8639614400433961695[14] = 0;
   out_8639614400433961695[15] = 0;
   out_8639614400433961695[16] = 0;
   out_8639614400433961695[17] = 0;
   out_8639614400433961695[18] = 0;
   out_8639614400433961695[19] = 0;
   out_8639614400433961695[20] = 0;
   out_8639614400433961695[21] = 0;
   out_8639614400433961695[22] = 0;
   out_8639614400433961695[23] = 0;
   out_8639614400433961695[24] = 0;
   out_8639614400433961695[25] = 1;
   out_8639614400433961695[26] = 0;
   out_8639614400433961695[27] = 0;
   out_8639614400433961695[28] = 1;
   out_8639614400433961695[29] = 0;
   out_8639614400433961695[30] = 0;
   out_8639614400433961695[31] = 0;
   out_8639614400433961695[32] = 0;
   out_8639614400433961695[33] = 0;
   out_8639614400433961695[34] = 0;
   out_8639614400433961695[35] = 0;
   out_8639614400433961695[36] = 0;
   out_8639614400433961695[37] = 0;
   out_8639614400433961695[38] = 0;
   out_8639614400433961695[39] = 0;
   out_8639614400433961695[40] = 0;
   out_8639614400433961695[41] = 0;
   out_8639614400433961695[42] = 0;
   out_8639614400433961695[43] = 0;
   out_8639614400433961695[44] = 1;
   out_8639614400433961695[45] = 0;
   out_8639614400433961695[46] = 0;
   out_8639614400433961695[47] = 1;
   out_8639614400433961695[48] = 0;
   out_8639614400433961695[49] = 0;
   out_8639614400433961695[50] = 0;
   out_8639614400433961695[51] = 0;
   out_8639614400433961695[52] = 0;
   out_8639614400433961695[53] = 0;
}
void h_10(double *state, double *unused, double *out_3294648635274985008) {
   out_3294648635274985008[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_3294648635274985008[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_3294648635274985008[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_3780608178453222524) {
   out_3780608178453222524[0] = 0;
   out_3780608178453222524[1] = 9.8100000000000005*cos(state[1]);
   out_3780608178453222524[2] = 0;
   out_3780608178453222524[3] = 0;
   out_3780608178453222524[4] = -state[8];
   out_3780608178453222524[5] = state[7];
   out_3780608178453222524[6] = 0;
   out_3780608178453222524[7] = state[5];
   out_3780608178453222524[8] = -state[4];
   out_3780608178453222524[9] = 0;
   out_3780608178453222524[10] = 0;
   out_3780608178453222524[11] = 0;
   out_3780608178453222524[12] = 1;
   out_3780608178453222524[13] = 0;
   out_3780608178453222524[14] = 0;
   out_3780608178453222524[15] = 1;
   out_3780608178453222524[16] = 0;
   out_3780608178453222524[17] = 0;
   out_3780608178453222524[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_3780608178453222524[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_3780608178453222524[20] = 0;
   out_3780608178453222524[21] = state[8];
   out_3780608178453222524[22] = 0;
   out_3780608178453222524[23] = -state[6];
   out_3780608178453222524[24] = -state[5];
   out_3780608178453222524[25] = 0;
   out_3780608178453222524[26] = state[3];
   out_3780608178453222524[27] = 0;
   out_3780608178453222524[28] = 0;
   out_3780608178453222524[29] = 0;
   out_3780608178453222524[30] = 0;
   out_3780608178453222524[31] = 1;
   out_3780608178453222524[32] = 0;
   out_3780608178453222524[33] = 0;
   out_3780608178453222524[34] = 1;
   out_3780608178453222524[35] = 0;
   out_3780608178453222524[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_3780608178453222524[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_3780608178453222524[38] = 0;
   out_3780608178453222524[39] = -state[7];
   out_3780608178453222524[40] = state[6];
   out_3780608178453222524[41] = 0;
   out_3780608178453222524[42] = state[4];
   out_3780608178453222524[43] = -state[3];
   out_3780608178453222524[44] = 0;
   out_3780608178453222524[45] = 0;
   out_3780608178453222524[46] = 0;
   out_3780608178453222524[47] = 0;
   out_3780608178453222524[48] = 0;
   out_3780608178453222524[49] = 0;
   out_3780608178453222524[50] = 1;
   out_3780608178453222524[51] = 0;
   out_3780608178453222524[52] = 0;
   out_3780608178453222524[53] = 1;
}
void h_13(double *state, double *unused, double *out_8905113933939181200) {
   out_8905113933939181200[0] = state[3];
   out_8905113933939181200[1] = state[4];
   out_8905113933939181200[2] = state[5];
}
void H_13(double *state, double *unused, double *out_6594855847943257120) {
   out_6594855847943257120[0] = 0;
   out_6594855847943257120[1] = 0;
   out_6594855847943257120[2] = 0;
   out_6594855847943257120[3] = 1;
   out_6594855847943257120[4] = 0;
   out_6594855847943257120[5] = 0;
   out_6594855847943257120[6] = 0;
   out_6594855847943257120[7] = 0;
   out_6594855847943257120[8] = 0;
   out_6594855847943257120[9] = 0;
   out_6594855847943257120[10] = 0;
   out_6594855847943257120[11] = 0;
   out_6594855847943257120[12] = 0;
   out_6594855847943257120[13] = 0;
   out_6594855847943257120[14] = 0;
   out_6594855847943257120[15] = 0;
   out_6594855847943257120[16] = 0;
   out_6594855847943257120[17] = 0;
   out_6594855847943257120[18] = 0;
   out_6594855847943257120[19] = 0;
   out_6594855847943257120[20] = 0;
   out_6594855847943257120[21] = 0;
   out_6594855847943257120[22] = 1;
   out_6594855847943257120[23] = 0;
   out_6594855847943257120[24] = 0;
   out_6594855847943257120[25] = 0;
   out_6594855847943257120[26] = 0;
   out_6594855847943257120[27] = 0;
   out_6594855847943257120[28] = 0;
   out_6594855847943257120[29] = 0;
   out_6594855847943257120[30] = 0;
   out_6594855847943257120[31] = 0;
   out_6594855847943257120[32] = 0;
   out_6594855847943257120[33] = 0;
   out_6594855847943257120[34] = 0;
   out_6594855847943257120[35] = 0;
   out_6594855847943257120[36] = 0;
   out_6594855847943257120[37] = 0;
   out_6594855847943257120[38] = 0;
   out_6594855847943257120[39] = 0;
   out_6594855847943257120[40] = 0;
   out_6594855847943257120[41] = 1;
   out_6594855847943257120[42] = 0;
   out_6594855847943257120[43] = 0;
   out_6594855847943257120[44] = 0;
   out_6594855847943257120[45] = 0;
   out_6594855847943257120[46] = 0;
   out_6594855847943257120[47] = 0;
   out_6594855847943257120[48] = 0;
   out_6594855847943257120[49] = 0;
   out_6594855847943257120[50] = 0;
   out_6594855847943257120[51] = 0;
   out_6594855847943257120[52] = 0;
   out_6594855847943257120[53] = 0;
}
void h_14(double *state, double *unused, double *out_8324071568749841126) {
   out_8324071568749841126[0] = state[6];
   out_8324071568749841126[1] = state[7];
   out_8324071568749841126[2] = state[8];
}
void H_14(double *state, double *unused, double *out_5843888816936105392) {
   out_5843888816936105392[0] = 0;
   out_5843888816936105392[1] = 0;
   out_5843888816936105392[2] = 0;
   out_5843888816936105392[3] = 0;
   out_5843888816936105392[4] = 0;
   out_5843888816936105392[5] = 0;
   out_5843888816936105392[6] = 1;
   out_5843888816936105392[7] = 0;
   out_5843888816936105392[8] = 0;
   out_5843888816936105392[9] = 0;
   out_5843888816936105392[10] = 0;
   out_5843888816936105392[11] = 0;
   out_5843888816936105392[12] = 0;
   out_5843888816936105392[13] = 0;
   out_5843888816936105392[14] = 0;
   out_5843888816936105392[15] = 0;
   out_5843888816936105392[16] = 0;
   out_5843888816936105392[17] = 0;
   out_5843888816936105392[18] = 0;
   out_5843888816936105392[19] = 0;
   out_5843888816936105392[20] = 0;
   out_5843888816936105392[21] = 0;
   out_5843888816936105392[22] = 0;
   out_5843888816936105392[23] = 0;
   out_5843888816936105392[24] = 0;
   out_5843888816936105392[25] = 1;
   out_5843888816936105392[26] = 0;
   out_5843888816936105392[27] = 0;
   out_5843888816936105392[28] = 0;
   out_5843888816936105392[29] = 0;
   out_5843888816936105392[30] = 0;
   out_5843888816936105392[31] = 0;
   out_5843888816936105392[32] = 0;
   out_5843888816936105392[33] = 0;
   out_5843888816936105392[34] = 0;
   out_5843888816936105392[35] = 0;
   out_5843888816936105392[36] = 0;
   out_5843888816936105392[37] = 0;
   out_5843888816936105392[38] = 0;
   out_5843888816936105392[39] = 0;
   out_5843888816936105392[40] = 0;
   out_5843888816936105392[41] = 0;
   out_5843888816936105392[42] = 0;
   out_5843888816936105392[43] = 0;
   out_5843888816936105392[44] = 1;
   out_5843888816936105392[45] = 0;
   out_5843888816936105392[46] = 0;
   out_5843888816936105392[47] = 0;
   out_5843888816936105392[48] = 0;
   out_5843888816936105392[49] = 0;
   out_5843888816936105392[50] = 0;
   out_5843888816936105392[51] = 0;
   out_5843888816936105392[52] = 0;
   out_5843888816936105392[53] = 0;
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
void pose_err_fun(double *nom_x, double *delta_x, double *out_8299703332077589328) {
  err_fun(nom_x, delta_x, out_8299703332077589328);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_4608058237383429265) {
  inv_err_fun(nom_x, true_x, out_4608058237383429265);
}
void pose_H_mod_fun(double *state, double *out_7885453398379249088) {
  H_mod_fun(state, out_7885453398379249088);
}
void pose_f_fun(double *state, double dt, double *out_1688144950946873165) {
  f_fun(state,  dt, out_1688144950946873165);
}
void pose_F_fun(double *state, double dt, double *out_4851283621730691038) {
  F_fun(state,  dt, out_4851283621730691038);
}
void pose_h_4(double *state, double *unused, double *out_2329133011647763937) {
  h_4(state, unused, out_2329133011647763937);
}
void pose_H_4(double *state, double *unused, double *out_8639614400433961695) {
  H_4(state, unused, out_8639614400433961695);
}
void pose_h_10(double *state, double *unused, double *out_3294648635274985008) {
  h_10(state, unused, out_3294648635274985008);
}
void pose_H_10(double *state, double *unused, double *out_3780608178453222524) {
  H_10(state, unused, out_3780608178453222524);
}
void pose_h_13(double *state, double *unused, double *out_8905113933939181200) {
  h_13(state, unused, out_8905113933939181200);
}
void pose_H_13(double *state, double *unused, double *out_6594855847943257120) {
  H_13(state, unused, out_6594855847943257120);
}
void pose_h_14(double *state, double *unused, double *out_8324071568749841126) {
  h_14(state, unused, out_8324071568749841126);
}
void pose_H_14(double *state, double *unused, double *out_5843888816936105392) {
  H_14(state, unused, out_5843888816936105392);
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
