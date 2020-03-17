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

verbose = False
Overwrite = True

wavfile = sys.argv[1]
csvfile = (wavfile[:-3] + 'csv')

_,meta = utils.read_audiomoth_hdr(wavfile)

if not(Overwrite):
    if (os.path.isfile(csvfile)):
        raise(NameError("File has already been processed"))

nbcat = int(sys.argv[2])

checkpoint_path='./LeeNet11_mAP=0.266.pth'

nbsec = 10

beg_seg = 0
end_seg = np.floor(get_duration(filename=wavfile))

allpreds = []
onsets = []

#audioset_fm = []
audioset_proba = []
n=0

all_seg = []


with torch.no_grad():    
    for curstart in tqdm(np.arange(beg_seg,end_seg,nbsec)):

        start = curstart
        
        onsets.append(curstart)

        # Make predictions for audioset 
        clipwise_output, labels,sorted_indexes,embedding = audio_tagging(wavfile,checkpoint_path,offset=curstart,duration=nbsec,usecuda=True)


        # Print audio tagging top probabilities
        texttagging = ''
        for k in range(nbcat):
            texttagging += np.array(labels)[sorted_indexes[k]]
            proba = 100 * clipwise_output[sorted_indexes[k]]
            texttagging += ' ({0:2.1f}%)'.format(proba)
            texttagging += ', '
        texttagging = texttagging[:-2]

        
        ## AUdioSet
        audioset_proba.append(clipwise_output)
        #audioset_fm.append(embedding)

        annotation_str = "{tagging}".format(tagging=texttagging)

        if verbose:
            print(annotation_str)

        ### Append to srt file with timecode 
        #annotation_str = "{tagging}\n".format(tagging=texttagging)
        #utils.gen_srt(annotation_str,int(np.round(start)),srtfile=srtfile,num=n,duration=int(np.floor(nbsec)))
        #n=n+1

        onset_dt = time(hour=meta['time'].hour,minute=meta['time'].minute,second=meta['time'].second + int(curstart))

        all_seg.append(dict(time=onset_dt,onsets=curstart,freq=0.5,label=annotation_str,date=meta['date']))


df = pd.DataFrame(all_seg)

df_forannot = df[['onsets','freq','label']]
df_forannot.to_csv(csvfile,index=False)