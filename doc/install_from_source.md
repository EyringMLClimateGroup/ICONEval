[Back to README](../README.md)

# Installation from Source (Development Installation)

It is recommended to also install ESMValTool and ESMValCore from source because
the development version of ICONEval is always developed against the development
version of ESMValTool and ESMValCore.

> [!TIP]
> If you already have a development installation of ESMValTool/ESMValCore in an
> existing Mamba environment, just skip steps 1-4 below and replace the
> environment name below with your environment name.

1. Install
   [Mamba](https://mamba.readthedocs.io/en/latest/installation/mamba-installation.html)
   if this is not already available on your system.

2. Clone the ESMValTool and ESMValCore repositories:

   ```bash
   git clone https://github.com/ESMValGroup/ESMValTool.git
   git clone https://github.com/ESMValGroup/ESMValCore.git
   ```

   or

   ```bash
   git clone git@github.com:ESMValGroup/ESMValTool.git
   git clone git@github.com:ESMValGroup/ESMValCore.git
   ```

   if you prefer to connect to the repository over SSH.

3. Create a Mamba environment called `iconeval` (this name is arbitrary):

   ```bash
   mamba env create -n iconeval -f ESMValTool/environment.yml
   mamba env update -n iconeval -f ESMValCore/environment.yml
   ```

4. Install ESMValTool and ESMValCore from source:

   ```bash
   mamba activate iconeval
   cd ESMValTool
   pip install --no-deps --editable '.[develop]'
   cd ../ESMValCore
   pip install --no-deps --editable '.[develop]'
   cd ..
   ```

5. Clone the ICONEval repository:

   ```bash
   git clone https://github.com/EyringMLClimateGroup/ICONEval.git
   ```

   or

   ```bash
   git clone git@github.com:EyringMLClimateGroup/ICONEval.git
   ```

   if you prefer to connect to the repository over SSH.

6. Update the existing Mamba environment with the ICONEval dependencies:

   ```bash
   mamba env update -n iconeval -f ICONEval/environment.yml
   ```

7. Install ICONEval from source:

   ```bash
   mamba activate iconeval
   cd ICONEval
   pip install --no-deps --editable '.[develop]'
   ```
