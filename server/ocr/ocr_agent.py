from .config import LLM_MODEL_NAME, VLM_MODEL_NAME, load_curriculum_units
from transformers import AutoModelForCausalLM, AutoProcessor, AutoTokenizer
from .ocr_utils import get_easyocr_reader, get_paddleocr_instance
from .graph_utils import build_graph
import torch
import os

class OCRAgent:
    def __init__(self):
        self._init_ocr()
        self._init_llm()
        self._init_vlm()
        self._init_graph()

    def _init_ocr(self):
        self.easyocr_reader = get_easyocr_reader()
        self.paddleocr_instance = get_paddleocr_instance()

    def _init_llm(self):
        self.llm_tokenizer = AutoTokenizer.from_pretrained(LLM_MODEL_NAME)
        self.llm_model = AutoModelForCausalLM.from_pretrained(
            LLM_MODEL_NAME,
            torch_dtype=torch.float16,
            trust_remote_code=True,
            device_map="auto",
            offload_buffers=True
        )
        self.curriculum_units = load_curriculum_units()

    def _init_vlm(self):
        self.vlm_model = AutoModelForCausalLM.from_pretrained(
            VLM_MODEL_NAME,
            device_map="auto",
            trust_remote_code=True)
        self.vlm_processor = AutoProcessor.from_pretrained(VLM_MODEL_NAME, trust_remote_code=True)

    def _init_graph(self):
        self.graph = build_graph(self.llm_tokenizer,
                                 self.llm_model,
                                 self.vlm_processor,
                                 self.vlm_model,
                                 self.paddleocr_instance,
                                 self.easyocr_reader,
                                 self.curriculum_units)

    def run(self, file_path=None):
        result = self.graph.invoke({"image_path": file_path})

        titles = [item['title'] for item in self.curriculum_units]
        predicted_subtopic = result.get("valid_topic", None)
        if not predicted_subtopic or predicted_subtopic not in titles:
            predicted_subtopic = "unknown"

        print("최종 선택 단원: ", predicted_subtopic)
        return predicted_subtopic

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