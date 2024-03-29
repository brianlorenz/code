# Plots the balmer decrement vs a vairiety of properies
import initialize_mosdef_dirs as imd
import matplotlib.pyplot as plt
from astropy.io import ascii
import numpy as np
from matplotlib.patches import Ellipse
from ellipses_for_plotting import get_ellipse_shapes
import matplotlib as mpl
from plot_vals import *
from dust_model import *
from sympy.solvers import solve
from sympy import Symbol





def plot_cluster_sfr_metals(plot_ssfr=False, plot_re=False, plot_sanders=False, mass_color=False, show_mass=False):
    summary_df = ascii.read(imd.loc_cluster_summary_df).to_pandas()
    # ignore_groups = imd.ignore_groups
    ignore_groups = []
    fig, ax = plt.subplots(figsize = (8,8))

    # Plot the points
    for i in range(len(summary_df)):
        if i in ignore_groups:
            continue
        row = summary_df.iloc[i]

        ax.set_ylim(8.2, 8.95)
        ax_y_len = 0.75
        if plot_ssfr==True:
            ax.set_xlim(-9.6, -8.1)
            ax_x_len = 1.5
        else:
            ax.set_xlim(0, 2.6)
            ax_x_len = 2.6
       
        fontsize=full_page_axisfont

        cmap = mpl.cm.inferno
        if mass_color==True:
            norm = mpl.colors.Normalize(vmin=9, vmax=11.5) 
            rgba = cmap(norm(row['median_log_mass']))
        else:
            # norm = mpl.colors.Normalize(vmin=3, vmax=5.5)
            norm = mpl.colors.Normalize(vmin=0, vmax=3) 
            # rgba = cmap(norm(row['balmer_dec']))
            rgba = cmap(norm(row['balmer_av_with_limit']))
            # norm = mpl.colors.Normalize(vmin=0.5, vmax=2.5) 
            # rgba = cmap(norm(row['balmer_dec']))
        
        if plot_ssfr == True:
            x_points = row['computed_log_ssfr_with_limit']
            ax.set_xlabel('log(sSFR)', fontsize=fontsize)
        else:
            x_points = row['computed_log_sfr_with_limit']
            ax.set_xlabel(sfr_label, fontsize=fontsize)
            if plot_re==True:
                # Not supported yet
                x_points = np.log10(10**row['computed_log_sfr_with_limit'] / row['re_median'])
                ax.set_xlabel('log(SFR/R_e)', fontsize=fontsize)
        if row['flag_balmer_lower_limit'] == 1:
            marker = '^'
            yerr=yerr=np.array([[0,0]]).T
        else:
            marker = 'o'
            yerr=yerr=np.array([[row['err_O3N2_metallicity_low'], row['err_O3N2_metallicity_high']]]).T
    
        ax.errorbar(x_points, row['O3N2_metallicity'], yerr=yerr, color=rgba, marker=marker, ls='None', zorder=3)

        ax.text(x_points, row['O3N2_metallicity'], f"{int(row['groupID'])}", color='black')
        zorder=15-i
        ax.set_ylabel('12 + log(O/H)', fontsize=fontsize)
    
    # Plot lines on constant dust
    metal_vals = np.arange(8.1, 9.0, 0.1)
    x = Symbol('x')
   
    def get_slope(x1, x2, y1, y2):
        slope = (y2-y1) /(x2-x1) 
        print(slope)
        return slope

    # # low mass
    # A_lambda = 0.85
    # re = 0.25
    # sfrs = [float(solve(const2 * 10**(a*metal_vals[i]) * (x/(re**2))**(1/n) - A_lambda, x)[0]) for i in range(len(metal_vals))] #Dust
    # sfrs=np.array(sfrs)
    # log_sfrs = np.log10(sfrs)
    # if plot_ssfr == True:
    #     log_mass = 9.75
    #     x_plot = np.log10(sfrs/(10**log_mass))
    #     label = '$R_\mathrm{eff} = 0.25$, $A_\mathrm{balmer} = 0.85$' + f', mass={log_mass}'
    # else:
    #     x_plot = log_sfrs
    #     if plot_re==True:
    #         x_plot = np.log10(10**log_sfrs/re)
    #     label = '$R_\mathrm{eff} = 0.25$, $A_\mathrm{balmer} = 0.85$'
    # ax.plot(x_plot, metal_vals, ls='--', color='#8E248C', marker='None', zorder=2)
    # get_slope(x_plot[0], x_plot[-1], metal_vals[0], metal_vals[-1])

    def plot_dust(A_lambda, re=1):
        # low mass
        sfrs = [float(solve(const2 * 10**(a*metal_vals[i]) * (x/(re**2))**(1/n) - A_lambda, x)[0]) for i in range(len(metal_vals))] #Dust
        sfrs=np.array(sfrs)
        # metal_vals = np.log10(A_lambda / ((const2) * ((sfrs/(re**2))**(1/n)))) / a
        log_sfrs = np.log10(sfrs)
        x_plot = log_sfrs
        label = '$R_\mathrm{eff} = 0.25$, $A_\mathrm{balmer} = 0.85$'
        rgba_color = cmap(norm(A_lambda))
        ax.plot(x_plot, metal_vals, ls='--', color=rgba_color, marker='None', zorder=2)
    for i in range(len(summary_df)):
        plot_dust(summary_df.iloc[i]['balmer_av'], 4*summary_df.iloc[i]['median_re'])
    # plot_dust(0.5)
    # plot_dust(1)
    # plot_dust(1.5)
    # plot_dust(2, re=2)
    # plot_dust(2.5, re=2)

    # high mass
    if plot_ssfr == True:
        pass
    else:
        pass
        # A_lambda = 2.0
        # re = 0.5
        # sfrs = [float(solve(const2 * 10**(a*metal_vals[i]) * (x/(re**2))**(1/n) - A_lambda, x)[0]) for i in range(len(metal_vals))] #Dust
        # sfrs=np.array(sfrs)
        # log_sfrs = np.log10(sfrs)
        # if plot_re==True:
        #     log_sfrs = np.log10(10**np.log10(sfrs)/re)
        # ax.plot(log_sfrs, metal_vals, ls='--', color='skyblue', marker='None', label='$R_\mathrm{eff} = 0.5$, $A_\mathrm{balmer} = 2.0$')


    # mass/metal/sfr relation
    def compute_metals(log_mass, fm_s, re):
        '''
        Parameters:
        log_mass: Log stellar mass
        fm_s: log sfrs (array)
        '''
        fm_m = (log_mass-10)*np.ones(len(fm_s))
        fm_metals = fundamental_plane(fm_m, fm_s)
        add_str2 = ''
        if plot_sanders==True:
            fm_metals = sanders_plane(log_mass, fm_s)
            add_str2 = '_sanders'
        if plot_ssfr == True:
            x_plot = np.log10(10**fm_s/(10**log_mass))
        elif plot_re == True:
            x_plot = np.log10(10**fm_s/(re))
        else:
            x_plot = fm_s
        return x_plot, fm_metals, add_str2

    fm_s = np.arange(0, 3, 0.1)
    log_mass = 9.55
    re = 0.25
    x_plot, fm_metals_lowm_bot, add_str2 = compute_metals(log_mass, fm_s, re) 
    if mass_color == True and show_mass==True:
        rgba_massline = cmap(norm(log_mass))
        ax.plot(x_plot, fm_metals_lowm_bot, marker='None', color=rgba_massline, ls='-')
    log_mass = 9.8
    x_plot, fm_metals_lowm_top, add_str2 = compute_metals(log_mass, fm_s, re) 
    # ax.plot(x_plot, fm_metals_lowm_top, ls='--', color='black', marker='None', label=f'Stellar Mass = {log_mass}, {add_str2}')
    if mass_color == True and show_mass==True:
        rgba_massline = cmap(norm(log_mass))
        ax.plot(x_plot, fm_metals_lowm_top, marker='None', color=rgba_massline, ls='-')
    if show_mass == False:
        ax.fill_between(x_plot, fm_metals_lowm_bot, fm_metals_lowm_top, color='black', alpha=0.35, zorder=1)
    get_slope(x_plot[10], x_plot[16], fm_metals_lowm_bot[10], fm_metals_lowm_bot[16])

    



    log_mass = 10.2
    re = 0.4
    x_plot, fm_metals_highm_bot, add_str2 = compute_metals(log_mass, fm_s, re) 
    if mass_color == True and show_mass==True:
        rgba_massline = cmap(norm(log_mass))
        ax.plot(x_plot, fm_metals_highm_bot, marker='None', color=rgba_massline, ls='-')
        
    log_mass = 10.35
    x_plot, fm_metals_highm_top, add_str2 = compute_metals(log_mass, fm_s, re) 
    if mass_color == True and show_mass==True:
        rgba_massline = cmap(norm(log_mass))
        ax.plot(x_plot, fm_metals_highm_top, marker='None', color=rgba_massline, ls='-')
    if mass_color == False:
        ax.fill_between(x_plot, fm_metals_highm_bot, fm_metals_highm_top, color='black', alpha=0.2, zorder=1)
    get_slope(x_plot[10], x_plot[16], fm_metals_highm_bot[10], fm_metals_highm_bot[16])

    log_mass = 10.6
    x_plot, fm_metals_higher_m, add_str2 = compute_metals(log_mass, fm_s, re) 
    if mass_color == True and show_mass==True:
        rgba_massline = cmap(norm(log_mass))
        ax.plot(x_plot, fm_metals_higher_m, marker='None', color=rgba_massline, ls='-')

    log_mass = 11.00
    x_plot, fm_metals_very_high_m, add_str2 = compute_metals(log_mass, fm_s, re) 
    if mass_color == True and show_mass==True:
        rgba_massline = cmap(norm(log_mass))
        ax.plot(x_plot, fm_metals_very_high_m, marker='None', color=rgba_massline, ls='-')

    cbar = fig.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap), ax=ax, fraction=0.046, pad=0.04)
    # cbar.set_label(balmer_label, fontsize=fontsize)
    if mass_color==True:
        cbar.set_label('median log mass', fontsize=fontsize)
    else:
        cbar.set_label('A$_\mathrm{balmer}$ with limit', fontsize=fontsize)
    cbar.ax.tick_params(labelsize=fontsize)
    ax.tick_params(labelsize=full_page_axisfont)
    # ax.legend()

    ax.text(1.345, 8.21, 'Low M$_*$ FMR', fontsize=18, rotation=315)
    ax.text(1.91, 8.33, 'High M$_*$ FMR', fontsize=18, rotation=315)
    # ax.text(0.18, 8.60, 'A$_\mathrm{balmer} = 0.85$', fontsize=16, rotation=308, color='#8E248C')
    # ax.text(0.80, 8.71, 'A$_\mathrm{balmer} = 1.9$', fontsize=16, rotation=308, color='#FF640A')
    
    ax.plot([0],[0],ls='--',color='dimgrey',marker='None',label='Dust Model')
    ax.legend(fontsize=16)
    plt.setp(ax.get_yticklabels()[0], visible=False)   


    if plot_ssfr==True:
        add_str = '_ssfr'
    elif plot_re==True:
        add_str = '_divre'
    elif plot_sanders==True:
        add_str = '_sanders'
    else:
        add_str = ''
    if mass_color==True:
        fig.savefig(imd.cluster_dir + f'/cluster_stats/' + 'sfr_metallicity_masscolor.pdf',bbox_inches='tight')
    else:
        fig.savefig(imd.cluster_dir + f'/cluster_stats/' + 'sfr_metallicity.pdf',bbox_inches='tight')


# plot_sfr_metals('whitaker_sfms_boot100')
# plot_sfr_metals('whitaker_sfms_boot100', plot_sanders=True)
# plot_sfr_metals('whitaker_sfms_boot100', plot_re=True)


plot_cluster_sfr_metals(plot_sanders=True)
# plot_cluster_sfr_metals(plot_sanders=True, mass_color=True)
# plot_cluster_sfr_metals(plot_sanders=True, mass_color=True, show_mass=True)

