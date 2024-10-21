# ================ Helper Functions =================

def calculate_aspect_ratio(ellipse):
    _, (major_axis, minor_axis), _ = ellipse
    if major_axis == 0:
        return 0
    return minor_axis / major_axis

def average_radius(ellipse):
    (_, axes, _) = ellipse
    major_axis = axes[0] / 2
    minor_axis = axes[1] / 2
    return (major_axis + minor_axis) / 2

# ================ Main Script ======================

import cv2
import numpy as np

# Open the camera feed (0 for the default camera)
camera_feed = cv2.VideoCapture(1, cv2.CAP_DSHOW)
camera_feed.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  
camera_feed.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
camera_feed.set(cv2.CAP_PROP_FPS, 10)

# Constants for filtering
MAXIMUM_RATIO = 0.7
MINIMUM_RATIO = 0.085
MAX_CENTER_DISTANCE = 0.2
ASPECT_RATIO_THRESHOLD = 0.3

# Continuously capture frames from the camera feed
while camera_feed.isOpened():
    ret, frame = camera_feed.read()
    
    if not ret:
        print("Failed to capture image")
        break
    
    # ================ Image Preprocessing ==============

    grey_scale = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(grey_scale, (5, 5), 0)

    # ================ Edge Detection ===================
    
    # Median of the single-channel pixel intensities
    v = np.median(blur)

    # Apply automatic Canny edge detection using the computed median
    sigma = 0.9
    lower = int(max(0, (1.0 - sigma) * v))
    upper = int(min(255, (1.0 + sigma) * v))
    canny = cv2.Canny(blur, lower, upper)

    # Show canny edges
    cv2.imshow("Canny", canny)

    # ================ Contour Detection ================

    contours, hierarchy = cv2.findContours(canny, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    final_ellipses = []

    if hierarchy is not None:
        hierarchy = hierarchy[0]

        # Iterate through contours and hierarchy
        for i, (contour, hier) in enumerate(zip(contours, hierarchy)):
            # Check if the contour has a child (potential outer contour)
            if hier[2] == -1:
                continue

            outer_contour = contour

            # Get the child index from the hierarchy
            child_idx = hier[2]

            while child_idx != -1:
                inner_contour = contours[child_idx]

                # Check if the contours have enough points to fit an ellipse
                if len(outer_contour) <= 5 or len(inner_contour) <= 5:
                    child_idx = hierarchy[child_idx][0]  # Move to next child
                    continue

                outer_ellipse = cv2.fitEllipse(outer_contour)
                inner_ellipse = cv2.fitEllipse(inner_contour)

                inner_aspect_ratio = calculate_aspect_ratio(inner_ellipse)

                if inner_aspect_ratio <= ASPECT_RATIO_THRESHOLD:
                    child_idx = hierarchy[child_idx][0]  # Move to next child
                    continue

                outer_radius = average_radius(outer_ellipse)
                inner_radius = average_radius(inner_ellipse)
                radius_ratio = inner_radius / outer_radius


                if radius_ratio < MAXIMUM_RATIO and radius_ratio > MINIMUM_RATIO:
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

            # If a valid pair has been found, stop looking for more
            if final_ellipses:
                break

    # ================ Drawing Ellipses =================

    # Ensure that both outer and inner ellipses are detected before drawing
    if final_ellipses:
        for outer_ellipse, inner_ellipse in final_ellipses:
            # Draw outer ellipse in green
            cv2.ellipse(frame, outer_ellipse, (0, 255, 0), 2)
            # Draw inner ellipse in red
            cv2.ellipse(frame, inner_ellipse, (0, 0, 255), 2)

    # Show the processed frame with the ellipses
    cv2.imshow("Processed Camera Feed", frame)

    # Press 'q' to exit the loop
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera feed and close windows
camera_feed.release()
cv2.destroyAllWindows()
