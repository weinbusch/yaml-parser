from unittest import TestCase

from yaml_parser.tokenizer import string_tokenizer, file_tokenizer
from yaml_parser.parser import Parser

class TokenizerTest(TestCase):

    def assertIsToken(self, token, **kwargs):
        for key, value in kwargs.items():
            self.assertEqual(getattr(token, key), value)

    def get_tokens(self, source):
        return list(string_tokenizer(source))

    def test_mappings(self):
        source = (
            'foo  :    bar\n'
            'baz:\n'
            '    foobar'
        )
        tokens = self.get_tokens(source)
        self.assertIsToken(tokens[0], type='indentation', value='')
        self.assertIsToken(tokens[1], type='plain_scalar', value='foo')
        self.assertIsToken(tokens[2], type='mapping_value', value=':')
        self.assertIsToken(tokens[3], type='plain_scalar', value='bar')
        self.assertIsToken(tokens[4], type='newline', value='\n')
        self.assertIsToken(tokens[5], type='indentation', value='')
        self.assertIsToken(tokens[6], type='plain_scalar', value='baz')
        self.assertIsToken(tokens[7], type='mapping_value', value=':')
        self.assertIsToken(tokens[8], type='newline', value='\n')
        self.assertIsToken(tokens[9], type='indentation', value='    ')
        self.assertIsToken(tokens[10], type='plain_scalar', value='foobar')

    def test_sequences(self):
        source = (
            '- foo\n'
            '-    bar\n'
            '   - baz\n'
            '- \n' 
            '  baz\n'
        )
        tokens = self.get_tokens(source)
        self.assertIsToken(tokens[0], type='indentation', value='')
        self.assertIsToken(tokens[1], type='sequence_entry', value='-')
        self.assertIsToken(tokens[2], type='plain_scalar', value='foo')
        self.assertIsToken(tokens[3], type='newline')
        self.assertIsToken(tokens[4], type='indentation', value='')
        self.assertIsToken(tokens[5], type='sequence_entry', value='-')
        self.assertIsToken(tokens[6], type='plain_scalar', value='bar')
        self.assertIsToken(tokens[7], type='newline')
        self.assertIsToken(tokens[8], type='indentation', value='   ')
        self.assertIsToken(tokens[9], type='sequence_entry', value='-')
        self.assertIsToken(tokens[10], type='plain_scalar', value='baz')
        self.assertIsToken(tokens[11], type='newline')
        self.assertIsToken(tokens[12], type='indentation', value='')
        self.assertIsToken(tokens[13], type='sequence_entry', value='-')
        self.assertIsToken(tokens[14], type='newline')
        self.assertIsToken(tokens[15], type='indentation', value='  ')
        self.assertIsToken(tokens[16], type='plain_scalar', value='baz')
        self.assertIsToken(tokens[17], type='newline')

    def test_flow_sequences(self):
        source = '[foo, bar, baz]'
        tokens = self.get_tokens(source)
        self.assertIsToken(tokens[0], type='indentation')
        self.assertIsToken(tokens[1], type='sequence_start', value='[')
        self.assertIsToken(tokens[2], type='plain_scalar', value='foo')
        self.assertIsToken(tokens[3], type='comma', value=',')
        self.assertIsToken(tokens[-2], type='plain_scalar', value='baz')
        self.assertIsToken(tokens[-1], type='sequence_end', value=']')

class ParserTest(TestCase):

    def from_string(self, source):
        return Parser().from_string(source)

    def test_example_file(self):
        filename = 'tests/simple.example.yaml'
        result = Parser().from_file(filename)
        self.assertEqual(
            result['teams'][0]['league'], 'Champions League'
        )

    def test_invoice_example_file(self):
        filename = 'tests/invoice.example.yaml'
        result = Parser().from_file(filename)
        self.assertEqual(result['invoice'], '34843')

    # TODO: Flow scalars

    # Plain scalars

    def test_block_list_of_plain_scalars(self):
        source = '\n'.join((
            '- ::vector',
            '- Up, up, and away!',
            '- -123',
            '- http://example.com/foo#bar',
        ))
        result = self.from_string(source)
        self.assertListEqual(
            result,
            ['::vector', 'Up, up, and away!', '-123', 'http://example.com/foo#bar']
        )

    # Block styles

    def test_mapping(self):
        source = '\n'.join([
            'name: Max Mustermann',
            'age: 33'
        ])
        result = self.from_string(source)
        self.assertDictEqual(
            result,
            dict(name='Max Mustermann', age='33')
        )

    def test_implicit_keys(self):
        source = (
            'key with whitespace : value with whitespace'
        )
        result = self.from_string(source)
        self.assertDictEqual(result, {'key with whitespace': 'value with whitespace'})

    def test_sequence(self):
        source = '\n'.join([
            '- London',
            '- Paris',
            '- Bochum',
        ])
        result = self.from_string(source)
        self.assertListEqual(
            result, ['London', 'Paris', 'Bochum']
        )

    def test_mapping_nested_in_mapping(self):
        source = '\n'.join([
            'name: Max Mustermann',
            'address:',
            '  street: Musterstraße',
            '  city: Neustadt',
            'age: 33'
        ])
        result = self.from_string(source)
        self.assertDictEqual(
            result,
            dict(name='Max Mustermann', address=dict(street='Musterstraße', city='Neustadt'), age='33')
        )

    def test_list_nested_in_mapping(self):
        source = '\n'.join([
            'name: Max Mustermann',
            'friends:',
            '  - Fritz',
            '  - Moritz',
            'age: 33'
        ])
        result = self.from_string(source)
        self.assertDictEqual(
            result,
            dict(name='Max Mustermann', friends=['Fritz', 'Moritz'], age='33')
        )

    def test_list_nested_in_list(self):
        source = '\n'.join([
            '- Max',
            '-',
            '  - Fritz',
            '  - Moritz',
            '- Franz'
        ])
        result = self.from_string(source)
        self.assertListEqual(
            result,
            ['Max', ['Fritz', 'Moritz'], 'Franz']
        )

    def test_mapping_nested_in_list(self):
        source = '\n'.join([
            '- Max Mustermann',
            '-',
            '  street: Musterstraße',
            '  city: Neustadt',
            '- 33'
        ])
        result = self.from_string(source)
        self.assertListEqual(
            result,
            ['Max Mustermann', dict(street='Musterstraße', city='Neustadt'), '33']
        )

    # Anchors

    def test_anchors_and_alias(self):
        source = (
            'primary: &foo\n'
            '   - first\n'
            '   - second\n'
            'secondary: *foo\n'
        )
        result = self.from_string(source)
        self.assertListEqual(result['primary'], result['secondary'])

    # Documents

    def test_explicit_document(self):
        source = '\n'.join([
            '---',
            '- London',
            '- Paris',
            '- Bochum',
        ])
        result = self.from_string(source)
        self.assertListEqual(
            result, ['London', 'Paris', 'Bochum']
        )

    def test_ignore_tag(self):
        source = '\n'.join([
            '--- !<http://foo.bar>',
            '- London',
            '- Paris',
            '- Bochum',
        ])
        result = self.from_string(source)
        self.assertListEqual(
            result, ['London', 'Paris', 'Bochum']
        )
