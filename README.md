# komamripy

Pulseq-compatible, high-performance MRI simulation in Python.

`komamripy` is powered by the Julia package [KomaMRI.jl](https://github.com/JuliaHealth/KomaMRI.jl), which is designed for fast CPU/GPU MRI simulation.

## Why komamripy?

```python
import komamripy as km

sys = km.Scanner()
obj = km.brain_2dphantom()
seq = km.PulseDesigner.EPI_example()

raw = km.simulate(obj, seq, sys)
```
