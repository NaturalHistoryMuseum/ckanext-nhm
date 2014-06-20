#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""

import sys
import os
import re
import os, sys
from PIL import Image
import csv

source_dir = '/vagrant/exports/sykes/'
destination_dir = '/vagrant/lib/default/src/ckanext-nhm/ckanext/nhm/files'
folder = 'sykes'
thumbnail_size = 128, 128
image_size = 800, 800

def main():

    with open('/vagrant/sykes.csv', 'wb') as csvfile:

        csvfile_writer = csv.writer(csvfile, delimiter=',')

        # Write header
        csvfile_writer.writerow(['Catalogue key', 'Image', 'Thumbnail'])

        for f in os.listdir(source_dir):

            cat_key = get_cat_key_from_filename(f)
            thumbnail_name = 'thumb_' + f

            thumbnail = os.path.join(destination_dir, folder, thumbnail_name)
            image = os.path.join(destination_dir, folder, f)

            im = Image.open(os.path.join(source_dir, f))
            im.thumbnail(thumbnail_size, Image.ANTIALIAS)
            im.save(thumbnail, "JPEG")

            im = Image.open(os.path.join(source_dir, f))
            im.thumbnail(image_size, Image.ANTIALIAS)
            im.save(image, "JPEG")

            thumbnail_src = '/' + os.path.join(folder, thumbnail_name)
            image_src = '/' + os.path.join(folder, f)

            csvfile_writer.writerow([cat_key, image_src, thumbnail_src])



def get_cat_key_from_filename(filename):
    return filename.replace('NHM-UK_L_', '').split('-')[0].split('_')[0]


def get_cat_keys_from_file():
    cat_keys = set()
    subdirs = [x[0] for x in os.walk(source_dir)]
    for subdir in subdirs:
        print subdir
        files = os.walk(subdir).next()[2]
        if (len(files) > 0):
            for file in files:

                print file

                cat_key = file.replace('NHM-UK_L_', '').split('-')[0].split('_')[0]
                cat_keys.add(cat_key)

    for cat_key in sorted(cat_keys):
        print cat_key


if __name__ == '__main__':
    main()

