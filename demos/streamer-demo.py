"""
  Kinect for Azure Color, Depth and Infrared streaming in Python

  Supported resolutions:
  720:  1280 x 720 @ 25 FPS  binned depth
  1080: 1920 x 1080 @ 24 FPS binned depth
  1440: 2560 x 1440 @ 22 FPS binned depth
  1535: 2048 x 1536 @ 23 FPS binned depth
  2160: 3840 x 2160 @ 20 FPS binned depth
  3072: 4096 x 3072 @ 12 FPS binned depth
"""
import numpy as np 
import cv2
import pyk4

# Create Kinect object and initialize
kin = pyk4.Kinect(resolution=720, wfov=True, binned=True, framerate=30)
kin.setGain(gain = 200)
kin.setExposure(exposure = 8330)


# initialize fps counter
t = cv2.getTickCount()
fps_count = 0
fps = 0

while True:
    if fps_count==0:
      t = cv2.getTickCount()

    # read kinect frames. If frames available return 1
    if kin.getFrames(getColor=True, getDepth=True, getIR=True):
        color_data = kin.getColorData()
        depth_data = kin.getDepthData(align=True)
        ir_data = kin.getIRData()

        # extract frames to np arrays
        depth_image = np.array(depth_data, copy = True)
        color_image = np.array(color_data, copy = True) # image is BGRA
        color_image = cv2.cvtColor(color_image, cv2.COLOR_BGRA2BGR) # to BGR
        ir_image = np.array(ir_data, copy = True)
        print("Current exposure:", kin.getExposure())

        print('Depth shape and type:', depth_image.shape, depth_image.dtype)
        print('Color shape type:', color_image.shape, color_image.dtype)
        print('IR shape and type:', ir_image.shape, ir_image.dtype)
        print('Depth range values:', np.amin(depth_image), np.amax(depth_image))
        print('IR range values:', np.amin(ir_image), np.amax(ir_image))

        # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)

        # Reescale IR image values
        ir_image = cv2.convertScaleAbs(ir_image, alpha=0.04)

        # Resize images
        depth_small = cv2.resize(depth_colormap, None, fx=0.5, fy=0.5)
        color_small = cv2.resize(color_image, None, fx=0.25, fy=0.25)
        size = color_small.shape[0:2]
        cv2.putText(color_small, "{0:.2f}-FPS".format(fps), (20, size[0]-20), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 0, 255), 2)

        cv2.imshow('Depth', depth_small)
        cv2.imshow('Color', color_small)
        cv2.imshow('IR', ir_image)

    k = cv2.waitKey(1) & 0xFF
    if k == 27:
        break
    elif k == ord('s'):
        cv2.imwrite("color.jpg", color_image)
        print("Image saved")

    # increment frame counter and calculate FPS
    fps_count = fps_count + 1
    if (fps_count == 20):
      t = (cv2.getTickCount() - t)/cv2.getTickFrequency()
      fps = 20.0/t
      fps_count = 0

kin.close()  # close Kinect
cv2.destroyAllWindows()