# Changelog — ionworks-schema

All notable changes to this package are documented here. The format
is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this package follows [Semantic Versioning](https://semver.org/).

For platform-wide release notes (Studio, pipeline, SDK, and more),
see [docs.ionworks.com/changelog](https://docs.ionworks.com/changelog).

<!-- New release sections are prepended below by the release-packages skill. -->

## [0.8.1] - 2026-05-29

### Removed
- Dropped the unused ``numpy`` runtime dependency (#752).

## [0.8.0] - 2026-05-28

### Added
- ``costs.WassersteinDistance`` now supports a weighted point-cloud mode for
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
- ``costs.WassersteinDistance`` error metric for data-fit objective
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
