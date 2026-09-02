"""Typed result objects a pipeline element returns.

:class:`BaseResults` is the shared base and carries the fitted
``parameter_values``; the subclasses add what their kind of element produces —
an optimizer's cost history, a sampler's chains, a validation's summary stats.
Every result round-trips through :meth:`BaseResults.to_config` and
:func:`from_config`, which dispatches on the stored ``type``.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import ClassVar

_REGISTRY: dict[str, type] = {}

#: Names of the lazily-fetchable fields on :class:`BaseResults`.
_LAZY_FIELDS = ("overlay", "trace", "posterior", "series")


class BaseResults:
    """Base class for typed result objects returned by pipeline elements.

    Subclasses set a unique ``type`` ClassVar and override
    :meth:`to_config` to expose their payload fields.
    """

    type: ClassVar[str] = "element_result"

    def __init__(self, parameter_values: dict | None = None, **_):
        self._parameter_values = dict(parameter_values or {})
        # A backing store and a fetcher slot per lazy field.
        self._overlay: dict | None = None
        self._overlay_fetcher: Callable[[], dict | None] | None = None
        self._trace: list[dict] | None = None
        self._trace_fetcher: Callable[[], list[dict] | None] | None = None
        self._posterior: dict | None = None
        self._posterior_fetcher: Callable[[], dict | None] | None = None
        self._series: dict | None = None
        self._series_fetcher: Callable[[], dict | None] | None = None
        self._no_plots_hint: str | None = None

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        _REGISTRY[cls.type] = cls

    def attach_source(self, fetcher_map: dict) -> None:
        """Register zero-arg fetchers for the lazy fields.

        A fetcher runs when its field is first read and its answer is cached.
        An empty answer is not cached, so a later read retries. It never
        overrides a value already set directly.

        Parameters
        ----------
        fetcher_map : dict
            Mapping of lazy field name (one of ``"overlay"``, ``"trace"``,
            ``"posterior"``, ``"series"``) to a zero-argument callable returning
            that field's value.

        Raises
        ------
        ValueError
            If ``fetcher_map`` contains a key that isn't a recognized lazy
            field.
        """
        unknown = set(fetcher_map) - set(_LAZY_FIELDS)
        if unknown:
            raise ValueError(
                f"Unknown lazy field(s) {sorted(unknown)}; expected one of "
                f"{_LAZY_FIELDS}"
            )
        for name, fetcher in fetcher_map.items():
            setattr(self, f"_{name}_fetcher", fetcher)

    def set_source(self, **fetchers) -> None:
        """Keyword-argument alias for :meth:`attach_source`.

        Parameters
        ----------
        ``**fetchers``
            Same as ``fetcher_map`` in :meth:`attach_source`, passed as
            keyword arguments, e.g. ``set_source(overlay=fetch_overlay)``.
        """
        self.attach_source(fetchers)

    def _read_lazy(self, name: str):
        """Return a lazy field, fetching it once it has something to give.

        An empty answer leaves the fetcher armed, so the next read tries again.
        """
        cached = getattr(self, f"_{name}")
        if cached is not None:
            return cached
        fetcher = getattr(self, f"_{name}_fetcher")
        if fetcher is None:
            return None
        fetched = fetcher()
        if not fetched:
            return fetched
        setattr(self, f"_{name}", fetched)
        setattr(self, f"_{name}_fetcher", None)
        return fetched

    def explain_no_plots(self, message: str) -> None:
        """Set what :meth:`plot_fit_results` says when no plots are stored.

        Parameters
        ----------
        message : str
            Replaces the default explanation.
        """
        self._no_plots_hint = message

    @property
    def overlay(self) -> dict | None:
        """The fit's model-vs-data plots, keyed by objective name.

        Each entry is ``{"type": <objective type>, "plots": [...]}``, where
        ``type`` is the objective's discriminator (``"EIS"``, ``"CycleAgeing"``,
        ...) and each plot carries named ``traces`` plus axis titles — the shape
        documented in :mod:`ionworks_schema.plots`.

        Used by :meth:`plot_fit_results`. ``None`` until populated (directly,
        or lazily via a fetcher registered with :meth:`attach_source`).
        """
        return self._read_lazy("overlay")

    @overlay.setter
    def overlay(self, value: dict | None) -> None:
        self._overlay = value
        self._overlay_fetcher = None

    @property
    def trace(self) -> list[dict] | None:
        """Optimizer trace: list of ``{"best_cost", "cost", "inputs_unscaled"}``.

        Used by :meth:`plot_trace`. ``None`` until populated (directly, or
        lazily via a fetcher registered with :meth:`attach_source`).
        """
        return self._read_lazy("trace")

    @trace.setter
    def trace(self, value: list[dict] | None) -> None:
        self._trace = value
        self._trace_fetcher = None

    @property
    def posterior(self) -> dict | None:
        """Posterior sampling data, populated directly or lazily via a fetcher.

        ``None`` until populated (directly, or lazily via a fetcher
        registered with :meth:`attach_source`).
        """
        return self._read_lazy("posterior")

    @posterior.setter
    def posterior(self, value: dict | None) -> None:
        self._posterior = value
        self._posterior_fetcher = None

    @property
    def series(self) -> dict | None:
        """Raw model-vs-data time series, keyed by objective then source.

        Each entry is ``{source: {channel: [values]}}`` where ``source`` is
        ``"optimal"`` or ``"baseline"`` and the channels are the objective's
        full-resolution data and model traces (e.g. ``"Time [s]"``,
        ``"Voltage [V] (data)"``, ``"Voltage [V] (model)"``). Unlike
        :attr:`overlay` (decimated plot data for figures), this is the numeric
        series to save or analyse.

        ``None`` until populated (directly, or lazily via a fetcher registered
        with :meth:`attach_source`).
        """
        return self._read_lazy("series")

    @series.setter
    def series(self, value: dict | None) -> None:
        self._series = value
        self._series_fetcher = None

    @property
    def parameter_values(self) -> dict:
        return dict(self._parameter_values)

    def __getitem__(self, name: str):
        return self.parameter_values[name]

    def to_config(self) -> dict:
        return {"type": self.type, "parameter_values": self.parameter_values}

    @classmethod
    def from_config(cls, config: dict) -> BaseResults:
        """Instantiate the right :class:`BaseResults` subclass from a config dict.

        Pops ``type``, looks up the subclass via the module-level registry,
        recurses into ``children`` so nested results deserialize to the right
        subclass, and forwards the rest as kwargs.

        Parameters
        ----------
        config : dict
            A result config dict as produced by :meth:`to_config`.

        Returns
        -------
        BaseResults
            An instance of the registered subclass matching ``config["type"]``.

        Raises
        ------
        ValueError
            If ``config`` does not contain a recognized ``type`` key.
        """
        config = dict(config)
        type_ = config.pop("type", None)
        children = config.get("children")
        if isinstance(children, list) and all(isinstance(c, dict) for c in children):
            config["children"] = [cls.from_config(c) for c in children]
        target = _REGISTRY.get(type_)
        if target is None:
            raise ValueError(f"Unknown {cls.__name__} type: {type_!r}")
        return target(**config)

    def plot_fit_results(self) -> dict:
        """Plot measured-vs-model data for each objective in :attr:`overlay`.

        Each objective is drawn by the renderer for its type
        (:func:`ionworks_schema.plots.render`), so a fit's figures look the same
        here as they do in the pipeline that produced them.

        Returns
        -------
        dict
            ``{objective: (fig, axes)}`` for every objective in :attr:`overlay`
            that has plots. An objective the backend stored no plots for is left
            out rather than contributing an empty figure.

        Raises
        ------
        ValueError
            If :attr:`overlay` is ``None``, or if it yields nothing to draw.
        ImportError
            If matplotlib (the ``plot`` extra) is not installed.
        """
        from . import plots as plots_module

        if self.overlay is None:
            raise ValueError(
                "No overlay data available on this result; cannot plot fit results."
            )

        fig_axes: dict = {}
        for objective, entry in self.overlay.items():
            entry = entry if isinstance(entry, dict) else {}
            objective_plots = entry.get("plots") or []
            if not objective_plots:
                continue
            fig, axes = plots_module.render(entry.get("type"), objective_plots)
            fig.suptitle(objective)
            fig_axes[objective] = (fig, axes)
        if not fig_axes:
            raise ValueError(
                self._no_plots_hint
                or "No plots are stored for any objective on this result "
                f"({len(self.overlay)} objective(s) in the overlay), so there is "
                "nothing to draw. A fit stores its model-vs-data overlay only "
                "when it validated its best-fit parameters; one that did not "
                "stores none. Read .overlay to check before plotting."
            )
        return fig_axes

    def plot_trace(self):
        """Plot optimizer convergence from :attr:`trace`.

        Draws the best-cost curve plus a per-parameter staircase of
        ``inputs_unscaled`` across iterations.

        Returns
        -------
        tuple
            ``(fig, axes)`` where ``axes`` has one subplot for the best-cost
            curve followed by one subplot per parameter.

        Raises
        ------
        ValueError
            If :attr:`trace` is ``None``.
        ImportError
            If matplotlib (the ``plot`` extra) is not installed.
        """
        from .plots import _import_matplotlib

        if self.trace is None:
            raise ValueError(
                "No trace data available on this result; cannot plot trace."
            )
        plt = _import_matplotlib()

        param_names = (
            list(self.trace[0]["inputs_unscaled"].keys()) if self.trace else []
        )
        n_axes = 1 + len(param_names)
        fig, axes = plt.subplots(n_axes, 1, sharex=True, figsize=(6, 2 * n_axes))
        if n_axes == 1:
            axes = [axes]

        iterations = list(range(len(self.trace)))
        axes[0].plot(iterations, [row["best_cost"] for row in self.trace])
        axes[0].set_ylabel("best cost")

        for i, name in enumerate(param_names):
            axes[i + 1].step(
                iterations, [row["inputs_unscaled"][name] for row in self.trace]
            )
            axes[i + 1].set_ylabel(name)
        axes[-1].set_xlabel("iteration")

        return fig, axes


# Register the base class too, so a plain BaseResults round-trips via from_config.
_REGISTRY[BaseResults.type] = BaseResults


def from_config(config: dict) -> BaseResults:
    """Instantiate the right :class:`BaseResults` subclass from a config dict.

    Convenience wrapper for :meth:`BaseResults.from_config`, mirroring
    ``ionworkspipeline.results.parse_element_result``; see it for the dispatch
    rules and what an unrecognized ``type`` raises.

    Parameters
    ----------
    config : dict
        A result config dict as produced by :meth:`BaseResults.to_config`.

    Returns
    -------
    BaseResults
        An instance of the registered subclass matching ``config["type"]``.
    """
    return BaseResults.from_config(config)


class ParameterEstimatorResult(BaseResults):
    """DataFit-family result: an optimizer/sampler's fitted parameters plus
    the cost history that produced them.

    Mirrors ``ionworkspipeline.data_fits.results.ParameterEstimatorResult``.
    """

    type: ClassVar[str] = "ParameterEstimatorResult"

    def __init__(
        self,
        parameter_values: dict | None = None,
        *,
        cost: float | None = None,
        samples=None,
        costs=None,
        children: list[ParameterEstimatorResult] | None = None,
        initial_guess: dict | None = None,
        job_id: int | None = None,
        **kwargs,
    ):
        super().__init__(parameter_values=parameter_values, **kwargs)
        self._cost = cost
        self._samples = samples
        self._costs = costs
        # ``None``, not ``[self]`` — a self-reference defeats the GC. The
        # ``children`` property resolves the ``[self]`` default on read.
        self._children = children
        self._initial_guess = initial_guess
        self._job_id = job_id

    @property
    def cost(self) -> float | None:
        return self._cost

    @property
    def samples(self):
        return self._samples

    @property
    def costs(self):
        return self._costs

    @property
    def children(self) -> list[ParameterEstimatorResult]:
        children = self._children
        return [self] if children is None else children

    @property
    def initial_guess(self) -> dict | None:
        return dict(self._initial_guess) if self._initial_guess is not None else None

    @property
    def job_id(self) -> int | None:
        return self._job_id

    def best_results(
        self, num_results: int | None = None
    ) -> list[ParameterEstimatorResult]:
        """Return the best ``num_results`` children, assumed ordered ascending by cost.

        Parameters
        ----------
        num_results : int, optional
            Number of children to return. Defaults to all of ``children``.

        Returns
        -------
        list of ParameterEstimatorResult
            The first ``num_results`` entries of :attr:`children`.

        Raises
        ------
        ValueError
            If ``num_results`` exceeds the number of available children.
        """
        children = self.children
        if num_results is None:
            num_results = len(children)
        if len(children) < num_results:
            raise ValueError(
                f"Only {len(children)} children found. "
                f"Cannot return {num_results} best results."
            )
        return list(children[:num_results])

    def to_config(self) -> dict:
        return {
            **super().to_config(),
            "cost": self._cost,
            "samples": self._samples,
            "costs": self._costs,
            "initial_guess": (
                dict(self._initial_guess) if self._initial_guess is not None else None
            ),
            "job_id": self._job_id,
            # Emit ``None`` for a leaf (not ``[self]``) so parsing re-derives the
            # lazy default instead of duplicating the self-child.
            "children": (
                None
                if self._children is None
                else [child.to_config() for child in self._children]
            ),
        }


class OptimizationResult(ParameterEstimatorResult):
    """DataFit return for deterministic optimizers (CMA-ES, Scipy, ...)."""

    type: ClassVar[str] = "OptimizationResult"

    def __init__(
        self,
        parameter_values: dict | None = None,
        *,
        x=None,
        fun: float | None = None,
        success: bool | None = None,
        message: str | None = None,
        evaluations: int | None = None,
        iterations: int | None = None,
        **kwargs,
    ):
        super().__init__(parameter_values=parameter_values, **kwargs)
        self._x = x
        self._fun = fun
        self._success = success
        self._message = message
        self._evaluations = evaluations
        self._iterations = iterations

    @property
    def x(self):
        return self._x

    @property
    def fun(self) -> float | None:
        return self._fun

    @property
    def success(self) -> bool | None:
        return self._success

    @property
    def message(self) -> str | None:
        return self._message

    @property
    def evaluations(self) -> int | None:
        return self._evaluations

    @property
    def iterations(self) -> int | None:
        return self._iterations

    def to_config(self) -> dict:
        return {
            **super().to_config(),
            "x": self._x,
            "fun": self._fun,
            "success": self._success,
            "message": self._message,
            "evaluations": self._evaluations,
            "iterations": self._iterations,
        }


class EnsembleResult(ParameterEstimatorResult):
    """DataFit return for ensemble-of-points evaluators (grid search, point
    estimate, batch point estimate).
    """

    type: ClassVar[str] = "EnsembleResult"

    def __init__(
        self,
        parameter_values: dict | None = None,
        *,
        x=None,
        method: str | None = None,
        **kwargs,
    ):
        super().__init__(parameter_values=parameter_values, **kwargs)
        self._x = x
        self._method = method

    @property
    def x(self):
        return self._x

    @property
    def method(self) -> str | None:
        return self._method

    def to_config(self) -> dict:
        return {
            **super().to_config(),
            "x": self._x,
            "method": self._method,
        }


class PosteriorResult(ParameterEstimatorResult):
    """DataFit return for MCMC samplers (e.g. Pints)."""

    type: ClassVar[str] = "PosteriorResult"

    #: Payload-keyed cache for :meth:`_posterior_arrays`, so a reassigned
    #: ``posterior`` wins. Class level: subclasses define their own ``__init__``.
    _recovered: tuple | None = None

    def __init__(
        self,
        parameter_values: dict | None = None,
        *,
        chains=None,
        chains_storage_ref: str | None = None,
        log_pdfs=None,
        parameter_names: list[str] | None = None,
        burnin: int = 0,
        method: str | None = None,
        acceptance_rate: float | None = None,
        r_hat: dict[str, float] | None = None,
        ess: dict[str, float] | None = None,
        posterior_summary: dict[str, dict[str, float]] | None = None,
        **kwargs,
    ):
        super().__init__(parameter_values=parameter_values, **kwargs)
        self._chains = chains
        self._chains_storage_ref = chains_storage_ref
        self._log_pdfs = log_pdfs
        if parameter_names is None and parameter_values:
            parameter_names = list(parameter_values.keys())
        self._parameter_names = list(parameter_names or [])
        self._burnin = burnin
        self._method = method
        self._acceptance_rate = acceptance_rate
        self._r_hat = dict(r_hat) if r_hat is not None else None
        self._ess = dict(ess) if ess is not None else None
        self._posterior_summary = (
            {k: dict(v) for k, v in posterior_summary.items()}
            if posterior_summary is not None
            else None
        )

    @property
    def chains(self):
        """``(chain, draw, parameter)`` samples, or ``None`` when unavailable.

        Populates on access like :attr:`overlay` / :attr:`trace` /
        :attr:`posterior`: a fit whose chains were offloaded rebuilds them from
        the :attr:`posterior` payload. :meth:`to_config` still reports them as
        offloaded, so recovering here cannot inline them back onto the wire.
        """
        if self._chains is not None:
            return self._chains
        recovered = self._posterior_arrays()
        return None if recovered is None else recovered[0]

    @property
    def chains_storage_ref(self) -> str | None:
        return self._chains_storage_ref

    def _posterior_arrays(self):
        """``(chains, costs, burnin)`` rebuilt from the :attr:`posterior` payload.

        An offloaded fit's samples arrive keyed by parameter name rather than
        as a ``(chain, draw, parameter)`` array. ``costs`` is ``None`` when the
        payload has no per-draw cost, and the whole result is ``None`` when it
        cannot supply chains.

        Cached against the payload it was built from, so a per-parameter loop
        rebuilds once while a reassigned :attr:`posterior` still takes effect.
        Deliberately not cached into ``_chains``, which stays the wire field
        :meth:`to_config` reads.
        """
        import numpy as np

        payload = self.posterior or {}
        if self._recovered is not None and self._recovered[0] is payload:
            return self._recovered[1]
        samples = payload.get("samples") or {}
        names = self._parameter_names
        if not names or any(name not in samples for name in names):
            return None
        # Keyed by name in `names` order, so the parameter axis matches
        # `parameter_names`; a single-start chain arrives flat, hence atleast_2d.
        chains = np.stack(
            [np.atleast_2d(np.asarray(samples[name], dtype=float)) for name in names],
            axis=-1,
        )
        costs = payload.get("sample_costs")
        self._recovered = (
            payload,
            (
                chains,
                None if costs is None else np.asarray(costs, dtype=float).reshape(-1),
                self._burnin or int(payload.get("sample_burnin") or 0),
            ),
        )
        return self._recovered[1]

    @property
    def x(self):
        """Best-cost sample, for parity with scipy's ``OptimizeResult.x``.

        Falls back to the :attr:`posterior` payload when the chains were
        offloaded. ``None`` when neither can supply samples and costs.
        """
        import numpy as np

        samples, costs = self._samples, self._costs
        if samples is None or costs is None:
            recovered = self._posterior_arrays()
            if recovered is None or recovered[1] is None:
                return None
            chains, costs, _ = recovered
            samples = chains.reshape(-1, chains.shape[-1])
        return samples[int(np.nanargmin(costs))]

    @property
    def log_pdfs(self):
        return self._log_pdfs

    @property
    def parameter_names(self) -> list[str]:
        return list(self._parameter_names)

    @property
    def burnin(self) -> int:
        """Draws per chain this result was constructed with, and serializes.

        Not necessarily the number :meth:`marginal` dropped: when the chains
        were rebuilt from the :attr:`posterior` payload, that payload's own
        ``sample_burnin`` applies instead. Read a marginal's length rather than
        this field to know what was discarded.
        """
        return self._burnin

    @property
    def method(self) -> str | None:
        return self._method

    @property
    def acceptance_rate(self) -> float | None:
        return self._acceptance_rate

    @property
    def r_hat(self) -> dict[str, float] | None:
        return dict(self._r_hat) if self._r_hat is not None else None

    @property
    def ess(self) -> dict[str, float] | None:
        return dict(self._ess) if self._ess is not None else None

    @property
    def posterior_summary(self) -> dict[str, dict[str, float]] | None:
        """Per-parameter ``{mean, std, median, q05, q95}``, if provided."""
        if self._posterior_summary is None:
            return None
        return {k: dict(v) for k, v in self._posterior_summary.items()}

    def marginal(self, name: str):
        """Flattened post-burnin samples for parameter ``name``.

        Parameters
        ----------
        name : str
            Parameter name; must be one of :attr:`parameter_names`.

        Returns
        -------
        numpy.ndarray
            1-D array of samples for ``name`` across all chains, with the
            first :attr:`burnin` draws of each chain dropped.

        Raises
        ------
        ValueError
            If neither :attr:`chains` nor :attr:`posterior` can supply samples.
        KeyError
            If ``name`` is not in :attr:`parameter_names`.
        """
        import numpy as np

        if name not in self._parameter_names:
            raise KeyError(f"Unknown parameter: {name!r}")
        chains, burnin = self._chains, self._burnin
        if chains is None:
            recovered = self._posterior_arrays()
            if recovered is None:
                ref = self._chains_storage_ref
                raise ValueError(
                    "PosteriorResult has no chains and no posterior samples to "
                    "rebuild them from; cannot compute a marginal."
                    + (f" The chains were offloaded to {ref!r}." if ref else "")
                )
            chains, _, burnin = recovered
        else:
            chains = np.asarray(chains)
        idx = self._parameter_names.index(name)
        if burnin and burnin < chains.shape[1]:
            chains = chains[:, burnin:, :]
        return chains[:, :, idx].reshape(-1)

    def credible_interval(self, name: str, level: float = 0.95) -> tuple[float, float]:
        """Equal-tailed credible interval for parameter ``name`` at ``level``.

        Parameters
        ----------
        name : str
            Parameter name; must be one of :attr:`parameter_names`.
        level : float, optional
            Central probability mass to cover. Defaults to 0.95.

        Returns
        -------
        tuple of float
            ``(lower, upper)`` quantile bounds of the marginal distribution.
        """
        import numpy as np

        marginal = self.marginal(name)
        alpha = (1 - level) / 2
        lower = float(np.quantile(marginal, alpha))
        upper = float(np.quantile(marginal, 1 - alpha))
        return lower, upper

    def posterior_mean(self) -> dict[str, float]:
        """Mean of each parameter's post-burnin marginal.

        Reads from :attr:`posterior_summary` when it is present, so it still
        works when the full chains were too large to inline; otherwise computes
        the mean from ``chains``.

        Returns
        -------
        dict of str to float
            ``{parameter_name: mean}``.
        """
        if self._posterior_summary is not None:
            return {k: float(v["mean"]) for k, v in self._posterior_summary.items()}
        import numpy as np

        return {
            name: float(np.mean(self.marginal(name))) for name in self._parameter_names
        }

    def to_config(self) -> dict:
        return {
            **super().to_config(),
            "chains": self._chains,
            "chains_storage_ref": self._chains_storage_ref,
            "log_pdfs": self._log_pdfs,
            "parameter_names": list(self._parameter_names),
            "burnin": self._burnin,
            "method": self._method,
            "acceptance_rate": self._acceptance_rate,
            "r_hat": dict(self._r_hat) if self._r_hat is not None else None,
            "ess": dict(self._ess) if self._ess is not None else None,
            "posterior_summary": (
                {k: dict(v) for k, v in self._posterior_summary.items()}
                if self._posterior_summary is not None
                else None
            ),
        }


class RegressionResult(ParameterEstimatorResult):
    """DataFit return for ``Regressor`` optimizers."""

    type: ClassVar[str] = "RegressionResult"

    def __init__(
        self,
        parameter_values: dict | None = None,
        *,
        x=None,
        results=None,
        **kwargs,
    ):
        super().__init__(parameter_values=parameter_values, **kwargs)
        self._x = x
        self._results = results

    @property
    def x(self):
        return self._x

    @property
    def results(self):
        return self._results

    def to_config(self) -> dict:
        return {
            **super().to_config(),
            "x": self._x,
            "results": self._results,
        }


class PassthroughResult(BaseResults):
    """Wraps elements that return a plain dict / parameter-values mapping."""

    type: ClassVar[str] = "PassthroughResult"


class ValidationResult(BaseResults):
    """Result returned by ``iws.Validation``."""

    type: ClassVar[str] = "ValidationResult"

    def __init__(
        self,
        parameter_values: dict | None = None,
        *,
        validation_results: dict | None = None,
        summary_stats: dict | None = None,
        failed_objectives: dict[str, str] | None = None,
        **kwargs,
    ):
        super().__init__(parameter_values=parameter_values, **kwargs)
        self._validation_results = dict(validation_results or {})
        self._summary_stats = dict(summary_stats or {})
        self._failed_objectives = dict(failed_objectives or {})

    @property
    def validation_results(self) -> dict:
        return dict(self._validation_results)

    @property
    def summary_stats(self) -> dict:
        return dict(self._summary_stats)

    @property
    def failed_objectives(self) -> dict[str, str]:
        return dict(self._failed_objectives)

    def to_config(self) -> dict:
        return {
            **super().to_config(),
            "validation_results": dict(self._validation_results),
            "summary_stats": dict(self._summary_stats),
            "failed_objectives": dict(self._failed_objectives),
        }


__all__ = [
    "BaseResults",
    "EnsembleResult",
    "OptimizationResult",
    "ParameterEstimatorResult",
    "PassthroughResult",
    "PosteriorResult",
    "RegressionResult",
    "ValidationResult",
    "from_config",
]
