# encoding=utf-8

import numpy as np
import os
import argparse
import cv2

def parse_args():

    parser = argparse.ArgumentParser(description='resize images.')

    parser.add_argument('path')

    parser.add_argument('--width', '-w', default=256, type=int, help='')
    parser.add_argument('--height', '-e', default=256, type=int, help='')

    parser.add_argument('--output', '-o', default='img_resize', type=str, help='output folder or filepath')

    args = parser.parse_args()

    return args

if __name__ == '__main__':
    args = parse_args()
    path = args.path
    output = args.output
    width = args.width
    height = args.height
    if not os.path.exists(path):
        raise(IOError, 'path not exists.')

    isdir = os.path.isdir(path)
    if isdir:
        if not os.path.exists(output):
            os.mkdir(output)
        l = os.listdir(path)
        l.sort()
        for f in l:
            print('handling %s' % os.path.join(path, f))
            img = cv2.imread(os.path.join(path, f))
            img_resize = cv2.resize(img, (width, height))
            cv2.imwrite(os.path.join(output, f), img_resize)
            del img
            del img_resize
    else:
        print('handling %s' % path)
        img = cv2.imread(path)
        img_resize = cv2.resize(img, (width, height))
        cv2.imwrite(output, img_resize)
        del img
        del img_resize

