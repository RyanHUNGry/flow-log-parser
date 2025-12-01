# Start CLI application
import os
import sys

if os.path.join(os.getcwd(), "src") not in sys.path:
    sys.path.append(os.path.join(os.getcwd(), "src"))

from src.cli.cli import FlowlogParserCLI

if __name__ == '__main__':
    FlowlogParserCLI().cmdloop()
