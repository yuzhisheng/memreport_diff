# -*- coding: UTF-8 -*-

import re
import os
import sys
from optparse import OptionParser
import urllib.request
import time
import shutil
from enum import Enum

os.chdir(".")

class ObjectSortType(Enum):
    Class = 1
    CountIncrease = 2
    NumKBIncrease = 3
    MaxKBIncrease = 4

class UObjectInfo():
    def __init__(self, line = ""):
        self.Clsname = ""
        self.Count = 0
        self.NumKB = 0
        self.MaxKB = 0
        self.precision = 2
        self.ParseFromeLine(line)

    def ParseFromeLine(self,line):
        if line == "":
            return
        ls = line.split()
        if len(ls) < 4:
            return

        self.Clsname = ls[0]
        self.Count = int(ls[1])
        self.NumKB = float("{:.2f}".format(float(ls[2])))
        self.MaxKB = float("{:.2f}".format(float(ls[3])))

    def __iadd__(self, other):
        self.Count += other.Count
        self.NumKB += other.NumKB
        self.MaxKB += other.MaxKB
        return self


class UObjectDiffInfo():
    SortType = ObjectSortType.CountIncrease

    def __init__(self, o1 = None, o2 = None):
        self.Clsname = ""
        self.CountDiff = 0
        self.NumKBDiff = 0
        self.MaxKBDiff = 0
        self.o1 = o1
        self.o2 = o2
        if not o2:
            self.o2 = UObjectInfo()
        if not o1:
            self.o1 = UObjectInfo()

        self.Diff()

    def __lt__(self, other):
        if UObjectDiffInfo.SortType == ObjectSortType.CountIncrease:
            return self.CountDiff > other.CountDiff
        elif UObjectDiffInfo.SortType == ObjectSortType.Class:
            return self.Clsname < other.Clsname
        elif UObjectDiffInfo.SortType == ObjectSortType.NumKBIncrease:
            return self.NumKBDiff > other.NumKBDiff
        else:
            return self.MaxKBDiff > other.MaxKBDiff

    def __iadd__(self, other):
        self.o1 += other.o1
        self.o2 += other.o2
        self.Diff()
        return self

    def Diff(self):
        self.Clsname = self.o1.Clsname or self.o2.Clsname
        self.CountDiff = self.o2.Count - self.o1.Count
        self.NumKBDiff = float("%.2f"%(self.o2.NumKB - self.o1.NumKB))
        self.MaxKBDiff = float("%.2f"%(self.o2.MaxKB - self.o1.MaxKB))

    @staticmethod
    def Fmt():
        return "{0:>65}\t{1:>20}\t{2:>25}\t{3:>15}\t{4:>25}\t{5:>15}\t{6:>25}\n"

    @staticmethod
    def Title():
        return UObjectDiffInfo.Fmt().format("Class", "Count_Increase", "Count_Increase_Detail", "NumKB_Increase", "NumKB_Increase_Detail", "MaxKB_Diff", "MaxKB_Diff_Detail")

    def GetInfoLine(self):
        if self.CountDiff == 0:
            return ""
        CountDiffDetail = "%d -> %d"%(self.o1.Count, self.o2.Count)
        NumKBDiffDetail = "%.2f -> %.2f"%(self.o1.NumKB, self.o2.NumKB)
        MaxKBDiffDetail = "%.2f -> %.2f"%(self.o1.MaxKB, self.o2.MaxKB)
        return UObjectDiffInfo.Fmt().format(self.Clsname, self.CountDiff, CountDiffDetail, "%.2f"%(self.NumKBDiff), NumKBDiffDetail, "%.2f"%(self.MaxKBDiff), MaxKBDiffDetail)  

class MemoryReportInfo():
    def __init__(self, path):
        self.path = path
        self.lines = []
        self.ObjectInfos = {}

        #summary
        self.SummaryMemoryList = []
        self.CommonSummaryReg = re.compile(r".*?\s(?P<value>(\d+\.\d+)).*")
        self.SummaryPeakReg = re.compile(r".*?(?P<value>(\d+\.\d+))\sMB\speak.*")
        
        self.StatMemoryList = []
        self.StatReg = re.compile(r"\s*?(?P<value>(\d+)).*")

        self.InitDicts()

        self.Run()

    def InitDicts(self):
        self.SummaryMemoryList.append({"key":"Process Physical Memory", "reg": self.CommonSummaryReg, "value" : .0})
        self.SummaryMemoryList.append({"key":"Process Physical Memory", "reg": self.SummaryPeakReg, "value" : .0, "des":"Process Physical Memory Peak"})
        self.SummaryMemoryList.append({"key":"Process Virtual Memory", "reg": self.CommonSummaryReg, "value" : .0})
        self.SummaryMemoryList.append({"key":"Small Pool Allocations", "reg": self.CommonSummaryReg, "value" : .0})
        self.SummaryMemoryList.append({"key":"Large Pool Requested Allocations", "reg": self.CommonSummaryReg, "value" : .0})
        self.SummaryMemoryList.append({"key":"Large Pool OS Allocated", "reg": self.CommonSummaryReg, "value" : .0})
        self.SummaryMemoryList.append({"key":"Requested Allocations", "reg": self.CommonSummaryReg, "value" : .0})
        self.SummaryMemoryList.append({"key":"OS Allocated", "reg": self.CommonSummaryReg, "value" : .0})
        self.SummaryMemoryList.append({"key":"Total allocated from OS", "reg": self.CommonSummaryReg, "value" : .0})
        self.SummaryMemoryList.append({"key":"Cached free OS pages", "reg": self.CommonSummaryReg, "value" : .0})

        self.StatMemoryList.append({"key":"PhysX Memory Used", "reg": self.StatReg, "value" : 0})
        self.StatMemoryList.append({"key":"PhysX TriMesh Used", "reg": self.StatReg, "value" : 0})
        self.StatMemoryList.append({"key":"Navigation Memory", "reg": self.StatReg, "value" : 0})
        
        
    def LoadFile(self):
        if self.path.startswith("http"):
            self.lines = urllib.request.urlopen(self.path).read().decode().split("\n")
        else:
            with open(self.path, encoding='utf8') as f:
                self.lines = f.readlines()


    def ParseSummaryInfos(self, List):
        for i, item  in  enumerate(List):
            for line in self.lines:
                if line.find(item['key']) < 0:
                    continue
                regRet = item["reg"].search(line)
                if regRet:
                    value = regRet.group("value")
                    if value.find(".") < 0:
                        value = float(value) / 1024 / 1024
                    else:
                        value = float(value)
                    List[i]["value"] = value
                    break

    def ParseObjectInfos(self):
        start_idx = 0
        for i in range(len(self.lines)):
            if self.lines[i].strip() == "Obj List:":
                start_idx = i + 4

        for i in range(start_idx, len(self.lines)):
            line = self.lines[i].strip()
            if line == "":
                return
            obj = UObjectInfo(line)
            self.ObjectInfos[obj.Clsname] = obj


    def Run(self):
        self.LoadFile()
        self.ParseObjectInfos()
        self.ParseSummaryInfos(self.SummaryMemoryList)
        self.ParseSummaryInfos(self.StatMemoryList)

class MemoryReportDiffInfo():
    def __init__(self, m1, m2):
        self.m1 = m1
        self.m2 = m2
        self.ObjDiffs = []
        self.Diff()

    def DiffSummary(self):
        pass

    def DiffObjects(self):
        for k, v in self.m1.ObjectInfos.items():
            o2 = self.m2.ObjectInfos.get(k)
            self.ObjDiffs.append(UObjectDiffInfo(v, o2))
        
        for k, v in self.m2.ObjectInfos.items():
            o1 = self.m1.ObjectInfos.get(k)
            if not o1:
                self.ObjDiffs.append(UObjectDiffInfo(o1, v))

        self.ObjDiffs = sorted(self.ObjDiffs)

    def Diff(self):
        print("正在对比%s ... %s"%(os.path.basename(self.m1.path), os.path.basename(self.m2.path)))
        self.DiffObjects()

    def Title(self):
        return "\n\n%s ... %s\n"%(os.path.basename(self.m1.path), os.path.basename(self.m2.path))

    def GetObjectDiffOutput(self):
        outLines = []
        outLines.append("\nObj List\n\n")
        outLines.append(UObjectDiffInfo.Title())
        TotalInfo = UObjectDiffInfo()
        for ObjDiff in self.ObjDiffs:
            outLines.append(ObjDiff.GetInfoLine())
            TotalInfo += ObjDiff
        TotalInfo.Clsname = "*Total*"
        outLines += "\n"
        outLines += TotalInfo.GetInfoLine()

        return outLines

    def GetSummaryDiffOutput(self, CategoryName, List1, List2):
        outLines = []
        outLines.append("\n%s\n\n"%(CategoryName))
        fmt = "{0:>65}\t{1:>20}\t{2:>25}\n"
        outLines.append(fmt.format("Type", "MemoryIncrease(MB)", "MemoryIncreaseDetail(MB)"))
        for i, item1 in enumerate(List1):
            item2 = List2[i]
            valueDiff = "%.2f -> %.2f"%(item1['value'], item2['value'])
            diffLog = fmt.format(item1.get('des') or item1.get('key'), "%.2f"%(item2['value'] - item1['value']), valueDiff)
            outLines.append(diffLog)
        return outLines

    def OutputInfo(self):
        outLines = []
        outLines += self.GetSummaryDiffOutput("Summary", self.m1.SummaryMemoryList, self.m2.SummaryMemoryList)
        outLines += self.GetSummaryDiffOutput("Stat", self.m1.StatMemoryList, self.m2.StatMemoryList)
        outLines += self.GetObjectDiffOutput()

        return outLines

class MemoryReportDiffer():
    def __init__(self, path):
        self.path = path
        self.path_list = []
        self.memoryReportInfos = []
        self.DiffInfos = []
        self.Run()

    def ParseBaseUrl(self):
        if self.path.startswith("http"):
            lines = urllib.request.urlopen(self.path).read().decode()
            self.path_list =re.findall(r"(?<=href=\").+?(?=\")|(?<=href=\').+?(?=\')" ,lines)
            for i in range(len(self.path_list)):
                self.path_list[i] = self.path + "/" + self.path_list[i]
        else:
            g = os.walk(self.path)  
            for root, _, file_list in g:  
                for file_name in file_list:  
                    if file_name.endswith(".memreport"):
                        self.path_list.append(os.path.join(root, file_name))
        self.path_list.sort()

    def ParseMemoryReportInfos(self):
        for path in self.path_list:
            self.memoryReportInfos.append(MemoryReportInfo(path))


    def DiffMemoryReports(self):
        for i in range(len(self.memoryReportInfos) - 1):
           Info = MemoryReportDiffInfo(self.memoryReportInfos[i], self.memoryReportInfos[i + 1])
           self.DiffInfos.append(Info)
        self.DiffInfos.append(MemoryReportDiffInfo(self.memoryReportInfos[0], self.memoryReportInfos[-1]))

    def Write(self):
        savePath = "./%s"%(os.path.basename(self.path))
        if os.path.exists(savePath):
            shutil.rmtree(savePath)
        os.mkdir(savePath)

        for diff in self.DiffInfos:
            OutLines = []
            OutLines.append('-' * 100 + "\n")
            OutLines += diff.Title()
            OutLines += diff.OutputInfo()
            saveFileName = "%s---%s"%(os.path.basename(diff.m1.path), os.path.basename(diff.m2.path))
            
            saveFilePath = "%s/%s"%(savePath, saveFileName)
            print("保存文件%s"%(saveFilePath))
            with open(saveFilePath,'w', encoding='utf8') as f:
                f.write(''.join(OutLines))
        

    def Run(self):
        self.ParseBaseUrl()
        self.ParseMemoryReportInfos()
        self.DiffMemoryReports()
        self.Write()

def main(opts):
    if opts.sort == 'c':
        UObjectDiffInfo.SortType = ObjectSortType.CountIncrease
    elif opts.sort == 'n':
        UObjectDiffInfo.SortType = ObjectSortType.NumKBIncrease
    else:
        UObjectDiffInfo.SortType = ObjectSortType.MaxKBIncrease

    MemoryReportDiffer(opts.url)
 

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option(
        '-u', '--url', dest='url', help='url')

    parser.add_option(
        '-s', '--sort', dest='sort', default = 'c', help='排序 c=CountDiff, n=NumKBDiff, m=MaxKBDiff')

    opts, args = parser.parse_args()

    main(opts)