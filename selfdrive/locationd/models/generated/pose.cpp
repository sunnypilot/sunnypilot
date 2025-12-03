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
void err_fun(double *nom_x, double *delta_x, double *out_6822829480064316427) {
   out_6822829480064316427[0] = delta_x[0] + nom_x[0];
   out_6822829480064316427[1] = delta_x[1] + nom_x[1];
   out_6822829480064316427[2] = delta_x[2] + nom_x[2];
   out_6822829480064316427[3] = delta_x[3] + nom_x[3];
   out_6822829480064316427[4] = delta_x[4] + nom_x[4];
   out_6822829480064316427[5] = delta_x[5] + nom_x[5];
   out_6822829480064316427[6] = delta_x[6] + nom_x[6];
   out_6822829480064316427[7] = delta_x[7] + nom_x[7];
   out_6822829480064316427[8] = delta_x[8] + nom_x[8];
   out_6822829480064316427[9] = delta_x[9] + nom_x[9];
   out_6822829480064316427[10] = delta_x[10] + nom_x[10];
   out_6822829480064316427[11] = delta_x[11] + nom_x[11];
   out_6822829480064316427[12] = delta_x[12] + nom_x[12];
   out_6822829480064316427[13] = delta_x[13] + nom_x[13];
   out_6822829480064316427[14] = delta_x[14] + nom_x[14];
   out_6822829480064316427[15] = delta_x[15] + nom_x[15];
   out_6822829480064316427[16] = delta_x[16] + nom_x[16];
   out_6822829480064316427[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_8351755903623348291) {
   out_8351755903623348291[0] = -nom_x[0] + true_x[0];
   out_8351755903623348291[1] = -nom_x[1] + true_x[1];
   out_8351755903623348291[2] = -nom_x[2] + true_x[2];
   out_8351755903623348291[3] = -nom_x[3] + true_x[3];
   out_8351755903623348291[4] = -nom_x[4] + true_x[4];
   out_8351755903623348291[5] = -nom_x[5] + true_x[5];
   out_8351755903623348291[6] = -nom_x[6] + true_x[6];
   out_8351755903623348291[7] = -nom_x[7] + true_x[7];
   out_8351755903623348291[8] = -nom_x[8] + true_x[8];
   out_8351755903623348291[9] = -nom_x[9] + true_x[9];
   out_8351755903623348291[10] = -nom_x[10] + true_x[10];
   out_8351755903623348291[11] = -nom_x[11] + true_x[11];
   out_8351755903623348291[12] = -nom_x[12] + true_x[12];
   out_8351755903623348291[13] = -nom_x[13] + true_x[13];
   out_8351755903623348291[14] = -nom_x[14] + true_x[14];
   out_8351755903623348291[15] = -nom_x[15] + true_x[15];
   out_8351755903623348291[16] = -nom_x[16] + true_x[16];
   out_8351755903623348291[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_3160786903936238065) {
   out_3160786903936238065[0] = 1.0;
   out_3160786903936238065[1] = 0.0;
   out_3160786903936238065[2] = 0.0;
   out_3160786903936238065[3] = 0.0;
   out_3160786903936238065[4] = 0.0;
   out_3160786903936238065[5] = 0.0;
   out_3160786903936238065[6] = 0.0;
   out_3160786903936238065[7] = 0.0;
   out_3160786903936238065[8] = 0.0;
   out_3160786903936238065[9] = 0.0;
   out_3160786903936238065[10] = 0.0;
   out_3160786903936238065[11] = 0.0;
   out_3160786903936238065[12] = 0.0;
   out_3160786903936238065[13] = 0.0;
   out_3160786903936238065[14] = 0.0;
   out_3160786903936238065[15] = 0.0;
   out_3160786903936238065[16] = 0.0;
   out_3160786903936238065[17] = 0.0;
   out_3160786903936238065[18] = 0.0;
   out_3160786903936238065[19] = 1.0;
   out_3160786903936238065[20] = 0.0;
   out_3160786903936238065[21] = 0.0;
   out_3160786903936238065[22] = 0.0;
   out_3160786903936238065[23] = 0.0;
   out_3160786903936238065[24] = 0.0;
   out_3160786903936238065[25] = 0.0;
   out_3160786903936238065[26] = 0.0;
   out_3160786903936238065[27] = 0.0;
   out_3160786903936238065[28] = 0.0;
   out_3160786903936238065[29] = 0.0;
   out_3160786903936238065[30] = 0.0;
   out_3160786903936238065[31] = 0.0;
   out_3160786903936238065[32] = 0.0;
   out_3160786903936238065[33] = 0.0;
   out_3160786903936238065[34] = 0.0;
   out_3160786903936238065[35] = 0.0;
   out_3160786903936238065[36] = 0.0;
   out_3160786903936238065[37] = 0.0;
   out_3160786903936238065[38] = 1.0;
   out_3160786903936238065[39] = 0.0;
   out_3160786903936238065[40] = 0.0;
   out_3160786903936238065[41] = 0.0;
   out_3160786903936238065[42] = 0.0;
   out_3160786903936238065[43] = 0.0;
   out_3160786903936238065[44] = 0.0;
   out_3160786903936238065[45] = 0.0;
   out_3160786903936238065[46] = 0.0;
   out_3160786903936238065[47] = 0.0;
   out_3160786903936238065[48] = 0.0;
   out_3160786903936238065[49] = 0.0;
   out_3160786903936238065[50] = 0.0;
   out_3160786903936238065[51] = 0.0;
   out_3160786903936238065[52] = 0.0;
   out_3160786903936238065[53] = 0.0;
   out_3160786903936238065[54] = 0.0;
   out_3160786903936238065[55] = 0.0;
   out_3160786903936238065[56] = 0.0;
   out_3160786903936238065[57] = 1.0;
   out_3160786903936238065[58] = 0.0;
   out_3160786903936238065[59] = 0.0;
   out_3160786903936238065[60] = 0.0;
   out_3160786903936238065[61] = 0.0;
   out_3160786903936238065[62] = 0.0;
   out_3160786903936238065[63] = 0.0;
   out_3160786903936238065[64] = 0.0;
   out_3160786903936238065[65] = 0.0;
   out_3160786903936238065[66] = 0.0;
   out_3160786903936238065[67] = 0.0;
   out_3160786903936238065[68] = 0.0;
   out_3160786903936238065[69] = 0.0;
   out_3160786903936238065[70] = 0.0;
   out_3160786903936238065[71] = 0.0;
   out_3160786903936238065[72] = 0.0;
   out_3160786903936238065[73] = 0.0;
   out_3160786903936238065[74] = 0.0;
   out_3160786903936238065[75] = 0.0;
   out_3160786903936238065[76] = 1.0;
   out_3160786903936238065[77] = 0.0;
   out_3160786903936238065[78] = 0.0;
   out_3160786903936238065[79] = 0.0;
   out_3160786903936238065[80] = 0.0;
   out_3160786903936238065[81] = 0.0;
   out_3160786903936238065[82] = 0.0;
   out_3160786903936238065[83] = 0.0;
   out_3160786903936238065[84] = 0.0;
   out_3160786903936238065[85] = 0.0;
   out_3160786903936238065[86] = 0.0;
   out_3160786903936238065[87] = 0.0;
   out_3160786903936238065[88] = 0.0;
   out_3160786903936238065[89] = 0.0;
   out_3160786903936238065[90] = 0.0;
   out_3160786903936238065[91] = 0.0;
   out_3160786903936238065[92] = 0.0;
   out_3160786903936238065[93] = 0.0;
   out_3160786903936238065[94] = 0.0;
   out_3160786903936238065[95] = 1.0;
   out_3160786903936238065[96] = 0.0;
   out_3160786903936238065[97] = 0.0;
   out_3160786903936238065[98] = 0.0;
   out_3160786903936238065[99] = 0.0;
   out_3160786903936238065[100] = 0.0;
   out_3160786903936238065[101] = 0.0;
   out_3160786903936238065[102] = 0.0;
   out_3160786903936238065[103] = 0.0;
   out_3160786903936238065[104] = 0.0;
   out_3160786903936238065[105] = 0.0;
   out_3160786903936238065[106] = 0.0;
   out_3160786903936238065[107] = 0.0;
   out_3160786903936238065[108] = 0.0;
   out_3160786903936238065[109] = 0.0;
   out_3160786903936238065[110] = 0.0;
   out_3160786903936238065[111] = 0.0;
   out_3160786903936238065[112] = 0.0;
   out_3160786903936238065[113] = 0.0;
   out_3160786903936238065[114] = 1.0;
   out_3160786903936238065[115] = 0.0;
   out_3160786903936238065[116] = 0.0;
   out_3160786903936238065[117] = 0.0;
   out_3160786903936238065[118] = 0.0;
   out_3160786903936238065[119] = 0.0;
   out_3160786903936238065[120] = 0.0;
   out_3160786903936238065[121] = 0.0;
   out_3160786903936238065[122] = 0.0;
   out_3160786903936238065[123] = 0.0;
   out_3160786903936238065[124] = 0.0;
   out_3160786903936238065[125] = 0.0;
   out_3160786903936238065[126] = 0.0;
   out_3160786903936238065[127] = 0.0;
   out_3160786903936238065[128] = 0.0;
   out_3160786903936238065[129] = 0.0;
   out_3160786903936238065[130] = 0.0;
   out_3160786903936238065[131] = 0.0;
   out_3160786903936238065[132] = 0.0;
   out_3160786903936238065[133] = 1.0;
   out_3160786903936238065[134] = 0.0;
   out_3160786903936238065[135] = 0.0;
   out_3160786903936238065[136] = 0.0;
   out_3160786903936238065[137] = 0.0;
   out_3160786903936238065[138] = 0.0;
   out_3160786903936238065[139] = 0.0;
   out_3160786903936238065[140] = 0.0;
   out_3160786903936238065[141] = 0.0;
   out_3160786903936238065[142] = 0.0;
   out_3160786903936238065[143] = 0.0;
   out_3160786903936238065[144] = 0.0;
   out_3160786903936238065[145] = 0.0;
   out_3160786903936238065[146] = 0.0;
   out_3160786903936238065[147] = 0.0;
   out_3160786903936238065[148] = 0.0;
   out_3160786903936238065[149] = 0.0;
   out_3160786903936238065[150] = 0.0;
   out_3160786903936238065[151] = 0.0;
   out_3160786903936238065[152] = 1.0;
   out_3160786903936238065[153] = 0.0;
   out_3160786903936238065[154] = 0.0;
   out_3160786903936238065[155] = 0.0;
   out_3160786903936238065[156] = 0.0;
   out_3160786903936238065[157] = 0.0;
   out_3160786903936238065[158] = 0.0;
   out_3160786903936238065[159] = 0.0;
   out_3160786903936238065[160] = 0.0;
   out_3160786903936238065[161] = 0.0;
   out_3160786903936238065[162] = 0.0;
   out_3160786903936238065[163] = 0.0;
   out_3160786903936238065[164] = 0.0;
   out_3160786903936238065[165] = 0.0;
   out_3160786903936238065[166] = 0.0;
   out_3160786903936238065[167] = 0.0;
   out_3160786903936238065[168] = 0.0;
   out_3160786903936238065[169] = 0.0;
   out_3160786903936238065[170] = 0.0;
   out_3160786903936238065[171] = 1.0;
   out_3160786903936238065[172] = 0.0;
   out_3160786903936238065[173] = 0.0;
   out_3160786903936238065[174] = 0.0;
   out_3160786903936238065[175] = 0.0;
   out_3160786903936238065[176] = 0.0;
   out_3160786903936238065[177] = 0.0;
   out_3160786903936238065[178] = 0.0;
   out_3160786903936238065[179] = 0.0;
   out_3160786903936238065[180] = 0.0;
   out_3160786903936238065[181] = 0.0;
   out_3160786903936238065[182] = 0.0;
   out_3160786903936238065[183] = 0.0;
   out_3160786903936238065[184] = 0.0;
   out_3160786903936238065[185] = 0.0;
   out_3160786903936238065[186] = 0.0;
   out_3160786903936238065[187] = 0.0;
   out_3160786903936238065[188] = 0.0;
   out_3160786903936238065[189] = 0.0;
   out_3160786903936238065[190] = 1.0;
   out_3160786903936238065[191] = 0.0;
   out_3160786903936238065[192] = 0.0;
   out_3160786903936238065[193] = 0.0;
   out_3160786903936238065[194] = 0.0;
   out_3160786903936238065[195] = 0.0;
   out_3160786903936238065[196] = 0.0;
   out_3160786903936238065[197] = 0.0;
   out_3160786903936238065[198] = 0.0;
   out_3160786903936238065[199] = 0.0;
   out_3160786903936238065[200] = 0.0;
   out_3160786903936238065[201] = 0.0;
   out_3160786903936238065[202] = 0.0;
   out_3160786903936238065[203] = 0.0;
   out_3160786903936238065[204] = 0.0;
   out_3160786903936238065[205] = 0.0;
   out_3160786903936238065[206] = 0.0;
   out_3160786903936238065[207] = 0.0;
   out_3160786903936238065[208] = 0.0;
   out_3160786903936238065[209] = 1.0;
   out_3160786903936238065[210] = 0.0;
   out_3160786903936238065[211] = 0.0;
   out_3160786903936238065[212] = 0.0;
   out_3160786903936238065[213] = 0.0;
   out_3160786903936238065[214] = 0.0;
   out_3160786903936238065[215] = 0.0;
   out_3160786903936238065[216] = 0.0;
   out_3160786903936238065[217] = 0.0;
   out_3160786903936238065[218] = 0.0;
   out_3160786903936238065[219] = 0.0;
   out_3160786903936238065[220] = 0.0;
   out_3160786903936238065[221] = 0.0;
   out_3160786903936238065[222] = 0.0;
   out_3160786903936238065[223] = 0.0;
   out_3160786903936238065[224] = 0.0;
   out_3160786903936238065[225] = 0.0;
   out_3160786903936238065[226] = 0.0;
   out_3160786903936238065[227] = 0.0;
   out_3160786903936238065[228] = 1.0;
   out_3160786903936238065[229] = 0.0;
   out_3160786903936238065[230] = 0.0;
   out_3160786903936238065[231] = 0.0;
   out_3160786903936238065[232] = 0.0;
   out_3160786903936238065[233] = 0.0;
   out_3160786903936238065[234] = 0.0;
   out_3160786903936238065[235] = 0.0;
   out_3160786903936238065[236] = 0.0;
   out_3160786903936238065[237] = 0.0;
   out_3160786903936238065[238] = 0.0;
   out_3160786903936238065[239] = 0.0;
   out_3160786903936238065[240] = 0.0;
   out_3160786903936238065[241] = 0.0;
   out_3160786903936238065[242] = 0.0;
   out_3160786903936238065[243] = 0.0;
   out_3160786903936238065[244] = 0.0;
   out_3160786903936238065[245] = 0.0;
   out_3160786903936238065[246] = 0.0;
   out_3160786903936238065[247] = 1.0;
   out_3160786903936238065[248] = 0.0;
   out_3160786903936238065[249] = 0.0;
   out_3160786903936238065[250] = 0.0;
   out_3160786903936238065[251] = 0.0;
   out_3160786903936238065[252] = 0.0;
   out_3160786903936238065[253] = 0.0;
   out_3160786903936238065[254] = 0.0;
   out_3160786903936238065[255] = 0.0;
   out_3160786903936238065[256] = 0.0;
   out_3160786903936238065[257] = 0.0;
   out_3160786903936238065[258] = 0.0;
   out_3160786903936238065[259] = 0.0;
   out_3160786903936238065[260] = 0.0;
   out_3160786903936238065[261] = 0.0;
   out_3160786903936238065[262] = 0.0;
   out_3160786903936238065[263] = 0.0;
   out_3160786903936238065[264] = 0.0;
   out_3160786903936238065[265] = 0.0;
   out_3160786903936238065[266] = 1.0;
   out_3160786903936238065[267] = 0.0;
   out_3160786903936238065[268] = 0.0;
   out_3160786903936238065[269] = 0.0;
   out_3160786903936238065[270] = 0.0;
   out_3160786903936238065[271] = 0.0;
   out_3160786903936238065[272] = 0.0;
   out_3160786903936238065[273] = 0.0;
   out_3160786903936238065[274] = 0.0;
   out_3160786903936238065[275] = 0.0;
   out_3160786903936238065[276] = 0.0;
   out_3160786903936238065[277] = 0.0;
   out_3160786903936238065[278] = 0.0;
   out_3160786903936238065[279] = 0.0;
   out_3160786903936238065[280] = 0.0;
   out_3160786903936238065[281] = 0.0;
   out_3160786903936238065[282] = 0.0;
   out_3160786903936238065[283] = 0.0;
   out_3160786903936238065[284] = 0.0;
   out_3160786903936238065[285] = 1.0;
   out_3160786903936238065[286] = 0.0;
   out_3160786903936238065[287] = 0.0;
   out_3160786903936238065[288] = 0.0;
   out_3160786903936238065[289] = 0.0;
   out_3160786903936238065[290] = 0.0;
   out_3160786903936238065[291] = 0.0;
   out_3160786903936238065[292] = 0.0;
   out_3160786903936238065[293] = 0.0;
   out_3160786903936238065[294] = 0.0;
   out_3160786903936238065[295] = 0.0;
   out_3160786903936238065[296] = 0.0;
   out_3160786903936238065[297] = 0.0;
   out_3160786903936238065[298] = 0.0;
   out_3160786903936238065[299] = 0.0;
   out_3160786903936238065[300] = 0.0;
   out_3160786903936238065[301] = 0.0;
   out_3160786903936238065[302] = 0.0;
   out_3160786903936238065[303] = 0.0;
   out_3160786903936238065[304] = 1.0;
   out_3160786903936238065[305] = 0.0;
   out_3160786903936238065[306] = 0.0;
   out_3160786903936238065[307] = 0.0;
   out_3160786903936238065[308] = 0.0;
   out_3160786903936238065[309] = 0.0;
   out_3160786903936238065[310] = 0.0;
   out_3160786903936238065[311] = 0.0;
   out_3160786903936238065[312] = 0.0;
   out_3160786903936238065[313] = 0.0;
   out_3160786903936238065[314] = 0.0;
   out_3160786903936238065[315] = 0.0;
   out_3160786903936238065[316] = 0.0;
   out_3160786903936238065[317] = 0.0;
   out_3160786903936238065[318] = 0.0;
   out_3160786903936238065[319] = 0.0;
   out_3160786903936238065[320] = 0.0;
   out_3160786903936238065[321] = 0.0;
   out_3160786903936238065[322] = 0.0;
   out_3160786903936238065[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_3649248979314528992) {
   out_3649248979314528992[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_3649248979314528992[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_3649248979314528992[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_3649248979314528992[3] = dt*state[12] + state[3];
   out_3649248979314528992[4] = dt*state[13] + state[4];
   out_3649248979314528992[5] = dt*state[14] + state[5];
   out_3649248979314528992[6] = state[6];
   out_3649248979314528992[7] = state[7];
   out_3649248979314528992[8] = state[8];
   out_3649248979314528992[9] = state[9];
   out_3649248979314528992[10] = state[10];
   out_3649248979314528992[11] = state[11];
   out_3649248979314528992[12] = state[12];
   out_3649248979314528992[13] = state[13];
   out_3649248979314528992[14] = state[14];
   out_3649248979314528992[15] = state[15];
   out_3649248979314528992[16] = state[16];
   out_3649248979314528992[17] = state[17];
}
void F_fun(double *state, double dt, double *out_5219362633347118737) {
   out_5219362633347118737[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_5219362633347118737[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_5219362633347118737[2] = 0;
   out_5219362633347118737[3] = 0;
   out_5219362633347118737[4] = 0;
   out_5219362633347118737[5] = 0;
   out_5219362633347118737[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_5219362633347118737[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_5219362633347118737[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_5219362633347118737[9] = 0;
   out_5219362633347118737[10] = 0;
   out_5219362633347118737[11] = 0;
   out_5219362633347118737[12] = 0;
   out_5219362633347118737[13] = 0;
   out_5219362633347118737[14] = 0;
   out_5219362633347118737[15] = 0;
   out_5219362633347118737[16] = 0;
   out_5219362633347118737[17] = 0;
   out_5219362633347118737[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_5219362633347118737[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_5219362633347118737[20] = 0;
   out_5219362633347118737[21] = 0;
   out_5219362633347118737[22] = 0;
   out_5219362633347118737[23] = 0;
   out_5219362633347118737[24] = 0;
   out_5219362633347118737[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_5219362633347118737[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_5219362633347118737[27] = 0;
   out_5219362633347118737[28] = 0;
   out_5219362633347118737[29] = 0;
   out_5219362633347118737[30] = 0;
   out_5219362633347118737[31] = 0;
   out_5219362633347118737[32] = 0;
   out_5219362633347118737[33] = 0;
   out_5219362633347118737[34] = 0;
   out_5219362633347118737[35] = 0;
   out_5219362633347118737[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_5219362633347118737[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_5219362633347118737[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_5219362633347118737[39] = 0;
   out_5219362633347118737[40] = 0;
   out_5219362633347118737[41] = 0;
   out_5219362633347118737[42] = 0;
   out_5219362633347118737[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_5219362633347118737[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_5219362633347118737[45] = 0;
   out_5219362633347118737[46] = 0;
   out_5219362633347118737[47] = 0;
   out_5219362633347118737[48] = 0;
   out_5219362633347118737[49] = 0;
   out_5219362633347118737[50] = 0;
   out_5219362633347118737[51] = 0;
   out_5219362633347118737[52] = 0;
   out_5219362633347118737[53] = 0;
   out_5219362633347118737[54] = 0;
   out_5219362633347118737[55] = 0;
   out_5219362633347118737[56] = 0;
   out_5219362633347118737[57] = 1;
   out_5219362633347118737[58] = 0;
   out_5219362633347118737[59] = 0;
   out_5219362633347118737[60] = 0;
   out_5219362633347118737[61] = 0;
   out_5219362633347118737[62] = 0;
   out_5219362633347118737[63] = 0;
   out_5219362633347118737[64] = 0;
   out_5219362633347118737[65] = 0;
   out_5219362633347118737[66] = dt;
   out_5219362633347118737[67] = 0;
   out_5219362633347118737[68] = 0;
   out_5219362633347118737[69] = 0;
   out_5219362633347118737[70] = 0;
   out_5219362633347118737[71] = 0;
   out_5219362633347118737[72] = 0;
   out_5219362633347118737[73] = 0;
   out_5219362633347118737[74] = 0;
   out_5219362633347118737[75] = 0;
   out_5219362633347118737[76] = 1;
   out_5219362633347118737[77] = 0;
   out_5219362633347118737[78] = 0;
   out_5219362633347118737[79] = 0;
   out_5219362633347118737[80] = 0;
   out_5219362633347118737[81] = 0;
   out_5219362633347118737[82] = 0;
   out_5219362633347118737[83] = 0;
   out_5219362633347118737[84] = 0;
   out_5219362633347118737[85] = dt;
   out_5219362633347118737[86] = 0;
   out_5219362633347118737[87] = 0;
   out_5219362633347118737[88] = 0;
   out_5219362633347118737[89] = 0;
   out_5219362633347118737[90] = 0;
   out_5219362633347118737[91] = 0;
   out_5219362633347118737[92] = 0;
   out_5219362633347118737[93] = 0;
   out_5219362633347118737[94] = 0;
   out_5219362633347118737[95] = 1;
   out_5219362633347118737[96] = 0;
   out_5219362633347118737[97] = 0;
   out_5219362633347118737[98] = 0;
   out_5219362633347118737[99] = 0;
   out_5219362633347118737[100] = 0;
   out_5219362633347118737[101] = 0;
   out_5219362633347118737[102] = 0;
   out_5219362633347118737[103] = 0;
   out_5219362633347118737[104] = dt;
   out_5219362633347118737[105] = 0;
   out_5219362633347118737[106] = 0;
   out_5219362633347118737[107] = 0;
   out_5219362633347118737[108] = 0;
   out_5219362633347118737[109] = 0;
   out_5219362633347118737[110] = 0;
   out_5219362633347118737[111] = 0;
   out_5219362633347118737[112] = 0;
   out_5219362633347118737[113] = 0;
   out_5219362633347118737[114] = 1;
   out_5219362633347118737[115] = 0;
   out_5219362633347118737[116] = 0;
   out_5219362633347118737[117] = 0;
   out_5219362633347118737[118] = 0;
   out_5219362633347118737[119] = 0;
   out_5219362633347118737[120] = 0;
   out_5219362633347118737[121] = 0;
   out_5219362633347118737[122] = 0;
   out_5219362633347118737[123] = 0;
   out_5219362633347118737[124] = 0;
   out_5219362633347118737[125] = 0;
   out_5219362633347118737[126] = 0;
   out_5219362633347118737[127] = 0;
   out_5219362633347118737[128] = 0;
   out_5219362633347118737[129] = 0;
   out_5219362633347118737[130] = 0;
   out_5219362633347118737[131] = 0;
   out_5219362633347118737[132] = 0;
   out_5219362633347118737[133] = 1;
   out_5219362633347118737[134] = 0;
   out_5219362633347118737[135] = 0;
   out_5219362633347118737[136] = 0;
   out_5219362633347118737[137] = 0;
   out_5219362633347118737[138] = 0;
   out_5219362633347118737[139] = 0;
   out_5219362633347118737[140] = 0;
   out_5219362633347118737[141] = 0;
   out_5219362633347118737[142] = 0;
   out_5219362633347118737[143] = 0;
   out_5219362633347118737[144] = 0;
   out_5219362633347118737[145] = 0;
   out_5219362633347118737[146] = 0;
   out_5219362633347118737[147] = 0;
   out_5219362633347118737[148] = 0;
   out_5219362633347118737[149] = 0;
   out_5219362633347118737[150] = 0;
   out_5219362633347118737[151] = 0;
   out_5219362633347118737[152] = 1;
   out_5219362633347118737[153] = 0;
   out_5219362633347118737[154] = 0;
   out_5219362633347118737[155] = 0;
   out_5219362633347118737[156] = 0;
   out_5219362633347118737[157] = 0;
   out_5219362633347118737[158] = 0;
   out_5219362633347118737[159] = 0;
   out_5219362633347118737[160] = 0;
   out_5219362633347118737[161] = 0;
   out_5219362633347118737[162] = 0;
   out_5219362633347118737[163] = 0;
   out_5219362633347118737[164] = 0;
   out_5219362633347118737[165] = 0;
   out_5219362633347118737[166] = 0;
   out_5219362633347118737[167] = 0;
   out_5219362633347118737[168] = 0;
   out_5219362633347118737[169] = 0;
   out_5219362633347118737[170] = 0;
   out_5219362633347118737[171] = 1;
   out_5219362633347118737[172] = 0;
   out_5219362633347118737[173] = 0;
   out_5219362633347118737[174] = 0;
   out_5219362633347118737[175] = 0;
   out_5219362633347118737[176] = 0;
   out_5219362633347118737[177] = 0;
   out_5219362633347118737[178] = 0;
   out_5219362633347118737[179] = 0;
   out_5219362633347118737[180] = 0;
   out_5219362633347118737[181] = 0;
   out_5219362633347118737[182] = 0;
   out_5219362633347118737[183] = 0;
   out_5219362633347118737[184] = 0;
   out_5219362633347118737[185] = 0;
   out_5219362633347118737[186] = 0;
   out_5219362633347118737[187] = 0;
   out_5219362633347118737[188] = 0;
   out_5219362633347118737[189] = 0;
   out_5219362633347118737[190] = 1;
   out_5219362633347118737[191] = 0;
   out_5219362633347118737[192] = 0;
   out_5219362633347118737[193] = 0;
   out_5219362633347118737[194] = 0;
   out_5219362633347118737[195] = 0;
   out_5219362633347118737[196] = 0;
   out_5219362633347118737[197] = 0;
   out_5219362633347118737[198] = 0;
   out_5219362633347118737[199] = 0;
   out_5219362633347118737[200] = 0;
   out_5219362633347118737[201] = 0;
   out_5219362633347118737[202] = 0;
   out_5219362633347118737[203] = 0;
   out_5219362633347118737[204] = 0;
   out_5219362633347118737[205] = 0;
   out_5219362633347118737[206] = 0;
   out_5219362633347118737[207] = 0;
   out_5219362633347118737[208] = 0;
   out_5219362633347118737[209] = 1;
   out_5219362633347118737[210] = 0;
   out_5219362633347118737[211] = 0;
   out_5219362633347118737[212] = 0;
   out_5219362633347118737[213] = 0;
   out_5219362633347118737[214] = 0;
   out_5219362633347118737[215] = 0;
   out_5219362633347118737[216] = 0;
   out_5219362633347118737[217] = 0;
   out_5219362633347118737[218] = 0;
   out_5219362633347118737[219] = 0;
   out_5219362633347118737[220] = 0;
   out_5219362633347118737[221] = 0;
   out_5219362633347118737[222] = 0;
   out_5219362633347118737[223] = 0;
   out_5219362633347118737[224] = 0;
   out_5219362633347118737[225] = 0;
   out_5219362633347118737[226] = 0;
   out_5219362633347118737[227] = 0;
   out_5219362633347118737[228] = 1;
   out_5219362633347118737[229] = 0;
   out_5219362633347118737[230] = 0;
   out_5219362633347118737[231] = 0;
   out_5219362633347118737[232] = 0;
   out_5219362633347118737[233] = 0;
   out_5219362633347118737[234] = 0;
   out_5219362633347118737[235] = 0;
   out_5219362633347118737[236] = 0;
   out_5219362633347118737[237] = 0;
   out_5219362633347118737[238] = 0;
   out_5219362633347118737[239] = 0;
   out_5219362633347118737[240] = 0;
   out_5219362633347118737[241] = 0;
   out_5219362633347118737[242] = 0;
   out_5219362633347118737[243] = 0;
   out_5219362633347118737[244] = 0;
   out_5219362633347118737[245] = 0;
   out_5219362633347118737[246] = 0;
   out_5219362633347118737[247] = 1;
   out_5219362633347118737[248] = 0;
   out_5219362633347118737[249] = 0;
   out_5219362633347118737[250] = 0;
   out_5219362633347118737[251] = 0;
   out_5219362633347118737[252] = 0;
   out_5219362633347118737[253] = 0;
   out_5219362633347118737[254] = 0;
   out_5219362633347118737[255] = 0;
   out_5219362633347118737[256] = 0;
   out_5219362633347118737[257] = 0;
   out_5219362633347118737[258] = 0;
   out_5219362633347118737[259] = 0;
   out_5219362633347118737[260] = 0;
   out_5219362633347118737[261] = 0;
   out_5219362633347118737[262] = 0;
   out_5219362633347118737[263] = 0;
   out_5219362633347118737[264] = 0;
   out_5219362633347118737[265] = 0;
   out_5219362633347118737[266] = 1;
   out_5219362633347118737[267] = 0;
   out_5219362633347118737[268] = 0;
   out_5219362633347118737[269] = 0;
   out_5219362633347118737[270] = 0;
   out_5219362633347118737[271] = 0;
   out_5219362633347118737[272] = 0;
   out_5219362633347118737[273] = 0;
   out_5219362633347118737[274] = 0;
   out_5219362633347118737[275] = 0;
   out_5219362633347118737[276] = 0;
   out_5219362633347118737[277] = 0;
   out_5219362633347118737[278] = 0;
   out_5219362633347118737[279] = 0;
   out_5219362633347118737[280] = 0;
   out_5219362633347118737[281] = 0;
   out_5219362633347118737[282] = 0;
   out_5219362633347118737[283] = 0;
   out_5219362633347118737[284] = 0;
   out_5219362633347118737[285] = 1;
   out_5219362633347118737[286] = 0;
   out_5219362633347118737[287] = 0;
   out_5219362633347118737[288] = 0;
   out_5219362633347118737[289] = 0;
   out_5219362633347118737[290] = 0;
   out_5219362633347118737[291] = 0;
   out_5219362633347118737[292] = 0;
   out_5219362633347118737[293] = 0;
   out_5219362633347118737[294] = 0;
   out_5219362633347118737[295] = 0;
   out_5219362633347118737[296] = 0;
   out_5219362633347118737[297] = 0;
   out_5219362633347118737[298] = 0;
   out_5219362633347118737[299] = 0;
   out_5219362633347118737[300] = 0;
   out_5219362633347118737[301] = 0;
   out_5219362633347118737[302] = 0;
   out_5219362633347118737[303] = 0;
   out_5219362633347118737[304] = 1;
   out_5219362633347118737[305] = 0;
   out_5219362633347118737[306] = 0;
   out_5219362633347118737[307] = 0;
   out_5219362633347118737[308] = 0;
   out_5219362633347118737[309] = 0;
   out_5219362633347118737[310] = 0;
   out_5219362633347118737[311] = 0;
   out_5219362633347118737[312] = 0;
   out_5219362633347118737[313] = 0;
   out_5219362633347118737[314] = 0;
   out_5219362633347118737[315] = 0;
   out_5219362633347118737[316] = 0;
   out_5219362633347118737[317] = 0;
   out_5219362633347118737[318] = 0;
   out_5219362633347118737[319] = 0;
   out_5219362633347118737[320] = 0;
   out_5219362633347118737[321] = 0;
   out_5219362633347118737[322] = 0;
   out_5219362633347118737[323] = 1;
}
void h_4(double *state, double *unused, double *out_7519118996374711979) {
   out_7519118996374711979[0] = state[6] + state[9];
   out_7519118996374711979[1] = state[7] + state[10];
   out_7519118996374711979[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_8313305288975318800) {
   out_8313305288975318800[0] = 0;
   out_8313305288975318800[1] = 0;
   out_8313305288975318800[2] = 0;
   out_8313305288975318800[3] = 0;
   out_8313305288975318800[4] = 0;
   out_8313305288975318800[5] = 0;
   out_8313305288975318800[6] = 1;
   out_8313305288975318800[7] = 0;
   out_8313305288975318800[8] = 0;
   out_8313305288975318800[9] = 1;
   out_8313305288975318800[10] = 0;
   out_8313305288975318800[11] = 0;
   out_8313305288975318800[12] = 0;
   out_8313305288975318800[13] = 0;
   out_8313305288975318800[14] = 0;
   out_8313305288975318800[15] = 0;
   out_8313305288975318800[16] = 0;
   out_8313305288975318800[17] = 0;
   out_8313305288975318800[18] = 0;
   out_8313305288975318800[19] = 0;
   out_8313305288975318800[20] = 0;
   out_8313305288975318800[21] = 0;
   out_8313305288975318800[22] = 0;
   out_8313305288975318800[23] = 0;
   out_8313305288975318800[24] = 0;
   out_8313305288975318800[25] = 1;
   out_8313305288975318800[26] = 0;
   out_8313305288975318800[27] = 0;
   out_8313305288975318800[28] = 1;
   out_8313305288975318800[29] = 0;
   out_8313305288975318800[30] = 0;
   out_8313305288975318800[31] = 0;
   out_8313305288975318800[32] = 0;
   out_8313305288975318800[33] = 0;
   out_8313305288975318800[34] = 0;
   out_8313305288975318800[35] = 0;
   out_8313305288975318800[36] = 0;
   out_8313305288975318800[37] = 0;
   out_8313305288975318800[38] = 0;
   out_8313305288975318800[39] = 0;
   out_8313305288975318800[40] = 0;
   out_8313305288975318800[41] = 0;
   out_8313305288975318800[42] = 0;
   out_8313305288975318800[43] = 0;
   out_8313305288975318800[44] = 1;
   out_8313305288975318800[45] = 0;
   out_8313305288975318800[46] = 0;
   out_8313305288975318800[47] = 1;
   out_8313305288975318800[48] = 0;
   out_8313305288975318800[49] = 0;
   out_8313305288975318800[50] = 0;
   out_8313305288975318800[51] = 0;
   out_8313305288975318800[52] = 0;
   out_8313305288975318800[53] = 0;
}
void h_10(double *state, double *unused, double *out_6206587983423265688) {
   out_6206587983423265688[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_6206587983423265688[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_6206587983423265688[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_2459625458239534432) {
   out_2459625458239534432[0] = 0;
   out_2459625458239534432[1] = 9.8100000000000005*cos(state[1]);
   out_2459625458239534432[2] = 0;
   out_2459625458239534432[3] = 0;
   out_2459625458239534432[4] = -state[8];
   out_2459625458239534432[5] = state[7];
   out_2459625458239534432[6] = 0;
   out_2459625458239534432[7] = state[5];
   out_2459625458239534432[8] = -state[4];
   out_2459625458239534432[9] = 0;
   out_2459625458239534432[10] = 0;
   out_2459625458239534432[11] = 0;
   out_2459625458239534432[12] = 1;
   out_2459625458239534432[13] = 0;
   out_2459625458239534432[14] = 0;
   out_2459625458239534432[15] = 1;
   out_2459625458239534432[16] = 0;
   out_2459625458239534432[17] = 0;
   out_2459625458239534432[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_2459625458239534432[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_2459625458239534432[20] = 0;
   out_2459625458239534432[21] = state[8];
   out_2459625458239534432[22] = 0;
   out_2459625458239534432[23] = -state[6];
   out_2459625458239534432[24] = -state[5];
   out_2459625458239534432[25] = 0;
   out_2459625458239534432[26] = state[3];
   out_2459625458239534432[27] = 0;
   out_2459625458239534432[28] = 0;
   out_2459625458239534432[29] = 0;
   out_2459625458239534432[30] = 0;
   out_2459625458239534432[31] = 1;
   out_2459625458239534432[32] = 0;
   out_2459625458239534432[33] = 0;
   out_2459625458239534432[34] = 1;
   out_2459625458239534432[35] = 0;
   out_2459625458239534432[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_2459625458239534432[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_2459625458239534432[38] = 0;
   out_2459625458239534432[39] = -state[7];
   out_2459625458239534432[40] = state[6];
   out_2459625458239534432[41] = 0;
   out_2459625458239534432[42] = state[4];
   out_2459625458239534432[43] = -state[3];
   out_2459625458239534432[44] = 0;
   out_2459625458239534432[45] = 0;
   out_2459625458239534432[46] = 0;
   out_2459625458239534432[47] = 0;
   out_2459625458239534432[48] = 0;
   out_2459625458239534432[49] = 0;
   out_2459625458239534432[50] = 1;
   out_2459625458239534432[51] = 0;
   out_2459625458239534432[52] = 0;
   out_2459625458239534432[53] = 1;
}
void h_13(double *state, double *unused, double *out_6892691385862434963) {
   out_6892691385862434963[0] = state[3];
   out_6892691385862434963[1] = state[4];
   out_6892691385862434963[2] = state[5];
}
void H_13(double *state, double *unused, double *out_6921164959401900015) {
   out_6921164959401900015[0] = 0;
   out_6921164959401900015[1] = 0;
   out_6921164959401900015[2] = 0;
   out_6921164959401900015[3] = 1;
   out_6921164959401900015[4] = 0;
   out_6921164959401900015[5] = 0;
   out_6921164959401900015[6] = 0;
   out_6921164959401900015[7] = 0;
   out_6921164959401900015[8] = 0;
   out_6921164959401900015[9] = 0;
   out_6921164959401900015[10] = 0;
   out_6921164959401900015[11] = 0;
   out_6921164959401900015[12] = 0;
   out_6921164959401900015[13] = 0;
   out_6921164959401900015[14] = 0;
   out_6921164959401900015[15] = 0;
   out_6921164959401900015[16] = 0;
   out_6921164959401900015[17] = 0;
   out_6921164959401900015[18] = 0;
   out_6921164959401900015[19] = 0;
   out_6921164959401900015[20] = 0;
   out_6921164959401900015[21] = 0;
   out_6921164959401900015[22] = 1;
   out_6921164959401900015[23] = 0;
   out_6921164959401900015[24] = 0;
   out_6921164959401900015[25] = 0;
   out_6921164959401900015[26] = 0;
   out_6921164959401900015[27] = 0;
   out_6921164959401900015[28] = 0;
   out_6921164959401900015[29] = 0;
   out_6921164959401900015[30] = 0;
   out_6921164959401900015[31] = 0;
   out_6921164959401900015[32] = 0;
   out_6921164959401900015[33] = 0;
   out_6921164959401900015[34] = 0;
   out_6921164959401900015[35] = 0;
   out_6921164959401900015[36] = 0;
   out_6921164959401900015[37] = 0;
   out_6921164959401900015[38] = 0;
   out_6921164959401900015[39] = 0;
   out_6921164959401900015[40] = 0;
   out_6921164959401900015[41] = 1;
   out_6921164959401900015[42] = 0;
   out_6921164959401900015[43] = 0;
   out_6921164959401900015[44] = 0;
   out_6921164959401900015[45] = 0;
   out_6921164959401900015[46] = 0;
   out_6921164959401900015[47] = 0;
   out_6921164959401900015[48] = 0;
   out_6921164959401900015[49] = 0;
   out_6921164959401900015[50] = 0;
   out_6921164959401900015[51] = 0;
   out_6921164959401900015[52] = 0;
   out_6921164959401900015[53] = 0;
}
void h_14(double *state, double *unused, double *out_7370507100637914212) {
   out_7370507100637914212[0] = state[6];
   out_7370507100637914212[1] = state[7];
   out_7370507100637914212[2] = state[8];
}
void H_14(double *state, double *unused, double *out_6170197928394748287) {
   out_6170197928394748287[0] = 0;
   out_6170197928394748287[1] = 0;
   out_6170197928394748287[2] = 0;
   out_6170197928394748287[3] = 0;
   out_6170197928394748287[4] = 0;
   out_6170197928394748287[5] = 0;
   out_6170197928394748287[6] = 1;
   out_6170197928394748287[7] = 0;
   out_6170197928394748287[8] = 0;
   out_6170197928394748287[9] = 0;
   out_6170197928394748287[10] = 0;
   out_6170197928394748287[11] = 0;
   out_6170197928394748287[12] = 0;
   out_6170197928394748287[13] = 0;
   out_6170197928394748287[14] = 0;
   out_6170197928394748287[15] = 0;
   out_6170197928394748287[16] = 0;
   out_6170197928394748287[17] = 0;
   out_6170197928394748287[18] = 0;
   out_6170197928394748287[19] = 0;
   out_6170197928394748287[20] = 0;
   out_6170197928394748287[21] = 0;
   out_6170197928394748287[22] = 0;
   out_6170197928394748287[23] = 0;
   out_6170197928394748287[24] = 0;
   out_6170197928394748287[25] = 1;
   out_6170197928394748287[26] = 0;
   out_6170197928394748287[27] = 0;
   out_6170197928394748287[28] = 0;
   out_6170197928394748287[29] = 0;
   out_6170197928394748287[30] = 0;
   out_6170197928394748287[31] = 0;
   out_6170197928394748287[32] = 0;
   out_6170197928394748287[33] = 0;
   out_6170197928394748287[34] = 0;
   out_6170197928394748287[35] = 0;
   out_6170197928394748287[36] = 0;
   out_6170197928394748287[37] = 0;
   out_6170197928394748287[38] = 0;
   out_6170197928394748287[39] = 0;
   out_6170197928394748287[40] = 0;
   out_6170197928394748287[41] = 0;
   out_6170197928394748287[42] = 0;
   out_6170197928394748287[43] = 0;
   out_6170197928394748287[44] = 1;
   out_6170197928394748287[45] = 0;
   out_6170197928394748287[46] = 0;
   out_6170197928394748287[47] = 0;
   out_6170197928394748287[48] = 0;
   out_6170197928394748287[49] = 0;
   out_6170197928394748287[50] = 0;
   out_6170197928394748287[51] = 0;
   out_6170197928394748287[52] = 0;
   out_6170197928394748287[53] = 0;
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
void pose_err_fun(double *nom_x, double *delta_x, double *out_6822829480064316427) {
  err_fun(nom_x, delta_x, out_6822829480064316427);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_8351755903623348291) {
  inv_err_fun(nom_x, true_x, out_8351755903623348291);
}
void pose_H_mod_fun(double *state, double *out_3160786903936238065) {
  H_mod_fun(state, out_3160786903936238065);
}
void pose_f_fun(double *state, double dt, double *out_3649248979314528992) {
  f_fun(state,  dt, out_3649248979314528992);
}
void pose_F_fun(double *state, double dt, double *out_5219362633347118737) {
  F_fun(state,  dt, out_5219362633347118737);
}
void pose_h_4(double *state, double *unused, double *out_7519118996374711979) {
  h_4(state, unused, out_7519118996374711979);
}
void pose_H_4(double *state, double *unused, double *out_8313305288975318800) {
  H_4(state, unused, out_8313305288975318800);
}
void pose_h_10(double *state, double *unused, double *out_6206587983423265688) {
  h_10(state, unused, out_6206587983423265688);
}
void pose_H_10(double *state, double *unused, double *out_2459625458239534432) {
  H_10(state, unused, out_2459625458239534432);
}
void pose_h_13(double *state, double *unused, double *out_6892691385862434963) {
  h_13(state, unused, out_6892691385862434963);
}
void pose_H_13(double *state, double *unused, double *out_6921164959401900015) {
  H_13(state, unused, out_6921164959401900015);
}
void pose_h_14(double *state, double *unused, double *out_7370507100637914212) {
  h_14(state, unused, out_7370507100637914212);
}
void pose_H_14(double *state, double *unused, double *out_6170197928394748287) {
  H_14(state, unused, out_6170197928394748287);
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
