import json
from pathlib import Path
import time
from typing import Dict, Optional

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
    
    def checkout(self, branch: str, create_branch: bool):
        previous_branch = self.get_current_branch()
        files_to_clear = set()
        previous_commit_hash = None
        try:
            previous_commit_hash = self.get_branch_commit(previous_branch)
            if previous_commit_hash:
                previous_commit_object = self.load_object(previous_commit_hash)
                previous_commit = Commit.from_content(previous_commit_object.content)
                if previous_commit.tree_hash:
                    files_to_clear = self.get_files_from_tree_recursive(previous_commit.tree_hash)
        except Exception:
            files_to_clear = set()
 
        branch_file = self.heads_dir / branch
 
        if not branch_file.exists():
            if create_branch:
                if previous_commit_hash:
                    self.set_branch_commit(branch, previous_commit_hash)
                    print(f'Created a new branch {branch}.')
                else:
                    print('Make a new commit before switching to a new branch.')
                    return
            else:
                print(f'Branch {branch} not found.')
                print(f"Use 'checkout -b {branch}' to create and switch to a new branch.")
                return
 
        self.head_file.write_text(f'ref: refs/heads/{branch}\n')
        self.restore_working_directory(branch, files_to_clear)
        print(f'Switched to branch {branch}.')
 
    def get_files_from_tree_recursive(self, tree_hash: str, prefix: str = ''):
        files = set()
        try:
            tree_obj = self.load_object(tree_hash)
            tree = Tree.from_content(tree_obj.content)
            for mode, name, obj_hash in tree.entries:
                full_name = f'{prefix}{name}'
                if mode.startswith('100'):
                    files.add(full_name)
                elif mode.startswith('400'):
                    subtree_files = self.get_files_from_tree_recursive(obj_hash, f'{full_name}/')
                    files.update(subtree_files)
 
        except Exception as e:
            print(f'Warning: Could not read tree {tree_hash}: {e}')
 
        return files
 
    def restore_working_directory(self, branch: str, files_to_clear: set):
        target_commit_hash = self.get_branch_commit(branch)
        if not target_commit_hash:
            return
 
        for rel_path in sorted(files_to_clear):
            file_path = self.path / rel_path
            try:
                if file_path.is_file():
                    file_path.unlink() 
                elif file_path.is_dir():
                    if not any(file_path.iterdir()):
                        file_path.rmdir()
                         
            except Exception:
                pass
 
        target_commit_obj = self.load_object(target_commit_hash)
        target_commit = Commit.from_content(target_commit_obj.content)
 
        new_index = {}
        if target_commit.tree_hash:
            self.restore_tree(target_commit.tree_hash, self.path, new_index)
            # note to the user if work is not commited
 
        self.save_index(new_index)
 
    def restore_tree(self, tree_hash: str, path: Path, index_out: Dict[str, str] = None, prefix: str = ''):
        tree_obj = self.load_object(tree_hash)
        tree = Tree.from_content(tree_obj.content)
        for mode, name, obj_hash in tree.entries:
            file_path = path / name
            full_name = f'{prefix}{name}'
            if mode.startswith('100'):
                blob_obj = self.load_object(obj_hash)
                file_path.write_bytes(blob_obj.content)
                if index_out is not None:
                    index_out[full_name] = obj_hash
            elif mode.startswith('400'):
                file_path.mkdir(exist_ok=True)
                self.restore_tree(obj_hash, file_path, index_out, f'{full_name}/')
                
    def branch(self, branch_name: str = None, delete: bool = False):
        if delete:
            if not branch_name:
                print('Branch name required to delete a branch.')
                return
 
            current_branch = self.get_current_branch()
            if branch_name == current_branch:
                print(f'Cannot delete the currently checked out branch {branch_name}.')
                return
 
            branch_file = self.heads_dir / branch_name
            if branch_file.exists():
                branch_file.unlink()
                print(f'Deleted the branch {branch_name}.')
            else:
                print(f'Branch {branch_name} not found.')
            return
 
        if branch_name:
            branch_file = self.heads_dir / branch_name
            if branch_file.exists():
                print(f'Branch {branch_name} already exists.')
                return
 
            current_branch = self.get_current_branch()
            current_commit = self.get_branch_commit(current_branch)
            if current_commit:
                self.set_branch_commit(branch_name, current_commit)
                print(f'Created a new branch {branch_name}.')
            else:
                print('Make a new commit before creating a new branch.')
            return
 
        current_branch = self.get_current_branch()
        branches = []
        for branch_file in self.heads_dir.iterdir():
            if branch_file.is_file():
                branches.append(branch_file.name)
 
        for branch_item in sorted(branches):
            if branch_item == current_branch:
                print(f'* {branch_item}')
            else:
                print(f'  {branch_item}')
                
    def log(self, max_count: int = 10):
        current_branch = self.get_current_branch()
        current_commit = self.get_branch_commit(current_branch)
 
        if not current_commit:
            print('No commits yet.')
            return
 
        count = 0
        while current_commit and count < max_count:
            commit_obj = self.load_object(current_commit)
            commit = Commit.from_content(commit_obj.content)
            print(f'commit: {current_commit}')
            print(f'author: {commit.author}')
            print(f'timestamp: {time.ctime(commit.timestamp)}')
            print(f'\n    {commit.message}\n')
 
            current_commit = commit.parent_hashes[0] if commit.parent_hashes else None
            count += 1
 
        if current_commit and count >= max_count:
            print(f'(showing last {max_count} commits, use --max-count to see more)')