import cv2
import numpy as np
import pandas as pd
import os

def find_largest_green_rectangles(image_path, output_file, rectnum):
    # Load the image
    image = cv2.imread(image_path)
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    # Define range for green color in HSV
    lower_green = np.array([35, 100, 100])
    upper_green = np.array([85, 255, 255])
    
    # Create mask to detect green areas
    mask = cv2.inRange(hsv_image, lower_green, upper_green)
    
    # Find contours of green rectangles
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # List to store rectangle data
    rectangles_data = []
    
    for cnt in contours:
        # Get bounding rectangle of contour
        x, y, w, h = cv2.boundingRect(cnt)
        
        # Calculate the center of the rectangle
        center_x = x + w // 2
        center_y = y + h // 2
        
        # Save rectangle data including area for sorting
        area = w * h
        rectangles_data.append({'Center_X': center_x, 'Center_Y': center_y, 'Width': w, 'Height': h, 'Area': area})
    
    # Sort rectangles by area and keep the 6 largest
    rectangles_data = sorted(rectangles_data, key=lambda x: x['Area'], reverse=True)[:rectnum]
    
    # Draw the largest rectangles and centers on the image for visualization
    for rect in rectangles_data:
        x, y, w, h = rect['Center_X'] - rect['Width'] // 2, rect['Center_Y'] - rect['Height'] // 2, rect['Width'], rect['Height']
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.circle(image, (rect['Center_X'], rect['Center_Y']), 5, (0, 0, 255), -1)
    
    # Save rectangle data to a text file
    with open(output_file, 'w') as file:
        for rect in rectangles_data:
            file.write(f"Center: ({rect['Center_X']}, {rect['Center_Y']}), Width: {rect['Width']}, Height: {rect['Height']}\n")
    
    # Display the result
    cv2.imshow('Detected Rectangles', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    return rectangles_data

# Example usage
image_path = 'tagbuttons.png'  # Replace with your screenshot path
output_file = 'tagbuttons.txt'  # Replace with your desired output file name
rectnum = 5
rectangles = find_largest_green_rectangles(image_path, output_file, rectnum)
print(f"Detected rectangles saved to {output_file}")
