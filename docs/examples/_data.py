"""Figure helper for the schema docs examples.

Writing a figure to disk is something the docs build does and a reader does
not, so it lives here rather than inside a script's copyable region.
"""

from pathlib import Path


def save_first_fig(figs: dict, path: Path) -> None:
    """Save the first figure from a ``plot_fit_results()`` output to disk.

    Parameters
    ----------
    figs : dict
        Mapping of plot name to ``(figure, axes)`` tuples, as returned by
        ``FitResult.plot_fit_results()``.
    path : Path
        Destination file path for the saved figure. Parent directories are
        created if they don't already exist. No-op when ``figs`` is empty.
    """
    if not figs:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    next(iter(figs.values()))[0].savefig(path, dpi=110, bbox_inches="tight")
