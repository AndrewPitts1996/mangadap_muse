
import pytest
import os

from IPython import embed

import numpy
from scipy import interpolate
from astropy.io import fits
import astropy.constants

from mangadap.datacube import MaNGADataCube

from mangadap.par.artifactdb import ArtifactDB
from mangadap.par.emissionlinedb import EmissionLineDB

from mangadap.util.drpfits import DRPFitsBitMask
from mangadap.util.pixelmask import SpectralPixelMask

from mangadap.proc.templatelibrary import TemplateLibrary
from mangadap.proc.ppxffit import PPXFFit
from mangadap.proc.stellarcontinuummodel import StellarContinuumModel, StellarContinuumModelBitMask

from mangadap.tests.util import data_test_file

from mangadap.proc.sasuke import Sasuke
from mangadap.proc.emissionlinemodel import EmissionLineModelBitMask

import warnings
warnings.simplefilter("ignore", UserWarning)
warnings.simplefilter("ignore", RuntimeWarning)

def test_sasuke():
    # Read the data
    specfile = data_test_file('MaNGA_test_spectra.fits.gz')
    hdu = fits.open(specfile)
    drpbm = DRPFitsBitMask()
    flux = numpy.ma.MaskedArray(hdu['FLUX'].data, mask=drpbm.flagged(hdu['MASK'].data,
                                                                MaNGADataCube.do_not_fit_flags()))
    ferr = numpy.ma.power(hdu['IVAR'].data, -0.5)
    flux[ferr.mask] = numpy.ma.masked
    ferr[flux.mask] = numpy.ma.masked
    nspec = flux.shape[0]

    # Instantiate the template libary
    velscale_ratio = 4
    tpl = TemplateLibrary('MILESHC', match_resolution=False, velscale_ratio=velscale_ratio,
                          spectral_step=1e-4, log=True, hardcopy=False)
    tpl_sres = numpy.mean(tpl['SPECRES'].data, axis=0)

    # Get the pixel mask
    pixelmask = SpectralPixelMask(artdb=ArtifactDB.from_key('BADSKY'),
                                  emldb=EmissionLineDB.from_key('ELPFULL'))

    # Instantiate the fitting class
    ppxf = PPXFFit(StellarContinuumModelBitMask())

    # Perform the fit
    sc_wave, sc_flux, sc_mask, sc_par \
        = ppxf.fit(tpl['WAVE'].data.copy(), tpl['FLUX'].data.copy(), hdu['WAVE'].data, flux, ferr,
                   hdu['Z'].data, numpy.full(nspec, 100.), iteration_mode='no_global_wrej',
                   reject_boxcar=100, ensemble=False, velscale_ratio=velscale_ratio,
                   mask=pixelmask, matched_resolution=False, tpl_sres=tpl_sres,
                   obj_sres=hdu['SRES'].data, degree=8, moments=2)

    # Mask the 5577 sky line
    pixelmask = SpectralPixelMask(artdb=ArtifactDB.from_key('BADSKY'))

    # Read the emission line fitting database
    emldb = EmissionLineDB.from_key('ELPMILES')
    assert emldb['name'][18] == 'Ha', 'Emission-line database names or ordering changed'

    # Instantiate the fitting class
    emlfit = Sasuke(EmissionLineModelBitMask())

    # Perform the fit
    el_wave, model, el_flux, el_mask, el_fit, el_par \
            = emlfit.fit(emldb, hdu['WAVE'].data, flux, obj_ferr=ferr, obj_mask=pixelmask,
                         obj_sres=hdu['SRES'].data, guess_redshift=hdu['Z'].data,
                         guess_dispersion=numpy.full(nspec, 100.), reject_boxcar=101,
                         stpl_wave=tpl['WAVE'].data, stpl_flux=tpl['FLUX'].data,
                         stpl_sres=tpl_sres, stellar_kinematics=sc_par['KIN'],
                         etpl_sinst_mode='offset', etpl_sinst_min=10.,
                         velscale_ratio=velscale_ratio, matched_resolution=False) #, # mdegree=8,
                         #plot=True)

    # Test the results

    # Rejected pixels
    assert numpy.sum(emlfit.bitmask.flagged(el_mask, flag='PPXF_REJECT')) == 277, \
                'Different number of rejected pixels'

    # Unable to fit
    assert numpy.array_equal(emlfit.bitmask.flagged_bits(el_fit['MASK'][5]), ['NO_FIT']), \
                'Expected NO_FIT in 6th spectrum'

    # Number of used templates
    assert numpy.array_equal(numpy.sum(numpy.absolute(el_fit['TPLWGT']) > 1e-10, axis=1),
                             [25, 24, 32, 32, 28,  0, 17, 22]), \
                'Different number of templates with non-zero weights'

    # No additive coefficients
    assert numpy.all(el_fit['ADDCOEF'] == 0), \
                'No additive coefficients should exist'

    # No multiplicative coefficients
    assert numpy.all(el_fit['MULTCOEF'] == 0), \
                'No multiplicative coefficients should exist'

    # Fit statistics
    assert numpy.all(numpy.absolute(el_fit['RCHI2'] - 
                                    numpy.array([2.34, 1.22, 1.58, 1.88, 3.20, 0., 1.05, 0.88]))
                     < 0.02), 'Reduced chi-square are too different'

    assert numpy.all(numpy.absolute(el_fit['RMS'] -
                                    numpy.array([0.0362, 0.0191, 0.0366, 0.0246, 0.0507, 0.,
                                                 0.0128, 0.0124])) < 1e-4), 'RMS too different'

    assert numpy.all(numpy.absolute(el_fit['FRMS'] -
                                    numpy.array([0.0210, 0.0265, 0.0272, 0.0348, 0.0186, 0.,
                                                 1.1298, 0.1096])) < 1e-4), \
            'Fractional RMS too different'

    assert numpy.all(numpy.absolute(el_fit['RMSGRW'][:,2] -
                                    numpy.array([0.0708, 0.0375, 0.0707, 0.0477, 0.1009, 0.,
                                                 0.0271, 0.0244])) < 1e-4), \
            'Median absolute residual too different'

    # All lines should have the same velocity
    assert numpy.all(numpy.all(el_par['KIN'][:,:,0] == el_par['KIN'][:,None,0,0], axis=1)), \
                'All velocities should be the same'

    # Test velocity values
    # TODO: Need some better examples!
    assert numpy.all(numpy.absolute(el_par['KIN'][:,0,0] -
                                    numpy.array([14694.0, 14882.2, 14767.1, 8159.5, 9258.7, 0.,
                                                 5131.1, 5432.4])) < 1e-1), \
                'Velocities are too different'

    # H-alpha dispersions
    assert numpy.all(numpy.absolute(el_par['KIN'][:,18,1] - 
                                    numpy.array([1000.5, 1000.5, 224.7, 114.0, 170.9, 0., 81.3,
                                                 50.1])) < 1e-1), \
            'H-alpha dispersions are too different'

if __name__ == '__main__':
    test_sasuke()
