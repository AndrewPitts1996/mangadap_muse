# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
"""Plot DAP QA."""

from __future__ import (division, print_function, absolute_import,
                        unicode_literals)

import os
from os.path import join
import sys
import copy

from imp import reload

import matplotlib as mpl
mpl.use('Agg')

from mangadap import dap_access
from mangadap.plot import plotdap
from mangadap.plot import cfg_io
from mangadap.plot import util

import __main__ as main

if hasattr(main, '__file__'):
    # run as script
    try:
        file_list = sys.argv[1]
        plottypes_list = sys.argv[2]
    except IndexError:
        raise IndexError('Usage: python plotqa.py file_list plottypes_list')
else:
    # interactive session
    # Utah MPL4 file
    file_list = join(os.getenv('MANGA_SPECTRO_ANALYSIS'),
                     os.getenv('MANGADRP_VER'), os.getenv('MANGADAP_VER'),
                     'full', '8083', '1901', 'CUBE_files_to_plot.txt')
    # Portsmouth MPL4 file
    # file_list = join(os.getenv('MANGA_SANDBOX_MPL4'),
    #                  os.getenv('MANGADRP_VER'), os.getenv('MANGADAP_VER'),
    #                  os.getenv('MANGADAP_TPL'), '7443', '1901',
    #                  'CUBE_files_to_plot.txt')
    plottypes_list = 'dapqa_plottypes.ini'

# COMMENT OUT
# plottypes_list = join(os.getenv('HOME'), 'mangadap', 'trunk', 'python',
#                       'mangadap', 'plot', 'config', 'dapqa_plottypes.ini')

file_kws_all = util.read_file_list(file_list)
cfg_dir = util.make_config_path(plottypes_list)
paths_cfg = join(cfg_dir, 'sdss_paths.ini')

# COMMENT OUT
# file_kws = file_kws_all[0]
# path_data = util.make_data_path(paths_cfg, file_kws)
# gal = dap_access.DAPAccess(path_data, file_kws, paths_cfg, verbose=True)
# gal.get_all_ext()
# mg_kws = util.make_mg_kws(gal, file_kws)
# ptypes_list = util.check_h3_h4(gal.bintype, gal.binsn, plottypes_list)
# plottypes = cfg_io.read_plottypes_config(join(cfg_dir, ptypes_list))


for file_kws in file_kws_all:
    path_data = util.make_data_path(paths_cfg, file_kws)
    gal = dap_access.DAPAccess(path_data, file_kws, paths_cfg, verbose=True)
    gal.get_all_ext()
    mg_kws = util.make_mg_kws(gal, file_kws)

    ptypes_list = util.check_h3_h4(gal.bintype, gal.binsn, plottypes_list)
    plottypes = cfg_io.read_plottypes_config(join(cfg_dir, ptypes_list))
    for plottype in plottypes:
        cfg = cfg_io.read_config(join(cfg_dir, plottype + '.ini'))
        plot_kws = cfg_io.make_kws(cfg)
        plot_kws['main'] = hasattr(main, '__file__')
        plotdap.make_plots(plottype=plottype, dapdata=gal, mg_kws=mg_kws,
                           plot_kws=plot_kws)


# plottype = 'flux_ew_maps'
# cfg = cfg_io.read_config(join(cfg_dir, plottype + '.ini'))
# plot_kws = cfg_io.make_kws(cfg)
# plot_kws['main'] = hasattr(main, '__file__')
# plot_kws['columns'] = ['Ha6564']
# plot_kws['make_multi'] = False
# plot_kws['savefig_multi'] = False
# plot_kws['savefig_single'] = True
# 
# from mangadap.plot import plotdap
# reload(plotdap)
# plotdap.make_plots(plottype=plottype, dapdata=gal, mg_kws=mg_kws, plot_kws=plot_kws)



"""
1. run for two plates
2. email marvin list
"""

# MPL-4 file
# python3 plotqa.py $MANGA_SPECTRO_ANALYSIS/test/andrews/$MANGADRP_VER/$MANGADAP_VER/full/8082/1901/CUBE_files_to_plot.txt dapqa_plottypes.ini

# MPL-4 Sandbox
# python3 plotqa.py $MANGA_SANDBOX_MPL4/$MANGADRP_VER/$MANGADAP_VER/mpl4_m11stelibzsol/7443/1901/CUBE_files_to_plot.txt dapqa_plottypes.ini