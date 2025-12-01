from parser.parser import Parser

parser = Parser("data/default.txt")
parser.deserialize()

print(parser.search_by_source_ip("10.13.169.21"))