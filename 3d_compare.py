#!/usr/bin/python
from netCDF4 import Dataset
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from datetime import datetime, timedelta
from iris.cube import Cube
import iris

import cis
from satellite_utils import comp_parser

def main(args):
    fig, ax = plt.subplots(ncols=1, nrows=5, gridspec_kw={"height_ratios":[1, 1, 0.1, 1, 0.1]}, figsize=(7, 12))

    sdata = Dataset(args.satname, 'r')
    mdata = Dataset(args.modname, 'r')

    print sdata.variables[args.satvar][:].shape

    svar = np.nanmean(sdata.variables[args.satvar][:], axis=(0,3))
    mvar = np.nanmean(mdata.variables[args.modvar][:], axis=(0,3))

    mod_grid = [('height', mdata.variables['height'][:]*0.001), ('latitude', mdata.variables['lat'][:])]

    sbounds = sdata.variables['alt_bound'][:]
    scenters = 0.5*(sbounds[1]+sbounds[0])
    sat_grid = [('height', scenters), ('latitude', sdata.variables['latitude'][:])]

    slat_dim = iris.coords.DimCoord(sat_grid[1][1], standard_name=sat_grid[1][0], units='degree')
    mlat_dim = iris.coords.DimCoord(mod_grid[1][1], standard_name=mod_grid[1][0], units='degree')

    sheight_dim = iris.coords.DimCoord(sat_grid[0][1], standard_name=sat_grid[0][0], units='km')
    mheight_dim = iris.coords.DimCoord(mod_grid[0][1], standard_name=mod_grid[0][0], units='km')

    sat_cube = Cube(svar, units='1', dim_coords_and_dims=[(sheight_dim,0),(slat_dim,1)])
    mod_cube = Cube(mvar, units='1', dim_coords_and_dims=[(mheight_dim,0),(mlat_dim,1)])

    sat_cube_intp = iris.analysis.interpolate.linear(sat_cube, mod_grid)

    x, y = np.meshgrid(mod_grid[1][1], mod_grid[0][1])

    ax[0].set_title('Satellite')
    ax[0].contourf(x, y, sat_cube_intp.data)
    
    ax[1].set_title('Model')
    c1 = ax[1].contourf(x, y, mvar)

    ax[3].set_title('Model - Satellite')
    diff = mvar-sat_cube_intp.data
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
