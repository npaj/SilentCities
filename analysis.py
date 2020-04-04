import pandas as pd
import numpy as np
from audioset_tagging_cnn.config import labels
import datetime
from matplotlib import pyplot as plt 

from sklearn.manifold import TSNE
from umap import UMAP
import datetime

def extract_subject(Df,partID):
    return Df[Df['id']==partID]

def return_preprocessed(Df,confin_day=datetime.date(2020,3,16)):
    # data
    allprobas = np.stack(Df['probas'])
    labelmax = np.argmax(allprobas,axis=1)
    allembed = np.stack(Df['embedding'])
    allndsi = np.stack(Df['ndsi'])
    allpeaks = np.stack(Df['nbpeaks'])


    # times in seconds after the first acquisition
    listtimes = list(Df['datetime'])
    listdates = list(Df['date'])

    t0 = listtimes[0]
    seconds_after = [(t-t0).total_seconds() for t in listtimes]

    days_after = [(t-confin_day).days for t in listdates]
    
    times = np.stack(Df['time'])
    night_day = np.stack([(curtime.hour < 19) & (curtime.hour > 4) for curtime in times]).astype(int)
    

    return seconds_after,allprobas,allembed,allndsi,night_day,labelmax,allpeaks,days_after


def process_tsne(Df,confin_day=datetime.date(2020,3,16)):
    secs,allprobas,allembed,allndsi,night_day,labelmax,allpeaks,days_after = return_preprocessed(Df,confin_day)
    mytsne = TSNE(n_components=2)
    embed_tsne = mytsne.fit_transform(allembed)
    return embed_tsne,secs,allprobas,allembed,allndsi,night_day,labelmax,allpeaks,days_after



def process_umap(Df,confin_day=datetime.date(2020,3,16)):
    secs,allprobas,allembed,allndsi,night_day,labelmax,allpeaks,days_after = return_preprocessed(Df,confin_day)
    myproj = UMAP(n_components=2,metric='cosine')
    embed_low = myproj.fit_transform(allembed)
    return embed_low,secs,allprobas,allembed,allndsi,night_day,labelmax,allpeaks,days_after



def keep_array_thresh(probasarray,threshold=0.1):
    array_max = np.max(probasarray,axis=0)
    ind_max = np.argwhere(array_max>threshold)

    return ind_max,array_max[ind_max]


def inverse_search(allprobas,label,Df):
    ## find the label in thr list of all labels
    
    ind = int(np.argwhere([c==label for c in labels]))
    
    probas = allprobas[:,ind]
    ind_max = np.argmax(probas)
    files = list(Df.file)
    return files[ind_max]


def subset_probas(Df,search_labels):
    _,allprobas,_,_,_,_,_,_ = return_preprocessed(Df)

    ind_list = []
    for curlabel in search_labels:
        ind_list.append(int(np.argwhere([c==curlabel for c in labels])))

    return allprobas[:,ind_list]


def heatmap_probas(Df,search_labels,nbannot = 30):
    
    prob = subset_probas(Df,search_labels)
    nbobs = prob.shape[0]


    skiptime = nbobs//nbannot ### this is necessary to annotate the x axis, change this value to print more or less date / time labels

    timelabels = [''] * len(Df.datetime)

    origtimes = list(Df.datetime)

    for i in np.arange(0,len(origtimes),skiptime):
        timelabels[i] = origtimes[i]


    fig = plt.figure(figsize=(20,10))
    plt.matshow(prob.T,vmin=0,aspect='auto',cmap=plt.cm.Reds)
    plt.yticks(ticks = range(len(search_labels)),labels=search_labels)
    plt.xticks(ticks = range(len(timelabels)),labels = timelabels,rotation=90)
    plt.colorbar()
    return fig

def figure_embedding(Df,confin_day=datetime.date(2020,3,16)):

    embed_low,seconds_after,allprobas,allembed,allndsi,night_day,labelmax,allpeaks,days_after = process_umap(Df,confin_day)
    
    fig = plt.figure(figsize=(10,10))

    ax = plt.subplot(221)

    scatter = ax.scatter(embed_low[:,0],embed_low[:,1],c=labelmax,alpha=0.7,cmap=plt.cm.tab20)
    ind,indlabels = scatter.legend_elements(num=None)

    whichlabels = np.argwhere(np.bincount(labelmax)).ravel()

    labels_final = [labels[i] for i in whichlabels]

    # produce a legend with the unique colors from the scatter
    legend1 = ax.legend(ind,labels_final,
                        loc="lower left", title="Classes",ncol=3,bbox_to_anchor=(0,1.1))
    plt.title('Colored by Label')

    ax = plt.subplot(222)

    scatter = ax.scatter(embed_low[:,0],embed_low[:,1],c=night_day,alpha=0.8)
    ind,indlabels = scatter.legend_elements(num=None)


    # produce a legend with the unique colors from the scatter
    legend1 = ax.legend(ind,['night','day'],
                        loc="best", title="Classes",ncol=2)
    plt.title('Colored by Night / Day')

    #ax = plt.subplot(223)

    #scatter = ax.scatter(embed_umap[:,0],embed_umap[:,1],c=allndsi,alpha=0.6,cmap=plt.cm.RdBu_r)
    #fig.colorbar(scatter, ax=ax)
    #plt.title('Colored by NDSI')




    ax = plt.subplot(223)


    scatter = ax.scatter(embed_low[:,0],embed_low[:,1],c=allpeaks,alpha=0.6,cmap=plt.cm.hot)
    fig.colorbar(scatter, ax=ax,orientation='horizontal',fraction=0.042)
    plt.title('Only Nb Peaks')


    """ ax = plt.subplot(223)

    allndsi_neg = (allndsi < 0 )

    scatter = ax.scatter(embed_low[allndsi_neg,0],embed_low[allndsi_neg,1],c=allndsi[allndsi_neg],alpha=0.6,cmap=plt.cm.Blues_r)
    fig.colorbar(scatter, ax=ax)
    plt.title('Only negative NDSI') """


    """ 
    ax = plt.subplot(224)

    allndsi_pos = (allndsi > 0 )

    scatter = ax.scatter(embed_low[allndsi_pos,0],embed_low[allndsi_pos,1],c=allndsi[allndsi_pos],alpha=0.6,cmap=plt.cm.spring)
    fig.colorbar(scatter, ax=ax)
    plt.title('Only positive NDSI')
    """


    ax = plt.subplot(224)


    scatter = ax.scatter(embed_low[:,0],embed_low[:,1],c=days_after,alpha=0.1,cmap=plt.cm.hot,vmin=-2)
    fig.colorbar(scatter, ax=ax,orientation='horizontal',fraction=0.042)
    plt.title('Colored by day after confinement')
    
    
    
    return fig