import os
from .ocr_agent import OCRAgent

IMAGE_EXTS = {'.png', '.jpg', '.jpeg', '.bmp', '.tif', '.tiff', '.webp'}

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="img2 하위 모든 이미지를 OCRAgent로 테스트")
    parser.add_argument('--img-root', type=str, default=None, help='이미지 루트 폴더 (기본값: ocr_agent.py와 같은 위치의 img2)')
    args = parser.parse_args()

    # img2 폴더 경로 결정
    if args.img_root:
        IMG_ROOT = os.path.abspath(args.img_root)
    else:
        IMG_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), 'img2'))

    print(f"IMG_ROOT 경로: {IMG_ROOT}")
    if not os.path.exists(IMG_ROOT):
        print(f"오류: IMG_ROOT 경로가 존재하지 않습니다: {IMG_ROOT}")
        exit(1)

    agent = OCRAgent()
    image_count = 0
    for root, dirs, files in os.walk(IMG_ROOT):
        for fname in files:
            ext = os.path.splitext(fname)[1].lower()
            if ext in IMAGE_EXTS:
                img_path = os.path.join(root, fname)
                print(f"\n===== {img_path} =====")
                result = agent.run(file_path=img_path)
                # print("LLM 결과():", result.get("merged_text", "N/A"))
                print("LLM 결과():", result)
                image_count += 1
    if image_count == 0:
        print("처리할 이미지 파일을 찾을 수 없습니다.")
    else:
        print(f"\n총 {image_count}개의 이미지 파일을 처리했습니다.") 