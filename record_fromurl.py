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
import urllib.request
import sys

baseurl = "http://locus.creacast.com:9001"

allstreams = ["/acra_wave_farm.mp3",
"/aix-en-provence_arabicus_sonus.ogg",
"/aix_provence_st_jerome.ogg",
"/amsterdam_Patapoe.mp3",
"/brisbane_floodlands.ogg",
"/cologne_aporee.ogg",
"/emporda_aiguamolls.ogg",
"/english_heritage_grimes_graves.ogg",
"/exeter_music_machines.ogg",
"/florence_ears_in_space.mp3",
"/gary_gmo_dunes1.ogg",
"/jasper_ridge_birdcast.mp3",
"/jeju_georo.mp3",
"/kolkata_chittaranjan_colony.mp3",
"/le-rove_niolon.mp3",
"/leamington_point_pelee_canada.ogg",
"/lisboa_graça.mp3",
"/london_camberwell.ogg",
"/london_walworth.mp3",
"/mobile_cl.ogg",
"/nwt_pigneys_wood.ogg",
"/rspb_titchwell_marsh.ogg",
"/sheringham_sheringham_park.ogg",
"/vallejo_bluerocksprings.mp3",
"/vesinet_cerceris.ogg",
"/wave_farm_pond_station_new_york.mp3",
"/zwolle_sonic_heartbeat.ogg"]

allurls = [baseurl + cururl for cururl in allstreams]



def browse_button():
    global folder_path
    filename = filedialog.askdirectory()
    folder_path.set(filename)
    print(filename)



OPTION = []
for k in allurls:
    OPTION.append(k)
    

def record_from_url(fname,url,nbsec=10):
    print ("Connecting to "+url)

    response = urllib.request.urlopen(url, timeout=10.0)

    f = open(fname, 'wb')
    block_size = 1024
    print ("Recording roughly {} seconds of audio Now - Please wait".format(nbsec))

    limit = nbsec
    start = time.time()
    
    while time.time() - start < limit:
        try:
            audio = response.read(block_size)
            if not audio:
                break
            f.write(audio)
            sys.stdout.write('.')
            sys.stdout.flush()
        except Exception as e:
            print ("Error "+str(e))
    f.close()
    sys.stdout.flush()
    print("")
    print ("{} seconds recorded from {} to file {}".format(nbsec,url,fname))


def choose_interface(name):
    global allurls
    for k in range(len(allurls)):
        if k==name:
            #print(k)
            return(k)
    

def Rec(url, save_path,serial_number):
    if len(serial_number)!= 8:
        CallBack()
    
    CHANNELS = int(1)
    fs = 48000
    RECORD_SECONDS = 60 # seconds
   
    def job():
        utc_datetime = datetime.datetime.utcnow()
        WAVE_OUTPUT_FILENAME = "{}_{}.wav".format(os.path.join(save_path,serial_number),utc_datetime.strftime('%Y%m%d_%H%M%S')) 
        print("Currently recording audio....")

        record_from_url(fname=WAVE_OUTPUT_FILENAME,url=url,nbsec=RECORD_SECONDS)

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
variable.set('URL to stream') 
w = tk.OptionMenu(root, variable, *OPTION)
canvas1.create_window(200,180, window=w)
    
but = tk.Button(text='Start Recording', bg='brown', fg='white', font=('helvetica', 9, 'bold'))
canvas1.create_window(200, 250, window=but)
but['command'] = lambda : Rec(variable.get(), folder_path.get() ,entry1.get())

root.mainloop()

