# encoding=utf-8

import numpy as np
import os
import argparse
import cv2
import numpy as np

from src.base import Base
from src.load_config import load_yml
from src.misc_utils import attach_file_suffix, f1, f2, binaryzation
from skimage.metrics import peak_signal_noise_ratio as compare_psnr
from skimage.metrics import structural_similarity as compare_ssim


def parse_args():
    parser = argparse.ArgumentParser(description='resize images.')

    parser.add_argument('ymlpath')

    args = parser.parse_args()

    return args


class Evaluate(Base):
    def __init__(self, cfg):
        Base.__init__(self, cfg)
        self.mode = '2_to_0'

    def _handle_image(self, input_path, output_path, compare_path=None, abs_out_dir=None, filename=None):
        img1 = cv2.imread(input_path)
        img2 = cv2.imread(compare_path)
        evaluation = self.cfg['evaluate']
        if 'f1' in evaluation:
            bin1 = binaryzation(img1, max=1)
            bin2 = binaryzation(img2, max=1)
            f1_score = f1(bin1, bin2)
            print('   f1: %f' % f1_score)
        if 'f2' in evaluation:
            bin1 = binaryzation(img1, max=1)
            bin2 = binaryzation(img2, max=1)
            f2_score = f2(bin1, bin2)
            print('   f2: %f' % f2_score)
        if 'psnr' in evaluation:
            psnr = compare_psnr(img1, img2)
            print('   psnr: %f' % psnr)
        if 'ssim' in evaluation:
            ssim = compare_ssim(img1, img2, multichannel=True)
            print('   ssim: %f' % ssim)


def evaluate(cfg):
    eva = Evaluate(cfg)
    eva.handle()


if __name__ == '__main__':
    args = parse_args()
    cfg = load_yml(args.ymlpath)
    evaluate(cfg)
