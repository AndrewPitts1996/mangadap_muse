#!/usr/bin/env python3

"""
Dynamically build the rst documentation of the bitmasks.
"""

import os
import time
import textwrap
import numpy

from pkg_resources import resource_filename

#-----------------------------------------------------------------------------

def write_bitmask(bitmask_class, opath):
    ofile = os.path.join(opath, '{0}.rst'.format(bitmask_class.__name__.lower()))
    lines = bitmask_class().to_rst_table(header=False)
    with open(ofile, 'w') as f:
        f.write('\n'.join(lines))

if __name__ == '__main__':
    t = time.perf_counter()

    # Needed to define $MANGADAP_DIR
    import mangadap

    path = os.path.join(os.environ['MANGADAP_DIR'], 'docs', 'tables')
    if not os.path.isdir(path):
        os.makedirs(path)

    # Tables to write:
    #
    from mangadap.drpfits import DRPQuality3DBitMask
    write_bitmask(DRPQuality3DBitMask, path)

    from mangadap.drpfits import DRPFitsBitMask
    write_bitmask(DRPFitsBitMask, path)

    from mangadap.dapfits import DAPQualityBitMask
    write_bitmask(DAPQualityBitMask, path)
    from mangadap.dapfits import DAPMapsBitMask
    write_bitmask(DAPMapsBitMask, path)
    from mangadap.dapfits import DAPCubeBitMask
    write_bitmask(DAPCubeBitMask, path)

    from mangadap.proc.spatiallybinnedspectra import SpatiallyBinnedSpectraBitMask
    write_bitmask(SpatiallyBinnedSpectraBitMask, path)
    from mangadap.proc.templatelibrary import TemplateLibraryBitMask
    write_bitmask(TemplateLibraryBitMask, path)
    from mangadap.proc.stellarcontinuummodel import StellarContinuumModelBitMask
    write_bitmask(StellarContinuumModelBitMask, path)
    from mangadap.proc.emissionlinemoments import EmissionLineMomentsBitMask
    write_bitmask(EmissionLineMomentsBitMask, path)
    from mangadap.proc.emissionlinemodel import EmissionLineModelBitMask
    write_bitmask(EmissionLineModelBitMask, path)
    from mangadap.proc.spectralindices import SpectralIndicesBitMask
    write_bitmask(SpectralIndicesBitMask, path)

    print('Elapsed time: {0} seconds'.format(time.perf_counter() - t))



