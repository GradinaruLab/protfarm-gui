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
from analysis.Analysis_Set import Analysis_Set
from workspace import Workspace as ws
from workspace import Library as lb
from workspace import Template as tp
from workspace import Alignment as al
from workspace import Database as db
from analysis import enrichment as enrichment_analysis
from Tab import *

class Analysis_Tab(Tab):

	def __init__(self, master, **kwargs):
		"""Initializes the current tab"""
		Tab.__init__(self, master, **kwargs)

		self.analysis_set = Analysis_Set()

		self.main_frame = Frame(self, padx=10, pady=10, relief=GROOVE, bd=2)

		Grid.columnconfigure(self.main_frame, 0, weight=1)
		Grid.columnconfigure(self.main_frame, 1, weight=1)
		Grid.columnconfigure(self.main_frame, 2, weight=1)

		# Enrichment frame
		self.enrichment_frame = Frame(self.main_frame, padx=5, pady=5,
			relief=GROOVE, bd=2)
		self.specificity_frame = Frame(self.main_frame, padx=5, pady=5,
			relief=GROOVE, bd=2)

		# 1 - Starting library
		Label(self.enrichment_frame, text='Starting Library').grid(row=0, column=0,
			sticky='nw', padx=5, pady=5)
		var = StringVar()
		self.library_list = [library.name for library in db.get_libraries()]
		
		try:
			self.starting_library_dd = OptionMenu(
				self.enrichment_frame, var, *self.library_list)
			self.starting_library_dd.var = var
			self.starting_library_dd.configure(relief=RAISED)
			self.starting_library_dd.grid(
				row=0, column=1, sticky='nws', padx=5, pady=5)
		except:
			pass

		self.libraries_of_interest = Listbox(self.enrichment_frame)
		self.libraries_to_compare = Listbox(self.specificity_frame)
		
		for library in db.get_libraries():
			self.add_to_frame(library.name, self.libraries_of_interest)

		# 2 - Libraries of interest
		lab = Label(self.enrichment_frame, text='Libraries of Interest ')
		lab.grid(row=1, column=0, sticky='nw', padx=5, pady=5)

		self.libraries_of_interest.grid(
			row=1, column=1, sticky='news', padx=5, pady=5, rowspan=2)

		# Grid.columnconfigure(self.enrichment_frame, 0, weight=1)
		Grid.columnconfigure(self.enrichment_frame, 1, weight=1)

		browse_button = Button(self.enrichment_frame, text='Browse \nLibraries',
			command=lambda: self.display_libraries([self.libraries_of_interest]))
		browse_button.grid(row=2, column=0, sticky='ne')

		self.enrichment_frame.grid(row=1, column=0, sticky='news', pady=5, padx=5)

		# 3 - Specificity
		lab = Label(self.specificity_frame, text='Libraries to Compare')
		lab.grid(row=0, column=0, sticky='nws', padx=5, pady=5)

		self.libraries_to_compare.grid(
			row=0, column=1, sticky='news', padx=5, pady=5, rowspan=2)

		# Grid.columnconfigure(self.specificity_frame, 0, weight=1)
		Grid.columnconfigure(self.specificity_frame, 1, weight=1)

		browse_button = Button(self.specificity_frame, text = 'Browse \nLibraries',
			command=lambda: self.display_libraries([self.libraries_to_compare]))
		browse_button.grid(row=1, column=0, sticky='ne')

		self.specificity_frame.grid(row=2, column=0, sticky='news', pady=5, padx=5)

		# 4 - Count threshold
		frame = Frame(self.main_frame)
		lab = Label(frame, text='Count Threshold').grid(
			row=0, column=0, sticky='nw', padx=5, pady=5)
		self.count_threshold = StringVar()
		self.threshold_entry = Entry(frame, textvariable = self.count_threshold).grid(
			row=0, column=1, sticky='news', padx=5, pady=5)
		frame.grid(row=3, column=0)

		self.export_btn = Button(self.main_frame, text='Export All to CSV',
			command= self.export_all)

		self.export_btn.grid(row=4, column=3, sticky='se', padx=5, pady=5)

		self.plot_enrichment_distribution_btn = \
			Button(self.main_frame, text='Plot enrichment distribution', \
				command= self.plot_enrichment_distribution)

		self.plot_enrichment_distribution_btn.grid(row=3, column = 3,
			sticky='se', padx=5, pady = 5)

		Grid.columnconfigure(self, 0, weight=1)		
		self.main_frame.grid(column=0, row=0, sticky='news')


	def reload(self):
		"""
		Reloads everything from the database and initializes
		"""
		pass

	def plot_enrichment_distribution(self):

		self.analysis_set = Analysis_Set()
		starting_library = self.starting_library_dd.var.get()
		libraries_of_interest = [str(line.name) for line in self.libraries_of_interest.winfo_children()]

		try:
			threshold = int(self.count_threshold.get().strip())
		except:
			threshold = False

		enrichments = []

		self.analysis_set.add_library(db.get_library(starting_library))
		
		for library in libraries_of_interest:
			self.analysis_set.add_library(db.get_library(library))

		for library_name in libraries_of_interest:
			sequence_enrichments = self.analysis_set.get_enrichment( \
				starting_library, library_name, count_threshold=threshold)
			enrichments.extend(sequence_enrichments.values())

		enrichment_analysis.plot_distribution(enrichments)

	def export_all(self):

		self.analysis_set = Analysis_Set()
		starting_library = self.starting_library_dd.var.get()
		libraries_of_interest = [str(line.name) for line in self.libraries_of_interest.winfo_children()]
		libraries_to_compare = [str(line.name) for line in self.libraries_to_compare.winfo_children()]
		try:
			threshold = int(self.count_threshold.get().strip())
		except:
			threshold = False

		if not (starting_library and libraries_of_interest and libraries_to_compare and threshold):
			return
		
		for library in libraries_of_interest:
			self.analysis_set.add_library(db.get_library(library))

		filename = 'analysis.csv'
		self.analysis_set.export_enrichment_specificity(filename,
			starting_library, libraries_to_compare, count_threshold = self.count_threshold.get(),
			by_amino_acid = True)
		print 'starting',  starting_library
		print 'Threshold', self.count_threshold.get()
		print 'libraries_of_interest', libraries_of_interest
		print 'libraries_to_compare',libraries_to_compare

	def add_to_frame(self, library, frame, destroy = None):
		"""
		Adds a new line for 'library' in the frame 'frame'
		"""
		line = Frame(frame, bg='white')
		Label(line, text = library, bg='white').grid(row=0, column=0)
		rm_button = Button(line, text = 'Remove', command=line.destroy)
		rm_button.grid(column=1, row=0)
		line.name = library
		line.pack(side=TOP, fill=BOTH, ipadx=5, ipady=5, padx=5, pady=5)
		if destroy:
			destroy.destroy()

	def display_libraries(self, listboxes):
		"""
		Displays libraries that are not included in the frame 'listbox',
		in a separate window.
		"""
		if hasattr(self, 'library_window'):
			self.library_window.destroy()
		listbox = listboxes[0]

		self.library_window = Toplevel()
		self.library_window.title('Libraries')

		old_list = [str(line.name) for box in listboxes for line in box.winfo_children()]

		new_list = [str(library.name) for library in db.get_libraries() \
			if str(library.name) not in old_list]

		for library in new_list:
			line = Frame(self.library_window)
			add_button = Button(line, text='Add',
				command = lambda lib = library, line=line: self.add_to_frame(lib, listbox, destroy=line))
			label = Label(line, text=library)

			label.grid(column=0, row=0)
			add_button.grid(column=1, row=0)
			line.pack(side=TOP, fill=BOTH)