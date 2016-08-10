from Tkinter import *
from tkFileDialog import askopenfilename
import ttk
import tkFont
from gui.main import Application
from workspace import Workspace as ws
import sys

root = Tk()
root.attributes('-zoomed', True)

root.wm_title('CLOVERpuff')

if len(sys.argv) > 1:
    ws.set_workspace_path(sys.argv[1])
else:
    ws.set_workspace_path('.')

app = Application(master=root)
app.mainloop()
root.destroy()