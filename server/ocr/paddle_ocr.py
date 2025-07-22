#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from paddleocr import PaddleOCR
import time
import logging
from typing import List, Tuple, Dict, Any, Optional
import os
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class OptimizedImagePreprocessor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def preprocess_image(
        self, image_path: str
    ) -> Tuple[np.ndarray, np.ndarray]:
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"이미지를 읽을 수 없습니다: {image_path}")

        height, width = image.shape[:2]
        if width >= 1280:
            scale = 0.6
            new_width = int(width * scale)
            new_height = int(height * scale)
            image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
            self.logger.error(f"이미지 리사이즈: {width}x{height} -> {new_width}x{new_height}")
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        dark_threshold = 30
        dark_mask = gray < dark_threshold
        
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(4, 4))
        enhanced = clahe.apply(gray)
        
        enhanced = enhanced.copy()
        enhanced[dark_mask] = gray[dark_mask]
        
        kernel = np.ones((3,3), np.uint8)
        dark_mask_dilated = cv2.dilate(dark_mask.astype(np.uint8), kernel, iterations=1)
        dark_mask_dilated = dark_mask_dilated.astype(bool)
        
        border_mask = dark_mask_dilated & ~dark_mask
        if np.any(border_mask):
            border_indices = np.where(border_mask)
            gray_border = gray[border_indices]
            enhanced_border = enhanced[border_indices]
            weighted_result = cv2.addWeighted(gray_border, 0.7, enhanced_border, 0.3, 0)
            if weighted_result.ndim > 1:
                weighted_result = weighted_result.flatten()
            enhanced[border_indices] = weighted_result
        
        color_enhanced = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)
    
        return color_enhanced, image

class OptimizedOCR:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.ocr = PaddleOCR(
            text_recognition_model_name="korean_PP-OCRv5_mobile_rec",
            use_doc_orientation_classify=False,
            use_doc_unwarping=False, 
            use_textline_orientation=True,
            text_det_box_thresh=0.3,
            text_rec_score_thresh=0.5,
            text_det_unclip_ratio=1.5,
            text_det_thresh=0.2,
        )

        # self.logger.info("OCR 시스템 초기화 완료 (GPU, korean_PP-OCRv5_mobile_rec 사용자 지정 경로)")

    def predict(self, image: np.ndarray) -> List[Dict[str, Any]]:
        # print("OptimizedOCR - predict")
        # debug
        # cv2.imwrite("debug_resized.png", image)

        try:
            start_time = time.time()
            result = self.ocr.predict(image)
            processing_time = time.time() - start_time

            # debug
            # for res in result:
            #     res.print()
            #     res.save_to_img("output")
            #     res.save_to_json("output")

            # self.logger.info(f"OCR 예측 완료 (소요시간: {processing_time:.2f}초) - STEP1 최적화 적용")

            return result
            
        except RuntimeError as e:
            if "std::exception" in str(e):
                self.logger.error(f"PaddleOCR C++ 오류 발생: {e}")
                self.logger.error("이미지 크기나 형식 문제일 수 있습니다.")
                return []
            else:
                raise
        except Exception as e:
            self.logger.error(f"OCR 예측 중 예상치 못한 오류: {e}")
            return []

class ResultProcessor:
    def __init__(self, min_confidence: float = 0.5):
        self.min_confidence = min_confidence
        self.logger = logging.getLogger(__name__)
    
    def process_results(
        self, result: List[Dict[str, Any]]
    ) -> List[Tuple[str, float, np.ndarray]]:
        if not result or not isinstance(result, list) or len(result) == 0:
            self.logger.warning("OCR 결과가 없습니다")
            return []
        
        res = result[0]
        texts = res['rec_texts']
        scores = res['rec_scores']
        polys = res['rec_polys']
        
        def filter_text_item(item):
            i, text, score = item
            if score > self.min_confidence:
                return (text, score, polys[i])
            return None

        items = [(i, text, score) for i, (text, score) in enumerate(zip(texts, scores))]

        filtered_results = []
        with ThreadPoolExecutor(max_workers=4) as executor:
            future_to_item = {executor.submit(filter_text_item, item): item for item in items}
            for future in as_completed(future_to_item):
                result_item = future.result()
                if result_item is not None:
                    filtered_results.append(result_item)

        return filtered_results

class OptimizedOCRSystem:    
    def __init__(self, min_confidence: float = 0.5):
        self.preprocessor = OptimizedImagePreprocessor()
        self.ocr = OptimizedOCR()
        self.processor = ResultProcessor(min_confidence)
        self.logger = logging.getLogger(__name__)
    
    def process_image(self, image_path: str) -> Dict[str, Any]:
        start_time = time.time()
        
        try:
            preprocessed_img, original_img = self.preprocessor.preprocess_image(image_path)
            result = self.ocr.predict(preprocessed_img)
            filtered_results = self.processor.process_results(result)
            recognized_text = ""
            if filtered_results:
                texts = [text for text, _, _ in filtered_results]
                recognized_text = " ".join(texts)
            else:
                recognized_text = "신뢰도가 높은 텍스트를 찾지 못했습니다."
            total_time = time.time() - start_time
            final_results = {
                'image_path': image_path,
                'processing_time': total_time,
                'total_detected': len(result[0]['rec_texts']) if result and len(result) > 0 else 0,
                'filtered_results': filtered_results,
                'recognized_text': recognized_text,
                'original_image': original_img,
                'preprocessed_image': preprocessed_img
            }
            
            print(f"이미지 처리 완료 (총 소요시간: {total_time:.2f}초) - STEP1+STEP2 최적화 적용")
            return final_results
            
        except Exception as e:
            self.logger.error(f"이미지 처리 중 오류 발생: {str(e)}")
            raise
    
    def classify_ocr_by_position(self, result: Dict[str, Any], image_width: int) -> Tuple[List[str], List[str]]:
        left_texts = []
        right_texts = []
        for text, score, poly in result['filtered_results']:
            x_coords = [p[0] for p in poly]
            avg_x = sum(x_coords) / len(x_coords)
            if avg_x < image_width / 2:
                left_texts.append(text)
            else:
                right_texts.append(text)
        return left_texts, right_texts
    
    def is_image_split_left_right(self, result: Dict[str, Any], image_width: int, 
                                 threshold_ratio: float = 0.3, center_gap_ratio: float = 0.2) -> bool:
        def analyze_text_position(item):
            text, score, poly = item
            x_coords = [p[0] for p in poly]
            avg_x = sum(x_coords) / len(x_coords)
            
            left_threshold = image_width * (0.5 - center_gap_ratio/2)
            right_threshold = image_width * (0.5 + center_gap_ratio/2)
            
            if avg_x < left_threshold:
                return 'left'
            elif avg_x > right_threshold:
                return 'right'
            else:
                return 'center'
        
        left_count = 0
        right_count = 0
        center_count = 0
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            future_to_item = {executor.submit(analyze_text_position, item): item for item in result['filtered_results']}
            for future in as_completed(future_to_item):
                position = future.result()
                if position == 'left':
                    left_count += 1
                elif position == 'right':
                    right_count += 1
                else:
                    center_count += 1
        
        total = left_count + right_count + center_count
        if total == 0:
            return False
        
        left_ratio = left_count / total
        right_ratio = right_count / total
        center_ratio = center_count / total
        
        is_split = (left_ratio > threshold_ratio and
                   right_ratio > threshold_ratio and
                   center_ratio < 0.1)
        
        # self.logger.info(f"좌우 분할 판단: {'예' if is_split else '아니오'}")
        return is_split
    
    def process_image_with_split_detection(self, image_path: str) -> Dict[str, Any]:
        start_time = time.time()
        
        try:
            original_img = cv2.imread(image_path)
            if original_img is None:
                raise ValueError(f"이미지를 읽을 수 없습니다: {image_path}")
            original_width = original_img.shape[1]
            original_height = original_img.shape[0]
            preprocessed_img, _ = self.preprocessor.preprocess_image(image_path)
            preprocessed_height, preprocessed_width = preprocessed_img.shape[:2]
            result = self.ocr.predict(preprocessed_img)
            if not result or len(result) == 0:
                self.logger.warning("OCR 결과가 비어있습니다.")
                return {
                    'is_split': False,
                    'full_text': "OCR 처리 중 오류가 발생했습니다.",
                    'processing_time': time.time() - start_time,
                    'image_path': image_path,
                    'total_detected': 0,
                    'filtered_results': []
                }
            filtered_results = self.processor.process_results(result)
            if original_width != preprocessed_width or original_height != preprocessed_height:
                scale_x = original_width / preprocessed_width
                scale_y = original_height / preprocessed_height
                converted_results = []
                for text, score, poly in filtered_results:
                    converted_poly = []
                    for point in poly:
                        converted_x = int(point[0] * scale_x)
                        converted_y = int(point[1] * scale_y)
                        converted_poly.append([converted_x, converted_y])
                    converted_poly = np.array(converted_poly)
                    converted_results.append((text, score, converted_poly))
                filtered_results = converted_results
            texts = result[0]['rec_texts']
            recognized_text = " ".join(texts)
            temp_result = {
                'filtered_results': filtered_results,
                'recognized_text': recognized_text
            }
            is_split = self.is_image_split_left_right(temp_result, original_width, threshold_ratio=0.2, center_gap_ratio=0.15)
            if is_split:
                left_texts, right_texts = self.classify_ocr_by_position(temp_result, original_width)
                left_text = '\n'.join(left_texts)
                right_text = '\n'.join(right_texts)
                aleft_text = " ".join(left_texts)
                aright_text = " ".join(right_texts)
                split_result = {
                    'is_split': True,
                    'left_text': left_text,
                    'right_text': right_text,
                    'full_text': aleft_text + aright_text,
                    'processing_time': time.time() - start_time,
                    'image_path': image_path,
                    'total_detected': len(result[0]['rec_texts']) if result and len(result) > 0 else 0,
                    'filtered_results': filtered_results
                }
                return split_result
            else:
                split_result = {
                    'is_split': False,
                    'full_text': recognized_text,
                    'processing_time': time.time() - start_time,
                    'image_path': image_path,
                    'total_detected': len(result[0]['rec_texts']) if result and len(result) > 0 else 0,
                    'filtered_results': filtered_results
                }
                return split_result
            
        except Exception as e:
            self.logger.error(f"좌우 분할 감지 OCR 중 오류 발생: {str(e)}")
            raise
    
    def save_results(self, results: Dict[str, Any], save_path: Optional[str] = None):
        if save_path is None:
            base_name = os.path.splitext(os.path.basename(results['image_path']))[0]
            save_path = f"step3_v3_s0.7_{base_name}_optimized_results.txt"
        
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write("=" * 50 + "\n")
            f.write("=" * 50 + "\n\n")
            
            f.write(f"이미지 경로: {results['image_path']}\n")
            f.write(f"처리 시간: {results['processing_time']:.2f}초\n")
            f.write(f"총 감지된 텍스트: {results['total_detected']}개\n")
            f.write(f"필터링된 텍스트: {len(results['filtered_results'])}개\n\n")
            
            if results.get('is_split', False):
                f.write(f"좌우 분할 감지: 예\n")
                f.write(f"좌측 텍스트:\n{results['left_text']}\n\n")
                f.write(f"우측 텍스트:\n{results['right_text']}\n\n")
            else:
                f.write(f"좌우 분할 감지: 아니오\n")
                f.write(f"전체 텍스트:\n{results['full_text']}\n\n")
        
        # self.logger.info(f"결과 저장 완료: {save_path}")
        return results.get('full_text', '')

def main():
    parser = argparse.ArgumentParser(description='PaddleOCR (v3.0)')
    parser.add_argument('--image', '-i', type=str, 
                       default='img/hand_write_14.png',
                       help='처리할 이미지 파일 경로 (기본값: hand_write_13.png)')
    parser.add_argument('--confidence', '-c', type=float, default=0.5,
                       help='신뢰도 임계값 (기본값: 0.5)')
    args = parser.parse_args()
    
    print("PaddleOCR (v3.0)")
    print("=" * 80)
    print(f"처리할 이미지: {args.image}")
    print(f"신뢰도 임계값: {args.confidence}")
    print("=" * 80)
    
    if not os.path.exists(args.image):
        print(f"오류: 이미지 파일을 찾을 수 없습니다: {args.image}")
        print("사용법 예시:")
        print("python paddleOCR_lr_step3.py --image path/to/image.png")
        return
    
    ocr_system = OptimizedOCRSystem(
        min_confidence=args.confidence
    )
    
    try:
        result = ocr_system.process_image_with_split_detection(args.image)
        print(f"\n처리 시간: {result['processing_time']:.2f}초")
        print(f"감지된 텍스트: {result['total_detected']}개")
        print(f"필터링된 텍스트: {len(result['filtered_results'])}개")
        
        if result.get('is_split', False):
            print(f"좌우 분할 감지: 예")
        else:
            print(f"좌우 분할 감지: 아니오")
        
        if result['processing_time'] <= 5.0:
            print(f"\n목표 달성! 5초 이내 처리 완료: {result['processing_time']:.2f}초")
        else:
            print(f"\n목표 미달성. 추가 최적화 필요: {result['processing_time']:.2f}초")
        
        ocr_system.save_results(result)
        
    except Exception as e:
        print(f"오류 발생: {str(e)}")

if __name__ == '__main__':
    main()
