# encoding=utf-8

import numpy as np
import os
import argparse
import cv2
import numpy as np

from src.base import Base
from src.load_config import load_yml
from src.misc_utils import checkdir, attach_file_suffix, safe_key, args


class Combination(Base):
    def __init__(self, cfg):
        Base.__init__(self, cfg)
        self.mode = 'n_to_1'

        self._combination = self.cfg['combine']
        self._axis = self._combination['priority_axis']
        self._one_folder_axis = safe_key(self._combination, 'one_folder_in_axis')

        self._tiles = safe_key(self._combination, 'tiles')
        self._combine_size = safe_key(self._combination, 'combine_size')

        self._gap = safe_key(self._combination, 'gap', {'dw': 0, 'dh': 0})

        if 'image_size' in self._combination:
            self._image_size = self._combination['image_size']
            self._create_background()
        else:
            self._image_size = None

    def _create_background(self):
        if self._tiles is None:
            return

        if self._combine_size is not None:
            # overlap mode
            height, width = self._combine_size['h'], self._combine_size['w']
            self._back = np.zeros((height, width, 3))  # white background
            self._cont = np.zeros((height, width))
            return

        nw, nh = self._tiles['x'], self._tiles['y']
        w1, h1 = self._image_size['w'], self._image_size['h']
        dw1, dh1 = self._gap['dw'], self._gap['dh']
        width = nw * w1 + (nw - 1) * dw1  # width for combination image
        height = nh * h1 + (nh - 1) * dh1

        self._back = np.ones((height, width, 3), np.uint8) * 255  # white background

    def _handle_image(self, input_path, output_path, compare_path=None, abs_out_dir=None, filename=None):
        img = cv2.imread(input_path)
        if self._image_size is None:
            h, w, _ = img.shape
            self._image_size = {'w': w, 'h': h}
        self._create_background()

    def _combine_one_folder_in_xy(self):
        for f in self.folders:
            dir = self.folders[f]
            if not dir:
                continue
            dir.sort()
            self._create_background()

            if self._combine_size is not None:
                width, height = self._combine_size['w'], self._combine_size['h']
                # overlap
                base_name = dir[0].split('.')[0][:-10]
                suffix = dir[0].split('.')[-1]
                px, py = self._tiles['x'], self._tiles['y']
                channel = 3
                for i in range(py):
                    for j in range(px):
                        file_name = '%s_%04d_%04d.%s' % (base_name, i, j, suffix)
                        input_path = self._get_input_abs_path(f, file_name)
                        print(input_path + ' & ', end='')
                        img = cv2.imread(input_path)
                        patch_h, patch_w, channel = img.shape
                        stride_x = (width - patch_w) // (px - 1)
                        stride_y = (height - patch_h) // (py - 1)

                        if i < py - 1:
                            y = i * stride_y
                        else:
                            y = height - patch_h  # the last patch not following the stride
                        if j < px - 1:
                            x = j * stride_x
                        else:
                            x = width - patch_w

                        self._back[y:y + patch_h, x:x + patch_w] += img
                        self._cont[y:y + patch_h, x:x + patch_w] += 1

                for c in range(channel):
                    self._back[:, :, c] /= self._cont

            else:
                # not overlap
                for w in range(self._tiles['x']):
                    for h in range(self._tiles['y']):
                        if self._axis == 'x':
                            i = h * self._tiles['x'] + w
                        else:
                            i = w * self._tiles['y'] + h
                        # dir = keylist[i]
                        input_path = self._get_input_abs_path(f, dir[i])
                        print(input_path + ' & ', end='')
                        img = cv2.imread(input_path)
                        w1, h1 = self._image_size['w'], self._image_size['h']
                        dw1, dh1 = self._gap['dw'], self._gap['dh']
                        if img.shape[0] != h1 or img.shape[1] != w1:
                            img = cv2.resize(img, (w1, h1))
                        self._back[h * (h1 + dh1):h * (h1 + dh1) + h1, w * (w1 + dw1):w * (w1 + dw1) + w1] = img

            print('\033[1;32m->\033[0m')
            savename = f if '.' in f else f + '.png'
            if self.mode == 'n_to_n':
                checkdir(os.path.join(self._output_root, f))
                output_path = self._get_output_abs_path(f, savename)
            else:
                output_path = self._get_output_abs_path('', savename)

            os.makedirs(self._get_output_abs_path('','.'), exist_ok=True)
            self.save_img(output_path, self._back)

    def _handle_dict(self, dir_dict, len_x, len_y):
        if self._one_folder_axis == 'xy':
            self._combine_one_folder_in_xy()

            return

        folder_list = [folder for folder in dir_dict]

        if self._one_folder_axis == 'x':
            if self._tiles is None:
                self._tiles = {'x': len_y, 'y': len_x}
                self._create_background()
            for h in range(len_x):
                folder = folder_list[h]
                file_list = dir_dict[folder]
                for w in range(len_y):
                    file = file_list[w]
                    input_path = self._get_input_abs_path(folder, file)
                    print(input_path + ' & ', end='')
                    img = cv2.imread(input_path)
                    w1, h1 = self._image_size['w'], self._image_size['h']
                    dw1, dh1 = self._gap['dw'], self._gap['dh']
                    if img.shape[0] != h1 or img.shape[1] != w1:
                        img = cv2.resize(img, (w1, h1))
                    self._back[h * (h1 + dh1):h * (h1 + dh1) + h1, w * (w1 + dw1):w * (w1 + dw1) + w1] = img

            print('\033[1;32m->\033[0m')
            output_path = self._get_output_abs_path('', 'combine.png')
            self.save_img(output_path, self._back)

        elif self._one_folder_axis == 'y':
            if self._tiles is None:
                print(len_x)
                self._tiles = {'x': len_x, 'y': len_y}
                self._create_background()
            for w in range(len_x):
                folder = folder_list[w]
                file_list = dir_dict[folder]
                for h in range(len_y):
                    file = file_list[h]
                    input_path = self._get_input_abs_path(folder, file)
                    print(input_path + ' & ', end='')
                    img = cv2.imread(input_path)
                    w1, h1 = self._image_size['w'], self._image_size['h']
                    dw1, dh1 = self._gap['dw'], self._gap['dh']
                    if img.shape[0] != h1 or img.shape[1] != w1:
                        img = cv2.resize(img, (w1, h1))
                    self._back[h * (h1 + dh1):h * (h1 + dh1) + h1, w * (w1 + dw1):w * (w1 + dw1) + w1] = img

            print('\033[1;32m->\033[0m')
            output_path = self._get_output_abs_path('', 'combine.png')
            self.save_img(output_path, self._back)

        # if self._axis == 'xy':
        #     pass
        # elif self._axis == 'x':
        #     for file_index in range(len(filelist)):
        #         self._create_background()
        #         for h in range(self._tiles['y']):
        #             for w in range(self._tiles['x']):
        #                 i = h * self._tiles['x'] + w
        #                 dir = keylist[i]
        #                 input_path = self._get_input_abs_path(dir, folders[dir][file_index])
        #                 print(input_path + ' & ', end='')
        #                 img = cv2.imread(input_path)
        #                 w1, h1 = self._image_size['w'], self._image_size['h']
        #                 dw1, dh1 = self._gap['dw'], self._gap['dh']
        #                 if img.shape[0] != h1 or img.shape[1] != w1:
        #                     img = cv2.resize(img, (w1, h1))
        #                 self._back[h * (h1 + dh1):h * (h1 + dh1) + h1, w * (w1 + dw1):w * (w1 + dw1) + w1] = img
        #
        #         print('\033[1;32m->\033[0m')
        #         output_path = self._get_output_abs_path('', filelist[file_index])
        #         self.save_img(output_path, self._back)
        #
        # elif self._axis == 'y':
        #     for file_index in range(len(filelist)):
        #         self._create_background()
        #         for w in range(self._tiles['x']):
        #             for h in range(self._tiles['y']):
        #                 i = w * self._tiles['y'] + h
        #                 dir = keylist[i]
        #                 input_path = self._get_input_abs_path(dir, folders[dir][file_index])
        #                 print(input_path + ' & ', end='')
        #                 img = cv2.imread(input_path)
        #                 w1, h1 = self._image_size['w'], self._image_size['h']
        #                 dw1, dh1 = self._gap['dw'], self._gap['dh']
        #                 if img.shape[0] != h1 or img.shape[1] != w1:
        #                     img = cv2.resize(img, (w1, h1))
        #                 self._back[h * (h1 + dh1):h * (h1 + dh1) + h1, w * (w1 + dw1):w * (w1 + dw1) + w1] = img
        #
        #         print('\033[1;32m->\033[0m')
        #         output_path = self._get_output_abs_path('', filelist[file_index])
        #         self.save_img(output_path, self._back)


def combine(cfg):
    combine = Combination(cfg)
    combine.handle()


if __name__ == '__main__':
    cfg = load_yml(args.ymlpath)
    combine(cfg)
