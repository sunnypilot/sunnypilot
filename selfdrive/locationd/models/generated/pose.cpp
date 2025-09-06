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
void err_fun(double *nom_x, double *delta_x, double *out_2598376982485037805) {
   out_2598376982485037805[0] = delta_x[0] + nom_x[0];
   out_2598376982485037805[1] = delta_x[1] + nom_x[1];
   out_2598376982485037805[2] = delta_x[2] + nom_x[2];
   out_2598376982485037805[3] = delta_x[3] + nom_x[3];
   out_2598376982485037805[4] = delta_x[4] + nom_x[4];
   out_2598376982485037805[5] = delta_x[5] + nom_x[5];
   out_2598376982485037805[6] = delta_x[6] + nom_x[6];
   out_2598376982485037805[7] = delta_x[7] + nom_x[7];
   out_2598376982485037805[8] = delta_x[8] + nom_x[8];
   out_2598376982485037805[9] = delta_x[9] + nom_x[9];
   out_2598376982485037805[10] = delta_x[10] + nom_x[10];
   out_2598376982485037805[11] = delta_x[11] + nom_x[11];
   out_2598376982485037805[12] = delta_x[12] + nom_x[12];
   out_2598376982485037805[13] = delta_x[13] + nom_x[13];
   out_2598376982485037805[14] = delta_x[14] + nom_x[14];
   out_2598376982485037805[15] = delta_x[15] + nom_x[15];
   out_2598376982485037805[16] = delta_x[16] + nom_x[16];
   out_2598376982485037805[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_4512324947371561180) {
   out_4512324947371561180[0] = -nom_x[0] + true_x[0];
   out_4512324947371561180[1] = -nom_x[1] + true_x[1];
   out_4512324947371561180[2] = -nom_x[2] + true_x[2];
   out_4512324947371561180[3] = -nom_x[3] + true_x[3];
   out_4512324947371561180[4] = -nom_x[4] + true_x[4];
   out_4512324947371561180[5] = -nom_x[5] + true_x[5];
   out_4512324947371561180[6] = -nom_x[6] + true_x[6];
   out_4512324947371561180[7] = -nom_x[7] + true_x[7];
   out_4512324947371561180[8] = -nom_x[8] + true_x[8];
   out_4512324947371561180[9] = -nom_x[9] + true_x[9];
   out_4512324947371561180[10] = -nom_x[10] + true_x[10];
   out_4512324947371561180[11] = -nom_x[11] + true_x[11];
   out_4512324947371561180[12] = -nom_x[12] + true_x[12];
   out_4512324947371561180[13] = -nom_x[13] + true_x[13];
   out_4512324947371561180[14] = -nom_x[14] + true_x[14];
   out_4512324947371561180[15] = -nom_x[15] + true_x[15];
   out_4512324947371561180[16] = -nom_x[16] + true_x[16];
   out_4512324947371561180[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_2316928423571127677) {
   out_2316928423571127677[0] = 1.0;
   out_2316928423571127677[1] = 0.0;
   out_2316928423571127677[2] = 0.0;
   out_2316928423571127677[3] = 0.0;
   out_2316928423571127677[4] = 0.0;
   out_2316928423571127677[5] = 0.0;
   out_2316928423571127677[6] = 0.0;
   out_2316928423571127677[7] = 0.0;
   out_2316928423571127677[8] = 0.0;
   out_2316928423571127677[9] = 0.0;
   out_2316928423571127677[10] = 0.0;
   out_2316928423571127677[11] = 0.0;
   out_2316928423571127677[12] = 0.0;
   out_2316928423571127677[13] = 0.0;
   out_2316928423571127677[14] = 0.0;
   out_2316928423571127677[15] = 0.0;
   out_2316928423571127677[16] = 0.0;
   out_2316928423571127677[17] = 0.0;
   out_2316928423571127677[18] = 0.0;
   out_2316928423571127677[19] = 1.0;
   out_2316928423571127677[20] = 0.0;
   out_2316928423571127677[21] = 0.0;
   out_2316928423571127677[22] = 0.0;
   out_2316928423571127677[23] = 0.0;
   out_2316928423571127677[24] = 0.0;
   out_2316928423571127677[25] = 0.0;
   out_2316928423571127677[26] = 0.0;
   out_2316928423571127677[27] = 0.0;
   out_2316928423571127677[28] = 0.0;
   out_2316928423571127677[29] = 0.0;
   out_2316928423571127677[30] = 0.0;
   out_2316928423571127677[31] = 0.0;
   out_2316928423571127677[32] = 0.0;
   out_2316928423571127677[33] = 0.0;
   out_2316928423571127677[34] = 0.0;
   out_2316928423571127677[35] = 0.0;
   out_2316928423571127677[36] = 0.0;
   out_2316928423571127677[37] = 0.0;
   out_2316928423571127677[38] = 1.0;
   out_2316928423571127677[39] = 0.0;
   out_2316928423571127677[40] = 0.0;
   out_2316928423571127677[41] = 0.0;
   out_2316928423571127677[42] = 0.0;
   out_2316928423571127677[43] = 0.0;
   out_2316928423571127677[44] = 0.0;
   out_2316928423571127677[45] = 0.0;
   out_2316928423571127677[46] = 0.0;
   out_2316928423571127677[47] = 0.0;
   out_2316928423571127677[48] = 0.0;
   out_2316928423571127677[49] = 0.0;
   out_2316928423571127677[50] = 0.0;
   out_2316928423571127677[51] = 0.0;
   out_2316928423571127677[52] = 0.0;
   out_2316928423571127677[53] = 0.0;
   out_2316928423571127677[54] = 0.0;
   out_2316928423571127677[55] = 0.0;
   out_2316928423571127677[56] = 0.0;
   out_2316928423571127677[57] = 1.0;
   out_2316928423571127677[58] = 0.0;
   out_2316928423571127677[59] = 0.0;
   out_2316928423571127677[60] = 0.0;
   out_2316928423571127677[61] = 0.0;
   out_2316928423571127677[62] = 0.0;
   out_2316928423571127677[63] = 0.0;
   out_2316928423571127677[64] = 0.0;
   out_2316928423571127677[65] = 0.0;
   out_2316928423571127677[66] = 0.0;
   out_2316928423571127677[67] = 0.0;
   out_2316928423571127677[68] = 0.0;
   out_2316928423571127677[69] = 0.0;
   out_2316928423571127677[70] = 0.0;
   out_2316928423571127677[71] = 0.0;
   out_2316928423571127677[72] = 0.0;
   out_2316928423571127677[73] = 0.0;
   out_2316928423571127677[74] = 0.0;
   out_2316928423571127677[75] = 0.0;
   out_2316928423571127677[76] = 1.0;
   out_2316928423571127677[77] = 0.0;
   out_2316928423571127677[78] = 0.0;
   out_2316928423571127677[79] = 0.0;
   out_2316928423571127677[80] = 0.0;
   out_2316928423571127677[81] = 0.0;
   out_2316928423571127677[82] = 0.0;
   out_2316928423571127677[83] = 0.0;
   out_2316928423571127677[84] = 0.0;
   out_2316928423571127677[85] = 0.0;
   out_2316928423571127677[86] = 0.0;
   out_2316928423571127677[87] = 0.0;
   out_2316928423571127677[88] = 0.0;
   out_2316928423571127677[89] = 0.0;
   out_2316928423571127677[90] = 0.0;
   out_2316928423571127677[91] = 0.0;
   out_2316928423571127677[92] = 0.0;
   out_2316928423571127677[93] = 0.0;
   out_2316928423571127677[94] = 0.0;
   out_2316928423571127677[95] = 1.0;
   out_2316928423571127677[96] = 0.0;
   out_2316928423571127677[97] = 0.0;
   out_2316928423571127677[98] = 0.0;
   out_2316928423571127677[99] = 0.0;
   out_2316928423571127677[100] = 0.0;
   out_2316928423571127677[101] = 0.0;
   out_2316928423571127677[102] = 0.0;
   out_2316928423571127677[103] = 0.0;
   out_2316928423571127677[104] = 0.0;
   out_2316928423571127677[105] = 0.0;
   out_2316928423571127677[106] = 0.0;
   out_2316928423571127677[107] = 0.0;
   out_2316928423571127677[108] = 0.0;
   out_2316928423571127677[109] = 0.0;
   out_2316928423571127677[110] = 0.0;
   out_2316928423571127677[111] = 0.0;
   out_2316928423571127677[112] = 0.0;
   out_2316928423571127677[113] = 0.0;
   out_2316928423571127677[114] = 1.0;
   out_2316928423571127677[115] = 0.0;
   out_2316928423571127677[116] = 0.0;
   out_2316928423571127677[117] = 0.0;
   out_2316928423571127677[118] = 0.0;
   out_2316928423571127677[119] = 0.0;
   out_2316928423571127677[120] = 0.0;
   out_2316928423571127677[121] = 0.0;
   out_2316928423571127677[122] = 0.0;
   out_2316928423571127677[123] = 0.0;
   out_2316928423571127677[124] = 0.0;
   out_2316928423571127677[125] = 0.0;
   out_2316928423571127677[126] = 0.0;
   out_2316928423571127677[127] = 0.0;
   out_2316928423571127677[128] = 0.0;
   out_2316928423571127677[129] = 0.0;
   out_2316928423571127677[130] = 0.0;
   out_2316928423571127677[131] = 0.0;
   out_2316928423571127677[132] = 0.0;
   out_2316928423571127677[133] = 1.0;
   out_2316928423571127677[134] = 0.0;
   out_2316928423571127677[135] = 0.0;
   out_2316928423571127677[136] = 0.0;
   out_2316928423571127677[137] = 0.0;
   out_2316928423571127677[138] = 0.0;
   out_2316928423571127677[139] = 0.0;
   out_2316928423571127677[140] = 0.0;
   out_2316928423571127677[141] = 0.0;
   out_2316928423571127677[142] = 0.0;
   out_2316928423571127677[143] = 0.0;
   out_2316928423571127677[144] = 0.0;
   out_2316928423571127677[145] = 0.0;
   out_2316928423571127677[146] = 0.0;
   out_2316928423571127677[147] = 0.0;
   out_2316928423571127677[148] = 0.0;
   out_2316928423571127677[149] = 0.0;
   out_2316928423571127677[150] = 0.0;
   out_2316928423571127677[151] = 0.0;
   out_2316928423571127677[152] = 1.0;
   out_2316928423571127677[153] = 0.0;
   out_2316928423571127677[154] = 0.0;
   out_2316928423571127677[155] = 0.0;
   out_2316928423571127677[156] = 0.0;
   out_2316928423571127677[157] = 0.0;
   out_2316928423571127677[158] = 0.0;
   out_2316928423571127677[159] = 0.0;
   out_2316928423571127677[160] = 0.0;
   out_2316928423571127677[161] = 0.0;
   out_2316928423571127677[162] = 0.0;
   out_2316928423571127677[163] = 0.0;
   out_2316928423571127677[164] = 0.0;
   out_2316928423571127677[165] = 0.0;
   out_2316928423571127677[166] = 0.0;
   out_2316928423571127677[167] = 0.0;
   out_2316928423571127677[168] = 0.0;
   out_2316928423571127677[169] = 0.0;
   out_2316928423571127677[170] = 0.0;
   out_2316928423571127677[171] = 1.0;
   out_2316928423571127677[172] = 0.0;
   out_2316928423571127677[173] = 0.0;
   out_2316928423571127677[174] = 0.0;
   out_2316928423571127677[175] = 0.0;
   out_2316928423571127677[176] = 0.0;
   out_2316928423571127677[177] = 0.0;
   out_2316928423571127677[178] = 0.0;
   out_2316928423571127677[179] = 0.0;
   out_2316928423571127677[180] = 0.0;
   out_2316928423571127677[181] = 0.0;
   out_2316928423571127677[182] = 0.0;
   out_2316928423571127677[183] = 0.0;
   out_2316928423571127677[184] = 0.0;
   out_2316928423571127677[185] = 0.0;
   out_2316928423571127677[186] = 0.0;
   out_2316928423571127677[187] = 0.0;
   out_2316928423571127677[188] = 0.0;
   out_2316928423571127677[189] = 0.0;
   out_2316928423571127677[190] = 1.0;
   out_2316928423571127677[191] = 0.0;
   out_2316928423571127677[192] = 0.0;
   out_2316928423571127677[193] = 0.0;
   out_2316928423571127677[194] = 0.0;
   out_2316928423571127677[195] = 0.0;
   out_2316928423571127677[196] = 0.0;
   out_2316928423571127677[197] = 0.0;
   out_2316928423571127677[198] = 0.0;
   out_2316928423571127677[199] = 0.0;
   out_2316928423571127677[200] = 0.0;
   out_2316928423571127677[201] = 0.0;
   out_2316928423571127677[202] = 0.0;
   out_2316928423571127677[203] = 0.0;
   out_2316928423571127677[204] = 0.0;
   out_2316928423571127677[205] = 0.0;
   out_2316928423571127677[206] = 0.0;
   out_2316928423571127677[207] = 0.0;
   out_2316928423571127677[208] = 0.0;
   out_2316928423571127677[209] = 1.0;
   out_2316928423571127677[210] = 0.0;
   out_2316928423571127677[211] = 0.0;
   out_2316928423571127677[212] = 0.0;
   out_2316928423571127677[213] = 0.0;
   out_2316928423571127677[214] = 0.0;
   out_2316928423571127677[215] = 0.0;
   out_2316928423571127677[216] = 0.0;
   out_2316928423571127677[217] = 0.0;
   out_2316928423571127677[218] = 0.0;
   out_2316928423571127677[219] = 0.0;
   out_2316928423571127677[220] = 0.0;
   out_2316928423571127677[221] = 0.0;
   out_2316928423571127677[222] = 0.0;
   out_2316928423571127677[223] = 0.0;
   out_2316928423571127677[224] = 0.0;
   out_2316928423571127677[225] = 0.0;
   out_2316928423571127677[226] = 0.0;
   out_2316928423571127677[227] = 0.0;
   out_2316928423571127677[228] = 1.0;
   out_2316928423571127677[229] = 0.0;
   out_2316928423571127677[230] = 0.0;
   out_2316928423571127677[231] = 0.0;
   out_2316928423571127677[232] = 0.0;
   out_2316928423571127677[233] = 0.0;
   out_2316928423571127677[234] = 0.0;
   out_2316928423571127677[235] = 0.0;
   out_2316928423571127677[236] = 0.0;
   out_2316928423571127677[237] = 0.0;
   out_2316928423571127677[238] = 0.0;
   out_2316928423571127677[239] = 0.0;
   out_2316928423571127677[240] = 0.0;
   out_2316928423571127677[241] = 0.0;
   out_2316928423571127677[242] = 0.0;
   out_2316928423571127677[243] = 0.0;
   out_2316928423571127677[244] = 0.0;
   out_2316928423571127677[245] = 0.0;
   out_2316928423571127677[246] = 0.0;
   out_2316928423571127677[247] = 1.0;
   out_2316928423571127677[248] = 0.0;
   out_2316928423571127677[249] = 0.0;
   out_2316928423571127677[250] = 0.0;
   out_2316928423571127677[251] = 0.0;
   out_2316928423571127677[252] = 0.0;
   out_2316928423571127677[253] = 0.0;
   out_2316928423571127677[254] = 0.0;
   out_2316928423571127677[255] = 0.0;
   out_2316928423571127677[256] = 0.0;
   out_2316928423571127677[257] = 0.0;
   out_2316928423571127677[258] = 0.0;
   out_2316928423571127677[259] = 0.0;
   out_2316928423571127677[260] = 0.0;
   out_2316928423571127677[261] = 0.0;
   out_2316928423571127677[262] = 0.0;
   out_2316928423571127677[263] = 0.0;
   out_2316928423571127677[264] = 0.0;
   out_2316928423571127677[265] = 0.0;
   out_2316928423571127677[266] = 1.0;
   out_2316928423571127677[267] = 0.0;
   out_2316928423571127677[268] = 0.0;
   out_2316928423571127677[269] = 0.0;
   out_2316928423571127677[270] = 0.0;
   out_2316928423571127677[271] = 0.0;
   out_2316928423571127677[272] = 0.0;
   out_2316928423571127677[273] = 0.0;
   out_2316928423571127677[274] = 0.0;
   out_2316928423571127677[275] = 0.0;
   out_2316928423571127677[276] = 0.0;
   out_2316928423571127677[277] = 0.0;
   out_2316928423571127677[278] = 0.0;
   out_2316928423571127677[279] = 0.0;
   out_2316928423571127677[280] = 0.0;
   out_2316928423571127677[281] = 0.0;
   out_2316928423571127677[282] = 0.0;
   out_2316928423571127677[283] = 0.0;
   out_2316928423571127677[284] = 0.0;
   out_2316928423571127677[285] = 1.0;
   out_2316928423571127677[286] = 0.0;
   out_2316928423571127677[287] = 0.0;
   out_2316928423571127677[288] = 0.0;
   out_2316928423571127677[289] = 0.0;
   out_2316928423571127677[290] = 0.0;
   out_2316928423571127677[291] = 0.0;
   out_2316928423571127677[292] = 0.0;
   out_2316928423571127677[293] = 0.0;
   out_2316928423571127677[294] = 0.0;
   out_2316928423571127677[295] = 0.0;
   out_2316928423571127677[296] = 0.0;
   out_2316928423571127677[297] = 0.0;
   out_2316928423571127677[298] = 0.0;
   out_2316928423571127677[299] = 0.0;
   out_2316928423571127677[300] = 0.0;
   out_2316928423571127677[301] = 0.0;
   out_2316928423571127677[302] = 0.0;
   out_2316928423571127677[303] = 0.0;
   out_2316928423571127677[304] = 1.0;
   out_2316928423571127677[305] = 0.0;
   out_2316928423571127677[306] = 0.0;
   out_2316928423571127677[307] = 0.0;
   out_2316928423571127677[308] = 0.0;
   out_2316928423571127677[309] = 0.0;
   out_2316928423571127677[310] = 0.0;
   out_2316928423571127677[311] = 0.0;
   out_2316928423571127677[312] = 0.0;
   out_2316928423571127677[313] = 0.0;
   out_2316928423571127677[314] = 0.0;
   out_2316928423571127677[315] = 0.0;
   out_2316928423571127677[316] = 0.0;
   out_2316928423571127677[317] = 0.0;
   out_2316928423571127677[318] = 0.0;
   out_2316928423571127677[319] = 0.0;
   out_2316928423571127677[320] = 0.0;
   out_2316928423571127677[321] = 0.0;
   out_2316928423571127677[322] = 0.0;
   out_2316928423571127677[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_5656120576541900457) {
   out_5656120576541900457[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_5656120576541900457[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_5656120576541900457[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_5656120576541900457[3] = dt*state[12] + state[3];
   out_5656120576541900457[4] = dt*state[13] + state[4];
   out_5656120576541900457[5] = dt*state[14] + state[5];
   out_5656120576541900457[6] = state[6];
   out_5656120576541900457[7] = state[7];
   out_5656120576541900457[8] = state[8];
   out_5656120576541900457[9] = state[9];
   out_5656120576541900457[10] = state[10];
   out_5656120576541900457[11] = state[11];
   out_5656120576541900457[12] = state[12];
   out_5656120576541900457[13] = state[13];
   out_5656120576541900457[14] = state[14];
   out_5656120576541900457[15] = state[15];
   out_5656120576541900457[16] = state[16];
   out_5656120576541900457[17] = state[17];
}
void F_fun(double *state, double dt, double *out_4610640204669690281) {
   out_4610640204669690281[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_4610640204669690281[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_4610640204669690281[2] = 0;
   out_4610640204669690281[3] = 0;
   out_4610640204669690281[4] = 0;
   out_4610640204669690281[5] = 0;
   out_4610640204669690281[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_4610640204669690281[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_4610640204669690281[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_4610640204669690281[9] = 0;
   out_4610640204669690281[10] = 0;
   out_4610640204669690281[11] = 0;
   out_4610640204669690281[12] = 0;
   out_4610640204669690281[13] = 0;
   out_4610640204669690281[14] = 0;
   out_4610640204669690281[15] = 0;
   out_4610640204669690281[16] = 0;
   out_4610640204669690281[17] = 0;
   out_4610640204669690281[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_4610640204669690281[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_4610640204669690281[20] = 0;
   out_4610640204669690281[21] = 0;
   out_4610640204669690281[22] = 0;
   out_4610640204669690281[23] = 0;
   out_4610640204669690281[24] = 0;
   out_4610640204669690281[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_4610640204669690281[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_4610640204669690281[27] = 0;
   out_4610640204669690281[28] = 0;
   out_4610640204669690281[29] = 0;
   out_4610640204669690281[30] = 0;
   out_4610640204669690281[31] = 0;
   out_4610640204669690281[32] = 0;
   out_4610640204669690281[33] = 0;
   out_4610640204669690281[34] = 0;
   out_4610640204669690281[35] = 0;
   out_4610640204669690281[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_4610640204669690281[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_4610640204669690281[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_4610640204669690281[39] = 0;
   out_4610640204669690281[40] = 0;
   out_4610640204669690281[41] = 0;
   out_4610640204669690281[42] = 0;
   out_4610640204669690281[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_4610640204669690281[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_4610640204669690281[45] = 0;
   out_4610640204669690281[46] = 0;
   out_4610640204669690281[47] = 0;
   out_4610640204669690281[48] = 0;
   out_4610640204669690281[49] = 0;
   out_4610640204669690281[50] = 0;
   out_4610640204669690281[51] = 0;
   out_4610640204669690281[52] = 0;
   out_4610640204669690281[53] = 0;
   out_4610640204669690281[54] = 0;
   out_4610640204669690281[55] = 0;
   out_4610640204669690281[56] = 0;
   out_4610640204669690281[57] = 1;
   out_4610640204669690281[58] = 0;
   out_4610640204669690281[59] = 0;
   out_4610640204669690281[60] = 0;
   out_4610640204669690281[61] = 0;
   out_4610640204669690281[62] = 0;
   out_4610640204669690281[63] = 0;
   out_4610640204669690281[64] = 0;
   out_4610640204669690281[65] = 0;
   out_4610640204669690281[66] = dt;
   out_4610640204669690281[67] = 0;
   out_4610640204669690281[68] = 0;
   out_4610640204669690281[69] = 0;
   out_4610640204669690281[70] = 0;
   out_4610640204669690281[71] = 0;
   out_4610640204669690281[72] = 0;
   out_4610640204669690281[73] = 0;
   out_4610640204669690281[74] = 0;
   out_4610640204669690281[75] = 0;
   out_4610640204669690281[76] = 1;
   out_4610640204669690281[77] = 0;
   out_4610640204669690281[78] = 0;
   out_4610640204669690281[79] = 0;
   out_4610640204669690281[80] = 0;
   out_4610640204669690281[81] = 0;
   out_4610640204669690281[82] = 0;
   out_4610640204669690281[83] = 0;
   out_4610640204669690281[84] = 0;
   out_4610640204669690281[85] = dt;
   out_4610640204669690281[86] = 0;
   out_4610640204669690281[87] = 0;
   out_4610640204669690281[88] = 0;
   out_4610640204669690281[89] = 0;
   out_4610640204669690281[90] = 0;
   out_4610640204669690281[91] = 0;
   out_4610640204669690281[92] = 0;
   out_4610640204669690281[93] = 0;
   out_4610640204669690281[94] = 0;
   out_4610640204669690281[95] = 1;
   out_4610640204669690281[96] = 0;
   out_4610640204669690281[97] = 0;
   out_4610640204669690281[98] = 0;
   out_4610640204669690281[99] = 0;
   out_4610640204669690281[100] = 0;
   out_4610640204669690281[101] = 0;
   out_4610640204669690281[102] = 0;
   out_4610640204669690281[103] = 0;
   out_4610640204669690281[104] = dt;
   out_4610640204669690281[105] = 0;
   out_4610640204669690281[106] = 0;
   out_4610640204669690281[107] = 0;
   out_4610640204669690281[108] = 0;
   out_4610640204669690281[109] = 0;
   out_4610640204669690281[110] = 0;
   out_4610640204669690281[111] = 0;
   out_4610640204669690281[112] = 0;
   out_4610640204669690281[113] = 0;
   out_4610640204669690281[114] = 1;
   out_4610640204669690281[115] = 0;
   out_4610640204669690281[116] = 0;
   out_4610640204669690281[117] = 0;
   out_4610640204669690281[118] = 0;
   out_4610640204669690281[119] = 0;
   out_4610640204669690281[120] = 0;
   out_4610640204669690281[121] = 0;
   out_4610640204669690281[122] = 0;
   out_4610640204669690281[123] = 0;
   out_4610640204669690281[124] = 0;
   out_4610640204669690281[125] = 0;
   out_4610640204669690281[126] = 0;
   out_4610640204669690281[127] = 0;
   out_4610640204669690281[128] = 0;
   out_4610640204669690281[129] = 0;
   out_4610640204669690281[130] = 0;
   out_4610640204669690281[131] = 0;
   out_4610640204669690281[132] = 0;
   out_4610640204669690281[133] = 1;
   out_4610640204669690281[134] = 0;
   out_4610640204669690281[135] = 0;
   out_4610640204669690281[136] = 0;
   out_4610640204669690281[137] = 0;
   out_4610640204669690281[138] = 0;
   out_4610640204669690281[139] = 0;
   out_4610640204669690281[140] = 0;
   out_4610640204669690281[141] = 0;
   out_4610640204669690281[142] = 0;
   out_4610640204669690281[143] = 0;
   out_4610640204669690281[144] = 0;
   out_4610640204669690281[145] = 0;
   out_4610640204669690281[146] = 0;
   out_4610640204669690281[147] = 0;
   out_4610640204669690281[148] = 0;
   out_4610640204669690281[149] = 0;
   out_4610640204669690281[150] = 0;
   out_4610640204669690281[151] = 0;
   out_4610640204669690281[152] = 1;
   out_4610640204669690281[153] = 0;
   out_4610640204669690281[154] = 0;
   out_4610640204669690281[155] = 0;
   out_4610640204669690281[156] = 0;
   out_4610640204669690281[157] = 0;
   out_4610640204669690281[158] = 0;
   out_4610640204669690281[159] = 0;
   out_4610640204669690281[160] = 0;
   out_4610640204669690281[161] = 0;
   out_4610640204669690281[162] = 0;
   out_4610640204669690281[163] = 0;
   out_4610640204669690281[164] = 0;
   out_4610640204669690281[165] = 0;
   out_4610640204669690281[166] = 0;
   out_4610640204669690281[167] = 0;
   out_4610640204669690281[168] = 0;
   out_4610640204669690281[169] = 0;
   out_4610640204669690281[170] = 0;
   out_4610640204669690281[171] = 1;
   out_4610640204669690281[172] = 0;
   out_4610640204669690281[173] = 0;
   out_4610640204669690281[174] = 0;
   out_4610640204669690281[175] = 0;
   out_4610640204669690281[176] = 0;
   out_4610640204669690281[177] = 0;
   out_4610640204669690281[178] = 0;
   out_4610640204669690281[179] = 0;
   out_4610640204669690281[180] = 0;
   out_4610640204669690281[181] = 0;
   out_4610640204669690281[182] = 0;
   out_4610640204669690281[183] = 0;
   out_4610640204669690281[184] = 0;
   out_4610640204669690281[185] = 0;
   out_4610640204669690281[186] = 0;
   out_4610640204669690281[187] = 0;
   out_4610640204669690281[188] = 0;
   out_4610640204669690281[189] = 0;
   out_4610640204669690281[190] = 1;
   out_4610640204669690281[191] = 0;
   out_4610640204669690281[192] = 0;
   out_4610640204669690281[193] = 0;
   out_4610640204669690281[194] = 0;
   out_4610640204669690281[195] = 0;
   out_4610640204669690281[196] = 0;
   out_4610640204669690281[197] = 0;
   out_4610640204669690281[198] = 0;
   out_4610640204669690281[199] = 0;
   out_4610640204669690281[200] = 0;
   out_4610640204669690281[201] = 0;
   out_4610640204669690281[202] = 0;
   out_4610640204669690281[203] = 0;
   out_4610640204669690281[204] = 0;
   out_4610640204669690281[205] = 0;
   out_4610640204669690281[206] = 0;
   out_4610640204669690281[207] = 0;
   out_4610640204669690281[208] = 0;
   out_4610640204669690281[209] = 1;
   out_4610640204669690281[210] = 0;
   out_4610640204669690281[211] = 0;
   out_4610640204669690281[212] = 0;
   out_4610640204669690281[213] = 0;
   out_4610640204669690281[214] = 0;
   out_4610640204669690281[215] = 0;
   out_4610640204669690281[216] = 0;
   out_4610640204669690281[217] = 0;
   out_4610640204669690281[218] = 0;
   out_4610640204669690281[219] = 0;
   out_4610640204669690281[220] = 0;
   out_4610640204669690281[221] = 0;
   out_4610640204669690281[222] = 0;
   out_4610640204669690281[223] = 0;
   out_4610640204669690281[224] = 0;
   out_4610640204669690281[225] = 0;
   out_4610640204669690281[226] = 0;
   out_4610640204669690281[227] = 0;
   out_4610640204669690281[228] = 1;
   out_4610640204669690281[229] = 0;
   out_4610640204669690281[230] = 0;
   out_4610640204669690281[231] = 0;
   out_4610640204669690281[232] = 0;
   out_4610640204669690281[233] = 0;
   out_4610640204669690281[234] = 0;
   out_4610640204669690281[235] = 0;
   out_4610640204669690281[236] = 0;
   out_4610640204669690281[237] = 0;
   out_4610640204669690281[238] = 0;
   out_4610640204669690281[239] = 0;
   out_4610640204669690281[240] = 0;
   out_4610640204669690281[241] = 0;
   out_4610640204669690281[242] = 0;
   out_4610640204669690281[243] = 0;
   out_4610640204669690281[244] = 0;
   out_4610640204669690281[245] = 0;
   out_4610640204669690281[246] = 0;
   out_4610640204669690281[247] = 1;
   out_4610640204669690281[248] = 0;
   out_4610640204669690281[249] = 0;
   out_4610640204669690281[250] = 0;
   out_4610640204669690281[251] = 0;
   out_4610640204669690281[252] = 0;
   out_4610640204669690281[253] = 0;
   out_4610640204669690281[254] = 0;
   out_4610640204669690281[255] = 0;
   out_4610640204669690281[256] = 0;
   out_4610640204669690281[257] = 0;
   out_4610640204669690281[258] = 0;
   out_4610640204669690281[259] = 0;
   out_4610640204669690281[260] = 0;
   out_4610640204669690281[261] = 0;
   out_4610640204669690281[262] = 0;
   out_4610640204669690281[263] = 0;
   out_4610640204669690281[264] = 0;
   out_4610640204669690281[265] = 0;
   out_4610640204669690281[266] = 1;
   out_4610640204669690281[267] = 0;
   out_4610640204669690281[268] = 0;
   out_4610640204669690281[269] = 0;
   out_4610640204669690281[270] = 0;
   out_4610640204669690281[271] = 0;
   out_4610640204669690281[272] = 0;
   out_4610640204669690281[273] = 0;
   out_4610640204669690281[274] = 0;
   out_4610640204669690281[275] = 0;
   out_4610640204669690281[276] = 0;
   out_4610640204669690281[277] = 0;
   out_4610640204669690281[278] = 0;
   out_4610640204669690281[279] = 0;
   out_4610640204669690281[280] = 0;
   out_4610640204669690281[281] = 0;
   out_4610640204669690281[282] = 0;
   out_4610640204669690281[283] = 0;
   out_4610640204669690281[284] = 0;
   out_4610640204669690281[285] = 1;
   out_4610640204669690281[286] = 0;
   out_4610640204669690281[287] = 0;
   out_4610640204669690281[288] = 0;
   out_4610640204669690281[289] = 0;
   out_4610640204669690281[290] = 0;
   out_4610640204669690281[291] = 0;
   out_4610640204669690281[292] = 0;
   out_4610640204669690281[293] = 0;
   out_4610640204669690281[294] = 0;
   out_4610640204669690281[295] = 0;
   out_4610640204669690281[296] = 0;
   out_4610640204669690281[297] = 0;
   out_4610640204669690281[298] = 0;
   out_4610640204669690281[299] = 0;
   out_4610640204669690281[300] = 0;
   out_4610640204669690281[301] = 0;
   out_4610640204669690281[302] = 0;
   out_4610640204669690281[303] = 0;
   out_4610640204669690281[304] = 1;
   out_4610640204669690281[305] = 0;
   out_4610640204669690281[306] = 0;
   out_4610640204669690281[307] = 0;
   out_4610640204669690281[308] = 0;
   out_4610640204669690281[309] = 0;
   out_4610640204669690281[310] = 0;
   out_4610640204669690281[311] = 0;
   out_4610640204669690281[312] = 0;
   out_4610640204669690281[313] = 0;
   out_4610640204669690281[314] = 0;
   out_4610640204669690281[315] = 0;
   out_4610640204669690281[316] = 0;
   out_4610640204669690281[317] = 0;
   out_4610640204669690281[318] = 0;
   out_4610640204669690281[319] = 0;
   out_4610640204669690281[320] = 0;
   out_4610640204669690281[321] = 0;
   out_4610640204669690281[322] = 0;
   out_4610640204669690281[323] = 1;
}
void h_4(double *state, double *unused, double *out_1496184824162482188) {
   out_1496184824162482188[0] = state[6] + state[9];
   out_1496184824162482188[1] = state[7] + state[10];
   out_1496184824162482188[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_3514875905454025781) {
   out_3514875905454025781[0] = 0;
   out_3514875905454025781[1] = 0;
   out_3514875905454025781[2] = 0;
   out_3514875905454025781[3] = 0;
   out_3514875905454025781[4] = 0;
   out_3514875905454025781[5] = 0;
   out_3514875905454025781[6] = 1;
   out_3514875905454025781[7] = 0;
   out_3514875905454025781[8] = 0;
   out_3514875905454025781[9] = 1;
   out_3514875905454025781[10] = 0;
   out_3514875905454025781[11] = 0;
   out_3514875905454025781[12] = 0;
   out_3514875905454025781[13] = 0;
   out_3514875905454025781[14] = 0;
   out_3514875905454025781[15] = 0;
   out_3514875905454025781[16] = 0;
   out_3514875905454025781[17] = 0;
   out_3514875905454025781[18] = 0;
   out_3514875905454025781[19] = 0;
   out_3514875905454025781[20] = 0;
   out_3514875905454025781[21] = 0;
   out_3514875905454025781[22] = 0;
   out_3514875905454025781[23] = 0;
   out_3514875905454025781[24] = 0;
   out_3514875905454025781[25] = 1;
   out_3514875905454025781[26] = 0;
   out_3514875905454025781[27] = 0;
   out_3514875905454025781[28] = 1;
   out_3514875905454025781[29] = 0;
   out_3514875905454025781[30] = 0;
   out_3514875905454025781[31] = 0;
   out_3514875905454025781[32] = 0;
   out_3514875905454025781[33] = 0;
   out_3514875905454025781[34] = 0;
   out_3514875905454025781[35] = 0;
   out_3514875905454025781[36] = 0;
   out_3514875905454025781[37] = 0;
   out_3514875905454025781[38] = 0;
   out_3514875905454025781[39] = 0;
   out_3514875905454025781[40] = 0;
   out_3514875905454025781[41] = 0;
   out_3514875905454025781[42] = 0;
   out_3514875905454025781[43] = 0;
   out_3514875905454025781[44] = 1;
   out_3514875905454025781[45] = 0;
   out_3514875905454025781[46] = 0;
   out_3514875905454025781[47] = 1;
   out_3514875905454025781[48] = 0;
   out_3514875905454025781[49] = 0;
   out_3514875905454025781[50] = 0;
   out_3514875905454025781[51] = 0;
   out_3514875905454025781[52] = 0;
   out_3514875905454025781[53] = 0;
}
void h_10(double *state, double *unused, double *out_3267969363232743915) {
   out_3267969363232743915[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_3267969363232743915[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_3267969363232743915[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_4777186157283160163) {
   out_4777186157283160163[0] = 0;
   out_4777186157283160163[1] = 9.8100000000000005*cos(state[1]);
   out_4777186157283160163[2] = 0;
   out_4777186157283160163[3] = 0;
   out_4777186157283160163[4] = -state[8];
   out_4777186157283160163[5] = state[7];
   out_4777186157283160163[6] = 0;
   out_4777186157283160163[7] = state[5];
   out_4777186157283160163[8] = -state[4];
   out_4777186157283160163[9] = 0;
   out_4777186157283160163[10] = 0;
   out_4777186157283160163[11] = 0;
   out_4777186157283160163[12] = 1;
   out_4777186157283160163[13] = 0;
   out_4777186157283160163[14] = 0;
   out_4777186157283160163[15] = 1;
   out_4777186157283160163[16] = 0;
   out_4777186157283160163[17] = 0;
   out_4777186157283160163[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_4777186157283160163[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_4777186157283160163[20] = 0;
   out_4777186157283160163[21] = state[8];
   out_4777186157283160163[22] = 0;
   out_4777186157283160163[23] = -state[6];
   out_4777186157283160163[24] = -state[5];
   out_4777186157283160163[25] = 0;
   out_4777186157283160163[26] = state[3];
   out_4777186157283160163[27] = 0;
   out_4777186157283160163[28] = 0;
   out_4777186157283160163[29] = 0;
   out_4777186157283160163[30] = 0;
   out_4777186157283160163[31] = 1;
   out_4777186157283160163[32] = 0;
   out_4777186157283160163[33] = 0;
   out_4777186157283160163[34] = 1;
   out_4777186157283160163[35] = 0;
   out_4777186157283160163[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_4777186157283160163[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_4777186157283160163[38] = 0;
   out_4777186157283160163[39] = -state[7];
   out_4777186157283160163[40] = state[6];
   out_4777186157283160163[41] = 0;
   out_4777186157283160163[42] = state[4];
   out_4777186157283160163[43] = -state[3];
   out_4777186157283160163[44] = 0;
   out_4777186157283160163[45] = 0;
   out_4777186157283160163[46] = 0;
   out_4777186157283160163[47] = 0;
   out_4777186157283160163[48] = 0;
   out_4777186157283160163[49] = 0;
   out_4777186157283160163[50] = 1;
   out_4777186157283160163[51] = 0;
   out_4777186157283160163[52] = 0;
   out_4777186157283160163[53] = 1;
}
void h_13(double *state, double *unused, double *out_8965969219897386723) {
   out_8965969219897386723[0] = state[3];
   out_8965969219897386723[1] = state[4];
   out_8965969219897386723[2] = state[5];
}
void H_13(double *state, double *unused, double *out_318879557848498243) {
   out_318879557848498243[0] = 0;
   out_318879557848498243[1] = 0;
   out_318879557848498243[2] = 0;
   out_318879557848498243[3] = 1;
   out_318879557848498243[4] = 0;
   out_318879557848498243[5] = 0;
   out_318879557848498243[6] = 0;
   out_318879557848498243[7] = 0;
   out_318879557848498243[8] = 0;
   out_318879557848498243[9] = 0;
   out_318879557848498243[10] = 0;
   out_318879557848498243[11] = 0;
   out_318879557848498243[12] = 0;
   out_318879557848498243[13] = 0;
   out_318879557848498243[14] = 0;
   out_318879557848498243[15] = 0;
   out_318879557848498243[16] = 0;
   out_318879557848498243[17] = 0;
   out_318879557848498243[18] = 0;
   out_318879557848498243[19] = 0;
   out_318879557848498243[20] = 0;
   out_318879557848498243[21] = 0;
   out_318879557848498243[22] = 1;
   out_318879557848498243[23] = 0;
   out_318879557848498243[24] = 0;
   out_318879557848498243[25] = 0;
   out_318879557848498243[26] = 0;
   out_318879557848498243[27] = 0;
   out_318879557848498243[28] = 0;
   out_318879557848498243[29] = 0;
   out_318879557848498243[30] = 0;
   out_318879557848498243[31] = 0;
   out_318879557848498243[32] = 0;
   out_318879557848498243[33] = 0;
   out_318879557848498243[34] = 0;
   out_318879557848498243[35] = 0;
   out_318879557848498243[36] = 0;
   out_318879557848498243[37] = 0;
   out_318879557848498243[38] = 0;
   out_318879557848498243[39] = 0;
   out_318879557848498243[40] = 0;
   out_318879557848498243[41] = 1;
   out_318879557848498243[42] = 0;
   out_318879557848498243[43] = 0;
   out_318879557848498243[44] = 0;
   out_318879557848498243[45] = 0;
   out_318879557848498243[46] = 0;
   out_318879557848498243[47] = 0;
   out_318879557848498243[48] = 0;
   out_318879557848498243[49] = 0;
   out_318879557848498243[50] = 0;
   out_318879557848498243[51] = 0;
   out_318879557848498243[52] = 0;
   out_318879557848498243[53] = 0;
}
void h_14(double *state, double *unused, double *out_2613336441508122949) {
   out_2613336441508122949[0] = state[6];
   out_2613336441508122949[1] = state[7];
   out_2613336441508122949[2] = state[8];
}
void H_14(double *state, double *unused, double *out_432087473158653485) {
   out_432087473158653485[0] = 0;
   out_432087473158653485[1] = 0;
   out_432087473158653485[2] = 0;
   out_432087473158653485[3] = 0;
   out_432087473158653485[4] = 0;
   out_432087473158653485[5] = 0;
   out_432087473158653485[6] = 1;
   out_432087473158653485[7] = 0;
   out_432087473158653485[8] = 0;
   out_432087473158653485[9] = 0;
   out_432087473158653485[10] = 0;
   out_432087473158653485[11] = 0;
   out_432087473158653485[12] = 0;
   out_432087473158653485[13] = 0;
   out_432087473158653485[14] = 0;
   out_432087473158653485[15] = 0;
   out_432087473158653485[16] = 0;
   out_432087473158653485[17] = 0;
   out_432087473158653485[18] = 0;
   out_432087473158653485[19] = 0;
   out_432087473158653485[20] = 0;
   out_432087473158653485[21] = 0;
   out_432087473158653485[22] = 0;
   out_432087473158653485[23] = 0;
   out_432087473158653485[24] = 0;
   out_432087473158653485[25] = 1;
   out_432087473158653485[26] = 0;
   out_432087473158653485[27] = 0;
   out_432087473158653485[28] = 0;
   out_432087473158653485[29] = 0;
   out_432087473158653485[30] = 0;
   out_432087473158653485[31] = 0;
   out_432087473158653485[32] = 0;
   out_432087473158653485[33] = 0;
   out_432087473158653485[34] = 0;
   out_432087473158653485[35] = 0;
   out_432087473158653485[36] = 0;
   out_432087473158653485[37] = 0;
   out_432087473158653485[38] = 0;
   out_432087473158653485[39] = 0;
   out_432087473158653485[40] = 0;
   out_432087473158653485[41] = 0;
   out_432087473158653485[42] = 0;
   out_432087473158653485[43] = 0;
   out_432087473158653485[44] = 1;
   out_432087473158653485[45] = 0;
   out_432087473158653485[46] = 0;
   out_432087473158653485[47] = 0;
   out_432087473158653485[48] = 0;
   out_432087473158653485[49] = 0;
   out_432087473158653485[50] = 0;
   out_432087473158653485[51] = 0;
   out_432087473158653485[52] = 0;
   out_432087473158653485[53] = 0;
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
void pose_err_fun(double *nom_x, double *delta_x, double *out_2598376982485037805) {
  err_fun(nom_x, delta_x, out_2598376982485037805);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_4512324947371561180) {
  inv_err_fun(nom_x, true_x, out_4512324947371561180);
}
void pose_H_mod_fun(double *state, double *out_2316928423571127677) {
  H_mod_fun(state, out_2316928423571127677);
}
void pose_f_fun(double *state, double dt, double *out_5656120576541900457) {
  f_fun(state,  dt, out_5656120576541900457);
}
void pose_F_fun(double *state, double dt, double *out_4610640204669690281) {
  F_fun(state,  dt, out_4610640204669690281);
}
void pose_h_4(double *state, double *unused, double *out_1496184824162482188) {
  h_4(state, unused, out_1496184824162482188);
}
void pose_H_4(double *state, double *unused, double *out_3514875905454025781) {
  H_4(state, unused, out_3514875905454025781);
}
void pose_h_10(double *state, double *unused, double *out_3267969363232743915) {
  h_10(state, unused, out_3267969363232743915);
}
void pose_H_10(double *state, double *unused, double *out_4777186157283160163) {
  H_10(state, unused, out_4777186157283160163);
}
void pose_h_13(double *state, double *unused, double *out_8965969219897386723) {
  h_13(state, unused, out_8965969219897386723);
}
void pose_H_13(double *state, double *unused, double *out_318879557848498243) {
  H_13(state, unused, out_318879557848498243);
}
void pose_h_14(double *state, double *unused, double *out_2613336441508122949) {
  h_14(state, unused, out_2613336441508122949);
}
void pose_H_14(double *state, double *unused, double *out_432087473158653485) {
  H_14(state, unused, out_432087473158653485);
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
