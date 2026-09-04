[Back to README](../README.md)

# FAQs

1. My ICON data is not found or the wrong data is found.

   The directories you specify as positional arguments to ICONEval will be used
   as the `exp` facets.
   [By default](https://docs.esmvaltool.org/projects/ESMValCore/en/latest/quickstart/find_data.html#icon),
   ESMValTool will search for files using the following patterns:

   - `{exp}_{output_stream}*.nc`
   - `outdata/{exp}_{output_stream}*.nc`
   - `output/{exp}_{output_stream}*.nc`

   If you want to use custom input file patterns for your ICON data, you can
   use the command line option `--path_templates`. For example,

   ```bash
   iconeval path/to/ICON_output --path_templates='["{exp}_*.nc", "my_output/{output_stream}_x*.nc"]'
   ```

   will search for files using the patterns:

   - `{exp}_*.nc`
   - `my_output/{output_stream}_x*.nc`

   `output_stream` can be defined in the recipe or as custom [extra
   facets](https://docs.esmvaltool.org/projects/ESMValCore/en/latest/quickstart/configure.html#extra-facets)
   passed to ICONEval via [custom ESMValTool configuration
   options](customization.md#custom-esmvaltool-configuration). If not given,
   ESMValTool will use [default
   values](https://github.com/ESMValGroup/ESMValCore/blob/main/esmvalcore/config/configurations/defaults/extra_facets_icon.yml)
   for this.

   For example, if your output consists of individual files for each variable
   (e.g., `my-icon-run_tas_atm_2d_ml_20200101.nc`), you need to adapt the
   `output_stream` to `output_stream: tas_atm_2d_ml`.

   This can be done by creating a file `my_custom_config_file.yml` in a new
   directory `/path/to/config/dir` with the contents

   ```yaml
   # Contents of /path/to/config/dir/my_custom_config_file.yml
   projects:
     ICON:
       extra_facets:
         ICON:  # alternatively, ICON-XPP
           '*':
             tas:  # variable name goes here
               output_stream: tas_atm_2d_ml
   ```

   and running ICONEval with

   ```bash
   iconeval path/to/ICON_output --esmvaltool_options='{"--config_dir": "/path/to/config/dir"}'
   ```

1. ESMValTool fails with `No input data available for years ... in files ...`
   even though the required years are present in the ICON output files.

   This happens if you explicitly specified a ``--timerange`` when running
   ICONEval and your ICON output contains multiple years per file.

   To fix this, run ICONEval with the option

   ```bash
   iconeval path/to/ICON_output --ignore_datetimes_in_filename=True
   ```

   More details can be found in the corresponding [ESMValCore
   issue](https://github.com/ESMValGroup/ESMValCore/issues/3208).

1. ESMValTool does not find my variable (e.g., `Unable to load CMOR table
   (project) 'ICON' for variable ...`).

   Without further changes, ESMValTool can only use variables defined in the
   "official" CMIP6 data request. You can search for variables
   [here](https://clipc-services.ceda.ac.uk/dreq/mipVars.html). After clicking
   on a variable of interest, you will find a list of MIP tables that can be
   used in the recipe as `mip` facet. For example, the variable `fgco2` is
   provided in the tables `Omon` and `Oyr`. Note that you can specify a custom
   frequency in the recipe or as command line argument `--frequency` to
   ICONEval.

   If you found a suitable variable but its name differs from the ICON name,
   you can specify `raw_name: name_of_the_var_in_icon` in the recipe or extra
   facets (see FAQ 1). In addition, you can specify `raw_units:
   units_of_the_var_in_icon` in the recipe or extra facets (see FAQ 1) if the
   units in the ICON file differ from the ones required by CMOR.  Note that in
   this case the units need to be convertible to the corresponding CMOR units.

   If you did not find a suitable variable, you can define a custom variable
   table. In this case, the `mip` facet in the recipe is basically ignored, but
   still needs to be specified for technical reasons (it is recommended to use
   a table with the correct frequency though, e.g., `mip: E1hr` for hourly
   data). The following steps are necessary to use custom variables:

   - Add a new variable table file to a directory of your choice (e.g.,
     `/your/table/directory`). This file needs to be a JSON file (`*.json`) and
     contain information about your variable like names, units, etc.; an
     example can be found
     [here](https://github.com/ESMValGroup/ESMValCore/blob/main/esmvalcore/cmor/tables/cmip6-custom/CMIP6_custom.json).
     Make sure to provide the `Header` and one `variable_entry` per custom
     variable.
   - Create a file `my_custom_config_file.yml` in a new directory
     `/path/to/config/dir` with the contents

     ```yaml
     # Contents of /path/to/config/dir/my_custom_config_file.yml
     projects:
       ICON:
         cmor_table:
           paths:
             - cmip6/Tables
             - cmip6-custom
             - /your/table/directory
     ```

   - Run ICONEval with

     ```bash
     iconeval path/to/ICON_output --esmvaltool_options='{"--config_dir": "/path/to/config/dir"}'
     ```

1. ESMValTool misses a vertical coordinate in the data (e.g.,
   `esmvalcore.cmor.check.CMORCheckError: There were errors in variable ...:
   alevel: does not exist`).

   Most likely, your input data contains files without vertical grid
   information (e.g., the `zg` or `pfull` variable). In these cases, the
   vertical grid information (i.e., the `zg` variable) is usually stored in a
   separate file. This file can be specified in ICONEval with the `--zg_file`
   command line argument.  In addition, a file containing the bounds of the
   vertical coordinate (i.e., the `zghalf` variable) can be specified with the
   command line argument `--zghalf_file`.  See
   [here](https://docs.esmvaltool.org/projects/ESMValCore/en/latest/quickstart/find_data.html#icon)
   for more details on this.

   If you need the corresponding air pressure information, you can use the
   following preprocessor to convert altitude (i.e., `zg`) to air pressure:

   ```yaml
   extract_pressure_levels_for_icon:
     extract_levels:
       levels: [100000, 10000, 1000]  # units: Pa
       scheme: linear
       coordinate: air_pressure
   ```

1. ESMValTool cannot find the horizontal grid file (e.g., `Cube does not
   contain the attribute 'grid_file_uri' necessary to download the ICON
   horizontal grid file`).

   You can specify a custom location to your ICON horizontal grid file with the
   command line argument `--horizontal_grid`. See
   [here](https://docs.esmvaltool.org/projects/ESMValCore/en/latest/quickstart/find_data.html#icon)
   for more details on this.

1. I get weird certificate errors when trying to publish the summary HTML
   (e.g., `HTTPSConnectionPool(host='swift.dkrz.de', port=443): Max retries
   exceeded with url: ... (Caused by SSLError(SSLCertVerificationError(1,
   '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: certificate
   signature failure (_ssl.c:1006)')))`).

   Try using a different Levante login node. E.g., if you are on `levante1`,
   try `levante2` via `ssh levante2`.

1. ESMValTool cannot find observational data from *Tier 3* (e.g., `- Missing
   data for Dataset: tas, Amon, OBS6, MERRA2, 5.12.4`).

   You are probably not a member of the ESMValTool project on DKRZ (*bd0854*).
   To join this, select project "854: Erdsystemmodellevaluierung (DLR-Institut
   für Physik der Atmosphäre)" [here](https://luv.dkrz.de/projects/ask/),
   describe the reason why you want to join the project (access to Tier 3 data)
   and submit the form. You should be given access very soon. Please do not use
   any resources (computation time and/or storage) of that project without
   consulting the project admins.

1. I get an `OSError: File name too long`.

   This happens when you try to evaluate lots of simulations without specifying
   an `--html_name`. Please specify a `--html_name` in these cases.

1. My jobs don't start with the error `FATAL: while extracting
   /work/bd1179/iconeval/0.0.5/esmvaltool/bin/esmvaltool: root filesystem
   extraction failed: failed to copy content in staging file: write
   /tmp/rootfs-3224830439/archive-104220727: no space left on device`.

   This happens when the temporary file system is full. Login to a different
   Levante login node and try again, this should fix it.

1. My Swift token expired.

   User authentication for publishing results on [DKRZ's Swift object
   storage](https://docs.dkrz.de/doc/datastorage/swift/python-swiftclient.html)
   works via a *Swift token* that needs to be renewed monthly. If the token
   expired, ICONEval will automatically prompt you for your DKRZ account and
   password information the next time you run it.

   If you prefer to renew the token without running ICONEval (e.g., because you
   run ICONEval non-interactively), you can use:

   ```bash
   publish_html --force_new_token=True /path/to/a/random/directory
   ```

1. I want to access the raw files published via `--publish_html=True`.

   Access them via DKRZ's [Swiftbrowser](https://swiftbrowser.dkrz.de/).

1. I want to use ICONEval within an `sbatch` script or an `salloc` session.

   If ICONEval is run as a standalone script, one
   [Slurm](https://slurm.schedmd.com/) job per recipe is launched. If ICONEval
   is run within an `sbatch` script or `salloc` session, one job step per
   recipe is created.

   For example, the following `sbatch` script can be used to submit a job on a
   compute node of [DKRZ's Levante](https://docs.dkrz.de/doc/levante/) in which
   8 recipes are run in parallel:

   ```bash
   #!/bin/bash -e
   #SBATCH --mem=0
   #SBATCH --nodes=1
   #SBATCH --partition=compute
   #SBATCH --time=03:00:00

   iconeval path/to/ICON_output --srun_options='{"--cpus-per-task": 16, "--mem-per-cpu": "1940M"}'
   ```

   This will request all memory (`--mem=0`) of a single compute node
   (`--nodes=1`, `--partition=compute`) with [128 CPUs and 256 GB of main
   memory](https://docs.dkrz.de/doc/levante/configuration.html). Since 1 recipe
   run = 1 task and 16 CPUs per task are requested, this results in 8 (= 128 /
   16) recipe runs in parallel.
