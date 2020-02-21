#!/usr/bin/env python3

from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

import os
import time

from argparse import ArgumentParser

import numpy

from mangadap.par.obsinput import ObsInputPar
from mangadap.par.analysisplan import AnalysisPlanSet
from mangadap.survey.manga_dap import manga_dap

#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------

if __name__ == '__main__':
    t = time.perf_counter()

    parser = ArgumentParser()

    parser.add_argument('obs', type=str, help='SDSS parameter file with observational input')
    parser.add_argument('plan', type=str, help='SDSS parameter file with analysis plan')
    parser.add_argument('--dbg', help='Run manga_dap in debug mode', action='store_true',
                        default=False)
    parser.add_argument('--log', type=str, help='File name for runtime log', default=None)
    parser.add_argument('-v', '--verbose', action='count',
                        help='Set verbosity level; can be omitted and set up to -vv', default=0)

    parser.add_argument('--drpver', type=str, help='DRP version', default=None)
    parser.add_argument('-r', '--redux_path', type=str,
                        help='Top-level directory with the DRP products; defaults to '
                             '$MANGA_SPECTRO_REDUX/$MANGADRP_VER', default=None)
    parser.add_argument('-d', '--directory_path', type=str,
                        help='Path directly to directory with DRP file to analyze', default=None)
    parser.add_argument('--dapver', type=str, help='DAP version', default=None)
    parser.add_argument('-a', '--analysis_path', type=str,
                        help='Top-level output directory for the DAP results; defaults to '
                             '$MANGA_SPECTRO_ANALYSIS/$MANGADRP_VER/$MANGADAP_VER', default=None)

    arg = parser.parse_args()
    obspar = ObsInputPar.from_par_file(arg.obs)
    analysisplan = AnalysisPlanSet.from_par_file(arg.plan)

    status = manga_dap(obspar, analysisplan, dbg=arg.dbg, log=arg.log, verbose=arg.verbose,
                       drpver=arg.drpver, redux_path=arg.redux_path,
                       directory_path=arg.directory_path, dapver=arg.dapver,
                       analysis_path=arg.analysis_path)

    print('Elapsed time: {0} seconds'.format(time.perf_counter() - t))



