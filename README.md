# A YAML parser for Python

## Usage

```python
from yaml_parser import load, prettyprint

filename = 'tests/simple.example.yaml'

# Load data from .yaml file
result = load(filename)
print(result)

# Print a colored version of the .yaml file
prettyprint(filename)
```

## Note

YAML 1.2 documentation can be found [here](http://yaml.org/spec/1.2/spec.html).

`yaml_parser` only supports a small set of features of YAML and only allows to load data from YAML files,
not to serialize python data into YAML format. For an overview of what features of YAML are supported, please take a
look at `tests/simple.example.yaml`.

`yaml_parser.parser.Parser` implements a recursive descent parser based on a reduced version of the YAML grammar.

`yaml_parser.tokenizer.tokenizer` is a lexer/tokenizer for analysing YAML data. It covers more features of YAML than the parser.

## Testing

Use `unittest`'s autodiscovery:

```
$ python -m unittest
```