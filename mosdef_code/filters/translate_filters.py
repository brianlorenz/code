# Uses the .translate files to create filter lists for each of the catalogs

import sys
import os
import string
import numpy as np
import pandas as pd
import re
from astropy.io import ascii
import initialize_mosdef_dirs as imd


# Location of folders for the surveys is in imd

# Dictionary of locations for the translate files
translate_dict = {
    'AEGIS': imd.loc_3DHST + 'AEGIS/aegis_3dhst.v4.1.translate',
    'GOODS-S': imd.loc_ZFOURGE + 'cdfs/cdfs.v1.6.9.translate',
    'COSMOS': imd.loc_ZFOURGE + 'cosmos/cosmos.v1.3.6.translate',
    'GOODS-N': imd.loc_3DHST + 'GOODS-N/GOODS-N_3dhst.v4.1.translate',
    'UDS': imd.loc_ZFOURGE + 'uds/uds.v1.5.8.translate',
    'GOODS-S_3DHST': imd.loc_3DHST + 'GOODS-S/goodss_3dhst.v4.1.translate',
    'COSMOS_3DHST': imd.loc_3DHST + 'COSMOS/cosmos_3dhst.v4.1.translate',
    'UDS_3DHST': imd.loc_3DHST + 'UDS/uds_3dhst.v4.1.translate'
}

'''
Ran this in unix to create the overview file
> more FILTER.RES.latest | grep lambda_c. > overview
> more overview
A few lines (308-313) gave issues with units of um. Manually changed these to e+04.
'''

# Location of the overview file
loc_overview = '/Users/brianlorenz/code/mosdef_code/filters/catalog_filters/overview'

df = pd.read_csv(loc_overview, header=None, sep='\n')
breakpoint()
df2 = df


df = df[0].str.split('_c=', expand=True)
df = df[1].str.split(' AB', expand=True)


# These are the peak wavelengths we want
filter_df = pd.to_numeric(df[0])
'''filter_df = pd.DataFrame(zip(filter_list, centers), columns=[
    'filter_num', 'peak_wavelength'])
'''
filter_df.to_csv('catalog_filters/filter_df.csv')

# AEGIS


def make_filter_csv(cat):
    """Uses the translate file to produce a catalog with the appropriate filters

    Parameters:
    cat (string): name of the catalog - eg 'AEGIS', 'GOODS-N'


    Returns:
    Nothing, but saves the dataframe as a csv to be read by other programs
    """
    # Read in the translate file
    translate_df = ascii.read(translate_dict[cat], data_start=0).to_pandas()
    translate_df.columns = ['filter_name', 'filter_num']
    # Selecting only the columfs with F - all the others start with E (error)
    translate_df = translate_df[translate_df['filter_name'].str.startswith(
        'f')]
    # Drops the F, leaving just the numbers
    translate_df['filter_num'] = translate_df.filter_num.str.replace('F', '')
    # Reset the indexing
    translate_df.reset_index(drop=True, inplace=True)
    # Have to subtract 1 since the catalog is 1 indexed and python uses 0-index
    peak_waves = [filter_df[filter_df.index ==
                            (int(translate_df['filter_num'].iloc[i]) - 1)] for i in range(len(translate_df))]
    # Change data type to float
    peak_waves = [float(i) for i in peak_waves]
    peak_waves_df = pd.DataFrame(peak_waves, columns=['peak_wavelength'])
    filter_csv_df = translate_df.merge(
        peak_waves_df, left_index=True, right_index=True)
    # Save the dataframe
    filter_csv_df.to_csv('catalog_filters/' + cat +
                         '_filterlist.csv', index=False)


catalogs = ['AEGIS', 'COSMOS', 'GOODS-N', 'GOODS-S',
            'UDS', 'GOODS-S_3DHST', 'UDS_3DHST', 'COSMOS_3DHST']
[make_filter_csv(cat) for cat in catalogs]
