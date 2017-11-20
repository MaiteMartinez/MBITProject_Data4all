@ECHO OFF 

:: this stops any other python processes in the pc
taskkill /F /IM python.exe

:: this stops team viewer and restarts it
taskkill /F /IM TeamViewer.exe
START "" "C:\Program Files (x86)\TeamViewer\TeamViewer.exe" 


:: this launches again the download script
cd C:\DATOS\MBIT\Proyecto\MBITProject_Data4all\Python\

C:\DATOS\Anaconda\Python.exe C:\DATOS\MBIT\Proyecto\MBITProject_Data4all\Python\download_tweets_stream.py

ECHO Run streaming tweets download
PAUSE
