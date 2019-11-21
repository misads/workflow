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


class Combination(Base):
    def __init__(self, cfg):
        Base.__init__(self, cfg)
        self._combination = self.cfg['combination']
        self._axis = self._combination['axis']
        if 'one_folder_axis' in self._combination:
            self._one_folder_axis = self._combination['one_folder_axis']
        else:
            self._one_folder_axis = None

        self._tiles = self._combination['tiles']

        if 'gap' in self._combination:
            self._gap = self._combination['gap']
        else:
            self._gap = {'dw': 0, 'dh': 0}

        if 'image_size' in self._combination:
            self._image_size = self._combination['image_size']
            self._create_background()
        else:
            self._image_size = None

    def _create_background(self):
        nw, nh = self._tiles['w'], self._tiles['h']
        w1, h1 = self._image_size['w'], self._image_size['h']
        dw1, dh1 = self._gap['dw'], self._gap['dh']
        width = nw * w1 + (nw - 1) * dw1  # width for combination image
        height = nh * h1 + (nh - 1) * dh1

        self._back = np.ones((height, width, 3), np.uint8) * 255  # white background

    def _handle_image(self, input_path, output_path, compare_path=None):
        if not self._image_size:
            img = cv2.imread(input_path)
            h, w, _ = img.shape
            self._image_size = {'w': w, 'h': h}
            self._create_background()

        if self._back is None:
            self._create_background()

    def combine_xy(self):
        for f in self.folders:
            dir = self.folders[f]
            if not dir:
                continue
            dir.sort()
            self._create_background()

            for w in range(self._tiles['w']):
                for h in range(self._tiles['h']):
                    if self._axis == 'x':
                        i = h * self._tiles['w'] + w
                    else:
                        i = w * self._tiles['h'] + h
                    # dir = keylist[i]
                    input_path = self._get_input_abs_path(f, dir[i])
                    print(input_path + ' & ', end='')
                    img = cv2.imread(input_path)
                    w1, h1 = self._image_size['w'], self._image_size['h']
                    dw1, dh1 = self._gap['dw'], self._gap['dh']
                    self._back[h * (h1 + dh1):h * (h1 + dh1) + h1, w * (w1 + dw1):w * (w1 + dw1) + w1] = img

            print('\033[1;32m->\033[0m')
            checkdir(os.path.join(self._output_root, f))
            output_path = self._get_output_abs_path(f, 'combine.png')
            self.save_img(output_path, self._back)

    def combine(self):
        if self._one_folder_axis == 'xy':
            self.combine_xy()

            return
        folders = self.folders
        keylist = []
        for f in folders:
            if f:
                keylist.append(f)
        filelist = folders[keylist[0]]

        if self._axis == 'xy':
            pass
        elif self._axis == 'x':
            for file_index in range(len(filelist)):
                self._create_background()
                for h in range(self._tiles['h']):
                    for w in range(self._tiles['w']):
                        i = h * self._tiles['w'] + w
                        dir = keylist[i]
                        input_path = self._get_input_abs_path(dir, folders[dir][file_index])
                        print(input_path + ' & ', end='')
                        img = cv2.imread(input_path)
                        w1, h1 = self._image_size['w'], self._image_size['h']
                        dw1, dh1 = self._gap['dw'], self._gap['dh']
                        self._back[h * (h1 + dh1):h * (h1 + dh1) + h1, w * (w1 + dw1):w * (w1 + dw1) + w1] = img

                print('\033[1;32m->\033[0m')
                output_path = self._get_output_abs_path('', filelist[file_index])
                self.save_img(output_path, self._back)

        elif self._axis == 'y':
            for file_index in range(len(filelist)):
                self._create_background()
                for w in range(self._tiles['w']):
                    for h in range(self._tiles['h']):
                        i = w * self._tiles['h'] + h
                        dir = keylist[i]
                        input_path = self._get_input_abs_path(dir, folders[dir][file_index])
                        print(input_path + ' & ', end='')
                        img = cv2.imread(input_path)
                        w1, h1 = self._image_size['w'], self._image_size['h']
                        dw1, dh1 = self._gap['dw'], self._gap['dh']
                        self._back[h * (h1 + dh1):h * (h1 + dh1) + h1, w * (w1 + dw1):w * (w1 + dw1) + w1] = img

                print('\033[1;32m->\033[0m')
                output_path = self._get_output_abs_path('', filelist[file_index])
                self.save_img(output_path, self._back)


def combine(cfg):
    combine = Combination(cfg)
    combine.handle()
    combine.combine()


if __name__ == '__main__':
    args = parse_args()
    cfg = load_yml(args.ymlpath)
    combine(cfg)
