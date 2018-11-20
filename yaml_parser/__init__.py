
from .parser import Parser
from .pretty import prettyprint

def load(filename):
    return Parser().from_file(filename)
