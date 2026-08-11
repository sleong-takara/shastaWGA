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

def get_bamfile(pseudobulk_infofile):
    df = pd.read_csv(pseudobulk_infofile)
    merged_bamlist = df['pseudobulk_filepath'].unique().tolist()
    return(merged_bamlist)

def run_gatk_per_bam(args):
    bamfile_path, reference_genome = args
    output_metrics=bamfile_path.split('/')[-1].split('.bam')[0]+'_collect_wgs_metrics.txt'
    output_plot=bamfile_path.split('/')[-1].split('.bam')[0]+'_collect_wgs_metrics.pdf'
    cmd=f'gatk CollectWgsMetricsWithNonZeroCoverage I={bamfile_path} O={output_metrics} CHART={output_plot} R={reference_genome}'

    try:
        print(cmd)
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Sub process Error: {e}")
    return()

def summary_table(WGS_METRIC_FOLDER):
    coverage=[]
    samplename=[]
    for filename in os.listdir(WGS_METRIC_FOLDER):
        if filename.endswith("_collect_wgs_metrics.txt"):
            with open(os.path.join(WGS_METRIC_FOLDER, filename), "r") as file:
                for line in file:
                    if line.startswith("WHOLE_GENOME"):
                        PCT_1X=line.strip().split('\t')[14]
                        samplename.append(filename)
                        coverage.append(PCT_1X)

    data = {'samplename' : samplename, 'coverage' : coverage}
    df = pd.DataFrame(data)
    return(df)

def main():
    parser = argparse.ArgumentParser(description='computes coverage for pseudobam file', formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=50)) # Create a parser
    parser.add_argument('--pseudobulk_infofile', required=True, type=str, help='default:specify csv file with pseudobam filepaths') 
    parser.add_argument('--reference_genome', required=True, type=str, help='default:genome fasta file used to generate bam') 
    parser.add_argument('--num_process', default=5, help='default:genome fasta file used to generate bam')
    args = parser.parse_args() 

    # Argument for each process
    bamlist = get_bamfile(args.pseudobulk_infofile)

    ref_genome = args.reference_genome

    print('Number of bamfiles to run = '+str(len(bamlist)))
    print('Number of processes specified = '+str(args.num_process))

    if (len(bamlist) == 0):
        
        print('check input file: no BAM file found')

    if (len(bamlist) < args.num_process):

        print("Number of process should be less than number of bamfiles, specify the --num_process argument")
    
    else:

        print('Number of processes used = '+str(args.num_process))

        tasks = []

        for i in range(0,len(bamlist),args.num_process):
            tasks = [(bamlist[j], ref_genome) for j in range(i, i+args.num_process)]
            with Pool(processes=args.num_process) as pool:
                pool.map(run_gatk_per_bam, tasks)
            pool.close()
            pool.join

    path=os.getcwd()
    df = summary_table(path)
    df.to_csv('coverage.csv',index=False)

    
if __name__ == '__main__':
    main()
