import hashlib
import zlib


class GitObject:
    def __init__(self, obj_type: str, content: bytes):
        self.type = obj_type
        self.content = content

    def hash(self) -> str:
        # f{<type> <size>\0<content>}
        header = f"{self.type} {len(self.content)}\0".encode()
        return hashlib.sha1(header + self.content).hexdigest()

    def serialize(self) -> bytes:
        # f{<type> <size>\0<content>}
        header = f"{self.type} {len(self.content)}\0".encode()
        return zlib.compress(header + self.content)

    @classmethod
    def deserialize(cls, data: bytes) -> 'GitObject':
        decompressed = zlib.decompress(data)
        null_idx = decompressed.find(b'\0')
        header = decompressed[:null_idx]
        content = decompressed[null_idx + 1:]
        obj_type, _ = header.split(b" ")
        return cls(obj_type.decode(), content)