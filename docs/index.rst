######################
Ionworks Schema API
######################

``ionworks_schema`` provides Pydantic schemas for declaratively building
configurations for the Ionworks battery parameterization and simulation
stack. Every runtime class in the pipeline has a matching schema here, so
you can assemble a pipeline configuration from typed objects, serialize it
to a config dict, and submit it to the Ionworks API without installing the
pipeline runtime itself.

For conceptual / mathematical background, see the `Technical Guide
<https://guide.ionworks.com/>`_.

.. note::

   ``.to_config()`` is the only supported serializer. Pydantic's own
   ``.model_dump()`` is **not** a wire format — it omits the ``type``
   discriminator and emits Python attribute names rather than the wire names
   the API expects (``data_input`` rather than ``data``), so it returns a
   dict the Ionworks API may reject. Always build API payloads with
   ``.to_config()``.

Core classes
============

The top-level entry points for assembling a pipeline configuration:

.. autoclass:: ionworks_schema.BaseSchema
    :members:

.. autoclass:: ionworks_schema.Pipeline
    :members:
    :no-index:

.. autoclass:: ionworks_schema.DataFit
    :members:
    :no-index:

.. autoclass:: ionworks_schema.ArrayDataFit
    :members:
    :no-index:

.. autoclass:: ionworks_schema.Parameter
    :members:
    :no-index:

.. autoclass:: ionworks_schema.Library
    :members:
    :no-index:

.. autoclass:: ionworks_schema.Material
    :members:
    :no-index:

.. autoclass:: ionworks_schema.Validation
    :members:
    :no-index:

.. toctree::
    :maxdepth: 2
    :caption: Examples

    source/api/examples/index

Submodule reference
===================

.. toctree::
    :maxdepth: 2

    source/api/objectives
    source/api/calculations
    source/api/data_fit
    source/api/result
    source/api/data_loader
    source/api/plots
    source/api/direct_entries
    source/api/costs
    source/api/priors
    source/api/stats
    source/api/transforms
    source/api/parameter
    source/api/parameter_estimators
    source/api/distribution_samplers
    source/api/library
    source/api/models
    source/api/objective_functions
    source/api/validation
    source/api/core
