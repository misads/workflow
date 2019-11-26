# encoding=utf-8

import numpy as np
import os
import argparse
import cv2
import numpy as np

from src.base import Base
from src.load_config import load_yml
from src.misc_utils import attach_file_suffix, binaryzation, args, random_crop


class Transform(Base):
    def __init__(self, cfg):
        Base.__init__(self, cfg)
        self.mode = '1_to_1' if args.mode == 'default' else args.mode

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
        changed = False
        for trans in transformation:

            if 'copy' in trans:
                save_path = output_path
                if check_dict_or_str(trans, 'copy'):
                    self.save_img(save_path, img)

                changed = False

            if 'binary' in trans:
                binary = trans['binary']
                thresh = binary['thresh']
                img = binaryzation(img, thresh=thresh)
                changed = save_middle(binary)

            if 'resize' in trans:
                resize = trans['resize']
                w, h = resize['w'], resize['h']
                img = cv2.resize(img, (w, h))
                changed = save_middle(resize)

            if 'random_crop' in trans:
                crop = trans['random_crop']
                size = crop['size']
                w, h = size['w'], size['h']
                patchs = crop['patches']
                if 'save' in crop:
                    suffix = crop['save']
                    save_path = attach_file_suffix(output_path, suffix)
                else:
                    save_path = output_path
                for i in range(patchs + 1):
                    patch = random_crop(img, w, h)
                    output_suffux_path = attach_file_suffix(save_path, '_%04d' % i)
                    print('   %s \033[1;32m->\033[0m %s' % (input_path, output_suffux_path))
                    self.save_img(output_suffux_path, patch)

                changed = False

            if 'fix_crop' in trans:
                crop = trans['fix_crop']
                size = crop['size']
                w, h = size['w'], size['h']
                start_point = crop['from']
                x, y = start_point['left'], start_point['top']
                img = img[y:y + h, x:x + w]
                changed = save_middle(crop)

            if 'flip' in trans:
                flips = trans['flip']
                for flip in flips:
                    if 'vertical' in flip:
                        img = cv2.flip(img, 0)
                        changed = check_dict_or_str(flip, 'vertical')

                    if 'horizontal' in flip:
                        img = cv2.flip(img, 1)
                        changed = check_dict_or_str(flip, 'horizontal')

                    if 'both' in flip:
                        img = cv2.flip(img, -1)
                        changed = check_dict_or_str(flip, 'both')

            if 'rotate' in trans:
                rotates = trans['rotate']
                for rotate in rotates:
                    if type(rotate) == int:
                        rotate = [rotate]
                    if 90 in rotate:
                        img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
                        changed = check_dict_or_str(rotate, 90)

                    if 270 in rotate:
                        img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
                        changed = check_dict_or_str(rotate, 270)

                    if 180 in rotate:
                        img = cv2.rotate(img, cv2.ROTATE_180)
                        changed = check_dict_or_str(rotate, 180)

        if changed:
            self.save_img(output_path, img)


def transform(cfg):
    trans = Transform(cfg)
    trans.handle()


if __name__ == '__main__':
    cfg = load_yml(args.ymlpath)
    transform(cfg)
