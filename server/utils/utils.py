"""유틸리티 함수들"""
import os
import re
import random


def add_newline_before_string(text):
    """정규 표현식을 사용하여 ①, ②, ③, ④, ⑤ 또는 (1), (2), (3) 앞에 줄바꿈 문자를 추가"""
    modified_text = re.sub(r'(\(\d+\)|①|②|③|④|⑤|⑥|⑦|⑧|⑨)', r'\n\1', text)
    return modified_text

def validate_file_data(data_dict):
    """업로드 파일 데이터 유효성 검사"""
    required_fields = ['question_type', 'filename', 'file']
    
    for field in required_fields:
        if field not in data_dict or not data_dict[field]:
            return False, f"Missing required field: {field}"
    
    return True, "Valid"

def safe_get_random_index(max_value):
    """안전한 랜덤 인덱스 생성"""
    if max_value <= 0:
        return 0
    return random.randrange(0, max_value)

def read_datasets_from_file(file_path):
    datasets = []
    with open(file_path, "r") as file:
        lines = file.readlines()
        for line in lines:
            data = eval(line.strip())
            datasets.append(data)
    return datasets