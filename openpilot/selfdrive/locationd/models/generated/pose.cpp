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
void err_fun(double *nom_x, double *delta_x, double *out_7117000844039973656) {
   out_7117000844039973656[0] = delta_x[0] + nom_x[0];
   out_7117000844039973656[1] = delta_x[1] + nom_x[1];
   out_7117000844039973656[2] = delta_x[2] + nom_x[2];
   out_7117000844039973656[3] = delta_x[3] + nom_x[3];
   out_7117000844039973656[4] = delta_x[4] + nom_x[4];
   out_7117000844039973656[5] = delta_x[5] + nom_x[5];
   out_7117000844039973656[6] = delta_x[6] + nom_x[6];
   out_7117000844039973656[7] = delta_x[7] + nom_x[7];
   out_7117000844039973656[8] = delta_x[8] + nom_x[8];
   out_7117000844039973656[9] = delta_x[9] + nom_x[9];
   out_7117000844039973656[10] = delta_x[10] + nom_x[10];
   out_7117000844039973656[11] = delta_x[11] + nom_x[11];
   out_7117000844039973656[12] = delta_x[12] + nom_x[12];
   out_7117000844039973656[13] = delta_x[13] + nom_x[13];
   out_7117000844039973656[14] = delta_x[14] + nom_x[14];
   out_7117000844039973656[15] = delta_x[15] + nom_x[15];
   out_7117000844039973656[16] = delta_x[16] + nom_x[16];
   out_7117000844039973656[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_5738271447995775317) {
   out_5738271447995775317[0] = -nom_x[0] + true_x[0];
   out_5738271447995775317[1] = -nom_x[1] + true_x[1];
   out_5738271447995775317[2] = -nom_x[2] + true_x[2];
   out_5738271447995775317[3] = -nom_x[3] + true_x[3];
   out_5738271447995775317[4] = -nom_x[4] + true_x[4];
   out_5738271447995775317[5] = -nom_x[5] + true_x[5];
   out_5738271447995775317[6] = -nom_x[6] + true_x[6];
   out_5738271447995775317[7] = -nom_x[7] + true_x[7];
   out_5738271447995775317[8] = -nom_x[8] + true_x[8];
   out_5738271447995775317[9] = -nom_x[9] + true_x[9];
   out_5738271447995775317[10] = -nom_x[10] + true_x[10];
   out_5738271447995775317[11] = -nom_x[11] + true_x[11];
   out_5738271447995775317[12] = -nom_x[12] + true_x[12];
   out_5738271447995775317[13] = -nom_x[13] + true_x[13];
   out_5738271447995775317[14] = -nom_x[14] + true_x[14];
   out_5738271447995775317[15] = -nom_x[15] + true_x[15];
   out_5738271447995775317[16] = -nom_x[16] + true_x[16];
   out_5738271447995775317[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_4131332949940298666) {
   out_4131332949940298666[0] = 1.0;
   out_4131332949940298666[1] = 0.0;
   out_4131332949940298666[2] = 0.0;
   out_4131332949940298666[3] = 0.0;
   out_4131332949940298666[4] = 0.0;
   out_4131332949940298666[5] = 0.0;
   out_4131332949940298666[6] = 0.0;
   out_4131332949940298666[7] = 0.0;
   out_4131332949940298666[8] = 0.0;
   out_4131332949940298666[9] = 0.0;
   out_4131332949940298666[10] = 0.0;
   out_4131332949940298666[11] = 0.0;
   out_4131332949940298666[12] = 0.0;
   out_4131332949940298666[13] = 0.0;
   out_4131332949940298666[14] = 0.0;
   out_4131332949940298666[15] = 0.0;
   out_4131332949940298666[16] = 0.0;
   out_4131332949940298666[17] = 0.0;
   out_4131332949940298666[18] = 0.0;
   out_4131332949940298666[19] = 1.0;
   out_4131332949940298666[20] = 0.0;
   out_4131332949940298666[21] = 0.0;
   out_4131332949940298666[22] = 0.0;
   out_4131332949940298666[23] = 0.0;
   out_4131332949940298666[24] = 0.0;
   out_4131332949940298666[25] = 0.0;
   out_4131332949940298666[26] = 0.0;
   out_4131332949940298666[27] = 0.0;
   out_4131332949940298666[28] = 0.0;
   out_4131332949940298666[29] = 0.0;
   out_4131332949940298666[30] = 0.0;
   out_4131332949940298666[31] = 0.0;
   out_4131332949940298666[32] = 0.0;
   out_4131332949940298666[33] = 0.0;
   out_4131332949940298666[34] = 0.0;
   out_4131332949940298666[35] = 0.0;
   out_4131332949940298666[36] = 0.0;
   out_4131332949940298666[37] = 0.0;
   out_4131332949940298666[38] = 1.0;
   out_4131332949940298666[39] = 0.0;
   out_4131332949940298666[40] = 0.0;
   out_4131332949940298666[41] = 0.0;
   out_4131332949940298666[42] = 0.0;
   out_4131332949940298666[43] = 0.0;
   out_4131332949940298666[44] = 0.0;
   out_4131332949940298666[45] = 0.0;
   out_4131332949940298666[46] = 0.0;
   out_4131332949940298666[47] = 0.0;
   out_4131332949940298666[48] = 0.0;
   out_4131332949940298666[49] = 0.0;
   out_4131332949940298666[50] = 0.0;
   out_4131332949940298666[51] = 0.0;
   out_4131332949940298666[52] = 0.0;
   out_4131332949940298666[53] = 0.0;
   out_4131332949940298666[54] = 0.0;
   out_4131332949940298666[55] = 0.0;
   out_4131332949940298666[56] = 0.0;
   out_4131332949940298666[57] = 1.0;
   out_4131332949940298666[58] = 0.0;
   out_4131332949940298666[59] = 0.0;
   out_4131332949940298666[60] = 0.0;
   out_4131332949940298666[61] = 0.0;
   out_4131332949940298666[62] = 0.0;
   out_4131332949940298666[63] = 0.0;
   out_4131332949940298666[64] = 0.0;
   out_4131332949940298666[65] = 0.0;
   out_4131332949940298666[66] = 0.0;
   out_4131332949940298666[67] = 0.0;
   out_4131332949940298666[68] = 0.0;
   out_4131332949940298666[69] = 0.0;
   out_4131332949940298666[70] = 0.0;
   out_4131332949940298666[71] = 0.0;
   out_4131332949940298666[72] = 0.0;
   out_4131332949940298666[73] = 0.0;
   out_4131332949940298666[74] = 0.0;
   out_4131332949940298666[75] = 0.0;
   out_4131332949940298666[76] = 1.0;
   out_4131332949940298666[77] = 0.0;
   out_4131332949940298666[78] = 0.0;
   out_4131332949940298666[79] = 0.0;
   out_4131332949940298666[80] = 0.0;
   out_4131332949940298666[81] = 0.0;
   out_4131332949940298666[82] = 0.0;
   out_4131332949940298666[83] = 0.0;
   out_4131332949940298666[84] = 0.0;
   out_4131332949940298666[85] = 0.0;
   out_4131332949940298666[86] = 0.0;
   out_4131332949940298666[87] = 0.0;
   out_4131332949940298666[88] = 0.0;
   out_4131332949940298666[89] = 0.0;
   out_4131332949940298666[90] = 0.0;
   out_4131332949940298666[91] = 0.0;
   out_4131332949940298666[92] = 0.0;
   out_4131332949940298666[93] = 0.0;
   out_4131332949940298666[94] = 0.0;
   out_4131332949940298666[95] = 1.0;
   out_4131332949940298666[96] = 0.0;
   out_4131332949940298666[97] = 0.0;
   out_4131332949940298666[98] = 0.0;
   out_4131332949940298666[99] = 0.0;
   out_4131332949940298666[100] = 0.0;
   out_4131332949940298666[101] = 0.0;
   out_4131332949940298666[102] = 0.0;
   out_4131332949940298666[103] = 0.0;
   out_4131332949940298666[104] = 0.0;
   out_4131332949940298666[105] = 0.0;
   out_4131332949940298666[106] = 0.0;
   out_4131332949940298666[107] = 0.0;
   out_4131332949940298666[108] = 0.0;
   out_4131332949940298666[109] = 0.0;
   out_4131332949940298666[110] = 0.0;
   out_4131332949940298666[111] = 0.0;
   out_4131332949940298666[112] = 0.0;
   out_4131332949940298666[113] = 0.0;
   out_4131332949940298666[114] = 1.0;
   out_4131332949940298666[115] = 0.0;
   out_4131332949940298666[116] = 0.0;
   out_4131332949940298666[117] = 0.0;
   out_4131332949940298666[118] = 0.0;
   out_4131332949940298666[119] = 0.0;
   out_4131332949940298666[120] = 0.0;
   out_4131332949940298666[121] = 0.0;
   out_4131332949940298666[122] = 0.0;
   out_4131332949940298666[123] = 0.0;
   out_4131332949940298666[124] = 0.0;
   out_4131332949940298666[125] = 0.0;
   out_4131332949940298666[126] = 0.0;
   out_4131332949940298666[127] = 0.0;
   out_4131332949940298666[128] = 0.0;
   out_4131332949940298666[129] = 0.0;
   out_4131332949940298666[130] = 0.0;
   out_4131332949940298666[131] = 0.0;
   out_4131332949940298666[132] = 0.0;
   out_4131332949940298666[133] = 1.0;
   out_4131332949940298666[134] = 0.0;
   out_4131332949940298666[135] = 0.0;
   out_4131332949940298666[136] = 0.0;
   out_4131332949940298666[137] = 0.0;
   out_4131332949940298666[138] = 0.0;
   out_4131332949940298666[139] = 0.0;
   out_4131332949940298666[140] = 0.0;
   out_4131332949940298666[141] = 0.0;
   out_4131332949940298666[142] = 0.0;
   out_4131332949940298666[143] = 0.0;
   out_4131332949940298666[144] = 0.0;
   out_4131332949940298666[145] = 0.0;
   out_4131332949940298666[146] = 0.0;
   out_4131332949940298666[147] = 0.0;
   out_4131332949940298666[148] = 0.0;
   out_4131332949940298666[149] = 0.0;
   out_4131332949940298666[150] = 0.0;
   out_4131332949940298666[151] = 0.0;
   out_4131332949940298666[152] = 1.0;
   out_4131332949940298666[153] = 0.0;
   out_4131332949940298666[154] = 0.0;
   out_4131332949940298666[155] = 0.0;
   out_4131332949940298666[156] = 0.0;
   out_4131332949940298666[157] = 0.0;
   out_4131332949940298666[158] = 0.0;
   out_4131332949940298666[159] = 0.0;
   out_4131332949940298666[160] = 0.0;
   out_4131332949940298666[161] = 0.0;
   out_4131332949940298666[162] = 0.0;
   out_4131332949940298666[163] = 0.0;
   out_4131332949940298666[164] = 0.0;
   out_4131332949940298666[165] = 0.0;
   out_4131332949940298666[166] = 0.0;
   out_4131332949940298666[167] = 0.0;
   out_4131332949940298666[168] = 0.0;
   out_4131332949940298666[169] = 0.0;
   out_4131332949940298666[170] = 0.0;
   out_4131332949940298666[171] = 1.0;
   out_4131332949940298666[172] = 0.0;
   out_4131332949940298666[173] = 0.0;
   out_4131332949940298666[174] = 0.0;
   out_4131332949940298666[175] = 0.0;
   out_4131332949940298666[176] = 0.0;
   out_4131332949940298666[177] = 0.0;
   out_4131332949940298666[178] = 0.0;
   out_4131332949940298666[179] = 0.0;
   out_4131332949940298666[180] = 0.0;
   out_4131332949940298666[181] = 0.0;
   out_4131332949940298666[182] = 0.0;
   out_4131332949940298666[183] = 0.0;
   out_4131332949940298666[184] = 0.0;
   out_4131332949940298666[185] = 0.0;
   out_4131332949940298666[186] = 0.0;
   out_4131332949940298666[187] = 0.0;
   out_4131332949940298666[188] = 0.0;
   out_4131332949940298666[189] = 0.0;
   out_4131332949940298666[190] = 1.0;
   out_4131332949940298666[191] = 0.0;
   out_4131332949940298666[192] = 0.0;
   out_4131332949940298666[193] = 0.0;
   out_4131332949940298666[194] = 0.0;
   out_4131332949940298666[195] = 0.0;
   out_4131332949940298666[196] = 0.0;
   out_4131332949940298666[197] = 0.0;
   out_4131332949940298666[198] = 0.0;
   out_4131332949940298666[199] = 0.0;
   out_4131332949940298666[200] = 0.0;
   out_4131332949940298666[201] = 0.0;
   out_4131332949940298666[202] = 0.0;
   out_4131332949940298666[203] = 0.0;
   out_4131332949940298666[204] = 0.0;
   out_4131332949940298666[205] = 0.0;
   out_4131332949940298666[206] = 0.0;
   out_4131332949940298666[207] = 0.0;
   out_4131332949940298666[208] = 0.0;
   out_4131332949940298666[209] = 1.0;
   out_4131332949940298666[210] = 0.0;
   out_4131332949940298666[211] = 0.0;
   out_4131332949940298666[212] = 0.0;
   out_4131332949940298666[213] = 0.0;
   out_4131332949940298666[214] = 0.0;
   out_4131332949940298666[215] = 0.0;
   out_4131332949940298666[216] = 0.0;
   out_4131332949940298666[217] = 0.0;
   out_4131332949940298666[218] = 0.0;
   out_4131332949940298666[219] = 0.0;
   out_4131332949940298666[220] = 0.0;
   out_4131332949940298666[221] = 0.0;
   out_4131332949940298666[222] = 0.0;
   out_4131332949940298666[223] = 0.0;
   out_4131332949940298666[224] = 0.0;
   out_4131332949940298666[225] = 0.0;
   out_4131332949940298666[226] = 0.0;
   out_4131332949940298666[227] = 0.0;
   out_4131332949940298666[228] = 1.0;
   out_4131332949940298666[229] = 0.0;
   out_4131332949940298666[230] = 0.0;
   out_4131332949940298666[231] = 0.0;
   out_4131332949940298666[232] = 0.0;
   out_4131332949940298666[233] = 0.0;
   out_4131332949940298666[234] = 0.0;
   out_4131332949940298666[235] = 0.0;
   out_4131332949940298666[236] = 0.0;
   out_4131332949940298666[237] = 0.0;
   out_4131332949940298666[238] = 0.0;
   out_4131332949940298666[239] = 0.0;
   out_4131332949940298666[240] = 0.0;
   out_4131332949940298666[241] = 0.0;
   out_4131332949940298666[242] = 0.0;
   out_4131332949940298666[243] = 0.0;
   out_4131332949940298666[244] = 0.0;
   out_4131332949940298666[245] = 0.0;
   out_4131332949940298666[246] = 0.0;
   out_4131332949940298666[247] = 1.0;
   out_4131332949940298666[248] = 0.0;
   out_4131332949940298666[249] = 0.0;
   out_4131332949940298666[250] = 0.0;
   out_4131332949940298666[251] = 0.0;
   out_4131332949940298666[252] = 0.0;
   out_4131332949940298666[253] = 0.0;
   out_4131332949940298666[254] = 0.0;
   out_4131332949940298666[255] = 0.0;
   out_4131332949940298666[256] = 0.0;
   out_4131332949940298666[257] = 0.0;
   out_4131332949940298666[258] = 0.0;
   out_4131332949940298666[259] = 0.0;
   out_4131332949940298666[260] = 0.0;
   out_4131332949940298666[261] = 0.0;
   out_4131332949940298666[262] = 0.0;
   out_4131332949940298666[263] = 0.0;
   out_4131332949940298666[264] = 0.0;
   out_4131332949940298666[265] = 0.0;
   out_4131332949940298666[266] = 1.0;
   out_4131332949940298666[267] = 0.0;
   out_4131332949940298666[268] = 0.0;
   out_4131332949940298666[269] = 0.0;
   out_4131332949940298666[270] = 0.0;
   out_4131332949940298666[271] = 0.0;
   out_4131332949940298666[272] = 0.0;
   out_4131332949940298666[273] = 0.0;
   out_4131332949940298666[274] = 0.0;
   out_4131332949940298666[275] = 0.0;
   out_4131332949940298666[276] = 0.0;
   out_4131332949940298666[277] = 0.0;
   out_4131332949940298666[278] = 0.0;
   out_4131332949940298666[279] = 0.0;
   out_4131332949940298666[280] = 0.0;
   out_4131332949940298666[281] = 0.0;
   out_4131332949940298666[282] = 0.0;
   out_4131332949940298666[283] = 0.0;
   out_4131332949940298666[284] = 0.0;
   out_4131332949940298666[285] = 1.0;
   out_4131332949940298666[286] = 0.0;
   out_4131332949940298666[287] = 0.0;
   out_4131332949940298666[288] = 0.0;
   out_4131332949940298666[289] = 0.0;
   out_4131332949940298666[290] = 0.0;
   out_4131332949940298666[291] = 0.0;
   out_4131332949940298666[292] = 0.0;
   out_4131332949940298666[293] = 0.0;
   out_4131332949940298666[294] = 0.0;
   out_4131332949940298666[295] = 0.0;
   out_4131332949940298666[296] = 0.0;
   out_4131332949940298666[297] = 0.0;
   out_4131332949940298666[298] = 0.0;
   out_4131332949940298666[299] = 0.0;
   out_4131332949940298666[300] = 0.0;
   out_4131332949940298666[301] = 0.0;
   out_4131332949940298666[302] = 0.0;
   out_4131332949940298666[303] = 0.0;
   out_4131332949940298666[304] = 1.0;
   out_4131332949940298666[305] = 0.0;
   out_4131332949940298666[306] = 0.0;
   out_4131332949940298666[307] = 0.0;
   out_4131332949940298666[308] = 0.0;
   out_4131332949940298666[309] = 0.0;
   out_4131332949940298666[310] = 0.0;
   out_4131332949940298666[311] = 0.0;
   out_4131332949940298666[312] = 0.0;
   out_4131332949940298666[313] = 0.0;
   out_4131332949940298666[314] = 0.0;
   out_4131332949940298666[315] = 0.0;
   out_4131332949940298666[316] = 0.0;
   out_4131332949940298666[317] = 0.0;
   out_4131332949940298666[318] = 0.0;
   out_4131332949940298666[319] = 0.0;
   out_4131332949940298666[320] = 0.0;
   out_4131332949940298666[321] = 0.0;
   out_4131332949940298666[322] = 0.0;
   out_4131332949940298666[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_6388120990768684370) {
   out_6388120990768684370[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_6388120990768684370[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_6388120990768684370[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_6388120990768684370[3] = dt*state[12] + state[3];
   out_6388120990768684370[4] = dt*state[13] + state[4];
   out_6388120990768684370[5] = dt*state[14] + state[5];
   out_6388120990768684370[6] = state[6];
   out_6388120990768684370[7] = state[7];
   out_6388120990768684370[8] = state[8];
   out_6388120990768684370[9] = state[9];
   out_6388120990768684370[10] = state[10];
   out_6388120990768684370[11] = state[11];
   out_6388120990768684370[12] = state[12];
   out_6388120990768684370[13] = state[13];
   out_6388120990768684370[14] = state[14];
   out_6388120990768684370[15] = state[15];
   out_6388120990768684370[16] = state[16];
   out_6388120990768684370[17] = state[17];
}
void F_fun(double *state, double dt, double *out_7678082896540462195) {
   out_7678082896540462195[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_7678082896540462195[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_7678082896540462195[2] = 0;
   out_7678082896540462195[3] = 0;
   out_7678082896540462195[4] = 0;
   out_7678082896540462195[5] = 0;
   out_7678082896540462195[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_7678082896540462195[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_7678082896540462195[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_7678082896540462195[9] = 0;
   out_7678082896540462195[10] = 0;
   out_7678082896540462195[11] = 0;
   out_7678082896540462195[12] = 0;
   out_7678082896540462195[13] = 0;
   out_7678082896540462195[14] = 0;
   out_7678082896540462195[15] = 0;
   out_7678082896540462195[16] = 0;
   out_7678082896540462195[17] = 0;
   out_7678082896540462195[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_7678082896540462195[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_7678082896540462195[20] = 0;
   out_7678082896540462195[21] = 0;
   out_7678082896540462195[22] = 0;
   out_7678082896540462195[23] = 0;
   out_7678082896540462195[24] = 0;
   out_7678082896540462195[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_7678082896540462195[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_7678082896540462195[27] = 0;
   out_7678082896540462195[28] = 0;
   out_7678082896540462195[29] = 0;
   out_7678082896540462195[30] = 0;
   out_7678082896540462195[31] = 0;
   out_7678082896540462195[32] = 0;
   out_7678082896540462195[33] = 0;
   out_7678082896540462195[34] = 0;
   out_7678082896540462195[35] = 0;
   out_7678082896540462195[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_7678082896540462195[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_7678082896540462195[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_7678082896540462195[39] = 0;
   out_7678082896540462195[40] = 0;
   out_7678082896540462195[41] = 0;
   out_7678082896540462195[42] = 0;
   out_7678082896540462195[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_7678082896540462195[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_7678082896540462195[45] = 0;
   out_7678082896540462195[46] = 0;
   out_7678082896540462195[47] = 0;
   out_7678082896540462195[48] = 0;
   out_7678082896540462195[49] = 0;
   out_7678082896540462195[50] = 0;
   out_7678082896540462195[51] = 0;
   out_7678082896540462195[52] = 0;
   out_7678082896540462195[53] = 0;
   out_7678082896540462195[54] = 0;
   out_7678082896540462195[55] = 0;
   out_7678082896540462195[56] = 0;
   out_7678082896540462195[57] = 1;
   out_7678082896540462195[58] = 0;
   out_7678082896540462195[59] = 0;
   out_7678082896540462195[60] = 0;
   out_7678082896540462195[61] = 0;
   out_7678082896540462195[62] = 0;
   out_7678082896540462195[63] = 0;
   out_7678082896540462195[64] = 0;
   out_7678082896540462195[65] = 0;
   out_7678082896540462195[66] = dt;
   out_7678082896540462195[67] = 0;
   out_7678082896540462195[68] = 0;
   out_7678082896540462195[69] = 0;
   out_7678082896540462195[70] = 0;
   out_7678082896540462195[71] = 0;
   out_7678082896540462195[72] = 0;
   out_7678082896540462195[73] = 0;
   out_7678082896540462195[74] = 0;
   out_7678082896540462195[75] = 0;
   out_7678082896540462195[76] = 1;
   out_7678082896540462195[77] = 0;
   out_7678082896540462195[78] = 0;
   out_7678082896540462195[79] = 0;
   out_7678082896540462195[80] = 0;
   out_7678082896540462195[81] = 0;
   out_7678082896540462195[82] = 0;
   out_7678082896540462195[83] = 0;
   out_7678082896540462195[84] = 0;
   out_7678082896540462195[85] = dt;
   out_7678082896540462195[86] = 0;
   out_7678082896540462195[87] = 0;
   out_7678082896540462195[88] = 0;
   out_7678082896540462195[89] = 0;
   out_7678082896540462195[90] = 0;
   out_7678082896540462195[91] = 0;
   out_7678082896540462195[92] = 0;
   out_7678082896540462195[93] = 0;
   out_7678082896540462195[94] = 0;
   out_7678082896540462195[95] = 1;
   out_7678082896540462195[96] = 0;
   out_7678082896540462195[97] = 0;
   out_7678082896540462195[98] = 0;
   out_7678082896540462195[99] = 0;
   out_7678082896540462195[100] = 0;
   out_7678082896540462195[101] = 0;
   out_7678082896540462195[102] = 0;
   out_7678082896540462195[103] = 0;
   out_7678082896540462195[104] = dt;
   out_7678082896540462195[105] = 0;
   out_7678082896540462195[106] = 0;
   out_7678082896540462195[107] = 0;
   out_7678082896540462195[108] = 0;
   out_7678082896540462195[109] = 0;
   out_7678082896540462195[110] = 0;
   out_7678082896540462195[111] = 0;
   out_7678082896540462195[112] = 0;
   out_7678082896540462195[113] = 0;
   out_7678082896540462195[114] = 1;
   out_7678082896540462195[115] = 0;
   out_7678082896540462195[116] = 0;
   out_7678082896540462195[117] = 0;
   out_7678082896540462195[118] = 0;
   out_7678082896540462195[119] = 0;
   out_7678082896540462195[120] = 0;
   out_7678082896540462195[121] = 0;
   out_7678082896540462195[122] = 0;
   out_7678082896540462195[123] = 0;
   out_7678082896540462195[124] = 0;
   out_7678082896540462195[125] = 0;
   out_7678082896540462195[126] = 0;
   out_7678082896540462195[127] = 0;
   out_7678082896540462195[128] = 0;
   out_7678082896540462195[129] = 0;
   out_7678082896540462195[130] = 0;
   out_7678082896540462195[131] = 0;
   out_7678082896540462195[132] = 0;
   out_7678082896540462195[133] = 1;
   out_7678082896540462195[134] = 0;
   out_7678082896540462195[135] = 0;
   out_7678082896540462195[136] = 0;
   out_7678082896540462195[137] = 0;
   out_7678082896540462195[138] = 0;
   out_7678082896540462195[139] = 0;
   out_7678082896540462195[140] = 0;
   out_7678082896540462195[141] = 0;
   out_7678082896540462195[142] = 0;
   out_7678082896540462195[143] = 0;
   out_7678082896540462195[144] = 0;
   out_7678082896540462195[145] = 0;
   out_7678082896540462195[146] = 0;
   out_7678082896540462195[147] = 0;
   out_7678082896540462195[148] = 0;
   out_7678082896540462195[149] = 0;
   out_7678082896540462195[150] = 0;
   out_7678082896540462195[151] = 0;
   out_7678082896540462195[152] = 1;
   out_7678082896540462195[153] = 0;
   out_7678082896540462195[154] = 0;
   out_7678082896540462195[155] = 0;
   out_7678082896540462195[156] = 0;
   out_7678082896540462195[157] = 0;
   out_7678082896540462195[158] = 0;
   out_7678082896540462195[159] = 0;
   out_7678082896540462195[160] = 0;
   out_7678082896540462195[161] = 0;
   out_7678082896540462195[162] = 0;
   out_7678082896540462195[163] = 0;
   out_7678082896540462195[164] = 0;
   out_7678082896540462195[165] = 0;
   out_7678082896540462195[166] = 0;
   out_7678082896540462195[167] = 0;
   out_7678082896540462195[168] = 0;
   out_7678082896540462195[169] = 0;
   out_7678082896540462195[170] = 0;
   out_7678082896540462195[171] = 1;
   out_7678082896540462195[172] = 0;
   out_7678082896540462195[173] = 0;
   out_7678082896540462195[174] = 0;
   out_7678082896540462195[175] = 0;
   out_7678082896540462195[176] = 0;
   out_7678082896540462195[177] = 0;
   out_7678082896540462195[178] = 0;
   out_7678082896540462195[179] = 0;
   out_7678082896540462195[180] = 0;
   out_7678082896540462195[181] = 0;
   out_7678082896540462195[182] = 0;
   out_7678082896540462195[183] = 0;
   out_7678082896540462195[184] = 0;
   out_7678082896540462195[185] = 0;
   out_7678082896540462195[186] = 0;
   out_7678082896540462195[187] = 0;
   out_7678082896540462195[188] = 0;
   out_7678082896540462195[189] = 0;
   out_7678082896540462195[190] = 1;
   out_7678082896540462195[191] = 0;
   out_7678082896540462195[192] = 0;
   out_7678082896540462195[193] = 0;
   out_7678082896540462195[194] = 0;
   out_7678082896540462195[195] = 0;
   out_7678082896540462195[196] = 0;
   out_7678082896540462195[197] = 0;
   out_7678082896540462195[198] = 0;
   out_7678082896540462195[199] = 0;
   out_7678082896540462195[200] = 0;
   out_7678082896540462195[201] = 0;
   out_7678082896540462195[202] = 0;
   out_7678082896540462195[203] = 0;
   out_7678082896540462195[204] = 0;
   out_7678082896540462195[205] = 0;
   out_7678082896540462195[206] = 0;
   out_7678082896540462195[207] = 0;
   out_7678082896540462195[208] = 0;
   out_7678082896540462195[209] = 1;
   out_7678082896540462195[210] = 0;
   out_7678082896540462195[211] = 0;
   out_7678082896540462195[212] = 0;
   out_7678082896540462195[213] = 0;
   out_7678082896540462195[214] = 0;
   out_7678082896540462195[215] = 0;
   out_7678082896540462195[216] = 0;
   out_7678082896540462195[217] = 0;
   out_7678082896540462195[218] = 0;
   out_7678082896540462195[219] = 0;
   out_7678082896540462195[220] = 0;
   out_7678082896540462195[221] = 0;
   out_7678082896540462195[222] = 0;
   out_7678082896540462195[223] = 0;
   out_7678082896540462195[224] = 0;
   out_7678082896540462195[225] = 0;
   out_7678082896540462195[226] = 0;
   out_7678082896540462195[227] = 0;
   out_7678082896540462195[228] = 1;
   out_7678082896540462195[229] = 0;
   out_7678082896540462195[230] = 0;
   out_7678082896540462195[231] = 0;
   out_7678082896540462195[232] = 0;
   out_7678082896540462195[233] = 0;
   out_7678082896540462195[234] = 0;
   out_7678082896540462195[235] = 0;
   out_7678082896540462195[236] = 0;
   out_7678082896540462195[237] = 0;
   out_7678082896540462195[238] = 0;
   out_7678082896540462195[239] = 0;
   out_7678082896540462195[240] = 0;
   out_7678082896540462195[241] = 0;
   out_7678082896540462195[242] = 0;
   out_7678082896540462195[243] = 0;
   out_7678082896540462195[244] = 0;
   out_7678082896540462195[245] = 0;
   out_7678082896540462195[246] = 0;
   out_7678082896540462195[247] = 1;
   out_7678082896540462195[248] = 0;
   out_7678082896540462195[249] = 0;
   out_7678082896540462195[250] = 0;
   out_7678082896540462195[251] = 0;
   out_7678082896540462195[252] = 0;
   out_7678082896540462195[253] = 0;
   out_7678082896540462195[254] = 0;
   out_7678082896540462195[255] = 0;
   out_7678082896540462195[256] = 0;
   out_7678082896540462195[257] = 0;
   out_7678082896540462195[258] = 0;
   out_7678082896540462195[259] = 0;
   out_7678082896540462195[260] = 0;
   out_7678082896540462195[261] = 0;
   out_7678082896540462195[262] = 0;
   out_7678082896540462195[263] = 0;
   out_7678082896540462195[264] = 0;
   out_7678082896540462195[265] = 0;
   out_7678082896540462195[266] = 1;
   out_7678082896540462195[267] = 0;
   out_7678082896540462195[268] = 0;
   out_7678082896540462195[269] = 0;
   out_7678082896540462195[270] = 0;
   out_7678082896540462195[271] = 0;
   out_7678082896540462195[272] = 0;
   out_7678082896540462195[273] = 0;
   out_7678082896540462195[274] = 0;
   out_7678082896540462195[275] = 0;
   out_7678082896540462195[276] = 0;
   out_7678082896540462195[277] = 0;
   out_7678082896540462195[278] = 0;
   out_7678082896540462195[279] = 0;
   out_7678082896540462195[280] = 0;
   out_7678082896540462195[281] = 0;
   out_7678082896540462195[282] = 0;
   out_7678082896540462195[283] = 0;
   out_7678082896540462195[284] = 0;
   out_7678082896540462195[285] = 1;
   out_7678082896540462195[286] = 0;
   out_7678082896540462195[287] = 0;
   out_7678082896540462195[288] = 0;
   out_7678082896540462195[289] = 0;
   out_7678082896540462195[290] = 0;
   out_7678082896540462195[291] = 0;
   out_7678082896540462195[292] = 0;
   out_7678082896540462195[293] = 0;
   out_7678082896540462195[294] = 0;
   out_7678082896540462195[295] = 0;
   out_7678082896540462195[296] = 0;
   out_7678082896540462195[297] = 0;
   out_7678082896540462195[298] = 0;
   out_7678082896540462195[299] = 0;
   out_7678082896540462195[300] = 0;
   out_7678082896540462195[301] = 0;
   out_7678082896540462195[302] = 0;
   out_7678082896540462195[303] = 0;
   out_7678082896540462195[304] = 1;
   out_7678082896540462195[305] = 0;
   out_7678082896540462195[306] = 0;
   out_7678082896540462195[307] = 0;
   out_7678082896540462195[308] = 0;
   out_7678082896540462195[309] = 0;
   out_7678082896540462195[310] = 0;
   out_7678082896540462195[311] = 0;
   out_7678082896540462195[312] = 0;
   out_7678082896540462195[313] = 0;
   out_7678082896540462195[314] = 0;
   out_7678082896540462195[315] = 0;
   out_7678082896540462195[316] = 0;
   out_7678082896540462195[317] = 0;
   out_7678082896540462195[318] = 0;
   out_7678082896540462195[319] = 0;
   out_7678082896540462195[320] = 0;
   out_7678082896540462195[321] = 0;
   out_7678082896540462195[322] = 0;
   out_7678082896540462195[323] = 1;
}
void h_4(double *state, double *unused, double *out_285865806461862263) {
   out_285865806461862263[0] = state[6] + state[9];
   out_285865806461862263[1] = state[7] + state[10];
   out_285865806461862263[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_2311634224034001805) {
   out_2311634224034001805[0] = 0;
   out_2311634224034001805[1] = 0;
   out_2311634224034001805[2] = 0;
   out_2311634224034001805[3] = 0;
   out_2311634224034001805[4] = 0;
   out_2311634224034001805[5] = 0;
   out_2311634224034001805[6] = 1;
   out_2311634224034001805[7] = 0;
   out_2311634224034001805[8] = 0;
   out_2311634224034001805[9] = 1;
   out_2311634224034001805[10] = 0;
   out_2311634224034001805[11] = 0;
   out_2311634224034001805[12] = 0;
   out_2311634224034001805[13] = 0;
   out_2311634224034001805[14] = 0;
   out_2311634224034001805[15] = 0;
   out_2311634224034001805[16] = 0;
   out_2311634224034001805[17] = 0;
   out_2311634224034001805[18] = 0;
   out_2311634224034001805[19] = 0;
   out_2311634224034001805[20] = 0;
   out_2311634224034001805[21] = 0;
   out_2311634224034001805[22] = 0;
   out_2311634224034001805[23] = 0;
   out_2311634224034001805[24] = 0;
   out_2311634224034001805[25] = 1;
   out_2311634224034001805[26] = 0;
   out_2311634224034001805[27] = 0;
   out_2311634224034001805[28] = 1;
   out_2311634224034001805[29] = 0;
   out_2311634224034001805[30] = 0;
   out_2311634224034001805[31] = 0;
   out_2311634224034001805[32] = 0;
   out_2311634224034001805[33] = 0;
   out_2311634224034001805[34] = 0;
   out_2311634224034001805[35] = 0;
   out_2311634224034001805[36] = 0;
   out_2311634224034001805[37] = 0;
   out_2311634224034001805[38] = 0;
   out_2311634224034001805[39] = 0;
   out_2311634224034001805[40] = 0;
   out_2311634224034001805[41] = 0;
   out_2311634224034001805[42] = 0;
   out_2311634224034001805[43] = 0;
   out_2311634224034001805[44] = 1;
   out_2311634224034001805[45] = 0;
   out_2311634224034001805[46] = 0;
   out_2311634224034001805[47] = 1;
   out_2311634224034001805[48] = 0;
   out_2311634224034001805[49] = 0;
   out_2311634224034001805[50] = 0;
   out_2311634224034001805[51] = 0;
   out_2311634224034001805[52] = 0;
   out_2311634224034001805[53] = 0;
}
void h_10(double *state, double *unused, double *out_3345721551474225191) {
   out_3345721551474225191[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_3345721551474225191[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_3345721551474225191[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_7600016663620136720) {
   out_7600016663620136720[0] = 0;
   out_7600016663620136720[1] = 9.8100000000000005*cos(state[1]);
   out_7600016663620136720[2] = 0;
   out_7600016663620136720[3] = 0;
   out_7600016663620136720[4] = -state[8];
   out_7600016663620136720[5] = state[7];
   out_7600016663620136720[6] = 0;
   out_7600016663620136720[7] = state[5];
   out_7600016663620136720[8] = -state[4];
   out_7600016663620136720[9] = 0;
   out_7600016663620136720[10] = 0;
   out_7600016663620136720[11] = 0;
   out_7600016663620136720[12] = 1;
   out_7600016663620136720[13] = 0;
   out_7600016663620136720[14] = 0;
   out_7600016663620136720[15] = 1;
   out_7600016663620136720[16] = 0;
   out_7600016663620136720[17] = 0;
   out_7600016663620136720[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_7600016663620136720[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_7600016663620136720[20] = 0;
   out_7600016663620136720[21] = state[8];
   out_7600016663620136720[22] = 0;
   out_7600016663620136720[23] = -state[6];
   out_7600016663620136720[24] = -state[5];
   out_7600016663620136720[25] = 0;
   out_7600016663620136720[26] = state[3];
   out_7600016663620136720[27] = 0;
   out_7600016663620136720[28] = 0;
   out_7600016663620136720[29] = 0;
   out_7600016663620136720[30] = 0;
   out_7600016663620136720[31] = 1;
   out_7600016663620136720[32] = 0;
   out_7600016663620136720[33] = 0;
   out_7600016663620136720[34] = 1;
   out_7600016663620136720[35] = 0;
   out_7600016663620136720[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_7600016663620136720[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_7600016663620136720[38] = 0;
   out_7600016663620136720[39] = -state[7];
   out_7600016663620136720[40] = state[6];
   out_7600016663620136720[41] = 0;
   out_7600016663620136720[42] = state[4];
   out_7600016663620136720[43] = -state[3];
   out_7600016663620136720[44] = 0;
   out_7600016663620136720[45] = 0;
   out_7600016663620136720[46] = 0;
   out_7600016663620136720[47] = 0;
   out_7600016663620136720[48] = 0;
   out_7600016663620136720[49] = 0;
   out_7600016663620136720[50] = 1;
   out_7600016663620136720[51] = 0;
   out_7600016663620136720[52] = 0;
   out_7600016663620136720[53] = 1;
}
void h_13(double *state, double *unused, double *out_3239845409590022619) {
   out_3239845409590022619[0] = state[3];
   out_3239845409590022619[1] = state[4];
   out_3239845409590022619[2] = state[5];
}
void H_13(double *state, double *unused, double *out_5523908049366334606) {
   out_5523908049366334606[0] = 0;
   out_5523908049366334606[1] = 0;
   out_5523908049366334606[2] = 0;
   out_5523908049366334606[3] = 1;
   out_5523908049366334606[4] = 0;
   out_5523908049366334606[5] = 0;
   out_5523908049366334606[6] = 0;
   out_5523908049366334606[7] = 0;
   out_5523908049366334606[8] = 0;
   out_5523908049366334606[9] = 0;
   out_5523908049366334606[10] = 0;
   out_5523908049366334606[11] = 0;
   out_5523908049366334606[12] = 0;
   out_5523908049366334606[13] = 0;
   out_5523908049366334606[14] = 0;
   out_5523908049366334606[15] = 0;
   out_5523908049366334606[16] = 0;
   out_5523908049366334606[17] = 0;
   out_5523908049366334606[18] = 0;
   out_5523908049366334606[19] = 0;
   out_5523908049366334606[20] = 0;
   out_5523908049366334606[21] = 0;
   out_5523908049366334606[22] = 1;
   out_5523908049366334606[23] = 0;
   out_5523908049366334606[24] = 0;
   out_5523908049366334606[25] = 0;
   out_5523908049366334606[26] = 0;
   out_5523908049366334606[27] = 0;
   out_5523908049366334606[28] = 0;
   out_5523908049366334606[29] = 0;
   out_5523908049366334606[30] = 0;
   out_5523908049366334606[31] = 0;
   out_5523908049366334606[32] = 0;
   out_5523908049366334606[33] = 0;
   out_5523908049366334606[34] = 0;
   out_5523908049366334606[35] = 0;
   out_5523908049366334606[36] = 0;
   out_5523908049366334606[37] = 0;
   out_5523908049366334606[38] = 0;
   out_5523908049366334606[39] = 0;
   out_5523908049366334606[40] = 0;
   out_5523908049366334606[41] = 1;
   out_5523908049366334606[42] = 0;
   out_5523908049366334606[43] = 0;
   out_5523908049366334606[44] = 0;
   out_5523908049366334606[45] = 0;
   out_5523908049366334606[46] = 0;
   out_5523908049366334606[47] = 0;
   out_5523908049366334606[48] = 0;
   out_5523908049366334606[49] = 0;
   out_5523908049366334606[50] = 0;
   out_5523908049366334606[51] = 0;
   out_5523908049366334606[52] = 0;
   out_5523908049366334606[53] = 0;
}
void h_14(double *state, double *unused, double *out_8238467406184066972) {
   out_8238467406184066972[0] = state[6];
   out_8238467406184066972[1] = state[7];
   out_8238467406184066972[2] = state[8];
}
void H_14(double *state, double *unused, double *out_6274875080373486334) {
   out_6274875080373486334[0] = 0;
   out_6274875080373486334[1] = 0;
   out_6274875080373486334[2] = 0;
   out_6274875080373486334[3] = 0;
   out_6274875080373486334[4] = 0;
   out_6274875080373486334[5] = 0;
   out_6274875080373486334[6] = 1;
   out_6274875080373486334[7] = 0;
   out_6274875080373486334[8] = 0;
   out_6274875080373486334[9] = 0;
   out_6274875080373486334[10] = 0;
   out_6274875080373486334[11] = 0;
   out_6274875080373486334[12] = 0;
   out_6274875080373486334[13] = 0;
   out_6274875080373486334[14] = 0;
   out_6274875080373486334[15] = 0;
   out_6274875080373486334[16] = 0;
   out_6274875080373486334[17] = 0;
   out_6274875080373486334[18] = 0;
   out_6274875080373486334[19] = 0;
   out_6274875080373486334[20] = 0;
   out_6274875080373486334[21] = 0;
   out_6274875080373486334[22] = 0;
   out_6274875080373486334[23] = 0;
   out_6274875080373486334[24] = 0;
   out_6274875080373486334[25] = 1;
   out_6274875080373486334[26] = 0;
   out_6274875080373486334[27] = 0;
   out_6274875080373486334[28] = 0;
   out_6274875080373486334[29] = 0;
   out_6274875080373486334[30] = 0;
   out_6274875080373486334[31] = 0;
   out_6274875080373486334[32] = 0;
   out_6274875080373486334[33] = 0;
   out_6274875080373486334[34] = 0;
   out_6274875080373486334[35] = 0;
   out_6274875080373486334[36] = 0;
   out_6274875080373486334[37] = 0;
   out_6274875080373486334[38] = 0;
   out_6274875080373486334[39] = 0;
   out_6274875080373486334[40] = 0;
   out_6274875080373486334[41] = 0;
   out_6274875080373486334[42] = 0;
   out_6274875080373486334[43] = 0;
   out_6274875080373486334[44] = 1;
   out_6274875080373486334[45] = 0;
   out_6274875080373486334[46] = 0;
   out_6274875080373486334[47] = 0;
   out_6274875080373486334[48] = 0;
   out_6274875080373486334[49] = 0;
   out_6274875080373486334[50] = 0;
   out_6274875080373486334[51] = 0;
   out_6274875080373486334[52] = 0;
   out_6274875080373486334[53] = 0;
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
void pose_err_fun(double *nom_x, double *delta_x, double *out_7117000844039973656) {
  err_fun(nom_x, delta_x, out_7117000844039973656);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_5738271447995775317) {
  inv_err_fun(nom_x, true_x, out_5738271447995775317);
}
void pose_H_mod_fun(double *state, double *out_4131332949940298666) {
  H_mod_fun(state, out_4131332949940298666);
}
void pose_f_fun(double *state, double dt, double *out_6388120990768684370) {
  f_fun(state,  dt, out_6388120990768684370);
}
void pose_F_fun(double *state, double dt, double *out_7678082896540462195) {
  F_fun(state,  dt, out_7678082896540462195);
}
void pose_h_4(double *state, double *unused, double *out_285865806461862263) {
  h_4(state, unused, out_285865806461862263);
}
void pose_H_4(double *state, double *unused, double *out_2311634224034001805) {
  H_4(state, unused, out_2311634224034001805);
}
void pose_h_10(double *state, double *unused, double *out_3345721551474225191) {
  h_10(state, unused, out_3345721551474225191);
}
void pose_H_10(double *state, double *unused, double *out_7600016663620136720) {
  H_10(state, unused, out_7600016663620136720);
}
void pose_h_13(double *state, double *unused, double *out_3239845409590022619) {
  h_13(state, unused, out_3239845409590022619);
}
void pose_H_13(double *state, double *unused, double *out_5523908049366334606) {
  H_13(state, unused, out_5523908049366334606);
}
void pose_h_14(double *state, double *unused, double *out_8238467406184066972) {
  h_14(state, unused, out_8238467406184066972);
}
void pose_H_14(double *state, double *unused, double *out_6274875080373486334) {
  H_14(state, unused, out_6274875080373486334);
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
