"""Build a PyPulseq EPI sequence, read it with KomaMRI, and show an image."""

import os
import tempfile

import matplotlib.pyplot as plt
import numpy as np
import pypulseq as pp
import sigpy as sp

import komamripy as km

# Build a PyPulseq sequence
system = pp.Opts(
    max_grad=32,
    grad_unit="mT/m",
    max_slew=130,
    slew_unit="T/m/s",
    rf_ringdown_time=30e-6,
    rf_dead_time=100e-6,
)
seq = pp.Sequence(system=system)
fov = 220e-3
matrix_size = 64
slice_thickness = 3e-3
delta_k = 1 / fov
rf, gz, gz_reph = pp.make_sinc_pulse(
    flip_angle=np.pi / 2,
    duration=3e-3,
    slice_thickness=slice_thickness,
    return_gz=True,
    system=system,
    delay=system.rf_dead_time,
    use="excitation",
)
adc_dwell = 4e-6
adc_duration = matrix_size * adc_dwell
gx_flat_time = np.ceil(adc_duration / system.grad_raster_time) * system.grad_raster_time
gx_amp = matrix_size * delta_k / adc_duration
gx = pp.make_trapezoid("x", amplitude=gx_amp, flat_time=gx_flat_time, system=system)
adc_delay = gx.rise_time + gx_flat_time / 2 - (adc_duration - adc_dwell) / 2
adc_pos = pp.make_adc(
    matrix_size,
    duration=adc_duration,
    delay=adc_delay - adc_dwell,
)
adc_neg = pp.make_adc(matrix_size, duration=adc_duration, delay=adc_delay)
pre_time = 8e-4
phase_pre_area = -matrix_size / 2 * delta_k
gx_pre = pp.make_trapezoid("x", area=-gx.area / 2, duration=pre_time, system=system)
gy_pre = pp.make_trapezoid("y", area=phase_pre_area, duration=pre_time, system=system)
gy_blip_duration = 2 * np.sqrt(delta_k / system.max_slew)
grad_raster_time = system.grad_raster_time
gy_blip_duration = np.ceil(gy_blip_duration / grad_raster_time) * grad_raster_time
gy = pp.make_trapezoid("y", area=delta_k, duration=gy_blip_duration, system=system)
seq.add_block(rf, gz)
seq.add_block(gx_pre, gy_pre, gz_reph)
for line in range(matrix_size):
    seq.add_block(gx, adc_pos if line % 2 == 0 else adc_neg)
    seq.add_block(gy)
    gx.amplitude = -gx.amplitude

# Bridge PyPulseq to KomaMRI through the Pulseq file format
with tempfile.TemporaryDirectory() as tmpdir:
    seq_path = os.path.join(tmpdir, "simple_pypulseq.seq")
    seq.write(seq_path)  # PyPulseq write
    seq_koma = km.files.read_seq(seq_path)

# Define simulation inputs
sys = km.Scanner()
obj = km.brain_phantom2D()
obj.Δw = np.zeros_like(obj.Δw)  # removes fat off-resonance
sim_params = {"return_type": "mat"}

# Simulate with KomaMRI
signal = km.simulate(obj, seq_koma, sys, sim_params=sim_params)
signal = np.asarray(signal).reshape(-1)

# Reconstruct with SigPy
kdata = signal.reshape(matrix_size, matrix_size)
kdata[1::2] = kdata[1::2, ::-1]
image = sp.ifft(kdata, axes=(0, 1))

# Show the reconstructed image
plt.imshow(np.abs(image), cmap="gray", origin="lower")
plt.title("PyPulseq EPI")
plt.axis("off")
plt.show()
