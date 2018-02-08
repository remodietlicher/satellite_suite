#!/usr/bin/python
from netCDF4 import Dataset
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import argparse
from datetime import datetime, timedelta

from satellite_utils import get_box_area, get_yearly_means, get_datetime, get_timedelta


def arg_parser():
    usage = """
    """

    description = """
    """

    ap = argparse.ArgumentParser(usage=usage, description=description)
    
    ap.add_argument('filename', metavar='filename', help='the echam histogram file')
    ap.add_argument('varname', metavar='varname', help='name of the variable')

    return ap

def main(args):
    data = Dataset(args.filename, 'r')
    fig, ax = plt.subplots(ncols=1, nrows=2, gridspec_kw={"height_ratios":[1, 0.1]}, figsize=(7, 10))

    lat = data.variables['latitude'][:]
    lon = data.variables['longitude'][:]

    date = get_datetime(data.variables['time'])
    var = data.variables[args.varname][:]

    print var.shape
    print date

    return




if __name__ == '__main__':
    ap = arg_parser()
    args = ap.parse_args()
    main(args)
