# encoding=utf-8

import numpy as np
import os
import argparse
import cv2
import numpy as np

from src.base import Base
from src.load_config import load_yml
from src.misc_utils import checkdir, attach_file_suffix, safe_key, args


class Ensemble(Base):
    def __init__(self, cfg):
        Base.__init__(self, cfg)
        self.mode = 'n_to_1'

        self._ensemble = self.cfg['ensemble']
        self._mode = self._ensemble['mode']
        self._thresh = safe_key(self._ensemble, 'thresh')
        self._save = safe_key(self._ensemble, 'save')
        self._preview = safe_key(self._ensemble, 'preview')

    def _handle_image(self, input_path, output_path, compare_path=None, abs_out_dir=None, filename=None):
        pass

    def _handle_dict(self, dir_dict, len_x, len_y):
        mode = self._mode
        for i in range(len_y):  # image index
            ensemble_img = None
            for folder_name in dir_dict:
                file_list = dir_dict[folder_name]
                # print(folder)
                input_path = self._get_input_abs_path(folder_name, file_list[i])
                print(input_path + ' & ', end='')
                img = cv2.imread(input_path)
                if ensemble_img is None:
                    ensemble_img = np.array(img, np.float)
                else:
                    if mode == 'mean':
                        ensemble_img += img
                    elif mode == 'vote':
                        pass
            ensemble_img = ensemble_img / len_x
            if self._thresh:
                ensemble_img[ensemble_img < self._thresh] = 0
                ensemble_img[ensemble_img >= self._thresh] = 255
            else:
                ensemble_img[ensemble_img > 255] = 255
                ensemble_img[ensemble_img < 0] = 0
            ensemble_img = np.array(ensemble_img, np.uint8)
            savename = dir_dict[list(dir_dict.keys())[0]][i]
            if self._save:
                savename = attach_file_suffix(savename, self._save)
            output_path = self._get_output_abs_path('', savename)
            print('\033[1;32m->\033[0m')
            if self._preview:
                cv2.imshow('ensemble', ensemble_img)
                cv2.waitKey(0)
            self.save_img(output_path, ensemble_img)



def ensemble(cfg):
    ensemble = Ensemble(cfg)
    ensemble.handle()


if __name__ == '__main__':
    cfg = load_yml(args.ymlpath)
    ensemble(cfg)
