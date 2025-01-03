import os
import argparse
import sys
from datetime import datetime
from shlex import join

LOG_FILE = "logs.log"
MAPPING_FILE = "backup_mapping.txt"

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

"""

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

def rename_all_files(directory, prefix, start_number):
    try:
        check_write_permissions(directory)
        
        files = sorted(os.listdir(directory))
        
        if not files:
            print(f"Warning: The directory '{directory}' is empty.")
            sys.exit(1)
        
        log_action("Command: " + ' '.join(sys.argv))
        
        files_renamed = 0
        mapping_entries = []
        
        for i, file in enumerate(files):
            old_path = os.path.join(directory, file)
            extension = file.split('.')[-1] if '.' in file else ''
            new_filename = f"{prefix}{start_number + i}.{extension}"
            new_path = os.path.join(directory, new_filename)
            
            os.rename(old_path, new_path)
            mapping_entries.append(f"{new_filename} -> {file}\n")
            
            print(f"Renamed: {file} -> {new_filename}")
            log_action(f"Renamed: {file} -> {new_filename}")
            
            files_renamed += 1
        
        # Guardar el mapeo para rollback
        if files_renamed > 0:
            with open(MAPPING_FILE, "w") as backup:
                backup.writelines(mapping_entries)
            print(f"Renaming completed. Total files renamed: {files_renamed}.")
            log_action(f"Renaming completed. Total files renamed: {files_renamed}.")
        else:
            print("No files were renamed.")
            log_action("No files were renamed.")
    
    except Exception as e:
        print(f"Error: {e}")
        log_action(f"Renamed error: {e}")





def rename_files(directory, prefix, current_start, current_end, new_start):
    try:
    
        check_write_permissions(directory)
        # Listar los archivos en la carpeta
        files = sorted(os.listdir(directory))
        
        # Validar si la carpeta está vacía
        if not files:
            print(f"Warning: The directory '{directory}' is empty.")
            sys.exit(1)
        
        # Filtrar archivos con o sin prefijo
        current_files = [f for f in files if 
                 (prefix and f.startswith(prefix) and current_start <= int(f[len(prefix):].split('.')[0]) <= current_end) or
                 (not prefix and f.split('.')[0].isdigit() and current_start <= int(f.split('.')[0]) <= current_end)]
        
        log_action("Command: " + ' '.join(sys.argv))
        
        # Detectar archivos faltantes en el rango
        missing_files = [f"{prefix or ''}{i}" for i in range(current_start, current_end + 1) 
                         if not any(f.startswith(f"{prefix or ''}{i}.") for f in files)]

        # Si faltan archivos, advertir al usuario
        if missing_files:
            print(f"Warning: The following files are missing: {', '.join(missing_files)}")
            log_action(f"Warning: The following files are missing: {', '.join(missing_files)}")
            confirm = input("Do you want to continue renaming the available files? (Y/N): ")
            log_action(f"User selected: {confirm}")  # Registrar respuesta del usuario

            if confirm.lower() != 'y':
                print("Operation cancelled.")
                log_action("Operation cancelled by user.")
                sys.exit(1)

        # Ordenar los archivos por su número actual
        current_files.sort(key=lambda x: int(x[len(prefix or ''):].split('.')[0]))


        # Verificar si hay suficientes archivos para renombrar
        if len(current_files) != (current_end - current_start + 1):
            print("Warning: The current range does not match the number of available files.")
            log_action("Warning: The current range does not match the number of available files.")
        # Renombrar los archivos en orden inverso para evitar conflictos
        
        
        files_renamed = 0  # Contador de archivos renombrados
        mapping_entries = []
        
        # Renombrar los archivos en orden inverso para evitar conflictos
        for i, file in enumerate(reversed(current_files)):
            old_path = os.path.join(directory, file)
            extension = file.split('.')[-1] if '.' in file else ''
            new_filename = f"{prefix or ''}{new_start + len(current_files) - 1 - i}.{extension}"
            new_path = os.path.join(directory, new_filename)
            os.rename(old_path, new_path)
            mapping_entries.append(f"{new_filename} -> {file}\n") 
            
            print(f"Renamed: {file} -> {new_filename}")
            log_action(f"Renamed: {file} -> {new_filename}")

            files_renamed += 1  # Incrementar contador si se renombra un archivo

        # Mensaje final basado en archivos renombrados
        if files_renamed > 0:
        # Guardar el mapeo para rollback
            with open(MAPPING_FILE, "w") as backup:
                backup.writelines(mapping_entries)  # Escribir todos los mapeos
            print(f"Renaming completed. Total files renamed: {files_renamed}.")
            log_action(f"Renaming completed. Total files renamed: {files_renamed}.")
        else:
            print(f"No files were renamed because the files {', '.join(missing_files)} are missing.")
            log_action(f"No files were renamed because the files {', '.join(missing_files)} are missing.")

    except Exception as e:
        print(f"Error: {e}")
        log_action(f"Renamed error: {e}")


def rollback(directory):
    try:

        check_write_permissions(directory)
        # Verificar si existe el archivo de mapeo
        if not os.path.exists(MAPPING_FILE):
            print("Error: No rollback mapping available.")
            return
        log_action("Commad: " + ' '.join(sys.argv))
        # Leer el archivo de mapeo
        with open(MAPPING_FILE, "r") as backup:
            lines = backup.readlines()
        # Verificar que el archivo de mapeo no esté vacío
        if not lines:
            print("The mapping file is empty. There is nothing to revert.")
            return
                
        # Revertir cada archivo al nombre original (inverso)
        for line in reversed(lines):
            new_name, old_name = line.strip().split(" -> ")
            old_path = os.path.join(directory, old_name)
            new_path = os.path.join(directory, new_name)
            
            if os.path.exists(new_path):
                os.rename(new_path, old_path)
                print(f"Rollback: {new_name} -> {old_name}")
                
                log_action(f"Rollback: {new_name} -> {old_name}")    
            else:
                print(f"Warning: {new_name} does not exist, rollback skipped.")
                
        
        # Eliminar el archivo de mapeo después del rollback
        os.remove(MAPPING_FILE)
        print("Rollback completed.")
        log_action("Rollback completed.")
        
    except Exception as e:
        print(f"Rollback error: {e}")
        log_action(f"Rollback error: {e}")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Batch file renaming tool with rollback functionality – efficient, simple, and powerful.\n")
    
    parser.add_argument("-l", "--location", help="Folder where files are located.")
    parser.add_argument("-p", "--prefix", help="Prefix of files (optional).")
    parser.add_argument("-a", "--all", action="store_true", help="Rename all files in the directory.")
    parser.add_argument("-cs", "--current_start", type=int, help="Start of current range.")
    parser.add_argument("-ce", "--current_end", type=int, help="End of current range.")
    parser.add_argument("-ns", "--new_start", type=int, help="New start point for renaming.")
    parser.add_argument("-r", "--rollback", action="store_true", help="Revert last renaming operation.")
    
    if len(sys.argv) == 1:
        parser.print_help()
        print(EXAMPLES)
        sys.exit(0)
    
    if '--help' in sys.argv or '-h' in sys.argv:
        parser.print_help()
        print(EXAMPLES)
        sys.exit(0)
    
    
    try:
        args = parser.parse_args()
        
        # Nueva lógica para renombrar todos los archivos
        if args.all:
            prefix = args.prefix or "File"  # Usa "File" si no se especifica prefijo
            start_number = args.new_start if args.new_start else 1
            
            rename_all_files(args.location, prefix, start_number)
            sys.exit(0)  # Terminar después de renombrar todo
        
 
        # Preguntar por la ruta si no se proporciona como argumento
        if not args.location:
            args.location = input("Enter the path to the folder where the files are located: ").strip()
                     
       # Si se solicita rollback, ejecutarlo inmediatamente
        if args.rollback:
            rollback(args.location)
            sys.exit(0)
        
        # Validación para renombrado
        missing_params = []

        if args.current_start is None:
            missing_params.append("-cs/--current_start")
        if args.current_end is None:
            missing_params.append("-ce/--current_end")
        if args.new_start is None:
            missing_params.append("-ns/--new_start")

        if missing_params:
            print(f"Error: the following arguments are required: {', '.join(missing_params)}")
            sys.exit(1)

        # Ejecutar renumerado
        rename_files(args.location, args.prefix, args.current_start, args.current_end, args.new_start)
        

    except argparse.ArgumentError as e:
        print(f"Arguments error: {e}")
        parser.print_help()

    except Exception as ex:
        print(f"Error: {ex}")
        print(error_message)
        log_action(error_message)  # Registra el error en el log
        parser.print_help()
