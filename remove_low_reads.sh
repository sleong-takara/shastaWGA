#!/bin/bash

#to run: remove_low_reads.sh 500


# Check if the number of files to remove is provided as an argument
if [ -z "$1" ]; then
    echo "Usage: $0 NUM_FILES_TO_REMOVE"
    exit 1
fi

# Get the number of files to remove from the first command-line argument
NUM_FILES_TO_REMOVE=$1

# Directory containing the BAM files
BAM_DIR="./"

# Temporary file to store the read counts
TEMP_FILE="bam_read_counts.txt"

# Ensure the temp file is empty
> $TEMP_FILE

# Loop through each BAM file in the directory and count reads
for BAM_FILE in "$BAM_DIR"/*.bam; do
    # Get the number of reads in the BAM file
    READ_COUNT=$(samtools view -c "$BAM_FILE")
    # Save the read count and file name to the temp file
    echo "$READ_COUNT $BAM_FILE" >> $TEMP_FILE
done

# Sort the files by read count in ascending order and take the last NUM_FILES_TO_REMOVE
FILES_TO_REMOVE=$(sort -n $TEMP_FILE | head -n $NUM_FILES_TO_REMOVE | awk '{print $2}')

# Remove the selected files
for FILE in $FILES_TO_REMOVE; do
    echo "Removing $FILE"
    rm "$FILE"
done

# Clean up the temporary file
rm $TEMP_FILE
