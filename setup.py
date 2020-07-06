import os
import sys
from os.path import join
from typing import List

from setuptools import find_namespace_packages, setup

import importlib

SOURCES_ROOT = "src"
NAMESPACE = "company_utils"
PACKAGES_PATH = join(SOURCES_ROOT, NAMESPACE)


def parse_requirements_txt(filename: str) -> List[str]:
    with open(filename) as fd:
        return list(filter(lambda line: bool(line.strip()), fd.read().splitlines()))


def get_sub_package(packages_path: str) -> str:
    package_cmd = "--package"
    packages = os.listdir(packages_path)
    available_packages = ", ".join(packages)

    if package_cmd not in sys.argv:
        raise RuntimeError(
            f"Specify which package to build with '{package_cmd} <PACKAGE NAME>'. "
            f"Available packages are: {available_packages}"
        )

    index = sys.argv.index(package_cmd)
    sys.argv.pop(index)  # Removes the switch
    package = sys.argv.pop(index)  # Returns the element after the switch
    if package not in packages:
        raise RuntimeError(
            f"Unknown package '{package}'. Available packages are: {available_packages}"
        )
    return package


def get_version(sub_package: str) -> str:
    return importlib.import_module(f"{SOURCES_ROOT}.{NAMESPACE}.{sub_package}").__version__


SUB_PACKAGE = get_sub_package(PACKAGES_PATH)

setup(
    name=f"{NAMESPACE}.{SUB_PACKAGE.replace('_utils', '')}",
    version=get_version(SUB_PACKAGE),
    url="https://github.com/radeklat/namespaced-libraries-monorepo",
    author="A company",
    description="Common utilities for my company",
    long_description=__doc__,
    # See https://setuptools.readthedocs.io/en/latest/setuptools.html#find-namespace-packages
    package_dir={"": SOURCES_ROOT},
    packages=find_namespace_packages(
        where=SOURCES_ROOT, include=[f"{NAMESPACE}.{SUB_PACKAGE}"]
    ),
    include_package_data=True,
    zip_safe=False,
    platforms="any",
    install_requires=parse_requirements_txt(
        join(PACKAGES_PATH, SUB_PACKAGE, "requirements.txt")
    ),
    python_requires=">=3.6,<3.9",
    classifiers=[
        # As from http://pypi.python.org/pypi?%3Aaction=list_classifiers
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
