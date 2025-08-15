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
void err_fun(double *nom_x, double *delta_x, double *out_2669393212407968939) {
   out_2669393212407968939[0] = delta_x[0] + nom_x[0];
   out_2669393212407968939[1] = delta_x[1] + nom_x[1];
   out_2669393212407968939[2] = delta_x[2] + nom_x[2];
   out_2669393212407968939[3] = delta_x[3] + nom_x[3];
   out_2669393212407968939[4] = delta_x[4] + nom_x[4];
   out_2669393212407968939[5] = delta_x[5] + nom_x[5];
   out_2669393212407968939[6] = delta_x[6] + nom_x[6];
   out_2669393212407968939[7] = delta_x[7] + nom_x[7];
   out_2669393212407968939[8] = delta_x[8] + nom_x[8];
   out_2669393212407968939[9] = delta_x[9] + nom_x[9];
   out_2669393212407968939[10] = delta_x[10] + nom_x[10];
   out_2669393212407968939[11] = delta_x[11] + nom_x[11];
   out_2669393212407968939[12] = delta_x[12] + nom_x[12];
   out_2669393212407968939[13] = delta_x[13] + nom_x[13];
   out_2669393212407968939[14] = delta_x[14] + nom_x[14];
   out_2669393212407968939[15] = delta_x[15] + nom_x[15];
   out_2669393212407968939[16] = delta_x[16] + nom_x[16];
   out_2669393212407968939[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_6589919633801240756) {
   out_6589919633801240756[0] = -nom_x[0] + true_x[0];
   out_6589919633801240756[1] = -nom_x[1] + true_x[1];
   out_6589919633801240756[2] = -nom_x[2] + true_x[2];
   out_6589919633801240756[3] = -nom_x[3] + true_x[3];
   out_6589919633801240756[4] = -nom_x[4] + true_x[4];
   out_6589919633801240756[5] = -nom_x[5] + true_x[5];
   out_6589919633801240756[6] = -nom_x[6] + true_x[6];
   out_6589919633801240756[7] = -nom_x[7] + true_x[7];
   out_6589919633801240756[8] = -nom_x[8] + true_x[8];
   out_6589919633801240756[9] = -nom_x[9] + true_x[9];
   out_6589919633801240756[10] = -nom_x[10] + true_x[10];
   out_6589919633801240756[11] = -nom_x[11] + true_x[11];
   out_6589919633801240756[12] = -nom_x[12] + true_x[12];
   out_6589919633801240756[13] = -nom_x[13] + true_x[13];
   out_6589919633801240756[14] = -nom_x[14] + true_x[14];
   out_6589919633801240756[15] = -nom_x[15] + true_x[15];
   out_6589919633801240756[16] = -nom_x[16] + true_x[16];
   out_6589919633801240756[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_8225234534934843580) {
   out_8225234534934843580[0] = 1.0;
   out_8225234534934843580[1] = 0.0;
   out_8225234534934843580[2] = 0.0;
   out_8225234534934843580[3] = 0.0;
   out_8225234534934843580[4] = 0.0;
   out_8225234534934843580[5] = 0.0;
   out_8225234534934843580[6] = 0.0;
   out_8225234534934843580[7] = 0.0;
   out_8225234534934843580[8] = 0.0;
   out_8225234534934843580[9] = 0.0;
   out_8225234534934843580[10] = 0.0;
   out_8225234534934843580[11] = 0.0;
   out_8225234534934843580[12] = 0.0;
   out_8225234534934843580[13] = 0.0;
   out_8225234534934843580[14] = 0.0;
   out_8225234534934843580[15] = 0.0;
   out_8225234534934843580[16] = 0.0;
   out_8225234534934843580[17] = 0.0;
   out_8225234534934843580[18] = 0.0;
   out_8225234534934843580[19] = 1.0;
   out_8225234534934843580[20] = 0.0;
   out_8225234534934843580[21] = 0.0;
   out_8225234534934843580[22] = 0.0;
   out_8225234534934843580[23] = 0.0;
   out_8225234534934843580[24] = 0.0;
   out_8225234534934843580[25] = 0.0;
   out_8225234534934843580[26] = 0.0;
   out_8225234534934843580[27] = 0.0;
   out_8225234534934843580[28] = 0.0;
   out_8225234534934843580[29] = 0.0;
   out_8225234534934843580[30] = 0.0;
   out_8225234534934843580[31] = 0.0;
   out_8225234534934843580[32] = 0.0;
   out_8225234534934843580[33] = 0.0;
   out_8225234534934843580[34] = 0.0;
   out_8225234534934843580[35] = 0.0;
   out_8225234534934843580[36] = 0.0;
   out_8225234534934843580[37] = 0.0;
   out_8225234534934843580[38] = 1.0;
   out_8225234534934843580[39] = 0.0;
   out_8225234534934843580[40] = 0.0;
   out_8225234534934843580[41] = 0.0;
   out_8225234534934843580[42] = 0.0;
   out_8225234534934843580[43] = 0.0;
   out_8225234534934843580[44] = 0.0;
   out_8225234534934843580[45] = 0.0;
   out_8225234534934843580[46] = 0.0;
   out_8225234534934843580[47] = 0.0;
   out_8225234534934843580[48] = 0.0;
   out_8225234534934843580[49] = 0.0;
   out_8225234534934843580[50] = 0.0;
   out_8225234534934843580[51] = 0.0;
   out_8225234534934843580[52] = 0.0;
   out_8225234534934843580[53] = 0.0;
   out_8225234534934843580[54] = 0.0;
   out_8225234534934843580[55] = 0.0;
   out_8225234534934843580[56] = 0.0;
   out_8225234534934843580[57] = 1.0;
   out_8225234534934843580[58] = 0.0;
   out_8225234534934843580[59] = 0.0;
   out_8225234534934843580[60] = 0.0;
   out_8225234534934843580[61] = 0.0;
   out_8225234534934843580[62] = 0.0;
   out_8225234534934843580[63] = 0.0;
   out_8225234534934843580[64] = 0.0;
   out_8225234534934843580[65] = 0.0;
   out_8225234534934843580[66] = 0.0;
   out_8225234534934843580[67] = 0.0;
   out_8225234534934843580[68] = 0.0;
   out_8225234534934843580[69] = 0.0;
   out_8225234534934843580[70] = 0.0;
   out_8225234534934843580[71] = 0.0;
   out_8225234534934843580[72] = 0.0;
   out_8225234534934843580[73] = 0.0;
   out_8225234534934843580[74] = 0.0;
   out_8225234534934843580[75] = 0.0;
   out_8225234534934843580[76] = 1.0;
   out_8225234534934843580[77] = 0.0;
   out_8225234534934843580[78] = 0.0;
   out_8225234534934843580[79] = 0.0;
   out_8225234534934843580[80] = 0.0;
   out_8225234534934843580[81] = 0.0;
   out_8225234534934843580[82] = 0.0;
   out_8225234534934843580[83] = 0.0;
   out_8225234534934843580[84] = 0.0;
   out_8225234534934843580[85] = 0.0;
   out_8225234534934843580[86] = 0.0;
   out_8225234534934843580[87] = 0.0;
   out_8225234534934843580[88] = 0.0;
   out_8225234534934843580[89] = 0.0;
   out_8225234534934843580[90] = 0.0;
   out_8225234534934843580[91] = 0.0;
   out_8225234534934843580[92] = 0.0;
   out_8225234534934843580[93] = 0.0;
   out_8225234534934843580[94] = 0.0;
   out_8225234534934843580[95] = 1.0;
   out_8225234534934843580[96] = 0.0;
   out_8225234534934843580[97] = 0.0;
   out_8225234534934843580[98] = 0.0;
   out_8225234534934843580[99] = 0.0;
   out_8225234534934843580[100] = 0.0;
   out_8225234534934843580[101] = 0.0;
   out_8225234534934843580[102] = 0.0;
   out_8225234534934843580[103] = 0.0;
   out_8225234534934843580[104] = 0.0;
   out_8225234534934843580[105] = 0.0;
   out_8225234534934843580[106] = 0.0;
   out_8225234534934843580[107] = 0.0;
   out_8225234534934843580[108] = 0.0;
   out_8225234534934843580[109] = 0.0;
   out_8225234534934843580[110] = 0.0;
   out_8225234534934843580[111] = 0.0;
   out_8225234534934843580[112] = 0.0;
   out_8225234534934843580[113] = 0.0;
   out_8225234534934843580[114] = 1.0;
   out_8225234534934843580[115] = 0.0;
   out_8225234534934843580[116] = 0.0;
   out_8225234534934843580[117] = 0.0;
   out_8225234534934843580[118] = 0.0;
   out_8225234534934843580[119] = 0.0;
   out_8225234534934843580[120] = 0.0;
   out_8225234534934843580[121] = 0.0;
   out_8225234534934843580[122] = 0.0;
   out_8225234534934843580[123] = 0.0;
   out_8225234534934843580[124] = 0.0;
   out_8225234534934843580[125] = 0.0;
   out_8225234534934843580[126] = 0.0;
   out_8225234534934843580[127] = 0.0;
   out_8225234534934843580[128] = 0.0;
   out_8225234534934843580[129] = 0.0;
   out_8225234534934843580[130] = 0.0;
   out_8225234534934843580[131] = 0.0;
   out_8225234534934843580[132] = 0.0;
   out_8225234534934843580[133] = 1.0;
   out_8225234534934843580[134] = 0.0;
   out_8225234534934843580[135] = 0.0;
   out_8225234534934843580[136] = 0.0;
   out_8225234534934843580[137] = 0.0;
   out_8225234534934843580[138] = 0.0;
   out_8225234534934843580[139] = 0.0;
   out_8225234534934843580[140] = 0.0;
   out_8225234534934843580[141] = 0.0;
   out_8225234534934843580[142] = 0.0;
   out_8225234534934843580[143] = 0.0;
   out_8225234534934843580[144] = 0.0;
   out_8225234534934843580[145] = 0.0;
   out_8225234534934843580[146] = 0.0;
   out_8225234534934843580[147] = 0.0;
   out_8225234534934843580[148] = 0.0;
   out_8225234534934843580[149] = 0.0;
   out_8225234534934843580[150] = 0.0;
   out_8225234534934843580[151] = 0.0;
   out_8225234534934843580[152] = 1.0;
   out_8225234534934843580[153] = 0.0;
   out_8225234534934843580[154] = 0.0;
   out_8225234534934843580[155] = 0.0;
   out_8225234534934843580[156] = 0.0;
   out_8225234534934843580[157] = 0.0;
   out_8225234534934843580[158] = 0.0;
   out_8225234534934843580[159] = 0.0;
   out_8225234534934843580[160] = 0.0;
   out_8225234534934843580[161] = 0.0;
   out_8225234534934843580[162] = 0.0;
   out_8225234534934843580[163] = 0.0;
   out_8225234534934843580[164] = 0.0;
   out_8225234534934843580[165] = 0.0;
   out_8225234534934843580[166] = 0.0;
   out_8225234534934843580[167] = 0.0;
   out_8225234534934843580[168] = 0.0;
   out_8225234534934843580[169] = 0.0;
   out_8225234534934843580[170] = 0.0;
   out_8225234534934843580[171] = 1.0;
   out_8225234534934843580[172] = 0.0;
   out_8225234534934843580[173] = 0.0;
   out_8225234534934843580[174] = 0.0;
   out_8225234534934843580[175] = 0.0;
   out_8225234534934843580[176] = 0.0;
   out_8225234534934843580[177] = 0.0;
   out_8225234534934843580[178] = 0.0;
   out_8225234534934843580[179] = 0.0;
   out_8225234534934843580[180] = 0.0;
   out_8225234534934843580[181] = 0.0;
   out_8225234534934843580[182] = 0.0;
   out_8225234534934843580[183] = 0.0;
   out_8225234534934843580[184] = 0.0;
   out_8225234534934843580[185] = 0.0;
   out_8225234534934843580[186] = 0.0;
   out_8225234534934843580[187] = 0.0;
   out_8225234534934843580[188] = 0.0;
   out_8225234534934843580[189] = 0.0;
   out_8225234534934843580[190] = 1.0;
   out_8225234534934843580[191] = 0.0;
   out_8225234534934843580[192] = 0.0;
   out_8225234534934843580[193] = 0.0;
   out_8225234534934843580[194] = 0.0;
   out_8225234534934843580[195] = 0.0;
   out_8225234534934843580[196] = 0.0;
   out_8225234534934843580[197] = 0.0;
   out_8225234534934843580[198] = 0.0;
   out_8225234534934843580[199] = 0.0;
   out_8225234534934843580[200] = 0.0;
   out_8225234534934843580[201] = 0.0;
   out_8225234534934843580[202] = 0.0;
   out_8225234534934843580[203] = 0.0;
   out_8225234534934843580[204] = 0.0;
   out_8225234534934843580[205] = 0.0;
   out_8225234534934843580[206] = 0.0;
   out_8225234534934843580[207] = 0.0;
   out_8225234534934843580[208] = 0.0;
   out_8225234534934843580[209] = 1.0;
   out_8225234534934843580[210] = 0.0;
   out_8225234534934843580[211] = 0.0;
   out_8225234534934843580[212] = 0.0;
   out_8225234534934843580[213] = 0.0;
   out_8225234534934843580[214] = 0.0;
   out_8225234534934843580[215] = 0.0;
   out_8225234534934843580[216] = 0.0;
   out_8225234534934843580[217] = 0.0;
   out_8225234534934843580[218] = 0.0;
   out_8225234534934843580[219] = 0.0;
   out_8225234534934843580[220] = 0.0;
   out_8225234534934843580[221] = 0.0;
   out_8225234534934843580[222] = 0.0;
   out_8225234534934843580[223] = 0.0;
   out_8225234534934843580[224] = 0.0;
   out_8225234534934843580[225] = 0.0;
   out_8225234534934843580[226] = 0.0;
   out_8225234534934843580[227] = 0.0;
   out_8225234534934843580[228] = 1.0;
   out_8225234534934843580[229] = 0.0;
   out_8225234534934843580[230] = 0.0;
   out_8225234534934843580[231] = 0.0;
   out_8225234534934843580[232] = 0.0;
   out_8225234534934843580[233] = 0.0;
   out_8225234534934843580[234] = 0.0;
   out_8225234534934843580[235] = 0.0;
   out_8225234534934843580[236] = 0.0;
   out_8225234534934843580[237] = 0.0;
   out_8225234534934843580[238] = 0.0;
   out_8225234534934843580[239] = 0.0;
   out_8225234534934843580[240] = 0.0;
   out_8225234534934843580[241] = 0.0;
   out_8225234534934843580[242] = 0.0;
   out_8225234534934843580[243] = 0.0;
   out_8225234534934843580[244] = 0.0;
   out_8225234534934843580[245] = 0.0;
   out_8225234534934843580[246] = 0.0;
   out_8225234534934843580[247] = 1.0;
   out_8225234534934843580[248] = 0.0;
   out_8225234534934843580[249] = 0.0;
   out_8225234534934843580[250] = 0.0;
   out_8225234534934843580[251] = 0.0;
   out_8225234534934843580[252] = 0.0;
   out_8225234534934843580[253] = 0.0;
   out_8225234534934843580[254] = 0.0;
   out_8225234534934843580[255] = 0.0;
   out_8225234534934843580[256] = 0.0;
   out_8225234534934843580[257] = 0.0;
   out_8225234534934843580[258] = 0.0;
   out_8225234534934843580[259] = 0.0;
   out_8225234534934843580[260] = 0.0;
   out_8225234534934843580[261] = 0.0;
   out_8225234534934843580[262] = 0.0;
   out_8225234534934843580[263] = 0.0;
   out_8225234534934843580[264] = 0.0;
   out_8225234534934843580[265] = 0.0;
   out_8225234534934843580[266] = 1.0;
   out_8225234534934843580[267] = 0.0;
   out_8225234534934843580[268] = 0.0;
   out_8225234534934843580[269] = 0.0;
   out_8225234534934843580[270] = 0.0;
   out_8225234534934843580[271] = 0.0;
   out_8225234534934843580[272] = 0.0;
   out_8225234534934843580[273] = 0.0;
   out_8225234534934843580[274] = 0.0;
   out_8225234534934843580[275] = 0.0;
   out_8225234534934843580[276] = 0.0;
   out_8225234534934843580[277] = 0.0;
   out_8225234534934843580[278] = 0.0;
   out_8225234534934843580[279] = 0.0;
   out_8225234534934843580[280] = 0.0;
   out_8225234534934843580[281] = 0.0;
   out_8225234534934843580[282] = 0.0;
   out_8225234534934843580[283] = 0.0;
   out_8225234534934843580[284] = 0.0;
   out_8225234534934843580[285] = 1.0;
   out_8225234534934843580[286] = 0.0;
   out_8225234534934843580[287] = 0.0;
   out_8225234534934843580[288] = 0.0;
   out_8225234534934843580[289] = 0.0;
   out_8225234534934843580[290] = 0.0;
   out_8225234534934843580[291] = 0.0;
   out_8225234534934843580[292] = 0.0;
   out_8225234534934843580[293] = 0.0;
   out_8225234534934843580[294] = 0.0;
   out_8225234534934843580[295] = 0.0;
   out_8225234534934843580[296] = 0.0;
   out_8225234534934843580[297] = 0.0;
   out_8225234534934843580[298] = 0.0;
   out_8225234534934843580[299] = 0.0;
   out_8225234534934843580[300] = 0.0;
   out_8225234534934843580[301] = 0.0;
   out_8225234534934843580[302] = 0.0;
   out_8225234534934843580[303] = 0.0;
   out_8225234534934843580[304] = 1.0;
   out_8225234534934843580[305] = 0.0;
   out_8225234534934843580[306] = 0.0;
   out_8225234534934843580[307] = 0.0;
   out_8225234534934843580[308] = 0.0;
   out_8225234534934843580[309] = 0.0;
   out_8225234534934843580[310] = 0.0;
   out_8225234534934843580[311] = 0.0;
   out_8225234534934843580[312] = 0.0;
   out_8225234534934843580[313] = 0.0;
   out_8225234534934843580[314] = 0.0;
   out_8225234534934843580[315] = 0.0;
   out_8225234534934843580[316] = 0.0;
   out_8225234534934843580[317] = 0.0;
   out_8225234534934843580[318] = 0.0;
   out_8225234534934843580[319] = 0.0;
   out_8225234534934843580[320] = 0.0;
   out_8225234534934843580[321] = 0.0;
   out_8225234534934843580[322] = 0.0;
   out_8225234534934843580[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_3713400227530287176) {
   out_3713400227530287176[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_3713400227530287176[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_3713400227530287176[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_3713400227530287176[3] = dt*state[12] + state[3];
   out_3713400227530287176[4] = dt*state[13] + state[4];
   out_3713400227530287176[5] = dt*state[14] + state[5];
   out_3713400227530287176[6] = state[6];
   out_3713400227530287176[7] = state[7];
   out_3713400227530287176[8] = state[8];
   out_3713400227530287176[9] = state[9];
   out_3713400227530287176[10] = state[10];
   out_3713400227530287176[11] = state[11];
   out_3713400227530287176[12] = state[12];
   out_3713400227530287176[13] = state[13];
   out_3713400227530287176[14] = state[14];
   out_3713400227530287176[15] = state[15];
   out_3713400227530287176[16] = state[16];
   out_3713400227530287176[17] = state[17];
}
void F_fun(double *state, double dt, double *out_7623311308597317329) {
   out_7623311308597317329[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_7623311308597317329[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_7623311308597317329[2] = 0;
   out_7623311308597317329[3] = 0;
   out_7623311308597317329[4] = 0;
   out_7623311308597317329[5] = 0;
   out_7623311308597317329[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_7623311308597317329[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_7623311308597317329[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_7623311308597317329[9] = 0;
   out_7623311308597317329[10] = 0;
   out_7623311308597317329[11] = 0;
   out_7623311308597317329[12] = 0;
   out_7623311308597317329[13] = 0;
   out_7623311308597317329[14] = 0;
   out_7623311308597317329[15] = 0;
   out_7623311308597317329[16] = 0;
   out_7623311308597317329[17] = 0;
   out_7623311308597317329[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_7623311308597317329[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_7623311308597317329[20] = 0;
   out_7623311308597317329[21] = 0;
   out_7623311308597317329[22] = 0;
   out_7623311308597317329[23] = 0;
   out_7623311308597317329[24] = 0;
   out_7623311308597317329[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_7623311308597317329[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_7623311308597317329[27] = 0;
   out_7623311308597317329[28] = 0;
   out_7623311308597317329[29] = 0;
   out_7623311308597317329[30] = 0;
   out_7623311308597317329[31] = 0;
   out_7623311308597317329[32] = 0;
   out_7623311308597317329[33] = 0;
   out_7623311308597317329[34] = 0;
   out_7623311308597317329[35] = 0;
   out_7623311308597317329[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_7623311308597317329[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_7623311308597317329[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_7623311308597317329[39] = 0;
   out_7623311308597317329[40] = 0;
   out_7623311308597317329[41] = 0;
   out_7623311308597317329[42] = 0;
   out_7623311308597317329[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_7623311308597317329[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_7623311308597317329[45] = 0;
   out_7623311308597317329[46] = 0;
   out_7623311308597317329[47] = 0;
   out_7623311308597317329[48] = 0;
   out_7623311308597317329[49] = 0;
   out_7623311308597317329[50] = 0;
   out_7623311308597317329[51] = 0;
   out_7623311308597317329[52] = 0;
   out_7623311308597317329[53] = 0;
   out_7623311308597317329[54] = 0;
   out_7623311308597317329[55] = 0;
   out_7623311308597317329[56] = 0;
   out_7623311308597317329[57] = 1;
   out_7623311308597317329[58] = 0;
   out_7623311308597317329[59] = 0;
   out_7623311308597317329[60] = 0;
   out_7623311308597317329[61] = 0;
   out_7623311308597317329[62] = 0;
   out_7623311308597317329[63] = 0;
   out_7623311308597317329[64] = 0;
   out_7623311308597317329[65] = 0;
   out_7623311308597317329[66] = dt;
   out_7623311308597317329[67] = 0;
   out_7623311308597317329[68] = 0;
   out_7623311308597317329[69] = 0;
   out_7623311308597317329[70] = 0;
   out_7623311308597317329[71] = 0;
   out_7623311308597317329[72] = 0;
   out_7623311308597317329[73] = 0;
   out_7623311308597317329[74] = 0;
   out_7623311308597317329[75] = 0;
   out_7623311308597317329[76] = 1;
   out_7623311308597317329[77] = 0;
   out_7623311308597317329[78] = 0;
   out_7623311308597317329[79] = 0;
   out_7623311308597317329[80] = 0;
   out_7623311308597317329[81] = 0;
   out_7623311308597317329[82] = 0;
   out_7623311308597317329[83] = 0;
   out_7623311308597317329[84] = 0;
   out_7623311308597317329[85] = dt;
   out_7623311308597317329[86] = 0;
   out_7623311308597317329[87] = 0;
   out_7623311308597317329[88] = 0;
   out_7623311308597317329[89] = 0;
   out_7623311308597317329[90] = 0;
   out_7623311308597317329[91] = 0;
   out_7623311308597317329[92] = 0;
   out_7623311308597317329[93] = 0;
   out_7623311308597317329[94] = 0;
   out_7623311308597317329[95] = 1;
   out_7623311308597317329[96] = 0;
   out_7623311308597317329[97] = 0;
   out_7623311308597317329[98] = 0;
   out_7623311308597317329[99] = 0;
   out_7623311308597317329[100] = 0;
   out_7623311308597317329[101] = 0;
   out_7623311308597317329[102] = 0;
   out_7623311308597317329[103] = 0;
   out_7623311308597317329[104] = dt;
   out_7623311308597317329[105] = 0;
   out_7623311308597317329[106] = 0;
   out_7623311308597317329[107] = 0;
   out_7623311308597317329[108] = 0;
   out_7623311308597317329[109] = 0;
   out_7623311308597317329[110] = 0;
   out_7623311308597317329[111] = 0;
   out_7623311308597317329[112] = 0;
   out_7623311308597317329[113] = 0;
   out_7623311308597317329[114] = 1;
   out_7623311308597317329[115] = 0;
   out_7623311308597317329[116] = 0;
   out_7623311308597317329[117] = 0;
   out_7623311308597317329[118] = 0;
   out_7623311308597317329[119] = 0;
   out_7623311308597317329[120] = 0;
   out_7623311308597317329[121] = 0;
   out_7623311308597317329[122] = 0;
   out_7623311308597317329[123] = 0;
   out_7623311308597317329[124] = 0;
   out_7623311308597317329[125] = 0;
   out_7623311308597317329[126] = 0;
   out_7623311308597317329[127] = 0;
   out_7623311308597317329[128] = 0;
   out_7623311308597317329[129] = 0;
   out_7623311308597317329[130] = 0;
   out_7623311308597317329[131] = 0;
   out_7623311308597317329[132] = 0;
   out_7623311308597317329[133] = 1;
   out_7623311308597317329[134] = 0;
   out_7623311308597317329[135] = 0;
   out_7623311308597317329[136] = 0;
   out_7623311308597317329[137] = 0;
   out_7623311308597317329[138] = 0;
   out_7623311308597317329[139] = 0;
   out_7623311308597317329[140] = 0;
   out_7623311308597317329[141] = 0;
   out_7623311308597317329[142] = 0;
   out_7623311308597317329[143] = 0;
   out_7623311308597317329[144] = 0;
   out_7623311308597317329[145] = 0;
   out_7623311308597317329[146] = 0;
   out_7623311308597317329[147] = 0;
   out_7623311308597317329[148] = 0;
   out_7623311308597317329[149] = 0;
   out_7623311308597317329[150] = 0;
   out_7623311308597317329[151] = 0;
   out_7623311308597317329[152] = 1;
   out_7623311308597317329[153] = 0;
   out_7623311308597317329[154] = 0;
   out_7623311308597317329[155] = 0;
   out_7623311308597317329[156] = 0;
   out_7623311308597317329[157] = 0;
   out_7623311308597317329[158] = 0;
   out_7623311308597317329[159] = 0;
   out_7623311308597317329[160] = 0;
   out_7623311308597317329[161] = 0;
   out_7623311308597317329[162] = 0;
   out_7623311308597317329[163] = 0;
   out_7623311308597317329[164] = 0;
   out_7623311308597317329[165] = 0;
   out_7623311308597317329[166] = 0;
   out_7623311308597317329[167] = 0;
   out_7623311308597317329[168] = 0;
   out_7623311308597317329[169] = 0;
   out_7623311308597317329[170] = 0;
   out_7623311308597317329[171] = 1;
   out_7623311308597317329[172] = 0;
   out_7623311308597317329[173] = 0;
   out_7623311308597317329[174] = 0;
   out_7623311308597317329[175] = 0;
   out_7623311308597317329[176] = 0;
   out_7623311308597317329[177] = 0;
   out_7623311308597317329[178] = 0;
   out_7623311308597317329[179] = 0;
   out_7623311308597317329[180] = 0;
   out_7623311308597317329[181] = 0;
   out_7623311308597317329[182] = 0;
   out_7623311308597317329[183] = 0;
   out_7623311308597317329[184] = 0;
   out_7623311308597317329[185] = 0;
   out_7623311308597317329[186] = 0;
   out_7623311308597317329[187] = 0;
   out_7623311308597317329[188] = 0;
   out_7623311308597317329[189] = 0;
   out_7623311308597317329[190] = 1;
   out_7623311308597317329[191] = 0;
   out_7623311308597317329[192] = 0;
   out_7623311308597317329[193] = 0;
   out_7623311308597317329[194] = 0;
   out_7623311308597317329[195] = 0;
   out_7623311308597317329[196] = 0;
   out_7623311308597317329[197] = 0;
   out_7623311308597317329[198] = 0;
   out_7623311308597317329[199] = 0;
   out_7623311308597317329[200] = 0;
   out_7623311308597317329[201] = 0;
   out_7623311308597317329[202] = 0;
   out_7623311308597317329[203] = 0;
   out_7623311308597317329[204] = 0;
   out_7623311308597317329[205] = 0;
   out_7623311308597317329[206] = 0;
   out_7623311308597317329[207] = 0;
   out_7623311308597317329[208] = 0;
   out_7623311308597317329[209] = 1;
   out_7623311308597317329[210] = 0;
   out_7623311308597317329[211] = 0;
   out_7623311308597317329[212] = 0;
   out_7623311308597317329[213] = 0;
   out_7623311308597317329[214] = 0;
   out_7623311308597317329[215] = 0;
   out_7623311308597317329[216] = 0;
   out_7623311308597317329[217] = 0;
   out_7623311308597317329[218] = 0;
   out_7623311308597317329[219] = 0;
   out_7623311308597317329[220] = 0;
   out_7623311308597317329[221] = 0;
   out_7623311308597317329[222] = 0;
   out_7623311308597317329[223] = 0;
   out_7623311308597317329[224] = 0;
   out_7623311308597317329[225] = 0;
   out_7623311308597317329[226] = 0;
   out_7623311308597317329[227] = 0;
   out_7623311308597317329[228] = 1;
   out_7623311308597317329[229] = 0;
   out_7623311308597317329[230] = 0;
   out_7623311308597317329[231] = 0;
   out_7623311308597317329[232] = 0;
   out_7623311308597317329[233] = 0;
   out_7623311308597317329[234] = 0;
   out_7623311308597317329[235] = 0;
   out_7623311308597317329[236] = 0;
   out_7623311308597317329[237] = 0;
   out_7623311308597317329[238] = 0;
   out_7623311308597317329[239] = 0;
   out_7623311308597317329[240] = 0;
   out_7623311308597317329[241] = 0;
   out_7623311308597317329[242] = 0;
   out_7623311308597317329[243] = 0;
   out_7623311308597317329[244] = 0;
   out_7623311308597317329[245] = 0;
   out_7623311308597317329[246] = 0;
   out_7623311308597317329[247] = 1;
   out_7623311308597317329[248] = 0;
   out_7623311308597317329[249] = 0;
   out_7623311308597317329[250] = 0;
   out_7623311308597317329[251] = 0;
   out_7623311308597317329[252] = 0;
   out_7623311308597317329[253] = 0;
   out_7623311308597317329[254] = 0;
   out_7623311308597317329[255] = 0;
   out_7623311308597317329[256] = 0;
   out_7623311308597317329[257] = 0;
   out_7623311308597317329[258] = 0;
   out_7623311308597317329[259] = 0;
   out_7623311308597317329[260] = 0;
   out_7623311308597317329[261] = 0;
   out_7623311308597317329[262] = 0;
   out_7623311308597317329[263] = 0;
   out_7623311308597317329[264] = 0;
   out_7623311308597317329[265] = 0;
   out_7623311308597317329[266] = 1;
   out_7623311308597317329[267] = 0;
   out_7623311308597317329[268] = 0;
   out_7623311308597317329[269] = 0;
   out_7623311308597317329[270] = 0;
   out_7623311308597317329[271] = 0;
   out_7623311308597317329[272] = 0;
   out_7623311308597317329[273] = 0;
   out_7623311308597317329[274] = 0;
   out_7623311308597317329[275] = 0;
   out_7623311308597317329[276] = 0;
   out_7623311308597317329[277] = 0;
   out_7623311308597317329[278] = 0;
   out_7623311308597317329[279] = 0;
   out_7623311308597317329[280] = 0;
   out_7623311308597317329[281] = 0;
   out_7623311308597317329[282] = 0;
   out_7623311308597317329[283] = 0;
   out_7623311308597317329[284] = 0;
   out_7623311308597317329[285] = 1;
   out_7623311308597317329[286] = 0;
   out_7623311308597317329[287] = 0;
   out_7623311308597317329[288] = 0;
   out_7623311308597317329[289] = 0;
   out_7623311308597317329[290] = 0;
   out_7623311308597317329[291] = 0;
   out_7623311308597317329[292] = 0;
   out_7623311308597317329[293] = 0;
   out_7623311308597317329[294] = 0;
   out_7623311308597317329[295] = 0;
   out_7623311308597317329[296] = 0;
   out_7623311308597317329[297] = 0;
   out_7623311308597317329[298] = 0;
   out_7623311308597317329[299] = 0;
   out_7623311308597317329[300] = 0;
   out_7623311308597317329[301] = 0;
   out_7623311308597317329[302] = 0;
   out_7623311308597317329[303] = 0;
   out_7623311308597317329[304] = 1;
   out_7623311308597317329[305] = 0;
   out_7623311308597317329[306] = 0;
   out_7623311308597317329[307] = 0;
   out_7623311308597317329[308] = 0;
   out_7623311308597317329[309] = 0;
   out_7623311308597317329[310] = 0;
   out_7623311308597317329[311] = 0;
   out_7623311308597317329[312] = 0;
   out_7623311308597317329[313] = 0;
   out_7623311308597317329[314] = 0;
   out_7623311308597317329[315] = 0;
   out_7623311308597317329[316] = 0;
   out_7623311308597317329[317] = 0;
   out_7623311308597317329[318] = 0;
   out_7623311308597317329[319] = 0;
   out_7623311308597317329[320] = 0;
   out_7623311308597317329[321] = 0;
   out_7623311308597317329[322] = 0;
   out_7623311308597317329[323] = 1;
}
void h_4(double *state, double *unused, double *out_1299539042272213645) {
   out_1299539042272213645[0] = state[6] + state[9];
   out_1299539042272213645[1] = state[7] + state[10];
   out_1299539042272213645[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_1355781524233554350) {
   out_1355781524233554350[0] = 0;
   out_1355781524233554350[1] = 0;
   out_1355781524233554350[2] = 0;
   out_1355781524233554350[3] = 0;
   out_1355781524233554350[4] = 0;
   out_1355781524233554350[5] = 0;
   out_1355781524233554350[6] = 1;
   out_1355781524233554350[7] = 0;
   out_1355781524233554350[8] = 0;
   out_1355781524233554350[9] = 1;
   out_1355781524233554350[10] = 0;
   out_1355781524233554350[11] = 0;
   out_1355781524233554350[12] = 0;
   out_1355781524233554350[13] = 0;
   out_1355781524233554350[14] = 0;
   out_1355781524233554350[15] = 0;
   out_1355781524233554350[16] = 0;
   out_1355781524233554350[17] = 0;
   out_1355781524233554350[18] = 0;
   out_1355781524233554350[19] = 0;
   out_1355781524233554350[20] = 0;
   out_1355781524233554350[21] = 0;
   out_1355781524233554350[22] = 0;
   out_1355781524233554350[23] = 0;
   out_1355781524233554350[24] = 0;
   out_1355781524233554350[25] = 1;
   out_1355781524233554350[26] = 0;
   out_1355781524233554350[27] = 0;
   out_1355781524233554350[28] = 1;
   out_1355781524233554350[29] = 0;
   out_1355781524233554350[30] = 0;
   out_1355781524233554350[31] = 0;
   out_1355781524233554350[32] = 0;
   out_1355781524233554350[33] = 0;
   out_1355781524233554350[34] = 0;
   out_1355781524233554350[35] = 0;
   out_1355781524233554350[36] = 0;
   out_1355781524233554350[37] = 0;
   out_1355781524233554350[38] = 0;
   out_1355781524233554350[39] = 0;
   out_1355781524233554350[40] = 0;
   out_1355781524233554350[41] = 0;
   out_1355781524233554350[42] = 0;
   out_1355781524233554350[43] = 0;
   out_1355781524233554350[44] = 1;
   out_1355781524233554350[45] = 0;
   out_1355781524233554350[46] = 0;
   out_1355781524233554350[47] = 1;
   out_1355781524233554350[48] = 0;
   out_1355781524233554350[49] = 0;
   out_1355781524233554350[50] = 0;
   out_1355781524233554350[51] = 0;
   out_1355781524233554350[52] = 0;
   out_1355781524233554350[53] = 0;
}
void h_10(double *state, double *unused, double *out_4564875173987417445) {
   out_4564875173987417445[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_4564875173987417445[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_4564875173987417445[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_6426002362757736416) {
   out_6426002362757736416[0] = 0;
   out_6426002362757736416[1] = 9.8100000000000005*cos(state[1]);
   out_6426002362757736416[2] = 0;
   out_6426002362757736416[3] = 0;
   out_6426002362757736416[4] = -state[8];
   out_6426002362757736416[5] = state[7];
   out_6426002362757736416[6] = 0;
   out_6426002362757736416[7] = state[5];
   out_6426002362757736416[8] = -state[4];
   out_6426002362757736416[9] = 0;
   out_6426002362757736416[10] = 0;
   out_6426002362757736416[11] = 0;
   out_6426002362757736416[12] = 1;
   out_6426002362757736416[13] = 0;
   out_6426002362757736416[14] = 0;
   out_6426002362757736416[15] = 1;
   out_6426002362757736416[16] = 0;
   out_6426002362757736416[17] = 0;
   out_6426002362757736416[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_6426002362757736416[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_6426002362757736416[20] = 0;
   out_6426002362757736416[21] = state[8];
   out_6426002362757736416[22] = 0;
   out_6426002362757736416[23] = -state[6];
   out_6426002362757736416[24] = -state[5];
   out_6426002362757736416[25] = 0;
   out_6426002362757736416[26] = state[3];
   out_6426002362757736416[27] = 0;
   out_6426002362757736416[28] = 0;
   out_6426002362757736416[29] = 0;
   out_6426002362757736416[30] = 0;
   out_6426002362757736416[31] = 1;
   out_6426002362757736416[32] = 0;
   out_6426002362757736416[33] = 0;
   out_6426002362757736416[34] = 1;
   out_6426002362757736416[35] = 0;
   out_6426002362757736416[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_6426002362757736416[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_6426002362757736416[38] = 0;
   out_6426002362757736416[39] = -state[7];
   out_6426002362757736416[40] = state[6];
   out_6426002362757736416[41] = 0;
   out_6426002362757736416[42] = state[4];
   out_6426002362757736416[43] = -state[3];
   out_6426002362757736416[44] = 0;
   out_6426002362757736416[45] = 0;
   out_6426002362757736416[46] = 0;
   out_6426002362757736416[47] = 0;
   out_6426002362757736416[48] = 0;
   out_6426002362757736416[49] = 0;
   out_6426002362757736416[50] = 1;
   out_6426002362757736416[51] = 0;
   out_6426002362757736416[52] = 0;
   out_6426002362757736416[53] = 1;
}
void h_13(double *state, double *unused, double *out_8828664930147326382) {
   out_8828664930147326382[0] = state[3];
   out_8828664930147326382[1] = state[4];
   out_8828664930147326382[2] = state[5];
}
void H_13(double *state, double *unused, double *out_4568055349565887151) {
   out_4568055349565887151[0] = 0;
   out_4568055349565887151[1] = 0;
   out_4568055349565887151[2] = 0;
   out_4568055349565887151[3] = 1;
   out_4568055349565887151[4] = 0;
   out_4568055349565887151[5] = 0;
   out_4568055349565887151[6] = 0;
   out_4568055349565887151[7] = 0;
   out_4568055349565887151[8] = 0;
   out_4568055349565887151[9] = 0;
   out_4568055349565887151[10] = 0;
   out_4568055349565887151[11] = 0;
   out_4568055349565887151[12] = 0;
   out_4568055349565887151[13] = 0;
   out_4568055349565887151[14] = 0;
   out_4568055349565887151[15] = 0;
   out_4568055349565887151[16] = 0;
   out_4568055349565887151[17] = 0;
   out_4568055349565887151[18] = 0;
   out_4568055349565887151[19] = 0;
   out_4568055349565887151[20] = 0;
   out_4568055349565887151[21] = 0;
   out_4568055349565887151[22] = 1;
   out_4568055349565887151[23] = 0;
   out_4568055349565887151[24] = 0;
   out_4568055349565887151[25] = 0;
   out_4568055349565887151[26] = 0;
   out_4568055349565887151[27] = 0;
   out_4568055349565887151[28] = 0;
   out_4568055349565887151[29] = 0;
   out_4568055349565887151[30] = 0;
   out_4568055349565887151[31] = 0;
   out_4568055349565887151[32] = 0;
   out_4568055349565887151[33] = 0;
   out_4568055349565887151[34] = 0;
   out_4568055349565887151[35] = 0;
   out_4568055349565887151[36] = 0;
   out_4568055349565887151[37] = 0;
   out_4568055349565887151[38] = 0;
   out_4568055349565887151[39] = 0;
   out_4568055349565887151[40] = 0;
   out_4568055349565887151[41] = 1;
   out_4568055349565887151[42] = 0;
   out_4568055349565887151[43] = 0;
   out_4568055349565887151[44] = 0;
   out_4568055349565887151[45] = 0;
   out_4568055349565887151[46] = 0;
   out_4568055349565887151[47] = 0;
   out_4568055349565887151[48] = 0;
   out_4568055349565887151[49] = 0;
   out_4568055349565887151[50] = 0;
   out_4568055349565887151[51] = 0;
   out_4568055349565887151[52] = 0;
   out_4568055349565887151[53] = 0;
}
void h_14(double *state, double *unused, double *out_960453994518179958) {
   out_960453994518179958[0] = state[6];
   out_960453994518179958[1] = state[7];
   out_960453994518179958[2] = state[8];
}
void H_14(double *state, double *unused, double *out_5319022380573038879) {
   out_5319022380573038879[0] = 0;
   out_5319022380573038879[1] = 0;
   out_5319022380573038879[2] = 0;
   out_5319022380573038879[3] = 0;
   out_5319022380573038879[4] = 0;
   out_5319022380573038879[5] = 0;
   out_5319022380573038879[6] = 1;
   out_5319022380573038879[7] = 0;
   out_5319022380573038879[8] = 0;
   out_5319022380573038879[9] = 0;
   out_5319022380573038879[10] = 0;
   out_5319022380573038879[11] = 0;
   out_5319022380573038879[12] = 0;
   out_5319022380573038879[13] = 0;
   out_5319022380573038879[14] = 0;
   out_5319022380573038879[15] = 0;
   out_5319022380573038879[16] = 0;
   out_5319022380573038879[17] = 0;
   out_5319022380573038879[18] = 0;
   out_5319022380573038879[19] = 0;
   out_5319022380573038879[20] = 0;
   out_5319022380573038879[21] = 0;
   out_5319022380573038879[22] = 0;
   out_5319022380573038879[23] = 0;
   out_5319022380573038879[24] = 0;
   out_5319022380573038879[25] = 1;
   out_5319022380573038879[26] = 0;
   out_5319022380573038879[27] = 0;
   out_5319022380573038879[28] = 0;
   out_5319022380573038879[29] = 0;
   out_5319022380573038879[30] = 0;
   out_5319022380573038879[31] = 0;
   out_5319022380573038879[32] = 0;
   out_5319022380573038879[33] = 0;
   out_5319022380573038879[34] = 0;
   out_5319022380573038879[35] = 0;
   out_5319022380573038879[36] = 0;
   out_5319022380573038879[37] = 0;
   out_5319022380573038879[38] = 0;
   out_5319022380573038879[39] = 0;
   out_5319022380573038879[40] = 0;
   out_5319022380573038879[41] = 0;
   out_5319022380573038879[42] = 0;
   out_5319022380573038879[43] = 0;
   out_5319022380573038879[44] = 1;
   out_5319022380573038879[45] = 0;
   out_5319022380573038879[46] = 0;
   out_5319022380573038879[47] = 0;
   out_5319022380573038879[48] = 0;
   out_5319022380573038879[49] = 0;
   out_5319022380573038879[50] = 0;
   out_5319022380573038879[51] = 0;
   out_5319022380573038879[52] = 0;
   out_5319022380573038879[53] = 0;
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
void pose_err_fun(double *nom_x, double *delta_x, double *out_2669393212407968939) {
  err_fun(nom_x, delta_x, out_2669393212407968939);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_6589919633801240756) {
  inv_err_fun(nom_x, true_x, out_6589919633801240756);
}
void pose_H_mod_fun(double *state, double *out_8225234534934843580) {
  H_mod_fun(state, out_8225234534934843580);
}
void pose_f_fun(double *state, double dt, double *out_3713400227530287176) {
  f_fun(state,  dt, out_3713400227530287176);
}
void pose_F_fun(double *state, double dt, double *out_7623311308597317329) {
  F_fun(state,  dt, out_7623311308597317329);
}
void pose_h_4(double *state, double *unused, double *out_1299539042272213645) {
  h_4(state, unused, out_1299539042272213645);
}
void pose_H_4(double *state, double *unused, double *out_1355781524233554350) {
  H_4(state, unused, out_1355781524233554350);
}
void pose_h_10(double *state, double *unused, double *out_4564875173987417445) {
  h_10(state, unused, out_4564875173987417445);
}
void pose_H_10(double *state, double *unused, double *out_6426002362757736416) {
  H_10(state, unused, out_6426002362757736416);
}
void pose_h_13(double *state, double *unused, double *out_8828664930147326382) {
  h_13(state, unused, out_8828664930147326382);
}
void pose_H_13(double *state, double *unused, double *out_4568055349565887151) {
  H_13(state, unused, out_4568055349565887151);
}
void pose_h_14(double *state, double *unused, double *out_960453994518179958) {
  h_14(state, unused, out_960453994518179958);
}
void pose_H_14(double *state, double *unused, double *out_5319022380573038879) {
  H_14(state, unused, out_5319022380573038879);
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
