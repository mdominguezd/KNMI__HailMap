import wradlib as wrl
from Clutter_Removal import detect_clutter

def project_radar_data(filename, EPSG, AntennaElev, var, gabella = True):
    """
      Objective: Project the 3D radar data to a coordinate reference system (CRS) specified by an EPSG.

      Inputs:
          - filename: Name of the hdf5 file to be projected
          - EPSG: EPSG code of the coordinate reference system to which the dta will be projected
          - AntennaElev: Elevation of the antenna above sea level
          - var: Name of the variable to be projected (e.g. Z, Zv, CCOR, CPA, etc)

      Outputs:
          - data: Array with the values of the variable specified
          - xyz: 3D coordinates of each value
          - rad_dict: dictionary with data from the radar (e.g. name, num_scans, sitecoords, elevation angles)

    """
    # Read radar data
    raw = wrl.io.read_opera_hdf5(filename)

    # Name of the antenna
    name = str(raw['radar1']['radar_name']).split("'")[1]

    # Time of measurement
    time = filename.split('_')[-1].split('.')[0]
    time = datetime.strptime(time, '%Y%m%d%H%M')

    print('Projecting data for', name,'/', time)

    # Get number of scans
    num_scans = raw['overview']['number_scan_groups'][0]

    if gabella:
        # Detect clutter maps
        clutter_maps = detect_clutter(filename)

    # this is the radar position tuple (longitude, latitude, altitude)
    sitecoords = (raw['radar1']['radar_location'][0], raw['radar1']['radar_location'][1])

    # define the cartesian reference system using the EPSG
    proj = osr.SpatialReference()
    proj.ImportFromEPSG(EPSG)

    # Empty arrays to hold Cartesian coordinates and data
    xyz, data = np.array([]).reshape((-1, 3)), np.array([])

    elevs = []

    for i in range(num_scans):

        # get the scan metadata, data and calibration for each elevation
        meta = raw['scan'+str(i+1)]
        what = raw['scan'+str(i+1)+'/scan_'+var+'_data']
        calib = raw['scan'+str(i+1)+'/calibration']

        naray = what.shape[0]
        nbins = what.shape[1]

        # define variable with elevation angle and append it to elevs list
        el = meta['scan_elevation'][0]
        elevs.append(el)
        
        # define array with azimuth angles 
        az = np.arange(0.0, 360.0, 360.0 / naray).reshape(360,1)

        bin_range = (299792458./(2.*meta['scan_high_PRF'][0]))/nbins

        # maximum range for the KNMI radar dataset is supposed to be 200 km.
        r = np.linspace(0,nbins*bin_range, nbins)

        # Calibrate data (NEED TO CHECK THIS)
        multi = float(str(calib['calibration_'+var+'_formulas']).split('=')[1].split('*')[0])
        sum_ = float(str(calib['calibration_'+var+'_formulas']).split('+')[1].split("'")[0])

        data_ = sum_ + multi * what

        if gabella:
            data_[clutter_maps[i]] = np.nan

        site = (sitecoords[0], sitecoords[1], AntennaElev) # Check if elevation = 50m
        
        # Get volumetric coordinates
        xyz_ = wrl.vpr.volcoords_from_polar(site, el, az, ranges = r, proj = proj)

        xyz, data = np.vstack((xyz, xyz_)), np.append(data, data_.ravel())

    # Radar characteristics
    rad_dict = {'name' : name,
                'time': time,
                'num_scans' : num_scans,
                'sitecoords' : sitecoords,
                'elev_ang' : elevs,
                'proj':proj}

    return data, xyz, rad_dict