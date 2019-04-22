from decimal import *
from protfarm.workspace import Database as db
from .Tab import *


class Alignment_Statistics_Tab(Tab):
    """Instant of the analysis tab"""

    def __init__(self, master, **kwargs):
        """Initializes the current tab"""
        self.selected_libraries = []
        self.selected_alignments = []
        self.by_alignment = True

        Tab.__init__(self, master, **kwargs)

        self.left_frame = Frame(self, bg = '#1f1f1f', relief=GROOVE, bd = 2)
        self.right_frame = Frame(self, relief=GROOVE, bd = 2)

        self.first_left_frame = Frame(self.left_frame)
        self.second_left_frame = Frame(self.left_frame)

        Label(self.first_left_frame, text = 'Samples').pack(side=TOP)
        Label(self.second_left_frame, text = 'Alignments').pack(side=TOP)
    
        all_libs = StringVar()
        all_aligns = StringVar()
        all_libs.set(0)
        all_aligns.set(0)
        self.select_all_libs = Checkbutton(self.first_left_frame,
            text='Select All',     variable = all_libs)
        self.select_all_aligns = Checkbutton(self.second_left_frame,
            text='Select All', variable = all_aligns)
        self.select_all_aligns.pack(side=TOP)
        self.select_all_libs.pack(side=TOP)
        height = self.winfo_screenheight()*0.3
        self.library_wrapper = self.scroll_area(self.first_left_frame,
            height=height)
        self.alignment_wrapper = self.scroll_area(self.second_left_frame,
            height=height)

        self.library_lines = []
        self.alignment_lines = []
        self.methods = []
        
        self.update_lists()

        self.select_all_libs['command'] = \
            lambda: self.select_all(self.library_wrapper, self.select_all_libs)
        self.select_all_aligns['command'] = \
            lambda: self.select_all(self.alignment_wrapper,
                self.select_all_aligns)
        self.select_all_libs.var = all_libs
        self.select_all_aligns.var = all_aligns

        self.resize_bar(self.right_frame, orient='y')

        self.table_wrapper = Frame(self.right_frame)
        height = self.winfo_screenheight()*0.8
        self.table_frame = self.scroll_area(self.table_wrapper, scroll_x=True,
            height=height)
        self.table_frame.bind('<Button-4>', lambda e:self.scroll(e))
        self.table_frame.bind('<Button-5>', lambda e:self.scroll(e))
        self.table_frame.bind('<Control-4>', lambda e:self.scroll_x(e))
        self.table_frame.bind('<Control-5>', lambda e:self.scroll_x(e))

        self.button_frame = Frame(self.right_frame)
        swap_button = Button(self.button_frame, text='Swap', command=self.swap)

        export_button = Button(self.button_frame, text='Export to CSV',
            command=self.export)
        export_button.pack(side=RIGHT, fill='y')

        selected_method = StringVar()
        try:
            active_alignment = ws.get_active_alignment()
            selected_method.set(active_alignment.name)
        except:
            pass

        swap_button.pack(side = LEFT, fill='y')
        try:
            frame = Frame(self.button_frame)
            select_best = OptionMenu(frame, selected_method, \
                *self.methods, command=self.method_selected)
            # select_best.pack(side = TOP, fill='y')
            lab = Label(frame, text='Selected method:')
            lab.pack(side=LEFT, padx=5)
            select_best.pack(side=LEFT, padx=5)
            frame.pack(side = TOP, fill='y')

        except:
            pass

        self.button_frame.pack(side=BOTTOM, fill = 'x', padx=5, pady=5)
        offset = 0.02
        # self.table_frame.pack()
        # self.table_wrapper.place(relx = 0+offset, rely = 0, relheight=1.0,
        #     relwidth=1.0-offset)
        self.table_wrapper.pack(side=TOP, fill =BOTH)

        ratio = 0.1

        self.left_frame.place(relx=0, rely=0, relheight=1.0, relwidth=ratio)
        self.right_frame.place(relx=ratio, rely=0, relheight=1.0,
            relwidth=1-ratio)
        ratio = 0.5
        self.first_left_frame.place(relx = 0, rely = 0, relwidth = 1.0,
            relheight = ratio)
        self.second_left_frame.place(relx = 0, rely = ratio, relwidth = 1.0,
            relheight = 1-ratio)
    
    def select_all(self, frame, widget):
        value = bool(int(widget.var.get()))
        if value:
            for line in frame.winfo_children():
                line.ch_btn.deselect()
                line.ch_btn.invoke()
        else:
            for line in frame.winfo_children():
                line.ch_btn.select()
                line.ch_btn.invoke()

    def method_selected(self, selected_method_name):

        alignment = db.get_alignment(selected_method_name)
        ws.set_active_alignment(alignment)
        
    def export(self):
        ws.export_alignment_statistics()

    def swap(self):
        self.by_alignment = not self.by_alignment
        self.display_table()

    def update_lists(self):
        self.library_lines = []
        self.alignment_lines = []

        self.methods = [alignment.name for alignment in db.get_alignments()]


        for child in self.library_wrapper.winfo_children():
            child.destroy()
        for child in self.alignment_wrapper.winfo_children():
            child.destroy()
        
        i = 0
        for library in db.get_libraries():
            line = Frame(self.library_wrapper)
            line.id = library.id
            line.name = library.name
            line.var = StringVar()
            line.var.set('0')
            line.ch_btn = Checkbutton(line, text = line.name,
                variable=line.var)
            line.ch_btn.pack(side=LEFT, fill=BOTH)
            line.ch_btn['command'] = lambda index=i: \
                self.add_library_to_comparison(index)
            btn = Button(line, text='Files')
            btn.bind("<Button-1>",self.view_files)
            btn.pack(side=RIGHT, pady = 2, padx=2)
            line.pack(side=TOP, fill=BOTH)
            self.library_lines.append(line)

            line.bind("<Button-4>", self.scroll)
            line.bind("<Button-5>", self.scroll)
            line.ch_btn.bind("<Button-4>", self.scroll)
            line.ch_btn.bind("<Button-5>", self.scroll)
            btn.bind("<Button-4>", self.scroll)
            btn.bind("<Button-5>", self.scroll)
            i+=1

        i = 0
        for alignment in db.get_alignments():
            line = Frame(self.alignment_wrapper)
            line.id = alignment.id
            line.name = alignment.name
            line.var = StringVar()
            line.var.set('0')
            line.ch_btn = Checkbutton(line, text = line.name,
                variable=line.var)
            line.ch_btn.pack(side=LEFT, fill=BOTH)
            line.ch_btn['command'] = \
                lambda index=i: self.add_alignment_to_comparison(index)
            btn = Button(line, text='Parameters')
            btn.bind("<Button-1>", lambda e: self.view_parameters(e))
            btn.pack(side=RIGHT, pady = 2, padx=2)
            line.pack(side=TOP, fill=BOTH)
            self.alignment_lines.append(line)
            i += 1

    def reload(self):
        self.update_lists()

    def add_alignment_to_comparison(self, index):
        widget = self.alignment_wrapper.winfo_children()[index]
        old = bool(int(widget.var.get()))
        self.selected_alignments = [line for line in self.alignment_lines\
            if line.var.get() in ["1",1]][:]

        self.display_table()
        
    def add_library_to_comparison(self, index):
        widget = self.library_wrapper.winfo_children()[index]
        old = bool(int(widget.var.get()))
        self.selected_libraries = [line for line in self.library_lines\
            if line.var.get() in ["1",1]][:]

        self.display_table()

    def view_files(self, event):
        parent = event.widget.master
        grid_kwargs = {
            'padx': 1,
            'pady': 1,
            'sticky': 'news',
            'column': 0
            }

        if hasattr(self, 'file_viewer'):
            self.file_viewer.destroy()
        self.file_viewer = Toplevel(padx=10, pady=10)
        self.file_viewer.title('Files in '+str(parent.id))

        Label(self.file_viewer, text = 'FASTQ file', bg='white')\
            .grid(**grid_kwargs)
        i = 1
        files = db.get_library_by_id(str(parent.id)).fastq_files
        for file in files:
            Label(self.file_viewer, text=str(file), bg='white')\
            .grid(row=i, **grid_kwargs)
            i+=1

    def view_parameters(self, event):
        parent = event.widget.master
        grid_kwargs = {
            'padx': 1,
            'pady': 1,
            'sticky': 'news',
            'ipadx': 5,
            'ipady': 5
            }

        if hasattr(self, 'parameter_viewer'):
            self.parameter_viewer.destroy()

        self.parameter_viewer = Toplevel(padx=10, pady=10)
        self.parameter_viewer.title('Parameters for '+parent.name)

        Label(self.parameter_viewer, text = 'Parameter', bg = 'white')\
            .grid(row=0, column=0, **grid_kwargs)
        Label(self.parameter_viewer, text = 'Value', bg = 'white')\
            .grid(row=0, column=1, **grid_kwargs)
        i = 1

        for parameter, value in db.get_alignment_by_id(str(parent.id))\
            .parameters.items():
            Label(self.parameter_viewer, text = parameter, bg = 'white',
                anchor='e')\
                .grid(row=i, column=0, **grid_kwargs)
            Label(self.parameter_viewer, text = value, bg = 'white')\
                .grid(row=i, column=1, **grid_kwargs)
            i += 1

    def display_table(self):

        for child in self.table_frame.winfo_children():
            child.destroy()

        libraries = self.selected_libraries[:]
        aligns = self.selected_alignments[:]
        self.columns = []
        h1_font = font.Font(weight=font.BOLD)

        # If table is to be sorted by alignment
        if self.by_alignment:
            
            # Loop through alignments to create labels
            for i, alignment in enumerate(aligns):
                align_name = alignment.name
                index = i*(len(libraries))+i+1
                method_label = Label(self.table_frame, text=align_name, padx=1,
                    pady=1, bg ='white', font = h1_font)
                method_label.grid(column=0, row=index,
                    sticky = 'news', columnspan=2, pady = 2, padx = 2)

                alignment_id = alignment.id
                getcontext().prec = 4
                # Loop through libraries for data rows in table
                for j, library in enumerate(libraries):
                    name = library.name
                    offset = index + j + 1
                    Label(self.table_frame, text=name, padx= 1, pady=1,
                        bg ='white').grid(column=1, row=offset,
                        sticky = 'news', pady = 2, padx = 2)
                    library_id = library.id
                    try:
                        stats = db.get_alignment_by_id(alignment_id).statistics
                        stats = stats[library_id]

                        # Loop through statistics for to put in table
                        for stat, value in stats.items():

                            # If stat has not yet been displayed, add a column
                            if stat not in self.columns:
                                self.columns.append(stat)
                                col_num = len(self.columns)-1+2
                                Label(self.table_frame, text = stat,
                                    bg='white')\
                                .grid(row = 0, column = col_num,
                                    sticky ='news', pady = 2, padx = 2)
                                Grid.columnconfigure(self.table_frame, col_num,
                                    weight = 1)
                            if (int(value) != float(value) and
                                float(value) != 0.0):                            
                                value = \
                                    str(Decimal(float(value))/Decimal(0.01)) \
                                    + '%'

                            k = self.columns.index(stat)
                            label = Label(self.table_frame, text=str(value),
                                bg = 'white')
                            label.grid(row = offset, column = k+2, pady = 2,
                                padx = 2, sticky = 'news')
                            label.bind('<Button-4>', lambda e: self.scroll(e))
                            label.bind('<Button-5>', lambda e: self.scroll(e))
                    except:
                        pass
        # If the table is to be sorted by library
        else:
            for i, library in enumerate(libraries):
                lib_name = library.name
                index = i*(len(aligns))+i+1
                lib_label = Label(self.table_frame, text=lib_name, padx= 1,
                    pady=1, bg ='white', font = h1_font)
                lib_label.grid(column=0, row=index, sticky = 'news',
                    columnspan=2, padx=2, pady=2)

                library_id = library.id
                for j, alignment in enumerate(aligns):
                    name = alignment.name    
                    offset = index + j + 1
                    Label(self.table_frame, text=name, padx= 1, pady=1,
                        bg ='white').grid(column=1, row=offset, sticky='news',
                        pady=2, padx=2)
                    alignment_id = alignment.id
                    try:
                        stats = db.get_alignment_by_id(alignment_id).statistics
                        stats = stats[library_id]
                        for stat, value in stats.items():
                            if stat not in self.columns:
                                self.columns.append(stat)
                                col_num = len(self.columns)-1+2
                                Label(self.table_frame, text = stat,
                                    bg='white')\
                                .grid(row = 0, column = col_num,
                                    sticky ='news', pady = 2, padx = 2)
                                Grid.columnconfigure(self.table_frame, col_num,
                                    weight = 1)
                            if (int(value) != float(value) and
                                float(value) != 0.0):                            
                                value = \
                                    str(Decimal(float(value))/Decimal(0.01)) \
                                    + '%'

                            k = self.columns.index(stat)
                            label = Label(self.table_frame, text=value,
                                bg = 'white')
                            label.grid(row = offset, column = k+2, pady = 2,
                                padx = 2, sticky = 'news')
                            label.bind('<Button-4>', lambda e: self.scroll(e))
                            label.bind('<Button-5>', lambda e: self.scroll(e))
                    except:
                        pass