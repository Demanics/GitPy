import time
from typing import List

from git_object import GitObject


class Commit(GitObject):
    def __init__(
        self,
        tree_hash: str,
        parent_hashes: List[str],
        author: str,
        committer: str,
        message: str,
        timestamp: int = None):
        self.tree_hash = tree_hash
        self.parent_hashes = parent_hashes
        self.author = author
        self.committer = committer
        self.message = message
        self.timestamp = timestamp or int(time.time())

        content = self._serialize_commit()
        super().__init__('commit', content)

    def _serialize_commit(self):
        lines = [f'tree {self.tree_hash}']

        for parent in self.parent_hashes:
            lines.append(f'parent {parent}')

        lines.append(f'author {self.author} {self.timestamp} +0000')
        lines.append(f'committer {self.committer} {self.timestamp} +0000')
        lines.append('')
        lines.append(self.message)

        return '\n'.join(lines).encode()

    @classmethod
    def from_content(cls, content: bytes) -> 'Commit':
        lines = content.decode().split('\n')
        tree_hash = None
        parent_hashes = []
        author = None
        committer = None
        timestamp = 0
        message_start = 0

        for i, line in enumerate(lines):
            if line.startswith('tree '):
                tree_hash = line[5:]
            elif line.startswith('parent '):
                parent_hashes.append(line[7:])
            elif line.startswith('author '):
                author_parts = line[7:].rsplit(' ', 2)
                author = author_parts[0]
                timestamp = int(author_parts[1])
            elif line.startswith('committer '):
                committer_parts = line[10:].rsplit(' ', 2)
                committer = committer_parts[0]
            elif line == '':
                message_start = i + 1
                break

        message = '\n'.join(lines[message_start:])
        commit = cls(tree_hash, parent_hashes, author, committer, message, timestamp)
        return commit