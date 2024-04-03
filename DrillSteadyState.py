import numpy as np
import imutils
import cv2
import csv
import pandas as pd
dataname = 'SteadyState.csv'

#T, V, and P correspond to Time, Voltage, and Power
#11, 12, 21, 22; the first number corresponds to speed, the second number is trial
#for example: V21 is the Voltage values in speed 2 trial 1, listed as Voltage21 in the CSV
#CSV files are formatted with the first row as headers with the full name such as Voltage21

# Read the CSV file into a DataFrame
dataframe_SS = pd.read_csv('SteadyState.csv')

# Extract each column as a separate variable and convert to float
T11 = dataframe_SS['Time11'].astype(float)
T12 = dataframe_SS['Time12'].astype(float)
T21 = dataframe_SS['Time21'].astype(float)
T22 = dataframe_SS['Time22'].astype(float)
V11 = dataframe_SS['Voltage11'].astype(float)
V12 = dataframe_SS['Voltage12'].astype(float)
V21 = dataframe_SS['Voltage21'].astype(float)
V22 = dataframe_SS['Voltage22'].astype(float)
P11 = dataframe_SS['Power11'].astype(float)
P12 = dataframe_SS['Power12'].astype(float)
P21 = dataframe_SS['Power21'].astype(float)
P22 = dataframe_SS['Power22'].astype(float)

movavg = 20 # size of moving average, no need to change if not using moving average
intsize = 1500 # size of moving interval
Termina = 0 # 0=V11, 1 = V12, 2 = V21, 3 = V22
buffer = .1 # to add a bit of leniency to std deviation if too tight

Final = np.size(V11) #size of interval, assuming all columns are the same size
for i in range(Final-movavg,Final): #chops off moving average value from end of column
    T11.pop(i)
    V11.pop(i)
    T12.pop(i)
    V12.pop(i)
    T21.pop(i)
    V21.pop(i)
    T22.pop(i)
    V22.pop(i)
    P11.pop(i)
    P12.pop(i)
    P21.pop(i)
    P22.pop(i)

minV11 = np.argmin(V11) #find minumum values to set startzero
minV12 = np.argmin(V12)
minV21 = np.argmin(V21)
minV22 = np.argmin(V22)

if Termina == 0: #V11
    Final = np.size(V11)
    movint = []  # initialize interval
    startmean = 0 #boolean variable condition
    startzero = 0 #boolean variable condition
    startthresh = 0 #boolean variable condition
    zcount = 0 #position in data
    powercalc = 0 #intializing energy calculation variable
    for z in range(Final-1): #standard deviation of known steady state region
        if T11[z] > 1 and T11[z] < 2: #between 1 and 2 seconds
            movint = np.insert(movint,zcount,V11[z])
            zcount += 1
    stdcheck = np.std(movint) #comparison standard deviation
    meancheck = np.mean(movint) #comparison for mean
    movint = [] #re intialize moving interval
    for x in range(Final-1):
        powercalc = powercalc + P11[x] * (T11[x+1]-T11[x]) #calculates energy values using numerical integration
        if startzero == 0: #check 1 to make sure we are on a nonzero x value
            if (T11[x]) > (T11[minV11]):
                startzero = 1
        if startzero == 1 and startmean == 0: #check 2 to make sure we have reached above mean steady state, always peaks before
            if V11[x] > meancheck:
                startmean = 1
        if startzero == 1 and startmean == 1 and startthresh == 0:
            if V11[x] < V11[x-1]:
                startthresh = 1
        if startmean == 1 and startzero == 1 and startthresh == 1 and Termina == 0: #proceed to start calc
            for y in range(intsize-1): # moving interval to calculate std deviation
                locmain = x+y-1
                locmov = y
                movint = np.insert(movint,locmov,V11[locmain])
            std = np.std(movint) #std dev calc
            movint = [] #clear interval
            if std < stdcheck + buffer and Termina == 0: #std is within the std of the steady state, meaning they're the same
                starttimeloc = (T11[x]) # Starting time of standard deviation
                Termina += 1 #next set of data
                print("Steady State start time for Speed 1 for Trial 1: " + str(starttimeloc) + " seconds")
                print("Energy required for startup Speed 1 Trial 1: " + str("%.2f" % powercalc) + " Joules")

if Termina == 1: #V12; will continue to cycle through all trials and samples once
   Final = np.size(V12)
   movint = []  # initialize interval
   startmean = 0
   startzero = 0
   startthresh = 0
   zcount = 0
   powercalc = 0
   for z in range(Final-1): #standard deviation of known steady state region
       if T12[z] > 1 and T12[z] < 2: #between 1 and 2 seconds
           movint = np.insert(movint,zcount,V12[z])
           zcount += 1
   stdcheck = np.std(movint) #comparison standard deviation
   meancheck = np.mean(movint) #comparison for mean
   movint = [] #re intialize moving interval
   for x in range(Final-1):
       powercalc = powercalc + P12[x] * (T12[x+1]-T12[x])
       if startzero == 0: #check 1 to make sure we are on a nonzero x value
           if (T12[x]) > (T12[minV12]):
               startzero = 1
       if startzero == 1 and startmean == 0: #check 2 to make sure we have reached above mean steady state, always peaks before
           if V12[x] > meancheck:
               startmean = 1
       if startzero == 1 and startmean == 1 and startthresh == 0:
           if V12[x] < V12[x-1]:
               startthresh = 1
       if startmean == 1 and startzero == 1 and startthresh == 1 and Termina == 1: #proceed to start calc
           for y in range(intsize-1): # moving interval to calculate std deviation
               locmain = x+y-1
               locmov = y
               movint = np.insert(movint,locmov,V12[locmain])
           std = np.std(movint) #std dev calc
           movint = [] #clear interval
           if std < stdcheck + buffer and Termina == 1: # adjust standard deviation value
               starttimeloc = (T12[x]) # Starting time of standard deviation
               Termina += 1 #next set of points
               print("Steady State start time for Speed 1 for Trial 2: " + str(starttimeloc) + " seconds")
               print("Energy required for startup Speed 1 Trial 2: " + str("%.2f" %powercalc) + " Joules")

if Termina == 2: #V21
   Final = np.size(V21)
   movint = []  # initialize interval
   startmean = 0
   startzero = 0
   startthresh = 0
   zcount = 0
   powercalc = 0
   for z in range(Final-1): #standard deviation of known steady state region

       if T21[z] > 1 and T21[z] < 2: #between 1 and 2 seconds
           movint = np.insert(movint,zcount,V21[z])
           zcount += 1
   stdcheck = np.std(movint) #comparison standard deviation
   meancheck = np.mean(movint) #comparison for mean
   movint = [] #re intialize moving interval
   for x in range(Final-1):
       powercalc = powercalc + P21[x] * (T21[x+1]-T21[x])
       if startzero == 0: #check 1 to make sure we are on a nonzero x value
           if (T21[x]) > (T21[minV21]):
               startzero = 1
       if startzero == 1 and startmean == 0: #check 2 to make sure we have reached above mean steady state, always peaks before
           if V21[x] > meancheck:
               startmean = 1
       if startzero == 1 and startmean == 1 and startthresh == 0:
           if V21[x] < V21[x-1]:
               startthresh = 1
       if startmean == 1 and startzero == 1 and startthresh == 1 and Termina == 2: #proceed to start calc
           for y in range(intsize-1): # moving interval to calculate std deviation
               locmain = x+y-1
               locmov = y
               movint = np.insert(movint,locmov,V21[locmain])
           std = np.std(movint) #std dev calc
           movint = [] #clear interval
           if std < stdcheck + buffer and Termina == 2: # adjust standard deviation value
               starttimeloc = (T21[x]) # Starting time of standard deviation
               Termina += 1 #next set of points
               print("Steady State start time for Speed 2 for Trial 1: " + str(starttimeloc) + " seconds")
               print("Energy required for startup Speed 2 Trial 1: " + str("%.2f" %powercalc) + " Joules")

if Termina == 3: #V22
   Final = np.size(V22)
   movint = []  # initialize interval
   startmean = 0
   startzero = 0
   startthresh = 0
   zcount = 0
   powercalc = 0
   for z in range(Final-1): #standard deviation of known steady state region
       if T22[z] > 1 and T22[z] < 2: #between 1 and 2 seconds
           movint = np.insert(movint,zcount,V22[z])
           zcount += 1
   stdcheck = np.std(movint) #comparison standard deviation
   meancheck = np.mean(movint) #comparison for mean
   movint = [] #re intialize moving interval
   for x in range(Final-1):
       powercalc = powercalc + P22[x] * (T22[x+1]-T22[x])
       if startzero == 0: #check 1 to make sure we are on a nonzero x value
           if (T22[x]) > (T22[minV22]):
               startzero = 1
       if startzero == 1 and startmean == 0: #check 2 to make sure we have reached above mean steady state, always peaks before
           if V22[x] > meancheck:
               startmean = 1
       if startzero == 1 and startmean == 1 and startthresh == 0:
           if V22[x] < V22[x-1]:
               startthresh = 1
       if startmean == 1 and startzero == 1 and startthresh == 1 and Termina == 3: #proceed to start calc
           for y in range(intsize-1): # moving interval to calculate std deviation
               locmain = x+y-1
               locmov = y
               movint = np.insert(movint,locmov,V22[locmain])
           std = np.std(movint) #std dev calc
           movint = [] #clear interval
           if std < stdcheck + buffer and Termina == 3: # adjust standard deviation value
               starttimeloc = (T22[x]) # Starting time of standard deviation
               Termina += 1 #next set of points
               print("Steady State start time for Speed 2 for Trial 2: " + str(starttimeloc) + " seconds")
               print("Energy required for startup Speed 2 Trial 2: " + str("%.2f" %powercalc) + " Joules")