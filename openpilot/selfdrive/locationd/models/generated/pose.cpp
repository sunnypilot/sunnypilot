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
void err_fun(double *nom_x, double *delta_x, double *out_8799966904452395012) {
   out_8799966904452395012[0] = delta_x[0] + nom_x[0];
   out_8799966904452395012[1] = delta_x[1] + nom_x[1];
   out_8799966904452395012[2] = delta_x[2] + nom_x[2];
   out_8799966904452395012[3] = delta_x[3] + nom_x[3];
   out_8799966904452395012[4] = delta_x[4] + nom_x[4];
   out_8799966904452395012[5] = delta_x[5] + nom_x[5];
   out_8799966904452395012[6] = delta_x[6] + nom_x[6];
   out_8799966904452395012[7] = delta_x[7] + nom_x[7];
   out_8799966904452395012[8] = delta_x[8] + nom_x[8];
   out_8799966904452395012[9] = delta_x[9] + nom_x[9];
   out_8799966904452395012[10] = delta_x[10] + nom_x[10];
   out_8799966904452395012[11] = delta_x[11] + nom_x[11];
   out_8799966904452395012[12] = delta_x[12] + nom_x[12];
   out_8799966904452395012[13] = delta_x[13] + nom_x[13];
   out_8799966904452395012[14] = delta_x[14] + nom_x[14];
   out_8799966904452395012[15] = delta_x[15] + nom_x[15];
   out_8799966904452395012[16] = delta_x[16] + nom_x[16];
   out_8799966904452395012[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_1661397671847398073) {
   out_1661397671847398073[0] = -nom_x[0] + true_x[0];
   out_1661397671847398073[1] = -nom_x[1] + true_x[1];
   out_1661397671847398073[2] = -nom_x[2] + true_x[2];
   out_1661397671847398073[3] = -nom_x[3] + true_x[3];
   out_1661397671847398073[4] = -nom_x[4] + true_x[4];
   out_1661397671847398073[5] = -nom_x[5] + true_x[5];
   out_1661397671847398073[6] = -nom_x[6] + true_x[6];
   out_1661397671847398073[7] = -nom_x[7] + true_x[7];
   out_1661397671847398073[8] = -nom_x[8] + true_x[8];
   out_1661397671847398073[9] = -nom_x[9] + true_x[9];
   out_1661397671847398073[10] = -nom_x[10] + true_x[10];
   out_1661397671847398073[11] = -nom_x[11] + true_x[11];
   out_1661397671847398073[12] = -nom_x[12] + true_x[12];
   out_1661397671847398073[13] = -nom_x[13] + true_x[13];
   out_1661397671847398073[14] = -nom_x[14] + true_x[14];
   out_1661397671847398073[15] = -nom_x[15] + true_x[15];
   out_1661397671847398073[16] = -nom_x[16] + true_x[16];
   out_1661397671847398073[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_2131008325054536789) {
   out_2131008325054536789[0] = 1.0;
   out_2131008325054536789[1] = 0.0;
   out_2131008325054536789[2] = 0.0;
   out_2131008325054536789[3] = 0.0;
   out_2131008325054536789[4] = 0.0;
   out_2131008325054536789[5] = 0.0;
   out_2131008325054536789[6] = 0.0;
   out_2131008325054536789[7] = 0.0;
   out_2131008325054536789[8] = 0.0;
   out_2131008325054536789[9] = 0.0;
   out_2131008325054536789[10] = 0.0;
   out_2131008325054536789[11] = 0.0;
   out_2131008325054536789[12] = 0.0;
   out_2131008325054536789[13] = 0.0;
   out_2131008325054536789[14] = 0.0;
   out_2131008325054536789[15] = 0.0;
   out_2131008325054536789[16] = 0.0;
   out_2131008325054536789[17] = 0.0;
   out_2131008325054536789[18] = 0.0;
   out_2131008325054536789[19] = 1.0;
   out_2131008325054536789[20] = 0.0;
   out_2131008325054536789[21] = 0.0;
   out_2131008325054536789[22] = 0.0;
   out_2131008325054536789[23] = 0.0;
   out_2131008325054536789[24] = 0.0;
   out_2131008325054536789[25] = 0.0;
   out_2131008325054536789[26] = 0.0;
   out_2131008325054536789[27] = 0.0;
   out_2131008325054536789[28] = 0.0;
   out_2131008325054536789[29] = 0.0;
   out_2131008325054536789[30] = 0.0;
   out_2131008325054536789[31] = 0.0;
   out_2131008325054536789[32] = 0.0;
   out_2131008325054536789[33] = 0.0;
   out_2131008325054536789[34] = 0.0;
   out_2131008325054536789[35] = 0.0;
   out_2131008325054536789[36] = 0.0;
   out_2131008325054536789[37] = 0.0;
   out_2131008325054536789[38] = 1.0;
   out_2131008325054536789[39] = 0.0;
   out_2131008325054536789[40] = 0.0;
   out_2131008325054536789[41] = 0.0;
   out_2131008325054536789[42] = 0.0;
   out_2131008325054536789[43] = 0.0;
   out_2131008325054536789[44] = 0.0;
   out_2131008325054536789[45] = 0.0;
   out_2131008325054536789[46] = 0.0;
   out_2131008325054536789[47] = 0.0;
   out_2131008325054536789[48] = 0.0;
   out_2131008325054536789[49] = 0.0;
   out_2131008325054536789[50] = 0.0;
   out_2131008325054536789[51] = 0.0;
   out_2131008325054536789[52] = 0.0;
   out_2131008325054536789[53] = 0.0;
   out_2131008325054536789[54] = 0.0;
   out_2131008325054536789[55] = 0.0;
   out_2131008325054536789[56] = 0.0;
   out_2131008325054536789[57] = 1.0;
   out_2131008325054536789[58] = 0.0;
   out_2131008325054536789[59] = 0.0;
   out_2131008325054536789[60] = 0.0;
   out_2131008325054536789[61] = 0.0;
   out_2131008325054536789[62] = 0.0;
   out_2131008325054536789[63] = 0.0;
   out_2131008325054536789[64] = 0.0;
   out_2131008325054536789[65] = 0.0;
   out_2131008325054536789[66] = 0.0;
   out_2131008325054536789[67] = 0.0;
   out_2131008325054536789[68] = 0.0;
   out_2131008325054536789[69] = 0.0;
   out_2131008325054536789[70] = 0.0;
   out_2131008325054536789[71] = 0.0;
   out_2131008325054536789[72] = 0.0;
   out_2131008325054536789[73] = 0.0;
   out_2131008325054536789[74] = 0.0;
   out_2131008325054536789[75] = 0.0;
   out_2131008325054536789[76] = 1.0;
   out_2131008325054536789[77] = 0.0;
   out_2131008325054536789[78] = 0.0;
   out_2131008325054536789[79] = 0.0;
   out_2131008325054536789[80] = 0.0;
   out_2131008325054536789[81] = 0.0;
   out_2131008325054536789[82] = 0.0;
   out_2131008325054536789[83] = 0.0;
   out_2131008325054536789[84] = 0.0;
   out_2131008325054536789[85] = 0.0;
   out_2131008325054536789[86] = 0.0;
   out_2131008325054536789[87] = 0.0;
   out_2131008325054536789[88] = 0.0;
   out_2131008325054536789[89] = 0.0;
   out_2131008325054536789[90] = 0.0;
   out_2131008325054536789[91] = 0.0;
   out_2131008325054536789[92] = 0.0;
   out_2131008325054536789[93] = 0.0;
   out_2131008325054536789[94] = 0.0;
   out_2131008325054536789[95] = 1.0;
   out_2131008325054536789[96] = 0.0;
   out_2131008325054536789[97] = 0.0;
   out_2131008325054536789[98] = 0.0;
   out_2131008325054536789[99] = 0.0;
   out_2131008325054536789[100] = 0.0;
   out_2131008325054536789[101] = 0.0;
   out_2131008325054536789[102] = 0.0;
   out_2131008325054536789[103] = 0.0;
   out_2131008325054536789[104] = 0.0;
   out_2131008325054536789[105] = 0.0;
   out_2131008325054536789[106] = 0.0;
   out_2131008325054536789[107] = 0.0;
   out_2131008325054536789[108] = 0.0;
   out_2131008325054536789[109] = 0.0;
   out_2131008325054536789[110] = 0.0;
   out_2131008325054536789[111] = 0.0;
   out_2131008325054536789[112] = 0.0;
   out_2131008325054536789[113] = 0.0;
   out_2131008325054536789[114] = 1.0;
   out_2131008325054536789[115] = 0.0;
   out_2131008325054536789[116] = 0.0;
   out_2131008325054536789[117] = 0.0;
   out_2131008325054536789[118] = 0.0;
   out_2131008325054536789[119] = 0.0;
   out_2131008325054536789[120] = 0.0;
   out_2131008325054536789[121] = 0.0;
   out_2131008325054536789[122] = 0.0;
   out_2131008325054536789[123] = 0.0;
   out_2131008325054536789[124] = 0.0;
   out_2131008325054536789[125] = 0.0;
   out_2131008325054536789[126] = 0.0;
   out_2131008325054536789[127] = 0.0;
   out_2131008325054536789[128] = 0.0;
   out_2131008325054536789[129] = 0.0;
   out_2131008325054536789[130] = 0.0;
   out_2131008325054536789[131] = 0.0;
   out_2131008325054536789[132] = 0.0;
   out_2131008325054536789[133] = 1.0;
   out_2131008325054536789[134] = 0.0;
   out_2131008325054536789[135] = 0.0;
   out_2131008325054536789[136] = 0.0;
   out_2131008325054536789[137] = 0.0;
   out_2131008325054536789[138] = 0.0;
   out_2131008325054536789[139] = 0.0;
   out_2131008325054536789[140] = 0.0;
   out_2131008325054536789[141] = 0.0;
   out_2131008325054536789[142] = 0.0;
   out_2131008325054536789[143] = 0.0;
   out_2131008325054536789[144] = 0.0;
   out_2131008325054536789[145] = 0.0;
   out_2131008325054536789[146] = 0.0;
   out_2131008325054536789[147] = 0.0;
   out_2131008325054536789[148] = 0.0;
   out_2131008325054536789[149] = 0.0;
   out_2131008325054536789[150] = 0.0;
   out_2131008325054536789[151] = 0.0;
   out_2131008325054536789[152] = 1.0;
   out_2131008325054536789[153] = 0.0;
   out_2131008325054536789[154] = 0.0;
   out_2131008325054536789[155] = 0.0;
   out_2131008325054536789[156] = 0.0;
   out_2131008325054536789[157] = 0.0;
   out_2131008325054536789[158] = 0.0;
   out_2131008325054536789[159] = 0.0;
   out_2131008325054536789[160] = 0.0;
   out_2131008325054536789[161] = 0.0;
   out_2131008325054536789[162] = 0.0;
   out_2131008325054536789[163] = 0.0;
   out_2131008325054536789[164] = 0.0;
   out_2131008325054536789[165] = 0.0;
   out_2131008325054536789[166] = 0.0;
   out_2131008325054536789[167] = 0.0;
   out_2131008325054536789[168] = 0.0;
   out_2131008325054536789[169] = 0.0;
   out_2131008325054536789[170] = 0.0;
   out_2131008325054536789[171] = 1.0;
   out_2131008325054536789[172] = 0.0;
   out_2131008325054536789[173] = 0.0;
   out_2131008325054536789[174] = 0.0;
   out_2131008325054536789[175] = 0.0;
   out_2131008325054536789[176] = 0.0;
   out_2131008325054536789[177] = 0.0;
   out_2131008325054536789[178] = 0.0;
   out_2131008325054536789[179] = 0.0;
   out_2131008325054536789[180] = 0.0;
   out_2131008325054536789[181] = 0.0;
   out_2131008325054536789[182] = 0.0;
   out_2131008325054536789[183] = 0.0;
   out_2131008325054536789[184] = 0.0;
   out_2131008325054536789[185] = 0.0;
   out_2131008325054536789[186] = 0.0;
   out_2131008325054536789[187] = 0.0;
   out_2131008325054536789[188] = 0.0;
   out_2131008325054536789[189] = 0.0;
   out_2131008325054536789[190] = 1.0;
   out_2131008325054536789[191] = 0.0;
   out_2131008325054536789[192] = 0.0;
   out_2131008325054536789[193] = 0.0;
   out_2131008325054536789[194] = 0.0;
   out_2131008325054536789[195] = 0.0;
   out_2131008325054536789[196] = 0.0;
   out_2131008325054536789[197] = 0.0;
   out_2131008325054536789[198] = 0.0;
   out_2131008325054536789[199] = 0.0;
   out_2131008325054536789[200] = 0.0;
   out_2131008325054536789[201] = 0.0;
   out_2131008325054536789[202] = 0.0;
   out_2131008325054536789[203] = 0.0;
   out_2131008325054536789[204] = 0.0;
   out_2131008325054536789[205] = 0.0;
   out_2131008325054536789[206] = 0.0;
   out_2131008325054536789[207] = 0.0;
   out_2131008325054536789[208] = 0.0;
   out_2131008325054536789[209] = 1.0;
   out_2131008325054536789[210] = 0.0;
   out_2131008325054536789[211] = 0.0;
   out_2131008325054536789[212] = 0.0;
   out_2131008325054536789[213] = 0.0;
   out_2131008325054536789[214] = 0.0;
   out_2131008325054536789[215] = 0.0;
   out_2131008325054536789[216] = 0.0;
   out_2131008325054536789[217] = 0.0;
   out_2131008325054536789[218] = 0.0;
   out_2131008325054536789[219] = 0.0;
   out_2131008325054536789[220] = 0.0;
   out_2131008325054536789[221] = 0.0;
   out_2131008325054536789[222] = 0.0;
   out_2131008325054536789[223] = 0.0;
   out_2131008325054536789[224] = 0.0;
   out_2131008325054536789[225] = 0.0;
   out_2131008325054536789[226] = 0.0;
   out_2131008325054536789[227] = 0.0;
   out_2131008325054536789[228] = 1.0;
   out_2131008325054536789[229] = 0.0;
   out_2131008325054536789[230] = 0.0;
   out_2131008325054536789[231] = 0.0;
   out_2131008325054536789[232] = 0.0;
   out_2131008325054536789[233] = 0.0;
   out_2131008325054536789[234] = 0.0;
   out_2131008325054536789[235] = 0.0;
   out_2131008325054536789[236] = 0.0;
   out_2131008325054536789[237] = 0.0;
   out_2131008325054536789[238] = 0.0;
   out_2131008325054536789[239] = 0.0;
   out_2131008325054536789[240] = 0.0;
   out_2131008325054536789[241] = 0.0;
   out_2131008325054536789[242] = 0.0;
   out_2131008325054536789[243] = 0.0;
   out_2131008325054536789[244] = 0.0;
   out_2131008325054536789[245] = 0.0;
   out_2131008325054536789[246] = 0.0;
   out_2131008325054536789[247] = 1.0;
   out_2131008325054536789[248] = 0.0;
   out_2131008325054536789[249] = 0.0;
   out_2131008325054536789[250] = 0.0;
   out_2131008325054536789[251] = 0.0;
   out_2131008325054536789[252] = 0.0;
   out_2131008325054536789[253] = 0.0;
   out_2131008325054536789[254] = 0.0;
   out_2131008325054536789[255] = 0.0;
   out_2131008325054536789[256] = 0.0;
   out_2131008325054536789[257] = 0.0;
   out_2131008325054536789[258] = 0.0;
   out_2131008325054536789[259] = 0.0;
   out_2131008325054536789[260] = 0.0;
   out_2131008325054536789[261] = 0.0;
   out_2131008325054536789[262] = 0.0;
   out_2131008325054536789[263] = 0.0;
   out_2131008325054536789[264] = 0.0;
   out_2131008325054536789[265] = 0.0;
   out_2131008325054536789[266] = 1.0;
   out_2131008325054536789[267] = 0.0;
   out_2131008325054536789[268] = 0.0;
   out_2131008325054536789[269] = 0.0;
   out_2131008325054536789[270] = 0.0;
   out_2131008325054536789[271] = 0.0;
   out_2131008325054536789[272] = 0.0;
   out_2131008325054536789[273] = 0.0;
   out_2131008325054536789[274] = 0.0;
   out_2131008325054536789[275] = 0.0;
   out_2131008325054536789[276] = 0.0;
   out_2131008325054536789[277] = 0.0;
   out_2131008325054536789[278] = 0.0;
   out_2131008325054536789[279] = 0.0;
   out_2131008325054536789[280] = 0.0;
   out_2131008325054536789[281] = 0.0;
   out_2131008325054536789[282] = 0.0;
   out_2131008325054536789[283] = 0.0;
   out_2131008325054536789[284] = 0.0;
   out_2131008325054536789[285] = 1.0;
   out_2131008325054536789[286] = 0.0;
   out_2131008325054536789[287] = 0.0;
   out_2131008325054536789[288] = 0.0;
   out_2131008325054536789[289] = 0.0;
   out_2131008325054536789[290] = 0.0;
   out_2131008325054536789[291] = 0.0;
   out_2131008325054536789[292] = 0.0;
   out_2131008325054536789[293] = 0.0;
   out_2131008325054536789[294] = 0.0;
   out_2131008325054536789[295] = 0.0;
   out_2131008325054536789[296] = 0.0;
   out_2131008325054536789[297] = 0.0;
   out_2131008325054536789[298] = 0.0;
   out_2131008325054536789[299] = 0.0;
   out_2131008325054536789[300] = 0.0;
   out_2131008325054536789[301] = 0.0;
   out_2131008325054536789[302] = 0.0;
   out_2131008325054536789[303] = 0.0;
   out_2131008325054536789[304] = 1.0;
   out_2131008325054536789[305] = 0.0;
   out_2131008325054536789[306] = 0.0;
   out_2131008325054536789[307] = 0.0;
   out_2131008325054536789[308] = 0.0;
   out_2131008325054536789[309] = 0.0;
   out_2131008325054536789[310] = 0.0;
   out_2131008325054536789[311] = 0.0;
   out_2131008325054536789[312] = 0.0;
   out_2131008325054536789[313] = 0.0;
   out_2131008325054536789[314] = 0.0;
   out_2131008325054536789[315] = 0.0;
   out_2131008325054536789[316] = 0.0;
   out_2131008325054536789[317] = 0.0;
   out_2131008325054536789[318] = 0.0;
   out_2131008325054536789[319] = 0.0;
   out_2131008325054536789[320] = 0.0;
   out_2131008325054536789[321] = 0.0;
   out_2131008325054536789[322] = 0.0;
   out_2131008325054536789[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_884777716370448931) {
   out_884777716370448931[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_884777716370448931[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_884777716370448931[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_884777716370448931[3] = dt*state[12] + state[3];
   out_884777716370448931[4] = dt*state[13] + state[4];
   out_884777716370448931[5] = dt*state[14] + state[5];
   out_884777716370448931[6] = state[6];
   out_884777716370448931[7] = state[7];
   out_884777716370448931[8] = state[8];
   out_884777716370448931[9] = state[9];
   out_884777716370448931[10] = state[10];
   out_884777716370448931[11] = state[11];
   out_884777716370448931[12] = state[12];
   out_884777716370448931[13] = state[13];
   out_884777716370448931[14] = state[14];
   out_884777716370448931[15] = state[15];
   out_884777716370448931[16] = state[16];
   out_884777716370448931[17] = state[17];
}
void F_fun(double *state, double dt, double *out_6755798908020795646) {
   out_6755798908020795646[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_6755798908020795646[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_6755798908020795646[2] = 0;
   out_6755798908020795646[3] = 0;
   out_6755798908020795646[4] = 0;
   out_6755798908020795646[5] = 0;
   out_6755798908020795646[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_6755798908020795646[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_6755798908020795646[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_6755798908020795646[9] = 0;
   out_6755798908020795646[10] = 0;
   out_6755798908020795646[11] = 0;
   out_6755798908020795646[12] = 0;
   out_6755798908020795646[13] = 0;
   out_6755798908020795646[14] = 0;
   out_6755798908020795646[15] = 0;
   out_6755798908020795646[16] = 0;
   out_6755798908020795646[17] = 0;
   out_6755798908020795646[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_6755798908020795646[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_6755798908020795646[20] = 0;
   out_6755798908020795646[21] = 0;
   out_6755798908020795646[22] = 0;
   out_6755798908020795646[23] = 0;
   out_6755798908020795646[24] = 0;
   out_6755798908020795646[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_6755798908020795646[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_6755798908020795646[27] = 0;
   out_6755798908020795646[28] = 0;
   out_6755798908020795646[29] = 0;
   out_6755798908020795646[30] = 0;
   out_6755798908020795646[31] = 0;
   out_6755798908020795646[32] = 0;
   out_6755798908020795646[33] = 0;
   out_6755798908020795646[34] = 0;
   out_6755798908020795646[35] = 0;
   out_6755798908020795646[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_6755798908020795646[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_6755798908020795646[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_6755798908020795646[39] = 0;
   out_6755798908020795646[40] = 0;
   out_6755798908020795646[41] = 0;
   out_6755798908020795646[42] = 0;
   out_6755798908020795646[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_6755798908020795646[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_6755798908020795646[45] = 0;
   out_6755798908020795646[46] = 0;
   out_6755798908020795646[47] = 0;
   out_6755798908020795646[48] = 0;
   out_6755798908020795646[49] = 0;
   out_6755798908020795646[50] = 0;
   out_6755798908020795646[51] = 0;
   out_6755798908020795646[52] = 0;
   out_6755798908020795646[53] = 0;
   out_6755798908020795646[54] = 0;
   out_6755798908020795646[55] = 0;
   out_6755798908020795646[56] = 0;
   out_6755798908020795646[57] = 1;
   out_6755798908020795646[58] = 0;
   out_6755798908020795646[59] = 0;
   out_6755798908020795646[60] = 0;
   out_6755798908020795646[61] = 0;
   out_6755798908020795646[62] = 0;
   out_6755798908020795646[63] = 0;
   out_6755798908020795646[64] = 0;
   out_6755798908020795646[65] = 0;
   out_6755798908020795646[66] = dt;
   out_6755798908020795646[67] = 0;
   out_6755798908020795646[68] = 0;
   out_6755798908020795646[69] = 0;
   out_6755798908020795646[70] = 0;
   out_6755798908020795646[71] = 0;
   out_6755798908020795646[72] = 0;
   out_6755798908020795646[73] = 0;
   out_6755798908020795646[74] = 0;
   out_6755798908020795646[75] = 0;
   out_6755798908020795646[76] = 1;
   out_6755798908020795646[77] = 0;
   out_6755798908020795646[78] = 0;
   out_6755798908020795646[79] = 0;
   out_6755798908020795646[80] = 0;
   out_6755798908020795646[81] = 0;
   out_6755798908020795646[82] = 0;
   out_6755798908020795646[83] = 0;
   out_6755798908020795646[84] = 0;
   out_6755798908020795646[85] = dt;
   out_6755798908020795646[86] = 0;
   out_6755798908020795646[87] = 0;
   out_6755798908020795646[88] = 0;
   out_6755798908020795646[89] = 0;
   out_6755798908020795646[90] = 0;
   out_6755798908020795646[91] = 0;
   out_6755798908020795646[92] = 0;
   out_6755798908020795646[93] = 0;
   out_6755798908020795646[94] = 0;
   out_6755798908020795646[95] = 1;
   out_6755798908020795646[96] = 0;
   out_6755798908020795646[97] = 0;
   out_6755798908020795646[98] = 0;
   out_6755798908020795646[99] = 0;
   out_6755798908020795646[100] = 0;
   out_6755798908020795646[101] = 0;
   out_6755798908020795646[102] = 0;
   out_6755798908020795646[103] = 0;
   out_6755798908020795646[104] = dt;
   out_6755798908020795646[105] = 0;
   out_6755798908020795646[106] = 0;
   out_6755798908020795646[107] = 0;
   out_6755798908020795646[108] = 0;
   out_6755798908020795646[109] = 0;
   out_6755798908020795646[110] = 0;
   out_6755798908020795646[111] = 0;
   out_6755798908020795646[112] = 0;
   out_6755798908020795646[113] = 0;
   out_6755798908020795646[114] = 1;
   out_6755798908020795646[115] = 0;
   out_6755798908020795646[116] = 0;
   out_6755798908020795646[117] = 0;
   out_6755798908020795646[118] = 0;
   out_6755798908020795646[119] = 0;
   out_6755798908020795646[120] = 0;
   out_6755798908020795646[121] = 0;
   out_6755798908020795646[122] = 0;
   out_6755798908020795646[123] = 0;
   out_6755798908020795646[124] = 0;
   out_6755798908020795646[125] = 0;
   out_6755798908020795646[126] = 0;
   out_6755798908020795646[127] = 0;
   out_6755798908020795646[128] = 0;
   out_6755798908020795646[129] = 0;
   out_6755798908020795646[130] = 0;
   out_6755798908020795646[131] = 0;
   out_6755798908020795646[132] = 0;
   out_6755798908020795646[133] = 1;
   out_6755798908020795646[134] = 0;
   out_6755798908020795646[135] = 0;
   out_6755798908020795646[136] = 0;
   out_6755798908020795646[137] = 0;
   out_6755798908020795646[138] = 0;
   out_6755798908020795646[139] = 0;
   out_6755798908020795646[140] = 0;
   out_6755798908020795646[141] = 0;
   out_6755798908020795646[142] = 0;
   out_6755798908020795646[143] = 0;
   out_6755798908020795646[144] = 0;
   out_6755798908020795646[145] = 0;
   out_6755798908020795646[146] = 0;
   out_6755798908020795646[147] = 0;
   out_6755798908020795646[148] = 0;
   out_6755798908020795646[149] = 0;
   out_6755798908020795646[150] = 0;
   out_6755798908020795646[151] = 0;
   out_6755798908020795646[152] = 1;
   out_6755798908020795646[153] = 0;
   out_6755798908020795646[154] = 0;
   out_6755798908020795646[155] = 0;
   out_6755798908020795646[156] = 0;
   out_6755798908020795646[157] = 0;
   out_6755798908020795646[158] = 0;
   out_6755798908020795646[159] = 0;
   out_6755798908020795646[160] = 0;
   out_6755798908020795646[161] = 0;
   out_6755798908020795646[162] = 0;
   out_6755798908020795646[163] = 0;
   out_6755798908020795646[164] = 0;
   out_6755798908020795646[165] = 0;
   out_6755798908020795646[166] = 0;
   out_6755798908020795646[167] = 0;
   out_6755798908020795646[168] = 0;
   out_6755798908020795646[169] = 0;
   out_6755798908020795646[170] = 0;
   out_6755798908020795646[171] = 1;
   out_6755798908020795646[172] = 0;
   out_6755798908020795646[173] = 0;
   out_6755798908020795646[174] = 0;
   out_6755798908020795646[175] = 0;
   out_6755798908020795646[176] = 0;
   out_6755798908020795646[177] = 0;
   out_6755798908020795646[178] = 0;
   out_6755798908020795646[179] = 0;
   out_6755798908020795646[180] = 0;
   out_6755798908020795646[181] = 0;
   out_6755798908020795646[182] = 0;
   out_6755798908020795646[183] = 0;
   out_6755798908020795646[184] = 0;
   out_6755798908020795646[185] = 0;
   out_6755798908020795646[186] = 0;
   out_6755798908020795646[187] = 0;
   out_6755798908020795646[188] = 0;
   out_6755798908020795646[189] = 0;
   out_6755798908020795646[190] = 1;
   out_6755798908020795646[191] = 0;
   out_6755798908020795646[192] = 0;
   out_6755798908020795646[193] = 0;
   out_6755798908020795646[194] = 0;
   out_6755798908020795646[195] = 0;
   out_6755798908020795646[196] = 0;
   out_6755798908020795646[197] = 0;
   out_6755798908020795646[198] = 0;
   out_6755798908020795646[199] = 0;
   out_6755798908020795646[200] = 0;
   out_6755798908020795646[201] = 0;
   out_6755798908020795646[202] = 0;
   out_6755798908020795646[203] = 0;
   out_6755798908020795646[204] = 0;
   out_6755798908020795646[205] = 0;
   out_6755798908020795646[206] = 0;
   out_6755798908020795646[207] = 0;
   out_6755798908020795646[208] = 0;
   out_6755798908020795646[209] = 1;
   out_6755798908020795646[210] = 0;
   out_6755798908020795646[211] = 0;
   out_6755798908020795646[212] = 0;
   out_6755798908020795646[213] = 0;
   out_6755798908020795646[214] = 0;
   out_6755798908020795646[215] = 0;
   out_6755798908020795646[216] = 0;
   out_6755798908020795646[217] = 0;
   out_6755798908020795646[218] = 0;
   out_6755798908020795646[219] = 0;
   out_6755798908020795646[220] = 0;
   out_6755798908020795646[221] = 0;
   out_6755798908020795646[222] = 0;
   out_6755798908020795646[223] = 0;
   out_6755798908020795646[224] = 0;
   out_6755798908020795646[225] = 0;
   out_6755798908020795646[226] = 0;
   out_6755798908020795646[227] = 0;
   out_6755798908020795646[228] = 1;
   out_6755798908020795646[229] = 0;
   out_6755798908020795646[230] = 0;
   out_6755798908020795646[231] = 0;
   out_6755798908020795646[232] = 0;
   out_6755798908020795646[233] = 0;
   out_6755798908020795646[234] = 0;
   out_6755798908020795646[235] = 0;
   out_6755798908020795646[236] = 0;
   out_6755798908020795646[237] = 0;
   out_6755798908020795646[238] = 0;
   out_6755798908020795646[239] = 0;
   out_6755798908020795646[240] = 0;
   out_6755798908020795646[241] = 0;
   out_6755798908020795646[242] = 0;
   out_6755798908020795646[243] = 0;
   out_6755798908020795646[244] = 0;
   out_6755798908020795646[245] = 0;
   out_6755798908020795646[246] = 0;
   out_6755798908020795646[247] = 1;
   out_6755798908020795646[248] = 0;
   out_6755798908020795646[249] = 0;
   out_6755798908020795646[250] = 0;
   out_6755798908020795646[251] = 0;
   out_6755798908020795646[252] = 0;
   out_6755798908020795646[253] = 0;
   out_6755798908020795646[254] = 0;
   out_6755798908020795646[255] = 0;
   out_6755798908020795646[256] = 0;
   out_6755798908020795646[257] = 0;
   out_6755798908020795646[258] = 0;
   out_6755798908020795646[259] = 0;
   out_6755798908020795646[260] = 0;
   out_6755798908020795646[261] = 0;
   out_6755798908020795646[262] = 0;
   out_6755798908020795646[263] = 0;
   out_6755798908020795646[264] = 0;
   out_6755798908020795646[265] = 0;
   out_6755798908020795646[266] = 1;
   out_6755798908020795646[267] = 0;
   out_6755798908020795646[268] = 0;
   out_6755798908020795646[269] = 0;
   out_6755798908020795646[270] = 0;
   out_6755798908020795646[271] = 0;
   out_6755798908020795646[272] = 0;
   out_6755798908020795646[273] = 0;
   out_6755798908020795646[274] = 0;
   out_6755798908020795646[275] = 0;
   out_6755798908020795646[276] = 0;
   out_6755798908020795646[277] = 0;
   out_6755798908020795646[278] = 0;
   out_6755798908020795646[279] = 0;
   out_6755798908020795646[280] = 0;
   out_6755798908020795646[281] = 0;
   out_6755798908020795646[282] = 0;
   out_6755798908020795646[283] = 0;
   out_6755798908020795646[284] = 0;
   out_6755798908020795646[285] = 1;
   out_6755798908020795646[286] = 0;
   out_6755798908020795646[287] = 0;
   out_6755798908020795646[288] = 0;
   out_6755798908020795646[289] = 0;
   out_6755798908020795646[290] = 0;
   out_6755798908020795646[291] = 0;
   out_6755798908020795646[292] = 0;
   out_6755798908020795646[293] = 0;
   out_6755798908020795646[294] = 0;
   out_6755798908020795646[295] = 0;
   out_6755798908020795646[296] = 0;
   out_6755798908020795646[297] = 0;
   out_6755798908020795646[298] = 0;
   out_6755798908020795646[299] = 0;
   out_6755798908020795646[300] = 0;
   out_6755798908020795646[301] = 0;
   out_6755798908020795646[302] = 0;
   out_6755798908020795646[303] = 0;
   out_6755798908020795646[304] = 1;
   out_6755798908020795646[305] = 0;
   out_6755798908020795646[306] = 0;
   out_6755798908020795646[307] = 0;
   out_6755798908020795646[308] = 0;
   out_6755798908020795646[309] = 0;
   out_6755798908020795646[310] = 0;
   out_6755798908020795646[311] = 0;
   out_6755798908020795646[312] = 0;
   out_6755798908020795646[313] = 0;
   out_6755798908020795646[314] = 0;
   out_6755798908020795646[315] = 0;
   out_6755798908020795646[316] = 0;
   out_6755798908020795646[317] = 0;
   out_6755798908020795646[318] = 0;
   out_6755798908020795646[319] = 0;
   out_6755798908020795646[320] = 0;
   out_6755798908020795646[321] = 0;
   out_6755798908020795646[322] = 0;
   out_6755798908020795646[323] = 1;
}
void h_4(double *state, double *unused, double *out_4561759232303120700) {
   out_4561759232303120700[0] = state[6] + state[9];
   out_4561759232303120700[1] = state[7] + state[10];
   out_4561759232303120700[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_5331418226156006813) {
   out_5331418226156006813[0] = 0;
   out_5331418226156006813[1] = 0;
   out_5331418226156006813[2] = 0;
   out_5331418226156006813[3] = 0;
   out_5331418226156006813[4] = 0;
   out_5331418226156006813[5] = 0;
   out_5331418226156006813[6] = 1;
   out_5331418226156006813[7] = 0;
   out_5331418226156006813[8] = 0;
   out_5331418226156006813[9] = 1;
   out_5331418226156006813[10] = 0;
   out_5331418226156006813[11] = 0;
   out_5331418226156006813[12] = 0;
   out_5331418226156006813[13] = 0;
   out_5331418226156006813[14] = 0;
   out_5331418226156006813[15] = 0;
   out_5331418226156006813[16] = 0;
   out_5331418226156006813[17] = 0;
   out_5331418226156006813[18] = 0;
   out_5331418226156006813[19] = 0;
   out_5331418226156006813[20] = 0;
   out_5331418226156006813[21] = 0;
   out_5331418226156006813[22] = 0;
   out_5331418226156006813[23] = 0;
   out_5331418226156006813[24] = 0;
   out_5331418226156006813[25] = 1;
   out_5331418226156006813[26] = 0;
   out_5331418226156006813[27] = 0;
   out_5331418226156006813[28] = 1;
   out_5331418226156006813[29] = 0;
   out_5331418226156006813[30] = 0;
   out_5331418226156006813[31] = 0;
   out_5331418226156006813[32] = 0;
   out_5331418226156006813[33] = 0;
   out_5331418226156006813[34] = 0;
   out_5331418226156006813[35] = 0;
   out_5331418226156006813[36] = 0;
   out_5331418226156006813[37] = 0;
   out_5331418226156006813[38] = 0;
   out_5331418226156006813[39] = 0;
   out_5331418226156006813[40] = 0;
   out_5331418226156006813[41] = 0;
   out_5331418226156006813[42] = 0;
   out_5331418226156006813[43] = 0;
   out_5331418226156006813[44] = 1;
   out_5331418226156006813[45] = 0;
   out_5331418226156006813[46] = 0;
   out_5331418226156006813[47] = 1;
   out_5331418226156006813[48] = 0;
   out_5331418226156006813[49] = 0;
   out_5331418226156006813[50] = 0;
   out_5331418226156006813[51] = 0;
   out_5331418226156006813[52] = 0;
   out_5331418226156006813[53] = 0;
}
void h_10(double *state, double *unused, double *out_8855709713594721197) {
   out_8855709713594721197[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_8855709713594721197[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_8855709713594721197[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_3758101988975610904) {
   out_3758101988975610904[0] = 0;
   out_3758101988975610904[1] = 9.8100000000000005*cos(state[1]);
   out_3758101988975610904[2] = 0;
   out_3758101988975610904[3] = 0;
   out_3758101988975610904[4] = -state[8];
   out_3758101988975610904[5] = state[7];
   out_3758101988975610904[6] = 0;
   out_3758101988975610904[7] = state[5];
   out_3758101988975610904[8] = -state[4];
   out_3758101988975610904[9] = 0;
   out_3758101988975610904[10] = 0;
   out_3758101988975610904[11] = 0;
   out_3758101988975610904[12] = 1;
   out_3758101988975610904[13] = 0;
   out_3758101988975610904[14] = 0;
   out_3758101988975610904[15] = 1;
   out_3758101988975610904[16] = 0;
   out_3758101988975610904[17] = 0;
   out_3758101988975610904[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_3758101988975610904[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_3758101988975610904[20] = 0;
   out_3758101988975610904[21] = state[8];
   out_3758101988975610904[22] = 0;
   out_3758101988975610904[23] = -state[6];
   out_3758101988975610904[24] = -state[5];
   out_3758101988975610904[25] = 0;
   out_3758101988975610904[26] = state[3];
   out_3758101988975610904[27] = 0;
   out_3758101988975610904[28] = 0;
   out_3758101988975610904[29] = 0;
   out_3758101988975610904[30] = 0;
   out_3758101988975610904[31] = 1;
   out_3758101988975610904[32] = 0;
   out_3758101988975610904[33] = 0;
   out_3758101988975610904[34] = 1;
   out_3758101988975610904[35] = 0;
   out_3758101988975610904[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_3758101988975610904[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_3758101988975610904[38] = 0;
   out_3758101988975610904[39] = -state[7];
   out_3758101988975610904[40] = state[6];
   out_3758101988975610904[41] = 0;
   out_3758101988975610904[42] = state[4];
   out_3758101988975610904[43] = -state[3];
   out_3758101988975610904[44] = 0;
   out_3758101988975610904[45] = 0;
   out_3758101988975610904[46] = 0;
   out_3758101988975610904[47] = 0;
   out_3758101988975610904[48] = 0;
   out_3758101988975610904[49] = 0;
   out_3758101988975610904[50] = 1;
   out_3758101988975610904[51] = 0;
   out_3758101988975610904[52] = 0;
   out_3758101988975610904[53] = 1;
}
void h_13(double *state, double *unused, double *out_6255148116667054704) {
   out_6255148116667054704[0] = state[3];
   out_6255148116667054704[1] = state[4];
   out_6255148116667054704[2] = state[5];
}
void H_13(double *state, double *unused, double *out_2279212982160694116) {
   out_2279212982160694116[0] = 0;
   out_2279212982160694116[1] = 0;
   out_2279212982160694116[2] = 0;
   out_2279212982160694116[3] = 1;
   out_2279212982160694116[4] = 0;
   out_2279212982160694116[5] = 0;
   out_2279212982160694116[6] = 0;
   out_2279212982160694116[7] = 0;
   out_2279212982160694116[8] = 0;
   out_2279212982160694116[9] = 0;
   out_2279212982160694116[10] = 0;
   out_2279212982160694116[11] = 0;
   out_2279212982160694116[12] = 0;
   out_2279212982160694116[13] = 0;
   out_2279212982160694116[14] = 0;
   out_2279212982160694116[15] = 0;
   out_2279212982160694116[16] = 0;
   out_2279212982160694116[17] = 0;
   out_2279212982160694116[18] = 0;
   out_2279212982160694116[19] = 0;
   out_2279212982160694116[20] = 0;
   out_2279212982160694116[21] = 0;
   out_2279212982160694116[22] = 1;
   out_2279212982160694116[23] = 0;
   out_2279212982160694116[24] = 0;
   out_2279212982160694116[25] = 0;
   out_2279212982160694116[26] = 0;
   out_2279212982160694116[27] = 0;
   out_2279212982160694116[28] = 0;
   out_2279212982160694116[29] = 0;
   out_2279212982160694116[30] = 0;
   out_2279212982160694116[31] = 0;
   out_2279212982160694116[32] = 0;
   out_2279212982160694116[33] = 0;
   out_2279212982160694116[34] = 0;
   out_2279212982160694116[35] = 0;
   out_2279212982160694116[36] = 0;
   out_2279212982160694116[37] = 0;
   out_2279212982160694116[38] = 0;
   out_2279212982160694116[39] = 0;
   out_2279212982160694116[40] = 0;
   out_2279212982160694116[41] = 1;
   out_2279212982160694116[42] = 0;
   out_2279212982160694116[43] = 0;
   out_2279212982160694116[44] = 0;
   out_2279212982160694116[45] = 0;
   out_2279212982160694116[46] = 0;
   out_2279212982160694116[47] = 0;
   out_2279212982160694116[48] = 0;
   out_2279212982160694116[49] = 0;
   out_2279212982160694116[50] = 0;
   out_2279212982160694116[51] = 0;
   out_2279212982160694116[52] = 0;
   out_2279212982160694116[53] = 0;
}
void h_14(double *state, double *unused, double *out_5422638595254952120) {
   out_5422638595254952120[0] = state[6];
   out_5422638595254952120[1] = state[7];
   out_5422638595254952120[2] = state[8];
}
void H_14(double *state, double *unused, double *out_8414206658451379109) {
   out_8414206658451379109[0] = 0;
   out_8414206658451379109[1] = 0;
   out_8414206658451379109[2] = 0;
   out_8414206658451379109[3] = 0;
   out_8414206658451379109[4] = 0;
   out_8414206658451379109[5] = 0;
   out_8414206658451379109[6] = 1;
   out_8414206658451379109[7] = 0;
   out_8414206658451379109[8] = 0;
   out_8414206658451379109[9] = 0;
   out_8414206658451379109[10] = 0;
   out_8414206658451379109[11] = 0;
   out_8414206658451379109[12] = 0;
   out_8414206658451379109[13] = 0;
   out_8414206658451379109[14] = 0;
   out_8414206658451379109[15] = 0;
   out_8414206658451379109[16] = 0;
   out_8414206658451379109[17] = 0;
   out_8414206658451379109[18] = 0;
   out_8414206658451379109[19] = 0;
   out_8414206658451379109[20] = 0;
   out_8414206658451379109[21] = 0;
   out_8414206658451379109[22] = 0;
   out_8414206658451379109[23] = 0;
   out_8414206658451379109[24] = 0;
   out_8414206658451379109[25] = 1;
   out_8414206658451379109[26] = 0;
   out_8414206658451379109[27] = 0;
   out_8414206658451379109[28] = 0;
   out_8414206658451379109[29] = 0;
   out_8414206658451379109[30] = 0;
   out_8414206658451379109[31] = 0;
   out_8414206658451379109[32] = 0;
   out_8414206658451379109[33] = 0;
   out_8414206658451379109[34] = 0;
   out_8414206658451379109[35] = 0;
   out_8414206658451379109[36] = 0;
   out_8414206658451379109[37] = 0;
   out_8414206658451379109[38] = 0;
   out_8414206658451379109[39] = 0;
   out_8414206658451379109[40] = 0;
   out_8414206658451379109[41] = 0;
   out_8414206658451379109[42] = 0;
   out_8414206658451379109[43] = 0;
   out_8414206658451379109[44] = 1;
   out_8414206658451379109[45] = 0;
   out_8414206658451379109[46] = 0;
   out_8414206658451379109[47] = 0;
   out_8414206658451379109[48] = 0;
   out_8414206658451379109[49] = 0;
   out_8414206658451379109[50] = 0;
   out_8414206658451379109[51] = 0;
   out_8414206658451379109[52] = 0;
   out_8414206658451379109[53] = 0;
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
void pose_err_fun(double *nom_x, double *delta_x, double *out_8799966904452395012) {
  err_fun(nom_x, delta_x, out_8799966904452395012);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_1661397671847398073) {
  inv_err_fun(nom_x, true_x, out_1661397671847398073);
}
void pose_H_mod_fun(double *state, double *out_2131008325054536789) {
  H_mod_fun(state, out_2131008325054536789);
}
void pose_f_fun(double *state, double dt, double *out_884777716370448931) {
  f_fun(state,  dt, out_884777716370448931);
}
void pose_F_fun(double *state, double dt, double *out_6755798908020795646) {
  F_fun(state,  dt, out_6755798908020795646);
}
void pose_h_4(double *state, double *unused, double *out_4561759232303120700) {
  h_4(state, unused, out_4561759232303120700);
}
void pose_H_4(double *state, double *unused, double *out_5331418226156006813) {
  H_4(state, unused, out_5331418226156006813);
}
void pose_h_10(double *state, double *unused, double *out_8855709713594721197) {
  h_10(state, unused, out_8855709713594721197);
}
void pose_H_10(double *state, double *unused, double *out_3758101988975610904) {
  H_10(state, unused, out_3758101988975610904);
}
void pose_h_13(double *state, double *unused, double *out_6255148116667054704) {
  h_13(state, unused, out_6255148116667054704);
}
void pose_H_13(double *state, double *unused, double *out_2279212982160694116) {
  H_13(state, unused, out_2279212982160694116);
}
void pose_h_14(double *state, double *unused, double *out_5422638595254952120) {
  h_14(state, unused, out_5422638595254952120);
}
void pose_H_14(double *state, double *unused, double *out_8414206658451379109) {
  H_14(state, unused, out_8414206658451379109);
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
