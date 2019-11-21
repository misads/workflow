# encoding=utf-8

import numpy as np
import os
import argparse
import cv2
import numpy as np

from base import Base
from load_config import load_yml
from misc_utils import checkdir, attach_file_suffix


def parse_args():
    parser = argparse.ArgumentParser(description='resize images.')

    parser.add_argument('ymlpath')

    args = parser.parse_args()

    return args


class Submit(Base):
    def __init__(self, cfg):
        Base.__init__(self, cfg)

    def _handle_image(self, input_path, output_path, compare_path=None):
        img = cv2.imread(input_path, 0)
        img[img < 200] = 0
        img[img >= 200] = 255
        t = output_path.split('/')
        save = self._get_output_abs_path('', t[1] + '.tiff')
        cv2.imwrite(save, img)
        print(save)


if __name__ == '__main__':
    args = parse_args()
    cfg = load_yml(args.ymlpath)
    submit = Submit(cfg)
    submit.handle()
