# ionworks-schema Demo

This demo shows how to use `ionworks_schema` to build pipeline configurations
and run them with `ionworkspipeline`.

## Requirements

- **Config generation (01_generate_config.py)**: Only requires `ionworks-schema`
- **Config execution (02_run_config.py)**: Requires `ionworkspipeline` (which includes PyBaMM)

## Setup

```bash
# Install ionworks-schema (lightweight, for config generation)
pip install ionworks-schema

# To run the execution demo, also install ionworkspipeline
pip install ionworkspipeline
```

## Usage

```bash
# 1. Generate synthetic data (requires numpy/pandas only)
python generate_synthetic_data.py

# 2. Build config using ionworks_schema (no pybamm needed)
python 01_generate_config.py

# 3. Run config using ionworkspipeline (requires pybamm)
python 02_run_config.py
```

## What This Demonstrates

1. **ionworks_schema** - Lightweight config generation
   - Material library access
   - Parameter definitions with bounds
   - Objective and pipeline construction
   - JSON export for API submission
   - No PyBaMM dependency

2. **ionworkspipeline** - Execution (requires PyBaMM)
   - Parse JSON config into Pipeline objects
   - Run the fitting
   - Plot results
