from atcore import ATCore
import numpy as np
# import pyfits

# def save(image, path, config):
#     hdu = pyfits.PrimaryHDU(image)
#     hdulist=pyfits.HDUList([hdu])
#     for k,v in config.items():
#         hdulist[0].header["HIERARCH " + k.upper()] = v
#     hdulist.writeto(path, clobber=True)

def main() :

    print("Single Scan Example")

    print("Intialising SDK3")
    sdk3 = ATCore() # Initialise SDK3
    deviceCount = sdk3.get_int(sdk3.AT_HNDL_SYSTEM,"DeviceCount");

    print("Found : ",deviceCount," device(s)");

    if deviceCount > 0 :

        try :
            print("  Opening camera ");
            hndl = sdk3.open(0);
            
            print("    Setting up acuisition")
            sdk3.set_enum_string(hndl, "PixelEncoding", "Mono16")

            imageSizeBytes = sdk3.get_int(hndl,"ImageSizeBytes");
            print("    Queuing Buffer (size",imageSizeBytes,")");
            buf = np.empty((imageSizeBytes,), dtype='B')
            sdk3.queue_buffer(hndl,buf.ctypes.data,imageSizeBytes);
            buf2 = np.empty((imageSizeBytes,), dtype='B')
            sdk3.queue_buffer(hndl,buf2.ctypes.data,imageSizeBytes);
            
            print("    Acquiring Frame");
            sdk3.command(hndl,"AcquisitionStart");
            (returnedBuf, returnedSize) = sdk3.wait_buffer(hndl);

            print("    Frame Returned, first 10 pixels");
            pixels = buf.view(dtype='H');
            for i in range(0,10) :
              print("      Pixel ",i," value ",pixels[i])
            
            sdk3.command(hndl,"AcquisitionStop");
            print("    Configuring Image")
            config = {}
            config['aoiheight'] = sdk3.get_int(hndl, "AOIHeight")
            config['aoiwidth'] = sdk3.get_int(hndl, "AOIWidth")
            config['aoistride'] = sdk3.get_int(hndl, "AOIStride")
            config['pixelencoding'] = sdk3.get_enum_string(hndl, "PixelEncoding")

            np_arr = buf[0:config['aoiheight'] * config['aoistride']]
            np_d = np_arr.view(dtype='H')
            np_d = np_d.reshape(config['aoiheight'], round(np_d.size/config['aoiheight']))
            formatted_img = np_d[0:config['aoiheight'], 0:config['aoiwidth']]

            file_name = "./test_fits_image.fits"
            print("    Saving to fits file: {0}".format(file_name))
            # save(formatted_img, file_name, config)

        except ATCoreException as err :
          print("     SDK3 Error {0}".format(err));
        print("  Closing camera");
        sdk3.close(hndl);
    else :
        print("Could not connect to camera");

main()
