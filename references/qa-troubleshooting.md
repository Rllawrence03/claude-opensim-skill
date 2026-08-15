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
5. Only then consider weights — ask the user for a known-working setup file's
   weights if one exists, otherwise start from an official example

### High ID residuals

1. Check external loads applied at all (identifier/column mismatch ⇒ silent zero
   force; compare column names in the .mot to the identifiers in the XML)
2. Belt/plate assignment and crossover steps (data-sources.md §Force plate /
   instrumented treadmill GRF); also check the moment convention (free moment
   about COP vs. raw about-plate-origin — see the same section)
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
  *IEEE Trans Biomed Eng* 63(10):2068–79. — a widely used generic full-body
  model; note 1-DOF coupled knee and lumped lumbar joint as known limitations
  if it's the model in use.
- **Al Borno M et al. (2022).** OpenSense: An open-source toolbox for
  inertial-measurement-unit-based measurement of lower extremity kinematics over
  long durations. *J NeuroEng Rehabil* 19:22. — IMU-IK validation band.
- **Werling K et al. (2023).** AddBiomechanics: Automating model scaling, inverse
  kinematics, and inverse dynamics from human motion data through sequential
  optimization. *PLoS ONE* 18(11):e0295152.
- **Mihy JA, Wagatsuma M, Cain SM, Hafer JF (2026).** A Functional
  Sensor-to-Segment Calibration Method Reduces the Effects of Varied Sensor
  Placement on Estimates of Segment Angular Excursion. *J Appl Biomech* 42:131–139.
  — source of the IMU placement/calibration guidance in `references/opensense.md`
  §Sensor placement and functional calibration (APDM Opal hardware).
- **Hafer JF, Mihy JA, Hunt A, Zernicke RF, Johnson RT (2023).** Lower Extremity
  Inverse Kinematics Results Differ Between Inertial Measurement Unit- and
  Marker-Derived Gait Data. *J Appl Biomech* 39(3):133–142. — MoCap-vs-IMU
  kinematics comparison in young adults, older adults, and older adults with
  knee osteoarthritis (sagittal hip/knee/ankle differed by stride phase, no
  tool-by-group interaction). Complements the Al Borno 2022 IMU-IK plausibility
  band with population-specific context for older-adult/OA cohorts.
