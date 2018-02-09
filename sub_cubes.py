#!/usr/bin/python
from netCDF4 import Dataset
from iris.cube import Cube
import numpy as np
import iris

class NetCube(Cube):
    def __init__(self, array, grid, units):
        self.grid = grid
        self.dims = {}

        dim_coords_and_dims = []
        for i in range(len(grid)):
            name, val = grid[i]
            dim = iris.coords.DimCoord(val, standard_name=name, units=units[i])
            self.dims[name] = val
            dim_coords_and_dims.append((dim, i))
            
        super(NetCube, self).__init__(array, units=units[-1], dim_coords_and_dims=dim_coords_and_dims)

class ECHAMCube(NetCube):
    def __init__(self, filename, varname):
        data = Dataset(filename, 'r')
        var = data.variables[varname]
        dims = var.dimensions

        if('time' in dims):
            array = np.nanmean(var[:], axis=0)
        else:
            array = var[:]
            
        if('height' in dims):
            grid = [('height', data.variables['height'][:]*0.001), ('latitude', data.variables['lat'][:]), ('longitude', data.variables['lon'][:])]
            units = ['km', 'degree', 'degree', '1']
        else:
            grid = [('latitude', data.variables['lat'][:]), ('longitude', data.variables['lon'][:])]
            units = ['degree', 'degree', '1']

        super(ECHAMCube, self).__init__(array, grid, units)

class GOCCPCube(NetCube):
    def __init__(self, filename, varname):
        data = Dataset(filename, 'r')
        var = data.variables[varname]
        array = np.nanmean(var[:], axis=0)

        bounds = data.variables['alt_bound'][:]
        centers = 0.5*(bounds[1]+bounds[0])
        grid = [('height', centers), ('latitude', data.variables['latitude'][:]), ('longitude', data.variables['longitude'][:])]
        units = ['km', 'degree', 'degree', '1']
        
        super(GOCCPCube, self).__init__(array, grid, units)

        
def main():
    filename = 'model.nc'
    varname = 'aclcac'
    ncube = ECHAMCube(filename, varname)

    filename = 'GOCCP/climato/3D_CloudFraction_avg_2008-2014_2.70.nc'
    varname = 'clcalipso'
    scube = GOCCPCube(filename, varname)

if __name__ == '__main__':
    main()
