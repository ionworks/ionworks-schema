# Changelog — ionworks-schema

All notable changes to this package are documented here. The format
is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this package follows [Semantic Versioning](https://semver.org/).

For platform-wide release notes (Studio, pipeline, SDK, and more),
see [docs.ionworks.com/changelog](https://docs.ionworks.com/changelog).

<!-- New release sections are prepended below by the release-packages skill. -->

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
