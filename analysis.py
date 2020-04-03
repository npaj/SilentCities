import pandas as pd
import numpy as np
from audioset_tagging_cnn.config import labels
import datetime
from matplotlib import pyplot as plt 

from sklearn.manifold import TSNE

def extract_subject(Df,partID):
    return Df[Df['id']==partID]

def return_preprocessed(Df):
    # data
    allprobas = np.stack(Df['probas'])
    labelmax = np.argmax(allprobas,axis=1)
    allembed = np.stack(Df['embedding'])
    allndsi = np.stack(Df['ndsi'])

    # times in seconds after the first acquisition
    listtimes = list(Df['datetime'])
    t0 = listtimes[0]
    seconds_after = [(t-t0).total_seconds() for t in listtimes]
    
    times = np.stack(Df['time'])
    night_day = np.stack([(curtime.hour < 19) & (curtime.hour > 4) for curtime in times]).astype(int)

    return seconds_after,allprobas,allembed,allndsi,night_day,labelmax


def process_tsne(Df):
    secs,allprobas,allembed,allndsi,night_day,labelmax = return_preprocessed(Df)
    mytsne = TSNE(n_components=2)
    embed_tsne = mytsne.fit_transform(allembed)
    return embed_tsne,secs,allprobas,allembed,allndsi,night_day,labelmax



def keep_array_thresh(probasarray,threshold=0.1):
    array_max = np.max(probasarray,axis=0)
    ind_max = np.argwhere(array_max>threshold)

    return ind_max,array_max[ind_max]


def inverse_search(allprobas,labels_all,label,Df):
    ## find the label in thr list of all labels
    
    ind = int(np.argwhere([c==label for c in labels_all]))
    
    probas = allprobas[:,ind]
    ind_max = np.argmax(probas)
    files = list(Df.file)
    return files[ind_max]