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
void err_fun(double *nom_x, double *delta_x, double *out_264984234156022510) {
   out_264984234156022510[0] = delta_x[0] + nom_x[0];
   out_264984234156022510[1] = delta_x[1] + nom_x[1];
   out_264984234156022510[2] = delta_x[2] + nom_x[2];
   out_264984234156022510[3] = delta_x[3] + nom_x[3];
   out_264984234156022510[4] = delta_x[4] + nom_x[4];
   out_264984234156022510[5] = delta_x[5] + nom_x[5];
   out_264984234156022510[6] = delta_x[6] + nom_x[6];
   out_264984234156022510[7] = delta_x[7] + nom_x[7];
   out_264984234156022510[8] = delta_x[8] + nom_x[8];
   out_264984234156022510[9] = delta_x[9] + nom_x[9];
   out_264984234156022510[10] = delta_x[10] + nom_x[10];
   out_264984234156022510[11] = delta_x[11] + nom_x[11];
   out_264984234156022510[12] = delta_x[12] + nom_x[12];
   out_264984234156022510[13] = delta_x[13] + nom_x[13];
   out_264984234156022510[14] = delta_x[14] + nom_x[14];
   out_264984234156022510[15] = delta_x[15] + nom_x[15];
   out_264984234156022510[16] = delta_x[16] + nom_x[16];
   out_264984234156022510[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_4459356063444070539) {
   out_4459356063444070539[0] = -nom_x[0] + true_x[0];
   out_4459356063444070539[1] = -nom_x[1] + true_x[1];
   out_4459356063444070539[2] = -nom_x[2] + true_x[2];
   out_4459356063444070539[3] = -nom_x[3] + true_x[3];
   out_4459356063444070539[4] = -nom_x[4] + true_x[4];
   out_4459356063444070539[5] = -nom_x[5] + true_x[5];
   out_4459356063444070539[6] = -nom_x[6] + true_x[6];
   out_4459356063444070539[7] = -nom_x[7] + true_x[7];
   out_4459356063444070539[8] = -nom_x[8] + true_x[8];
   out_4459356063444070539[9] = -nom_x[9] + true_x[9];
   out_4459356063444070539[10] = -nom_x[10] + true_x[10];
   out_4459356063444070539[11] = -nom_x[11] + true_x[11];
   out_4459356063444070539[12] = -nom_x[12] + true_x[12];
   out_4459356063444070539[13] = -nom_x[13] + true_x[13];
   out_4459356063444070539[14] = -nom_x[14] + true_x[14];
   out_4459356063444070539[15] = -nom_x[15] + true_x[15];
   out_4459356063444070539[16] = -nom_x[16] + true_x[16];
   out_4459356063444070539[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_7005986214264108234) {
   out_7005986214264108234[0] = 1.0;
   out_7005986214264108234[1] = 0.0;
   out_7005986214264108234[2] = 0.0;
   out_7005986214264108234[3] = 0.0;
   out_7005986214264108234[4] = 0.0;
   out_7005986214264108234[5] = 0.0;
   out_7005986214264108234[6] = 0.0;
   out_7005986214264108234[7] = 0.0;
   out_7005986214264108234[8] = 0.0;
   out_7005986214264108234[9] = 0.0;
   out_7005986214264108234[10] = 0.0;
   out_7005986214264108234[11] = 0.0;
   out_7005986214264108234[12] = 0.0;
   out_7005986214264108234[13] = 0.0;
   out_7005986214264108234[14] = 0.0;
   out_7005986214264108234[15] = 0.0;
   out_7005986214264108234[16] = 0.0;
   out_7005986214264108234[17] = 0.0;
   out_7005986214264108234[18] = 0.0;
   out_7005986214264108234[19] = 1.0;
   out_7005986214264108234[20] = 0.0;
   out_7005986214264108234[21] = 0.0;
   out_7005986214264108234[22] = 0.0;
   out_7005986214264108234[23] = 0.0;
   out_7005986214264108234[24] = 0.0;
   out_7005986214264108234[25] = 0.0;
   out_7005986214264108234[26] = 0.0;
   out_7005986214264108234[27] = 0.0;
   out_7005986214264108234[28] = 0.0;
   out_7005986214264108234[29] = 0.0;
   out_7005986214264108234[30] = 0.0;
   out_7005986214264108234[31] = 0.0;
   out_7005986214264108234[32] = 0.0;
   out_7005986214264108234[33] = 0.0;
   out_7005986214264108234[34] = 0.0;
   out_7005986214264108234[35] = 0.0;
   out_7005986214264108234[36] = 0.0;
   out_7005986214264108234[37] = 0.0;
   out_7005986214264108234[38] = 1.0;
   out_7005986214264108234[39] = 0.0;
   out_7005986214264108234[40] = 0.0;
   out_7005986214264108234[41] = 0.0;
   out_7005986214264108234[42] = 0.0;
   out_7005986214264108234[43] = 0.0;
   out_7005986214264108234[44] = 0.0;
   out_7005986214264108234[45] = 0.0;
   out_7005986214264108234[46] = 0.0;
   out_7005986214264108234[47] = 0.0;
   out_7005986214264108234[48] = 0.0;
   out_7005986214264108234[49] = 0.0;
   out_7005986214264108234[50] = 0.0;
   out_7005986214264108234[51] = 0.0;
   out_7005986214264108234[52] = 0.0;
   out_7005986214264108234[53] = 0.0;
   out_7005986214264108234[54] = 0.0;
   out_7005986214264108234[55] = 0.0;
   out_7005986214264108234[56] = 0.0;
   out_7005986214264108234[57] = 1.0;
   out_7005986214264108234[58] = 0.0;
   out_7005986214264108234[59] = 0.0;
   out_7005986214264108234[60] = 0.0;
   out_7005986214264108234[61] = 0.0;
   out_7005986214264108234[62] = 0.0;
   out_7005986214264108234[63] = 0.0;
   out_7005986214264108234[64] = 0.0;
   out_7005986214264108234[65] = 0.0;
   out_7005986214264108234[66] = 0.0;
   out_7005986214264108234[67] = 0.0;
   out_7005986214264108234[68] = 0.0;
   out_7005986214264108234[69] = 0.0;
   out_7005986214264108234[70] = 0.0;
   out_7005986214264108234[71] = 0.0;
   out_7005986214264108234[72] = 0.0;
   out_7005986214264108234[73] = 0.0;
   out_7005986214264108234[74] = 0.0;
   out_7005986214264108234[75] = 0.0;
   out_7005986214264108234[76] = 1.0;
   out_7005986214264108234[77] = 0.0;
   out_7005986214264108234[78] = 0.0;
   out_7005986214264108234[79] = 0.0;
   out_7005986214264108234[80] = 0.0;
   out_7005986214264108234[81] = 0.0;
   out_7005986214264108234[82] = 0.0;
   out_7005986214264108234[83] = 0.0;
   out_7005986214264108234[84] = 0.0;
   out_7005986214264108234[85] = 0.0;
   out_7005986214264108234[86] = 0.0;
   out_7005986214264108234[87] = 0.0;
   out_7005986214264108234[88] = 0.0;
   out_7005986214264108234[89] = 0.0;
   out_7005986214264108234[90] = 0.0;
   out_7005986214264108234[91] = 0.0;
   out_7005986214264108234[92] = 0.0;
   out_7005986214264108234[93] = 0.0;
   out_7005986214264108234[94] = 0.0;
   out_7005986214264108234[95] = 1.0;
   out_7005986214264108234[96] = 0.0;
   out_7005986214264108234[97] = 0.0;
   out_7005986214264108234[98] = 0.0;
   out_7005986214264108234[99] = 0.0;
   out_7005986214264108234[100] = 0.0;
   out_7005986214264108234[101] = 0.0;
   out_7005986214264108234[102] = 0.0;
   out_7005986214264108234[103] = 0.0;
   out_7005986214264108234[104] = 0.0;
   out_7005986214264108234[105] = 0.0;
   out_7005986214264108234[106] = 0.0;
   out_7005986214264108234[107] = 0.0;
   out_7005986214264108234[108] = 0.0;
   out_7005986214264108234[109] = 0.0;
   out_7005986214264108234[110] = 0.0;
   out_7005986214264108234[111] = 0.0;
   out_7005986214264108234[112] = 0.0;
   out_7005986214264108234[113] = 0.0;
   out_7005986214264108234[114] = 1.0;
   out_7005986214264108234[115] = 0.0;
   out_7005986214264108234[116] = 0.0;
   out_7005986214264108234[117] = 0.0;
   out_7005986214264108234[118] = 0.0;
   out_7005986214264108234[119] = 0.0;
   out_7005986214264108234[120] = 0.0;
   out_7005986214264108234[121] = 0.0;
   out_7005986214264108234[122] = 0.0;
   out_7005986214264108234[123] = 0.0;
   out_7005986214264108234[124] = 0.0;
   out_7005986214264108234[125] = 0.0;
   out_7005986214264108234[126] = 0.0;
   out_7005986214264108234[127] = 0.0;
   out_7005986214264108234[128] = 0.0;
   out_7005986214264108234[129] = 0.0;
   out_7005986214264108234[130] = 0.0;
   out_7005986214264108234[131] = 0.0;
   out_7005986214264108234[132] = 0.0;
   out_7005986214264108234[133] = 1.0;
   out_7005986214264108234[134] = 0.0;
   out_7005986214264108234[135] = 0.0;
   out_7005986214264108234[136] = 0.0;
   out_7005986214264108234[137] = 0.0;
   out_7005986214264108234[138] = 0.0;
   out_7005986214264108234[139] = 0.0;
   out_7005986214264108234[140] = 0.0;
   out_7005986214264108234[141] = 0.0;
   out_7005986214264108234[142] = 0.0;
   out_7005986214264108234[143] = 0.0;
   out_7005986214264108234[144] = 0.0;
   out_7005986214264108234[145] = 0.0;
   out_7005986214264108234[146] = 0.0;
   out_7005986214264108234[147] = 0.0;
   out_7005986214264108234[148] = 0.0;
   out_7005986214264108234[149] = 0.0;
   out_7005986214264108234[150] = 0.0;
   out_7005986214264108234[151] = 0.0;
   out_7005986214264108234[152] = 1.0;
   out_7005986214264108234[153] = 0.0;
   out_7005986214264108234[154] = 0.0;
   out_7005986214264108234[155] = 0.0;
   out_7005986214264108234[156] = 0.0;
   out_7005986214264108234[157] = 0.0;
   out_7005986214264108234[158] = 0.0;
   out_7005986214264108234[159] = 0.0;
   out_7005986214264108234[160] = 0.0;
   out_7005986214264108234[161] = 0.0;
   out_7005986214264108234[162] = 0.0;
   out_7005986214264108234[163] = 0.0;
   out_7005986214264108234[164] = 0.0;
   out_7005986214264108234[165] = 0.0;
   out_7005986214264108234[166] = 0.0;
   out_7005986214264108234[167] = 0.0;
   out_7005986214264108234[168] = 0.0;
   out_7005986214264108234[169] = 0.0;
   out_7005986214264108234[170] = 0.0;
   out_7005986214264108234[171] = 1.0;
   out_7005986214264108234[172] = 0.0;
   out_7005986214264108234[173] = 0.0;
   out_7005986214264108234[174] = 0.0;
   out_7005986214264108234[175] = 0.0;
   out_7005986214264108234[176] = 0.0;
   out_7005986214264108234[177] = 0.0;
   out_7005986214264108234[178] = 0.0;
   out_7005986214264108234[179] = 0.0;
   out_7005986214264108234[180] = 0.0;
   out_7005986214264108234[181] = 0.0;
   out_7005986214264108234[182] = 0.0;
   out_7005986214264108234[183] = 0.0;
   out_7005986214264108234[184] = 0.0;
   out_7005986214264108234[185] = 0.0;
   out_7005986214264108234[186] = 0.0;
   out_7005986214264108234[187] = 0.0;
   out_7005986214264108234[188] = 0.0;
   out_7005986214264108234[189] = 0.0;
   out_7005986214264108234[190] = 1.0;
   out_7005986214264108234[191] = 0.0;
   out_7005986214264108234[192] = 0.0;
   out_7005986214264108234[193] = 0.0;
   out_7005986214264108234[194] = 0.0;
   out_7005986214264108234[195] = 0.0;
   out_7005986214264108234[196] = 0.0;
   out_7005986214264108234[197] = 0.0;
   out_7005986214264108234[198] = 0.0;
   out_7005986214264108234[199] = 0.0;
   out_7005986214264108234[200] = 0.0;
   out_7005986214264108234[201] = 0.0;
   out_7005986214264108234[202] = 0.0;
   out_7005986214264108234[203] = 0.0;
   out_7005986214264108234[204] = 0.0;
   out_7005986214264108234[205] = 0.0;
   out_7005986214264108234[206] = 0.0;
   out_7005986214264108234[207] = 0.0;
   out_7005986214264108234[208] = 0.0;
   out_7005986214264108234[209] = 1.0;
   out_7005986214264108234[210] = 0.0;
   out_7005986214264108234[211] = 0.0;
   out_7005986214264108234[212] = 0.0;
   out_7005986214264108234[213] = 0.0;
   out_7005986214264108234[214] = 0.0;
   out_7005986214264108234[215] = 0.0;
   out_7005986214264108234[216] = 0.0;
   out_7005986214264108234[217] = 0.0;
   out_7005986214264108234[218] = 0.0;
   out_7005986214264108234[219] = 0.0;
   out_7005986214264108234[220] = 0.0;
   out_7005986214264108234[221] = 0.0;
   out_7005986214264108234[222] = 0.0;
   out_7005986214264108234[223] = 0.0;
   out_7005986214264108234[224] = 0.0;
   out_7005986214264108234[225] = 0.0;
   out_7005986214264108234[226] = 0.0;
   out_7005986214264108234[227] = 0.0;
   out_7005986214264108234[228] = 1.0;
   out_7005986214264108234[229] = 0.0;
   out_7005986214264108234[230] = 0.0;
   out_7005986214264108234[231] = 0.0;
   out_7005986214264108234[232] = 0.0;
   out_7005986214264108234[233] = 0.0;
   out_7005986214264108234[234] = 0.0;
   out_7005986214264108234[235] = 0.0;
   out_7005986214264108234[236] = 0.0;
   out_7005986214264108234[237] = 0.0;
   out_7005986214264108234[238] = 0.0;
   out_7005986214264108234[239] = 0.0;
   out_7005986214264108234[240] = 0.0;
   out_7005986214264108234[241] = 0.0;
   out_7005986214264108234[242] = 0.0;
   out_7005986214264108234[243] = 0.0;
   out_7005986214264108234[244] = 0.0;
   out_7005986214264108234[245] = 0.0;
   out_7005986214264108234[246] = 0.0;
   out_7005986214264108234[247] = 1.0;
   out_7005986214264108234[248] = 0.0;
   out_7005986214264108234[249] = 0.0;
   out_7005986214264108234[250] = 0.0;
   out_7005986214264108234[251] = 0.0;
   out_7005986214264108234[252] = 0.0;
   out_7005986214264108234[253] = 0.0;
   out_7005986214264108234[254] = 0.0;
   out_7005986214264108234[255] = 0.0;
   out_7005986214264108234[256] = 0.0;
   out_7005986214264108234[257] = 0.0;
   out_7005986214264108234[258] = 0.0;
   out_7005986214264108234[259] = 0.0;
   out_7005986214264108234[260] = 0.0;
   out_7005986214264108234[261] = 0.0;
   out_7005986214264108234[262] = 0.0;
   out_7005986214264108234[263] = 0.0;
   out_7005986214264108234[264] = 0.0;
   out_7005986214264108234[265] = 0.0;
   out_7005986214264108234[266] = 1.0;
   out_7005986214264108234[267] = 0.0;
   out_7005986214264108234[268] = 0.0;
   out_7005986214264108234[269] = 0.0;
   out_7005986214264108234[270] = 0.0;
   out_7005986214264108234[271] = 0.0;
   out_7005986214264108234[272] = 0.0;
   out_7005986214264108234[273] = 0.0;
   out_7005986214264108234[274] = 0.0;
   out_7005986214264108234[275] = 0.0;
   out_7005986214264108234[276] = 0.0;
   out_7005986214264108234[277] = 0.0;
   out_7005986214264108234[278] = 0.0;
   out_7005986214264108234[279] = 0.0;
   out_7005986214264108234[280] = 0.0;
   out_7005986214264108234[281] = 0.0;
   out_7005986214264108234[282] = 0.0;
   out_7005986214264108234[283] = 0.0;
   out_7005986214264108234[284] = 0.0;
   out_7005986214264108234[285] = 1.0;
   out_7005986214264108234[286] = 0.0;
   out_7005986214264108234[287] = 0.0;
   out_7005986214264108234[288] = 0.0;
   out_7005986214264108234[289] = 0.0;
   out_7005986214264108234[290] = 0.0;
   out_7005986214264108234[291] = 0.0;
   out_7005986214264108234[292] = 0.0;
   out_7005986214264108234[293] = 0.0;
   out_7005986214264108234[294] = 0.0;
   out_7005986214264108234[295] = 0.0;
   out_7005986214264108234[296] = 0.0;
   out_7005986214264108234[297] = 0.0;
   out_7005986214264108234[298] = 0.0;
   out_7005986214264108234[299] = 0.0;
   out_7005986214264108234[300] = 0.0;
   out_7005986214264108234[301] = 0.0;
   out_7005986214264108234[302] = 0.0;
   out_7005986214264108234[303] = 0.0;
   out_7005986214264108234[304] = 1.0;
   out_7005986214264108234[305] = 0.0;
   out_7005986214264108234[306] = 0.0;
   out_7005986214264108234[307] = 0.0;
   out_7005986214264108234[308] = 0.0;
   out_7005986214264108234[309] = 0.0;
   out_7005986214264108234[310] = 0.0;
   out_7005986214264108234[311] = 0.0;
   out_7005986214264108234[312] = 0.0;
   out_7005986214264108234[313] = 0.0;
   out_7005986214264108234[314] = 0.0;
   out_7005986214264108234[315] = 0.0;
   out_7005986214264108234[316] = 0.0;
   out_7005986214264108234[317] = 0.0;
   out_7005986214264108234[318] = 0.0;
   out_7005986214264108234[319] = 0.0;
   out_7005986214264108234[320] = 0.0;
   out_7005986214264108234[321] = 0.0;
   out_7005986214264108234[322] = 0.0;
   out_7005986214264108234[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_4717377945151750388) {
   out_4717377945151750388[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_4717377945151750388[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_4717377945151750388[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_4717377945151750388[3] = dt*state[12] + state[3];
   out_4717377945151750388[4] = dt*state[13] + state[4];
   out_4717377945151750388[5] = dt*state[14] + state[5];
   out_4717377945151750388[6] = state[6];
   out_4717377945151750388[7] = state[7];
   out_4717377945151750388[8] = state[8];
   out_4717377945151750388[9] = state[9];
   out_4717377945151750388[10] = state[10];
   out_4717377945151750388[11] = state[11];
   out_4717377945151750388[12] = state[12];
   out_4717377945151750388[13] = state[13];
   out_4717377945151750388[14] = state[14];
   out_4717377945151750388[15] = state[15];
   out_4717377945151750388[16] = state[16];
   out_4717377945151750388[17] = state[17];
}
void F_fun(double *state, double dt, double *out_4729405661658211402) {
   out_4729405661658211402[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_4729405661658211402[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_4729405661658211402[2] = 0;
   out_4729405661658211402[3] = 0;
   out_4729405661658211402[4] = 0;
   out_4729405661658211402[5] = 0;
   out_4729405661658211402[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_4729405661658211402[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_4729405661658211402[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_4729405661658211402[9] = 0;
   out_4729405661658211402[10] = 0;
   out_4729405661658211402[11] = 0;
   out_4729405661658211402[12] = 0;
   out_4729405661658211402[13] = 0;
   out_4729405661658211402[14] = 0;
   out_4729405661658211402[15] = 0;
   out_4729405661658211402[16] = 0;
   out_4729405661658211402[17] = 0;
   out_4729405661658211402[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_4729405661658211402[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_4729405661658211402[20] = 0;
   out_4729405661658211402[21] = 0;
   out_4729405661658211402[22] = 0;
   out_4729405661658211402[23] = 0;
   out_4729405661658211402[24] = 0;
   out_4729405661658211402[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_4729405661658211402[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_4729405661658211402[27] = 0;
   out_4729405661658211402[28] = 0;
   out_4729405661658211402[29] = 0;
   out_4729405661658211402[30] = 0;
   out_4729405661658211402[31] = 0;
   out_4729405661658211402[32] = 0;
   out_4729405661658211402[33] = 0;
   out_4729405661658211402[34] = 0;
   out_4729405661658211402[35] = 0;
   out_4729405661658211402[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_4729405661658211402[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_4729405661658211402[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_4729405661658211402[39] = 0;
   out_4729405661658211402[40] = 0;
   out_4729405661658211402[41] = 0;
   out_4729405661658211402[42] = 0;
   out_4729405661658211402[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_4729405661658211402[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_4729405661658211402[45] = 0;
   out_4729405661658211402[46] = 0;
   out_4729405661658211402[47] = 0;
   out_4729405661658211402[48] = 0;
   out_4729405661658211402[49] = 0;
   out_4729405661658211402[50] = 0;
   out_4729405661658211402[51] = 0;
   out_4729405661658211402[52] = 0;
   out_4729405661658211402[53] = 0;
   out_4729405661658211402[54] = 0;
   out_4729405661658211402[55] = 0;
   out_4729405661658211402[56] = 0;
   out_4729405661658211402[57] = 1;
   out_4729405661658211402[58] = 0;
   out_4729405661658211402[59] = 0;
   out_4729405661658211402[60] = 0;
   out_4729405661658211402[61] = 0;
   out_4729405661658211402[62] = 0;
   out_4729405661658211402[63] = 0;
   out_4729405661658211402[64] = 0;
   out_4729405661658211402[65] = 0;
   out_4729405661658211402[66] = dt;
   out_4729405661658211402[67] = 0;
   out_4729405661658211402[68] = 0;
   out_4729405661658211402[69] = 0;
   out_4729405661658211402[70] = 0;
   out_4729405661658211402[71] = 0;
   out_4729405661658211402[72] = 0;
   out_4729405661658211402[73] = 0;
   out_4729405661658211402[74] = 0;
   out_4729405661658211402[75] = 0;
   out_4729405661658211402[76] = 1;
   out_4729405661658211402[77] = 0;
   out_4729405661658211402[78] = 0;
   out_4729405661658211402[79] = 0;
   out_4729405661658211402[80] = 0;
   out_4729405661658211402[81] = 0;
   out_4729405661658211402[82] = 0;
   out_4729405661658211402[83] = 0;
   out_4729405661658211402[84] = 0;
   out_4729405661658211402[85] = dt;
   out_4729405661658211402[86] = 0;
   out_4729405661658211402[87] = 0;
   out_4729405661658211402[88] = 0;
   out_4729405661658211402[89] = 0;
   out_4729405661658211402[90] = 0;
   out_4729405661658211402[91] = 0;
   out_4729405661658211402[92] = 0;
   out_4729405661658211402[93] = 0;
   out_4729405661658211402[94] = 0;
   out_4729405661658211402[95] = 1;
   out_4729405661658211402[96] = 0;
   out_4729405661658211402[97] = 0;
   out_4729405661658211402[98] = 0;
   out_4729405661658211402[99] = 0;
   out_4729405661658211402[100] = 0;
   out_4729405661658211402[101] = 0;
   out_4729405661658211402[102] = 0;
   out_4729405661658211402[103] = 0;
   out_4729405661658211402[104] = dt;
   out_4729405661658211402[105] = 0;
   out_4729405661658211402[106] = 0;
   out_4729405661658211402[107] = 0;
   out_4729405661658211402[108] = 0;
   out_4729405661658211402[109] = 0;
   out_4729405661658211402[110] = 0;
   out_4729405661658211402[111] = 0;
   out_4729405661658211402[112] = 0;
   out_4729405661658211402[113] = 0;
   out_4729405661658211402[114] = 1;
   out_4729405661658211402[115] = 0;
   out_4729405661658211402[116] = 0;
   out_4729405661658211402[117] = 0;
   out_4729405661658211402[118] = 0;
   out_4729405661658211402[119] = 0;
   out_4729405661658211402[120] = 0;
   out_4729405661658211402[121] = 0;
   out_4729405661658211402[122] = 0;
   out_4729405661658211402[123] = 0;
   out_4729405661658211402[124] = 0;
   out_4729405661658211402[125] = 0;
   out_4729405661658211402[126] = 0;
   out_4729405661658211402[127] = 0;
   out_4729405661658211402[128] = 0;
   out_4729405661658211402[129] = 0;
   out_4729405661658211402[130] = 0;
   out_4729405661658211402[131] = 0;
   out_4729405661658211402[132] = 0;
   out_4729405661658211402[133] = 1;
   out_4729405661658211402[134] = 0;
   out_4729405661658211402[135] = 0;
   out_4729405661658211402[136] = 0;
   out_4729405661658211402[137] = 0;
   out_4729405661658211402[138] = 0;
   out_4729405661658211402[139] = 0;
   out_4729405661658211402[140] = 0;
   out_4729405661658211402[141] = 0;
   out_4729405661658211402[142] = 0;
   out_4729405661658211402[143] = 0;
   out_4729405661658211402[144] = 0;
   out_4729405661658211402[145] = 0;
   out_4729405661658211402[146] = 0;
   out_4729405661658211402[147] = 0;
   out_4729405661658211402[148] = 0;
   out_4729405661658211402[149] = 0;
   out_4729405661658211402[150] = 0;
   out_4729405661658211402[151] = 0;
   out_4729405661658211402[152] = 1;
   out_4729405661658211402[153] = 0;
   out_4729405661658211402[154] = 0;
   out_4729405661658211402[155] = 0;
   out_4729405661658211402[156] = 0;
   out_4729405661658211402[157] = 0;
   out_4729405661658211402[158] = 0;
   out_4729405661658211402[159] = 0;
   out_4729405661658211402[160] = 0;
   out_4729405661658211402[161] = 0;
   out_4729405661658211402[162] = 0;
   out_4729405661658211402[163] = 0;
   out_4729405661658211402[164] = 0;
   out_4729405661658211402[165] = 0;
   out_4729405661658211402[166] = 0;
   out_4729405661658211402[167] = 0;
   out_4729405661658211402[168] = 0;
   out_4729405661658211402[169] = 0;
   out_4729405661658211402[170] = 0;
   out_4729405661658211402[171] = 1;
   out_4729405661658211402[172] = 0;
   out_4729405661658211402[173] = 0;
   out_4729405661658211402[174] = 0;
   out_4729405661658211402[175] = 0;
   out_4729405661658211402[176] = 0;
   out_4729405661658211402[177] = 0;
   out_4729405661658211402[178] = 0;
   out_4729405661658211402[179] = 0;
   out_4729405661658211402[180] = 0;
   out_4729405661658211402[181] = 0;
   out_4729405661658211402[182] = 0;
   out_4729405661658211402[183] = 0;
   out_4729405661658211402[184] = 0;
   out_4729405661658211402[185] = 0;
   out_4729405661658211402[186] = 0;
   out_4729405661658211402[187] = 0;
   out_4729405661658211402[188] = 0;
   out_4729405661658211402[189] = 0;
   out_4729405661658211402[190] = 1;
   out_4729405661658211402[191] = 0;
   out_4729405661658211402[192] = 0;
   out_4729405661658211402[193] = 0;
   out_4729405661658211402[194] = 0;
   out_4729405661658211402[195] = 0;
   out_4729405661658211402[196] = 0;
   out_4729405661658211402[197] = 0;
   out_4729405661658211402[198] = 0;
   out_4729405661658211402[199] = 0;
   out_4729405661658211402[200] = 0;
   out_4729405661658211402[201] = 0;
   out_4729405661658211402[202] = 0;
   out_4729405661658211402[203] = 0;
   out_4729405661658211402[204] = 0;
   out_4729405661658211402[205] = 0;
   out_4729405661658211402[206] = 0;
   out_4729405661658211402[207] = 0;
   out_4729405661658211402[208] = 0;
   out_4729405661658211402[209] = 1;
   out_4729405661658211402[210] = 0;
   out_4729405661658211402[211] = 0;
   out_4729405661658211402[212] = 0;
   out_4729405661658211402[213] = 0;
   out_4729405661658211402[214] = 0;
   out_4729405661658211402[215] = 0;
   out_4729405661658211402[216] = 0;
   out_4729405661658211402[217] = 0;
   out_4729405661658211402[218] = 0;
   out_4729405661658211402[219] = 0;
   out_4729405661658211402[220] = 0;
   out_4729405661658211402[221] = 0;
   out_4729405661658211402[222] = 0;
   out_4729405661658211402[223] = 0;
   out_4729405661658211402[224] = 0;
   out_4729405661658211402[225] = 0;
   out_4729405661658211402[226] = 0;
   out_4729405661658211402[227] = 0;
   out_4729405661658211402[228] = 1;
   out_4729405661658211402[229] = 0;
   out_4729405661658211402[230] = 0;
   out_4729405661658211402[231] = 0;
   out_4729405661658211402[232] = 0;
   out_4729405661658211402[233] = 0;
   out_4729405661658211402[234] = 0;
   out_4729405661658211402[235] = 0;
   out_4729405661658211402[236] = 0;
   out_4729405661658211402[237] = 0;
   out_4729405661658211402[238] = 0;
   out_4729405661658211402[239] = 0;
   out_4729405661658211402[240] = 0;
   out_4729405661658211402[241] = 0;
   out_4729405661658211402[242] = 0;
   out_4729405661658211402[243] = 0;
   out_4729405661658211402[244] = 0;
   out_4729405661658211402[245] = 0;
   out_4729405661658211402[246] = 0;
   out_4729405661658211402[247] = 1;
   out_4729405661658211402[248] = 0;
   out_4729405661658211402[249] = 0;
   out_4729405661658211402[250] = 0;
   out_4729405661658211402[251] = 0;
   out_4729405661658211402[252] = 0;
   out_4729405661658211402[253] = 0;
   out_4729405661658211402[254] = 0;
   out_4729405661658211402[255] = 0;
   out_4729405661658211402[256] = 0;
   out_4729405661658211402[257] = 0;
   out_4729405661658211402[258] = 0;
   out_4729405661658211402[259] = 0;
   out_4729405661658211402[260] = 0;
   out_4729405661658211402[261] = 0;
   out_4729405661658211402[262] = 0;
   out_4729405661658211402[263] = 0;
   out_4729405661658211402[264] = 0;
   out_4729405661658211402[265] = 0;
   out_4729405661658211402[266] = 1;
   out_4729405661658211402[267] = 0;
   out_4729405661658211402[268] = 0;
   out_4729405661658211402[269] = 0;
   out_4729405661658211402[270] = 0;
   out_4729405661658211402[271] = 0;
   out_4729405661658211402[272] = 0;
   out_4729405661658211402[273] = 0;
   out_4729405661658211402[274] = 0;
   out_4729405661658211402[275] = 0;
   out_4729405661658211402[276] = 0;
   out_4729405661658211402[277] = 0;
   out_4729405661658211402[278] = 0;
   out_4729405661658211402[279] = 0;
   out_4729405661658211402[280] = 0;
   out_4729405661658211402[281] = 0;
   out_4729405661658211402[282] = 0;
   out_4729405661658211402[283] = 0;
   out_4729405661658211402[284] = 0;
   out_4729405661658211402[285] = 1;
   out_4729405661658211402[286] = 0;
   out_4729405661658211402[287] = 0;
   out_4729405661658211402[288] = 0;
   out_4729405661658211402[289] = 0;
   out_4729405661658211402[290] = 0;
   out_4729405661658211402[291] = 0;
   out_4729405661658211402[292] = 0;
   out_4729405661658211402[293] = 0;
   out_4729405661658211402[294] = 0;
   out_4729405661658211402[295] = 0;
   out_4729405661658211402[296] = 0;
   out_4729405661658211402[297] = 0;
   out_4729405661658211402[298] = 0;
   out_4729405661658211402[299] = 0;
   out_4729405661658211402[300] = 0;
   out_4729405661658211402[301] = 0;
   out_4729405661658211402[302] = 0;
   out_4729405661658211402[303] = 0;
   out_4729405661658211402[304] = 1;
   out_4729405661658211402[305] = 0;
   out_4729405661658211402[306] = 0;
   out_4729405661658211402[307] = 0;
   out_4729405661658211402[308] = 0;
   out_4729405661658211402[309] = 0;
   out_4729405661658211402[310] = 0;
   out_4729405661658211402[311] = 0;
   out_4729405661658211402[312] = 0;
   out_4729405661658211402[313] = 0;
   out_4729405661658211402[314] = 0;
   out_4729405661658211402[315] = 0;
   out_4729405661658211402[316] = 0;
   out_4729405661658211402[317] = 0;
   out_4729405661658211402[318] = 0;
   out_4729405661658211402[319] = 0;
   out_4729405661658211402[320] = 0;
   out_4729405661658211402[321] = 0;
   out_4729405661658211402[322] = 0;
   out_4729405661658211402[323] = 1;
}
void h_4(double *state, double *unused, double *out_5738722976826185665) {
   out_5738722976826185665[0] = state[6] + state[9];
   out_5738722976826185665[1] = state[7] + state[10];
   out_5738722976826185665[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_8862099202367372115) {
   out_8862099202367372115[0] = 0;
   out_8862099202367372115[1] = 0;
   out_8862099202367372115[2] = 0;
   out_8862099202367372115[3] = 0;
   out_8862099202367372115[4] = 0;
   out_8862099202367372115[5] = 0;
   out_8862099202367372115[6] = 1;
   out_8862099202367372115[7] = 0;
   out_8862099202367372115[8] = 0;
   out_8862099202367372115[9] = 1;
   out_8862099202367372115[10] = 0;
   out_8862099202367372115[11] = 0;
   out_8862099202367372115[12] = 0;
   out_8862099202367372115[13] = 0;
   out_8862099202367372115[14] = 0;
   out_8862099202367372115[15] = 0;
   out_8862099202367372115[16] = 0;
   out_8862099202367372115[17] = 0;
   out_8862099202367372115[18] = 0;
   out_8862099202367372115[19] = 0;
   out_8862099202367372115[20] = 0;
   out_8862099202367372115[21] = 0;
   out_8862099202367372115[22] = 0;
   out_8862099202367372115[23] = 0;
   out_8862099202367372115[24] = 0;
   out_8862099202367372115[25] = 1;
   out_8862099202367372115[26] = 0;
   out_8862099202367372115[27] = 0;
   out_8862099202367372115[28] = 1;
   out_8862099202367372115[29] = 0;
   out_8862099202367372115[30] = 0;
   out_8862099202367372115[31] = 0;
   out_8862099202367372115[32] = 0;
   out_8862099202367372115[33] = 0;
   out_8862099202367372115[34] = 0;
   out_8862099202367372115[35] = 0;
   out_8862099202367372115[36] = 0;
   out_8862099202367372115[37] = 0;
   out_8862099202367372115[38] = 0;
   out_8862099202367372115[39] = 0;
   out_8862099202367372115[40] = 0;
   out_8862099202367372115[41] = 0;
   out_8862099202367372115[42] = 0;
   out_8862099202367372115[43] = 0;
   out_8862099202367372115[44] = 1;
   out_8862099202367372115[45] = 0;
   out_8862099202367372115[46] = 0;
   out_8862099202367372115[47] = 1;
   out_8862099202367372115[48] = 0;
   out_8862099202367372115[49] = 0;
   out_8862099202367372115[50] = 0;
   out_8862099202367372115[51] = 0;
   out_8862099202367372115[52] = 0;
   out_8862099202367372115[53] = 0;
}
void h_10(double *state, double *unused, double *out_2388008800197743067) {
   out_2388008800197743067[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_2388008800197743067[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_2388008800197743067[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_8909533314766452476) {
   out_8909533314766452476[0] = 0;
   out_8909533314766452476[1] = 9.8100000000000005*cos(state[1]);
   out_8909533314766452476[2] = 0;
   out_8909533314766452476[3] = 0;
   out_8909533314766452476[4] = -state[8];
   out_8909533314766452476[5] = state[7];
   out_8909533314766452476[6] = 0;
   out_8909533314766452476[7] = state[5];
   out_8909533314766452476[8] = -state[4];
   out_8909533314766452476[9] = 0;
   out_8909533314766452476[10] = 0;
   out_8909533314766452476[11] = 0;
   out_8909533314766452476[12] = 1;
   out_8909533314766452476[13] = 0;
   out_8909533314766452476[14] = 0;
   out_8909533314766452476[15] = 1;
   out_8909533314766452476[16] = 0;
   out_8909533314766452476[17] = 0;
   out_8909533314766452476[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_8909533314766452476[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_8909533314766452476[20] = 0;
   out_8909533314766452476[21] = state[8];
   out_8909533314766452476[22] = 0;
   out_8909533314766452476[23] = -state[6];
   out_8909533314766452476[24] = -state[5];
   out_8909533314766452476[25] = 0;
   out_8909533314766452476[26] = state[3];
   out_8909533314766452476[27] = 0;
   out_8909533314766452476[28] = 0;
   out_8909533314766452476[29] = 0;
   out_8909533314766452476[30] = 0;
   out_8909533314766452476[31] = 1;
   out_8909533314766452476[32] = 0;
   out_8909533314766452476[33] = 0;
   out_8909533314766452476[34] = 1;
   out_8909533314766452476[35] = 0;
   out_8909533314766452476[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_8909533314766452476[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_8909533314766452476[38] = 0;
   out_8909533314766452476[39] = -state[7];
   out_8909533314766452476[40] = state[6];
   out_8909533314766452476[41] = 0;
   out_8909533314766452476[42] = state[4];
   out_8909533314766452476[43] = -state[3];
   out_8909533314766452476[44] = 0;
   out_8909533314766452476[45] = 0;
   out_8909533314766452476[46] = 0;
   out_8909533314766452476[47] = 0;
   out_8909533314766452476[48] = 0;
   out_8909533314766452476[49] = 0;
   out_8909533314766452476[50] = 1;
   out_8909533314766452476[51] = 0;
   out_8909533314766452476[52] = 0;
   out_8909533314766452476[53] = 1;
}
void h_13(double *state, double *unused, double *out_9149861557909701017) {
   out_9149861557909701017[0] = state[3];
   out_9149861557909701017[1] = state[4];
   out_9149861557909701017[2] = state[5];
}
void H_13(double *state, double *unused, double *out_5649825377035039314) {
   out_5649825377035039314[0] = 0;
   out_5649825377035039314[1] = 0;
   out_5649825377035039314[2] = 0;
   out_5649825377035039314[3] = 1;
   out_5649825377035039314[4] = 0;
   out_5649825377035039314[5] = 0;
   out_5649825377035039314[6] = 0;
   out_5649825377035039314[7] = 0;
   out_5649825377035039314[8] = 0;
   out_5649825377035039314[9] = 0;
   out_5649825377035039314[10] = 0;
   out_5649825377035039314[11] = 0;
   out_5649825377035039314[12] = 0;
   out_5649825377035039314[13] = 0;
   out_5649825377035039314[14] = 0;
   out_5649825377035039314[15] = 0;
   out_5649825377035039314[16] = 0;
   out_5649825377035039314[17] = 0;
   out_5649825377035039314[18] = 0;
   out_5649825377035039314[19] = 0;
   out_5649825377035039314[20] = 0;
   out_5649825377035039314[21] = 0;
   out_5649825377035039314[22] = 1;
   out_5649825377035039314[23] = 0;
   out_5649825377035039314[24] = 0;
   out_5649825377035039314[25] = 0;
   out_5649825377035039314[26] = 0;
   out_5649825377035039314[27] = 0;
   out_5649825377035039314[28] = 0;
   out_5649825377035039314[29] = 0;
   out_5649825377035039314[30] = 0;
   out_5649825377035039314[31] = 0;
   out_5649825377035039314[32] = 0;
   out_5649825377035039314[33] = 0;
   out_5649825377035039314[34] = 0;
   out_5649825377035039314[35] = 0;
   out_5649825377035039314[36] = 0;
   out_5649825377035039314[37] = 0;
   out_5649825377035039314[38] = 0;
   out_5649825377035039314[39] = 0;
   out_5649825377035039314[40] = 0;
   out_5649825377035039314[41] = 1;
   out_5649825377035039314[42] = 0;
   out_5649825377035039314[43] = 0;
   out_5649825377035039314[44] = 0;
   out_5649825377035039314[45] = 0;
   out_5649825377035039314[46] = 0;
   out_5649825377035039314[47] = 0;
   out_5649825377035039314[48] = 0;
   out_5649825377035039314[49] = 0;
   out_5649825377035039314[50] = 0;
   out_5649825377035039314[51] = 0;
   out_5649825377035039314[52] = 0;
   out_5649825377035039314[53] = 0;
}
void h_14(double *state, double *unused, double *out_3251330187002382357) {
   out_3251330187002382357[0] = state[6];
   out_3251330187002382357[1] = state[7];
   out_3251330187002382357[2] = state[8];
}
void H_14(double *state, double *unused, double *out_9149528344697295902) {
   out_9149528344697295902[0] = 0;
   out_9149528344697295902[1] = 0;
   out_9149528344697295902[2] = 0;
   out_9149528344697295902[3] = 0;
   out_9149528344697295902[4] = 0;
   out_9149528344697295902[5] = 0;
   out_9149528344697295902[6] = 1;
   out_9149528344697295902[7] = 0;
   out_9149528344697295902[8] = 0;
   out_9149528344697295902[9] = 0;
   out_9149528344697295902[10] = 0;
   out_9149528344697295902[11] = 0;
   out_9149528344697295902[12] = 0;
   out_9149528344697295902[13] = 0;
   out_9149528344697295902[14] = 0;
   out_9149528344697295902[15] = 0;
   out_9149528344697295902[16] = 0;
   out_9149528344697295902[17] = 0;
   out_9149528344697295902[18] = 0;
   out_9149528344697295902[19] = 0;
   out_9149528344697295902[20] = 0;
   out_9149528344697295902[21] = 0;
   out_9149528344697295902[22] = 0;
   out_9149528344697295902[23] = 0;
   out_9149528344697295902[24] = 0;
   out_9149528344697295902[25] = 1;
   out_9149528344697295902[26] = 0;
   out_9149528344697295902[27] = 0;
   out_9149528344697295902[28] = 0;
   out_9149528344697295902[29] = 0;
   out_9149528344697295902[30] = 0;
   out_9149528344697295902[31] = 0;
   out_9149528344697295902[32] = 0;
   out_9149528344697295902[33] = 0;
   out_9149528344697295902[34] = 0;
   out_9149528344697295902[35] = 0;
   out_9149528344697295902[36] = 0;
   out_9149528344697295902[37] = 0;
   out_9149528344697295902[38] = 0;
   out_9149528344697295902[39] = 0;
   out_9149528344697295902[40] = 0;
   out_9149528344697295902[41] = 0;
   out_9149528344697295902[42] = 0;
   out_9149528344697295902[43] = 0;
   out_9149528344697295902[44] = 1;
   out_9149528344697295902[45] = 0;
   out_9149528344697295902[46] = 0;
   out_9149528344697295902[47] = 0;
   out_9149528344697295902[48] = 0;
   out_9149528344697295902[49] = 0;
   out_9149528344697295902[50] = 0;
   out_9149528344697295902[51] = 0;
   out_9149528344697295902[52] = 0;
   out_9149528344697295902[53] = 0;
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
void pose_err_fun(double *nom_x, double *delta_x, double *out_264984234156022510) {
  err_fun(nom_x, delta_x, out_264984234156022510);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_4459356063444070539) {
  inv_err_fun(nom_x, true_x, out_4459356063444070539);
}
void pose_H_mod_fun(double *state, double *out_7005986214264108234) {
  H_mod_fun(state, out_7005986214264108234);
}
void pose_f_fun(double *state, double dt, double *out_4717377945151750388) {
  f_fun(state,  dt, out_4717377945151750388);
}
void pose_F_fun(double *state, double dt, double *out_4729405661658211402) {
  F_fun(state,  dt, out_4729405661658211402);
}
void pose_h_4(double *state, double *unused, double *out_5738722976826185665) {
  h_4(state, unused, out_5738722976826185665);
}
void pose_H_4(double *state, double *unused, double *out_8862099202367372115) {
  H_4(state, unused, out_8862099202367372115);
}
void pose_h_10(double *state, double *unused, double *out_2388008800197743067) {
  h_10(state, unused, out_2388008800197743067);
}
void pose_H_10(double *state, double *unused, double *out_8909533314766452476) {
  H_10(state, unused, out_8909533314766452476);
}
void pose_h_13(double *state, double *unused, double *out_9149861557909701017) {
  h_13(state, unused, out_9149861557909701017);
}
void pose_H_13(double *state, double *unused, double *out_5649825377035039314) {
  H_13(state, unused, out_5649825377035039314);
}
void pose_h_14(double *state, double *unused, double *out_3251330187002382357) {
  h_14(state, unused, out_3251330187002382357);
}
void pose_H_14(double *state, double *unused, double *out_9149528344697295902) {
  H_14(state, unused, out_9149528344697295902);
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
