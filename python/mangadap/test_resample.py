#!/usr/bin/env python3

import os
import time
import numpy

from matplotlib import pyplot

from astropy.io import fits

from mangadap.util.instrument import Resample, _pixel_borders
from mangadap.proc.bandpassfilter import passband_integral

import spectres

#-----------------------------------------------------------------------------

def resample_test():
    root = os.path.join(os.environ['MANGA_SPECTRO_REDUX'], os.environ['MANGADRP_VER'])
   
    pltifu = '7815-1901'
    hdu = fits.open(os.path.join(root, pltifu.split('-')[0], 'stack',
                                 'manga-{0}-LOGCUBE.fits.gz'.format(pltifu)))

    drpall_file = os.path.join(root, 'drpall-{0}.fits'.format(os.environ['MANGADRP_VER']))
    drpall = fits.open(drpall_file)[1].data

    indx = drpall['PLATEIFU'] == pltifu
    z = drpall['NSA_Z'][indx][0]
    print(z)

    old_wave = hdu['WAVE'].data
    old_flux = hdu['FLUX'].data[:,10,10]
    indx = (old_wave > old_wave[0]/(1+z)) & (old_wave < old_wave[-2]/(1+z))

    pyplot.plot(old_wave/(1+z), old_flux)

    t = time.clock()
    new_flux_spectres = spectres.spectres(old_wave[indx], old_wave/(1+z), old_flux)
    print('SpectRes Time: ', time.clock()-t)

    pyplot.plot(old_wave[indx], new_flux_spectres)

    t = time.clock()
    borders = _pixel_borders(numpy.array([old_wave[0],old_wave[-1]]), old_wave.size, log=True)[0]
    _p = numpy.repeat(borders, 2)[1:-1].reshape(-1,2)
    new_flux_brute = passband_integral(old_wave/(1+z), old_flux, passband=_p,
                                       log=True)/(_p[:,1]-_p[:,0])
    print('Brute Force Time: ', time.clock()-t)

    pyplot.plot(old_wave, new_flux_brute)

    t = time.clock()
    r = Resample(old_flux, x=old_wave/(1+z), newRange=[old_wave[0], old_wave[-1]], inLog=True,
                 newLog=True)
    print('Resample Time: ', time.clock()-t)

    pyplot.plot(r.outx, r.outy)

    print('Mean diff:')
    print('    spectres - brute    = {0:.5e}'.format(
            numpy.mean(numpy.absolute(new_flux_spectres-new_flux_brute[indx]))))
    print('    spectres - resample = {0:.5e}'.format(
            numpy.mean(numpy.absolute(new_flux_spectres-r.outy[indx]))))
    print('    brute - resample    = {0:.5e}'.format(
            numpy.mean(numpy.absolute(new_flux_brute-r.outy))))

    pyplot.show()



#-----------------------------------------------------------------------------

if __name__ == '__main__':
    resample_test()



