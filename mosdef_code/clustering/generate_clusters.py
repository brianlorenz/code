import initialize_mosdef_dirs as imd
from query_funcs import get_zobjs
from axis_ratio_funcs import read_interp_axis_ratio
from emission_measurements import read_emission_df
from interpolate import gen_all_seds
from cross_correlate import correlate_all_seds
from clustering import cluster_seds
from astropy.io import ascii
import numpy as np
import matplotlib.pyplot as plt
import time

def generate_clusters(n_clusters, stop_to_eval=False, skip_slow_steps=False):
    """Main method that will generate all the clusters from scratch
    
    Parameters: 
    stop_to_eval(boolean): Set to True to pause and make a plot of eigenvalues
    skip_slow_steps(boolean): Set to True to skip over making mock seds and cross_correlating
    
    """
    # Prepare the directories
    imd.reset_cluster_dirs(imd.cluster_dir)
    imd.reset_sed_dirs(imd.mosdef_dir)

    # Prepare the galaxies dataframes
    filter_gal_df()
    gal_df = read_filtered_gal_df()
    zobjs = [(gal_df['field'].iloc[i], gal_df['v4id'].iloc[i])
             for i in range(len(gal_df))]
    
    # Generate the mock sed csvs
    if skip_slow_steps==False:
        gen_all_seds(zobjs)

    # Cross-correlate the mock seds
    if skip_slow_steps==False:
        correlate_all_seds(zobjs)
    affinity_matrix = ascii.read(imd.cluster_dir + '/similarity_matrix.csv').to_pandas().to_numpy()

    # Evaluate how many clusters to make
    if stop_to_eval==True:
        eigenvals, eignvectors = np.linalg.eig(affinity_matrix)
        x_axis = np.arange(1, len(eigenvals)+1, 1)
        plt.plot(x_axis, eigenvals, ls='-', marker='o', color='black')
        plt.show()
    
    # Make the clusters
    if skip_slow_steps==False:
        cluster_seds(n_clusters)

    # Make dataframes for each cluster with galaxy properties
    make_cluster_dfs(n_clusters, gal_df)



    


    

def make_cluster_dfs(n_clusters, gal_df):
    """Make dataframes that contain properties for the individual galaxies in each cluster
    
    Parameters:
    n_clusters(int): Number of clusters
    gal_df (pd.DataFrame): Dataframe of galaxies that were used for clustering

    """
    imd.check_and_make_dir(imd.cluster_indiv_dfs_dir)
    zobjs_clusters = ascii.read(imd.cluster_dir + '/zobjs_clustered.csv').to_pandas()

    for group_num in range(n_clusters):
        group_members_df = zobjs_clusters[zobjs_clusters['cluster_num']==group_num]
        group_members_df = group_members_df.drop(['original_zobjs_index'], axis=1)
        group_gal_df = group_members_df.merge(gal_df, on=['field', 'v4id'])
        group_gal_df.to_csv(imd.cluster_indiv_dfs_dir + f'/{group_num}_cluster_df.csv', index=False)


def filter_gal_df():
    """Brings together all data sources into a single dataframe for easy access"""
    gal_df = read_interp_axis_ratio()

    #Filter out objects that are flagged as optical AGN in MOSDEF (see readme)
    gal_df = gal_df[gal_df['agn_flag'] < 4]

    #Filter out objects that don't have a spectroscopic redshift
    gal_df = gal_df[gal_df['z_qual_flag'] == 7]

    gal_df.to_csv(imd.loc_filtered_gal_df, index=False)

def read_filtered_gal_df():
    gal_df = ascii.read(imd.loc_filtered_gal_df).to_pandas()
    return gal_df




generate_clusters(23, stop_to_eval=False, skip_slow_steps=True)