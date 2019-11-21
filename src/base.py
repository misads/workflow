# encoding = utf-8
"""
Author: xuhaoyu@tju.edu.cn

Usage: define a new class inherited from Base, then set self.mode in one of {'1_to_1', '1_to_n', 'n_to_1', 'n_to_0'}
    in `1_to_*` mode `_handle_image` function will be called for each image file by Base
    in `n_to_*` mode `_handle_dict` function will be called once after parsing the directory

Example:

class Transform(Base):
    def __init__(self, cfg):
        Base.__init__(self, cfg)
        self.mode = '1_to_1'

    def _handle_image(self, input_path, output_path, compare_path=None, abs_out_dir=None, filename=None):
        img = cv2.imread(input_path)
        ......

"""

import argparse
import os
import cv2

from src.load_config import load_yml
from src.misc_utils import checkdir, is_file_image, abstractmethod, safe_key


def parse_args():
    parser = argparse.ArgumentParser(description='usage: python [filename].py configs/[config].yml')
    parser.add_argument('ymlpath')

    args = parser.parse_args()

    return args


class Base(object):
    def __init__(self, cfg):
        self.cfg = cfg
        self._parse_meta()
        self._i = 1
        self.folders = {}

    # parse meta info in cfg
    def _parse_meta(self):
        cfg = self.cfg
        if '__meta__' not in cfg:
            raise Exception('meta info not found in config file (*.yml)')
        meta = cfg['__meta__']
        try:
            self._input_root = meta['input']
            self._compare_root = safe_key(meta, 'compare')
            self._output_root = safe_key(meta, 'output')
            self._recursively = safe_key(meta, 'recursively', True)

            self.is_dir_input = os.path.isdir(self._input_root)
            if not os.path.exists(self._input_root):
                raise FileNotFoundError('input directory "%s" not found' % self._input_root)
            if self.is_dir_input and self._output_root:
                # check root
                checkdir(self._output_root)

            if self._compare_root and not os.path.exists(self._compare_root):
                raise FileNotFoundError('compare directory "%s" not found' % self._compare_root)

            self._folder_list = safe_key(meta, 'folder_list')
            self.save_format = safe_key(meta, 'save_format')

        except KeyError:
            raise Exception('key missing in config file (*.yml)')

    def _get_input_abs_path(self, folder, filename=None):
        if filename:
            return os.path.join(self._input_root, folder, filename)
        else:
            return os.path.join(self._input_root, folder)

    def _get_compare_abs_path(self, folder, filename=None):
        if filename:
            return os.path.join(self._compare_root, folder, filename)
        else:
            return os.path.join(self._compare_root, folder)

    def _get_output_abs_path(self, folder, filename=None):
        if filename:
            return os.path.join(self._output_root, folder, filename)
        return os.path.join(self._input_root, folder)

    def _check_image(self, folder, imfile):
        if not is_file_image(imfile):
            return

        self.folders[folder].append(imfile)

        # dir input
        if self.is_dir_input:
            input_path = self._get_input_abs_path(folder, imfile)
            compare_path = self._get_compare_abs_path(folder, imfile) if self._compare_root else None
            if compare_path and not os.path.exists(compare_path):
                raise FileNotFoundError('compare file "%s" not found' % compare_path)

            '''
            if 'combination' not in self.cfg:
                checkdir(os.path.join(self._output_root, folder))
            if 'crop' in self.cfg:
                checkdir(os.path.join(self._output_root, imfile))
                output_path = self._get_output_abs_path(imfile, imfile)
            else:
                output_path = self._get_output_abs_path(folder, imfile)
            '''
            if self.mode == '1_to_1':
                output_path = self._get_output_abs_path(folder, imfile)
                checkdir(os.path.join(self._output_root, folder))
                out_dir = folder
                abs_out_dir = os.path.join(self._output_root, out_dir)
            elif self.mode == '1_to_n':
                out_dir = os.path.join(folder, imfile)
                abs_out_dir = os.path.join(self._output_root, out_dir)
                checkdir(os.path.join(self._output_root, imfile))
                output_path = self._get_output_abs_path(out_dir, imfile)

            elif self.mode == 'n_to_n':
                # do not handle image
                checkdir(os.path.join(self._output_root, folder))
                return
            elif self.mode == 'n_to_1':
                return
            else:  # 2_to_0 or default
                output_path = None
                abs_out_dir = None

        else:
            # only one image for input
            input_path = self._input_root
            compare_path = self._compare_root if self._compare_root else None
            if compare_path and not os.path.exists(compare_path):
                raise FileNotFoundError('compare file "%s" not found' % compare_path)
            output_path = self._output_root

        # print('%d %s \033[1;33m->\033[0m %s' % (self._i, input_path, output_path))
        self._log(input_path, output_path, compare_path)
        self._handle_image(input_path, output_path, compare_path, abs_out_dir, imfile)
        self._i = self._i + 1

    # must be implemented in subclass
    @abstractmethod
    def _handle_image(self, input_path, output_path, compare_path=None, abs_out_dir=None, filename=None):
        pass

    def _handle_dict(self, dir_dict, len_x, len_y):
        if 'n_to_' in self.mode:
            raise NotImplementedError('must be implemented in n_to_* mode')

    def _handle_folder(self, folder):
        abs_folder = self._get_input_abs_path(folder)

        lists = os.listdir(abs_folder)
        lists.sort()
        for f in lists:
            full_path_f = os.path.join(abs_folder, f)
            # f is folder
            if os.path.isdir(full_path_f):
                if self._recursively:
                    # if assign folders
                    if self._folder_list and f not in self._folder_list:
                        continue
                    self.folders[os.path.join(folder, f)] = []

                    self._handle_folder(os.path.join(folder, f))

            # f is img? file
            else:
                self._check_image(folder, f)  # chech if f is image file

    def save_img(self, filename, img):
        print('   ' + filename)
        cv2.imwrite(filename, img)

    def handle(self):
        if self.is_dir_input:
            self.folders[''] = []
            self._handle_folder('')
            if 'n_to_' in self.mode:
                keys = [i for i in self.folders]
                # ignore empty folders
                for k in keys:
                    if not self.folders[k]:
                        self.folders.pop(k)
                keys = [i for i in self.folders]
                len_x = len(self.folders)
                len_y = len(self.folders[keys[0]]) if keys else 0

                # call _handle_image once
                dir1 = list(self.folders.keys())[0]
                imgpath = (self.folders[dir1][0])
                img_abs_path = self._get_input_abs_path(dir1, imgpath)
                self._handle_image(img_abs_path, None)

                self._handle_dict(self.folders, len_x, len_y)
        else:
            self._check_image('', self._input_root)

    def _log(self, input_path, output_path, compare_path=None):
        if 'n_to_' in self.mode:
            return
        if compare_path:
            print('%d %s \033[1;33m&\033[0m %s \033[1;32m->\033[0m' % (self._i, input_path, compare_path))
        else:
            print('%d %s \033[1;32m->\033[0m' % (self._i, input_path))


# test code
class Test(Base):
    def __init__(self, cfg):
        Base.__init__(self, cfg)

    def _handle_image(self, input_path, output_path, compare_path=None, abs_out_dir=None, filename=None):
        abs = self._get_output_abs_path(input_path, output_path)

        print(abs_out_dir)
        # self.save_img(output_path, '')
        # img = cv2.imread(abs)
        # print('%s->%s' % (input_path, output_path))

    def _handle_dict(self, dir_dict, len_x, len_y):
        print(dir_dict)
        print(len_x, len_y)


def test(cfg):
    base = Test(cfg)
    base.mode = 'n_to_1'
    base.handle()


if __name__ == '__main__':
    args = parse_args()
    cfg = load_yml(args.ymlpath)

    test(cfg)
