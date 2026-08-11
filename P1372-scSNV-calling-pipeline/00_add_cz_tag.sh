#!/bin/bash
# -------------------------------------------
# Code to Modify BAM files to add the tags
# Author: Hima Anbunathan
# Date last updated: 24 Oct 2023
# -------------------------------------------


#------------------
# Usage
#------------------
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <bamfiles_from_picoplex> <output_dir>"
    exit 1
fi

input_dir="$1"
output_dir="$2"

TEMP_SAM=$output_dir"/temp.sam"
CBZ=$output_dir"/CBZ"

HEADER=$output_dir"/header_toadd.sam"
MODIFIED_SAM=$output_dir"temp.with-CBZ.sam"

echo $TEMP_SAM
echo $CBZ
echo $HEADER
echo $MODIFIED_SAM

mkdir -p "$output_dir"

# modify each files in the directory
for INPUT_BAM in "$input_dir"/*.bam; do
    echo "$INPUT_BAM"
    input_bam=$(basename "$INPUT_BAM")
    name="${input_bam%????}"
    output_bam="$name.bam"

    # Extract Barcodes and add CBZ
    samtools view "$INPUT_BAM" | cut -f1 | cut -f2 -d_ | sed -E 's/(.*)/CB:Z:\1-1/' > $CBZ

    # convert BAM to SAM
    samtools view $INPUT_BAM > $TEMP_SAM 

    # Add the CBZ barcode tag to SAM file
    paste $TEMP_SAM $CBZ > $MODIFIED_SAM

    # Extract header info from BAM
    samtools view -H $INPUT_BAM > $HEADER

    # Add header to SAM file
    cat $MODIFIED_SAM >> $HEADER

    # Convert SAM to BAM
    samtools view -bS $HEADER > "$output_dir/$output_bam"

    # Index BAM
    samtools index "$output_dir/$output_bam"

    # Delete temp files
    rm $TEMP_SAM
    rm $MODIFIED_SAM
    rm $HEADER
    rm $CBZ

done
