
from .tokenizer import tokenizer

''' YAML grammar

stream ::= document
document ::= block_content
block_content ::= block_sequence | block_mapping | scalar
block_sequence ::= BLOCK_START (DASH block_node)* BLOCK_END
block_mapping ::= BLOCK_START (block_node ": " block_node)* BLOCK_END
'''

class Parser(object):

    def from_file(self, filename, encoding='utf8'):
        with open(filename, 'r', encoding=encoding) as f:
            source = f.read()
        return self.parse(source)

    def parse(self, source):
        self.tokenizer = tokenizer(source)
        self.current = None
        self.next = None
        self.advance()
        self.indentation = 0
        return self.stream()

    def advance(self):
        self.current, self.next = self.next, next(self.tokenizer, None)

    def stream(self):
        if not self.current:
            self.advance()
        return self.document()

    def document(self):
        return self.block_content()

    def block_content(self):
        '''
        block_content :== block_mapping | block_sequence | scalar
        '''

        # First check indentation; 
        # this skips over a single newline and a single indentation token
        self.check_indentation()

        # Continue with analysing the current token
        # it can be a mapping
        if self.next and self.next.type == 'colon':
            return self.block_mapping()
        # or a sequence
        if self.current.type == 'dash':
            return self.block_sequence()
        # or a scalar
        if self.current.type == 'scalar':
            return self.scalar()
        
        raise Exception('Could not parse block content at {}'.format(self.current))

    def check_indentation(self):
        # If a newline is encountered, 
        if self.current.type == 'newline':
            # advance to next token.
            self.advance()
            # If this token is an indentation
            if self.current.type == 'indentation':
                # Assign self.indentation 
                self.indentation = len(self.current.value)
                # Advance to next token
                self.advance()
            else:
                # If newline is followed by something else, 
                # self.indentation is 0
                self.indentation = 0
                # Continue with the current token

    def scalar(self):
        '''
        Return scalar value
        '''
        value = self.current.value
        self.advance()
        return value

    def block_sequence(self):
        '''
        block_sequence :== BLOCK_START ("- " block_content)* BLOCK_END
        '''
        sequence = []
        block_level = self.indentation
        while self.current:
            self.check_indentation()
            if self.block_end(block_level):
                break
            # We should be looking at a dash
            if not self.current.type == 'dash':
                raise Exception('Malformed token at {}. Expected "dash"'.format(self.current))
            self.advance()
            value = self.block_content()
            sequence.append(value)
        return sequence

    def block_mapping(self):
        '''
        block_mapping:== BLOCK_START (scalar ": " block_content)* BLOCK_END
        '''
        mapping = {}
        block_level = self.indentation
        while self.current:
            # Update indentation, also skips a single newline and a single indentations
            self.check_indentation()
            if self.block_end(block_level) or not self.next:
                break
            if not self.next.type == 'colon' or not self.current.type=='scalar':
                raise Exception(
                    'Malformed mapping key at {}'.format(self.current)
                )
            key = self.scalar()
            # Implicitly advances to the next token, which is the colon
            # Advance to the next token, which is the value
            self.advance()
            mapping[key] = self.block_content()
        return mapping

    def block_end(self, level=0):
        # If current indentation is < block_level, we have reached the end of the current block
        return self.indentation < level
