import os
from shutil import copyfile
import cv2
import numpy as np


def abstractmethod(func):
    def dec(*args):
        result = func(*args)
        raise NotImplementedError('abstract method not implemented')
        return result

    return dec


def checkdir(dir):
    if not os.path.isdir(dir):
        os.mkdir(dir)


def copydir(dir1, dir2):
    files = os.listdir(dir1)
    for file in files:
        copyfile(os.path.join(dir1, file), os.path.join(dir2, file))


def get_file_paths(folder):
    image_file_paths = []
    for root, dirs, filenames in os.walk(folder):
        filenames = sorted(filenames)
        for filename in filenames:
            input_path = os.path.abspath(root)
            file_path = os.path.join(input_path, filename)
            image_file_paths.append(file_path)

        break  # prevent descending into subfolders
    return np.array(image_file_paths)


def is_file_image(filename):
    img_ex = ['jpg', 'png', 'bmp', 'jpeg', 'tiff']
    if '.' not in filename:
        return False
    s = filename.split('.')

    if s[-1].lower() not in img_ex:
        return False

    return True


def attach_file_suffix(filename, suffix, ex=''):
    if suffix:
        suffix = '_' + suffix
    s = filename.split('.')
    ext = s[-1]
    if ex == '':
        ex = '.' + ext
    name = filename[:-len(ext)-1]

    return name + suffix + ex



def annotate_all(dir, start_point, h, w, BGR, thickness=5):
    paths = os.listdir(dir)
    for filename in paths:
        path = os.path.join(dir, filename)
        img = cv2.imread(path)
        # cv2.imwrite(os.path.join(outputs_path1, filename), img_cut)
        img_rec = cv2.rectangle(img, (start_point[1], start_point[0]), (start_point[1] + w, start_point[0] + h), BGR,
                                thickness)
        cv2.imwrite(path, img_rec)


def save_crop(input_dir, output_dir, start_point, h, w):
    paths = os.listdir(input_dir)
    for filename in paths:
        path = os.path.join(input_dir, filename)
        img = cv2.imread(path)
        img_cut = img[start_point[0]:start_point[0] + h, start_point[1]:start_point[1] + w, :]
        cv2.imwrite(os.path.join(output_dir, filename), img_cut)


def crop_image(inputs_path, outputs_path1, outputs_path2, start_point, h, w, BGR):
    inputs_path = get_file_paths(inputs_path)
    images = []
    for path in inputs_path:
        _, filename = os.path.split(path)
        print(filename)
        img = cv2.imread(path)
        img_cut = img[start_point[0]:start_point[0] + h, start_point[1]:start_point[1] + w, :]
        # cv2.imwrite(os.path.join(outputs_path1, filename), img_cut)
        cv2.imwrite(os.path.join('./outputs2/87_2', filename), img_cut)
        img_rec = cv2.rectangle(img, (start_point[1], start_point[0]), (start_point[1] + w, start_point[0] + h), BGR, 5)
        cv2.imwrite(os.path.join(outputs_path2, filename), img_rec)
