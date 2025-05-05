# This file allows the user to open a document image that has multiple lines, and
# separate its different lines into their own images. 
# Near the end, it shows the use a vertically stacked collage of the images so that
# the user can then go ahead and edit the corresponding text file to the image so that
# the lining in the text file matches the line images.

import cv2
import os
import numpy as np
from tkinter import Tk, filedialog


# Function that resizes the selected image such that
# it's easier to crop it. Aspect ratio is maintained.
def resize_to_fit(img, max_width=1200, max_height=800):
    image_height, image_width = img.shape[:2]
    scale = min(max_width / image_width, max_height / image_height, 1.0)
    new_width, new_height = int(image_width * scale), int(image_height * scale)
    resized_image = cv2.resize(img, (new_width, new_height))
    return resized_image, scale

# Function for stacking the resulting cropped images on top of each other 
# so that we can match the corresponding guide text's new lines and other 
# changes with what we see in the stacked line images.
def stack_vertically_with_labels(images, specified_width=800, pad=10, sep_color=(64, 0, 128), text_color=(0, 100, 0)):
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.6
    font_thickness = 1
    sep_height = 2

    resized_images = []
    total_height = pad

    # Resizing the images
    for image_index, img in enumerate(images):
        # Different rescaling than resize_to_fit()
        image_height, image_width = img.shape[:2]
        scale = specified_width / image_width
        new_width, new_height = int(image_width * scale), int(image_height * scale)
        resized = cv2.resize(img, (new_width, new_height))

        # Label is the index of the image (for better line indexing when the guide text file is open in an IDE or text-editor)
        label = f"{image_index + 1}"
        text_x = 5
        text_y = new_height - 5
        cv2.putText(resized, label, (text_x, text_y), font, font_scale, text_color, font_thickness, cv2.LINE_AA)

        resized_images.append(resized)
        total_height += new_height + sep_height + pad

    # Stacking the resized images on top of each other
    stacked_img = np.full((total_height, specified_width, 3), 255, dtype=np.uint8) 
    y_offset = pad
    for resized_image in resized_images:
        h = resized_image.shape[0]
        stacked_img[y_offset:y_offset + h, :resized_image.shape[1]] = resized_image
        y_offset += h
        # Drawing separator lines between the images to make it easier to separate them
        cv2.line(stacked_img, (0, y_offset), (specified_width, y_offset), sep_color, thickness=sep_height)
        y_offset += sep_height + pad

    return stacked_img




# The default path that opens up when the prompt for selecting the picture appears
script_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/data_100(bottom)_images/")


# Hide the main tkinter window
Tk().withdraw()

# Opening file selection dialog (default value is controled by scrpit_dir)
image_path = filedialog.askopenfilename(
    title="Select an image",
    initialdir=script_dir,
    filetypes=[("Image files", "*.png")]
)

if not image_path:
    print("No image selected. Exiting.")
    exit()

img = cv2.imread(image_path)
if img is None:
    print(f"Error: Cannot open {image_path}. Please select a correct image file.")
    exit()

# Resizing the image so that it's easier to select lines
resized_img, scale = resize_to_fit(img)

# Getting the regions of interest from the user. These will be used to designate a line of text
rois = cv2.selectROIs("Select lines (Enter or Space = Done, ESC = Cancel)", resized_img, False, False)

# If the user specified no regions of interest, we can interpret that as the user wanting to exit the process
if rois is None or len(rois) == 0:
    print("No selections made. Aborting.")
    cv2.destroyAllWindows()
    exit()

# Cropping selected regions of interest
cropped_images = []
for roi in rois:
    x_size, y_size, width,  height = [int(c / scale) for c in roi]
    cropped = img[y_size:y_size+ height, x_size:x_size+width]
    cropped_images.append(cropped)

# Showing vertical preview with labels
# This is necessary because at this stage, we can match the lines in the guid text with
# what we see in the preview.
preview_lines_stacked = stack_vertically_with_labels(
    cropped_images,
    specified_width=800,
    pad=15,
    sep_color=(64, 0, 128),
    text_color=(0, 100, 0)
)
cv2.imshow("Cropped Lines Preview", preview_lines_stacked)
cv2.waitKey(0)
cv2.destroyAllWindows()

# Saving cropped images (images of the lines)
output_root = './data/line_crops_round2'
image_name = os.path.splitext(os.path.basename(image_path))[0]
save_dir = os.path.join(output_root, image_name)
os.makedirs(save_dir, exist_ok=True)

for crop_index, crop in enumerate(cropped_images):
    save_path = os.path.join(save_dir, f"line_{crop_index}.jpg")
    cv2.imwrite(save_path, crop)
    print(f"Saved: {save_path}")
