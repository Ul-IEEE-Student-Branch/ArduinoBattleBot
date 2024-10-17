"""
    Detects weight plates and their holes in an image, 
    drawing two bounding ellipses around each to outline both 
    the outer circumference and the inner hole.

"""

# ================ Helper Functions =================

def calculate_aspect_ratio(ellipse):
    _, (major_axis, minor_axis), _ = ellipse
    return minor_axis / major_axis

def average_radius(ellipse):
                (_, axes, _) = ellipse
                major_axis = axes[0] / 2
                minor_axis = axes[1] / 2
                return (major_axis + minor_axis) / 2

# ================ Main Script ======================

import os
import cv2
import numpy as np
import math

images_folder = "RoboVision/images"
image_files = os.listdir(images_folder)

# Loop over all the images
for image_file in image_files:
    image_path = os.path.join(images_folder, image_file)

    # ================ Image Preprocessing ==============

    # Read the image
    image = cv2.imread(image_path)
    grey_scale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(grey_scale, (5, 5), 0)

    # ================ Edge Detection ===================
    
    # Median of the single-channel pixel intensities
    v = np.median(blur)

    # Apply automatic Canny edge detection using the computed median
    sigma = 0.3
    lower = int(max(0, (1.0 - sigma) * v))
    upper = int(min(255, (1.0 + sigma) * v))
    canny = cv2.Canny(blur, lower, upper)


    # ================ Contour Detection ================

    # Finding exactly two contours in the image (The plates' edge and hole)
    contours, hierarchy = cv2.findContours(canny, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Constants for filtering
    EXPECTED_RATIO = 0.111 
    RATIO_TOLERANCE = 0.1
    MAX_CENTER_DISTANCE = 0.2
    ASPECT_RATIO_THRESHOLD = 0.3

    final_ellipses = []

    if hierarchy is not None:
        hierarchy = hierarchy[0]

        # Iterate through contours and hierarchy
        for i, (contour, hier) in enumerate(zip(contours, hierarchy)):
            # Check if the contour has a child (potential outer contour)
            if hier[2] == -1:
                # Skip the contours that don't have a child
                continue

            outer_contour = contour
            outer_idx = i

            # Get the child index from the hierarchy
            child_idx = hier[2]

            while child_idx != -1:
                inner_contour = contours[child_idx]

                # Check if the contours have enough points to fit an ellipse
                if len(outer_contour) <= 5 and len(inner_contour) <= 5:
                    # If they can't form an ellipse, move on 
                    break

                outer_ellipse = cv2.fitEllipse(outer_contour)
                inner_ellipse = cv2.fitEllipse(inner_contour)

                inner_aspect_ratio = calculate_aspect_ratio(inner_ellipse)

                # Check if the inner ellipse is elliptical enough
                if inner_aspect_ratio <= ASPECT_RATIO_THRESHOLD:
                    # If the aspect ratio is too small, move on
                    break

                # Calculate the average radii of the ellipses
                outer_radius = average_radius(outer_ellipse)
                inner_radius = average_radius(inner_ellipse)
                radius_ratio = inner_radius / outer_radius

                # Check if the radius ratio is within the expected tolerance
                if abs(radius_ratio - EXPECTED_RATIO) <= RATIO_TOLERANCE:

                    # Calculate the distance between the centers of the ellipses 
                    center_distance = np.linalg.norm(
                        np.array(outer_ellipse[0]) - np.array(inner_ellipse[0])
                    )
                    max_center_distance = MAX_CENTER_DISTANCE * outer_radius

                    if center_distance <= max_center_distance:
                            # Ellipses match the profile of a weight plate!
                            final_ellipses.append((outer_ellipse, inner_ellipse))
                            break 
                        
                # Move to the next child contour
                child_idx = hierarchy[child_idx][0]

            # If a valid pair has been found, no need to continue processing
            if final_ellipses:
                break

    # ================ Drawing Ellipses =================

    # Draw the ellipses on the image
    for outer_ellipse, inner_ellipse in final_ellipses:
        cv2.ellipse(image, outer_ellipse, (0, 255, 0), 2)
        cv2.ellipse(image, inner_ellipse, (0, 0, 255), 2)


    cv2.imshow("Processed Image", image)

    # Wait for a key press and close the window
    cv2.waitKey(0)
    cv2.destroyAllWindows()
