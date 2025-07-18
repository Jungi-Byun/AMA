# from ocr_utils import EasyOCR_from_file, PaddleOCR_from_file, get_easyocr_reader, get_paddleocr_instance
from .ocr_utils import EasyOCR_from_file, PaddleOCR_from_file, get_easyocr_reader, get_paddleocr_instance
from .config import MODEL_NAME, load_curriculum_units
from transformers import AutoModelForCausalLM, AutoTokenizer
from .graph_utils import build_graph
import torch
import os

class OCRAgent:
    def __init__(self):
        self._init_ocr()
        self._init_llm()
        self._init_graph()

    def _init_ocr(self):
        self.easyocr_reader = get_easyocr_reader()
        self.paddleocr_instance = get_paddleocr_instance()

    def _init_llm(self):
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        self.llm_model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            torch_dtype=torch.float16,
            trust_remote_code=True,
            device_map="auto",
            offload_buffers=True
        )
        self.curriculum_units = load_curriculum_units()

    def _init_graph(self):
        self.graph = build_graph(self.tokenizer, self.llm_model, self.curriculum_units)

    def run(self, file_path=None, url=None):
        paddleocr_result = PaddleOCR_from_file(file_path, url, False, self.paddleocr_instance)
        torch.cuda.empty_cache()
        results, _ = EasyOCR_from_file(file_path, url, reader=self.easyocr_reader)
        easyocr_result = " ".join([text for _, text, _ in results])
        torch.cuda.empty_cache()
        result = self.graph.invoke({
            "easyocr_result": easyocr_result,
            "paddleocr_result": paddleocr_result
        })
        # return result
        return result["valid_topic"]

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="OCRAgent(langgraph) OCR+LLM 파이프라인")
    parser.add_argument('--image', type=str, required=True, help='이미지 파일 경로')
    args = parser.parse_args()
    image_path = args.image
    if not os.path.exists(image_path):
        print(f"오류: 파일이 존재하지 않습니다: {image_path}")
        exit(1)
    agent = OCRAgent()
    result = agent.run(file_path=image_path)
    print("LLM 결과(merged_text):", result.get("merged_text", "N/A")) 