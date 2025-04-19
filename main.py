import os
import shutil
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class Tanker:
    def __init__(self, root):
        self.root = root

        # Get screen dimensions
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        # Set a smaller base window size
        base_width = 600
        base_height = 450
        window_width = min(base_width, int(screen_width * 0.5))
        window_height = min(base_height, int(screen_height * 0.5))

        # Center the window
        x_position = (screen_width - window_width) // 2
        y_position = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

        # Set minimum size to prevent the window from being too small
        self.root.minsize(400, 300)

        # Use fixed font size and padding
        font_size = 10
        padding = 8

        self.root.title("Tanker")
        self.root.resizable(True, True)

        style = ttk.Style()
        style.theme_use("clam")  # Use a modern theme

        style.configure("TLabel", font=("Helvetica", font_size, "bold"), padding=padding)
        style.configure("TButton", font=("Helvetica", font_size - 1), padding=padding, relief="flat", background="#0056b3", foreground="white")
        style.configure("TCheckbutton", font=("Helvetica", font_size - 1))
        style.map("TButton", background=[('active', '#003f88')])

        # Add a fancy header
        header_frame = tk.Frame(root, bg="#0056b3", height=50)
        header_frame.pack(fill="x")
        header_label = tk.Label(header_frame, text="Tanker - File Organizer", bg="#0056b3", fg="white", font=("Helvetica", 16, "bold"))
        header_label.pack(pady=10)

        # Main Frame with fixed padding
        main_frame = ttk.Frame(root, padding=f"{padding} {padding} {padding} {padding}")
        main_frame.pack(fill="both", expand=True)

        # Frame for Source Directory
        source_frame = ttk.Frame(main_frame)
        source_frame.grid(row=0, column=0, pady=padding, padx=padding, sticky='ew')

        self.source_label = ttk.Label(source_frame, text="Source directory:")
        self.source_label.grid(row=0, column=0, sticky='w')
        self.source_entry = ttk.Entry(source_frame, font=("Helvetica", font_size - 1))
        self.source_entry.grid(row=1, column=0, padx=padding, sticky='ew')
        self.source_button = ttk.Button(source_frame, text="📁 Browse", command=self.browse_source)
        self.source_button.grid(row=1, column=1, padx=padding)

        # Frame for Destination Directory
        dest_frame = ttk.Frame(main_frame)
        dest_frame.grid(row=1, column=0, pady=padding, padx=padding, sticky='ew')

        self.dest_label = ttk.Label(dest_frame, text="Destination directory:")
        self.dest_label.grid(row=0, column=0, sticky='w')
        self.dest_entry = ttk.Entry(dest_frame, font=("Helvetica", font_size - 1))
        self.dest_entry.grid(row=1, column=0, padx=padding, sticky='ew')
        self.dest_button = ttk.Button(dest_frame, text="📁 Browse", command=self.browse_destination)
        self.dest_button.grid(row=1, column=1, padx=padding)

        # Frame for Exclude Files
        exclude_frame = ttk.Frame(main_frame)
        exclude_frame.grid(row=2, column=0, pady=padding, padx=padding, sticky='ew')

        self.exclude_label = ttk.Label(exclude_frame, text="Files to exclude (comma-separated):")
        self.exclude_label.grid(row=0, column=0, sticky='w')
        self.exclude_entry = ttk.Entry(exclude_frame, font=("Helvetica", font_size - 1))
        self.exclude_entry.insert(0, "exclude_this_file.txt")
        self.exclude_entry.grid(row=1, column=0, padx=padding, sticky='ew')

        # Toggle for omitting files
        self.omit_files_var = tk.BooleanVar(value=False)  # Default to off
        self.omit_files_check = ttk.Checkbutton(main_frame, text="Omit specified files", variable=self.omit_files_var, command=self.toggle_exclude_entry)
        self.omit_files_check.grid(row=3, column=0, pady=padding, padx=padding, sticky='w')

        # Copy Button
        self.copy_button = ttk.Button(main_frame, text="📂 Copy folders", command=self.copy_folders)
        self.copy_button.grid(row=4, column=0, pady=padding)

        # Add a footer
        footer_frame = tk.Frame(root, bg="#f0f0f0", height=30)
        footer_frame.pack(fill="x")
        footer_label = tk.Label(footer_frame, text="© 2025 Tanker - All rights reserved", bg="#f0f0f0", font=("Helvetica", 8))
        footer_label.pack(pady=5)

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
    app = Tanker(root)
    root.mainloop()