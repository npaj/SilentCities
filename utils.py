## Author : Nicolas Farrugia, Feb/March 2020

import torch
from torchvision.io import read_video,read_video_timestamps

import matplotlib.patches as patches
from matplotlib import pyplot as plt

import datetime

import os

def convert_Audio(mediaFile, outFile):
    cmd = 'ffmpeg -i '+mediaFile+' '+outFile
    os.system(cmd)
    return outFile

def gen_srt(strlabel,onset,srtfile,duration=2,num=1):

    starttime = onset
    endtime = starttime + duration

    string_start = datetime.time(0,starttime//60,starttime%60).strftime("%H:%M:%S")

    string_end = datetime.time(0,endtime//60,endtime%60).strftime("%H:%M:%S")

    with open(srtfile,'a') as f:
        f.write("{}\n".format(num+1))
        f.write("{starttime} --> {endtime}\n".format(starttime=string_start,endtime=string_end))
        f.write("{}\n".format(strlabel))
        f.write("\n")


def read_audio_hdr(strWAVFile):
# Open file
    fileIn = open(strWAVFile, 'rb')
        
    # end try
    # Read in all data
    bufHeader = fileIn.read(200)
    fileIn.close()


    AMOhdr = str(bufHeader[56:170])
    
    
    words = AMOhdr.split()
    if 'Recorded' in words[0]:
        curtime = datetime.datetime.strptime(str(words[2]),"%H:%M:%S").time()
        curdate = datetime.datetime.strptime(str(words[3]),"%d/%m/%Y").date()
        AMOid = words[7]
        print('Audiomoth detected, ID is {}'.format(AMOid))
        
        gain = float(words[11])
        battery = words[16]

        metadata = dict(time=curtime,date=curdate,id=AMOid,gain=gain,battery=float(battery[:-2]))
    else:
        
        curtime = datetime.datetime.strptime(strWAVFile[-10:-5],"%H%M%S").time()
        curdate = datetime.datetime.strptime(strWAVFile[-19:-12],"%Y%m%d").date()

        SM4id = strWAVFile[-28:-20]
        print('SM4 detected, ID is {}'.format(SM4id))

        metadata = dict(time=curtime,date=curdate,id=SM4id,gain=0,battery=0)

    return AMOhdr,metadata