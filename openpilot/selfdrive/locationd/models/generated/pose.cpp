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
void err_fun(double *nom_x, double *delta_x, double *out_7491504487925958906) {
   out_7491504487925958906[0] = delta_x[0] + nom_x[0];
   out_7491504487925958906[1] = delta_x[1] + nom_x[1];
   out_7491504487925958906[2] = delta_x[2] + nom_x[2];
   out_7491504487925958906[3] = delta_x[3] + nom_x[3];
   out_7491504487925958906[4] = delta_x[4] + nom_x[4];
   out_7491504487925958906[5] = delta_x[5] + nom_x[5];
   out_7491504487925958906[6] = delta_x[6] + nom_x[6];
   out_7491504487925958906[7] = delta_x[7] + nom_x[7];
   out_7491504487925958906[8] = delta_x[8] + nom_x[8];
   out_7491504487925958906[9] = delta_x[9] + nom_x[9];
   out_7491504487925958906[10] = delta_x[10] + nom_x[10];
   out_7491504487925958906[11] = delta_x[11] + nom_x[11];
   out_7491504487925958906[12] = delta_x[12] + nom_x[12];
   out_7491504487925958906[13] = delta_x[13] + nom_x[13];
   out_7491504487925958906[14] = delta_x[14] + nom_x[14];
   out_7491504487925958906[15] = delta_x[15] + nom_x[15];
   out_7491504487925958906[16] = delta_x[16] + nom_x[16];
   out_7491504487925958906[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_8173082431785614969) {
   out_8173082431785614969[0] = -nom_x[0] + true_x[0];
   out_8173082431785614969[1] = -nom_x[1] + true_x[1];
   out_8173082431785614969[2] = -nom_x[2] + true_x[2];
   out_8173082431785614969[3] = -nom_x[3] + true_x[3];
   out_8173082431785614969[4] = -nom_x[4] + true_x[4];
   out_8173082431785614969[5] = -nom_x[5] + true_x[5];
   out_8173082431785614969[6] = -nom_x[6] + true_x[6];
   out_8173082431785614969[7] = -nom_x[7] + true_x[7];
   out_8173082431785614969[8] = -nom_x[8] + true_x[8];
   out_8173082431785614969[9] = -nom_x[9] + true_x[9];
   out_8173082431785614969[10] = -nom_x[10] + true_x[10];
   out_8173082431785614969[11] = -nom_x[11] + true_x[11];
   out_8173082431785614969[12] = -nom_x[12] + true_x[12];
   out_8173082431785614969[13] = -nom_x[13] + true_x[13];
   out_8173082431785614969[14] = -nom_x[14] + true_x[14];
   out_8173082431785614969[15] = -nom_x[15] + true_x[15];
   out_8173082431785614969[16] = -nom_x[16] + true_x[16];
   out_8173082431785614969[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_3955896825213980969) {
   out_3955896825213980969[0] = 1.0;
   out_3955896825213980969[1] = 0.0;
   out_3955896825213980969[2] = 0.0;
   out_3955896825213980969[3] = 0.0;
   out_3955896825213980969[4] = 0.0;
   out_3955896825213980969[5] = 0.0;
   out_3955896825213980969[6] = 0.0;
   out_3955896825213980969[7] = 0.0;
   out_3955896825213980969[8] = 0.0;
   out_3955896825213980969[9] = 0.0;
   out_3955896825213980969[10] = 0.0;
   out_3955896825213980969[11] = 0.0;
   out_3955896825213980969[12] = 0.0;
   out_3955896825213980969[13] = 0.0;
   out_3955896825213980969[14] = 0.0;
   out_3955896825213980969[15] = 0.0;
   out_3955896825213980969[16] = 0.0;
   out_3955896825213980969[17] = 0.0;
   out_3955896825213980969[18] = 0.0;
   out_3955896825213980969[19] = 1.0;
   out_3955896825213980969[20] = 0.0;
   out_3955896825213980969[21] = 0.0;
   out_3955896825213980969[22] = 0.0;
   out_3955896825213980969[23] = 0.0;
   out_3955896825213980969[24] = 0.0;
   out_3955896825213980969[25] = 0.0;
   out_3955896825213980969[26] = 0.0;
   out_3955896825213980969[27] = 0.0;
   out_3955896825213980969[28] = 0.0;
   out_3955896825213980969[29] = 0.0;
   out_3955896825213980969[30] = 0.0;
   out_3955896825213980969[31] = 0.0;
   out_3955896825213980969[32] = 0.0;
   out_3955896825213980969[33] = 0.0;
   out_3955896825213980969[34] = 0.0;
   out_3955896825213980969[35] = 0.0;
   out_3955896825213980969[36] = 0.0;
   out_3955896825213980969[37] = 0.0;
   out_3955896825213980969[38] = 1.0;
   out_3955896825213980969[39] = 0.0;
   out_3955896825213980969[40] = 0.0;
   out_3955896825213980969[41] = 0.0;
   out_3955896825213980969[42] = 0.0;
   out_3955896825213980969[43] = 0.0;
   out_3955896825213980969[44] = 0.0;
   out_3955896825213980969[45] = 0.0;
   out_3955896825213980969[46] = 0.0;
   out_3955896825213980969[47] = 0.0;
   out_3955896825213980969[48] = 0.0;
   out_3955896825213980969[49] = 0.0;
   out_3955896825213980969[50] = 0.0;
   out_3955896825213980969[51] = 0.0;
   out_3955896825213980969[52] = 0.0;
   out_3955896825213980969[53] = 0.0;
   out_3955896825213980969[54] = 0.0;
   out_3955896825213980969[55] = 0.0;
   out_3955896825213980969[56] = 0.0;
   out_3955896825213980969[57] = 1.0;
   out_3955896825213980969[58] = 0.0;
   out_3955896825213980969[59] = 0.0;
   out_3955896825213980969[60] = 0.0;
   out_3955896825213980969[61] = 0.0;
   out_3955896825213980969[62] = 0.0;
   out_3955896825213980969[63] = 0.0;
   out_3955896825213980969[64] = 0.0;
   out_3955896825213980969[65] = 0.0;
   out_3955896825213980969[66] = 0.0;
   out_3955896825213980969[67] = 0.0;
   out_3955896825213980969[68] = 0.0;
   out_3955896825213980969[69] = 0.0;
   out_3955896825213980969[70] = 0.0;
   out_3955896825213980969[71] = 0.0;
   out_3955896825213980969[72] = 0.0;
   out_3955896825213980969[73] = 0.0;
   out_3955896825213980969[74] = 0.0;
   out_3955896825213980969[75] = 0.0;
   out_3955896825213980969[76] = 1.0;
   out_3955896825213980969[77] = 0.0;
   out_3955896825213980969[78] = 0.0;
   out_3955896825213980969[79] = 0.0;
   out_3955896825213980969[80] = 0.0;
   out_3955896825213980969[81] = 0.0;
   out_3955896825213980969[82] = 0.0;
   out_3955896825213980969[83] = 0.0;
   out_3955896825213980969[84] = 0.0;
   out_3955896825213980969[85] = 0.0;
   out_3955896825213980969[86] = 0.0;
   out_3955896825213980969[87] = 0.0;
   out_3955896825213980969[88] = 0.0;
   out_3955896825213980969[89] = 0.0;
   out_3955896825213980969[90] = 0.0;
   out_3955896825213980969[91] = 0.0;
   out_3955896825213980969[92] = 0.0;
   out_3955896825213980969[93] = 0.0;
   out_3955896825213980969[94] = 0.0;
   out_3955896825213980969[95] = 1.0;
   out_3955896825213980969[96] = 0.0;
   out_3955896825213980969[97] = 0.0;
   out_3955896825213980969[98] = 0.0;
   out_3955896825213980969[99] = 0.0;
   out_3955896825213980969[100] = 0.0;
   out_3955896825213980969[101] = 0.0;
   out_3955896825213980969[102] = 0.0;
   out_3955896825213980969[103] = 0.0;
   out_3955896825213980969[104] = 0.0;
   out_3955896825213980969[105] = 0.0;
   out_3955896825213980969[106] = 0.0;
   out_3955896825213980969[107] = 0.0;
   out_3955896825213980969[108] = 0.0;
   out_3955896825213980969[109] = 0.0;
   out_3955896825213980969[110] = 0.0;
   out_3955896825213980969[111] = 0.0;
   out_3955896825213980969[112] = 0.0;
   out_3955896825213980969[113] = 0.0;
   out_3955896825213980969[114] = 1.0;
   out_3955896825213980969[115] = 0.0;
   out_3955896825213980969[116] = 0.0;
   out_3955896825213980969[117] = 0.0;
   out_3955896825213980969[118] = 0.0;
   out_3955896825213980969[119] = 0.0;
   out_3955896825213980969[120] = 0.0;
   out_3955896825213980969[121] = 0.0;
   out_3955896825213980969[122] = 0.0;
   out_3955896825213980969[123] = 0.0;
   out_3955896825213980969[124] = 0.0;
   out_3955896825213980969[125] = 0.0;
   out_3955896825213980969[126] = 0.0;
   out_3955896825213980969[127] = 0.0;
   out_3955896825213980969[128] = 0.0;
   out_3955896825213980969[129] = 0.0;
   out_3955896825213980969[130] = 0.0;
   out_3955896825213980969[131] = 0.0;
   out_3955896825213980969[132] = 0.0;
   out_3955896825213980969[133] = 1.0;
   out_3955896825213980969[134] = 0.0;
   out_3955896825213980969[135] = 0.0;
   out_3955896825213980969[136] = 0.0;
   out_3955896825213980969[137] = 0.0;
   out_3955896825213980969[138] = 0.0;
   out_3955896825213980969[139] = 0.0;
   out_3955896825213980969[140] = 0.0;
   out_3955896825213980969[141] = 0.0;
   out_3955896825213980969[142] = 0.0;
   out_3955896825213980969[143] = 0.0;
   out_3955896825213980969[144] = 0.0;
   out_3955896825213980969[145] = 0.0;
   out_3955896825213980969[146] = 0.0;
   out_3955896825213980969[147] = 0.0;
   out_3955896825213980969[148] = 0.0;
   out_3955896825213980969[149] = 0.0;
   out_3955896825213980969[150] = 0.0;
   out_3955896825213980969[151] = 0.0;
   out_3955896825213980969[152] = 1.0;
   out_3955896825213980969[153] = 0.0;
   out_3955896825213980969[154] = 0.0;
   out_3955896825213980969[155] = 0.0;
   out_3955896825213980969[156] = 0.0;
   out_3955896825213980969[157] = 0.0;
   out_3955896825213980969[158] = 0.0;
   out_3955896825213980969[159] = 0.0;
   out_3955896825213980969[160] = 0.0;
   out_3955896825213980969[161] = 0.0;
   out_3955896825213980969[162] = 0.0;
   out_3955896825213980969[163] = 0.0;
   out_3955896825213980969[164] = 0.0;
   out_3955896825213980969[165] = 0.0;
   out_3955896825213980969[166] = 0.0;
   out_3955896825213980969[167] = 0.0;
   out_3955896825213980969[168] = 0.0;
   out_3955896825213980969[169] = 0.0;
   out_3955896825213980969[170] = 0.0;
   out_3955896825213980969[171] = 1.0;
   out_3955896825213980969[172] = 0.0;
   out_3955896825213980969[173] = 0.0;
   out_3955896825213980969[174] = 0.0;
   out_3955896825213980969[175] = 0.0;
   out_3955896825213980969[176] = 0.0;
   out_3955896825213980969[177] = 0.0;
   out_3955896825213980969[178] = 0.0;
   out_3955896825213980969[179] = 0.0;
   out_3955896825213980969[180] = 0.0;
   out_3955896825213980969[181] = 0.0;
   out_3955896825213980969[182] = 0.0;
   out_3955896825213980969[183] = 0.0;
   out_3955896825213980969[184] = 0.0;
   out_3955896825213980969[185] = 0.0;
   out_3955896825213980969[186] = 0.0;
   out_3955896825213980969[187] = 0.0;
   out_3955896825213980969[188] = 0.0;
   out_3955896825213980969[189] = 0.0;
   out_3955896825213980969[190] = 1.0;
   out_3955896825213980969[191] = 0.0;
   out_3955896825213980969[192] = 0.0;
   out_3955896825213980969[193] = 0.0;
   out_3955896825213980969[194] = 0.0;
   out_3955896825213980969[195] = 0.0;
   out_3955896825213980969[196] = 0.0;
   out_3955896825213980969[197] = 0.0;
   out_3955896825213980969[198] = 0.0;
   out_3955896825213980969[199] = 0.0;
   out_3955896825213980969[200] = 0.0;
   out_3955896825213980969[201] = 0.0;
   out_3955896825213980969[202] = 0.0;
   out_3955896825213980969[203] = 0.0;
   out_3955896825213980969[204] = 0.0;
   out_3955896825213980969[205] = 0.0;
   out_3955896825213980969[206] = 0.0;
   out_3955896825213980969[207] = 0.0;
   out_3955896825213980969[208] = 0.0;
   out_3955896825213980969[209] = 1.0;
   out_3955896825213980969[210] = 0.0;
   out_3955896825213980969[211] = 0.0;
   out_3955896825213980969[212] = 0.0;
   out_3955896825213980969[213] = 0.0;
   out_3955896825213980969[214] = 0.0;
   out_3955896825213980969[215] = 0.0;
   out_3955896825213980969[216] = 0.0;
   out_3955896825213980969[217] = 0.0;
   out_3955896825213980969[218] = 0.0;
   out_3955896825213980969[219] = 0.0;
   out_3955896825213980969[220] = 0.0;
   out_3955896825213980969[221] = 0.0;
   out_3955896825213980969[222] = 0.0;
   out_3955896825213980969[223] = 0.0;
   out_3955896825213980969[224] = 0.0;
   out_3955896825213980969[225] = 0.0;
   out_3955896825213980969[226] = 0.0;
   out_3955896825213980969[227] = 0.0;
   out_3955896825213980969[228] = 1.0;
   out_3955896825213980969[229] = 0.0;
   out_3955896825213980969[230] = 0.0;
   out_3955896825213980969[231] = 0.0;
   out_3955896825213980969[232] = 0.0;
   out_3955896825213980969[233] = 0.0;
   out_3955896825213980969[234] = 0.0;
   out_3955896825213980969[235] = 0.0;
   out_3955896825213980969[236] = 0.0;
   out_3955896825213980969[237] = 0.0;
   out_3955896825213980969[238] = 0.0;
   out_3955896825213980969[239] = 0.0;
   out_3955896825213980969[240] = 0.0;
   out_3955896825213980969[241] = 0.0;
   out_3955896825213980969[242] = 0.0;
   out_3955896825213980969[243] = 0.0;
   out_3955896825213980969[244] = 0.0;
   out_3955896825213980969[245] = 0.0;
   out_3955896825213980969[246] = 0.0;
   out_3955896825213980969[247] = 1.0;
   out_3955896825213980969[248] = 0.0;
   out_3955896825213980969[249] = 0.0;
   out_3955896825213980969[250] = 0.0;
   out_3955896825213980969[251] = 0.0;
   out_3955896825213980969[252] = 0.0;
   out_3955896825213980969[253] = 0.0;
   out_3955896825213980969[254] = 0.0;
   out_3955896825213980969[255] = 0.0;
   out_3955896825213980969[256] = 0.0;
   out_3955896825213980969[257] = 0.0;
   out_3955896825213980969[258] = 0.0;
   out_3955896825213980969[259] = 0.0;
   out_3955896825213980969[260] = 0.0;
   out_3955896825213980969[261] = 0.0;
   out_3955896825213980969[262] = 0.0;
   out_3955896825213980969[263] = 0.0;
   out_3955896825213980969[264] = 0.0;
   out_3955896825213980969[265] = 0.0;
   out_3955896825213980969[266] = 1.0;
   out_3955896825213980969[267] = 0.0;
   out_3955896825213980969[268] = 0.0;
   out_3955896825213980969[269] = 0.0;
   out_3955896825213980969[270] = 0.0;
   out_3955896825213980969[271] = 0.0;
   out_3955896825213980969[272] = 0.0;
   out_3955896825213980969[273] = 0.0;
   out_3955896825213980969[274] = 0.0;
   out_3955896825213980969[275] = 0.0;
   out_3955896825213980969[276] = 0.0;
   out_3955896825213980969[277] = 0.0;
   out_3955896825213980969[278] = 0.0;
   out_3955896825213980969[279] = 0.0;
   out_3955896825213980969[280] = 0.0;
   out_3955896825213980969[281] = 0.0;
   out_3955896825213980969[282] = 0.0;
   out_3955896825213980969[283] = 0.0;
   out_3955896825213980969[284] = 0.0;
   out_3955896825213980969[285] = 1.0;
   out_3955896825213980969[286] = 0.0;
   out_3955896825213980969[287] = 0.0;
   out_3955896825213980969[288] = 0.0;
   out_3955896825213980969[289] = 0.0;
   out_3955896825213980969[290] = 0.0;
   out_3955896825213980969[291] = 0.0;
   out_3955896825213980969[292] = 0.0;
   out_3955896825213980969[293] = 0.0;
   out_3955896825213980969[294] = 0.0;
   out_3955896825213980969[295] = 0.0;
   out_3955896825213980969[296] = 0.0;
   out_3955896825213980969[297] = 0.0;
   out_3955896825213980969[298] = 0.0;
   out_3955896825213980969[299] = 0.0;
   out_3955896825213980969[300] = 0.0;
   out_3955896825213980969[301] = 0.0;
   out_3955896825213980969[302] = 0.0;
   out_3955896825213980969[303] = 0.0;
   out_3955896825213980969[304] = 1.0;
   out_3955896825213980969[305] = 0.0;
   out_3955896825213980969[306] = 0.0;
   out_3955896825213980969[307] = 0.0;
   out_3955896825213980969[308] = 0.0;
   out_3955896825213980969[309] = 0.0;
   out_3955896825213980969[310] = 0.0;
   out_3955896825213980969[311] = 0.0;
   out_3955896825213980969[312] = 0.0;
   out_3955896825213980969[313] = 0.0;
   out_3955896825213980969[314] = 0.0;
   out_3955896825213980969[315] = 0.0;
   out_3955896825213980969[316] = 0.0;
   out_3955896825213980969[317] = 0.0;
   out_3955896825213980969[318] = 0.0;
   out_3955896825213980969[319] = 0.0;
   out_3955896825213980969[320] = 0.0;
   out_3955896825213980969[321] = 0.0;
   out_3955896825213980969[322] = 0.0;
   out_3955896825213980969[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_6226431844178190638) {
   out_6226431844178190638[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_6226431844178190638[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_6226431844178190638[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_6226431844178190638[3] = dt*state[12] + state[3];
   out_6226431844178190638[4] = dt*state[13] + state[4];
   out_6226431844178190638[5] = dt*state[14] + state[5];
   out_6226431844178190638[6] = state[6];
   out_6226431844178190638[7] = state[7];
   out_6226431844178190638[8] = state[8];
   out_6226431844178190638[9] = state[9];
   out_6226431844178190638[10] = state[10];
   out_6226431844178190638[11] = state[11];
   out_6226431844178190638[12] = state[12];
   out_6226431844178190638[13] = state[13];
   out_6226431844178190638[14] = state[14];
   out_6226431844178190638[15] = state[15];
   out_6226431844178190638[16] = state[16];
   out_6226431844178190638[17] = state[17];
}
void F_fun(double *state, double dt, double *out_5590858509180719260) {
   out_5590858509180719260[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_5590858509180719260[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_5590858509180719260[2] = 0;
   out_5590858509180719260[3] = 0;
   out_5590858509180719260[4] = 0;
   out_5590858509180719260[5] = 0;
   out_5590858509180719260[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_5590858509180719260[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_5590858509180719260[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_5590858509180719260[9] = 0;
   out_5590858509180719260[10] = 0;
   out_5590858509180719260[11] = 0;
   out_5590858509180719260[12] = 0;
   out_5590858509180719260[13] = 0;
   out_5590858509180719260[14] = 0;
   out_5590858509180719260[15] = 0;
   out_5590858509180719260[16] = 0;
   out_5590858509180719260[17] = 0;
   out_5590858509180719260[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_5590858509180719260[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_5590858509180719260[20] = 0;
   out_5590858509180719260[21] = 0;
   out_5590858509180719260[22] = 0;
   out_5590858509180719260[23] = 0;
   out_5590858509180719260[24] = 0;
   out_5590858509180719260[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_5590858509180719260[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_5590858509180719260[27] = 0;
   out_5590858509180719260[28] = 0;
   out_5590858509180719260[29] = 0;
   out_5590858509180719260[30] = 0;
   out_5590858509180719260[31] = 0;
   out_5590858509180719260[32] = 0;
   out_5590858509180719260[33] = 0;
   out_5590858509180719260[34] = 0;
   out_5590858509180719260[35] = 0;
   out_5590858509180719260[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_5590858509180719260[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_5590858509180719260[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_5590858509180719260[39] = 0;
   out_5590858509180719260[40] = 0;
   out_5590858509180719260[41] = 0;
   out_5590858509180719260[42] = 0;
   out_5590858509180719260[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_5590858509180719260[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_5590858509180719260[45] = 0;
   out_5590858509180719260[46] = 0;
   out_5590858509180719260[47] = 0;
   out_5590858509180719260[48] = 0;
   out_5590858509180719260[49] = 0;
   out_5590858509180719260[50] = 0;
   out_5590858509180719260[51] = 0;
   out_5590858509180719260[52] = 0;
   out_5590858509180719260[53] = 0;
   out_5590858509180719260[54] = 0;
   out_5590858509180719260[55] = 0;
   out_5590858509180719260[56] = 0;
   out_5590858509180719260[57] = 1;
   out_5590858509180719260[58] = 0;
   out_5590858509180719260[59] = 0;
   out_5590858509180719260[60] = 0;
   out_5590858509180719260[61] = 0;
   out_5590858509180719260[62] = 0;
   out_5590858509180719260[63] = 0;
   out_5590858509180719260[64] = 0;
   out_5590858509180719260[65] = 0;
   out_5590858509180719260[66] = dt;
   out_5590858509180719260[67] = 0;
   out_5590858509180719260[68] = 0;
   out_5590858509180719260[69] = 0;
   out_5590858509180719260[70] = 0;
   out_5590858509180719260[71] = 0;
   out_5590858509180719260[72] = 0;
   out_5590858509180719260[73] = 0;
   out_5590858509180719260[74] = 0;
   out_5590858509180719260[75] = 0;
   out_5590858509180719260[76] = 1;
   out_5590858509180719260[77] = 0;
   out_5590858509180719260[78] = 0;
   out_5590858509180719260[79] = 0;
   out_5590858509180719260[80] = 0;
   out_5590858509180719260[81] = 0;
   out_5590858509180719260[82] = 0;
   out_5590858509180719260[83] = 0;
   out_5590858509180719260[84] = 0;
   out_5590858509180719260[85] = dt;
   out_5590858509180719260[86] = 0;
   out_5590858509180719260[87] = 0;
   out_5590858509180719260[88] = 0;
   out_5590858509180719260[89] = 0;
   out_5590858509180719260[90] = 0;
   out_5590858509180719260[91] = 0;
   out_5590858509180719260[92] = 0;
   out_5590858509180719260[93] = 0;
   out_5590858509180719260[94] = 0;
   out_5590858509180719260[95] = 1;
   out_5590858509180719260[96] = 0;
   out_5590858509180719260[97] = 0;
   out_5590858509180719260[98] = 0;
   out_5590858509180719260[99] = 0;
   out_5590858509180719260[100] = 0;
   out_5590858509180719260[101] = 0;
   out_5590858509180719260[102] = 0;
   out_5590858509180719260[103] = 0;
   out_5590858509180719260[104] = dt;
   out_5590858509180719260[105] = 0;
   out_5590858509180719260[106] = 0;
   out_5590858509180719260[107] = 0;
   out_5590858509180719260[108] = 0;
   out_5590858509180719260[109] = 0;
   out_5590858509180719260[110] = 0;
   out_5590858509180719260[111] = 0;
   out_5590858509180719260[112] = 0;
   out_5590858509180719260[113] = 0;
   out_5590858509180719260[114] = 1;
   out_5590858509180719260[115] = 0;
   out_5590858509180719260[116] = 0;
   out_5590858509180719260[117] = 0;
   out_5590858509180719260[118] = 0;
   out_5590858509180719260[119] = 0;
   out_5590858509180719260[120] = 0;
   out_5590858509180719260[121] = 0;
   out_5590858509180719260[122] = 0;
   out_5590858509180719260[123] = 0;
   out_5590858509180719260[124] = 0;
   out_5590858509180719260[125] = 0;
   out_5590858509180719260[126] = 0;
   out_5590858509180719260[127] = 0;
   out_5590858509180719260[128] = 0;
   out_5590858509180719260[129] = 0;
   out_5590858509180719260[130] = 0;
   out_5590858509180719260[131] = 0;
   out_5590858509180719260[132] = 0;
   out_5590858509180719260[133] = 1;
   out_5590858509180719260[134] = 0;
   out_5590858509180719260[135] = 0;
   out_5590858509180719260[136] = 0;
   out_5590858509180719260[137] = 0;
   out_5590858509180719260[138] = 0;
   out_5590858509180719260[139] = 0;
   out_5590858509180719260[140] = 0;
   out_5590858509180719260[141] = 0;
   out_5590858509180719260[142] = 0;
   out_5590858509180719260[143] = 0;
   out_5590858509180719260[144] = 0;
   out_5590858509180719260[145] = 0;
   out_5590858509180719260[146] = 0;
   out_5590858509180719260[147] = 0;
   out_5590858509180719260[148] = 0;
   out_5590858509180719260[149] = 0;
   out_5590858509180719260[150] = 0;
   out_5590858509180719260[151] = 0;
   out_5590858509180719260[152] = 1;
   out_5590858509180719260[153] = 0;
   out_5590858509180719260[154] = 0;
   out_5590858509180719260[155] = 0;
   out_5590858509180719260[156] = 0;
   out_5590858509180719260[157] = 0;
   out_5590858509180719260[158] = 0;
   out_5590858509180719260[159] = 0;
   out_5590858509180719260[160] = 0;
   out_5590858509180719260[161] = 0;
   out_5590858509180719260[162] = 0;
   out_5590858509180719260[163] = 0;
   out_5590858509180719260[164] = 0;
   out_5590858509180719260[165] = 0;
   out_5590858509180719260[166] = 0;
   out_5590858509180719260[167] = 0;
   out_5590858509180719260[168] = 0;
   out_5590858509180719260[169] = 0;
   out_5590858509180719260[170] = 0;
   out_5590858509180719260[171] = 1;
   out_5590858509180719260[172] = 0;
   out_5590858509180719260[173] = 0;
   out_5590858509180719260[174] = 0;
   out_5590858509180719260[175] = 0;
   out_5590858509180719260[176] = 0;
   out_5590858509180719260[177] = 0;
   out_5590858509180719260[178] = 0;
   out_5590858509180719260[179] = 0;
   out_5590858509180719260[180] = 0;
   out_5590858509180719260[181] = 0;
   out_5590858509180719260[182] = 0;
   out_5590858509180719260[183] = 0;
   out_5590858509180719260[184] = 0;
   out_5590858509180719260[185] = 0;
   out_5590858509180719260[186] = 0;
   out_5590858509180719260[187] = 0;
   out_5590858509180719260[188] = 0;
   out_5590858509180719260[189] = 0;
   out_5590858509180719260[190] = 1;
   out_5590858509180719260[191] = 0;
   out_5590858509180719260[192] = 0;
   out_5590858509180719260[193] = 0;
   out_5590858509180719260[194] = 0;
   out_5590858509180719260[195] = 0;
   out_5590858509180719260[196] = 0;
   out_5590858509180719260[197] = 0;
   out_5590858509180719260[198] = 0;
   out_5590858509180719260[199] = 0;
   out_5590858509180719260[200] = 0;
   out_5590858509180719260[201] = 0;
   out_5590858509180719260[202] = 0;
   out_5590858509180719260[203] = 0;
   out_5590858509180719260[204] = 0;
   out_5590858509180719260[205] = 0;
   out_5590858509180719260[206] = 0;
   out_5590858509180719260[207] = 0;
   out_5590858509180719260[208] = 0;
   out_5590858509180719260[209] = 1;
   out_5590858509180719260[210] = 0;
   out_5590858509180719260[211] = 0;
   out_5590858509180719260[212] = 0;
   out_5590858509180719260[213] = 0;
   out_5590858509180719260[214] = 0;
   out_5590858509180719260[215] = 0;
   out_5590858509180719260[216] = 0;
   out_5590858509180719260[217] = 0;
   out_5590858509180719260[218] = 0;
   out_5590858509180719260[219] = 0;
   out_5590858509180719260[220] = 0;
   out_5590858509180719260[221] = 0;
   out_5590858509180719260[222] = 0;
   out_5590858509180719260[223] = 0;
   out_5590858509180719260[224] = 0;
   out_5590858509180719260[225] = 0;
   out_5590858509180719260[226] = 0;
   out_5590858509180719260[227] = 0;
   out_5590858509180719260[228] = 1;
   out_5590858509180719260[229] = 0;
   out_5590858509180719260[230] = 0;
   out_5590858509180719260[231] = 0;
   out_5590858509180719260[232] = 0;
   out_5590858509180719260[233] = 0;
   out_5590858509180719260[234] = 0;
   out_5590858509180719260[235] = 0;
   out_5590858509180719260[236] = 0;
   out_5590858509180719260[237] = 0;
   out_5590858509180719260[238] = 0;
   out_5590858509180719260[239] = 0;
   out_5590858509180719260[240] = 0;
   out_5590858509180719260[241] = 0;
   out_5590858509180719260[242] = 0;
   out_5590858509180719260[243] = 0;
   out_5590858509180719260[244] = 0;
   out_5590858509180719260[245] = 0;
   out_5590858509180719260[246] = 0;
   out_5590858509180719260[247] = 1;
   out_5590858509180719260[248] = 0;
   out_5590858509180719260[249] = 0;
   out_5590858509180719260[250] = 0;
   out_5590858509180719260[251] = 0;
   out_5590858509180719260[252] = 0;
   out_5590858509180719260[253] = 0;
   out_5590858509180719260[254] = 0;
   out_5590858509180719260[255] = 0;
   out_5590858509180719260[256] = 0;
   out_5590858509180719260[257] = 0;
   out_5590858509180719260[258] = 0;
   out_5590858509180719260[259] = 0;
   out_5590858509180719260[260] = 0;
   out_5590858509180719260[261] = 0;
   out_5590858509180719260[262] = 0;
   out_5590858509180719260[263] = 0;
   out_5590858509180719260[264] = 0;
   out_5590858509180719260[265] = 0;
   out_5590858509180719260[266] = 1;
   out_5590858509180719260[267] = 0;
   out_5590858509180719260[268] = 0;
   out_5590858509180719260[269] = 0;
   out_5590858509180719260[270] = 0;
   out_5590858509180719260[271] = 0;
   out_5590858509180719260[272] = 0;
   out_5590858509180719260[273] = 0;
   out_5590858509180719260[274] = 0;
   out_5590858509180719260[275] = 0;
   out_5590858509180719260[276] = 0;
   out_5590858509180719260[277] = 0;
   out_5590858509180719260[278] = 0;
   out_5590858509180719260[279] = 0;
   out_5590858509180719260[280] = 0;
   out_5590858509180719260[281] = 0;
   out_5590858509180719260[282] = 0;
   out_5590858509180719260[283] = 0;
   out_5590858509180719260[284] = 0;
   out_5590858509180719260[285] = 1;
   out_5590858509180719260[286] = 0;
   out_5590858509180719260[287] = 0;
   out_5590858509180719260[288] = 0;
   out_5590858509180719260[289] = 0;
   out_5590858509180719260[290] = 0;
   out_5590858509180719260[291] = 0;
   out_5590858509180719260[292] = 0;
   out_5590858509180719260[293] = 0;
   out_5590858509180719260[294] = 0;
   out_5590858509180719260[295] = 0;
   out_5590858509180719260[296] = 0;
   out_5590858509180719260[297] = 0;
   out_5590858509180719260[298] = 0;
   out_5590858509180719260[299] = 0;
   out_5590858509180719260[300] = 0;
   out_5590858509180719260[301] = 0;
   out_5590858509180719260[302] = 0;
   out_5590858509180719260[303] = 0;
   out_5590858509180719260[304] = 1;
   out_5590858509180719260[305] = 0;
   out_5590858509180719260[306] = 0;
   out_5590858509180719260[307] = 0;
   out_5590858509180719260[308] = 0;
   out_5590858509180719260[309] = 0;
   out_5590858509180719260[310] = 0;
   out_5590858509180719260[311] = 0;
   out_5590858509180719260[312] = 0;
   out_5590858509180719260[313] = 0;
   out_5590858509180719260[314] = 0;
   out_5590858509180719260[315] = 0;
   out_5590858509180719260[316] = 0;
   out_5590858509180719260[317] = 0;
   out_5590858509180719260[318] = 0;
   out_5590858509180719260[319] = 0;
   out_5590858509180719260[320] = 0;
   out_5590858509180719260[321] = 0;
   out_5590858509180719260[322] = 0;
   out_5590858509180719260[323] = 1;
}
void h_4(double *state, double *unused, double *out_8311116516369893334) {
   out_8311116516369893334[0] = state[6] + state[9];
   out_8311116516369893334[1] = state[7] + state[10];
   out_8311116516369893334[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_1196621559825099766) {
   out_1196621559825099766[0] = 0;
   out_1196621559825099766[1] = 0;
   out_1196621559825099766[2] = 0;
   out_1196621559825099766[3] = 0;
   out_1196621559825099766[4] = 0;
   out_1196621559825099766[5] = 0;
   out_1196621559825099766[6] = 1;
   out_1196621559825099766[7] = 0;
   out_1196621559825099766[8] = 0;
   out_1196621559825099766[9] = 1;
   out_1196621559825099766[10] = 0;
   out_1196621559825099766[11] = 0;
   out_1196621559825099766[12] = 0;
   out_1196621559825099766[13] = 0;
   out_1196621559825099766[14] = 0;
   out_1196621559825099766[15] = 0;
   out_1196621559825099766[16] = 0;
   out_1196621559825099766[17] = 0;
   out_1196621559825099766[18] = 0;
   out_1196621559825099766[19] = 0;
   out_1196621559825099766[20] = 0;
   out_1196621559825099766[21] = 0;
   out_1196621559825099766[22] = 0;
   out_1196621559825099766[23] = 0;
   out_1196621559825099766[24] = 0;
   out_1196621559825099766[25] = 1;
   out_1196621559825099766[26] = 0;
   out_1196621559825099766[27] = 0;
   out_1196621559825099766[28] = 1;
   out_1196621559825099766[29] = 0;
   out_1196621559825099766[30] = 0;
   out_1196621559825099766[31] = 0;
   out_1196621559825099766[32] = 0;
   out_1196621559825099766[33] = 0;
   out_1196621559825099766[34] = 0;
   out_1196621559825099766[35] = 0;
   out_1196621559825099766[36] = 0;
   out_1196621559825099766[37] = 0;
   out_1196621559825099766[38] = 0;
   out_1196621559825099766[39] = 0;
   out_1196621559825099766[40] = 0;
   out_1196621559825099766[41] = 0;
   out_1196621559825099766[42] = 0;
   out_1196621559825099766[43] = 0;
   out_1196621559825099766[44] = 1;
   out_1196621559825099766[45] = 0;
   out_1196621559825099766[46] = 0;
   out_1196621559825099766[47] = 1;
   out_1196621559825099766[48] = 0;
   out_1196621559825099766[49] = 0;
   out_1196621559825099766[50] = 0;
   out_1196621559825099766[51] = 0;
   out_1196621559825099766[52] = 0;
   out_1196621559825099766[53] = 0;
}
void h_10(double *state, double *unused, double *out_8024633733467632830) {
   out_8024633733467632830[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_8024633733467632830[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_8024633733467632830[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_9211636060607930666) {
   out_9211636060607930666[0] = 0;
   out_9211636060607930666[1] = 9.8100000000000005*cos(state[1]);
   out_9211636060607930666[2] = 0;
   out_9211636060607930666[3] = 0;
   out_9211636060607930666[4] = -state[8];
   out_9211636060607930666[5] = state[7];
   out_9211636060607930666[6] = 0;
   out_9211636060607930666[7] = state[5];
   out_9211636060607930666[8] = -state[4];
   out_9211636060607930666[9] = 0;
   out_9211636060607930666[10] = 0;
   out_9211636060607930666[11] = 0;
   out_9211636060607930666[12] = 1;
   out_9211636060607930666[13] = 0;
   out_9211636060607930666[14] = 0;
   out_9211636060607930666[15] = 1;
   out_9211636060607930666[16] = 0;
   out_9211636060607930666[17] = 0;
   out_9211636060607930666[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_9211636060607930666[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_9211636060607930666[20] = 0;
   out_9211636060607930666[21] = state[8];
   out_9211636060607930666[22] = 0;
   out_9211636060607930666[23] = -state[6];
   out_9211636060607930666[24] = -state[5];
   out_9211636060607930666[25] = 0;
   out_9211636060607930666[26] = state[3];
   out_9211636060607930666[27] = 0;
   out_9211636060607930666[28] = 0;
   out_9211636060607930666[29] = 0;
   out_9211636060607930666[30] = 0;
   out_9211636060607930666[31] = 1;
   out_9211636060607930666[32] = 0;
   out_9211636060607930666[33] = 0;
   out_9211636060607930666[34] = 1;
   out_9211636060607930666[35] = 0;
   out_9211636060607930666[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_9211636060607930666[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_9211636060607930666[38] = 0;
   out_9211636060607930666[39] = -state[7];
   out_9211636060607930666[40] = state[6];
   out_9211636060607930666[41] = 0;
   out_9211636060607930666[42] = state[4];
   out_9211636060607930666[43] = -state[3];
   out_9211636060607930666[44] = 0;
   out_9211636060607930666[45] = 0;
   out_9211636060607930666[46] = 0;
   out_9211636060607930666[47] = 0;
   out_9211636060607930666[48] = 0;
   out_9211636060607930666[49] = 0;
   out_9211636060607930666[50] = 1;
   out_9211636060607930666[51] = 0;
   out_9211636060607930666[52] = 0;
   out_9211636060607930666[53] = 1;
}
void h_13(double *state, double *unused, double *out_5246243153983473200) {
   out_5246243153983473200[0] = state[3];
   out_5246243153983473200[1] = state[4];
   out_5246243153983473200[2] = state[5];
}
void H_13(double *state, double *unused, double *out_4408895385157432567) {
   out_4408895385157432567[0] = 0;
   out_4408895385157432567[1] = 0;
   out_4408895385157432567[2] = 0;
   out_4408895385157432567[3] = 1;
   out_4408895385157432567[4] = 0;
   out_4408895385157432567[5] = 0;
   out_4408895385157432567[6] = 0;
   out_4408895385157432567[7] = 0;
   out_4408895385157432567[8] = 0;
   out_4408895385157432567[9] = 0;
   out_4408895385157432567[10] = 0;
   out_4408895385157432567[11] = 0;
   out_4408895385157432567[12] = 0;
   out_4408895385157432567[13] = 0;
   out_4408895385157432567[14] = 0;
   out_4408895385157432567[15] = 0;
   out_4408895385157432567[16] = 0;
   out_4408895385157432567[17] = 0;
   out_4408895385157432567[18] = 0;
   out_4408895385157432567[19] = 0;
   out_4408895385157432567[20] = 0;
   out_4408895385157432567[21] = 0;
   out_4408895385157432567[22] = 1;
   out_4408895385157432567[23] = 0;
   out_4408895385157432567[24] = 0;
   out_4408895385157432567[25] = 0;
   out_4408895385157432567[26] = 0;
   out_4408895385157432567[27] = 0;
   out_4408895385157432567[28] = 0;
   out_4408895385157432567[29] = 0;
   out_4408895385157432567[30] = 0;
   out_4408895385157432567[31] = 0;
   out_4408895385157432567[32] = 0;
   out_4408895385157432567[33] = 0;
   out_4408895385157432567[34] = 0;
   out_4408895385157432567[35] = 0;
   out_4408895385157432567[36] = 0;
   out_4408895385157432567[37] = 0;
   out_4408895385157432567[38] = 0;
   out_4408895385157432567[39] = 0;
   out_4408895385157432567[40] = 0;
   out_4408895385157432567[41] = 1;
   out_4408895385157432567[42] = 0;
   out_4408895385157432567[43] = 0;
   out_4408895385157432567[44] = 0;
   out_4408895385157432567[45] = 0;
   out_4408895385157432567[46] = 0;
   out_4408895385157432567[47] = 0;
   out_4408895385157432567[48] = 0;
   out_4408895385157432567[49] = 0;
   out_4408895385157432567[50] = 0;
   out_4408895385157432567[51] = 0;
   out_4408895385157432567[52] = 0;
   out_4408895385157432567[53] = 0;
}
void h_14(double *state, double *unused, double *out_2666716766060469740) {
   out_2666716766060469740[0] = state[6];
   out_2666716766060469740[1] = state[7];
   out_2666716766060469740[2] = state[8];
}
void H_14(double *state, double *unused, double *out_5159862416164584295) {
   out_5159862416164584295[0] = 0;
   out_5159862416164584295[1] = 0;
   out_5159862416164584295[2] = 0;
   out_5159862416164584295[3] = 0;
   out_5159862416164584295[4] = 0;
   out_5159862416164584295[5] = 0;
   out_5159862416164584295[6] = 1;
   out_5159862416164584295[7] = 0;
   out_5159862416164584295[8] = 0;
   out_5159862416164584295[9] = 0;
   out_5159862416164584295[10] = 0;
   out_5159862416164584295[11] = 0;
   out_5159862416164584295[12] = 0;
   out_5159862416164584295[13] = 0;
   out_5159862416164584295[14] = 0;
   out_5159862416164584295[15] = 0;
   out_5159862416164584295[16] = 0;
   out_5159862416164584295[17] = 0;
   out_5159862416164584295[18] = 0;
   out_5159862416164584295[19] = 0;
   out_5159862416164584295[20] = 0;
   out_5159862416164584295[21] = 0;
   out_5159862416164584295[22] = 0;
   out_5159862416164584295[23] = 0;
   out_5159862416164584295[24] = 0;
   out_5159862416164584295[25] = 1;
   out_5159862416164584295[26] = 0;
   out_5159862416164584295[27] = 0;
   out_5159862416164584295[28] = 0;
   out_5159862416164584295[29] = 0;
   out_5159862416164584295[30] = 0;
   out_5159862416164584295[31] = 0;
   out_5159862416164584295[32] = 0;
   out_5159862416164584295[33] = 0;
   out_5159862416164584295[34] = 0;
   out_5159862416164584295[35] = 0;
   out_5159862416164584295[36] = 0;
   out_5159862416164584295[37] = 0;
   out_5159862416164584295[38] = 0;
   out_5159862416164584295[39] = 0;
   out_5159862416164584295[40] = 0;
   out_5159862416164584295[41] = 0;
   out_5159862416164584295[42] = 0;
   out_5159862416164584295[43] = 0;
   out_5159862416164584295[44] = 1;
   out_5159862416164584295[45] = 0;
   out_5159862416164584295[46] = 0;
   out_5159862416164584295[47] = 0;
   out_5159862416164584295[48] = 0;
   out_5159862416164584295[49] = 0;
   out_5159862416164584295[50] = 0;
   out_5159862416164584295[51] = 0;
   out_5159862416164584295[52] = 0;
   out_5159862416164584295[53] = 0;
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
void pose_err_fun(double *nom_x, double *delta_x, double *out_7491504487925958906) {
  err_fun(nom_x, delta_x, out_7491504487925958906);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_8173082431785614969) {
  inv_err_fun(nom_x, true_x, out_8173082431785614969);
}
void pose_H_mod_fun(double *state, double *out_3955896825213980969) {
  H_mod_fun(state, out_3955896825213980969);
}
void pose_f_fun(double *state, double dt, double *out_6226431844178190638) {
  f_fun(state,  dt, out_6226431844178190638);
}
void pose_F_fun(double *state, double dt, double *out_5590858509180719260) {
  F_fun(state,  dt, out_5590858509180719260);
}
void pose_h_4(double *state, double *unused, double *out_8311116516369893334) {
  h_4(state, unused, out_8311116516369893334);
}
void pose_H_4(double *state, double *unused, double *out_1196621559825099766) {
  H_4(state, unused, out_1196621559825099766);
}
void pose_h_10(double *state, double *unused, double *out_8024633733467632830) {
  h_10(state, unused, out_8024633733467632830);
}
void pose_H_10(double *state, double *unused, double *out_9211636060607930666) {
  H_10(state, unused, out_9211636060607930666);
}
void pose_h_13(double *state, double *unused, double *out_5246243153983473200) {
  h_13(state, unused, out_5246243153983473200);
}
void pose_H_13(double *state, double *unused, double *out_4408895385157432567) {
  H_13(state, unused, out_4408895385157432567);
}
void pose_h_14(double *state, double *unused, double *out_2666716766060469740) {
  h_14(state, unused, out_2666716766060469740);
}
void pose_H_14(double *state, double *unused, double *out_5159862416164584295) {
  H_14(state, unused, out_5159862416164584295);
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
