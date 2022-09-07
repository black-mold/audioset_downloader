# audioset_downloader

- AudioSet csv file download link : https://research.google.com/audioset/download.html


### Folder configuration : './audioset_csv'
- Download belows. and move them at './audioset_csv'
- http://storage.googleapis.com/us_audioset/youtube_corpus/v1/csv/eval_segments.csv
- http://storage.googleapis.com/us_audioset/youtube_corpus/v1/csv/balanced_train_segments.csv
- http://storage.googleapis.com/us_audioset/youtube_corpus/v1/csv/unbalanced_train_segments.csv
- http://storage.googleapis.com/us_audioset/youtube_corpus/v1/csv/class_labels_indices.csv

### Step for AudioSet download

1. create pickle or csv file.
   * origin files located at 'audioset_csv' folder
   * created files will be located at 'csv_files' folder

2. download AudioSet files by classes




### code

1. create pickle or csv files

- To generate csv and pickle files located at ./audioset_csv/ folder 

```

```

2. download AudioSet files by classes

```
python download.py -c /m/09x0r -pn eval_segments.pickle
```
