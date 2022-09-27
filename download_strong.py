
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


def audio_cut_10s(file_name, start, download_dir, raw_audio_dir):
    """
    Args: 
        file_name : audio file to be sliced
        start : audio start time
        save_dir : save directory for sliced audio file. default : ./download/slice_audio/
        csv_partition : balanced_train_segments or eval_segments or unbalanced_train_segments  ex.) balanced_train_segments
    """
    start_rm_dot = start.replace('.', '') # remove '.'

    # youtube_id = file_name[:file_name.index('_')]
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    file_name_only = os.path.splitext(file_name)[0] # not contain extension

    command = (f'ffmpeg -y -ss {start} -t 10 -i {raw_audio_dir}{file_name} {download_dir}/{file_name_only}_{start_rm_dot}.wav')    
    subprocess.call(command,shell=True,stdout=None)
    # ffmpeg -ss 0 -t 10 -i ./raw_audio/-0DdlOuIFUI.wav hhj3.wav

    strong_file = f'{download_dir}/{file_name_only}_{start_rm_dot}.wav'

    return strong_file


def target_class_finder(tsv_dir, target_class = None):
    """
    Args:
        tsv_dir : directory of tsv file given by AudioSet. ex.) './audioset_csv/audioset_eval_strong.tsv'
        target_class : target machine ID(MID) of sound event class ex.) '/m/09x0r'
    Return:
        df : Dataframe for the clips and segments containing only the target class.
        series : Series for the clips containing only the target class.
    """
    df = pd.read_csv(tsv_dir, sep = '\t')

    if target_class is not None:
        df = df.where(df['label'] == target_class).dropna() # dataframe for the clips and segments containing only the target class.

    series = df.loc[:, ['segment_id']] # Series for the clips containing only the target class.
    series = series.drop_duplicates()

    return df, series


def split_youtubeid_starttimes(series):

    """
    Args:
        series : Series for the clips containing only the target class. (return of target_class_finder function)
    Return:
        youtube_id_list : list of Youtube ID extracted from the series
        start_time_list : list of start time converted to use in ffmpeg
    """

    seg_id = series.values.squeeze() # type of seg_id : numpy

    seg_id_list = seg_id.tolist()
    youtube_id_list = []
    start_time_list = []

    for segment_id in seg_id:
        # print(segment_id)

        # find youtube id from segment_id
        idx = segment_id.rfind('_') # find the highest index of '_'
        youtube_id = segment_id[:idx]
        start_time = segment_id[idx+1:]

        youtube_id_list.append(youtube_id)
        start_time_list.append(start_time)
    # print(start_time_list, len(start_time_list))
        
    # rewrite 'start time' to use in ffmpeg
    for i, start in enumerate(start_time_list):

        # transform '0' -> '0000'
        if start == '0':
            start_time_list[i] = '0000'

        # insert dot('.') to use in ffmpeg
        start_time_list[i] = start_time_list[i][:-3] + '.' + start_time_list[i][-3:]

    return youtube_id_list, start_time_list, seg_id_list


def mid_to_display_name(mid_to_display_dir = './audioset_csv/mid_to_display_name.tsv', target_class = ''):
    """
    Args: 
        target_class : mid columns at 'class_labels_indices.csv' file . ex) '/m/09x0r'
    
    return:
        display_name : display name columns at 'class_labels_indices.csv' file. ex) Speech
    """
    df = df = pd.read_csv(mid_to_display_dir, sep = '\t', header = 0, names = ['mid', 'display_name'])

    for i in range(len(df.loc[:])):
        if (df.iloc[i, 0] == target_class):
            display_name = df.iloc[i, 1]

    if display_name == None :
        print("error : check class label")

    return display_name.replace(" ", "_")

def is_overlap_a_b(a_segment, b_segment):
    # case 1. start point of a_segment is located between b_segment
    if (b_segment[0] <= a_segment[0]) & (a_segment[0] <= b_segment[1]):
        # print('1 case')
        return True

    # case 2. a_segment contains b_segment
    elif (a_segment[0] <= b_segment[0]) & (b_segment[1] <= a_segment[1]):
        # print('2 case')
        return True

    # case3. end point of a_segment is located between b_segment
    elif (b_segment[0] <= a_segment[1]) & (a_segment[1] <= b_segment[1]):
        # print('3 case')
        return True

    else :
        # print("non overlap")
        return False

def overlap_append(df_seg):

    df_seg = df_seg.reset_index(drop=True)  # reset index

    overlap = []
    overlap_class = []
    overlap_class_display_name = []

    label_display_name_list = []

    for i in range(len(df_seg)):
        # search overlap between a_segment and b_segment
        a_segment = df_seg.iloc[i]['start_time_seconds':'end_time_seconds'].values # Dataframe -> Numpy

        label_display_name = mid_to_display_name(target_class = df_seg.iloc[i]['label'])
        overlap_class_tmp = []
        overlap_class_display_name_tmp = []
        overlap_cnt = 0

        for j in range(len(df_seg)):

            if i != j:
                b_segment = df_seg.iloc[j]['start_time_seconds':'end_time_seconds'].values # Dataframe -> Numpy
                # print(b_segment)

                # there is overlap
                if is_overlap_a_b(a_segment, b_segment):

                    mid = df_seg.iloc[j]['label']
                    display_name = mid_to_display_name(target_class = mid)

                    overlap_class_tmp.append(mid)     # if overlap, append label name
                    overlap_class_display_name_tmp.append(display_name)
                    overlap_cnt += 1
                    # print(overlap_cnt)

        if overlap_cnt >= 1:
            overlap.append(True)
        
        else:
            overlap.append(False)

        overlap_class.append(overlap_class_tmp)
        overlap_class_display_name.append(overlap_class_display_name_tmp)
        label_display_name_list.append(label_display_name)

    raw_data = {
        'label_display_name' : label_display_name_list,
        'overlap' : overlap,
        'overlap_class' : overlap_class,
        'overlap_class_display_name' : overlap_class_display_name
    }
    df_seg = pd.concat([df_seg, pd.DataFrame(raw_data)], axis=1, join = 'inner')

    return df_seg

def target_class_pusher(mid_to_display_dir = './audioset_csv/mid_to_display_name.tsv'):
    target_class_list = []
    df_target_class = pd.read_csv(mid_to_display_dir, sep = '\t', header = 0, names = ['mid', 'display_name'])

    for i in range(len(df_target_class)):
        target_class_list.append(df_target_class.iloc[i][0])

    return target_class_list


def download_df(tsv_dir, target_class, download_dir):

    if 'train' in tsv_dir:
        partition = 'train'
    else: # 'eval in tsv_dir
        partition = 'eval'

    _, series = target_class_finder(tsv_dir, target_class) # set DataFraim contains only target class datas
    df_origin, _ = target_class_finder(tsv_dir) # set DataFraim contains all datas

    

    if target_class is not None:
        target_class_display_name = mid_to_display_name(target_class = target_class)
        download_dir = f'{download_dir}target/{partition}/{target_class_display_name}'
    else:
        download_dir = f'{download_dir}all/{partition}'

    youtube_id_list, start_time_list, seg_id_list = split_youtubeid_starttimes(series)

    for i in tqdm(range(len(youtube_id_list))):
        youtube_id = youtube_id_list[i]
        start = start_time_list[i]
        segment_id = seg_id_list[i] # filename = segment_id
        print(youtube_id)

        file_name = download(youtube_id, ext = 'wav', raw_audio_dir = raw_audio_dir)

        if os.path.isfile(f'{raw_audio_dir}{file_name}'): # audio download check

            strong_file = audio_cut_10s(file_name, start, download_dir, raw_audio_dir)
            csv_filename = os.path.splitext(strong_file)[0]

            df_seg = overlap_append(df_seg = df_origin.loc[df_origin['segment_id'] == segment_id])
            df_seg.to_csv(f"{csv_filename}.csv", mode = 'w', header = True)


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
    "-t", "--tsv_dir",  # './audioset_csv/audioset_eval_strong.tsv' or './audioset_csv/audioset_train_strong.tsv' <----------------------------------------------
    default='./audioset_csv/audioset_eval_strong.tsv',
    action="store",
    help="pickle directory",
    )

    parser.add_argument(
    "-r", "--raw_audio_dir", 
    default="./download/raw_audio/",
    action="store",
    help="raw audiofile(to be sliced using ffmpeg) save directory. ex) ./download/raw_audio/",
    )

    parser.add_argument(
    "-d", "--download_dir", 
    default="./download/strong_slice_audio/",
    action="store",
    help="directory for sliced audio",
    )

    parser.add_argument(
    "-mid", "--mid", 
    default="./audioset_csv/mid_to_display_name.tsv", # convert mid to display name
    action="store",
    help="convert mid to display name",
    )

    parser.add_argument(
    "-m", "--mode", 
    default="target", # "target" or "all"
    action="store",
    help="download only target class vs. all class",
    )


    args = parser.parse_args()

    target_class = args.class_labels # "/m/0brhx"
    tsv_dir = args.tsv_dir
    mid_to_display_dir = args.mid

    raw_audio_dir = args.raw_audio_dir
    download_dir = args.download_dir

    mode = args.mode # target or all



    if mode == 'target':
        print('target')
        # input : target_class, tsv_dir, download_dir

        download_df(tsv_dir, target_class, download_dir)


    elif mode == 'all':
        print('all')

        download_df(tsv_dir, target_class = None, download_dir = download_dir)





