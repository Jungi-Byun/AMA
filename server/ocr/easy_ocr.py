#---------------------------------------------------------
# EasyOCR, PaddleOCR 관련 함수 및 OCR 리더 초기화
#---------------------------------------------------------

import easyocr
import cv2
import requests
import numpy as np
import matplotlib.pyplot as plt
from paddleocr import PaddleOCR
from paddle_ocr import OptimizedOCRSystem

# EasyOCR 리더 초기화
def get_easyocr_reader():
    return easyocr.Reader(['ko', 'en'], gpu=True)

# EasyOCR 함수
def EasyOCR_from_file(file_path=None, url=None, show_image=False, reader=None):
    if reader is None:
        reader = get_easyocr_reader()
    if file_path:
        img = cv2.imread(file_path)
    elif url:
        response  = requests.get(url)
        img = np.asarray(bytearray(response.content), dtype="uint8")
        img = cv2.imdecode(img, cv2.IMREAD_COLOR)
    else:
        raise ValueError("Either file_path or url must be provided.")
    img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    _, binary = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    results = reader.readtext(binary)
    if show_image:
        plt.figure(figsize=(8, 6))
        plt.imshow(binary, cmap='gray')
        plt.axis('off')
        plt.show()
    return results, binary

# PaddleOCR 인스턴스 생성 함수
def get_paddleocr_instance():
    return OptimizedOCRSystem()

# PaddleOCR 함수
def PaddleOCR_from_file(file_path=None, url=None, show_image=False, ocr=None):
    if ocr is None:
        ocr = get_paddleocr_instance()
    if file_path:
        img = cv2.imread(file_path)
    elif url:
        response = requests.get(url)
        img = np.asarray(bytearray(response.content), dtype="uint8")
        img = cv2.imdecode(img, cv2.IMREAD_COLOR)
    else:
        raise ValueError("Either file_path or url must be provided.")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    denoised = cv2.fastNlMeansDenoising(gray)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(denoised)
    _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    padding = 30
    padded_binary = cv2.copyMakeBorder(binary, padding, padding, padding, padding, cv2.BORDER_CONSTANT, value=255)
    color_binary = cv2.cvtColor(padded_binary, cv2.COLOR_GRAY2BGR)
    result = ocr.predict(color_binary)
    ocr_result = result[0]
    texts = ocr_result["rec_texts"]
    if show_image:
        plt.figure(figsize=(8, 6))
        plt.imshow(color_binary)
        plt.axis('off')
        plt.show()
    return ' '.join(texts) 