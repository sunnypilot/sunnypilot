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
 *                      Code generated with SymPy 1.13.2                      *
 *                                                                            *
 *              See http://www.sympy.org/ for more information.               *
 *                                                                            *
 *                         This file is part of 'ekf'                         *
 ******************************************************************************/
void err_fun(double *nom_x, double *delta_x, double *out_3059021723261949722) {
   out_3059021723261949722[0] = delta_x[0] + nom_x[0];
   out_3059021723261949722[1] = delta_x[1] + nom_x[1];
   out_3059021723261949722[2] = delta_x[2] + nom_x[2];
   out_3059021723261949722[3] = delta_x[3] + nom_x[3];
   out_3059021723261949722[4] = delta_x[4] + nom_x[4];
   out_3059021723261949722[5] = delta_x[5] + nom_x[5];
   out_3059021723261949722[6] = delta_x[6] + nom_x[6];
   out_3059021723261949722[7] = delta_x[7] + nom_x[7];
   out_3059021723261949722[8] = delta_x[8] + nom_x[8];
   out_3059021723261949722[9] = delta_x[9] + nom_x[9];
   out_3059021723261949722[10] = delta_x[10] + nom_x[10];
   out_3059021723261949722[11] = delta_x[11] + nom_x[11];
   out_3059021723261949722[12] = delta_x[12] + nom_x[12];
   out_3059021723261949722[13] = delta_x[13] + nom_x[13];
   out_3059021723261949722[14] = delta_x[14] + nom_x[14];
   out_3059021723261949722[15] = delta_x[15] + nom_x[15];
   out_3059021723261949722[16] = delta_x[16] + nom_x[16];
   out_3059021723261949722[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_6771718338208051804) {
   out_6771718338208051804[0] = -nom_x[0] + true_x[0];
   out_6771718338208051804[1] = -nom_x[1] + true_x[1];
   out_6771718338208051804[2] = -nom_x[2] + true_x[2];
   out_6771718338208051804[3] = -nom_x[3] + true_x[3];
   out_6771718338208051804[4] = -nom_x[4] + true_x[4];
   out_6771718338208051804[5] = -nom_x[5] + true_x[5];
   out_6771718338208051804[6] = -nom_x[6] + true_x[6];
   out_6771718338208051804[7] = -nom_x[7] + true_x[7];
   out_6771718338208051804[8] = -nom_x[8] + true_x[8];
   out_6771718338208051804[9] = -nom_x[9] + true_x[9];
   out_6771718338208051804[10] = -nom_x[10] + true_x[10];
   out_6771718338208051804[11] = -nom_x[11] + true_x[11];
   out_6771718338208051804[12] = -nom_x[12] + true_x[12];
   out_6771718338208051804[13] = -nom_x[13] + true_x[13];
   out_6771718338208051804[14] = -nom_x[14] + true_x[14];
   out_6771718338208051804[15] = -nom_x[15] + true_x[15];
   out_6771718338208051804[16] = -nom_x[16] + true_x[16];
   out_6771718338208051804[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_1014308954846494831) {
   out_1014308954846494831[0] = 1.0;
   out_1014308954846494831[1] = 0.0;
   out_1014308954846494831[2] = 0.0;
   out_1014308954846494831[3] = 0.0;
   out_1014308954846494831[4] = 0.0;
   out_1014308954846494831[5] = 0.0;
   out_1014308954846494831[6] = 0.0;
   out_1014308954846494831[7] = 0.0;
   out_1014308954846494831[8] = 0.0;
   out_1014308954846494831[9] = 0.0;
   out_1014308954846494831[10] = 0.0;
   out_1014308954846494831[11] = 0.0;
   out_1014308954846494831[12] = 0.0;
   out_1014308954846494831[13] = 0.0;
   out_1014308954846494831[14] = 0.0;
   out_1014308954846494831[15] = 0.0;
   out_1014308954846494831[16] = 0.0;
   out_1014308954846494831[17] = 0.0;
   out_1014308954846494831[18] = 0.0;
   out_1014308954846494831[19] = 1.0;
   out_1014308954846494831[20] = 0.0;
   out_1014308954846494831[21] = 0.0;
   out_1014308954846494831[22] = 0.0;
   out_1014308954846494831[23] = 0.0;
   out_1014308954846494831[24] = 0.0;
   out_1014308954846494831[25] = 0.0;
   out_1014308954846494831[26] = 0.0;
   out_1014308954846494831[27] = 0.0;
   out_1014308954846494831[28] = 0.0;
   out_1014308954846494831[29] = 0.0;
   out_1014308954846494831[30] = 0.0;
   out_1014308954846494831[31] = 0.0;
   out_1014308954846494831[32] = 0.0;
   out_1014308954846494831[33] = 0.0;
   out_1014308954846494831[34] = 0.0;
   out_1014308954846494831[35] = 0.0;
   out_1014308954846494831[36] = 0.0;
   out_1014308954846494831[37] = 0.0;
   out_1014308954846494831[38] = 1.0;
   out_1014308954846494831[39] = 0.0;
   out_1014308954846494831[40] = 0.0;
   out_1014308954846494831[41] = 0.0;
   out_1014308954846494831[42] = 0.0;
   out_1014308954846494831[43] = 0.0;
   out_1014308954846494831[44] = 0.0;
   out_1014308954846494831[45] = 0.0;
   out_1014308954846494831[46] = 0.0;
   out_1014308954846494831[47] = 0.0;
   out_1014308954846494831[48] = 0.0;
   out_1014308954846494831[49] = 0.0;
   out_1014308954846494831[50] = 0.0;
   out_1014308954846494831[51] = 0.0;
   out_1014308954846494831[52] = 0.0;
   out_1014308954846494831[53] = 0.0;
   out_1014308954846494831[54] = 0.0;
   out_1014308954846494831[55] = 0.0;
   out_1014308954846494831[56] = 0.0;
   out_1014308954846494831[57] = 1.0;
   out_1014308954846494831[58] = 0.0;
   out_1014308954846494831[59] = 0.0;
   out_1014308954846494831[60] = 0.0;
   out_1014308954846494831[61] = 0.0;
   out_1014308954846494831[62] = 0.0;
   out_1014308954846494831[63] = 0.0;
   out_1014308954846494831[64] = 0.0;
   out_1014308954846494831[65] = 0.0;
   out_1014308954846494831[66] = 0.0;
   out_1014308954846494831[67] = 0.0;
   out_1014308954846494831[68] = 0.0;
   out_1014308954846494831[69] = 0.0;
   out_1014308954846494831[70] = 0.0;
   out_1014308954846494831[71] = 0.0;
   out_1014308954846494831[72] = 0.0;
   out_1014308954846494831[73] = 0.0;
   out_1014308954846494831[74] = 0.0;
   out_1014308954846494831[75] = 0.0;
   out_1014308954846494831[76] = 1.0;
   out_1014308954846494831[77] = 0.0;
   out_1014308954846494831[78] = 0.0;
   out_1014308954846494831[79] = 0.0;
   out_1014308954846494831[80] = 0.0;
   out_1014308954846494831[81] = 0.0;
   out_1014308954846494831[82] = 0.0;
   out_1014308954846494831[83] = 0.0;
   out_1014308954846494831[84] = 0.0;
   out_1014308954846494831[85] = 0.0;
   out_1014308954846494831[86] = 0.0;
   out_1014308954846494831[87] = 0.0;
   out_1014308954846494831[88] = 0.0;
   out_1014308954846494831[89] = 0.0;
   out_1014308954846494831[90] = 0.0;
   out_1014308954846494831[91] = 0.0;
   out_1014308954846494831[92] = 0.0;
   out_1014308954846494831[93] = 0.0;
   out_1014308954846494831[94] = 0.0;
   out_1014308954846494831[95] = 1.0;
   out_1014308954846494831[96] = 0.0;
   out_1014308954846494831[97] = 0.0;
   out_1014308954846494831[98] = 0.0;
   out_1014308954846494831[99] = 0.0;
   out_1014308954846494831[100] = 0.0;
   out_1014308954846494831[101] = 0.0;
   out_1014308954846494831[102] = 0.0;
   out_1014308954846494831[103] = 0.0;
   out_1014308954846494831[104] = 0.0;
   out_1014308954846494831[105] = 0.0;
   out_1014308954846494831[106] = 0.0;
   out_1014308954846494831[107] = 0.0;
   out_1014308954846494831[108] = 0.0;
   out_1014308954846494831[109] = 0.0;
   out_1014308954846494831[110] = 0.0;
   out_1014308954846494831[111] = 0.0;
   out_1014308954846494831[112] = 0.0;
   out_1014308954846494831[113] = 0.0;
   out_1014308954846494831[114] = 1.0;
   out_1014308954846494831[115] = 0.0;
   out_1014308954846494831[116] = 0.0;
   out_1014308954846494831[117] = 0.0;
   out_1014308954846494831[118] = 0.0;
   out_1014308954846494831[119] = 0.0;
   out_1014308954846494831[120] = 0.0;
   out_1014308954846494831[121] = 0.0;
   out_1014308954846494831[122] = 0.0;
   out_1014308954846494831[123] = 0.0;
   out_1014308954846494831[124] = 0.0;
   out_1014308954846494831[125] = 0.0;
   out_1014308954846494831[126] = 0.0;
   out_1014308954846494831[127] = 0.0;
   out_1014308954846494831[128] = 0.0;
   out_1014308954846494831[129] = 0.0;
   out_1014308954846494831[130] = 0.0;
   out_1014308954846494831[131] = 0.0;
   out_1014308954846494831[132] = 0.0;
   out_1014308954846494831[133] = 1.0;
   out_1014308954846494831[134] = 0.0;
   out_1014308954846494831[135] = 0.0;
   out_1014308954846494831[136] = 0.0;
   out_1014308954846494831[137] = 0.0;
   out_1014308954846494831[138] = 0.0;
   out_1014308954846494831[139] = 0.0;
   out_1014308954846494831[140] = 0.0;
   out_1014308954846494831[141] = 0.0;
   out_1014308954846494831[142] = 0.0;
   out_1014308954846494831[143] = 0.0;
   out_1014308954846494831[144] = 0.0;
   out_1014308954846494831[145] = 0.0;
   out_1014308954846494831[146] = 0.0;
   out_1014308954846494831[147] = 0.0;
   out_1014308954846494831[148] = 0.0;
   out_1014308954846494831[149] = 0.0;
   out_1014308954846494831[150] = 0.0;
   out_1014308954846494831[151] = 0.0;
   out_1014308954846494831[152] = 1.0;
   out_1014308954846494831[153] = 0.0;
   out_1014308954846494831[154] = 0.0;
   out_1014308954846494831[155] = 0.0;
   out_1014308954846494831[156] = 0.0;
   out_1014308954846494831[157] = 0.0;
   out_1014308954846494831[158] = 0.0;
   out_1014308954846494831[159] = 0.0;
   out_1014308954846494831[160] = 0.0;
   out_1014308954846494831[161] = 0.0;
   out_1014308954846494831[162] = 0.0;
   out_1014308954846494831[163] = 0.0;
   out_1014308954846494831[164] = 0.0;
   out_1014308954846494831[165] = 0.0;
   out_1014308954846494831[166] = 0.0;
   out_1014308954846494831[167] = 0.0;
   out_1014308954846494831[168] = 0.0;
   out_1014308954846494831[169] = 0.0;
   out_1014308954846494831[170] = 0.0;
   out_1014308954846494831[171] = 1.0;
   out_1014308954846494831[172] = 0.0;
   out_1014308954846494831[173] = 0.0;
   out_1014308954846494831[174] = 0.0;
   out_1014308954846494831[175] = 0.0;
   out_1014308954846494831[176] = 0.0;
   out_1014308954846494831[177] = 0.0;
   out_1014308954846494831[178] = 0.0;
   out_1014308954846494831[179] = 0.0;
   out_1014308954846494831[180] = 0.0;
   out_1014308954846494831[181] = 0.0;
   out_1014308954846494831[182] = 0.0;
   out_1014308954846494831[183] = 0.0;
   out_1014308954846494831[184] = 0.0;
   out_1014308954846494831[185] = 0.0;
   out_1014308954846494831[186] = 0.0;
   out_1014308954846494831[187] = 0.0;
   out_1014308954846494831[188] = 0.0;
   out_1014308954846494831[189] = 0.0;
   out_1014308954846494831[190] = 1.0;
   out_1014308954846494831[191] = 0.0;
   out_1014308954846494831[192] = 0.0;
   out_1014308954846494831[193] = 0.0;
   out_1014308954846494831[194] = 0.0;
   out_1014308954846494831[195] = 0.0;
   out_1014308954846494831[196] = 0.0;
   out_1014308954846494831[197] = 0.0;
   out_1014308954846494831[198] = 0.0;
   out_1014308954846494831[199] = 0.0;
   out_1014308954846494831[200] = 0.0;
   out_1014308954846494831[201] = 0.0;
   out_1014308954846494831[202] = 0.0;
   out_1014308954846494831[203] = 0.0;
   out_1014308954846494831[204] = 0.0;
   out_1014308954846494831[205] = 0.0;
   out_1014308954846494831[206] = 0.0;
   out_1014308954846494831[207] = 0.0;
   out_1014308954846494831[208] = 0.0;
   out_1014308954846494831[209] = 1.0;
   out_1014308954846494831[210] = 0.0;
   out_1014308954846494831[211] = 0.0;
   out_1014308954846494831[212] = 0.0;
   out_1014308954846494831[213] = 0.0;
   out_1014308954846494831[214] = 0.0;
   out_1014308954846494831[215] = 0.0;
   out_1014308954846494831[216] = 0.0;
   out_1014308954846494831[217] = 0.0;
   out_1014308954846494831[218] = 0.0;
   out_1014308954846494831[219] = 0.0;
   out_1014308954846494831[220] = 0.0;
   out_1014308954846494831[221] = 0.0;
   out_1014308954846494831[222] = 0.0;
   out_1014308954846494831[223] = 0.0;
   out_1014308954846494831[224] = 0.0;
   out_1014308954846494831[225] = 0.0;
   out_1014308954846494831[226] = 0.0;
   out_1014308954846494831[227] = 0.0;
   out_1014308954846494831[228] = 1.0;
   out_1014308954846494831[229] = 0.0;
   out_1014308954846494831[230] = 0.0;
   out_1014308954846494831[231] = 0.0;
   out_1014308954846494831[232] = 0.0;
   out_1014308954846494831[233] = 0.0;
   out_1014308954846494831[234] = 0.0;
   out_1014308954846494831[235] = 0.0;
   out_1014308954846494831[236] = 0.0;
   out_1014308954846494831[237] = 0.0;
   out_1014308954846494831[238] = 0.0;
   out_1014308954846494831[239] = 0.0;
   out_1014308954846494831[240] = 0.0;
   out_1014308954846494831[241] = 0.0;
   out_1014308954846494831[242] = 0.0;
   out_1014308954846494831[243] = 0.0;
   out_1014308954846494831[244] = 0.0;
   out_1014308954846494831[245] = 0.0;
   out_1014308954846494831[246] = 0.0;
   out_1014308954846494831[247] = 1.0;
   out_1014308954846494831[248] = 0.0;
   out_1014308954846494831[249] = 0.0;
   out_1014308954846494831[250] = 0.0;
   out_1014308954846494831[251] = 0.0;
   out_1014308954846494831[252] = 0.0;
   out_1014308954846494831[253] = 0.0;
   out_1014308954846494831[254] = 0.0;
   out_1014308954846494831[255] = 0.0;
   out_1014308954846494831[256] = 0.0;
   out_1014308954846494831[257] = 0.0;
   out_1014308954846494831[258] = 0.0;
   out_1014308954846494831[259] = 0.0;
   out_1014308954846494831[260] = 0.0;
   out_1014308954846494831[261] = 0.0;
   out_1014308954846494831[262] = 0.0;
   out_1014308954846494831[263] = 0.0;
   out_1014308954846494831[264] = 0.0;
   out_1014308954846494831[265] = 0.0;
   out_1014308954846494831[266] = 1.0;
   out_1014308954846494831[267] = 0.0;
   out_1014308954846494831[268] = 0.0;
   out_1014308954846494831[269] = 0.0;
   out_1014308954846494831[270] = 0.0;
   out_1014308954846494831[271] = 0.0;
   out_1014308954846494831[272] = 0.0;
   out_1014308954846494831[273] = 0.0;
   out_1014308954846494831[274] = 0.0;
   out_1014308954846494831[275] = 0.0;
   out_1014308954846494831[276] = 0.0;
   out_1014308954846494831[277] = 0.0;
   out_1014308954846494831[278] = 0.0;
   out_1014308954846494831[279] = 0.0;
   out_1014308954846494831[280] = 0.0;
   out_1014308954846494831[281] = 0.0;
   out_1014308954846494831[282] = 0.0;
   out_1014308954846494831[283] = 0.0;
   out_1014308954846494831[284] = 0.0;
   out_1014308954846494831[285] = 1.0;
   out_1014308954846494831[286] = 0.0;
   out_1014308954846494831[287] = 0.0;
   out_1014308954846494831[288] = 0.0;
   out_1014308954846494831[289] = 0.0;
   out_1014308954846494831[290] = 0.0;
   out_1014308954846494831[291] = 0.0;
   out_1014308954846494831[292] = 0.0;
   out_1014308954846494831[293] = 0.0;
   out_1014308954846494831[294] = 0.0;
   out_1014308954846494831[295] = 0.0;
   out_1014308954846494831[296] = 0.0;
   out_1014308954846494831[297] = 0.0;
   out_1014308954846494831[298] = 0.0;
   out_1014308954846494831[299] = 0.0;
   out_1014308954846494831[300] = 0.0;
   out_1014308954846494831[301] = 0.0;
   out_1014308954846494831[302] = 0.0;
   out_1014308954846494831[303] = 0.0;
   out_1014308954846494831[304] = 1.0;
   out_1014308954846494831[305] = 0.0;
   out_1014308954846494831[306] = 0.0;
   out_1014308954846494831[307] = 0.0;
   out_1014308954846494831[308] = 0.0;
   out_1014308954846494831[309] = 0.0;
   out_1014308954846494831[310] = 0.0;
   out_1014308954846494831[311] = 0.0;
   out_1014308954846494831[312] = 0.0;
   out_1014308954846494831[313] = 0.0;
   out_1014308954846494831[314] = 0.0;
   out_1014308954846494831[315] = 0.0;
   out_1014308954846494831[316] = 0.0;
   out_1014308954846494831[317] = 0.0;
   out_1014308954846494831[318] = 0.0;
   out_1014308954846494831[319] = 0.0;
   out_1014308954846494831[320] = 0.0;
   out_1014308954846494831[321] = 0.0;
   out_1014308954846494831[322] = 0.0;
   out_1014308954846494831[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_6438442720881406331) {
   out_6438442720881406331[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_6438442720881406331[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_6438442720881406331[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_6438442720881406331[3] = dt*state[12] + state[3];
   out_6438442720881406331[4] = dt*state[13] + state[4];
   out_6438442720881406331[5] = dt*state[14] + state[5];
   out_6438442720881406331[6] = state[6];
   out_6438442720881406331[7] = state[7];
   out_6438442720881406331[8] = state[8];
   out_6438442720881406331[9] = state[9];
   out_6438442720881406331[10] = state[10];
   out_6438442720881406331[11] = state[11];
   out_6438442720881406331[12] = state[12];
   out_6438442720881406331[13] = state[13];
   out_6438442720881406331[14] = state[14];
   out_6438442720881406331[15] = state[15];
   out_6438442720881406331[16] = state[16];
   out_6438442720881406331[17] = state[17];
}
void F_fun(double *state, double dt, double *out_6531472760490035339) {
   out_6531472760490035339[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_6531472760490035339[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_6531472760490035339[2] = 0;
   out_6531472760490035339[3] = 0;
   out_6531472760490035339[4] = 0;
   out_6531472760490035339[5] = 0;
   out_6531472760490035339[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_6531472760490035339[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_6531472760490035339[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_6531472760490035339[9] = 0;
   out_6531472760490035339[10] = 0;
   out_6531472760490035339[11] = 0;
   out_6531472760490035339[12] = 0;
   out_6531472760490035339[13] = 0;
   out_6531472760490035339[14] = 0;
   out_6531472760490035339[15] = 0;
   out_6531472760490035339[16] = 0;
   out_6531472760490035339[17] = 0;
   out_6531472760490035339[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_6531472760490035339[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_6531472760490035339[20] = 0;
   out_6531472760490035339[21] = 0;
   out_6531472760490035339[22] = 0;
   out_6531472760490035339[23] = 0;
   out_6531472760490035339[24] = 0;
   out_6531472760490035339[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_6531472760490035339[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_6531472760490035339[27] = 0;
   out_6531472760490035339[28] = 0;
   out_6531472760490035339[29] = 0;
   out_6531472760490035339[30] = 0;
   out_6531472760490035339[31] = 0;
   out_6531472760490035339[32] = 0;
   out_6531472760490035339[33] = 0;
   out_6531472760490035339[34] = 0;
   out_6531472760490035339[35] = 0;
   out_6531472760490035339[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_6531472760490035339[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_6531472760490035339[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_6531472760490035339[39] = 0;
   out_6531472760490035339[40] = 0;
   out_6531472760490035339[41] = 0;
   out_6531472760490035339[42] = 0;
   out_6531472760490035339[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_6531472760490035339[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_6531472760490035339[45] = 0;
   out_6531472760490035339[46] = 0;
   out_6531472760490035339[47] = 0;
   out_6531472760490035339[48] = 0;
   out_6531472760490035339[49] = 0;
   out_6531472760490035339[50] = 0;
   out_6531472760490035339[51] = 0;
   out_6531472760490035339[52] = 0;
   out_6531472760490035339[53] = 0;
   out_6531472760490035339[54] = 0;
   out_6531472760490035339[55] = 0;
   out_6531472760490035339[56] = 0;
   out_6531472760490035339[57] = 1;
   out_6531472760490035339[58] = 0;
   out_6531472760490035339[59] = 0;
   out_6531472760490035339[60] = 0;
   out_6531472760490035339[61] = 0;
   out_6531472760490035339[62] = 0;
   out_6531472760490035339[63] = 0;
   out_6531472760490035339[64] = 0;
   out_6531472760490035339[65] = 0;
   out_6531472760490035339[66] = dt;
   out_6531472760490035339[67] = 0;
   out_6531472760490035339[68] = 0;
   out_6531472760490035339[69] = 0;
   out_6531472760490035339[70] = 0;
   out_6531472760490035339[71] = 0;
   out_6531472760490035339[72] = 0;
   out_6531472760490035339[73] = 0;
   out_6531472760490035339[74] = 0;
   out_6531472760490035339[75] = 0;
   out_6531472760490035339[76] = 1;
   out_6531472760490035339[77] = 0;
   out_6531472760490035339[78] = 0;
   out_6531472760490035339[79] = 0;
   out_6531472760490035339[80] = 0;
   out_6531472760490035339[81] = 0;
   out_6531472760490035339[82] = 0;
   out_6531472760490035339[83] = 0;
   out_6531472760490035339[84] = 0;
   out_6531472760490035339[85] = dt;
   out_6531472760490035339[86] = 0;
   out_6531472760490035339[87] = 0;
   out_6531472760490035339[88] = 0;
   out_6531472760490035339[89] = 0;
   out_6531472760490035339[90] = 0;
   out_6531472760490035339[91] = 0;
   out_6531472760490035339[92] = 0;
   out_6531472760490035339[93] = 0;
   out_6531472760490035339[94] = 0;
   out_6531472760490035339[95] = 1;
   out_6531472760490035339[96] = 0;
   out_6531472760490035339[97] = 0;
   out_6531472760490035339[98] = 0;
   out_6531472760490035339[99] = 0;
   out_6531472760490035339[100] = 0;
   out_6531472760490035339[101] = 0;
   out_6531472760490035339[102] = 0;
   out_6531472760490035339[103] = 0;
   out_6531472760490035339[104] = dt;
   out_6531472760490035339[105] = 0;
   out_6531472760490035339[106] = 0;
   out_6531472760490035339[107] = 0;
   out_6531472760490035339[108] = 0;
   out_6531472760490035339[109] = 0;
   out_6531472760490035339[110] = 0;
   out_6531472760490035339[111] = 0;
   out_6531472760490035339[112] = 0;
   out_6531472760490035339[113] = 0;
   out_6531472760490035339[114] = 1;
   out_6531472760490035339[115] = 0;
   out_6531472760490035339[116] = 0;
   out_6531472760490035339[117] = 0;
   out_6531472760490035339[118] = 0;
   out_6531472760490035339[119] = 0;
   out_6531472760490035339[120] = 0;
   out_6531472760490035339[121] = 0;
   out_6531472760490035339[122] = 0;
   out_6531472760490035339[123] = 0;
   out_6531472760490035339[124] = 0;
   out_6531472760490035339[125] = 0;
   out_6531472760490035339[126] = 0;
   out_6531472760490035339[127] = 0;
   out_6531472760490035339[128] = 0;
   out_6531472760490035339[129] = 0;
   out_6531472760490035339[130] = 0;
   out_6531472760490035339[131] = 0;
   out_6531472760490035339[132] = 0;
   out_6531472760490035339[133] = 1;
   out_6531472760490035339[134] = 0;
   out_6531472760490035339[135] = 0;
   out_6531472760490035339[136] = 0;
   out_6531472760490035339[137] = 0;
   out_6531472760490035339[138] = 0;
   out_6531472760490035339[139] = 0;
   out_6531472760490035339[140] = 0;
   out_6531472760490035339[141] = 0;
   out_6531472760490035339[142] = 0;
   out_6531472760490035339[143] = 0;
   out_6531472760490035339[144] = 0;
   out_6531472760490035339[145] = 0;
   out_6531472760490035339[146] = 0;
   out_6531472760490035339[147] = 0;
   out_6531472760490035339[148] = 0;
   out_6531472760490035339[149] = 0;
   out_6531472760490035339[150] = 0;
   out_6531472760490035339[151] = 0;
   out_6531472760490035339[152] = 1;
   out_6531472760490035339[153] = 0;
   out_6531472760490035339[154] = 0;
   out_6531472760490035339[155] = 0;
   out_6531472760490035339[156] = 0;
   out_6531472760490035339[157] = 0;
   out_6531472760490035339[158] = 0;
   out_6531472760490035339[159] = 0;
   out_6531472760490035339[160] = 0;
   out_6531472760490035339[161] = 0;
   out_6531472760490035339[162] = 0;
   out_6531472760490035339[163] = 0;
   out_6531472760490035339[164] = 0;
   out_6531472760490035339[165] = 0;
   out_6531472760490035339[166] = 0;
   out_6531472760490035339[167] = 0;
   out_6531472760490035339[168] = 0;
   out_6531472760490035339[169] = 0;
   out_6531472760490035339[170] = 0;
   out_6531472760490035339[171] = 1;
   out_6531472760490035339[172] = 0;
   out_6531472760490035339[173] = 0;
   out_6531472760490035339[174] = 0;
   out_6531472760490035339[175] = 0;
   out_6531472760490035339[176] = 0;
   out_6531472760490035339[177] = 0;
   out_6531472760490035339[178] = 0;
   out_6531472760490035339[179] = 0;
   out_6531472760490035339[180] = 0;
   out_6531472760490035339[181] = 0;
   out_6531472760490035339[182] = 0;
   out_6531472760490035339[183] = 0;
   out_6531472760490035339[184] = 0;
   out_6531472760490035339[185] = 0;
   out_6531472760490035339[186] = 0;
   out_6531472760490035339[187] = 0;
   out_6531472760490035339[188] = 0;
   out_6531472760490035339[189] = 0;
   out_6531472760490035339[190] = 1;
   out_6531472760490035339[191] = 0;
   out_6531472760490035339[192] = 0;
   out_6531472760490035339[193] = 0;
   out_6531472760490035339[194] = 0;
   out_6531472760490035339[195] = 0;
   out_6531472760490035339[196] = 0;
   out_6531472760490035339[197] = 0;
   out_6531472760490035339[198] = 0;
   out_6531472760490035339[199] = 0;
   out_6531472760490035339[200] = 0;
   out_6531472760490035339[201] = 0;
   out_6531472760490035339[202] = 0;
   out_6531472760490035339[203] = 0;
   out_6531472760490035339[204] = 0;
   out_6531472760490035339[205] = 0;
   out_6531472760490035339[206] = 0;
   out_6531472760490035339[207] = 0;
   out_6531472760490035339[208] = 0;
   out_6531472760490035339[209] = 1;
   out_6531472760490035339[210] = 0;
   out_6531472760490035339[211] = 0;
   out_6531472760490035339[212] = 0;
   out_6531472760490035339[213] = 0;
   out_6531472760490035339[214] = 0;
   out_6531472760490035339[215] = 0;
   out_6531472760490035339[216] = 0;
   out_6531472760490035339[217] = 0;
   out_6531472760490035339[218] = 0;
   out_6531472760490035339[219] = 0;
   out_6531472760490035339[220] = 0;
   out_6531472760490035339[221] = 0;
   out_6531472760490035339[222] = 0;
   out_6531472760490035339[223] = 0;
   out_6531472760490035339[224] = 0;
   out_6531472760490035339[225] = 0;
   out_6531472760490035339[226] = 0;
   out_6531472760490035339[227] = 0;
   out_6531472760490035339[228] = 1;
   out_6531472760490035339[229] = 0;
   out_6531472760490035339[230] = 0;
   out_6531472760490035339[231] = 0;
   out_6531472760490035339[232] = 0;
   out_6531472760490035339[233] = 0;
   out_6531472760490035339[234] = 0;
   out_6531472760490035339[235] = 0;
   out_6531472760490035339[236] = 0;
   out_6531472760490035339[237] = 0;
   out_6531472760490035339[238] = 0;
   out_6531472760490035339[239] = 0;
   out_6531472760490035339[240] = 0;
   out_6531472760490035339[241] = 0;
   out_6531472760490035339[242] = 0;
   out_6531472760490035339[243] = 0;
   out_6531472760490035339[244] = 0;
   out_6531472760490035339[245] = 0;
   out_6531472760490035339[246] = 0;
   out_6531472760490035339[247] = 1;
   out_6531472760490035339[248] = 0;
   out_6531472760490035339[249] = 0;
   out_6531472760490035339[250] = 0;
   out_6531472760490035339[251] = 0;
   out_6531472760490035339[252] = 0;
   out_6531472760490035339[253] = 0;
   out_6531472760490035339[254] = 0;
   out_6531472760490035339[255] = 0;
   out_6531472760490035339[256] = 0;
   out_6531472760490035339[257] = 0;
   out_6531472760490035339[258] = 0;
   out_6531472760490035339[259] = 0;
   out_6531472760490035339[260] = 0;
   out_6531472760490035339[261] = 0;
   out_6531472760490035339[262] = 0;
   out_6531472760490035339[263] = 0;
   out_6531472760490035339[264] = 0;
   out_6531472760490035339[265] = 0;
   out_6531472760490035339[266] = 1;
   out_6531472760490035339[267] = 0;
   out_6531472760490035339[268] = 0;
   out_6531472760490035339[269] = 0;
   out_6531472760490035339[270] = 0;
   out_6531472760490035339[271] = 0;
   out_6531472760490035339[272] = 0;
   out_6531472760490035339[273] = 0;
   out_6531472760490035339[274] = 0;
   out_6531472760490035339[275] = 0;
   out_6531472760490035339[276] = 0;
   out_6531472760490035339[277] = 0;
   out_6531472760490035339[278] = 0;
   out_6531472760490035339[279] = 0;
   out_6531472760490035339[280] = 0;
   out_6531472760490035339[281] = 0;
   out_6531472760490035339[282] = 0;
   out_6531472760490035339[283] = 0;
   out_6531472760490035339[284] = 0;
   out_6531472760490035339[285] = 1;
   out_6531472760490035339[286] = 0;
   out_6531472760490035339[287] = 0;
   out_6531472760490035339[288] = 0;
   out_6531472760490035339[289] = 0;
   out_6531472760490035339[290] = 0;
   out_6531472760490035339[291] = 0;
   out_6531472760490035339[292] = 0;
   out_6531472760490035339[293] = 0;
   out_6531472760490035339[294] = 0;
   out_6531472760490035339[295] = 0;
   out_6531472760490035339[296] = 0;
   out_6531472760490035339[297] = 0;
   out_6531472760490035339[298] = 0;
   out_6531472760490035339[299] = 0;
   out_6531472760490035339[300] = 0;
   out_6531472760490035339[301] = 0;
   out_6531472760490035339[302] = 0;
   out_6531472760490035339[303] = 0;
   out_6531472760490035339[304] = 1;
   out_6531472760490035339[305] = 0;
   out_6531472760490035339[306] = 0;
   out_6531472760490035339[307] = 0;
   out_6531472760490035339[308] = 0;
   out_6531472760490035339[309] = 0;
   out_6531472760490035339[310] = 0;
   out_6531472760490035339[311] = 0;
   out_6531472760490035339[312] = 0;
   out_6531472760490035339[313] = 0;
   out_6531472760490035339[314] = 0;
   out_6531472760490035339[315] = 0;
   out_6531472760490035339[316] = 0;
   out_6531472760490035339[317] = 0;
   out_6531472760490035339[318] = 0;
   out_6531472760490035339[319] = 0;
   out_6531472760490035339[320] = 0;
   out_6531472760490035339[321] = 0;
   out_6531472760490035339[322] = 0;
   out_6531472760490035339[323] = 1;
}
void h_4(double *state, double *unused, double *out_2496877672334565060) {
   out_2496877672334565060[0] = state[6] + state[9];
   out_2496877672334565060[1] = state[7] + state[10];
   out_2496877672334565060[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_7942831634537215637) {
   out_7942831634537215637[0] = 0;
   out_7942831634537215637[1] = 0;
   out_7942831634537215637[2] = 0;
   out_7942831634537215637[3] = 0;
   out_7942831634537215637[4] = 0;
   out_7942831634537215637[5] = 0;
   out_7942831634537215637[6] = 1;
   out_7942831634537215637[7] = 0;
   out_7942831634537215637[8] = 0;
   out_7942831634537215637[9] = 1;
   out_7942831634537215637[10] = 0;
   out_7942831634537215637[11] = 0;
   out_7942831634537215637[12] = 0;
   out_7942831634537215637[13] = 0;
   out_7942831634537215637[14] = 0;
   out_7942831634537215637[15] = 0;
   out_7942831634537215637[16] = 0;
   out_7942831634537215637[17] = 0;
   out_7942831634537215637[18] = 0;
   out_7942831634537215637[19] = 0;
   out_7942831634537215637[20] = 0;
   out_7942831634537215637[21] = 0;
   out_7942831634537215637[22] = 0;
   out_7942831634537215637[23] = 0;
   out_7942831634537215637[24] = 0;
   out_7942831634537215637[25] = 1;
   out_7942831634537215637[26] = 0;
   out_7942831634537215637[27] = 0;
   out_7942831634537215637[28] = 1;
   out_7942831634537215637[29] = 0;
   out_7942831634537215637[30] = 0;
   out_7942831634537215637[31] = 0;
   out_7942831634537215637[32] = 0;
   out_7942831634537215637[33] = 0;
   out_7942831634537215637[34] = 0;
   out_7942831634537215637[35] = 0;
   out_7942831634537215637[36] = 0;
   out_7942831634537215637[37] = 0;
   out_7942831634537215637[38] = 0;
   out_7942831634537215637[39] = 0;
   out_7942831634537215637[40] = 0;
   out_7942831634537215637[41] = 0;
   out_7942831634537215637[42] = 0;
   out_7942831634537215637[43] = 0;
   out_7942831634537215637[44] = 1;
   out_7942831634537215637[45] = 0;
   out_7942831634537215637[46] = 0;
   out_7942831634537215637[47] = 1;
   out_7942831634537215637[48] = 0;
   out_7942831634537215637[49] = 0;
   out_7942831634537215637[50] = 0;
   out_7942831634537215637[51] = 0;
   out_7942831634537215637[52] = 0;
   out_7942831634537215637[53] = 0;
}
void h_10(double *state, double *unused, double *out_6821224095196569661) {
   out_6821224095196569661[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_6821224095196569661[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_6821224095196569661[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_2541800970645913241) {
   out_2541800970645913241[0] = 0;
   out_2541800970645913241[1] = 9.8100000000000005*cos(state[1]);
   out_2541800970645913241[2] = 0;
   out_2541800970645913241[3] = 0;
   out_2541800970645913241[4] = -state[8];
   out_2541800970645913241[5] = state[7];
   out_2541800970645913241[6] = 0;
   out_2541800970645913241[7] = state[5];
   out_2541800970645913241[8] = -state[4];
   out_2541800970645913241[9] = 0;
   out_2541800970645913241[10] = 0;
   out_2541800970645913241[11] = 0;
   out_2541800970645913241[12] = 1;
   out_2541800970645913241[13] = 0;
   out_2541800970645913241[14] = 0;
   out_2541800970645913241[15] = 1;
   out_2541800970645913241[16] = 0;
   out_2541800970645913241[17] = 0;
   out_2541800970645913241[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_2541800970645913241[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_2541800970645913241[20] = 0;
   out_2541800970645913241[21] = state[8];
   out_2541800970645913241[22] = 0;
   out_2541800970645913241[23] = -state[6];
   out_2541800970645913241[24] = -state[5];
   out_2541800970645913241[25] = 0;
   out_2541800970645913241[26] = state[3];
   out_2541800970645913241[27] = 0;
   out_2541800970645913241[28] = 0;
   out_2541800970645913241[29] = 0;
   out_2541800970645913241[30] = 0;
   out_2541800970645913241[31] = 1;
   out_2541800970645913241[32] = 0;
   out_2541800970645913241[33] = 0;
   out_2541800970645913241[34] = 1;
   out_2541800970645913241[35] = 0;
   out_2541800970645913241[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_2541800970645913241[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_2541800970645913241[38] = 0;
   out_2541800970645913241[39] = -state[7];
   out_2541800970645913241[40] = state[6];
   out_2541800970645913241[41] = 0;
   out_2541800970645913241[42] = state[4];
   out_2541800970645913241[43] = -state[3];
   out_2541800970645913241[44] = 0;
   out_2541800970645913241[45] = 0;
   out_2541800970645913241[46] = 0;
   out_2541800970645913241[47] = 0;
   out_2541800970645913241[48] = 0;
   out_2541800970645913241[49] = 0;
   out_2541800970645913241[50] = 1;
   out_2541800970645913241[51] = 0;
   out_2541800970645913241[52] = 0;
   out_2541800970645913241[53] = 1;
}
void h_13(double *state, double *unused, double *out_8366060029539452607) {
   out_8366060029539452607[0] = state[3];
   out_8366060029539452607[1] = state[4];
   out_8366060029539452607[2] = state[5];
}
void H_13(double *state, double *unused, double *out_7291638613840003178) {
   out_7291638613840003178[0] = 0;
   out_7291638613840003178[1] = 0;
   out_7291638613840003178[2] = 0;
   out_7291638613840003178[3] = 1;
   out_7291638613840003178[4] = 0;
   out_7291638613840003178[5] = 0;
   out_7291638613840003178[6] = 0;
   out_7291638613840003178[7] = 0;
   out_7291638613840003178[8] = 0;
   out_7291638613840003178[9] = 0;
   out_7291638613840003178[10] = 0;
   out_7291638613840003178[11] = 0;
   out_7291638613840003178[12] = 0;
   out_7291638613840003178[13] = 0;
   out_7291638613840003178[14] = 0;
   out_7291638613840003178[15] = 0;
   out_7291638613840003178[16] = 0;
   out_7291638613840003178[17] = 0;
   out_7291638613840003178[18] = 0;
   out_7291638613840003178[19] = 0;
   out_7291638613840003178[20] = 0;
   out_7291638613840003178[21] = 0;
   out_7291638613840003178[22] = 1;
   out_7291638613840003178[23] = 0;
   out_7291638613840003178[24] = 0;
   out_7291638613840003178[25] = 0;
   out_7291638613840003178[26] = 0;
   out_7291638613840003178[27] = 0;
   out_7291638613840003178[28] = 0;
   out_7291638613840003178[29] = 0;
   out_7291638613840003178[30] = 0;
   out_7291638613840003178[31] = 0;
   out_7291638613840003178[32] = 0;
   out_7291638613840003178[33] = 0;
   out_7291638613840003178[34] = 0;
   out_7291638613840003178[35] = 0;
   out_7291638613840003178[36] = 0;
   out_7291638613840003178[37] = 0;
   out_7291638613840003178[38] = 0;
   out_7291638613840003178[39] = 0;
   out_7291638613840003178[40] = 0;
   out_7291638613840003178[41] = 1;
   out_7291638613840003178[42] = 0;
   out_7291638613840003178[43] = 0;
   out_7291638613840003178[44] = 0;
   out_7291638613840003178[45] = 0;
   out_7291638613840003178[46] = 0;
   out_7291638613840003178[47] = 0;
   out_7291638613840003178[48] = 0;
   out_7291638613840003178[49] = 0;
   out_7291638613840003178[50] = 0;
   out_7291638613840003178[51] = 0;
   out_7291638613840003178[52] = 0;
   out_7291638613840003178[53] = 0;
}
void h_14(double *state, double *unused, double *out_1084678045620217578) {
   out_1084678045620217578[0] = state[6];
   out_1084678045620217578[1] = state[7];
   out_1084678045620217578[2] = state[8];
}
void H_14(double *state, double *unused, double *out_461685819257475213) {
   out_461685819257475213[0] = 0;
   out_461685819257475213[1] = 0;
   out_461685819257475213[2] = 0;
   out_461685819257475213[3] = 0;
   out_461685819257475213[4] = 0;
   out_461685819257475213[5] = 0;
   out_461685819257475213[6] = 1;
   out_461685819257475213[7] = 0;
   out_461685819257475213[8] = 0;
   out_461685819257475213[9] = 0;
   out_461685819257475213[10] = 0;
   out_461685819257475213[11] = 0;
   out_461685819257475213[12] = 0;
   out_461685819257475213[13] = 0;
   out_461685819257475213[14] = 0;
   out_461685819257475213[15] = 0;
   out_461685819257475213[16] = 0;
   out_461685819257475213[17] = 0;
   out_461685819257475213[18] = 0;
   out_461685819257475213[19] = 0;
   out_461685819257475213[20] = 0;
   out_461685819257475213[21] = 0;
   out_461685819257475213[22] = 0;
   out_461685819257475213[23] = 0;
   out_461685819257475213[24] = 0;
   out_461685819257475213[25] = 1;
   out_461685819257475213[26] = 0;
   out_461685819257475213[27] = 0;
   out_461685819257475213[28] = 0;
   out_461685819257475213[29] = 0;
   out_461685819257475213[30] = 0;
   out_461685819257475213[31] = 0;
   out_461685819257475213[32] = 0;
   out_461685819257475213[33] = 0;
   out_461685819257475213[34] = 0;
   out_461685819257475213[35] = 0;
   out_461685819257475213[36] = 0;
   out_461685819257475213[37] = 0;
   out_461685819257475213[38] = 0;
   out_461685819257475213[39] = 0;
   out_461685819257475213[40] = 0;
   out_461685819257475213[41] = 0;
   out_461685819257475213[42] = 0;
   out_461685819257475213[43] = 0;
   out_461685819257475213[44] = 1;
   out_461685819257475213[45] = 0;
   out_461685819257475213[46] = 0;
   out_461685819257475213[47] = 0;
   out_461685819257475213[48] = 0;
   out_461685819257475213[49] = 0;
   out_461685819257475213[50] = 0;
   out_461685819257475213[51] = 0;
   out_461685819257475213[52] = 0;
   out_461685819257475213[53] = 0;
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
void pose_err_fun(double *nom_x, double *delta_x, double *out_3059021723261949722) {
  err_fun(nom_x, delta_x, out_3059021723261949722);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_6771718338208051804) {
  inv_err_fun(nom_x, true_x, out_6771718338208051804);
}
void pose_H_mod_fun(double *state, double *out_1014308954846494831) {
  H_mod_fun(state, out_1014308954846494831);
}
void pose_f_fun(double *state, double dt, double *out_6438442720881406331) {
  f_fun(state,  dt, out_6438442720881406331);
}
void pose_F_fun(double *state, double dt, double *out_6531472760490035339) {
  F_fun(state,  dt, out_6531472760490035339);
}
void pose_h_4(double *state, double *unused, double *out_2496877672334565060) {
  h_4(state, unused, out_2496877672334565060);
}
void pose_H_4(double *state, double *unused, double *out_7942831634537215637) {
  H_4(state, unused, out_7942831634537215637);
}
void pose_h_10(double *state, double *unused, double *out_6821224095196569661) {
  h_10(state, unused, out_6821224095196569661);
}
void pose_H_10(double *state, double *unused, double *out_2541800970645913241) {
  H_10(state, unused, out_2541800970645913241);
}
void pose_h_13(double *state, double *unused, double *out_8366060029539452607) {
  h_13(state, unused, out_8366060029539452607);
}
void pose_H_13(double *state, double *unused, double *out_7291638613840003178) {
  H_13(state, unused, out_7291638613840003178);
}
void pose_h_14(double *state, double *unused, double *out_1084678045620217578) {
  h_14(state, unused, out_1084678045620217578);
}
void pose_H_14(double *state, double *unused, double *out_461685819257475213) {
  H_14(state, unused, out_461685819257475213);
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
