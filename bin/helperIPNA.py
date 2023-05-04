#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May  4 10:34:07 2023

@author: luis
"""

import os
import subprocess
import tkinter as tk
from tkinter import filedialog
import shutil

root = tk.Tk()
root.withdraw()

rawSatFilesDir = filedialog.askdirectory(title="Select the directory containing all the raw satellite data files to uncompress if needed")
satFilesDir = os.path.join(os.path.dirname(rawSatFilesDir), "rawSatelliteFiles")
try:
    os.makedirs(satFilesDir)
except FileExistsError:
    pass

for folder in os.listdir(satFilesDir):
    folderDir = os.path.join(rawSatFilesDir, folder)
    
    for file in os.listdir(os.path.join(rawSatFilesDir, folder)):
        fileDir = os.path.join(folderDir, file)
        
        if len(file.split(".")) == 3 and file.split(".")[2] == "gz":
            subprocess.call(["winrar", 'x', '-y', fileDir], cwd = folderDir, stdout = subprocess.PIPE)
            shutil.move(os.path.join(folderDir, file.split(".gz")[0]), satFilesDir)
        
        if len(file.split(".")) == 2:
            shutil.move(fileDir, satFilesDir)
            
            
            
            
            
            
            
            
            
            
            
            
            
            
        