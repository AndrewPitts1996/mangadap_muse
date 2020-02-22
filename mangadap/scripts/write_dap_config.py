import os
import time
import argparse

from astropy.io import fits

from mangadap.datacube import MaNGADataCube
from mangadap.survey.drpcomplete import DRPComplete

def parse_args(options=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('plate', type=int, help='Plate number')
    parser.add_argument('ifudesign', type=int, help='IFU design number')
    parser.add_argument('ofile', type=str, help='Output file name')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-c', '--drpcomplete', type=str, help='DRP complete fits file',
                        default=None)
    group.add_argument('-a', '--drpall', type=str, help='DRPall fits file', default=None)

    parser.add_argument('--sres_ext', type=str, default=None,
                        help='Root of spectral resolution extension to use.  Default set by '
                             'MaNGADataCube class.')
    parser.add_argument('--sres_fill', type=str, default=None,
                        help='If present, use interpolation to fill any masked pixels in the '
                             'spectral resolution vectors. Default set by MaNGADataCube class.')
    parser.add_argument('--covar_ext', type=str, default=None,
                        help='Use this extension to define the spatial correlation matrix.  '
                             'Default set by MaNGADataCube class.')
    parser.add_argument('--drpver', type=str, default=None,
                        help='DRP version.  Default set by MaNGADataCube class.')
    parser.add_argument('--redux_path', type=str, default=None,
                        help='Path to the top-level DRP reduction directory.  Default set by '
                             'MaNGADataCube class.')
    parser.add_argument('--directory_path', type=str, default=None,
                        help='Exact path to the directory with the MaNGA DRP datacube.  The name '
                             'of the file itself must match the nominal MaNGA DRP naming '
                             'convention.  Default set by MaNGADataCube class.')
    parser.add_argument('-o', '--overwrite', type=bool, default=False, action='store_true',
                        help='Overwrite any existing files.')

    return parser.parse_args() if options is None else parser.parse_args(options)

def main(args):
    t = time.perf_counter()

    # Parse the spectral resolution extension
    sres_pre = None if args.sres_ext is None else 'PRE' in args.sres_ext
    if sres_pre:
        # Won't reach here if args.sres_ext is None
        args.sres_ext = args.sres_ext[3:]

    if args.drpcomplete is not None:
        # Use the DRPcomplete file
        root_dir = os.path.dirname(args.drpcomplete)
        if len(root_dir) == 0:
            root_dir = '.'
        drpver = args.drpcomplete[args.drpcomplete.find('_v')+1 : args.drpcomplete.find('.fits')]
        drpc = DRPComplete(drpver=drpver, directory_path=root_dir, readonly=True)
        drpc.write_config(args.ofile, plate=args.plate, ifudesign=args.ifudesign,
                          sres_ext=args.sres_ext, sres_pre=args.sres_pre, sres_fill=args.sres_fill,
                          covar_ext=args.covar_ext, overwrite=args.overwrite)
        return

    # Use the DRPall file
    with fits.open(args.drpall) as hdu:
        indx = hdu['MANGA'].data['PLATEIFU'] == '{0}-{1}'.format(plate, ifudesign)
        if numpy.sum(indx) != 1:
            raise ValueError('{0}-{1} either does not exist or has more than one match!'.format(
                                plate, ifudesign))

        MaNGADataCube.write_config(args.ofile, args.plate, args.ifudesign,
                                   z=hdu[1].data['z'][indx],
                                   ell=1-hdu[1].data['nsa_elpetro_ba'][indx],
                                   pa=hdu[1].data['nsa_elpetro_phi'][indx],
                                   reff=hdu[1].data['nsa_elpetro_th50_r'][indx],
                                   sres_ext=args.sres_ext, sres_pre=sres_pre,
                                   sres_fill=args.sres_fill, covar_ext=args.covar_ext,
                                   drpver=args.drpver, redux_path=args.redux_path,
                                   directory_path=args.directory_path, overwrite=args.overwrite)

    print('Elapsed time: {0} seconds'.format(time.perf_counter() - t))

