# encoding = utf-8

import argparse


from src.load_config import load_yml
from src.misc_utils import args
from src.transform import transform
from src.split import split
from src.combine import combine
# from src.evaluate import evaluate

# operations dictionary, map strings to functions
ops_dict = {'transformation': transform,
            'split': split,
            'combine': combine,
            # 'evaluate': evaluate,
            }


def workflow(cfg):
    # print(cfg)

    if 'workflow' not in cfg:
        raise KeyError('the following key is required: workflow')

    _workflow = cfg['workflow']

    for jobname in _workflow:
        assert len(jobname) == 1, 'only one operation could be done in one work'
        for key in jobname:
            job = jobname[key]

        op = False
        for op_key in ops_dict:
            if op_key in job:
                op_func = ops_dict[op_key]
                op = True
                print('\033[1;33m---------[%s: %s]---------\033[0m' % (list(jobname.keys())[0], op_key))
                op_func(job)

        if not op:
            print('Warning: no known operation found in %s' % list(jobname.keys())[0])


if __name__ == '__main__':
    cfg = load_yml(args.ymlpath)
    workflow(cfg)
