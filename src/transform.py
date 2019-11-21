# encoding=utf-8

import numpy as np
import os
import argparse
import cv2
import numpy as np

from src.base import Base
from src.load_config import load_yml
from src.misc_utils import attach_file_suffix


def parse_args():
    parser = argparse.ArgumentParser(description='resize images.')

    parser.add_argument('ymlpath')

    args = parser.parse_args()

    return args


class Transform(Base):
    def __init__(self, cfg):
        Base.__init__(self, cfg)
        self.mode = '1_to_1'

    def _random_crop(self, img, w, h):
        height, width, _ = img.shape
        x = np.random.randint(0, width - w)
        y = np.random.randint(0, height - h)
        patch = img[y:y + h, x:x + w]
        return patch

    def _handle_image(self, input_path, output_path, compare_path=None, abs_out_dir=None, filename=None):

        def save_middle(trans_op):
            if 'save' in trans_op:
                suffix = trans_op['save']
                save_path = attach_file_suffix(output_path, suffix)
                self.save_img(save_path, img)
                return False
            else:
                return True

        def check_dict_or_str(parent_node, op):
            if type(parent_node) == dict:
                node = parent_node[op]  # <dict>{'save': '_1.png'}
                return save_middle(node)
            else:
                return True

        img = cv2.imread(input_path)
        transformation = self.cfg['transformation']
        save = True
        for trans in transformation:

            if 'copy' in trans:
                save_path = output_path
                if check_dict_or_str(trans, 'copy'):
                    self.save_img(save_path, img)

                save = False

                '''
                if type(trans) == dict:
                    copy = trans['copy']
                    if 'save' in copy:
                        suffix = copy['save']
                        save_path = attach_file_suffix(output_path, suffix)
                '''


            if 'resize' in trans:
                resize = trans['resize']
                w, h = resize['w'], resize['h']
                img = cv2.resize(img, (w, h))
                if 'save' in resize:
                    suffix = resize['save']
                    save_path = attach_file_suffix(output_path, suffix)
                    self.save_img(save_path, img)
                    save = False

            if 'crop' in trans:
                crop = trans['crop']
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

            if 'flip' in trans:
                flip = trans['flip']
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

            if 'rotate' in trans:
                rotate = trans['rotate']
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


def transform(cfg):
    trans = Transform(cfg)
    trans.handle()


if __name__ == '__main__':
    args = parse_args()
    cfg = load_yml(args.ymlpath)
    transform(cfg)
