from flask import Flask, render_template, send_file
import numpy as np
import cv2
import depthai as dai
import os

app = Flask(__name__)

def capture_image_and_compute():
    # Define the function to capture images using the OAK camera
    def start_capture_integral():
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
                cv2.imshow("OAK Camera", frame)
                
                # Press 's' to capture the image
                key = cv2.waitKey(1) & 0xFF
                if key == ord("s"):
                    # Save the captured frame to a file named "object_image.png"
                    cv2.imwrite("object_image.png", frame)
                    break

            # Release the camera
            cv2.destroyAllWindows()

    # Capture an image
    start_capture_integral()

    # Read the captured image
    object_image = cv2.imread("object_image.png")

    # Compute Integral Image
    img = cv2.imread('object_image.png', cv2.IMREAD_GRAYSCALE)
    integral_img = cv2.integral(img)

    # Normalize the integral image for display
    integral_image = cv2.normalize(integral_img, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)

    # Resize the integral image to match the width of the object image
    integral_image_resized = cv2.resize(integral_image, (object_image.shape[1], object_image.shape[0]))
    cv2.imwrite("integral_image_display.png",integral_image_resized)

    # Concatenate the object image and integral image horizontally
    concat_img = np.concatenate((object_image, cv2.cvtColor(integral_image_resized, cv2.COLOR_GRAY2BGR)), axis=1)
    cv2.imwrite("concatenated_image.png", concat_img)

    # Prepare the output information string
    output_info = f"<h3>Initial Object Image:</h3><img src='/object_image_with_text' alt='Object Image' width='50%'>" \
                  f"<br><h3>Integral Image:</h3><img src='/integral_image_display' alt='Integral Image' width='50%'>" \
                  f"<br><h3>Concatenated Image:</h3><img src='/concatenated_image' alt='Concatenated Image' width='80%'>"

    return output_info

def capture_images(num_images):
    os.makedirs('captured_images', exist_ok=True)
    
    def capture_image(idx):
        pipeline = dai.Pipeline()
        cam = pipeline.createColorCamera()
        cam.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
        xout = pipeline.createXLinkOut()
        xout.setStreamName("video")
        cam.video.link(xout.input)

        with dai.Device(pipeline) as device:
            q = device.getOutputQueue(name="video", maxSize=1, blocking=True)
            frame = None
            while True:
                in_video = q.get()
                frame = in_video.getCvFrame()
                cv2.imshow("OAK Camera", frame)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord("s"):
                    cv2.imwrite(f"captured_images/image_{idx}.png", frame)
                    break

            cv2.destroyAllWindows()

    for i in range(num_images):
        capture_image(i)

    images = [cv2.imread(f'captured_images/image_{i}.png') for i in range(num_images)]
    return images

def stitch_2_imgs(img1, img2, feature='SIFT', blending=True, save_path=None):
    img1_bw = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    img2_bw = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    
    if feature == 'SIFT':
        feat = cv2.SIFT_create() 
    elif feature == 'ORB':
        feat = cv2.ORB_create()
    else:
        print("Please enter correct feature value.")
        return None

    kp_img1, desc_img1 = feat.detectAndCompute(img1_bw, None) 
    kp_img2, desc_img2 = feat.detectAndCompute(img2_bw, None) 

    bf = cv2.BFMatcher()
    matches = bf.knnMatch(desc_img2, desc_img1, k=2)

    good_points = []
    for m, n in matches: 
        if m.distance < 0.6 * n.distance: 
            good_points.append(m) 

    if len(good_points) < 4:
        print("Not enough matches found to compute homography.")
        return None

    query_pts = np.float32([kp_img2[m.queryIdx].pt for m in good_points]).reshape(-1, 1, 2) 
    train_pts = np.float32([kp_img1[m.trainIdx].pt for m in good_points]).reshape(-1, 1, 2) 

    matrix, mask = cv2.findHomography(query_pts, train_pts, cv2.RANSAC, 5.0) 

    dst = cv2.warpPerspective(img2, matrix, ((img1.shape[1] + img2.shape[1]), img2.shape[0])) 

    if blending:
        dst[0:img1.shape[0], 0:img1.shape[1]] = img1
    else:
        dst[0:img1.shape[0], 0:img1.shape[1]] = img1
        dst = cv2.addWeighted(dst, 0.5, img2, 0.5, 0)

    if save_path:
        cv2.imwrite(save_path, dst)

    return dst

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_capture_integral', methods=['POST'])
def start_capture_integral():
    # Run the Python code to capture the image and compute dimensions
    output_info = capture_image_and_compute()
    return render_template('result_integral.html', output_info=output_info)

@app.route('/start_capture_stitch', methods=['POST'])
def start_capture():
    images = capture_images(3)
    
    if len(images) != 3:
        return "Error capturing images", 500

    save_folder = 'stitched_images'
    os.makedirs(save_folder, exist_ok=True)
    
    stitch_2_imgs(images[0], images[1], blending=True, save_path=f"{save_folder}/stitched_1.png")
    stitch_2_imgs(images[1], images[2], blending=True, save_path=f"{save_folder}/stitched_2.png")
    
    stitched_1 = cv2.imread(f"{save_folder}/stitched_1.png")
    stitched_2 = cv2.imread(f"{save_folder}/stitched_2.png")
    
    panorama = stitch_2_imgs(stitched_1, stitched_2, blending=True, save_path=f"{save_folder}/panorama.png")
    
    output_info = f"<h3>Stitched Image 1:</h3><img src='/stitched_images_stitched_1' alt='Stitched Image 1' width='50%'>" \
                  f"<br><h3>Stitched Image 2:</h3><img src='/stitched_images_stitched_2' alt='Stitched Image 2' width='50%'>" \
                  f"<br><h3>Panorama:</h3><img src='/stitched_images_panorama' alt='Panorama' width='80%'>"

    return render_template('result_stitch.html', output_info=output_info)

@app.route('/object_image_with_text')
def get_captured_image():
    return send_file('object_image.png', mimetype='image/png')

@app.route('/integral_image_display')
def get_integral_image():
    return send_file('integral_image_display.png', mimetype='image/png')

@app.route('/concatenated_image')
def get_concatenated_image():
    return send_file('concatenated_image.png', mimetype='image/png')

@app.route('/stitched_images_stitched_1')
def get_image():
    return send_file('stitched_images/stitched_1.png', mimetype='image/png')

@app.route('/stitched_images_stitched_2')
def get_stitched_image():
    return send_file('stitched_images/stitched_2.png', mimetype='image/png')

@app.route('/stitched_images_panorama')
def get_panorama_image():
    return send_file('stitched_images/panorama.png', mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)
