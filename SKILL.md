---
name: opensim-dev
description: >
  OpenSim musculoskeletal modeling development and troubleshooting assistant for gait
  and movement biomechanics work. Defaults to a Rajagopal 2016 model, Plug-in Gait
  markers, Vicon Nexus mocap, a Bertec instrumented treadmill, Cometa EMG, APDM and
  Vicon Blue Trident IMUs, and Novel loadsol insoles — see SKILL.md §Default hardware
  & model to change these for a different setup. Use this skill whenever the user
  mentions OpenSim, OpenSense, opensim-cmd, .osim models, scaling, inverse kinematics
  (IK), inverse dynamics (ID), marker data, TRC/MOT/STO files, C3D processing, IMU
  calibration or IMU-based IK, setup XML files, residuals, or is debugging any
  biomechanics pipeline code that imports opensim — even if they don't say "OpenSim"
  explicitly. Also use for questions about marker error, residual thresholds, external
  loads, or converting motion capture / IMU / EMG / insole data between formats.
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

See §Default hardware & model below for the generic model/marker
set/hardware this skill assumes unless the user says otherwise —
`references/data-sources.md` and `references/opensense.md` are written to be
brand-agnostic so they still apply even when the defaults don't match.

## Checking for updates (once per session)

The first time this skill is used in a conversation, run
`python scripts/check_updates.py` to see whether a newer version of the skill
itself is available on GitHub. Don't run it again for the rest of the session —
once is enough.

- This script only inspects the local git checkout and the `origin` remote; it
  needs no OpenSim environment and no credentials beyond whatever already works
  for `git` (SSH key, cached HTTPS auth).
- If `up_to_date` is `false`, tell the user a newer version is available and
  share the `compare_url` so they can see what changed, then let them decide
  whether to `git pull` — don't pull automatically.
- If the script errors (not a git checkout, no network, remote unreachable,
  etc.), don't surface that to the user — just skip the check silently and
  proceed with whatever OpenSim task they asked for.

## Session start checklist

1. Confirm the environment: `python -c "import opensim; print(opensim.__version__)"`.
   If a specific env/version is already recorded in `references/documentation.md`
   §Version pinning, use that as a starting point. All guidance in references/ is
   written against the OpenSim 4.6 schema; if the installed version differs, verify
   tag names with introspection (below) before trusting any template.
2. If a command-line workflow is involved, confirm `opensim-cmd --help` runs. On
   Windows conda installs, `opensim-cmd.exe` lives in `<env>\Library\bin` and is not
   on PATH by default unless the env is activated — use the full path if needed.

## Consulting documentation (mandatory ordering)

Do **not** rely on training-data recall of the OpenSim API or XML schema — both are
version-sensitive and commonly misremembered. Resolution order:

1. **Local introspection** (always version-correct):
   - `python -c "import opensim; help(opensim.ClassName)"` for API signatures
   - `opensim-cmd print-xml <ToolName>` / `-PrintSetup` for default setup files
   - `opensim-cmd info ClassName` for a class's property list (confirmed current
     subcommand on OpenSim 4.6 via `opensim-cmd --help`; the older `-PropertyInfo`
     flag form does not exist in 4.6)
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
| `references/opensense.md` | IMU data (any brand), calibration, IMUPlacer, IMU IK |
| `references/data-sources.md` | C3D/mocap, marker sets on a generic model, force plate/treadmill GRF, EMG, pressure insoles |
| `references/qa-troubleshooting.md` | "Is this result OK?", marker error, residuals, reserves, diagnostic decision trees, citations |

## Diagnostic scripts (run without loading into context)

All read-only; safe on any file. Run with the user's opensim env active.

- `scripts/inspect_c3d.py <file.c3d>` — markers, analog channels, rates, units, frames
- `scripts/inspect_model.py <model.osim>` — coordinates, bodies, markers, muscles, mass
- `scripts/check_ik_errors.py <trial_ik_marker_errors.sto>` — RMS/max errors vs. thresholds
- `scripts/check_id_residuals.py <id_output.sto> --grf <grf.mot>` — residuals vs. Hicks thresholds
- `scripts/sto_to_csv.py <file.sto|.mot>` — dump any OpenSim table to CSV for inspection

## Default hardware & model

These are the defaults this skill assumes **unless the user's own setup says
otherwise** — treat them as a starting point, not a hard requirement. If the
user mentions different equipment (in conversation, or evident from the files
they're working with), use *that* instead, for the rest of the session at
least. To change the standing defaults for your own setup, edit this section
directly.

- Generic model: **Rajagopal et al. 2016** full-body model
- Marker set: **Plug-in Gait**, mapped to the generic model via a validated
  `markerset.xml` — ask the user for theirs if a marker-mapping question
  comes up
- Mocap: **Vicon Nexus** → C3D; GRF from a **Bertec instrumented split-belt
  treadmill** (analog channels in the C3D)
- EMG: **Cometa Wave Plus** (analog channels in C3D or Cometa's own export)
- IMUs: **APDM Opals** (native `APDMDataReader` — `references/opensense.md`
  Path A) and **Vicon Blue Trident** (custom reader required —
  `references/opensense.md` Path B)
- Insoles: **Novel loadsol** (ASCII export)
- OS: Windows; envs managed with conda

`references/data-sources.md` and `references/opensense.md` describe these
patterns generically (by data type, not brand) so the same guidance applies
whether or not the defaults above match a given user's actual hardware.

## Known-good exemplars

When troubleshooting a failing setup file, **diff against a known-good baseline
first** — most setup failures are a missing/renamed tag, wrong relative path, or a
time-range mismatch, and a diff finds them faster than reasoning from scratch.
Resolution order for the baseline:

1. **Ask the user** whether they have a known-working version of this exact
   file (an earlier trial's setup, a teammate's copy, a version-controlled
   original) — a real working example from their own project beats a generic
   one, and costs nothing to ask for.
2. `opensim-cmd print-xml <ToolName>` — schema-correct default for the *installed*
   version, always available, zero setup. Best default baseline for structural
   issues (missing/renamed/misordered tags).
3. Official example setup files on GitHub — `OpenSim/Examples/` (e.g. Gait2354) and
   `Bindings/Python/examples/` in `opensim-org/opensim-core` (see
   `references/documentation.md`). Useful for seeing a *populated* working example,
   not just an empty schema template.

## AddBiomechanics pathway

For quick automated scale+IK+ID (e.g., sanity-checking a manual result), the
browser-based AddBiomechanics service (addbiomechanics.org) accepts a generic
model (Rajagopal) + marker set + TRCs and returns scaled models and motions
(Werling et al. 2023). This skill covers preparing the upload bundle and parsing
the downloaded results; the service itself cannot be called headlessly. Details in
`references/tools-xml.md` §AddBiomechanics.
