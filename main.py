import argparse
import sys

from commit import Commit
from repository import Repository


def main():
    parser = argparse.ArgumentParser(
        description="GitPy: A small Pie of Git."
        )
    subparsers = parser.add_subparsers(
        dest="command", help="Available commands"
        )

    init_parser = subparsers.add_parser(
        "init",
        help="Initialize a new GitPy repository."
        )

    add_parser = subparsers.add_parser(
        "add",
        help="Add files and directories to the staging."
        )
    add_parser.add_argument(
        'paths',
        nargs='+',
        help='Files and directories to add in GitPy.'
        )

    commit_parser = subparsers.add_parser(
        'commit',
        help='create a new commit.'
        )
    commit_parser.add_argument(
        '-m',
        '--message',
        help='Commit message.',
        required=True
        )
    commit_parser.add_argument(
        '--author',
        help='Author name and email.',
        )
    
    checkout_parser=subparsers.add_parser(
        'checkout',
        help='Switch to another branch in GitPy repository.'
        )
    checkout_parser.add_argument(
        'branch',
        help='Branch to switch to.',
        )
    checkout_parser.add_argument(
        '-b',
        '--create-branch',
        action='store_true',
        help='Add a new branch.',
        )
    
    branch_parser = subparsers.add_parser(
        'branch',
        help='List and manage the branches.'
        )
    branch_parser.add_argument(
        '-d',
        '--delete',
        action='store_true',
        help='Delete a branch.',
        )
    branch_parser.add_argument(
        'name',
        nargs='?',
        help='Branch name to create or delete.'
        )   
    
    log_parser = subparsers.add_parser(
        'log',
        help='Show commit history.'
        )
    log_parser.add_argument(
        '-n',
        '--max-count',
        type=int,
        default=10,
        help='Maximum number of commits to show.'
    )
    
    status_parser = subparsers.add_parser(
        'status',
        help='Show status of the repository.'
        )
    
    

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    repository = Repository()

    try:
        if args.command == 'init':
            repository.init()
            return
        elif args.command == 'add':
            if not repository.gitpy_dir.exists():
                print(f"GitPy repository does not exist at {repository.gitpy_dir}")
                return

            for path in args.paths:
                repository.add_path(path)
        elif args.command == 'commit':
            if not repository.gitpy_dir.exists():
                print(f"GitPy repository does not exist at {repository.gitpy_dir}")
                return
            author = args.author or 'GitPy user <user@gitpy.com>'
            repository.commit(args.message, author)
        elif args.command == 'checkout':
            if not repository.gitpy_dir.exists():
                print(f"GitPy repository does not exist at {repository.gitpy_dir}")
                return
            repository.checkout(args.branch,args.create_branch)
        elif args.command == 'branch':
            if not repository.gitpy_dir.exists():
                print(f"GitPy repository does not exist at {repository.gitpy_dir}")
                return
            repository.branch(args.name, args.delete)
        elif args.command == 'log':
            if not repository.gitpy_dir.exists():
                print(f"GitPy repository does not exist at {repository.gitpy_dir}")
                return
            repository.log(args.max_count)
        elif args.command == 'status':
            if not repository.gitpy_dir.exists():
                print(f"GitPy repository does not exist at {repository.gitpy_dir}")
                return
            repository.status()


    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()