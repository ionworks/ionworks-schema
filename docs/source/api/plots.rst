Plots
=====

A result's figures. :class:`~ionworks_schema.plots.PlotConfig` describes *what is
in a panel* — its traces and its axis labels, with no styling — and the renderers
here draw it. A fit's own panels and a result decoded from the API therefore
produce the same figure.

Reach for these directly only when building panels by hand; a result object
plots itself with :meth:`~ionworks_schema.BaseResults.plot_fit_results`, which
picks a renderer by the objective's type.

Plotting needs the optional ``plot`` extra::

    pip install ionworks-schema[plot]

.. automodule:: ionworks_schema.plots
    :members:
    :undoc-members:
    :show-inheritance:
