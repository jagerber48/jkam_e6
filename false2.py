
import numpy as np
import pyqtgraph as pg

#Andor FALSE2 colormap
pos = np.linspace(0,1,9)
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
cmap = pg.ColorMap(pos, color_list)