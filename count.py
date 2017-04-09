#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import re
import csv
import sqlite3
from typing import Sequence
from pathlib import Path


from tqdm import tqdm  # type: ignore

from js_tokenize import Token, tokenize

minified = re.compile(r'\bmin[.]js$')


def main():
    conn = sqlite3.connect('sources.sqlite3')
    cur = conn.execute('''SELECT hash, path, source FROM source_file''')

    fields = 'filehash', 'ntokens', 'sloc', 'min.js', 'path'
    with open('tokens.csv', 'w') as res:
        writer = csv.DictWriter(res, fields)
        writer.writeheader()

        # Map to matrix
        for filehash, path, source in tqdm(cur):
            # Variables to create:
            #  - sloc
            #  - number of tokens
            #  - matches /\bmin[.]js$/
            tokens = tokenize(source)
            if len(tokens) == 0:
                # Skip zero length files
                continue

            writer.writerow({
                'filehash': filehash,
                'ntokens': len(tokens),
                'sloc': sloc(tokens),
                'min.js': bool(minified.search(path)),
                'path': Path(path).name
            })


def sloc(tokens: Sequence[Token]) -> int:
    return len(set(t.line for t in tokens))


if __name__ == '__main__':
    main()
