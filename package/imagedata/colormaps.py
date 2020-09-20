import matplotlib.pyplot as plt
import numpy as np
import pyqtgraph as pg


def generate_andor_false2_colormap():
    # Andor FALSE2 colormap
    pos = np.linspace(0, 1, 9)
    color_list = np.array([
        [     0,     0,     0, 255],
        [   160,     0,   255, 255],
        [     0,     0,   255, 255],
        [     0,   255,   255, 255],
        [     0,   255,     0, 255],
        [   255,   255,     0, 255],
        [   255,     0,     0, 255],
        [   255,     0,   255, 255],
        [   255,   255,   255, 255]])
    return pg.ColorMap(pos, color_list)


def generate_pg_colormap_from_plt(cm_name):
    pltMap = plt.get_cmap(cm_name)
    pltMap._init()
    colors = pltMap._lut * 255
    colors = colors[:-3]
    positions = np.linspace(0, 1, len(colors))
    pgMap = pg.ColorMap(positions, colors)
    return pgMap


jet_cmap = generate_pg_colormap_from_plt('jet')
gray_cmap = generate_pg_colormap_from_plt('gray')
viridis_cmap = generate_pg_colormap_from_plt('viridis')
false2_cmap = generate_andor_false2_colormap()

cmap_dict = {'jet': jet_cmap,
             'gray': gray_cmap,
             'viridis': viridis_cmap,
             'false2': false2_cmap}
