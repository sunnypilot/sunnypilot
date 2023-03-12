#include <CL/cl.h>
#include <algorithm>
#include <time.h>
#include <dirent.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/time.h>

#include "libyuv.h"
#include "common/clutil.h"

#include "selfdrive/ui/qt/onroad.h"
#include "selfdrive/ui/qt/screenrecorder/screenrecorder.h"
#include "selfdrive/ui/qt/util.h"
#include "selfdrive/ui/ui.h"
#include "system/hardware/hw.h"

static long long milliseconds(void) {
    struct timeval tv;
    gettimeofday(&tv,NULL);
    return (((long long)tv.tv_sec)*1000)+(tv.tv_usec/1000);
}

ScreenRecoder::ScreenRecoder(QWidget *parent) : QPushButton(parent), image_queue(30)
{

  recording = false;
  started = 0;
  frame = 0;

  setFixedSize(btn_size, btn_size);
  setFocusPolicy(Qt::NoFocus);
  connect(this, SIGNAL(pressed()),this,SLOT(btnPressed()));
  connect(this, SIGNAL(released()),this,SLOT(btnReleased()));

  std::string path = "/data/media/0/videos";
  src_width = 2160;
  src_height = 1080;

  dst_height = 720;
  dst_width = src_width * dst_height / src_height;
  if(dst_width % 2 != 0)
      dst_width += 1;

  rgb_buffer = std::make_unique<uint8_t[]>(src_width*src_height*4);
  rgb_scale_buffer = std::make_unique<uint8_t[]>(dst_width*dst_height*4);
  encoder = std::make_unique<OmxEncoder>(path.c_str(), dst_width, dst_height, UI_FREQ, 2*1024*1024, false, false);

  //soundStart.setSource(QUrl::fromLocalFile("../assets/sounds/rec_on.wav"));
  //soundStop.setSource(QUrl::fromLocalFile("../assets/sounds/rec_off.wav"));

  //soundStart.setVolume(0.7f);
  //soundStop.setVolume(0.9f);
}

ScreenRecoder::~ScreenRecoder() {
  stop(false);
}

void ScreenRecoder::applyColor() {

  if(frame % (UI_FREQ/2) == 0) {

  recording_color = QColor::fromRgbF(1, 0, 0, 0.4);
    //if(frame % UI_FREQ < (UI_FREQ/2))
      //recording_color = QColor::fromRgbF(1, 0, 0, 0.6);
    //else
      //recording_color = QColor::fromRgbF(0, 0, 0, 0.3);

    update();
  }
}

void ScreenRecoder::paintEvent(QPaintEvent *event) {
/*
    QRect r = QRect(30, 0, width(), height());
    r -= QMargins(5, 5, 5, 5);

    QPainter p(this);
    // its drwas outter circle.
    //p.setCompositionMode(QPainter::CompositionMode_SourceOver);
    //p.setPen(QPen(QColor::fromRgbF(1, 1, 1, 0.4), 10, Qt::SolidLine, Qt::FlatCap));

    //p.setBrush(QBrush(QColor::fromRgbF(0, 0, 0, 0)));
    //p.drawEllipse(r);

    r -= QMargins(40, 40, 40, 40);
    p.setPen(Qt::NoPen);

    //TODO: make it square?
    QColor bg = recording ? recording_color : QColor(252, 255, 253, 70);
    p.setBrush(QBrush(bg));
    p.drawEllipse(r);

    //QPainter painter(this);
    p.setPen(Qt::white);
    p.setFont(QFont("Arial", 30));
    p.drawText(r,Qt::AlignCenter, "REC");
*/
  QPainter p(this);
  p.setRenderHint(QPainter::Antialiasing);

  QPoint center(btn_size / 2 - 25, btn_size / 2 + 10 - uiState()->scene.rn_offset);
  QRect rec_btn(36 - 25, 36 + 10 - uiState()->scene.rn_offset, 120, 120);

  p.setOpacity(1.0);
  p.setPen(Qt::NoPen);
  p.setBrush(QBrush(recording ? recording_color : QColor(252, 255, 253, 70)));
  p.setOpacity(isDown() ? 0.8 : 1.0);
  p.drawEllipse(center, 120 / 2, 120 / 2);
  p.setPen(Qt::white);
  p.setFont(QFont("Arial", 30));
  p.drawText(rec_btn, Qt::AlignCenter, "REC");
}

void ScreenRecoder::btnReleased(void) {
    toggle();
}

void ScreenRecoder::btnPressed(void) {
}

void ScreenRecoder::openEncoder(const char* filename) {
    encoder->encoder_open(filename);
}

void ScreenRecoder::closeEncoder() {
  if(encoder)
      encoder->encoder_close();
}

void ScreenRecoder::toggle() {

  if(!recording)
      start(true);
  else
      stop(true);
}

void ScreenRecoder::start(bool sound) {

  if(recording)
    return;

  char filename[64];
  time_t t = time(NULL);
  struct tm tm = *localtime(&t);
  snprintf(filename,sizeof(filename),"%04d%02d%02d-%02d%02d%02d.mp4", tm.tm_year + 1900, tm.tm_mon + 1, tm.tm_mday, tm.tm_hour, tm.tm_min, tm.tm_sec);

  recording = true;
  frame = 0;

  QWidget* widget = this;
  while (widget->parentWidget() != Q_NULLPTR)
    widget = widget->parentWidget();

  rootWidget = widget;

  openEncoder(filename);
  encoding_thread = std::thread([=] { encoding_thread_func(); });

  update();

  started = milliseconds();

  //if(sound)
  //    soundStart.play();
}

void ScreenRecoder::encoding_thread_func() {
  uint64_t start_time = nanos_since_boot() -1;
  while(recording && encoder) {
    QImage popImage;
    if(image_queue.pop_wait_for(popImage, std::chrono::milliseconds(10))) {

      QImage image = popImage.convertToFormat(QImage::Format_RGBA8888);

      libyuv::ARGBScale(image.bits(), image.width()*4,
            image.width(), image.height(),
            rgb_scale_buffer.get(), dst_width*4,
            dst_width, dst_height,
            libyuv::kFilterLinear);

      encoder->encode_frame_rgba(rgb_scale_buffer.get(), dst_width, dst_height, ((uint64_t)nanos_since_boot() - start_time ));
    }
  }
}

void ScreenRecoder::stop(bool sound) {

  if(recording) {
    recording = false;
    update();

  closeEncoder();
  image_queue.clear();
  if(encoding_thread.joinable())
    encoding_thread.join();

  //if(sound)
  //    soundStop.play();
  }
}

void ScreenRecoder::update_screen() {

  if(recording) {

    if(milliseconds() - started > 1000*60*3) {
      stop(false);
      start(false);
      return;
    }

    applyColor();

    if(rootWidget != nullptr) {
      QPixmap pixmap = rootWidget->grab();
      image_queue.push(pixmap.toImage());
    }
  }

  frame++;
}
