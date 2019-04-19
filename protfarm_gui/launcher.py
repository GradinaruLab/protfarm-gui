from tkinter import ttk
from tkinter import filedialog
from .Template_Tab import *
from .Sample_Tab import *
from .Alignment_Tab import *
from .Analysis_Tab import *
from .Alignment_Statistics_Tab import *
from protfarm.workspace import Workspace as ws
from protfarm.workspace import Database as db


class Application(Frame):

    def __init__(self, master=None):
        
        Frame.__init__(self, master)
        
        databases = {
            'template_db' : db.template_db,
            'library_db' : db.library_db,
            'alignment_db' : db.alignment_db
        }

        globals.next_template_seed = int(db.template_db['next_template_id'])
        globals.next_method_seed = int(db.alignment_db['next_alignment_id'])

        self.current_selection = []
        
        if master:
            master.minsize(width=600, height=400)
        self.headerFont = font.Font(size=14)
        self.listFont = font.Font(size=12)

        self.notebook = ttk.Notebook(master)
        self.template_tab = Template_Tab(self.notebook)
        self.sample_tab = Sample_Tab(self.notebook)
        self.alignment_tab = Alignment_Tab(self.notebook)
        self.stats_tab = Alignment_Statistics_Tab(self.notebook)
        self.analysis_tab = Analysis_Tab(self.notebook)

        self.notebook.add(self.template_tab, text='Templates', padding=20)
        self.notebook.add(self.sample_tab, text="Samples", padding=20)
        self.notebook.add(self.alignment_tab, text='Alignment', padding=20)
        self.notebook.add(
            self.stats_tab, text='Alignment Statistics', padding=20)
        self.notebook.add(self.analysis_tab, text='Analysis', padding=20)

        self.notebook.place(relheight=1.0, relwidth=1.0)

        self.notebook.bind("<1>", self.tab_handler)
        self.pack(fill='both')
        self.template_tab.reload()

    def tab_handler(self, event):
        if event.widget.identify(event.x, event.y) in ['label', 'padding']:
            index = event.widget.index('@%d,%d' % (event.x, event.y))
            instance = event.widget.winfo_children()[index]
            try:
                instance.reload()
            except AttributeError:
                pass


def launch():
    root = Tk()

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    root.geometry("%sx%s" % (screen_width, screen_height))

    root.wm_title('ProtFarm')

    if len(sys.argv) > 1:
        directory = sys.argv[1]
    else:
        directory = filedialog.askdirectory()

    if directory:
        ws.set_workspace_path(directory)
        app = Application(master=root)

        root.update()

        def on_closing():
            if messagebox.askokcancel("Quit", "Do you want to quit?"):
                root.destroy()

        root.protocol("WM_DELETE_WINDOW", on_closing)
        app.mainloop()


if __name__ == "__main__":
    launch()
