[Back to README](../README.md)

# Containerized Installation of ESMValTool

To avoid installing a development installation of ESMValTool in a conda/mamba
environment that creates thousands of files, a containerized installation can
be used. This can be done with [Apptainer](https://apptainer.org/) (formerly
Singularity), which is an alternative to [Docker](https://www.docker.com/)
better suited for HPC systems.

## Levante

On Levante, a container image is available at
`/work/bd1179/esmvaltool/bin/esmvaltool.sif`. It can be run via

```bash
singularity run -B /work:/work,/scratch:/scratch esmvaltool.sif run /path/to/recipe.yml
```

Make sure to `module load singularity` first.

## Build custom Container

To build a custom container image, you need root access. Note that you can
build the container image on another machine and then copy it to the machine of
your choice. Use the following instructions to build an ESMValTool container
image:

1. Create a [definition
   file](https://apptainer.org/docs/user/main/definition_files.html) called
   `esmvaltool.def` with the following contents:

   ```def
   Bootstrap: docker
   From: ghcr.io/prefix-dev/pixi:latest

   %labels
       Author manuel.schlund@dlr.de

   %post
       pixi info
       pixi global install git
       git --version
       git clone https://github.com/ESMValGroup/ESMValTool.git /ESMValTool
       cd /ESMValTool
       pixi install -e esmvalcore-dev --frozen
       pixi shell-hook -e esmvalcore-dev -s bash --no-completions >> /entrypoint.sh
       cat /entrypoint.sh

   %environment
       . /entrypoint.sh

   %runscript
       esmvaltool "$@"
   ```

1. Build the container image with

   ```bash
   sudo -E apptainer build esmvaltool.sif esmvaltool.def
   ```

   If you get `No space left on device` errors, try to use a different
   temporary directory by exporting the following environment variable before
   starting the build:

   ```bash
   export APPTAINER_TMPDIR=/path/to/better/tmp
   ```

This container can be run with

```bash
apptainer run -B src:dest esmvaltool.sif run /path/to/recipe.yml
```

The `-B` option allows you to bind an outside directory (`src`) to an inside
(i.e., within the container) directory (`dest`). This is useful to ensure that
the container has access to all necessary data.
