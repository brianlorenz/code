import numpy as np
from fit_emission_uncover_old import line_list
from uncover_read_data import read_SPS_cat
from dust_equations_prospector import dust2_to_AV
from astropy.io import ascii

avneb_str = 'A$_{\\mathrm{V,neb}}$'

# theoretical scalings (to Hb, from naveen's paper)
ha_factor = 2.79
hb_factor = 1
pab_factor = 0.155
paa_factor = 0.305

# nii_correction_ha_flux = 0.75
def get_nii_correction(id_msa, sps_df = []):
    if len(sps_df) == 0:
        sps_df = read_SPS_cat()
    sps_row = sps_df[sps_df['id_msa'] == id_msa]
    logmass = sps_row['mstar_50'].iloc[0]
    logsfr = np.log10(sps_row['sfr100_50'].iloc[0])
    predicted_metallicity = sanders_plane(logmass, logsfr)
    nii6585_ha_rat = sanders_nii_ratio(predicted_metallicity) # Adjusted relation
    niicombined_ha_rat = nii6585_ha_rat * 1.5 # From the other plot
    nii_correction_factor = 1 / (1+niicombined_ha_rat)
    return nii_correction_factor

def get_nii_correction_formmet(id_msa, sps_df = []):
    if len(sps_df) == 0:
        sps_df = read_SPS_cat()
    sps_row = sps_df[sps_df['id_msa'] == id_msa]
    metallicity = sps_row['met_50'].iloc[0]
    nii6585_ha_rat = sanders_nii_ratio(metallicity, linear_scale=0) # Adjusted relation
    niicombined_ha_rat = nii6585_ha_rat * 1.5 # From the other plot
    nii_correction_factor = 1 / (1+niicombined_ha_rat)
    return nii_correction_factor

def get_fe_correction(id_msa, boot=False): # From fe_diagnostics.py
    fe_cor_df_indiv = ascii.read('/Users/brianlorenz/uncover/Data/generated_tables/fe_cor_df_indiv.csv').to_pandas()
    fe_cor_df_row = fe_cor_df_indiv[fe_cor_df_indiv['id_msa'] == id_msa]
    if len(fe_cor_df_row) == 0:
        predicted_fe_pab_ratio = fe_cor_df_indiv['median_fe_pab_ratios'].iloc[0]
    else:
        predicted_fe_pab_ratio = fe_cor_df_row['fe_pab_ratio'].iloc[0]
    if boot == True:
        fe_scatter = np.std(fe_cor_df_indiv['fe_pab_ratio'])
        predicted_fe_pab_ratio = predicted_fe_pab_ratio+np.random.normal(loc=0, scale=fe_scatter)
    
    # if id_msa in [14573]:
    #     predicted_fe_pab_ratio = 0
    pab_correction_factor = 1 / (1+predicted_fe_pab_ratio)
    return pab_correction_factor

def get_fe_correction_bymass(id_msa, sps_df = []): # From fe_diagnostics.py
    if len(sps_df) == 0:
        sps_df = read_SPS_cat()
    sps_row = sps_df[sps_df['id_msa'] == id_msa]
    log_mass = sps_row['mstar_50'].iloc[0]
    fe_cor_df = ascii.read('/Users/brianlorenz/uncover/Data/generated_tables/fe_cor_df.csv').to_pandas()
    predicted_fe_pab_ratio = fe_cor_df['y_int'].iloc[0]+fe_cor_df['slope'].iloc[0]*log_mass
    pab_correction_factor = 1 / (1+predicted_fe_pab_ratio)
    return pab_correction_factor

ha_wave = line_list[0][1]/10000
pab_wave = line_list[1][1]/10000
paa_wave = 18750/10000
hb_wave = 0.4861

def calzetti_law(wavelength_um):
    if wavelength_um >= 0.6300 and wavelength_um <= 2.2000:
        k_lambda = 2.659 * (-1.857 + 1.040 / wavelength_um) + 4.05
    if wavelength_um >= 0.1200  and wavelength_um < 0.6300:
        k_lambda = 2.659 * (-2.156 + 1.509 / wavelength_um - 0.198 / wavelength_um**2 + 0.011 / wavelength_um**3) + 4.05
    return k_lambda

def compute_ha_paalpha_av(paalpha_ha_ratio):
    """ PaB / Ha is the ratio you need, should be slightly greater than 1/20"""
    R_V_value = 4.05
    intrinsic_ratio = paa_factor / ha_factor
    k_factor = 2.5/(calzetti_law(ha_wave) - calzetti_law(paa_wave))
    A_V_value = R_V_value*k_factor*np.log10(paalpha_ha_ratio/intrinsic_ratio)
    return A_V_value

def compute_paalpha_pabeta_av(paalpha_pabeta_ratio):
    """ PaB / Ha is the ratio you need, should be slightly greater than 1/20"""
    R_V_value = 4.05
    intrinsic_ratio = paa_factor / pab_factor
    k_factor = 2.5/(calzetti_law(pab_wave) - calzetti_law(paa_wave))
    A_V_value = R_V_value*k_factor*np.log10(paalpha_pabeta_ratio/intrinsic_ratio)
    return A_V_value


def compute_ha_pab_av(pab_ha_ratio):
    """ PaB / Ha is the ratio you need, should be slightly greater than 1/20"""
    R_V_value = 4.05
    intrinsic_ratio = pab_factor / ha_factor
    k_factor = 2.5/(calzetti_law(ha_wave) - calzetti_law(pab_wave))
    A_V_value = R_V_value*k_factor*np.log10(pab_ha_ratio/intrinsic_ratio)
    return A_V_value
def compute_ha_pab_av2(ha_pab_ratio): # Does the same thin but it's more intuitive this way
    """ PaB / Ha is the ratio you need, should be slightly greater than 1/20"""
    R_V_value = 4.05
    intrinsic_ratio = ha_factor / pab_factor
    k_factor = 2.5/(calzetti_law(pab_wave) - calzetti_law(ha_wave))
    A_V_value = R_V_value*k_factor*np.log10(ha_pab_ratio/intrinsic_ratio)
    return A_V_value

def compute_ratio_from_av(A_V_value):
    """ PaB / Ha is the ratio you need, should be slightly greater than 1/20"""
    R_V_value = 4.05
    intrinsic_ratio = pab_factor / ha_factor
    k_factor = 2.5/(calzetti_law(ha_wave) - calzetti_law(pab_wave))
    pab_ha_ratio = 10**(A_V_value / (R_V_value*k_factor)) * intrinsic_ratio
    return pab_ha_ratio

def compute_ha_pab_av_from_dustmap(dustmap_ratio):
    """ PaB / Ha is the ratio you need, should be slightly greater than 1/20. Already have pab ratio there, so don'tneed intrinsice"""
    R_V_value = 4.05
    k_factor = 2.5/(calzetti_law(ha_wave) - calzetti_law(pab_wave))
    intrinsic_ratio = pab_factor / ha_factor
    A_V_value = R_V_value*k_factor*np.log10(dustmap_ratio / intrinsic_ratio)
    return A_V_value

def compute_balmer_av(balmer_dec):
    R_V_value = 4.05
    intrinsic_ratio = ha_factor / hb_factor
    k_factor = 2.5/(calzetti_law(hb_wave) - calzetti_law(ha_wave))
    A_V_value = R_V_value*k_factor*np.log10(balmer_dec/intrinsic_ratio)
    return A_V_value

def read_catalog_av(id_msa, zqual_df):
    sps_df = read_SPS_cat()
    # id_dr2 = zqual_df[zqual_df['id_msa']==id_msa]['id_DR2'].iloc[0]
    sps_row = sps_df[sps_df['id_msa']==id_msa]
    dust_16 = sps_row['dust2_16'].iloc[0]
    dust_50 = sps_row['dust2_50'].iloc[0]
    dust_84 = sps_row['dust2_84'].iloc[0]
    av_16 = dust2_to_AV(dust_16)
    av_50 = dust2_to_AV(dust_50)
    av_84 = dust2_to_AV(dust_84)
    print(f'A_V 50 for id_msa {id_msa}: {av_50}')
    return av_16, av_50, av_84


def sanders_plane(log_mass, log_sfr):
    u60 = log_mass - 0.6*log_sfr
    y = u60 - 10
    metallicity = 8.8 + (0.188*y) + (-0.22 * y**2) + (-0.0531 * y**3)
    return metallicity

def sanders_nii_ratio(met_12_log_OH, linear_scale = 8.69):
    c0 = -0.606
    c1 = 1.28
    c2 = -0.435
    c3 = -0.485
    x = met_12_log_OH - linear_scale
    log_nii_ratio = c0 + (c1*x) + (c2 * x**2) + (c3 * x**3)
    nii_ratio = 10**log_nii_ratio
    return nii_ratio


# print(compute_ha_pab_av(1/16))
# print(get_fe_correction(18471))
