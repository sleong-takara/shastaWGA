#!/bin/bash

# Check if samtools is installed
if ! command -v samtools &> /dev/null
then
    echo "samtools could not be found. Please install samtools and try again."
    exit
fi

# List all .bam files in the current directory
bam_files=(*.bam)

# Check if there are any .bam files in the directory
if [ ${#bam_files[@]} -eq 0 ]; then
    echo "No BAM files found in the current directory."
    exit
fi

# Create an associative array to store read counts
declare -A bam_read_counts

# Loop through each BAM file and get the read count
for bam_file in "${bam_files[@]}"; do
    read_count=$(samtools view -@ 16 -c "$bam_file")
    bam_read_counts["$bam_file"]=$read_count
done

# Output file
output_file="bam_read_counts.txt"

# Write sorted BAM files by read count to the output file
for bam_file in "${!bam_read_counts[@]}"; do
    echo "$bam_file ${bam_read_counts[$bam_file]}"
done | sort -k2,2nr > "$output_file"

echo "Read counts have been written to $output_file"
