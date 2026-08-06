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
void err_fun(double *nom_x, double *delta_x, double *out_228345055687174559) {
   out_228345055687174559[0] = delta_x[0] + nom_x[0];
   out_228345055687174559[1] = delta_x[1] + nom_x[1];
   out_228345055687174559[2] = delta_x[2] + nom_x[2];
   out_228345055687174559[3] = delta_x[3] + nom_x[3];
   out_228345055687174559[4] = delta_x[4] + nom_x[4];
   out_228345055687174559[5] = delta_x[5] + nom_x[5];
   out_228345055687174559[6] = delta_x[6] + nom_x[6];
   out_228345055687174559[7] = delta_x[7] + nom_x[7];
   out_228345055687174559[8] = delta_x[8] + nom_x[8];
   out_228345055687174559[9] = delta_x[9] + nom_x[9];
   out_228345055687174559[10] = delta_x[10] + nom_x[10];
   out_228345055687174559[11] = delta_x[11] + nom_x[11];
   out_228345055687174559[12] = delta_x[12] + nom_x[12];
   out_228345055687174559[13] = delta_x[13] + nom_x[13];
   out_228345055687174559[14] = delta_x[14] + nom_x[14];
   out_228345055687174559[15] = delta_x[15] + nom_x[15];
   out_228345055687174559[16] = delta_x[16] + nom_x[16];
   out_228345055687174559[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_3726714603593551859) {
   out_3726714603593551859[0] = -nom_x[0] + true_x[0];
   out_3726714603593551859[1] = -nom_x[1] + true_x[1];
   out_3726714603593551859[2] = -nom_x[2] + true_x[2];
   out_3726714603593551859[3] = -nom_x[3] + true_x[3];
   out_3726714603593551859[4] = -nom_x[4] + true_x[4];
   out_3726714603593551859[5] = -nom_x[5] + true_x[5];
   out_3726714603593551859[6] = -nom_x[6] + true_x[6];
   out_3726714603593551859[7] = -nom_x[7] + true_x[7];
   out_3726714603593551859[8] = -nom_x[8] + true_x[8];
   out_3726714603593551859[9] = -nom_x[9] + true_x[9];
   out_3726714603593551859[10] = -nom_x[10] + true_x[10];
   out_3726714603593551859[11] = -nom_x[11] + true_x[11];
   out_3726714603593551859[12] = -nom_x[12] + true_x[12];
   out_3726714603593551859[13] = -nom_x[13] + true_x[13];
   out_3726714603593551859[14] = -nom_x[14] + true_x[14];
   out_3726714603593551859[15] = -nom_x[15] + true_x[15];
   out_3726714603593551859[16] = -nom_x[16] + true_x[16];
   out_3726714603593551859[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_6712772131857650620) {
   out_6712772131857650620[0] = 1.0;
   out_6712772131857650620[1] = 0.0;
   out_6712772131857650620[2] = 0.0;
   out_6712772131857650620[3] = 0.0;
   out_6712772131857650620[4] = 0.0;
   out_6712772131857650620[5] = 0.0;
   out_6712772131857650620[6] = 0.0;
   out_6712772131857650620[7] = 0.0;
   out_6712772131857650620[8] = 0.0;
   out_6712772131857650620[9] = 0.0;
   out_6712772131857650620[10] = 0.0;
   out_6712772131857650620[11] = 0.0;
   out_6712772131857650620[12] = 0.0;
   out_6712772131857650620[13] = 0.0;
   out_6712772131857650620[14] = 0.0;
   out_6712772131857650620[15] = 0.0;
   out_6712772131857650620[16] = 0.0;
   out_6712772131857650620[17] = 0.0;
   out_6712772131857650620[18] = 0.0;
   out_6712772131857650620[19] = 1.0;
   out_6712772131857650620[20] = 0.0;
   out_6712772131857650620[21] = 0.0;
   out_6712772131857650620[22] = 0.0;
   out_6712772131857650620[23] = 0.0;
   out_6712772131857650620[24] = 0.0;
   out_6712772131857650620[25] = 0.0;
   out_6712772131857650620[26] = 0.0;
   out_6712772131857650620[27] = 0.0;
   out_6712772131857650620[28] = 0.0;
   out_6712772131857650620[29] = 0.0;
   out_6712772131857650620[30] = 0.0;
   out_6712772131857650620[31] = 0.0;
   out_6712772131857650620[32] = 0.0;
   out_6712772131857650620[33] = 0.0;
   out_6712772131857650620[34] = 0.0;
   out_6712772131857650620[35] = 0.0;
   out_6712772131857650620[36] = 0.0;
   out_6712772131857650620[37] = 0.0;
   out_6712772131857650620[38] = 1.0;
   out_6712772131857650620[39] = 0.0;
   out_6712772131857650620[40] = 0.0;
   out_6712772131857650620[41] = 0.0;
   out_6712772131857650620[42] = 0.0;
   out_6712772131857650620[43] = 0.0;
   out_6712772131857650620[44] = 0.0;
   out_6712772131857650620[45] = 0.0;
   out_6712772131857650620[46] = 0.0;
   out_6712772131857650620[47] = 0.0;
   out_6712772131857650620[48] = 0.0;
   out_6712772131857650620[49] = 0.0;
   out_6712772131857650620[50] = 0.0;
   out_6712772131857650620[51] = 0.0;
   out_6712772131857650620[52] = 0.0;
   out_6712772131857650620[53] = 0.0;
   out_6712772131857650620[54] = 0.0;
   out_6712772131857650620[55] = 0.0;
   out_6712772131857650620[56] = 0.0;
   out_6712772131857650620[57] = 1.0;
   out_6712772131857650620[58] = 0.0;
   out_6712772131857650620[59] = 0.0;
   out_6712772131857650620[60] = 0.0;
   out_6712772131857650620[61] = 0.0;
   out_6712772131857650620[62] = 0.0;
   out_6712772131857650620[63] = 0.0;
   out_6712772131857650620[64] = 0.0;
   out_6712772131857650620[65] = 0.0;
   out_6712772131857650620[66] = 0.0;
   out_6712772131857650620[67] = 0.0;
   out_6712772131857650620[68] = 0.0;
   out_6712772131857650620[69] = 0.0;
   out_6712772131857650620[70] = 0.0;
   out_6712772131857650620[71] = 0.0;
   out_6712772131857650620[72] = 0.0;
   out_6712772131857650620[73] = 0.0;
   out_6712772131857650620[74] = 0.0;
   out_6712772131857650620[75] = 0.0;
   out_6712772131857650620[76] = 1.0;
   out_6712772131857650620[77] = 0.0;
   out_6712772131857650620[78] = 0.0;
   out_6712772131857650620[79] = 0.0;
   out_6712772131857650620[80] = 0.0;
   out_6712772131857650620[81] = 0.0;
   out_6712772131857650620[82] = 0.0;
   out_6712772131857650620[83] = 0.0;
   out_6712772131857650620[84] = 0.0;
   out_6712772131857650620[85] = 0.0;
   out_6712772131857650620[86] = 0.0;
   out_6712772131857650620[87] = 0.0;
   out_6712772131857650620[88] = 0.0;
   out_6712772131857650620[89] = 0.0;
   out_6712772131857650620[90] = 0.0;
   out_6712772131857650620[91] = 0.0;
   out_6712772131857650620[92] = 0.0;
   out_6712772131857650620[93] = 0.0;
   out_6712772131857650620[94] = 0.0;
   out_6712772131857650620[95] = 1.0;
   out_6712772131857650620[96] = 0.0;
   out_6712772131857650620[97] = 0.0;
   out_6712772131857650620[98] = 0.0;
   out_6712772131857650620[99] = 0.0;
   out_6712772131857650620[100] = 0.0;
   out_6712772131857650620[101] = 0.0;
   out_6712772131857650620[102] = 0.0;
   out_6712772131857650620[103] = 0.0;
   out_6712772131857650620[104] = 0.0;
   out_6712772131857650620[105] = 0.0;
   out_6712772131857650620[106] = 0.0;
   out_6712772131857650620[107] = 0.0;
   out_6712772131857650620[108] = 0.0;
   out_6712772131857650620[109] = 0.0;
   out_6712772131857650620[110] = 0.0;
   out_6712772131857650620[111] = 0.0;
   out_6712772131857650620[112] = 0.0;
   out_6712772131857650620[113] = 0.0;
   out_6712772131857650620[114] = 1.0;
   out_6712772131857650620[115] = 0.0;
   out_6712772131857650620[116] = 0.0;
   out_6712772131857650620[117] = 0.0;
   out_6712772131857650620[118] = 0.0;
   out_6712772131857650620[119] = 0.0;
   out_6712772131857650620[120] = 0.0;
   out_6712772131857650620[121] = 0.0;
   out_6712772131857650620[122] = 0.0;
   out_6712772131857650620[123] = 0.0;
   out_6712772131857650620[124] = 0.0;
   out_6712772131857650620[125] = 0.0;
   out_6712772131857650620[126] = 0.0;
   out_6712772131857650620[127] = 0.0;
   out_6712772131857650620[128] = 0.0;
   out_6712772131857650620[129] = 0.0;
   out_6712772131857650620[130] = 0.0;
   out_6712772131857650620[131] = 0.0;
   out_6712772131857650620[132] = 0.0;
   out_6712772131857650620[133] = 1.0;
   out_6712772131857650620[134] = 0.0;
   out_6712772131857650620[135] = 0.0;
   out_6712772131857650620[136] = 0.0;
   out_6712772131857650620[137] = 0.0;
   out_6712772131857650620[138] = 0.0;
   out_6712772131857650620[139] = 0.0;
   out_6712772131857650620[140] = 0.0;
   out_6712772131857650620[141] = 0.0;
   out_6712772131857650620[142] = 0.0;
   out_6712772131857650620[143] = 0.0;
   out_6712772131857650620[144] = 0.0;
   out_6712772131857650620[145] = 0.0;
   out_6712772131857650620[146] = 0.0;
   out_6712772131857650620[147] = 0.0;
   out_6712772131857650620[148] = 0.0;
   out_6712772131857650620[149] = 0.0;
   out_6712772131857650620[150] = 0.0;
   out_6712772131857650620[151] = 0.0;
   out_6712772131857650620[152] = 1.0;
   out_6712772131857650620[153] = 0.0;
   out_6712772131857650620[154] = 0.0;
   out_6712772131857650620[155] = 0.0;
   out_6712772131857650620[156] = 0.0;
   out_6712772131857650620[157] = 0.0;
   out_6712772131857650620[158] = 0.0;
   out_6712772131857650620[159] = 0.0;
   out_6712772131857650620[160] = 0.0;
   out_6712772131857650620[161] = 0.0;
   out_6712772131857650620[162] = 0.0;
   out_6712772131857650620[163] = 0.0;
   out_6712772131857650620[164] = 0.0;
   out_6712772131857650620[165] = 0.0;
   out_6712772131857650620[166] = 0.0;
   out_6712772131857650620[167] = 0.0;
   out_6712772131857650620[168] = 0.0;
   out_6712772131857650620[169] = 0.0;
   out_6712772131857650620[170] = 0.0;
   out_6712772131857650620[171] = 1.0;
   out_6712772131857650620[172] = 0.0;
   out_6712772131857650620[173] = 0.0;
   out_6712772131857650620[174] = 0.0;
   out_6712772131857650620[175] = 0.0;
   out_6712772131857650620[176] = 0.0;
   out_6712772131857650620[177] = 0.0;
   out_6712772131857650620[178] = 0.0;
   out_6712772131857650620[179] = 0.0;
   out_6712772131857650620[180] = 0.0;
   out_6712772131857650620[181] = 0.0;
   out_6712772131857650620[182] = 0.0;
   out_6712772131857650620[183] = 0.0;
   out_6712772131857650620[184] = 0.0;
   out_6712772131857650620[185] = 0.0;
   out_6712772131857650620[186] = 0.0;
   out_6712772131857650620[187] = 0.0;
   out_6712772131857650620[188] = 0.0;
   out_6712772131857650620[189] = 0.0;
   out_6712772131857650620[190] = 1.0;
   out_6712772131857650620[191] = 0.0;
   out_6712772131857650620[192] = 0.0;
   out_6712772131857650620[193] = 0.0;
   out_6712772131857650620[194] = 0.0;
   out_6712772131857650620[195] = 0.0;
   out_6712772131857650620[196] = 0.0;
   out_6712772131857650620[197] = 0.0;
   out_6712772131857650620[198] = 0.0;
   out_6712772131857650620[199] = 0.0;
   out_6712772131857650620[200] = 0.0;
   out_6712772131857650620[201] = 0.0;
   out_6712772131857650620[202] = 0.0;
   out_6712772131857650620[203] = 0.0;
   out_6712772131857650620[204] = 0.0;
   out_6712772131857650620[205] = 0.0;
   out_6712772131857650620[206] = 0.0;
   out_6712772131857650620[207] = 0.0;
   out_6712772131857650620[208] = 0.0;
   out_6712772131857650620[209] = 1.0;
   out_6712772131857650620[210] = 0.0;
   out_6712772131857650620[211] = 0.0;
   out_6712772131857650620[212] = 0.0;
   out_6712772131857650620[213] = 0.0;
   out_6712772131857650620[214] = 0.0;
   out_6712772131857650620[215] = 0.0;
   out_6712772131857650620[216] = 0.0;
   out_6712772131857650620[217] = 0.0;
   out_6712772131857650620[218] = 0.0;
   out_6712772131857650620[219] = 0.0;
   out_6712772131857650620[220] = 0.0;
   out_6712772131857650620[221] = 0.0;
   out_6712772131857650620[222] = 0.0;
   out_6712772131857650620[223] = 0.0;
   out_6712772131857650620[224] = 0.0;
   out_6712772131857650620[225] = 0.0;
   out_6712772131857650620[226] = 0.0;
   out_6712772131857650620[227] = 0.0;
   out_6712772131857650620[228] = 1.0;
   out_6712772131857650620[229] = 0.0;
   out_6712772131857650620[230] = 0.0;
   out_6712772131857650620[231] = 0.0;
   out_6712772131857650620[232] = 0.0;
   out_6712772131857650620[233] = 0.0;
   out_6712772131857650620[234] = 0.0;
   out_6712772131857650620[235] = 0.0;
   out_6712772131857650620[236] = 0.0;
   out_6712772131857650620[237] = 0.0;
   out_6712772131857650620[238] = 0.0;
   out_6712772131857650620[239] = 0.0;
   out_6712772131857650620[240] = 0.0;
   out_6712772131857650620[241] = 0.0;
   out_6712772131857650620[242] = 0.0;
   out_6712772131857650620[243] = 0.0;
   out_6712772131857650620[244] = 0.0;
   out_6712772131857650620[245] = 0.0;
   out_6712772131857650620[246] = 0.0;
   out_6712772131857650620[247] = 1.0;
   out_6712772131857650620[248] = 0.0;
   out_6712772131857650620[249] = 0.0;
   out_6712772131857650620[250] = 0.0;
   out_6712772131857650620[251] = 0.0;
   out_6712772131857650620[252] = 0.0;
   out_6712772131857650620[253] = 0.0;
   out_6712772131857650620[254] = 0.0;
   out_6712772131857650620[255] = 0.0;
   out_6712772131857650620[256] = 0.0;
   out_6712772131857650620[257] = 0.0;
   out_6712772131857650620[258] = 0.0;
   out_6712772131857650620[259] = 0.0;
   out_6712772131857650620[260] = 0.0;
   out_6712772131857650620[261] = 0.0;
   out_6712772131857650620[262] = 0.0;
   out_6712772131857650620[263] = 0.0;
   out_6712772131857650620[264] = 0.0;
   out_6712772131857650620[265] = 0.0;
   out_6712772131857650620[266] = 1.0;
   out_6712772131857650620[267] = 0.0;
   out_6712772131857650620[268] = 0.0;
   out_6712772131857650620[269] = 0.0;
   out_6712772131857650620[270] = 0.0;
   out_6712772131857650620[271] = 0.0;
   out_6712772131857650620[272] = 0.0;
   out_6712772131857650620[273] = 0.0;
   out_6712772131857650620[274] = 0.0;
   out_6712772131857650620[275] = 0.0;
   out_6712772131857650620[276] = 0.0;
   out_6712772131857650620[277] = 0.0;
   out_6712772131857650620[278] = 0.0;
   out_6712772131857650620[279] = 0.0;
   out_6712772131857650620[280] = 0.0;
   out_6712772131857650620[281] = 0.0;
   out_6712772131857650620[282] = 0.0;
   out_6712772131857650620[283] = 0.0;
   out_6712772131857650620[284] = 0.0;
   out_6712772131857650620[285] = 1.0;
   out_6712772131857650620[286] = 0.0;
   out_6712772131857650620[287] = 0.0;
   out_6712772131857650620[288] = 0.0;
   out_6712772131857650620[289] = 0.0;
   out_6712772131857650620[290] = 0.0;
   out_6712772131857650620[291] = 0.0;
   out_6712772131857650620[292] = 0.0;
   out_6712772131857650620[293] = 0.0;
   out_6712772131857650620[294] = 0.0;
   out_6712772131857650620[295] = 0.0;
   out_6712772131857650620[296] = 0.0;
   out_6712772131857650620[297] = 0.0;
   out_6712772131857650620[298] = 0.0;
   out_6712772131857650620[299] = 0.0;
   out_6712772131857650620[300] = 0.0;
   out_6712772131857650620[301] = 0.0;
   out_6712772131857650620[302] = 0.0;
   out_6712772131857650620[303] = 0.0;
   out_6712772131857650620[304] = 1.0;
   out_6712772131857650620[305] = 0.0;
   out_6712772131857650620[306] = 0.0;
   out_6712772131857650620[307] = 0.0;
   out_6712772131857650620[308] = 0.0;
   out_6712772131857650620[309] = 0.0;
   out_6712772131857650620[310] = 0.0;
   out_6712772131857650620[311] = 0.0;
   out_6712772131857650620[312] = 0.0;
   out_6712772131857650620[313] = 0.0;
   out_6712772131857650620[314] = 0.0;
   out_6712772131857650620[315] = 0.0;
   out_6712772131857650620[316] = 0.0;
   out_6712772131857650620[317] = 0.0;
   out_6712772131857650620[318] = 0.0;
   out_6712772131857650620[319] = 0.0;
   out_6712772131857650620[320] = 0.0;
   out_6712772131857650620[321] = 0.0;
   out_6712772131857650620[322] = 0.0;
   out_6712772131857650620[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_2706993655191654809) {
   out_2706993655191654809[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_2706993655191654809[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_2706993655191654809[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_2706993655191654809[3] = dt*state[12] + state[3];
   out_2706993655191654809[4] = dt*state[13] + state[4];
   out_2706993655191654809[5] = dt*state[14] + state[5];
   out_2706993655191654809[6] = state[6];
   out_2706993655191654809[7] = state[7];
   out_2706993655191654809[8] = state[8];
   out_2706993655191654809[9] = state[9];
   out_2706993655191654809[10] = state[10];
   out_2706993655191654809[11] = state[11];
   out_2706993655191654809[12] = state[12];
   out_2706993655191654809[13] = state[13];
   out_2706993655191654809[14] = state[14];
   out_2706993655191654809[15] = state[15];
   out_2706993655191654809[16] = state[16];
   out_2706993655191654809[17] = state[17];
}
void F_fun(double *state, double dt, double *out_372841931129064371) {
   out_372841931129064371[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_372841931129064371[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_372841931129064371[2] = 0;
   out_372841931129064371[3] = 0;
   out_372841931129064371[4] = 0;
   out_372841931129064371[5] = 0;
   out_372841931129064371[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_372841931129064371[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_372841931129064371[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_372841931129064371[9] = 0;
   out_372841931129064371[10] = 0;
   out_372841931129064371[11] = 0;
   out_372841931129064371[12] = 0;
   out_372841931129064371[13] = 0;
   out_372841931129064371[14] = 0;
   out_372841931129064371[15] = 0;
   out_372841931129064371[16] = 0;
   out_372841931129064371[17] = 0;
   out_372841931129064371[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_372841931129064371[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_372841931129064371[20] = 0;
   out_372841931129064371[21] = 0;
   out_372841931129064371[22] = 0;
   out_372841931129064371[23] = 0;
   out_372841931129064371[24] = 0;
   out_372841931129064371[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_372841931129064371[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_372841931129064371[27] = 0;
   out_372841931129064371[28] = 0;
   out_372841931129064371[29] = 0;
   out_372841931129064371[30] = 0;
   out_372841931129064371[31] = 0;
   out_372841931129064371[32] = 0;
   out_372841931129064371[33] = 0;
   out_372841931129064371[34] = 0;
   out_372841931129064371[35] = 0;
   out_372841931129064371[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_372841931129064371[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_372841931129064371[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_372841931129064371[39] = 0;
   out_372841931129064371[40] = 0;
   out_372841931129064371[41] = 0;
   out_372841931129064371[42] = 0;
   out_372841931129064371[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_372841931129064371[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_372841931129064371[45] = 0;
   out_372841931129064371[46] = 0;
   out_372841931129064371[47] = 0;
   out_372841931129064371[48] = 0;
   out_372841931129064371[49] = 0;
   out_372841931129064371[50] = 0;
   out_372841931129064371[51] = 0;
   out_372841931129064371[52] = 0;
   out_372841931129064371[53] = 0;
   out_372841931129064371[54] = 0;
   out_372841931129064371[55] = 0;
   out_372841931129064371[56] = 0;
   out_372841931129064371[57] = 1;
   out_372841931129064371[58] = 0;
   out_372841931129064371[59] = 0;
   out_372841931129064371[60] = 0;
   out_372841931129064371[61] = 0;
   out_372841931129064371[62] = 0;
   out_372841931129064371[63] = 0;
   out_372841931129064371[64] = 0;
   out_372841931129064371[65] = 0;
   out_372841931129064371[66] = dt;
   out_372841931129064371[67] = 0;
   out_372841931129064371[68] = 0;
   out_372841931129064371[69] = 0;
   out_372841931129064371[70] = 0;
   out_372841931129064371[71] = 0;
   out_372841931129064371[72] = 0;
   out_372841931129064371[73] = 0;
   out_372841931129064371[74] = 0;
   out_372841931129064371[75] = 0;
   out_372841931129064371[76] = 1;
   out_372841931129064371[77] = 0;
   out_372841931129064371[78] = 0;
   out_372841931129064371[79] = 0;
   out_372841931129064371[80] = 0;
   out_372841931129064371[81] = 0;
   out_372841931129064371[82] = 0;
   out_372841931129064371[83] = 0;
   out_372841931129064371[84] = 0;
   out_372841931129064371[85] = dt;
   out_372841931129064371[86] = 0;
   out_372841931129064371[87] = 0;
   out_372841931129064371[88] = 0;
   out_372841931129064371[89] = 0;
   out_372841931129064371[90] = 0;
   out_372841931129064371[91] = 0;
   out_372841931129064371[92] = 0;
   out_372841931129064371[93] = 0;
   out_372841931129064371[94] = 0;
   out_372841931129064371[95] = 1;
   out_372841931129064371[96] = 0;
   out_372841931129064371[97] = 0;
   out_372841931129064371[98] = 0;
   out_372841931129064371[99] = 0;
   out_372841931129064371[100] = 0;
   out_372841931129064371[101] = 0;
   out_372841931129064371[102] = 0;
   out_372841931129064371[103] = 0;
   out_372841931129064371[104] = dt;
   out_372841931129064371[105] = 0;
   out_372841931129064371[106] = 0;
   out_372841931129064371[107] = 0;
   out_372841931129064371[108] = 0;
   out_372841931129064371[109] = 0;
   out_372841931129064371[110] = 0;
   out_372841931129064371[111] = 0;
   out_372841931129064371[112] = 0;
   out_372841931129064371[113] = 0;
   out_372841931129064371[114] = 1;
   out_372841931129064371[115] = 0;
   out_372841931129064371[116] = 0;
   out_372841931129064371[117] = 0;
   out_372841931129064371[118] = 0;
   out_372841931129064371[119] = 0;
   out_372841931129064371[120] = 0;
   out_372841931129064371[121] = 0;
   out_372841931129064371[122] = 0;
   out_372841931129064371[123] = 0;
   out_372841931129064371[124] = 0;
   out_372841931129064371[125] = 0;
   out_372841931129064371[126] = 0;
   out_372841931129064371[127] = 0;
   out_372841931129064371[128] = 0;
   out_372841931129064371[129] = 0;
   out_372841931129064371[130] = 0;
   out_372841931129064371[131] = 0;
   out_372841931129064371[132] = 0;
   out_372841931129064371[133] = 1;
   out_372841931129064371[134] = 0;
   out_372841931129064371[135] = 0;
   out_372841931129064371[136] = 0;
   out_372841931129064371[137] = 0;
   out_372841931129064371[138] = 0;
   out_372841931129064371[139] = 0;
   out_372841931129064371[140] = 0;
   out_372841931129064371[141] = 0;
   out_372841931129064371[142] = 0;
   out_372841931129064371[143] = 0;
   out_372841931129064371[144] = 0;
   out_372841931129064371[145] = 0;
   out_372841931129064371[146] = 0;
   out_372841931129064371[147] = 0;
   out_372841931129064371[148] = 0;
   out_372841931129064371[149] = 0;
   out_372841931129064371[150] = 0;
   out_372841931129064371[151] = 0;
   out_372841931129064371[152] = 1;
   out_372841931129064371[153] = 0;
   out_372841931129064371[154] = 0;
   out_372841931129064371[155] = 0;
   out_372841931129064371[156] = 0;
   out_372841931129064371[157] = 0;
   out_372841931129064371[158] = 0;
   out_372841931129064371[159] = 0;
   out_372841931129064371[160] = 0;
   out_372841931129064371[161] = 0;
   out_372841931129064371[162] = 0;
   out_372841931129064371[163] = 0;
   out_372841931129064371[164] = 0;
   out_372841931129064371[165] = 0;
   out_372841931129064371[166] = 0;
   out_372841931129064371[167] = 0;
   out_372841931129064371[168] = 0;
   out_372841931129064371[169] = 0;
   out_372841931129064371[170] = 0;
   out_372841931129064371[171] = 1;
   out_372841931129064371[172] = 0;
   out_372841931129064371[173] = 0;
   out_372841931129064371[174] = 0;
   out_372841931129064371[175] = 0;
   out_372841931129064371[176] = 0;
   out_372841931129064371[177] = 0;
   out_372841931129064371[178] = 0;
   out_372841931129064371[179] = 0;
   out_372841931129064371[180] = 0;
   out_372841931129064371[181] = 0;
   out_372841931129064371[182] = 0;
   out_372841931129064371[183] = 0;
   out_372841931129064371[184] = 0;
   out_372841931129064371[185] = 0;
   out_372841931129064371[186] = 0;
   out_372841931129064371[187] = 0;
   out_372841931129064371[188] = 0;
   out_372841931129064371[189] = 0;
   out_372841931129064371[190] = 1;
   out_372841931129064371[191] = 0;
   out_372841931129064371[192] = 0;
   out_372841931129064371[193] = 0;
   out_372841931129064371[194] = 0;
   out_372841931129064371[195] = 0;
   out_372841931129064371[196] = 0;
   out_372841931129064371[197] = 0;
   out_372841931129064371[198] = 0;
   out_372841931129064371[199] = 0;
   out_372841931129064371[200] = 0;
   out_372841931129064371[201] = 0;
   out_372841931129064371[202] = 0;
   out_372841931129064371[203] = 0;
   out_372841931129064371[204] = 0;
   out_372841931129064371[205] = 0;
   out_372841931129064371[206] = 0;
   out_372841931129064371[207] = 0;
   out_372841931129064371[208] = 0;
   out_372841931129064371[209] = 1;
   out_372841931129064371[210] = 0;
   out_372841931129064371[211] = 0;
   out_372841931129064371[212] = 0;
   out_372841931129064371[213] = 0;
   out_372841931129064371[214] = 0;
   out_372841931129064371[215] = 0;
   out_372841931129064371[216] = 0;
   out_372841931129064371[217] = 0;
   out_372841931129064371[218] = 0;
   out_372841931129064371[219] = 0;
   out_372841931129064371[220] = 0;
   out_372841931129064371[221] = 0;
   out_372841931129064371[222] = 0;
   out_372841931129064371[223] = 0;
   out_372841931129064371[224] = 0;
   out_372841931129064371[225] = 0;
   out_372841931129064371[226] = 0;
   out_372841931129064371[227] = 0;
   out_372841931129064371[228] = 1;
   out_372841931129064371[229] = 0;
   out_372841931129064371[230] = 0;
   out_372841931129064371[231] = 0;
   out_372841931129064371[232] = 0;
   out_372841931129064371[233] = 0;
   out_372841931129064371[234] = 0;
   out_372841931129064371[235] = 0;
   out_372841931129064371[236] = 0;
   out_372841931129064371[237] = 0;
   out_372841931129064371[238] = 0;
   out_372841931129064371[239] = 0;
   out_372841931129064371[240] = 0;
   out_372841931129064371[241] = 0;
   out_372841931129064371[242] = 0;
   out_372841931129064371[243] = 0;
   out_372841931129064371[244] = 0;
   out_372841931129064371[245] = 0;
   out_372841931129064371[246] = 0;
   out_372841931129064371[247] = 1;
   out_372841931129064371[248] = 0;
   out_372841931129064371[249] = 0;
   out_372841931129064371[250] = 0;
   out_372841931129064371[251] = 0;
   out_372841931129064371[252] = 0;
   out_372841931129064371[253] = 0;
   out_372841931129064371[254] = 0;
   out_372841931129064371[255] = 0;
   out_372841931129064371[256] = 0;
   out_372841931129064371[257] = 0;
   out_372841931129064371[258] = 0;
   out_372841931129064371[259] = 0;
   out_372841931129064371[260] = 0;
   out_372841931129064371[261] = 0;
   out_372841931129064371[262] = 0;
   out_372841931129064371[263] = 0;
   out_372841931129064371[264] = 0;
   out_372841931129064371[265] = 0;
   out_372841931129064371[266] = 1;
   out_372841931129064371[267] = 0;
   out_372841931129064371[268] = 0;
   out_372841931129064371[269] = 0;
   out_372841931129064371[270] = 0;
   out_372841931129064371[271] = 0;
   out_372841931129064371[272] = 0;
   out_372841931129064371[273] = 0;
   out_372841931129064371[274] = 0;
   out_372841931129064371[275] = 0;
   out_372841931129064371[276] = 0;
   out_372841931129064371[277] = 0;
   out_372841931129064371[278] = 0;
   out_372841931129064371[279] = 0;
   out_372841931129064371[280] = 0;
   out_372841931129064371[281] = 0;
   out_372841931129064371[282] = 0;
   out_372841931129064371[283] = 0;
   out_372841931129064371[284] = 0;
   out_372841931129064371[285] = 1;
   out_372841931129064371[286] = 0;
   out_372841931129064371[287] = 0;
   out_372841931129064371[288] = 0;
   out_372841931129064371[289] = 0;
   out_372841931129064371[290] = 0;
   out_372841931129064371[291] = 0;
   out_372841931129064371[292] = 0;
   out_372841931129064371[293] = 0;
   out_372841931129064371[294] = 0;
   out_372841931129064371[295] = 0;
   out_372841931129064371[296] = 0;
   out_372841931129064371[297] = 0;
   out_372841931129064371[298] = 0;
   out_372841931129064371[299] = 0;
   out_372841931129064371[300] = 0;
   out_372841931129064371[301] = 0;
   out_372841931129064371[302] = 0;
   out_372841931129064371[303] = 0;
   out_372841931129064371[304] = 1;
   out_372841931129064371[305] = 0;
   out_372841931129064371[306] = 0;
   out_372841931129064371[307] = 0;
   out_372841931129064371[308] = 0;
   out_372841931129064371[309] = 0;
   out_372841931129064371[310] = 0;
   out_372841931129064371[311] = 0;
   out_372841931129064371[312] = 0;
   out_372841931129064371[313] = 0;
   out_372841931129064371[314] = 0;
   out_372841931129064371[315] = 0;
   out_372841931129064371[316] = 0;
   out_372841931129064371[317] = 0;
   out_372841931129064371[318] = 0;
   out_372841931129064371[319] = 0;
   out_372841931129064371[320] = 0;
   out_372841931129064371[321] = 0;
   out_372841931129064371[322] = 0;
   out_372841931129064371[323] = 1;
}
void h_4(double *state, double *unused, double *out_3997723666308670841) {
   out_3997723666308670841[0] = state[6] + state[9];
   out_3997723666308670841[1] = state[7] + state[10];
   out_3997723666308670841[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_4134113474779579353) {
   out_4134113474779579353[0] = 0;
   out_4134113474779579353[1] = 0;
   out_4134113474779579353[2] = 0;
   out_4134113474779579353[3] = 0;
   out_4134113474779579353[4] = 0;
   out_4134113474779579353[5] = 0;
   out_4134113474779579353[6] = 1;
   out_4134113474779579353[7] = 0;
   out_4134113474779579353[8] = 0;
   out_4134113474779579353[9] = 1;
   out_4134113474779579353[10] = 0;
   out_4134113474779579353[11] = 0;
   out_4134113474779579353[12] = 0;
   out_4134113474779579353[13] = 0;
   out_4134113474779579353[14] = 0;
   out_4134113474779579353[15] = 0;
   out_4134113474779579353[16] = 0;
   out_4134113474779579353[17] = 0;
   out_4134113474779579353[18] = 0;
   out_4134113474779579353[19] = 0;
   out_4134113474779579353[20] = 0;
   out_4134113474779579353[21] = 0;
   out_4134113474779579353[22] = 0;
   out_4134113474779579353[23] = 0;
   out_4134113474779579353[24] = 0;
   out_4134113474779579353[25] = 1;
   out_4134113474779579353[26] = 0;
   out_4134113474779579353[27] = 0;
   out_4134113474779579353[28] = 1;
   out_4134113474779579353[29] = 0;
   out_4134113474779579353[30] = 0;
   out_4134113474779579353[31] = 0;
   out_4134113474779579353[32] = 0;
   out_4134113474779579353[33] = 0;
   out_4134113474779579353[34] = 0;
   out_4134113474779579353[35] = 0;
   out_4134113474779579353[36] = 0;
   out_4134113474779579353[37] = 0;
   out_4134113474779579353[38] = 0;
   out_4134113474779579353[39] = 0;
   out_4134113474779579353[40] = 0;
   out_4134113474779579353[41] = 0;
   out_4134113474779579353[42] = 0;
   out_4134113474779579353[43] = 0;
   out_4134113474779579353[44] = 1;
   out_4134113474779579353[45] = 0;
   out_4134113474779579353[46] = 0;
   out_4134113474779579353[47] = 1;
   out_4134113474779579353[48] = 0;
   out_4134113474779579353[49] = 0;
   out_4134113474779579353[50] = 0;
   out_4134113474779579353[51] = 0;
   out_4134113474779579353[52] = 0;
   out_4134113474779579353[53] = 0;
}
void h_10(double *state, double *unused, double *out_6627456117207891484) {
   out_6627456117207891484[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_6627456117207891484[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_6627456117207891484[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_1462818273599549569) {
   out_1462818273599549569[0] = 0;
   out_1462818273599549569[1] = 9.8100000000000005*cos(state[1]);
   out_1462818273599549569[2] = 0;
   out_1462818273599549569[3] = 0;
   out_1462818273599549569[4] = -state[8];
   out_1462818273599549569[5] = state[7];
   out_1462818273599549569[6] = 0;
   out_1462818273599549569[7] = state[5];
   out_1462818273599549569[8] = -state[4];
   out_1462818273599549569[9] = 0;
   out_1462818273599549569[10] = 0;
   out_1462818273599549569[11] = 0;
   out_1462818273599549569[12] = 1;
   out_1462818273599549569[13] = 0;
   out_1462818273599549569[14] = 0;
   out_1462818273599549569[15] = 1;
   out_1462818273599549569[16] = 0;
   out_1462818273599549569[17] = 0;
   out_1462818273599549569[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_1462818273599549569[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_1462818273599549569[20] = 0;
   out_1462818273599549569[21] = state[8];
   out_1462818273599549569[22] = 0;
   out_1462818273599549569[23] = -state[6];
   out_1462818273599549569[24] = -state[5];
   out_1462818273599549569[25] = 0;
   out_1462818273599549569[26] = state[3];
   out_1462818273599549569[27] = 0;
   out_1462818273599549569[28] = 0;
   out_1462818273599549569[29] = 0;
   out_1462818273599549569[30] = 0;
   out_1462818273599549569[31] = 1;
   out_1462818273599549569[32] = 0;
   out_1462818273599549569[33] = 0;
   out_1462818273599549569[34] = 1;
   out_1462818273599549569[35] = 0;
   out_1462818273599549569[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_1462818273599549569[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_1462818273599549569[38] = 0;
   out_1462818273599549569[39] = -state[7];
   out_1462818273599549569[40] = state[6];
   out_1462818273599549569[41] = 0;
   out_1462818273599549569[42] = state[4];
   out_1462818273599549569[43] = -state[3];
   out_1462818273599549569[44] = 0;
   out_1462818273599549569[45] = 0;
   out_1462818273599549569[46] = 0;
   out_1462818273599549569[47] = 0;
   out_1462818273599549569[48] = 0;
   out_1462818273599549569[49] = 0;
   out_1462818273599549569[50] = 1;
   out_1462818273599549569[51] = 0;
   out_1462818273599549569[52] = 0;
   out_1462818273599549569[53] = 1;
}
void h_13(double *state, double *unused, double *out_2824244578095522440) {
   out_2824244578095522440[0] = state[3];
   out_2824244578095522440[1] = state[4];
   out_2824244578095522440[2] = state[5];
}
void H_13(double *state, double *unused, double *out_921839649447246552) {
   out_921839649447246552[0] = 0;
   out_921839649447246552[1] = 0;
   out_921839649447246552[2] = 0;
   out_921839649447246552[3] = 1;
   out_921839649447246552[4] = 0;
   out_921839649447246552[5] = 0;
   out_921839649447246552[6] = 0;
   out_921839649447246552[7] = 0;
   out_921839649447246552[8] = 0;
   out_921839649447246552[9] = 0;
   out_921839649447246552[10] = 0;
   out_921839649447246552[11] = 0;
   out_921839649447246552[12] = 0;
   out_921839649447246552[13] = 0;
   out_921839649447246552[14] = 0;
   out_921839649447246552[15] = 0;
   out_921839649447246552[16] = 0;
   out_921839649447246552[17] = 0;
   out_921839649447246552[18] = 0;
   out_921839649447246552[19] = 0;
   out_921839649447246552[20] = 0;
   out_921839649447246552[21] = 0;
   out_921839649447246552[22] = 1;
   out_921839649447246552[23] = 0;
   out_921839649447246552[24] = 0;
   out_921839649447246552[25] = 0;
   out_921839649447246552[26] = 0;
   out_921839649447246552[27] = 0;
   out_921839649447246552[28] = 0;
   out_921839649447246552[29] = 0;
   out_921839649447246552[30] = 0;
   out_921839649447246552[31] = 0;
   out_921839649447246552[32] = 0;
   out_921839649447246552[33] = 0;
   out_921839649447246552[34] = 0;
   out_921839649447246552[35] = 0;
   out_921839649447246552[36] = 0;
   out_921839649447246552[37] = 0;
   out_921839649447246552[38] = 0;
   out_921839649447246552[39] = 0;
   out_921839649447246552[40] = 0;
   out_921839649447246552[41] = 1;
   out_921839649447246552[42] = 0;
   out_921839649447246552[43] = 0;
   out_921839649447246552[44] = 0;
   out_921839649447246552[45] = 0;
   out_921839649447246552[46] = 0;
   out_921839649447246552[47] = 0;
   out_921839649447246552[48] = 0;
   out_921839649447246552[49] = 0;
   out_921839649447246552[50] = 0;
   out_921839649447246552[51] = 0;
   out_921839649447246552[52] = 0;
   out_921839649447246552[53] = 0;
}
void h_14(double *state, double *unused, double *out_696698419016090920) {
   out_696698419016090920[0] = state[6];
   out_696698419016090920[1] = state[7];
   out_696698419016090920[2] = state[8];
}
void H_14(double *state, double *unused, double *out_7216901907074951649) {
   out_7216901907074951649[0] = 0;
   out_7216901907074951649[1] = 0;
   out_7216901907074951649[2] = 0;
   out_7216901907074951649[3] = 0;
   out_7216901907074951649[4] = 0;
   out_7216901907074951649[5] = 0;
   out_7216901907074951649[6] = 1;
   out_7216901907074951649[7] = 0;
   out_7216901907074951649[8] = 0;
   out_7216901907074951649[9] = 0;
   out_7216901907074951649[10] = 0;
   out_7216901907074951649[11] = 0;
   out_7216901907074951649[12] = 0;
   out_7216901907074951649[13] = 0;
   out_7216901907074951649[14] = 0;
   out_7216901907074951649[15] = 0;
   out_7216901907074951649[16] = 0;
   out_7216901907074951649[17] = 0;
   out_7216901907074951649[18] = 0;
   out_7216901907074951649[19] = 0;
   out_7216901907074951649[20] = 0;
   out_7216901907074951649[21] = 0;
   out_7216901907074951649[22] = 0;
   out_7216901907074951649[23] = 0;
   out_7216901907074951649[24] = 0;
   out_7216901907074951649[25] = 1;
   out_7216901907074951649[26] = 0;
   out_7216901907074951649[27] = 0;
   out_7216901907074951649[28] = 0;
   out_7216901907074951649[29] = 0;
   out_7216901907074951649[30] = 0;
   out_7216901907074951649[31] = 0;
   out_7216901907074951649[32] = 0;
   out_7216901907074951649[33] = 0;
   out_7216901907074951649[34] = 0;
   out_7216901907074951649[35] = 0;
   out_7216901907074951649[36] = 0;
   out_7216901907074951649[37] = 0;
   out_7216901907074951649[38] = 0;
   out_7216901907074951649[39] = 0;
   out_7216901907074951649[40] = 0;
   out_7216901907074951649[41] = 0;
   out_7216901907074951649[42] = 0;
   out_7216901907074951649[43] = 0;
   out_7216901907074951649[44] = 1;
   out_7216901907074951649[45] = 0;
   out_7216901907074951649[46] = 0;
   out_7216901907074951649[47] = 0;
   out_7216901907074951649[48] = 0;
   out_7216901907074951649[49] = 0;
   out_7216901907074951649[50] = 0;
   out_7216901907074951649[51] = 0;
   out_7216901907074951649[52] = 0;
   out_7216901907074951649[53] = 0;
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
void pose_err_fun(double *nom_x, double *delta_x, double *out_228345055687174559) {
  err_fun(nom_x, delta_x, out_228345055687174559);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_3726714603593551859) {
  inv_err_fun(nom_x, true_x, out_3726714603593551859);
}
void pose_H_mod_fun(double *state, double *out_6712772131857650620) {
  H_mod_fun(state, out_6712772131857650620);
}
void pose_f_fun(double *state, double dt, double *out_2706993655191654809) {
  f_fun(state,  dt, out_2706993655191654809);
}
void pose_F_fun(double *state, double dt, double *out_372841931129064371) {
  F_fun(state,  dt, out_372841931129064371);
}
void pose_h_4(double *state, double *unused, double *out_3997723666308670841) {
  h_4(state, unused, out_3997723666308670841);
}
void pose_H_4(double *state, double *unused, double *out_4134113474779579353) {
  H_4(state, unused, out_4134113474779579353);
}
void pose_h_10(double *state, double *unused, double *out_6627456117207891484) {
  h_10(state, unused, out_6627456117207891484);
}
void pose_H_10(double *state, double *unused, double *out_1462818273599549569) {
  H_10(state, unused, out_1462818273599549569);
}
void pose_h_13(double *state, double *unused, double *out_2824244578095522440) {
  h_13(state, unused, out_2824244578095522440);
}
void pose_H_13(double *state, double *unused, double *out_921839649447246552) {
  H_13(state, unused, out_921839649447246552);
}
void pose_h_14(double *state, double *unused, double *out_696698419016090920) {
  h_14(state, unused, out_696698419016090920);
}
void pose_H_14(double *state, double *unused, double *out_7216901907074951649) {
  H_14(state, unused, out_7216901907074951649);
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
