[Back to README](../README.md)

# Installation from Source (Development Installation)

1. Install [Pixi](https://pixi.prefix.dev/latest/installation/) if this is not
   already available on your system.

1. Clone the ICONEval repository:

   ```bash
   git clone https://github.com/EyringMLClimateGroup/ICONEval.git
   ```

   or

   ```bash
   git clone git@github.com:EyringMLClimateGroup/ICONEval.git
   ```

   if you prefer to connect to the repository over SSH.

1. Install the `esmvaltool-dev` Pixi environment (this will use development
   versions of ESMValCore and ESMValTool; recommended). Alternatively, omit the
   `-e` flag to use the stable ESMValCore and ESMValTool versions.

   ```bash
   cd ICONEval
   pixi install -e esmaltool-dev
   ```

Now you can use

```bash
pixi shell -e esmaltool-dev
```

to launch a shell in your Pixi environment (this is similar to activating a Conda environment) or

```bash
pixi run -e esmaltool-dev ...
```

to run commands in your Pixi environment, e.g.,

```bash
pixi run -e esmaltool-dev iconeval path/to/ICON_output --publish_html=True
```
