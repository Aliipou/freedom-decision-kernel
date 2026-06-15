"""
The golden rule, made mechanical.

The Freedom Decision Kernel rests on a brutal epistemic separation: a minimal,
deterministic, fully-testable, non-semantic KERNEL (`fdk_kernel`) and an
experimental RESEARCH layer (`fdk_research`) layered on top. The dependency may
only run research → kernel. If the kernel ever imports from research, the gate is
no longer the gate — a soft heuristic has leaked into the hard surface.

This test IS that rule. It enforces it two ways: statically (no `fdk_research`
import statement appears in any `fdk_kernel` source file) and dynamically
(importing `fdk_kernel` from a clean module table pulls in no `fdk_research`
module). If either fails, the split has been violated — fix the import, do not
relax the test.
"""
from __future__ import annotations

import ast
import importlib
import pkgutil
import sys

import fdk_kernel


def _kernel_source_files() -> list[str]:
    paths = []
    for mod in pkgutil.walk_packages(fdk_kernel.__path__, prefix="fdk_kernel."):
        spec = importlib.util.find_spec(mod.name)
        if spec and spec.origin and spec.origin.endswith(".py"):
            paths.append(spec.origin)
    # include the package __init__ itself
    paths.extend(p for p in fdk_kernel.__path__)
    return paths


def _imported_names(source: str) -> set[str]:
    """Every top-level module name referenced by an import in `source`."""
    tree = ast.parse(source)
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            names.add(node.module.split(".")[0])
    return names


def test_kernel_source_never_imports_research():
    """STATIC: no fdk_kernel module contains an `import fdk_research` statement."""
    import os

    offenders: list[str] = []
    for directory in fdk_kernel.__path__:
        for root, _dirs, files in os.walk(directory):
            for name in files:
                if not name.endswith(".py"):
                    continue
                path = os.path.join(root, name)
                with open(path, encoding="utf-8") as fh:
                    if "fdk_research" in _imported_names(fh.read()):
                        offenders.append(path)
    assert not offenders, f"fdk_kernel modules import fdk_research: {offenders}"


def test_importing_kernel_loads_no_research_module():
    """DYNAMIC: a clean import of fdk_kernel pulls in no fdk_research module."""
    for mod in [m for m in sys.modules if m.startswith(("fdk_kernel", "fdk_research"))]:
        del sys.modules[mod]
    importlib.import_module("fdk_kernel")
    leaked = [m for m in sys.modules if m.startswith("fdk_research")]
    assert not leaked, f"importing fdk_kernel loaded research modules: {leaked}"


def test_research_does_depend_on_kernel():
    """SANITY: the dependency direction is real — research uses the kernel."""
    import fdk_research  # noqa: F401

    assert any(m.startswith("fdk_kernel") for m in sys.modules), (
        "fdk_research should import from fdk_kernel"
    )
