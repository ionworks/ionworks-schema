# Changelog — ionworks-schema

All notable changes to this package are documented here. The format
is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this package follows [Semantic Versioning](https://semver.org/).

For platform-wide release notes (Studio, pipeline, SDK, and more),
see [docs.ionworks.com/changelog](https://docs.ionworks.com/changelog).

<!-- New release sections are prepended below by the release-packages skill. -->

## [0.25.0] - 2026-09-09

### Added
- `penalize Xj complement bounds` on `iws.objectives.MSMRHalfCellOptions`
  (default `False`) penalizes a reformulated Xj complement that falls outside the
  final Xj bounds. Only used with the `reformulate` method.

### Changed
- `MSMRHalfCell` documents that the capacity origin is carried by the electrode's
  lower excess capacity, and how to seed it.
- `Constraint` and `Penalty` document that a `pybamm.Symbol` ``fun`` is local
  only — it does not survive submission through the API, where the serialized
  symbol is rejected in validation.

## [0.24.1] - 2026-09-08

### Added
- `iws.example_data(name)` returns the path to a small dataset bundled with the
  package, and `iws.list_example_data()` names the ones available. They back the
  worked examples in the documentation, so an example can be copied out and run
  as-is with no download and no network. The datasets are synthetic sample data
  for illustration — substitute your own export, or read a measurement from the
  platform.
- Worked examples in the documentation for current-driven fitting, cycle ageing,
  EIS, and MSMR OCP, each rendered with its figure and runnable from a copy.

## [0.24.0] - 2026-09-07

### Added
- Post-fit analysis is expressible as a pipeline element: `iws.LinearConfidenceInterval`
  for linear confidence intervals and `iws.SobolSensitivity` for Sobol sensitivity.
  Both take the same `objectives` and `parameters` as a `DataFit`, and accept only
  a `PointEstimate` optimizer, since they analyse a fit rather than performing one.
- `iws.ConfidenceIntervalResult` and `iws.SensitivityResult` type their results, so
  intervals and sensitivity indices are reachable off the result object rather than
  by reading raw job metadata.
- An analysis element placed after a `DataFit` with the same objectives and
  parameters picks up the fitted point automatically, so the parameters do not have
  to be restated.

## [0.23.0] - 2026-09-04

### Added
- 33 schema classes that their packages defined but never re-exported are now
  reachable as attributes: 15 in `calculations`, 11 in `objectives`, 5 in
  `models`, plus `direct_entries.BaseInterpolation` and
  `objective_functions.Regularizer`. Every `*Options` companion was affected —
  `iws.objectives.CurrentDrivenOptions`, `iws.models.ECMOptions`,
  `iws.calculations.ElectrodeSOHOptions` and their siblings did not exist as
  attributes at all, so building a fit against a typed options object was not
  possible without reaching into a submodule. `LumpedSPMR` is also newly
  exported alongside its options.

## [0.22.0] - 2026-08-31

### Added
- A typed result hierarchy in the new `ionworks_schema.results` module, exported
  at the top level: `BaseResults` plus `ParameterEstimatorResult`,
  `OptimizationResult`, `EnsembleResult`, `PosteriorResult`, `RegressionResult`,
  `ValidationResult`, and `PassthroughResult`, with `from_config` to rebuild one
  from a config. Results round-trip through `to_config()`/`from_config()` and
  expose `plot_fit_results()` and `plot_trace()`. Plotting needs matplotlib,
  available as an optional extra: `pip install 'ionworks-schema[plot]'`.
- Lazy `overlay`, `trace`, `posterior`, and `series` fields on `BaseResults`,
  fetched on first read and cached. `overlay` gives decimated data suited to
  figures; `series` gives the full-resolution per-objective model-vs-data
  channels as `{objective: {channel: [values]}}` for saving or further analysis.
- A new `ionworks_schema.plots` module describing what a panel contains — its
  traces and axis labels — independently of how it is drawn, so the same
  description backs both the schema's own plotting and the pipeline's.

### Changed
- `StoichiometryLimitsFromCapacity` now rejects a missing `usable capacity` at
  validation time when `particle phases` contains `"2"`, instead of accepting
  the config and failing once the calculation runs. `usable capacity` is
  per direction: a joint-hysteresis fit uses a different value for charge than
  for discharge, so run one calculation per direction with that direction's
  value.
- Requires pybamm 26.8.0.0 or newer.

## [0.21.0] - 2026-08-25

### Added
- `TimeRangeSpec`, and a `time_range` field on `DataPayloadSpec`, describing an
  elapsed-seconds window that pins a `db:` source to the samples it held when
  the run was first pinned. `start` and `end` are `Time [s]` values from the
  first sample rather than wall-clock datetimes, and a window whose `end`
  precedes its `start` is rejected at validation.

### Changed
- Declares support for Python 3.13.

## [0.20.0] - 2026-08-18

### Breaking changes
- The `options` field on every model, objective, and calculation class is now
  a typed options model instead of a free-form `dict[str, Any]`. Unknown or
  misspelt keys are rejected when the class is constructed, instead of being
  silently accepted (and previously ignored) at runtime. Pass a plain `dict`
  as before — it's still validated against the typed schema — or import the
  new `*Options` class (e.g. `ECMOptions`, `CalendarAgeingOptions`,
  `StoichiometryLimitsFromCapacityOptions`) directly for autocomplete and
  static checking.

### Added
- `StoichiometryLimitsFromCapacityOptions` gains `negative voltage limits`,
  `positive voltage limits`, and `usable capacity` options, used to solve the
  shared stoichiometry window for a composite electrode from its lower-excess
  capacity.

## [0.19.0] - 2026-08-11

### Breaking changes
- Simulation objectives (`CalendarAgeing`, `CurrentDriven`, `CycleAgeing`,
  `EIS`, `Pulse`, and any other `SimulationObjective` subclass) now require a
  model, and construction fails without one. Pass it as
  `options={"model": <pybamm model>}`, or name a stored model with
  `options={"parameterized_model_id": <id>}`. Previously an objective with no
  model was accepted and only failed later, once the fit ran.

  ```python
  # before
  obj = iws.objectives.Pulse(data_input="file:gitt.csv")

  # after
  obj = iws.objectives.Pulse(
      data_input="file:gitt.csv", options={"model": "SPM"}
  )
  ```

- A parameter whose value is `None` is now rejected instead of being
  serialised as a null the rest of the stack cannot use. The error names every
  offending key. Give the parameter a value, or omit the key entirely.

- A measurement given as a string must now start with a locator prefix saying
  where to read it from — `file:`, `folder:`, or `db:`. The loader already
  required this and rejected anything else; the rejection now happens when the
  config is built. Rewrite a bare path as `file:path/to/data.csv`.

- A measurement given as a dict is now routed by its keys to a named,
  strictly-validated shape, so a misspelt key or option is rejected at
  construction rather than silently ignored. `time_series`, `steps`, `data`,
  `options`, and `metadata` are consequently reserved: a dict using one of them
  is read as a payload key, not as a column of that name. A dict matching none
  of the named shapes is still accepted as a plain column mapping.

### Added
- `DataLoaderOptions` and `DataLoaderTransforms` schemas, giving the
  measurement-loading option surface a validated, documented type. Both are
  accepted anywhere loader options are taken, alongside a plain mapping.

### Changed
- The design-optimization optimizer field is now typed rather than free-form,
  so an unsupported optimizer is caught at construction.

## [0.18.1] - 2026-08-10

### Changed
- Documented that `MultiCost.calculation_structure` accepts only `None` for
  every value. A `MultiCost` weights and sums what its component costs return,
  so per-variable scoping belongs on those components. Construction does not
  reject a variable list: converting such a config directly to a runtime cost
  raises, while sending it as a stored configuration drops the list and logs a
  warning. Behaviour is unchanged — the constraint was already real but
  undocumented.

## [0.18.0] - 2026-08-06

### Breaking changes
- `MultiCost.costs` now takes a **list of costs** instead of a
  `{cost: weight}` mapping. A bare cost gets weight 1.0; wrap one in the new
  `WeightedCost` to give it another. At least one component is required.

  ```python
  # before
  cost = iws.costs.MultiCost(costs={rmse: 1.0, max_err: 0.25})
  # after
  cost = iws.costs.MultiCost(
      costs=[iws.costs.RMSE(), iws.costs.WeightedCost(iws.costs.Max(), 0.25)]
  )
  ```

  Passing a mapping now raises a `ValueError` naming the accepted form. The
  same change landed in `ionworkspipeline`, so the two packages now describe
  a combined cost the same way.
- `MultiCost.accumulator` is gone. Only summation was ever supported for
  serialization, which is what the field now does unconditionally.
- `MultiCost` rejects `normalization`, `nan_values`, `objective_weights`, and
  `variable_weights`. It only weights and sums what its components return, so
  these never affected the result — set them on the component costs instead.
  Previously they were accepted and silently ignored.

### Added
- `WeightedCost(cost, weight)` pairs a component cost with its weight inside a
  `MultiCost`. It serializes to a bare `{"cost": ..., "weight": ...}` record,
  so a stored config round-trips through `MultiCost.to_config()`.

### Changed
- `ChiSquare`, `GaussianLogLikelihood`, and `DesignFunction` now raise when
  given a field they cannot apply, rather than accepting and ignoring it:
  - `ChiSquare` — `normalization` (fixed at 1), `objective_weights`, and
    `variable_weights` (derived from `variable_standard_deviations`).
  - `GaussianLogLikelihood` — `objective_weights` and `variable_weights`;
    every variable already carries its noise scale via `sigma`.
  - `DesignFunction` — `nan_values` and `variable_weights`; design metrics are
    scalar per objective, so there is no per-variable axis.
- `MultiCost.to_config()` normalizes every component to a
  `{"cost": ..., "weight": ...}` record regardless of how it was constructed,
  so the emitted config always matches what the pipeline parser reads.
- Documented that `RMSE` supports scalar output only, so a `MultiCost`
  containing it needs a scalar optimizer rather than a least-squares one.

## [0.17.2] - 2026-08-03

### Added
- Documented the `ECM` model option `"butler-volmer"` (`"false"` by default).
  When `"true"`, the series overpotential gains a symmetric charge-transfer
  term driven by the new `"Exchange current [A]"` parameter, exposed as the
  `"Charge-transfer overpotential [V]"` variable. The
  `parameter_dependencies` key `"i0"` controls its dependencies and defaults
  to `("soc",)` even when a mapping is supplied, so existing configs keep a
  state-of-charge-dependent exchange current; pass `"i0": ()` for a constant.

### Changed
- `EIS` now inherits from `SimulationObjective` rather than
  `FittingObjective`, matching the other objectives that run a simulation and
  compare against measured data. The accepted arguments are unchanged.

## [0.17.1] - 2026-07-29

### Fixed
- `canonicalize_element_type` now raises the documented `ValueError` when given
  a non-string value, instead of leaking a `TypeError` from the internal alias
  lookup.

## [0.17.0] - 2026-07-28

### Added
- `canonicalize_element_type` and the legacy display-label → wire alias map
  are now owned and exported by `ionworks_schema`, making it the single
  source of truth for element-type wire aliasing. The package does not
  start accepting display labels — `schema_class_for` still rejects them —
  so the contract itself is unchanged.
- `LEGACY_ELEMENT_TYPE_ALIASES` is exported so consumers can derive their
  own alias tables from the schema vocabulary instead of hand-listing it.
- `ionworks_schema.serialize` with `serialize_parameter_value`,
  `serialize_parameters`, `deserialize_parameter_value`, and
  `deserialize_parameters` — the single definition of the parameter wire
  format, so a `ParameterValues`, interpolant, or other pybamm symbol
  round-trips identically wherever it appears in a config.

### Changed
- A `ParameterValues` nested anywhere in a config now serialises through
  the shared helper (dropping citations, flattening `Scalar`s), and
  objectives route their `parameters` field through it, matching how a
  direct entry has always been written.

## [0.16.0] - 2026-07-24

### Added
- Persistent model `simulation_settings` (mesh and solver configuration).

### Changed
- Migrated to numpy 2 and pandas 3; bumped pybamm to 26.7.1.0.

## [0.15.5] - 2026-07-22

### Changed
- ``MSMRHalfCell``: the ``constrain Xj method`` option gained a new
  ``"project"`` mode and its default changed from ``"explicit"`` to
  ``"project"``. With ``"project"`` the complete Xj groups are projected onto
  the bounded simplex so the fitted fractions sum to exactly 1, whereas the
  previous ``"explicit"`` default applied a soft equality constraint that
  could drift. Configs omitting this option now use ``"project"`` (#1304).

## [0.15.4] - 2026-07-20

### Changed
- Raised the ``pydantic`` dependency floor from ``>=2.12.5`` to
  ``>=2.13.4`` (#1284).

## [0.15.3] - 2026-07-16

### Changed
- Documentation only: expanded the ``ECM`` docstring to document the new
  ``options`` keys for throughput-based degradation — ``"capacity"`` and
  ``"resistance scale"`` (``"constant"`` or ``"function"``), and the
  degradation inputs (``"Capacity throughput [A.h]"``, ``"Time [s]"``)
  supplied to a degradation function (#1235).

## [0.15.2] - 2026-07-14

### Changed
- Documentation only: clarified which ``simulation_kwargs`` keys the ``EIS``
  objective honors — only the mesh/discretisation kwargs (``var_pts``,
  ``submesh_types``, ``geometry``, ``spatial_methods``) are applied, so an
  ``EIS`` objective can share a ``simulation_kwargs`` dict with a
  ``CurrentDriven`` / ``Pulse`` objective in the same fit without error
  (#1126).

## [0.15.1] - 2026-07-14

### Changed
- Documentation only: clarified the ``to_config()`` serializer and the
  runtime-object guard in the README and package docs (#1078).

## [0.15.0] - 2026-07-13

### Breaking changes
- Dropped support for Python 3.10; the minimum supported version is now
  Python 3.11 (#1174).

## [0.14.0] - 2026-07-08

### Added
- ``interpolant_lossless`` option on the ``CurrentDriven`` and ``Pulse``
  objectives: when True, the measured current samples are used directly
  for the interpolant (reproducing the input exactly) instead of being
  compressed within ``interpolant_atol`` / ``interpolant_rtol`` (#1104).

### Removed
- ``solver_max_save_points`` option on ``CurrentDriven`` and ``Pulse``,
  which is no longer supported (#1104).

## [0.13.1] - 2026-07-07

### Added
- Parameter-estimator and optimizer schemas (``Nested``,
  ``BayesianOptimization``, ``CMAES``, ``PSO``, ``SOBER``, ``TuRBO``,
  ``XNES``, ``DifferentialEvolution``, ``GridSearch``, and more), so
  least-squares fitting configurations that select an optimizer are
  validated at construction time (#1023).

## [0.13.0] - 2026-06-30

### Added
- ``data_fit.ArrayDataFit`` schema for fits that run independently at
  each value of an independent variable and return the fitted parameter
  as a 2xN array (e.g. diffusivity vs. stoichiometry, parameter vs.
  temperature).

## [0.12.0] - 2026-06-26

### Added
- ``Material`` is now strictly validated, rejecting unknown fields and
  enforcing per-field types (#980).
- Priors, distributions, and samplers are now modelled as discriminated
  unions, so invalid combinations are caught at construction time (#978).

### Changed
- All 1-D interpolant calculations now accept ``"pchip"`` as an
  interpolator option (#1044).
- ``Pipeline.elements`` is now deeply validated against the contract,
  surfacing nested configuration errors earlier (#981, #982).

## [0.11.0] - 2026-06-25

### Breaking changes
- Removed ``num_workers``, ``parallel``, and ``max_batch_size`` from ``DataFit``,
  and ``async_mode`` from ``AskTellOptimizer``. Parallelism is now determined by
  the execution engine rather than these schema fields. Because the schema
  forbids unknown fields, constructing a model with a removed field (e.g.
  ``DataFit(num_workers=...)``) now raises a validation error. Stored configs
  carrying the removed fields are migrated automatically when parsed, so no
  action is needed for existing saved configurations (#949).
- The ``cost`` field on ``DataFit`` and objectives no longer accepts a bare
  cost-name string (e.g. ``cost="RMSE"``). Pass a cost schema instance
  (``iws.costs.SSE()``) or a config dict (``{"type": "SSE"}``) instead (#1015).
- Objectives are now validated against a discriminated union at the schema
  gate: each objective carries a ``type`` tag (e.g. ``"CurrentDriven"``,
  ``"CycleAgeing"``) and unknown objective types or fields are rejected rather
  than silently accepted. Objects built directly (``iws.objectives.X(...)``)
  are unaffected (#962).

### Added
- ``objective_parallelism`` (``"auto"|"on"|"off"``) on ``DataFit`` controls
  objective-level parallelism. Defaults to ``"auto"`` (#949).

## [0.10.0] - 2026-06-16

### Added
- ``GITTModel``: a diffusion-only schema for fitting solid diffusivities
  (and the lumped ohmic resistance) to GITT or pulse-relaxation data (#904).
- dQ/dU outputs on ``ElectrodeBalancing``: new ``dQdU cutoff`` /
  ``dU/dQ cutoff`` options and the ``"Differential capacity [Ah/V]"`` output
  (with masked-axis siblings ``"Voltage [V] (dQdU)"`` /
  ``"Capacity [A.h] (dQdU)"``) so weighted costs (e.g. Wasserstein) can
  compare incremental-capacity curves (#859).
- ``calculation_structure`` field on cost / objective-function schemas
  (e.g. ``SSE``): an explicit objective→variable scoping map (objective
  name to the list of variable names to compute, or ``null`` for all).
  Use it to keep a per-variable cost from consuming variables that only a
  weighted Wasserstein should, such as model-axis dQ/dV arrays whose model
  and data lengths differ by construction (#953).
- ``dQdU model axis`` option on ``ElectrodeBalancing``: additionally emit
  dQ/dV on the model's own full-window voltage axis
  (``"Differential capacity [Ah/V] (model axis)"`` /
  ``"Voltage [V] (model axis)"``) so a weighted cost can position-shift,
  aligning dQ/dV peaks in voltage rather than on the data grid (#953).

### Deprecated
- ``objective_names`` on cost / objective-function schemas — a flat list of
  objective names the cost applies to. Use ``calculation_structure``
  instead; specifying both raises a validation error (#953).

### Fixed
- A bare ``pandas``/``polars`` DataFrame passed to a ``data`` field (objective
  ``data_input``, ``OCPDataInterpolant.data``, Arrhenius calculations) now
  serializes wrapped as ``{"data": <columns>}``, matching what the server parser
  expects. Previously it serialized to a bare column dict and the server rejected
  it with "Required field 'data' missing", forcing callers to hand-wrap as
  ``{"data": df}``. String paths and already-wrapped dicts are unaffected (#1005).

## [0.9.0] - 2026-06-10

### Added
- Bayesian Optimization, TuRBO, and SOBER optimization algorithms (#727).
- ``SimplePipeline`` schema for single-datafit / single-validation runs,
  with accompanying documentation (#658).
- ``solve_kwargs`` on objectives — a generic mapping forwarded to
  ``sim.solve`` (#821).

### Changed
- ``store_first_last`` is now auto-enabled for ``CycleAgeing`` metrics
  that only need the first/last cycle (#828).
- ``CycleAgeing`` objective now supports ``experiment='from data'`` (#834).
- ``CycleAgeing.simulation_kwargs`` documents ``experiment_model_mode``,
  which defaults to ``"unified"`` whenever an experiment is supplied (#862).

## [0.8.2] - 2026-06-05

### Changed
- Documented the ``skip_objective_callbacks`` data-fit option, which
  skips capturing initial/final per-objective fit results for
  performance (#765).
- Documented that ``simulation_kwargs`` on simulation objectives may
  include ``solver_kwargs`` to tune the auto-built solver (#776).

## [0.8.1] - 2026-05-29

### Removed
- Dropped the unused ``numpy`` runtime dependency (#752).

## [0.8.0] - 2026-05-28

### Added
- ``costs.Wasserstein`` now supports a weighted point-cloud mode for
  comparing sparse experimental data against dense simulation outputs (#733).
- ``MSMRFullCell`` data-fit objective now exposes dQ/dU (incremental capacity
  analysis) output alongside the existing voltage curves (#733).
- ``DirectEntry`` now accepts a ``pybamm.ParameterValues`` object directly,
  serializing callable entries to symbolic JSON automatically (#742).

## [0.7.0] - 2026-05-19

### Breaking changes
- Renamed ``maxiters`` to ``max_iterations`` in ``DataFit.options``
  to unify optimiser kwargs across the stack. Update any configs or
  call sites that set ``options={"maxiters": ...}`` to use
  ``options={"max_iterations": ...}`` (#655).

### Added
- ``costs.Wasserstein`` error metric for data-fit objective
  functions (#679).

## [0.6.0] - 2026-05-12

### Breaking changes
- Renamed ``direct_entries.AverageOcp`` to
  ``direct_entries.AverageOCP`` to match the project-wide ``OCP``
  capitalisation (``OCPHalfCell``, ``OCPDataInterpolant``,
  ``OCPMSMRInterpolant``). Update any imports of ``AverageOcp``.
- Removed the opaque ``distribution`` placeholder field from the
  ``stats.Distribution`` base class. Concrete subclasses
  (``Normal``, ``LogNormal``, ``Uniform``, …) never used it, and
  ``to_config()`` continues to emit ``"distribution": "<ClassName>"``
  unchanged, so configs round-trip identically.

### Improved
- Docstrings on the public schema surface re-written for non-technical
  users. ``to_config()`` is now consistently described as the method
  that builds the dict you submit through ``ionworks-api``.
- ``_types`` placeholder classes for optional dependencies
  (``polars``, ``ionworksdata``) simplified to plain sentinel classes
  instead of a nested module-impersonation wrapper.
- Added numpy-style ``Parameters`` blocks to ``Pipeline``,
  ``library.Material``, and ``direct_entries.DirectEntry`` so every
  public schema class surfaces its fields in ``help()`` / IDE
  hovers / Sphinx (#634).
- Fixed LaTeX math rendering in ``calculations`` docstrings — four
  classes (Arrhenius / standard ``DiffusivityFromMSMR{Data,Function}``)
  switched to raw strings so ``\frac`` no longer renders as ``rac``
  (#634).
- Renamed footnote references on ``DiffusivityFromPulse`` and
  ``ElectrodeSOH`` from the anonymous ``[1]_`` to named
  ``[Wang2022]_`` and ``[Mohtat2019]_`` so they don't collide under
  docutils (#634).
- Schema docs site live at
  https://packages.docs.ionworks.com/ionworks-schema/ (vanity URL:
  https://schema.docs.ionworks.com/) (#634).

## [0.5.0] - 2026-05-11

### Added
- Schema gap fixes: new `Constraint`, `Penalty`, `*Options`
  (CMAES/PSO/DE/XNES), `LatinHypercube`, and `Uniform` classes to
  match what pipeline already supports (#509).
- Sphinx documentation skeleton with autodoc + per-submodule
  reference pages and intersphinx cross-links to ionworkspipeline
  (#509).
- `Field(description=...)` enrichment across ~40 classes in
  `objectives`, `data_fit`, `direct_entries`, `costs`,
  `parameter_estimators`, `stats`, `parameter`, `library`,
  `regularizers`, `distribution_samplers`, plus top-level
  `Pipeline` and `Validation` (#509).

### Changed
- `Uniform` now lives only in `distribution_samplers` (resolves the
  previous ambiguity with `iws.Uniform`) (#509).

## [0.4.0] - 2026-04-30

### Breaking changes
- Cost schema restructure with correctness fixes. Existing pipeline
  configs that reference the old cost shape will need to be updated
  to match the new structure.
