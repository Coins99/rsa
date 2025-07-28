import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import subprocess
import os
import sys
import threading

class RSAFileGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("RSA File Encryption - C Backend")
        self.root.geometry("700x600")
        
        # Variables
        self.input_file_path = tk.StringVar()
        self.c_executable_path = tk.StringVar()
        
        # Auto-find executable
        self.auto_find_executable()
        
        self.create_widgets()
    
    def auto_find_executable(self):
        """Automatically find the C executable"""
        possible_locations = [
            "build/rsa_encrypt.exe",  # Standard build location
            "build\\rsa_encrypt.exe",  # Windows path
            "rsa_encrypt.exe",  # Current directory
            "src/rsa_encrypt.exe",  # In src folder
            "src\\rsa_encrypt.exe",  # Windows src path
            "../build/rsa_encrypt.exe",  # One level up
            "../build\\rsa_encrypt.exe",  # Windows one level up
        ]
        
        # Also check for non-Windows executable
        if os.name != 'nt':
            possible_locations.extend([
                "build/rsa_encrypt",
                "rsa_encrypt",
                "src/rsa_encrypt",
                "../build/rsa_encrypt"
            ])
        
        for location in possible_locations:
            if os.path.isfile(location):
                self.c_executable_path.set(os.path.abspath(location))
                return
        
        # If not found, set default name
        default_name = "rsa_encrypt.exe" if os.name == 'nt' else "rsa_encrypt"
        self.c_executable_path.set(default_name)
    
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="RSA File Encryption Tool", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # C Executable path (read-only display)
        ttk.Label(main_frame, text="C Executable:").grid(row=1, column=0, sticky=tk.W, pady=5)
        exe_entry = ttk.Entry(main_frame, textvariable=self.c_executable_path, width=50, state="readonly")
        exe_entry.grid(row=1, column=1, padx=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_executable).grid(row=1, column=2)
        
        # Executable status
        self.exe_status_label = ttk.Label(main_frame, text="Checking executable...", foreground="blue")
        self.exe_status_label.grid(row=2, column=0, columnspan=3, pady=(0, 10))
        
        # Input file selection
        ttk.Label(main_frame, text="Select File to Encrypt:").grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.input_file_path, width=50).grid(row=3, column=1, padx=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_input_file).grid(row=3, column=2)
        
        # Encrypt button (initially disabled)
        self.encrypt_btn = ttk.Button(main_frame, text="🔒 Encrypt File", 
                                     command=self.encrypt_file_threaded, 
                                     state=tk.DISABLED,
                                     style="Accent.TButton")
        self.encrypt_btn.grid(row=4, column=0, columnspan=3, pady=20)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # Output display
        output_frame = ttk.LabelFrame(main_frame, text="Output", padding="10")
        output_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Text widget with scrollbar
        text_frame = ttk.Frame(output_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.output_text = tk.Text(text_frame, height=15, width=80, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.output_text.yview)
        self.output_text.configure(yscrollcommand=scrollbar.set)
        
        self.output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Status
        self.status_label = ttk.Label(main_frame, text="Ready - Please select a file to encrypt", foreground="blue")
        self.status_label.grid(row=7, column=0, columnspan=3, pady=10)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(6, weight=1)
        
        # Check executable on startup
        self.root.after(100, self.check_executable)
    
    def browse_executable(self):
        filename = filedialog.askopenfilename(
            title="Select RSA executable",
            filetypes=[("Executable files", "*.exe"), ("All files", "*.*")]
        )
        if filename:
            self.c_executable_path.set(filename)
            self.check_executable()
    
    def browse_input_file(self):
        filename = filedialog.askopenfilename(
            title="Select file to encrypt",
            filetypes=[
                ("Text files", "*.txt"),
                ("Document files", "*.doc;*.docx;*.pdf"),
                ("Image files", "*.jpg;*.jpeg;*.png;*.gif;*.bmp"),
                ("All files", "*.*")
            ]
        )
        if filename:
            self.input_file_path.set(filename)
            self.update_encrypt_button_state()
            self.log_output(f"Selected file: {os.path.basename(filename)}")
    
    def log_output(self, message, color="black"):
        """Add message to output text widget"""
        self.output_text.insert(tk.END, message + "\n")
        self.output_text.see(tk.END)
        self.root.update_idletasks()
    
    def check_executable(self):
        """Check if the C executable exists and is runnable"""
        exe_path = self.c_executable_path.get()
        
        if not exe_path:
            self.exe_status_label.config(text="❌ No executable specified", foreground="red")
            return
        
        # Check if file exists
        if not os.path.isfile(exe_path):
            self.exe_status_label.config(text="❌ Executable not found", foreground="red")
            self.log_output(f"Error: Executable '{exe_path}' not found")
            return
        
        # Test the executable (just check it runs, not output)
        try:
            result = subprocess.run([exe_path], capture_output=True, text=True, timeout=5)
            if result.returncode == 0 or result.returncode == 1:
                self.exe_status_label.config(text="✅ Executable ready", foreground="green")
                self.log_output("✓ C executable found and runnable")
                self.update_encrypt_button_state()
            else:
                self.exe_status_label.config(text="❌ Executable error", foreground="red")
                self.log_output("Error: Executable test failed (nonzero exit code)")
        except subprocess.TimeoutExpired:
            self.exe_status_label.config(text="❌ Executable timeout", foreground="red")
            self.log_output("Error: Executable test timed out")
        except Exception as e:
            self.exe_status_label.config(text="❌ Executable error", foreground="red")
            self.log_output(f"Error testing executable: {str(e)}")
    
    def update_encrypt_button_state(self):
        """Enable encrypt button only when both executable and file are ready"""
        exe_ready = "✅" in self.exe_status_label.cget("text")
        file_selected = bool(self.input_file_path.get() and os.path.isfile(self.input_file_path.get()))
        
        if exe_ready and file_selected:
            self.encrypt_btn.config(state=tk.NORMAL)
            self.status_label.config(text="Ready to encrypt!", foreground="green")
        else:
            self.encrypt_btn.config(state=tk.DISABLED)
            if not exe_ready:
                self.status_label.config(text="Waiting for executable...", foreground="orange")
            elif not file_selected:
                self.status_label.config(text="Please select a file to encrypt", foreground="blue")
    
    def generate_output_paths(self):
        """Generate output file paths based on input file"""
        if not self.input_file_path.get():
            return None, None
        
        input_file = self.input_file_path.get()
        base_name = os.path.splitext(input_file)[0]
        directory = os.path.dirname(input_file)
        
        # Generate unique filenames
        encrypted_file = os.path.join(directory, f"{os.path.basename(base_name)}_encrypted.enc")
        key_file = os.path.join(directory, f"{os.path.basename(base_name)}_keys.key")
        
        # Make sure files don't already exist (add counter if they do)
        counter = 1
        original_encrypted = encrypted_file
        original_key = key_file
        
        while os.path.exists(encrypted_file) or os.path.exists(key_file):
            base_encrypted = os.path.splitext(original_encrypted)[0]
            base_key = os.path.splitext(original_key)[0]
            encrypted_file = f"{base_encrypted}_{counter}.enc"
            key_file = f"{base_key}_{counter}.key"
            counter += 1
        
        return encrypted_file, key_file
    
    def run_encryption(self):
        """Run the C program for encryption"""
        try:
            # Generate output paths
            encrypted_file, key_file = self.generate_output_paths()
            if not encrypted_file or not key_file:
                raise Exception("Could not generate output file paths")
            
            cmd = [
                self.c_executable_path.get(),
                "encrypt",
                self.input_file_path.get(),
                encrypted_file,
                key_file
            ]
            
            self.log_output(f"🔄 Starting encryption...")
            self.log_output(f"Input: {os.path.basename(self.input_file_path.get())}")
            self.log_output(f"Output: {os.path.basename(encrypted_file)}")
            self.log_output(f"Keys: {os.path.basename(key_file)}")
            self.log_output("")
            
            # Run the C program
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60  # 60 second timeout
            )
            
            # Log stdout
            if result.stdout:
                self.log_output("--- Encryption Results ---")
                self.log_output(result.stdout.strip())
            
            # Log stderr if there are errors
            if result.stderr:
                self.log_output("--- Error Output ---")
                self.log_output(result.stderr.strip())
            
            # Check return code
            if result.returncode == 0:
                self.log_output("")
                self.log_output("🎉 SUCCESS! File encrypted successfully!")
                self.log_output(f"📁 Encrypted file: {encrypted_file}")
                self.log_output(f"🔑 Key file: {key_file}")
                self.log_output("")
                self.log_output("⚠️  IMPORTANT: Keep the key file safe! You need it to decrypt the file.")
                
                self.status_label.config(text="Encryption completed successfully!", foreground="green")
                messagebox.showinfo("Success", 
                    f"File encrypted successfully!\n\n"
                    f"Encrypted file: {os.path.basename(encrypted_file)}\n"
                    f"Key file: {os.path.basename(key_file)}\n\n"
                    f"Keep the key file safe - you need it to decrypt!")
                
                # Show key file info
                self.show_key_info(key_file)
                
            else:
                self.log_output("❌ Encryption failed!")
                self.status_label.config(text="Encryption failed", foreground="red")
                messagebox.showerror("Error", "Encryption failed. Check output for details.")
        
        except subprocess.TimeoutExpired:
            self.log_output("❌ Encryption timed out")
            self.status_label.config(text="Encryption timed out", foreground="red")
            messagebox.showerror("Error", "Encryption operation timed out")
        
        except Exception as e:
            self.log_output(f"❌ Error during encryption: {str(e)}")
            self.status_label.config(text="Encryption error", foreground="red")
            messagebox.showerror("Error", f"Error during encryption: {str(e)}")
        
        finally:
            # Stop progress bar and re-enable button
            self.progress.stop()
            self.encrypt_btn.config(state=tk.NORMAL)
    
    def show_key_info(self, key_file):
        """Display key information from key file"""
        try:
            with open(key_file, 'r') as f:
                key_content = f.read()
                self.log_output("--- RSA Key Information ---")
                self.log_output(key_content.strip())
                self.log_output("--- End of Key Information ---")
        except Exception as e:
            self.log_output(f"Could not read key file: {str(e)}")
    
    def encrypt_file_threaded(self):
        """Encrypt file in a separate thread"""
        # Final validation
        if not self.input_file_path.get() or not os.path.isfile(self.input_file_path.get()):
            messagebox.showerror("Error", "Please select a valid input file")
            return
        
        if not self.c_executable_path.get() or not os.path.isfile(self.c_executable_path.get()):
            messagebox.showerror("Error", "C executable not found")
            return
        
        # Disable button and start progress
        self.encrypt_btn.config(state=tk.DISABLED)
        self.progress.start()
        self.status_label.config(text="Encrypting file...", foreground="blue")
        
        # Clear previous output
        self.output_text.delete(1.0, tk.END)
        
        # Run in thread to prevent GUI freezing
        thread = threading.Thread(target=self.run_encryption)
        thread.daemon = True
        thread.start()
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = RSAFileGUI()
    app.run()