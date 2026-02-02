# ionworksschema Demo

This demo shows how to use `ionworksschema` to build pipeline configurations
and run them with `ionworkspipeline`.

## Setup

```bash
# Install ionworksschema (from repo root)
pip install -e ./ionworksschema
```

## Usage

```bash
# 1. Generate synthetic data
python generate_synthetic_data.py

# 2. Build config using ionworksschema (no execution logic needed)
python 01_generate_config.py

# 3. Run config using ionworkspipeline (execution happens here)
python 02_run_config.py
```

## What This Demonstrates

1. **ionworksschema** - Pydantic schemas for config generation
   - Material library access
   - Parameter definitions with bounds
   - Objective and pipeline construction
   - JSON export for API submission

2. **ionworkspipeline** - Execution (cloud-side)
   - Parse JSON config into Pipeline objects
   - Run the fitting
   - Plot results
