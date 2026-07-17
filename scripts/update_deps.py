"""Resolve KomaMRI dependencies and update juliapkg.json and pyproject.toml."""

import json
import re
import subprocess
import sys
from pathlib import Path


def resolve_julia_versions():
    """Resolve KomaMRI package versions using Julia.

    Returns:
        Dict mapping package names to version strings.
    """

    julia_code = """
import Pkg
names = [
    "KomaMRI",
    "KomaMRIBase",
    "KomaMRICore",
    "KomaMRIFiles",
    "KomaMRIPlots",
]
Pkg.Registry.update()
Pkg.activate(; temp=true)
Pkg.add(names)

resolved = Dict(pkg.name => pkg.version for pkg in values(Pkg.dependencies()))
for name in names
    println(name, '\t', resolved[name])
end
"""

    try:
        result = subprocess.run(
            ["julia", "-e", julia_code],
            capture_output=True,
            text=True,
            timeout=300,
        )

        if result.returncode != 0:
            print(f"Julia resolution failed:\n{result.stderr}", file=sys.stderr)
            sys.exit(1)

        return dict(line.split("\t", 1) for line in result.stdout.splitlines())
    except FileNotFoundError:
        print("Error: Julia not found. Install Julia.", file=sys.stderr)
        sys.exit(1)
    except subprocess.TimeoutExpired:
        print("Error: Julia resolution timed out (5 min).", file=sys.stderr)
        sys.exit(1)


def compare_versions(current, resolved):
    """Compare current and resolved versions.

    Returns:
        (changes_list, updated_bool, new_python_version)
    """
    changes = []
    updated = False

    pkg_names = [
        "KomaMRI",
        "KomaMRIBase",
        "KomaMRICore",
        "KomaMRIFiles",
        "KomaMRIPlots",
    ]
    for pkg in pkg_names:
        old_version = current["packages"][pkg]["version"].lstrip("=")
        new_version = resolved[pkg]

        if old_version != new_version:
            updated = True
            changes.append(f"{pkg}: {old_version} → {new_version}")
            current["packages"][pkg]["version"] = f"={new_version}"

    # Bump Python patch version if anything changed
    new_python_version = None
    if updated:
        pyproject_path = Path("pyproject.toml")
        with open(pyproject_path) as f:
            content = f.read()

        match = re.search(r'version = "(\d+)\.(\d+)\.(\d+)"', content)
        if match:
            major, minor, patch = match.groups()
            new_python_version = f"{major}.{minor}.{int(patch) + 1}"
            content = re.sub(
                r'version = "\d+\.\d+\.\d+"',
                f'version = "{new_python_version}"',
                content,
            )
            with open(pyproject_path, "w") as f:
                f.write(content)

    return changes, updated, new_python_version


def format_pr_body(changes):
    """Format dependency changes for the automated pull request."""
    lines = ["## Version Changes", ""]
    for change in changes:
        package, versions = change.split(": ", 1)
        lines.append(f"- **{package}**: {versions}")
    return "\n".join(lines)


def main():
    # Read current juliapkg.json
    juliapkg_path = Path("src/komamripy/juliapkg.json")
    with open(juliapkg_path) as f:
        current = json.load(f)

    # Resolve Julia versions
    resolved = resolve_julia_versions()

    # Compare and update
    changes, updated, new_python_version = compare_versions(current, resolved)

    if not updated:
        return 0

    # Write updated juliapkg.json
    with open(juliapkg_path, "w") as f:
        json.dump(current, f, indent=2)
        f.write("\n")  # Add newline at end

    print(format_pr_body(changes))

    return 0


if __name__ == "__main__":
    sys.exit(main())
