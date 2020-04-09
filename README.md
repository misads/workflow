## Workflow (for image)
　　A configurable batch script for common image operations (crop, affine transformation, split, combination, comparison, etc.).

### What Can it Do?

　　With this workflow script, image operations can be easily & automatically performed following the guidance of which has been configured in a `*.yml` file, an example is as below:  

![result](http://www.xyu.ink/wp-content/uploads/2019/11/workflow.png)

　　(op1: **split** images; op2: **combine** them back; op3: **evaluate** their similarity)

### Requirements

```
  opencv-python  
  PyYAML
  numpy
  scikit-image (for evaluation metrics)
```

### Quick Start

1. Put your image files in a structure like this:

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

2. Copy one of the configure templates in 'configs' directory (e.g. `configs/workflow.yml`) to `configs/my_workflow.yml` (leaving the original as a backup).

3. Modify `configs/my_workflow.yml` as you need. Beware that `input`, `compare`, `output` fields should be set to corresponding directory paths.
```yaml
    input: 'raw'
    compare: 'compare'
    output: 'result'
```

4. Run `python workflow.py configs/my_config.yml`

### Arguments

```bash
usage: workflow.py [-h] [--input INPUT] [--output OUTPUT] [--compare COMPARE]
                   [--yes]
                   [--mode {default,1_to_1,1_to_n,n_to_1,2_to_0,n_to_0}]
                   ymlpath

usage: python [filename].py configs/[config].yml

positional arguments:
  ymlpath

optional arguments:
  -h, --help            show this help message and exit
  --input INPUT, -i INPUT
                        input dir (can set in configure file)
  --output OUTPUT, -o OUTPUT
                        output dir
  --compare COMPARE, -c COMPARE
                        compare dir
  --yes, -y             ignore confirmations.
  --mode {default,1_to_1,1_to_n,n_to_1,2_to_0,n_to_0}
                        set to `default` or `{x}_to_{y}`. x: num of images
                        handled once, y: if n, a folder will be created for
                        each input image.
                        
```

### Yml File Example

　　The following example shows the configure file to **split** images in folder `val` into 2 × 2 tiles (saved in `split` folder) and then **combine** them back (saved in `combine` folder). Afterwards, our `op3` will check if the inputs and combined results are exactly the same. (by *ssim*)

```yaml
workflow:
    - op1:
        __meta__:
            input: 'val'  # input directory
            output: 'split'
            recursively: False  # recursively = False: not include sub directory
        split:
            tiles:
                w: 2
                h: 2

    - op2:
        __meta__:
            input: 'split'
            output: 'combine'
            recursively: True  # recursively = True: include sub directory
        combine:
            one_folder_in_axis: 'xy'  # one folder in one output image
            priority_axis: 'x'  # row-major
            tiles:
                w: 2  # num_a_row
                h: 2  # rows(folders)

    - op3:
          __meta__:
              input: 'val'
              compare: 'combine'

          evaluate:
              - f1
              - f2
              - ssim
```

　　The running result snapshot is shown in *What Can it Do* part.

　　A more comprehensive configure template is available [here](https://github.com/misads/img_workflow/blob/master/configs/template.yml).



