from tkinter import *
from tkinter import messagebox
import sys
import glob
import os
import threading
from analysis import heat
from . import methods
from . import globals
import re
import numpy as np
from analysis.Analysis_Set import Analysis_Set
from workspace import Workspace as ws
from workspace import Library as lb
from workspace import Template as tp
from workspace import Alignment as al
from workspace import Database as db
from analysis import enrichment as enrichment_analysis
from analysis import amino_acids as amino_acid_analysis
from analysis import coverage as coverage_analysis
from ml import feature_analysis
from .Tab import *
import matplotlib
matplotlib.use("TkAgg")
from matplotlib import pyplot as plt
import seaborn as sns
from utils.AminoAcid import AminoAcid

from multiprocessing import Process

class Analysis_Tab(Tab):

	def __init__(self, master, **kwargs):
		"""Initializes the current tab"""
		Tab.__init__(self, master, **kwargs)

		self.analysis_set = Analysis_Set()
		self.processes = []
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

		frame = Frame(self.enrichment_frame)
		height = self.winfo_screenheight()
		self.libraries_of_interest = self.scroll_area(frame, height=height*0.2)
		frame.grid(row=1, column=1, sticky='news')	
		frame = Frame(self.specificity_frame)
		self.libraries_to_compare = self.scroll_area(frame, height=height*0.2)
		frame.grid(row=0, column=1, sticky='news')

		self.libraries_of_interest.bind('<Button-4>', self.scroll)
		self.libraries_of_interest.bind('<Button-5>', self.scroll)

		# 2 - Libraries of interest
		lab = Label(self.enrichment_frame, text='Libraries of Interest ')
		lab.grid(row=1, column=0, sticky='nw', padx=5, pady=5)

		Grid.columnconfigure(self.enrichment_frame, 1, weight=1)

		browse_button = Button(self.enrichment_frame, text='Browse \nLibraries',
			command=lambda: self.display_libraries([self.libraries_of_interest]))
		browse_button.grid(row=1, column=0, sticky='s')

		self.enrichment_frame.grid(row=1, column=0, sticky='news', pady=5, padx=5)

		# 3 - Specificity
		lab = Label(self.specificity_frame, text='Libraries to Compare')
		lab.grid(row=0, column=0, sticky='nws', padx=5, pady=5)

		Grid.columnconfigure(self.specificity_frame, 1, weight=1)

		browse_button = Button(self.specificity_frame, text = 'Browse \nLibraries',
			command=lambda: self.display_libraries([self.libraries_to_compare]))
		browse_button.grid(row=0, column=0, sticky='s')

		self.specificity_frame.grid(row=2, column=0, sticky='news', pady=5, padx=5)

		# 4 - Count threshold
		frame = Frame(self.main_frame)
		Label(frame, text='Count Threshold').grid(
			row=0, column=0, sticky='nw', padx=5, pady=5)
		self.count_threshold = StringVar()
		self.count_threshold.set('100')
		self.threshold_entry = Entry(frame, textvariable = self.count_threshold).grid(
			row=0, column=1, sticky='news', padx=5, pady=5)
		frame.grid(row=1, column=1, sticky='n')

		#5 - Include zero counts
		Label(frame, text='Include zero counts?').grid(
			row=1, column=0, sticky='nw', padx=5, pady=5)
		self.include_zero_counts = IntVar()
		self.include_zero_counts_checkbox = Checkbutton(frame,
			variable=self.include_zero_counts)
		self.include_zero_counts_checkbox.deselect()
		self.include_zero_counts_checkbox.grid(row=1, column=1, sticky='w',
			padx=5, pady=5)

		#6 - Zero count default value
		Label(frame, text='Zero Count Default Value').grid(
			row=2, column=0, sticky='nw', padx=5, pady=5)
		self.zero_count_default_value = StringVar()
		self.zero_count_default_value.set('')
		self.zero_count_default_value_entry = Entry(frame, \
			textvariable = self.zero_count_default_value).grid(
			row=2, column=1, sticky='news', padx=5, pady=5)

		#7 - By Amino Acid
		Label(frame, text='By Amino Acid?').grid(
			row=3, column=0, sticky='nw', padx=5, pady=5)
		self.by_amino_acid = IntVar()
		self.by_amino_acid_checkbox = Checkbutton(frame,
			variable=self.by_amino_acid)
		self.by_amino_acid_checkbox.select()
		self.by_amino_acid_checkbox.grid(row=3, column=1, sticky='w',
			padx=5, pady=5)

		#8 - Log Scale
		Label(frame, text='Log Scale?').grid(
			row=4, column=0, sticky='nw', padx=5, pady=5)
		self.log_scale = IntVar()
		self.log_scale_checkbox = Checkbutton(frame,
			variable=self.log_scale)
		self.log_scale_checkbox.select()
		self.log_scale_checkbox.grid(row=4, column=1, sticky='w',
			padx=5, pady=5)

		#9 - Enrichment threshold
		Label(frame, text='Enrichment threshold').grid(
			row=6, column=0, sticky='nw', padx=5, pady=5)
		self.enrichment_threshold = StringVar()
		self.enrichment_threshold.set('0.0')
		self.enrichment_threshold_entry = Entry(frame, \
			textvariable = self.enrichment_threshold).grid(
			row=6, column=1, sticky='news', padx=5, pady=5)

		#10 - Amino acid properties
		Label(frame, text='Amino acid property').grid(
			row=7, column=0, sticky='nw', padx=5, pady=5)
		self.amino_acid_property = StringVar()
		self.amino_acid_property_list = AminoAcid.properties
		self.amino_acid_property_dropdown = OptionMenu(
			frame, self.amino_acid_property, *self.amino_acid_property_list)

		self.amino_acid_property.set(self.amino_acid_property_list[0])

		self.amino_acid_property_dropdown.grid(row=7, column=1, sticky='nw',
			padx=5, pady=5)
		
		####Buttons for things
		nice_button_wrapper = Frame(self.main_frame)

		self.amino_acid_count_heatmap_btn = Button(nice_button_wrapper,
			text='Amino Acid Count Heatmap',
			command=self.amino_acid_count_heatmap)
		self.amino_acid_count_heatmap_btn.pack(side='top', fill='both', padx=5,
			pady=5)

		self.position_heatmap_btn = Button(nice_button_wrapper,
			text='Position Heatmap',
			command=self.position_heatmap)
		self.position_heatmap_btn.pack(side='top', fill='both',
			padx=5, pady=5)

		self.amino_acid_properties_heatmap_btn = Button(\
			nice_button_wrapper,
			text='Amino Acid Properties Heatmap',
			command=self.amino_acid_properties_heatmap)
		self.amino_acid_properties_heatmap_btn.pack(side='top',
			fill='both', padx=5, pady=5)

		self.export_btn = Button(nice_button_wrapper, text='Export All to CSV',
			command= self.export_all)
		self.export_btn.pack(side='top', fill='both', padx=5, pady=5)

		self.plot_enrichment_distribution_btn = \
			Button(nice_button_wrapper, text='Plot Enrichment Distribution', \
				command= self.plot_enrichment_distribution)
		self.plot_enrichment_distribution_btn.pack(side='top', fill='both',
			padx=5, pady = 5)

		self.plot_specificity_distribution_btn = \
			Button(nice_button_wrapper, text='Plot Specificity Distribution', \
				command= self.plot_specificity_distribution)
		self.plot_specificity_distribution_btn.pack(side='top', fill='both',
			padx=5, pady = 5)

		self.plot_amino_acid_property_distribution_btn = \
			Button(nice_button_wrapper, text='Plot Amino Acid Property Distribution', \
				command = self.plot_amino_acid_property_distribution)

		self.plot_amino_acid_property_distribution_btn.pack(side='top', fill='both', padx=5, pady=5)

		self.coverage_analysis_btn = \
			Button(nice_button_wrapper, text='Analyze Library Coverage', \
				command = self.analyze_coverage)
		self.coverage_analysis_btn.pack(side='top', fill='both', padx=5, pady = 5)

		Grid.columnconfigure(self, 0, weight=1)		
		nice_button_wrapper.grid(column=3, row=2, sticky='se', padx=5, pady=5)

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
			self.show_message('Invalid count threshold: must be a number')
			return

		try:
			enrichment_threshold = float(self.enrichment_threshold.get().strip())
		except:
			self.show_message('Invalid enrichment threshold: must be a number')
			return
		
		try:
			by_amino_acid = bool(self.by_amino_acid.get())
		except:
			by_amino_acid = True


		if self.zero_count_default_value.get().strip() == "":
			zero_count_default_value = None
		else:
			try:
				zero_count_default_value = float(self.zero_count_default_value.get().strip())
			except:
				self.show_message('Invalid zero count default: must be a number')
				return

		try:
			include_zero_counts = bool(self.include_zero_counts.get())
		except:
			include_zero_counts = False

		try:
			log_scale = bool(self.log_scale.get())
		except:
			log_scale = True

		enrichments = []

		self.analysis_set.add_library(db.get_library(starting_library))
		
		for library in libraries_of_interest:
			self.analysis_set.add_library(db.get_library(library))

		for library_name in libraries_of_interest:
			sequence_enrichments = self.analysis_set.get_enrichment( \
				library_name, starting_library, count_threshold=threshold,
				by_amino_acid = by_amino_acid, zero_count_magic_number = zero_count_default_value,
				include_zero_count = include_zero_counts, Log_Scale = log_scale)

			enrichments.extend(sequence_enrichments.values())

		enrichment_analysis.plot_distribution(enrichments, enrichment_threshold)

	def plot_specificity_distribution(self):

		self.analysis_set = Analysis_Set()
		libraries_of_interest = [str(line.name) for line in self.libraries_of_interest.winfo_children()]
		libraries_to_compare = [str(line.name) for line in self.libraries_to_compare.winfo_children()]

		try:
			threshold = int(self.count_threshold.get().strip())
		except:
			self.show_message('Invalid count threshold: must be a number')
			return

		try:
			specificity_threshold = float(self.enrichment_threshold.get().strip())
		except:
			self.show_message('Invalid specificity threshold: must be a number')
			return

		if self.zero_count_default_value.get().strip() == "":
			zero_count_default_value = None
		else:
			try:
				zero_count_default_value = float(self.zero_count_default_value.get().strip())
			except:
				self.show_message('Invalid zero count default: must be a number')
				return

		try:
			include_zero_counts = bool(self.include_zero_counts.get())
		except:
			include_zero_counts = False
		
		try:
			by_amino_acid = bool(self.by_amino_acid.get())
		except:
			by_amino_acid = True

		try:
			log_scale = bool(self.log_scale.get())
		except:
			log_scale = True
		
		for library in libraries_of_interest:
			self.analysis_set.add_library(db.get_library(library))
		for library in libraries_to_compare:
			self.analysis_set.add_library(db.get_library(library))

		sequence_specificities = self.analysis_set.get_specificity( \
			libraries_of_interest, libraries_to_compare, count_threshold=threshold,
			by_amino_acid = by_amino_acid, log_scale = log_scale,
			zero_count_magic_number = zero_count_default_value)
		
		sns.distplot(list(sequence_specificities.values()),bins=100,kde=False,rug=False)
		plt.xlabel('specificity')
		plt.ylabel('sequence counts')
		plt.axvline(specificity_threshold)
		plt.show()

	def plot_amino_acid_property_distribution(self):

		self.analysis_set = Analysis_Set()
		starting_library = self.starting_library_dd.var.get()
		libraries_of_interest = [str(line.name) for line in self.libraries_of_interest.winfo_children()]

		try:
			threshold = int(self.count_threshold.get().strip())
		except:
			self.show_message('Invalid count threshold: must be a number')
			return

		try:
			by_amino_acid = bool(self.by_amino_acid.get())

			if not by_amino_acid:
				self.show_message('Must do analysis by amino acid for amino acid property distributions')
				return
		except:
			by_amino_acid = True

		if self.zero_count_default_value.get().strip() == "":
			zero_count_default_value = None
		else:
			try:
				zero_count_default_value = float(self.zero_count_default_value.get().strip())
			except:
				self.show_message('Invalid zero count default: must be a number')
				return

		try:
			include_zero_counts = bool(self.include_zero_counts.get())
		except:
			include_zero_counts = False

		try:
			log_scale = bool(self.log_scale.get())
		except:
			log_scale = True

		try:
			amino_acid_property = str(self.amino_acid_property.get())
		except:
			amino_acid_property = self.amino_acid_property_list[0]

		try:
			enrichment_threshold = float(self.enrichment_threshold.get().strip())
		except:
			self.show_message('Invalid enrichment threshold: must be a number')
			return

		self.analysis_set.add_library(db.get_library(starting_library))

		above_enrichment_sequences = []
		below_enrichment_sequences = []
		
		for library in libraries_of_interest:
			self.analysis_set.add_library(db.get_library(library))

		for library_name in libraries_of_interest:
				
			sequence_enrichments = self.analysis_set.get_enrichment( \
				library_name, starting_library, count_threshold=threshold,
				by_amino_acid = by_amino_acid, zero_count_magic_number = zero_count_default_value,
				include_zero_count = include_zero_counts, Log_Scale = log_scale)

			library_above_enrichment_sequences, library_below_enrichment_sequences = \
				enrichment_analysis.split_by_enrichment(sequence_enrichments,
					enrichment_threshold=enrichment_threshold)

			above_enrichment_sequences.extend(library_above_enrichment_sequences)
			below_enrichment_sequences.extend(library_below_enrichment_sequences)

		amino_acid_charact_matrix_high_enrich = amino_acid_analysis.generate_matrix_of_interest(above_enrichment_sequences,matrix_property=amino_acid_property)
		amino_acid_charact_matrix_below_enrich = amino_acid_analysis.generate_matrix_of_interest(below_enrichment_sequences,matrix_property=amino_acid_property)
		amino_acid_analysis.plot_amino_acid_property_distribution_from_matrix(amino_acid_charact_matrix_high_enrich,amino_acid_property,'Enriched above 0')
		amino_acid_analysis.plot_amino_acid_property_distribution_from_matrix(amino_acid_charact_matrix_below_enrich,amino_acid_property,'Enriched below 0')

		plt.show(block=False)

	def analyze_coverage(self):

		try:
			by_amino_acid = bool(self.by_amino_acid.get())
		except:
			by_amino_acid = False

		self.analysis_set = Analysis_Set()

		starting_library = self.starting_library_dd.var.get()
		libraries_of_interest = [str(line.name) for line in self.libraries_of_interest.winfo_children()]
		libraries_to_compare = [str(line.name) for line in self.libraries_to_compare.winfo_children()]

		if starting_library:
			self.analysis_set.add_library(db.get_library(starting_library))
		
		for library in libraries_of_interest:
			self.analysis_set.add_library(db.get_library(library))

		for library in libraries_to_compare:
			self.analysis_set.add_library(db.get_library(library))

		num_included_sequences, num_possible_sequences = coverage_analysis.get_coverage(self.analysis_set, by_amino_acid = by_amino_acid)

		libraries_included_string = 'Libraries included:\n'

		for library_name, library in self.analysis_set.get_libraries().items():
			libraries_included_string += library_name + '\n'

		sequences_included_string = "\n%04e sequences included\n" % num_included_sequences
		possible_sequences_string = "%04e possible sequences.\n" % num_possible_sequences
		coverage_string = "%06f%% coverage\n" % (num_included_sequences * 100.0 / num_possible_sequences)
		messagebox.showinfo('Coverage analysis', libraries_included_string + sequences_included_string + possible_sequences_string + coverage_string)

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
			messagebox.showerror('Missing library or threshold - make sure threshold is set and there is a starting library, library of interest, and library to compare to')
			return

		self.analysis_set.add_library(db.get_library(starting_library))
		
		for library in libraries_of_interest:
			self.analysis_set.add_library(db.get_library(library))
		for library in libraries_to_compare:
			self.analysis_set.add_library(db.get_library(library))

		filename = 'analysis.csv'
		self.analysis_set.export_enrichment_specificity(filename,
			starting_library, libraries_to_compare, count_threshold = threshold,
			by_amino_acid = True)
		print('starting',  starting_library)
		print('Threshold', self.count_threshold.get())
		print('libraries_of_interest', libraries_of_interest)
		print('libraries_to_compare',libraries_to_compare)

	def add_to_frame(self, library, frame, destroy = None):
		"""
		Adds a new line for 'library' in the frame 'frame'
		"""
		line = Frame(frame, bg='white')
		label = Label(line, text = library, bg='white')
		label.grid(row=0, column=0)
		rm_button = Button(line, text = 'Remove', command=line.destroy)
		rm_button.grid(column=1, row=0)


		Grid.columnconfigure(line, 0, weight=0)
		Grid.columnconfigure(line, 0, weight=1)

		line.bind('<Button-4>', self.scroll)
		line.bind('<Button-5>', self.scroll)
		label.bind('<Button-4>', self.scroll)
		label.bind('<Button-5>', self.scroll)
		rm_button.bind('<Button-4>', self.scroll)
		rm_button.bind('<Button-5>', self.scroll)

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
		w = str(int(self.winfo_screenwidth()*0.4))
		h = str(int(self.winfo_screenheight()*0.5))
		self.library_window.geometry('300x500+0+0')

		old_list = [str(line.name) for box in listboxes for line in \
			box.winfo_children()]

		new_list = [str(library.name) for library in db.get_libraries() \
			if str(library.name) not in old_list]

		for library in new_list:
			line = Frame(self.library_window)
			add_button = Button(line, text='Add',
				command = lambda lib = library, line=line: self.add_to_frame(\
					lib, listbox, destroy=line))
			label = Label(line, text=library)

			add_button.grid(column=0, row=0, padx=5, pady=5)
			label.grid(column=1, row=0, padx=5, pady=5)
			line.pack(side=TOP, fill=BOTH)

	def position_heatmap(self):

		try:
			count_threshold = int(self.count_threshold.get().strip())
		except:
			self.show_message('Invalid count threshold: must be a number')
			return

		try:
			by_amino_acid = bool(self.by_amino_acid.get())
		except:
			by_amino_acid = True

		try:
			enrichment_threshold = float(self.enrichment_threshold.get().strip())
		except:
			self.show_message('Invalid enrichment threshold: must be a number')
			return

		if self.zero_count_default_value.get().strip() == "":
			zero_count_default_value = None
		else:
			try:
				zero_count_default_value = float(self.zero_count_default_value.get().strip())
			except:
				self.show_message('Invalid zero count default: must be a number')
				return

		try:
			include_zero_counts = bool(self.include_zero_counts.get())
		except:
			include_zero_counts = False

		analysis_set = Analysis_Set()
		starting_library_name = self.starting_library_dd.var.get()

		libraries_of_interest_names = [str(line.name) for line in \
			self.libraries_of_interest.winfo_children()]

		analysis_set.add_library(db.get_library(starting_library_name))

		for library_of_interest_name in libraries_of_interest_names:
			analysis_set.add_library(db.get_library(library_of_interest_name))

		for library_of_interest_name in libraries_of_interest_names:

			sequence_enrichments = analysis_set.get_enrichment(library_of_interest_name,
				starting_library_name, by_amino_acid=by_amino_acid,
				count_threshold=count_threshold, include_zero_count = include_zero_counts,
				zero_count_magic_number = zero_count_default_value)

			weights, feature_labels = \
				feature_analysis.get_position_feature_weights(sequence_enrichments,
				label_threshold = enrichment_threshold)

			position_labels = reversed(range(1,analysis_set.get_sequence_length() + 1))
			position_labels = [str(i) for i in position_labels]

			heatmap = heat.heatmap(title = 'Weight of AA Positions for Predicting Enrichment of ' + library_of_interest_name,
				data=weights, y_labels=position_labels, x_labels=feature_labels)

			heat.heatmap.draw(heatmap, show=False)

		plt.show()

	def amino_acid_properties_heatmap(self):

		try:
			count_threshold = int(self.count_threshold.get().strip())
		except:
			self.show_message('Invalid count threshold: must be a number')
			return

		try:
			enrichment_threshold = float(self.enrichment_threshold.get().strip())
		except:
			self.show_message('Invalid enrichment threshold: must be a number')
			return

		if self.zero_count_default_value.get().strip() == "":
			zero_count_default_value = None
		else:
			try:
				zero_count_default_value = float(self.zero_count_default_value.get().strip())
			except:
				self.show_message('Invalid zero count default: must be a number')
				return

		try:
			include_zero_counts = bool(self.include_zero_counts.get())
		except:
			include_zero_counts = False

		try:
			log_scale = bool(self.log_scale.get())
		except:
			log_scale = True

		analysis_set = Analysis_Set()
		starting_library_name = self.starting_library_dd.var.get()

		libraries_of_interest_names = [str(line.name) for line in \
			self.libraries_of_interest.winfo_children()]

		analysis_set.add_library(db.get_library(starting_library_name))

		for library_of_interest_name in libraries_of_interest_names:
			analysis_set.add_library(db.get_library(library_of_interest_name))

		for library_of_interest_name in libraries_of_interest_names:

			sequence_enrichments = analysis_set.get_enrichment(library_of_interest_name,
				starting_library_name, by_amino_acid=True, count_threshold=count_threshold,
				include_zero_count = include_zero_counts,
				zero_count_magic_number = zero_count_default_value,
				Log_Scale = log_scale)

			print('Got enrichment for %i sequences' % len(sequence_enrichments))

			weights, feature_labels = \
				feature_analysis.get_amino_acid_characteristics_feature_weights(
					sequence_enrichments, label_threshold = enrichment_threshold)

			position_labels = reversed(range(1,analysis_set.get_sequence_length() + 1))
			position_labels = [str(i) for i in position_labels]

			heatmap = heat.heatmap(title = 'Weight of AA Properties for Predicting Enrichment of ' + library_of_interest_name,
				data=weights, y_labels=position_labels, x_labels=feature_labels)

			heat.heatmap.draw(heatmap, show=False)
		plt.show()

	def amino_acid_count_heatmap(self):

		try:
			count_threshold = int(self.count_threshold.get().strip())
		except:
			self.show_message('Invalid count threshold: must be a number')
			return
		
		by_amino_acid = True

		filter_invalid = False

		libraries_of_interest = [str(line.name) for line in \
			self.libraries_of_interest.winfo_children()]
		try:
			for library in libraries_of_interest:
				library = db.get_library(library)
				heatmap = heat.heatmap(title = 'Amino Acid Distribution of ' + library.name)
				heatmap.normalized_sequence_counts(
					library=library,
					by_amino_acid=by_amino_acid,
					count_threshold=count_threshold,
					filter_invalid=filter_invalid)
				heat.heatmap.draw(heatmap,show=False)

			plt.show()

		except Exception as e:
			messagebox.showinfo("",
				str(e))
