import os
import json
import base64
from .config import (META_DB, TOPIC_DB, LABELS_DIRECTORY_PATH, 
                    IMAGES_DIRECTORY_PATH, DEFAULT_QUESTION_COUNT, 
                    QUESTION_TYPE_RANDOM, QUESTION_TYPE_GENERATE)

from .utils import read_datasets_from_file, add_newline_before_string, safe_get_random_index

meta_db = META_DB
topic_db = TOPIC_DB
labels_directory_path = LABELS_DIRECTORY_PATH
images_directory_path = IMAGES_DIRECTORY_PATH

def list_all_files(directory, format):
    file_info = []
    if os.path.exists(directory):
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(f'.{format}'):  # JSON 파일만 처리
                    file_path = os.path.join(root, file)
                    file_info.append(file_path)
    return file_info

def save_question_meta_info(directory_path):
    file_info = list_all_files(directory_path, 'json')
    question_list = []

    for file_data in file_info:
        try:
            with open(file_data, 'r', encoding='utf-8-sig') as file:
                json_data = json.load(file)
                question_info = json_data['question_info'][0]
                if question_info['question_grade'] in ['P3', 'P4']:
                    question = {
                        "question_topic_name": question_info['question_topic_name'],
                        "question_grade": question_info['question_grade'],
                        "question_term": question_info['question_term'],
                        "question_unit": question_info['question_unit'],
                        "question_type1": question_info['question_type1'],
                        "question_type2": question_info['question_type2'],
                        "question_filename": json_data['question_filename']
                    }
                    question_list.append(question)
        except Exception as e:
            print(f"Error processing file {file_data}: {e}")

    with open(meta_db, "w") as file:
        for item in question_list:
            file.write(f"{item}\n")

def extract_value_from_datasets(dataset, key):
    extracted_values = set()
    for fset in dataset:
        data_dict = dict(fset)
        if key in data_dict:
            # if (data_dict['question_grade'] == 'P3' and data_dict['question_term'] == 1 and data_dict['question_unit'] == '02') \
            #    or (data_dict['question_grade'] == 'P3' and data_dict['question_term'] == 2 and data_dict['question_unit'] == '03') \
            #    or (data_dict['question_grade'] == 'P4' and data_dict['question_term'] == 1 and data_dict['question_unit'] == '02') \
            #    or (data_dict['question_grade'] == 'P4' and data_dict['question_term'] == 2 and data_dict['question_unit'] == '02') \
            #    or (data_dict['question_grade'] == 'P4' and data_dict['question_term'] == 2 and data_dict['question_unit'] == '04'):
                extracted_values.add(data_dict[key])
    print(extracted_values)
    return extracted_values

def get_question_topic_name_list():
    # 파일에서 dataset 데이터를 읽어옴
    loaded_datasets = read_datasets_from_file(meta_db)

    # dataset 딕셔너리로 변환
    # 특정 키의 값 추출 (예: 'question_topic_name' 키의 값)
    key_to_extract = "question_topic_name"
    extracted_values = extract_value_from_datasets(loaded_datasets, key_to_extract)

    print(extracted_values)
    # set을 파일로 저장
    with open(topic_db, "w") as file:
        for item in extracted_values:
            file.write(f"{item}\n")


def get_math_question_list(topic, type):
    loaded_datasets = (meta_db)
    
    extracted_values = []
    for data in loaded_datasets:
        data_dict = dict(data)
        if type == QUESTION_TYPE_RANDOM: 
            if data_dict['question_topic_name'] == topic: 
                extracted_values.append(data_dict)
        else:
            if (data_dict['question_topic_name'] == topic and 
                data_dict['question_type2'] == type):
                extracted_values.append(data_dict)
    
    return extracted_values

def get_math_questions(topic, type, count=DEFAULT_QUESTION_COUNT):
    total_list = get_math_question_list(topic, type)
    question_list = []
    question_index_list = set()

    if len(total_list) == 0:
        return question_list
    
    if type == QUESTION_TYPE_RANDOM:
        while len(question_list) < count:
            index = safe_get_random_index(len(total_list)-1)
            
            if index not in question_index_list:
                question_index_list.add(index)
                file = total_list[index]['question_filename']
                if file: 
                    image_path = os.path.join(images_directory_path, file)
                    
                    with open(image_path, "rb") as image_file:
                        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                        question_list.append(encoded_string)
    elif type == QUESTION_TYPE_GENERATE:
        while len(question_list) < count:
            index = safe_get_random_index(len(total_list)-1)
            file = total_list[index]['question_filename'].replace('.png', '.json')
            
            if file:
                json_path = os.path.join(labels_directory_path, file)
                with open(json_path, "rb") as json_file:
                    json_data = json.load(json_file)
                    ocr_info = json_data['OCR_info'][0]

                    image_exist = any(bbox['type'] == 'image' for bbox in ocr_info.get('question_bbox', []))
                    if not image_exist:
                        question = add_newline_before_string(ocr_info['question_text'])
                        question_list.append(question)
                    
    return question_list

