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
void err_fun(double *nom_x, double *delta_x, double *out_1350382518294072040) {
   out_1350382518294072040[0] = delta_x[0] + nom_x[0];
   out_1350382518294072040[1] = delta_x[1] + nom_x[1];
   out_1350382518294072040[2] = delta_x[2] + nom_x[2];
   out_1350382518294072040[3] = delta_x[3] + nom_x[3];
   out_1350382518294072040[4] = delta_x[4] + nom_x[4];
   out_1350382518294072040[5] = delta_x[5] + nom_x[5];
   out_1350382518294072040[6] = delta_x[6] + nom_x[6];
   out_1350382518294072040[7] = delta_x[7] + nom_x[7];
   out_1350382518294072040[8] = delta_x[8] + nom_x[8];
   out_1350382518294072040[9] = delta_x[9] + nom_x[9];
   out_1350382518294072040[10] = delta_x[10] + nom_x[10];
   out_1350382518294072040[11] = delta_x[11] + nom_x[11];
   out_1350382518294072040[12] = delta_x[12] + nom_x[12];
   out_1350382518294072040[13] = delta_x[13] + nom_x[13];
   out_1350382518294072040[14] = delta_x[14] + nom_x[14];
   out_1350382518294072040[15] = delta_x[15] + nom_x[15];
   out_1350382518294072040[16] = delta_x[16] + nom_x[16];
   out_1350382518294072040[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_4816619957066290687) {
   out_4816619957066290687[0] = -nom_x[0] + true_x[0];
   out_4816619957066290687[1] = -nom_x[1] + true_x[1];
   out_4816619957066290687[2] = -nom_x[2] + true_x[2];
   out_4816619957066290687[3] = -nom_x[3] + true_x[3];
   out_4816619957066290687[4] = -nom_x[4] + true_x[4];
   out_4816619957066290687[5] = -nom_x[5] + true_x[5];
   out_4816619957066290687[6] = -nom_x[6] + true_x[6];
   out_4816619957066290687[7] = -nom_x[7] + true_x[7];
   out_4816619957066290687[8] = -nom_x[8] + true_x[8];
   out_4816619957066290687[9] = -nom_x[9] + true_x[9];
   out_4816619957066290687[10] = -nom_x[10] + true_x[10];
   out_4816619957066290687[11] = -nom_x[11] + true_x[11];
   out_4816619957066290687[12] = -nom_x[12] + true_x[12];
   out_4816619957066290687[13] = -nom_x[13] + true_x[13];
   out_4816619957066290687[14] = -nom_x[14] + true_x[14];
   out_4816619957066290687[15] = -nom_x[15] + true_x[15];
   out_4816619957066290687[16] = -nom_x[16] + true_x[16];
   out_4816619957066290687[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_6137993433719180276) {
   out_6137993433719180276[0] = 1.0;
   out_6137993433719180276[1] = 0.0;
   out_6137993433719180276[2] = 0.0;
   out_6137993433719180276[3] = 0.0;
   out_6137993433719180276[4] = 0.0;
   out_6137993433719180276[5] = 0.0;
   out_6137993433719180276[6] = 0.0;
   out_6137993433719180276[7] = 0.0;
   out_6137993433719180276[8] = 0.0;
   out_6137993433719180276[9] = 0.0;
   out_6137993433719180276[10] = 0.0;
   out_6137993433719180276[11] = 0.0;
   out_6137993433719180276[12] = 0.0;
   out_6137993433719180276[13] = 0.0;
   out_6137993433719180276[14] = 0.0;
   out_6137993433719180276[15] = 0.0;
   out_6137993433719180276[16] = 0.0;
   out_6137993433719180276[17] = 0.0;
   out_6137993433719180276[18] = 0.0;
   out_6137993433719180276[19] = 1.0;
   out_6137993433719180276[20] = 0.0;
   out_6137993433719180276[21] = 0.0;
   out_6137993433719180276[22] = 0.0;
   out_6137993433719180276[23] = 0.0;
   out_6137993433719180276[24] = 0.0;
   out_6137993433719180276[25] = 0.0;
   out_6137993433719180276[26] = 0.0;
   out_6137993433719180276[27] = 0.0;
   out_6137993433719180276[28] = 0.0;
   out_6137993433719180276[29] = 0.0;
   out_6137993433719180276[30] = 0.0;
   out_6137993433719180276[31] = 0.0;
   out_6137993433719180276[32] = 0.0;
   out_6137993433719180276[33] = 0.0;
   out_6137993433719180276[34] = 0.0;
   out_6137993433719180276[35] = 0.0;
   out_6137993433719180276[36] = 0.0;
   out_6137993433719180276[37] = 0.0;
   out_6137993433719180276[38] = 1.0;
   out_6137993433719180276[39] = 0.0;
   out_6137993433719180276[40] = 0.0;
   out_6137993433719180276[41] = 0.0;
   out_6137993433719180276[42] = 0.0;
   out_6137993433719180276[43] = 0.0;
   out_6137993433719180276[44] = 0.0;
   out_6137993433719180276[45] = 0.0;
   out_6137993433719180276[46] = 0.0;
   out_6137993433719180276[47] = 0.0;
   out_6137993433719180276[48] = 0.0;
   out_6137993433719180276[49] = 0.0;
   out_6137993433719180276[50] = 0.0;
   out_6137993433719180276[51] = 0.0;
   out_6137993433719180276[52] = 0.0;
   out_6137993433719180276[53] = 0.0;
   out_6137993433719180276[54] = 0.0;
   out_6137993433719180276[55] = 0.0;
   out_6137993433719180276[56] = 0.0;
   out_6137993433719180276[57] = 1.0;
   out_6137993433719180276[58] = 0.0;
   out_6137993433719180276[59] = 0.0;
   out_6137993433719180276[60] = 0.0;
   out_6137993433719180276[61] = 0.0;
   out_6137993433719180276[62] = 0.0;
   out_6137993433719180276[63] = 0.0;
   out_6137993433719180276[64] = 0.0;
   out_6137993433719180276[65] = 0.0;
   out_6137993433719180276[66] = 0.0;
   out_6137993433719180276[67] = 0.0;
   out_6137993433719180276[68] = 0.0;
   out_6137993433719180276[69] = 0.0;
   out_6137993433719180276[70] = 0.0;
   out_6137993433719180276[71] = 0.0;
   out_6137993433719180276[72] = 0.0;
   out_6137993433719180276[73] = 0.0;
   out_6137993433719180276[74] = 0.0;
   out_6137993433719180276[75] = 0.0;
   out_6137993433719180276[76] = 1.0;
   out_6137993433719180276[77] = 0.0;
   out_6137993433719180276[78] = 0.0;
   out_6137993433719180276[79] = 0.0;
   out_6137993433719180276[80] = 0.0;
   out_6137993433719180276[81] = 0.0;
   out_6137993433719180276[82] = 0.0;
   out_6137993433719180276[83] = 0.0;
   out_6137993433719180276[84] = 0.0;
   out_6137993433719180276[85] = 0.0;
   out_6137993433719180276[86] = 0.0;
   out_6137993433719180276[87] = 0.0;
   out_6137993433719180276[88] = 0.0;
   out_6137993433719180276[89] = 0.0;
   out_6137993433719180276[90] = 0.0;
   out_6137993433719180276[91] = 0.0;
   out_6137993433719180276[92] = 0.0;
   out_6137993433719180276[93] = 0.0;
   out_6137993433719180276[94] = 0.0;
   out_6137993433719180276[95] = 1.0;
   out_6137993433719180276[96] = 0.0;
   out_6137993433719180276[97] = 0.0;
   out_6137993433719180276[98] = 0.0;
   out_6137993433719180276[99] = 0.0;
   out_6137993433719180276[100] = 0.0;
   out_6137993433719180276[101] = 0.0;
   out_6137993433719180276[102] = 0.0;
   out_6137993433719180276[103] = 0.0;
   out_6137993433719180276[104] = 0.0;
   out_6137993433719180276[105] = 0.0;
   out_6137993433719180276[106] = 0.0;
   out_6137993433719180276[107] = 0.0;
   out_6137993433719180276[108] = 0.0;
   out_6137993433719180276[109] = 0.0;
   out_6137993433719180276[110] = 0.0;
   out_6137993433719180276[111] = 0.0;
   out_6137993433719180276[112] = 0.0;
   out_6137993433719180276[113] = 0.0;
   out_6137993433719180276[114] = 1.0;
   out_6137993433719180276[115] = 0.0;
   out_6137993433719180276[116] = 0.0;
   out_6137993433719180276[117] = 0.0;
   out_6137993433719180276[118] = 0.0;
   out_6137993433719180276[119] = 0.0;
   out_6137993433719180276[120] = 0.0;
   out_6137993433719180276[121] = 0.0;
   out_6137993433719180276[122] = 0.0;
   out_6137993433719180276[123] = 0.0;
   out_6137993433719180276[124] = 0.0;
   out_6137993433719180276[125] = 0.0;
   out_6137993433719180276[126] = 0.0;
   out_6137993433719180276[127] = 0.0;
   out_6137993433719180276[128] = 0.0;
   out_6137993433719180276[129] = 0.0;
   out_6137993433719180276[130] = 0.0;
   out_6137993433719180276[131] = 0.0;
   out_6137993433719180276[132] = 0.0;
   out_6137993433719180276[133] = 1.0;
   out_6137993433719180276[134] = 0.0;
   out_6137993433719180276[135] = 0.0;
   out_6137993433719180276[136] = 0.0;
   out_6137993433719180276[137] = 0.0;
   out_6137993433719180276[138] = 0.0;
   out_6137993433719180276[139] = 0.0;
   out_6137993433719180276[140] = 0.0;
   out_6137993433719180276[141] = 0.0;
   out_6137993433719180276[142] = 0.0;
   out_6137993433719180276[143] = 0.0;
   out_6137993433719180276[144] = 0.0;
   out_6137993433719180276[145] = 0.0;
   out_6137993433719180276[146] = 0.0;
   out_6137993433719180276[147] = 0.0;
   out_6137993433719180276[148] = 0.0;
   out_6137993433719180276[149] = 0.0;
   out_6137993433719180276[150] = 0.0;
   out_6137993433719180276[151] = 0.0;
   out_6137993433719180276[152] = 1.0;
   out_6137993433719180276[153] = 0.0;
   out_6137993433719180276[154] = 0.0;
   out_6137993433719180276[155] = 0.0;
   out_6137993433719180276[156] = 0.0;
   out_6137993433719180276[157] = 0.0;
   out_6137993433719180276[158] = 0.0;
   out_6137993433719180276[159] = 0.0;
   out_6137993433719180276[160] = 0.0;
   out_6137993433719180276[161] = 0.0;
   out_6137993433719180276[162] = 0.0;
   out_6137993433719180276[163] = 0.0;
   out_6137993433719180276[164] = 0.0;
   out_6137993433719180276[165] = 0.0;
   out_6137993433719180276[166] = 0.0;
   out_6137993433719180276[167] = 0.0;
   out_6137993433719180276[168] = 0.0;
   out_6137993433719180276[169] = 0.0;
   out_6137993433719180276[170] = 0.0;
   out_6137993433719180276[171] = 1.0;
   out_6137993433719180276[172] = 0.0;
   out_6137993433719180276[173] = 0.0;
   out_6137993433719180276[174] = 0.0;
   out_6137993433719180276[175] = 0.0;
   out_6137993433719180276[176] = 0.0;
   out_6137993433719180276[177] = 0.0;
   out_6137993433719180276[178] = 0.0;
   out_6137993433719180276[179] = 0.0;
   out_6137993433719180276[180] = 0.0;
   out_6137993433719180276[181] = 0.0;
   out_6137993433719180276[182] = 0.0;
   out_6137993433719180276[183] = 0.0;
   out_6137993433719180276[184] = 0.0;
   out_6137993433719180276[185] = 0.0;
   out_6137993433719180276[186] = 0.0;
   out_6137993433719180276[187] = 0.0;
   out_6137993433719180276[188] = 0.0;
   out_6137993433719180276[189] = 0.0;
   out_6137993433719180276[190] = 1.0;
   out_6137993433719180276[191] = 0.0;
   out_6137993433719180276[192] = 0.0;
   out_6137993433719180276[193] = 0.0;
   out_6137993433719180276[194] = 0.0;
   out_6137993433719180276[195] = 0.0;
   out_6137993433719180276[196] = 0.0;
   out_6137993433719180276[197] = 0.0;
   out_6137993433719180276[198] = 0.0;
   out_6137993433719180276[199] = 0.0;
   out_6137993433719180276[200] = 0.0;
   out_6137993433719180276[201] = 0.0;
   out_6137993433719180276[202] = 0.0;
   out_6137993433719180276[203] = 0.0;
   out_6137993433719180276[204] = 0.0;
   out_6137993433719180276[205] = 0.0;
   out_6137993433719180276[206] = 0.0;
   out_6137993433719180276[207] = 0.0;
   out_6137993433719180276[208] = 0.0;
   out_6137993433719180276[209] = 1.0;
   out_6137993433719180276[210] = 0.0;
   out_6137993433719180276[211] = 0.0;
   out_6137993433719180276[212] = 0.0;
   out_6137993433719180276[213] = 0.0;
   out_6137993433719180276[214] = 0.0;
   out_6137993433719180276[215] = 0.0;
   out_6137993433719180276[216] = 0.0;
   out_6137993433719180276[217] = 0.0;
   out_6137993433719180276[218] = 0.0;
   out_6137993433719180276[219] = 0.0;
   out_6137993433719180276[220] = 0.0;
   out_6137993433719180276[221] = 0.0;
   out_6137993433719180276[222] = 0.0;
   out_6137993433719180276[223] = 0.0;
   out_6137993433719180276[224] = 0.0;
   out_6137993433719180276[225] = 0.0;
   out_6137993433719180276[226] = 0.0;
   out_6137993433719180276[227] = 0.0;
   out_6137993433719180276[228] = 1.0;
   out_6137993433719180276[229] = 0.0;
   out_6137993433719180276[230] = 0.0;
   out_6137993433719180276[231] = 0.0;
   out_6137993433719180276[232] = 0.0;
   out_6137993433719180276[233] = 0.0;
   out_6137993433719180276[234] = 0.0;
   out_6137993433719180276[235] = 0.0;
   out_6137993433719180276[236] = 0.0;
   out_6137993433719180276[237] = 0.0;
   out_6137993433719180276[238] = 0.0;
   out_6137993433719180276[239] = 0.0;
   out_6137993433719180276[240] = 0.0;
   out_6137993433719180276[241] = 0.0;
   out_6137993433719180276[242] = 0.0;
   out_6137993433719180276[243] = 0.0;
   out_6137993433719180276[244] = 0.0;
   out_6137993433719180276[245] = 0.0;
   out_6137993433719180276[246] = 0.0;
   out_6137993433719180276[247] = 1.0;
   out_6137993433719180276[248] = 0.0;
   out_6137993433719180276[249] = 0.0;
   out_6137993433719180276[250] = 0.0;
   out_6137993433719180276[251] = 0.0;
   out_6137993433719180276[252] = 0.0;
   out_6137993433719180276[253] = 0.0;
   out_6137993433719180276[254] = 0.0;
   out_6137993433719180276[255] = 0.0;
   out_6137993433719180276[256] = 0.0;
   out_6137993433719180276[257] = 0.0;
   out_6137993433719180276[258] = 0.0;
   out_6137993433719180276[259] = 0.0;
   out_6137993433719180276[260] = 0.0;
   out_6137993433719180276[261] = 0.0;
   out_6137993433719180276[262] = 0.0;
   out_6137993433719180276[263] = 0.0;
   out_6137993433719180276[264] = 0.0;
   out_6137993433719180276[265] = 0.0;
   out_6137993433719180276[266] = 1.0;
   out_6137993433719180276[267] = 0.0;
   out_6137993433719180276[268] = 0.0;
   out_6137993433719180276[269] = 0.0;
   out_6137993433719180276[270] = 0.0;
   out_6137993433719180276[271] = 0.0;
   out_6137993433719180276[272] = 0.0;
   out_6137993433719180276[273] = 0.0;
   out_6137993433719180276[274] = 0.0;
   out_6137993433719180276[275] = 0.0;
   out_6137993433719180276[276] = 0.0;
   out_6137993433719180276[277] = 0.0;
   out_6137993433719180276[278] = 0.0;
   out_6137993433719180276[279] = 0.0;
   out_6137993433719180276[280] = 0.0;
   out_6137993433719180276[281] = 0.0;
   out_6137993433719180276[282] = 0.0;
   out_6137993433719180276[283] = 0.0;
   out_6137993433719180276[284] = 0.0;
   out_6137993433719180276[285] = 1.0;
   out_6137993433719180276[286] = 0.0;
   out_6137993433719180276[287] = 0.0;
   out_6137993433719180276[288] = 0.0;
   out_6137993433719180276[289] = 0.0;
   out_6137993433719180276[290] = 0.0;
   out_6137993433719180276[291] = 0.0;
   out_6137993433719180276[292] = 0.0;
   out_6137993433719180276[293] = 0.0;
   out_6137993433719180276[294] = 0.0;
   out_6137993433719180276[295] = 0.0;
   out_6137993433719180276[296] = 0.0;
   out_6137993433719180276[297] = 0.0;
   out_6137993433719180276[298] = 0.0;
   out_6137993433719180276[299] = 0.0;
   out_6137993433719180276[300] = 0.0;
   out_6137993433719180276[301] = 0.0;
   out_6137993433719180276[302] = 0.0;
   out_6137993433719180276[303] = 0.0;
   out_6137993433719180276[304] = 1.0;
   out_6137993433719180276[305] = 0.0;
   out_6137993433719180276[306] = 0.0;
   out_6137993433719180276[307] = 0.0;
   out_6137993433719180276[308] = 0.0;
   out_6137993433719180276[309] = 0.0;
   out_6137993433719180276[310] = 0.0;
   out_6137993433719180276[311] = 0.0;
   out_6137993433719180276[312] = 0.0;
   out_6137993433719180276[313] = 0.0;
   out_6137993433719180276[314] = 0.0;
   out_6137993433719180276[315] = 0.0;
   out_6137993433719180276[316] = 0.0;
   out_6137993433719180276[317] = 0.0;
   out_6137993433719180276[318] = 0.0;
   out_6137993433719180276[319] = 0.0;
   out_6137993433719180276[320] = 0.0;
   out_6137993433719180276[321] = 0.0;
   out_6137993433719180276[322] = 0.0;
   out_6137993433719180276[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_8563298307309017918) {
   out_8563298307309017918[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_8563298307309017918[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_8563298307309017918[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_8563298307309017918[3] = dt*state[12] + state[3];
   out_8563298307309017918[4] = dt*state[13] + state[4];
   out_8563298307309017918[5] = dt*state[14] + state[5];
   out_8563298307309017918[6] = state[6];
   out_8563298307309017918[7] = state[7];
   out_8563298307309017918[8] = state[8];
   out_8563298307309017918[9] = state[9];
   out_8563298307309017918[10] = state[10];
   out_8563298307309017918[11] = state[11];
   out_8563298307309017918[12] = state[12];
   out_8563298307309017918[13] = state[13];
   out_8563298307309017918[14] = state[14];
   out_8563298307309017918[15] = state[15];
   out_8563298307309017918[16] = state[16];
   out_8563298307309017918[17] = state[17];
}
void F_fun(double *state, double dt, double *out_6651613570104814248) {
   out_6651613570104814248[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_6651613570104814248[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_6651613570104814248[2] = 0;
   out_6651613570104814248[3] = 0;
   out_6651613570104814248[4] = 0;
   out_6651613570104814248[5] = 0;
   out_6651613570104814248[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_6651613570104814248[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_6651613570104814248[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_6651613570104814248[9] = 0;
   out_6651613570104814248[10] = 0;
   out_6651613570104814248[11] = 0;
   out_6651613570104814248[12] = 0;
   out_6651613570104814248[13] = 0;
   out_6651613570104814248[14] = 0;
   out_6651613570104814248[15] = 0;
   out_6651613570104814248[16] = 0;
   out_6651613570104814248[17] = 0;
   out_6651613570104814248[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_6651613570104814248[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_6651613570104814248[20] = 0;
   out_6651613570104814248[21] = 0;
   out_6651613570104814248[22] = 0;
   out_6651613570104814248[23] = 0;
   out_6651613570104814248[24] = 0;
   out_6651613570104814248[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_6651613570104814248[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_6651613570104814248[27] = 0;
   out_6651613570104814248[28] = 0;
   out_6651613570104814248[29] = 0;
   out_6651613570104814248[30] = 0;
   out_6651613570104814248[31] = 0;
   out_6651613570104814248[32] = 0;
   out_6651613570104814248[33] = 0;
   out_6651613570104814248[34] = 0;
   out_6651613570104814248[35] = 0;
   out_6651613570104814248[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_6651613570104814248[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_6651613570104814248[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_6651613570104814248[39] = 0;
   out_6651613570104814248[40] = 0;
   out_6651613570104814248[41] = 0;
   out_6651613570104814248[42] = 0;
   out_6651613570104814248[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_6651613570104814248[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_6651613570104814248[45] = 0;
   out_6651613570104814248[46] = 0;
   out_6651613570104814248[47] = 0;
   out_6651613570104814248[48] = 0;
   out_6651613570104814248[49] = 0;
   out_6651613570104814248[50] = 0;
   out_6651613570104814248[51] = 0;
   out_6651613570104814248[52] = 0;
   out_6651613570104814248[53] = 0;
   out_6651613570104814248[54] = 0;
   out_6651613570104814248[55] = 0;
   out_6651613570104814248[56] = 0;
   out_6651613570104814248[57] = 1;
   out_6651613570104814248[58] = 0;
   out_6651613570104814248[59] = 0;
   out_6651613570104814248[60] = 0;
   out_6651613570104814248[61] = 0;
   out_6651613570104814248[62] = 0;
   out_6651613570104814248[63] = 0;
   out_6651613570104814248[64] = 0;
   out_6651613570104814248[65] = 0;
   out_6651613570104814248[66] = dt;
   out_6651613570104814248[67] = 0;
   out_6651613570104814248[68] = 0;
   out_6651613570104814248[69] = 0;
   out_6651613570104814248[70] = 0;
   out_6651613570104814248[71] = 0;
   out_6651613570104814248[72] = 0;
   out_6651613570104814248[73] = 0;
   out_6651613570104814248[74] = 0;
   out_6651613570104814248[75] = 0;
   out_6651613570104814248[76] = 1;
   out_6651613570104814248[77] = 0;
   out_6651613570104814248[78] = 0;
   out_6651613570104814248[79] = 0;
   out_6651613570104814248[80] = 0;
   out_6651613570104814248[81] = 0;
   out_6651613570104814248[82] = 0;
   out_6651613570104814248[83] = 0;
   out_6651613570104814248[84] = 0;
   out_6651613570104814248[85] = dt;
   out_6651613570104814248[86] = 0;
   out_6651613570104814248[87] = 0;
   out_6651613570104814248[88] = 0;
   out_6651613570104814248[89] = 0;
   out_6651613570104814248[90] = 0;
   out_6651613570104814248[91] = 0;
   out_6651613570104814248[92] = 0;
   out_6651613570104814248[93] = 0;
   out_6651613570104814248[94] = 0;
   out_6651613570104814248[95] = 1;
   out_6651613570104814248[96] = 0;
   out_6651613570104814248[97] = 0;
   out_6651613570104814248[98] = 0;
   out_6651613570104814248[99] = 0;
   out_6651613570104814248[100] = 0;
   out_6651613570104814248[101] = 0;
   out_6651613570104814248[102] = 0;
   out_6651613570104814248[103] = 0;
   out_6651613570104814248[104] = dt;
   out_6651613570104814248[105] = 0;
   out_6651613570104814248[106] = 0;
   out_6651613570104814248[107] = 0;
   out_6651613570104814248[108] = 0;
   out_6651613570104814248[109] = 0;
   out_6651613570104814248[110] = 0;
   out_6651613570104814248[111] = 0;
   out_6651613570104814248[112] = 0;
   out_6651613570104814248[113] = 0;
   out_6651613570104814248[114] = 1;
   out_6651613570104814248[115] = 0;
   out_6651613570104814248[116] = 0;
   out_6651613570104814248[117] = 0;
   out_6651613570104814248[118] = 0;
   out_6651613570104814248[119] = 0;
   out_6651613570104814248[120] = 0;
   out_6651613570104814248[121] = 0;
   out_6651613570104814248[122] = 0;
   out_6651613570104814248[123] = 0;
   out_6651613570104814248[124] = 0;
   out_6651613570104814248[125] = 0;
   out_6651613570104814248[126] = 0;
   out_6651613570104814248[127] = 0;
   out_6651613570104814248[128] = 0;
   out_6651613570104814248[129] = 0;
   out_6651613570104814248[130] = 0;
   out_6651613570104814248[131] = 0;
   out_6651613570104814248[132] = 0;
   out_6651613570104814248[133] = 1;
   out_6651613570104814248[134] = 0;
   out_6651613570104814248[135] = 0;
   out_6651613570104814248[136] = 0;
   out_6651613570104814248[137] = 0;
   out_6651613570104814248[138] = 0;
   out_6651613570104814248[139] = 0;
   out_6651613570104814248[140] = 0;
   out_6651613570104814248[141] = 0;
   out_6651613570104814248[142] = 0;
   out_6651613570104814248[143] = 0;
   out_6651613570104814248[144] = 0;
   out_6651613570104814248[145] = 0;
   out_6651613570104814248[146] = 0;
   out_6651613570104814248[147] = 0;
   out_6651613570104814248[148] = 0;
   out_6651613570104814248[149] = 0;
   out_6651613570104814248[150] = 0;
   out_6651613570104814248[151] = 0;
   out_6651613570104814248[152] = 1;
   out_6651613570104814248[153] = 0;
   out_6651613570104814248[154] = 0;
   out_6651613570104814248[155] = 0;
   out_6651613570104814248[156] = 0;
   out_6651613570104814248[157] = 0;
   out_6651613570104814248[158] = 0;
   out_6651613570104814248[159] = 0;
   out_6651613570104814248[160] = 0;
   out_6651613570104814248[161] = 0;
   out_6651613570104814248[162] = 0;
   out_6651613570104814248[163] = 0;
   out_6651613570104814248[164] = 0;
   out_6651613570104814248[165] = 0;
   out_6651613570104814248[166] = 0;
   out_6651613570104814248[167] = 0;
   out_6651613570104814248[168] = 0;
   out_6651613570104814248[169] = 0;
   out_6651613570104814248[170] = 0;
   out_6651613570104814248[171] = 1;
   out_6651613570104814248[172] = 0;
   out_6651613570104814248[173] = 0;
   out_6651613570104814248[174] = 0;
   out_6651613570104814248[175] = 0;
   out_6651613570104814248[176] = 0;
   out_6651613570104814248[177] = 0;
   out_6651613570104814248[178] = 0;
   out_6651613570104814248[179] = 0;
   out_6651613570104814248[180] = 0;
   out_6651613570104814248[181] = 0;
   out_6651613570104814248[182] = 0;
   out_6651613570104814248[183] = 0;
   out_6651613570104814248[184] = 0;
   out_6651613570104814248[185] = 0;
   out_6651613570104814248[186] = 0;
   out_6651613570104814248[187] = 0;
   out_6651613570104814248[188] = 0;
   out_6651613570104814248[189] = 0;
   out_6651613570104814248[190] = 1;
   out_6651613570104814248[191] = 0;
   out_6651613570104814248[192] = 0;
   out_6651613570104814248[193] = 0;
   out_6651613570104814248[194] = 0;
   out_6651613570104814248[195] = 0;
   out_6651613570104814248[196] = 0;
   out_6651613570104814248[197] = 0;
   out_6651613570104814248[198] = 0;
   out_6651613570104814248[199] = 0;
   out_6651613570104814248[200] = 0;
   out_6651613570104814248[201] = 0;
   out_6651613570104814248[202] = 0;
   out_6651613570104814248[203] = 0;
   out_6651613570104814248[204] = 0;
   out_6651613570104814248[205] = 0;
   out_6651613570104814248[206] = 0;
   out_6651613570104814248[207] = 0;
   out_6651613570104814248[208] = 0;
   out_6651613570104814248[209] = 1;
   out_6651613570104814248[210] = 0;
   out_6651613570104814248[211] = 0;
   out_6651613570104814248[212] = 0;
   out_6651613570104814248[213] = 0;
   out_6651613570104814248[214] = 0;
   out_6651613570104814248[215] = 0;
   out_6651613570104814248[216] = 0;
   out_6651613570104814248[217] = 0;
   out_6651613570104814248[218] = 0;
   out_6651613570104814248[219] = 0;
   out_6651613570104814248[220] = 0;
   out_6651613570104814248[221] = 0;
   out_6651613570104814248[222] = 0;
   out_6651613570104814248[223] = 0;
   out_6651613570104814248[224] = 0;
   out_6651613570104814248[225] = 0;
   out_6651613570104814248[226] = 0;
   out_6651613570104814248[227] = 0;
   out_6651613570104814248[228] = 1;
   out_6651613570104814248[229] = 0;
   out_6651613570104814248[230] = 0;
   out_6651613570104814248[231] = 0;
   out_6651613570104814248[232] = 0;
   out_6651613570104814248[233] = 0;
   out_6651613570104814248[234] = 0;
   out_6651613570104814248[235] = 0;
   out_6651613570104814248[236] = 0;
   out_6651613570104814248[237] = 0;
   out_6651613570104814248[238] = 0;
   out_6651613570104814248[239] = 0;
   out_6651613570104814248[240] = 0;
   out_6651613570104814248[241] = 0;
   out_6651613570104814248[242] = 0;
   out_6651613570104814248[243] = 0;
   out_6651613570104814248[244] = 0;
   out_6651613570104814248[245] = 0;
   out_6651613570104814248[246] = 0;
   out_6651613570104814248[247] = 1;
   out_6651613570104814248[248] = 0;
   out_6651613570104814248[249] = 0;
   out_6651613570104814248[250] = 0;
   out_6651613570104814248[251] = 0;
   out_6651613570104814248[252] = 0;
   out_6651613570104814248[253] = 0;
   out_6651613570104814248[254] = 0;
   out_6651613570104814248[255] = 0;
   out_6651613570104814248[256] = 0;
   out_6651613570104814248[257] = 0;
   out_6651613570104814248[258] = 0;
   out_6651613570104814248[259] = 0;
   out_6651613570104814248[260] = 0;
   out_6651613570104814248[261] = 0;
   out_6651613570104814248[262] = 0;
   out_6651613570104814248[263] = 0;
   out_6651613570104814248[264] = 0;
   out_6651613570104814248[265] = 0;
   out_6651613570104814248[266] = 1;
   out_6651613570104814248[267] = 0;
   out_6651613570104814248[268] = 0;
   out_6651613570104814248[269] = 0;
   out_6651613570104814248[270] = 0;
   out_6651613570104814248[271] = 0;
   out_6651613570104814248[272] = 0;
   out_6651613570104814248[273] = 0;
   out_6651613570104814248[274] = 0;
   out_6651613570104814248[275] = 0;
   out_6651613570104814248[276] = 0;
   out_6651613570104814248[277] = 0;
   out_6651613570104814248[278] = 0;
   out_6651613570104814248[279] = 0;
   out_6651613570104814248[280] = 0;
   out_6651613570104814248[281] = 0;
   out_6651613570104814248[282] = 0;
   out_6651613570104814248[283] = 0;
   out_6651613570104814248[284] = 0;
   out_6651613570104814248[285] = 1;
   out_6651613570104814248[286] = 0;
   out_6651613570104814248[287] = 0;
   out_6651613570104814248[288] = 0;
   out_6651613570104814248[289] = 0;
   out_6651613570104814248[290] = 0;
   out_6651613570104814248[291] = 0;
   out_6651613570104814248[292] = 0;
   out_6651613570104814248[293] = 0;
   out_6651613570104814248[294] = 0;
   out_6651613570104814248[295] = 0;
   out_6651613570104814248[296] = 0;
   out_6651613570104814248[297] = 0;
   out_6651613570104814248[298] = 0;
   out_6651613570104814248[299] = 0;
   out_6651613570104814248[300] = 0;
   out_6651613570104814248[301] = 0;
   out_6651613570104814248[302] = 0;
   out_6651613570104814248[303] = 0;
   out_6651613570104814248[304] = 1;
   out_6651613570104814248[305] = 0;
   out_6651613570104814248[306] = 0;
   out_6651613570104814248[307] = 0;
   out_6651613570104814248[308] = 0;
   out_6651613570104814248[309] = 0;
   out_6651613570104814248[310] = 0;
   out_6651613570104814248[311] = 0;
   out_6651613570104814248[312] = 0;
   out_6651613570104814248[313] = 0;
   out_6651613570104814248[314] = 0;
   out_6651613570104814248[315] = 0;
   out_6651613570104814248[316] = 0;
   out_6651613570104814248[317] = 0;
   out_6651613570104814248[318] = 0;
   out_6651613570104814248[319] = 0;
   out_6651613570104814248[320] = 0;
   out_6651613570104814248[321] = 0;
   out_6651613570104814248[322] = 0;
   out_6651613570104814248[323] = 1;
}
void h_4(double *state, double *unused, double *out_3971641468391678980) {
   out_3971641468391678980[0] = state[6] + state[9];
   out_3971641468391678980[1] = state[7] + state[10];
   out_3971641468391678980[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_8716652090797251543) {
   out_8716652090797251543[0] = 0;
   out_8716652090797251543[1] = 0;
   out_8716652090797251543[2] = 0;
   out_8716652090797251543[3] = 0;
   out_8716652090797251543[4] = 0;
   out_8716652090797251543[5] = 0;
   out_8716652090797251543[6] = 1;
   out_8716652090797251543[7] = 0;
   out_8716652090797251543[8] = 0;
   out_8716652090797251543[9] = 1;
   out_8716652090797251543[10] = 0;
   out_8716652090797251543[11] = 0;
   out_8716652090797251543[12] = 0;
   out_8716652090797251543[13] = 0;
   out_8716652090797251543[14] = 0;
   out_8716652090797251543[15] = 0;
   out_8716652090797251543[16] = 0;
   out_8716652090797251543[17] = 0;
   out_8716652090797251543[18] = 0;
   out_8716652090797251543[19] = 0;
   out_8716652090797251543[20] = 0;
   out_8716652090797251543[21] = 0;
   out_8716652090797251543[22] = 0;
   out_8716652090797251543[23] = 0;
   out_8716652090797251543[24] = 0;
   out_8716652090797251543[25] = 1;
   out_8716652090797251543[26] = 0;
   out_8716652090797251543[27] = 0;
   out_8716652090797251543[28] = 1;
   out_8716652090797251543[29] = 0;
   out_8716652090797251543[30] = 0;
   out_8716652090797251543[31] = 0;
   out_8716652090797251543[32] = 0;
   out_8716652090797251543[33] = 0;
   out_8716652090797251543[34] = 0;
   out_8716652090797251543[35] = 0;
   out_8716652090797251543[36] = 0;
   out_8716652090797251543[37] = 0;
   out_8716652090797251543[38] = 0;
   out_8716652090797251543[39] = 0;
   out_8716652090797251543[40] = 0;
   out_8716652090797251543[41] = 0;
   out_8716652090797251543[42] = 0;
   out_8716652090797251543[43] = 0;
   out_8716652090797251543[44] = 1;
   out_8716652090797251543[45] = 0;
   out_8716652090797251543[46] = 0;
   out_8716652090797251543[47] = 1;
   out_8716652090797251543[48] = 0;
   out_8716652090797251543[49] = 0;
   out_8716652090797251543[50] = 0;
   out_8716652090797251543[51] = 0;
   out_8716652090797251543[52] = 0;
   out_8716652090797251543[53] = 0;
}
void h_10(double *state, double *unused, double *out_9093229976132518865) {
   out_9093229976132518865[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_9093229976132518865[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_9093229976132518865[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_943400041793457972) {
   out_943400041793457972[0] = 0;
   out_943400041793457972[1] = 9.8100000000000005*cos(state[1]);
   out_943400041793457972[2] = 0;
   out_943400041793457972[3] = 0;
   out_943400041793457972[4] = -state[8];
   out_943400041793457972[5] = state[7];
   out_943400041793457972[6] = 0;
   out_943400041793457972[7] = state[5];
   out_943400041793457972[8] = -state[4];
   out_943400041793457972[9] = 0;
   out_943400041793457972[10] = 0;
   out_943400041793457972[11] = 0;
   out_943400041793457972[12] = 1;
   out_943400041793457972[13] = 0;
   out_943400041793457972[14] = 0;
   out_943400041793457972[15] = 1;
   out_943400041793457972[16] = 0;
   out_943400041793457972[17] = 0;
   out_943400041793457972[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_943400041793457972[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_943400041793457972[20] = 0;
   out_943400041793457972[21] = state[8];
   out_943400041793457972[22] = 0;
   out_943400041793457972[23] = -state[6];
   out_943400041793457972[24] = -state[5];
   out_943400041793457972[25] = 0;
   out_943400041793457972[26] = state[3];
   out_943400041793457972[27] = 0;
   out_943400041793457972[28] = 0;
   out_943400041793457972[29] = 0;
   out_943400041793457972[30] = 0;
   out_943400041793457972[31] = 1;
   out_943400041793457972[32] = 0;
   out_943400041793457972[33] = 0;
   out_943400041793457972[34] = 1;
   out_943400041793457972[35] = 0;
   out_943400041793457972[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_943400041793457972[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_943400041793457972[38] = 0;
   out_943400041793457972[39] = -state[7];
   out_943400041793457972[40] = state[6];
   out_943400041793457972[41] = 0;
   out_943400041793457972[42] = state[4];
   out_943400041793457972[43] = -state[3];
   out_943400041793457972[44] = 0;
   out_943400041793457972[45] = 0;
   out_943400041793457972[46] = 0;
   out_943400041793457972[47] = 0;
   out_943400041793457972[48] = 0;
   out_943400041793457972[49] = 0;
   out_943400041793457972[50] = 1;
   out_943400041793457972[51] = 0;
   out_943400041793457972[52] = 0;
   out_943400041793457972[53] = 1;
}
void h_13(double *state, double *unused, double *out_3008735883514341503) {
   out_3008735883514341503[0] = state[3];
   out_3008735883514341503[1] = state[4];
   out_3008735883514341503[2] = state[5];
}
void H_13(double *state, double *unused, double *out_6517818157579967272) {
   out_6517818157579967272[0] = 0;
   out_6517818157579967272[1] = 0;
   out_6517818157579967272[2] = 0;
   out_6517818157579967272[3] = 1;
   out_6517818157579967272[4] = 0;
   out_6517818157579967272[5] = 0;
   out_6517818157579967272[6] = 0;
   out_6517818157579967272[7] = 0;
   out_6517818157579967272[8] = 0;
   out_6517818157579967272[9] = 0;
   out_6517818157579967272[10] = 0;
   out_6517818157579967272[11] = 0;
   out_6517818157579967272[12] = 0;
   out_6517818157579967272[13] = 0;
   out_6517818157579967272[14] = 0;
   out_6517818157579967272[15] = 0;
   out_6517818157579967272[16] = 0;
   out_6517818157579967272[17] = 0;
   out_6517818157579967272[18] = 0;
   out_6517818157579967272[19] = 0;
   out_6517818157579967272[20] = 0;
   out_6517818157579967272[21] = 0;
   out_6517818157579967272[22] = 1;
   out_6517818157579967272[23] = 0;
   out_6517818157579967272[24] = 0;
   out_6517818157579967272[25] = 0;
   out_6517818157579967272[26] = 0;
   out_6517818157579967272[27] = 0;
   out_6517818157579967272[28] = 0;
   out_6517818157579967272[29] = 0;
   out_6517818157579967272[30] = 0;
   out_6517818157579967272[31] = 0;
   out_6517818157579967272[32] = 0;
   out_6517818157579967272[33] = 0;
   out_6517818157579967272[34] = 0;
   out_6517818157579967272[35] = 0;
   out_6517818157579967272[36] = 0;
   out_6517818157579967272[37] = 0;
   out_6517818157579967272[38] = 0;
   out_6517818157579967272[39] = 0;
   out_6517818157579967272[40] = 0;
   out_6517818157579967272[41] = 1;
   out_6517818157579967272[42] = 0;
   out_6517818157579967272[43] = 0;
   out_6517818157579967272[44] = 0;
   out_6517818157579967272[45] = 0;
   out_6517818157579967272[46] = 0;
   out_6517818157579967272[47] = 0;
   out_6517818157579967272[48] = 0;
   out_6517818157579967272[49] = 0;
   out_6517818157579967272[50] = 0;
   out_6517818157579967272[51] = 0;
   out_6517818157579967272[52] = 0;
   out_6517818157579967272[53] = 0;
}
void h_14(double *state, double *unused, double *out_879287342420246227) {
   out_879287342420246227[0] = state[6];
   out_879287342420246227[1] = state[7];
   out_879287342420246227[2] = state[8];
}
void H_14(double *state, double *unused, double *out_5766851126572815544) {
   out_5766851126572815544[0] = 0;
   out_5766851126572815544[1] = 0;
   out_5766851126572815544[2] = 0;
   out_5766851126572815544[3] = 0;
   out_5766851126572815544[4] = 0;
   out_5766851126572815544[5] = 0;
   out_5766851126572815544[6] = 1;
   out_5766851126572815544[7] = 0;
   out_5766851126572815544[8] = 0;
   out_5766851126572815544[9] = 0;
   out_5766851126572815544[10] = 0;
   out_5766851126572815544[11] = 0;
   out_5766851126572815544[12] = 0;
   out_5766851126572815544[13] = 0;
   out_5766851126572815544[14] = 0;
   out_5766851126572815544[15] = 0;
   out_5766851126572815544[16] = 0;
   out_5766851126572815544[17] = 0;
   out_5766851126572815544[18] = 0;
   out_5766851126572815544[19] = 0;
   out_5766851126572815544[20] = 0;
   out_5766851126572815544[21] = 0;
   out_5766851126572815544[22] = 0;
   out_5766851126572815544[23] = 0;
   out_5766851126572815544[24] = 0;
   out_5766851126572815544[25] = 1;
   out_5766851126572815544[26] = 0;
   out_5766851126572815544[27] = 0;
   out_5766851126572815544[28] = 0;
   out_5766851126572815544[29] = 0;
   out_5766851126572815544[30] = 0;
   out_5766851126572815544[31] = 0;
   out_5766851126572815544[32] = 0;
   out_5766851126572815544[33] = 0;
   out_5766851126572815544[34] = 0;
   out_5766851126572815544[35] = 0;
   out_5766851126572815544[36] = 0;
   out_5766851126572815544[37] = 0;
   out_5766851126572815544[38] = 0;
   out_5766851126572815544[39] = 0;
   out_5766851126572815544[40] = 0;
   out_5766851126572815544[41] = 0;
   out_5766851126572815544[42] = 0;
   out_5766851126572815544[43] = 0;
   out_5766851126572815544[44] = 1;
   out_5766851126572815544[45] = 0;
   out_5766851126572815544[46] = 0;
   out_5766851126572815544[47] = 0;
   out_5766851126572815544[48] = 0;
   out_5766851126572815544[49] = 0;
   out_5766851126572815544[50] = 0;
   out_5766851126572815544[51] = 0;
   out_5766851126572815544[52] = 0;
   out_5766851126572815544[53] = 0;
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
void pose_err_fun(double *nom_x, double *delta_x, double *out_1350382518294072040) {
  err_fun(nom_x, delta_x, out_1350382518294072040);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_4816619957066290687) {
  inv_err_fun(nom_x, true_x, out_4816619957066290687);
}
void pose_H_mod_fun(double *state, double *out_6137993433719180276) {
  H_mod_fun(state, out_6137993433719180276);
}
void pose_f_fun(double *state, double dt, double *out_8563298307309017918) {
  f_fun(state,  dt, out_8563298307309017918);
}
void pose_F_fun(double *state, double dt, double *out_6651613570104814248) {
  F_fun(state,  dt, out_6651613570104814248);
}
void pose_h_4(double *state, double *unused, double *out_3971641468391678980) {
  h_4(state, unused, out_3971641468391678980);
}
void pose_H_4(double *state, double *unused, double *out_8716652090797251543) {
  H_4(state, unused, out_8716652090797251543);
}
void pose_h_10(double *state, double *unused, double *out_9093229976132518865) {
  h_10(state, unused, out_9093229976132518865);
}
void pose_H_10(double *state, double *unused, double *out_943400041793457972) {
  H_10(state, unused, out_943400041793457972);
}
void pose_h_13(double *state, double *unused, double *out_3008735883514341503) {
  h_13(state, unused, out_3008735883514341503);
}
void pose_H_13(double *state, double *unused, double *out_6517818157579967272) {
  H_13(state, unused, out_6517818157579967272);
}
void pose_h_14(double *state, double *unused, double *out_879287342420246227) {
  h_14(state, unused, out_879287342420246227);
}
void pose_H_14(double *state, double *unused, double *out_5766851126572815544) {
  H_14(state, unused, out_5766851126572815544);
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
