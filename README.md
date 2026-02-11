# Ionworks Schema

Pydantic schemas for building Ionworks pipeline configurations.

## Overview

**Ionworks Schema** (`ionworks_schema`) provides the schema for constructing [Ionworks pipeline configurations](https://pipeline.docs.ionworks.com/). Use these classes to define pipelines (data fits, calculations, entries, validations) in Python with validation, then export JSON to submit via the Ionworks API. Pipeline concepts, objectives, and workflows are described in the [Pipeline documentation](https://pipeline.docs.ionworks.com/) and in the [Ionworks documentation](https://docs.ionworks.com).

Pipelines are **executed by submitting configurations** to the Ionworks API. Use the [ionworks-api](https://github.com/ionworks/ionworks-api) Python client to create and run jobs: `pip install ionworks-api`.

## Installation

```bash
pip install ionworks_schema
```

## Quick start

Build a pipeline configuration with schema classes, export to JSON, and submit with the Ionworks API client:

```python
import ionworks_schema as iws
import json

# Define a parameter to fit (name, initial_value, bounds)
parameter = iws.Parameter(
    name="Positive electrode capacity [A.h]",
    initial_value=1.0,
    bounds=(0.5, 2.0),
)

# Objective: MSMR half-cell fit; data can be "db:<measurement_id>" for uploaded data (use objectives submodule)
objective = iws.objectives.MSMRHalfCell(
    data_input="db:your-measurement-id",
    options={"model": {"electrode": "positive"}},
)

data_fit = iws.DataFit(
    objectives={"ocp": objective},
    parameters={"Positive electrode capacity [A.h]": parameter},
)

pipeline = iws.Pipeline(elements={"fit": data_fit})

# Export to JSON for API submission
config = pipeline.to_config()
with open("pipeline_config.json", "w") as f:
    json.dump(config, f, indent=2)

# Submit via ionworks-api (requires credentials and project ID — see ionworks-api README)
# from ionworks import Ionworks
# client = Ionworks()
# job = client.pipeline.create(config)
# client.pipeline.wait_for_completion(job.id, timeout=600)
```

## Schema classes and pipeline elements

Schema classes mirror the pipeline configuration format consumed by the Ionworks pipeline and API. Runtime behavior and options are documented in the [Pipeline user guide](https://pipeline.docs.ionworks.com/) and in the `ionworkspipeline` package (e.g. parsers, `data_fits`, `objectives`).

A pipeline is a top-level **`Pipeline`** with a dictionary of named **elements**. Each element has an `element_type`: `entry`, `data_fit`, `calculation`, or `validation`.

| Role | Schema class | Description |
|------|--------------|-------------|
| **Top-level** | `Pipeline` | Pipeline configuration with named `elements`. |
| **Entry** | `DirectEntry` | Supply fixed parameter values (no fitting or calculation). |
| **Data fit** | `DataFit`, `ArrayDataFit` | Fit model parameters to data; contain `objectives` and `parameters`. |
| **Calculation** | `ionworks_schema.calculations` | Run calculations (e.g. OCP, diffusivity, geometry). See submodule for available classes. |
| **Objectives** | `MSMRHalfCell`, `MSMRFullCell`, `CurrentDriven`, `CycleAgeing`, `CalendarAgeing`, `EIS`, `Pulse`, `Resistance`, `ElectrodeBalancing`, `OCPHalfCell`, and others | Used inside `DataFit.objectives` to define what to fit. Import from `ionworks_schema.objectives` (e.g. `iws.objectives.MSMRHalfCell`). |
| **Parameters** | `Parameter` | `name`, `initial_value`, `bounds` (and optional prior, etc.). Used in `DataFit.parameters`; dict key is the parameter name. |
| **Library** | `Material`, `Library` | Built-in material library for initial parameter values. |

## Material library

Access built-in materials with validated parameter values for use as initial values or entries:

```python
import ionworks_schema as iws

# List available materials
materials = iws.Library.list_materials()

# Get a specific material (e.g. NMC - Verbrugge 2017)
material = iws.Material.from_library("NMC - Verbrugge 2017")
print(material.parameter_values)
```

Parameter names and interpretation are described in the [Pipeline documentation](https://pipeline.docs.ionworks.com/).

## Resources

- [Pipeline documentation](https://pipeline.docs.ionworks.com/) — workflows, objectives, data fits, and pipeline concepts.
- [ionworks-api](https://github.com/ionworks/ionworks-api) — submit and manage pipelines (`pip install ionworks-api`).
- [Ionworks documentation](https://docs.ionworks.com) — product and platform documentation.

## Note

This package provides configuration schemas only. To run pipelines, export JSON with `pipeline.to_config()` and submit it via the Ionworks API using the [ionworks-api](https://github.com/ionworks/ionworks-api) client.
