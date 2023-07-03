import numpy as np
import warnings
warnings.simplefilter("ignore")

from Data_gathering_n_PreProcessing.PreP_Download_KNMI import download_KNMI
from Data_gathering_n_PreProcessing.PreP_Project_KNMIRadarData import project_radar_data
from Data_gathering_n_PreProcessing.PreP_KNMIData_Interpolation import interpolate_radar_data
from HailDetectionAlgorithms.HDA_MEHS import MEHS_grid
from Visualization.VIS_MEHS import vis_mehs

# Get API key for KNMI data download
with open('KEYS.txt') as f:
    key = f.read()

# Download data for a specified time
filenames = download_KNMI(key, 20200612, 1945)

v = []
c = []
m = []

for fn in filenames:
    # Convert coordinates from polar to cartesian and project them to a knwon CRS
    data, xyz, rad_dict = project_radar_data(fn, 32632, 50, 'Z')

    res_params = dict(maxrange = 200000.0,
                  minelev = np.min(rad_dict['elev_ang']),
                  maxelev = np.max(rad_dict['elev_ang']),
                  maxalt = 15000.0,
                  horiz_res = 1000.0,
                  vert_res = 250.0)

    # Interpote Radar data
    vol, xyz = interpolate_radar_data(data, xyz, rad_dict['proj'], rad_dict['sitecoords'], **res_params)
    v.append(vol)
    c.append(xyz)

    # Apply MEHS algorithm
    mehs = MEHS_grid(vol, xyz, [3000, 5900])
    m.append(mehs)


vis_mehs(m, c)
    
    

    

