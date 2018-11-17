
import re, collections
from colorama import Fore, Back, init, deinit

INDICATOR_CHARACTERS = "-?:,[]{}#&*!|>'%@`" + '"'
INSIDE_FORBIDDEN = ":,[]{}#"

'''
Plain scalars must never contain the “: ” and “ #” character combinations. 
Such combinations would cause ambiguity with mapping key: value pairs and comments. 
In addition, inside flow collections, or when used as implicit keys, plain scalars 
must not contain the “[”, “]”, “{”, “}” and “,” characters. These characters would 
cause ambiguity with flow collection structures. 
'''

PATTERNS = [
    # Whitespace
    r'(?P<indentation>(^[ \t]+))',
    r'(?P<newline>[\r\n])',
    r'(?P<empty_line>^[ \t]*[\n\r])',
    # Comments
    r'(?P<comment>#(?<=\s)[^\n\r]*)',
    # Block indicators
    r'(?P<colon>(:(?=\s)))',
    r'(?P<dash>(-(?=\s)))',
    r'(?P<complex_mapping_key>\?)',
    r'(?P<literal>\|[-+]?)',
    r'(?P<folded>\>)',
    # Flow indicators
    r'(?P<open_sequence>\[)',
    r'(?P<close_sequence>\])',
    r'(?P<open_mapping>\{)',
    r'(?P<close_mapping>\})',
    r'(?P<comma>,[ \t]*)',
    # Directives
    r'(?P<directive>---)',
    r'(?P<end_of_document>\.\.\.)',
    # Anchor and alias
    r'(?P<anchor>&\w*)',
    r'(?P<alias>\*\w*)',
    # Scalars
    r'(?P<scalar>([^{indicator_characters}\s]|[-?:](?=\S))([^{inside_forbidden}\n\r]|#(?<![ ])|[:](?=\S))*)'.format(
        indicator_characters = re.escape(INDICATOR_CHARACTERS),
        inside_forbidden = re.escape(INSIDE_FORBIDDEN)
    ),
    # Tags
    r'(?P<tag>!.+)',
]

MASTER_PATTERN = re.compile('|'.join(PATTERNS))

Token = collections.namedtuple('Token', ['type', 'value', 'line', 'column'])

def file_tokenizer(filename, pattern=MASTER_PATTERN):
    with open(filename, 'r', encoding='utf8') as f:
        lineno = 1
        for line in f:
            for token in line_tokenizer(line, lineno, pattern):
                yield token
            lineno += 1

def string_tokenizer(source, pattern=MASTER_PATTERN):
    lineno = 1
    for line in source.splitlines(keepends=True):
        for token in line_tokenizer(line, lineno, pattern):
            yield token
        lineno +=1

def line_tokenizer(line, lineno, pattern=MASTER_PATTERN):
    for m in pattern.finditer(line):
        kind = m.lastgroup
        value = m.group()
        column = m.start() + 1
        token = Token(kind, value, lineno, column)
        yield token

def prettyprint(filename, encoding='utf8'):
    init()
    try:
        for token in file_tokenizer(filename):
            print_token(token)
        print()
    finally:
        deinit()

TOKEN_STYLES = {
    'indentation': Back.CYAN,
    'newline': Back.CYAN,
    'comment': Back.LIGHTBLUE_EX,
    'dash': Back.RED,
    'colon': Back.RED,
    'open_sequence': Back.YELLOW + Fore.BLUE,
    'close_sequence': Back.YELLOW + Fore.BLUE,
    'open_mapping': Back.YELLOW + Fore.BLUE,
    'close_mapping': Back.YELLOW + Fore.BLUE,
    'comma': Back.YELLOW + Fore.BLUE,
    # Structures
    'directive': Back.RED,
    'end_of_document': Back.RED,
    'anchor': Back.BLUE,
    'alias': Back.BLUE,
    'complex_mapping_key': Back.RED,
    # Scalars
    'literal': Back.MAGENTA,
    'folded': Back.MAGENTA,
    'scalar': Back.GREEN,
    # Tags
    'tag': Back.LIGHTRED_EX + Fore.CYAN,
}

def print_token(token):
    prefix = TOKEN_STYLES.get(token.type, '')
    prefix += '\\n' if token.type == 'newline' else ''
    suffix = Back.RESET + Fore.RESET
    suffix += '' if token.value.endswith('\n') else ' '
    print(prefix + token.value + suffix, end='')

if __name__ == '__main__':
    import sys
    filename = sys.argv[1]
    for token in file_tokenizer(filename):
        print(token)
