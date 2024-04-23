'''
Implement a real-time object tracker (two versions) that 
(ii) does not use any marker and only relies on the object
'''

import cv2
import depthai as dai

# Create DepthAI pipeline
pipeline = dai.Pipeline()

# Define camera node
cam_rgb = pipeline.createColorCamera()
cam_rgb.setPreviewSize(300, 300)
cam_rgb.setInterleaved(False)

# Create XLinkOut node
xout_rgb = pipeline.createXLinkOut()
xout_rgb.setStreamName("rgb")
cam_rgb.preview.link(xout_rgb.input)

# Connect to the device
with dai.Device(pipeline) as device:
    # Output queue will be used to get the frames from the output defined above
    q_rgb = device.getOutputQueue(name="rgb", maxSize=1, blocking=True)

    # Read the initial frame
    in_rgb = q_rgb.get()
    frame = in_rgb.getCvFrame()

    # Define a region of interest (ROI) for tracking
    x, y, w, h = 200, 200, 100, 100  # Example ROI coordinates
    track_window = (x, y, w, h)

    # Convert the ROI to HSV color space
    roi = frame[y:y+h, x:x+w]
    hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

    # Create a histogram to use for back projection
    roi_hist = cv2.calcHist([hsv_roi], [0], None, [180], [0, 180])
    cv2.normalize(roi_hist, roi_hist, 0, 255, cv2.NORM_MINMAX)

    # Set the termination criteria for the MeanShift algorithm
    term_crit = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1)

    while True:
        # Read a new frame
        in_rgb = q_rgb.get()
        frame = in_rgb.getCvFrame()

        # Convert the frame to HSV color space
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Calculate the back projection based on the histogram
        dst = cv2.calcBackProject([hsv], [0], roi_hist, [0, 180], 1)

        # Apply the MeanShift algorithm to track the object
        ret, track_window = cv2.meanShift(dst, track_window, term_crit)

        # Draw the tracked window on the frame
        x, y, w, h = track_window
        img = cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        # Display the frame
        cv2.imshow('Object Tracking', img)

        # Check if 's' key is pressed to save the image
        key = cv2.waitKey(1)
        if key == ord('s'):
            cv2.imwrite("tracked_object_qr_without_marker.jpg", img)
            print("Image saved as 'tracked_object_qr_without_marker.jpg'.")

        # Break the loop if 'q' is pressed
        if key == ord('q'):
            break

# Release resources
cv2.destroyAllWindows()
