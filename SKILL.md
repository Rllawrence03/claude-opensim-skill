---
name: opensim-dev
description: >
  OpenSim musculoskeletal modeling development and troubleshooting assistant for a gait
  biomechanics lab (Rajagopal 2016 model, Plug-in Gait markers, Vicon Nexus, Bertec
  instrumented treadmill, APDM and Vicon Blue Trident IMUs, Cometa EMG, Novel loadsol).
  Use this skill whenever the user mentions OpenSim, OpenSense, opensim-cmd, .osim models,
  scaling, inverse kinematics (IK), inverse dynamics (ID), marker data, TRC/MOT/STO files,
  C3D processing, IMU calibration or IMU-based IK, setup XML files, residuals, or is
  debugging any biomechanics pipeline code that imports opensim — even if they don't say
  "OpenSim" explicitly. Also use for questions about marker error, residual thresholds,
  external loads, or converting motion capture / IMU / EMG / insole data between formats.
---

# OpenSim Development & Troubleshooting

## Purpose and scope

This skill supports **development and troubleshooting**: writing new OpenSim Python
scripts, debugging errors, diagnosing bad results, prototyping on sample data, and
explaining tool behavior.

**It does not operate on production study data.** Guardrails, always in force:

1. Work only in scratch/development directories the user designates.
2. Treat any path that looks like study data (subject IDs, session folders, anything
   the user has not explicitly offered as test data) as **read-only**. Never write
   into, modify, move, or re-run tools inside such directories.
3. Never delete or overwrite `.osim`, `.trc`, `.mot`, `.sto`, `.c3d`, or setup XML
   files you did not create in the current session.
4. When a reproduction case is needed, copy the minimum necessary files into scratch,
   or use OpenSim's shipped example data (Gait2354, OpenSense examples).

## Session start checklist

1. Confirm the environment: `python -c "import opensim; print(opensim.__version__)"`.
   All guidance in references/ is written against the OpenSim 4.5/4.6 schema; if the
   installed version differs, verify tag names with introspection (below) before
   trusting any template.
2. If a command-line workflow is involved, confirm `opensim-cmd --help` runs.

## Consulting documentation (mandatory ordering)

Do **not** rely on training-data recall of the OpenSim API or XML schema — both are
version-sensitive and commonly misremembered. Resolution order:

1. **Local introspection** (always version-correct):
   - `python -c "import opensim; help(opensim.ClassName)"` for API signatures
   - `opensim-cmd print-xml <ToolName>` / `-PrintSetup` for default setup files
   - `opensim-cmd -PropertyInfo ClassName.propertyName` for XML tag documentation
2. **GitHub** (machine-readable, reliable fetch): raw files from
   `github.com/opensim-org/opensim-core` — `CHANGELOG.md`, `Bindings/Python/examples/`,
   `OpenSim/Examples/`.
3. **Web docs** for concepts/workflows: see `references/documentation.md` for the
   task→URL map. Use only the curated URLs there; never cite legacy
   `simtk-confluence.stanford.edu` pages or OpenSim 3.x documentation.

## Reference files — read the relevant one before answering

| File | Read when the task involves |
|---|---|
| `references/documentation.md` | Looking anything up; doc URLs; version pinning |
| `references/api-patterns.md` | Python API code, TimeSeriesTable, file adapters, C3D/TRC/STO/MOT I/O, pandas conversion |
| `references/tools-xml.md` | Scale, IK, ID, AnalyzeTool, StaticOptimization setup files; opensim-cmd; batch patterns |
| `references/opensense.md` | IMU data (APDM or Blue Trident), calibration, IMUPlacer, IMU IK |
| `references/data-sources.md` | Vicon Nexus C3Ds, Plug-in Gait markers, Bertec treadmill GRF, Cometa EMG, Novel loadsol |
| `references/qa-troubleshooting.md` | "Is this result OK?", marker error, residuals, reserves, diagnostic decision trees, citations |

## Diagnostic scripts (run without loading into context)

All read-only; safe on any file. Run with the user's opensim env active.

- `scripts/inspect_c3d.py <file.c3d>` — markers, analog channels, rates, units, frames
- `scripts/inspect_model.py <model.osim>` — coordinates, bodies, markers, muscles, mass
- `scripts/check_ik_errors.py <trial_ik_marker_errors.sto>` — RMS/max errors vs. thresholds
- `scripts/check_id_residuals.py <id_output.sto> --grf <grf.mot>` — residuals vs. Hicks thresholds
- `scripts/sto_to_csv.py <file.sto|.mot>` — dump any OpenSim table to CSV for inspection

## Lab context (defaults to assume unless told otherwise)

- Generic model: **Rajagopal et al. 2016** full-body model
- Marker set: **Plug-in Gait**, mapped to Rajagopal via the lab's `markerset.xml`
  (exemplar in `assets/lab-exemplars/` once provided — see README there)
- Mocap: Vicon Nexus → C3D; GRF from **Bertec FIT 5 instrumented split-belt treadmill**
  (analog channels in the C3D)
- EMG: Cometa Wave Plus (analog channels in C3D or Cometa export)
- IMUs: APDM Opals (native `APDMDataReader`) and Vicon Blue Trident (custom reader
  needed — see `references/opensense.md`)
- Insoles: Novel loadsol (ASCII export)
- OS: Windows; envs managed with conda

## Known-good exemplars

`assets/lab-exemplars/` holds the lab's validated setup XMLs and marker set. When
troubleshooting a failing setup file, **diff against the exemplar first** — most
setup failures are a missing/renamed tag, wrong relative path, or a time-range
mismatch, and the diff finds them faster than reasoning from scratch.

## AddBiomechanics pathway

For quick automated scale+IK+ID (e.g., sanity-checking a manual result), the
browser-based AddBiomechanics service (addbiomechanics.org) accepts the generic
Rajagopal model + marker set + TRCs and returns scaled models and motions
(Werling et al. 2023). This skill covers preparing the upload bundle and parsing
the downloaded results; the service itself cannot be called headlessly. Details in
`references/tools-xml.md` §AddBiomechanics.
