import matplotlib.pyplot as plt
from astropy.io import ascii
import matplotlib as mpl
import numpy as np
from uncover_read_data import read_lineflux_cat, get_id_msa_list, read_SPS_cat
# from plot_vals import scale_aspect
from scipy import stats
import pandas as pd


def plot_prop_vs_fe(id_msa_list, prop, color_var='he_snr', add_str=''):
    lineratio_df = ascii.read(f'/Users/brianlorenz/uncover/Figures/diagnostic_lineratio/lineratio_df.csv', data_start=1).to_pandas()
    zqual_df_cont_covered = ascii.read('/Users/brianlorenz/uncover/zqual_df_cont_covered.csv').to_pandas()
    sps_df = read_SPS_cat()

    fig, ax_prop_fe = plt.subplots(1, 1, figsize = (7, 6))
    fontsize = 12
    
    
    ax_prop_fe.set_ylabel('(FeII / PaB) ratio', fontsize=fontsize)

    cmap = mpl.cm.inferno
    
    fe_pab_ratios = []
    mass_values = []
    

    for id_msa in id_msa_list:
        fe_df = ascii.read(f'/Users/brianlorenz/uncover/Data/emission_fitting_fe_only/{id_msa}_emission_fits.csv').to_pandas()
        pab_em_df = ascii.read(f'/Users/brianlorenz/uncover/Data/emission_fitting_pabeta_only/{id_msa}_emission_fits.csv').to_pandas()
        lineratio_row = lineratio_df[lineratio_df['id_msa'] == id_msa]
        zqual_df_cont_covered_row = zqual_df_cont_covered[zqual_df_cont_covered['id_msa']==id_msa]
        sps_row = sps_df[sps_df['id_msa'] == id_msa]

        pab_flux = pab_em_df.iloc[0]['flux']
        fe_flux = fe_df.iloc[0]['flux']
        redshift = fe_df.iloc[0]['redshift'] - 1
        fe_pab_ratio = fe_flux / pab_flux
        fe_pab_ratios.append(fe_pab_ratio)

        fe_sigma = fe_df.iloc[0]['sigma']
        fe_snr = fe_df.iloc[0]['signal_noise_ratio']

        if prop == 'fe_snr':
            ax_prop_fe.set_xlim(0, vmax=5) 
            x_val = fe_snr
            prop_str = '_fe_snr'
        elif prop == 'sed_ratio':
            ax_prop_fe.set_xlim(0, vmax=18) 
            print(lineratio_row['sed_lineratio'])
            x_val = lineratio_row['sed_lineratio']
            prop_str = '_sed_ratio'
        elif prop == 'redshift':
            ax_prop_fe.set_xlim(1.3, 2.3) 
            x_val = zqual_df_cont_covered_row['z_spec']
            prop_str = '_redshift'
        elif prop == 'metallicity':
            ax_prop_fe.set_xlim(-1.2, 0.1) 
            x_val = sps_row['met_50']
            prop_str = '_metallicity'
        elif prop == 'mass':
            ax_prop_fe.set_xlim(7.8, 11) 
            x_val = sps_row['mstar_50'].iloc[0]
            mass_values.append(x_val)
            prop_str = '_mass'
        elif prop == 'logsfr':
            ax_prop_fe.set_xlim(0.1, 100) 
            x_val = np.log10(sps_row['sfr100_50'])
            prop_str = '_logsfr'
            ax_prop_fe.set_xscale('log')
        
        else:
            rgba = 'black'
            prop_str = ''
        rgba = 'black'

        ax_prop_fe.set_xlabel('Mass', fontsize=fontsize)
        # ax_prop_fe.set_xlabel(prop_str, fontsize=fontsize)


        ax_prop_fe.plot(x_val, fe_pab_ratio, marker='o', color=rgba, ls='None', mec='black')
        # ax_prop_fe.text(x_val, fe_pab_ratio, f'{id_msa}')
        # ax_prop_fe.text(x_val, fe_pab_ratio, f'{redshift:0.2f}')

    
    
    # ax_prop_fe.set_yscale('log')
    # ax_prop_fe.set_ylim(0.1e-19, 5e-17)
    ax_prop_fe.set_ylim(0, 0.75)
    # ax_prop_fe.legend(loc=2)

    y_int, slope = fit_fe_mass(fe_pab_ratios, mass_values)
    masses = np.arange(6.5,12,0.1)
    fe_pab_ratio_predicted = y_int+slope*masses
    # ax_prop_fe.plot(masses, fe_pab_ratio_predicted, ls='--', color='red', label='best fit', marker='None')
    # ax_prop_fe.legend()

    line_p1 = np.array([masses[0], fe_pab_ratio_predicted[0]])
    line_p2 = np.array([masses[-1], fe_pab_ratio_predicted[-1]])
    def get_distance(datapoint):
        distance = np.cross(line_p2-line_p1,datapoint-line_p1)/np.linalg.norm(line_p2-line_p1)
        return distance
    
    distances = [get_distance(np.array([mass_values[i], fe_pab_ratios[i]])) for i in range(len(mass_values))]
    scatter = np.median(np.abs(distances))
    median_fe_pab_ratio = np.median(fe_pab_ratios)
    median_fe_pab_ratios = [median_fe_pab_ratio for i in range(len(id_msa_list))]
    print(f'median: {median_fe_pab_ratio}')


    fe_cor_df = pd.DataFrame(zip([y_int], [slope], [scatter]), columns=['y_int', 'slope', 'scatter'])
    fe_cor_df.to_csv('/Users/brianlorenz/uncover/Data/generated_tables/fe_cor_df.csv', index=False)

    fe_cor_df_indiv = pd.DataFrame(zip(id_msa_list, fe_pab_ratios, median_fe_pab_ratios), columns=['id_msa', 'fe_pab_ratio', 'median_fe_pab_ratios'])
    fe_cor_df_indiv.to_csv('/Users/brianlorenz/uncover/Data/generated_tables/fe_cor_df_indiv.csv', index=False)


    scale_aspect(ax_prop_fe)

    fig.savefig(f'/Users/brianlorenz/uncover/Figures/diagnostic_lineratio/he_plots/fe_vs{prop_str}{add_str}.pdf', bbox_inches='tight')
    # plt.show()

def fit_fe_mass(fe_pab_ratios, mass_values):
    from scipy import stats
    res = stats.linregress(mass_values, fe_pab_ratios)
    print(f"R-squared: {res.rvalue**2:.6f}")
    y_int = res.intercept
    slope = res.slope
    return y_int, slope


def scale_aspect(ax):
    ylims = ax.get_ylim()
    xlims = ax.get_xlim()
    ydiff = np.abs(ylims[1]-ylims[0])
    xdiff = np.abs(xlims[1]-xlims[0])
    ax.set_aspect(xdiff/ydiff)

if __name__ == "__main__":
    # id_msa_list = get_id_msa_list(full_sample=False)
    # id_msa_list = [14573, 18471, 19179, 25147, 32111, 38163, 39855, 42213, 47875]
    # plot_prop_vs_fe(id_msa_list, prop='mass')
    
    
    
    # id_msa_list = [6291, 14573, 18471, 19179, 19981, 21834, 25147, 32111, 38163, 39855, 42213, 47875]
    id_msa_list = [6291, 18471, 21834, 22755, 25147, 32111, 35401, 42203, 42213, 47875]
    plot_prop_vs_fe(id_msa_list, prop='mass', add_str='_all')
    pass