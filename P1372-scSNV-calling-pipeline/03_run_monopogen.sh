#!/bin/bash
# ------------------------------------------------
# Author: Hima Anbunathan
# Last updated: 2023-11-28
# Description: Bash Script to run SNV calling using Monopogen (step 3 - snv calling workflow)
# ------------------------------------------------

if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <bam_lst> <cell_cluster> <output_dir>"
    exit 1
fi

# ------------------
# Set environment
# ------------------
path="/wgbs/scratch2/hanbunathan/pipelines/monopogen_worflow_modified/Monopogen"  
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:${path}/apps

#----------------------------
# Set filepaths
#----------------------------
BAM_LIST_FILE="$1"
CELL_CLUSTER_FILE="$2"
OUTPUT_DIR="$3"

MONOPOGEN='/wgbs/scratch2/hanbunathan/pipelines/monopogen_worflow_modified/Monopogen/src/Monopogen.py'
MONOPOGEN_APP='/wgbs/scratch2/hanbunathan/pipelines/monopogen_worflow_modified/Monopogen/apps'
REFERENCE_FASTA='/wgbs/scratch2/hanbunathan/pipelines/monopogen_worflow_modified/grch38.fa'

REGION_LIST_FILE='/wgbs/scratch2/hanbunathan/pipelines/monopogen_worflow_modified/region.lst'
REGION_LIST_DIR='/wgbs/scratch2/hanbunathan/pipelines/monopogen_worflow_modified/1K3G_imputation_panel/'


echo $BAM_LIST_FILE
echo $CELL_CLUSTER_FILE
echo $OUTPUT_DIR

# -------------------------------------------
# Step 1 - preprocess
# -------------------------------------------
python $MONOPOGEN preProcess -b $BAM_LIST_FILE -o $OUTPUT_DIR -a $MONOPOGEN_APP -t 64

# -------------------------------------------
# Step 2 - germline calling
# -------------------------------------------
python $MONOPOGEN germline -a $MONOPOGEN_APP -r $REGION_LIST_FILE -p $REGION_LIST_DIR -t 64 -g $REFERENCE_FASTA -m 3 -s all -o $OUTPUT_DIR

# -------------------------------------------------------------------------
# Step3 Putative LD refinement step
# -------------------------------------------------------------------------
python $MONOPOGEN somatic -a $MONOPOGEN_APP -r $REGION_LIST_FILE -i $OUTPUT_DIR -l $CELL_CLUSTER_FILE -t 64 -s all -g $REFERENCE_FASTA

echo 'end of pipeline'