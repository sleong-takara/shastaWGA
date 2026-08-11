#!/bin/bash

# Function to count reads in a BAM file using samtools with 4 threads
count_reads_in_bam() {
    local bam_file=$1
    local count=$(samtools view -@ 4 -c "$bam_file" 2>/dev/null)
    echo "$count"
}

# Get the directory containing BAM files from the user
echo "Enter the full path of the directory containing BAM files:"
read -r directory

# Check if the directory exists
if [ ! -d "$directory" ]; then
    echo "Directory does not exist!"
    exit 1
fi

# Check if coverage.csv exists in the directory
coverage_file="$directory/coverage.csv"
if [ ! -f "$coverage_file" ]; then
    echo "coverage.csv does not exist in the specified directory!"
    exit 1
fi

# Create a copy of coverage.csv named coverage_updated.csv
updated_coverage_file="$directory/coverage_updated.csv"
cp "$coverage_file" "$updated_coverage_file"

# Rename the "samplename" column and remove "_collect_wgs_metrics.txt" suffix
temp_file=$(mktemp)
awk -F',' 'BEGIN {OFS = FS} NR==1 {for (i=1; i<=NF; i++) if ($i == "samplename") col=i} NR>1 {$col = gensub("_collect_wgs_metrics.txt", "", "g", $col)} {print}' "$updated_coverage_file" > "$temp_file"

# Move the modified coverage_updated.csv back to the original file
mv "$temp_file" "$updated_coverage_file"

# Read the modified coverage_updated.csv to get the list of sample names
declare -A sample_read_counts

# Iterate over BAM files in the directory
for bam_file in "$directory"/*.bam; do
    if [ -e "$bam_file" ]; then
        # Get the base name of the BAM file (without the .bam extension)
        bam_basename=$(basename "$bam_file" .bam)
        # Count the number of reads in the BAM file
        read_count=$(count_reads_in_bam "$bam_file")
        # Store the read count in the associative array
        sample_read_counts["$bam_basename"]=$read_count
    fi
done

# Add the read counts to the coverage_updated.csv, matching the "samplename" column
temp_file=$(mktemp)
awk -F',' -v OFS=',' -v counts="${sample_read_counts[*]}" '
BEGIN {
    n = split(counts, countArray, " ");
    for (i = 1; i <= n; i++) {
        split(countArray[i], pair, "=");
        read_counts[pair[1]] = pair[2];
    }
}
NR == 1 {
    print $0, "reads"
}
NR > 1 {
    print $0, read_counts[$1]
}
' "$updated_coverage_file" > "$temp_file"

# Move the updated file back to the coverage_updated.csv
mv "$temp_file" "$updated_coverage_file"

echo "Updated coverage.csv and saved as coverage_updated.csv with read counts."
