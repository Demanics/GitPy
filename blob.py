from git_object import GitObject


class Blob(GitObject):
    def __init__(self, content):
        super().__init__("blob", content)

    def get_content(self) -> bytes:
        return self.content