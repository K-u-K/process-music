from pm4py.objects.log.adapters.pandas import csv_import_adapter
from pm4py.objects.conversion.log import factory as conversion_factory
from pm4py.objects.log.exporter.xes import factory as xes_exporter
import pandas as pd
import numpy as np 
import os
import sys

if __name__ == '__main__':
    filename   = sys.argv[1] if len(sys.argv) > 1 else "examples\melody_guitar\\track_0.csv"
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "examples\melody_guitar\\track_0.xes"

    if not os.path.exists(filename):
        print(f"file '{filename}' not found")
        sys.exit(1)

    if output_dir == "":
        output_dir = os.path.splitext(filename)[0].lower()

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    df = csv_import_adapter.import_dataframe_from_path(os.path.join(os.getcwd(), filename), sep=";")
    df = df.rename(columns={"Case_ID": "case:concept:name", 
                            "Event": "concept:name",
                            "Type": "org:type",
                            "Order": "org:order",
                            "Is_Chord": "org:is_chord"})

    print(df)
    log = conversion_factory.apply(df)
    for i in range(0, 2):
        print(f"---- Case {i} ----")
        for k in range(0, 10):
            print(log[i][k])
            
    xes_exporter.export_log(log, os.path.join(os.getcwd(), output_dir))