"""유틸리티 함수들"""
import os
import re
import random

def validate_file_data(data_dict):
    """업로드 파일 데이터 유효성 검사"""
    required_fields = ['question_type', 'filename', 'file']
    
    for field in required_fields:
        if field not in data_dict or not data_dict[field]:
            return False, f"Missing required field: {field}"
    
    return True, "Valid"