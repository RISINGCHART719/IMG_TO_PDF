# This file preprocesses the original ~1500 images in the kaggle dataset.
# There is another prepcossing method done by hand (separating lines and the guide-text
#   lines which only uses 200 of the images). The files for that process are in 
#   the "Util Files" folder.

import cv2
import numpy as np
from PIL import Image
import os
import json
import pytesseract
import time

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Function for extracting the top portion of the image using the pytesseract library
def extract_guide_text (image_array):
    image = Image.fromarray(image_array)
    text = pytesseract.image_to_string(image)
    return text

# Function for returning the y-level of a line (the one at the top, bottom, or middle)
def detect_line (image, position) :
    # Creating a kernel to use for close morphological operation
    morph_operation_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))

    # Converting image to grayscale (already done in crop_below_title_line)
    #gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Performing OPEN morphological operation on the image
    opened = cv2.morphologyEx(image, cv2.MORPH_OPEN, morph_operation_kernel)

    # Detecting the edges found
    edges = cv2.Canny(opened, 50, 150, apertureSize=3)

    # Detecting lines using Hough Transform (from the edges)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 90, threshold=2,
                            minLineLength=120, maxLineGap=3)

    y_level = 0
    if position == "top":
        #Starting from the bottom, and finding highest possible horizontal (y-length < 7) long line
        top_y = image.shape[0]
        for line in lines:
            x1, y1, x2, y2 = line[0]
            if abs(y1 - y2) < 7 :  # horizontal & long
                if y1 < top_y:
                    top_y = y1
        y_level = top_y
        
    elif position == "bottom":
        #Starting at the top, and finding the lowest (y-length < 7) long line
        bottom_y = 0
        for line in lines:
            x1, y1, x2, y2 = line[0]
            if  abs(y1 - y2) < 7:  # horizontal & long
                if y1 > bottom_y:
                    bottom_y = y1
        y_level = bottom_y
        
    else:
        #This is the middle case. Just run the same algorithm that we ram in the bottom case.
        middle_y = 0
        for line in lines:
            x1, y1, x2, y2 = line[0]
            if  abs(y1 - y2) < 7:  # horizontal & long
                if y1 > middle_y and y1 < (int(image.shape[0]/2)) and y1 > (int(image.shape[0] * .05)):
                    middle_y = y1
        y_level = middle_y

    return y_level

# down the road: I think we need to preprocess more (remove background table and enhance lines)
def process_image(image_path):
    # Loading image
    # These files are "temporary" because we would like to crop them.
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


    # Before detecting lines, crop away the bottom part of the image, because all of the images have -
    # - some sort a fold line that the models would detect as a line and mess up the separation
    # fatal bug happened: (12% fix for now)
    # Cropping the bottom 10% of the image
    num_pixels_to_be_cut = int(image.shape[0] * 0.88)
    image = image[:num_pixels_to_be_cut - 1, :]

    return image

def crop_below_title_line(image_path, output_guide_text_path=None, output_handwritten_image_path = None):
    image = process_image(image_path)

    top_line_y = detect_line(image, "top")
    bottom_line_y = detect_line(image, "bottom")


    # Cropping the image so that what is left is below the top-most long line, and above the bottom-most long line
    # This would make it so that what's left is only the handwriting and the guide image
    cropped_1 = image[top_line_y+1:, :]
    cropped_2 = cropped_1[:bottom_line_y - top_line_y - 10, :]

    # Detecting the middle line in the cropped image.
    middle_line_y = detect_line(cropped_2, "middle")

    if (top_line_y == 0 or bottom_line_y == 0 or middle_line_y == 0):
        print(f'Error in image:', os.path.basename(image_path))
        print(f'top line: {top_line_y}')
        print(f'bottom line: {bottom_line_y}')
        print(f'middle line: {middle_line_y}')



    # Separating the handwriting and the guide image based on the middle line y-level. After this,
    # we will have 2 new images that will be used in the rest of the segments after this segment.
    img_guide = cropped_2[:middle_line_y - 1, :]
    img_handwritten = cropped_2[middle_line_y+1:, :]

    # Turning the guide image to text
    guide_text = extract_guide_text(img_guide)

    #Storing the txt file
    if output_guide_text_path:
        output_guide_text_path = output_guide_text_path.replace('.png', '.txt')

    if output_guide_text_path:
        os.makedirs(os.path.dirname(output_guide_text_path), exist_ok=True)

    with open(output_guide_text_path, 'w', encoding='utf-8') as f:
        f.write(guide_text)

    # Storing the handwritten text image
    if output_handwritten_image_path:
        #print(output_handwritten_image_path)
        if img_handwritten.size > 0:
            cv2.imwrite(output_handwritten_image_path, img_handwritten)
        else:
            print("Handwritten image is empty, skipping save.")
    else:
        print("handwritten image not saved as no output path was provided for handwritten image.")
    # output path of changed filetype .txt
    return output_guide_text_path

# test bugs
def test_image(folder_path, filename, guide_output_dir, handwritten_output_dir):
    if not os.path.isdir(folder_path):
        print(f"Folder does not exist: {folder_path}")
        return

    image_path = os.path.join(folder_path, filename)
    if not os.path.exists(image_path):
        print(f"File not found: {image_path}")
        return

    label = f"{os.path.basename(folder_path)}_{filename}"

    output_guide_image_path = os.path.join(guide_output_dir, f"guide_text_{label}")
    output_handwritten_image_path = os.path.join(handwritten_output_dir, f"handwritten_{label}")

    print(f"Testing image: {image_path}")
    result = crop_below_title_line(image_path, output_guide_image_path, output_handwritten_image_path)

    print(f"Saved: {os.path.basename(output_guide_image_path)} & {os.path.basename(output_handwritten_image_path)}")
    return result

if __name__ == "__main__":

    # The location of the dataset will be stored in a .gitignored file
    with open("../Dataset_Location_specifier.json", "r") as file:
        address_specifier = json.load(file)

    input_image_path = '' 
    input_image_folder = address_specifier["Dataset Address"]
    guide_text_output_folder = address_specifier["Guide Text Store Address"]
    handwritten_image_output_folder = address_specifier["Handwritten Text Image Address"]

    # fatal crash here (problem with line detection) [changed cropping of page from 10 -> 12]
    #test_image("../../data/149", "c02-089.png", "../../guide_text", "../../handwritten_text")
    #exit(0)

    # track how long this process takes
    start_time = time.time()

    # iterate through each folder in our dataset
    for folder in os.listdir(input_image_folder):
        folder_path = os.path.join(input_image_folder, folder)
        # Processing all images in the input folder
        print("PREPROCESSING FOLDER: ", folder)
        image_counter = 1
        for file in os.listdir(folder_path):

            # we can if statement: safety check not necessary (all images are .png)
            #if file.lower().endswith('.png'):
                # obtain image path and status of remaining images that to be processed in folder
                input_image_path = os.path.join(folder_path, file)
                #print(f'Image: {image_counter} of {len(os.listdir(folder_path))}:',os.path.basename(input_image_path))
                image_counter += 1

                # label with folder name and name file name
                label = f"{folder}_{file}"
                output_guide_image_path = os.path.join(guide_text_output_folder, f"guide_text_{label}")
                output_handwritten_image_path = os.path.join(handwritten_image_output_folder, f"handwritten_{label}")
                # revised so it returns updated path name of the .txt conversion
                output_guide_image_path = crop_below_title_line(input_image_path, output_guide_image_path, output_handwritten_image_path)
                #print(f"Processed and saved: {os.path.basename(output_guide_image_path)} & {os.path.basename(output_handwritten_image_path)}\n")

    end_time = time.time()
    elapsed_time = end_time - start_time
    # before: 1113.9 seconds
    # after: 853.04 seconds
    print(f"\nCompleted preprocessing in {elapsed_time:.2f} seconds.")
