
from colorama import Fore, Back, init, deinit
from yaml_parser.tokenizer import file_tokenizer

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

def prettyprint(filename, encoding='utf8'):
    init()
    try:
        for token in file_tokenizer(filename):
            print_token(token)
        print()
    finally:
        deinit()
