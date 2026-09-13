#include <array>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <tuple>

#include "system/camerad/cameras/nv12_info.h"

namespace {

constexpr int SOURCE_WIDTH = 1928, SOURCE_HEIGHT = 1208;
constexpr int TARGET_WIDTH = 1344, TARGET_HEIGHT = 760;

template <size_t Source, size_t Target>
constexpr std::array<uint16_t, Target> coordinates() {
  std::array<uint16_t, Target> result{};
  for (size_t i = 0; i < Target; ++i) {
    result[i] = static_cast<uint16_t>((2 * i + 1) * Source / (2 * Target));
  }
  return result;
}

constexpr auto y_columns = coordinates<SOURCE_WIDTH, TARGET_WIDTH>();
constexpr auto y_rows = coordinates<SOURCE_HEIGHT, TARGET_HEIGHT>();
constexpr auto uv_columns = coordinates<SOURCE_WIDTH / 2, TARGET_WIDTH / 2>();
constexpr auto uv_rows = coordinates<SOURCE_HEIGHT / 2, TARGET_HEIGHT / 2>();

const auto source_nv12 = get_nv12_info(SOURCE_WIDTH, SOURCE_HEIGHT);
const auto target_nv12 = get_nv12_info(TARGET_WIDTH, TARGET_HEIGHT);
const size_t source_stride = std::get<0>(source_nv12), source_y_height = std::get<1>(source_nv12), source_uv_height = std::get<2>(source_nv12);
const size_t target_stride = std::get<0>(target_nv12), target_y_height = std::get<1>(target_nv12), target_uv_height = std::get<2>(target_nv12);
const size_t source_copy_size = source_stride * (source_y_height + source_uv_height);
const size_t target_copy_size = target_stride * (target_y_height + target_uv_height);

}  // namespace

extern "C" int frame_resize_nv12(const uint8_t *source, size_t source_size,
                                uint8_t *destination, size_t destination_size) noexcept {
  if (source == nullptr || destination == nullptr || source_size < source_copy_size || destination_size != target_copy_size) {
    return 1;
  }
  const auto src_address = reinterpret_cast<uintptr_t>(source);
  const auto dst_address = reinterpret_cast<uintptr_t>(destination);
  // Subtract ordered addresses to avoid overflow when checking buffer overlap.
  if ((src_address <= dst_address && dst_address - src_address < source_size) ||
      (dst_address < src_address && src_address - dst_address < destination_size)) {
    return 1;
  }

  for (size_t y = 0; y < TARGET_HEIGHT; ++y) {
    const uint8_t *src_row = source + static_cast<size_t>(y_rows[y]) * source_stride;
    uint8_t *dst_row = destination + y * target_stride;
    for (size_t x = 0; x < TARGET_WIDTH; ++x) {
      dst_row[x] = src_row[y_columns[x]];
    }
    std::memset(dst_row + TARGET_WIDTH, dst_row[TARGET_WIDTH - 1], target_stride - TARGET_WIDTH);
  }
  for (size_t y = TARGET_HEIGHT; y < target_y_height; ++y) {
    std::memcpy(destination + y * target_stride, destination + (TARGET_HEIGHT - 1) * target_stride, target_stride);
  }

  const uint8_t *source_uv = source + source_stride * source_y_height;
  uint8_t *destination_uv = destination + target_stride * target_y_height;
  for (size_t y = 0; y < TARGET_HEIGHT / 2; ++y) {
    const uint8_t *src_row = source_uv + static_cast<size_t>(uv_rows[y]) * source_stride;
    uint8_t *dst_row = destination_uv + y * target_stride;
    for (size_t x = 0; x < TARGET_WIDTH / 2; ++x) {
      dst_row[2 * x] = src_row[2 * uv_columns[x]];
      dst_row[2 * x + 1] = src_row[2 * uv_columns[x] + 1];
    }
    for (size_t x = TARGET_WIDTH; x < target_stride; x += 2) {
      dst_row[x] = dst_row[TARGET_WIDTH - 2];
      dst_row[x + 1] = dst_row[TARGET_WIDTH - 1];
    }
  }
  for (size_t y = TARGET_HEIGHT / 2; y < target_uv_height; ++y) {
    std::memcpy(destination_uv + y * target_stride, destination_uv + (TARGET_HEIGHT / 2 - 1) * target_stride, target_stride);
  }
  return 0;
}
