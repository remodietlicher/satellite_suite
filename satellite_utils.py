#!/usr/bin/python
import numpy as np
from datetime import datetime, timedelta
import argparse

r_earth = 6371000

# provide meshed lon-lat grid
def get_box_area(lat, lon):
    # ceres data is on a 1x1 degree grid
    res_lat = 1
    res_lon = 1

    # prepare edges
    lat1 = lat-res_lat*0.5
    lat2 = lat+res_lat*0.5
    lon1 = lon-res_lon*0.5
    lon2 = lon+res_lon*0.5

    # compute area
    area = (np.pi/180)*r_earth**2*np.abs(np.sin(lat1*np.pi/180.)-np.sin(lat2*np.pi/180.))*np.abs(lon1-lon2)

    return area

# convert monthly means to yearly means
# starting with the first month in the array
def get_yearly_means(var, date):
    nt, nlon, nlat = var.shape

    nyears = nt/12

    years = np.array([d.year for d in date])
    months = np.array([d.month for d in date])
    days = np.array([d.day for d in date])

    yearmin = np.min(years)
    yearmax = np.max(years)

    nyears = yearmax-yearmin+1

    if(nyears == len(years)):
        print('got yearly means already')
        dates = [datetime(y, 1, 1, 0, 0, 0) for y in years]
        means = var
        return means, dates
    if(months[0] > 1):
        yearmin += 1
    if(months[-1] < 12):
        yearmax -= 1

    nyears = yearmax-yearmin+1

    dates = [None]*nyears
    means = np.zeros((nyears, nlon, nlat))
    for i,y in enumerate(np.arange(yearmin, yearmax+1)):
        idx = [j for j in range(len(years)) if years[j] == y]
        means[i,:,:] = np.average(var[idx,:,:], axis=0)
        dates[i] = datetime(y, 1, 1, 0, 0, 0)

    return means, dates

# convert the netCDF time units string to python datetime object
def get_datetime(time):
    dum, dum, ymd, hms = time.units.split(' ')
    uyear, umonth, uday = np.array(ymd.split('-')).astype(int)
    uhour, umin, usec = np.array(hms.split(':')).astype(int)

    start = datetime(uyear, umonth, uday, uhour, umin, usec)
    date = [start + timedelta(days=int(t)) for t in time[:]]
    
    return date

def get_timedelta(date, reftime):
    return np.array([(d-reftime).days for d in date])

# parses the arguments for a satellite to model comparison
def comp_parser():
    usage = """
    usage: %(prog)s satname satvar modname modvar
    e.g. : %(prog)s CERES-TOA.nc toa_lw_all_mon multi_annual_means.nc LW
    """

    description = """
    Collocates the model and satellite grids and displays the difference
    between the two fields.
    """

    ap = argparse.ArgumentParser(usage=usage, description=description)
    
    ap.add_argument('satname', metavar='satname', help='the file containing satellite data')
    ap.add_argument('satvar', metavar='satvar', help='name of the variable: satellite')
    ap.add_argument('modname', metavar='modname', help='the file containing model data')
    ap.add_argument('modvar', metavar='modvar', help='name of the variable: model')
    ap.add_argument('--save', dest='spath', metavar='save path', help='Path to save the file to')

    return ap

# parses the arguments for an overview plot of 2D-Data.
def mean_parser():
    usage = """
    usage: %(prog)s filename varname
    e.g. : %(prog)s CERES-TOA.nc toa_lw_all_mon
    """

    description = """
    Computes yearly means as well as the total mean of the dataset provided. From this
    two plots are produced. Top: Yearly global means, Bottom: Dataset-mean lat-lon field
    """

    ap = argparse.ArgumentParser(usage=usage, description=description)
    
    ap.add_argument('filename', metavar='filename', help='the echam histogram file')
    ap.add_argument('varname', metavar='varname', help='name of the variable')
    ap.add_argument('--save', dest='spath', metavar='save path', help='Path to save the file to')

    return ap
