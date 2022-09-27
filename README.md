# audioset_downloader

- AudioSet csv file download link : https://research.google.com/audioset/download.html


### './audioset_csv'
- Download items below. And move them to './audioset_csv'
- http://storage.googleapis.com/us_audioset/youtube_corpus/v1/csv/eval_segments.csv
- http://storage.googleapis.com/us_audioset/youtube_corpus/v1/csv/balanced_train_segments.csv
- http://storage.googleapis.com/us_audioset/youtube_corpus/v1/csv/unbalanced_train_segments.csv
- http://storage.googleapis.com/us_audioset/youtube_corpus/v1/csv/class_labels_indices.csv


### './csv_files'
- Transformation of './audioset_csv'' files to use pandas library.
-

### Step for AudioSet download

1. create pickle or csv file.
   * origin files located at 'audioset_csv' folder
   * created files will be located at 'csv_files' folder

2. download AudioSet files by classes




### 1. Audioset download code

1. create pickle or csv files

- To generate csv and pickle files located at ./audioset_csv/ folder 

```

```

2. download AudioSet files by classes

```
# download class : /m/09x0r, partition : eval_segments
python download.py -c /m/09x0r -pn eval_segments.pickle

# download class : /m/09x0r, partition : balanced_train_segments
python download.py -c /m/09x0r -pn balanced_train_segments.pickle

# download class : /m/09x0r, partition : unbalanced_train_segments
python download.py -c /m/09x0r -pn eval_segments.pickle
```


### 2. Audioset(strong) download code
'''
# download. class : /m/03qc9zr, partition : train
python download_strong.py -m target -c /m/03qc9zr -t ./audioset_csv/audioset_train_strong.tsv

# download all classes. partition : eval
python download_strong.py -m all -t ./audioset_csv/audioset_eval_strong.tsv
# 
'''
