import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import csv
import os, sys
import json
from datetime import datetime

def resource_path(relative_path):
    '''Get absolute path to resource, works for dev and for PyInstaller'''
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath('.')

    return os.path.join(base_path, relative_path)

class SpeciesCounterGUI:

    def __init__(self):
        self.create_root()

        self.style = ttk.Style(self.root)
        self.csv_filepath = None
        self.has_unsaved_changes = False

        self.load_themes()

        self.create_general_frame()

        self.create_widgets_frame()
        self.create_csv_tools()
        self.create_separator()
        self.create_theme_tool()

        self.create_tree_frame()
        self.create_treeview()
        self.load_hotkeys()

        self.root.mainloop()

    #####################
    # INTERFACE METHODS #
    #####################

    def create_root(self):
        self.root = tk.Tk()
        self.root.title('Species Counter')
        self.make_grid_resizable(self.root, 1, 1)
        self.root.protocol('WM_DELETE_WINDOW', self.ask_save_changes)

        self.root.focus_set()

    def ask_save_changes(self):
        if self.has_unsaved_changes:
            response = messagebox.askyesnocancel('Save Changes', 
                                                'You have unsaved changes. Do you want to save before exiting?')
            if response is True:
                self.save()
                self.root.destroy()
            elif response is False:
                self.root.destroy()
        else:
            self.root.destroy()

    def load_themes(self):
        self.root.tk.call('source', resource_path('themes/forest-light.tcl'))
        self.root.tk.call('source', resource_path('themes/forest-dark.tcl'))
        self.style.theme_use('forest-dark')

    def create_general_frame(self):
        self.frame = ttk.Frame(self.root)
        self.frame.grid(row=0, column=0, sticky='nsew')
        self.make_grid_resizable(self.frame, 1, 2)

    def create_widgets_frame(self):
        self.widgets_frame = ttk.Frame(self.frame)
        self.widgets_frame.grid(row=0, column=0, padx=20, pady=10, sticky='nsew')
        self.make_grid_resizable(self.widgets_frame, 3, 1)

    def create_csv_tools(self):
        self.csv_frame = ttk.LabelFrame(self.widgets_frame, text='CSV Tools', labelanchor='n')
        self.csv_frame.grid(row=0, column=0, pady=10, sticky='nsew')
        self.make_grid_resizable(self.csv_frame, 5, 1)

        self.csv_widgets_frame = ttk.Frame(self.csv_frame)
        self.csv_widgets_frame.grid(row=0, column=0, sticky='nsew')
        self.make_grid_resizable(self.csv_widgets_frame, 5, 1)

        self.create_button = ttk.Button(self.csv_widgets_frame, text='New CSV', command=self.reset_treeview)
        self.create_button.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')

        self.load_button = ttk.Button(self.csv_widgets_frame, text='Load CSV', command=self.load_csv)
        self.load_button.grid(row=1, column=0, padx=5, pady=5, sticky='nsew')

        self.csv_tools_separator = ttk.Separator(self.csv_widgets_frame)
        self.csv_tools_separator.grid(row=2, column=0, padx=5, pady=10, sticky='ew')

        self.delete_button = ttk.Button(self.csv_widgets_frame, text='Delete last row', command=self.delete_last_row)
        self.delete_button.grid(row=3, column=0, padx=5, pady=5, sticky='nsew')

        self.save_button = ttk.Button(self.csv_widgets_frame, text='Save', command=self.save)
        self.save_button.grid(row=4, column=0, padx=5, pady=(5, 10), sticky='nsew')

    def create_separator(self):
        self.separator = ttk.Separator(self.widgets_frame)
        self.separator.grid(row=1, column=0, padx=10, pady=(5, 15), sticky='ew')

    def create_theme_tool(self):
        self.theme_switch = ttk.Checkbutton(self.widgets_frame, text='Theme', style='Switch', command=self.toggle_theme)
        self.theme_switch.grid(row=2, column=0, sticky='nsew')

    def create_tree_frame(self):
        self.tree_frame = ttk.Frame(self.frame)
        self.tree_frame.grid(row=0, column=1, padx=(0, 20), pady=10, sticky='nsew')
        self.tree_frame.grid_rowconfigure(0, weight=1)
        self.tree_frame.grid_columnconfigure(0, weight=1)
        self.tree_frame.grid_rowconfigure(1, weight=0)
        self.tree_frame.grid_columnconfigure(1, weight=0)
    
    def create_treeview(self):
        self.col_widths = {
            'Species': 200,
            'Count': 100,
            'Timestamp': 250,
            'Latitude': 150,
            'Longitude': 150
        }
        self.tree = ttk.Treeview(self.tree_frame, show='headings', columns=list(self.col_widths.keys()), height=15)
        self.tree.grid(row=0, column=0, sticky='nsew')

        self.tree_xscroll = ttk.Scrollbar(self.tree_frame, orient='horizontal', command=self.tree.xview)
        self.tree_xscroll.grid(row=1, column=0, sticky='ew')
        self.tree_yscroll = ttk.Scrollbar(self.tree_frame, orient='vertical', command=self.tree.yview)
        self.tree_yscroll.grid(row=0, column=1, sticky='ns')

        self.tree.configure(xscrollcommand=self.tree_xscroll.set, yscrollcommand=self.tree_yscroll.set)

        self.reset_treeview()

    #####################
    # MECHANICS METHODS #
    #####################

    def make_grid_resizable(self, element, rows, cols):
        for i in range(rows):
            element.grid_rowconfigure(i, weight=1)
        for i in range(cols):
            element.grid_columnconfigure(i, weight=1)

    def reset_treeview(self):
        for heading, width in self.col_widths.items():
            self.tree.heading(heading, text=heading, anchor='w')
            self.tree.column(heading, width=width, anchor='w')

        for item in self.tree.get_children():
            self.tree.delete(item)

        self.csv_filepath = None

    def load_csv(self):
        self.reset_treeview()

        filepath = filedialog.askopenfilename(filetypes=[('CSV files', '*.csv')])
        if filepath:
            with open(filepath) as file:
                csvFile = csv.reader(file)
                headers = next(csvFile)
                if headers == list(self.col_widths.keys()):
                    for heading, width in self.col_widths.items():
                        self.tree.heading(heading, text=heading, anchor='w')
                        self.tree.column(heading, width=width, anchor='w')
                else:
                    self.tree['columns'] = headers
                    for header in headers:
                        self.tree.heading(header, text=header, anchor='w')
                        self.tree.column(header, width=200, anchor='w')

                for row in csvFile:
                    self.tree.insert("", tk.END, values=row)

            self.csv_filepath = filepath

        self.root.focus_set()
        
    def delete_last_row(self):
        if self.tree.get_children():
            last_item = self.tree.get_children()[-1]
            self.tree.delete(last_item)

            self.has_unsaved_changes = True
    
    def save(self):
        if not self.csv_filepath:
            time = datetime.now().replace(microsecond=0)
            default_name = f'{time} Dotting.csv'
            self.csv_filepath = filedialog.asksaveasfilename(initialfile=default_name,
                                                     defaultextension='.csv', 
                                                     filetypes=[('CSV files', '*.csv')])
        if self.csv_filepath:
            with open(self.csv_filepath, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(self.tree['columns'])
                for row in self.tree.get_children():
                    writer.writerow(self.tree.item(row)['values'])

        self.has_unsaved_changes = False
                        
    def toggle_theme(self):
        if self.theme_switch.instate(['selected']):
            self.style.theme_use('forest-light')
        else:
            self.style.theme_use('forest-dark')

    def load_hotkeys(self):
        filepath = resource_path('hot_keys.json')

        with open(filepath) as file:
            self.hotkeys = json.load(file)

        self.last_key = ''
        self.digits = ''

        for key in self.hotkeys.keys():
            self.root.bind(f'<KeyPress-{key}>', self.key_pressed)

        for i in range(10):
            self.root.bind(f'<KeyPress-{i}>', self.number_key_pressed)

        self.root.bind('<Return>', self.add_row)

    def key_pressed(self, event):
        self.last_key = event.char

    def number_key_pressed(self, event):
        if self.last_key and not (self.digits == '' and event.char == '0'):
            self.digits += event.char

    def add_row(self, event):
        if self.last_key and self.digits:
            species = self.hotkeys[self.last_key]
            count = self.digits
            time = datetime.now().replace(microsecond=0)
            latitude = '38.8951'
            longitude = '-77.0364'

            row = [species, count, time, latitude, longitude]
            self.tree.insert("", tk.END, values=row)

            self.last_key = ''
            self.digits = ''

            self.has_unsaved_changes = True

if __name__ == '__main__':
    SpeciesCounterGUI()