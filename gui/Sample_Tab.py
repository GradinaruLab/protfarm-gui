from .Tab import *
from tkinter import messagebox
from workspace import Database as db
from workspace.Library import Library
from functools import partial

class Sample_Tab(Tab):

    def __init__(self, master, **kwargs):

        Tab.__init__(self, master, **kwargs)

        self._samples_frame = Frame(self)
        self._samples_frame.place(relwidth=0.5, relheight=1.0, relx=0.0, rely=0.0)

        self._existing_samples_frame = Frame(self._samples_frame)
        self._existing_samples_frame.pack(side=TOP)

        self._add_sample_button = Button(self._samples_frame, \
            text="Add Sample", command=self.add_sample_clicked)

        self._add_sample_button.pack(side=TOP)

        self._FASTQ_frame = Frame(self)
        self._FASTQ_frame.place(relwidth=0.5, relheight=1.0, relx=0.5, rely=0.0)

        self._samples = []
        self._sample_list_frame = None

        self._FASTQ_files = []
        self._FASTQ_list_frame = None

        self._new_sample_frame = None

    def reload(self):

        self.load_samples()
        self.load_FASTQ_files()

    def load_samples(self):

        self._samples = db.get_samples()

        if self._sample_list_frame != None:
            self._sample_list_frame.destroy()

        self._sample_list_frame = Frame(self._existing_samples_frame)
        self._sample_list_frame.pack()

        sample_index = 0

        self._sample_labels = []
        self._sample_rename_buttons = []
        self._sample_delete_buttons = []

        for sample in self._samples:

            label = Label(self._sample_list_frame, text=sample.name)
            label.grid(row = sample_index, column = 0)

            rename_button = Button(self._sample_list_frame, text="Rename", \
                command=lambda index=sample_index: \
                self.rename_sample_clicked(index))
            rename_button.grid(row = sample_index, column=1, sticky="news")

            delete_button = Button(self._sample_list_frame, text="Delete", \
                command=lambda index=sample_index: \
                self.delete_sample_clicked(index))
            delete_button.grid(row = sample_index, column=2, sticky="news")

            self._sample_labels.append(label)
            self._sample_rename_buttons.append(rename_button)
            self._sample_delete_buttons.append(delete_button)

            sample_index += 1

    def load_FASTQ_files(self):

        self._FASTQ_files = db.get_FASTQ_files()

        if self._FASTQ_list_frame != None:
            self._FASTQ_list_frame.destroy()

        self._FASTQ_list_frame = Frame(self._FASTQ_frame)
        self._FASTQ_list_frame.pack(fill=BOTH)

        self._FASTQ_scroll_area = self.scroll_area(self._FASTQ_list_frame, \
            height=self.winfo_toplevel().winfo_height())

        FASTQ_file_index = 0

        self._sample_options = ["(None)"]
        self._sample_options.extend([sample.name for sample in self._samples])

        self._sample_dropdowns = []

        for FASTQ_file in self._FASTQ_files:

            label = Label(self._FASTQ_scroll_area, text=FASTQ_file.name, \
                bg="white")
            label.grid(row = FASTQ_file_index, column = 0, sticky="news")

            label.bind("<Button-4>", self.scroll)
            label.bind("<Button-5>", self.scroll)

            associated_sample_var = StringVar()

            associated_sample = db.get_associated_library(FASTQ_file.name)

            if associated_sample == None:
                associated_sample_var.set(self._sample_options[0])
            else:
                associated_sample_var.set(associated_sample.name)

            sample_selected_command = partial(self.sample_selected, \
                FASTQ_file_index)

            sample_dropdown = OptionMenu(self._FASTQ_scroll_area, \
                associated_sample_var, *self._sample_options,\
                command=sample_selected_command)
            sample_dropdown.grid(row = FASTQ_file_index, column = 1, \
                sticky="news")

            sample_dropdown.bind("<Button-4>", self.scroll)
            sample_dropdown.bind("<Button-5>", self.scroll)

            self._sample_dropdowns.append(sample_dropdown)
            
            FASTQ_file_index += 1

        Grid.columnconfigure(self._FASTQ_scroll_area, 0, weight=1)

    def sample_selected(self, FASTQ_file_index, selected_value):

        FASTQ_file = self._FASTQ_files[FASTQ_file_index]

        current_sample = db.get_associated_library(FASTQ_file.name)

        if current_sample != None:
            if current_sample.name == selected_value:
                return
            else:
                current_sample.remove_file(FASTQ_file.name)

        if selected_value == self._sample_options[0]:
            return

        new_sample = db.get_library(selected_value)
        new_sample.add_file(FASTQ_file.name)

    def add_sample_clicked(self):
        self.add_edit_sample()

    def add_edit_sample(self, sample = None):

        if self._new_sample_frame != None:
            self._new_sample_frame.destroy()

        self._new_sample_frame = Frame(self._samples_frame)
        self._new_sample_frame.pack(side=TOP)

        self._editing_sample = sample

        new_sample_fields_frame = Frame(self._new_sample_frame)
        new_sample_fields_frame.pack(side=TOP)

        self._sample_edit_name = StringVar()
        Label(new_sample_fields_frame, text="Name")\
            .grid(row=0, column=0)

        Entry(new_sample_fields_frame, \
            textvariable=self._sample_edit_name)\
            .grid(row=0, column=1)

        if sample != None:
            self._sample_edit_name.set(sample.name)

        done_close_frame = Frame(self._new_sample_frame)
        done_close_frame.pack(side=TOP)

        if sample != None:
            done_button_text = "Update"
        else:
            done_button_text = "Add"

        Button(done_close_frame, text=done_button_text,
            command=lambda sample=sample: self.add_update_clicked(sample))\
            .grid(row=0,column=0)

        Button(done_close_frame, text="Cancel",
            command=self._new_sample_frame.destroy)\
            .grid(row=0,column=1)

    def add_update_clicked(self, sample):

        try:
        
            sample_name = self._sample_edit_name.get()

            if sample == None:

                sample = Library(sample_name)

            else:
                sample.name = sample_name

            self._new_sample_frame.destroy()

            self.reload()
        except Exception as exception:
            messagebox.showinfo("Error", str(exception))

    def rename_sample_clicked(self, sample_index):
        self.add_edit_sample(self._samples[sample_index])

    def delete_sample_clicked(self, sample_index):

        db.delete_sample(self._samples[sample_index])

        for dropdown in self._sample_dropdowns:
            dropdown["menu"].delete(sample_index + 1)

        self._sample_labels[sample_index].destroy()
        self._sample_rename_buttons[sample_index].destroy()
        self._sample_delete_buttons[sample_index].destroy()
        del self._sample_labels[sample_index]