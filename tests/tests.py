from unittest import TestCase

from yaml_parser.tokenizer import tokenizer

class TokenizerTest(TestCase):

    def assertIsToken(self, token, type, value=None, line=None, column=None):
        self.assertEqual(token.type, type)
        if value:
            self.assertEqual(token.value, value)
        if line:
            self.assertEqual(token.line, line)
        if column:
            self.assertEqual(token.column, column)

    def test_colon(self):
        source = 'tie-fighter: |\-*-/|'
        tokens = list(tokenizer(source))
        self.assertIsToken(tokens[0], 'scalar', 'tie-fighter')
        self.assertIsToken(tokens[1], 'colon', ': ')
        self.assertIsToken(tokens[2], 'scalar', '|\-*-/|')

    def test_dash(self):
        source = '\n'.join(['- 1.2', '- -5.4'])
        tokens = tokenizer(source)
        self.assertIsToken(next(tokens), 'dash', '- ')
        self.assertIsToken(next(tokens), 'scalar', '1.2')
        self.assertIsToken(next(tokens), 'newline', '\n')
        self.assertIsToken(next(tokens), 'dash', '- ')
        self.assertIsToken(next(tokens), 'scalar', '-5.4')

    def test_scalars(self):
        source = '\n'.join(['foo', 'http://www.foo.bar', '-0.1'])
        tokens = list(tokenizer(source))
        self.assertIsToken(tokens[0], 'scalar', 'foo')
        self.assertIsToken(tokens[1], 'newline', '\n')
        self.assertIsToken(tokens[2], 'scalar', 'http://www.foo.bar')
        self.assertIsToken(tokens[3], 'newline', '\n')
        self.assertIsToken(tokens[4], 'scalar', '-0.1')

    def indentation(self):
        source = '  foo'
        tokens = list(tokenizer(source))
        self.assertIsToken(tokens[0], 'indentation', '   ')
        self.assertIsToken(tokens[1], 'scalar', 'foo')

    def test_sequences(self):
        tokens = list(tokenizer('[foo, bar, baz]'))
        self.assertEqual(len(tokens), 7)
        self.assertListEqual(
            ['open_sequence', 'scalar', 'comma', 'scalar', 'comma', 'scalar', 'close_sequence'],
            [token.type for token in tokens]
        )

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
        self.assertIsToken(next(tokens), 'colon', ': ')
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
