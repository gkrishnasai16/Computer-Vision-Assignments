# CSc 8830: Computer Vision - Assignment 2 Solutions

## Question 1

The solution for this question is provided in the 'A2_Q1.ipynb' file.

The code prompts the user to record a 10-second video, storing its frames in the "video_frames" folder. A random frame from this video underwent Canny edge detection and was saved as 'canny_edge_detection.png'.

![Canny Edge Detection](canny_edge_detection.png)

___

## Question 2

For this question, we manually applied the Harris corner detection algorithm to a 5x5 image patch within a selected region that harbored a corner of interest. This manual detection was then compared with the automated implementation using DepthAI's Harris corner detection function.

The detailed solution is available in 'A2_Q2.ipynb'.

![Harris Corner Detection](harris_corner_detection.png)

___

## Question 3

We implemented the SIFT feature extraction and matching algorithm to calculate the sum of squared differences (SSD) between super-pixel patches from two 'video_frames' images separated by at least 2 seconds with some scene overlap. We also computed the Homography matrix and its inverse using Python.

Find the solution in 'A2_Q3.ipynb'.

![Homography](homography.png)

___

## Question 4

We designed a code to display the integral image feed alongside the RGB feed without relying on any built-in integral image functions. The integral image was initialized to zero, pixel values were copied from the grayscale image, and the integral image was computed using the integral image algorithm.

**Integral Image Matrix:** [Integral Image Matrix File](integral_matrix.txt)

**Integral Image Display for image.jpg:**

![Integral Image](integral_image_display.png)

___

## Question 5

We successfully implemented real-time image stitching for creating 360-degree panoramic outputs using SIFT or ORB features. The panoramas were constructed from images of home and science buildings without using direct built-in image stitching functions.

The solution can be found in 'A2_Q5.ipynb'.

**Images of Home Buildings Used:** 
![Home Buildings](image_stitching/image-3.jpg)
![Home Buildings](image_stitching/image-2.jpg)
![Home Buildings](image_stitching/image-1.jpg)

**Home Buildings SIFT Stitching:** 
![SIFT Stitching](image_stitching/ORB1.jpg)

**Home Buildings ORB Stitching:** 
![ORB Stitching](image_stitching/ORB2.png)

**Home Buildings SIFT Stitching Panorama:** 
![Panorama](image_stitching/image_stiched.jpg)

___

## Question 6

We integrated the applications developed for questions 4 and 5 into a web application.

[Demo Video Link](https://youtu.be/LWzCbX0lU38)

**Home Page:** 
![Home Page](https://github.com/gkrishnasai16/Computer-Vision-Assignments/assets/39943509/2c554357-eb54-4630-add0-525cbc6cb467)

**Problem 4 Solution:** 
![Problem 4](https://github.com/gkrishnasai16/Computer-Vision-Assignments/assets/39943509/fc6f77e3-7ab0-49c0-92c3-7f0086579252)

**Problem 5 Solution:** 
![Problem 5](https://github.com/gkrishnasai16/Computer-Vision-Assignments/assets/39943509/d3aa8037-7526-4288-a675-f3c2e595bae7)
