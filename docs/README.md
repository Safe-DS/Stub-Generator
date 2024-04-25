# Stub Generator

[![PyPI](https://img.shields.io/pypi/v/safe-ds-stubgen)](https://pypi.org/project/safe-ds-stubgen)
[![Main](https://github.com/Safe-DS/Stub-Generator/actions/workflows/main.yml/badge.svg)](https://github.com/Safe-DS/Stub-Generator/actions/workflows/main.yml)
[![codecov](https://codecov.io/gh/Safe-DS/Stub-Generator/branch/main/graph/badge.svg?token=UyCUY59HKM)](https://codecov.io/gh/Safe-DS/Stub-Generator)
[![Documentation Status](https://readthedocs.org/projects/safe-ds-stub-generator/badge/?version=stable)](https://stubgen.safeds.com)

Automated generation of [Safe-DS stubs](https://dsl.safeds.com/en/stable/stub-language/) for Python libraries.

## Installation

Get the latest version from [PyPI](https://pypi.org/project/safe-ds-stubgen):

```shell
pip install safe-ds-stubgen
```

## Usage

To run this program:

```txt
usage: safe-ds-stubgen [-h] [-v] -p PACKAGE [-s SRC] -o OUT [--docstyle {PLAINTEXT,EPYDOC,GOOGLE,NUMPYDOC,REST}] [-tr] [-nc]

Analyze Python code.

options:
  -h, --help            show this help message and exit
  -v, --verbose         show info messages
  -p PACKAGE, --package PACKAGE
                        The name of the package.
  -s SRC, --src SRC     Source directory containing the Python code of the package.
  -o OUT, --out OUT     Output directory.
  --docstyle {PLAINTEXT,EPYDOC,GOOGLE,NUMPYDOC,REST}
                        The docstring style.
  -tr, --testrun        Set this flag if files in /test or /tests directories should be included.
  -nc, --naming_convert
                        Set this flag if the name identifiers should be converted to Safe-DS standard (UpperCamelCase for classes and camelCase for everything else).
```

## Documentation

You can find the full documentation [here](https://stubgen.safeds.com).

## Contributing

We welcome contributions from everyone. As a starting point, check the following resources:

* [Setting up a development environment](https://stubgen.safeds.com/en/latest/development/environment/)
* [Project guidelines](https://stubgen.safeds.com/en/latest/development/project_guidelines/)
* [Contributing page](https://github.com/Safe-DS/Stub-Generator/contribute)

If you need further help, please [use our discussion forum][forum].

[forum]: https://github.com/orgs/Safe-DS/discussions
