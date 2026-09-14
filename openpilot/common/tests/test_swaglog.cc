#include <cstdlib>
#include <string>

#include <zmq.h>

#include "common/hardware/hw.h"
#include "common/swaglog.h"
#include "common/tests/native_test.h"
#include "json11/json11.hpp"

#include "sunnypilot/common/version.h"

std::string daemon_name = "testy";
std::string dongle_id = "test_dongle_id";
int LINE_NO = 0;

void test_swaglog() {
  setenv("MANAGER_DAEMON", "swaglog_test", 1);
  setenv("DONGLE_ID", "test_dongle_id", 1);
  setenv("CLEAN", "1", 1);

  void *context = zmq_ctx_new();
  CHECK(context != nullptr);
  void *socket = zmq_socket(context, ZMQ_PULL);
  CHECK(socket != nullptr);
  int timeout = 5000;
  CHECK(zmq_setsockopt(socket, ZMQ_RCVTIMEO, &timeout, sizeof(timeout)) == 0);
  CHECK(zmq_bind(socket, Path::swaglog_ipc().c_str()) == 0);

  LOGD("native-cpp-log");

  char buffer[4096] = {};
  const int size = zmq_recv(socket, buffer, sizeof(buffer), 0);
  CHECK(size > 1);
  CHECK(buffer[0] == CLOUDLOG_DEBUG);
  std::string error;
  const auto message = json11::Json::parse(std::string(buffer + 1, size - 1), error);
  CHECK(error.empty());
  CHECK(message["levelnum"].int_value() == CLOUDLOG_DEBUG);
  CHECK(message["msg"].string_value() == "native-cpp-log");
  CHECK(message["funcname"].string_value() == "test_swaglog");
  CHECK(message["filename"].string_value().find("test_swaglog.cc") != std::string::npos);
  CHECK(message["ctx"]["daemon"].string_value() == "swaglog_test");
  CHECK(message["ctx"]["dongle_id"].string_value() == "test_dongle_id");
  CHECK(message["ctx"]["dirty"].bool_value() == false);

  CHECK(zmq_close(socket) == 0);
  CHECK(zmq_ctx_destroy(context) == 0);
}

void recv_log(int thread_cnt, int thread_msg_cnt) {
  void *zctx = zmq_ctx_new();
  void *sock = zmq_socket(zctx, ZMQ_PULL);
  zmq_bind(sock, Path::swaglog_ipc().c_str());
  std::vector<int> thread_msgs(thread_cnt);
  int total_count = 0;

  for (auto start = std::chrono::steady_clock::now(), now = start;
       now < start + std::chrono::seconds{1} && total_count < (thread_cnt * thread_msg_cnt);
       now = std::chrono::steady_clock::now()) {
    char buf[4096] = {};
    if (zmq_recv(sock, buf, sizeof(buf), ZMQ_DONTWAIT) <= 0) {
      if (errno == EAGAIN || errno == EINTR || errno == EFSM) continue;
      break;
    }

    CHECK(buf[0] == CLOUDLOG_DEBUG);
    std::string err;
    auto msg = json11::Json::parse(buf + 1, err);
    CHECK(!msg.is_null());

    CHECK(msg["levelnum"].int_value() == CLOUDLOG_DEBUG);
    CHECK(msg["filename"].string_value().find("test_swaglog.cc") != std::string::npos);
    CHECK(msg["funcname"].string_value() == "log_thread");
    CHECK(msg["lineno"].int_value() == LINE_NO);

    auto ctx = msg["ctx"];

    CHECK(ctx["daemon"].string_value() == daemon_name);
    CHECK(ctx["dongle_id"].string_value() == dongle_id);
    CHECK(ctx["dirty"].bool_value() == true);

    CHECK(ctx["version"].string_value() == SUNNYPILOT_VERSION);

    std::string device = Hardware::get_name();
    CHECK(ctx["device"].string_value() == device);

    int thread_id = atoi(msg["msg"].string_value().c_str());
    CHECK((thread_id >= 0 && thread_id < thread_cnt));
    thread_msgs[thread_id]++;
    total_count++;
  }
  for (int i = 0; i < thread_cnt; ++i) {
    CHECK(thread_msgs[i] == thread_msg_cnt);
  }
  zmq_close(sock);
  zmq_ctx_destroy(zctx);
}

int main() {
  return run_native_test(test_swaglog);
}
