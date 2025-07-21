"""유틸리티 함수들"""
import os
import re
import random

def add_newline_before_string(text):
    """정규 표현식을 사용하여 ①, ②, ③, ④, ⑤ 또는 (1), (2), (3) 앞에 줄바꿈 문자를 추가"""
    modified_text = re.sub(r'(\(\d+\)|①|②|③|④|⑤|⑥|⑦|⑧|⑨)', r'\n\1', text)
    return modified_text