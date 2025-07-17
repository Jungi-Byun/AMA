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
    return OptimizedOCRSystem(min_confidence=0.5)

# PaddleOCR 함수
def PaddleOCR_from_file(file_path=None, url=None, show_image=False, ocr=None):
    if ocr is None:
        ocr = get_paddleocr_instance()
    if file_path:
        img_path = file_path
    elif url:
        import tempfile
        import requests
        response = requests.get(url)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
            tmp.write(response.content)
            img_path = tmp.name
    else:
        raise ValueError("Either file_path or url must be provided.")
    result = ocr.process_image_with_split_detection(img_path)
    texts = result.get('full_text', '')
    if show_image:
        import matplotlib.pyplot as plt
        import cv2
        img = cv2.imread(img_path)
        plt.figure(figsize=(8, 6))
        plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        plt.axis('off')
        plt.show()
    return texts 