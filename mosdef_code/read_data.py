# Functions to open the data tables in mosdef and store them it into
# pandas dataframes

import sys
import os
import string
import numpy as np
import pandas as pd
from astropy.io import ascii
from astropy.io import fits
from tabulate import tabulate
from astropy.table import Table
import initialize_mosdef_dirs as imd


def read_file(data_file):
    """Reads the fits file into a pandas table

    Parameters:
    data_file (string): location of the file to read


    Returns:
    df (pd.DataFrame): pandas dataframe of the fits table
    """
    data = Table.read(data_file, format='fits')
    df = data.to_pandas()
    return df


mosdef_df = read_file(imd.loc_mosdef0d)
# The 'FIELD' column is in bytes format - here we convert to a string
mosdef_df['FIELD_STR'] = [mosdef_df.iloc[i]['FIELD'].decode(
    "utf-8").rstrip() for i in range(len(mosdef_df))]
linemeas_df = read_file(imd.mosdef_dir + '/Mosdef_cats/linemeas_latest.fits')
sfrs_df = read_file(imd.loc_sfrs_latest)
agnflag_df = read_file(imd.mosdef_dir + '/Mosdef_cats/agnflag_latest.fits')
metal_df = read_file(imd.mosdef_dir + '/Mosdef_cats/mosdef_metallicity_latest.fits')



    

