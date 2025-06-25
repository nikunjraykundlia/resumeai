import logging
import os
import re
from PIL import Image
import numpy as np

# Import OpenCV and pytesseract with error handling
try:
    import cv2
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    logging.error("OpenCV or pytesseract not available. OCR functionality will be limited.")
    OCR_AVAILABLE = False

# Configure tesseract path if needed (uncomment and set if not in PATH)
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def process_image_resume(image_path):
    """Process an image of a resume using OCR and return extracted text"""
    if not OCR_AVAILABLE:
        logging.warning("OCR functionality is not available. Please upload a PDF file instead.")
        return "OCR functionality is not available. Please upload a PDF file instead."
        
    try:
        # Read the image
        img = cv2.imread(image_path)
        
        if img is None:
            logging.error(f"Failed to read image: {image_path}")
            return "Error: Could not read the image file."
        
        # Preprocess the image
        img = preprocess_image(img)
        
        # Perform OCR
        text = pytesseract.image_to_string(img)
        
        # Post-process the text
        text = post_process_text(text)
        
        return text
        
    except Exception as e:
        logging.error(f"Error in OCR processing: {str(e)}")
        return "Error processing the resume image. Please try uploading a clearer image or a PDF file."

def preprocess_image(img):
    """Preprocess the image to improve OCR accuracy"""
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply slight Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Apply adaptive thresholding
    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                  cv2.THRESH_BINARY, 11, 2)
    
    # Denoise
    denoised = cv2.fastNlMeansDenoising(thresh, None, 10, 7, 21)
    
    return denoised

def post_process_text(text):
    """Clean up the extracted text"""
    # Remove excessive newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Fix common OCR errors
    text = re.sub(r'l\b', '1', text)  # lowercase l at word end often mistaken for 1
    text = re.sub(r'\bI\b', '1', text)  # capital I often mistaken for 1
    text = re.sub(r'O', '0', text)  # capital O often mistaken for 0
    
    return text

def extract_text_with_layout(image_path):
    """Extract text while attempting to preserve layout"""
    if not OCR_AVAILABLE:
        logging.warning("OCR functionality is not available. Please upload a PDF file instead.")
        return "OCR functionality is not available. Please upload a PDF file instead."
        
    try:
        # Use Tesseract with specific parameters to preserve layout
        custom_config = r'--oem 3 --psm 6'
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img, config=custom_config)
        return text
    except Exception as e:
        logging.error(f"Error in layout-preserving OCR: {str(e)}")
        # Fall back to regular processing
        return process_image_resume(image_path)
