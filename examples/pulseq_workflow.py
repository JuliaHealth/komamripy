"""Pulseq sequence read/write workflow.

Demonstrates:
1. Creating a simple GRE sequence in KomaMRI using PulseDesigner
2. Writing it to standard Pulseq .seq format
3. Reading it back and simulating
4. Verifying round-trip compatibility

Run from the repository root after installing the package::

    python examples/pulseq_workflow.py
"""

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

    # Build a basic GRE sequence using PulseDesigner
    seq = km.PulseDesigner.EPI_example()

    print(f"    sequence created: {seq.DEF.get('Name', 'unnamed')}")
    print(f"    num blocks: {len(seq.blocks)}")

    # Step 2: Write to Pulseq .seq format
    print("\n[Step 2] Writing sequence to .seq file...")

    # Create a temporary file for the .seq output
    with tempfile.TemporaryDirectory() as tmpdir:
        seq_path = Path(tmpdir) / "example_gre.seq"

        # Write the sequence using the KomaMRIFiles API
        km.files.write_seq(seq, str(seq_path), sys=sys)

        print(f"    sequence written to: {seq_path}")
        print(f"    file size: {seq_path.stat().st_size} bytes")

        # Step 3: Read back the .seq file
        print("\n[Step 3] Reading .seq file back into memory...")

        seq_read = km.files.read_seq(str(seq_path))

        print(f"    sequence read: {seq_read.DEF.get('Name', 'unnamed')}")
        print(f"    num blocks after read: {len(seq_read.blocks)}")

        # Step 4: Verify by simulation (original vs. read-back)
        print("\n[Step 4] Simulating with both sequences...")

        obj = km.brain_phantom2D()

        # Configure simulation to return raw signal matrix for comparison
        sim_params_orig = km.core.default_sim_params()
        sim_params_orig["return_type"] = "mat"

        signal_original = km.simulate(obj, seq, sys, sim_params=sim_params_orig)
        signal_readback = km.simulate(obj, seq_read, sys, sim_params=sim_params_orig)

        # Convert to numpy for comparison
        signal_orig_np = np.asarray(signal_original)
        signal_read_np = np.asarray(signal_readback)

        print(f"    original signal shape: {signal_orig_np.shape}")
        print(f"    read-back signal shape: {signal_read_np.shape}")

        # Compute error (should be tiny; numerical precision differences only)
        error = np.linalg.norm(signal_orig_np - signal_read_np) / np.linalg.norm(signal_orig_np)
        print(f"    relative difference: {error:.2e}")

        if error < 1e-6:
            print("    round-trip validation PASSED (signals match within tolerance)")
        else:
            print("  ⚠ signals differ; inspect for sequence parameter changes")

    print("\nExample 1 complete")


if __name__ == "__main__":
    main()