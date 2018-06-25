#!/usr/bin/python
from netCDF4 import Dataset
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from pylab import cm
from satellite_utils import get_box_area

import argparse
matplotlib.rcParams.update({'font.size': 20})


tmlt = 273.15
cmap = cm.get_cmap('jet', 10)
lw = 4

# parses the arguments
def arg_parser():
    usage = """
    """

    description = """
    """

    ap = argparse.ArgumentParser(usage=usage, description=description)
    
    ap.add_argument('mode', metavar='mode', help='select generation or show mode')
    ap.add_argument('filenames', metavar='filenames', nargs='*', help='the echam histogram file')
    ap.add_argument('--save', dest='spath', metavar='save path', help='Path to save the file to')

    return ap

def generate_hist_from_satellite_data(data):
    out = {}

    temp = data.variables['temp_bound'][:]
    phase = data.variables['cltemp_phase'][:]
    lon = data.variables['longitude'][:]
    lat = data.variables['latitude'][:]
    ntim, ntmp, nlat, nlon = phase.shape

    x, y = np.meshgrid(lat, lon, indexing='ij')
    area = get_box_area(x, y)
    area = np.repeat(area[np.newaxis,:,:], ntmp, axis=0)
    area = np.repeat(area[np.newaxis,:,:,:], ntim, axis=0)

    center_temp = 0.5*(temp[0,:]+temp[1,:])

    center_temp = np.repeat(center_temp[np.newaxis,:], ntim, axis=0)
    center_temp = np.repeat(center_temp[:,:,np.newaxis], nlat, axis=2)
    center_temp = np.repeat(center_temp[:,:,:,np.newaxis], nlon, axis=3)

    tedges = np.arange(-45, 4, 3)
    pedges = np.linspace(0, 1, 10+1)
    ctlf_cc = np.zeros((len(tedges)-1, 10))
    ct_lf = np.zeros((len(tedges)-1))
    ct_cc = np.zeros((len(tedges)-1))

    ones = np.ones_like(phase)
    ones[np.isnan(phase)] = 0
    # calculate the histograms per bin (already binned in data)
    for i in range(16):
        # the temperature of -45 has an offset of 16
        midx = i+16
        ctlf_cc[i,:], xe = np.histogram(phase[:,midx,:,:].flatten(), bins=pedges, weights=area[:,midx,:,:].flatten())
        ct_lf[i] = np.nansum(phase[:,midx,:,:]*area[:,midx,:,:])
        ct_cc[i] = np.nansum(area[:,midx,:,:]*ones[:,midx,:,:])

    out['ctlf_cc'] = ctlf_cc
    out['ct_lf'] = ct_lf
    out['ct_cc'] = ct_cc

    return out

def generate_hist(args):
    tmlt = 273.15
    data = [Dataset(f, 'r') for f in args.filenames]
    
    for i,d in enumerate(data):
        name = args.filenames[i]
        print 'processing file', name
        hist = generate_hist_from_satellite_data(d)
        spath = name[:-3] + '_histogram.npy'
        print 'saving histogram as %s'%(spath)
        np.save(spath, hist)

    return

def show_hist(args):
    hists = [np.load(f).item() for f in args.filenames]

    nt, npr = hists[0]['ctlf_cc'].shape

    ctlf_cc = np.zeros((nt, npr))
    ct_lf = np.zeros((nt))
    ct_cc = np.zeros((nt))
    print 'adding up %i hists'%(len(hists))
    for h in hists:
        ctlf_cc = ctlf_cc + h['ctlf_cc']
        ct_lf = ct_lf + h['ct_lf']
        ct_cc = ct_cc + h['ct_cc']

    ctlf_cc = ctlf_cc/np.sum(ctlf_cc)
    ct_lf = ct_lf/ct_cc
    fig, ax = plt.subplots(nrows=1, ncols=1)

    extent = [233.15-tmlt, 278.15-tmlt, 0, 1]
    origin='lower'
    c = ax.imshow(np.transpose(ctlf_cc)*100, interpolation='none', origin=origin, extent=extent, aspect='auto', vmin=0.01, vmax=2, cmap=cmap)
    tedges = np.arange(-45, 4, 3)
    tcenters = 0.5*(tedges[:-1] + tedges[1:])
    ax.plot(tcenters, ct_lf, 'red', lw=lw)
    ax.set_xlim(xmin=-45, xmax=3)
    ax.set_xlabel('Temperature / K')
    ax.set_ylabel('Ice fraction')


    plt.colorbar(c, ax=ax, format='$%.1f$', extend='both')
    c.cmap.set_under('white')
    c.cmap.set_over('pink')

    plt.tight_layout()

    if(args.spath):
        print 'saving figure to %s...'%(args.spath)
        fig.savefig(args.spath)
    else:
        plt.show()

if __name__ == '__main__':
    ap = arg_parser()
    args = ap.parse_args()

    print 'got file list:', args.filenames
    print 'process in mode:', args.mode

    if args.mode == 'generate':
        generate_hist(args)
    elif args.mode == 'show':
        show_hist(args)
