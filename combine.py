import argparse
import os
import numpy as np
from cut_rec import get_file_paths
import cv2

from load_config import load_yml


def parse_args():
    parser = argparse.ArgumentParser(description='manual annotation images for comparison.')
    parser.add_argument('ymlpath')

    args = parser.parse_args()

    return args


def combine(root_path, folderlist=None, cfg='configs/config.yml'):
    cfg = load_yml(cfg, 'combination')

    image_size = cfg['image_size']
    gap = cfg['gap']
    tile = cfg['tiles']
    if folderlist:
        paths = folderlist
    else:
        auto = cfg['folder_path'] == 'auto'
        if auto:
            if not root_path:
                root_path = cfg['input_dir']
            paths = os.listdir(root_path)
            paths.sort()
        else:
            paths = cfg['folder']

    w1, h1 = image_size['w'], image_size['h']  # image will first be resized to this size
    dw1, dh1 = gap['dw'], gap['dh']  # space between images
    nw, nh = tile['w'], tile['h']  # nw × nh, nh should be the number of folders

    print(paths)

    width = nw * w1 + (nw - 1) * dw1  # width for combination image
    height = nh * h1 + (nh - 1) * dh1

    back = np.ones((height, width, 3), np.uint8) * 255  # white background

    # combination
    for h in range(nh):
        try:
            path = paths[h]
            file_path = os.listdir(os.path.join(root_path, path))
            file_path.sort()

            for i in range(nw):
                img_path = os.path.join(root_path, path, file_path[i])
                img = cv2.imread(img_path)
                img = cv2.resize(img, (w1, h1))
                # pt1y,pt2y, pt1x,pt2x = h*(h1+dh1),h*(h1+dh1)+h1, i*(w1+dw1),i*(w1+dw1)+w1
                # print(pt1y,pt2y, pt1x,pt2x)
                back[h * (h1 + dh1):h * (h1 + dh1) + h1, i * (w1 + dw1):i * (w1 + dw1) + w1] = img
        except:
            pass

    cv2.imshow('image', back)
    cv2.imwrite(cfg['output'], back)
    cv2.waitKey(0)


if __name__ == "__main__":
    args = parse_args()
    combine(None, None, args.ymlpath)
