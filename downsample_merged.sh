#!/bin/bash

# Usage: bash downsample_merged.sh merged.bam 4


# Check if input BAM file is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <input_bam> [threads]"
    exit 1
fi

# Define the input BAM file and the number of threads
input_bam="$1"
threads=${2:-1}  # Default to 1 thread if not specified
output_dir="./downsampled"

# Ensure the output directory exists
mkdir -p $output_dir

# Loop over the downsampling fractions from 10% to 90%
for i in {1..9}; do
    fraction="0.$i"
    output_bam="${output_dir}/merged_0${i}.bam"
    
    echo "Downsampling at $((i * 10))% (fraction: $fraction) with $threads thread(s) and saving to $output_bam"
    
    samtools view -b -s $fraction -@ $threads $input_bam > $output_bam
done

echo "Downsampling completed."
