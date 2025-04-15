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
void err_fun(double *nom_x, double *delta_x, double *out_3306664206309014289) {
   out_3306664206309014289[0] = delta_x[0] + nom_x[0];
   out_3306664206309014289[1] = delta_x[1] + nom_x[1];
   out_3306664206309014289[2] = delta_x[2] + nom_x[2];
   out_3306664206309014289[3] = delta_x[3] + nom_x[3];
   out_3306664206309014289[4] = delta_x[4] + nom_x[4];
   out_3306664206309014289[5] = delta_x[5] + nom_x[5];
   out_3306664206309014289[6] = delta_x[6] + nom_x[6];
   out_3306664206309014289[7] = delta_x[7] + nom_x[7];
   out_3306664206309014289[8] = delta_x[8] + nom_x[8];
   out_3306664206309014289[9] = delta_x[9] + nom_x[9];
   out_3306664206309014289[10] = delta_x[10] + nom_x[10];
   out_3306664206309014289[11] = delta_x[11] + nom_x[11];
   out_3306664206309014289[12] = delta_x[12] + nom_x[12];
   out_3306664206309014289[13] = delta_x[13] + nom_x[13];
   out_3306664206309014289[14] = delta_x[14] + nom_x[14];
   out_3306664206309014289[15] = delta_x[15] + nom_x[15];
   out_3306664206309014289[16] = delta_x[16] + nom_x[16];
   out_3306664206309014289[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_570891515664221910) {
   out_570891515664221910[0] = -nom_x[0] + true_x[0];
   out_570891515664221910[1] = -nom_x[1] + true_x[1];
   out_570891515664221910[2] = -nom_x[2] + true_x[2];
   out_570891515664221910[3] = -nom_x[3] + true_x[3];
   out_570891515664221910[4] = -nom_x[4] + true_x[4];
   out_570891515664221910[5] = -nom_x[5] + true_x[5];
   out_570891515664221910[6] = -nom_x[6] + true_x[6];
   out_570891515664221910[7] = -nom_x[7] + true_x[7];
   out_570891515664221910[8] = -nom_x[8] + true_x[8];
   out_570891515664221910[9] = -nom_x[9] + true_x[9];
   out_570891515664221910[10] = -nom_x[10] + true_x[10];
   out_570891515664221910[11] = -nom_x[11] + true_x[11];
   out_570891515664221910[12] = -nom_x[12] + true_x[12];
   out_570891515664221910[13] = -nom_x[13] + true_x[13];
   out_570891515664221910[14] = -nom_x[14] + true_x[14];
   out_570891515664221910[15] = -nom_x[15] + true_x[15];
   out_570891515664221910[16] = -nom_x[16] + true_x[16];
   out_570891515664221910[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_8375847635798993256) {
   out_8375847635798993256[0] = 1.0;
   out_8375847635798993256[1] = 0.0;
   out_8375847635798993256[2] = 0.0;
   out_8375847635798993256[3] = 0.0;
   out_8375847635798993256[4] = 0.0;
   out_8375847635798993256[5] = 0.0;
   out_8375847635798993256[6] = 0.0;
   out_8375847635798993256[7] = 0.0;
   out_8375847635798993256[8] = 0.0;
   out_8375847635798993256[9] = 0.0;
   out_8375847635798993256[10] = 0.0;
   out_8375847635798993256[11] = 0.0;
   out_8375847635798993256[12] = 0.0;
   out_8375847635798993256[13] = 0.0;
   out_8375847635798993256[14] = 0.0;
   out_8375847635798993256[15] = 0.0;
   out_8375847635798993256[16] = 0.0;
   out_8375847635798993256[17] = 0.0;
   out_8375847635798993256[18] = 0.0;
   out_8375847635798993256[19] = 1.0;
   out_8375847635798993256[20] = 0.0;
   out_8375847635798993256[21] = 0.0;
   out_8375847635798993256[22] = 0.0;
   out_8375847635798993256[23] = 0.0;
   out_8375847635798993256[24] = 0.0;
   out_8375847635798993256[25] = 0.0;
   out_8375847635798993256[26] = 0.0;
   out_8375847635798993256[27] = 0.0;
   out_8375847635798993256[28] = 0.0;
   out_8375847635798993256[29] = 0.0;
   out_8375847635798993256[30] = 0.0;
   out_8375847635798993256[31] = 0.0;
   out_8375847635798993256[32] = 0.0;
   out_8375847635798993256[33] = 0.0;
   out_8375847635798993256[34] = 0.0;
   out_8375847635798993256[35] = 0.0;
   out_8375847635798993256[36] = 0.0;
   out_8375847635798993256[37] = 0.0;
   out_8375847635798993256[38] = 1.0;
   out_8375847635798993256[39] = 0.0;
   out_8375847635798993256[40] = 0.0;
   out_8375847635798993256[41] = 0.0;
   out_8375847635798993256[42] = 0.0;
   out_8375847635798993256[43] = 0.0;
   out_8375847635798993256[44] = 0.0;
   out_8375847635798993256[45] = 0.0;
   out_8375847635798993256[46] = 0.0;
   out_8375847635798993256[47] = 0.0;
   out_8375847635798993256[48] = 0.0;
   out_8375847635798993256[49] = 0.0;
   out_8375847635798993256[50] = 0.0;
   out_8375847635798993256[51] = 0.0;
   out_8375847635798993256[52] = 0.0;
   out_8375847635798993256[53] = 0.0;
   out_8375847635798993256[54] = 0.0;
   out_8375847635798993256[55] = 0.0;
   out_8375847635798993256[56] = 0.0;
   out_8375847635798993256[57] = 1.0;
   out_8375847635798993256[58] = 0.0;
   out_8375847635798993256[59] = 0.0;
   out_8375847635798993256[60] = 0.0;
   out_8375847635798993256[61] = 0.0;
   out_8375847635798993256[62] = 0.0;
   out_8375847635798993256[63] = 0.0;
   out_8375847635798993256[64] = 0.0;
   out_8375847635798993256[65] = 0.0;
   out_8375847635798993256[66] = 0.0;
   out_8375847635798993256[67] = 0.0;
   out_8375847635798993256[68] = 0.0;
   out_8375847635798993256[69] = 0.0;
   out_8375847635798993256[70] = 0.0;
   out_8375847635798993256[71] = 0.0;
   out_8375847635798993256[72] = 0.0;
   out_8375847635798993256[73] = 0.0;
   out_8375847635798993256[74] = 0.0;
   out_8375847635798993256[75] = 0.0;
   out_8375847635798993256[76] = 1.0;
   out_8375847635798993256[77] = 0.0;
   out_8375847635798993256[78] = 0.0;
   out_8375847635798993256[79] = 0.0;
   out_8375847635798993256[80] = 0.0;
   out_8375847635798993256[81] = 0.0;
   out_8375847635798993256[82] = 0.0;
   out_8375847635798993256[83] = 0.0;
   out_8375847635798993256[84] = 0.0;
   out_8375847635798993256[85] = 0.0;
   out_8375847635798993256[86] = 0.0;
   out_8375847635798993256[87] = 0.0;
   out_8375847635798993256[88] = 0.0;
   out_8375847635798993256[89] = 0.0;
   out_8375847635798993256[90] = 0.0;
   out_8375847635798993256[91] = 0.0;
   out_8375847635798993256[92] = 0.0;
   out_8375847635798993256[93] = 0.0;
   out_8375847635798993256[94] = 0.0;
   out_8375847635798993256[95] = 1.0;
   out_8375847635798993256[96] = 0.0;
   out_8375847635798993256[97] = 0.0;
   out_8375847635798993256[98] = 0.0;
   out_8375847635798993256[99] = 0.0;
   out_8375847635798993256[100] = 0.0;
   out_8375847635798993256[101] = 0.0;
   out_8375847635798993256[102] = 0.0;
   out_8375847635798993256[103] = 0.0;
   out_8375847635798993256[104] = 0.0;
   out_8375847635798993256[105] = 0.0;
   out_8375847635798993256[106] = 0.0;
   out_8375847635798993256[107] = 0.0;
   out_8375847635798993256[108] = 0.0;
   out_8375847635798993256[109] = 0.0;
   out_8375847635798993256[110] = 0.0;
   out_8375847635798993256[111] = 0.0;
   out_8375847635798993256[112] = 0.0;
   out_8375847635798993256[113] = 0.0;
   out_8375847635798993256[114] = 1.0;
   out_8375847635798993256[115] = 0.0;
   out_8375847635798993256[116] = 0.0;
   out_8375847635798993256[117] = 0.0;
   out_8375847635798993256[118] = 0.0;
   out_8375847635798993256[119] = 0.0;
   out_8375847635798993256[120] = 0.0;
   out_8375847635798993256[121] = 0.0;
   out_8375847635798993256[122] = 0.0;
   out_8375847635798993256[123] = 0.0;
   out_8375847635798993256[124] = 0.0;
   out_8375847635798993256[125] = 0.0;
   out_8375847635798993256[126] = 0.0;
   out_8375847635798993256[127] = 0.0;
   out_8375847635798993256[128] = 0.0;
   out_8375847635798993256[129] = 0.0;
   out_8375847635798993256[130] = 0.0;
   out_8375847635798993256[131] = 0.0;
   out_8375847635798993256[132] = 0.0;
   out_8375847635798993256[133] = 1.0;
   out_8375847635798993256[134] = 0.0;
   out_8375847635798993256[135] = 0.0;
   out_8375847635798993256[136] = 0.0;
   out_8375847635798993256[137] = 0.0;
   out_8375847635798993256[138] = 0.0;
   out_8375847635798993256[139] = 0.0;
   out_8375847635798993256[140] = 0.0;
   out_8375847635798993256[141] = 0.0;
   out_8375847635798993256[142] = 0.0;
   out_8375847635798993256[143] = 0.0;
   out_8375847635798993256[144] = 0.0;
   out_8375847635798993256[145] = 0.0;
   out_8375847635798993256[146] = 0.0;
   out_8375847635798993256[147] = 0.0;
   out_8375847635798993256[148] = 0.0;
   out_8375847635798993256[149] = 0.0;
   out_8375847635798993256[150] = 0.0;
   out_8375847635798993256[151] = 0.0;
   out_8375847635798993256[152] = 1.0;
   out_8375847635798993256[153] = 0.0;
   out_8375847635798993256[154] = 0.0;
   out_8375847635798993256[155] = 0.0;
   out_8375847635798993256[156] = 0.0;
   out_8375847635798993256[157] = 0.0;
   out_8375847635798993256[158] = 0.0;
   out_8375847635798993256[159] = 0.0;
   out_8375847635798993256[160] = 0.0;
   out_8375847635798993256[161] = 0.0;
   out_8375847635798993256[162] = 0.0;
   out_8375847635798993256[163] = 0.0;
   out_8375847635798993256[164] = 0.0;
   out_8375847635798993256[165] = 0.0;
   out_8375847635798993256[166] = 0.0;
   out_8375847635798993256[167] = 0.0;
   out_8375847635798993256[168] = 0.0;
   out_8375847635798993256[169] = 0.0;
   out_8375847635798993256[170] = 0.0;
   out_8375847635798993256[171] = 1.0;
   out_8375847635798993256[172] = 0.0;
   out_8375847635798993256[173] = 0.0;
   out_8375847635798993256[174] = 0.0;
   out_8375847635798993256[175] = 0.0;
   out_8375847635798993256[176] = 0.0;
   out_8375847635798993256[177] = 0.0;
   out_8375847635798993256[178] = 0.0;
   out_8375847635798993256[179] = 0.0;
   out_8375847635798993256[180] = 0.0;
   out_8375847635798993256[181] = 0.0;
   out_8375847635798993256[182] = 0.0;
   out_8375847635798993256[183] = 0.0;
   out_8375847635798993256[184] = 0.0;
   out_8375847635798993256[185] = 0.0;
   out_8375847635798993256[186] = 0.0;
   out_8375847635798993256[187] = 0.0;
   out_8375847635798993256[188] = 0.0;
   out_8375847635798993256[189] = 0.0;
   out_8375847635798993256[190] = 1.0;
   out_8375847635798993256[191] = 0.0;
   out_8375847635798993256[192] = 0.0;
   out_8375847635798993256[193] = 0.0;
   out_8375847635798993256[194] = 0.0;
   out_8375847635798993256[195] = 0.0;
   out_8375847635798993256[196] = 0.0;
   out_8375847635798993256[197] = 0.0;
   out_8375847635798993256[198] = 0.0;
   out_8375847635798993256[199] = 0.0;
   out_8375847635798993256[200] = 0.0;
   out_8375847635798993256[201] = 0.0;
   out_8375847635798993256[202] = 0.0;
   out_8375847635798993256[203] = 0.0;
   out_8375847635798993256[204] = 0.0;
   out_8375847635798993256[205] = 0.0;
   out_8375847635798993256[206] = 0.0;
   out_8375847635798993256[207] = 0.0;
   out_8375847635798993256[208] = 0.0;
   out_8375847635798993256[209] = 1.0;
   out_8375847635798993256[210] = 0.0;
   out_8375847635798993256[211] = 0.0;
   out_8375847635798993256[212] = 0.0;
   out_8375847635798993256[213] = 0.0;
   out_8375847635798993256[214] = 0.0;
   out_8375847635798993256[215] = 0.0;
   out_8375847635798993256[216] = 0.0;
   out_8375847635798993256[217] = 0.0;
   out_8375847635798993256[218] = 0.0;
   out_8375847635798993256[219] = 0.0;
   out_8375847635798993256[220] = 0.0;
   out_8375847635798993256[221] = 0.0;
   out_8375847635798993256[222] = 0.0;
   out_8375847635798993256[223] = 0.0;
   out_8375847635798993256[224] = 0.0;
   out_8375847635798993256[225] = 0.0;
   out_8375847635798993256[226] = 0.0;
   out_8375847635798993256[227] = 0.0;
   out_8375847635798993256[228] = 1.0;
   out_8375847635798993256[229] = 0.0;
   out_8375847635798993256[230] = 0.0;
   out_8375847635798993256[231] = 0.0;
   out_8375847635798993256[232] = 0.0;
   out_8375847635798993256[233] = 0.0;
   out_8375847635798993256[234] = 0.0;
   out_8375847635798993256[235] = 0.0;
   out_8375847635798993256[236] = 0.0;
   out_8375847635798993256[237] = 0.0;
   out_8375847635798993256[238] = 0.0;
   out_8375847635798993256[239] = 0.0;
   out_8375847635798993256[240] = 0.0;
   out_8375847635798993256[241] = 0.0;
   out_8375847635798993256[242] = 0.0;
   out_8375847635798993256[243] = 0.0;
   out_8375847635798993256[244] = 0.0;
   out_8375847635798993256[245] = 0.0;
   out_8375847635798993256[246] = 0.0;
   out_8375847635798993256[247] = 1.0;
   out_8375847635798993256[248] = 0.0;
   out_8375847635798993256[249] = 0.0;
   out_8375847635798993256[250] = 0.0;
   out_8375847635798993256[251] = 0.0;
   out_8375847635798993256[252] = 0.0;
   out_8375847635798993256[253] = 0.0;
   out_8375847635798993256[254] = 0.0;
   out_8375847635798993256[255] = 0.0;
   out_8375847635798993256[256] = 0.0;
   out_8375847635798993256[257] = 0.0;
   out_8375847635798993256[258] = 0.0;
   out_8375847635798993256[259] = 0.0;
   out_8375847635798993256[260] = 0.0;
   out_8375847635798993256[261] = 0.0;
   out_8375847635798993256[262] = 0.0;
   out_8375847635798993256[263] = 0.0;
   out_8375847635798993256[264] = 0.0;
   out_8375847635798993256[265] = 0.0;
   out_8375847635798993256[266] = 1.0;
   out_8375847635798993256[267] = 0.0;
   out_8375847635798993256[268] = 0.0;
   out_8375847635798993256[269] = 0.0;
   out_8375847635798993256[270] = 0.0;
   out_8375847635798993256[271] = 0.0;
   out_8375847635798993256[272] = 0.0;
   out_8375847635798993256[273] = 0.0;
   out_8375847635798993256[274] = 0.0;
   out_8375847635798993256[275] = 0.0;
   out_8375847635798993256[276] = 0.0;
   out_8375847635798993256[277] = 0.0;
   out_8375847635798993256[278] = 0.0;
   out_8375847635798993256[279] = 0.0;
   out_8375847635798993256[280] = 0.0;
   out_8375847635798993256[281] = 0.0;
   out_8375847635798993256[282] = 0.0;
   out_8375847635798993256[283] = 0.0;
   out_8375847635798993256[284] = 0.0;
   out_8375847635798993256[285] = 1.0;
   out_8375847635798993256[286] = 0.0;
   out_8375847635798993256[287] = 0.0;
   out_8375847635798993256[288] = 0.0;
   out_8375847635798993256[289] = 0.0;
   out_8375847635798993256[290] = 0.0;
   out_8375847635798993256[291] = 0.0;
   out_8375847635798993256[292] = 0.0;
   out_8375847635798993256[293] = 0.0;
   out_8375847635798993256[294] = 0.0;
   out_8375847635798993256[295] = 0.0;
   out_8375847635798993256[296] = 0.0;
   out_8375847635798993256[297] = 0.0;
   out_8375847635798993256[298] = 0.0;
   out_8375847635798993256[299] = 0.0;
   out_8375847635798993256[300] = 0.0;
   out_8375847635798993256[301] = 0.0;
   out_8375847635798993256[302] = 0.0;
   out_8375847635798993256[303] = 0.0;
   out_8375847635798993256[304] = 1.0;
   out_8375847635798993256[305] = 0.0;
   out_8375847635798993256[306] = 0.0;
   out_8375847635798993256[307] = 0.0;
   out_8375847635798993256[308] = 0.0;
   out_8375847635798993256[309] = 0.0;
   out_8375847635798993256[310] = 0.0;
   out_8375847635798993256[311] = 0.0;
   out_8375847635798993256[312] = 0.0;
   out_8375847635798993256[313] = 0.0;
   out_8375847635798993256[314] = 0.0;
   out_8375847635798993256[315] = 0.0;
   out_8375847635798993256[316] = 0.0;
   out_8375847635798993256[317] = 0.0;
   out_8375847635798993256[318] = 0.0;
   out_8375847635798993256[319] = 0.0;
   out_8375847635798993256[320] = 0.0;
   out_8375847635798993256[321] = 0.0;
   out_8375847635798993256[322] = 0.0;
   out_8375847635798993256[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_8983403032593092745) {
   out_8983403032593092745[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_8983403032593092745[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_8983403032593092745[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_8983403032593092745[3] = dt*state[12] + state[3];
   out_8983403032593092745[4] = dt*state[13] + state[4];
   out_8983403032593092745[5] = dt*state[14] + state[5];
   out_8983403032593092745[6] = state[6];
   out_8983403032593092745[7] = state[7];
   out_8983403032593092745[8] = state[8];
   out_8983403032593092745[9] = state[9];
   out_8983403032593092745[10] = state[10];
   out_8983403032593092745[11] = state[11];
   out_8983403032593092745[12] = state[12];
   out_8983403032593092745[13] = state[13];
   out_8983403032593092745[14] = state[14];
   out_8983403032593092745[15] = state[15];
   out_8983403032593092745[16] = state[16];
   out_8983403032593092745[17] = state[17];
}
void F_fun(double *state, double dt, double *out_564215406758229092) {
   out_564215406758229092[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_564215406758229092[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_564215406758229092[2] = 0;
   out_564215406758229092[3] = 0;
   out_564215406758229092[4] = 0;
   out_564215406758229092[5] = 0;
   out_564215406758229092[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_564215406758229092[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_564215406758229092[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_564215406758229092[9] = 0;
   out_564215406758229092[10] = 0;
   out_564215406758229092[11] = 0;
   out_564215406758229092[12] = 0;
   out_564215406758229092[13] = 0;
   out_564215406758229092[14] = 0;
   out_564215406758229092[15] = 0;
   out_564215406758229092[16] = 0;
   out_564215406758229092[17] = 0;
   out_564215406758229092[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_564215406758229092[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_564215406758229092[20] = 0;
   out_564215406758229092[21] = 0;
   out_564215406758229092[22] = 0;
   out_564215406758229092[23] = 0;
   out_564215406758229092[24] = 0;
   out_564215406758229092[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_564215406758229092[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_564215406758229092[27] = 0;
   out_564215406758229092[28] = 0;
   out_564215406758229092[29] = 0;
   out_564215406758229092[30] = 0;
   out_564215406758229092[31] = 0;
   out_564215406758229092[32] = 0;
   out_564215406758229092[33] = 0;
   out_564215406758229092[34] = 0;
   out_564215406758229092[35] = 0;
   out_564215406758229092[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_564215406758229092[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_564215406758229092[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_564215406758229092[39] = 0;
   out_564215406758229092[40] = 0;
   out_564215406758229092[41] = 0;
   out_564215406758229092[42] = 0;
   out_564215406758229092[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_564215406758229092[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_564215406758229092[45] = 0;
   out_564215406758229092[46] = 0;
   out_564215406758229092[47] = 0;
   out_564215406758229092[48] = 0;
   out_564215406758229092[49] = 0;
   out_564215406758229092[50] = 0;
   out_564215406758229092[51] = 0;
   out_564215406758229092[52] = 0;
   out_564215406758229092[53] = 0;
   out_564215406758229092[54] = 0;
   out_564215406758229092[55] = 0;
   out_564215406758229092[56] = 0;
   out_564215406758229092[57] = 1;
   out_564215406758229092[58] = 0;
   out_564215406758229092[59] = 0;
   out_564215406758229092[60] = 0;
   out_564215406758229092[61] = 0;
   out_564215406758229092[62] = 0;
   out_564215406758229092[63] = 0;
   out_564215406758229092[64] = 0;
   out_564215406758229092[65] = 0;
   out_564215406758229092[66] = dt;
   out_564215406758229092[67] = 0;
   out_564215406758229092[68] = 0;
   out_564215406758229092[69] = 0;
   out_564215406758229092[70] = 0;
   out_564215406758229092[71] = 0;
   out_564215406758229092[72] = 0;
   out_564215406758229092[73] = 0;
   out_564215406758229092[74] = 0;
   out_564215406758229092[75] = 0;
   out_564215406758229092[76] = 1;
   out_564215406758229092[77] = 0;
   out_564215406758229092[78] = 0;
   out_564215406758229092[79] = 0;
   out_564215406758229092[80] = 0;
   out_564215406758229092[81] = 0;
   out_564215406758229092[82] = 0;
   out_564215406758229092[83] = 0;
   out_564215406758229092[84] = 0;
   out_564215406758229092[85] = dt;
   out_564215406758229092[86] = 0;
   out_564215406758229092[87] = 0;
   out_564215406758229092[88] = 0;
   out_564215406758229092[89] = 0;
   out_564215406758229092[90] = 0;
   out_564215406758229092[91] = 0;
   out_564215406758229092[92] = 0;
   out_564215406758229092[93] = 0;
   out_564215406758229092[94] = 0;
   out_564215406758229092[95] = 1;
   out_564215406758229092[96] = 0;
   out_564215406758229092[97] = 0;
   out_564215406758229092[98] = 0;
   out_564215406758229092[99] = 0;
   out_564215406758229092[100] = 0;
   out_564215406758229092[101] = 0;
   out_564215406758229092[102] = 0;
   out_564215406758229092[103] = 0;
   out_564215406758229092[104] = dt;
   out_564215406758229092[105] = 0;
   out_564215406758229092[106] = 0;
   out_564215406758229092[107] = 0;
   out_564215406758229092[108] = 0;
   out_564215406758229092[109] = 0;
   out_564215406758229092[110] = 0;
   out_564215406758229092[111] = 0;
   out_564215406758229092[112] = 0;
   out_564215406758229092[113] = 0;
   out_564215406758229092[114] = 1;
   out_564215406758229092[115] = 0;
   out_564215406758229092[116] = 0;
   out_564215406758229092[117] = 0;
   out_564215406758229092[118] = 0;
   out_564215406758229092[119] = 0;
   out_564215406758229092[120] = 0;
   out_564215406758229092[121] = 0;
   out_564215406758229092[122] = 0;
   out_564215406758229092[123] = 0;
   out_564215406758229092[124] = 0;
   out_564215406758229092[125] = 0;
   out_564215406758229092[126] = 0;
   out_564215406758229092[127] = 0;
   out_564215406758229092[128] = 0;
   out_564215406758229092[129] = 0;
   out_564215406758229092[130] = 0;
   out_564215406758229092[131] = 0;
   out_564215406758229092[132] = 0;
   out_564215406758229092[133] = 1;
   out_564215406758229092[134] = 0;
   out_564215406758229092[135] = 0;
   out_564215406758229092[136] = 0;
   out_564215406758229092[137] = 0;
   out_564215406758229092[138] = 0;
   out_564215406758229092[139] = 0;
   out_564215406758229092[140] = 0;
   out_564215406758229092[141] = 0;
   out_564215406758229092[142] = 0;
   out_564215406758229092[143] = 0;
   out_564215406758229092[144] = 0;
   out_564215406758229092[145] = 0;
   out_564215406758229092[146] = 0;
   out_564215406758229092[147] = 0;
   out_564215406758229092[148] = 0;
   out_564215406758229092[149] = 0;
   out_564215406758229092[150] = 0;
   out_564215406758229092[151] = 0;
   out_564215406758229092[152] = 1;
   out_564215406758229092[153] = 0;
   out_564215406758229092[154] = 0;
   out_564215406758229092[155] = 0;
   out_564215406758229092[156] = 0;
   out_564215406758229092[157] = 0;
   out_564215406758229092[158] = 0;
   out_564215406758229092[159] = 0;
   out_564215406758229092[160] = 0;
   out_564215406758229092[161] = 0;
   out_564215406758229092[162] = 0;
   out_564215406758229092[163] = 0;
   out_564215406758229092[164] = 0;
   out_564215406758229092[165] = 0;
   out_564215406758229092[166] = 0;
   out_564215406758229092[167] = 0;
   out_564215406758229092[168] = 0;
   out_564215406758229092[169] = 0;
   out_564215406758229092[170] = 0;
   out_564215406758229092[171] = 1;
   out_564215406758229092[172] = 0;
   out_564215406758229092[173] = 0;
   out_564215406758229092[174] = 0;
   out_564215406758229092[175] = 0;
   out_564215406758229092[176] = 0;
   out_564215406758229092[177] = 0;
   out_564215406758229092[178] = 0;
   out_564215406758229092[179] = 0;
   out_564215406758229092[180] = 0;
   out_564215406758229092[181] = 0;
   out_564215406758229092[182] = 0;
   out_564215406758229092[183] = 0;
   out_564215406758229092[184] = 0;
   out_564215406758229092[185] = 0;
   out_564215406758229092[186] = 0;
   out_564215406758229092[187] = 0;
   out_564215406758229092[188] = 0;
   out_564215406758229092[189] = 0;
   out_564215406758229092[190] = 1;
   out_564215406758229092[191] = 0;
   out_564215406758229092[192] = 0;
   out_564215406758229092[193] = 0;
   out_564215406758229092[194] = 0;
   out_564215406758229092[195] = 0;
   out_564215406758229092[196] = 0;
   out_564215406758229092[197] = 0;
   out_564215406758229092[198] = 0;
   out_564215406758229092[199] = 0;
   out_564215406758229092[200] = 0;
   out_564215406758229092[201] = 0;
   out_564215406758229092[202] = 0;
   out_564215406758229092[203] = 0;
   out_564215406758229092[204] = 0;
   out_564215406758229092[205] = 0;
   out_564215406758229092[206] = 0;
   out_564215406758229092[207] = 0;
   out_564215406758229092[208] = 0;
   out_564215406758229092[209] = 1;
   out_564215406758229092[210] = 0;
   out_564215406758229092[211] = 0;
   out_564215406758229092[212] = 0;
   out_564215406758229092[213] = 0;
   out_564215406758229092[214] = 0;
   out_564215406758229092[215] = 0;
   out_564215406758229092[216] = 0;
   out_564215406758229092[217] = 0;
   out_564215406758229092[218] = 0;
   out_564215406758229092[219] = 0;
   out_564215406758229092[220] = 0;
   out_564215406758229092[221] = 0;
   out_564215406758229092[222] = 0;
   out_564215406758229092[223] = 0;
   out_564215406758229092[224] = 0;
   out_564215406758229092[225] = 0;
   out_564215406758229092[226] = 0;
   out_564215406758229092[227] = 0;
   out_564215406758229092[228] = 1;
   out_564215406758229092[229] = 0;
   out_564215406758229092[230] = 0;
   out_564215406758229092[231] = 0;
   out_564215406758229092[232] = 0;
   out_564215406758229092[233] = 0;
   out_564215406758229092[234] = 0;
   out_564215406758229092[235] = 0;
   out_564215406758229092[236] = 0;
   out_564215406758229092[237] = 0;
   out_564215406758229092[238] = 0;
   out_564215406758229092[239] = 0;
   out_564215406758229092[240] = 0;
   out_564215406758229092[241] = 0;
   out_564215406758229092[242] = 0;
   out_564215406758229092[243] = 0;
   out_564215406758229092[244] = 0;
   out_564215406758229092[245] = 0;
   out_564215406758229092[246] = 0;
   out_564215406758229092[247] = 1;
   out_564215406758229092[248] = 0;
   out_564215406758229092[249] = 0;
   out_564215406758229092[250] = 0;
   out_564215406758229092[251] = 0;
   out_564215406758229092[252] = 0;
   out_564215406758229092[253] = 0;
   out_564215406758229092[254] = 0;
   out_564215406758229092[255] = 0;
   out_564215406758229092[256] = 0;
   out_564215406758229092[257] = 0;
   out_564215406758229092[258] = 0;
   out_564215406758229092[259] = 0;
   out_564215406758229092[260] = 0;
   out_564215406758229092[261] = 0;
   out_564215406758229092[262] = 0;
   out_564215406758229092[263] = 0;
   out_564215406758229092[264] = 0;
   out_564215406758229092[265] = 0;
   out_564215406758229092[266] = 1;
   out_564215406758229092[267] = 0;
   out_564215406758229092[268] = 0;
   out_564215406758229092[269] = 0;
   out_564215406758229092[270] = 0;
   out_564215406758229092[271] = 0;
   out_564215406758229092[272] = 0;
   out_564215406758229092[273] = 0;
   out_564215406758229092[274] = 0;
   out_564215406758229092[275] = 0;
   out_564215406758229092[276] = 0;
   out_564215406758229092[277] = 0;
   out_564215406758229092[278] = 0;
   out_564215406758229092[279] = 0;
   out_564215406758229092[280] = 0;
   out_564215406758229092[281] = 0;
   out_564215406758229092[282] = 0;
   out_564215406758229092[283] = 0;
   out_564215406758229092[284] = 0;
   out_564215406758229092[285] = 1;
   out_564215406758229092[286] = 0;
   out_564215406758229092[287] = 0;
   out_564215406758229092[288] = 0;
   out_564215406758229092[289] = 0;
   out_564215406758229092[290] = 0;
   out_564215406758229092[291] = 0;
   out_564215406758229092[292] = 0;
   out_564215406758229092[293] = 0;
   out_564215406758229092[294] = 0;
   out_564215406758229092[295] = 0;
   out_564215406758229092[296] = 0;
   out_564215406758229092[297] = 0;
   out_564215406758229092[298] = 0;
   out_564215406758229092[299] = 0;
   out_564215406758229092[300] = 0;
   out_564215406758229092[301] = 0;
   out_564215406758229092[302] = 0;
   out_564215406758229092[303] = 0;
   out_564215406758229092[304] = 1;
   out_564215406758229092[305] = 0;
   out_564215406758229092[306] = 0;
   out_564215406758229092[307] = 0;
   out_564215406758229092[308] = 0;
   out_564215406758229092[309] = 0;
   out_564215406758229092[310] = 0;
   out_564215406758229092[311] = 0;
   out_564215406758229092[312] = 0;
   out_564215406758229092[313] = 0;
   out_564215406758229092[314] = 0;
   out_564215406758229092[315] = 0;
   out_564215406758229092[316] = 0;
   out_564215406758229092[317] = 0;
   out_564215406758229092[318] = 0;
   out_564215406758229092[319] = 0;
   out_564215406758229092[320] = 0;
   out_564215406758229092[321] = 0;
   out_564215406758229092[322] = 0;
   out_564215406758229092[323] = 1;
}
void h_4(double *state, double *unused, double *out_7331136994390451530) {
   out_7331136994390451530[0] = state[6] + state[9];
   out_7331136994390451530[1] = state[7] + state[10];
   out_7331136994390451530[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_3761220598869676892) {
   out_3761220598869676892[0] = 0;
   out_3761220598869676892[1] = 0;
   out_3761220598869676892[2] = 0;
   out_3761220598869676892[3] = 0;
   out_3761220598869676892[4] = 0;
   out_3761220598869676892[5] = 0;
   out_3761220598869676892[6] = 1;
   out_3761220598869676892[7] = 0;
   out_3761220598869676892[8] = 0;
   out_3761220598869676892[9] = 1;
   out_3761220598869676892[10] = 0;
   out_3761220598869676892[11] = 0;
   out_3761220598869676892[12] = 0;
   out_3761220598869676892[13] = 0;
   out_3761220598869676892[14] = 0;
   out_3761220598869676892[15] = 0;
   out_3761220598869676892[16] = 0;
   out_3761220598869676892[17] = 0;
   out_3761220598869676892[18] = 0;
   out_3761220598869676892[19] = 0;
   out_3761220598869676892[20] = 0;
   out_3761220598869676892[21] = 0;
   out_3761220598869676892[22] = 0;
   out_3761220598869676892[23] = 0;
   out_3761220598869676892[24] = 0;
   out_3761220598869676892[25] = 1;
   out_3761220598869676892[26] = 0;
   out_3761220598869676892[27] = 0;
   out_3761220598869676892[28] = 1;
   out_3761220598869676892[29] = 0;
   out_3761220598869676892[30] = 0;
   out_3761220598869676892[31] = 0;
   out_3761220598869676892[32] = 0;
   out_3761220598869676892[33] = 0;
   out_3761220598869676892[34] = 0;
   out_3761220598869676892[35] = 0;
   out_3761220598869676892[36] = 0;
   out_3761220598869676892[37] = 0;
   out_3761220598869676892[38] = 0;
   out_3761220598869676892[39] = 0;
   out_3761220598869676892[40] = 0;
   out_3761220598869676892[41] = 0;
   out_3761220598869676892[42] = 0;
   out_3761220598869676892[43] = 0;
   out_3761220598869676892[44] = 1;
   out_3761220598869676892[45] = 0;
   out_3761220598869676892[46] = 0;
   out_3761220598869676892[47] = 1;
   out_3761220598869676892[48] = 0;
   out_3761220598869676892[49] = 0;
   out_3761220598869676892[50] = 0;
   out_3761220598869676892[51] = 0;
   out_3761220598869676892[52] = 0;
   out_3761220598869676892[53] = 0;
}
void h_10(double *state, double *unused, double *out_6890323315298812884) {
   out_6890323315298812884[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_6890323315298812884[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_6890323315298812884[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_8621903665340213317) {
   out_8621903665340213317[0] = 0;
   out_8621903665340213317[1] = 9.8100000000000005*cos(state[1]);
   out_8621903665340213317[2] = 0;
   out_8621903665340213317[3] = 0;
   out_8621903665340213317[4] = -state[8];
   out_8621903665340213317[5] = state[7];
   out_8621903665340213317[6] = 0;
   out_8621903665340213317[7] = state[5];
   out_8621903665340213317[8] = -state[4];
   out_8621903665340213317[9] = 0;
   out_8621903665340213317[10] = 0;
   out_8621903665340213317[11] = 0;
   out_8621903665340213317[12] = 1;
   out_8621903665340213317[13] = 0;
   out_8621903665340213317[14] = 0;
   out_8621903665340213317[15] = 1;
   out_8621903665340213317[16] = 0;
   out_8621903665340213317[17] = 0;
   out_8621903665340213317[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_8621903665340213317[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_8621903665340213317[20] = 0;
   out_8621903665340213317[21] = state[8];
   out_8621903665340213317[22] = 0;
   out_8621903665340213317[23] = -state[6];
   out_8621903665340213317[24] = -state[5];
   out_8621903665340213317[25] = 0;
   out_8621903665340213317[26] = state[3];
   out_8621903665340213317[27] = 0;
   out_8621903665340213317[28] = 0;
   out_8621903665340213317[29] = 0;
   out_8621903665340213317[30] = 0;
   out_8621903665340213317[31] = 1;
   out_8621903665340213317[32] = 0;
   out_8621903665340213317[33] = 0;
   out_8621903665340213317[34] = 1;
   out_8621903665340213317[35] = 0;
   out_8621903665340213317[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_8621903665340213317[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_8621903665340213317[38] = 0;
   out_8621903665340213317[39] = -state[7];
   out_8621903665340213317[40] = state[6];
   out_8621903665340213317[41] = 0;
   out_8621903665340213317[42] = state[4];
   out_8621903665340213317[43] = -state[3];
   out_8621903665340213317[44] = 0;
   out_8621903665340213317[45] = 0;
   out_8621903665340213317[46] = 0;
   out_8621903665340213317[47] = 0;
   out_8621903665340213317[48] = 0;
   out_8621903665340213317[49] = 0;
   out_8621903665340213317[50] = 1;
   out_8621903665340213317[51] = 0;
   out_8621903665340213317[52] = 0;
   out_8621903665340213317[53] = 1;
}
void h_13(double *state, double *unused, double *out_3221209345999227064) {
   out_3221209345999227064[0] = state[3];
   out_3221209345999227064[1] = state[4];
   out_3221209345999227064[2] = state[5];
}
void H_13(double *state, double *unused, double *out_3849410609447024037) {
   out_3849410609447024037[0] = 0;
   out_3849410609447024037[1] = 0;
   out_3849410609447024037[2] = 0;
   out_3849410609447024037[3] = 1;
   out_3849410609447024037[4] = 0;
   out_3849410609447024037[5] = 0;
   out_3849410609447024037[6] = 0;
   out_3849410609447024037[7] = 0;
   out_3849410609447024037[8] = 0;
   out_3849410609447024037[9] = 0;
   out_3849410609447024037[10] = 0;
   out_3849410609447024037[11] = 0;
   out_3849410609447024037[12] = 0;
   out_3849410609447024037[13] = 0;
   out_3849410609447024037[14] = 0;
   out_3849410609447024037[15] = 0;
   out_3849410609447024037[16] = 0;
   out_3849410609447024037[17] = 0;
   out_3849410609447024037[18] = 0;
   out_3849410609447024037[19] = 0;
   out_3849410609447024037[20] = 0;
   out_3849410609447024037[21] = 0;
   out_3849410609447024037[22] = 1;
   out_3849410609447024037[23] = 0;
   out_3849410609447024037[24] = 0;
   out_3849410609447024037[25] = 0;
   out_3849410609447024037[26] = 0;
   out_3849410609447024037[27] = 0;
   out_3849410609447024037[28] = 0;
   out_3849410609447024037[29] = 0;
   out_3849410609447024037[30] = 0;
   out_3849410609447024037[31] = 0;
   out_3849410609447024037[32] = 0;
   out_3849410609447024037[33] = 0;
   out_3849410609447024037[34] = 0;
   out_3849410609447024037[35] = 0;
   out_3849410609447024037[36] = 0;
   out_3849410609447024037[37] = 0;
   out_3849410609447024037[38] = 0;
   out_3849410609447024037[39] = 0;
   out_3849410609447024037[40] = 0;
   out_3849410609447024037[41] = 1;
   out_3849410609447024037[42] = 0;
   out_3849410609447024037[43] = 0;
   out_3849410609447024037[44] = 0;
   out_3849410609447024037[45] = 0;
   out_3849410609447024037[46] = 0;
   out_3849410609447024037[47] = 0;
   out_3849410609447024037[48] = 0;
   out_3849410609447024037[49] = 0;
   out_3849410609447024037[50] = 0;
   out_3849410609447024037[51] = 0;
   out_3849410609447024037[52] = 0;
   out_3849410609447024037[53] = 0;
}
void h_14(double *state, double *unused, double *out_6812638219376417230) {
   out_6812638219376417230[0] = state[6];
   out_6812638219376417230[1] = state[7];
   out_6812638219376417230[2] = state[8];
}
void H_14(double *state, double *unused, double *out_202020257469807637) {
   out_202020257469807637[0] = 0;
   out_202020257469807637[1] = 0;
   out_202020257469807637[2] = 0;
   out_202020257469807637[3] = 0;
   out_202020257469807637[4] = 0;
   out_202020257469807637[5] = 0;
   out_202020257469807637[6] = 1;
   out_202020257469807637[7] = 0;
   out_202020257469807637[8] = 0;
   out_202020257469807637[9] = 0;
   out_202020257469807637[10] = 0;
   out_202020257469807637[11] = 0;
   out_202020257469807637[12] = 0;
   out_202020257469807637[13] = 0;
   out_202020257469807637[14] = 0;
   out_202020257469807637[15] = 0;
   out_202020257469807637[16] = 0;
   out_202020257469807637[17] = 0;
   out_202020257469807637[18] = 0;
   out_202020257469807637[19] = 0;
   out_202020257469807637[20] = 0;
   out_202020257469807637[21] = 0;
   out_202020257469807637[22] = 0;
   out_202020257469807637[23] = 0;
   out_202020257469807637[24] = 0;
   out_202020257469807637[25] = 1;
   out_202020257469807637[26] = 0;
   out_202020257469807637[27] = 0;
   out_202020257469807637[28] = 0;
   out_202020257469807637[29] = 0;
   out_202020257469807637[30] = 0;
   out_202020257469807637[31] = 0;
   out_202020257469807637[32] = 0;
   out_202020257469807637[33] = 0;
   out_202020257469807637[34] = 0;
   out_202020257469807637[35] = 0;
   out_202020257469807637[36] = 0;
   out_202020257469807637[37] = 0;
   out_202020257469807637[38] = 0;
   out_202020257469807637[39] = 0;
   out_202020257469807637[40] = 0;
   out_202020257469807637[41] = 0;
   out_202020257469807637[42] = 0;
   out_202020257469807637[43] = 0;
   out_202020257469807637[44] = 1;
   out_202020257469807637[45] = 0;
   out_202020257469807637[46] = 0;
   out_202020257469807637[47] = 0;
   out_202020257469807637[48] = 0;
   out_202020257469807637[49] = 0;
   out_202020257469807637[50] = 0;
   out_202020257469807637[51] = 0;
   out_202020257469807637[52] = 0;
   out_202020257469807637[53] = 0;
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
void pose_err_fun(double *nom_x, double *delta_x, double *out_3306664206309014289) {
  err_fun(nom_x, delta_x, out_3306664206309014289);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_570891515664221910) {
  inv_err_fun(nom_x, true_x, out_570891515664221910);
}
void pose_H_mod_fun(double *state, double *out_8375847635798993256) {
  H_mod_fun(state, out_8375847635798993256);
}
void pose_f_fun(double *state, double dt, double *out_8983403032593092745) {
  f_fun(state,  dt, out_8983403032593092745);
}
void pose_F_fun(double *state, double dt, double *out_564215406758229092) {
  F_fun(state,  dt, out_564215406758229092);
}
void pose_h_4(double *state, double *unused, double *out_7331136994390451530) {
  h_4(state, unused, out_7331136994390451530);
}
void pose_H_4(double *state, double *unused, double *out_3761220598869676892) {
  H_4(state, unused, out_3761220598869676892);
}
void pose_h_10(double *state, double *unused, double *out_6890323315298812884) {
  h_10(state, unused, out_6890323315298812884);
}
void pose_H_10(double *state, double *unused, double *out_8621903665340213317) {
  H_10(state, unused, out_8621903665340213317);
}
void pose_h_13(double *state, double *unused, double *out_3221209345999227064) {
  h_13(state, unused, out_3221209345999227064);
}
void pose_H_13(double *state, double *unused, double *out_3849410609447024037) {
  H_13(state, unused, out_3849410609447024037);
}
void pose_h_14(double *state, double *unused, double *out_6812638219376417230) {
  h_14(state, unused, out_6812638219376417230);
}
void pose_H_14(double *state, double *unused, double *out_202020257469807637) {
  H_14(state, unused, out_202020257469807637);
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
