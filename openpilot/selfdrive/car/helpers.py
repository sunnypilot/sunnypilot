import capnp
from typing import Any

from openpilot.cereal import custom
from opendbc.car import structs

_FIELDS = '__dataclass_fields__'  # copy of dataclasses._FIELDS


def is_dataclass(obj):
  """Similar to dataclasses.is_dataclass without instance type check checking"""
  return hasattr(obj, _FIELDS)


def _asdictref_inner(obj) -> dict[str, Any] | Any:
  if is_dataclass(obj):
    ret = {}
    for field in getattr(obj, _FIELDS):  # similar to dataclasses.fields()
      ret[field] = _asdictref_inner(getattr(obj, field))
    return ret
  elif isinstance(obj, (tuple, list)):
    return type(obj)(_asdictref_inner(v) for v in obj)
  else:
    return obj


def asdictref(obj) -> dict[str, Any]:
  """
  Similar to dataclasses.asdict without recursive type checking and copy.deepcopy
  Note that the resulting dict will contain references to the original struct as a result
  """
  if not is_dataclass(obj):
    raise TypeError("asdictref() should be called on dataclass instances")

  return _asdictref_inner(obj)


def convert_to_capnp(struct: structs.CarParamsSP | structs.CarStateSP) -> capnp.lib.capnp._DynamicStructBuilder:
  struct_dict = asdictref(struct)

  if isinstance(struct, structs.CarParamsSP):
    struct_capnp = custom.CarParamsSP.new_message(**struct_dict)
  elif isinstance(struct, structs.CarStateSP):
    struct_capnp = custom.CarStateSP.new_message(**struct_dict)
  else:
    raise ValueError(f"Unsupported struct type: {type(struct)}")

  return struct_capnp


def convert_carControlSP(struct: capnp.lib.capnp._DynamicStructReader) -> structs.CarControlSP:
  def convert_lead(src) -> structs.LeadData:
    lead_is_default = not any((
      src.dRel, src.yRel, src.vRel, src.aRel, src.vLead, src.aLeadDEPRECATED, src.dPath, src.vLat,
      src.vLeadK, src.aLeadK, src.fcw, src.status, src.aLeadTau, src.modelProb, src.radar,
      src.radarTrackId != -1,
    ))
    if lead_is_default:
      return structs.LeadData()

    return structs.LeadData(
      dRel=src.dRel,
      yRel=src.yRel,
      vRel=src.vRel,
      aRel=src.aRel,
      vLead=src.vLead,
      dPath=src.dPath,
      vLat=src.vLat,
      vLeadK=src.vLeadK,
      aLeadK=src.aLeadK,
      fcw=src.fcw,
      status=src.status,
      aLeadTau=src.aLeadTau,
      modelProb=src.modelProb,
      radar=src.radar,
      radarTrackId=src.radarTrackId,
    )

  return structs.CarControlSP(
    mads=structs.ModularAssistiveDrivingSystem(
      state=str(struct.mads.state),
      enabled=struct.mads.enabled,
      active=struct.mads.active,
      available=struct.mads.available,
    ),
    params=[
      {"key": param.key, "type": str(param.type), "value": bytes(param.value)}
      for param in struct.params
    ],
    leadOne=convert_lead(struct.leadOne),
    leadTwo=convert_lead(struct.leadTwo),
    intelligentCruiseButtonManagement=structs.IntelligentCruiseButtonManagement(
      state=str(struct.intelligentCruiseButtonManagement.state),
      sendButton=str(struct.intelligentCruiseButtonManagement.sendButton),
      vTarget=struct.intelligentCruiseButtonManagement.vTarget,
    ),
    radarTracks=[
      structs.CarControlSP.RadarTrack(
        trackId=track.trackId,
        dRel=track.dRel,
        yRel=track.yRel,
        vRel=track.vRel,
        motionState=track.motionState,
        age=track.age,
      )
      for track in struct.radarTracks
    ],
    radarTracksActive=struct.radarTracksActive,
  )
