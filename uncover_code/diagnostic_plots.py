from uncover_read_data import read_spec_cat
from astropy.io import ascii
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.cm import ScalarMappable
from sedpy import observate
from make_dust_maps import make_3color
from uncover_read_data import read_raw_spec
from uncover_make_sed import get_sed
from compute_av import ha_factor, pab_factor, compute_ratio_from_av, compute_ha_pab_av, compute_ha_pab_av_from_dustmap, read_catalog_av
import pandas as pd

def diagnostic_av_emissionfit_vs_av_prospector(color_var = 'None', use_subsample=True, remove_nii=False):
    zqual_df = read_spec_cat()

    zqual_df_cont_covered = ascii.read('/Users/brianlorenz/uncover/zqual_df_cont_covered.csv').to_pandas()
    lineratio_df = ascii.read('/Users/brianlorenz/uncover/Figures/diagnostic_lineratio/lineratio_df.csv').to_pandas()
    id_msa_list = zqual_df_cont_covered['id_msa']

    if use_subsample:
        filtered_lineratio_df = ascii.read(f'/Users/brianlorenz/uncover/Figures/diagnostic_lineratio/filtered_lineratio_df.csv').to_pandas()
        lineratio_df = filtered_lineratio_df
        id_msa_list = lineratio_df['id_msa']
        add_str = '_subsamp'
    else:
        add_str = ''
    if remove_nii:
        add_str = add_str + '_removeNii'
    
    lineratio_df['integrated_spec_av'] = compute_ha_pab_av(1/lineratio_df['integrated_spec_lineratio'])
    sed_lineratio = lineratio_df['sed_lineratio']
    if remove_nii:
        sed_lineratio = 0.8*sed_lineratio
    lineratio_df['sed_av'] = compute_ha_pab_av(1/sed_lineratio)
    
    
        


    redshifts = zqual_df_cont_covered['z_spec'].to_numpy()
    fig, axarr = plt.subplots(1, 2, figsize=(12,6))
    ax_sed_emfit = axarr[0]
    ax_emfit_prospector = axarr[1]

    ha_line_avg_transmissions = []
    pab_line_avg_transmissions = []

    # Color coding
    cmap = mpl.cm.inferno
    if color_var == 'redshift':
        norm = mpl.colors.Normalize(vmin=1.3, vmax=2.4) 
        color_array = redshifts
    if color_var == 'halpha_trasmission':
        norm = mpl.colors.Normalize(vmin=0.2, vmax=1) 
        color_array = ha_line_avg_transmissions
    if color_var == 'pabeta_trasmission':
        norm = mpl.colors.Normalize(vmin=0.2, vmax=1) 
        color_array = pab_line_avg_transmissions
    

    err_av_50s_lows = []
    av_50s = []
    err_av_50s_highs = []

    for i in range(len(id_msa_list)):
        id_msa = id_msa_list[i]
        emission_df = ascii.read(f'/Users/brianlorenz/uncover/Data/emission_fitting/{id_msa}_emission_fits.csv').to_pandas()
        
        ha_filters, ha_images, wht_ha_images, obj_segmap, ha_photfnus = make_3color(id_msa, line_index=0, plot=False)
        pab_filters, pab_images, wht_pab_images, obj_segmap, pab_photfnus = make_3color(id_msa, line_index=1, plot=False)
        ha_sedpy_name = ha_filters[1].replace('f', 'jwst_f')
        ha_sedpy_filt = observate.load_filters([ha_sedpy_name])[0]
        pab_sedpy_name = pab_filters[1].replace('f', 'jwst_f')
        pab_sedpy_filt = observate.load_filters([pab_sedpy_name])[0]
        def get_transmission(line_idx, sedpy_filt):
            line_range_low = (1+redshifts[i])*(emission_df.iloc[line_idx]['line_center_rest']-2*emission_df.iloc[0]['sigma'])
            line_range_high = (1+redshifts[i])*(emission_df.iloc[line_idx]['line_center_rest']+2*emission_df.iloc[0]['sigma'])
            filter_wave_idxs = np.logical_and(sedpy_filt.wavelength>line_range_low, sedpy_filt.wavelength<line_range_high)
            line_transmissions = sedpy_filt.transmission[filter_wave_idxs]
            avg_line_transmission = np.mean(line_transmissions) / np.max(sedpy_filt.transmission)
            return avg_line_transmission
        ha_avg_line_transmission = get_transmission(0, ha_sedpy_filt)
        pab_avg_line_transmission = get_transmission(1, pab_sedpy_filt)
        ha_line_avg_transmissions.append(ha_avg_line_transmission)
        pab_line_avg_transmissions.append(pab_avg_line_transmission)

        ha_pab_ratio = emission_df['ha_pab_ratio'].iloc[0]
        err_ha_pab_ratio_low = emission_df['err_ha_pab_ratio_low'].iloc[0]
        err_ha_pab_ratio_high = emission_df['err_ha_pab_ratio_high'].iloc[0]

        # Test for NII contributions, remove 20%
        if remove_nii:
            ha_pab_ratio = ha_pab_ratio*0.8
            err_ha_pab_ratio_low = err_ha_pab_ratio_low*0.8
            err_ha_pab_ratio_high = err_ha_pab_ratio_high*0.8

        av_emission_fit = compute_ha_pab_av(1/ha_pab_ratio)
        av_emission_fit_high = compute_ha_pab_av(1/(ha_pab_ratio-err_ha_pab_ratio_low))
        av_emission_fit_low = compute_ha_pab_av(1/(ha_pab_ratio+err_ha_pab_ratio_high))
        err_av_emission_fit_low = av_emission_fit - av_emission_fit_low
        err_av_emission_fit_high = av_emission_fit_high - av_emission_fit

        av_16, av_50, av_84 = read_catalog_av(id_msa, zqual_df)
        err_av_50_low = av_50-av_16
        err_av_50_high = av_84-av_50
        av_50s.append(av_50)
        err_av_50s_lows.append(err_av_50_low)
        err_av_50s_highs.append(err_av_50_high)

        if color_var != 'None':
            rgba = cmap(norm(color_array[i]))
        else:
            rgba = 'black'

        #FOr sed method
        sed_av_50 = lineratio_df.iloc[i]['sed_av']
        sed_av_16 = lineratio_df.iloc[i]['sed_av_16']
        sed_av_84 = lineratio_df.iloc[i]['sed_av_84']
        sed_err_av_50_low = sed_av_50-sed_av_16
        sed_err_av_50_high = sed_av_84-sed_av_50
        
        print(f'sed av: {sed_av_50}')
        ax_sed_emfit.errorbar(av_emission_fit, sed_av_50, xerr=np.array([[err_av_emission_fit_low, err_av_emission_fit_high]]).T, yerr=np.array([[sed_err_av_50_low, sed_err_av_50_high]]).T, marker='o', ls='None', color=rgba)
        ax_emfit_prospector.errorbar(av_emission_fit, av_50, xerr=np.array([[err_av_emission_fit_low, err_av_emission_fit_high]]).T, yerr=np.array([[err_av_50_low, err_av_50_high]]).T, marker='o', ls='None', color=rgba)
    # one-to-one
    for ax in axarr:
        ax.plot([-100, 100], [-100, 100], ls='--', color='red', marker='None')
        ax.set_xlim(-1, 2.5)
        ax.set_ylim(-1, 2.5)
        ax.set_xlabel('Emission Fit AV')
    ax_sed_emfit.set_ylabel('SED Method AV')
    ax_sed_emfit.set_ylim(-1,8)
    ax_emfit_prospector.set_ylabel('Prospector AV')
    if color_var != 'None':
        sm =  ScalarMappable(norm=norm, cmap=cmap)
        cbar = fig.colorbar(sm, ax=ax)
        cbar.set_label(color_var, fontsize=16)
        cbar.ax.tick_params(labelsize=16)
    # plt.show()
    fig.savefig(f'/Users/brianlorenz/uncover/Figures/diagnostic_lineratio/sed_and_prospect_vs_fit_{color_var}{add_str}.pdf')
    plt.close('all')
    import sys
    sys.exit()


    # Integrated spectra vs prospector
    fig, ax = plt.subplots(figsize=(6,6))
    for i in range(len(lineratio_df)):
        if color_var != 'None':
            rgba = cmap(norm(color_array[i]))
        ax.plot(lineratio_df['integrated_spec_av'].iloc[i], av_50s[i], marker='o', ls='None', color=rgba)
    ax.plot([-100, 100], [-100, 100], ls='--', color='red', marker='None')
    ax.set_xlim(-2, 11)
    ax.set_ylim(-1, 2.5)
    ax.set_xlabel('Integrated Spectrum AV')
    ax.set_ylabel('Prospector AV')
    if color_var != 'None':
        sm =  ScalarMappable(norm=norm, cmap=cmap)
        cbar = fig.colorbar(sm, ax=ax)
        cbar.set_label(color_var, fontsize=16)
        cbar.ax.tick_params(labelsize=16)
    fig.savefig(f'/Users/brianlorenz/uncover/Figures/diagnostic_lineratio/prospect_vs_intspec_{color_var}{add_str}.pdf')

    # SED vs prospector
    fig, ax = plt.subplots(figsize=(6,6))
    for i in range(len(lineratio_df)):
        if color_var != 'None':
            rgba = cmap(norm(color_array[i]))
        ax.plot(lineratio_df['sed_av'].iloc[i], av_50s[i], marker='o', ls='None', color=rgba)
    ax.plot([-100, 100], [-100, 100], ls='--', color='red', marker='None')
    ax.set_xlim(-2, 10)
    ax.set_ylim(-1, 2.5)
    ax.set_xlabel('SED AV')
    ax.set_ylabel('Prospector AV')
    if color_var != 'None':
        sm =  ScalarMappable(norm=norm, cmap=cmap)
        cbar = fig.colorbar(sm, ax=ax)
        cbar.set_label(color_var, fontsize=16)
        cbar.ax.tick_params(labelsize=16)
    fig.savefig(f'/Users/brianlorenz/uncover/Figures/diagnostic_lineratio/prospect_vs_sed_{color_var}{add_str}.pdf')

    # SED vs prospector (1+z)2
    fig, ax = plt.subplots(figsize=(6,6))
    for i in range(len(lineratio_df)):
        if color_var != 'None':
            rgba = cmap(norm(color_array[i]))
        ax.plot(lineratio_df['sed_av'].iloc[i] / (1+zqual_df_cont_covered['z_spec'].iloc[i])**2, av_50s[i], marker='o', ls='None', color=rgba)
    ax.plot([-100, 100], [-100, 100], ls='--', color='red', marker='None')
    ax.set_xlim(-1, 2.5)
    ax.set_ylim(-1, 2.5)
    ax.set_xlabel('SED AV / (1+z)^2')
    ax.set_ylabel('Prospector AV')
    if color_var != 'None':
        sm =  ScalarMappable(norm=norm, cmap=cmap)
        cbar = fig.colorbar(sm, ax=ax)
        cbar.set_label(color_var, fontsize=16)
        cbar.ax.tick_params(labelsize=16)
    fig.savefig(f'/Users/brianlorenz/uncover/Figures/diagnostic_lineratio/prospect_vs_sed_{color_var}_dividez{add_str}.pdf')

    # SED vs prospector log10
    fig, ax = plt.subplots(figsize=(6,6))
    for i in range(len(lineratio_df)):
        if color_var != 'None':
            rgba = cmap(norm(color_array[i]))
        ax.plot(np.log10(lineratio_df['sed_av'].iloc[i]), av_50s[i], marker='o', ls='None', color=rgba)
    ax.plot([-100, 100], [-100, 100], ls='--', color='red', marker='None')
    ax.set_xlim(-1, 2.5)
    ax.set_ylim(-1, 2.5)
    ax.set_xlabel('log10(SED AV)')
    ax.set_ylabel('Prospector AV')
    if color_var != 'None':
        sm =  ScalarMappable(norm=norm, cmap=cmap)
        cbar = fig.colorbar(sm, ax=ax)
        cbar.set_label(color_var, fontsize=16)
        cbar.ax.tick_params(labelsize=16)
    fig.savefig(f'/Users/brianlorenz/uncover/Figures/diagnostic_lineratio/prospect_vs_sed_{color_var}_log10{add_str}.pdf')


    # SED vs integrated spectrum
    fig, ax = plt.subplots(figsize=(6,6))
    for i in range(len(lineratio_df)):
        if color_var != 'None':
            rgba = cmap(norm(color_array[i]))
        ax.plot(lineratio_df['sed_av'].iloc[i], lineratio_df['integrated_spec_av'].iloc[i], marker='o', ls='None', color=rgba)
    ax.plot([-100, 100], [-100, 100], ls='--', color='red', marker='None')
    ax.set_xlim(-2, 10)
    ax.set_ylim(-2, 10)
    ax.set_xlabel('SED AV')
    ax.set_ylabel('Integrated Spectrum AV')
    if color_var != 'None':
        sm =  ScalarMappable(norm=norm, cmap=cmap)
        cbar = fig.colorbar(sm, ax=ax)
        cbar.set_label(color_var, fontsize=16)
        cbar.ax.tick_params(labelsize=16)
    fig.savefig(f'/Users/brianlorenz/uncover/Figures/diagnostic_lineratio/integratedspec_vs_sed_{color_var}{add_str}.pdf')


def diagnostic_spec_flux_vs_phot_flux():
    fig, ax = plt.subplots(figsize=(6,6))
    zqual_df_cont_covered = ascii.read('/Users/brianlorenz/uncover/zqual_df_cont_covered.csv').to_pandas()
    id_msa_list = zqual_df_cont_covered['id_msa']
    for id_msa in id_msa_list:
        print(f'Making plot for id_msa = {id_msa}')
        fig2, ax2 = plt.subplots(figsize=(6,6))
        spec_df = read_raw_spec(id_msa)
        scale_factor = spec_df['scaled_flux'][100] / spec_df['flux'][100]
        sed_df = get_sed(id_msa)
        integrated_spec_df = ascii.read(f'/Users/brianlorenz/uncover/Data/integrated_specs/{id_msa}_integrated_spec.csv').to_pandas()
        integrated_spec_df['scaled_integrated_spec_flux_jy'] = integrated_spec_df['integrated_spec_flux_jy']*scale_factor
        colors = ['blue', 'orange', 'green', 'red']
        for idx in [1,2,3,4]:
            row_idxs = integrated_spec_df['use_filter_flag'] == idx
            scaled_integrated_fluxes = integrated_spec_df[row_idxs]['scaled_integrated_spec_flux_jy']
            sed_fluxes = sed_df[row_idxs]['flux']
            ax.plot(sed_fluxes, scaled_integrated_fluxes, ls='None', color=colors[idx-1], marker='o')
            ax2.plot(sed_fluxes, scaled_integrated_fluxes, ls='None', color=colors[idx-1], marker='o')
        ax2.set_xlabel('Photometry')
        ax2.set_ylabel('Integrated Spectrum')
        ax2_xlims = ax2.get_xlim()
        ax2_ylims = ax2.get_ylim()
        ax2_min_lim = np.min([ax2_xlims, ax2_ylims])
        ax2_max_lim = np.max([ax2_xlims, ax2_ylims])
        ax2.plot([-100, 100], [-100, 100], color='red', linestyle='--')
        ax2.set_xlim((ax2_min_lim, ax2_max_lim))
        ax2.set_ylim((ax2_min_lim, ax2_max_lim))
        fig2.savefig(f'/Users/brianlorenz/uncover/Figures/diagnostic_lineratio/phot_vs_spec_{id_msa}.pdf')
        plt.close(fig2)
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax_xlims = ax.get_xlim()
    ax_ylims = ax.get_ylim()
    ax_min_lim = np.min([ax_xlims, ax_ylims])
    ax_max_lim = np.max([ax_xlims, ax_ylims])
    ax.plot([-100, 100], [-100, 100], color='red', linestyle='--')
    ax.set_xlim((ax_min_lim,ax_max_lim))
    ax.set_ylim((ax_min_lim,ax_max_lim))    # ax.set_xlim(-2, 10)
    # ax.set_ylim(-1, 2.5)
    ax.set_xlabel('Photometry')
    ax.set_ylabel('Integrated Spectrum')
    

    fig.savefig(f'/Users/brianlorenz/uncover/Figures/diagnostic_lineratio/phot_vs_spec_all.pdf')

def diagnostic_measured_value_vs_truth(truth_var, plot_var, color_var='None'):
    """Scatter plot of one of our measurement methods vs one of our truth methods

    truth_var (str): either 'prospector' or 'emission_fit'
    
    """
    add_str = ''
    filtered_lineratio_df = ascii.read(f'/Users/brianlorenz/uncover/Figures/diagnostic_lineratio/filtered_lineratio_df{add_str}.csv').to_pandas()
    filtered_lineratio_df['prospector_lineratio_50'] = 1/compute_ratio_from_av(filtered_lineratio_df['av_50'])
    filtered_lineratio_df['prospector_lineratio_84'] = 1/compute_ratio_from_av(filtered_lineratio_df['av_16'])
    filtered_lineratio_df['prospector_lineratio_16'] = 1/compute_ratio_from_av(filtered_lineratio_df['av_84'])

    zqual_df_cont_covered = ascii.read('/Users/brianlorenz/uncover/zqual_df_cont_covered.csv').to_pandas()
    # breakpoint()

    fig, ax = plt.subplots(figsize=(6,6))

    # Color coding
    cmap = mpl.cm.inferno
    

    for i in range(len(filtered_lineratio_df)):
        

        row = filtered_lineratio_df.iloc[i]
        id_msa = int(row['id_msa'])

        emission_df = ascii.read(f'/Users/brianlorenz/uncover/Data/emission_fitting/{id_msa}_emission_fits.csv').to_pandas()

        # breakpoint()
        zqual_row = zqual_df_cont_covered[zqual_df_cont_covered['id_msa'] == id_msa]

        if color_var == 'z_spec':
            norm = mpl.colors.Normalize(vmin=1.3, vmax=2.4) 
            rgba = cmap(norm(zqual_row[color_var].iloc[0]))
        elif color_var == 'ha_flux':
            norm = mpl.colors.Normalize(vmin=1e-18, vmax=1e-16) 
            rgba = cmap(norm(emission_df['flux'].iloc[0]))
        elif color_var == 'pab_flux':
            norm = mpl.colors.Normalize(vmin=3e-19, vmax=5e-18) 
            rgba = cmap(norm(emission_df['flux'].iloc[1]))
        elif color_var == 'ha_sigma':
            norm = mpl.colors.Normalize(vmin=35, vmax=65) 
            rgba = cmap(norm(emission_df['sigma'].iloc[0]))
        elif color_var == 'pab_sigma':
            norm = mpl.colors.Normalize(vmin=15, vmax=40) 
            rgba = cmap(norm(emission_df['sigma'].iloc[1]))
        elif color_var == 'ha_snr':
            norm = mpl.colors.Normalize(vmin=10, vmax=60) 
            rgba = cmap(norm(emission_df['signal_noise_ratio'].iloc[0]))
        elif color_var == 'pab_snr':
            norm = mpl.colors.Normalize(vmin=1, vmax=20) 
            rgba = cmap(norm(emission_df['signal_noise_ratio'].iloc[1]))
        elif color_var == 'texp_tot':
            norm = mpl.colors.Normalize(vmin=2, vmax=12) 
            rgba = cmap(norm(zqual_row[color_var].iloc[0]))
        else:
            rgba = 'black'

        if truth_var == 'prospector':
            y_var = 'prospector_lineratio_50'
            y_err=np.array([[row[y_var]-row[y_var.replace('50','16')], row[y_var.replace('50','84')]-row[y_var]]]).T
        if truth_var == 'emission_fit':
            y_var = 'emission_fit_lineratio'
            y_err=np.array([[row['err_emission_fit_lineratio_low'], row['err_emission_fit_lineratio_high']]]).T

        # Factor of 2.5 or so
        ax.errorbar(row[plot_var], row[y_var], yerr=y_err, color=rgba, ls='None', marker='o')
    
    # one-to-one
    ax.plot([-100, 100], [-100, 100], ls='--', color='red', marker='None')

    ax.set_xlim(0, 30)
    ax.set_ylim(0, 30)
    ax.set_xlabel(plot_var)
    ax.set_ylabel(truth_var)
    if color_var != 'None':
        sm =  ScalarMappable(norm=norm, cmap=cmap)
        cbar = fig.colorbar(sm, ax=ax)
        cbar.set_label(color_var, fontsize=16)
        cbar.ax.tick_params(labelsize=16)
    fig.savefig(f'/Users/brianlorenz/uncover/Figures/measurement_vs_fit/{truth_var}_{plot_var}_{color_var}.pdf')
    plt.close('all')
    return

# diagnostic_spec_flux_vs_phot_flux()
# diagnostic_av_emissionfit_vs_av_prospector(color_var='redshift')
# diagnostic_av_emissionfit_vs_av_prospector(color_var='halpha_trasmission')
# diagnostic_av_emissionfit_vs_av_prospector(color_var='pabeta_trasmission')
truth_vars = ['emission_fit', 'prospector']
plot_vars = ['line_ratio_prospector_fit', 'sed_lineratio']
color_vars = ['z_spec', 'ha_flux', 'pab_flux', 'ha_sigma', 'pab_sigma', 'texp_tot', 'ha_snr', 'pab_snr']
for truth_var in truth_vars:
    for plot_var in plot_vars:
        for color_var in color_vars:
            diagnostic_measured_value_vs_truth(truth_var=truth_var, plot_var=plot_var, color_var=color_var)

def lineflux_compare(plot_all=False):
    compare_emfit_df = ascii.read('/Users/brianlorenz/uncover/Figures/diagnostic_lineratio/compare_emfit_df.csv').to_pandas()
    compare_emfit_df['ha_ratio'] = compare_emfit_df['ha_sed_flux'] / compare_emfit_df['ha_emfit_flux']
    compare_emfit_df['pab_ratio'] = compare_emfit_df['pab_sed_flux'] / compare_emfit_df['pab_emfit_flux']

    lineratio_df = ascii.read('/Users/brianlorenz/uncover/Figures/diagnostic_lineratio/lineratio_df.csv').to_pandas()
    filtered_lineratio_df = ascii.read(f'/Users/brianlorenz/uncover/Figures/diagnostic_lineratio/filtered_lineratio_df.csv').to_pandas()
    breakpoint()
    compute_ratio_from_av(A_V_value)


    if plot_all:
        merged_df = pd.merge(compare_emfit_df, lineratio_df, on='id_msa')
        add_str = '_all'
    else:
        merged_df = pd.merge(compare_emfit_df, filtered_lineratio_df, on='id_msa')
        add_str = ''

    fig, axarr = plt.subplots(1,3,figsize=(18,6))
    ax_ha = axarr[0]
    ax_pab = axarr[1]
    ax_ratio = axarr[2]

    ax_ha.plot(merged_df['ha_emfit_flux'], merged_df['ha_sed_flux'], marker='o', ls='None', color='black')
    ax_pab.plot(merged_df['pab_emfit_flux'], merged_df['pab_sed_flux'], marker='o', ls='None', color='black')
    ax_ratio.plot(merged_df['emission_fit_lineratio'], merged_df['sed_lineratio'], marker='o', ls='None', color='black')

    for ax in axarr:
        ax.tick_params(labelsize=12)
        ax.set_xscale('log')
        ax.set_yscale('log')
        xlims = ax.get_xlim()
        ylims = ax.get_ylim()
        ax.plot([-100, 100], [-100, 100], ls='--', color='red', marker='None')
        ax.set_xlim(xlims)
        ax.set_ylim(ylims)
    for ax in [ax_ha, ax_pab]:
        ax.set_ylabel('SED Method Flux')
        ax.set_xlabel('Emission Fit Flux')
    
    ax_ha.set_title('Halpha')
    ax_pab.set_title('PaBeta')

    ax_ratio.set_ylabel('SED Method Ratio')
    ax_ratio.set_xlabel('Emission Fit Ratio')

    fig.savefig(f'/Users/brianlorenz/uncover/Figures/diagnostic_lineratio/lineflux_compare{add_str}.pdf')

def hb_eq_width_continuum(use_subsample=1, line='pab'):
    eq_width_df = ascii.read('/Users/brianlorenz/uncover/Figures/diagnostic_lineratio/eq_width_df.csv').to_pandas()
    # breakpoint()
    fig, ax = plt.subplots(figsize=(6,6))
    eq_width_95 = eq_width_df[eq_width_df['continuum_adjust_factor'] == 0.95]
    eq_width_97 = eq_width_df[eq_width_df['continuum_adjust_factor'] == 0.97]
    eq_width_99 = eq_width_df[eq_width_df['continuum_adjust_factor'] == 0.99]
    eq_dfs = [eq_width_95, eq_width_97, eq_width_99]
    colors = ['black', 'orange', 'blue']
    labels = ['5%', '3%', '1%']
    for i in range(3):
        ax.plot(eq_dfs[i]['PaB_eq_width'], eq_dfs[i]['flux_offset_factor'], marker='o', ls='--', color=colors[i], label=labels[i])
    

    # Vertical lines at the real equivalent widths from our galaxies
    if use_subsample:
        filtered_lineratio_df = ascii.read(f'/Users/brianlorenz/uncover/Figures/diagnostic_lineratio/filtered_lineratio_df.csv').to_pandas()
        lineratio_df = filtered_lineratio_df
        add_str = '_subsamp'
    else:
        lineratio_df = ascii.read('/Users/brianlorenz/uncover/Figures/diagnostic_lineratio/lineratio_df.csv').to_pandas()
    id_msa_list = lineratio_df['id_msa']
    line_eq_widths = []
    for id_msa in id_msa_list:
        emission_df = ascii.read(f'/Users/brianlorenz/uncover/Data/emission_fitting/{id_msa}_emission_fits.csv').to_pandas()
        if line=='pab':
            line_eq_width = emission_df['equivalent_width_aa'].iloc[1]
            line_label = 'Sample PaB'
            line_color = 'red'
        elif line=='ha':
            line_eq_width = emission_df['equivalent_width_aa'].iloc[0]
            line_label = 'Sample Ha'
            line_color = 'magenta'
        line_eq_widths.append(line_eq_width)
    ax.vlines(line_eq_widths, -5, 10, colors=line_color, linestyles='--', label=line_label)
    
    
    ax.set_xscale('log')
    ax.set_yscale('log')
    import matplotlib.ticker as mticker
    ax.xaxis.set_major_formatter(mticker.ScalarFormatter())
    ax.yaxis.set_major_formatter(mticker.ScalarFormatter())
    ax.yaxis.set_minor_formatter(mticker.ScalarFormatter())

    ax.set_xlabel('Equivalent Width')
    ax.set_ylabel('Flux Offset Factor')

    ax.set_ylim(0.95, 5)

    ax.legend()


    fig.savefig(f'/Users/brianlorenz/uncover/Figures/diagnostic_lineratio/eq_width_test_{line}.pdf')


# lineflux_compare(plot_all=True)

# hb_eq_width_continuum(line='ha')
# hb_eq_width_continuum(line='pab')

# diagnostic_av_emissionfit_vs_av_prospector(remove_nii=True)
# diagnostic_measured_value_vs_truth(truth_var='emission_fit', plot_var='line_ratio_prospector_fit', color_var='z_spec')
