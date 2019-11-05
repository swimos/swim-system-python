# Swim System Python
[![Build Status](https://travis-ci.com/swimos/swim-system-python.svg?branch=master)](https://travis-ci.com/swimos/swim-system-python)

<a href="https://www.swimos.org"><img src="https://docs.swimos.org/readme/marlin-blue.svg" align="left"></a>

The **Swim System** Python implementation provides a standalone set of
frameworks for building massively real-time streaming WARP clients.
<br>
## Installation
`pip install swimai`
## Usage

## Development

### Setup
`pip install -r requirements.txt`
### Running tests
`python -m unittest`
### Build package
1) Building the package: `python setup.py sdist bdist_wheel`
2) Uploading to PyPi: `python -m twine upload  dist/*`
3) Uploading new versions: `twine upload --skip-existing dist/*`
