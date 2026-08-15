# External data sources

General troubleshooting patterns for the data types that feed an OpenSim
pipeline. These apply across mocap/EMG/force-plate/insole hardware brands —
the underlying file-format and biomechanics footguns are the same regardless
of vendor. Ask the user what specific hardware/software they're using before
assuming a particular export format or convention.

## C3D from marker-based motion capture

- Marker labels may carry a subject/session prefix (e.g. `Subj01:RASI`) —
  strip before markerset matching.
- Gap-filled vs. raw: pattern/spline fills can create physically impossible
  marker paths that surface later as IK error spikes; when diagnosing
  localized IK error, ask whether the marker was gap-filled in that window.
- Point rate vs. analog rate differ (e.g., 100 vs. 1000–2000 Hz); the C3D
  adapter returns them as separate tables with separate time columns.
- First-frame offsets: trials often don't start at frame 1; time vectors in
  the adapter output reflect this — don't assume t starts at 0.
- Lab/capture-volume frame is often Z-up → rotate to Y-up for OpenSim
  (api-patterns.md).

## Marker sets on a generic model

- A validated `markerset.xml` defines where each physical marker sits on the
  generic model's segments — treat that mapping as settled; don't re-derive
  marker placements from scratch.
- Joint-axis landmark markers (e.g. knee/ankle) typically get high scale/IK
  weight; wand/tracking markers get lower weight and are expected to show
  worse RMS without concern.
- The static trial must contain every marker in the markerset — a missing
  marker in the static capture is a classic scale failure.

## Force plate / instrumented treadmill GRF

- GRF arrives either as analog channels in the C3D or as a separate export
  (per plate/belt: Fx Fy Fz Mx My Mz, or force/COP/torque depending on the
  capture software's export pipeline).
- **Belt/plate assignment**: left/right force → correct foot. Failure modes:
  crossover steps, a foot landing across plates, or plates swapped in the
  external-loads XML. Symptom: ID moments flip sign or double at specific
  gait events.
- **COP artifacts**: COP diverges when vertical force ≈ 0 (swing/unloaded).
  Threshold the vertical force (commonly 10–20 N) and zero force+COP below it
  before writing the GRF `.mot`; otherwise ID gets huge lever arms from
  garbage COP.
- **Moment convention**: check whether the exported moment columns are the
  *free moment about COP* (Mx/My ≈ 0 by definition) or raw moments about the
  plate's own origin — feeding raw about-origin moments straight into an
  `ExternalForce`'s `torque_identifier` (which expects the free moment)
  produces wildly inflated ID residuals that look like a modeling problem but
  are actually a units/frame mismatch in the GRF conversion.
- **Zeroing/drift**: nonzero baseline during unloaded phases = plate not
  zeroed; check before blaming the model for residuals.
- **Filtering**: match GRF low-pass to kinematics cutoff for ID (tools-xml.md).
- **Units**: verify N and N·m vs. raw unconverted voltage (this appears when
  an export pipeline skips the force-plate calibration/conversion step).
- Treadmill ID: forces are in the lab frame, standard ID applies; belt speed
  matters for interpreting joint power and any progression-based metrics.

## Surface EMG

- Identify channels by label; keep a channel→muscle map per collection in the
  analysis code, never by column index.
- Extraction target: filtered envelopes to CSV/MAT for whatever downstream
  processing (MATLAB, NMF, etc.) the user runs — this skill stops at clean EMG
  export.
- No universal default filter chain — conventions vary by lab and hardware.
  Common building blocks: notch filter at mains-hum harmonics, high-pass
  ~20–40 Hz to remove motion artifact, full-wave rectify, low-pass envelope
  (~6–10 Hz), and optional wavelet denoising for SNR. Ask for (or look up) the
  user's specific protocol rather than assuming one; cite the source when a
  specific pipeline is used.
- Footguns: mains noise (50/60 Hz harmonics — inspect PSD before filtering
  decisions); clipped/saturated channels; wireless dropouts (flat-line
  segments, exact-zero runs).

## Pressure/force insoles

- ASCII/CSV export: per-insole vertical force time series (optionally
  regional).
- Uses: gait events outside a lab, kinetic sanity checks, external loads when
  no force plates are available.
- To external loads: vertical force only, applied to `calcn_*`; a fixed point
  under the foot is an approximation — no COP trajectory, so **do not** treat
  insole-based ID as equivalent to plate-based ID; document the limitation in
  any comparison.
- Time sync: usually no hardware sync with the mocap system by default. Sync
  via event (e.g. heel stomps at start/end) and cross-correlate against plate
  Fz or ankle kinematics; always plot the overlay to verify before use.
- Drift/calibration: check standing weight against known body weight at trial
  start.
