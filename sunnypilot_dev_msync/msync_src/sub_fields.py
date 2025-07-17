import time
import cereal.messaging as messaging
import csv
import os

model_fields = [
    ("frameId", ""),
    ("frameIdExtra", ""),
    ("frameAge", ""),
    ("frameDropPerc", "%"),
    ("timestampEof", "ns"),
    ("modelExecutionTime", "s"),
    ("rawPredictions", "bytes"),
    ("position", "m, s"),
    ("orientation", "rad, s"),
    ("velocity", "m/s, s"),
    ("orientationRate", "rad/s, s"),
    ("acceleration", "m/s^2, s"),
    ("laneLines", "m, s"),
    ("laneLineProbs", "prob"),
    ("laneLineStds", "std"),
    ("roadEdges", "m, s"),
    ("roadEdgeStds", "std"),
    ("leads", "various"),
    ("leadsV3", "various"),
    ("meta", "various"),
    ("confidence", "enum"),
    ("temporalPose", "various"),
    ("action", "various"),
    ("gpuExecutionTimeDEPRECATED", "s"),
    ("navEnabledDEPRECATED", "bool"),
    ("locationMonoTimeDEPRECATED", "ns"),
    ("lateralPlannerSolutionDEPRECATED", "various"),
]

# Define all struct fields and their subfields from the capnp file
model_struct_fields = {
    "LeadDataV2": ["prob", "t", "xyva", "xyvaStd"],
    "LeadDataV3": ["prob", "probTime", "t", "x", "xStd", "y", "yStd", "v", "vStd", "a", "aStd"],
    "MetaData": ["engagedProb", "desirePrediction", "desireState", "disengagePredictions",
                 "hardBrakePredicted", "laneChangeState", "laneChangeDirection",
                 "brakeDisengageProbDEPRECATED", "gasDisengageProbDEPRECATED", "steerOverrideProbDEPRECATED"],
    "DisengagePredictions": ["t", "brakeDisengageProbs", "gasDisengageProbs", "steerOverrideProbs",
                           "brake3MetersPerSecondSquaredProbs", "brake4MetersPerSecondSquaredProbs",
                           "brake5MetersPerSecondSquaredProbs", "gasPressProbs", "brakePressProbs"],
    "Pose": ["trans", "rot", "transStd", "rotStd"],
    "LateralPlannerSolution": ["x", "y", "yaw", "yawRate", "xStd", "yStd", "yawStd", "yawRateStd"],
    "Action": ["desiredCurvature", "desiredAcceleration", "shouldStop"],
    "XYZTData": ["x", "y", "z", "t", "xStd", "yStd", "zStd"]
}

def create_model_sample(sub):
    """
    Reads and processes perception-prediction model messages.
    Writes all ModelDataV2 fields to a CSV file, including units where applicable.
    """
    csv_file = "model_data_v2_output.csv"
    rows = []

    # Process simple fields first
    for field, unit in model_fields:
        value = getattr(sub, field, None)

        # For simple types, add one row
        if not hasattr(value, '__dict__') or isinstance(value, (list, str, int, float, bool)):
            if isinstance(value, (list, dict)):
                value_str = str(value)
            else:
                value_str = str(value) if value is not None else ""

            rows.append({
                "field": field,
                "subfield": field,
                "unit": unit,
                "value": value_str
            })
        else:
            # For complex objects, try to get their attributes
            if hasattr(value, '__dict__'):
                for attr_name in dir(value):
                    if not attr_name.startswith('_'):
                        try:
                            attr_value = getattr(value, attr_name)
                            if not callable(attr_value):
                                if isinstance(attr_value, (list, dict)):
                                    attr_value_str = str(attr_value)
                                else:
                                    attr_value_str = str(attr_value) if attr_value is not None else ""

                                rows.append({
                                    "field": field,
                                    "subfield": attr_name,
                                    "unit": unit,
                                    "value": attr_value_str
                                })
                        except Exception:
                            continue

    # Process struct fields
    for struct_name, subfields in model_struct_fields.items():
        # Try to find this struct in the model data
        struct_obj = None

        # Check if it's a direct field
        if hasattr(sub, struct_name.lower()):
            struct_obj = getattr(sub, struct_name.lower())
        else:
            # Check if it's nested in other fields
            for field, _ in model_fields:
                field_value = getattr(sub, field, None)
                if field_value and hasattr(field_value, '__class__') and struct_name.lower() in field_value.__class__.__name__.lower():
                    struct_obj = field_value
                    break

        if struct_obj:
            for subfield in subfields:
                try:
                    subfield_value = getattr(struct_obj, subfield, None)
                    if isinstance(subfield_value, (list, dict)):
                        subfield_value_str = str(subfield_value)
                    else:
                        subfield_value_str = str(subfield_value) if subfield_value is not None else ""

                    rows.append({
                        "field": struct_name,
                        "subfield": subfield,
                        "unit": "various",
                        "value": subfield_value_str
                    })
                except Exception:
                    continue

    # Write header if file does not exist
    write_header = not os.path.exists(csv_file)
    with open(csv_file, mode='a', newline='') as f:
        if rows:
            fieldnames = ["field", "subfield", "unit", "value"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if write_header:
                writer.writeheader()
            writer.writerows(rows)
