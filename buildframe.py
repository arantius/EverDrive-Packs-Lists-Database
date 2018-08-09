#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Graphical User Iterface for build_pack and parse_pack scripts.
"""


import tkinter as tk
from tkinter import *
from tkinter import ttk


__author__ = "aleyr"
__date__ = "2018/08/09"
__version__ = "$Revision: 0.3"


class BuildFrame(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)

        self.parent = parent

        self.grid(column=0, row=0, sticky=(N, W, E, S))
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.path_dir_roms = StringVar()
        self.path_pack_file = StringVar()
        self.path_dir_pack = StringVar()
        self.path_missing_file = StringVar()
        self.file_strategy = IntVar()
        self.overwrite = IntVar()

        # self.file_strategy.set(0)
        # self.overwrite.set(1)

        # ROMs directory
        textbox_roms = Entry(self, width=50, textvariable=self.path_dir_roms)
        textbox_roms.grid(column=2, row=1, sticky=E)
        ttk.Label(self, text="ROMs folder: "
                  ).grid(column=1, row=1, sticky=W)
        ttk.Button(self, text="Browse",
                   command=lambda:
                   select_folder(self.path_dir_roms, "Select ROMs folder")
                   ).grid(column=3, row=1, sticky=W)

        # SMDB file
        textbox_pack_file = Entry(self, width=50,
                                  textvariable=self.path_pack_file)
        textbox_pack_file.grid(column=2, row=2, sticky=E)
        ttk.Label(self, text="SMDB/pack file: "
                  ).grid(column=1, row=2, sticky=W)
        ttk.Button(self, text="Browse",
                   command=lambda:
                   select_file_open(self.path_pack_file,
                                    "Select SMDB/pack file")
                   ).grid(column=3, row=2, sticky=W)

        # Pack directory
        textbox_pack = Entry(self, width=50, textvariable=self.path_dir_pack)
        textbox_pack.grid(column=2, row=3, sticky=E)
        ttk.Label(self, text="Pack folder: "
                  ).grid(column=1, row=3, sticky=W)
        ttk.Button(self, text="Browse",
                   command=lambda:
                   select_folder(self.path_dir_pack, "Select Pack folder")
                   ).grid(column=3, row=3, sticky=W)

        # Missing file
        textbox_missing_file = Entry(self, width=50,
                                     textvariable=self.path_missing_file)
        textbox_missing_file.grid(column=2, row=4, sticky=E)
        ttk.Label(self, text="Missing file: "
                  ).grid(column=1, row=4, sticky=W)
        ttk.Button(self, text="Browse",
                   command=lambda:
                   select_file_save(self.path_missing_file,
                                    "Save missing file")
                   ).grid(column=3, row=4, sticky=W)

        ttk.Label(self, text="File strategy: "
                  ).grid(column=1, row=5, sticky=W)
        Radiobutton(self, text="Copy", variable=self.file_strategy, value=0
                    ).grid(column=2, row=5, sticky=W)
        Radiobutton(self, text="HardLink", variable=self.file_strategy, value=1
                    ).grid(column=2, row=6, sticky=W)

        ttk.Label(self, text="Skip existing: "
                  ).grid(column=1, row=7, sticky=W)
        Checkbutton(self, text="", variable=self.overwrite
                    ).grid(column=2, row=7, sticky=W)
        self.overwrite.set(1)

        button_frame = ttk.Frame(self)
        ttk.Button(button_frame, text="Clear", underline=0,
                   command=lambda:
                   self.click_clear()
                   ).grid(column=1, row=1, sticky=E)
        self.parent.bind("<Alt_L><c>", lambda e: self.click_clear())
        ttk.Button(button_frame, text="Command", underline=2,
                   command=lambda:
                   self.click_command()
                   ).grid(column=2, row=1, sticky=E)
        self.parent.bind("<Alt_L><m>", lambda e: self.click_command())
        # ttk.Button(button_frame, text="Build", underline=0,
        #            command=lambda:
        #            self.click_build()
        #            ).grid(column=3, row=1, sticky=W)
        # self.parent.bind("<Alt_L><b>", lambda e: self.click_build())
        button_frame.grid(column=2, row=8, columnspan=3, sticky=E)

        textbox_roms.focus_set()

    def click_clear(self):
        self.path_dir_roms.set('')
        self.path_pack_file.set('')
        self.path_dir_pack.set('')
        self.path_missing_file.set('')
        self.file_strategy.set(0)
        self.overwrite.set(1)

    def click_command(self):
        if self.validate_info():
            cmd = create_command(input_folder=self.path_dir_roms.get(),
                                 database=self.path_pack_file.get(),
                                 output_folder=self.path_dir_pack.get(),
                                 missing=self.path_missing_file.get(),
                                 file_strategy=self.file_strategy.get(),
                                 skip_eisting=self.overwrite.get())
            TextMessage().popup("Python command", cmd)

    def validate_info(self):
        out = False
        if (not self.path_dir_roms.get() == "" and
                os.path.lexists(self.path_dir_roms.get()) and
                not self.path_pack_file.get() == "" and
                not self.path_dir_pack.get() == ""):
            out = True
        else:
            error_msg = ""
            if self.path_dir_roms.get() == "":
                error_msg += "ROMs folder is a required field.\n"
            if not os.path.lexists(self.path_dir_roms.get()):
                error_msg += "ROMs folder does not exist, "
                error_msg += "please select a valid folder.\n"
            if self.path_pack_file.get() == "":
                error_msg += "SMDB/pack file is a required field.\n"
            if self.path_dir_pack.get() == "":
                error_msg += "Pack folder is a required field.\n"
            TextMessage().popup("Error", error_msg)

        return out

    def click_build(self):
        if self.validate_info():
            print("Build")


