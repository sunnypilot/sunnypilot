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
void err_fun(double *nom_x, double *delta_x, double *out_2314661006140587753) {
   out_2314661006140587753[0] = delta_x[0] + nom_x[0];
   out_2314661006140587753[1] = delta_x[1] + nom_x[1];
   out_2314661006140587753[2] = delta_x[2] + nom_x[2];
   out_2314661006140587753[3] = delta_x[3] + nom_x[3];
   out_2314661006140587753[4] = delta_x[4] + nom_x[4];
   out_2314661006140587753[5] = delta_x[5] + nom_x[5];
   out_2314661006140587753[6] = delta_x[6] + nom_x[6];
   out_2314661006140587753[7] = delta_x[7] + nom_x[7];
   out_2314661006140587753[8] = delta_x[8] + nom_x[8];
   out_2314661006140587753[9] = delta_x[9] + nom_x[9];
   out_2314661006140587753[10] = delta_x[10] + nom_x[10];
   out_2314661006140587753[11] = delta_x[11] + nom_x[11];
   out_2314661006140587753[12] = delta_x[12] + nom_x[12];
   out_2314661006140587753[13] = delta_x[13] + nom_x[13];
   out_2314661006140587753[14] = delta_x[14] + nom_x[14];
   out_2314661006140587753[15] = delta_x[15] + nom_x[15];
   out_2314661006140587753[16] = delta_x[16] + nom_x[16];
   out_2314661006140587753[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_6192097384047082973) {
   out_6192097384047082973[0] = -nom_x[0] + true_x[0];
   out_6192097384047082973[1] = -nom_x[1] + true_x[1];
   out_6192097384047082973[2] = -nom_x[2] + true_x[2];
   out_6192097384047082973[3] = -nom_x[3] + true_x[3];
   out_6192097384047082973[4] = -nom_x[4] + true_x[4];
   out_6192097384047082973[5] = -nom_x[5] + true_x[5];
   out_6192097384047082973[6] = -nom_x[6] + true_x[6];
   out_6192097384047082973[7] = -nom_x[7] + true_x[7];
   out_6192097384047082973[8] = -nom_x[8] + true_x[8];
   out_6192097384047082973[9] = -nom_x[9] + true_x[9];
   out_6192097384047082973[10] = -nom_x[10] + true_x[10];
   out_6192097384047082973[11] = -nom_x[11] + true_x[11];
   out_6192097384047082973[12] = -nom_x[12] + true_x[12];
   out_6192097384047082973[13] = -nom_x[13] + true_x[13];
   out_6192097384047082973[14] = -nom_x[14] + true_x[14];
   out_6192097384047082973[15] = -nom_x[15] + true_x[15];
   out_6192097384047082973[16] = -nom_x[16] + true_x[16];
   out_6192097384047082973[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_1438273545813297818) {
   out_1438273545813297818[0] = 1.0;
   out_1438273545813297818[1] = 0.0;
   out_1438273545813297818[2] = 0.0;
   out_1438273545813297818[3] = 0.0;
   out_1438273545813297818[4] = 0.0;
   out_1438273545813297818[5] = 0.0;
   out_1438273545813297818[6] = 0.0;
   out_1438273545813297818[7] = 0.0;
   out_1438273545813297818[8] = 0.0;
   out_1438273545813297818[9] = 0.0;
   out_1438273545813297818[10] = 0.0;
   out_1438273545813297818[11] = 0.0;
   out_1438273545813297818[12] = 0.0;
   out_1438273545813297818[13] = 0.0;
   out_1438273545813297818[14] = 0.0;
   out_1438273545813297818[15] = 0.0;
   out_1438273545813297818[16] = 0.0;
   out_1438273545813297818[17] = 0.0;
   out_1438273545813297818[18] = 0.0;
   out_1438273545813297818[19] = 1.0;
   out_1438273545813297818[20] = 0.0;
   out_1438273545813297818[21] = 0.0;
   out_1438273545813297818[22] = 0.0;
   out_1438273545813297818[23] = 0.0;
   out_1438273545813297818[24] = 0.0;
   out_1438273545813297818[25] = 0.0;
   out_1438273545813297818[26] = 0.0;
   out_1438273545813297818[27] = 0.0;
   out_1438273545813297818[28] = 0.0;
   out_1438273545813297818[29] = 0.0;
   out_1438273545813297818[30] = 0.0;
   out_1438273545813297818[31] = 0.0;
   out_1438273545813297818[32] = 0.0;
   out_1438273545813297818[33] = 0.0;
   out_1438273545813297818[34] = 0.0;
   out_1438273545813297818[35] = 0.0;
   out_1438273545813297818[36] = 0.0;
   out_1438273545813297818[37] = 0.0;
   out_1438273545813297818[38] = 1.0;
   out_1438273545813297818[39] = 0.0;
   out_1438273545813297818[40] = 0.0;
   out_1438273545813297818[41] = 0.0;
   out_1438273545813297818[42] = 0.0;
   out_1438273545813297818[43] = 0.0;
   out_1438273545813297818[44] = 0.0;
   out_1438273545813297818[45] = 0.0;
   out_1438273545813297818[46] = 0.0;
   out_1438273545813297818[47] = 0.0;
   out_1438273545813297818[48] = 0.0;
   out_1438273545813297818[49] = 0.0;
   out_1438273545813297818[50] = 0.0;
   out_1438273545813297818[51] = 0.0;
   out_1438273545813297818[52] = 0.0;
   out_1438273545813297818[53] = 0.0;
   out_1438273545813297818[54] = 0.0;
   out_1438273545813297818[55] = 0.0;
   out_1438273545813297818[56] = 0.0;
   out_1438273545813297818[57] = 1.0;
   out_1438273545813297818[58] = 0.0;
   out_1438273545813297818[59] = 0.0;
   out_1438273545813297818[60] = 0.0;
   out_1438273545813297818[61] = 0.0;
   out_1438273545813297818[62] = 0.0;
   out_1438273545813297818[63] = 0.0;
   out_1438273545813297818[64] = 0.0;
   out_1438273545813297818[65] = 0.0;
   out_1438273545813297818[66] = 0.0;
   out_1438273545813297818[67] = 0.0;
   out_1438273545813297818[68] = 0.0;
   out_1438273545813297818[69] = 0.0;
   out_1438273545813297818[70] = 0.0;
   out_1438273545813297818[71] = 0.0;
   out_1438273545813297818[72] = 0.0;
   out_1438273545813297818[73] = 0.0;
   out_1438273545813297818[74] = 0.0;
   out_1438273545813297818[75] = 0.0;
   out_1438273545813297818[76] = 1.0;
   out_1438273545813297818[77] = 0.0;
   out_1438273545813297818[78] = 0.0;
   out_1438273545813297818[79] = 0.0;
   out_1438273545813297818[80] = 0.0;
   out_1438273545813297818[81] = 0.0;
   out_1438273545813297818[82] = 0.0;
   out_1438273545813297818[83] = 0.0;
   out_1438273545813297818[84] = 0.0;
   out_1438273545813297818[85] = 0.0;
   out_1438273545813297818[86] = 0.0;
   out_1438273545813297818[87] = 0.0;
   out_1438273545813297818[88] = 0.0;
   out_1438273545813297818[89] = 0.0;
   out_1438273545813297818[90] = 0.0;
   out_1438273545813297818[91] = 0.0;
   out_1438273545813297818[92] = 0.0;
   out_1438273545813297818[93] = 0.0;
   out_1438273545813297818[94] = 0.0;
   out_1438273545813297818[95] = 1.0;
   out_1438273545813297818[96] = 0.0;
   out_1438273545813297818[97] = 0.0;
   out_1438273545813297818[98] = 0.0;
   out_1438273545813297818[99] = 0.0;
   out_1438273545813297818[100] = 0.0;
   out_1438273545813297818[101] = 0.0;
   out_1438273545813297818[102] = 0.0;
   out_1438273545813297818[103] = 0.0;
   out_1438273545813297818[104] = 0.0;
   out_1438273545813297818[105] = 0.0;
   out_1438273545813297818[106] = 0.0;
   out_1438273545813297818[107] = 0.0;
   out_1438273545813297818[108] = 0.0;
   out_1438273545813297818[109] = 0.0;
   out_1438273545813297818[110] = 0.0;
   out_1438273545813297818[111] = 0.0;
   out_1438273545813297818[112] = 0.0;
   out_1438273545813297818[113] = 0.0;
   out_1438273545813297818[114] = 1.0;
   out_1438273545813297818[115] = 0.0;
   out_1438273545813297818[116] = 0.0;
   out_1438273545813297818[117] = 0.0;
   out_1438273545813297818[118] = 0.0;
   out_1438273545813297818[119] = 0.0;
   out_1438273545813297818[120] = 0.0;
   out_1438273545813297818[121] = 0.0;
   out_1438273545813297818[122] = 0.0;
   out_1438273545813297818[123] = 0.0;
   out_1438273545813297818[124] = 0.0;
   out_1438273545813297818[125] = 0.0;
   out_1438273545813297818[126] = 0.0;
   out_1438273545813297818[127] = 0.0;
   out_1438273545813297818[128] = 0.0;
   out_1438273545813297818[129] = 0.0;
   out_1438273545813297818[130] = 0.0;
   out_1438273545813297818[131] = 0.0;
   out_1438273545813297818[132] = 0.0;
   out_1438273545813297818[133] = 1.0;
   out_1438273545813297818[134] = 0.0;
   out_1438273545813297818[135] = 0.0;
   out_1438273545813297818[136] = 0.0;
   out_1438273545813297818[137] = 0.0;
   out_1438273545813297818[138] = 0.0;
   out_1438273545813297818[139] = 0.0;
   out_1438273545813297818[140] = 0.0;
   out_1438273545813297818[141] = 0.0;
   out_1438273545813297818[142] = 0.0;
   out_1438273545813297818[143] = 0.0;
   out_1438273545813297818[144] = 0.0;
   out_1438273545813297818[145] = 0.0;
   out_1438273545813297818[146] = 0.0;
   out_1438273545813297818[147] = 0.0;
   out_1438273545813297818[148] = 0.0;
   out_1438273545813297818[149] = 0.0;
   out_1438273545813297818[150] = 0.0;
   out_1438273545813297818[151] = 0.0;
   out_1438273545813297818[152] = 1.0;
   out_1438273545813297818[153] = 0.0;
   out_1438273545813297818[154] = 0.0;
   out_1438273545813297818[155] = 0.0;
   out_1438273545813297818[156] = 0.0;
   out_1438273545813297818[157] = 0.0;
   out_1438273545813297818[158] = 0.0;
   out_1438273545813297818[159] = 0.0;
   out_1438273545813297818[160] = 0.0;
   out_1438273545813297818[161] = 0.0;
   out_1438273545813297818[162] = 0.0;
   out_1438273545813297818[163] = 0.0;
   out_1438273545813297818[164] = 0.0;
   out_1438273545813297818[165] = 0.0;
   out_1438273545813297818[166] = 0.0;
   out_1438273545813297818[167] = 0.0;
   out_1438273545813297818[168] = 0.0;
   out_1438273545813297818[169] = 0.0;
   out_1438273545813297818[170] = 0.0;
   out_1438273545813297818[171] = 1.0;
   out_1438273545813297818[172] = 0.0;
   out_1438273545813297818[173] = 0.0;
   out_1438273545813297818[174] = 0.0;
   out_1438273545813297818[175] = 0.0;
   out_1438273545813297818[176] = 0.0;
   out_1438273545813297818[177] = 0.0;
   out_1438273545813297818[178] = 0.0;
   out_1438273545813297818[179] = 0.0;
   out_1438273545813297818[180] = 0.0;
   out_1438273545813297818[181] = 0.0;
   out_1438273545813297818[182] = 0.0;
   out_1438273545813297818[183] = 0.0;
   out_1438273545813297818[184] = 0.0;
   out_1438273545813297818[185] = 0.0;
   out_1438273545813297818[186] = 0.0;
   out_1438273545813297818[187] = 0.0;
   out_1438273545813297818[188] = 0.0;
   out_1438273545813297818[189] = 0.0;
   out_1438273545813297818[190] = 1.0;
   out_1438273545813297818[191] = 0.0;
   out_1438273545813297818[192] = 0.0;
   out_1438273545813297818[193] = 0.0;
   out_1438273545813297818[194] = 0.0;
   out_1438273545813297818[195] = 0.0;
   out_1438273545813297818[196] = 0.0;
   out_1438273545813297818[197] = 0.0;
   out_1438273545813297818[198] = 0.0;
   out_1438273545813297818[199] = 0.0;
   out_1438273545813297818[200] = 0.0;
   out_1438273545813297818[201] = 0.0;
   out_1438273545813297818[202] = 0.0;
   out_1438273545813297818[203] = 0.0;
   out_1438273545813297818[204] = 0.0;
   out_1438273545813297818[205] = 0.0;
   out_1438273545813297818[206] = 0.0;
   out_1438273545813297818[207] = 0.0;
   out_1438273545813297818[208] = 0.0;
   out_1438273545813297818[209] = 1.0;
   out_1438273545813297818[210] = 0.0;
   out_1438273545813297818[211] = 0.0;
   out_1438273545813297818[212] = 0.0;
   out_1438273545813297818[213] = 0.0;
   out_1438273545813297818[214] = 0.0;
   out_1438273545813297818[215] = 0.0;
   out_1438273545813297818[216] = 0.0;
   out_1438273545813297818[217] = 0.0;
   out_1438273545813297818[218] = 0.0;
   out_1438273545813297818[219] = 0.0;
   out_1438273545813297818[220] = 0.0;
   out_1438273545813297818[221] = 0.0;
   out_1438273545813297818[222] = 0.0;
   out_1438273545813297818[223] = 0.0;
   out_1438273545813297818[224] = 0.0;
   out_1438273545813297818[225] = 0.0;
   out_1438273545813297818[226] = 0.0;
   out_1438273545813297818[227] = 0.0;
   out_1438273545813297818[228] = 1.0;
   out_1438273545813297818[229] = 0.0;
   out_1438273545813297818[230] = 0.0;
   out_1438273545813297818[231] = 0.0;
   out_1438273545813297818[232] = 0.0;
   out_1438273545813297818[233] = 0.0;
   out_1438273545813297818[234] = 0.0;
   out_1438273545813297818[235] = 0.0;
   out_1438273545813297818[236] = 0.0;
   out_1438273545813297818[237] = 0.0;
   out_1438273545813297818[238] = 0.0;
   out_1438273545813297818[239] = 0.0;
   out_1438273545813297818[240] = 0.0;
   out_1438273545813297818[241] = 0.0;
   out_1438273545813297818[242] = 0.0;
   out_1438273545813297818[243] = 0.0;
   out_1438273545813297818[244] = 0.0;
   out_1438273545813297818[245] = 0.0;
   out_1438273545813297818[246] = 0.0;
   out_1438273545813297818[247] = 1.0;
   out_1438273545813297818[248] = 0.0;
   out_1438273545813297818[249] = 0.0;
   out_1438273545813297818[250] = 0.0;
   out_1438273545813297818[251] = 0.0;
   out_1438273545813297818[252] = 0.0;
   out_1438273545813297818[253] = 0.0;
   out_1438273545813297818[254] = 0.0;
   out_1438273545813297818[255] = 0.0;
   out_1438273545813297818[256] = 0.0;
   out_1438273545813297818[257] = 0.0;
   out_1438273545813297818[258] = 0.0;
   out_1438273545813297818[259] = 0.0;
   out_1438273545813297818[260] = 0.0;
   out_1438273545813297818[261] = 0.0;
   out_1438273545813297818[262] = 0.0;
   out_1438273545813297818[263] = 0.0;
   out_1438273545813297818[264] = 0.0;
   out_1438273545813297818[265] = 0.0;
   out_1438273545813297818[266] = 1.0;
   out_1438273545813297818[267] = 0.0;
   out_1438273545813297818[268] = 0.0;
   out_1438273545813297818[269] = 0.0;
   out_1438273545813297818[270] = 0.0;
   out_1438273545813297818[271] = 0.0;
   out_1438273545813297818[272] = 0.0;
   out_1438273545813297818[273] = 0.0;
   out_1438273545813297818[274] = 0.0;
   out_1438273545813297818[275] = 0.0;
   out_1438273545813297818[276] = 0.0;
   out_1438273545813297818[277] = 0.0;
   out_1438273545813297818[278] = 0.0;
   out_1438273545813297818[279] = 0.0;
   out_1438273545813297818[280] = 0.0;
   out_1438273545813297818[281] = 0.0;
   out_1438273545813297818[282] = 0.0;
   out_1438273545813297818[283] = 0.0;
   out_1438273545813297818[284] = 0.0;
   out_1438273545813297818[285] = 1.0;
   out_1438273545813297818[286] = 0.0;
   out_1438273545813297818[287] = 0.0;
   out_1438273545813297818[288] = 0.0;
   out_1438273545813297818[289] = 0.0;
   out_1438273545813297818[290] = 0.0;
   out_1438273545813297818[291] = 0.0;
   out_1438273545813297818[292] = 0.0;
   out_1438273545813297818[293] = 0.0;
   out_1438273545813297818[294] = 0.0;
   out_1438273545813297818[295] = 0.0;
   out_1438273545813297818[296] = 0.0;
   out_1438273545813297818[297] = 0.0;
   out_1438273545813297818[298] = 0.0;
   out_1438273545813297818[299] = 0.0;
   out_1438273545813297818[300] = 0.0;
   out_1438273545813297818[301] = 0.0;
   out_1438273545813297818[302] = 0.0;
   out_1438273545813297818[303] = 0.0;
   out_1438273545813297818[304] = 1.0;
   out_1438273545813297818[305] = 0.0;
   out_1438273545813297818[306] = 0.0;
   out_1438273545813297818[307] = 0.0;
   out_1438273545813297818[308] = 0.0;
   out_1438273545813297818[309] = 0.0;
   out_1438273545813297818[310] = 0.0;
   out_1438273545813297818[311] = 0.0;
   out_1438273545813297818[312] = 0.0;
   out_1438273545813297818[313] = 0.0;
   out_1438273545813297818[314] = 0.0;
   out_1438273545813297818[315] = 0.0;
   out_1438273545813297818[316] = 0.0;
   out_1438273545813297818[317] = 0.0;
   out_1438273545813297818[318] = 0.0;
   out_1438273545813297818[319] = 0.0;
   out_1438273545813297818[320] = 0.0;
   out_1438273545813297818[321] = 0.0;
   out_1438273545813297818[322] = 0.0;
   out_1438273545813297818[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_5533301484302365435) {
   out_5533301484302365435[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_5533301484302365435[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_5533301484302365435[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_5533301484302365435[3] = dt*state[12] + state[3];
   out_5533301484302365435[4] = dt*state[13] + state[4];
   out_5533301484302365435[5] = dt*state[14] + state[5];
   out_5533301484302365435[6] = state[6];
   out_5533301484302365435[7] = state[7];
   out_5533301484302365435[8] = state[8];
   out_5533301484302365435[9] = state[9];
   out_5533301484302365435[10] = state[10];
   out_5533301484302365435[11] = state[11];
   out_5533301484302365435[12] = state[12];
   out_5533301484302365435[13] = state[13];
   out_5533301484302365435[14] = state[14];
   out_5533301484302365435[15] = state[15];
   out_5533301484302365435[16] = state[16];
   out_5533301484302365435[17] = state[17];
}
void F_fun(double *state, double dt, double *out_8970483331473945713) {
   out_8970483331473945713[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_8970483331473945713[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_8970483331473945713[2] = 0;
   out_8970483331473945713[3] = 0;
   out_8970483331473945713[4] = 0;
   out_8970483331473945713[5] = 0;
   out_8970483331473945713[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_8970483331473945713[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_8970483331473945713[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_8970483331473945713[9] = 0;
   out_8970483331473945713[10] = 0;
   out_8970483331473945713[11] = 0;
   out_8970483331473945713[12] = 0;
   out_8970483331473945713[13] = 0;
   out_8970483331473945713[14] = 0;
   out_8970483331473945713[15] = 0;
   out_8970483331473945713[16] = 0;
   out_8970483331473945713[17] = 0;
   out_8970483331473945713[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_8970483331473945713[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_8970483331473945713[20] = 0;
   out_8970483331473945713[21] = 0;
   out_8970483331473945713[22] = 0;
   out_8970483331473945713[23] = 0;
   out_8970483331473945713[24] = 0;
   out_8970483331473945713[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_8970483331473945713[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_8970483331473945713[27] = 0;
   out_8970483331473945713[28] = 0;
   out_8970483331473945713[29] = 0;
   out_8970483331473945713[30] = 0;
   out_8970483331473945713[31] = 0;
   out_8970483331473945713[32] = 0;
   out_8970483331473945713[33] = 0;
   out_8970483331473945713[34] = 0;
   out_8970483331473945713[35] = 0;
   out_8970483331473945713[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_8970483331473945713[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_8970483331473945713[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_8970483331473945713[39] = 0;
   out_8970483331473945713[40] = 0;
   out_8970483331473945713[41] = 0;
   out_8970483331473945713[42] = 0;
   out_8970483331473945713[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_8970483331473945713[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_8970483331473945713[45] = 0;
   out_8970483331473945713[46] = 0;
   out_8970483331473945713[47] = 0;
   out_8970483331473945713[48] = 0;
   out_8970483331473945713[49] = 0;
   out_8970483331473945713[50] = 0;
   out_8970483331473945713[51] = 0;
   out_8970483331473945713[52] = 0;
   out_8970483331473945713[53] = 0;
   out_8970483331473945713[54] = 0;
   out_8970483331473945713[55] = 0;
   out_8970483331473945713[56] = 0;
   out_8970483331473945713[57] = 1;
   out_8970483331473945713[58] = 0;
   out_8970483331473945713[59] = 0;
   out_8970483331473945713[60] = 0;
   out_8970483331473945713[61] = 0;
   out_8970483331473945713[62] = 0;
   out_8970483331473945713[63] = 0;
   out_8970483331473945713[64] = 0;
   out_8970483331473945713[65] = 0;
   out_8970483331473945713[66] = dt;
   out_8970483331473945713[67] = 0;
   out_8970483331473945713[68] = 0;
   out_8970483331473945713[69] = 0;
   out_8970483331473945713[70] = 0;
   out_8970483331473945713[71] = 0;
   out_8970483331473945713[72] = 0;
   out_8970483331473945713[73] = 0;
   out_8970483331473945713[74] = 0;
   out_8970483331473945713[75] = 0;
   out_8970483331473945713[76] = 1;
   out_8970483331473945713[77] = 0;
   out_8970483331473945713[78] = 0;
   out_8970483331473945713[79] = 0;
   out_8970483331473945713[80] = 0;
   out_8970483331473945713[81] = 0;
   out_8970483331473945713[82] = 0;
   out_8970483331473945713[83] = 0;
   out_8970483331473945713[84] = 0;
   out_8970483331473945713[85] = dt;
   out_8970483331473945713[86] = 0;
   out_8970483331473945713[87] = 0;
   out_8970483331473945713[88] = 0;
   out_8970483331473945713[89] = 0;
   out_8970483331473945713[90] = 0;
   out_8970483331473945713[91] = 0;
   out_8970483331473945713[92] = 0;
   out_8970483331473945713[93] = 0;
   out_8970483331473945713[94] = 0;
   out_8970483331473945713[95] = 1;
   out_8970483331473945713[96] = 0;
   out_8970483331473945713[97] = 0;
   out_8970483331473945713[98] = 0;
   out_8970483331473945713[99] = 0;
   out_8970483331473945713[100] = 0;
   out_8970483331473945713[101] = 0;
   out_8970483331473945713[102] = 0;
   out_8970483331473945713[103] = 0;
   out_8970483331473945713[104] = dt;
   out_8970483331473945713[105] = 0;
   out_8970483331473945713[106] = 0;
   out_8970483331473945713[107] = 0;
   out_8970483331473945713[108] = 0;
   out_8970483331473945713[109] = 0;
   out_8970483331473945713[110] = 0;
   out_8970483331473945713[111] = 0;
   out_8970483331473945713[112] = 0;
   out_8970483331473945713[113] = 0;
   out_8970483331473945713[114] = 1;
   out_8970483331473945713[115] = 0;
   out_8970483331473945713[116] = 0;
   out_8970483331473945713[117] = 0;
   out_8970483331473945713[118] = 0;
   out_8970483331473945713[119] = 0;
   out_8970483331473945713[120] = 0;
   out_8970483331473945713[121] = 0;
   out_8970483331473945713[122] = 0;
   out_8970483331473945713[123] = 0;
   out_8970483331473945713[124] = 0;
   out_8970483331473945713[125] = 0;
   out_8970483331473945713[126] = 0;
   out_8970483331473945713[127] = 0;
   out_8970483331473945713[128] = 0;
   out_8970483331473945713[129] = 0;
   out_8970483331473945713[130] = 0;
   out_8970483331473945713[131] = 0;
   out_8970483331473945713[132] = 0;
   out_8970483331473945713[133] = 1;
   out_8970483331473945713[134] = 0;
   out_8970483331473945713[135] = 0;
   out_8970483331473945713[136] = 0;
   out_8970483331473945713[137] = 0;
   out_8970483331473945713[138] = 0;
   out_8970483331473945713[139] = 0;
   out_8970483331473945713[140] = 0;
   out_8970483331473945713[141] = 0;
   out_8970483331473945713[142] = 0;
   out_8970483331473945713[143] = 0;
   out_8970483331473945713[144] = 0;
   out_8970483331473945713[145] = 0;
   out_8970483331473945713[146] = 0;
   out_8970483331473945713[147] = 0;
   out_8970483331473945713[148] = 0;
   out_8970483331473945713[149] = 0;
   out_8970483331473945713[150] = 0;
   out_8970483331473945713[151] = 0;
   out_8970483331473945713[152] = 1;
   out_8970483331473945713[153] = 0;
   out_8970483331473945713[154] = 0;
   out_8970483331473945713[155] = 0;
   out_8970483331473945713[156] = 0;
   out_8970483331473945713[157] = 0;
   out_8970483331473945713[158] = 0;
   out_8970483331473945713[159] = 0;
   out_8970483331473945713[160] = 0;
   out_8970483331473945713[161] = 0;
   out_8970483331473945713[162] = 0;
   out_8970483331473945713[163] = 0;
   out_8970483331473945713[164] = 0;
   out_8970483331473945713[165] = 0;
   out_8970483331473945713[166] = 0;
   out_8970483331473945713[167] = 0;
   out_8970483331473945713[168] = 0;
   out_8970483331473945713[169] = 0;
   out_8970483331473945713[170] = 0;
   out_8970483331473945713[171] = 1;
   out_8970483331473945713[172] = 0;
   out_8970483331473945713[173] = 0;
   out_8970483331473945713[174] = 0;
   out_8970483331473945713[175] = 0;
   out_8970483331473945713[176] = 0;
   out_8970483331473945713[177] = 0;
   out_8970483331473945713[178] = 0;
   out_8970483331473945713[179] = 0;
   out_8970483331473945713[180] = 0;
   out_8970483331473945713[181] = 0;
   out_8970483331473945713[182] = 0;
   out_8970483331473945713[183] = 0;
   out_8970483331473945713[184] = 0;
   out_8970483331473945713[185] = 0;
   out_8970483331473945713[186] = 0;
   out_8970483331473945713[187] = 0;
   out_8970483331473945713[188] = 0;
   out_8970483331473945713[189] = 0;
   out_8970483331473945713[190] = 1;
   out_8970483331473945713[191] = 0;
   out_8970483331473945713[192] = 0;
   out_8970483331473945713[193] = 0;
   out_8970483331473945713[194] = 0;
   out_8970483331473945713[195] = 0;
   out_8970483331473945713[196] = 0;
   out_8970483331473945713[197] = 0;
   out_8970483331473945713[198] = 0;
   out_8970483331473945713[199] = 0;
   out_8970483331473945713[200] = 0;
   out_8970483331473945713[201] = 0;
   out_8970483331473945713[202] = 0;
   out_8970483331473945713[203] = 0;
   out_8970483331473945713[204] = 0;
   out_8970483331473945713[205] = 0;
   out_8970483331473945713[206] = 0;
   out_8970483331473945713[207] = 0;
   out_8970483331473945713[208] = 0;
   out_8970483331473945713[209] = 1;
   out_8970483331473945713[210] = 0;
   out_8970483331473945713[211] = 0;
   out_8970483331473945713[212] = 0;
   out_8970483331473945713[213] = 0;
   out_8970483331473945713[214] = 0;
   out_8970483331473945713[215] = 0;
   out_8970483331473945713[216] = 0;
   out_8970483331473945713[217] = 0;
   out_8970483331473945713[218] = 0;
   out_8970483331473945713[219] = 0;
   out_8970483331473945713[220] = 0;
   out_8970483331473945713[221] = 0;
   out_8970483331473945713[222] = 0;
   out_8970483331473945713[223] = 0;
   out_8970483331473945713[224] = 0;
   out_8970483331473945713[225] = 0;
   out_8970483331473945713[226] = 0;
   out_8970483331473945713[227] = 0;
   out_8970483331473945713[228] = 1;
   out_8970483331473945713[229] = 0;
   out_8970483331473945713[230] = 0;
   out_8970483331473945713[231] = 0;
   out_8970483331473945713[232] = 0;
   out_8970483331473945713[233] = 0;
   out_8970483331473945713[234] = 0;
   out_8970483331473945713[235] = 0;
   out_8970483331473945713[236] = 0;
   out_8970483331473945713[237] = 0;
   out_8970483331473945713[238] = 0;
   out_8970483331473945713[239] = 0;
   out_8970483331473945713[240] = 0;
   out_8970483331473945713[241] = 0;
   out_8970483331473945713[242] = 0;
   out_8970483331473945713[243] = 0;
   out_8970483331473945713[244] = 0;
   out_8970483331473945713[245] = 0;
   out_8970483331473945713[246] = 0;
   out_8970483331473945713[247] = 1;
   out_8970483331473945713[248] = 0;
   out_8970483331473945713[249] = 0;
   out_8970483331473945713[250] = 0;
   out_8970483331473945713[251] = 0;
   out_8970483331473945713[252] = 0;
   out_8970483331473945713[253] = 0;
   out_8970483331473945713[254] = 0;
   out_8970483331473945713[255] = 0;
   out_8970483331473945713[256] = 0;
   out_8970483331473945713[257] = 0;
   out_8970483331473945713[258] = 0;
   out_8970483331473945713[259] = 0;
   out_8970483331473945713[260] = 0;
   out_8970483331473945713[261] = 0;
   out_8970483331473945713[262] = 0;
   out_8970483331473945713[263] = 0;
   out_8970483331473945713[264] = 0;
   out_8970483331473945713[265] = 0;
   out_8970483331473945713[266] = 1;
   out_8970483331473945713[267] = 0;
   out_8970483331473945713[268] = 0;
   out_8970483331473945713[269] = 0;
   out_8970483331473945713[270] = 0;
   out_8970483331473945713[271] = 0;
   out_8970483331473945713[272] = 0;
   out_8970483331473945713[273] = 0;
   out_8970483331473945713[274] = 0;
   out_8970483331473945713[275] = 0;
   out_8970483331473945713[276] = 0;
   out_8970483331473945713[277] = 0;
   out_8970483331473945713[278] = 0;
   out_8970483331473945713[279] = 0;
   out_8970483331473945713[280] = 0;
   out_8970483331473945713[281] = 0;
   out_8970483331473945713[282] = 0;
   out_8970483331473945713[283] = 0;
   out_8970483331473945713[284] = 0;
   out_8970483331473945713[285] = 1;
   out_8970483331473945713[286] = 0;
   out_8970483331473945713[287] = 0;
   out_8970483331473945713[288] = 0;
   out_8970483331473945713[289] = 0;
   out_8970483331473945713[290] = 0;
   out_8970483331473945713[291] = 0;
   out_8970483331473945713[292] = 0;
   out_8970483331473945713[293] = 0;
   out_8970483331473945713[294] = 0;
   out_8970483331473945713[295] = 0;
   out_8970483331473945713[296] = 0;
   out_8970483331473945713[297] = 0;
   out_8970483331473945713[298] = 0;
   out_8970483331473945713[299] = 0;
   out_8970483331473945713[300] = 0;
   out_8970483331473945713[301] = 0;
   out_8970483331473945713[302] = 0;
   out_8970483331473945713[303] = 0;
   out_8970483331473945713[304] = 1;
   out_8970483331473945713[305] = 0;
   out_8970483331473945713[306] = 0;
   out_8970483331473945713[307] = 0;
   out_8970483331473945713[308] = 0;
   out_8970483331473945713[309] = 0;
   out_8970483331473945713[310] = 0;
   out_8970483331473945713[311] = 0;
   out_8970483331473945713[312] = 0;
   out_8970483331473945713[313] = 0;
   out_8970483331473945713[314] = 0;
   out_8970483331473945713[315] = 0;
   out_8970483331473945713[316] = 0;
   out_8970483331473945713[317] = 0;
   out_8970483331473945713[318] = 0;
   out_8970483331473945713[319] = 0;
   out_8970483331473945713[320] = 0;
   out_8970483331473945713[321] = 0;
   out_8970483331473945713[322] = 0;
   out_8970483331473945713[323] = 1;
}
void h_4(double *state, double *unused, double *out_667285240629023896) {
   out_667285240629023896[0] = state[6] + state[9];
   out_667285240629023896[1] = state[7] + state[10];
   out_667285240629023896[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_684112543758585211) {
   out_684112543758585211[0] = 0;
   out_684112543758585211[1] = 0;
   out_684112543758585211[2] = 0;
   out_684112543758585211[3] = 0;
   out_684112543758585211[4] = 0;
   out_684112543758585211[5] = 0;
   out_684112543758585211[6] = 1;
   out_684112543758585211[7] = 0;
   out_684112543758585211[8] = 0;
   out_684112543758585211[9] = 1;
   out_684112543758585211[10] = 0;
   out_684112543758585211[11] = 0;
   out_684112543758585211[12] = 0;
   out_684112543758585211[13] = 0;
   out_684112543758585211[14] = 0;
   out_684112543758585211[15] = 0;
   out_684112543758585211[16] = 0;
   out_684112543758585211[17] = 0;
   out_684112543758585211[18] = 0;
   out_684112543758585211[19] = 0;
   out_684112543758585211[20] = 0;
   out_684112543758585211[21] = 0;
   out_684112543758585211[22] = 0;
   out_684112543758585211[23] = 0;
   out_684112543758585211[24] = 0;
   out_684112543758585211[25] = 1;
   out_684112543758585211[26] = 0;
   out_684112543758585211[27] = 0;
   out_684112543758585211[28] = 1;
   out_684112543758585211[29] = 0;
   out_684112543758585211[30] = 0;
   out_684112543758585211[31] = 0;
   out_684112543758585211[32] = 0;
   out_684112543758585211[33] = 0;
   out_684112543758585211[34] = 0;
   out_684112543758585211[35] = 0;
   out_684112543758585211[36] = 0;
   out_684112543758585211[37] = 0;
   out_684112543758585211[38] = 0;
   out_684112543758585211[39] = 0;
   out_684112543758585211[40] = 0;
   out_684112543758585211[41] = 0;
   out_684112543758585211[42] = 0;
   out_684112543758585211[43] = 0;
   out_684112543758585211[44] = 1;
   out_684112543758585211[45] = 0;
   out_684112543758585211[46] = 0;
   out_684112543758585211[47] = 1;
   out_684112543758585211[48] = 0;
   out_684112543758585211[49] = 0;
   out_684112543758585211[50] = 0;
   out_684112543758585211[51] = 0;
   out_684112543758585211[52] = 0;
   out_684112543758585211[53] = 0;
}
void h_10(double *state, double *unused, double *out_6645666359799058327) {
   out_6645666359799058327[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_6645666359799058327[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_6645666359799058327[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_2536663734245119922) {
   out_2536663734245119922[0] = 0;
   out_2536663734245119922[1] = 9.8100000000000005*cos(state[1]);
   out_2536663734245119922[2] = 0;
   out_2536663734245119922[3] = 0;
   out_2536663734245119922[4] = -state[8];
   out_2536663734245119922[5] = state[7];
   out_2536663734245119922[6] = 0;
   out_2536663734245119922[7] = state[5];
   out_2536663734245119922[8] = -state[4];
   out_2536663734245119922[9] = 0;
   out_2536663734245119922[10] = 0;
   out_2536663734245119922[11] = 0;
   out_2536663734245119922[12] = 1;
   out_2536663734245119922[13] = 0;
   out_2536663734245119922[14] = 0;
   out_2536663734245119922[15] = 1;
   out_2536663734245119922[16] = 0;
   out_2536663734245119922[17] = 0;
   out_2536663734245119922[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_2536663734245119922[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_2536663734245119922[20] = 0;
   out_2536663734245119922[21] = state[8];
   out_2536663734245119922[22] = 0;
   out_2536663734245119922[23] = -state[6];
   out_2536663734245119922[24] = -state[5];
   out_2536663734245119922[25] = 0;
   out_2536663734245119922[26] = state[3];
   out_2536663734245119922[27] = 0;
   out_2536663734245119922[28] = 0;
   out_2536663734245119922[29] = 0;
   out_2536663734245119922[30] = 0;
   out_2536663734245119922[31] = 1;
   out_2536663734245119922[32] = 0;
   out_2536663734245119922[33] = 0;
   out_2536663734245119922[34] = 1;
   out_2536663734245119922[35] = 0;
   out_2536663734245119922[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_2536663734245119922[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_2536663734245119922[38] = 0;
   out_2536663734245119922[39] = -state[7];
   out_2536663734245119922[40] = state[6];
   out_2536663734245119922[41] = 0;
   out_2536663734245119922[42] = state[4];
   out_2536663734245119922[43] = -state[3];
   out_2536663734245119922[44] = 0;
   out_2536663734245119922[45] = 0;
   out_2536663734245119922[46] = 0;
   out_2536663734245119922[47] = 0;
   out_2536663734245119922[48] = 0;
   out_2536663734245119922[49] = 0;
   out_2536663734245119922[50] = 1;
   out_2536663734245119922[51] = 0;
   out_2536663734245119922[52] = 0;
   out_2536663734245119922[53] = 1;
}
void h_13(double *state, double *unused, double *out_2409725172809164603) {
   out_2409725172809164603[0] = state[3];
   out_2409725172809164603[1] = state[4];
   out_2409725172809164603[2] = state[5];
}
void H_13(double *state, double *unused, double *out_6926518664558115718) {
   out_6926518664558115718[0] = 0;
   out_6926518664558115718[1] = 0;
   out_6926518664558115718[2] = 0;
   out_6926518664558115718[3] = 1;
   out_6926518664558115718[4] = 0;
   out_6926518664558115718[5] = 0;
   out_6926518664558115718[6] = 0;
   out_6926518664558115718[7] = 0;
   out_6926518664558115718[8] = 0;
   out_6926518664558115718[9] = 0;
   out_6926518664558115718[10] = 0;
   out_6926518664558115718[11] = 0;
   out_6926518664558115718[12] = 0;
   out_6926518664558115718[13] = 0;
   out_6926518664558115718[14] = 0;
   out_6926518664558115718[15] = 0;
   out_6926518664558115718[16] = 0;
   out_6926518664558115718[17] = 0;
   out_6926518664558115718[18] = 0;
   out_6926518664558115718[19] = 0;
   out_6926518664558115718[20] = 0;
   out_6926518664558115718[21] = 0;
   out_6926518664558115718[22] = 1;
   out_6926518664558115718[23] = 0;
   out_6926518664558115718[24] = 0;
   out_6926518664558115718[25] = 0;
   out_6926518664558115718[26] = 0;
   out_6926518664558115718[27] = 0;
   out_6926518664558115718[28] = 0;
   out_6926518664558115718[29] = 0;
   out_6926518664558115718[30] = 0;
   out_6926518664558115718[31] = 0;
   out_6926518664558115718[32] = 0;
   out_6926518664558115718[33] = 0;
   out_6926518664558115718[34] = 0;
   out_6926518664558115718[35] = 0;
   out_6926518664558115718[36] = 0;
   out_6926518664558115718[37] = 0;
   out_6926518664558115718[38] = 0;
   out_6926518664558115718[39] = 0;
   out_6926518664558115718[40] = 0;
   out_6926518664558115718[41] = 1;
   out_6926518664558115718[42] = 0;
   out_6926518664558115718[43] = 0;
   out_6926518664558115718[44] = 0;
   out_6926518664558115718[45] = 0;
   out_6926518664558115718[46] = 0;
   out_6926518664558115718[47] = 0;
   out_6926518664558115718[48] = 0;
   out_6926518664558115718[49] = 0;
   out_6926518664558115718[50] = 0;
   out_6926518664558115718[51] = 0;
   out_6926518664558115718[52] = 0;
   out_6926518664558115718[53] = 0;
}
void h_14(double *state, double *unused, double *out_8151145315765671202) {
   out_8151145315765671202[0] = state[6];
   out_8151145315765671202[1] = state[7];
   out_8151145315765671202[2] = state[8];
}
void H_14(double *state, double *unused, double *out_3279128312580899318) {
   out_3279128312580899318[0] = 0;
   out_3279128312580899318[1] = 0;
   out_3279128312580899318[2] = 0;
   out_3279128312580899318[3] = 0;
   out_3279128312580899318[4] = 0;
   out_3279128312580899318[5] = 0;
   out_3279128312580899318[6] = 1;
   out_3279128312580899318[7] = 0;
   out_3279128312580899318[8] = 0;
   out_3279128312580899318[9] = 0;
   out_3279128312580899318[10] = 0;
   out_3279128312580899318[11] = 0;
   out_3279128312580899318[12] = 0;
   out_3279128312580899318[13] = 0;
   out_3279128312580899318[14] = 0;
   out_3279128312580899318[15] = 0;
   out_3279128312580899318[16] = 0;
   out_3279128312580899318[17] = 0;
   out_3279128312580899318[18] = 0;
   out_3279128312580899318[19] = 0;
   out_3279128312580899318[20] = 0;
   out_3279128312580899318[21] = 0;
   out_3279128312580899318[22] = 0;
   out_3279128312580899318[23] = 0;
   out_3279128312580899318[24] = 0;
   out_3279128312580899318[25] = 1;
   out_3279128312580899318[26] = 0;
   out_3279128312580899318[27] = 0;
   out_3279128312580899318[28] = 0;
   out_3279128312580899318[29] = 0;
   out_3279128312580899318[30] = 0;
   out_3279128312580899318[31] = 0;
   out_3279128312580899318[32] = 0;
   out_3279128312580899318[33] = 0;
   out_3279128312580899318[34] = 0;
   out_3279128312580899318[35] = 0;
   out_3279128312580899318[36] = 0;
   out_3279128312580899318[37] = 0;
   out_3279128312580899318[38] = 0;
   out_3279128312580899318[39] = 0;
   out_3279128312580899318[40] = 0;
   out_3279128312580899318[41] = 0;
   out_3279128312580899318[42] = 0;
   out_3279128312580899318[43] = 0;
   out_3279128312580899318[44] = 1;
   out_3279128312580899318[45] = 0;
   out_3279128312580899318[46] = 0;
   out_3279128312580899318[47] = 0;
   out_3279128312580899318[48] = 0;
   out_3279128312580899318[49] = 0;
   out_3279128312580899318[50] = 0;
   out_3279128312580899318[51] = 0;
   out_3279128312580899318[52] = 0;
   out_3279128312580899318[53] = 0;
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
void pose_err_fun(double *nom_x, double *delta_x, double *out_2314661006140587753) {
  err_fun(nom_x, delta_x, out_2314661006140587753);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_6192097384047082973) {
  inv_err_fun(nom_x, true_x, out_6192097384047082973);
}
void pose_H_mod_fun(double *state, double *out_1438273545813297818) {
  H_mod_fun(state, out_1438273545813297818);
}
void pose_f_fun(double *state, double dt, double *out_5533301484302365435) {
  f_fun(state,  dt, out_5533301484302365435);
}
void pose_F_fun(double *state, double dt, double *out_8970483331473945713) {
  F_fun(state,  dt, out_8970483331473945713);
}
void pose_h_4(double *state, double *unused, double *out_667285240629023896) {
  h_4(state, unused, out_667285240629023896);
}
void pose_H_4(double *state, double *unused, double *out_684112543758585211) {
  H_4(state, unused, out_684112543758585211);
}
void pose_h_10(double *state, double *unused, double *out_6645666359799058327) {
  h_10(state, unused, out_6645666359799058327);
}
void pose_H_10(double *state, double *unused, double *out_2536663734245119922) {
  H_10(state, unused, out_2536663734245119922);
}
void pose_h_13(double *state, double *unused, double *out_2409725172809164603) {
  h_13(state, unused, out_2409725172809164603);
}
void pose_H_13(double *state, double *unused, double *out_6926518664558115718) {
  H_13(state, unused, out_6926518664558115718);
}
void pose_h_14(double *state, double *unused, double *out_8151145315765671202) {
  h_14(state, unused, out_8151145315765671202);
}
void pose_H_14(double *state, double *unused, double *out_3279128312580899318) {
  H_14(state, unused, out_3279128312580899318);
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
