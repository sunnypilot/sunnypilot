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
void err_fun(double *nom_x, double *delta_x, double *out_7899872685628621531) {
   out_7899872685628621531[0] = delta_x[0] + nom_x[0];
   out_7899872685628621531[1] = delta_x[1] + nom_x[1];
   out_7899872685628621531[2] = delta_x[2] + nom_x[2];
   out_7899872685628621531[3] = delta_x[3] + nom_x[3];
   out_7899872685628621531[4] = delta_x[4] + nom_x[4];
   out_7899872685628621531[5] = delta_x[5] + nom_x[5];
   out_7899872685628621531[6] = delta_x[6] + nom_x[6];
   out_7899872685628621531[7] = delta_x[7] + nom_x[7];
   out_7899872685628621531[8] = delta_x[8] + nom_x[8];
   out_7899872685628621531[9] = delta_x[9] + nom_x[9];
   out_7899872685628621531[10] = delta_x[10] + nom_x[10];
   out_7899872685628621531[11] = delta_x[11] + nom_x[11];
   out_7899872685628621531[12] = delta_x[12] + nom_x[12];
   out_7899872685628621531[13] = delta_x[13] + nom_x[13];
   out_7899872685628621531[14] = delta_x[14] + nom_x[14];
   out_7899872685628621531[15] = delta_x[15] + nom_x[15];
   out_7899872685628621531[16] = delta_x[16] + nom_x[16];
   out_7899872685628621531[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_1215289726053279423) {
   out_1215289726053279423[0] = -nom_x[0] + true_x[0];
   out_1215289726053279423[1] = -nom_x[1] + true_x[1];
   out_1215289726053279423[2] = -nom_x[2] + true_x[2];
   out_1215289726053279423[3] = -nom_x[3] + true_x[3];
   out_1215289726053279423[4] = -nom_x[4] + true_x[4];
   out_1215289726053279423[5] = -nom_x[5] + true_x[5];
   out_1215289726053279423[6] = -nom_x[6] + true_x[6];
   out_1215289726053279423[7] = -nom_x[7] + true_x[7];
   out_1215289726053279423[8] = -nom_x[8] + true_x[8];
   out_1215289726053279423[9] = -nom_x[9] + true_x[9];
   out_1215289726053279423[10] = -nom_x[10] + true_x[10];
   out_1215289726053279423[11] = -nom_x[11] + true_x[11];
   out_1215289726053279423[12] = -nom_x[12] + true_x[12];
   out_1215289726053279423[13] = -nom_x[13] + true_x[13];
   out_1215289726053279423[14] = -nom_x[14] + true_x[14];
   out_1215289726053279423[15] = -nom_x[15] + true_x[15];
   out_1215289726053279423[16] = -nom_x[16] + true_x[16];
   out_1215289726053279423[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_420741753375595218) {
   out_420741753375595218[0] = 1.0;
   out_420741753375595218[1] = 0.0;
   out_420741753375595218[2] = 0.0;
   out_420741753375595218[3] = 0.0;
   out_420741753375595218[4] = 0.0;
   out_420741753375595218[5] = 0.0;
   out_420741753375595218[6] = 0.0;
   out_420741753375595218[7] = 0.0;
   out_420741753375595218[8] = 0.0;
   out_420741753375595218[9] = 0.0;
   out_420741753375595218[10] = 0.0;
   out_420741753375595218[11] = 0.0;
   out_420741753375595218[12] = 0.0;
   out_420741753375595218[13] = 0.0;
   out_420741753375595218[14] = 0.0;
   out_420741753375595218[15] = 0.0;
   out_420741753375595218[16] = 0.0;
   out_420741753375595218[17] = 0.0;
   out_420741753375595218[18] = 0.0;
   out_420741753375595218[19] = 1.0;
   out_420741753375595218[20] = 0.0;
   out_420741753375595218[21] = 0.0;
   out_420741753375595218[22] = 0.0;
   out_420741753375595218[23] = 0.0;
   out_420741753375595218[24] = 0.0;
   out_420741753375595218[25] = 0.0;
   out_420741753375595218[26] = 0.0;
   out_420741753375595218[27] = 0.0;
   out_420741753375595218[28] = 0.0;
   out_420741753375595218[29] = 0.0;
   out_420741753375595218[30] = 0.0;
   out_420741753375595218[31] = 0.0;
   out_420741753375595218[32] = 0.0;
   out_420741753375595218[33] = 0.0;
   out_420741753375595218[34] = 0.0;
   out_420741753375595218[35] = 0.0;
   out_420741753375595218[36] = 0.0;
   out_420741753375595218[37] = 0.0;
   out_420741753375595218[38] = 1.0;
   out_420741753375595218[39] = 0.0;
   out_420741753375595218[40] = 0.0;
   out_420741753375595218[41] = 0.0;
   out_420741753375595218[42] = 0.0;
   out_420741753375595218[43] = 0.0;
   out_420741753375595218[44] = 0.0;
   out_420741753375595218[45] = 0.0;
   out_420741753375595218[46] = 0.0;
   out_420741753375595218[47] = 0.0;
   out_420741753375595218[48] = 0.0;
   out_420741753375595218[49] = 0.0;
   out_420741753375595218[50] = 0.0;
   out_420741753375595218[51] = 0.0;
   out_420741753375595218[52] = 0.0;
   out_420741753375595218[53] = 0.0;
   out_420741753375595218[54] = 0.0;
   out_420741753375595218[55] = 0.0;
   out_420741753375595218[56] = 0.0;
   out_420741753375595218[57] = 1.0;
   out_420741753375595218[58] = 0.0;
   out_420741753375595218[59] = 0.0;
   out_420741753375595218[60] = 0.0;
   out_420741753375595218[61] = 0.0;
   out_420741753375595218[62] = 0.0;
   out_420741753375595218[63] = 0.0;
   out_420741753375595218[64] = 0.0;
   out_420741753375595218[65] = 0.0;
   out_420741753375595218[66] = 0.0;
   out_420741753375595218[67] = 0.0;
   out_420741753375595218[68] = 0.0;
   out_420741753375595218[69] = 0.0;
   out_420741753375595218[70] = 0.0;
   out_420741753375595218[71] = 0.0;
   out_420741753375595218[72] = 0.0;
   out_420741753375595218[73] = 0.0;
   out_420741753375595218[74] = 0.0;
   out_420741753375595218[75] = 0.0;
   out_420741753375595218[76] = 1.0;
   out_420741753375595218[77] = 0.0;
   out_420741753375595218[78] = 0.0;
   out_420741753375595218[79] = 0.0;
   out_420741753375595218[80] = 0.0;
   out_420741753375595218[81] = 0.0;
   out_420741753375595218[82] = 0.0;
   out_420741753375595218[83] = 0.0;
   out_420741753375595218[84] = 0.0;
   out_420741753375595218[85] = 0.0;
   out_420741753375595218[86] = 0.0;
   out_420741753375595218[87] = 0.0;
   out_420741753375595218[88] = 0.0;
   out_420741753375595218[89] = 0.0;
   out_420741753375595218[90] = 0.0;
   out_420741753375595218[91] = 0.0;
   out_420741753375595218[92] = 0.0;
   out_420741753375595218[93] = 0.0;
   out_420741753375595218[94] = 0.0;
   out_420741753375595218[95] = 1.0;
   out_420741753375595218[96] = 0.0;
   out_420741753375595218[97] = 0.0;
   out_420741753375595218[98] = 0.0;
   out_420741753375595218[99] = 0.0;
   out_420741753375595218[100] = 0.0;
   out_420741753375595218[101] = 0.0;
   out_420741753375595218[102] = 0.0;
   out_420741753375595218[103] = 0.0;
   out_420741753375595218[104] = 0.0;
   out_420741753375595218[105] = 0.0;
   out_420741753375595218[106] = 0.0;
   out_420741753375595218[107] = 0.0;
   out_420741753375595218[108] = 0.0;
   out_420741753375595218[109] = 0.0;
   out_420741753375595218[110] = 0.0;
   out_420741753375595218[111] = 0.0;
   out_420741753375595218[112] = 0.0;
   out_420741753375595218[113] = 0.0;
   out_420741753375595218[114] = 1.0;
   out_420741753375595218[115] = 0.0;
   out_420741753375595218[116] = 0.0;
   out_420741753375595218[117] = 0.0;
   out_420741753375595218[118] = 0.0;
   out_420741753375595218[119] = 0.0;
   out_420741753375595218[120] = 0.0;
   out_420741753375595218[121] = 0.0;
   out_420741753375595218[122] = 0.0;
   out_420741753375595218[123] = 0.0;
   out_420741753375595218[124] = 0.0;
   out_420741753375595218[125] = 0.0;
   out_420741753375595218[126] = 0.0;
   out_420741753375595218[127] = 0.0;
   out_420741753375595218[128] = 0.0;
   out_420741753375595218[129] = 0.0;
   out_420741753375595218[130] = 0.0;
   out_420741753375595218[131] = 0.0;
   out_420741753375595218[132] = 0.0;
   out_420741753375595218[133] = 1.0;
   out_420741753375595218[134] = 0.0;
   out_420741753375595218[135] = 0.0;
   out_420741753375595218[136] = 0.0;
   out_420741753375595218[137] = 0.0;
   out_420741753375595218[138] = 0.0;
   out_420741753375595218[139] = 0.0;
   out_420741753375595218[140] = 0.0;
   out_420741753375595218[141] = 0.0;
   out_420741753375595218[142] = 0.0;
   out_420741753375595218[143] = 0.0;
   out_420741753375595218[144] = 0.0;
   out_420741753375595218[145] = 0.0;
   out_420741753375595218[146] = 0.0;
   out_420741753375595218[147] = 0.0;
   out_420741753375595218[148] = 0.0;
   out_420741753375595218[149] = 0.0;
   out_420741753375595218[150] = 0.0;
   out_420741753375595218[151] = 0.0;
   out_420741753375595218[152] = 1.0;
   out_420741753375595218[153] = 0.0;
   out_420741753375595218[154] = 0.0;
   out_420741753375595218[155] = 0.0;
   out_420741753375595218[156] = 0.0;
   out_420741753375595218[157] = 0.0;
   out_420741753375595218[158] = 0.0;
   out_420741753375595218[159] = 0.0;
   out_420741753375595218[160] = 0.0;
   out_420741753375595218[161] = 0.0;
   out_420741753375595218[162] = 0.0;
   out_420741753375595218[163] = 0.0;
   out_420741753375595218[164] = 0.0;
   out_420741753375595218[165] = 0.0;
   out_420741753375595218[166] = 0.0;
   out_420741753375595218[167] = 0.0;
   out_420741753375595218[168] = 0.0;
   out_420741753375595218[169] = 0.0;
   out_420741753375595218[170] = 0.0;
   out_420741753375595218[171] = 1.0;
   out_420741753375595218[172] = 0.0;
   out_420741753375595218[173] = 0.0;
   out_420741753375595218[174] = 0.0;
   out_420741753375595218[175] = 0.0;
   out_420741753375595218[176] = 0.0;
   out_420741753375595218[177] = 0.0;
   out_420741753375595218[178] = 0.0;
   out_420741753375595218[179] = 0.0;
   out_420741753375595218[180] = 0.0;
   out_420741753375595218[181] = 0.0;
   out_420741753375595218[182] = 0.0;
   out_420741753375595218[183] = 0.0;
   out_420741753375595218[184] = 0.0;
   out_420741753375595218[185] = 0.0;
   out_420741753375595218[186] = 0.0;
   out_420741753375595218[187] = 0.0;
   out_420741753375595218[188] = 0.0;
   out_420741753375595218[189] = 0.0;
   out_420741753375595218[190] = 1.0;
   out_420741753375595218[191] = 0.0;
   out_420741753375595218[192] = 0.0;
   out_420741753375595218[193] = 0.0;
   out_420741753375595218[194] = 0.0;
   out_420741753375595218[195] = 0.0;
   out_420741753375595218[196] = 0.0;
   out_420741753375595218[197] = 0.0;
   out_420741753375595218[198] = 0.0;
   out_420741753375595218[199] = 0.0;
   out_420741753375595218[200] = 0.0;
   out_420741753375595218[201] = 0.0;
   out_420741753375595218[202] = 0.0;
   out_420741753375595218[203] = 0.0;
   out_420741753375595218[204] = 0.0;
   out_420741753375595218[205] = 0.0;
   out_420741753375595218[206] = 0.0;
   out_420741753375595218[207] = 0.0;
   out_420741753375595218[208] = 0.0;
   out_420741753375595218[209] = 1.0;
   out_420741753375595218[210] = 0.0;
   out_420741753375595218[211] = 0.0;
   out_420741753375595218[212] = 0.0;
   out_420741753375595218[213] = 0.0;
   out_420741753375595218[214] = 0.0;
   out_420741753375595218[215] = 0.0;
   out_420741753375595218[216] = 0.0;
   out_420741753375595218[217] = 0.0;
   out_420741753375595218[218] = 0.0;
   out_420741753375595218[219] = 0.0;
   out_420741753375595218[220] = 0.0;
   out_420741753375595218[221] = 0.0;
   out_420741753375595218[222] = 0.0;
   out_420741753375595218[223] = 0.0;
   out_420741753375595218[224] = 0.0;
   out_420741753375595218[225] = 0.0;
   out_420741753375595218[226] = 0.0;
   out_420741753375595218[227] = 0.0;
   out_420741753375595218[228] = 1.0;
   out_420741753375595218[229] = 0.0;
   out_420741753375595218[230] = 0.0;
   out_420741753375595218[231] = 0.0;
   out_420741753375595218[232] = 0.0;
   out_420741753375595218[233] = 0.0;
   out_420741753375595218[234] = 0.0;
   out_420741753375595218[235] = 0.0;
   out_420741753375595218[236] = 0.0;
   out_420741753375595218[237] = 0.0;
   out_420741753375595218[238] = 0.0;
   out_420741753375595218[239] = 0.0;
   out_420741753375595218[240] = 0.0;
   out_420741753375595218[241] = 0.0;
   out_420741753375595218[242] = 0.0;
   out_420741753375595218[243] = 0.0;
   out_420741753375595218[244] = 0.0;
   out_420741753375595218[245] = 0.0;
   out_420741753375595218[246] = 0.0;
   out_420741753375595218[247] = 1.0;
   out_420741753375595218[248] = 0.0;
   out_420741753375595218[249] = 0.0;
   out_420741753375595218[250] = 0.0;
   out_420741753375595218[251] = 0.0;
   out_420741753375595218[252] = 0.0;
   out_420741753375595218[253] = 0.0;
   out_420741753375595218[254] = 0.0;
   out_420741753375595218[255] = 0.0;
   out_420741753375595218[256] = 0.0;
   out_420741753375595218[257] = 0.0;
   out_420741753375595218[258] = 0.0;
   out_420741753375595218[259] = 0.0;
   out_420741753375595218[260] = 0.0;
   out_420741753375595218[261] = 0.0;
   out_420741753375595218[262] = 0.0;
   out_420741753375595218[263] = 0.0;
   out_420741753375595218[264] = 0.0;
   out_420741753375595218[265] = 0.0;
   out_420741753375595218[266] = 1.0;
   out_420741753375595218[267] = 0.0;
   out_420741753375595218[268] = 0.0;
   out_420741753375595218[269] = 0.0;
   out_420741753375595218[270] = 0.0;
   out_420741753375595218[271] = 0.0;
   out_420741753375595218[272] = 0.0;
   out_420741753375595218[273] = 0.0;
   out_420741753375595218[274] = 0.0;
   out_420741753375595218[275] = 0.0;
   out_420741753375595218[276] = 0.0;
   out_420741753375595218[277] = 0.0;
   out_420741753375595218[278] = 0.0;
   out_420741753375595218[279] = 0.0;
   out_420741753375595218[280] = 0.0;
   out_420741753375595218[281] = 0.0;
   out_420741753375595218[282] = 0.0;
   out_420741753375595218[283] = 0.0;
   out_420741753375595218[284] = 0.0;
   out_420741753375595218[285] = 1.0;
   out_420741753375595218[286] = 0.0;
   out_420741753375595218[287] = 0.0;
   out_420741753375595218[288] = 0.0;
   out_420741753375595218[289] = 0.0;
   out_420741753375595218[290] = 0.0;
   out_420741753375595218[291] = 0.0;
   out_420741753375595218[292] = 0.0;
   out_420741753375595218[293] = 0.0;
   out_420741753375595218[294] = 0.0;
   out_420741753375595218[295] = 0.0;
   out_420741753375595218[296] = 0.0;
   out_420741753375595218[297] = 0.0;
   out_420741753375595218[298] = 0.0;
   out_420741753375595218[299] = 0.0;
   out_420741753375595218[300] = 0.0;
   out_420741753375595218[301] = 0.0;
   out_420741753375595218[302] = 0.0;
   out_420741753375595218[303] = 0.0;
   out_420741753375595218[304] = 1.0;
   out_420741753375595218[305] = 0.0;
   out_420741753375595218[306] = 0.0;
   out_420741753375595218[307] = 0.0;
   out_420741753375595218[308] = 0.0;
   out_420741753375595218[309] = 0.0;
   out_420741753375595218[310] = 0.0;
   out_420741753375595218[311] = 0.0;
   out_420741753375595218[312] = 0.0;
   out_420741753375595218[313] = 0.0;
   out_420741753375595218[314] = 0.0;
   out_420741753375595218[315] = 0.0;
   out_420741753375595218[316] = 0.0;
   out_420741753375595218[317] = 0.0;
   out_420741753375595218[318] = 0.0;
   out_420741753375595218[319] = 0.0;
   out_420741753375595218[320] = 0.0;
   out_420741753375595218[321] = 0.0;
   out_420741753375595218[322] = 0.0;
   out_420741753375595218[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_5996963235034927992) {
   out_5996963235034927992[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_5996963235034927992[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_5996963235034927992[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_5996963235034927992[3] = dt*state[12] + state[3];
   out_5996963235034927992[4] = dt*state[13] + state[4];
   out_5996963235034927992[5] = dt*state[14] + state[5];
   out_5996963235034927992[6] = state[6];
   out_5996963235034927992[7] = state[7];
   out_5996963235034927992[8] = state[8];
   out_5996963235034927992[9] = state[9];
   out_5996963235034927992[10] = state[10];
   out_5996963235034927992[11] = state[11];
   out_5996963235034927992[12] = state[12];
   out_5996963235034927992[13] = state[13];
   out_5996963235034927992[14] = state[14];
   out_5996963235034927992[15] = state[15];
   out_5996963235034927992[16] = state[16];
   out_5996963235034927992[17] = state[17];
}
void F_fun(double *state, double dt, double *out_78320000076568703) {
   out_78320000076568703[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_78320000076568703[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_78320000076568703[2] = 0;
   out_78320000076568703[3] = 0;
   out_78320000076568703[4] = 0;
   out_78320000076568703[5] = 0;
   out_78320000076568703[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_78320000076568703[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_78320000076568703[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_78320000076568703[9] = 0;
   out_78320000076568703[10] = 0;
   out_78320000076568703[11] = 0;
   out_78320000076568703[12] = 0;
   out_78320000076568703[13] = 0;
   out_78320000076568703[14] = 0;
   out_78320000076568703[15] = 0;
   out_78320000076568703[16] = 0;
   out_78320000076568703[17] = 0;
   out_78320000076568703[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_78320000076568703[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_78320000076568703[20] = 0;
   out_78320000076568703[21] = 0;
   out_78320000076568703[22] = 0;
   out_78320000076568703[23] = 0;
   out_78320000076568703[24] = 0;
   out_78320000076568703[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_78320000076568703[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_78320000076568703[27] = 0;
   out_78320000076568703[28] = 0;
   out_78320000076568703[29] = 0;
   out_78320000076568703[30] = 0;
   out_78320000076568703[31] = 0;
   out_78320000076568703[32] = 0;
   out_78320000076568703[33] = 0;
   out_78320000076568703[34] = 0;
   out_78320000076568703[35] = 0;
   out_78320000076568703[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_78320000076568703[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_78320000076568703[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_78320000076568703[39] = 0;
   out_78320000076568703[40] = 0;
   out_78320000076568703[41] = 0;
   out_78320000076568703[42] = 0;
   out_78320000076568703[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_78320000076568703[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_78320000076568703[45] = 0;
   out_78320000076568703[46] = 0;
   out_78320000076568703[47] = 0;
   out_78320000076568703[48] = 0;
   out_78320000076568703[49] = 0;
   out_78320000076568703[50] = 0;
   out_78320000076568703[51] = 0;
   out_78320000076568703[52] = 0;
   out_78320000076568703[53] = 0;
   out_78320000076568703[54] = 0;
   out_78320000076568703[55] = 0;
   out_78320000076568703[56] = 0;
   out_78320000076568703[57] = 1;
   out_78320000076568703[58] = 0;
   out_78320000076568703[59] = 0;
   out_78320000076568703[60] = 0;
   out_78320000076568703[61] = 0;
   out_78320000076568703[62] = 0;
   out_78320000076568703[63] = 0;
   out_78320000076568703[64] = 0;
   out_78320000076568703[65] = 0;
   out_78320000076568703[66] = dt;
   out_78320000076568703[67] = 0;
   out_78320000076568703[68] = 0;
   out_78320000076568703[69] = 0;
   out_78320000076568703[70] = 0;
   out_78320000076568703[71] = 0;
   out_78320000076568703[72] = 0;
   out_78320000076568703[73] = 0;
   out_78320000076568703[74] = 0;
   out_78320000076568703[75] = 0;
   out_78320000076568703[76] = 1;
   out_78320000076568703[77] = 0;
   out_78320000076568703[78] = 0;
   out_78320000076568703[79] = 0;
   out_78320000076568703[80] = 0;
   out_78320000076568703[81] = 0;
   out_78320000076568703[82] = 0;
   out_78320000076568703[83] = 0;
   out_78320000076568703[84] = 0;
   out_78320000076568703[85] = dt;
   out_78320000076568703[86] = 0;
   out_78320000076568703[87] = 0;
   out_78320000076568703[88] = 0;
   out_78320000076568703[89] = 0;
   out_78320000076568703[90] = 0;
   out_78320000076568703[91] = 0;
   out_78320000076568703[92] = 0;
   out_78320000076568703[93] = 0;
   out_78320000076568703[94] = 0;
   out_78320000076568703[95] = 1;
   out_78320000076568703[96] = 0;
   out_78320000076568703[97] = 0;
   out_78320000076568703[98] = 0;
   out_78320000076568703[99] = 0;
   out_78320000076568703[100] = 0;
   out_78320000076568703[101] = 0;
   out_78320000076568703[102] = 0;
   out_78320000076568703[103] = 0;
   out_78320000076568703[104] = dt;
   out_78320000076568703[105] = 0;
   out_78320000076568703[106] = 0;
   out_78320000076568703[107] = 0;
   out_78320000076568703[108] = 0;
   out_78320000076568703[109] = 0;
   out_78320000076568703[110] = 0;
   out_78320000076568703[111] = 0;
   out_78320000076568703[112] = 0;
   out_78320000076568703[113] = 0;
   out_78320000076568703[114] = 1;
   out_78320000076568703[115] = 0;
   out_78320000076568703[116] = 0;
   out_78320000076568703[117] = 0;
   out_78320000076568703[118] = 0;
   out_78320000076568703[119] = 0;
   out_78320000076568703[120] = 0;
   out_78320000076568703[121] = 0;
   out_78320000076568703[122] = 0;
   out_78320000076568703[123] = 0;
   out_78320000076568703[124] = 0;
   out_78320000076568703[125] = 0;
   out_78320000076568703[126] = 0;
   out_78320000076568703[127] = 0;
   out_78320000076568703[128] = 0;
   out_78320000076568703[129] = 0;
   out_78320000076568703[130] = 0;
   out_78320000076568703[131] = 0;
   out_78320000076568703[132] = 0;
   out_78320000076568703[133] = 1;
   out_78320000076568703[134] = 0;
   out_78320000076568703[135] = 0;
   out_78320000076568703[136] = 0;
   out_78320000076568703[137] = 0;
   out_78320000076568703[138] = 0;
   out_78320000076568703[139] = 0;
   out_78320000076568703[140] = 0;
   out_78320000076568703[141] = 0;
   out_78320000076568703[142] = 0;
   out_78320000076568703[143] = 0;
   out_78320000076568703[144] = 0;
   out_78320000076568703[145] = 0;
   out_78320000076568703[146] = 0;
   out_78320000076568703[147] = 0;
   out_78320000076568703[148] = 0;
   out_78320000076568703[149] = 0;
   out_78320000076568703[150] = 0;
   out_78320000076568703[151] = 0;
   out_78320000076568703[152] = 1;
   out_78320000076568703[153] = 0;
   out_78320000076568703[154] = 0;
   out_78320000076568703[155] = 0;
   out_78320000076568703[156] = 0;
   out_78320000076568703[157] = 0;
   out_78320000076568703[158] = 0;
   out_78320000076568703[159] = 0;
   out_78320000076568703[160] = 0;
   out_78320000076568703[161] = 0;
   out_78320000076568703[162] = 0;
   out_78320000076568703[163] = 0;
   out_78320000076568703[164] = 0;
   out_78320000076568703[165] = 0;
   out_78320000076568703[166] = 0;
   out_78320000076568703[167] = 0;
   out_78320000076568703[168] = 0;
   out_78320000076568703[169] = 0;
   out_78320000076568703[170] = 0;
   out_78320000076568703[171] = 1;
   out_78320000076568703[172] = 0;
   out_78320000076568703[173] = 0;
   out_78320000076568703[174] = 0;
   out_78320000076568703[175] = 0;
   out_78320000076568703[176] = 0;
   out_78320000076568703[177] = 0;
   out_78320000076568703[178] = 0;
   out_78320000076568703[179] = 0;
   out_78320000076568703[180] = 0;
   out_78320000076568703[181] = 0;
   out_78320000076568703[182] = 0;
   out_78320000076568703[183] = 0;
   out_78320000076568703[184] = 0;
   out_78320000076568703[185] = 0;
   out_78320000076568703[186] = 0;
   out_78320000076568703[187] = 0;
   out_78320000076568703[188] = 0;
   out_78320000076568703[189] = 0;
   out_78320000076568703[190] = 1;
   out_78320000076568703[191] = 0;
   out_78320000076568703[192] = 0;
   out_78320000076568703[193] = 0;
   out_78320000076568703[194] = 0;
   out_78320000076568703[195] = 0;
   out_78320000076568703[196] = 0;
   out_78320000076568703[197] = 0;
   out_78320000076568703[198] = 0;
   out_78320000076568703[199] = 0;
   out_78320000076568703[200] = 0;
   out_78320000076568703[201] = 0;
   out_78320000076568703[202] = 0;
   out_78320000076568703[203] = 0;
   out_78320000076568703[204] = 0;
   out_78320000076568703[205] = 0;
   out_78320000076568703[206] = 0;
   out_78320000076568703[207] = 0;
   out_78320000076568703[208] = 0;
   out_78320000076568703[209] = 1;
   out_78320000076568703[210] = 0;
   out_78320000076568703[211] = 0;
   out_78320000076568703[212] = 0;
   out_78320000076568703[213] = 0;
   out_78320000076568703[214] = 0;
   out_78320000076568703[215] = 0;
   out_78320000076568703[216] = 0;
   out_78320000076568703[217] = 0;
   out_78320000076568703[218] = 0;
   out_78320000076568703[219] = 0;
   out_78320000076568703[220] = 0;
   out_78320000076568703[221] = 0;
   out_78320000076568703[222] = 0;
   out_78320000076568703[223] = 0;
   out_78320000076568703[224] = 0;
   out_78320000076568703[225] = 0;
   out_78320000076568703[226] = 0;
   out_78320000076568703[227] = 0;
   out_78320000076568703[228] = 1;
   out_78320000076568703[229] = 0;
   out_78320000076568703[230] = 0;
   out_78320000076568703[231] = 0;
   out_78320000076568703[232] = 0;
   out_78320000076568703[233] = 0;
   out_78320000076568703[234] = 0;
   out_78320000076568703[235] = 0;
   out_78320000076568703[236] = 0;
   out_78320000076568703[237] = 0;
   out_78320000076568703[238] = 0;
   out_78320000076568703[239] = 0;
   out_78320000076568703[240] = 0;
   out_78320000076568703[241] = 0;
   out_78320000076568703[242] = 0;
   out_78320000076568703[243] = 0;
   out_78320000076568703[244] = 0;
   out_78320000076568703[245] = 0;
   out_78320000076568703[246] = 0;
   out_78320000076568703[247] = 1;
   out_78320000076568703[248] = 0;
   out_78320000076568703[249] = 0;
   out_78320000076568703[250] = 0;
   out_78320000076568703[251] = 0;
   out_78320000076568703[252] = 0;
   out_78320000076568703[253] = 0;
   out_78320000076568703[254] = 0;
   out_78320000076568703[255] = 0;
   out_78320000076568703[256] = 0;
   out_78320000076568703[257] = 0;
   out_78320000076568703[258] = 0;
   out_78320000076568703[259] = 0;
   out_78320000076568703[260] = 0;
   out_78320000076568703[261] = 0;
   out_78320000076568703[262] = 0;
   out_78320000076568703[263] = 0;
   out_78320000076568703[264] = 0;
   out_78320000076568703[265] = 0;
   out_78320000076568703[266] = 1;
   out_78320000076568703[267] = 0;
   out_78320000076568703[268] = 0;
   out_78320000076568703[269] = 0;
   out_78320000076568703[270] = 0;
   out_78320000076568703[271] = 0;
   out_78320000076568703[272] = 0;
   out_78320000076568703[273] = 0;
   out_78320000076568703[274] = 0;
   out_78320000076568703[275] = 0;
   out_78320000076568703[276] = 0;
   out_78320000076568703[277] = 0;
   out_78320000076568703[278] = 0;
   out_78320000076568703[279] = 0;
   out_78320000076568703[280] = 0;
   out_78320000076568703[281] = 0;
   out_78320000076568703[282] = 0;
   out_78320000076568703[283] = 0;
   out_78320000076568703[284] = 0;
   out_78320000076568703[285] = 1;
   out_78320000076568703[286] = 0;
   out_78320000076568703[287] = 0;
   out_78320000076568703[288] = 0;
   out_78320000076568703[289] = 0;
   out_78320000076568703[290] = 0;
   out_78320000076568703[291] = 0;
   out_78320000076568703[292] = 0;
   out_78320000076568703[293] = 0;
   out_78320000076568703[294] = 0;
   out_78320000076568703[295] = 0;
   out_78320000076568703[296] = 0;
   out_78320000076568703[297] = 0;
   out_78320000076568703[298] = 0;
   out_78320000076568703[299] = 0;
   out_78320000076568703[300] = 0;
   out_78320000076568703[301] = 0;
   out_78320000076568703[302] = 0;
   out_78320000076568703[303] = 0;
   out_78320000076568703[304] = 1;
   out_78320000076568703[305] = 0;
   out_78320000076568703[306] = 0;
   out_78320000076568703[307] = 0;
   out_78320000076568703[308] = 0;
   out_78320000076568703[309] = 0;
   out_78320000076568703[310] = 0;
   out_78320000076568703[311] = 0;
   out_78320000076568703[312] = 0;
   out_78320000076568703[313] = 0;
   out_78320000076568703[314] = 0;
   out_78320000076568703[315] = 0;
   out_78320000076568703[316] = 0;
   out_78320000076568703[317] = 0;
   out_78320000076568703[318] = 0;
   out_78320000076568703[319] = 0;
   out_78320000076568703[320] = 0;
   out_78320000076568703[321] = 0;
   out_78320000076568703[322] = 0;
   out_78320000076568703[323] = 1;
}
void h_4(double *state, double *unused, double *out_2403402202974529453) {
   out_2403402202974529453[0] = state[6] + state[9];
   out_2403402202974529453[1] = state[7] + state[10];
   out_2403402202974529453[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_5573260138414675953) {
   out_5573260138414675953[0] = 0;
   out_5573260138414675953[1] = 0;
   out_5573260138414675953[2] = 0;
   out_5573260138414675953[3] = 0;
   out_5573260138414675953[4] = 0;
   out_5573260138414675953[5] = 0;
   out_5573260138414675953[6] = 1;
   out_5573260138414675953[7] = 0;
   out_5573260138414675953[8] = 0;
   out_5573260138414675953[9] = 1;
   out_5573260138414675953[10] = 0;
   out_5573260138414675953[11] = 0;
   out_5573260138414675953[12] = 0;
   out_5573260138414675953[13] = 0;
   out_5573260138414675953[14] = 0;
   out_5573260138414675953[15] = 0;
   out_5573260138414675953[16] = 0;
   out_5573260138414675953[17] = 0;
   out_5573260138414675953[18] = 0;
   out_5573260138414675953[19] = 0;
   out_5573260138414675953[20] = 0;
   out_5573260138414675953[21] = 0;
   out_5573260138414675953[22] = 0;
   out_5573260138414675953[23] = 0;
   out_5573260138414675953[24] = 0;
   out_5573260138414675953[25] = 1;
   out_5573260138414675953[26] = 0;
   out_5573260138414675953[27] = 0;
   out_5573260138414675953[28] = 1;
   out_5573260138414675953[29] = 0;
   out_5573260138414675953[30] = 0;
   out_5573260138414675953[31] = 0;
   out_5573260138414675953[32] = 0;
   out_5573260138414675953[33] = 0;
   out_5573260138414675953[34] = 0;
   out_5573260138414675953[35] = 0;
   out_5573260138414675953[36] = 0;
   out_5573260138414675953[37] = 0;
   out_5573260138414675953[38] = 0;
   out_5573260138414675953[39] = 0;
   out_5573260138414675953[40] = 0;
   out_5573260138414675953[41] = 0;
   out_5573260138414675953[42] = 0;
   out_5573260138414675953[43] = 0;
   out_5573260138414675953[44] = 1;
   out_5573260138414675953[45] = 0;
   out_5573260138414675953[46] = 0;
   out_5573260138414675953[47] = 1;
   out_5573260138414675953[48] = 0;
   out_5573260138414675953[49] = 0;
   out_5573260138414675953[50] = 0;
   out_5573260138414675953[51] = 0;
   out_5573260138414675953[52] = 0;
   out_5573260138414675953[53] = 0;
}
void h_10(double *state, double *unused, double *out_1415940429779603810) {
   out_1415940429779603810[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_1415940429779603810[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_1415940429779603810[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_5540918162512642087) {
   out_5540918162512642087[0] = 0;
   out_5540918162512642087[1] = 9.8100000000000005*cos(state[1]);
   out_5540918162512642087[2] = 0;
   out_5540918162512642087[3] = 0;
   out_5540918162512642087[4] = -state[8];
   out_5540918162512642087[5] = state[7];
   out_5540918162512642087[6] = 0;
   out_5540918162512642087[7] = state[5];
   out_5540918162512642087[8] = -state[4];
   out_5540918162512642087[9] = 0;
   out_5540918162512642087[10] = 0;
   out_5540918162512642087[11] = 0;
   out_5540918162512642087[12] = 1;
   out_5540918162512642087[13] = 0;
   out_5540918162512642087[14] = 0;
   out_5540918162512642087[15] = 1;
   out_5540918162512642087[16] = 0;
   out_5540918162512642087[17] = 0;
   out_5540918162512642087[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_5540918162512642087[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_5540918162512642087[20] = 0;
   out_5540918162512642087[21] = state[8];
   out_5540918162512642087[22] = 0;
   out_5540918162512642087[23] = -state[6];
   out_5540918162512642087[24] = -state[5];
   out_5540918162512642087[25] = 0;
   out_5540918162512642087[26] = state[3];
   out_5540918162512642087[27] = 0;
   out_5540918162512642087[28] = 0;
   out_5540918162512642087[29] = 0;
   out_5540918162512642087[30] = 0;
   out_5540918162512642087[31] = 1;
   out_5540918162512642087[32] = 0;
   out_5540918162512642087[33] = 0;
   out_5540918162512642087[34] = 1;
   out_5540918162512642087[35] = 0;
   out_5540918162512642087[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_5540918162512642087[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_5540918162512642087[38] = 0;
   out_5540918162512642087[39] = -state[7];
   out_5540918162512642087[40] = state[6];
   out_5540918162512642087[41] = 0;
   out_5540918162512642087[42] = state[4];
   out_5540918162512642087[43] = -state[3];
   out_5540918162512642087[44] = 0;
   out_5540918162512642087[45] = 0;
   out_5540918162512642087[46] = 0;
   out_5540918162512642087[47] = 0;
   out_5540918162512642087[48] = 0;
   out_5540918162512642087[49] = 0;
   out_5540918162512642087[50] = 1;
   out_5540918162512642087[51] = 0;
   out_5540918162512642087[52] = 0;
   out_5540918162512642087[53] = 1;
}
void h_13(double *state, double *unused, double *out_8116494657900557165) {
   out_8116494657900557165[0] = state[3];
   out_8116494657900557165[1] = state[4];
   out_8116494657900557165[2] = state[5];
}
void H_13(double *state, double *unused, double *out_8785533963747008754) {
   out_8785533963747008754[0] = 0;
   out_8785533963747008754[1] = 0;
   out_8785533963747008754[2] = 0;
   out_8785533963747008754[3] = 1;
   out_8785533963747008754[4] = 0;
   out_8785533963747008754[5] = 0;
   out_8785533963747008754[6] = 0;
   out_8785533963747008754[7] = 0;
   out_8785533963747008754[8] = 0;
   out_8785533963747008754[9] = 0;
   out_8785533963747008754[10] = 0;
   out_8785533963747008754[11] = 0;
   out_8785533963747008754[12] = 0;
   out_8785533963747008754[13] = 0;
   out_8785533963747008754[14] = 0;
   out_8785533963747008754[15] = 0;
   out_8785533963747008754[16] = 0;
   out_8785533963747008754[17] = 0;
   out_8785533963747008754[18] = 0;
   out_8785533963747008754[19] = 0;
   out_8785533963747008754[20] = 0;
   out_8785533963747008754[21] = 0;
   out_8785533963747008754[22] = 1;
   out_8785533963747008754[23] = 0;
   out_8785533963747008754[24] = 0;
   out_8785533963747008754[25] = 0;
   out_8785533963747008754[26] = 0;
   out_8785533963747008754[27] = 0;
   out_8785533963747008754[28] = 0;
   out_8785533963747008754[29] = 0;
   out_8785533963747008754[30] = 0;
   out_8785533963747008754[31] = 0;
   out_8785533963747008754[32] = 0;
   out_8785533963747008754[33] = 0;
   out_8785533963747008754[34] = 0;
   out_8785533963747008754[35] = 0;
   out_8785533963747008754[36] = 0;
   out_8785533963747008754[37] = 0;
   out_8785533963747008754[38] = 0;
   out_8785533963747008754[39] = 0;
   out_8785533963747008754[40] = 0;
   out_8785533963747008754[41] = 1;
   out_8785533963747008754[42] = 0;
   out_8785533963747008754[43] = 0;
   out_8785533963747008754[44] = 0;
   out_8785533963747008754[45] = 0;
   out_8785533963747008754[46] = 0;
   out_8785533963747008754[47] = 0;
   out_8785533963747008754[48] = 0;
   out_8785533963747008754[49] = 0;
   out_8785533963747008754[50] = 0;
   out_8785533963747008754[51] = 0;
   out_8785533963747008754[52] = 0;
   out_8785533963747008754[53] = 0;
}
void h_14(double *state, double *unused, double *out_2556692697037776409) {
   out_2556692697037776409[0] = state[6];
   out_2556692697037776409[1] = state[7];
   out_2556692697037776409[2] = state[8];
}
void H_14(double *state, double *unused, double *out_8910243078955391134) {
   out_8910243078955391134[0] = 0;
   out_8910243078955391134[1] = 0;
   out_8910243078955391134[2] = 0;
   out_8910243078955391134[3] = 0;
   out_8910243078955391134[4] = 0;
   out_8910243078955391134[5] = 0;
   out_8910243078955391134[6] = 1;
   out_8910243078955391134[7] = 0;
   out_8910243078955391134[8] = 0;
   out_8910243078955391134[9] = 0;
   out_8910243078955391134[10] = 0;
   out_8910243078955391134[11] = 0;
   out_8910243078955391134[12] = 0;
   out_8910243078955391134[13] = 0;
   out_8910243078955391134[14] = 0;
   out_8910243078955391134[15] = 0;
   out_8910243078955391134[16] = 0;
   out_8910243078955391134[17] = 0;
   out_8910243078955391134[18] = 0;
   out_8910243078955391134[19] = 0;
   out_8910243078955391134[20] = 0;
   out_8910243078955391134[21] = 0;
   out_8910243078955391134[22] = 0;
   out_8910243078955391134[23] = 0;
   out_8910243078955391134[24] = 0;
   out_8910243078955391134[25] = 1;
   out_8910243078955391134[26] = 0;
   out_8910243078955391134[27] = 0;
   out_8910243078955391134[28] = 0;
   out_8910243078955391134[29] = 0;
   out_8910243078955391134[30] = 0;
   out_8910243078955391134[31] = 0;
   out_8910243078955391134[32] = 0;
   out_8910243078955391134[33] = 0;
   out_8910243078955391134[34] = 0;
   out_8910243078955391134[35] = 0;
   out_8910243078955391134[36] = 0;
   out_8910243078955391134[37] = 0;
   out_8910243078955391134[38] = 0;
   out_8910243078955391134[39] = 0;
   out_8910243078955391134[40] = 0;
   out_8910243078955391134[41] = 0;
   out_8910243078955391134[42] = 0;
   out_8910243078955391134[43] = 0;
   out_8910243078955391134[44] = 1;
   out_8910243078955391134[45] = 0;
   out_8910243078955391134[46] = 0;
   out_8910243078955391134[47] = 0;
   out_8910243078955391134[48] = 0;
   out_8910243078955391134[49] = 0;
   out_8910243078955391134[50] = 0;
   out_8910243078955391134[51] = 0;
   out_8910243078955391134[52] = 0;
   out_8910243078955391134[53] = 0;
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
void pose_err_fun(double *nom_x, double *delta_x, double *out_7899872685628621531) {
  err_fun(nom_x, delta_x, out_7899872685628621531);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_1215289726053279423) {
  inv_err_fun(nom_x, true_x, out_1215289726053279423);
}
void pose_H_mod_fun(double *state, double *out_420741753375595218) {
  H_mod_fun(state, out_420741753375595218);
}
void pose_f_fun(double *state, double dt, double *out_5996963235034927992) {
  f_fun(state,  dt, out_5996963235034927992);
}
void pose_F_fun(double *state, double dt, double *out_78320000076568703) {
  F_fun(state,  dt, out_78320000076568703);
}
void pose_h_4(double *state, double *unused, double *out_2403402202974529453) {
  h_4(state, unused, out_2403402202974529453);
}
void pose_H_4(double *state, double *unused, double *out_5573260138414675953) {
  H_4(state, unused, out_5573260138414675953);
}
void pose_h_10(double *state, double *unused, double *out_1415940429779603810) {
  h_10(state, unused, out_1415940429779603810);
}
void pose_H_10(double *state, double *unused, double *out_5540918162512642087) {
  H_10(state, unused, out_5540918162512642087);
}
void pose_h_13(double *state, double *unused, double *out_8116494657900557165) {
  h_13(state, unused, out_8116494657900557165);
}
void pose_H_13(double *state, double *unused, double *out_8785533963747008754) {
  H_13(state, unused, out_8785533963747008754);
}
void pose_h_14(double *state, double *unused, double *out_2556692697037776409) {
  h_14(state, unused, out_2556692697037776409);
}
void pose_H_14(double *state, double *unused, double *out_8910243078955391134) {
  H_14(state, unused, out_8910243078955391134);
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
