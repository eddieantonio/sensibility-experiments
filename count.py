#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import re
import csv
import sqlite3
from typing import Sequence
from pathlib import Path

#import numpy as np  # type: ignore
#import matplotlib.pyplot as ply  # type: ignore
#from sklearn import svm  # type: ignore

from tqdm import tqdm  # type: ignore

from sensibility.token_utils import Token  # type: ignore

minified = re.compile(r'\bmin[.]js$')


def parse(source: bytes) -> Sequence[Token]:
    ...


def main():
    conn = sqlite3.connect('sources.sqlite3')
    cur = conn.execute('''SELECT hash, path, source FROM source_file''')

    fields = 'filehash', 'ntokens', 'sloc', 'min.js', 'path'
    with open('results', 'w') as res:
        writer = csv.DictWriter(res, fields)
        writer.writeheader()

        # Map to matrix
        for filehash, path, source in tqdm(cur):
            # Variables to create:
            #  - sloc
            #  - number of tokens
            #  - matches /\bmin[.]js$/
            tokens = parse(source)
            if len(ntokens) == 0:
                # Skip zero length files
                continue

            writer.writerow({
                'filehash': filehash,
                'ntokens': len(tokens),
                'nlines': tokens[-1].lines,
                'min.js': bool(minified.search(path)),
                'path': Path(path).name
            })

if __name__ == '__main__':
    main()
