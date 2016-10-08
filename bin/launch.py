from Tkinter import *
import tkFileDialog
import tkMessageBox
from tkFileDialog import *
import ttk
import tkFont
import sys
import glob
import os
from analysis import heat
from gui import methods
from gui import globals
from gui.Alignment_Tab import *
from gui.Analysis_Tab import *
from gui.Alignment_Statistics_Tab import *
from workspace import Workspace as ws
from workspace import Library as lb
from workspace import Template as tp
from workspace import Alignment as al
from workspace import Database as db

from tkFileDialog import askopenfilename


class Application(Frame):

    def __init__(self, master=None):
        
        Frame.__init__(self, master, height=160)
        
        databases = {
            'template_db' : db.template_db,
            'library_db' : db.library_db,
            'alignment_db' : db.alignment_db
        }

        globals.next_template_seed = int(db.template_db['next_template_id'])
        globals.next_method_seed = int(db.alignment_db['next_alignment_id'])

        globals.library_dictionary = {}
        globals.method_instances = {}
        self.current_selection = []
        
        if master:
            master.minsize(width=600, height=400)
        self.headerFont = tkFont.Font(size=14)
        self.listFont = tkFont.Font(size=12)

        self.notebook = ttk.Notebook(master)
        self.alignment_tab = Alignment_Tab(self.notebook)
        self.stats_tab = Alignment_Statistics_Tab(self.notebook)
        self.analysis_tab = Analysis_Tab(self.notebook)

        self.notebook.add(self.alignment_tab, text='Alignment', padding=20)
        self.notebook.add(
            self.stats_tab, text='Alignment Statistics', padding=20)
        self.notebook.add(self.analysis_tab, text='Analysis', padding=20)

        self.notebook.place(relheight=1.0, relwidth=1.0)

        self.notebook.bind("<1>", self.tab_handler)
        self.pack(fill='both')

    def tab_handler(self, event):
        if event.widget.identify(event.x, event.y) in ['label', 'padding']:
            index = event.widget.index('@%d,%d' % (event.x, event.y))
            instance = event.widget.winfo_children()[index]
            try:
                instance.reload()
            except AttributeError:
                pass

root = Tk()
root.attributes('-zoomed', True)

root.wm_title('CLOVERbot')


if len(sys.argv) > 1:
    directory = sys.argv[1]
else:
    directory = tkFileDialog.askdirectory()

if directory:
    ws.set_workspace_path(directory)
    app = Application( master=root)
    app.mainloop()
root.destroy()