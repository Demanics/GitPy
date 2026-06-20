# GitPy

> A lightweight Git-inspired version control system built in Python.

GitPy is a Python implementation of a distributed version control system inspired by Git. It helps developers understand how modern version control systems work internally by recreating core Git functionality such as commits, staging, branching, object storage, and repository tracking.

---

## Features

- Initialize repositories
- Track file changes
- Stage files before committing
- Create commits with commit messages
- Store file snapshots using hashing
- Maintain commit history
- Branch creation and management
- Restore previous versions
- Lightweight object storage system
- Built completely in Python

---

## Motivation

Git is one of the most important developer tools, but its internal architecture can feel like a black box.

GitPy was built to answer:

**"What if we recreated Git from scratch in Python to understand how version control actually works?"**

This project focuses on learning the internal mechanics behind:

- Content-addressable storage
- Commit trees
- Snapshot management
- Branch references
- File tracking
- Hash-based object storage

---

## Tech Stack

- **Python 3**
- File System Operations (`os`, `pathlib`)
- Hashing (`hashlib`)
- Serialization (`json`, `pickle`)
- CLI Argument Parsing (`argparse`)

---

## Project Structure

```bash
GitPy/
│
├── gitpy/                 # Core source code
│   ├── init.py           # Repository initialization
│   ├── add.py            # Staging files
│   ├── commit.py         # Commit logic
│   ├── branch.py         # Branch management
│   ├── checkout.py       # Restore snapshots
│   ├── objects.py        # Object storage handling
│   └── utils.py          # Helper functions
│
├── tests/               # Unit tests
├── .gitignore
├── README.md
└── main.py
```

*(Modify structure if your repo differs.)*

---

## Installation

Clone the repository:

```bash
git clone https://github.com/Demanics/GitPy.git
cd GitPy
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate environment:

**Windows**

```bash
venv\Scripts\activate
```

**Linux / Mac**

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Usage

### Initialize Repository

```bash
python main.py init
```

### Add Files

```bash
python main.py add filename.txt
```

### Commit Changes

```bash
python main.py commit -m "Initial commit"
```

### Create Branch

```bash
python main.py branch new-feature
```

### View Commit History

```bash
python main.py log
```

### Checkout Branch

```bash
python main.py checkout new-feature
```

---

## How It Works

GitPy follows a simplified Git architecture.

### 1. Staging Area

Files are added to an index before committing.

### 2. Object Storage

Each file is converted into a hashed object.

Example:

```text
hello.txt → SHA-1 Hash → Stored in objects/
```

### 3. Commits

A commit stores:

- Snapshot of tracked files
- Parent commit reference
- Timestamp
- Commit message

### 4. Branches

Branches are simply pointers to commits.

---

## Example Workflow

```bash
gitpy init

gitpy add app.py

gitpy commit -m "First commit"

gitpy branch development

gitpy checkout development
```

---

## Learning Outcomes

This project demonstrates understanding of:

- Version Control Systems
- Data Structures
- File Handling
- Hashing Algorithms
- CLI Application Development
- Repository Architecture
- Git Internals

---

## Future Improvements

- Remote repository support
- Push and pull functionality
- Merge conflict resolution
- Diff tracking
- Better branch visualization
- Compression for stored objects
- Network synchronization

---

## Contributing

Contributions are welcome.

```bash
Fork → Clone → Make Changes → Commit → Push → Pull Request
```

---

## License

MIT License

---

## Author

Built by Muhammad Ali and contributors.

GitHub:

https://github.com/Demanics

---

## Inspiration

Inspired by:

- :contentReference[oaicite:1]{index=1}  
- :contentReference[oaicite:2]{index=2}  
- :contentReference[oaicite:3]{index=3}  

---
