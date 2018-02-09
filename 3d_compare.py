#!/usr/bin/python
from netCDF4 import Dataset
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from datetime import datetime, timedelta
import iris

from sub_cubes import GOCCPCube, ECHAMCube

import cis
from satellite_utils import comp_parser

def main(args):
    fig, ax = plt.subplots(ncols=1, nrows=5, gridspec_kw={"height_ratios":[1, 1, 0.1, 1, 0.1]}, figsize=(7, 12))

    mcube = ECHAMCube(args.modname, args.modvar)
    scube = GOCCPCube(args.satname, args.satvar)

    scube_intp = scube.regrid_onto(mcube)
    svar_intp = scube_intp.data
    mvar = mcube.data
    diffvar = mvar - svar_intp

    satellite = np.nanmean(svar_intp, axis=2)
    model = np.nanmean(mvar, axis=2)
    diff = np.nanmean(diffvar, axis=2)

    x, y = np.meshgrid(mcube.dims['latitude'], mcube.dims['height'])

    smax = np.max(satellite)
    mmax = np.max(model)
    smin = np.min(satellite)
    mmin = np.min(model)
    maxvar = max(smax, mmax)
    minvar = min(smin, mmin)

    levels = np.linspace(minvar, maxvar, 10)

    ax[0].set_title('Satellite')
    ax[0].contourf(x, y, satellite, levels=levels)
    
    ax[1].set_title('Model')
    c1 = ax[1].contourf(x, y, model, levels=levels)

    ax[3].set_title('Model - Satellite')
    maxdiff = np.max(np.abs(diff))
    levels = np.linspace(-maxdiff, maxdiff, 13)
    c2 = ax[3].contourf(x, y, diff, levels=levels)

    plt.colorbar(c1, cax=ax[2], orientation='horizontal')
    plt.colorbar(c2, cax=ax[4], orientation='horizontal')

    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    ap = comp_parser()
    args = ap.parse_args()
    main(args)
