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
void err_fun(double *nom_x, double *delta_x, double *out_3055639861342664638) {
   out_3055639861342664638[0] = delta_x[0] + nom_x[0];
   out_3055639861342664638[1] = delta_x[1] + nom_x[1];
   out_3055639861342664638[2] = delta_x[2] + nom_x[2];
   out_3055639861342664638[3] = delta_x[3] + nom_x[3];
   out_3055639861342664638[4] = delta_x[4] + nom_x[4];
   out_3055639861342664638[5] = delta_x[5] + nom_x[5];
   out_3055639861342664638[6] = delta_x[6] + nom_x[6];
   out_3055639861342664638[7] = delta_x[7] + nom_x[7];
   out_3055639861342664638[8] = delta_x[8] + nom_x[8];
   out_3055639861342664638[9] = delta_x[9] + nom_x[9];
   out_3055639861342664638[10] = delta_x[10] + nom_x[10];
   out_3055639861342664638[11] = delta_x[11] + nom_x[11];
   out_3055639861342664638[12] = delta_x[12] + nom_x[12];
   out_3055639861342664638[13] = delta_x[13] + nom_x[13];
   out_3055639861342664638[14] = delta_x[14] + nom_x[14];
   out_3055639861342664638[15] = delta_x[15] + nom_x[15];
   out_3055639861342664638[16] = delta_x[16] + nom_x[16];
   out_3055639861342664638[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_2233443736881945674) {
   out_2233443736881945674[0] = -nom_x[0] + true_x[0];
   out_2233443736881945674[1] = -nom_x[1] + true_x[1];
   out_2233443736881945674[2] = -nom_x[2] + true_x[2];
   out_2233443736881945674[3] = -nom_x[3] + true_x[3];
   out_2233443736881945674[4] = -nom_x[4] + true_x[4];
   out_2233443736881945674[5] = -nom_x[5] + true_x[5];
   out_2233443736881945674[6] = -nom_x[6] + true_x[6];
   out_2233443736881945674[7] = -nom_x[7] + true_x[7];
   out_2233443736881945674[8] = -nom_x[8] + true_x[8];
   out_2233443736881945674[9] = -nom_x[9] + true_x[9];
   out_2233443736881945674[10] = -nom_x[10] + true_x[10];
   out_2233443736881945674[11] = -nom_x[11] + true_x[11];
   out_2233443736881945674[12] = -nom_x[12] + true_x[12];
   out_2233443736881945674[13] = -nom_x[13] + true_x[13];
   out_2233443736881945674[14] = -nom_x[14] + true_x[14];
   out_2233443736881945674[15] = -nom_x[15] + true_x[15];
   out_2233443736881945674[16] = -nom_x[16] + true_x[16];
   out_2233443736881945674[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_5454317104155112741) {
   out_5454317104155112741[0] = 1.0;
   out_5454317104155112741[1] = 0.0;
   out_5454317104155112741[2] = 0.0;
   out_5454317104155112741[3] = 0.0;
   out_5454317104155112741[4] = 0.0;
   out_5454317104155112741[5] = 0.0;
   out_5454317104155112741[6] = 0.0;
   out_5454317104155112741[7] = 0.0;
   out_5454317104155112741[8] = 0.0;
   out_5454317104155112741[9] = 0.0;
   out_5454317104155112741[10] = 0.0;
   out_5454317104155112741[11] = 0.0;
   out_5454317104155112741[12] = 0.0;
   out_5454317104155112741[13] = 0.0;
   out_5454317104155112741[14] = 0.0;
   out_5454317104155112741[15] = 0.0;
   out_5454317104155112741[16] = 0.0;
   out_5454317104155112741[17] = 0.0;
   out_5454317104155112741[18] = 0.0;
   out_5454317104155112741[19] = 1.0;
   out_5454317104155112741[20] = 0.0;
   out_5454317104155112741[21] = 0.0;
   out_5454317104155112741[22] = 0.0;
   out_5454317104155112741[23] = 0.0;
   out_5454317104155112741[24] = 0.0;
   out_5454317104155112741[25] = 0.0;
   out_5454317104155112741[26] = 0.0;
   out_5454317104155112741[27] = 0.0;
   out_5454317104155112741[28] = 0.0;
   out_5454317104155112741[29] = 0.0;
   out_5454317104155112741[30] = 0.0;
   out_5454317104155112741[31] = 0.0;
   out_5454317104155112741[32] = 0.0;
   out_5454317104155112741[33] = 0.0;
   out_5454317104155112741[34] = 0.0;
   out_5454317104155112741[35] = 0.0;
   out_5454317104155112741[36] = 0.0;
   out_5454317104155112741[37] = 0.0;
   out_5454317104155112741[38] = 1.0;
   out_5454317104155112741[39] = 0.0;
   out_5454317104155112741[40] = 0.0;
   out_5454317104155112741[41] = 0.0;
   out_5454317104155112741[42] = 0.0;
   out_5454317104155112741[43] = 0.0;
   out_5454317104155112741[44] = 0.0;
   out_5454317104155112741[45] = 0.0;
   out_5454317104155112741[46] = 0.0;
   out_5454317104155112741[47] = 0.0;
   out_5454317104155112741[48] = 0.0;
   out_5454317104155112741[49] = 0.0;
   out_5454317104155112741[50] = 0.0;
   out_5454317104155112741[51] = 0.0;
   out_5454317104155112741[52] = 0.0;
   out_5454317104155112741[53] = 0.0;
   out_5454317104155112741[54] = 0.0;
   out_5454317104155112741[55] = 0.0;
   out_5454317104155112741[56] = 0.0;
   out_5454317104155112741[57] = 1.0;
   out_5454317104155112741[58] = 0.0;
   out_5454317104155112741[59] = 0.0;
   out_5454317104155112741[60] = 0.0;
   out_5454317104155112741[61] = 0.0;
   out_5454317104155112741[62] = 0.0;
   out_5454317104155112741[63] = 0.0;
   out_5454317104155112741[64] = 0.0;
   out_5454317104155112741[65] = 0.0;
   out_5454317104155112741[66] = 0.0;
   out_5454317104155112741[67] = 0.0;
   out_5454317104155112741[68] = 0.0;
   out_5454317104155112741[69] = 0.0;
   out_5454317104155112741[70] = 0.0;
   out_5454317104155112741[71] = 0.0;
   out_5454317104155112741[72] = 0.0;
   out_5454317104155112741[73] = 0.0;
   out_5454317104155112741[74] = 0.0;
   out_5454317104155112741[75] = 0.0;
   out_5454317104155112741[76] = 1.0;
   out_5454317104155112741[77] = 0.0;
   out_5454317104155112741[78] = 0.0;
   out_5454317104155112741[79] = 0.0;
   out_5454317104155112741[80] = 0.0;
   out_5454317104155112741[81] = 0.0;
   out_5454317104155112741[82] = 0.0;
   out_5454317104155112741[83] = 0.0;
   out_5454317104155112741[84] = 0.0;
   out_5454317104155112741[85] = 0.0;
   out_5454317104155112741[86] = 0.0;
   out_5454317104155112741[87] = 0.0;
   out_5454317104155112741[88] = 0.0;
   out_5454317104155112741[89] = 0.0;
   out_5454317104155112741[90] = 0.0;
   out_5454317104155112741[91] = 0.0;
   out_5454317104155112741[92] = 0.0;
   out_5454317104155112741[93] = 0.0;
   out_5454317104155112741[94] = 0.0;
   out_5454317104155112741[95] = 1.0;
   out_5454317104155112741[96] = 0.0;
   out_5454317104155112741[97] = 0.0;
   out_5454317104155112741[98] = 0.0;
   out_5454317104155112741[99] = 0.0;
   out_5454317104155112741[100] = 0.0;
   out_5454317104155112741[101] = 0.0;
   out_5454317104155112741[102] = 0.0;
   out_5454317104155112741[103] = 0.0;
   out_5454317104155112741[104] = 0.0;
   out_5454317104155112741[105] = 0.0;
   out_5454317104155112741[106] = 0.0;
   out_5454317104155112741[107] = 0.0;
   out_5454317104155112741[108] = 0.0;
   out_5454317104155112741[109] = 0.0;
   out_5454317104155112741[110] = 0.0;
   out_5454317104155112741[111] = 0.0;
   out_5454317104155112741[112] = 0.0;
   out_5454317104155112741[113] = 0.0;
   out_5454317104155112741[114] = 1.0;
   out_5454317104155112741[115] = 0.0;
   out_5454317104155112741[116] = 0.0;
   out_5454317104155112741[117] = 0.0;
   out_5454317104155112741[118] = 0.0;
   out_5454317104155112741[119] = 0.0;
   out_5454317104155112741[120] = 0.0;
   out_5454317104155112741[121] = 0.0;
   out_5454317104155112741[122] = 0.0;
   out_5454317104155112741[123] = 0.0;
   out_5454317104155112741[124] = 0.0;
   out_5454317104155112741[125] = 0.0;
   out_5454317104155112741[126] = 0.0;
   out_5454317104155112741[127] = 0.0;
   out_5454317104155112741[128] = 0.0;
   out_5454317104155112741[129] = 0.0;
   out_5454317104155112741[130] = 0.0;
   out_5454317104155112741[131] = 0.0;
   out_5454317104155112741[132] = 0.0;
   out_5454317104155112741[133] = 1.0;
   out_5454317104155112741[134] = 0.0;
   out_5454317104155112741[135] = 0.0;
   out_5454317104155112741[136] = 0.0;
   out_5454317104155112741[137] = 0.0;
   out_5454317104155112741[138] = 0.0;
   out_5454317104155112741[139] = 0.0;
   out_5454317104155112741[140] = 0.0;
   out_5454317104155112741[141] = 0.0;
   out_5454317104155112741[142] = 0.0;
   out_5454317104155112741[143] = 0.0;
   out_5454317104155112741[144] = 0.0;
   out_5454317104155112741[145] = 0.0;
   out_5454317104155112741[146] = 0.0;
   out_5454317104155112741[147] = 0.0;
   out_5454317104155112741[148] = 0.0;
   out_5454317104155112741[149] = 0.0;
   out_5454317104155112741[150] = 0.0;
   out_5454317104155112741[151] = 0.0;
   out_5454317104155112741[152] = 1.0;
   out_5454317104155112741[153] = 0.0;
   out_5454317104155112741[154] = 0.0;
   out_5454317104155112741[155] = 0.0;
   out_5454317104155112741[156] = 0.0;
   out_5454317104155112741[157] = 0.0;
   out_5454317104155112741[158] = 0.0;
   out_5454317104155112741[159] = 0.0;
   out_5454317104155112741[160] = 0.0;
   out_5454317104155112741[161] = 0.0;
   out_5454317104155112741[162] = 0.0;
   out_5454317104155112741[163] = 0.0;
   out_5454317104155112741[164] = 0.0;
   out_5454317104155112741[165] = 0.0;
   out_5454317104155112741[166] = 0.0;
   out_5454317104155112741[167] = 0.0;
   out_5454317104155112741[168] = 0.0;
   out_5454317104155112741[169] = 0.0;
   out_5454317104155112741[170] = 0.0;
   out_5454317104155112741[171] = 1.0;
   out_5454317104155112741[172] = 0.0;
   out_5454317104155112741[173] = 0.0;
   out_5454317104155112741[174] = 0.0;
   out_5454317104155112741[175] = 0.0;
   out_5454317104155112741[176] = 0.0;
   out_5454317104155112741[177] = 0.0;
   out_5454317104155112741[178] = 0.0;
   out_5454317104155112741[179] = 0.0;
   out_5454317104155112741[180] = 0.0;
   out_5454317104155112741[181] = 0.0;
   out_5454317104155112741[182] = 0.0;
   out_5454317104155112741[183] = 0.0;
   out_5454317104155112741[184] = 0.0;
   out_5454317104155112741[185] = 0.0;
   out_5454317104155112741[186] = 0.0;
   out_5454317104155112741[187] = 0.0;
   out_5454317104155112741[188] = 0.0;
   out_5454317104155112741[189] = 0.0;
   out_5454317104155112741[190] = 1.0;
   out_5454317104155112741[191] = 0.0;
   out_5454317104155112741[192] = 0.0;
   out_5454317104155112741[193] = 0.0;
   out_5454317104155112741[194] = 0.0;
   out_5454317104155112741[195] = 0.0;
   out_5454317104155112741[196] = 0.0;
   out_5454317104155112741[197] = 0.0;
   out_5454317104155112741[198] = 0.0;
   out_5454317104155112741[199] = 0.0;
   out_5454317104155112741[200] = 0.0;
   out_5454317104155112741[201] = 0.0;
   out_5454317104155112741[202] = 0.0;
   out_5454317104155112741[203] = 0.0;
   out_5454317104155112741[204] = 0.0;
   out_5454317104155112741[205] = 0.0;
   out_5454317104155112741[206] = 0.0;
   out_5454317104155112741[207] = 0.0;
   out_5454317104155112741[208] = 0.0;
   out_5454317104155112741[209] = 1.0;
   out_5454317104155112741[210] = 0.0;
   out_5454317104155112741[211] = 0.0;
   out_5454317104155112741[212] = 0.0;
   out_5454317104155112741[213] = 0.0;
   out_5454317104155112741[214] = 0.0;
   out_5454317104155112741[215] = 0.0;
   out_5454317104155112741[216] = 0.0;
   out_5454317104155112741[217] = 0.0;
   out_5454317104155112741[218] = 0.0;
   out_5454317104155112741[219] = 0.0;
   out_5454317104155112741[220] = 0.0;
   out_5454317104155112741[221] = 0.0;
   out_5454317104155112741[222] = 0.0;
   out_5454317104155112741[223] = 0.0;
   out_5454317104155112741[224] = 0.0;
   out_5454317104155112741[225] = 0.0;
   out_5454317104155112741[226] = 0.0;
   out_5454317104155112741[227] = 0.0;
   out_5454317104155112741[228] = 1.0;
   out_5454317104155112741[229] = 0.0;
   out_5454317104155112741[230] = 0.0;
   out_5454317104155112741[231] = 0.0;
   out_5454317104155112741[232] = 0.0;
   out_5454317104155112741[233] = 0.0;
   out_5454317104155112741[234] = 0.0;
   out_5454317104155112741[235] = 0.0;
   out_5454317104155112741[236] = 0.0;
   out_5454317104155112741[237] = 0.0;
   out_5454317104155112741[238] = 0.0;
   out_5454317104155112741[239] = 0.0;
   out_5454317104155112741[240] = 0.0;
   out_5454317104155112741[241] = 0.0;
   out_5454317104155112741[242] = 0.0;
   out_5454317104155112741[243] = 0.0;
   out_5454317104155112741[244] = 0.0;
   out_5454317104155112741[245] = 0.0;
   out_5454317104155112741[246] = 0.0;
   out_5454317104155112741[247] = 1.0;
   out_5454317104155112741[248] = 0.0;
   out_5454317104155112741[249] = 0.0;
   out_5454317104155112741[250] = 0.0;
   out_5454317104155112741[251] = 0.0;
   out_5454317104155112741[252] = 0.0;
   out_5454317104155112741[253] = 0.0;
   out_5454317104155112741[254] = 0.0;
   out_5454317104155112741[255] = 0.0;
   out_5454317104155112741[256] = 0.0;
   out_5454317104155112741[257] = 0.0;
   out_5454317104155112741[258] = 0.0;
   out_5454317104155112741[259] = 0.0;
   out_5454317104155112741[260] = 0.0;
   out_5454317104155112741[261] = 0.0;
   out_5454317104155112741[262] = 0.0;
   out_5454317104155112741[263] = 0.0;
   out_5454317104155112741[264] = 0.0;
   out_5454317104155112741[265] = 0.0;
   out_5454317104155112741[266] = 1.0;
   out_5454317104155112741[267] = 0.0;
   out_5454317104155112741[268] = 0.0;
   out_5454317104155112741[269] = 0.0;
   out_5454317104155112741[270] = 0.0;
   out_5454317104155112741[271] = 0.0;
   out_5454317104155112741[272] = 0.0;
   out_5454317104155112741[273] = 0.0;
   out_5454317104155112741[274] = 0.0;
   out_5454317104155112741[275] = 0.0;
   out_5454317104155112741[276] = 0.0;
   out_5454317104155112741[277] = 0.0;
   out_5454317104155112741[278] = 0.0;
   out_5454317104155112741[279] = 0.0;
   out_5454317104155112741[280] = 0.0;
   out_5454317104155112741[281] = 0.0;
   out_5454317104155112741[282] = 0.0;
   out_5454317104155112741[283] = 0.0;
   out_5454317104155112741[284] = 0.0;
   out_5454317104155112741[285] = 1.0;
   out_5454317104155112741[286] = 0.0;
   out_5454317104155112741[287] = 0.0;
   out_5454317104155112741[288] = 0.0;
   out_5454317104155112741[289] = 0.0;
   out_5454317104155112741[290] = 0.0;
   out_5454317104155112741[291] = 0.0;
   out_5454317104155112741[292] = 0.0;
   out_5454317104155112741[293] = 0.0;
   out_5454317104155112741[294] = 0.0;
   out_5454317104155112741[295] = 0.0;
   out_5454317104155112741[296] = 0.0;
   out_5454317104155112741[297] = 0.0;
   out_5454317104155112741[298] = 0.0;
   out_5454317104155112741[299] = 0.0;
   out_5454317104155112741[300] = 0.0;
   out_5454317104155112741[301] = 0.0;
   out_5454317104155112741[302] = 0.0;
   out_5454317104155112741[303] = 0.0;
   out_5454317104155112741[304] = 1.0;
   out_5454317104155112741[305] = 0.0;
   out_5454317104155112741[306] = 0.0;
   out_5454317104155112741[307] = 0.0;
   out_5454317104155112741[308] = 0.0;
   out_5454317104155112741[309] = 0.0;
   out_5454317104155112741[310] = 0.0;
   out_5454317104155112741[311] = 0.0;
   out_5454317104155112741[312] = 0.0;
   out_5454317104155112741[313] = 0.0;
   out_5454317104155112741[314] = 0.0;
   out_5454317104155112741[315] = 0.0;
   out_5454317104155112741[316] = 0.0;
   out_5454317104155112741[317] = 0.0;
   out_5454317104155112741[318] = 0.0;
   out_5454317104155112741[319] = 0.0;
   out_5454317104155112741[320] = 0.0;
   out_5454317104155112741[321] = 0.0;
   out_5454317104155112741[322] = 0.0;
   out_5454317104155112741[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_4996223981732405570) {
   out_4996223981732405570[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_4996223981732405570[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_4996223981732405570[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_4996223981732405570[3] = dt*state[12] + state[3];
   out_4996223981732405570[4] = dt*state[13] + state[4];
   out_4996223981732405570[5] = dt*state[14] + state[5];
   out_4996223981732405570[6] = state[6];
   out_4996223981732405570[7] = state[7];
   out_4996223981732405570[8] = state[8];
   out_4996223981732405570[9] = state[9];
   out_4996223981732405570[10] = state[10];
   out_4996223981732405570[11] = state[11];
   out_4996223981732405570[12] = state[12];
   out_4996223981732405570[13] = state[13];
   out_4996223981732405570[14] = state[14];
   out_4996223981732405570[15] = state[15];
   out_4996223981732405570[16] = state[16];
   out_4996223981732405570[17] = state[17];
}
void F_fun(double *state, double dt, double *out_5891913618111355049) {
   out_5891913618111355049[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_5891913618111355049[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_5891913618111355049[2] = 0;
   out_5891913618111355049[3] = 0;
   out_5891913618111355049[4] = 0;
   out_5891913618111355049[5] = 0;
   out_5891913618111355049[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_5891913618111355049[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_5891913618111355049[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_5891913618111355049[9] = 0;
   out_5891913618111355049[10] = 0;
   out_5891913618111355049[11] = 0;
   out_5891913618111355049[12] = 0;
   out_5891913618111355049[13] = 0;
   out_5891913618111355049[14] = 0;
   out_5891913618111355049[15] = 0;
   out_5891913618111355049[16] = 0;
   out_5891913618111355049[17] = 0;
   out_5891913618111355049[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_5891913618111355049[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_5891913618111355049[20] = 0;
   out_5891913618111355049[21] = 0;
   out_5891913618111355049[22] = 0;
   out_5891913618111355049[23] = 0;
   out_5891913618111355049[24] = 0;
   out_5891913618111355049[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_5891913618111355049[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_5891913618111355049[27] = 0;
   out_5891913618111355049[28] = 0;
   out_5891913618111355049[29] = 0;
   out_5891913618111355049[30] = 0;
   out_5891913618111355049[31] = 0;
   out_5891913618111355049[32] = 0;
   out_5891913618111355049[33] = 0;
   out_5891913618111355049[34] = 0;
   out_5891913618111355049[35] = 0;
   out_5891913618111355049[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_5891913618111355049[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_5891913618111355049[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_5891913618111355049[39] = 0;
   out_5891913618111355049[40] = 0;
   out_5891913618111355049[41] = 0;
   out_5891913618111355049[42] = 0;
   out_5891913618111355049[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_5891913618111355049[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_5891913618111355049[45] = 0;
   out_5891913618111355049[46] = 0;
   out_5891913618111355049[47] = 0;
   out_5891913618111355049[48] = 0;
   out_5891913618111355049[49] = 0;
   out_5891913618111355049[50] = 0;
   out_5891913618111355049[51] = 0;
   out_5891913618111355049[52] = 0;
   out_5891913618111355049[53] = 0;
   out_5891913618111355049[54] = 0;
   out_5891913618111355049[55] = 0;
   out_5891913618111355049[56] = 0;
   out_5891913618111355049[57] = 1;
   out_5891913618111355049[58] = 0;
   out_5891913618111355049[59] = 0;
   out_5891913618111355049[60] = 0;
   out_5891913618111355049[61] = 0;
   out_5891913618111355049[62] = 0;
   out_5891913618111355049[63] = 0;
   out_5891913618111355049[64] = 0;
   out_5891913618111355049[65] = 0;
   out_5891913618111355049[66] = dt;
   out_5891913618111355049[67] = 0;
   out_5891913618111355049[68] = 0;
   out_5891913618111355049[69] = 0;
   out_5891913618111355049[70] = 0;
   out_5891913618111355049[71] = 0;
   out_5891913618111355049[72] = 0;
   out_5891913618111355049[73] = 0;
   out_5891913618111355049[74] = 0;
   out_5891913618111355049[75] = 0;
   out_5891913618111355049[76] = 1;
   out_5891913618111355049[77] = 0;
   out_5891913618111355049[78] = 0;
   out_5891913618111355049[79] = 0;
   out_5891913618111355049[80] = 0;
   out_5891913618111355049[81] = 0;
   out_5891913618111355049[82] = 0;
   out_5891913618111355049[83] = 0;
   out_5891913618111355049[84] = 0;
   out_5891913618111355049[85] = dt;
   out_5891913618111355049[86] = 0;
   out_5891913618111355049[87] = 0;
   out_5891913618111355049[88] = 0;
   out_5891913618111355049[89] = 0;
   out_5891913618111355049[90] = 0;
   out_5891913618111355049[91] = 0;
   out_5891913618111355049[92] = 0;
   out_5891913618111355049[93] = 0;
   out_5891913618111355049[94] = 0;
   out_5891913618111355049[95] = 1;
   out_5891913618111355049[96] = 0;
   out_5891913618111355049[97] = 0;
   out_5891913618111355049[98] = 0;
   out_5891913618111355049[99] = 0;
   out_5891913618111355049[100] = 0;
   out_5891913618111355049[101] = 0;
   out_5891913618111355049[102] = 0;
   out_5891913618111355049[103] = 0;
   out_5891913618111355049[104] = dt;
   out_5891913618111355049[105] = 0;
   out_5891913618111355049[106] = 0;
   out_5891913618111355049[107] = 0;
   out_5891913618111355049[108] = 0;
   out_5891913618111355049[109] = 0;
   out_5891913618111355049[110] = 0;
   out_5891913618111355049[111] = 0;
   out_5891913618111355049[112] = 0;
   out_5891913618111355049[113] = 0;
   out_5891913618111355049[114] = 1;
   out_5891913618111355049[115] = 0;
   out_5891913618111355049[116] = 0;
   out_5891913618111355049[117] = 0;
   out_5891913618111355049[118] = 0;
   out_5891913618111355049[119] = 0;
   out_5891913618111355049[120] = 0;
   out_5891913618111355049[121] = 0;
   out_5891913618111355049[122] = 0;
   out_5891913618111355049[123] = 0;
   out_5891913618111355049[124] = 0;
   out_5891913618111355049[125] = 0;
   out_5891913618111355049[126] = 0;
   out_5891913618111355049[127] = 0;
   out_5891913618111355049[128] = 0;
   out_5891913618111355049[129] = 0;
   out_5891913618111355049[130] = 0;
   out_5891913618111355049[131] = 0;
   out_5891913618111355049[132] = 0;
   out_5891913618111355049[133] = 1;
   out_5891913618111355049[134] = 0;
   out_5891913618111355049[135] = 0;
   out_5891913618111355049[136] = 0;
   out_5891913618111355049[137] = 0;
   out_5891913618111355049[138] = 0;
   out_5891913618111355049[139] = 0;
   out_5891913618111355049[140] = 0;
   out_5891913618111355049[141] = 0;
   out_5891913618111355049[142] = 0;
   out_5891913618111355049[143] = 0;
   out_5891913618111355049[144] = 0;
   out_5891913618111355049[145] = 0;
   out_5891913618111355049[146] = 0;
   out_5891913618111355049[147] = 0;
   out_5891913618111355049[148] = 0;
   out_5891913618111355049[149] = 0;
   out_5891913618111355049[150] = 0;
   out_5891913618111355049[151] = 0;
   out_5891913618111355049[152] = 1;
   out_5891913618111355049[153] = 0;
   out_5891913618111355049[154] = 0;
   out_5891913618111355049[155] = 0;
   out_5891913618111355049[156] = 0;
   out_5891913618111355049[157] = 0;
   out_5891913618111355049[158] = 0;
   out_5891913618111355049[159] = 0;
   out_5891913618111355049[160] = 0;
   out_5891913618111355049[161] = 0;
   out_5891913618111355049[162] = 0;
   out_5891913618111355049[163] = 0;
   out_5891913618111355049[164] = 0;
   out_5891913618111355049[165] = 0;
   out_5891913618111355049[166] = 0;
   out_5891913618111355049[167] = 0;
   out_5891913618111355049[168] = 0;
   out_5891913618111355049[169] = 0;
   out_5891913618111355049[170] = 0;
   out_5891913618111355049[171] = 1;
   out_5891913618111355049[172] = 0;
   out_5891913618111355049[173] = 0;
   out_5891913618111355049[174] = 0;
   out_5891913618111355049[175] = 0;
   out_5891913618111355049[176] = 0;
   out_5891913618111355049[177] = 0;
   out_5891913618111355049[178] = 0;
   out_5891913618111355049[179] = 0;
   out_5891913618111355049[180] = 0;
   out_5891913618111355049[181] = 0;
   out_5891913618111355049[182] = 0;
   out_5891913618111355049[183] = 0;
   out_5891913618111355049[184] = 0;
   out_5891913618111355049[185] = 0;
   out_5891913618111355049[186] = 0;
   out_5891913618111355049[187] = 0;
   out_5891913618111355049[188] = 0;
   out_5891913618111355049[189] = 0;
   out_5891913618111355049[190] = 1;
   out_5891913618111355049[191] = 0;
   out_5891913618111355049[192] = 0;
   out_5891913618111355049[193] = 0;
   out_5891913618111355049[194] = 0;
   out_5891913618111355049[195] = 0;
   out_5891913618111355049[196] = 0;
   out_5891913618111355049[197] = 0;
   out_5891913618111355049[198] = 0;
   out_5891913618111355049[199] = 0;
   out_5891913618111355049[200] = 0;
   out_5891913618111355049[201] = 0;
   out_5891913618111355049[202] = 0;
   out_5891913618111355049[203] = 0;
   out_5891913618111355049[204] = 0;
   out_5891913618111355049[205] = 0;
   out_5891913618111355049[206] = 0;
   out_5891913618111355049[207] = 0;
   out_5891913618111355049[208] = 0;
   out_5891913618111355049[209] = 1;
   out_5891913618111355049[210] = 0;
   out_5891913618111355049[211] = 0;
   out_5891913618111355049[212] = 0;
   out_5891913618111355049[213] = 0;
   out_5891913618111355049[214] = 0;
   out_5891913618111355049[215] = 0;
   out_5891913618111355049[216] = 0;
   out_5891913618111355049[217] = 0;
   out_5891913618111355049[218] = 0;
   out_5891913618111355049[219] = 0;
   out_5891913618111355049[220] = 0;
   out_5891913618111355049[221] = 0;
   out_5891913618111355049[222] = 0;
   out_5891913618111355049[223] = 0;
   out_5891913618111355049[224] = 0;
   out_5891913618111355049[225] = 0;
   out_5891913618111355049[226] = 0;
   out_5891913618111355049[227] = 0;
   out_5891913618111355049[228] = 1;
   out_5891913618111355049[229] = 0;
   out_5891913618111355049[230] = 0;
   out_5891913618111355049[231] = 0;
   out_5891913618111355049[232] = 0;
   out_5891913618111355049[233] = 0;
   out_5891913618111355049[234] = 0;
   out_5891913618111355049[235] = 0;
   out_5891913618111355049[236] = 0;
   out_5891913618111355049[237] = 0;
   out_5891913618111355049[238] = 0;
   out_5891913618111355049[239] = 0;
   out_5891913618111355049[240] = 0;
   out_5891913618111355049[241] = 0;
   out_5891913618111355049[242] = 0;
   out_5891913618111355049[243] = 0;
   out_5891913618111355049[244] = 0;
   out_5891913618111355049[245] = 0;
   out_5891913618111355049[246] = 0;
   out_5891913618111355049[247] = 1;
   out_5891913618111355049[248] = 0;
   out_5891913618111355049[249] = 0;
   out_5891913618111355049[250] = 0;
   out_5891913618111355049[251] = 0;
   out_5891913618111355049[252] = 0;
   out_5891913618111355049[253] = 0;
   out_5891913618111355049[254] = 0;
   out_5891913618111355049[255] = 0;
   out_5891913618111355049[256] = 0;
   out_5891913618111355049[257] = 0;
   out_5891913618111355049[258] = 0;
   out_5891913618111355049[259] = 0;
   out_5891913618111355049[260] = 0;
   out_5891913618111355049[261] = 0;
   out_5891913618111355049[262] = 0;
   out_5891913618111355049[263] = 0;
   out_5891913618111355049[264] = 0;
   out_5891913618111355049[265] = 0;
   out_5891913618111355049[266] = 1;
   out_5891913618111355049[267] = 0;
   out_5891913618111355049[268] = 0;
   out_5891913618111355049[269] = 0;
   out_5891913618111355049[270] = 0;
   out_5891913618111355049[271] = 0;
   out_5891913618111355049[272] = 0;
   out_5891913618111355049[273] = 0;
   out_5891913618111355049[274] = 0;
   out_5891913618111355049[275] = 0;
   out_5891913618111355049[276] = 0;
   out_5891913618111355049[277] = 0;
   out_5891913618111355049[278] = 0;
   out_5891913618111355049[279] = 0;
   out_5891913618111355049[280] = 0;
   out_5891913618111355049[281] = 0;
   out_5891913618111355049[282] = 0;
   out_5891913618111355049[283] = 0;
   out_5891913618111355049[284] = 0;
   out_5891913618111355049[285] = 1;
   out_5891913618111355049[286] = 0;
   out_5891913618111355049[287] = 0;
   out_5891913618111355049[288] = 0;
   out_5891913618111355049[289] = 0;
   out_5891913618111355049[290] = 0;
   out_5891913618111355049[291] = 0;
   out_5891913618111355049[292] = 0;
   out_5891913618111355049[293] = 0;
   out_5891913618111355049[294] = 0;
   out_5891913618111355049[295] = 0;
   out_5891913618111355049[296] = 0;
   out_5891913618111355049[297] = 0;
   out_5891913618111355049[298] = 0;
   out_5891913618111355049[299] = 0;
   out_5891913618111355049[300] = 0;
   out_5891913618111355049[301] = 0;
   out_5891913618111355049[302] = 0;
   out_5891913618111355049[303] = 0;
   out_5891913618111355049[304] = 1;
   out_5891913618111355049[305] = 0;
   out_5891913618111355049[306] = 0;
   out_5891913618111355049[307] = 0;
   out_5891913618111355049[308] = 0;
   out_5891913618111355049[309] = 0;
   out_5891913618111355049[310] = 0;
   out_5891913618111355049[311] = 0;
   out_5891913618111355049[312] = 0;
   out_5891913618111355049[313] = 0;
   out_5891913618111355049[314] = 0;
   out_5891913618111355049[315] = 0;
   out_5891913618111355049[316] = 0;
   out_5891913618111355049[317] = 0;
   out_5891913618111355049[318] = 0;
   out_5891913618111355049[319] = 0;
   out_5891913618111355049[320] = 0;
   out_5891913618111355049[321] = 0;
   out_5891913618111355049[322] = 0;
   out_5891913618111355049[323] = 1;
}
void h_4(double *state, double *unused, double *out_1832779376905477896) {
   out_1832779376905477896[0] = state[6] + state[9];
   out_1832779376905477896[1] = state[7] + state[10];
   out_1832779376905477896[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_4792122085581214108) {
   out_4792122085581214108[0] = 0;
   out_4792122085581214108[1] = 0;
   out_4792122085581214108[2] = 0;
   out_4792122085581214108[3] = 0;
   out_4792122085581214108[4] = 0;
   out_4792122085581214108[5] = 0;
   out_4792122085581214108[6] = 1;
   out_4792122085581214108[7] = 0;
   out_4792122085581214108[8] = 0;
   out_4792122085581214108[9] = 1;
   out_4792122085581214108[10] = 0;
   out_4792122085581214108[11] = 0;
   out_4792122085581214108[12] = 0;
   out_4792122085581214108[13] = 0;
   out_4792122085581214108[14] = 0;
   out_4792122085581214108[15] = 0;
   out_4792122085581214108[16] = 0;
   out_4792122085581214108[17] = 0;
   out_4792122085581214108[18] = 0;
   out_4792122085581214108[19] = 0;
   out_4792122085581214108[20] = 0;
   out_4792122085581214108[21] = 0;
   out_4792122085581214108[22] = 0;
   out_4792122085581214108[23] = 0;
   out_4792122085581214108[24] = 0;
   out_4792122085581214108[25] = 1;
   out_4792122085581214108[26] = 0;
   out_4792122085581214108[27] = 0;
   out_4792122085581214108[28] = 1;
   out_4792122085581214108[29] = 0;
   out_4792122085581214108[30] = 0;
   out_4792122085581214108[31] = 0;
   out_4792122085581214108[32] = 0;
   out_4792122085581214108[33] = 0;
   out_4792122085581214108[34] = 0;
   out_4792122085581214108[35] = 0;
   out_4792122085581214108[36] = 0;
   out_4792122085581214108[37] = 0;
   out_4792122085581214108[38] = 0;
   out_4792122085581214108[39] = 0;
   out_4792122085581214108[40] = 0;
   out_4792122085581214108[41] = 0;
   out_4792122085581214108[42] = 0;
   out_4792122085581214108[43] = 0;
   out_4792122085581214108[44] = 1;
   out_4792122085581214108[45] = 0;
   out_4792122085581214108[46] = 0;
   out_4792122085581214108[47] = 1;
   out_4792122085581214108[48] = 0;
   out_4792122085581214108[49] = 0;
   out_4792122085581214108[50] = 0;
   out_4792122085581214108[51] = 0;
   out_4792122085581214108[52] = 0;
   out_4792122085581214108[53] = 0;
}
void h_10(double *state, double *unused, double *out_4235949127536262679) {
   out_4235949127536262679[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_4235949127536262679[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_4235949127536262679[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_692750502701317014) {
   out_692750502701317014[0] = 0;
   out_692750502701317014[1] = 9.8100000000000005*cos(state[1]);
   out_692750502701317014[2] = 0;
   out_692750502701317014[3] = 0;
   out_692750502701317014[4] = -state[8];
   out_692750502701317014[5] = state[7];
   out_692750502701317014[6] = 0;
   out_692750502701317014[7] = state[5];
   out_692750502701317014[8] = -state[4];
   out_692750502701317014[9] = 0;
   out_692750502701317014[10] = 0;
   out_692750502701317014[11] = 0;
   out_692750502701317014[12] = 1;
   out_692750502701317014[13] = 0;
   out_692750502701317014[14] = 0;
   out_692750502701317014[15] = 1;
   out_692750502701317014[16] = 0;
   out_692750502701317014[17] = 0;
   out_692750502701317014[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_692750502701317014[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_692750502701317014[20] = 0;
   out_692750502701317014[21] = state[8];
   out_692750502701317014[22] = 0;
   out_692750502701317014[23] = -state[6];
   out_692750502701317014[24] = -state[5];
   out_692750502701317014[25] = 0;
   out_692750502701317014[26] = state[3];
   out_692750502701317014[27] = 0;
   out_692750502701317014[28] = 0;
   out_692750502701317014[29] = 0;
   out_692750502701317014[30] = 0;
   out_692750502701317014[31] = 1;
   out_692750502701317014[32] = 0;
   out_692750502701317014[33] = 0;
   out_692750502701317014[34] = 1;
   out_692750502701317014[35] = 0;
   out_692750502701317014[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_692750502701317014[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_692750502701317014[38] = 0;
   out_692750502701317014[39] = -state[7];
   out_692750502701317014[40] = state[6];
   out_692750502701317014[41] = 0;
   out_692750502701317014[42] = state[4];
   out_692750502701317014[43] = -state[3];
   out_692750502701317014[44] = 0;
   out_692750502701317014[45] = 0;
   out_692750502701317014[46] = 0;
   out_692750502701317014[47] = 0;
   out_692750502701317014[48] = 0;
   out_692750502701317014[49] = 0;
   out_692750502701317014[50] = 1;
   out_692750502701317014[51] = 0;
   out_692750502701317014[52] = 0;
   out_692750502701317014[53] = 1;
}
void h_13(double *state, double *unused, double *out_3117911153244826867) {
   out_3117911153244826867[0] = state[3];
   out_3117911153244826867[1] = state[4];
   out_3117911153244826867[2] = state[5];
}
void H_13(double *state, double *unused, double *out_2818509122735486821) {
   out_2818509122735486821[0] = 0;
   out_2818509122735486821[1] = 0;
   out_2818509122735486821[2] = 0;
   out_2818509122735486821[3] = 1;
   out_2818509122735486821[4] = 0;
   out_2818509122735486821[5] = 0;
   out_2818509122735486821[6] = 0;
   out_2818509122735486821[7] = 0;
   out_2818509122735486821[8] = 0;
   out_2818509122735486821[9] = 0;
   out_2818509122735486821[10] = 0;
   out_2818509122735486821[11] = 0;
   out_2818509122735486821[12] = 0;
   out_2818509122735486821[13] = 0;
   out_2818509122735486821[14] = 0;
   out_2818509122735486821[15] = 0;
   out_2818509122735486821[16] = 0;
   out_2818509122735486821[17] = 0;
   out_2818509122735486821[18] = 0;
   out_2818509122735486821[19] = 0;
   out_2818509122735486821[20] = 0;
   out_2818509122735486821[21] = 0;
   out_2818509122735486821[22] = 1;
   out_2818509122735486821[23] = 0;
   out_2818509122735486821[24] = 0;
   out_2818509122735486821[25] = 0;
   out_2818509122735486821[26] = 0;
   out_2818509122735486821[27] = 0;
   out_2818509122735486821[28] = 0;
   out_2818509122735486821[29] = 0;
   out_2818509122735486821[30] = 0;
   out_2818509122735486821[31] = 0;
   out_2818509122735486821[32] = 0;
   out_2818509122735486821[33] = 0;
   out_2818509122735486821[34] = 0;
   out_2818509122735486821[35] = 0;
   out_2818509122735486821[36] = 0;
   out_2818509122735486821[37] = 0;
   out_2818509122735486821[38] = 0;
   out_2818509122735486821[39] = 0;
   out_2818509122735486821[40] = 0;
   out_2818509122735486821[41] = 1;
   out_2818509122735486821[42] = 0;
   out_2818509122735486821[43] = 0;
   out_2818509122735486821[44] = 0;
   out_2818509122735486821[45] = 0;
   out_2818509122735486821[46] = 0;
   out_2818509122735486821[47] = 0;
   out_2818509122735486821[48] = 0;
   out_2818509122735486821[49] = 0;
   out_2818509122735486821[50] = 0;
   out_2818509122735486821[51] = 0;
   out_2818509122735486821[52] = 0;
   out_2818509122735486821[53] = 0;
}
void h_14(double *state, double *unused, double *out_622989207303169877) {
   out_622989207303169877[0] = state[6];
   out_622989207303169877[1] = state[7];
   out_622989207303169877[2] = state[8];
}
void H_14(double *state, double *unused, double *out_828881229241729579) {
   out_828881229241729579[0] = 0;
   out_828881229241729579[1] = 0;
   out_828881229241729579[2] = 0;
   out_828881229241729579[3] = 0;
   out_828881229241729579[4] = 0;
   out_828881229241729579[5] = 0;
   out_828881229241729579[6] = 1;
   out_828881229241729579[7] = 0;
   out_828881229241729579[8] = 0;
   out_828881229241729579[9] = 0;
   out_828881229241729579[10] = 0;
   out_828881229241729579[11] = 0;
   out_828881229241729579[12] = 0;
   out_828881229241729579[13] = 0;
   out_828881229241729579[14] = 0;
   out_828881229241729579[15] = 0;
   out_828881229241729579[16] = 0;
   out_828881229241729579[17] = 0;
   out_828881229241729579[18] = 0;
   out_828881229241729579[19] = 0;
   out_828881229241729579[20] = 0;
   out_828881229241729579[21] = 0;
   out_828881229241729579[22] = 0;
   out_828881229241729579[23] = 0;
   out_828881229241729579[24] = 0;
   out_828881229241729579[25] = 1;
   out_828881229241729579[26] = 0;
   out_828881229241729579[27] = 0;
   out_828881229241729579[28] = 0;
   out_828881229241729579[29] = 0;
   out_828881229241729579[30] = 0;
   out_828881229241729579[31] = 0;
   out_828881229241729579[32] = 0;
   out_828881229241729579[33] = 0;
   out_828881229241729579[34] = 0;
   out_828881229241729579[35] = 0;
   out_828881229241729579[36] = 0;
   out_828881229241729579[37] = 0;
   out_828881229241729579[38] = 0;
   out_828881229241729579[39] = 0;
   out_828881229241729579[40] = 0;
   out_828881229241729579[41] = 0;
   out_828881229241729579[42] = 0;
   out_828881229241729579[43] = 0;
   out_828881229241729579[44] = 1;
   out_828881229241729579[45] = 0;
   out_828881229241729579[46] = 0;
   out_828881229241729579[47] = 0;
   out_828881229241729579[48] = 0;
   out_828881229241729579[49] = 0;
   out_828881229241729579[50] = 0;
   out_828881229241729579[51] = 0;
   out_828881229241729579[52] = 0;
   out_828881229241729579[53] = 0;
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
void pose_err_fun(double *nom_x, double *delta_x, double *out_3055639861342664638) {
  err_fun(nom_x, delta_x, out_3055639861342664638);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_2233443736881945674) {
  inv_err_fun(nom_x, true_x, out_2233443736881945674);
}
void pose_H_mod_fun(double *state, double *out_5454317104155112741) {
  H_mod_fun(state, out_5454317104155112741);
}
void pose_f_fun(double *state, double dt, double *out_4996223981732405570) {
  f_fun(state,  dt, out_4996223981732405570);
}
void pose_F_fun(double *state, double dt, double *out_5891913618111355049) {
  F_fun(state,  dt, out_5891913618111355049);
}
void pose_h_4(double *state, double *unused, double *out_1832779376905477896) {
  h_4(state, unused, out_1832779376905477896);
}
void pose_H_4(double *state, double *unused, double *out_4792122085581214108) {
  H_4(state, unused, out_4792122085581214108);
}
void pose_h_10(double *state, double *unused, double *out_4235949127536262679) {
  h_10(state, unused, out_4235949127536262679);
}
void pose_H_10(double *state, double *unused, double *out_692750502701317014) {
  H_10(state, unused, out_692750502701317014);
}
void pose_h_13(double *state, double *unused, double *out_3117911153244826867) {
  h_13(state, unused, out_3117911153244826867);
}
void pose_H_13(double *state, double *unused, double *out_2818509122735486821) {
  H_13(state, unused, out_2818509122735486821);
}
void pose_h_14(double *state, double *unused, double *out_622989207303169877) {
  h_14(state, unused, out_622989207303169877);
}
void pose_H_14(double *state, double *unused, double *out_828881229241729579) {
  H_14(state, unused, out_828881229241729579);
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
