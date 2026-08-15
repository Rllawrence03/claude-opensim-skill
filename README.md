# opensim-dev — Claude Code skill

OpenSim development and troubleshooting skill for gait and movement
biomechanics work. Defaults to a Rajagopal 2016 model, Plug-in Gait markers,
Vicon Nexus mocap, a Bertec instrumented treadmill, Cometa EMG, APDM + Vicon
Blue Trident IMUs, and Novel loadsol insoles — edit `SKILL.md` §Default
hardware & model to change these for a different setup, or just tell Claude
your actual equipment and it'll use that instead. The reference docs describe
each data type's patterns generically, so they still apply even when your
hardware doesn't match the defaults.

**Scope:** development and troubleshooting only. The skill instructs Claude to treat
study data as read-only and to work in scratch directories — it is not a pipeline
executor.

## Install (Claude Code)

Copy or clone this folder into your skills directory:

```bash
# personal skills
git clone https://github.com/Rllawrence03/claude-opensim-dev.git ~/.claude/skills/opensim-dev

# or project-level
git clone https://github.com/Rllawrence03/claude-opensim-dev.git <project>/.claude/skills/opensim-dev
```

Claude Code picks it up automatically; verify with `/skills` or by asking Claude an
OpenSim question.

## Layout

```
opensim-dev/
├── SKILL.md                     # router: scope, guardrails, doc rules
├── references/
│   ├── documentation.md         # doc map: introspection > GitHub > Confluence/doxygen
│   ├── api-patterns.md          # Python API, TimeSeriesTable, C3D/TRC/STO I/O
│   ├── tools-xml.md             # Scale/IK/ID/Analyze setups, opensim-cmd, AddBiomechanics
│   ├── opensense.md             # native + custom IMU readers -> IMUPlacer -> IMU IK
│   ├── data-sources.md          # C3D/mocap, marker sets, force plate/treadmill GRF, EMG, insoles
│   └── qa-troubleshooting.md    # Hicks 2015 thresholds, decision trees, bibliography
├── scripts/                     # read-only diagnostics (run in the opensim conda env)
│   ├── inspect_c3d.py
│   ├── inspect_model.py
│   ├── check_ik_errors.py
│   ├── check_id_residuals.py
│   ├── sto_to_csv.py
│   └── check_updates.py         # stdlib-only; checks this repo against origin, no opensim env needed
```

## Requirements

- Python env with the `opensim` package — see `references/documentation.md`
  §Version pinning for how to record your specific version/env once known.
- `opensim-cmd` for the introspection commands. On Windows conda installs it lives at
  `<env>\Library\bin\opensim-cmd.exe` and is not on PATH unless the env is activated.

## Open TODOs

None currently open.

## Data policy

No participant data in this repo, ever. The skill never writes study data into
the repo itself — known-working reference files come from asking the user for
one in conversation, not from files committed here.
