
import re, collections
from colorama import Fore, Back, init, deinit

PATTERNS = [
    # Collections
    r'(?P<indentation>(^ +))',
    r'(?P<newline>[\r\n])',
    r'(?P<comment># .*)',
    r'(?P<dash>(\-(?=\s)))',
    r'(?P<colon>(\:(?=\s)))',
    r'(?P<open_sequence>\[)',
    r'(?P<close_sequence>\])',
    r'(?P<open_mapping>\{)',
    r'(?P<close_mapping>\})',
    r'(?P<comma>,(?=.*\]))',
    # Structures
    r'(?P<directive>^---)',
    r'(?P<end_of_document>^\.\.\.)',
    r'(?P<anchor>&\w*)',
    r'(?P<alias>\*\w*)',
    r'(?P<complex_mapping_key>^\? )',
    # Scalars
    r'(?P<literal>\|[-+]?$)',
    r'(?P<folded>\>$)',
    r'(?P<scalar>[^,:&*#!\s]([^:,\n\r\]\[]|:(?=\S)|,(?=\S))*)',
    # Tags
    r'(?P<tag>!.+)',
]

MASTER_PATTERN = re.compile('|'.join(PATTERNS), re.MULTILINE)

Token = collections.namedtuple('Token', ['type', 'value', 'line', 'column'])

def tokenizer(source, pattern=MASTER_PATTERN):
    line = 1
    linestart = 0
    for m in pattern.finditer(source):
        kind = m.lastgroup
        value = m.group()
        column = m.start() - linestart + 1
        token = Token(kind, value, line, column)
        if token.type == 'newline':
            line += 1
            linestart = m.end()
        yield token

def prettyprint(filename, encoding='utf8'):
    with open(filename, 'r', encoding=encoding) as f:
        source = f.read()
    init()
    try:
        for token in tokenizer(source):
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
