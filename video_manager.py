import tkinter as tk
from tkinter import ttk, filedialog, simpledialog, messagebox
from video_database import (create_table, get_all_videos, is_code_unique, update_unique_code, update_video_path,
                            update_uploaded_status, delete_video_from_db)
from video_filter import get_filtered_videos
from video_scanner import scan_directory

class VideoManager:
    def __init__(self, root):
        create_table()
        self.conn = None
        self.sort_order = {}
        self.selected_item = None
        self.active_filters = {'uploader': None, 'date': None, 'disk': None}
        self.setup_ui(root)
        self.load_data()
        self.update_status_bar()

    def setup_ui(self, root):
        """Set up the Tkinter UI."""
        columns = ('ID', 'Uploader', 'Unique Code', 'Datetime', 'Title', '.ext', 'Disk', 'Filename', 'Uploaded?')
        self.tree = ttk.Treeview(root, columns=columns, show='headings')

        # Define columns to center-align
        columns_to_center = ['ID', 'Uploader', 'Unique Code', 'Datetime', '.ext', 'Disk', 'Uploaded?']
        fixed_width_columns = ['Title', 'Filename']

        # Load all data to measure column widths
        all_data = get_all_videos()

        total_width = 0  # To store the total width of all columns

        # Define column headings, set alignment, and calculate width
        for col in columns:
            self.tree.heading(col, text=col, command=lambda _col=col: self.sort_table(_col))

            if col in columns_to_center:
                # Calculate the maximum width required for the column
                max_data_width = max(len(str(row[columns.index(col)])) for row in all_data) if all_data else 0
                max_header_width = len(col)

                # Calculate the final width, considering both data and header lengths
                max_width = max(max_data_width, max_header_width) * 10
                self.tree.column(col, anchor=tk.CENTER, width=max_width, stretch=False)
                total_width += max_width
            elif col in fixed_width_columns:
                fixed_width = 200
                self.tree.column(col, width=fixed_width, anchor=tk.W, stretch=False)
                total_width += fixed_width
            else:
                self.tree.column(col, anchor=tk.W, stretch=True)

        # Add a scrollbar to the Treeview
        self.scrollbar = ttk.Scrollbar(root, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        self.tree.grid(row=0, column=0, sticky='nsew')
        self.scrollbar.grid(row=0, column=1, sticky='ns')

        # Adjust the window width based on the total content width
        total_width += 20  # Add some extra space for padding and scrollbar
        window_height = 750
        root.geometry(f"{total_width}x{window_height}")

        # Add buttons for various actions in a horizontal layout
        button_frame = tk.Frame(root)
        button_frame.grid(row=1, column=0, columnspan=2, pady=5, sticky='ew')

        scan_button = tk.Button(button_frame, text="Scan Folder", command=self.scan_folder)
        scan_button.pack(side='left', padx=5)

        edit_code_button = tk.Button(button_frame, text="Edit 'Unique Code'", command=self.edit_unique_code)
        edit_code_button.pack(side='left', padx=5)

        edit_path_button = tk.Button(button_frame, text="Edit 'Disk'", command=self.edit_file_path)
        edit_path_button.pack(side='left', padx=5)

        toggle_uploaded_button = tk.Button(button_frame, text="Toggle 'Uploaded?'", command=self.toggle_uploaded)
        toggle_uploaded_button.pack(side='left', padx=5)

        filter_button = tk.Button(button_frame, text="Filter by 'Uploader'", command=self.filter_by_uploader)
        filter_button.pack(side='left', padx=5)

        filter_button = tk.Button(button_frame, text="Filter by 'Date'", command=self.filter_by_date)
        filter_button.pack(side='left', padx=5)

        filter_button = tk.Button(button_frame, text="Filter by 'Disk'", command=self.filter_by_disk)
        filter_button.pack(side='left', padx=5)

        remove_button = tk.Button(button_frame, text="Remove Entry", command=self.remove_entry)
        remove_button.pack(side='left', padx=5)

        # Configure the grid to expand properly
        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)

        # Add a status bar at the bottom of the window
        self.status_bar = tk.Label(root, text="Selected Rows: 0", anchor='e')
        self.status_bar.grid(row=2, column=0, columnspan=2, sticky='ew')

        # Bind the selection event to update the status bar
        self.tree.bind("<<TreeviewSelect>>", self.on_selection_change)

    def update_status_bar(self):
        """Update the status bar with the number of selected rows."""
        selected_count = len(self.tree.selection())
        self.status_bar.config(text=f"Selected Rows: {selected_count}")

    def on_selection_change(self, event):
        """Handle the selection change event in the Treeview."""
        self.update_status_bar()

    def load_data(self):
        """Load and display the current data, considering active filters and sorting."""
        # Determine sorting parameters
        sort_column = next(iter(self.sort_order.keys()), None)
        sort_order = self.sort_order.get(sort_column, 'ASC') if sort_column else None

        # Fetch filtered and sorted data
        data = get_filtered_videos(
            uploader_name=self.active_filters.get('uploader'),
            date_name=self.active_filters.get('date'),
            disk_name=self.active_filters.get('disk'),
            sort_column=sort_column,
            sort_order=sort_order
        )

        # Load the data into the Treeview
        self.tree.delete(*self.tree.get_children())
        for row in data:
            row = list(row)
            row[-1] = '✔' if row[-1] == 1 else '✘'
            self.tree.insert('', 'end', values=row)

    def scan_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            scan_directory(folder_path)
            self.load_data()

    def edit_unique_code(self):
        """Edit the unique code for the selected entries."""
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "Please select at least one row to edit.")
            return

        new_code = simpledialog.askstring("Edit 'Unique Code'", "Enter new unique code (#0000 to #9999):")
        if not new_code or not new_code.startswith('#') or not new_code[1:].isdigit() or len(new_code) != 5:
            messagebox.showerror("Error", "Invalid code format. Must be in the form #0000 to #9999.")
            return

        code_number = int(new_code[1:])
        if code_number < 0 or code_number > 9999:
            messagebox.showerror("Error", "Code must be between #0000 and #9999.")
            return

        for item in selected_items:
            video_id = self.tree.item(item, 'values')[0]
            uploader_name = self.tree.item(item, 'values')[1]

            # If the code is not #0000, check for uniqueness
            if new_code != "#0000":
                if not is_code_unique(uploader_name, new_code):
                    messagebox.showerror("Error", f"Code {new_code} is already used for uploader {uploader_name}.")
                    return

            # Update the Treeview and database
            self.tree.set(item, 'Unique Code', new_code)
            update_unique_code(video_id, new_code)
        messagebox.showinfo("Success", "Unique code updated successfully!")

    def edit_file_path(self):
        """Open a dialog to edit the file path of selected rows."""
        # Get all selected items in the Treeview
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "Please select at least one row to edit.")
            return

        # Prompt the user to enter a new file path
        new_path = simpledialog.askstring("Edit 'Disk'", "Enter new file path (disk) for selected entries:")
        if new_path is None or new_path.strip() == "":
            return  # If the user cancels or enters an empty path, do nothing

        # Loop through each selected item and update the file path
        for item in selected_items:
            video_id = self.tree.item(item, 'values')[0]

            # Update the Treeview with the new path
            self.tree.set(item, 'Disk', new_path)

            # Update the database with the new path
            update_video_path(video_id, new_path)

        messagebox.showinfo("Success", "File path (disk) updated for all selected entries!")

    def toggle_uploaded(self):
        """Toggle the 'Uploaded?' status for selected entries."""
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "Please select at least one row to toggle.")
            return

        for item in selected_items:
            current_status = self.tree.item(item, 'values')[8]
            new_status = '✔' if current_status == '✘' else '✘'
            video_id = self.tree.item(item, 'values')[0]

            # Update the Treeview and database
            self.tree.set(item, 'Uploaded?', new_status)
            update_uploaded_status(video_id, new_status == '✔')
        messagebox.showinfo("Success", "Uploaded status toggled successfully!")

    def filter_by_uploader(self):
        """Filter videos by a specific uploader."""
        uploader = simpledialog.askstring("Filter by Uploader", "Enter Uploader Name:")
        self.active_filters['uploader'] = uploader  # Save filter
        self.load_data()  # Reload data with the updated filter

    def filter_by_date(self):
        """Filter videos by a specific date."""
        date = simpledialog.askstring("Filter by Date", "Enter Date (YYYY-MM-DD):")
        self.active_filters['date'] = date  # Save filter
        self.load_data()

    def filter_by_disk(self):
        """Filter videos by a specific path."""
        disk = simpledialog.askstring("Filter by Disk/Path", "Enter Disk/Path:")
        self.active_filters['disk'] = disk  # Save filter
        self.load_data()

    def remove_entry(self):
        """Remove the selected entry/entries from the Treeview and the database."""
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "Please select at least one row to remove.")
            return

        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete the selected entries?")
        if not confirm:
            return

        for item in selected_items:
            # Get the video ID from the Treeview
            video_id = self.tree.item(item, 'values')[0]

            # Delete from the database
            delete_video_from_db(video_id)

            # Remove the entry from the Treeview
            self.tree.delete(item)

        messagebox.showinfo("Success", "Selected entries have been removed successfully.")

    def sort_table(self, column):
        """Sort the Treeview based on the selected column."""
        column_mapping = {
            'ID': 'id',
            'Uploader': 'uploader_name',
            'Unique Code': 'unique_code',
            'Datetime': 'datetime',
            'Title': 'title',
            '.ext': 'extension',
            'Disk': 'file_path',
            'Filename': 'filename',
            'Uploaded?': 'uploaded'
        }

        db_column = column_mapping.get(column)
        if not db_column:
            return

        # Update sort order
        if db_column not in self.sort_order or self.sort_order[db_column] == 'DESC':
            self.sort_order[db_column] = 'ASC'
        else:
            self.sort_order[db_column] = 'DESC'

        self.load_data()  # Reload data with updated sorting

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Video Manager")

    # Make the window resizable
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)

    app = VideoManager(root)
    root.mainloop()
