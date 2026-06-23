# GitPy (git-pie 🥧)

> A minimal, lightweight implementation of the Git Version Control System built completely from scratch in Python.

GitPy replicates Git’s foundational internal architecture, utilizing a **content-addressable storage system** and maintaining standard local repository states to track files, stage changes, and manage branches entirely offline. It is designed to act as a clear, tactile learning tool to understand how modern version control systems handle snapshots under the hood.

---

## 🏗️ Architecture & Internals

GitPy splits your working space into three independent layers:
1. **Working Directory:** The local file tree on your disk where you actively create and modify files.
2. **Staging Area (Index):** A state file (`.gitpy/index`) caching unique relative paths to compressed file content hashes.
3. **Local Repository:** The internal key-value database storing immutable, compressed data files under `.gitpy/objects/`.

### 📦 The Core Storage Engine
Every historical artifact in GitPy is saved under `.gitpy/objects/` using **lossless compression (via `zlib`)** and indexed via a deterministic **SHA-1 hash**. 

To maximize linear directory lookup speeds, the system splits the hex hash string into a two-character fan-out directory configuration (e.g., hash `b878fd...` is written directly as `.gitpy/objects/b8/78fd...`). This scales lookup performance closer to an ideal $O(1)$ bucketing map.

The system handles three structural object types:
* **Blob (Binary Large Object):** Stores the raw decompressed byte array content of a file. It completely ignores both the filename and full path. If multiple identical files exist across different directories, only a *single* blob instance is saved.
* **Tree:** Represents the specific hierarchy configuration of your folders. It maps local permissions (file modes like `100644` for regular entries or `40000` for directory paths), strings, and related object hashes.
* **Commit:** An immutable textual file cataloging a target base root `Tree` hash string, parent array tracking links (for historical tracing), active author attributes, time configurations, and messages.

---

## 🚀 Supported Commands

GitPy drives an optimized, interactive command-line workspace mapped out natively through Python's built-in `argparse` parser toolkit.

### 1. Initialize a Workspace
Prepares a fresh offline database track mapping environment:
```bash
python3 main.py init
Generates a structural .gitpy/ directory mapping empty objects/ folders, a refs/heads/ track directory, an empty JSON staging reference index, and updates a .gitpy/HEAD pointer pointing by default to ref: refs/heads/master.

2. Stage Changes
Stages local changes directly into your tracking engine framework:

Bash
# Stage an isolated specific file path
python3 main.py add file.txt

# Recursively stage everything inside the active folder directory
python3 main.py add .
Recursively reviews target paths, generates matching compressed Blob components into the key database tracking tree, and logs mapped paths within the dynamic .gitpy/index layout configuration.

3. Record Snapshots
Freezes and registers staged configurations safely into the repo layout timeline:

Bash
python3 main.py commit -m "Your commit message"
Compiles the dynamic layout index into immutable multi-level Tree blocks bottom-up, bundles parameters alongside the primary tip hash into a permanent Commit node, resets your active index staging area, and moves the head reference marker under .gitpy/refs/heads/.

4. Audit Tracking States
Inspects localized deviations across tracking zones instantly:

Bash
python3 main.py status
Tracks and returns clear data reports across 4 distinct file arrays: Changes to be committed (staged differences), Changes not staged for commit (modified local files vs index maps), Untracked files, and Deleted files.

5. Review History Tracks
Iterates over continuous metadata link strings to map chronological history logs:

Bash
python3 main.py log

# Optional: limit log listings using an index limit switch parameter
python3 main.py log -n 5
6. Manage Parallel Streams (Branching)
Generates, views, or tears down standalone working lines:

Bash
# List all active system branches (* labels the current active target head)
python3 main.py branch

# Spawn a safe parallel stream pointing to the active tip commit hash
python3 main.py branch <branch-name>

# Wipe out a targeted pointer reference channel completely
python3 main.py branch -d <branch-name>
7. Shift Contexts (Checkout)
Safely handles shifting file system configurations across active timeline lines:

Bash
# Shift context cleanly into an existing branch path
python3 main.py checkout <branch-name>

# Spawn a completely new branch path and switch contexts immediately
python3 main.py checkout -b <new-branch-name>
Identifies file assets tied to the incoming state node, purges old tracking data components safely from disk workspace via file unlink methods, materializes and writes correct target content layout trees from compressed blobs, and swaps the tracking link reference string inside .gitpy/HEAD.

📁 Project Structure
Bash
GitPy/
│
├── .gitpy/               # Generated database environment (Internal use only)
│   ├── objects/          # Content-addressable key-value zip vault database
│   ├── refs/             # Tracking reference stream channels for branch points
│   ├── HEAD              # Tracks active branch focus state string
│   └── index             # Caches active pathing layouts (JSON mapping file)
│
├── main.py               # Monolithic engine script hosting internal system mechanics
├── README.md             # Project documentation manual
└── requirements.txt      # Dev workspace configuration mapping targets
🛠️ Getting Started
Installation
Clone the source directory map locally onto your computer:

Bash
git clone [https://github.com/Demanics/GitPy.git](https://github.com/Demanics/GitPy.git)
cd GitPy
Configuration Sandbox
Ensure you have Python 3.9+ set up. Since the execution engine depends exclusively on native library extensions (argparse, pathlib, zlib, hashlib, json), zero mandatory third-party software configuration packages are needed.

To prevent collision problems with real standard Git layouts inside text editors, your tracking engine relies strictly on custom .gitpy/ storage zones.

📈 Future Iterations
Garbage Collection (gc): Scan data maps and wipe unreferenced, orphaned blob nodes floating inside the objects structure directory.

Merge Trees (merge): Parse dual matching history arrays at single code nodes to reconstruct combined timelines.

Stash Cache (stash): Safely cache uncommitted changes on a temporary internal stack loop.

📄 License
This project is licensed under the MIT License.

✍️ Author
Built from scratch by Muhammad Ali.

GitHub: @Demanics
