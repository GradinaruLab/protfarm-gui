from Tkinter import *
import tkFont
import sys
import glob
import os
import threading
from analysis import heat
from workspace import Workspace as ws

class Threaded_Aligner(threading.Thread):
  
	def __init__(self, alignment_tab):
		threading.Thread.__init__(self)
		self.alignment_tab = alignment_tab
 
	def run(self):
		ws.align_all(self.alignment_tab.update_progress)
		self.alignment_tab.update_progress("Done!")

class Tab(Frame):

	def __init__(self, master):
		"""Initializes a tab"""
		Frame.__init__(self, master)
		self.headerFont = tkFont.Font(size=14)
		self.listFont = tkFont.Font(size=12)

	def save_dialog(self):
		somefile = asksaveasfile(mode='w')
		print somefile, type(somefile)

	def resize_x(self, event):
		"""
		Resizes frames. Event is either affiliated to a bottom frame or a
		right frame
		"""
		widget = event.widget.master
		master = widget.master
		index = master.winfo_children().index(widget)
		sibling = master.winfo_children()[index - 1] if index > 0 else None
		if sibling is None:
			return

		# The width to split
		width = (0.0 + sibling.winfo_width() + widget.winfo_width()) /\
			master.winfo_width()
		delta = event.x / (width * master.winfo_width())
		ratio = (0.0 + sibling.winfo_width()) / master.winfo_width()
		ratio = ratio + delta if 0.01 * width < ratio + delta < 0.99 * width \
			else ratio

		sibling.place(relwidth=ratio)
		start = (0.0 + sibling.winfo_x()) / master.winfo_width() + ratio
		widget.place(relwidth=width - ratio, relx=start)

	def resize_y(self, event):
		"""
		Resizes frames. Event is either affiliated to a bottom frame or a
		right frame
		"""
		widget = event.widget.master
		master = widget.master
		index = master.winfo_children().index(widget)
		sibling = master.winfo_children()[index - 1] if index > 0 else None
		if sibling is None:
			return

		# The height to split
		height = (0.0 + sibling.winfo_height() +
				  widget.winfo_height()) / master.winfo_height()
		delta = event.y / (height * master.winfo_height())
		ratio = (0.0 + sibling.winfo_height()) / master.winfo_height()
		ratio = ratio + delta if 0.01 * height < ratio + delta < 0.99 * height\
			else ratio

		sibling.place(relheight=ratio)
		start = (0.0 + sibling.winfo_y()) / master.winfo_height() + ratio
		widget.place(relheight=height - ratio, rely=start)

	def scroll(self, event):
		widget = event.widget
		num = event.num
		delta = event.delta

		if num == 5 or delta == -120 or delta == -1:
			delta = -120
		elif num == 4 or delta == 120 or delta == 1:
			delta = 120

		while widget.master:
			try:
				widget.yview_scroll(int(-1.0 * delta / 120), "units")
			except AttributeError:
				widget = widget.master
				continue
			else:
				break
	def scroll_x(self, event):
		widget = event.widget
		num = event.num
		delta = event.delta

		if num == 5 or delta == -120 or delta == -1:
			delta = -120
		elif num == 4 or delta == 120 or delta == 1:
			delta = 120

		while widget.master:
			try:
				widget.xview_scroll(int(-1.0 * delta / 120), "units")
			except AttributeError:
				widget = widget.master
				continue
			else:
				break
	def scroll_area(self, parent_frame, scroll_y = True, scroll_x = False,
		height = 200):
		scroll_frame = Frame(parent_frame, relief = GROOVE, bd = 2)
		
		canvas = Canvas(scroll_frame, bd=3, bg='white')
		wrapper = Frame(canvas, height = 0, bg='white')
		
		if scroll_y:
			myscrollbar = Scrollbar(
				scroll_frame, orient="vertical", command=canvas.yview)

			canvas.configure(yscrollcommand=myscrollbar.set)
			canvas.bind("<Button-4>", lambda e: self.scroll(e))
			canvas.bind("<Button-5>", lambda e: self.scroll(e))
			myscrollbar.pack(side=LEFT, fill='y')
		
		if scroll_x:
			x_scrollbar = Scrollbar(
			scroll_frame, orient="horizontal", command=canvas.xview)
			canvas.configure(yscrollcommand=x_scrollbar.set)
			canvas.bind("<Control-4>", lambda e: self.scroll_x(e))
			canvas.bind("<Control-5>", lambda e: self.scroll_x(e))
			x_scrollbar.pack(side=BOTTOM, fill='x')	

		canvas.pack(side=TOP, fill='x')
		canvas.create_window((20, 0), window=wrapper, anchor='nw')
		wrapper.bind("<Configure>", lambda e: canvas.configure(
			scrollregion=canvas.bbox("all"),
			height = height))
		scroll_frame.pack(fill='x', padx=10, pady=10)

		return wrapper

	def getlen(self, lst):
		return len(lst)

	def show_message(self, message, mtype = 'error'):
		if type(message).__name__ == 'str':
			message = [message]
		mtype = mtype.upper()
		if mtype == 'ERROR':
			tkMessageBox.showerror(mtype, '\n\n'.join(message))
		elif mtype == 'WARNING':
			tkMessageBox.showerror(mtype, '\n\n'.join(message))
		elif mtype == 'INFO':
			tkMessageBox.showinfo(mtype, '\n\n'.join(message))

	def resize_bar(self, frame, orient='x', size=3, bg='#1f1f1f'):
		"""
		Creates a resize bar in frame.
		Must be the first child of a frame, be it horizontal or vertical
		"""
		s = LabelFrame(frame,
					   bg=bg)
		if orient == 'x':
			s["cursor"]='sb_v_double_arrow'
			s["height"]=size
			s.bind("<B1-Motion>", lambda event: self.resize_y(event))
			s.pack(side='top', fill='x')
		elif orient == 'y':
			s["cursor"]='sb_h_double_arrow'
			s["width"]=size
			s.bind("<B1-Motion>", lambda event: self.resize_x(event))
			s.pack(side='left', fill='both')
		else:
			raise Exception('Orient \''+orient+'\' is not recognized')
