import json
from pathlib import Path
from typing import Dict

from blob import Blob
from git_object import GitObject


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
    
    def add_path(self,path:str)->None:
        full_path=self.path / path
        
        if not full_path.exists:
            raise FileNotFoundError(f'Path {path} not found.')
        
        if full_path.is_file():
            self.add_file(path)
        elif full_path.is_dir():
            self.add_directory(path)
        else:
            raise ValueError(f'{path} is neither a directory nor a file.')
        
    def add_file(self, path:str):
        full_path=self.path / path
        if not full_path.exists():
            raise FileNotFoundError(f'Path {path} not found.')
            return
        
        # Read the file content
        content =full_path.read_bytes()
        
        # create BLOB object form content
        blob=Blob(content)
        
        # Store the BLOB object in database (./git objects)
        blob_hash=self.store_object(blob)
        
        # update index to include the file
        index=self.load_index()
        index[path]=blob_hash
        self.save_index(index)
        
        print(f'Added {path} ')
        
        
    def store_object(self, obj:GitObject)->str:
        obj_hash=obj.hash()
        obj_dir=self.objects_dir / obj_hash[:2]
        obj_file=obj_dir/obj_hash[2:]
        
        if not obj_file.exists():
            obj_dir.mkdir(exist_ok=True)
            obj_file.write_bytes(obj.serialize())
            
        return obj_hash
    
    def load_index(self)->Dict[str,str]:
        if not self.index_file.exists():
            return {}
        try:
            return json.loads(self.index_file.read_text())
        except:
            return {}
        
    def save_index(self,index: Dict[str,str]):
        self.index_file.write_text(json.dumps(index,indent=2))
        
    def add_directory(self,path:str):
        full_path=self.path / path
        if not full_path.exists():
            raise FileNotFoundError(f'Directory {path} not found.')
            return
        if not full_path.is_dir():
            raise ValueError(f'{path} not a directory.')
        count=0
        # recursively traverse the directory
        for file_path in full_path.rglob("*"):
            if file_path.is_file():
                if any(ignored in file_path.parts for ignored in ['.gitpy', '__pycache__']):
                    continue
                
                relative_path = str(file_path.relative_to(self.path))
                self.add_file(relative_path)
                count+=1
                
        if count==0:
            print(f'Directory {path} is already upto date.')
        else:
            print(f'Added {count} files from directory "{path}".')