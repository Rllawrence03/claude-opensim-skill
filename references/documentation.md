# Documentation map

## Rules

1. Check `opensim.__version__` before consulting anything.
2. Prefer local introspection for API signatures and XML tags (always matches the
   installed version). Web docs are for concepts and workflows.
3. The unversioned doxygen URL tracks the **latest release** and may be ahead of the
   installed version after a new OpenSim release — flag mismatches to the user.
4. Never use or cite: `simtk-confluence.stanford.edu` (legacy mirror), any OpenSim 3.x
   page, or forum posts older than ~2018 for API specifics (forum posts are fine for
   diagnosing symptoms).

## Local introspection (first resort)

```bash
# API signature / methods for any class
python -c "import opensim; help(opensim.InverseKinematicsTool)"
python -c "import opensim; print([m for m in dir(opensim.Model) if 'arker' in m])"

# Default setup XML for a tool (then edit)
opensim-cmd print-xml InverseKinematicsTool   # 4.x subcommand form
# legacy flag form if the above is unavailable in the installed version:
# ik -PrintSetup

# Documentation for a specific XML tag
opensim-cmd -PropertyInfo InverseKinematicsTool.marker_file
opensim-cmd -PropertyInfo   # lists all registered classes
```

## Web sources

### User documentation (Confluence — current home)

Base: `https://opensimconfluence.atlassian.net/wiki/spaces/OpenSim/`

Fetch note: Atlassian pages sometimes render poorly for scrapers. If a fetch returns
mostly navigation chrome, fall back to the GitHub sources below.

### API reference (Doxygen)

- Latest release: `https://simtk.org/api_docs/opensim/api_docs/`
- One class per page, predictable URL: `.../classOpenSim_1_1<ClassName>.html`
  (e.g., `classOpenSim_1_1InverseKinematicsTool.html`)
- Archived versions exist at versioned paths (e.g., `api_docs24`); prefer the archive
  matching the installed version when they diverge.

### GitHub (machine-readable, reliable)

Base: `https://raw.githubusercontent.com/opensim-org/opensim-core/main/`

- `CHANGELOG.md` — version differences; check here first when code that "used to work" breaks after an upgrade
- `Bindings/Python/examples/` — canonical Python usage patterns
- `OpenSim/Examples/` — C++ examples + example setup files and data

## Task → source lookup

| Task | Introspection | Web |
|---|---|---|
| IK setup file tags | `print-xml InverseKinematicsTool`, `-PropertyInfo` | Confluence "Inverse Kinematics"; doxygen `InverseKinematicsTool` |
| Scale setup / measurement set | `print-xml ScaleTool` | Confluence "Scaling"; doxygen `ScaleTool`, `MarkerPlacer`, `ModelScaler` |
| ID + external loads | `print-xml InverseDynamicsTool`; `-PropertyInfo ExternalLoads.*` | Confluence "Inverse Dynamics" + "External Loads"; doxygen `ExternalLoads`, `ExternalForce` |
| AnalyzeTool / BodyKinematics / MuscleAnalysis | `print-xml AnalyzeTool` | doxygen `AnalyzeTool` + analysis classes |
| Static Optimization | `print-xml AnalyzeTool` (SO is an analysis) | Confluence "Static Optimization" |
| C3D / TRC / STO adapters | `help(opensim.C3DFileAdapter)` etc. | doxygen `C3DFileAdapter`, `TRCFileAdapter`, `STOFileAdapter`, `TimeSeriesTable` |
| OpenSense calibration / IMU IK | `help(opensim.IMUPlacer)`, `help(opensim.IMUInverseKinematicsTool)`, `help(opensim.APDMDataReader)` | Confluence OpenSense pages; doxygen `IMUPlacer`, `IMUInverseKinematicsTool`, `APDMDataReader`, `OpenSenseUtilities` |
| Model editing | `help(opensim.Model)` | doxygen `Model`, `Body`, `Joint`, `Coordinate` |
| Result thresholds | — | `references/qa-troubleshooting.md` (do not re-derive) |

## Version pinning

Record in this file once known:

- Lab OpenSim version: **TODO — fill from `opensim.__version__`**
- Lab Python version: **TODO**
- Install route (conda vs. pip wheel): **TODO**

Until filled, treat 4.5/4.6 as the assumed schema and verify tags via introspection.
