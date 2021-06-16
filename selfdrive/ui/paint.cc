#include "paint.h"

#include <assert.h>

#include <algorithm>

#ifdef __APPLE__
#include <OpenGL/gl3.h>
#define NANOVG_GL3_IMPLEMENTATION
#define nvgCreate nvgCreateGL3
#else
#include <GLES3/gl3.h>
#define NANOVG_GLES3_IMPLEMENTATION
#define nvgCreate nvgCreateGLES3
#endif

#define NANOVG_GLES3_IMPLEMENTATION
#include <nanovg_gl.h>
#include <nanovg_gl_utils.h>

#include "selfdrive/common/timing.h"
#include "selfdrive/common/util.h"
#include "selfdrive/hardware/hw.h"

#include "selfdrive/ui/ui.h"

static void ui_print(UIState *s, int x, int y,  const char* fmt, ... )
{
  char* msg_buf = NULL;
  va_list args;
  va_start(args, fmt);
  vasprintf( &msg_buf, fmt, args);
  va_end(args);
  nvgText(s->vg, x, y, msg_buf, NULL);
}

static void ui_draw_text(const UIState *s, float x, float y, const char *string, float size, NVGcolor color, const char *font_name) {
  nvgFontFace(s->vg, font_name);
  nvgFontSize(s->vg, size*0.8);
  nvgFillColor(s->vg, color);
  nvgText(s->vg, x, y, string, NULL);
}

static void draw_chevron(UIState *s, float x, float y, float sz, NVGcolor fillColor, NVGcolor glowColor) {
  // glow
  float g_xo = sz/5;
  float g_yo = sz/10;
  nvgBeginPath(s->vg);
  nvgMoveTo(s->vg, x+(sz*1.35)+g_xo, y+sz+g_yo);
  nvgLineTo(s->vg, x, y-g_xo);
  nvgLineTo(s->vg, x-(sz*1.35)-g_xo, y+sz+g_yo);
  nvgClosePath(s->vg);
  nvgFillColor(s->vg, glowColor);
  nvgFill(s->vg);

  // chevron
  nvgBeginPath(s->vg);
  nvgMoveTo(s->vg, x+(sz*1.25), y+sz);
  nvgLineTo(s->vg, x, y);
  nvgLineTo(s->vg, x-(sz*1.25), y+sz);
  nvgClosePath(s->vg);
  nvgFillColor(s->vg, fillColor);
  nvgFill(s->vg);
}

//atom(conan)'s steering wheel
static void ui_draw_circle_image(const UIState *s, int center_x, int center_y, int radius, const char *image, NVGcolor color, float img_alpha, float angleSteers = 0) {
  const int img_size = radius * 1.5;
  float img_rotation =  angleSteers/180*3.141592;
  int ct_pos = -radius * 0.75;

  nvgBeginPath(s->vg);
  nvgCircle(s->vg, center_x, center_y + (bdr_s+7), radius);
  nvgFillColor(s->vg, color);
  nvgFill(s->vg);
  //ui_draw_image(s, {center_x - (img_size / 2), center_y - (img_size / 2), img_size, img_size}, image, img_alpha);

  nvgSave( s->vg );
  nvgTranslate(s->vg, center_x, (center_y + (bdr_s*1.5)));
  nvgRotate(s->vg, -img_rotation);  

  ui_draw_image(s, {ct_pos, ct_pos, img_size, img_size}, image, img_alpha);
  nvgRestore(s->vg); 
}

static void ui_draw_circle_image(const UIState *s, int center_x, int center_y, int radius, const char *image, bool active) {
  float bg_alpha = active ? 0.3f : 0.1f;
  float img_alpha = active ? 1.0f : 0.15f;
  if (s->scene.monitoring_mode) {
    ui_draw_circle_image(s, center_x, center_y, radius, image, nvgRGBA(10, 120, 20, (255 * bg_alpha * 1.1)), img_alpha);
  } else {
    ui_draw_circle_image(s, center_x, center_y, radius, image, nvgRGBA(0, 0, 0, (255 * bg_alpha)), img_alpha);
  }
}

static void draw_lead(UIState *s, const cereal::RadarState::LeadData::Reader &lead_data, const vertex_data &vd) {
  // Draw lead car indicator
  auto [x, y] = vd;

  float fillAlpha = 0;
  float speedBuff = 10.;
  float leadBuff = 40.;
  float d_rel = lead_data.getDRel();
  float v_rel = lead_data.getVRel();
  if (d_rel < leadBuff) {
    fillAlpha = 255*(1.0-(d_rel/leadBuff));
    if (v_rel < 0) {
      fillAlpha += 255*(-1*(v_rel/speedBuff));
    }
    fillAlpha = (int)(fmin(fillAlpha, 255));
  }

  float sz = std::clamp((25 * 30) / (d_rel / 3 + 30), 15.0f, 30.0f) * s->zoom;
  x = std::clamp(x, 0.f, s->viz_rect.right() - sz / 2);
  y = std::fmin(s->viz_rect.bottom() - sz * .6, y);
  nvgTextAlign(s->vg, NVG_ALIGN_CENTER | NVG_ALIGN_MIDDLE);

  if (s->scene.radarDistance < 149) {
    draw_chevron(s, x, y, sz, nvgRGBA(201, 34, 49, fillAlpha), COLOR_YELLOW);
    ui_draw_text(s, x, y + sz/1.5f, "R", 20 * 2.5, COLOR_WHITE, "sans-bold"); //neokii
  } else {
    draw_chevron(s, x, y, sz, nvgRGBA(165, 255, 135, fillAlpha), COLOR_GREEN);
    ui_draw_text(s, x, y + sz/1.5f, "C", 20 * 2.5, COLOR_BLACK, "sans-bold"); //hoya
  }
}

static void ui_draw_line(UIState *s, const line_vertices_data &vd, NVGcolor *color, NVGpaint *paint) {
  if (vd.cnt == 0) return;

  const vertex_data *v = &vd.v[0];
  nvgBeginPath(s->vg);
  nvgMoveTo(s->vg, v[0].x, v[0].y);
  for (int i = 1; i < vd.cnt; i++) {
    nvgLineTo(s->vg, v[i].x, v[i].y);
  }
  nvgClosePath(s->vg);
  if (color) {
    nvgFillColor(s->vg, *color);
  } else if (paint) {
    nvgFillPaint(s->vg, *paint);
  }
  nvgFill(s->vg);
}

//Atom(Conan)'s colored track, some codes come from Hoya
static void ui_draw_track(UIState *s, const line_vertices_data &vd) 
{
  if (vd.cnt == 0) return;

  nvgBeginPath(s->vg);
  nvgMoveTo(s->vg, vd.v[0].x, vd.v[0].y);
  for (int i=1; i<vd.cnt; i++) {
    nvgLineTo(s->vg, vd.v[i].x, vd.v[i].y);
  }
  nvgClosePath(s->vg);

  int steerOverride = s->scene.car_state.getSteeringPressed();
  NVGpaint track_bg;
  if (s->scene.controls_state.getEnabled() && !s->scene.comma_stock_ui) {
    if (steerOverride) {
      track_bg = nvgLinearGradient(s->vg, s->fb_w, s->fb_h, s->fb_w, s->fb_h*.4,
        COLOR_BLACK_ALPHA(80), COLOR_BLACK_ALPHA(20));
    } else {
      float steer_max_v = s->scene.steerMax_V - (1.5 * (s->scene.steerMax_V - 0.9));
      int torque_scale = (int)fabs(255*(float)s->scene.output_scale*steer_max_v);
      int red_lvl = fmin(255, torque_scale);
      int green_lvl = fmin(255, 255-torque_scale);
      track_bg = nvgLinearGradient(s->vg, s->fb_w, s->fb_h, s->fb_w, s->fb_h*.4,
        nvgRGBA(          red_lvl,            green_lvl,  0, 150),
        nvgRGBA((int)(0.7*red_lvl), (int)(0.7*green_lvl), 0, 20));
    }
  } else {
    // Draw white vision track
    track_bg = nvgLinearGradient(s->vg, s->fb_w, s->fb_h, s->fb_w, s->fb_h * .4,
                                        COLOR_WHITE_ALPHA(150), COLOR_WHITE_ALPHA(20));
  }

  nvgFillPaint(s->vg, track_bg);
  nvgFill(s->vg); 
}

static void draw_frame(UIState *s) {
  glBindVertexArray(s->frame_vao);
  mat4 *out_mat = &s->rear_frame_mat;
  glActiveTexture(GL_TEXTURE0);

  if (s->last_frame) {
    glBindTexture(GL_TEXTURE_2D, s->texture[s->last_frame->idx]->frame_tex);
    if (!Hardware::EON()) {
      // this is handled in ion on QCOM
      glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, s->last_frame->width, s->last_frame->height,
                   0, GL_RGB, GL_UNSIGNED_BYTE, s->last_frame->addr);
    }
  }

  glUseProgram(s->gl_shader->prog);
  glUniform1i(s->gl_shader->getUniformLocation("uTexture"), 0);
  glUniformMatrix4fv(s->gl_shader->getUniformLocation("uTransform"), 1, GL_TRUE, out_mat->v);

  assert(glGetError() == GL_NO_ERROR);
  glEnableVertexAttribArray(0);
  glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_BYTE, (const void *)0);
  glDisableVertexAttribArray(0);
  glBindVertexArray(0);
}

// Hoya's colored lane line
static void ui_draw_vision_lane_lines(UIState *s) {
  const UIScene &scene = s->scene;
  float red_lvl = 0.0;
  float green_lvl = 0.0;
  //if (!scene.end_to_end) {
  if (!scene.lateralPlan.lanelessModeStatus) {
    // paint lanelines
    for (int i = 0; i < std::size(scene.lane_line_vertices); i++) {
      red_lvl = 0.0;
      green_lvl = 0.0;
      if (scene.lane_line_probs[i] > 0.4){
        red_lvl = 1.0 - (scene.lane_line_probs[i] - 0.4) * 2.5;
        green_lvl = 1.0 ;
      }
      else {
        red_lvl = 1.0 ;
        green_lvl = 1.0 - (0.4 - scene.lane_line_probs[i]) * 2.5;
      }
      NVGcolor lane_color = nvgRGBAf(red_lvl, green_lvl, 0, 1);
      if (s->scene.comma_stock_ui) {
        lane_color = nvgRGBAf(1.0, 1.0, 1.0, scene.lane_line_probs[i]);
      }
      ui_draw_line(s, scene.lane_line_vertices[i], &lane_color, nullptr);
    }

    // paint road edges
    for (int i = 0; i < std::size(scene.road_edge_vertices); i++) {
      NVGcolor color = nvgRGBAf(1.0, 0.0, 0.0, std::clamp<float>(1.0 - scene.road_edge_stds[i], 0.0, 1.0));
      ui_draw_line(s, scene.road_edge_vertices[i], &color, nullptr);
    }
  }

  // paint path
  ui_draw_track(s, scene.track_vertices);
  //NVGpaint track_bg = nvgLinearGradient(s->vg, s->fb_w, s->fb_h, s->fb_w, s->fb_h * .4,
  //                                      COLOR_WHITE, COLOR_WHITE_ALPHA(0));
  //ui_draw_line(s, scene.track_vertices, nullptr, &track_bg);
}

// Draw all world space objects.
static void ui_draw_world(UIState *s) {
  // Don't draw on top of sidebar
  nvgScissor(s->vg, s->viz_rect.x, s->viz_rect.y, s->viz_rect.w, s->viz_rect.h);

  // Draw lane edges and vision/mpc tracks
  ui_draw_vision_lane_lines(s);

  // Draw lead indicators if openpilot is handling longitudinal
  //if (s->scene.longitudinal_control) {
  if (true) {
    auto radar_state = (*s->sm)["radarState"].getRadarState();
    auto lead_one = radar_state.getLeadOne();
    auto lead_two = radar_state.getLeadTwo();
    if (lead_one.getStatus()) {
      draw_lead(s, lead_one, s->scene.lead_vertices[0]);
    }
    if (lead_two.getStatus() && (std::abs(lead_one.getDRel() - lead_two.getDRel()) > 3.0)) {
      draw_lead(s, lead_two, s->scene.lead_vertices[1]);
    }
  }
  nvgResetScissor(s->vg);
}

// TPMS code added from OPKR
static void ui_draw_tpms(UIState *s) {
  char tpmsFl[32];
  char tpmsFr[32];
  char tpmsRl[32];
  char tpmsRr[32];
  int viz_tpms_w = 230;
  int viz_tpms_h = 160;
  int viz_tpms_x = s->viz_rect.x + s->viz_rect.w - (bdr_s+425);
  int viz_tpms_y = s->viz_rect.y + (bdr_s);
  float maxv = 0;
  float minv = 300;
  const Rect rect = {viz_tpms_x, viz_tpms_y, viz_tpms_w, viz_tpms_h};

  if (maxv < s->scene.tpmsPressureFl) {maxv = s->scene.tpmsPressureFl;}
  if (maxv < s->scene.tpmsPressureFr) {maxv = s->scene.tpmsPressureFr;}
  if (maxv < s->scene.tpmsPressureRl) {maxv = s->scene.tpmsPressureRl;}
  if (maxv < s->scene.tpmsPressureRr) {maxv = s->scene.tpmsPressureRr;}
  if (minv > s->scene.tpmsPressureFl) {minv = s->scene.tpmsPressureFl;}
  if (minv > s->scene.tpmsPressureFr) {minv = s->scene.tpmsPressureFr;}
  if (minv > s->scene.tpmsPressureRl) {minv = s->scene.tpmsPressureRl;}
  if (minv > s->scene.tpmsPressureRr) {minv = s->scene.tpmsPressureRr;}

  // Draw Border
  ui_draw_rect(s->vg, rect, COLOR_WHITE_ALPHA(100), 10, 20.);
  // Draw Background
  if ((maxv - minv) > 3) {
    ui_fill_rect(s->vg, rect, COLOR_RED_ALPHA(80), 20);
  } else {
    ui_fill_rect(s->vg, rect, COLOR_BLACK_ALPHA(80), 20);
  }

  nvgTextAlign(s->vg, NVG_ALIGN_CENTER | NVG_ALIGN_BASELINE);
  const int pos_x = viz_tpms_x + (viz_tpms_w / 2);
  const int pos_y = viz_tpms_y + 45;
  ui_draw_text(s, pos_x, pos_y, "TPMS(psi)", 45, COLOR_WHITE_ALPHA(180), "sans-regular");
  snprintf(tpmsFl, sizeof(tpmsFl), "%.1f", s->scene.tpmsPressureFl);
  snprintf(tpmsFr, sizeof(tpmsFr), "%.1f", s->scene.tpmsPressureFr);
  snprintf(tpmsRl, sizeof(tpmsRl), "%.1f", s->scene.tpmsPressureRl);
  snprintf(tpmsRr, sizeof(tpmsRr), "%.1f", s->scene.tpmsPressureRr);
  if (s->scene.tpmsPressureFl < 34) {
    ui_draw_text(s, pos_x-55, pos_y+50, tpmsFl, 60, COLOR_RED, "sans-bold");
  } else if (s->scene.tpmsPressureFl > 50) {
    ui_draw_text(s, pos_x-55, pos_y+50, "N/A", 60, COLOR_WHITE_ALPHA(200), "sans-semibold");
  } else {
    ui_draw_text(s, pos_x-55, pos_y+50, tpmsFl, 60, COLOR_WHITE_ALPHA(200), "sans-semibold");
  }
  if (s->scene.tpmsPressureFr < 34) {
    ui_draw_text(s, pos_x+55, pos_y+50, tpmsFr, 60, COLOR_RED, "sans-bold");
  } else if (s->scene.tpmsPressureFr > 50) {
    ui_draw_text(s, pos_x+55, pos_y+50, "N/A", 60, COLOR_WHITE_ALPHA(200), "sans-semibold");
  } else {
    ui_draw_text(s, pos_x+55, pos_y+50, tpmsFr, 60, COLOR_WHITE_ALPHA(200), "sans-semibold");
  }
  if (s->scene.tpmsPressureRl < 34) {
    ui_draw_text(s, pos_x-55, pos_y+100, tpmsRl, 60, COLOR_RED, "sans-bold");
  } else if (s->scene.tpmsPressureRl > 50) {
    ui_draw_text(s, pos_x-55, pos_y+100, "N/A", 60, COLOR_WHITE_ALPHA(200), "sans-semibold");
  } else {
    ui_draw_text(s, pos_x-55, pos_y+100, tpmsRl, 60, COLOR_WHITE_ALPHA(200), "sans-semibold");
  }
  if (s->scene.tpmsPressureRr < 34) {
    ui_draw_text(s, pos_x+55, pos_y+100, tpmsRr, 60, COLOR_RED, "sans-bold");
  } else if (s->scene.tpmsPressureRr > 50) {
    ui_draw_text(s, pos_x+55, pos_y+100, "N/A", 60, COLOR_WHITE_ALPHA(200), "sans-semibold");
  } else {
    ui_draw_text(s, pos_x+55, pos_y+100, tpmsRr, 60, COLOR_WHITE_ALPHA(200), "sans-semibold");
  }
}

static void ui_draw_standstill(UIState *s) {
  UIScene &scene = s->scene;

  int viz_standstill_x = s->viz_rect.x + s->viz_rect.w - 560;
  int viz_standstill_y = s->viz_rect.y + (bdr_s) + 160 + 250;
  
  int minute = 0;
  int second = 0;

  minute = int(scene.lateralPlan.standstillElapsedTime / 60);
  second = int(scene.lateralPlan.standstillElapsedTime) - (minute * 60);

  if (scene.standStill) {
    nvgTextAlign(s->vg, NVG_ALIGN_CENTER | NVG_ALIGN_BASELINE);
    nvgFontSize(s->vg, 125);
    nvgFillColor(s->vg, COLOR_ORANGE_ALPHA(240));
    ui_print(s, viz_standstill_x, viz_standstill_y, "STOP");
    nvgFontSize(s->vg, 150);
    nvgFillColor(s->vg, COLOR_WHITE_ALPHA(240));
    ui_print(s, viz_standstill_x, viz_standstill_y+150, "%01d:%02d", minute, second);
  }
}

static void ui_draw_debug(UIState *s) 
{
  UIScene &scene = s->scene;

  int ui_viz_rx = s->viz_rect.x + bdr_s + 192;
  int ui_viz_ry = bdr_s+28;
  int ui_viz_rx_center = s->viz_rect.centerX();
  
  nvgTextAlign(s->vg, NVG_ALIGN_LEFT | NVG_ALIGN_BASELINE);

  if (s->nDebugUi1) {
    ui_draw_text(s, 0, 1035, scene.alertTextMsg1.c_str(), 50, COLOR_WHITE_ALPHA(125), "sans-semibold");
    ui_draw_text(s, 0, 1078, scene.alertTextMsg2.c_str(), 50, COLOR_WHITE_ALPHA(125), "sans-semibold");
  }

  
  nvgFillColor(s->vg, COLOR_WHITE_ALPHA(125));
  if (s->nDebugUi2) {
    //if (scene.gpsAccuracyUblox != 0.00) {
    //  nvgFontSize(s->vg, 34);
    //  ui_print(s, 28, 28, "LAT／LON: %.5f／%.5f", scene.latitudeUblox, scene.longitudeUblox);
    //}
    nvgFontSize(s->vg, 40);
    //ui_print(s, ui_viz_rx, ui_viz_ry, "Live Parameters");
    ui_print(s, ui_viz_rx, ui_viz_ry+250, "SR:%.2f", scene.liveParams.steerRatio);
    //ui_print(s, ui_viz_rx, ui_viz_ry+100, "AOfs:%.2f", scene.liveParams.angleOffset);
    ui_print(s, ui_viz_rx, ui_viz_ry+300, "AA:%.2f", scene.liveParams.angleOffsetAverage);
    ui_print(s, ui_viz_rx, ui_viz_ry+350, "SF:%.2f", scene.liveParams.stiffnessFactor);

    ui_print(s, ui_viz_rx, ui_viz_ry+400, "AD:%.2f", scene.lateralPlan.steerActuatorDelay);
    ui_print(s, ui_viz_rx, ui_viz_ry+450, "SC:%.2f", scene.lateralPlan.steerRateCost);
    ui_print(s, ui_viz_rx, ui_viz_ry+500, "OS:%.2f", abs(scene.output_scale));
    ui_print(s, ui_viz_rx, ui_viz_ry+550, "Prob:");
    ui_print(s, ui_viz_rx, ui_viz_ry+600, "%.2f|%.2f", scene.lateralPlan.lProb, scene.lateralPlan.rProb);
    if (s->scene.longitudinal_control) {
      if (scene.long_plan_source == 0) {
        ui_print(s, ui_viz_rx, ui_viz_ry+650, "LP:none");
      } else if (scene.long_plan_source == 1) {
        ui_print(s, ui_viz_rx, ui_viz_ry+650, "LP:cruise");
      } else if (scene.long_plan_source == 2) {
        ui_print(s, ui_viz_rx, ui_viz_ry+650, "LP:mpc1");
      } else if (scene.long_plan_source == 3) {
        ui_print(s, ui_viz_rx, ui_viz_ry+650, "LP:mpc2");
      } else if (scene.long_plan_source == 4) {
        ui_print(s, ui_viz_rx, ui_viz_ry+650, "LP:mpc3");
      } else if (scene.long_plan_source == 5) {
        ui_print(s, ui_viz_rx, ui_viz_ry+650, "LP:model");
      }
    }
    ui_print(s, ui_viz_rx, ui_viz_ry+700, "MS:%.0f", scene.mapSign);
    nvgFontSize(s->vg, 40);
    nvgTextAlign(s->vg, NVG_ALIGN_CENTER | NVG_ALIGN_MIDDLE);
    if (scene.lateralControlMethod == 0) {
      ui_print(s, ui_viz_rx_center, ui_viz_ry+310, "PID");
    } else if (scene.lateralControlMethod == 1) {
      ui_print(s, ui_viz_rx_center, ui_viz_ry+310, "INDI");
    } else if (scene.lateralControlMethod == 2) {
      ui_print(s, ui_viz_rx_center, ui_viz_ry+310, "LQR");
    }
  }
}

/*
  park @1;
  drive @2;
  neutral @3;
  reverse @4;
  sport @5;
  low @6;
  brake @7;
  eco @8;
*/
static void ui_draw_gear( UIState *s )
{
  UIScene &scene = s->scene;  
  NVGcolor nColor = COLOR_WHITE;
  int x_pos = s->viz_rect.right() - (90 + bdr_s);
  int y_pos = s->viz_rect.y + (bdr_s) + 140;
  int  ngetGearShifter = int(scene.getGearShifter);
  //int  x_pos = 1795;
  //int  y_pos = 155;
  char str_msg[512];

  nvgFontFace(s->vg, "sans-bold");
  nvgFontSize(s->vg, 160 );
  switch( ngetGearShifter )
  {
    case 1 : strcpy( str_msg, "P" ); nColor = nvgRGBA(200, 200, 255, 255); break;
    case 2 : strcpy( str_msg, "D" ); nColor = COLOR_GREEN; break;
    case 3 : strcpy( str_msg, "N" ); nColor = COLOR_WHITE; break;
    case 4 : strcpy( str_msg, "R" ); nColor = COLOR_RED; break;
    case 7 : strcpy( str_msg, "B" ); break;
    default: sprintf( str_msg, "%d", ngetGearShifter ); break;
  }

  nvgFillColor(s->vg, nColor);
  ui_print( s, x_pos, y_pos, str_msg );
}

static void ui_draw_vision_maxspeed_org(UIState *s) {
  const int SET_SPEED_NA = 255;
  float maxspeed = s->scene.controls_state.getVCruise();
  float cruise_speed = s->scene.vSetDis;
  const bool is_cruise_set = maxspeed != 0 && maxspeed != SET_SPEED_NA;
  s->is_speed_over_limit = s->scene.limitSpeedCamera > 29 && ((s->scene.limitSpeedCamera+round(s->scene.limitSpeedCamera*0.01*s->scene.speed_lim_off))+1 < s->scene.car_state.getVEgo()*3.6);
  if (is_cruise_set && !s->scene.is_metric) { maxspeed *= 0.6225; }

  const Rect rect = {s->viz_rect.x + (bdr_s), int(s->viz_rect.y + (bdr_s)), 184, 202};
  NVGcolor color = COLOR_BLACK_ALPHA(100);
  if (s->is_speed_over_limit) {
    color = COLOR_OCHRE_ALPHA(100);
  } else if (s->scene.limitSpeedCamera > 29 && !s->is_speed_over_limit) {
    color = nvgRGBA(0, 120, 0, 100);
  } else if (s->scene.cruiseAccStatus) {
    color = nvgRGBA(0, 100, 200, 100);
  } else if (s->scene.controls_state.getEnabled()) {
    color = COLOR_WHITE_ALPHA(75);
  }
  ui_fill_rect(s->vg, rect, color, 30.);
  ui_draw_rect(s->vg, rect, COLOR_WHITE_ALPHA(100), 10, 20.);

  nvgTextAlign(s->vg, NVG_ALIGN_CENTER | NVG_ALIGN_BASELINE);
  if (cruise_speed >= 30 && s->scene.controls_state.getEnabled()) {
    const std::string cruise_speed_str = std::to_string((int)std::nearbyint(cruise_speed));
    ui_draw_text(s, rect.centerX(), int(s->viz_rect.y + (bdr_s))+65, cruise_speed_str.c_str(), 26 * 2.8, COLOR_WHITE_ALPHA(is_cruise_set ? 200 : 100), "sans-bold");
  } else {
  	ui_draw_text(s, rect.centerX(), int(s->viz_rect.y + (bdr_s))+65, "-", 26 * 2.8, COLOR_WHITE_ALPHA(is_cruise_set ? 200 : 100), "sans-semibold");
  }
  if (is_cruise_set) {
    const std::string maxspeed_str = std::to_string((int)std::nearbyint(maxspeed));
    ui_draw_text(s, rect.centerX(), int(s->viz_rect.y + (bdr_s))+165, maxspeed_str.c_str(), 48 * 2.4, COLOR_WHITE, "sans-bold");
  } else {
    ui_draw_text(s, rect.centerX(), int(s->viz_rect.y + (bdr_s))+165, "-", 42 * 2.4, COLOR_WHITE_ALPHA(100), "sans-semibold");
  }
}

static void ui_draw_vision_maxspeed(UIState *s) {
  const int SET_SPEED_NA = 255;
  float maxspeed = (*s->sm)["controlsState"].getControlsState().getVCruise();
  const bool is_cruise_set = maxspeed != 0 && maxspeed != SET_SPEED_NA && s->scene.controls_state.getEnabled();
  if (is_cruise_set && !s->scene.is_metric) { maxspeed *= 0.6225; }

  int viz_max_o = 184; //offset value to move right
  const Rect rect = {s->viz_rect.x + (bdr_s), int(s->viz_rect.y + (bdr_s)), 184+viz_max_o, 202};
  ui_fill_rect(s->vg, rect, COLOR_BLACK_ALPHA(100), 30.);
  ui_draw_rect(s->vg, rect, COLOR_WHITE_ALPHA(100), 10, 20.);

  nvgTextAlign(s->vg, NVG_ALIGN_CENTER | NVG_ALIGN_BASELINE);
  ui_draw_text(s, rect.centerX()+viz_max_o/2, int(s->viz_rect.y + (bdr_s))+65, "설정속도", 26 * 2.2, COLOR_WHITE_ALPHA(is_cruise_set ? 200 : 100), "sans-regular");
  if (is_cruise_set) {
    const std::string maxspeed_str = std::to_string((int)std::nearbyint(maxspeed));
    ui_draw_text(s, rect.centerX()+viz_max_o/2, int(s->viz_rect.y + (bdr_s))+165, maxspeed_str.c_str(), 48 * 2.3, COLOR_WHITE, "sans-bold");
  } else {
    ui_draw_text(s, rect.centerX()+viz_max_o/2, int(s->viz_rect.y + (bdr_s))+165, "-", 42 * 2.3, COLOR_WHITE_ALPHA(100), "sans-semibold");
  }
}

static void ui_draw_vision_cruise_speed(UIState *s) {
  float cruise_speed = s->scene.vSetDis;
  if (!s->scene.is_metric) { cruise_speed *= 0.621371; }
  s->is_speed_over_limit = s->scene.limitSpeedCamera > 29 && ((s->scene.limitSpeedCamera+round(s->scene.limitSpeedCamera*0.01*s->scene.speed_lim_off))+1 < s->scene.car_state.getVEgo()*3.6);
  const Rect rect = {s->viz_rect.x + (bdr_s), int(s->viz_rect.y + (bdr_s)), 184, 202};

  NVGcolor color = COLOR_GREY;
  if (s->is_speed_over_limit) {
    color = COLOR_OCHRE_ALPHA(200);
  } else if (s->scene.limitSpeedCamera > 29 && !s->is_speed_over_limit) {
    color = nvgRGBA(0, 120, 0, 200);
  } else if (s->scene.cruiseAccStatus) {
    color = nvgRGBA(0, 100, 200, 200);
  } else if (s->scene.controls_state.getEnabled()) {
    color = COLOR_WHITE_ALPHA(75);
  }
  ui_fill_rect(s->vg, rect, color, 30.);
  ui_draw_rect(s->vg, rect, COLOR_WHITE_ALPHA(100), 10, 20.);

  nvgTextAlign(s->vg, NVG_ALIGN_CENTER | NVG_ALIGN_BASELINE);
  if (s->scene.limitSpeedCamera > 29) {
    ui_draw_text(s, rect.centerX(), int(s->viz_rect.y + (bdr_s))+65, "제한속도", 26 * 2.2, COLOR_WHITE_ALPHA(s->scene.cruiseAccStatus ? 200 : 100), "sans-regular");
  } else {
    ui_draw_text(s, rect.centerX(), int(s->viz_rect.y + (bdr_s))+65, "크루즈", 26 * 2.2, COLOR_WHITE_ALPHA(s->scene.cruiseAccStatus ? 200 : 100), "sans-regular");
  }
  const std::string cruise_speed_str = std::to_string((int)std::nearbyint(cruise_speed));
  if (cruise_speed >= 30 && s->scene.controls_state.getEnabled()) {
    ui_draw_text(s, rect.centerX(), int(s->viz_rect.y + (bdr_s))+165, cruise_speed_str.c_str(), 48 * 2.3, COLOR_WHITE, "sans-bold");
  } else {
    ui_draw_text(s, rect.centerX(), int(s->viz_rect.y + (bdr_s))+165, "-", 42 * 2.3, COLOR_WHITE_ALPHA(100), "sans-semibold");
  }
}

static void ui_draw_vision_speed(UIState *s) {
  const float speed = std::max(0.0, (*s->sm)["carState"].getCarState().getVEgo() * (s->scene.is_metric ? 3.6 : 2.2369363));
  const std::string speed_str = std::to_string((int)std::nearbyint(speed));
  const Rect &viz_rect = s->viz_rect;
  const UIScene *scene = &s->scene;
  const int viz_speed_w = 260;
  const int viz_speed_x = viz_rect.centerX() - viz_speed_w/2;
  const int header_h2 = 400;

  // turning blinker from kegman, moving signal by OPKR
  if(scene->leftBlinker && !s->scene.comma_stock_ui) {
    nvgBeginPath(s->vg);
    nvgMoveTo(s->vg, viz_speed_x, viz_rect.y + header_h2/4);
    nvgLineTo(s->vg, viz_speed_x - viz_speed_w/2, viz_rect.y + header_h2/4 + header_h2/4);
    nvgLineTo(s->vg, viz_speed_x, viz_rect.y + header_h2/2 + header_h2/4);
    nvgClosePath(s->vg);
    nvgFillColor(s->vg, nvgRGBA(255,230,70,(scene->blinker_blinkingrate<=120 && scene->blinker_blinkingrate>=50)?70:0));
    nvgFill(s->vg);

    nvgBeginPath(s->vg);
    nvgMoveTo(s->vg, viz_speed_x-145, viz_rect.y + header_h2/4);
    nvgLineTo(s->vg, viz_speed_x-145 - viz_speed_w/2, viz_rect.y + header_h2/4 + header_h2/4);
    nvgLineTo(s->vg, viz_speed_x-145, viz_rect.y + header_h2/2 + header_h2/4);
    nvgClosePath(s->vg);
    nvgFillColor(s->vg, nvgRGBA(255,230,70,(scene->blinker_blinkingrate<=100 && scene->blinker_blinkingrate>=50)?140:0));
    nvgFill(s->vg);

    nvgBeginPath(s->vg);
    nvgMoveTo(s->vg, viz_speed_x-290, viz_rect.y + header_h2/4);
    nvgLineTo(s->vg, viz_speed_x-290 - viz_speed_w/2, viz_rect.y + header_h2/4 + header_h2/4);
    nvgLineTo(s->vg, viz_speed_x-290, viz_rect.y + header_h2/2 + header_h2/4);
    nvgClosePath(s->vg);
    nvgFillColor(s->vg, nvgRGBA(255,230,70,(scene->blinker_blinkingrate<=80 && scene->blinker_blinkingrate>=50)?210:0));
    nvgFill(s->vg);
  }
  if(scene->rightBlinker && !s->scene.comma_stock_ui) {
    nvgBeginPath(s->vg);
    nvgMoveTo(s->vg, viz_speed_x+viz_speed_w, viz_rect.y + header_h2/4);
    nvgLineTo(s->vg, viz_speed_x+viz_speed_w + viz_speed_w/2, viz_rect.y + header_h2/4 + header_h2/4);
    nvgLineTo(s->vg, viz_speed_x+viz_speed_w, viz_rect.y + header_h2/2 + header_h2/4);
    nvgClosePath(s->vg);
    nvgFillColor(s->vg, nvgRGBA(255,230,70,(scene->blinker_blinkingrate<=120 && scene->blinker_blinkingrate>=50)?70:0));
    nvgFill(s->vg);

    nvgBeginPath(s->vg);
    nvgMoveTo(s->vg, viz_speed_x+viz_speed_w+145, viz_rect.y + header_h2/4);
    nvgLineTo(s->vg, viz_speed_x+viz_speed_w+145 + viz_speed_w/2, viz_rect.y + header_h2/4 + header_h2/4);
    nvgLineTo(s->vg, viz_speed_x+viz_speed_w+145, viz_rect.y + header_h2/2 + header_h2/4);
    nvgClosePath(s->vg);
    nvgFillColor(s->vg, nvgRGBA(255,230,70,(scene->blinker_blinkingrate<=100 && scene->blinker_blinkingrate>=50)?140:0));
    nvgFill(s->vg);

    nvgBeginPath(s->vg);
    nvgMoveTo(s->vg, viz_speed_x+viz_speed_w+290, viz_rect.y + header_h2/4);
    nvgLineTo(s->vg, viz_speed_x+viz_speed_w+290 + viz_speed_w/2, viz_rect.y + header_h2/4 + header_h2/4);
    nvgLineTo(s->vg, viz_speed_x+viz_speed_w+290, viz_rect.y + header_h2/2 + header_h2/4);
    nvgClosePath(s->vg);
    nvgFillColor(s->vg, nvgRGBA(255,230,70,(scene->blinker_blinkingrate<=80 && scene->blinker_blinkingrate>=50)?210:0));
    nvgFill(s->vg);
    }
  if(scene->leftBlinker || scene->rightBlinker) {
    s->scene.blinker_blinkingrate -= 5;
    if(scene->blinker_blinkingrate<0) s->scene.blinker_blinkingrate = 120;
  }

  NVGcolor val_color = COLOR_WHITE;

  if( scene->brakePress && !s->scene.comma_stock_ui ) val_color = COLOR_RED;
  else if( scene->brakeLights && !s->scene.comma_stock_ui ) val_color = nvgRGBA(201, 34, 49, 100);
  nvgTextAlign(s->vg, NVG_ALIGN_CENTER | NVG_ALIGN_BASELINE);
  ui_draw_text(s, s->viz_rect.centerX(), 240, speed_str.c_str(), 96 * 2.5, val_color, "sans-bold");
  ui_draw_text(s, s->viz_rect.centerX(), 320, s->scene.is_metric ? "km/h" : "mph", 36 * 2.5, COLOR_WHITE_ALPHA(200), "sans-regular");
}

static void ui_draw_vision_event(UIState *s) {
  const int viz_event_w = 220;
  const int viz_event_x = s->viz_rect.right() - (viz_event_w + bdr_s);
  const int viz_event_y = s->viz_rect.y + (bdr_s);

  if (s->scene.limitSpeedCamera > 29 && !s->scene.comma_stock_ui) {
    int img_speedlimit_growing_size_init = 0;
    int img_speedlimit_growing_size = 0;
    int img_speedlimit_size = 0;
    int img_speedlimit_x = 0;
    int img_speedlimit_y = 0;
    img_speedlimit_growing_size_init = (s->scene.limitSpeedCameraDist>600?600:s->scene.limitSpeedCameraDist);
    img_speedlimit_growing_size = 601 - img_speedlimit_growing_size_init;
    if (s->scene.limitSpeedCameraDist > 600) {img_speedlimit_growing_size = 300;}
    img_speedlimit_size = img_speedlimit_growing_size;
    img_speedlimit_x = s->viz_rect.centerX() - img_speedlimit_size/2;
    img_speedlimit_y = s->viz_rect.centerY() - img_speedlimit_size/2;
    float img_speedlimit_alpha = 0.35f;
    if(s->scene.car_state.getVEgo()*3.6 < 1 || s->scene.limitSpeedCameraDist > 600) {img_speedlimit_alpha = 0.1f;}
    if (s->scene.limitSpeedCamera < 40) {ui_draw_image(s, {img_speedlimit_x, img_speedlimit_y, img_speedlimit_size, img_speedlimit_size}, "speed_30", img_speedlimit_alpha);}
    else if (s->scene.limitSpeedCamera < 50) {ui_draw_image(s, {img_speedlimit_x, img_speedlimit_y, img_speedlimit_size, img_speedlimit_size}, "speed_40", img_speedlimit_alpha);}
    else if (s->scene.limitSpeedCamera < 60) {ui_draw_image(s, {img_speedlimit_x, img_speedlimit_y, img_speedlimit_size, img_speedlimit_size}, "speed_50", img_speedlimit_alpha);}
    else if (s->scene.limitSpeedCamera < 70) {ui_draw_image(s, {img_speedlimit_x, img_speedlimit_y, img_speedlimit_size, img_speedlimit_size}, "speed_60", img_speedlimit_alpha);}
    else if (s->scene.limitSpeedCamera < 80) {ui_draw_image(s, {img_speedlimit_x, img_speedlimit_y, img_speedlimit_size, img_speedlimit_size}, "speed_70", img_speedlimit_alpha);}
    else if (s->scene.limitSpeedCamera < 90) {ui_draw_image(s, {img_speedlimit_x, img_speedlimit_y, img_speedlimit_size, img_speedlimit_size}, "speed_80", img_speedlimit_alpha);}
    else if (s->scene.limitSpeedCamera < 100) {ui_draw_image(s, {img_speedlimit_x, img_speedlimit_y, img_speedlimit_size, img_speedlimit_size}, "speed_90", img_speedlimit_alpha);}
    else if (s->scene.limitSpeedCamera < 110) {ui_draw_image(s, {img_speedlimit_x, img_speedlimit_y, img_speedlimit_size, img_speedlimit_size}, "speed_100", img_speedlimit_alpha);}
    else if (s->scene.limitSpeedCamera < 120) {ui_draw_image(s, {img_speedlimit_x, img_speedlimit_y, img_speedlimit_size, img_speedlimit_size}, "speed_110", img_speedlimit_alpha);}
  }
  
  //draw compass by opkr
  if (s->scene.gpsAccuracyUblox != 0.00 && !s->scene.comma_stock_ui) {
    const int compass_x = s->viz_rect.x + s->viz_rect.w - 167 - (bdr_s);
    const int compass_y = (s->viz_rect.y + (bdr_s)) + 713;
    const int direction_x = compass_x + 74;
    const int direction_y = compass_y + 74;
    ui_draw_image(s, {compass_x, compass_y, 150, 150}, "compass", 0.6f);
    ui_draw_circle_image(s, direction_x, direction_y - (bdr_s+7), 90, "direction", nvgRGBA(0x0, 0x0, 0x0, 0x0), 0.6f, -(s->scene.bearingUblox));
  }

  // draw steering wheel
  const int bg_wheel_size = 90;
  const int bg_wheel_x = viz_event_x + (viz_event_w-bg_wheel_size);
  const int bg_wheel_y = viz_event_y + (bg_wheel_size/2);
  const QColor &color = bg_colors[s->status];
  NVGcolor nvg_color = nvgRGBA(color.red(), color.green(), color.blue(), color.alpha());
  if (s->scene.controls_state.getEnabled() || s->scene.forceGearD || s->scene.comma_stock_ui){
    float angleSteers = s->scene.car_state.getSteeringAngleDeg();
    ui_draw_circle_image(s, bg_wheel_x, bg_wheel_y+20, bg_wheel_size, "wheel", nvg_color, 1.0f, angleSteers);
  } else {
    if (!s->scene.comma_stock_ui) ui_draw_gear(s);
  }
  if (!s->scene.comma_stock_ui) ui_draw_debug(s);
}

static void ui_draw_vision_face(UIState *s) {
  const int radius = 85;
  const int center_x = s->viz_rect.x + radius + (bdr_s);
  const int center_y = s->viz_rect.bottom() - footer_h + ((footer_h - radius) / 2);
  ui_draw_circle_image(s, center_x, center_y, radius, "driver_face", s->scene.dm_active);
}

// Model Long does not work well. Sometimes it works unexpectedly. So it is disabled for now.
// static void ui_draw_ml_button(UIState *s) {
//   int btn_w = 140;
//   int btn_h = 140;
//   int btn_x = s->viz_rect.x + s->viz_rect.w - btn_w - 515;
//   int btn_y = 1080 - btn_h - 35;
//   int btn_xc = btn_x + (btn_w/2);
//   int btn_yc = btn_y + (btn_h/2);
//   nvgBeginPath(s->vg);
//   nvgRoundedRect(s->vg, btn_x, btn_y, btn_w, btn_h, 100);
//   if (s->scene.mlButtonEnabled) {
//     nvgStrokeColor(s->vg, nvgRGBA(55, 184, 104, 255));
//   } else {
//     nvgStrokeColor(s->vg, nvgRGBA(255,10,10,80));
//   }
//   nvgStrokeWidth(s->vg, 6);
//   nvgStroke(s->vg);

//   nvgTextAlign(s->vg, NVG_ALIGN_CENTER | NVG_ALIGN_MIDDLE);
//   nvgFontSize(s->vg, 45);
//   if (s->scene.mlButtonEnabled) {
//     nvgFillColor(s->vg, nvgRGBA(55, 184, 104, 255));
//     nvgFontSize(s->vg, 55);
//     nvgText(s->vg,btn_xc,btn_yc,"MDL",NULL);
//   } else {
//     nvgFillColor(s->vg, nvgRGBA(255,255,255,200));
//     nvgText(s->vg,btn_xc,btn_yc,"MDL",NULL);
//   }
// }

//BB START: functions added for the display of various items
static int bb_ui_draw_measure(UIState *s, const char* bb_value, const char* bb_uom, const char* bb_label,
    int bb_x, int bb_y, int bb_uom_dx,
    NVGcolor bb_valueColor, NVGcolor bb_labelColor, NVGcolor bb_uomColor,
    int bb_valueFontSize, int bb_labelFontSize, int bb_uomFontSize )  {
  nvgTextAlign(s->vg, NVG_ALIGN_CENTER | NVG_ALIGN_BASELINE);
  int dx = 0;
  if (strlen(bb_uom) > 0) {
    dx = (int)(bb_uomFontSize*2.5/2);
   }
  //print value
  nvgFontFace(s->vg, "sans-semibold");
  nvgFontSize(s->vg, bb_valueFontSize*2.5);
  nvgFillColor(s->vg, bb_valueColor);
  nvgText(s->vg, bb_x-dx/2, bb_y+ (int)(bb_valueFontSize*2.5)+5, bb_value, NULL);
  //print label
  nvgFontFace(s->vg, "sans-regular");
  nvgFontSize(s->vg, bb_labelFontSize*2.5);
  nvgFillColor(s->vg, bb_labelColor);
  nvgText(s->vg, bb_x, bb_y + (int)(bb_valueFontSize*2.5)+5 + (int)(bb_labelFontSize*2.5)+5, bb_label, NULL);
  //print uom
  if (strlen(bb_uom) > 0) {
      nvgSave(s->vg);
    int rx =bb_x + bb_uom_dx + bb_valueFontSize -3;
    int ry = bb_y + (int)(bb_valueFontSize*2.5/2)+25;
    nvgTranslate(s->vg,rx,ry);
    nvgRotate(s->vg, -1.5708); //-90deg in radians
    nvgFontFace(s->vg, "sans-regular");
    nvgFontSize(s->vg, (int)(bb_uomFontSize*2.5));
    nvgFillColor(s->vg, bb_uomColor);
    nvgText(s->vg, 0, 0, bb_uom, NULL);
    nvgRestore(s->vg);
  }
  return (int)((bb_valueFontSize + bb_labelFontSize)*2.5) + 5;
}

static void bb_ui_draw_measures_left(UIState *s, int bb_x, int bb_y, int bb_w ) {
  const UIScene *scene = &s->scene;
  int bb_rx = bb_x + (int)(bb_w/2);
  int bb_ry = bb_y;
  int bb_h = 5;
  NVGcolor lab_color = COLOR_WHITE_ALPHA(200);
  NVGcolor uom_color = COLOR_WHITE_ALPHA(200);
  int value_fontSize=30*0.8;
  int label_fontSize=15*0.8;
  int uom_fontSize = 15*0.8;
  int bb_uom_dx =  (int)(bb_w /2 - uom_fontSize*2.5) ;
  //CPU TEMP
  if (true) {
    //char val_str[16];
    char uom_str[6];
    std::string cpu_temp_val = std::to_string(int(s->scene.cpuTemp)) + "°C";
    NVGcolor val_color = COLOR_WHITE_ALPHA(200);
    //snprintf(val_str, sizeof(val_str), "%.0fC", (round(s->scene.cpuTemp)));
    snprintf(uom_str, sizeof(uom_str), "%d%%", (s->scene.cpuPerc));
    bb_h +=bb_ui_draw_measure(s, cpu_temp_val.c_str(), uom_str, "CPU 온도",
        bb_rx, bb_ry, bb_uom_dx,
        val_color, lab_color, uom_color,
        value_fontSize, label_fontSize, uom_fontSize );
    bb_ry = bb_y + bb_h;
  }
  //BAT TEMP
  if (true) {
    //char val_str[16];
    char uom_str[6];
    NVGcolor val_color = COLOR_WHITE_ALPHA(200);
    float batteryTemp = scene->deviceState.getBatteryTempC();
    std::string bat_temp_val = std::to_string(int(batteryTemp)) + "°C";
    if(batteryTemp > 40.f) {
      val_color = nvgRGBA(255, 188, 3, 200);
    }
    if(batteryTemp > 50.f) {
      val_color = nvgRGBA(255, 0, 0, 200);
    }
    // temp is alway in C * 1000
    //snprintf(val_str, sizeof(val_str), "%.0fC", batteryTemp);
    snprintf(uom_str, sizeof(uom_str), "%d", (s->scene.fanSpeed)/1000);
    bb_h +=bb_ui_draw_measure(s, bat_temp_val.c_str(), uom_str, "배터리온도",
        bb_rx, bb_ry, bb_uom_dx,
        val_color, lab_color, uom_color,
        value_fontSize, label_fontSize, uom_fontSize );
    bb_ry = bb_y + bb_h;
  }
  //BAT LEVEL
  if(true) {
    char val_str[16];
    char uom_str[6];
    NVGcolor val_color = COLOR_WHITE_ALPHA(200);
    int batteryPercent = scene->deviceState.getBatteryPercent();
    snprintf(val_str, sizeof(val_str), "%d%%", batteryPercent);
    snprintf(uom_str, sizeof(uom_str), "%s", scene->deviceState.getBatteryStatus() == "Charging" ? "++" : "--");
    bb_h +=bb_ui_draw_measure(s, val_str, uom_str, "배터리레벨",
        bb_rx, bb_ry, bb_uom_dx,
        val_color, lab_color, uom_color,
        value_fontSize, label_fontSize, uom_fontSize );
    bb_ry = bb_y + bb_h;
  }
  //add Ublox GPS accuracy
  if (scene->gpsAccuracyUblox != 0.00) {
    char val_str[16];
    char uom_str[3];
    NVGcolor val_color = COLOR_WHITE_ALPHA(200);
    //show red/orange if gps accuracy is low
      if(scene->gpsAccuracyUblox > 0.85) {
         val_color = COLOR_ORANGE_ALPHA(200);
      }
      if(scene->gpsAccuracyUblox > 1.3) {
         val_color = COLOR_RED_ALPHA(200);
      }
    // gps accuracy is always in meters
    if(scene->gpsAccuracyUblox > 99 || scene->gpsAccuracyUblox == 0) {
       snprintf(val_str, sizeof(val_str), "None");
    }else if(scene->gpsAccuracyUblox > 9.99) {
      snprintf(val_str, sizeof(val_str), "%.1f", (s->scene.gpsAccuracyUblox));
    }
    else {
      snprintf(val_str, sizeof(val_str), "%.2f", (s->scene.gpsAccuracyUblox));
    }
    snprintf(uom_str, sizeof(uom_str), "%d", (s->scene.satelliteCount));
    bb_h +=bb_ui_draw_measure(s,  val_str, uom_str, "GPS 정확도",
        bb_rx, bb_ry, bb_uom_dx,
        val_color, lab_color, uom_color,
        value_fontSize, label_fontSize, uom_fontSize );
    bb_ry = bb_y + bb_h;
  }
  //add altitude
  if (scene->gpsAccuracyUblox != 0.00) {
    char val_str[16];
    char uom_str[3];
    NVGcolor val_color = COLOR_WHITE_ALPHA(200);
    snprintf(val_str, sizeof(val_str), "%.0f", (s->scene.altitudeUblox));
    snprintf(uom_str, sizeof(uom_str), "m");
    bb_h +=bb_ui_draw_measure(s,  val_str, uom_str, "고도",
        bb_rx, bb_ry, bb_uom_dx,
        val_color, lab_color, uom_color,
        value_fontSize, label_fontSize, uom_fontSize );
    bb_ry = bb_y + bb_h;
  }

  //finally draw the frame
  bb_h += 20;
  nvgBeginPath(s->vg);
    nvgRoundedRect(s->vg, bb_x, bb_y, bb_w, bb_h, 20);
    nvgStrokeColor(s->vg, COLOR_WHITE_ALPHA(80));
    nvgStrokeWidth(s->vg, 6);
    nvgStroke(s->vg);
}

static void bb_ui_draw_measures_right(UIState *s, int bb_x, int bb_y, int bb_w ) {
  const UIScene *scene = &s->scene;
  int bb_rx = bb_x + (int)(bb_w/2);
  int bb_ry = bb_y;
  int bb_h = 5;
  NVGcolor lab_color = COLOR_WHITE_ALPHA(200);
  NVGcolor uom_color = COLOR_WHITE_ALPHA(200);
  int value_fontSize=30*0.8;
  int label_fontSize=15*0.8;
  int uom_fontSize = 15*0.8;
  int bb_uom_dx =  (int)(bb_w /2 - uom_fontSize*2.5) ;

  //add visual radar relative distance
  if (true) {
    char val_str[16];
    char uom_str[6];
    NVGcolor val_color = COLOR_WHITE_ALPHA(200);
    if (scene->lead_data[0].getStatus()) {
      //show RED if less than 5 meters
      //show orange if less than 15 meters
      if((int)(scene->lead_data[0].getDRel()) < 15) {
        val_color = COLOR_ORANGE_ALPHA(200);
      }
      if((int)(scene->lead_data[0].getDRel()) < 5) {
        val_color = COLOR_RED_ALPHA(200);
      }
      // lead car relative distance is always in meters
      if((float)(scene->lead_data[0].getDRel()) < 10) {
        snprintf(val_str, sizeof(val_str), "%.1f", (float)scene->lead_data[0].getDRel());
      } else {
        snprintf(val_str, sizeof(val_str), "%d", (int)scene->lead_data[0].getDRel());
      }

    } else {
       snprintf(val_str, sizeof(val_str), "-");
    }
    snprintf(uom_str, sizeof(uom_str), "m");
    bb_h +=bb_ui_draw_measure(s,  val_str, uom_str, "차간거리",
        bb_rx, bb_ry, bb_uom_dx,
        val_color, lab_color, uom_color,
        value_fontSize, label_fontSize, uom_fontSize );
    bb_ry = bb_y + bb_h;
  }
  //add visual radar relative speed
  if (true) {
    char val_str[16];
    char uom_str[6];
    NVGcolor val_color = COLOR_WHITE_ALPHA(200);
    if (scene->lead_data[0].getStatus()) {
      //show Orange if negative speed (approaching)
      //show Orange if negative speed faster than 5mph (approaching fast)
      if((int)(scene->lead_data[0].getVRel()) < 0) {
        val_color = nvgRGBA(255, 188, 3, 200);
      }
      if((int)(scene->lead_data[0].getVRel()) < -5) {
        val_color = nvgRGBA(255, 0, 0, 200);
      }
      // lead car relative speed is always in meters
      if (s->scene.is_metric) {
         snprintf(val_str, sizeof(val_str), "%d", (int)(scene->lead_data[0].getVRel() * 3.6 + 0.5));
      } else {
         snprintf(val_str, sizeof(val_str), "%d", (int)(scene->lead_data[0].getVRel() * 2.2374144 + 0.5));
      }
    } else {
       snprintf(val_str, sizeof(val_str), "-");
    }
    if (s->scene.is_metric) {
      snprintf(uom_str, sizeof(uom_str), "km/h");;
    } else {
      snprintf(uom_str, sizeof(uom_str), "mi/h");
    }
    bb_h +=bb_ui_draw_measure(s,  val_str, uom_str, "상대속도",
        bb_rx, bb_ry, bb_uom_dx,
        val_color, lab_color, uom_color,
        value_fontSize, label_fontSize, uom_fontSize );
    bb_ry = bb_y + bb_h;
  }
  //add steering angle
  if (true) {
    char val_str[16];
    char uom_str[6];
    //std::string angle_val = std::to_string(int(s->scene.angleSteers*10)/10) + "°";
    NVGcolor val_color = COLOR_GREEN_ALPHA(200);
    //show Orange if more than 30 degrees
    //show red if  more than 50 degrees
    if(((int)(s->scene.angleSteers) < -30) || ((int)(scene->angleSteers) > 30)) {
      val_color = COLOR_ORANGE_ALPHA(200);
    }
    if(((int)(s->scene.angleSteers) < -50) || ((int)(scene->angleSteers) > 50)) {
      val_color = COLOR_RED_ALPHA(200);
    }
    // steering is in degrees
    snprintf(val_str, sizeof(val_str), "%.1f°",(s->scene.angleSteers));
    snprintf(uom_str, sizeof(uom_str), "   °");

    bb_h +=bb_ui_draw_measure(s, val_str, uom_str, "현재조향각",
        bb_rx, bb_ry, bb_uom_dx,
        val_color, lab_color, uom_color,
        value_fontSize, label_fontSize, uom_fontSize );
    bb_ry = bb_y + bb_h;
  }

  //add desired steering angle
  if (true) {
    char val_str[16];
    char uom_str[6];
    //std::string desire_val;
    NVGcolor val_color = COLOR_WHITE_ALPHA(200);
    if (scene->controls_state.getEnabled()) {
      //show Orange if more than 30 degrees
      //show red if  more than 50 degrees
      if(((int)(s->scene.angleSteersDes) < -30) || ((int)(scene->angleSteersDes) > 30)) {
        val_color = COLOR_WHITE_ALPHA(200);
      }
      if(((int)(s->scene.angleSteersDes) < -50) || ((int)(scene->angleSteersDes) > 50)) {
        val_color = COLOR_WHITE_ALPHA(200);
      }
      // steering is in degrees
      snprintf(val_str, sizeof(val_str), "%.1f°",(s->scene.angleSteersDes));
      //desire_val = std::to_string(int(s->scene.angleSteersDes*10)/10) + "°";
    } else {
      snprintf(val_str, sizeof(val_str), "-");
      //desire_val = "-";
    }
    snprintf(uom_str, sizeof(uom_str), "   °");

    bb_h +=bb_ui_draw_measure(s, val_str, uom_str, "필요조향각",
        bb_rx, bb_ry, bb_uom_dx,
        val_color, lab_color, uom_color,
        value_fontSize, label_fontSize, uom_fontSize );
    bb_ry = bb_y + bb_h;
  }

  //add steerratio from lateralplan
  if (true) {
    char val_str[16];
    char uom_str[6];
    NVGcolor val_color = COLOR_WHITE_ALPHA(200);
    if (scene->controls_state.getEnabled()) {
      snprintf(val_str, sizeof(val_str), "%.2f",(s->scene.steerRatio));
    } else {
       snprintf(val_str, sizeof(val_str), "-");
    }
      snprintf(uom_str, sizeof(uom_str), "");
    bb_h +=bb_ui_draw_measure(s,  val_str, uom_str, "SteerRatio",
        bb_rx, bb_ry, bb_uom_dx,
        val_color, lab_color, uom_color,
        value_fontSize, label_fontSize, uom_fontSize );
    bb_ry = bb_y + bb_h;
  }

  //finally draw the frame
  bb_h += 20;
  nvgBeginPath(s->vg);
  nvgRoundedRect(s->vg, bb_x, bb_y, bb_w, bb_h, 20);
  nvgStrokeColor(s->vg, COLOR_WHITE_ALPHA(80));
  nvgStrokeWidth(s->vg, 6);
  nvgStroke(s->vg);
}

//BB END: functions added for the display of various items

static void bb_ui_draw_UI(UIState *s) {
  const int bb_dml_w = 180;
  const int bb_dml_x = (s->viz_rect.x + (bdr_s));
  const int bb_dml_y = (s->viz_rect.y + (bdr_s)) + 220;

  const int bb_dmr_w = 180;
  const int bb_dmr_x = s->viz_rect.x + s->viz_rect.w - bb_dmr_w - (bdr_s);
  const int bb_dmr_y = (s->viz_rect.y + (bdr_s)) + 220;

  bb_ui_draw_measures_right(s, bb_dml_x, bb_dml_y, bb_dml_w);
  bb_ui_draw_measures_left(s, bb_dmr_x, bb_dmr_y-20, bb_dmr_w);
}

static void draw_navi_button(UIState *s) {
  if (s->vipc_client->connected || s->is_OpenpilotViewEnabled) {
    int btn_w = 140;
    int btn_h = 140;
    int btn_x1 = s->viz_rect.x + s->viz_rect.w - btn_w - 195;
    int btn_y = 1080 - btn_h - 35;
    int btn_xc1 = btn_x1 + (btn_w/2);
    int btn_yc = btn_y + (btn_h/2);
    nvgTextAlign(s->vg, NVG_ALIGN_CENTER | NVG_ALIGN_MIDDLE);
    nvgBeginPath(s->vg);
    nvgRoundedRect(s->vg, btn_x1, btn_y, btn_w, btn_h, 100);
    nvgStrokeColor(s->vg, nvgRGBA(255,255,255,80));
    nvgStrokeWidth(s->vg, 6);
    nvgStroke(s->vg);
    nvgFontSize(s->vg, 45);
    nvgFillColor(s->vg, nvgRGBA(255,255,255,200));
    nvgText(s->vg,btn_xc1,btn_yc,"NAVI",NULL);
  }
}

static void draw_laneless_button(UIState *s) {
  if (s->vipc_client->connected || s->is_OpenpilotViewEnabled) {
    int btn_w = 140;
    int btn_h = 140;
    int btn_x1 = s->viz_rect.x + s->viz_rect.w - btn_w - 355;
    int btn_y = 1080 - btn_h - 35;
    int btn_xc1 = btn_x1 + (btn_w/2);
    int btn_yc = btn_y + (btn_h/2);
    nvgTextAlign(s->vg, NVG_ALIGN_CENTER | NVG_ALIGN_MIDDLE);
    nvgBeginPath(s->vg);
    nvgRoundedRect(s->vg, btn_x1, btn_y, btn_w, btn_h, 100);
    nvgStrokeColor(s->vg, nvgRGBA(255,255,255,80));
    nvgStrokeWidth(s->vg, 6);
    nvgStroke(s->vg);
    nvgFontSize(s->vg, 45);
    if (s->scene.lateralPlan.lanelessModeStatus) {
      NVGcolor fillColor = nvgRGBA(0,255,0,80);
      nvgFillColor(s->vg, fillColor);
      nvgFill(s->vg);
    }
    nvgFillColor(s->vg, nvgRGBA(255,255,255,200));
    if (s->scene.laneless_mode == 0) {
      nvgText(s->vg,btn_xc1,btn_yc,"OFF",NULL);
    } else if (s->scene.laneless_mode == 1) {
      nvgText(s->vg,btn_xc1,btn_yc,"ON",NULL);
    } else if (s->scene.laneless_mode == 2) {
      nvgText(s->vg,btn_xc1,btn_yc,"AUTO",NULL);
    }
  }
}

static void ui_draw_vision_header(UIState *s) {
  NVGpaint gradient = nvgLinearGradient(s->vg, s->viz_rect.x,
                        s->viz_rect.y+(header_h-(header_h/2.5)),
                        s->viz_rect.x, s->viz_rect.y+header_h,
                        nvgRGBAf(0,0,0,0.45), nvgRGBAf(0,0,0,0));

  ui_fill_rect(s->vg, {s->viz_rect.x, s->viz_rect.y, s->viz_rect.w, header_h}, gradient);

  if (!s->scene.comma_stock_ui) {
    ui_draw_vision_maxspeed(s);
    ui_draw_vision_cruise_speed(s);
  } else {
    ui_draw_vision_maxspeed_org(s);
  }
  ui_draw_vision_speed(s);
  ui_draw_vision_event(s);
  if (!s->scene.comma_stock_ui) {
    bb_ui_draw_UI(s);
    ui_draw_tpms(s);
    draw_navi_button(s);
  }
  if (s->scene.end_to_end && !s->scene.comma_stock_ui) {
    draw_laneless_button(s);
  }
  if (s->scene.controls_state.getEnabled() && !s->scene.comma_stock_ui) {
    ui_draw_standstill(s);
  }
}

//blind spot warning by OPKR
static void ui_draw_vision_car(UIState *s) {
  const UIScene *scene = &s->scene;
  const int car_size = 350;
  const int car_x_left = (s->viz_rect.centerX() - 400);
  const int car_x_right = (s->viz_rect.centerX() + 400);
  const int car_y = 500;
  const int car_img_size_w = (car_size * 1);
  const int car_img_size_h = (car_size * 1);
  const int car_img_x_left = (car_x_left - (car_img_size_w / 2));
  const int car_img_x_right = (car_x_right - (car_img_size_w / 2));
  const int car_img_y = (car_y - (car_size / 4));

  int car_valid_status = 0;
  bool car_valid_left = scene->leftblindspot;
  bool car_valid_right = scene->rightblindspot;
  float car_img_alpha;
  if (s->nOpkrBlindSpotDetect) {
    if (s->scene.car_valid_status_changed != car_valid_status) {
      s->scene.blindspot_blinkingrate = 114;
      s->scene.car_valid_status_changed = car_valid_status;
    }
    if (car_valid_left || car_valid_right) {
      if (!car_valid_left && car_valid_right) {
        car_valid_status = 1;
      } else if (car_valid_left && !car_valid_right) {
        car_valid_status = 2;
      } else if (car_valid_left && car_valid_right) {
        car_valid_status = 3;
      } else {
        car_valid_status = 0;
      }
      s->scene.blindspot_blinkingrate -= 6;
      if(scene->blindspot_blinkingrate<0) s->scene.blindspot_blinkingrate = 120;
      if (scene->blindspot_blinkingrate>=60) {
        car_img_alpha = 0.6f;
      } else {
        car_img_alpha = 0.0f;
      }
    } else {
      s->scene.blindspot_blinkingrate = 120;
    }

    if(car_valid_left) {
      ui_draw_image(s, {car_img_x_left, car_img_y, car_img_size_w, car_img_size_h}, "car_left", car_img_alpha);
    }
    if(car_valid_right) {
      ui_draw_image(s, {car_img_x_right, car_img_y, car_img_size_w, car_img_size_h}, "car_right", car_img_alpha);
    }
  }
}

static void ui_draw_vision_frame(UIState *s) {
  // Draw video frames
  glEnable(GL_SCISSOR_TEST);
  glViewport(s->video_rect.x, s->video_rect.y, s->video_rect.w, s->video_rect.h);
  glScissor(s->viz_rect.x, s->viz_rect.y, s->viz_rect.w, s->viz_rect.h);
  draw_frame(s);
  glDisable(GL_SCISSOR_TEST);

  glViewport(0, 0, s->fb_w, s->fb_h);
}

static void ui_draw_vision(UIState *s) {
  const UIScene *scene = &s->scene;
  // Draw augmented elements
  if (scene->world_objects_visible) {
    ui_draw_world(s);
  }
  // Set Speed, Current Speed, Status/Events
  ui_draw_vision_header(s);
  if ((*s->sm)["controlsState"].getControlsState().getAlertSize() == cereal::ControlsState::AlertSize::NONE) {
    ui_draw_vision_face(s);
    if (!s->scene.comma_stock_ui) {
      ui_draw_vision_car(s);
    }
  }
}

static void ui_draw_background(UIState *s) {
  const QColor &color = bg_colors[s->status];
  glClearColor(color.redF(), color.greenF(), color.blueF(), 1.0);
  glClear(GL_STENCIL_BUFFER_BIT | GL_COLOR_BUFFER_BIT);
}

void ui_draw(UIState *s, int w, int h) {
  s->viz_rect = Rect{bdr_s, bdr_s, w - 2 * bdr_s, h - 2 * bdr_s};

  const bool draw_vision = s->scene.started && s->vipc_client->connected;

  // GL drawing functions
  ui_draw_background(s);
  if (draw_vision) {
    ui_draw_vision_frame(s);
  }
  glEnable(GL_BLEND);
  glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
  glViewport(0, 0, s->fb_w, s->fb_h);

  // NVG drawing functions - should be no GL inside NVG frame
  nvgBeginFrame(s->vg, s->fb_w, s->fb_h, 1.0f);

  if (draw_vision) {
    ui_draw_vision(s);
  }

  nvgEndFrame(s->vg);
  glDisable(GL_BLEND);
}

void ui_draw_image(const UIState *s, const Rect &r, const char *name, float alpha) {
  nvgBeginPath(s->vg);
  NVGpaint imgPaint = nvgImagePattern(s->vg, r.x, r.y, r.w, r.h, 0, s->images.at(name), alpha);
  nvgRect(s->vg, r.x, r.y, r.w, r.h);
  nvgFillPaint(s->vg, imgPaint);
  nvgFill(s->vg);
}

void ui_draw_rect(NVGcontext *vg, const Rect &r, NVGcolor color, int width, float radius) {
  nvgBeginPath(vg);
  radius > 0 ? nvgRoundedRect(vg, r.x, r.y, r.w, r.h, radius) : nvgRect(vg, r.x, r.y, r.w, r.h);
  nvgStrokeColor(vg, color);
  nvgStrokeWidth(vg, width);
  nvgStroke(vg);
}

static inline void fill_rect(NVGcontext *vg, const Rect &r, const NVGcolor *color, const NVGpaint *paint, float radius) {
  nvgBeginPath(vg);
  radius > 0 ? nvgRoundedRect(vg, r.x, r.y, r.w, r.h, radius) : nvgRect(vg, r.x, r.y, r.w, r.h);
  if (color) nvgFillColor(vg, *color);
  if (paint) nvgFillPaint(vg, *paint);
  nvgFill(vg);
}
void ui_fill_rect(NVGcontext *vg, const Rect &r, const NVGcolor &color, float radius) {
  fill_rect(vg, r, &color, nullptr, radius);
}
void ui_fill_rect(NVGcontext *vg, const Rect &r, const NVGpaint &paint, float radius) {
  fill_rect(vg, r, nullptr, &paint, radius);
}

static const char frame_vertex_shader[] =
#ifdef NANOVG_GL3_IMPLEMENTATION
  "#version 150 core\n"
#else
  "#version 300 es\n"
#endif
  "in vec4 aPosition;\n"
  "in vec4 aTexCoord;\n"
  "uniform mat4 uTransform;\n"
  "out vec4 vTexCoord;\n"
  "void main() {\n"
  "  gl_Position = uTransform * aPosition;\n"
  "  vTexCoord = aTexCoord;\n"
  "}\n";

static const char frame_fragment_shader[] =
#ifdef NANOVG_GL3_IMPLEMENTATION
  "#version 150 core\n"
#else
  "#version 300 es\n"
#endif
  "precision mediump float;\n"
  "uniform sampler2D uTexture;\n"
  "in vec4 vTexCoord;\n"
  "out vec4 colorOut;\n"
  "void main() {\n"
  "  colorOut = texture(uTexture, vTexCoord.xy);\n"
#ifdef QCOM
  "  vec3 dz = vec3(0.0627f, 0.0627f, 0.0627f);\n"
  "  colorOut.rgb = ((vec3(1.0f, 1.0f, 1.0f) - dz) * colorOut.rgb / vec3(1.0f, 1.0f, 1.0f)) + dz;\n"
#endif
  "}\n";

static const mat4 device_transform = {{
  1.0,  0.0, 0.0, 0.0,
  0.0,  1.0, 0.0, 0.0,
  0.0,  0.0, 1.0, 0.0,
  0.0,  0.0, 0.0, 1.0,
}};

void ui_nvg_init(UIState *s) {
  // init drawing

  // on EON, we enable MSAA
  s->vg = Hardware::EON() ? nvgCreate(0) : nvgCreate(NVG_ANTIALIAS | NVG_STENCIL_STROKES | NVG_DEBUG);
  assert(s->vg);

  // init fonts
  std::pair<const char *, const char *> fonts[] = {
      {"sans-regular", "../assets/fonts/opensans_regular.ttf"},
      {"sans-semibold", "../assets/fonts/opensans_semibold.ttf"},
      {"sans-bold", "../assets/fonts/opensans_bold.ttf"},
  };
  for (auto [name, file] : fonts) {
    int font_id = nvgCreateFont(s->vg, name, file);
    assert(font_id >= 0);
  }

  // init images
  std::vector<std::pair<const char *, const char *>> images = {
    {"wheel", "../assets/img_chffr_wheel.png"},
    {"driver_face", "../assets/img_driver_face.png"},
    {"speed_30", "../assets/img_30_speedahead.png"},
    {"speed_40", "../assets/img_40_speedahead.png"},
    {"speed_50", "../assets/img_50_speedahead.png"},
    {"speed_60", "../assets/img_60_speedahead.png"},
    {"speed_70", "../assets/img_70_speedahead.png"},
    {"speed_80", "../assets/img_80_speedahead.png"},
    {"speed_90", "../assets/img_90_speedahead.png"},
    {"speed_100", "../assets/img_100_speedahead.png"},
    {"speed_110", "../assets/img_110_speedahead.png"},
    {"car_left", "../assets/img_car_left.png"},
    {"car_right", "../assets/img_car_right.png"},
    {"compass", "../assets/img_compass.png"},
    {"direction", "../assets/img_direction.png"},
  };
  for (auto [name, file] : images) {
    s->images[name] = nvgCreateImage(s->vg, file, 1);
    assert(s->images[name] != 0);
  }

  // init gl
  s->gl_shader = std::make_unique<GLShader>(frame_vertex_shader, frame_fragment_shader);
  GLint frame_pos_loc = glGetAttribLocation(s->gl_shader->prog, "aPosition");
  GLint frame_texcoord_loc = glGetAttribLocation(s->gl_shader->prog, "aTexCoord");

  glViewport(0, 0, s->fb_w, s->fb_h);

  glDisable(GL_DEPTH_TEST);

  assert(glGetError() == GL_NO_ERROR);

  float x1 = 1.0, x2 = 0.0, y1 = 1.0, y2 = 0.0;
  const uint8_t frame_indicies[] = {0, 1, 2, 0, 2, 3};
  const float frame_coords[4][4] = {
    {-1.0, -1.0, x2, y1}, //bl
    {-1.0,  1.0, x2, y2}, //tl
    { 1.0,  1.0, x1, y2}, //tr
    { 1.0, -1.0, x1, y1}, //br
  };

  glGenVertexArrays(1, &s->frame_vao);
  glBindVertexArray(s->frame_vao);
  glGenBuffers(1, &s->frame_vbo);
  glBindBuffer(GL_ARRAY_BUFFER, s->frame_vbo);
  glBufferData(GL_ARRAY_BUFFER, sizeof(frame_coords), frame_coords, GL_STATIC_DRAW);
  glEnableVertexAttribArray(frame_pos_loc);
  glVertexAttribPointer(frame_pos_loc, 2, GL_FLOAT, GL_FALSE,
                        sizeof(frame_coords[0]), (const void *)0);
  glEnableVertexAttribArray(frame_texcoord_loc);
  glVertexAttribPointer(frame_texcoord_loc, 2, GL_FLOAT, GL_FALSE,
                        sizeof(frame_coords[0]), (const void *)(sizeof(float) * 2));
  glGenBuffers(1, &s->frame_ibo);
  glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, s->frame_ibo);
  glBufferData(GL_ELEMENT_ARRAY_BUFFER, sizeof(frame_indicies), frame_indicies, GL_STATIC_DRAW);
  glBindBuffer(GL_ARRAY_BUFFER, 0);
  glBindVertexArray(0);

  ui_resize(s, s->fb_w, s->fb_h);
}

void ui_resize(UIState *s, int width, int height){
  s->fb_w = width;
  s->fb_h = height;

  auto intrinsic_matrix = s->wide_camera ? ecam_intrinsic_matrix : fcam_intrinsic_matrix;

  s->zoom = zoom / intrinsic_matrix.v[0];

  if (s->wide_camera) {
    s->zoom *= 0.5;
  }

  s->video_rect = Rect{bdr_s, bdr_s, s->fb_w - 2 * bdr_s, s->fb_h - 2 * bdr_s};
  float zx = s->zoom * 2 * intrinsic_matrix.v[2] / s->video_rect.w;
  float zy = s->zoom * 2 * intrinsic_matrix.v[5] / s->video_rect.h;

  const mat4 frame_transform = {{
    zx, 0.0, 0.0, 0.0,
    0.0, zy, 0.0, -y_offset / s->video_rect.h * 2,
    0.0, 0.0, 1.0, 0.0,
    0.0, 0.0, 0.0, 1.0,
  }};

  s->rear_frame_mat = matmul(device_transform, frame_transform);

  // Apply transformation such that video pixel coordinates match video
  // 1) Put (0, 0) in the middle of the video
  nvgTranslate(s->vg, s->video_rect.x + s->video_rect.w / 2, s->video_rect.y + s->video_rect.h / 2 + y_offset);

  // 2) Apply same scaling as video
  nvgScale(s->vg, s->zoom, s->zoom);

  // 3) Put (0, 0) in top left corner of video
  nvgTranslate(s->vg, -intrinsic_matrix.v[2], -intrinsic_matrix.v[5]);

  nvgCurrentTransform(s->vg, s->car_space_transform);
  nvgResetTransform(s->vg);
}
