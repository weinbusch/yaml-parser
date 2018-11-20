# A YAML parser for Python

## Usage

```python
from yaml_parser import load

filename = 'tests/simple.example.yaml'

# Load data from .yaml file
result = load(filename)
print(result)
```

## Note

This is a test project driven by curiosity only. For a functioning Python YAML parser, take a look at
[ruamel.yaml](https://pypi.org/project/ruamel.yaml/).

YAML 1.2 documentation can be found [here](http://yaml.org/spec/1.2/spec.html).

`yaml_parser` only supports a small set of features of YAML and only allows to load data from YAML files,
not to serialize python data into YAML format. For an overview of what features of YAML are supported, please take a
look at `tests/simple.example.yaml`.

`yaml_parser.parser.Parser` implements a recursive descent parser based on a reduced version of the YAML grammar.

`yaml_parser.tokenizer.tokenizer` is a lexer/tokenizer for analysing YAML data.

## Testing

Tests reside in `tests/tests.py`. Use `unittest`'s autodiscovery to run the tests:

```
$ python -m unittest
```