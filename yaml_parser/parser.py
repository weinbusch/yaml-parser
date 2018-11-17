
from .tokenizer import file_tokenizer, string_tokenizer

'''
Recursive descent parser based on YAML grammar according to 
    	http://yaml.org/spec/1.2/spec.html#Syntax
'''

class Parser(object):

    def from_file(self, filename, encoding='utf8'):
        self.tokenizer = file_tokenizer(filename)
        return self.parse()

    def from_string(self, source):
        self.tokenizer = string_tokenizer(source)
        return self.parse()

    def parse(self):
        self.current = None
        self.next = next(self.tokenizer)
        self.advance()
        self.indentation = -1
        try:
            return self.stream()
        except:
            raise Exception('Parser failed at {}.\nNext token is: {}.'.format(self.current, self.next))

    def advance(self):
        self.current, self.next = self.next, next(self.tokenizer, None)
        # skip some tokens:
        while self.current and self.current.type in ['tag']:
            self.advance()

    def consume_and_advance(self):
        output = self.current.value
        self.advance()
        return output

    def join_tokens(self, types=[]):
        output = []
        while self.current and self.current.type in types:
            output.append(self.current.value)
            self.advance()
        return ''.join(output)

    def stream(self):
        '''
        l-yaml-stream ::= l-document-prefix* l-any-document?
                        ( l-document-suffix+ l-document-prefix* l-any-document?
                        | l-document-prefix* l-explicit-document? )*        
        '''
        return self.any_document()

    def any_document(self):
        '''
        l-any-document ::=   l-directive-document
                   | l-explicit-document
                   | l-bare-document
        '''
        return self.explicit_document() or self.bare_document() # TODO: directive-document

    def bare_document(self):
        '''
        l-bare-document ::= s-l+block-node(-1,block-in)
        '''
        return self.block_node(-1, 'block-in')

    def explicit_document(self):
        '''
        l-explicit-document 	::= 	c-directives-end
                                        ( l-bare-document
                                        | ( e-node s-l-comments ) ) 
        c-directives-end 	::= 	“-” “-” “-”
        '''
        if self.current.value != '---':
            return
        self.advance()
        return self.bare_document() # TODO: e-node, comments

    def block_node(self, n, c):
        '''
        s-l+block-in-block(n,c) | s-l+flow-in-block(n)
        '''
        return self.block_in_block(n, c) or self.flow_in_block(n) 

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
        s-separate(n,c) 	::= 	c = block-out ⇒ s-separate-lines(n)
                                    c = block-in  ⇒ s-separate-lines(n)
                                    c = flow-out  ⇒ s-separate-lines(n)
                                    c = flow-in   ⇒ s-separate-lines(n)
                                    c = block-key ⇒ s-separate-in-line
                                    c = flow-key  ⇒ s-separate-in-line
        s-separate-lines(n) 	::= 	  ( s-l-comments s-flow-line-prefix(n) )
                                          | s-separate-in-line
        s-separate-in-line 	::= 	s-white+ | /* Start of line */ 
        s-l-comments 	::= 	( s-b-comment | /* Start of line */ )
                                l-comment* 
        s-flow-line-prefix(n) 	::= 	s-indent(n) s-separate-in-line?
        '''
        self.indent()
        return self.block_mapping(n) or self.block_sequence(n) # TODO: comments, properties, separate

    def block_mapping(self, n):
        '''
        l+block-mapping(n) ::= ( s-indent(n+m) ns-l-block-map-entry(n+m) )+
                       /* For some fixed auto-detected m > 0 */
        '''
        # We should be either looking at an explicit mapping, i.e. a '?' token
        # or at an implicit mapping key, i.e. a 'scalar' followed by a 'colon' token. 
        # If not, return.
        if self.current.type != 'complex_mapping_key' and (self.next == None or self.next.type != 'colon'):
            return
        mapping = {}
        n_plus_m = self.indentation
        while self.current:
            self.indent()
            if self.indentation < n_plus_m:
                break
            entry = self.block_map_entry(n_plus_m)            
            mapping.update(entry)
        return mapping

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
        ns-s-implicit-yaml-key(c) ::= ns-flow-yaml-node(n/a,c) s-separate-in-line?
                              /* At most 1024 characters altogether */
        ns-flow-yaml-node(n,c) 	::= 	c-ns-alias-node
                                        | ns-flow-yaml-content(n,c)
                                        | ( c-ns-properties(n,c)
                                            ( ( s-separate(n,c)
                                                ns-flow-yaml-content(n,c) )
                                            | e-scalar ) ) 
        '''
        return self.flow_content(1024, 'block-key')

    def block_map_implicit_value(self, n):
        '''
        c-l-block-map-implicit-value(n) ::= “:” ( s-l+block-node(n,block-out)
                                        | ( e-node s-l-comments ) )
        '''
        if not self.current.type == 'colon':
            raise Exception('Expected a "colon", found a {}'.format(self.current))
        self.advance()
        return self.block_node(n, 'block-out') # TODO: e-node, comments

    def block_sequence(self, n):
        '''
        l+block-sequence(n) 	::= 	( s-indent(n+m) c-l-block-seq-entry(n+m) )+
                                        /* For some fixed auto-detected m > 0 */ 
        '''
        # We expect looking at a dash
        if self.current.type != 'dash':
            return 
        sequence = []
        n_plus_m = self.indentation
        while self.current:
            self.indent()
            if self.indentation < n_plus_m:
                break
            entry = self.block_seq_entry(self.indentation)            
            sequence.append(entry)
        return sequence

    def block_seq_entry(self, n):
        '''
        c-l-block-seq-entry(n) 	::= 	“-” /* Not followed by an ns-char */
                                        s-l+block-indented(n,block-in)
        s-l+block-indented(n,c) 	::= 	  ( s-indent(m)
                                            ( ns-l-compact-sequence(n+1+m)
                                            | ns-l-compact-mapping(n+1+m) ) )
                                            | s-l+block-node(n,c)
                                            | ( e-node s-l-comments )
        '''
        if not self.current.type == 'dash':
            raise Exception('Expected a "dash", found a {}'.format(self.current))
        self.advance()
        self.indent()
        return self.block_node(n, 'block-in') # TODO: compact-sequence, compact-mapping, e-node, comments

    def flow_in_block(self, n):
        '''
        s-l+flow-in-block(n) ::= s-separate(n+1,flow-out)
                         ns-flow-node(n+1,flow-out) s-l-comments
        '''
        return self.flow_node(n+1, 'flow-out') # TODO: comments, separate

    def flow_node(self, n, c):
        '''
        ns-flow-node(n,c) ::=   c-ns-alias-node
                      | ns-flow-content(n,c)
                      | ( c-ns-properties(n,c)
                          ( ( s-separate(n,c)
                              ns-flow-content(n,c) )
                            | e-scalar ) )
        '''
        return self.flow_content(n, c) # TODO: alias, properties, separate, e-scalar

    def flow_content(self, n, c):
        '''
        ns-flow-content(n,c) 	::= 	ns-flow-yaml-content(n,c) | c-flow-json-content(n,c)
        ns-flow-yaml-content(n,c) 	::= 	ns-plain(n,c)
        ns-plain(n,c) 	::= 	c = flow-out  ⇒ ns-plain-multi-line(n,c)
                                c = flow-in   ⇒ ns-plain-multi-line(n,c)
                                c = block-key ⇒ ns-plain-one-line(c)
                                c = flow-key  ⇒ ns-plain-one-line(c)
        ns-plain-multi-line(n,c) 	::= 	ns-plain-one-line(c)
                                            s-ns-plain-next-line(n,c)* 
        s-ns-plain-next-line(n,c) 	::= 	s-flow-folded(n)
                                            ns-plain-char(c) nb-ns-plain-in-line(c)
        ns-plain-one-line(c) 	::= 	ns-plain-first(c) nb-ns-plain-in-line(c)
        ns-plain-first(c) 	::= 	( ns-char - c-indicator )
                                    | ( ( “?” | “:” | “-” )
                                    /* Followed by an ns-plain-safe(c)) */ ) 
        nb-ns-plain-in-line(c) 	::= 	( s-white* ns-plain-char(c) )* 
        '''
        if c in ['flow-out', 'flow-in']:
            # TODO: Handle multi-line
            if not self.current.type == 'scalar':
                raise Exception('Expected a "scalar" found a {}'.format(self.current))
            return self.join_tokens(['scalar', 'comma'])
        elif c in ['block-key', 'flow-key']:
            if not self.current.type == 'scalar':
                raise Exception('Expected a "scalar" found a {}'.format(self.current))
            return self.join_tokens(['scalar', 'comma'])
        else:
            raise Exception('Invalid value for c: "{}"'.format(c))

    def indent(self):
        if self.current.type == 'newline':
            self.indentation = 0
            self.advance()
        if self.current.type == 'indentation':
            self.indentation = len(self.current.value)
            self.advance()
