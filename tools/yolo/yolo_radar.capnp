# MIT: RadarData layout from sunnypilot/opendbc ccnc-port-radar-tracks.
# Isolated schema IDs preserve extended source metadata without changing car schemas.
@0xc3ff973bc6bf00a1;
struct RadarData @0xc8d8f7ee713e964d {
  errors @3 :Error;
  points @1 :List(RadarPoint);
  trackSources @4 :List(RadarTrackSource);
  radarTracksAvailable @5 :Bool;

  struct RadarTrackSource {
    startAddress @0 :UInt16;
    endAddress @1 :UInt16;
    bus @2 :UInt8;
    trackCount @3 :UInt16;
  }

  struct Error {
    canError @0 :Bool;
    radarFault @1 :Bool;
    wrongConfig @2 :Bool;
    radarUnavailableTemporary @3 :Bool;  # radar data is temporarily unavailable due to conditions the car sets
  }

  # similar to LiveTracks
  struct RadarPoint {
    # all fields required
    trackId @0 :UInt64;  # no trackId reuse
    dRel @1 :Float32;    # m from the front bumper of the car
    yRel @2 :Float32;    # m
    vRel @3 :Float32;    # m/s

    # optional radar-provided motion classification:
    # 0 = unknown/unavailable, 1 = stationary, 2 = moving
    motionState @7 :UInt8;

    # optional source metadata for radars that combine multiple CAN ranges
    sourceAddress @8 :UInt16;
    sourceBus @9 :UInt8;

    # number of consecutive radar cycles this track ID has remained valid
    trackAge @10 :UInt16;

    deprecated :group {
      aRel @4 :Float32; # m/s^2
      yvRel @5 :Float32; # m/s
      measured @6 :Bool;  # measurement VS estimate flag
    }
  }

  enum ErrorDEPRECATED {
    canError @0;
    fault @1;
    wrongConfig @2;
  }

  deprecated :group {
    canMonoTimes @2 :List(UInt64);
    errors @0 :List(ErrorDEPRECATED);
  }
}

