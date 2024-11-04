import cv2
import re
import pytesseract

# Image processing and text extraction
def load_rectangle_data_from_file(file_path):
    rectangle_data = []
    with open(file_path, 'r') as file:
        for line in file:
            match = re.search(r'Center: \((\d+), (\d+)\), Width: (\d+), Height: (\d+)', line)
            if match:
                center_x = int(match.group(1))
                center_y = int(match.group(2))
                width = int(match.group(3))
                height = int(match.group(4))
                rectangle_data.append({'Center_X': center_x, 'Center_Y': center_y, 'Width': width, 'Height': height})
    return rectangle_data

def extract_text_from_rectangles(rectangle_data, new_image_path):
    new_image = cv2.imread(new_image_path)
    if new_image is None:
        print("Error: Could not load the image.")
        return [], []

    text_results, positions = [], []
    for rect in rectangle_data:
        x = max(0, rect['Center_X'] - rect['Width'] // 2)
        y = max(0, rect['Center_Y'] - rect['Height'] // 2)
        x_end = min(x + rect['Width'], new_image.shape[1])
        y_end = min(y + rect['Height'], new_image.shape[0])
        cropped_region = new_image[y:y_end, x:x_end]
        text = pytesseract.image_to_string(cropped_region).strip()
        text_results.append(text)
        positions.append((rect['Center_X'], rect['Center_Y']))
    return text_results, positions

def recruit_ocr(rectangle_data_file, new_image_path):
    # Load rectangle data
    rectangle_data = load_rectangle_data_from_file(rectangle_data_file)
    # Extract text from rectangles in the screenshot
    text_results, positions = extract_text_from_rectangles(rectangle_data, new_image_path)
    return text_results, positions

