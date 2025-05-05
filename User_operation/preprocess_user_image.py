import cv2
import numpy as np

def correct_skew(image):
    # Edges were detected using Canny process
    edges = cv2.Canny(image, 50, 150, apertureSize=3)

    # we used the HoughLines for detecting straight lines
    lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)

    # collecting all angels that are roughly vertical then picking median
    angles = []
    if lines is not None:
        for line in lines:
            rho, theta = line[0]
            angle = (theta * 180 / np.pi) - 90
            if -45 < angle < 45:
                angles.append(angle)
        median_angle = np.median(angles)
    else:
        median_angle = 0

    # Applying the image dimension and median_angle to correct the skews
    (h, w) = image.shape
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, median_angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return rotated

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

    # this function is improving the models recognition
    skew_corrected = correct_skew(thresh)

    # Morphological operations to clean small noise
    kernel = np.ones((2, 2), np.uint8)
    cleaned = cv2.morphologyEx(skew_corrected, cv2.MORPH_OPEN, kernel)

    # enabling small images by resizing them
    height = cleaned.shape[0]
    if height < 800:
        scale = 800 / height
        cleaned = cv2.resize(cleaned, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)
    return cleaned
