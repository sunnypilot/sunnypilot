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
void err_fun(double *nom_x, double *delta_x, double *out_427463338731457644) {
   out_427463338731457644[0] = delta_x[0] + nom_x[0];
   out_427463338731457644[1] = delta_x[1] + nom_x[1];
   out_427463338731457644[2] = delta_x[2] + nom_x[2];
   out_427463338731457644[3] = delta_x[3] + nom_x[3];
   out_427463338731457644[4] = delta_x[4] + nom_x[4];
   out_427463338731457644[5] = delta_x[5] + nom_x[5];
   out_427463338731457644[6] = delta_x[6] + nom_x[6];
   out_427463338731457644[7] = delta_x[7] + nom_x[7];
   out_427463338731457644[8] = delta_x[8] + nom_x[8];
   out_427463338731457644[9] = delta_x[9] + nom_x[9];
   out_427463338731457644[10] = delta_x[10] + nom_x[10];
   out_427463338731457644[11] = delta_x[11] + nom_x[11];
   out_427463338731457644[12] = delta_x[12] + nom_x[12];
   out_427463338731457644[13] = delta_x[13] + nom_x[13];
   out_427463338731457644[14] = delta_x[14] + nom_x[14];
   out_427463338731457644[15] = delta_x[15] + nom_x[15];
   out_427463338731457644[16] = delta_x[16] + nom_x[16];
   out_427463338731457644[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_2896227888136381140) {
   out_2896227888136381140[0] = -nom_x[0] + true_x[0];
   out_2896227888136381140[1] = -nom_x[1] + true_x[1];
   out_2896227888136381140[2] = -nom_x[2] + true_x[2];
   out_2896227888136381140[3] = -nom_x[3] + true_x[3];
   out_2896227888136381140[4] = -nom_x[4] + true_x[4];
   out_2896227888136381140[5] = -nom_x[5] + true_x[5];
   out_2896227888136381140[6] = -nom_x[6] + true_x[6];
   out_2896227888136381140[7] = -nom_x[7] + true_x[7];
   out_2896227888136381140[8] = -nom_x[8] + true_x[8];
   out_2896227888136381140[9] = -nom_x[9] + true_x[9];
   out_2896227888136381140[10] = -nom_x[10] + true_x[10];
   out_2896227888136381140[11] = -nom_x[11] + true_x[11];
   out_2896227888136381140[12] = -nom_x[12] + true_x[12];
   out_2896227888136381140[13] = -nom_x[13] + true_x[13];
   out_2896227888136381140[14] = -nom_x[14] + true_x[14];
   out_2896227888136381140[15] = -nom_x[15] + true_x[15];
   out_2896227888136381140[16] = -nom_x[16] + true_x[16];
   out_2896227888136381140[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_2158205211507318632) {
   out_2158205211507318632[0] = 1.0;
   out_2158205211507318632[1] = 0.0;
   out_2158205211507318632[2] = 0.0;
   out_2158205211507318632[3] = 0.0;
   out_2158205211507318632[4] = 0.0;
   out_2158205211507318632[5] = 0.0;
   out_2158205211507318632[6] = 0.0;
   out_2158205211507318632[7] = 0.0;
   out_2158205211507318632[8] = 0.0;
   out_2158205211507318632[9] = 0.0;
   out_2158205211507318632[10] = 0.0;
   out_2158205211507318632[11] = 0.0;
   out_2158205211507318632[12] = 0.0;
   out_2158205211507318632[13] = 0.0;
   out_2158205211507318632[14] = 0.0;
   out_2158205211507318632[15] = 0.0;
   out_2158205211507318632[16] = 0.0;
   out_2158205211507318632[17] = 0.0;
   out_2158205211507318632[18] = 0.0;
   out_2158205211507318632[19] = 1.0;
   out_2158205211507318632[20] = 0.0;
   out_2158205211507318632[21] = 0.0;
   out_2158205211507318632[22] = 0.0;
   out_2158205211507318632[23] = 0.0;
   out_2158205211507318632[24] = 0.0;
   out_2158205211507318632[25] = 0.0;
   out_2158205211507318632[26] = 0.0;
   out_2158205211507318632[27] = 0.0;
   out_2158205211507318632[28] = 0.0;
   out_2158205211507318632[29] = 0.0;
   out_2158205211507318632[30] = 0.0;
   out_2158205211507318632[31] = 0.0;
   out_2158205211507318632[32] = 0.0;
   out_2158205211507318632[33] = 0.0;
   out_2158205211507318632[34] = 0.0;
   out_2158205211507318632[35] = 0.0;
   out_2158205211507318632[36] = 0.0;
   out_2158205211507318632[37] = 0.0;
   out_2158205211507318632[38] = 1.0;
   out_2158205211507318632[39] = 0.0;
   out_2158205211507318632[40] = 0.0;
   out_2158205211507318632[41] = 0.0;
   out_2158205211507318632[42] = 0.0;
   out_2158205211507318632[43] = 0.0;
   out_2158205211507318632[44] = 0.0;
   out_2158205211507318632[45] = 0.0;
   out_2158205211507318632[46] = 0.0;
   out_2158205211507318632[47] = 0.0;
   out_2158205211507318632[48] = 0.0;
   out_2158205211507318632[49] = 0.0;
   out_2158205211507318632[50] = 0.0;
   out_2158205211507318632[51] = 0.0;
   out_2158205211507318632[52] = 0.0;
   out_2158205211507318632[53] = 0.0;
   out_2158205211507318632[54] = 0.0;
   out_2158205211507318632[55] = 0.0;
   out_2158205211507318632[56] = 0.0;
   out_2158205211507318632[57] = 1.0;
   out_2158205211507318632[58] = 0.0;
   out_2158205211507318632[59] = 0.0;
   out_2158205211507318632[60] = 0.0;
   out_2158205211507318632[61] = 0.0;
   out_2158205211507318632[62] = 0.0;
   out_2158205211507318632[63] = 0.0;
   out_2158205211507318632[64] = 0.0;
   out_2158205211507318632[65] = 0.0;
   out_2158205211507318632[66] = 0.0;
   out_2158205211507318632[67] = 0.0;
   out_2158205211507318632[68] = 0.0;
   out_2158205211507318632[69] = 0.0;
   out_2158205211507318632[70] = 0.0;
   out_2158205211507318632[71] = 0.0;
   out_2158205211507318632[72] = 0.0;
   out_2158205211507318632[73] = 0.0;
   out_2158205211507318632[74] = 0.0;
   out_2158205211507318632[75] = 0.0;
   out_2158205211507318632[76] = 1.0;
   out_2158205211507318632[77] = 0.0;
   out_2158205211507318632[78] = 0.0;
   out_2158205211507318632[79] = 0.0;
   out_2158205211507318632[80] = 0.0;
   out_2158205211507318632[81] = 0.0;
   out_2158205211507318632[82] = 0.0;
   out_2158205211507318632[83] = 0.0;
   out_2158205211507318632[84] = 0.0;
   out_2158205211507318632[85] = 0.0;
   out_2158205211507318632[86] = 0.0;
   out_2158205211507318632[87] = 0.0;
   out_2158205211507318632[88] = 0.0;
   out_2158205211507318632[89] = 0.0;
   out_2158205211507318632[90] = 0.0;
   out_2158205211507318632[91] = 0.0;
   out_2158205211507318632[92] = 0.0;
   out_2158205211507318632[93] = 0.0;
   out_2158205211507318632[94] = 0.0;
   out_2158205211507318632[95] = 1.0;
   out_2158205211507318632[96] = 0.0;
   out_2158205211507318632[97] = 0.0;
   out_2158205211507318632[98] = 0.0;
   out_2158205211507318632[99] = 0.0;
   out_2158205211507318632[100] = 0.0;
   out_2158205211507318632[101] = 0.0;
   out_2158205211507318632[102] = 0.0;
   out_2158205211507318632[103] = 0.0;
   out_2158205211507318632[104] = 0.0;
   out_2158205211507318632[105] = 0.0;
   out_2158205211507318632[106] = 0.0;
   out_2158205211507318632[107] = 0.0;
   out_2158205211507318632[108] = 0.0;
   out_2158205211507318632[109] = 0.0;
   out_2158205211507318632[110] = 0.0;
   out_2158205211507318632[111] = 0.0;
   out_2158205211507318632[112] = 0.0;
   out_2158205211507318632[113] = 0.0;
   out_2158205211507318632[114] = 1.0;
   out_2158205211507318632[115] = 0.0;
   out_2158205211507318632[116] = 0.0;
   out_2158205211507318632[117] = 0.0;
   out_2158205211507318632[118] = 0.0;
   out_2158205211507318632[119] = 0.0;
   out_2158205211507318632[120] = 0.0;
   out_2158205211507318632[121] = 0.0;
   out_2158205211507318632[122] = 0.0;
   out_2158205211507318632[123] = 0.0;
   out_2158205211507318632[124] = 0.0;
   out_2158205211507318632[125] = 0.0;
   out_2158205211507318632[126] = 0.0;
   out_2158205211507318632[127] = 0.0;
   out_2158205211507318632[128] = 0.0;
   out_2158205211507318632[129] = 0.0;
   out_2158205211507318632[130] = 0.0;
   out_2158205211507318632[131] = 0.0;
   out_2158205211507318632[132] = 0.0;
   out_2158205211507318632[133] = 1.0;
   out_2158205211507318632[134] = 0.0;
   out_2158205211507318632[135] = 0.0;
   out_2158205211507318632[136] = 0.0;
   out_2158205211507318632[137] = 0.0;
   out_2158205211507318632[138] = 0.0;
   out_2158205211507318632[139] = 0.0;
   out_2158205211507318632[140] = 0.0;
   out_2158205211507318632[141] = 0.0;
   out_2158205211507318632[142] = 0.0;
   out_2158205211507318632[143] = 0.0;
   out_2158205211507318632[144] = 0.0;
   out_2158205211507318632[145] = 0.0;
   out_2158205211507318632[146] = 0.0;
   out_2158205211507318632[147] = 0.0;
   out_2158205211507318632[148] = 0.0;
   out_2158205211507318632[149] = 0.0;
   out_2158205211507318632[150] = 0.0;
   out_2158205211507318632[151] = 0.0;
   out_2158205211507318632[152] = 1.0;
   out_2158205211507318632[153] = 0.0;
   out_2158205211507318632[154] = 0.0;
   out_2158205211507318632[155] = 0.0;
   out_2158205211507318632[156] = 0.0;
   out_2158205211507318632[157] = 0.0;
   out_2158205211507318632[158] = 0.0;
   out_2158205211507318632[159] = 0.0;
   out_2158205211507318632[160] = 0.0;
   out_2158205211507318632[161] = 0.0;
   out_2158205211507318632[162] = 0.0;
   out_2158205211507318632[163] = 0.0;
   out_2158205211507318632[164] = 0.0;
   out_2158205211507318632[165] = 0.0;
   out_2158205211507318632[166] = 0.0;
   out_2158205211507318632[167] = 0.0;
   out_2158205211507318632[168] = 0.0;
   out_2158205211507318632[169] = 0.0;
   out_2158205211507318632[170] = 0.0;
   out_2158205211507318632[171] = 1.0;
   out_2158205211507318632[172] = 0.0;
   out_2158205211507318632[173] = 0.0;
   out_2158205211507318632[174] = 0.0;
   out_2158205211507318632[175] = 0.0;
   out_2158205211507318632[176] = 0.0;
   out_2158205211507318632[177] = 0.0;
   out_2158205211507318632[178] = 0.0;
   out_2158205211507318632[179] = 0.0;
   out_2158205211507318632[180] = 0.0;
   out_2158205211507318632[181] = 0.0;
   out_2158205211507318632[182] = 0.0;
   out_2158205211507318632[183] = 0.0;
   out_2158205211507318632[184] = 0.0;
   out_2158205211507318632[185] = 0.0;
   out_2158205211507318632[186] = 0.0;
   out_2158205211507318632[187] = 0.0;
   out_2158205211507318632[188] = 0.0;
   out_2158205211507318632[189] = 0.0;
   out_2158205211507318632[190] = 1.0;
   out_2158205211507318632[191] = 0.0;
   out_2158205211507318632[192] = 0.0;
   out_2158205211507318632[193] = 0.0;
   out_2158205211507318632[194] = 0.0;
   out_2158205211507318632[195] = 0.0;
   out_2158205211507318632[196] = 0.0;
   out_2158205211507318632[197] = 0.0;
   out_2158205211507318632[198] = 0.0;
   out_2158205211507318632[199] = 0.0;
   out_2158205211507318632[200] = 0.0;
   out_2158205211507318632[201] = 0.0;
   out_2158205211507318632[202] = 0.0;
   out_2158205211507318632[203] = 0.0;
   out_2158205211507318632[204] = 0.0;
   out_2158205211507318632[205] = 0.0;
   out_2158205211507318632[206] = 0.0;
   out_2158205211507318632[207] = 0.0;
   out_2158205211507318632[208] = 0.0;
   out_2158205211507318632[209] = 1.0;
   out_2158205211507318632[210] = 0.0;
   out_2158205211507318632[211] = 0.0;
   out_2158205211507318632[212] = 0.0;
   out_2158205211507318632[213] = 0.0;
   out_2158205211507318632[214] = 0.0;
   out_2158205211507318632[215] = 0.0;
   out_2158205211507318632[216] = 0.0;
   out_2158205211507318632[217] = 0.0;
   out_2158205211507318632[218] = 0.0;
   out_2158205211507318632[219] = 0.0;
   out_2158205211507318632[220] = 0.0;
   out_2158205211507318632[221] = 0.0;
   out_2158205211507318632[222] = 0.0;
   out_2158205211507318632[223] = 0.0;
   out_2158205211507318632[224] = 0.0;
   out_2158205211507318632[225] = 0.0;
   out_2158205211507318632[226] = 0.0;
   out_2158205211507318632[227] = 0.0;
   out_2158205211507318632[228] = 1.0;
   out_2158205211507318632[229] = 0.0;
   out_2158205211507318632[230] = 0.0;
   out_2158205211507318632[231] = 0.0;
   out_2158205211507318632[232] = 0.0;
   out_2158205211507318632[233] = 0.0;
   out_2158205211507318632[234] = 0.0;
   out_2158205211507318632[235] = 0.0;
   out_2158205211507318632[236] = 0.0;
   out_2158205211507318632[237] = 0.0;
   out_2158205211507318632[238] = 0.0;
   out_2158205211507318632[239] = 0.0;
   out_2158205211507318632[240] = 0.0;
   out_2158205211507318632[241] = 0.0;
   out_2158205211507318632[242] = 0.0;
   out_2158205211507318632[243] = 0.0;
   out_2158205211507318632[244] = 0.0;
   out_2158205211507318632[245] = 0.0;
   out_2158205211507318632[246] = 0.0;
   out_2158205211507318632[247] = 1.0;
   out_2158205211507318632[248] = 0.0;
   out_2158205211507318632[249] = 0.0;
   out_2158205211507318632[250] = 0.0;
   out_2158205211507318632[251] = 0.0;
   out_2158205211507318632[252] = 0.0;
   out_2158205211507318632[253] = 0.0;
   out_2158205211507318632[254] = 0.0;
   out_2158205211507318632[255] = 0.0;
   out_2158205211507318632[256] = 0.0;
   out_2158205211507318632[257] = 0.0;
   out_2158205211507318632[258] = 0.0;
   out_2158205211507318632[259] = 0.0;
   out_2158205211507318632[260] = 0.0;
   out_2158205211507318632[261] = 0.0;
   out_2158205211507318632[262] = 0.0;
   out_2158205211507318632[263] = 0.0;
   out_2158205211507318632[264] = 0.0;
   out_2158205211507318632[265] = 0.0;
   out_2158205211507318632[266] = 1.0;
   out_2158205211507318632[267] = 0.0;
   out_2158205211507318632[268] = 0.0;
   out_2158205211507318632[269] = 0.0;
   out_2158205211507318632[270] = 0.0;
   out_2158205211507318632[271] = 0.0;
   out_2158205211507318632[272] = 0.0;
   out_2158205211507318632[273] = 0.0;
   out_2158205211507318632[274] = 0.0;
   out_2158205211507318632[275] = 0.0;
   out_2158205211507318632[276] = 0.0;
   out_2158205211507318632[277] = 0.0;
   out_2158205211507318632[278] = 0.0;
   out_2158205211507318632[279] = 0.0;
   out_2158205211507318632[280] = 0.0;
   out_2158205211507318632[281] = 0.0;
   out_2158205211507318632[282] = 0.0;
   out_2158205211507318632[283] = 0.0;
   out_2158205211507318632[284] = 0.0;
   out_2158205211507318632[285] = 1.0;
   out_2158205211507318632[286] = 0.0;
   out_2158205211507318632[287] = 0.0;
   out_2158205211507318632[288] = 0.0;
   out_2158205211507318632[289] = 0.0;
   out_2158205211507318632[290] = 0.0;
   out_2158205211507318632[291] = 0.0;
   out_2158205211507318632[292] = 0.0;
   out_2158205211507318632[293] = 0.0;
   out_2158205211507318632[294] = 0.0;
   out_2158205211507318632[295] = 0.0;
   out_2158205211507318632[296] = 0.0;
   out_2158205211507318632[297] = 0.0;
   out_2158205211507318632[298] = 0.0;
   out_2158205211507318632[299] = 0.0;
   out_2158205211507318632[300] = 0.0;
   out_2158205211507318632[301] = 0.0;
   out_2158205211507318632[302] = 0.0;
   out_2158205211507318632[303] = 0.0;
   out_2158205211507318632[304] = 1.0;
   out_2158205211507318632[305] = 0.0;
   out_2158205211507318632[306] = 0.0;
   out_2158205211507318632[307] = 0.0;
   out_2158205211507318632[308] = 0.0;
   out_2158205211507318632[309] = 0.0;
   out_2158205211507318632[310] = 0.0;
   out_2158205211507318632[311] = 0.0;
   out_2158205211507318632[312] = 0.0;
   out_2158205211507318632[313] = 0.0;
   out_2158205211507318632[314] = 0.0;
   out_2158205211507318632[315] = 0.0;
   out_2158205211507318632[316] = 0.0;
   out_2158205211507318632[317] = 0.0;
   out_2158205211507318632[318] = 0.0;
   out_2158205211507318632[319] = 0.0;
   out_2158205211507318632[320] = 0.0;
   out_2158205211507318632[321] = 0.0;
   out_2158205211507318632[322] = 0.0;
   out_2158205211507318632[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_1184498683811889789) {
   out_1184498683811889789[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_1184498683811889789[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_1184498683811889789[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_1184498683811889789[3] = dt*state[12] + state[3];
   out_1184498683811889789[4] = dt*state[13] + state[4];
   out_1184498683811889789[5] = dt*state[14] + state[5];
   out_1184498683811889789[6] = state[6];
   out_1184498683811889789[7] = state[7];
   out_1184498683811889789[8] = state[8];
   out_1184498683811889789[9] = state[9];
   out_1184498683811889789[10] = state[10];
   out_1184498683811889789[11] = state[11];
   out_1184498683811889789[12] = state[12];
   out_1184498683811889789[13] = state[13];
   out_1184498683811889789[14] = state[14];
   out_1184498683811889789[15] = state[15];
   out_1184498683811889789[16] = state[16];
   out_1184498683811889789[17] = state[17];
}
void F_fun(double *state, double dt, double *out_3361969816109204330) {
   out_3361969816109204330[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_3361969816109204330[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_3361969816109204330[2] = 0;
   out_3361969816109204330[3] = 0;
   out_3361969816109204330[4] = 0;
   out_3361969816109204330[5] = 0;
   out_3361969816109204330[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_3361969816109204330[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_3361969816109204330[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_3361969816109204330[9] = 0;
   out_3361969816109204330[10] = 0;
   out_3361969816109204330[11] = 0;
   out_3361969816109204330[12] = 0;
   out_3361969816109204330[13] = 0;
   out_3361969816109204330[14] = 0;
   out_3361969816109204330[15] = 0;
   out_3361969816109204330[16] = 0;
   out_3361969816109204330[17] = 0;
   out_3361969816109204330[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_3361969816109204330[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_3361969816109204330[20] = 0;
   out_3361969816109204330[21] = 0;
   out_3361969816109204330[22] = 0;
   out_3361969816109204330[23] = 0;
   out_3361969816109204330[24] = 0;
   out_3361969816109204330[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_3361969816109204330[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_3361969816109204330[27] = 0;
   out_3361969816109204330[28] = 0;
   out_3361969816109204330[29] = 0;
   out_3361969816109204330[30] = 0;
   out_3361969816109204330[31] = 0;
   out_3361969816109204330[32] = 0;
   out_3361969816109204330[33] = 0;
   out_3361969816109204330[34] = 0;
   out_3361969816109204330[35] = 0;
   out_3361969816109204330[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_3361969816109204330[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_3361969816109204330[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_3361969816109204330[39] = 0;
   out_3361969816109204330[40] = 0;
   out_3361969816109204330[41] = 0;
   out_3361969816109204330[42] = 0;
   out_3361969816109204330[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_3361969816109204330[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_3361969816109204330[45] = 0;
   out_3361969816109204330[46] = 0;
   out_3361969816109204330[47] = 0;
   out_3361969816109204330[48] = 0;
   out_3361969816109204330[49] = 0;
   out_3361969816109204330[50] = 0;
   out_3361969816109204330[51] = 0;
   out_3361969816109204330[52] = 0;
   out_3361969816109204330[53] = 0;
   out_3361969816109204330[54] = 0;
   out_3361969816109204330[55] = 0;
   out_3361969816109204330[56] = 0;
   out_3361969816109204330[57] = 1;
   out_3361969816109204330[58] = 0;
   out_3361969816109204330[59] = 0;
   out_3361969816109204330[60] = 0;
   out_3361969816109204330[61] = 0;
   out_3361969816109204330[62] = 0;
   out_3361969816109204330[63] = 0;
   out_3361969816109204330[64] = 0;
   out_3361969816109204330[65] = 0;
   out_3361969816109204330[66] = dt;
   out_3361969816109204330[67] = 0;
   out_3361969816109204330[68] = 0;
   out_3361969816109204330[69] = 0;
   out_3361969816109204330[70] = 0;
   out_3361969816109204330[71] = 0;
   out_3361969816109204330[72] = 0;
   out_3361969816109204330[73] = 0;
   out_3361969816109204330[74] = 0;
   out_3361969816109204330[75] = 0;
   out_3361969816109204330[76] = 1;
   out_3361969816109204330[77] = 0;
   out_3361969816109204330[78] = 0;
   out_3361969816109204330[79] = 0;
   out_3361969816109204330[80] = 0;
   out_3361969816109204330[81] = 0;
   out_3361969816109204330[82] = 0;
   out_3361969816109204330[83] = 0;
   out_3361969816109204330[84] = 0;
   out_3361969816109204330[85] = dt;
   out_3361969816109204330[86] = 0;
   out_3361969816109204330[87] = 0;
   out_3361969816109204330[88] = 0;
   out_3361969816109204330[89] = 0;
   out_3361969816109204330[90] = 0;
   out_3361969816109204330[91] = 0;
   out_3361969816109204330[92] = 0;
   out_3361969816109204330[93] = 0;
   out_3361969816109204330[94] = 0;
   out_3361969816109204330[95] = 1;
   out_3361969816109204330[96] = 0;
   out_3361969816109204330[97] = 0;
   out_3361969816109204330[98] = 0;
   out_3361969816109204330[99] = 0;
   out_3361969816109204330[100] = 0;
   out_3361969816109204330[101] = 0;
   out_3361969816109204330[102] = 0;
   out_3361969816109204330[103] = 0;
   out_3361969816109204330[104] = dt;
   out_3361969816109204330[105] = 0;
   out_3361969816109204330[106] = 0;
   out_3361969816109204330[107] = 0;
   out_3361969816109204330[108] = 0;
   out_3361969816109204330[109] = 0;
   out_3361969816109204330[110] = 0;
   out_3361969816109204330[111] = 0;
   out_3361969816109204330[112] = 0;
   out_3361969816109204330[113] = 0;
   out_3361969816109204330[114] = 1;
   out_3361969816109204330[115] = 0;
   out_3361969816109204330[116] = 0;
   out_3361969816109204330[117] = 0;
   out_3361969816109204330[118] = 0;
   out_3361969816109204330[119] = 0;
   out_3361969816109204330[120] = 0;
   out_3361969816109204330[121] = 0;
   out_3361969816109204330[122] = 0;
   out_3361969816109204330[123] = 0;
   out_3361969816109204330[124] = 0;
   out_3361969816109204330[125] = 0;
   out_3361969816109204330[126] = 0;
   out_3361969816109204330[127] = 0;
   out_3361969816109204330[128] = 0;
   out_3361969816109204330[129] = 0;
   out_3361969816109204330[130] = 0;
   out_3361969816109204330[131] = 0;
   out_3361969816109204330[132] = 0;
   out_3361969816109204330[133] = 1;
   out_3361969816109204330[134] = 0;
   out_3361969816109204330[135] = 0;
   out_3361969816109204330[136] = 0;
   out_3361969816109204330[137] = 0;
   out_3361969816109204330[138] = 0;
   out_3361969816109204330[139] = 0;
   out_3361969816109204330[140] = 0;
   out_3361969816109204330[141] = 0;
   out_3361969816109204330[142] = 0;
   out_3361969816109204330[143] = 0;
   out_3361969816109204330[144] = 0;
   out_3361969816109204330[145] = 0;
   out_3361969816109204330[146] = 0;
   out_3361969816109204330[147] = 0;
   out_3361969816109204330[148] = 0;
   out_3361969816109204330[149] = 0;
   out_3361969816109204330[150] = 0;
   out_3361969816109204330[151] = 0;
   out_3361969816109204330[152] = 1;
   out_3361969816109204330[153] = 0;
   out_3361969816109204330[154] = 0;
   out_3361969816109204330[155] = 0;
   out_3361969816109204330[156] = 0;
   out_3361969816109204330[157] = 0;
   out_3361969816109204330[158] = 0;
   out_3361969816109204330[159] = 0;
   out_3361969816109204330[160] = 0;
   out_3361969816109204330[161] = 0;
   out_3361969816109204330[162] = 0;
   out_3361969816109204330[163] = 0;
   out_3361969816109204330[164] = 0;
   out_3361969816109204330[165] = 0;
   out_3361969816109204330[166] = 0;
   out_3361969816109204330[167] = 0;
   out_3361969816109204330[168] = 0;
   out_3361969816109204330[169] = 0;
   out_3361969816109204330[170] = 0;
   out_3361969816109204330[171] = 1;
   out_3361969816109204330[172] = 0;
   out_3361969816109204330[173] = 0;
   out_3361969816109204330[174] = 0;
   out_3361969816109204330[175] = 0;
   out_3361969816109204330[176] = 0;
   out_3361969816109204330[177] = 0;
   out_3361969816109204330[178] = 0;
   out_3361969816109204330[179] = 0;
   out_3361969816109204330[180] = 0;
   out_3361969816109204330[181] = 0;
   out_3361969816109204330[182] = 0;
   out_3361969816109204330[183] = 0;
   out_3361969816109204330[184] = 0;
   out_3361969816109204330[185] = 0;
   out_3361969816109204330[186] = 0;
   out_3361969816109204330[187] = 0;
   out_3361969816109204330[188] = 0;
   out_3361969816109204330[189] = 0;
   out_3361969816109204330[190] = 1;
   out_3361969816109204330[191] = 0;
   out_3361969816109204330[192] = 0;
   out_3361969816109204330[193] = 0;
   out_3361969816109204330[194] = 0;
   out_3361969816109204330[195] = 0;
   out_3361969816109204330[196] = 0;
   out_3361969816109204330[197] = 0;
   out_3361969816109204330[198] = 0;
   out_3361969816109204330[199] = 0;
   out_3361969816109204330[200] = 0;
   out_3361969816109204330[201] = 0;
   out_3361969816109204330[202] = 0;
   out_3361969816109204330[203] = 0;
   out_3361969816109204330[204] = 0;
   out_3361969816109204330[205] = 0;
   out_3361969816109204330[206] = 0;
   out_3361969816109204330[207] = 0;
   out_3361969816109204330[208] = 0;
   out_3361969816109204330[209] = 1;
   out_3361969816109204330[210] = 0;
   out_3361969816109204330[211] = 0;
   out_3361969816109204330[212] = 0;
   out_3361969816109204330[213] = 0;
   out_3361969816109204330[214] = 0;
   out_3361969816109204330[215] = 0;
   out_3361969816109204330[216] = 0;
   out_3361969816109204330[217] = 0;
   out_3361969816109204330[218] = 0;
   out_3361969816109204330[219] = 0;
   out_3361969816109204330[220] = 0;
   out_3361969816109204330[221] = 0;
   out_3361969816109204330[222] = 0;
   out_3361969816109204330[223] = 0;
   out_3361969816109204330[224] = 0;
   out_3361969816109204330[225] = 0;
   out_3361969816109204330[226] = 0;
   out_3361969816109204330[227] = 0;
   out_3361969816109204330[228] = 1;
   out_3361969816109204330[229] = 0;
   out_3361969816109204330[230] = 0;
   out_3361969816109204330[231] = 0;
   out_3361969816109204330[232] = 0;
   out_3361969816109204330[233] = 0;
   out_3361969816109204330[234] = 0;
   out_3361969816109204330[235] = 0;
   out_3361969816109204330[236] = 0;
   out_3361969816109204330[237] = 0;
   out_3361969816109204330[238] = 0;
   out_3361969816109204330[239] = 0;
   out_3361969816109204330[240] = 0;
   out_3361969816109204330[241] = 0;
   out_3361969816109204330[242] = 0;
   out_3361969816109204330[243] = 0;
   out_3361969816109204330[244] = 0;
   out_3361969816109204330[245] = 0;
   out_3361969816109204330[246] = 0;
   out_3361969816109204330[247] = 1;
   out_3361969816109204330[248] = 0;
   out_3361969816109204330[249] = 0;
   out_3361969816109204330[250] = 0;
   out_3361969816109204330[251] = 0;
   out_3361969816109204330[252] = 0;
   out_3361969816109204330[253] = 0;
   out_3361969816109204330[254] = 0;
   out_3361969816109204330[255] = 0;
   out_3361969816109204330[256] = 0;
   out_3361969816109204330[257] = 0;
   out_3361969816109204330[258] = 0;
   out_3361969816109204330[259] = 0;
   out_3361969816109204330[260] = 0;
   out_3361969816109204330[261] = 0;
   out_3361969816109204330[262] = 0;
   out_3361969816109204330[263] = 0;
   out_3361969816109204330[264] = 0;
   out_3361969816109204330[265] = 0;
   out_3361969816109204330[266] = 1;
   out_3361969816109204330[267] = 0;
   out_3361969816109204330[268] = 0;
   out_3361969816109204330[269] = 0;
   out_3361969816109204330[270] = 0;
   out_3361969816109204330[271] = 0;
   out_3361969816109204330[272] = 0;
   out_3361969816109204330[273] = 0;
   out_3361969816109204330[274] = 0;
   out_3361969816109204330[275] = 0;
   out_3361969816109204330[276] = 0;
   out_3361969816109204330[277] = 0;
   out_3361969816109204330[278] = 0;
   out_3361969816109204330[279] = 0;
   out_3361969816109204330[280] = 0;
   out_3361969816109204330[281] = 0;
   out_3361969816109204330[282] = 0;
   out_3361969816109204330[283] = 0;
   out_3361969816109204330[284] = 0;
   out_3361969816109204330[285] = 1;
   out_3361969816109204330[286] = 0;
   out_3361969816109204330[287] = 0;
   out_3361969816109204330[288] = 0;
   out_3361969816109204330[289] = 0;
   out_3361969816109204330[290] = 0;
   out_3361969816109204330[291] = 0;
   out_3361969816109204330[292] = 0;
   out_3361969816109204330[293] = 0;
   out_3361969816109204330[294] = 0;
   out_3361969816109204330[295] = 0;
   out_3361969816109204330[296] = 0;
   out_3361969816109204330[297] = 0;
   out_3361969816109204330[298] = 0;
   out_3361969816109204330[299] = 0;
   out_3361969816109204330[300] = 0;
   out_3361969816109204330[301] = 0;
   out_3361969816109204330[302] = 0;
   out_3361969816109204330[303] = 0;
   out_3361969816109204330[304] = 1;
   out_3361969816109204330[305] = 0;
   out_3361969816109204330[306] = 0;
   out_3361969816109204330[307] = 0;
   out_3361969816109204330[308] = 0;
   out_3361969816109204330[309] = 0;
   out_3361969816109204330[310] = 0;
   out_3361969816109204330[311] = 0;
   out_3361969816109204330[312] = 0;
   out_3361969816109204330[313] = 0;
   out_3361969816109204330[314] = 0;
   out_3361969816109204330[315] = 0;
   out_3361969816109204330[316] = 0;
   out_3361969816109204330[317] = 0;
   out_3361969816109204330[318] = 0;
   out_3361969816109204330[319] = 0;
   out_3361969816109204330[320] = 0;
   out_3361969816109204330[321] = 0;
   out_3361969816109204330[322] = 0;
   out_3361969816109204330[323] = 1;
}
void h_4(double *state, double *unused, double *out_4817713328626282849) {
   out_4817713328626282849[0] = state[6] + state[9];
   out_4817713328626282849[1] = state[7] + state[10];
   out_4817713328626282849[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_2912366213562031239) {
   out_2912366213562031239[0] = 0;
   out_2912366213562031239[1] = 0;
   out_2912366213562031239[2] = 0;
   out_2912366213562031239[3] = 0;
   out_2912366213562031239[4] = 0;
   out_2912366213562031239[5] = 0;
   out_2912366213562031239[6] = 1;
   out_2912366213562031239[7] = 0;
   out_2912366213562031239[8] = 0;
   out_2912366213562031239[9] = 1;
   out_2912366213562031239[10] = 0;
   out_2912366213562031239[11] = 0;
   out_2912366213562031239[12] = 0;
   out_2912366213562031239[13] = 0;
   out_2912366213562031239[14] = 0;
   out_2912366213562031239[15] = 0;
   out_2912366213562031239[16] = 0;
   out_2912366213562031239[17] = 0;
   out_2912366213562031239[18] = 0;
   out_2912366213562031239[19] = 0;
   out_2912366213562031239[20] = 0;
   out_2912366213562031239[21] = 0;
   out_2912366213562031239[22] = 0;
   out_2912366213562031239[23] = 0;
   out_2912366213562031239[24] = 0;
   out_2912366213562031239[25] = 1;
   out_2912366213562031239[26] = 0;
   out_2912366213562031239[27] = 0;
   out_2912366213562031239[28] = 1;
   out_2912366213562031239[29] = 0;
   out_2912366213562031239[30] = 0;
   out_2912366213562031239[31] = 0;
   out_2912366213562031239[32] = 0;
   out_2912366213562031239[33] = 0;
   out_2912366213562031239[34] = 0;
   out_2912366213562031239[35] = 0;
   out_2912366213562031239[36] = 0;
   out_2912366213562031239[37] = 0;
   out_2912366213562031239[38] = 0;
   out_2912366213562031239[39] = 0;
   out_2912366213562031239[40] = 0;
   out_2912366213562031239[41] = 0;
   out_2912366213562031239[42] = 0;
   out_2912366213562031239[43] = 0;
   out_2912366213562031239[44] = 1;
   out_2912366213562031239[45] = 0;
   out_2912366213562031239[46] = 0;
   out_2912366213562031239[47] = 1;
   out_2912366213562031239[48] = 0;
   out_2912366213562031239[49] = 0;
   out_2912366213562031239[50] = 0;
   out_2912366213562031239[51] = 0;
   out_2912366213562031239[52] = 0;
   out_2912366213562031239[53] = 0;
}
void h_10(double *state, double *unused, double *out_8260153212022429064) {
   out_8260153212022429064[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_8260153212022429064[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_8260153212022429064[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_3272792128311919869) {
   out_3272792128311919869[0] = 0;
   out_3272792128311919869[1] = 9.8100000000000005*cos(state[1]);
   out_3272792128311919869[2] = 0;
   out_3272792128311919869[3] = 0;
   out_3272792128311919869[4] = -state[8];
   out_3272792128311919869[5] = state[7];
   out_3272792128311919869[6] = 0;
   out_3272792128311919869[7] = state[5];
   out_3272792128311919869[8] = -state[4];
   out_3272792128311919869[9] = 0;
   out_3272792128311919869[10] = 0;
   out_3272792128311919869[11] = 0;
   out_3272792128311919869[12] = 1;
   out_3272792128311919869[13] = 0;
   out_3272792128311919869[14] = 0;
   out_3272792128311919869[15] = 1;
   out_3272792128311919869[16] = 0;
   out_3272792128311919869[17] = 0;
   out_3272792128311919869[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_3272792128311919869[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_3272792128311919869[20] = 0;
   out_3272792128311919869[21] = state[8];
   out_3272792128311919869[22] = 0;
   out_3272792128311919869[23] = -state[6];
   out_3272792128311919869[24] = -state[5];
   out_3272792128311919869[25] = 0;
   out_3272792128311919869[26] = state[3];
   out_3272792128311919869[27] = 0;
   out_3272792128311919869[28] = 0;
   out_3272792128311919869[29] = 0;
   out_3272792128311919869[30] = 0;
   out_3272792128311919869[31] = 1;
   out_3272792128311919869[32] = 0;
   out_3272792128311919869[33] = 0;
   out_3272792128311919869[34] = 1;
   out_3272792128311919869[35] = 0;
   out_3272792128311919869[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_3272792128311919869[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_3272792128311919869[38] = 0;
   out_3272792128311919869[39] = -state[7];
   out_3272792128311919869[40] = state[6];
   out_3272792128311919869[41] = 0;
   out_3272792128311919869[42] = state[4];
   out_3272792128311919869[43] = -state[3];
   out_3272792128311919869[44] = 0;
   out_3272792128311919869[45] = 0;
   out_3272792128311919869[46] = 0;
   out_3272792128311919869[47] = 0;
   out_3272792128311919869[48] = 0;
   out_3272792128311919869[49] = 0;
   out_3272792128311919869[50] = 1;
   out_3272792128311919869[51] = 0;
   out_3272792128311919869[52] = 0;
   out_3272792128311919869[53] = 1;
}
void h_13(double *state, double *unused, double *out_972726228359974118) {
   out_972726228359974118[0] = state[3];
   out_972726228359974118[1] = state[4];
   out_972726228359974118[2] = state[5];
}
void H_13(double *state, double *unused, double *out_7923746651830819448) {
   out_7923746651830819448[0] = 0;
   out_7923746651830819448[1] = 0;
   out_7923746651830819448[2] = 0;
   out_7923746651830819448[3] = 1;
   out_7923746651830819448[4] = 0;
   out_7923746651830819448[5] = 0;
   out_7923746651830819448[6] = 0;
   out_7923746651830819448[7] = 0;
   out_7923746651830819448[8] = 0;
   out_7923746651830819448[9] = 0;
   out_7923746651830819448[10] = 0;
   out_7923746651830819448[11] = 0;
   out_7923746651830819448[12] = 0;
   out_7923746651830819448[13] = 0;
   out_7923746651830819448[14] = 0;
   out_7923746651830819448[15] = 0;
   out_7923746651830819448[16] = 0;
   out_7923746651830819448[17] = 0;
   out_7923746651830819448[18] = 0;
   out_7923746651830819448[19] = 0;
   out_7923746651830819448[20] = 0;
   out_7923746651830819448[21] = 0;
   out_7923746651830819448[22] = 1;
   out_7923746651830819448[23] = 0;
   out_7923746651830819448[24] = 0;
   out_7923746651830819448[25] = 0;
   out_7923746651830819448[26] = 0;
   out_7923746651830819448[27] = 0;
   out_7923746651830819448[28] = 0;
   out_7923746651830819448[29] = 0;
   out_7923746651830819448[30] = 0;
   out_7923746651830819448[31] = 0;
   out_7923746651830819448[32] = 0;
   out_7923746651830819448[33] = 0;
   out_7923746651830819448[34] = 0;
   out_7923746651830819448[35] = 0;
   out_7923746651830819448[36] = 0;
   out_7923746651830819448[37] = 0;
   out_7923746651830819448[38] = 0;
   out_7923746651830819448[39] = 0;
   out_7923746651830819448[40] = 0;
   out_7923746651830819448[41] = 1;
   out_7923746651830819448[42] = 0;
   out_7923746651830819448[43] = 0;
   out_7923746651830819448[44] = 0;
   out_7923746651830819448[45] = 0;
   out_7923746651830819448[46] = 0;
   out_7923746651830819448[47] = 0;
   out_7923746651830819448[48] = 0;
   out_7923746651830819448[49] = 0;
   out_7923746651830819448[50] = 0;
   out_7923746651830819448[51] = 0;
   out_7923746651830819448[52] = 0;
   out_7923746651830819448[53] = 0;
}
void h_14(double *state, double *unused, double *out_6022082422796717247) {
   out_6022082422796717247[0] = state[6];
   out_6022082422796717247[1] = state[7];
   out_6022082422796717247[2] = state[8];
}
void H_14(double *state, double *unused, double *out_6875607069901515768) {
   out_6875607069901515768[0] = 0;
   out_6875607069901515768[1] = 0;
   out_6875607069901515768[2] = 0;
   out_6875607069901515768[3] = 0;
   out_6875607069901515768[4] = 0;
   out_6875607069901515768[5] = 0;
   out_6875607069901515768[6] = 1;
   out_6875607069901515768[7] = 0;
   out_6875607069901515768[8] = 0;
   out_6875607069901515768[9] = 0;
   out_6875607069901515768[10] = 0;
   out_6875607069901515768[11] = 0;
   out_6875607069901515768[12] = 0;
   out_6875607069901515768[13] = 0;
   out_6875607069901515768[14] = 0;
   out_6875607069901515768[15] = 0;
   out_6875607069901515768[16] = 0;
   out_6875607069901515768[17] = 0;
   out_6875607069901515768[18] = 0;
   out_6875607069901515768[19] = 0;
   out_6875607069901515768[20] = 0;
   out_6875607069901515768[21] = 0;
   out_6875607069901515768[22] = 0;
   out_6875607069901515768[23] = 0;
   out_6875607069901515768[24] = 0;
   out_6875607069901515768[25] = 1;
   out_6875607069901515768[26] = 0;
   out_6875607069901515768[27] = 0;
   out_6875607069901515768[28] = 0;
   out_6875607069901515768[29] = 0;
   out_6875607069901515768[30] = 0;
   out_6875607069901515768[31] = 0;
   out_6875607069901515768[32] = 0;
   out_6875607069901515768[33] = 0;
   out_6875607069901515768[34] = 0;
   out_6875607069901515768[35] = 0;
   out_6875607069901515768[36] = 0;
   out_6875607069901515768[37] = 0;
   out_6875607069901515768[38] = 0;
   out_6875607069901515768[39] = 0;
   out_6875607069901515768[40] = 0;
   out_6875607069901515768[41] = 0;
   out_6875607069901515768[42] = 0;
   out_6875607069901515768[43] = 0;
   out_6875607069901515768[44] = 1;
   out_6875607069901515768[45] = 0;
   out_6875607069901515768[46] = 0;
   out_6875607069901515768[47] = 0;
   out_6875607069901515768[48] = 0;
   out_6875607069901515768[49] = 0;
   out_6875607069901515768[50] = 0;
   out_6875607069901515768[51] = 0;
   out_6875607069901515768[52] = 0;
   out_6875607069901515768[53] = 0;
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
void pose_err_fun(double *nom_x, double *delta_x, double *out_427463338731457644) {
  err_fun(nom_x, delta_x, out_427463338731457644);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_2896227888136381140) {
  inv_err_fun(nom_x, true_x, out_2896227888136381140);
}
void pose_H_mod_fun(double *state, double *out_2158205211507318632) {
  H_mod_fun(state, out_2158205211507318632);
}
void pose_f_fun(double *state, double dt, double *out_1184498683811889789) {
  f_fun(state,  dt, out_1184498683811889789);
}
void pose_F_fun(double *state, double dt, double *out_3361969816109204330) {
  F_fun(state,  dt, out_3361969816109204330);
}
void pose_h_4(double *state, double *unused, double *out_4817713328626282849) {
  h_4(state, unused, out_4817713328626282849);
}
void pose_H_4(double *state, double *unused, double *out_2912366213562031239) {
  H_4(state, unused, out_2912366213562031239);
}
void pose_h_10(double *state, double *unused, double *out_8260153212022429064) {
  h_10(state, unused, out_8260153212022429064);
}
void pose_H_10(double *state, double *unused, double *out_3272792128311919869) {
  H_10(state, unused, out_3272792128311919869);
}
void pose_h_13(double *state, double *unused, double *out_972726228359974118) {
  h_13(state, unused, out_972726228359974118);
}
void pose_H_13(double *state, double *unused, double *out_7923746651830819448) {
  H_13(state, unused, out_7923746651830819448);
}
void pose_h_14(double *state, double *unused, double *out_6022082422796717247) {
  h_14(state, unused, out_6022082422796717247);
}
void pose_H_14(double *state, double *unused, double *out_6875607069901515768) {
  H_14(state, unused, out_6875607069901515768);
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
