# encoding = utf-8

import argparse
import os

from src.ensemble import ensemble
from src.labeling import labeling
from src.load_config import load_yml
from src.misc_utils import args
from src.transform import transform
from src.split import split
from src.combine import combine
from src.evaluate import evaluate

# operations dictionary, map strings to functions
ops_dict = {'transformation': transform,
            'split': split,
            'combine': combine,
            'evaluate': evaluate,
            'ensemble': ensemble,
            'labeling': labeling
            }


def workflow(cfg):
    # print(cfg)

    if 'workflow' not in cfg:
        raise KeyError('the following key is required: workflow')

    _workflow = cfg['workflow']
    job_count = len(_workflow)

    for i, jobname in enumerate(_workflow):
        assert len(jobname) == 1, 'only one operation could be done in one work'
        for key in jobname:
            job = jobname[key]

        if i == 0 and args.input:
            job['__meta__']['input'] = args.input
        if i == 0 and args.compare:
            job['__meta__']['compare'] = args.compare

        if i == job_count - 1 and args.output:
            job['__meta__']['output'] = args.output

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

    if not args.yes:
        if args.input:
            print('\033[1;33minput: %s\033[0m' % args.input)
        if args.output:
            print('\033[1;32moutput: %s\033[0m' % args.output)

        file = args.ymlpath
        if not os.path.isfile(file):
            raise FileNotFoundError('File "%s" not found' % file)

        with open(file, 'r') as f:
            lines = f.readlines()
            for line in lines:
                if not line.strip().startswith('#') and line.strip():
                    print(line.rstrip('\n'))

        confirm = input('continue? (y/n) ')
        if confirm.lower() != 'y':
            print('Abort')
            exit()

    cfg = load_yml(args.ymlpath)
    workflow(cfg)
