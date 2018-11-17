from unittest import TestCase

from yaml_parser.tokenizer import string_tokenizer, file_tokenizer
from yaml_parser.parser import Parser

class ParserTest(TestCase):

    def from_string(self, source):
        return Parser().from_string(source)

    def test_example_file(self):
        filename = 'tests/simple.example.yaml'
        result = Parser().from_file(filename)
        self.assertEqual(
            result['teams'][0]['league'], 'Champions League'
        )

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
