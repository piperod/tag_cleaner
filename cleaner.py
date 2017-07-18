
import os
import sys
import glob
import shutil
import numpy as np
import pandas as pd
import argparse
import json
from progress.bar import Bar


class FilterTags(object):

    def __init__(self, file_to_read, formatt="by_frame"):

        self.name = file_to_read
        self.tags = pd.read_json(file_to_read)
        self.formatt = formatt

    def from_frame_to_id(self):

        print("...converting from by_frame to by_id format....")

        if self.formatt == "by_frame":
            self.formatt = "by_id"
            by_id_tags = {}
            #bar = Bar('converting from frames to ids ', max=len(by_id_tags))
            for frame in self.tags:
                # bar.next()
                ids = [int(t['id']) for t in self.tags[frame]['tags']]
                for t in self.tags[frame]['tags']:
                    t['id'] = int(t['id'])
                    if t['id'] in ids:
                        try:
                            by_id_tags[t['id']]['tags'].append(t)
                        except:
                            by_id_tags[t['id']] = {}
                            by_id_tags[t['id']]['tags'] = []
                            by_id_tags[t['id']]['tags'].append(t)
            print(".... converted.....")
            self.tags = by_id_tags
        return

    def from_id_to_frame(self):

        print("... Converting from by_id to by_frame format....")

        if self.formatt == "by_id":
            self.formatt = "by_frame"
            by_frame_tags = {}
            #bar = Bar('converting from id to frames ', max=len(self.tags))
            for Id in self.tags:
                # bar.next()
                frames = [int(t['frame']) for t in self.tags[Id]['tags']]
                for t in self.tags[Id]['tags']:
                    if t['frame'] in frames:
                        try:
                            by_frame_tags[t['frame']]['tags'].append(t)
                        except:
                            by_frame_tags[t['frame']] = {}
                            by_frame_tags[t['frame']]['tags'] = []
                            by_frame_tags[t['frame']]['tags'].append(t)

            print(".... converted.....")

            self.tags = by_frame_tags

        return 

    def subsampling_by_window(self, subsampling_window):
        # converting from frame to id
        self.from_frame_to_id()
        # subsampling tags using the window:
        bar = Bar('....SubSampling Frames  by Window.... ', max=len(self.tags))

        for id_tag in self.tags:
            new_frames = []
            frames = [int(t['frame']) for t in self.tags[id_tag]['tags']]
            frames.sort()
            num_frames = int(len(frames) / subsampling_window)
            start = int(np.floor(subsampling_window / 2))

            if num_frames > 0:
                bar.next()

                for index in range(start, len(frames), subsampling_window):
                    new_frames.append(frames[index])

                self.tags[id_tag]['tags'] = [tag for tag in self.tags[
                    id_tag]['tags'] if tag['frame'] in new_frames]
        bar.finish()
        self.from_id_to_frame()

        return

    def filter_by_hamming (self, hamming=0):

        print("--------Deleting tags with hamming distance bigger than", hamming,"  -------")

        n_tags = {}

        for tag in self.tags:
            new_row = {}
            new_row['tags'] = [t for t in self.tags[tag]
                               ['tags'] if int(t['hamming']) <= hamming]

            if new_row['tags'] != []:
                n_tags[tag] = new_row

        self.tags = n_tags

        return 

    def filter_control_ids (self, ids):

        print("------Excluding tags:", ids, "-------")

        new_file = {}

        for tag in self.tags:
            new_row = {}
            new_row['tags'] = [t for t in self.tags[int(tag)]['tags'] if t[
                'id'] not in ids]
            if new_row['tags'] != []:
                new_file[int(tag)] = new_row

        self.tags = new_file

        return


    def filter_box(self,left,right,bottom, up):
        new_file = {}
        for tag in self.tags:
            new_row = {}
            new_row['tags'] = [t for t in self.tags[int(tag)]['tags']
                               if t['c'][0] > left and t['c'][0]<right]
            if new_row['tags'] != []:
                new_file[int(tag)] = new_row
        self.tags = new_file
        
        return





"""

This function converts tags from  { frame 1:[...id:....] , frame2:[...id:...] }
 
to {id1:[...frame:...], id2: [...frame:...]}


"""


def from_frame_to_id(by_frame_tags):
    by_id_tags = {}
    #bar = Bar('converting from frames to ids ', max=len(by_id_tags))
    for frame in by_frame_tags:
        # bar.next()
        ids = [int(t['id']) for t in by_frame_tags[frame]['tags']]
        for t in by_frame_tags[frame]['tags']:
            t['id'] = int(t['id'])
            if t['id'] in ids:
                try:
                    by_id_tags[t['id']]['tags'].append(t)
                except:
                    by_id_tags[t['id']] = {}
                    by_id_tags[t['id']]['tags'] = []
                    by_id_tags[t['id']]['tags'].append(t)

    # bar.finish()
    return by_id_tags


"""

This function converts tags from  {id1:[...frame:...], id2: [...frame:...]}  
to { frame 1:[...id:....] , frame2:[...id:...] }

"""


def from_id_to_frame(by_id_tags):
    by_frame_tags = {}
    #bar = Bar('converting from id to frames ', max=len(by_id_tags))
    for Id in by_id_tags:
        # bar.next()
        frames = [int(t['frame']) for t in by_id_tags[Id]['tags']]
        for t in by_id_tags[Id]['tags']:
            if t['frame'] in frames:
                try:
                    by_frame_tags[t['frame']]['tags'].append(t)
                except:
                    by_frame_tags[t['frame']] = {}
                    by_frame_tags[t['frame']]['tags'] = []
                    by_frame_tags[t['frame']]['tags'].append(t)
    # bar.finish()
    return by_frame_tags


def subsampling_tags(tags, subsampling_window):

    # converting from frame to id
    frame_tags = from_frame_to_id(tags)
    # subsampling tags using the window:
    bar = Bar('....SubSampling frames.... ', max=len(frame_tags))
    for id_tag in frame_tags:
        new_frames = []
        frames = [int(t['frame']) for t in frame_tags[id_tag]['tags']]
        frames.sort()

        num_frames = int(len(frames) / subsampling_window)
        start = int(np.floor(subsampling_window / 2))

        if num_frames > 0:
            bar.next()
            for index in range(start, len(frames), subsampling_window):
                new_frames.append(frames[index])
            frame_tags[id_tag]['tags'] = [tag for tag in frame_tags[
                id_tag]['tags'] if tag['frame'] in new_frames]
    bar.finish()
    new_tags = from_id_to_frame(frame_tags)

    return new_tags


def main(args):
    # Change the name from tag to frame

    # ids = exclude ids
    jsonfile = args['input']
    print("--------processing file-------")
    # Cleaning the json file by ids
    tags = pd.read_json(jsonfile)
    new_file = {}
    # Filtering with hamming bigger than 0
    if args['hamming'] == None:
        print("--------Deleting tags with hamming distance bigger than 0-------")
        n_tags = {}
        for tag in tags:
            new_row = {}
            new_row['tags'] = [t for t in tags[tag]
                               ['tags'] if int(t['hamming']) < 1]
            if new_row['tags'] != []:
                n_tags[tag] = new_row
    else:
        n_tags = tags
    if args['ids'] != None:
        idds = map(int, args['ids'].strip('[]').split(','))
        ids = [i for i in idds]
        print("------Excluding tags:", ids, "-------")
    else:
        ids = []
    if args['window'] != None:
        subsampling_window = int(args['window'])
        new_tags = subsampling_tags(n_tags, subsampling_window)
    else:
        new_tags = n_tags

    bar = Bar('Filtering  Ids ', max=len(new_tags))
    for tag in new_tags:
        bar.next()
        new_row = {}
        new_row['tags'] = [t for t in tags[int(tag)]['tags'] if t[
            'id'] not in ids]
        if new_row['tags'] != []:
            new_file[int(tag)] = new_row

    bar.finish()

    print("-------saving new file------------")

    with open(args['output'], 'w') as outfile:

        json.dump(new_file, outfile)


if __name__ == '__main__':

    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--input", required=True, help="Input file")
    ap.add_argument("-o", "--output", required=True, help="Output file")
    ap.add_argument("-ids", "--ids", required=False,
                    help="List of ids to avoid ej [1602,1603,1604]")
    ap.add_argument("-hm", "--hamming", required=False,
                    help="Hamming distance tolerance by default cleans hamming bigger than 0")
    ap.add_argument("-window", "--window", required=False,
                    help="How many frames (window) to ignore on each id")
    args = vars(ap.parse_args())

    main(args)
