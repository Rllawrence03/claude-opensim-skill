#!/usr/bin/env python
"""Check pelvis residuals in ID/SO output vs. Hicks et al. 2015 thresholds.
usage: check_id_residuals.py <id_output.sto> --grf <grf.mot> [--com-height 1.0]
Force threshold: 5% of peak resultant external force.
Moment threshold: 1% of (COM height * peak resultant external force)."""
import sys, argparse
import numpy as np
import opensim as osim

def resultant_peak(grf_path):
    t = osim.TimeSeriesTable(grf_path)
    labels = list(t.getColumnLabels())
    mat = t.getMatrix().to_numpy()
    groups = {}
    for j, lab in enumerate(labels):
        low = lab.lower()
        # Force-vector components follow OpenSim's ExternalForce identifier
        # convention "..._v[xyz]" (e.g. "ground_force_vx"). Point/COP columns
        # ("..._p[xyz]") and torque/moment columns also end in x/y/z but must
        # not be swept into a force group.
        if low.endswith(("_vx", "_vy", "_vz")):
            groups.setdefault(lab[:-1], []).append(j)
    peaks = []
    for pre, idx in groups.items():
        if len(idx) == 3:
            peaks.append(np.nanmax(np.linalg.norm(mat[:, idx], axis=1)))
    if not peaks:
        # Fallback for non-standard naming: a single vertical-force-looking
        # column, still excluding point/torque columns.
        fz = [j for j, l in enumerate(labels)
              if l.lower().endswith(("vy", "fz"))
              and "torque" not in l.lower() and "moment" not in l.lower()]
        peaks = [np.nanmax(mat[:, j]) for j in fz] or [np.nan]
    return float(np.nanmax(peaks))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("id_file"); ap.add_argument("--grf", required=True)
    ap.add_argument("--com-height", type=float, default=1.0,
                    help="approx standing COM height in m (default 1.0)")
    a = ap.parse_args()
    peak = resultant_peak(a.grf)
    f_thr, m_thr = 0.05 * peak, 0.01 * a.com_height * peak
    print(f"Peak resultant external force: {peak:.1f} N")
    print(f"Thresholds (Hicks 2015): |F_res| < {f_thr:.1f} N, |M_res| < {m_thr:.2f} N*m")
    t = osim.TimeSeriesTable(a.id_file)
    labels = list(t.getColumnLabels()); mat = t.getMatrix().to_numpy()
    bad = []
    for j, lab in enumerate(labels):
        if not lab.startswith("pelvis_"): continue
        col = np.abs(mat[:, j]); pk, rms = np.nanmax(col), np.sqrt(np.nanmean(col**2))
        is_force = lab.endswith(("_force", "_tx", "_ty", "_tz"))
        thr = f_thr if is_force else m_thr
        mark = " **EXCEEDS**" if pk > thr else ""
        if mark: bad.append(lab)
        print(f"  {lab:28s} RMS={rms:8.2f}  peak={pk:8.2f}  (thr {thr:.2f}){mark}")
    print("RESULT:", "FAIL: " + ", ".join(bad) if bad else "residuals within Hicks 2015 thresholds")

if __name__ == "__main__":
    main()
