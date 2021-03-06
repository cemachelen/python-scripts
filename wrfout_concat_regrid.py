#!/usr/bin/env python3
import xarray as xr
import salem
import os
import glob
import xesmf as xe
import numpy as np

year   = '2015' 
month  = '08'
res    = 0.25
domains = ['1', '2']
variables = ['PM2_5_DRY', 'o3', 'AOD550_sfc']
surface_only = 'yes'
regrid = 'yes'

for domain in domains:
    path = os.getcwd() # run from wrf output/base folder
    filelist = []
    filelist.extend(glob.glob(path + '/wrfout_d0' + domain + '_' + year + '-'+ month + '*'))
    filelist = sorted(filelist)
    for variable in variables:
        # concatenate
        with salem.open_mf_wrf_dataset(filelist, chunks={'Time': -1}) as ds:
            if (surface_only == 'yes') and (variable == 'PM2_5_DRY') or (variable == 'o3'):
                wrf = ds[variable].isel(bottom_top=0)
            else:
                wrf = ds[variable]

        # regrid
        if regrid == 'yes':
            ds_out = xr.Dataset({'lat': (['lat'], np.arange(-60, 85, 0.25)), 'lon': (['lon'], np.arange(-180, 180, 0.25)),})
            regridder = xe.Regridder(wrf, ds_out, 'bilinear', reuse_weights=True)
            wrf_regrid = regridder(wrf)

        wrf_regrid.to_netcdf(path + '/wrfout_d0' + domain + '_global_'+ str(res) +'deg_' + year + '-' + month + '_' + variable + '.nc')

    regridder.clean_weight_file()

