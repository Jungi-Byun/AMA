import os
import json
import random
import base64
import re

# # 파일에 저장할 경로와 파일명
meta_db = "data/big_math_meta.txt"
topic_db = "data/big_math_topic_list.txt"
labels_directory_path  = 'big_math_bank/labels'
images_directory_path  = 'big_math_bank/origins'

def list_all_files(directory, format):
    file_info = []
    
    if os.path.exists(directory):
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(f'.{format}'):  # JSON 파일만 처리
                    file_path = os.path.join(root, file)
                    file_info.append(file_path)
    return file_info

def read_datasets_from_file(file_path):
    datasets = []
    with open(file_path, "r") as file:
        lines = file.readlines()
        for line in lines:
            # eval을 사용하여 문자열을 frozenset으로 변환
            data = eval(line.strip())
            datasets.append(data)
    return datasets

def extract_value_from_datasets(dataset, key):
    extracted_values = set()
    for fset in dataset:
        data_dict = dict(fset)
        if key in data_dict:
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


def save_question_meta_info(directory_path):
    file_info = list_all_files(directory_path, 'json')
    question_list = []

    # 각 파일 처리
    for file_data in file_info:
        try:
            print(file_data)
            with open(file_data, 'r', encoding='utf-8') as file:
                json_data = json.load(file)
                question_info = json_data['question_info'][0]
                if question_info['question_grade'] == 'P3' or question_info['question_grade'] == 'P4' :
                    question = {
                        "question_topic_name" : question_info['question_topic_name'],
                        "question_grade": question_info['question_grade'],
                        "question_term": question_info['question_term'],
                        "question_unit": question_info['question_unit'],
                        "question_type2" : question_info['question_type2'],
                        "question_filename" : json_data['question_filename']
                    }
                    question_list.append(question)
        except Exception as e:
            print(f"Error processing file {file_data}: {e}")

    # set을 파일로 저장
    with open(meta_db, "w") as file:
        for item in question_list:
            file.write(f"{item}\n")

    print(f"데이터가 {meta_db} 파일에 저장되었습니다.")


def get_math_question_list(topic, type):
    # 파일에서 dataset 데이터를 읽어옴
    loaded_datasets = read_datasets_from_file(meta_db)

    extracted_values = []
    for data in loaded_datasets:
        data_dict = dict(data)
        if type == 1 : 
            if data_dict['question_topic_name'] == topic: 
                extracted_values.append(data_dict)
        else:
            if data_dict['question_topic_name'] == topic and data_dict['question_type2'] == type: 
                extracted_values.append(data_dict)
    
    return extracted_values

def add_newline_before_string(text):
    # 정규 표현식을 사용하여 ①, ②, ③, ④, ⑤ 또는 (1), (2), (3) 앞에 줄바꿈 문자를 추가
    modified_text = re.sub(r'(\(\d+\)|①|②|③|④|⑤|⑥|⑦|⑧|⑨)', r'\n\1', text)
    return modified_text

#----------------------------------------------------
# math_meta.txt 생성
# save_question_meta_info(labels_directory_path)
#----------------------------------------------------

#----------------------------------------------------
# math_topic_list.txt 생성
# get_question_topic_name_list()
#----------------------------------------------------

#----------------------------------------------------
topic = '삼각형을 각의 크기에 따라 분류하기'
#----------------------------------------------------
# get_math_questions 함수
# @topic : 학습 목표(학습 단원)
# @type : 문제 유형(1 - Random, 2-유형 생성)
#----------------------------------------------------
def get_math_questions(topic, type, count=4):
    total_list = get_math_question_list(topic, type)
    
    question_list = []
    question_index_list = set()
    print('question_list len: ', len(total_list))

    if len(total_list) == 0 :
        return question_list
    
    if type == 1:
        while len(question_list) < count:
            #Random index 생성
            index = random.randrange(0, len(total_list)-1)
            print('question_index_list :', question_index_list)
            print('random index : ', index )

            #이전에 생성된 index와 중복되는지 확인
            if index not in question_index_list:
                question_index_list.add(index)
                file = total_list[index]['question_filename']
                if file: 
                    image_path = os.path.join(images_directory_path, file)
                    
                    with open(image_path, "rb") as image_file:
                        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                        question_list.append(encoded_string)
    elif type == 2:
        while len(question_list) < count:
            #Random index 생성
            index = random.randrange(0, len(total_list)-1)
            print('random index : ', index )

            #PNG 파일에서 JSON 파일로 변경
            file = total_list[index]['question_filename'].replace('.png', '.json')
            print('file : ', file)
            if file:
                json_path = os.path.join(labels_directory_path, file)
                with open(json_path, "rb") as json_file:
                    json_data = json.load(json_file)
                    ocr_info = json_data['OCR_info'][0]

                    image_exist = any(bbox['type'] == 'image' for bbox in ocr_info.get('question_bbox', []))
                    if not image_exist:
                        print(ocr_info['question_text'])
                        question = add_newline_before_string(ocr_info['question_text'])
                        question_list.append(question)
                    else:
                        print("image bbox found in OCR_info") 
                    
    return question_list

# question_list = get_math_questions(topic, 2)
# print(question_list)
# print(len(question_list))