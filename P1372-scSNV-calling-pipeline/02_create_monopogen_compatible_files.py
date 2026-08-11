#-----------------------------------------------------------------------------------------
# Author: Hima Anbunathan
# Last updated: 2023-Nov-22
# Description: Code creates input files to run Monopogen (step 2 - snv calling workflow)
#-----------------------------------------------------------------------------------------

import argparse
import pandas as pd
import subprocess

def merge_bam(cell_and_cluster_mapping_file, output_filepath=None):
    
    df = pd.read_csv(cell_and_cluster_mapping_file)
    clusters = df['cluster_id'].unique()

    for val in clusters:
        print('iterating through cluster_'+str(val))
        bam_cluster = df.loc[df['cluster_id'] == val, 'cell'].tolist()
        
        bam_dir_path = "00_picoplex_bams"

        cmd = "mkdir -p "+bam_dir_path
        subprocess.run(["mkdir", "-p", bam_dir_path], check=True, text=True)
       
        for item in bam_cluster:
            bam_filepath = df.loc[df['cell'] == item, 'bamfile'].values[0]
            bam_filename = bam_filepath.split('/')[-1]
            print(bam_filename) 
            lncmd = "ln -Tf "+bam_filepath +" $PWD/"+bam_dir_path+"/"+bam_filename
            subprocess.run(lncmd, shell=True, check=True, timeout=5, text=True)

        bamfiles = bam_dir_path+"/*.bam"

        if (output_filepath is None):
            output_bam = 'cluster_id'+str(val)+'_cells_merged.bam'
        else:
            output_bam = output_filepath+'/cluster_id'+str(val)+'_cells_merged.bam' 

        cmd = f"samtools merge {output_bam} {bamfiles}"  

        try:
            print(cmd)
            subprocess.run(cmd, shell=True, check=True)

        except subprocess.CalledProcessError as e:
            print(f"Sub process Error: {e}")
        
        bamindex = index_bam(output_bam)
        print('\n')

        cmd = "rm -rf "+bam_dir_path
        print(cmd)
        subprocess.run(["rm", "-rf", bam_dir_path], check=True, text=True)

    return()


def index_bam(bamfile):
    cmd=f'samtools index {bamfile}'
    try:
        print(cmd)
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Sub process Error: {e}")
    return()


def create_bamlst_file(cell_and_cluster_mapping_file, output_filepath=None):
    df = pd.read_csv(cell_and_cluster_mapping_file)
    clusters = df['cluster_id'].unique()

    samplename = []
    output_bampath = []
    for val in clusters:

        if (output_filepath is None):
            output_filepath = subprocess.run(['pwd'], stdout=subprocess.PIPE, text=True).stdout.strip()
            output_bam = output_filepath+'/cluster_id'+str(val)+'_cells_merged.bam'
        else:
            output_bam = output_filepath+'/cluster_id'+str(val)+'_cells_merged.bam'
            
        samplename.append('cluster_id'+str(val))
        output_bampath.append(output_bam)
        
    out = pd.DataFrame(list(zip(samplename, output_bampath)))
    return(out)


def split_str(value):
    return(value.split('_')[-1])

def get_barcodes(cell_and_cluster_mapping_file):
    df = pd.read_csv(cell_and_cluster_mapping_file)
    df['barcode'] = df['cell']
    df['barcode'] = df['barcode'].str.replace('Pos_Ctrl', 'PosCtrl')
    for index, row in df.iterrows():
        df.at[index, 'barcode'] = split_str(row['barcode'])
    df['barcode'] = df['barcode'] + '-1'
    return(df['barcode'].tolist())

def samtool_count(bam_filepath):
    cmd = f"samtools view -c {bam_filepath}"
    out=subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, text=True).stdout.strip()
    return(out)

def read_counts(cell_and_cluster_mapping_file):
    df = pd.read_csv(cell_and_cluster_mapping_file)
    for index, row in df.iterrows():
        df.at[index, 'cluster'] = samtool_count(df.at[index, 'bamfile'])
    return(df['cluster'].tolist())

def main():
    parser = argparse.ArgumentParser(description='creates bam_lst file for Monopogen', formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=50)) # Create a parser
    parser.add_argument('--cell_and_cluster_mapping_file', required=True, type=str, help='default:all') 
    parser.add_argument('--output_filepath', type=str, help='default:current working directory')
    args = parser.parse_args() 

    merge_bam(args.cell_and_cluster_mapping_file)
    out = create_bamlst_file(args.cell_and_cluster_mapping_file, args.output_filepath)
    out.to_csv('bam.lst', header=False, index=False)

    cell = get_barcodes(args.cell_and_cluster_mapping_file)
    cluster = read_counts(args.cell_and_cluster_mapping_file)
    out = pd.DataFrame(list(zip(cell, cluster)), columns=['cell', 'cluster'])
    out.to_csv('cell_cluster.csv', header=True, index=False)
    
if __name__ == '__main__':
    main()

