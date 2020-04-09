import argparse
import os
import pdb
from shutil import copyfile
import cv2
import numpy as np


def parse_args():
    parser = argparse.ArgumentParser(description='usage: python workflow.py [config].yml --input input_dir')
    parser.add_argument('ymlpath', help='yml configure file')
    parser.add_argument('--input', '-i', help='input dir')
    parser.add_argument('--output', '-o', help='output dir')
    parser.add_argument('--compare', '-c', help='compare dir')
    parser.add_argument('--yes', '-y',  action='store_true', help='ignore confirmations.')
    parser.add_argument('--mode', dest='mode',
                        help='set to `default` or `{x}_to_{y}`. x: num of images handled once, y: if n, a folder ' +
                             'will be created for each input image.',
                        choices=['default', '1_to_1', '1_to_n', 'n_to_1', '2_to_0', 'n_to_0'], default='default')

    args = parser.parse_args()
    return args


args = parse_args()


def binaryzation(img, thresh=128, max=255):
    grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    grey[grey < thresh] = 0
    grey[grey >= thresh] = max
    return grey


def random_crop(img, w, h):
    height, width, _ = img.shape
    x = np.random.randint(0, width - w)
    y = np.random.randint(0, height - h)
    patch = img[y:y + h, x:x + w]
    return patch


def numeric_score(prediction, groundtruth):
    """Computes scores:
    FP = False Positives
    FN = False Negatives
    TP = True Positives
    TN = True Negatives
    return: FP, FN, TP, TN"""

    FP = np.float(np.sum((prediction == 0) & (groundtruth == 1)))
    FN = np.float(np.sum((prediction == 1) & (groundtruth == 0)))
    TP = np.float(np.sum((prediction == 0) & (groundtruth == 0)))
    TN = np.float(np.sum((prediction == 1) & (groundtruth == 1)))

    return FP, FN, TP, TN


def f_score(prediction, groundtruth, beta=1.0):

    FP, FN, TP, TN = numeric_score(prediction, groundtruth)
    # pdb.set_trace()
    Precision = np.divide(TP, TP + FP)
    Recall = np.divide(TP, TP + FN)
    f = np.divide((1 + beta ** 2) * Precision * Recall, beta ** 2 * Precision + Recall)
    return f * 100.0


# precision and recall share the same importance
def f1(prediction, groundtruth):
    return f_score(prediction, groundtruth, beta=1.0)


# recall is more important
def f2(prediction, groundtruth):
    return f_score(prediction, groundtruth, beta=2.0)


def accuracy_score(prediction, groundtruth):
    """Getting the accuracy of the model"""

    FP, FN, TP, TN = numeric_score(prediction, groundtruth)
    N = FP + FN + TP + TN
    accuracy = np.divide(TP + TN, N)
    return accuracy * 100.0


def safe_key(dic, key, default=None):
    if key in dic:
        return dic[key]
    else:
        return default


def abstractmethod(func):
    def dec(*args):
        result = func(*args)
        raise NotImplementedError('abstract method not implemented')
        return result

    return dec


def checkdir(dir):
    if not os.path.isdir(dir):
        os.makedirs(dir)


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


def is_file_image(filename: str):
    img_ex = ['jpg', 'png', 'bmp', 'jpeg', 'tiff']
    if '.' not in filename:
        return False
    s = filename.split('.')

    # return any(filename.endswith('extension') for extension in img_ex)

    if s[-1].lower() not in img_ex:
        return False

    return True


def attach_file_suffix(filename, suffix, ex=''):
    # if suffix and suffix[0] != '_':
    #     suffix = '_' + suffix
    s = filename.split('.')
    ext = s[-1]
    if ex == '':
        ex = '.' + ext
    name = filename[:-len(ext) - 1]

    if suffix and '.' in suffix:
        sf = suffix.split('.')
        ex = sf[1]
        return name + suffix

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
