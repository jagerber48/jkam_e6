import numpy as np
from AndorCamera import AndorCamera

cam = AndorCamera()

try:
    gains = cam.get_preamp_gains()
    
    print('#, Gains')
    for idx, gain in enumerate(gains):
        print('{:d}, {:.2f}'.format(idx, gain))

    channel = 0
    outamp = 0
    speeds = cam.get_hs_speeds(channel, outamp)
    
    print('#, HSS')
    for idx, speed in enumerate(speeds):
        print('{:d}, {:.3f}'.format(idx, speed))

    speeds = cam.get_vs_speeds()
    
    print('#, VSS')
    for idx, speed in enumerate(speeds):
        print('{:d}, {:.3f}'.format(idx, speed))
                
    
finally:
    cam.shut_down()
    