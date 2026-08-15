# Lab exemplars (to be populated)

Empty for now. Until the lab's own files are dropped here, the skill falls back to
OpenSim's own current documentation as the known-good baseline for diffing setup
files — see `SKILL.md` §Known-good exemplars:

- `opensim-cmd print-xml <ToolName>` for a schema-correct default matching the
  installed version
- Official example setups on GitHub (`OpenSim/Examples/`,
  `Bindings/Python/examples/` in `opensim-org/opensim-core`) for populated,
  working examples

Optionally, drop the lab's validated, de-identified working files here later for a
baseline that matches this lab's exact conventions (Plug-in Gait -> Rajagopal
markerset mapping, Bertec external loads, etc.) rather than a generic example:

- `scale_setup.xml`, `ik_setup.xml`, `id_setup.xml`, any AnalyzeTool setups
- `markerset.xml` (Plug-in Gait -> Rajagopal mapping) + scale measurement set
- `external_loads_bertec.xml`
- OpenSense: `imu_placer_setup.xml`, `imu_ik_setup.xml`, `apdm_settings.xml`
- Generic Rajagopal `.osim` filename/variant note (do not commit study data)

Remove all subject identifiers and absolute lab paths before adding files.
