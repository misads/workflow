import yaml
import sys
import os


def load_yml(file='configs/config.yml', op=None):
    if not os.path.isfile(file):
        raise FileNotFoundError('File "%s" not found' % file)

    with open(file, 'r') as f:
        try:
            cfg = yaml.safe_load(f.read())
        except yaml.YAMLError:
            raise Exception('Error parsing YAML file: ' + file)

    if op:
        return cfg[op]
    else:
        return cfg


if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg1 = sys.argv[1]
        cfg = load_yml(arg1)
    else:
        cfg = load_yml()
    print(cfg)
