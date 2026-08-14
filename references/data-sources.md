# Lab data sources

## Vicon Nexus → C3D

- Marker labels may carry subject prefix (`Subj01:RASI`) — strip before markerset
  matching.
- Gap-filled vs. raw: pattern/spline fills can create physically impossible marker
  paths that surface later as IK error spikes; when diagnosing localized IK error,
  ask whether the marker was gap-filled in that window.
- Point rate vs. analog rate differ (e.g., 100 vs. 1000–2000 Hz); the C3D adapter
  returns them as separate tables with separate time columns.
- First-frame offsets: Nexus trials often start at frame ≠ 1; time vectors in the
  adapter output reflect this — don't assume t starts at 0.
- Lab frame is typically Z-up → rotate to Y-up for OpenSim (api-patterns.md).

## Plug-in Gait marker set on Rajagopal

- Canonical PiG lower-body names: `LASI RASI LPSI RPSI LTHI LKNE LTIB LANK LHEE LTOE`
  (+ right-side R*); full-body adds torso/upper-limb markers.
- The lab `markerset.xml` (exemplar) defines where each PiG marker sits on Rajagopal
  segments — this mapping is validated; don't re-derive marker placements.
- KNE/ANK are joint-axis landmarks (high scale/IK weight); THI/TIB are wand/tracking
  markers (lower weight, expect worse RMS on them without concern).
- Static trial must contain every marker in the markerset; missing medial markers
  (if the lab uses a medial-marker static) is a classic scale failure.

## Bertec FIT 5 instrumented treadmill (GRF)

- GRF arrives as analog channels in the Nexus C3D (per belt: Fx Fy Fz Mx My Mz, or
  force/COP/torque depending on Nexus pipeline export).
- **Belt assignment**: left/right force → correct foot. Failure modes: crossover
  steps, a foot landing across belts, or belts swapped in the external-loads XML.
  Symptom: ID moments flip sign or double at specific gait events.
- **COP artifacts**: COP diverges when vertical force ≈ 0 (swing). Threshold the
  vertical force (commonly 10–20 N) and zero force+COP below it before writing the
  GRF .mot; otherwise ID gets huge lever arms from garbage COP.
- **Zeroing/drift**: nonzero baseline during swing = plate not zeroed; check before
  blaming the model for residuals.
- **Filtering**: match GRF low-pass to kinematics cutoff for ID (tools-xml.md).
- **Units**: verify N and N·m vs. mV (raw unconverted channels appear when the Nexus
  export pipeline skips the force-plate conversion step).
- Treadmill ID: forces are in the lab frame, standard ID applies; belt speed matters
  for interpreting joint power and any progression-based metrics.

## Cometa Wave Plus EMG

- EMG appears in the C3D analog table (or Cometa's own export). Identify channels by
  label; keep a channel→muscle map per collection in the analysis code, never by
  column index.
- Extraction target: filtered envelopes to CSV/MAT for the downstream (MATLAB/NMF)
  pipeline — this skill stops at clean EMG export.
- Default processing (verify against lab conventions / Allen papers — see
  qa-troubleshooting.md bibliography): band-pass (e.g., 20–450 Hz), rectify,
  low-pass envelope; sampling ≥1 kHz.
- Footguns: mains noise (50/60 Hz harmonics — inspect PSD before filtering
  decisions); clipped/saturated channels; wireless dropouts (flat-line segments,
  exact-zero runs).

## Novel loadsol insoles

- ASCII/CSV export: per-insole vertical force time series (optionally regional).
- Uses: gait events outside the lab, kinetic sanity checks, external loads when no
  force plates.
- To external loads: vertical force only, applied to `calcn_*`; a fixed point under
  the foot is an approximation — no COP trajectory, so **do not** treat loadsol-based
  ID as equivalent to plate-based ID; document the limitation in any comparison.
- Time sync: no hardware sync with Nexus by default. Sync via event (heel stomps at
  start/end) and cross-correlate against plate Fz or ankle kinematics; always plot
  the overlay to verify before use.
- Drift/calibration: check standing weight against known body weight at trial start.
