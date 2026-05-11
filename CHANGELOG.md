# Changelog — ionworks-schema

All notable changes to this package are documented here. The format
is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this package follows [Semantic Versioning](https://semver.org/).

For platform-wide release notes (Studio, pipeline, SDK, and more),
see [docs.ionworks.com/changelog](https://docs.ionworks.com/changelog).

<!-- New release sections are prepended below by the release-packages skill. -->

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
