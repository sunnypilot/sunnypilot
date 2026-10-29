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
void err_fun(double *nom_x, double *delta_x, double *out_5308991872147398563) {
   out_5308991872147398563[0] = delta_x[0] + nom_x[0];
   out_5308991872147398563[1] = delta_x[1] + nom_x[1];
   out_5308991872147398563[2] = delta_x[2] + nom_x[2];
   out_5308991872147398563[3] = delta_x[3] + nom_x[3];
   out_5308991872147398563[4] = delta_x[4] + nom_x[4];
   out_5308991872147398563[5] = delta_x[5] + nom_x[5];
   out_5308991872147398563[6] = delta_x[6] + nom_x[6];
   out_5308991872147398563[7] = delta_x[7] + nom_x[7];
   out_5308991872147398563[8] = delta_x[8] + nom_x[8];
   out_5308991872147398563[9] = delta_x[9] + nom_x[9];
   out_5308991872147398563[10] = delta_x[10] + nom_x[10];
   out_5308991872147398563[11] = delta_x[11] + nom_x[11];
   out_5308991872147398563[12] = delta_x[12] + nom_x[12];
   out_5308991872147398563[13] = delta_x[13] + nom_x[13];
   out_5308991872147398563[14] = delta_x[14] + nom_x[14];
   out_5308991872147398563[15] = delta_x[15] + nom_x[15];
   out_5308991872147398563[16] = delta_x[16] + nom_x[16];
   out_5308991872147398563[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_5440750294658648606) {
   out_5440750294658648606[0] = -nom_x[0] + true_x[0];
   out_5440750294658648606[1] = -nom_x[1] + true_x[1];
   out_5440750294658648606[2] = -nom_x[2] + true_x[2];
   out_5440750294658648606[3] = -nom_x[3] + true_x[3];
   out_5440750294658648606[4] = -nom_x[4] + true_x[4];
   out_5440750294658648606[5] = -nom_x[5] + true_x[5];
   out_5440750294658648606[6] = -nom_x[6] + true_x[6];
   out_5440750294658648606[7] = -nom_x[7] + true_x[7];
   out_5440750294658648606[8] = -nom_x[8] + true_x[8];
   out_5440750294658648606[9] = -nom_x[9] + true_x[9];
   out_5440750294658648606[10] = -nom_x[10] + true_x[10];
   out_5440750294658648606[11] = -nom_x[11] + true_x[11];
   out_5440750294658648606[12] = -nom_x[12] + true_x[12];
   out_5440750294658648606[13] = -nom_x[13] + true_x[13];
   out_5440750294658648606[14] = -nom_x[14] + true_x[14];
   out_5440750294658648606[15] = -nom_x[15] + true_x[15];
   out_5440750294658648606[16] = -nom_x[16] + true_x[16];
   out_5440750294658648606[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_7655853576405724458) {
   out_7655853576405724458[0] = 1.0;
   out_7655853576405724458[1] = 0.0;
   out_7655853576405724458[2] = 0.0;
   out_7655853576405724458[3] = 0.0;
   out_7655853576405724458[4] = 0.0;
   out_7655853576405724458[5] = 0.0;
   out_7655853576405724458[6] = 0.0;
   out_7655853576405724458[7] = 0.0;
   out_7655853576405724458[8] = 0.0;
   out_7655853576405724458[9] = 0.0;
   out_7655853576405724458[10] = 0.0;
   out_7655853576405724458[11] = 0.0;
   out_7655853576405724458[12] = 0.0;
   out_7655853576405724458[13] = 0.0;
   out_7655853576405724458[14] = 0.0;
   out_7655853576405724458[15] = 0.0;
   out_7655853576405724458[16] = 0.0;
   out_7655853576405724458[17] = 0.0;
   out_7655853576405724458[18] = 0.0;
   out_7655853576405724458[19] = 1.0;
   out_7655853576405724458[20] = 0.0;
   out_7655853576405724458[21] = 0.0;
   out_7655853576405724458[22] = 0.0;
   out_7655853576405724458[23] = 0.0;
   out_7655853576405724458[24] = 0.0;
   out_7655853576405724458[25] = 0.0;
   out_7655853576405724458[26] = 0.0;
   out_7655853576405724458[27] = 0.0;
   out_7655853576405724458[28] = 0.0;
   out_7655853576405724458[29] = 0.0;
   out_7655853576405724458[30] = 0.0;
   out_7655853576405724458[31] = 0.0;
   out_7655853576405724458[32] = 0.0;
   out_7655853576405724458[33] = 0.0;
   out_7655853576405724458[34] = 0.0;
   out_7655853576405724458[35] = 0.0;
   out_7655853576405724458[36] = 0.0;
   out_7655853576405724458[37] = 0.0;
   out_7655853576405724458[38] = 1.0;
   out_7655853576405724458[39] = 0.0;
   out_7655853576405724458[40] = 0.0;
   out_7655853576405724458[41] = 0.0;
   out_7655853576405724458[42] = 0.0;
   out_7655853576405724458[43] = 0.0;
   out_7655853576405724458[44] = 0.0;
   out_7655853576405724458[45] = 0.0;
   out_7655853576405724458[46] = 0.0;
   out_7655853576405724458[47] = 0.0;
   out_7655853576405724458[48] = 0.0;
   out_7655853576405724458[49] = 0.0;
   out_7655853576405724458[50] = 0.0;
   out_7655853576405724458[51] = 0.0;
   out_7655853576405724458[52] = 0.0;
   out_7655853576405724458[53] = 0.0;
   out_7655853576405724458[54] = 0.0;
   out_7655853576405724458[55] = 0.0;
   out_7655853576405724458[56] = 0.0;
   out_7655853576405724458[57] = 1.0;
   out_7655853576405724458[58] = 0.0;
   out_7655853576405724458[59] = 0.0;
   out_7655853576405724458[60] = 0.0;
   out_7655853576405724458[61] = 0.0;
   out_7655853576405724458[62] = 0.0;
   out_7655853576405724458[63] = 0.0;
   out_7655853576405724458[64] = 0.0;
   out_7655853576405724458[65] = 0.0;
   out_7655853576405724458[66] = 0.0;
   out_7655853576405724458[67] = 0.0;
   out_7655853576405724458[68] = 0.0;
   out_7655853576405724458[69] = 0.0;
   out_7655853576405724458[70] = 0.0;
   out_7655853576405724458[71] = 0.0;
   out_7655853576405724458[72] = 0.0;
   out_7655853576405724458[73] = 0.0;
   out_7655853576405724458[74] = 0.0;
   out_7655853576405724458[75] = 0.0;
   out_7655853576405724458[76] = 1.0;
   out_7655853576405724458[77] = 0.0;
   out_7655853576405724458[78] = 0.0;
   out_7655853576405724458[79] = 0.0;
   out_7655853576405724458[80] = 0.0;
   out_7655853576405724458[81] = 0.0;
   out_7655853576405724458[82] = 0.0;
   out_7655853576405724458[83] = 0.0;
   out_7655853576405724458[84] = 0.0;
   out_7655853576405724458[85] = 0.0;
   out_7655853576405724458[86] = 0.0;
   out_7655853576405724458[87] = 0.0;
   out_7655853576405724458[88] = 0.0;
   out_7655853576405724458[89] = 0.0;
   out_7655853576405724458[90] = 0.0;
   out_7655853576405724458[91] = 0.0;
   out_7655853576405724458[92] = 0.0;
   out_7655853576405724458[93] = 0.0;
   out_7655853576405724458[94] = 0.0;
   out_7655853576405724458[95] = 1.0;
   out_7655853576405724458[96] = 0.0;
   out_7655853576405724458[97] = 0.0;
   out_7655853576405724458[98] = 0.0;
   out_7655853576405724458[99] = 0.0;
   out_7655853576405724458[100] = 0.0;
   out_7655853576405724458[101] = 0.0;
   out_7655853576405724458[102] = 0.0;
   out_7655853576405724458[103] = 0.0;
   out_7655853576405724458[104] = 0.0;
   out_7655853576405724458[105] = 0.0;
   out_7655853576405724458[106] = 0.0;
   out_7655853576405724458[107] = 0.0;
   out_7655853576405724458[108] = 0.0;
   out_7655853576405724458[109] = 0.0;
   out_7655853576405724458[110] = 0.0;
   out_7655853576405724458[111] = 0.0;
   out_7655853576405724458[112] = 0.0;
   out_7655853576405724458[113] = 0.0;
   out_7655853576405724458[114] = 1.0;
   out_7655853576405724458[115] = 0.0;
   out_7655853576405724458[116] = 0.0;
   out_7655853576405724458[117] = 0.0;
   out_7655853576405724458[118] = 0.0;
   out_7655853576405724458[119] = 0.0;
   out_7655853576405724458[120] = 0.0;
   out_7655853576405724458[121] = 0.0;
   out_7655853576405724458[122] = 0.0;
   out_7655853576405724458[123] = 0.0;
   out_7655853576405724458[124] = 0.0;
   out_7655853576405724458[125] = 0.0;
   out_7655853576405724458[126] = 0.0;
   out_7655853576405724458[127] = 0.0;
   out_7655853576405724458[128] = 0.0;
   out_7655853576405724458[129] = 0.0;
   out_7655853576405724458[130] = 0.0;
   out_7655853576405724458[131] = 0.0;
   out_7655853576405724458[132] = 0.0;
   out_7655853576405724458[133] = 1.0;
   out_7655853576405724458[134] = 0.0;
   out_7655853576405724458[135] = 0.0;
   out_7655853576405724458[136] = 0.0;
   out_7655853576405724458[137] = 0.0;
   out_7655853576405724458[138] = 0.0;
   out_7655853576405724458[139] = 0.0;
   out_7655853576405724458[140] = 0.0;
   out_7655853576405724458[141] = 0.0;
   out_7655853576405724458[142] = 0.0;
   out_7655853576405724458[143] = 0.0;
   out_7655853576405724458[144] = 0.0;
   out_7655853576405724458[145] = 0.0;
   out_7655853576405724458[146] = 0.0;
   out_7655853576405724458[147] = 0.0;
   out_7655853576405724458[148] = 0.0;
   out_7655853576405724458[149] = 0.0;
   out_7655853576405724458[150] = 0.0;
   out_7655853576405724458[151] = 0.0;
   out_7655853576405724458[152] = 1.0;
   out_7655853576405724458[153] = 0.0;
   out_7655853576405724458[154] = 0.0;
   out_7655853576405724458[155] = 0.0;
   out_7655853576405724458[156] = 0.0;
   out_7655853576405724458[157] = 0.0;
   out_7655853576405724458[158] = 0.0;
   out_7655853576405724458[159] = 0.0;
   out_7655853576405724458[160] = 0.0;
   out_7655853576405724458[161] = 0.0;
   out_7655853576405724458[162] = 0.0;
   out_7655853576405724458[163] = 0.0;
   out_7655853576405724458[164] = 0.0;
   out_7655853576405724458[165] = 0.0;
   out_7655853576405724458[166] = 0.0;
   out_7655853576405724458[167] = 0.0;
   out_7655853576405724458[168] = 0.0;
   out_7655853576405724458[169] = 0.0;
   out_7655853576405724458[170] = 0.0;
   out_7655853576405724458[171] = 1.0;
   out_7655853576405724458[172] = 0.0;
   out_7655853576405724458[173] = 0.0;
   out_7655853576405724458[174] = 0.0;
   out_7655853576405724458[175] = 0.0;
   out_7655853576405724458[176] = 0.0;
   out_7655853576405724458[177] = 0.0;
   out_7655853576405724458[178] = 0.0;
   out_7655853576405724458[179] = 0.0;
   out_7655853576405724458[180] = 0.0;
   out_7655853576405724458[181] = 0.0;
   out_7655853576405724458[182] = 0.0;
   out_7655853576405724458[183] = 0.0;
   out_7655853576405724458[184] = 0.0;
   out_7655853576405724458[185] = 0.0;
   out_7655853576405724458[186] = 0.0;
   out_7655853576405724458[187] = 0.0;
   out_7655853576405724458[188] = 0.0;
   out_7655853576405724458[189] = 0.0;
   out_7655853576405724458[190] = 1.0;
   out_7655853576405724458[191] = 0.0;
   out_7655853576405724458[192] = 0.0;
   out_7655853576405724458[193] = 0.0;
   out_7655853576405724458[194] = 0.0;
   out_7655853576405724458[195] = 0.0;
   out_7655853576405724458[196] = 0.0;
   out_7655853576405724458[197] = 0.0;
   out_7655853576405724458[198] = 0.0;
   out_7655853576405724458[199] = 0.0;
   out_7655853576405724458[200] = 0.0;
   out_7655853576405724458[201] = 0.0;
   out_7655853576405724458[202] = 0.0;
   out_7655853576405724458[203] = 0.0;
   out_7655853576405724458[204] = 0.0;
   out_7655853576405724458[205] = 0.0;
   out_7655853576405724458[206] = 0.0;
   out_7655853576405724458[207] = 0.0;
   out_7655853576405724458[208] = 0.0;
   out_7655853576405724458[209] = 1.0;
   out_7655853576405724458[210] = 0.0;
   out_7655853576405724458[211] = 0.0;
   out_7655853576405724458[212] = 0.0;
   out_7655853576405724458[213] = 0.0;
   out_7655853576405724458[214] = 0.0;
   out_7655853576405724458[215] = 0.0;
   out_7655853576405724458[216] = 0.0;
   out_7655853576405724458[217] = 0.0;
   out_7655853576405724458[218] = 0.0;
   out_7655853576405724458[219] = 0.0;
   out_7655853576405724458[220] = 0.0;
   out_7655853576405724458[221] = 0.0;
   out_7655853576405724458[222] = 0.0;
   out_7655853576405724458[223] = 0.0;
   out_7655853576405724458[224] = 0.0;
   out_7655853576405724458[225] = 0.0;
   out_7655853576405724458[226] = 0.0;
   out_7655853576405724458[227] = 0.0;
   out_7655853576405724458[228] = 1.0;
   out_7655853576405724458[229] = 0.0;
   out_7655853576405724458[230] = 0.0;
   out_7655853576405724458[231] = 0.0;
   out_7655853576405724458[232] = 0.0;
   out_7655853576405724458[233] = 0.0;
   out_7655853576405724458[234] = 0.0;
   out_7655853576405724458[235] = 0.0;
   out_7655853576405724458[236] = 0.0;
   out_7655853576405724458[237] = 0.0;
   out_7655853576405724458[238] = 0.0;
   out_7655853576405724458[239] = 0.0;
   out_7655853576405724458[240] = 0.0;
   out_7655853576405724458[241] = 0.0;
   out_7655853576405724458[242] = 0.0;
   out_7655853576405724458[243] = 0.0;
   out_7655853576405724458[244] = 0.0;
   out_7655853576405724458[245] = 0.0;
   out_7655853576405724458[246] = 0.0;
   out_7655853576405724458[247] = 1.0;
   out_7655853576405724458[248] = 0.0;
   out_7655853576405724458[249] = 0.0;
   out_7655853576405724458[250] = 0.0;
   out_7655853576405724458[251] = 0.0;
   out_7655853576405724458[252] = 0.0;
   out_7655853576405724458[253] = 0.0;
   out_7655853576405724458[254] = 0.0;
   out_7655853576405724458[255] = 0.0;
   out_7655853576405724458[256] = 0.0;
   out_7655853576405724458[257] = 0.0;
   out_7655853576405724458[258] = 0.0;
   out_7655853576405724458[259] = 0.0;
   out_7655853576405724458[260] = 0.0;
   out_7655853576405724458[261] = 0.0;
   out_7655853576405724458[262] = 0.0;
   out_7655853576405724458[263] = 0.0;
   out_7655853576405724458[264] = 0.0;
   out_7655853576405724458[265] = 0.0;
   out_7655853576405724458[266] = 1.0;
   out_7655853576405724458[267] = 0.0;
   out_7655853576405724458[268] = 0.0;
   out_7655853576405724458[269] = 0.0;
   out_7655853576405724458[270] = 0.0;
   out_7655853576405724458[271] = 0.0;
   out_7655853576405724458[272] = 0.0;
   out_7655853576405724458[273] = 0.0;
   out_7655853576405724458[274] = 0.0;
   out_7655853576405724458[275] = 0.0;
   out_7655853576405724458[276] = 0.0;
   out_7655853576405724458[277] = 0.0;
   out_7655853576405724458[278] = 0.0;
   out_7655853576405724458[279] = 0.0;
   out_7655853576405724458[280] = 0.0;
   out_7655853576405724458[281] = 0.0;
   out_7655853576405724458[282] = 0.0;
   out_7655853576405724458[283] = 0.0;
   out_7655853576405724458[284] = 0.0;
   out_7655853576405724458[285] = 1.0;
   out_7655853576405724458[286] = 0.0;
   out_7655853576405724458[287] = 0.0;
   out_7655853576405724458[288] = 0.0;
   out_7655853576405724458[289] = 0.0;
   out_7655853576405724458[290] = 0.0;
   out_7655853576405724458[291] = 0.0;
   out_7655853576405724458[292] = 0.0;
   out_7655853576405724458[293] = 0.0;
   out_7655853576405724458[294] = 0.0;
   out_7655853576405724458[295] = 0.0;
   out_7655853576405724458[296] = 0.0;
   out_7655853576405724458[297] = 0.0;
   out_7655853576405724458[298] = 0.0;
   out_7655853576405724458[299] = 0.0;
   out_7655853576405724458[300] = 0.0;
   out_7655853576405724458[301] = 0.0;
   out_7655853576405724458[302] = 0.0;
   out_7655853576405724458[303] = 0.0;
   out_7655853576405724458[304] = 1.0;
   out_7655853576405724458[305] = 0.0;
   out_7655853576405724458[306] = 0.0;
   out_7655853576405724458[307] = 0.0;
   out_7655853576405724458[308] = 0.0;
   out_7655853576405724458[309] = 0.0;
   out_7655853576405724458[310] = 0.0;
   out_7655853576405724458[311] = 0.0;
   out_7655853576405724458[312] = 0.0;
   out_7655853576405724458[313] = 0.0;
   out_7655853576405724458[314] = 0.0;
   out_7655853576405724458[315] = 0.0;
   out_7655853576405724458[316] = 0.0;
   out_7655853576405724458[317] = 0.0;
   out_7655853576405724458[318] = 0.0;
   out_7655853576405724458[319] = 0.0;
   out_7655853576405724458[320] = 0.0;
   out_7655853576405724458[321] = 0.0;
   out_7655853576405724458[322] = 0.0;
   out_7655853576405724458[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_4136808220434975141) {
   out_4136808220434975141[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_4136808220434975141[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_4136808220434975141[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_4136808220434975141[3] = dt*state[12] + state[3];
   out_4136808220434975141[4] = dt*state[13] + state[4];
   out_4136808220434975141[5] = dt*state[14] + state[5];
   out_4136808220434975141[6] = state[6];
   out_4136808220434975141[7] = state[7];
   out_4136808220434975141[8] = state[8];
   out_4136808220434975141[9] = state[9];
   out_4136808220434975141[10] = state[10];
   out_4136808220434975141[11] = state[11];
   out_4136808220434975141[12] = state[12];
   out_4136808220434975141[13] = state[13];
   out_4136808220434975141[14] = state[14];
   out_4136808220434975141[15] = state[15];
   out_4136808220434975141[16] = state[16];
   out_4136808220434975141[17] = state[17];
}
void F_fun(double *state, double dt, double *out_2537852680944861179) {
   out_2537852680944861179[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_2537852680944861179[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_2537852680944861179[2] = 0;
   out_2537852680944861179[3] = 0;
   out_2537852680944861179[4] = 0;
   out_2537852680944861179[5] = 0;
   out_2537852680944861179[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_2537852680944861179[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_2537852680944861179[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_2537852680944861179[9] = 0;
   out_2537852680944861179[10] = 0;
   out_2537852680944861179[11] = 0;
   out_2537852680944861179[12] = 0;
   out_2537852680944861179[13] = 0;
   out_2537852680944861179[14] = 0;
   out_2537852680944861179[15] = 0;
   out_2537852680944861179[16] = 0;
   out_2537852680944861179[17] = 0;
   out_2537852680944861179[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_2537852680944861179[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_2537852680944861179[20] = 0;
   out_2537852680944861179[21] = 0;
   out_2537852680944861179[22] = 0;
   out_2537852680944861179[23] = 0;
   out_2537852680944861179[24] = 0;
   out_2537852680944861179[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_2537852680944861179[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_2537852680944861179[27] = 0;
   out_2537852680944861179[28] = 0;
   out_2537852680944861179[29] = 0;
   out_2537852680944861179[30] = 0;
   out_2537852680944861179[31] = 0;
   out_2537852680944861179[32] = 0;
   out_2537852680944861179[33] = 0;
   out_2537852680944861179[34] = 0;
   out_2537852680944861179[35] = 0;
   out_2537852680944861179[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_2537852680944861179[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_2537852680944861179[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_2537852680944861179[39] = 0;
   out_2537852680944861179[40] = 0;
   out_2537852680944861179[41] = 0;
   out_2537852680944861179[42] = 0;
   out_2537852680944861179[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_2537852680944861179[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_2537852680944861179[45] = 0;
   out_2537852680944861179[46] = 0;
   out_2537852680944861179[47] = 0;
   out_2537852680944861179[48] = 0;
   out_2537852680944861179[49] = 0;
   out_2537852680944861179[50] = 0;
   out_2537852680944861179[51] = 0;
   out_2537852680944861179[52] = 0;
   out_2537852680944861179[53] = 0;
   out_2537852680944861179[54] = 0;
   out_2537852680944861179[55] = 0;
   out_2537852680944861179[56] = 0;
   out_2537852680944861179[57] = 1;
   out_2537852680944861179[58] = 0;
   out_2537852680944861179[59] = 0;
   out_2537852680944861179[60] = 0;
   out_2537852680944861179[61] = 0;
   out_2537852680944861179[62] = 0;
   out_2537852680944861179[63] = 0;
   out_2537852680944861179[64] = 0;
   out_2537852680944861179[65] = 0;
   out_2537852680944861179[66] = dt;
   out_2537852680944861179[67] = 0;
   out_2537852680944861179[68] = 0;
   out_2537852680944861179[69] = 0;
   out_2537852680944861179[70] = 0;
   out_2537852680944861179[71] = 0;
   out_2537852680944861179[72] = 0;
   out_2537852680944861179[73] = 0;
   out_2537852680944861179[74] = 0;
   out_2537852680944861179[75] = 0;
   out_2537852680944861179[76] = 1;
   out_2537852680944861179[77] = 0;
   out_2537852680944861179[78] = 0;
   out_2537852680944861179[79] = 0;
   out_2537852680944861179[80] = 0;
   out_2537852680944861179[81] = 0;
   out_2537852680944861179[82] = 0;
   out_2537852680944861179[83] = 0;
   out_2537852680944861179[84] = 0;
   out_2537852680944861179[85] = dt;
   out_2537852680944861179[86] = 0;
   out_2537852680944861179[87] = 0;
   out_2537852680944861179[88] = 0;
   out_2537852680944861179[89] = 0;
   out_2537852680944861179[90] = 0;
   out_2537852680944861179[91] = 0;
   out_2537852680944861179[92] = 0;
   out_2537852680944861179[93] = 0;
   out_2537852680944861179[94] = 0;
   out_2537852680944861179[95] = 1;
   out_2537852680944861179[96] = 0;
   out_2537852680944861179[97] = 0;
   out_2537852680944861179[98] = 0;
   out_2537852680944861179[99] = 0;
   out_2537852680944861179[100] = 0;
   out_2537852680944861179[101] = 0;
   out_2537852680944861179[102] = 0;
   out_2537852680944861179[103] = 0;
   out_2537852680944861179[104] = dt;
   out_2537852680944861179[105] = 0;
   out_2537852680944861179[106] = 0;
   out_2537852680944861179[107] = 0;
   out_2537852680944861179[108] = 0;
   out_2537852680944861179[109] = 0;
   out_2537852680944861179[110] = 0;
   out_2537852680944861179[111] = 0;
   out_2537852680944861179[112] = 0;
   out_2537852680944861179[113] = 0;
   out_2537852680944861179[114] = 1;
   out_2537852680944861179[115] = 0;
   out_2537852680944861179[116] = 0;
   out_2537852680944861179[117] = 0;
   out_2537852680944861179[118] = 0;
   out_2537852680944861179[119] = 0;
   out_2537852680944861179[120] = 0;
   out_2537852680944861179[121] = 0;
   out_2537852680944861179[122] = 0;
   out_2537852680944861179[123] = 0;
   out_2537852680944861179[124] = 0;
   out_2537852680944861179[125] = 0;
   out_2537852680944861179[126] = 0;
   out_2537852680944861179[127] = 0;
   out_2537852680944861179[128] = 0;
   out_2537852680944861179[129] = 0;
   out_2537852680944861179[130] = 0;
   out_2537852680944861179[131] = 0;
   out_2537852680944861179[132] = 0;
   out_2537852680944861179[133] = 1;
   out_2537852680944861179[134] = 0;
   out_2537852680944861179[135] = 0;
   out_2537852680944861179[136] = 0;
   out_2537852680944861179[137] = 0;
   out_2537852680944861179[138] = 0;
   out_2537852680944861179[139] = 0;
   out_2537852680944861179[140] = 0;
   out_2537852680944861179[141] = 0;
   out_2537852680944861179[142] = 0;
   out_2537852680944861179[143] = 0;
   out_2537852680944861179[144] = 0;
   out_2537852680944861179[145] = 0;
   out_2537852680944861179[146] = 0;
   out_2537852680944861179[147] = 0;
   out_2537852680944861179[148] = 0;
   out_2537852680944861179[149] = 0;
   out_2537852680944861179[150] = 0;
   out_2537852680944861179[151] = 0;
   out_2537852680944861179[152] = 1;
   out_2537852680944861179[153] = 0;
   out_2537852680944861179[154] = 0;
   out_2537852680944861179[155] = 0;
   out_2537852680944861179[156] = 0;
   out_2537852680944861179[157] = 0;
   out_2537852680944861179[158] = 0;
   out_2537852680944861179[159] = 0;
   out_2537852680944861179[160] = 0;
   out_2537852680944861179[161] = 0;
   out_2537852680944861179[162] = 0;
   out_2537852680944861179[163] = 0;
   out_2537852680944861179[164] = 0;
   out_2537852680944861179[165] = 0;
   out_2537852680944861179[166] = 0;
   out_2537852680944861179[167] = 0;
   out_2537852680944861179[168] = 0;
   out_2537852680944861179[169] = 0;
   out_2537852680944861179[170] = 0;
   out_2537852680944861179[171] = 1;
   out_2537852680944861179[172] = 0;
   out_2537852680944861179[173] = 0;
   out_2537852680944861179[174] = 0;
   out_2537852680944861179[175] = 0;
   out_2537852680944861179[176] = 0;
   out_2537852680944861179[177] = 0;
   out_2537852680944861179[178] = 0;
   out_2537852680944861179[179] = 0;
   out_2537852680944861179[180] = 0;
   out_2537852680944861179[181] = 0;
   out_2537852680944861179[182] = 0;
   out_2537852680944861179[183] = 0;
   out_2537852680944861179[184] = 0;
   out_2537852680944861179[185] = 0;
   out_2537852680944861179[186] = 0;
   out_2537852680944861179[187] = 0;
   out_2537852680944861179[188] = 0;
   out_2537852680944861179[189] = 0;
   out_2537852680944861179[190] = 1;
   out_2537852680944861179[191] = 0;
   out_2537852680944861179[192] = 0;
   out_2537852680944861179[193] = 0;
   out_2537852680944861179[194] = 0;
   out_2537852680944861179[195] = 0;
   out_2537852680944861179[196] = 0;
   out_2537852680944861179[197] = 0;
   out_2537852680944861179[198] = 0;
   out_2537852680944861179[199] = 0;
   out_2537852680944861179[200] = 0;
   out_2537852680944861179[201] = 0;
   out_2537852680944861179[202] = 0;
   out_2537852680944861179[203] = 0;
   out_2537852680944861179[204] = 0;
   out_2537852680944861179[205] = 0;
   out_2537852680944861179[206] = 0;
   out_2537852680944861179[207] = 0;
   out_2537852680944861179[208] = 0;
   out_2537852680944861179[209] = 1;
   out_2537852680944861179[210] = 0;
   out_2537852680944861179[211] = 0;
   out_2537852680944861179[212] = 0;
   out_2537852680944861179[213] = 0;
   out_2537852680944861179[214] = 0;
   out_2537852680944861179[215] = 0;
   out_2537852680944861179[216] = 0;
   out_2537852680944861179[217] = 0;
   out_2537852680944861179[218] = 0;
   out_2537852680944861179[219] = 0;
   out_2537852680944861179[220] = 0;
   out_2537852680944861179[221] = 0;
   out_2537852680944861179[222] = 0;
   out_2537852680944861179[223] = 0;
   out_2537852680944861179[224] = 0;
   out_2537852680944861179[225] = 0;
   out_2537852680944861179[226] = 0;
   out_2537852680944861179[227] = 0;
   out_2537852680944861179[228] = 1;
   out_2537852680944861179[229] = 0;
   out_2537852680944861179[230] = 0;
   out_2537852680944861179[231] = 0;
   out_2537852680944861179[232] = 0;
   out_2537852680944861179[233] = 0;
   out_2537852680944861179[234] = 0;
   out_2537852680944861179[235] = 0;
   out_2537852680944861179[236] = 0;
   out_2537852680944861179[237] = 0;
   out_2537852680944861179[238] = 0;
   out_2537852680944861179[239] = 0;
   out_2537852680944861179[240] = 0;
   out_2537852680944861179[241] = 0;
   out_2537852680944861179[242] = 0;
   out_2537852680944861179[243] = 0;
   out_2537852680944861179[244] = 0;
   out_2537852680944861179[245] = 0;
   out_2537852680944861179[246] = 0;
   out_2537852680944861179[247] = 1;
   out_2537852680944861179[248] = 0;
   out_2537852680944861179[249] = 0;
   out_2537852680944861179[250] = 0;
   out_2537852680944861179[251] = 0;
   out_2537852680944861179[252] = 0;
   out_2537852680944861179[253] = 0;
   out_2537852680944861179[254] = 0;
   out_2537852680944861179[255] = 0;
   out_2537852680944861179[256] = 0;
   out_2537852680944861179[257] = 0;
   out_2537852680944861179[258] = 0;
   out_2537852680944861179[259] = 0;
   out_2537852680944861179[260] = 0;
   out_2537852680944861179[261] = 0;
   out_2537852680944861179[262] = 0;
   out_2537852680944861179[263] = 0;
   out_2537852680944861179[264] = 0;
   out_2537852680944861179[265] = 0;
   out_2537852680944861179[266] = 1;
   out_2537852680944861179[267] = 0;
   out_2537852680944861179[268] = 0;
   out_2537852680944861179[269] = 0;
   out_2537852680944861179[270] = 0;
   out_2537852680944861179[271] = 0;
   out_2537852680944861179[272] = 0;
   out_2537852680944861179[273] = 0;
   out_2537852680944861179[274] = 0;
   out_2537852680944861179[275] = 0;
   out_2537852680944861179[276] = 0;
   out_2537852680944861179[277] = 0;
   out_2537852680944861179[278] = 0;
   out_2537852680944861179[279] = 0;
   out_2537852680944861179[280] = 0;
   out_2537852680944861179[281] = 0;
   out_2537852680944861179[282] = 0;
   out_2537852680944861179[283] = 0;
   out_2537852680944861179[284] = 0;
   out_2537852680944861179[285] = 1;
   out_2537852680944861179[286] = 0;
   out_2537852680944861179[287] = 0;
   out_2537852680944861179[288] = 0;
   out_2537852680944861179[289] = 0;
   out_2537852680944861179[290] = 0;
   out_2537852680944861179[291] = 0;
   out_2537852680944861179[292] = 0;
   out_2537852680944861179[293] = 0;
   out_2537852680944861179[294] = 0;
   out_2537852680944861179[295] = 0;
   out_2537852680944861179[296] = 0;
   out_2537852680944861179[297] = 0;
   out_2537852680944861179[298] = 0;
   out_2537852680944861179[299] = 0;
   out_2537852680944861179[300] = 0;
   out_2537852680944861179[301] = 0;
   out_2537852680944861179[302] = 0;
   out_2537852680944861179[303] = 0;
   out_2537852680944861179[304] = 1;
   out_2537852680944861179[305] = 0;
   out_2537852680944861179[306] = 0;
   out_2537852680944861179[307] = 0;
   out_2537852680944861179[308] = 0;
   out_2537852680944861179[309] = 0;
   out_2537852680944861179[310] = 0;
   out_2537852680944861179[311] = 0;
   out_2537852680944861179[312] = 0;
   out_2537852680944861179[313] = 0;
   out_2537852680944861179[314] = 0;
   out_2537852680944861179[315] = 0;
   out_2537852680944861179[316] = 0;
   out_2537852680944861179[317] = 0;
   out_2537852680944861179[318] = 0;
   out_2537852680944861179[319] = 0;
   out_2537852680944861179[320] = 0;
   out_2537852680944861179[321] = 0;
   out_2537852680944861179[322] = 0;
   out_2537852680944861179[323] = 1;
}
void h_4(double *state, double *unused, double *out_7730454059225088569) {
   out_7730454059225088569[0] = state[6] + state[9];
   out_7730454059225088569[1] = state[7] + state[10];
   out_7730454059225088569[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_7019083287459919586) {
   out_7019083287459919586[0] = 0;
   out_7019083287459919586[1] = 0;
   out_7019083287459919586[2] = 0;
   out_7019083287459919586[3] = 0;
   out_7019083287459919586[4] = 0;
   out_7019083287459919586[5] = 0;
   out_7019083287459919586[6] = 1;
   out_7019083287459919586[7] = 0;
   out_7019083287459919586[8] = 0;
   out_7019083287459919586[9] = 1;
   out_7019083287459919586[10] = 0;
   out_7019083287459919586[11] = 0;
   out_7019083287459919586[12] = 0;
   out_7019083287459919586[13] = 0;
   out_7019083287459919586[14] = 0;
   out_7019083287459919586[15] = 0;
   out_7019083287459919586[16] = 0;
   out_7019083287459919586[17] = 0;
   out_7019083287459919586[18] = 0;
   out_7019083287459919586[19] = 0;
   out_7019083287459919586[20] = 0;
   out_7019083287459919586[21] = 0;
   out_7019083287459919586[22] = 0;
   out_7019083287459919586[23] = 0;
   out_7019083287459919586[24] = 0;
   out_7019083287459919586[25] = 1;
   out_7019083287459919586[26] = 0;
   out_7019083287459919586[27] = 0;
   out_7019083287459919586[28] = 1;
   out_7019083287459919586[29] = 0;
   out_7019083287459919586[30] = 0;
   out_7019083287459919586[31] = 0;
   out_7019083287459919586[32] = 0;
   out_7019083287459919586[33] = 0;
   out_7019083287459919586[34] = 0;
   out_7019083287459919586[35] = 0;
   out_7019083287459919586[36] = 0;
   out_7019083287459919586[37] = 0;
   out_7019083287459919586[38] = 0;
   out_7019083287459919586[39] = 0;
   out_7019083287459919586[40] = 0;
   out_7019083287459919586[41] = 0;
   out_7019083287459919586[42] = 0;
   out_7019083287459919586[43] = 0;
   out_7019083287459919586[44] = 1;
   out_7019083287459919586[45] = 0;
   out_7019083287459919586[46] = 0;
   out_7019083287459919586[47] = 1;
   out_7019083287459919586[48] = 0;
   out_7019083287459919586[49] = 0;
   out_7019083287459919586[50] = 0;
   out_7019083287459919586[51] = 0;
   out_7019083287459919586[52] = 0;
   out_7019083287459919586[53] = 0;
}
void h_10(double *state, double *unused, double *out_1910166407148471034) {
   out_1910166407148471034[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_1910166407148471034[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_1910166407148471034[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_3315929574475692252) {
   out_3315929574475692252[0] = 0;
   out_3315929574475692252[1] = 9.8100000000000005*cos(state[1]);
   out_3315929574475692252[2] = 0;
   out_3315929574475692252[3] = 0;
   out_3315929574475692252[4] = -state[8];
   out_3315929574475692252[5] = state[7];
   out_3315929574475692252[6] = 0;
   out_3315929574475692252[7] = state[5];
   out_3315929574475692252[8] = -state[4];
   out_3315929574475692252[9] = 0;
   out_3315929574475692252[10] = 0;
   out_3315929574475692252[11] = 0;
   out_3315929574475692252[12] = 1;
   out_3315929574475692252[13] = 0;
   out_3315929574475692252[14] = 0;
   out_3315929574475692252[15] = 1;
   out_3315929574475692252[16] = 0;
   out_3315929574475692252[17] = 0;
   out_3315929574475692252[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_3315929574475692252[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_3315929574475692252[20] = 0;
   out_3315929574475692252[21] = state[8];
   out_3315929574475692252[22] = 0;
   out_3315929574475692252[23] = -state[6];
   out_3315929574475692252[24] = -state[5];
   out_3315929574475692252[25] = 0;
   out_3315929574475692252[26] = state[3];
   out_3315929574475692252[27] = 0;
   out_3315929574475692252[28] = 0;
   out_3315929574475692252[29] = 0;
   out_3315929574475692252[30] = 0;
   out_3315929574475692252[31] = 1;
   out_3315929574475692252[32] = 0;
   out_3315929574475692252[33] = 0;
   out_3315929574475692252[34] = 1;
   out_3315929574475692252[35] = 0;
   out_3315929574475692252[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_3315929574475692252[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_3315929574475692252[38] = 0;
   out_3315929574475692252[39] = -state[7];
   out_3315929574475692252[40] = state[6];
   out_3315929574475692252[41] = 0;
   out_3315929574475692252[42] = state[4];
   out_3315929574475692252[43] = -state[3];
   out_3315929574475692252[44] = 0;
   out_3315929574475692252[45] = 0;
   out_3315929574475692252[46] = 0;
   out_3315929574475692252[47] = 0;
   out_3315929574475692252[48] = 0;
   out_3315929574475692252[49] = 0;
   out_3315929574475692252[50] = 1;
   out_3315929574475692252[51] = 0;
   out_3315929574475692252[52] = 0;
   out_3315929574475692252[53] = 1;
}
void h_13(double *state, double *unused, double *out_2907941445058093810) {
   out_2907941445058093810[0] = state[3];
   out_2907941445058093810[1] = state[4];
   out_2907941445058093810[2] = state[5];
}
void H_13(double *state, double *unused, double *out_7593905322947108006) {
   out_7593905322947108006[0] = 0;
   out_7593905322947108006[1] = 0;
   out_7593905322947108006[2] = 0;
   out_7593905322947108006[3] = 1;
   out_7593905322947108006[4] = 0;
   out_7593905322947108006[5] = 0;
   out_7593905322947108006[6] = 0;
   out_7593905322947108006[7] = 0;
   out_7593905322947108006[8] = 0;
   out_7593905322947108006[9] = 0;
   out_7593905322947108006[10] = 0;
   out_7593905322947108006[11] = 0;
   out_7593905322947108006[12] = 0;
   out_7593905322947108006[13] = 0;
   out_7593905322947108006[14] = 0;
   out_7593905322947108006[15] = 0;
   out_7593905322947108006[16] = 0;
   out_7593905322947108006[17] = 0;
   out_7593905322947108006[18] = 0;
   out_7593905322947108006[19] = 0;
   out_7593905322947108006[20] = 0;
   out_7593905322947108006[21] = 0;
   out_7593905322947108006[22] = 1;
   out_7593905322947108006[23] = 0;
   out_7593905322947108006[24] = 0;
   out_7593905322947108006[25] = 0;
   out_7593905322947108006[26] = 0;
   out_7593905322947108006[27] = 0;
   out_7593905322947108006[28] = 0;
   out_7593905322947108006[29] = 0;
   out_7593905322947108006[30] = 0;
   out_7593905322947108006[31] = 0;
   out_7593905322947108006[32] = 0;
   out_7593905322947108006[33] = 0;
   out_7593905322947108006[34] = 0;
   out_7593905322947108006[35] = 0;
   out_7593905322947108006[36] = 0;
   out_7593905322947108006[37] = 0;
   out_7593905322947108006[38] = 0;
   out_7593905322947108006[39] = 0;
   out_7593905322947108006[40] = 0;
   out_7593905322947108006[41] = 1;
   out_7593905322947108006[42] = 0;
   out_7593905322947108006[43] = 0;
   out_7593905322947108006[44] = 0;
   out_7593905322947108006[45] = 0;
   out_7593905322947108006[46] = 0;
   out_7593905322947108006[47] = 0;
   out_7593905322947108006[48] = 0;
   out_7593905322947108006[49] = 0;
   out_7593905322947108006[50] = 0;
   out_7593905322947108006[51] = 0;
   out_7593905322947108006[52] = 0;
   out_7593905322947108006[53] = 0;
}
void h_14(double *state, double *unused, double *out_5410884076226838020) {
   out_5410884076226838020[0] = state[6];
   out_5410884076226838020[1] = state[7];
   out_5410884076226838020[2] = state[8];
}
void H_14(double *state, double *unused, double *out_8344872353954259734) {
   out_8344872353954259734[0] = 0;
   out_8344872353954259734[1] = 0;
   out_8344872353954259734[2] = 0;
   out_8344872353954259734[3] = 0;
   out_8344872353954259734[4] = 0;
   out_8344872353954259734[5] = 0;
   out_8344872353954259734[6] = 1;
   out_8344872353954259734[7] = 0;
   out_8344872353954259734[8] = 0;
   out_8344872353954259734[9] = 0;
   out_8344872353954259734[10] = 0;
   out_8344872353954259734[11] = 0;
   out_8344872353954259734[12] = 0;
   out_8344872353954259734[13] = 0;
   out_8344872353954259734[14] = 0;
   out_8344872353954259734[15] = 0;
   out_8344872353954259734[16] = 0;
   out_8344872353954259734[17] = 0;
   out_8344872353954259734[18] = 0;
   out_8344872353954259734[19] = 0;
   out_8344872353954259734[20] = 0;
   out_8344872353954259734[21] = 0;
   out_8344872353954259734[22] = 0;
   out_8344872353954259734[23] = 0;
   out_8344872353954259734[24] = 0;
   out_8344872353954259734[25] = 1;
   out_8344872353954259734[26] = 0;
   out_8344872353954259734[27] = 0;
   out_8344872353954259734[28] = 0;
   out_8344872353954259734[29] = 0;
   out_8344872353954259734[30] = 0;
   out_8344872353954259734[31] = 0;
   out_8344872353954259734[32] = 0;
   out_8344872353954259734[33] = 0;
   out_8344872353954259734[34] = 0;
   out_8344872353954259734[35] = 0;
   out_8344872353954259734[36] = 0;
   out_8344872353954259734[37] = 0;
   out_8344872353954259734[38] = 0;
   out_8344872353954259734[39] = 0;
   out_8344872353954259734[40] = 0;
   out_8344872353954259734[41] = 0;
   out_8344872353954259734[42] = 0;
   out_8344872353954259734[43] = 0;
   out_8344872353954259734[44] = 1;
   out_8344872353954259734[45] = 0;
   out_8344872353954259734[46] = 0;
   out_8344872353954259734[47] = 0;
   out_8344872353954259734[48] = 0;
   out_8344872353954259734[49] = 0;
   out_8344872353954259734[50] = 0;
   out_8344872353954259734[51] = 0;
   out_8344872353954259734[52] = 0;
   out_8344872353954259734[53] = 0;
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
void pose_err_fun(double *nom_x, double *delta_x, double *out_5308991872147398563) {
  err_fun(nom_x, delta_x, out_5308991872147398563);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_5440750294658648606) {
  inv_err_fun(nom_x, true_x, out_5440750294658648606);
}
void pose_H_mod_fun(double *state, double *out_7655853576405724458) {
  H_mod_fun(state, out_7655853576405724458);
}
void pose_f_fun(double *state, double dt, double *out_4136808220434975141) {
  f_fun(state,  dt, out_4136808220434975141);
}
void pose_F_fun(double *state, double dt, double *out_2537852680944861179) {
  F_fun(state,  dt, out_2537852680944861179);
}
void pose_h_4(double *state, double *unused, double *out_7730454059225088569) {
  h_4(state, unused, out_7730454059225088569);
}
void pose_H_4(double *state, double *unused, double *out_7019083287459919586) {
  H_4(state, unused, out_7019083287459919586);
}
void pose_h_10(double *state, double *unused, double *out_1910166407148471034) {
  h_10(state, unused, out_1910166407148471034);
}
void pose_H_10(double *state, double *unused, double *out_3315929574475692252) {
  H_10(state, unused, out_3315929574475692252);
}
void pose_h_13(double *state, double *unused, double *out_2907941445058093810) {
  h_13(state, unused, out_2907941445058093810);
}
void pose_H_13(double *state, double *unused, double *out_7593905322947108006) {
  H_13(state, unused, out_7593905322947108006);
}
void pose_h_14(double *state, double *unused, double *out_5410884076226838020) {
  h_14(state, unused, out_5410884076226838020);
}
void pose_H_14(double *state, double *unused, double *out_8344872353954259734) {
  H_14(state, unused, out_8344872353954259734);
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
