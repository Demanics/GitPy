import json
from pathlib import Path
from typing import Dict

from blob import Blob
from commit import Commit
from git_object import GitObject
from tree import Tree


class Repository:
    def __init__(self, path="."):
        self.path = Path(path).resolve()
        self.gitpy_dir = self.path / ".gitpy"
        self.objects_dir = self.gitpy_dir / "objects"
        self.ref_dir = self.gitpy_dir / "refs"
        self.heads_dir = self.ref_dir / "heads"
        self.head_file = self.gitpy_dir / "HEAD"
        self.index_file = self.gitpy_dir / "index"

    def init(self) -> bool:
        if self.gitpy_dir.exists():
            print(f"GitPy repository already exists at {self.gitpy_dir}")
            return False

        self.gitpy_dir.mkdir()
        self.objects_dir.mkdir()
        self.ref_dir.mkdir()
        self.heads_dir.mkdir()

        self.head_file.write_text("ref: refs/heads/master\n")
        self.save_index({})

        print(f"Initialized empty GitPy repository in {self.gitpy_dir}")
        return True

    def add_path(self, path: str) -> None:
        full_path = self.path / path

        if not full_path.exists():
            raise FileNotFoundError(f'Path {path} not found.')

        if full_path.is_file():
            self.add_file(path)
        elif full_path.is_dir():
            self.add_directory(path)
        else:
            raise ValueError(f'{path} is neither a directory nor a file.')

    def add_file(self, path: str):
        full_path = self.path / path
        if not full_path.exists():
            raise FileNotFoundError(f'Path {path} not found.')

        # Read the file content
        content = full_path.read_bytes()

        # create BLOB object from content
        blob = Blob(content)

        # Store the BLOB object in database (./gitpy/objects)
        blob_hash = self.store_object(blob)

        # update index to include the file
        index = self.load_index()
        index[path] = blob_hash
        self.save_index(index)

        print(f'Added {path}')

    def store_object(self, obj: GitObject) -> str:
        obj_hash = obj.hash()
        obj_dir = self.objects_dir / obj_hash[:2]
        obj_file = obj_dir / obj_hash[2:]

        if not obj_file.exists():
            obj_dir.mkdir(exist_ok=True)
            obj_file.write_bytes(obj.serialize())

        return obj_hash

    def load_index(self) -> Dict[str, str]:
        if not self.index_file.exists():
            return {}
        try:
            return json.loads(self.index_file.read_text())
        except Exception:
            return {}

    def save_index(self, index: Dict[str, str]):
        self.index_file.write_text(json.dumps(index, indent=2))

    def add_directory(self, path: str):
        full_path = self.path / path
        if not full_path.exists():
            raise FileNotFoundError(f'Directory {path} not found.')
        if not full_path.is_dir():
            raise ValueError(f'{path} not a directory.')
        count = 0
        # recursively traverse the directory
        for file_path in full_path.rglob("*"):
            if file_path.is_file():
                if any(ignored in file_path.parts for ignored in ['.gitpy', '__pycache__']):
                    continue

                relative_path = str(file_path.relative_to(self.path))
                self.add_file(relative_path)
                count += 1

        if count == 0:
            print(f'Directory {path} is already up to date.')
        else:
            print(f'Added {count} files from directory "{path}".')

    def commit(self, message: str, author: str = 'GitPy User <user@gitpy.com>'):
        # create a tree from the index
        tree_hash = self.create_tree_from_index()
        current_branch = self.get_current_branch()
        parent_commit = self.get_branch_commit(current_branch)
        parent_hashes = [parent_commit] if parent_commit else []

        index = self.load_index()
        if not index:
            print('No files at the staging area. Working tree is clean.')
            return None

        if parent_commit:
            parent_git_commit_obj = self.load_object(parent_commit)
            parent_commit_data = Commit.from_content(parent_git_commit_obj.content)

            if tree_hash == parent_commit_data.tree_hash:
                print('No files at the staging area. Working tree is clean.')
                return None

        commit = Commit(
            tree_hash=tree_hash,
            parent_hashes=parent_hashes,
            author=author,
            committer=author,
            message=message
        )

        commit_hash = self.store_object(commit)
        self.set_branch_commit(current_branch, commit_hash)
        self.save_index({})
        print(f'Created commit {commit_hash} on branch {current_branch}.')
        return commit_hash

    def create_tree_from_index(self):
        index = self.load_index()
        if not index:
            tree = Tree()
            return self.store_object(tree)

        dirs = {}
        files = {}
        for file_path, blob_hash in index.items():
            parts = file_path.split('/')

            if len(parts) == 1:
                files[parts[0]] = blob_hash
            else:
                dir_name = parts[0]
                if dir_name not in dirs:
                    dirs[dir_name] = {}
                current = dirs[dir_name]

                for part in parts[1:-1]:
                    if part not in current:
                        current[part] = {}

                    current = current[part]

                current[parts[-1]] = blob_hash

        def create_tree_recursive(entries_dict: Dict):
            tree = Tree()
            for name, value in entries_dict.items():
                if isinstance(value, str):
                    tree.add_entry('100644', name, value)
                elif isinstance(value, dict):
                    subtree_hash = create_tree_recursive(value)
                    tree.add_entry('40000', name, subtree_hash)

            return self.store_object(tree)

        root_entries = {**files}

        for dir_name, dir_contents in dirs.items():
            root_entries[dir_name] = dir_contents

        return create_tree_recursive(root_entries)

    def get_current_branch(self) -> str:
        if not self.head_file.exists():
            return 'master'

        head_content = self.head_file.read_text().strip()
        if head_content.startswith('ref: refs/heads/'):
            return head_content[len('ref: refs/heads/'):]

        return 'HEAD'

    def get_branch_commit(self, current_branch: str):
        branch_file = self.heads_dir / current_branch

        if branch_file.exists():
            return branch_file.read_text().strip()

        return None

    def set_branch_commit(self, current_branch: str, commit_hash: str):
        branch_file = self.heads_dir / current_branch
        branch_file.write_text(commit_hash + '\n')

    def load_object(self, obj_hash: str) -> GitObject:
        obj_dir = self.objects_dir / obj_hash[:2]
        obj_file = obj_dir / obj_hash[2:]
        if not obj_file.exists():
            raise FileNotFoundError(f'Object {obj_hash} not found.')

        return GitObject.deserialize(obj_file.read_bytes())