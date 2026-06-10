import argparse
import sys

from repository import Repository

def main():
    parser=argparse.ArgumentParser(description="GitPy: A small Pie of Git.")
    subparsers=parser.add_subparsers(dest="command", help="Available commands")
    
    init_parser=subparsers.add_parser("init", help="Initialize a new GitPy repository.")
    
    args=parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if(args.command=='init'):
            repository=Repository()
            repository.init()
            return
    except Exception as e:
        print(f"1. Error: {e}")
        sys.exit(1)
    
    


main()