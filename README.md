# namespaced-libraries-monorepo

Example of a collection of Python namespaced libraries (PEP 420) in a monorepo. See [Package namespacing for Python library collection](https://lat.sk/2020/06/python-package-namespacing-git-monorepo/).

# Examples

### Installing all development dependencies

```bash
pip install pipenv
pipenv install -d
pipenv run inv install-subpackage-dependencies
```

### Installing dependencies for one sub-package only

```bash
pipenv run inv install-subpackage-dependencies --name flask_utils
```

### Building all sub-packages

```bash
pipenv run inv build
```

Result in `dist`:

```text
company_utils.constants-1.0.0-py3-none-any.whl
company_utils.flask-1.0.1-py3-none-any.whl
company_utils.logging-2.3.1-py3-none-any.whl
```

### Resetting the repository

```bash
git clean -fxd .
```

### Switching to a different Python version

```bash
pipenv run inv switch-python-version 3.7
```