from tkinter import *
from tkinter.ttk import *
from tkinter import font
import sys
import glob
import os
import threading
from analysis import heat
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

class Alignment_Tab(Tab):

	def __init__(self, master, **kwargs):
		"""
		Initalizes an alignment tab
		"""
		if not globals.next_template_seed:
			globals.next_template_seed = 0
		Tab.__init__(self, master, **kwargs)
		self._progress_text = ""

		# Set up frames

		self.left_frame = Frame(self)
		self.right_frame = Frame(self, bd=2, relief=GROOVE)
		self.first_left_frame = Frame(self.left_frame, bd=2, relief=GROOVE)
		self.layer = Frame(self.left_frame, bd=0, relief=GROOVE)
		self.second_left_frame = Frame(self.layer, bd=2, relief=GROOVE)
		self.third_left_frame = Frame(self.layer, bd=2, relief=GROOVE)

		self.second_left_frame.place(
			relwidth=1.0, relheight=0.40, relx=0.0, rely=0.0)
		self.third_left_frame.place(
			relwidth=1.0, relheight=0.60, relx=0.0, rely=0.40)


		# self.library_frame = Frame(
		# 	self.third_left_frame, bg='white', padx=5, pady=5)

		# height = self.third_left_frame.winfo_height()
		# print height
		# self.library_frame = self.scroll_area(self.third_left_frame, height = height*0.9)

		# Templates
		self.template_lines = []

		Label(self.first_left_frame, text='Insert Template').pack(
			side='top', pady=10)

		var = StringVar()
		# var.set('ACGT' * 25)

		line = Frame(self.first_left_frame, pady=4, bd=1, relief=SUNKEN)
		pocket = Frame(line)
		self.template = Entry(pocket, textvariable = var,
			font = font.Font(family="Courier", size=11))
		self.template.pack(fill='both')
		Label(line, text='Template ID: ' +
			  str(globals.next_template_seed), bg='white').pack(anchor='w')
		line.id = globals.next_template_seed
		line.var = var
		pocket.pack(fill=BOTH, anchor='w')
		globals.next_template_seed += 1
		line.pack(fill=BOTH, pady=0)
		self.template_lines.append(line)

		frame = Frame(self.first_left_frame)
		add_template_btn = Button(frame, text='Add template',
								  command=lambda: self.add_template(
									self.first_left_frame))
		view_templates_btn = Button(frame, text='View Existing Templates',
			command = self.show_old_templates)
		view_templates_btn.pack(side=RIGHT)
		add_template_btn.pack(side=RIGHT, pady=10)
		frame.pack(side=BOTTOM, pady=5)

		# FASTQ files

		Label(self.second_left_frame, text='Add files for alignment')\
			.pack(side=TOP)
		reset_lib_temp_btn = Button(self.second_left_frame, text = 'Reset')
		reset_lib_temp_btn["command"] = self.reset_libraries
		reset_lib_temp_btn.pack(side = BOTTOM, anchor = 'e', pady=5, padx=5)

		frame = Frame(self.second_left_frame)
		new_lib = StringVar()
		self.add_library_entry = Entry(frame, textvariable=new_lib)
		add_lib_btn = Button(frame, text='Add Library')
		self.add_library_entry.pack(side=LEFT, fill=BOTH)
		add_lib_btn.pack(side=LEFT, fill=BOTH)
		frame.pack(pady=5, side=TOP)

		# Make a scrollable area
		self.file_wrapper = self.scroll_area(self.second_left_frame)

		# View libraries

		# Resize bar:
		self.resize_bar(self.third_left_frame, orient ='x')

		# Display frame
		display_frame = Frame(self.third_left_frame)
		display_frame.pack(side=TOP, pady=15)
		Label(display_frame, text='Existing Libraries').pack(side=TOP)

		height = int(self.winfo_screenheight()*0.4)
		self.library_frame = self.scroll_area(self.third_left_frame,
			height = height)
		self.add_existing_libraries()

		self.add_library_entry.bind("<Return>", lambda: self.add_library(
			new_lib))

		add_lib_btn["command"]=lambda: self.add_library(new_lib)

		# self.library_frame.pack()
		self.first_left_frame.grid(column=0, row=0, sticky='news')
		self.layer.grid(column=0, row=1, sticky='news')

		Grid.columnconfigure(self.left_frame, 0, weight=1)
		Grid.rowconfigure(self.left_frame, 1, weight=1)

		# self.second_left_frame.place(
		# 	relwidth=1.0, relheight=0.40, relx=0.0, rely=0.0)
		# self.third_left_frame.place(
		# 	relwidth=1.0, relheight=0.60, relx=0.0, rely=0.40)

		# Right frame

		self.resize_bar(self.right_frame, orient='y')

		# Parameters and choice of alignment methods

		par_label = Label(self.right_frame, text='Alignment methods')
		par_label.pack(side=TOP, fill=BOTH)

		s = ttk.Separator(self.right_frame, orient=HORIZONTAL)
		s.pack(side=TOP, fill='x')

		# Create a container frame for methods
		self.method_instances = []
		self.params_frame = Frame(self.right_frame, bg='white')
		self.method_parameters = []

		self.number_of_columns = 2

		frame = Frame(self.right_frame)
		var = StringVar()
		method_list = [name for name in sorted(methods.methods)]
		var.set(method_list[0])
		self.method_menu = OptionMenu(frame, var, *method_list)
		self.method_menu.configure(relief=RAISED)
		self.add_method_button = Button(frame, text='Add Method',
										command=lambda: self.add_method(
											[var.get(),
											methods.methods[var.get()]]))

		self.method_menu.pack(side=LEFT, pady=5, padx=5)
		self.add_method_button.pack(side=LEFT, pady=5, padx=5)
		frame.pack(side=TOP)

		self.go_button = Button(self.right_frame, text='Start Alignment',
								command=self.start_alignment)
		self.go_button.pack(side=BOTTOM, anchor='e', padx=5, pady=5)

		self.progress_label = Label(self.right_frame)
		self.progress_label.pack(side=BOTTOM, anchor='e', padx=5, pady=5)

		self.params_frame.pack(side=TOP, ipadx=5, ipady=5)

		# Place left and right frame
		ratio = 0.5
		self.left_frame.place(relwidth=ratio, relheight=1.0, relx=0.0,
							  rely=0.0)
		self.right_frame.place(relwidth=1 - ratio, relheight=1.0,
							   relx=ratio, rely=0.0)
	def reset_libraries(self):
		if not messagebox.askokcancel("WARNING", "Are you sure you want to reset" +
			" libraries? All unsaved library changes will be lost."):
			return

		# Remove all libraries. This sets all fastq's to ('Select')
		for i, frame in enumerate(self.library_frame.winfo_children()):
			library = frame.library
			self.remove_frame(frame, library, force_delete = True)

		# Add existing libraries
		self.add_existing_libraries()

	def add_template(self, frame):
		var = StringVar()
		# var.set('ACGT' * 25)

		line = Frame(self.first_left_frame, pady=4, bd=1, relief=SUNKEN)
		pocket = Frame(line)
		template = Entry(pocket, textvariable=var, font = font.Font(
			family = "Courier", size=12))
		template.pack(fill='both')

		Label(line, text='Template ID: ' + str(globals.next_template_seed),
			  bg='white').pack(anchor='w')
		line.id = globals.next_template_seed
		line.var = var
		globals.next_template_seed += 1
		pocket.pack(fill=BOTH, anchor='w')
		line.pack(fill=BOTH, pady=0)
		self.template_lines.append(line)

	def show_old_templates(self):
		"""
		Displays a window with old templates to be viewed
		"""
		if hasattr(self, 'template_window'):
			self.template_window.destroy()
		self.template_window = Toplevel(padx = 10, pady = 10)
		self.template_window.title('Templates')
		n = len(db.get_templates())
		Label(self.template_window, text = str('ID'), bg = 'white',
			font=font.Font(size=14, weight='bold'))\
			.grid(row = 0, column = 0, padx = 2, pady = 2, sticky = 'news')
		Label(self.template_window, text = str('Sequence'),
			font = font.Font(size=14, weight='bold'), bg = 'white')\
			.grid(row = 0, column = 1, padx = 2, pady = 2, sticky = 'news')		
		i = 1
		for template in db.get_templates():
			Label(self.template_window, text = str(template.id), bg = 'white',
				font = font.Font(family='Courier'))\
				.grid(row = i, column = 0, padx = 2, pady = 2, sticky ='news')
			Label(self.template_window, text = str(template.sequence),
				bg = 'white', font = font.Font(family='Courier'))\
				.grid(row = i, column = 1, padx = 2, pady = 2, sticky='news')
			i += 1

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
		for name, lib in self.library_dictionary.items():
			if name == '(Select)':
				continue

			ids = re.findall('\d+', str(lib['template'].get()))
			for id in ids:
				try:
					id = int(id)
					if not (0 <= id <= globals.next_template_seed or id in \
						[template.id for template in db.get_templates()]):
						errors.append('Template ID '+str(id)+' not found')
				except:
					errors.append('Illegal Template ID \'' + id +
						'\' for library ' + name + '. ID should be an integer')
			if len(ids) > 1:
				errors.append('The alignment only allows exactly one template'+
					' per library, ' + str(len(ids)) + ' given.')
		if errors:
			self.show_message(errors)
			return

		# Check if any fastq file have not been assigned to a library
		del errors[:]
		for i, dropdown in enumerate(self.library_selection_menus):
			if dropdown.selected_lib.get() == '(Select)':
				errors.append(self.fastq_files[i])
		if errors and not messagebox.askokcancel('Warning', 'The following files have' +
			' not been assigned to a library.\n\n' + '\n'.join(errors) +
			'\nAre you sure you want to continue?'):
			return

		# The next template id before we started adding any
		previous_next_template_id = int(db.get_template_seed())

		# Create templates or get them from database
		for t in self.template_lines:
			if str(t.var.get()) == '':
				continue
			try:
				t.template = tp.Template(str(t.var.get()))
			except:
				t.template = db.get_template_by_sequence(str(t.var.get()))

		# Get enabled instances
		# count = 0
		# for instance in self.method_instances:
		# 	if instance['is_enabled'].get() in [0,'0']:
		# 		continue
		# 	count += 1

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
			library_templates = {}

			for name, info in self.library_dictionary.items():
				print(name, info)
				if name == '(Select)':
					continue
				try:
					library = lb.Library(name)
				except:
					library = db.get_library(name)
				library.fastq_files = info['files']
				try:
					id = info['template'].get()
					print('id',id)
					if int(id) >= previous_next_template_id:
						for t in self.template_lines:
							print('t.id:', t.id, ', id:',id, name)
							if int(t.id) == int(id):
								print(library.name, t.template.id)
								library_templates[library.id] = t.template.id
								break
					else:
						print(library.name, 'id:',id)
						library_templates[library.id] = int(id)
				except:
					pass

			alignment = al.Alignment(method, parameters, library_templates)
			print(library_templates)
			print(parameters)
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

	def add_existing_libraries(self):
		self.db_libraries = []
		for library in db.get_libraries():
			self.db_libraries.append(library.name)
		self.library_selection_menus = []
		self.library_dictionary = {}
		self.libraries = ['(Select)']
		self.library_dictionary['(Select)'] = {'files': [],
			'template': StringVar()}

		self.fastq_files = ws.get_fastq_files()[:]

		self.append_files(self.fastq_files)

		for library in db.get_libraries():
			name = str(library.name)
			fastq_files = library.fastq_files[:]
			self.add_library(name)
			for file in fastq_files:
				index = self.fastq_files.index(file)
				self.selected_index_changed(index, name)


	def add_library(self, lib_var, fastq_files = []):
		if '' in self.libraries:
			self.libraries.remove('')
		lib_name = None
		if type(lib_var).__name__ in ['str', 'unicode']:
			lib_name = lib_var
		else:
			lib_name = lib_var.get()
		if lib_name == '' or lib_name in self.libraries:
			return
		self.library_dictionary[lib_name] = {'files': fastq_files[:]}
		self.libraries.append(lib_name)

		# zero index and skip the '(Select)' item
		length = len(self.library_dictionary) - 1 - 1
		frame = Frame(self.library_frame, bg='white', padx=5, pady=5)
		inner_frame = Frame(frame, padx=2, pady=2)
		template = StringVar()
		enter_template = Entry(inner_frame, textvariable=template)

		self.library_dictionary[lib_name]['template'] = template
		frame.library = lib_name
		Label(inner_frame, text=lib_name).grid(row=0, column=1)
		Button(inner_frame, text='Remove', command=lambda: self.remove_frame(
			frame, lib_name)).grid(row=0, column=2, padx=2, pady=2)
		Label(inner_frame, text='Template ID: ').grid(column=0, row=1)
		enter_template.grid(row=1, column=1, columnspan=2, sticky='ew')
		ttk.Separator(inner_frame, orient=HORIZONTAL).grid(
			row=2, column=0, columnspan=3, sticky='ew')
		Grid.columnconfigure(inner_frame, 0, weight=1)
		Grid.columnconfigure(inner_frame, 1, weight=1)
		Grid.columnconfigure(inner_frame, 2, weight=1)

		inner_frame.pack(side=TOP, fill=BOTH)
		frame.grid(row=int(length / 3), column=length %
				   3, ipadx=5, ipady=5, sticky='news')

		for i, dropdown in enumerate(self.library_selection_menus):
			dropdown['menu'].add_command(label=lib_name,
										 command=lambda index=i: \
										 self.selected_index_changed(index,
											lib_name))
		if type(lib_var).__name__ not in ['str', 'unicode']:
			lib_var.set('')

		def binder(widget):
			for child in widget.winfo_children():
				binder(child)

			widget.bind('<Button-4>', self.scroll)
			widget.bind('<Button-5>', self.scroll)

		binder(frame)

		try:
			self.add_library_entry.focus()
		except AttributeError:
			pass

	def remove_frame(self, frame, library, force_delete = False):
		if library in self.db_libraries and not force_delete:
			if not messagebox.askokcancel('Warning', 'Are you sure you want'+
				' to remove' + library + ' from your libraries? All alignment'+
				' data will be' + ' lost.\nYou can undo this action by' +
				' clicking the Reset' + ' button before you align.'):
				return
		frame.destroy()
		list = self.library_dictionary[library]['files']
		del self.library_dictionary[library]

		for dropdown in self.library_selection_menus:
			index = self.libraries.index(library)
			dropdown['menu'].delete(index, index)
		for file in list:
			index = self.fastq_files.index(file)
			self.library_selection_menus[index].selected_lib.set('')
		self.libraries.remove(library)

	def selected_index_changed(self, index, new_lib):
		"""
		Handles when a file is being assigned to a library
		index: The index of the file being assigned a library
		new_lib: The name of target library
		"""

		file = self.fastq_files[index]
		old_lib = self.library_selection_menus[index].selected_lib.get()
		self.library_selection_menus[index].selected_lib.set(new_lib)

		if old_lib == new_lib:
			return

		try:
			if old_lib in self.db_libraries\
				and old_lib == db.get_associated_library(file).name:
				if not messagebox.askokcancel("Warning",
					'Are you sure you want to change'
				+ ' the library for '+file+'? All aligment data for the'
				+ ' subsequent' + ' libraries will be deleted?'):
					self.library_selection_menus[index].selected_lib\
					.set(old_lib)
					return
		except:
			pass

		if new_lib not in ['(Select)', '']:
			self.library_dictionary[new_lib]['files'].append(file)
			library_box = self.library_frame.winfo_children()\
			[self.libraries.index(new_lib) - 1]
			label = Label(library_box, text=file)
			label.bind("<Button-4>",self.scroll)
			label.bind("<Button-5>",self.scroll)
			label.pack(side=TOP, fill=BOTH, anchor='w')
		try:
			old_index = self.library_dictionary[old_lib]['files'].index(file)
			self.library_dictionary[old_lib]['files'].remove(file)
			library_box = self.library_frame.winfo_children(
			)[self.libraries.index(old_lib) - 1]
			library_box.winfo_children()[old_index + 1].destroy()
		except KeyError:
			pass
		except ValueError:
			pass


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
				   row=index / self.number_of_columns, padx=5, pady=5, ipadx=5,
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

	def init_dropdown(self, some_var, item):
		"""
		Handles when '(Select)' is selected in any of library_selection_menus
		some_var: Name of selected value (e.g. '(Select)')
		item: Name of file being assigned to no library
		"""
		index = self.fastq_files.index(item)
		old_lib = self.library_selection_menus[index].selected_lib.get()
		try:
			name = db.get_associated_library(item).name
		except:
			name = old_lib
		if name in self.db_libraries \
			and name == db.get_associated_library(item).name \
			and not messagebox.askokcancel("Warning",
						'Are you sure you want to change the library for ' + \
						item + '? All aligment data for the subsequent'
						+ ' library will be deleted when you run alignment'):
			self.library_selection_menus[index].selected_lib.set(name)
			return
		for name, lib in self.library_dictionary.items():
			files = lib['files']
			if str(item) in files or unicode(item):
				if name == old_lib == some_var:
					continue
				old_lib = name

				try:
					old_index = self.library_dictionary[
						old_lib]['files'].index(item)
					self.library_dictionary[old_lib]['files'].remove(item)
					
					library_box = self.library_frame.winfo_children(
					)[self.libraries.index(old_lib) - 1]
					library_box.winfo_children()[1 + old_index].destroy()
				except KeyError:
					print('KeyError')
				except ValueError:
					print('ValueError')

	def append_files(self, items):

		for i, item in enumerate(items):

			selected_lib = StringVar()
			selected_lib.set(self.libraries[0])
			dropdown = OptionMenu(self.file_wrapper, selected_lib,
								  *self.libraries,
								  command=lambda index=i, item=item: \
								  self.init_dropdown(index, item))
			dropdown.selected_lib = selected_lib
			dropdown.configure(relief=RAISED)
			self.library_selection_menus.append(dropdown)

			lab = Label(self.file_wrapper, bg='white', text=str(item),
						padx=10, pady=10)
			lab.bind("<Button-4>", lambda e: self.scroll(e))
			lab.bind("<Button-5>", lambda e: self.scroll(e))
			dropdown.bind("<Button-4>", lambda e: self.scroll(e))
			dropdown.bind("<Button-5>", lambda e: self.scroll(e))
			lab.grid(column=0, row=i, sticky='news')
			dropdown.grid(column=1, row=i, sticky='news')

			Grid.columnconfigure(self.file_wrapper, 0, weight=1)
			Grid.columnconfigure(self.file_wrapper, 1, weight=1)

	def reload(self):
		pass

