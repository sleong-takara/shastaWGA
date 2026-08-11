# -*- coding: utf-8 -*-
"""
Created on Tue Jun 11 12:28:57 2024

@author: leongs
"""

#---------------------------------------------------------------------------------------------
# Author: Hima Anbunathan
# Last updated: 2024-May-21
# Description: Code computes breadth of coverage for pseudoBAM/scBAM file from SNV pipeline
#-----------------------------------------------------------------------------------------------

import argparse
import pandas as pd
import os
import subprocess
from multiprocessing import Pool

#%%

def summary_table(WGS_METRIC_FOLDER):
    # Initialize lists to store data
    samplename = []
    coverage_1x = []
    coverage_5x = []
    coverage_10x = []
    coverage_15x = []
    coverage_20x = []
    coverage_25x = []
    coverage_30x = []

    # Loop through each file in the specified folder
    for filename in os.listdir(WGS_METRIC_FOLDER):
        if filename.endswith("_collect_wgs_metrics.txt"):
            with open(os.path.join(WGS_METRIC_FOLDER, filename), "r") as file:
                for line in file:
                    if line.startswith("WHOLE_GENOME"):
                        columns = line.strip().split('\t')
                        # Extract the required coverage metrics
                        PCT_1X = columns[14]
                        PCT_5X = columns[15]
                        PCT_10X = columns[16]
                        PCT_15X = columns[17]
                        PCT_20X = columns[18]
                        PCT_25X = columns[19]
                        PCT_30X = columns[20]
                        # Append data to lists
                        samplename.append(filename)
                        coverage_1x.append(PCT_1X)
                        coverage_5x.append(PCT_5X)
                        coverage_10x.append(PCT_10X)
                        coverage_15x.append(PCT_15X)
                        coverage_20x.append(PCT_20X)
                        coverage_25x.append(PCT_25X)
                        coverage_30x.append(PCT_30X)

    # Create a dictionary with the collected data
    data = {
        'samplename': samplename,
        'coverage_1x': coverage_1x,
        'coverage_5x': coverage_5x,
        'coverage_10x': coverage_10x,
        'coverage_15x': coverage_15x,
        'coverage_20x': coverage_20x,
        'coverage_25x': coverage_25x,
        'coverage_30x': coverage_30x
    }

    # Create a DataFrame from the dictionary
    df = pd.DataFrame(data)
    return df
#%%

path = "C:/Users/leongs/OneDrive - Takara Bio USA, Inc/5. Data analysis/WGA/40cells"
df = summary_table(path)
df.to_csv(path+'/coverage.csv',index=False)

