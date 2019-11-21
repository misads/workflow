# encoding=utf-8

import numpy as np
import os
import argparse
import cv2
import numpy as np

from src.base import Base
from src.load_config import load_yml
from src.misc_utils import checkdir, attach_file_suffix


def parse_args():
    parser = argparse.ArgumentParser(description='resize images.')

    parser.add_argument('ymlpath')

    args = parser.parse_args()

    return args


class Split(Base):
    def __init__(self, cfg):
        Base.__init__(self, cfg)
        self.mode = '1_to_n'  # want all splits in one folder? try setting mode to `1_to_1`
        split = self.cfg['split']
        self._tiles = split['tiles']

    def _handle_image(self, input_path, output_path, compare_path=None, abs_out_dir=None, filename=None):
        img = cv2.imread(input_path)
        height, width, _ = img.shape
        h, w = self._tiles['h'], self._tiles['w']
        h1 = int(height / h)
        w1 = int(width / w)

        for j in range(h):
            for i in range(w):
                img2 = img[j * h1:j * h1 + h1, i * w1:i * w1 + w1]  # (y1,y2):(x1,x2)

                save_path = attach_file_suffix(output_path, '_%02d_%02d' % (j, i))
                print(save_path)

                cv2.imwrite(save_path, img2)


def split(cfg):
    split = Split(cfg)
    split.handle()


if __name__ == '__main__':
    args = parse_args()
    cfg = load_yml(args.ymlpath)
    split(cfg)
