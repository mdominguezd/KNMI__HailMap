import wradlib as wrl
import numpy as np
import warnings
warnings.simplefilter("ignore")

def interpolate_radar_data(data, coords, proj, sitecoords, maxrange, minelev, maxelev, maxalt, horiz_res, vert_res):
    """
      Objective: Function to interpolate the data in a 3D volume grid

      Inputs:
          - data: Array with the values of a specified variable
          - coords: Array with the xyz coordinates of the specified variable
          - proj: CRS to which the data will be projected
          - sitecoords: Location of the radar antenna
          - Remaining are related to the resolution desired

      Outputs:
          - vol: Masked array with the values of the specified variable
          - xyz: list with x, y and z the coordinates
    """
    
    # Create 3D grid
    trgxyz, trgshape = wrl.vpr.make_3d_grid(sitecoords, proj, maxrange, maxalt, horiz_res, vert_res)

    x = trgxyz[:, 0].reshape(trgshape)[0, 0, :]
    y = trgxyz[:, 1].reshape(trgshape)[0, :, 0]
    z = trgxyz[:, 2].reshape(trgshape)[:, 0, 0]

    xyz = [x, y, z]

    # interpolate to Cartesian 3-D volume grid
    gridder = wrl.vpr.CAPPI(coords, trgxyz, trgshape, maxrange, minelev, maxelev)
    vol = np.ma.masked_invalid(gridder(data).reshape(trgshape))

    return vol, xyz