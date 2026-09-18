// Opt-in Ford joint encoder. Numerical request state is estimated, not ECU RAM.
#include <algorithm>
#include <array>
#include <cmath>
#include <cstring>
#include <map>

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

static double command_cost(const double *initial, const double *p, double target,
                           const double *pref, int count, double c0, double c1, double *s) {
  std::memcpy(s, initial, 5 * sizeof(double));
  double steady_raw = p[0] * pref[0] + p[1] * pref[1];
  double steady_error = (steady_raw - target) / .01, cost = 0;
  for (int j = 0; j < count; j++) {
    step(s, p, c0, c1);
    double error = (s[3] - target) / .01;
    cost += .008 * (error * error - steady_error * steady_error);
  }
  return cost;
}

static double return_cost(const double *first, const double *p, double target, const double *pref, double cost) {
  double s[5];
  std::memcpy(s, first, sizeof(s));
  double steady_raw = p[0] * pref[0] + p[1] * pref[1];
  double steady_error = (steady_raw - target) / .01;
  auto tick = [&](double a, double b) {
    step(s, p, a, b);
    double error = (s[3] - target) / .01;
    cost += .008 * (error * error - steady_error * steady_error);
  };
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

extern "C" double paired_cost(const double *initial, const double *p, double target,
                              const double *pref, int count, double c0, double c1, double *first) {
  double s[5];
  double cost = command_cost(initial, p, target, pref, count, c0, c1, s);
  if (first) std::memcpy(first, s, sizeof(s));
  return return_cost(s, p, target, pref, cost);
}

extern "C" void paired_select(const double *initial, const double *p, double target,
                              const double *pref, int count, const double *c0s, int n0,
                              const double *c1s, int n1, int preserve_now, double *result) {
  double best = 1e300, best_move = 1e300, best_remaining = 1e300;
  double first[5];
  // Slew clipping makes different command fields reach identical states. Reuse
  // their exact return cost within this selection only. Include the prefix cost
  // so the original floating-point accumulation and tie breaks are preserved.
  std::map<std::array<double, 6>, double> costs;
  auto finish = [&](double cost) {
    if (!std::isfinite(cost)) return return_cost(first, p, target, pref, cost);
    std::array<double, 6> key = {first[0], first[1], first[2], first[3], first[4], cost};
    auto entry = costs.emplace(key, 0.0);
    if (entry.second) entry.first->second = return_cost(first, p, target, pref, cost);
    return entry.first->second;
  };
  double max_error = 1e300, anchor_score = 1e300, anchor_move = 1e300, anchor_remaining = 1e300;
  if (preserve_now) {
    // Preserve the C1-anchored policy's immediate target accuracy.
    // An inequality against a feasible reference, not a new gain/deadband.
    for (int i = 0; i < n0; i++) {
      double cost = command_cost(initial, p, target, pref, count, c0s[i], pref[1], first);
      cost = finish(cost);
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
      double cost = command_cost(initial, p, target, pref, count, c0s[i], c1s[j], first);
      if (std::abs(first[3] - target) > max_error + 1e-12) continue;
      // Reject infeasible candidates before simulating their full return.
      cost = finish(cost);
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

// Forecast the recent target trend briefly, then hold. The current-target
// accuracy bound remains the ordinary encoder's feasible reference.
extern "C" void paired_preview_select(const double *initial, const double *p,
                                      const double *targets, const double *prefs, int n,
                                      int count, double max_error, const double *c0s, int n0,
                                      const double *c1s, int n1, double *result) {
  double best = 1e300, best_move = 1e300, best_remaining = 1e300;
  std::map<std::array<double, 6>, double> cache;
  for (int i = 0; i < n0; i++) for (int j = 0; j < n1; j++) {
    double first[5];
    std::memcpy(first, initial, sizeof(first));
    double cost = 0;
    for (int k = 0; k < count; k++) {
      step(first, p, c0s[i], c1s[j]);
      double e = (first[3] - targets[std::min(k + 1, n)]) / .01;
      cost += .008 * e * e;
    }
    // Preserve the ordinary C1-anchored bound against the current target.
    if (std::abs(first[3] - targets[0]) > max_error + 1e-12) continue;
    std::array<double, 6> key = {first[0], first[1], first[2], first[3], first[4], cost};
    auto entry = cache.emplace(key, 0.);
    if (entry.second) {
      double s[5];
      std::memcpy(s, first, sizeof(s));
      for (int k = count; k < n; k++) {
        step(s, p, prefs[2 * (k + 1)], prefs[2 * (k + 1) + 1]);
        double e = (s[3] - targets[k + 1]) / .01;
        cost += .008 * e * e;
      }
      entry.first->second = return_cost(s, p, targets[n], prefs + 2 * n, cost);
    }
    cost = entry.first->second;
    double score = std::nearbyint(cost * 1e12) / 1e12;
    double move = std::abs(c0s[i] - initial[0]) / 5.11 + std::abs(c1s[j] - initial[1]) / .5;
    double remaining = std::abs(c0s[i] - prefs[2 * n]) / 5.11 + std::abs(c1s[j] - prefs[2 * n + 1]) / .5;
    if (score < best || (score == best && (move < best_move || (move == best_move && remaining < best_remaining)))) {
      best = score;
      best_move = move;
      best_remaining = remaining;
      result[0] = c0s[i];
      result[1] = c1s[j];
      result[2] = cost;
      std::memcpy(result + 3, first, sizeof(first));
    }
  }
  result[8] = max_error;
}
