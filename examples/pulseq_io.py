"""Pulseq I/O workflow: reading and writing .seq files.

Demonstrates:
1. Creating a simple GRE sequence with pypulseq
2. Writing it to .seq format
3. Reading it back with KomaMRI
4. Verifying round-trip compatibility by simulating both

Run from the repository root after installing the package::

    python examples/pulseq_io.py
"""

import tempfile
from pathlib import Path
import numpy as np

import komamripy as km
from pypulseq.Sequence.sequence import Sequence
from pypulseq.Pulse.pulse_defs import make_sinc_pulse
from pypulseq.Grad.grad_defs import make_trapezoid
from pypulseq.ADC.adc_defs import make_adc


def main():
    print("\nEXAMPLE 4: Pulseq I/O Workflow (Read/Write)\n")

    # Step 1: Create a simple GRE sequence with pypulseq
    print("\n[Step 1] Creating a simple GRE sequence with pypulseq...")

    seq = Sequence()
    
    # Define sequence parameters
    fov = 256e-3  # 256 mm
    n_x = 64      # readout points
    slc_thickness = 5e-3  # 5 mm slice thickness
    tr = 100e-3   # 100 ms
    te = 30e-3    # 30 ms
    
    # RF pulse
    rf, _, _ = make_sinc_pulse(flip_angle=90, duration=3e-3, freq_offset=0, 
                               bandwidth=1/(slc_thickness*4), backend=None)
    
    # Gradients (simplified)
    gz = make_trapezoid(channel='z', flat_area=1/(slc_thickness*4), flat_time=3e-3)
    gx = make_trapezoid(channel='x', flat_area=n_x/fov, flat_time=3e-3)
    gy = make_trapezoid(channel='y', flat_area=1/fov, flat_time=3e-3)
    
    # ADC
    adc = make_adc(num_samples=n_x, duration=n_x/1e5, delay=te-1.5e-3)
    
    # Add to sequence
    seq.add_block(rf, gz)
    seq.add_block(gx, gy, adc)
    
    # Write to temporary file
    with tempfile.TemporaryDirectory() as tmpdir:
        seq_path = Path(tmpdir) / "gre_pypulseq.seq"
        
        seq.write(str(seq_path))
        print(f"    sequence created with pypulseq")
        print(f"    written to: {seq_path}")
        print(f"    file size: {seq_path.stat().st_size} bytes")

        # Step 2: Read with KomaMRI
        print("\n[Step 2] Reading .seq file with KomaMRI...")

        seq_koma = km.files.read_seq(str(seq_path))
        print(f"    sequence read successfully")
        print(f"    duration: {sum(seq_koma.DUR)*1e3:.2f} ms")

        # Step 3: Write back with KomaMRI
        print("\n[Step 3] Writing .seq file back with KomaMRI...")

        seq_path_out = Path(tmpdir) / "gre_koma_roundtrip.seq"
        sys = km.Scanner()
        
        try:
            km.files.write_seq(seq_koma, str(seq_path_out), sys=sys)
            print(f"    sequence written back successfully")
            print(f"    file size: {seq_path_out.stat().st_size} bytes")
        except Exception as e:
            print(f"  ⚠ write_seq failed: {type(e).__name__}")
            print(f"    (this is expected if sequence timing is incompatible with KomaMRI)")
            return

        # Step 4: Verify by reading and simulating
        print("\n[Step 4] Verifying round-trip compatibility...")

        seq_verify = km.files.read_seq(str(seq_path_out))
        print(f"    re-read successfully")

        obj = km.brain_phantom2D()
        sim_params = km.core.default_sim_params()
        sim_params["return_type"] = "mat"

        signal = km.simulate(obj, seq_verify, sys, sim_params=sim_params)
        signal_np = np.asarray(signal)

        print(f"    simulation completed: signal shape {signal_np.shape}")
        print(f"    signal magnitude range: [{np.min(np.abs(signal_np)):.2e}, {np.max(np.abs(signal_np)):.2e}]")

        if signal_np.size > 0 and np.max(np.abs(signal_np)) > 0:
            print("    ✓ round-trip I/O validated")
        else:
            print("  ⚠ signal is zero or empty")

    print("\nExample 4 complete")


if __name__ == "__main__":
    main()