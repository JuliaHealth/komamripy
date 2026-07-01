# komamripy

[![CI](https://github.com/JuliaHealth/komamripy/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/JuliaHealth/komamripy/actions/workflows/ci.yml)

**Pulseq-compatible, high-performance MRI simulation in Python.**

`komamripy` is a thin Python interface to
[KomaMRI.jl](https://github.com/JuliaHealth/KomaMRI.jl), a high-performance
Julia framework for MRI simulation. It exposes KomaMRI to Python through
[juliacall](https://juliapy.github.io/PythonCall.jl/stable/juliacall/), so
Python users can run fast CPU/GPU MRI simulations without writing any Julia.

## Installation

Install from PyPI with [uv](https://docs.astral.sh/uv/) (recommended):

```bash
uv init project-folder
cd project-folder
uv add komamripy
```

or with pip:

```bash
pip install komamripy
```

You do **not** need to install Julia yourself: `juliacall` provisions a suitable
Julia automatically, and KomaMRI is installed on first import.

The examples additionally use NumPy (`pip install numpy`), which is not a runtime
dependency of `komamripy` itself.

## Quick start

The first import downloads Julia and precompiles KomaMRI, which can take a few
minutes. Subsequent runs are fast.

```python
import komamripy as km
import numpy as np

sys = km.Scanner()                       # scanner hardware
obj = km.brain_phantom2D()               # 2D brain phantom
seq = km.PulseDesigner.EPI_example()     # example EPI sequence

sim_params = km.KomaMRICore.default_sim_params()
sim_params["return_type"] = "mat"        # return the raw signal matrix

raw = km.simulate(obj, seq, sys, sim_params=sim_params)
signal = np.asarray(raw)

print(signal.shape)
```

A runnable version lives in [`examples/`](examples/).

## How it works

`komamripy` mirrors the KomaMRI Julia namespace: any function or type that
KomaMRI exposes is available as an attribute of `komamripy`. Julia code
therefore translates to Python almost line for line.

Simulation results are returned as Julia objects; convert array-like results to
NumPy with `numpy.asarray`.

## Status

`komamripy` is under active development as a Google Summer of Code project.

Currently supported: the core simulation pipeline and reading Pulseq files.

Planned: GPU backend selection, tighter pypulseq integration, and differentiable
workflows.