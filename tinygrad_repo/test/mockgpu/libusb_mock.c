#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/un.h>

struct libusb_device_descriptor {
  uint8_t bLength, bDescriptorType; uint16_t bcdUSB; uint8_t bDeviceClass, bDeviceSubClass, bDeviceProtocol, bMaxPacketSize0;
  uint16_t idVendor, idProduct, bcdDevice; uint8_t iManufacturer, iProduct, iSerialNumber, bNumConfigurations;
};
struct libusb_transfer;
typedef void (*libusb_transfer_cb_fn)(struct libusb_transfer *);
struct libusb_transfer {
  void *dev_handle; uint8_t flags; unsigned char endpoint, type; unsigned int timeout; int status, length, actual_length;
  libusb_transfer_cb_fn callback; void *user_data; unsigned char *buffer; int num_iso_packets;
};
enum { CTRL_OUT = 1, CTRL_IN = 2, BULK_OUT = 3, BULK_IN = 4, PROGRESS = 5 };
enum { LIBUSB_ERROR_IO = -1, LIBUSB_TRANSFER_COMPLETED = 0, LIBUSB_TRANSFER_ERROR = 1 };

static uint64_t ctx_obj, dev_obj, handle_obj;
static void *dev_list[2] = {&dev_obj, NULL};
static int sock = -1;
static struct libusb_transfer *done[64];
static int ndone;

static void io(int (*fn)(int, void *, size_t), void *p, size_t n) {
  for (size_t got = 0; got < n;) {
    ssize_t r = fn(sock, (char *)p + got, n - got);
    if (r <= 0) { fprintf(stderr, "libusb_mock: the mock usb server went away\n"); _exit(70); }
    got += r;
  }
}
static int rd(int fd, void *p, size_t n) { return read(fd, p, n); }
static int wr(int fd, void *p, size_t n) { return write(fd, p, n); }

static int call(uint8_t op, uint8_t req, uint16_t value, uint16_t index, unsigned char *data, uint32_t len) {
  if (sock < 0) {
    const char *path = getenv("MOCKUSB_SOCKET");
    struct sockaddr_un a = {.sun_family = AF_UNIX};
    if (!path || strlen(path) >= sizeof(a.sun_path)) { fprintf(stderr, "libusb_mock: MOCKUSB_SOCKET is not set\n"); _exit(70); }
    strcpy(a.sun_path, path);
    if ((sock = socket(AF_UNIX, SOCK_STREAM, 0)) < 0 || connect(sock, (struct sockaddr *)&a, sizeof(a)) < 0) {
      fprintf(stderr, "libusb_mock: cannot reach the mock usb server at %s\n", path); _exit(70);
    }
  }
  unsigned char hdr[10] = {op, req, value & 0xff, value >> 8, index & 0xff, index >> 8, len & 0xff, (len >> 8) & 0xff, (len >> 16) & 0xff, len >> 24};
  io(wr, hdr, sizeof(hdr));
  if (op == CTRL_OUT || op == BULK_OUT) io(wr, data, len);
  int32_t rc;
  io(rd, &rc, sizeof(rc));
  if (rc > 0 && (op == CTRL_IN || op == BULK_IN)) io(rd, data, rc);
  return rc;
}

int libusb_init(void **ctx) { if (ctx) *ctx = &ctx_obj; return 0; }
void libusb_exit(void *ctx) {}
int libusb_set_option(void *ctx, int option, ...) { return 0; }
const char *libusb_strerror(int code) { return "mock usb transfer failed (see the mock usb server's log)"; }
const char *libusb_error_name(int code) { return "LIBUSB_ERROR_IO"; }
long libusb_get_device_list(void *ctx, void ***list) { *list = dev_list; return 1; }
void libusb_free_device_list(void **list, int unref) {}
void *libusb_ref_device(void *dev) { return dev; }
void libusb_unref_device(void *dev) {}
uint8_t libusb_get_bus_number(void *dev) { return 1; }
uint8_t libusb_get_device_address(void *dev) { return 1; }
int libusb_get_device_descriptor(void *dev, struct libusb_device_descriptor *d) {
  *d = (struct libusb_device_descriptor){.bLength = 18, .bDescriptorType = 1, .bcdUSB = 0x320, .idVendor = 0xADD1, .idProduct = 0x0001,
                                         .iProduct = 2, .bNumConfigurations = 1};
  return 0;
}
int libusb_open(void *dev, void **handle) { *handle = &handle_obj; return 0; }
void libusb_close(void *handle) {}
void *libusb_get_device(void *handle) { return &dev_obj; }
int libusb_get_string_descriptor_ascii(void *handle, uint8_t index, unsigned char *data, int length) {
  const char *s = "custom mock";
  int n = (int)strlen(s) < length ? (int)strlen(s) : length;
  memcpy(data, s, n);
  return n;
}
int libusb_kernel_driver_active(void *handle, int iface) { return 0; }
int libusb_detach_kernel_driver(void *handle, int iface) { return 0; }
int libusb_reset_device(void *handle) { return 0; }
int libusb_set_configuration(void *handle, int config) { return 0; }
int libusb_claim_interface(void *handle, int iface) { return 0; }
int libusb_release_interface(void *handle, int iface) { return 0; }
int libusb_set_interface_alt_setting(void *handle, int iface, int alt) { return 0; }

int libusb_control_transfer(void *handle, uint8_t rtype, uint8_t req, uint16_t value, uint16_t index, unsigned char *data, uint16_t length,
                            unsigned int timeout) {
  return call(rtype & 0x80 ? CTRL_IN : CTRL_OUT, req, value, index, data, length);
}
int libusb_bulk_transfer(void *handle, unsigned char ep, unsigned char *data, int length, int *actual, unsigned int timeout) {
  int rc = call(ep & 0x80 ? BULK_IN : BULK_OUT, 0, 0, 0, data, length);
  if (actual) *actual = rc < 0 ? 0 : rc;
  return rc < 0 ? rc : 0;
}

struct libusb_transfer *libusb_alloc_transfer(int iso_packets) { return calloc(1, sizeof(struct libusb_transfer) + 16 * iso_packets); }
void libusb_free_transfer(struct libusb_transfer *t) { free(t); }
int libusb_submit_transfer(struct libusb_transfer *t) {
  int rc = call(t->endpoint & 0x80 ? BULK_IN : BULK_OUT, 0, 0, 0, t->buffer, t->length);
  t->actual_length = rc < 0 ? 0 : rc;
  t->status = rc < 0 ? LIBUSB_TRANSFER_ERROR : LIBUSB_TRANSFER_COMPLETED;
  if (t->callback) {
    if (ndone == 64) return LIBUSB_ERROR_IO;
    done[ndone++] = t;
  }
  return 0;
}
int libusb_cancel_transfer(struct libusb_transfer *t) { return 0; }
int libusb_handle_events_timeout_completed(void *ctx, void *tv, int *completed) {
  int rc = call(PROGRESS, 0, 0, 0, NULL, 0); // polls are where a waiting host lets the gpu run
  struct libusb_transfer *now[64];
  int n = ndone;
  memcpy(now, done, n * sizeof(*now)), ndone = 0; // a callback may submit again
  for (int i = 0; i < n; i++) now[i]->callback(now[i]);
  return rc < 0 ? rc : 0;
}
int libusb_handle_events_timeout(void *ctx, void *tv) { return libusb_handle_events_timeout_completed(ctx, tv, NULL); }
int libusb_handle_events(void *ctx) { return libusb_handle_events_timeout_completed(ctx, NULL, NULL); }
int libusb_handle_events_completed(void *ctx, int *completed) { return libusb_handle_events_timeout_completed(ctx, NULL, completed); }
