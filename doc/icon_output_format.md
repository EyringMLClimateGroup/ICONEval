[Back to README](../README.md)

# Common ICON Output Format

To ensure that ICONEval works smoothly, the ICON simulation output should
follow the subsequent criteria as closely as possible.

## 2D Variables

2D variables (*time*, *latitude*, *longitude*) that should be available in the
`atm_2d_ml` files:

| Description                                         | CMIP variable     | ICON-XPP variable        | ICON-A variable   | Comments                           |
| --------------------------------------------------- | ----------------- | ------------------------ | ----------------- | ---------------------------------- |
| Ice Water Path                                      | clivi (kg/m2)     | tqi_dia (kg/m2)          | clivi (kg/m2)     | -                                  |
| Total Cloud Cover                                   | clt (%)           | clct (%)                 | clt (%)           | -                                  |
| Evaporation Including Sublimation and Transpiration | evspsbl (kg/m2/s) | qhfl_s (kg/m2/s)         | evspsbl (kg/m2/s) | -                                  |
| Surface Upward Latent Heat Flux                     | hfls (W/m2)       | lhfl_s (W/m2)            | hfls (W/m2)       | ICON-A and ICON-XPP: opposite sign |
| Surface Upward Sensible Heat Flux                   | hfss (W/m2)       | shfl_s (W/m2)            | hfss (W/m2)       | ICON-A and ICON-XPP: opposite sign |
| Liquid Water Path                                   | lwp (kg/m2)       | tqc_dia (kg/m2)          | cllvi (kg/m2)     | -                                  |
| Ocean Mixed Layer Thickness Defined by Sigma T      | mlotst (m)        | mld (m)                  | -                 | Not yet supported for ICON-A       |
| Precipitation                                       | pr (kg/m2/s)      | tot_prec_rate  (kg/m2/s) | pr (kg/m2/s)      | -                                  |
| Water Vapor Path                                    | prw (kg/m2)       | tqv_dia (kg/m2)          | prw (kg/m2)       | -                                  |
| Surface Air Pressure                                | ps (Pa)           | pres_sfc (Pa)            | ps (Pa)           | -                                  |
| Sea Level Pressure                                  | psl (Pa)          | pres_msl (Pa)            | psl (Pa)          | -                                  |
| TOA Upward Longwave Radiation Flux                  | rlut (W/m2)       | thb_t (W/m2)             | rlut (W/m2)       | ICON-XPP: opposite sign            |
| TOA Upward Clear-Sky Longwave Radiation Flux        | rlutcs (W/m2)     | lwflx_up_clr (W/m2)      | rlutcs (W/m2)     | ICON-XPP: level 0 of lwflx_up_clr  |
| TOA Downward Shortwave Radiation Flux               | rsdt (W/m2)       | sod_t (W/m2)             | rsdt (W/m2)       | -                                  |
| TOA Upward Shortwave Radiation Flux                 | rsut (W/m2)       | sou_t (W/m2)             | rsut (W/m2)       | -                                  |
| TOA Upward Clear-Sky Shortwave Radiation Flux       | rsutcs (W/m2)     | swflx_up_clr (W/m2)      | rsutcs (W/m2)     | ICON-XPP: level 0 of swflx_up_clr  |
| Sea-Ice Area Percentage                             | siconc (%)        | conc (1)                 | sic (1)           | -                                  |
| Near-Surface (2m) Air Temperature                   | tas (K)           | t_2m (K)                 | tas (K)           | -                                  |
| Surface Downward Eastward Wind Stress               | tauu (Pa)         | umfl_s (N/m2)            | tauu (N/m2)       | -                                  |
| Surface Downward Northward Wind Stress              | tauv (Pa)         | vmfl_s (N/m2)            | tauv (N/m2)       | -                                  |
| Sea Surface Temperature                             | tos (degC)        | t_seasfc (K)             | -                 | Not yet supported for ICON-A       |
| Surface Temperature                                 | ts (K)            | t_s (K)                  | ts (K)            | -                                  |

## 3D Variables

3D variables (*time*, *height*/*depth*, *latitude*, *longitude*) that should be
available in the `atm_3d_ml` files:

| Description                      | CMIP variable | ICON-XPP variable  | ICON-A variable | Comments                                     |
| -------------------------------- | ------------- | ------------------ | --------------- | -------------------------------------------- |
| Cloud Cover                      | cl (%)        | clc (%)            | cl (%)          | -                                            |
| Cloud Ice Mass Fraction          | cli (kg/kg)   | tot_qi_dia (kg/kg) | cli (kg/kg)     | -                                            |
| Cloud Liquid Water Mass Fraction | clw (kg/kg)   | tot_qc_dia (kg/kg) | clw (kg/kg)     | -                                            |
| Specific Humidity                | hus (1)       | qv (kg/kg)         | hus (1)         | -                                            |
| Pressure at Model Full-Levels    | pfull (Pa)    | pres (Pa)          | pfull (Pa)      | -                                            |
| Pressure on Model Half-Levels    | phalf (Pa)    | -                  | phalf (Pa)      | -                                            |
| Sea Water Salinity               | so (0.001)    | so (0.001)         | -               | Not yet supported for ICON-A                 |
| Air Temperature                  | ta (K)        | temp (K)           | ta (K)          | -                                            |
| Eastward Wind                    | ua (m/s)      | u (m/s)            | ua (m/s)        | -                                            |
| Northward Wind                   | va (m/s)      | v (m/s)            | va (m/s)        | -                                            |
| Vertical velocity omega (=dp/dt) | wap (Pa/s)    | omega (Pa/s)       | wap (Pa/s)      | -                                            |
| Geopotential Height              | zg (m)        | geopot (m2/s2)     | zg (m)          | ICON-XPP: zg needs to be derived from geopot |

## Output Frequency

- Most diagnostics are tailored towards **monthly mean** data, but should in
  principle work with higher frequency output (this might take longer, though).
- Some diagnostics require sub-daily (preferably **1-hourly**) output.
- Sub-hourly output is **not** supported at the moment.
- The output should contain **averaged** quantities, not **instantaneous**
  values.

## File Naming

The output files should follow one of the following naming conventions:

- `{exp}/{exp}_{var_type}*.nc`
- `{exp}/outdata/{exp}_{var_type}*.nc`

`{exp}` corresponds to the name of your experiment, and `{var_type}` to the
type of the output variable (namelist; e.g., `atm_2d_ml`).

If possible, one file should contain one simulated year. Less than that is fine
(e.g., one file per time step) but makes the evaluation slower; more than that
(e.g., one file per 5 years) is **not** supported at the moment.

## Simulation Period

- If possible, at least 20 years should be simulated. This enables a meaningful
  comparison to reference data like observations.
- Usually, simulations start in 1979. This might be problematic, since most
  satellite observations are only available for later years. Thus, the starting
  year might change to a later year in the future.
- Simulations should not start earlier than 1979-01-01 and not end after
  2020-12-31 for maximum overlap with the reference data.
