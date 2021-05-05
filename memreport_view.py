# -*- coding: UTF-8 -*-
from dearpygui.core import *
from dearpygui.core import *
from dearpygui.simple import *
from dearpygui.demo import show_demo
import tkinter as tk
from tkinter import filedialog
import os
from memreport_model import *
from filemanager import *


class MainWindow():
    def __init__(self, Controller):
        add_additional_font('C:\\Windows\\Fonts\\simhei.TTF', 18, glyph_ranges='chinese_simplified_common')
        set_theme("Light")
        set_style_frame_rounding(6)

        self.Controller = Controller
        self.CreateWindow()
        # show_demo()
        start_dearpygui(primary_window = "MemreportDiff")



    def FilePicker(self, sender, data):
        tk.Tk().withdraw()
        answer = filedialog.askdirectory(initialdir=os.getcwd(),
                                        title="请选择MemReport文件夹:")
        set_value("sourceurl", answer)


    def CreateWindow(self):
        mainWindowSize = get_main_window_size()
        with window("MemreportDiff", width = mainWindowSize[0], height = mainWindowSize[1],
            x_pos = 0, y_pos = 0, no_move = True, no_collapse = True, no_title_bar = True, menubar = True):
            add_input_text("##sourceurl", source = "sourceurl", hint = "url或者文件夹路径")
            add_same_line()
            add_button("打开文件夹", callback=self.FilePicker)
            add_same_line()

            add_button("加载所有文件", callback = self.Controller.LoadAllFiles)
            add_separator()
            add_spacing(count = 2)


            add_text("Diff Start")
            add_same_line()
            add_combo("##DiffStart", width = 400, callback = self.Controller.OnSelectDiffStart)

            add_same_line()
            add_text("Diff End")
            add_same_line()
            add_combo("##DiffEnd", width = 400, callback = self.Controller.OnSelectDiffEnd)

            add_same_line()
            add_button("Go", callback = self.Controller.Diff)

            add_text("统计对比")
            add_table("Table##Summary", ["类型", "占用[MB]", "Diff Start占用[MB]", "Diff End占用(MB)"], height = 200)
            

            add_text("Object对比")
            add_same_line()
            add_text("Sort")
            add_same_line()
            add_combo("##Sort",default_value = "CountIncrease", items=["Class", "CountIncrease", "NumKBIncrease", "MaxKBIncrease"], callback = self.Controller.OnSortTypeChange)

            self.AddObjectDiffTable()

    def AddObjectDiffTable(self):
        add_table("Table##ObjectDiff", ["Class", "CountIncrease", "Count Start", "Count End", "NumKBIncrease", "NumKB Start", "NumKB End", "MaxKBIncrease", "MaxKB Start", "MaxKB End"], height = -1)