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
void err_fun(double *nom_x, double *delta_x, double *out_7318184160914923263) {
   out_7318184160914923263[0] = delta_x[0] + nom_x[0];
   out_7318184160914923263[1] = delta_x[1] + nom_x[1];
   out_7318184160914923263[2] = delta_x[2] + nom_x[2];
   out_7318184160914923263[3] = delta_x[3] + nom_x[3];
   out_7318184160914923263[4] = delta_x[4] + nom_x[4];
   out_7318184160914923263[5] = delta_x[5] + nom_x[5];
   out_7318184160914923263[6] = delta_x[6] + nom_x[6];
   out_7318184160914923263[7] = delta_x[7] + nom_x[7];
   out_7318184160914923263[8] = delta_x[8] + nom_x[8];
   out_7318184160914923263[9] = delta_x[9] + nom_x[9];
   out_7318184160914923263[10] = delta_x[10] + nom_x[10];
   out_7318184160914923263[11] = delta_x[11] + nom_x[11];
   out_7318184160914923263[12] = delta_x[12] + nom_x[12];
   out_7318184160914923263[13] = delta_x[13] + nom_x[13];
   out_7318184160914923263[14] = delta_x[14] + nom_x[14];
   out_7318184160914923263[15] = delta_x[15] + nom_x[15];
   out_7318184160914923263[16] = delta_x[16] + nom_x[16];
   out_7318184160914923263[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_8130026506067701099) {
   out_8130026506067701099[0] = -nom_x[0] + true_x[0];
   out_8130026506067701099[1] = -nom_x[1] + true_x[1];
   out_8130026506067701099[2] = -nom_x[2] + true_x[2];
   out_8130026506067701099[3] = -nom_x[3] + true_x[3];
   out_8130026506067701099[4] = -nom_x[4] + true_x[4];
   out_8130026506067701099[5] = -nom_x[5] + true_x[5];
   out_8130026506067701099[6] = -nom_x[6] + true_x[6];
   out_8130026506067701099[7] = -nom_x[7] + true_x[7];
   out_8130026506067701099[8] = -nom_x[8] + true_x[8];
   out_8130026506067701099[9] = -nom_x[9] + true_x[9];
   out_8130026506067701099[10] = -nom_x[10] + true_x[10];
   out_8130026506067701099[11] = -nom_x[11] + true_x[11];
   out_8130026506067701099[12] = -nom_x[12] + true_x[12];
   out_8130026506067701099[13] = -nom_x[13] + true_x[13];
   out_8130026506067701099[14] = -nom_x[14] + true_x[14];
   out_8130026506067701099[15] = -nom_x[15] + true_x[15];
   out_8130026506067701099[16] = -nom_x[16] + true_x[16];
   out_8130026506067701099[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_5907612673153772883) {
   out_5907612673153772883[0] = 1.0;
   out_5907612673153772883[1] = 0.0;
   out_5907612673153772883[2] = 0.0;
   out_5907612673153772883[3] = 0.0;
   out_5907612673153772883[4] = 0.0;
   out_5907612673153772883[5] = 0.0;
   out_5907612673153772883[6] = 0.0;
   out_5907612673153772883[7] = 0.0;
   out_5907612673153772883[8] = 0.0;
   out_5907612673153772883[9] = 0.0;
   out_5907612673153772883[10] = 0.0;
   out_5907612673153772883[11] = 0.0;
   out_5907612673153772883[12] = 0.0;
   out_5907612673153772883[13] = 0.0;
   out_5907612673153772883[14] = 0.0;
   out_5907612673153772883[15] = 0.0;
   out_5907612673153772883[16] = 0.0;
   out_5907612673153772883[17] = 0.0;
   out_5907612673153772883[18] = 0.0;
   out_5907612673153772883[19] = 1.0;
   out_5907612673153772883[20] = 0.0;
   out_5907612673153772883[21] = 0.0;
   out_5907612673153772883[22] = 0.0;
   out_5907612673153772883[23] = 0.0;
   out_5907612673153772883[24] = 0.0;
   out_5907612673153772883[25] = 0.0;
   out_5907612673153772883[26] = 0.0;
   out_5907612673153772883[27] = 0.0;
   out_5907612673153772883[28] = 0.0;
   out_5907612673153772883[29] = 0.0;
   out_5907612673153772883[30] = 0.0;
   out_5907612673153772883[31] = 0.0;
   out_5907612673153772883[32] = 0.0;
   out_5907612673153772883[33] = 0.0;
   out_5907612673153772883[34] = 0.0;
   out_5907612673153772883[35] = 0.0;
   out_5907612673153772883[36] = 0.0;
   out_5907612673153772883[37] = 0.0;
   out_5907612673153772883[38] = 1.0;
   out_5907612673153772883[39] = 0.0;
   out_5907612673153772883[40] = 0.0;
   out_5907612673153772883[41] = 0.0;
   out_5907612673153772883[42] = 0.0;
   out_5907612673153772883[43] = 0.0;
   out_5907612673153772883[44] = 0.0;
   out_5907612673153772883[45] = 0.0;
   out_5907612673153772883[46] = 0.0;
   out_5907612673153772883[47] = 0.0;
   out_5907612673153772883[48] = 0.0;
   out_5907612673153772883[49] = 0.0;
   out_5907612673153772883[50] = 0.0;
   out_5907612673153772883[51] = 0.0;
   out_5907612673153772883[52] = 0.0;
   out_5907612673153772883[53] = 0.0;
   out_5907612673153772883[54] = 0.0;
   out_5907612673153772883[55] = 0.0;
   out_5907612673153772883[56] = 0.0;
   out_5907612673153772883[57] = 1.0;
   out_5907612673153772883[58] = 0.0;
   out_5907612673153772883[59] = 0.0;
   out_5907612673153772883[60] = 0.0;
   out_5907612673153772883[61] = 0.0;
   out_5907612673153772883[62] = 0.0;
   out_5907612673153772883[63] = 0.0;
   out_5907612673153772883[64] = 0.0;
   out_5907612673153772883[65] = 0.0;
   out_5907612673153772883[66] = 0.0;
   out_5907612673153772883[67] = 0.0;
   out_5907612673153772883[68] = 0.0;
   out_5907612673153772883[69] = 0.0;
   out_5907612673153772883[70] = 0.0;
   out_5907612673153772883[71] = 0.0;
   out_5907612673153772883[72] = 0.0;
   out_5907612673153772883[73] = 0.0;
   out_5907612673153772883[74] = 0.0;
   out_5907612673153772883[75] = 0.0;
   out_5907612673153772883[76] = 1.0;
   out_5907612673153772883[77] = 0.0;
   out_5907612673153772883[78] = 0.0;
   out_5907612673153772883[79] = 0.0;
   out_5907612673153772883[80] = 0.0;
   out_5907612673153772883[81] = 0.0;
   out_5907612673153772883[82] = 0.0;
   out_5907612673153772883[83] = 0.0;
   out_5907612673153772883[84] = 0.0;
   out_5907612673153772883[85] = 0.0;
   out_5907612673153772883[86] = 0.0;
   out_5907612673153772883[87] = 0.0;
   out_5907612673153772883[88] = 0.0;
   out_5907612673153772883[89] = 0.0;
   out_5907612673153772883[90] = 0.0;
   out_5907612673153772883[91] = 0.0;
   out_5907612673153772883[92] = 0.0;
   out_5907612673153772883[93] = 0.0;
   out_5907612673153772883[94] = 0.0;
   out_5907612673153772883[95] = 1.0;
   out_5907612673153772883[96] = 0.0;
   out_5907612673153772883[97] = 0.0;
   out_5907612673153772883[98] = 0.0;
   out_5907612673153772883[99] = 0.0;
   out_5907612673153772883[100] = 0.0;
   out_5907612673153772883[101] = 0.0;
   out_5907612673153772883[102] = 0.0;
   out_5907612673153772883[103] = 0.0;
   out_5907612673153772883[104] = 0.0;
   out_5907612673153772883[105] = 0.0;
   out_5907612673153772883[106] = 0.0;
   out_5907612673153772883[107] = 0.0;
   out_5907612673153772883[108] = 0.0;
   out_5907612673153772883[109] = 0.0;
   out_5907612673153772883[110] = 0.0;
   out_5907612673153772883[111] = 0.0;
   out_5907612673153772883[112] = 0.0;
   out_5907612673153772883[113] = 0.0;
   out_5907612673153772883[114] = 1.0;
   out_5907612673153772883[115] = 0.0;
   out_5907612673153772883[116] = 0.0;
   out_5907612673153772883[117] = 0.0;
   out_5907612673153772883[118] = 0.0;
   out_5907612673153772883[119] = 0.0;
   out_5907612673153772883[120] = 0.0;
   out_5907612673153772883[121] = 0.0;
   out_5907612673153772883[122] = 0.0;
   out_5907612673153772883[123] = 0.0;
   out_5907612673153772883[124] = 0.0;
   out_5907612673153772883[125] = 0.0;
   out_5907612673153772883[126] = 0.0;
   out_5907612673153772883[127] = 0.0;
   out_5907612673153772883[128] = 0.0;
   out_5907612673153772883[129] = 0.0;
   out_5907612673153772883[130] = 0.0;
   out_5907612673153772883[131] = 0.0;
   out_5907612673153772883[132] = 0.0;
   out_5907612673153772883[133] = 1.0;
   out_5907612673153772883[134] = 0.0;
   out_5907612673153772883[135] = 0.0;
   out_5907612673153772883[136] = 0.0;
   out_5907612673153772883[137] = 0.0;
   out_5907612673153772883[138] = 0.0;
   out_5907612673153772883[139] = 0.0;
   out_5907612673153772883[140] = 0.0;
   out_5907612673153772883[141] = 0.0;
   out_5907612673153772883[142] = 0.0;
   out_5907612673153772883[143] = 0.0;
   out_5907612673153772883[144] = 0.0;
   out_5907612673153772883[145] = 0.0;
   out_5907612673153772883[146] = 0.0;
   out_5907612673153772883[147] = 0.0;
   out_5907612673153772883[148] = 0.0;
   out_5907612673153772883[149] = 0.0;
   out_5907612673153772883[150] = 0.0;
   out_5907612673153772883[151] = 0.0;
   out_5907612673153772883[152] = 1.0;
   out_5907612673153772883[153] = 0.0;
   out_5907612673153772883[154] = 0.0;
   out_5907612673153772883[155] = 0.0;
   out_5907612673153772883[156] = 0.0;
   out_5907612673153772883[157] = 0.0;
   out_5907612673153772883[158] = 0.0;
   out_5907612673153772883[159] = 0.0;
   out_5907612673153772883[160] = 0.0;
   out_5907612673153772883[161] = 0.0;
   out_5907612673153772883[162] = 0.0;
   out_5907612673153772883[163] = 0.0;
   out_5907612673153772883[164] = 0.0;
   out_5907612673153772883[165] = 0.0;
   out_5907612673153772883[166] = 0.0;
   out_5907612673153772883[167] = 0.0;
   out_5907612673153772883[168] = 0.0;
   out_5907612673153772883[169] = 0.0;
   out_5907612673153772883[170] = 0.0;
   out_5907612673153772883[171] = 1.0;
   out_5907612673153772883[172] = 0.0;
   out_5907612673153772883[173] = 0.0;
   out_5907612673153772883[174] = 0.0;
   out_5907612673153772883[175] = 0.0;
   out_5907612673153772883[176] = 0.0;
   out_5907612673153772883[177] = 0.0;
   out_5907612673153772883[178] = 0.0;
   out_5907612673153772883[179] = 0.0;
   out_5907612673153772883[180] = 0.0;
   out_5907612673153772883[181] = 0.0;
   out_5907612673153772883[182] = 0.0;
   out_5907612673153772883[183] = 0.0;
   out_5907612673153772883[184] = 0.0;
   out_5907612673153772883[185] = 0.0;
   out_5907612673153772883[186] = 0.0;
   out_5907612673153772883[187] = 0.0;
   out_5907612673153772883[188] = 0.0;
   out_5907612673153772883[189] = 0.0;
   out_5907612673153772883[190] = 1.0;
   out_5907612673153772883[191] = 0.0;
   out_5907612673153772883[192] = 0.0;
   out_5907612673153772883[193] = 0.0;
   out_5907612673153772883[194] = 0.0;
   out_5907612673153772883[195] = 0.0;
   out_5907612673153772883[196] = 0.0;
   out_5907612673153772883[197] = 0.0;
   out_5907612673153772883[198] = 0.0;
   out_5907612673153772883[199] = 0.0;
   out_5907612673153772883[200] = 0.0;
   out_5907612673153772883[201] = 0.0;
   out_5907612673153772883[202] = 0.0;
   out_5907612673153772883[203] = 0.0;
   out_5907612673153772883[204] = 0.0;
   out_5907612673153772883[205] = 0.0;
   out_5907612673153772883[206] = 0.0;
   out_5907612673153772883[207] = 0.0;
   out_5907612673153772883[208] = 0.0;
   out_5907612673153772883[209] = 1.0;
   out_5907612673153772883[210] = 0.0;
   out_5907612673153772883[211] = 0.0;
   out_5907612673153772883[212] = 0.0;
   out_5907612673153772883[213] = 0.0;
   out_5907612673153772883[214] = 0.0;
   out_5907612673153772883[215] = 0.0;
   out_5907612673153772883[216] = 0.0;
   out_5907612673153772883[217] = 0.0;
   out_5907612673153772883[218] = 0.0;
   out_5907612673153772883[219] = 0.0;
   out_5907612673153772883[220] = 0.0;
   out_5907612673153772883[221] = 0.0;
   out_5907612673153772883[222] = 0.0;
   out_5907612673153772883[223] = 0.0;
   out_5907612673153772883[224] = 0.0;
   out_5907612673153772883[225] = 0.0;
   out_5907612673153772883[226] = 0.0;
   out_5907612673153772883[227] = 0.0;
   out_5907612673153772883[228] = 1.0;
   out_5907612673153772883[229] = 0.0;
   out_5907612673153772883[230] = 0.0;
   out_5907612673153772883[231] = 0.0;
   out_5907612673153772883[232] = 0.0;
   out_5907612673153772883[233] = 0.0;
   out_5907612673153772883[234] = 0.0;
   out_5907612673153772883[235] = 0.0;
   out_5907612673153772883[236] = 0.0;
   out_5907612673153772883[237] = 0.0;
   out_5907612673153772883[238] = 0.0;
   out_5907612673153772883[239] = 0.0;
   out_5907612673153772883[240] = 0.0;
   out_5907612673153772883[241] = 0.0;
   out_5907612673153772883[242] = 0.0;
   out_5907612673153772883[243] = 0.0;
   out_5907612673153772883[244] = 0.0;
   out_5907612673153772883[245] = 0.0;
   out_5907612673153772883[246] = 0.0;
   out_5907612673153772883[247] = 1.0;
   out_5907612673153772883[248] = 0.0;
   out_5907612673153772883[249] = 0.0;
   out_5907612673153772883[250] = 0.0;
   out_5907612673153772883[251] = 0.0;
   out_5907612673153772883[252] = 0.0;
   out_5907612673153772883[253] = 0.0;
   out_5907612673153772883[254] = 0.0;
   out_5907612673153772883[255] = 0.0;
   out_5907612673153772883[256] = 0.0;
   out_5907612673153772883[257] = 0.0;
   out_5907612673153772883[258] = 0.0;
   out_5907612673153772883[259] = 0.0;
   out_5907612673153772883[260] = 0.0;
   out_5907612673153772883[261] = 0.0;
   out_5907612673153772883[262] = 0.0;
   out_5907612673153772883[263] = 0.0;
   out_5907612673153772883[264] = 0.0;
   out_5907612673153772883[265] = 0.0;
   out_5907612673153772883[266] = 1.0;
   out_5907612673153772883[267] = 0.0;
   out_5907612673153772883[268] = 0.0;
   out_5907612673153772883[269] = 0.0;
   out_5907612673153772883[270] = 0.0;
   out_5907612673153772883[271] = 0.0;
   out_5907612673153772883[272] = 0.0;
   out_5907612673153772883[273] = 0.0;
   out_5907612673153772883[274] = 0.0;
   out_5907612673153772883[275] = 0.0;
   out_5907612673153772883[276] = 0.0;
   out_5907612673153772883[277] = 0.0;
   out_5907612673153772883[278] = 0.0;
   out_5907612673153772883[279] = 0.0;
   out_5907612673153772883[280] = 0.0;
   out_5907612673153772883[281] = 0.0;
   out_5907612673153772883[282] = 0.0;
   out_5907612673153772883[283] = 0.0;
   out_5907612673153772883[284] = 0.0;
   out_5907612673153772883[285] = 1.0;
   out_5907612673153772883[286] = 0.0;
   out_5907612673153772883[287] = 0.0;
   out_5907612673153772883[288] = 0.0;
   out_5907612673153772883[289] = 0.0;
   out_5907612673153772883[290] = 0.0;
   out_5907612673153772883[291] = 0.0;
   out_5907612673153772883[292] = 0.0;
   out_5907612673153772883[293] = 0.0;
   out_5907612673153772883[294] = 0.0;
   out_5907612673153772883[295] = 0.0;
   out_5907612673153772883[296] = 0.0;
   out_5907612673153772883[297] = 0.0;
   out_5907612673153772883[298] = 0.0;
   out_5907612673153772883[299] = 0.0;
   out_5907612673153772883[300] = 0.0;
   out_5907612673153772883[301] = 0.0;
   out_5907612673153772883[302] = 0.0;
   out_5907612673153772883[303] = 0.0;
   out_5907612673153772883[304] = 1.0;
   out_5907612673153772883[305] = 0.0;
   out_5907612673153772883[306] = 0.0;
   out_5907612673153772883[307] = 0.0;
   out_5907612673153772883[308] = 0.0;
   out_5907612673153772883[309] = 0.0;
   out_5907612673153772883[310] = 0.0;
   out_5907612673153772883[311] = 0.0;
   out_5907612673153772883[312] = 0.0;
   out_5907612673153772883[313] = 0.0;
   out_5907612673153772883[314] = 0.0;
   out_5907612673153772883[315] = 0.0;
   out_5907612673153772883[316] = 0.0;
   out_5907612673153772883[317] = 0.0;
   out_5907612673153772883[318] = 0.0;
   out_5907612673153772883[319] = 0.0;
   out_5907612673153772883[320] = 0.0;
   out_5907612673153772883[321] = 0.0;
   out_5907612673153772883[322] = 0.0;
   out_5907612673153772883[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_4351928450748542819) {
   out_4351928450748542819[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_4351928450748542819[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_4351928450748542819[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_4351928450748542819[3] = dt*state[12] + state[3];
   out_4351928450748542819[4] = dt*state[13] + state[4];
   out_4351928450748542819[5] = dt*state[14] + state[5];
   out_4351928450748542819[6] = state[6];
   out_4351928450748542819[7] = state[7];
   out_4351928450748542819[8] = state[8];
   out_4351928450748542819[9] = state[9];
   out_4351928450748542819[10] = state[10];
   out_4351928450748542819[11] = state[11];
   out_4351928450748542819[12] = state[12];
   out_4351928450748542819[13] = state[13];
   out_4351928450748542819[14] = state[14];
   out_4351928450748542819[15] = state[15];
   out_4351928450748542819[16] = state[16];
   out_4351928450748542819[17] = state[17];
}
void F_fun(double *state, double dt, double *out_1555904624671315142) {
   out_1555904624671315142[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_1555904624671315142[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_1555904624671315142[2] = 0;
   out_1555904624671315142[3] = 0;
   out_1555904624671315142[4] = 0;
   out_1555904624671315142[5] = 0;
   out_1555904624671315142[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_1555904624671315142[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_1555904624671315142[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_1555904624671315142[9] = 0;
   out_1555904624671315142[10] = 0;
   out_1555904624671315142[11] = 0;
   out_1555904624671315142[12] = 0;
   out_1555904624671315142[13] = 0;
   out_1555904624671315142[14] = 0;
   out_1555904624671315142[15] = 0;
   out_1555904624671315142[16] = 0;
   out_1555904624671315142[17] = 0;
   out_1555904624671315142[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_1555904624671315142[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_1555904624671315142[20] = 0;
   out_1555904624671315142[21] = 0;
   out_1555904624671315142[22] = 0;
   out_1555904624671315142[23] = 0;
   out_1555904624671315142[24] = 0;
   out_1555904624671315142[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_1555904624671315142[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_1555904624671315142[27] = 0;
   out_1555904624671315142[28] = 0;
   out_1555904624671315142[29] = 0;
   out_1555904624671315142[30] = 0;
   out_1555904624671315142[31] = 0;
   out_1555904624671315142[32] = 0;
   out_1555904624671315142[33] = 0;
   out_1555904624671315142[34] = 0;
   out_1555904624671315142[35] = 0;
   out_1555904624671315142[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_1555904624671315142[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_1555904624671315142[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_1555904624671315142[39] = 0;
   out_1555904624671315142[40] = 0;
   out_1555904624671315142[41] = 0;
   out_1555904624671315142[42] = 0;
   out_1555904624671315142[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_1555904624671315142[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_1555904624671315142[45] = 0;
   out_1555904624671315142[46] = 0;
   out_1555904624671315142[47] = 0;
   out_1555904624671315142[48] = 0;
   out_1555904624671315142[49] = 0;
   out_1555904624671315142[50] = 0;
   out_1555904624671315142[51] = 0;
   out_1555904624671315142[52] = 0;
   out_1555904624671315142[53] = 0;
   out_1555904624671315142[54] = 0;
   out_1555904624671315142[55] = 0;
   out_1555904624671315142[56] = 0;
   out_1555904624671315142[57] = 1;
   out_1555904624671315142[58] = 0;
   out_1555904624671315142[59] = 0;
   out_1555904624671315142[60] = 0;
   out_1555904624671315142[61] = 0;
   out_1555904624671315142[62] = 0;
   out_1555904624671315142[63] = 0;
   out_1555904624671315142[64] = 0;
   out_1555904624671315142[65] = 0;
   out_1555904624671315142[66] = dt;
   out_1555904624671315142[67] = 0;
   out_1555904624671315142[68] = 0;
   out_1555904624671315142[69] = 0;
   out_1555904624671315142[70] = 0;
   out_1555904624671315142[71] = 0;
   out_1555904624671315142[72] = 0;
   out_1555904624671315142[73] = 0;
   out_1555904624671315142[74] = 0;
   out_1555904624671315142[75] = 0;
   out_1555904624671315142[76] = 1;
   out_1555904624671315142[77] = 0;
   out_1555904624671315142[78] = 0;
   out_1555904624671315142[79] = 0;
   out_1555904624671315142[80] = 0;
   out_1555904624671315142[81] = 0;
   out_1555904624671315142[82] = 0;
   out_1555904624671315142[83] = 0;
   out_1555904624671315142[84] = 0;
   out_1555904624671315142[85] = dt;
   out_1555904624671315142[86] = 0;
   out_1555904624671315142[87] = 0;
   out_1555904624671315142[88] = 0;
   out_1555904624671315142[89] = 0;
   out_1555904624671315142[90] = 0;
   out_1555904624671315142[91] = 0;
   out_1555904624671315142[92] = 0;
   out_1555904624671315142[93] = 0;
   out_1555904624671315142[94] = 0;
   out_1555904624671315142[95] = 1;
   out_1555904624671315142[96] = 0;
   out_1555904624671315142[97] = 0;
   out_1555904624671315142[98] = 0;
   out_1555904624671315142[99] = 0;
   out_1555904624671315142[100] = 0;
   out_1555904624671315142[101] = 0;
   out_1555904624671315142[102] = 0;
   out_1555904624671315142[103] = 0;
   out_1555904624671315142[104] = dt;
   out_1555904624671315142[105] = 0;
   out_1555904624671315142[106] = 0;
   out_1555904624671315142[107] = 0;
   out_1555904624671315142[108] = 0;
   out_1555904624671315142[109] = 0;
   out_1555904624671315142[110] = 0;
   out_1555904624671315142[111] = 0;
   out_1555904624671315142[112] = 0;
   out_1555904624671315142[113] = 0;
   out_1555904624671315142[114] = 1;
   out_1555904624671315142[115] = 0;
   out_1555904624671315142[116] = 0;
   out_1555904624671315142[117] = 0;
   out_1555904624671315142[118] = 0;
   out_1555904624671315142[119] = 0;
   out_1555904624671315142[120] = 0;
   out_1555904624671315142[121] = 0;
   out_1555904624671315142[122] = 0;
   out_1555904624671315142[123] = 0;
   out_1555904624671315142[124] = 0;
   out_1555904624671315142[125] = 0;
   out_1555904624671315142[126] = 0;
   out_1555904624671315142[127] = 0;
   out_1555904624671315142[128] = 0;
   out_1555904624671315142[129] = 0;
   out_1555904624671315142[130] = 0;
   out_1555904624671315142[131] = 0;
   out_1555904624671315142[132] = 0;
   out_1555904624671315142[133] = 1;
   out_1555904624671315142[134] = 0;
   out_1555904624671315142[135] = 0;
   out_1555904624671315142[136] = 0;
   out_1555904624671315142[137] = 0;
   out_1555904624671315142[138] = 0;
   out_1555904624671315142[139] = 0;
   out_1555904624671315142[140] = 0;
   out_1555904624671315142[141] = 0;
   out_1555904624671315142[142] = 0;
   out_1555904624671315142[143] = 0;
   out_1555904624671315142[144] = 0;
   out_1555904624671315142[145] = 0;
   out_1555904624671315142[146] = 0;
   out_1555904624671315142[147] = 0;
   out_1555904624671315142[148] = 0;
   out_1555904624671315142[149] = 0;
   out_1555904624671315142[150] = 0;
   out_1555904624671315142[151] = 0;
   out_1555904624671315142[152] = 1;
   out_1555904624671315142[153] = 0;
   out_1555904624671315142[154] = 0;
   out_1555904624671315142[155] = 0;
   out_1555904624671315142[156] = 0;
   out_1555904624671315142[157] = 0;
   out_1555904624671315142[158] = 0;
   out_1555904624671315142[159] = 0;
   out_1555904624671315142[160] = 0;
   out_1555904624671315142[161] = 0;
   out_1555904624671315142[162] = 0;
   out_1555904624671315142[163] = 0;
   out_1555904624671315142[164] = 0;
   out_1555904624671315142[165] = 0;
   out_1555904624671315142[166] = 0;
   out_1555904624671315142[167] = 0;
   out_1555904624671315142[168] = 0;
   out_1555904624671315142[169] = 0;
   out_1555904624671315142[170] = 0;
   out_1555904624671315142[171] = 1;
   out_1555904624671315142[172] = 0;
   out_1555904624671315142[173] = 0;
   out_1555904624671315142[174] = 0;
   out_1555904624671315142[175] = 0;
   out_1555904624671315142[176] = 0;
   out_1555904624671315142[177] = 0;
   out_1555904624671315142[178] = 0;
   out_1555904624671315142[179] = 0;
   out_1555904624671315142[180] = 0;
   out_1555904624671315142[181] = 0;
   out_1555904624671315142[182] = 0;
   out_1555904624671315142[183] = 0;
   out_1555904624671315142[184] = 0;
   out_1555904624671315142[185] = 0;
   out_1555904624671315142[186] = 0;
   out_1555904624671315142[187] = 0;
   out_1555904624671315142[188] = 0;
   out_1555904624671315142[189] = 0;
   out_1555904624671315142[190] = 1;
   out_1555904624671315142[191] = 0;
   out_1555904624671315142[192] = 0;
   out_1555904624671315142[193] = 0;
   out_1555904624671315142[194] = 0;
   out_1555904624671315142[195] = 0;
   out_1555904624671315142[196] = 0;
   out_1555904624671315142[197] = 0;
   out_1555904624671315142[198] = 0;
   out_1555904624671315142[199] = 0;
   out_1555904624671315142[200] = 0;
   out_1555904624671315142[201] = 0;
   out_1555904624671315142[202] = 0;
   out_1555904624671315142[203] = 0;
   out_1555904624671315142[204] = 0;
   out_1555904624671315142[205] = 0;
   out_1555904624671315142[206] = 0;
   out_1555904624671315142[207] = 0;
   out_1555904624671315142[208] = 0;
   out_1555904624671315142[209] = 1;
   out_1555904624671315142[210] = 0;
   out_1555904624671315142[211] = 0;
   out_1555904624671315142[212] = 0;
   out_1555904624671315142[213] = 0;
   out_1555904624671315142[214] = 0;
   out_1555904624671315142[215] = 0;
   out_1555904624671315142[216] = 0;
   out_1555904624671315142[217] = 0;
   out_1555904624671315142[218] = 0;
   out_1555904624671315142[219] = 0;
   out_1555904624671315142[220] = 0;
   out_1555904624671315142[221] = 0;
   out_1555904624671315142[222] = 0;
   out_1555904624671315142[223] = 0;
   out_1555904624671315142[224] = 0;
   out_1555904624671315142[225] = 0;
   out_1555904624671315142[226] = 0;
   out_1555904624671315142[227] = 0;
   out_1555904624671315142[228] = 1;
   out_1555904624671315142[229] = 0;
   out_1555904624671315142[230] = 0;
   out_1555904624671315142[231] = 0;
   out_1555904624671315142[232] = 0;
   out_1555904624671315142[233] = 0;
   out_1555904624671315142[234] = 0;
   out_1555904624671315142[235] = 0;
   out_1555904624671315142[236] = 0;
   out_1555904624671315142[237] = 0;
   out_1555904624671315142[238] = 0;
   out_1555904624671315142[239] = 0;
   out_1555904624671315142[240] = 0;
   out_1555904624671315142[241] = 0;
   out_1555904624671315142[242] = 0;
   out_1555904624671315142[243] = 0;
   out_1555904624671315142[244] = 0;
   out_1555904624671315142[245] = 0;
   out_1555904624671315142[246] = 0;
   out_1555904624671315142[247] = 1;
   out_1555904624671315142[248] = 0;
   out_1555904624671315142[249] = 0;
   out_1555904624671315142[250] = 0;
   out_1555904624671315142[251] = 0;
   out_1555904624671315142[252] = 0;
   out_1555904624671315142[253] = 0;
   out_1555904624671315142[254] = 0;
   out_1555904624671315142[255] = 0;
   out_1555904624671315142[256] = 0;
   out_1555904624671315142[257] = 0;
   out_1555904624671315142[258] = 0;
   out_1555904624671315142[259] = 0;
   out_1555904624671315142[260] = 0;
   out_1555904624671315142[261] = 0;
   out_1555904624671315142[262] = 0;
   out_1555904624671315142[263] = 0;
   out_1555904624671315142[264] = 0;
   out_1555904624671315142[265] = 0;
   out_1555904624671315142[266] = 1;
   out_1555904624671315142[267] = 0;
   out_1555904624671315142[268] = 0;
   out_1555904624671315142[269] = 0;
   out_1555904624671315142[270] = 0;
   out_1555904624671315142[271] = 0;
   out_1555904624671315142[272] = 0;
   out_1555904624671315142[273] = 0;
   out_1555904624671315142[274] = 0;
   out_1555904624671315142[275] = 0;
   out_1555904624671315142[276] = 0;
   out_1555904624671315142[277] = 0;
   out_1555904624671315142[278] = 0;
   out_1555904624671315142[279] = 0;
   out_1555904624671315142[280] = 0;
   out_1555904624671315142[281] = 0;
   out_1555904624671315142[282] = 0;
   out_1555904624671315142[283] = 0;
   out_1555904624671315142[284] = 0;
   out_1555904624671315142[285] = 1;
   out_1555904624671315142[286] = 0;
   out_1555904624671315142[287] = 0;
   out_1555904624671315142[288] = 0;
   out_1555904624671315142[289] = 0;
   out_1555904624671315142[290] = 0;
   out_1555904624671315142[291] = 0;
   out_1555904624671315142[292] = 0;
   out_1555904624671315142[293] = 0;
   out_1555904624671315142[294] = 0;
   out_1555904624671315142[295] = 0;
   out_1555904624671315142[296] = 0;
   out_1555904624671315142[297] = 0;
   out_1555904624671315142[298] = 0;
   out_1555904624671315142[299] = 0;
   out_1555904624671315142[300] = 0;
   out_1555904624671315142[301] = 0;
   out_1555904624671315142[302] = 0;
   out_1555904624671315142[303] = 0;
   out_1555904624671315142[304] = 1;
   out_1555904624671315142[305] = 0;
   out_1555904624671315142[306] = 0;
   out_1555904624671315142[307] = 0;
   out_1555904624671315142[308] = 0;
   out_1555904624671315142[309] = 0;
   out_1555904624671315142[310] = 0;
   out_1555904624671315142[311] = 0;
   out_1555904624671315142[312] = 0;
   out_1555904624671315142[313] = 0;
   out_1555904624671315142[314] = 0;
   out_1555904624671315142[315] = 0;
   out_1555904624671315142[316] = 0;
   out_1555904624671315142[317] = 0;
   out_1555904624671315142[318] = 0;
   out_1555904624671315142[319] = 0;
   out_1555904624671315142[320] = 0;
   out_1555904624671315142[321] = 0;
   out_1555904624671315142[322] = 0;
   out_1555904624671315142[323] = 1;
}
void h_4(double *state, double *unused, double *out_6344336926878520260) {
   out_6344336926878520260[0] = state[6] + state[9];
   out_6344336926878520260[1] = state[7] + state[10];
   out_6344336926878520260[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_7105560155036670987) {
   out_7105560155036670987[0] = 0;
   out_7105560155036670987[1] = 0;
   out_7105560155036670987[2] = 0;
   out_7105560155036670987[3] = 0;
   out_7105560155036670987[4] = 0;
   out_7105560155036670987[5] = 0;
   out_7105560155036670987[6] = 1;
   out_7105560155036670987[7] = 0;
   out_7105560155036670987[8] = 0;
   out_7105560155036670987[9] = 1;
   out_7105560155036670987[10] = 0;
   out_7105560155036670987[11] = 0;
   out_7105560155036670987[12] = 0;
   out_7105560155036670987[13] = 0;
   out_7105560155036670987[14] = 0;
   out_7105560155036670987[15] = 0;
   out_7105560155036670987[16] = 0;
   out_7105560155036670987[17] = 0;
   out_7105560155036670987[18] = 0;
   out_7105560155036670987[19] = 0;
   out_7105560155036670987[20] = 0;
   out_7105560155036670987[21] = 0;
   out_7105560155036670987[22] = 0;
   out_7105560155036670987[23] = 0;
   out_7105560155036670987[24] = 0;
   out_7105560155036670987[25] = 1;
   out_7105560155036670987[26] = 0;
   out_7105560155036670987[27] = 0;
   out_7105560155036670987[28] = 1;
   out_7105560155036670987[29] = 0;
   out_7105560155036670987[30] = 0;
   out_7105560155036670987[31] = 0;
   out_7105560155036670987[32] = 0;
   out_7105560155036670987[33] = 0;
   out_7105560155036670987[34] = 0;
   out_7105560155036670987[35] = 0;
   out_7105560155036670987[36] = 0;
   out_7105560155036670987[37] = 0;
   out_7105560155036670987[38] = 0;
   out_7105560155036670987[39] = 0;
   out_7105560155036670987[40] = 0;
   out_7105560155036670987[41] = 0;
   out_7105560155036670987[42] = 0;
   out_7105560155036670987[43] = 0;
   out_7105560155036670987[44] = 1;
   out_7105560155036670987[45] = 0;
   out_7105560155036670987[46] = 0;
   out_7105560155036670987[47] = 1;
   out_7105560155036670987[48] = 0;
   out_7105560155036670987[49] = 0;
   out_7105560155036670987[50] = 0;
   out_7105560155036670987[51] = 0;
   out_7105560155036670987[52] = 0;
   out_7105560155036670987[53] = 0;
}
void h_10(double *state, double *unused, double *out_1404827797723103364) {
   out_1404827797723103364[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_1404827797723103364[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_1404827797723103364[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_7149609403250573740) {
   out_7149609403250573740[0] = 0;
   out_7149609403250573740[1] = 9.8100000000000005*cos(state[1]);
   out_7149609403250573740[2] = 0;
   out_7149609403250573740[3] = 0;
   out_7149609403250573740[4] = -state[8];
   out_7149609403250573740[5] = state[7];
   out_7149609403250573740[6] = 0;
   out_7149609403250573740[7] = state[5];
   out_7149609403250573740[8] = -state[4];
   out_7149609403250573740[9] = 0;
   out_7149609403250573740[10] = 0;
   out_7149609403250573740[11] = 0;
   out_7149609403250573740[12] = 1;
   out_7149609403250573740[13] = 0;
   out_7149609403250573740[14] = 0;
   out_7149609403250573740[15] = 1;
   out_7149609403250573740[16] = 0;
   out_7149609403250573740[17] = 0;
   out_7149609403250573740[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_7149609403250573740[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_7149609403250573740[20] = 0;
   out_7149609403250573740[21] = state[8];
   out_7149609403250573740[22] = 0;
   out_7149609403250573740[23] = -state[6];
   out_7149609403250573740[24] = -state[5];
   out_7149609403250573740[25] = 0;
   out_7149609403250573740[26] = state[3];
   out_7149609403250573740[27] = 0;
   out_7149609403250573740[28] = 0;
   out_7149609403250573740[29] = 0;
   out_7149609403250573740[30] = 0;
   out_7149609403250573740[31] = 1;
   out_7149609403250573740[32] = 0;
   out_7149609403250573740[33] = 0;
   out_7149609403250573740[34] = 1;
   out_7149609403250573740[35] = 0;
   out_7149609403250573740[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_7149609403250573740[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_7149609403250573740[38] = 0;
   out_7149609403250573740[39] = -state[7];
   out_7149609403250573740[40] = state[6];
   out_7149609403250573740[41] = 0;
   out_7149609403250573740[42] = state[4];
   out_7149609403250573740[43] = -state[3];
   out_7149609403250573740[44] = 0;
   out_7149609403250573740[45] = 0;
   out_7149609403250573740[46] = 0;
   out_7149609403250573740[47] = 0;
   out_7149609403250573740[48] = 0;
   out_7149609403250573740[49] = 0;
   out_7149609403250573740[50] = 1;
   out_7149609403250573740[51] = 0;
   out_7149609403250573740[52] = 0;
   out_7149609403250573740[53] = 1;
}
void h_13(double *state, double *unused, double *out_7533459209982952318) {
   out_7533459209982952318[0] = state[3];
   out_7533459209982952318[1] = state[4];
   out_7533459209982952318[2] = state[5];
}
void H_13(double *state, double *unused, double *out_3271804691734146963) {
   out_3271804691734146963[0] = 0;
   out_3271804691734146963[1] = 0;
   out_3271804691734146963[2] = 0;
   out_3271804691734146963[3] = 1;
   out_3271804691734146963[4] = 0;
   out_3271804691734146963[5] = 0;
   out_3271804691734146963[6] = 0;
   out_3271804691734146963[7] = 0;
   out_3271804691734146963[8] = 0;
   out_3271804691734146963[9] = 0;
   out_3271804691734146963[10] = 0;
   out_3271804691734146963[11] = 0;
   out_3271804691734146963[12] = 0;
   out_3271804691734146963[13] = 0;
   out_3271804691734146963[14] = 0;
   out_3271804691734146963[15] = 0;
   out_3271804691734146963[16] = 0;
   out_3271804691734146963[17] = 0;
   out_3271804691734146963[18] = 0;
   out_3271804691734146963[19] = 0;
   out_3271804691734146963[20] = 0;
   out_3271804691734146963[21] = 0;
   out_3271804691734146963[22] = 1;
   out_3271804691734146963[23] = 0;
   out_3271804691734146963[24] = 0;
   out_3271804691734146963[25] = 0;
   out_3271804691734146963[26] = 0;
   out_3271804691734146963[27] = 0;
   out_3271804691734146963[28] = 0;
   out_3271804691734146963[29] = 0;
   out_3271804691734146963[30] = 0;
   out_3271804691734146963[31] = 0;
   out_3271804691734146963[32] = 0;
   out_3271804691734146963[33] = 0;
   out_3271804691734146963[34] = 0;
   out_3271804691734146963[35] = 0;
   out_3271804691734146963[36] = 0;
   out_3271804691734146963[37] = 0;
   out_3271804691734146963[38] = 0;
   out_3271804691734146963[39] = 0;
   out_3271804691734146963[40] = 0;
   out_3271804691734146963[41] = 1;
   out_3271804691734146963[42] = 0;
   out_3271804691734146963[43] = 0;
   out_3271804691734146963[44] = 0;
   out_3271804691734146963[45] = 0;
   out_3271804691734146963[46] = 0;
   out_3271804691734146963[47] = 0;
   out_3271804691734146963[48] = 0;
   out_3271804691734146963[49] = 0;
   out_3271804691734146963[50] = 0;
   out_3271804691734146963[51] = 0;
   out_3271804691734146963[52] = 0;
   out_3271804691734146963[53] = 0;
}
void h_14(double *state, double *unused, double *out_2121789093779121634) {
   out_2121789093779121634[0] = state[6];
   out_2121789093779121634[1] = state[7];
   out_2121789093779121634[2] = state[8];
}
void H_14(double *state, double *unused, double *out_4022771722741298691) {
   out_4022771722741298691[0] = 0;
   out_4022771722741298691[1] = 0;
   out_4022771722741298691[2] = 0;
   out_4022771722741298691[3] = 0;
   out_4022771722741298691[4] = 0;
   out_4022771722741298691[5] = 0;
   out_4022771722741298691[6] = 1;
   out_4022771722741298691[7] = 0;
   out_4022771722741298691[8] = 0;
   out_4022771722741298691[9] = 0;
   out_4022771722741298691[10] = 0;
   out_4022771722741298691[11] = 0;
   out_4022771722741298691[12] = 0;
   out_4022771722741298691[13] = 0;
   out_4022771722741298691[14] = 0;
   out_4022771722741298691[15] = 0;
   out_4022771722741298691[16] = 0;
   out_4022771722741298691[17] = 0;
   out_4022771722741298691[18] = 0;
   out_4022771722741298691[19] = 0;
   out_4022771722741298691[20] = 0;
   out_4022771722741298691[21] = 0;
   out_4022771722741298691[22] = 0;
   out_4022771722741298691[23] = 0;
   out_4022771722741298691[24] = 0;
   out_4022771722741298691[25] = 1;
   out_4022771722741298691[26] = 0;
   out_4022771722741298691[27] = 0;
   out_4022771722741298691[28] = 0;
   out_4022771722741298691[29] = 0;
   out_4022771722741298691[30] = 0;
   out_4022771722741298691[31] = 0;
   out_4022771722741298691[32] = 0;
   out_4022771722741298691[33] = 0;
   out_4022771722741298691[34] = 0;
   out_4022771722741298691[35] = 0;
   out_4022771722741298691[36] = 0;
   out_4022771722741298691[37] = 0;
   out_4022771722741298691[38] = 0;
   out_4022771722741298691[39] = 0;
   out_4022771722741298691[40] = 0;
   out_4022771722741298691[41] = 0;
   out_4022771722741298691[42] = 0;
   out_4022771722741298691[43] = 0;
   out_4022771722741298691[44] = 1;
   out_4022771722741298691[45] = 0;
   out_4022771722741298691[46] = 0;
   out_4022771722741298691[47] = 0;
   out_4022771722741298691[48] = 0;
   out_4022771722741298691[49] = 0;
   out_4022771722741298691[50] = 0;
   out_4022771722741298691[51] = 0;
   out_4022771722741298691[52] = 0;
   out_4022771722741298691[53] = 0;
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
void pose_err_fun(double *nom_x, double *delta_x, double *out_7318184160914923263) {
  err_fun(nom_x, delta_x, out_7318184160914923263);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_8130026506067701099) {
  inv_err_fun(nom_x, true_x, out_8130026506067701099);
}
void pose_H_mod_fun(double *state, double *out_5907612673153772883) {
  H_mod_fun(state, out_5907612673153772883);
}
void pose_f_fun(double *state, double dt, double *out_4351928450748542819) {
  f_fun(state,  dt, out_4351928450748542819);
}
void pose_F_fun(double *state, double dt, double *out_1555904624671315142) {
  F_fun(state,  dt, out_1555904624671315142);
}
void pose_h_4(double *state, double *unused, double *out_6344336926878520260) {
  h_4(state, unused, out_6344336926878520260);
}
void pose_H_4(double *state, double *unused, double *out_7105560155036670987) {
  H_4(state, unused, out_7105560155036670987);
}
void pose_h_10(double *state, double *unused, double *out_1404827797723103364) {
  h_10(state, unused, out_1404827797723103364);
}
void pose_H_10(double *state, double *unused, double *out_7149609403250573740) {
  H_10(state, unused, out_7149609403250573740);
}
void pose_h_13(double *state, double *unused, double *out_7533459209982952318) {
  h_13(state, unused, out_7533459209982952318);
}
void pose_H_13(double *state, double *unused, double *out_3271804691734146963) {
  H_13(state, unused, out_3271804691734146963);
}
void pose_h_14(double *state, double *unused, double *out_2121789093779121634) {
  h_14(state, unused, out_2121789093779121634);
}
void pose_H_14(double *state, double *unused, double *out_4022771722741298691) {
  H_14(state, unused, out_4022771722741298691);
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
