# Plot and/or write a map for a specific component, scenario, and year
import numpy as np              # Numpy
from netCDF4 import Dataset     # This package reads netcdf files
import matplotlib.pyplot as plt # Matplotlib's pyplot used to make the plots
import os                       # Extracts directory names etc
from scipy.interpolate import interp2d

def example_run():
    confidence = 'Medium'

    # For years: choose from [2020, 2030, 2040, 2050, 2060, 2070, 2080, 2090, 2100, 2110, 2120, 2130, 2140, 2150]
    year = 2100

    # if confidence is 'medium', choose scenario from ['ssp119', 'ssp126', 'ssp245', 'ssp370', 'ssp585']
    # if confidence is 'low', choose scenario from ['ssp126', 'ssp245','ssp585']
    scenario='ssp585'

    # For process, choose from
    for process in ['glaciers','GIS','AIS','landwaterstorage','oceandynamics','verticallandmotion','total']:
        write_scenario_map(confidence, year, scenario, process)

    # process='total'

    plot_scenario_map(confidence, year, scenario, process)
    write_scenario_map(confidence, year, scenario, process)

def plot_scenario_map(confidence,year,scenario,process):
    dir_data = os.getenv('HOME')+'/Data/AR6/Regional/' # Here I've put the data, must probably change for each user

    # lat,lon coords and land-sea mask
    fn = dir_data +  confidence + 'Confidence/' + scenario + '/' + 'total' + '_' + scenario + '_' + confidence + '_confidence_values.nc'
    fh = Dataset(fn, 'r')
    fh.set_auto_mask(False)
    lat = fh['lat'][1030:].reshape(181,360)[:,0]
    lon = fh['lon'][1030:].reshape(181,360)[0,:]
    lon[lon<0]+=360
    fh.close()

    mask = compute_sea_mask(lat, lon)


    fn = dir_data +  confidence + 'Confidence/' + scenario + '/' + process + '_' + scenario + '_' + confidence + '_confidence_values.nc'
    fh = Dataset(fn, 'r')
    fh.set_auto_mask(False)

    # Time steps
    years = fh['years'][:14]
    year_idx = np.where(years == year)[0][0]

    # Find quantiles
    l_quant = np.where(fh['quantiles'][:] == 0.05)[0][0]
    m_quant = np.where(fh['quantiles'][:] == 0.50)[0][0]
    h_quant = np.where(fh['quantiles'][:] == 0.95)[0][0]
    quants = np.array([l_quant,m_quant,h_quant])

    4[quants,year_idx,1030:].reshape(3,181,360)/1000
    fh.close()

    gridlims = 0.9*np.max(grid)

    fig, axs = plt.subplots(3, 1, figsize=(10, 15), sharex=True)
    tst = axs[0].pcolormesh(lon,lat,mask*grid[0,:,:],shading='auto',vmin=-gridlims,vmax=gridlims,cmap="RdYlBu_r")
    axs[0].set_title("Lower bound")
    axs[0].contour(lon,lat,mask,[0.5],colors='k',linewidths=0.5)
    axs[1].pcolormesh(lon,lat,mask*grid[1,:,:],shading='auto',vmin=-gridlims,vmax=gridlims,cmap="RdYlBu_r")
    axs[1].contour(lon,lat,mask,[0.5],colors='k',linewidths=0.5)
    axs[1].set_title("Median")
    axs[2].pcolormesh(lon,lat,mask*grid[2,:,:],shading='auto',vmin=-gridlims,vmax=gridlims,cmap="RdYlBu_r")
    axs[2].contour(lon,lat,mask,[0.5],colors='k',linewidths=0.5)
    axs[2].set_title("Upper bound")
    fig.suptitle('Process '+ process+" Scenario "+scenario + " Year "+str(year))
    fig.colorbar(tst, ax=axs[2], orientation='horizontal', fraction=.075,label="Sea level (m)")
    fig.tight_layout()
    return

def write_scenario_map(confidence,year,scenario,process):
    dir_data = os.getenv('HOME')+'/Data/AR6/Regional/' # Here I've put the data, must probably change for each user

    # lat,lon coords and land-sea mask
    fn = dir_data +  confidence + 'Confidence/' + scenario + '/' + 'total' + '_' + scenario + '_' + confidence + '_confidence_values.nc'
    fh = Dataset(fn, 'r')
    fh.set_auto_mask(False)
    lat = fh['lat'][1030:].reshape(181,360)[:,0]
    lon = fh['lon'][1030:].reshape(181,360)[0,:]
    lon[lon<0]+=360
    fh.close()

    mask = compute_sea_mask(lat, lon)

    fn = dir_data +  confidence + 'Confidence/' + scenario + '/' + process + '_' + scenario + '_' + confidence + '_confidence_values.nc'
    fh = Dataset(fn, 'r')
    fh.set_auto_mask(False)

    # Time steps
    years = fh['years'][:14]
    year_idx = np.where(years == year)[0][0]

    # Find quantiles
    l_quant = np.where(fh['quantiles'][:] == 0.05)[0][0]
    m_quant = np.where(fh['quantiles'][:] == 0.50)[0][0]
    h_quant = np.where(fh['quantiles'][:] == 0.95)[0][0]
    quants = np.array([l_quant,m_quant,h_quant])

    grid = fh['sea_level_change'][quants,year_idx,1030:].reshape(3,181,360)
    fh.close()

    # Write the scenario
    dir_write = os.getenv('HOME')+'/Projects/2021_Portal_AR6/Data/Results/' # Here to store the written files
    fn = dir_write + process + "_" + str(year) + '_' + scenario +'_' + confidence +'.nc'
    fh = Dataset(fn, 'w')
    fh.createDimension('lon', len(lon))
    fh.createDimension('lat', len(lat))
    fh.createDimension('CI', 3)
    fh.createVariable('lon', 'f4', ('lon',),zlib=True)[:] = lon
    fh.createVariable('lat', 'f4', ('lat',),zlib=True)[:] = lat
    fh.createVariable('CI', 'f4', ('CI',),zlib=True)[:] = np.array([0.05,0.50,0.95])
    fh.createVariable('sealevel (mm)','i4',('CI','lat','lon',),zlib=True)[:] = grid
    fh.createVariable('mask','i4',('lat','lon',),zlib=True)[:] = mask
    fh.close()
    return

def compute_sea_mask(lat,lon):
    fn = os.getenv('HOME')+'/Data/GRACE/JPL_mascon/LAND_MASK.CRI.nc'
    fh = Dataset(fn, 'r')
    fh.set_auto_mask(False)
    lon_GRACE = fh["lon"][:]
    lat_GRACE = fh["lat"][:]
    mask_GRACE = 1.0 - fh['land_mask'][:]

    mask = np.flipud((interp2d(lon_GRACE,lat_GRACE,mask_GRACE,kind='linear')(lon,lat)) > 0.5)

    return mask




