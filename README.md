# ammcpc --- Archivematica (AM) MediaConch (MC) Policy Checker (PC)

[![PyPI version](https://img.shields.io/pypi/v/ammcpc.svg)](https://pypi.python.org/pypi/ammcpc)
[![GitHub CI](https://github.com/artefactual-labs/ammcpc/actions/workflows/test.yml/badge.svg)](https://github.com/artefactual-labs/ammcpc/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/artefactual-labs/ammcpc/branch/master/graph/badge.svg?token=rNmMA59AqJ)](https://codecov.io/gh/artefactual-labs/ammcpc)

This command-line application and python module is a simple wrapper around the
MediaConch tool which takes a file and a MediaConch policy file as input and
prints to stdout a JSON object indicating, in a way that Archivematica likes,
whether the file passes the policy check.

## Installation

Install with pip:

```shell
    pip install ammcpc
```

Install from source:

```shell
    python setup.py install
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

## Testing

To run the tests, make sure tox is installed, then:

```shell
    tox
```
