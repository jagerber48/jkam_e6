class andor_configuration(object):
    
    '''
    path to atmcd32d.dll SDK library
    '''
    path_to_dll = 'C:\\Program Files\\Andor iXon 4.9\\atmcd32d.dll'
    #default parameters
    cooler = False
    set_temperature = 20 #degrees C
    read_mode = 'Image'
    acquisition_mode = 'Kinetics'
    trigger_mode = 'Internal'
    exposure_time = 0.0003 #seconds
    preamp_gain = None
    output_amp = 0
    vs_speed = 0
    hs_speed = 0
    binning = [2, 2] #numbers of pixels for horizontal and vertical binning
    image_region = [2, 2, 1, 1000, 30, 631] #[hbin, vbin, hstart, hend, vstart, vend]
    
    
