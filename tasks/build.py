"""Type checking on source code."""

import os
import shutil

from invoke import call, task

from tasks.sub_package import install_subpackage_dependencies
from tasks.utils import PROJECT_INFO, print_header


@task(pre=[call(install_subpackage_dependencies, force=True)])
def build(ctx):
    print_header("Running build", icon="🔨")

    for package in os.listdir(PROJECT_INFO.namespace_directory):
        print_header(f"Building '{package}' package", level=2)

        print("Cleanup the 'build' directory")
        shutil.rmtree("build", ignore_errors=True)

        ctx.run(
            f"python setup.py bdist_wheel --package {package}",
            env={"PYTHONPATH": PROJECT_INFO.source_directory},
            pty=True,
        )
