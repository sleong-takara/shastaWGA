#-----------------------------------------------------------------------------------------
# Author: Hima Anbunathan
# Last updated: 2023-Dec-13
# Description: Code creates cell_and_cluster_mapping file (step 1 - snv calling workflow)
#-----------------------------------------------------------------------------------------

# Load dependencies
import numpy
import argparse
import hdbscan
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import pandas as pd
from sklearn.preprocessing import StandardScaler
import umap 
import glob

set_seed=42

def get_filepath(picoplex_bam_dir):
    for name in glob.glob(picoplex_bam_dir):
        return(name)

# create metadata based on copynumber file and well list
def create_metadata(cnv_analyzer_file, picoplex_bam_dir, well_list_file):
    dat = read_file(cnv_analyzer_file)
    dat['sample_name'] = dat.index.values
    lst_cnv_sample_names = dat.index.values.tolist()
    well_df = pd.read_csv(well_list_file, sep='\t')
    well_df['Sample'] = well_df['Sample'].str.replace(' ','_')
    well_df['Sample'] = well_df['Sample'].str.replace('-','_')
    well_df['Barcode'] = well_df['Barcode'].str.replace('+','')
    well_df['wellist_sample_name'] = well_df['Sample'] + '_' + well_df['Barcode']
    meta_df = well_df[well_df['wellist_sample_name'].isin(lst_cnv_sample_names)]
    meta_df = meta_df[['wellist_sample_name','Sample']]
    meta_df = meta_df.rename(columns={'wellist_sample_name':'samples'})
    meta_df = meta_df.rename(columns={'Sample':'cell_type'})
    meta_df['bamfile'] = picoplex_bam_dir + '/' + meta_df['samples'] + '_mkdp_all.bam'
    meta_df.set_index('samples', inplace=True)
    meta_df = meta_df.reindex(index=dat['sample_name'])
    meta_df = meta_df.reset_index()
    print(meta_df.shape)
    return(meta_df)

# umap functionality
def compute_umap_embedding(cnv_analyzer_file, n_neighbors=None, min_dist=None, n_components=None, metric=None):
    u = umap.UMAP(random_state=set_seed, n_neighbors=n_neighbors, min_dist=min_dist, n_components=n_components, metric=metric)
    dat = read_file(cnv_analyzer_file)
    print(dat.shape)
    scaled_data = StandardScaler().fit_transform(dat.values)
    print(scaled_data.shape)    
    embedding = u.fit_transform(scaled_data)
    print('Number of cells/samples in the input *.ccn.csv file = ', embedding.shape[0])
    return(embedding)

def plot_umap(embedding, meta_df, plot_title=None, n_components=None, plot_legend_position=None):
    group = get_sample_lst(meta_df)
    sorted_color_dict = set_to_dict(group)
    print(sorted_color_dict)
    if n_components == 3:
        df = pd.DataFrame(dict(UMAP1=embedding[:,0], UMAP2=embedding[:,1], UMAP3=embedding[:,2], group = group))
        fig = plt.figure()
        fig = fig.add_subplot(111, projection='3d')
        plt.scatter(df['UMAP1'], df['UMAP2'], df['UMAP3'],c=df['group'].map(sorted_color_dict))
        plt.title(plot_title, fontsize=15)
    else:
        df = pd.DataFrame(dict(UMAP1=embedding[:,0], UMAP2=embedding[:,1], group = group))
        plt.scatter(df['UMAP1'], df['UMAP2'], c=df['group'].map(sorted_color_dict), s=3)
        if (len(sorted_color_dict) > 1):
            markers = [plt.Line2D([0,0],[0,0], color=color, marker='o', linestyle='') for color in sorted_color_dict.values()]
            plt.legend(markers, sorted_color_dict.keys(), numpoints=1, loc=plot_legend_position, fontsize="5")
            plt.title(plot_title, fontsize=12)
        else:
            print("Number of legends ==", len(sorted_color_dict))
            plt.title(plot_title, fontsize=12)
    return(plt)


# formats ginkgo output to match <*_ccn.csv> file format
def read_file(cnv_analyzer_file):
    df = format_ginkgo_file(cnv_analyzer_file)
    chr_bin_id = df['chr'].astype(str) +"-"+ df["bin_id"].astype(str)
    df.insert(loc = 1, column = 'chr_bin_id', value = chr_bin_id)
    df = df.drop(columns=['chr', 'bin_id'])
    df = df.set_index('chr_bin_id')
    formatted_df = df.T
    return(formatted_df)

def format_ginkgo_file(ginkgo_segnorm_file):
    df = pd.read_csv(ginkgo_segnorm_file, sep='\t')
    df = df.rename(columns={"CHR": "chr"})
    df['bin_id'] = df["START"].astype(str) + '-' + df["END"].astype(str)
    col = df.pop('bin_id')
    df.insert(1, col.name, col)
    df.columns = df.columns.str.replace(r"_mkd", "", regex=True)
    formatted_df = df.drop(['START', 'END'], axis=1)
    return(formatted_df)

def get_sample_lst(meta_df): 
    print('Number of cells/samples in the metadata file = ', meta_df.shape[0])
    sample_lst=meta_df['cell_type'].tolist()
    sample_lst.sort()
    return(sample_lst)
    
# color scheme for plot legends   
def set_to_dict(sample_lst):
    s=set(sample_lst)
    no_of_colors=len(s)
    colors_lst=["blue", "green", "red", "orange", "grey", "Maroon", "Pink", "Lime", "Teal"]
    colors=[]
    for i in range(no_of_colors):
        colors.append(colors_lst[i])
    keys = list(s)
    keys.sort()
    return {k: v for k, v in zip(keys, colors)}

# Adding clustering component (using HDBSCAN)
def umap_clustering(embedding, meta_df):
    labels = hdbscan.HDBSCAN(min_cluster_size=10, min_samples=2).fit_predict(embedding)
    clusterdf = pd.DataFrame(embedding, columns=['UMAP1', 'UMAP2'])
    clusterdf['cluster_id'] = labels
    clusterdf['sample_name'] = meta_df['sample_name'].tolist()
    print(clusterdf.head())
    # clusterdf.index = dat.T.columns.tolist()
    return(clusterdf)

def plot_clusters(clusterdf):
    plt.clf()
    categories = clusterdf['cluster_id']
    print('categories == '+str(len(categories)))
    colors = ["blue", "green", "red", "orange", "grey", "Maroon", "Pink", "Lime", "Teal", "yellow","aqua"]
    plt.scatter(clusterdf['UMAP1'], clusterdf['UMAP2'], c=clusterdf['cluster_id'], cmap='jet', s=10)
    plt.colorbar(label='legend')
    plt.title('clustering plot', fontsize=12)
    figure_out = plt.gcf()
    return(figure_out)

def output_cell_mapping_file(clusterdf, meta_df):
    merge_df = pd.merge(clusterdf, meta_df, on="sample_name")
    merge_df = merge_df.drop(columns=['UMAP1', 'UMAP2'])
    merge_df.set_index('sample_name', inplace=True)
    merge_df.index.name='cell'
    return(merge_df)

def main():

    parser = argparse.ArgumentParser(description='Generate UMAP plots', formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=50)) # Create a parser
    parser.add_argument('--cnv_analyzer_file', required=True, help='Required: *.ccn.csv file from CNV_analyzer output',nargs='?')
    parser.add_argument('--picoplex_bam_dir', required=True, help='Required: PICOPLEX_RD_BAM_FOLDER',nargs='?')
    parser.add_argument('--well_list_file', required=True, help='Required: WELL_LIST_FILE',nargs='?')
    parser.add_argument('--output_dir', help='output dir')
    parser.add_argument('--n_neighbors', default=15, type=int, help='default:15')
    parser.add_argument('--min_dist', default=0.1, type=int, help='default:0.1') 
    parser.add_argument('--n_components', default=2, type=int, help='default:2')
    parser.add_argument('--metric', default='euclidean', type=str, help='default:Euclidean')
    parser.add_argument('--perform_clustering', default=True, type=bool, help='Performs clustering using HDBSCAN')
    parser.add_argument('--plot_title', default='UMAP plot', type=str, help='default title:UMAP plot')
    parser.add_argument('--plot_legend_position', default='upper right', type=str, help='default legend position')
    parser.add_argument('--figure_file', default='umap_plot.png', type=str, help='default filename:umap_plot.png')
    parser.add_argument('--output_umap_embedding', default=False, type=bool, help='default:False')
    parser.add_argument('--output_umap_embedding_filepath', default='umap_embedding.csv', type=str, help='default:current directory')
    args = parser.parse_args() 

    # run script
    print('set seed for UMAP and clustering = ', str(set_seed))
    embedding = compute_umap_embedding(args.cnv_analyzer_file, args.n_neighbors, args.min_dist, args.n_components, args.metric)
    meta_df = create_metadata(args.cnv_analyzer_file, args.picoplex_bam_dir, args.well_list_file)
    plot_umap(embedding, meta_df, args.plot_title, args.n_components, args.plot_legend_position).savefig(args.figure_file)
    
    
    if(args.perform_clustering == False):
        print('clustering option not selected')
        meta_df.to_csv('cell_and_cluster_mapping_file.csv', index=True)
    else:
        print('clustering option selected')
        df = umap_clustering(embedding, meta_df)
        plot_clusters(df).savefig('clustering.png')
        output_cell_mapping_file(df, meta_df).to_csv('cell_and_cluster_mapping_file.csv', index=True)
    
    if (args.output_umap_embedding == True):
        sampleidentifier = meta_df.iloc[:, [0, 1]]
        sampleidentifier.reset_index(inplace=True)
        print(sampleidentifier.head())
        if (args.n_components == 3):
            print('output umap embedding')
            df = pd.DataFrame(data = embedding, columns = ['UMAP1', 'UMAP2', 'UMAP3'])
            result = pd.concat([sampleidentifier, df], axis=1)
            result.to_csv(args.output_umap_embedding_filepath, index=False)
        else:
            print('output umap embedding')
            df = pd.DataFrame(data = embedding, columns = ['UMAP1', 'UMAP2'])
            result = pd.concat([sampleidentifier, df], axis=1)
            result.to_csv(args.output_umap_embedding_filepath, index=False)
    else:
        print('option to output embedding dataframe not specified') 

if __name__ == '__main__':
    main()