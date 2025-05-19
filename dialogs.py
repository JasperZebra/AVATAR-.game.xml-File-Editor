import tkinter as tk
from tkinter import messagebox, ttk


class AttributeEditDialog:
    """Dialog for editing XML attributes"""
    
    def __init__(self, parent, attr_name, attr_value):
        self.result = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Edit Attribute")
        self.dialog.geometry("400x150")
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


class FindDialog:
    """Dialog for finding elements in the tree"""
    
    def __init__(self, parent, tree):
        self.tree = tree
        self.current_matches = []
        self.current_index = 0
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Find")
        self.dialog.geometry("350x120")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        # Create form
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Search text
        ttk.Label(main_frame, text="Find:").grid(row=0, column=0, sticky="w", pady=5)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(main_frame, textvariable=self.search_var, width=30)
        search_entry.grid(row=0, column=1, sticky="ew", pady=5)
        search_entry.focus()
        
        # Search options
        options_frame = ttk.Frame(main_frame)
        options_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=5)
        
        self.case_sensitive = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="Case sensitive", 
                       variable=self.case_sensitive).pack(side=tk.LEFT)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Find Next", command=self.find_next).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Find All", command=self.find_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Close", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Configure grid
        main_frame.grid_columnconfigure(1, weight=1)
        
        # Bind Enter key to find next
        self.dialog.bind('<Return>', lambda e: self.find_next())
        self.dialog.bind('<Escape>', lambda e: self.dialog.destroy())
        
        # Bind search text change to reset matches
        self.search_var.trace('w', self.reset_search)
    
    def reset_search(self, *args):
        """Reset search when text changes"""
        self.current_matches = []
        self.current_index = 0
    
    def find_next(self):
        """Find next occurrence"""
        search_text = self.search_var.get()
        if not search_text:
            return
        
        # If no current matches, find all first
        if not self.current_matches:
            self.find_all_matches(search_text)
            if not self.current_matches:
                messagebox.showinfo("Not Found", f"'{search_text}' not found.")
                return
        
        # Move to next match
        if self.current_matches:
            item = self.current_matches[self.current_index]
            self.tree.selection_set(item)
            self.tree.focus(item)
            self.tree.see(item)
            
            # Move to next match for next search
            self.current_index = (self.current_index + 1) % len(self.current_matches)
    
    def find_all(self):
        """Find and highlight all occurrences"""
        search_text = self.search_var.get()
        if not search_text:
            return
        
        self.find_all_matches(search_text)
        
        if self.current_matches:
            # Select all matches
            self.tree.selection_set(self.current_matches)
            # Focus on first match
            self.tree.focus(self.current_matches[0])
            self.tree.see(self.current_matches[0])
            
            messagebox.showinfo("Search Results", 
                              f"Found {len(self.current_matches)} occurrences of '{search_text}'.")
        else:
            messagebox.showinfo("Not Found", f"'{search_text}' not found.")
    
    def find_all_matches(self, search_text):
        """Find all matching items in the tree"""
        self.current_matches = []
        
        if not self.case_sensitive.get():
            search_text = search_text.lower()
        
        # Search recursively through all items
        self.search_recursive("", search_text)
        
        # Reset index
        self.current_index = 0
    
    def search_recursive(self, item, search_text):
        """Recursively search through tree items"""
        # Search in current item
        if item:  # Skip root
            item_text = self.tree.item(item, "text")
            if not self.case_sensitive.get():
                item_text = item_text.lower()
            
            if search_text in item_text:
                self.current_matches.append(item)
        
        # Search in children
        for child in self.tree.get_children(item):
            self.search_recursive(child, search_text)