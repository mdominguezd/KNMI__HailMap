import contextily as ctx
import matplotlib.pyplot as plt

def vis_mehs(m, c):
    fig, ax = plt.subplots(1,1, figsize = (8,8))
    
    data = ax.imshow(m[0]/10, cmap= 'jet', alpha = 0.55, zorder = 4, vmin = 0, vmax = 4,
                             extent = [min(c[0][0]), max(c[0][0]), max(c[0][1]), min(c[0][1])])
    
    data_ = ax.imshow(m[1]/10, cmap= 'jet', alpha = 0.55, zorder = 4, vmin = 0, vmax = 4,
                             extent = [min(c[1][0]), max(c[1][0]), max(c[1][1]), min(c[1][1])])
    
    ctx.add_basemap(ax, crs = 32632, alpha = 1, source = ctx.providers.CartoDB.Positron)
    
    ax.invert_yaxis()