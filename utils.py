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


def read_audiomoth_hdr(strWAVFile):
# Open file
    fileIn = open(strWAVFile, 'rb')
        
    # end try
    # Read in all data
    bufHeader = fileIn.read(200)
    fileIn.close()


    AMOhdr = str(bufHeader[56:170])
    
    words = AMOhdr.split()
    
    curtime = datetime.datetime.strptime(str(words[2]),"%H:%M:%S").time()
    curdate = datetime.datetime.strptime(str(words[3]),"%d/%m/%Y").date()
    AMOid = words[7]
    gain = float(words[11])
    battery = words[16]

    metadata = dict(time=curtime,date=curdate,AMOid=AMOid,gain=gain,battery=float(battery[:-2]))

    return AMOhdr,metadata