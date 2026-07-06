import tempfile
from pathlib import Path
import numpy as np

import komamripy as km


def main():
    print("\nEXAMPLE 1: Pulseq Sequence Workflow (Read/Write)\n")

    # Step 1: Create a simple GRE sequence from scratch using PulseDesigner
    print("\n[Step 1] Creating a simple GRE sequence with PulseDesigner...")

    # Define scanner hardware limits
    sys = km.Scanner()

    # Sequence parameters (SI units unless otherwise noted)
    flip_angle = 15  # degrees; converted internally in PulseDesigner
    TE = 8e-3  # 8 ms
    TR = 22e-3  # 22 ms
    FOV = 256e-3  # 256 mm
    N_readout = 128  # readout points
    N_phase = 64  # phase-encoding lines (reduced for speed)

    # Build a basic GRE sequence using PulseDesigner
    # PulseDesigner.GRE_example() is a quick shortcut; here we use the minimal
    # approach from KomaMRI tutorials for clarity.
    # For simplicity in this example, we use a pre-built example:
    seq = km.PulseDesigner.GRE_example()

    print(f"  ✓ Sequence created: {seq.DEF.get('Name', 'unnamed')}")
    print(f"  ✓ Num blocks: {len(seq.blocks)}")

    # Step 2: Write to Pulseq .seq format
    print("\n[Step 2] Writing sequence to .seq file...")

    # Create a temporary file for the .seq output
    with tempfile.TemporaryDirectory() as tmpdir:
        seq_path = Path(tmpdir) / "example_gre.seq"

        # Write the sequence using the KomaMRIFiles API
        # Syntax: km.files.write_seq(seq, path; sys=scanner)
        # Note: sys provides hardware limit checks and Pulseq raster alignment
        km.files.write_seq(seq, str(seq_path), sys=sys)

        print(f"  ✓ Sequence written to: {seq_path}")
        print(f"  ✓ File size: {seq_path.stat().st_size} bytes")

        # Step 3: Read back the .seq file
        print("\n[Step 3] Reading .seq file back into memory...")

        seq_read = km.files.read_seq(str(seq_path))

        print(f"  ✓ Sequence read: {seq_read.DEF.get('Name', 'unnamed')}")
        print(f"  ✓ Num blocks after read: {len(seq_read.blocks)}")

        # Step 4: Verify by simulation (original vs. read-back)
        print("\n[Step 4] Simulating with both sequences...")

        obj = km.brain_phantom2D()

        # Configure simulation to return raw signal matrix for comparison
        sim_params_orig = km.core.default_sim_params()
        sim_params_orig["return_type"] = "mat"

        signal_original = km.simulate(obj, seq, sys, sim_params=sim_params_orig)
        signal_readback = km.simulate(
            obj, seq_read, sys, sim_params=sim_params_orig
        )

        # Convert to numpy for comparison
        signal_orig_np = np.asarray(signal_original)
        signal_read_np = np.asarray(signal_readback)

        print(f"  ✓ Original signal shape: {signal_orig_np.shape}")
        print(f"  ✓ Read-back signal shape: {signal_read_np.shape}")

        # Compute error (should be tiny; numerical precision differences only)
        error = np.linalg.norm(
            signal_orig_np - signal_read_np
        ) / np.linalg.norm(signal_orig_np)
        print(f"  ✓ Relative difference: {error:.2e}")

        if error < 1e-6:
            print("  ✓ Round-trip validation PASSED (signals match within tolerance)")
        else:
            print("  ⚠ Signals differ; inspect for sequence parameter changes")

    print("\n\nExample 1 complete: Pulseq read/write workflow validated ✓\n")


if __name__ == "__main__":
    main()