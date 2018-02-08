#!/usr/bin/python
from netCDF4 import Dataset
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import argparse
from datetime import datetime, timedelta

import cis
from satellite_utils import comp_parser

from mpl_toolkits.basemap import Basemap, cm

cmap = plt.cm.rainbow

def main(args):
    fig, ax = plt.subplots(ncols=1, nrows=2, gridspec_kw={"height_ratios":[1, 0.1]}, figsize=(6, 5))

    sdata = cis.read_data(args.satname, args.satvar).subset(time=[datetime(2000,1,1), datetime(2020,1,1)])
    mdata = cis.read_data(args.modname, args.modvar).subset(time=[datetime(2000,1,1), datetime(2020,1,1)])

    mdata_col, = mdata.collocated_onto(sdata)

    # note that fluxes are defined in opposite directions
    diff = mdata_col.data - sdata.data

    sdata.plot()
    mdata.plot()

    netdata = Dataset(args.satname, 'r')
    lat = netdata.variables['lat'][:]
    lon = netdata.variables['lon'][:]

    ax[0].set_title('Sum')
    m = Basemap(projection='cyl',llcrnrlat=-90,urcrnrlat=90, llcrnrlon=0,urcrnrlon=360,resolution='c', ax=ax[0])
    m.drawcoastlines()
    c = m.pcolormesh(lon, lat, diff, shading='flat',cmap=cmap,latlon=True)

    plt.colorbar(c, cax=ax[-1], orientation='horizontal')
    plt.show()

    return

    

if __name__ == '__main__':
    ap = comp_parser()
    args = ap.parse_args()
    main(args)
