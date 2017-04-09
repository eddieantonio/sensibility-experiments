#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import csv

import numpy as np  # type: ignore
#import matplotlib.pyplot as ply  # type: ignore
from sklearn.cluster import KMeans  # type: ignore

from typing import NamedTuple
from math import log


class SourceFile(NamedTuple):
    filehash: str
    ntokens: int
    sloc: int
    minified: bool
    path: str


def to_bool(text: str) -> bool:
    if text == 'True':
        return True
    elif text == 'False':
        return False
    else:
        raise ValueError(text)


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

    for label, sf in zip(kmeans.labels_, files):
        print(f"{label}:{sf.ntokens / sf.sloc:.1}:{sf.filehash}")
