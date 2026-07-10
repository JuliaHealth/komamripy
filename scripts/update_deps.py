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
import Pkg, JSON, Tempdir
specs = [
    Pkg.PackageSpec(name="KomaMRI", uuid="6a340f8b-2cdf-4c04-99be-4953d9b66d0a"),
    Pkg.PackageSpec(name="KomaMRIBase", uuid="d0bc0b20-b151-4d03-b2a4-6ca51751cb9c"),
    Pkg.PackageSpec(name="KomaMRICore", uuid="4baa4f4d-2ae9-40db-8331-a7d1080e3f4e"),
    Pkg.PackageSpec(name="KomaMRIFiles", uuid="fcf631a6-1c7e-4e88-9e64-b8888386d9dc"),
    Pkg.PackageSpec(name="KomaMRIPlots", uuid="76db0263-63f3-4d26-bb9a-5dba378db904"),
]
Pkg.Registry.update()
mktempdir() do tmpdir
    cd(tmpdir)
    Pkg.activate(".")
    Pkg.add(specs)
    deps = Pkg.dependencies()
    versions = Dict()
    for (name, uuid) in [
        ("KomaMRI", "6a340f8b-2cdf-4c04-99be-4953d9b66d0a"),
        ("KomaMRIBase", "d0bc0b20-b151-4d03-b2a4-6ca51751cb9c"),
        ("KomaMRICore", "4baa4f4d-2ae9-40db-8331-a7d1080e3f4e"),
        ("KomaMRIFiles", "fcf631a6-1c7e-4e88-9e64-b8888386d9dc"),
        ("KomaMRIPlots", "76db0263-63f3-4d26-bb9a-5dba378db904"),
    ]
        versions[name] = string(deps[Base.UUID(uuid)].version)
    end
    println(JSON.json(versions))
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

        return json.loads(result.stdout.strip())
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
        print("No KomaMRI updates available.")
        return 0

    # Print PR info
    print("=" * 60)
    print(f"PR Title: Bump to version {new_python_version}")
    print("=" * 60)
    print("\nVersion Changes:")
    for change in changes:
        print(f"  {change}")
    print("=" * 60)

    # Write updated juliapkg.json
    with open(juliapkg_path, "w") as f:
        json.dump(current, f, indent=2)
        f.write("\n")  # Add newline at end

    print("\n✓ Updated komamripy/juliapkg.json")
    print(f"✓ Bumped version to {new_python_version} in pyproject.toml")

    return 0


if __name__ == "__main__":
    sys.exit(main())
