Silent Cities AudioTagging
--

Applying a pretrained DL model to annotate soundscapes. 
This was developed for analyzing the data collected in the [Silent Cities project](https://osf.io/h285u/).

Used model: 
- Audio Tagging on [Audioset](https://research.google.com/audioset/) using LeeNet11 from [PANNs](https://github.com/qiuqiangkong/audioset_tagging_cnn)

Requirements
--
- [pytorch](https://pytorch.org/) 1.4.0
- [librosa](https://librosa.github.io/librosa/)
- tqdm
- pandas
- numpy
- matplotlib

Usage
--
    python tag_silentcities.py [-h] [--length LENGTH] [--nbcat NBCAT]
                       [--folder FOLDER] [--file FILE] [--verbose]
                       [--overwrite] [--out OUT]

    Silent City Audio Tagging with pretrained LeeNet11 on Audioset

    optional arguments:
    -h, --help       show this help message and exit
    --length LENGTH  Segment length
    --nbcat NBCAT    Maximum number of categories for writing annotated csv
    --folder FOLDER  Path to folder with wavefiles, will walk through subfolders
    --file FILE      Path to file to process
    --verbose        Verbose (default False = nothing printed)
    --overwrite      Overwrite files (default False)
    --out OUT        Output file (pandas pickle), default is output.xz

This will save a pandas dataframe as an output file, which can be analyzed as explained in [this notebook](Analysis.ipynb), which generates a heatmap such as this one : 

![Audio tagging of one night long recording in a street of Toulouse, France (March 16th / 17th 2020). Audio tagging was performed using a deep neural network pretrained on the Audioset dataset.
](silentcity.png)

(note though that the notebook preview doesn't seem to work on gitlab, so you have to clone / download the file)

Credits
--
Nicolas Farrugia, IMT Atlantique, 2020. 

Code for Audioset Tagging CNN from [Qiu Qiang Kong](https://github.com/qiuqiangkong/audioset_tagging_cnn)