# OpenSense: IMU calibration and IMU-based IK

Any IMU brand's export converges on the same pipeline once it's a quaternion
orientation table:

```
Native reader (e.g. APDM) ──────┐
Other brand, custom conversion ─┴─> TimeSeriesTableQuaternion (.sto)
    └> IMUPlacer (calibration pose) ─> calibrated .osim with IMU frames
    └> IMUInverseKinematicsTool ─────> ik.mot
```

## Path A: brands with a native OpenSim reader

OpenSim ships `APDMDataReader` for APDM's CSV export, driven by an XML
settings file mapping each sensor (by name/ID in the export header) to an
experimental sensor name:

```xml
<APDMDataReaderSettings>
  <ExperimentalSensors>
    <ExperimentalSensor name="_pelvis">        <!-- leading underscore convention -->
      <name_in_model>pelvis_imu</name_in_model>
    </ExperimentalSensor>
    <!-- one per sensor: torso_imu, femur_r_imu, tibia_r_imu, calcn_r_imu, ... -->
  </ExperimentalSensors>
</APDMDataReaderSettings>
```

```python
reader = osim.APDMDataReader(osim.APDMDataReaderSettings("apdm_settings.xml"))
tables = reader.read("session.csv")
quat = reader.getOrientationsTable(tables)
osim.STOFileAdapterQuaternion.write(quat, "orientations.sto")
```

Sensor names must end up matching `<physical_offset_frame>_imu` names the
placer creates on the model — mismatches fail at IK, not at read time.

Check `dir(osim)` / the doc map (`references/documentation.md`) for other
brands with a native reader (e.g. `XsensDataReader`) before assuming a custom
conversion is needed — native support has grown across OpenSim versions.

## Path B: brands without a native reader (custom conversion)

Build the quaternion table from whatever CSV/export the vendor's software
produces (columns typically include per-sensor quaternion `qw,qx,qy,qz` or
`w,x,y,z`) — for example Vicon Blue Trident's Capture.U export:

```python
import numpy as np, pandas as pd, opensim as osim

def custom_imu_to_quat_table(csv_path, colmap, rate):
    """colmap: {'pelvis_imu': ('q0','q1','q2','q3'), ...} column names per sensor."""
    df = pd.read_csv(csv_path)
    qtable = osim.TimeSeriesTableQuaternion()
    qtable.setColumnLabels(list(colmap.keys()))
    dt = 1.0 / rate
    for i in range(len(df)):
        row = osim.RowVectorQuaternion(len(colmap))
        for j, cols in enumerate(colmap.values()):
            w, x, y, z = (df.iloc[i][c] for c in cols)
            row[j] = osim.Quaternion(w, x, y, z)
        qtable.appendRow(i * dt, row)
    qtable.addTableMetaDataString("DataRate", str(rate))
    return qtable
```

Verify sensor coordinate conventions before trusting output — different export
tools/versions may use a different quaternion component order (w-first vs.
w-last). A quaternion norm ≠ 1 or wildly discontinuous headings = wrong column
map. If this becomes a recurring need for a specific brand, a validated
`<brand>_to_quat_table.py` belongs in `scripts/` once tested against a real
export from that device.

## Sensor placement and functional calibration

Mihy, Wagatsuma, Cain, Hafer 2026 (see qa-troubleshooting.md bibliography)
tested APDM Opal v2 IMUs on pelvis/thigh/shank/foot, comparing assumed vs.
walking-based functional sensor-to-segment calibration across varied
placements:

- **Functional calibration matters most where soft tissue moves most.** Shank
  RMS difference between placements: 15° with assumed calibration vs. **1.5°
  with functional calibration**. Pelvis and thigh showed no significant
  difference between assumed/functional — placement precision matters less
  there.
- After functional calibration, between-sensor angular-excursion RMS
  differences were **< 5°** for most comparisons — use as a rough
  plausibility band when comparing repeat placements or sessions, similar in
  spirit to the marker-IK thresholds in qa-troubleshooting.md.
- **Avoid placing sensors over high soft-tissue-artifact areas** (their
  example: anterior thigh) — soft tissue motion degrades functional
  calibration performance independent of the calibration method.
- This does not replace `references/qa-troubleshooting.md`'s IMU-IK
  plausibility band (Al Borno et al. 2022, joint-angle level) — it's evidence
  for *why* placement/calibration choices matter upstream of that.

## Calibration: IMUPlacer

```python
placer = osim.IMUPlacer("imu_placer_setup.xml")
placer.run(False)          # True = visualize
model = placer.getCalibratedModel()
```

Key setup tags:
- `sensor_to_opensim_rotations` — Euler XYZ (radians) rotating the IMU world
  frame to OpenSim ground. **The most common source of "model walks
  sideways/backwards" or limbs folded wrong.** For a Y-up conversion this is
  often `-1.5707963 0 0`, but verify per setup/vendor, don't assume.
- `base_imu_label` + `base_heading_axis` — heading correction anchor (usually
  pelvis)
- `orientation_file_for_calibration` — quaternion `.sto` of the **static/
  calibration pose**, model posed to match (default pose ≈ neutral standing)

## IMU IK: IMUInverseKinematicsTool

```python
tool = osim.IMUInverseKinematicsTool("imu_ik_setup.xml")
tool.run(False)
```

Tags: `model_file` (the **calibrated** model), `orientations_file`,
`sensor_to_opensim_rotations` (same as calibration), `time_range`,
`<OrientationWeightSet>` for per-sensor weights.

Outputs orientation errors alongside the .mot — same QA logic as marker IK but
in radians of orientation error (see qa-troubleshooting.md for expected
magnitudes from Al Borno et al. 2022).

## Troubleshooting quick table

| Symptom | First check |
|---|---|
| Segments folded/inverted after calibration | `sensor_to_opensim_rotations`; calibration pose vs. model default pose |
| Model drifts in heading over trial | magnetometer disabled/enabled mismatch across sensors; base heading axis |
| IK fails: "sensor not found" | sensor names vs. `*_imu` frame names on calibrated model |
| Jitter/spikes in joint angles | quaternion discontinuities (sign flips) in input table; export gaps |
| Systematic offset in a joint | sensor mounting shifted between calibration and trial |
