# Example data

Synthetic sample datasets for the documentation's worked examples, loaded with
`iws.example_data("<name>")`. They exist so an example can be copied out of the
docs and run as-is, with no download and no network.

**These are illustrations, not reference measurements.** Substitute your own
export, or read a measurement from the platform.

Each one is simulated from the model its example fits, at a known parameter
value the example's fit is checked against. The generators ship in the source
distribution and use only the package's public dependencies; the wheel carries
only the generated data.

| Dataset | Columns | Simulated from |
|---|---|---|
| `current_driven_discharge` | `Time [s]`, `Current [A]`, `Voltage [V]` | SPMe, C/2 discharge |
| `eis_synthetic` | `Frequency [Hz]`, `Z_Re [Ohm]`, `Z_Im [Ohm]` | DFN, frequency domain |
| `msmr_half_cell_ocp` | `Capacity [A.h]`, `Voltage [V]` | MSMR half-cell OCP, graphite |
| `cycle_ageing_summary` | `Cycle number`, `LLI [%]` | SPMe, solvent-diffusion-limited SEI |
