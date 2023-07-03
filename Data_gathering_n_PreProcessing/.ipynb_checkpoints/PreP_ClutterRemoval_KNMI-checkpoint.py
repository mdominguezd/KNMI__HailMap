import wradlib as wrl
from datetime import datetime
import datetime as dt

def detect_clutter(filename):
    """
      Objective: Detect the clutter from a b-scan radar data file.

      Inputs:
          - filename: Name of the hdf5 file to be projected

      Outputs:
          - clutter_maps: List with b-scans of the clutter that was detected with the gabella filter

    """
    # Read radar data
    raw = wrl.io.read_opera_hdf5(filename)

    var = 'Z'

    # Name of the antenna
    name = str(raw['radar1']['radar_name']).split("'")[1]

    # Time of measurement
    time = filename.split('_')[-1].split('.')[0]
    time = datetime.strptime(time, '%Y%m%d%H%M')

    print('Detecting clutter for', name,'/', time)

    # Get number of scans
    num_scans = raw['overview']['number_scan_groups'][0]

    # Create empty list in which the clutter maps will be included
    clutter_maps = []

    for i in range(num_scans):

        # get the scan metadata, data and calibration for each elevation
        meta = raw['scan'+str(i+1)]
        what = raw['scan'+str(i+1)+'/scan_'+var+'_data']
        calib = raw['scan'+str(i+1)+'/calibration']

        # Calibrate data (NEED TO CHECK THIS)
        multi = float(str(calib['calibration_'+var+'_formulas']).split('=')[1].split('*')[0])
        sum_ = float(str(calib['calibration_'+var+'_formulas']).split('+')[1].split("'")[0])

        data_ = sum_ + multi * what

        # Detect clutter using the gabella filter
        clutter = wrl.clutter.filter_gabella(data_)

        # Add the clutter map of the scan to the clutter_map list
        clutter_maps.append(clutter)

    return clutter_maps