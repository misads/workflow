# encoding=utf-8

import numpy as np
import os
import argparse
import cv2

from base import Base
from load_config import load_yml
from misc_utils import checkdir


def parse_args():

    parser = argparse.ArgumentParser(description='resize images.')

    parser.add_argument('ymlpath')

    args = parser.parse_args()

    return args


class Transform(Base):
    def __init__(self, cfg):
        Base.__init__(self, cfg)

    def _handle_image(self, input_path, output_path, compare_path=None):
        img = cv2.imread(input_path)

        cv2.imwrite(output_path, img)



# def transform(cfg):
#     print(cfg)
#
#     if not '__init__' in cfg:
#         raise Exception('Incomplete yaml file.')
#     init = cfg['__init__']
#     root_path = init['input']
#     output_dir = init['output']
#
#     auto = cfg['folder_path'] == 'auto'
#     if auto:
#         paths = os.listdir(root_path)
#         paths.sort()
#     else:
#         paths = cfg['folder']
#
#     is_input_dir = os.path.isdir(root_path)
#
#     if is_input_dir:
#         checkdir(root_path)
#
#
#
#     else: # only 1 image file
#         pass

if __name__ == '__main__':
    args = parse_args()
    cfg = load_yml(args.ymlpath)
    trans = Transform(cfg)
    trans.handle()
    #print(trans.folders)
