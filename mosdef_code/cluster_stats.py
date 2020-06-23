# Plots some statistics about each cluser
# plot_similarity can plot the similarities between each pair of galaxies
# in a cluster and each galaxy and its SED

import sys
import os
import string
import numpy as np
import pandas as pd
from astropy.io import ascii
from astropy.io import fits
from read_data import mosdef_df
from mosdef_obj_data_funcs import read_sed
import matplotlib.pyplot as plt
import initialize_mosdef_dirs as imd


def plot_similarity(composite_sed=False):
    """Create a histogram of similarities between individual galaxies in each cluser

    Parameters:
    composite_sed (boolean): Set to True if you want to compare to the SED rather then to each other

    Returns:
    """
    save_dir = imd.cluster_dir + '/cluster_stats/similarities/'

    similarity_matrix = ascii.read(
        imd.cluster_dir + 'similarity_matrix.csv').to_pandas().to_numpy()
    zobjs = ascii.read(
        imd.cluster_dir + 'zobjs_clustered.csv', data_start=1).to_pandas()

    num_clusters = np.max(zobjs['cluster_num']) + 1

    for groupID in range(num_clusters):
        print(f'Computing Similarity for Cluster {groupID}')
        galaxies = zobjs[zobjs['cluster_num'] == groupID]
        similarities = []
        num_galaxies = len(galaxies)
        for i in range(num_galaxies):
            for j in range(num_galaxies - i):
                if i != j:
                    similarities.append(
                        similarity_matrix[galaxies.iloc[i]['new_index'], galaxies.iloc[j]['new_index']])

        axisfont = 14
        ticksize = 12
        ticks = 8
        titlefont = 24
        legendfont = 14
        textfont = 16

        fig, ax = plt.subplots(figsize=(8, 7))

        bins = np.arange(0, 1.05, 0.05)
        ax.hist(similarities, bins=bins, color='black')

        ax.set_xlim(-0.05, 1.05)
        ax.set_xlabel('Similarity', fontsize=axisfont)
        ax.set_ylabel('Number of pairs', fontsize=axisfont)
        ax.tick_params(labelsize=ticksize, size=ticks)
        fig.savefig(save_dir + f'{groupID}_similarity')
        plt.close()
