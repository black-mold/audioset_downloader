
import subprocess
import os
import time
import pickle
import csv
import argparse
import re

import pandas as pd
from tqdm import tqdm



## Youtube_download
def download(youtube_id, ext, raw_audio_dir):
    """
    Args:
        youtube_id : https://www.youtube.com/watch?v={youtube_id}
        start_time : audio start time(it is only use for naming)
        end_time : audio end time(it is only use for naming)
        ext : wav, m4a, etc.

    Returns : 
        file_name 
    """
    # print(f'youtube-dl --force-ipv4 --extract-audio --audio-format wav --audio-quality 0 -o ./download/raw_audio/{youtube_id}.{ext} https://www.youtube.com/watch?v={youtube_id}')
    command = (f'youtube-dl --force-ipv4 --extract-audio --audio-format wav --audio-quality 0 -o {raw_audio_dir}{youtube_id}.{ext} https://www.youtube.com/watch?v={youtube_id}')
    #file name : YouTubeID.wav
    subprocess.call(command,shell=True,stdout=None)

    file_name = f'{youtube_id}.{ext}'
    time.sleep(3)   

    return file_name


def audio_cut_10s(file_name, start, end, slice_audio_dir, raw_audio_dir):
    """
    Args: 
        file_name : audio file to be sliced
        start : audio start time
        save_dir : save directory for sliced audio file. default : ./download/slice_audio/
        csv_partition : balanced_train_segments or eval_segments or unbalanced_train_segments  ex.) balanced_train_segments
    """

    # youtube_id = file_name[:file_name.index('_')]
    if not os.path.exists(slice_audio_dir):
        os.makedirs(slice_audio_dir)

    file_name_only = os.path.splitext(file_name)[0] # not contain extension

    command = (f'ffmpeg -y -ss {start} -t 10 -i {raw_audio_dir}{file_name} {slice_audio_dir}/{file_name_only}_{start}_{end}.wav')    
    subprocess.call(command,shell=True,stdout=None)
    # ffmpeg -ss 0 -t 10 -i ./raw_audio/-0DdlOuIFUI.wav hhj3.wav


def download_from_pd(df_target, save_dir, target_class, csv_partition, raw_audio_dir):
    """
    main function

    Args:
        df_target :
        save_dir : save directory for sliced audio file. default : ./download/slice_audio/ 
        csv_partition : balanced_train_segments or eval_segments or unbalanced_train_segments  ex.) balanced_train_segments
    
    """

    target_class_display_name = target_encoder(target_class = target_class).replace(" ", "_")
    slice_audio_dir = f'{save_dir}{target_class_display_name}/{csv_partition}'  # directory for sliced audio file


    for i in tqdm(range(len(df_target.loc[:]))):
        youtube_id = df_target.iloc[i,0]
        start = df_target.iloc[i,1].strip()  # .strip() : remove space
        end = df_target.iloc[i,2].strip()    # .strip() : remove space
        labels = df_target.iloc[i,3]
        # import pdb
        # pdb.set_trace()
    
        file_name = download(youtube_id, ext = 'wav', raw_audio_dir = raw_audio_dir)

        if os.path.isfile(f'{raw_audio_dir}{file_name}'): # audio download check

            audio_cut_10s(file_name, start, end, slice_audio_dir, raw_audio_dir)

            #label_save
            display_name = []

            for t in labels:

                if t[0:2] == ' "':
                    t = t[2:]

                if t[-1] == '"':
                    t = t[:-1]

                display_name.append(target_encoder(target_class = t))


            df = pd.DataFrame([[[youtube_id], [start], [end], labels, display_name]], columns = ['youtube_id', 'start', 'end', 'labels', 'display_name'])
            df.to_csv(f"{slice_audio_dir}/{os.path.splitext(file_name)[0]}_{start}_{end}.csv", mode = 'w', header = True)

    
    print("done")
    return youtube_id, start, end


def class_finder(df, target_class):
    
    df_target = pd.DataFrame(columns = ['YoutubeID', 'start', 'end', 'labels'])


    for i in range(len(df.loc[:])):
        for label in df.iloc[i, 3]:
            # print(label)
            if label.find(target_class) != -1 :
                # print(i)
                df_target = pd.concat([df_target, pd.DataFrame([list(df.iloc[i,:])], columns = ['YoutubeID', 'start', 'end', 'labels'])], ignore_index = True)

                
    return df_target


def target_encoder(class_labels_indices_dir = './audioset_csv/class_labels_indices.csv', target_class = ''):
    """
    Args: 
        target_class : mid columns at 'class_labels_indices.csv' file . ex) '/m/09x0r'
    
    return:
        display_name : display name columns at 'class_labels_indices.csv' file. ex) Speech
    """
    df = pd.read_csv(class_labels_indices_dir)

    for i in range(len(df.loc[:])):
        if (df.iloc[i, 1] == target_class):
            display_name = df.iloc[i, 2]

    if display_name == None :
        print("error : check class label")

    return display_name


def read_AudioSet_csv(audioset_csv, csv_save = False, pickle_save = False):

    """
    read csv given AudioSet, return csv to be used pandas library    
    """

    df = pd.DataFrame()

    f = open(f'{audioset_csv}')
    r = csv.reader(f)


    # csv processing
    print("\n ------csv(AudioSet) -> DataFrame-------- \n")
    for i, row in tqdm(enumerate(r, 0)):
        if i >=3:          
            df = pd.concat([df, pd.DataFrame([[row[0], row[1], row[2], row[3:]]], columns = ['YoutubeID', 'start', 'end', 'labels'])], ignore_index = True)

    file_name = os.path.basename(audioset_csv)
    # csv save
    if csv_save == True:
        df.to_csv(f"./csv_files/{os.path.splitext(file_name)[0]}.csv", mode = 'w', header = True, index = False) # csv file 저장
        #save dir : ./csv_files/filename ex) ./csv_files/eval_segments.csv

    # pickle save
    if pickle_save == True:
        with open(f"./csv_files/{os.path.splitext(file_name)[0]}.pickle", 'wb') as f:
            pickle.dump(df, f, pickle.HIGHEST_PROTOCOL)


    return df
#

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    ####################################
    ### --- change this argument--- ####
    parser.add_argument(
    "-c", "--class_labels", 
    default="/m/0brhx",   # <----------------------------------------------
    action="store",
    help="target class. ex) '/m/0brhx' ",
    )
    ### --- change this argument--- ####
    ####################################

    parser.add_argument(
    "-p", "--pickle_dir", 
    default="./csv_files/",
    action="store",
    help="pickle directory",
    )
    ####################################
    ### --- change this argument--- ####
    parser.add_argument(
    "-pn", "--pickle_name", 
    default="eval_segments.pickle", # <----------------------------------------------
    action="store",
    help="pickle name. ex) balanced_train_segments.pickle",
    )
    ### --- change this argument--- ####
    ####################################

    parser.add_argument(
    "-r", "--raw_audio_dir", 
    default="./download/raw_audio/",
    action="store",
    help="raw audiofile(to be sliced using ffmpeg) save directory. ex) ./download/raw_audio/",
    )

    parser.add_argument(
    "-d", "--download_dir", 
    default="./download/slice_audio/",
    action="store",
    help="directory for sliced audio",
    )

    parser.add_argument(
    "-m", "--mode", 
    default="download", # download or csv
    action="store",
    help="directory for sliced audio",
    )

    args = parser.parse_args()


    if args.mode == 'csv':
        read_AudioSet_csv(audioset_csv = './audioset_csv/unbalanced_train_segments.csv', csv_save = True, pickle_save = True)

        # audioset_csv = './audioset_csv/balanced_train_segments.csv' or 
        # audioset_csv = './audioset_csv/eval_segments.csv' or 
        # audioset_csv = './audioset_csv/unbalanced_train_segments.csv'


    else :
        csv_partition = os.path.splitext(args.pickle_name)[0]
        print(csv_partition)
        raw_audio_dir = args.raw_audio_dir


        with open(f"{args.pickle_dir}{args.pickle_name}","rb") as fr:
            df = pickle.load(fr)

        df_target = class_finder(df, args.class_labels)
        download_from_pd(df_target, args.download_dir, args.class_labels, csv_partition, raw_audio_dir)
