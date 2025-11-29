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
void err_fun(double *nom_x, double *delta_x, double *out_6859609651364947806) {
   out_6859609651364947806[0] = delta_x[0] + nom_x[0];
   out_6859609651364947806[1] = delta_x[1] + nom_x[1];
   out_6859609651364947806[2] = delta_x[2] + nom_x[2];
   out_6859609651364947806[3] = delta_x[3] + nom_x[3];
   out_6859609651364947806[4] = delta_x[4] + nom_x[4];
   out_6859609651364947806[5] = delta_x[5] + nom_x[5];
   out_6859609651364947806[6] = delta_x[6] + nom_x[6];
   out_6859609651364947806[7] = delta_x[7] + nom_x[7];
   out_6859609651364947806[8] = delta_x[8] + nom_x[8];
   out_6859609651364947806[9] = delta_x[9] + nom_x[9];
   out_6859609651364947806[10] = delta_x[10] + nom_x[10];
   out_6859609651364947806[11] = delta_x[11] + nom_x[11];
   out_6859609651364947806[12] = delta_x[12] + nom_x[12];
   out_6859609651364947806[13] = delta_x[13] + nom_x[13];
   out_6859609651364947806[14] = delta_x[14] + nom_x[14];
   out_6859609651364947806[15] = delta_x[15] + nom_x[15];
   out_6859609651364947806[16] = delta_x[16] + nom_x[16];
   out_6859609651364947806[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_1490819210114812961) {
   out_1490819210114812961[0] = -nom_x[0] + true_x[0];
   out_1490819210114812961[1] = -nom_x[1] + true_x[1];
   out_1490819210114812961[2] = -nom_x[2] + true_x[2];
   out_1490819210114812961[3] = -nom_x[3] + true_x[3];
   out_1490819210114812961[4] = -nom_x[4] + true_x[4];
   out_1490819210114812961[5] = -nom_x[5] + true_x[5];
   out_1490819210114812961[6] = -nom_x[6] + true_x[6];
   out_1490819210114812961[7] = -nom_x[7] + true_x[7];
   out_1490819210114812961[8] = -nom_x[8] + true_x[8];
   out_1490819210114812961[9] = -nom_x[9] + true_x[9];
   out_1490819210114812961[10] = -nom_x[10] + true_x[10];
   out_1490819210114812961[11] = -nom_x[11] + true_x[11];
   out_1490819210114812961[12] = -nom_x[12] + true_x[12];
   out_1490819210114812961[13] = -nom_x[13] + true_x[13];
   out_1490819210114812961[14] = -nom_x[14] + true_x[14];
   out_1490819210114812961[15] = -nom_x[15] + true_x[15];
   out_1490819210114812961[16] = -nom_x[16] + true_x[16];
   out_1490819210114812961[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_1066489817404091299) {
   out_1066489817404091299[0] = 1.0;
   out_1066489817404091299[1] = 0.0;
   out_1066489817404091299[2] = 0.0;
   out_1066489817404091299[3] = 0.0;
   out_1066489817404091299[4] = 0.0;
   out_1066489817404091299[5] = 0.0;
   out_1066489817404091299[6] = 0.0;
   out_1066489817404091299[7] = 0.0;
   out_1066489817404091299[8] = 0.0;
   out_1066489817404091299[9] = 0.0;
   out_1066489817404091299[10] = 0.0;
   out_1066489817404091299[11] = 0.0;
   out_1066489817404091299[12] = 0.0;
   out_1066489817404091299[13] = 0.0;
   out_1066489817404091299[14] = 0.0;
   out_1066489817404091299[15] = 0.0;
   out_1066489817404091299[16] = 0.0;
   out_1066489817404091299[17] = 0.0;
   out_1066489817404091299[18] = 0.0;
   out_1066489817404091299[19] = 1.0;
   out_1066489817404091299[20] = 0.0;
   out_1066489817404091299[21] = 0.0;
   out_1066489817404091299[22] = 0.0;
   out_1066489817404091299[23] = 0.0;
   out_1066489817404091299[24] = 0.0;
   out_1066489817404091299[25] = 0.0;
   out_1066489817404091299[26] = 0.0;
   out_1066489817404091299[27] = 0.0;
   out_1066489817404091299[28] = 0.0;
   out_1066489817404091299[29] = 0.0;
   out_1066489817404091299[30] = 0.0;
   out_1066489817404091299[31] = 0.0;
   out_1066489817404091299[32] = 0.0;
   out_1066489817404091299[33] = 0.0;
   out_1066489817404091299[34] = 0.0;
   out_1066489817404091299[35] = 0.0;
   out_1066489817404091299[36] = 0.0;
   out_1066489817404091299[37] = 0.0;
   out_1066489817404091299[38] = 1.0;
   out_1066489817404091299[39] = 0.0;
   out_1066489817404091299[40] = 0.0;
   out_1066489817404091299[41] = 0.0;
   out_1066489817404091299[42] = 0.0;
   out_1066489817404091299[43] = 0.0;
   out_1066489817404091299[44] = 0.0;
   out_1066489817404091299[45] = 0.0;
   out_1066489817404091299[46] = 0.0;
   out_1066489817404091299[47] = 0.0;
   out_1066489817404091299[48] = 0.0;
   out_1066489817404091299[49] = 0.0;
   out_1066489817404091299[50] = 0.0;
   out_1066489817404091299[51] = 0.0;
   out_1066489817404091299[52] = 0.0;
   out_1066489817404091299[53] = 0.0;
   out_1066489817404091299[54] = 0.0;
   out_1066489817404091299[55] = 0.0;
   out_1066489817404091299[56] = 0.0;
   out_1066489817404091299[57] = 1.0;
   out_1066489817404091299[58] = 0.0;
   out_1066489817404091299[59] = 0.0;
   out_1066489817404091299[60] = 0.0;
   out_1066489817404091299[61] = 0.0;
   out_1066489817404091299[62] = 0.0;
   out_1066489817404091299[63] = 0.0;
   out_1066489817404091299[64] = 0.0;
   out_1066489817404091299[65] = 0.0;
   out_1066489817404091299[66] = 0.0;
   out_1066489817404091299[67] = 0.0;
   out_1066489817404091299[68] = 0.0;
   out_1066489817404091299[69] = 0.0;
   out_1066489817404091299[70] = 0.0;
   out_1066489817404091299[71] = 0.0;
   out_1066489817404091299[72] = 0.0;
   out_1066489817404091299[73] = 0.0;
   out_1066489817404091299[74] = 0.0;
   out_1066489817404091299[75] = 0.0;
   out_1066489817404091299[76] = 1.0;
   out_1066489817404091299[77] = 0.0;
   out_1066489817404091299[78] = 0.0;
   out_1066489817404091299[79] = 0.0;
   out_1066489817404091299[80] = 0.0;
   out_1066489817404091299[81] = 0.0;
   out_1066489817404091299[82] = 0.0;
   out_1066489817404091299[83] = 0.0;
   out_1066489817404091299[84] = 0.0;
   out_1066489817404091299[85] = 0.0;
   out_1066489817404091299[86] = 0.0;
   out_1066489817404091299[87] = 0.0;
   out_1066489817404091299[88] = 0.0;
   out_1066489817404091299[89] = 0.0;
   out_1066489817404091299[90] = 0.0;
   out_1066489817404091299[91] = 0.0;
   out_1066489817404091299[92] = 0.0;
   out_1066489817404091299[93] = 0.0;
   out_1066489817404091299[94] = 0.0;
   out_1066489817404091299[95] = 1.0;
   out_1066489817404091299[96] = 0.0;
   out_1066489817404091299[97] = 0.0;
   out_1066489817404091299[98] = 0.0;
   out_1066489817404091299[99] = 0.0;
   out_1066489817404091299[100] = 0.0;
   out_1066489817404091299[101] = 0.0;
   out_1066489817404091299[102] = 0.0;
   out_1066489817404091299[103] = 0.0;
   out_1066489817404091299[104] = 0.0;
   out_1066489817404091299[105] = 0.0;
   out_1066489817404091299[106] = 0.0;
   out_1066489817404091299[107] = 0.0;
   out_1066489817404091299[108] = 0.0;
   out_1066489817404091299[109] = 0.0;
   out_1066489817404091299[110] = 0.0;
   out_1066489817404091299[111] = 0.0;
   out_1066489817404091299[112] = 0.0;
   out_1066489817404091299[113] = 0.0;
   out_1066489817404091299[114] = 1.0;
   out_1066489817404091299[115] = 0.0;
   out_1066489817404091299[116] = 0.0;
   out_1066489817404091299[117] = 0.0;
   out_1066489817404091299[118] = 0.0;
   out_1066489817404091299[119] = 0.0;
   out_1066489817404091299[120] = 0.0;
   out_1066489817404091299[121] = 0.0;
   out_1066489817404091299[122] = 0.0;
   out_1066489817404091299[123] = 0.0;
   out_1066489817404091299[124] = 0.0;
   out_1066489817404091299[125] = 0.0;
   out_1066489817404091299[126] = 0.0;
   out_1066489817404091299[127] = 0.0;
   out_1066489817404091299[128] = 0.0;
   out_1066489817404091299[129] = 0.0;
   out_1066489817404091299[130] = 0.0;
   out_1066489817404091299[131] = 0.0;
   out_1066489817404091299[132] = 0.0;
   out_1066489817404091299[133] = 1.0;
   out_1066489817404091299[134] = 0.0;
   out_1066489817404091299[135] = 0.0;
   out_1066489817404091299[136] = 0.0;
   out_1066489817404091299[137] = 0.0;
   out_1066489817404091299[138] = 0.0;
   out_1066489817404091299[139] = 0.0;
   out_1066489817404091299[140] = 0.0;
   out_1066489817404091299[141] = 0.0;
   out_1066489817404091299[142] = 0.0;
   out_1066489817404091299[143] = 0.0;
   out_1066489817404091299[144] = 0.0;
   out_1066489817404091299[145] = 0.0;
   out_1066489817404091299[146] = 0.0;
   out_1066489817404091299[147] = 0.0;
   out_1066489817404091299[148] = 0.0;
   out_1066489817404091299[149] = 0.0;
   out_1066489817404091299[150] = 0.0;
   out_1066489817404091299[151] = 0.0;
   out_1066489817404091299[152] = 1.0;
   out_1066489817404091299[153] = 0.0;
   out_1066489817404091299[154] = 0.0;
   out_1066489817404091299[155] = 0.0;
   out_1066489817404091299[156] = 0.0;
   out_1066489817404091299[157] = 0.0;
   out_1066489817404091299[158] = 0.0;
   out_1066489817404091299[159] = 0.0;
   out_1066489817404091299[160] = 0.0;
   out_1066489817404091299[161] = 0.0;
   out_1066489817404091299[162] = 0.0;
   out_1066489817404091299[163] = 0.0;
   out_1066489817404091299[164] = 0.0;
   out_1066489817404091299[165] = 0.0;
   out_1066489817404091299[166] = 0.0;
   out_1066489817404091299[167] = 0.0;
   out_1066489817404091299[168] = 0.0;
   out_1066489817404091299[169] = 0.0;
   out_1066489817404091299[170] = 0.0;
   out_1066489817404091299[171] = 1.0;
   out_1066489817404091299[172] = 0.0;
   out_1066489817404091299[173] = 0.0;
   out_1066489817404091299[174] = 0.0;
   out_1066489817404091299[175] = 0.0;
   out_1066489817404091299[176] = 0.0;
   out_1066489817404091299[177] = 0.0;
   out_1066489817404091299[178] = 0.0;
   out_1066489817404091299[179] = 0.0;
   out_1066489817404091299[180] = 0.0;
   out_1066489817404091299[181] = 0.0;
   out_1066489817404091299[182] = 0.0;
   out_1066489817404091299[183] = 0.0;
   out_1066489817404091299[184] = 0.0;
   out_1066489817404091299[185] = 0.0;
   out_1066489817404091299[186] = 0.0;
   out_1066489817404091299[187] = 0.0;
   out_1066489817404091299[188] = 0.0;
   out_1066489817404091299[189] = 0.0;
   out_1066489817404091299[190] = 1.0;
   out_1066489817404091299[191] = 0.0;
   out_1066489817404091299[192] = 0.0;
   out_1066489817404091299[193] = 0.0;
   out_1066489817404091299[194] = 0.0;
   out_1066489817404091299[195] = 0.0;
   out_1066489817404091299[196] = 0.0;
   out_1066489817404091299[197] = 0.0;
   out_1066489817404091299[198] = 0.0;
   out_1066489817404091299[199] = 0.0;
   out_1066489817404091299[200] = 0.0;
   out_1066489817404091299[201] = 0.0;
   out_1066489817404091299[202] = 0.0;
   out_1066489817404091299[203] = 0.0;
   out_1066489817404091299[204] = 0.0;
   out_1066489817404091299[205] = 0.0;
   out_1066489817404091299[206] = 0.0;
   out_1066489817404091299[207] = 0.0;
   out_1066489817404091299[208] = 0.0;
   out_1066489817404091299[209] = 1.0;
   out_1066489817404091299[210] = 0.0;
   out_1066489817404091299[211] = 0.0;
   out_1066489817404091299[212] = 0.0;
   out_1066489817404091299[213] = 0.0;
   out_1066489817404091299[214] = 0.0;
   out_1066489817404091299[215] = 0.0;
   out_1066489817404091299[216] = 0.0;
   out_1066489817404091299[217] = 0.0;
   out_1066489817404091299[218] = 0.0;
   out_1066489817404091299[219] = 0.0;
   out_1066489817404091299[220] = 0.0;
   out_1066489817404091299[221] = 0.0;
   out_1066489817404091299[222] = 0.0;
   out_1066489817404091299[223] = 0.0;
   out_1066489817404091299[224] = 0.0;
   out_1066489817404091299[225] = 0.0;
   out_1066489817404091299[226] = 0.0;
   out_1066489817404091299[227] = 0.0;
   out_1066489817404091299[228] = 1.0;
   out_1066489817404091299[229] = 0.0;
   out_1066489817404091299[230] = 0.0;
   out_1066489817404091299[231] = 0.0;
   out_1066489817404091299[232] = 0.0;
   out_1066489817404091299[233] = 0.0;
   out_1066489817404091299[234] = 0.0;
   out_1066489817404091299[235] = 0.0;
   out_1066489817404091299[236] = 0.0;
   out_1066489817404091299[237] = 0.0;
   out_1066489817404091299[238] = 0.0;
   out_1066489817404091299[239] = 0.0;
   out_1066489817404091299[240] = 0.0;
   out_1066489817404091299[241] = 0.0;
   out_1066489817404091299[242] = 0.0;
   out_1066489817404091299[243] = 0.0;
   out_1066489817404091299[244] = 0.0;
   out_1066489817404091299[245] = 0.0;
   out_1066489817404091299[246] = 0.0;
   out_1066489817404091299[247] = 1.0;
   out_1066489817404091299[248] = 0.0;
   out_1066489817404091299[249] = 0.0;
   out_1066489817404091299[250] = 0.0;
   out_1066489817404091299[251] = 0.0;
   out_1066489817404091299[252] = 0.0;
   out_1066489817404091299[253] = 0.0;
   out_1066489817404091299[254] = 0.0;
   out_1066489817404091299[255] = 0.0;
   out_1066489817404091299[256] = 0.0;
   out_1066489817404091299[257] = 0.0;
   out_1066489817404091299[258] = 0.0;
   out_1066489817404091299[259] = 0.0;
   out_1066489817404091299[260] = 0.0;
   out_1066489817404091299[261] = 0.0;
   out_1066489817404091299[262] = 0.0;
   out_1066489817404091299[263] = 0.0;
   out_1066489817404091299[264] = 0.0;
   out_1066489817404091299[265] = 0.0;
   out_1066489817404091299[266] = 1.0;
   out_1066489817404091299[267] = 0.0;
   out_1066489817404091299[268] = 0.0;
   out_1066489817404091299[269] = 0.0;
   out_1066489817404091299[270] = 0.0;
   out_1066489817404091299[271] = 0.0;
   out_1066489817404091299[272] = 0.0;
   out_1066489817404091299[273] = 0.0;
   out_1066489817404091299[274] = 0.0;
   out_1066489817404091299[275] = 0.0;
   out_1066489817404091299[276] = 0.0;
   out_1066489817404091299[277] = 0.0;
   out_1066489817404091299[278] = 0.0;
   out_1066489817404091299[279] = 0.0;
   out_1066489817404091299[280] = 0.0;
   out_1066489817404091299[281] = 0.0;
   out_1066489817404091299[282] = 0.0;
   out_1066489817404091299[283] = 0.0;
   out_1066489817404091299[284] = 0.0;
   out_1066489817404091299[285] = 1.0;
   out_1066489817404091299[286] = 0.0;
   out_1066489817404091299[287] = 0.0;
   out_1066489817404091299[288] = 0.0;
   out_1066489817404091299[289] = 0.0;
   out_1066489817404091299[290] = 0.0;
   out_1066489817404091299[291] = 0.0;
   out_1066489817404091299[292] = 0.0;
   out_1066489817404091299[293] = 0.0;
   out_1066489817404091299[294] = 0.0;
   out_1066489817404091299[295] = 0.0;
   out_1066489817404091299[296] = 0.0;
   out_1066489817404091299[297] = 0.0;
   out_1066489817404091299[298] = 0.0;
   out_1066489817404091299[299] = 0.0;
   out_1066489817404091299[300] = 0.0;
   out_1066489817404091299[301] = 0.0;
   out_1066489817404091299[302] = 0.0;
   out_1066489817404091299[303] = 0.0;
   out_1066489817404091299[304] = 1.0;
   out_1066489817404091299[305] = 0.0;
   out_1066489817404091299[306] = 0.0;
   out_1066489817404091299[307] = 0.0;
   out_1066489817404091299[308] = 0.0;
   out_1066489817404091299[309] = 0.0;
   out_1066489817404091299[310] = 0.0;
   out_1066489817404091299[311] = 0.0;
   out_1066489817404091299[312] = 0.0;
   out_1066489817404091299[313] = 0.0;
   out_1066489817404091299[314] = 0.0;
   out_1066489817404091299[315] = 0.0;
   out_1066489817404091299[316] = 0.0;
   out_1066489817404091299[317] = 0.0;
   out_1066489817404091299[318] = 0.0;
   out_1066489817404091299[319] = 0.0;
   out_1066489817404091299[320] = 0.0;
   out_1066489817404091299[321] = 0.0;
   out_1066489817404091299[322] = 0.0;
   out_1066489817404091299[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_5163101270829834523) {
   out_5163101270829834523[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_5163101270829834523[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_5163101270829834523[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_5163101270829834523[3] = dt*state[12] + state[3];
   out_5163101270829834523[4] = dt*state[13] + state[4];
   out_5163101270829834523[5] = dt*state[14] + state[5];
   out_5163101270829834523[6] = state[6];
   out_5163101270829834523[7] = state[7];
   out_5163101270829834523[8] = state[8];
   out_5163101270829834523[9] = state[9];
   out_5163101270829834523[10] = state[10];
   out_5163101270829834523[11] = state[11];
   out_5163101270829834523[12] = state[12];
   out_5163101270829834523[13] = state[13];
   out_5163101270829834523[14] = state[14];
   out_5163101270829834523[15] = state[15];
   out_5163101270829834523[16] = state[16];
   out_5163101270829834523[17] = state[17];
}
void F_fun(double *state, double dt, double *out_2904788492881068911) {
   out_2904788492881068911[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_2904788492881068911[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_2904788492881068911[2] = 0;
   out_2904788492881068911[3] = 0;
   out_2904788492881068911[4] = 0;
   out_2904788492881068911[5] = 0;
   out_2904788492881068911[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_2904788492881068911[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_2904788492881068911[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_2904788492881068911[9] = 0;
   out_2904788492881068911[10] = 0;
   out_2904788492881068911[11] = 0;
   out_2904788492881068911[12] = 0;
   out_2904788492881068911[13] = 0;
   out_2904788492881068911[14] = 0;
   out_2904788492881068911[15] = 0;
   out_2904788492881068911[16] = 0;
   out_2904788492881068911[17] = 0;
   out_2904788492881068911[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_2904788492881068911[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_2904788492881068911[20] = 0;
   out_2904788492881068911[21] = 0;
   out_2904788492881068911[22] = 0;
   out_2904788492881068911[23] = 0;
   out_2904788492881068911[24] = 0;
   out_2904788492881068911[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_2904788492881068911[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_2904788492881068911[27] = 0;
   out_2904788492881068911[28] = 0;
   out_2904788492881068911[29] = 0;
   out_2904788492881068911[30] = 0;
   out_2904788492881068911[31] = 0;
   out_2904788492881068911[32] = 0;
   out_2904788492881068911[33] = 0;
   out_2904788492881068911[34] = 0;
   out_2904788492881068911[35] = 0;
   out_2904788492881068911[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_2904788492881068911[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_2904788492881068911[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_2904788492881068911[39] = 0;
   out_2904788492881068911[40] = 0;
   out_2904788492881068911[41] = 0;
   out_2904788492881068911[42] = 0;
   out_2904788492881068911[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_2904788492881068911[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_2904788492881068911[45] = 0;
   out_2904788492881068911[46] = 0;
   out_2904788492881068911[47] = 0;
   out_2904788492881068911[48] = 0;
   out_2904788492881068911[49] = 0;
   out_2904788492881068911[50] = 0;
   out_2904788492881068911[51] = 0;
   out_2904788492881068911[52] = 0;
   out_2904788492881068911[53] = 0;
   out_2904788492881068911[54] = 0;
   out_2904788492881068911[55] = 0;
   out_2904788492881068911[56] = 0;
   out_2904788492881068911[57] = 1;
   out_2904788492881068911[58] = 0;
   out_2904788492881068911[59] = 0;
   out_2904788492881068911[60] = 0;
   out_2904788492881068911[61] = 0;
   out_2904788492881068911[62] = 0;
   out_2904788492881068911[63] = 0;
   out_2904788492881068911[64] = 0;
   out_2904788492881068911[65] = 0;
   out_2904788492881068911[66] = dt;
   out_2904788492881068911[67] = 0;
   out_2904788492881068911[68] = 0;
   out_2904788492881068911[69] = 0;
   out_2904788492881068911[70] = 0;
   out_2904788492881068911[71] = 0;
   out_2904788492881068911[72] = 0;
   out_2904788492881068911[73] = 0;
   out_2904788492881068911[74] = 0;
   out_2904788492881068911[75] = 0;
   out_2904788492881068911[76] = 1;
   out_2904788492881068911[77] = 0;
   out_2904788492881068911[78] = 0;
   out_2904788492881068911[79] = 0;
   out_2904788492881068911[80] = 0;
   out_2904788492881068911[81] = 0;
   out_2904788492881068911[82] = 0;
   out_2904788492881068911[83] = 0;
   out_2904788492881068911[84] = 0;
   out_2904788492881068911[85] = dt;
   out_2904788492881068911[86] = 0;
   out_2904788492881068911[87] = 0;
   out_2904788492881068911[88] = 0;
   out_2904788492881068911[89] = 0;
   out_2904788492881068911[90] = 0;
   out_2904788492881068911[91] = 0;
   out_2904788492881068911[92] = 0;
   out_2904788492881068911[93] = 0;
   out_2904788492881068911[94] = 0;
   out_2904788492881068911[95] = 1;
   out_2904788492881068911[96] = 0;
   out_2904788492881068911[97] = 0;
   out_2904788492881068911[98] = 0;
   out_2904788492881068911[99] = 0;
   out_2904788492881068911[100] = 0;
   out_2904788492881068911[101] = 0;
   out_2904788492881068911[102] = 0;
   out_2904788492881068911[103] = 0;
   out_2904788492881068911[104] = dt;
   out_2904788492881068911[105] = 0;
   out_2904788492881068911[106] = 0;
   out_2904788492881068911[107] = 0;
   out_2904788492881068911[108] = 0;
   out_2904788492881068911[109] = 0;
   out_2904788492881068911[110] = 0;
   out_2904788492881068911[111] = 0;
   out_2904788492881068911[112] = 0;
   out_2904788492881068911[113] = 0;
   out_2904788492881068911[114] = 1;
   out_2904788492881068911[115] = 0;
   out_2904788492881068911[116] = 0;
   out_2904788492881068911[117] = 0;
   out_2904788492881068911[118] = 0;
   out_2904788492881068911[119] = 0;
   out_2904788492881068911[120] = 0;
   out_2904788492881068911[121] = 0;
   out_2904788492881068911[122] = 0;
   out_2904788492881068911[123] = 0;
   out_2904788492881068911[124] = 0;
   out_2904788492881068911[125] = 0;
   out_2904788492881068911[126] = 0;
   out_2904788492881068911[127] = 0;
   out_2904788492881068911[128] = 0;
   out_2904788492881068911[129] = 0;
   out_2904788492881068911[130] = 0;
   out_2904788492881068911[131] = 0;
   out_2904788492881068911[132] = 0;
   out_2904788492881068911[133] = 1;
   out_2904788492881068911[134] = 0;
   out_2904788492881068911[135] = 0;
   out_2904788492881068911[136] = 0;
   out_2904788492881068911[137] = 0;
   out_2904788492881068911[138] = 0;
   out_2904788492881068911[139] = 0;
   out_2904788492881068911[140] = 0;
   out_2904788492881068911[141] = 0;
   out_2904788492881068911[142] = 0;
   out_2904788492881068911[143] = 0;
   out_2904788492881068911[144] = 0;
   out_2904788492881068911[145] = 0;
   out_2904788492881068911[146] = 0;
   out_2904788492881068911[147] = 0;
   out_2904788492881068911[148] = 0;
   out_2904788492881068911[149] = 0;
   out_2904788492881068911[150] = 0;
   out_2904788492881068911[151] = 0;
   out_2904788492881068911[152] = 1;
   out_2904788492881068911[153] = 0;
   out_2904788492881068911[154] = 0;
   out_2904788492881068911[155] = 0;
   out_2904788492881068911[156] = 0;
   out_2904788492881068911[157] = 0;
   out_2904788492881068911[158] = 0;
   out_2904788492881068911[159] = 0;
   out_2904788492881068911[160] = 0;
   out_2904788492881068911[161] = 0;
   out_2904788492881068911[162] = 0;
   out_2904788492881068911[163] = 0;
   out_2904788492881068911[164] = 0;
   out_2904788492881068911[165] = 0;
   out_2904788492881068911[166] = 0;
   out_2904788492881068911[167] = 0;
   out_2904788492881068911[168] = 0;
   out_2904788492881068911[169] = 0;
   out_2904788492881068911[170] = 0;
   out_2904788492881068911[171] = 1;
   out_2904788492881068911[172] = 0;
   out_2904788492881068911[173] = 0;
   out_2904788492881068911[174] = 0;
   out_2904788492881068911[175] = 0;
   out_2904788492881068911[176] = 0;
   out_2904788492881068911[177] = 0;
   out_2904788492881068911[178] = 0;
   out_2904788492881068911[179] = 0;
   out_2904788492881068911[180] = 0;
   out_2904788492881068911[181] = 0;
   out_2904788492881068911[182] = 0;
   out_2904788492881068911[183] = 0;
   out_2904788492881068911[184] = 0;
   out_2904788492881068911[185] = 0;
   out_2904788492881068911[186] = 0;
   out_2904788492881068911[187] = 0;
   out_2904788492881068911[188] = 0;
   out_2904788492881068911[189] = 0;
   out_2904788492881068911[190] = 1;
   out_2904788492881068911[191] = 0;
   out_2904788492881068911[192] = 0;
   out_2904788492881068911[193] = 0;
   out_2904788492881068911[194] = 0;
   out_2904788492881068911[195] = 0;
   out_2904788492881068911[196] = 0;
   out_2904788492881068911[197] = 0;
   out_2904788492881068911[198] = 0;
   out_2904788492881068911[199] = 0;
   out_2904788492881068911[200] = 0;
   out_2904788492881068911[201] = 0;
   out_2904788492881068911[202] = 0;
   out_2904788492881068911[203] = 0;
   out_2904788492881068911[204] = 0;
   out_2904788492881068911[205] = 0;
   out_2904788492881068911[206] = 0;
   out_2904788492881068911[207] = 0;
   out_2904788492881068911[208] = 0;
   out_2904788492881068911[209] = 1;
   out_2904788492881068911[210] = 0;
   out_2904788492881068911[211] = 0;
   out_2904788492881068911[212] = 0;
   out_2904788492881068911[213] = 0;
   out_2904788492881068911[214] = 0;
   out_2904788492881068911[215] = 0;
   out_2904788492881068911[216] = 0;
   out_2904788492881068911[217] = 0;
   out_2904788492881068911[218] = 0;
   out_2904788492881068911[219] = 0;
   out_2904788492881068911[220] = 0;
   out_2904788492881068911[221] = 0;
   out_2904788492881068911[222] = 0;
   out_2904788492881068911[223] = 0;
   out_2904788492881068911[224] = 0;
   out_2904788492881068911[225] = 0;
   out_2904788492881068911[226] = 0;
   out_2904788492881068911[227] = 0;
   out_2904788492881068911[228] = 1;
   out_2904788492881068911[229] = 0;
   out_2904788492881068911[230] = 0;
   out_2904788492881068911[231] = 0;
   out_2904788492881068911[232] = 0;
   out_2904788492881068911[233] = 0;
   out_2904788492881068911[234] = 0;
   out_2904788492881068911[235] = 0;
   out_2904788492881068911[236] = 0;
   out_2904788492881068911[237] = 0;
   out_2904788492881068911[238] = 0;
   out_2904788492881068911[239] = 0;
   out_2904788492881068911[240] = 0;
   out_2904788492881068911[241] = 0;
   out_2904788492881068911[242] = 0;
   out_2904788492881068911[243] = 0;
   out_2904788492881068911[244] = 0;
   out_2904788492881068911[245] = 0;
   out_2904788492881068911[246] = 0;
   out_2904788492881068911[247] = 1;
   out_2904788492881068911[248] = 0;
   out_2904788492881068911[249] = 0;
   out_2904788492881068911[250] = 0;
   out_2904788492881068911[251] = 0;
   out_2904788492881068911[252] = 0;
   out_2904788492881068911[253] = 0;
   out_2904788492881068911[254] = 0;
   out_2904788492881068911[255] = 0;
   out_2904788492881068911[256] = 0;
   out_2904788492881068911[257] = 0;
   out_2904788492881068911[258] = 0;
   out_2904788492881068911[259] = 0;
   out_2904788492881068911[260] = 0;
   out_2904788492881068911[261] = 0;
   out_2904788492881068911[262] = 0;
   out_2904788492881068911[263] = 0;
   out_2904788492881068911[264] = 0;
   out_2904788492881068911[265] = 0;
   out_2904788492881068911[266] = 1;
   out_2904788492881068911[267] = 0;
   out_2904788492881068911[268] = 0;
   out_2904788492881068911[269] = 0;
   out_2904788492881068911[270] = 0;
   out_2904788492881068911[271] = 0;
   out_2904788492881068911[272] = 0;
   out_2904788492881068911[273] = 0;
   out_2904788492881068911[274] = 0;
   out_2904788492881068911[275] = 0;
   out_2904788492881068911[276] = 0;
   out_2904788492881068911[277] = 0;
   out_2904788492881068911[278] = 0;
   out_2904788492881068911[279] = 0;
   out_2904788492881068911[280] = 0;
   out_2904788492881068911[281] = 0;
   out_2904788492881068911[282] = 0;
   out_2904788492881068911[283] = 0;
   out_2904788492881068911[284] = 0;
   out_2904788492881068911[285] = 1;
   out_2904788492881068911[286] = 0;
   out_2904788492881068911[287] = 0;
   out_2904788492881068911[288] = 0;
   out_2904788492881068911[289] = 0;
   out_2904788492881068911[290] = 0;
   out_2904788492881068911[291] = 0;
   out_2904788492881068911[292] = 0;
   out_2904788492881068911[293] = 0;
   out_2904788492881068911[294] = 0;
   out_2904788492881068911[295] = 0;
   out_2904788492881068911[296] = 0;
   out_2904788492881068911[297] = 0;
   out_2904788492881068911[298] = 0;
   out_2904788492881068911[299] = 0;
   out_2904788492881068911[300] = 0;
   out_2904788492881068911[301] = 0;
   out_2904788492881068911[302] = 0;
   out_2904788492881068911[303] = 0;
   out_2904788492881068911[304] = 1;
   out_2904788492881068911[305] = 0;
   out_2904788492881068911[306] = 0;
   out_2904788492881068911[307] = 0;
   out_2904788492881068911[308] = 0;
   out_2904788492881068911[309] = 0;
   out_2904788492881068911[310] = 0;
   out_2904788492881068911[311] = 0;
   out_2904788492881068911[312] = 0;
   out_2904788492881068911[313] = 0;
   out_2904788492881068911[314] = 0;
   out_2904788492881068911[315] = 0;
   out_2904788492881068911[316] = 0;
   out_2904788492881068911[317] = 0;
   out_2904788492881068911[318] = 0;
   out_2904788492881068911[319] = 0;
   out_2904788492881068911[320] = 0;
   out_2904788492881068911[321] = 0;
   out_2904788492881068911[322] = 0;
   out_2904788492881068911[323] = 1;
}
void h_4(double *state, double *unused, double *out_7771273734247816938) {
   out_7771273734247816938[0] = state[6] + state[9];
   out_7771273734247816938[1] = state[7] + state[10];
   out_7771273734247816938[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_6914571624156050020) {
   out_6914571624156050020[0] = 0;
   out_6914571624156050020[1] = 0;
   out_6914571624156050020[2] = 0;
   out_6914571624156050020[3] = 0;
   out_6914571624156050020[4] = 0;
   out_6914571624156050020[5] = 0;
   out_6914571624156050020[6] = 1;
   out_6914571624156050020[7] = 0;
   out_6914571624156050020[8] = 0;
   out_6914571624156050020[9] = 1;
   out_6914571624156050020[10] = 0;
   out_6914571624156050020[11] = 0;
   out_6914571624156050020[12] = 0;
   out_6914571624156050020[13] = 0;
   out_6914571624156050020[14] = 0;
   out_6914571624156050020[15] = 0;
   out_6914571624156050020[16] = 0;
   out_6914571624156050020[17] = 0;
   out_6914571624156050020[18] = 0;
   out_6914571624156050020[19] = 0;
   out_6914571624156050020[20] = 0;
   out_6914571624156050020[21] = 0;
   out_6914571624156050020[22] = 0;
   out_6914571624156050020[23] = 0;
   out_6914571624156050020[24] = 0;
   out_6914571624156050020[25] = 1;
   out_6914571624156050020[26] = 0;
   out_6914571624156050020[27] = 0;
   out_6914571624156050020[28] = 1;
   out_6914571624156050020[29] = 0;
   out_6914571624156050020[30] = 0;
   out_6914571624156050020[31] = 0;
   out_6914571624156050020[32] = 0;
   out_6914571624156050020[33] = 0;
   out_6914571624156050020[34] = 0;
   out_6914571624156050020[35] = 0;
   out_6914571624156050020[36] = 0;
   out_6914571624156050020[37] = 0;
   out_6914571624156050020[38] = 0;
   out_6914571624156050020[39] = 0;
   out_6914571624156050020[40] = 0;
   out_6914571624156050020[41] = 0;
   out_6914571624156050020[42] = 0;
   out_6914571624156050020[43] = 0;
   out_6914571624156050020[44] = 1;
   out_6914571624156050020[45] = 0;
   out_6914571624156050020[46] = 0;
   out_6914571624156050020[47] = 1;
   out_6914571624156050020[48] = 0;
   out_6914571624156050020[49] = 0;
   out_6914571624156050020[50] = 0;
   out_6914571624156050020[51] = 0;
   out_6914571624156050020[52] = 0;
   out_6914571624156050020[53] = 0;
}
void h_10(double *state, double *unused, double *out_6177822575693060145) {
   out_6177822575693060145[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_6177822575693060145[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_6177822575693060145[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_2577262322223255437) {
   out_2577262322223255437[0] = 0;
   out_2577262322223255437[1] = 9.8100000000000005*cos(state[1]);
   out_2577262322223255437[2] = 0;
   out_2577262322223255437[3] = 0;
   out_2577262322223255437[4] = -state[8];
   out_2577262322223255437[5] = state[7];
   out_2577262322223255437[6] = 0;
   out_2577262322223255437[7] = state[5];
   out_2577262322223255437[8] = -state[4];
   out_2577262322223255437[9] = 0;
   out_2577262322223255437[10] = 0;
   out_2577262322223255437[11] = 0;
   out_2577262322223255437[12] = 1;
   out_2577262322223255437[13] = 0;
   out_2577262322223255437[14] = 0;
   out_2577262322223255437[15] = 1;
   out_2577262322223255437[16] = 0;
   out_2577262322223255437[17] = 0;
   out_2577262322223255437[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_2577262322223255437[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_2577262322223255437[20] = 0;
   out_2577262322223255437[21] = state[8];
   out_2577262322223255437[22] = 0;
   out_2577262322223255437[23] = -state[6];
   out_2577262322223255437[24] = -state[5];
   out_2577262322223255437[25] = 0;
   out_2577262322223255437[26] = state[3];
   out_2577262322223255437[27] = 0;
   out_2577262322223255437[28] = 0;
   out_2577262322223255437[29] = 0;
   out_2577262322223255437[30] = 0;
   out_2577262322223255437[31] = 1;
   out_2577262322223255437[32] = 0;
   out_2577262322223255437[33] = 0;
   out_2577262322223255437[34] = 1;
   out_2577262322223255437[35] = 0;
   out_2577262322223255437[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_2577262322223255437[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_2577262322223255437[38] = 0;
   out_2577262322223255437[39] = -state[7];
   out_2577262322223255437[40] = state[6];
   out_2577262322223255437[41] = 0;
   out_2577262322223255437[42] = state[4];
   out_2577262322223255437[43] = -state[3];
   out_2577262322223255437[44] = 0;
   out_2577262322223255437[45] = 0;
   out_2577262322223255437[46] = 0;
   out_2577262322223255437[47] = 0;
   out_2577262322223255437[48] = 0;
   out_2577262322223255437[49] = 0;
   out_2577262322223255437[50] = 1;
   out_2577262322223255437[51] = 0;
   out_2577262322223255437[52] = 0;
   out_2577262322223255437[53] = 1;
}
void h_13(double *state, double *unused, double *out_3327759072994423416) {
   out_3327759072994423416[0] = state[3];
   out_3327759072994423416[1] = state[4];
   out_3327759072994423416[2] = state[5];
}
void H_13(double *state, double *unused, double *out_3702297798823717219) {
   out_3702297798823717219[0] = 0;
   out_3702297798823717219[1] = 0;
   out_3702297798823717219[2] = 0;
   out_3702297798823717219[3] = 1;
   out_3702297798823717219[4] = 0;
   out_3702297798823717219[5] = 0;
   out_3702297798823717219[6] = 0;
   out_3702297798823717219[7] = 0;
   out_3702297798823717219[8] = 0;
   out_3702297798823717219[9] = 0;
   out_3702297798823717219[10] = 0;
   out_3702297798823717219[11] = 0;
   out_3702297798823717219[12] = 0;
   out_3702297798823717219[13] = 0;
   out_3702297798823717219[14] = 0;
   out_3702297798823717219[15] = 0;
   out_3702297798823717219[16] = 0;
   out_3702297798823717219[17] = 0;
   out_3702297798823717219[18] = 0;
   out_3702297798823717219[19] = 0;
   out_3702297798823717219[20] = 0;
   out_3702297798823717219[21] = 0;
   out_3702297798823717219[22] = 1;
   out_3702297798823717219[23] = 0;
   out_3702297798823717219[24] = 0;
   out_3702297798823717219[25] = 0;
   out_3702297798823717219[26] = 0;
   out_3702297798823717219[27] = 0;
   out_3702297798823717219[28] = 0;
   out_3702297798823717219[29] = 0;
   out_3702297798823717219[30] = 0;
   out_3702297798823717219[31] = 0;
   out_3702297798823717219[32] = 0;
   out_3702297798823717219[33] = 0;
   out_3702297798823717219[34] = 0;
   out_3702297798823717219[35] = 0;
   out_3702297798823717219[36] = 0;
   out_3702297798823717219[37] = 0;
   out_3702297798823717219[38] = 0;
   out_3702297798823717219[39] = 0;
   out_3702297798823717219[40] = 0;
   out_3702297798823717219[41] = 1;
   out_3702297798823717219[42] = 0;
   out_3702297798823717219[43] = 0;
   out_3702297798823717219[44] = 0;
   out_3702297798823717219[45] = 0;
   out_3702297798823717219[46] = 0;
   out_3702297798823717219[47] = 0;
   out_3702297798823717219[48] = 0;
   out_3702297798823717219[49] = 0;
   out_3702297798823717219[50] = 0;
   out_3702297798823717219[51] = 0;
   out_3702297798823717219[52] = 0;
   out_3702297798823717219[53] = 0;
}
void h_14(double *state, double *unused, double *out_4339241047534864282) {
   out_4339241047534864282[0] = state[6];
   out_4339241047534864282[1] = state[7];
   out_4339241047534864282[2] = state[8];
}
void H_14(double *state, double *unused, double *out_2951330767816565491) {
   out_2951330767816565491[0] = 0;
   out_2951330767816565491[1] = 0;
   out_2951330767816565491[2] = 0;
   out_2951330767816565491[3] = 0;
   out_2951330767816565491[4] = 0;
   out_2951330767816565491[5] = 0;
   out_2951330767816565491[6] = 1;
   out_2951330767816565491[7] = 0;
   out_2951330767816565491[8] = 0;
   out_2951330767816565491[9] = 0;
   out_2951330767816565491[10] = 0;
   out_2951330767816565491[11] = 0;
   out_2951330767816565491[12] = 0;
   out_2951330767816565491[13] = 0;
   out_2951330767816565491[14] = 0;
   out_2951330767816565491[15] = 0;
   out_2951330767816565491[16] = 0;
   out_2951330767816565491[17] = 0;
   out_2951330767816565491[18] = 0;
   out_2951330767816565491[19] = 0;
   out_2951330767816565491[20] = 0;
   out_2951330767816565491[21] = 0;
   out_2951330767816565491[22] = 0;
   out_2951330767816565491[23] = 0;
   out_2951330767816565491[24] = 0;
   out_2951330767816565491[25] = 1;
   out_2951330767816565491[26] = 0;
   out_2951330767816565491[27] = 0;
   out_2951330767816565491[28] = 0;
   out_2951330767816565491[29] = 0;
   out_2951330767816565491[30] = 0;
   out_2951330767816565491[31] = 0;
   out_2951330767816565491[32] = 0;
   out_2951330767816565491[33] = 0;
   out_2951330767816565491[34] = 0;
   out_2951330767816565491[35] = 0;
   out_2951330767816565491[36] = 0;
   out_2951330767816565491[37] = 0;
   out_2951330767816565491[38] = 0;
   out_2951330767816565491[39] = 0;
   out_2951330767816565491[40] = 0;
   out_2951330767816565491[41] = 0;
   out_2951330767816565491[42] = 0;
   out_2951330767816565491[43] = 0;
   out_2951330767816565491[44] = 1;
   out_2951330767816565491[45] = 0;
   out_2951330767816565491[46] = 0;
   out_2951330767816565491[47] = 0;
   out_2951330767816565491[48] = 0;
   out_2951330767816565491[49] = 0;
   out_2951330767816565491[50] = 0;
   out_2951330767816565491[51] = 0;
   out_2951330767816565491[52] = 0;
   out_2951330767816565491[53] = 0;
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
void pose_err_fun(double *nom_x, double *delta_x, double *out_6859609651364947806) {
  err_fun(nom_x, delta_x, out_6859609651364947806);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_1490819210114812961) {
  inv_err_fun(nom_x, true_x, out_1490819210114812961);
}
void pose_H_mod_fun(double *state, double *out_1066489817404091299) {
  H_mod_fun(state, out_1066489817404091299);
}
void pose_f_fun(double *state, double dt, double *out_5163101270829834523) {
  f_fun(state,  dt, out_5163101270829834523);
}
void pose_F_fun(double *state, double dt, double *out_2904788492881068911) {
  F_fun(state,  dt, out_2904788492881068911);
}
void pose_h_4(double *state, double *unused, double *out_7771273734247816938) {
  h_4(state, unused, out_7771273734247816938);
}
void pose_H_4(double *state, double *unused, double *out_6914571624156050020) {
  H_4(state, unused, out_6914571624156050020);
}
void pose_h_10(double *state, double *unused, double *out_6177822575693060145) {
  h_10(state, unused, out_6177822575693060145);
}
void pose_H_10(double *state, double *unused, double *out_2577262322223255437) {
  H_10(state, unused, out_2577262322223255437);
}
void pose_h_13(double *state, double *unused, double *out_3327759072994423416) {
  h_13(state, unused, out_3327759072994423416);
}
void pose_H_13(double *state, double *unused, double *out_3702297798823717219) {
  H_13(state, unused, out_3702297798823717219);
}
void pose_h_14(double *state, double *unused, double *out_4339241047534864282) {
  h_14(state, unused, out_4339241047534864282);
}
void pose_H_14(double *state, double *unused, double *out_2951330767816565491) {
  H_14(state, unused, out_2951330767816565491);
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
