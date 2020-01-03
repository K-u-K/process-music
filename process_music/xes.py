from pm4py.objects.log.adapters.pandas import csv_import_adapter
from pm4py.objects.conversion.log import factory as conversion_factory
from pm4py.objects.log.exporter.xes import factory as xes_exporter

import pandas

import os
import sys

def export_to_xes(filename):
    output = os.path.splitext(filename)[0].lower()

    df = csv_import_adapter.import_dataframe_from_path(filename, sep=";")
    df = df.rename(columns={
        "Case_ID":  "case:concept:name", 
        "Event":    "concept:name",
        "Type":     "org:type",
        "Order":    "org:order",
        "Is_Chord": "org:is_chord"
    })

    # create internal XES log from pandas dataframe
    log = conversion_factory.apply(df)
    # save XES log
    xes_exporter.export_log(log, f"{output}.xes")
