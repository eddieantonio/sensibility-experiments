#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# Copyright (C) 2017 Eddie Antonio Santos <easantos@ualberta.ca>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


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
