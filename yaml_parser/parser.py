
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
        self.indentation = -1
        return self.stream()

    def advance(self):
        self.current, self.next = self.next, next(self.tokenizer, None)

    def stream(self):
        '''
        l-yaml-stream ::= l-document-prefix* l-any-document?
                        ( l-document-suffix+ l-document-prefix* l-any-document?
                        | l-document-prefix* l-explicit-document? )*        
        '''
        # if not self.current:
        #     self.advance()
        # return self.any_document()
        pass

    def any_document(self):
        '''
        l-any-document ::=   l-directive-document
                   | l-explicit-document
                   | l-bare-document
        '''
        return self.bare_document() # TODO: directive-document and explicit-document

    def bare_document(self):
        '''
        l-bare-document ::= s-l+block-node(-1,block-in)
        '''
        return self.block_node(-1, 'block-in')

    def block_node(self, n, c):
        '''
        s-l+block-in-block(n,c) | s-l+flow-in-block(n)
        '''
        return self.block_in_block(n, c) | self.flow_in_block(n) 

    def block_in_block(self, n, c):
        '''
        s-l+block-in-block(n,c) ::= s-l+block-scalar(n,c) | s-l+block-collection(n,c)
        '''
        return self.block_collection(n, c) # TODO: block-scalar

    def block_collection(self, n, c):
        '''
        s-l+block-collection(n,c) ::= ( s-separate(n+1,c) c-ns-properties(n+1,c) )?
                              s-l-comments
                              ( l+block-sequence(seq-spaces(n,c))
                              | l+block-mapping(n) )
        '''
        return self.block_mapping(n) # TODO: block-sequence, comments, properties, separate

    def block_mapping(self, n):
        '''
        l+block-mapping(n) ::= ( s-indent(n+m) ns-l-block-map-entry(n+m) )+
                       /* For some fixed auto-detected m > 0 */
        '''
        mapping = {}
        while n <= self.indentation:
            self.indent()
            entry = self.block_map_entry(self.indentation)            
            mapping.update(entry)
        return mapping

    def indent(self):
        if self.current.type == 'indentation':
            self.indentation = len(self.current.value)
            self.advance()

    def block_map_entry(self, n):
        '''
        ns-l-block-map-entry(n) ::=   c-l-block-map-explicit-entry(n)
                            | ns-l-block-map-implicit-entry(n)
        '''
        return self.block_map_implicit_entry(n) # TODO: block-map-explicit-entry
        
    def block_map_implicit_entry(self, n):
        '''
        ns-l-block-map-implicit-entry(n) ::= ( ns-s-block-map-implicit-key
                                     | e-node )
                                     c-l-block-map-implicit-value(n)
        '''
        key = self.block_map_implicit_key() # TODO: e-node
        value = self.block_map_implicit_value(n)
        return {key: value} # TODO: e-node

    def block_map_implicit_key(self):
        '''
        ns-s-block-map-implicit-key ::=   c-s-implicit-json-key(block-key)
                                | ns-s-implicit-yaml-key(block-key)
        '''
        return self.implicit_yaml_key('block-key') # TODO: implicit-json-key

    def implicit_yaml_key(self, c):
        '''
        ns-s-implicit-yaml-key(c) ::= ns-flow-yaml-node(n/a,c) s-separate-in-line?
                              /* At most 1024 characters altogether */
        '''
        pass

    def block_map_implicit_value(self, n):
        '''
        c-l-block-map-implicit-value(n) ::= “:” ( s-l+block-node(n,block-out)
                                        | ( e-node s-l-comments ) )
        '''
        if self.current.type == 'colon':
            self.advance()
            return self.block_node(n, 'block-out') # TODO: e-node, comments

    def flow_in_block(self, n):
        '''
        s-l+flow-in-block(n) ::= s-separate(n+1,flow-out)
                         ns-flow-node(n+1,flow-out) s-l-comments
        '''
        # self.separate(n+1, 'flow-out') # TODO: separate
        return self.flow_node(n+1, 'flow-out') # TODO: comments

    def separate(self, n, c):
        '''
        s-separate(n,c) ::= c = block-out ⇒ s-separate-lines(n)
                    c = block-in  ⇒ s-separate-lines(n)
                    c = flow-out  ⇒ s-separate-lines(n)
                    c = flow-in   ⇒ s-separate-lines(n)
                    c = block-key ⇒ s-separate-in-line
                    c = flow-key  ⇒ s-separate-in-line
        '''
        if c in ['block-out', 'block-in', 'flow-out', 'flow-in']:
            return self.separate_lines(n)
        elif c in ['block-key', 'flow-key']:
            return self.separate_in_line()

    def separate_lines(self, n):
        '''
        s-separate-lines(n) ::=   ( s-l-comments s-flow-line-prefix(n) )
                        | s-separate-in-line
        '''
        return self.separate_in_line() # TODO: comments flow-line-prefix

    def separate_in_line(self):
        '''
        s-separate-in-line ::= s-white+ | /* Start of line */
        '''
        pass # TODO: separate-in-line

    def flow_node(self, n, c):
        '''
        ns-flow-node(n,c) ::=   c-ns-alias-node
                      | ns-flow-content(n,c)
                      | ( c-ns-properties(n,c)
                          ( ( s-separate(n,c)
                              ns-flow-content(n,c) )
                            | e-scalar ) )
        '''
        return self.flow_content(n, c) # TODO: 