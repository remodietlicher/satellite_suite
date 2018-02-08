#!/usr/bin/python
from netCDF4 import Dataset
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import argparse
from datetime import datetime, timedelta

import cis

from mpl_toolkits.basemap import Basemap, cm

from satellite_utils import get_box_area, get_yearly_means, get_datetime, get_timedelta, mean_parser

cmap = plt.cm.rainbow
reftime = datetime(2000, 1, 1, 0, 0, 0)

def main(args):
    fig, ax = plt.subplots(ncols=1, nrows=3, gridspec_kw={"height_ratios":[1, 1, 0.1]}, figsize=(7, 10))

    data = Dataset(args.filename, 'r')

    lat = data.variables['lat'][:]
    lon = data.variables['lon'][:]

    date = get_datetime(data.variables['time'])

    var = data.variables[args.varname][:]
    
    lonm, latm = np.meshgrid(lon, lat)

    var_yearly, dates_yearly = get_yearly_means(var, date)

    area = get_box_area(lonm, latm)

    var_yearly_global = np.sum(var_yearly*area, axis=(1,2))/np.sum(area)

    var = np.average(var, axis=0)

    ax[0].plot(dates_yearly, var_yearly_global)

    ax[1].set_title('Sum')
    m = Basemap(projection='cyl',llcrnrlat=-90,urcrnrlat=90, llcrnrlon=0,urcrnrlon=360,resolution='c', ax=ax[1])
    m.drawcoastlines()
    c = m.pcolormesh(lon, lat, var, shading='flat',cmap=cmap,latlon=True)

    plt.colorbar(c, cax=ax[-1], orientation='horizontal')
    plt.show()

    data.close()
    return
    

if __name__ == '__main__':
    ap = mean_parser()
    args = ap.parse_args()
    main(args)
