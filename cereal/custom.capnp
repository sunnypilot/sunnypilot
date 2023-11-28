using Cxx = import "./include/c++.capnp";
$Cxx.namespace("cereal");

using Car = import "car.capnp";

@0xb526ba661d550a59;

# custom.capnp: a home for empty structs reserved for custom forks
# These structs are guaranteed to remain reserved and empty in mainline
# cereal, so use these if you want custom events in your fork.

# you can rename the struct, but don't change the identifier

enum LongitudinalPersonalitySP {
  aggressive @0;
  moderate @1;
  standard @2;
  relaxed @3;
}

struct ControlsStateSP @0x81c2f05a394cf4af {
  lateralState @0 :Text;

  lateralControlState :union {
    indiState @1 :LateralINDIState;
    pidState @2 :LateralPIDState;
    angleState @3 :LateralAngleState;
    debugState @4 :LateralDebugState;
    torqueState @5 :LateralTorqueState;
    curvatureState @6 :LateralCurvatureState;

    lqrStateDEPRECATED @7 :LateralLQRState;
  }

  struct LateralINDIState {
  }

  struct LateralPIDState {
  }

  struct LateralAngleState {
  }

  struct LateralDebugState {
  }

  struct LateralTorqueState {
    nnLog @0 :List(Float32);
  }

  struct LateralCurvatureState {
  }

  struct LateralLQRState {
  }
}

struct LongitudinalPlanSP @0xaedffd8f31e7b55d {
  visionTurnControllerState @0 :VisionTurnControllerState;
  visionTurnSpeed @1 :Float32;
  visionCurrentLatAcc @16 :Float32;
  visionMaxPredLatAcc @17 :Float32;

  speedLimitControlState @2 :SpeedLimitControlState;
  speedLimit @3 :Float32;
  speedLimitOffset @4 :Float32;
  distToSpeedLimit @5 :Float32;
  isMapSpeedLimit @6 :Bool;
  speedLimitPercOffset @11 :Bool;
  speedLimitValueOffset @12 :Float32;
  desiredTF @13 :Float32;
  notSpeedLimit @14 :Int16;
  e2eX @15 :List(Float32);
  e2eBlended @18 :Text;

  distToTurn @7 :Float32;
  turnSpeed @8 :Float32;
  turnSpeedControlState @9 :SpeedLimitControlState;
  turnSign @10 :Int16;

  events @19 :List(Car.CarEvent);
  longitudinalPlanSource @20 :LongitudinalPlanSource;

  personality @21 :LongitudinalPersonalitySP;

  enum SpeedLimitControlState {
    inactive @0; # No speed limit set or not enabled by parameter.
    tempInactive @1; # User wants to ignore speed limit until it changes.
    adapting @2; # Reducing speed to match new speed limit.
    active @3; # Cruising at speed limit.
    preActive @4;
  }

  enum VisionTurnControllerState {
    disabled @0; # No predicted substantial turn on vision range or feature disabled.
    entering @1; # A substantial turn is predicted ahead, adapting speed to turn comfort levels.
    turning @2; # Actively turning. Managing acceleration to provide a roll on turn feeling.
    leaving @3; # Road ahead straightens. Start to allow positive acceleration.
  }

  enum LongitudinalPlanSource {
    cruise @0;
    lead0 @1;
    lead1 @2;
    lead2 @3;
    e2e @4;
    turn @5;
    limit @6;
    turnlimit @7;
  }
}

struct LateralPlanSP @0xf35cc4560bbf6ec2 {
  laneWidth @0 :Float32;
  lProb @1 :Float32;
  rProb @2 :Float32;

  dProb @3 :Float32;
  dPathWLinesX @6 :List(Float32);
  dPathWLinesY @7 :List(Float32);

  laneChangePrev @8 :Bool;
  laneChangeEdgeBlock @10 :Bool;

  dynamicLaneProfile @4 :Int8;
  standstillElapsed @5 :Float32;
  dynamicLaneProfileStatus @9 :Bool;
}

struct DriverMonitoringStateSP @0xda96579883444c35 {
  handsOnWheelState @0 :HandsOnWheelState;
  notModified @1 :Float32;

  enum HandsOnWheelState {
    none @0;          # hand on wheel monitoring inactive
    ok @1;            # driver has hands on steering wheel
    minor @2;         # hands off steering wheel for acceptable period
    warning @3;       # hands off steering wheel for warning period
    critical @4;      # # hands off steering wheel for critical period
    terminal @5;      # # hands off steering wheel for terminal period
  }
}

struct LiveMapDataSP @0x80ae746ee2596b11 {
  speedLimitValid @0 :Bool;
  speedLimit @1 :Float32;
  speedLimitAheadValid @2 :Bool;
  speedLimitAhead @3 :Float32;
  speedLimitAheadDistance @4 :Float32;
  turnSpeedLimitValid @5 :Bool;
  turnSpeedLimit @6 :Float32;
  turnSpeedLimitEndDistance @7 :Float32;
  turnSpeedLimitSign @8 :Int16;
  turnSpeedLimitsAhead @9 :List(Float32);
  turnSpeedLimitsAheadDistances @10 :List(Float32);
  turnSpeedLimitsAheadSigns @11 :List(Int16);
  lastGpsTimestamp @12 :Int64;  # Milliseconds since January 1, 1970.
  currentRoadName @13 :Text;
  lastGpsLatitude @14 :Float64;
  lastGpsLongitude @15 :Float64;
  lastGpsSpeed @16 :Float32;
  lastGpsBearingDeg @17 :Float32;
  lastGpsAccuracy @18 :Float32;
  lastGpsBearingAccuracyDeg @19 :Float32;
  dataType @20 :DataType;

  enum DataType {
    default @0;
    offline @1;
    online @2;
  }
}

struct E2eLongStateSP @0xa5cd762cd951a455 {
  status @0 :UInt16;
}

struct CustomReserved6 @0xf98d843bfd7004a3 {
}

struct CustomReserved7 @0xb86e6369214c01c8 {
}

struct CustomReserved8 @0xf416ec09499d9d19 {
}

struct CustomReserved9 @0xa1680744031fdb2d {
}
