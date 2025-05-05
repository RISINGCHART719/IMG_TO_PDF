from preprocess_user_image import preprocess_image_for_ocr
from Detect_and_recognize import detect_and_recognize_words_with_positions
import matplotlib.pyplot as plt
import cv2
import numpy as np
import json
import fitz
import os

# This function combines the detected lines in such a way that
# they are organized by their x values, and combined based on their y_value 
def combine_lines(detection, threshold):
    if not detection:
        return detection

    y_grouped_lines = []
    
    # Grouping lines by similar y-position (based on the threshold value in the argument list)
    for line in detection:
        line_matched_group = False
        for group in y_grouped_lines:
            # Checking if current line matches any line in the group 
            # (similar y position within the specified threshold)
            if abs(line[0][0][1] - group[0][0][0][1]) < threshold:
                group.append(line)
                line_matched_group = True
                break
        # Creating a new group with line in it if line didn't fit to any other group
        if not line_matched_group:
            y_grouped_lines.append([line])  

    # Merging lines in each group. We don't have to worry about 
    merged_lines = []
    for group in y_grouped_lines:

        if len(group) == 1:
            merged_lines.append(group[0])
            continue
            
        # Sorting based on x_level of each line, since we want the words to appear sequentially
        group.sort(key=lambda line: line[0][0][0])
        
        # Merging all lines in the group
        merged_text = " ".join([line[1][0] for line in group])
        x_min = min(line[0][0][0] for line in group)
        y_min = min(line[0][0][1] for line in group)
        x_max = max(line[0][2][0] for line in group)
        y_max = max(line[0][2][1] for line in group)
        confidence = min(line[1][1] for line in group)
        
        # merged_line will have the same structure as "detection"
        # so that we can assign it to detection outside of the function.
        merged_line = [
            [[x_min, y_min], [x_max, y_min], [x_max, y_max], [x_min, y_max]],
            [merged_text, confidence]
        ]
        merged_lines.append(merged_line)

    return merged_lines


# Debug function to help with visualizing the process
def draw_detections_on_image(input_path, result):
    original_image = cv2.imread(input_path)
    original_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)
    for detection in result:
        if detection:
            for line in detection:
                box = line[0]
                text = line[1][0]
                x_min, y_min, x_max, y_max = box
                points = [(x_min, y_min), (x_max, y_min), (x_max, y_max), (x_min, y_max)]
                points = np.array(points, np.int32).reshape((-1, 1, 2))
                cv2.polylines(original_image, [points], isClosed=True, color=(0, 255, 0), thickness=2)
                cv2.putText(original_image, text, (int(x_min[0]), int(y_min[1])), cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=(255, 0, 0), thickness=1)
    return original_image


# This function determines if a text fits within its text-box. 
# It has some estimates in this process, so it's not always 100% accurate.
def text_fits(text, rect, fontsize=11, fontname="helv"):
    text_width = fitz.get_text_length(text, fontname=fontname, fontsize=fontsize) * 1.5
    text_height = fontsize * 1.5
    return text_width <= rect.width and text_height <= rect.height


# Addressing
def make_pdf(input_image_path, inter_dir):

    # # #*************&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
    base_image_name = os.path.splitext(os.path.basename(input_image_path))[0]
    int_file_path = os.path.join(inter_dir, base_image_name)

    json_output_path = f'{int_file_path}.json'
    int_file_path = f'{int_file_path}.jpg'

    image = preprocess_image_for_ocr(input_image_path)
    plt.imsave(int_file_path, image, cmap='gray')
    print(f'Intermediary image saved in: {int_file_path}')
    result = list(detect_and_recognize_words_with_positions(int_file_path))

    # Save the result to a JSON file
    with open(json_output_path, 'w') as json_file:
        json.dump(result, json_file, indent=4)
    print(f"Detected text saved to JSON file at: {json_output_path}")
    # #*************&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&

    # Creating new pdf document using Pymupdf (fitz)
    pdf_document = fitz.open()

    with open(json_output_path, 'r') as json_file:
        result = json.load(json_file)

    # Calculating what dimensions the page within the pdf document should have.
    max_x = 0
    max_y = 0
    for detection in result:
        if detection:
            for line in detection:
                box = line[0]  # Bounding box coordinates
                x_min, y_min, x_max, y_max = box
                max_x = max(max_x, x_max[0])
                max_y = max(max_y, y_max[1])
    padding = 50
    image_width = max_x + padding
    image_height = max_y + padding


    # Giving order to the lines and combining lines that are roughly on the same horizaontal line
    for i in range(len(result)):
        result[i] = combine_lines(result[i], threshold=40)

    # Creatoing a new page in the PDF
    page = pdf_document.new_page(width=image_width, height=image_height) 


    # Determining the font size to use for all of the text
    font_sizes = []
    for detection in result:
        if detection:
            for line in detection:
                box = line[0]
                x_min, y_min, x_max, y_max = box
                rect = fitz.Rect(x_min[0], y_min[1], x_max[0], y_max[1])
                rect_height = rect.x1 - rect.x0
                font_sizes.append(rect.height / 1.8)  # Adjust font size to fit the text within the rectangle

    if font_sizes:
        font_size = int(sum(font_sizes) / len(font_sizes))
    else:
        font_size = 45
        

    # Drawing the lines on the pdf page.
    for detection in result:

        for line in detection:
            box = line[0]
            # Debug: Drawing the bounding box on the PDF
            #rect = fitz.Rect(box[0][0], box[1][1], box[2][0], box[3][1])
            #page.draw_rect(rect, color=(1, 0, 0), width=0.5)
            text = line[1][0] 
            x_min, y_min, x_max, y_max = box
            rect = fitz.Rect(x_min[0], y_min[1], x_max[0], y_max[1])
            rect_height = rect.x1 - rect.x0
            specific_font_size = int(rect.height / 1.3)

            # if specific_font_size is more than font_size/3 points away from font_size (which is the average font_size,
            # it means that it is probably a head or smaller written text)
            if abs(specific_font_size - font_size) < int(font_size/3):
                specific_font_size = font_size

            

            # Converting coordinates to PDF points. We make the rect a little bigger than before
            # So that the text can show up properly.
            rect = fitz.Rect(x_min[0] - int(font_size/3), y_min[1] - int(font_size/3), x_max[0] + int(font_size/3), y_max[1] + int(font_size/3))
            # Ensuring the rectangle sides are at least 5 units (otherwise the text would not show)
            if rect.width <= 5:
                rect.x1 = rect.x0 + 5
            if rect.height <= 5:
                rect.y1 = rect.y0 + 5

            # Adjusing the font with the new rect so that the text fits within the rectangle.
            while( not text_fits(text, rect,  specific_font_size, 'helv') ):
                specific_font_size -= 1
            
            # Adding the text with all of the obtained attributes
            page.insert_textbox(rect, text, fontsize=specific_font_size, color=(0, 0, 0), fontname = 'helv')


    #Returning the created page back to the caller
    return pdf_document
