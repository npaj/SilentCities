### Silent Cities
### AUthor : Nicolas Pajuco, Nicolas Farrugia

from tkinter import filedialog
# from tkinter import *
import tkinter as tk
import schedule
import numpy as np
from scipy.io import wavfile
import sounddevice as sd
import datetime
import time
from tkinter import messagebox
import os
def browse_button():
    global folder_path
    filename = filedialog.askdirectory()
    folder_path.set(filename)
    print(filename)



devices = sd.query_devices()
OPTION = []
for k in devices:
    OPTION.append(k['name'])
    



def choose_interface(name):
    devices = sd.query_devices()
    for k in range(len(devices)):
        if devices[k]['name']==name:
            #print(k)
            return(k)
    

def Rec(interface_name, save_path,serial_number):
    if len(serial_number)!= 8:
        CallBack()
    
    CHANNELS = int(1)
    fs = 48000
    RECORD_SECONDS = 60 # seconds
    device = choose_interface(interface_name)
    sd.default.device = device
   
    def job():
        utc_datetime = datetime.datetime.utcnow()
        WAVE_OUTPUT_FILENAME = "{}_{}.wav".format(os.path.join(save_path,serial_number),utc_datetime.strftime('%Y%m%d_%H%M%S')) 
        print("Currently recording audio....") 
        result = sd.rec(int(RECORD_SECONDS*fs),samplerate = fs, channels =CHANNELS ,blocking = True,dtype = 'int16')
        wavfile.write(WAVE_OUTPUT_FILENAME,fs,result)

        print("done recording, file : {}".format(WAVE_OUTPUT_FILENAME))

        
    print('Running..')
    schedule.every().hour.at(":00").do(job)
    schedule.every().hour.at(":10").do(job)
    schedule.every().hour.at(":20").do(job)
    schedule.every().hour.at(":30").do(job)
    schedule.every().hour.at(":40").do(job)
    schedule.every().hour.at(":50").do(job)
    
    while True:
        schedule.run_pending()
        time.sleep(1)

def CallBack():
        messagebox.showinfo('Message', 'ID must be 8 characters')

root= tk.Tk()

canvas1 = tk.Canvas(root, width = 400, height = 300,  relief = 'raised')
canvas1.pack()

label1 = tk.Label(root, text='Bio Acoustique')
label1.config(font=('helvetica', 14))
canvas1.create_window(200, 25, window=label1)

label2 = tk.Label(root, text='ID (serial number):')
label2.config(font=('helvetica', 10))
canvas1.create_window(80, 80, window=label2)

entry1 = tk.Entry (root) 
canvas1.create_window(250,80, window=entry1)

folder_path = tk.StringVar()
lbl1 = tk.Label(master=root,textvariable=folder_path)
canvas1.create_window(120,120, window=lbl1)
button2 = tk.Button(text="Save Folder", command=browse_button)
canvas1.create_window(320,120, window=button2)
variable = tk.StringVar(root)
variable.set('Audio interface') 
w = tk.OptionMenu(root, variable, *OPTION)
canvas1.create_window(200,180, window=w)
    
but = tk.Button(text='Start Recording', bg='brown', fg='white', font=('helvetica', 9, 'bold'))
canvas1.create_window(200, 250, window=but)
but['command'] = lambda : Rec(variable.get(), folder_path.get() ,entry1.get())

root.mainloop()

