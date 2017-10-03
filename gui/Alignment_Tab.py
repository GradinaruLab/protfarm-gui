from tkinter import *
from tkinter import messagebox
from tkinter.ttk import *
from tkinter import font
import sys
import glob
import os
import threading
from . import methods
from . import globals
import re
import numpy as np
from workspace import Workspace as ws
from workspace import Library as lb
from workspace import Template as tp
from workspace import Alignment as al
from workspace import Database as db
from .Tab import *
from functools import partial

class Alignment_Tab(Tab):

	def __init__(self, master, **kwargs):

		Tab.__init__(self, master, **kwargs)

		self._left_frame = Frame(self)
		self._right_frame = Frame(self)

		self._left_frame.place(relwidth=0.5, relheight=1.0, relx=0.0,
							  rely=0.0)
		self._right_frame.place(relwidth=0.5, relheight=1.0,
							   relx=0.5, rely=0.0)

		self._samples_frame = None
		self._alignment_frame = None

	def reload(self):

		self._progress_text = ""
		self._sample_templates = {}

		self.load_samples()
		self.load_alignment()

	def load_samples(self):

		if self._samples_frame != None:
			self._samples_frame.destroy()

		self._samples_frame = Frame(self._left_frame)
		self._samples_frame.pack()

		Label(self._samples_frame, text='Existing Samples')\
			.pack(side=TOP)

		self._samples_scroll_area = self.scroll_area(self._samples_frame,
			height = self.winfo_toplevel().winfo_height())

		self._samples = db.get_samples()
		self._templates = db.get_templates()
		self._template_options = ["(None)"]
		self._template_options.extend(\
			[template.name for template in self._templates])

		for sample_index, sample in enumerate(self._samples):

			label = Label(self._samples_scroll_area, text=sample.name, \
				bg="white")
			label.grid(row = sample_index, column = 0)
			label.bind("<Button-4>", self.scroll)
			label.bind("<Button-5>", self.scroll)

			associated_template_var = StringVar()
			associated_template_var.set(self._template_options[0])

			template_selected_command = partial(self.template_selected, \
				sample_index)

			template_dropdown = OptionMenu(self._samples_scroll_area, \
				associated_template_var, *self._template_options, \
				command=template_selected_command)
			template_dropdown.grid(row = sample_index, column = 1, \
				sticky="news")

			template_dropdown.bind("<Button-4>", self.scroll)
			template_dropdown.bind("<Button-5>", self.scroll)

	def template_selected(self, sample_index, selected_value):

		sample = self._samples[sample_index]

		if selected_value == self._template_options[0]:
			del self._library_templates[sample.id]
		else:
			selected_template_index = self._templates.index(selected_value)
			selected_template = self._templates[selected_template_index]

			self._library_templates[sample.id] = selected_template.id

	def load_alignment(self):

		if self._alignment_frame != None:
			self._alignment_frame.destroy()

		self._alignment_frame = Frame(self._right_frame)
		#self._alignment_frame.pack(fill=BOTH)
		self._alignment_frame.place(relwidth=1.0, relheight=1.0, relx=0.0,
							  rely=0.0)

		self._methods_frame = Frame(self._alignment_frame)
		self._methods_frame.pack(fill=BOTH)

		# Parameters and choice of alignment methods

		par_label = Label(self._methods_frame, text='Alignment methods')
		par_label.pack(side=TOP, fill=BOTH)

		s = ttk.Separator(self._methods_frame, orient=HORIZONTAL)
		s.pack(side=TOP, fill='x')

		# Create a container frame for methods
		self.method_instances = []
		self.params_frame = Frame(self._methods_frame, bg='white')
		self.method_parameters = []

		self.number_of_columns = 2

		frame = Frame(self._methods_frame)
		var = StringVar()
		method_list = [name for name in sorted(methods.methods)]
		var.set(method_list[0])
		self.method_menu = OptionMenu(frame, var, *method_list)
		self.method_menu.configure(relief=RAISED)
		self.add_method_button = Button(frame, text='Add Method',
										command=lambda: self.add_method(
											[var.get(),
											methods.methods[(var.get())]]))

		self.method_menu.pack(side=LEFT, pady=5, padx=5)
		self.add_method_button.pack(side=LEFT, pady=5, padx=5)
		frame.pack(side=TOP)

		self.go_button = Button(self._alignment_frame, text='Start Alignment',
								command=self.start_alignment)
		self.go_button.pack(side=BOTTOM, anchor='e', padx=5, pady=5)

		self.progress_label = Label(self._alignment_frame)
		self.progress_label.pack(side=BOTTOM, anchor='e', padx=5, pady=5)

		self.params_frame.pack(side=TOP, ipadx=5, ipady=5)

	def update_progress(self, text):

		self._progress_text = text
		print(text)
		self.progress_label["text"] = self._progress_text

	def check_alignment_progress(self):

		if self._progress_text != "Done!":
			self.master.after(100, self.check_alignment_progress)
		else:
			self.go_button["state"] = "normal"

	def start_alignment(self):

		# Check if all libraries have been assigned to existing templates
		errors = []
		for sample in self._samples:
			if sample.id not in self._sample_templates:
				errors.append("Missing template for sample '%s'" % sample.name)
		if errors:
			self.show_message(errors)
			return

		for instance in self.method_instances:
			if instance['is_enabled'].get() in [0,'0']:
				continue
			method = instance['name']
			try:
				parameters = {name:(int(value.get())
					if (hasattr(value,'datatype') and value.datatype=='int')\
					else value.get())\
					for name, value in instance['parameters'].items()}
			except Error as e:
				messagebox.showerror(str(e))
				return

			alignment = al.Alignment(method, parameters, self._sample_templates)
		for lib in self.library_dictionary:
			globals.method_instances = self.method_instances
			globals.library_dictionary = self.library_dictionary
		try:
			self.go_button["state"] = "disabled"
			Threaded_Aligner(self).start()
			self.master.after(100, self.check_alignment_progress)
		except Exception as e:
			print(str(e))
			messagebox.showinfo("Exception", str(e))
			self.go_button["state"] = "normal"

	def add_method(self, method):
		"""Adds a box for the selected method"""
		# create a container frame
		index = len(self.method_instances)
		frame = Frame(self.params_frame)
		frame.name = method[0] + ' ' + str(globals.next_method_seed)

		instance = {'name': method[0], 'parameters': {}}
		globals.next_method_seed += 1
		frame.index = index
		params = method[1]['parameters']
		is_enabled = StringVar()
		is_enabled.set('0')
		lab = Checkbutton(frame, text=frame.name, variable=is_enabled)
		instance['is_enabled'] = is_enabled
		lab.index = frame.index
		lab.name = frame.name
		lab.checked = False
		lab.bind("<Button>", self.disable_method)
		lab.bind("<space>", self.disable_method)
		frame.widgets = [lab]
		lab.pack(side=TOP, fill=Y)
		for parameter, info in sorted(params.items()):
			type = info['type']
			line = Frame(frame, highlightcolor='red',
						 highlightbackground='red')
			val = None
			text = Label(line, text=parameter)
			variable = StringVar()
			if type == 'Checkbutton':
				variable.set('0')
				val = Checkbutton(line, disabledforeground='gray',
								  variable=variable)
			elif type == 'Entry':
				val = Entry(line, textvariable=variable)
				try:
					val.datatype = info['datatype']
				except:
					pass
			elif type == 'Radiobutton':
				options = info['options']
				val = Frame(line)
				if len(options.items())==0:
					continue
				for a, b in options.items():
					if not variable.get():
						variable.set(b)
					b = Radiobutton(val, text=a, value=b, 
						variable=variable)
					b.pack(side=TOP, padx=0, anchor='w')	
			else:
				continue

			val.variable = variable
			instance['parameters'][info['name']] = val.variable
			if hasattr(val,'datatype'):
				instance['parameters'][info['name']].datatype = val.datatype
			try:
				val['state'] = DISABLED
			except:
				pass
			line.pack(side=TOP, fill=BOTH, padx=5)
			text.pack(side=LEFT, fill=Y)
			val.pack(side=RIGHT, fill=Y)

			frame.widgets.append(val)

		frame.grid(column=index % self.number_of_columns,
				   row=int(index / self.number_of_columns), padx=5, pady=5, ipadx=5,
				   ipady=5, sticky='WNES')
		self.method_parameters.append(frame)
		self.method_instances.append(instance)

	def disable_method(self, event):
		"""Disables a certain alignment method"""
		frame = self.method_parameters[event.widget.index]
		frame.widgets[0].checked = not frame.widgets[0].checked
		if frame.widgets[0].checked:
			for widget in frame.widgets[1:]:
				try:
					widget['state'] = NORMAL
				except:pass
		else:
			for widget in frame.widgets[1:]:
				try:
					widget['state'] = DISABLED
				except:pass