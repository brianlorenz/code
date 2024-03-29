# Generate fake emission lines with different velocity dispersions, do a median stack, then change the velocity dispersion, then stack again, talk to Aliza about this, N-med method? 
import numpy as np
import pandas as pd
from fit_emission import gaussian_func, velocity_to_sig, get_amp, get_flux
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import initialize_mosdef_dirs as imd
from scipy import interpolate
from stack_spectra import perform_stack
from scipy.optimize import curve_fit
import time
from astropy.io import ascii
import os
import matplotlib as mpl
from scipy.interpolate import interp1d


def plot_balmer_df_results(save_dir='/fixed_balmer_vel_z'):
    file_dir = imd.axis_output_dir + f'/emline_stack_tests{save_dir}/emline_stack_balmer_dfs/'
    files = os.listdir(file_dir)
    
    median_points = []
    median_stds = []
    mean_points = []
    mean_stds = []
    n_loops = []
    for file in files:
        n_loop = int(file.split('_')[2])
        balmer_df = ascii.read(file_dir + file).to_pandas()
        # Negative since we did target-stack
        # median_points.append(np.mean(-balmer_df['median_diff']))
        # median_stds.append(np.std(balmer_df['median_diff']))
        balmer_df['median_diff_from_mean'] = balmer_df['stack_median']-balmer_df['target_mean']
        balmer_df['mean_pct_diff_from_mean'] = balmer_df['stack_mean']/balmer_df['target_mean']
        balmer_df['median_pct_diff_from_mean'] = balmer_df['stack_median']/balmer_df['target_mean']
        median_points.append(np.mean(balmer_df['median_pct_diff_from_mean']))
        median_stds.append(np.std(balmer_df['median_pct_diff_from_mean']))
        mean_points.append(np.mean(balmer_df['mean_pct_diff_from_mean']))
        mean_stds.append(np.std(balmer_df['mean_pct_diff_from_mean']))

        # median_points.append(np.mean(balmer_df['median_diff_from_mean']))
        # median_stds.append(np.std(balmer_df['median_diff_from_mean']))
        # mean_points.append(np.mean(-balmer_df['mean_diff']))
        # mean_stds.append(np.std(balmer_df['mean_diff']))
        n_loops.append(n_loop)

    fig, ax = plt.subplots(figsize=(8,8))
    ax.errorbar(n_loops, median_points, yerr=median_stds, ls='None', marker='o', color='black', label='Median')
    ax.errorbar(n_loops, mean_points, yerr=mean_stds, ls='None', marker='o', color='orange', label='Mean')
    # ax.plot((0.01, 0), (100000000, 0), ls='-', marker='o', color='red')
    ax.axhline(1, color='red', ls='--')
    ax.set_ylim(0.94, 1.06)
    ax.set_xlim(5, 1100)
    ax.set_xscale('log')
    ax.set_xlabel('Number of galaxies', fontsize=12)
    ax.set_ylabel('Stack Balmer / Mean Source Balmer', fontsize=12)
    ax.legend(fontsize=12)
    fig.savefig(imd.axis_output_dir + f'/emline_stack_tests{save_dir}/balmer_summary_plot.pdf')



def main(n_spec=100, n_loops=100, balmer_test=True, fixed_variables=[], save_dir='/all_free_smoothvel', interp_resolution=0.5, smooth_vel=1):
    """
    Runs all the functions to generate the plot. 

    Parameters:
    n_spec (int): Number of spectra to generate
    n_loops (int): How many itmes to repeat the process
    balmer_test (boolean): Whether or not to generate hbeta as well as halpha, makes slightly different plots
    fixed_variables (list of str): Which variable to hold constant ['redshift', 'vel_disp', 'balmer_dec]
    interp_resolution (float): Number of angstroms per pixel (pixel scale?)
    smooth_vel (boolean): Set to 1 to smooth the velocity dispersion to 200kms
    """
    start = time.time()
    loop_count = 0
    skip_figs = 0
    while loop_count < n_loops: 
        if balmer_test:
            line_peaks = [4861, 6563]
        else:
            line_peaks = [6563]
        gal_dfs, balmer_decs = generate_group_of_spectra(n_spec=n_spec, line_peaks = line_peaks, fixed_variables = fixed_variables, smooth_vel=smooth_vel)
        interp_spectrum_dfs = [interpolate_spec(gal_dfs[i], balmer_test, resolution=interp_resolution) for i in range(len(gal_dfs))]
        norm_factors = np.ones(len(interp_spectrum_dfs))
        median_total_spec, _, _, _, _ = perform_stack('median', interp_spectrum_dfs, norm_factors)
        mean_total_spec, _, _, _, _ = perform_stack('mean', interp_spectrum_dfs, norm_factors)
        stacked_spec_df = pd.DataFrame(zip(median_total_spec, mean_total_spec), columns=['median_total_spec', 'mean_total_spec'])
        out_balmer_dec_df = plot_group_of_spectra(save_dir, gal_dfs, interp_spectrum_dfs, stacked_spec_df, balmer_test, balmer_decs, skip_figs)
        if n_loops == 1:
            return
        if loop_count == 0:
            # Creates a copy where changes aren't reflected in original
            balmer_dec_df = out_balmer_dec_df.copy(deep=True)
        else:
            balmer_dec_df = pd.concat([balmer_dec_df, out_balmer_dec_df])
        skip_figs = 1
        loop_count += 1
    balmer_dec_df['mean_diff'] = balmer_dec_df['target_mean']-balmer_dec_df['stack_mean']
    balmer_dec_df['median_diff'] = balmer_dec_df['target_median']-balmer_dec_df['stack_median']
    print(np.mean(balmer_dec_df['mean_diff']))
    print(np.std(balmer_dec_df['mean_diff']))
    print(np.mean(balmer_dec_df['median_diff']))
    print(np.std(balmer_dec_df['median_diff']))
    imd.check_and_make_dir(imd.axis_output_dir + f'/emline_stack_tests{save_dir}/emline_stack_balmer_dfs')
    balmer_dec_df.to_csv(imd.axis_output_dir + f'/emline_stack_tests{save_dir}/emline_stack_balmer_dfs/balmer_df_{n_spec}_{n_loops}.csv', index=False)
    end = time.time()
    print(f'Runtime = {end-start}')

def plot_group_of_spectra(save_dir, gal_dfs, interp_spectrum_dfs, stacked_spec_df, balmer_test, balmer_decs, skip_figs = False):
    """Plots the spectra passed to it
    
    """

    def format_axes(fig):
        for i, ax in enumerate(fig.axes):
            ax.text(0.5, 0.5, "ax%d" % (i+1), va="center", ha="center")
            ax.tick_params(labelbottom=False, labelleft=False)
    
    if skip_figs==False:
        if balmer_test == False:
            fig = plt.figure(constrained_layout=True, figsize=(10, 14))
            gs = GridSpec(5, 3, figure=fig)
            ax1 = fig.add_subplot(gs[0, 0])
            ax2 = fig.add_subplot(gs[0, 1])
            ax3 = fig.add_subplot(gs[0, 2])
            ax4 = fig.add_subplot(gs[1, 0])
            ax5 = fig.add_subplot(gs[1, 1])
            ax6 = fig.add_subplot(gs[1, 2])
            ax7 = fig.add_subplot(gs[2, 0])
            ax8 = fig.add_subplot(gs[2, 1])
            ax9 = fig.add_subplot(gs[2, 2])
            spec_axs = [ax1, ax2, ax3, ax4, ax5, ax6, ax7, ax8, ax9]
            ax_stack = fig.add_subplot(gs[3:, 0:])
            ax_stacks = [ax_stack]
            ax_stacks_names = ['halpha']
        
        if balmer_test == True:
            fig = plt.figure(constrained_layout=True, figsize=(20, 16))
            gs = GridSpec(4, 4, figure=fig)
            ax1 = fig.add_subplot(gs[0, 0])
            ax2 = fig.add_subplot(gs[0, 1])
            ax3 = fig.add_subplot(gs[0, 2])
            ax4 = fig.add_subplot(gs[0, 3])
            ax5 = fig.add_subplot(gs[1, 0])
            ax6 = fig.add_subplot(gs[1, 1])
            ax7 = fig.add_subplot(gs[1, 2])
            ax8 = fig.add_subplot(gs[1, 3])
            spec_axs = [ax1, ax2, ax3, ax4, ax5, ax6, ax7, ax8]
            ax_hb_stack = fig.add_subplot(gs[2:, 0:2])
            ax_ha_stack = fig.add_subplot(gs[2:, 2:4])
            ax_stacks = [ax_hb_stack, ax_ha_stack]
            ax_stacks_names = ['hbeta', 'halpha']

    spec_wavelength = interp_spectrum_dfs[0]['rest_wavelength']
    ha_filt = gal_dfs[0]['rest_wavelength'] > 6000
    ha_filt_interp = spec_wavelength > 6000
    hb_filt = gal_dfs[0]['rest_wavelength'] < 6000
    hb_filt_interp = spec_wavelength < 6000

    if skip_figs == False:
        for i in range(len(spec_axs)):
            ax = spec_axs[i]
            ax.plot(gal_dfs[i][ha_filt]['rest_wavelength'], gal_dfs[i][ha_filt]['f_lambda_norm'], marker='o', color='black', ls='-', label = 'rest-frame')
            ax.plot(spec_wavelength[ha_filt_interp], interp_spectrum_dfs[i][ha_filt_interp]['f_lambda_norm'], marker='o', color='blue', ls='-', label='interpolated')
            ax.set_ylim(0, 0.5)
            ax.set_xlim(6553, 6577)
            ax.set_xlabel('wavelength', fontsize=14)
            ax.set_ylabel('flux', fontsize=14)
            ax.tick_params(labelsize=14)

        # Fit the output emission lines
        if balmer_test == False:
            mean_center, mean_amp, mean_sigma, mean_ha_flux = fit_emission_line(spec_wavelength, stacked_spec_df['mean_total_spec'], 6563)
            median_center, median_amp, median_sigma, median_ha_flux = fit_emission_line(spec_wavelength, stacked_spec_df['median_total_spec'], 6563)
            mean_fit_fluxes = gaussian_func(spec_wavelength, mean_center, mean_amp, mean_sigma)
            median_fit_fluxes = gaussian_func(spec_wavelength, median_center, median_amp, median_sigma)
        
    if balmer_test == True:
        # ha_mean_center, ha_mean_amp, ha_mean_sigma, ha_mean_line_flux = fit_emission_line(spec_wavelength[ha_filt_interp], stacked_spec_df[ha_filt_interp]['mean_total_spec'], 6563)
        # ha_median_center, ha_median_amp, ha_median_sigma, ha_median_line_flux = fit_emission_line(spec_wavelength[ha_filt_interp], stacked_spec_df[ha_filt_interp]['median_total_spec'], 6563)
        # hb_mean_center, hb_mean_amp, hb_mean_sigma, hb_mean_line_flux = fit_emission_line(spec_wavelength[hb_filt_interp], stacked_spec_df[hb_filt_interp]['mean_total_spec'], 4861)
        # hb_median_center, hb_median_amp, hb_median_sigma, hb_median_line_flux = fit_emission_line(spec_wavelength[hb_filt_interp], stacked_spec_df[hb_filt_interp]['median_total_spec'], 4861)
        # mean_dec = ha_mean_line_flux / hb_mean_line_flux
        # median_dec = ha_median_line_flux / hb_median_line_flux
        median_zoffset, median_velocity, median_ha_amp, median_hb_amp, median_ha_flux, median_hb_flux, median_balmer_dec = fit_ha_hb(spec_wavelength, stacked_spec_df['median_total_spec'])
        mean_zoffset, mean_velocity, mean_ha_amp, mean_hb_amp, mean_ha_flux, mean_hb_flux, mean_balmer_dec = fit_ha_hb(spec_wavelength, stacked_spec_df['mean_total_spec'])
        # print(f'mean: {mean_balmer_dec}')
        # print(f'median: {median_balmer_dec}')
        # print(f'target mean: {np.mean(balmer_decs)}')
        # print(f'target median: {np.median(balmer_decs)}')

        median_fit_fluxes = gauss_ha_hb(spec_wavelength, median_zoffset, median_velocity, median_ha_amp, median_hb_amp)
        mean_fit_fluxes = gauss_ha_hb(spec_wavelength, mean_zoffset, mean_velocity, mean_ha_amp, mean_hb_amp)
        balmer_out_df = pd.DataFrame([[mean_balmer_dec, median_balmer_dec, np.mean(balmer_decs), np.median(balmer_decs)]], columns=['stack_mean', 'stack_median', 'target_mean', 'target_median'])


    fit_flux_df = pd.DataFrame(zip(median_fit_fluxes, mean_fit_fluxes), columns=['median_fit', 'mean_fit'])
    
    if skip_figs == True:
        return balmer_out_df


    for i in range(len(ax_stacks)):
        if ax_stacks_names[i]=='halpha':
            filt = ha_filt_interp
        elif ax_stacks_names[i]=='hbeta':
            filt = hb_filt_interp
        ax_stacks[i].plot(spec_wavelength[filt], stacked_spec_df['median_total_spec'][filt], color='black', marker='o', ls='', label='median', zorder=10)
        ax_stacks[i].plot(spec_wavelength[filt], stacked_spec_df['mean_total_spec'][filt], color='orange', marker='o', ls='', label='mean', zorder=10)
        ax_stacks[i].plot(spec_wavelength[filt], fit_flux_df['median_fit'][filt], color='mediumseagreen', marker='None', ls='-', label='median_fit', zorder=1)
        ax_stacks[i].plot(spec_wavelength[filt], fit_flux_df['mean_fit'][filt], color='blue', marker='None', ls='-', label='mean_fit', zorder=1)
        ax_stacks[i].set_xlabel('wavelength', fontsize=18)
        ax_stacks[i].set_ylabel('flux', fontsize=18)
        ax_stacks[i].legend(loc=1, fontsize=18)
        ax_stacks[i].text(6567.5, 0.128, f'Stacked {len(gal_dfs)} Galaxies', fontsize=18)
        ax_stacks[i].text(6567.5, 0.115, f'Median {round(median_ha_flux, 5)}', fontsize=18)
        ax_stacks[i].text(6567.5, 0.102, f'Mean {round(mean_ha_flux, 5)}', fontsize=18)
        if ax_stacks_names[i]=='hbeta':
            ax_stacks[i].text(4868.5, 0.115, f'Median {round(median_hb_flux, 5)}', fontsize=18)
            ax_stacks[i].text(4868.5, 0.102, f'Mean {round(mean_hb_flux, 5)}', fontsize=18)
            plt.gcf().text(0.28, 0.92, f'Sample  Balmer  Dec  median {round(np.median(balmer_decs), 5)} and mean {round(np.mean(balmer_decs), 5)}', fontsize=24, color='red')
            plt.gcf().text(0.28, 0.96, f'Computed Balmer Dec median {round(np.median(median_balmer_dec), 5)} and mean {round(np.mean(mean_balmer_dec), 5)}', fontsize=24, color='red')
            plt.gcf().text(0.28, 0.89, f'Error                                          {round(np.median(balmer_decs)-np.median(median_balmer_dec), 5)}                 {round(np.mean(balmer_decs)-np.mean(mean_balmer_dec), 5)}', fontsize=24, color='black')
        ax_stacks[i].tick_params(labelsize=14)
        ax_stacks[i].set_ylim(-0.005, 0.2)

    

    

    ax1.legend(loc=1, fontsize=18)
    if balmer_test==True:
        save_addon = 'balmer'
    else:
        save_addon = ''
    imd.check_and_make_dir(imd.axis_output_dir + f'/emline_stack_tests{save_dir}')
    fig.savefig(imd.axis_output_dir + f'/emline_stack_tests{save_dir}/stacked_{len(gal_dfs)}_{save_addon}.pdf')
    plt.close('all') 
    if balmer_test==False:
        balmer_out_df = 1
    return balmer_out_df

def interpolate_spec(spectrum_df, balmer_test, resolution=0.5):
    """Interpolate teh spectrum and add uncertainties in the same way that is done in stack_spectra"""
    spectrum_wavelength = np.arange(6553, 6577, resolution)
    if balmer_test:
        spectrum_wavelength_hb = np.arange(4843, 4883, resolution)
        spectrum_wavelength = np.concatenate([spectrum_wavelength_hb, spectrum_wavelength])
    norm_interp = interpolate.interp1d(
                spectrum_df['rest_wavelength'], spectrum_df['f_lambda_norm'], fill_value=0, bounds_error=False)
    spectrum_flux_norm = norm_interp(spectrum_wavelength)
    spectrum_err_norm = np.ones(len(spectrum_wavelength)) / 10
    cont_norm = np.zeros(len(spectrum_wavelength))
    interp_spectrum_df = pd.DataFrame(zip(spectrum_wavelength, spectrum_flux_norm, spectrum_err_norm, cont_norm), columns=['rest_wavelength', 'f_lambda_norm', 'err_f_lambda_norm', 'cont_norm'])
    return interp_spectrum_df

def generate_group_of_spectra(n_spec=9, line_peaks = [4861, 6563], fixed_variables=[], smooth_vel=0):
    """Makes a group of spectra from the parameter space

    Parameters:
    n_spec (int): Number of spectra to generate
    line_peaks (array): Peak wavelengths of the lines to generate for
    fixed_variables (list of str): Which variables not to randomize
    smooth_vel (boolean): Set to 1 to smooth to velocity dispersion
    """
    if 'redshift' in fixed_variables:
        zs = [2 for i in range(n_spec)]
    else:
        zs = [np.random.random() + 1.6 for i in range(n_spec)]
    if 'vel_disp' in fixed_variables:
        vel_disps = [100 for i in range(n_spec)]
    else:
        vel_disps = [np.random.random()*80 + 70 for i in range(n_spec)]
    if 'balmer_dec' in fixed_variables:
        balmer_decs = [4.5 for i in range(n_spec)]
    else:
        balmer_decs = [np.random.random()*3 + 3 for i in range(n_spec)]
    if 'flux' in fixed_variables:
        balmer_decs = [1 for i in range(n_spec)]
    else:
        balmer_decs = [np.random.random()*2 + 1 for i in range(n_spec)]
    gal_dfs = [generate_fake_galaxy_prop(zs[i], 1, vel_disps[i], line_peaks, balmer_decs[i], smooth_vel=smooth_vel) for i in range(n_spec)]
    return gal_dfs, balmer_decs

def generate_fake_galaxy_prop(z, flux, vel_disp, line_peaks, balmer_dec, smooth_vel=0, wavelength_res = 1.5):
    """Makes a fake galaxy spectrum with the properties specified
    
    Parameters:
    z (float): redshift of the galaxy
    flux (float): flux of the halpha line
    vel_disp (float): velocity dispersion of the galaxy 
    line_peaks (array): Peak wavelengths of the lines to generate for
    balmer_dec (float): Ratio between halpha and hbeta lines. Halpha stays fixed to 1, hbeta is some fraction of its flux
    smooth_vel (boolean): Set to 1 to smooth the velocity dispersion of the spectrum
    wavelength_res (float): step size for wavelength resolution
    """
    line_dfs = []
    for line_peak in line_peaks:
        if line_peak == 4861:
            use_flux = 1/balmer_dec
        else:
            use_flux = flux
        obs_line_peak = line_peak * (1+z)
        wavelength = np.arange(int(obs_line_peak)-40, int(obs_line_peak)+40, wavelength_res)
        fluxes = generate_emission_line(wavelength, use_flux, vel_disp)
        rest_wavelength = wavelength / (1+z)
        rest_flux = fluxes * (1+z)

        if smooth_vel:
            fluxes = smooth_velocity(rest_wavelength, rest_flux, vel_disp)

        line_df = pd.DataFrame(zip(wavelength, fluxes, rest_wavelength, rest_flux), columns = ['wavelength', 'flux', 'rest_wavelength', 'f_lambda_norm'])
        line_dfs.append(line_df)
    gal_df = pd.concat(line_dfs)
    # plt.plot(gal_df['rest_wavelength'], gal_df['f_lambda_norm'], ls='None', marker='o')
    # plt.text(5000, 0, f'{balmer_dec}')
    # plt.show()
    # exit()
    # fit_emission_line(gal_df, 6563)
    return gal_df
    


def generate_emission_line(wavelength, flux, vel_disp):
    """Given an amplitude and velocity dispersion, generate an emission line
    
    Parameters:
    wavelength (array): Wavelength array to put the line on. It will be centered
    flux (float): flux of the line
    vel_disp (float): Velocity dispersion of the line, will be converted into a width

    Returns:
    fluxes (array): Array of same length as wavelength, containing the line fluxes
    """
    # Put the line in the center of the wavelength range
    line_center = np.median(wavelength)

    # Convert the velocity dispersion into a line width, depends on wavelength
    sigma = velocity_to_sig(line_center, vel_disp)
    amplitude = get_amp(flux, sigma)
    # print(amplitude)
    fluxes = gaussian_func(wavelength, line_center, amplitude, sigma)
    return fluxes


def fit_emission_line(rest_wavelength, fluxes, line_center):
    """Fit an emission line from a gal_df

    Parameters:
    rest_wavelength (array): Wavelength array
    fluxes (array): Fluxes array
    line_center (float): Central wavelength (angstrom)
    
    """
    guess_center = line_center
    guess_amp = 0.15
    guess_sigma = 6
    guess = [guess_center, guess_amp, guess_sigma]
    popt, pcov = curve_fit(gaussian_func, rest_wavelength, fluxes, guess)
    center, amp, sigma = popt
    line_flux, _ = get_flux(amp, sigma)
    # print(line_flux)
    return center, amp, sigma, line_flux

def fit_ha_hb(wavelength_cut, fluxes):
    """Fit an emission line from a gal_df

    Parameters:
    wavelength_cut (array): Slice of wavelength that has ha and hb in it
    fluxes (array): Fluxes array, matching the same slice
    
    """
    guess_z_offset = 0
    guess_velocity = 100
    guess_amp_ha = 0.15
    guess_amp_hb = 0.05
    guess = [guess_z_offset, guess_velocity, guess_amp_ha, guess_amp_hb]
    popt, pcov = curve_fit(gauss_ha_hb, wavelength_cut, fluxes, guess)
    zoffset, velocity, ha_amp, hb_amp = popt
    ha_flux, _ = get_flux(ha_amp, velocity_to_sig(6563, velocity))
    hb_flux, _ = get_flux(hb_amp, velocity_to_sig(4861, velocity))
    balmer_dec = ha_flux/hb_flux
    # print(line_flux)
    return zoffset, velocity, ha_amp, hb_amp, ha_flux, hb_flux, balmer_dec

def gauss_ha_hb(wavelength_cut, z_offset, velocity, ha_amp, hb_amp):
    """Fits all Gaussians simulatneously at fixed redshift

    Parameters:
    wavelength_cut (pd.DataFrame): Wavelength array to fit, just the two emission line regions concatenated together
    pars (list): List of all of the parameters
    fit (boolean): Set to True if fitting (ie amps are not constrained yet)

    Returns:
    combined_gauss (array): Gaussian function over the h_beta and h_alpha region concatenated
    """

    # Split the wavelength into its Halpha nad Hbeta parts
    wavelength_hb = wavelength_cut[wavelength_cut < 5500]
    wavelength_ha = wavelength_cut[wavelength_cut > 5500]

    gaussians_hb = gaussian_func(wavelength_hb, 4861 + z_offset, hb_amp, velocity_to_sig(4861, velocity))
    gaussians_ha = gaussian_func(wavelength_ha, 6563 + z_offset, ha_amp, velocity_to_sig(6563, velocity))

    combined_gauss = np.concatenate([gaussians_hb, gaussians_ha])

    return combined_gauss


def plot_range_of_vel_disp():
    """Makes a plot of the same amplitude with a range of velocity dispersions"""
    line_peaks = [6563]
    n_spec=10
    zs = [2 for i in range(n_spec)]
    balmer_decs = [4 for i in range(n_spec)]
    vel_disps = np.arange(70, 150, 80/n_spec)
    gal_dfs = [generate_fake_galaxy_prop(zs[i], 1, vel_disps[i], line_peaks, balmer_decs[i]) for i in range(n_spec)]
    
    fig, ax = plt.subplots(figsize=(9,8))
    cmap = mpl.cm.inferno 
    norm = mpl.colors.Normalize(vmin=70, vmax=150) 
    for i in range(n_spec):
        rgba = cmap(norm(vel_disps[i]))
        ax.plot(gal_dfs[i]['rest_wavelength'], gal_dfs[i]['f_lambda_norm'], color=rgba)
    cbar = fig.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap), ax=ax)
    cbar.set_label('Velocity Dispersion (km/s)', fontsize=14)
    ax.set_title('Fixed z=2, Flux = 1', fontsize=14)
    ax.set_xlabel('Rest Wavelength', fontsize=14)
    ax.set_ylabel('f_lambda', fontsize=14)
    fig.savefig(imd.axis_output_dir + '/emline_stack_tests/var_veldisp_ha.pdf')


def smooth_velocity(wave,spec,insig,mask=None,sigma=200,scale=1):
    '''
    Convolve spectrum to desired velocity dispersion
    Code inspired by prospector 'smooth_vel' function in 'smoothing.py'

    :param wave:
        The wavelength vector of the input spectrum, ndarray.  Assumed
        angstroms.
    :param spec:
        The flux vector of the input spectrum, ndarray
    :param insig:
        The velocity dispersion of the input spectrum
    :param mask:
        Wavelengths to mask (eg skylines), these are interpolated over before convolving.
    :param sigma:
        Desired velocity resolution (km/s), *not* FWHM.
    :returns flux:
        The smoothed spectrum on the input wave grid, ndarray.
    '''
    sigma_eff_sq = sigma**2 - insig**2
    if np.any(sigma_eff_sq) < 0.0:
        raise ValueError("Desired velocity resolution smaller than the value"
                        "possible for this input spectrum.".format(insig))
    # sigma_eff is in units of sigma_lambda / lambda
    sigma_eff = np.sqrt(sigma_eff_sq) / 299792

    if mask is not None:
        y = interp1d(wave[~mask],spec[~mask],fill_value='extrapolate')
        spec = y(wave)

    flux = np.zeros(len(wave))
    for i, w in enumerate(wave):
        # x = (np.log(w) - lnwave) / sigma_eff # what's used in propsector
        x = (w-wave)/(sigma_eff*w) # what makes more sense to me (gives same result)
        f = np.exp(-0.5 * x**2) / np.trapz(np.exp(-0.5 * x**2), wave)
        flux[i] = np.trapz(f**scale * spec, wave) # / np.trapz(f, wave)

    return flux


# main()
# plot_balmer_df_results(save_dir='/all_free_smoothvel')
# plot_range_of_vel_disp()
# main(n_spec=10, n_loops=10, balmer_test=True, fixed_variables=[], save_dir='/resolution_001_allfree', interp_resolution=0.001)