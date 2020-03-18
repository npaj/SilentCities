## Author : Nicolas Farrugia, March 2020
## Silent City Project

import torch
import torchvision.transforms as transforms
import utils
import torch.nn as nn
from torch.nn import functional as F
from importlib import reload
from tqdm import tqdm
import os 
import sys
import numpy as np
from audioset_tagging_cnn.inference import audio_tagging
from datetime import time
import pandas as pd 
from librosa.core import get_duration

import datetime 

import argparse

parser = argparse.ArgumentParser(description='Silent City Audio Tagging with pretrained LeeNet11 on Audioset')
parser.add_argument('--length', default=10, type=int, help='Segment length')
parser.add_argument('--nbcat', default=3, type=int, help='Maximum number of categories for writing annotated csv')
parser.add_argument('--folder', default=None, type=str, help='Path to folder with wavefiles, will walk through subfolders')
parser.add_argument('--file', default=None, type=str, help='Path to file to process')
parser.add_argument('--verbose', action='store_true', help='Verbose (default False = nothing printed)')
parser.add_argument('--overwrite', action='store_true', help='Overwrite files (default False)')
parser.add_argument('--out', default='output.xz', type=str, help='Output file (pandas pickle), default is output.xz')
parser.add_argument('--cuda', action='store_false', help='Use the GPU for acceleration (Default True)')

args = parser.parse_args()

if args.folder is None:
    
    if args.file is None:
        raise(AttributeError("Must provide either a file or a folder"))

verbose = args.verbose
Overwrite = args.overwrite



all_seg = []

if args.folder is None:
    filelist = [args.file]
else:
    filelist = []

    for root, dirs, files in os.walk(args.folder, topdown=False):
        for name in files:
            if name[-3:] == 'WAV':
                filelist.append(os.path.join(root, name))
                #print(currentvid)
                
            
print(filelist)



nbcat = args.nbcat

checkpoint_path='./LeeNet11_mAP=0.266.pth'

if not(os.path.isfile(checkpoint_path)):
    raise(FileNotFoundError("Pretrained model {} wasn't found, did you download it ?".format(checkpoint_path)))

nbsec = args.length


for wavfile in tqdm(filelist):
    csvfile = (wavfile[:-3] + 'csv')
    if not(Overwrite):
        if (os.path.isfile(csvfile)):
            raise(NameError("File has already been processed"))

    _,meta = utils.read_audio_hdr(wavfile,verbose)
        
    beg_seg = 0
    end_seg = np.floor(get_duration(filename=wavfile))

    allpreds = []
    onsets = []

    audioset_proba = []
    n=0

    all_seg_folder = []
    with torch.no_grad():    
        for curstart in tqdm(np.arange(beg_seg,end_seg,nbsec)):

            start = curstart
            
            onsets.append(curstart)

            # Make predictions for audioset 
            clipwise_output, labels,sorted_indexes,embedding = audio_tagging(wavfile,checkpoint_path,offset=curstart,duration=nbsec,usecuda=args.cuda)


            # Print audio tagging top probabilities
            texttagging = ''
            for k in range(nbcat):
                texttagging += np.array(labels)[sorted_indexes[k]]
                proba = 100 * clipwise_output[sorted_indexes[k]]
                texttagging += ' ({0:2.1f}%)'.format(proba)
                texttagging += ', '
            texttagging = texttagging[:-2]

            
            ## AudioSet
            audioset_proba.append(clipwise_output)
            #audioset_fm.append(embedding)

            annotation_str = "{tagging}".format(tagging=texttagging)

            if verbose:
                print(annotation_str)


            onset_dt = time(hour=meta['time'].hour,minute=meta['time'].minute,second=meta['time'].second + int(curstart))
            curdict = dict(time=onset_dt,onsets=curstart,freq=0.5,label=annotation_str,date=meta['date'],probas=clipwise_output)
            curdict2 = dict(time=onset_dt,onsets=curstart,label=annotation_str,date=meta['date'],probas=clipwise_output)

            all_seg.append(curdict2)
            all_seg_folder.append(curdict)
            
    df_forannot = pd.DataFrame(all_seg_folder)
    df_forannot = df_forannot[['onsets','freq','label']]
    df_forannot.to_csv(csvfile,index=False)


df = pd.DataFrame(all_seg)

### Aggregate all datetimes with updated times
alldatetimes = [datetime.datetime(cdate.year,cdate.month,cdate.day,ctime.hour,ctime.minute,ctime.second) for ctime,cdate in zip(df.time,df.date)]

df['datetime'] = alldatetimes

df = df.sort_values(by='datetime')

df.to_pickle(args.out)