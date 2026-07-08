"""Run every example script."""

import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = [path.relative_to(ROOT) for path in sorted((ROOT / "examples").glob("*.py"))]


@pytest.mark.parametrize("example", EXAMPLES, ids=str)
def test_example_runs(example):
    subprocess.run(
        # Run with the same Python interpreter as pytest.
        [sys.executable, str(example)],
        # Match normal usage from the repository root.
        cwd=ROOT,
        # Avoid opening plot windows when examples call plt.show().
        env=os.environ | {"MPLBACKEND": "Agg"},
        # Fail the test if the script exits with an error.
        check=True,
    )
