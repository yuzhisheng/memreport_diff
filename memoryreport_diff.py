# -*- coding: UTF-8 -*-

from dearpygui.core import *
from dearpygui.simple import *
from dearpygui.demo import show_demo
import tkinter as tk
from tkinter import filedialog
import os



# add_additional_font('C:\\Windows\\Fonts\\simhei.TTF', 18, glyph_ranges='chinese_simplified_common')


def file_picker(sender, data):
    tk.Tk().withdraw()
    answer = filedialog.askdirectory(initialdir=os.getcwd(),
                                    title="Please select a folder:")
    print(answer)




# def apply_selected_file(sender, data):
#     log_debug(data)  # so we can see what is inside of data
#     directory = data[0]
#     file = data[1]
#     set_value("directory", directory)
#     set_value("file", file)
#     set_value("file_path", f"{directory}\\{file}")


with window("Tutorial"):
    add_button("Directory Selector", callback=file_picker)
    add_text("Directory Path: ")
    add_same_line()
    add_label_text("##filedir", source="directory", color=[255, 0, 0])
    add_text("File: ")
    add_same_line()
    add_label_text("##file", source="file", color=[255, 0, 0])
    add_text("File Path: ")
    add_same_line()
    add_label_text("##filepath", source="file_path", color=[255, 0, 0])


show_demo()
start_dearpygui()

