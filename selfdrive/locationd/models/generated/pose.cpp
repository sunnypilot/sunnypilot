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
void err_fun(double *nom_x, double *delta_x, double *out_7849211930432319310) {
   out_7849211930432319310[0] = delta_x[0] + nom_x[0];
   out_7849211930432319310[1] = delta_x[1] + nom_x[1];
   out_7849211930432319310[2] = delta_x[2] + nom_x[2];
   out_7849211930432319310[3] = delta_x[3] + nom_x[3];
   out_7849211930432319310[4] = delta_x[4] + nom_x[4];
   out_7849211930432319310[5] = delta_x[5] + nom_x[5];
   out_7849211930432319310[6] = delta_x[6] + nom_x[6];
   out_7849211930432319310[7] = delta_x[7] + nom_x[7];
   out_7849211930432319310[8] = delta_x[8] + nom_x[8];
   out_7849211930432319310[9] = delta_x[9] + nom_x[9];
   out_7849211930432319310[10] = delta_x[10] + nom_x[10];
   out_7849211930432319310[11] = delta_x[11] + nom_x[11];
   out_7849211930432319310[12] = delta_x[12] + nom_x[12];
   out_7849211930432319310[13] = delta_x[13] + nom_x[13];
   out_7849211930432319310[14] = delta_x[14] + nom_x[14];
   out_7849211930432319310[15] = delta_x[15] + nom_x[15];
   out_7849211930432319310[16] = delta_x[16] + nom_x[16];
   out_7849211930432319310[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_4938013129047494051) {
   out_4938013129047494051[0] = -nom_x[0] + true_x[0];
   out_4938013129047494051[1] = -nom_x[1] + true_x[1];
   out_4938013129047494051[2] = -nom_x[2] + true_x[2];
   out_4938013129047494051[3] = -nom_x[3] + true_x[3];
   out_4938013129047494051[4] = -nom_x[4] + true_x[4];
   out_4938013129047494051[5] = -nom_x[5] + true_x[5];
   out_4938013129047494051[6] = -nom_x[6] + true_x[6];
   out_4938013129047494051[7] = -nom_x[7] + true_x[7];
   out_4938013129047494051[8] = -nom_x[8] + true_x[8];
   out_4938013129047494051[9] = -nom_x[9] + true_x[9];
   out_4938013129047494051[10] = -nom_x[10] + true_x[10];
   out_4938013129047494051[11] = -nom_x[11] + true_x[11];
   out_4938013129047494051[12] = -nom_x[12] + true_x[12];
   out_4938013129047494051[13] = -nom_x[13] + true_x[13];
   out_4938013129047494051[14] = -nom_x[14] + true_x[14];
   out_4938013129047494051[15] = -nom_x[15] + true_x[15];
   out_4938013129047494051[16] = -nom_x[16] + true_x[16];
   out_4938013129047494051[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_4310619498118974873) {
   out_4310619498118974873[0] = 1.0;
   out_4310619498118974873[1] = 0.0;
   out_4310619498118974873[2] = 0.0;
   out_4310619498118974873[3] = 0.0;
   out_4310619498118974873[4] = 0.0;
   out_4310619498118974873[5] = 0.0;
   out_4310619498118974873[6] = 0.0;
   out_4310619498118974873[7] = 0.0;
   out_4310619498118974873[8] = 0.0;
   out_4310619498118974873[9] = 0.0;
   out_4310619498118974873[10] = 0.0;
   out_4310619498118974873[11] = 0.0;
   out_4310619498118974873[12] = 0.0;
   out_4310619498118974873[13] = 0.0;
   out_4310619498118974873[14] = 0.0;
   out_4310619498118974873[15] = 0.0;
   out_4310619498118974873[16] = 0.0;
   out_4310619498118974873[17] = 0.0;
   out_4310619498118974873[18] = 0.0;
   out_4310619498118974873[19] = 1.0;
   out_4310619498118974873[20] = 0.0;
   out_4310619498118974873[21] = 0.0;
   out_4310619498118974873[22] = 0.0;
   out_4310619498118974873[23] = 0.0;
   out_4310619498118974873[24] = 0.0;
   out_4310619498118974873[25] = 0.0;
   out_4310619498118974873[26] = 0.0;
   out_4310619498118974873[27] = 0.0;
   out_4310619498118974873[28] = 0.0;
   out_4310619498118974873[29] = 0.0;
   out_4310619498118974873[30] = 0.0;
   out_4310619498118974873[31] = 0.0;
   out_4310619498118974873[32] = 0.0;
   out_4310619498118974873[33] = 0.0;
   out_4310619498118974873[34] = 0.0;
   out_4310619498118974873[35] = 0.0;
   out_4310619498118974873[36] = 0.0;
   out_4310619498118974873[37] = 0.0;
   out_4310619498118974873[38] = 1.0;
   out_4310619498118974873[39] = 0.0;
   out_4310619498118974873[40] = 0.0;
   out_4310619498118974873[41] = 0.0;
   out_4310619498118974873[42] = 0.0;
   out_4310619498118974873[43] = 0.0;
   out_4310619498118974873[44] = 0.0;
   out_4310619498118974873[45] = 0.0;
   out_4310619498118974873[46] = 0.0;
   out_4310619498118974873[47] = 0.0;
   out_4310619498118974873[48] = 0.0;
   out_4310619498118974873[49] = 0.0;
   out_4310619498118974873[50] = 0.0;
   out_4310619498118974873[51] = 0.0;
   out_4310619498118974873[52] = 0.0;
   out_4310619498118974873[53] = 0.0;
   out_4310619498118974873[54] = 0.0;
   out_4310619498118974873[55] = 0.0;
   out_4310619498118974873[56] = 0.0;
   out_4310619498118974873[57] = 1.0;
   out_4310619498118974873[58] = 0.0;
   out_4310619498118974873[59] = 0.0;
   out_4310619498118974873[60] = 0.0;
   out_4310619498118974873[61] = 0.0;
   out_4310619498118974873[62] = 0.0;
   out_4310619498118974873[63] = 0.0;
   out_4310619498118974873[64] = 0.0;
   out_4310619498118974873[65] = 0.0;
   out_4310619498118974873[66] = 0.0;
   out_4310619498118974873[67] = 0.0;
   out_4310619498118974873[68] = 0.0;
   out_4310619498118974873[69] = 0.0;
   out_4310619498118974873[70] = 0.0;
   out_4310619498118974873[71] = 0.0;
   out_4310619498118974873[72] = 0.0;
   out_4310619498118974873[73] = 0.0;
   out_4310619498118974873[74] = 0.0;
   out_4310619498118974873[75] = 0.0;
   out_4310619498118974873[76] = 1.0;
   out_4310619498118974873[77] = 0.0;
   out_4310619498118974873[78] = 0.0;
   out_4310619498118974873[79] = 0.0;
   out_4310619498118974873[80] = 0.0;
   out_4310619498118974873[81] = 0.0;
   out_4310619498118974873[82] = 0.0;
   out_4310619498118974873[83] = 0.0;
   out_4310619498118974873[84] = 0.0;
   out_4310619498118974873[85] = 0.0;
   out_4310619498118974873[86] = 0.0;
   out_4310619498118974873[87] = 0.0;
   out_4310619498118974873[88] = 0.0;
   out_4310619498118974873[89] = 0.0;
   out_4310619498118974873[90] = 0.0;
   out_4310619498118974873[91] = 0.0;
   out_4310619498118974873[92] = 0.0;
   out_4310619498118974873[93] = 0.0;
   out_4310619498118974873[94] = 0.0;
   out_4310619498118974873[95] = 1.0;
   out_4310619498118974873[96] = 0.0;
   out_4310619498118974873[97] = 0.0;
   out_4310619498118974873[98] = 0.0;
   out_4310619498118974873[99] = 0.0;
   out_4310619498118974873[100] = 0.0;
   out_4310619498118974873[101] = 0.0;
   out_4310619498118974873[102] = 0.0;
   out_4310619498118974873[103] = 0.0;
   out_4310619498118974873[104] = 0.0;
   out_4310619498118974873[105] = 0.0;
   out_4310619498118974873[106] = 0.0;
   out_4310619498118974873[107] = 0.0;
   out_4310619498118974873[108] = 0.0;
   out_4310619498118974873[109] = 0.0;
   out_4310619498118974873[110] = 0.0;
   out_4310619498118974873[111] = 0.0;
   out_4310619498118974873[112] = 0.0;
   out_4310619498118974873[113] = 0.0;
   out_4310619498118974873[114] = 1.0;
   out_4310619498118974873[115] = 0.0;
   out_4310619498118974873[116] = 0.0;
   out_4310619498118974873[117] = 0.0;
   out_4310619498118974873[118] = 0.0;
   out_4310619498118974873[119] = 0.0;
   out_4310619498118974873[120] = 0.0;
   out_4310619498118974873[121] = 0.0;
   out_4310619498118974873[122] = 0.0;
   out_4310619498118974873[123] = 0.0;
   out_4310619498118974873[124] = 0.0;
   out_4310619498118974873[125] = 0.0;
   out_4310619498118974873[126] = 0.0;
   out_4310619498118974873[127] = 0.0;
   out_4310619498118974873[128] = 0.0;
   out_4310619498118974873[129] = 0.0;
   out_4310619498118974873[130] = 0.0;
   out_4310619498118974873[131] = 0.0;
   out_4310619498118974873[132] = 0.0;
   out_4310619498118974873[133] = 1.0;
   out_4310619498118974873[134] = 0.0;
   out_4310619498118974873[135] = 0.0;
   out_4310619498118974873[136] = 0.0;
   out_4310619498118974873[137] = 0.0;
   out_4310619498118974873[138] = 0.0;
   out_4310619498118974873[139] = 0.0;
   out_4310619498118974873[140] = 0.0;
   out_4310619498118974873[141] = 0.0;
   out_4310619498118974873[142] = 0.0;
   out_4310619498118974873[143] = 0.0;
   out_4310619498118974873[144] = 0.0;
   out_4310619498118974873[145] = 0.0;
   out_4310619498118974873[146] = 0.0;
   out_4310619498118974873[147] = 0.0;
   out_4310619498118974873[148] = 0.0;
   out_4310619498118974873[149] = 0.0;
   out_4310619498118974873[150] = 0.0;
   out_4310619498118974873[151] = 0.0;
   out_4310619498118974873[152] = 1.0;
   out_4310619498118974873[153] = 0.0;
   out_4310619498118974873[154] = 0.0;
   out_4310619498118974873[155] = 0.0;
   out_4310619498118974873[156] = 0.0;
   out_4310619498118974873[157] = 0.0;
   out_4310619498118974873[158] = 0.0;
   out_4310619498118974873[159] = 0.0;
   out_4310619498118974873[160] = 0.0;
   out_4310619498118974873[161] = 0.0;
   out_4310619498118974873[162] = 0.0;
   out_4310619498118974873[163] = 0.0;
   out_4310619498118974873[164] = 0.0;
   out_4310619498118974873[165] = 0.0;
   out_4310619498118974873[166] = 0.0;
   out_4310619498118974873[167] = 0.0;
   out_4310619498118974873[168] = 0.0;
   out_4310619498118974873[169] = 0.0;
   out_4310619498118974873[170] = 0.0;
   out_4310619498118974873[171] = 1.0;
   out_4310619498118974873[172] = 0.0;
   out_4310619498118974873[173] = 0.0;
   out_4310619498118974873[174] = 0.0;
   out_4310619498118974873[175] = 0.0;
   out_4310619498118974873[176] = 0.0;
   out_4310619498118974873[177] = 0.0;
   out_4310619498118974873[178] = 0.0;
   out_4310619498118974873[179] = 0.0;
   out_4310619498118974873[180] = 0.0;
   out_4310619498118974873[181] = 0.0;
   out_4310619498118974873[182] = 0.0;
   out_4310619498118974873[183] = 0.0;
   out_4310619498118974873[184] = 0.0;
   out_4310619498118974873[185] = 0.0;
   out_4310619498118974873[186] = 0.0;
   out_4310619498118974873[187] = 0.0;
   out_4310619498118974873[188] = 0.0;
   out_4310619498118974873[189] = 0.0;
   out_4310619498118974873[190] = 1.0;
   out_4310619498118974873[191] = 0.0;
   out_4310619498118974873[192] = 0.0;
   out_4310619498118974873[193] = 0.0;
   out_4310619498118974873[194] = 0.0;
   out_4310619498118974873[195] = 0.0;
   out_4310619498118974873[196] = 0.0;
   out_4310619498118974873[197] = 0.0;
   out_4310619498118974873[198] = 0.0;
   out_4310619498118974873[199] = 0.0;
   out_4310619498118974873[200] = 0.0;
   out_4310619498118974873[201] = 0.0;
   out_4310619498118974873[202] = 0.0;
   out_4310619498118974873[203] = 0.0;
   out_4310619498118974873[204] = 0.0;
   out_4310619498118974873[205] = 0.0;
   out_4310619498118974873[206] = 0.0;
   out_4310619498118974873[207] = 0.0;
   out_4310619498118974873[208] = 0.0;
   out_4310619498118974873[209] = 1.0;
   out_4310619498118974873[210] = 0.0;
   out_4310619498118974873[211] = 0.0;
   out_4310619498118974873[212] = 0.0;
   out_4310619498118974873[213] = 0.0;
   out_4310619498118974873[214] = 0.0;
   out_4310619498118974873[215] = 0.0;
   out_4310619498118974873[216] = 0.0;
   out_4310619498118974873[217] = 0.0;
   out_4310619498118974873[218] = 0.0;
   out_4310619498118974873[219] = 0.0;
   out_4310619498118974873[220] = 0.0;
   out_4310619498118974873[221] = 0.0;
   out_4310619498118974873[222] = 0.0;
   out_4310619498118974873[223] = 0.0;
   out_4310619498118974873[224] = 0.0;
   out_4310619498118974873[225] = 0.0;
   out_4310619498118974873[226] = 0.0;
   out_4310619498118974873[227] = 0.0;
   out_4310619498118974873[228] = 1.0;
   out_4310619498118974873[229] = 0.0;
   out_4310619498118974873[230] = 0.0;
   out_4310619498118974873[231] = 0.0;
   out_4310619498118974873[232] = 0.0;
   out_4310619498118974873[233] = 0.0;
   out_4310619498118974873[234] = 0.0;
   out_4310619498118974873[235] = 0.0;
   out_4310619498118974873[236] = 0.0;
   out_4310619498118974873[237] = 0.0;
   out_4310619498118974873[238] = 0.0;
   out_4310619498118974873[239] = 0.0;
   out_4310619498118974873[240] = 0.0;
   out_4310619498118974873[241] = 0.0;
   out_4310619498118974873[242] = 0.0;
   out_4310619498118974873[243] = 0.0;
   out_4310619498118974873[244] = 0.0;
   out_4310619498118974873[245] = 0.0;
   out_4310619498118974873[246] = 0.0;
   out_4310619498118974873[247] = 1.0;
   out_4310619498118974873[248] = 0.0;
   out_4310619498118974873[249] = 0.0;
   out_4310619498118974873[250] = 0.0;
   out_4310619498118974873[251] = 0.0;
   out_4310619498118974873[252] = 0.0;
   out_4310619498118974873[253] = 0.0;
   out_4310619498118974873[254] = 0.0;
   out_4310619498118974873[255] = 0.0;
   out_4310619498118974873[256] = 0.0;
   out_4310619498118974873[257] = 0.0;
   out_4310619498118974873[258] = 0.0;
   out_4310619498118974873[259] = 0.0;
   out_4310619498118974873[260] = 0.0;
   out_4310619498118974873[261] = 0.0;
   out_4310619498118974873[262] = 0.0;
   out_4310619498118974873[263] = 0.0;
   out_4310619498118974873[264] = 0.0;
   out_4310619498118974873[265] = 0.0;
   out_4310619498118974873[266] = 1.0;
   out_4310619498118974873[267] = 0.0;
   out_4310619498118974873[268] = 0.0;
   out_4310619498118974873[269] = 0.0;
   out_4310619498118974873[270] = 0.0;
   out_4310619498118974873[271] = 0.0;
   out_4310619498118974873[272] = 0.0;
   out_4310619498118974873[273] = 0.0;
   out_4310619498118974873[274] = 0.0;
   out_4310619498118974873[275] = 0.0;
   out_4310619498118974873[276] = 0.0;
   out_4310619498118974873[277] = 0.0;
   out_4310619498118974873[278] = 0.0;
   out_4310619498118974873[279] = 0.0;
   out_4310619498118974873[280] = 0.0;
   out_4310619498118974873[281] = 0.0;
   out_4310619498118974873[282] = 0.0;
   out_4310619498118974873[283] = 0.0;
   out_4310619498118974873[284] = 0.0;
   out_4310619498118974873[285] = 1.0;
   out_4310619498118974873[286] = 0.0;
   out_4310619498118974873[287] = 0.0;
   out_4310619498118974873[288] = 0.0;
   out_4310619498118974873[289] = 0.0;
   out_4310619498118974873[290] = 0.0;
   out_4310619498118974873[291] = 0.0;
   out_4310619498118974873[292] = 0.0;
   out_4310619498118974873[293] = 0.0;
   out_4310619498118974873[294] = 0.0;
   out_4310619498118974873[295] = 0.0;
   out_4310619498118974873[296] = 0.0;
   out_4310619498118974873[297] = 0.0;
   out_4310619498118974873[298] = 0.0;
   out_4310619498118974873[299] = 0.0;
   out_4310619498118974873[300] = 0.0;
   out_4310619498118974873[301] = 0.0;
   out_4310619498118974873[302] = 0.0;
   out_4310619498118974873[303] = 0.0;
   out_4310619498118974873[304] = 1.0;
   out_4310619498118974873[305] = 0.0;
   out_4310619498118974873[306] = 0.0;
   out_4310619498118974873[307] = 0.0;
   out_4310619498118974873[308] = 0.0;
   out_4310619498118974873[309] = 0.0;
   out_4310619498118974873[310] = 0.0;
   out_4310619498118974873[311] = 0.0;
   out_4310619498118974873[312] = 0.0;
   out_4310619498118974873[313] = 0.0;
   out_4310619498118974873[314] = 0.0;
   out_4310619498118974873[315] = 0.0;
   out_4310619498118974873[316] = 0.0;
   out_4310619498118974873[317] = 0.0;
   out_4310619498118974873[318] = 0.0;
   out_4310619498118974873[319] = 0.0;
   out_4310619498118974873[320] = 0.0;
   out_4310619498118974873[321] = 0.0;
   out_4310619498118974873[322] = 0.0;
   out_4310619498118974873[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_1974982568906725041) {
   out_1974982568906725041[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_1974982568906725041[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_1974982568906725041[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_1974982568906725041[3] = dt*state[12] + state[3];
   out_1974982568906725041[4] = dt*state[13] + state[4];
   out_1974982568906725041[5] = dt*state[14] + state[5];
   out_1974982568906725041[6] = state[6];
   out_1974982568906725041[7] = state[7];
   out_1974982568906725041[8] = state[8];
   out_1974982568906725041[9] = state[9];
   out_1974982568906725041[10] = state[10];
   out_1974982568906725041[11] = state[11];
   out_1974982568906725041[12] = state[12];
   out_1974982568906725041[13] = state[13];
   out_1974982568906725041[14] = state[14];
   out_1974982568906725041[15] = state[15];
   out_1974982568906725041[16] = state[16];
   out_1974982568906725041[17] = state[17];
}
void F_fun(double *state, double dt, double *out_6575454721087425774) {
   out_6575454721087425774[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_6575454721087425774[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_6575454721087425774[2] = 0;
   out_6575454721087425774[3] = 0;
   out_6575454721087425774[4] = 0;
   out_6575454721087425774[5] = 0;
   out_6575454721087425774[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_6575454721087425774[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_6575454721087425774[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_6575454721087425774[9] = 0;
   out_6575454721087425774[10] = 0;
   out_6575454721087425774[11] = 0;
   out_6575454721087425774[12] = 0;
   out_6575454721087425774[13] = 0;
   out_6575454721087425774[14] = 0;
   out_6575454721087425774[15] = 0;
   out_6575454721087425774[16] = 0;
   out_6575454721087425774[17] = 0;
   out_6575454721087425774[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_6575454721087425774[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_6575454721087425774[20] = 0;
   out_6575454721087425774[21] = 0;
   out_6575454721087425774[22] = 0;
   out_6575454721087425774[23] = 0;
   out_6575454721087425774[24] = 0;
   out_6575454721087425774[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_6575454721087425774[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_6575454721087425774[27] = 0;
   out_6575454721087425774[28] = 0;
   out_6575454721087425774[29] = 0;
   out_6575454721087425774[30] = 0;
   out_6575454721087425774[31] = 0;
   out_6575454721087425774[32] = 0;
   out_6575454721087425774[33] = 0;
   out_6575454721087425774[34] = 0;
   out_6575454721087425774[35] = 0;
   out_6575454721087425774[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_6575454721087425774[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_6575454721087425774[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_6575454721087425774[39] = 0;
   out_6575454721087425774[40] = 0;
   out_6575454721087425774[41] = 0;
   out_6575454721087425774[42] = 0;
   out_6575454721087425774[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_6575454721087425774[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_6575454721087425774[45] = 0;
   out_6575454721087425774[46] = 0;
   out_6575454721087425774[47] = 0;
   out_6575454721087425774[48] = 0;
   out_6575454721087425774[49] = 0;
   out_6575454721087425774[50] = 0;
   out_6575454721087425774[51] = 0;
   out_6575454721087425774[52] = 0;
   out_6575454721087425774[53] = 0;
   out_6575454721087425774[54] = 0;
   out_6575454721087425774[55] = 0;
   out_6575454721087425774[56] = 0;
   out_6575454721087425774[57] = 1;
   out_6575454721087425774[58] = 0;
   out_6575454721087425774[59] = 0;
   out_6575454721087425774[60] = 0;
   out_6575454721087425774[61] = 0;
   out_6575454721087425774[62] = 0;
   out_6575454721087425774[63] = 0;
   out_6575454721087425774[64] = 0;
   out_6575454721087425774[65] = 0;
   out_6575454721087425774[66] = dt;
   out_6575454721087425774[67] = 0;
   out_6575454721087425774[68] = 0;
   out_6575454721087425774[69] = 0;
   out_6575454721087425774[70] = 0;
   out_6575454721087425774[71] = 0;
   out_6575454721087425774[72] = 0;
   out_6575454721087425774[73] = 0;
   out_6575454721087425774[74] = 0;
   out_6575454721087425774[75] = 0;
   out_6575454721087425774[76] = 1;
   out_6575454721087425774[77] = 0;
   out_6575454721087425774[78] = 0;
   out_6575454721087425774[79] = 0;
   out_6575454721087425774[80] = 0;
   out_6575454721087425774[81] = 0;
   out_6575454721087425774[82] = 0;
   out_6575454721087425774[83] = 0;
   out_6575454721087425774[84] = 0;
   out_6575454721087425774[85] = dt;
   out_6575454721087425774[86] = 0;
   out_6575454721087425774[87] = 0;
   out_6575454721087425774[88] = 0;
   out_6575454721087425774[89] = 0;
   out_6575454721087425774[90] = 0;
   out_6575454721087425774[91] = 0;
   out_6575454721087425774[92] = 0;
   out_6575454721087425774[93] = 0;
   out_6575454721087425774[94] = 0;
   out_6575454721087425774[95] = 1;
   out_6575454721087425774[96] = 0;
   out_6575454721087425774[97] = 0;
   out_6575454721087425774[98] = 0;
   out_6575454721087425774[99] = 0;
   out_6575454721087425774[100] = 0;
   out_6575454721087425774[101] = 0;
   out_6575454721087425774[102] = 0;
   out_6575454721087425774[103] = 0;
   out_6575454721087425774[104] = dt;
   out_6575454721087425774[105] = 0;
   out_6575454721087425774[106] = 0;
   out_6575454721087425774[107] = 0;
   out_6575454721087425774[108] = 0;
   out_6575454721087425774[109] = 0;
   out_6575454721087425774[110] = 0;
   out_6575454721087425774[111] = 0;
   out_6575454721087425774[112] = 0;
   out_6575454721087425774[113] = 0;
   out_6575454721087425774[114] = 1;
   out_6575454721087425774[115] = 0;
   out_6575454721087425774[116] = 0;
   out_6575454721087425774[117] = 0;
   out_6575454721087425774[118] = 0;
   out_6575454721087425774[119] = 0;
   out_6575454721087425774[120] = 0;
   out_6575454721087425774[121] = 0;
   out_6575454721087425774[122] = 0;
   out_6575454721087425774[123] = 0;
   out_6575454721087425774[124] = 0;
   out_6575454721087425774[125] = 0;
   out_6575454721087425774[126] = 0;
   out_6575454721087425774[127] = 0;
   out_6575454721087425774[128] = 0;
   out_6575454721087425774[129] = 0;
   out_6575454721087425774[130] = 0;
   out_6575454721087425774[131] = 0;
   out_6575454721087425774[132] = 0;
   out_6575454721087425774[133] = 1;
   out_6575454721087425774[134] = 0;
   out_6575454721087425774[135] = 0;
   out_6575454721087425774[136] = 0;
   out_6575454721087425774[137] = 0;
   out_6575454721087425774[138] = 0;
   out_6575454721087425774[139] = 0;
   out_6575454721087425774[140] = 0;
   out_6575454721087425774[141] = 0;
   out_6575454721087425774[142] = 0;
   out_6575454721087425774[143] = 0;
   out_6575454721087425774[144] = 0;
   out_6575454721087425774[145] = 0;
   out_6575454721087425774[146] = 0;
   out_6575454721087425774[147] = 0;
   out_6575454721087425774[148] = 0;
   out_6575454721087425774[149] = 0;
   out_6575454721087425774[150] = 0;
   out_6575454721087425774[151] = 0;
   out_6575454721087425774[152] = 1;
   out_6575454721087425774[153] = 0;
   out_6575454721087425774[154] = 0;
   out_6575454721087425774[155] = 0;
   out_6575454721087425774[156] = 0;
   out_6575454721087425774[157] = 0;
   out_6575454721087425774[158] = 0;
   out_6575454721087425774[159] = 0;
   out_6575454721087425774[160] = 0;
   out_6575454721087425774[161] = 0;
   out_6575454721087425774[162] = 0;
   out_6575454721087425774[163] = 0;
   out_6575454721087425774[164] = 0;
   out_6575454721087425774[165] = 0;
   out_6575454721087425774[166] = 0;
   out_6575454721087425774[167] = 0;
   out_6575454721087425774[168] = 0;
   out_6575454721087425774[169] = 0;
   out_6575454721087425774[170] = 0;
   out_6575454721087425774[171] = 1;
   out_6575454721087425774[172] = 0;
   out_6575454721087425774[173] = 0;
   out_6575454721087425774[174] = 0;
   out_6575454721087425774[175] = 0;
   out_6575454721087425774[176] = 0;
   out_6575454721087425774[177] = 0;
   out_6575454721087425774[178] = 0;
   out_6575454721087425774[179] = 0;
   out_6575454721087425774[180] = 0;
   out_6575454721087425774[181] = 0;
   out_6575454721087425774[182] = 0;
   out_6575454721087425774[183] = 0;
   out_6575454721087425774[184] = 0;
   out_6575454721087425774[185] = 0;
   out_6575454721087425774[186] = 0;
   out_6575454721087425774[187] = 0;
   out_6575454721087425774[188] = 0;
   out_6575454721087425774[189] = 0;
   out_6575454721087425774[190] = 1;
   out_6575454721087425774[191] = 0;
   out_6575454721087425774[192] = 0;
   out_6575454721087425774[193] = 0;
   out_6575454721087425774[194] = 0;
   out_6575454721087425774[195] = 0;
   out_6575454721087425774[196] = 0;
   out_6575454721087425774[197] = 0;
   out_6575454721087425774[198] = 0;
   out_6575454721087425774[199] = 0;
   out_6575454721087425774[200] = 0;
   out_6575454721087425774[201] = 0;
   out_6575454721087425774[202] = 0;
   out_6575454721087425774[203] = 0;
   out_6575454721087425774[204] = 0;
   out_6575454721087425774[205] = 0;
   out_6575454721087425774[206] = 0;
   out_6575454721087425774[207] = 0;
   out_6575454721087425774[208] = 0;
   out_6575454721087425774[209] = 1;
   out_6575454721087425774[210] = 0;
   out_6575454721087425774[211] = 0;
   out_6575454721087425774[212] = 0;
   out_6575454721087425774[213] = 0;
   out_6575454721087425774[214] = 0;
   out_6575454721087425774[215] = 0;
   out_6575454721087425774[216] = 0;
   out_6575454721087425774[217] = 0;
   out_6575454721087425774[218] = 0;
   out_6575454721087425774[219] = 0;
   out_6575454721087425774[220] = 0;
   out_6575454721087425774[221] = 0;
   out_6575454721087425774[222] = 0;
   out_6575454721087425774[223] = 0;
   out_6575454721087425774[224] = 0;
   out_6575454721087425774[225] = 0;
   out_6575454721087425774[226] = 0;
   out_6575454721087425774[227] = 0;
   out_6575454721087425774[228] = 1;
   out_6575454721087425774[229] = 0;
   out_6575454721087425774[230] = 0;
   out_6575454721087425774[231] = 0;
   out_6575454721087425774[232] = 0;
   out_6575454721087425774[233] = 0;
   out_6575454721087425774[234] = 0;
   out_6575454721087425774[235] = 0;
   out_6575454721087425774[236] = 0;
   out_6575454721087425774[237] = 0;
   out_6575454721087425774[238] = 0;
   out_6575454721087425774[239] = 0;
   out_6575454721087425774[240] = 0;
   out_6575454721087425774[241] = 0;
   out_6575454721087425774[242] = 0;
   out_6575454721087425774[243] = 0;
   out_6575454721087425774[244] = 0;
   out_6575454721087425774[245] = 0;
   out_6575454721087425774[246] = 0;
   out_6575454721087425774[247] = 1;
   out_6575454721087425774[248] = 0;
   out_6575454721087425774[249] = 0;
   out_6575454721087425774[250] = 0;
   out_6575454721087425774[251] = 0;
   out_6575454721087425774[252] = 0;
   out_6575454721087425774[253] = 0;
   out_6575454721087425774[254] = 0;
   out_6575454721087425774[255] = 0;
   out_6575454721087425774[256] = 0;
   out_6575454721087425774[257] = 0;
   out_6575454721087425774[258] = 0;
   out_6575454721087425774[259] = 0;
   out_6575454721087425774[260] = 0;
   out_6575454721087425774[261] = 0;
   out_6575454721087425774[262] = 0;
   out_6575454721087425774[263] = 0;
   out_6575454721087425774[264] = 0;
   out_6575454721087425774[265] = 0;
   out_6575454721087425774[266] = 1;
   out_6575454721087425774[267] = 0;
   out_6575454721087425774[268] = 0;
   out_6575454721087425774[269] = 0;
   out_6575454721087425774[270] = 0;
   out_6575454721087425774[271] = 0;
   out_6575454721087425774[272] = 0;
   out_6575454721087425774[273] = 0;
   out_6575454721087425774[274] = 0;
   out_6575454721087425774[275] = 0;
   out_6575454721087425774[276] = 0;
   out_6575454721087425774[277] = 0;
   out_6575454721087425774[278] = 0;
   out_6575454721087425774[279] = 0;
   out_6575454721087425774[280] = 0;
   out_6575454721087425774[281] = 0;
   out_6575454721087425774[282] = 0;
   out_6575454721087425774[283] = 0;
   out_6575454721087425774[284] = 0;
   out_6575454721087425774[285] = 1;
   out_6575454721087425774[286] = 0;
   out_6575454721087425774[287] = 0;
   out_6575454721087425774[288] = 0;
   out_6575454721087425774[289] = 0;
   out_6575454721087425774[290] = 0;
   out_6575454721087425774[291] = 0;
   out_6575454721087425774[292] = 0;
   out_6575454721087425774[293] = 0;
   out_6575454721087425774[294] = 0;
   out_6575454721087425774[295] = 0;
   out_6575454721087425774[296] = 0;
   out_6575454721087425774[297] = 0;
   out_6575454721087425774[298] = 0;
   out_6575454721087425774[299] = 0;
   out_6575454721087425774[300] = 0;
   out_6575454721087425774[301] = 0;
   out_6575454721087425774[302] = 0;
   out_6575454721087425774[303] = 0;
   out_6575454721087425774[304] = 1;
   out_6575454721087425774[305] = 0;
   out_6575454721087425774[306] = 0;
   out_6575454721087425774[307] = 0;
   out_6575454721087425774[308] = 0;
   out_6575454721087425774[309] = 0;
   out_6575454721087425774[310] = 0;
   out_6575454721087425774[311] = 0;
   out_6575454721087425774[312] = 0;
   out_6575454721087425774[313] = 0;
   out_6575454721087425774[314] = 0;
   out_6575454721087425774[315] = 0;
   out_6575454721087425774[316] = 0;
   out_6575454721087425774[317] = 0;
   out_6575454721087425774[318] = 0;
   out_6575454721087425774[319] = 0;
   out_6575454721087425774[320] = 0;
   out_6575454721087425774[321] = 0;
   out_6575454721087425774[322] = 0;
   out_6575454721087425774[323] = 1;
}
void h_4(double *state, double *unused, double *out_1876366542928782564) {
   out_1876366542928782564[0] = state[6] + state[9];
   out_1876366542928782564[1] = state[7] + state[10];
   out_1876366542928782564[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_3790922340853437677) {
   out_3790922340853437677[0] = 0;
   out_3790922340853437677[1] = 0;
   out_3790922340853437677[2] = 0;
   out_3790922340853437677[3] = 0;
   out_3790922340853437677[4] = 0;
   out_3790922340853437677[5] = 0;
   out_3790922340853437677[6] = 1;
   out_3790922340853437677[7] = 0;
   out_3790922340853437677[8] = 0;
   out_3790922340853437677[9] = 1;
   out_3790922340853437677[10] = 0;
   out_3790922340853437677[11] = 0;
   out_3790922340853437677[12] = 0;
   out_3790922340853437677[13] = 0;
   out_3790922340853437677[14] = 0;
   out_3790922340853437677[15] = 0;
   out_3790922340853437677[16] = 0;
   out_3790922340853437677[17] = 0;
   out_3790922340853437677[18] = 0;
   out_3790922340853437677[19] = 0;
   out_3790922340853437677[20] = 0;
   out_3790922340853437677[21] = 0;
   out_3790922340853437677[22] = 0;
   out_3790922340853437677[23] = 0;
   out_3790922340853437677[24] = 0;
   out_3790922340853437677[25] = 1;
   out_3790922340853437677[26] = 0;
   out_3790922340853437677[27] = 0;
   out_3790922340853437677[28] = 1;
   out_3790922340853437677[29] = 0;
   out_3790922340853437677[30] = 0;
   out_3790922340853437677[31] = 0;
   out_3790922340853437677[32] = 0;
   out_3790922340853437677[33] = 0;
   out_3790922340853437677[34] = 0;
   out_3790922340853437677[35] = 0;
   out_3790922340853437677[36] = 0;
   out_3790922340853437677[37] = 0;
   out_3790922340853437677[38] = 0;
   out_3790922340853437677[39] = 0;
   out_3790922340853437677[40] = 0;
   out_3790922340853437677[41] = 0;
   out_3790922340853437677[42] = 0;
   out_3790922340853437677[43] = 0;
   out_3790922340853437677[44] = 1;
   out_3790922340853437677[45] = 0;
   out_3790922340853437677[46] = 0;
   out_3790922340853437677[47] = 1;
   out_3790922340853437677[48] = 0;
   out_3790922340853437677[49] = 0;
   out_3790922340853437677[50] = 0;
   out_3790922340853437677[51] = 0;
   out_3790922340853437677[52] = 0;
   out_3790922340853437677[53] = 0;
}
void h_10(double *state, double *unused, double *out_3919183550661363398) {
   out_3919183550661363398[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_3919183550661363398[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_3919183550661363398[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_2325412850660363779) {
   out_2325412850660363779[0] = 0;
   out_2325412850660363779[1] = 9.8100000000000005*cos(state[1]);
   out_2325412850660363779[2] = 0;
   out_2325412850660363779[3] = 0;
   out_2325412850660363779[4] = -state[8];
   out_2325412850660363779[5] = state[7];
   out_2325412850660363779[6] = 0;
   out_2325412850660363779[7] = state[5];
   out_2325412850660363779[8] = -state[4];
   out_2325412850660363779[9] = 0;
   out_2325412850660363779[10] = 0;
   out_2325412850660363779[11] = 0;
   out_2325412850660363779[12] = 1;
   out_2325412850660363779[13] = 0;
   out_2325412850660363779[14] = 0;
   out_2325412850660363779[15] = 1;
   out_2325412850660363779[16] = 0;
   out_2325412850660363779[17] = 0;
   out_2325412850660363779[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_2325412850660363779[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_2325412850660363779[20] = 0;
   out_2325412850660363779[21] = state[8];
   out_2325412850660363779[22] = 0;
   out_2325412850660363779[23] = -state[6];
   out_2325412850660363779[24] = -state[5];
   out_2325412850660363779[25] = 0;
   out_2325412850660363779[26] = state[3];
   out_2325412850660363779[27] = 0;
   out_2325412850660363779[28] = 0;
   out_2325412850660363779[29] = 0;
   out_2325412850660363779[30] = 0;
   out_2325412850660363779[31] = 1;
   out_2325412850660363779[32] = 0;
   out_2325412850660363779[33] = 0;
   out_2325412850660363779[34] = 1;
   out_2325412850660363779[35] = 0;
   out_2325412850660363779[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_2325412850660363779[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_2325412850660363779[38] = 0;
   out_2325412850660363779[39] = -state[7];
   out_2325412850660363779[40] = state[6];
   out_2325412850660363779[41] = 0;
   out_2325412850660363779[42] = state[4];
   out_2325412850660363779[43] = -state[3];
   out_2325412850660363779[44] = 0;
   out_2325412850660363779[45] = 0;
   out_2325412850660363779[46] = 0;
   out_2325412850660363779[47] = 0;
   out_2325412850660363779[48] = 0;
   out_2325412850660363779[49] = 0;
   out_2325412850660363779[50] = 1;
   out_2325412850660363779[51] = 0;
   out_2325412850660363779[52] = 0;
   out_2325412850660363779[53] = 1;
}
void h_13(double *state, double *unused, double *out_5236404584387533616) {
   out_5236404584387533616[0] = state[3];
   out_5236404584387533616[1] = state[4];
   out_5236404584387533616[2] = state[5];
}
void H_13(double *state, double *unused, double *out_578648515521104876) {
   out_578648515521104876[0] = 0;
   out_578648515521104876[1] = 0;
   out_578648515521104876[2] = 0;
   out_578648515521104876[3] = 1;
   out_578648515521104876[4] = 0;
   out_578648515521104876[5] = 0;
   out_578648515521104876[6] = 0;
   out_578648515521104876[7] = 0;
   out_578648515521104876[8] = 0;
   out_578648515521104876[9] = 0;
   out_578648515521104876[10] = 0;
   out_578648515521104876[11] = 0;
   out_578648515521104876[12] = 0;
   out_578648515521104876[13] = 0;
   out_578648515521104876[14] = 0;
   out_578648515521104876[15] = 0;
   out_578648515521104876[16] = 0;
   out_578648515521104876[17] = 0;
   out_578648515521104876[18] = 0;
   out_578648515521104876[19] = 0;
   out_578648515521104876[20] = 0;
   out_578648515521104876[21] = 0;
   out_578648515521104876[22] = 1;
   out_578648515521104876[23] = 0;
   out_578648515521104876[24] = 0;
   out_578648515521104876[25] = 0;
   out_578648515521104876[26] = 0;
   out_578648515521104876[27] = 0;
   out_578648515521104876[28] = 0;
   out_578648515521104876[29] = 0;
   out_578648515521104876[30] = 0;
   out_578648515521104876[31] = 0;
   out_578648515521104876[32] = 0;
   out_578648515521104876[33] = 0;
   out_578648515521104876[34] = 0;
   out_578648515521104876[35] = 0;
   out_578648515521104876[36] = 0;
   out_578648515521104876[37] = 0;
   out_578648515521104876[38] = 0;
   out_578648515521104876[39] = 0;
   out_578648515521104876[40] = 0;
   out_578648515521104876[41] = 1;
   out_578648515521104876[42] = 0;
   out_578648515521104876[43] = 0;
   out_578648515521104876[44] = 0;
   out_578648515521104876[45] = 0;
   out_578648515521104876[46] = 0;
   out_578648515521104876[47] = 0;
   out_578648515521104876[48] = 0;
   out_578648515521104876[49] = 0;
   out_578648515521104876[50] = 0;
   out_578648515521104876[51] = 0;
   out_578648515521104876[52] = 0;
   out_578648515521104876[53] = 0;
}
void h_14(double *state, double *unused, double *out_3604078571385785794) {
   out_3604078571385785794[0] = state[6];
   out_3604078571385785794[1] = state[7];
   out_3604078571385785794[2] = state[8];
}
void H_14(double *state, double *unused, double *out_172318515486046852) {
   out_172318515486046852[0] = 0;
   out_172318515486046852[1] = 0;
   out_172318515486046852[2] = 0;
   out_172318515486046852[3] = 0;
   out_172318515486046852[4] = 0;
   out_172318515486046852[5] = 0;
   out_172318515486046852[6] = 1;
   out_172318515486046852[7] = 0;
   out_172318515486046852[8] = 0;
   out_172318515486046852[9] = 0;
   out_172318515486046852[10] = 0;
   out_172318515486046852[11] = 0;
   out_172318515486046852[12] = 0;
   out_172318515486046852[13] = 0;
   out_172318515486046852[14] = 0;
   out_172318515486046852[15] = 0;
   out_172318515486046852[16] = 0;
   out_172318515486046852[17] = 0;
   out_172318515486046852[18] = 0;
   out_172318515486046852[19] = 0;
   out_172318515486046852[20] = 0;
   out_172318515486046852[21] = 0;
   out_172318515486046852[22] = 0;
   out_172318515486046852[23] = 0;
   out_172318515486046852[24] = 0;
   out_172318515486046852[25] = 1;
   out_172318515486046852[26] = 0;
   out_172318515486046852[27] = 0;
   out_172318515486046852[28] = 0;
   out_172318515486046852[29] = 0;
   out_172318515486046852[30] = 0;
   out_172318515486046852[31] = 0;
   out_172318515486046852[32] = 0;
   out_172318515486046852[33] = 0;
   out_172318515486046852[34] = 0;
   out_172318515486046852[35] = 0;
   out_172318515486046852[36] = 0;
   out_172318515486046852[37] = 0;
   out_172318515486046852[38] = 0;
   out_172318515486046852[39] = 0;
   out_172318515486046852[40] = 0;
   out_172318515486046852[41] = 0;
   out_172318515486046852[42] = 0;
   out_172318515486046852[43] = 0;
   out_172318515486046852[44] = 1;
   out_172318515486046852[45] = 0;
   out_172318515486046852[46] = 0;
   out_172318515486046852[47] = 0;
   out_172318515486046852[48] = 0;
   out_172318515486046852[49] = 0;
   out_172318515486046852[50] = 0;
   out_172318515486046852[51] = 0;
   out_172318515486046852[52] = 0;
   out_172318515486046852[53] = 0;
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
void pose_err_fun(double *nom_x, double *delta_x, double *out_7849211930432319310) {
  err_fun(nom_x, delta_x, out_7849211930432319310);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_4938013129047494051) {
  inv_err_fun(nom_x, true_x, out_4938013129047494051);
}
void pose_H_mod_fun(double *state, double *out_4310619498118974873) {
  H_mod_fun(state, out_4310619498118974873);
}
void pose_f_fun(double *state, double dt, double *out_1974982568906725041) {
  f_fun(state,  dt, out_1974982568906725041);
}
void pose_F_fun(double *state, double dt, double *out_6575454721087425774) {
  F_fun(state,  dt, out_6575454721087425774);
}
void pose_h_4(double *state, double *unused, double *out_1876366542928782564) {
  h_4(state, unused, out_1876366542928782564);
}
void pose_H_4(double *state, double *unused, double *out_3790922340853437677) {
  H_4(state, unused, out_3790922340853437677);
}
void pose_h_10(double *state, double *unused, double *out_3919183550661363398) {
  h_10(state, unused, out_3919183550661363398);
}
void pose_H_10(double *state, double *unused, double *out_2325412850660363779) {
  H_10(state, unused, out_2325412850660363779);
}
void pose_h_13(double *state, double *unused, double *out_5236404584387533616) {
  h_13(state, unused, out_5236404584387533616);
}
void pose_H_13(double *state, double *unused, double *out_578648515521104876) {
  H_13(state, unused, out_578648515521104876);
}
void pose_h_14(double *state, double *unused, double *out_3604078571385785794) {
  h_14(state, unused, out_3604078571385785794);
}
void pose_H_14(double *state, double *unused, double *out_172318515486046852) {
  H_14(state, unused, out_172318515486046852);
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
