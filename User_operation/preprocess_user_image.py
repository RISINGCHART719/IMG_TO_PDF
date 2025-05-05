import cv2
import numpy as np

def preprocess_image_for_ocr(input_path):

    # If the image is not found then outputs an error and exits the program
    image = cv2.imread(input_path)
    if image is None:
        print(f'Error: {input_path} is not a valid image.')
        exit(-1)

    # Converting image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Denoising image
    denoised = cv2.medianBlur(gray, 3)

    # Contrast enhancement using CLAHE
    # this uses an Adaptive Histogram Equalization to remove noise
    # added for removing instances of uneven lighting
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    contrast_enhanced = clahe.apply(denoised)

    # applying Ostu and inverting image color
    _, thresh = cv2.threshold(
    contrast_enhanced,
    0,
    255,
    cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )

    # Morphological operations to clean small noise
    kernel = np.ones((2, 2), np.uint8)
    cleaned = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

    # enabling small images by resizing them
    height = cleaned.shape[0]
    if height < 800:
        scale = 800 / height
        cleaned = cv2.resize(cleaned, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)
    return cleaned
