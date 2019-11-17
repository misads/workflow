## img_opration
　　batch scripts for some basic image operations (crop, affine transformation, tile, combination, comparison, etc.).


### Required Python Packages

```
  opencv-python  
  PyYAML
  numpy
```

### Usage

1.put your image files in a structure like this:

```yaml
. 
├── raw
│   ├── 1.png
│   ├── 2.png
│   ├── 3.png
│   ├── 4.png
│   └── ...
├── compare  # only if comparison is needed
│   ├── 1.png
│   ├── 2.png
│   ├── 3.png
│   ├── 4.png
│   └── ...
└─── result
```

2. copy config template in 'configs' directory (e.g. configs/trans.yml) to configs/my_trans.yml (leave original as a backup).

3. modify configs/my_trans.yml as you need. Be aware that 'input_root', 'compare_root', 'output_root' fields should be set to corresponding directory path.
```yaml
    input_root: 'raw'
    compare_root: 'compare'
    output_root: 'result'
```

4. run `python transform.py configs/my_trans.yml`

### Operations & Config Template

  Transformation

```yaml
_meta_:
    input_root: 'raw'  # could either be a directory or a (single) image path
    compare_root: ''  # set only when comparison is needed/ should have the same struture with input_root's
    output_root: 'trans'
    recursively: True  # whether enable recursively folder detecting
    # folder_list: ["12", "4", "29", "94", "96"]  # if assigned, only selected folders will be handled
    # save_format: '.jpg'  # be one of {'', '.jpg', '.png', '.bmp', '.jpeg', '.tiff'}. save as input's original format if not assigned

resize:  # image will first resize to this size
    w: 400  # width
    h: 400  # height

crop:  
    mode: "random"  # 'random' or 'fix'
    times:
        10  # only set in random mode, randomly crop 10 patchs from input image
    start_point:   # only set in fix mode, croping starts from this point
        left: 0
        top: 0
    size:  # crop size
        w: 400
        h: 400
flip:
    vertical: 'v'  # save suffix, empty for not saving
    horizontal: 'h'
    both: 'vh'

rotate:  # clockwise
    90: '90'  # save suffix, empty for not saving
    180: '180'
    270: '270'
```