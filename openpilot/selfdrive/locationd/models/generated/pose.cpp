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
void err_fun(double *nom_x, double *delta_x, double *out_1372154176746733435) {
   out_1372154176746733435[0] = delta_x[0] + nom_x[0];
   out_1372154176746733435[1] = delta_x[1] + nom_x[1];
   out_1372154176746733435[2] = delta_x[2] + nom_x[2];
   out_1372154176746733435[3] = delta_x[3] + nom_x[3];
   out_1372154176746733435[4] = delta_x[4] + nom_x[4];
   out_1372154176746733435[5] = delta_x[5] + nom_x[5];
   out_1372154176746733435[6] = delta_x[6] + nom_x[6];
   out_1372154176746733435[7] = delta_x[7] + nom_x[7];
   out_1372154176746733435[8] = delta_x[8] + nom_x[8];
   out_1372154176746733435[9] = delta_x[9] + nom_x[9];
   out_1372154176746733435[10] = delta_x[10] + nom_x[10];
   out_1372154176746733435[11] = delta_x[11] + nom_x[11];
   out_1372154176746733435[12] = delta_x[12] + nom_x[12];
   out_1372154176746733435[13] = delta_x[13] + nom_x[13];
   out_1372154176746733435[14] = delta_x[14] + nom_x[14];
   out_1372154176746733435[15] = delta_x[15] + nom_x[15];
   out_1372154176746733435[16] = delta_x[16] + nom_x[16];
   out_1372154176746733435[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_1523580565963320994) {
   out_1523580565963320994[0] = -nom_x[0] + true_x[0];
   out_1523580565963320994[1] = -nom_x[1] + true_x[1];
   out_1523580565963320994[2] = -nom_x[2] + true_x[2];
   out_1523580565963320994[3] = -nom_x[3] + true_x[3];
   out_1523580565963320994[4] = -nom_x[4] + true_x[4];
   out_1523580565963320994[5] = -nom_x[5] + true_x[5];
   out_1523580565963320994[6] = -nom_x[6] + true_x[6];
   out_1523580565963320994[7] = -nom_x[7] + true_x[7];
   out_1523580565963320994[8] = -nom_x[8] + true_x[8];
   out_1523580565963320994[9] = -nom_x[9] + true_x[9];
   out_1523580565963320994[10] = -nom_x[10] + true_x[10];
   out_1523580565963320994[11] = -nom_x[11] + true_x[11];
   out_1523580565963320994[12] = -nom_x[12] + true_x[12];
   out_1523580565963320994[13] = -nom_x[13] + true_x[13];
   out_1523580565963320994[14] = -nom_x[14] + true_x[14];
   out_1523580565963320994[15] = -nom_x[15] + true_x[15];
   out_1523580565963320994[16] = -nom_x[16] + true_x[16];
   out_1523580565963320994[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_7104221342799173532) {
   out_7104221342799173532[0] = 1.0;
   out_7104221342799173532[1] = 0.0;
   out_7104221342799173532[2] = 0.0;
   out_7104221342799173532[3] = 0.0;
   out_7104221342799173532[4] = 0.0;
   out_7104221342799173532[5] = 0.0;
   out_7104221342799173532[6] = 0.0;
   out_7104221342799173532[7] = 0.0;
   out_7104221342799173532[8] = 0.0;
   out_7104221342799173532[9] = 0.0;
   out_7104221342799173532[10] = 0.0;
   out_7104221342799173532[11] = 0.0;
   out_7104221342799173532[12] = 0.0;
   out_7104221342799173532[13] = 0.0;
   out_7104221342799173532[14] = 0.0;
   out_7104221342799173532[15] = 0.0;
   out_7104221342799173532[16] = 0.0;
   out_7104221342799173532[17] = 0.0;
   out_7104221342799173532[18] = 0.0;
   out_7104221342799173532[19] = 1.0;
   out_7104221342799173532[20] = 0.0;
   out_7104221342799173532[21] = 0.0;
   out_7104221342799173532[22] = 0.0;
   out_7104221342799173532[23] = 0.0;
   out_7104221342799173532[24] = 0.0;
   out_7104221342799173532[25] = 0.0;
   out_7104221342799173532[26] = 0.0;
   out_7104221342799173532[27] = 0.0;
   out_7104221342799173532[28] = 0.0;
   out_7104221342799173532[29] = 0.0;
   out_7104221342799173532[30] = 0.0;
   out_7104221342799173532[31] = 0.0;
   out_7104221342799173532[32] = 0.0;
   out_7104221342799173532[33] = 0.0;
   out_7104221342799173532[34] = 0.0;
   out_7104221342799173532[35] = 0.0;
   out_7104221342799173532[36] = 0.0;
   out_7104221342799173532[37] = 0.0;
   out_7104221342799173532[38] = 1.0;
   out_7104221342799173532[39] = 0.0;
   out_7104221342799173532[40] = 0.0;
   out_7104221342799173532[41] = 0.0;
   out_7104221342799173532[42] = 0.0;
   out_7104221342799173532[43] = 0.0;
   out_7104221342799173532[44] = 0.0;
   out_7104221342799173532[45] = 0.0;
   out_7104221342799173532[46] = 0.0;
   out_7104221342799173532[47] = 0.0;
   out_7104221342799173532[48] = 0.0;
   out_7104221342799173532[49] = 0.0;
   out_7104221342799173532[50] = 0.0;
   out_7104221342799173532[51] = 0.0;
   out_7104221342799173532[52] = 0.0;
   out_7104221342799173532[53] = 0.0;
   out_7104221342799173532[54] = 0.0;
   out_7104221342799173532[55] = 0.0;
   out_7104221342799173532[56] = 0.0;
   out_7104221342799173532[57] = 1.0;
   out_7104221342799173532[58] = 0.0;
   out_7104221342799173532[59] = 0.0;
   out_7104221342799173532[60] = 0.0;
   out_7104221342799173532[61] = 0.0;
   out_7104221342799173532[62] = 0.0;
   out_7104221342799173532[63] = 0.0;
   out_7104221342799173532[64] = 0.0;
   out_7104221342799173532[65] = 0.0;
   out_7104221342799173532[66] = 0.0;
   out_7104221342799173532[67] = 0.0;
   out_7104221342799173532[68] = 0.0;
   out_7104221342799173532[69] = 0.0;
   out_7104221342799173532[70] = 0.0;
   out_7104221342799173532[71] = 0.0;
   out_7104221342799173532[72] = 0.0;
   out_7104221342799173532[73] = 0.0;
   out_7104221342799173532[74] = 0.0;
   out_7104221342799173532[75] = 0.0;
   out_7104221342799173532[76] = 1.0;
   out_7104221342799173532[77] = 0.0;
   out_7104221342799173532[78] = 0.0;
   out_7104221342799173532[79] = 0.0;
   out_7104221342799173532[80] = 0.0;
   out_7104221342799173532[81] = 0.0;
   out_7104221342799173532[82] = 0.0;
   out_7104221342799173532[83] = 0.0;
   out_7104221342799173532[84] = 0.0;
   out_7104221342799173532[85] = 0.0;
   out_7104221342799173532[86] = 0.0;
   out_7104221342799173532[87] = 0.0;
   out_7104221342799173532[88] = 0.0;
   out_7104221342799173532[89] = 0.0;
   out_7104221342799173532[90] = 0.0;
   out_7104221342799173532[91] = 0.0;
   out_7104221342799173532[92] = 0.0;
   out_7104221342799173532[93] = 0.0;
   out_7104221342799173532[94] = 0.0;
   out_7104221342799173532[95] = 1.0;
   out_7104221342799173532[96] = 0.0;
   out_7104221342799173532[97] = 0.0;
   out_7104221342799173532[98] = 0.0;
   out_7104221342799173532[99] = 0.0;
   out_7104221342799173532[100] = 0.0;
   out_7104221342799173532[101] = 0.0;
   out_7104221342799173532[102] = 0.0;
   out_7104221342799173532[103] = 0.0;
   out_7104221342799173532[104] = 0.0;
   out_7104221342799173532[105] = 0.0;
   out_7104221342799173532[106] = 0.0;
   out_7104221342799173532[107] = 0.0;
   out_7104221342799173532[108] = 0.0;
   out_7104221342799173532[109] = 0.0;
   out_7104221342799173532[110] = 0.0;
   out_7104221342799173532[111] = 0.0;
   out_7104221342799173532[112] = 0.0;
   out_7104221342799173532[113] = 0.0;
   out_7104221342799173532[114] = 1.0;
   out_7104221342799173532[115] = 0.0;
   out_7104221342799173532[116] = 0.0;
   out_7104221342799173532[117] = 0.0;
   out_7104221342799173532[118] = 0.0;
   out_7104221342799173532[119] = 0.0;
   out_7104221342799173532[120] = 0.0;
   out_7104221342799173532[121] = 0.0;
   out_7104221342799173532[122] = 0.0;
   out_7104221342799173532[123] = 0.0;
   out_7104221342799173532[124] = 0.0;
   out_7104221342799173532[125] = 0.0;
   out_7104221342799173532[126] = 0.0;
   out_7104221342799173532[127] = 0.0;
   out_7104221342799173532[128] = 0.0;
   out_7104221342799173532[129] = 0.0;
   out_7104221342799173532[130] = 0.0;
   out_7104221342799173532[131] = 0.0;
   out_7104221342799173532[132] = 0.0;
   out_7104221342799173532[133] = 1.0;
   out_7104221342799173532[134] = 0.0;
   out_7104221342799173532[135] = 0.0;
   out_7104221342799173532[136] = 0.0;
   out_7104221342799173532[137] = 0.0;
   out_7104221342799173532[138] = 0.0;
   out_7104221342799173532[139] = 0.0;
   out_7104221342799173532[140] = 0.0;
   out_7104221342799173532[141] = 0.0;
   out_7104221342799173532[142] = 0.0;
   out_7104221342799173532[143] = 0.0;
   out_7104221342799173532[144] = 0.0;
   out_7104221342799173532[145] = 0.0;
   out_7104221342799173532[146] = 0.0;
   out_7104221342799173532[147] = 0.0;
   out_7104221342799173532[148] = 0.0;
   out_7104221342799173532[149] = 0.0;
   out_7104221342799173532[150] = 0.0;
   out_7104221342799173532[151] = 0.0;
   out_7104221342799173532[152] = 1.0;
   out_7104221342799173532[153] = 0.0;
   out_7104221342799173532[154] = 0.0;
   out_7104221342799173532[155] = 0.0;
   out_7104221342799173532[156] = 0.0;
   out_7104221342799173532[157] = 0.0;
   out_7104221342799173532[158] = 0.0;
   out_7104221342799173532[159] = 0.0;
   out_7104221342799173532[160] = 0.0;
   out_7104221342799173532[161] = 0.0;
   out_7104221342799173532[162] = 0.0;
   out_7104221342799173532[163] = 0.0;
   out_7104221342799173532[164] = 0.0;
   out_7104221342799173532[165] = 0.0;
   out_7104221342799173532[166] = 0.0;
   out_7104221342799173532[167] = 0.0;
   out_7104221342799173532[168] = 0.0;
   out_7104221342799173532[169] = 0.0;
   out_7104221342799173532[170] = 0.0;
   out_7104221342799173532[171] = 1.0;
   out_7104221342799173532[172] = 0.0;
   out_7104221342799173532[173] = 0.0;
   out_7104221342799173532[174] = 0.0;
   out_7104221342799173532[175] = 0.0;
   out_7104221342799173532[176] = 0.0;
   out_7104221342799173532[177] = 0.0;
   out_7104221342799173532[178] = 0.0;
   out_7104221342799173532[179] = 0.0;
   out_7104221342799173532[180] = 0.0;
   out_7104221342799173532[181] = 0.0;
   out_7104221342799173532[182] = 0.0;
   out_7104221342799173532[183] = 0.0;
   out_7104221342799173532[184] = 0.0;
   out_7104221342799173532[185] = 0.0;
   out_7104221342799173532[186] = 0.0;
   out_7104221342799173532[187] = 0.0;
   out_7104221342799173532[188] = 0.0;
   out_7104221342799173532[189] = 0.0;
   out_7104221342799173532[190] = 1.0;
   out_7104221342799173532[191] = 0.0;
   out_7104221342799173532[192] = 0.0;
   out_7104221342799173532[193] = 0.0;
   out_7104221342799173532[194] = 0.0;
   out_7104221342799173532[195] = 0.0;
   out_7104221342799173532[196] = 0.0;
   out_7104221342799173532[197] = 0.0;
   out_7104221342799173532[198] = 0.0;
   out_7104221342799173532[199] = 0.0;
   out_7104221342799173532[200] = 0.0;
   out_7104221342799173532[201] = 0.0;
   out_7104221342799173532[202] = 0.0;
   out_7104221342799173532[203] = 0.0;
   out_7104221342799173532[204] = 0.0;
   out_7104221342799173532[205] = 0.0;
   out_7104221342799173532[206] = 0.0;
   out_7104221342799173532[207] = 0.0;
   out_7104221342799173532[208] = 0.0;
   out_7104221342799173532[209] = 1.0;
   out_7104221342799173532[210] = 0.0;
   out_7104221342799173532[211] = 0.0;
   out_7104221342799173532[212] = 0.0;
   out_7104221342799173532[213] = 0.0;
   out_7104221342799173532[214] = 0.0;
   out_7104221342799173532[215] = 0.0;
   out_7104221342799173532[216] = 0.0;
   out_7104221342799173532[217] = 0.0;
   out_7104221342799173532[218] = 0.0;
   out_7104221342799173532[219] = 0.0;
   out_7104221342799173532[220] = 0.0;
   out_7104221342799173532[221] = 0.0;
   out_7104221342799173532[222] = 0.0;
   out_7104221342799173532[223] = 0.0;
   out_7104221342799173532[224] = 0.0;
   out_7104221342799173532[225] = 0.0;
   out_7104221342799173532[226] = 0.0;
   out_7104221342799173532[227] = 0.0;
   out_7104221342799173532[228] = 1.0;
   out_7104221342799173532[229] = 0.0;
   out_7104221342799173532[230] = 0.0;
   out_7104221342799173532[231] = 0.0;
   out_7104221342799173532[232] = 0.0;
   out_7104221342799173532[233] = 0.0;
   out_7104221342799173532[234] = 0.0;
   out_7104221342799173532[235] = 0.0;
   out_7104221342799173532[236] = 0.0;
   out_7104221342799173532[237] = 0.0;
   out_7104221342799173532[238] = 0.0;
   out_7104221342799173532[239] = 0.0;
   out_7104221342799173532[240] = 0.0;
   out_7104221342799173532[241] = 0.0;
   out_7104221342799173532[242] = 0.0;
   out_7104221342799173532[243] = 0.0;
   out_7104221342799173532[244] = 0.0;
   out_7104221342799173532[245] = 0.0;
   out_7104221342799173532[246] = 0.0;
   out_7104221342799173532[247] = 1.0;
   out_7104221342799173532[248] = 0.0;
   out_7104221342799173532[249] = 0.0;
   out_7104221342799173532[250] = 0.0;
   out_7104221342799173532[251] = 0.0;
   out_7104221342799173532[252] = 0.0;
   out_7104221342799173532[253] = 0.0;
   out_7104221342799173532[254] = 0.0;
   out_7104221342799173532[255] = 0.0;
   out_7104221342799173532[256] = 0.0;
   out_7104221342799173532[257] = 0.0;
   out_7104221342799173532[258] = 0.0;
   out_7104221342799173532[259] = 0.0;
   out_7104221342799173532[260] = 0.0;
   out_7104221342799173532[261] = 0.0;
   out_7104221342799173532[262] = 0.0;
   out_7104221342799173532[263] = 0.0;
   out_7104221342799173532[264] = 0.0;
   out_7104221342799173532[265] = 0.0;
   out_7104221342799173532[266] = 1.0;
   out_7104221342799173532[267] = 0.0;
   out_7104221342799173532[268] = 0.0;
   out_7104221342799173532[269] = 0.0;
   out_7104221342799173532[270] = 0.0;
   out_7104221342799173532[271] = 0.0;
   out_7104221342799173532[272] = 0.0;
   out_7104221342799173532[273] = 0.0;
   out_7104221342799173532[274] = 0.0;
   out_7104221342799173532[275] = 0.0;
   out_7104221342799173532[276] = 0.0;
   out_7104221342799173532[277] = 0.0;
   out_7104221342799173532[278] = 0.0;
   out_7104221342799173532[279] = 0.0;
   out_7104221342799173532[280] = 0.0;
   out_7104221342799173532[281] = 0.0;
   out_7104221342799173532[282] = 0.0;
   out_7104221342799173532[283] = 0.0;
   out_7104221342799173532[284] = 0.0;
   out_7104221342799173532[285] = 1.0;
   out_7104221342799173532[286] = 0.0;
   out_7104221342799173532[287] = 0.0;
   out_7104221342799173532[288] = 0.0;
   out_7104221342799173532[289] = 0.0;
   out_7104221342799173532[290] = 0.0;
   out_7104221342799173532[291] = 0.0;
   out_7104221342799173532[292] = 0.0;
   out_7104221342799173532[293] = 0.0;
   out_7104221342799173532[294] = 0.0;
   out_7104221342799173532[295] = 0.0;
   out_7104221342799173532[296] = 0.0;
   out_7104221342799173532[297] = 0.0;
   out_7104221342799173532[298] = 0.0;
   out_7104221342799173532[299] = 0.0;
   out_7104221342799173532[300] = 0.0;
   out_7104221342799173532[301] = 0.0;
   out_7104221342799173532[302] = 0.0;
   out_7104221342799173532[303] = 0.0;
   out_7104221342799173532[304] = 1.0;
   out_7104221342799173532[305] = 0.0;
   out_7104221342799173532[306] = 0.0;
   out_7104221342799173532[307] = 0.0;
   out_7104221342799173532[308] = 0.0;
   out_7104221342799173532[309] = 0.0;
   out_7104221342799173532[310] = 0.0;
   out_7104221342799173532[311] = 0.0;
   out_7104221342799173532[312] = 0.0;
   out_7104221342799173532[313] = 0.0;
   out_7104221342799173532[314] = 0.0;
   out_7104221342799173532[315] = 0.0;
   out_7104221342799173532[316] = 0.0;
   out_7104221342799173532[317] = 0.0;
   out_7104221342799173532[318] = 0.0;
   out_7104221342799173532[319] = 0.0;
   out_7104221342799173532[320] = 0.0;
   out_7104221342799173532[321] = 0.0;
   out_7104221342799173532[322] = 0.0;
   out_7104221342799173532[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_7349931890006772642) {
   out_7349931890006772642[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_7349931890006772642[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_7349931890006772642[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_7349931890006772642[3] = dt*state[12] + state[3];
   out_7349931890006772642[4] = dt*state[13] + state[4];
   out_7349931890006772642[5] = dt*state[14] + state[5];
   out_7349931890006772642[6] = state[6];
   out_7349931890006772642[7] = state[7];
   out_7349931890006772642[8] = state[8];
   out_7349931890006772642[9] = state[9];
   out_7349931890006772642[10] = state[10];
   out_7349931890006772642[11] = state[11];
   out_7349931890006772642[12] = state[12];
   out_7349931890006772642[13] = state[13];
   out_7349931890006772642[14] = state[14];
   out_7349931890006772642[15] = state[15];
   out_7349931890006772642[16] = state[16];
   out_7349931890006772642[17] = state[17];
}
void F_fun(double *state, double dt, double *out_1064691538495726265) {
   out_1064691538495726265[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_1064691538495726265[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_1064691538495726265[2] = 0;
   out_1064691538495726265[3] = 0;
   out_1064691538495726265[4] = 0;
   out_1064691538495726265[5] = 0;
   out_1064691538495726265[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_1064691538495726265[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_1064691538495726265[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_1064691538495726265[9] = 0;
   out_1064691538495726265[10] = 0;
   out_1064691538495726265[11] = 0;
   out_1064691538495726265[12] = 0;
   out_1064691538495726265[13] = 0;
   out_1064691538495726265[14] = 0;
   out_1064691538495726265[15] = 0;
   out_1064691538495726265[16] = 0;
   out_1064691538495726265[17] = 0;
   out_1064691538495726265[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_1064691538495726265[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_1064691538495726265[20] = 0;
   out_1064691538495726265[21] = 0;
   out_1064691538495726265[22] = 0;
   out_1064691538495726265[23] = 0;
   out_1064691538495726265[24] = 0;
   out_1064691538495726265[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_1064691538495726265[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_1064691538495726265[27] = 0;
   out_1064691538495726265[28] = 0;
   out_1064691538495726265[29] = 0;
   out_1064691538495726265[30] = 0;
   out_1064691538495726265[31] = 0;
   out_1064691538495726265[32] = 0;
   out_1064691538495726265[33] = 0;
   out_1064691538495726265[34] = 0;
   out_1064691538495726265[35] = 0;
   out_1064691538495726265[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_1064691538495726265[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_1064691538495726265[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_1064691538495726265[39] = 0;
   out_1064691538495726265[40] = 0;
   out_1064691538495726265[41] = 0;
   out_1064691538495726265[42] = 0;
   out_1064691538495726265[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_1064691538495726265[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_1064691538495726265[45] = 0;
   out_1064691538495726265[46] = 0;
   out_1064691538495726265[47] = 0;
   out_1064691538495726265[48] = 0;
   out_1064691538495726265[49] = 0;
   out_1064691538495726265[50] = 0;
   out_1064691538495726265[51] = 0;
   out_1064691538495726265[52] = 0;
   out_1064691538495726265[53] = 0;
   out_1064691538495726265[54] = 0;
   out_1064691538495726265[55] = 0;
   out_1064691538495726265[56] = 0;
   out_1064691538495726265[57] = 1;
   out_1064691538495726265[58] = 0;
   out_1064691538495726265[59] = 0;
   out_1064691538495726265[60] = 0;
   out_1064691538495726265[61] = 0;
   out_1064691538495726265[62] = 0;
   out_1064691538495726265[63] = 0;
   out_1064691538495726265[64] = 0;
   out_1064691538495726265[65] = 0;
   out_1064691538495726265[66] = dt;
   out_1064691538495726265[67] = 0;
   out_1064691538495726265[68] = 0;
   out_1064691538495726265[69] = 0;
   out_1064691538495726265[70] = 0;
   out_1064691538495726265[71] = 0;
   out_1064691538495726265[72] = 0;
   out_1064691538495726265[73] = 0;
   out_1064691538495726265[74] = 0;
   out_1064691538495726265[75] = 0;
   out_1064691538495726265[76] = 1;
   out_1064691538495726265[77] = 0;
   out_1064691538495726265[78] = 0;
   out_1064691538495726265[79] = 0;
   out_1064691538495726265[80] = 0;
   out_1064691538495726265[81] = 0;
   out_1064691538495726265[82] = 0;
   out_1064691538495726265[83] = 0;
   out_1064691538495726265[84] = 0;
   out_1064691538495726265[85] = dt;
   out_1064691538495726265[86] = 0;
   out_1064691538495726265[87] = 0;
   out_1064691538495726265[88] = 0;
   out_1064691538495726265[89] = 0;
   out_1064691538495726265[90] = 0;
   out_1064691538495726265[91] = 0;
   out_1064691538495726265[92] = 0;
   out_1064691538495726265[93] = 0;
   out_1064691538495726265[94] = 0;
   out_1064691538495726265[95] = 1;
   out_1064691538495726265[96] = 0;
   out_1064691538495726265[97] = 0;
   out_1064691538495726265[98] = 0;
   out_1064691538495726265[99] = 0;
   out_1064691538495726265[100] = 0;
   out_1064691538495726265[101] = 0;
   out_1064691538495726265[102] = 0;
   out_1064691538495726265[103] = 0;
   out_1064691538495726265[104] = dt;
   out_1064691538495726265[105] = 0;
   out_1064691538495726265[106] = 0;
   out_1064691538495726265[107] = 0;
   out_1064691538495726265[108] = 0;
   out_1064691538495726265[109] = 0;
   out_1064691538495726265[110] = 0;
   out_1064691538495726265[111] = 0;
   out_1064691538495726265[112] = 0;
   out_1064691538495726265[113] = 0;
   out_1064691538495726265[114] = 1;
   out_1064691538495726265[115] = 0;
   out_1064691538495726265[116] = 0;
   out_1064691538495726265[117] = 0;
   out_1064691538495726265[118] = 0;
   out_1064691538495726265[119] = 0;
   out_1064691538495726265[120] = 0;
   out_1064691538495726265[121] = 0;
   out_1064691538495726265[122] = 0;
   out_1064691538495726265[123] = 0;
   out_1064691538495726265[124] = 0;
   out_1064691538495726265[125] = 0;
   out_1064691538495726265[126] = 0;
   out_1064691538495726265[127] = 0;
   out_1064691538495726265[128] = 0;
   out_1064691538495726265[129] = 0;
   out_1064691538495726265[130] = 0;
   out_1064691538495726265[131] = 0;
   out_1064691538495726265[132] = 0;
   out_1064691538495726265[133] = 1;
   out_1064691538495726265[134] = 0;
   out_1064691538495726265[135] = 0;
   out_1064691538495726265[136] = 0;
   out_1064691538495726265[137] = 0;
   out_1064691538495726265[138] = 0;
   out_1064691538495726265[139] = 0;
   out_1064691538495726265[140] = 0;
   out_1064691538495726265[141] = 0;
   out_1064691538495726265[142] = 0;
   out_1064691538495726265[143] = 0;
   out_1064691538495726265[144] = 0;
   out_1064691538495726265[145] = 0;
   out_1064691538495726265[146] = 0;
   out_1064691538495726265[147] = 0;
   out_1064691538495726265[148] = 0;
   out_1064691538495726265[149] = 0;
   out_1064691538495726265[150] = 0;
   out_1064691538495726265[151] = 0;
   out_1064691538495726265[152] = 1;
   out_1064691538495726265[153] = 0;
   out_1064691538495726265[154] = 0;
   out_1064691538495726265[155] = 0;
   out_1064691538495726265[156] = 0;
   out_1064691538495726265[157] = 0;
   out_1064691538495726265[158] = 0;
   out_1064691538495726265[159] = 0;
   out_1064691538495726265[160] = 0;
   out_1064691538495726265[161] = 0;
   out_1064691538495726265[162] = 0;
   out_1064691538495726265[163] = 0;
   out_1064691538495726265[164] = 0;
   out_1064691538495726265[165] = 0;
   out_1064691538495726265[166] = 0;
   out_1064691538495726265[167] = 0;
   out_1064691538495726265[168] = 0;
   out_1064691538495726265[169] = 0;
   out_1064691538495726265[170] = 0;
   out_1064691538495726265[171] = 1;
   out_1064691538495726265[172] = 0;
   out_1064691538495726265[173] = 0;
   out_1064691538495726265[174] = 0;
   out_1064691538495726265[175] = 0;
   out_1064691538495726265[176] = 0;
   out_1064691538495726265[177] = 0;
   out_1064691538495726265[178] = 0;
   out_1064691538495726265[179] = 0;
   out_1064691538495726265[180] = 0;
   out_1064691538495726265[181] = 0;
   out_1064691538495726265[182] = 0;
   out_1064691538495726265[183] = 0;
   out_1064691538495726265[184] = 0;
   out_1064691538495726265[185] = 0;
   out_1064691538495726265[186] = 0;
   out_1064691538495726265[187] = 0;
   out_1064691538495726265[188] = 0;
   out_1064691538495726265[189] = 0;
   out_1064691538495726265[190] = 1;
   out_1064691538495726265[191] = 0;
   out_1064691538495726265[192] = 0;
   out_1064691538495726265[193] = 0;
   out_1064691538495726265[194] = 0;
   out_1064691538495726265[195] = 0;
   out_1064691538495726265[196] = 0;
   out_1064691538495726265[197] = 0;
   out_1064691538495726265[198] = 0;
   out_1064691538495726265[199] = 0;
   out_1064691538495726265[200] = 0;
   out_1064691538495726265[201] = 0;
   out_1064691538495726265[202] = 0;
   out_1064691538495726265[203] = 0;
   out_1064691538495726265[204] = 0;
   out_1064691538495726265[205] = 0;
   out_1064691538495726265[206] = 0;
   out_1064691538495726265[207] = 0;
   out_1064691538495726265[208] = 0;
   out_1064691538495726265[209] = 1;
   out_1064691538495726265[210] = 0;
   out_1064691538495726265[211] = 0;
   out_1064691538495726265[212] = 0;
   out_1064691538495726265[213] = 0;
   out_1064691538495726265[214] = 0;
   out_1064691538495726265[215] = 0;
   out_1064691538495726265[216] = 0;
   out_1064691538495726265[217] = 0;
   out_1064691538495726265[218] = 0;
   out_1064691538495726265[219] = 0;
   out_1064691538495726265[220] = 0;
   out_1064691538495726265[221] = 0;
   out_1064691538495726265[222] = 0;
   out_1064691538495726265[223] = 0;
   out_1064691538495726265[224] = 0;
   out_1064691538495726265[225] = 0;
   out_1064691538495726265[226] = 0;
   out_1064691538495726265[227] = 0;
   out_1064691538495726265[228] = 1;
   out_1064691538495726265[229] = 0;
   out_1064691538495726265[230] = 0;
   out_1064691538495726265[231] = 0;
   out_1064691538495726265[232] = 0;
   out_1064691538495726265[233] = 0;
   out_1064691538495726265[234] = 0;
   out_1064691538495726265[235] = 0;
   out_1064691538495726265[236] = 0;
   out_1064691538495726265[237] = 0;
   out_1064691538495726265[238] = 0;
   out_1064691538495726265[239] = 0;
   out_1064691538495726265[240] = 0;
   out_1064691538495726265[241] = 0;
   out_1064691538495726265[242] = 0;
   out_1064691538495726265[243] = 0;
   out_1064691538495726265[244] = 0;
   out_1064691538495726265[245] = 0;
   out_1064691538495726265[246] = 0;
   out_1064691538495726265[247] = 1;
   out_1064691538495726265[248] = 0;
   out_1064691538495726265[249] = 0;
   out_1064691538495726265[250] = 0;
   out_1064691538495726265[251] = 0;
   out_1064691538495726265[252] = 0;
   out_1064691538495726265[253] = 0;
   out_1064691538495726265[254] = 0;
   out_1064691538495726265[255] = 0;
   out_1064691538495726265[256] = 0;
   out_1064691538495726265[257] = 0;
   out_1064691538495726265[258] = 0;
   out_1064691538495726265[259] = 0;
   out_1064691538495726265[260] = 0;
   out_1064691538495726265[261] = 0;
   out_1064691538495726265[262] = 0;
   out_1064691538495726265[263] = 0;
   out_1064691538495726265[264] = 0;
   out_1064691538495726265[265] = 0;
   out_1064691538495726265[266] = 1;
   out_1064691538495726265[267] = 0;
   out_1064691538495726265[268] = 0;
   out_1064691538495726265[269] = 0;
   out_1064691538495726265[270] = 0;
   out_1064691538495726265[271] = 0;
   out_1064691538495726265[272] = 0;
   out_1064691538495726265[273] = 0;
   out_1064691538495726265[274] = 0;
   out_1064691538495726265[275] = 0;
   out_1064691538495726265[276] = 0;
   out_1064691538495726265[277] = 0;
   out_1064691538495726265[278] = 0;
   out_1064691538495726265[279] = 0;
   out_1064691538495726265[280] = 0;
   out_1064691538495726265[281] = 0;
   out_1064691538495726265[282] = 0;
   out_1064691538495726265[283] = 0;
   out_1064691538495726265[284] = 0;
   out_1064691538495726265[285] = 1;
   out_1064691538495726265[286] = 0;
   out_1064691538495726265[287] = 0;
   out_1064691538495726265[288] = 0;
   out_1064691538495726265[289] = 0;
   out_1064691538495726265[290] = 0;
   out_1064691538495726265[291] = 0;
   out_1064691538495726265[292] = 0;
   out_1064691538495726265[293] = 0;
   out_1064691538495726265[294] = 0;
   out_1064691538495726265[295] = 0;
   out_1064691538495726265[296] = 0;
   out_1064691538495726265[297] = 0;
   out_1064691538495726265[298] = 0;
   out_1064691538495726265[299] = 0;
   out_1064691538495726265[300] = 0;
   out_1064691538495726265[301] = 0;
   out_1064691538495726265[302] = 0;
   out_1064691538495726265[303] = 0;
   out_1064691538495726265[304] = 1;
   out_1064691538495726265[305] = 0;
   out_1064691538495726265[306] = 0;
   out_1064691538495726265[307] = 0;
   out_1064691538495726265[308] = 0;
   out_1064691538495726265[309] = 0;
   out_1064691538495726265[310] = 0;
   out_1064691538495726265[311] = 0;
   out_1064691538495726265[312] = 0;
   out_1064691538495726265[313] = 0;
   out_1064691538495726265[314] = 0;
   out_1064691538495726265[315] = 0;
   out_1064691538495726265[316] = 0;
   out_1064691538495726265[317] = 0;
   out_1064691538495726265[318] = 0;
   out_1064691538495726265[319] = 0;
   out_1064691538495726265[320] = 0;
   out_1064691538495726265[321] = 0;
   out_1064691538495726265[322] = 0;
   out_1064691538495726265[323] = 1;
}
void h_4(double *state, double *unused, double *out_5786601062018184200) {
   out_5786601062018184200[0] = state[6] + state[9];
   out_5786601062018184200[1] = state[7] + state[10];
   out_5786601062018184200[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_8923920068705470393) {
   out_8923920068705470393[0] = 0;
   out_8923920068705470393[1] = 0;
   out_8923920068705470393[2] = 0;
   out_8923920068705470393[3] = 0;
   out_8923920068705470393[4] = 0;
   out_8923920068705470393[5] = 0;
   out_8923920068705470393[6] = 1;
   out_8923920068705470393[7] = 0;
   out_8923920068705470393[8] = 0;
   out_8923920068705470393[9] = 1;
   out_8923920068705470393[10] = 0;
   out_8923920068705470393[11] = 0;
   out_8923920068705470393[12] = 0;
   out_8923920068705470393[13] = 0;
   out_8923920068705470393[14] = 0;
   out_8923920068705470393[15] = 0;
   out_8923920068705470393[16] = 0;
   out_8923920068705470393[17] = 0;
   out_8923920068705470393[18] = 0;
   out_8923920068705470393[19] = 0;
   out_8923920068705470393[20] = 0;
   out_8923920068705470393[21] = 0;
   out_8923920068705470393[22] = 0;
   out_8923920068705470393[23] = 0;
   out_8923920068705470393[24] = 0;
   out_8923920068705470393[25] = 1;
   out_8923920068705470393[26] = 0;
   out_8923920068705470393[27] = 0;
   out_8923920068705470393[28] = 1;
   out_8923920068705470393[29] = 0;
   out_8923920068705470393[30] = 0;
   out_8923920068705470393[31] = 0;
   out_8923920068705470393[32] = 0;
   out_8923920068705470393[33] = 0;
   out_8923920068705470393[34] = 0;
   out_8923920068705470393[35] = 0;
   out_8923920068705470393[36] = 0;
   out_8923920068705470393[37] = 0;
   out_8923920068705470393[38] = 0;
   out_8923920068705470393[39] = 0;
   out_8923920068705470393[40] = 0;
   out_8923920068705470393[41] = 0;
   out_8923920068705470393[42] = 0;
   out_8923920068705470393[43] = 0;
   out_8923920068705470393[44] = 1;
   out_8923920068705470393[45] = 0;
   out_8923920068705470393[46] = 0;
   out_8923920068705470393[47] = 1;
   out_8923920068705470393[48] = 0;
   out_8923920068705470393[49] = 0;
   out_8923920068705470393[50] = 0;
   out_8923920068705470393[51] = 0;
   out_8923920068705470393[52] = 0;
   out_8923920068705470393[53] = 0;
}
void h_10(double *state, double *unused, double *out_8200446056116706374) {
   out_8200446056116706374[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_8200446056116706374[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_8200446056116706374[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_8156688557227160880) {
   out_8156688557227160880[0] = 0;
   out_8156688557227160880[1] = 9.8100000000000005*cos(state[1]);
   out_8156688557227160880[2] = 0;
   out_8156688557227160880[3] = 0;
   out_8156688557227160880[4] = -state[8];
   out_8156688557227160880[5] = state[7];
   out_8156688557227160880[6] = 0;
   out_8156688557227160880[7] = state[5];
   out_8156688557227160880[8] = -state[4];
   out_8156688557227160880[9] = 0;
   out_8156688557227160880[10] = 0;
   out_8156688557227160880[11] = 0;
   out_8156688557227160880[12] = 1;
   out_8156688557227160880[13] = 0;
   out_8156688557227160880[14] = 0;
   out_8156688557227160880[15] = 1;
   out_8156688557227160880[16] = 0;
   out_8156688557227160880[17] = 0;
   out_8156688557227160880[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_8156688557227160880[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_8156688557227160880[20] = 0;
   out_8156688557227160880[21] = state[8];
   out_8156688557227160880[22] = 0;
   out_8156688557227160880[23] = -state[6];
   out_8156688557227160880[24] = -state[5];
   out_8156688557227160880[25] = 0;
   out_8156688557227160880[26] = state[3];
   out_8156688557227160880[27] = 0;
   out_8156688557227160880[28] = 0;
   out_8156688557227160880[29] = 0;
   out_8156688557227160880[30] = 0;
   out_8156688557227160880[31] = 1;
   out_8156688557227160880[32] = 0;
   out_8156688557227160880[33] = 0;
   out_8156688557227160880[34] = 1;
   out_8156688557227160880[35] = 0;
   out_8156688557227160880[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_8156688557227160880[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_8156688557227160880[38] = 0;
   out_8156688557227160880[39] = -state[7];
   out_8156688557227160880[40] = state[6];
   out_8156688557227160880[41] = 0;
   out_8156688557227160880[42] = state[4];
   out_8156688557227160880[43] = -state[3];
   out_8156688557227160880[44] = 0;
   out_8156688557227160880[45] = 0;
   out_8156688557227160880[46] = 0;
   out_8156688557227160880[47] = 0;
   out_8156688557227160880[48] = 0;
   out_8156688557227160880[49] = 0;
   out_8156688557227160880[50] = 1;
   out_8156688557227160880[51] = 0;
   out_8156688557227160880[52] = 0;
   out_8156688557227160880[53] = 1;
}
void h_13(double *state, double *unused, double *out_9145870174400750931) {
   out_9145870174400750931[0] = state[3];
   out_9145870174400750931[1] = state[4];
   out_9145870174400750931[2] = state[5];
}
void H_13(double *state, double *unused, double *out_5711646243373137592) {
   out_5711646243373137592[0] = 0;
   out_5711646243373137592[1] = 0;
   out_5711646243373137592[2] = 0;
   out_5711646243373137592[3] = 1;
   out_5711646243373137592[4] = 0;
   out_5711646243373137592[5] = 0;
   out_5711646243373137592[6] = 0;
   out_5711646243373137592[7] = 0;
   out_5711646243373137592[8] = 0;
   out_5711646243373137592[9] = 0;
   out_5711646243373137592[10] = 0;
   out_5711646243373137592[11] = 0;
   out_5711646243373137592[12] = 0;
   out_5711646243373137592[13] = 0;
   out_5711646243373137592[14] = 0;
   out_5711646243373137592[15] = 0;
   out_5711646243373137592[16] = 0;
   out_5711646243373137592[17] = 0;
   out_5711646243373137592[18] = 0;
   out_5711646243373137592[19] = 0;
   out_5711646243373137592[20] = 0;
   out_5711646243373137592[21] = 0;
   out_5711646243373137592[22] = 1;
   out_5711646243373137592[23] = 0;
   out_5711646243373137592[24] = 0;
   out_5711646243373137592[25] = 0;
   out_5711646243373137592[26] = 0;
   out_5711646243373137592[27] = 0;
   out_5711646243373137592[28] = 0;
   out_5711646243373137592[29] = 0;
   out_5711646243373137592[30] = 0;
   out_5711646243373137592[31] = 0;
   out_5711646243373137592[32] = 0;
   out_5711646243373137592[33] = 0;
   out_5711646243373137592[34] = 0;
   out_5711646243373137592[35] = 0;
   out_5711646243373137592[36] = 0;
   out_5711646243373137592[37] = 0;
   out_5711646243373137592[38] = 0;
   out_5711646243373137592[39] = 0;
   out_5711646243373137592[40] = 0;
   out_5711646243373137592[41] = 1;
   out_5711646243373137592[42] = 0;
   out_5711646243373137592[43] = 0;
   out_5711646243373137592[44] = 0;
   out_5711646243373137592[45] = 0;
   out_5711646243373137592[46] = 0;
   out_5711646243373137592[47] = 0;
   out_5711646243373137592[48] = 0;
   out_5711646243373137592[49] = 0;
   out_5711646243373137592[50] = 0;
   out_5711646243373137592[51] = 0;
   out_5711646243373137592[52] = 0;
   out_5711646243373137592[53] = 0;
}
void h_14(double *state, double *unused, double *out_5989511771500844071) {
   out_5989511771500844071[0] = state[6];
   out_5989511771500844071[1] = state[7];
   out_5989511771500844071[2] = state[8];
}
void H_14(double *state, double *unused, double *out_6440035572708708927) {
   out_6440035572708708927[0] = 0;
   out_6440035572708708927[1] = 0;
   out_6440035572708708927[2] = 0;
   out_6440035572708708927[3] = 0;
   out_6440035572708708927[4] = 0;
   out_6440035572708708927[5] = 0;
   out_6440035572708708927[6] = 1;
   out_6440035572708708927[7] = 0;
   out_6440035572708708927[8] = 0;
   out_6440035572708708927[9] = 0;
   out_6440035572708708927[10] = 0;
   out_6440035572708708927[11] = 0;
   out_6440035572708708927[12] = 0;
   out_6440035572708708927[13] = 0;
   out_6440035572708708927[14] = 0;
   out_6440035572708708927[15] = 0;
   out_6440035572708708927[16] = 0;
   out_6440035572708708927[17] = 0;
   out_6440035572708708927[18] = 0;
   out_6440035572708708927[19] = 0;
   out_6440035572708708927[20] = 0;
   out_6440035572708708927[21] = 0;
   out_6440035572708708927[22] = 0;
   out_6440035572708708927[23] = 0;
   out_6440035572708708927[24] = 0;
   out_6440035572708708927[25] = 1;
   out_6440035572708708927[26] = 0;
   out_6440035572708708927[27] = 0;
   out_6440035572708708927[28] = 0;
   out_6440035572708708927[29] = 0;
   out_6440035572708708927[30] = 0;
   out_6440035572708708927[31] = 0;
   out_6440035572708708927[32] = 0;
   out_6440035572708708927[33] = 0;
   out_6440035572708708927[34] = 0;
   out_6440035572708708927[35] = 0;
   out_6440035572708708927[36] = 0;
   out_6440035572708708927[37] = 0;
   out_6440035572708708927[38] = 0;
   out_6440035572708708927[39] = 0;
   out_6440035572708708927[40] = 0;
   out_6440035572708708927[41] = 0;
   out_6440035572708708927[42] = 0;
   out_6440035572708708927[43] = 0;
   out_6440035572708708927[44] = 1;
   out_6440035572708708927[45] = 0;
   out_6440035572708708927[46] = 0;
   out_6440035572708708927[47] = 0;
   out_6440035572708708927[48] = 0;
   out_6440035572708708927[49] = 0;
   out_6440035572708708927[50] = 0;
   out_6440035572708708927[51] = 0;
   out_6440035572708708927[52] = 0;
   out_6440035572708708927[53] = 0;
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
void pose_err_fun(double *nom_x, double *delta_x, double *out_1372154176746733435) {
  err_fun(nom_x, delta_x, out_1372154176746733435);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_1523580565963320994) {
  inv_err_fun(nom_x, true_x, out_1523580565963320994);
}
void pose_H_mod_fun(double *state, double *out_7104221342799173532) {
  H_mod_fun(state, out_7104221342799173532);
}
void pose_f_fun(double *state, double dt, double *out_7349931890006772642) {
  f_fun(state,  dt, out_7349931890006772642);
}
void pose_F_fun(double *state, double dt, double *out_1064691538495726265) {
  F_fun(state,  dt, out_1064691538495726265);
}
void pose_h_4(double *state, double *unused, double *out_5786601062018184200) {
  h_4(state, unused, out_5786601062018184200);
}
void pose_H_4(double *state, double *unused, double *out_8923920068705470393) {
  H_4(state, unused, out_8923920068705470393);
}
void pose_h_10(double *state, double *unused, double *out_8200446056116706374) {
  h_10(state, unused, out_8200446056116706374);
}
void pose_H_10(double *state, double *unused, double *out_8156688557227160880) {
  H_10(state, unused, out_8156688557227160880);
}
void pose_h_13(double *state, double *unused, double *out_9145870174400750931) {
  h_13(state, unused, out_9145870174400750931);
}
void pose_H_13(double *state, double *unused, double *out_5711646243373137592) {
  H_13(state, unused, out_5711646243373137592);
}
void pose_h_14(double *state, double *unused, double *out_5989511771500844071) {
  h_14(state, unused, out_5989511771500844071);
}
void pose_H_14(double *state, double *unused, double *out_6440035572708708927) {
  H_14(state, unused, out_6440035572708708927);
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
