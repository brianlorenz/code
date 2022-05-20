# Functions that deal with reading and manipulating the axis ratio data

import sys
import os
import string
import numpy as np
import pandas as pd
from astropy.io import ascii
from astropy.io import fits
from read_data import mosdef_df
from mosdef_obj_data_funcs import read_sed, read_mock_sed, get_mosdef_obj, read_composite_sed
from filter_response import lines, overview, get_index, get_filter_response
import matplotlib.pyplot as plt
from scipy import interpolate
import scipy.integrate as integrate
from query_funcs import get_zobjs, get_zobjs_sort_nodup
import initialize_mosdef_dirs as imd
import cluster_data_funcs as cdf
from save_counts import save_count
from spectra_funcs import check_line_coverage
import stat
import time



def make_axis_ratio_catalogs():
    '''Makes the galfit_data.csv file that is used for all of our objects

    Parameters:

    Returns:
    '''

    field_names = ['AEGIS', 'COSMOS', 'GOODS-N', 'GOODS-S', 'UDS']
    cat_names = os.listdir(imd.mosdef_dir + '/axis_ratio_data/AEGIS/')

    zobjs = get_zobjs_sort_nodup()

    for cat_name in cat_names:
        cat_dfs = [ascii.read(imd.mosdef_dir + f'/axis_ratio_data/{field}/' +
                              cat_name).to_pandas() for field in field_names]
        for i in range(len(cat_dfs)):
            cat_dfs[i]['FIELD'] = field_names[i]
        rows = []
        for obj in zobjs:
            field = obj[0]
            v4id = obj[1]
            print(f'Finding Match for {field}, {v4id}')
            mosdef_obj = get_mosdef_obj(field, v4id)
            cat_idx = field_names.index(field)
            cat_df = cat_dfs[cat_idx]
            obj_row = cat_df[cat_df['NUMBER'] == v4id]
            ra_diff = obj_row['RA'] - mosdef_obj['RA']
            dec_diff = obj_row['DEC'] - mosdef_obj['DEC']
            if (ra_diff + dec_diff).iloc[0] > 0.01:
                sys.exit(f'ERROR! WRONG MATCH ON OBJECT FOR {field}, {v4id}')
            rows.append(obj_row)
        final_df = pd.concat(rows)
        final_df.to_csv(
            imd.mosdef_dir + '/axis_ratio_data/Merged_catalogs/mosdef_' + cat_name[:-3] + 'csv', index=False)


def read_axis_ratio(filt, objs):
    '''Gets the axis ratio for a particular object or list of objects

    Parameters:
    filt (int): Filter to read, either 125, 140, or 160
    objs (list): list of tuples of the form (field, v4id) to get the axis ratios for

    Returns:
    final_df (pd.DataFrame): Dataframe with the objects in order, containing axis ratios and other info from galfit
    '''
    ar_cat = ascii.read(imd.mosdef_dir + '/axis_ratio_data/Merged_catalogs/' + f'mosdef_F{filt}W_galfit_v4.0.csv').to_pandas()
    ar_cat = ar_cat.rename(
        columns={'NUMBER': 'v4id', 'q': 'axis_ratio', 'dq': 'err_axis_ratio'})

    rows = []
    for obj in objs:
        field = obj[0]
        v4id = obj[1]
        cat_obj = ar_cat[np.logical_and(
            ar_cat['v4id'] == v4id, ar_cat['FIELD'] == field)]
        rows.append(cat_obj)
    final_df = pd.concat(rows)
    return final_df


def interpolate_axis_ratio():
    '''Use the redshift of each object to make a catalog of what the axis ratio would be at 5000 angstroms

    Parameters:

    Returns:
    '''
    zobjs = get_zobjs_sort_nodup()
    F125_df = read_axis_ratio(125, zobjs)
    F140_df = read_axis_ratio(140, zobjs)
    F160_df = read_axis_ratio(160, zobjs)
    F125_df[['F125_axis_ratio', 'F125_err_axis_ratio']
            ] = F125_df[['axis_ratio', 'err_axis_ratio']]
    F140_df[['F140_axis_ratio', 'F140_err_axis_ratio']
            ] = F140_df[['axis_ratio', 'err_axis_ratio']]
    F160_df[['F160_axis_ratio', 'F160_err_axis_ratio']
            ] = F160_df[['axis_ratio', 'err_axis_ratio']]
    all_axis_ratios_df = pd.concat([F125_df[['F125_axis_ratio', 'F125_err_axis_ratio']], F140_df[
                                   ['F140_axis_ratio', 'F140_err_axis_ratio']]], axis=1)
    all_axis_ratios_df = pd.concat([all_axis_ratios_df, F160_df[
                                   ['F160_axis_ratio', 'F160_err_axis_ratio']]], axis=1)
    zs = []
    fields = []
    v4ids = []
    for obj in zobjs:
        mosdef_obj = get_mosdef_obj(obj[0], obj[1])
        zs.append(mosdef_obj['Z_MOSFIRE'])
        fields.append(obj[0])
        v4ids.append(obj[1])
    all_axis_ratios_df['Z_MOSFIRE'] = zs

    # If 5000 angstrom is outside of the range of observations, use the closest measurement
    # If 5000 is in the range, interpolate
    # DOESNT HANDLE NEGATIVE VALUES WELL
    # NOT SURE WHAT TO DO WITH ERRORS. IS THIS EVEN GOOD? SHOULD I IGNORE F140
    use_ratios = []
    use_errors = []
    # Now ignores F140
    for i in range(len(all_axis_ratios_df)):
        F125W_peak = 12471.0
        #F140W_peak = 13924.0
        F160W_peak = 15396.0
        peaks = [F125W_peak, F160W_peak]  # F140W_peak,
        rest_waves = np.array([peak / (1 + all_axis_ratios_df.iloc[i]['Z_MOSFIRE'])
                               for peak in peaks])
        filters = ['125', '160']  # '140',
        axis_ratios = np.array([all_axis_ratios_df.iloc[i][f'F{j}_axis_ratio'] for j in filters])
        axis_errors = np.array([all_axis_ratios_df.iloc[i][f'F{j}_err_axis_ratio'] for j in filters])
        good_ratios = [ratio > -0.1 for ratio in axis_ratios]
        if len(axis_ratios[good_ratios]) == 1:
            use_ratio = axis_ratios[good_ratios]
            use_error = axis_errors[good_ratios]
            use_ratios.append(float(use_ratio))
            use_errors.append(float(use_error))
            continue
        if len(axis_ratios[good_ratios]) == 0:
            use_ratio = -999.0
            use_error = -999.0
            use_ratios.append(float(use_ratio))
            use_errors.append(float(use_error))
            continue
        axis_interp = interpolate.interp1d(rest_waves[good_ratios], axis_ratios[good_ratios], fill_value=(
            axis_ratios[good_ratios][0], axis_ratios[good_ratios][-1]), bounds_error=False)
        err_interp = interpolate.interp1d(rest_waves[good_ratios], axis_errors[good_ratios], fill_value=(
            axis_errors[good_ratios][0], axis_errors[good_ratios][-1]), bounds_error=False)
        use_ratio = axis_interp(5000)
        use_error = err_interp(5000)
        use_ratios.append(float(use_ratio))
        use_errors.append(float(use_error))
    all_axis_ratios_df['use_ratio'] = use_ratios
    all_axis_ratios_df['err_use_ratio'] = use_errors
    all_axis_ratios_df['field'] = fields
    all_axis_ratios_df['v4id'] = v4ids
    all_axis_ratios_df.to_csv(
        imd.mosdef_dir + '/axis_ratio_data/Merged_catalogs/mosdef_all_cats.csv', index=False)


def read_interp_axis_ratio():
    merged_ar_df = ascii.read(imd.mosdef_dir +
                              '/axis_ratio_data/Merged_catalogs/mosdef_all_cats_v2.csv').to_pandas()
    return merged_ar_df

def filter_ar_df(ar_df, return_std_ar=False):
    """Removes any of the unwanted objects in our analysis, such as AGN or those with bad halpha detections
    
    Parameters:
    ar_df (pd.DataFrame): Axis ratio dataframe to filter down
    return_std_ar (boolead): Set to true to return the standard deviation of the axis ratio differencee as well as ar_df. Will not filter tohe bad axis ratios
    """
    # Remove objects with greater than 0.1 error
    # ar_df = ar_df[ar_df['err_use_ratio'] < 0.1]

    #Count the total number of objects at the beginning and end
    total_num_start = len(ar_df)

    #For counting purposes
    z_qual_bad = ar_df['z_qual_flag'] != 7
    save_count(ar_df[z_qual_bad], 'z_qual_bad', 'z_qual flag from mosdef')
    #Remove low quality galaxies
    ar_df = ar_df[ar_df['z_qual_flag'] == 7]
    
    #For counting purposes
    AGN = ar_df['agn_flag'] != 0
    save_count(ar_df[AGN], 'agn', 'AGN flag from mosdef')
    # Remove AGN
    ar_df = ar_df[ar_df['agn_flag'] == 0]
    
    #For counting purposes
    bad_ar_flag = ar_df['axis_ratio_flag'] == -999
    save_count(ar_df[bad_ar_flag], 'axis_ratio_bad_ar_flag', 'F125 or F160 is not detected')
    # Remove objects flagged for axis ratio inconsistencies (1 is F160-F125 > std, and -999 has measurements missing)
    ar_df = ar_df[ar_df['axis_ratio_flag'] != -999]




    
    #For counting purposes
    ha_bad = ar_df['ha_detflag_sfr'] == -999
    save_count(ar_df[ha_bad], 'ha_negative_flux', 'Halpha not covered')
    ar_df = ar_df[ar_df['ha_detflag_sfr'] != -999]

    hb_bad = ar_df['hb_detflag_sfr'] == -999
    save_count(ar_df[hb_bad], 'hb_negative_flux', 'Hbeta not covered')
    # Remove objects wiithout ha/hb detections
    ar_df = ar_df[ar_df['hb_detflag_sfr']!= -999]

    #For counting purposes
    ha_SN_low = (ar_df['ha_flux'] / ar_df['err_ha_flux']) <= 3
    save_count(ar_df[ha_SN_low], 'ha_SN_low', 'Halpha Signal/Noise less or equal 3')
    # Add filtering for Halpha S/N,
    ar_df = ar_df[(ar_df['ha_flux'] / ar_df['err_ha_flux']) > 3]
    
   


    # #For counting purposes
    # sfr_bad = ar_df['sfr'] <= 0
    # save_count(ar_df[sfr_bad], 'sfr_bad', 'no measured sfr')
    # # Remove anything without a measured sfr 
    # ar_df = ar_df[ar_df['sfr'] > 0]


    #For counting purposes
    mass_bad = ar_df['log_mass'] <= 0
    save_count(ar_df[mass_bad], 'mass_bad', 'no measured mass')
    # Remove anything without a measured mass 
    ar_df = ar_df[ar_df['log_mass'] > 0]

    #For counting purposes
    mass_out = np.logical_or(ar_df['log_mass'] <= 9.0, ar_df['log_mass'] >= 11.00)
    save_count(ar_df[mass_out], 'mass_out_of_range', 'mass out of range')
    # Remove anything outside of our mass limits
    ar_df = ar_df[np.logical_not(mass_out)]


    # Compute the difference and standard devaition
    ar_diff = ar_df['F160_axis_ratio'] - ar_df['F125_axis_ratio']
    std_ar_diff = np.std(ar_diff)

    if return_std_ar==True:
        print('Stopping early and returning')
        return ar_df, std_ar_diff

    # Flag the galaixes greater than 2 sigma
    above_sigma = ar_diff > 2*std_ar_diff
    below_sigma = ar_diff < -2*std_ar_diff
    flagged_gals = np.logical_or(above_sigma, below_sigma)
    idxs = ar_diff[flagged_gals].index
    ar_df.loc[idxs, 'axis_ratio_flag'] = 2
    
    # too_diff_ar = ar_df['axis_ratio_flag'] == 2
    # save_count(ar_df[too_diff_ar], 'axis_ratio_ar_too_diff', 'F125 and F160 dont agree well')
    # ar_df = ar_df[ar_df['axis_ratio_flag'] != 2]

    # get all the mosdef objs, going to be used for checking coverage
    mosdef_objs = [get_mosdef_obj(ar_df.iloc[j]['field'], ar_df.iloc[j]['v4id']) for j in range(len(ar_df))]
    # Filter all galaxies to make sure that they have both emission lines covered
    before_cover = len(ar_df)
    coverage_list = [
        ('Halpha', 6564.61),
        ('Hbeta', 4862.68)
    ]
    covered = [check_line_coverage(mosdef_obj, coverage_list) for mosdef_obj in mosdef_objs]
    ar_df = ar_df[covered]
    after_cover = len(ar_df)
    print(f'Removed {before_cover - after_cover} galaxies from line coverage')

    total_num_end = len(ar_df)
    total_removed = total_num_start - total_num_end
    print(f'Removed {total_removed} galaxies in total')
    print(f'There are {total_num_end} galaxies remaining')
    
    ar_df.to_csv(imd.mosdef_dir + '/axis_ratio_data/Merged_catalogs/filtered_ar_df.csv', index=False)

    return ar_df

def read_filtered_ar_df():
    """Reads the output form the above function that filters the ar_df
    
    """
    ar_path = imd.mosdef_dir + '/axis_ratio_data/Merged_catalogs/filtered_ar_df.csv'
    ar_df = ascii.read(ar_path).to_pandas()

    fileStatsObj = os.stat(ar_path)
    modificationTime = time.ctime(fileStatsObj[stat.ST_MTIME])
    print("Last Filtered ar_df: ", modificationTime)
    return ar_df

# ar_df = read_interp_axis_ratio()
# ar_df = filter_ar_df(ar_df)