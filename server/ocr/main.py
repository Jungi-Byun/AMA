#---------------------------------------------------------
# 실행 및 테스트용 진입점
#---------------------------------------------------------

import threading
import time
import torch
from ocr_utils import EasyOCR_from_file, PaddleOCR_from_file, get_easyocr_reader, get_paddleocr_instance
from llm_utils import run_ocr_merge, run_exaone_summary, run_exaone_select
from graph_utils import build_graph
from config import MODEL_NAME, load_curriculum_units
from transformers import AutoModelForCausalLM, AutoTokenizer
# from typing import AgentState  # 잘못된 import 제거

_easyocr_reader = None
_paddleocr_instance = None
_tokenizer = None
_llm_model = None

def get_or_create_easyocr_reader():
    global _easyocr_reader
    if _easyocr_reader is None:
        print("EasyOCR 리더 초기화 중...")
        _easyocr_reader = get_easyocr_reader()
        print("EasyOCR 리더 초기화 완료")
    return _easyocr_reader

def get_or_create_paddleocr_instance():
    global _paddleocr_instance
    if _paddleocr_instance is None:
        clear_all_instances()
        torch.cuda.empty_cache()
        print("PaddleOCR 인스턴스 초기화 중...")
        _paddleocr_instance = get_paddleocr_instance()
        print("PaddleOCR 인스턴스 초기화 완료")
    return _paddleocr_instance

def get_or_create_models():
    """LLM 모델과 토크나이저를 미리 로딩하거나 기존 인스턴스 반환"""
    global _tokenizer, _llm_model
    if _tokenizer is None or _llm_model is None:
        print("LLM 모델 및 토크나이저 초기화 중...")
        _tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        _llm_model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            # torch_dtype="auto",
            torch_dtype=torch.float16,
            trust_remote_code=True,
            device_map="auto",
            offload_buffers=True
        )
        print("LLM 모델 및 토크나이저 초기화 완료")
    return _tokenizer, _llm_model

def clear_easyocr_reader():
    """EasyOCR 리더 인스턴스 제거"""
    global _easyocr_reader
    if _easyocr_reader is not None:
        print("EasyOCR 리더 인스턴스 제거 중...")
        _easyocr_reader = None
        print("EasyOCR 리더 인스턴스 제거 완료")

def clear_paddleocr_instance():
    """PaddleOCR 인스턴스 제거"""
    global _paddleocr_instance
    if _paddleocr_instance is not None:
        print("PaddleOCR 인스턴스 제거 중...")
        _paddleocr_instance = None
        print("PaddleOCR 인스턴스 제거 완료")

def clear_llm_models():
    """LLM 모델 및 토크나이저 인스턴스 제거"""
    global _tokenizer, _llm_model
    if _tokenizer is not None or _llm_model is not None:
        print("LLM 모델 및 토크나이저 인스턴스 제거 중...")
        _tokenizer = None
        _llm_model = None
        print("LLM 모델 및 토크나이저 인스턴스 제거 완료")

def clear_all_instances():
    """모든 인스턴스 제거"""
    clear_easyocr_reader()
    clear_paddleocr_instance()
    clear_llm_models()
    print("모든 인스턴스 제거 완료")

def test_graph(file_path=None, url=None):
    # PaddleOCR 순차 실행
    paddleocr_start = time.time()
    paddleocr_instance = get_or_create_paddleocr_instance()
    paddleocr_result = PaddleOCR_from_file(file_path, url, False, paddleocr_instance)
    paddleocr_time = time.time() - paddleocr_start

    torch.cuda.empty_cache()

    # EasyOCR 순차 실행
    easyocr_start = time.time()
    easyocr_reader = get_or_create_easyocr_reader()
    results, binary = EasyOCR_from_file(file_path, url, reader=easyocr_reader)
    easyocr_time = time.time() - easyocr_start
    easyocr_result = " ".join([text for _, text, _ in results])

    torch.cuda.empty_cache()

    curriculum_units = load_curriculum_units()
    tokenizer, llm_model = get_or_create_models()
    graph = build_graph(tokenizer, llm_model, curriculum_units)
    llm_start = time.time()
    result = graph.invoke({"easyocr_result": easyocr_result, "paddleocr_result": paddleocr_result})
    llm_time = time.time() - llm_start
    print("요약 및 문제 생성 완료!")


    # 결과를 특정 파일에 누적 기록
    result_log_path = "ocr_test_results.txt"
    with open(result_log_path, "a", encoding="utf-8") as f:
        f.write("PaddleOCR 결과: {}\n".format(paddleocr_result))
        f.write("PaddleOCR 수행 시간: {:.2f}초\n".format(paddleocr_time if paddleocr_time is not None else 0))
        f.write("EasyOCR 결과: {}\n".format(easyocr_result))
        f.write("EasyOCR 수행 시간: {:.2f}초\n".format(easyocr_time))
        f.write("LLM 결과(merged_text): {}\n".format(result["merged_text"]))
        f.write("LLM 결과(valid_topic): {}\n".format(result.get("valid_topic", "N/A")))
        f.write("LLM 수행 시간: {:.2f}초\n".format(llm_time))
        f.write("="*60 + "\n")

if __name__ == "__main__":
    import os
    import sys
    import argparse

    # url = 'https://www.home-learn.co.kr/common/image.do?imgPath=newsroom&imgName=CK20221222103639635.png&imgGubun=D'
    # test_graph(url=url)
    # print(f"\nstart test")

    # 명령행 인수 파싱
    parser = argparse.ArgumentParser(
        description='OCR 및 LLM 처리를 위한 이미지 파일 처리 도구',
        epilog="""
            사용 예시:
            python main.py                    # 전체 폴더 처리
            python main.py --list-folders     # 사용 가능한 폴더 목록 출력
            python main.py --folder folder1   # 특정 폴더만 처리
            python main.py -f folder1         # 특정 폴더만 처리 (단축형)
        """
    )
    parser.add_argument('--folder', '-f', type=str, help='처리할 특정 폴더명 (예: folder1)')
    parser.add_argument('--list-folders', '-l', action='store_true', help='사용 가능한 폴더 목록 출력')
    args = parser.parse_args()
    
    IMG_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__),'img'))
    print(f"IMG_ROOT 경로: {IMG_ROOT}")
    
    if not os.path.exists(IMG_ROOT):
        print(f"오류: IMG_ROOT 경로가 존재하지 않습니다: {IMG_ROOT}")
        print("현재 작업 디렉토리:", os.getcwd())
        print("현재 파일 위치:", __file__)
        exit(1)

    if args.list_folders:
        print("\n=== 사용 가능한 폴더 목록 ===")
        folders = [d for d in os.listdir(IMG_ROOT) if os.path.isdir(os.path.join(IMG_ROOT, d))]
        if folders:
            for folder in sorted(folders):
                folder_path = os.path.join(IMG_ROOT, folder)
                file_count = len([f for f in os.listdir(folder_path) 
                                if os.path.splitext(f)[1].lower() in {'.png', '.jpg', '.jpeg', '.bmp', '.tif', '.tiff', '.webp'}])
                print(f"{folder} ({file_count}개 이미지)")
        else:
            print("하위 폴더가 없습니다.")
        print()
        exit(0)

    IMAGE_EXTS = {'.png', '.jpg', '.jpeg', '.bmp', '.tif', '.tiff', '.webp'}

    if args.folder:
        target_path = os.path.join(IMG_ROOT, args.folder)
        if not os.path.exists(target_path):
            print(f"오류: 지정된 폴더가 존재하지 않습니다: {target_path}")
            print("사용 가능한 폴더를 확인하려면: python main_with_llm.py --list-folders")
            exit(1)
        print(f"특정 폴더 처리: {args.folder}")
        search_paths = [target_path]
    else:
        print("전체 폴더 처리")
        search_paths = [IMG_ROOT]

    image_count = 0
    for search_path in search_paths:
        for root, dirs, files in os.walk(search_path):
            for fname in files:
                ext = os.path.splitext(fname)[1].lower()
                if ext in IMAGE_EXTS:
                    img_path = os.path.join(root, fname)
                    print(f"\n===== {img_path} =====")
                    test_graph(file_path=img_path)
                    image_count += 1
    
    if image_count == 0:
        print("처리할 이미지 파일을 찾을 수 없습니다.")
    else:
        print(f"\n총 {image_count}개의 이미지 파일을 처리했습니다.")