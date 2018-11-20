
import re
import collections
from colorama import Fore, Back, init, deinit

Token = collections.namedtuple(
    'Token', ['type', 'value', 'line', 'lineno', 'start', 'end'])

patterns = [
    r'(?P<whitespace>[ \t]+)',
    r'(?P<newline>[\r\n])',
    r'(?P<directive>---)',
    r'(?P<tag>!.*)',
    r'(?P<mapping_value>(:(?=\s))|(:$))',
    r'(?P<sequence_entry>(-(?=\s))|(-$))',
    r'(?P<anchor>&\S*)',
    r'(?P<alias>\*\S*)',
    r'(?P<literal>\|[+-]?)',
    r'(?P<sequence_start>\[)',
    r'(?P<sequence_end>\])',
    r'(?P<comma>,)',
]

indicators = re.escape('-?:,[]{}#&*!|>"%@`' + "'")
inside_forbidden = re.escape('[]{},')

def plain_scalar(head_forbidden='', tail_forbidden=''):
    head = r'[^{0}]|[:&-](?=\S)'.format(head_forbidden)
    tail = r'([^:#{0}]|[:#](?=\S))*[^\s:#{0}]'.format(tail_forbidden)
    pattern = r'(?P<plain_scalar>({0})({1})?)'.format(head, tail)
    return pattern

# Different patterns for plain scalars, depending whether they are inside or outside of a flow collection
plain_scalar_outside = plain_scalar(head_forbidden=indicators, tail_forbidden='')
plain_scalar_inside = plain_scalar(head_forbidden=indicators, tail_forbidden=inside_forbidden)

def _any(*patterns):
    return '|'.join(patterns)

outside_pattern = re.compile(_any(*patterns, plain_scalar_outside))
inside_pattern = re.compile(_any(*patterns, plain_scalar_inside))

def tokenizer(readline):
    # Readline is a callable that returns a single line of text, terminated with a \n character
    lineno = 0
    pattern = outside_pattern

    while True:
        try:
            line = readline()
        except StopIteration:
            line = '' # Make looping using file.readline consistent with looping using string.splitlines
        if not line:
            break
        lineno += 1
        indentation = 0
        pos, max = 0, len(line)

        while pos < max:  # measure indentation
            if line[pos] == ' ':
                indentation += 1
            else:
                break
            pos += 1
        yield Token(type='indentation', value=' '*indentation, line=line, lineno=lineno, start=0, end=pos)

        while pos < max:
            m = pattern.match(line, pos)
            if m:
                pos = m.end()
                type = m.lastgroup
                if type == 'whitespace': # skip whitespace
                    continue
                if type == 'sequence_start': # switch patterns
                    pattern = inside_pattern
                if type == 'sequence_end':
                    pattern = outside_pattern
                yield Token(type=type, value=m.group(type), line=line, lineno=lineno, start=m.start(), end=m.end())
            else:
                yield Token(type='UNKNOWN', value=line[pos], line=line, lineno=lineno, start=pos, end=pos)
                pos += 1

def file_tokenizer(filename):
    with open(filename, 'r', encoding='utf8') as f:
        for token in tokenizer(f.readline):
            yield token


def string_tokenizer(source):
    def generator(source):
        for line in source.splitlines(keepends=True): # keepends to make string.splitlines consistent with file.readline
            yield line
    for token in tokenizer(generator(source).__next__):
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
