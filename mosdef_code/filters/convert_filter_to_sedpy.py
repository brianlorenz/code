# run convert_filter_to_sedpy.py
# '/Users/brianlorenz/mosdef/composite_sed_csvs/composite_filter_csvs/0_filter_csvs/'

import sys
import os
import string
import numpy as np
import pandas as pd
from astropy.io import ascii
from astropy.io import fits
from read_data import mosdef_df
from mosdef_obj_data_funcs import get_mosdef_obj, read_sed
import matplotlib.pyplot as plt
from sedpy import observate
import initialize_mosdef_dirs as imd


# e.g. target_folder =
# '/Users/brianlorenz/mosdef/composite_sed_csvs/composite_filter_csvs/0_filter_csvs/'


def find_median_redshift(composite_group):
    """Finds the median redshift within a composite sed group

    Parameters:
    composite_group (int): number of the group to convert, used to find median z

    Returns:
    median_z (float): median redshift in that group

    """
    files_list = os.listdir(f'/Users/brianlorenz/mosdef/Clustering/{composite_group}')
    names_list = [file[:-9] for file in files_list]
    z_list = []
    for name in names_list:
        try:
            z = ascii.read(f'/Users/brianlorenz/mosdef/sed_csvs/{name}_sed.csv').to_pandas()['Z_MOSFIRE'].iloc[0]
        except FileNotFoundError:
            z = ascii.read(f'/Users/brianlorenz/mosdef/sed_csvs/{name}_3DHST_sed.csv').to_pandas()['Z_MOSFIRE'].iloc[0]
        z_list.append(z)
    median_z = np.median(z_list)
    return median_z


def to_median_redshift(wavelength, median_z):
    """Converts wavelength array to the median redshift of the sample

    Parameters:
    wavelength (array): wavelength values to convert
    median_z (int): redshift to change the wavelength by

    Returns:
    wavelength_red (array): redshifted wavelength

    """

    wavelength_red = wavelength * (1 + median_z)
    return wavelength_red


def de_median_redshift(wavelength, median_z):
    """De-redshifts the same way as above

    Parameters:
    wavelength (array): wavelength values to convert
    median_z (int): redshift to change the wavelength by

    Returns:
    wavelength_red (array): redshifted wavelength

    """

    wavelength_red = wavelength / (1 + median_z)
    return wavelength_red


def convert_filters_to_sedpy(target_folder):
    """Converts every filter csv in the target folder into a style readable by sedpy

    Parameters:
    target_folder (str) - location of folder containing filter points

    """

    # Figure out which files  in the folder are csv filters:
    filt_files = [file for file in os.listdir(target_folder) if '.csv' in file]

    # Loop through files one at a time
    for file in filt_files:
        print(f'Converting {file}')
        # Read the wavelength/transmisison data
        data = ascii.read(target_folder + file).to_pandas()
        # Find the range that we care about, only the nonzero values
        nonzero_points = np.array(data[data['transmission'] > 0].index)
        # Add 2 points on either side to serve as zeroes
        prepend_val = nonzero_points[0] - 2
        append_val = nonzero_points[-1] + 2
        if prepend_val >= 0:
            nonzero_points = np.insert(
                nonzero_points, 0, [prepend_val, prepend_val + 1])
        if append_val <= data.index[-1]:
            nonzero_points = np.append(
                nonzero_points, [append_val - 1, append_val])

        # Append zeroes to the file number if they are less than 5 long
        new_name = append_zeros_to_filtname(file)

        data = data.iloc[nonzero_points]
        data.to_csv(target_folder + new_name.replace('.csv', '.par'),
                    index=False, sep=' ', header=False)

        # Redshift to the medain redshift of the group
        group_num = int(target_folder[67:-13])
        median_z = find_median_redshift(group_num)
        data['rest_wavelength'] = to_median_redshift(
            data['rest_wavelength'], median_z)
        data.to_csv(target_folder + new_name.replace('.csv', '_red.par'),
                    index=False, sep=' ', header=False)


def convert_multiple_folders():
    for i in range(0, 29):
        target_folder = f'/Users/brianlorenz/mosdef/composite_sed_csvs/composite_filter_csvs/{i}_filter_csvs/'
        convert_filters_to_sedpy(target_folder)


def get_filt_list(target_folder):
    """Uses sedpy to read in a list of filters when given a folder that contains them

    Parameters:
    target_folder (str) - location of folder containing sedpy filter .par files

    """
    filt_files = [file.replace('.par', '') for file in os.listdir(
        target_folder) if '_red.par' in file]
    filt_files.sort()
    filt_list = observate.load_filters(filt_files, directory=target_folder)
    return filt_list


def append_zeros_to_filtname(filtname):
    """Adds zeros to standardize the size of all filternames

    Parameters:
    filtname (str) - name of the filter file

    Returns:
    filtname (str) - name of the filter file, possibly now with zeroes inserted

    """
    while len(filtname) < 15:
        filtname = filtname[:6] + '0' + filtname[6:]
    return filtname