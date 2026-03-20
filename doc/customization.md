[Back to README](../README.md)

# Customization

To evaluate ICON simulation output, ICONEval reads [ESMValTool recipe
templates](#esmvaltool-recipes). These templates are then filled with
information from the ICON simulation that will be evaluated. This is done via
placeholders (`{{placeholder}}`) in the files.

Individual ESMValTool runs can be further customized with additional
[ESMValTool configuration options](#esmvaltool-configuration), [Slurm
options](#slurm-options-for-jobjob-step-submission) and/or [Dask
options](#dask-options). Finally, [additional command line
options](#additional-command-line-options) allow an even further customization
of ICONEval.

## ESMValTool Recipes

By default, recipe templates are read from the [recipe template
directory](https://github.com/EyringMLClimateGroup/ICONEval/tree/main/iconeval/recipe_templates)
in the installation directory of this tool. To only run a custom recipe, use

```bash
iconeval path/to/ICON_output --recipe_templates=/path/to/recipe_1.yml
```

Make sure that all recipe names start with `recipe_`.

Unix-style wildcards are supported:

```bash
iconeval path/to/ICON_output --recipe_templates=/path/to/recipe_*.yml
```

To run multiple recipe (patterns), use the syntax:

```bash
iconeval path/to/ICON_output --recipe_templates='["/path/to/recipe_1_*.yml", "/path/to/recipe_2.yml"]'
```

To run custom recipes in addition to the default recipes, use

```bash
iconeval path/to/ICON_output --recipe_templates='["/path/to/recipe_1_*.yml", "/path/to/recipe_2.yml"]' --always_use_default_recipe_templates=True
```

The default recipes are designed to run effectively on 1/8 of a compute on
DKRZ's Levante (16 cores, 32 GB of RAM).

The following placeholders are required in the recipe templates:

- `{{dataset_list}}`: Filled with the ICON dataset(s). By default, this uses
  the following facets:

  ```yaml
  datasets:
    - {project: ICON, dataset: ICON-XPP, exp: '{{exp}}'}
  ```

  if the ICON output looks like ICON-XPP output (i.e., if a namelist file
  `NAMELIST_ICON_output_atm` exists in the output directory and it does not
  contain the string `ECHAM_`), and

  ```yaml
  datasets:
    - {project: ICON, dataset: ICON, exp: '{{exp}}'}
  ```

  otherwise. Here, `{{exp}}` is the ICON experiment name determined from the
  input directory/directories. The facets of all datasets can be
  expanded/overwritten by additional command line arguments given to ICONEval,
  e.g., `--dataset=ICON-XPP`, `--timerange=20000101/20100101`
  `--frequency=day`, `--horizontal_grid=/path/to/grid_file.nc`.

The following placeholders are optional:

- `{{alias_plot_kwargs}}`: Filled with aliases of the ICON dataset for each
  experiment. Must be a dictionary key in the YAML file. If `color` is missing in
  the subsequent options, automatically add `C0`, `C1`, etc. Example:

  ```yaml
  "{{alias_plot_kwargs}}":
    linewidth: 1.5
  ```

  is expanded in such a way that it includes the aliases, i.e.,

  ```yaml
  ICON_exp1:
    linewidth: 1.5
    color: C0
  ICON_exp2:
    linewidth: 1.5
    color: C1
  ```

  for experiments `exp1` and `exp2`.
- `{{dataset}}`: Filled with the dataset name specified by the `--dataset`
  command line argument. By default, uses `ICON`.
- `{{project}}`: Filled with the project specified by the `--project` command
  line argument. By default, uses `ICON`.
- `{{timerange}}`: Filled with the time range specified by the `--timerange`
  command line argument. By default, the entire available time range is
  considered (i.e., `--timerange='*'`). Please specify the time range with at
  least 8 digits (`YYYYMMDD`).

More information on ESMValTool recipes in general are given
[here](https://docs.esmvaltool.org/projects/esmvalcore/en/latest/recipe/index.html).
A list of all currently available recipes is given
[here](https://docs.esmvaltool.org/en/latest/recipes/index.html).

Furthermore, the following magic comments can be specified in the recipe
templates to fine-tune individual recipe runs:

- `#ESMVALTOOL --key=val`: ESMValTool configuration options.
- `#SRUN --key=val`: Options for the `srun` command that is used to submit
  Slurm jobs/job steps.
- `#DASK --key=val`: Options for the Dask Distributed scheduler used by
  ESMValTool.

More information on these settings is given in the following three sections.

## ESMValTool Configuration

### Default ESMValTool Configuration

By default, an ESMValTool configuration template is read from the [installation
directory of this
tool](https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/esmvaltool_config_template.yml)
and filled with information from the current ICONEval run.

The configuration options `dask`, `output_dir`, and `rootpath` must not be
overwritten in the [custom ESMValTool
configuration](#custom-esmvaltool-configuration)!

### Custom ESMValTool Configuration

Additional ESMValTool configuration options can also be specified via the
command line, e.g.,

```bash
iconeval path/to/ICON_output --esmvaltool_options='{"--max_parallel_tasks": 1}'
```

These options are used for all recipes.

More complicated configuration options can be given in [YAML
files](https://docs.esmvaltool.org/projects/ESMValCore/en/latest/quickstart/configure.html#yaml-files)
located in a dedicated configuration directory (e.g., `/path/to/config/dir`),
which can then be specified via

```bash
iconeval path/to/ICON_output --esmvaltool_options='{"--config_dir": "/path/to/config/dir"}'
```

For example, this is useful to specify custom [extra
facets](https://docs.esmvaltool.org/projects/ESMValCore/en/latest/quickstart/configure.html#extra-facets).

Moreover, additional recipe-specific ESMValTool configuration options can be
specified in the recipe templates, e.g.,

```yaml
#ESMVALTOOL --max_parallel_tasks=1
```

This is particularly useful if a specific recipe needs special requirements
like a reduced number of parallel processes.

If the optional ICONEval command line argument
`--ignore_recipe_esmvaltool_options=True` is used, these recipe-specific
ESMValTool configuration options are ignored for all recipes.

Recipe-specific options take priority over options specified via command line.

More information and all possible ESMValTool configuration options are given
[here](https://docs.esmvaltool.org/projects/ESMValCore/en/latest/quickstart/configure.html#top-level-configuration-options).

## Slurm options for job/job step submission

ICONEval uses [`srun`](https://slurm.schedmd.com/srun.html) to submit jobs or
job steps depending on how ICONEval is started:

1. If ICONEval is run within an
   [`sbatch`](https://slurm.schedmd.com/sbatch.html) script or
   [`salloc`](https://slurm.schedmd.com/salloc.html), one job step per recipe
   is submitted. In this case, the only default option for `srun` is
   `--ntasks=1` (to ensure that each recipe is only run once). All other
   options are inherited from the `sbatch` script/`salloc` session.

1. If ICONEval is run as a standalone script, one job per recipe is submitted.
   In this case, the default `srun` options for each job are:

   ```bash
   --cpus-per-task=16
   --mem-per-cpu=1940M  # maximum memory per CPU
   --nodes=1
   --ntasks=1
   --partition=interactive
   --time=03:00:00
   ```

The account that is charged for the job can be specified by the `--account`
command line option given to ICONEval. By default, this account is either
inherited from `sbatch`/`salloc` (if ICONEval is run within an `sbatch`
script/`salloc` session), or set to `'bd1179'` (if ICONEval is run as a
standalone script).

Additional `srun` options can also be specified via the command line, e.g.,

```bash
iconeval path/to/ICON_output --srun_options='{"--mem": "16G"}'
```

These options are used for all recipes.

Furthermore, additional recipe-specific `srun` options can be specified in the
recipe templates, e.g.,

```yaml
#SRUN --cpus-per-task=128
#SRUN --mem-per-cpu=1940M
#SRUN --nodes=1
#SRUN --ntasks=1
#SRUN --partition=compute
#SRUN --time=03:00:00
```

The above will reserve an entire compute node for 3 hours, which is
particularly useful for heavy recipes. Make sure to adapt the [Dask
options](#dask-options) accordingly.

If the optional ICONEval command line argument
`--ignore_recipe_srun_options=True` is used, these recipe-specific `srun`
options are ignored for all recipes. This might be useful if ICONEval is run
within an `sbatch` script/`salloc` session to ensure that the recipe-specific
settings are not conflicting with the `sbatch`/`salloc` options.

Recipe-specific options take priority over options specified via command line.

An overview of all possible `srun` options is given
[here](https://slurm.schedmd.com/srun.html).

## Dask options

ESMValTool uses [Dask](https://docs.dask.org/en/stable/) for parallel and
distributed computing. By default, the following configuration is used:

```yaml
memory_limit: 3880MB  # 2 x memory per CPU as defined by srun
n_workers: 8
threads_per_worker: 2
type: distributed.LocalCluster
```

This will use a
[`LocalCluster`](https://distributed.dask.org/en/stable/api.html#distributed.LocalCluster).

Additional Dask options can also be specified via the command line, e.g.,

```bash
iconeval path/to/ICON_output --dask_options='{"--memory_limit": "8GB"}'
```

These options are used for all recipes.

In addition, recipe-specific Dask options can be specified in the recipe
templates, e.g.,

```yaml
#DASK --memory_limit=8GB
#DASK --n_workers=32
```

Note that these settings need to be synchronized with the Slurm settings (see
section above). For example, the custom Dask settings given here require a
total memory of 32 workers times 8 GB = 256 GB. When using a
[`SLURMCluster`](https://jobqueue.dask.org/en/latest/generated/dask_jobqueue.SLURMCluster.html)
with `type: dask_jobqueue.SLURMCluster`, the account specified by the command
line argument `--account` given to ICONEval is charged. If a different `type`
than `distributed.LocalCluster` is used, the default options given above are
ignored.

If the optional ICONEval command line argument
`--ignore_recipe_dask_options=True` is used, these recipe-specific Dask options
are ignored for all recipes.

Recipe-specific options take priority over options specified via command line.

An overview of ESMValTool's Dask configuration is given
[here](https://docs.esmvaltool.org/projects/ESMValCore/en/latest/quickstart/configure.html#dask-configuration).
Options given to ICONEval are interpreted as `cluster` keyword arguments.

To use the default (thread-based) Dask scheduler instead of a distributed
scheduler, run ICONEval with the command line argument `--dask=False`.

## Tags

All default recipe templates are marked with tags. An overview of all available
tags is given [here](tags.md). To only run a subset of recipes associated with certain tags, use

```bash
iconeval path/to/ICON_output --tags='["atmosphere", "!subdaily"]'
```

This will run all recipes marked with `atmosphere` excluding those marked as
`subdaily` (the syntax `!tag` can be used to exclude recipes marked with
`tag`).

To run all recipes except for ones marked as `subdaily`, use

```bash
iconeval path/to/ICON_output --tags='!subdaily'
```

Make sure to properly escape the string via `'`.

Custom [recipe templates](#esmvaltool-recipes) can be marked with arbitrary
tags using the syntax

```yaml
#TAGS my-new-tag-1
#TAGS my-new-tag-2
```

## Additional Command Line Options

- `--publish_html`: Enable/Disable publishing of an ESMValTool summary HTML on
  a **public** website using DKRZ's
  [Python-swiftclient](https://docs.dkrz.de/doc/datastorage/swift/python-swiftclient.html)
  (default: `False`). To delete existing websites, login to the [swift
  web client](https://swiftbrowser.dkrz.de/) and delete the corresponding
  directories in the *iconeval* container.
- `--html_name`: Name that is used for the URL of the ESMValTool summary HTML;
  if `None`, use the name of the output directory (default: `None`). Use this
  to get a consistent URL (this will potentially overwrite existing data!).
  Ignored if `--publish_html=False`.
- `--log_level`: Log level for ICONEval (default: `info`).
- `--output_dir`: Output directory for ICONEval (default: `./output_iconeval`).
- `--background`: Terminate ICONEval after submitting all jobs/job steps
  (default: `False`). Summary HTMLs cannot be published/written in this mode.
- `--esmvaltool_executable`: Path to ESMValTool executable (default:
  `esmvaltool`).
- `--srun_executable`: Path to `srun` executable (default: `srun`).
- Additional options are interpreted as extra facets for the ICON data. For
  example, can include `--timerange` (desired time range, see
  [here](https://docs.esmvaltool.org/projects/ESMValCore/en/latest/recipe/overview.html#time-ranges)
  for examples, but make sure to use at least 8 digits, i.e., the format
  `YYYYMMDD`), `--frequency` (output frequency of the ICON data),
  `--horizontal_grid` (path to the ICON horizontal grid file), `--zg_file`
  (path to the ICON file that contains the vertical coordinate `zg`),
  `--zghalf_file` (path to the ICON file that contains the vertical coordinate
  `zghalf`), etc.  All available extra facets for ICON are given
  [here](https://docs.esmvaltool.org/projects/ESMValCore/en/latest/quickstart/find_data.html#icon).
