# opensim-dev — Claude Code skill

OpenSim development and troubleshooting skill for a gait biomechanics lab
(Rajagopal 2016 model, Plug-in Gait markers, Vicon Nexus, Bertec FIT 5 instrumented
treadmill, APDM + Vicon Blue Trident IMUs, Cometa Wave Plus EMG, Novel loadsol).

**Scope:** development and troubleshooting only. The skill instructs Claude to treat
study data as read-only and to work in scratch directories — it is not a pipeline
executor.

## Install (Claude Code)

Copy or clone this folder into your skills directory:

```bash
# personal skills
git clone <this-repo> ~/.claude/skills/opensim-dev
# or project-level: <project>/.claude/skills/opensim-dev
```

Claude Code picks it up automatically; verify with `/skills` or by asking Claude an
OpenSim question. Alternatively, install the packaged `opensim-dev.skill` file via
the Claude UI.

## Layout

```
opensim-dev/
├── SKILL.md                     # router: scope, guardrails, doc rules
├── references/
│   ├── documentation.md         # doc map: introspection > GitHub > Confluence/doxygen
│   ├── api-patterns.md          # Python API, TimeSeriesTable, C3D/TRC/STO I/O
│   ├── tools-xml.md             # Scale/IK/ID/Analyze setups, opensim-cmd, AddBiomechanics
│   ├── opensense.md             # APDM + Blue Trident -> IMUPlacer -> IMU IK
│   ├── data-sources.md          # Nexus, Plug-in Gait, Bertec, Cometa, loadsol
│   └── qa-troubleshooting.md    # Hicks 2015 thresholds, decision trees, bibliography
├── scripts/                     # read-only diagnostics (run in the opensim conda env)
│   ├── inspect_c3d.py
│   ├── inspect_model.py
│   ├── check_ik_errors.py
│   ├── check_id_residuals.py
│   └── sto_to_csv.py
└── assets/lab-exemplars/        # drop sanitized known-good setup XMLs here (see README there)
```

## Requirements

- Python env with the `opensim` package (4.5/4.6 assumed; pin your version in
  `references/documentation.md`)
- `opensim-cmd` on PATH for the introspection commands

## Open TODOs

- [ ] Pin OpenSim + Python versions in `references/documentation.md`
- [ ] Add sanitized lab setup XMLs + markerset to `assets/lab-exemplars/`
- [ ] Pull Allen / Cain / Hafer citations and extract parameters
      (`references/qa-troubleshooting.md` §Bibliography)
- [ ] Test scripts against a real C3D / APDM / Trident export; add
      `trident_to_quat_table.py` once validated

## Data policy

No participant data in this repo. Exemplar files must be de-identified with lab
paths removed.
