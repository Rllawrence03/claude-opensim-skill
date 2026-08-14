# QA thresholds, diagnostics, and bibliography

Use these numbers when judging results; cite the source when reporting. Do not
invent thresholds beyond these.

## Verification thresholds

### Marker IK (from `_ik_marker_errors.sto`)

Rule of thumb for gait (OpenSim best-practice guidance; Hicks et al. 2015 frame it
as "within measurement error"):
- RMS marker error: **< 0.02 m** (2 cm)
- Max marker error: **< 0.04 m** (4 cm)
- Anatomical landmarks should sit at the low end; wand/cluster markers (THI/TIB)
  may run higher without concern.

### Inverse dynamics residuals (Hicks et al. 2015)

- Residual forces (FX/FY/FZ on the pelvis): **< 5% of the peak net external force**
  (for gait: peak resultant GRF)
- Residual moments (MX/MY/MZ): **< 1% of (COM height × peak net external force)**

`scripts/check_id_residuals.py` computes both bounds from a GRF file.

### Reserve actuators (Static Optimization / muscle-driven analyses)

- Peak and RMS reserve moment at each joint: **< 5% of the peak net joint moment**
  at that joint (Hicks et al. 2015). Larger ⇒ muscle forces at that joint are not
  trustworthy.

### IMU-based IK (OpenSense)

- Al Borno et al. 2022 validated OpenSense against marker-based mocap in walking:
  lower-limb sagittal joint-angle RMS differences on the order of a few degrees
  (roughly 2–6° depending on joint/condition). Use as the plausibility band —
  results wildly outside it indicate a calibration/rotation problem, not a
  biological finding. Orientation-error outputs should be small (≪ 0.5 rad) and
  stable over the trial; growing error = heading drift.

## Diagnostic decision trees

### High IK marker error

1. One marker or all? → run `scripts/check_ik_errors.py` (per-marker breakdown)
2. One marker → gap-fill artifact, swapped label, or fell-off marker (inspect the
   TRC around the bad window)
3. All markers, all trials → wrong/unscaled model, unit mismatch (mm/m), missing
   Z-up→Y-up rotation
4. All markers, one trial → wrong subject's model, prefix mismatch, corrupted trial
5. Only then consider weights — and start from the lab exemplar's weights

### High ID residuals

1. Check external loads applied at all (identifier/column mismatch ⇒ silent zero
   force; compare column names in the .mot to the identifiers in the XML)
2. Belt/foot assignment and crossover steps (data-sources.md §Bertec)
3. COP artifacts at low vertical force (threshold + zero)
4. Filter mismatch between kinematics and GRF
5. Upstream IK quality (bad kinematics ⇒ bad accelerations ⇒ residuals)
6. Only then consider mass distribution / scaling (Hicks: inertial adjustment)

### "Tool ran but output is nonsense"

- Check `inDegrees` headers, unit headers, and time ranges first — the three most
  common silent corruptions
- Re-run with `osim.Logger.setLevelString("Debug")` and read warnings; OpenSim
  frequently warns rather than errors on the actual problem

## Bibliography (cite these; consult at need via PubMed/DOI)

Software / model / methods anchors:
- **Hicks JL, Uchida TK, Seth A, Rajagopal A, Delp SL (2015).** Is my model good
  enough? Best practices for verification and validation of musculoskeletal models
  and simulations of movement. *J Biomech Eng* 137(2):020905. — source of the
  residual/reserve thresholds above.
- **Delp SL et al. (2007).** OpenSim: open-source software to create and analyze
  dynamic simulations of movement. *IEEE Trans Biomed Eng* 54(11):1940–50.
- **Seth A et al. (2018).** OpenSim: Simulating musculoskeletal dynamics and
  neuromuscular control... *PLoS Comput Biol* 14(7):e1006223. — cite for OpenSim 4.x.
- **Rajagopal A, Dembia CL, DeMers MS, Delp DD, Hicks JL, Delp SL (2016).**
  Full-body musculoskeletal model for muscle-driven simulation of human gait.
  *IEEE Trans Biomed Eng* 63(10):2068–79. — the lab's generic model; note 1-DOF
  coupled knee and lumped lumbar joint as known limitations.
- **Al Borno M et al. (2022).** OpenSense: An open-source toolbox for
  inertial-measurement-unit-based measurement of lower extremity kinematics over
  long durations. *J NeuroEng Rehabil* 19:22. — IMU-IK validation band.
- **Werling K et al. (2023).** AddBiomechanics: Automating model scaling, inverse
  kinematics, and inverse dynamics from human motion data through sequential
  optimization. *PLoS ONE* 18(11):e0295152.

Lab-lineage parameter sources — **TODO, fill at next build session via PubMed**
(do not guess citations; pull real ones and extract the parameters into
data-sources.md):
- J.L. Allen (PI): EMG processing conventions (filter cutoffs, normalization,
  channel sets) from her motor-module papers → becomes the EMG defaults.
- S.M. Cain: IMU methods (placement, filtering, estimation approaches) → IMU
  defaults.
- J.A. Hafer: IMU gait analysis in older adults (sensor placement, gait events,
  validation) → OUTDOORS-relevant defaults.
