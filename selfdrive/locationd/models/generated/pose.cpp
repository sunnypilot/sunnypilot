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
void err_fun(double *nom_x, double *delta_x, double *out_9115622508544891145) {
   out_9115622508544891145[0] = delta_x[0] + nom_x[0];
   out_9115622508544891145[1] = delta_x[1] + nom_x[1];
   out_9115622508544891145[2] = delta_x[2] + nom_x[2];
   out_9115622508544891145[3] = delta_x[3] + nom_x[3];
   out_9115622508544891145[4] = delta_x[4] + nom_x[4];
   out_9115622508544891145[5] = delta_x[5] + nom_x[5];
   out_9115622508544891145[6] = delta_x[6] + nom_x[6];
   out_9115622508544891145[7] = delta_x[7] + nom_x[7];
   out_9115622508544891145[8] = delta_x[8] + nom_x[8];
   out_9115622508544891145[9] = delta_x[9] + nom_x[9];
   out_9115622508544891145[10] = delta_x[10] + nom_x[10];
   out_9115622508544891145[11] = delta_x[11] + nom_x[11];
   out_9115622508544891145[12] = delta_x[12] + nom_x[12];
   out_9115622508544891145[13] = delta_x[13] + nom_x[13];
   out_9115622508544891145[14] = delta_x[14] + nom_x[14];
   out_9115622508544891145[15] = delta_x[15] + nom_x[15];
   out_9115622508544891145[16] = delta_x[16] + nom_x[16];
   out_9115622508544891145[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_112942660134600720) {
   out_112942660134600720[0] = -nom_x[0] + true_x[0];
   out_112942660134600720[1] = -nom_x[1] + true_x[1];
   out_112942660134600720[2] = -nom_x[2] + true_x[2];
   out_112942660134600720[3] = -nom_x[3] + true_x[3];
   out_112942660134600720[4] = -nom_x[4] + true_x[4];
   out_112942660134600720[5] = -nom_x[5] + true_x[5];
   out_112942660134600720[6] = -nom_x[6] + true_x[6];
   out_112942660134600720[7] = -nom_x[7] + true_x[7];
   out_112942660134600720[8] = -nom_x[8] + true_x[8];
   out_112942660134600720[9] = -nom_x[9] + true_x[9];
   out_112942660134600720[10] = -nom_x[10] + true_x[10];
   out_112942660134600720[11] = -nom_x[11] + true_x[11];
   out_112942660134600720[12] = -nom_x[12] + true_x[12];
   out_112942660134600720[13] = -nom_x[13] + true_x[13];
   out_112942660134600720[14] = -nom_x[14] + true_x[14];
   out_112942660134600720[15] = -nom_x[15] + true_x[15];
   out_112942660134600720[16] = -nom_x[16] + true_x[16];
   out_112942660134600720[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_1372883240507492868) {
   out_1372883240507492868[0] = 1.0;
   out_1372883240507492868[1] = 0.0;
   out_1372883240507492868[2] = 0.0;
   out_1372883240507492868[3] = 0.0;
   out_1372883240507492868[4] = 0.0;
   out_1372883240507492868[5] = 0.0;
   out_1372883240507492868[6] = 0.0;
   out_1372883240507492868[7] = 0.0;
   out_1372883240507492868[8] = 0.0;
   out_1372883240507492868[9] = 0.0;
   out_1372883240507492868[10] = 0.0;
   out_1372883240507492868[11] = 0.0;
   out_1372883240507492868[12] = 0.0;
   out_1372883240507492868[13] = 0.0;
   out_1372883240507492868[14] = 0.0;
   out_1372883240507492868[15] = 0.0;
   out_1372883240507492868[16] = 0.0;
   out_1372883240507492868[17] = 0.0;
   out_1372883240507492868[18] = 0.0;
   out_1372883240507492868[19] = 1.0;
   out_1372883240507492868[20] = 0.0;
   out_1372883240507492868[21] = 0.0;
   out_1372883240507492868[22] = 0.0;
   out_1372883240507492868[23] = 0.0;
   out_1372883240507492868[24] = 0.0;
   out_1372883240507492868[25] = 0.0;
   out_1372883240507492868[26] = 0.0;
   out_1372883240507492868[27] = 0.0;
   out_1372883240507492868[28] = 0.0;
   out_1372883240507492868[29] = 0.0;
   out_1372883240507492868[30] = 0.0;
   out_1372883240507492868[31] = 0.0;
   out_1372883240507492868[32] = 0.0;
   out_1372883240507492868[33] = 0.0;
   out_1372883240507492868[34] = 0.0;
   out_1372883240507492868[35] = 0.0;
   out_1372883240507492868[36] = 0.0;
   out_1372883240507492868[37] = 0.0;
   out_1372883240507492868[38] = 1.0;
   out_1372883240507492868[39] = 0.0;
   out_1372883240507492868[40] = 0.0;
   out_1372883240507492868[41] = 0.0;
   out_1372883240507492868[42] = 0.0;
   out_1372883240507492868[43] = 0.0;
   out_1372883240507492868[44] = 0.0;
   out_1372883240507492868[45] = 0.0;
   out_1372883240507492868[46] = 0.0;
   out_1372883240507492868[47] = 0.0;
   out_1372883240507492868[48] = 0.0;
   out_1372883240507492868[49] = 0.0;
   out_1372883240507492868[50] = 0.0;
   out_1372883240507492868[51] = 0.0;
   out_1372883240507492868[52] = 0.0;
   out_1372883240507492868[53] = 0.0;
   out_1372883240507492868[54] = 0.0;
   out_1372883240507492868[55] = 0.0;
   out_1372883240507492868[56] = 0.0;
   out_1372883240507492868[57] = 1.0;
   out_1372883240507492868[58] = 0.0;
   out_1372883240507492868[59] = 0.0;
   out_1372883240507492868[60] = 0.0;
   out_1372883240507492868[61] = 0.0;
   out_1372883240507492868[62] = 0.0;
   out_1372883240507492868[63] = 0.0;
   out_1372883240507492868[64] = 0.0;
   out_1372883240507492868[65] = 0.0;
   out_1372883240507492868[66] = 0.0;
   out_1372883240507492868[67] = 0.0;
   out_1372883240507492868[68] = 0.0;
   out_1372883240507492868[69] = 0.0;
   out_1372883240507492868[70] = 0.0;
   out_1372883240507492868[71] = 0.0;
   out_1372883240507492868[72] = 0.0;
   out_1372883240507492868[73] = 0.0;
   out_1372883240507492868[74] = 0.0;
   out_1372883240507492868[75] = 0.0;
   out_1372883240507492868[76] = 1.0;
   out_1372883240507492868[77] = 0.0;
   out_1372883240507492868[78] = 0.0;
   out_1372883240507492868[79] = 0.0;
   out_1372883240507492868[80] = 0.0;
   out_1372883240507492868[81] = 0.0;
   out_1372883240507492868[82] = 0.0;
   out_1372883240507492868[83] = 0.0;
   out_1372883240507492868[84] = 0.0;
   out_1372883240507492868[85] = 0.0;
   out_1372883240507492868[86] = 0.0;
   out_1372883240507492868[87] = 0.0;
   out_1372883240507492868[88] = 0.0;
   out_1372883240507492868[89] = 0.0;
   out_1372883240507492868[90] = 0.0;
   out_1372883240507492868[91] = 0.0;
   out_1372883240507492868[92] = 0.0;
   out_1372883240507492868[93] = 0.0;
   out_1372883240507492868[94] = 0.0;
   out_1372883240507492868[95] = 1.0;
   out_1372883240507492868[96] = 0.0;
   out_1372883240507492868[97] = 0.0;
   out_1372883240507492868[98] = 0.0;
   out_1372883240507492868[99] = 0.0;
   out_1372883240507492868[100] = 0.0;
   out_1372883240507492868[101] = 0.0;
   out_1372883240507492868[102] = 0.0;
   out_1372883240507492868[103] = 0.0;
   out_1372883240507492868[104] = 0.0;
   out_1372883240507492868[105] = 0.0;
   out_1372883240507492868[106] = 0.0;
   out_1372883240507492868[107] = 0.0;
   out_1372883240507492868[108] = 0.0;
   out_1372883240507492868[109] = 0.0;
   out_1372883240507492868[110] = 0.0;
   out_1372883240507492868[111] = 0.0;
   out_1372883240507492868[112] = 0.0;
   out_1372883240507492868[113] = 0.0;
   out_1372883240507492868[114] = 1.0;
   out_1372883240507492868[115] = 0.0;
   out_1372883240507492868[116] = 0.0;
   out_1372883240507492868[117] = 0.0;
   out_1372883240507492868[118] = 0.0;
   out_1372883240507492868[119] = 0.0;
   out_1372883240507492868[120] = 0.0;
   out_1372883240507492868[121] = 0.0;
   out_1372883240507492868[122] = 0.0;
   out_1372883240507492868[123] = 0.0;
   out_1372883240507492868[124] = 0.0;
   out_1372883240507492868[125] = 0.0;
   out_1372883240507492868[126] = 0.0;
   out_1372883240507492868[127] = 0.0;
   out_1372883240507492868[128] = 0.0;
   out_1372883240507492868[129] = 0.0;
   out_1372883240507492868[130] = 0.0;
   out_1372883240507492868[131] = 0.0;
   out_1372883240507492868[132] = 0.0;
   out_1372883240507492868[133] = 1.0;
   out_1372883240507492868[134] = 0.0;
   out_1372883240507492868[135] = 0.0;
   out_1372883240507492868[136] = 0.0;
   out_1372883240507492868[137] = 0.0;
   out_1372883240507492868[138] = 0.0;
   out_1372883240507492868[139] = 0.0;
   out_1372883240507492868[140] = 0.0;
   out_1372883240507492868[141] = 0.0;
   out_1372883240507492868[142] = 0.0;
   out_1372883240507492868[143] = 0.0;
   out_1372883240507492868[144] = 0.0;
   out_1372883240507492868[145] = 0.0;
   out_1372883240507492868[146] = 0.0;
   out_1372883240507492868[147] = 0.0;
   out_1372883240507492868[148] = 0.0;
   out_1372883240507492868[149] = 0.0;
   out_1372883240507492868[150] = 0.0;
   out_1372883240507492868[151] = 0.0;
   out_1372883240507492868[152] = 1.0;
   out_1372883240507492868[153] = 0.0;
   out_1372883240507492868[154] = 0.0;
   out_1372883240507492868[155] = 0.0;
   out_1372883240507492868[156] = 0.0;
   out_1372883240507492868[157] = 0.0;
   out_1372883240507492868[158] = 0.0;
   out_1372883240507492868[159] = 0.0;
   out_1372883240507492868[160] = 0.0;
   out_1372883240507492868[161] = 0.0;
   out_1372883240507492868[162] = 0.0;
   out_1372883240507492868[163] = 0.0;
   out_1372883240507492868[164] = 0.0;
   out_1372883240507492868[165] = 0.0;
   out_1372883240507492868[166] = 0.0;
   out_1372883240507492868[167] = 0.0;
   out_1372883240507492868[168] = 0.0;
   out_1372883240507492868[169] = 0.0;
   out_1372883240507492868[170] = 0.0;
   out_1372883240507492868[171] = 1.0;
   out_1372883240507492868[172] = 0.0;
   out_1372883240507492868[173] = 0.0;
   out_1372883240507492868[174] = 0.0;
   out_1372883240507492868[175] = 0.0;
   out_1372883240507492868[176] = 0.0;
   out_1372883240507492868[177] = 0.0;
   out_1372883240507492868[178] = 0.0;
   out_1372883240507492868[179] = 0.0;
   out_1372883240507492868[180] = 0.0;
   out_1372883240507492868[181] = 0.0;
   out_1372883240507492868[182] = 0.0;
   out_1372883240507492868[183] = 0.0;
   out_1372883240507492868[184] = 0.0;
   out_1372883240507492868[185] = 0.0;
   out_1372883240507492868[186] = 0.0;
   out_1372883240507492868[187] = 0.0;
   out_1372883240507492868[188] = 0.0;
   out_1372883240507492868[189] = 0.0;
   out_1372883240507492868[190] = 1.0;
   out_1372883240507492868[191] = 0.0;
   out_1372883240507492868[192] = 0.0;
   out_1372883240507492868[193] = 0.0;
   out_1372883240507492868[194] = 0.0;
   out_1372883240507492868[195] = 0.0;
   out_1372883240507492868[196] = 0.0;
   out_1372883240507492868[197] = 0.0;
   out_1372883240507492868[198] = 0.0;
   out_1372883240507492868[199] = 0.0;
   out_1372883240507492868[200] = 0.0;
   out_1372883240507492868[201] = 0.0;
   out_1372883240507492868[202] = 0.0;
   out_1372883240507492868[203] = 0.0;
   out_1372883240507492868[204] = 0.0;
   out_1372883240507492868[205] = 0.0;
   out_1372883240507492868[206] = 0.0;
   out_1372883240507492868[207] = 0.0;
   out_1372883240507492868[208] = 0.0;
   out_1372883240507492868[209] = 1.0;
   out_1372883240507492868[210] = 0.0;
   out_1372883240507492868[211] = 0.0;
   out_1372883240507492868[212] = 0.0;
   out_1372883240507492868[213] = 0.0;
   out_1372883240507492868[214] = 0.0;
   out_1372883240507492868[215] = 0.0;
   out_1372883240507492868[216] = 0.0;
   out_1372883240507492868[217] = 0.0;
   out_1372883240507492868[218] = 0.0;
   out_1372883240507492868[219] = 0.0;
   out_1372883240507492868[220] = 0.0;
   out_1372883240507492868[221] = 0.0;
   out_1372883240507492868[222] = 0.0;
   out_1372883240507492868[223] = 0.0;
   out_1372883240507492868[224] = 0.0;
   out_1372883240507492868[225] = 0.0;
   out_1372883240507492868[226] = 0.0;
   out_1372883240507492868[227] = 0.0;
   out_1372883240507492868[228] = 1.0;
   out_1372883240507492868[229] = 0.0;
   out_1372883240507492868[230] = 0.0;
   out_1372883240507492868[231] = 0.0;
   out_1372883240507492868[232] = 0.0;
   out_1372883240507492868[233] = 0.0;
   out_1372883240507492868[234] = 0.0;
   out_1372883240507492868[235] = 0.0;
   out_1372883240507492868[236] = 0.0;
   out_1372883240507492868[237] = 0.0;
   out_1372883240507492868[238] = 0.0;
   out_1372883240507492868[239] = 0.0;
   out_1372883240507492868[240] = 0.0;
   out_1372883240507492868[241] = 0.0;
   out_1372883240507492868[242] = 0.0;
   out_1372883240507492868[243] = 0.0;
   out_1372883240507492868[244] = 0.0;
   out_1372883240507492868[245] = 0.0;
   out_1372883240507492868[246] = 0.0;
   out_1372883240507492868[247] = 1.0;
   out_1372883240507492868[248] = 0.0;
   out_1372883240507492868[249] = 0.0;
   out_1372883240507492868[250] = 0.0;
   out_1372883240507492868[251] = 0.0;
   out_1372883240507492868[252] = 0.0;
   out_1372883240507492868[253] = 0.0;
   out_1372883240507492868[254] = 0.0;
   out_1372883240507492868[255] = 0.0;
   out_1372883240507492868[256] = 0.0;
   out_1372883240507492868[257] = 0.0;
   out_1372883240507492868[258] = 0.0;
   out_1372883240507492868[259] = 0.0;
   out_1372883240507492868[260] = 0.0;
   out_1372883240507492868[261] = 0.0;
   out_1372883240507492868[262] = 0.0;
   out_1372883240507492868[263] = 0.0;
   out_1372883240507492868[264] = 0.0;
   out_1372883240507492868[265] = 0.0;
   out_1372883240507492868[266] = 1.0;
   out_1372883240507492868[267] = 0.0;
   out_1372883240507492868[268] = 0.0;
   out_1372883240507492868[269] = 0.0;
   out_1372883240507492868[270] = 0.0;
   out_1372883240507492868[271] = 0.0;
   out_1372883240507492868[272] = 0.0;
   out_1372883240507492868[273] = 0.0;
   out_1372883240507492868[274] = 0.0;
   out_1372883240507492868[275] = 0.0;
   out_1372883240507492868[276] = 0.0;
   out_1372883240507492868[277] = 0.0;
   out_1372883240507492868[278] = 0.0;
   out_1372883240507492868[279] = 0.0;
   out_1372883240507492868[280] = 0.0;
   out_1372883240507492868[281] = 0.0;
   out_1372883240507492868[282] = 0.0;
   out_1372883240507492868[283] = 0.0;
   out_1372883240507492868[284] = 0.0;
   out_1372883240507492868[285] = 1.0;
   out_1372883240507492868[286] = 0.0;
   out_1372883240507492868[287] = 0.0;
   out_1372883240507492868[288] = 0.0;
   out_1372883240507492868[289] = 0.0;
   out_1372883240507492868[290] = 0.0;
   out_1372883240507492868[291] = 0.0;
   out_1372883240507492868[292] = 0.0;
   out_1372883240507492868[293] = 0.0;
   out_1372883240507492868[294] = 0.0;
   out_1372883240507492868[295] = 0.0;
   out_1372883240507492868[296] = 0.0;
   out_1372883240507492868[297] = 0.0;
   out_1372883240507492868[298] = 0.0;
   out_1372883240507492868[299] = 0.0;
   out_1372883240507492868[300] = 0.0;
   out_1372883240507492868[301] = 0.0;
   out_1372883240507492868[302] = 0.0;
   out_1372883240507492868[303] = 0.0;
   out_1372883240507492868[304] = 1.0;
   out_1372883240507492868[305] = 0.0;
   out_1372883240507492868[306] = 0.0;
   out_1372883240507492868[307] = 0.0;
   out_1372883240507492868[308] = 0.0;
   out_1372883240507492868[309] = 0.0;
   out_1372883240507492868[310] = 0.0;
   out_1372883240507492868[311] = 0.0;
   out_1372883240507492868[312] = 0.0;
   out_1372883240507492868[313] = 0.0;
   out_1372883240507492868[314] = 0.0;
   out_1372883240507492868[315] = 0.0;
   out_1372883240507492868[316] = 0.0;
   out_1372883240507492868[317] = 0.0;
   out_1372883240507492868[318] = 0.0;
   out_1372883240507492868[319] = 0.0;
   out_1372883240507492868[320] = 0.0;
   out_1372883240507492868[321] = 0.0;
   out_1372883240507492868[322] = 0.0;
   out_1372883240507492868[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_8885506350385188796) {
   out_8885506350385188796[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_8885506350385188796[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_8885506350385188796[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_8885506350385188796[3] = dt*state[12] + state[3];
   out_8885506350385188796[4] = dt*state[13] + state[4];
   out_8885506350385188796[5] = dt*state[14] + state[5];
   out_8885506350385188796[6] = state[6];
   out_8885506350385188796[7] = state[7];
   out_8885506350385188796[8] = state[8];
   out_8885506350385188796[9] = state[9];
   out_8885506350385188796[10] = state[10];
   out_8885506350385188796[11] = state[11];
   out_8885506350385188796[12] = state[12];
   out_8885506350385188796[13] = state[13];
   out_8885506350385188796[14] = state[14];
   out_8885506350385188796[15] = state[15];
   out_8885506350385188796[16] = state[16];
   out_8885506350385188796[17] = state[17];
}
void F_fun(double *state, double dt, double *out_6694399137447510067) {
   out_6694399137447510067[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_6694399137447510067[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_6694399137447510067[2] = 0;
   out_6694399137447510067[3] = 0;
   out_6694399137447510067[4] = 0;
   out_6694399137447510067[5] = 0;
   out_6694399137447510067[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_6694399137447510067[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_6694399137447510067[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_6694399137447510067[9] = 0;
   out_6694399137447510067[10] = 0;
   out_6694399137447510067[11] = 0;
   out_6694399137447510067[12] = 0;
   out_6694399137447510067[13] = 0;
   out_6694399137447510067[14] = 0;
   out_6694399137447510067[15] = 0;
   out_6694399137447510067[16] = 0;
   out_6694399137447510067[17] = 0;
   out_6694399137447510067[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_6694399137447510067[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_6694399137447510067[20] = 0;
   out_6694399137447510067[21] = 0;
   out_6694399137447510067[22] = 0;
   out_6694399137447510067[23] = 0;
   out_6694399137447510067[24] = 0;
   out_6694399137447510067[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_6694399137447510067[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_6694399137447510067[27] = 0;
   out_6694399137447510067[28] = 0;
   out_6694399137447510067[29] = 0;
   out_6694399137447510067[30] = 0;
   out_6694399137447510067[31] = 0;
   out_6694399137447510067[32] = 0;
   out_6694399137447510067[33] = 0;
   out_6694399137447510067[34] = 0;
   out_6694399137447510067[35] = 0;
   out_6694399137447510067[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_6694399137447510067[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_6694399137447510067[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_6694399137447510067[39] = 0;
   out_6694399137447510067[40] = 0;
   out_6694399137447510067[41] = 0;
   out_6694399137447510067[42] = 0;
   out_6694399137447510067[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_6694399137447510067[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_6694399137447510067[45] = 0;
   out_6694399137447510067[46] = 0;
   out_6694399137447510067[47] = 0;
   out_6694399137447510067[48] = 0;
   out_6694399137447510067[49] = 0;
   out_6694399137447510067[50] = 0;
   out_6694399137447510067[51] = 0;
   out_6694399137447510067[52] = 0;
   out_6694399137447510067[53] = 0;
   out_6694399137447510067[54] = 0;
   out_6694399137447510067[55] = 0;
   out_6694399137447510067[56] = 0;
   out_6694399137447510067[57] = 1;
   out_6694399137447510067[58] = 0;
   out_6694399137447510067[59] = 0;
   out_6694399137447510067[60] = 0;
   out_6694399137447510067[61] = 0;
   out_6694399137447510067[62] = 0;
   out_6694399137447510067[63] = 0;
   out_6694399137447510067[64] = 0;
   out_6694399137447510067[65] = 0;
   out_6694399137447510067[66] = dt;
   out_6694399137447510067[67] = 0;
   out_6694399137447510067[68] = 0;
   out_6694399137447510067[69] = 0;
   out_6694399137447510067[70] = 0;
   out_6694399137447510067[71] = 0;
   out_6694399137447510067[72] = 0;
   out_6694399137447510067[73] = 0;
   out_6694399137447510067[74] = 0;
   out_6694399137447510067[75] = 0;
   out_6694399137447510067[76] = 1;
   out_6694399137447510067[77] = 0;
   out_6694399137447510067[78] = 0;
   out_6694399137447510067[79] = 0;
   out_6694399137447510067[80] = 0;
   out_6694399137447510067[81] = 0;
   out_6694399137447510067[82] = 0;
   out_6694399137447510067[83] = 0;
   out_6694399137447510067[84] = 0;
   out_6694399137447510067[85] = dt;
   out_6694399137447510067[86] = 0;
   out_6694399137447510067[87] = 0;
   out_6694399137447510067[88] = 0;
   out_6694399137447510067[89] = 0;
   out_6694399137447510067[90] = 0;
   out_6694399137447510067[91] = 0;
   out_6694399137447510067[92] = 0;
   out_6694399137447510067[93] = 0;
   out_6694399137447510067[94] = 0;
   out_6694399137447510067[95] = 1;
   out_6694399137447510067[96] = 0;
   out_6694399137447510067[97] = 0;
   out_6694399137447510067[98] = 0;
   out_6694399137447510067[99] = 0;
   out_6694399137447510067[100] = 0;
   out_6694399137447510067[101] = 0;
   out_6694399137447510067[102] = 0;
   out_6694399137447510067[103] = 0;
   out_6694399137447510067[104] = dt;
   out_6694399137447510067[105] = 0;
   out_6694399137447510067[106] = 0;
   out_6694399137447510067[107] = 0;
   out_6694399137447510067[108] = 0;
   out_6694399137447510067[109] = 0;
   out_6694399137447510067[110] = 0;
   out_6694399137447510067[111] = 0;
   out_6694399137447510067[112] = 0;
   out_6694399137447510067[113] = 0;
   out_6694399137447510067[114] = 1;
   out_6694399137447510067[115] = 0;
   out_6694399137447510067[116] = 0;
   out_6694399137447510067[117] = 0;
   out_6694399137447510067[118] = 0;
   out_6694399137447510067[119] = 0;
   out_6694399137447510067[120] = 0;
   out_6694399137447510067[121] = 0;
   out_6694399137447510067[122] = 0;
   out_6694399137447510067[123] = 0;
   out_6694399137447510067[124] = 0;
   out_6694399137447510067[125] = 0;
   out_6694399137447510067[126] = 0;
   out_6694399137447510067[127] = 0;
   out_6694399137447510067[128] = 0;
   out_6694399137447510067[129] = 0;
   out_6694399137447510067[130] = 0;
   out_6694399137447510067[131] = 0;
   out_6694399137447510067[132] = 0;
   out_6694399137447510067[133] = 1;
   out_6694399137447510067[134] = 0;
   out_6694399137447510067[135] = 0;
   out_6694399137447510067[136] = 0;
   out_6694399137447510067[137] = 0;
   out_6694399137447510067[138] = 0;
   out_6694399137447510067[139] = 0;
   out_6694399137447510067[140] = 0;
   out_6694399137447510067[141] = 0;
   out_6694399137447510067[142] = 0;
   out_6694399137447510067[143] = 0;
   out_6694399137447510067[144] = 0;
   out_6694399137447510067[145] = 0;
   out_6694399137447510067[146] = 0;
   out_6694399137447510067[147] = 0;
   out_6694399137447510067[148] = 0;
   out_6694399137447510067[149] = 0;
   out_6694399137447510067[150] = 0;
   out_6694399137447510067[151] = 0;
   out_6694399137447510067[152] = 1;
   out_6694399137447510067[153] = 0;
   out_6694399137447510067[154] = 0;
   out_6694399137447510067[155] = 0;
   out_6694399137447510067[156] = 0;
   out_6694399137447510067[157] = 0;
   out_6694399137447510067[158] = 0;
   out_6694399137447510067[159] = 0;
   out_6694399137447510067[160] = 0;
   out_6694399137447510067[161] = 0;
   out_6694399137447510067[162] = 0;
   out_6694399137447510067[163] = 0;
   out_6694399137447510067[164] = 0;
   out_6694399137447510067[165] = 0;
   out_6694399137447510067[166] = 0;
   out_6694399137447510067[167] = 0;
   out_6694399137447510067[168] = 0;
   out_6694399137447510067[169] = 0;
   out_6694399137447510067[170] = 0;
   out_6694399137447510067[171] = 1;
   out_6694399137447510067[172] = 0;
   out_6694399137447510067[173] = 0;
   out_6694399137447510067[174] = 0;
   out_6694399137447510067[175] = 0;
   out_6694399137447510067[176] = 0;
   out_6694399137447510067[177] = 0;
   out_6694399137447510067[178] = 0;
   out_6694399137447510067[179] = 0;
   out_6694399137447510067[180] = 0;
   out_6694399137447510067[181] = 0;
   out_6694399137447510067[182] = 0;
   out_6694399137447510067[183] = 0;
   out_6694399137447510067[184] = 0;
   out_6694399137447510067[185] = 0;
   out_6694399137447510067[186] = 0;
   out_6694399137447510067[187] = 0;
   out_6694399137447510067[188] = 0;
   out_6694399137447510067[189] = 0;
   out_6694399137447510067[190] = 1;
   out_6694399137447510067[191] = 0;
   out_6694399137447510067[192] = 0;
   out_6694399137447510067[193] = 0;
   out_6694399137447510067[194] = 0;
   out_6694399137447510067[195] = 0;
   out_6694399137447510067[196] = 0;
   out_6694399137447510067[197] = 0;
   out_6694399137447510067[198] = 0;
   out_6694399137447510067[199] = 0;
   out_6694399137447510067[200] = 0;
   out_6694399137447510067[201] = 0;
   out_6694399137447510067[202] = 0;
   out_6694399137447510067[203] = 0;
   out_6694399137447510067[204] = 0;
   out_6694399137447510067[205] = 0;
   out_6694399137447510067[206] = 0;
   out_6694399137447510067[207] = 0;
   out_6694399137447510067[208] = 0;
   out_6694399137447510067[209] = 1;
   out_6694399137447510067[210] = 0;
   out_6694399137447510067[211] = 0;
   out_6694399137447510067[212] = 0;
   out_6694399137447510067[213] = 0;
   out_6694399137447510067[214] = 0;
   out_6694399137447510067[215] = 0;
   out_6694399137447510067[216] = 0;
   out_6694399137447510067[217] = 0;
   out_6694399137447510067[218] = 0;
   out_6694399137447510067[219] = 0;
   out_6694399137447510067[220] = 0;
   out_6694399137447510067[221] = 0;
   out_6694399137447510067[222] = 0;
   out_6694399137447510067[223] = 0;
   out_6694399137447510067[224] = 0;
   out_6694399137447510067[225] = 0;
   out_6694399137447510067[226] = 0;
   out_6694399137447510067[227] = 0;
   out_6694399137447510067[228] = 1;
   out_6694399137447510067[229] = 0;
   out_6694399137447510067[230] = 0;
   out_6694399137447510067[231] = 0;
   out_6694399137447510067[232] = 0;
   out_6694399137447510067[233] = 0;
   out_6694399137447510067[234] = 0;
   out_6694399137447510067[235] = 0;
   out_6694399137447510067[236] = 0;
   out_6694399137447510067[237] = 0;
   out_6694399137447510067[238] = 0;
   out_6694399137447510067[239] = 0;
   out_6694399137447510067[240] = 0;
   out_6694399137447510067[241] = 0;
   out_6694399137447510067[242] = 0;
   out_6694399137447510067[243] = 0;
   out_6694399137447510067[244] = 0;
   out_6694399137447510067[245] = 0;
   out_6694399137447510067[246] = 0;
   out_6694399137447510067[247] = 1;
   out_6694399137447510067[248] = 0;
   out_6694399137447510067[249] = 0;
   out_6694399137447510067[250] = 0;
   out_6694399137447510067[251] = 0;
   out_6694399137447510067[252] = 0;
   out_6694399137447510067[253] = 0;
   out_6694399137447510067[254] = 0;
   out_6694399137447510067[255] = 0;
   out_6694399137447510067[256] = 0;
   out_6694399137447510067[257] = 0;
   out_6694399137447510067[258] = 0;
   out_6694399137447510067[259] = 0;
   out_6694399137447510067[260] = 0;
   out_6694399137447510067[261] = 0;
   out_6694399137447510067[262] = 0;
   out_6694399137447510067[263] = 0;
   out_6694399137447510067[264] = 0;
   out_6694399137447510067[265] = 0;
   out_6694399137447510067[266] = 1;
   out_6694399137447510067[267] = 0;
   out_6694399137447510067[268] = 0;
   out_6694399137447510067[269] = 0;
   out_6694399137447510067[270] = 0;
   out_6694399137447510067[271] = 0;
   out_6694399137447510067[272] = 0;
   out_6694399137447510067[273] = 0;
   out_6694399137447510067[274] = 0;
   out_6694399137447510067[275] = 0;
   out_6694399137447510067[276] = 0;
   out_6694399137447510067[277] = 0;
   out_6694399137447510067[278] = 0;
   out_6694399137447510067[279] = 0;
   out_6694399137447510067[280] = 0;
   out_6694399137447510067[281] = 0;
   out_6694399137447510067[282] = 0;
   out_6694399137447510067[283] = 0;
   out_6694399137447510067[284] = 0;
   out_6694399137447510067[285] = 1;
   out_6694399137447510067[286] = 0;
   out_6694399137447510067[287] = 0;
   out_6694399137447510067[288] = 0;
   out_6694399137447510067[289] = 0;
   out_6694399137447510067[290] = 0;
   out_6694399137447510067[291] = 0;
   out_6694399137447510067[292] = 0;
   out_6694399137447510067[293] = 0;
   out_6694399137447510067[294] = 0;
   out_6694399137447510067[295] = 0;
   out_6694399137447510067[296] = 0;
   out_6694399137447510067[297] = 0;
   out_6694399137447510067[298] = 0;
   out_6694399137447510067[299] = 0;
   out_6694399137447510067[300] = 0;
   out_6694399137447510067[301] = 0;
   out_6694399137447510067[302] = 0;
   out_6694399137447510067[303] = 0;
   out_6694399137447510067[304] = 1;
   out_6694399137447510067[305] = 0;
   out_6694399137447510067[306] = 0;
   out_6694399137447510067[307] = 0;
   out_6694399137447510067[308] = 0;
   out_6694399137447510067[309] = 0;
   out_6694399137447510067[310] = 0;
   out_6694399137447510067[311] = 0;
   out_6694399137447510067[312] = 0;
   out_6694399137447510067[313] = 0;
   out_6694399137447510067[314] = 0;
   out_6694399137447510067[315] = 0;
   out_6694399137447510067[316] = 0;
   out_6694399137447510067[317] = 0;
   out_6694399137447510067[318] = 0;
   out_6694399137447510067[319] = 0;
   out_6694399137447510067[320] = 0;
   out_6694399137447510067[321] = 0;
   out_6694399137447510067[322] = 0;
   out_6694399137447510067[323] = 1;
}
void h_4(double *state, double *unused, double *out_3136727019084366089) {
   out_3136727019084366089[0] = state[6] + state[9];
   out_3136727019084366089[1] = state[7] + state[10];
   out_3136727019084366089[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_6525401625546573603) {
   out_6525401625546573603[0] = 0;
   out_6525401625546573603[1] = 0;
   out_6525401625546573603[2] = 0;
   out_6525401625546573603[3] = 0;
   out_6525401625546573603[4] = 0;
   out_6525401625546573603[5] = 0;
   out_6525401625546573603[6] = 1;
   out_6525401625546573603[7] = 0;
   out_6525401625546573603[8] = 0;
   out_6525401625546573603[9] = 1;
   out_6525401625546573603[10] = 0;
   out_6525401625546573603[11] = 0;
   out_6525401625546573603[12] = 0;
   out_6525401625546573603[13] = 0;
   out_6525401625546573603[14] = 0;
   out_6525401625546573603[15] = 0;
   out_6525401625546573603[16] = 0;
   out_6525401625546573603[17] = 0;
   out_6525401625546573603[18] = 0;
   out_6525401625546573603[19] = 0;
   out_6525401625546573603[20] = 0;
   out_6525401625546573603[21] = 0;
   out_6525401625546573603[22] = 0;
   out_6525401625546573603[23] = 0;
   out_6525401625546573603[24] = 0;
   out_6525401625546573603[25] = 1;
   out_6525401625546573603[26] = 0;
   out_6525401625546573603[27] = 0;
   out_6525401625546573603[28] = 1;
   out_6525401625546573603[29] = 0;
   out_6525401625546573603[30] = 0;
   out_6525401625546573603[31] = 0;
   out_6525401625546573603[32] = 0;
   out_6525401625546573603[33] = 0;
   out_6525401625546573603[34] = 0;
   out_6525401625546573603[35] = 0;
   out_6525401625546573603[36] = 0;
   out_6525401625546573603[37] = 0;
   out_6525401625546573603[38] = 0;
   out_6525401625546573603[39] = 0;
   out_6525401625546573603[40] = 0;
   out_6525401625546573603[41] = 0;
   out_6525401625546573603[42] = 0;
   out_6525401625546573603[43] = 0;
   out_6525401625546573603[44] = 1;
   out_6525401625546573603[45] = 0;
   out_6525401625546573603[46] = 0;
   out_6525401625546573603[47] = 1;
   out_6525401625546573603[48] = 0;
   out_6525401625546573603[49] = 0;
   out_6525401625546573603[50] = 0;
   out_6525401625546573603[51] = 0;
   out_6525401625546573603[52] = 0;
   out_6525401625546573603[53] = 0;
}
void h_10(double *state, double *unused, double *out_198014718045503526) {
   out_198014718045503526[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_198014718045503526[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_198014718045503526[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_1683049892870523227) {
   out_1683049892870523227[0] = 0;
   out_1683049892870523227[1] = 9.8100000000000005*cos(state[1]);
   out_1683049892870523227[2] = 0;
   out_1683049892870523227[3] = 0;
   out_1683049892870523227[4] = -state[8];
   out_1683049892870523227[5] = state[7];
   out_1683049892870523227[6] = 0;
   out_1683049892870523227[7] = state[5];
   out_1683049892870523227[8] = -state[4];
   out_1683049892870523227[9] = 0;
   out_1683049892870523227[10] = 0;
   out_1683049892870523227[11] = 0;
   out_1683049892870523227[12] = 1;
   out_1683049892870523227[13] = 0;
   out_1683049892870523227[14] = 0;
   out_1683049892870523227[15] = 1;
   out_1683049892870523227[16] = 0;
   out_1683049892870523227[17] = 0;
   out_1683049892870523227[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_1683049892870523227[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_1683049892870523227[20] = 0;
   out_1683049892870523227[21] = state[8];
   out_1683049892870523227[22] = 0;
   out_1683049892870523227[23] = -state[6];
   out_1683049892870523227[24] = -state[5];
   out_1683049892870523227[25] = 0;
   out_1683049892870523227[26] = state[3];
   out_1683049892870523227[27] = 0;
   out_1683049892870523227[28] = 0;
   out_1683049892870523227[29] = 0;
   out_1683049892870523227[30] = 0;
   out_1683049892870523227[31] = 1;
   out_1683049892870523227[32] = 0;
   out_1683049892870523227[33] = 0;
   out_1683049892870523227[34] = 1;
   out_1683049892870523227[35] = 0;
   out_1683049892870523227[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_1683049892870523227[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_1683049892870523227[38] = 0;
   out_1683049892870523227[39] = -state[7];
   out_1683049892870523227[40] = state[6];
   out_1683049892870523227[41] = 0;
   out_1683049892870523227[42] = state[4];
   out_1683049892870523227[43] = -state[3];
   out_1683049892870523227[44] = 0;
   out_1683049892870523227[45] = 0;
   out_1683049892870523227[46] = 0;
   out_1683049892870523227[47] = 0;
   out_1683049892870523227[48] = 0;
   out_1683049892870523227[49] = 0;
   out_1683049892870523227[50] = 1;
   out_1683049892870523227[51] = 0;
   out_1683049892870523227[52] = 0;
   out_1683049892870523227[53] = 1;
}
void h_13(double *state, double *unused, double *out_7309627388739009073) {
   out_7309627388739009073[0] = state[3];
   out_7309627388739009073[1] = state[4];
   out_7309627388739009073[2] = state[5];
}
void H_13(double *state, double *unused, double *out_8709068622830645212) {
   out_8709068622830645212[0] = 0;
   out_8709068622830645212[1] = 0;
   out_8709068622830645212[2] = 0;
   out_8709068622830645212[3] = 1;
   out_8709068622830645212[4] = 0;
   out_8709068622830645212[5] = 0;
   out_8709068622830645212[6] = 0;
   out_8709068622830645212[7] = 0;
   out_8709068622830645212[8] = 0;
   out_8709068622830645212[9] = 0;
   out_8709068622830645212[10] = 0;
   out_8709068622830645212[11] = 0;
   out_8709068622830645212[12] = 0;
   out_8709068622830645212[13] = 0;
   out_8709068622830645212[14] = 0;
   out_8709068622830645212[15] = 0;
   out_8709068622830645212[16] = 0;
   out_8709068622830645212[17] = 0;
   out_8709068622830645212[18] = 0;
   out_8709068622830645212[19] = 0;
   out_8709068622830645212[20] = 0;
   out_8709068622830645212[21] = 0;
   out_8709068622830645212[22] = 1;
   out_8709068622830645212[23] = 0;
   out_8709068622830645212[24] = 0;
   out_8709068622830645212[25] = 0;
   out_8709068622830645212[26] = 0;
   out_8709068622830645212[27] = 0;
   out_8709068622830645212[28] = 0;
   out_8709068622830645212[29] = 0;
   out_8709068622830645212[30] = 0;
   out_8709068622830645212[31] = 0;
   out_8709068622830645212[32] = 0;
   out_8709068622830645212[33] = 0;
   out_8709068622830645212[34] = 0;
   out_8709068622830645212[35] = 0;
   out_8709068622830645212[36] = 0;
   out_8709068622830645212[37] = 0;
   out_8709068622830645212[38] = 0;
   out_8709068622830645212[39] = 0;
   out_8709068622830645212[40] = 0;
   out_8709068622830645212[41] = 1;
   out_8709068622830645212[42] = 0;
   out_8709068622830645212[43] = 0;
   out_8709068622830645212[44] = 0;
   out_8709068622830645212[45] = 0;
   out_8709068622830645212[46] = 0;
   out_8709068622830645212[47] = 0;
   out_8709068622830645212[48] = 0;
   out_8709068622830645212[49] = 0;
   out_8709068622830645212[50] = 0;
   out_8709068622830645212[51] = 0;
   out_8709068622830645212[52] = 0;
   out_8709068622830645212[53] = 0;
}
void h_14(double *state, double *unused, double *out_6553607367466278032) {
   out_6553607367466278032[0] = state[6];
   out_6553607367466278032[1] = state[7];
   out_6553607367466278032[2] = state[8];
}
void H_14(double *state, double *unused, double *out_7958101591823493484) {
   out_7958101591823493484[0] = 0;
   out_7958101591823493484[1] = 0;
   out_7958101591823493484[2] = 0;
   out_7958101591823493484[3] = 0;
   out_7958101591823493484[4] = 0;
   out_7958101591823493484[5] = 0;
   out_7958101591823493484[6] = 1;
   out_7958101591823493484[7] = 0;
   out_7958101591823493484[8] = 0;
   out_7958101591823493484[9] = 0;
   out_7958101591823493484[10] = 0;
   out_7958101591823493484[11] = 0;
   out_7958101591823493484[12] = 0;
   out_7958101591823493484[13] = 0;
   out_7958101591823493484[14] = 0;
   out_7958101591823493484[15] = 0;
   out_7958101591823493484[16] = 0;
   out_7958101591823493484[17] = 0;
   out_7958101591823493484[18] = 0;
   out_7958101591823493484[19] = 0;
   out_7958101591823493484[20] = 0;
   out_7958101591823493484[21] = 0;
   out_7958101591823493484[22] = 0;
   out_7958101591823493484[23] = 0;
   out_7958101591823493484[24] = 0;
   out_7958101591823493484[25] = 1;
   out_7958101591823493484[26] = 0;
   out_7958101591823493484[27] = 0;
   out_7958101591823493484[28] = 0;
   out_7958101591823493484[29] = 0;
   out_7958101591823493484[30] = 0;
   out_7958101591823493484[31] = 0;
   out_7958101591823493484[32] = 0;
   out_7958101591823493484[33] = 0;
   out_7958101591823493484[34] = 0;
   out_7958101591823493484[35] = 0;
   out_7958101591823493484[36] = 0;
   out_7958101591823493484[37] = 0;
   out_7958101591823493484[38] = 0;
   out_7958101591823493484[39] = 0;
   out_7958101591823493484[40] = 0;
   out_7958101591823493484[41] = 0;
   out_7958101591823493484[42] = 0;
   out_7958101591823493484[43] = 0;
   out_7958101591823493484[44] = 1;
   out_7958101591823493484[45] = 0;
   out_7958101591823493484[46] = 0;
   out_7958101591823493484[47] = 0;
   out_7958101591823493484[48] = 0;
   out_7958101591823493484[49] = 0;
   out_7958101591823493484[50] = 0;
   out_7958101591823493484[51] = 0;
   out_7958101591823493484[52] = 0;
   out_7958101591823493484[53] = 0;
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
void pose_err_fun(double *nom_x, double *delta_x, double *out_9115622508544891145) {
  err_fun(nom_x, delta_x, out_9115622508544891145);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_112942660134600720) {
  inv_err_fun(nom_x, true_x, out_112942660134600720);
}
void pose_H_mod_fun(double *state, double *out_1372883240507492868) {
  H_mod_fun(state, out_1372883240507492868);
}
void pose_f_fun(double *state, double dt, double *out_8885506350385188796) {
  f_fun(state,  dt, out_8885506350385188796);
}
void pose_F_fun(double *state, double dt, double *out_6694399137447510067) {
  F_fun(state,  dt, out_6694399137447510067);
}
void pose_h_4(double *state, double *unused, double *out_3136727019084366089) {
  h_4(state, unused, out_3136727019084366089);
}
void pose_H_4(double *state, double *unused, double *out_6525401625546573603) {
  H_4(state, unused, out_6525401625546573603);
}
void pose_h_10(double *state, double *unused, double *out_198014718045503526) {
  h_10(state, unused, out_198014718045503526);
}
void pose_H_10(double *state, double *unused, double *out_1683049892870523227) {
  H_10(state, unused, out_1683049892870523227);
}
void pose_h_13(double *state, double *unused, double *out_7309627388739009073) {
  h_13(state, unused, out_7309627388739009073);
}
void pose_H_13(double *state, double *unused, double *out_8709068622830645212) {
  H_13(state, unused, out_8709068622830645212);
}
void pose_h_14(double *state, double *unused, double *out_6553607367466278032) {
  h_14(state, unused, out_6553607367466278032);
}
void pose_H_14(double *state, double *unused, double *out_7958101591823493484) {
  H_14(state, unused, out_7958101591823493484);
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
