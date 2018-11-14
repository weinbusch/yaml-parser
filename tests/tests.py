from unittest import TestCase

from yaml_parser.tokenizer import tokenizer
from yaml_parser.parser import Parser

class TokenizerTest(TestCase):

    def assertIsToken(self, token, type, value=None, line=None, column=None):
        self.assertEqual(token.type, type)
        if value:
            self.assertEqual(token.value, value)
        if line:
            self.assertEqual(token.line, line)
        if column:
            self.assertEqual(token.column, column)

    def get_tokens(self, source):
        return list(tokenizer(source))

    def test_colon_inline(self):
        source = 'url: http://www.foo.bar'
        tokens = self.get_tokens(source)
        self.assertIsToken(tokens[0], 'scalar', 'url')
        self.assertIsToken(tokens[1], 'colon', ':')
        self.assertIsToken(tokens[2], 'scalar', 'http://www.foo.bar')

    def test_colon_linebreak(self):
        source = 'foo:\n  bar'
        tokens = self.get_tokens(source)
        self.assertIsToken(tokens[0], 'scalar', 'foo')
        self.assertIsToken(tokens[1], 'colon', ':')
        self.assertIsToken(tokens[-1], 'scalar', 'bar')
        
    def test_dash(self):
        source = '\n'.join(['- 1.2', '- -5.4'])
        tokens = self.get_tokens(source)
        self.assertIsToken(tokens[0], 'dash', '-')
        self.assertIsToken(tokens[1], 'scalar', '1.2')
        self.assertIsToken(tokens[-2], 'dash', '-')
        self.assertIsToken(tokens[-1], 'scalar', '-5.4')

    def test_comma_as_decimal_separator(self):
        source = '2,4'
        tokens = self.get_tokens(source)
        self.assertIsToken(tokens[0], 'scalar', '2,4')

    def test_scalars(self):
        source = '\n'.join(['foo', 'http://www.foo.bar', '-0.1'])
        tokens = self.get_tokens(source)
        self.assertIsToken(tokens[0], 'scalar', 'foo')
        self.assertIsToken(tokens[1], 'newline', '\n')
        self.assertIsToken(tokens[2], 'scalar', 'http://www.foo.bar')
        self.assertIsToken(tokens[3], 'newline', '\n')
        self.assertIsToken(tokens[4], 'scalar', '-0.1')

    def indentation(self):
        source = '  foo\n    bar'
        tokens = self.get_tokens(source)
        self.assertIsToken(tokens[0], 'indentation', '   ')
        self.assertIsToken(tokens[1], 'scalar', 'foo')
        self.assertIsToken(tokens[-2], 'indentation', '    ')
        self.assertIsToken(tokens[-1], 'scalar', 'bar')

    def test_sequences(self):
        source = '[foo, bar, baz]'
        tokens = self.get_tokens(source)
        self.assertIsToken(tokens[0], 'open_sequence', '[')
        self.assertIsToken(tokens[1], 'scalar', 'foo')
        self.assertIsToken(tokens[2], 'comma', ',')
        self.assertIsToken(tokens[3], 'scalar', 'bar')
        self.assertIsToken(tokens[4], 'comma', ',')
        self.assertIsToken(tokens[5], 'scalar', 'baz')
        self.assertIsToken(tokens[6], 'close_sequence', ']')

    def test_anchors_and_alias(self):
        source = '&foo\n*foo'
        tokens = tokenizer(source)
        self.assertIsToken(next(tokens), 'anchor', '&foo')
        self.assertIsToken(next(tokens), 'newline', '\n')
        self.assertIsToken(next(tokens), 'alias', '*foo')
        
    def test_literal(self):
        source = '\n'.join(['foo: |-', '  \//||\/||', '  // ||  ||__'])
        tokens = tokenizer(source)
        self.assertIsToken(next(tokens), 'scalar', 'foo')
        self.assertIsToken(next(tokens), 'colon', ':')
        self.assertIsToken(next(tokens), 'literal', '|-')
        self.assertIsToken(next(tokens), 'newline', '\n')
        self.assertIsToken(next(tokens), 'indentation', '  ')
        self.assertIsToken(next(tokens), 'scalar', '\//||\/||')
        self.assertIsToken(next(tokens), 'newline', '\n')
        self.assertIsToken(next(tokens), 'indentation', '  ')
        self.assertIsToken(next(tokens), 'scalar', '// ||  ||__')
        
    def test_line_number(self):
        source = '\n'.join(
            ['one: foo',
            'two: bar',
            'three: foobar']
        )
        tokens = list(tokenizer(source))
        self.assertIsToken(tokens[5], 'colon', line=1, column=3)
        self.assertIsToken(tokens[10], 'scalar', 'foobar', line=2, column=7)

class ParserTest(TestCase):

    def parse(self):
        return Parser().from_file('tests/simple.example.yaml')

    def from_string(self, source):
        return Parser().parse(source)

    def test_mapping(self):
        source = '\n'.join((
            'name: Max Mustermann',
            'age: 33'
        ))
        result = self.from_string(source)
        self.assertDictEqual(
            result,
            dict(name='Max Mustermann', age='33')
        )
