# -*- coding: UTF-8 -*-
import urllib.request
import time
import shutil
import os
import re

class FileManager():
    def __init__(self):
        self.url = ""
        self.url_list = []
        self.file_list = []

    def LoadAllFiles(self, url):
        self.url_list = []
        self.file_list = []
        self.url = url
        if url.startswith("http"):
            lines = urllib.request.urlopen(url).read().decode()
            self.url_list =re.findall(r"(?<=href=\").+?(?=\")|(?<=href=\').+?(?=\')" ,lines)
            for i in range(len(self.url_list)):
                self.url_list[i] = url + "/" + self.url_list[i]
                print("find url: "+ self.url_list[i])
        else:
            g = os.walk(url)  
            for root, _, file_list in g:  
                for file_name in file_list:  
                    if file_name.endswith(".memreport"):
                        self.url_list.append(os.path.join(root, file_name))
        self.url_list.sort()

        for url in self.url_list:
            self.file_list.append(os.path.basename(url))

    def GetUrlByFile(self, file):
        for url in self.url_list:
            if url.endswith(file):
                return url