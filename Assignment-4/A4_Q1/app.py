import os
import cv2
import math
import imutils
import numpy as np
import depthai as dai
from imutils import contours, perspective
from scipy.spatial import distance as dist
from flask import Flask, render_template, request, Response

app = Flask(__name__)

# Function to identify QR codes in a frame
def identify_qr_codes(frame):
    qr_detector = cv2.QRCodeDetector()
    ret, decoded_info, points, _ = qr_detector.detectAndDecodeMulti(frame)
    if ret:
        for info, point in zip(decoded_info, points):
            if info:
                frame = cv2.polylines(frame, [point.astype(int)], True, (255, 0, 255), 8)  # Purple lines
                cv2.putText(frame, info, (int(point[0][0]), int(point[0][1])-10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)  # Yellow text
            else:
                color = (0, 255, 255)  # Cyan color
                frame = cv2.polylines(frame, [point.astype(int)], True, color, 8)
    return frame

# Object tracking class
class ObjectTracker:
    def __init__(self):
        self.object_centers = {}
        self.object_id_count = 0

    def update(self, frame):
        roi = frame
        object_detector = cv2.createBackgroundSubtractorMOG2(history=100, varThreshold=40)
        mask = object_detector.apply(roi)
        _, mask = cv2.threshold(mask, 254, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        detections = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > 100:
                x, y, w, h = cv2.boundingRect(cnt)
                detections.append([x, y, w, h])

        tracked_boxes_ids = self._track_objects(detections)
        for box_id in tracked_boxes_ids:
            x, y, w, h, obj_id = box_id
            cv2.rectangle(roi, (x, y), (x + w, y + h), (255, 165, 0), 3)  # Orange rectangle

        return roi

    def _track_objects(self, object_rectangles):
        tracked_objects = []
        for rect in object_rectangles:
            x, y, w, h = rect
            cx = (x + x + w) // 2
            cy = (y + y + h) // 2
            object_detected = False
            for obj_id, center in self.object_centers.items():
                dist = math.hypot(cx - center[0], cy - center[1])
                if dist < 25:
                    self.object_centers[obj_id] = (cx, cy)
                    tracked_objects.append([x, y, w, h, obj_id])
                    object_detected = True
                    break
            if not object_detected:
                self.object_centers[self.object_id_count] = (cx, cy)
                tracked_objects.append([x, y, w, h, self.object_id_count])
                self.object_id_count += 1

        new_object_centers = {}
        for obj_bb_id in tracked_objects:
            _, _, _, _, obj_id = obj_bb_id
            center = self.object_centers[obj_id]
            new_object_centers[obj_id] = center

        self.object_centers = new_object_centers.copy()
        return tracked_objects

# Calculate midpoint
def midpoint(ptA, ptB):
    return ((ptA[0] + ptB[0]) * 0.5, (ptA[1] + ptB[1]) * 0.5)

# Object dimension marking class
class ObjectDimensionMarker:
    def __init__(self, object_width_inches):
        self.object_width_inches = object_width_inches
        self.pixelsPerMetric = None

    def mark_object_dimensions(self, gray_frame):
        edged = cv2.Canny(gray_frame, 50, 100)
        edged = cv2.dilate(edged, None, iterations=1)
        edged = cv2.erode(edged, None, iterations=1)
        cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        (cnts, _) = contours.sort_contours(cnts)
        result_frame = cv2.cvtColor(gray_frame, cv2.COLOR_GRAY2BGR)
        for c in cnts:
            if cv2.contourArea(c) < 100:
                continue
            box = cv2.minAreaRect(c)
            box = cv2.boxPoints(box) if imutils.is_cv2() else cv2.boxPoints(box)
            box = np.array(box, dtype="int")
            box = perspective.order_points(box)
            cv2.drawContours(result_frame, [box.astype("int")], -1, (0, 255, 0), 2)  # Green color
            (tl, tr, br, bl) = box
            (tltrX, tltrY) = midpoint(tl, tr)
            (blbrX, blbrY) = midpoint(bl, br)
            (tlblX, tlblY) = midpoint(tl, bl)
            (trbrX, trbrY) = midpoint(tr, br)
            dA = dist.euclidean((tltrX, tltrY), (blbrX, blbrY))
            dB = dist.euclidean((tlblX, tlblY), (trbrX, trbrY))
            if self.pixelsPerMetric is None:
                self.pixelsPerMetric = dB / self.object_width_inches
            dimA_cm = dA / self.pixelsPerMetric * 2.54
            dimB_cm = dB / self.pixelsPerMetric * 2.54
            cv2.putText(result_frame, "{:.1f} in".format(dimA_cm), (int(tltrX - 15), int(tltrY - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 0), 2)  # Light Blue text
            cv2.putText(result_frame, "{:.1f} in".format(dimB_cm), (int(trbrX + 10), int(trbrY)), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 0), 2)  # Light Blue text
        return result_frame

# Route for the index page
@app.route('/')
def index():
    return render_template('index.html')

# Video feed processing function
def process_feed():
    object_width = 0.995
    try:
        tracker = ObjectTracker()
        object_marker = ObjectDimensionMarker(object_width_inches=object_width)
        pipeline = dai.Pipeline()
        stereo = pipeline.createStereoDepth()
        stereo.setConfidenceThreshold(255)
        left = pipeline.createMonoCamera()
        left.setResolution(dai.MonoCameraProperties.SensorResolution.THE_720_P)
        right = pipeline.createMonoCamera()
        right.setResolution(dai.MonoCameraProperties.SensorResolution.THE_720_P)
        left.out.link(stereo.left)
        right.out.link(stereo.right)
        xoutDepth = pipeline.createXLinkOut()
        xoutDepth.setStreamName("depth")
        stereo.depth.link(xoutDepth.input)
        xoutLeft = pipeline.createXLinkOut()
        xoutLeft.setStreamName("left")
        left.out.link(xoutLeft.input)
        xoutRight = pipeline.createXLinkOut()
        xoutRight.setStreamName("right")
        right.out.link(xoutRight.input)
        cam = pipeline.createColorCamera()
        cam.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
        xout = pipeline.createXLinkOut()
        xout.setStreamName("rgb")
        cam.video.link(xout.input)
        with dai.Device(pipeline) as device:
            depthQueue = device.getOutputQueue(name="depth", maxSize=4, blocking=False)
            leftQueue = device.getOutputQueue(name="left", maxSize=4, blocking=False)
            rightQueue = device.getOutputQueue(name="right", maxSize=4, blocking=False)
            rgbQueue = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)
            device.startPipeline()
            camera_id = 0
            delay = 1
            while True:
                inDepth = depthQueue.get()
                inLeft = leftQueue.get()
                inRight = rightQueue.get()
                inSrc = rgbQueue.get()
                depthFrame = inDepth.getFrame()
                leftFrame = inLeft.getCvFrame()
                rightFrame = inRight.getCvFrame()
                rgbFrame = inSrc.getCvFrame()
                stereoFrame = cv2.hconcat([leftFrame, rightFrame])
                stereoFrame = identify_qr_codes(stereoFrame)
                stereoFrame = tracker.update(stereoFrame)
                gray_frame = cv2.cvtColor(rgbFrame, cv2.COLOR_BGR2GRAY)
                frame = object_marker.mark_object_dimensions(gray_frame)
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    except:
        tracker = ObjectTracker()
        object_marker = ObjectDimensionMarker(object_width_inches=object_width)
        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame = identify_qr_codes(frame)
            frame = tracker.update(frame)
            frame = object_marker.mark_object_dimensions(frame)
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# Route for video streaming
@app.route('/video_stream')
def video_stream():
    return Response(process_feed(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Route for live streaming
@app.route('/livestreaming', methods=['GET', 'POST'])
def object_detection():
    try:
        return render_template('result.html')
    except Exception as e:
        return render_template('index.html', message=str(e))

if __name__ == '__main__':
    app.run(debug=True)
