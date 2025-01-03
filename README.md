# R3nameX 🚀  
Batch file renaming tool with rollback functionality – efficient, simple, and powerful.  

## 📜 Description  
**R3nameX** is a Python-based file renaming utility that automates batch file renaming with precision.  
It supports rollback functionality to revert changes if needed, making it a reliable solution for managing large sets of files.  

🔧 **Key Features:**  
- Rename files sequentially with custom prefixes.  
- Rollback feature to undo renaming operations.  
- Generates logs for every operation (renaming, rollback, and errors).  
- Permission checks to ensure smooth operations.  

---

## 🛠️ Installation  
### Clone the repository:  
```bash
git clone https://github.com/stuxboynet/r3namex.git
cd r3namex
```

---

## 🚀 Usage
### Basic Renaming:
```bash
python r3namex.py -l /images -a -p Photo -ns 10
Renames all files with the prefix "Photo", starting at 10.
```
### Basic Renumber:
```bash
python r3namex.py -l /my/folder -p File -cs 1 -ce 10 -ns 50
Renumber files with the prefix "File" from 1 to 10, starting at 50.
```
### Rollback (Undo Renaming):
```bash
python r3namex.py -l /my/folder -r
Restores the last renaming operation.
```

---

## 🔍 Examples
```bash
# Rename with prefix
python r3namex.py -l /images -a -p Photo -ns 10
python r3namex.py --location /images --all --prefix Photo --new-start 10

# Rename without prefix (Script will use "File" for default prefeix)
python r3namex.py -l /images -a -ns 10
python r3namex.py --location /images --all --new-start 10

# Renumber files with prefix
python r3namex.py -l /my/folder -p Evidence -cs 1 -ce 3 -ns 5  
python r3namex.py --location /my/folder --prefix Evidence --current-start 1 --current-end 3 --new-start 5  

# Renumber without prefix
python r3namex.py -l /my/folder -cs 1 -ce 3 -ns 5
python r3namex.py --location /my/folder --current-start 1 --current-end 3 --new-start 5  

# Rollback
python r3namex.py -l /my/folder -r  
python r3namex.py --location /my/folder --rollback  
```


## ⚙️ Command Line Options
```bash
python r3namex.py [options]
```

| Option | Description | Example |
| --- | --- | --- |
| `-l`, `--location` | Folder where files are located | `-l myfolder` |
| `-p`, `--prefix` | Prefix of files (optional) | `-p Invoice` |
| `-a`, `--all` | Rename all files in the directory | `-a` |
| `-cs`, `--current_start` | Start of current range | `-cs 1` |
| `-ce`, `--current_end` | End of current range | `-ce 20` |
| `-ns`, `--new_start` | New start point for renaming | `-ns 50` |
| `-r`, `--rollback` | Revert last renaming operation | `-r` |


---

## 🧩 Automatic Rollback
When a renaming operation is performed, R3nameX saves a mapping of the original files in `backup_mapping.txt`.
If an error occurs, the rollback automatically reverts the files to their previous state.


## 🔍 Activity Log (Log)  
Every time a renaming or rollback operation is performed, R3nameX saves a detailed record in the `logs.log` file.  

Example log:  
```text
2025-01-02 14:35:21 - Command: python r3namex.py -l /my/folder -cs 1 -ce 5 -ns 10
2025-01-02 14:35:22 - Renamed: 1.txt -> 10.txt
2025-01-02 14:35:23 - Renaming completed. Total files renamed: 5.
```

