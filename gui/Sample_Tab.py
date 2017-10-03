from .Tab import *
from tkinter import messagebox
from workspace import Database as db
from workspace.Library import Library

class Sample_Tab(Tab):

    def __init__(self, master, **kwargs):

        Tab.__init__(self, master, **kwargs)

        self._samples_frame = Frame(self)
        self._samples_frame.pack(side=LEFT)

        self._existing_samples_frame = Frame(self._samples_frame)
        self._existing_samples_frame.pack()

        self._add_sample_button = Button(self._samples_frame, \
            text="Add Sample", command=self.add_sample_clicked)

        self._add_sample_button.pack()

        self._FASTQ_frame = Frame(self)
        self._FASTQ_frame.pack()

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

        for sample in self._samples:

            Label(self._sample_list_frame, text=sample.name)\
                .grid(row = sample_index, column = 0)

            Button(self._sample_list_frame, text="Rename", \
                command=lambda index=sample_index: \
                self.rename_sample_clicked(index))\
                .grid(row = sample_index, column=1, sticky="news")

            Button(self._sample_list_frame, text="Delete", \
                command=lambda index=sample_index: \
                self.delete_sample_clicked(index))\
                .grid(row = sample_index, column=2, sticky="news")

            sample_index += 1

    def load_FASTQ_files(self):

        self._FASTQ_files = db.get_FASTQ_files()

        if self._FASTQ_list_frame != None:
            self._FASTQ_list_frame.destroy()

        self._FASTQ_list_frame = Frame(self._FASTQ_frame)
        self._FASTQ_list_frame.pack()

        self._FASTQ_scroll_area = self.scroll_area(self._FASTQ_list_frame, \
            height=self.winfo_toplevel().winfo_height())

        FASTQ_file_index = 0

        for FASTQ_file in self._FASTQ_files:

            Label(self._FASTQ_scroll_area, text=FASTQ_file.name)\
                .grid(row = FASTQ_file_index, column = 0)
            
            FASTQ_file_index += 1

        Grid.columnconfigure(self._FASTQ_scroll_area, 0, weight=1)

    def add_sample_clicked(self):
        self.add_edit_sample()

    def add_edit_sample(self, sample = None):

        if self._new_sample_frame != None:
            self._new_sample_frame.destroy()

        self._new_sample_frame = Frame(self._samples_frame)
        self._new_sample_frame.pack()

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

        self.reload()