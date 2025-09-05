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
void err_fun(double *nom_x, double *delta_x, double *out_5712645316975978292) {
   out_5712645316975978292[0] = delta_x[0] + nom_x[0];
   out_5712645316975978292[1] = delta_x[1] + nom_x[1];
   out_5712645316975978292[2] = delta_x[2] + nom_x[2];
   out_5712645316975978292[3] = delta_x[3] + nom_x[3];
   out_5712645316975978292[4] = delta_x[4] + nom_x[4];
   out_5712645316975978292[5] = delta_x[5] + nom_x[5];
   out_5712645316975978292[6] = delta_x[6] + nom_x[6];
   out_5712645316975978292[7] = delta_x[7] + nom_x[7];
   out_5712645316975978292[8] = delta_x[8] + nom_x[8];
   out_5712645316975978292[9] = delta_x[9] + nom_x[9];
   out_5712645316975978292[10] = delta_x[10] + nom_x[10];
   out_5712645316975978292[11] = delta_x[11] + nom_x[11];
   out_5712645316975978292[12] = delta_x[12] + nom_x[12];
   out_5712645316975978292[13] = delta_x[13] + nom_x[13];
   out_5712645316975978292[14] = delta_x[14] + nom_x[14];
   out_5712645316975978292[15] = delta_x[15] + nom_x[15];
   out_5712645316975978292[16] = delta_x[16] + nom_x[16];
   out_5712645316975978292[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_2375481713030026782) {
   out_2375481713030026782[0] = -nom_x[0] + true_x[0];
   out_2375481713030026782[1] = -nom_x[1] + true_x[1];
   out_2375481713030026782[2] = -nom_x[2] + true_x[2];
   out_2375481713030026782[3] = -nom_x[3] + true_x[3];
   out_2375481713030026782[4] = -nom_x[4] + true_x[4];
   out_2375481713030026782[5] = -nom_x[5] + true_x[5];
   out_2375481713030026782[6] = -nom_x[6] + true_x[6];
   out_2375481713030026782[7] = -nom_x[7] + true_x[7];
   out_2375481713030026782[8] = -nom_x[8] + true_x[8];
   out_2375481713030026782[9] = -nom_x[9] + true_x[9];
   out_2375481713030026782[10] = -nom_x[10] + true_x[10];
   out_2375481713030026782[11] = -nom_x[11] + true_x[11];
   out_2375481713030026782[12] = -nom_x[12] + true_x[12];
   out_2375481713030026782[13] = -nom_x[13] + true_x[13];
   out_2375481713030026782[14] = -nom_x[14] + true_x[14];
   out_2375481713030026782[15] = -nom_x[15] + true_x[15];
   out_2375481713030026782[16] = -nom_x[16] + true_x[16];
   out_2375481713030026782[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_9187572088722537132) {
   out_9187572088722537132[0] = 1.0;
   out_9187572088722537132[1] = 0.0;
   out_9187572088722537132[2] = 0.0;
   out_9187572088722537132[3] = 0.0;
   out_9187572088722537132[4] = 0.0;
   out_9187572088722537132[5] = 0.0;
   out_9187572088722537132[6] = 0.0;
   out_9187572088722537132[7] = 0.0;
   out_9187572088722537132[8] = 0.0;
   out_9187572088722537132[9] = 0.0;
   out_9187572088722537132[10] = 0.0;
   out_9187572088722537132[11] = 0.0;
   out_9187572088722537132[12] = 0.0;
   out_9187572088722537132[13] = 0.0;
   out_9187572088722537132[14] = 0.0;
   out_9187572088722537132[15] = 0.0;
   out_9187572088722537132[16] = 0.0;
   out_9187572088722537132[17] = 0.0;
   out_9187572088722537132[18] = 0.0;
   out_9187572088722537132[19] = 1.0;
   out_9187572088722537132[20] = 0.0;
   out_9187572088722537132[21] = 0.0;
   out_9187572088722537132[22] = 0.0;
   out_9187572088722537132[23] = 0.0;
   out_9187572088722537132[24] = 0.0;
   out_9187572088722537132[25] = 0.0;
   out_9187572088722537132[26] = 0.0;
   out_9187572088722537132[27] = 0.0;
   out_9187572088722537132[28] = 0.0;
   out_9187572088722537132[29] = 0.0;
   out_9187572088722537132[30] = 0.0;
   out_9187572088722537132[31] = 0.0;
   out_9187572088722537132[32] = 0.0;
   out_9187572088722537132[33] = 0.0;
   out_9187572088722537132[34] = 0.0;
   out_9187572088722537132[35] = 0.0;
   out_9187572088722537132[36] = 0.0;
   out_9187572088722537132[37] = 0.0;
   out_9187572088722537132[38] = 1.0;
   out_9187572088722537132[39] = 0.0;
   out_9187572088722537132[40] = 0.0;
   out_9187572088722537132[41] = 0.0;
   out_9187572088722537132[42] = 0.0;
   out_9187572088722537132[43] = 0.0;
   out_9187572088722537132[44] = 0.0;
   out_9187572088722537132[45] = 0.0;
   out_9187572088722537132[46] = 0.0;
   out_9187572088722537132[47] = 0.0;
   out_9187572088722537132[48] = 0.0;
   out_9187572088722537132[49] = 0.0;
   out_9187572088722537132[50] = 0.0;
   out_9187572088722537132[51] = 0.0;
   out_9187572088722537132[52] = 0.0;
   out_9187572088722537132[53] = 0.0;
   out_9187572088722537132[54] = 0.0;
   out_9187572088722537132[55] = 0.0;
   out_9187572088722537132[56] = 0.0;
   out_9187572088722537132[57] = 1.0;
   out_9187572088722537132[58] = 0.0;
   out_9187572088722537132[59] = 0.0;
   out_9187572088722537132[60] = 0.0;
   out_9187572088722537132[61] = 0.0;
   out_9187572088722537132[62] = 0.0;
   out_9187572088722537132[63] = 0.0;
   out_9187572088722537132[64] = 0.0;
   out_9187572088722537132[65] = 0.0;
   out_9187572088722537132[66] = 0.0;
   out_9187572088722537132[67] = 0.0;
   out_9187572088722537132[68] = 0.0;
   out_9187572088722537132[69] = 0.0;
   out_9187572088722537132[70] = 0.0;
   out_9187572088722537132[71] = 0.0;
   out_9187572088722537132[72] = 0.0;
   out_9187572088722537132[73] = 0.0;
   out_9187572088722537132[74] = 0.0;
   out_9187572088722537132[75] = 0.0;
   out_9187572088722537132[76] = 1.0;
   out_9187572088722537132[77] = 0.0;
   out_9187572088722537132[78] = 0.0;
   out_9187572088722537132[79] = 0.0;
   out_9187572088722537132[80] = 0.0;
   out_9187572088722537132[81] = 0.0;
   out_9187572088722537132[82] = 0.0;
   out_9187572088722537132[83] = 0.0;
   out_9187572088722537132[84] = 0.0;
   out_9187572088722537132[85] = 0.0;
   out_9187572088722537132[86] = 0.0;
   out_9187572088722537132[87] = 0.0;
   out_9187572088722537132[88] = 0.0;
   out_9187572088722537132[89] = 0.0;
   out_9187572088722537132[90] = 0.0;
   out_9187572088722537132[91] = 0.0;
   out_9187572088722537132[92] = 0.0;
   out_9187572088722537132[93] = 0.0;
   out_9187572088722537132[94] = 0.0;
   out_9187572088722537132[95] = 1.0;
   out_9187572088722537132[96] = 0.0;
   out_9187572088722537132[97] = 0.0;
   out_9187572088722537132[98] = 0.0;
   out_9187572088722537132[99] = 0.0;
   out_9187572088722537132[100] = 0.0;
   out_9187572088722537132[101] = 0.0;
   out_9187572088722537132[102] = 0.0;
   out_9187572088722537132[103] = 0.0;
   out_9187572088722537132[104] = 0.0;
   out_9187572088722537132[105] = 0.0;
   out_9187572088722537132[106] = 0.0;
   out_9187572088722537132[107] = 0.0;
   out_9187572088722537132[108] = 0.0;
   out_9187572088722537132[109] = 0.0;
   out_9187572088722537132[110] = 0.0;
   out_9187572088722537132[111] = 0.0;
   out_9187572088722537132[112] = 0.0;
   out_9187572088722537132[113] = 0.0;
   out_9187572088722537132[114] = 1.0;
   out_9187572088722537132[115] = 0.0;
   out_9187572088722537132[116] = 0.0;
   out_9187572088722537132[117] = 0.0;
   out_9187572088722537132[118] = 0.0;
   out_9187572088722537132[119] = 0.0;
   out_9187572088722537132[120] = 0.0;
   out_9187572088722537132[121] = 0.0;
   out_9187572088722537132[122] = 0.0;
   out_9187572088722537132[123] = 0.0;
   out_9187572088722537132[124] = 0.0;
   out_9187572088722537132[125] = 0.0;
   out_9187572088722537132[126] = 0.0;
   out_9187572088722537132[127] = 0.0;
   out_9187572088722537132[128] = 0.0;
   out_9187572088722537132[129] = 0.0;
   out_9187572088722537132[130] = 0.0;
   out_9187572088722537132[131] = 0.0;
   out_9187572088722537132[132] = 0.0;
   out_9187572088722537132[133] = 1.0;
   out_9187572088722537132[134] = 0.0;
   out_9187572088722537132[135] = 0.0;
   out_9187572088722537132[136] = 0.0;
   out_9187572088722537132[137] = 0.0;
   out_9187572088722537132[138] = 0.0;
   out_9187572088722537132[139] = 0.0;
   out_9187572088722537132[140] = 0.0;
   out_9187572088722537132[141] = 0.0;
   out_9187572088722537132[142] = 0.0;
   out_9187572088722537132[143] = 0.0;
   out_9187572088722537132[144] = 0.0;
   out_9187572088722537132[145] = 0.0;
   out_9187572088722537132[146] = 0.0;
   out_9187572088722537132[147] = 0.0;
   out_9187572088722537132[148] = 0.0;
   out_9187572088722537132[149] = 0.0;
   out_9187572088722537132[150] = 0.0;
   out_9187572088722537132[151] = 0.0;
   out_9187572088722537132[152] = 1.0;
   out_9187572088722537132[153] = 0.0;
   out_9187572088722537132[154] = 0.0;
   out_9187572088722537132[155] = 0.0;
   out_9187572088722537132[156] = 0.0;
   out_9187572088722537132[157] = 0.0;
   out_9187572088722537132[158] = 0.0;
   out_9187572088722537132[159] = 0.0;
   out_9187572088722537132[160] = 0.0;
   out_9187572088722537132[161] = 0.0;
   out_9187572088722537132[162] = 0.0;
   out_9187572088722537132[163] = 0.0;
   out_9187572088722537132[164] = 0.0;
   out_9187572088722537132[165] = 0.0;
   out_9187572088722537132[166] = 0.0;
   out_9187572088722537132[167] = 0.0;
   out_9187572088722537132[168] = 0.0;
   out_9187572088722537132[169] = 0.0;
   out_9187572088722537132[170] = 0.0;
   out_9187572088722537132[171] = 1.0;
   out_9187572088722537132[172] = 0.0;
   out_9187572088722537132[173] = 0.0;
   out_9187572088722537132[174] = 0.0;
   out_9187572088722537132[175] = 0.0;
   out_9187572088722537132[176] = 0.0;
   out_9187572088722537132[177] = 0.0;
   out_9187572088722537132[178] = 0.0;
   out_9187572088722537132[179] = 0.0;
   out_9187572088722537132[180] = 0.0;
   out_9187572088722537132[181] = 0.0;
   out_9187572088722537132[182] = 0.0;
   out_9187572088722537132[183] = 0.0;
   out_9187572088722537132[184] = 0.0;
   out_9187572088722537132[185] = 0.0;
   out_9187572088722537132[186] = 0.0;
   out_9187572088722537132[187] = 0.0;
   out_9187572088722537132[188] = 0.0;
   out_9187572088722537132[189] = 0.0;
   out_9187572088722537132[190] = 1.0;
   out_9187572088722537132[191] = 0.0;
   out_9187572088722537132[192] = 0.0;
   out_9187572088722537132[193] = 0.0;
   out_9187572088722537132[194] = 0.0;
   out_9187572088722537132[195] = 0.0;
   out_9187572088722537132[196] = 0.0;
   out_9187572088722537132[197] = 0.0;
   out_9187572088722537132[198] = 0.0;
   out_9187572088722537132[199] = 0.0;
   out_9187572088722537132[200] = 0.0;
   out_9187572088722537132[201] = 0.0;
   out_9187572088722537132[202] = 0.0;
   out_9187572088722537132[203] = 0.0;
   out_9187572088722537132[204] = 0.0;
   out_9187572088722537132[205] = 0.0;
   out_9187572088722537132[206] = 0.0;
   out_9187572088722537132[207] = 0.0;
   out_9187572088722537132[208] = 0.0;
   out_9187572088722537132[209] = 1.0;
   out_9187572088722537132[210] = 0.0;
   out_9187572088722537132[211] = 0.0;
   out_9187572088722537132[212] = 0.0;
   out_9187572088722537132[213] = 0.0;
   out_9187572088722537132[214] = 0.0;
   out_9187572088722537132[215] = 0.0;
   out_9187572088722537132[216] = 0.0;
   out_9187572088722537132[217] = 0.0;
   out_9187572088722537132[218] = 0.0;
   out_9187572088722537132[219] = 0.0;
   out_9187572088722537132[220] = 0.0;
   out_9187572088722537132[221] = 0.0;
   out_9187572088722537132[222] = 0.0;
   out_9187572088722537132[223] = 0.0;
   out_9187572088722537132[224] = 0.0;
   out_9187572088722537132[225] = 0.0;
   out_9187572088722537132[226] = 0.0;
   out_9187572088722537132[227] = 0.0;
   out_9187572088722537132[228] = 1.0;
   out_9187572088722537132[229] = 0.0;
   out_9187572088722537132[230] = 0.0;
   out_9187572088722537132[231] = 0.0;
   out_9187572088722537132[232] = 0.0;
   out_9187572088722537132[233] = 0.0;
   out_9187572088722537132[234] = 0.0;
   out_9187572088722537132[235] = 0.0;
   out_9187572088722537132[236] = 0.0;
   out_9187572088722537132[237] = 0.0;
   out_9187572088722537132[238] = 0.0;
   out_9187572088722537132[239] = 0.0;
   out_9187572088722537132[240] = 0.0;
   out_9187572088722537132[241] = 0.0;
   out_9187572088722537132[242] = 0.0;
   out_9187572088722537132[243] = 0.0;
   out_9187572088722537132[244] = 0.0;
   out_9187572088722537132[245] = 0.0;
   out_9187572088722537132[246] = 0.0;
   out_9187572088722537132[247] = 1.0;
   out_9187572088722537132[248] = 0.0;
   out_9187572088722537132[249] = 0.0;
   out_9187572088722537132[250] = 0.0;
   out_9187572088722537132[251] = 0.0;
   out_9187572088722537132[252] = 0.0;
   out_9187572088722537132[253] = 0.0;
   out_9187572088722537132[254] = 0.0;
   out_9187572088722537132[255] = 0.0;
   out_9187572088722537132[256] = 0.0;
   out_9187572088722537132[257] = 0.0;
   out_9187572088722537132[258] = 0.0;
   out_9187572088722537132[259] = 0.0;
   out_9187572088722537132[260] = 0.0;
   out_9187572088722537132[261] = 0.0;
   out_9187572088722537132[262] = 0.0;
   out_9187572088722537132[263] = 0.0;
   out_9187572088722537132[264] = 0.0;
   out_9187572088722537132[265] = 0.0;
   out_9187572088722537132[266] = 1.0;
   out_9187572088722537132[267] = 0.0;
   out_9187572088722537132[268] = 0.0;
   out_9187572088722537132[269] = 0.0;
   out_9187572088722537132[270] = 0.0;
   out_9187572088722537132[271] = 0.0;
   out_9187572088722537132[272] = 0.0;
   out_9187572088722537132[273] = 0.0;
   out_9187572088722537132[274] = 0.0;
   out_9187572088722537132[275] = 0.0;
   out_9187572088722537132[276] = 0.0;
   out_9187572088722537132[277] = 0.0;
   out_9187572088722537132[278] = 0.0;
   out_9187572088722537132[279] = 0.0;
   out_9187572088722537132[280] = 0.0;
   out_9187572088722537132[281] = 0.0;
   out_9187572088722537132[282] = 0.0;
   out_9187572088722537132[283] = 0.0;
   out_9187572088722537132[284] = 0.0;
   out_9187572088722537132[285] = 1.0;
   out_9187572088722537132[286] = 0.0;
   out_9187572088722537132[287] = 0.0;
   out_9187572088722537132[288] = 0.0;
   out_9187572088722537132[289] = 0.0;
   out_9187572088722537132[290] = 0.0;
   out_9187572088722537132[291] = 0.0;
   out_9187572088722537132[292] = 0.0;
   out_9187572088722537132[293] = 0.0;
   out_9187572088722537132[294] = 0.0;
   out_9187572088722537132[295] = 0.0;
   out_9187572088722537132[296] = 0.0;
   out_9187572088722537132[297] = 0.0;
   out_9187572088722537132[298] = 0.0;
   out_9187572088722537132[299] = 0.0;
   out_9187572088722537132[300] = 0.0;
   out_9187572088722537132[301] = 0.0;
   out_9187572088722537132[302] = 0.0;
   out_9187572088722537132[303] = 0.0;
   out_9187572088722537132[304] = 1.0;
   out_9187572088722537132[305] = 0.0;
   out_9187572088722537132[306] = 0.0;
   out_9187572088722537132[307] = 0.0;
   out_9187572088722537132[308] = 0.0;
   out_9187572088722537132[309] = 0.0;
   out_9187572088722537132[310] = 0.0;
   out_9187572088722537132[311] = 0.0;
   out_9187572088722537132[312] = 0.0;
   out_9187572088722537132[313] = 0.0;
   out_9187572088722537132[314] = 0.0;
   out_9187572088722537132[315] = 0.0;
   out_9187572088722537132[316] = 0.0;
   out_9187572088722537132[317] = 0.0;
   out_9187572088722537132[318] = 0.0;
   out_9187572088722537132[319] = 0.0;
   out_9187572088722537132[320] = 0.0;
   out_9187572088722537132[321] = 0.0;
   out_9187572088722537132[322] = 0.0;
   out_9187572088722537132[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_6968288532191998630) {
   out_6968288532191998630[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_6968288532191998630[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_6968288532191998630[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_6968288532191998630[3] = dt*state[12] + state[3];
   out_6968288532191998630[4] = dt*state[13] + state[4];
   out_6968288532191998630[5] = dt*state[14] + state[5];
   out_6968288532191998630[6] = state[6];
   out_6968288532191998630[7] = state[7];
   out_6968288532191998630[8] = state[8];
   out_6968288532191998630[9] = state[9];
   out_6968288532191998630[10] = state[10];
   out_6968288532191998630[11] = state[11];
   out_6968288532191998630[12] = state[12];
   out_6968288532191998630[13] = state[13];
   out_6968288532191998630[14] = state[14];
   out_6968288532191998630[15] = state[15];
   out_6968288532191998630[16] = state[16];
   out_6968288532191998630[17] = state[17];
}
void F_fun(double *state, double dt, double *out_396713754572384652) {
   out_396713754572384652[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_396713754572384652[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_396713754572384652[2] = 0;
   out_396713754572384652[3] = 0;
   out_396713754572384652[4] = 0;
   out_396713754572384652[5] = 0;
   out_396713754572384652[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_396713754572384652[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_396713754572384652[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_396713754572384652[9] = 0;
   out_396713754572384652[10] = 0;
   out_396713754572384652[11] = 0;
   out_396713754572384652[12] = 0;
   out_396713754572384652[13] = 0;
   out_396713754572384652[14] = 0;
   out_396713754572384652[15] = 0;
   out_396713754572384652[16] = 0;
   out_396713754572384652[17] = 0;
   out_396713754572384652[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_396713754572384652[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_396713754572384652[20] = 0;
   out_396713754572384652[21] = 0;
   out_396713754572384652[22] = 0;
   out_396713754572384652[23] = 0;
   out_396713754572384652[24] = 0;
   out_396713754572384652[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_396713754572384652[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_396713754572384652[27] = 0;
   out_396713754572384652[28] = 0;
   out_396713754572384652[29] = 0;
   out_396713754572384652[30] = 0;
   out_396713754572384652[31] = 0;
   out_396713754572384652[32] = 0;
   out_396713754572384652[33] = 0;
   out_396713754572384652[34] = 0;
   out_396713754572384652[35] = 0;
   out_396713754572384652[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_396713754572384652[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_396713754572384652[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_396713754572384652[39] = 0;
   out_396713754572384652[40] = 0;
   out_396713754572384652[41] = 0;
   out_396713754572384652[42] = 0;
   out_396713754572384652[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_396713754572384652[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_396713754572384652[45] = 0;
   out_396713754572384652[46] = 0;
   out_396713754572384652[47] = 0;
   out_396713754572384652[48] = 0;
   out_396713754572384652[49] = 0;
   out_396713754572384652[50] = 0;
   out_396713754572384652[51] = 0;
   out_396713754572384652[52] = 0;
   out_396713754572384652[53] = 0;
   out_396713754572384652[54] = 0;
   out_396713754572384652[55] = 0;
   out_396713754572384652[56] = 0;
   out_396713754572384652[57] = 1;
   out_396713754572384652[58] = 0;
   out_396713754572384652[59] = 0;
   out_396713754572384652[60] = 0;
   out_396713754572384652[61] = 0;
   out_396713754572384652[62] = 0;
   out_396713754572384652[63] = 0;
   out_396713754572384652[64] = 0;
   out_396713754572384652[65] = 0;
   out_396713754572384652[66] = dt;
   out_396713754572384652[67] = 0;
   out_396713754572384652[68] = 0;
   out_396713754572384652[69] = 0;
   out_396713754572384652[70] = 0;
   out_396713754572384652[71] = 0;
   out_396713754572384652[72] = 0;
   out_396713754572384652[73] = 0;
   out_396713754572384652[74] = 0;
   out_396713754572384652[75] = 0;
   out_396713754572384652[76] = 1;
   out_396713754572384652[77] = 0;
   out_396713754572384652[78] = 0;
   out_396713754572384652[79] = 0;
   out_396713754572384652[80] = 0;
   out_396713754572384652[81] = 0;
   out_396713754572384652[82] = 0;
   out_396713754572384652[83] = 0;
   out_396713754572384652[84] = 0;
   out_396713754572384652[85] = dt;
   out_396713754572384652[86] = 0;
   out_396713754572384652[87] = 0;
   out_396713754572384652[88] = 0;
   out_396713754572384652[89] = 0;
   out_396713754572384652[90] = 0;
   out_396713754572384652[91] = 0;
   out_396713754572384652[92] = 0;
   out_396713754572384652[93] = 0;
   out_396713754572384652[94] = 0;
   out_396713754572384652[95] = 1;
   out_396713754572384652[96] = 0;
   out_396713754572384652[97] = 0;
   out_396713754572384652[98] = 0;
   out_396713754572384652[99] = 0;
   out_396713754572384652[100] = 0;
   out_396713754572384652[101] = 0;
   out_396713754572384652[102] = 0;
   out_396713754572384652[103] = 0;
   out_396713754572384652[104] = dt;
   out_396713754572384652[105] = 0;
   out_396713754572384652[106] = 0;
   out_396713754572384652[107] = 0;
   out_396713754572384652[108] = 0;
   out_396713754572384652[109] = 0;
   out_396713754572384652[110] = 0;
   out_396713754572384652[111] = 0;
   out_396713754572384652[112] = 0;
   out_396713754572384652[113] = 0;
   out_396713754572384652[114] = 1;
   out_396713754572384652[115] = 0;
   out_396713754572384652[116] = 0;
   out_396713754572384652[117] = 0;
   out_396713754572384652[118] = 0;
   out_396713754572384652[119] = 0;
   out_396713754572384652[120] = 0;
   out_396713754572384652[121] = 0;
   out_396713754572384652[122] = 0;
   out_396713754572384652[123] = 0;
   out_396713754572384652[124] = 0;
   out_396713754572384652[125] = 0;
   out_396713754572384652[126] = 0;
   out_396713754572384652[127] = 0;
   out_396713754572384652[128] = 0;
   out_396713754572384652[129] = 0;
   out_396713754572384652[130] = 0;
   out_396713754572384652[131] = 0;
   out_396713754572384652[132] = 0;
   out_396713754572384652[133] = 1;
   out_396713754572384652[134] = 0;
   out_396713754572384652[135] = 0;
   out_396713754572384652[136] = 0;
   out_396713754572384652[137] = 0;
   out_396713754572384652[138] = 0;
   out_396713754572384652[139] = 0;
   out_396713754572384652[140] = 0;
   out_396713754572384652[141] = 0;
   out_396713754572384652[142] = 0;
   out_396713754572384652[143] = 0;
   out_396713754572384652[144] = 0;
   out_396713754572384652[145] = 0;
   out_396713754572384652[146] = 0;
   out_396713754572384652[147] = 0;
   out_396713754572384652[148] = 0;
   out_396713754572384652[149] = 0;
   out_396713754572384652[150] = 0;
   out_396713754572384652[151] = 0;
   out_396713754572384652[152] = 1;
   out_396713754572384652[153] = 0;
   out_396713754572384652[154] = 0;
   out_396713754572384652[155] = 0;
   out_396713754572384652[156] = 0;
   out_396713754572384652[157] = 0;
   out_396713754572384652[158] = 0;
   out_396713754572384652[159] = 0;
   out_396713754572384652[160] = 0;
   out_396713754572384652[161] = 0;
   out_396713754572384652[162] = 0;
   out_396713754572384652[163] = 0;
   out_396713754572384652[164] = 0;
   out_396713754572384652[165] = 0;
   out_396713754572384652[166] = 0;
   out_396713754572384652[167] = 0;
   out_396713754572384652[168] = 0;
   out_396713754572384652[169] = 0;
   out_396713754572384652[170] = 0;
   out_396713754572384652[171] = 1;
   out_396713754572384652[172] = 0;
   out_396713754572384652[173] = 0;
   out_396713754572384652[174] = 0;
   out_396713754572384652[175] = 0;
   out_396713754572384652[176] = 0;
   out_396713754572384652[177] = 0;
   out_396713754572384652[178] = 0;
   out_396713754572384652[179] = 0;
   out_396713754572384652[180] = 0;
   out_396713754572384652[181] = 0;
   out_396713754572384652[182] = 0;
   out_396713754572384652[183] = 0;
   out_396713754572384652[184] = 0;
   out_396713754572384652[185] = 0;
   out_396713754572384652[186] = 0;
   out_396713754572384652[187] = 0;
   out_396713754572384652[188] = 0;
   out_396713754572384652[189] = 0;
   out_396713754572384652[190] = 1;
   out_396713754572384652[191] = 0;
   out_396713754572384652[192] = 0;
   out_396713754572384652[193] = 0;
   out_396713754572384652[194] = 0;
   out_396713754572384652[195] = 0;
   out_396713754572384652[196] = 0;
   out_396713754572384652[197] = 0;
   out_396713754572384652[198] = 0;
   out_396713754572384652[199] = 0;
   out_396713754572384652[200] = 0;
   out_396713754572384652[201] = 0;
   out_396713754572384652[202] = 0;
   out_396713754572384652[203] = 0;
   out_396713754572384652[204] = 0;
   out_396713754572384652[205] = 0;
   out_396713754572384652[206] = 0;
   out_396713754572384652[207] = 0;
   out_396713754572384652[208] = 0;
   out_396713754572384652[209] = 1;
   out_396713754572384652[210] = 0;
   out_396713754572384652[211] = 0;
   out_396713754572384652[212] = 0;
   out_396713754572384652[213] = 0;
   out_396713754572384652[214] = 0;
   out_396713754572384652[215] = 0;
   out_396713754572384652[216] = 0;
   out_396713754572384652[217] = 0;
   out_396713754572384652[218] = 0;
   out_396713754572384652[219] = 0;
   out_396713754572384652[220] = 0;
   out_396713754572384652[221] = 0;
   out_396713754572384652[222] = 0;
   out_396713754572384652[223] = 0;
   out_396713754572384652[224] = 0;
   out_396713754572384652[225] = 0;
   out_396713754572384652[226] = 0;
   out_396713754572384652[227] = 0;
   out_396713754572384652[228] = 1;
   out_396713754572384652[229] = 0;
   out_396713754572384652[230] = 0;
   out_396713754572384652[231] = 0;
   out_396713754572384652[232] = 0;
   out_396713754572384652[233] = 0;
   out_396713754572384652[234] = 0;
   out_396713754572384652[235] = 0;
   out_396713754572384652[236] = 0;
   out_396713754572384652[237] = 0;
   out_396713754572384652[238] = 0;
   out_396713754572384652[239] = 0;
   out_396713754572384652[240] = 0;
   out_396713754572384652[241] = 0;
   out_396713754572384652[242] = 0;
   out_396713754572384652[243] = 0;
   out_396713754572384652[244] = 0;
   out_396713754572384652[245] = 0;
   out_396713754572384652[246] = 0;
   out_396713754572384652[247] = 1;
   out_396713754572384652[248] = 0;
   out_396713754572384652[249] = 0;
   out_396713754572384652[250] = 0;
   out_396713754572384652[251] = 0;
   out_396713754572384652[252] = 0;
   out_396713754572384652[253] = 0;
   out_396713754572384652[254] = 0;
   out_396713754572384652[255] = 0;
   out_396713754572384652[256] = 0;
   out_396713754572384652[257] = 0;
   out_396713754572384652[258] = 0;
   out_396713754572384652[259] = 0;
   out_396713754572384652[260] = 0;
   out_396713754572384652[261] = 0;
   out_396713754572384652[262] = 0;
   out_396713754572384652[263] = 0;
   out_396713754572384652[264] = 0;
   out_396713754572384652[265] = 0;
   out_396713754572384652[266] = 1;
   out_396713754572384652[267] = 0;
   out_396713754572384652[268] = 0;
   out_396713754572384652[269] = 0;
   out_396713754572384652[270] = 0;
   out_396713754572384652[271] = 0;
   out_396713754572384652[272] = 0;
   out_396713754572384652[273] = 0;
   out_396713754572384652[274] = 0;
   out_396713754572384652[275] = 0;
   out_396713754572384652[276] = 0;
   out_396713754572384652[277] = 0;
   out_396713754572384652[278] = 0;
   out_396713754572384652[279] = 0;
   out_396713754572384652[280] = 0;
   out_396713754572384652[281] = 0;
   out_396713754572384652[282] = 0;
   out_396713754572384652[283] = 0;
   out_396713754572384652[284] = 0;
   out_396713754572384652[285] = 1;
   out_396713754572384652[286] = 0;
   out_396713754572384652[287] = 0;
   out_396713754572384652[288] = 0;
   out_396713754572384652[289] = 0;
   out_396713754572384652[290] = 0;
   out_396713754572384652[291] = 0;
   out_396713754572384652[292] = 0;
   out_396713754572384652[293] = 0;
   out_396713754572384652[294] = 0;
   out_396713754572384652[295] = 0;
   out_396713754572384652[296] = 0;
   out_396713754572384652[297] = 0;
   out_396713754572384652[298] = 0;
   out_396713754572384652[299] = 0;
   out_396713754572384652[300] = 0;
   out_396713754572384652[301] = 0;
   out_396713754572384652[302] = 0;
   out_396713754572384652[303] = 0;
   out_396713754572384652[304] = 1;
   out_396713754572384652[305] = 0;
   out_396713754572384652[306] = 0;
   out_396713754572384652[307] = 0;
   out_396713754572384652[308] = 0;
   out_396713754572384652[309] = 0;
   out_396713754572384652[310] = 0;
   out_396713754572384652[311] = 0;
   out_396713754572384652[312] = 0;
   out_396713754572384652[313] = 0;
   out_396713754572384652[314] = 0;
   out_396713754572384652[315] = 0;
   out_396713754572384652[316] = 0;
   out_396713754572384652[317] = 0;
   out_396713754572384652[318] = 0;
   out_396713754572384652[319] = 0;
   out_396713754572384652[320] = 0;
   out_396713754572384652[321] = 0;
   out_396713754572384652[322] = 0;
   out_396713754572384652[323] = 1;
}
void h_4(double *state, double *unused, double *out_3828905798867891597) {
   out_3828905798867891597[0] = state[6] + state[9];
   out_3828905798867891597[1] = state[7] + state[10];
   out_3828905798867891597[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_8433411086667824525) {
   out_8433411086667824525[0] = 0;
   out_8433411086667824525[1] = 0;
   out_8433411086667824525[2] = 0;
   out_8433411086667824525[3] = 0;
   out_8433411086667824525[4] = 0;
   out_8433411086667824525[5] = 0;
   out_8433411086667824525[6] = 1;
   out_8433411086667824525[7] = 0;
   out_8433411086667824525[8] = 0;
   out_8433411086667824525[9] = 1;
   out_8433411086667824525[10] = 0;
   out_8433411086667824525[11] = 0;
   out_8433411086667824525[12] = 0;
   out_8433411086667824525[13] = 0;
   out_8433411086667824525[14] = 0;
   out_8433411086667824525[15] = 0;
   out_8433411086667824525[16] = 0;
   out_8433411086667824525[17] = 0;
   out_8433411086667824525[18] = 0;
   out_8433411086667824525[19] = 0;
   out_8433411086667824525[20] = 0;
   out_8433411086667824525[21] = 0;
   out_8433411086667824525[22] = 0;
   out_8433411086667824525[23] = 0;
   out_8433411086667824525[24] = 0;
   out_8433411086667824525[25] = 1;
   out_8433411086667824525[26] = 0;
   out_8433411086667824525[27] = 0;
   out_8433411086667824525[28] = 1;
   out_8433411086667824525[29] = 0;
   out_8433411086667824525[30] = 0;
   out_8433411086667824525[31] = 0;
   out_8433411086667824525[32] = 0;
   out_8433411086667824525[33] = 0;
   out_8433411086667824525[34] = 0;
   out_8433411086667824525[35] = 0;
   out_8433411086667824525[36] = 0;
   out_8433411086667824525[37] = 0;
   out_8433411086667824525[38] = 0;
   out_8433411086667824525[39] = 0;
   out_8433411086667824525[40] = 0;
   out_8433411086667824525[41] = 0;
   out_8433411086667824525[42] = 0;
   out_8433411086667824525[43] = 0;
   out_8433411086667824525[44] = 1;
   out_8433411086667824525[45] = 0;
   out_8433411086667824525[46] = 0;
   out_8433411086667824525[47] = 1;
   out_8433411086667824525[48] = 0;
   out_8433411086667824525[49] = 0;
   out_8433411086667824525[50] = 0;
   out_8433411086667824525[51] = 0;
   out_8433411086667824525[52] = 0;
   out_8433411086667824525[53] = 0;
}
void h_10(double *state, double *unused, double *out_5109572919123009845) {
   out_5109572919123009845[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_5109572919123009845[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_5109572919123009845[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_1305010934300019274) {
   out_1305010934300019274[0] = 0;
   out_1305010934300019274[1] = 9.8100000000000005*cos(state[1]);
   out_1305010934300019274[2] = 0;
   out_1305010934300019274[3] = 0;
   out_1305010934300019274[4] = -state[8];
   out_1305010934300019274[5] = state[7];
   out_1305010934300019274[6] = 0;
   out_1305010934300019274[7] = state[5];
   out_1305010934300019274[8] = -state[4];
   out_1305010934300019274[9] = 0;
   out_1305010934300019274[10] = 0;
   out_1305010934300019274[11] = 0;
   out_1305010934300019274[12] = 1;
   out_1305010934300019274[13] = 0;
   out_1305010934300019274[14] = 0;
   out_1305010934300019274[15] = 1;
   out_1305010934300019274[16] = 0;
   out_1305010934300019274[17] = 0;
   out_1305010934300019274[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_1305010934300019274[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_1305010934300019274[20] = 0;
   out_1305010934300019274[21] = state[8];
   out_1305010934300019274[22] = 0;
   out_1305010934300019274[23] = -state[6];
   out_1305010934300019274[24] = -state[5];
   out_1305010934300019274[25] = 0;
   out_1305010934300019274[26] = state[3];
   out_1305010934300019274[27] = 0;
   out_1305010934300019274[28] = 0;
   out_1305010934300019274[29] = 0;
   out_1305010934300019274[30] = 0;
   out_1305010934300019274[31] = 1;
   out_1305010934300019274[32] = 0;
   out_1305010934300019274[33] = 0;
   out_1305010934300019274[34] = 1;
   out_1305010934300019274[35] = 0;
   out_1305010934300019274[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_1305010934300019274[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_1305010934300019274[38] = 0;
   out_1305010934300019274[39] = -state[7];
   out_1305010934300019274[40] = state[6];
   out_1305010934300019274[41] = 0;
   out_1305010934300019274[42] = state[4];
   out_1305010934300019274[43] = -state[3];
   out_1305010934300019274[44] = 0;
   out_1305010934300019274[45] = 0;
   out_1305010934300019274[46] = 0;
   out_1305010934300019274[47] = 0;
   out_1305010934300019274[48] = 0;
   out_1305010934300019274[49] = 0;
   out_1305010934300019274[50] = 1;
   out_1305010934300019274[51] = 0;
   out_1305010934300019274[52] = 0;
   out_1305010934300019274[53] = 1;
}
void h_13(double *state, double *unused, double *out_5661171709549975544) {
   out_5661171709549975544[0] = state[3];
   out_5661171709549975544[1] = state[4];
   out_5661171709549975544[2] = state[5];
}
void H_13(double *state, double *unused, double *out_5221137261335491724) {
   out_5221137261335491724[0] = 0;
   out_5221137261335491724[1] = 0;
   out_5221137261335491724[2] = 0;
   out_5221137261335491724[3] = 1;
   out_5221137261335491724[4] = 0;
   out_5221137261335491724[5] = 0;
   out_5221137261335491724[6] = 0;
   out_5221137261335491724[7] = 0;
   out_5221137261335491724[8] = 0;
   out_5221137261335491724[9] = 0;
   out_5221137261335491724[10] = 0;
   out_5221137261335491724[11] = 0;
   out_5221137261335491724[12] = 0;
   out_5221137261335491724[13] = 0;
   out_5221137261335491724[14] = 0;
   out_5221137261335491724[15] = 0;
   out_5221137261335491724[16] = 0;
   out_5221137261335491724[17] = 0;
   out_5221137261335491724[18] = 0;
   out_5221137261335491724[19] = 0;
   out_5221137261335491724[20] = 0;
   out_5221137261335491724[21] = 0;
   out_5221137261335491724[22] = 1;
   out_5221137261335491724[23] = 0;
   out_5221137261335491724[24] = 0;
   out_5221137261335491724[25] = 0;
   out_5221137261335491724[26] = 0;
   out_5221137261335491724[27] = 0;
   out_5221137261335491724[28] = 0;
   out_5221137261335491724[29] = 0;
   out_5221137261335491724[30] = 0;
   out_5221137261335491724[31] = 0;
   out_5221137261335491724[32] = 0;
   out_5221137261335491724[33] = 0;
   out_5221137261335491724[34] = 0;
   out_5221137261335491724[35] = 0;
   out_5221137261335491724[36] = 0;
   out_5221137261335491724[37] = 0;
   out_5221137261335491724[38] = 0;
   out_5221137261335491724[39] = 0;
   out_5221137261335491724[40] = 0;
   out_5221137261335491724[41] = 1;
   out_5221137261335491724[42] = 0;
   out_5221137261335491724[43] = 0;
   out_5221137261335491724[44] = 0;
   out_5221137261335491724[45] = 0;
   out_5221137261335491724[46] = 0;
   out_5221137261335491724[47] = 0;
   out_5221137261335491724[48] = 0;
   out_5221137261335491724[49] = 0;
   out_5221137261335491724[50] = 0;
   out_5221137261335491724[51] = 0;
   out_5221137261335491724[52] = 0;
   out_5221137261335491724[53] = 0;
}
void h_14(double *state, double *unused, double *out_6329175778955850944) {
   out_6329175778955850944[0] = state[6];
   out_6329175778955850944[1] = state[7];
   out_6329175778955850944[2] = state[8];
}
void H_14(double *state, double *unused, double *out_6930544554746354795) {
   out_6930544554746354795[0] = 0;
   out_6930544554746354795[1] = 0;
   out_6930544554746354795[2] = 0;
   out_6930544554746354795[3] = 0;
   out_6930544554746354795[4] = 0;
   out_6930544554746354795[5] = 0;
   out_6930544554746354795[6] = 1;
   out_6930544554746354795[7] = 0;
   out_6930544554746354795[8] = 0;
   out_6930544554746354795[9] = 0;
   out_6930544554746354795[10] = 0;
   out_6930544554746354795[11] = 0;
   out_6930544554746354795[12] = 0;
   out_6930544554746354795[13] = 0;
   out_6930544554746354795[14] = 0;
   out_6930544554746354795[15] = 0;
   out_6930544554746354795[16] = 0;
   out_6930544554746354795[17] = 0;
   out_6930544554746354795[18] = 0;
   out_6930544554746354795[19] = 0;
   out_6930544554746354795[20] = 0;
   out_6930544554746354795[21] = 0;
   out_6930544554746354795[22] = 0;
   out_6930544554746354795[23] = 0;
   out_6930544554746354795[24] = 0;
   out_6930544554746354795[25] = 1;
   out_6930544554746354795[26] = 0;
   out_6930544554746354795[27] = 0;
   out_6930544554746354795[28] = 0;
   out_6930544554746354795[29] = 0;
   out_6930544554746354795[30] = 0;
   out_6930544554746354795[31] = 0;
   out_6930544554746354795[32] = 0;
   out_6930544554746354795[33] = 0;
   out_6930544554746354795[34] = 0;
   out_6930544554746354795[35] = 0;
   out_6930544554746354795[36] = 0;
   out_6930544554746354795[37] = 0;
   out_6930544554746354795[38] = 0;
   out_6930544554746354795[39] = 0;
   out_6930544554746354795[40] = 0;
   out_6930544554746354795[41] = 0;
   out_6930544554746354795[42] = 0;
   out_6930544554746354795[43] = 0;
   out_6930544554746354795[44] = 1;
   out_6930544554746354795[45] = 0;
   out_6930544554746354795[46] = 0;
   out_6930544554746354795[47] = 0;
   out_6930544554746354795[48] = 0;
   out_6930544554746354795[49] = 0;
   out_6930544554746354795[50] = 0;
   out_6930544554746354795[51] = 0;
   out_6930544554746354795[52] = 0;
   out_6930544554746354795[53] = 0;
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
void pose_err_fun(double *nom_x, double *delta_x, double *out_5712645316975978292) {
  err_fun(nom_x, delta_x, out_5712645316975978292);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_2375481713030026782) {
  inv_err_fun(nom_x, true_x, out_2375481713030026782);
}
void pose_H_mod_fun(double *state, double *out_9187572088722537132) {
  H_mod_fun(state, out_9187572088722537132);
}
void pose_f_fun(double *state, double dt, double *out_6968288532191998630) {
  f_fun(state,  dt, out_6968288532191998630);
}
void pose_F_fun(double *state, double dt, double *out_396713754572384652) {
  F_fun(state,  dt, out_396713754572384652);
}
void pose_h_4(double *state, double *unused, double *out_3828905798867891597) {
  h_4(state, unused, out_3828905798867891597);
}
void pose_H_4(double *state, double *unused, double *out_8433411086667824525) {
  H_4(state, unused, out_8433411086667824525);
}
void pose_h_10(double *state, double *unused, double *out_5109572919123009845) {
  h_10(state, unused, out_5109572919123009845);
}
void pose_H_10(double *state, double *unused, double *out_1305010934300019274) {
  H_10(state, unused, out_1305010934300019274);
}
void pose_h_13(double *state, double *unused, double *out_5661171709549975544) {
  h_13(state, unused, out_5661171709549975544);
}
void pose_H_13(double *state, double *unused, double *out_5221137261335491724) {
  H_13(state, unused, out_5221137261335491724);
}
void pose_h_14(double *state, double *unused, double *out_6329175778955850944) {
  h_14(state, unused, out_6329175778955850944);
}
void pose_H_14(double *state, double *unused, double *out_6930544554746354795) {
  H_14(state, unused, out_6930544554746354795);
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
