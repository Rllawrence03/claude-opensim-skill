# Tools, setup XML, and workflows

Get a schema-correct default with `opensim-cmd print-xml <ToolName>` and edit from
there, or ask the user for a known-working version of the file if they have one.
Tag documentation: `opensim-cmd info <ClassName>` (confirmed current subcommand
on OpenSim 4.6 — see `references/documentation.md` §Version pinning).

## Workflow spine

```
C3D (mocap) ──> TRC (markers, Y-up) ───────────┐
            └─> GRF .mot + external_loads.xml ─┤
Generic model + markerset ─> Scale ─> scaled.osim
scaled.osim + TRC ────────────────> IK  ─> trial_ik.mot (+ _ik_marker_errors.sto)
scaled.osim + ik.mot + GRF ───────> ID  ─> inverse_dynamics.sto
scaled.osim + ik.mot [+ GRF] ─────> AnalyzeTool (BodyKinematics, MuscleAnalysis, SO)
```

## ScaleTool

Three nested blocks; each can be enabled/disabled independently:

- `<GenericModelMaker>` — generic .osim + markerset file
- `<ModelScaler>` — `<measurements>` (marker-pair based scale factors) and/or manual
  scales; `<marker_file>` = static trial TRC; `<time_range>` must lie inside the trial
- `<MarkerPlacer>` — moves model markers to match the static pose; outputs the
  scaled+adjusted model

Common failures:
- `time_range` outside the static trial → cryptic "no rows in range" errors
- Marker name mismatch between markerset.xml and TRC (case-sensitive; watch for
  subject/session prefixes from the capture software)
- Mass mismatch: `<mass>` must be the subject's measured mass; scaling distributes it
- Units: TRC in mm with `Units mm` header is fine; silent meter/mm confusion produces
  ~1000× scale factors — check `scale_factors` output when a scaled model looks wrong

## InverseKinematicsTool

Key tags: `model_file`, `marker_file`, `time_range`, `output_motion_file`,
`<IKTaskSet>` (per-marker `<IKMarkerTask>` with `weight`, plus optional
`<IKCoordinateTask>`), `report_marker_locations`, `constraint_weight`, `accuracy`.

- Always keep `report_errors` on: `_ik_marker_errors.sto` is the primary QA artifact
  (see qa-troubleshooting.md).
- Weights: order-of-magnitude reasoning only (anatomical landmarks high, wand/cluster
  markers lower). Ask the user for a known-working IK setup if one exists — its
  weights are the best starting point.
- A single misbehaving marker (gap-filled artifact, swapped label) can wreck all
  coordinates — check per-marker errors before touching weights.

## InverseDynamicsTool

Key tags: `model_file`, `coordinates_file` (IK .mot), `external_loads_file`,
`lowpass_cutoff_frequency_for_coordinates`, `time_range`, `output_gen_force_file`.

- **Filter consistency**: kinematics and GRF must be filtered comparably (classic
  artifact: unfiltered GRF + 6 Hz kinematics → impact-phase moment spikes).
  `lowpass_cutoff_frequency_for_coordinates` filters coordinates only; GRF filtering
  happens upstream when writing the .mot.
- `inDegrees` header of the coordinates file must be correct or all results are garbage.

### ExternalLoads XML (split-belt treadmill / two force plates: two forces)

```xml
<ExternalLoads name="treadmill">
  <objects>
    <ExternalForce name="left">
      <applied_to_body>calcn_l</applied_to_body>
      <force_expressed_in_body>ground</force_expressed_in_body>
      <point_expressed_in_body>ground</point_expressed_in_body>
      <force_identifier>ground_force_l_v</force_identifier>
      <point_identifier>ground_force_l_p</point_identifier>
      <torque_identifier>ground_torque_l_</torque_identifier>
    </ExternalForce>
    <ExternalForce name="right"> <!-- same pattern, _r, calcn_r --> </ExternalForce>
  </objects>
  <datafile>trial_grf.mot</datafile>
</ExternalLoads>
```

Identifiers are **column-name prefixes** in the GRF .mot — the #1 external-loads
failure is identifier/column mismatch (tool silently applies zero force; ID runs
"successfully" with absurd results). Verify with `scripts/sto_to_csv.py` on the .mot.

## AnalyzeTool

Container tool; analyses go in `<AnalysisSet>`: `BodyKinematics` (COM — directly
relevant to balance work), `MuscleAnalysis`, `StaticOptimization`, `PointKinematics`,
`ForceReporter`. Needs `coordinates_file` + optionally `external_loads_file`.
`solve_for_equilibrium_for_auxiliary_states` matters for muscle analyses.

Static Optimization notes:
- Append reserve/residual actuators via `<force_set_files>` (don't edit the model)
- Activation bounds and `use_muscle_physiology` change results materially — record
  settings alongside outputs
- Check reserve outputs against thresholds (qa-troubleshooting.md) before trusting
  muscle forces

## Batch pattern (development/testing only — not for production data)

```python
from string import Template
tpl = Template(open("ik_setup_template.xml").read())
for trial in trials:
    xml = tpl.substitute(TRIAL=trial, MODEL=model_path, T0=t0, T1=t1)
    path = f"scratch/{trial}_ik_setup.xml"
    open(path, "w").write(xml)
    osim.InverseKinematicsTool(path).run()
```

Keep generated setups next to outputs — they are the provenance record.

## opensim-cmd quick reference

```bash
opensim-cmd run-tool setup_ik.xml       # run any tool from a setup file
opensim-cmd print-xml ScaleTool         # schema-correct default setup
opensim-cmd info ScaleTool              # list a class's properties
opensim-cmd update-file old.osim new.osim   # migrate old-version files
```

## AddBiomechanics pathway

Automated scale+IK(+ID) as a cross-check on manual results (Werling et al. 2023).
Browser-based (addbiomechanics.org) — no headless API; the skill's role:

**Prep:** a folder with (1) a generic `.osim` (Rajagopal is the model
AddBiomechanics is built around) with the matching markerset attached, (2) one
TRC per trial (Y-up, correct units), (3) optional GRF `.mot` per trial with
matching filenames for ID. Subject mass/height entered on upload.

**Parse results:** download contains scaled `.osim`, per-trial IK `.mot`, marker
errors, and (if GRF given) ID results — read with the standard adapters. Compare
against the manual pipeline with the QA thresholds; AddBiomechanics optimizes mass
distribution, so residuals are typically lower than hand-scaled results.

When to suggest it: second opinion on a suspect scale/IK result; quick processing of
throwaway pilot data. Not a replacement for a validated, purpose-built pipeline.
