from inspect import stack
from perform_axis_stack import stack_all_and_plot_all


class stack_params:
    
    def __init__(self, mass_width, split_width, starting_points, ratio_bins, nbins, split_by, save_name, stack_type, sfms_bins, use_whitaker_sfms, use_z_dependent_sfms, bootstrap, only_plot, run_stack):
        '''
        
        Parameters:
        mass_width (float): Length of a mass bin in log stellar masses, e.g. 0.7
        split_width (float): Length of a bin on the y-axis (ssfr or equivalent width, typically)
        starting_points (list of tuples): Each tuple is a coordinate in (mass,y) space for where to put the lower-left of each bin. The above widths determine the enclosed points
        ratio_bins (list): List of where to divide the bins in axis ratios, e.g [0.4, 0.7] gives 3 bins from 0-0.4, 0.4-0.7, 0.7-1
        nbins (int): Total number of bins, could be computed as len(starting points)*(len(ratio_bins)+1)
        split_by (str): Column name for the y-axis, either some form of ssfr ('log_use_ssfr') or 'eq_width_ha'
        save_name (str): Name for the directory where all outputs will be saved
        stack_type (str): 'mean' or 'median' for how to stack the spectra
        sfms_bins (boolean): Set to True to use different bins from the star-forming main sequence instead of the above method
        bootstrap (int): Set to 0 to not bootstrap, or the number of boostrap samples to run to do so
        only_plot (boolean): Set to True to skip the stacking step and just re-run the plots
        run_stack (boolean): Set to True to include this group in the current run of the code

        '''
        
        self.mass_width = mass_width
        self.split_width = split_width
        self.starting_points = starting_points
        self.ratio_bins = ratio_bins
        self.nbins = nbins
        self.split_by = split_by
        self.save_name = save_name
        self.stack_type = stack_type
        self.sfms_bins = sfms_bins
        self.use_whitaker_sfms = use_whitaker_sfms # Need sfms_bins = True to use
        self.use_z_dependent_sfms = use_z_dependent_sfms # Need sfms_bins = True to use
        self.bootstrap = bootstrap
        self.only_plot = only_plot
        self.run_stack = run_stack
        

# Normal 12bin using combined sfrs, using sfr2 when both lines are good, halpha_sfr when hbeta is below 3 sigma (or not covered)
## -----------------------------------------------------------------
## USING
## -----------------------------------------------------------------

# PRimary as of 6/26/22
def make_zdep_whitaker_sfms_boot100(run_stack = False, only_plot = False):
    run_stack = run_stack
    only_plot = only_plot
    mass_width = 1.0
    split_width = 0.75
    starting_points = [(9, -8.85), (10, -8.85), (9, -9.6), (10, -9.6)]
    ratio_bins = [0.55]
    nbins = 8
    split_by = 'log_use_sfr'
    save_name = 'zdep_whitaker_sfms_boot100_masscorr'
    stack_type = 'median'
    sfms_bins = True
    use_whitaker_sfms = True
    use_z_dependent_sfms = True
    bootstrap = 100
    both_ssfrs_4bin_mean_params = stack_params(mass_width, split_width, starting_points, ratio_bins, nbins, split_by, save_name, stack_type, sfms_bins, use_whitaker_sfms, use_z_dependent_sfms, bootstrap, only_plot, run_stack)
    return both_ssfrs_4bin_mean_params
zdep_whitaker_sfms_boot100 = make_zdep_whitaker_sfms_boot100()

def make_whitaker_sfms_boot100(run_stack = True, only_plot = False):
    run_stack = run_stack
    only_plot = only_plot
    mass_width = 1.0
    split_width = 0.75
    starting_points = [(9, -8.85), (10, -8.85), (9, -9.6), (10, -9.6)]
    ratio_bins = [0.55]
    nbins = 8
    split_by = 'log_use_sfr'
    save_name = 'whitaker_sfms_boot100'
    stack_type = 'median'
    sfms_bins = True
    use_whitaker_sfms = True
    use_z_dependent_sfms = False
    bootstrap = 100
    both_ssfrs_4bin_mean_params = stack_params(mass_width, split_width, starting_points, ratio_bins, nbins, split_by, save_name, stack_type, sfms_bins, use_whitaker_sfms, use_z_dependent_sfms, bootstrap, only_plot, run_stack)
    return both_ssfrs_4bin_mean_params
whitaker_sfms_boot100 = make_whitaker_sfms_boot100()


# Currently the primary one we are using
def make_both_sfms_4bin_2axis_median_params(run_stack = False, only_plot = True):
    run_stack = run_stack
    only_plot = only_plot
    mass_width = 1.0
    split_width = 0.75
    starting_points = [(9, -8.85), (10, -8.85), (9, -9.6), (10, -9.6)]
    ratio_bins = [0.55]
    nbins = 8
    split_by = 'log_use_sfr'
    save_name = 'both_sfms_4bin_median_2axis_boot100'
    stack_type = 'median'
    sfms_bins = True
    use_whitaker_sfms = False
    use_z_dependent_sfms = False
    bootstrap = 100
    both_ssfrs_4bin_mean_params = stack_params(mass_width, split_width, starting_points, ratio_bins, nbins, split_by, save_name, stack_type, sfms_bins, use_whitaker_sfms, use_z_dependent_sfms, bootstrap, only_plot, run_stack)
    return both_ssfrs_4bin_mean_params
both_sfms_4bin_2axis_median_params = make_both_sfms_4bin_2axis_median_params()

def both_whitaker_sfms_4bin_median_2axis_params(run_stack = False, only_plot = True):
    run_stack = run_stack
    only_plot = only_plot
    mass_width = 1.0
    split_width = 0.75
    starting_points = [(9, -8.85), (10, -8.85), (9, -9.6), (10, -9.6)]
    ratio_bins = [0.55]
    nbins = 8
    split_by = 'log_use_sfr'
    save_name = 'both_whitaker_sfms_4bin_median_2axis_boot10'
    stack_type = 'median'
    sfms_bins = True
    use_whitaker_sfms = True
    use_z_dependent_sfms = False
    bootstrap = 10
    both_ssfrs_4bin_mean_params = stack_params(mass_width, split_width, starting_points, ratio_bins, nbins, split_by, save_name, stack_type, sfms_bins, use_whitaker_sfms, use_z_dependent_sfms, bootstrap, only_plot, run_stack)
    return both_ssfrs_4bin_mean_params
both_whitaker_sfms_4bin_median_2axis = both_whitaker_sfms_4bin_median_2axis_params()

def both_z_divided_sfms_4bin_median_2axis_params(run_stack = False, only_plot = True):
    run_stack = run_stack
    only_plot = only_plot
    mass_width = 1.0
    split_width = 0.75
    starting_points = [(9, -8.85), (10, -8.85), (9, -9.6), (10, -9.6)]
    ratio_bins = [0.55]
    nbins = 8
    split_by = 'log_use_sfr'
    save_name = 'both_z_divided_sfms_4bin_median_2axis_boot10'
    stack_type = 'median'
    sfms_bins = True
    use_whitaker_sfms = False
    use_z_dependent_sfms = True
    bootstrap = 10
    both_ssfrs_4bin_mean_params = stack_params(mass_width, split_width, starting_points, ratio_bins, nbins, split_by, save_name, stack_type, sfms_bins, use_whitaker_sfms, use_z_dependent_sfms, bootstrap, only_plot, run_stack)
    return both_ssfrs_4bin_mean_params
both_z_divided_sfms_4bin_median_2axis = both_z_divided_sfms_4bin_median_2axis_params()


# 
def lowz_sample_params(run_stack = False, only_plot = False):
    run_stack = run_stack
    only_plot = only_plot
    mass_width = 1.0
    split_width = 0.75
    starting_points = [(9, -8.85), (10, -8.85), (9, -9.6), (10, -9.6)]
    ratio_bins = [0.55]
    nbins = 8
    split_by = 'log_use_sfr'
    save_name = 'lowz_sample'
    stack_type = 'median'
    sfms_bins = True
    use_whitaker_sfms = False
    use_z_dependent_sfms = True
    bootstrap = 10
    both_ssfrs_4bin_mean_params = stack_params(mass_width, split_width, starting_points, ratio_bins, nbins, split_by, save_name, stack_type, sfms_bins, use_whitaker_sfms, use_z_dependent_sfms, bootstrap, only_plot, run_stack)
    return both_ssfrs_4bin_mean_params
lowz_sample = lowz_sample_params()

def highz_sample_params(run_stack = False, only_plot = False):
    run_stack = run_stack
    only_plot = only_plot
    mass_width = 1.0
    split_width = 0.75
    starting_points = [(9, -8.85), (10, -8.85), (9, -9.6), (10, -9.6)]
    ratio_bins = [0.55]
    nbins = 8
    split_by = 'log_use_sfr'
    save_name = 'high_sample'
    stack_type = 'median'
    sfms_bins = True
    use_whitaker_sfms = False
    use_z_dependent_sfms = True
    bootstrap = 10
    both_ssfrs_4bin_mean_params = stack_params(mass_width, split_width, starting_points, ratio_bins, nbins, split_by, save_name, stack_type, sfms_bins, use_whitaker_sfms, use_z_dependent_sfms, bootstrap, only_plot, run_stack)
    return both_ssfrs_4bin_mean_params
highz_sample = highz_sample_params()



# Single stack, for background of some plots
def make_both_singlestack_median_params(run_stack = False, only_plot = False):
    run_stack = run_stack
    only_plot = only_plot
    mass_width = 2.0
    split_width = 1.5
    starting_points = [(9, -9.6)]
    ratio_bins = []
    nbins = 1
    split_by = 'log_use_ssfr'
    save_name = 'both_singlestack_median'
    stack_type = 'median'
    sfms_bins = False
    use_whitaker_sfms = False
    use_z_dependent_sfms = False
    bootstrap = 100
    both_ssfrs_4bin_mean_params = stack_params(mass_width, split_width, starting_points, ratio_bins, nbins, split_by, save_name, stack_type, sfms_bins, use_whitaker_sfms, use_z_dependent_sfms, bootstrap, only_plot, run_stack)
    return both_ssfrs_4bin_mean_params
both_singlestack_median_params = make_both_singlestack_median_params()




## -----------------------------------------------------------------
## End Using
## -----------------------------------------------------------------

# def make_both_ssfrs_4bin_median_params(run_stack = False, only_plot = True):
#     run_stack = run_stack
#     only_plot = only_plot
#     mass_width = 1.0
#     split_width = 0.75
#     starting_points = [(9.0, -8.85), (10.0, -8.85), (9.0, -9.6), (10.0, -9.6)]
#     ratio_bins = [0.4, 0.7]
#     nbins = 12
#     split_by = 'log_use_ssfr'
#     save_name = 'both_ssfrs_4bin_median'
#     stack_type = 'median'
#     sfms_bins = False
#     bootstrap = 10
#     both_ssfrs_4bin_mean_params = stack_params(mass_width, split_width, starting_points, ratio_bins, nbins, split_by, save_name, stack_type, sfms_bins, bootstrap, only_plot, run_stack)
#     return both_ssfrs_4bin_mean_params
# both_ssfrs_4bin_median_params = make_both_ssfrs_4bin_median_params()

# # Normal 12bin using combined sfrs, using sfr2 when both lines are good, halpha_sfr when hbeta is below 3 sigma (or not covered)
# def make_both_ssfrs_4bin_2axis_median_params(run_stack = False, only_plot = True):
#     run_stack = run_stack
#     only_plot = only_plot
#     mass_width = 1.0
#     split_width = 0.75
#     starting_points = [(9.0, -8.85), (10.0, -8.85), (9.0, -9.6), (10.0, -9.6)]
#     ratio_bins = [0.55]
#     nbins = 8
#     split_by = 'log_use_ssfr'
#     save_name = 'both_ssfrs_4bin_median_2axis_boot100'
#     stack_type = 'median'
#     sfms_bins = False
#     bootstrap = 100
#     both_ssfrs_4bin_mean_params = stack_params(mass_width, split_width, starting_points, ratio_bins, nbins, split_by, save_name, stack_type, sfms_bins, bootstrap, only_plot, run_stack)
#     return both_ssfrs_4bin_mean_params
# both_ssfrs_4bin_2axis_median_params = make_both_ssfrs_4bin_2axis_median_params()


# def make_both_sfms_4bin_2axis_median_retest_params(run_stack = False, only_plot = False):
#     run_stack = run_stack
#     only_plot = only_plot
#     mass_width = 1.0
#     split_width = 0.75
#     starting_points = [(9, -8.85), (10, -8.85), (9, -9.6), (10, -9.6)]
#     ratio_bins = [0.55]
#     nbins = 8
#     split_by = 'log_use_sfr'
#     save_name = 'both_sfms_4bin_median_2axis_boot100_retest'
#     stack_type = 'median'
#     sfms_bins = True
#     bootstrap = 100
#     both_ssfrs_4bin_mean_params = stack_params(mass_width, split_width, starting_points, ratio_bins, nbins, split_by, save_name, stack_type, sfms_bins, bootstrap, only_plot, run_stack)
#     return both_ssfrs_4bin_mean_params
# both_sfms_4bin_2axis_median_retest_params = make_both_sfms_4bin_2axis_median_retest_params()

# def make_both_sfms_4bin_2axis_mean_params(run_stack = False, only_plot = False):
#     run_stack = run_stack
#     only_plot = only_plot
#     mass_width = 1.0
#     split_width = 0.75
#     starting_points = [(9, -8.85), (10, -8.85), (9, -9.6), (10, -9.6)]
#     ratio_bins = [0.55]
#     nbins = 8
#     split_by = 'log_use_sfr'
#     save_name = 'both_sfms_4bin_mean_2axis_boot100'
#     stack_type = 'mean'
#     sfms_bins = True
#     bootstrap = 100
#     both_ssfrs_4bin_mean_params = stack_params(mass_width, split_width, starting_points, ratio_bins, nbins, split_by, save_name, stack_type, sfms_bins, bootstrap, only_plot, run_stack)
#     return both_ssfrs_4bin_mean_params
# both_sfms_4bin_2axis_mean_params = make_both_sfms_4bin_2axis_mean_params()

# def make_both_sfms_4bin_2axis_ar_split_median_params(run_stack = False, only_plot = False):
#     run_stack = run_stack
#     only_plot = only_plot
#     mass_width = 1.0
#     split_width = 0.75
#     starting_points = [(9, -8.85), (10, -8.85), (9, -9.6), (10, -9.6)]
#     ratio_bins = [0.35, 0.75]
#     nbins = 12
#     split_by = 'log_use_sfr'
#     save_name = 'both_sfms_4bin_median_2axis_boot100_ar_split'
#     stack_type = 'median'
#     sfms_bins = True
#     bootstrap = 100
#     both_ssfrs_4bin_mean_params = stack_params(mass_width, split_width, starting_points, ratio_bins, nbins, split_by, save_name, stack_type, sfms_bins, bootstrap, only_plot, run_stack)
#     return both_ssfrs_4bin_mean_params
# both_sfms_4bin_2axis_ar_split_median_params = make_both_sfms_4bin_2axis_ar_split_median_params()


# def make_both_sfms_4bin_2axis_median_metaltest2_params(run_stack = False, only_plot = False):
#     run_stack = run_stack
#     only_plot = only_plot
#     mass_width = 1.0
#     split_width = 0.75
#     starting_points = [(9, -8.85), (10, -8.85), (9, -9.6), (10, -9.6)]
#     ratio_bins = [0.55]
#     nbins = 8
#     split_by = 'log_use_sfr'
#     save_name = 'both_sfms_4bin_median_2axis_boot100_metaltest2'
#     stack_type = 'median'
#     sfms_bins = True
#     bootstrap = 100
#     both_ssfrs_4bin_mean_params = stack_params(mass_width, split_width, starting_points, ratio_bins, nbins, split_by, save_name, stack_type, sfms_bins, bootstrap, only_plot, run_stack)
#     return both_ssfrs_4bin_mean_params
# both_sfms_4bin_2axis_median_metaltest2_params = make_both_sfms_4bin_2axis_median_metaltest2_params()

# def make_both_4bin_1axis_median_params(run_stack = False, only_plot = True):
#     run_stack = run_stack
#     only_plot = only_plot
#     mass_width = 1.0
#     split_width = 0.75
#     starting_points = [(9.0, -8.85), (10.0, -8.85), (9.0, -9.6), (10.0, -9.6)]
#     ratio_bins = []
#     nbins = 4
#     split_by = 'log_use_ssfr'
#     save_name = 'both_4bin_1axis_median_params'
#     stack_type = 'median'
#     sfms_bins = False
#     bootstrap = 10
#     both_ssfrs_4bin_mean_params = stack_params(mass_width, split_width, starting_points, ratio_bins, nbins, split_by, save_name, stack_type, sfms_bins, bootstrap, only_plot, run_stack)
#     return both_ssfrs_4bin_mean_params
# both_4bin_1axis_median_params = make_both_4bin_1axis_median_params()

# def make_both_6bin_1axis_median_params(run_stack = False, only_plot = True):
#     run_stack = run_stack
#     only_plot = only_plot
#     mass_width = 1.0
#     split_width = 0.5
#     starting_points = [(9.0, -8.6), (10.0, -8.6), (9.0, -9.1), (10.0, -9.1), (9.0, -9.6), (10.0, -9.6)]
#     ratio_bins = []
#     nbins = 6
#     split_by = 'log_use_ssfr'
#     save_name = 'both_6bin_1axis_median_params'
#     stack_type = 'median'
#     sfms_bins = False
#     bootstrap = 10
#     both_ssfrs_4bin_mean_params = stack_params(mass_width, split_width, starting_points, ratio_bins, nbins, split_by, save_name, stack_type, sfms_bins, bootstrap, only_plot, run_stack)
#     return both_ssfrs_4bin_mean_params
# both_6bin_1axis_median_params = make_both_6bin_1axis_median_params()

# 12 bins, 2 mass 2 ssfr, new halpha ssfrs
# run_stack = True
# only_plot = False
# mass_width = 0.8
# split_width = 0.75
# starting_points = [(9.3, -8.85), (10.1, -8.85), (9.3, -9.6), (10.1, -9.6)]
# ratio_bins = [0.4, 0.7]
# nbins = 12
# split_by = 'log_halpha_ssfr'
# save_name = 'halpha_ssfr_4bin_mean'
# stack_type = 'mean'


# stack_all_and_plot_all(eq_width_ha_params)
# stack_all_and_plot_all(both_ssfrs_4bin_mean_2axis_params)
# stack_all_and_plot_all(both_ssfrs_4bin_mean_params)
# stack_all_and_plot_all(both_ssfrs_4bin_median_params)
# stack_all_and_plot_all(both_ssfrs_4bin_2axis_median_params)
stack_all_and_plot_all(zdep_whitaker_sfms_boot100)
stack_all_and_plot_all(whitaker_sfms_boot100)
stack_all_and_plot_all(both_sfms_4bin_2axis_median_params)
stack_all_and_plot_all(both_whitaker_sfms_4bin_median_2axis)
stack_all_and_plot_all(both_z_divided_sfms_4bin_median_2axis)
stack_all_and_plot_all(lowz_sample)
stack_all_and_plot_all(highz_sample)
# stack_all_and_plot_all(both_sfms_4bin_2axis_median_retest_params)
# stack_all_and_plot_all(both_sfms_4bin_2axis_mean_params)
# stack_all_and_plot_all(both_sfms_4bin_2axis_ar_split_median_params)
stack_all_and_plot_all(both_singlestack_median_params)
# stack_all_and_plot_all(both_4bin_1axis_median_params)
# stack_all_and_plot_all(both_6bin_1axis_median_params)
# stack_all_and_plot_all(both_sfms_4bin_2axis_median_metaltest2_params)

# stack_all_and_plot_all(mosdef_ssfr_4bin_mean_params)
# stack_all_and_plot_all(mosdef_ssfr_4bin_median_params)
# stack_all_and_plot_all(halpha_ssfr_4bin_mean_shifted_params)
