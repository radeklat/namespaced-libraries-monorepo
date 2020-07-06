"""
Runnable tasks for this project. Project tooling for build, distribute, etc.

Invoked with the Python `invoke` framework. Tasks should be invoked from the project root directory, not
the `tasks` dir.

Task code is for tooling only and should strictly not be mixed with `src` code.
"""

from invoke import Collection

from tasks.sub_package import install_subpackage_dependencies, switch_python_version
from tasks.build import build

namespace = Collection()  # pylint: disable=invalid-name

namespace.add_task(build)
namespace.add_task(install_subpackage_dependencies)
namespace.add_task(switch_python_version)
