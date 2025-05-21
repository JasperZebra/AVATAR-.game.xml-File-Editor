import tkinter as tk
from tkinter import messagebox, ttk


class AttributeEditDialog:
    """Dialog for editing XML attributes"""
    
    def __init__(self, parent, attr_name, attr_value):
        self.result = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Edit Attribute")
        self.dialog.geometry("400x200")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        # Create form
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Attribute name
        ttk.Label(main_frame, text="Name:").grid(row=0, column=0, sticky="w", pady=5)
        self.name_var = tk.StringVar(value=attr_name)
        name_entry = ttk.Entry(main_frame, textvariable=self.name_var, width=40)
        name_entry.grid(row=0, column=1, sticky="ew", pady=5)
        name_entry.focus()
        
        # Attribute value
        ttk.Label(main_frame, text="Value:").grid(row=1, column=0, sticky="w", pady=5)
        self.value_var = tk.StringVar(value=attr_value)
        value_entry = ttk.Entry(main_frame, textvariable=self.value_var, width=40)
        value_entry.grid(row=1, column=1, sticky="ew", pady=5)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="OK", command=self.ok_clicked).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.cancel_clicked).pack(side=tk.LEFT, padx=5)
        
        # Configure grid
        main_frame.grid_columnconfigure(1, weight=1)
        
        # Bind Enter key
        self.dialog.bind('<Return>', lambda e: self.ok_clicked())
        self.dialog.bind('<Escape>', lambda e: self.cancel_clicked())
    
    def ok_clicked(self):
        """Handle OK button click"""
        name = self.name_var.get().strip()
        value = self.value_var.get()
        
        if not name:
            messagebox.showwarning("Invalid Input", "Attribute name cannot be empty.")
            return
        
        self.result = (name, value)
        self.dialog.destroy()
    
    def cancel_clicked(self):
        """Handle Cancel button click"""
        self.dialog.destroy()

