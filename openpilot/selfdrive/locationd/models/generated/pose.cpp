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
void err_fun(double *nom_x, double *delta_x, double *out_8239082397058567475) {
   out_8239082397058567475[0] = delta_x[0] + nom_x[0];
   out_8239082397058567475[1] = delta_x[1] + nom_x[1];
   out_8239082397058567475[2] = delta_x[2] + nom_x[2];
   out_8239082397058567475[3] = delta_x[3] + nom_x[3];
   out_8239082397058567475[4] = delta_x[4] + nom_x[4];
   out_8239082397058567475[5] = delta_x[5] + nom_x[5];
   out_8239082397058567475[6] = delta_x[6] + nom_x[6];
   out_8239082397058567475[7] = delta_x[7] + nom_x[7];
   out_8239082397058567475[8] = delta_x[8] + nom_x[8];
   out_8239082397058567475[9] = delta_x[9] + nom_x[9];
   out_8239082397058567475[10] = delta_x[10] + nom_x[10];
   out_8239082397058567475[11] = delta_x[11] + nom_x[11];
   out_8239082397058567475[12] = delta_x[12] + nom_x[12];
   out_8239082397058567475[13] = delta_x[13] + nom_x[13];
   out_8239082397058567475[14] = delta_x[14] + nom_x[14];
   out_8239082397058567475[15] = delta_x[15] + nom_x[15];
   out_8239082397058567475[16] = delta_x[16] + nom_x[16];
   out_8239082397058567475[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_7476243289318583052) {
   out_7476243289318583052[0] = -nom_x[0] + true_x[0];
   out_7476243289318583052[1] = -nom_x[1] + true_x[1];
   out_7476243289318583052[2] = -nom_x[2] + true_x[2];
   out_7476243289318583052[3] = -nom_x[3] + true_x[3];
   out_7476243289318583052[4] = -nom_x[4] + true_x[4];
   out_7476243289318583052[5] = -nom_x[5] + true_x[5];
   out_7476243289318583052[6] = -nom_x[6] + true_x[6];
   out_7476243289318583052[7] = -nom_x[7] + true_x[7];
   out_7476243289318583052[8] = -nom_x[8] + true_x[8];
   out_7476243289318583052[9] = -nom_x[9] + true_x[9];
   out_7476243289318583052[10] = -nom_x[10] + true_x[10];
   out_7476243289318583052[11] = -nom_x[11] + true_x[11];
   out_7476243289318583052[12] = -nom_x[12] + true_x[12];
   out_7476243289318583052[13] = -nom_x[13] + true_x[13];
   out_7476243289318583052[14] = -nom_x[14] + true_x[14];
   out_7476243289318583052[15] = -nom_x[15] + true_x[15];
   out_7476243289318583052[16] = -nom_x[16] + true_x[16];
   out_7476243289318583052[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_6682901757221528583) {
   out_6682901757221528583[0] = 1.0;
   out_6682901757221528583[1] = 0.0;
   out_6682901757221528583[2] = 0.0;
   out_6682901757221528583[3] = 0.0;
   out_6682901757221528583[4] = 0.0;
   out_6682901757221528583[5] = 0.0;
   out_6682901757221528583[6] = 0.0;
   out_6682901757221528583[7] = 0.0;
   out_6682901757221528583[8] = 0.0;
   out_6682901757221528583[9] = 0.0;
   out_6682901757221528583[10] = 0.0;
   out_6682901757221528583[11] = 0.0;
   out_6682901757221528583[12] = 0.0;
   out_6682901757221528583[13] = 0.0;
   out_6682901757221528583[14] = 0.0;
   out_6682901757221528583[15] = 0.0;
   out_6682901757221528583[16] = 0.0;
   out_6682901757221528583[17] = 0.0;
   out_6682901757221528583[18] = 0.0;
   out_6682901757221528583[19] = 1.0;
   out_6682901757221528583[20] = 0.0;
   out_6682901757221528583[21] = 0.0;
   out_6682901757221528583[22] = 0.0;
   out_6682901757221528583[23] = 0.0;
   out_6682901757221528583[24] = 0.0;
   out_6682901757221528583[25] = 0.0;
   out_6682901757221528583[26] = 0.0;
   out_6682901757221528583[27] = 0.0;
   out_6682901757221528583[28] = 0.0;
   out_6682901757221528583[29] = 0.0;
   out_6682901757221528583[30] = 0.0;
   out_6682901757221528583[31] = 0.0;
   out_6682901757221528583[32] = 0.0;
   out_6682901757221528583[33] = 0.0;
   out_6682901757221528583[34] = 0.0;
   out_6682901757221528583[35] = 0.0;
   out_6682901757221528583[36] = 0.0;
   out_6682901757221528583[37] = 0.0;
   out_6682901757221528583[38] = 1.0;
   out_6682901757221528583[39] = 0.0;
   out_6682901757221528583[40] = 0.0;
   out_6682901757221528583[41] = 0.0;
   out_6682901757221528583[42] = 0.0;
   out_6682901757221528583[43] = 0.0;
   out_6682901757221528583[44] = 0.0;
   out_6682901757221528583[45] = 0.0;
   out_6682901757221528583[46] = 0.0;
   out_6682901757221528583[47] = 0.0;
   out_6682901757221528583[48] = 0.0;
   out_6682901757221528583[49] = 0.0;
   out_6682901757221528583[50] = 0.0;
   out_6682901757221528583[51] = 0.0;
   out_6682901757221528583[52] = 0.0;
   out_6682901757221528583[53] = 0.0;
   out_6682901757221528583[54] = 0.0;
   out_6682901757221528583[55] = 0.0;
   out_6682901757221528583[56] = 0.0;
   out_6682901757221528583[57] = 1.0;
   out_6682901757221528583[58] = 0.0;
   out_6682901757221528583[59] = 0.0;
   out_6682901757221528583[60] = 0.0;
   out_6682901757221528583[61] = 0.0;
   out_6682901757221528583[62] = 0.0;
   out_6682901757221528583[63] = 0.0;
   out_6682901757221528583[64] = 0.0;
   out_6682901757221528583[65] = 0.0;
   out_6682901757221528583[66] = 0.0;
   out_6682901757221528583[67] = 0.0;
   out_6682901757221528583[68] = 0.0;
   out_6682901757221528583[69] = 0.0;
   out_6682901757221528583[70] = 0.0;
   out_6682901757221528583[71] = 0.0;
   out_6682901757221528583[72] = 0.0;
   out_6682901757221528583[73] = 0.0;
   out_6682901757221528583[74] = 0.0;
   out_6682901757221528583[75] = 0.0;
   out_6682901757221528583[76] = 1.0;
   out_6682901757221528583[77] = 0.0;
   out_6682901757221528583[78] = 0.0;
   out_6682901757221528583[79] = 0.0;
   out_6682901757221528583[80] = 0.0;
   out_6682901757221528583[81] = 0.0;
   out_6682901757221528583[82] = 0.0;
   out_6682901757221528583[83] = 0.0;
   out_6682901757221528583[84] = 0.0;
   out_6682901757221528583[85] = 0.0;
   out_6682901757221528583[86] = 0.0;
   out_6682901757221528583[87] = 0.0;
   out_6682901757221528583[88] = 0.0;
   out_6682901757221528583[89] = 0.0;
   out_6682901757221528583[90] = 0.0;
   out_6682901757221528583[91] = 0.0;
   out_6682901757221528583[92] = 0.0;
   out_6682901757221528583[93] = 0.0;
   out_6682901757221528583[94] = 0.0;
   out_6682901757221528583[95] = 1.0;
   out_6682901757221528583[96] = 0.0;
   out_6682901757221528583[97] = 0.0;
   out_6682901757221528583[98] = 0.0;
   out_6682901757221528583[99] = 0.0;
   out_6682901757221528583[100] = 0.0;
   out_6682901757221528583[101] = 0.0;
   out_6682901757221528583[102] = 0.0;
   out_6682901757221528583[103] = 0.0;
   out_6682901757221528583[104] = 0.0;
   out_6682901757221528583[105] = 0.0;
   out_6682901757221528583[106] = 0.0;
   out_6682901757221528583[107] = 0.0;
   out_6682901757221528583[108] = 0.0;
   out_6682901757221528583[109] = 0.0;
   out_6682901757221528583[110] = 0.0;
   out_6682901757221528583[111] = 0.0;
   out_6682901757221528583[112] = 0.0;
   out_6682901757221528583[113] = 0.0;
   out_6682901757221528583[114] = 1.0;
   out_6682901757221528583[115] = 0.0;
   out_6682901757221528583[116] = 0.0;
   out_6682901757221528583[117] = 0.0;
   out_6682901757221528583[118] = 0.0;
   out_6682901757221528583[119] = 0.0;
   out_6682901757221528583[120] = 0.0;
   out_6682901757221528583[121] = 0.0;
   out_6682901757221528583[122] = 0.0;
   out_6682901757221528583[123] = 0.0;
   out_6682901757221528583[124] = 0.0;
   out_6682901757221528583[125] = 0.0;
   out_6682901757221528583[126] = 0.0;
   out_6682901757221528583[127] = 0.0;
   out_6682901757221528583[128] = 0.0;
   out_6682901757221528583[129] = 0.0;
   out_6682901757221528583[130] = 0.0;
   out_6682901757221528583[131] = 0.0;
   out_6682901757221528583[132] = 0.0;
   out_6682901757221528583[133] = 1.0;
   out_6682901757221528583[134] = 0.0;
   out_6682901757221528583[135] = 0.0;
   out_6682901757221528583[136] = 0.0;
   out_6682901757221528583[137] = 0.0;
   out_6682901757221528583[138] = 0.0;
   out_6682901757221528583[139] = 0.0;
   out_6682901757221528583[140] = 0.0;
   out_6682901757221528583[141] = 0.0;
   out_6682901757221528583[142] = 0.0;
   out_6682901757221528583[143] = 0.0;
   out_6682901757221528583[144] = 0.0;
   out_6682901757221528583[145] = 0.0;
   out_6682901757221528583[146] = 0.0;
   out_6682901757221528583[147] = 0.0;
   out_6682901757221528583[148] = 0.0;
   out_6682901757221528583[149] = 0.0;
   out_6682901757221528583[150] = 0.0;
   out_6682901757221528583[151] = 0.0;
   out_6682901757221528583[152] = 1.0;
   out_6682901757221528583[153] = 0.0;
   out_6682901757221528583[154] = 0.0;
   out_6682901757221528583[155] = 0.0;
   out_6682901757221528583[156] = 0.0;
   out_6682901757221528583[157] = 0.0;
   out_6682901757221528583[158] = 0.0;
   out_6682901757221528583[159] = 0.0;
   out_6682901757221528583[160] = 0.0;
   out_6682901757221528583[161] = 0.0;
   out_6682901757221528583[162] = 0.0;
   out_6682901757221528583[163] = 0.0;
   out_6682901757221528583[164] = 0.0;
   out_6682901757221528583[165] = 0.0;
   out_6682901757221528583[166] = 0.0;
   out_6682901757221528583[167] = 0.0;
   out_6682901757221528583[168] = 0.0;
   out_6682901757221528583[169] = 0.0;
   out_6682901757221528583[170] = 0.0;
   out_6682901757221528583[171] = 1.0;
   out_6682901757221528583[172] = 0.0;
   out_6682901757221528583[173] = 0.0;
   out_6682901757221528583[174] = 0.0;
   out_6682901757221528583[175] = 0.0;
   out_6682901757221528583[176] = 0.0;
   out_6682901757221528583[177] = 0.0;
   out_6682901757221528583[178] = 0.0;
   out_6682901757221528583[179] = 0.0;
   out_6682901757221528583[180] = 0.0;
   out_6682901757221528583[181] = 0.0;
   out_6682901757221528583[182] = 0.0;
   out_6682901757221528583[183] = 0.0;
   out_6682901757221528583[184] = 0.0;
   out_6682901757221528583[185] = 0.0;
   out_6682901757221528583[186] = 0.0;
   out_6682901757221528583[187] = 0.0;
   out_6682901757221528583[188] = 0.0;
   out_6682901757221528583[189] = 0.0;
   out_6682901757221528583[190] = 1.0;
   out_6682901757221528583[191] = 0.0;
   out_6682901757221528583[192] = 0.0;
   out_6682901757221528583[193] = 0.0;
   out_6682901757221528583[194] = 0.0;
   out_6682901757221528583[195] = 0.0;
   out_6682901757221528583[196] = 0.0;
   out_6682901757221528583[197] = 0.0;
   out_6682901757221528583[198] = 0.0;
   out_6682901757221528583[199] = 0.0;
   out_6682901757221528583[200] = 0.0;
   out_6682901757221528583[201] = 0.0;
   out_6682901757221528583[202] = 0.0;
   out_6682901757221528583[203] = 0.0;
   out_6682901757221528583[204] = 0.0;
   out_6682901757221528583[205] = 0.0;
   out_6682901757221528583[206] = 0.0;
   out_6682901757221528583[207] = 0.0;
   out_6682901757221528583[208] = 0.0;
   out_6682901757221528583[209] = 1.0;
   out_6682901757221528583[210] = 0.0;
   out_6682901757221528583[211] = 0.0;
   out_6682901757221528583[212] = 0.0;
   out_6682901757221528583[213] = 0.0;
   out_6682901757221528583[214] = 0.0;
   out_6682901757221528583[215] = 0.0;
   out_6682901757221528583[216] = 0.0;
   out_6682901757221528583[217] = 0.0;
   out_6682901757221528583[218] = 0.0;
   out_6682901757221528583[219] = 0.0;
   out_6682901757221528583[220] = 0.0;
   out_6682901757221528583[221] = 0.0;
   out_6682901757221528583[222] = 0.0;
   out_6682901757221528583[223] = 0.0;
   out_6682901757221528583[224] = 0.0;
   out_6682901757221528583[225] = 0.0;
   out_6682901757221528583[226] = 0.0;
   out_6682901757221528583[227] = 0.0;
   out_6682901757221528583[228] = 1.0;
   out_6682901757221528583[229] = 0.0;
   out_6682901757221528583[230] = 0.0;
   out_6682901757221528583[231] = 0.0;
   out_6682901757221528583[232] = 0.0;
   out_6682901757221528583[233] = 0.0;
   out_6682901757221528583[234] = 0.0;
   out_6682901757221528583[235] = 0.0;
   out_6682901757221528583[236] = 0.0;
   out_6682901757221528583[237] = 0.0;
   out_6682901757221528583[238] = 0.0;
   out_6682901757221528583[239] = 0.0;
   out_6682901757221528583[240] = 0.0;
   out_6682901757221528583[241] = 0.0;
   out_6682901757221528583[242] = 0.0;
   out_6682901757221528583[243] = 0.0;
   out_6682901757221528583[244] = 0.0;
   out_6682901757221528583[245] = 0.0;
   out_6682901757221528583[246] = 0.0;
   out_6682901757221528583[247] = 1.0;
   out_6682901757221528583[248] = 0.0;
   out_6682901757221528583[249] = 0.0;
   out_6682901757221528583[250] = 0.0;
   out_6682901757221528583[251] = 0.0;
   out_6682901757221528583[252] = 0.0;
   out_6682901757221528583[253] = 0.0;
   out_6682901757221528583[254] = 0.0;
   out_6682901757221528583[255] = 0.0;
   out_6682901757221528583[256] = 0.0;
   out_6682901757221528583[257] = 0.0;
   out_6682901757221528583[258] = 0.0;
   out_6682901757221528583[259] = 0.0;
   out_6682901757221528583[260] = 0.0;
   out_6682901757221528583[261] = 0.0;
   out_6682901757221528583[262] = 0.0;
   out_6682901757221528583[263] = 0.0;
   out_6682901757221528583[264] = 0.0;
   out_6682901757221528583[265] = 0.0;
   out_6682901757221528583[266] = 1.0;
   out_6682901757221528583[267] = 0.0;
   out_6682901757221528583[268] = 0.0;
   out_6682901757221528583[269] = 0.0;
   out_6682901757221528583[270] = 0.0;
   out_6682901757221528583[271] = 0.0;
   out_6682901757221528583[272] = 0.0;
   out_6682901757221528583[273] = 0.0;
   out_6682901757221528583[274] = 0.0;
   out_6682901757221528583[275] = 0.0;
   out_6682901757221528583[276] = 0.0;
   out_6682901757221528583[277] = 0.0;
   out_6682901757221528583[278] = 0.0;
   out_6682901757221528583[279] = 0.0;
   out_6682901757221528583[280] = 0.0;
   out_6682901757221528583[281] = 0.0;
   out_6682901757221528583[282] = 0.0;
   out_6682901757221528583[283] = 0.0;
   out_6682901757221528583[284] = 0.0;
   out_6682901757221528583[285] = 1.0;
   out_6682901757221528583[286] = 0.0;
   out_6682901757221528583[287] = 0.0;
   out_6682901757221528583[288] = 0.0;
   out_6682901757221528583[289] = 0.0;
   out_6682901757221528583[290] = 0.0;
   out_6682901757221528583[291] = 0.0;
   out_6682901757221528583[292] = 0.0;
   out_6682901757221528583[293] = 0.0;
   out_6682901757221528583[294] = 0.0;
   out_6682901757221528583[295] = 0.0;
   out_6682901757221528583[296] = 0.0;
   out_6682901757221528583[297] = 0.0;
   out_6682901757221528583[298] = 0.0;
   out_6682901757221528583[299] = 0.0;
   out_6682901757221528583[300] = 0.0;
   out_6682901757221528583[301] = 0.0;
   out_6682901757221528583[302] = 0.0;
   out_6682901757221528583[303] = 0.0;
   out_6682901757221528583[304] = 1.0;
   out_6682901757221528583[305] = 0.0;
   out_6682901757221528583[306] = 0.0;
   out_6682901757221528583[307] = 0.0;
   out_6682901757221528583[308] = 0.0;
   out_6682901757221528583[309] = 0.0;
   out_6682901757221528583[310] = 0.0;
   out_6682901757221528583[311] = 0.0;
   out_6682901757221528583[312] = 0.0;
   out_6682901757221528583[313] = 0.0;
   out_6682901757221528583[314] = 0.0;
   out_6682901757221528583[315] = 0.0;
   out_6682901757221528583[316] = 0.0;
   out_6682901757221528583[317] = 0.0;
   out_6682901757221528583[318] = 0.0;
   out_6682901757221528583[319] = 0.0;
   out_6682901757221528583[320] = 0.0;
   out_6682901757221528583[321] = 0.0;
   out_6682901757221528583[322] = 0.0;
   out_6682901757221528583[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_8926187974092623704) {
   out_8926187974092623704[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_8926187974092623704[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_8926187974092623704[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_8926187974092623704[3] = dt*state[12] + state[3];
   out_8926187974092623704[4] = dt*state[13] + state[4];
   out_8926187974092623704[5] = dt*state[14] + state[5];
   out_8926187974092623704[6] = state[6];
   out_8926187974092623704[7] = state[7];
   out_8926187974092623704[8] = state[8];
   out_8926187974092623704[9] = state[9];
   out_8926187974092623704[10] = state[10];
   out_8926187974092623704[11] = state[11];
   out_8926187974092623704[12] = state[12];
   out_8926187974092623704[13] = state[13];
   out_8926187974092623704[14] = state[14];
   out_8926187974092623704[15] = state[15];
   out_8926187974092623704[16] = state[16];
   out_8926187974092623704[17] = state[17];
}
void F_fun(double *state, double dt, double *out_7762434416297877994) {
   out_7762434416297877994[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_7762434416297877994[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_7762434416297877994[2] = 0;
   out_7762434416297877994[3] = 0;
   out_7762434416297877994[4] = 0;
   out_7762434416297877994[5] = 0;
   out_7762434416297877994[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_7762434416297877994[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_7762434416297877994[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_7762434416297877994[9] = 0;
   out_7762434416297877994[10] = 0;
   out_7762434416297877994[11] = 0;
   out_7762434416297877994[12] = 0;
   out_7762434416297877994[13] = 0;
   out_7762434416297877994[14] = 0;
   out_7762434416297877994[15] = 0;
   out_7762434416297877994[16] = 0;
   out_7762434416297877994[17] = 0;
   out_7762434416297877994[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_7762434416297877994[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_7762434416297877994[20] = 0;
   out_7762434416297877994[21] = 0;
   out_7762434416297877994[22] = 0;
   out_7762434416297877994[23] = 0;
   out_7762434416297877994[24] = 0;
   out_7762434416297877994[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_7762434416297877994[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_7762434416297877994[27] = 0;
   out_7762434416297877994[28] = 0;
   out_7762434416297877994[29] = 0;
   out_7762434416297877994[30] = 0;
   out_7762434416297877994[31] = 0;
   out_7762434416297877994[32] = 0;
   out_7762434416297877994[33] = 0;
   out_7762434416297877994[34] = 0;
   out_7762434416297877994[35] = 0;
   out_7762434416297877994[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_7762434416297877994[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_7762434416297877994[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_7762434416297877994[39] = 0;
   out_7762434416297877994[40] = 0;
   out_7762434416297877994[41] = 0;
   out_7762434416297877994[42] = 0;
   out_7762434416297877994[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_7762434416297877994[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_7762434416297877994[45] = 0;
   out_7762434416297877994[46] = 0;
   out_7762434416297877994[47] = 0;
   out_7762434416297877994[48] = 0;
   out_7762434416297877994[49] = 0;
   out_7762434416297877994[50] = 0;
   out_7762434416297877994[51] = 0;
   out_7762434416297877994[52] = 0;
   out_7762434416297877994[53] = 0;
   out_7762434416297877994[54] = 0;
   out_7762434416297877994[55] = 0;
   out_7762434416297877994[56] = 0;
   out_7762434416297877994[57] = 1;
   out_7762434416297877994[58] = 0;
   out_7762434416297877994[59] = 0;
   out_7762434416297877994[60] = 0;
   out_7762434416297877994[61] = 0;
   out_7762434416297877994[62] = 0;
   out_7762434416297877994[63] = 0;
   out_7762434416297877994[64] = 0;
   out_7762434416297877994[65] = 0;
   out_7762434416297877994[66] = dt;
   out_7762434416297877994[67] = 0;
   out_7762434416297877994[68] = 0;
   out_7762434416297877994[69] = 0;
   out_7762434416297877994[70] = 0;
   out_7762434416297877994[71] = 0;
   out_7762434416297877994[72] = 0;
   out_7762434416297877994[73] = 0;
   out_7762434416297877994[74] = 0;
   out_7762434416297877994[75] = 0;
   out_7762434416297877994[76] = 1;
   out_7762434416297877994[77] = 0;
   out_7762434416297877994[78] = 0;
   out_7762434416297877994[79] = 0;
   out_7762434416297877994[80] = 0;
   out_7762434416297877994[81] = 0;
   out_7762434416297877994[82] = 0;
   out_7762434416297877994[83] = 0;
   out_7762434416297877994[84] = 0;
   out_7762434416297877994[85] = dt;
   out_7762434416297877994[86] = 0;
   out_7762434416297877994[87] = 0;
   out_7762434416297877994[88] = 0;
   out_7762434416297877994[89] = 0;
   out_7762434416297877994[90] = 0;
   out_7762434416297877994[91] = 0;
   out_7762434416297877994[92] = 0;
   out_7762434416297877994[93] = 0;
   out_7762434416297877994[94] = 0;
   out_7762434416297877994[95] = 1;
   out_7762434416297877994[96] = 0;
   out_7762434416297877994[97] = 0;
   out_7762434416297877994[98] = 0;
   out_7762434416297877994[99] = 0;
   out_7762434416297877994[100] = 0;
   out_7762434416297877994[101] = 0;
   out_7762434416297877994[102] = 0;
   out_7762434416297877994[103] = 0;
   out_7762434416297877994[104] = dt;
   out_7762434416297877994[105] = 0;
   out_7762434416297877994[106] = 0;
   out_7762434416297877994[107] = 0;
   out_7762434416297877994[108] = 0;
   out_7762434416297877994[109] = 0;
   out_7762434416297877994[110] = 0;
   out_7762434416297877994[111] = 0;
   out_7762434416297877994[112] = 0;
   out_7762434416297877994[113] = 0;
   out_7762434416297877994[114] = 1;
   out_7762434416297877994[115] = 0;
   out_7762434416297877994[116] = 0;
   out_7762434416297877994[117] = 0;
   out_7762434416297877994[118] = 0;
   out_7762434416297877994[119] = 0;
   out_7762434416297877994[120] = 0;
   out_7762434416297877994[121] = 0;
   out_7762434416297877994[122] = 0;
   out_7762434416297877994[123] = 0;
   out_7762434416297877994[124] = 0;
   out_7762434416297877994[125] = 0;
   out_7762434416297877994[126] = 0;
   out_7762434416297877994[127] = 0;
   out_7762434416297877994[128] = 0;
   out_7762434416297877994[129] = 0;
   out_7762434416297877994[130] = 0;
   out_7762434416297877994[131] = 0;
   out_7762434416297877994[132] = 0;
   out_7762434416297877994[133] = 1;
   out_7762434416297877994[134] = 0;
   out_7762434416297877994[135] = 0;
   out_7762434416297877994[136] = 0;
   out_7762434416297877994[137] = 0;
   out_7762434416297877994[138] = 0;
   out_7762434416297877994[139] = 0;
   out_7762434416297877994[140] = 0;
   out_7762434416297877994[141] = 0;
   out_7762434416297877994[142] = 0;
   out_7762434416297877994[143] = 0;
   out_7762434416297877994[144] = 0;
   out_7762434416297877994[145] = 0;
   out_7762434416297877994[146] = 0;
   out_7762434416297877994[147] = 0;
   out_7762434416297877994[148] = 0;
   out_7762434416297877994[149] = 0;
   out_7762434416297877994[150] = 0;
   out_7762434416297877994[151] = 0;
   out_7762434416297877994[152] = 1;
   out_7762434416297877994[153] = 0;
   out_7762434416297877994[154] = 0;
   out_7762434416297877994[155] = 0;
   out_7762434416297877994[156] = 0;
   out_7762434416297877994[157] = 0;
   out_7762434416297877994[158] = 0;
   out_7762434416297877994[159] = 0;
   out_7762434416297877994[160] = 0;
   out_7762434416297877994[161] = 0;
   out_7762434416297877994[162] = 0;
   out_7762434416297877994[163] = 0;
   out_7762434416297877994[164] = 0;
   out_7762434416297877994[165] = 0;
   out_7762434416297877994[166] = 0;
   out_7762434416297877994[167] = 0;
   out_7762434416297877994[168] = 0;
   out_7762434416297877994[169] = 0;
   out_7762434416297877994[170] = 0;
   out_7762434416297877994[171] = 1;
   out_7762434416297877994[172] = 0;
   out_7762434416297877994[173] = 0;
   out_7762434416297877994[174] = 0;
   out_7762434416297877994[175] = 0;
   out_7762434416297877994[176] = 0;
   out_7762434416297877994[177] = 0;
   out_7762434416297877994[178] = 0;
   out_7762434416297877994[179] = 0;
   out_7762434416297877994[180] = 0;
   out_7762434416297877994[181] = 0;
   out_7762434416297877994[182] = 0;
   out_7762434416297877994[183] = 0;
   out_7762434416297877994[184] = 0;
   out_7762434416297877994[185] = 0;
   out_7762434416297877994[186] = 0;
   out_7762434416297877994[187] = 0;
   out_7762434416297877994[188] = 0;
   out_7762434416297877994[189] = 0;
   out_7762434416297877994[190] = 1;
   out_7762434416297877994[191] = 0;
   out_7762434416297877994[192] = 0;
   out_7762434416297877994[193] = 0;
   out_7762434416297877994[194] = 0;
   out_7762434416297877994[195] = 0;
   out_7762434416297877994[196] = 0;
   out_7762434416297877994[197] = 0;
   out_7762434416297877994[198] = 0;
   out_7762434416297877994[199] = 0;
   out_7762434416297877994[200] = 0;
   out_7762434416297877994[201] = 0;
   out_7762434416297877994[202] = 0;
   out_7762434416297877994[203] = 0;
   out_7762434416297877994[204] = 0;
   out_7762434416297877994[205] = 0;
   out_7762434416297877994[206] = 0;
   out_7762434416297877994[207] = 0;
   out_7762434416297877994[208] = 0;
   out_7762434416297877994[209] = 1;
   out_7762434416297877994[210] = 0;
   out_7762434416297877994[211] = 0;
   out_7762434416297877994[212] = 0;
   out_7762434416297877994[213] = 0;
   out_7762434416297877994[214] = 0;
   out_7762434416297877994[215] = 0;
   out_7762434416297877994[216] = 0;
   out_7762434416297877994[217] = 0;
   out_7762434416297877994[218] = 0;
   out_7762434416297877994[219] = 0;
   out_7762434416297877994[220] = 0;
   out_7762434416297877994[221] = 0;
   out_7762434416297877994[222] = 0;
   out_7762434416297877994[223] = 0;
   out_7762434416297877994[224] = 0;
   out_7762434416297877994[225] = 0;
   out_7762434416297877994[226] = 0;
   out_7762434416297877994[227] = 0;
   out_7762434416297877994[228] = 1;
   out_7762434416297877994[229] = 0;
   out_7762434416297877994[230] = 0;
   out_7762434416297877994[231] = 0;
   out_7762434416297877994[232] = 0;
   out_7762434416297877994[233] = 0;
   out_7762434416297877994[234] = 0;
   out_7762434416297877994[235] = 0;
   out_7762434416297877994[236] = 0;
   out_7762434416297877994[237] = 0;
   out_7762434416297877994[238] = 0;
   out_7762434416297877994[239] = 0;
   out_7762434416297877994[240] = 0;
   out_7762434416297877994[241] = 0;
   out_7762434416297877994[242] = 0;
   out_7762434416297877994[243] = 0;
   out_7762434416297877994[244] = 0;
   out_7762434416297877994[245] = 0;
   out_7762434416297877994[246] = 0;
   out_7762434416297877994[247] = 1;
   out_7762434416297877994[248] = 0;
   out_7762434416297877994[249] = 0;
   out_7762434416297877994[250] = 0;
   out_7762434416297877994[251] = 0;
   out_7762434416297877994[252] = 0;
   out_7762434416297877994[253] = 0;
   out_7762434416297877994[254] = 0;
   out_7762434416297877994[255] = 0;
   out_7762434416297877994[256] = 0;
   out_7762434416297877994[257] = 0;
   out_7762434416297877994[258] = 0;
   out_7762434416297877994[259] = 0;
   out_7762434416297877994[260] = 0;
   out_7762434416297877994[261] = 0;
   out_7762434416297877994[262] = 0;
   out_7762434416297877994[263] = 0;
   out_7762434416297877994[264] = 0;
   out_7762434416297877994[265] = 0;
   out_7762434416297877994[266] = 1;
   out_7762434416297877994[267] = 0;
   out_7762434416297877994[268] = 0;
   out_7762434416297877994[269] = 0;
   out_7762434416297877994[270] = 0;
   out_7762434416297877994[271] = 0;
   out_7762434416297877994[272] = 0;
   out_7762434416297877994[273] = 0;
   out_7762434416297877994[274] = 0;
   out_7762434416297877994[275] = 0;
   out_7762434416297877994[276] = 0;
   out_7762434416297877994[277] = 0;
   out_7762434416297877994[278] = 0;
   out_7762434416297877994[279] = 0;
   out_7762434416297877994[280] = 0;
   out_7762434416297877994[281] = 0;
   out_7762434416297877994[282] = 0;
   out_7762434416297877994[283] = 0;
   out_7762434416297877994[284] = 0;
   out_7762434416297877994[285] = 1;
   out_7762434416297877994[286] = 0;
   out_7762434416297877994[287] = 0;
   out_7762434416297877994[288] = 0;
   out_7762434416297877994[289] = 0;
   out_7762434416297877994[290] = 0;
   out_7762434416297877994[291] = 0;
   out_7762434416297877994[292] = 0;
   out_7762434416297877994[293] = 0;
   out_7762434416297877994[294] = 0;
   out_7762434416297877994[295] = 0;
   out_7762434416297877994[296] = 0;
   out_7762434416297877994[297] = 0;
   out_7762434416297877994[298] = 0;
   out_7762434416297877994[299] = 0;
   out_7762434416297877994[300] = 0;
   out_7762434416297877994[301] = 0;
   out_7762434416297877994[302] = 0;
   out_7762434416297877994[303] = 0;
   out_7762434416297877994[304] = 1;
   out_7762434416297877994[305] = 0;
   out_7762434416297877994[306] = 0;
   out_7762434416297877994[307] = 0;
   out_7762434416297877994[308] = 0;
   out_7762434416297877994[309] = 0;
   out_7762434416297877994[310] = 0;
   out_7762434416297877994[311] = 0;
   out_7762434416297877994[312] = 0;
   out_7762434416297877994[313] = 0;
   out_7762434416297877994[314] = 0;
   out_7762434416297877994[315] = 0;
   out_7762434416297877994[316] = 0;
   out_7762434416297877994[317] = 0;
   out_7762434416297877994[318] = 0;
   out_7762434416297877994[319] = 0;
   out_7762434416297877994[320] = 0;
   out_7762434416297877994[321] = 0;
   out_7762434416297877994[322] = 0;
   out_7762434416297877994[323] = 1;
}
void h_4(double *state, double *unused, double *out_4305306830373346392) {
   out_4305306830373346392[0] = state[6] + state[9];
   out_4305306830373346392[1] = state[7] + state[10];
   out_4305306830373346392[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_1517403126751696184) {
   out_1517403126751696184[0] = 0;
   out_1517403126751696184[1] = 0;
   out_1517403126751696184[2] = 0;
   out_1517403126751696184[3] = 0;
   out_1517403126751696184[4] = 0;
   out_1517403126751696184[5] = 0;
   out_1517403126751696184[6] = 1;
   out_1517403126751696184[7] = 0;
   out_1517403126751696184[8] = 0;
   out_1517403126751696184[9] = 1;
   out_1517403126751696184[10] = 0;
   out_1517403126751696184[11] = 0;
   out_1517403126751696184[12] = 0;
   out_1517403126751696184[13] = 0;
   out_1517403126751696184[14] = 0;
   out_1517403126751696184[15] = 0;
   out_1517403126751696184[16] = 0;
   out_1517403126751696184[17] = 0;
   out_1517403126751696184[18] = 0;
   out_1517403126751696184[19] = 0;
   out_1517403126751696184[20] = 0;
   out_1517403126751696184[21] = 0;
   out_1517403126751696184[22] = 0;
   out_1517403126751696184[23] = 0;
   out_1517403126751696184[24] = 0;
   out_1517403126751696184[25] = 1;
   out_1517403126751696184[26] = 0;
   out_1517403126751696184[27] = 0;
   out_1517403126751696184[28] = 1;
   out_1517403126751696184[29] = 0;
   out_1517403126751696184[30] = 0;
   out_1517403126751696184[31] = 0;
   out_1517403126751696184[32] = 0;
   out_1517403126751696184[33] = 0;
   out_1517403126751696184[34] = 0;
   out_1517403126751696184[35] = 0;
   out_1517403126751696184[36] = 0;
   out_1517403126751696184[37] = 0;
   out_1517403126751696184[38] = 0;
   out_1517403126751696184[39] = 0;
   out_1517403126751696184[40] = 0;
   out_1517403126751696184[41] = 0;
   out_1517403126751696184[42] = 0;
   out_1517403126751696184[43] = 0;
   out_1517403126751696184[44] = 1;
   out_1517403126751696184[45] = 0;
   out_1517403126751696184[46] = 0;
   out_1517403126751696184[47] = 1;
   out_1517403126751696184[48] = 0;
   out_1517403126751696184[49] = 0;
   out_1517403126751696184[50] = 0;
   out_1517403126751696184[51] = 0;
   out_1517403126751696184[52] = 0;
   out_1517403126751696184[53] = 0;
}
void h_10(double *state, double *unused, double *out_6976768425782679545) {
   out_6976768425782679545[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_6976768425782679545[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_6976768425782679545[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_3773372038423704930) {
   out_3773372038423704930[0] = 0;
   out_3773372038423704930[1] = 9.8100000000000005*cos(state[1]);
   out_3773372038423704930[2] = 0;
   out_3773372038423704930[3] = 0;
   out_3773372038423704930[4] = -state[8];
   out_3773372038423704930[5] = state[7];
   out_3773372038423704930[6] = 0;
   out_3773372038423704930[7] = state[5];
   out_3773372038423704930[8] = -state[4];
   out_3773372038423704930[9] = 0;
   out_3773372038423704930[10] = 0;
   out_3773372038423704930[11] = 0;
   out_3773372038423704930[12] = 1;
   out_3773372038423704930[13] = 0;
   out_3773372038423704930[14] = 0;
   out_3773372038423704930[15] = 1;
   out_3773372038423704930[16] = 0;
   out_3773372038423704930[17] = 0;
   out_3773372038423704930[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_3773372038423704930[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_3773372038423704930[20] = 0;
   out_3773372038423704930[21] = state[8];
   out_3773372038423704930[22] = 0;
   out_3773372038423704930[23] = -state[6];
   out_3773372038423704930[24] = -state[5];
   out_3773372038423704930[25] = 0;
   out_3773372038423704930[26] = state[3];
   out_3773372038423704930[27] = 0;
   out_3773372038423704930[28] = 0;
   out_3773372038423704930[29] = 0;
   out_3773372038423704930[30] = 0;
   out_3773372038423704930[31] = 1;
   out_3773372038423704930[32] = 0;
   out_3773372038423704930[33] = 0;
   out_3773372038423704930[34] = 1;
   out_3773372038423704930[35] = 0;
   out_3773372038423704930[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_3773372038423704930[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_3773372038423704930[38] = 0;
   out_3773372038423704930[39] = -state[7];
   out_3773372038423704930[40] = state[6];
   out_3773372038423704930[41] = 0;
   out_3773372038423704930[42] = state[4];
   out_3773372038423704930[43] = -state[3];
   out_3773372038423704930[44] = 0;
   out_3773372038423704930[45] = 0;
   out_3773372038423704930[46] = 0;
   out_3773372038423704930[47] = 0;
   out_3773372038423704930[48] = 0;
   out_3773372038423704930[49] = 0;
   out_3773372038423704930[50] = 1;
   out_3773372038423704930[51] = 0;
   out_3773372038423704930[52] = 0;
   out_3773372038423704930[53] = 1;
}
void h_13(double *state, double *unused, double *out_6361379321214522320) {
   out_6361379321214522320[0] = state[3];
   out_6361379321214522320[1] = state[4];
   out_6361379321214522320[2] = state[5];
}
void H_13(double *state, double *unused, double *out_9128034335068397113) {
   out_9128034335068397113[0] = 0;
   out_9128034335068397113[1] = 0;
   out_9128034335068397113[2] = 0;
   out_9128034335068397113[3] = 1;
   out_9128034335068397113[4] = 0;
   out_9128034335068397113[5] = 0;
   out_9128034335068397113[6] = 0;
   out_9128034335068397113[7] = 0;
   out_9128034335068397113[8] = 0;
   out_9128034335068397113[9] = 0;
   out_9128034335068397113[10] = 0;
   out_9128034335068397113[11] = 0;
   out_9128034335068397113[12] = 0;
   out_9128034335068397113[13] = 0;
   out_9128034335068397113[14] = 0;
   out_9128034335068397113[15] = 0;
   out_9128034335068397113[16] = 0;
   out_9128034335068397113[17] = 0;
   out_9128034335068397113[18] = 0;
   out_9128034335068397113[19] = 0;
   out_9128034335068397113[20] = 0;
   out_9128034335068397113[21] = 0;
   out_9128034335068397113[22] = 1;
   out_9128034335068397113[23] = 0;
   out_9128034335068397113[24] = 0;
   out_9128034335068397113[25] = 0;
   out_9128034335068397113[26] = 0;
   out_9128034335068397113[27] = 0;
   out_9128034335068397113[28] = 0;
   out_9128034335068397113[29] = 0;
   out_9128034335068397113[30] = 0;
   out_9128034335068397113[31] = 0;
   out_9128034335068397113[32] = 0;
   out_9128034335068397113[33] = 0;
   out_9128034335068397113[34] = 0;
   out_9128034335068397113[35] = 0;
   out_9128034335068397113[36] = 0;
   out_9128034335068397113[37] = 0;
   out_9128034335068397113[38] = 0;
   out_9128034335068397113[39] = 0;
   out_9128034335068397113[40] = 0;
   out_9128034335068397113[41] = 1;
   out_9128034335068397113[42] = 0;
   out_9128034335068397113[43] = 0;
   out_9128034335068397113[44] = 0;
   out_9128034335068397113[45] = 0;
   out_9128034335068397113[46] = 0;
   out_9128034335068397113[47] = 0;
   out_9128034335068397113[48] = 0;
   out_9128034335068397113[49] = 0;
   out_9128034335068397113[50] = 0;
   out_9128034335068397113[51] = 0;
   out_9128034335068397113[52] = 0;
   out_9128034335068397113[53] = 0;
}
void h_14(double *state, double *unused, double *out_4542222400622544050) {
   out_4542222400622544050[0] = state[6];
   out_4542222400622544050[1] = state[7];
   out_4542222400622544050[2] = state[8];
}
void H_14(double *state, double *unused, double *out_5480643983091180713) {
   out_5480643983091180713[0] = 0;
   out_5480643983091180713[1] = 0;
   out_5480643983091180713[2] = 0;
   out_5480643983091180713[3] = 0;
   out_5480643983091180713[4] = 0;
   out_5480643983091180713[5] = 0;
   out_5480643983091180713[6] = 1;
   out_5480643983091180713[7] = 0;
   out_5480643983091180713[8] = 0;
   out_5480643983091180713[9] = 0;
   out_5480643983091180713[10] = 0;
   out_5480643983091180713[11] = 0;
   out_5480643983091180713[12] = 0;
   out_5480643983091180713[13] = 0;
   out_5480643983091180713[14] = 0;
   out_5480643983091180713[15] = 0;
   out_5480643983091180713[16] = 0;
   out_5480643983091180713[17] = 0;
   out_5480643983091180713[18] = 0;
   out_5480643983091180713[19] = 0;
   out_5480643983091180713[20] = 0;
   out_5480643983091180713[21] = 0;
   out_5480643983091180713[22] = 0;
   out_5480643983091180713[23] = 0;
   out_5480643983091180713[24] = 0;
   out_5480643983091180713[25] = 1;
   out_5480643983091180713[26] = 0;
   out_5480643983091180713[27] = 0;
   out_5480643983091180713[28] = 0;
   out_5480643983091180713[29] = 0;
   out_5480643983091180713[30] = 0;
   out_5480643983091180713[31] = 0;
   out_5480643983091180713[32] = 0;
   out_5480643983091180713[33] = 0;
   out_5480643983091180713[34] = 0;
   out_5480643983091180713[35] = 0;
   out_5480643983091180713[36] = 0;
   out_5480643983091180713[37] = 0;
   out_5480643983091180713[38] = 0;
   out_5480643983091180713[39] = 0;
   out_5480643983091180713[40] = 0;
   out_5480643983091180713[41] = 0;
   out_5480643983091180713[42] = 0;
   out_5480643983091180713[43] = 0;
   out_5480643983091180713[44] = 1;
   out_5480643983091180713[45] = 0;
   out_5480643983091180713[46] = 0;
   out_5480643983091180713[47] = 0;
   out_5480643983091180713[48] = 0;
   out_5480643983091180713[49] = 0;
   out_5480643983091180713[50] = 0;
   out_5480643983091180713[51] = 0;
   out_5480643983091180713[52] = 0;
   out_5480643983091180713[53] = 0;
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
void pose_err_fun(double *nom_x, double *delta_x, double *out_8239082397058567475) {
  err_fun(nom_x, delta_x, out_8239082397058567475);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_7476243289318583052) {
  inv_err_fun(nom_x, true_x, out_7476243289318583052);
}
void pose_H_mod_fun(double *state, double *out_6682901757221528583) {
  H_mod_fun(state, out_6682901757221528583);
}
void pose_f_fun(double *state, double dt, double *out_8926187974092623704) {
  f_fun(state,  dt, out_8926187974092623704);
}
void pose_F_fun(double *state, double dt, double *out_7762434416297877994) {
  F_fun(state,  dt, out_7762434416297877994);
}
void pose_h_4(double *state, double *unused, double *out_4305306830373346392) {
  h_4(state, unused, out_4305306830373346392);
}
void pose_H_4(double *state, double *unused, double *out_1517403126751696184) {
  H_4(state, unused, out_1517403126751696184);
}
void pose_h_10(double *state, double *unused, double *out_6976768425782679545) {
  h_10(state, unused, out_6976768425782679545);
}
void pose_H_10(double *state, double *unused, double *out_3773372038423704930) {
  H_10(state, unused, out_3773372038423704930);
}
void pose_h_13(double *state, double *unused, double *out_6361379321214522320) {
  h_13(state, unused, out_6361379321214522320);
}
void pose_H_13(double *state, double *unused, double *out_9128034335068397113) {
  H_13(state, unused, out_9128034335068397113);
}
void pose_h_14(double *state, double *unused, double *out_4542222400622544050) {
  h_14(state, unused, out_4542222400622544050);
}
void pose_H_14(double *state, double *unused, double *out_5480643983091180713) {
  H_14(state, unused, out_5480643983091180713);
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
