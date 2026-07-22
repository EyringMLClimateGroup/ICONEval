[Back to README](../README.md)

# Setup of ICONEval Module

This document describes how to setup a module for ICONEval on Levante, JSC, or
any other machine that uses the [Module
Environment](http://modules.sourceforge.net/).

1. Install ICONEval [from source](install_from_source.md) at a location that is
   accessible to everyone who will use the module (e.g., `/path/to/ICONEval`).

1. Setup the modulefile at your desired location.

   - On Levante, it could be called `/path/to/modulefiles/iconeval/1.0.0` and
     look like this:

     ```module
     #%Module1.0

     module-whatis "ICON model output evaluation with ESMValTool."
     module-version "development"


     proc ModulesHelp { } {
         puts stderr "For more information on this tool run"
         puts stderr ""
         puts stderr "iconeval -- --help"
         puts stderr ""
         puts stderr "or visit https://github.com/EyringMLClimateGroup/ICONEval"
     }

     conflict mambaforge
     conflict esmvaltool
     conflict py-python-swiftclient

     set root "/path/to/ICONEval/.pixi/envs/esmvaltool-dev"

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

   - On JSC, it could be called `/path/to/modulefiles/iconeval/1.0.0.lua` and
     look like this:

     ```lua
     help([==[
     For more information on this tool run

     iconeval -- --help

     or visit https://github.com/EyringMLClimateGroup/ICONEval
     ]==])

     whatis("ICON model output evaluation with ESMValTool.")

     conflict("mambaforge", "esmvaltool")

     local container_root = "/path/to/esmvaltool/container"
     local root = "/path/to/ICONEval/.pixi/envs/esmvaltool-dev"

     prepend_path("PATH", pathJoin(container_root, "bin"))
     prepend_path("PATH", pathJoin(root, "bin"))
     prepend_path("MANPATH", pathJoin(root, "man"))
     prepend_path("MANPATH", pathJoin(root, "share/man"))
     prepend_path("ACLOCAL_PATH", pathJoin(root, "share/aclocal"))
     prepend_path("C_INCLUDE_PATH", pathJoin(root, "include"))
     prepend_path("CPLUS_INCLUDE_PATH", pathJoin(root, "include"))
     prepend_path("INCLUDE", pathJoin(root, "include"))
     prepend_path("PKG_CONFIG_PATH", pathJoin(root, "lib/pkgconfig"))
     prepend_path("PKG_CONFIG_PATH", pathJoin(root, "share/pkgconfig"))
     ```

     This will use a [containerized installation](esmvaltool_container.md) of
     ESMValTool available at `/path/to/esmvaltool/container/bin`.

1. Load the module:

   ```bash
   module use -a /path/to/modulefiles
   module load iconeval
   ```
