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
void err_fun(double *nom_x, double *delta_x, double *out_920130119510719117) {
   out_920130119510719117[0] = delta_x[0] + nom_x[0];
   out_920130119510719117[1] = delta_x[1] + nom_x[1];
   out_920130119510719117[2] = delta_x[2] + nom_x[2];
   out_920130119510719117[3] = delta_x[3] + nom_x[3];
   out_920130119510719117[4] = delta_x[4] + nom_x[4];
   out_920130119510719117[5] = delta_x[5] + nom_x[5];
   out_920130119510719117[6] = delta_x[6] + nom_x[6];
   out_920130119510719117[7] = delta_x[7] + nom_x[7];
   out_920130119510719117[8] = delta_x[8] + nom_x[8];
   out_920130119510719117[9] = delta_x[9] + nom_x[9];
   out_920130119510719117[10] = delta_x[10] + nom_x[10];
   out_920130119510719117[11] = delta_x[11] + nom_x[11];
   out_920130119510719117[12] = delta_x[12] + nom_x[12];
   out_920130119510719117[13] = delta_x[13] + nom_x[13];
   out_920130119510719117[14] = delta_x[14] + nom_x[14];
   out_920130119510719117[15] = delta_x[15] + nom_x[15];
   out_920130119510719117[16] = delta_x[16] + nom_x[16];
   out_920130119510719117[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_4602168207176775062) {
   out_4602168207176775062[0] = -nom_x[0] + true_x[0];
   out_4602168207176775062[1] = -nom_x[1] + true_x[1];
   out_4602168207176775062[2] = -nom_x[2] + true_x[2];
   out_4602168207176775062[3] = -nom_x[3] + true_x[3];
   out_4602168207176775062[4] = -nom_x[4] + true_x[4];
   out_4602168207176775062[5] = -nom_x[5] + true_x[5];
   out_4602168207176775062[6] = -nom_x[6] + true_x[6];
   out_4602168207176775062[7] = -nom_x[7] + true_x[7];
   out_4602168207176775062[8] = -nom_x[8] + true_x[8];
   out_4602168207176775062[9] = -nom_x[9] + true_x[9];
   out_4602168207176775062[10] = -nom_x[10] + true_x[10];
   out_4602168207176775062[11] = -nom_x[11] + true_x[11];
   out_4602168207176775062[12] = -nom_x[12] + true_x[12];
   out_4602168207176775062[13] = -nom_x[13] + true_x[13];
   out_4602168207176775062[14] = -nom_x[14] + true_x[14];
   out_4602168207176775062[15] = -nom_x[15] + true_x[15];
   out_4602168207176775062[16] = -nom_x[16] + true_x[16];
   out_4602168207176775062[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_1639299711796095424) {
   out_1639299711796095424[0] = 1.0;
   out_1639299711796095424[1] = 0.0;
   out_1639299711796095424[2] = 0.0;
   out_1639299711796095424[3] = 0.0;
   out_1639299711796095424[4] = 0.0;
   out_1639299711796095424[5] = 0.0;
   out_1639299711796095424[6] = 0.0;
   out_1639299711796095424[7] = 0.0;
   out_1639299711796095424[8] = 0.0;
   out_1639299711796095424[9] = 0.0;
   out_1639299711796095424[10] = 0.0;
   out_1639299711796095424[11] = 0.0;
   out_1639299711796095424[12] = 0.0;
   out_1639299711796095424[13] = 0.0;
   out_1639299711796095424[14] = 0.0;
   out_1639299711796095424[15] = 0.0;
   out_1639299711796095424[16] = 0.0;
   out_1639299711796095424[17] = 0.0;
   out_1639299711796095424[18] = 0.0;
   out_1639299711796095424[19] = 1.0;
   out_1639299711796095424[20] = 0.0;
   out_1639299711796095424[21] = 0.0;
   out_1639299711796095424[22] = 0.0;
   out_1639299711796095424[23] = 0.0;
   out_1639299711796095424[24] = 0.0;
   out_1639299711796095424[25] = 0.0;
   out_1639299711796095424[26] = 0.0;
   out_1639299711796095424[27] = 0.0;
   out_1639299711796095424[28] = 0.0;
   out_1639299711796095424[29] = 0.0;
   out_1639299711796095424[30] = 0.0;
   out_1639299711796095424[31] = 0.0;
   out_1639299711796095424[32] = 0.0;
   out_1639299711796095424[33] = 0.0;
   out_1639299711796095424[34] = 0.0;
   out_1639299711796095424[35] = 0.0;
   out_1639299711796095424[36] = 0.0;
   out_1639299711796095424[37] = 0.0;
   out_1639299711796095424[38] = 1.0;
   out_1639299711796095424[39] = 0.0;
   out_1639299711796095424[40] = 0.0;
   out_1639299711796095424[41] = 0.0;
   out_1639299711796095424[42] = 0.0;
   out_1639299711796095424[43] = 0.0;
   out_1639299711796095424[44] = 0.0;
   out_1639299711796095424[45] = 0.0;
   out_1639299711796095424[46] = 0.0;
   out_1639299711796095424[47] = 0.0;
   out_1639299711796095424[48] = 0.0;
   out_1639299711796095424[49] = 0.0;
   out_1639299711796095424[50] = 0.0;
   out_1639299711796095424[51] = 0.0;
   out_1639299711796095424[52] = 0.0;
   out_1639299711796095424[53] = 0.0;
   out_1639299711796095424[54] = 0.0;
   out_1639299711796095424[55] = 0.0;
   out_1639299711796095424[56] = 0.0;
   out_1639299711796095424[57] = 1.0;
   out_1639299711796095424[58] = 0.0;
   out_1639299711796095424[59] = 0.0;
   out_1639299711796095424[60] = 0.0;
   out_1639299711796095424[61] = 0.0;
   out_1639299711796095424[62] = 0.0;
   out_1639299711796095424[63] = 0.0;
   out_1639299711796095424[64] = 0.0;
   out_1639299711796095424[65] = 0.0;
   out_1639299711796095424[66] = 0.0;
   out_1639299711796095424[67] = 0.0;
   out_1639299711796095424[68] = 0.0;
   out_1639299711796095424[69] = 0.0;
   out_1639299711796095424[70] = 0.0;
   out_1639299711796095424[71] = 0.0;
   out_1639299711796095424[72] = 0.0;
   out_1639299711796095424[73] = 0.0;
   out_1639299711796095424[74] = 0.0;
   out_1639299711796095424[75] = 0.0;
   out_1639299711796095424[76] = 1.0;
   out_1639299711796095424[77] = 0.0;
   out_1639299711796095424[78] = 0.0;
   out_1639299711796095424[79] = 0.0;
   out_1639299711796095424[80] = 0.0;
   out_1639299711796095424[81] = 0.0;
   out_1639299711796095424[82] = 0.0;
   out_1639299711796095424[83] = 0.0;
   out_1639299711796095424[84] = 0.0;
   out_1639299711796095424[85] = 0.0;
   out_1639299711796095424[86] = 0.0;
   out_1639299711796095424[87] = 0.0;
   out_1639299711796095424[88] = 0.0;
   out_1639299711796095424[89] = 0.0;
   out_1639299711796095424[90] = 0.0;
   out_1639299711796095424[91] = 0.0;
   out_1639299711796095424[92] = 0.0;
   out_1639299711796095424[93] = 0.0;
   out_1639299711796095424[94] = 0.0;
   out_1639299711796095424[95] = 1.0;
   out_1639299711796095424[96] = 0.0;
   out_1639299711796095424[97] = 0.0;
   out_1639299711796095424[98] = 0.0;
   out_1639299711796095424[99] = 0.0;
   out_1639299711796095424[100] = 0.0;
   out_1639299711796095424[101] = 0.0;
   out_1639299711796095424[102] = 0.0;
   out_1639299711796095424[103] = 0.0;
   out_1639299711796095424[104] = 0.0;
   out_1639299711796095424[105] = 0.0;
   out_1639299711796095424[106] = 0.0;
   out_1639299711796095424[107] = 0.0;
   out_1639299711796095424[108] = 0.0;
   out_1639299711796095424[109] = 0.0;
   out_1639299711796095424[110] = 0.0;
   out_1639299711796095424[111] = 0.0;
   out_1639299711796095424[112] = 0.0;
   out_1639299711796095424[113] = 0.0;
   out_1639299711796095424[114] = 1.0;
   out_1639299711796095424[115] = 0.0;
   out_1639299711796095424[116] = 0.0;
   out_1639299711796095424[117] = 0.0;
   out_1639299711796095424[118] = 0.0;
   out_1639299711796095424[119] = 0.0;
   out_1639299711796095424[120] = 0.0;
   out_1639299711796095424[121] = 0.0;
   out_1639299711796095424[122] = 0.0;
   out_1639299711796095424[123] = 0.0;
   out_1639299711796095424[124] = 0.0;
   out_1639299711796095424[125] = 0.0;
   out_1639299711796095424[126] = 0.0;
   out_1639299711796095424[127] = 0.0;
   out_1639299711796095424[128] = 0.0;
   out_1639299711796095424[129] = 0.0;
   out_1639299711796095424[130] = 0.0;
   out_1639299711796095424[131] = 0.0;
   out_1639299711796095424[132] = 0.0;
   out_1639299711796095424[133] = 1.0;
   out_1639299711796095424[134] = 0.0;
   out_1639299711796095424[135] = 0.0;
   out_1639299711796095424[136] = 0.0;
   out_1639299711796095424[137] = 0.0;
   out_1639299711796095424[138] = 0.0;
   out_1639299711796095424[139] = 0.0;
   out_1639299711796095424[140] = 0.0;
   out_1639299711796095424[141] = 0.0;
   out_1639299711796095424[142] = 0.0;
   out_1639299711796095424[143] = 0.0;
   out_1639299711796095424[144] = 0.0;
   out_1639299711796095424[145] = 0.0;
   out_1639299711796095424[146] = 0.0;
   out_1639299711796095424[147] = 0.0;
   out_1639299711796095424[148] = 0.0;
   out_1639299711796095424[149] = 0.0;
   out_1639299711796095424[150] = 0.0;
   out_1639299711796095424[151] = 0.0;
   out_1639299711796095424[152] = 1.0;
   out_1639299711796095424[153] = 0.0;
   out_1639299711796095424[154] = 0.0;
   out_1639299711796095424[155] = 0.0;
   out_1639299711796095424[156] = 0.0;
   out_1639299711796095424[157] = 0.0;
   out_1639299711796095424[158] = 0.0;
   out_1639299711796095424[159] = 0.0;
   out_1639299711796095424[160] = 0.0;
   out_1639299711796095424[161] = 0.0;
   out_1639299711796095424[162] = 0.0;
   out_1639299711796095424[163] = 0.0;
   out_1639299711796095424[164] = 0.0;
   out_1639299711796095424[165] = 0.0;
   out_1639299711796095424[166] = 0.0;
   out_1639299711796095424[167] = 0.0;
   out_1639299711796095424[168] = 0.0;
   out_1639299711796095424[169] = 0.0;
   out_1639299711796095424[170] = 0.0;
   out_1639299711796095424[171] = 1.0;
   out_1639299711796095424[172] = 0.0;
   out_1639299711796095424[173] = 0.0;
   out_1639299711796095424[174] = 0.0;
   out_1639299711796095424[175] = 0.0;
   out_1639299711796095424[176] = 0.0;
   out_1639299711796095424[177] = 0.0;
   out_1639299711796095424[178] = 0.0;
   out_1639299711796095424[179] = 0.0;
   out_1639299711796095424[180] = 0.0;
   out_1639299711796095424[181] = 0.0;
   out_1639299711796095424[182] = 0.0;
   out_1639299711796095424[183] = 0.0;
   out_1639299711796095424[184] = 0.0;
   out_1639299711796095424[185] = 0.0;
   out_1639299711796095424[186] = 0.0;
   out_1639299711796095424[187] = 0.0;
   out_1639299711796095424[188] = 0.0;
   out_1639299711796095424[189] = 0.0;
   out_1639299711796095424[190] = 1.0;
   out_1639299711796095424[191] = 0.0;
   out_1639299711796095424[192] = 0.0;
   out_1639299711796095424[193] = 0.0;
   out_1639299711796095424[194] = 0.0;
   out_1639299711796095424[195] = 0.0;
   out_1639299711796095424[196] = 0.0;
   out_1639299711796095424[197] = 0.0;
   out_1639299711796095424[198] = 0.0;
   out_1639299711796095424[199] = 0.0;
   out_1639299711796095424[200] = 0.0;
   out_1639299711796095424[201] = 0.0;
   out_1639299711796095424[202] = 0.0;
   out_1639299711796095424[203] = 0.0;
   out_1639299711796095424[204] = 0.0;
   out_1639299711796095424[205] = 0.0;
   out_1639299711796095424[206] = 0.0;
   out_1639299711796095424[207] = 0.0;
   out_1639299711796095424[208] = 0.0;
   out_1639299711796095424[209] = 1.0;
   out_1639299711796095424[210] = 0.0;
   out_1639299711796095424[211] = 0.0;
   out_1639299711796095424[212] = 0.0;
   out_1639299711796095424[213] = 0.0;
   out_1639299711796095424[214] = 0.0;
   out_1639299711796095424[215] = 0.0;
   out_1639299711796095424[216] = 0.0;
   out_1639299711796095424[217] = 0.0;
   out_1639299711796095424[218] = 0.0;
   out_1639299711796095424[219] = 0.0;
   out_1639299711796095424[220] = 0.0;
   out_1639299711796095424[221] = 0.0;
   out_1639299711796095424[222] = 0.0;
   out_1639299711796095424[223] = 0.0;
   out_1639299711796095424[224] = 0.0;
   out_1639299711796095424[225] = 0.0;
   out_1639299711796095424[226] = 0.0;
   out_1639299711796095424[227] = 0.0;
   out_1639299711796095424[228] = 1.0;
   out_1639299711796095424[229] = 0.0;
   out_1639299711796095424[230] = 0.0;
   out_1639299711796095424[231] = 0.0;
   out_1639299711796095424[232] = 0.0;
   out_1639299711796095424[233] = 0.0;
   out_1639299711796095424[234] = 0.0;
   out_1639299711796095424[235] = 0.0;
   out_1639299711796095424[236] = 0.0;
   out_1639299711796095424[237] = 0.0;
   out_1639299711796095424[238] = 0.0;
   out_1639299711796095424[239] = 0.0;
   out_1639299711796095424[240] = 0.0;
   out_1639299711796095424[241] = 0.0;
   out_1639299711796095424[242] = 0.0;
   out_1639299711796095424[243] = 0.0;
   out_1639299711796095424[244] = 0.0;
   out_1639299711796095424[245] = 0.0;
   out_1639299711796095424[246] = 0.0;
   out_1639299711796095424[247] = 1.0;
   out_1639299711796095424[248] = 0.0;
   out_1639299711796095424[249] = 0.0;
   out_1639299711796095424[250] = 0.0;
   out_1639299711796095424[251] = 0.0;
   out_1639299711796095424[252] = 0.0;
   out_1639299711796095424[253] = 0.0;
   out_1639299711796095424[254] = 0.0;
   out_1639299711796095424[255] = 0.0;
   out_1639299711796095424[256] = 0.0;
   out_1639299711796095424[257] = 0.0;
   out_1639299711796095424[258] = 0.0;
   out_1639299711796095424[259] = 0.0;
   out_1639299711796095424[260] = 0.0;
   out_1639299711796095424[261] = 0.0;
   out_1639299711796095424[262] = 0.0;
   out_1639299711796095424[263] = 0.0;
   out_1639299711796095424[264] = 0.0;
   out_1639299711796095424[265] = 0.0;
   out_1639299711796095424[266] = 1.0;
   out_1639299711796095424[267] = 0.0;
   out_1639299711796095424[268] = 0.0;
   out_1639299711796095424[269] = 0.0;
   out_1639299711796095424[270] = 0.0;
   out_1639299711796095424[271] = 0.0;
   out_1639299711796095424[272] = 0.0;
   out_1639299711796095424[273] = 0.0;
   out_1639299711796095424[274] = 0.0;
   out_1639299711796095424[275] = 0.0;
   out_1639299711796095424[276] = 0.0;
   out_1639299711796095424[277] = 0.0;
   out_1639299711796095424[278] = 0.0;
   out_1639299711796095424[279] = 0.0;
   out_1639299711796095424[280] = 0.0;
   out_1639299711796095424[281] = 0.0;
   out_1639299711796095424[282] = 0.0;
   out_1639299711796095424[283] = 0.0;
   out_1639299711796095424[284] = 0.0;
   out_1639299711796095424[285] = 1.0;
   out_1639299711796095424[286] = 0.0;
   out_1639299711796095424[287] = 0.0;
   out_1639299711796095424[288] = 0.0;
   out_1639299711796095424[289] = 0.0;
   out_1639299711796095424[290] = 0.0;
   out_1639299711796095424[291] = 0.0;
   out_1639299711796095424[292] = 0.0;
   out_1639299711796095424[293] = 0.0;
   out_1639299711796095424[294] = 0.0;
   out_1639299711796095424[295] = 0.0;
   out_1639299711796095424[296] = 0.0;
   out_1639299711796095424[297] = 0.0;
   out_1639299711796095424[298] = 0.0;
   out_1639299711796095424[299] = 0.0;
   out_1639299711796095424[300] = 0.0;
   out_1639299711796095424[301] = 0.0;
   out_1639299711796095424[302] = 0.0;
   out_1639299711796095424[303] = 0.0;
   out_1639299711796095424[304] = 1.0;
   out_1639299711796095424[305] = 0.0;
   out_1639299711796095424[306] = 0.0;
   out_1639299711796095424[307] = 0.0;
   out_1639299711796095424[308] = 0.0;
   out_1639299711796095424[309] = 0.0;
   out_1639299711796095424[310] = 0.0;
   out_1639299711796095424[311] = 0.0;
   out_1639299711796095424[312] = 0.0;
   out_1639299711796095424[313] = 0.0;
   out_1639299711796095424[314] = 0.0;
   out_1639299711796095424[315] = 0.0;
   out_1639299711796095424[316] = 0.0;
   out_1639299711796095424[317] = 0.0;
   out_1639299711796095424[318] = 0.0;
   out_1639299711796095424[319] = 0.0;
   out_1639299711796095424[320] = 0.0;
   out_1639299711796095424[321] = 0.0;
   out_1639299711796095424[322] = 0.0;
   out_1639299711796095424[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_1392497273260296337) {
   out_1392497273260296337[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_1392497273260296337[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_1392497273260296337[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_1392497273260296337[3] = dt*state[12] + state[3];
   out_1392497273260296337[4] = dt*state[13] + state[4];
   out_1392497273260296337[5] = dt*state[14] + state[5];
   out_1392497273260296337[6] = state[6];
   out_1392497273260296337[7] = state[7];
   out_1392497273260296337[8] = state[8];
   out_1392497273260296337[9] = state[9];
   out_1392497273260296337[10] = state[10];
   out_1392497273260296337[11] = state[11];
   out_1392497273260296337[12] = state[12];
   out_1392497273260296337[13] = state[13];
   out_1392497273260296337[14] = state[14];
   out_1392497273260296337[15] = state[15];
   out_1392497273260296337[16] = state[16];
   out_1392497273260296337[17] = state[17];
}
void F_fun(double *state, double dt, double *out_2156255028652572290) {
   out_2156255028652572290[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_2156255028652572290[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_2156255028652572290[2] = 0;
   out_2156255028652572290[3] = 0;
   out_2156255028652572290[4] = 0;
   out_2156255028652572290[5] = 0;
   out_2156255028652572290[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_2156255028652572290[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_2156255028652572290[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_2156255028652572290[9] = 0;
   out_2156255028652572290[10] = 0;
   out_2156255028652572290[11] = 0;
   out_2156255028652572290[12] = 0;
   out_2156255028652572290[13] = 0;
   out_2156255028652572290[14] = 0;
   out_2156255028652572290[15] = 0;
   out_2156255028652572290[16] = 0;
   out_2156255028652572290[17] = 0;
   out_2156255028652572290[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_2156255028652572290[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_2156255028652572290[20] = 0;
   out_2156255028652572290[21] = 0;
   out_2156255028652572290[22] = 0;
   out_2156255028652572290[23] = 0;
   out_2156255028652572290[24] = 0;
   out_2156255028652572290[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_2156255028652572290[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_2156255028652572290[27] = 0;
   out_2156255028652572290[28] = 0;
   out_2156255028652572290[29] = 0;
   out_2156255028652572290[30] = 0;
   out_2156255028652572290[31] = 0;
   out_2156255028652572290[32] = 0;
   out_2156255028652572290[33] = 0;
   out_2156255028652572290[34] = 0;
   out_2156255028652572290[35] = 0;
   out_2156255028652572290[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_2156255028652572290[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_2156255028652572290[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_2156255028652572290[39] = 0;
   out_2156255028652572290[40] = 0;
   out_2156255028652572290[41] = 0;
   out_2156255028652572290[42] = 0;
   out_2156255028652572290[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_2156255028652572290[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_2156255028652572290[45] = 0;
   out_2156255028652572290[46] = 0;
   out_2156255028652572290[47] = 0;
   out_2156255028652572290[48] = 0;
   out_2156255028652572290[49] = 0;
   out_2156255028652572290[50] = 0;
   out_2156255028652572290[51] = 0;
   out_2156255028652572290[52] = 0;
   out_2156255028652572290[53] = 0;
   out_2156255028652572290[54] = 0;
   out_2156255028652572290[55] = 0;
   out_2156255028652572290[56] = 0;
   out_2156255028652572290[57] = 1;
   out_2156255028652572290[58] = 0;
   out_2156255028652572290[59] = 0;
   out_2156255028652572290[60] = 0;
   out_2156255028652572290[61] = 0;
   out_2156255028652572290[62] = 0;
   out_2156255028652572290[63] = 0;
   out_2156255028652572290[64] = 0;
   out_2156255028652572290[65] = 0;
   out_2156255028652572290[66] = dt;
   out_2156255028652572290[67] = 0;
   out_2156255028652572290[68] = 0;
   out_2156255028652572290[69] = 0;
   out_2156255028652572290[70] = 0;
   out_2156255028652572290[71] = 0;
   out_2156255028652572290[72] = 0;
   out_2156255028652572290[73] = 0;
   out_2156255028652572290[74] = 0;
   out_2156255028652572290[75] = 0;
   out_2156255028652572290[76] = 1;
   out_2156255028652572290[77] = 0;
   out_2156255028652572290[78] = 0;
   out_2156255028652572290[79] = 0;
   out_2156255028652572290[80] = 0;
   out_2156255028652572290[81] = 0;
   out_2156255028652572290[82] = 0;
   out_2156255028652572290[83] = 0;
   out_2156255028652572290[84] = 0;
   out_2156255028652572290[85] = dt;
   out_2156255028652572290[86] = 0;
   out_2156255028652572290[87] = 0;
   out_2156255028652572290[88] = 0;
   out_2156255028652572290[89] = 0;
   out_2156255028652572290[90] = 0;
   out_2156255028652572290[91] = 0;
   out_2156255028652572290[92] = 0;
   out_2156255028652572290[93] = 0;
   out_2156255028652572290[94] = 0;
   out_2156255028652572290[95] = 1;
   out_2156255028652572290[96] = 0;
   out_2156255028652572290[97] = 0;
   out_2156255028652572290[98] = 0;
   out_2156255028652572290[99] = 0;
   out_2156255028652572290[100] = 0;
   out_2156255028652572290[101] = 0;
   out_2156255028652572290[102] = 0;
   out_2156255028652572290[103] = 0;
   out_2156255028652572290[104] = dt;
   out_2156255028652572290[105] = 0;
   out_2156255028652572290[106] = 0;
   out_2156255028652572290[107] = 0;
   out_2156255028652572290[108] = 0;
   out_2156255028652572290[109] = 0;
   out_2156255028652572290[110] = 0;
   out_2156255028652572290[111] = 0;
   out_2156255028652572290[112] = 0;
   out_2156255028652572290[113] = 0;
   out_2156255028652572290[114] = 1;
   out_2156255028652572290[115] = 0;
   out_2156255028652572290[116] = 0;
   out_2156255028652572290[117] = 0;
   out_2156255028652572290[118] = 0;
   out_2156255028652572290[119] = 0;
   out_2156255028652572290[120] = 0;
   out_2156255028652572290[121] = 0;
   out_2156255028652572290[122] = 0;
   out_2156255028652572290[123] = 0;
   out_2156255028652572290[124] = 0;
   out_2156255028652572290[125] = 0;
   out_2156255028652572290[126] = 0;
   out_2156255028652572290[127] = 0;
   out_2156255028652572290[128] = 0;
   out_2156255028652572290[129] = 0;
   out_2156255028652572290[130] = 0;
   out_2156255028652572290[131] = 0;
   out_2156255028652572290[132] = 0;
   out_2156255028652572290[133] = 1;
   out_2156255028652572290[134] = 0;
   out_2156255028652572290[135] = 0;
   out_2156255028652572290[136] = 0;
   out_2156255028652572290[137] = 0;
   out_2156255028652572290[138] = 0;
   out_2156255028652572290[139] = 0;
   out_2156255028652572290[140] = 0;
   out_2156255028652572290[141] = 0;
   out_2156255028652572290[142] = 0;
   out_2156255028652572290[143] = 0;
   out_2156255028652572290[144] = 0;
   out_2156255028652572290[145] = 0;
   out_2156255028652572290[146] = 0;
   out_2156255028652572290[147] = 0;
   out_2156255028652572290[148] = 0;
   out_2156255028652572290[149] = 0;
   out_2156255028652572290[150] = 0;
   out_2156255028652572290[151] = 0;
   out_2156255028652572290[152] = 1;
   out_2156255028652572290[153] = 0;
   out_2156255028652572290[154] = 0;
   out_2156255028652572290[155] = 0;
   out_2156255028652572290[156] = 0;
   out_2156255028652572290[157] = 0;
   out_2156255028652572290[158] = 0;
   out_2156255028652572290[159] = 0;
   out_2156255028652572290[160] = 0;
   out_2156255028652572290[161] = 0;
   out_2156255028652572290[162] = 0;
   out_2156255028652572290[163] = 0;
   out_2156255028652572290[164] = 0;
   out_2156255028652572290[165] = 0;
   out_2156255028652572290[166] = 0;
   out_2156255028652572290[167] = 0;
   out_2156255028652572290[168] = 0;
   out_2156255028652572290[169] = 0;
   out_2156255028652572290[170] = 0;
   out_2156255028652572290[171] = 1;
   out_2156255028652572290[172] = 0;
   out_2156255028652572290[173] = 0;
   out_2156255028652572290[174] = 0;
   out_2156255028652572290[175] = 0;
   out_2156255028652572290[176] = 0;
   out_2156255028652572290[177] = 0;
   out_2156255028652572290[178] = 0;
   out_2156255028652572290[179] = 0;
   out_2156255028652572290[180] = 0;
   out_2156255028652572290[181] = 0;
   out_2156255028652572290[182] = 0;
   out_2156255028652572290[183] = 0;
   out_2156255028652572290[184] = 0;
   out_2156255028652572290[185] = 0;
   out_2156255028652572290[186] = 0;
   out_2156255028652572290[187] = 0;
   out_2156255028652572290[188] = 0;
   out_2156255028652572290[189] = 0;
   out_2156255028652572290[190] = 1;
   out_2156255028652572290[191] = 0;
   out_2156255028652572290[192] = 0;
   out_2156255028652572290[193] = 0;
   out_2156255028652572290[194] = 0;
   out_2156255028652572290[195] = 0;
   out_2156255028652572290[196] = 0;
   out_2156255028652572290[197] = 0;
   out_2156255028652572290[198] = 0;
   out_2156255028652572290[199] = 0;
   out_2156255028652572290[200] = 0;
   out_2156255028652572290[201] = 0;
   out_2156255028652572290[202] = 0;
   out_2156255028652572290[203] = 0;
   out_2156255028652572290[204] = 0;
   out_2156255028652572290[205] = 0;
   out_2156255028652572290[206] = 0;
   out_2156255028652572290[207] = 0;
   out_2156255028652572290[208] = 0;
   out_2156255028652572290[209] = 1;
   out_2156255028652572290[210] = 0;
   out_2156255028652572290[211] = 0;
   out_2156255028652572290[212] = 0;
   out_2156255028652572290[213] = 0;
   out_2156255028652572290[214] = 0;
   out_2156255028652572290[215] = 0;
   out_2156255028652572290[216] = 0;
   out_2156255028652572290[217] = 0;
   out_2156255028652572290[218] = 0;
   out_2156255028652572290[219] = 0;
   out_2156255028652572290[220] = 0;
   out_2156255028652572290[221] = 0;
   out_2156255028652572290[222] = 0;
   out_2156255028652572290[223] = 0;
   out_2156255028652572290[224] = 0;
   out_2156255028652572290[225] = 0;
   out_2156255028652572290[226] = 0;
   out_2156255028652572290[227] = 0;
   out_2156255028652572290[228] = 1;
   out_2156255028652572290[229] = 0;
   out_2156255028652572290[230] = 0;
   out_2156255028652572290[231] = 0;
   out_2156255028652572290[232] = 0;
   out_2156255028652572290[233] = 0;
   out_2156255028652572290[234] = 0;
   out_2156255028652572290[235] = 0;
   out_2156255028652572290[236] = 0;
   out_2156255028652572290[237] = 0;
   out_2156255028652572290[238] = 0;
   out_2156255028652572290[239] = 0;
   out_2156255028652572290[240] = 0;
   out_2156255028652572290[241] = 0;
   out_2156255028652572290[242] = 0;
   out_2156255028652572290[243] = 0;
   out_2156255028652572290[244] = 0;
   out_2156255028652572290[245] = 0;
   out_2156255028652572290[246] = 0;
   out_2156255028652572290[247] = 1;
   out_2156255028652572290[248] = 0;
   out_2156255028652572290[249] = 0;
   out_2156255028652572290[250] = 0;
   out_2156255028652572290[251] = 0;
   out_2156255028652572290[252] = 0;
   out_2156255028652572290[253] = 0;
   out_2156255028652572290[254] = 0;
   out_2156255028652572290[255] = 0;
   out_2156255028652572290[256] = 0;
   out_2156255028652572290[257] = 0;
   out_2156255028652572290[258] = 0;
   out_2156255028652572290[259] = 0;
   out_2156255028652572290[260] = 0;
   out_2156255028652572290[261] = 0;
   out_2156255028652572290[262] = 0;
   out_2156255028652572290[263] = 0;
   out_2156255028652572290[264] = 0;
   out_2156255028652572290[265] = 0;
   out_2156255028652572290[266] = 1;
   out_2156255028652572290[267] = 0;
   out_2156255028652572290[268] = 0;
   out_2156255028652572290[269] = 0;
   out_2156255028652572290[270] = 0;
   out_2156255028652572290[271] = 0;
   out_2156255028652572290[272] = 0;
   out_2156255028652572290[273] = 0;
   out_2156255028652572290[274] = 0;
   out_2156255028652572290[275] = 0;
   out_2156255028652572290[276] = 0;
   out_2156255028652572290[277] = 0;
   out_2156255028652572290[278] = 0;
   out_2156255028652572290[279] = 0;
   out_2156255028652572290[280] = 0;
   out_2156255028652572290[281] = 0;
   out_2156255028652572290[282] = 0;
   out_2156255028652572290[283] = 0;
   out_2156255028652572290[284] = 0;
   out_2156255028652572290[285] = 1;
   out_2156255028652572290[286] = 0;
   out_2156255028652572290[287] = 0;
   out_2156255028652572290[288] = 0;
   out_2156255028652572290[289] = 0;
   out_2156255028652572290[290] = 0;
   out_2156255028652572290[291] = 0;
   out_2156255028652572290[292] = 0;
   out_2156255028652572290[293] = 0;
   out_2156255028652572290[294] = 0;
   out_2156255028652572290[295] = 0;
   out_2156255028652572290[296] = 0;
   out_2156255028652572290[297] = 0;
   out_2156255028652572290[298] = 0;
   out_2156255028652572290[299] = 0;
   out_2156255028652572290[300] = 0;
   out_2156255028652572290[301] = 0;
   out_2156255028652572290[302] = 0;
   out_2156255028652572290[303] = 0;
   out_2156255028652572290[304] = 1;
   out_2156255028652572290[305] = 0;
   out_2156255028652572290[306] = 0;
   out_2156255028652572290[307] = 0;
   out_2156255028652572290[308] = 0;
   out_2156255028652572290[309] = 0;
   out_2156255028652572290[310] = 0;
   out_2156255028652572290[311] = 0;
   out_2156255028652572290[312] = 0;
   out_2156255028652572290[313] = 0;
   out_2156255028652572290[314] = 0;
   out_2156255028652572290[315] = 0;
   out_2156255028652572290[316] = 0;
   out_2156255028652572290[317] = 0;
   out_2156255028652572290[318] = 0;
   out_2156255028652572290[319] = 0;
   out_2156255028652572290[320] = 0;
   out_2156255028652572290[321] = 0;
   out_2156255028652572290[322] = 0;
   out_2156255028652572290[323] = 1;
}
void h_4(double *state, double *unused, double *out_3043836967836844088) {
   out_3043836967836844088[0] = state[6] + state[9];
   out_3043836967836844088[1] = state[7] + state[10];
   out_3043836967836844088[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_7863082695855634850) {
   out_7863082695855634850[0] = 0;
   out_7863082695855634850[1] = 0;
   out_7863082695855634850[2] = 0;
   out_7863082695855634850[3] = 0;
   out_7863082695855634850[4] = 0;
   out_7863082695855634850[5] = 0;
   out_7863082695855634850[6] = 1;
   out_7863082695855634850[7] = 0;
   out_7863082695855634850[8] = 0;
   out_7863082695855634850[9] = 1;
   out_7863082695855634850[10] = 0;
   out_7863082695855634850[11] = 0;
   out_7863082695855634850[12] = 0;
   out_7863082695855634850[13] = 0;
   out_7863082695855634850[14] = 0;
   out_7863082695855634850[15] = 0;
   out_7863082695855634850[16] = 0;
   out_7863082695855634850[17] = 0;
   out_7863082695855634850[18] = 0;
   out_7863082695855634850[19] = 0;
   out_7863082695855634850[20] = 0;
   out_7863082695855634850[21] = 0;
   out_7863082695855634850[22] = 0;
   out_7863082695855634850[23] = 0;
   out_7863082695855634850[24] = 0;
   out_7863082695855634850[25] = 1;
   out_7863082695855634850[26] = 0;
   out_7863082695855634850[27] = 0;
   out_7863082695855634850[28] = 1;
   out_7863082695855634850[29] = 0;
   out_7863082695855634850[30] = 0;
   out_7863082695855634850[31] = 0;
   out_7863082695855634850[32] = 0;
   out_7863082695855634850[33] = 0;
   out_7863082695855634850[34] = 0;
   out_7863082695855634850[35] = 0;
   out_7863082695855634850[36] = 0;
   out_7863082695855634850[37] = 0;
   out_7863082695855634850[38] = 0;
   out_7863082695855634850[39] = 0;
   out_7863082695855634850[40] = 0;
   out_7863082695855634850[41] = 0;
   out_7863082695855634850[42] = 0;
   out_7863082695855634850[43] = 0;
   out_7863082695855634850[44] = 1;
   out_7863082695855634850[45] = 0;
   out_7863082695855634850[46] = 0;
   out_7863082695855634850[47] = 1;
   out_7863082695855634850[48] = 0;
   out_7863082695855634850[49] = 0;
   out_7863082695855634850[50] = 0;
   out_7863082695855634850[51] = 0;
   out_7863082695855634850[52] = 0;
   out_7863082695855634850[53] = 0;
}
void h_10(double *state, double *unused, double *out_7404958229428552171) {
   out_7404958229428552171[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_7404958229428552171[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_7404958229428552171[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_6268263964996001431) {
   out_6268263964996001431[0] = 0;
   out_6268263964996001431[1] = 9.8100000000000005*cos(state[1]);
   out_6268263964996001431[2] = 0;
   out_6268263964996001431[3] = 0;
   out_6268263964996001431[4] = -state[8];
   out_6268263964996001431[5] = state[7];
   out_6268263964996001431[6] = 0;
   out_6268263964996001431[7] = state[5];
   out_6268263964996001431[8] = -state[4];
   out_6268263964996001431[9] = 0;
   out_6268263964996001431[10] = 0;
   out_6268263964996001431[11] = 0;
   out_6268263964996001431[12] = 1;
   out_6268263964996001431[13] = 0;
   out_6268263964996001431[14] = 0;
   out_6268263964996001431[15] = 1;
   out_6268263964996001431[16] = 0;
   out_6268263964996001431[17] = 0;
   out_6268263964996001431[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_6268263964996001431[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_6268263964996001431[20] = 0;
   out_6268263964996001431[21] = state[8];
   out_6268263964996001431[22] = 0;
   out_6268263964996001431[23] = -state[6];
   out_6268263964996001431[24] = -state[5];
   out_6268263964996001431[25] = 0;
   out_6268263964996001431[26] = state[3];
   out_6268263964996001431[27] = 0;
   out_6268263964996001431[28] = 0;
   out_6268263964996001431[29] = 0;
   out_6268263964996001431[30] = 0;
   out_6268263964996001431[31] = 1;
   out_6268263964996001431[32] = 0;
   out_6268263964996001431[33] = 0;
   out_6268263964996001431[34] = 1;
   out_6268263964996001431[35] = 0;
   out_6268263964996001431[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_6268263964996001431[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_6268263964996001431[38] = 0;
   out_6268263964996001431[39] = -state[7];
   out_6268263964996001431[40] = state[6];
   out_6268263964996001431[41] = 0;
   out_6268263964996001431[42] = state[4];
   out_6268263964996001431[43] = -state[3];
   out_6268263964996001431[44] = 0;
   out_6268263964996001431[45] = 0;
   out_6268263964996001431[46] = 0;
   out_6268263964996001431[47] = 0;
   out_6268263964996001431[48] = 0;
   out_6268263964996001431[49] = 0;
   out_6268263964996001431[50] = 1;
   out_6268263964996001431[51] = 0;
   out_6268263964996001431[52] = 0;
   out_6268263964996001431[53] = 1;
}
void h_13(double *state, double *unused, double *out_5572039581656493534) {
   out_5572039581656493534[0] = state[3];
   out_5572039581656493534[1] = state[4];
   out_5572039581656493534[2] = state[5];
}
void H_13(double *state, double *unused, double *out_7371387552521583965) {
   out_7371387552521583965[0] = 0;
   out_7371387552521583965[1] = 0;
   out_7371387552521583965[2] = 0;
   out_7371387552521583965[3] = 1;
   out_7371387552521583965[4] = 0;
   out_7371387552521583965[5] = 0;
   out_7371387552521583965[6] = 0;
   out_7371387552521583965[7] = 0;
   out_7371387552521583965[8] = 0;
   out_7371387552521583965[9] = 0;
   out_7371387552521583965[10] = 0;
   out_7371387552521583965[11] = 0;
   out_7371387552521583965[12] = 0;
   out_7371387552521583965[13] = 0;
   out_7371387552521583965[14] = 0;
   out_7371387552521583965[15] = 0;
   out_7371387552521583965[16] = 0;
   out_7371387552521583965[17] = 0;
   out_7371387552521583965[18] = 0;
   out_7371387552521583965[19] = 0;
   out_7371387552521583965[20] = 0;
   out_7371387552521583965[21] = 0;
   out_7371387552521583965[22] = 1;
   out_7371387552521583965[23] = 0;
   out_7371387552521583965[24] = 0;
   out_7371387552521583965[25] = 0;
   out_7371387552521583965[26] = 0;
   out_7371387552521583965[27] = 0;
   out_7371387552521583965[28] = 0;
   out_7371387552521583965[29] = 0;
   out_7371387552521583965[30] = 0;
   out_7371387552521583965[31] = 0;
   out_7371387552521583965[32] = 0;
   out_7371387552521583965[33] = 0;
   out_7371387552521583965[34] = 0;
   out_7371387552521583965[35] = 0;
   out_7371387552521583965[36] = 0;
   out_7371387552521583965[37] = 0;
   out_7371387552521583965[38] = 0;
   out_7371387552521583965[39] = 0;
   out_7371387552521583965[40] = 0;
   out_7371387552521583965[41] = 1;
   out_7371387552521583965[42] = 0;
   out_7371387552521583965[43] = 0;
   out_7371387552521583965[44] = 0;
   out_7371387552521583965[45] = 0;
   out_7371387552521583965[46] = 0;
   out_7371387552521583965[47] = 0;
   out_7371387552521583965[48] = 0;
   out_7371387552521583965[49] = 0;
   out_7371387552521583965[50] = 0;
   out_7371387552521583965[51] = 0;
   out_7371387552521583965[52] = 0;
   out_7371387552521583965[53] = 0;
}
void h_14(double *state, double *unused, double *out_4488120958675282001) {
   out_4488120958675282001[0] = state[6];
   out_4488120958675282001[1] = state[7];
   out_4488120958675282001[2] = state[8];
}
void H_14(double *state, double *unused, double *out_6620420521514432237) {
   out_6620420521514432237[0] = 0;
   out_6620420521514432237[1] = 0;
   out_6620420521514432237[2] = 0;
   out_6620420521514432237[3] = 0;
   out_6620420521514432237[4] = 0;
   out_6620420521514432237[5] = 0;
   out_6620420521514432237[6] = 1;
   out_6620420521514432237[7] = 0;
   out_6620420521514432237[8] = 0;
   out_6620420521514432237[9] = 0;
   out_6620420521514432237[10] = 0;
   out_6620420521514432237[11] = 0;
   out_6620420521514432237[12] = 0;
   out_6620420521514432237[13] = 0;
   out_6620420521514432237[14] = 0;
   out_6620420521514432237[15] = 0;
   out_6620420521514432237[16] = 0;
   out_6620420521514432237[17] = 0;
   out_6620420521514432237[18] = 0;
   out_6620420521514432237[19] = 0;
   out_6620420521514432237[20] = 0;
   out_6620420521514432237[21] = 0;
   out_6620420521514432237[22] = 0;
   out_6620420521514432237[23] = 0;
   out_6620420521514432237[24] = 0;
   out_6620420521514432237[25] = 1;
   out_6620420521514432237[26] = 0;
   out_6620420521514432237[27] = 0;
   out_6620420521514432237[28] = 0;
   out_6620420521514432237[29] = 0;
   out_6620420521514432237[30] = 0;
   out_6620420521514432237[31] = 0;
   out_6620420521514432237[32] = 0;
   out_6620420521514432237[33] = 0;
   out_6620420521514432237[34] = 0;
   out_6620420521514432237[35] = 0;
   out_6620420521514432237[36] = 0;
   out_6620420521514432237[37] = 0;
   out_6620420521514432237[38] = 0;
   out_6620420521514432237[39] = 0;
   out_6620420521514432237[40] = 0;
   out_6620420521514432237[41] = 0;
   out_6620420521514432237[42] = 0;
   out_6620420521514432237[43] = 0;
   out_6620420521514432237[44] = 1;
   out_6620420521514432237[45] = 0;
   out_6620420521514432237[46] = 0;
   out_6620420521514432237[47] = 0;
   out_6620420521514432237[48] = 0;
   out_6620420521514432237[49] = 0;
   out_6620420521514432237[50] = 0;
   out_6620420521514432237[51] = 0;
   out_6620420521514432237[52] = 0;
   out_6620420521514432237[53] = 0;
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
void pose_err_fun(double *nom_x, double *delta_x, double *out_920130119510719117) {
  err_fun(nom_x, delta_x, out_920130119510719117);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_4602168207176775062) {
  inv_err_fun(nom_x, true_x, out_4602168207176775062);
}
void pose_H_mod_fun(double *state, double *out_1639299711796095424) {
  H_mod_fun(state, out_1639299711796095424);
}
void pose_f_fun(double *state, double dt, double *out_1392497273260296337) {
  f_fun(state,  dt, out_1392497273260296337);
}
void pose_F_fun(double *state, double dt, double *out_2156255028652572290) {
  F_fun(state,  dt, out_2156255028652572290);
}
void pose_h_4(double *state, double *unused, double *out_3043836967836844088) {
  h_4(state, unused, out_3043836967836844088);
}
void pose_H_4(double *state, double *unused, double *out_7863082695855634850) {
  H_4(state, unused, out_7863082695855634850);
}
void pose_h_10(double *state, double *unused, double *out_7404958229428552171) {
  h_10(state, unused, out_7404958229428552171);
}
void pose_H_10(double *state, double *unused, double *out_6268263964996001431) {
  H_10(state, unused, out_6268263964996001431);
}
void pose_h_13(double *state, double *unused, double *out_5572039581656493534) {
  h_13(state, unused, out_5572039581656493534);
}
void pose_H_13(double *state, double *unused, double *out_7371387552521583965) {
  H_13(state, unused, out_7371387552521583965);
}
void pose_h_14(double *state, double *unused, double *out_4488120958675282001) {
  h_14(state, unused, out_4488120958675282001);
}
void pose_H_14(double *state, double *unused, double *out_6620420521514432237) {
  H_14(state, unused, out_6620420521514432237);
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
