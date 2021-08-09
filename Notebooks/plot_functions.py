import numpy as np # We will use numpy arrays to read stored data
import matplotlib.pyplot as plt # We use matplotlib to make the plots
import pandas as pd # Pandas can read the excel file
import ipywidgets as widgets

def define_widgets():
    scenario = widgets.Dropdown(
        options=['SSP1.19', 'SSP1.26', 'SSP2.45', 'SSP3.70', 'SSP5.85'],
        description='Scenario:',
        value='SSP2.45',
        disabled=False,
    )
    process = widgets.Dropdown(
        options=['Sterodynamic', 'Glaciers', 'Greenland Ice Sheet', 'Antarctic Ice Sheet', 'Land water storage', 'Vertical land motion', 'Total'],
        description='Process:',
        value='Total',
        disabled=False,
    )
    confidence = widgets.Dropdown(
        options=['Medium', 'Low'],
        description='Confidence level:',
        value='Medium',
        disabled=False,
    )
    return(scenario,process,confidence)

def return_labels(scenario,process,confidence):
    scenario_dict = {'SSP1.19':'ssp119', 'SSP1.26':'ssp126', 'SSP2.45':'ssp245','SSP3.70':'ssp370','SSP5.85':'ssp585'}
    process_dict = {'Sterodynamic':'Sterodynamic', 'Glaciers':'Glaciers','Greenland Ice Sheet':'GIS','Antarctic Ice Sheet':'AIS','Land water storage':'LandWaterStorage','Vertical land motion':'VerticalLandMotion','Total':'Total'}
    confidence_dict={'Medium':'medium','Low':'low'}
    if (confidence == 'Low') & (scenario!='SSP1.26') & (scenario!='SSP5.85'):
        confval='Medium'
        print('Low confidence only available for SSP1.26 and SSP5.85. Showing medium confidence instead')
    else:
        confval=confidence
    return scenario_dict[scenario], process_dict[process], confidence_dict[confval]

def read_and_plot(scenario, process, confidence,filename):
    scenario_key, process_key, confidence_key = return_labels(scenario, process, confidence)

    data_table = pd.read_excel(filename, process_key)
    # percentiles = data_table[(data_table["scenario"] == scenario_key) & (data_table["confidence"] == confidence_key)].iloc[:, 4].to_numpy()
    sealevel_values = data_table[(data_table["scenario"] == scenario_key) & (data_table["confidence"] == confidence_key)].iloc[:, 5:].to_numpy()
    years = np.array(list(data_table.columns)[5:])

    plt.figure()
    plt.fill_between(years, sealevel_values[0, :], sealevel_values[4, :], alpha=0.2, color='C0',label='5-95% confidence interval')
    plt.fill_between(years, sealevel_values[1, :], sealevel_values[3, :], alpha=0.4, color='C0',label='17-83% confidence interval')
    plt.plot(years, sealevel_values[2, :], color='C0',label='Median')
    plt.xlim([years[0], years[-1]])
    plt.ylabel('Sea level (m)')
    plt.title('Process: '+process+'  Scenario: '+scenario+'  Confidence: '+confidence,fontsize=10)
    plt.legend()
    plt.tight_layout()
    plt.show()
    return


# def garbage:
#     display(scenario)
#     display(process)
#     display(confidence)
#
#     scenario_key, process_key, confidence_key = plf.return_labels(scenario, process, confidence)
#
#     data_table = pd.read_excel(filename, process_key)
#     percentiles = data_table[(data_table["scenario"] == scenario_key) & (data_table["confidence"] == confidence_key)].iloc[:, 4].to_numpy()
#     sealevel_values = data_table[(data_table["scenario"] == scenario_key) & (data_table["confidence"] == confidence_key)].iloc[:, 5:].to_numpy()
#     years = np.array(list(data_table.columns)[5:])
#
#     plt.figure()
#     plt.fill_between(years, sealevel_values[0, :], sealevel_values[4, :], alpha=0.2, color='C0')
#     plt.fill_between(years, sealevel_values[1, :], sealevel_values[3, :], alpha=0.4, color='C0')
#     plt.plot(years, sealevel_values[2, :], color='C0')
#     plt.xlim([years[0], years[-1]])
#     plt.ylabel('Sea level (m)')
#     return