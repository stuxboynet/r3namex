#!/usr/bin/env python3
"""
R3nameX - Batch File Renaming Tool
Created by: Fabian Peña (stuxboynet)
GitHub: https://github.com/stuxboynet/r3namex
Version: 2.0.0
License: BSD 3-Clause
"""

import os
import argparse
import sys
import json
import shutil
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
try:
    import urllib.request
    import urllib.error
except ImportError:
    urllib = None

# Version info - MUST be before BANNER
__author__ = "Fabian Peña (stuxboynet)"
__version__ = "2.0.0"
__license__ = "BSD 3-Clause"
__repo__ = "https://github.com/stuxboynet/r3namex"

LOG_FILE = "logs.log"
MAPPING_FILE = "backup_mapping.json"

BANNER = """
  _____  ____                            __   __ 
 |  __ \|___ \                           \ \ / / 
 | |__) | __) |_ __   __ _ _ __ ___   ___ \ V /  
 |  _  / |__ <| '_ \ / _` | '_ ` _ \ / _ \ > <   
 | | \ \ ___) | | | | (_| | | | | | |  __// . \  
 |_|  \_\____/|_| |_|\__,_|_| |_| |_|\___/_/ \_\ 
                                                 
        Created by Fabian Peña (stuxboynet)
                    Version """ + __version__

EXAMPLES = """
EXAMPLES:

To rename and enumerate all files:

    python r3namex.py -l /images -a -p Photo -ns 10
    python r3namex.py --location /images --all --prefix Photo --new-start 10

To renumber files with numbering:

    python r3namex.py -l /my/folder -p Evidence -cs 1 -ce 3 -ns 5  
    python r3namex.py --location /my/folder --prefix Evidence --current-start 1 --current-end 3 --new-start 5  

To revert renaming (rollback):

    python r3namex.py -l /my/folder -p Evidence -r  
    python r3namex.py --location /my/folder --prefix Evidence --rollback  

To handle duplicates:

    python r3namex.py -l /my/folder -p Photo -cs 1 -ce 5 -ns 1 -ds suffix
    python r3namex.py --location /my/folder --prefix Photo --current-start 1 --current-end 5 --new-start 1 --duplicate-strategy suffix

"""


def check_for_updates():
    """Check GitHub for newer version"""
    if urllib is None:
        print("Error: urllib module not available for update check")
        return
    
    try:
        print("Checking for updates...")
        url = f"{__repo__}/raw/main/r3namex.py"
        
        # Get remote version
        response = urllib.request.urlopen(url, timeout=5)
        content = response.read().decode('utf-8')
        
        # Extract version from remote file
        for line in content.split('\n'):
            if line.startswith('__version__') and '=' in line:
                remote_version = line.split('"')[1]
                break
        else:
            print("Could not determine remote version")
            return
        
        # Compare versions
        current = tuple(map(int, __version__.split('.')))
        remote = tuple(map(int, remote_version.split('.')))
        
        if remote > current:
            print(f"\n✨ New version available: {remote_version} (current: {__version__})")
            print(f"📥 Download: {__repo__}/releases/latest")
            
            choice = input("\nDo you want to update now? [Y/N]: ").strip().lower()
            if choice == 'y':
                update_script(url)
        else:
            print(f"✓ You're using the latest version ({__version__})")
            
    except urllib.error.URLError as e:
        print(f"Error checking for updates: Network error")
    except Exception as e:
        print(f"Unexpected error: {e}")


def update_script(url):
    """Download and replace current script with new version"""
    try:
        print("Downloading new version...")
        
        # Download to temporary file
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as tmp:
            response = urllib.request.urlopen(url)
            tmp.write(response.read())
            tmp_path = tmp.name
        
        # Backup current script
        current_script = os.path.abspath(sys.argv[0])
        backup_path = current_script + '.backup'
        shutil.copy2(current_script, backup_path)
        
        # Replace with new version
        shutil.move(tmp_path, current_script)
        
        # Make executable on Unix-like systems
        if os.name != 'nt':
            os.chmod(current_script, 0o755)
        
        print(f"✓ Update successful! Backup saved as: {backup_path}")
        print("Please restart the script to use the new version.")
        sys.exit(0)
        
    except Exception as e:
        print(f"Error updating: {e}")
        if 'tmp_path' in locals() and os.path.exists(tmp_path):
            os.remove(tmp_path)


def show_version():
    """Display version information"""
    print(f"""{BANNER}

R3nameX - Batch File Renaming Tool
Version: {__version__}
Author: {__author__}
License: {__license__}
GitHub: {__repo__}

Python: {sys.version.split()[0]}
Platform: {sys.platform}
""")


class RenameOperation:
    """Clase para representar una operación de renombrado"""
    def __init__(self, old_path, new_path, operation_type="rename"):
        self.old_path = os.path.abspath(old_path)
        self.new_path = os.path.abspath(new_path)
        self.operation_type = operation_type  # "rename", "backup", "overwrite"
        self.backup_path = None
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self):
        return {
            "old_path": self.old_path,
            "new_path": self.new_path,
            "operation_type": self.operation_type,
            "backup_path": self.backup_path,
            "timestamp": self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data):
        op = cls(data["old_path"], data["new_path"], data["operation_type"])
        op.backup_path = data.get("backup_path")
        op.timestamp = data.get("timestamp")
        return op


class DuplicateHandler:
    """Maneja archivos duplicados con soporte completo de rollback"""
    
    def __init__(self, strategy="ask", backup_dir=".rename_backups"):
        self.strategy = strategy
        self.backup_dir = backup_dir
        self.operations = []
    
    def handle_duplicate(self, old_path, new_path):
        """Maneja un caso de duplicado y registra la operación para rollback"""
        
        # Si no hay conflicto, es un renombrado simple
        if not os.path.exists(new_path):
            os.rename(old_path, new_path)
            op = RenameOperation(old_path, new_path, "rename")
            self.operations.append(op)
            return new_path
        
        # Si son el mismo archivo, no hacer nada
        if os.path.samefile(old_path, new_path):
            return new_path
        
        # Manejar según estrategia
        if self.strategy == "skip":
            return self._handle_skip(old_path, new_path)
        elif self.strategy == "suffix":
            return self._handle_suffix(old_path, new_path)
        elif self.strategy == "backup":
            return self._handle_backup(old_path, new_path)
        elif self.strategy == "overwrite":
            return self._handle_overwrite(old_path, new_path)
        else:  # ask
            return self._handle_ask(old_path, new_path)
    
    def _handle_skip(self, old_path, new_path):
        """Omite el archivo si ya existe el destino"""
        print(f"  [SKIP] {os.path.basename(old_path)} (destination already exists)")
        # No se registra operación porque no se hizo nada
        return old_path
    
    def _handle_suffix(self, old_path, new_path):
        """Agrega sufijo numérico para evitar colisión"""
        directory = os.path.dirname(new_path)
        filename = os.path.basename(new_path)
        name, ext = os.path.splitext(filename)
        
        # Encontrar nombre disponible
        counter = 1
        original_new_path = new_path
        while os.path.exists(new_path):
            new_filename = f"{name}_{counter}{ext}"
            new_path = os.path.join(directory, new_filename)
            counter += 1
        
        os.rename(old_path, new_path)
        op = RenameOperation(old_path, new_path, "rename")
        self.operations.append(op)
        
        print(f"  [RENAMED] {os.path.basename(old_path)} -> {os.path.basename(new_path)}")
        return new_path
    
    def _handle_backup(self, old_path, new_path):
        """Hace backup del archivo existente antes de renombrar"""
        # Crear directorio de backup
        backup_dir = os.path.join(os.path.dirname(new_path), self.backup_dir)
        os.makedirs(backup_dir, exist_ok=True)
        
        # Generar nombre de backup único
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        backup_name = f"{os.path.basename(new_path)}.{timestamp}.backup"
        backup_path = os.path.join(backup_dir, backup_name)
        
        # Mover archivo existente a backup
        shutil.move(new_path, backup_path)
        
        # Renombrar archivo original
        os.rename(old_path, new_path)
        
        # Registrar operación compleja
        op = RenameOperation(old_path, new_path, "backup")
        op.backup_path = backup_path
        self.operations.append(op)
        
        print(f"  [BACKUP] {os.path.basename(new_path)} -> {backup_name}")
        print(f"  [RENAMED] {os.path.basename(old_path)} -> {os.path.basename(new_path)}")
        return new_path
    
    def _handle_overwrite(self, old_path, new_path):
        """Sobrescribe el archivo existente (con backup oculto para rollback)"""
        # Crear backup oculto para poder hacer rollback
        backup_dir = os.path.join(os.path.dirname(new_path), self.backup_dir, "overwritten")
        os.makedirs(backup_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        backup_name = f"{os.path.basename(new_path)}.{timestamp}.overwritten"
        backup_path = os.path.join(backup_dir, backup_name)
        
        # Mover el archivo que será sobrescrito al backup
        shutil.move(new_path, backup_path)
        
        # Renombrar
        os.rename(old_path, new_path)
        
        # Registrar operación
        op = RenameOperation(old_path, new_path, "overwrite")
        op.backup_path = backup_path
        self.operations.append(op)
        
        print(f"  [OVERWRITE] {os.path.basename(new_path)}")
        return new_path
    
    def _handle_ask(self, old_path, new_path):
        """Pregunta al usuario qué hacer"""
        print(f"\nConflict: '{os.path.basename(new_path)}' already exists")
        print("Options:")
        print("  1. Skip this file")
        print("  2. Rename with suffix (file_1, file_2, etc.)")
        print("  3. Backup existing file")
        print("  4. Overwrite existing file")
        
        while True:
            choice = input("Choose option (1-4): ").strip()
            
            if choice == "1":
                return self._handle_skip(old_path, new_path)
            elif choice == "2":
                return self._handle_suffix(old_path, new_path)
            elif choice == "3":
                return self._handle_backup(old_path, new_path)
            elif choice == "4":
                return self._handle_overwrite(old_path, new_path)
            else:
                print("Invalid option. Please choose 1-4.")
    
    def save_operations(self, mapping_file):
        """Guarda las operaciones para rollback"""
        data = {
            "version": "2.0",  # Versión del formato para compatibilidad futura
            "timestamp": datetime.now().isoformat(),
            "operations": [op.to_dict() for op in self.operations]
        }
        
        with open(mapping_file, "w") as f:
            json.dump(data, f, indent=2)


def check_write_permissions(directory):
    if not os.access(directory, os.W_OK):
        print(f"Error: You do not have write permissions in {directory}.")
        log_action(f"You do not have write permissions in {directory}.")
        sys.exit(1)


def log_action(message, command=None):
    with open(LOG_FILE, "a") as log:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cmd_info = f"Command: {command}\n" if command else ""
        log.write(f"{timestamp} - {cmd_info}{message}\n")


def rename_all_files_interactive(directory, prefix=None, start_number=1, duplicate_strategy="ask"):
    try:
        directory = os.path.abspath(directory)
        if not os.path.exists(directory):
            print(f"Error: The directory '{directory}' does not exist.")
            return

        check_write_permissions(directory)
        
        print("\n" + "="*60)
        print("INTERACTIVE RENAME MODE")
        print("="*60)
        print(f"Base directory: {directory}")
        print("="*60)
        
        handler = DuplicateHandler(duplicate_strategy)
        total_files_renamed = 0
        
        # Función recursiva para procesar carpetas nivel por nivel
        def process_folder_level(current_path, current_prefix, current_start):
            nonlocal total_files_renamed
            
            # Obtener archivos en la carpeta actual (sin subcarpetas)
            files = [f for f in os.listdir(current_path) 
                    if os.path.isfile(os.path.join(current_path, f))]
            
            if files:
                # Mostrar información de la carpeta actual
                rel_path = os.path.relpath(current_path, directory)
                if rel_path == ".":
                    print(f"\nProcessing: MAIN FOLDER")
                else:
                    print(f"\nProcessing: {rel_path}")
                
                print(f"Files in this folder: {len(files)}")
                
                # Preguntar si quiere cambiar el prefijo para esta carpeta
                folder_prefix = current_prefix
                if folder_prefix is None or input("\n> Do you want to set a new prefix? [Y/N]: ").strip().lower() == 'y':
                    folder_prefix = input("> Enter new prefix (leave empty for 'File'): ").strip()
                    if not folder_prefix:
                        folder_prefix = "File"
                
                # Preguntar si quiere cambiar la numeración
                folder_start_number = current_start
                if input("> Do you want to change the start numbering? [Y/N]: ").strip().lower() == 'y':
                    folder_start_number = int(input("> Start numbering from: ").strip())
                
                print(f"\nRenaming files with prefix '{folder_prefix}' starting from {folder_start_number}...")
                print("-" * 50)
                
                # Renombrar los archivos
                for i, file in enumerate(sorted(files)):
                    old_path = os.path.join(current_path, file)
                    extension = os.path.splitext(file)[1]
                    new_filename = f"{folder_prefix}{folder_start_number + i}{extension}"
                    new_path = os.path.join(current_path, new_filename)
                    
                    print(f"  {file:<30} -> {new_filename}")
                    
                    result_path = handler.handle_duplicate(old_path, new_path)
                    if result_path != old_path:
                        total_files_renamed += 1
                
                print("-" * 50)
                print(f"Finished processing this folder.")
            
            # Después de procesar los archivos, buscar subcarpetas
            subdirs = [d for d in os.listdir(current_path) 
                      if os.path.isdir(os.path.join(current_path, d))]
            
            if subdirs:
                # Contar archivos en cada subcarpeta
                subfolders_info = []
                for subdir in subdirs:
                    subdir_path = os.path.join(current_path, subdir)
                    file_count = len([f for f in os.listdir(subdir_path) 
                                    if os.path.isfile(os.path.join(subdir_path, f))])
                    if file_count > 0:  # Solo mostrar subcarpetas con archivos
                        subfolders_info.append({
                            'name': subdir,
                            'path': subdir_path,
                            'count': file_count
                        })
                
                if subfolders_info:
                    print(f"\nFound {len(subfolders_info)} subfolder(s) with files:")
                    for i, info in enumerate(subfolders_info, 1):
                        print(f"  {i}. {info['name']} ({info['count']} files)")
                    
                    choice = input("\nDo you want to rename files in these subfolders? [Y/N]: ").strip().lower()
                    
                    if choice == 'y':
                        print("\nWhich subfolders do you want to process?")
                        print("  A. All subfolders")
                        print("  S. Select specific subfolders")
                        print("  N. None")
                        sub_choice = input("Choice [A/S/N]: ").strip().upper()
                        
                        selected_folders = []
                        
                        if sub_choice == 'A':
                            selected_folders = subfolders_info
                        elif sub_choice == 'S':
                            print("\nEnter subfolder numbers separated by commas (e.g., 1,3,5):")
                            numbers = input("Subfolders: ").strip()
                            
                            try:
                                indices = [int(n.strip()) - 1 for n in numbers.split(',')]
                                for idx in indices:
                                    if 0 <= idx < len(subfolders_info):
                                        selected_folders.append(subfolders_info[idx])
                            except:
                                print("Invalid selection. Skipping subfolders.")
                        
                        # Procesar las subcarpetas seleccionadas recursivamente
                        for folder_info in selected_folders:
                            process_folder_level(folder_info['path'], None, 1)
        
        # Iniciar el procesamiento desde la carpeta principal
        process_folder_level(directory, prefix, start_number)
        
        # Guardar operaciones para rollback
        if handler.operations:
            handler.save_operations(MAPPING_FILE)
            print(f"\n" + "="*60)
            print(f"OPERATION COMPLETED!")
            print(f"Summary:")
            print(f"   - Total files renamed: {total_files_renamed}")
            print(f"   - Rollback available: YES (use -r flag)")
            print("="*60)
            log_action(f"Interactive renaming completed. Files renamed: {total_files_renamed}")
        else:
            print("\nNo files were renamed.")
            log_action("No files were renamed.")
    
    except Exception as e:
        print(f"\nError: {e}")
        log_action(f"Rename error: {e}")


def rename_files(directory, prefix, current_start, current_end, new_start, duplicate_strategy="ask"):
    try:
        check_write_permissions(directory)
        
        # Listar los archivos en la carpeta
        files = sorted(os.listdir(directory))
        
        if not files:
            print(f"Warning: The directory '{directory}' is empty.")
            sys.exit(1)
        
        # Filtrar archivos con o sin prefijo
        current_files = [f for f in files if 
                 (prefix and f.startswith(prefix) and current_start <= int(f[len(prefix):].split('.')[0]) <= current_end) or
                 (not prefix and f.split('.')[0].isdigit() and current_start <= int(f.split('.')[0]) <= current_end)]
        
        log_action("Command: " + ' '.join(sys.argv))
        
        # Mostrar resumen de la operación
        print("\n" + "="*60)
        print("RENAME OPERATION SUMMARY")
        print("="*60)
        print(f"Directory: {directory}")
        print(f"Prefix: {prefix or '(no prefix)'}")
        print(f"Range: {prefix or ''}{current_start} to {prefix or ''}{current_end}")
        print(f"New numbering: starting from {new_start}")
        print(f"Duplicate strategy: {duplicate_strategy}")
        print(f"Files found in range: {len(current_files)}")
        print("="*60)
        
        # Detectar archivos faltantes
        missing_files = [f"{prefix or ''}{i}" for i in range(current_start, current_end + 1) 
                         if not any(f.startswith(f"{prefix or ''}{i}.") for f in files)]

        if missing_files:
            print(f"\nWarning: The following files are missing: {', '.join(missing_files)}")
            log_action(f"Warning: The following files are missing: {', '.join(missing_files)}")
            confirm = input("\nDo you want to continue renaming the available files? (Y/N): ")
            log_action(f"User selected: {confirm}")

            if confirm.lower() != 'y':
                print("Operation cancelled.")
                log_action("Operation cancelled by user.")
                sys.exit(1)

        # Mostrar preview de cambios
        print("\nPREVIEW OF CHANGES:")
        print("-" * 50)
        current_files.sort(key=lambda x: int(x[len(prefix or ''):].split('.')[0]))
        
        for i, file in enumerate(current_files):
            extension = os.path.splitext(file)[1]
            new_filename = f"{prefix or ''}{new_start + i}{extension}"
            print(f"  {file:<25} -> {new_filename}")
        print("-" * 50)
        
        # Confirmar antes de proceder
        if input("\nProceed with renaming? (Y/N): ").lower() != 'y':
            print("Operation cancelled by user.")
            sys.exit(0)
        
        print("\nRENAMING IN PROGRESS...")
        print("-" * 50)
        
        handler = DuplicateHandler(duplicate_strategy)
        files_renamed = 0
        files_skipped = 0
        
        # Renombrar los archivos en orden inverso para evitar conflictos
        for i, file in enumerate(reversed(current_files)):
            old_path = os.path.join(directory, file)
            extension = os.path.splitext(file)[1]
            new_filename = f"{prefix or ''}{new_start + len(current_files) - 1 - i}{extension}"
            new_path = os.path.join(directory, new_filename)
            
            print(f"\n  Processing: {file} -> {new_filename}")
            
            result_path = handler.handle_duplicate(old_path, new_path)
            if result_path != old_path:
                files_renamed += 1
                log_action(f"Renamed: {file} -> {os.path.basename(result_path)}")
            else:
                files_skipped += 1

        # Guardar operaciones para rollback
        print("-" * 50)
        
        if handler.operations:
            handler.save_operations(MAPPING_FILE)
            print(f"\nOPERATION COMPLETED!")
            print(f"Summary:")
            print(f"   - Files renamed: {files_renamed}")
            print(f"   - Files skipped: {files_skipped}")
            print(f"   - Rollback available: YES (use -r flag)")
            log_action(f"Renaming completed. Files renamed: {files_renamed}, skipped: {files_skipped}")
        else:
            print(f"\nNo files were renamed.")
            log_action(f"No files were renamed.")

    except Exception as e:
        print(f"\nError: {e}")
        log_action(f"Rename error: {e}")


def rollback(directory):
    """Revierte TODAS las operaciones, incluyendo backups y sobrescrituras"""
    try:
        directory = os.path.abspath(directory)
        check_write_permissions(directory)
        
        # Verificar si existe el archivo de mapeo
        if not os.path.exists(MAPPING_FILE):
            print("\nError: No rollback mapping available.")
            print("(No previous rename operation found)")
            return
        
        log_action("Command: " + ' '.join(sys.argv))
        
        # Leer el archivo de mapeo
        with open(MAPPING_FILE, "r") as f:
            data = json.load(f)
        
        operations = [RenameOperation.from_dict(op) for op in data["operations"]]
        
        if not operations:
            print("\nThe mapping file is empty. There is nothing to revert.")
            return
        
        print("\n" + "="*60)
        print("ROLLBACK OPERATION")
        print("="*60)
        print(f"Directory: {directory}")
        print(f"Operations to revert: {len(operations)}")
        print(f"Original operation time: {data['timestamp']}")
        print("="*60)
        
        if input("\nProceed with rollback? (Y/N): ").lower() != 'y':
            print("Rollback cancelled by user.")
            return
        
        print("\nREVERTING CHANGES...")
        print("-" * 50)
        
        successful_rollbacks = 0
        failed_rollbacks = 0
        
        # Revertir cada operación en orden inverso
        for op in reversed(operations):
            try:
                if op.operation_type == "rename":
                    # Renombrado simple: revertir el nombre
                    if os.path.exists(op.new_path):
                        os.rename(op.new_path, op.old_path)
                        print(f"[OK] Reverted: {os.path.basename(op.new_path)} -> {os.path.basename(op.old_path)}")
                        successful_rollbacks += 1
                    else:
                        print(f"[SKIP] File not found: {os.path.basename(op.new_path)}")
                        failed_rollbacks += 1
                
                elif op.operation_type == "backup":
                    # Restaurar el archivo del backup
                    if os.path.exists(op.new_path):
                        os.rename(op.new_path, op.old_path)
                        print(f"[OK] Reverted: {os.path.basename(op.new_path)} -> {os.path.basename(op.old_path)}")
                    
                    if op.backup_path and os.path.exists(op.backup_path):
                        # Restaurar el archivo original que fue respaldado
                        shutil.move(op.backup_path, op.new_path)
                        print(f"[OK] Restored from backup: {os.path.basename(op.new_path)}")
                    
                    successful_rollbacks += 1
                
                elif op.operation_type == "overwrite":
                    # Restaurar archivo sobrescrito
                    if os.path.exists(op.new_path):
                        os.rename(op.new_path, op.old_path)
                        print(f"[OK] Reverted: {os.path.basename(op.new_path)} -> {os.path.basename(op.old_path)}")
                    
                    if op.backup_path and os.path.exists(op.backup_path):
                        # Restaurar el archivo que fue sobrescrito
                        shutil.move(op.backup_path, op.new_path)
                        print(f"[OK] Restored overwritten file: {os.path.basename(op.new_path)}")
                    
                    successful_rollbacks += 1
                
            except Exception as e:
                print(f"[ERROR] Failed to revert {os.path.basename(op.new_path)}: {e}")
                failed_rollbacks += 1
                log_action(f"Error during rollback: {e}")
        
        print("-" * 50)
        
        # Limpiar directorios de backup si están vacíos
        backup_dir = os.path.join(directory, ".rename_backups")
        if os.path.exists(backup_dir):
            try:
                # Eliminar subdirectorios vacíos
                for root, dirs, files in os.walk(backup_dir, topdown=False):
                    if not files and not dirs:
                        os.rmdir(root)
                print("[OK] Cleaned up backup directories")
            except:
                pass
        
        # Eliminar el archivo de mapeo después del rollback exitoso
        os.remove(MAPPING_FILE)
        
        print(f"\nROLLBACK COMPLETED!")
        print(f"Summary:")
        print(f"   - Successful rollbacks: {successful_rollbacks}")
        print(f"   - Failed rollbacks: {failed_rollbacks}")
        print(f"   - Mapping file removed: YES")
        
        log_action(f"Rollback completed. Success: {successful_rollbacks}, Failed: {failed_rollbacks}")
    
    except Exception as e:
        print(f"\nRollback error: {e}")
        log_action(f"Rollback error: {e}")


if __name__ == "__main__":
    # Custom description with better formatting
    description = """Batch file renaming tool with rollback functionality – efficient, simple, and powerful.

Rename multiple files with custom prefixes and numbering, handle duplicates intelligently,
and rollback changes when needed. Perfect for organizing photos, documents, and any file collections."""
    
    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=False  # We'll handle help manually for custom formatting
    )
    
    parser.add_argument("-h", "--help", action="store_true", help="Show this help message and exit")
    parser.add_argument("-l", "--location", help="Folder where files are located.")
    parser.add_argument("-p", "--prefix", help="Prefix of files (optional).")
    parser.add_argument("-a", "--all", action="store_true", help="Interactive rename for all files in directory and subfolders.")
    parser.add_argument("-cs", "--current-start", type=int, help="Start of current range.")
    parser.add_argument("-ce", "--current-end", type=int, help="End of current range.")
    parser.add_argument("-ns", "--new-start", type=int, help="New start point for renaming.")
    parser.add_argument("-r", "--rollback", action="store_true", help="Revert last renaming operation.")
    parser.add_argument("-ds", "--duplicate-strategy", 
                       choices=['skip', 'suffix', 'backup', 'overwrite', 'ask'],
                       default='ask',
                       help="How to handle duplicate filenames (default: ask)")
    
    # Handle special arguments first
    if len(sys.argv) == 1 or '--help' in sys.argv or '-h' in sys.argv:
        print(BANNER)
        print("\n" + description + "\n")
        print("Usage: r3namex.py [-h] [-l LOCATION] [-p PREFIX] [-a] [-cs CURRENT_START]")
        print("                  [-ce CURRENT_END] [-ns NEW_START] [-r]")
        print("                  [-ds {skip,suffix,backup,overwrite,ask}]\n")
        print("Options:")
        print("  -h, --help            Show this help message and exit")
        print("  -l, --location        Folder where files are located")
        print("  -p, --prefix          Prefix of files (optional)")
        print("  -a, --all             Interactive rename for all files in directory and subfolders")
        print("  -cs, --current-start  Start of current range")
        print("  -ce, --current-end    End of current range")
        print("  -ns, --new-start      New start point for renaming")
        print("  -r, --rollback        Revert last renaming operation")
        print("  -ds, --duplicate-strategy")
        print("                        How to handle duplicate filenames (default: ask)")
        print("                        Choices: skip, suffix, backup, overwrite, ask")
        print(EXAMPLES)
        sys.exit(0)
    
    if '--version' in sys.argv or '-v' in sys.argv:
        show_version()
        sys.exit(0)
    
    if '--update' in sys.argv or '-u' in sys.argv:
        check_for_updates()
        sys.exit(0)
    
    try:
        args = parser.parse_args()

        # Nueva lógica para el renombrado interactivo
        if args.all:
            if not args.location:
                args.location = input("Enter the path to the folder where the files are located: ").strip()
            prefix = args.prefix or "File"
            start_number = args.new_start if args.new_start else 1
            rename_all_files_interactive(args.location, prefix, start_number, args.duplicate_strategy)
            sys.exit(0)  
 
        # Preguntar por la ruta si no se proporciona
        if not args.location:
            args.location = input("Enter the path to the folder where the files are located: ").strip()
                     
        # Si se solicita rollback, ejecutarlo inmediatamente
        if args.rollback:
            rollback(args.location)
            sys.exit(0)
        
        # Validación para renombrado
        missing_params = []

        if args.current_start is None:
            missing_params.append("-cs/--current-start")
        if args.current_end is None:
            missing_params.append("-ce/--current-end")
        if args.new_start is None:
            missing_params.append("-ns/--new-start")

        if missing_params:
            print(f"Error: the following arguments are required: {', '.join(missing_params)}")
            sys.exit(1)

        # Ejecutar renumerado
        rename_files(args.location, args.prefix, args.current_start, args.current_end, 
                    args.new_start, args.duplicate_strategy)

    except argparse.ArgumentError as e:
        print(f"Arguments error: {e}")
        parser.print_help()

    except Exception as ex:
        print(f"Error: {ex}")
        log_action(f"Error: {ex}")
        parser.print_help()
