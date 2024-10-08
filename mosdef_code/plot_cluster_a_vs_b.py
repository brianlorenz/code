import initialize_mosdef_dirs as imd
import matplotlib.pyplot as plt
import matplotlib as mpl
from plot_vals import *
from leja_sfms_redshift import leja2022_sfms
from astropy.io import ascii
import os
import pandas as pd
import sys
from matplotlib.patches import Ellipse



if os.path.exists(imd.loc_cluster_summary_df): 
    cluster_summary_df = imd.read_cluster_summary_df()

def plot_cluster_summaries(x_var, y_var, savename, color_var='None', plot_lims='None', one_to_one=False, ignore_groups=[], log=False, lower_limit=False, add_leja=False, yerr=False, prospector_run_name = ''):
    """Plots two columsn of cluster_summary_df against each other
    
    Parameters:
    x_var (str): x variable to plot
    y_var (str): y variable to plot
    savename (str): Name to save the figure under
    color_var (str): 'None' or the column to use as color
    plot_lims (list of 4): [xmin, xmax, ymin, ymax]
    one_to_one (boolean): Set to True to add a 1-1 line
    log (boolean): Set to True to make it a log-log plot
    lower_limit (boolean): Set to true to use lower limit SFRs and hollow out those points
    add_leja (boolean): If True, add the sfms from Leja 2022 to the plot
    yerr (boolean): Set to true to plot errorbars on the yaxis
    prospector_run_name (str): Set to the prospector run name if using
    """

    fig, ax = plt.subplots(figsize = (8,8))

    if lower_limit == True:
        y_var = y_var+'_with_limit'
        savename = savename+'_with_limit'

   

    if y_var == 'override_flux_with_limit':
        cluster_summary_df2 = ascii.read(imd.mosdef_dir + '/Clustering_20230823_scaledtoindivha/cluster_summary.csv').to_pandas()
        cluster_summary_df['override_flux_with_limit'] = cluster_summary_df2[x_var]

    for i in range(len(cluster_summary_df)):
        if i in ignore_groups:
            continue
        row = cluster_summary_df.iloc[i]

        if prospector_run_name != '':
            if os.path.exists(imd.prospector_emission_fits_dir + f'/{prospector_run_name}_emission_fits/{i}_emission_fits.csv'):
                prospector_emission = ascii.read(imd.prospector_emission_fits_dir + f'/{prospector_run_name}_emission_fits/{i}_emission_fits.csv').to_pandas()
                ha_row = prospector_emission[prospector_emission['line_name']=='Halpha']
                row[y_var] = ha_row[y_var]
            else:
                continue
        
        if x_var=='sfr50':
            row[x_var] = np.log10(row[x_var])

        if y_var=='AV_diff':
            row[y_var] = row['balmer_av'] - row['Prospector_AV_50']
            if row[y_var]>2.5:
                continue
            ax.axhline(0, ls='--', color='black')
        
        if color_var=='AV_diff':
            row['AV_diff'] = row['balmer_av'] - row['Prospector_AV_50']
        
        if color_var != 'None':
            cmap = mpl.cm.inferno
            norm = assign_color(color_var)
            rgba = cmap(norm(row[color_var]))
        else:
            rgba = 'black'

        # Make the point hollow if it's a lower limit
        if lower_limit == True:
            if row['flag_balmer_lower_limit']==1:
                marker='^'
            else:
                marker='o'
        else:
            marker='o'
        if yerr == True:
            try:
                ax.errorbar(row[x_var], row[y_var], yerr=np.array([[row['err_'+y_var+'_low'], row['err_'+y_var+'_high']]]).T, color=rgba, marker=marker, ls='None', zorder=3, mec='black')
            except:
                pass
            try:
                ax.errorbar(row[x_var], row[y_var], yerr=row['err_'+y_var], color=rgba, marker=marker, ls='None', zorder=3, mec='black')
            except:
                pass
        else:
            ax.plot(row[x_var], row[y_var], color=rgba, marker=marker, ls='None', zorder=3, mec='black')
            
        # ax.text(row[x_var], row[y_var], f"{int(row['groupID'])}", color='black')
        ax.text(row[x_var], row[y_var], f"{int(row['paperID'])}", color='black')

    if add_leja:
        add_leja_sfms(ax)
        ax.legend()

    if plot_lims != 'None':
        ax.set_xlim(plot_lims[0], plot_lims[1])
        ax.set_ylim(plot_lims[2], plot_lims[3])


    if log:
        ax.set_xscale('log')
        ax.set_yscale('log')

    if color_var!='None':
        cbar = fig.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap), ax=ax, fraction=0.046, pad=0.04)
        cbar.set_label(color_var, fontsize=full_page_axisfont)
        cbar.ax.tick_params(labelsize=full_page_axisfont)
    ax.tick_params(labelsize=full_page_axisfont)

    ax.set_xlabel(x_var, fontsize=full_page_axisfont)
    ax.set_ylabel(y_var, fontsize=full_page_axisfont)
    if y_var == 'override_flux_with_limit':
        ax.set_ylabel(x_var + '_older_method', fontsize=full_page_axisfont)
    if prospector_run_name != '':
        ax.set_ylabel('Prospector ' + y_var, fontsize=full_page_axisfont)

    if one_to_one:
        xlims = ax.get_xlim()
        ylims = ax.get_ylim()
        ax.plot([-20, 20e60], [-20, 20e60], ls='--', color='red')
        ax.set_xlim(xlims)
        ax.set_ylim(ylims)
        # ax.plot([0,1],[0,1], transform=ax.transAxes, ls='--', color='red')

    fig.savefig(imd.cluster_dir + f'/cluster_stats/{savename}.pdf', bbox_inches='tight')
    plt.close('all')

def plot_ratio(x_var_numerator, x_var_denominator, y_var_numerator, y_var_denominator, savename, color_var='None', plot_lims='None', one_to_one=False, ignore_groups=[], log=False, lower_limit=False):
    """Plots two columsn of cluster_summary_df against each other
    
    Parameters:
    savename (str): Name to save the figure under
    color_var (str): 'None' or the column to use as color
    plot_lims (list of 4): [xmin, xmax, ymin, ymax]
    one_to_one (boolean): Set to True to add a 1-1 line
    log (boolean): Set to True to make it a log-log plot
    lower_limit (boolean): Set to true to use lower limit SFRs and hollow out those points
    """

    fig, ax = plt.subplots(figsize = (8,8))

    if lower_limit == True:
        pass
        # y_var = y_var+'_with_limit'
        # savename = savename+'_with_limit'

    for i in range(len(cluster_summary_df)):
        if i in ignore_groups:
            continue
        row = cluster_summary_df.iloc[i]

        if color_var != 'None':
            cmap = mpl.cm.inferno
            norm = assign_color(color_var)
        else:
            rgba = 'black'

        # Make the point hollow if it's a lower limit
        if lower_limit == True:
            if row['flag_balmer_lower_limit']==1:
                marker='^'
            else:
                marker='o'
        else:
            marker='o'
        x_ratio = row[x_var_numerator] / row[x_var_denominator]
        y_ratio = row[y_var_numerator] / row[y_var_denominator]
        ax.plot(x_ratio, y_ratio, color=rgba, marker=marker, ls='None', zorder=3, mec='black')

    if plot_lims != 'None':
        ax.set_xlim(plot_lims[0], plot_lims[1])
        ax.set_ylim(plot_lims[2], plot_lims[3])

    if one_to_one:
        # ax.plot([-(1e18), 1e10], [-(1e18), 1e10], ls='--', color='red')
        ax.plot([0,1],[0,1], transform=ax.transAxes, ls='--', color='red')

    if log:
        ax.set_xscale('log')
        ax.set_yscale('log')

    cbar = fig.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap), ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label(color_var, fontsize=full_page_axisfont)
    cbar.ax.tick_params(labelsize=full_page_axisfont)
    ax.tick_params(labelsize=full_page_axisfont)

    ax.set_xlabel(f'{x_var_numerator} / {x_var_denominator}', fontsize=full_page_axisfont)
    ax.set_ylabel(f'{y_var_numerator} / {y_var_denominator}', fontsize=full_page_axisfont)

    fig.savefig(imd.cluster_dir + f'/cluster_stats/{savename}.pdf', bbox_inches='tight')
    plt.close('all')

def plot_a_vs_b_paper(x_var, y_var, x_label, y_label, savename, axis_obj='False', color_var='None', plot_lims='None', lower_limit=False, one_to_one=False, ignore_groups=[], log=False, add_leja=False, yerr=False, xerr=False, prospector_run_name = '', fig='None', use_color_df=True, prospector_xerr=False, factor_of_2=False, upper_limit=False, add_numbers=False, set_gray=False, contour_ellipse_errs=False):
    """Plots two columsn of cluster_summary_df against each other
    
    Parameters:
    x_var (str): x variable to plot
    y_var (str): y variable to plot
    savename (str): Name to save the figure under
    color_var (str): 'None' or the column to use as color
    plot_lims (list of 4): [xmin, xmax, ymin, ymax]
    one_to_one (boolean): Set to True to add a 1-1 line
    log (boolean): Set to True to make it a log-log plot
    add_leja (boolean): If True, add the sfms from Leja 2022 to the plot
    yerr (boolean): Set to true to plot errorbars on the yaxis
    prospector_run_name (str): Set to the prospector run name if using
    """
    if yerr == False:
        overall_yerr = False
    else:
        overall_yerr = True

    if axis_obj == 'False':
        fig, ax = plt.subplots(figsize=(8, 8))
    else:
        ax = axis_obj

    if y_var == 'balmer_av_with_limit':
        pass
        # y_var = 'balmer_av_with_limit_2'
        # cluster_summary_df['balmer_av_with_limit_2'] = 2* cluster_summary_df['balmer_av_with_limit']

    for i in range(len(cluster_summary_df)):
        if i in ignore_groups:
            continue
        row = cluster_summary_df.iloc[i]
        markersize = get_row_size(i)

        if x_var == 'ssfr50' or x_var == 'Prospector_ssfr50_target_mass' or  x_var == 'Prospector_ssfr50_normmedian_mass' or x_var=='sfr50':
            row[x_var] = np.log10(row[x_var])
        if x_var == 'sfr_surface':
            row[x_var] = np.log10((10**row['computed_log_sfr_with_limit'])/ (2*np.pi * row['median_re']**2))
            print(row[x_var])
        if prospector_run_name != '':
            if os.path.exists(imd.prospector_emission_fits_dir + f'/{prospector_run_name}_emission_fits/{i}_emission_fits.csv'):
                prospector_emission = ascii.read(imd.prospector_emission_fits_dir + f'/{prospector_run_name}_emission_fits/{i}_emission_fits.csv').to_pandas()
                ha_row = prospector_emission[prospector_emission['line_name']=='Halpha']
                row[y_var] = ha_row[y_var]
            else:
                continue

        if color_var != 'None':
            cmap = mpl.cm.inferno
            # cmap = mpl.cm.RuBu
            cmap = mpl.cm.get_cmap('OrRd')
            norm = assign_color(color_var)
            rgba = cmap(norm(row[color_var]))
        else:
            rgba = 'black'
        if use_color_df == True:
            rgba = get_row_color(i)
       
 
        # Make the point a triangle if it's a lower limit
        rotation = 0
        mec = 'black'
        markerfacecolor=rgba
        if lower_limit == True:
            if row['flag_balmer_lower_limit']==1:
                marker='s'
                yerr = False
            else:
                marker='o'
                yerr = True
        if lower_limit == 3:
            if row['flag_balmer_lower_limit']==1:
                marker='s'
                yerr = True
            else:
                marker='o'
                yerr = True
        elif lower_limit > 5:
            if row['flag_balmer_lower_limit']==1:
                rotation = lower_limit
                # marker = (3, 0, rotation)
                arrow = u'$\u2191$'
                rotated_marker = mpl.markers.MarkerStyle(marker=arrow)
                rotated_marker._transform = rotated_marker.get_transform().rotate_deg(rotation)
                marker = rotated_marker
                yerr = False
                marker='s'
                # markerfacecolor='None'
                if set_gray:
                    rgba = 'grey'
                    markerfacecolor = 'grey'
                xrange = plot_lims[1] - plot_lims[0]
                yrange = plot_lims[3] - plot_lims[2]
                arrow_width = 0.005
                arrow_length = 0.04
                if lower_limit <= 135:
                    ax.arrow((row[x_var]-plot_lims[0])/xrange, (row[y_var]-plot_lims[2])/yrange, arrow_length, 0, color=rgba, width=arrow_width, transform=ax.transAxes)
                if lower_limit >=135 and lower_limit <= 225:
                    ax.arrow((row[x_var]-plot_lims[0])/xrange, (row[y_var]-plot_lims[2])/yrange, 0, arrow_length, color=rgba, width=arrow_width, transform=ax.transAxes)
                if lower_limit >= 225 and lower_limit <= 315:
                    ax.arrow((row[x_var]-plot_lims[0])/xrange, (row[y_var]-plot_lims[2])/yrange, -arrow_length, 0, color=rgba, width=arrow_width, transform=ax.transAxes)
                if lower_limit >= 315:
                    ax.arrow((row[x_var]-plot_lims[0])/xrange, (row[y_var]-plot_lims[2])/yrange, 0, -arrow_length, color=rgba, width=arrow_width, transform=ax.transAxes)
                
            else:
                marker='o'
                yerr = True
        elif upper_limit == True:
            if row['flag_hb_limit']==1:
                marker='v'
                yerr = False
            else:
                marker='o'
                yerr = True
        else:
            marker='o'
        
        
        if yerr == True and overall_yerr==True:
            if prospector_xerr == True:
                print('plotting here')
                prospector_xerr_values = np.array([[row[x_var]-row[x_var.replace('_50','_16')], row[x_var.replace('_50','_84')]-row[x_var]]]).T
                ax.errorbar(row[x_var], row[y_var], xerr=prospector_xerr_values, yerr=np.array([[row['err_'+y_var+'_low'], row['err_'+y_var+'_high']]]).T, color=rgba, marker=marker, ls='None', zorder=3, mec=mec, markerfacecolor=markerfacecolor, ms=markersize)
            elif xerr == True:
                if 'Prospector' in y_var:
                    yerr_low = row[y_var]-row[y_var.replace('_50','_16')]
                    yerr_high = row[y_var]-row[y_var.replace('_50','_16')]
                else:
                    yerr_low = row['err_'+y_var+'_low']
                    yerr_high = row['err_'+y_var+'_high']
                    

                ax.errorbar(row[x_var], row[y_var], xerr=np.array([[row['err_'+x_var+'_low'], row['err_'+x_var+'_high']]]).T, yerr=np.array([[yerr_low, yerr_high]]).T, color=rgba, marker=marker, ls='None', zorder=3, mec=mec, markerfacecolor=markerfacecolor, ms=markersize)
            else:
                try:
                    ax.errorbar(row[x_var], row[y_var], yerr=np.array([[row['err_'+y_var+'_low'], row['err_'+y_var+'_high']]]).T, color=rgba, marker=marker, ls='None', zorder=3, mec=mec, markerfacecolor=markerfacecolor, ms=markersize)
                except:
                    pass
                try:
                    ax.errorbar(row[x_var], row[y_var], yerr=np.array([[row[y_var]-row[y_var.replace('50','16')], row[y_var.replace('50','84')]-row[y_var]]]).T, color=rgba, marker=marker, ls='None', zorder=3, mec=mec, markerfacecolor=markerfacecolor, ms=markersize)
                except:
                    pass
                try:
                    ax.errorbar(row[x_var], row[y_var], yerr=row['err_'+y_var], color=rgba, marker=marker, ls='None', zorder=3, mec=mec, markerfacecolor=markerfacecolor, ms=markersize)
                except:
                    pass
        else:
            ax.plot(row[x_var], row[y_var], color=rgba, marker=marker, ls='None', zorder=3, mec=mec, markerfacecolor=markerfacecolor, ms=markersize)
            
        if add_numbers==True:
            ax.text(row[x_var], row[y_var], f"{int(row['groupID'])}", color='black', fontsize=15)

        if contour_ellipse_errs == True:
            if row['flag_balmer_lower_limit']==1:
                continue
            sfr_err_df = ascii.read(imd.cluster_dir + f'/sfr_errs/{i}_sfr_errs.csv').to_pandas()
            x = np.array(np.log10(sfr_err_df['sfr']))
            if y_var == 'AV_difference_with_limit':
                new_stellar_avs = []
                for i in range(len(sfr_err_df)):
                    # breakpoint()
                    center = row['Prospector_AV_50']
                    low_err = row['Prospector_AV_50'] - row['Prospector_AV_16']
                    high_err = row['Prospector_AV_84'] - row['Prospector_AV_50']
                    half = np.random.random()
                    if half < 0.5:
                        new_stellar_av = np.random.normal(loc=center, scale=low_err)
                        if new_stellar_av > center:
                            new_stellar_av = center - (new_stellar_av - center)
                    else:
                        new_stellar_av = np.random.normal(loc=center, scale=high_err)
                        if new_stellar_av < center:
                            new_stellar_av = center + (center - new_stellar_av)
                    new_stellar_avs.append(new_stellar_av)
                sfr_err_df['monte_stellar_av'] = new_stellar_avs
                sfr_err_df['av_difference'] = sfr_err_df['balmer_av'] - sfr_err_df['monte_stellar_av']
                y = np.array(sfr_err_df['av_difference'])
            else:
                y = np.array(sfr_err_df['balmer_av'])
            
            # Combine x and y into a single array for easier computation
            data = np.vstack([x, y]).T

            # Calculate the mean and covariance matrix
            mean = np.mean(data, axis=0)
            cov = np.cov(data.T)

            # Eigenvalues and eigenvectors
            eigenvalues, eigenvectors = np.linalg.eigh(cov)

            # Sort the eigenvalues and eigenvectors
            sorted_indices = np.argsort(eigenvalues)[::-1]
            eigenvalues = eigenvalues[sorted_indices]
            eigenvectors = eigenvectors[:, sorted_indices]

            # Get the angle of the ellipse
            angle = np.arctan2(*eigenvectors[:, 0][::-1])

            # Get the width and height of the ellipse
            width, height = 2 * np.sqrt(eigenvalues)

            # Create the ellipse
            ellipse = Ellipse(xy=mean, width=width, height=height, angle=np.degrees(angle),
                            edgecolor=rgba, facecolor='none', linestyle='-')
            ax.add_patch(ellipse)
        # if y_var == 'computed_log_ssfr_with_limit' and row['flag_hb_limit']==1:
        #     # breakpoint()
        #     ax.plot(row[x_var], np.log10(row['Prospector_ssfr50_normmedian_mass']), color=rgba, marker=marker, ls='None', zorder=1000, mec=mec, markerfacecolor=markerfacecolor, ms=markersize)
        #     ax.plot([row[x_var], row[x_var]], [row['computed_log_ssfr_with_limit'], np.log10(row['Prospector_ssfr50_normmedian_mass'])], color=rgba, marker='None', ls='-', zorder=3)

    
    if add_leja:
        redshift = 2
        mode = 'ridge'
        logmasses = np.arange(9, 11, 0.02)
        logSFRs = np.array([leja2022_sfms(logmass, redshift, mode) for logmass in logmasses])
        logssfrs = np.log10((10**logSFRs) / (10**logmasses))
        ax.plot(logmasses, logssfrs, color='black', marker='None', ls='-', zorder=1, label=f'Leja SFMS z={redshift}, type={mode}')
        ax.legend()

    if plot_lims != 'None':
        ax.set_xlim(plot_lims[0], plot_lims[1])
        ax.set_ylim(plot_lims[2], plot_lims[3])

    if log:
        ax.set_xscale('log')
        ax.set_yscale('log')
    if color_var != 'None':
        cbar = fig.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap), ax=ax, fraction=0.046, pad=0.04)
        if color_var=='balmer_av':
            color_var='A$_\mathrm{V,neb}$'
        cbar.set_label(color_var, fontsize=full_page_axisfont)
        cbar.ax.tick_params(labelsize=full_page_axisfont)
    ax.tick_params(labelsize=full_page_axisfont)

    ax.set_xlabel(x_label, fontsize=full_page_axisfont)
    ax.set_ylabel(y_label, fontsize=full_page_axisfont)
    if prospector_run_name != '':
        ax.set_ylabel('Prospector ' + y_var, fontsize=full_page_axisfont)

    if one_to_one:
        xlims = ax.get_xlim()
        ylims = ax.get_ylim()
        ax.plot([-20, 20e60], [-20, 20e60], ls='--', color='red')
        ax.set_xlim(xlims)
        ax.set_ylim(ylims)
        # ax.plot([0,1],[0,1], transform=ax.transAxes, ls='--', color='red')

    if factor_of_2:
        # ax.plot([-10, 10], [-9, 11], ls='--', color='red', label='Nebular A$_V$ = 1+Stellar A$_V$')
        ax.plot([-10, 10], [-20, 20], ls='--', color='orange', label='Nebular A$_V$ = 2*Stellar A$_V$')

    
    if axis_obj == 'False':
        fig.savefig(imd.cluster_dir + f'/paper_figures/{savename}.pdf', bbox_inches='tight')

def assign_color(color_var):
    if color_var=='balmer_dec':
        norm = mpl.colors.Normalize(vmin=3, vmax=5) 
    elif color_var=='balmer_dec_with_limit':
        norm = mpl.colors.Normalize(vmin=3, vmax=6) 
    elif color_var=='O3N2_metallicity':
        norm = mpl.colors.Normalize(vmin=8.2, vmax=9) 
    elif color_var=='norm_median_log_mass' or color_var=='median_log_mass':
        norm = mpl.colors.Normalize(vmin=9, vmax=11) 
    elif color_var=='prospector_log_mass':
        norm = mpl.colors.Normalize(vmin=12, vmax=14) 
    elif color_var=='median_U_V':
        norm = mpl.colors.Normalize(vmin=0.5, vmax=1.5) 
    elif color_var=='balmer_av':
        norm = mpl.colors.Normalize(vmin=0, vmax=3.5) 
    elif color_var=='Prospector_AV_50':
        norm = mpl.colors.Normalize(vmin=0, vmax=1.0) 
    elif color_var=='computed_log_sfr_with_limit':
        norm = mpl.colors.Normalize(vmin=0, vmax=1.5) 
    elif color_var=='AV_diff':
        norm = mpl.colors.Normalize(vmin=0, vmax=2.5) 
    elif color_var=='AV_difference_with_limit':
        norm = mpl.colors.Normalize(vmin=0, vmax=2.5) 
    else:
        norm = mpl.colors.Normalize(vmin=-10, vmax=10) 
    return norm

def add_leja_sfms(ax, mode='mean'):
    redshift = 2
    # mode = 'ridge'
    logmasses = np.arange(9, 11, 0.02)
    logSFRs = np.array([leja2022_sfms(logmass, redshift, mode) for logmass in logmasses])
    logssfrs = np.log10((10**logSFRs) / (10**logmasses))
    ax.plot(logmasses, logssfrs, color='black', marker='None', ls='--', zorder=1, label=f'Leja SFMS z={redshift}, {mode}')
    cluster_summary_df = ascii.read(imd.loc_cluster_summary_df).to_pandas()
    sfrs = [] 
    for i in range(len(cluster_summary_df)):
        sfrs.append(leja2022_sfms(cluster_summary_df.iloc[i]['median_log_mass'], redshift, mode))
    sfms_offset = cluster_summary_df['computed_log_sfr_with_limit']-sfrs
    cluster_summary_df['sfms_offset_with_limit'] = sfms_offset
    cluster_summary_df.to_csv(imd.loc_cluster_summary_df, index=False)



def make_plots_a_vs_b(reduce_plot_count=False, reduce_prospector_plots=False):
    """Plots variables in cluster_summary_df against each other
    
    Parameters:
    reduce_plot_count (boolean): False to make all plot, True to make only some
    prospector_plots (boolean): True to make all plot, false to make only some

    """
    try:
        ignore_groups = imd.ignore_groups
    except:
        ignore_groups = []
    lower_limit = True

    plot_cluster_summaries('median_log_mass', 'computed_log_sfr', 'sfr_mass_balmercolor', color_var='balmer_av', ignore_groups=ignore_groups, lower_limit=lower_limit, yerr=True, plot_lims=[9, 11, 0, 2.5])
    plot_cluster_summaries('median_log_mass', 'computed_log_sfr', 'sfr_mass_stellarcolor', color_var='Prospector_AV_50', ignore_groups=ignore_groups, lower_limit=lower_limit, yerr=True, plot_lims=[9, 11, 0, 2.5])
    plot_cluster_summaries('median_log_mass', 'computed_log_sfr', 'sfr_mass_avdiff', color_var='AV_diff', ignore_groups=ignore_groups, lower_limit=lower_limit, yerr=True, plot_lims=[9, 11, 0, 2.5])
    plot_cluster_summaries('sfms_offset_with_limit', 'AV_diff', 'sfms_offset_avdiff', color_var='median_log_mass', ignore_groups=ignore_groups, lower_limit=False, yerr=False, plot_lims=[-1, 1, -0.5, 2.5])


    if reduce_plot_count == False:
        # # SFR comparison plots
        plot_cluster_summaries('norm_median_halphas', 'ha_flux', 'sfrs/ha_flux_compare_norm', color_var='balmer_dec', plot_lims=[6e-18, 8e-16, 6e-18, 8e-16], one_to_one=True, ignore_groups=ignore_groups, log=True)
        plot_cluster_summaries('median_indiv_halphas', 'ha_flux', 'sfrs/ha_flux_compare_nonorm', color_var='median_log_mass', plot_lims=[6e-18, 8e-16, 6e-18, 8e-16], one_to_one=True, ignore_groups=ignore_groups, log=True)
        plot_cluster_summaries('median_halpha_luminosity', 'ha_flux', 'sfrs/ha_luminosity_compare_nonorm', color_var='median_log_mass', plot_lims=[3e41, 4e42, 3e41, 4e42], one_to_one=True, ignore_groups=ignore_groups, log=True, yerr=True)
        plot_cluster_summaries('median_indiv_halphas', 'ha_flux', 'sfrs/ha_flux_compare_nonorm_balmer', color_var='balmer_dec', plot_lims=[6e-18, 8e-16, 6e-18, 8e-16], one_to_one=True, ignore_groups=ignore_groups, log=True)
        plot_cluster_summaries('median_log_sfr', 'computed_log_sfr', 'sfrs/sfr_compare', color_var='balmer_dec', plot_lims=[0.3, 3, 0.3, 3], one_to_one=True, ignore_groups=ignore_groups, lower_limit=lower_limit, yerr=True)
        plot_cluster_summaries('median_log_ssfr', 'computed_log_ssfr', 'sfrs/ssfr_compare', color_var='balmer_dec', plot_lims=[-10.7, -6.5, -10.7, -6.5], one_to_one=True, ignore_groups=ignore_groups, lower_limit=lower_limit, yerr=True)
        plot_cluster_summaries('computed_log_sfr_with_limit', 'median_indiv_computed_log_sfr', 'sfrs/sfr_indiv_vs_cluster', color_var='balmer_dec', plot_lims=[0.3, 3, 0.3, 3], one_to_one=True, ignore_groups=ignore_groups, lower_limit=lower_limit)
        plot_cluster_summaries('computed_log_ssfr_with_limit', 'median_indiv_computed_log_ssfr', 'sfrs/ssfr_indiv_vs_cluster', color_var='balmer_dec', plot_lims=[-10.7, -6.5, -10.7, -6.5], one_to_one=True, ignore_groups=ignore_groups, lower_limit=lower_limit)
        plot_cluster_summaries('computed_log_sfr_with_limit', 'override_flux', 'sfrs/sfr_compare_new_vs_old_method', color_var='balmer_dec', plot_lims=[0.3, 3, 0.3, 3], one_to_one=True, ignore_groups=ignore_groups, lower_limit=lower_limit)
        plot_cluster_summaries('median_log_sfr', 'median_indiv_computed_log_sfr', 'sfrs/sfr_indiv_vs_mosdef', color_var='balmer_dec', plot_lims=[0.3, 3, 0.3, 3], one_to_one=True, ignore_groups=ignore_groups, lower_limit=lower_limit)

        # # Find which groups have accurate Ha and Hb measurements:
        ignore_groups = np.array(cluster_summary_df[cluster_summary_df['err_balmer_dec_high']>1].index)
        plot_cluster_summaries('norm_median_halphas', 'ha_flux', 'sfrs/ha_flux_compare_balmer_accurate', color_var='balmer_dec', plot_lims=[6e-18, 8e-16, 6e-18, 8e-16], one_to_one=True, ignore_groups=ignore_groups, log=True)
        plot_cluster_summaries('median_log_sfr', 'computed_log_sfr', 'sfrs/sfr_compare_balmer_accurate', color_var='balmer_dec', plot_lims=[0.3, 3, 0.3, 3], one_to_one=True, ignore_groups=ignore_groups, lower_limit=lower_limit, yerr=True)
        plot_cluster_summaries('median_log_ssfr', 'computed_log_ssfr', 'sfrs/ssfr_compare_balmer_accurate', color_var='balmer_dec', plot_lims=[-10.7, -6.5, -10.7, -6.5], one_to_one=True, ignore_groups=ignore_groups, lower_limit=lower_limit, yerr=True)
        try:
            ignore_groups = imd.ignore_groups
        except:
            ignore_groups = []

        # # SFMS
        plot_cluster_summaries('median_log_mass', 'median_log_ssfr', 'sfrs/sfms', color_var='O3N2_metallicity', ignore_groups=ignore_groups)
        plot_cluster_summaries('median_log_mass', 'computed_log_ssfr', 'sfrs/sfms_computed', color_var='O3N2_metallicity', ignore_groups=ignore_groups, lower_limit=lower_limit, yerr=True, plot_lims=[9, 11, -10.5, -7.5])
        plot_cluster_summaries('median_log_mass', 'computed_log_ssfr', 'sfrs/sfms_computed_balmercolor', color_var='balmer_dec', ignore_groups=ignore_groups, lower_limit=lower_limit, yerr=True, plot_lims=[9, 11, -10.5, -7.5])
        plot_cluster_summaries('median_log_mass', 'computed_log_ssfr', 'sfrs/sfms_with_Leja', color_var='balmer_dec', ignore_groups=ignore_groups, lower_limit=lower_limit, add_leja=True, yerr=True, plot_lims=[9, 11, -10.5, -7.5])

        # # SFR Mass
        plot_cluster_summaries('median_log_mass', 'computed_log_sfr', 'sfrs/sfr_mass_lower_limit', color_var='balmer_dec', ignore_groups=ignore_groups, lower_limit=lower_limit, yerr=True, plot_lims=[9, 11, 0.3, 3])
        plot_cluster_summaries('median_log_mass', 'median_log_sfr', 'sfrs/sfr_mass_median', color_var='balmer_dec', ignore_groups=ignore_groups, plot_lims=[9, 11, 0.3, 3])

        # # Halpha compare
        plot_cluster_summaries('ha_flux', 'median_indiv_halphas', 'sfrs/halpha_norm_compare', color_var='balmer_dec', ignore_groups=ignore_groups, one_to_one=True, log=True)

        # #AV comparison
        plot_cluster_summaries('AV', 'balmer_av', 'sfrs/av_compare', color_var='norm_median_log_mass', ignore_groups=ignore_groups, one_to_one=True, plot_lims=[0, 4.5, 0, 4.5], lower_limit=lower_limit, yerr=True)

        # # Trying to diagnose what makes the SFR high
        imd.check_and_make_dir(imd.cluster_dir + f'/cluster_stats/sfrs/diagnostics/')
        plot_cluster_summaries('median_indiv_balmer_decs', 'balmer_dec', 'sfrs/diagnostics/balmer_dec_compare', color_var='median_log_mass', ignore_groups=ignore_groups, lower_limit=lower_limit, yerr=True, one_to_one=True)
        sys.exit()
        plot_cluster_summaries('redshift', 'computed_log_sfr', 'sfrs/diagnostics/sfr_z_lower_limit', color_var='balmer_dec_with_limit', ignore_groups=ignore_groups, lower_limit=lower_limit, yerr=True)
        plot_cluster_summaries('target_galaxy_redshifts', 'computed_log_sfr', 'sfrs/diagnostics/sfr_ztarget_lower_limit', color_var='balmer_dec_with_limit', ignore_groups=ignore_groups, lower_limit=lower_limit, yerr=True)
        plot_cluster_summaries('target_galaxy_median_log_mass', 'computed_log_sfr', 'sfrs/diagnostics/sfr_masstarget_lower_limit', color_var='balmer_dec_with_limit', ignore_groups=ignore_groups, lower_limit=lower_limit, yerr=True)
        plot_cluster_summaries('median_log_mass', 'computed_log_sfr', 'sfrs/diagnostics/sfr_massgroup_lower_limit', color_var='balmer_dec_with_limit', ignore_groups=ignore_groups, lower_limit=lower_limit, yerr=True)
        plot_cluster_summaries('ha_flux', 'computed_log_sfr', 'sfrs/diagnostics/sfr_haflux_lower_limit', color_var='balmer_dec_with_limit', ignore_groups=ignore_groups, lower_limit=lower_limit, yerr=True)
        plot_cluster_summaries('balmer_dec', 'computed_log_sfr', 'sfrs/diagnostics/sfr_balmer_lower_limit', color_var='balmer_dec_with_limit', ignore_groups=ignore_groups, lower_limit=lower_limit, yerr=True)
        plot_cluster_summaries('balmer_av', 'computed_log_sfr', 'sfrs/diagnostics/sfr_balmerav_lower_limit', color_var='balmer_dec_with_limit', ignore_groups=ignore_groups, lower_limit=lower_limit, yerr=True)
        plot_cluster_summaries('balmer_dec_with_limit', 'computed_log_sfr', 'sfrs/diagnostics/sfr_balmerlimit_lower_limit', color_var='balmer_dec_with_limit', ignore_groups=ignore_groups, lower_limit=lower_limit, yerr=True)
        plot_cluster_summaries('ha_flux', 'computed_log_sfr', 'sfrs/diagnostics/sfr_haflux_lower_limit', color_var='balmer_dec_with_limit', ignore_groups=ignore_groups, lower_limit=lower_limit, yerr=True)
        plot_cluster_summaries('hb_flux', 'computed_log_sfr', 'sfrs/diagnostics/sfr_hbflux_lower_limit', color_var='balmer_dec_with_limit', ignore_groups=ignore_groups, lower_limit=lower_limit, yerr=True)

    if reduce_prospector_plots == False:    
        # #SNR Plots
        # plot_cluster_summaries('hb_snr', 'balmer_dec_snr', 'sfrs/hbeta_balmer_snr', color_var='balmer_dec_with_limit', ignore_groups=ignore_groups, one_to_one=True)

        # Prospector emission - to use, set the yvar to the prospector name, and prospector_run_name to be accurate
        imd.check_and_make_dir(imd.cluster_dir + '/cluster_stats/prospector/')
        plot_cluster_summaries('ha_flux', 'luminosity', 'sfrs/prospector_ha_compare', color_var='median_log_mass', one_to_one=True, ignore_groups=ignore_groups, log=True, prospector_run_name='dust4_new_scale')

        # Prospector eline properties:
        plot_cluster_summaries('prospector_balmer_dec', 'balmer_dec', 'prospector/balmer_dec_compare', color_var='median_log_mass', ignore_groups=ignore_groups, lower_limit=lower_limit, one_to_one=True, plot_lims=[2.7, 6.5, 2.7, 6.5])
        plot_cluster_summaries('O3N2_metallicity', 'prospector_O3N2_metallicity', 'prospector/metallicity_compare', color_var='median_log_mass', ignore_groups=ignore_groups, one_to_one=True, plot_lims=[7.7, 9, 7.7, 9])
        plot_cluster_summaries('O3N2_metallicity', 'prospector_O3N2_metallicity', 'prospector/metallicity_compare_prospmassscolor', color_var='prospector_log_mass', ignore_groups=ignore_groups, one_to_one=True, plot_lims=[7.7, 9, 7.7, 9])
        plot_cluster_summaries('O3N2_metallicity', 'prospector_O3N2_metallicity', 'prospector/metallicity_compare_balmercolor', color_var='balmer_dec_with_limit', ignore_groups=ignore_groups, one_to_one=True, plot_lims=[7.7, 9, 7.7, 9])
        plot_cluster_summaries('cluster_av_prospector_log_ssfr', 'prospector_log_ssfr', 'prospector/prospector_ssfr_compare', color_var='balmer_dec_with_limit', ignore_groups=ignore_groups, one_to_one=True, plot_lims=[-11, -7.5, -11, -7.5])
        plot_cluster_summaries('cluster_av_prospector_log_ssfr', 'computed_log_ssfr', 'prospector/ssfr_compare_to_cluster', color_var='balmer_dec_with_limit', ignore_groups=ignore_groups, lower_limit=lower_limit, one_to_one=True, plot_lims=[-11, -7.5, -11, -7.5])

        # Prospector Dust Index
        plot_cluster_summaries('computed_log_ssfr_with_limit', 'dustindex50', 'prospector/dust_index_ssfr', color_var='balmer_dec', ignore_groups=ignore_groups)
        plot_cluster_summaries('median_log_mass', 'dustindex50', 'prospector/dust_index_mass', color_var='balmer_dec', ignore_groups=ignore_groups)
        plot_cluster_summaries('balmer_dec', 'dustindex50', 'prospector/dust_index_balmer', color_var='balmer_dec', ignore_groups=ignore_groups)
        plot_cluster_summaries('AV', 'dustindex50', 'prospector/dust_index_av', color_var='balmer_dec', ignore_groups=ignore_groups)
        plot_cluster_summaries('logzsol50', 'dustindex50', 'prospector/dust_index_prospmetals', color_var='balmer_dec', ignore_groups=ignore_groups)
        plot_cluster_summaries('O3N2_metallicity', 'dustindex50', 'prospector/dust_index_metals', color_var='balmer_dec', ignore_groups=ignore_groups)

        # Prospector AV
        plot_cluster_summaries('median_log_mass', 'dust2_50', 'prospector/dust2_mass', color_var='balmer_dec', ignore_groups=ignore_groups)
        plot_cluster_summaries('AV', 'dust2_50', 'prospector/dust2_medianAVA', color_var='balmer_dec', ignore_groups=ignore_groups, one_to_one=True)
        plot_cluster_summaries('Prospector_AV_50', 'dustindex50', 'prospector/dustindex_AV', color_var='median_log_mass', ignore_groups=ignore_groups, one_to_one=True)


        #Compare 
        plot_cluster_summaries('prospector_log_mass', 'target_galaxy_median_log_mass', 'prospector/prospector_mass_compare', color_var='median_log_mass', ignore_groups=ignore_groups, one_to_one=True)
        plot_cluster_summaries('prospector_log_mass', 'median_log_mass', 'prospector/prospector_mass_compare_cluster', color_var='median_log_mass', ignore_groups=ignore_groups, one_to_one=True)
        plot_cluster_summaries('sfr50', 'computed_log_sfr', 'prospector/prospector_sfr_compare', color_var='median_log_mass', ignore_groups=ignore_groups, one_to_one=True, lower_limit=True)


    # Dust model
    plot_cluster_summaries('O3N2_metallicity', 'balmer_av', 'dust_model_vis/abalmer_vs_metals', color_var='median_log_mass', ignore_groups=ignore_groups, lower_limit=True)
    plot_cluster_summaries('computed_log_sfr_with_limit', 'balmer_av', 'dust_model_vis/abalmer_vs_sfr', color_var='median_log_mass', ignore_groups=ignore_groups, lower_limit=True)
    plot_cluster_summaries('O3N2_metallicity', 'computed_log_sfr', 'dust_model_vis/sfr_metal', color_var='median_log_mass', ignore_groups=ignore_groups, lower_limit=True)

    # Other
    plot_cluster_summaries('computed_log_sfr_with_limit', 'AV_diff', 'sfr_vs_balmer_diff', color_var='median_log_mass', ignore_groups=ignore_groups, lower_limit=False, yerr=False, plot_lims=[-0.7, 2.1, -1.5, 2.5])

    



# make_plots_a_vs_b(reduce_plot_count=True, reduce_prospector_plots=False)