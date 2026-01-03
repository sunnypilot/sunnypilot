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
void err_fun(double *nom_x, double *delta_x, double *out_2078931456649821549) {
   out_2078931456649821549[0] = delta_x[0] + nom_x[0];
   out_2078931456649821549[1] = delta_x[1] + nom_x[1];
   out_2078931456649821549[2] = delta_x[2] + nom_x[2];
   out_2078931456649821549[3] = delta_x[3] + nom_x[3];
   out_2078931456649821549[4] = delta_x[4] + nom_x[4];
   out_2078931456649821549[5] = delta_x[5] + nom_x[5];
   out_2078931456649821549[6] = delta_x[6] + nom_x[6];
   out_2078931456649821549[7] = delta_x[7] + nom_x[7];
   out_2078931456649821549[8] = delta_x[8] + nom_x[8];
   out_2078931456649821549[9] = delta_x[9] + nom_x[9];
   out_2078931456649821549[10] = delta_x[10] + nom_x[10];
   out_2078931456649821549[11] = delta_x[11] + nom_x[11];
   out_2078931456649821549[12] = delta_x[12] + nom_x[12];
   out_2078931456649821549[13] = delta_x[13] + nom_x[13];
   out_2078931456649821549[14] = delta_x[14] + nom_x[14];
   out_2078931456649821549[15] = delta_x[15] + nom_x[15];
   out_2078931456649821549[16] = delta_x[16] + nom_x[16];
   out_2078931456649821549[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_4018826878271793945) {
   out_4018826878271793945[0] = -nom_x[0] + true_x[0];
   out_4018826878271793945[1] = -nom_x[1] + true_x[1];
   out_4018826878271793945[2] = -nom_x[2] + true_x[2];
   out_4018826878271793945[3] = -nom_x[3] + true_x[3];
   out_4018826878271793945[4] = -nom_x[4] + true_x[4];
   out_4018826878271793945[5] = -nom_x[5] + true_x[5];
   out_4018826878271793945[6] = -nom_x[6] + true_x[6];
   out_4018826878271793945[7] = -nom_x[7] + true_x[7];
   out_4018826878271793945[8] = -nom_x[8] + true_x[8];
   out_4018826878271793945[9] = -nom_x[9] + true_x[9];
   out_4018826878271793945[10] = -nom_x[10] + true_x[10];
   out_4018826878271793945[11] = -nom_x[11] + true_x[11];
   out_4018826878271793945[12] = -nom_x[12] + true_x[12];
   out_4018826878271793945[13] = -nom_x[13] + true_x[13];
   out_4018826878271793945[14] = -nom_x[14] + true_x[14];
   out_4018826878271793945[15] = -nom_x[15] + true_x[15];
   out_4018826878271793945[16] = -nom_x[16] + true_x[16];
   out_4018826878271793945[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_1512654483837860004) {
   out_1512654483837860004[0] = 1.0;
   out_1512654483837860004[1] = 0.0;
   out_1512654483837860004[2] = 0.0;
   out_1512654483837860004[3] = 0.0;
   out_1512654483837860004[4] = 0.0;
   out_1512654483837860004[5] = 0.0;
   out_1512654483837860004[6] = 0.0;
   out_1512654483837860004[7] = 0.0;
   out_1512654483837860004[8] = 0.0;
   out_1512654483837860004[9] = 0.0;
   out_1512654483837860004[10] = 0.0;
   out_1512654483837860004[11] = 0.0;
   out_1512654483837860004[12] = 0.0;
   out_1512654483837860004[13] = 0.0;
   out_1512654483837860004[14] = 0.0;
   out_1512654483837860004[15] = 0.0;
   out_1512654483837860004[16] = 0.0;
   out_1512654483837860004[17] = 0.0;
   out_1512654483837860004[18] = 0.0;
   out_1512654483837860004[19] = 1.0;
   out_1512654483837860004[20] = 0.0;
   out_1512654483837860004[21] = 0.0;
   out_1512654483837860004[22] = 0.0;
   out_1512654483837860004[23] = 0.0;
   out_1512654483837860004[24] = 0.0;
   out_1512654483837860004[25] = 0.0;
   out_1512654483837860004[26] = 0.0;
   out_1512654483837860004[27] = 0.0;
   out_1512654483837860004[28] = 0.0;
   out_1512654483837860004[29] = 0.0;
   out_1512654483837860004[30] = 0.0;
   out_1512654483837860004[31] = 0.0;
   out_1512654483837860004[32] = 0.0;
   out_1512654483837860004[33] = 0.0;
   out_1512654483837860004[34] = 0.0;
   out_1512654483837860004[35] = 0.0;
   out_1512654483837860004[36] = 0.0;
   out_1512654483837860004[37] = 0.0;
   out_1512654483837860004[38] = 1.0;
   out_1512654483837860004[39] = 0.0;
   out_1512654483837860004[40] = 0.0;
   out_1512654483837860004[41] = 0.0;
   out_1512654483837860004[42] = 0.0;
   out_1512654483837860004[43] = 0.0;
   out_1512654483837860004[44] = 0.0;
   out_1512654483837860004[45] = 0.0;
   out_1512654483837860004[46] = 0.0;
   out_1512654483837860004[47] = 0.0;
   out_1512654483837860004[48] = 0.0;
   out_1512654483837860004[49] = 0.0;
   out_1512654483837860004[50] = 0.0;
   out_1512654483837860004[51] = 0.0;
   out_1512654483837860004[52] = 0.0;
   out_1512654483837860004[53] = 0.0;
   out_1512654483837860004[54] = 0.0;
   out_1512654483837860004[55] = 0.0;
   out_1512654483837860004[56] = 0.0;
   out_1512654483837860004[57] = 1.0;
   out_1512654483837860004[58] = 0.0;
   out_1512654483837860004[59] = 0.0;
   out_1512654483837860004[60] = 0.0;
   out_1512654483837860004[61] = 0.0;
   out_1512654483837860004[62] = 0.0;
   out_1512654483837860004[63] = 0.0;
   out_1512654483837860004[64] = 0.0;
   out_1512654483837860004[65] = 0.0;
   out_1512654483837860004[66] = 0.0;
   out_1512654483837860004[67] = 0.0;
   out_1512654483837860004[68] = 0.0;
   out_1512654483837860004[69] = 0.0;
   out_1512654483837860004[70] = 0.0;
   out_1512654483837860004[71] = 0.0;
   out_1512654483837860004[72] = 0.0;
   out_1512654483837860004[73] = 0.0;
   out_1512654483837860004[74] = 0.0;
   out_1512654483837860004[75] = 0.0;
   out_1512654483837860004[76] = 1.0;
   out_1512654483837860004[77] = 0.0;
   out_1512654483837860004[78] = 0.0;
   out_1512654483837860004[79] = 0.0;
   out_1512654483837860004[80] = 0.0;
   out_1512654483837860004[81] = 0.0;
   out_1512654483837860004[82] = 0.0;
   out_1512654483837860004[83] = 0.0;
   out_1512654483837860004[84] = 0.0;
   out_1512654483837860004[85] = 0.0;
   out_1512654483837860004[86] = 0.0;
   out_1512654483837860004[87] = 0.0;
   out_1512654483837860004[88] = 0.0;
   out_1512654483837860004[89] = 0.0;
   out_1512654483837860004[90] = 0.0;
   out_1512654483837860004[91] = 0.0;
   out_1512654483837860004[92] = 0.0;
   out_1512654483837860004[93] = 0.0;
   out_1512654483837860004[94] = 0.0;
   out_1512654483837860004[95] = 1.0;
   out_1512654483837860004[96] = 0.0;
   out_1512654483837860004[97] = 0.0;
   out_1512654483837860004[98] = 0.0;
   out_1512654483837860004[99] = 0.0;
   out_1512654483837860004[100] = 0.0;
   out_1512654483837860004[101] = 0.0;
   out_1512654483837860004[102] = 0.0;
   out_1512654483837860004[103] = 0.0;
   out_1512654483837860004[104] = 0.0;
   out_1512654483837860004[105] = 0.0;
   out_1512654483837860004[106] = 0.0;
   out_1512654483837860004[107] = 0.0;
   out_1512654483837860004[108] = 0.0;
   out_1512654483837860004[109] = 0.0;
   out_1512654483837860004[110] = 0.0;
   out_1512654483837860004[111] = 0.0;
   out_1512654483837860004[112] = 0.0;
   out_1512654483837860004[113] = 0.0;
   out_1512654483837860004[114] = 1.0;
   out_1512654483837860004[115] = 0.0;
   out_1512654483837860004[116] = 0.0;
   out_1512654483837860004[117] = 0.0;
   out_1512654483837860004[118] = 0.0;
   out_1512654483837860004[119] = 0.0;
   out_1512654483837860004[120] = 0.0;
   out_1512654483837860004[121] = 0.0;
   out_1512654483837860004[122] = 0.0;
   out_1512654483837860004[123] = 0.0;
   out_1512654483837860004[124] = 0.0;
   out_1512654483837860004[125] = 0.0;
   out_1512654483837860004[126] = 0.0;
   out_1512654483837860004[127] = 0.0;
   out_1512654483837860004[128] = 0.0;
   out_1512654483837860004[129] = 0.0;
   out_1512654483837860004[130] = 0.0;
   out_1512654483837860004[131] = 0.0;
   out_1512654483837860004[132] = 0.0;
   out_1512654483837860004[133] = 1.0;
   out_1512654483837860004[134] = 0.0;
   out_1512654483837860004[135] = 0.0;
   out_1512654483837860004[136] = 0.0;
   out_1512654483837860004[137] = 0.0;
   out_1512654483837860004[138] = 0.0;
   out_1512654483837860004[139] = 0.0;
   out_1512654483837860004[140] = 0.0;
   out_1512654483837860004[141] = 0.0;
   out_1512654483837860004[142] = 0.0;
   out_1512654483837860004[143] = 0.0;
   out_1512654483837860004[144] = 0.0;
   out_1512654483837860004[145] = 0.0;
   out_1512654483837860004[146] = 0.0;
   out_1512654483837860004[147] = 0.0;
   out_1512654483837860004[148] = 0.0;
   out_1512654483837860004[149] = 0.0;
   out_1512654483837860004[150] = 0.0;
   out_1512654483837860004[151] = 0.0;
   out_1512654483837860004[152] = 1.0;
   out_1512654483837860004[153] = 0.0;
   out_1512654483837860004[154] = 0.0;
   out_1512654483837860004[155] = 0.0;
   out_1512654483837860004[156] = 0.0;
   out_1512654483837860004[157] = 0.0;
   out_1512654483837860004[158] = 0.0;
   out_1512654483837860004[159] = 0.0;
   out_1512654483837860004[160] = 0.0;
   out_1512654483837860004[161] = 0.0;
   out_1512654483837860004[162] = 0.0;
   out_1512654483837860004[163] = 0.0;
   out_1512654483837860004[164] = 0.0;
   out_1512654483837860004[165] = 0.0;
   out_1512654483837860004[166] = 0.0;
   out_1512654483837860004[167] = 0.0;
   out_1512654483837860004[168] = 0.0;
   out_1512654483837860004[169] = 0.0;
   out_1512654483837860004[170] = 0.0;
   out_1512654483837860004[171] = 1.0;
   out_1512654483837860004[172] = 0.0;
   out_1512654483837860004[173] = 0.0;
   out_1512654483837860004[174] = 0.0;
   out_1512654483837860004[175] = 0.0;
   out_1512654483837860004[176] = 0.0;
   out_1512654483837860004[177] = 0.0;
   out_1512654483837860004[178] = 0.0;
   out_1512654483837860004[179] = 0.0;
   out_1512654483837860004[180] = 0.0;
   out_1512654483837860004[181] = 0.0;
   out_1512654483837860004[182] = 0.0;
   out_1512654483837860004[183] = 0.0;
   out_1512654483837860004[184] = 0.0;
   out_1512654483837860004[185] = 0.0;
   out_1512654483837860004[186] = 0.0;
   out_1512654483837860004[187] = 0.0;
   out_1512654483837860004[188] = 0.0;
   out_1512654483837860004[189] = 0.0;
   out_1512654483837860004[190] = 1.0;
   out_1512654483837860004[191] = 0.0;
   out_1512654483837860004[192] = 0.0;
   out_1512654483837860004[193] = 0.0;
   out_1512654483837860004[194] = 0.0;
   out_1512654483837860004[195] = 0.0;
   out_1512654483837860004[196] = 0.0;
   out_1512654483837860004[197] = 0.0;
   out_1512654483837860004[198] = 0.0;
   out_1512654483837860004[199] = 0.0;
   out_1512654483837860004[200] = 0.0;
   out_1512654483837860004[201] = 0.0;
   out_1512654483837860004[202] = 0.0;
   out_1512654483837860004[203] = 0.0;
   out_1512654483837860004[204] = 0.0;
   out_1512654483837860004[205] = 0.0;
   out_1512654483837860004[206] = 0.0;
   out_1512654483837860004[207] = 0.0;
   out_1512654483837860004[208] = 0.0;
   out_1512654483837860004[209] = 1.0;
   out_1512654483837860004[210] = 0.0;
   out_1512654483837860004[211] = 0.0;
   out_1512654483837860004[212] = 0.0;
   out_1512654483837860004[213] = 0.0;
   out_1512654483837860004[214] = 0.0;
   out_1512654483837860004[215] = 0.0;
   out_1512654483837860004[216] = 0.0;
   out_1512654483837860004[217] = 0.0;
   out_1512654483837860004[218] = 0.0;
   out_1512654483837860004[219] = 0.0;
   out_1512654483837860004[220] = 0.0;
   out_1512654483837860004[221] = 0.0;
   out_1512654483837860004[222] = 0.0;
   out_1512654483837860004[223] = 0.0;
   out_1512654483837860004[224] = 0.0;
   out_1512654483837860004[225] = 0.0;
   out_1512654483837860004[226] = 0.0;
   out_1512654483837860004[227] = 0.0;
   out_1512654483837860004[228] = 1.0;
   out_1512654483837860004[229] = 0.0;
   out_1512654483837860004[230] = 0.0;
   out_1512654483837860004[231] = 0.0;
   out_1512654483837860004[232] = 0.0;
   out_1512654483837860004[233] = 0.0;
   out_1512654483837860004[234] = 0.0;
   out_1512654483837860004[235] = 0.0;
   out_1512654483837860004[236] = 0.0;
   out_1512654483837860004[237] = 0.0;
   out_1512654483837860004[238] = 0.0;
   out_1512654483837860004[239] = 0.0;
   out_1512654483837860004[240] = 0.0;
   out_1512654483837860004[241] = 0.0;
   out_1512654483837860004[242] = 0.0;
   out_1512654483837860004[243] = 0.0;
   out_1512654483837860004[244] = 0.0;
   out_1512654483837860004[245] = 0.0;
   out_1512654483837860004[246] = 0.0;
   out_1512654483837860004[247] = 1.0;
   out_1512654483837860004[248] = 0.0;
   out_1512654483837860004[249] = 0.0;
   out_1512654483837860004[250] = 0.0;
   out_1512654483837860004[251] = 0.0;
   out_1512654483837860004[252] = 0.0;
   out_1512654483837860004[253] = 0.0;
   out_1512654483837860004[254] = 0.0;
   out_1512654483837860004[255] = 0.0;
   out_1512654483837860004[256] = 0.0;
   out_1512654483837860004[257] = 0.0;
   out_1512654483837860004[258] = 0.0;
   out_1512654483837860004[259] = 0.0;
   out_1512654483837860004[260] = 0.0;
   out_1512654483837860004[261] = 0.0;
   out_1512654483837860004[262] = 0.0;
   out_1512654483837860004[263] = 0.0;
   out_1512654483837860004[264] = 0.0;
   out_1512654483837860004[265] = 0.0;
   out_1512654483837860004[266] = 1.0;
   out_1512654483837860004[267] = 0.0;
   out_1512654483837860004[268] = 0.0;
   out_1512654483837860004[269] = 0.0;
   out_1512654483837860004[270] = 0.0;
   out_1512654483837860004[271] = 0.0;
   out_1512654483837860004[272] = 0.0;
   out_1512654483837860004[273] = 0.0;
   out_1512654483837860004[274] = 0.0;
   out_1512654483837860004[275] = 0.0;
   out_1512654483837860004[276] = 0.0;
   out_1512654483837860004[277] = 0.0;
   out_1512654483837860004[278] = 0.0;
   out_1512654483837860004[279] = 0.0;
   out_1512654483837860004[280] = 0.0;
   out_1512654483837860004[281] = 0.0;
   out_1512654483837860004[282] = 0.0;
   out_1512654483837860004[283] = 0.0;
   out_1512654483837860004[284] = 0.0;
   out_1512654483837860004[285] = 1.0;
   out_1512654483837860004[286] = 0.0;
   out_1512654483837860004[287] = 0.0;
   out_1512654483837860004[288] = 0.0;
   out_1512654483837860004[289] = 0.0;
   out_1512654483837860004[290] = 0.0;
   out_1512654483837860004[291] = 0.0;
   out_1512654483837860004[292] = 0.0;
   out_1512654483837860004[293] = 0.0;
   out_1512654483837860004[294] = 0.0;
   out_1512654483837860004[295] = 0.0;
   out_1512654483837860004[296] = 0.0;
   out_1512654483837860004[297] = 0.0;
   out_1512654483837860004[298] = 0.0;
   out_1512654483837860004[299] = 0.0;
   out_1512654483837860004[300] = 0.0;
   out_1512654483837860004[301] = 0.0;
   out_1512654483837860004[302] = 0.0;
   out_1512654483837860004[303] = 0.0;
   out_1512654483837860004[304] = 1.0;
   out_1512654483837860004[305] = 0.0;
   out_1512654483837860004[306] = 0.0;
   out_1512654483837860004[307] = 0.0;
   out_1512654483837860004[308] = 0.0;
   out_1512654483837860004[309] = 0.0;
   out_1512654483837860004[310] = 0.0;
   out_1512654483837860004[311] = 0.0;
   out_1512654483837860004[312] = 0.0;
   out_1512654483837860004[313] = 0.0;
   out_1512654483837860004[314] = 0.0;
   out_1512654483837860004[315] = 0.0;
   out_1512654483837860004[316] = 0.0;
   out_1512654483837860004[317] = 0.0;
   out_1512654483837860004[318] = 0.0;
   out_1512654483837860004[319] = 0.0;
   out_1512654483837860004[320] = 0.0;
   out_1512654483837860004[321] = 0.0;
   out_1512654483837860004[322] = 0.0;
   out_1512654483837860004[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_2374336605048301418) {
   out_2374336605048301418[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_2374336605048301418[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_2374336605048301418[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_2374336605048301418[3] = dt*state[12] + state[3];
   out_2374336605048301418[4] = dt*state[13] + state[4];
   out_2374336605048301418[5] = dt*state[14] + state[5];
   out_2374336605048301418[6] = state[6];
   out_2374336605048301418[7] = state[7];
   out_2374336605048301418[8] = state[8];
   out_2374336605048301418[9] = state[9];
   out_2374336605048301418[10] = state[10];
   out_2374336605048301418[11] = state[11];
   out_2374336605048301418[12] = state[12];
   out_2374336605048301418[13] = state[13];
   out_2374336605048301418[14] = state[14];
   out_2374336605048301418[15] = state[15];
   out_2374336605048301418[16] = state[16];
   out_2374336605048301418[17] = state[17];
}
void F_fun(double *state, double dt, double *out_7174832122982687242) {
   out_7174832122982687242[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_7174832122982687242[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_7174832122982687242[2] = 0;
   out_7174832122982687242[3] = 0;
   out_7174832122982687242[4] = 0;
   out_7174832122982687242[5] = 0;
   out_7174832122982687242[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_7174832122982687242[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_7174832122982687242[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_7174832122982687242[9] = 0;
   out_7174832122982687242[10] = 0;
   out_7174832122982687242[11] = 0;
   out_7174832122982687242[12] = 0;
   out_7174832122982687242[13] = 0;
   out_7174832122982687242[14] = 0;
   out_7174832122982687242[15] = 0;
   out_7174832122982687242[16] = 0;
   out_7174832122982687242[17] = 0;
   out_7174832122982687242[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_7174832122982687242[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_7174832122982687242[20] = 0;
   out_7174832122982687242[21] = 0;
   out_7174832122982687242[22] = 0;
   out_7174832122982687242[23] = 0;
   out_7174832122982687242[24] = 0;
   out_7174832122982687242[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_7174832122982687242[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_7174832122982687242[27] = 0;
   out_7174832122982687242[28] = 0;
   out_7174832122982687242[29] = 0;
   out_7174832122982687242[30] = 0;
   out_7174832122982687242[31] = 0;
   out_7174832122982687242[32] = 0;
   out_7174832122982687242[33] = 0;
   out_7174832122982687242[34] = 0;
   out_7174832122982687242[35] = 0;
   out_7174832122982687242[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_7174832122982687242[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_7174832122982687242[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_7174832122982687242[39] = 0;
   out_7174832122982687242[40] = 0;
   out_7174832122982687242[41] = 0;
   out_7174832122982687242[42] = 0;
   out_7174832122982687242[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_7174832122982687242[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_7174832122982687242[45] = 0;
   out_7174832122982687242[46] = 0;
   out_7174832122982687242[47] = 0;
   out_7174832122982687242[48] = 0;
   out_7174832122982687242[49] = 0;
   out_7174832122982687242[50] = 0;
   out_7174832122982687242[51] = 0;
   out_7174832122982687242[52] = 0;
   out_7174832122982687242[53] = 0;
   out_7174832122982687242[54] = 0;
   out_7174832122982687242[55] = 0;
   out_7174832122982687242[56] = 0;
   out_7174832122982687242[57] = 1;
   out_7174832122982687242[58] = 0;
   out_7174832122982687242[59] = 0;
   out_7174832122982687242[60] = 0;
   out_7174832122982687242[61] = 0;
   out_7174832122982687242[62] = 0;
   out_7174832122982687242[63] = 0;
   out_7174832122982687242[64] = 0;
   out_7174832122982687242[65] = 0;
   out_7174832122982687242[66] = dt;
   out_7174832122982687242[67] = 0;
   out_7174832122982687242[68] = 0;
   out_7174832122982687242[69] = 0;
   out_7174832122982687242[70] = 0;
   out_7174832122982687242[71] = 0;
   out_7174832122982687242[72] = 0;
   out_7174832122982687242[73] = 0;
   out_7174832122982687242[74] = 0;
   out_7174832122982687242[75] = 0;
   out_7174832122982687242[76] = 1;
   out_7174832122982687242[77] = 0;
   out_7174832122982687242[78] = 0;
   out_7174832122982687242[79] = 0;
   out_7174832122982687242[80] = 0;
   out_7174832122982687242[81] = 0;
   out_7174832122982687242[82] = 0;
   out_7174832122982687242[83] = 0;
   out_7174832122982687242[84] = 0;
   out_7174832122982687242[85] = dt;
   out_7174832122982687242[86] = 0;
   out_7174832122982687242[87] = 0;
   out_7174832122982687242[88] = 0;
   out_7174832122982687242[89] = 0;
   out_7174832122982687242[90] = 0;
   out_7174832122982687242[91] = 0;
   out_7174832122982687242[92] = 0;
   out_7174832122982687242[93] = 0;
   out_7174832122982687242[94] = 0;
   out_7174832122982687242[95] = 1;
   out_7174832122982687242[96] = 0;
   out_7174832122982687242[97] = 0;
   out_7174832122982687242[98] = 0;
   out_7174832122982687242[99] = 0;
   out_7174832122982687242[100] = 0;
   out_7174832122982687242[101] = 0;
   out_7174832122982687242[102] = 0;
   out_7174832122982687242[103] = 0;
   out_7174832122982687242[104] = dt;
   out_7174832122982687242[105] = 0;
   out_7174832122982687242[106] = 0;
   out_7174832122982687242[107] = 0;
   out_7174832122982687242[108] = 0;
   out_7174832122982687242[109] = 0;
   out_7174832122982687242[110] = 0;
   out_7174832122982687242[111] = 0;
   out_7174832122982687242[112] = 0;
   out_7174832122982687242[113] = 0;
   out_7174832122982687242[114] = 1;
   out_7174832122982687242[115] = 0;
   out_7174832122982687242[116] = 0;
   out_7174832122982687242[117] = 0;
   out_7174832122982687242[118] = 0;
   out_7174832122982687242[119] = 0;
   out_7174832122982687242[120] = 0;
   out_7174832122982687242[121] = 0;
   out_7174832122982687242[122] = 0;
   out_7174832122982687242[123] = 0;
   out_7174832122982687242[124] = 0;
   out_7174832122982687242[125] = 0;
   out_7174832122982687242[126] = 0;
   out_7174832122982687242[127] = 0;
   out_7174832122982687242[128] = 0;
   out_7174832122982687242[129] = 0;
   out_7174832122982687242[130] = 0;
   out_7174832122982687242[131] = 0;
   out_7174832122982687242[132] = 0;
   out_7174832122982687242[133] = 1;
   out_7174832122982687242[134] = 0;
   out_7174832122982687242[135] = 0;
   out_7174832122982687242[136] = 0;
   out_7174832122982687242[137] = 0;
   out_7174832122982687242[138] = 0;
   out_7174832122982687242[139] = 0;
   out_7174832122982687242[140] = 0;
   out_7174832122982687242[141] = 0;
   out_7174832122982687242[142] = 0;
   out_7174832122982687242[143] = 0;
   out_7174832122982687242[144] = 0;
   out_7174832122982687242[145] = 0;
   out_7174832122982687242[146] = 0;
   out_7174832122982687242[147] = 0;
   out_7174832122982687242[148] = 0;
   out_7174832122982687242[149] = 0;
   out_7174832122982687242[150] = 0;
   out_7174832122982687242[151] = 0;
   out_7174832122982687242[152] = 1;
   out_7174832122982687242[153] = 0;
   out_7174832122982687242[154] = 0;
   out_7174832122982687242[155] = 0;
   out_7174832122982687242[156] = 0;
   out_7174832122982687242[157] = 0;
   out_7174832122982687242[158] = 0;
   out_7174832122982687242[159] = 0;
   out_7174832122982687242[160] = 0;
   out_7174832122982687242[161] = 0;
   out_7174832122982687242[162] = 0;
   out_7174832122982687242[163] = 0;
   out_7174832122982687242[164] = 0;
   out_7174832122982687242[165] = 0;
   out_7174832122982687242[166] = 0;
   out_7174832122982687242[167] = 0;
   out_7174832122982687242[168] = 0;
   out_7174832122982687242[169] = 0;
   out_7174832122982687242[170] = 0;
   out_7174832122982687242[171] = 1;
   out_7174832122982687242[172] = 0;
   out_7174832122982687242[173] = 0;
   out_7174832122982687242[174] = 0;
   out_7174832122982687242[175] = 0;
   out_7174832122982687242[176] = 0;
   out_7174832122982687242[177] = 0;
   out_7174832122982687242[178] = 0;
   out_7174832122982687242[179] = 0;
   out_7174832122982687242[180] = 0;
   out_7174832122982687242[181] = 0;
   out_7174832122982687242[182] = 0;
   out_7174832122982687242[183] = 0;
   out_7174832122982687242[184] = 0;
   out_7174832122982687242[185] = 0;
   out_7174832122982687242[186] = 0;
   out_7174832122982687242[187] = 0;
   out_7174832122982687242[188] = 0;
   out_7174832122982687242[189] = 0;
   out_7174832122982687242[190] = 1;
   out_7174832122982687242[191] = 0;
   out_7174832122982687242[192] = 0;
   out_7174832122982687242[193] = 0;
   out_7174832122982687242[194] = 0;
   out_7174832122982687242[195] = 0;
   out_7174832122982687242[196] = 0;
   out_7174832122982687242[197] = 0;
   out_7174832122982687242[198] = 0;
   out_7174832122982687242[199] = 0;
   out_7174832122982687242[200] = 0;
   out_7174832122982687242[201] = 0;
   out_7174832122982687242[202] = 0;
   out_7174832122982687242[203] = 0;
   out_7174832122982687242[204] = 0;
   out_7174832122982687242[205] = 0;
   out_7174832122982687242[206] = 0;
   out_7174832122982687242[207] = 0;
   out_7174832122982687242[208] = 0;
   out_7174832122982687242[209] = 1;
   out_7174832122982687242[210] = 0;
   out_7174832122982687242[211] = 0;
   out_7174832122982687242[212] = 0;
   out_7174832122982687242[213] = 0;
   out_7174832122982687242[214] = 0;
   out_7174832122982687242[215] = 0;
   out_7174832122982687242[216] = 0;
   out_7174832122982687242[217] = 0;
   out_7174832122982687242[218] = 0;
   out_7174832122982687242[219] = 0;
   out_7174832122982687242[220] = 0;
   out_7174832122982687242[221] = 0;
   out_7174832122982687242[222] = 0;
   out_7174832122982687242[223] = 0;
   out_7174832122982687242[224] = 0;
   out_7174832122982687242[225] = 0;
   out_7174832122982687242[226] = 0;
   out_7174832122982687242[227] = 0;
   out_7174832122982687242[228] = 1;
   out_7174832122982687242[229] = 0;
   out_7174832122982687242[230] = 0;
   out_7174832122982687242[231] = 0;
   out_7174832122982687242[232] = 0;
   out_7174832122982687242[233] = 0;
   out_7174832122982687242[234] = 0;
   out_7174832122982687242[235] = 0;
   out_7174832122982687242[236] = 0;
   out_7174832122982687242[237] = 0;
   out_7174832122982687242[238] = 0;
   out_7174832122982687242[239] = 0;
   out_7174832122982687242[240] = 0;
   out_7174832122982687242[241] = 0;
   out_7174832122982687242[242] = 0;
   out_7174832122982687242[243] = 0;
   out_7174832122982687242[244] = 0;
   out_7174832122982687242[245] = 0;
   out_7174832122982687242[246] = 0;
   out_7174832122982687242[247] = 1;
   out_7174832122982687242[248] = 0;
   out_7174832122982687242[249] = 0;
   out_7174832122982687242[250] = 0;
   out_7174832122982687242[251] = 0;
   out_7174832122982687242[252] = 0;
   out_7174832122982687242[253] = 0;
   out_7174832122982687242[254] = 0;
   out_7174832122982687242[255] = 0;
   out_7174832122982687242[256] = 0;
   out_7174832122982687242[257] = 0;
   out_7174832122982687242[258] = 0;
   out_7174832122982687242[259] = 0;
   out_7174832122982687242[260] = 0;
   out_7174832122982687242[261] = 0;
   out_7174832122982687242[262] = 0;
   out_7174832122982687242[263] = 0;
   out_7174832122982687242[264] = 0;
   out_7174832122982687242[265] = 0;
   out_7174832122982687242[266] = 1;
   out_7174832122982687242[267] = 0;
   out_7174832122982687242[268] = 0;
   out_7174832122982687242[269] = 0;
   out_7174832122982687242[270] = 0;
   out_7174832122982687242[271] = 0;
   out_7174832122982687242[272] = 0;
   out_7174832122982687242[273] = 0;
   out_7174832122982687242[274] = 0;
   out_7174832122982687242[275] = 0;
   out_7174832122982687242[276] = 0;
   out_7174832122982687242[277] = 0;
   out_7174832122982687242[278] = 0;
   out_7174832122982687242[279] = 0;
   out_7174832122982687242[280] = 0;
   out_7174832122982687242[281] = 0;
   out_7174832122982687242[282] = 0;
   out_7174832122982687242[283] = 0;
   out_7174832122982687242[284] = 0;
   out_7174832122982687242[285] = 1;
   out_7174832122982687242[286] = 0;
   out_7174832122982687242[287] = 0;
   out_7174832122982687242[288] = 0;
   out_7174832122982687242[289] = 0;
   out_7174832122982687242[290] = 0;
   out_7174832122982687242[291] = 0;
   out_7174832122982687242[292] = 0;
   out_7174832122982687242[293] = 0;
   out_7174832122982687242[294] = 0;
   out_7174832122982687242[295] = 0;
   out_7174832122982687242[296] = 0;
   out_7174832122982687242[297] = 0;
   out_7174832122982687242[298] = 0;
   out_7174832122982687242[299] = 0;
   out_7174832122982687242[300] = 0;
   out_7174832122982687242[301] = 0;
   out_7174832122982687242[302] = 0;
   out_7174832122982687242[303] = 0;
   out_7174832122982687242[304] = 1;
   out_7174832122982687242[305] = 0;
   out_7174832122982687242[306] = 0;
   out_7174832122982687242[307] = 0;
   out_7174832122982687242[308] = 0;
   out_7174832122982687242[309] = 0;
   out_7174832122982687242[310] = 0;
   out_7174832122982687242[311] = 0;
   out_7174832122982687242[312] = 0;
   out_7174832122982687242[313] = 0;
   out_7174832122982687242[314] = 0;
   out_7174832122982687242[315] = 0;
   out_7174832122982687242[316] = 0;
   out_7174832122982687242[317] = 0;
   out_7174832122982687242[318] = 0;
   out_7174832122982687242[319] = 0;
   out_7174832122982687242[320] = 0;
   out_7174832122982687242[321] = 0;
   out_7174832122982687242[322] = 0;
   out_7174832122982687242[323] = 1;
}
void h_4(double *state, double *unused, double *out_5731849632354204325) {
   out_5731849632354204325[0] = state[6] + state[9];
   out_5731849632354204325[1] = state[7] + state[10];
   out_5731849632354204325[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_388519179644441129) {
   out_388519179644441129[0] = 0;
   out_388519179644441129[1] = 0;
   out_388519179644441129[2] = 0;
   out_388519179644441129[3] = 0;
   out_388519179644441129[4] = 0;
   out_388519179644441129[5] = 0;
   out_388519179644441129[6] = 1;
   out_388519179644441129[7] = 0;
   out_388519179644441129[8] = 0;
   out_388519179644441129[9] = 1;
   out_388519179644441129[10] = 0;
   out_388519179644441129[11] = 0;
   out_388519179644441129[12] = 0;
   out_388519179644441129[13] = 0;
   out_388519179644441129[14] = 0;
   out_388519179644441129[15] = 0;
   out_388519179644441129[16] = 0;
   out_388519179644441129[17] = 0;
   out_388519179644441129[18] = 0;
   out_388519179644441129[19] = 0;
   out_388519179644441129[20] = 0;
   out_388519179644441129[21] = 0;
   out_388519179644441129[22] = 0;
   out_388519179644441129[23] = 0;
   out_388519179644441129[24] = 0;
   out_388519179644441129[25] = 1;
   out_388519179644441129[26] = 0;
   out_388519179644441129[27] = 0;
   out_388519179644441129[28] = 1;
   out_388519179644441129[29] = 0;
   out_388519179644441129[30] = 0;
   out_388519179644441129[31] = 0;
   out_388519179644441129[32] = 0;
   out_388519179644441129[33] = 0;
   out_388519179644441129[34] = 0;
   out_388519179644441129[35] = 0;
   out_388519179644441129[36] = 0;
   out_388519179644441129[37] = 0;
   out_388519179644441129[38] = 0;
   out_388519179644441129[39] = 0;
   out_388519179644441129[40] = 0;
   out_388519179644441129[41] = 0;
   out_388519179644441129[42] = 0;
   out_388519179644441129[43] = 0;
   out_388519179644441129[44] = 1;
   out_388519179644441129[45] = 0;
   out_388519179644441129[46] = 0;
   out_388519179644441129[47] = 1;
   out_388519179644441129[48] = 0;
   out_388519179644441129[49] = 0;
   out_388519179644441129[50] = 0;
   out_388519179644441129[51] = 0;
   out_388519179644441129[52] = 0;
   out_388519179644441129[53] = 0;
}
void h_10(double *state, double *unused, double *out_6794229724487339636) {
   out_6794229724487339636[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_6794229724487339636[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_6794229724487339636[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_7294889413993203975) {
   out_7294889413993203975[0] = 0;
   out_7294889413993203975[1] = 9.8100000000000005*cos(state[1]);
   out_7294889413993203975[2] = 0;
   out_7294889413993203975[3] = 0;
   out_7294889413993203975[4] = -state[8];
   out_7294889413993203975[5] = state[7];
   out_7294889413993203975[6] = 0;
   out_7294889413993203975[7] = state[5];
   out_7294889413993203975[8] = -state[4];
   out_7294889413993203975[9] = 0;
   out_7294889413993203975[10] = 0;
   out_7294889413993203975[11] = 0;
   out_7294889413993203975[12] = 1;
   out_7294889413993203975[13] = 0;
   out_7294889413993203975[14] = 0;
   out_7294889413993203975[15] = 1;
   out_7294889413993203975[16] = 0;
   out_7294889413993203975[17] = 0;
   out_7294889413993203975[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_7294889413993203975[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_7294889413993203975[20] = 0;
   out_7294889413993203975[21] = state[8];
   out_7294889413993203975[22] = 0;
   out_7294889413993203975[23] = -state[6];
   out_7294889413993203975[24] = -state[5];
   out_7294889413993203975[25] = 0;
   out_7294889413993203975[26] = state[3];
   out_7294889413993203975[27] = 0;
   out_7294889413993203975[28] = 0;
   out_7294889413993203975[29] = 0;
   out_7294889413993203975[30] = 0;
   out_7294889413993203975[31] = 1;
   out_7294889413993203975[32] = 0;
   out_7294889413993203975[33] = 0;
   out_7294889413993203975[34] = 1;
   out_7294889413993203975[35] = 0;
   out_7294889413993203975[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_7294889413993203975[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_7294889413993203975[38] = 0;
   out_7294889413993203975[39] = -state[7];
   out_7294889413993203975[40] = state[6];
   out_7294889413993203975[41] = 0;
   out_7294889413993203975[42] = state[4];
   out_7294889413993203975[43] = -state[3];
   out_7294889413993203975[44] = 0;
   out_7294889413993203975[45] = 0;
   out_7294889413993203975[46] = 0;
   out_7294889413993203975[47] = 0;
   out_7294889413993203975[48] = 0;
   out_7294889413993203975[49] = 0;
   out_7294889413993203975[50] = 1;
   out_7294889413993203975[51] = 0;
   out_7294889413993203975[52] = 0;
   out_7294889413993203975[53] = 1;
}
void h_13(double *state, double *unused, double *out_6365979606409915125) {
   out_6365979606409915125[0] = state[3];
   out_6365979606409915125[1] = state[4];
   out_6365979606409915125[2] = state[5];
}
void H_13(double *state, double *unused, double *out_2823754645687891672) {
   out_2823754645687891672[0] = 0;
   out_2823754645687891672[1] = 0;
   out_2823754645687891672[2] = 0;
   out_2823754645687891672[3] = 1;
   out_2823754645687891672[4] = 0;
   out_2823754645687891672[5] = 0;
   out_2823754645687891672[6] = 0;
   out_2823754645687891672[7] = 0;
   out_2823754645687891672[8] = 0;
   out_2823754645687891672[9] = 0;
   out_2823754645687891672[10] = 0;
   out_2823754645687891672[11] = 0;
   out_2823754645687891672[12] = 0;
   out_2823754645687891672[13] = 0;
   out_2823754645687891672[14] = 0;
   out_2823754645687891672[15] = 0;
   out_2823754645687891672[16] = 0;
   out_2823754645687891672[17] = 0;
   out_2823754645687891672[18] = 0;
   out_2823754645687891672[19] = 0;
   out_2823754645687891672[20] = 0;
   out_2823754645687891672[21] = 0;
   out_2823754645687891672[22] = 1;
   out_2823754645687891672[23] = 0;
   out_2823754645687891672[24] = 0;
   out_2823754645687891672[25] = 0;
   out_2823754645687891672[26] = 0;
   out_2823754645687891672[27] = 0;
   out_2823754645687891672[28] = 0;
   out_2823754645687891672[29] = 0;
   out_2823754645687891672[30] = 0;
   out_2823754645687891672[31] = 0;
   out_2823754645687891672[32] = 0;
   out_2823754645687891672[33] = 0;
   out_2823754645687891672[34] = 0;
   out_2823754645687891672[35] = 0;
   out_2823754645687891672[36] = 0;
   out_2823754645687891672[37] = 0;
   out_2823754645687891672[38] = 0;
   out_2823754645687891672[39] = 0;
   out_2823754645687891672[40] = 0;
   out_2823754645687891672[41] = 1;
   out_2823754645687891672[42] = 0;
   out_2823754645687891672[43] = 0;
   out_2823754645687891672[44] = 0;
   out_2823754645687891672[45] = 0;
   out_2823754645687891672[46] = 0;
   out_2823754645687891672[47] = 0;
   out_2823754645687891672[48] = 0;
   out_2823754645687891672[49] = 0;
   out_2823754645687891672[50] = 0;
   out_2823754645687891672[51] = 0;
   out_2823754645687891672[52] = 0;
   out_2823754645687891672[53] = 0;
}
void h_14(double *state, double *unused, double *out_7685359376293741420) {
   out_7685359376293741420[0] = state[6];
   out_7685359376293741420[1] = state[7];
   out_7685359376293741420[2] = state[8];
}
void H_14(double *state, double *unused, double *out_3574721676695043400) {
   out_3574721676695043400[0] = 0;
   out_3574721676695043400[1] = 0;
   out_3574721676695043400[2] = 0;
   out_3574721676695043400[3] = 0;
   out_3574721676695043400[4] = 0;
   out_3574721676695043400[5] = 0;
   out_3574721676695043400[6] = 1;
   out_3574721676695043400[7] = 0;
   out_3574721676695043400[8] = 0;
   out_3574721676695043400[9] = 0;
   out_3574721676695043400[10] = 0;
   out_3574721676695043400[11] = 0;
   out_3574721676695043400[12] = 0;
   out_3574721676695043400[13] = 0;
   out_3574721676695043400[14] = 0;
   out_3574721676695043400[15] = 0;
   out_3574721676695043400[16] = 0;
   out_3574721676695043400[17] = 0;
   out_3574721676695043400[18] = 0;
   out_3574721676695043400[19] = 0;
   out_3574721676695043400[20] = 0;
   out_3574721676695043400[21] = 0;
   out_3574721676695043400[22] = 0;
   out_3574721676695043400[23] = 0;
   out_3574721676695043400[24] = 0;
   out_3574721676695043400[25] = 1;
   out_3574721676695043400[26] = 0;
   out_3574721676695043400[27] = 0;
   out_3574721676695043400[28] = 0;
   out_3574721676695043400[29] = 0;
   out_3574721676695043400[30] = 0;
   out_3574721676695043400[31] = 0;
   out_3574721676695043400[32] = 0;
   out_3574721676695043400[33] = 0;
   out_3574721676695043400[34] = 0;
   out_3574721676695043400[35] = 0;
   out_3574721676695043400[36] = 0;
   out_3574721676695043400[37] = 0;
   out_3574721676695043400[38] = 0;
   out_3574721676695043400[39] = 0;
   out_3574721676695043400[40] = 0;
   out_3574721676695043400[41] = 0;
   out_3574721676695043400[42] = 0;
   out_3574721676695043400[43] = 0;
   out_3574721676695043400[44] = 1;
   out_3574721676695043400[45] = 0;
   out_3574721676695043400[46] = 0;
   out_3574721676695043400[47] = 0;
   out_3574721676695043400[48] = 0;
   out_3574721676695043400[49] = 0;
   out_3574721676695043400[50] = 0;
   out_3574721676695043400[51] = 0;
   out_3574721676695043400[52] = 0;
   out_3574721676695043400[53] = 0;
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
void pose_err_fun(double *nom_x, double *delta_x, double *out_2078931456649821549) {
  err_fun(nom_x, delta_x, out_2078931456649821549);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_4018826878271793945) {
  inv_err_fun(nom_x, true_x, out_4018826878271793945);
}
void pose_H_mod_fun(double *state, double *out_1512654483837860004) {
  H_mod_fun(state, out_1512654483837860004);
}
void pose_f_fun(double *state, double dt, double *out_2374336605048301418) {
  f_fun(state,  dt, out_2374336605048301418);
}
void pose_F_fun(double *state, double dt, double *out_7174832122982687242) {
  F_fun(state,  dt, out_7174832122982687242);
}
void pose_h_4(double *state, double *unused, double *out_5731849632354204325) {
  h_4(state, unused, out_5731849632354204325);
}
void pose_H_4(double *state, double *unused, double *out_388519179644441129) {
  H_4(state, unused, out_388519179644441129);
}
void pose_h_10(double *state, double *unused, double *out_6794229724487339636) {
  h_10(state, unused, out_6794229724487339636);
}
void pose_H_10(double *state, double *unused, double *out_7294889413993203975) {
  H_10(state, unused, out_7294889413993203975);
}
void pose_h_13(double *state, double *unused, double *out_6365979606409915125) {
  h_13(state, unused, out_6365979606409915125);
}
void pose_H_13(double *state, double *unused, double *out_2823754645687891672) {
  H_13(state, unused, out_2823754645687891672);
}
void pose_h_14(double *state, double *unused, double *out_7685359376293741420) {
  h_14(state, unused, out_7685359376293741420);
}
void pose_H_14(double *state, double *unused, double *out_3574721676695043400) {
  H_14(state, unused, out_3574721676695043400);
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
