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
from librosa.core import get_duration,load
import soundfile as sf

import datetime 

import argparse
from ecoacoustics import compute_NDSI,compute_NB_peaks,compute_ACI

parser = argparse.ArgumentParser(description='Silent City Audio Tagging with pretrained LeeNet11 on Audioset')
parser.add_argument('--length', default=10, type=int, help='Segment length')
parser.add_argument('--nbcat', default=3, type=int, help='Maximum number of categories for writing annotated csv')
parser.add_argument('--folder', default=None, type=str, help='Path to folder with wavefiles, will walk through subfolders')
parser.add_argument('--file', default=None, type=str, help='Path to file to process')
parser.add_argument('--verbose', action='store_true', help='Verbose (default False = nothing printed)')
parser.add_argument('--overwrite', action='store_true', help='Overwrite files (default False)')
parser.add_argument('--out', default='output.xz', type=str, help='Output file (pandas pickle), default is output.xz')
parser.add_argument('--nocuda', action='store_false', help='Do not use the GPU for acceleration')

args = parser.parse_args()

if args.folder is None:
    
    if args.file is None:
        raise(AttributeError("Must provide either a file or a folder"))

verbose = args.verbose
Overwrite = args.overwrite



all_files = []

if args.folder is None:
    filelist = [args.file]
else:
    filelist = []

    for root, dirs, files in os.walk(args.folder, topdown=False):
        for name in files:
            if name[-3:].casefold() == 'wav':
                filelist.append(os.path.join(root, name))
                #print(currentvid)
                
if verbose:            
    print(filelist)



nbcat = args.nbcat

#checkpoint_path='./LeeNet11_mAP=0.266.pth'
checkpoint_path = 'ResNet22_mAP=0.430.pth'

if not(os.path.isfile(checkpoint_path)):
    raise(FileNotFoundError("Pretrained model {} wasn't found, did you download it ?".format(checkpoint_path)))

nbsec = args.length


for wavfile in tqdm(filelist):
    pdfile = (wavfile[:-3] + 'xz')
    try:
        if not(Overwrite):
            if (os.path.isfile(pdfile)):
                
                print(("File {} has already been processed ; loading ".format(wavfile)))

                Df = pd.read_pickle(pdfile)

                all_files.append(Df)
                continue
                
        _,meta = utils.read_audio_hdr(wavfile,verbose)
            
        beg_seg = 0
        end_seg = np.floor(get_duration(filename=wavfile))

        allpreds = []
        onsets = []

        audioset_proba = []
        n=0

        all_seg = []
        with torch.no_grad():    
            for curstart in (np.arange(beg_seg,end_seg,nbsec)):

                start = curstart
                
                onsets.append(curstart)

                # Make predictions for audioset 
                clipwise_output, labels,sorted_indexes,embedding = audio_tagging(wavfile,checkpoint_path,offset=curstart,duration=nbsec,usecuda=args.nocuda)

                ### Calculate Eco acoustic indices
                (waveform, sr) = load(wavfile, sr=None, mono=True,offset=curstart,duration=nbsec)
                
                ndsi = compute_NDSI(waveform,sr)
                nbpeaks = compute_NB_peaks(waveform,sr)

                aci,_ = compute_ACI(waveform,sr)                

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

                current_dt = meta['datetime']

                delta=datetime.timedelta(seconds=int(curstart))

                onset_dt = current_dt + delta

                curdict = dict(datetime=onset_dt,time=onset_dt.time(),file=wavfile,id=meta['id'],onsets=curstart,label=annotation_str,date=onset_dt.date(),probas=clipwise_output,embedding=embedding,ndsi=ndsi,nbpeaks=nbpeaks,aci=aci)

                all_seg.append(curdict)
                
        df_forannot = pd.DataFrame(all_seg)
        df_forannot.to_pickle(pdfile)
        all_files.append(df_forannot)
                
    except Exception as e:
        print('Error with file {}'.format(wavfile))
        raise(e)


df = pd.concat(all_files)

df = df.sort_values(by='datetime')

df.to_pickle(args.out)