#!/usr/bin/env python3

#-----------------------------------------------------------------------
import sys
import os.path
from mangadap.drpcomplete import drpcomplete
#-----------------------------------------------------------------------

def write_dap_par():

    if len(sys.argv) != 6:
        print('Usage: write_par.py <drpcomplete file> <plate> <ifudesign> <(CUBE or RSS)> <output file>')
        raise Exception('Incorrect number of arguments!')

    root_dir = os.path.dirname(sys.argv[1])
    if len(root_dir) == 0:
        root_dir = '.'
    drpc_file = sys.argv[1]
    drpver = drpc_file[drpc_file.find('_v')+1 : drpc_file.find('.fits')]

    drpc = drpcomplete(drpver=drpver, analysis_path=root_dir, readonly=True)

    drpc.write_par(ofile=sys.argv[5], mode=sys.argv[4], plate=int(sys.argv[2]),
                   ifudesign=int(sys.argv[3]))


if __name__ == '__main__':
    write_dap_par()

