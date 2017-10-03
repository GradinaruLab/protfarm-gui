from .Tab import *
from tkinter import messagebox
from workspace import Database as db
from workspace.Template import Template

class Template_Tab(Tab):

    def __init__(self, master, **kwargs):

        Tab.__init__(self, master, **kwargs)

        self._templates_frame = Frame(self)
        self._templates_frame.pack()
        self._existing_templates_frame = Frame(self._templates_frame)
        self._existing_templates_frame.pack()
        self._new_template_frame = None
        self._existing_templates_table = None

        self._add_template_button = Button(self._templates_frame,
            text='Add template',
            command=self.add_template_clicked)
        self._add_template_button.pack(side=TOP)

    def reload(self):
        self.load_templates()

    def load_templates(self):

        self._templates = db.get_templates()

        if self._existing_templates_table != None:
            self._existing_templates_table.destroy()

        self._existing_templates_table = Frame(self._existing_templates_frame)
        self._existing_templates_table.pack()

        Label(self._existing_templates_table, text="Name")\
            .grid(row = 0, column = 0)
        Label(self._existing_templates_table, text="Sequence")\
            .grid(row = 0, column = 1)
        Label(self._existing_templates_table, text="Reverse complement")\
            .grid(row = 0, column = 2)

        i = 1
        for template in self._templates:
            Label(self._existing_templates_table, text=template.name, bd=1, relief="solid")\
                .grid(row = i, column=0, sticky="news")
            Label(self._existing_templates_table, text=template.sequence, bd=1, relief="solid")\
                .grid(row = i, column=1, sticky="news")

            if template.reverse_complement_template_id != None:
                reverse_complement_name = db.get_template_by_id(\
                    template.reverse_complement_template_id).name
            else:
                reverse_complement_name = ""

            Label(self._existing_templates_table, text=reverse_complement_name,\
                bd=1, relief="solid")\
                .grid(row = i, column=2, sticky="news")

            Button(self._existing_templates_table, text="Edit", \
                command=lambda index=i-1: self.edit_template_clicked(index))\
                .grid(row = i, column=3, sticky="news")

            Button(self._existing_templates_table, text="Delete", \
                command=lambda index=i-1: self.delete_template_clicked(index))\
                .grid(row = i, column=4, sticky="news")

            i += 1

    def delete_template_clicked(self, template_index):

        template_to_delete = self._templates[template_index]

        alignments = db.get_alignments()

        template_in_use = False

        for alignment in alignments:
            for library, template in alignment.library_templates.items():
                if template == template_to_delete.id:
                    template_in_use = True
                    break

        if template_to_delete.reverse_complement_template_id != None:
            reverse_complement_template = db.get_template_by_id(\
                template_to_delete.reverse_complement_template_id)

            for alignment in alignments:
                for library, template in alignment.library_templates.items():
                    if template == reverse_complement_template.id:
                        template_in_use = True
                        break

        if template_in_use:
            messagebox.showinfo("Error", "Template in use, cannot delete")
        else:
            db.delete_template(template_to_delete)

        self.load_templates()

    def add_template_clicked(self):

        self.add_edit_template()

    def add_edit_template(self, template = None):

        if self._new_template_frame != None:
            self._new_template_frame.destroy()

        self._editing_template = template
        self._new_template_frame = Frame(self._templates_frame)
        self._new_template_frame.pack(side=TOP)

        new_template_fields_frame = Frame(self._new_template_frame)
        new_template_fields_frame.pack(side=TOP)

        Label(new_template_fields_frame, text="Name")\
            .grid(row=0, column=0, sticky="e")
        Label(new_template_fields_frame, text="Sequence")\
            .grid(row=1, column=0, sticky="e")
        Label(new_template_fields_frame, text="Reverse Complement Sequence")\
            .grid(row=2, column=0, sticky="e")

        self._template_edit_name = StringVar()
        Entry(new_template_fields_frame, textvariable=self._template_edit_name)\
            .grid(row=0, column=1, sticky="w")

        if template != None:
            self._template_edit_name.set(template.name)

        self._template_edit_sequence = StringVar()
        Entry(new_template_fields_frame, width=150, \
            textvariable=self._template_edit_sequence)\
            .grid(row=1, column=1, sticky="w")

        if template != None:
            self._template_edit_sequence.set(template.sequence)

        templates = db.get_templates()
        self._selected_reverse_complement = StringVar()

        template_names = ["(None)"]

        if template != None and template.reverse_complement_template_id != None:
            self._selected_reverse_complement.set(db.get_template_by_id(\
                template.reverse_complement_template_id).name)
        else:
            self._selected_reverse_complement.set(template_names[0])

        template_names.extend([template.name for template in templates])

        reverse_complement_dropdown = OptionMenu(new_template_fields_frame,\
            self._selected_reverse_complement, *template_names)

        reverse_complement_dropdown.grid(row=2, column=1, sticky="w")

        if template != None:
            done_button_text = "Update"
        else:
            done_button_text = "Add"

        done_close_frame = Frame(self._new_template_frame)
        done_close_frame.pack(side=TOP)

        Button(done_close_frame, text=done_button_text,
            command=lambda template=template: self.add_update_clicked(template))\
            .grid(row=0,column=0)

        Button(done_close_frame, text="Cancel",
            command=self._new_template_frame.destroy)\
            .grid(row=0,column=1)

    def add_update_clicked(self, template):

        try:
        
            if template == None:

                template_name = self._template_edit_name.get()
                template_sequence = self._template_edit_sequence.get()
                reverse_complement_name = self._selected_reverse_complement.get()
                if reverse_complement_name == "(None)":
                    reverse_complement_template_id = None
                else:
                    reverse_complement_template = db.get_template_by_name(reverse_complement_name)
                    reverse_complement_template_id = reverse_complement_template.id

                new_template = Template(template_sequence, template_name, \
                    reverse_complement_template_id = reverse_complement_template_id)
            else:

                template.name = self._template_edit_name.get()
                template.sequence = self._template_edit_sequence.get()
                reverse_complement_name = self._selected_reverse_complement.get()

                if reverse_complement_name == "(None)":
                    reverse_complement_template_id = None
                else:
                    reverse_complement_template = db.get_template_by_name(reverse_complement_name)
                    reverse_complement_template_id = reverse_complement_template.id

                template.reverse_complement_template_id = reverse_complement_template_id
        except Exception as exception:
            messagebox.showinfo("Error", str(exception))

        self._new_template_frame.destroy()
        self.load_templates()

    def edit_template_clicked(self, index):
        self.add_edit_template(self._templates[index])