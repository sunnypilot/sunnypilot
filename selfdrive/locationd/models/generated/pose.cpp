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
void err_fun(double *nom_x, double *delta_x, double *out_4675916976957672131) {
   out_4675916976957672131[0] = delta_x[0] + nom_x[0];
   out_4675916976957672131[1] = delta_x[1] + nom_x[1];
   out_4675916976957672131[2] = delta_x[2] + nom_x[2];
   out_4675916976957672131[3] = delta_x[3] + nom_x[3];
   out_4675916976957672131[4] = delta_x[4] + nom_x[4];
   out_4675916976957672131[5] = delta_x[5] + nom_x[5];
   out_4675916976957672131[6] = delta_x[6] + nom_x[6];
   out_4675916976957672131[7] = delta_x[7] + nom_x[7];
   out_4675916976957672131[8] = delta_x[8] + nom_x[8];
   out_4675916976957672131[9] = delta_x[9] + nom_x[9];
   out_4675916976957672131[10] = delta_x[10] + nom_x[10];
   out_4675916976957672131[11] = delta_x[11] + nom_x[11];
   out_4675916976957672131[12] = delta_x[12] + nom_x[12];
   out_4675916976957672131[13] = delta_x[13] + nom_x[13];
   out_4675916976957672131[14] = delta_x[14] + nom_x[14];
   out_4675916976957672131[15] = delta_x[15] + nom_x[15];
   out_4675916976957672131[16] = delta_x[16] + nom_x[16];
   out_4675916976957672131[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_8932320044125663978) {
   out_8932320044125663978[0] = -nom_x[0] + true_x[0];
   out_8932320044125663978[1] = -nom_x[1] + true_x[1];
   out_8932320044125663978[2] = -nom_x[2] + true_x[2];
   out_8932320044125663978[3] = -nom_x[3] + true_x[3];
   out_8932320044125663978[4] = -nom_x[4] + true_x[4];
   out_8932320044125663978[5] = -nom_x[5] + true_x[5];
   out_8932320044125663978[6] = -nom_x[6] + true_x[6];
   out_8932320044125663978[7] = -nom_x[7] + true_x[7];
   out_8932320044125663978[8] = -nom_x[8] + true_x[8];
   out_8932320044125663978[9] = -nom_x[9] + true_x[9];
   out_8932320044125663978[10] = -nom_x[10] + true_x[10];
   out_8932320044125663978[11] = -nom_x[11] + true_x[11];
   out_8932320044125663978[12] = -nom_x[12] + true_x[12];
   out_8932320044125663978[13] = -nom_x[13] + true_x[13];
   out_8932320044125663978[14] = -nom_x[14] + true_x[14];
   out_8932320044125663978[15] = -nom_x[15] + true_x[15];
   out_8932320044125663978[16] = -nom_x[16] + true_x[16];
   out_8932320044125663978[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_8547583619141688255) {
   out_8547583619141688255[0] = 1.0;
   out_8547583619141688255[1] = 0.0;
   out_8547583619141688255[2] = 0.0;
   out_8547583619141688255[3] = 0.0;
   out_8547583619141688255[4] = 0.0;
   out_8547583619141688255[5] = 0.0;
   out_8547583619141688255[6] = 0.0;
   out_8547583619141688255[7] = 0.0;
   out_8547583619141688255[8] = 0.0;
   out_8547583619141688255[9] = 0.0;
   out_8547583619141688255[10] = 0.0;
   out_8547583619141688255[11] = 0.0;
   out_8547583619141688255[12] = 0.0;
   out_8547583619141688255[13] = 0.0;
   out_8547583619141688255[14] = 0.0;
   out_8547583619141688255[15] = 0.0;
   out_8547583619141688255[16] = 0.0;
   out_8547583619141688255[17] = 0.0;
   out_8547583619141688255[18] = 0.0;
   out_8547583619141688255[19] = 1.0;
   out_8547583619141688255[20] = 0.0;
   out_8547583619141688255[21] = 0.0;
   out_8547583619141688255[22] = 0.0;
   out_8547583619141688255[23] = 0.0;
   out_8547583619141688255[24] = 0.0;
   out_8547583619141688255[25] = 0.0;
   out_8547583619141688255[26] = 0.0;
   out_8547583619141688255[27] = 0.0;
   out_8547583619141688255[28] = 0.0;
   out_8547583619141688255[29] = 0.0;
   out_8547583619141688255[30] = 0.0;
   out_8547583619141688255[31] = 0.0;
   out_8547583619141688255[32] = 0.0;
   out_8547583619141688255[33] = 0.0;
   out_8547583619141688255[34] = 0.0;
   out_8547583619141688255[35] = 0.0;
   out_8547583619141688255[36] = 0.0;
   out_8547583619141688255[37] = 0.0;
   out_8547583619141688255[38] = 1.0;
   out_8547583619141688255[39] = 0.0;
   out_8547583619141688255[40] = 0.0;
   out_8547583619141688255[41] = 0.0;
   out_8547583619141688255[42] = 0.0;
   out_8547583619141688255[43] = 0.0;
   out_8547583619141688255[44] = 0.0;
   out_8547583619141688255[45] = 0.0;
   out_8547583619141688255[46] = 0.0;
   out_8547583619141688255[47] = 0.0;
   out_8547583619141688255[48] = 0.0;
   out_8547583619141688255[49] = 0.0;
   out_8547583619141688255[50] = 0.0;
   out_8547583619141688255[51] = 0.0;
   out_8547583619141688255[52] = 0.0;
   out_8547583619141688255[53] = 0.0;
   out_8547583619141688255[54] = 0.0;
   out_8547583619141688255[55] = 0.0;
   out_8547583619141688255[56] = 0.0;
   out_8547583619141688255[57] = 1.0;
   out_8547583619141688255[58] = 0.0;
   out_8547583619141688255[59] = 0.0;
   out_8547583619141688255[60] = 0.0;
   out_8547583619141688255[61] = 0.0;
   out_8547583619141688255[62] = 0.0;
   out_8547583619141688255[63] = 0.0;
   out_8547583619141688255[64] = 0.0;
   out_8547583619141688255[65] = 0.0;
   out_8547583619141688255[66] = 0.0;
   out_8547583619141688255[67] = 0.0;
   out_8547583619141688255[68] = 0.0;
   out_8547583619141688255[69] = 0.0;
   out_8547583619141688255[70] = 0.0;
   out_8547583619141688255[71] = 0.0;
   out_8547583619141688255[72] = 0.0;
   out_8547583619141688255[73] = 0.0;
   out_8547583619141688255[74] = 0.0;
   out_8547583619141688255[75] = 0.0;
   out_8547583619141688255[76] = 1.0;
   out_8547583619141688255[77] = 0.0;
   out_8547583619141688255[78] = 0.0;
   out_8547583619141688255[79] = 0.0;
   out_8547583619141688255[80] = 0.0;
   out_8547583619141688255[81] = 0.0;
   out_8547583619141688255[82] = 0.0;
   out_8547583619141688255[83] = 0.0;
   out_8547583619141688255[84] = 0.0;
   out_8547583619141688255[85] = 0.0;
   out_8547583619141688255[86] = 0.0;
   out_8547583619141688255[87] = 0.0;
   out_8547583619141688255[88] = 0.0;
   out_8547583619141688255[89] = 0.0;
   out_8547583619141688255[90] = 0.0;
   out_8547583619141688255[91] = 0.0;
   out_8547583619141688255[92] = 0.0;
   out_8547583619141688255[93] = 0.0;
   out_8547583619141688255[94] = 0.0;
   out_8547583619141688255[95] = 1.0;
   out_8547583619141688255[96] = 0.0;
   out_8547583619141688255[97] = 0.0;
   out_8547583619141688255[98] = 0.0;
   out_8547583619141688255[99] = 0.0;
   out_8547583619141688255[100] = 0.0;
   out_8547583619141688255[101] = 0.0;
   out_8547583619141688255[102] = 0.0;
   out_8547583619141688255[103] = 0.0;
   out_8547583619141688255[104] = 0.0;
   out_8547583619141688255[105] = 0.0;
   out_8547583619141688255[106] = 0.0;
   out_8547583619141688255[107] = 0.0;
   out_8547583619141688255[108] = 0.0;
   out_8547583619141688255[109] = 0.0;
   out_8547583619141688255[110] = 0.0;
   out_8547583619141688255[111] = 0.0;
   out_8547583619141688255[112] = 0.0;
   out_8547583619141688255[113] = 0.0;
   out_8547583619141688255[114] = 1.0;
   out_8547583619141688255[115] = 0.0;
   out_8547583619141688255[116] = 0.0;
   out_8547583619141688255[117] = 0.0;
   out_8547583619141688255[118] = 0.0;
   out_8547583619141688255[119] = 0.0;
   out_8547583619141688255[120] = 0.0;
   out_8547583619141688255[121] = 0.0;
   out_8547583619141688255[122] = 0.0;
   out_8547583619141688255[123] = 0.0;
   out_8547583619141688255[124] = 0.0;
   out_8547583619141688255[125] = 0.0;
   out_8547583619141688255[126] = 0.0;
   out_8547583619141688255[127] = 0.0;
   out_8547583619141688255[128] = 0.0;
   out_8547583619141688255[129] = 0.0;
   out_8547583619141688255[130] = 0.0;
   out_8547583619141688255[131] = 0.0;
   out_8547583619141688255[132] = 0.0;
   out_8547583619141688255[133] = 1.0;
   out_8547583619141688255[134] = 0.0;
   out_8547583619141688255[135] = 0.0;
   out_8547583619141688255[136] = 0.0;
   out_8547583619141688255[137] = 0.0;
   out_8547583619141688255[138] = 0.0;
   out_8547583619141688255[139] = 0.0;
   out_8547583619141688255[140] = 0.0;
   out_8547583619141688255[141] = 0.0;
   out_8547583619141688255[142] = 0.0;
   out_8547583619141688255[143] = 0.0;
   out_8547583619141688255[144] = 0.0;
   out_8547583619141688255[145] = 0.0;
   out_8547583619141688255[146] = 0.0;
   out_8547583619141688255[147] = 0.0;
   out_8547583619141688255[148] = 0.0;
   out_8547583619141688255[149] = 0.0;
   out_8547583619141688255[150] = 0.0;
   out_8547583619141688255[151] = 0.0;
   out_8547583619141688255[152] = 1.0;
   out_8547583619141688255[153] = 0.0;
   out_8547583619141688255[154] = 0.0;
   out_8547583619141688255[155] = 0.0;
   out_8547583619141688255[156] = 0.0;
   out_8547583619141688255[157] = 0.0;
   out_8547583619141688255[158] = 0.0;
   out_8547583619141688255[159] = 0.0;
   out_8547583619141688255[160] = 0.0;
   out_8547583619141688255[161] = 0.0;
   out_8547583619141688255[162] = 0.0;
   out_8547583619141688255[163] = 0.0;
   out_8547583619141688255[164] = 0.0;
   out_8547583619141688255[165] = 0.0;
   out_8547583619141688255[166] = 0.0;
   out_8547583619141688255[167] = 0.0;
   out_8547583619141688255[168] = 0.0;
   out_8547583619141688255[169] = 0.0;
   out_8547583619141688255[170] = 0.0;
   out_8547583619141688255[171] = 1.0;
   out_8547583619141688255[172] = 0.0;
   out_8547583619141688255[173] = 0.0;
   out_8547583619141688255[174] = 0.0;
   out_8547583619141688255[175] = 0.0;
   out_8547583619141688255[176] = 0.0;
   out_8547583619141688255[177] = 0.0;
   out_8547583619141688255[178] = 0.0;
   out_8547583619141688255[179] = 0.0;
   out_8547583619141688255[180] = 0.0;
   out_8547583619141688255[181] = 0.0;
   out_8547583619141688255[182] = 0.0;
   out_8547583619141688255[183] = 0.0;
   out_8547583619141688255[184] = 0.0;
   out_8547583619141688255[185] = 0.0;
   out_8547583619141688255[186] = 0.0;
   out_8547583619141688255[187] = 0.0;
   out_8547583619141688255[188] = 0.0;
   out_8547583619141688255[189] = 0.0;
   out_8547583619141688255[190] = 1.0;
   out_8547583619141688255[191] = 0.0;
   out_8547583619141688255[192] = 0.0;
   out_8547583619141688255[193] = 0.0;
   out_8547583619141688255[194] = 0.0;
   out_8547583619141688255[195] = 0.0;
   out_8547583619141688255[196] = 0.0;
   out_8547583619141688255[197] = 0.0;
   out_8547583619141688255[198] = 0.0;
   out_8547583619141688255[199] = 0.0;
   out_8547583619141688255[200] = 0.0;
   out_8547583619141688255[201] = 0.0;
   out_8547583619141688255[202] = 0.0;
   out_8547583619141688255[203] = 0.0;
   out_8547583619141688255[204] = 0.0;
   out_8547583619141688255[205] = 0.0;
   out_8547583619141688255[206] = 0.0;
   out_8547583619141688255[207] = 0.0;
   out_8547583619141688255[208] = 0.0;
   out_8547583619141688255[209] = 1.0;
   out_8547583619141688255[210] = 0.0;
   out_8547583619141688255[211] = 0.0;
   out_8547583619141688255[212] = 0.0;
   out_8547583619141688255[213] = 0.0;
   out_8547583619141688255[214] = 0.0;
   out_8547583619141688255[215] = 0.0;
   out_8547583619141688255[216] = 0.0;
   out_8547583619141688255[217] = 0.0;
   out_8547583619141688255[218] = 0.0;
   out_8547583619141688255[219] = 0.0;
   out_8547583619141688255[220] = 0.0;
   out_8547583619141688255[221] = 0.0;
   out_8547583619141688255[222] = 0.0;
   out_8547583619141688255[223] = 0.0;
   out_8547583619141688255[224] = 0.0;
   out_8547583619141688255[225] = 0.0;
   out_8547583619141688255[226] = 0.0;
   out_8547583619141688255[227] = 0.0;
   out_8547583619141688255[228] = 1.0;
   out_8547583619141688255[229] = 0.0;
   out_8547583619141688255[230] = 0.0;
   out_8547583619141688255[231] = 0.0;
   out_8547583619141688255[232] = 0.0;
   out_8547583619141688255[233] = 0.0;
   out_8547583619141688255[234] = 0.0;
   out_8547583619141688255[235] = 0.0;
   out_8547583619141688255[236] = 0.0;
   out_8547583619141688255[237] = 0.0;
   out_8547583619141688255[238] = 0.0;
   out_8547583619141688255[239] = 0.0;
   out_8547583619141688255[240] = 0.0;
   out_8547583619141688255[241] = 0.0;
   out_8547583619141688255[242] = 0.0;
   out_8547583619141688255[243] = 0.0;
   out_8547583619141688255[244] = 0.0;
   out_8547583619141688255[245] = 0.0;
   out_8547583619141688255[246] = 0.0;
   out_8547583619141688255[247] = 1.0;
   out_8547583619141688255[248] = 0.0;
   out_8547583619141688255[249] = 0.0;
   out_8547583619141688255[250] = 0.0;
   out_8547583619141688255[251] = 0.0;
   out_8547583619141688255[252] = 0.0;
   out_8547583619141688255[253] = 0.0;
   out_8547583619141688255[254] = 0.0;
   out_8547583619141688255[255] = 0.0;
   out_8547583619141688255[256] = 0.0;
   out_8547583619141688255[257] = 0.0;
   out_8547583619141688255[258] = 0.0;
   out_8547583619141688255[259] = 0.0;
   out_8547583619141688255[260] = 0.0;
   out_8547583619141688255[261] = 0.0;
   out_8547583619141688255[262] = 0.0;
   out_8547583619141688255[263] = 0.0;
   out_8547583619141688255[264] = 0.0;
   out_8547583619141688255[265] = 0.0;
   out_8547583619141688255[266] = 1.0;
   out_8547583619141688255[267] = 0.0;
   out_8547583619141688255[268] = 0.0;
   out_8547583619141688255[269] = 0.0;
   out_8547583619141688255[270] = 0.0;
   out_8547583619141688255[271] = 0.0;
   out_8547583619141688255[272] = 0.0;
   out_8547583619141688255[273] = 0.0;
   out_8547583619141688255[274] = 0.0;
   out_8547583619141688255[275] = 0.0;
   out_8547583619141688255[276] = 0.0;
   out_8547583619141688255[277] = 0.0;
   out_8547583619141688255[278] = 0.0;
   out_8547583619141688255[279] = 0.0;
   out_8547583619141688255[280] = 0.0;
   out_8547583619141688255[281] = 0.0;
   out_8547583619141688255[282] = 0.0;
   out_8547583619141688255[283] = 0.0;
   out_8547583619141688255[284] = 0.0;
   out_8547583619141688255[285] = 1.0;
   out_8547583619141688255[286] = 0.0;
   out_8547583619141688255[287] = 0.0;
   out_8547583619141688255[288] = 0.0;
   out_8547583619141688255[289] = 0.0;
   out_8547583619141688255[290] = 0.0;
   out_8547583619141688255[291] = 0.0;
   out_8547583619141688255[292] = 0.0;
   out_8547583619141688255[293] = 0.0;
   out_8547583619141688255[294] = 0.0;
   out_8547583619141688255[295] = 0.0;
   out_8547583619141688255[296] = 0.0;
   out_8547583619141688255[297] = 0.0;
   out_8547583619141688255[298] = 0.0;
   out_8547583619141688255[299] = 0.0;
   out_8547583619141688255[300] = 0.0;
   out_8547583619141688255[301] = 0.0;
   out_8547583619141688255[302] = 0.0;
   out_8547583619141688255[303] = 0.0;
   out_8547583619141688255[304] = 1.0;
   out_8547583619141688255[305] = 0.0;
   out_8547583619141688255[306] = 0.0;
   out_8547583619141688255[307] = 0.0;
   out_8547583619141688255[308] = 0.0;
   out_8547583619141688255[309] = 0.0;
   out_8547583619141688255[310] = 0.0;
   out_8547583619141688255[311] = 0.0;
   out_8547583619141688255[312] = 0.0;
   out_8547583619141688255[313] = 0.0;
   out_8547583619141688255[314] = 0.0;
   out_8547583619141688255[315] = 0.0;
   out_8547583619141688255[316] = 0.0;
   out_8547583619141688255[317] = 0.0;
   out_8547583619141688255[318] = 0.0;
   out_8547583619141688255[319] = 0.0;
   out_8547583619141688255[320] = 0.0;
   out_8547583619141688255[321] = 0.0;
   out_8547583619141688255[322] = 0.0;
   out_8547583619141688255[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_5173460647487908586) {
   out_5173460647487908586[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_5173460647487908586[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_5173460647487908586[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_5173460647487908586[3] = dt*state[12] + state[3];
   out_5173460647487908586[4] = dt*state[13] + state[4];
   out_5173460647487908586[5] = dt*state[14] + state[5];
   out_5173460647487908586[6] = state[6];
   out_5173460647487908586[7] = state[7];
   out_5173460647487908586[8] = state[8];
   out_5173460647487908586[9] = state[9];
   out_5173460647487908586[10] = state[10];
   out_5173460647487908586[11] = state[11];
   out_5173460647487908586[12] = state[12];
   out_5173460647487908586[13] = state[13];
   out_5173460647487908586[14] = state[14];
   out_5173460647487908586[15] = state[15];
   out_5173460647487908586[16] = state[16];
   out_5173460647487908586[17] = state[17];
}
void F_fun(double *state, double dt, double *out_7570643880185265565) {
   out_7570643880185265565[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_7570643880185265565[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_7570643880185265565[2] = 0;
   out_7570643880185265565[3] = 0;
   out_7570643880185265565[4] = 0;
   out_7570643880185265565[5] = 0;
   out_7570643880185265565[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_7570643880185265565[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_7570643880185265565[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_7570643880185265565[9] = 0;
   out_7570643880185265565[10] = 0;
   out_7570643880185265565[11] = 0;
   out_7570643880185265565[12] = 0;
   out_7570643880185265565[13] = 0;
   out_7570643880185265565[14] = 0;
   out_7570643880185265565[15] = 0;
   out_7570643880185265565[16] = 0;
   out_7570643880185265565[17] = 0;
   out_7570643880185265565[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_7570643880185265565[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_7570643880185265565[20] = 0;
   out_7570643880185265565[21] = 0;
   out_7570643880185265565[22] = 0;
   out_7570643880185265565[23] = 0;
   out_7570643880185265565[24] = 0;
   out_7570643880185265565[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_7570643880185265565[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_7570643880185265565[27] = 0;
   out_7570643880185265565[28] = 0;
   out_7570643880185265565[29] = 0;
   out_7570643880185265565[30] = 0;
   out_7570643880185265565[31] = 0;
   out_7570643880185265565[32] = 0;
   out_7570643880185265565[33] = 0;
   out_7570643880185265565[34] = 0;
   out_7570643880185265565[35] = 0;
   out_7570643880185265565[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_7570643880185265565[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_7570643880185265565[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_7570643880185265565[39] = 0;
   out_7570643880185265565[40] = 0;
   out_7570643880185265565[41] = 0;
   out_7570643880185265565[42] = 0;
   out_7570643880185265565[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_7570643880185265565[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_7570643880185265565[45] = 0;
   out_7570643880185265565[46] = 0;
   out_7570643880185265565[47] = 0;
   out_7570643880185265565[48] = 0;
   out_7570643880185265565[49] = 0;
   out_7570643880185265565[50] = 0;
   out_7570643880185265565[51] = 0;
   out_7570643880185265565[52] = 0;
   out_7570643880185265565[53] = 0;
   out_7570643880185265565[54] = 0;
   out_7570643880185265565[55] = 0;
   out_7570643880185265565[56] = 0;
   out_7570643880185265565[57] = 1;
   out_7570643880185265565[58] = 0;
   out_7570643880185265565[59] = 0;
   out_7570643880185265565[60] = 0;
   out_7570643880185265565[61] = 0;
   out_7570643880185265565[62] = 0;
   out_7570643880185265565[63] = 0;
   out_7570643880185265565[64] = 0;
   out_7570643880185265565[65] = 0;
   out_7570643880185265565[66] = dt;
   out_7570643880185265565[67] = 0;
   out_7570643880185265565[68] = 0;
   out_7570643880185265565[69] = 0;
   out_7570643880185265565[70] = 0;
   out_7570643880185265565[71] = 0;
   out_7570643880185265565[72] = 0;
   out_7570643880185265565[73] = 0;
   out_7570643880185265565[74] = 0;
   out_7570643880185265565[75] = 0;
   out_7570643880185265565[76] = 1;
   out_7570643880185265565[77] = 0;
   out_7570643880185265565[78] = 0;
   out_7570643880185265565[79] = 0;
   out_7570643880185265565[80] = 0;
   out_7570643880185265565[81] = 0;
   out_7570643880185265565[82] = 0;
   out_7570643880185265565[83] = 0;
   out_7570643880185265565[84] = 0;
   out_7570643880185265565[85] = dt;
   out_7570643880185265565[86] = 0;
   out_7570643880185265565[87] = 0;
   out_7570643880185265565[88] = 0;
   out_7570643880185265565[89] = 0;
   out_7570643880185265565[90] = 0;
   out_7570643880185265565[91] = 0;
   out_7570643880185265565[92] = 0;
   out_7570643880185265565[93] = 0;
   out_7570643880185265565[94] = 0;
   out_7570643880185265565[95] = 1;
   out_7570643880185265565[96] = 0;
   out_7570643880185265565[97] = 0;
   out_7570643880185265565[98] = 0;
   out_7570643880185265565[99] = 0;
   out_7570643880185265565[100] = 0;
   out_7570643880185265565[101] = 0;
   out_7570643880185265565[102] = 0;
   out_7570643880185265565[103] = 0;
   out_7570643880185265565[104] = dt;
   out_7570643880185265565[105] = 0;
   out_7570643880185265565[106] = 0;
   out_7570643880185265565[107] = 0;
   out_7570643880185265565[108] = 0;
   out_7570643880185265565[109] = 0;
   out_7570643880185265565[110] = 0;
   out_7570643880185265565[111] = 0;
   out_7570643880185265565[112] = 0;
   out_7570643880185265565[113] = 0;
   out_7570643880185265565[114] = 1;
   out_7570643880185265565[115] = 0;
   out_7570643880185265565[116] = 0;
   out_7570643880185265565[117] = 0;
   out_7570643880185265565[118] = 0;
   out_7570643880185265565[119] = 0;
   out_7570643880185265565[120] = 0;
   out_7570643880185265565[121] = 0;
   out_7570643880185265565[122] = 0;
   out_7570643880185265565[123] = 0;
   out_7570643880185265565[124] = 0;
   out_7570643880185265565[125] = 0;
   out_7570643880185265565[126] = 0;
   out_7570643880185265565[127] = 0;
   out_7570643880185265565[128] = 0;
   out_7570643880185265565[129] = 0;
   out_7570643880185265565[130] = 0;
   out_7570643880185265565[131] = 0;
   out_7570643880185265565[132] = 0;
   out_7570643880185265565[133] = 1;
   out_7570643880185265565[134] = 0;
   out_7570643880185265565[135] = 0;
   out_7570643880185265565[136] = 0;
   out_7570643880185265565[137] = 0;
   out_7570643880185265565[138] = 0;
   out_7570643880185265565[139] = 0;
   out_7570643880185265565[140] = 0;
   out_7570643880185265565[141] = 0;
   out_7570643880185265565[142] = 0;
   out_7570643880185265565[143] = 0;
   out_7570643880185265565[144] = 0;
   out_7570643880185265565[145] = 0;
   out_7570643880185265565[146] = 0;
   out_7570643880185265565[147] = 0;
   out_7570643880185265565[148] = 0;
   out_7570643880185265565[149] = 0;
   out_7570643880185265565[150] = 0;
   out_7570643880185265565[151] = 0;
   out_7570643880185265565[152] = 1;
   out_7570643880185265565[153] = 0;
   out_7570643880185265565[154] = 0;
   out_7570643880185265565[155] = 0;
   out_7570643880185265565[156] = 0;
   out_7570643880185265565[157] = 0;
   out_7570643880185265565[158] = 0;
   out_7570643880185265565[159] = 0;
   out_7570643880185265565[160] = 0;
   out_7570643880185265565[161] = 0;
   out_7570643880185265565[162] = 0;
   out_7570643880185265565[163] = 0;
   out_7570643880185265565[164] = 0;
   out_7570643880185265565[165] = 0;
   out_7570643880185265565[166] = 0;
   out_7570643880185265565[167] = 0;
   out_7570643880185265565[168] = 0;
   out_7570643880185265565[169] = 0;
   out_7570643880185265565[170] = 0;
   out_7570643880185265565[171] = 1;
   out_7570643880185265565[172] = 0;
   out_7570643880185265565[173] = 0;
   out_7570643880185265565[174] = 0;
   out_7570643880185265565[175] = 0;
   out_7570643880185265565[176] = 0;
   out_7570643880185265565[177] = 0;
   out_7570643880185265565[178] = 0;
   out_7570643880185265565[179] = 0;
   out_7570643880185265565[180] = 0;
   out_7570643880185265565[181] = 0;
   out_7570643880185265565[182] = 0;
   out_7570643880185265565[183] = 0;
   out_7570643880185265565[184] = 0;
   out_7570643880185265565[185] = 0;
   out_7570643880185265565[186] = 0;
   out_7570643880185265565[187] = 0;
   out_7570643880185265565[188] = 0;
   out_7570643880185265565[189] = 0;
   out_7570643880185265565[190] = 1;
   out_7570643880185265565[191] = 0;
   out_7570643880185265565[192] = 0;
   out_7570643880185265565[193] = 0;
   out_7570643880185265565[194] = 0;
   out_7570643880185265565[195] = 0;
   out_7570643880185265565[196] = 0;
   out_7570643880185265565[197] = 0;
   out_7570643880185265565[198] = 0;
   out_7570643880185265565[199] = 0;
   out_7570643880185265565[200] = 0;
   out_7570643880185265565[201] = 0;
   out_7570643880185265565[202] = 0;
   out_7570643880185265565[203] = 0;
   out_7570643880185265565[204] = 0;
   out_7570643880185265565[205] = 0;
   out_7570643880185265565[206] = 0;
   out_7570643880185265565[207] = 0;
   out_7570643880185265565[208] = 0;
   out_7570643880185265565[209] = 1;
   out_7570643880185265565[210] = 0;
   out_7570643880185265565[211] = 0;
   out_7570643880185265565[212] = 0;
   out_7570643880185265565[213] = 0;
   out_7570643880185265565[214] = 0;
   out_7570643880185265565[215] = 0;
   out_7570643880185265565[216] = 0;
   out_7570643880185265565[217] = 0;
   out_7570643880185265565[218] = 0;
   out_7570643880185265565[219] = 0;
   out_7570643880185265565[220] = 0;
   out_7570643880185265565[221] = 0;
   out_7570643880185265565[222] = 0;
   out_7570643880185265565[223] = 0;
   out_7570643880185265565[224] = 0;
   out_7570643880185265565[225] = 0;
   out_7570643880185265565[226] = 0;
   out_7570643880185265565[227] = 0;
   out_7570643880185265565[228] = 1;
   out_7570643880185265565[229] = 0;
   out_7570643880185265565[230] = 0;
   out_7570643880185265565[231] = 0;
   out_7570643880185265565[232] = 0;
   out_7570643880185265565[233] = 0;
   out_7570643880185265565[234] = 0;
   out_7570643880185265565[235] = 0;
   out_7570643880185265565[236] = 0;
   out_7570643880185265565[237] = 0;
   out_7570643880185265565[238] = 0;
   out_7570643880185265565[239] = 0;
   out_7570643880185265565[240] = 0;
   out_7570643880185265565[241] = 0;
   out_7570643880185265565[242] = 0;
   out_7570643880185265565[243] = 0;
   out_7570643880185265565[244] = 0;
   out_7570643880185265565[245] = 0;
   out_7570643880185265565[246] = 0;
   out_7570643880185265565[247] = 1;
   out_7570643880185265565[248] = 0;
   out_7570643880185265565[249] = 0;
   out_7570643880185265565[250] = 0;
   out_7570643880185265565[251] = 0;
   out_7570643880185265565[252] = 0;
   out_7570643880185265565[253] = 0;
   out_7570643880185265565[254] = 0;
   out_7570643880185265565[255] = 0;
   out_7570643880185265565[256] = 0;
   out_7570643880185265565[257] = 0;
   out_7570643880185265565[258] = 0;
   out_7570643880185265565[259] = 0;
   out_7570643880185265565[260] = 0;
   out_7570643880185265565[261] = 0;
   out_7570643880185265565[262] = 0;
   out_7570643880185265565[263] = 0;
   out_7570643880185265565[264] = 0;
   out_7570643880185265565[265] = 0;
   out_7570643880185265565[266] = 1;
   out_7570643880185265565[267] = 0;
   out_7570643880185265565[268] = 0;
   out_7570643880185265565[269] = 0;
   out_7570643880185265565[270] = 0;
   out_7570643880185265565[271] = 0;
   out_7570643880185265565[272] = 0;
   out_7570643880185265565[273] = 0;
   out_7570643880185265565[274] = 0;
   out_7570643880185265565[275] = 0;
   out_7570643880185265565[276] = 0;
   out_7570643880185265565[277] = 0;
   out_7570643880185265565[278] = 0;
   out_7570643880185265565[279] = 0;
   out_7570643880185265565[280] = 0;
   out_7570643880185265565[281] = 0;
   out_7570643880185265565[282] = 0;
   out_7570643880185265565[283] = 0;
   out_7570643880185265565[284] = 0;
   out_7570643880185265565[285] = 1;
   out_7570643880185265565[286] = 0;
   out_7570643880185265565[287] = 0;
   out_7570643880185265565[288] = 0;
   out_7570643880185265565[289] = 0;
   out_7570643880185265565[290] = 0;
   out_7570643880185265565[291] = 0;
   out_7570643880185265565[292] = 0;
   out_7570643880185265565[293] = 0;
   out_7570643880185265565[294] = 0;
   out_7570643880185265565[295] = 0;
   out_7570643880185265565[296] = 0;
   out_7570643880185265565[297] = 0;
   out_7570643880185265565[298] = 0;
   out_7570643880185265565[299] = 0;
   out_7570643880185265565[300] = 0;
   out_7570643880185265565[301] = 0;
   out_7570643880185265565[302] = 0;
   out_7570643880185265565[303] = 0;
   out_7570643880185265565[304] = 1;
   out_7570643880185265565[305] = 0;
   out_7570643880185265565[306] = 0;
   out_7570643880185265565[307] = 0;
   out_7570643880185265565[308] = 0;
   out_7570643880185265565[309] = 0;
   out_7570643880185265565[310] = 0;
   out_7570643880185265565[311] = 0;
   out_7570643880185265565[312] = 0;
   out_7570643880185265565[313] = 0;
   out_7570643880185265565[314] = 0;
   out_7570643880185265565[315] = 0;
   out_7570643880185265565[316] = 0;
   out_7570643880185265565[317] = 0;
   out_7570643880185265565[318] = 0;
   out_7570643880185265565[319] = 0;
   out_7570643880185265565[320] = 0;
   out_7570643880185265565[321] = 0;
   out_7570643880185265565[322] = 0;
   out_7570643880185265565[323] = 1;
}
void h_4(double *state, double *unused, double *out_680141703095616266) {
   out_680141703095616266[0] = state[6] + state[9];
   out_680141703095616266[1] = state[7] + state[10];
   out_680141703095616266[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_318144395399465431) {
   out_318144395399465431[0] = 0;
   out_318144395399465431[1] = 0;
   out_318144395399465431[2] = 0;
   out_318144395399465431[3] = 0;
   out_318144395399465431[4] = 0;
   out_318144395399465431[5] = 0;
   out_318144395399465431[6] = 1;
   out_318144395399465431[7] = 0;
   out_318144395399465431[8] = 0;
   out_318144395399465431[9] = 1;
   out_318144395399465431[10] = 0;
   out_318144395399465431[11] = 0;
   out_318144395399465431[12] = 0;
   out_318144395399465431[13] = 0;
   out_318144395399465431[14] = 0;
   out_318144395399465431[15] = 0;
   out_318144395399465431[16] = 0;
   out_318144395399465431[17] = 0;
   out_318144395399465431[18] = 0;
   out_318144395399465431[19] = 0;
   out_318144395399465431[20] = 0;
   out_318144395399465431[21] = 0;
   out_318144395399465431[22] = 0;
   out_318144395399465431[23] = 0;
   out_318144395399465431[24] = 0;
   out_318144395399465431[25] = 1;
   out_318144395399465431[26] = 0;
   out_318144395399465431[27] = 0;
   out_318144395399465431[28] = 1;
   out_318144395399465431[29] = 0;
   out_318144395399465431[30] = 0;
   out_318144395399465431[31] = 0;
   out_318144395399465431[32] = 0;
   out_318144395399465431[33] = 0;
   out_318144395399465431[34] = 0;
   out_318144395399465431[35] = 0;
   out_318144395399465431[36] = 0;
   out_318144395399465431[37] = 0;
   out_318144395399465431[38] = 0;
   out_318144395399465431[39] = 0;
   out_318144395399465431[40] = 0;
   out_318144395399465431[41] = 0;
   out_318144395399465431[42] = 0;
   out_318144395399465431[43] = 0;
   out_318144395399465431[44] = 1;
   out_318144395399465431[45] = 0;
   out_318144395399465431[46] = 0;
   out_318144395399465431[47] = 1;
   out_318144395399465431[48] = 0;
   out_318144395399465431[49] = 0;
   out_318144395399465431[50] = 0;
   out_318144395399465431[51] = 0;
   out_318144395399465431[52] = 0;
   out_318144395399465431[53] = 0;
}
void h_10(double *state, double *unused, double *out_8746364681564070660) {
   out_8746364681564070660[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_8746364681564070660[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_8746364681564070660[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_4156082973223883983) {
   out_4156082973223883983[0] = 0;
   out_4156082973223883983[1] = 9.8100000000000005*cos(state[1]);
   out_4156082973223883983[2] = 0;
   out_4156082973223883983[3] = 0;
   out_4156082973223883983[4] = -state[8];
   out_4156082973223883983[5] = state[7];
   out_4156082973223883983[6] = 0;
   out_4156082973223883983[7] = state[5];
   out_4156082973223883983[8] = -state[4];
   out_4156082973223883983[9] = 0;
   out_4156082973223883983[10] = 0;
   out_4156082973223883983[11] = 0;
   out_4156082973223883983[12] = 1;
   out_4156082973223883983[13] = 0;
   out_4156082973223883983[14] = 0;
   out_4156082973223883983[15] = 1;
   out_4156082973223883983[16] = 0;
   out_4156082973223883983[17] = 0;
   out_4156082973223883983[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_4156082973223883983[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_4156082973223883983[20] = 0;
   out_4156082973223883983[21] = state[8];
   out_4156082973223883983[22] = 0;
   out_4156082973223883983[23] = -state[6];
   out_4156082973223883983[24] = -state[5];
   out_4156082973223883983[25] = 0;
   out_4156082973223883983[26] = state[3];
   out_4156082973223883983[27] = 0;
   out_4156082973223883983[28] = 0;
   out_4156082973223883983[29] = 0;
   out_4156082973223883983[30] = 0;
   out_4156082973223883983[31] = 1;
   out_4156082973223883983[32] = 0;
   out_4156082973223883983[33] = 0;
   out_4156082973223883983[34] = 1;
   out_4156082973223883983[35] = 0;
   out_4156082973223883983[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_4156082973223883983[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_4156082973223883983[38] = 0;
   out_4156082973223883983[39] = -state[7];
   out_4156082973223883983[40] = state[6];
   out_4156082973223883983[41] = 0;
   out_4156082973223883983[42] = state[4];
   out_4156082973223883983[43] = -state[3];
   out_4156082973223883983[44] = 0;
   out_4156082973223883983[45] = 0;
   out_4156082973223883983[46] = 0;
   out_4156082973223883983[47] = 0;
   out_4156082973223883983[48] = 0;
   out_4156082973223883983[49] = 0;
   out_4156082973223883983[50] = 1;
   out_4156082973223883983[51] = 0;
   out_4156082973223883983[52] = 0;
   out_4156082973223883983[53] = 1;
}
void h_13(double *state, double *unused, double *out_5669417444424150126) {
   out_5669417444424150126[0] = state[3];
   out_5669417444424150126[1] = state[4];
   out_5669417444424150126[2] = state[5];
}
void H_13(double *state, double *unused, double *out_7292486812917235498) {
   out_7292486812917235498[0] = 0;
   out_7292486812917235498[1] = 0;
   out_7292486812917235498[2] = 0;
   out_7292486812917235498[3] = 1;
   out_7292486812917235498[4] = 0;
   out_7292486812917235498[5] = 0;
   out_7292486812917235498[6] = 0;
   out_7292486812917235498[7] = 0;
   out_7292486812917235498[8] = 0;
   out_7292486812917235498[9] = 0;
   out_7292486812917235498[10] = 0;
   out_7292486812917235498[11] = 0;
   out_7292486812917235498[12] = 0;
   out_7292486812917235498[13] = 0;
   out_7292486812917235498[14] = 0;
   out_7292486812917235498[15] = 0;
   out_7292486812917235498[16] = 0;
   out_7292486812917235498[17] = 0;
   out_7292486812917235498[18] = 0;
   out_7292486812917235498[19] = 0;
   out_7292486812917235498[20] = 0;
   out_7292486812917235498[21] = 0;
   out_7292486812917235498[22] = 1;
   out_7292486812917235498[23] = 0;
   out_7292486812917235498[24] = 0;
   out_7292486812917235498[25] = 0;
   out_7292486812917235498[26] = 0;
   out_7292486812917235498[27] = 0;
   out_7292486812917235498[28] = 0;
   out_7292486812917235498[29] = 0;
   out_7292486812917235498[30] = 0;
   out_7292486812917235498[31] = 0;
   out_7292486812917235498[32] = 0;
   out_7292486812917235498[33] = 0;
   out_7292486812917235498[34] = 0;
   out_7292486812917235498[35] = 0;
   out_7292486812917235498[36] = 0;
   out_7292486812917235498[37] = 0;
   out_7292486812917235498[38] = 0;
   out_7292486812917235498[39] = 0;
   out_7292486812917235498[40] = 0;
   out_7292486812917235498[41] = 1;
   out_7292486812917235498[42] = 0;
   out_7292486812917235498[43] = 0;
   out_7292486812917235498[44] = 0;
   out_7292486812917235498[45] = 0;
   out_7292486812917235498[46] = 0;
   out_7292486812917235498[47] = 0;
   out_7292486812917235498[48] = 0;
   out_7292486812917235498[49] = 0;
   out_7292486812917235498[50] = 0;
   out_7292486812917235498[51] = 0;
   out_7292486812917235498[52] = 0;
   out_7292486812917235498[53] = 0;
}
void h_14(double *state, double *unused, double *out_4745054529679966551) {
   out_4745054529679966551[0] = state[6];
   out_4745054529679966551[1] = state[7];
   out_4745054529679966551[2] = state[8];
}
void H_14(double *state, double *unused, double *out_3645096460940019098) {
   out_3645096460940019098[0] = 0;
   out_3645096460940019098[1] = 0;
   out_3645096460940019098[2] = 0;
   out_3645096460940019098[3] = 0;
   out_3645096460940019098[4] = 0;
   out_3645096460940019098[5] = 0;
   out_3645096460940019098[6] = 1;
   out_3645096460940019098[7] = 0;
   out_3645096460940019098[8] = 0;
   out_3645096460940019098[9] = 0;
   out_3645096460940019098[10] = 0;
   out_3645096460940019098[11] = 0;
   out_3645096460940019098[12] = 0;
   out_3645096460940019098[13] = 0;
   out_3645096460940019098[14] = 0;
   out_3645096460940019098[15] = 0;
   out_3645096460940019098[16] = 0;
   out_3645096460940019098[17] = 0;
   out_3645096460940019098[18] = 0;
   out_3645096460940019098[19] = 0;
   out_3645096460940019098[20] = 0;
   out_3645096460940019098[21] = 0;
   out_3645096460940019098[22] = 0;
   out_3645096460940019098[23] = 0;
   out_3645096460940019098[24] = 0;
   out_3645096460940019098[25] = 1;
   out_3645096460940019098[26] = 0;
   out_3645096460940019098[27] = 0;
   out_3645096460940019098[28] = 0;
   out_3645096460940019098[29] = 0;
   out_3645096460940019098[30] = 0;
   out_3645096460940019098[31] = 0;
   out_3645096460940019098[32] = 0;
   out_3645096460940019098[33] = 0;
   out_3645096460940019098[34] = 0;
   out_3645096460940019098[35] = 0;
   out_3645096460940019098[36] = 0;
   out_3645096460940019098[37] = 0;
   out_3645096460940019098[38] = 0;
   out_3645096460940019098[39] = 0;
   out_3645096460940019098[40] = 0;
   out_3645096460940019098[41] = 0;
   out_3645096460940019098[42] = 0;
   out_3645096460940019098[43] = 0;
   out_3645096460940019098[44] = 1;
   out_3645096460940019098[45] = 0;
   out_3645096460940019098[46] = 0;
   out_3645096460940019098[47] = 0;
   out_3645096460940019098[48] = 0;
   out_3645096460940019098[49] = 0;
   out_3645096460940019098[50] = 0;
   out_3645096460940019098[51] = 0;
   out_3645096460940019098[52] = 0;
   out_3645096460940019098[53] = 0;
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
void pose_err_fun(double *nom_x, double *delta_x, double *out_4675916976957672131) {
  err_fun(nom_x, delta_x, out_4675916976957672131);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_8932320044125663978) {
  inv_err_fun(nom_x, true_x, out_8932320044125663978);
}
void pose_H_mod_fun(double *state, double *out_8547583619141688255) {
  H_mod_fun(state, out_8547583619141688255);
}
void pose_f_fun(double *state, double dt, double *out_5173460647487908586) {
  f_fun(state,  dt, out_5173460647487908586);
}
void pose_F_fun(double *state, double dt, double *out_7570643880185265565) {
  F_fun(state,  dt, out_7570643880185265565);
}
void pose_h_4(double *state, double *unused, double *out_680141703095616266) {
  h_4(state, unused, out_680141703095616266);
}
void pose_H_4(double *state, double *unused, double *out_318144395399465431) {
  H_4(state, unused, out_318144395399465431);
}
void pose_h_10(double *state, double *unused, double *out_8746364681564070660) {
  h_10(state, unused, out_8746364681564070660);
}
void pose_H_10(double *state, double *unused, double *out_4156082973223883983) {
  H_10(state, unused, out_4156082973223883983);
}
void pose_h_13(double *state, double *unused, double *out_5669417444424150126) {
  h_13(state, unused, out_5669417444424150126);
}
void pose_H_13(double *state, double *unused, double *out_7292486812917235498) {
  H_13(state, unused, out_7292486812917235498);
}
void pose_h_14(double *state, double *unused, double *out_4745054529679966551) {
  h_14(state, unused, out_4745054529679966551);
}
void pose_H_14(double *state, double *unused, double *out_3645096460940019098) {
  H_14(state, unused, out_3645096460940019098);
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
