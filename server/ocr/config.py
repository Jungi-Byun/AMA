#---------------------------------------------------------
# 모델명, 경로, curriculum_units 로딩
#---------------------------------------------------------

import os
import json

LLM_MODEL_NAME = "LGAI-EXAONE/EXAONE-3.5-7.8B-Instruct"
VLM_MODEL_NAME = "naver-hyperclovax/HyperCLOVAX-SEED-Vision-Instruct-3B"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CURRICULUM_UNITS_PATH = os.path.join(BASE_DIR, "json", "curriculum_units.json")

def load_curriculum_units():
    with open(CURRICULUM_UNITS_PATH, "r", encoding="utf-8") as f:
        return json.load(f) 