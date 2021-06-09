#include <time.h>
#include <dirent.h>
#include <sys/types.h>
#include <sys/stat.h>
#include "ui.h"

#define CAPTURE_STATE_NONE 0
#define CAPTURE_STATE_CAPTURING 1
#define CAPTURE_STATE_NOT_CAPTURING 2
#define CAPTURE_STATE_PAUSED 3
#define CLICK_TIME 0.2
#define RECORD_INTERVAL 180 // Time in seconds to rotate recordings; Max for screenrecord is 3 minutes
#define RECORD_FILES 200 // Limitation of file count. Approximately 70MB * 200 = 14GB

typedef struct dashcam_element {
  int pos_x;
  int pos_y;
  int width;
  int height;
} dashcam_element;

int captureState = CAPTURE_STATE_NOT_CAPTURING;
int captureNum = 0;
int start_time = 0;
int elapsed_time = 0; // Time of current recording
int click_elapsed_time = 0;
int click_time = 0;
char filenames[RECORD_FILES][50]; // Track the filenames so they can be deleted when rotating

bool lock_current_video = false; // If true save the current video before rotating
bool locked_files[RECORD_FILES]; // Track which files are locked
int files_created = 0;

int get_time() {
  // Get current time (in seconds)

  int iRet;
  struct timeval tv;
  int seconds = 0;

  iRet = gettimeofday(&tv,NULL);
  if (iRet == 0) {
    seconds = (int)tv.tv_sec;
  }
  return seconds;
}

struct tm get_time_struct() {
  time_t t = time(NULL);
  struct tm tm = *localtime(&t);
  return tm;
}

void remove_file(char *videos_dir, char *filename) {
  if (filename[0] == '\0') {
    // Don't do anything if no filename is passed
    return;
  }

  int status;
  char fullpath[64];
  snprintf(fullpath,sizeof(fullpath),"%s/%s", videos_dir, filename);
  status = remove(fullpath);
  if (status == 0) {
    printf("Removed file: %s\n", fullpath);
  }
  else {
    printf("Unable to remove file: %s\n", fullpath);
    perror("Error message:");
  }
}

void save_file(char *videos_dir, char *filename) {
  if (!strlen(filename)) {
    return;
  }

  // Rename file to save it from being overwritten
  char cmd[128];
  snprintf(cmd,sizeof(cmd), "mv %s/%s %s/saved_%s", videos_dir, filename, videos_dir, filename);
  printf("save: %s\n",cmd);
  system(cmd);
}

void stop_capture() {
  char videos_dir[50] = "/storage/emulated/0/videos";

  if (captureState == CAPTURE_STATE_CAPTURING) {
    system("killall -SIGINT screenrecord");
    captureState = CAPTURE_STATE_NOT_CAPTURING;
    elapsed_time = get_time() - start_time;
    if (elapsed_time < 3) {
      remove_file(videos_dir, filenames[captureNum]);
    } else {
      //printf("Stop capturing screen\n");
      captureNum++;

      if (captureNum > RECORD_FILES-1) {
        captureNum = 0;
      }
    }
  }
}

void start_capture(UIState *s) {
  captureState = CAPTURE_STATE_CAPTURING;
  char cmd[128] = "";
  char purge[128] = "";
  char videos_dir[50] = "/storage/emulated/0/videos";

  //////////////////////////////////
  // NOTE: make sure videos_dir folder exists on the device!
  //////////////////////////////////
  struct stat st = {0};
  if (stat(videos_dir, &st) == -1) {
    mkdir(videos_dir,0700);
  }

  if (strlen(filenames[captureNum]) && files_created >= RECORD_FILES) {
    if (locked_files[captureNum] > 0) {
      save_file(videos_dir, filenames[captureNum]);
    }
    else {
      // remove the old file
      remove_file(videos_dir, filenames[captureNum]);
    }
    locked_files[captureNum] = 0;
  }

  char filename[64];
  struct tm tm = get_time_struct();
  snprintf(filename,sizeof(filename),"%04d%02d%02d-%02d%02d%02d.mp4", tm.tm_year + 1900, tm.tm_mon + 1, tm.tm_mday, tm.tm_hour, tm.tm_min, tm.tm_sec);
  if (s->scene.recording_quality == 0) {
    snprintf(cmd,sizeof(cmd),"screenrecord --size 800x450 --bit-rate 2000000 %s/%s&",videos_dir,filename);
  } else if (s->scene.recording_quality == 1) {
    snprintf(cmd,sizeof(cmd),"screenrecord --size 960x540 --bit-rate 3000000 %s/%s&",videos_dir,filename);
  } else if (s->scene.recording_quality == 2) {
    snprintf(cmd,sizeof(cmd),"screenrecord --size 1280x720 --bit-rate 4000000 %s/%s&",videos_dir,filename);
  } else {
    snprintf(cmd,sizeof(cmd),"screenrecord --size 1920x1080 --bit-rate 5000000 %s/%s&",videos_dir,filename);
  }
  strcpy(filenames[captureNum],filename);

  printf("Capturing to file: %s\n",cmd);
  start_time = get_time();

  // Auto purge if files are greater than recording_count. It will remove older files.
  snprintf(purge,sizeof(purge),"ls -td1 %s/*.mp4 | tail -n +%d | xargs rm -f&", videos_dir, s->scene.recording_count);
  system(purge);
  system(cmd);

  if (lock_current_video) {
    // Lock is still on so mark this file for saving
    locked_files[captureNum] = 1;
  }
  else {
    locked_files[captureNum] = 0;
  }

  files_created++;
}

bool screen_button_clicked(UIState *s) {
  if (s->scene.recording) {
    return true;
  }
  return false;
}

void draw_date_time(UIState *s) {
  if (captureState == CAPTURE_STATE_NOT_CAPTURING) {
    // Don't draw if we're not recording
    return;
  }

  // Draw the current date/time

  int rect_w = 425;
  int rect_h = 70;
  int rect_x = 1920-rect_w;
  int rect_y = -42;

  // Get local time to display
  char now[50];
  struct tm tm = get_time_struct();
  snprintf(now,sizeof(now),"%04d-%02d-%02d  %02d:%02d:%02d", tm.tm_year + 1900, tm.tm_mon + 1, tm.tm_mday, tm.tm_hour, tm.tm_min, tm.tm_sec);

  nvgBeginPath(s->vg);
    nvgRoundedRect(s->vg, rect_x, rect_y, rect_w, rect_h, 0);
    nvgFillColor(s->vg, nvgRGBA(0, 0, 0, 0));
    nvgFill(s->vg);
    nvgStrokeColor(s->vg, nvgRGBA(255,255,255,0));
    nvgStrokeWidth(s->vg, 0);
    nvgStroke(s->vg);

  nvgFontSize(s->vg, 34);
    nvgFontFace(s->vg, "sans-semibold");
    nvgFillColor(s->vg, nvgRGBA(255, 255, 255, 200));
    nvgText(s->vg,rect_x+229,rect_y+57,now,NULL);
}

static void rotate_video(UIState *s) {
  // Overwrite the existing video (if needed)
  elapsed_time = 0;
  stop_capture();
  captureState = CAPTURE_STATE_CAPTURING;
  start_capture(s);
}

static void screen_draw_button(UIState *s) {
  // Set button to bottom left of screen
//  if (s->vision_connected && s->plus_state == 0) {
  if (s->vipc_client->connected || s->is_OpenpilotViewEnabled) {
    int btn_w = 140;
    int btn_h = 140;
    int btn_x = s->viz_rect.x + s->viz_rect.w - btn_w - 35;
    int btn_y = 1080 - btn_h - 35;
    int btn_xc = btn_x + (btn_w/2);
    int btn_yc = btn_y + (btn_h/2);
    nvgBeginPath(s->vg);
    nvgRoundedRect(s->vg, btn_x, btn_y, btn_w, btn_h, 100);
    nvgStrokeColor(s->vg, nvgRGBA(255,255,255,80));
    nvgStrokeWidth(s->vg, 6);
    nvgStroke(s->vg);

    nvgFontSize(s->vg, 45);

    if (captureState == CAPTURE_STATE_CAPTURING) {
      NVGcolor fillColor = nvgRGBA(255,0,0,150);
      nvgFillColor(s->vg, fillColor);
      nvgFill(s->vg);
      nvgFillColor(s->vg, nvgRGBA(255,255,255,200));
    }
    else {
      nvgFillColor(s->vg, nvgRGBA(255, 255, 255, 200));
    }
    nvgTextAlign(s->vg, NVG_ALIGN_CENTER | NVG_ALIGN_MIDDLE);
    nvgText(s->vg, btn_xc, btn_yc, "REC", NULL);
  }

  if (captureState == CAPTURE_STATE_CAPTURING) {
    //draw_date_time(s);

    elapsed_time = get_time() - start_time;

    if (elapsed_time >= RECORD_INTERVAL) {
      rotate_video(s);
    }
  }
}

void screen_toggle_record_state(UIState *s) {
  if (captureState == CAPTURE_STATE_CAPTURING) {
    stop_capture();
    lock_current_video = false;
  }
  else {
    //captureState = CAPTURE_STATE_CAPTURING;
    start_capture(s);
  }
}

void screen_toggle_lock() {
  if (lock_current_video) {
    lock_current_video = false;
  }
  else {
    lock_current_video = true;
    locked_files[captureNum] = 1;
  }
}

void dashcam(UIState *s) {
  if (!s->scene.comma_stock_ui) {
    screen_draw_button(s);
  }
  if (s->scene.touched && screen_button_clicked(s) && !s->sidebar_view) {
    click_elapsed_time = get_time() - click_time;

    if (click_elapsed_time > 0) {
      click_time = get_time() + 1;
      screen_toggle_record_state(s);
      s->scene.touched = !s->scene.touched;
    }
  }

  if (!s->vipc_client->connected) {
    // Assume car is not in drive so stop recording
    stop_capture();
  }

  if (s->driving_record) {
    if (s->scene.car_state.getVEgo() > 1 && captureState == CAPTURE_STATE_NOT_CAPTURING && s->scene.controls_state.getEnabled()) {
      start_capture(s);
    } else if (s->scene.standStill && captureState == CAPTURE_STATE_CAPTURING && s->scene.controls_state.getEnabled()) {
      stop_capture();
    }
  }
  s->scene.recording = (captureState != CAPTURE_STATE_NOT_CAPTURING);
}
