#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 17 11:06:58 2023

@author: luis
"""
import numpy as np
import os
import subprocess
import shutil
import tkinter as tk
from tkinter import filedialog
from tqdm import tqdm
from datetime import datetime
import requests
from scipy.optimize import fsolve
from matplotlib import pyplot as plt

"""
In the following code we create the folders and specify their path:
"""

root = tk.Tk()
root.withdraw()

satFilesDir = filedialog.askdirectory(title="Select the directory containing only the raw satellite data files")
rinexFilesDir = os.path.join(os.path.dirname(satFilesDir), "rinexFiles")
navFilesDir = os.path.join(rinexFilesDir, "navFiles")
obsFilesDir = os.path.join(rinexFilesDir, "obsFiles")
sp3FilesDir = os.path.join(os.path.dirname(satFilesDir), "sp3Files")
ionoFilesDir = os.path.join(os.path.dirname(satFilesDir), "ionoFiles")
blqFilesDir = os.path.join(os.path.dirname(satFilesDir), "blqFiles")
atxFilesDir = os.path.join(os.path.dirname(satFilesDir), "atxFiles") 
eopFilesDir = os.path.join(os.path.dirname(satFilesDir),"eopFiles")
dcbFilesDir = os.path.join(os.path.dirname(satFilesDir), "dcbFiles")
clsFilesDir = os.path.join(os.path.dirname(satFilesDir), "clsFiles")
posFilesDir = os.path.join(os.path.dirname(satFilesDir), "posFiles") 
binDir = os.path.join(os.path.dirname(os.path.dirname(satFilesDir)), "bin")
resultsDir = os.path.join(os.path.dirname(os.path.dirname(satFilesDir)), "results")
resultsGraphsDir = os.path.join(resultsDir, "graphs")
resultsFilesDir = os.path.join(resultsDir, "files")
teqcDir = os.path.join(binDir, "teqc.exe")
netrcDir = os.path.join(os.path.expanduser("~"), ".netrc")
configurationFileDir = os.path.join(binDir, "configuration.conf")
rnx2rtkpDir = os.path.join(binDir, "rnx2rtkp.exe") 
    
try:
    os.makedirs(rinexFilesDir)
except FileExistsError:
    pass
try:
    os.makedirs(navFilesDir)
except FileExistsError:
    pass
try:
    os.makedirs(obsFilesDir)
except FileExistsError:
    pass
try:
    os.makedirs(sp3FilesDir)
except FileExistsError:
    pass
try:
    os.makedirs(ionoFilesDir)
except FileExistsError:
    pass
try:
    os.makedirs(eopFilesDir)
except FileExistsError:
    pass
try:
    os.makedirs(dcbFilesDir)
except FileExistsError:
    pass
try:
    os.makedirs(clsFilesDir)
except FileExistsError:
    pass
try:
    os.makedirs(posFilesDir)
except FileExistsError:
    pass
try:
    os.makedirs(resultsDir)
except FileExistsError:
    pass
try:
    os.makedirs(resultsGraphsDir)
except FileExistsError:
    pass
try:
    os.makedirs(resultsFilesDir)
except FileExistsError:
    pass

"""
We define every function and class which we will use in the code:
"""

# This function given the path to the observation file, returns [[gps week, gps day of week], [utc year, utc day of year, utc month]]:
def firstObsTime(obsFileDir):
    os.chdir(obsFilesDir)
    file = os.path.basename(obsFileDir)
    f = open(file)
    data = f.readlines()
    i = 0
    for k in data:
        dato = k.split()
        if dato[-1] != "OBS":
            i = i + 1
        if dato[-1] == "OBS":
            break
    d = np.array(data[i].split()[0:6]).astype("float")
    utcTime = datetime(int(d[0]), int(d[1]), int(d[2]), int(d[3]), int(d[4]), int(d[5]))  # UTC time
    dayOfYear = datetime(int(d[0]), int(d[1]), int(d[2])).timetuple().tm_yday
    gpsEpoch = datetime(1980, 1, 6, 0, 0, 0) #GPS epoch start time
    timeDiff = utcTime - gpsEpoch
    totalSeconds = timeDiff.total_seconds() # Total number of seconds since GPS epoch
    gpsWeek = int(totalSeconds / 604800)
    gpsDayWeek = int(totalSeconds % 604800 / 86400)
    if len(list(str(gpsWeek))) == 4:
        gpsTime = [gpsWeek, gpsDayWeek]
    if len(list(str(gpsWeek))) == 3:
        gpsWeek = "0" + str(gpsWeek)
        gpsTime = [gpsWeek, gpsDayWeek]
    if len(list(str(dayOfYear))) == 3:
        firstObsTime = [gpsTime, [int(d[0]), str(dayOfYear), int(d[1])]]
    if len(list(str(dayOfYear))) == 2:
        dayOfYear = "0" + str(dayOfYear)
        firstObsTime = [gpsTime, [int(d[0]), dayOfYear, int(d[1])]]
    if len(list(str(dayOfYear))) == 1:
        dayOfYear = "00" + str(dayOfYear)
        firstObsTime = [gpsTime, [int(d[0]), dayOfYear, int(d[1])]]
    return firstObsTime


# This function updates the configuration file for PPP-Static in RTKLIB  
# in the bin folder:
def configFile(dcbFileDir, eopFileDir, ionoFileDir): 
    os.chdir(binDir)
    shutil.copy2(os.path.join(binDir, "configuration.conf"), os.path.join(binDir, "configurationOriginal.conf"))
    configurationFile = "configuration.conf"
    satFileDir = os.path.join(atxFilesDir, "sat.atx")
    antFileDir = os.path.join(atxFilesDir, "ant.atx")
    with open(configurationFile, 'r') as f:
        content = f.read()
    
    if os.path.isfile(satFileDir) == True:
        content = content.replace("file-satantfile    =", "file-satantfile    =" + satFileDir) # Satellite Antenna PCV File ANTEX (.atx file) (path/to/file)
    if os.path.isfile(satFileDir) == False:
        pass
    if os.path.isfile(antFileDir) == True:
        content = content.replace("file-rcvantfile    =", "file-rcvantfile    =" + antFileDir) # Receiver Antenna PCV File ANTEX (.atx file) (path/to/file)
    if os.path.isfile(antFileDir) == False:
        pass
    if os.path.isfile(dcbFileDir) == True:
        content = content.replace("file-dcbfile       =", "file-dcbfile       =" + dcbFileDir) # DCB Data File (.BSX file) (path/to/file)
    if os.path.isfile(dcbFileDir) == False:
        pass
    if os.path.isfile(eopFileDir) == True:
        content = content.replace("file-eopfile       =", "file-eopfile       =" + eopFileDir) # EOP Data File (format IGS ERP) (path/to/file)
    if os.path.isfile(eopFileDir) == False:
        pass
    if os.path.isfile(os.path.join(blqFilesDir, os.listdir(blqFilesDir)[0])) == True:
        content = content.replace("file-blqfile       =", "file-blqfile       =" + os.path.join(blqFilesDir, os.listdir(blqFilesDir)[0])) # OTL coefficients files (BQL format) (path/to/file)
    if os.path.isfile(os.path.join(blqFilesDir, os.listdir(blqFilesDir)[0])) == False:
        pass
    if os.path.isfile(ionoFileDir) == True:
        content = content.replace("file-ionofile      =", "file-ionofile      =" + ionoFileDir) # Ionosphere Data File (path/to/file)
    if os.path.isfile(ionoFileDir) == False:
        pass
   
    with open(configurationFile, 'w') as f:
        f.write(content)
      
        
def resetConfigFile():
    # Replace modified configuration file with original file:
    os.chdir(binDir)
    shutil.move("configurationOriginal.conf", "configuration.conf")

    
class cddisNasa:
    
    # Functions for creating the .netrc file to access CDDIS NASA
    def loginAccount():
        # Enter your CDDIS NASA login credentials
        username = input("Enter your CDDIS NASA username: ")
        password = input("Enter your CDDIS NASA password: ")
        line = "machine urs.earthdata.nasa.gov login " + str(username) + " password " + str(password)
        os.chdir(os.path.expanduser("~"))
        netrc = open(".netrc", "w")
        netrc.write(line)
        os.chmod(netrcDir, 0o600)
   
    
    def deleteNetrcFile():
        os.remove(netrcDir)


class download:
    
    # This function downloads the .sp3 file given the GPS week and day in the 
    # sp3FilesDirectory with the filename of the obs file:
    def sp3File(gpsTime, obsFile): # One file for each gps week and day
        
        if os.path.isfile(os.path.join(sp3FilesDir, obsFile.split(".")[0]+".sp3")) == True:
            return
        if os.path.isfile(os.path.join(clsFilesDir, obsFile.split(".")[0]+".sp3")) == False:
            sp3zFilename = "igs" + str(gpsTime[0]) + str(gpsTime[1]) + ".sp3.Z"
            sp3zUrl = "https://cddis.nasa.gov/archive/gps/products/" + str(gpsTime[0]) + "/" + sp3zFilename
            
            try:
                # Makes request of URL, stores response in variable r
                r = requests.get(sp3zUrl)

                # Opens a local file for writing to
                os.chdir(sp3FilesDir)
                sp3zNewFilename = obsFile.split(".")[0]+".sp3.Z"
                sp3zFileDir = os.path.join(sp3FilesDir, sp3zNewFilename)
                with open(sp3zNewFilename, 'wb') as fd:
                    for chunk in r.iter_content(chunk_size=1000):
                        fd.write(chunk)
                try:
                    subprocess.call(["winrar", 'x', '-y', sp3zFileDir], cwd = sp3FilesDir, stdout = subprocess.PIPE)
                    os.remove(sp3zFileDir) # remove .sp3.Z file and keep only .sp3 file
                except Exception as e:
                    print("Error extracting dcb file:" + str(e))
                    os.remove(sp3zFileDir) # remove .sp3.Z file and keep only .sp3 file
                    sp3zFilename = "igr" + str(gpsTime[0]) + str(gpsTime[1]) + ".sp3.Z"
                    sp3zUrl = "https://cddis.nasa.gov/archive/gps/products/" + str(gpsTime[0]) + "/" + sp3zFilename
                    try:
                        # Makes request of URL, stores response in variable r
                        r = requests.get(sp3zUrl)

                        # Opens a local file of same name as remote file for writing to
                        os.chdir(sp3FilesDir)
                        sp3zNewFilename = obsFile.split(".")[0]+".sp3.Z"
                        sp3zFileDir = os.path.join(sp3FilesDir, sp3zNewFilename)
                        with open(sp3zNewFilename, 'wb') as fd:
                            for chunk in r.iter_content(chunk_size=1000):
                                fd.write(chunk)
                        try:
                            subprocess.call(["winrar", 'x', '-y', sp3zFileDir], cwd = sp3FilesDir, stdout = subprocess.PIPE)
                            os.remove(sp3zFileDir) # remove .sp3.Z file and keep only .sp3 file
                        except Exception as e:
                            print("Error extracting dcb file:" + str(e))
                            os.remove(sp3zFileDir) # remove .sp3.Z file and keep only .sp3 file
                        
                    except Exception as e:
                        print("Error:" + str(e))
                        return 
            
            except Exception:
                sp3zFilename = "igr" + str(gpsTime[0]) + str(gpsTime[1]) + ".sp3.Z"
                sp3zUrl = "https://cddis.nasa.gov/archive/gps/products/" + str(gpsTime[0]) + "/" + sp3zFilename
                try:
                    # Makes request of URL, stores response in variable r
                    r = requests.get(sp3zUrl)

                    # Opens a local file of same name as remote file for writing to
                    os.chdir(sp3FilesDir)
                    sp3zNewFilename = obsFile.split(".")[0]+".sp3.Z"
                    sp3zFileDir = os.path.join(sp3FilesDir, sp3zNewFilename)
                    with open(sp3zNewFilename, 'wb') as fd:
                        for chunk in r.iter_content(chunk_size=1000):
                            fd.write(chunk)
                    try:
                        subprocess.call(["winrar", 'x', '-y', sp3zFileDir], cwd = sp3FilesDir, stdout = subprocess.PIPE)
                        os.remove(sp3zFileDir) # remove .sp3.Z file and keep only .sp3 file
                    except Exception as e:
                        print("Error extracting dcb file:" + str(e))
                        os.remove(sp3zFileDir) # remove .sp3.Z file and keep only .sp3 file
                    
                except Exception as e:
                    print("Error:" + str(e))
                    return 
        
    
    
    def clsFile(gpsTime, obsFile): # One file for each gps week and day
    
        if os.path.isfile(os.path.join(clsFilesDir, obsFile.split(".")[0]+".cls")) == True:
            return
        if os.path.isfile(os.path.join(clsFilesDir, obsFile.split(".")[0]+".cls")) == False:
            clszFilename = "igs" + str(gpsTime[0]) + str(gpsTime[1]) + ".cls.Z"
            clszUrl = "https://cddis.nasa.gov/archive/gps/products/" + str(gpsTime[0]) + "/" + clszFilename
            
            try:
                # Makes request of URL, stores response in variable r
                r = requests.get(clszUrl)

                # Opens a local file for writing to
                os.chdir(clsFilesDir)
                clszNewFilename = obsFile.split(".")[0]+".cls.Z"
                clszFileDir = os.path.join(clsFilesDir, clszNewFilename)
                with open(clszNewFilename, 'wb') as fd:
                    for chunk in r.iter_content(chunk_size=1000):
                        fd.write(chunk)
                try:
                    subprocess.call(["winrar", 'x', '-y', clszFileDir], cwd = clsFilesDir, stdout = subprocess.PIPE)
                    os.remove(clszFileDir) # remove .cls.Z file and keep only .cls file
                except Exception as e:
                    print("Error extracting dcb file:" + str(e))
                    os.remove(clszFileDir) # remove .cls.Z file and keep only .cls file
                    clszFilename = "igr" + str(gpsTime[0]) + str(gpsTime[1]) + ".cls.Z"
                    clszUrl = "https://cddis.nasa.gov/archive/gps/products/" + str(gpsTime[0]) + "/" + clszFilename
                    try:
                        # Makes request of URL, stores response in variable r
                        r = requests.get(clszUrl)

                        # Opens a local file of same name as remote file for writing to
                        os.chdir(clsFilesDir)
                        clszNewFilename = obsFile.split(".")[0]+".cls.Z"
                        clszFileDir = os.path.join(clsFilesDir, clszNewFilename)
                        with open(clszNewFilename, 'wb') as fd:
                            for chunk in r.iter_content(chunk_size=1000):
                                fd.write(chunk)
                        try:
                            subprocess.call(["winrar", 'x', '-y', clszFileDir], cwd = clsFilesDir, stdout = subprocess.PIPE)
                            os.remove(clszFileDir) # remove .cls.Z file and keep only .cls file
                        except Exception as e:
                            print("Error extracting dcb file:" + str(e))
                            os.remove(clszFileDir) # remove .cls.Z file and keep only .cls file
                        
                    except Exception as e:
                        print("Error:" + str(e))
                        return 
            
            except Exception:
                clszFilename = "igr" + str(gpsTime[0]) + str(gpsTime[1]) + ".cls.Z"
                clszUrl = "https://cddis.nasa.gov/archive/gps/products/" + str(gpsTime[0]) + "/" + clszFilename
                try:
                    # Makes request of URL, stores response in variable r
                    r = requests.get(clszUrl)

                    # Opens a local file of same name as remote file for writing to
                    os.chdir(clsFilesDir)
                    clszNewFilename = obsFile.split(".")[0]+".cls.Z"
                    clszFileDir = os.path.join(clsFilesDir, clszNewFilename)
                    with open(clszNewFilename, 'wb') as fd:
                        for chunk in r.iter_content(chunk_size=1000):
                            fd.write(chunk)
                    try:
                        subprocess.call(["winrar", 'x', '-y', clszFileDir], cwd = clsFilesDir, stdout = subprocess.PIPE)
                        os.remove(clszFileDir) # remove .cls.Z file and keep only .cls file
                    except Exception as e:
                        print("Error extracting dcb file:" + str(e))
                        os.remove(clszFileDir) # remove .cls.Z file and keep only .cls file
                    
                except Exception as e:
                    print("Error:" + str(e))
                    return 
    
    
    # This function downloads the iono file .21i, one for each utc year and day
    # with the filename of the obs file
    def ionoFile(utcTime, obsFile): 
        
        if os.path.isfile(os.path.join(ionoFilesDir, obsFile.split(".")[0]+".21i")) == True:
            return
        if os.path.isfile(os.path.join(ionoFilesDir, obsFile.split(".")[0]+".21i")) == False:
            
            iono21izFilename = "igsg" + str(utcTime[1]) + "0.21i.Z"
            iono21izUrl = "https://cddis.nasa.gov/archive/gps/products/ionex/" + str(utcTime[0]) + "/" + str(utcTime[1]) + "/" + iono21izFilename
           
            try:
                # Makes request of URL, stores response in variable r
                r = requests.get(iono21izUrl)

                # Opens a local file for writing to
                os.chdir(ionoFilesDir)
                iono21izNewFilename = obsFile.split(".")[0]+".21i.Z"
                iono21izFileDir = os.path.join(ionoFilesDir, iono21izNewFilename)
                with open(iono21izNewFilename, 'wb') as fd:
                    for chunk in r.iter_content(chunk_size=1000):
                        fd.write(chunk)
                try:
                    subprocess.call(["winrar", 'x', '-y', iono21izFileDir], cwd = ionoFilesDir, stdout = subprocess.PIPE)
                    os.remove(iono21izFileDir) # remove .21i.Z file and keep only .21i file
                except Exception as e:
                    print("Error extracting dcb file:" + str(e))
                    os.remove(iono21izFileDir) # remove .21i.Z file and keep only .21i file
                    iono21izFilename = "igrg" + str(utcTime[1]) + "0.21i.Z"
                    iono21izUrl = "https://cddis.nasa.gov/archive/gps/products/ionex/" + str(utcTime[0]) + "/" + str(utcTime[1]) + "/" + iono21izFilename
                    
                    try:
                        # Makes request of URL, stores response in variable r
                        r = requests.get(iono21izUrl)

                        # Opens a local file of same name as remote file for writing to
                        os.chdir(ionoFilesDir)
                        iono21izNewFilename = obsFile.split(".")[0]+".21i.Z"
                        iono21izFileDir = os.path.join(ionoFilesDir, iono21izNewFilename)
                        with open(iono21izNewFilename, 'wb') as fd:
                            for chunk in r.iter_content(chunk_size=1000):
                                fd.write(chunk)
                        try:
                            subprocess.call(["winrar", 'x', '-y', iono21izFileDir], cwd = ionoFilesDir, stdout = subprocess.PIPE)
                            os.remove(iono21izFileDir) # remove .21i.Z file and keep only .21i file
                        except Exception as e:
                            print("Error extracting dcb file:" + str(e))
                            os.remove(iono21izFileDir) # remove .21i.Z file and keep only .21i file

                    except Exception as e:
                        print("Error:" + str(e))
                        return 
            
            except Exception:
                iono21izFilename = "igrg" + str(utcTime[1]) + "0.21i.Z"
                iono21izUrl = "https://cddis.nasa.gov/archive/gps/products/ionex/" + str(utcTime[0]) + "/" + str(utcTime[1]) + "/" + iono21izFilename
                
                try:
                    # Makes request of URL, stores response in variable r
                    r = requests.get(iono21izUrl)

                    # Opens a local file of same name as remote file for writing to
                    os.chdir(ionoFilesDir)
                    iono21izNewFilename = obsFile.split(".")[0]+".21i.Z"
                    iono21izFileDir = os.path.join(ionoFilesDir, iono21izNewFilename)
                    with open(iono21izNewFilename, 'wb') as fd:
                        for chunk in r.iter_content(chunk_size=1000):
                            fd.write(chunk)
                    try:
                        subprocess.call(["winrar", 'x', '-y', iono21izFileDir], cwd = ionoFilesDir, stdout = subprocess.PIPE)
                        os.remove(iono21izFileDir) # remove .21i.Z file and keep only .21i file
                    except Exception as e:
                        print("Error extracting dcb file:" + str(e))
                        os.remove(iono21izFileDir) # remove .21i.Z file and keep only .21i file

                except Exception as e:
                    print("Error:" + str(e))
                    return 
    
    
    # This function downloads the eop file .erp, one for each gps week,
    # with the filename gpsWeek
    def eopFile(firstObsTime): # Only 1 file for each gps week
        if os.path.isfile(os.path.join(eopFilesDir, str(firstObsTime[0][0]) + ".erp")) == True:
            return
        if os.path.isfile(os.path.join(eopFilesDir, str(firstObsTime[0][0]) + ".erp")) == False:  
            erpzFilename = "igs" + list(str(firstObsTime[1][0]))[2] + list(str(firstObsTime[1][0]))[3] + "P" + str(firstObsTime[0][0]) + ".erp.Z"  
            erpzUrl = "https://cddis.nasa.gov/archive/gps/products/" + str(firstObsTime[0][0]) + "/" + erpzFilename
                
            try:
                # Makes request of URL, stores response in variable r
                r = requests.get(erpzUrl)
                # Opens a local file of same name as remote file for writing to
                os.chdir(eopFilesDir)
                erpzNewFilename = str(firstObsTime[0][0]) + ".erp.Z"
                erpzFileDir = os.path.join(eopFilesDir, erpzNewFilename)
                with open(erpzNewFilename, 'wb') as fd:
                    for chunk in r.iter_content(chunk_size=1000):
                        fd.write(chunk)
                try:
                    subprocess.call(["winrar", 'x', '-y', erpzFileDir], cwd = eopFilesDir, stdout = subprocess.PIPE)
                    os.remove(erpzFileDir) # remove .erp.Z file and keep only .erp file
                except Exception as e:
                    print("Error extracting dcb file:" + str(e))
                    os.remove(erpzFileDir) # remove .erp.Z file and keep only .erp file
                    
                    erpzFilename = "igr" + list(str(firstObsTime[1][0]))[2] + list(str(firstObsTime[1][0]))[3] + "P" + str(firstObsTime[0][0]) + ".erp.Z"  
                    erpzUrl = "https://cddis.nasa.gov/archive/gps/products/" + str(firstObsTime[0][0]) + "/" + erpzFilename
                        
                    try:
                        # Makes request of URL, stores response in variable r
                        r = requests.get(erpzUrl)

                        # Opens a local file of same name as remote file for writing to
                        os.chdir(eopFilesDir)
                        erpzNewFilename = str(firstObsTime[0][0]) + ".erp.Z"
                        erpzFileDir = os.path.join(eopFilesDir, erpzNewFilename)
                        with open(erpzNewFilename, 'wb') as fd:
                            for chunk in r.iter_content(chunk_size=1000):
                                fd.write(chunk)
                        try:
                            subprocess.call(["winrar", 'x', '-y', erpzFileDir], cwd = eopFilesDir, stdout = subprocess.PIPE)
                            os.remove(erpzFileDir) # remove .erp.Z file and keep only .erp file
                        except Exception as e:
                            print("Error extracting dcb file:" + str(e))
                            os.remove(erpzFileDir) # remove .erp.Z file and keep only .erp file
                            
                    except Exception as e:
                        print("Error:" + str(e))
                        return 
                    
            except Exception:
                erpzFilename = "igr" + list(str(firstObsTime[1][0]))[2] + list(str(firstObsTime[1][0]))[3] + "P" + str(firstObsTime[0][0]) + ".erp.Z"  
                erpzUrl = "https://cddis.nasa.gov/archive/gps/products/" + str(firstObsTime[0][0]) + "/" + erpzFilename
                    
                try:
                    # Makes request of URL, stores response in variable r
                    r = requests.get(erpzUrl)

                    # Opens a local file of same name as remote file for writing to
                    os.chdir(eopFilesDir)
                    erpzNewFilename = str(firstObsTime[0][0]) + ".erp.Z"
                    erpzFileDir = os.path.join(eopFilesDir, erpzNewFilename)
                    with open(erpzNewFilename, 'wb') as fd:
                        for chunk in r.iter_content(chunk_size=1000):
                            fd.write(chunk)
                    try:
                        subprocess.call(["winrar", 'x', '-y', erpzFileDir], cwd = eopFilesDir, stdout = subprocess.PIPE)
                        os.remove(erpzFileDir) # remove .erp.Z file and keep only .erp file
                    except Exception as e:
                        print("Error extracting dcb file:", str(e))
                        os.remove(erpzFileDir) # remove .erp.Z file and keep only .erp file
                        
                except Exception as e:
                    print("Error:", str(e))
                    return 
    
    
    # This function downloads the DCB file .SBX, with the filename "utcYear"+"utcTrim [1, 2, 3 or 4]"
    def dcbFile(utcTime):
        month = utcTime[2]
        if month <= 3:
            trim = "1"
        if month > 3 and month <= 6:
            trim = "2"
        if month > 6 and month <= 9:
            trim = "3"
        if month > 9 and month <= 12:
            trim = "4"
            
        if os.path.isfile(os.path.join(dcbFilesDir, str(utcTime[0]) + trim + ".dcb")) == True:
            return
        if os.path.isfile(os.path.join(dcbFilesDir, str(utcTime[0]) + trim + ".dcb")) == False:
            if month <= 3:
                dcbzFilename = "DLR0MGXFIN_" + str(utcTime[0]) + "001" + "0000_03L_01D_DCB.BSX.gz"
            if month > 3 and month <= 6:
                dcbzFilename = "DLR0MGXFIN_" + str(utcTime[0]) + "091" + "0000_03L_01D_DCB.BSX.gz"
            if month > 6 and month <= 9:
                dcbzFilename = "DLR0MGXFIN_" + str(utcTime[0]) + "182" + "0000_03L_01D_DCB.BSX.gz"
            if month > 9 and month <= 12:
                dcbzFilename = "DLR0MGXFIN_" + str(utcTime[0]) + "274" + "0000_03L_01D_DCB.BSX.gz"
            
            dcbzUrl = "https://cddis.nasa.gov/archive/gnss/products/bias/" + str(utcTime[0]) + "/" + dcbzFilename
                
            try:
                # Makes request of URL, stores response in variable r
                r = requests.get(dcbzUrl)
                    
                # Opens a local file of same name as remote file for writing to
                os.chdir(dcbFilesDir)
                dcbzNewFilename = str(utcTime[0]) + trim + ".dcb"
                dcbzFileDir = os.path.join(dcbFilesDir, dcbzFilename)
                with open(dcbzFilename, 'wb') as fd:
                    for chunk in r.iter_content(chunk_size=1000):
                        fd.write(chunk)  
                subprocess.call(["winrar", 'x', '-y', dcbzFileDir], cwd = dcbFilesDir, stdout = subprocess.PIPE)
                shutil.move(dcbzFilename.split(".gz")[0], dcbzNewFilename)
                os.remove(dcbzFileDir)
                        
            except Exception as e:
                print("Error:", str(e))
                return
 
               
class pos:
    
    # This function given the filename of the .pos file returns lists with
    # utcTime (datetime object), latitude, longitude, height, [stdN, errorStdN], 
    # [stdE, errorStdE], [stdU, errorStdU]:
    def readPosFile(posFile):
        os.chdir(posFilesDir)
        file = open(posFile, "r")
        lines = file.readlines()
        
        utcTime = [] # datetime(year, month, day, hour, minute, seconds) -> each index (string)
        
        latitude = [] # degrees
        longitude = [] # degrees
        height = [] # m
        
        stdN = [] # m (float)
        stdE = [] # m (float)
        stdU = [] # m (float)
        errorStdN = [] # m (float)
        errorStdE = [] # m (float)
        errorStdU = [] # m (float)
        
        for i, l in enumerate(lines):
            line = l.split()
            if len(line) > 1 and line[1] == "UTC":
                data = lines[i+1:]
        
        for k in data:
            d = k.split()
            
            utc_time = d[0:2]
            utc_year = utc_time[0].split("/")[0]
            utc_month = utc_time[0].split("/")[1]
            utc_day = utc_time[0].split("/")[2]
            utc_hour = utc_time[1].split(":")[0]
            utc_min = utc_time[1].split(":")[1]
            utc_sec = utc_time[1].split(":")[2]
            utcTime.append(datetime(int(utc_year), int(utc_month), int(utc_day), int(utc_hour), int(utc_min), int(float(utc_sec))))
            
            lat = float(d[2:5][0]) + float(d[2:5][1])/60 + float(d[2:5][2])/3600 # degrees
            latitude.append(lat)
            lon = float(d[5:8][0]) + float(d[5:8][1])/60 + float(d[5:8][2])/3600 # degrees
            longitude.append(lon)
            height.append(float(d[8]))
            
            stdN.append(float(d[11]))
            stdE.append(float(d[12]))
            stdU.append(float(d[13]))
            errorStdN.append(abs(float(d[14])))
            errorStdE.append(abs(float(d[15])))
            errorStdU.append(abs(float(d[16])))
        
        return utcTime, latitude, longitude, height, np.array([stdN, errorStdN]), np.array([stdE, errorStdE]), np.array([stdU, errorStdU])


    # This function returns the mean effective latitude, longitude and height from the
    # data of the time period given (utcTime):
    def effectivePosData(utcTime, latitude, longitude, height):
        
        # Determining the mean effective latitude of the day:
        latX = np.arange(0, len(longitude))
        latCoeffs = np.polyfit(latX, latitude, 20) 
        latPoly = np.poly1d(latCoeffs)
        latDPoly = latPoly.deriv()
        latRoots = fsolve(latDPoly, x0=np.array([0, 300]))
        effLat1 = np.array(latitude[int(np.ceil(latRoots[1])):])
        effLat1Coeffs = np.polyfit(range(0, len(effLat1)), effLat1, 3)
        effLat1Fix = np.polyval(effLat1Coeffs, range(0, len(effLat1)))
        effLatErr = 0.25*np.abs(np.std(effLat1Fix))
        effLatIndex = np.abs(effLat1 - effLat1Fix) < effLatErr
        effLat = effLat1[effLatIndex]
        effLatMean = np.mean(effLat)
        effLatMax = np.max(effLat)
        effLatMin = np.min(effLat)
        
        # Determining the mean effective longitude of the day:
        lonX = np.arange(0, len(longitude))
        lonCoeffs = np.polyfit(lonX, longitude, 20) 
        lonPoly = np.poly1d(lonCoeffs)
        lonDPoly = lonPoly.deriv()
        lonRoots = fsolve(lonDPoly, x0=np.array([0, 300]))
        effLon1 = np.array(longitude[int(np.ceil(lonRoots[1])):])
        effLon1Coeffs = np.polyfit(range(0, len(effLon1)), effLon1, 3)
        effLon1Fix = np.polyval(effLon1Coeffs, range(0, len(effLon1)))
        effLonErr = 0.25*np.abs(np.std(effLon1Fix))
        effLonIndex = np.abs(effLon1 - effLon1Fix) < effLonErr
        effLon = effLon1[effLonIndex]
        effLonMean = np.mean(effLon)
        effLonMax = np.max(effLon)
        effLonMin = np.min(effLon)
        
        # Determining the mean effective height of the day:
        heightX = np.arange(0, len(height))
        heightCoeffs = np.polyfit(heightX, height, 20) 
        heightPoly = np.poly1d(heightCoeffs)
        heightDPoly = heightPoly.deriv()
        heightRoots = fsolve(heightDPoly, x0=np.array([0, 300]))
        effHeight1 = np.array(height[int(np.ceil(heightRoots[1])):])
        effHeight1Coeffs = np.polyfit(range(0, len(effHeight1)), effHeight1, 3)
        effHeight1Fix = np.polyval(effHeight1Coeffs, range(0, len(effHeight1)))
        effHeightErr = 0.25*np.abs(np.std(effHeight1Fix))
        effHeightIndex = np.abs(effHeight1 - effHeight1Fix) < effHeightErr
        effHeight = effHeight1[effHeightIndex]
        effHeightMean = np.mean(effHeight)
        effHeightMax = np.max(effHeight)
        effHeightMin = np.min(effHeight)
        
        return effLatMean, effLonMean, effHeightMean, [effLatMin, effLatMax], [effLonMin, effLonMax], [effHeightMin, effHeightMax]
    
    
    # This function given a list for the latitudes, longitudes and heights
    # returns a list of local coordinates, this local coordinate system is 
    # referred to as the East-North-Up (ENU) coordinate system:
    def geo2enu(latitudes, longitudes, heights):
        # Geodetic System WGS 84 axes
        a  = 6378137.0
        b  = 6356752.314245
        a2 = a**2
        b2 = b**2
        e2 = 1.0 - (b2 / a2)
        phi = np.deg2rad(latitudes)
        lmd = np.deg2rad(longitudes)
        cPhi = np.cos(phi)
        cLmd = np.cos(lmd)
        sPhi = np.sin(phi)
        sLmd = np.sin(lmd)
        N = a / np.sqrt(1.0 - e2 * sPhi * sPhi)
        x = (N + np.array(heights)) * cPhi * cLmd
        y = (N + np.array(heights)) * cPhi * sLmd
        z = ((b2 / a2) * N + np.array(heights)) * sPhi
        east = x-x[0]
        north = y-y[0]
        up = z-z[0]
        
        return east, north, up, x, y, z
    
    
    # This function given a list of the local coordinates of each day 
    # and the day the measurements began and ended, gives a 3 graphs
    #  N-S, E-W, and U-D graphs:
    def plotDataENU1(measurementsStartTime, east, north, up, stdEast, stdNorth, stdUp, errEast, errNorth, errUp):
        days = np.arange(0, len(measurementsStartTime))
        firstDay = str(measurementsStartTime[0].day) + "/" + str(measurementsStartTime[0].month) + "/" + str(measurementsStartTime[0].year)
        lastDay = str(measurementsStartTime[-1].day) + "/" + str(measurementsStartTime[-1].month) + "/" + str(measurementsStartTime[-1].year)
        numberOfDays = len(measurementsStartTime)
        
        os.chdir(resultsGraphsDir)
        # Plot the north, east, and upward components over time
        fig, (ax1, ax2, ax3) = plt.subplots(nrows=3, sharex=True, figsize = (20, 20))
        ax1.errorbar(days, 100*north, yerr = 100*np.array(stdNorth), fmt = "o-", ecolor = "b", linestyle = "None", markersize = 12, capsize = 13, linewidth = 3, color = "b")
        ax1.errorbar(days, 100*north, yerr = 100*errNorth, fmt = "o-", ecolor = "r", linestyle = "None", markersize = 14, capsize = 13, linewidth = 3, color = "r")
        ax1.legend(["Standard Desviation (BLUE)", "Model Error (RED)"], loc = "upper right", fontsize = 16)
        ax1.set_ylim([100*np.min(north)-1.5*100*abs(np.max(errNorth)), 100*np.max(north)+1.5*100*abs(np.max(errNorth))])
        ax1.set_xlim([-1, len(days)+10])
        ax1.set_ylabel('North - South (mm)', fontsize = 20)     
        ax1.set_title("Measurements starts on " + firstDay + " and ends on " + lastDay + " (The measurements take place during " + str(numberOfDays) + " days)", fontsize = 20)
        ax1.grid(True)

        ax2.set_ylabel("East - West (mm)", fontsize = 20)
        ax2.errorbar(days, 100*east, yerr = 100*np.array(stdEast), fmt = "o-", ecolor = "b", linestyle = "None", markersize = 12, capsize = 13, linewidth = 3, color = "b")
        ax2.errorbar(days, 100*east, yerr = 100*errEast, fmt = "o-", ecolor = "r", linestyle = "None", markersize = 14, capsize = 13, linewidth = 3, color = "r")
     
        ax2.legend(["Standard Desviation (BLUE)", "Model Error (RED)"], loc = "upper right", fontsize = 16)
        ax2.set_ylim([100*np.min(east)-1.5*100*abs(np.max(errEast)), 100*np.max(east)+1.5*100*abs(np.max(errEast))])
        ax2.set_xlim([-1, len(days)+10])
        ax2.grid(True)

        ax3.set_ylabel("Up - Down (mm)", fontsize = 20)
        ax3.errorbar(days, 100*up, yerr = 100*np.array(stdUp), fmt = "o-", ecolor = "b", linestyle = "None", markersize = 12, capsize = 13, linewidth = 3, color = "b")
        ax3.errorbar(days, 100*up, yerr = 100*errUp, fmt = "o-", ecolor = "r", linestyle = "None", markersize = 14, capsize = 13, linewidth = 3, color = "r")
        ax3.legend(["Standard Desviation (BLUE)", "Model Error (RED)"], loc = "upper right", fontsize = 16)
        ax3.set_ylim([100*np.min(up)-1.5*100*abs(np.max(errUp)), 100*np.max(up)+1.5*100*abs(np.max(errUp))])
        ax3.set_xlim([-1, len(days)+10])
        ax3.set_xlabel("Days", fontsize = 40) 
        ax3.set_xticks(days, days, fontsize =15)
        ax3.grid(True)
        
        plt.savefig("ENU1.png")
        
    def plotDataENU2(measurementsStartTime, lastEast, lastNorth, lastUp, lastStdEasts, lastStdNorths, lastStdUps):
        days = np.arange(0, len(measurementsStartTime))
        firstDay = str(measurementsStartTime[0].day) + "/" + str(measurementsStartTime[0].month) + "/" + str(measurementsStartTime[0].year)
        lastDay = str(measurementsStartTime[-1].day) + "/" + str(measurementsStartTime[-1].month) + "/" + str(measurementsStartTime[-1].year)
        numberOfDays = len(measurementsStartTime)
        
        os.chdir(resultsGraphsDir)
        # Plot the north, east, and upward components over time
        fig, (ax1, ax2, ax3) = plt.subplots(nrows=3, sharex=True, figsize = (20, 20))
        ax1.errorbar(days, 100*lastNorth, yerr = 100*np.array(lastStdNorths), fmt = "o-", ecolor = "b", linestyle = "None", markersize = 14, capsize = 13, linewidth = 3)
        ax1.legend(["Standard Desviation (BLUE)"], loc = "upper right", fontsize = 16)
        ax1.set_ylim([100*np.min(lastNorth)-1.5*100*abs(np.max(lastStdNorths)), 100*np.max(lastNorth)+1.5*100*abs(np.max(lastStdNorths))])
        ax1.set_xlim([-1, len(days)+10])
        ax1.set_ylabel('North - South (mm)', fontsize = 20)     
        ax1.set_title("Measurements starts on " + firstDay + " and ends on " + lastDay + " (The measurements take place during " + str(numberOfDays) + " days)", fontsize = 20)
        ax1.grid(True)

        ax2.set_ylabel("East - West (mm)", fontsize = 20)
        ax2.errorbar(days, 100*lastEast, yerr = 100*np.array(lastStdEasts), fmt = "o-", ecolor = "b", linestyle = "None", markersize = 14, capsize = 13, linewidth = 3)
        ax2.legend(["Standard Desviation (BLUE)"], loc = "upper right", fontsize = 16)
        ax2.set_ylim([100*np.min(lastEast)-1.5*100*abs(np.max(lastStdEasts)), 100*np.max(lastEast)+1.5*100*abs(np.max(lastStdEasts))])
        ax2.set_xlim([-1, len(days)+10])
        ax2.grid(True)

        ax3.set_ylabel("Up - Down (mm)", fontsize = 20)
        ax3.errorbar(days, 100*lastUp, yerr = 100*np.array(lastStdUps), fmt = "o-", ecolor = "b", linestyle = "None", markersize = 14, capsize = 13, linewidth = 3)
        ax3.legend(["Standard Desviation (BLUE)"], loc = "upper right", fontsize = 16)
        ax3.set_ylim([100*np.min(lastUp)-1.5*100*abs(np.max(lastStdUps)), 100*np.max(lastUp)+1.5*100*abs(np.max(lastStdUps))])
        ax3.set_xlim([-1, len(days)+10])
        ax3.set_xlabel("Days", fontsize = 40) 
        ax3.set_xticks(days, days, fontsize = 15)
        ax3.grid(True)
        
        plt.savefig("ENU2.png")
        
    def plotDataENU3(measurementsStartTime, east, north, up, stdEast, stdNorth, stdUp, errEast, errNorth, errUp, lastEast, lastNorth, lastUp, lastStdEasts, lastStdNorths, lastStdUps):
        days = np.arange(0, len(measurementsStartTime))
        firstDay = str(measurementsStartTime[0].day) + "/" + str(measurementsStartTime[0].month) + "/" + str(measurementsStartTime[0].year)
        lastDay = str(measurementsStartTime[-1].day) + "/" + str(measurementsStartTime[-1].month) + "/" + str(measurementsStartTime[-1].year)
        numberOfDays = len(measurementsStartTime)
        
        os.chdir(resultsGraphsDir)
        # Plot the north, east, and upward components over time
        fig, (ax1, ax2, ax3) = plt.subplots(nrows=3, sharex=True, figsize = (20, 20))
        ax1.errorbar(days, 100*north, yerr = 100*errNorth, fmt = "o-", ecolor = "r", linestyle = "None", markersize = 14, capsize = 13, linewidth = 3, color = "r")
        ax1.errorbar(days, 100*north, yerr = 100*np.array(stdNorth), fmt = "o-", ecolor = "b", linestyle = "None", markersize = 12, capsize = 13, linewidth = 3, color = "b")
        ax1.errorbar(days, 100*lastNorth, yerr = 100*np.array(lastStdNorths), fmt = "o-", ecolor = "g", linestyle = "None", markersize = 14, capsize = 13, linewidth = 3, color = "g")
        ax1.legend(["Model Error (Red)", "Standard Desviation (Blue)", "Last Measurement (Green)"], loc = "upper right", fontsize = 16)
        ax1.set_ylim([100*np.min(north)-1.5*100*abs(np.max(errNorth)), 100*np.max(north)+1.5*100*abs(np.max(errNorth))])
        ax1.set_xlim([-1, len(days)+10])
        ax1.set_ylabel('North - South (mm)', fontsize = 20)     
        ax1.set_title("Measurements starts on " + firstDay + " and ends on " + lastDay + " (The measurements take place during " + str(numberOfDays) + " days)", fontsize = 20)
        ax1.grid(True)

        ax2.set_ylabel("East - West (mm)", fontsize = 20)
        ax2.errorbar(days, 100*east, yerr = 100*errEast, fmt = "o-", ecolor = "r", linestyle = "None", markersize = 14, capsize = 13, linewidth = 3, color = "r")
        ax2.errorbar(days, 100*east, yerr = 100*np.array(stdEast), fmt = "o-", ecolor = "b", linestyle = "None", markersize = 12, capsize = 13, linewidth = 3, color = "b")
        ax2.errorbar(days, 100*lastEast, yerr = 100*np.array(lastStdEasts), fmt = "o-", ecolor = "g", linestyle = "None", markersize = 14, capsize = 13, linewidth = 3, color = "g")
        ax2.legend(["Model Error (Red)", "Standard Desviation (Blue)", "Last Measurement (Green)"], loc = "upper right", fontsize = 16)
        ax2.set_ylim([100*np.min(east)-1.5*100*abs(np.max(errEast)), 100*np.max(east)+1.5*100*abs(np.max(errEast))])
        ax2.set_xlim([-1, len(days)+10])
        ax2.grid(True)

        ax3.set_ylabel("Up - Down (mm)", fontsize = 20)
        ax3.errorbar(days, 100*up, yerr = 100*errUp, fmt = "o-", ecolor = "r", linestyle = "None", markersize = 14, capsize = 13, linewidth = 3, color = "r")
        ax3.errorbar(days, 100*up, yerr = 100*np.array(stdUp), fmt = "o-", ecolor = "b", linestyle = "None", markersize = 12, capsize = 13, linewidth = 3, color = "b")
        ax3.errorbar(days, 100*lastUp, yerr = 100*np.array(lastStdUps), fmt = "o-", ecolor = "g", linestyle = "None", markersize = 14, capsize = 13, linewidth = 3, color = "g")
        ax3.legend(["Model Error (Red)", "Standard Desviation (Blue)", "Last Measurement (Green)"], loc = "upper right", fontsize = 16)
        ax3.set_ylim([100*np.min(up)-1.5*100*abs(np.max(errUp)), 100*np.max(up)+1.5*100*abs(np.max(errUp))])
        ax3.set_xlim([-1, len(days)+10])
        ax3.set_xlabel("Days", fontsize = 40) 
        ax3.set_xticks(days, days, fontsize =15)
        ax3.grid(True)
        
        plt.savefig("ENU3.png")
        
    
    # This function creates a file and stores all the relevant data in columns:
    def createDataFileENU1(measurementsStartTime, latitudes, longitudes, heights, north, east, up, stdNorth, stdEast, stdUp, errNorth, errEast, errUp):
        os.chdir(resultsFilesDir)
        # Define the header text and adjust formatting
        header = f"{'Year/Month/Day'}   {'Mean-Latitude(º)'}   {'Mean-Longitude(º)'}   {'Mean-Height(m)'}   {'North-South(m)'}   {'East-West(m)'}   {'Up-Down(m)'}   {'Std-North(m)'}   {'Std-East(m)'}   {'Std-Up(m)'}   {'Error-North(m)'}   {'Error-East(m)'}   {'Error-Up(m)'}\n\n"
        
        time = []
        for t in measurementsStartTime:
            time.append(str(t.year)+"/"+str(t.month)+"/"+str(t.day)+" "+"12:00:00")
        
        data = np.column_stack((time, latitudes, longitudes, heights, north, east, up, stdNorth, stdEast, stdUp, errNorth, errEast, np.char.add(np.array(errUp).astype(str), "\n")))

        # Save the data to a file with a header
        np.savetxt("dataENU1.txt", data, delimiter="    ", header=header, comments="", fmt = ["%s"]*13)
   
    def createDataFileENU2(measurementsStartTime, lastLatitudes, lastLongitudes, lastHeights, lastNorth, lastEast, lastUp, lastStdNorths, lastStdEasts, lastStdUps):
        os.chdir(resultsFilesDir)
        # Define the header text and adjust formatting
        header = f"{'Year/Month/Day'}   {'Last-Latitude(º)'}   {'Last-Longitude(º)'}   {'Last-Height(m)'}   {'North-South(m)'}   {'East-West(m)'}   {'Up-Down(m)'}   {'Std-North(m)'}   {'Std-East(m)'}   {'Std-Up(m)'}\n\n"
        
        time = []
        for t in measurementsStartTime:
            time.append(str(t.year)+"/"+str(t.month)+"/"+str(t.day)+" "+"12:00:00")
        
        data = np.column_stack((time, lastLatitudes, lastLongitudes, lastHeights, lastNorth, lastEast, lastUp, lastStdNorths, lastStdEasts, np.char.add(np.array(lastStdUps).astype(str), "\n")))

        # Save the data to a file with a header
        np.savetxt("dataENU2.txt", data, delimiter="    ", header=header, comments="", fmt = ["%s"]*10)
    
"""
We login to CDDIS NASA:
"""        

nasaAccount = cddisNasa.loginAccount() # [username, password]
    
"""
Process to convert our raw data to RINEX 2.11 files and save them in the 
corresponding folders:
"""

for file in tqdm(os.listdir(satFilesDir), desc = "Converting raw satellite data files to RINEX files..."):
    if os.path.isfile(os.path.join(obsFilesDir, file.split(".")[0]+".o")) == True:
        continue
    fileName = file.split(".")[0]
    os.chdir(satFilesDir)
    obsFile = fileName + ".o"
    navFile = fileName + ".n"
    teqcCommand = ['teqc', '+obs', obsFile, '+nav', navFile, file]
    subprocess.call(teqcCommand, cwd = satFilesDir, executable = teqcDir, stdout=subprocess.PIPE)
    obsFileDir = os.path.join(satFilesDir, obsFile)
    obsFileNewDir = os.path.join(obsFilesDir, obsFile)
    navFileDir = os.path.join(satFilesDir, navFile)
    navFileNewDir = os.path.join(navFilesDir, navFile)
    shutil.move(obsFileDir, obsFileNewDir)
    shutil.move(navFileDir,navFileNewDir)

"""
In the following code we download necessary files from online archives to use 
the program RTKPOST of RTKLIB:
"""

firstObsTimeArr = []
for k in tqdm(os.listdir(obsFilesDir), desc = "Determining first observation time for each observation file..."):
    firstObsTimeArr.append(firstObsTime(os.path.join(obsFilesDir, k)))

for i, obs in tqdm(enumerate(os.listdir(obsFilesDir)), desc = "Downloading necessary files from online archives..."):
    firstObsTime = firstObsTimeArr[i] # [[gps week, gps day of week], [utc year, utc day of year]]
    download.sp3File(firstObsTime[0], obs)
    download.clsFile(firstObsTime[0], obs)
    download.ionoFile(firstObsTime[1], obs)
    download.dcbFile(firstObsTime[1])
    download.eopFile(firstObsTime)
   
"""
In the following code we run the rnx2rtkp.exe (CUI of RTKPOST) program from 
RTKLIB, for that we edit the configuration file in the bin directory for each 
observation file which has a different time of first observation, and we get
.pos files which are stored in the posFiles folder:
"""

for i, obs in tqdm(enumerate(os.listdir(obsFilesDir)), desc = "Creating .pos files..."):
    if os.path.isfile(os.path.join(posFilesDir, obs.split(".")[0] + ".pos")) == True:
        continue
    firstObsTime = firstObsTimeArr[i]
    gpsTime = firstObsTime[0]
    utcTime = firstObsTime[1]
    month = utcTime[2]
    if month <= 3:
        trim = "1"
    if month > 3 and month <= 6:
        trim = "2"
    if month > 6 and month <= 9:
        trim = "3"
    if month > 9 and month <= 12:
        trim = "4"
    dcbFileDir = os.path.join(dcbFilesDir, str(utcTime[0]) + trim + ".dcb")
    eopFileDir = os.path.join(eopFilesDir, str(gpsTime[0]) + ".erp")
    ionoFileDir = os.path.join(ionoFilesDir, obs.split(".")[0] + ".21i")
    sp3FileDir = os.path.join(sp3FilesDir, obs.split(".")[0] + ".sp3")
    clsFileDir = os.path.join(clsFilesDir, obs.split(".")[0] + ".cls")
        
    # We create the configuration file in the bin directory:
    configFile(dcbFileDir, eopFileDir, ionoFileDir)
    posFileDir = os.path.join(posFilesDir, obs.split(".")[0] + ".pos")
    navFileDir = os.path.join(navFilesDir, obs.split(".")[0] + ".n")
    obsFileDir = os.path.join(obsFilesDir, obs)
    # We run the program RTKPOST from the cmd with rnx2rtkp.exe to obtain
    # the .pos files that will be stored in the folder posFiles:
    cmd = ["rnx2rtkp.exe", "-k", configurationFileDir, "-o", posFileDir, obsFileDir, navFileDir, sp3FileDir, clsFileDir]
    subprocess.call(cmd, cwd = posFilesDir, executable=rnx2rtkpDir, stdout=subprocess.PIPE)
    resetConfigFile()
    
    
"""
We delete the .netrc file:
"""

cddisNasa.deleteNetrcFile()


"""
We obtain the data that will be ploted afterwards:
"""

lat = [] # latitudes list (degrees)
lon = [] # longitudes list (degrees)
h = [] # heights list (meters)
stdNorth = []
stdEast = []
stdUp = []
lastLat = []
lastLon =[]
lastH = []
lastStdNorth = []
lastStdEast = []
lastStdUp = []
latMin = []
latMax = []
lonMin = []
lonMax = []
heightMin = []
heightMax = []

for posFile in tqdm(os.listdir(posFilesDir), desc = "Obtaining and filtering data from the .pos files..."):
    utcTime, latitude, longitude, height, stdN, stdE, stdU = pos.readPosFile(posFile)
    
    effLatMean, effLonMean, effHeightMean, effLatMinMax, effLonMinMax, effHeightMinMax = pos.effectivePosData(utcTime, latitude, longitude, height)
    effStdNorth, effStdEast, effStdUp, _, __, ___ = pos.effectivePosData(utcTime, stdN[0], stdE[0], stdU[0])
    
    lat.append([utcTime[0], effLatMean])
    lon.append([utcTime[0], effLonMean])
    h.append([utcTime[0], effHeightMean])
    stdNorth.append([utcTime[0], effStdNorth])
    stdEast.append([utcTime[0], effStdEast])
    stdUp.append([utcTime[0], effStdUp])
    lastLat.append([utcTime[0], latitude[-1]])
    lastLon.append([utcTime[0], longitude[-1]])
    lastH.append([utcTime[0], height[-1]])
    lastStdNorth.append([utcTime[0], abs(stdN[0, -1])])
    lastStdEast.append([utcTime[0], abs(stdE[0, -1])])
    lastStdUp.append([utcTime[0], abs(stdU[0, -1])])
    latMin.append(effLatMinMax[0])
    latMax.append(effLatMinMax[1])
    lonMin.append(effLonMinMax[0])
    lonMax.append(effLonMinMax[1])
    heightMin.append(effHeightMinMax[0])
    heightMax.append(effHeightMinMax[1])

lat = sorted(lat, key=lambda x: x[0])
lon = sorted(lon, key=lambda x: x[0])
h = sorted(h, key=lambda x: x[0])
lastLat = sorted(lastLat, key=lambda x: x[0])
lastLon = sorted(lastLon, key=lambda x: x[0])
lastH = sorted(lastH, key=lambda x: x[0])
stdNorth = sorted(stdNorth, key=lambda x: x[0])
stdEast = sorted(stdEast, key=lambda x: x[0])
stdUp = sorted(stdUp, key=lambda x: x[0])

latitudes = []
longitudes = []
heights = []
lastLatitudes = []
lastLongitudes = []
lastHeights = []
stdNorths = []
stdEasts = []
stdUps = []
lastStdNorths = []
lastStdEasts = []
lastStdUps = []
measurementsStartTime = [] # daytime objects, the first index is the first day, the last index is the last day

for k in lat:
    latitudes.append(k[1])
for k in lon:
    longitudes.append(k[1])
for k in h:
    heights.append(k[1])
for k in lastLat:
    lastLatitudes.append(k[1])
for k in lastLon:
    lastLongitudes.append(k[1])
for k in lastH:
    lastHeights.append(k[1])
for k in stdNorth:
    stdNorths.append(k[1])
for k in stdEast:
    stdEasts.append(k[1])
for k in stdUp:
    stdUps.append(k[1])
for k in lastStdNorth:
    lastStdNorths.append(k[1])
for k in lastStdEast:
    lastStdEasts.append(k[1])
for k in lastStdUp:
    lastStdUps.append(k[1])
    
for k in h:
    measurementsStartTime.append(k[0])
    
east, north, up, _, __, ___ = pos.geo2enu(latitudes, longitudes, heights)
_, __, ___, maxEast, maxNorth, maxUp = pos.geo2enu(latMax, lonMax, heightMax)
_, __, ___, minEast, minNorth, minUp = pos.geo2enu(latMin, lonMin, heightMin)

errEast = np.abs(np.array(maxEast) - np.array(minEast))
errNorth = np.abs(np.array(maxNorth) - np.array(minNorth))
errUp = np.abs(np.array(maxUp) - np.array(minUp))

lastEast, lastNorth, lastUp, lastX, lastY, lastZ = pos.geo2enu(lastLatitudes, lastLongitudes, lastHeights)

"""
We plot the data:  
"""

pos.plotDataENU1(measurementsStartTime, east, north, up, stdEasts, stdNorths, stdUps, errEast, errNorth, errUp)
pos.plotDataENU2(measurementsStartTime, lastEast, lastNorth, lastUp, lastStdEasts, lastStdNorths, lastStdUps)
pos.plotDataENU3(measurementsStartTime, east, north, up, stdEasts, stdNorths, stdUps, errEast, errNorth, errUp, lastEast, lastNorth, lastUp, lastStdEasts, lastStdNorths, lastStdUps)
pos.createDataFileENU1(measurementsStartTime, latitudes, longitudes, heights, north, east, up, stdNorths, stdEasts, stdUps, errNorth, errEast, errUp)
pos.createDataFileENU2(measurementsStartTime, lastLatitudes, lastLongitudes, lastHeights, lastNorth, lastEast, lastUp, lastStdNorths, lastStdEasts, lastStdUps)






