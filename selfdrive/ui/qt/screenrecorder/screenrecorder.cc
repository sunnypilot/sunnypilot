#include <CL/cl.h>
#include <algorithm>
#include <time.h>
#include <dirent.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/time.h>

#include "libyuv.h"
#include "common/clutil.h"

#include "selfdrive/ui/qt/onroad/annotated_camera.h"
#include "selfdrive/ui/qt/screenrecorder/screenrecorder.h"
#include "selfdrive/ui/qt/util.h"
#include "selfdrive/ui/ui.h"
#include "system/hardware/hw.h"

static long long milliseconds(void) {
  struct timeval tv;
  gettimeofday(&tv,NULL);
  return (((long long)tv.tv_sec)*1000)+(tv.tv_usec/1000);
}

ScreenRecoder::ScreenRecoder(QWidget *parent) : QPushButton(parent), image_queue(30) {
  recording = false;
  started = 0;
  frame = 0;
  rec_btn_size = 150;

  setVisible(false);
  setEnabled(false);
  setFixedSize(rec_btn_size, rec_btn_size);
  setFocusPolicy(Qt::NoFocus);
  QObject::connect(this, &QPushButton::clicked, [=]() {
    toggle();
  });

  std::string path = "/data/media/0/videos";
  src_width = 2160;
  src_height = 1080;

  dst_height = 720;
  dst_width = src_width * dst_height / src_height;
  if (dst_width % 2 != 0)
    dst_width += 1;

  rgb_buffer = std::make_unique<uint8_t[]>(src_width*src_height*4);
  rgb_scale_buffer = std::make_unique<uint8_t[]>(dst_width*dst_height*4);
  encoder = std::make_unique<OmxEncoder>(path.c_str(), dst_width, dst_height, UI_FREQ, 2*1024*1024, false, false);
}

ScreenRecoder::~ScreenRecoder() {
  stop();
}

void ScreenRecoder::applyColor() {
  if (frame % (UI_FREQ / 2) == 0) {
    if (frame % UI_FREQ < (UI_FREQ / 2))
      recording_color = QColor::fromRgbF(1, 0, 0, 0.6);
    else
      recording_color = QColor::fromRgbF(0, 0, 0, 0.3);

    update();
  }
}

void ScreenRecoder::paintEvent(QPaintEvent *event) {
  QPainter p(this);
  p.setRenderHint(QPainter::Antialiasing);

  QPoint center(rec_btn_size / 2, rec_btn_size / 2);

  p.setOpacity(1.0);
  p.setPen(Qt::NoPen);
  p.setBrush(QBrush(recording ? recording_color : QColor(252, 255, 253, 70)));
  p.setOpacity(isDown() ? 0.6 : 1.0);
  p.drawEllipse(center, rec_btn_size / 2, rec_btn_size / 2);

  p.setPen(Qt::white);
  p.setFont(QFont("Arial", 30));
  QFontMetrics fontMetrics(p.font());
  int textWidth = fontMetrics.width("REC");
  int textHeight = fontMetrics.height();

  int textX = center.x() - textWidth / 2;
  int textY = center.y() / 1.5; // Adjust vertically for proper alignment

  p.drawText(textX, textY, textWidth, textHeight, Qt::AlignCenter, "REC");
}

void ScreenRecoder::openEncoder(const char* filename) {
  encoder->encoder_open(filename);
}

void ScreenRecoder::closeEncoder() {
  if (encoder)
    encoder->encoder_close();
}

void ScreenRecoder::toggle() {
  if (!recording)
    start();
  else
    stop();
}

void ScreenRecoder::start() {
  if (recording)
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
}

void ScreenRecoder::encoding_thread_func() {
  uint64_t start_time = nanos_since_boot();

  while (recording && encoder) {
    QImage popImage;
    if (image_queue.pop_wait_for(popImage, std::chrono::milliseconds(10))) {

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

void ScreenRecoder::stop() {
  if (recording) {
    recording = false;
    update();

    if (encoding_thread.joinable()) {
      encoding_thread.join();
    }
    closeEncoder();
    image_queue.clear();
  }
}

void ScreenRecoder::update_screen() {
  if (recording) {
    if (milliseconds() - started > 1000*60*1) {
      stop();
      start();
      return;
    }

    applyColor();

    if (rootWidget != nullptr) {
      QPixmap pixmap = rootWidget->grab();
      image_queue.push(pixmap.toImage());
    }
  }

  frame++;
}

void ScreenRecoder::updateState(const UIState &s) {
  bool show_toggle = params.getBool("ScreenRecorder") || recording;
  setVisible(show_toggle);
  setEnabled(show_toggle);
}
