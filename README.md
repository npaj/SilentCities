Silent City
--

Applying pretrained DL model to annotate soundscapes of the silent cities. 

Used model: 
- Audio Tagging on [Audioset](https://research.google.com/audioset/) using LeeNet11 from [PANNs](https://github.com/qiuqiangkong/audioset_tagging_cnn)

Requirements
--
[pytorch](https://pytorch.org/) 1.4.0
[librosa](https://librosa.github.io/librosa/)

Usage
--
    python audiotagging.py [-h] [--length LENGTH] [--nbcat NBCAT]
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

Credits
--
Nicolas Farrugia, IMT Atlantique, 2020. 

Code for Audioset Tagging CNN from [Qiu Qiang Kong](https://github.com/qiuqiangkong/audioset_tagging_cnn))