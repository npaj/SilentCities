import os,sys
import numpy as np
import pandas as pd 
from matplotlib import pyplot as plt 
from analysis import subset_probas

fewlabels = ['Applause',
'Bird vocalization, bird call, bird song',
'Chirp, tweet',
'Pigeon, dove',
'Caw',
'Bee, wasp, etc.',
'Wind noise (microphone)','Rain','Vehicle','Emergency vehicle','Rail transport','Aircraft','Silence']


def average_proba_over_freq(Df,freq_str='D',subset_labels=fewlabels):
    """
    Calculates probability density estimates over a configurable frequency

    arguments :
    Df : DataFrame, output of tag_silentcities
    freq_str : Frequency over which to calculate probability density estimate (default : days)
    subset_labels : Subset of labels from the Audioset Ontology to be used for the estimate. 
    default labels are :
    'Applause','Bird vocalization, bird call, bird song','Chirp, tweet','Pigeon, dove',
    'Caw','Bee, wasp, etc.','Wind noise (microphone)','Rain','Vehicle','Emergency vehicle','Rail transport',
    'Aircraft','Silence'

    outputs : 
    
    probas_agg : Probability Density estimates of the subset of labels calculate according to the frequency specified

    """
    #Let's use the datetime (Timestamp) as a new index for the dataframe
    ts = pd.DatetimeIndex(Df.datetime)
    Df.index = ts

    # Let's add the Labels from the shortlist as entries in the Df. Will be easier to manipulate them afterwards
    
    prob = subset_probas(Df,subset_labels)

    for f,curlabel in enumerate(subset_labels):
        Df[curlabel] = prob[:,f]

    # Now let's create a period range to easily compute statistics over days (frequency can be changed by changing the freq_str argument)
    prng = pd.period_range(start=ts[0],end=ts[-1], freq=freq_str).astype('datetime64[ns]')

    # And now create the final DataFrame that averages probabilities (of labels subset_labels) with the frequency defined in freq_str

    allser = dict()

    for lab in fewlabels:

        curser = pd.Series([Df[prng[i]:prng[i+1]][lab].mean() for i in range(len(prng)-1)],index=prng[:-1])
        
        allser[lab] = curser
        
    probas_agg = pd.DataFrame(allser)

    return probas_agg