#!/usr/bin/env python
"""Dump any OpenSim .sto/.mot table to CSV (stdout or file). Read-only on input."""
import sys
import numpy as np
import opensim as osim

def _read_table(path):
    """Quaternion-typed STOs (e.g. IMU orientation tables) raise 'Type mismatch'
    from the plain TimeSeriesTable constructor; the header's DataType line tells
    us which reader to use before we hit that error."""
    is_quat = False
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line.lower() == "endheader":
                break
            if line.lower().startswith("datatype=") and "quaternion" in line.lower():
                is_quat = True
    if is_quat:
        return osim.TimeSeriesTableQuaternion(path), True
    return osim.TimeSeriesTable(path), False

def main(path, out=None):
    t, is_quat = _read_table(path)
    if is_quat:
        labels = ["time"]
        for lab in t.getColumnLabels():
            labels += [f"{lab}_qw", f"{lab}_qx", f"{lab}_qy", f"{lab}_qz"]
        rows = []
        for i in range(t.getNumRows()):
            row = [t.getIndependentColumn()[i]]
            rv = t.getRowAtIndex(i)
            for j in range(t.getNumColumns()):
                q = rv.getElt(0, j)
                row += [q.get(0), q.get(1), q.get(2), q.get(3)]
            rows.append(row)
        mat = np.array(rows)
    else:
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
