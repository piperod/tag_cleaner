
import os
import glob
import shutil
import numpy as np
import argparse
import json


def main(args):

    jsonfile = args['input']

    print("________processing file________")
    # Cleaning the json file by ids
    with open(jsonfile) as json_data:
        tags = json.load(json_data)

        idds=  map(int, args['ids'].strip('[]').split(','))
        
        ids =[i for i in idds]

        print("------Excluding tags:", ids)
        new_file = {}
        for tag in tags:
            new_row = {}
            new_row['tags'] = [t for t in tags[tag]['tags'] if t['id'] not in ids]
            new_file[tag] = new_row

    print("________saving new file__________")

    with open(args['output'], 'w') as outfile:

        json.dump(new_file, outfile)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--input", required=True, help="Input file")
    ap.add_argument("-o", "--output", required=True, help="Output file")
    ap.add_argument("-ids", "--ids", required=True,
                    help="List of ids to avoid")
    args = vars(ap.parse_args())
    main(args)
