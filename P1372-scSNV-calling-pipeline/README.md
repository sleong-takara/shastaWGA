# P1372-snv-calling-pipeline
P1372-snv-calling workflow for gate meeting

Current snv calling workflow comprise 3 steps:
Required input (starting) files: GINKGO SegCopy file, PICOPLEX bam directory with bam files, WELL_LIST 
1) Run UMAP and clustering analysis to create cell_and_mapping_file
2) Create monopogen compatible files
3) Run Monopogen

