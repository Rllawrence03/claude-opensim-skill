#!/usr/bin/env python
"""Read-only .osim inspector: coordinates, bodies, markers, muscles, mass."""
import sys, opensim as osim

def main(path):
    m = osim.Model(path)
    s = m.initSystem()
    print(f"== {m.getName()} ({path}) ==")
    print(f"Total mass: {m.getTotalMass(s):.2f} kg")
    print(f"Bodies ({m.getBodySet().getSize()}):",
          ", ".join(m.getBodySet().get(i).getName() for i in range(m.getBodySet().getSize())))
    cs = m.getCoordinateSet()
    print(f"Coordinates ({cs.getSize()}):")
    for i in range(cs.getSize()):
        c = cs.get(i)
        print(f"  {c.getName():25s} [{c.getRangeMin():+.2f}, {c.getRangeMax():+.2f}] "
              f"{'locked' if c.getDefaultLocked() else ''}")
    ms = m.getMarkerSet()
    print(f"Markers ({ms.getSize()}):",
          ", ".join(ms.get(i).getName() for i in range(ms.getSize())))
    mus = m.getMuscles()
    print(f"Muscles: {mus.getSize()}")

if __name__ == "__main__":
    if len(sys.argv) != 2: sys.exit("usage: inspect_model.py <model.osim>")
    main(sys.argv[1])
