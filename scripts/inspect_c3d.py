#!/usr/bin/env python
"""Read-only C3D inspector: markers, analog channels, rates, units, frames."""
import sys, opensim as osim

def main(path):
    ad = osim.C3DFileAdapter()
    tables = ad.read(path)
    mk = ad.getMarkersTable(tables)
    an = ad.getAnalogDataTable(tables)
    t = list(mk.getIndependentColumn())
    print(f"== {path} ==")
    print(f"Markers: {mk.getNumColumns()} @ rows {mk.getNumRows()}, "
          f"t = [{t[0]:.3f}, {t[-1]:.3f}] s")
    for k in mk.getTableMetaDataKeys():
        try: print(f"  marker meta {k} = {mk.getTableMetaDataString(k)}")
        except Exception: pass
    print("  labels:", ", ".join(list(mk.getColumnLabels())))
    ta = list(an.getIndependentColumn())
    rate = (len(ta)-1)/(ta[-1]-ta[0]) if len(ta) > 1 else float('nan')
    print(f"Analog: {an.getNumColumns()} channels @ ~{rate:.0f} Hz")
    print("  labels:", ", ".join(list(an.getColumnLabels())))
    try:
        fr = ad.getForcesTable(tables)
        print(f"Forces table: {fr.getNumColumns()} cols "
              f"({', '.join(list(fr.getColumnLabels()))})")
    except Exception as e:
        print(f"Forces table: unavailable ({e})")

if __name__ == "__main__":
    if len(sys.argv) != 2: sys.exit("usage: inspect_c3d.py <file.c3d>")
    main(sys.argv[1])
