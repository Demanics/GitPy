import json
from pathlib import Path


class Repository:
    def __init__(self,path="."):
        self.path=Path(path).resolve()        
        self.gitpy_dir=self.path / ".gitpy"
        self.objects_dir=self.gitpy_dir / "objects"
        self.ref_dir=self.gitpy_dir / "refs"
        self.heads_dir=self.ref_dir / "heads"
        self.head_file=self.gitpy_dir / "HEAD"
        self.index_file=self.gitpy_dir / "index"
        
    
    def init(self)->bool:
        if(self.gitpy_dir.exists()):
            print(f"GitPy repository already exists at {self.gitpy_dir}")
            return False
        
        self.gitpy_dir.mkdir()
        self.objects_dir.mkdir()
        self.ref_dir.mkdir()
        self.heads_dir.mkdir()
        
        self.head_file.write_text("ref: refs/heads/master\n")
        self.index_file.write_text(json.dumps({},indent=2))
        
        print(f"Initialized empty GitPy repository in {self.gitpy_dir}")
        return True
        
        
        
        