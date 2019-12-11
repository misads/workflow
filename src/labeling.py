# encoding=utf-8
import pdb

import numpy as np
import os
import argparse
import cv2
import numpy as np

from src.base import Base
from src.load_config import load_yml
from src.misc_utils import attach_file_suffix, binaryzation, args, random_crop


class Labeling(Base):
    def __init__(self, cfg):
        Base.__init__(self, cfg)
        self.mode = '1_to_1' if args.mode == 'default' else args.mode

    def _handle_image(self, input_path, output_path, compare_path=None, abs_out_dir=None, filename=None):
        img = cv2.imread(input_path)
        # img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img[img >= 122] = 255
        img[img < 122] = 1
        img[img == 255] = 0
        # BGR set all G and R to 0
        img[:, :, 1] = 0
        img[:, :, 2] = 0
        cv2.imwrite(output_path, img)
        # mask = np.unpackbits(np.array(img), axis=2)[:, :, -1:-2:-1]
        # mask= mask *255
        # cv2.imshow("vis", mask)
        # cv2.waitKey(0)
        #pdb.set_trace()



def labeling(cfg):
    label = Labeling(cfg)
    label.handle()


if __name__ == '__main__':
    cfg = load_yml(args.ymlpath)
    labeling(cfg)
