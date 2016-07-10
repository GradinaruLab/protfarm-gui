from Tkinter import *
from tkFileDialog import askopenfilename
import ttk
import tkFont
from gui.main import Application
#from gui.main import Application


root = Tk()
root.attributes('-zoomed', True)
app = Application(master=root)
app.mainloop()
root.destroy()