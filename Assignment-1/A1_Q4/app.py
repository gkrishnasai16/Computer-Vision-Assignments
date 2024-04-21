from flask import Flask, render_template, send_file
import numpy as np
import cv2 as cv
import depthai as dai
import math

app = Flask(__name__)

def capture_image_and_compute():
    # Define the function to capture images using the OAK camera
    def capture_image():
        # Start defining a pipeline
        pipeline = dai.Pipeline()

        # Define a source - color camera
        cam = pipeline.createColorCamera()
        cam.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)

        # Create output
        xout = pipeline.createXLinkOut()
        xout.setStreamName("video")
        cam.video.link(xout.input)

        # Connect and start the pipeline
        with dai.Device(pipeline) as device:
            # Output queue will be used to get the frames from the output defined above
            q = device.getOutputQueue(name="video", maxSize=1, blocking=True)

            # Get the frames from the camera
            frame = None
            while True:
                in_video = q.get()
                frame = in_video.getCvFrame()
                cv.imshow("OAK Camera", frame)
                
                # Press 'c' to capture the image
                key = cv.waitKey(1) & 0xFF
                if key == ord("c"):
                    # Save the captured frame to a file named "object_image.png"
                    cv.imwrite("object_image.png", frame)
                    break

            # Release the camera
            cv.destroyAllWindows()

            # Read the captured image
            image = cv.imread("object_image.png")

            # Check if the image was read successfully
            if image is None:
                print("Error: Failed to read the image.")
                exit()

    # Load camera intrinsic matrix from file
    camera_matrix = np.loadtxt('images/left/camera_matrix.txt')

    print("CAMERA INTRINSIC MATRIX:")
    print(camera_matrix)

    # Extract focal lengths (FX and FY) from camera matrix
    FX = camera_matrix[0, 0]
    FY = camera_matrix[1, 1]

    # Assuming a baseline distance (distance between the camera and the object) in millimeters
    Z = 350  # Adjust this value based on your setup

    def convert_milli_to_inch(x):
        x = x / 10
        return x / 25.4

    # Capture an image
    capture_image()

    # Read the captured image
    image = cv.imread("object_image.png")

    # Dynamically select ROI
    x, y, w, h = cv.selectROI("Select ROI", image, fromCenter=False)

    # Draw ROI rectangle on the image
    cv.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 5)
    
    # Calculate the midpoint of the top and bottom edges of the ROI
    mid_x = (x + x + w) // 2
    top_y = y
    bottom_y = y + h

    # Draw a red vertical line through the middle of the ROI box
    cv.line(image, (mid_x, top_y), (mid_x, bottom_y), (0, 0, 255), 5)
    
    # Calculate real-world coordinates based on selected ROI
    Real_point1x = Z * (x / FX)
    Real_point1y = Z * (y / FY)
    Real_point2x = Z * ((x + w) / FX)
    Real_point2y = Z * ((y + h) / FY)

    print("Real-world coordinates of Point 1:")
    print(Real_point1x, Real_point1y)
    print("Real-world coordinates of Point 2:")
    print(Real_point2x, Real_point2y)

    # Calculate diameter of the object
    dist = math.sqrt((Real_point2y - Real_point1y) ** 2 + (Real_point2x - Real_point1x) ** 2)
    val = round(convert_milli_to_inch(dist * 2), 5)
    print("Diameter of the object:", val * 10, "inches")

    # Add the computed dimensions to the image
    text = f"Diameter of the object: {val * 10} inches"
    cv.putText(image, f"{val * 10}", (x - 200, (y + y + h) // 2 + 5), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # Save the image with the text
    cv.imwrite("object_image_with_text.png", image)

    # Prepare the output information string
    output_info = f"Real-world coordinates of Point 1: {Real_point1x}, {Real_point1y}<br>" \
                  f"Real-world coordinates of Point 2: {Real_point2x}, {Real_point2y}<br>" \
                  f"{text}"

    return output_info

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_capture', methods=['POST'])
def start_capture():
    # Run the Python code to capture the image and compute dimensions
    output_info = capture_image_and_compute()
    return render_template('result.html', output_info=output_info)

@app.route('/object_image_with_text')
def get_image():
    return send_file('object_image_with_text.png', mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)
