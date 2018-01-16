#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK

import csv

import os
from PIL import Image

source_dir = '/vagrant/exports/sykes/'
destination_dir = '/vagrant/lib/default/src/ckanext-nhm/ckanext/nhm/files'
folder = u'sykes'
thumbnail_size = 128, 128
image_size = 800, 800


def main():
    ''' '''
    with open('/vagrant/sykes.csv', u'wb') as csvfile:

        csvfile_writer = csv.writer(csvfile, delimiter=u',')

        # Write header
        csvfile_writer.writerow([u'Catalogue key', u'Image', u'Thumbnail'])

        for f in os.listdir(source_dir):

            cat_key = get_cat_key_from_filename(f)
            thumbnail_name = u'thumb_' + f

            thumbnail = os.path.join(destination_dir, folder, thumbnail_name)
            image = os.path.join(destination_dir, folder, f)

            im = Image.open(os.path.join(source_dir, f))
            im.thumbnail(thumbnail_size, Image.ANTIALIAS)
            im.save(thumbnail, u'JPEG')

            im = Image.open(os.path.join(source_dir, f))
            im.thumbnail(image_size, Image.ANTIALIAS)
            im.save(image, u'JPEG')

            thumbnail_src = '/' + os.path.join(folder, thumbnail_name)
            image_src = '/' + os.path.join(folder, f)

            csvfile_writer.writerow([cat_key, image_src, thumbnail_src])


def get_cat_key_from_filename(filename):
    '''

    :param filename: 

    '''
    return filename.replace(u'NHM-UK_L_', u'').split(u'-')[0].split(u'_')[0]


def get_cat_keys_from_file():
    ''' '''
    cat_keys = set()
    subdirs = [x[0] for x in os.walk(source_dir)]
    for subdir in subdirs:
        print subdir
        files = os.walk(subdir).next()[2]
        if (len(files) > 0):
            for file in files:

                print file

                cat_key = file.replace(u'NHM-UK_L_', u'').split(u'-')[0].split(u'_')[0]
                cat_keys.add(cat_key)

    for cat_key in sorted(cat_keys):
        print cat_key


if __name__ == u'__main__':
    main()

