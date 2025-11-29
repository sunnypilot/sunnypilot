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
void err_fun(double *nom_x, double *delta_x, double *out_1055807072610005846) {
   out_1055807072610005846[0] = delta_x[0] + nom_x[0];
   out_1055807072610005846[1] = delta_x[1] + nom_x[1];
   out_1055807072610005846[2] = delta_x[2] + nom_x[2];
   out_1055807072610005846[3] = delta_x[3] + nom_x[3];
   out_1055807072610005846[4] = delta_x[4] + nom_x[4];
   out_1055807072610005846[5] = delta_x[5] + nom_x[5];
   out_1055807072610005846[6] = delta_x[6] + nom_x[6];
   out_1055807072610005846[7] = delta_x[7] + nom_x[7];
   out_1055807072610005846[8] = delta_x[8] + nom_x[8];
   out_1055807072610005846[9] = delta_x[9] + nom_x[9];
   out_1055807072610005846[10] = delta_x[10] + nom_x[10];
   out_1055807072610005846[11] = delta_x[11] + nom_x[11];
   out_1055807072610005846[12] = delta_x[12] + nom_x[12];
   out_1055807072610005846[13] = delta_x[13] + nom_x[13];
   out_1055807072610005846[14] = delta_x[14] + nom_x[14];
   out_1055807072610005846[15] = delta_x[15] + nom_x[15];
   out_1055807072610005846[16] = delta_x[16] + nom_x[16];
   out_1055807072610005846[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_983516364171912274) {
   out_983516364171912274[0] = -nom_x[0] + true_x[0];
   out_983516364171912274[1] = -nom_x[1] + true_x[1];
   out_983516364171912274[2] = -nom_x[2] + true_x[2];
   out_983516364171912274[3] = -nom_x[3] + true_x[3];
   out_983516364171912274[4] = -nom_x[4] + true_x[4];
   out_983516364171912274[5] = -nom_x[5] + true_x[5];
   out_983516364171912274[6] = -nom_x[6] + true_x[6];
   out_983516364171912274[7] = -nom_x[7] + true_x[7];
   out_983516364171912274[8] = -nom_x[8] + true_x[8];
   out_983516364171912274[9] = -nom_x[9] + true_x[9];
   out_983516364171912274[10] = -nom_x[10] + true_x[10];
   out_983516364171912274[11] = -nom_x[11] + true_x[11];
   out_983516364171912274[12] = -nom_x[12] + true_x[12];
   out_983516364171912274[13] = -nom_x[13] + true_x[13];
   out_983516364171912274[14] = -nom_x[14] + true_x[14];
   out_983516364171912274[15] = -nom_x[15] + true_x[15];
   out_983516364171912274[16] = -nom_x[16] + true_x[16];
   out_983516364171912274[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_5307849917674294752) {
   out_5307849917674294752[0] = 1.0;
   out_5307849917674294752[1] = 0.0;
   out_5307849917674294752[2] = 0.0;
   out_5307849917674294752[3] = 0.0;
   out_5307849917674294752[4] = 0.0;
   out_5307849917674294752[5] = 0.0;
   out_5307849917674294752[6] = 0.0;
   out_5307849917674294752[7] = 0.0;
   out_5307849917674294752[8] = 0.0;
   out_5307849917674294752[9] = 0.0;
   out_5307849917674294752[10] = 0.0;
   out_5307849917674294752[11] = 0.0;
   out_5307849917674294752[12] = 0.0;
   out_5307849917674294752[13] = 0.0;
   out_5307849917674294752[14] = 0.0;
   out_5307849917674294752[15] = 0.0;
   out_5307849917674294752[16] = 0.0;
   out_5307849917674294752[17] = 0.0;
   out_5307849917674294752[18] = 0.0;
   out_5307849917674294752[19] = 1.0;
   out_5307849917674294752[20] = 0.0;
   out_5307849917674294752[21] = 0.0;
   out_5307849917674294752[22] = 0.0;
   out_5307849917674294752[23] = 0.0;
   out_5307849917674294752[24] = 0.0;
   out_5307849917674294752[25] = 0.0;
   out_5307849917674294752[26] = 0.0;
   out_5307849917674294752[27] = 0.0;
   out_5307849917674294752[28] = 0.0;
   out_5307849917674294752[29] = 0.0;
   out_5307849917674294752[30] = 0.0;
   out_5307849917674294752[31] = 0.0;
   out_5307849917674294752[32] = 0.0;
   out_5307849917674294752[33] = 0.0;
   out_5307849917674294752[34] = 0.0;
   out_5307849917674294752[35] = 0.0;
   out_5307849917674294752[36] = 0.0;
   out_5307849917674294752[37] = 0.0;
   out_5307849917674294752[38] = 1.0;
   out_5307849917674294752[39] = 0.0;
   out_5307849917674294752[40] = 0.0;
   out_5307849917674294752[41] = 0.0;
   out_5307849917674294752[42] = 0.0;
   out_5307849917674294752[43] = 0.0;
   out_5307849917674294752[44] = 0.0;
   out_5307849917674294752[45] = 0.0;
   out_5307849917674294752[46] = 0.0;
   out_5307849917674294752[47] = 0.0;
   out_5307849917674294752[48] = 0.0;
   out_5307849917674294752[49] = 0.0;
   out_5307849917674294752[50] = 0.0;
   out_5307849917674294752[51] = 0.0;
   out_5307849917674294752[52] = 0.0;
   out_5307849917674294752[53] = 0.0;
   out_5307849917674294752[54] = 0.0;
   out_5307849917674294752[55] = 0.0;
   out_5307849917674294752[56] = 0.0;
   out_5307849917674294752[57] = 1.0;
   out_5307849917674294752[58] = 0.0;
   out_5307849917674294752[59] = 0.0;
   out_5307849917674294752[60] = 0.0;
   out_5307849917674294752[61] = 0.0;
   out_5307849917674294752[62] = 0.0;
   out_5307849917674294752[63] = 0.0;
   out_5307849917674294752[64] = 0.0;
   out_5307849917674294752[65] = 0.0;
   out_5307849917674294752[66] = 0.0;
   out_5307849917674294752[67] = 0.0;
   out_5307849917674294752[68] = 0.0;
   out_5307849917674294752[69] = 0.0;
   out_5307849917674294752[70] = 0.0;
   out_5307849917674294752[71] = 0.0;
   out_5307849917674294752[72] = 0.0;
   out_5307849917674294752[73] = 0.0;
   out_5307849917674294752[74] = 0.0;
   out_5307849917674294752[75] = 0.0;
   out_5307849917674294752[76] = 1.0;
   out_5307849917674294752[77] = 0.0;
   out_5307849917674294752[78] = 0.0;
   out_5307849917674294752[79] = 0.0;
   out_5307849917674294752[80] = 0.0;
   out_5307849917674294752[81] = 0.0;
   out_5307849917674294752[82] = 0.0;
   out_5307849917674294752[83] = 0.0;
   out_5307849917674294752[84] = 0.0;
   out_5307849917674294752[85] = 0.0;
   out_5307849917674294752[86] = 0.0;
   out_5307849917674294752[87] = 0.0;
   out_5307849917674294752[88] = 0.0;
   out_5307849917674294752[89] = 0.0;
   out_5307849917674294752[90] = 0.0;
   out_5307849917674294752[91] = 0.0;
   out_5307849917674294752[92] = 0.0;
   out_5307849917674294752[93] = 0.0;
   out_5307849917674294752[94] = 0.0;
   out_5307849917674294752[95] = 1.0;
   out_5307849917674294752[96] = 0.0;
   out_5307849917674294752[97] = 0.0;
   out_5307849917674294752[98] = 0.0;
   out_5307849917674294752[99] = 0.0;
   out_5307849917674294752[100] = 0.0;
   out_5307849917674294752[101] = 0.0;
   out_5307849917674294752[102] = 0.0;
   out_5307849917674294752[103] = 0.0;
   out_5307849917674294752[104] = 0.0;
   out_5307849917674294752[105] = 0.0;
   out_5307849917674294752[106] = 0.0;
   out_5307849917674294752[107] = 0.0;
   out_5307849917674294752[108] = 0.0;
   out_5307849917674294752[109] = 0.0;
   out_5307849917674294752[110] = 0.0;
   out_5307849917674294752[111] = 0.0;
   out_5307849917674294752[112] = 0.0;
   out_5307849917674294752[113] = 0.0;
   out_5307849917674294752[114] = 1.0;
   out_5307849917674294752[115] = 0.0;
   out_5307849917674294752[116] = 0.0;
   out_5307849917674294752[117] = 0.0;
   out_5307849917674294752[118] = 0.0;
   out_5307849917674294752[119] = 0.0;
   out_5307849917674294752[120] = 0.0;
   out_5307849917674294752[121] = 0.0;
   out_5307849917674294752[122] = 0.0;
   out_5307849917674294752[123] = 0.0;
   out_5307849917674294752[124] = 0.0;
   out_5307849917674294752[125] = 0.0;
   out_5307849917674294752[126] = 0.0;
   out_5307849917674294752[127] = 0.0;
   out_5307849917674294752[128] = 0.0;
   out_5307849917674294752[129] = 0.0;
   out_5307849917674294752[130] = 0.0;
   out_5307849917674294752[131] = 0.0;
   out_5307849917674294752[132] = 0.0;
   out_5307849917674294752[133] = 1.0;
   out_5307849917674294752[134] = 0.0;
   out_5307849917674294752[135] = 0.0;
   out_5307849917674294752[136] = 0.0;
   out_5307849917674294752[137] = 0.0;
   out_5307849917674294752[138] = 0.0;
   out_5307849917674294752[139] = 0.0;
   out_5307849917674294752[140] = 0.0;
   out_5307849917674294752[141] = 0.0;
   out_5307849917674294752[142] = 0.0;
   out_5307849917674294752[143] = 0.0;
   out_5307849917674294752[144] = 0.0;
   out_5307849917674294752[145] = 0.0;
   out_5307849917674294752[146] = 0.0;
   out_5307849917674294752[147] = 0.0;
   out_5307849917674294752[148] = 0.0;
   out_5307849917674294752[149] = 0.0;
   out_5307849917674294752[150] = 0.0;
   out_5307849917674294752[151] = 0.0;
   out_5307849917674294752[152] = 1.0;
   out_5307849917674294752[153] = 0.0;
   out_5307849917674294752[154] = 0.0;
   out_5307849917674294752[155] = 0.0;
   out_5307849917674294752[156] = 0.0;
   out_5307849917674294752[157] = 0.0;
   out_5307849917674294752[158] = 0.0;
   out_5307849917674294752[159] = 0.0;
   out_5307849917674294752[160] = 0.0;
   out_5307849917674294752[161] = 0.0;
   out_5307849917674294752[162] = 0.0;
   out_5307849917674294752[163] = 0.0;
   out_5307849917674294752[164] = 0.0;
   out_5307849917674294752[165] = 0.0;
   out_5307849917674294752[166] = 0.0;
   out_5307849917674294752[167] = 0.0;
   out_5307849917674294752[168] = 0.0;
   out_5307849917674294752[169] = 0.0;
   out_5307849917674294752[170] = 0.0;
   out_5307849917674294752[171] = 1.0;
   out_5307849917674294752[172] = 0.0;
   out_5307849917674294752[173] = 0.0;
   out_5307849917674294752[174] = 0.0;
   out_5307849917674294752[175] = 0.0;
   out_5307849917674294752[176] = 0.0;
   out_5307849917674294752[177] = 0.0;
   out_5307849917674294752[178] = 0.0;
   out_5307849917674294752[179] = 0.0;
   out_5307849917674294752[180] = 0.0;
   out_5307849917674294752[181] = 0.0;
   out_5307849917674294752[182] = 0.0;
   out_5307849917674294752[183] = 0.0;
   out_5307849917674294752[184] = 0.0;
   out_5307849917674294752[185] = 0.0;
   out_5307849917674294752[186] = 0.0;
   out_5307849917674294752[187] = 0.0;
   out_5307849917674294752[188] = 0.0;
   out_5307849917674294752[189] = 0.0;
   out_5307849917674294752[190] = 1.0;
   out_5307849917674294752[191] = 0.0;
   out_5307849917674294752[192] = 0.0;
   out_5307849917674294752[193] = 0.0;
   out_5307849917674294752[194] = 0.0;
   out_5307849917674294752[195] = 0.0;
   out_5307849917674294752[196] = 0.0;
   out_5307849917674294752[197] = 0.0;
   out_5307849917674294752[198] = 0.0;
   out_5307849917674294752[199] = 0.0;
   out_5307849917674294752[200] = 0.0;
   out_5307849917674294752[201] = 0.0;
   out_5307849917674294752[202] = 0.0;
   out_5307849917674294752[203] = 0.0;
   out_5307849917674294752[204] = 0.0;
   out_5307849917674294752[205] = 0.0;
   out_5307849917674294752[206] = 0.0;
   out_5307849917674294752[207] = 0.0;
   out_5307849917674294752[208] = 0.0;
   out_5307849917674294752[209] = 1.0;
   out_5307849917674294752[210] = 0.0;
   out_5307849917674294752[211] = 0.0;
   out_5307849917674294752[212] = 0.0;
   out_5307849917674294752[213] = 0.0;
   out_5307849917674294752[214] = 0.0;
   out_5307849917674294752[215] = 0.0;
   out_5307849917674294752[216] = 0.0;
   out_5307849917674294752[217] = 0.0;
   out_5307849917674294752[218] = 0.0;
   out_5307849917674294752[219] = 0.0;
   out_5307849917674294752[220] = 0.0;
   out_5307849917674294752[221] = 0.0;
   out_5307849917674294752[222] = 0.0;
   out_5307849917674294752[223] = 0.0;
   out_5307849917674294752[224] = 0.0;
   out_5307849917674294752[225] = 0.0;
   out_5307849917674294752[226] = 0.0;
   out_5307849917674294752[227] = 0.0;
   out_5307849917674294752[228] = 1.0;
   out_5307849917674294752[229] = 0.0;
   out_5307849917674294752[230] = 0.0;
   out_5307849917674294752[231] = 0.0;
   out_5307849917674294752[232] = 0.0;
   out_5307849917674294752[233] = 0.0;
   out_5307849917674294752[234] = 0.0;
   out_5307849917674294752[235] = 0.0;
   out_5307849917674294752[236] = 0.0;
   out_5307849917674294752[237] = 0.0;
   out_5307849917674294752[238] = 0.0;
   out_5307849917674294752[239] = 0.0;
   out_5307849917674294752[240] = 0.0;
   out_5307849917674294752[241] = 0.0;
   out_5307849917674294752[242] = 0.0;
   out_5307849917674294752[243] = 0.0;
   out_5307849917674294752[244] = 0.0;
   out_5307849917674294752[245] = 0.0;
   out_5307849917674294752[246] = 0.0;
   out_5307849917674294752[247] = 1.0;
   out_5307849917674294752[248] = 0.0;
   out_5307849917674294752[249] = 0.0;
   out_5307849917674294752[250] = 0.0;
   out_5307849917674294752[251] = 0.0;
   out_5307849917674294752[252] = 0.0;
   out_5307849917674294752[253] = 0.0;
   out_5307849917674294752[254] = 0.0;
   out_5307849917674294752[255] = 0.0;
   out_5307849917674294752[256] = 0.0;
   out_5307849917674294752[257] = 0.0;
   out_5307849917674294752[258] = 0.0;
   out_5307849917674294752[259] = 0.0;
   out_5307849917674294752[260] = 0.0;
   out_5307849917674294752[261] = 0.0;
   out_5307849917674294752[262] = 0.0;
   out_5307849917674294752[263] = 0.0;
   out_5307849917674294752[264] = 0.0;
   out_5307849917674294752[265] = 0.0;
   out_5307849917674294752[266] = 1.0;
   out_5307849917674294752[267] = 0.0;
   out_5307849917674294752[268] = 0.0;
   out_5307849917674294752[269] = 0.0;
   out_5307849917674294752[270] = 0.0;
   out_5307849917674294752[271] = 0.0;
   out_5307849917674294752[272] = 0.0;
   out_5307849917674294752[273] = 0.0;
   out_5307849917674294752[274] = 0.0;
   out_5307849917674294752[275] = 0.0;
   out_5307849917674294752[276] = 0.0;
   out_5307849917674294752[277] = 0.0;
   out_5307849917674294752[278] = 0.0;
   out_5307849917674294752[279] = 0.0;
   out_5307849917674294752[280] = 0.0;
   out_5307849917674294752[281] = 0.0;
   out_5307849917674294752[282] = 0.0;
   out_5307849917674294752[283] = 0.0;
   out_5307849917674294752[284] = 0.0;
   out_5307849917674294752[285] = 1.0;
   out_5307849917674294752[286] = 0.0;
   out_5307849917674294752[287] = 0.0;
   out_5307849917674294752[288] = 0.0;
   out_5307849917674294752[289] = 0.0;
   out_5307849917674294752[290] = 0.0;
   out_5307849917674294752[291] = 0.0;
   out_5307849917674294752[292] = 0.0;
   out_5307849917674294752[293] = 0.0;
   out_5307849917674294752[294] = 0.0;
   out_5307849917674294752[295] = 0.0;
   out_5307849917674294752[296] = 0.0;
   out_5307849917674294752[297] = 0.0;
   out_5307849917674294752[298] = 0.0;
   out_5307849917674294752[299] = 0.0;
   out_5307849917674294752[300] = 0.0;
   out_5307849917674294752[301] = 0.0;
   out_5307849917674294752[302] = 0.0;
   out_5307849917674294752[303] = 0.0;
   out_5307849917674294752[304] = 1.0;
   out_5307849917674294752[305] = 0.0;
   out_5307849917674294752[306] = 0.0;
   out_5307849917674294752[307] = 0.0;
   out_5307849917674294752[308] = 0.0;
   out_5307849917674294752[309] = 0.0;
   out_5307849917674294752[310] = 0.0;
   out_5307849917674294752[311] = 0.0;
   out_5307849917674294752[312] = 0.0;
   out_5307849917674294752[313] = 0.0;
   out_5307849917674294752[314] = 0.0;
   out_5307849917674294752[315] = 0.0;
   out_5307849917674294752[316] = 0.0;
   out_5307849917674294752[317] = 0.0;
   out_5307849917674294752[318] = 0.0;
   out_5307849917674294752[319] = 0.0;
   out_5307849917674294752[320] = 0.0;
   out_5307849917674294752[321] = 0.0;
   out_5307849917674294752[322] = 0.0;
   out_5307849917674294752[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_3929566488353935407) {
   out_3929566488353935407[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_3929566488353935407[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_3929566488353935407[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_3929566488353935407[3] = dt*state[12] + state[3];
   out_3929566488353935407[4] = dt*state[13] + state[4];
   out_3929566488353935407[5] = dt*state[14] + state[5];
   out_3929566488353935407[6] = state[6];
   out_3929566488353935407[7] = state[7];
   out_3929566488353935407[8] = state[8];
   out_3929566488353935407[9] = state[9];
   out_3929566488353935407[10] = state[10];
   out_3929566488353935407[11] = state[11];
   out_3929566488353935407[12] = state[12];
   out_3929566488353935407[13] = state[13];
   out_3929566488353935407[14] = state[14];
   out_3929566488353935407[15] = state[15];
   out_3929566488353935407[16] = state[16];
   out_3929566488353935407[17] = state[17];
}
void F_fun(double *state, double dt, double *out_7175672084270467645) {
   out_7175672084270467645[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_7175672084270467645[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_7175672084270467645[2] = 0;
   out_7175672084270467645[3] = 0;
   out_7175672084270467645[4] = 0;
   out_7175672084270467645[5] = 0;
   out_7175672084270467645[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_7175672084270467645[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_7175672084270467645[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_7175672084270467645[9] = 0;
   out_7175672084270467645[10] = 0;
   out_7175672084270467645[11] = 0;
   out_7175672084270467645[12] = 0;
   out_7175672084270467645[13] = 0;
   out_7175672084270467645[14] = 0;
   out_7175672084270467645[15] = 0;
   out_7175672084270467645[16] = 0;
   out_7175672084270467645[17] = 0;
   out_7175672084270467645[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_7175672084270467645[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_7175672084270467645[20] = 0;
   out_7175672084270467645[21] = 0;
   out_7175672084270467645[22] = 0;
   out_7175672084270467645[23] = 0;
   out_7175672084270467645[24] = 0;
   out_7175672084270467645[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_7175672084270467645[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_7175672084270467645[27] = 0;
   out_7175672084270467645[28] = 0;
   out_7175672084270467645[29] = 0;
   out_7175672084270467645[30] = 0;
   out_7175672084270467645[31] = 0;
   out_7175672084270467645[32] = 0;
   out_7175672084270467645[33] = 0;
   out_7175672084270467645[34] = 0;
   out_7175672084270467645[35] = 0;
   out_7175672084270467645[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_7175672084270467645[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_7175672084270467645[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_7175672084270467645[39] = 0;
   out_7175672084270467645[40] = 0;
   out_7175672084270467645[41] = 0;
   out_7175672084270467645[42] = 0;
   out_7175672084270467645[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_7175672084270467645[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_7175672084270467645[45] = 0;
   out_7175672084270467645[46] = 0;
   out_7175672084270467645[47] = 0;
   out_7175672084270467645[48] = 0;
   out_7175672084270467645[49] = 0;
   out_7175672084270467645[50] = 0;
   out_7175672084270467645[51] = 0;
   out_7175672084270467645[52] = 0;
   out_7175672084270467645[53] = 0;
   out_7175672084270467645[54] = 0;
   out_7175672084270467645[55] = 0;
   out_7175672084270467645[56] = 0;
   out_7175672084270467645[57] = 1;
   out_7175672084270467645[58] = 0;
   out_7175672084270467645[59] = 0;
   out_7175672084270467645[60] = 0;
   out_7175672084270467645[61] = 0;
   out_7175672084270467645[62] = 0;
   out_7175672084270467645[63] = 0;
   out_7175672084270467645[64] = 0;
   out_7175672084270467645[65] = 0;
   out_7175672084270467645[66] = dt;
   out_7175672084270467645[67] = 0;
   out_7175672084270467645[68] = 0;
   out_7175672084270467645[69] = 0;
   out_7175672084270467645[70] = 0;
   out_7175672084270467645[71] = 0;
   out_7175672084270467645[72] = 0;
   out_7175672084270467645[73] = 0;
   out_7175672084270467645[74] = 0;
   out_7175672084270467645[75] = 0;
   out_7175672084270467645[76] = 1;
   out_7175672084270467645[77] = 0;
   out_7175672084270467645[78] = 0;
   out_7175672084270467645[79] = 0;
   out_7175672084270467645[80] = 0;
   out_7175672084270467645[81] = 0;
   out_7175672084270467645[82] = 0;
   out_7175672084270467645[83] = 0;
   out_7175672084270467645[84] = 0;
   out_7175672084270467645[85] = dt;
   out_7175672084270467645[86] = 0;
   out_7175672084270467645[87] = 0;
   out_7175672084270467645[88] = 0;
   out_7175672084270467645[89] = 0;
   out_7175672084270467645[90] = 0;
   out_7175672084270467645[91] = 0;
   out_7175672084270467645[92] = 0;
   out_7175672084270467645[93] = 0;
   out_7175672084270467645[94] = 0;
   out_7175672084270467645[95] = 1;
   out_7175672084270467645[96] = 0;
   out_7175672084270467645[97] = 0;
   out_7175672084270467645[98] = 0;
   out_7175672084270467645[99] = 0;
   out_7175672084270467645[100] = 0;
   out_7175672084270467645[101] = 0;
   out_7175672084270467645[102] = 0;
   out_7175672084270467645[103] = 0;
   out_7175672084270467645[104] = dt;
   out_7175672084270467645[105] = 0;
   out_7175672084270467645[106] = 0;
   out_7175672084270467645[107] = 0;
   out_7175672084270467645[108] = 0;
   out_7175672084270467645[109] = 0;
   out_7175672084270467645[110] = 0;
   out_7175672084270467645[111] = 0;
   out_7175672084270467645[112] = 0;
   out_7175672084270467645[113] = 0;
   out_7175672084270467645[114] = 1;
   out_7175672084270467645[115] = 0;
   out_7175672084270467645[116] = 0;
   out_7175672084270467645[117] = 0;
   out_7175672084270467645[118] = 0;
   out_7175672084270467645[119] = 0;
   out_7175672084270467645[120] = 0;
   out_7175672084270467645[121] = 0;
   out_7175672084270467645[122] = 0;
   out_7175672084270467645[123] = 0;
   out_7175672084270467645[124] = 0;
   out_7175672084270467645[125] = 0;
   out_7175672084270467645[126] = 0;
   out_7175672084270467645[127] = 0;
   out_7175672084270467645[128] = 0;
   out_7175672084270467645[129] = 0;
   out_7175672084270467645[130] = 0;
   out_7175672084270467645[131] = 0;
   out_7175672084270467645[132] = 0;
   out_7175672084270467645[133] = 1;
   out_7175672084270467645[134] = 0;
   out_7175672084270467645[135] = 0;
   out_7175672084270467645[136] = 0;
   out_7175672084270467645[137] = 0;
   out_7175672084270467645[138] = 0;
   out_7175672084270467645[139] = 0;
   out_7175672084270467645[140] = 0;
   out_7175672084270467645[141] = 0;
   out_7175672084270467645[142] = 0;
   out_7175672084270467645[143] = 0;
   out_7175672084270467645[144] = 0;
   out_7175672084270467645[145] = 0;
   out_7175672084270467645[146] = 0;
   out_7175672084270467645[147] = 0;
   out_7175672084270467645[148] = 0;
   out_7175672084270467645[149] = 0;
   out_7175672084270467645[150] = 0;
   out_7175672084270467645[151] = 0;
   out_7175672084270467645[152] = 1;
   out_7175672084270467645[153] = 0;
   out_7175672084270467645[154] = 0;
   out_7175672084270467645[155] = 0;
   out_7175672084270467645[156] = 0;
   out_7175672084270467645[157] = 0;
   out_7175672084270467645[158] = 0;
   out_7175672084270467645[159] = 0;
   out_7175672084270467645[160] = 0;
   out_7175672084270467645[161] = 0;
   out_7175672084270467645[162] = 0;
   out_7175672084270467645[163] = 0;
   out_7175672084270467645[164] = 0;
   out_7175672084270467645[165] = 0;
   out_7175672084270467645[166] = 0;
   out_7175672084270467645[167] = 0;
   out_7175672084270467645[168] = 0;
   out_7175672084270467645[169] = 0;
   out_7175672084270467645[170] = 0;
   out_7175672084270467645[171] = 1;
   out_7175672084270467645[172] = 0;
   out_7175672084270467645[173] = 0;
   out_7175672084270467645[174] = 0;
   out_7175672084270467645[175] = 0;
   out_7175672084270467645[176] = 0;
   out_7175672084270467645[177] = 0;
   out_7175672084270467645[178] = 0;
   out_7175672084270467645[179] = 0;
   out_7175672084270467645[180] = 0;
   out_7175672084270467645[181] = 0;
   out_7175672084270467645[182] = 0;
   out_7175672084270467645[183] = 0;
   out_7175672084270467645[184] = 0;
   out_7175672084270467645[185] = 0;
   out_7175672084270467645[186] = 0;
   out_7175672084270467645[187] = 0;
   out_7175672084270467645[188] = 0;
   out_7175672084270467645[189] = 0;
   out_7175672084270467645[190] = 1;
   out_7175672084270467645[191] = 0;
   out_7175672084270467645[192] = 0;
   out_7175672084270467645[193] = 0;
   out_7175672084270467645[194] = 0;
   out_7175672084270467645[195] = 0;
   out_7175672084270467645[196] = 0;
   out_7175672084270467645[197] = 0;
   out_7175672084270467645[198] = 0;
   out_7175672084270467645[199] = 0;
   out_7175672084270467645[200] = 0;
   out_7175672084270467645[201] = 0;
   out_7175672084270467645[202] = 0;
   out_7175672084270467645[203] = 0;
   out_7175672084270467645[204] = 0;
   out_7175672084270467645[205] = 0;
   out_7175672084270467645[206] = 0;
   out_7175672084270467645[207] = 0;
   out_7175672084270467645[208] = 0;
   out_7175672084270467645[209] = 1;
   out_7175672084270467645[210] = 0;
   out_7175672084270467645[211] = 0;
   out_7175672084270467645[212] = 0;
   out_7175672084270467645[213] = 0;
   out_7175672084270467645[214] = 0;
   out_7175672084270467645[215] = 0;
   out_7175672084270467645[216] = 0;
   out_7175672084270467645[217] = 0;
   out_7175672084270467645[218] = 0;
   out_7175672084270467645[219] = 0;
   out_7175672084270467645[220] = 0;
   out_7175672084270467645[221] = 0;
   out_7175672084270467645[222] = 0;
   out_7175672084270467645[223] = 0;
   out_7175672084270467645[224] = 0;
   out_7175672084270467645[225] = 0;
   out_7175672084270467645[226] = 0;
   out_7175672084270467645[227] = 0;
   out_7175672084270467645[228] = 1;
   out_7175672084270467645[229] = 0;
   out_7175672084270467645[230] = 0;
   out_7175672084270467645[231] = 0;
   out_7175672084270467645[232] = 0;
   out_7175672084270467645[233] = 0;
   out_7175672084270467645[234] = 0;
   out_7175672084270467645[235] = 0;
   out_7175672084270467645[236] = 0;
   out_7175672084270467645[237] = 0;
   out_7175672084270467645[238] = 0;
   out_7175672084270467645[239] = 0;
   out_7175672084270467645[240] = 0;
   out_7175672084270467645[241] = 0;
   out_7175672084270467645[242] = 0;
   out_7175672084270467645[243] = 0;
   out_7175672084270467645[244] = 0;
   out_7175672084270467645[245] = 0;
   out_7175672084270467645[246] = 0;
   out_7175672084270467645[247] = 1;
   out_7175672084270467645[248] = 0;
   out_7175672084270467645[249] = 0;
   out_7175672084270467645[250] = 0;
   out_7175672084270467645[251] = 0;
   out_7175672084270467645[252] = 0;
   out_7175672084270467645[253] = 0;
   out_7175672084270467645[254] = 0;
   out_7175672084270467645[255] = 0;
   out_7175672084270467645[256] = 0;
   out_7175672084270467645[257] = 0;
   out_7175672084270467645[258] = 0;
   out_7175672084270467645[259] = 0;
   out_7175672084270467645[260] = 0;
   out_7175672084270467645[261] = 0;
   out_7175672084270467645[262] = 0;
   out_7175672084270467645[263] = 0;
   out_7175672084270467645[264] = 0;
   out_7175672084270467645[265] = 0;
   out_7175672084270467645[266] = 1;
   out_7175672084270467645[267] = 0;
   out_7175672084270467645[268] = 0;
   out_7175672084270467645[269] = 0;
   out_7175672084270467645[270] = 0;
   out_7175672084270467645[271] = 0;
   out_7175672084270467645[272] = 0;
   out_7175672084270467645[273] = 0;
   out_7175672084270467645[274] = 0;
   out_7175672084270467645[275] = 0;
   out_7175672084270467645[276] = 0;
   out_7175672084270467645[277] = 0;
   out_7175672084270467645[278] = 0;
   out_7175672084270467645[279] = 0;
   out_7175672084270467645[280] = 0;
   out_7175672084270467645[281] = 0;
   out_7175672084270467645[282] = 0;
   out_7175672084270467645[283] = 0;
   out_7175672084270467645[284] = 0;
   out_7175672084270467645[285] = 1;
   out_7175672084270467645[286] = 0;
   out_7175672084270467645[287] = 0;
   out_7175672084270467645[288] = 0;
   out_7175672084270467645[289] = 0;
   out_7175672084270467645[290] = 0;
   out_7175672084270467645[291] = 0;
   out_7175672084270467645[292] = 0;
   out_7175672084270467645[293] = 0;
   out_7175672084270467645[294] = 0;
   out_7175672084270467645[295] = 0;
   out_7175672084270467645[296] = 0;
   out_7175672084270467645[297] = 0;
   out_7175672084270467645[298] = 0;
   out_7175672084270467645[299] = 0;
   out_7175672084270467645[300] = 0;
   out_7175672084270467645[301] = 0;
   out_7175672084270467645[302] = 0;
   out_7175672084270467645[303] = 0;
   out_7175672084270467645[304] = 1;
   out_7175672084270467645[305] = 0;
   out_7175672084270467645[306] = 0;
   out_7175672084270467645[307] = 0;
   out_7175672084270467645[308] = 0;
   out_7175672084270467645[309] = 0;
   out_7175672084270467645[310] = 0;
   out_7175672084270467645[311] = 0;
   out_7175672084270467645[312] = 0;
   out_7175672084270467645[313] = 0;
   out_7175672084270467645[314] = 0;
   out_7175672084270467645[315] = 0;
   out_7175672084270467645[316] = 0;
   out_7175672084270467645[317] = 0;
   out_7175672084270467645[318] = 0;
   out_7175672084270467645[319] = 0;
   out_7175672084270467645[320] = 0;
   out_7175672084270467645[321] = 0;
   out_7175672084270467645[322] = 0;
   out_7175672084270467645[323] = 1;
}
void h_4(double *state, double *unused, double *out_762986349532875001) {
   out_762986349532875001[0] = state[6] + state[9];
   out_762986349532875001[1] = state[7] + state[10];
   out_762986349532875001[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_4125909736121572372) {
   out_4125909736121572372[0] = 0;
   out_4125909736121572372[1] = 0;
   out_4125909736121572372[2] = 0;
   out_4125909736121572372[3] = 0;
   out_4125909736121572372[4] = 0;
   out_4125909736121572372[5] = 0;
   out_4125909736121572372[6] = 1;
   out_4125909736121572372[7] = 0;
   out_4125909736121572372[8] = 0;
   out_4125909736121572372[9] = 1;
   out_4125909736121572372[10] = 0;
   out_4125909736121572372[11] = 0;
   out_4125909736121572372[12] = 0;
   out_4125909736121572372[13] = 0;
   out_4125909736121572372[14] = 0;
   out_4125909736121572372[15] = 0;
   out_4125909736121572372[16] = 0;
   out_4125909736121572372[17] = 0;
   out_4125909736121572372[18] = 0;
   out_4125909736121572372[19] = 0;
   out_4125909736121572372[20] = 0;
   out_4125909736121572372[21] = 0;
   out_4125909736121572372[22] = 0;
   out_4125909736121572372[23] = 0;
   out_4125909736121572372[24] = 0;
   out_4125909736121572372[25] = 1;
   out_4125909736121572372[26] = 0;
   out_4125909736121572372[27] = 0;
   out_4125909736121572372[28] = 1;
   out_4125909736121572372[29] = 0;
   out_4125909736121572372[30] = 0;
   out_4125909736121572372[31] = 0;
   out_4125909736121572372[32] = 0;
   out_4125909736121572372[33] = 0;
   out_4125909736121572372[34] = 0;
   out_4125909736121572372[35] = 0;
   out_4125909736121572372[36] = 0;
   out_4125909736121572372[37] = 0;
   out_4125909736121572372[38] = 0;
   out_4125909736121572372[39] = 0;
   out_4125909736121572372[40] = 0;
   out_4125909736121572372[41] = 0;
   out_4125909736121572372[42] = 0;
   out_4125909736121572372[43] = 0;
   out_4125909736121572372[44] = 1;
   out_4125909736121572372[45] = 0;
   out_4125909736121572372[46] = 0;
   out_4125909736121572372[47] = 1;
   out_4125909736121572372[48] = 0;
   out_4125909736121572372[49] = 0;
   out_4125909736121572372[50] = 0;
   out_4125909736121572372[51] = 0;
   out_4125909736121572372[52] = 0;
   out_4125909736121572372[53] = 0;
}
void h_10(double *state, double *unused, double *out_895627576329681885) {
   out_895627576329681885[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_895627576329681885[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_895627576329681885[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_7661760800865717506) {
   out_7661760800865717506[0] = 0;
   out_7661760800865717506[1] = 9.8100000000000005*cos(state[1]);
   out_7661760800865717506[2] = 0;
   out_7661760800865717506[3] = 0;
   out_7661760800865717506[4] = -state[8];
   out_7661760800865717506[5] = state[7];
   out_7661760800865717506[6] = 0;
   out_7661760800865717506[7] = state[5];
   out_7661760800865717506[8] = -state[4];
   out_7661760800865717506[9] = 0;
   out_7661760800865717506[10] = 0;
   out_7661760800865717506[11] = 0;
   out_7661760800865717506[12] = 1;
   out_7661760800865717506[13] = 0;
   out_7661760800865717506[14] = 0;
   out_7661760800865717506[15] = 1;
   out_7661760800865717506[16] = 0;
   out_7661760800865717506[17] = 0;
   out_7661760800865717506[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_7661760800865717506[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_7661760800865717506[20] = 0;
   out_7661760800865717506[21] = state[8];
   out_7661760800865717506[22] = 0;
   out_7661760800865717506[23] = -state[6];
   out_7661760800865717506[24] = -state[5];
   out_7661760800865717506[25] = 0;
   out_7661760800865717506[26] = state[3];
   out_7661760800865717506[27] = 0;
   out_7661760800865717506[28] = 0;
   out_7661760800865717506[29] = 0;
   out_7661760800865717506[30] = 0;
   out_7661760800865717506[31] = 1;
   out_7661760800865717506[32] = 0;
   out_7661760800865717506[33] = 0;
   out_7661760800865717506[34] = 1;
   out_7661760800865717506[35] = 0;
   out_7661760800865717506[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_7661760800865717506[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_7661760800865717506[38] = 0;
   out_7661760800865717506[39] = -state[7];
   out_7661760800865717506[40] = state[6];
   out_7661760800865717506[41] = 0;
   out_7661760800865717506[42] = state[4];
   out_7661760800865717506[43] = -state[3];
   out_7661760800865717506[44] = 0;
   out_7661760800865717506[45] = 0;
   out_7661760800865717506[46] = 0;
   out_7661760800865717506[47] = 0;
   out_7661760800865717506[48] = 0;
   out_7661760800865717506[49] = 0;
   out_7661760800865717506[50] = 1;
   out_7661760800865717506[51] = 0;
   out_7661760800865717506[52] = 0;
   out_7661760800865717506[53] = 1;
}
void h_13(double *state, double *unused, double *out_4233008290515268972) {
   out_4233008290515268972[0] = state[3];
   out_4233008290515268972[1] = state[4];
   out_4233008290515268972[2] = state[5];
}
void H_13(double *state, double *unused, double *out_913635910789239571) {
   out_913635910789239571[0] = 0;
   out_913635910789239571[1] = 0;
   out_913635910789239571[2] = 0;
   out_913635910789239571[3] = 1;
   out_913635910789239571[4] = 0;
   out_913635910789239571[5] = 0;
   out_913635910789239571[6] = 0;
   out_913635910789239571[7] = 0;
   out_913635910789239571[8] = 0;
   out_913635910789239571[9] = 0;
   out_913635910789239571[10] = 0;
   out_913635910789239571[11] = 0;
   out_913635910789239571[12] = 0;
   out_913635910789239571[13] = 0;
   out_913635910789239571[14] = 0;
   out_913635910789239571[15] = 0;
   out_913635910789239571[16] = 0;
   out_913635910789239571[17] = 0;
   out_913635910789239571[18] = 0;
   out_913635910789239571[19] = 0;
   out_913635910789239571[20] = 0;
   out_913635910789239571[21] = 0;
   out_913635910789239571[22] = 1;
   out_913635910789239571[23] = 0;
   out_913635910789239571[24] = 0;
   out_913635910789239571[25] = 0;
   out_913635910789239571[26] = 0;
   out_913635910789239571[27] = 0;
   out_913635910789239571[28] = 0;
   out_913635910789239571[29] = 0;
   out_913635910789239571[30] = 0;
   out_913635910789239571[31] = 0;
   out_913635910789239571[32] = 0;
   out_913635910789239571[33] = 0;
   out_913635910789239571[34] = 0;
   out_913635910789239571[35] = 0;
   out_913635910789239571[36] = 0;
   out_913635910789239571[37] = 0;
   out_913635910789239571[38] = 0;
   out_913635910789239571[39] = 0;
   out_913635910789239571[40] = 0;
   out_913635910789239571[41] = 1;
   out_913635910789239571[42] = 0;
   out_913635910789239571[43] = 0;
   out_913635910789239571[44] = 0;
   out_913635910789239571[45] = 0;
   out_913635910789239571[46] = 0;
   out_913635910789239571[47] = 0;
   out_913635910789239571[48] = 0;
   out_913635910789239571[49] = 0;
   out_913635910789239571[50] = 0;
   out_913635910789239571[51] = 0;
   out_913635910789239571[52] = 0;
   out_913635910789239571[53] = 0;
}
void h_14(double *state, double *unused, double *out_5980176444970125081) {
   out_5980176444970125081[0] = state[6];
   out_5980176444970125081[1] = state[7];
   out_5980176444970125081[2] = state[8];
}
void H_14(double *state, double *unused, double *out_162668879782087843) {
   out_162668879782087843[0] = 0;
   out_162668879782087843[1] = 0;
   out_162668879782087843[2] = 0;
   out_162668879782087843[3] = 0;
   out_162668879782087843[4] = 0;
   out_162668879782087843[5] = 0;
   out_162668879782087843[6] = 1;
   out_162668879782087843[7] = 0;
   out_162668879782087843[8] = 0;
   out_162668879782087843[9] = 0;
   out_162668879782087843[10] = 0;
   out_162668879782087843[11] = 0;
   out_162668879782087843[12] = 0;
   out_162668879782087843[13] = 0;
   out_162668879782087843[14] = 0;
   out_162668879782087843[15] = 0;
   out_162668879782087843[16] = 0;
   out_162668879782087843[17] = 0;
   out_162668879782087843[18] = 0;
   out_162668879782087843[19] = 0;
   out_162668879782087843[20] = 0;
   out_162668879782087843[21] = 0;
   out_162668879782087843[22] = 0;
   out_162668879782087843[23] = 0;
   out_162668879782087843[24] = 0;
   out_162668879782087843[25] = 1;
   out_162668879782087843[26] = 0;
   out_162668879782087843[27] = 0;
   out_162668879782087843[28] = 0;
   out_162668879782087843[29] = 0;
   out_162668879782087843[30] = 0;
   out_162668879782087843[31] = 0;
   out_162668879782087843[32] = 0;
   out_162668879782087843[33] = 0;
   out_162668879782087843[34] = 0;
   out_162668879782087843[35] = 0;
   out_162668879782087843[36] = 0;
   out_162668879782087843[37] = 0;
   out_162668879782087843[38] = 0;
   out_162668879782087843[39] = 0;
   out_162668879782087843[40] = 0;
   out_162668879782087843[41] = 0;
   out_162668879782087843[42] = 0;
   out_162668879782087843[43] = 0;
   out_162668879782087843[44] = 1;
   out_162668879782087843[45] = 0;
   out_162668879782087843[46] = 0;
   out_162668879782087843[47] = 0;
   out_162668879782087843[48] = 0;
   out_162668879782087843[49] = 0;
   out_162668879782087843[50] = 0;
   out_162668879782087843[51] = 0;
   out_162668879782087843[52] = 0;
   out_162668879782087843[53] = 0;
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
void pose_err_fun(double *nom_x, double *delta_x, double *out_1055807072610005846) {
  err_fun(nom_x, delta_x, out_1055807072610005846);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_983516364171912274) {
  inv_err_fun(nom_x, true_x, out_983516364171912274);
}
void pose_H_mod_fun(double *state, double *out_5307849917674294752) {
  H_mod_fun(state, out_5307849917674294752);
}
void pose_f_fun(double *state, double dt, double *out_3929566488353935407) {
  f_fun(state,  dt, out_3929566488353935407);
}
void pose_F_fun(double *state, double dt, double *out_7175672084270467645) {
  F_fun(state,  dt, out_7175672084270467645);
}
void pose_h_4(double *state, double *unused, double *out_762986349532875001) {
  h_4(state, unused, out_762986349532875001);
}
void pose_H_4(double *state, double *unused, double *out_4125909736121572372) {
  H_4(state, unused, out_4125909736121572372);
}
void pose_h_10(double *state, double *unused, double *out_895627576329681885) {
  h_10(state, unused, out_895627576329681885);
}
void pose_H_10(double *state, double *unused, double *out_7661760800865717506) {
  H_10(state, unused, out_7661760800865717506);
}
void pose_h_13(double *state, double *unused, double *out_4233008290515268972) {
  h_13(state, unused, out_4233008290515268972);
}
void pose_H_13(double *state, double *unused, double *out_913635910789239571) {
  H_13(state, unused, out_913635910789239571);
}
void pose_h_14(double *state, double *unused, double *out_5980176444970125081) {
  h_14(state, unused, out_5980176444970125081);
}
void pose_H_14(double *state, double *unused, double *out_162668879782087843) {
  H_14(state, unused, out_162668879782087843);
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
