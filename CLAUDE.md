# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with
code in this repository.

## Project Overview

ICONEval evaluates [ICON model](https://www.icon-model.org/) output with
[ESMValTool](https://docs.esmvaltool.org/) by automatically running ESMValTool
recipes. It is designed for DKRZ's Levante HPC system but can run anywhere
Slurm is available.

## Common Commands

```bash
# Run all tests
pytest

# Run a single test file
pytest tests/unit/test_session.py

# Run tests in parallel
pytest -n auto

# Run pre-commit hooks
pre-commit run --all

# Run ICONEval
iconeval path/to/ICON_output

# Show ICONEval help
iconeval -- --help
```

## Architecture

ICONEval works by filling ESMValTool recipe templates with ICON simulation metadata, then submitting jobs to run them via Slurm.

### Core Flow (main.py → _session.py → _job.py)

1. **`main.py`** - CLI entry point using `fire`. Validates dependencies (ESMValTool, Slurm), creates a `Session`, generates `Job` objects, and executes them.

2. **`_session.py`** - Manages an evaluation session. Discovers ICON simulation output from input directories, creates output directory structure (`output_iconeval/<name>_<timestamp>/`), and creates `Job` objects from recipe templates.

3. **`_job.py`** - Represents a single Slurm job. Generates the recipe YAML and ESMValTool config, then submits via `sbatch` or `srun`.

### Template System (`_templates.py`)

Templates use Jinja2-like `{{placeholder}}` syntax. Two template types:

- **Recipe templates** (`recipe_templates/*.yml`) - ESMValTool recipes with special markers:
  - `#TAGS` - Recipe categorization
  - `#ESMVALTOOL` - ESMValTool options
  - `#SRUN` - Slurm/srun options
  - `#DASK` - Dask cluster options

- **ESMValTool config template** (`esmvaltool_config_template.yml`) - Base config with `{{placeholder}}` for data source paths

### Simulation Discovery (`_simulation_info.py`)

Parses ICON output directory structure to extract:

- Experiment name (from directory name)
- File facets (variable type, frequency, grid) from filename patterns like `exp_atm_2d_ml_YYYYMMDD.nc`

### HTML Output (`output_handling/`)

- `_summarize.py` - Creates summary HTML from ESMValTool output
- `publish_html.py` - Publishes results to DKRZ Swift storage
- `_html_templates/` - HTML template rendering

## Key Files

- `iconeval/main.py:46` - Main `icon_evaluation` function
- `iconeval/_session.py:29` - `Session` class
- `iconeval/_job.py:18` - `Job` class
- `iconeval/_templates.py:131` - `RecipeTemplate` class
- `iconeval/_simulation_info.py:10` - `SimulationInfo` class
- `iconeval/esmvaltool_config_template.yml` - ESMValTool config base
- `iconeval/recipe_templates/` - Default recipe templates (28 recipes)

## Testing

- Tests use `pytest` with fixtures in `tests/conftest.py`.
- Some tests use pre-calculated expected output (`@pytest.mark.uses_expected_output`).
- To re-calculate expected output, run `python /home/b/b309141/ICONEval/tests/generate_expected_output.py`
  and follow further instruction from the output of that command.

## Configuration

- `pyproject.toml` - Project config, dependencies, pytest/ruff settings
- `.pre-commit-config.yaml` - Pre-commit hooks (ruff, mypy, yamllint, codespell)
- `environment.yml` - Conda environment for development

When updating dependencies, always update `pyproject.toml` and `environment.yml`
