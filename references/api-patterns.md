# Python API patterns and file I/O

Verify signatures with `help()` when anything here disagrees with the installed
version. Patterns below target OpenSim 4.5/4.6.

## Environment gotchas (Windows/conda)

- Import failures (`DLL load failed`) usually mean the wrong env is active or a
  numpy ABI mismatch. Check `conda list opensim numpy` in the active env before
  debugging code.
- Paths in setup XMLs are resolved **relative to the setup file's directory** (for
  most tools) — a top source of "file not found" when running from a different CWD.
  When debugging path errors, print the resolved absolute path first.
- Backslashes in XML paths work on Windows but break portability; prefer forward
  slashes.

## TimeSeriesTable fundamentals

Almost all modern I/O goes through `TimeSeriesTable` (double), `TimeSeriesTableVec3`
(markers), or `TimeSeriesTableQuaternion` (IMU orientations).

```python
import opensim as osim
import numpy as np

table = osim.TimeSeriesTable("results.sto")          # also reads .mot
labels = list(table.getColumnLabels())
time = np.array(table.getIndependentColumn())

# Fast full-matrix extraction → numpy
mat = table.getMatrix().to_numpy()                    # (nrows, ncols)

# Single column
col = table.getDependentColumn("knee_angle_r").to_numpy()

# Metadata (units, headers)
meta_keys = table.getTableMetaDataKeys()
units = table.getTableMetaDataString("inDegrees")     # "yes"/"no" for .mot kinematics
```

**Footguns:**
- `.mot` kinematics may be in degrees (`inDegrees=yes`) while the API and `.osim`
  models work in radians. Always check the `inDegrees` header before math.
- `getIndependentColumn()` returns a tuple-like; wrap in `np.array`.
- Vec3 tables must be **flattened** before writing to STO or converting to plain
  numeric matrices: `table.flatten()` (adds `_1,_2,_3` suffixes) — or use
  `TRCFileAdapter` for marker output.

## To pandas

```python
import pandas as pd
def osim_table_to_df(table):
    return pd.DataFrame(table.getMatrix().to_numpy(),
                        index=np.array(table.getIndependentColumn()),
                        columns=list(table.getColumnLabels()))
```

## C3D reading

```python
adapter = osim.C3DFileAdapter()
adapter.setLocationForForceExpression(
    osim.C3DFileAdapter.ForceLocation_CenterOfPressure)  # or _OriginOfForcePlate / _PointOfWrenchApplication
tables = adapter.read("trial.c3d")
markers = adapter.getMarkersTable(tables)    # TimeSeriesTableVec3, mm usually
forces  = adapter.getForcesTable(tables)     # TimeSeriesTableVec3 (per-plate f/p/m)
analog  = adapter.getAnalogDataTable(tables) # EMG + raw force channels live here
```

**Footguns:**
- Marker units: Nexus C3Ds are typically **mm**; TRC for OpenSim tools should carry
  the correct `Units` header (mm is fine if declared). Check
  `markers.getTableMetaDataString("Units")`.
- Coordinate system: Vicon lab frame is usually Z-up; OpenSim models are **Y-up**.
  Rotate before writing TRC (see rotation snippet below).
- Analog vs. point rates differ (e.g., 100 Hz markers, 1000–2000 Hz analog). Never
  assume shared time vectors.
- Marker labels may carry the Nexus subject prefix (`Subj01:RASI`) — strip before
  matching a markerset.

## Rotating a Vec3 table (Z-up → Y-up)

```python
def rotate_table(table_vec3, axis_str, deg):
    R = osim.Rotation(np.deg2rad(deg),
                      osim.CoordinateAxis({"x":0,"y":1,"z":2}[axis_str]))
    for i in range(table_vec3.getNumRows()):
        row = table_vec3.getRowAtIndex(i)
        for j in range(table_vec3.getNumColumns()):
            row[j] = R.multiply(row[j])
# Typical Vicon→OpenSim: rotate -90° about x
```

## Writing files

```python
osim.TRCFileAdapter().write(markers_flat_or_vec3, "trial.trc")   # expects Vec3 table
osim.STOFileAdapter().write(table, "out.sto")                     # flat table
# .mot is STO with a different extension; STOFileAdapter handles it
```

## Model introspection

```python
model = osim.Model("scaled.osim")
state = model.initSystem()                    # required before most queries
[c.getName() for c in model.getCoordinateSet()]
[m.getName() for m in model.getMarkerSet()]
model.getTotalMass(state)
```

`initSystem()` omission is the most common cause of "SimTK Exception: State not
realized" style errors.

## Running tools from Python (vs. opensim-cmd)

```python
ik = osim.InverseKinematicsTool("ik_setup.xml")
ik.setMarkerDataFileName("trial.trc")
ik.set_output_motion_file("trial_ik.mot")
ik.run()
```

Equivalent to `opensim-cmd run-tool ik_setup.xml`. Python route is better for
programmatic edits; cmd route is better for reproducing exactly what the GUI does.
GUI note: the GUI writes a setup file for every run (Tools → Save Settings) — asking
the user for that file is the fastest way to reproduce a GUI result in code.

## Logging

```python
osim.Logger.setLevelString("Debug")   # Off/Critical/Error/Warn/Info/Debug
osim.Logger.addFileSink("opensim.log")
```

Turn on Debug before reproducing any opaque tool failure.
