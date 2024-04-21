# CSc 8830: Computer Vision : Assignment 2 Solutions

## Question 1

The solution can be found in the the file 'A2_Q1.ipynb'

The code prompts the user to take a 10 seconds video. The video frames are stored in the folder "video_frames".

A random image was chosen from the video frames to perform CANNY EDGE DETECTION and stored in canny_edge_detection.png.

<img src="canny_edge_detection.png" alt="Canny Edge Detection">

___

## Question 2

Similar to Question 1, The Harris corner detection algorithm was manually applied to a 5x5 image patch within a selected region containing a corner of interest. 

The detected corner pixels were noted and compared with automated implementations using DepthAI's Harris corner detection function for a comprehensive analysis.

The solution can be found in the the file 'A2_Q2.ipynb'

<img src="harris_corner_detection.png" alt="Canny Edge Detection">

___

## Question 3

The SIFT feature extraction and matching algorithm was implemented to compute the sum of squared differences (SSD) between corresponding super-pixel patches in two images from the 'video_frames' separated by at least 2 seconds with some scene overlap.

The Homography matrix was also computed between these images, along with its inverse, using Python implementation.

The solution can be found in the the file 'A2_Q3.ipynb'

<img src="homography.png" alt="Canny Edge Detection">

___

## Question 4

The code computes and displays the integral image feed alongside the RGB feed without relying on built-in functions such as "output = integral_image(input)".

The solution can be found in the the file 'A2_Q4.ipynb'

The implementation initializes the integral image to zero, copies pixel values from the grayscale image, and calculates the integral image using the integral image algorithm.

### Integral Image Matrix
[Integral Image Matrix File](integral_matrix.txt)


### Integral Image Display for image.jpg
<img src="integral_image_display.png" alt="integral_image">

___

## Question 5

The image stitching functionality for creating a 360-degree panoramic output in real-time was successfully implemented, utilizing SIFT or ORB features. 

The implementation involved constructing panoramas from images of home and science buildings without utilizing built-in functions directly performing image stitching.

The solution can be found in the the file 'A2_Q5.ipynb'



Below are the images of Home Buildings used: 
<table>
  <tr>
    <td><img src="image_stitching/image-3.jpg" alt="Image 3"></td>
    <td><img src="image_stitching/image-2.jpg" alt="Image 2"></td>
    <td><img src="image_stitching/image-1.jpg" alt="Image 1"></td>
  </tr>
</table>

### Home Buildings SIFT Stitching : 

<img src="image_stitching/ORB1.jpg" alt="ORB1.png">

### Home Buildings ORB Stitching, other buildings : 

<img src="image_stitching/ORB2.jpg" alt="ORB2.png">

### Home Buildings SIFT Stitching : Panaroma : 

<img src="image_stitching/image_stiched.jpg" alt="image_stiched.jpg">


___

## Question 6

Integrated the applications developed for problems 4 and 5 with the web application.

[Demo Video Link](https://youtu.be/LWzCbX0lU38)

## Home Page : 

![image](https://github.com/gkrishnasai16/Computer-Vision-Assignments/assets/39943509/2c554357-eb54-4630-add0-525cbc6cb467")


# Problem 4 Solution : 
![image]("https://github.com/gkrishnasai16/Computer-Vision-Assignments/assets/39943509/fc6f77e3-7ab0-49c0-92c3-7f0086579252")


# Problem 5 Solution : 
![image]("https://github.com/gkrishnasai16/Computer-Vision-Assignments/assets/39943509/d3aa8037-7526-4288-a675-f3c2e595bae7")
