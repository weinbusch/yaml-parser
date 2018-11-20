
import re
import collections

Token = collections.namedtuple(
    'Token', ['type', 'value', 'line', 'lineno', 'start', 'end'])

def _any(*patterns):
    # Helper function for joining patters
    return '|'.join(patterns)

indicators = re.escape('-?:,[]{}#&*!|>"%@`' + "'")

inside_forbidden = re.escape('[]{},') # Plain scalars inside flow collections must not contain these

patterns = [ # General patterns
    r'(?P<whitespace>[ \t]+)',
    r'(?P<newline>[\r\n])',
    r'(?P<directive>---)',
    r'(?P<tag>!.*)',
    r'(?P<mapping_value>:(?=\s))',
    r'(?P<sequence_entry>-(?=\s))',
    r'(?P<anchor>&\S*)',
    r'(?P<alias>\*\S*)',
    r'(?P<literal>\|[+-]?)',
    r'(?P<sequence_start>\[)',
    r'(?P<sequence_end>\])',
    r'(?P<comma>,)',
]

def plain_scalar(head_forbidden='', tail_forbidden=''):
    # Callable for construction a plain scalar pattern
    head = r'[^{0}]|[:&-](?=\S)'.format(head_forbidden)
    tail = r'([^:#{0}]|[:#](?=\S))*[^\s:#{0}]'.format(tail_forbidden)
    pattern = r'(?P<plain_scalar>({0})({1})?)'.format(head, tail)
    return pattern

# Different patterns for plain scalars, depending whether they are inside or outside of a flow collection
plain_scalar_outside = plain_scalar(head_forbidden=indicators, tail_forbidden='')
plain_scalar_inside = plain_scalar(head_forbidden=indicators, tail_forbidden=inside_forbidden)

outside_pattern = re.compile(_any(*patterns, plain_scalar_outside))
inside_pattern = re.compile(_any(*patterns, plain_scalar_inside))

def tokenizer(readline):
    '''
    Token generator

    The tokenize() generator requires one argument, readline, which
    must be a callable object which provides the same interface as the
    readline() method of built-in file objects.  Each call to the function
    should return one line of input as bytes.  Alternatively, readline
    can be a callable function terminating with StopIteration:
        readline = open(myfile, 'rb').__next__  # Example of alternate readline
    '''

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
    '''
    Tokenize file
    '''
    with open(filename, 'r', encoding='utf8') as f:
        for token in tokenizer(f.readline):
            yield token

def string_tokenizer(source):
    '''
    Tokenize string
    '''
    def generator(source):
        for line in source.splitlines(keepends=True): # keepends to make string.splitlines consistent with file.readline
            yield line
    for token in tokenizer(generator(source).__next__):
        yield token
