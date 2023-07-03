import numpy as np

def MEHS_grid(dBZ_grid, coords, levels):
    
    # Rain/Hail dBZ boundaries
    Zl = 40
    Zu = 50

    # Require levels
    if levels is None:
        raise Exception("Missing levels data for freezing level and -20C level")
        
    # Get z coordinates
    z = coords[2]

    # This dummy proofs the user input. The melting level will always
    # be lower in elevation than the negative 20 deg C isotherm
    meltlayer = np.min(levels)
    neg20layer = np.max(levels)

    # calc reflectivity weighting function
    DBZ_weights = (dBZ_grid - Zl) / (Zu - Zl)
    DBZ_weights[dBZ_grid <= Zl] = 0
    DBZ_weights[dBZ_grid >= Zu] = 1

    # calc hail kenetic energy
    E = (5 * 10 ** -6) * 10 ** (0.084 * dBZ_grid) * DBZ_weights

    # calc temperature based weighting function
    Wt = (z - meltlayer) / (neg20layer - meltlayer)
    Wt[z <= meltlayer] = 0
    Wt[z >= neg20layer] = 1

    inds_echo = np.where(dBZ_grid > 45)[0]

    if len(inds_echo) != 0:
        echo_top_ind = max(np.where(dBZ_grid > 40)[0])
        echo_top_z = z[echo_top_ind]
        
        print('echo top (45dBZ) detected at:',
              echo_top_z, 
              'm')
    else:
        echo_top_ind = max(np.where(z <= neg20layer)[0])
        echo_top_z = neg20layer
        print('No values above 45dBZ were detected.')
    

    We = E[:echo_top_ind,:,:]
    
    for i in range(echo_top_ind):
        We[i] = Wt[i] * E[i] 
    
    dz = coords[2][1]-coords[2][0]

    # calc severe hail index (element wise for integration)
    SHI = 0.1 * np.sum(We, axis=0) * dz

    MESH = 16.566 * SHI ** 0.181
    
    return MESH