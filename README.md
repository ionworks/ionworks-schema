# ionworks-schema

Pydantic schemas for building Ionworks pipeline configurations.

## Installation

```bash
pip install ionworks_schema
```

## Usage

```python
from ionworks_schema import (
    Pipeline,
    DataFit,
    MSMRHalfCell,
    Parameter,
    Material,
)
import json

# Access material library for initial parameter values
material = Material.from_library("NMC_VERBRUGGE2017")
initial_params = material.parameter_values

# Build configuration using pydantic schemas
parameter = Parameter(
    initial_value=1.0,
    bounds=(0.5, 2.0),
)

objective = MSMRHalfCell(
    data="db:your-data-uuid",
    options={"model": {"electrode": "positive"}},
)

data_fit = DataFit(
    objectives={"ocp": objective},
    parameters={"capacity": parameter},
)

pipeline = Pipeline(
    elements={"fit": data_fit}
)

# Export to JSON for API submission
config = pipeline.to_config()
with open("pipeline_config.json", "w") as f:
    json.dump(config, f, indent=2)
```

## Schema Classes

Schema classes mirror the ionworkspipeline API:

- `Pipeline` - Pipeline configuration
- `DataFit` - Data fitting configuration
- `Parameter` - Parameter configuration
- `MSMRHalfCell` - MSMR half-cell objective
- `MSMRFullCell` - MSMR full-cell objective
- `Material` - Material with parameter values
- `Library` - Access to built-in material library

## Material Library

Access built-in materials with validated parameter values:

```python
from ionworks_schema import Material, Library

# List available materials
materials = Library.list_materials()

# Get a specific material
nmc = Material.from_library("NMC_VERBRUGGE2017")
print(nmc.parameter_values)
```

## Note

This package provides configuration schemas only. To execute pipelines,
submit your configuration to the Ionworks API.