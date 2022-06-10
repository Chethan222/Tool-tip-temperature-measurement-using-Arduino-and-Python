# Importing Libraries
import serial
import time as tm
import matplotlib.pyplot as plt
import matplotlib.animation as anim
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
from csv import writer


#Setting figure sizes
plt.rcParams["figure.figsize"] = [7.50, 3.50]
plt.rcParams["figure.autolayout"] = True

# plt.style.use(['dark_background'])

fig, ax = plt.subplots()

#Getting data from serial 
def getData():
    tm.sleep(1.5)
    return arduino.readline().decode('utf-8').rstrip('\n\r')

#Writing data to the file
def writeToFile(data,):
    with open('tool-tip-temperatures.csv', 'a',newline='' ) as file:
        #Initializing the writer object with past temperatures 
        writerObj = writer(file)
        
        #Writing new current temeprature
        writerObj.writerow(data)

#Function to update the graph
def update(frame):
  
    time = datetime.now()
    time = time.strftime('%H:%M:%S')
    data = getData()
                
    if len(data)>0:
        cval,fval = data.split(',')
        print('temperature :',cval,'(°C) at',time)

        #Converting temperature-data into dataframe
        temperatureData = pd.DataFrame({'time':[time],'temperature(°C)':[cval]})
        
        #Writing the current temperature to file
        writeToFile(temperatureData.values.tolist()[0])
        
        #Loading temperature data
        dataframe = pd.read_csv('tool-tip-temperatures.csv')
        dataframe.append(temperatureData)
    
        #Plotting the temperatures
        ax.plot(pd.to_datetime(dataframe['time']),dataframe['temperature(°C)'],'b-o')

        #Adding labels
        ax.set_xlabel('time')
        ax.set_ylabel('temperature(°C)')
        
    
#Configuring the serial port data
arduino = serial.Serial(port='COM3', baudrate=9600, timeout=.1)

print('\n####### Temperatures from the thermocouple ######\n')

plt.xticks(rotation=45, ha="right", rotation_mode="anchor") 
plt.subplots_adjust(bottom = 0.2, top = 0.9) 
ani = anim.FuncAnimation(fig, update,interval=500)
plt.show()

   
   
    