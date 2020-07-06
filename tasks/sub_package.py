"""Type checking on source code."""
import hashlib
import os
import re
from collections import defaultdict
from typing import Dict, List, Match

from invoke import call, task
from termcolor import colored, cprint

from tasks.utils import PROJECT_INFO, print_header

_CHECKSUM_CACHE_FILE = ".requirements-checksum.txt"
_RE_PIP_CONFLICT = re.compile("Attempting uninstall: ([^\n]+)\n", re.MULTILINE)
_RE_DEPENDENCY_SPLIT = re.compile("[><=~]+")


def _list_libraries(requirements: str) -> List[str]:
    return list(
        filter(None, (_RE_DEPENDENCY_SPLIT.split(line.strip(), maxsplit=1)[0] for line in requirements.split("\n")),)
    )


def _print_conflicting_packages(libraries_to_sub_packages: Dict[str, List[str]], conflicts: List[Match]):
    if not conflicts:
        return

    warning: Dict = {"color": "yellow"}
    highlight: Dict = {**warning, "attrs": ["bold"]}
    indentation = colored("  * ", **warning)

    conflicts_list = indentation + indentation.join(
        colored(match.group(1), **highlight)
        + colored(" in sub-packages ", **warning)
        + colored(", ", **warning).join(
            colored(sub_package, **highlight) for sub_package in libraries_to_sub_packages[match.group(1)]
        )
        for match in conflicts
    )
    cprint("\nWARNING: ", attrs=["bold"], color="yellow", end="")
    cprint("Conflicting dependency versions detected:\n", **warning)
    print(conflicts_list)
    cprint(
        "\nLocal development may not work as expected. To fix this, see if you can "
        "specify all requirements using overlapping versions range.",
        **warning,
    )


def _requirements_checksum_not_changed(requirements: str) -> bool:
    try:
        with open(_CHECKSUM_CACHE_FILE) as file_pointer:
            existing_requirements_checksum = file_pointer.read()
    except FileNotFoundError:
        existing_requirements_checksum = ""

    new_requirements_checksum = hashlib.sha512(requirements.encode()).hexdigest()

    if existing_requirements_checksum == new_requirements_checksum:
        cprint(
            "\nRequirements have not changed. Skipping re-install. You can force it with:\n  "
            "pipenv run inv install-subpackage-dependencies --force",
            color="blue",
        )
        return True

    with open(_CHECKSUM_CACHE_FILE, "w") as file_pointer:
        file_pointer.write(new_requirements_checksum)

    cprint("\nOne or more requirements.txt files have been changed.", color="yellow")
    return False


@task
def install_subpackage_dependencies(ctx, name=None, force=False):
    """Replaces top-level Pipfile dependencies with sub-package dependencies.

    Use in CI to install only single sub-package dependencies.
    Use without the ``name`` in local development to get dependencies from all sub-packages.

    Args:
        ctx (invoke.Context): Context
        name (Optional[str]): Name of sub-package for which to collect and install dependencies.
            If not specified, all sub-packages will be used.
        force (bool): Forces reinstall.
    """
    print_header("Sub-packages", icon="📦")
    print_header("Collecting dependencies", level=2, icon="🛒")

    packages = os.listdir(PROJECT_INFO.namespace_directory) if name is None else [name]
    all_requirements = ""
    libraries_to_sub_packages = defaultdict(list)

    for package in packages:
        print(f"  * Collecting '{package}' package")
        with open(PROJECT_INFO.namespace_directory / package / "requirements.txt") as file_pointer:
            requirements = file_pointer.read()
            all_requirements += requirements
            for library in _list_libraries(requirements):
                libraries_to_sub_packages[library].append(package)

    if not force and _requirements_checksum_not_changed(all_requirements):
        return

    print_header("Uninstalling previous dependencies", level=2, icon="🔽")
    ctx.run("pipenv clean", pty=True)

    print_header("Installing new dependencies", level=2, icon="🔼")
    conflicts: List[Match] = []

    for package in packages:
        print_header(package, level=3)
        requirements_file_path = PROJECT_INFO.namespace_directory / package / "requirements.txt"
        result = ctx.run(f"pipenv run pip install -r {requirements_file_path}", echo=True)
        conflicts.extend(match for match in _RE_PIP_CONFLICT.finditer(result.stdout))

    _print_conflicting_packages(libraries_to_sub_packages, conflicts)


@task(post=[call(install_subpackage_dependencies, force=True)])
def switch_python_version(ctx, version):
    """Switches the local Python virtual environment to a different Python version.

    Use this to test the sub-packages with a different Python version. CI pipeline always
    checks all supported versions automatically.

    Notes:
        This task calls ``deactivate`` as a precaution for cases when the task is called
        from an active virtual environment.

    Args:
        ctx (invoke.Context): Context
        version (str): Desired Python version. You can use only MAJOR.MINOR (for example 3.6).
    """
    print_header(f"Switching to Python {version}", icon="🐍")
    ctx.run(f"deactivate; git clean -fxd .venv && pipenv sync --python {version} -d", pty=True)
