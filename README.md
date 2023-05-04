# PPP-Static
PPP Static CSIC IPNA

## Program Overview:
The following program is used to analize raw satellite files through Precise Point Positioning (PPP) in static mode, using only the GPS constellations. The dual frequency observables (L1 + L2) are used un-differenced and combined into the ionosphere-free combination, which allows for the removal of the first order effect of the ionosphere, in order to achieve the expected centimeter-level accuracy, PPP relies on very accurate error models, most of this corrections are obtained from the CDDIS NASA online archives and are the following: *satellite/receiver antenna PCV file (ANTEX file), DCB data file, EOP data file, OTL BLQ data file, ionosphere data file, sp3 data file & clock data file.*

After running the code, a **results** folder is created with the ENU graphs corresponding to the change in N-S, E-W and U-D for each day since the measurements began (the first day has a value of 0m in each graph, and the following days change respect to the first one). Inside the **results** folder we can also find a txt file with the relevant data for each day.

This program was tested with Septentrio raw satellite files, however with other types of raw satellite files should work.
 
## Before using the code follow this instructions:
1.) Download the folder atxFiles from this link: https://drive.google.com/drive/folders/1Ds064zg35fUxMaEipgoBginUHIwsWdP6?usp=sharing. 
Introduce the **atxFiles** folder inside the **data** folder. If you have your own ANTEX files for the antenna and satellite you can follow the same structure as in the **atxFiles** folder in the google drive link.
 
2.) If you have your own raw satellite data you want to analize, introduce the files in the **rawSatelliteFiles** folder inside the **data** folder.

3.) If you don't have an account created in CDDIS NASA create it here: https://urs.earthdata.nasa.gov/users/new

4.) Install WinRAR from this link: https://www.winrar.es/descargas. Set WinRAR to your environment variables.

5.) Create an Spyder (python 3.10) environment from Anaconda, if you don't have Anaconda installed, install it from here: https://www.anaconda.com/download. To create an Spyder environment just click the the button install Spyder in the Anaconda navigator.
 
6.) Finally run the python code **PPPStatic.py**, a window will pop up, select the **rawSatelliteFiles** folder, and finally introduce your CDDIS NASA credentials in the terminal. If the code doesn't work try installing **TEQC** for your Windows system and introducing **teqc.exe** inside the **bin** folder (replacing the already existent *teqc.exe*).
