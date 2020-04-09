import os
import argparse
import random

os.makedirs('./_.trash', exist_ok=True)


parser = argparse.ArgumentParser(description='usage: python clear.py [file or directory]')
parser.add_argument('file', help='file to clear')
opt = parser.parse_args()

string = '0123456789abcdef'
ran = ''.join([string[random.randint(0, 15)] for _ in range(16)])

cmd = 'mv %s ./_.trash/%s' % (opt.file, ran)
print(cmd)
os.system(cmd)

