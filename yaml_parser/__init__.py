
from .parser import Parser
from .tokenizer import prettyprint

def load(filename):
    return Parser().from_file(filename)
