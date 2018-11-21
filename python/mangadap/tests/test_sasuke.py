
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import pytest
import os

import numpy
from scipy import interpolate
from astropy.io import fits
import astropy.constants

from mangadap.drpfits import DRPFits, DRPFitsBitMask

from mangadap.par.artifactdb import ArtifactDB
from mangadap.par.emissionlinedb import EmissionLineDB

from mangadap.util.pixelmask import SpectralPixelMask

from mangadap.proc.templatelibrary import TemplateLibrary
from mangadap.proc.ppxffit import PPXFFit
from mangadap.proc.stellarcontinuummodel import StellarContinuumModel, StellarContinuumModelBitMask

from mangadap.tests.util import data_file

from mangadap.par.emissionmomentsdb import EmissionMomentsDB
from mangadap.proc.emissionlinemoments import EmissionLineMoments
from mangadap.proc.sasuke import Sasuke
from mangadap.proc.emissionlinemodel import EmissionLineModelBitMask

import warnings
warnings.simplefilter("ignore", UserWarning)
warnings.simplefilter("ignore", RuntimeWarning)

def test_sasuke():
    # Read the data
    specfile = data_file('MaNGA_test_spectra.fits.gz')
    hdu = fits.open(specfile)
    drpbm = DRPFitsBitMask()
    flux = numpy.ma.MaskedArray(hdu['FLUX'].data,
                                mask=drpbm.flagged(hdu['MASK'].data, DRPFits.do_not_fit_flags()))
    ferr = numpy.ma.power(hdu['IVAR'].data, -0.5)
    flux[ferr.mask] = numpy.ma.masked
    ferr[flux.mask] = numpy.ma.masked
    nspec = flux.shape[0]

    # Instantiate the template libary
    velscale_ratio = 4
    tpl = TemplateLibrary('MILESHC', match_to_drp_resolution=False, velscale_ratio=velscale_ratio,
                          spectral_step=1e-4, log=True, hardcopy=False)
    tpl_sres = numpy.mean(tpl['SPECRES'].data, axis=0)

    # Get the pixel mask
    pixelmask = SpectralPixelMask(artdb=ArtifactDB('BADSKY'), emldb=EmissionLineDB('ELPFULL'))

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
    pixelmask = SpectralPixelMask(artdb=ArtifactDB('BADSKY'))

    # Read the emission line fitting database
    emldb = EmissionLineDB('ELPMILES')
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
    assert numpy.array_equal(numpy.sum(el_fit['TPLWGT'] > 0, axis=1),
                             [25, 24, 32, 32, 28,  0, 17, 22]), \
                'Different number of templates with non-zero weights'

    # No additive coefficients
    assert numpy.all(el_fit['ADDCOEF'] == 0), \
                'No multiplicative coefficients should exist'

    # No multiplicative coefficients
    assert numpy.all(el_fit['MULTCOEF'] == 0), \
                'No multiplicative coefficients should exist'

    # Fit statistics
    assert numpy.allclose(el_fit['RCHI2'],
                    numpy.array([2.30526714, 1.19355894, 1.54887132, 1.84447282, 3.14657599,
                                 0.        , 1.03495789, 0.86928516])), 'Chi-square different'

    assert numpy.allclose(el_fit['RMS'],
                    numpy.array([0.03624053, 0.0191412 , 0.03661278, 0.02454041, 0.05073471,
                                 0.        , 0.01283324, 0.01245004])), 'RMS different'

    assert numpy.allclose(el_fit['FRMS'],
                    numpy.array([0.02098079, 0.02650329, 0.02718797, 0.03478277, 0.01857   ,
                                 0.        , 1.12984714, 0.10961989])), 'Fractional RMS different'

    assert numpy.allclose(el_fit['ABSRESID'][:,2],
                    numpy.array([0.07080605, 0.0374927 , 0.07063608, 0.0476781 , 0.10087567,
                                 0.        , 0.02704224, 0.02432112])), \
                    'Median absolute residual different'

    # All lines should have the same velocity
    assert numpy.all(numpy.all(el_par['KIN'][:,:,0] == el_par['KIN'][:,None,0,0], axis=1)), \
                'All velocities should be the same'

    # Test velocity values
    assert numpy.allclose(el_par['KIN'][:,0,0],
                numpy.array([14694.03503013, 14882.17193222, 14767.1212133 ,  8159.47649202,
                              9258.7217533 ,     0.        ,  5131.13183361,  5432.3821883 ])), \
                'Velocities are different'

    # H-alpha dispsersions
    # TODO: Need some better examples!
    assert numpy.allclose(el_par['KIN'][:,18,1],
                numpy.array([1000.47576421, 1000.47576421,  224.68070585,  114.02429333,
                             170.88750393,    0.        ,   81.28290423,   50.12936608])), \
                'H-alpha dispersions are different'
