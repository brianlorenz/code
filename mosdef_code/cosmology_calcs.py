# Codes for any cosmological calculations

import numpy as np
from astropy.cosmology import WMAP9 as cosmo
from astropy import units as u


def luminosity_to_flux(luminosities, redshift):
    '''
    Given a redshift, converts a luminosity (erg/s) to a flux (erg/s/cm^2). Uses WMAP9 cosmology

    Parameters:
    luminosities (np.array): Luminosities to convert, ideally in erg/s
    redshift (float): Redshift of the object, e.g. 1.7

    Returns:
    fluxes (np.array): output fluxes in units of luminosities/cm^2
    '''

    # Find the luminostiy distance, then convert to cm
    lum_dist = cosmo.luminosity_distance(redshift)
    lum_dist = lum_dist.to(u.cm)

    fluxes = luminosities / (4 * np.pi * lum_dist.value ** 2)

    return fluxes
