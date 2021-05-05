# -*- coding: UTF-8 -*-

from dearpygui.core import *
from dearpygui.simple import *
from dearpygui.demo import show_demo
import tkinter as tk
from tkinter import filedialog
import os
from memreport_model import *
from filemanager import *
from memreport_view import *


class MemreportDiff():
    def __init__(self):
        self.filemanager = FileManager()
        self.DiffStartMp = None
        self.DiffEndMp = None 
        self.DiffStart = None
        self.DiffEnd = None
        self.DiffInfo = None
        pass

    def LoadAllFiles(self):
        self.filemanager.LoadAllFiles(get_value("sourceurl"))
        configure_item("##DiffStart", items = self.filemanager.file_list)
        configure_item("##DiffEnd", items = self.filemanager.file_list)
        

    def OnSelectDiffStart(self, sender, data):
        self.DiffStart = MemoryReportInfo(self.filemanager.GetUrlByFile(get_value(sender)))

    def OnSelectDiffEnd(self, sender, data):
        self.DiffEnd = MemoryReportInfo(self.filemanager.GetUrlByFile(get_value(sender)))

    def Diff(self, sender = None, data = None):
        print("Diff" + str(self.DiffStart) + " " + str(self.DiffEnd))
        self.DiffInfo = MemoryReportDiffInfo(self.DiffStart, self.DiffEnd)
        self.RefreshObjTable(ObjectSortType.CountIncrease)

    def RefreshSummaryTable(self):
        pass

    def RefreshObjTable(self, sortType):
        TableData = []
        UObjectDiffInfo.SortType = sortType
        objDiffs = sorted(self.DiffInfo.ObjDiffs)

        TotalInfo = UObjectDiffInfo()
        for ObjDiff in objDiffs:
            TotalInfo += ObjDiff
        TotalInfo.Clsname = "*Total*"
        objDiffs.append(TotalInfo)

        for ObjDiffInfo in objDiffs:
            if ObjDiffInfo.CountDiff != 0:
                row = [ObjDiffInfo.Clsname, ObjDiffInfo.CountDiff, ObjDiffInfo.o1.Count, ObjDiffInfo.o2.Count, ObjDiffInfo.NumKBDiff, ObjDiffInfo.o1.NumKB, ObjDiffInfo.o2.NumKB, ObjDiffInfo.MaxKBDiff, ObjDiffInfo.o1.MaxKB, ObjDiffInfo.o2.MaxKB]
                TableData.append(row)



        set_table_data("Table##ObjectDiff", TableData)

    def OnSortTypeChange(self, sender, data):
        sortStr = get_value(sender)
        self.RefreshObjTable(ObjectSortType[sortStr])


def main():
    controller = MemreportDiff()
    # show_demo()
    MainWindow(controller)


if __name__ == '__main__':
    main()
