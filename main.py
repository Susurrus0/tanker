import os
import shutil
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class FolderCopyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tanker")
        self.root.geometry("450x350")
        self.root.resizable(False, False)

        style = ttk.Style()
        style.theme_use("clam")  # Use a modern theme

        style.configure("TLabel", font=("Helvetica", 12, "bold"), padding=5)
        style.configure("TButton", font=("Helvetica", 11), padding=6, relief="flat", background="#0056b3", foreground="white")
        style.configure("TCheckbutton", font=("Helvetica", 11))
        style.map("TButton", background=[('active', '#003f88')])

        # Main Frame
        main_frame = ttk.Frame(root, padding="10 10 10 10")
        main_frame.grid(row=0, column=0, sticky='nsew')

        # Frame for Source Directory
        source_frame = ttk.Frame(main_frame)
        source_frame.grid(row=0, column=0, pady=5, padx=5, sticky='ew')

        self.source_label = ttk.Label(source_frame, text="Source directory:")
        self.source_label.grid(row=0, column=0, sticky='w')
        self.source_entry = ttk.Entry(source_frame, width=40, font=("Helvetica", 11))
        self.source_entry.grid(row=1, column=0, padx=5, sticky='ew')
        self.source_button = ttk.Button(source_frame, text="📁 Browse", command=self.browse_source)
        self.source_button.grid(row=1, column=1, padx=5)

        # Frame for Destination Directory
        dest_frame = ttk.Frame(main_frame)
        dest_frame.grid(row=1, column=0, pady=5, padx=5, sticky='ew')

        self.dest_label = ttk.Label(dest_frame, text="Destination directory:")
        self.dest_label.grid(row=0, column=0, sticky='w')
        self.dest_entry = ttk.Entry(dest_frame, width=40, font=("Helvetica", 11))
        self.dest_entry.grid(row=1, column=0, padx=5, sticky='ew')
        self.dest_button = ttk.Button(dest_frame, text="📁 Browse", command=self.browse_destination)
        self.dest_button.grid(row=1, column=1, padx=5)

        # Frame for Exclude Files
        exclude_frame = ttk.Frame(main_frame)
        exclude_frame.grid(row=2, column=0, pady=5, padx=5, sticky='ew')

        self.exclude_label = ttk.Label(exclude_frame, text="Files to exclude (comma-separated):")
        self.exclude_label.grid(row=0, column=0, sticky='w')
        self.exclude_entry = ttk.Entry(exclude_frame, width=40, font=("Helvetica", 11))
        self.exclude_entry.insert(0, "exclude_this_file.txt")
        self.exclude_entry.grid(row=1, column=0, padx=5, sticky='ew')

        # Toggle for omitting files
        self.omit_files_var = tk.BooleanVar(value=False)  # Default to off
        self.omit_files_check = ttk.Checkbutton(main_frame, text="Omit specified files", variable=self.omit_files_var, command=self.toggle_exclude_entry)
        self.omit_files_check.grid(row=3, column=0, pady=10, padx=5, sticky='w')

        # Copy Button
        self.copy_button = ttk.Button(main_frame, text="📂 Copy folders", command=self.copy_folders)
        self.copy_button.grid(row=4, column=0, pady=20)

        # Tooltips
        self.create_tooltip(self.source_button, "Select the source directory")
        self.create_tooltip(self.dest_button, "Select the destination directory")
        self.create_tooltip(self.copy_button, "Copy folders from source to destination")

        # Initial state
        self.toggle_exclude_entry()

    def create_tooltip(self, widget, text):
        tooltip = Tooltip(widget, text)
        widget.bind("<Enter>", tooltip.show)
        widget.bind("<Leave>", tooltip.hide)

    def toggle_exclude_entry(self):
        if self.omit_files_var.get():
            self.exclude_entry.config(state='normal')
            self.exclude_label.config(state='normal')
        else:
            self.exclude_entry.config(state='disabled')
            self.exclude_label.config(state='disabled')

    def browse_source(self):
        directory = self.open_file_manager_for_directory()
        if directory:
            self.source_entry.delete(0, tk.END)
            self.source_entry.insert(0, directory)

    def browse_destination(self):
        directory = self.open_file_manager_for_directory()
        if directory:
            self.dest_entry.delete(0, tk.END)
            self.dest_entry.insert(0, directory)

    def open_file_manager_for_directory(self):
        return filedialog.askdirectory()

    def copy_folders(self):
        source_directory = self.source_entry.get()
        destination_directory = self.dest_entry.get()
        exclude_files = [name.strip() for name in self.exclude_entry.get().split(',')]

        if not source_directory or not destination_directory:
            messagebox.showerror("Error", "Both source and destination directories must be selected.")
            return

        try:
            self.perform_copy(source_directory, destination_directory, exclude_files, self.omit_files_var.get())
            messagebox.showinfo("Success", "Folders copied successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def perform_copy(self, source_directory, destination_directory, exclude_files, omit_files):
        subfolders = [f for f in os.listdir(source_directory) if os.path.isdir(os.path.join(source_directory, f))]

        for subfolder in subfolders:
            subfolder_path = os.path.join(source_directory, subfolder)
            items = os.listdir(subfolder_path)

            for item in items:
                if omit_files and item in exclude_files:
                    print(f"Skipping excluded file: {item}")
                    continue

                item_path = os.path.join(subfolder_path, item)
                destination_item_path = os.path.join(destination_directory, item)

                if os.path.exists(destination_item_path):
                    if not os.path.isdir(destination_item_path):
                        print(f"File already exists, skipping: {destination_item_path}")
                        continue

                if os.path.isdir(item_path):
                    shutil.copytree(item_path, destination_item_path, dirs_exist_ok=True)
                else:
                    shutil.copy2(item_path, destination_item_path)

class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None

    def show(self, event):
        if self.tooltip:
            return
        x, y, _cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        self.tooltip = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, background="lightyellow", relief="solid", borderwidth=1, font=("Helvetica", 10))
        label.pack()

    def hide(self, event):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

if __name__ == "__main__":
    root = tk.Tk()
    app = FolderCopyApp(root)
    root.mainloop()
