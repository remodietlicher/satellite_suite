#!/usr/bin/python
from netCDF4 import Dataset
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from datetime import datetime, timedelta
import iris

from mpl_toolkits.basemap import Basemap, cm

cmap = plt.cm.bwr
cmap2 = plt.cm.Reds

from sub_cubes import GOCCPCube, ECHAMCube, cube_factory

import cis
from satellite_utils import comp_parser

# For 2D data, plot on a lat-lon basemap
def latlon_plot(x, y, sat, mod, diff, lsm, ld):
    fig, ax = plt.subplots(ncols=1, nrows=5, gridspec_kw={"height_ratios":[1, 1, 0.1, 1, 0.1]}, figsize=(7, 12))
    ax[0].set_title('Satellite')
    m = Basemap(projection='cyl',llcrnrlat=-90,urcrnrlat=90, llcrnrlon=0,urcrnrlon=360,resolution='c', ax=ax[0])
    m.drawcoastlines()
    m.contourf(x, y, sat, shading='flat',cmap=cmap2,latlon=True, levels=lsm)
    
    ax[1].set_title('Model')
    m = Basemap(projection='cyl',llcrnrlat=-90,urcrnrlat=90, llcrnrlon=0,urcrnrlon=360,resolution='c', ax=ax[1])
    m.drawcoastlines()
    col = m.contourf(x, y, mod, shading='flat',cmap=cmap2,latlon=True, levels=lsm)

    print np.min(mod), np.max(mod)

    plt.colorbar(col, cax=ax[2], orientation='horizontal')

    ax[3].set_title('Model - Satellite')
    m = Basemap(projection='cyl',llcrnrlat=-90,urcrnrlat=90, llcrnrlon=0,urcrnrlon=360,resolution='c', ax=ax[3])
    m.drawcoastlines()
    col = m.contourf(x, y, diff, shading='flat',cmap=cmap,latlon=True, levels=ld)
    plt.colorbar(col, cax=ax[4], orientation='horizontal')

    plt.tight_layout()
    return fig

# For 3D data, plot on a lat-height projection, averaged over lons
def latheight_plot(x, y, sat, mod, diff, lsm, ld):
    fig, ax = plt.subplots(ncols=1, nrows=5, gridspec_kw={"height_ratios":[1, 1, 0.1, 1, 0.1]}, figsize=(7, 12))

    ax[0].set_title('Satellite')
    ax[0].contourf(x, y, sat, levels=lsm)
    
    ax[1].set_title('Model')
    c1 = ax[1].contourf(x, y, mod, levels=lsm)

    ax[3].set_title('Model - Satellite')
    c2 = ax[3].contourf(x, y, diff, levels=ld)

    plt.colorbar(c1, cax=ax[2], orientation='horizontal')
    plt.colorbar(c2, cax=ax[4], orientation='horizontal')

    plt.tight_layout()
    return fig

def main(args):
    mcube = ECHAMCube(args.modname, args.modvar)
    scube = cube_factory(args.satname, args.satvar)

    scube_intp = scube.interpolate(mcube.grid, iris.analysis.Linear())
    svar = scube_intp.data
    mvar = mcube.data
    # right now unfortunately satellite data and model data have oppositely defined signes
    if(np.sign(np.nanmean(svar)) != np.sign(np.nanmean(mvar))):
        svar = -svar
    dvar = mvar - svar

    if('height' in mcube.dims.keys()):
        svar = np.nanmean(svar, axis=2)
        mvar = np.nanmean(mvar, axis=2)
        dvar = np.nanmean(dvar, axis=2)

    smax = np.nanmax(svar)
    mmax = np.nanmax(mvar)
    smin = np.nanmin(svar)
    mmin = np.nanmin(mvar)
    maxvar = max(smax, mmax)
    minvar = min(smin, mmin)
    levels = np.linspace(minvar, maxvar, 10)

    maxdiff = np.nanmax(np.abs(dvar))
    dlevels = np.linspace(-maxdiff, maxdiff, 20)

    lon = mcube.dims['longitude']
    lat = mcube.dims['latitude']

    if('height' in mcube.dims.keys()):
        height = mcube.dims['height']
        x, y = np.meshgrid(lat, height)
        fig = latheight_plot(x, y, svar, mvar, dvar, levels, dlevels)
    else:
        x, y = np.meshgrid(lon, lat)
        fig = latlon_plot(x, y, svar, mvar, dvar, levels, dlevels)

    if(args.spath):
        print 'saving figure to %s...'%(args.spath)
        fig.savefig(args.spath)
    else:
        plt.show()

    return

if __name__ == '__main__':
    ap = comp_parser()
    args = ap.parse_args()
    main(args)
