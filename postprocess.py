import os,sys
import numpy as np
import pandas as pd 
from matplotlib import pyplot as plt 
from analysis import subset_probas
import plotly.graph_objects as go

fewlabels = ['Applause',
'Bird vocalization, bird call, bird song',
'Caw',
'Bee, wasp, etc.',
'Wind noise (microphone)','Rain','Vehicle','Silence']


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


def make_interactive_pdf(Df,list_resolutions = ['0.25H','H','3H','6H','12H','D'],active_beg = 4,subset_labels=fewlabels):
    
    fig = go.Figure()

     ## which resolution is active when starting

    ### loop on resolution 

    for cur_res in list_resolutions:

        probas_agg = average_proba_over_freq(Df,freq_str=cur_res,subset_labels=fewlabels)

        probas_agg['datetime'] = probas_agg.index

        # Create figure

        for curcol in probas_agg.columns:

            fig.add_trace(go.Scatter(x=probas_agg.datetime, y=probas_agg[curcol],name=curcol,visible=False))

            
    nbcol = len(probas_agg.columns)

    # Make one resolution visible trace visible
    for curcol,_ in enumerate(probas_agg.columns):

        fig.data[active_beg*nbcol+curcol].visible = True


    # Create and add slider
    steps = []
    for i in range(len(list_resolutions)): 
        step = dict(
            method="restyle",
            label=list_resolutions[i],
            args=["visible", [False] * len(fig.data)],
        )
        
        for curcol,_ in enumerate(probas_agg.columns):
            step["args"][1][i*nbcol+curcol] = True  # Toggle trace to "visible"
            steps.append(step)
        
    sliders = [dict(
        active=active_beg*nbcol,
        pad={"t": len(list_resolutions)},
        #currentvalue={"prefix": "Resolution: "},
        steps=steps
    )]

    fig.update_layout(
        sliders=sliders
    )
    return fig


if __name__ == "__main__":

    Df = pd.read_pickle('0001.xz')
    fig = make_interactive_pdf(Df)
    fig.write_html("myfig.html")
    fig.show()