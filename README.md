## img_workflow
　　Configurable batch script for several simple image operations (crop, affine transformation, split, combination, comparison, etc.).

### What Can it Do?

　　With this workflow script, image operations can be easily & automatically performed following the guidence of which be configured in a `*.yml` file, an example is as below:

![result](http://www.xyu.ink/wp-content/uploads/2019/11/workflow.png)

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

2. Copy a config template in 'configs' directory (e.g. `configs/workflow.yml`) to `configs/my_workflow.yml` (leave the original as a backup).

3. Modify `configs/my_workflow.yml` as you need. Beware that `input`, `compare`, `output` fields should be set to corresponding directory path.
```yaml
    input: 'raw'
    compare: 'compare'
    output: 'result'
```

4. Run `python workflow.py configs/my_workflow.yml`

### Yml File Example

　　The following example shows the config file to **split** images in folder `val` into 2 × 2 tiles (save in `split` folder) and then **combine** them back (save in `combine` folder). Afterwards, we will check if the inputs and combined results are the same. (by *ssim*)

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

　　The runing result snapshot is shown in preceding *What Can it Do* part.



