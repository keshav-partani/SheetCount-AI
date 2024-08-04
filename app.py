import streamlit as st
import cv2
import numpy as np
import math
from PIL import Image

# Function to process the image and count horizontal lines
def count_horizontal_lines(image_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    for _ in range(2):
        gray = cv2.GaussianBlur(image, (3, 3), cv2.BORDER_DEFAULT)
    gray = cv2.Canny(gray, 100, 200)

    img = np.zeros(gray.shape)
    lines = cv2.HoughLinesP(gray.copy(), 1, np.pi/180, 100, minLineLength=300, maxLineGap=100)
    horizontal_lines = []

    if lines is not None:
        for x1, y1, x2, y2 in lines.reshape(-1, 4):
            if x2 == x1:
                continue
            slope = (y2 - y1) / (x2 - x1)
            slope_degree = math.degrees(math.atan(abs(slope)))
            if slope_degree < 10:
                horizontal_lines.append([x1, y1, x2, y2])
                cv2.line(img, (x1, y1), (x2, y2), (255, 255, 255), 2)

        for i in range(0, len(horizontal_lines)):
            if horizontal_lines[i][1] > horizontal_lines[i][3]:
                temp = horizontal_lines[i][1]
                horizontal_lines[i][1] = horizontal_lines[i][3]
                horizontal_lines[i][3] = temp

        horizontal_lines_sorted = sorted(horizontal_lines, key=lambda x: x[1])

        differences = []

        # Calculate differences between consecutive second elements
        for i in range(len(horizontal_lines_sorted) - 1):
            differences.append(horizontal_lines_sorted[i][3] - horizontal_lines_sorted[i][1])

        gap = np.median(differences)

        start = 0
        arr = []

        for i in horizontal_lines_sorted:
            if start < i[1]:
                start = i[1] + 10
                arr.append(i)

        return len(arr)
    else:
        return 0

# Streamlit app
st.title('Sheet Counter')

uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Convert the uploaded file to an OpenCV image
    image = Image.open(uploaded_file)
    image = np.array(image)
    image_path = "temp_image.jpg"
    cv2.imwrite(image_path, cv2.cvtColor(image, cv2.COLOR_RGB2BGR))

    # Process the image and count the horizontal lines
    num_sheets = count_horizontal_lines(image_path)

    st.image(image, width=100, caption='Uploaded Image')
    st.write(f"Number of sheets detected: {num_sheets}")