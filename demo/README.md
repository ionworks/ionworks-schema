# ionworks-schema Demo

This demo shows how to use `ionworks_schema` to build pipeline configurations.

## Requirements

- `ionworks-schema` - for config generation
- `pybamm` - for synthetic data generation

## Setup

```bash
pip install ionworks-schema pybamm
```

## Usage

```bash
# 1. Generate synthetic data (requires pybamm)
python generate_synthetic_data.py

# 2. Build config using ionworks_schema
python 01_generate_config.py
```

## What This Demonstrates

- Material library access
- Parameter definitions with bounds
- Objective and pipeline construction
- JSON export for API submission
