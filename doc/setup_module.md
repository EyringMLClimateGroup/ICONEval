[Back to README](../README.md)

# Setup of ICONEval Module

This document describes how to setup a module for ICONEval on Levante, JSC, or
any other machine that uses the [Module
Environment](http://modules.sourceforge.net/).

1. Install [`mamba`](https://mamba.readthedocs.io/en/latest/installation.html)
   or
   [`conda`](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html)
   if this is not already available on your system. `mamba` is recommended.

2. Create a new `mamba`/`conda` environment at a location that is accessible to
   everyone who will use the module and [install ICONEval from
   source](install_from_source.md) and all its dependencies (e.g., ESMValTool)
   into it, for example:

   ```bash
   mamba env create -f iconeval/environment.yml -p $PREFIX
   mamba activate iconeval
   ```

   or

   ```bash
   conda env create -f iconeval/environment.yml -p $PREFIX
   conda activate iconeval
   ```

   Replace `$PREFIX` with your desired target location for the environment.

3. Setup the modulefile at your desired location.

   - On Levante, it could be called `$MODULEFILES/iconeval/1.0.0` and look like
     this:

     ```module
     #%Module1.0

     module-whatis "ICON model output evaluation with ESMValTool."
     module-version "1.0.0"

     proc ModulesHelp { } {
     puts stderr "For more information on this tool run"
     puts stderr ""
     puts stderr "iconeval -- --help"
     puts stderr ""
     puts stderr "or visit https://github.com/EyringMLClimateGroup/ICONEval"
     }

     conflict mambaforge
     conflict esmvaltool

     module load texlive

     set root $PREFIX

     prepend-path PATH "${root}/bin"
     prepend-path MANPATH "${root}/man"
     prepend-path MANPATH "${root}/share/man"
     prepend-path ACLOCAL_PATH "${root}/share/aclocal"
     prepend-path C_INCLUDE_PATH "${root}/include"
     prepend-path CPLUS_INCLUDE_PATH "${root}/include"
     prepend-path INCLUDE "${root}/include"
     prepend-path PKG_CONFIG_PATH "${root}/lib/pkgconfig"
     prepend-path PKG_CONFIG_PATH "${root}/share/pkgconfig"

     setenv PROJ_LIB "${root}/share/proj"
     setenv ESMFMKFILE "${root}/lib/esmf.mk"
     ```

   - On JSC, it could be called `$MODULEFILES/iconeval/1.0.0.lua` and look like
     this:

     ```lua
     help([==[
     For more information on this tool run

     iconeval -- --help

     or visit https://github.com/EyringMLClimateGroup/ICONEval
     ]==])

     whatis("ICON model output evaluation with ESMValTool.")

     conflict("mambaforge", "esmvaltool")

     local root = $PREFIX
     local root_env = pathJoin(root, "env")

     prepend_path("PATH", pathJoin(root, "bin"))
     prepend_path("PATH", pathJoin(root_env, "bin"))
     prepend_path("MANPATH", pathJoin(root_env, "man"))
     prepend_path("MANPATH", pathJoin(root_env, "share/man"))
     prepend_path("ACLOCAL_PATH", pathJoin(root_env, "share/aclocal"))
     prepend_path("C_INCLUDE_PATH", pathJoin(root_env, "include"))
     prepend_path("CPLUS_INCLUDE_PATH", pathJoin(root_env, "include"))
     prepend_path("INCLUDE", pathJoin(root_env, "include"))
     prepend_path("PKG_CONFIG_PATH", pathJoin(root_env, "lib/pkgconfig"))
     prepend_path("PKG_CONFIG_PATH", pathJoin(root_env, "share/pkgconfig"))
     ```

     This will use a [containerized installation](esmvaltool_container.md) of
     ESMValTool available at `$PREFIX/bin`.

   Make sure to replace `$PREFIX` with your actual environment directory.

4. Load the module:

   ```bash
   module use -a $MODULEFILES
   module load iconeval
   ```

   Make sure to replace `$MODULEFILES` with your actual modulefiles directory.

## Note

This documentation can also be used to create modules for any other `pip`- or
`mamba`/`conda`-installable software. When this module is loaded, all binaries
in the environment can be used. Thus, arbitrary modules can be set up by
installing new packages into the environment and creating corresponding
modulefiles.
