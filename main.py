import argparse
import sys

from repository import Repository

def main():
    parser=argparse.ArgumentParser(
        description="GitPy: A small Pie of Git."
        )
    subparsers=parser.add_subparsers(
        dest="command", help="Available commands"
        )
    
    init_parser=subparsers.add_parser(
        "init", 
        help="Initialize a new GitPy repository."
        )
    
    add_parser=subparsers.add_parser(
        "add", 
        help="Add files and directories to the staging."
        )
    add_parser.add_argument(
        'paths',
        nargs='+', 
        help='Files and directories to add in GitPy.'
        )
    
    args=parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    repository=Repository()
    
    try:
        if args.command=='init':
            repository.init()
            return
        elif args.command=='add':
            if not repository.gitpy_dir.exists():
                print(f"GitPy repository does not exists at {repository.gitpy_dir}")
                return False
            
            for path in args.paths:
                repository.add_path(path)
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    


main()