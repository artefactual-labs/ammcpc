# ammcpc --- Archivematica (AM) MediaConch (MC) Policy Checker (PC)

[![PyPI version](https://img.shields.io/pypi/v/ammcpc.svg)](https://pypi.python.org/pypi/ammcpc)
[![GitHub CI](https://github.com/artefactual-labs/ammcpc/actions/workflows/test.yml/badge.svg)](https://github.com/artefactual-labs/ammcpc/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/artefactual-labs/ammcpc/branch/main/graph/badge.svg?token=rNmMA59AqJ)](https://codecov.io/gh/artefactual-labs/ammcpc)

This command-line application and python module is a simple wrapper around the
MediaConch tool which takes a file and a MediaConch policy file as input and
prints to stdout a JSON object indicating, in a way that Archivematica likes,
whether the file passes the policy check.

## Installation

Install with pip:

```shell
    pip install ammcpc
```

## Usage

Command-line usage:

```shell
    ammcpc <PATH_TO_FILE> <PATH_TO_POLICY>
```

Python usage with a policy file path:

```python
    >>> from ammcpc import MediaConchPolicyCheckerCommand
    >>> policy_checker = MediaConchPolicyCheckerCommand(
            policy_file_path='/path/to/my-policy.xml')
    >>> exitcode = policy_checker.check('/path/to/file.mkv')
```

Python usage with a policy as a string:

```python
    >>> policy_checker = MediaConchPolicyCheckerCommand(
            policy='<?xml><policy> ... </policy>',
            policy_file_name='my-policy.xml')
    >>> exitcode = policy_checker.check('/path/to/file.mkv')
```

## Requirements

System dependencies:

- MediaConch version 16.12

## Development workflows

Install uv using the [uv installation documentation], then synchronize the
locked project and development dependencies:

```shell
    make sync
```

The Makefile exposes the common workflows:

- `make sync-runtime` installs only the project and runtime dependencies.
- `make sync` also installs development tools.
- `make lock-check` verifies that `uv.lock` matches `pyproject.toml`.
- `make lock` refreshes the lock without upgrading existing versions, while
  `make upgrade` upgrades all dependencies.
- `make check` verifies the lock and runs all pre-commit checks.
- `make test PYTEST_ARGS="..."` runs pytest with optional arguments.
- `make package-check` builds the distributions into `dist/` and validates
  them with twine.

Declare runtime dependencies in `project.dependencies` and development
dependencies in `dependency-groups.dev` in `pyproject.toml`. The committed
`uv.lock` is the sole dependency lock; requirements exports are not maintained.

The exact default interpreter is pinned in `.python-version`. Local uv commands
and the `setup-uv` GitHub Action discover it automatically. CI matrices
override this default to exercise every supported Python version. To upgrade
the default, update `.python-version` and run `make lock`. If the supported
range changes, also update `project.requires-python`, the classifiers and the
CI matrix.

`tool.uv.required-version` declares the minimum supported uv version and
accepts newer global installations. To raise it, update the value and run
`make lock` and `make check`.

The package version lives in `ammcpc/ammcpc.py`; release commits only need to
update `__version__` there. The lock does not record the project version.

[uv installation documentation]: https://docs.astral.sh/uv/getting-started/installation/
