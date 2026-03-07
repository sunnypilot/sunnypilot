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
void err_fun(double *nom_x, double *delta_x, double *out_8941250306396925607) {
   out_8941250306396925607[0] = delta_x[0] + nom_x[0];
   out_8941250306396925607[1] = delta_x[1] + nom_x[1];
   out_8941250306396925607[2] = delta_x[2] + nom_x[2];
   out_8941250306396925607[3] = delta_x[3] + nom_x[3];
   out_8941250306396925607[4] = delta_x[4] + nom_x[4];
   out_8941250306396925607[5] = delta_x[5] + nom_x[5];
   out_8941250306396925607[6] = delta_x[6] + nom_x[6];
   out_8941250306396925607[7] = delta_x[7] + nom_x[7];
   out_8941250306396925607[8] = delta_x[8] + nom_x[8];
   out_8941250306396925607[9] = delta_x[9] + nom_x[9];
   out_8941250306396925607[10] = delta_x[10] + nom_x[10];
   out_8941250306396925607[11] = delta_x[11] + nom_x[11];
   out_8941250306396925607[12] = delta_x[12] + nom_x[12];
   out_8941250306396925607[13] = delta_x[13] + nom_x[13];
   out_8941250306396925607[14] = delta_x[14] + nom_x[14];
   out_8941250306396925607[15] = delta_x[15] + nom_x[15];
   out_8941250306396925607[16] = delta_x[16] + nom_x[16];
   out_8941250306396925607[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_7188163769114424214) {
   out_7188163769114424214[0] = -nom_x[0] + true_x[0];
   out_7188163769114424214[1] = -nom_x[1] + true_x[1];
   out_7188163769114424214[2] = -nom_x[2] + true_x[2];
   out_7188163769114424214[3] = -nom_x[3] + true_x[3];
   out_7188163769114424214[4] = -nom_x[4] + true_x[4];
   out_7188163769114424214[5] = -nom_x[5] + true_x[5];
   out_7188163769114424214[6] = -nom_x[6] + true_x[6];
   out_7188163769114424214[7] = -nom_x[7] + true_x[7];
   out_7188163769114424214[8] = -nom_x[8] + true_x[8];
   out_7188163769114424214[9] = -nom_x[9] + true_x[9];
   out_7188163769114424214[10] = -nom_x[10] + true_x[10];
   out_7188163769114424214[11] = -nom_x[11] + true_x[11];
   out_7188163769114424214[12] = -nom_x[12] + true_x[12];
   out_7188163769114424214[13] = -nom_x[13] + true_x[13];
   out_7188163769114424214[14] = -nom_x[14] + true_x[14];
   out_7188163769114424214[15] = -nom_x[15] + true_x[15];
   out_7188163769114424214[16] = -nom_x[16] + true_x[16];
   out_7188163769114424214[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_3126609761481196981) {
   out_3126609761481196981[0] = 1.0;
   out_3126609761481196981[1] = 0.0;
   out_3126609761481196981[2] = 0.0;
   out_3126609761481196981[3] = 0.0;
   out_3126609761481196981[4] = 0.0;
   out_3126609761481196981[5] = 0.0;
   out_3126609761481196981[6] = 0.0;
   out_3126609761481196981[7] = 0.0;
   out_3126609761481196981[8] = 0.0;
   out_3126609761481196981[9] = 0.0;
   out_3126609761481196981[10] = 0.0;
   out_3126609761481196981[11] = 0.0;
   out_3126609761481196981[12] = 0.0;
   out_3126609761481196981[13] = 0.0;
   out_3126609761481196981[14] = 0.0;
   out_3126609761481196981[15] = 0.0;
   out_3126609761481196981[16] = 0.0;
   out_3126609761481196981[17] = 0.0;
   out_3126609761481196981[18] = 0.0;
   out_3126609761481196981[19] = 1.0;
   out_3126609761481196981[20] = 0.0;
   out_3126609761481196981[21] = 0.0;
   out_3126609761481196981[22] = 0.0;
   out_3126609761481196981[23] = 0.0;
   out_3126609761481196981[24] = 0.0;
   out_3126609761481196981[25] = 0.0;
   out_3126609761481196981[26] = 0.0;
   out_3126609761481196981[27] = 0.0;
   out_3126609761481196981[28] = 0.0;
   out_3126609761481196981[29] = 0.0;
   out_3126609761481196981[30] = 0.0;
   out_3126609761481196981[31] = 0.0;
   out_3126609761481196981[32] = 0.0;
   out_3126609761481196981[33] = 0.0;
   out_3126609761481196981[34] = 0.0;
   out_3126609761481196981[35] = 0.0;
   out_3126609761481196981[36] = 0.0;
   out_3126609761481196981[37] = 0.0;
   out_3126609761481196981[38] = 1.0;
   out_3126609761481196981[39] = 0.0;
   out_3126609761481196981[40] = 0.0;
   out_3126609761481196981[41] = 0.0;
   out_3126609761481196981[42] = 0.0;
   out_3126609761481196981[43] = 0.0;
   out_3126609761481196981[44] = 0.0;
   out_3126609761481196981[45] = 0.0;
   out_3126609761481196981[46] = 0.0;
   out_3126609761481196981[47] = 0.0;
   out_3126609761481196981[48] = 0.0;
   out_3126609761481196981[49] = 0.0;
   out_3126609761481196981[50] = 0.0;
   out_3126609761481196981[51] = 0.0;
   out_3126609761481196981[52] = 0.0;
   out_3126609761481196981[53] = 0.0;
   out_3126609761481196981[54] = 0.0;
   out_3126609761481196981[55] = 0.0;
   out_3126609761481196981[56] = 0.0;
   out_3126609761481196981[57] = 1.0;
   out_3126609761481196981[58] = 0.0;
   out_3126609761481196981[59] = 0.0;
   out_3126609761481196981[60] = 0.0;
   out_3126609761481196981[61] = 0.0;
   out_3126609761481196981[62] = 0.0;
   out_3126609761481196981[63] = 0.0;
   out_3126609761481196981[64] = 0.0;
   out_3126609761481196981[65] = 0.0;
   out_3126609761481196981[66] = 0.0;
   out_3126609761481196981[67] = 0.0;
   out_3126609761481196981[68] = 0.0;
   out_3126609761481196981[69] = 0.0;
   out_3126609761481196981[70] = 0.0;
   out_3126609761481196981[71] = 0.0;
   out_3126609761481196981[72] = 0.0;
   out_3126609761481196981[73] = 0.0;
   out_3126609761481196981[74] = 0.0;
   out_3126609761481196981[75] = 0.0;
   out_3126609761481196981[76] = 1.0;
   out_3126609761481196981[77] = 0.0;
   out_3126609761481196981[78] = 0.0;
   out_3126609761481196981[79] = 0.0;
   out_3126609761481196981[80] = 0.0;
   out_3126609761481196981[81] = 0.0;
   out_3126609761481196981[82] = 0.0;
   out_3126609761481196981[83] = 0.0;
   out_3126609761481196981[84] = 0.0;
   out_3126609761481196981[85] = 0.0;
   out_3126609761481196981[86] = 0.0;
   out_3126609761481196981[87] = 0.0;
   out_3126609761481196981[88] = 0.0;
   out_3126609761481196981[89] = 0.0;
   out_3126609761481196981[90] = 0.0;
   out_3126609761481196981[91] = 0.0;
   out_3126609761481196981[92] = 0.0;
   out_3126609761481196981[93] = 0.0;
   out_3126609761481196981[94] = 0.0;
   out_3126609761481196981[95] = 1.0;
   out_3126609761481196981[96] = 0.0;
   out_3126609761481196981[97] = 0.0;
   out_3126609761481196981[98] = 0.0;
   out_3126609761481196981[99] = 0.0;
   out_3126609761481196981[100] = 0.0;
   out_3126609761481196981[101] = 0.0;
   out_3126609761481196981[102] = 0.0;
   out_3126609761481196981[103] = 0.0;
   out_3126609761481196981[104] = 0.0;
   out_3126609761481196981[105] = 0.0;
   out_3126609761481196981[106] = 0.0;
   out_3126609761481196981[107] = 0.0;
   out_3126609761481196981[108] = 0.0;
   out_3126609761481196981[109] = 0.0;
   out_3126609761481196981[110] = 0.0;
   out_3126609761481196981[111] = 0.0;
   out_3126609761481196981[112] = 0.0;
   out_3126609761481196981[113] = 0.0;
   out_3126609761481196981[114] = 1.0;
   out_3126609761481196981[115] = 0.0;
   out_3126609761481196981[116] = 0.0;
   out_3126609761481196981[117] = 0.0;
   out_3126609761481196981[118] = 0.0;
   out_3126609761481196981[119] = 0.0;
   out_3126609761481196981[120] = 0.0;
   out_3126609761481196981[121] = 0.0;
   out_3126609761481196981[122] = 0.0;
   out_3126609761481196981[123] = 0.0;
   out_3126609761481196981[124] = 0.0;
   out_3126609761481196981[125] = 0.0;
   out_3126609761481196981[126] = 0.0;
   out_3126609761481196981[127] = 0.0;
   out_3126609761481196981[128] = 0.0;
   out_3126609761481196981[129] = 0.0;
   out_3126609761481196981[130] = 0.0;
   out_3126609761481196981[131] = 0.0;
   out_3126609761481196981[132] = 0.0;
   out_3126609761481196981[133] = 1.0;
   out_3126609761481196981[134] = 0.0;
   out_3126609761481196981[135] = 0.0;
   out_3126609761481196981[136] = 0.0;
   out_3126609761481196981[137] = 0.0;
   out_3126609761481196981[138] = 0.0;
   out_3126609761481196981[139] = 0.0;
   out_3126609761481196981[140] = 0.0;
   out_3126609761481196981[141] = 0.0;
   out_3126609761481196981[142] = 0.0;
   out_3126609761481196981[143] = 0.0;
   out_3126609761481196981[144] = 0.0;
   out_3126609761481196981[145] = 0.0;
   out_3126609761481196981[146] = 0.0;
   out_3126609761481196981[147] = 0.0;
   out_3126609761481196981[148] = 0.0;
   out_3126609761481196981[149] = 0.0;
   out_3126609761481196981[150] = 0.0;
   out_3126609761481196981[151] = 0.0;
   out_3126609761481196981[152] = 1.0;
   out_3126609761481196981[153] = 0.0;
   out_3126609761481196981[154] = 0.0;
   out_3126609761481196981[155] = 0.0;
   out_3126609761481196981[156] = 0.0;
   out_3126609761481196981[157] = 0.0;
   out_3126609761481196981[158] = 0.0;
   out_3126609761481196981[159] = 0.0;
   out_3126609761481196981[160] = 0.0;
   out_3126609761481196981[161] = 0.0;
   out_3126609761481196981[162] = 0.0;
   out_3126609761481196981[163] = 0.0;
   out_3126609761481196981[164] = 0.0;
   out_3126609761481196981[165] = 0.0;
   out_3126609761481196981[166] = 0.0;
   out_3126609761481196981[167] = 0.0;
   out_3126609761481196981[168] = 0.0;
   out_3126609761481196981[169] = 0.0;
   out_3126609761481196981[170] = 0.0;
   out_3126609761481196981[171] = 1.0;
   out_3126609761481196981[172] = 0.0;
   out_3126609761481196981[173] = 0.0;
   out_3126609761481196981[174] = 0.0;
   out_3126609761481196981[175] = 0.0;
   out_3126609761481196981[176] = 0.0;
   out_3126609761481196981[177] = 0.0;
   out_3126609761481196981[178] = 0.0;
   out_3126609761481196981[179] = 0.0;
   out_3126609761481196981[180] = 0.0;
   out_3126609761481196981[181] = 0.0;
   out_3126609761481196981[182] = 0.0;
   out_3126609761481196981[183] = 0.0;
   out_3126609761481196981[184] = 0.0;
   out_3126609761481196981[185] = 0.0;
   out_3126609761481196981[186] = 0.0;
   out_3126609761481196981[187] = 0.0;
   out_3126609761481196981[188] = 0.0;
   out_3126609761481196981[189] = 0.0;
   out_3126609761481196981[190] = 1.0;
   out_3126609761481196981[191] = 0.0;
   out_3126609761481196981[192] = 0.0;
   out_3126609761481196981[193] = 0.0;
   out_3126609761481196981[194] = 0.0;
   out_3126609761481196981[195] = 0.0;
   out_3126609761481196981[196] = 0.0;
   out_3126609761481196981[197] = 0.0;
   out_3126609761481196981[198] = 0.0;
   out_3126609761481196981[199] = 0.0;
   out_3126609761481196981[200] = 0.0;
   out_3126609761481196981[201] = 0.0;
   out_3126609761481196981[202] = 0.0;
   out_3126609761481196981[203] = 0.0;
   out_3126609761481196981[204] = 0.0;
   out_3126609761481196981[205] = 0.0;
   out_3126609761481196981[206] = 0.0;
   out_3126609761481196981[207] = 0.0;
   out_3126609761481196981[208] = 0.0;
   out_3126609761481196981[209] = 1.0;
   out_3126609761481196981[210] = 0.0;
   out_3126609761481196981[211] = 0.0;
   out_3126609761481196981[212] = 0.0;
   out_3126609761481196981[213] = 0.0;
   out_3126609761481196981[214] = 0.0;
   out_3126609761481196981[215] = 0.0;
   out_3126609761481196981[216] = 0.0;
   out_3126609761481196981[217] = 0.0;
   out_3126609761481196981[218] = 0.0;
   out_3126609761481196981[219] = 0.0;
   out_3126609761481196981[220] = 0.0;
   out_3126609761481196981[221] = 0.0;
   out_3126609761481196981[222] = 0.0;
   out_3126609761481196981[223] = 0.0;
   out_3126609761481196981[224] = 0.0;
   out_3126609761481196981[225] = 0.0;
   out_3126609761481196981[226] = 0.0;
   out_3126609761481196981[227] = 0.0;
   out_3126609761481196981[228] = 1.0;
   out_3126609761481196981[229] = 0.0;
   out_3126609761481196981[230] = 0.0;
   out_3126609761481196981[231] = 0.0;
   out_3126609761481196981[232] = 0.0;
   out_3126609761481196981[233] = 0.0;
   out_3126609761481196981[234] = 0.0;
   out_3126609761481196981[235] = 0.0;
   out_3126609761481196981[236] = 0.0;
   out_3126609761481196981[237] = 0.0;
   out_3126609761481196981[238] = 0.0;
   out_3126609761481196981[239] = 0.0;
   out_3126609761481196981[240] = 0.0;
   out_3126609761481196981[241] = 0.0;
   out_3126609761481196981[242] = 0.0;
   out_3126609761481196981[243] = 0.0;
   out_3126609761481196981[244] = 0.0;
   out_3126609761481196981[245] = 0.0;
   out_3126609761481196981[246] = 0.0;
   out_3126609761481196981[247] = 1.0;
   out_3126609761481196981[248] = 0.0;
   out_3126609761481196981[249] = 0.0;
   out_3126609761481196981[250] = 0.0;
   out_3126609761481196981[251] = 0.0;
   out_3126609761481196981[252] = 0.0;
   out_3126609761481196981[253] = 0.0;
   out_3126609761481196981[254] = 0.0;
   out_3126609761481196981[255] = 0.0;
   out_3126609761481196981[256] = 0.0;
   out_3126609761481196981[257] = 0.0;
   out_3126609761481196981[258] = 0.0;
   out_3126609761481196981[259] = 0.0;
   out_3126609761481196981[260] = 0.0;
   out_3126609761481196981[261] = 0.0;
   out_3126609761481196981[262] = 0.0;
   out_3126609761481196981[263] = 0.0;
   out_3126609761481196981[264] = 0.0;
   out_3126609761481196981[265] = 0.0;
   out_3126609761481196981[266] = 1.0;
   out_3126609761481196981[267] = 0.0;
   out_3126609761481196981[268] = 0.0;
   out_3126609761481196981[269] = 0.0;
   out_3126609761481196981[270] = 0.0;
   out_3126609761481196981[271] = 0.0;
   out_3126609761481196981[272] = 0.0;
   out_3126609761481196981[273] = 0.0;
   out_3126609761481196981[274] = 0.0;
   out_3126609761481196981[275] = 0.0;
   out_3126609761481196981[276] = 0.0;
   out_3126609761481196981[277] = 0.0;
   out_3126609761481196981[278] = 0.0;
   out_3126609761481196981[279] = 0.0;
   out_3126609761481196981[280] = 0.0;
   out_3126609761481196981[281] = 0.0;
   out_3126609761481196981[282] = 0.0;
   out_3126609761481196981[283] = 0.0;
   out_3126609761481196981[284] = 0.0;
   out_3126609761481196981[285] = 1.0;
   out_3126609761481196981[286] = 0.0;
   out_3126609761481196981[287] = 0.0;
   out_3126609761481196981[288] = 0.0;
   out_3126609761481196981[289] = 0.0;
   out_3126609761481196981[290] = 0.0;
   out_3126609761481196981[291] = 0.0;
   out_3126609761481196981[292] = 0.0;
   out_3126609761481196981[293] = 0.0;
   out_3126609761481196981[294] = 0.0;
   out_3126609761481196981[295] = 0.0;
   out_3126609761481196981[296] = 0.0;
   out_3126609761481196981[297] = 0.0;
   out_3126609761481196981[298] = 0.0;
   out_3126609761481196981[299] = 0.0;
   out_3126609761481196981[300] = 0.0;
   out_3126609761481196981[301] = 0.0;
   out_3126609761481196981[302] = 0.0;
   out_3126609761481196981[303] = 0.0;
   out_3126609761481196981[304] = 1.0;
   out_3126609761481196981[305] = 0.0;
   out_3126609761481196981[306] = 0.0;
   out_3126609761481196981[307] = 0.0;
   out_3126609761481196981[308] = 0.0;
   out_3126609761481196981[309] = 0.0;
   out_3126609761481196981[310] = 0.0;
   out_3126609761481196981[311] = 0.0;
   out_3126609761481196981[312] = 0.0;
   out_3126609761481196981[313] = 0.0;
   out_3126609761481196981[314] = 0.0;
   out_3126609761481196981[315] = 0.0;
   out_3126609761481196981[316] = 0.0;
   out_3126609761481196981[317] = 0.0;
   out_3126609761481196981[318] = 0.0;
   out_3126609761481196981[319] = 0.0;
   out_3126609761481196981[320] = 0.0;
   out_3126609761481196981[321] = 0.0;
   out_3126609761481196981[322] = 0.0;
   out_3126609761481196981[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_7800799004538587322) {
   out_7800799004538587322[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_7800799004538587322[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_7800799004538587322[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_7800799004538587322[3] = dt*state[12] + state[3];
   out_7800799004538587322[4] = dt*state[13] + state[4];
   out_7800799004538587322[5] = dt*state[14] + state[5];
   out_7800799004538587322[6] = state[6];
   out_7800799004538587322[7] = state[7];
   out_7800799004538587322[8] = state[8];
   out_7800799004538587322[9] = state[9];
   out_7800799004538587322[10] = state[10];
   out_7800799004538587322[11] = state[11];
   out_7800799004538587322[12] = state[12];
   out_7800799004538587322[13] = state[13];
   out_7800799004538587322[14] = state[14];
   out_7800799004538587322[15] = state[15];
   out_7800799004538587322[16] = state[16];
   out_7800799004538587322[17] = state[17];
}
void F_fun(double *state, double dt, double *out_834843542473115764) {
   out_834843542473115764[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_834843542473115764[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_834843542473115764[2] = 0;
   out_834843542473115764[3] = 0;
   out_834843542473115764[4] = 0;
   out_834843542473115764[5] = 0;
   out_834843542473115764[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_834843542473115764[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_834843542473115764[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_834843542473115764[9] = 0;
   out_834843542473115764[10] = 0;
   out_834843542473115764[11] = 0;
   out_834843542473115764[12] = 0;
   out_834843542473115764[13] = 0;
   out_834843542473115764[14] = 0;
   out_834843542473115764[15] = 0;
   out_834843542473115764[16] = 0;
   out_834843542473115764[17] = 0;
   out_834843542473115764[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_834843542473115764[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_834843542473115764[20] = 0;
   out_834843542473115764[21] = 0;
   out_834843542473115764[22] = 0;
   out_834843542473115764[23] = 0;
   out_834843542473115764[24] = 0;
   out_834843542473115764[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_834843542473115764[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_834843542473115764[27] = 0;
   out_834843542473115764[28] = 0;
   out_834843542473115764[29] = 0;
   out_834843542473115764[30] = 0;
   out_834843542473115764[31] = 0;
   out_834843542473115764[32] = 0;
   out_834843542473115764[33] = 0;
   out_834843542473115764[34] = 0;
   out_834843542473115764[35] = 0;
   out_834843542473115764[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_834843542473115764[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_834843542473115764[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_834843542473115764[39] = 0;
   out_834843542473115764[40] = 0;
   out_834843542473115764[41] = 0;
   out_834843542473115764[42] = 0;
   out_834843542473115764[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_834843542473115764[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_834843542473115764[45] = 0;
   out_834843542473115764[46] = 0;
   out_834843542473115764[47] = 0;
   out_834843542473115764[48] = 0;
   out_834843542473115764[49] = 0;
   out_834843542473115764[50] = 0;
   out_834843542473115764[51] = 0;
   out_834843542473115764[52] = 0;
   out_834843542473115764[53] = 0;
   out_834843542473115764[54] = 0;
   out_834843542473115764[55] = 0;
   out_834843542473115764[56] = 0;
   out_834843542473115764[57] = 1;
   out_834843542473115764[58] = 0;
   out_834843542473115764[59] = 0;
   out_834843542473115764[60] = 0;
   out_834843542473115764[61] = 0;
   out_834843542473115764[62] = 0;
   out_834843542473115764[63] = 0;
   out_834843542473115764[64] = 0;
   out_834843542473115764[65] = 0;
   out_834843542473115764[66] = dt;
   out_834843542473115764[67] = 0;
   out_834843542473115764[68] = 0;
   out_834843542473115764[69] = 0;
   out_834843542473115764[70] = 0;
   out_834843542473115764[71] = 0;
   out_834843542473115764[72] = 0;
   out_834843542473115764[73] = 0;
   out_834843542473115764[74] = 0;
   out_834843542473115764[75] = 0;
   out_834843542473115764[76] = 1;
   out_834843542473115764[77] = 0;
   out_834843542473115764[78] = 0;
   out_834843542473115764[79] = 0;
   out_834843542473115764[80] = 0;
   out_834843542473115764[81] = 0;
   out_834843542473115764[82] = 0;
   out_834843542473115764[83] = 0;
   out_834843542473115764[84] = 0;
   out_834843542473115764[85] = dt;
   out_834843542473115764[86] = 0;
   out_834843542473115764[87] = 0;
   out_834843542473115764[88] = 0;
   out_834843542473115764[89] = 0;
   out_834843542473115764[90] = 0;
   out_834843542473115764[91] = 0;
   out_834843542473115764[92] = 0;
   out_834843542473115764[93] = 0;
   out_834843542473115764[94] = 0;
   out_834843542473115764[95] = 1;
   out_834843542473115764[96] = 0;
   out_834843542473115764[97] = 0;
   out_834843542473115764[98] = 0;
   out_834843542473115764[99] = 0;
   out_834843542473115764[100] = 0;
   out_834843542473115764[101] = 0;
   out_834843542473115764[102] = 0;
   out_834843542473115764[103] = 0;
   out_834843542473115764[104] = dt;
   out_834843542473115764[105] = 0;
   out_834843542473115764[106] = 0;
   out_834843542473115764[107] = 0;
   out_834843542473115764[108] = 0;
   out_834843542473115764[109] = 0;
   out_834843542473115764[110] = 0;
   out_834843542473115764[111] = 0;
   out_834843542473115764[112] = 0;
   out_834843542473115764[113] = 0;
   out_834843542473115764[114] = 1;
   out_834843542473115764[115] = 0;
   out_834843542473115764[116] = 0;
   out_834843542473115764[117] = 0;
   out_834843542473115764[118] = 0;
   out_834843542473115764[119] = 0;
   out_834843542473115764[120] = 0;
   out_834843542473115764[121] = 0;
   out_834843542473115764[122] = 0;
   out_834843542473115764[123] = 0;
   out_834843542473115764[124] = 0;
   out_834843542473115764[125] = 0;
   out_834843542473115764[126] = 0;
   out_834843542473115764[127] = 0;
   out_834843542473115764[128] = 0;
   out_834843542473115764[129] = 0;
   out_834843542473115764[130] = 0;
   out_834843542473115764[131] = 0;
   out_834843542473115764[132] = 0;
   out_834843542473115764[133] = 1;
   out_834843542473115764[134] = 0;
   out_834843542473115764[135] = 0;
   out_834843542473115764[136] = 0;
   out_834843542473115764[137] = 0;
   out_834843542473115764[138] = 0;
   out_834843542473115764[139] = 0;
   out_834843542473115764[140] = 0;
   out_834843542473115764[141] = 0;
   out_834843542473115764[142] = 0;
   out_834843542473115764[143] = 0;
   out_834843542473115764[144] = 0;
   out_834843542473115764[145] = 0;
   out_834843542473115764[146] = 0;
   out_834843542473115764[147] = 0;
   out_834843542473115764[148] = 0;
   out_834843542473115764[149] = 0;
   out_834843542473115764[150] = 0;
   out_834843542473115764[151] = 0;
   out_834843542473115764[152] = 1;
   out_834843542473115764[153] = 0;
   out_834843542473115764[154] = 0;
   out_834843542473115764[155] = 0;
   out_834843542473115764[156] = 0;
   out_834843542473115764[157] = 0;
   out_834843542473115764[158] = 0;
   out_834843542473115764[159] = 0;
   out_834843542473115764[160] = 0;
   out_834843542473115764[161] = 0;
   out_834843542473115764[162] = 0;
   out_834843542473115764[163] = 0;
   out_834843542473115764[164] = 0;
   out_834843542473115764[165] = 0;
   out_834843542473115764[166] = 0;
   out_834843542473115764[167] = 0;
   out_834843542473115764[168] = 0;
   out_834843542473115764[169] = 0;
   out_834843542473115764[170] = 0;
   out_834843542473115764[171] = 1;
   out_834843542473115764[172] = 0;
   out_834843542473115764[173] = 0;
   out_834843542473115764[174] = 0;
   out_834843542473115764[175] = 0;
   out_834843542473115764[176] = 0;
   out_834843542473115764[177] = 0;
   out_834843542473115764[178] = 0;
   out_834843542473115764[179] = 0;
   out_834843542473115764[180] = 0;
   out_834843542473115764[181] = 0;
   out_834843542473115764[182] = 0;
   out_834843542473115764[183] = 0;
   out_834843542473115764[184] = 0;
   out_834843542473115764[185] = 0;
   out_834843542473115764[186] = 0;
   out_834843542473115764[187] = 0;
   out_834843542473115764[188] = 0;
   out_834843542473115764[189] = 0;
   out_834843542473115764[190] = 1;
   out_834843542473115764[191] = 0;
   out_834843542473115764[192] = 0;
   out_834843542473115764[193] = 0;
   out_834843542473115764[194] = 0;
   out_834843542473115764[195] = 0;
   out_834843542473115764[196] = 0;
   out_834843542473115764[197] = 0;
   out_834843542473115764[198] = 0;
   out_834843542473115764[199] = 0;
   out_834843542473115764[200] = 0;
   out_834843542473115764[201] = 0;
   out_834843542473115764[202] = 0;
   out_834843542473115764[203] = 0;
   out_834843542473115764[204] = 0;
   out_834843542473115764[205] = 0;
   out_834843542473115764[206] = 0;
   out_834843542473115764[207] = 0;
   out_834843542473115764[208] = 0;
   out_834843542473115764[209] = 1;
   out_834843542473115764[210] = 0;
   out_834843542473115764[211] = 0;
   out_834843542473115764[212] = 0;
   out_834843542473115764[213] = 0;
   out_834843542473115764[214] = 0;
   out_834843542473115764[215] = 0;
   out_834843542473115764[216] = 0;
   out_834843542473115764[217] = 0;
   out_834843542473115764[218] = 0;
   out_834843542473115764[219] = 0;
   out_834843542473115764[220] = 0;
   out_834843542473115764[221] = 0;
   out_834843542473115764[222] = 0;
   out_834843542473115764[223] = 0;
   out_834843542473115764[224] = 0;
   out_834843542473115764[225] = 0;
   out_834843542473115764[226] = 0;
   out_834843542473115764[227] = 0;
   out_834843542473115764[228] = 1;
   out_834843542473115764[229] = 0;
   out_834843542473115764[230] = 0;
   out_834843542473115764[231] = 0;
   out_834843542473115764[232] = 0;
   out_834843542473115764[233] = 0;
   out_834843542473115764[234] = 0;
   out_834843542473115764[235] = 0;
   out_834843542473115764[236] = 0;
   out_834843542473115764[237] = 0;
   out_834843542473115764[238] = 0;
   out_834843542473115764[239] = 0;
   out_834843542473115764[240] = 0;
   out_834843542473115764[241] = 0;
   out_834843542473115764[242] = 0;
   out_834843542473115764[243] = 0;
   out_834843542473115764[244] = 0;
   out_834843542473115764[245] = 0;
   out_834843542473115764[246] = 0;
   out_834843542473115764[247] = 1;
   out_834843542473115764[248] = 0;
   out_834843542473115764[249] = 0;
   out_834843542473115764[250] = 0;
   out_834843542473115764[251] = 0;
   out_834843542473115764[252] = 0;
   out_834843542473115764[253] = 0;
   out_834843542473115764[254] = 0;
   out_834843542473115764[255] = 0;
   out_834843542473115764[256] = 0;
   out_834843542473115764[257] = 0;
   out_834843542473115764[258] = 0;
   out_834843542473115764[259] = 0;
   out_834843542473115764[260] = 0;
   out_834843542473115764[261] = 0;
   out_834843542473115764[262] = 0;
   out_834843542473115764[263] = 0;
   out_834843542473115764[264] = 0;
   out_834843542473115764[265] = 0;
   out_834843542473115764[266] = 1;
   out_834843542473115764[267] = 0;
   out_834843542473115764[268] = 0;
   out_834843542473115764[269] = 0;
   out_834843542473115764[270] = 0;
   out_834843542473115764[271] = 0;
   out_834843542473115764[272] = 0;
   out_834843542473115764[273] = 0;
   out_834843542473115764[274] = 0;
   out_834843542473115764[275] = 0;
   out_834843542473115764[276] = 0;
   out_834843542473115764[277] = 0;
   out_834843542473115764[278] = 0;
   out_834843542473115764[279] = 0;
   out_834843542473115764[280] = 0;
   out_834843542473115764[281] = 0;
   out_834843542473115764[282] = 0;
   out_834843542473115764[283] = 0;
   out_834843542473115764[284] = 0;
   out_834843542473115764[285] = 1;
   out_834843542473115764[286] = 0;
   out_834843542473115764[287] = 0;
   out_834843542473115764[288] = 0;
   out_834843542473115764[289] = 0;
   out_834843542473115764[290] = 0;
   out_834843542473115764[291] = 0;
   out_834843542473115764[292] = 0;
   out_834843542473115764[293] = 0;
   out_834843542473115764[294] = 0;
   out_834843542473115764[295] = 0;
   out_834843542473115764[296] = 0;
   out_834843542473115764[297] = 0;
   out_834843542473115764[298] = 0;
   out_834843542473115764[299] = 0;
   out_834843542473115764[300] = 0;
   out_834843542473115764[301] = 0;
   out_834843542473115764[302] = 0;
   out_834843542473115764[303] = 0;
   out_834843542473115764[304] = 1;
   out_834843542473115764[305] = 0;
   out_834843542473115764[306] = 0;
   out_834843542473115764[307] = 0;
   out_834843542473115764[308] = 0;
   out_834843542473115764[309] = 0;
   out_834843542473115764[310] = 0;
   out_834843542473115764[311] = 0;
   out_834843542473115764[312] = 0;
   out_834843542473115764[313] = 0;
   out_834843542473115764[314] = 0;
   out_834843542473115764[315] = 0;
   out_834843542473115764[316] = 0;
   out_834843542473115764[317] = 0;
   out_834843542473115764[318] = 0;
   out_834843542473115764[319] = 0;
   out_834843542473115764[320] = 0;
   out_834843542473115764[321] = 0;
   out_834843542473115764[322] = 0;
   out_834843542473115764[323] = 1;
}
void h_4(double *state, double *unused, double *out_999525771239372771) {
   out_999525771239372771[0] = state[6] + state[9];
   out_999525771239372771[1] = state[7] + state[10];
   out_999525771239372771[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_645197448362710591) {
   out_645197448362710591[0] = 0;
   out_645197448362710591[1] = 0;
   out_645197448362710591[2] = 0;
   out_645197448362710591[3] = 0;
   out_645197448362710591[4] = 0;
   out_645197448362710591[5] = 0;
   out_645197448362710591[6] = 1;
   out_645197448362710591[7] = 0;
   out_645197448362710591[8] = 0;
   out_645197448362710591[9] = 1;
   out_645197448362710591[10] = 0;
   out_645197448362710591[11] = 0;
   out_645197448362710591[12] = 0;
   out_645197448362710591[13] = 0;
   out_645197448362710591[14] = 0;
   out_645197448362710591[15] = 0;
   out_645197448362710591[16] = 0;
   out_645197448362710591[17] = 0;
   out_645197448362710591[18] = 0;
   out_645197448362710591[19] = 0;
   out_645197448362710591[20] = 0;
   out_645197448362710591[21] = 0;
   out_645197448362710591[22] = 0;
   out_645197448362710591[23] = 0;
   out_645197448362710591[24] = 0;
   out_645197448362710591[25] = 1;
   out_645197448362710591[26] = 0;
   out_645197448362710591[27] = 0;
   out_645197448362710591[28] = 1;
   out_645197448362710591[29] = 0;
   out_645197448362710591[30] = 0;
   out_645197448362710591[31] = 0;
   out_645197448362710591[32] = 0;
   out_645197448362710591[33] = 0;
   out_645197448362710591[34] = 0;
   out_645197448362710591[35] = 0;
   out_645197448362710591[36] = 0;
   out_645197448362710591[37] = 0;
   out_645197448362710591[38] = 0;
   out_645197448362710591[39] = 0;
   out_645197448362710591[40] = 0;
   out_645197448362710591[41] = 0;
   out_645197448362710591[42] = 0;
   out_645197448362710591[43] = 0;
   out_645197448362710591[44] = 1;
   out_645197448362710591[45] = 0;
   out_645197448362710591[46] = 0;
   out_645197448362710591[47] = 1;
   out_645197448362710591[48] = 0;
   out_645197448362710591[49] = 0;
   out_645197448362710591[50] = 0;
   out_645197448362710591[51] = 0;
   out_645197448362710591[52] = 0;
   out_645197448362710591[53] = 0;
}
void h_10(double *state, double *unused, double *out_7654704647972063368) {
   out_7654704647972063368[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_7654704647972063368[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_7654704647972063368[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_3722851181056312265) {
   out_3722851181056312265[0] = 0;
   out_3722851181056312265[1] = 9.8100000000000005*cos(state[1]);
   out_3722851181056312265[2] = 0;
   out_3722851181056312265[3] = 0;
   out_3722851181056312265[4] = -state[8];
   out_3722851181056312265[5] = state[7];
   out_3722851181056312265[6] = 0;
   out_3722851181056312265[7] = state[5];
   out_3722851181056312265[8] = -state[4];
   out_3722851181056312265[9] = 0;
   out_3722851181056312265[10] = 0;
   out_3722851181056312265[11] = 0;
   out_3722851181056312265[12] = 1;
   out_3722851181056312265[13] = 0;
   out_3722851181056312265[14] = 0;
   out_3722851181056312265[15] = 1;
   out_3722851181056312265[16] = 0;
   out_3722851181056312265[17] = 0;
   out_3722851181056312265[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_3722851181056312265[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_3722851181056312265[20] = 0;
   out_3722851181056312265[21] = state[8];
   out_3722851181056312265[22] = 0;
   out_3722851181056312265[23] = -state[6];
   out_3722851181056312265[24] = -state[5];
   out_3722851181056312265[25] = 0;
   out_3722851181056312265[26] = state[3];
   out_3722851181056312265[27] = 0;
   out_3722851181056312265[28] = 0;
   out_3722851181056312265[29] = 0;
   out_3722851181056312265[30] = 0;
   out_3722851181056312265[31] = 1;
   out_3722851181056312265[32] = 0;
   out_3722851181056312265[33] = 0;
   out_3722851181056312265[34] = 1;
   out_3722851181056312265[35] = 0;
   out_3722851181056312265[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_3722851181056312265[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_3722851181056312265[38] = 0;
   out_3722851181056312265[39] = -state[7];
   out_3722851181056312265[40] = state[6];
   out_3722851181056312265[41] = 0;
   out_3722851181056312265[42] = state[4];
   out_3722851181056312265[43] = -state[3];
   out_3722851181056312265[44] = 0;
   out_3722851181056312265[45] = 0;
   out_3722851181056312265[46] = 0;
   out_3722851181056312265[47] = 0;
   out_3722851181056312265[48] = 0;
   out_3722851181056312265[49] = 0;
   out_3722851181056312265[50] = 1;
   out_3722851181056312265[51] = 0;
   out_3722851181056312265[52] = 0;
   out_3722851181056312265[53] = 1;
}
void h_13(double *state, double *unused, double *out_4337727964590481795) {
   out_4337727964590481795[0] = state[3];
   out_4337727964590481795[1] = state[4];
   out_4337727964590481795[2] = state[5];
}
void H_13(double *state, double *unused, double *out_3188558014939813433) {
   out_3188558014939813433[0] = 0;
   out_3188558014939813433[1] = 0;
   out_3188558014939813433[2] = 0;
   out_3188558014939813433[3] = 1;
   out_3188558014939813433[4] = 0;
   out_3188558014939813433[5] = 0;
   out_3188558014939813433[6] = 0;
   out_3188558014939813433[7] = 0;
   out_3188558014939813433[8] = 0;
   out_3188558014939813433[9] = 0;
   out_3188558014939813433[10] = 0;
   out_3188558014939813433[11] = 0;
   out_3188558014939813433[12] = 0;
   out_3188558014939813433[13] = 0;
   out_3188558014939813433[14] = 0;
   out_3188558014939813433[15] = 0;
   out_3188558014939813433[16] = 0;
   out_3188558014939813433[17] = 0;
   out_3188558014939813433[18] = 0;
   out_3188558014939813433[19] = 0;
   out_3188558014939813433[20] = 0;
   out_3188558014939813433[21] = 0;
   out_3188558014939813433[22] = 1;
   out_3188558014939813433[23] = 0;
   out_3188558014939813433[24] = 0;
   out_3188558014939813433[25] = 0;
   out_3188558014939813433[26] = 0;
   out_3188558014939813433[27] = 0;
   out_3188558014939813433[28] = 0;
   out_3188558014939813433[29] = 0;
   out_3188558014939813433[30] = 0;
   out_3188558014939813433[31] = 0;
   out_3188558014939813433[32] = 0;
   out_3188558014939813433[33] = 0;
   out_3188558014939813433[34] = 0;
   out_3188558014939813433[35] = 0;
   out_3188558014939813433[36] = 0;
   out_3188558014939813433[37] = 0;
   out_3188558014939813433[38] = 0;
   out_3188558014939813433[39] = 0;
   out_3188558014939813433[40] = 0;
   out_3188558014939813433[41] = 1;
   out_3188558014939813433[42] = 0;
   out_3188558014939813433[43] = 0;
   out_3188558014939813433[44] = 0;
   out_3188558014939813433[45] = 0;
   out_3188558014939813433[46] = 0;
   out_3188558014939813433[47] = 0;
   out_3188558014939813433[48] = 0;
   out_3188558014939813433[49] = 0;
   out_3188558014939813433[50] = 0;
   out_3188558014939813433[51] = 0;
   out_3188558014939813433[52] = 0;
   out_3188558014939813433[53] = 0;
}
void h_14(double *state, double *unused, double *out_4948904525269361383) {
   out_4948904525269361383[0] = state[6];
   out_4948904525269361383[1] = state[7];
   out_4948904525269361383[2] = state[8];
}
void H_14(double *state, double *unused, double *out_2437590983932661705) {
   out_2437590983932661705[0] = 0;
   out_2437590983932661705[1] = 0;
   out_2437590983932661705[2] = 0;
   out_2437590983932661705[3] = 0;
   out_2437590983932661705[4] = 0;
   out_2437590983932661705[5] = 0;
   out_2437590983932661705[6] = 1;
   out_2437590983932661705[7] = 0;
   out_2437590983932661705[8] = 0;
   out_2437590983932661705[9] = 0;
   out_2437590983932661705[10] = 0;
   out_2437590983932661705[11] = 0;
   out_2437590983932661705[12] = 0;
   out_2437590983932661705[13] = 0;
   out_2437590983932661705[14] = 0;
   out_2437590983932661705[15] = 0;
   out_2437590983932661705[16] = 0;
   out_2437590983932661705[17] = 0;
   out_2437590983932661705[18] = 0;
   out_2437590983932661705[19] = 0;
   out_2437590983932661705[20] = 0;
   out_2437590983932661705[21] = 0;
   out_2437590983932661705[22] = 0;
   out_2437590983932661705[23] = 0;
   out_2437590983932661705[24] = 0;
   out_2437590983932661705[25] = 1;
   out_2437590983932661705[26] = 0;
   out_2437590983932661705[27] = 0;
   out_2437590983932661705[28] = 0;
   out_2437590983932661705[29] = 0;
   out_2437590983932661705[30] = 0;
   out_2437590983932661705[31] = 0;
   out_2437590983932661705[32] = 0;
   out_2437590983932661705[33] = 0;
   out_2437590983932661705[34] = 0;
   out_2437590983932661705[35] = 0;
   out_2437590983932661705[36] = 0;
   out_2437590983932661705[37] = 0;
   out_2437590983932661705[38] = 0;
   out_2437590983932661705[39] = 0;
   out_2437590983932661705[40] = 0;
   out_2437590983932661705[41] = 0;
   out_2437590983932661705[42] = 0;
   out_2437590983932661705[43] = 0;
   out_2437590983932661705[44] = 1;
   out_2437590983932661705[45] = 0;
   out_2437590983932661705[46] = 0;
   out_2437590983932661705[47] = 0;
   out_2437590983932661705[48] = 0;
   out_2437590983932661705[49] = 0;
   out_2437590983932661705[50] = 0;
   out_2437590983932661705[51] = 0;
   out_2437590983932661705[52] = 0;
   out_2437590983932661705[53] = 0;
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
void pose_err_fun(double *nom_x, double *delta_x, double *out_8941250306396925607) {
  err_fun(nom_x, delta_x, out_8941250306396925607);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_7188163769114424214) {
  inv_err_fun(nom_x, true_x, out_7188163769114424214);
}
void pose_H_mod_fun(double *state, double *out_3126609761481196981) {
  H_mod_fun(state, out_3126609761481196981);
}
void pose_f_fun(double *state, double dt, double *out_7800799004538587322) {
  f_fun(state,  dt, out_7800799004538587322);
}
void pose_F_fun(double *state, double dt, double *out_834843542473115764) {
  F_fun(state,  dt, out_834843542473115764);
}
void pose_h_4(double *state, double *unused, double *out_999525771239372771) {
  h_4(state, unused, out_999525771239372771);
}
void pose_H_4(double *state, double *unused, double *out_645197448362710591) {
  H_4(state, unused, out_645197448362710591);
}
void pose_h_10(double *state, double *unused, double *out_7654704647972063368) {
  h_10(state, unused, out_7654704647972063368);
}
void pose_H_10(double *state, double *unused, double *out_3722851181056312265) {
  H_10(state, unused, out_3722851181056312265);
}
void pose_h_13(double *state, double *unused, double *out_4337727964590481795) {
  h_13(state, unused, out_4337727964590481795);
}
void pose_H_13(double *state, double *unused, double *out_3188558014939813433) {
  H_13(state, unused, out_3188558014939813433);
}
void pose_h_14(double *state, double *unused, double *out_4948904525269361383) {
  h_14(state, unused, out_4948904525269361383);
}
void pose_H_14(double *state, double *unused, double *out_2437590983932661705) {
  H_14(state, unused, out_2437590983932661705);
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
