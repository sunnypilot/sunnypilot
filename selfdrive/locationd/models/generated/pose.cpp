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
void err_fun(double *nom_x, double *delta_x, double *out_1387667857402197864) {
   out_1387667857402197864[0] = delta_x[0] + nom_x[0];
   out_1387667857402197864[1] = delta_x[1] + nom_x[1];
   out_1387667857402197864[2] = delta_x[2] + nom_x[2];
   out_1387667857402197864[3] = delta_x[3] + nom_x[3];
   out_1387667857402197864[4] = delta_x[4] + nom_x[4];
   out_1387667857402197864[5] = delta_x[5] + nom_x[5];
   out_1387667857402197864[6] = delta_x[6] + nom_x[6];
   out_1387667857402197864[7] = delta_x[7] + nom_x[7];
   out_1387667857402197864[8] = delta_x[8] + nom_x[8];
   out_1387667857402197864[9] = delta_x[9] + nom_x[9];
   out_1387667857402197864[10] = delta_x[10] + nom_x[10];
   out_1387667857402197864[11] = delta_x[11] + nom_x[11];
   out_1387667857402197864[12] = delta_x[12] + nom_x[12];
   out_1387667857402197864[13] = delta_x[13] + nom_x[13];
   out_1387667857402197864[14] = delta_x[14] + nom_x[14];
   out_1387667857402197864[15] = delta_x[15] + nom_x[15];
   out_1387667857402197864[16] = delta_x[16] + nom_x[16];
   out_1387667857402197864[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_7508820603663648737) {
   out_7508820603663648737[0] = -nom_x[0] + true_x[0];
   out_7508820603663648737[1] = -nom_x[1] + true_x[1];
   out_7508820603663648737[2] = -nom_x[2] + true_x[2];
   out_7508820603663648737[3] = -nom_x[3] + true_x[3];
   out_7508820603663648737[4] = -nom_x[4] + true_x[4];
   out_7508820603663648737[5] = -nom_x[5] + true_x[5];
   out_7508820603663648737[6] = -nom_x[6] + true_x[6];
   out_7508820603663648737[7] = -nom_x[7] + true_x[7];
   out_7508820603663648737[8] = -nom_x[8] + true_x[8];
   out_7508820603663648737[9] = -nom_x[9] + true_x[9];
   out_7508820603663648737[10] = -nom_x[10] + true_x[10];
   out_7508820603663648737[11] = -nom_x[11] + true_x[11];
   out_7508820603663648737[12] = -nom_x[12] + true_x[12];
   out_7508820603663648737[13] = -nom_x[13] + true_x[13];
   out_7508820603663648737[14] = -nom_x[14] + true_x[14];
   out_7508820603663648737[15] = -nom_x[15] + true_x[15];
   out_7508820603663648737[16] = -nom_x[16] + true_x[16];
   out_7508820603663648737[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_6469646688903378101) {
   out_6469646688903378101[0] = 1.0;
   out_6469646688903378101[1] = 0.0;
   out_6469646688903378101[2] = 0.0;
   out_6469646688903378101[3] = 0.0;
   out_6469646688903378101[4] = 0.0;
   out_6469646688903378101[5] = 0.0;
   out_6469646688903378101[6] = 0.0;
   out_6469646688903378101[7] = 0.0;
   out_6469646688903378101[8] = 0.0;
   out_6469646688903378101[9] = 0.0;
   out_6469646688903378101[10] = 0.0;
   out_6469646688903378101[11] = 0.0;
   out_6469646688903378101[12] = 0.0;
   out_6469646688903378101[13] = 0.0;
   out_6469646688903378101[14] = 0.0;
   out_6469646688903378101[15] = 0.0;
   out_6469646688903378101[16] = 0.0;
   out_6469646688903378101[17] = 0.0;
   out_6469646688903378101[18] = 0.0;
   out_6469646688903378101[19] = 1.0;
   out_6469646688903378101[20] = 0.0;
   out_6469646688903378101[21] = 0.0;
   out_6469646688903378101[22] = 0.0;
   out_6469646688903378101[23] = 0.0;
   out_6469646688903378101[24] = 0.0;
   out_6469646688903378101[25] = 0.0;
   out_6469646688903378101[26] = 0.0;
   out_6469646688903378101[27] = 0.0;
   out_6469646688903378101[28] = 0.0;
   out_6469646688903378101[29] = 0.0;
   out_6469646688903378101[30] = 0.0;
   out_6469646688903378101[31] = 0.0;
   out_6469646688903378101[32] = 0.0;
   out_6469646688903378101[33] = 0.0;
   out_6469646688903378101[34] = 0.0;
   out_6469646688903378101[35] = 0.0;
   out_6469646688903378101[36] = 0.0;
   out_6469646688903378101[37] = 0.0;
   out_6469646688903378101[38] = 1.0;
   out_6469646688903378101[39] = 0.0;
   out_6469646688903378101[40] = 0.0;
   out_6469646688903378101[41] = 0.0;
   out_6469646688903378101[42] = 0.0;
   out_6469646688903378101[43] = 0.0;
   out_6469646688903378101[44] = 0.0;
   out_6469646688903378101[45] = 0.0;
   out_6469646688903378101[46] = 0.0;
   out_6469646688903378101[47] = 0.0;
   out_6469646688903378101[48] = 0.0;
   out_6469646688903378101[49] = 0.0;
   out_6469646688903378101[50] = 0.0;
   out_6469646688903378101[51] = 0.0;
   out_6469646688903378101[52] = 0.0;
   out_6469646688903378101[53] = 0.0;
   out_6469646688903378101[54] = 0.0;
   out_6469646688903378101[55] = 0.0;
   out_6469646688903378101[56] = 0.0;
   out_6469646688903378101[57] = 1.0;
   out_6469646688903378101[58] = 0.0;
   out_6469646688903378101[59] = 0.0;
   out_6469646688903378101[60] = 0.0;
   out_6469646688903378101[61] = 0.0;
   out_6469646688903378101[62] = 0.0;
   out_6469646688903378101[63] = 0.0;
   out_6469646688903378101[64] = 0.0;
   out_6469646688903378101[65] = 0.0;
   out_6469646688903378101[66] = 0.0;
   out_6469646688903378101[67] = 0.0;
   out_6469646688903378101[68] = 0.0;
   out_6469646688903378101[69] = 0.0;
   out_6469646688903378101[70] = 0.0;
   out_6469646688903378101[71] = 0.0;
   out_6469646688903378101[72] = 0.0;
   out_6469646688903378101[73] = 0.0;
   out_6469646688903378101[74] = 0.0;
   out_6469646688903378101[75] = 0.0;
   out_6469646688903378101[76] = 1.0;
   out_6469646688903378101[77] = 0.0;
   out_6469646688903378101[78] = 0.0;
   out_6469646688903378101[79] = 0.0;
   out_6469646688903378101[80] = 0.0;
   out_6469646688903378101[81] = 0.0;
   out_6469646688903378101[82] = 0.0;
   out_6469646688903378101[83] = 0.0;
   out_6469646688903378101[84] = 0.0;
   out_6469646688903378101[85] = 0.0;
   out_6469646688903378101[86] = 0.0;
   out_6469646688903378101[87] = 0.0;
   out_6469646688903378101[88] = 0.0;
   out_6469646688903378101[89] = 0.0;
   out_6469646688903378101[90] = 0.0;
   out_6469646688903378101[91] = 0.0;
   out_6469646688903378101[92] = 0.0;
   out_6469646688903378101[93] = 0.0;
   out_6469646688903378101[94] = 0.0;
   out_6469646688903378101[95] = 1.0;
   out_6469646688903378101[96] = 0.0;
   out_6469646688903378101[97] = 0.0;
   out_6469646688903378101[98] = 0.0;
   out_6469646688903378101[99] = 0.0;
   out_6469646688903378101[100] = 0.0;
   out_6469646688903378101[101] = 0.0;
   out_6469646688903378101[102] = 0.0;
   out_6469646688903378101[103] = 0.0;
   out_6469646688903378101[104] = 0.0;
   out_6469646688903378101[105] = 0.0;
   out_6469646688903378101[106] = 0.0;
   out_6469646688903378101[107] = 0.0;
   out_6469646688903378101[108] = 0.0;
   out_6469646688903378101[109] = 0.0;
   out_6469646688903378101[110] = 0.0;
   out_6469646688903378101[111] = 0.0;
   out_6469646688903378101[112] = 0.0;
   out_6469646688903378101[113] = 0.0;
   out_6469646688903378101[114] = 1.0;
   out_6469646688903378101[115] = 0.0;
   out_6469646688903378101[116] = 0.0;
   out_6469646688903378101[117] = 0.0;
   out_6469646688903378101[118] = 0.0;
   out_6469646688903378101[119] = 0.0;
   out_6469646688903378101[120] = 0.0;
   out_6469646688903378101[121] = 0.0;
   out_6469646688903378101[122] = 0.0;
   out_6469646688903378101[123] = 0.0;
   out_6469646688903378101[124] = 0.0;
   out_6469646688903378101[125] = 0.0;
   out_6469646688903378101[126] = 0.0;
   out_6469646688903378101[127] = 0.0;
   out_6469646688903378101[128] = 0.0;
   out_6469646688903378101[129] = 0.0;
   out_6469646688903378101[130] = 0.0;
   out_6469646688903378101[131] = 0.0;
   out_6469646688903378101[132] = 0.0;
   out_6469646688903378101[133] = 1.0;
   out_6469646688903378101[134] = 0.0;
   out_6469646688903378101[135] = 0.0;
   out_6469646688903378101[136] = 0.0;
   out_6469646688903378101[137] = 0.0;
   out_6469646688903378101[138] = 0.0;
   out_6469646688903378101[139] = 0.0;
   out_6469646688903378101[140] = 0.0;
   out_6469646688903378101[141] = 0.0;
   out_6469646688903378101[142] = 0.0;
   out_6469646688903378101[143] = 0.0;
   out_6469646688903378101[144] = 0.0;
   out_6469646688903378101[145] = 0.0;
   out_6469646688903378101[146] = 0.0;
   out_6469646688903378101[147] = 0.0;
   out_6469646688903378101[148] = 0.0;
   out_6469646688903378101[149] = 0.0;
   out_6469646688903378101[150] = 0.0;
   out_6469646688903378101[151] = 0.0;
   out_6469646688903378101[152] = 1.0;
   out_6469646688903378101[153] = 0.0;
   out_6469646688903378101[154] = 0.0;
   out_6469646688903378101[155] = 0.0;
   out_6469646688903378101[156] = 0.0;
   out_6469646688903378101[157] = 0.0;
   out_6469646688903378101[158] = 0.0;
   out_6469646688903378101[159] = 0.0;
   out_6469646688903378101[160] = 0.0;
   out_6469646688903378101[161] = 0.0;
   out_6469646688903378101[162] = 0.0;
   out_6469646688903378101[163] = 0.0;
   out_6469646688903378101[164] = 0.0;
   out_6469646688903378101[165] = 0.0;
   out_6469646688903378101[166] = 0.0;
   out_6469646688903378101[167] = 0.0;
   out_6469646688903378101[168] = 0.0;
   out_6469646688903378101[169] = 0.0;
   out_6469646688903378101[170] = 0.0;
   out_6469646688903378101[171] = 1.0;
   out_6469646688903378101[172] = 0.0;
   out_6469646688903378101[173] = 0.0;
   out_6469646688903378101[174] = 0.0;
   out_6469646688903378101[175] = 0.0;
   out_6469646688903378101[176] = 0.0;
   out_6469646688903378101[177] = 0.0;
   out_6469646688903378101[178] = 0.0;
   out_6469646688903378101[179] = 0.0;
   out_6469646688903378101[180] = 0.0;
   out_6469646688903378101[181] = 0.0;
   out_6469646688903378101[182] = 0.0;
   out_6469646688903378101[183] = 0.0;
   out_6469646688903378101[184] = 0.0;
   out_6469646688903378101[185] = 0.0;
   out_6469646688903378101[186] = 0.0;
   out_6469646688903378101[187] = 0.0;
   out_6469646688903378101[188] = 0.0;
   out_6469646688903378101[189] = 0.0;
   out_6469646688903378101[190] = 1.0;
   out_6469646688903378101[191] = 0.0;
   out_6469646688903378101[192] = 0.0;
   out_6469646688903378101[193] = 0.0;
   out_6469646688903378101[194] = 0.0;
   out_6469646688903378101[195] = 0.0;
   out_6469646688903378101[196] = 0.0;
   out_6469646688903378101[197] = 0.0;
   out_6469646688903378101[198] = 0.0;
   out_6469646688903378101[199] = 0.0;
   out_6469646688903378101[200] = 0.0;
   out_6469646688903378101[201] = 0.0;
   out_6469646688903378101[202] = 0.0;
   out_6469646688903378101[203] = 0.0;
   out_6469646688903378101[204] = 0.0;
   out_6469646688903378101[205] = 0.0;
   out_6469646688903378101[206] = 0.0;
   out_6469646688903378101[207] = 0.0;
   out_6469646688903378101[208] = 0.0;
   out_6469646688903378101[209] = 1.0;
   out_6469646688903378101[210] = 0.0;
   out_6469646688903378101[211] = 0.0;
   out_6469646688903378101[212] = 0.0;
   out_6469646688903378101[213] = 0.0;
   out_6469646688903378101[214] = 0.0;
   out_6469646688903378101[215] = 0.0;
   out_6469646688903378101[216] = 0.0;
   out_6469646688903378101[217] = 0.0;
   out_6469646688903378101[218] = 0.0;
   out_6469646688903378101[219] = 0.0;
   out_6469646688903378101[220] = 0.0;
   out_6469646688903378101[221] = 0.0;
   out_6469646688903378101[222] = 0.0;
   out_6469646688903378101[223] = 0.0;
   out_6469646688903378101[224] = 0.0;
   out_6469646688903378101[225] = 0.0;
   out_6469646688903378101[226] = 0.0;
   out_6469646688903378101[227] = 0.0;
   out_6469646688903378101[228] = 1.0;
   out_6469646688903378101[229] = 0.0;
   out_6469646688903378101[230] = 0.0;
   out_6469646688903378101[231] = 0.0;
   out_6469646688903378101[232] = 0.0;
   out_6469646688903378101[233] = 0.0;
   out_6469646688903378101[234] = 0.0;
   out_6469646688903378101[235] = 0.0;
   out_6469646688903378101[236] = 0.0;
   out_6469646688903378101[237] = 0.0;
   out_6469646688903378101[238] = 0.0;
   out_6469646688903378101[239] = 0.0;
   out_6469646688903378101[240] = 0.0;
   out_6469646688903378101[241] = 0.0;
   out_6469646688903378101[242] = 0.0;
   out_6469646688903378101[243] = 0.0;
   out_6469646688903378101[244] = 0.0;
   out_6469646688903378101[245] = 0.0;
   out_6469646688903378101[246] = 0.0;
   out_6469646688903378101[247] = 1.0;
   out_6469646688903378101[248] = 0.0;
   out_6469646688903378101[249] = 0.0;
   out_6469646688903378101[250] = 0.0;
   out_6469646688903378101[251] = 0.0;
   out_6469646688903378101[252] = 0.0;
   out_6469646688903378101[253] = 0.0;
   out_6469646688903378101[254] = 0.0;
   out_6469646688903378101[255] = 0.0;
   out_6469646688903378101[256] = 0.0;
   out_6469646688903378101[257] = 0.0;
   out_6469646688903378101[258] = 0.0;
   out_6469646688903378101[259] = 0.0;
   out_6469646688903378101[260] = 0.0;
   out_6469646688903378101[261] = 0.0;
   out_6469646688903378101[262] = 0.0;
   out_6469646688903378101[263] = 0.0;
   out_6469646688903378101[264] = 0.0;
   out_6469646688903378101[265] = 0.0;
   out_6469646688903378101[266] = 1.0;
   out_6469646688903378101[267] = 0.0;
   out_6469646688903378101[268] = 0.0;
   out_6469646688903378101[269] = 0.0;
   out_6469646688903378101[270] = 0.0;
   out_6469646688903378101[271] = 0.0;
   out_6469646688903378101[272] = 0.0;
   out_6469646688903378101[273] = 0.0;
   out_6469646688903378101[274] = 0.0;
   out_6469646688903378101[275] = 0.0;
   out_6469646688903378101[276] = 0.0;
   out_6469646688903378101[277] = 0.0;
   out_6469646688903378101[278] = 0.0;
   out_6469646688903378101[279] = 0.0;
   out_6469646688903378101[280] = 0.0;
   out_6469646688903378101[281] = 0.0;
   out_6469646688903378101[282] = 0.0;
   out_6469646688903378101[283] = 0.0;
   out_6469646688903378101[284] = 0.0;
   out_6469646688903378101[285] = 1.0;
   out_6469646688903378101[286] = 0.0;
   out_6469646688903378101[287] = 0.0;
   out_6469646688903378101[288] = 0.0;
   out_6469646688903378101[289] = 0.0;
   out_6469646688903378101[290] = 0.0;
   out_6469646688903378101[291] = 0.0;
   out_6469646688903378101[292] = 0.0;
   out_6469646688903378101[293] = 0.0;
   out_6469646688903378101[294] = 0.0;
   out_6469646688903378101[295] = 0.0;
   out_6469646688903378101[296] = 0.0;
   out_6469646688903378101[297] = 0.0;
   out_6469646688903378101[298] = 0.0;
   out_6469646688903378101[299] = 0.0;
   out_6469646688903378101[300] = 0.0;
   out_6469646688903378101[301] = 0.0;
   out_6469646688903378101[302] = 0.0;
   out_6469646688903378101[303] = 0.0;
   out_6469646688903378101[304] = 1.0;
   out_6469646688903378101[305] = 0.0;
   out_6469646688903378101[306] = 0.0;
   out_6469646688903378101[307] = 0.0;
   out_6469646688903378101[308] = 0.0;
   out_6469646688903378101[309] = 0.0;
   out_6469646688903378101[310] = 0.0;
   out_6469646688903378101[311] = 0.0;
   out_6469646688903378101[312] = 0.0;
   out_6469646688903378101[313] = 0.0;
   out_6469646688903378101[314] = 0.0;
   out_6469646688903378101[315] = 0.0;
   out_6469646688903378101[316] = 0.0;
   out_6469646688903378101[317] = 0.0;
   out_6469646688903378101[318] = 0.0;
   out_6469646688903378101[319] = 0.0;
   out_6469646688903378101[320] = 0.0;
   out_6469646688903378101[321] = 0.0;
   out_6469646688903378101[322] = 0.0;
   out_6469646688903378101[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_6697963188238977834) {
   out_6697963188238977834[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_6697963188238977834[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_6697963188238977834[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_6697963188238977834[3] = dt*state[12] + state[3];
   out_6697963188238977834[4] = dt*state[13] + state[4];
   out_6697963188238977834[5] = dt*state[14] + state[5];
   out_6697963188238977834[6] = state[6];
   out_6697963188238977834[7] = state[7];
   out_6697963188238977834[8] = state[8];
   out_6697963188238977834[9] = state[9];
   out_6697963188238977834[10] = state[10];
   out_6697963188238977834[11] = state[11];
   out_6697963188238977834[12] = state[12];
   out_6697963188238977834[13] = state[13];
   out_6697963188238977834[14] = state[14];
   out_6697963188238977834[15] = state[15];
   out_6697963188238977834[16] = state[16];
   out_6697963188238977834[17] = state[17];
}
void F_fun(double *state, double dt, double *out_429527558939684598) {
   out_429527558939684598[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_429527558939684598[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_429527558939684598[2] = 0;
   out_429527558939684598[3] = 0;
   out_429527558939684598[4] = 0;
   out_429527558939684598[5] = 0;
   out_429527558939684598[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_429527558939684598[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_429527558939684598[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_429527558939684598[9] = 0;
   out_429527558939684598[10] = 0;
   out_429527558939684598[11] = 0;
   out_429527558939684598[12] = 0;
   out_429527558939684598[13] = 0;
   out_429527558939684598[14] = 0;
   out_429527558939684598[15] = 0;
   out_429527558939684598[16] = 0;
   out_429527558939684598[17] = 0;
   out_429527558939684598[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_429527558939684598[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_429527558939684598[20] = 0;
   out_429527558939684598[21] = 0;
   out_429527558939684598[22] = 0;
   out_429527558939684598[23] = 0;
   out_429527558939684598[24] = 0;
   out_429527558939684598[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_429527558939684598[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_429527558939684598[27] = 0;
   out_429527558939684598[28] = 0;
   out_429527558939684598[29] = 0;
   out_429527558939684598[30] = 0;
   out_429527558939684598[31] = 0;
   out_429527558939684598[32] = 0;
   out_429527558939684598[33] = 0;
   out_429527558939684598[34] = 0;
   out_429527558939684598[35] = 0;
   out_429527558939684598[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_429527558939684598[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_429527558939684598[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_429527558939684598[39] = 0;
   out_429527558939684598[40] = 0;
   out_429527558939684598[41] = 0;
   out_429527558939684598[42] = 0;
   out_429527558939684598[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_429527558939684598[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_429527558939684598[45] = 0;
   out_429527558939684598[46] = 0;
   out_429527558939684598[47] = 0;
   out_429527558939684598[48] = 0;
   out_429527558939684598[49] = 0;
   out_429527558939684598[50] = 0;
   out_429527558939684598[51] = 0;
   out_429527558939684598[52] = 0;
   out_429527558939684598[53] = 0;
   out_429527558939684598[54] = 0;
   out_429527558939684598[55] = 0;
   out_429527558939684598[56] = 0;
   out_429527558939684598[57] = 1;
   out_429527558939684598[58] = 0;
   out_429527558939684598[59] = 0;
   out_429527558939684598[60] = 0;
   out_429527558939684598[61] = 0;
   out_429527558939684598[62] = 0;
   out_429527558939684598[63] = 0;
   out_429527558939684598[64] = 0;
   out_429527558939684598[65] = 0;
   out_429527558939684598[66] = dt;
   out_429527558939684598[67] = 0;
   out_429527558939684598[68] = 0;
   out_429527558939684598[69] = 0;
   out_429527558939684598[70] = 0;
   out_429527558939684598[71] = 0;
   out_429527558939684598[72] = 0;
   out_429527558939684598[73] = 0;
   out_429527558939684598[74] = 0;
   out_429527558939684598[75] = 0;
   out_429527558939684598[76] = 1;
   out_429527558939684598[77] = 0;
   out_429527558939684598[78] = 0;
   out_429527558939684598[79] = 0;
   out_429527558939684598[80] = 0;
   out_429527558939684598[81] = 0;
   out_429527558939684598[82] = 0;
   out_429527558939684598[83] = 0;
   out_429527558939684598[84] = 0;
   out_429527558939684598[85] = dt;
   out_429527558939684598[86] = 0;
   out_429527558939684598[87] = 0;
   out_429527558939684598[88] = 0;
   out_429527558939684598[89] = 0;
   out_429527558939684598[90] = 0;
   out_429527558939684598[91] = 0;
   out_429527558939684598[92] = 0;
   out_429527558939684598[93] = 0;
   out_429527558939684598[94] = 0;
   out_429527558939684598[95] = 1;
   out_429527558939684598[96] = 0;
   out_429527558939684598[97] = 0;
   out_429527558939684598[98] = 0;
   out_429527558939684598[99] = 0;
   out_429527558939684598[100] = 0;
   out_429527558939684598[101] = 0;
   out_429527558939684598[102] = 0;
   out_429527558939684598[103] = 0;
   out_429527558939684598[104] = dt;
   out_429527558939684598[105] = 0;
   out_429527558939684598[106] = 0;
   out_429527558939684598[107] = 0;
   out_429527558939684598[108] = 0;
   out_429527558939684598[109] = 0;
   out_429527558939684598[110] = 0;
   out_429527558939684598[111] = 0;
   out_429527558939684598[112] = 0;
   out_429527558939684598[113] = 0;
   out_429527558939684598[114] = 1;
   out_429527558939684598[115] = 0;
   out_429527558939684598[116] = 0;
   out_429527558939684598[117] = 0;
   out_429527558939684598[118] = 0;
   out_429527558939684598[119] = 0;
   out_429527558939684598[120] = 0;
   out_429527558939684598[121] = 0;
   out_429527558939684598[122] = 0;
   out_429527558939684598[123] = 0;
   out_429527558939684598[124] = 0;
   out_429527558939684598[125] = 0;
   out_429527558939684598[126] = 0;
   out_429527558939684598[127] = 0;
   out_429527558939684598[128] = 0;
   out_429527558939684598[129] = 0;
   out_429527558939684598[130] = 0;
   out_429527558939684598[131] = 0;
   out_429527558939684598[132] = 0;
   out_429527558939684598[133] = 1;
   out_429527558939684598[134] = 0;
   out_429527558939684598[135] = 0;
   out_429527558939684598[136] = 0;
   out_429527558939684598[137] = 0;
   out_429527558939684598[138] = 0;
   out_429527558939684598[139] = 0;
   out_429527558939684598[140] = 0;
   out_429527558939684598[141] = 0;
   out_429527558939684598[142] = 0;
   out_429527558939684598[143] = 0;
   out_429527558939684598[144] = 0;
   out_429527558939684598[145] = 0;
   out_429527558939684598[146] = 0;
   out_429527558939684598[147] = 0;
   out_429527558939684598[148] = 0;
   out_429527558939684598[149] = 0;
   out_429527558939684598[150] = 0;
   out_429527558939684598[151] = 0;
   out_429527558939684598[152] = 1;
   out_429527558939684598[153] = 0;
   out_429527558939684598[154] = 0;
   out_429527558939684598[155] = 0;
   out_429527558939684598[156] = 0;
   out_429527558939684598[157] = 0;
   out_429527558939684598[158] = 0;
   out_429527558939684598[159] = 0;
   out_429527558939684598[160] = 0;
   out_429527558939684598[161] = 0;
   out_429527558939684598[162] = 0;
   out_429527558939684598[163] = 0;
   out_429527558939684598[164] = 0;
   out_429527558939684598[165] = 0;
   out_429527558939684598[166] = 0;
   out_429527558939684598[167] = 0;
   out_429527558939684598[168] = 0;
   out_429527558939684598[169] = 0;
   out_429527558939684598[170] = 0;
   out_429527558939684598[171] = 1;
   out_429527558939684598[172] = 0;
   out_429527558939684598[173] = 0;
   out_429527558939684598[174] = 0;
   out_429527558939684598[175] = 0;
   out_429527558939684598[176] = 0;
   out_429527558939684598[177] = 0;
   out_429527558939684598[178] = 0;
   out_429527558939684598[179] = 0;
   out_429527558939684598[180] = 0;
   out_429527558939684598[181] = 0;
   out_429527558939684598[182] = 0;
   out_429527558939684598[183] = 0;
   out_429527558939684598[184] = 0;
   out_429527558939684598[185] = 0;
   out_429527558939684598[186] = 0;
   out_429527558939684598[187] = 0;
   out_429527558939684598[188] = 0;
   out_429527558939684598[189] = 0;
   out_429527558939684598[190] = 1;
   out_429527558939684598[191] = 0;
   out_429527558939684598[192] = 0;
   out_429527558939684598[193] = 0;
   out_429527558939684598[194] = 0;
   out_429527558939684598[195] = 0;
   out_429527558939684598[196] = 0;
   out_429527558939684598[197] = 0;
   out_429527558939684598[198] = 0;
   out_429527558939684598[199] = 0;
   out_429527558939684598[200] = 0;
   out_429527558939684598[201] = 0;
   out_429527558939684598[202] = 0;
   out_429527558939684598[203] = 0;
   out_429527558939684598[204] = 0;
   out_429527558939684598[205] = 0;
   out_429527558939684598[206] = 0;
   out_429527558939684598[207] = 0;
   out_429527558939684598[208] = 0;
   out_429527558939684598[209] = 1;
   out_429527558939684598[210] = 0;
   out_429527558939684598[211] = 0;
   out_429527558939684598[212] = 0;
   out_429527558939684598[213] = 0;
   out_429527558939684598[214] = 0;
   out_429527558939684598[215] = 0;
   out_429527558939684598[216] = 0;
   out_429527558939684598[217] = 0;
   out_429527558939684598[218] = 0;
   out_429527558939684598[219] = 0;
   out_429527558939684598[220] = 0;
   out_429527558939684598[221] = 0;
   out_429527558939684598[222] = 0;
   out_429527558939684598[223] = 0;
   out_429527558939684598[224] = 0;
   out_429527558939684598[225] = 0;
   out_429527558939684598[226] = 0;
   out_429527558939684598[227] = 0;
   out_429527558939684598[228] = 1;
   out_429527558939684598[229] = 0;
   out_429527558939684598[230] = 0;
   out_429527558939684598[231] = 0;
   out_429527558939684598[232] = 0;
   out_429527558939684598[233] = 0;
   out_429527558939684598[234] = 0;
   out_429527558939684598[235] = 0;
   out_429527558939684598[236] = 0;
   out_429527558939684598[237] = 0;
   out_429527558939684598[238] = 0;
   out_429527558939684598[239] = 0;
   out_429527558939684598[240] = 0;
   out_429527558939684598[241] = 0;
   out_429527558939684598[242] = 0;
   out_429527558939684598[243] = 0;
   out_429527558939684598[244] = 0;
   out_429527558939684598[245] = 0;
   out_429527558939684598[246] = 0;
   out_429527558939684598[247] = 1;
   out_429527558939684598[248] = 0;
   out_429527558939684598[249] = 0;
   out_429527558939684598[250] = 0;
   out_429527558939684598[251] = 0;
   out_429527558939684598[252] = 0;
   out_429527558939684598[253] = 0;
   out_429527558939684598[254] = 0;
   out_429527558939684598[255] = 0;
   out_429527558939684598[256] = 0;
   out_429527558939684598[257] = 0;
   out_429527558939684598[258] = 0;
   out_429527558939684598[259] = 0;
   out_429527558939684598[260] = 0;
   out_429527558939684598[261] = 0;
   out_429527558939684598[262] = 0;
   out_429527558939684598[263] = 0;
   out_429527558939684598[264] = 0;
   out_429527558939684598[265] = 0;
   out_429527558939684598[266] = 1;
   out_429527558939684598[267] = 0;
   out_429527558939684598[268] = 0;
   out_429527558939684598[269] = 0;
   out_429527558939684598[270] = 0;
   out_429527558939684598[271] = 0;
   out_429527558939684598[272] = 0;
   out_429527558939684598[273] = 0;
   out_429527558939684598[274] = 0;
   out_429527558939684598[275] = 0;
   out_429527558939684598[276] = 0;
   out_429527558939684598[277] = 0;
   out_429527558939684598[278] = 0;
   out_429527558939684598[279] = 0;
   out_429527558939684598[280] = 0;
   out_429527558939684598[281] = 0;
   out_429527558939684598[282] = 0;
   out_429527558939684598[283] = 0;
   out_429527558939684598[284] = 0;
   out_429527558939684598[285] = 1;
   out_429527558939684598[286] = 0;
   out_429527558939684598[287] = 0;
   out_429527558939684598[288] = 0;
   out_429527558939684598[289] = 0;
   out_429527558939684598[290] = 0;
   out_429527558939684598[291] = 0;
   out_429527558939684598[292] = 0;
   out_429527558939684598[293] = 0;
   out_429527558939684598[294] = 0;
   out_429527558939684598[295] = 0;
   out_429527558939684598[296] = 0;
   out_429527558939684598[297] = 0;
   out_429527558939684598[298] = 0;
   out_429527558939684598[299] = 0;
   out_429527558939684598[300] = 0;
   out_429527558939684598[301] = 0;
   out_429527558939684598[302] = 0;
   out_429527558939684598[303] = 0;
   out_429527558939684598[304] = 1;
   out_429527558939684598[305] = 0;
   out_429527558939684598[306] = 0;
   out_429527558939684598[307] = 0;
   out_429527558939684598[308] = 0;
   out_429527558939684598[309] = 0;
   out_429527558939684598[310] = 0;
   out_429527558939684598[311] = 0;
   out_429527558939684598[312] = 0;
   out_429527558939684598[313] = 0;
   out_429527558939684598[314] = 0;
   out_429527558939684598[315] = 0;
   out_429527558939684598[316] = 0;
   out_429527558939684598[317] = 0;
   out_429527558939684598[318] = 0;
   out_429527558939684598[319] = 0;
   out_429527558939684598[320] = 0;
   out_429527558939684598[321] = 0;
   out_429527558939684598[322] = 0;
   out_429527558939684598[323] = 1;
}
void h_4(double *state, double *unused, double *out_7652981531568014253) {
   out_7652981531568014253[0] = state[6] + state[9];
   out_7652981531568014253[1] = state[7] + state[10];
   out_7652981531568014253[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_3195424610112428848) {
   out_3195424610112428848[0] = 0;
   out_3195424610112428848[1] = 0;
   out_3195424610112428848[2] = 0;
   out_3195424610112428848[3] = 0;
   out_3195424610112428848[4] = 0;
   out_3195424610112428848[5] = 0;
   out_3195424610112428848[6] = 1;
   out_3195424610112428848[7] = 0;
   out_3195424610112428848[8] = 0;
   out_3195424610112428848[9] = 1;
   out_3195424610112428848[10] = 0;
   out_3195424610112428848[11] = 0;
   out_3195424610112428848[12] = 0;
   out_3195424610112428848[13] = 0;
   out_3195424610112428848[14] = 0;
   out_3195424610112428848[15] = 0;
   out_3195424610112428848[16] = 0;
   out_3195424610112428848[17] = 0;
   out_3195424610112428848[18] = 0;
   out_3195424610112428848[19] = 0;
   out_3195424610112428848[20] = 0;
   out_3195424610112428848[21] = 0;
   out_3195424610112428848[22] = 0;
   out_3195424610112428848[23] = 0;
   out_3195424610112428848[24] = 0;
   out_3195424610112428848[25] = 1;
   out_3195424610112428848[26] = 0;
   out_3195424610112428848[27] = 0;
   out_3195424610112428848[28] = 1;
   out_3195424610112428848[29] = 0;
   out_3195424610112428848[30] = 0;
   out_3195424610112428848[31] = 0;
   out_3195424610112428848[32] = 0;
   out_3195424610112428848[33] = 0;
   out_3195424610112428848[34] = 0;
   out_3195424610112428848[35] = 0;
   out_3195424610112428848[36] = 0;
   out_3195424610112428848[37] = 0;
   out_3195424610112428848[38] = 0;
   out_3195424610112428848[39] = 0;
   out_3195424610112428848[40] = 0;
   out_3195424610112428848[41] = 0;
   out_3195424610112428848[42] = 0;
   out_3195424610112428848[43] = 0;
   out_3195424610112428848[44] = 1;
   out_3195424610112428848[45] = 0;
   out_3195424610112428848[46] = 0;
   out_3195424610112428848[47] = 1;
   out_3195424610112428848[48] = 0;
   out_3195424610112428848[49] = 0;
   out_3195424610112428848[50] = 0;
   out_3195424610112428848[51] = 0;
   out_3195424610112428848[52] = 0;
   out_3195424610112428848[53] = 0;
}
void h_10(double *state, double *unused, double *out_6006750715563175580) {
   out_6006750715563175580[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_6006750715563175580[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_6006750715563175580[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_7894245787152231876) {
   out_7894245787152231876[0] = 0;
   out_7894245787152231876[1] = 9.8100000000000005*cos(state[1]);
   out_7894245787152231876[2] = 0;
   out_7894245787152231876[3] = 0;
   out_7894245787152231876[4] = -state[8];
   out_7894245787152231876[5] = state[7];
   out_7894245787152231876[6] = 0;
   out_7894245787152231876[7] = state[5];
   out_7894245787152231876[8] = -state[4];
   out_7894245787152231876[9] = 0;
   out_7894245787152231876[10] = 0;
   out_7894245787152231876[11] = 0;
   out_7894245787152231876[12] = 1;
   out_7894245787152231876[13] = 0;
   out_7894245787152231876[14] = 0;
   out_7894245787152231876[15] = 1;
   out_7894245787152231876[16] = 0;
   out_7894245787152231876[17] = 0;
   out_7894245787152231876[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_7894245787152231876[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_7894245787152231876[20] = 0;
   out_7894245787152231876[21] = state[8];
   out_7894245787152231876[22] = 0;
   out_7894245787152231876[23] = -state[6];
   out_7894245787152231876[24] = -state[5];
   out_7894245787152231876[25] = 0;
   out_7894245787152231876[26] = state[3];
   out_7894245787152231876[27] = 0;
   out_7894245787152231876[28] = 0;
   out_7894245787152231876[29] = 0;
   out_7894245787152231876[30] = 0;
   out_7894245787152231876[31] = 1;
   out_7894245787152231876[32] = 0;
   out_7894245787152231876[33] = 0;
   out_7894245787152231876[34] = 1;
   out_7894245787152231876[35] = 0;
   out_7894245787152231876[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_7894245787152231876[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_7894245787152231876[38] = 0;
   out_7894245787152231876[39] = -state[7];
   out_7894245787152231876[40] = state[6];
   out_7894245787152231876[41] = 0;
   out_7894245787152231876[42] = state[4];
   out_7894245787152231876[43] = -state[3];
   out_7894245787152231876[44] = 0;
   out_7894245787152231876[45] = 0;
   out_7894245787152231876[46] = 0;
   out_7894245787152231876[47] = 0;
   out_7894245787152231876[48] = 0;
   out_7894245787152231876[49] = 0;
   out_7894245787152231876[50] = 1;
   out_7894245787152231876[51] = 0;
   out_7894245787152231876[52] = 0;
   out_7894245787152231876[53] = 1;
}
void h_13(double *state, double *unused, double *out_8907628765272580202) {
   out_8907628765272580202[0] = state[3];
   out_8907628765272580202[1] = state[4];
   out_8907628765272580202[2] = state[5];
}
void H_13(double *state, double *unused, double *out_7640688255280421839) {
   out_7640688255280421839[0] = 0;
   out_7640688255280421839[1] = 0;
   out_7640688255280421839[2] = 0;
   out_7640688255280421839[3] = 1;
   out_7640688255280421839[4] = 0;
   out_7640688255280421839[5] = 0;
   out_7640688255280421839[6] = 0;
   out_7640688255280421839[7] = 0;
   out_7640688255280421839[8] = 0;
   out_7640688255280421839[9] = 0;
   out_7640688255280421839[10] = 0;
   out_7640688255280421839[11] = 0;
   out_7640688255280421839[12] = 0;
   out_7640688255280421839[13] = 0;
   out_7640688255280421839[14] = 0;
   out_7640688255280421839[15] = 0;
   out_7640688255280421839[16] = 0;
   out_7640688255280421839[17] = 0;
   out_7640688255280421839[18] = 0;
   out_7640688255280421839[19] = 0;
   out_7640688255280421839[20] = 0;
   out_7640688255280421839[21] = 0;
   out_7640688255280421839[22] = 1;
   out_7640688255280421839[23] = 0;
   out_7640688255280421839[24] = 0;
   out_7640688255280421839[25] = 0;
   out_7640688255280421839[26] = 0;
   out_7640688255280421839[27] = 0;
   out_7640688255280421839[28] = 0;
   out_7640688255280421839[29] = 0;
   out_7640688255280421839[30] = 0;
   out_7640688255280421839[31] = 0;
   out_7640688255280421839[32] = 0;
   out_7640688255280421839[33] = 0;
   out_7640688255280421839[34] = 0;
   out_7640688255280421839[35] = 0;
   out_7640688255280421839[36] = 0;
   out_7640688255280421839[37] = 0;
   out_7640688255280421839[38] = 0;
   out_7640688255280421839[39] = 0;
   out_7640688255280421839[40] = 0;
   out_7640688255280421839[41] = 1;
   out_7640688255280421839[42] = 0;
   out_7640688255280421839[43] = 0;
   out_7640688255280421839[44] = 0;
   out_7640688255280421839[45] = 0;
   out_7640688255280421839[46] = 0;
   out_7640688255280421839[47] = 0;
   out_7640688255280421839[48] = 0;
   out_7640688255280421839[49] = 0;
   out_7640688255280421839[50] = 0;
   out_7640688255280421839[51] = 0;
   out_7640688255280421839[52] = 0;
   out_7640688255280421839[53] = 0;
}
void h_14(double *state, double *unused, double *out_3516354322614119174) {
   out_3516354322614119174[0] = state[6];
   out_3516354322614119174[1] = state[7];
   out_3516354322614119174[2] = state[8];
}
void H_14(double *state, double *unused, double *out_7158665466451913377) {
   out_7158665466451913377[0] = 0;
   out_7158665466451913377[1] = 0;
   out_7158665466451913377[2] = 0;
   out_7158665466451913377[3] = 0;
   out_7158665466451913377[4] = 0;
   out_7158665466451913377[5] = 0;
   out_7158665466451913377[6] = 1;
   out_7158665466451913377[7] = 0;
   out_7158665466451913377[8] = 0;
   out_7158665466451913377[9] = 0;
   out_7158665466451913377[10] = 0;
   out_7158665466451913377[11] = 0;
   out_7158665466451913377[12] = 0;
   out_7158665466451913377[13] = 0;
   out_7158665466451913377[14] = 0;
   out_7158665466451913377[15] = 0;
   out_7158665466451913377[16] = 0;
   out_7158665466451913377[17] = 0;
   out_7158665466451913377[18] = 0;
   out_7158665466451913377[19] = 0;
   out_7158665466451913377[20] = 0;
   out_7158665466451913377[21] = 0;
   out_7158665466451913377[22] = 0;
   out_7158665466451913377[23] = 0;
   out_7158665466451913377[24] = 0;
   out_7158665466451913377[25] = 1;
   out_7158665466451913377[26] = 0;
   out_7158665466451913377[27] = 0;
   out_7158665466451913377[28] = 0;
   out_7158665466451913377[29] = 0;
   out_7158665466451913377[30] = 0;
   out_7158665466451913377[31] = 0;
   out_7158665466451913377[32] = 0;
   out_7158665466451913377[33] = 0;
   out_7158665466451913377[34] = 0;
   out_7158665466451913377[35] = 0;
   out_7158665466451913377[36] = 0;
   out_7158665466451913377[37] = 0;
   out_7158665466451913377[38] = 0;
   out_7158665466451913377[39] = 0;
   out_7158665466451913377[40] = 0;
   out_7158665466451913377[41] = 0;
   out_7158665466451913377[42] = 0;
   out_7158665466451913377[43] = 0;
   out_7158665466451913377[44] = 1;
   out_7158665466451913377[45] = 0;
   out_7158665466451913377[46] = 0;
   out_7158665466451913377[47] = 0;
   out_7158665466451913377[48] = 0;
   out_7158665466451913377[49] = 0;
   out_7158665466451913377[50] = 0;
   out_7158665466451913377[51] = 0;
   out_7158665466451913377[52] = 0;
   out_7158665466451913377[53] = 0;
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
void pose_err_fun(double *nom_x, double *delta_x, double *out_1387667857402197864) {
  err_fun(nom_x, delta_x, out_1387667857402197864);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_7508820603663648737) {
  inv_err_fun(nom_x, true_x, out_7508820603663648737);
}
void pose_H_mod_fun(double *state, double *out_6469646688903378101) {
  H_mod_fun(state, out_6469646688903378101);
}
void pose_f_fun(double *state, double dt, double *out_6697963188238977834) {
  f_fun(state,  dt, out_6697963188238977834);
}
void pose_F_fun(double *state, double dt, double *out_429527558939684598) {
  F_fun(state,  dt, out_429527558939684598);
}
void pose_h_4(double *state, double *unused, double *out_7652981531568014253) {
  h_4(state, unused, out_7652981531568014253);
}
void pose_H_4(double *state, double *unused, double *out_3195424610112428848) {
  H_4(state, unused, out_3195424610112428848);
}
void pose_h_10(double *state, double *unused, double *out_6006750715563175580) {
  h_10(state, unused, out_6006750715563175580);
}
void pose_H_10(double *state, double *unused, double *out_7894245787152231876) {
  H_10(state, unused, out_7894245787152231876);
}
void pose_h_13(double *state, double *unused, double *out_8907628765272580202) {
  h_13(state, unused, out_8907628765272580202);
}
void pose_H_13(double *state, double *unused, double *out_7640688255280421839) {
  H_13(state, unused, out_7640688255280421839);
}
void pose_h_14(double *state, double *unused, double *out_3516354322614119174) {
  h_14(state, unused, out_3516354322614119174);
}
void pose_H_14(double *state, double *unused, double *out_7158665466451913377) {
  H_14(state, unused, out_7158665466451913377);
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
