# WGA Analysis Scripts

## Overview

This directory contains utility scripts for Whole Genome Amplification (WGA) data analysis, sequencing QC, BAM filtering, pseudobulk generation, coverage analysis, and preparation of inputs for the P1372 single-cell SNV pipeline.

The workflow primarily operates on:

- Single-cell BAMs (scBAM)
- Pseudobulk BAMs (pseudoBAM)
- Picard CollectWgsMetrics outputs
- Coverage summary reports
- Monopogen-compatible pseudobulk inputs

The scripts were developed to support WGA benchmarking, SNV pipeline validation, sequencing depth optimization, and pseudobulk coverage evaluation. 【1-7345cd】【2-e765ef】【3-a5fc0c】

---

# Directory Structure

```text
WGA/
│
├── compile_coverage.py
├── downsample_merged.sh
├── list_bam_reads.sh
├── move_low_reads_bam.sh
├── remove_low_reads.sh
├── update_coverage_with_reads.sh
├── WGA_GiniMedian.R
│
├── pseudobulk_infofile.csv
├── pseudobulk_infofile - Copy.csv
│
└── P1372-scSNV-calling-pipeline/
```

---

# Software Requirements

## Linux Utilities

Required by multiple scripts:

```bash
samtools
awk
sort
bash
```

Install on Ubuntu:

```bash
sudo apt install samtools
```

---

## Python Packages

```bash
pip install pandas
```

`compile_coverage.py` imports:

```python
argparse
pandas
os
subprocess
multiprocessing
```

【1-7345cd】

---

# Recommended Workflow

The intended workflow is:

```text
BAM files
    ↓
list_bam_reads.sh
    ↓
move_low_reads_bam.sh
or
remove_low_reads.sh
    ↓
CollectWgsMetrics
    ↓
compile_coverage.py
    ↓
coverage.csv
    ↓
update_coverage_with_reads.sh
    ↓
coverage_updated.csv
    ↓
WGA_GiniMedian.R
```

This produces a coverage report containing:

- Coverage breadth
- Read counts
- WGA uniformity metrics

---

# Script Documentation

---

# compile_coverage.py

## Purpose

Computes breadth-of-coverage statistics from WGA BAM files.

The script header states:

> computes breadth of coverage for pseudoBAM/scBAM file from SNV pipeline

The script summarizes coverage across multiple depth thresholds:

```python
coverage_1x
coverage_5x
coverage_10x
coverage_15x
coverage_20x
coverage_25x
coverage_30x
```

【1-7345cd】

## Input

Coverage metrics generated from WGS BAM files.

## Output

```text
coverage.csv
```

Expected metrics:

```text
samplename
coverage_1x
coverage_5x
coverage_10x
coverage_15x
coverage_20x
coverage_25x
coverage_30x
```

## Example

```bash
python compile_coverage.py
```

Current script contains a hard-coded path:

```python
path = "C:/Users/leongs/OneDrive - Takara Bio USA, Inc/5. Data analysis/WGA/40cells"
```

Modify as needed before execution.

## Typical Use Case

Determine:

- Coverage breadth
- Sequencing saturation
- WGA performance
- Pseudobulk coverage quality

---

# list_bam_reads.sh

## Purpose

Counts reads for all BAM files in the current directory.

Uses:

```bash
samtools view -@ 16 -c
```

to calculate BAM read counts. 【4-178f97】

## Usage

```bash
cd BAM_files

bash list_bam_reads.sh
```

## Output

```text
bam_read_counts.txt
```

Example:

```text
cell001.bam    452312
cell002.bam    441109
cell003.bam    12843
```

## Typical Use Case

Identify:

- Failed cells
- Low-depth cells
- Candidate BAMs for removal

---

# remove_low_reads.sh

## Purpose

Deletes the lowest-read BAM files.

Unlike threshold filtering, this script removes the lowest N BAMs ranked by read count. 【5-070d46】

## Usage

Remove the lowest 500 BAM files:

```bash
bash remove_low_reads.sh 500
```

The script contains the following example:

```bash
remove_low_reads.sh 500
```

## Workflow

```text
Read BAM counts
        ↓
Rank BAMs
        ↓
Remove N lowest BAMs
```

## Warning

Files are permanently deleted using:

```bash
rm "$FILE"
```

Use with caution.

---

# move_low_reads_bam.sh

## Purpose

Moves the lowest-read BAM files into an archive directory rather than deleting them.

This is the recommended alternative to `remove_low_reads.sh`. 【6-53aa75】

## Usage

Move the lowest 266 BAM files:

```bash
bash move_low_reads_bam.sh ./BAM_files 266
```

Example from script:

```bash
./move_low_reads_bam.sh /path/to/bam/files 266
```

## Output Structure

```text
BAM_files/
├── archive/
└── remaining_files.bam
```

## Typical Use Case

Archive:

- Failed cells
- Empty droplets
- Low-depth WGA reactions

while preserving data.

---

# downsample_merged.sh

## Purpose

Creates multiple downsampled versions of a merged BAM.

The script loops through the following fractions:

```text
10%
20%
30%
40%
50%
60%
70%
80%
90%
```

【7-ce2c08】

## Usage

Single-threaded:

```bash
bash downsample_merged.sh merged_all.bam
```

Multi-threaded:

```bash
bash downsample_merged.sh merged_all.bam 8
```

## Output Directory

```text
downsampled/
```

## Typical Use Cases

Coverage saturation studies:

```text
100%
90%
80%
70%
...
10%
```

Useful for determining:

- Minimum required sequencing depth
- Coverage saturation
- Cost optimization

---

# update_coverage_with_reads.sh

## Purpose

Combines coverage metrics with BAM read counts.

The script:

1. Reads coverage.csv
2. Counts reads in BAM files
3. Matches BAM names to sample names
4. Creates an updated report

【8-74ba70】

## Usage

```bash
bash update_coverage_with_reads.sh
```

You will be prompted for:

```text
Enter the full path of the directory containing BAM files:
```

## Required Inputs

```text
coverage.csv
*.bam
```

must exist in the specified directory.

## Output

```text
coverage_updated.csv
```

Additional column:

```text
reads
```

Example:

| samplename | coverage_30x | reads |
|------------|-------------|--------|
| cell001 | 84.5 | 512345 |
| cell002 | 80.2 | 488112 |

---

# WGA_GiniMedian.R

## Purpose

Calculates WGA uniformity metrics.

Typical outputs include:

```text
Median Coverage
Gini Coefficient
```

These metrics are commonly used to compare:

- PicoPLEX
- PTA
- MDA
- Shasta WGA

libraries.

Lower Gini coefficients indicate more uniform amplification.

---

# pseudobulk_infofile.csv

## Purpose

Defines BAM files used for pseudobulk analysis.

Example entries:

```text
merged_GM05067
merged_GM22601
merged_all
```

Each sample is associated with a specific BAM file path. 【3-a5fc0c】

## Example

```csv
sample,pseudobulk_filepath
merged_GM05067,/path/to/merged_GM05067.bam
merged_GM22601,/path/to/merged_GM22601.bam
merged_all,/path/to/merged_all.bam
```

---

# pseudobulk_infofile - Copy.csv

## Purpose

Template file used for downsampling studies.

Example entries:

```text
merged_01
merged_02
merged_03
...
merged_09
merged_all
```

【2-e765ef】

## Example Workflow

Create multiple pseudobulk BAMs:

```text
merged_01
merged_02
merged_03
...
merged_09
```

then compare coverage performance after downsampling.

---

# Common Examples

## Count reads

```bash
bash list_bam_reads.sh
```

---

## Archive lowest 200 BAMs

```bash
bash move_low_reads_bam.sh ./BAM_files 200
```

---

## Delete lowest 500 BAMs

```bash
bash remove_low_reads.sh 500
```

---

## Generate coverage metrics

```bash
python compile_coverage.py
```

---

## Add read counts to coverage report

```bash
bash update_coverage_with_reads.sh
```

---

## Downsample merged BAM

```bash
bash downsample_merged.sh merged_all.bam 8
```

---

## Generate WGA QC report

```bash
python compile_coverage.py

bash update_coverage_with_reads.sh

Rscript WGA_GiniMedian.R
```

This workflow is useful for evaluating coverage breadth, sequencing depth, amplification uniformity, and overall WGA performance.