import argparse
import os
import cv2


from load_config import load_yml
from misc_utils import checkdir, copydir, annotate_all, save_crop, is_file_image, abstractmethod


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
        if '_meta_' not in cfg:
            raise Exception('meta info not found in config file (*.yml)')
        meta = cfg['_meta_']
        try:
            self._input_root = meta['input_root']

            if 'compare_root' in meta:
                self._compare_root = meta['compare_root']

            self.is_dir_input = os.path.isdir(self._input_root)
            if not os.path.exists(self._input_root):
                raise FileNotFoundError('input directory "%s" not found' % self._input_root)

            if self._compare_root and not os.path.exists(self._compare_root):
                raise FileNotFoundError('compare directory "%s" not found' % self._compare_root)

            self._output_root = meta['output_root']
            if self.is_dir_input:
                checkdir(self._output_root)

            self._recursively = meta['recursively']
            if 'folder_list' in meta:
                self._folder_list = meta['folder_list']
            else:
                self._folder_list = None

            if 'save_format' in meta:
                self.save_format = meta['save_format']
            else:
                self.save_format = None

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

        if self.is_dir_input:
            input_path = self._get_input_abs_path(folder, imfile)
            compare_path = self._get_compare_abs_path(folder, imfile) if self._compare_root else None
            if compare_path and not os.path.exists(compare_path):
                raise FileNotFoundError('compare file "%s" not found' % compare_path)
            checkdir(os.path.join(self._output_root, folder))
            output_path = self._get_output_abs_path(folder, imfile)
        else:
            # only one image for input
            input_path = self._input_root
            compare_path = self._compare_root if self._compare_root else None
            if compare_path and not os.path.exists(compare_path):
                raise FileNotFoundError('compare file "%s" not found' % compare_path)
            output_path = self._output_root

        # print('%d %s \033[1;33m->\033[0m %s' % (self._i, input_path, output_path))
        self._handle_image(input_path, output_path, compare_path)
        self._log(input_path, output_path, compare_path)
        self._i = self._i + 1

    # must be implemented in subclass
    @abstractmethod
    def _handle_image(self, input_path, output_path, compare_path=None):
        pass

    def _handle_folder(self, folder):
        abs_folder = self._get_input_abs_path(folder)

        lists = os.listdir(abs_folder)
        for f in lists:
            full_path_f = os.path.join(abs_folder, f)
            if os.path.isdir(full_path_f):
                if self._recursively:
                    if self._folder_list and f not in self._folder_list:
                        continue
                    self.folders[os.path.join(folder, f)] = []
                    self._handle_folder(os.path.join(folder, f))

            else:

                self._check_image(folder, f)

    def handle(self):
        if self.is_dir_input:
            self.folders[''] = []
            self._handle_folder('')
        else:
            self._check_image('', self._input_root)

    def _log(self, input_path, output_path, compare_path=None):
        if compare_path:
            print('%d %s \033[1;33m&\033[0m %s \033[1;32m->\033[0m %s' % (self._i, input_path, compare_path, output_path))
        else:
            print('%d %s \033[1;32m->\033[0m %s' % (self._i, input_path, output_path))


class T(Base):
    def __init__(self, cfg):
        Base.__init__(self, cfg)

    def _handle_image(self, input_path, output_path):
        abs = self._get_output_abs_path(input_path, output_path)
        #img = cv2.imread(abs)
        # print('%s->%s' % (input_path, output_path))


def test(cfg):
    base = T(cfg)
    base.handle()


def main():
    args = parse_args()
    cfg = load_yml(args.ymlpath)

    test(cfg)


if __name__ == '__main__':
    main()
