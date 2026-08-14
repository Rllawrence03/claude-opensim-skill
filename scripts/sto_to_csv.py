#!/usr/bin/env python
"""Dump any OpenSim .sto/.mot table to CSV (stdout or file). Read-only on input."""
import sys
import numpy as np
import opensim as osim

def main(path, out=None):
    t = osim.TimeSeriesTable(path)
    labels = ["time"] + list(t.getColumnLabels())
    mat = np.column_stack([np.array(t.getIndependentColumn()), t.getMatrix().to_numpy()])
    lines = [",".join(labels)] + [",".join(f"{v:.8g}" for v in row) for row in mat]
    meta = {k: t.getTableMetaDataString(k) for k in t.getTableMetaDataKeys()
            if _safe(t, k)}
    sys.stderr.write(f"# {path}: {mat.shape[0]} rows x {mat.shape[1]} cols; meta={meta}\n")
    text = "\n".join(lines)
    if out: open(out, "w").write(text + "\n"); print(f"wrote {out}")
    else: print(text)

def _safe(t, k):
    try: t.getTableMetaDataString(k); return True
    except Exception: return False

if __name__ == "__main__":
    if len(sys.argv) < 2: sys.exit("usage: sto_to_csv.py <file.sto|.mot> [out.csv]")
    main(*sys.argv[1:3])
