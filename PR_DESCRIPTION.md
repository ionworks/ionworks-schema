# Align ionworks-schema import structure with ionworkspipeline

## Summary

Import structure now matches **ionworkspipeline** (`iwp`): top-level classes that are top-level in the pipeline stay top-level in the schema; objectives are only exposed via the `objectives` submodule. Previously only `MSMRHalfCell` and `MSMRFullCell` were top-level; other objectives (e.g. `CurrentDriven`) required `iws.objectives.*`. This PR makes the API consistent and adds deprecation warnings where behaviour will change.

This is now consistent with the documentation at https://pipeline.docs.ionworks.com/


## Changes

### Top-level (unchanged, no warnings)

- `iws.Pipeline`, `iws.DataFit`, `iws.ArrayDataFit`, `iws.Parameter`, `iws.Library`, `iws.Material`, `iws.BaseSchema`  
  Same as `iwp.Pipeline`, `iwp.DataFit`, etc.

### Objectives (canonical API)

- All objective classes are used via the **objectives submodule**:  
  `iws.objectives.MSMRHalfCell`, `iws.objectives.CurrentDriven`, `iws.objectives.CycleAgeing`, etc.  
  Matches `iwp.objectives.MSMRHalfCell`, `iwp.objectives.CurrentDriven`, etc.

### Deprecation

Top-level access to the following still works but emits a **DeprecationWarning**; use the submodule path instead. They are handled via a single `_TOP_LEVEL_DEPRECATED` map in the package `__init__.py`:

- **Objectives:** `iws.MSMRHalfCell`, `iws.MSMRFullCell` → use `iws.objectives.MSMRHalfCell`, `iws.objectives.MSMRFullCell`.
- **DirectEntry:** `iws.DirectEntry` → use `iws.direct_entries.DirectEntry`.

### Other

- **Entries:** `iws.direct_entries.DirectEntry` (same as `iwp.direct_entries.DirectEntry`). Top-level `iws.DirectEntry` is deprecated (see above).
- **Priors:** `iws.priors.Prior` (same as `iwp.priors.Prior`).
- **Costs:** `iws.costs` added so `iws.costs.RMSE`, `iws.costs.MAE`, etc. match `iwp.costs`.
- **Optimizers:** `iws.optimizers` is an alias for `iws.parameter_estimators` so `iws.optimizers.ScipyMinimize`, etc. match `iwp.optimizers`.
- `base` submodule is exposed so `iws.base` is available; top-level `Pipeline`/`BaseSchema` remain the recommended way.
- Objective names removed from package `__all__`; they are part of `objectives`, not the top-level public API.
- README: import-mapping table (iwp → iws); schema uses singular `data_fit` where pipeline uses `data_fits`.

## Documentation and examples

- **README:** Imports section updated to describe top-level vs `objectives` and the deprecation. Quick start and Material library use `iws.Pipeline`, `iws.DataFit`, `iws.Parameter`, `iws.Library`, `iws.Material` and `iws.objectives.MSMRHalfCell`.
- **Demo** (`demo/01_generate_config.py`): Uses the same pattern so the demo runs without deprecation warnings.

## Migration

- **No change** if you use: `iws.Pipeline`, `iws.DataFit`, `iws.Parameter`, `iws.Library`, `iws.Material`, `iws.objectives.*` for objectives, and `iws.direct_entries.DirectEntry` for entries.
- **Update** if you use deprecated top-level names: switch to `iws.objectives.MSMRHalfCell` / `iws.objectives.MSMRFullCell` for objectives, and `iws.direct_entries.DirectEntry` for entries, to avoid deprecation warnings.
