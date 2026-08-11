#!/bin/bash

#./move_low_reads_bam.sh /path/to/bam/files 266


if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <directory> <num_files_to_remove>"
    exit 1
fi

DIRECTORY=$1
NUM_FILES_TO_REMOVE=$2
ARCHIVE_DIR="$DIRECTORY/archive"

# Ensure samtools is installed
if ! command -v samtools &> /dev/null; then
    echo "samtools could not be found. Please install samtools to use this script."
    exit 1
fi

# Create the archive directory if it does not exist
mkdir -p "$ARCHIVE_DIR"

# Create a temporary file to store read counts
TEMP_FILE=$(mktemp)

# Count reads in each BAM file
for BAM_FILE in "$DIRECTORY"/*.bam; do
    READ_COUNT=$(samtools view -@ 4 -c "$BAM_FILE")
    echo "$READ_COUNT $BAM_FILE" >> "$TEMP_FILE"
done

# Sort the files by read count and move the last N files with the lowest read counts to the archive directory
sort -n "$TEMP_FILE" | head -n "$NUM_FILES_TO_REMOVE" | while read -r COUNT FILE; do
    mv "$FILE" "$ARCHIVE_DIR"
    echo "Moved $FILE with $COUNT reads to archive."
done

# Clean up the temporary file
rm "$TEMP_FILE"
