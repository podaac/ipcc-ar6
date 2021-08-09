# -----------------------------------------------------------------------------------------
# Read the AR6 projections for a specific location or a grid
# You need to choose from:
# - confidence: 'low' or 'medium'
# - psmsl_id: the PSMSL id of the tide-gauge location for which to read and plot the files
# - thresholds: list of thresholds for threshold plot
# -----------------------------------------------------------------------------------------
# Dependencies
import numpy as np              # Numpy
from netCDF4 import Dataset     # This package reads netcdf files
import matplotlib.pyplot as plt # Matplotlib's pyplot used to make the plots
import os                       # Extracts directory names etc

def example_run():
    # This example plots sea level in the georgeous town of Delfzijl
    confidence = 'medium'
    psmsl_id = 24
    thresholds = [0.25,0.5,1,1.5]                          # Plot the years for which these thresholds (in m) are met
    print_years = [2030,2050,2090,2100,2150]               # Print the numbers for the table for these years
    print_rate_tspan = np.array([[2040,2060],[2080,2100],[2130,2150]]) # Print the rates over these periods
    read_and_plot(confidence,psmsl_id,thresholds,print_years,print_rate_tspan)
    return


def read_and_plot(confidence,psmsl_id,thresholds,print_years,print_rate_tspan):
    if confidence=='medium':
        scenario_list = ['ssp119', 'ssp126', 'ssp245', 'ssp370', 'ssp585']
    elif confidence=='low':
        scenario_list = ['ssp126', 'ssp245','ssp585']

    processes       = ['glaciers','GIS','AIS','landwaterstorage','oceandynamics','verticallandmotion','total']
    processes_long  = ['Glaciers','Greenland','Antarctica','Land water storage','Sterodynamic sea level','Vertical land motion','Total sea level']

    sealevel = read_sealevel(confidence, psmsl_id, scenario_list, processes)
    plot_tseries(scenario_list, processes, processes_long, sealevel)
    plot_thresholds(scenario_list, sealevel, thresholds)

    # Print heights (m)
    print_table_heights(sealevel, scenario_list, processes, processes_long, print_years)

    # print rates (mm yr-1)
    print_table_rates(sealevel, scenario_list, processes, processes_long, print_rate_tspan)

    return


def read_sealevel(confidence,psmsl_id,scenario_list,processes):
    sealevel = {}
    dir_data = os.getenv('HOME')+'/Data/AR6/regional/' # Directory to be changed by user

    # Find index of psmsl station
    fn = dir_data + 'confidence_output_files/' + confidence + '_confidence/' + scenario_list[0] + '/' + processes[0] + '_' + scenario_list[0] + '_' + confidence + '_confidence_values.nc'
    fh = Dataset(fn, 'r')
    fh.set_auto_mask(False)
    station_index = np.where(fh['locations'][:1030] == psmsl_id)[0]
    if len(station_index) == 0:
        raise NameError('The PSMSL index you provided was not found. Try another station')
    station_index = station_index[0]

    # Find quantiles
    l_quant = np.where(fh['quantiles'][:] == 0.05)[0][0]
    m_quant = np.where(fh['quantiles'][:] == 0.50)[0][0]
    h_quant = np.where(fh['quantiles'][:] == 0.95)[0][0]
    quants = np.array([l_quant,m_quant,h_quant])

    # Time steps
    sealevel['years'] = fh['years'][:14]
    fh.close()

    # Read time series
    for scenario in scenario_list:
        sealevel[scenario] = {}
        for process in processes:
            fn = dir_data + 'confidence_output_files/'+confidence+'_confidence/'+scenario+'/'+process+'_'+scenario+'_'+confidence+'_confidence_values.nc'
            fh = Dataset(fn,'r')
            fh.set_auto_mask(False)
            sealevel[scenario][process] = fh['sea_level_change'][quants,:14,station_index]
            fh.close()



    return sealevel


def plot_tseries(scenario_list,processes,processes_long,sealevel):
    # Plot the time series for each process
    colors = ['C0','C1','C2','C3','C4'] # Pre-define colors
    for process_idx,process in enumerate(processes):
        # We make one figure for each process
        plt.figure()
        for scenario_idx,scenario in enumerate(scenario_list): # For each process plot eac h scenario in a single figure
            plt.fill_between(sealevel['years'],sealevel[scenario][process][0,:]/1000, sealevel[scenario][process][2,:]/1000,alpha=0.2,color=colors[scenario_idx]) # Plot uncertainty range as filled area
            plt.plot(sealevel['years'],sealevel[scenario][process][1,:]/1000,label=scenario,color=colors[scenario_idx],linewidth=2) # Plot median as solid line
            plt.xlim(sealevel['years'][0],sealevel['years'][-1])
            plt.ylabel('Height (m)')
            plt.title(processes_long[process_idx],fontsize=10)
            plt.legend(loc=2,fontsize=10)
            plt.grid()
            plt.tight_layout()
    return


def plot_thresholds(scenario_list,sealevel,thresholds):
    # Plot the exceedance thresholds. In other words, at which time is a specific sea level rise to be expected.
    # As in, in what year IJmuiden will face a sea-level rise of more than 1 meter for a specific scenario?

    # We make a panel for each threshold
    fig, axs = plt.subplots(len(thresholds), 1, figsize=(5, 2.5*len(thresholds)), sharex=True)
    colors = ['C0','C1','C2','C3','C4'] # Pre-define colors, so we match the fill and line
    for idx_t,threshold in enumerate(thresholds): # Loop over thresholds
        for idx_s,scenario in enumerate(scenario_list): # Loop over scenarios
            # Determine for the relevant quantiles when the threshold is reached
            yr_lower  = find_threshold(sealevel['years'], sealevel[scenario]['total'][0,:], threshold)
            yr_median = find_threshold(sealevel['years'], sealevel[scenario]['total'][1,:], threshold)
            yr_upper  = find_threshold(sealevel['years'], sealevel[scenario]['total'][2,:], threshold)
            # Plot the median threshold as a circle
            axs[idx_t].plot([yr_median],[idx_s],'o',color=colors[idx_s],markersize=12)
            # Plot the 5-95th quantile as a line
            axs[idx_t].plot([yr_lower,yr_upper],[idx_s, idx_s],color=colors[idx_s],linewidth=5,alpha=0.7)
        axs[idx_t].set_title('Exceedance of '+str(threshold)+ 'm by:',fontsize=10)
        axs[idx_t].set_xlim([2020,2150])
        axs[idx_t].set_ylim([-0.5,len(scenario_list)-0.5])
        axs[idx_t].set_yticks(np.arange(len(scenario_list)))
        axs[idx_t].set_yticklabels(scenario_list)
        axs[idx_t].grid()
    fig.tight_layout()
    return


def find_threshold(time,proj_lcl,threshold):
    # Determine the time when projected sea level (proj_lcl) surpasses threshold
    min_idx = np.where((proj_lcl - (1000 * threshold)) > 0)[0]
    if len(min_idx) == 0: # Set to high year outside plot range if threshold never reached
        t_threshold = 2400
    else:
        t_threshold = time[min_idx[0]]
    return t_threshold

def print_table_heights(sealevel,scenario_list,processes,processes_long,print_years):
    print("=================================================")
    print("Sea levels (m):  mean [lower bound - upper bound]")
    print("=================================================")
    print(" ")
    print("---------------------------------------------------------------------------")
    for print_year in print_years:
        print(" Year "+str(print_year)+":")
        year_idx = np.where(sealevel['years'] == print_year)[0]
        if len(year_idx) == 0:
            raise NameError('The year ' + str(print_year) +' you provided was not found. Try another year')
        year_idx = year_idx[0]
        for scenario in scenario_list:
            print("   Scenario " + scenario + ":")
            for process_idx,process in enumerate(processes):
                hgts = sealevel[scenario][process][:,year_idx] / 1000
                print('      '+processes_long[process_idx]+": "+str(hgts[1])+" ["+str(hgts[0])+" - "+str(hgts[2])+"] m")
        print("---------------------------------------------------------------------------")
        print(" ")
    return

def print_table_rates(sealevel,scenario_list,processes,processes_long,print_rate_tspan):
    print("===========================================================")
    print("Sea level trend (mm yr-1): mean [lower bound - upper bound]")
    print("===========================================================")
    print(" ")
    print("---------------------------------------------------------------------------")
    for tspan_idx in np.arange(print_rate_tspan.shape[0]):
        print(" Years "+str(print_rate_tspan[tspan_idx,:])+":")
        years_idx = (sealevel['years'] >= print_rate_tspan[tspan_idx,0]) & (sealevel['years'] <= print_rate_tspan[tspan_idx,1])
        if sum(years_idx) < 3:
            raise NameError('Period ' + str(print_rate_tspan[tspan_idx,:]) +' too short: I want 3 decadal points at least')
        amat = np.ones([sum(years_idx),2])
        amat[:,1] = sealevel['years'][years_idx]
        for scenario in scenario_list:
            print("   Scenario " + scenario + ":")
            for process_idx,process in enumerate(processes):
                t_low =  np.linalg.lstsq(amat,sealevel[scenario][process][0,years_idx],rcond=None)[0][1]
                t_med =  np.linalg.lstsq(amat,sealevel[scenario][process][1,years_idx],rcond=None)[0][1]
                t_high = np.linalg.lstsq(amat,sealevel[scenario][process][2,years_idx],rcond=None)[0][1]
                print('      '+processes_long[process_idx]+": "+"{:.2f}".format(t_med)+" ["+"{:.2f}".format(t_low)+" - "+"{:.2f}".format(t_high)+"] mm yr-1")
        print("---------------------------------------------------------------------------")
        print(" ")
    return

example_run()
