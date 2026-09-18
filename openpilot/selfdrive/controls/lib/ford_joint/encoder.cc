// Opt-in Ford joint encoder. Numerical request state is estimated, not ECU RAM.
#include <algorithm>
#include <cmath>
#include <cstring>

static double clip(double x, double lo, double hi) {
  return std::min(std::max(x, lo), hi);
}

// State: held C0, held C1, internal I, filtered curvature, fast-slew latch.
// Parameters: g0/g1, base alpha, heading low/high/gain, alpha max, speed,
// interaction threshold/value, C0 slow/fast, C1 slow/fast, latch clear C0/C1,
// opposite C0/I thresholds, I gain, delta low/high, I low/high, release rate.
static void step(double *s, const double *p, double c0, double c1) {
  if (p[9] < p[8]) {
    s[4] = 1;
  } else if (std::abs(c0) <= p[14] && std::abs(c1) <= p[15]) {
    s[4] = 0;
  }
  double r0 = p[s[4] ? 11 : 10], r1 = p[s[4] ? 13 : 12];
  s[0] += clip(c0 - s[0], -r0 * .008, r0 * .008);
  s[1] += clip(c1 - s[1], -r1 * .008, r1 * .008);
  if (std::abs(s[0]) > p[16] && std::abs(s[2]) > p[17] && s[0] * s[2] < 0) {
    s[2] += clip(-s[2], -p[23], p[23]);
  } else {
    s[2] = clip(s[2] + clip(s[0], p[19], p[20]) * p[18], p[21], p[22]);
  }
  double raw = p[0] * (s[0] + s[2]) + p[1] * s[1];
  double w = clip(std::abs(s[1] * p[7]) - p[3], 0, std::max(1e-6, p[4] - p[3])) / std::max(1e-6, p[4] - p[3]);
  double alpha = std::min(p[6], p[2] + p[5] * w);
  s[3] += alpha * (raw - s[3]);
}

extern "C" double paired_cost(const double *initial, const double *p, double target,
                              const double *pref, int count, double c0, double c1, double *first) {
  double s[5];
  std::memcpy(s, initial, sizeof(s));
  double steady_raw = p[0] * pref[0] + p[1] * pref[1];
  double steady_error = (steady_raw - target) / .01, cost = 0;
  auto tick = [&](double a, double b) {
    step(s, p, a, b);
    double error = (s[3] - target) / .01;
    cost += .008 * (error * error - steady_error * steady_error);
  };
  for (int j = 0; j < count; j++) tick(c0, c1);
  if (first) std::memcpy(first, s, sizeof(s));
  // Include both channels' entire return, followed by the exact filter tail.
  // There is no adjustable planning horizon or retained future command plan.
  int n = 2 + std::ceil(std::max(std::abs(s[0] - pref[0]) / std::min(p[10], p[11]),
                               std::abs(s[1] - pref[1]) / std::min(p[12], p[13])) / .008);
  for (int j = 0; j < n; j++) tick(pref[0], pref[1]);
  double w = clip(std::abs(s[1] * p[7]) - p[3], 0, p[4] - p[3]) / (p[4] - p[3]);
  double alpha = std::min(p[6], p[2] + p[5] * w), a = 1 - alpha;
  double d = (s[3] - steady_raw) / .01;
  return cost + .008 * (2 * steady_error * d * a / alpha + d * d * a * a / (1 - a * a));
}

extern "C" void paired_select(const double *initial, const double *p, double target,
                              const double *pref, int count, const double *c0s, int n0,
                              const double *c1s, int n1, int preserve_now, double *result) {
  double best = 1e300, best_move = 1e300, best_remaining = 1e300;
  double first[5];
  double max_error = 1e300, anchor_score = 1e300, anchor_move = 1e300, anchor_remaining = 1e300;
  if (preserve_now) {
    // Preserve the C1-anchored policy's immediate target accuracy.
    // An inequality against a feasible reference, not a new gain/deadband.
    for (int i = 0; i < n0; i++) {
      double cost = paired_cost(initial, p, target, pref, count, c0s[i], pref[1], first);
      double score = std::nearbyint(cost * 1e12) / 1e12;
      double move = std::abs(c0s[i] - initial[0]), remaining = std::abs(c0s[i] - pref[0]);
      if (score < anchor_score || (score == anchor_score && (move < anchor_move || (move == anchor_move && remaining < anchor_remaining)))) {
        anchor_score = score;
        anchor_move = move;
        anchor_remaining = remaining;
        max_error = std::abs(first[3] - target);
      }
    }
  }
  for (int i = 0; i < n0; i++) {
    for (int j = 0; j < n1; j++) {
      double cost = paired_cost(initial, p, target, pref, count, c0s[i], c1s[j], first);
      if (std::abs(first[3] - target) > max_error + 1e-12) continue;
      // Numerical equality only. Tie breaks cannot trade worse tracking for
      // less channel motion; normalize them using the existing field spans.
      double score = std::nearbyint(cost * 1e12) / 1e12;
      double move = std::abs(c0s[i] - initial[0]) / 5.11 + std::abs(c1s[j] - initial[1]) / .5;
      double remaining = std::abs(c0s[i] - pref[0]) / 5.11 + std::abs(c1s[j] - pref[1]) / .5;
      if (score < best || (score == best && (move < best_move || (move == best_move && remaining < best_remaining)))) {
        best = score;
        best_move = move;
        best_remaining = remaining;
        result[0] = c0s[i];
        result[1] = c1s[j];
        result[2] = cost;
        std::memcpy(result + 3, first, 5 * sizeof(double));
      }
    }
  }
  result[8] = max_error;
}
