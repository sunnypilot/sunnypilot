#pragma once

#include <memory>
#include <cstdint>
#include <QPainter>
#include <QPushButton>
#include <QSoundEffect>
#include <thread>
#include <chrono>

#include "omx_encoder.h"
#include "blocking_queue.h"
#include "selfdrive/ui/ui.h"

class ScreenRecoder : public QPushButton {
  Q_OBJECT

public:
  ScreenRecoder(QWidget *parent = 0);
  virtual ~ScreenRecoder();

public slots:
    void btnReleased(void);
    void btnPressed(void);

protected:
  void paintEvent(QPaintEvent*) override;

private:
  bool recording;
  long long started;
  int src_width, src_height;
  int dst_width, dst_height;

  QColor recording_color;
  int frame;

  //QSoundEffect soundStart;
  //QSoundEffect soundStop;

  void applyColor();

  std::unique_ptr<OmxEncoder> encoder;
  std::unique_ptr<uint8_t[]> rgb_buffer;
  std::unique_ptr<uint8_t[]> rgb_scale_buffer;

  std::thread encoding_thread;
  BlockingQueue<QImage> image_queue;
  QWidget* rootWidget;
  void encoding_thread_func();
  void openEncoder(const char* filename);
  void closeEncoder();

public:
    void start(bool sound);
    void stop(bool sound);
    void toggle();
    void update_screen();

};
