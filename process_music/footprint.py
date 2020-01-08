from pm4py.objects.log.adapters.pandas import csv_import_adapter

import numpy as np
import pandas as pd

import os
import sys

import constants

def calculate_footprint_symbol(ft, prevnext, curr, arrow1, arrow2):
    if prevnext is None:
        return ft

    if (ft[prevnext][curr] == '#'): 
        ft[prevnext][curr] = arrow1

    if (ft[prevnext][curr] == arrow2): 
        ft[prevnext][curr] = '||'

    return ft

def calculate_footprint_matrix(filename):
    output = os.path.splitext(filename)[0].lower()

    df = csv_import_adapter.import_dataframe_from_path(filename, sep=";")

    pitches          = constants.PITCHES + ["Pause"]
    pitches_range    = np.arange(len(pitches))
    footprint_matrix = pd.DataFrame('#', index=pitches_range, columns=pitches_range)

    rename_dict = {i:pitch for i, pitch in enumerate(pitches)}
    footprint_matrix.rename(
        index=rename_dict, 
        columns=rename_dict, 
        inplace=True)

    # Consider transitions only within a case
    # d = {}
    # for index, row in df.iterrows():
    #     if row['Case_ID'] not in d.keys():
    #         d[row['Case_ID']] = []
    #     d[row['Case_ID']].append(row['Event'])

    # Consider transitions beyond a case
    d = {"0": []}
    for _, row in df.iterrows():
        d["0"].append(row["Event"])

    for _, value in d.items():
        for prev, curr, next in zip([None]+value[:-1], value, value[1:]+[None]):
            if curr is None:
                continue
            
            if curr is not None and curr[:-1] in constants.PITCHES:
                curr = curr[:-1]
            if prev is not None and prev[:-1] in constants.PITCHES:
                prev = prev[:-1]
            if next is not None and next[:-1] in constants.PITCHES:
                next = next[:-1]

            if prev is not None:
                footprint_matrix = calculate_footprint_symbol(footprint_matrix, prev, curr, '<=', '=>')

            if next is not None:
                footprint_matrix = calculate_footprint_symbol(footprint_matrix, next, curr, '=>', '<=')

    return footprint_matrix
