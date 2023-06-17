import initialize_mosdef_dirs as imd
from cosmology_calcs import flux_to_luminosity
from compute_new_sfrs import correct_ha_lum_for_dust, ha_lum_to_sfr
import numpy as np

def compute_cluster_sfrs():
    cluster_summary_df = imd.read_cluster_summary_df()

    halpha_fluxes = cluster_summary_df['ha_flux']
    redshifts = cluster_summary_df['redshift']
    balmer_avs = cluster_summary_df['balmer_av']
    # log_mean_masses = cluster_summary_df['mean_log_mass']
    log_norm_median_masses = cluster_summary_df['norm_median_log_mass']
    
    # Another method is to try to compute using A_V rather than mass
    AV = cluster_summary_df['AV']

    #Convert the Balmer AV to A_Halpha using https://iopscience.iop.org/article/10.1088/0004-637X/763/2/145/pdf
    balmer_ahalphas = 3.33*(balmer_avs / 4.05)
    # ahalphas = 3.33*(AV / 4.05)

    # Convert ha to luminsoty
    halpha_lums = flux_to_luminosity(halpha_fluxes, redshifts)

    # Get dust-corrected halpha
    intrinsic_halpha_lums = correct_ha_lum_for_dust(halpha_lums, balmer_ahalphas)
    # intrinsic_halpha_lums = correct_ha_lum_for_dust(halpha_lums, ahalphas)

    # Derive SFR from Hao 2011
    halpha_sfrs = ha_lum_to_sfr(intrinsic_halpha_lums, imf='Hao_Chabrier')
    log_halpha_sfrs = np.log10(halpha_sfrs)

    # Divide by mean mass for sSFR
    halpha_ssfrs = halpha_sfrs / (10**log_norm_median_masses)
    log_halpha_ssfrs = np.log10(halpha_ssfrs)

    cluster_summary_df['computed_log_sfr'] = log_halpha_sfrs
    cluster_summary_df['computed_log_ssfr'] = log_halpha_ssfrs

    cluster_summary_df.to_csv(imd.loc_cluster_summary_df, index=False)



# compute_cluster_sfrs()