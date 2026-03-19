> [!IMPORTANT]
> Currently (March 2026), this repository contains an early version of
> ICONEval, which is targeted to the evaluation of
> [ICON](https://www.icon-model.org/) output on [DKRZ's
> Levante](https://docs.dkrz.de/doc/levante/).

---

[![LICENSE](https://img.shields.io/badge/License-Apache%202.0-blue)](https://www.apache.org/licenses/LICENSE-2.0.html)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18937450.svg)](https://doi.org/10.5281/zenodo.18937450)
[![SPEC 0 — Minimum Supported Dependencies](https://img.shields.io/badge/SPEC-0-green?labelColor=%23004811&color=%235CA038)](https://scientific-python.org/specs/spec-0000/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/EyringMLClimateGroup/ICONEval/main.svg)](https://results.pre-commit.ci/latest/github/EyringMLClimateGroup/ICONEval/main)
[![Run tests](https://github.com/EyringMLClimateGroup/ICONEval/actions/workflows/run_tests.yml/badge.svg)](https://github.com/EyringMLClimateGroup/ICONEval/actions/workflows/run_tests.yml)
<!-- Pytest Coverage Comment:Begin -->
<a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/README.md"><img alt="Coverage" src="https://img.shields.io/badge/Coverage-99%25-brightgreen.svg" /></a><details><summary>Coverage Report </summary><table><tr><th>File</th><th>Stmts</th><th>Miss</th><th>Cover</th><th>Missing</th></tr><tbody><tr><td><a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/__init__.py">__init__.py</a></td><td>16</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td><a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/_config.py">_config.py</a></td><td>11</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td><a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/_dependencies.py">_dependencies.py</a></td><td>16</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td><a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/_io_handler.py">_io_handler.py</a></td><td>178</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td><a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/_job.py">_job.py</a></td><td>98</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td><a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/_logging.py">_logging.py</a></td><td>12</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td><a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/_recipe.py">_recipe.py</a></td><td>10</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td><a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/_simulation_info.py">_simulation_info.py</a></td><td>42</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td><a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/_templates.py">_templates.py</a></td><td>220</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td><a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/_typing.py">_typing.py</a></td><td>6</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td><a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/main.py">main.py</a></td><td>154</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td colspan="5"><b>output_handling</b></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/__init__.py">__init__.py</a></td><td>0</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/_summarize.py">_summarize.py</a></td><td>193</td><td>1</td><td>99%</td><td><a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/_summarize.py#L304">304</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/publish_html.py">publish_html.py</a></td><td>115</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td><b>TOTAL</b></td><td><b>1071</b></td><td><b>1</b></td><td><b>99%</b></td><td>&nbsp;</td></tr></tbody></table></details>
<!-- Pytest Coverage Comment:End -->

---

# ICONEval

ICON model output evaluation with ESMValTool.

## Table of Contents

1. [Quick Start](#quick-start)
1. [Prerequisites](#prerequisites)
1. [Installation](#installation)
1. [Customization](#customization)
1. [Common ICON Output Format](#common-icon-output-format)
1. [FAQs](#faqs)

## Quick Start

ICONEval facilitates the evaluation of [ICON
model](https://www.icon-model.org/) output with [ESMValTool](doc/esmvaltool.md)
by automatically running a set of predefined ESMValTool recipes. Its only
necessary input is a valid path to ICON model output:

```bash
iconeval path/to/ICON_output
```

This path should point to the directory whose name is identical to the
experiment name of the ICON simulation you want to evaluate, e.g.,
`/root/to/my_amip_run` for the experiment `my_amip_run`. In this case, for
example, the simulation output files should be named
`my_amip_run_atm_2d_ml_<date>.nc` or `my_amip_run_lnd_mon_<date>.nc`. Multiple
simulations can be evaluated simultaneously by specifying multiple directories:

```bash
iconeval path/to/ICON_output path/to/other/ICON_output
```

ICONEval reads a set of file templates (ESMValTool recipes and ESMValTool
configuration) and fills these with the information from the ICON simulation
that will be evaluated. If no further options are specified, a set of default
recipes with default settings are run. If ICONEval is run as a standalone
script, one [Slurm](https://slurm.schedmd.com/) job per recipe is launched. If
ICONEval is run within an `sbatch` script or `salloc` session, one job step per
recipe is created. The following `sbatch` script can be used to submit a job on
a compute node of [DKRZ's Levante](https://docs.dkrz.de/doc/levante/) in which
8 recipes are run in parallel (see
[here](doc/customization.md#slurm-options-for-jobjob-step-submission) for
details on this):

```bash
#!/bin/bash -e
#SBATCH --mem=0
#SBATCH --nodes=1
#SBATCH --partition=compute
#SBATCH --time=03:00:00

iconeval path/to/ICON_output --srun_options='{"--cpus-per-task": 16, "--mem-per-cpu": "1940M"}'
```

ICONEval is highly customizable. For example, the desired time range and
frequency of the input data, as well as a flag to publish a summary HTML on a
**public** website can be passed with

```bash
iconeval path/to/ICON_output --timerange='20070101/20080101' --frequency=mon --publish_html=True
```

Publishing results via the command line option `--publish_html=True` uses the
[Swift object storage of
DKRZ](https://docs.dkrz.de/doc/datastorage/swift/python-swiftclient.html) and
requires a DKRZ account. User authentication works via a *Swift token* that
needs to be renewed monthly. If the token needs to be renewed, the user is
prompted for their DKRZ account and password information when running ICONEval.
The token can also be regenerated manually, see [FAQs](doc/faqs.md) for
details. The raw files (figures and data) from published results can be
accessed via DKRZ's [Swiftbrowser](https://swiftbrowser.dkrz.de/).

To only run a subset of available recipes, you can specify `--tags` when
running ICONEval:

```bash
iconeval path/to/ICON_output --tags=timeseries,maps
```

An overview of all tags available in the default recipe templates is given
[here](doc/tags.md).

For more information on this and a list of all options, run

```bash
iconeval -- --help
```

or have a look at the section on [Customization](#customization).

Installing ICONEval also provides the command line tool `publish_html`, which
can be used to publish a summary HTML on a public website for arbitrary
ESMValTool output. For more information, run

```bash
publish_html -- --help
```

## Example Results

- [Fully coupled historical ICON-XPP
  simulation](https://swift.dkrz.de/v1/dkrz_4eefb34f-8803-415a-bd70-9c455db9a403/iconeval/iconeval_example/index.html)

## Prerequisites

ICONEval needs to run on a machine where the [Slurm Workload
Manager](https://slurm.schedmd.com/) is available for the submission of jobs.

## Installation

On DKRZ's Levante, a pre-installed version of ICONEval is available via a
module. Thus, there is no need to install it yourself as a user on this
machine.

However, on other machines, or if you would like to develop new features for
ICONEval on Levante, an installation from source (*development installation*)
is necessary.

### Levante

To load the ICONEval module on Levante, use

```bash
module use -a /work/bd1179/modulefiles
module load iconeval
```

Add these lines to your shell configuration file if you use ICONEval regularly.
[This file](doc/setup_module.md) describes how the ICONEval module is set up.

### Installation from Source (Development Installation)

Installation from source is described [here](doc/install_from_source.md).

## Customization

ICONEval is highly customizable. Detailed information on this can be found
[here](doc/customization.md).

## Common ICON Output Format

To ensure that ICONEval works smoothly, the ICON simulation output should
follow [these criteria](doc/icon_output_format.md) as closely as possible.

## FAQs

A set of frequently asked questions can be found [here](doc/faqs.md).
