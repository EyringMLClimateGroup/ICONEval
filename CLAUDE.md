# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ICONEval facilitates evaluation of [ICON model](https://www.icon-model.org/) output with [ESMValTool](https://docs.esmvaltool.org/) by automatically running predefined ESMValTool recipes on ICON simulation data. It is designed for DKRZ's Levante HPC system.

## Common Commands

```bash
# Run evaluation on ICON output
iconeval path/to/ICON_output

# Run with specific options
iconeval path/to/ICON_output --timerange='20070101/20080101' --frequency=mon --publish_html=True

# Filter recipes by tags
iconeval path/to/ICON_output --tags='["atmosphere", "!subdaily"]'

# Run a single test
pytest tests/unit/test__io_handler.py::test_function_name -v

# Run tests in parallel
pytest -n auto

# Run with coverage
pytest --cov=iconeval --cov-report=term-missing
```

## Code Architecture

### Entry Point
- `iconeval/main.py`: CLI entry point using `fire` library. The `icon_evaluation()` function is the main logic.

### Core Modules
- `_io_handler.py`: Manages input/output directories, creates jobs from recipe templates
- `_job.py`: Represents a single ESMValTool recipe run as a Slurm job via `srun`
- `_templates.py`: Handles YAML recipe templates and ESMValTool config templates with placeholder substitution
- `_simulation_info.py`: Extracts metadata (experiment name, grid info, owner) from ICON output directories
- `_config.py`, `_recipe.py`: Dataclasses representing ESMValTool configuration and recipes

### Output Handling
- `output_handling/_summarize.py`: Creates summary HTML from ESMValTool output
- `output_handling/publish_html.py`: Publishes results to DKRZ Swift storage

### Template System
Recipe templates are YAML files in the package's `recipe_templates/` directory. They use special comment markers:
- `#TAGS` - Recipe categorization
- `#ESMVALTOOL --option=value` - ESMValTool options
- `#SRUN --option=value` - Slurm srun options
- `#DASK --option=value` - Dask cluster options

Placeholders like `{{dataset_list}}`, `{{timerange}}`, `{{alias_plot_kwargs}}` are replaced at runtime.

### Testing
- `tests/unit/` - Unit tests
- `tests/integration/` - Integration tests
- `tests/conftest.py` - Shared pytest fixtures
- Some tests use pre-calculated expected output (marked with `@pytest.mark.uses_expected_output`)
- Use `python /home/b/b309141/ICONEval/tests/generate_expected_output.py` to create expected output and look at the output of this script on how to copy the created output to the `expected_output` directory.

## Development Notes

- Python 3.12+ required
- Uses `ruff` for linting (configured in pyproject.toml)
- Uses `pre-commit` (see `.pre-commit-config.yaml`)
- 100% test coverage is maintained
- Templates are loaded via `importlib.resources.files("iconeval")`
