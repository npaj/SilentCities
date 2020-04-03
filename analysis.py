import pandas as pd
import numpy as np
from audioset_tagging_cnn.config import labels
import datetime
from matplotlib import pyplot as plt 

from sklearn.manifold import TSNE
from umap import UMAP


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



def process_umap(Df):
    secs,allprobas,allembed,allndsi,night_day,labelmax = return_preprocessed(Df)
    myproj = UMAP(n_components=2,metric='cosine')
    embed_low = myproj.fit_transform(allembed)
    return embed_low,secs,allprobas,allembed,allndsi,night_day,labelmax



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



def figure_embedding(Df):

    embed_low,seconds_after,allprobas,allembed,allndsi,night_day,labelmax = process_umap(Df)
    
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
                        loc="lower left", title="Classes",ncol=2)
    plt.title('Colored by Night / Day')

    #ax = plt.subplot(223)

    #scatter = ax.scatter(embed_umap[:,0],embed_umap[:,1],c=allndsi,alpha=0.6,cmap=plt.cm.RdBu_r)
    #fig.colorbar(scatter, ax=ax)
    #plt.title('Colored by NDSI')





    ax = plt.subplot(223)

    allndsi_neg = (allndsi < 0 )

    scatter = ax.scatter(embed_low[allndsi_neg,0],embed_low[allndsi_neg,1],c=allndsi[allndsi_neg],alpha=0.6,cmap=plt.cm.Blues_r)
    fig.colorbar(scatter, ax=ax)
    plt.title('Only negative NDSI')



    ax = plt.subplot(224)

    allndsi_pos = (allndsi > 0 )

    scatter = ax.scatter(embed_low[allndsi_pos,0],embed_low[allndsi_pos,1],c=allndsi[allndsi_pos],alpha=0.6,cmap=plt.cm.spring)
    fig.colorbar(scatter, ax=ax)
    plt.title('Only positive NDSI')
    
    
    return fig