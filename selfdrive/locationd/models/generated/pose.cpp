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
void err_fun(double *nom_x, double *delta_x, double *out_8901306953069029009) {
   out_8901306953069029009[0] = delta_x[0] + nom_x[0];
   out_8901306953069029009[1] = delta_x[1] + nom_x[1];
   out_8901306953069029009[2] = delta_x[2] + nom_x[2];
   out_8901306953069029009[3] = delta_x[3] + nom_x[3];
   out_8901306953069029009[4] = delta_x[4] + nom_x[4];
   out_8901306953069029009[5] = delta_x[5] + nom_x[5];
   out_8901306953069029009[6] = delta_x[6] + nom_x[6];
   out_8901306953069029009[7] = delta_x[7] + nom_x[7];
   out_8901306953069029009[8] = delta_x[8] + nom_x[8];
   out_8901306953069029009[9] = delta_x[9] + nom_x[9];
   out_8901306953069029009[10] = delta_x[10] + nom_x[10];
   out_8901306953069029009[11] = delta_x[11] + nom_x[11];
   out_8901306953069029009[12] = delta_x[12] + nom_x[12];
   out_8901306953069029009[13] = delta_x[13] + nom_x[13];
   out_8901306953069029009[14] = delta_x[14] + nom_x[14];
   out_8901306953069029009[15] = delta_x[15] + nom_x[15];
   out_8901306953069029009[16] = delta_x[16] + nom_x[16];
   out_8901306953069029009[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_5676752390099238868) {
   out_5676752390099238868[0] = -nom_x[0] + true_x[0];
   out_5676752390099238868[1] = -nom_x[1] + true_x[1];
   out_5676752390099238868[2] = -nom_x[2] + true_x[2];
   out_5676752390099238868[3] = -nom_x[3] + true_x[3];
   out_5676752390099238868[4] = -nom_x[4] + true_x[4];
   out_5676752390099238868[5] = -nom_x[5] + true_x[5];
   out_5676752390099238868[6] = -nom_x[6] + true_x[6];
   out_5676752390099238868[7] = -nom_x[7] + true_x[7];
   out_5676752390099238868[8] = -nom_x[8] + true_x[8];
   out_5676752390099238868[9] = -nom_x[9] + true_x[9];
   out_5676752390099238868[10] = -nom_x[10] + true_x[10];
   out_5676752390099238868[11] = -nom_x[11] + true_x[11];
   out_5676752390099238868[12] = -nom_x[12] + true_x[12];
   out_5676752390099238868[13] = -nom_x[13] + true_x[13];
   out_5676752390099238868[14] = -nom_x[14] + true_x[14];
   out_5676752390099238868[15] = -nom_x[15] + true_x[15];
   out_5676752390099238868[16] = -nom_x[16] + true_x[16];
   out_5676752390099238868[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_906252113673065885) {
   out_906252113673065885[0] = 1.0;
   out_906252113673065885[1] = 0.0;
   out_906252113673065885[2] = 0.0;
   out_906252113673065885[3] = 0.0;
   out_906252113673065885[4] = 0.0;
   out_906252113673065885[5] = 0.0;
   out_906252113673065885[6] = 0.0;
   out_906252113673065885[7] = 0.0;
   out_906252113673065885[8] = 0.0;
   out_906252113673065885[9] = 0.0;
   out_906252113673065885[10] = 0.0;
   out_906252113673065885[11] = 0.0;
   out_906252113673065885[12] = 0.0;
   out_906252113673065885[13] = 0.0;
   out_906252113673065885[14] = 0.0;
   out_906252113673065885[15] = 0.0;
   out_906252113673065885[16] = 0.0;
   out_906252113673065885[17] = 0.0;
   out_906252113673065885[18] = 0.0;
   out_906252113673065885[19] = 1.0;
   out_906252113673065885[20] = 0.0;
   out_906252113673065885[21] = 0.0;
   out_906252113673065885[22] = 0.0;
   out_906252113673065885[23] = 0.0;
   out_906252113673065885[24] = 0.0;
   out_906252113673065885[25] = 0.0;
   out_906252113673065885[26] = 0.0;
   out_906252113673065885[27] = 0.0;
   out_906252113673065885[28] = 0.0;
   out_906252113673065885[29] = 0.0;
   out_906252113673065885[30] = 0.0;
   out_906252113673065885[31] = 0.0;
   out_906252113673065885[32] = 0.0;
   out_906252113673065885[33] = 0.0;
   out_906252113673065885[34] = 0.0;
   out_906252113673065885[35] = 0.0;
   out_906252113673065885[36] = 0.0;
   out_906252113673065885[37] = 0.0;
   out_906252113673065885[38] = 1.0;
   out_906252113673065885[39] = 0.0;
   out_906252113673065885[40] = 0.0;
   out_906252113673065885[41] = 0.0;
   out_906252113673065885[42] = 0.0;
   out_906252113673065885[43] = 0.0;
   out_906252113673065885[44] = 0.0;
   out_906252113673065885[45] = 0.0;
   out_906252113673065885[46] = 0.0;
   out_906252113673065885[47] = 0.0;
   out_906252113673065885[48] = 0.0;
   out_906252113673065885[49] = 0.0;
   out_906252113673065885[50] = 0.0;
   out_906252113673065885[51] = 0.0;
   out_906252113673065885[52] = 0.0;
   out_906252113673065885[53] = 0.0;
   out_906252113673065885[54] = 0.0;
   out_906252113673065885[55] = 0.0;
   out_906252113673065885[56] = 0.0;
   out_906252113673065885[57] = 1.0;
   out_906252113673065885[58] = 0.0;
   out_906252113673065885[59] = 0.0;
   out_906252113673065885[60] = 0.0;
   out_906252113673065885[61] = 0.0;
   out_906252113673065885[62] = 0.0;
   out_906252113673065885[63] = 0.0;
   out_906252113673065885[64] = 0.0;
   out_906252113673065885[65] = 0.0;
   out_906252113673065885[66] = 0.0;
   out_906252113673065885[67] = 0.0;
   out_906252113673065885[68] = 0.0;
   out_906252113673065885[69] = 0.0;
   out_906252113673065885[70] = 0.0;
   out_906252113673065885[71] = 0.0;
   out_906252113673065885[72] = 0.0;
   out_906252113673065885[73] = 0.0;
   out_906252113673065885[74] = 0.0;
   out_906252113673065885[75] = 0.0;
   out_906252113673065885[76] = 1.0;
   out_906252113673065885[77] = 0.0;
   out_906252113673065885[78] = 0.0;
   out_906252113673065885[79] = 0.0;
   out_906252113673065885[80] = 0.0;
   out_906252113673065885[81] = 0.0;
   out_906252113673065885[82] = 0.0;
   out_906252113673065885[83] = 0.0;
   out_906252113673065885[84] = 0.0;
   out_906252113673065885[85] = 0.0;
   out_906252113673065885[86] = 0.0;
   out_906252113673065885[87] = 0.0;
   out_906252113673065885[88] = 0.0;
   out_906252113673065885[89] = 0.0;
   out_906252113673065885[90] = 0.0;
   out_906252113673065885[91] = 0.0;
   out_906252113673065885[92] = 0.0;
   out_906252113673065885[93] = 0.0;
   out_906252113673065885[94] = 0.0;
   out_906252113673065885[95] = 1.0;
   out_906252113673065885[96] = 0.0;
   out_906252113673065885[97] = 0.0;
   out_906252113673065885[98] = 0.0;
   out_906252113673065885[99] = 0.0;
   out_906252113673065885[100] = 0.0;
   out_906252113673065885[101] = 0.0;
   out_906252113673065885[102] = 0.0;
   out_906252113673065885[103] = 0.0;
   out_906252113673065885[104] = 0.0;
   out_906252113673065885[105] = 0.0;
   out_906252113673065885[106] = 0.0;
   out_906252113673065885[107] = 0.0;
   out_906252113673065885[108] = 0.0;
   out_906252113673065885[109] = 0.0;
   out_906252113673065885[110] = 0.0;
   out_906252113673065885[111] = 0.0;
   out_906252113673065885[112] = 0.0;
   out_906252113673065885[113] = 0.0;
   out_906252113673065885[114] = 1.0;
   out_906252113673065885[115] = 0.0;
   out_906252113673065885[116] = 0.0;
   out_906252113673065885[117] = 0.0;
   out_906252113673065885[118] = 0.0;
   out_906252113673065885[119] = 0.0;
   out_906252113673065885[120] = 0.0;
   out_906252113673065885[121] = 0.0;
   out_906252113673065885[122] = 0.0;
   out_906252113673065885[123] = 0.0;
   out_906252113673065885[124] = 0.0;
   out_906252113673065885[125] = 0.0;
   out_906252113673065885[126] = 0.0;
   out_906252113673065885[127] = 0.0;
   out_906252113673065885[128] = 0.0;
   out_906252113673065885[129] = 0.0;
   out_906252113673065885[130] = 0.0;
   out_906252113673065885[131] = 0.0;
   out_906252113673065885[132] = 0.0;
   out_906252113673065885[133] = 1.0;
   out_906252113673065885[134] = 0.0;
   out_906252113673065885[135] = 0.0;
   out_906252113673065885[136] = 0.0;
   out_906252113673065885[137] = 0.0;
   out_906252113673065885[138] = 0.0;
   out_906252113673065885[139] = 0.0;
   out_906252113673065885[140] = 0.0;
   out_906252113673065885[141] = 0.0;
   out_906252113673065885[142] = 0.0;
   out_906252113673065885[143] = 0.0;
   out_906252113673065885[144] = 0.0;
   out_906252113673065885[145] = 0.0;
   out_906252113673065885[146] = 0.0;
   out_906252113673065885[147] = 0.0;
   out_906252113673065885[148] = 0.0;
   out_906252113673065885[149] = 0.0;
   out_906252113673065885[150] = 0.0;
   out_906252113673065885[151] = 0.0;
   out_906252113673065885[152] = 1.0;
   out_906252113673065885[153] = 0.0;
   out_906252113673065885[154] = 0.0;
   out_906252113673065885[155] = 0.0;
   out_906252113673065885[156] = 0.0;
   out_906252113673065885[157] = 0.0;
   out_906252113673065885[158] = 0.0;
   out_906252113673065885[159] = 0.0;
   out_906252113673065885[160] = 0.0;
   out_906252113673065885[161] = 0.0;
   out_906252113673065885[162] = 0.0;
   out_906252113673065885[163] = 0.0;
   out_906252113673065885[164] = 0.0;
   out_906252113673065885[165] = 0.0;
   out_906252113673065885[166] = 0.0;
   out_906252113673065885[167] = 0.0;
   out_906252113673065885[168] = 0.0;
   out_906252113673065885[169] = 0.0;
   out_906252113673065885[170] = 0.0;
   out_906252113673065885[171] = 1.0;
   out_906252113673065885[172] = 0.0;
   out_906252113673065885[173] = 0.0;
   out_906252113673065885[174] = 0.0;
   out_906252113673065885[175] = 0.0;
   out_906252113673065885[176] = 0.0;
   out_906252113673065885[177] = 0.0;
   out_906252113673065885[178] = 0.0;
   out_906252113673065885[179] = 0.0;
   out_906252113673065885[180] = 0.0;
   out_906252113673065885[181] = 0.0;
   out_906252113673065885[182] = 0.0;
   out_906252113673065885[183] = 0.0;
   out_906252113673065885[184] = 0.0;
   out_906252113673065885[185] = 0.0;
   out_906252113673065885[186] = 0.0;
   out_906252113673065885[187] = 0.0;
   out_906252113673065885[188] = 0.0;
   out_906252113673065885[189] = 0.0;
   out_906252113673065885[190] = 1.0;
   out_906252113673065885[191] = 0.0;
   out_906252113673065885[192] = 0.0;
   out_906252113673065885[193] = 0.0;
   out_906252113673065885[194] = 0.0;
   out_906252113673065885[195] = 0.0;
   out_906252113673065885[196] = 0.0;
   out_906252113673065885[197] = 0.0;
   out_906252113673065885[198] = 0.0;
   out_906252113673065885[199] = 0.0;
   out_906252113673065885[200] = 0.0;
   out_906252113673065885[201] = 0.0;
   out_906252113673065885[202] = 0.0;
   out_906252113673065885[203] = 0.0;
   out_906252113673065885[204] = 0.0;
   out_906252113673065885[205] = 0.0;
   out_906252113673065885[206] = 0.0;
   out_906252113673065885[207] = 0.0;
   out_906252113673065885[208] = 0.0;
   out_906252113673065885[209] = 1.0;
   out_906252113673065885[210] = 0.0;
   out_906252113673065885[211] = 0.0;
   out_906252113673065885[212] = 0.0;
   out_906252113673065885[213] = 0.0;
   out_906252113673065885[214] = 0.0;
   out_906252113673065885[215] = 0.0;
   out_906252113673065885[216] = 0.0;
   out_906252113673065885[217] = 0.0;
   out_906252113673065885[218] = 0.0;
   out_906252113673065885[219] = 0.0;
   out_906252113673065885[220] = 0.0;
   out_906252113673065885[221] = 0.0;
   out_906252113673065885[222] = 0.0;
   out_906252113673065885[223] = 0.0;
   out_906252113673065885[224] = 0.0;
   out_906252113673065885[225] = 0.0;
   out_906252113673065885[226] = 0.0;
   out_906252113673065885[227] = 0.0;
   out_906252113673065885[228] = 1.0;
   out_906252113673065885[229] = 0.0;
   out_906252113673065885[230] = 0.0;
   out_906252113673065885[231] = 0.0;
   out_906252113673065885[232] = 0.0;
   out_906252113673065885[233] = 0.0;
   out_906252113673065885[234] = 0.0;
   out_906252113673065885[235] = 0.0;
   out_906252113673065885[236] = 0.0;
   out_906252113673065885[237] = 0.0;
   out_906252113673065885[238] = 0.0;
   out_906252113673065885[239] = 0.0;
   out_906252113673065885[240] = 0.0;
   out_906252113673065885[241] = 0.0;
   out_906252113673065885[242] = 0.0;
   out_906252113673065885[243] = 0.0;
   out_906252113673065885[244] = 0.0;
   out_906252113673065885[245] = 0.0;
   out_906252113673065885[246] = 0.0;
   out_906252113673065885[247] = 1.0;
   out_906252113673065885[248] = 0.0;
   out_906252113673065885[249] = 0.0;
   out_906252113673065885[250] = 0.0;
   out_906252113673065885[251] = 0.0;
   out_906252113673065885[252] = 0.0;
   out_906252113673065885[253] = 0.0;
   out_906252113673065885[254] = 0.0;
   out_906252113673065885[255] = 0.0;
   out_906252113673065885[256] = 0.0;
   out_906252113673065885[257] = 0.0;
   out_906252113673065885[258] = 0.0;
   out_906252113673065885[259] = 0.0;
   out_906252113673065885[260] = 0.0;
   out_906252113673065885[261] = 0.0;
   out_906252113673065885[262] = 0.0;
   out_906252113673065885[263] = 0.0;
   out_906252113673065885[264] = 0.0;
   out_906252113673065885[265] = 0.0;
   out_906252113673065885[266] = 1.0;
   out_906252113673065885[267] = 0.0;
   out_906252113673065885[268] = 0.0;
   out_906252113673065885[269] = 0.0;
   out_906252113673065885[270] = 0.0;
   out_906252113673065885[271] = 0.0;
   out_906252113673065885[272] = 0.0;
   out_906252113673065885[273] = 0.0;
   out_906252113673065885[274] = 0.0;
   out_906252113673065885[275] = 0.0;
   out_906252113673065885[276] = 0.0;
   out_906252113673065885[277] = 0.0;
   out_906252113673065885[278] = 0.0;
   out_906252113673065885[279] = 0.0;
   out_906252113673065885[280] = 0.0;
   out_906252113673065885[281] = 0.0;
   out_906252113673065885[282] = 0.0;
   out_906252113673065885[283] = 0.0;
   out_906252113673065885[284] = 0.0;
   out_906252113673065885[285] = 1.0;
   out_906252113673065885[286] = 0.0;
   out_906252113673065885[287] = 0.0;
   out_906252113673065885[288] = 0.0;
   out_906252113673065885[289] = 0.0;
   out_906252113673065885[290] = 0.0;
   out_906252113673065885[291] = 0.0;
   out_906252113673065885[292] = 0.0;
   out_906252113673065885[293] = 0.0;
   out_906252113673065885[294] = 0.0;
   out_906252113673065885[295] = 0.0;
   out_906252113673065885[296] = 0.0;
   out_906252113673065885[297] = 0.0;
   out_906252113673065885[298] = 0.0;
   out_906252113673065885[299] = 0.0;
   out_906252113673065885[300] = 0.0;
   out_906252113673065885[301] = 0.0;
   out_906252113673065885[302] = 0.0;
   out_906252113673065885[303] = 0.0;
   out_906252113673065885[304] = 1.0;
   out_906252113673065885[305] = 0.0;
   out_906252113673065885[306] = 0.0;
   out_906252113673065885[307] = 0.0;
   out_906252113673065885[308] = 0.0;
   out_906252113673065885[309] = 0.0;
   out_906252113673065885[310] = 0.0;
   out_906252113673065885[311] = 0.0;
   out_906252113673065885[312] = 0.0;
   out_906252113673065885[313] = 0.0;
   out_906252113673065885[314] = 0.0;
   out_906252113673065885[315] = 0.0;
   out_906252113673065885[316] = 0.0;
   out_906252113673065885[317] = 0.0;
   out_906252113673065885[318] = 0.0;
   out_906252113673065885[319] = 0.0;
   out_906252113673065885[320] = 0.0;
   out_906252113673065885[321] = 0.0;
   out_906252113673065885[322] = 0.0;
   out_906252113673065885[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_5850564288516734669) {
   out_5850564288516734669[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_5850564288516734669[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_5850564288516734669[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_5850564288516734669[3] = dt*state[12] + state[3];
   out_5850564288516734669[4] = dt*state[13] + state[4];
   out_5850564288516734669[5] = dt*state[14] + state[5];
   out_5850564288516734669[6] = state[6];
   out_5850564288516734669[7] = state[7];
   out_5850564288516734669[8] = state[8];
   out_5850564288516734669[9] = state[9];
   out_5850564288516734669[10] = state[10];
   out_5850564288516734669[11] = state[11];
   out_5850564288516734669[12] = state[12];
   out_5850564288516734669[13] = state[13];
   out_5850564288516734669[14] = state[14];
   out_5850564288516734669[15] = state[15];
   out_5850564288516734669[16] = state[16];
   out_5850564288516734669[17] = state[17];
}
void F_fun(double *state, double dt, double *out_7498091432372823234) {
   out_7498091432372823234[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_7498091432372823234[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_7498091432372823234[2] = 0;
   out_7498091432372823234[3] = 0;
   out_7498091432372823234[4] = 0;
   out_7498091432372823234[5] = 0;
   out_7498091432372823234[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_7498091432372823234[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_7498091432372823234[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_7498091432372823234[9] = 0;
   out_7498091432372823234[10] = 0;
   out_7498091432372823234[11] = 0;
   out_7498091432372823234[12] = 0;
   out_7498091432372823234[13] = 0;
   out_7498091432372823234[14] = 0;
   out_7498091432372823234[15] = 0;
   out_7498091432372823234[16] = 0;
   out_7498091432372823234[17] = 0;
   out_7498091432372823234[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_7498091432372823234[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_7498091432372823234[20] = 0;
   out_7498091432372823234[21] = 0;
   out_7498091432372823234[22] = 0;
   out_7498091432372823234[23] = 0;
   out_7498091432372823234[24] = 0;
   out_7498091432372823234[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_7498091432372823234[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_7498091432372823234[27] = 0;
   out_7498091432372823234[28] = 0;
   out_7498091432372823234[29] = 0;
   out_7498091432372823234[30] = 0;
   out_7498091432372823234[31] = 0;
   out_7498091432372823234[32] = 0;
   out_7498091432372823234[33] = 0;
   out_7498091432372823234[34] = 0;
   out_7498091432372823234[35] = 0;
   out_7498091432372823234[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_7498091432372823234[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_7498091432372823234[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_7498091432372823234[39] = 0;
   out_7498091432372823234[40] = 0;
   out_7498091432372823234[41] = 0;
   out_7498091432372823234[42] = 0;
   out_7498091432372823234[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_7498091432372823234[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_7498091432372823234[45] = 0;
   out_7498091432372823234[46] = 0;
   out_7498091432372823234[47] = 0;
   out_7498091432372823234[48] = 0;
   out_7498091432372823234[49] = 0;
   out_7498091432372823234[50] = 0;
   out_7498091432372823234[51] = 0;
   out_7498091432372823234[52] = 0;
   out_7498091432372823234[53] = 0;
   out_7498091432372823234[54] = 0;
   out_7498091432372823234[55] = 0;
   out_7498091432372823234[56] = 0;
   out_7498091432372823234[57] = 1;
   out_7498091432372823234[58] = 0;
   out_7498091432372823234[59] = 0;
   out_7498091432372823234[60] = 0;
   out_7498091432372823234[61] = 0;
   out_7498091432372823234[62] = 0;
   out_7498091432372823234[63] = 0;
   out_7498091432372823234[64] = 0;
   out_7498091432372823234[65] = 0;
   out_7498091432372823234[66] = dt;
   out_7498091432372823234[67] = 0;
   out_7498091432372823234[68] = 0;
   out_7498091432372823234[69] = 0;
   out_7498091432372823234[70] = 0;
   out_7498091432372823234[71] = 0;
   out_7498091432372823234[72] = 0;
   out_7498091432372823234[73] = 0;
   out_7498091432372823234[74] = 0;
   out_7498091432372823234[75] = 0;
   out_7498091432372823234[76] = 1;
   out_7498091432372823234[77] = 0;
   out_7498091432372823234[78] = 0;
   out_7498091432372823234[79] = 0;
   out_7498091432372823234[80] = 0;
   out_7498091432372823234[81] = 0;
   out_7498091432372823234[82] = 0;
   out_7498091432372823234[83] = 0;
   out_7498091432372823234[84] = 0;
   out_7498091432372823234[85] = dt;
   out_7498091432372823234[86] = 0;
   out_7498091432372823234[87] = 0;
   out_7498091432372823234[88] = 0;
   out_7498091432372823234[89] = 0;
   out_7498091432372823234[90] = 0;
   out_7498091432372823234[91] = 0;
   out_7498091432372823234[92] = 0;
   out_7498091432372823234[93] = 0;
   out_7498091432372823234[94] = 0;
   out_7498091432372823234[95] = 1;
   out_7498091432372823234[96] = 0;
   out_7498091432372823234[97] = 0;
   out_7498091432372823234[98] = 0;
   out_7498091432372823234[99] = 0;
   out_7498091432372823234[100] = 0;
   out_7498091432372823234[101] = 0;
   out_7498091432372823234[102] = 0;
   out_7498091432372823234[103] = 0;
   out_7498091432372823234[104] = dt;
   out_7498091432372823234[105] = 0;
   out_7498091432372823234[106] = 0;
   out_7498091432372823234[107] = 0;
   out_7498091432372823234[108] = 0;
   out_7498091432372823234[109] = 0;
   out_7498091432372823234[110] = 0;
   out_7498091432372823234[111] = 0;
   out_7498091432372823234[112] = 0;
   out_7498091432372823234[113] = 0;
   out_7498091432372823234[114] = 1;
   out_7498091432372823234[115] = 0;
   out_7498091432372823234[116] = 0;
   out_7498091432372823234[117] = 0;
   out_7498091432372823234[118] = 0;
   out_7498091432372823234[119] = 0;
   out_7498091432372823234[120] = 0;
   out_7498091432372823234[121] = 0;
   out_7498091432372823234[122] = 0;
   out_7498091432372823234[123] = 0;
   out_7498091432372823234[124] = 0;
   out_7498091432372823234[125] = 0;
   out_7498091432372823234[126] = 0;
   out_7498091432372823234[127] = 0;
   out_7498091432372823234[128] = 0;
   out_7498091432372823234[129] = 0;
   out_7498091432372823234[130] = 0;
   out_7498091432372823234[131] = 0;
   out_7498091432372823234[132] = 0;
   out_7498091432372823234[133] = 1;
   out_7498091432372823234[134] = 0;
   out_7498091432372823234[135] = 0;
   out_7498091432372823234[136] = 0;
   out_7498091432372823234[137] = 0;
   out_7498091432372823234[138] = 0;
   out_7498091432372823234[139] = 0;
   out_7498091432372823234[140] = 0;
   out_7498091432372823234[141] = 0;
   out_7498091432372823234[142] = 0;
   out_7498091432372823234[143] = 0;
   out_7498091432372823234[144] = 0;
   out_7498091432372823234[145] = 0;
   out_7498091432372823234[146] = 0;
   out_7498091432372823234[147] = 0;
   out_7498091432372823234[148] = 0;
   out_7498091432372823234[149] = 0;
   out_7498091432372823234[150] = 0;
   out_7498091432372823234[151] = 0;
   out_7498091432372823234[152] = 1;
   out_7498091432372823234[153] = 0;
   out_7498091432372823234[154] = 0;
   out_7498091432372823234[155] = 0;
   out_7498091432372823234[156] = 0;
   out_7498091432372823234[157] = 0;
   out_7498091432372823234[158] = 0;
   out_7498091432372823234[159] = 0;
   out_7498091432372823234[160] = 0;
   out_7498091432372823234[161] = 0;
   out_7498091432372823234[162] = 0;
   out_7498091432372823234[163] = 0;
   out_7498091432372823234[164] = 0;
   out_7498091432372823234[165] = 0;
   out_7498091432372823234[166] = 0;
   out_7498091432372823234[167] = 0;
   out_7498091432372823234[168] = 0;
   out_7498091432372823234[169] = 0;
   out_7498091432372823234[170] = 0;
   out_7498091432372823234[171] = 1;
   out_7498091432372823234[172] = 0;
   out_7498091432372823234[173] = 0;
   out_7498091432372823234[174] = 0;
   out_7498091432372823234[175] = 0;
   out_7498091432372823234[176] = 0;
   out_7498091432372823234[177] = 0;
   out_7498091432372823234[178] = 0;
   out_7498091432372823234[179] = 0;
   out_7498091432372823234[180] = 0;
   out_7498091432372823234[181] = 0;
   out_7498091432372823234[182] = 0;
   out_7498091432372823234[183] = 0;
   out_7498091432372823234[184] = 0;
   out_7498091432372823234[185] = 0;
   out_7498091432372823234[186] = 0;
   out_7498091432372823234[187] = 0;
   out_7498091432372823234[188] = 0;
   out_7498091432372823234[189] = 0;
   out_7498091432372823234[190] = 1;
   out_7498091432372823234[191] = 0;
   out_7498091432372823234[192] = 0;
   out_7498091432372823234[193] = 0;
   out_7498091432372823234[194] = 0;
   out_7498091432372823234[195] = 0;
   out_7498091432372823234[196] = 0;
   out_7498091432372823234[197] = 0;
   out_7498091432372823234[198] = 0;
   out_7498091432372823234[199] = 0;
   out_7498091432372823234[200] = 0;
   out_7498091432372823234[201] = 0;
   out_7498091432372823234[202] = 0;
   out_7498091432372823234[203] = 0;
   out_7498091432372823234[204] = 0;
   out_7498091432372823234[205] = 0;
   out_7498091432372823234[206] = 0;
   out_7498091432372823234[207] = 0;
   out_7498091432372823234[208] = 0;
   out_7498091432372823234[209] = 1;
   out_7498091432372823234[210] = 0;
   out_7498091432372823234[211] = 0;
   out_7498091432372823234[212] = 0;
   out_7498091432372823234[213] = 0;
   out_7498091432372823234[214] = 0;
   out_7498091432372823234[215] = 0;
   out_7498091432372823234[216] = 0;
   out_7498091432372823234[217] = 0;
   out_7498091432372823234[218] = 0;
   out_7498091432372823234[219] = 0;
   out_7498091432372823234[220] = 0;
   out_7498091432372823234[221] = 0;
   out_7498091432372823234[222] = 0;
   out_7498091432372823234[223] = 0;
   out_7498091432372823234[224] = 0;
   out_7498091432372823234[225] = 0;
   out_7498091432372823234[226] = 0;
   out_7498091432372823234[227] = 0;
   out_7498091432372823234[228] = 1;
   out_7498091432372823234[229] = 0;
   out_7498091432372823234[230] = 0;
   out_7498091432372823234[231] = 0;
   out_7498091432372823234[232] = 0;
   out_7498091432372823234[233] = 0;
   out_7498091432372823234[234] = 0;
   out_7498091432372823234[235] = 0;
   out_7498091432372823234[236] = 0;
   out_7498091432372823234[237] = 0;
   out_7498091432372823234[238] = 0;
   out_7498091432372823234[239] = 0;
   out_7498091432372823234[240] = 0;
   out_7498091432372823234[241] = 0;
   out_7498091432372823234[242] = 0;
   out_7498091432372823234[243] = 0;
   out_7498091432372823234[244] = 0;
   out_7498091432372823234[245] = 0;
   out_7498091432372823234[246] = 0;
   out_7498091432372823234[247] = 1;
   out_7498091432372823234[248] = 0;
   out_7498091432372823234[249] = 0;
   out_7498091432372823234[250] = 0;
   out_7498091432372823234[251] = 0;
   out_7498091432372823234[252] = 0;
   out_7498091432372823234[253] = 0;
   out_7498091432372823234[254] = 0;
   out_7498091432372823234[255] = 0;
   out_7498091432372823234[256] = 0;
   out_7498091432372823234[257] = 0;
   out_7498091432372823234[258] = 0;
   out_7498091432372823234[259] = 0;
   out_7498091432372823234[260] = 0;
   out_7498091432372823234[261] = 0;
   out_7498091432372823234[262] = 0;
   out_7498091432372823234[263] = 0;
   out_7498091432372823234[264] = 0;
   out_7498091432372823234[265] = 0;
   out_7498091432372823234[266] = 1;
   out_7498091432372823234[267] = 0;
   out_7498091432372823234[268] = 0;
   out_7498091432372823234[269] = 0;
   out_7498091432372823234[270] = 0;
   out_7498091432372823234[271] = 0;
   out_7498091432372823234[272] = 0;
   out_7498091432372823234[273] = 0;
   out_7498091432372823234[274] = 0;
   out_7498091432372823234[275] = 0;
   out_7498091432372823234[276] = 0;
   out_7498091432372823234[277] = 0;
   out_7498091432372823234[278] = 0;
   out_7498091432372823234[279] = 0;
   out_7498091432372823234[280] = 0;
   out_7498091432372823234[281] = 0;
   out_7498091432372823234[282] = 0;
   out_7498091432372823234[283] = 0;
   out_7498091432372823234[284] = 0;
   out_7498091432372823234[285] = 1;
   out_7498091432372823234[286] = 0;
   out_7498091432372823234[287] = 0;
   out_7498091432372823234[288] = 0;
   out_7498091432372823234[289] = 0;
   out_7498091432372823234[290] = 0;
   out_7498091432372823234[291] = 0;
   out_7498091432372823234[292] = 0;
   out_7498091432372823234[293] = 0;
   out_7498091432372823234[294] = 0;
   out_7498091432372823234[295] = 0;
   out_7498091432372823234[296] = 0;
   out_7498091432372823234[297] = 0;
   out_7498091432372823234[298] = 0;
   out_7498091432372823234[299] = 0;
   out_7498091432372823234[300] = 0;
   out_7498091432372823234[301] = 0;
   out_7498091432372823234[302] = 0;
   out_7498091432372823234[303] = 0;
   out_7498091432372823234[304] = 1;
   out_7498091432372823234[305] = 0;
   out_7498091432372823234[306] = 0;
   out_7498091432372823234[307] = 0;
   out_7498091432372823234[308] = 0;
   out_7498091432372823234[309] = 0;
   out_7498091432372823234[310] = 0;
   out_7498091432372823234[311] = 0;
   out_7498091432372823234[312] = 0;
   out_7498091432372823234[313] = 0;
   out_7498091432372823234[314] = 0;
   out_7498091432372823234[315] = 0;
   out_7498091432372823234[316] = 0;
   out_7498091432372823234[317] = 0;
   out_7498091432372823234[318] = 0;
   out_7498091432372823234[319] = 0;
   out_7498091432372823234[320] = 0;
   out_7498091432372823234[321] = 0;
   out_7498091432372823234[322] = 0;
   out_7498091432372823234[323] = 1;
}
void h_4(double *state, double *unused, double *out_3808668925773133272) {
   out_3808668925773133272[0] = state[6] + state[9];
   out_3808668925773133272[1] = state[7] + state[10];
   out_3808668925773133272[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_6754333920425024606) {
   out_6754333920425024606[0] = 0;
   out_6754333920425024606[1] = 0;
   out_6754333920425024606[2] = 0;
   out_6754333920425024606[3] = 0;
   out_6754333920425024606[4] = 0;
   out_6754333920425024606[5] = 0;
   out_6754333920425024606[6] = 1;
   out_6754333920425024606[7] = 0;
   out_6754333920425024606[8] = 0;
   out_6754333920425024606[9] = 1;
   out_6754333920425024606[10] = 0;
   out_6754333920425024606[11] = 0;
   out_6754333920425024606[12] = 0;
   out_6754333920425024606[13] = 0;
   out_6754333920425024606[14] = 0;
   out_6754333920425024606[15] = 0;
   out_6754333920425024606[16] = 0;
   out_6754333920425024606[17] = 0;
   out_6754333920425024606[18] = 0;
   out_6754333920425024606[19] = 0;
   out_6754333920425024606[20] = 0;
   out_6754333920425024606[21] = 0;
   out_6754333920425024606[22] = 0;
   out_6754333920425024606[23] = 0;
   out_6754333920425024606[24] = 0;
   out_6754333920425024606[25] = 1;
   out_6754333920425024606[26] = 0;
   out_6754333920425024606[27] = 0;
   out_6754333920425024606[28] = 1;
   out_6754333920425024606[29] = 0;
   out_6754333920425024606[30] = 0;
   out_6754333920425024606[31] = 0;
   out_6754333920425024606[32] = 0;
   out_6754333920425024606[33] = 0;
   out_6754333920425024606[34] = 0;
   out_6754333920425024606[35] = 0;
   out_6754333920425024606[36] = 0;
   out_6754333920425024606[37] = 0;
   out_6754333920425024606[38] = 0;
   out_6754333920425024606[39] = 0;
   out_6754333920425024606[40] = 0;
   out_6754333920425024606[41] = 0;
   out_6754333920425024606[42] = 0;
   out_6754333920425024606[43] = 0;
   out_6754333920425024606[44] = 1;
   out_6754333920425024606[45] = 0;
   out_6754333920425024606[46] = 0;
   out_6754333920425024606[47] = 1;
   out_6754333920425024606[48] = 0;
   out_6754333920425024606[49] = 0;
   out_6754333920425024606[50] = 0;
   out_6754333920425024606[51] = 0;
   out_6754333920425024606[52] = 0;
   out_6754333920425024606[53] = 0;
}
void h_10(double *state, double *unused, double *out_810924982525442876) {
   out_810924982525442876[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_810924982525442876[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_810924982525442876[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_653044011191738521) {
   out_653044011191738521[0] = 0;
   out_653044011191738521[1] = 9.8100000000000005*cos(state[1]);
   out_653044011191738521[2] = 0;
   out_653044011191738521[3] = 0;
   out_653044011191738521[4] = -state[8];
   out_653044011191738521[5] = state[7];
   out_653044011191738521[6] = 0;
   out_653044011191738521[7] = state[5];
   out_653044011191738521[8] = -state[4];
   out_653044011191738521[9] = 0;
   out_653044011191738521[10] = 0;
   out_653044011191738521[11] = 0;
   out_653044011191738521[12] = 1;
   out_653044011191738521[13] = 0;
   out_653044011191738521[14] = 0;
   out_653044011191738521[15] = 1;
   out_653044011191738521[16] = 0;
   out_653044011191738521[17] = 0;
   out_653044011191738521[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_653044011191738521[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_653044011191738521[20] = 0;
   out_653044011191738521[21] = state[8];
   out_653044011191738521[22] = 0;
   out_653044011191738521[23] = -state[6];
   out_653044011191738521[24] = -state[5];
   out_653044011191738521[25] = 0;
   out_653044011191738521[26] = state[3];
   out_653044011191738521[27] = 0;
   out_653044011191738521[28] = 0;
   out_653044011191738521[29] = 0;
   out_653044011191738521[30] = 0;
   out_653044011191738521[31] = 1;
   out_653044011191738521[32] = 0;
   out_653044011191738521[33] = 0;
   out_653044011191738521[34] = 1;
   out_653044011191738521[35] = 0;
   out_653044011191738521[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_653044011191738521[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_653044011191738521[38] = 0;
   out_653044011191738521[39] = -state[7];
   out_653044011191738521[40] = state[6];
   out_653044011191738521[41] = 0;
   out_653044011191738521[42] = state[4];
   out_653044011191738521[43] = -state[3];
   out_653044011191738521[44] = 0;
   out_653044011191738521[45] = 0;
   out_653044011191738521[46] = 0;
   out_653044011191738521[47] = 0;
   out_653044011191738521[48] = 0;
   out_653044011191738521[49] = 0;
   out_653044011191738521[50] = 1;
   out_653044011191738521[51] = 0;
   out_653044011191738521[52] = 0;
   out_653044011191738521[53] = 1;
}
void h_13(double *state, double *unused, double *out_2288129125178979412) {
   out_2288129125178979412[0] = state[3];
   out_2288129125178979412[1] = state[4];
   out_2288129125178979412[2] = state[5];
}
void H_13(double *state, double *unused, double *out_3542060095092691805) {
   out_3542060095092691805[0] = 0;
   out_3542060095092691805[1] = 0;
   out_3542060095092691805[2] = 0;
   out_3542060095092691805[3] = 1;
   out_3542060095092691805[4] = 0;
   out_3542060095092691805[5] = 0;
   out_3542060095092691805[6] = 0;
   out_3542060095092691805[7] = 0;
   out_3542060095092691805[8] = 0;
   out_3542060095092691805[9] = 0;
   out_3542060095092691805[10] = 0;
   out_3542060095092691805[11] = 0;
   out_3542060095092691805[12] = 0;
   out_3542060095092691805[13] = 0;
   out_3542060095092691805[14] = 0;
   out_3542060095092691805[15] = 0;
   out_3542060095092691805[16] = 0;
   out_3542060095092691805[17] = 0;
   out_3542060095092691805[18] = 0;
   out_3542060095092691805[19] = 0;
   out_3542060095092691805[20] = 0;
   out_3542060095092691805[21] = 0;
   out_3542060095092691805[22] = 1;
   out_3542060095092691805[23] = 0;
   out_3542060095092691805[24] = 0;
   out_3542060095092691805[25] = 0;
   out_3542060095092691805[26] = 0;
   out_3542060095092691805[27] = 0;
   out_3542060095092691805[28] = 0;
   out_3542060095092691805[29] = 0;
   out_3542060095092691805[30] = 0;
   out_3542060095092691805[31] = 0;
   out_3542060095092691805[32] = 0;
   out_3542060095092691805[33] = 0;
   out_3542060095092691805[34] = 0;
   out_3542060095092691805[35] = 0;
   out_3542060095092691805[36] = 0;
   out_3542060095092691805[37] = 0;
   out_3542060095092691805[38] = 0;
   out_3542060095092691805[39] = 0;
   out_3542060095092691805[40] = 0;
   out_3542060095092691805[41] = 1;
   out_3542060095092691805[42] = 0;
   out_3542060095092691805[43] = 0;
   out_3542060095092691805[44] = 0;
   out_3542060095092691805[45] = 0;
   out_3542060095092691805[46] = 0;
   out_3542060095092691805[47] = 0;
   out_3542060095092691805[48] = 0;
   out_3542060095092691805[49] = 0;
   out_3542060095092691805[50] = 0;
   out_3542060095092691805[51] = 0;
   out_3542060095092691805[52] = 0;
   out_3542060095092691805[53] = 0;
}
void h_14(double *state, double *unused, double *out_732552053741622262) {
   out_732552053741622262[0] = state[6];
   out_732552053741622262[1] = state[7];
   out_732552053741622262[2] = state[8];
}
void H_14(double *state, double *unused, double *out_2791093064085540077) {
   out_2791093064085540077[0] = 0;
   out_2791093064085540077[1] = 0;
   out_2791093064085540077[2] = 0;
   out_2791093064085540077[3] = 0;
   out_2791093064085540077[4] = 0;
   out_2791093064085540077[5] = 0;
   out_2791093064085540077[6] = 1;
   out_2791093064085540077[7] = 0;
   out_2791093064085540077[8] = 0;
   out_2791093064085540077[9] = 0;
   out_2791093064085540077[10] = 0;
   out_2791093064085540077[11] = 0;
   out_2791093064085540077[12] = 0;
   out_2791093064085540077[13] = 0;
   out_2791093064085540077[14] = 0;
   out_2791093064085540077[15] = 0;
   out_2791093064085540077[16] = 0;
   out_2791093064085540077[17] = 0;
   out_2791093064085540077[18] = 0;
   out_2791093064085540077[19] = 0;
   out_2791093064085540077[20] = 0;
   out_2791093064085540077[21] = 0;
   out_2791093064085540077[22] = 0;
   out_2791093064085540077[23] = 0;
   out_2791093064085540077[24] = 0;
   out_2791093064085540077[25] = 1;
   out_2791093064085540077[26] = 0;
   out_2791093064085540077[27] = 0;
   out_2791093064085540077[28] = 0;
   out_2791093064085540077[29] = 0;
   out_2791093064085540077[30] = 0;
   out_2791093064085540077[31] = 0;
   out_2791093064085540077[32] = 0;
   out_2791093064085540077[33] = 0;
   out_2791093064085540077[34] = 0;
   out_2791093064085540077[35] = 0;
   out_2791093064085540077[36] = 0;
   out_2791093064085540077[37] = 0;
   out_2791093064085540077[38] = 0;
   out_2791093064085540077[39] = 0;
   out_2791093064085540077[40] = 0;
   out_2791093064085540077[41] = 0;
   out_2791093064085540077[42] = 0;
   out_2791093064085540077[43] = 0;
   out_2791093064085540077[44] = 1;
   out_2791093064085540077[45] = 0;
   out_2791093064085540077[46] = 0;
   out_2791093064085540077[47] = 0;
   out_2791093064085540077[48] = 0;
   out_2791093064085540077[49] = 0;
   out_2791093064085540077[50] = 0;
   out_2791093064085540077[51] = 0;
   out_2791093064085540077[52] = 0;
   out_2791093064085540077[53] = 0;
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
void pose_err_fun(double *nom_x, double *delta_x, double *out_8901306953069029009) {
  err_fun(nom_x, delta_x, out_8901306953069029009);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_5676752390099238868) {
  inv_err_fun(nom_x, true_x, out_5676752390099238868);
}
void pose_H_mod_fun(double *state, double *out_906252113673065885) {
  H_mod_fun(state, out_906252113673065885);
}
void pose_f_fun(double *state, double dt, double *out_5850564288516734669) {
  f_fun(state,  dt, out_5850564288516734669);
}
void pose_F_fun(double *state, double dt, double *out_7498091432372823234) {
  F_fun(state,  dt, out_7498091432372823234);
}
void pose_h_4(double *state, double *unused, double *out_3808668925773133272) {
  h_4(state, unused, out_3808668925773133272);
}
void pose_H_4(double *state, double *unused, double *out_6754333920425024606) {
  H_4(state, unused, out_6754333920425024606);
}
void pose_h_10(double *state, double *unused, double *out_810924982525442876) {
  h_10(state, unused, out_810924982525442876);
}
void pose_H_10(double *state, double *unused, double *out_653044011191738521) {
  H_10(state, unused, out_653044011191738521);
}
void pose_h_13(double *state, double *unused, double *out_2288129125178979412) {
  h_13(state, unused, out_2288129125178979412);
}
void pose_H_13(double *state, double *unused, double *out_3542060095092691805) {
  H_13(state, unused, out_3542060095092691805);
}
void pose_h_14(double *state, double *unused, double *out_732552053741622262) {
  h_14(state, unused, out_732552053741622262);
}
void pose_H_14(double *state, double *unused, double *out_2791093064085540077) {
  H_14(state, unused, out_2791093064085540077);
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
