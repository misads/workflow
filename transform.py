# encoding=utf-8

import numpy as np
import os
import argparse
import cv2
import numpy as np

from base import Base
from load_config import load_yml
from misc_utils import attach_file_suffix


def parse_args():
    parser = argparse.ArgumentParser(description='resize images.')

    parser.add_argument('ymlpath')

    args = parser.parse_args()

    return args


class Transform(Base):
    def __init__(self, cfg):
        Base.__init__(self, cfg)

    def _random_crop(self, img, w, h):
        height, width, _ = img.shape
        x = np.random.randint(0, width - w)
        y = np.random.randint(0, height - h)
        patch = img[y:y + h, x:x + w]
        return patch

    def _handle_image(self, input_path, output_path, compare_path=None):
        img = cv2.imread(input_path)
        cfg = self.cfg
        save = True
        if 'resize' in cfg:
            resize = cfg['resize']
            w, h = resize['w'], resize['h']
            img = cv2.resize(img, (w, h))

        if 'crop' in cfg:
            crop = cfg['crop']
            mode = crop['mode']
            size = crop['size']
            w, h = size['w'], size['h']
            if mode == 'random':
                times = crop['times']
                for i in range(times + 1):
                    patch = self._random_crop(img, w, h)
                    output_suffux_path = attach_file_suffix(output_path, str(i + 1))
                    print('   %s \033[1;32m->\033[0m %s' % (input_path, output_suffux_path))
                    self.save_img(output_suffux_path, patch)

                save = False
            else:
                start_point = crop['start_point']
                x, y = start_point['left'], start_point['top']
                img = img[y:y + h, x:x + w]

        if 'flip' in cfg:
            flip = cfg['flip']
            if 'vertical' in flip:
                v = flip['vertical']
                if v:
                    img2 = cv2.flip(img, 0)
                    self.save_img(attach_file_suffix(output_path, v), img2)
                    save = False
                else:
                    img = cv2.flip(img, 0)

            if 'horizontal' in flip:
                h = flip['horizontal']
                if h:
                    img2 = cv2.flip(img, 1)
                    self.save_img(attach_file_suffix(output_path, h), img2)
                    save = False
                else:
                    img = cv2.flip(img, 1)

            if 'both' in flip:
                b = flip['both']
                if b:
                    img2 = cv2.flip(img, -1)
                    self.save_img(attach_file_suffix(output_path, b), img2)
                    save = False
                else:
                    img = cv2.flip(img, -1)

        if 'rotate' in cfg:
            rotate = cfg['rotate']
            if 90 in rotate:
                _90 = rotate[90]
                if _90:
                    img2 = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
                    self.save_img(attach_file_suffix(output_path, _90), img2)
                    save = False
                else:
                    img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)

            if 270 in rotate:
                _270 = rotate[270]
                if _90:
                    img2 = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
                    self.save_img(attach_file_suffix(output_path, _270), img2)
                    save = False
                else:
                    img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)

            if 180 in rotate:
                _180 = rotate[180]
                if _180:
                    img2 = cv2.rotate(img, cv2.ROTATE_180)
                    self.save_img(attach_file_suffix(output_path, _180), img2)
                    save = False
                else:
                    img = cv2.rotate(img, cv2.ROTATE_180)



        if save:
            self.save_img(output_path, img)


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
    # print(trans.folders)
