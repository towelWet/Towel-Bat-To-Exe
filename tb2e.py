import tkinter as tk
from tkinter import filedialog, messagebox
import os
import sys
import shutil
import subprocess
from pkg_resources import working_set

def check_and_install_pyinstaller():
    if 'PyInstaller' not in [pkg.key for pkg in working_set]:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])
            return True
        except subprocess.CalledProcessError:
            messagebox.showerror("Error", "Failed to install PyInstaller. Please install it manually using: pip install pyinstaller")
            return False
    return True

def select_batch_file():
    selected_file = filedialog.askopenfilename(filetypes=[("Batch files", "*.bat")])
    if selected_file:
        file_path.set(selected_file)
        validate_and_update_button()

def select_icon_file():
    selected_file = filedialog.askopenfilename(filetypes=[("Icon files", "*.ico")])
    if selected_file:
        icon_path.set(selected_file)
        validate_and_update_button()

def validate_and_update_button():
    batch_file = file_path.get()
    icon_file = icon_path.get()
    if batch_file and batch_file.endswith('.bat') and icon_file and icon_file.endswith('.ico'):
        convert_button.config(state='normal')
    else:
        convert_button.config(state='disabled')

def convert_to_exe():
    if not check_and_install_pyinstaller():
        return
        
    batch_file = file_path.get()
    icon_file = icon_path.get()
    
    if not os.path.exists(batch_file) or not os.path.exists(icon_file):
        messagebox.showerror("Error", "Selected files do not exist.")
        return
    
    # Create a temporary Python script that will run the batch file
    temp_py = os.path.splitext(batch_file)[0] + '_wrapper.py'
    with open(temp_py, 'w') as f:
        f.write(f'''
import subprocess
import os
import sys

def run_batch():
    batch_path = os.path.join(os.path.dirname(sys.executable), "{os.path.basename(batch_file)}")
    subprocess.run(batch_path, shell=True)

if __name__ == '__main__':
    run_batch()
''')

    try:
        # Copy batch file to temp directory
        output_directory = os.path.dirname(batch_file)
        
        # Build command for PyInstaller
        cmd = [
            'pyinstaller',
            '--onefile',
            '--noconsole',
            f'--icon={icon_file}',
            '--clean',
            temp_py
        ]
        
        # Run PyInstaller
        process = subprocess.run(cmd, capture_output=True, text=True)
        
        if process.returncode == 0:
            # Copy the generated EXE from dist folder
            exe_name = os.path.splitext(os.path.basename(batch_file))[0] + '.exe'
            src_exe = os.path.join('dist', os.path.splitext(os.path.basename(temp_py))[0] + '.exe')
            dst_exe = os.path.join(output_directory, exe_name)
            
            shutil.copy2(src_exe, dst_exe)
            
            # Clean up
            for folder in ['build', 'dist', '__pycache__']:
                if os.path.exists(folder):
                    shutil.rmtree(folder)
            if os.path.exists(temp_py):
                os.remove(temp_py)
            spec_file = os.path.splitext(temp_py)[0] + '.spec'
            if os.path.exists(spec_file):
                os.remove(spec_file)
                
            messagebox.showinfo("Success", f"Successfully created:\n{dst_exe}")
        else:
            messagebox.showerror("Error", f"Conversion failed:\n{process.stderr}")
            
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred:\n{str(e)}")
    finally:
        # Ensure temp file is removed
        if os.path.exists(temp_py):
            os.remove(temp_py)

# Create main window
app = tk.Tk()
app.title("Towel Bat2Exe")
app.resizable(False, False)

# Initialize variables
file_path = tk.StringVar()
icon_path = tk.StringVar()

# Create main frame
main_frame = tk.Frame(app, padx=10, pady=10)
main_frame.pack(expand=True, fill='both')

# Batch file selection row
batch_frame = tk.Frame(main_frame)
batch_frame.pack(fill='x', pady=(0, 5))

tk.Label(batch_frame, text="Batch File:").pack(side='left')
tk.Entry(batch_frame, textvariable=file_path, width=50).pack(side='left', padx=5)
tk.Button(batch_frame, text="Browse", command=select_batch_file).pack(side='left')

# Icon file selection row
icon_frame = tk.Frame(main_frame)
icon_frame.pack(fill='x', pady=5)

tk.Label(icon_frame, text="Icon File:  ").pack(side='left')
tk.Entry(icon_frame, textvariable=icon_path, width=50).pack(side='left', padx=5)
tk.Button(icon_frame, text="Browse", command=select_icon_file).pack(side='left')

# Convert button
convert_button = tk.Button(main_frame, text="Convert to EXE", command=convert_to_exe, 
                          state='disabled', width=20)
convert_button.pack(pady=(10, 0))

# Start application
app.mainloop()