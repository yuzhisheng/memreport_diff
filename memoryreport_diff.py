# -*- coding: UTF-8 -*-

from dearpygui.core import *
from dearpygui.simple import *
from dearpygui.demo import show_demo
import tkinter as tk
from tkinter import filedialog
import os



class MainWindow():
    def __init__(self):
        add_additional_font('C:\\Windows\\Fonts\\simhei.TTF', 18, glyph_ranges='chinese_simplified_common')
        set_theme("Light")
        set_style_frame_rounding(6)

        self.CreateWindow()

        # show_demo()
        start_dearpygui(primary_window = "MemreportDiff")

    def file_picker(self, sender, data):
        tk.Tk().withdraw()
        answer = filedialog.askdirectory(initialdir=os.getcwd(),
                                        title="Please select a folder:")
        set_value("sourceurl", answer)


    def CreateWindow(self):
        mainWindowSize = get_main_window_size()
        with window("MemreportDiff", width = mainWindowSize[0], height = mainWindowSize[1],
            x_pos = 0, y_pos = 0, no_move = True, no_collapse = True, no_title_bar = True, menubar = True):
            add_input_text("##sourceurl", source = "sourceurl", hint = "url或者文件夹路径")
            add_same_line()
            add_button("打开文件夹", callback=self.file_picker)
            add_same_line()

            add_button("加载所有文件", callback=self.file_picker)
            add_separator()
            add_spacing(count = 2)


            add_text("Diff Start")
            add_same_line()
            add_combo("##DiffStart", width = 200)

            add_same_line()
            add_text("Diff End")
            add_same_line()
            add_combo("##DiffEnd", width = 200)


def main():
    MainWindow()

if __name__ == '__main__':
    main()
