import numpy as np

from openpilot.tools.clustermaps.analyzer import (
  AnalyzerConfig,
  LocationInterpolator,
  _analyze_impacts,
  _cluster_problem_locations,
  route_to_geojson,
)


def test_location_interpolator():
  location = LocationInterpolator([
    {"t": 0.0, "latitude": 40.0, "longitude": -74.0},
    {"t": 1.0, "latitude": 40.001, "longitude": -73.999},
    {"t": 2.0, "latitude": 40.002, "longitude": -73.998},
  ])

  midpoint = location.at(0.5)
  assert midpoint is not None
  assert midpoint["latitude"] == 40.0005
  assert midpoint["longitude"] == -73.9995
  assert location.at(-0.1) is None
  assert location.at(2.1) is None


def test_impact_detection_finds_synthetic_peak():
  times = np.arange(0.0, 10.0, 0.01)
  vertical = -9.81 + 0.03 * np.sin(times * 11.0)
  vertical[np.argmin(np.abs(times - 5.0))] -= 2.5
  accelerometer = [(float(t), 0.0, 0.0, float(z)) for t, z in zip(times, vertical, strict=True)]
  car_state = [(float(t), 12.0, 0.0, False, False) for t in times]
  track = [{
    "t": float(t),
    "latitude": 40.0 + float(t) * 0.0001,
    "longitude": -74.0,
  } for t in np.arange(0.0, 10.1, 1.0)]

  impacts, _, diagnostics = _analyze_impacts(
    accelerometer,
    car_state,
    LocationInterpolator(track),
    start_time=0.0,
    config=AnalyzerConfig(),
  )

  assert len(impacts) == 1
  assert 4.9 <= impacts[0]["t"] <= 5.1
  assert impacts[0]["peakVerticalMps2"] > 2.0
  assert diagnostics["thresholdMps2"] >= AnalyzerConfig().impact_min_peak_mps2


def test_repeated_locations_require_independent_routes():
  def route(route_id, driver_id, latitude):
    return {
      "id": route_id,
      "driverId": driver_id,
      "layers": {
        "events": [{
          "kind": "impact",
          "latitude": latitude,
          "longitude": -74.0,
          "severity": 1.2,
        }],
        "roughness": [],
      },
    }

  one_route = _cluster_problem_locations([route("a", "driver-a", 40.0)], radius_m=20.0)
  two_routes = _cluster_problem_locations([
    route("a", "driver-a", 40.0),
    route("b", "driver-b", 40.00005),
  ], radius_m=20.0)

  assert one_route == []
  assert len(two_routes) == 1
  assert two_routes[0]["routeCount"] == 2
  assert two_routes[0]["driverCount"] == 2


def test_geojson_contains_route_and_events():
  route = {
    "id": "route-a",
    "label": "Route A",
    "driverId": "driver-a",
    "summary": {"distanceM": 10.0},
    "track": [
      {"latitude": 40.0, "longitude": -74.0},
      {"latitude": 40.001, "longitude": -74.001},
    ],
    "layers": {
      "events": [{
        "kind": "impact",
        "latitude": 40.0005,
        "longitude": -74.0005,
        "severity": 1.3,
      }],
      "roughness": [],
    },
  }

  geojson = route_to_geojson(route)
  assert geojson["type"] == "FeatureCollection"
  assert geojson["features"][0]["geometry"]["type"] == "LineString"
  assert geojson["features"][1]["geometry"]["type"] == "Point"
  assert geojson["features"][1]["properties"]["kind"] == "impact"
