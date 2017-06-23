
import os
import sys
import glob
import shutil
import numpy as np
import argparse
import json
from progress.bar import Bar

def maping_ids(tags,pfrm):

    mapids = {}

    new_tags = []

    for tag in tags:
        
        ids = [ int(t['id']) for t in tags[tag]['tags']]


        for i in np.unique(ids):

            try:

                mapids[i].append(int(tag))

            except: 

                mapids[i]=[]
                mapids[i].append(int(tag))

   
    for m in  mapids.keys():
       
        
        mapids[m].sort()
        mapidsort = mapids[m]

        np.union1d(new_tags,[mapidsort[0]])

        temp_tags= [int(mapidsort[i+1]) for i in range(len(mapidsort)-1) if mapidsort[i+1]-mapidsort[i]>pfrm]
        new_tags = np.union1d(new_tags, temp_tags)
    print(new_tags)
    return new_tags

        
def main(args):

    jsonfile = args['input']

    print("--------processing file-------")

    # Cleaning the json file by ids
    with open(jsonfile) as json_data:

        tags = json.load(json_data)
        new_file = {}

        if args['ids'] != None:

            idds = map(int, args['ids'].strip('[]').split(','))
            ids = [i for i in idds]
            print("------Excluding tags:", ids, "-------")

        else:

            ids = []

        if args['pfrm'] != None:

            pfrm = int(args['pfrm'])

            new_tags = maping_ids(tags,pfrm)
        else:

            new_tags = tags

       

        bar = Bar('Deleting Ids ', max=len(tags))
        
        for tag in new_tags:
            

            new_row = {}
            new_row['tags'] = [t for t in tags[str(int(tag))]['tags'] if t['id'] not in ids]

            if new_row['tags'] != []:
                new_file[str(int(tag))] = new_row
                bar.next()

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
    ap.add_argument("-hm", "--hamming",required = False, help="Hamming distance tolerance")
    ap.add_argument("-pfrm","--pfrm", required = False, help = "How many frames to avoid on each id")
    args = vars(ap.parse_args())

    main(args)
