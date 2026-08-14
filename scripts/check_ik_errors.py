#!/usr/bin/env python
"""Summarize _ik_marker_errors.sto against gait thresholds (RMS<2cm, max<4cm)."""
import sys
import numpy as np
import opensim as osim

RMS_T, MAX_T = 0.02, 0.04  # m; OpenSim gait rule of thumb (see qa-troubleshooting.md)

def main(path):
    t = osim.TimeSeriesTable(path)
    labels = list(t.getColumnLabels())
    mat = t.getMatrix().to_numpy()
    print(f"== {path} ==  ({mat.shape[0]} frames)")
    flags = []
    for j, lab in enumerate(labels):
        col = mat[:, j]
        line = f"  {lab:35s} mean={np.nanmean(col):.4f} max={np.nanmax(col):.4f}"
        if "RMS" in lab and np.nanmax(col) > RMS_T:
            line += f"   ** RMS exceeds {RMS_T} m"; flags.append(lab)
        if "max" in lab.lower() and np.nanmax(col) > MAX_T:
            line += f"   ** max exceeds {MAX_T} m"; flags.append(lab)
        print(line)
    print("RESULT:", "FLAGS: " + ", ".join(flags) if flags else "within gait thresholds")
    print("(Thresholds: RMS<2 cm, max<4 cm — see references/qa-troubleshooting.md)")

if __name__ == "__main__":
    if len(sys.argv) != 2: sys.exit("usage: check_ik_errors.py <ik_marker_errors.sto>")
    main(sys.argv[1])
