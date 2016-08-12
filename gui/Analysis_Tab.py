from Tkinter import *
import tkFileDialog
from tkFileDialog import *
import tkMessageBox
import ttk
import tkFont
import sys
import glob
import os
import threading
from analysis import heat
import methods
import globals
import re
import numpy as np
from workspace import Workspace as ws
from workspace import Library as lb
from workspace import Template as tp
from workspace import Alignment as al
from workspace import Database as db
from Tab import *

class Analysis_Tab(Tab):

	def __init__(self, master, **kwargs):
		"""Initializes the current tab"""
		Tab.__init__(self, master, **kwargs)

		self.main_frame = Frame(self, padx=10, pady=10, relief=GROOVE, bd=2)

		# Top left frame

		Grid.columnconfigure(self.main_frame, 0, weight=1)
		Grid.columnconfigure(self.main_frame, 1, weight=1)
		Grid.columnconfigure(self.main_frame, 2, weight=1)
		Grid.columnconfigure(self.main_frame, 3, weight=1)

		# 1 - Starting library
		Label(self.main_frame, text='Starting Library').grid(row=0, column=0,
			sticky='ne', padx=5, pady=5)
		var = StringVar()
		self.library_list = [library.name for library in db.get_libraries()]
		try:
			self.starting_library_dd = OptionMenu(
				self.main_frame, var, *self.library_list)

			self.starting_library_dd.configure(relief=RAISED)
			self.starting_library_dd.grid(
				row=0, column=1, sticky='news', padx=5, pady=5)
		except:
			pass

		interest_bundle = Frame(self.main_frame)
		comparison_bundle = Frame(self.main_frame)
		
		self.libraries_of_interest = Listbox(interest_bundle)
		self.libraries_to_compare = Listbox(comparison_bundle)

		# 2 - Libraries of interest
		lab = Label(interest_bundle, text='Libraries of Interest')
		lab.grid(row=0, column=0, sticky='ne', padx=5, pady=5)

		self.libraries_of_interest.grid(
			row=0, column=1, sticky='news', padx=5, pady=5, rowspan=2)

		Grid.columnconfigure(interest_bundle, 0, weight=1)
		Grid.columnconfigure(interest_bundle, 1, weight=1)

		browse_button = Button(interest_bundle, text='Browse \nLibraries',
			command=lambda: self.display_libraries([self.libraries_of_interest,
				self.libraries_to_compare]))
		browse_button.grid(row=1, column=0, sticky='ne')

		interest_bundle.grid(row=1, column=0, sticky='news', pady=5, padx=5,
			columnspan=2)

		# 3 - Libraries to compare
		lab = Label(comparison_bundle, text='Libraries to Compare')
		lab.grid(row=0, column=0, sticky='ne', padx=5, pady=5)

		self.libraries_to_compare.grid(
			row=0, column=1, sticky='news', padx=5, pady=5, rowspan=2)

		Grid.columnconfigure(comparison_bundle, 0, weight=1)
		Grid.columnconfigure(comparison_bundle, 1, weight=1)

		browse_button = Button(comparison_bundle, text = 'Browse \nLibraries',
			command=lambda: self.display_libraries([self.libraries_to_compare,
				self.libraries_of_interest]))
		browse_button.grid(row=1, column=0, sticky='ne')


		comparison_bundle.grid(row=2, column=0, sticky='news', pady=5, padx=5,
			columnspan=2)

		# 4 - Count threshold
		lab = Label(self.main_frame, text='Count Threshold').grid(
			row=3, column=0, sticky='ne', padx=5, pady=5)
		self.threshold_entry = Entry(self.main_frame).grid(
			row=3, column=1, sticky='news', padx=5, pady=5)

		self.export_btn = Button(self.main_frame, text='Export All to CSV').grid(
			row=4, column=3, sticky='se', padx=5, pady=5)

		Grid.columnconfigure(self, 0, weight=1)		
		self.main_frame.grid(column=0, row=0, sticky='news')

	def reload(self):
		pass

	def display_libraries(self, groups):
		"""
		groups is a list of Frame objects
		groups[0] is the target Frame
		other Frames in groups are used for filtering
		"""
		if hasattr(self, 'library_window'):
			self.library_window.destroy()
		self.library_window = Toplevel()
		self.library_window.title('Libraries')
		old_list = [str(line.name) for list in groups for line in list.winfo_children()]
		print old_list

		new_list = [str(library.name) for library in db.get_libraries() \
			if str(library.name) not in old_list]

		def add_to_frame(name, frame, to_destroy):
			line = Frame(frame)
			Label(line, text = name).grid(row=0, column=0)
			rm_button = Button(line, text = 'Remove', command=line.destroy)
			rm_button.grid(column=1, row=0)
			line.name = name
			line.pack(side=TOP, fill=BOTH)
			to_destroy.destroy()

		for library in new_list:
			line = Frame(self.library_window)
			add_button = Button(line, text='Add',
				command = lambda: add_to_frame(library, groups[0], line))
			label = Label(line, text=library)

			label.grid(column=0, row=0)
			add_button.grid(column=1, row=0)
			line.pack(side=TOP, fill=BOTH)