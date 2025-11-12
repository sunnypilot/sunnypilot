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
void err_fun(double *nom_x, double *delta_x, double *out_2708976385256854938) {
   out_2708976385256854938[0] = delta_x[0] + nom_x[0];
   out_2708976385256854938[1] = delta_x[1] + nom_x[1];
   out_2708976385256854938[2] = delta_x[2] + nom_x[2];
   out_2708976385256854938[3] = delta_x[3] + nom_x[3];
   out_2708976385256854938[4] = delta_x[4] + nom_x[4];
   out_2708976385256854938[5] = delta_x[5] + nom_x[5];
   out_2708976385256854938[6] = delta_x[6] + nom_x[6];
   out_2708976385256854938[7] = delta_x[7] + nom_x[7];
   out_2708976385256854938[8] = delta_x[8] + nom_x[8];
   out_2708976385256854938[9] = delta_x[9] + nom_x[9];
   out_2708976385256854938[10] = delta_x[10] + nom_x[10];
   out_2708976385256854938[11] = delta_x[11] + nom_x[11];
   out_2708976385256854938[12] = delta_x[12] + nom_x[12];
   out_2708976385256854938[13] = delta_x[13] + nom_x[13];
   out_2708976385256854938[14] = delta_x[14] + nom_x[14];
   out_2708976385256854938[15] = delta_x[15] + nom_x[15];
   out_2708976385256854938[16] = delta_x[16] + nom_x[16];
   out_2708976385256854938[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_5039075117443556308) {
   out_5039075117443556308[0] = -nom_x[0] + true_x[0];
   out_5039075117443556308[1] = -nom_x[1] + true_x[1];
   out_5039075117443556308[2] = -nom_x[2] + true_x[2];
   out_5039075117443556308[3] = -nom_x[3] + true_x[3];
   out_5039075117443556308[4] = -nom_x[4] + true_x[4];
   out_5039075117443556308[5] = -nom_x[5] + true_x[5];
   out_5039075117443556308[6] = -nom_x[6] + true_x[6];
   out_5039075117443556308[7] = -nom_x[7] + true_x[7];
   out_5039075117443556308[8] = -nom_x[8] + true_x[8];
   out_5039075117443556308[9] = -nom_x[9] + true_x[9];
   out_5039075117443556308[10] = -nom_x[10] + true_x[10];
   out_5039075117443556308[11] = -nom_x[11] + true_x[11];
   out_5039075117443556308[12] = -nom_x[12] + true_x[12];
   out_5039075117443556308[13] = -nom_x[13] + true_x[13];
   out_5039075117443556308[14] = -nom_x[14] + true_x[14];
   out_5039075117443556308[15] = -nom_x[15] + true_x[15];
   out_5039075117443556308[16] = -nom_x[16] + true_x[16];
   out_5039075117443556308[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_4768576861501722562) {
   out_4768576861501722562[0] = 1.0;
   out_4768576861501722562[1] = 0.0;
   out_4768576861501722562[2] = 0.0;
   out_4768576861501722562[3] = 0.0;
   out_4768576861501722562[4] = 0.0;
   out_4768576861501722562[5] = 0.0;
   out_4768576861501722562[6] = 0.0;
   out_4768576861501722562[7] = 0.0;
   out_4768576861501722562[8] = 0.0;
   out_4768576861501722562[9] = 0.0;
   out_4768576861501722562[10] = 0.0;
   out_4768576861501722562[11] = 0.0;
   out_4768576861501722562[12] = 0.0;
   out_4768576861501722562[13] = 0.0;
   out_4768576861501722562[14] = 0.0;
   out_4768576861501722562[15] = 0.0;
   out_4768576861501722562[16] = 0.0;
   out_4768576861501722562[17] = 0.0;
   out_4768576861501722562[18] = 0.0;
   out_4768576861501722562[19] = 1.0;
   out_4768576861501722562[20] = 0.0;
   out_4768576861501722562[21] = 0.0;
   out_4768576861501722562[22] = 0.0;
   out_4768576861501722562[23] = 0.0;
   out_4768576861501722562[24] = 0.0;
   out_4768576861501722562[25] = 0.0;
   out_4768576861501722562[26] = 0.0;
   out_4768576861501722562[27] = 0.0;
   out_4768576861501722562[28] = 0.0;
   out_4768576861501722562[29] = 0.0;
   out_4768576861501722562[30] = 0.0;
   out_4768576861501722562[31] = 0.0;
   out_4768576861501722562[32] = 0.0;
   out_4768576861501722562[33] = 0.0;
   out_4768576861501722562[34] = 0.0;
   out_4768576861501722562[35] = 0.0;
   out_4768576861501722562[36] = 0.0;
   out_4768576861501722562[37] = 0.0;
   out_4768576861501722562[38] = 1.0;
   out_4768576861501722562[39] = 0.0;
   out_4768576861501722562[40] = 0.0;
   out_4768576861501722562[41] = 0.0;
   out_4768576861501722562[42] = 0.0;
   out_4768576861501722562[43] = 0.0;
   out_4768576861501722562[44] = 0.0;
   out_4768576861501722562[45] = 0.0;
   out_4768576861501722562[46] = 0.0;
   out_4768576861501722562[47] = 0.0;
   out_4768576861501722562[48] = 0.0;
   out_4768576861501722562[49] = 0.0;
   out_4768576861501722562[50] = 0.0;
   out_4768576861501722562[51] = 0.0;
   out_4768576861501722562[52] = 0.0;
   out_4768576861501722562[53] = 0.0;
   out_4768576861501722562[54] = 0.0;
   out_4768576861501722562[55] = 0.0;
   out_4768576861501722562[56] = 0.0;
   out_4768576861501722562[57] = 1.0;
   out_4768576861501722562[58] = 0.0;
   out_4768576861501722562[59] = 0.0;
   out_4768576861501722562[60] = 0.0;
   out_4768576861501722562[61] = 0.0;
   out_4768576861501722562[62] = 0.0;
   out_4768576861501722562[63] = 0.0;
   out_4768576861501722562[64] = 0.0;
   out_4768576861501722562[65] = 0.0;
   out_4768576861501722562[66] = 0.0;
   out_4768576861501722562[67] = 0.0;
   out_4768576861501722562[68] = 0.0;
   out_4768576861501722562[69] = 0.0;
   out_4768576861501722562[70] = 0.0;
   out_4768576861501722562[71] = 0.0;
   out_4768576861501722562[72] = 0.0;
   out_4768576861501722562[73] = 0.0;
   out_4768576861501722562[74] = 0.0;
   out_4768576861501722562[75] = 0.0;
   out_4768576861501722562[76] = 1.0;
   out_4768576861501722562[77] = 0.0;
   out_4768576861501722562[78] = 0.0;
   out_4768576861501722562[79] = 0.0;
   out_4768576861501722562[80] = 0.0;
   out_4768576861501722562[81] = 0.0;
   out_4768576861501722562[82] = 0.0;
   out_4768576861501722562[83] = 0.0;
   out_4768576861501722562[84] = 0.0;
   out_4768576861501722562[85] = 0.0;
   out_4768576861501722562[86] = 0.0;
   out_4768576861501722562[87] = 0.0;
   out_4768576861501722562[88] = 0.0;
   out_4768576861501722562[89] = 0.0;
   out_4768576861501722562[90] = 0.0;
   out_4768576861501722562[91] = 0.0;
   out_4768576861501722562[92] = 0.0;
   out_4768576861501722562[93] = 0.0;
   out_4768576861501722562[94] = 0.0;
   out_4768576861501722562[95] = 1.0;
   out_4768576861501722562[96] = 0.0;
   out_4768576861501722562[97] = 0.0;
   out_4768576861501722562[98] = 0.0;
   out_4768576861501722562[99] = 0.0;
   out_4768576861501722562[100] = 0.0;
   out_4768576861501722562[101] = 0.0;
   out_4768576861501722562[102] = 0.0;
   out_4768576861501722562[103] = 0.0;
   out_4768576861501722562[104] = 0.0;
   out_4768576861501722562[105] = 0.0;
   out_4768576861501722562[106] = 0.0;
   out_4768576861501722562[107] = 0.0;
   out_4768576861501722562[108] = 0.0;
   out_4768576861501722562[109] = 0.0;
   out_4768576861501722562[110] = 0.0;
   out_4768576861501722562[111] = 0.0;
   out_4768576861501722562[112] = 0.0;
   out_4768576861501722562[113] = 0.0;
   out_4768576861501722562[114] = 1.0;
   out_4768576861501722562[115] = 0.0;
   out_4768576861501722562[116] = 0.0;
   out_4768576861501722562[117] = 0.0;
   out_4768576861501722562[118] = 0.0;
   out_4768576861501722562[119] = 0.0;
   out_4768576861501722562[120] = 0.0;
   out_4768576861501722562[121] = 0.0;
   out_4768576861501722562[122] = 0.0;
   out_4768576861501722562[123] = 0.0;
   out_4768576861501722562[124] = 0.0;
   out_4768576861501722562[125] = 0.0;
   out_4768576861501722562[126] = 0.0;
   out_4768576861501722562[127] = 0.0;
   out_4768576861501722562[128] = 0.0;
   out_4768576861501722562[129] = 0.0;
   out_4768576861501722562[130] = 0.0;
   out_4768576861501722562[131] = 0.0;
   out_4768576861501722562[132] = 0.0;
   out_4768576861501722562[133] = 1.0;
   out_4768576861501722562[134] = 0.0;
   out_4768576861501722562[135] = 0.0;
   out_4768576861501722562[136] = 0.0;
   out_4768576861501722562[137] = 0.0;
   out_4768576861501722562[138] = 0.0;
   out_4768576861501722562[139] = 0.0;
   out_4768576861501722562[140] = 0.0;
   out_4768576861501722562[141] = 0.0;
   out_4768576861501722562[142] = 0.0;
   out_4768576861501722562[143] = 0.0;
   out_4768576861501722562[144] = 0.0;
   out_4768576861501722562[145] = 0.0;
   out_4768576861501722562[146] = 0.0;
   out_4768576861501722562[147] = 0.0;
   out_4768576861501722562[148] = 0.0;
   out_4768576861501722562[149] = 0.0;
   out_4768576861501722562[150] = 0.0;
   out_4768576861501722562[151] = 0.0;
   out_4768576861501722562[152] = 1.0;
   out_4768576861501722562[153] = 0.0;
   out_4768576861501722562[154] = 0.0;
   out_4768576861501722562[155] = 0.0;
   out_4768576861501722562[156] = 0.0;
   out_4768576861501722562[157] = 0.0;
   out_4768576861501722562[158] = 0.0;
   out_4768576861501722562[159] = 0.0;
   out_4768576861501722562[160] = 0.0;
   out_4768576861501722562[161] = 0.0;
   out_4768576861501722562[162] = 0.0;
   out_4768576861501722562[163] = 0.0;
   out_4768576861501722562[164] = 0.0;
   out_4768576861501722562[165] = 0.0;
   out_4768576861501722562[166] = 0.0;
   out_4768576861501722562[167] = 0.0;
   out_4768576861501722562[168] = 0.0;
   out_4768576861501722562[169] = 0.0;
   out_4768576861501722562[170] = 0.0;
   out_4768576861501722562[171] = 1.0;
   out_4768576861501722562[172] = 0.0;
   out_4768576861501722562[173] = 0.0;
   out_4768576861501722562[174] = 0.0;
   out_4768576861501722562[175] = 0.0;
   out_4768576861501722562[176] = 0.0;
   out_4768576861501722562[177] = 0.0;
   out_4768576861501722562[178] = 0.0;
   out_4768576861501722562[179] = 0.0;
   out_4768576861501722562[180] = 0.0;
   out_4768576861501722562[181] = 0.0;
   out_4768576861501722562[182] = 0.0;
   out_4768576861501722562[183] = 0.0;
   out_4768576861501722562[184] = 0.0;
   out_4768576861501722562[185] = 0.0;
   out_4768576861501722562[186] = 0.0;
   out_4768576861501722562[187] = 0.0;
   out_4768576861501722562[188] = 0.0;
   out_4768576861501722562[189] = 0.0;
   out_4768576861501722562[190] = 1.0;
   out_4768576861501722562[191] = 0.0;
   out_4768576861501722562[192] = 0.0;
   out_4768576861501722562[193] = 0.0;
   out_4768576861501722562[194] = 0.0;
   out_4768576861501722562[195] = 0.0;
   out_4768576861501722562[196] = 0.0;
   out_4768576861501722562[197] = 0.0;
   out_4768576861501722562[198] = 0.0;
   out_4768576861501722562[199] = 0.0;
   out_4768576861501722562[200] = 0.0;
   out_4768576861501722562[201] = 0.0;
   out_4768576861501722562[202] = 0.0;
   out_4768576861501722562[203] = 0.0;
   out_4768576861501722562[204] = 0.0;
   out_4768576861501722562[205] = 0.0;
   out_4768576861501722562[206] = 0.0;
   out_4768576861501722562[207] = 0.0;
   out_4768576861501722562[208] = 0.0;
   out_4768576861501722562[209] = 1.0;
   out_4768576861501722562[210] = 0.0;
   out_4768576861501722562[211] = 0.0;
   out_4768576861501722562[212] = 0.0;
   out_4768576861501722562[213] = 0.0;
   out_4768576861501722562[214] = 0.0;
   out_4768576861501722562[215] = 0.0;
   out_4768576861501722562[216] = 0.0;
   out_4768576861501722562[217] = 0.0;
   out_4768576861501722562[218] = 0.0;
   out_4768576861501722562[219] = 0.0;
   out_4768576861501722562[220] = 0.0;
   out_4768576861501722562[221] = 0.0;
   out_4768576861501722562[222] = 0.0;
   out_4768576861501722562[223] = 0.0;
   out_4768576861501722562[224] = 0.0;
   out_4768576861501722562[225] = 0.0;
   out_4768576861501722562[226] = 0.0;
   out_4768576861501722562[227] = 0.0;
   out_4768576861501722562[228] = 1.0;
   out_4768576861501722562[229] = 0.0;
   out_4768576861501722562[230] = 0.0;
   out_4768576861501722562[231] = 0.0;
   out_4768576861501722562[232] = 0.0;
   out_4768576861501722562[233] = 0.0;
   out_4768576861501722562[234] = 0.0;
   out_4768576861501722562[235] = 0.0;
   out_4768576861501722562[236] = 0.0;
   out_4768576861501722562[237] = 0.0;
   out_4768576861501722562[238] = 0.0;
   out_4768576861501722562[239] = 0.0;
   out_4768576861501722562[240] = 0.0;
   out_4768576861501722562[241] = 0.0;
   out_4768576861501722562[242] = 0.0;
   out_4768576861501722562[243] = 0.0;
   out_4768576861501722562[244] = 0.0;
   out_4768576861501722562[245] = 0.0;
   out_4768576861501722562[246] = 0.0;
   out_4768576861501722562[247] = 1.0;
   out_4768576861501722562[248] = 0.0;
   out_4768576861501722562[249] = 0.0;
   out_4768576861501722562[250] = 0.0;
   out_4768576861501722562[251] = 0.0;
   out_4768576861501722562[252] = 0.0;
   out_4768576861501722562[253] = 0.0;
   out_4768576861501722562[254] = 0.0;
   out_4768576861501722562[255] = 0.0;
   out_4768576861501722562[256] = 0.0;
   out_4768576861501722562[257] = 0.0;
   out_4768576861501722562[258] = 0.0;
   out_4768576861501722562[259] = 0.0;
   out_4768576861501722562[260] = 0.0;
   out_4768576861501722562[261] = 0.0;
   out_4768576861501722562[262] = 0.0;
   out_4768576861501722562[263] = 0.0;
   out_4768576861501722562[264] = 0.0;
   out_4768576861501722562[265] = 0.0;
   out_4768576861501722562[266] = 1.0;
   out_4768576861501722562[267] = 0.0;
   out_4768576861501722562[268] = 0.0;
   out_4768576861501722562[269] = 0.0;
   out_4768576861501722562[270] = 0.0;
   out_4768576861501722562[271] = 0.0;
   out_4768576861501722562[272] = 0.0;
   out_4768576861501722562[273] = 0.0;
   out_4768576861501722562[274] = 0.0;
   out_4768576861501722562[275] = 0.0;
   out_4768576861501722562[276] = 0.0;
   out_4768576861501722562[277] = 0.0;
   out_4768576861501722562[278] = 0.0;
   out_4768576861501722562[279] = 0.0;
   out_4768576861501722562[280] = 0.0;
   out_4768576861501722562[281] = 0.0;
   out_4768576861501722562[282] = 0.0;
   out_4768576861501722562[283] = 0.0;
   out_4768576861501722562[284] = 0.0;
   out_4768576861501722562[285] = 1.0;
   out_4768576861501722562[286] = 0.0;
   out_4768576861501722562[287] = 0.0;
   out_4768576861501722562[288] = 0.0;
   out_4768576861501722562[289] = 0.0;
   out_4768576861501722562[290] = 0.0;
   out_4768576861501722562[291] = 0.0;
   out_4768576861501722562[292] = 0.0;
   out_4768576861501722562[293] = 0.0;
   out_4768576861501722562[294] = 0.0;
   out_4768576861501722562[295] = 0.0;
   out_4768576861501722562[296] = 0.0;
   out_4768576861501722562[297] = 0.0;
   out_4768576861501722562[298] = 0.0;
   out_4768576861501722562[299] = 0.0;
   out_4768576861501722562[300] = 0.0;
   out_4768576861501722562[301] = 0.0;
   out_4768576861501722562[302] = 0.0;
   out_4768576861501722562[303] = 0.0;
   out_4768576861501722562[304] = 1.0;
   out_4768576861501722562[305] = 0.0;
   out_4768576861501722562[306] = 0.0;
   out_4768576861501722562[307] = 0.0;
   out_4768576861501722562[308] = 0.0;
   out_4768576861501722562[309] = 0.0;
   out_4768576861501722562[310] = 0.0;
   out_4768576861501722562[311] = 0.0;
   out_4768576861501722562[312] = 0.0;
   out_4768576861501722562[313] = 0.0;
   out_4768576861501722562[314] = 0.0;
   out_4768576861501722562[315] = 0.0;
   out_4768576861501722562[316] = 0.0;
   out_4768576861501722562[317] = 0.0;
   out_4768576861501722562[318] = 0.0;
   out_4768576861501722562[319] = 0.0;
   out_4768576861501722562[320] = 0.0;
   out_4768576861501722562[321] = 0.0;
   out_4768576861501722562[322] = 0.0;
   out_4768576861501722562[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_3365426939231918965) {
   out_3365426939231918965[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_3365426939231918965[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_3365426939231918965[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_3365426939231918965[3] = dt*state[12] + state[3];
   out_3365426939231918965[4] = dt*state[13] + state[4];
   out_3365426939231918965[5] = dt*state[14] + state[5];
   out_3365426939231918965[6] = state[6];
   out_3365426939231918965[7] = state[7];
   out_3365426939231918965[8] = state[8];
   out_3365426939231918965[9] = state[9];
   out_3365426939231918965[10] = state[10];
   out_3365426939231918965[11] = state[11];
   out_3365426939231918965[12] = state[12];
   out_3365426939231918965[13] = state[13];
   out_3365426939231918965[14] = state[14];
   out_3365426939231918965[15] = state[15];
   out_3365426939231918965[16] = state[16];
   out_3365426939231918965[17] = state[17];
}
void F_fun(double *state, double dt, double *out_6077984892743029865) {
   out_6077984892743029865[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_6077984892743029865[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_6077984892743029865[2] = 0;
   out_6077984892743029865[3] = 0;
   out_6077984892743029865[4] = 0;
   out_6077984892743029865[5] = 0;
   out_6077984892743029865[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_6077984892743029865[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_6077984892743029865[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_6077984892743029865[9] = 0;
   out_6077984892743029865[10] = 0;
   out_6077984892743029865[11] = 0;
   out_6077984892743029865[12] = 0;
   out_6077984892743029865[13] = 0;
   out_6077984892743029865[14] = 0;
   out_6077984892743029865[15] = 0;
   out_6077984892743029865[16] = 0;
   out_6077984892743029865[17] = 0;
   out_6077984892743029865[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_6077984892743029865[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_6077984892743029865[20] = 0;
   out_6077984892743029865[21] = 0;
   out_6077984892743029865[22] = 0;
   out_6077984892743029865[23] = 0;
   out_6077984892743029865[24] = 0;
   out_6077984892743029865[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_6077984892743029865[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_6077984892743029865[27] = 0;
   out_6077984892743029865[28] = 0;
   out_6077984892743029865[29] = 0;
   out_6077984892743029865[30] = 0;
   out_6077984892743029865[31] = 0;
   out_6077984892743029865[32] = 0;
   out_6077984892743029865[33] = 0;
   out_6077984892743029865[34] = 0;
   out_6077984892743029865[35] = 0;
   out_6077984892743029865[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_6077984892743029865[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_6077984892743029865[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_6077984892743029865[39] = 0;
   out_6077984892743029865[40] = 0;
   out_6077984892743029865[41] = 0;
   out_6077984892743029865[42] = 0;
   out_6077984892743029865[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_6077984892743029865[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_6077984892743029865[45] = 0;
   out_6077984892743029865[46] = 0;
   out_6077984892743029865[47] = 0;
   out_6077984892743029865[48] = 0;
   out_6077984892743029865[49] = 0;
   out_6077984892743029865[50] = 0;
   out_6077984892743029865[51] = 0;
   out_6077984892743029865[52] = 0;
   out_6077984892743029865[53] = 0;
   out_6077984892743029865[54] = 0;
   out_6077984892743029865[55] = 0;
   out_6077984892743029865[56] = 0;
   out_6077984892743029865[57] = 1;
   out_6077984892743029865[58] = 0;
   out_6077984892743029865[59] = 0;
   out_6077984892743029865[60] = 0;
   out_6077984892743029865[61] = 0;
   out_6077984892743029865[62] = 0;
   out_6077984892743029865[63] = 0;
   out_6077984892743029865[64] = 0;
   out_6077984892743029865[65] = 0;
   out_6077984892743029865[66] = dt;
   out_6077984892743029865[67] = 0;
   out_6077984892743029865[68] = 0;
   out_6077984892743029865[69] = 0;
   out_6077984892743029865[70] = 0;
   out_6077984892743029865[71] = 0;
   out_6077984892743029865[72] = 0;
   out_6077984892743029865[73] = 0;
   out_6077984892743029865[74] = 0;
   out_6077984892743029865[75] = 0;
   out_6077984892743029865[76] = 1;
   out_6077984892743029865[77] = 0;
   out_6077984892743029865[78] = 0;
   out_6077984892743029865[79] = 0;
   out_6077984892743029865[80] = 0;
   out_6077984892743029865[81] = 0;
   out_6077984892743029865[82] = 0;
   out_6077984892743029865[83] = 0;
   out_6077984892743029865[84] = 0;
   out_6077984892743029865[85] = dt;
   out_6077984892743029865[86] = 0;
   out_6077984892743029865[87] = 0;
   out_6077984892743029865[88] = 0;
   out_6077984892743029865[89] = 0;
   out_6077984892743029865[90] = 0;
   out_6077984892743029865[91] = 0;
   out_6077984892743029865[92] = 0;
   out_6077984892743029865[93] = 0;
   out_6077984892743029865[94] = 0;
   out_6077984892743029865[95] = 1;
   out_6077984892743029865[96] = 0;
   out_6077984892743029865[97] = 0;
   out_6077984892743029865[98] = 0;
   out_6077984892743029865[99] = 0;
   out_6077984892743029865[100] = 0;
   out_6077984892743029865[101] = 0;
   out_6077984892743029865[102] = 0;
   out_6077984892743029865[103] = 0;
   out_6077984892743029865[104] = dt;
   out_6077984892743029865[105] = 0;
   out_6077984892743029865[106] = 0;
   out_6077984892743029865[107] = 0;
   out_6077984892743029865[108] = 0;
   out_6077984892743029865[109] = 0;
   out_6077984892743029865[110] = 0;
   out_6077984892743029865[111] = 0;
   out_6077984892743029865[112] = 0;
   out_6077984892743029865[113] = 0;
   out_6077984892743029865[114] = 1;
   out_6077984892743029865[115] = 0;
   out_6077984892743029865[116] = 0;
   out_6077984892743029865[117] = 0;
   out_6077984892743029865[118] = 0;
   out_6077984892743029865[119] = 0;
   out_6077984892743029865[120] = 0;
   out_6077984892743029865[121] = 0;
   out_6077984892743029865[122] = 0;
   out_6077984892743029865[123] = 0;
   out_6077984892743029865[124] = 0;
   out_6077984892743029865[125] = 0;
   out_6077984892743029865[126] = 0;
   out_6077984892743029865[127] = 0;
   out_6077984892743029865[128] = 0;
   out_6077984892743029865[129] = 0;
   out_6077984892743029865[130] = 0;
   out_6077984892743029865[131] = 0;
   out_6077984892743029865[132] = 0;
   out_6077984892743029865[133] = 1;
   out_6077984892743029865[134] = 0;
   out_6077984892743029865[135] = 0;
   out_6077984892743029865[136] = 0;
   out_6077984892743029865[137] = 0;
   out_6077984892743029865[138] = 0;
   out_6077984892743029865[139] = 0;
   out_6077984892743029865[140] = 0;
   out_6077984892743029865[141] = 0;
   out_6077984892743029865[142] = 0;
   out_6077984892743029865[143] = 0;
   out_6077984892743029865[144] = 0;
   out_6077984892743029865[145] = 0;
   out_6077984892743029865[146] = 0;
   out_6077984892743029865[147] = 0;
   out_6077984892743029865[148] = 0;
   out_6077984892743029865[149] = 0;
   out_6077984892743029865[150] = 0;
   out_6077984892743029865[151] = 0;
   out_6077984892743029865[152] = 1;
   out_6077984892743029865[153] = 0;
   out_6077984892743029865[154] = 0;
   out_6077984892743029865[155] = 0;
   out_6077984892743029865[156] = 0;
   out_6077984892743029865[157] = 0;
   out_6077984892743029865[158] = 0;
   out_6077984892743029865[159] = 0;
   out_6077984892743029865[160] = 0;
   out_6077984892743029865[161] = 0;
   out_6077984892743029865[162] = 0;
   out_6077984892743029865[163] = 0;
   out_6077984892743029865[164] = 0;
   out_6077984892743029865[165] = 0;
   out_6077984892743029865[166] = 0;
   out_6077984892743029865[167] = 0;
   out_6077984892743029865[168] = 0;
   out_6077984892743029865[169] = 0;
   out_6077984892743029865[170] = 0;
   out_6077984892743029865[171] = 1;
   out_6077984892743029865[172] = 0;
   out_6077984892743029865[173] = 0;
   out_6077984892743029865[174] = 0;
   out_6077984892743029865[175] = 0;
   out_6077984892743029865[176] = 0;
   out_6077984892743029865[177] = 0;
   out_6077984892743029865[178] = 0;
   out_6077984892743029865[179] = 0;
   out_6077984892743029865[180] = 0;
   out_6077984892743029865[181] = 0;
   out_6077984892743029865[182] = 0;
   out_6077984892743029865[183] = 0;
   out_6077984892743029865[184] = 0;
   out_6077984892743029865[185] = 0;
   out_6077984892743029865[186] = 0;
   out_6077984892743029865[187] = 0;
   out_6077984892743029865[188] = 0;
   out_6077984892743029865[189] = 0;
   out_6077984892743029865[190] = 1;
   out_6077984892743029865[191] = 0;
   out_6077984892743029865[192] = 0;
   out_6077984892743029865[193] = 0;
   out_6077984892743029865[194] = 0;
   out_6077984892743029865[195] = 0;
   out_6077984892743029865[196] = 0;
   out_6077984892743029865[197] = 0;
   out_6077984892743029865[198] = 0;
   out_6077984892743029865[199] = 0;
   out_6077984892743029865[200] = 0;
   out_6077984892743029865[201] = 0;
   out_6077984892743029865[202] = 0;
   out_6077984892743029865[203] = 0;
   out_6077984892743029865[204] = 0;
   out_6077984892743029865[205] = 0;
   out_6077984892743029865[206] = 0;
   out_6077984892743029865[207] = 0;
   out_6077984892743029865[208] = 0;
   out_6077984892743029865[209] = 1;
   out_6077984892743029865[210] = 0;
   out_6077984892743029865[211] = 0;
   out_6077984892743029865[212] = 0;
   out_6077984892743029865[213] = 0;
   out_6077984892743029865[214] = 0;
   out_6077984892743029865[215] = 0;
   out_6077984892743029865[216] = 0;
   out_6077984892743029865[217] = 0;
   out_6077984892743029865[218] = 0;
   out_6077984892743029865[219] = 0;
   out_6077984892743029865[220] = 0;
   out_6077984892743029865[221] = 0;
   out_6077984892743029865[222] = 0;
   out_6077984892743029865[223] = 0;
   out_6077984892743029865[224] = 0;
   out_6077984892743029865[225] = 0;
   out_6077984892743029865[226] = 0;
   out_6077984892743029865[227] = 0;
   out_6077984892743029865[228] = 1;
   out_6077984892743029865[229] = 0;
   out_6077984892743029865[230] = 0;
   out_6077984892743029865[231] = 0;
   out_6077984892743029865[232] = 0;
   out_6077984892743029865[233] = 0;
   out_6077984892743029865[234] = 0;
   out_6077984892743029865[235] = 0;
   out_6077984892743029865[236] = 0;
   out_6077984892743029865[237] = 0;
   out_6077984892743029865[238] = 0;
   out_6077984892743029865[239] = 0;
   out_6077984892743029865[240] = 0;
   out_6077984892743029865[241] = 0;
   out_6077984892743029865[242] = 0;
   out_6077984892743029865[243] = 0;
   out_6077984892743029865[244] = 0;
   out_6077984892743029865[245] = 0;
   out_6077984892743029865[246] = 0;
   out_6077984892743029865[247] = 1;
   out_6077984892743029865[248] = 0;
   out_6077984892743029865[249] = 0;
   out_6077984892743029865[250] = 0;
   out_6077984892743029865[251] = 0;
   out_6077984892743029865[252] = 0;
   out_6077984892743029865[253] = 0;
   out_6077984892743029865[254] = 0;
   out_6077984892743029865[255] = 0;
   out_6077984892743029865[256] = 0;
   out_6077984892743029865[257] = 0;
   out_6077984892743029865[258] = 0;
   out_6077984892743029865[259] = 0;
   out_6077984892743029865[260] = 0;
   out_6077984892743029865[261] = 0;
   out_6077984892743029865[262] = 0;
   out_6077984892743029865[263] = 0;
   out_6077984892743029865[264] = 0;
   out_6077984892743029865[265] = 0;
   out_6077984892743029865[266] = 1;
   out_6077984892743029865[267] = 0;
   out_6077984892743029865[268] = 0;
   out_6077984892743029865[269] = 0;
   out_6077984892743029865[270] = 0;
   out_6077984892743029865[271] = 0;
   out_6077984892743029865[272] = 0;
   out_6077984892743029865[273] = 0;
   out_6077984892743029865[274] = 0;
   out_6077984892743029865[275] = 0;
   out_6077984892743029865[276] = 0;
   out_6077984892743029865[277] = 0;
   out_6077984892743029865[278] = 0;
   out_6077984892743029865[279] = 0;
   out_6077984892743029865[280] = 0;
   out_6077984892743029865[281] = 0;
   out_6077984892743029865[282] = 0;
   out_6077984892743029865[283] = 0;
   out_6077984892743029865[284] = 0;
   out_6077984892743029865[285] = 1;
   out_6077984892743029865[286] = 0;
   out_6077984892743029865[287] = 0;
   out_6077984892743029865[288] = 0;
   out_6077984892743029865[289] = 0;
   out_6077984892743029865[290] = 0;
   out_6077984892743029865[291] = 0;
   out_6077984892743029865[292] = 0;
   out_6077984892743029865[293] = 0;
   out_6077984892743029865[294] = 0;
   out_6077984892743029865[295] = 0;
   out_6077984892743029865[296] = 0;
   out_6077984892743029865[297] = 0;
   out_6077984892743029865[298] = 0;
   out_6077984892743029865[299] = 0;
   out_6077984892743029865[300] = 0;
   out_6077984892743029865[301] = 0;
   out_6077984892743029865[302] = 0;
   out_6077984892743029865[303] = 0;
   out_6077984892743029865[304] = 1;
   out_6077984892743029865[305] = 0;
   out_6077984892743029865[306] = 0;
   out_6077984892743029865[307] = 0;
   out_6077984892743029865[308] = 0;
   out_6077984892743029865[309] = 0;
   out_6077984892743029865[310] = 0;
   out_6077984892743029865[311] = 0;
   out_6077984892743029865[312] = 0;
   out_6077984892743029865[313] = 0;
   out_6077984892743029865[314] = 0;
   out_6077984892743029865[315] = 0;
   out_6077984892743029865[316] = 0;
   out_6077984892743029865[317] = 0;
   out_6077984892743029865[318] = 0;
   out_6077984892743029865[319] = 0;
   out_6077984892743029865[320] = 0;
   out_6077984892743029865[321] = 0;
   out_6077984892743029865[322] = 0;
   out_6077984892743029865[323] = 1;
}
void h_4(double *state, double *unused, double *out_7953710333148623088) {
   out_7953710333148623088[0] = state[6] + state[9];
   out_7953710333148623088[1] = state[7] + state[10];
   out_7953710333148623088[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_4733805546150007712) {
   out_4733805546150007712[0] = 0;
   out_4733805546150007712[1] = 0;
   out_4733805546150007712[2] = 0;
   out_4733805546150007712[3] = 0;
   out_4733805546150007712[4] = 0;
   out_4733805546150007712[5] = 0;
   out_4733805546150007712[6] = 1;
   out_4733805546150007712[7] = 0;
   out_4733805546150007712[8] = 0;
   out_4733805546150007712[9] = 1;
   out_4733805546150007712[10] = 0;
   out_4733805546150007712[11] = 0;
   out_4733805546150007712[12] = 0;
   out_4733805546150007712[13] = 0;
   out_4733805546150007712[14] = 0;
   out_4733805546150007712[15] = 0;
   out_4733805546150007712[16] = 0;
   out_4733805546150007712[17] = 0;
   out_4733805546150007712[18] = 0;
   out_4733805546150007712[19] = 0;
   out_4733805546150007712[20] = 0;
   out_4733805546150007712[21] = 0;
   out_4733805546150007712[22] = 0;
   out_4733805546150007712[23] = 0;
   out_4733805546150007712[24] = 0;
   out_4733805546150007712[25] = 1;
   out_4733805546150007712[26] = 0;
   out_4733805546150007712[27] = 0;
   out_4733805546150007712[28] = 1;
   out_4733805546150007712[29] = 0;
   out_4733805546150007712[30] = 0;
   out_4733805546150007712[31] = 0;
   out_4733805546150007712[32] = 0;
   out_4733805546150007712[33] = 0;
   out_4733805546150007712[34] = 0;
   out_4733805546150007712[35] = 0;
   out_4733805546150007712[36] = 0;
   out_4733805546150007712[37] = 0;
   out_4733805546150007712[38] = 0;
   out_4733805546150007712[39] = 0;
   out_4733805546150007712[40] = 0;
   out_4733805546150007712[41] = 0;
   out_4733805546150007712[42] = 0;
   out_4733805546150007712[43] = 0;
   out_4733805546150007712[44] = 1;
   out_4733805546150007712[45] = 0;
   out_4733805546150007712[46] = 0;
   out_4733805546150007712[47] = 1;
   out_4733805546150007712[48] = 0;
   out_4733805546150007712[49] = 0;
   out_4733805546150007712[50] = 0;
   out_4733805546150007712[51] = 0;
   out_4733805546150007712[52] = 0;
   out_4733805546150007712[53] = 0;
}
void h_10(double *state, double *unused, double *out_8638301772534799194) {
   out_8638301772534799194[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_8638301772534799194[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_8638301772534799194[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_7550312672629139090) {
   out_7550312672629139090[0] = 0;
   out_7550312672629139090[1] = 9.8100000000000005*cos(state[1]);
   out_7550312672629139090[2] = 0;
   out_7550312672629139090[3] = 0;
   out_7550312672629139090[4] = -state[8];
   out_7550312672629139090[5] = state[7];
   out_7550312672629139090[6] = 0;
   out_7550312672629139090[7] = state[5];
   out_7550312672629139090[8] = -state[4];
   out_7550312672629139090[9] = 0;
   out_7550312672629139090[10] = 0;
   out_7550312672629139090[11] = 0;
   out_7550312672629139090[12] = 1;
   out_7550312672629139090[13] = 0;
   out_7550312672629139090[14] = 0;
   out_7550312672629139090[15] = 1;
   out_7550312672629139090[16] = 0;
   out_7550312672629139090[17] = 0;
   out_7550312672629139090[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_7550312672629139090[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_7550312672629139090[20] = 0;
   out_7550312672629139090[21] = state[8];
   out_7550312672629139090[22] = 0;
   out_7550312672629139090[23] = -state[6];
   out_7550312672629139090[24] = -state[5];
   out_7550312672629139090[25] = 0;
   out_7550312672629139090[26] = state[3];
   out_7550312672629139090[27] = 0;
   out_7550312672629139090[28] = 0;
   out_7550312672629139090[29] = 0;
   out_7550312672629139090[30] = 0;
   out_7550312672629139090[31] = 1;
   out_7550312672629139090[32] = 0;
   out_7550312672629139090[33] = 0;
   out_7550312672629139090[34] = 1;
   out_7550312672629139090[35] = 0;
   out_7550312672629139090[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_7550312672629139090[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_7550312672629139090[38] = 0;
   out_7550312672629139090[39] = -state[7];
   out_7550312672629139090[40] = state[6];
   out_7550312672629139090[41] = 0;
   out_7550312672629139090[42] = state[4];
   out_7550312672629139090[43] = -state[3];
   out_7550312672629139090[44] = 0;
   out_7550312672629139090[45] = 0;
   out_7550312672629139090[46] = 0;
   out_7550312672629139090[47] = 0;
   out_7550312672629139090[48] = 0;
   out_7550312672629139090[49] = 0;
   out_7550312672629139090[50] = 1;
   out_7550312672629139090[51] = 0;
   out_7550312672629139090[52] = 0;
   out_7550312672629139090[53] = 1;
}
void h_13(double *state, double *unused, double *out_4921048176335829394) {
   out_4921048176335829394[0] = state[3];
   out_4921048176335829394[1] = state[4];
   out_4921048176335829394[2] = state[5];
}
void H_13(double *state, double *unused, double *out_5298407465831851816) {
   out_5298407465831851816[0] = 0;
   out_5298407465831851816[1] = 0;
   out_5298407465831851816[2] = 0;
   out_5298407465831851816[3] = 1;
   out_5298407465831851816[4] = 0;
   out_5298407465831851816[5] = 0;
   out_5298407465831851816[6] = 0;
   out_5298407465831851816[7] = 0;
   out_5298407465831851816[8] = 0;
   out_5298407465831851816[9] = 0;
   out_5298407465831851816[10] = 0;
   out_5298407465831851816[11] = 0;
   out_5298407465831851816[12] = 0;
   out_5298407465831851816[13] = 0;
   out_5298407465831851816[14] = 0;
   out_5298407465831851816[15] = 0;
   out_5298407465831851816[16] = 0;
   out_5298407465831851816[17] = 0;
   out_5298407465831851816[18] = 0;
   out_5298407465831851816[19] = 0;
   out_5298407465831851816[20] = 0;
   out_5298407465831851816[21] = 0;
   out_5298407465831851816[22] = 1;
   out_5298407465831851816[23] = 0;
   out_5298407465831851816[24] = 0;
   out_5298407465831851816[25] = 0;
   out_5298407465831851816[26] = 0;
   out_5298407465831851816[27] = 0;
   out_5298407465831851816[28] = 0;
   out_5298407465831851816[29] = 0;
   out_5298407465831851816[30] = 0;
   out_5298407465831851816[31] = 0;
   out_5298407465831851816[32] = 0;
   out_5298407465831851816[33] = 0;
   out_5298407465831851816[34] = 0;
   out_5298407465831851816[35] = 0;
   out_5298407465831851816[36] = 0;
   out_5298407465831851816[37] = 0;
   out_5298407465831851816[38] = 0;
   out_5298407465831851816[39] = 0;
   out_5298407465831851816[40] = 0;
   out_5298407465831851816[41] = 1;
   out_5298407465831851816[42] = 0;
   out_5298407465831851816[43] = 0;
   out_5298407465831851816[44] = 0;
   out_5298407465831851816[45] = 0;
   out_5298407465831851816[46] = 0;
   out_5298407465831851816[47] = 0;
   out_5298407465831851816[48] = 0;
   out_5298407465831851816[49] = 0;
   out_5298407465831851816[50] = 0;
   out_5298407465831851816[51] = 0;
   out_5298407465831851816[52] = 0;
   out_5298407465831851816[53] = 0;
}
void h_14(double *state, double *unused, double *out_5016646202722718585) {
   out_5016646202722718585[0] = state[6];
   out_5016646202722718585[1] = state[7];
   out_5016646202722718585[2] = state[8];
}
void H_14(double *state, double *unused, double *out_1651017113854635416) {
   out_1651017113854635416[0] = 0;
   out_1651017113854635416[1] = 0;
   out_1651017113854635416[2] = 0;
   out_1651017113854635416[3] = 0;
   out_1651017113854635416[4] = 0;
   out_1651017113854635416[5] = 0;
   out_1651017113854635416[6] = 1;
   out_1651017113854635416[7] = 0;
   out_1651017113854635416[8] = 0;
   out_1651017113854635416[9] = 0;
   out_1651017113854635416[10] = 0;
   out_1651017113854635416[11] = 0;
   out_1651017113854635416[12] = 0;
   out_1651017113854635416[13] = 0;
   out_1651017113854635416[14] = 0;
   out_1651017113854635416[15] = 0;
   out_1651017113854635416[16] = 0;
   out_1651017113854635416[17] = 0;
   out_1651017113854635416[18] = 0;
   out_1651017113854635416[19] = 0;
   out_1651017113854635416[20] = 0;
   out_1651017113854635416[21] = 0;
   out_1651017113854635416[22] = 0;
   out_1651017113854635416[23] = 0;
   out_1651017113854635416[24] = 0;
   out_1651017113854635416[25] = 1;
   out_1651017113854635416[26] = 0;
   out_1651017113854635416[27] = 0;
   out_1651017113854635416[28] = 0;
   out_1651017113854635416[29] = 0;
   out_1651017113854635416[30] = 0;
   out_1651017113854635416[31] = 0;
   out_1651017113854635416[32] = 0;
   out_1651017113854635416[33] = 0;
   out_1651017113854635416[34] = 0;
   out_1651017113854635416[35] = 0;
   out_1651017113854635416[36] = 0;
   out_1651017113854635416[37] = 0;
   out_1651017113854635416[38] = 0;
   out_1651017113854635416[39] = 0;
   out_1651017113854635416[40] = 0;
   out_1651017113854635416[41] = 0;
   out_1651017113854635416[42] = 0;
   out_1651017113854635416[43] = 0;
   out_1651017113854635416[44] = 1;
   out_1651017113854635416[45] = 0;
   out_1651017113854635416[46] = 0;
   out_1651017113854635416[47] = 0;
   out_1651017113854635416[48] = 0;
   out_1651017113854635416[49] = 0;
   out_1651017113854635416[50] = 0;
   out_1651017113854635416[51] = 0;
   out_1651017113854635416[52] = 0;
   out_1651017113854635416[53] = 0;
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
void pose_err_fun(double *nom_x, double *delta_x, double *out_2708976385256854938) {
  err_fun(nom_x, delta_x, out_2708976385256854938);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_5039075117443556308) {
  inv_err_fun(nom_x, true_x, out_5039075117443556308);
}
void pose_H_mod_fun(double *state, double *out_4768576861501722562) {
  H_mod_fun(state, out_4768576861501722562);
}
void pose_f_fun(double *state, double dt, double *out_3365426939231918965) {
  f_fun(state,  dt, out_3365426939231918965);
}
void pose_F_fun(double *state, double dt, double *out_6077984892743029865) {
  F_fun(state,  dt, out_6077984892743029865);
}
void pose_h_4(double *state, double *unused, double *out_7953710333148623088) {
  h_4(state, unused, out_7953710333148623088);
}
void pose_H_4(double *state, double *unused, double *out_4733805546150007712) {
  H_4(state, unused, out_4733805546150007712);
}
void pose_h_10(double *state, double *unused, double *out_8638301772534799194) {
  h_10(state, unused, out_8638301772534799194);
}
void pose_H_10(double *state, double *unused, double *out_7550312672629139090) {
  H_10(state, unused, out_7550312672629139090);
}
void pose_h_13(double *state, double *unused, double *out_4921048176335829394) {
  h_13(state, unused, out_4921048176335829394);
}
void pose_H_13(double *state, double *unused, double *out_5298407465831851816) {
  H_13(state, unused, out_5298407465831851816);
}
void pose_h_14(double *state, double *unused, double *out_5016646202722718585) {
  h_14(state, unused, out_5016646202722718585);
}
void pose_H_14(double *state, double *unused, double *out_1651017113854635416) {
  H_14(state, unused, out_1651017113854635416);
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
