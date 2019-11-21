import argparse
import os

import cv2
from src.combine import combine
from src.load_config import load_yml
from src.misc_utils import checkdir, copydir, annotate_all, save_crop

global cfg
# print(cfg)

# id=["12","4","29","94","96"]
id = ["a", 'b', 'c', 'd']
colordict = {
    'red': (0, 0, 200),
    'green': (0, 200, 0),
    'blue': (200, 0, 0),
    'wheat': (200, 255, 255),
    'grey': (200, 200, 200),
}

global color, tag
global aaa
global img
global imgtmp
global point1, point2
global min_x, min_y, width, height


def parse_args():

    parser = argparse.ArgumentParser(description='manual annotation images for comparison.')
    parser.add_argument('ymlpath')

    args = parser.parse_args()

    return args


def on_mouse(event, x, y, flags, param):
    # global img, point1, point2, aaa, color, tag
    global point1, point2, img, imgtmp
    global min_x, min_y, width, height
    thickness = cfg['thickness']
    img2 = img.copy()
    color = param
    if event == cv2.EVENT_LBUTTONDOWN:  # 左键点击
        point1 = (x, y)
        cv2.circle(img2, point1, 10, color, thickness)
        cv2.imshow('image', img2)
    elif event == cv2.EVENT_MOUSEMOVE and (flags & cv2.EVENT_FLAG_LBUTTON):  # 按住左键拖曳
        cv2.rectangle(img2, point1, (x, y), color, thickness)
        cv2.imshow('image', img2)
    elif event == cv2.EVENT_LBUTTONUP:  # 左键释放
        point2 = (x, y)
        cv2.rectangle(img2, point1, point2, color, thickness)
        cv2.imshow('image', img2)
        min_x = min(point1[0], point2[0])
        min_y = min(point1[1], point2[1])
        width = abs(point1[0] - point2[0])
        height = abs(point1[1] - point2[1])

        imgtmp = img2
        return


def compare(root_path, ymlfile='configs/config.yml'):
    output_folder = cfg['output_folder']
    checkdir(output_folder)

    save_index = 1

    auto = cfg['folder_path'] == 'auto'
    if auto:
        paths = os.listdir(root_path)
        paths.sort()
    else:
        paths = cfg['folder']

    for i in range(len(paths)):
        path = paths[i]
        save_dir = os.path.join(output_folder, str(save_index))
        checkdir(save_dir)
        copydir(os.path.join(root_path, path), save_dir)
        save_index = annotation(save_dir, cfg['annotations'][i], cfg['color'][i], save_index)

    combine(output_folder, [str(i) for i in range(1, save_index)], cfg=ymlfile)
    # for path in paths: # a/b/c/d


# a folder
def annotation(img_folder, annotations=1, colors=['red'], save_index=1):
    assert annotations == len(colors), 'annotations != len(colors)'
    output_folder = cfg['output_folder']
    crop = cfg['mode'] == 'crop'
    thickness = cfg['thickness']
    if crop:
        crop_index = save_index
    global img
    global min_x, min_y, width, height

    print('annotate folder: ' + img_folder)

    img1 = os.listdir(img_folder)
    img1.sort()
    img_path = os.path.join(img_folder, img1[0])
    print(img_path)
    img = cv2.imread(img_path)

    for i in range(annotations):
        color = colors[i]
        color = colordict[color]

        cv2.namedWindow('image')
        cv2.setMouseCallback('image', on_mouse, param=color)
        cv2.imshow('image', img)
        cv2.waitKey(0)
        if crop:
            crop_index = crop_index + 1
            checkdir(os.path.join(output_folder, str(crop_index)))
            save_crop(img_folder, os.path.join(output_folder, str(crop_index)), [min_y, min_x], height, width)

        img = imgtmp
        save_dir = os.path.join(output_folder, str(save_index))
        annotate_all(save_dir, [min_y, min_x], height, width, color, thickness)
        print('    annotation %d saved' % (i + 1))

    if crop:
        save_index = crop_index

    return save_index + 1


if __name__ == '__main__':
    args = parse_args()
    cfg = load_yml(args.ymlpath, 'comparison_annotation')
    root_dir = cfg['input_dir']
    compare(root_dir, args.ymlpath)

