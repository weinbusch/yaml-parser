
import argparse
from yaml_parser import load, prettyprint

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    parser.add_argument('--parse', action='store_true')
    parser.add_argument('--pretty', action='store_true')
    args = parser.parse_args()
    if args.pretty:
        prettyprint(args.filename)
    if args.parse:
        result = load(args.filename)
        print(result)
