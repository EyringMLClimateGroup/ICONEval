[Back to README](../README.md)

# FAQs

1. My ICON data is not found or the wrong data is found.

   The directory you specify as main argument to ICONEval will be used as the
   `exp` facet.
   [By default](https://docs.esmvaltool.org/projects/ESMValCore/en/latest/quickstart/find_data.html#icon),
   ESMValTool will search for files using the following patterns:

   - `{exp}/{exp}_{var_type}*.nc`
   - `{exp}/outdata/{exp}_{var_type}*.nc`
   - `{exp}/output/{exp}_{var_type}*.nc`

   `var_type` can be defined in the recipe or as custom [extra
   facets](https://docs.esmvaltool.org/projects/ESMValCore/en/latest/quickstart/configure.html#extra-facets)
   passed to ICONEval via [custom ESMValTool configuration
   options](customization.md#custom-esmvaltool-configuration). If not given,
   ESMValTool will use [default
   values](https://github.com/ESMValGroup/ESMValCore/blob/main/esmvalcore/config/configurations/defaults/extra_facets_icon.yml)
   for this.

   For example, if your output consists of individual files for each variable
   (e.g., `my-icon-run_tas_atm_2d_ml_20200101.nc`), you need to adapt the
   `var_type` to `var_type: tas_atm_2d_ml`.

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
               var_type: tas_atm_2d_ml
   ```

   and running ICONEval with

   ```bash
   iconeval path/to/ICON_output --esmvaltool_options='{"--config_dir": "/path/to/config/dir"}'
   ```

   If you want to use a custom input file pattern for your ICON data, you can
   use the following configuration options:

   ```yaml
   # Contents of /path/to/config/dir/my_custom_config_file.yml
   projects:
     ICON:
       data:
         my_custom_paths:
           type: esmvalcore.io.local.LocalDataSource
           rootpath: path/to/ICON_output  # path you use as argument for ICONEval
           dirname_template: "my/icon_output"
           filename_template: "{exp}_{var_type}_custom_info_*.nc"
   ```

   Again, run ICONEval with

   ```bash
   iconeval path/to/ICON_output --esmvaltool_options='{"--config_dir": "/path/to/config/dir"}'
   ```

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

1. ESMValTool cannot find observational data from *Tier 3* (e.g., `- Missing data for Dataset: tas, Amon, OBS6, MERRA2, 5.12.4`).

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

1. My Swift token expired and I want to renew it without running ICONEval.

   On DKRZ's Levante, run

   ```bash
   module load py-python-swiftclient
   swift-token new
   ```

   Alternatively, run

   ```bash
   publish_html --force_new_token=True /path/to/a/random/directory
   ```
