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


class Crop(Base):
    def __init__(self, cfg):
        Base.__init__(self, cfg)
        crop = self.cfg['crop']
        self._tiles = crop['tiles']

    # 给的时候可以都给 各取所需
    def _handle_image(self, input_path, output_path, compare_path=None, input_folder=None, filename=None):
        pass

    def _handle_image(self, input_path, output_path, compare_path=None):
        img = cv2.imread(input_path)
        height, width, _ = img.shape
        h, w = self._tiles['h'], self._tiles['w']
        h1 = int(height / h)
        w1 = int(width / w)

        for j in range(h):
            for i in range(w):
                img2 = img[j * h1:j * h1 + h1, i * w1:i * w1 + w1]  # (y1,y2):(x1,x2)

                save_path = attach_file_suffix(output_path, '%d_%d' % (j, i))
                print(save_path)

                cv2.imwrite(save_path, img2)


def crop(cfg):
    crop = Crop(cfg)
    crop.handle()


if __name__ == '__main__':
    args = parse_args()
    cfg = load_yml(args.ymlpath)
    crop(cfg)
