"""
    Detects weight plates and their holes in an image, 
    drawing two bounding ellipses around each to outline both 
    the outer circumference and the inner hole.

"""
import os
import cv2
import numpy as np

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
    
    # Apply Canny edge detection
    t_lower = 50
    t_upper = 150

    canny = cv2.Canny(blur, 50, 150) 

    # ================ Contour Detection ================

    # Finding exactly two contours in the image (The plates' edge and hole)
    contours, hierarchy = cv2.findContours(canny, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    outer_contours = []
    inner_contours = []

    if hierarchy is not None:
        hierarchy = hierarchy[0]

        for i, contour_data in enumerate(zip(contours, hierarchy)):
            contour, hier = contour_data

            # No parent and has a child -> outer contour
            if hier[3] == -1 and hier[2] != -1:
                outer_contours.append((contour, i)) 
            # No child and has a parent -> inner contour
            elif hier[3] != -1 and hier[2] == -1:
                inner_contours.append(contour)

    final_ellipses = []

    for outer_contour, outer_idx in outer_contours:
        # Get the child index from the hierarchy
        child_idx = hierarchy[outer_idx][2]
        
        while child_idx != -1:
            inner_contour = contours[child_idx]
            
            # Check if the contours have enough points to make an ellipse
            if len(outer_contour) > 5 and len(inner_contour) > 5:
                outer_ellipse = cv2.fitEllipse(outer_contour)
                inner_ellipse = cv2.fitEllipse(inner_contour)

                # Check the distance between the centers of the ellipses 
                center_distance = np.linalg.norm(np.array(outer_ellipse[0]) - np.array(inner_ellipse[0]))

                if center_distance < 10: # Max distance between the centers
                    final_ellipses.append((outer_ellipse, inner_ellipse))
                    break  

            # Move to the next child contour
            child_idx = hierarchy[child_idx][0]

    # ================ Drawing Ellipses =================

    # Draw the ellipses on the image
    for outer_ellipse, inner_ellipse in final_ellipses:
        cv2.ellipse(image, outer_ellipse, (0, 255, 0), 2)
        cv2.ellipse(image, inner_ellipse, (0, 0, 255), 2)


    cv2.imshow("Processed Image", image)

    # Wait for a key press and close the window
    cv2.waitKey(0)
    cv2.destroyAllWindows()
