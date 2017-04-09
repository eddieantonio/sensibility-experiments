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


import sys
import csv

import numpy as np  # type: ignore
from sklearn.cluster import KMeans  # type: ignore

from operator import attrgetter
from typing import NamedTuple, List
from math import log


class BaseSourceFile(NamedTuple):
    filehash: str
    ntokens: int
    sloc: int
    minified: bool
    path: str


class SourceFile(BaseSourceFile):
    @property
    def ratio(self):
        return self.ntokens / self.sloc



def to_bool(text: str) -> bool:
    if text == 'True':
        return True
    elif text == 'False':
        return False
    else:
        raise ValueError(text)

def find_split(kmeans: KMeans, files: List[SourceFile]) -> None:
    handwritten: List[SourceFile] = []
    generated: List[SourceFile] = []

    for label, sf in zip(kmeans.labels_, files):
        if label == 0:
            handwritten.append(sf)
        else:
            generated.append(sf)

    a = max(handwritten, key=attrgetter('ratio'))
    b = min(generated, key=attrgetter('ratio'))
    split = (a.ratio + b.ratio) / 2

    print(f"Split at {split:.1f}")
    print(f"  last handwritten: {a.ratio:.1f}: {a.path}")
    print(f"  first generated:  {b.ratio:.1f}: {b.path}")


def dump(kmeans: KMeans, files: List[SourceFile]) -> None:
    for label, sf in zip(kmeans.labels_, files):
        print(f"{label}:{sf.ratio:.1f}:{sf.filehash}")


if __name__ == '__main__':
    files = []
    with open('tokens.csv') as csvfile:
        # filehash ntokens sloc min.js path
        reader = csv.DictReader(csvfile)
        for row in reader:
            files.append(SourceFile(
                filehash=row['filehash'],
                ntokens=int(row['ntokens']),
                sloc=int(row['sloc']),
                minified=to_bool(row['min.js']),
                path=row['path']
            ))

    # Plot the datums
    xs = np.zeros((len(files), 1))
    for i, source in enumerate(files):
        xs[i] = log(source.ntokens / source.sloc)

    estimator = KMeans(2)
    kmeans = estimator.fit(xs)

    if '--split' in sys.argv:
        find_split(kmeans, files)
    else:
        dump(kmeans, files)
